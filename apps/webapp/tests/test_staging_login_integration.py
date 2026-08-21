from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import os
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from competence_hub_api.config import RuntimeSettings
from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.tokens import digest_token, keyed_digest

APP_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_APP_DATABASE_URL"
MIGRATOR_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL"
ALLOWED_ORIGIN = "https://staging-test.example.invalid"
HMAC_KEY = b"synthetic-rate-limit-key-32-bytes"
PASSWORD = "synthetic staging passphrase"

pytestmark = [pytest.mark.anyio, pytest.mark.staging_integration]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@dataclass(frozen=True)
class StagingLoginFixture:
    app: object = field(repr=False)
    admin_engine: AsyncEngine = field(repr=False)
    user_ids: tuple[UUID, ...]
    emails: tuple[str, ...]
    client_ips: tuple[str, ...]


def _required_database_urls() -> tuple[str, str]:
    app_url = os.environ.get(APP_DATABASE_URL_ENV, "")
    migrator_url = os.environ.get(MIGRATOR_DATABASE_URL_ENV, "")
    if not app_url or not migrator_url:
        pytest.skip(
            "isolated staging URLs were not supplied through the process environment"
        )
    return app_url, migrator_url


async def _insert_user(
    connection,
    *,
    user_id: UUID,
    email: str,
    role: str,
    active: bool,
    password_hash: str,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO competence_hub.portal_users (
                id, display_name, email, active
            ) VALUES (
                :user_id, 'Synthetic Login User', :email, :active
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
    await connection.execute(
        text(
            """
            INSERT INTO competence_hub.auth_password_credentials (
                portal_user_id, password_hash
            ) VALUES (
                :user_id, :password_hash
            )
            """
        ),
        {"user_id": user_id, "password_hash": password_hash},
    )


@pytest.fixture
async def staging_login_fixture() -> StagingLoginFixture:
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
    suffix = uuid4().hex
    user_ids = tuple(uuid4() for _ in range(3))
    emails = (
        f"synthetic-login-active-{suffix}@example.invalid",
        f"synthetic-login-inactive-{suffix}@example.invalid",
        f"synthetic-login-coach-{suffix}@example.invalid",
    )
    client_ips = ("192.0.2.40", "192.0.2.41", "192.0.2.42", "192.0.2.43")
    password_service = PasswordService(PasswordPolicy(frozenset()))
    password_hash = password_service.hash(PASSWORD)

    try:
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await _insert_user(
                connection,
                user_id=user_ids[0],
                email=emails[0],
                role="internal",
                active=True,
                password_hash=password_hash,
            )
            await _insert_user(
                connection,
                user_id=user_ids[1],
                email=emails[1],
                role="internal",
                active=False,
                password_hash=password_hash,
            )
            await _insert_user(
                connection,
                user_id=user_ids[2],
                email=emails[2],
                role="coach",
                active=True,
                password_hash=password_hash,
            )

        settings = RuntimeSettings(
            database_url=app_url,
            allowed_origin=ALLOWED_ORIGIN,
            session_idle_timeout=timedelta(minutes=30),
            readiness_timeout_seconds=15,
            rate_limit_hmac_key=HMAC_KEY,
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
        yield StagingLoginFixture(
            app=app,
            admin_engine=admin_engine,
            user_ids=user_ids,
            emails=emails,
            client_ips=client_ips,
        )
    finally:
        try:
            bucket_hashes = [
                keyed_digest(f"login:account:{email}", HMAC_KEY) for email in emails
            ] + [
                keyed_digest(f"login:ip:{client_ip}", HMAC_KEY)
                for client_ip in client_ips
            ]
            async with admin_engine.begin() as connection:
                await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
                await connection.execute(
                    text(
                        """
                        DELETE FROM competence_hub.audit_events
                        WHERE actor_user_id = ANY(:user_ids)
                           OR entity_id = ANY(:user_ids)
                        """
                    ),
                    {"user_ids": list(user_ids)},
                )
                await connection.execute(
                    text(
                        """
                        DELETE FROM competence_hub.auth_rate_limit_buckets
                        WHERE action = 'login'
                          AND bucket_key_hash = ANY(:bucket_hashes)
                        """
                    ),
                    {"bucket_hashes": bucket_hashes},
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


def _client(fixture: StagingLoginFixture, client_ip: str) -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(
            app=fixture.app,
            client=(client_ip, 43123),
        ),
        base_url=ALLOWED_ORIGIN,
    )


async def test_staging_valid_first_factor_creates_hashed_challenge_and_audit(
    staging_login_fixture: StagingLoginFixture,
) -> None:
    async with _client(staging_login_fixture, staging_login_fixture.client_ips[0]) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": staging_login_fixture.emails[0], "password": PASSWORD},
        )

    assert response.status_code == 202
    assert response.json()["state"] == "mfa_enrollment_required"
    assert "competence_hub_session" not in "".join(
        response.headers.get_list("set-cookie")
    )
    login_token = client.cookies.get("__Host-competence_hub_login")
    assert login_token is not None

    async with staging_login_fixture.admin_engine.connect() as connection:
        challenge = (
            await connection.execute(
                text(
                    """
                    SELECT id, token_hash, csrf_token_hash, expires_at - created_at AS lifetime
                    FROM competence_hub.auth_login_challenges
                    WHERE portal_user_id = :user_id
                      AND revoked_at IS NULL
                    """
                ),
                {"user_id": staging_login_fixture.user_ids[0]},
            )
        ).mappings().one()
        audit_count = await connection.scalar(
            text(
                """
                SELECT count(*)
                FROM competence_hub.audit_events
                WHERE actor_user_id = :user_id
                  AND entity_id = :challenge_id
                  AND action = 'auth.login.first_factor'
                  AND outcome = 'success'
                """
            ),
            {
                "user_id": staging_login_fixture.user_ids[0],
                "challenge_id": challenge["id"],
            },
        )

    assert bytes(challenge["token_hash"]) == digest_token(login_token)
    assert bytes(challenge["csrf_token_hash"]) == digest_token(
        response.json()["csrf_token"]
    )
    assert challenge["lifetime"] == timedelta(minutes=5)
    assert audit_count == 1


@pytest.mark.parametrize("user_index", [1, 2])
async def test_staging_inactive_and_external_users_get_same_generic_failure(
    staging_login_fixture: StagingLoginFixture,
    user_index: int,
) -> None:
    client_ip = staging_login_fixture.client_ips[user_index]
    async with _client(staging_login_fixture, client_ip) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": staging_login_fixture.emails[user_index],
                "password": PASSWORD,
            },
        )

    assert response.status_code == 401
    assert response.json()["code"] == "authentication_failed"

    async with staging_login_fixture.admin_engine.connect() as connection:
        challenge_count = await connection.scalar(
            text(
                """
                SELECT count(*)
                FROM competence_hub.auth_login_challenges
                WHERE portal_user_id = :user_id
                """
            ),
            {"user_id": staging_login_fixture.user_ids[user_index]},
        )
    assert challenge_count == 0


async def test_staging_fifth_failed_password_attempt_is_rate_limited(
    staging_login_fixture: StagingLoginFixture,
) -> None:
    client_ip = staging_login_fixture.client_ips[3]
    responses = []
    async with _client(staging_login_fixture, client_ip) as client:
        for _ in range(5):
            responses.append(
                await client.post(
                    "/api/v1/auth/login",
                    json={
                        "email": staging_login_fixture.emails[0],
                        "password": "wrong synthetic password",
                    },
                )
            )

    assert [response.status_code for response in responses] == [401, 401, 401, 401, 429]
    assert responses[-1].json()["code"] == "rate_limit_exceeded"
    assert int(responses[-1].headers["retry-after"]) >= 1

    account_bucket_hash = keyed_digest(
        f"login:account:{staging_login_fixture.emails[0]}",
        HMAC_KEY,
    )
    ip_bucket_hash = keyed_digest(f"login:ip:{client_ip}", HMAC_KEY)
    async with staging_login_fixture.admin_engine.connect() as connection:
        buckets = (
            await connection.execute(
                text(
                    """
                    SELECT bucket_key_hash, failed_attempts, blocked_until
                    FROM competence_hub.auth_rate_limit_buckets
                    WHERE action = 'login'
                      AND bucket_key_hash IN (:account_bucket_hash, :ip_bucket_hash)
                    """
                ),
                {
                    "account_bucket_hash": account_bucket_hash,
                    "ip_bucket_hash": ip_bucket_hash,
                },
            )
        ).mappings().all()

    assert len(buckets) == 2
    assert {bytes(row["bucket_key_hash"]) for row in buckets} == {
        account_bucket_hash,
        ip_bucket_hash,
    }
    assert all(row["failed_attempts"] == 5 for row in buckets)
    assert all(row["blocked_until"] is not None for row in buckets)
