"""Opt-in bootstrap proof using an owned disposable localhost:55438 PG only.

Use the existing local-container harness pattern (bootstrap-staging + 0001-0009),
not a native Staging URL. The operator supplies fresh synthetic process URLs and
a database comment ``synthetic-initial-admin-owned:<NONCE>``. Never use this
fixture's synthetic keys or enrollment handling for a real person.
"""

import asyncio
from dataclasses import replace
from datetime import UTC, timedelta
import logging
import os
import re
from uuid import UUID

import pyotp
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.admin_cli import create_initial_admin_interactively
from competence_hub_api.auth.account_administration import (
    InitialAdminAlreadyExistsError,
    InitialAdminConfigurationError,
)
from competence_hub_api.auth.postgres_account_administration import (
    PostgresInitialAdminRepository,
)
from competence_hub_api.portal.coach_registry import CoachRegistryService
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)
from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.cookies import LOGIN_COOKIE_NAME, SESSION_COOKIE_NAME
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from test_runtime import runtime_settings

PREFIX = "COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_"
PASSWORD = "synthetic initial admin bootstrap passphrase"
EMAILS = (
    "synthetic-bootstrap-a@example.invalid",
    "synthetic-bootstrap-b@example.invalid",
)
BOOTSTRAP_TABLES = (
    "portal_users",
    "user_roles",
    "auth_password_credentials",
    "audit_events",
)
AUTH_TABLES = (
    "auth_sessions",
    "auth_login_challenges",
    "auth_totp_credentials",
    "auth_recovery_codes",
    "auth_one_time_tokens",
    "auth_rate_limit_buckets",
    "auth_idempotency_records",
    "auth_token_delivery_outbox",
)
UNTOUCHED_TABLES = (
    "coaches",
    "coach_topics",
    "company_contacts",
    "companies",
    "topics",
    "calendar_offers",
    "calendar_offer_revisions",
    "calendar_review_decisions",
    "coach_profile_revisions",
    "coach_import_sources",
    "coach_import_items",
    "coach_import_evidence",
    "coach_public_roles",
    "coach_qualifications",
    "coach_offering_families",
    "coach_object_evidence",
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _local_configuration():
    values = [
        os.environ.get(PREFIX + key, "") for key in ("APP_URL", "OWNER_URL", "NONCE")
    ]
    if not any(values):
        pytest.skip("requires an owned disposable initial-admin PostgreSQL container")
    app_url, owner_url, nonce = values
    assert re.fullmatch(r"[a-f0-9]{32}", nonce), "owned-container nonce is required"
    for raw, role in zip(
        (app_url, owner_url), ("competence_hub_app", "competence_hub_migrator")
    ):
        u = make_url(raw)
        assert (u.drivername, u.host, u.port, u.database, u.username) == (
            "postgresql+asyncpg",
            "127.0.0.1",
            55438,
            "competence_hub_staging",
            role,
        )
        assert u.password and not u.query
    return app_url, owner_url, nonce


@pytest.mark.parametrize(
    "invalid",
    [
        {
            "APP_URL": "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55432/competence_hub_staging"
        },
        {
            "APP_URL": "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55438/competence_hub_production"
        },
        {
            "APP_URL": "postgresql+asyncpg://competence_hub_app:synthetic@192.0.2.1:55438/competence_hub_staging"
        },
        {
            "OWNER_URL": "postgresql+asyncpg://postgres:synthetic@127.0.0.1:55438/competence_hub_staging"
        },
        {
            "OWNER_URL": "postgresql+asyncpg://competence_hub_migrator:synthetic@127.0.0.1:55438/competence_hub_staging?host=192.0.2.1"
        },
        {"NONCE": ""},
    ],
)
def test_local_bootstrap_guards_reject_other_targets_before_connect(
    monkeypatch, invalid
):
    values = {
        "APP_URL": "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55438/competence_hub_staging",
        "OWNER_URL": "postgresql+asyncpg://competence_hub_migrator:synthetic@127.0.0.1:55438/competence_hub_staging",
        "NONCE": "a" * 32,
    }
    for key, value in (values | invalid).items():
        monkeypatch.setenv(PREFIX + key, value)
    with pytest.raises(AssertionError):
        _local_configuration()


async def _counts(engine, tables):
    async with engine.connect() as c:
        return {
            table: await c.scalar(text(f"SELECT count(*) FROM competence_hub.{table}"))
            for table in tables
        }


async def _strict_bootstrap_guards(engine, owner, now):
    async with engine.connect() as c:
        tables = list(
            (
                await c.execute(
                    text(
                        "SELECT tablename FROM pg_tables WHERE schemaname='competence_hub' ORDER BY tablename"
                    )
                )
            ).scalars()
        )
    baseline = await _counts(engine, [t for t in tables if t != "schema_migrations"])
    # schema_migrations is intentionally unreadable to the app role.
    assert not any(baseline[t] for t in BOOTSTRAP_TABLES + UNTOUCHED_TABLES)

    for scenario in ("expired", "nonadmin", "active_admin", "coach"):
        seeded_user = seeded_coach = None
        try:
            async with owner.begin() as c:
                await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
                database_now = await c.scalar(text("SELECT clock_timestamp()"))
                if scenario in {"nonadmin", "active_admin"}:
                    seeded_user = await c.scalar(
                        text(
                            "INSERT INTO competence_hub.portal_users(display_name,email) "
                            "VALUES ('Synthetic strict bootstrap guard','strict-guard@example.invalid') RETURNING id"
                        )
                    )
                    if scenario == "active_admin":
                        await c.execute(
                            text(
                                "INSERT INTO competence_hub.user_roles(user_id,role_id) "
                                "SELECT :id,id FROM competence_hub.roles WHERE code='admin' AND active"
                            ),
                            {"id": seeded_user},
                        )
                elif scenario == "coach":
                    seeded_coach = await c.scalar(
                        text(
                            "INSERT INTO competence_hub.coaches(display_name,public_profile_status) "
                            "VALUES ('Synthetic strict bootstrap guard','not_published') RETURNING id"
                        )
                    )
            before = await _counts(engine, baseline)
            deadline = database_now + timedelta(
                seconds=-1 if scenario == "expired" else 120
            )
            repository = PostgresInitialAdminRepository(
                engine,
                require_empty_target=True,
                bootstrap_deadline=deadline,
            )
            with pytest.raises(InitialAdminConfigurationError):
                await repository.create_initial_admin(
                    normalized_email="strict-new@example.invalid",
                    display_name="Synthetic strict Admin",
                    password_hash="synthetic-strict-hash",
                    now=now,
                )
            assert await _counts(engine, baseline) == before, scenario
        finally:
            async with owner.begin() as c:
                await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
                if seeded_user is not None:
                    await c.execute(
                        text("DELETE FROM competence_hub.user_roles WHERE user_id=:id"),
                        {"id": seeded_user},
                    )
                    await c.execute(
                        text("DELETE FROM competence_hub.portal_users WHERE id=:id"),
                        {"id": seeded_user},
                    )
                if seeded_coach is not None:
                    await c.execute(
                        text("DELETE FROM competence_hub.coaches WHERE id=:id"),
                        {"id": seeded_coach},
                    )
        assert await _counts(engine, baseline) == baseline

    async with engine.connect() as c:
        deadline = await c.scalar(
            text("SELECT clock_timestamp() + interval '2 minutes'")
        )
    repository = PostgresInitialAdminRepository(
        engine,
        require_empty_target=True,
        bootstrap_deadline=deadline,
    )
    tasks = []
    winner = None
    try:
        async with owner.begin() as c:
            await c.execute(
                text(
                    "SELECT pg_advisory_xact_lock(hashtext('competence_hub.initial_admin'))"
                )
            )
            tasks = [
                asyncio.create_task(
                    repository.create_initial_admin(
                        normalized_email=email,
                        display_name="Synthetic strict concurrent Admin",
                        password_hash="synthetic-strict-hash",
                        now=now,
                    )
                )
                for email in EMAILS
            ]
            async with asyncio.timeout(10):
                while (
                    await c.scalar(
                        text(
                            "SELECT count(*) FROM pg_locks waiting JOIN pg_locks held "
                            "USING (locktype,database,classid,objid,objsubid) "
                            "WHERE held.pid=pg_backend_pid() AND held.locktype='advisory' "
                            "AND held.granted AND NOT waiting.granted"
                        )
                    )
                    != 2
                ):
                    await asyncio.sleep(0.02)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        winners = [r for r in results if isinstance(r, UUID)]
        assert len(winners) == 1
        winner = winners[0]
        assert sum(isinstance(r, InitialAdminConfigurationError) for r in results) == 1
        expected = {
            table: count + (table in BOOTSTRAP_TABLES)
            for table, count in baseline.items()
        }
        assert await _counts(engine, baseline) == expected
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        if winner is not None:
            async with owner.begin() as c:
                await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
                await c.execute(
                    text(
                        "DELETE FROM competence_hub.audit_events WHERE entity_id=:id "
                        "AND entity_type='portal_user' AND action='auth.initial_admin.create'"
                    ),
                    {"id": winner},
                )
                await c.execute(
                    text(
                        "DELETE FROM competence_hub.auth_password_credentials WHERE portal_user_id=:id"
                    ),
                    {"id": winner},
                )
                await c.execute(
                    text("DELETE FROM competence_hub.user_roles WHERE user_id=:id"),
                    {"id": winner},
                )
                await c.execute(
                    text("DELETE FROM competence_hub.portal_users WHERE id=:id"),
                    {"id": winner},
                )
    assert await _counts(engine, baseline) == baseline


@pytest.mark.anyio
async def test_initial_admin_app_privileges_atomic_bootstrap_and_native_auth(
    tmp_path, caplog
):
    app_url, owner_url, nonce = _local_configuration()
    caplog.set_level(logging.INFO, logger="sqlalchemy.engine")
    engine, owner = [
        create_async_engine(u, hide_parameters=True) for u in (app_url, owner_url)
    ]
    # Only this freshly generated synthetic fingerprint file is read by the CLI.
    fingerprints = tmp_path / "synthetic-compromised-fingerprints.txt"
    fingerprints.write_text("0" * 64 + "\n", encoding="ascii")
    try:
        async with engine.connect() as c:
            assert (
                await c.scalar(
                    text(
                        "SELECT shobj_description(oid, 'pg_database') FROM pg_database "
                        "WHERE datname=current_database()"
                    )
                )
                == "synthetic-initial-admin-owned:" + nonce
            )
            assert await c.scalar(text("SELECT current_user")) == "competence_hub_app"
            assert (
                await c.execute(
                    text(
                        "SELECT rolsuper, rolcreaterole, rolcreatedb, rolbypassrls "
                        "FROM pg_roles WHERE rolname=current_user"
                    )
                )
            ).one() == (False, False, False, False)
            assert not await c.scalar(
                text("SELECT pg_has_role(current_user,'competence_hub_owner','MEMBER')")
            )
            for privilege, expected in (
                ("SELECT", True),
                ("INSERT", False),
                ("UPDATE", False),
                ("DELETE", False),
            ):
                assert (
                    await c.scalar(
                        text(
                            "SELECT has_table_privilege(current_user,'competence_hub.roles',:privilege)"
                        ),
                        {"privilege": privilege},
                    )
                    is expected
                )
            now = (await c.scalar(text("SELECT clock_timestamp()"))).astimezone(
                UTC
            ) + timedelta(minutes=5)
        async with owner.connect() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            assert (
                await c.execute(
                    text(
                        "SELECT version FROM competence_hub.schema_migrations ORDER BY version"
                    )
                )
            ).scalars().all() == [f"{v:04}" for v in range(1, 10)]
        baseline = await _counts(
            engine, BOOTSTRAP_TABLES + AUTH_TABLES + UNTOUCHED_TABLES
        )
        assert not any(
            baseline.values()
        ), "refusing a nonempty synthetic bootstrap database"
        await _strict_bootstrap_guards(engine, owner, now)

        async def bootstrap(email=EMAILS[0]):
            inputs = iter((email, "Synthetic Initial Admin"))
            await create_initial_admin_interactively(
                environment={
                    "COMPETENCE_HUB_DATABASE_URL": app_url,
                    "COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH": str(
                        fingerprints
                    ),
                },
                input_reader=lambda _: next(inputs),
                password_reader=lambda _: PASSWORD,
                terminal_check=lambda: True,
                now=now,
            )

        # This reproduces the old query's actual PostgreSQL privilege failure.
        with pytest.raises(DBAPIError) as denied:
            async with engine.begin() as c:
                await c.execute(
                    text(
                        "SELECT id FROM competence_hub.roles WHERE code='admin' FOR SHARE"
                    )
                )
        assert denied.value.orig.sqlstate == "42501"

        async with owner.begin() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await c.execute(
                text("UPDATE competence_hub.roles SET active=false WHERE code='admin'")
            )
        try:
            with pytest.raises(InitialAdminConfigurationError):
                await bootstrap()
            assert await _counts(engine, baseline) == baseline
        finally:
            async with owner.begin() as c:
                await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
                await c.execute(
                    text(
                        "UPDATE competence_hub.roles SET active=true WHERE code='admin'"
                    )
                )

        # Reject the LAST write, proving user, role and password insert rollback too.
        async with owner.begin() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await c.execute(
                text(
                    "ALTER TABLE competence_hub.audit_events ADD CONSTRAINT synthetic_reject_bootstrap "
                    "CHECK (action <> 'auth.initial_admin.create')"
                )
            )
        try:
            with pytest.raises(DBAPIError) as failed_audit:
                await bootstrap()
            assert failed_audit.value.orig.sqlstate == "23514"
            assert await _counts(engine, baseline) == baseline
        finally:
            async with owner.begin() as c:
                await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
                await c.execute(
                    text(
                        "ALTER TABLE competence_hub.audit_events DROP CONSTRAINT synthetic_reject_bootstrap"
                    )
                )

        tasks = []
        try:
            async with owner.begin() as c:
                await c.execute(
                    text(
                        "SELECT pg_advisory_xact_lock(hashtext('competence_hub.initial_admin'))"
                    )
                )
                tasks = [asyncio.create_task(bootstrap(email)) for email in EMAILS]
                # Both real CLI transactions must wait on the exact bootstrap lock.
                async with asyncio.timeout(10):
                    while (
                        await c.scalar(
                            text(
                                "SELECT count(*) FROM pg_locks waiting JOIN pg_locks held "
                                "USING (locktype,database,classid,objid,objsubid) "
                                "WHERE held.pid=pg_backend_pid() AND held.locktype='advisory' "
                                "AND held.granted AND NOT waiting.granted"
                            )
                        )
                        != 2
                    ):
                        await asyncio.sleep(0.02)
            results = await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            await asyncio.gather(*tasks, return_exceptions=True)
        assert sum(r is None for r in results) == 1
        assert sum(isinstance(r, InitialAdminAlreadyExistsError) for r in results) == 1
        winner = EMAILS[results.index(None)]
        async with engine.connect() as c:
            user_id = await c.scalar(text("SELECT id FROM competence_hub.portal_users"))
            assert (
                await c.execute(
                    text(
                        "SELECT r.code, ur.assigned_by_user_id FROM competence_hub.user_roles ur "
                        "JOIN competence_hub.roles r ON r.id=ur.role_id WHERE ur.user_id=:id"
                    ),
                    {"id": user_id},
                )
            ).all() == [("admin", None)]
            credential = await c.scalar(
                text(
                    "SELECT password_hash FROM competence_hub.auth_password_credentials"
                )
            )
            assert credential.startswith("$argon2id$")
            assert PasswordService(PasswordPolicy(frozenset())).verify(
                credential, PASSWORD
            )
            audit = (
                (await c.execute(text("SELECT * FROM competence_hub.audit_events")))
                .mappings()
                .one()
            )
            assert set(audit) == {
                "id",
                "actor_user_id",
                "occurred_at",
                "action",
                "entity_type",
                "entity_id",
                "outcome",
            }
            assert (
                audit["actor_user_id"],
                audit["action"],
                audit["entity_type"],
                audit["entity_id"],
                audit["outcome"],
            ) == (
                None,
                "auth.initial_admin.create",
                "portal_user",
                user_id,
                "success",
            )
            assert audit["occurred_at"] == now
        after = await _counts(engine, baseline)
        assert {t: after[t] for t in BOOTSTRAP_TABLES} == dict.fromkeys(
            BOOTSTRAP_TABLES, 1
        )
        with pytest.raises(InitialAdminAlreadyExistsError):
            await bootstrap()
        assert await _counts(engine, baseline) == after
        assert not any((await _counts(engine, UNTOUCHED_TABLES)).values())

        await _native_auth(engine, app_url, now, winner, user_id, credential, caplog)
        assert not any((await _counts(engine, UNTOUCHED_TABLES)).values())
        assert (await _counts(engine, ("portal_users", "user_roles"))) == {
            "portal_users": 1,
            "user_roles": 1,
        }
    finally:
        await engine.dispose()
        await owner.dispose()


async def _native_auth(engine, app_url, now, email, user_id, password_hash, caplog):
    settings = replace(runtime_settings(), database_url=app_url)

    def runtime():
        app = create_runtime_app(settings, engine_factory=lambda _: engine)
        # Existing Registry tests use the same deliberate local-only wiring.
        app.state.coach_registry_service = CoachRegistryService(
            PostgresCoachRegistryRepository(engine)
        )
        app.state.clock = lambda: now
        return app

    origin = settings.allowed_origin
    async with AsyncClient(
        transport=ASGITransport(app=runtime()), base_url=origin
    ) as client:
        login = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
        )
        assert login.status_code == 202
        assert login.json()["state"] == "mfa_enrollment_required"
        headers = {"Origin": origin, "X-CSRF-Token": login.json()["csrf_token"]}
        assert (await client.get("/api/v1/auth/session")).status_code == 401
        assert (await client.get("/api/v1/admin/coaches")).status_code == 401
        enrollment = await client.post(
            "/api/v1/auth/mfa/totp/enrollment", headers=headers
        )
        assert enrollment.status_code == 201
        totp = pyotp.parse_uri(enrollment.json()["provisioning_uri"])
        assert isinstance(totp, pyotp.TOTP)
        code = totp.at(now.timestamp())
        confirm = await client.post(
            "/api/v1/auth/mfa/totp/enrollment/confirm",
            headers=headers,
            json={"code": code},
        )
        assert confirm.status_code == 200
        recovery = confirm.json()["recovery_codes"]
        assert len(set(recovery)) == 10
        assert client.cookies.get(LOGIN_COOKIE_NAME) is None
        first_session = client.cookies.get(SESSION_COOKIE_NAME)
        assert first_session
        current = await client.get("/api/v1/auth/session")
        assert current.status_code == 200
        assert current.json()["user"]["id"] == str(user_id)
        assert current.json()["user"]["roles"] == ["admin"]
        assert (await client.get("/api/v1/admin/coaches")).status_code == 200

    # Recreate the pool/runtime, preserving the same test keyrings: no ephemeral rekey.
    await engine.dispose()
    now += timedelta(seconds=60)
    async with AsyncClient(
        transport=ASGITransport(app=runtime()), base_url=origin
    ) as client:
        login = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
        )
        assert login.status_code == 202 and login.json()["state"] == "mfa_required"
        headers = {"Origin": origin, "X-CSRF-Token": login.json()["csrf_token"]}
        verified = await client.post(
            "/api/v1/auth/mfa/totp/verify",
            headers=headers,
            json={"code": totp.at(now.timestamp())},
        )
        assert verified.status_code == 204
        totp_session = client.cookies.get(SESSION_COOKIE_NAME)
        assert totp_session and totp_session != first_session
        login = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
        )
        headers = {"Origin": origin, "X-CSRF-Token": login.json()["csrf_token"]}
        replayed = await client.post(
            "/api/v1/auth/mfa/totp/verify",
            headers=headers,
            json={"code": totp.at(now.timestamp())},
        )
        assert replayed.status_code == 401
        verified = await client.post(
            "/api/v1/auth/mfa/recovery/verify",
            headers=headers,
            json={"code": recovery[0]},
        )
        assert verified.status_code == 204
        recovery_session = client.cookies.get(SESSION_COOKIE_NAME)
        assert recovery_session and recovery_session != totp_session
        login = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
        )
        headers = {"Origin": origin, "X-CSRF-Token": login.json()["csrf_token"]}
        reused = await client.post(
            "/api/v1/auth/mfa/recovery/verify",
            headers=headers,
            json={"code": recovery[0]},
        )
        assert reused.status_code == 401
        assert (await client.get("/api/v1/auth/session")).status_code == 200
        # Session CSRF rotation permits an explicit native logout after recovery.
        csrf = await client.post(
            "/api/v1/auth/session/csrf", headers={"Origin": origin}
        )
        assert csrf.status_code == 204
        logged_out = await client.delete(
            "/api/v1/auth/session",
            headers={
                "Origin": origin,
                "X-CSRF-Token": csrf.headers["X-CSRF-Token"],
            },
        )
        assert logged_out.status_code == 204
        assert (await client.get("/api/v1/auth/session")).status_code == 401

    async with engine.connect() as c:
        stored = (
            await c.execute(
                text(
                    "SELECT encrypted_secret,key_version,enabled_at FROM competence_hub.auth_totp_credentials"
                )
            )
        ).one()
        assert (
            stored.key_version == settings.totp_active_key_version and stored.enabled_at
        )
        assert totp.secret.encode() not in bytes(stored.encrypted_secret)
        assert (
            await c.execute(
                text(
                    "SELECT count(*),count(*) FILTER (WHERE used_at IS NOT NULL),count(DISTINCT key_version) "
                    "FROM competence_hub.auth_recovery_codes"
                )
            )
        ).one() == (10, 1, 1)
        audits = str(
            (await c.execute(text("SELECT * FROM competence_hub.audit_events"))).all()
        )
        assert "SQL parameters hidden" in caplog.text
        for sensitive in (
            email,
            PASSWORD,
            password_hash,
            totp.secret,
            code,
            *recovery,
            first_session,
            totp_session,
            recovery_session,
        ):
            assert sensitive not in audits
            assert sensitive not in caplog.text
