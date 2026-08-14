from datetime import UTC, datetime, timedelta
import os
from uuid import UUID, uuid4

import pyotp
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from competence_hub_api.config import RuntimeSettings
from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.cookies import (
    LOGIN_COOKIE_NAME,
    SESSION_COOKIE_NAME,
)
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.tokens import digest_token, keyed_digest

APP_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_APP_DATABASE_URL"
MIGRATOR_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL"
ALLOWED_ORIGIN = "https://staging-test.example.invalid"
PASSWORD = "synthetic MFA staging passphrase"
RATE_LIMIT_HMAC_KEY = b"synthetic-rate-limit-key-32-bytes"
TOTP_KEY_VERSION = "synthetic-totp-v1"
TOTP_ENCRYPTION_KEY = b"t" * 32
RECOVERY_KEY_VERSION = "synthetic-recovery-v1"
RECOVERY_HMAC_KEY = b"r" * 32
FIXED_NOW = datetime(2026, 8, 14, 14, 0, 5, tzinfo=UTC)
CLIENT_IP = "192.0.2.60"
RATE_LIMIT_CLIENT_IP = "192.0.2.61"

pytestmark = [pytest.mark.anyio, pytest.mark.staging_integration]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _required_database_urls() -> tuple[str, str]:
    app_url = os.environ.get(APP_DATABASE_URL_ENV, "")
    migrator_url = os.environ.get(MIGRATOR_DATABASE_URL_ENV, "")
    if not app_url or not migrator_url:
        pytest.skip(
            "isolated staging URLs were not supplied through the process environment"
        )
    return app_url, migrator_url


async def _insert_internal_user(
    engine: AsyncEngine,
    *,
    user_id: UUID,
    email: str,
) -> None:
    password_hash = PasswordService(PasswordPolicy(frozenset())).hash(PASSWORD)
    async with engine.begin() as connection:
        await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
        await connection.execute(
            text(
                """
                INSERT INTO competence_hub.portal_users (
                    id, display_name, email, active
                ) VALUES (
                    :user_id, 'Synthetic MFA Staging User', :email, true
                )
                """
            ),
            {"user_id": user_id, "email": email},
        )
        await connection.execute(
            text(
                """
                INSERT INTO competence_hub.user_roles (user_id, role_id)
                SELECT :user_id, id
                FROM competence_hub.roles
                WHERE code = 'internal'
                """
            ),
            {"user_id": user_id},
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


async def _login(client: AsyncClient, email: str):
    return await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    )


def _challenge_headers(csrf_token: str) -> dict[str, str]:
    return {
        "Origin": ALLOWED_ORIGIN,
        "X-CSRF-Token": csrf_token,
    }


@pytest.mark.anyio
async def test_staging_mfa_enrollment_replay_recovery_rotation_and_cleanup() -> None:
    app_url, migrator_url = _required_database_urls()
    app_engine = create_async_engine(app_url, pool_pre_ping=True, hide_parameters=True)
    admin_engine = create_async_engine(
        migrator_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    user_id = uuid4()
    email = f"synthetic-mfa-{uuid4().hex}@example.invalid"
    bucket_hashes = (
        keyed_digest(f"login:account:{email}", RATE_LIMIT_HMAC_KEY),
        keyed_digest(f"login:ip:{CLIENT_IP}", RATE_LIMIT_HMAC_KEY),
        keyed_digest(f"mfa:user:{user_id}", RATE_LIMIT_HMAC_KEY),
        keyed_digest(f"mfa:ip:{CLIENT_IP}", RATE_LIMIT_HMAC_KEY),
        keyed_digest(f"mfa:ip:{RATE_LIMIT_CLIENT_IP}", RATE_LIMIT_HMAC_KEY),
    )

    settings = RuntimeSettings(
        database_url=app_url,
        allowed_origin=ALLOWED_ORIGIN,
        session_idle_timeout=timedelta(minutes=30),
        readiness_timeout_seconds=15,
        rate_limit_hmac_key=RATE_LIMIT_HMAC_KEY,
        totp_encryption_keys={TOTP_KEY_VERSION: TOTP_ENCRYPTION_KEY},
        totp_active_key_version=TOTP_KEY_VERSION,
        recovery_hmac_keys={RECOVERY_KEY_VERSION: RECOVERY_HMAC_KEY},
        recovery_hmac_active_key_version=RECOVERY_KEY_VERSION,
    )
    app = create_runtime_app(settings, engine_factory=lambda _: app_engine)
    app.state.clock = lambda: FIXED_NOW

    try:
        await _insert_internal_user(admin_engine, user_id=user_id, email=email)
        async with AsyncClient(
            transport=ASGITransport(app=app, client=(CLIENT_IP, 43123)),
            base_url=ALLOWED_ORIGIN,
        ) as client:
            first_factor = await _login(client, email)
            assert first_factor.status_code == 202
            assert first_factor.json()["state"] == "mfa_enrollment_required"
            enrollment_csrf = first_factor.json()["csrf_token"]

            enrollment = await client.post(
                "/api/v1/auth/mfa/totp/enrollment",
                headers=_challenge_headers(enrollment_csrf),
            )
            assert enrollment.status_code == 201
            totp = pyotp.parse_uri(enrollment.json()["provisioning_uri"])
            assert isinstance(totp, pyotp.TOTP)
            current_code = totp.at(FIXED_NOW.timestamp())

            confirmation = await client.post(
                "/api/v1/auth/mfa/totp/enrollment/confirm",
                json={"code": current_code},
                headers=_challenge_headers(enrollment_csrf),
            )
            assert confirmation.status_code == 200
            recovery_codes = confirmation.json()["recovery_codes"]
            assert len(recovery_codes) == 10
            assert len(set(recovery_codes)) == 10
            assert client.cookies.get(LOGIN_COOKIE_NAME) is None
            session_token = client.cookies.get(SESSION_COOKIE_NAME)
            assert session_token is not None

            current_session = await client.get("/api/v1/auth/session")
            assert current_session.status_code == 200
            assert current_session.json()["user"]["id"] == str(user_id)

            replay_login = await _login(client, email)
            assert replay_login.status_code == 202
            assert replay_login.json()["state"] == "mfa_required"
            replay_csrf = replay_login.json()["csrf_token"]
            replay = await client.post(
                "/api/v1/auth/mfa/totp/verify",
                json={"code": current_code},
                headers=_challenge_headers(replay_csrf),
            )
            assert replay.status_code == 401

            recovery = await client.post(
                "/api/v1/auth/mfa/recovery/verify",
                json={"code": recovery_codes[0]},
                headers=_challenge_headers(replay_csrf),
            )
            assert recovery.status_code == 204
            assert client.cookies.get(SESSION_COOKIE_NAME) is not None

            reuse_login = await _login(client, email)
            assert reuse_login.status_code == 202
            reuse_csrf = reuse_login.json()["csrf_token"]
            reused = await client.post(
                "/api/v1/auth/mfa/recovery/verify",
                json={"code": recovery_codes[0]},
                headers=_challenge_headers(reuse_csrf),
            )
            assert reused.status_code == 401
            reuse_login_token = client.cookies.get(LOGIN_COOKIE_NAME)
            assert reuse_login_token is not None

            rate_responses = []
            async with AsyncClient(
                transport=ASGITransport(
                    app=app,
                    client=(RATE_LIMIT_CLIENT_IP, 43124),
                ),
                base_url=ALLOWED_ORIGIN,
            ) as rate_client:
                rate_client.cookies.set(LOGIN_COOKIE_NAME, reuse_login_token)
                for _ in range(4):
                    rate_responses.append(
                        await rate_client.post(
                            "/api/v1/auth/mfa/totp/verify",
                            json={"code": "000000"},
                            headers=_challenge_headers(reuse_csrf),
                        )
                    )
            assert [response.status_code for response in rate_responses] == [
                401,
                401,
                401,
                429,
            ]

        async with admin_engine.connect() as connection:
            credential = (
                await connection.execute(
                    text(
                        """
                        SELECT
                            encrypted_secret,
                            key_version,
                            enabled_at,
                            last_accepted_time_step
                        FROM competence_hub.auth_totp_credentials
                        WHERE portal_user_id = :user_id
                        """
                    ),
                    {"user_id": user_id},
                )
            ).mappings().one()
            recovery_summary = (
                await connection.execute(
                    text(
                        """
                        SELECT
                            count(*) AS total,
                            count(*) FILTER (WHERE used_at IS NOT NULL) AS used,
                            count(DISTINCT key_version) AS key_versions
                        FROM competence_hub.auth_recovery_codes
                        WHERE portal_user_id = :user_id
                        """
                    ),
                    {"user_id": user_id},
                )
            ).mappings().one()
            session_count = await connection.scalar(
                text(
                    """
                    SELECT count(*)
                    FROM competence_hub.auth_sessions
                    WHERE portal_user_id = :user_id
                    """
                ),
                {"user_id": user_id},
            )
            stored_session_count = await connection.scalar(
                text(
                    """
                    SELECT count(*)
                    FROM competence_hub.auth_sessions
                    WHERE portal_user_id = :user_id
                      AND token_hash = :token_hash
                    """
                ),
                {
                    "user_id": user_id,
                    "token_hash": digest_token(session_token),
                },
            )

        assert credential["key_version"] == TOTP_KEY_VERSION
        assert credential["enabled_at"] is not None
        assert credential["last_accepted_time_step"] == int(
            FIXED_NOW.timestamp() // 30
        )
        assert totp.secret.encode("ascii") not in bytes(credential["encrypted_secret"])
        assert recovery_summary["total"] == 10
        assert recovery_summary["used"] == 1
        assert recovery_summary["key_versions"] == 1
        assert session_count == 2
        assert stored_session_count == 1
    finally:
        try:
            async with admin_engine.begin() as connection:
                await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
                await connection.execute(
                    text(
                        """
                        DELETE FROM competence_hub.audit_events
                        WHERE actor_user_id = :user_id
                           OR entity_id IN (
                               SELECT id
                               FROM competence_hub.auth_login_challenges
                               WHERE portal_user_id = :user_id
                           )
                           OR entity_id IN (
                               SELECT id
                               FROM competence_hub.auth_sessions
                               WHERE portal_user_id = :user_id
                           )
                        """
                    ),
                    {"user_id": user_id},
                )
                await connection.execute(
                    text(
                        """
                        DELETE FROM competence_hub.auth_rate_limit_buckets
                        WHERE bucket_key_hash = ANY(:bucket_hashes)
                        """
                    ),
                    {"bucket_hashes": list(bucket_hashes)},
                )
                await connection.execute(
                    text(
                        """
                        DELETE FROM competence_hub.portal_users
                        WHERE id = :user_id
                        """
                    ),
                    {"user_id": user_id},
                )
        finally:
            await app_engine.dispose()
            await admin_engine.dispose()
