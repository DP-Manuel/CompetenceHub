from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import os
import secrets
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from competence_hub_api.config import RuntimeSettings
from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token

APP_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_APP_DATABASE_URL"
MIGRATOR_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL"
ALLOWED_ORIGIN = "https://staging-test.example.invalid"

pytestmark = [pytest.mark.anyio, pytest.mark.staging_integration]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@dataclass(frozen=True)
class SyntheticSession:
    session_id: UUID
    token: str = field(repr=False)
    csrf_token: str = field(repr=False)


@dataclass(frozen=True)
class StagingFixture:
    app: object = field(repr=False)
    admin_engine: AsyncEngine = field(repr=False)
    user_ids: tuple[UUID, ...]
    active: SyntheticSession
    expired: SyntheticSession
    revoked: SyntheticSession
    inactive_user: SyntheticSession
    wrong_role: SyntheticSession
    logout: SyntheticSession


def _required_database_urls() -> tuple[str, str]:
    app_url = os.environ.get(APP_DATABASE_URL_ENV, "")
    migrator_url = os.environ.get(MIGRATOR_DATABASE_URL_ENV, "")
    if not app_url or not migrator_url:
        pytest.skip(
            "isolated staging URLs were not supplied through the process environment"
        )
    return app_url, migrator_url


def _session() -> SyntheticSession:
    return SyntheticSession(
        session_id=uuid4(),
        token=secrets.token_urlsafe(32),
        csrf_token=secrets.token_urlsafe(32),
    )


async def _insert_user(
    connection,
    *,
    user_id: UUID,
    email: str,
    role: str,
    active: bool,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO competence_hub.portal_users (
                id, display_name, email, active
            ) VALUES (
                :user_id, 'Synthetic Staging User', :email, :active
            )
            """
        ),
        {"user_id": user_id, "email": email, "active": active},
    )
    await connection.execute(
        text(
            """
            INSERT INTO competence_hub.user_roles (user_id, role_id)
            SELECT :user_id, id
            FROM competence_hub.roles
            WHERE code = :role
            """
        ),
        {"user_id": user_id, "role": role},
    )


async def _insert_session(
    connection,
    *,
    user_id: UUID,
    session: SyntheticSession,
    created_at: datetime,
    idle_expires_at: datetime,
    absolute_expires_at: datetime,
    revoked_at: datetime | None = None,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO competence_hub.auth_sessions (
                id,
                portal_user_id,
                token_hash,
                csrf_token_hash,
                created_at,
                authenticated_at,
                mfa_completed_at,
                last_seen_at,
                idle_expires_at,
                absolute_expires_at,
                revoked_at,
                revoke_reason
            ) VALUES (
                :session_id,
                :user_id,
                :token_hash,
                :csrf_token_hash,
                :created_at,
                :created_at,
                :created_at,
                :created_at,
                :idle_expires_at,
                :absolute_expires_at,
                :revoked_at,
                :revoke_reason
            )
            """
        ),
        {
            "session_id": session.session_id,
            "user_id": user_id,
            "token_hash": digest_token(session.token),
            "csrf_token_hash": digest_token(session.csrf_token),
            "created_at": created_at,
            "idle_expires_at": idle_expires_at,
            "absolute_expires_at": absolute_expires_at,
            "revoked_at": revoked_at,
            "revoke_reason": "synthetic_setup" if revoked_at else None,
        },
    )


@pytest.fixture
async def staging_fixture() -> StagingFixture:
    app_url, migrator_url = _required_database_urls()
    app_engine = create_async_engine(
        app_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    admin_engine = create_async_engine(
        migrator_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    now = datetime.now(UTC).replace(microsecond=0)
    suffix = uuid4().hex

    user_ids = tuple(uuid4() for _ in range(6))
    sessions = tuple(_session() for _ in range(6))
    active, expired, revoked, inactive_user, wrong_role, logout = sessions

    try:
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            for index, user_id in enumerate(user_ids):
                await _insert_user(
                    connection,
                    user_id=user_id,
                    email=f"synthetic-sb03-{suffix}-{index}@example.invalid",
                    role="coach" if index == 4 else "internal",
                    active=index != 3,
                )

            await _insert_session(
                connection,
                user_id=user_ids[0],
                session=active,
                created_at=now - timedelta(hours=1),
                idle_expires_at=now + timedelta(minutes=10),
                absolute_expires_at=now + timedelta(hours=7),
            )
            await _insert_session(
                connection,
                user_id=user_ids[1],
                session=expired,
                created_at=now - timedelta(hours=2),
                idle_expires_at=now - timedelta(minutes=10),
                absolute_expires_at=now + timedelta(hours=6),
            )
            await _insert_session(
                connection,
                user_id=user_ids[2],
                session=revoked,
                created_at=now - timedelta(hours=1),
                idle_expires_at=now + timedelta(minutes=10),
                absolute_expires_at=now + timedelta(hours=7),
                revoked_at=now - timedelta(minutes=5),
            )
            await _insert_session(
                connection,
                user_id=user_ids[3],
                session=inactive_user,
                created_at=now - timedelta(hours=1),
                idle_expires_at=now + timedelta(minutes=10),
                absolute_expires_at=now + timedelta(hours=7),
            )
            await _insert_session(
                connection,
                user_id=user_ids[4],
                session=wrong_role,
                created_at=now - timedelta(hours=1),
                idle_expires_at=now + timedelta(minutes=10),
                absolute_expires_at=now + timedelta(hours=7),
            )
            await _insert_session(
                connection,
                user_id=user_ids[5],
                session=logout,
                created_at=now - timedelta(hours=1),
                idle_expires_at=now + timedelta(minutes=10),
                absolute_expires_at=now + timedelta(hours=7),
            )

        settings = RuntimeSettings(
            database_url=app_url,
            allowed_origin=ALLOWED_ORIGIN,
            session_idle_timeout=timedelta(minutes=30),
            readiness_timeout_seconds=15,
            rate_limit_hmac_key=b"synthetic-rate-limit-key-32-bytes",
            idempotency_hmac_key=b"synthetic-idempotency-key-32bytes",
            outbox_encryption_keys={"synthetic-v1": b"o" * 32},
            outbox_active_key_version="synthetic-v1",
            compromised_password_fingerprints=frozenset({"0" * 64}),
            totp_encryption_keys={"synthetic-v1": b"t" * 32},
            totp_active_key_version="synthetic-v1",
            recovery_hmac_keys={"synthetic-v1": b"r" * 32},
            recovery_hmac_active_key_version="synthetic-v1",
        )
        app = create_runtime_app(settings, engine_factory=lambda _: app_engine)
        yield StagingFixture(
            app=app,
            admin_engine=admin_engine,
            user_ids=user_ids,
            active=active,
            expired=expired,
            revoked=revoked,
            inactive_user=inactive_user,
            wrong_role=wrong_role,
            logout=logout,
        )
    finally:
        try:
            async with admin_engine.begin() as connection:
                await connection.execute(
                    text("SET LOCAL ROLE competence_hub_owner")
                )
                await connection.execute(
                    text(
                        """
                        DELETE FROM competence_hub.audit_events
                        WHERE entity_id = ANY(:session_ids)
                        """
                    ),
                    {"session_ids": [session.session_id for session in sessions]},
                )
                await connection.execute(
                    text(
                        """
                        DELETE FROM competence_hub.portal_users
                        WHERE id = ANY(:user_ids)
                        """
                    ),
                    {"user_ids": list(user_ids)},
                )
        finally:
            await app_engine.dispose()
            await admin_engine.dispose()


def _set_session_cookie(client: AsyncClient, session: SyntheticSession) -> None:
    client.cookies.set(SESSION_COOKIE_NAME, session.token)


@pytest.mark.parametrize(
    "session_name",
    ["expired", "revoked", "inactive_user", "wrong_role"],
)
async def test_staging_rejects_ineligible_sessions(
    staging_fixture: StagingFixture,
    session_name: str,
) -> None:
    session = getattr(staging_fixture, session_name)
    async with AsyncClient(
        transport=ASGITransport(app=staging_fixture.app),
        base_url=ALLOWED_ORIGIN,
    ) as client:
        _set_session_cookie(client, session)
        response = await client.get("/api/v1/auth/session")

    assert response.status_code == 401
    assert response.json()["code"] == "authentication_failed"


async def test_staging_active_session_refreshes_idle_expiry(
    staging_fixture: StagingFixture,
) -> None:
    async with staging_fixture.admin_engine.connect() as connection:
        before = await connection.scalar(
            text(
                """
                SELECT idle_expires_at
                FROM competence_hub.auth_sessions
                WHERE id = :session_id
                """
            ),
            {"session_id": staging_fixture.active.session_id},
        )

    async with AsyncClient(
        transport=ASGITransport(app=staging_fixture.app),
        base_url=ALLOWED_ORIGIN,
    ) as client:
        _set_session_cookie(client, staging_fixture.active)
        response = await client.get("/api/v1/auth/session")
        csrf_response = await client.post(
            "/api/v1/auth/session/csrf",
            headers={"Origin": ALLOWED_ORIGIN},
        )

    assert response.status_code == 200
    assert response.json()["user"]["roles"] == ["internal"]
    assert csrf_response.status_code == 204
    rotated_csrf_token = csrf_response.headers["x-csrf-token"]
    assert rotated_csrf_token != staging_fixture.active.csrf_token

    async with staging_fixture.admin_engine.connect() as connection:
        after = (
            await connection.execute(
                text(
                    """
                    SELECT idle_expires_at, csrf_token_hash
                    FROM competence_hub.auth_sessions
                    WHERE id = :session_id
                    """
                ),
                {"session_id": staging_fixture.active.session_id},
            )
        ).mappings().one()

    assert before is not None
    assert after["idle_expires_at"] > before
    assert bytes(after["csrf_token_hash"]) == digest_token(rotated_csrf_token)


async def test_staging_logout_checks_csrf_then_revokes_and_audits(
    staging_fixture: StagingFixture,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=staging_fixture.app),
        base_url=ALLOWED_ORIGIN,
    ) as client:
        _set_session_cookie(client, staging_fixture.logout)
        rejected = await client.delete(
            "/api/v1/auth/session",
            headers={"Origin": ALLOWED_ORIGIN, "X-CSRF-Token": "wrong-token"},
        )
        accepted = await client.delete(
            "/api/v1/auth/session",
            headers={
                "Origin": ALLOWED_ORIGIN,
                "X-CSRF-Token": staging_fixture.logout.csrf_token,
            },
        )

    assert rejected.status_code == 403
    assert accepted.status_code == 204

    async with staging_fixture.admin_engine.connect() as connection:
        revocation = (
            await connection.execute(
                text(
                    """
                    SELECT revoked_at, revoke_reason
                    FROM competence_hub.auth_sessions
                    WHERE id = :session_id
                    """
                ),
                {"session_id": staging_fixture.logout.session_id},
            )
        ).mappings().one()
        audit_count = await connection.scalar(
            text(
                """
                SELECT count(*)
                FROM competence_hub.audit_events
                WHERE entity_id = :session_id
                  AND action = 'auth.session.logout'
                  AND outcome = 'success'
                """
            ),
            {"session_id": staging_fixture.logout.session_id},
        )

    assert revocation["revoked_at"] is not None
    assert revocation["revoke_reason"] == "user_logout"
    assert audit_count == 1


async def test_staging_runtime_readiness_uses_postgresql(
    staging_fixture: StagingFixture,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=staging_fixture.app),
        base_url=ALLOWED_ORIGIN,
    ) as client:
        response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
