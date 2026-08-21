from datetime import UTC, datetime, timedelta
import os
from uuid import uuid4

import pyotp
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.auth.account_lifecycle import (
    AccountLifecycleService,
    IdempotencyConflictError,
    LifecycleAccepted,
    LifecycleQueued,
    LifecycleRejected,
)
from competence_hub_api.auth.mfa_service import (
    MfaService,
    MfaSessionCreated,
    TotpEnrollmentCreated,
)
from competence_hub_api.auth.postgres_mfa_repository import PostgresMfaRepository
from competence_hub_api.auth.postgres_account_lifecycle import (
    PostgresAccountLifecycleRepository,
)
from competence_hub_api.auth.postgres_token_delivery import (
    PostgresTokenDeliveryOutboxRepository,
)
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.auth.token_delivery import (
    OUTBOX_LEASE,
    OUTBOX_MAX_ATTEMPTS,
    TokenDeliveryWorker,
)
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.secret_encryption import SecretCipher
from competence_hub_api.security.tokens import digest_token, keyed_digest

APP_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_APP_DATABASE_URL"
MIGRATOR_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL"
RATE_LIMIT_KEY = b"synthetic-outbox-rate-key-32byte"
IDEMPOTENCY_KEY_SECRET = b"i" * 32
OUTBOX_KEY = b"o" * 32
IDEMPOTENCY_KEY = "synthetic-staging-idempotency-0001"

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


class CapturingAdapter:
    def __init__(self) -> None:
        self.messages = []

    async def deliver(self, **values) -> None:
        self.messages.append(values)


@pytest.mark.anyio
async def test_staging_outbox_idempotency_delivery_failure_cleanup_and_zero_residue() -> None:
    app_url, migrator_url = _required_database_urls()
    app_engine = create_async_engine(app_url, pool_pre_ping=True, hide_parameters=True)
    admin_engine = create_async_engine(
        migrator_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    async with admin_engine.connect() as connection:
        database_now = await connection.scalar(text("SELECT clock_timestamp()"))
    assert isinstance(database_now, datetime)
    now = database_now.astimezone(UTC) + timedelta(minutes=5)
    lifecycle_repository = PostgresAccountLifecycleRepository(app_engine)
    outbox_repository = PostgresTokenDeliveryOutboxRepository(app_engine)
    cipher = SecretCipher(
        {"synthetic-outbox-v1": OUTBOX_KEY},
        "synthetic-outbox-v1",
        context="auth-token-outbox",
    )
    service = AccountLifecycleService(
        lifecycle_repository,
        PasswordService(PasswordPolicy(frozenset())),
        rate_limit_hmac_key=RATE_LIMIT_KEY,
        idempotency_hmac_key=IDEMPOTENCY_KEY_SECRET,
        outbox_cipher=cipher,
    )
    mfa_service = MfaService(
        PostgresMfaRepository(app_engine),
        SecretCipher({"synthetic-totp-v1": b"t" * 32}, "synthetic-totp-v1"),
        recovery_hmac_keys={"synthetic-recovery-v1": b"r" * 32},
        recovery_active_key_version="synthetic-recovery-v1",
        rate_limit_hmac_key=RATE_LIMIT_KEY,
        session_idle_timeout=timedelta(minutes=30),
    )
    actor_id = uuid4()
    reset_user_id = uuid4()
    invitation_email = f"synthetic-invitation-{uuid4().hex}@example.invalid"
    reset_email = f"synthetic-reset-{uuid4().hex}@example.invalid"
    unknown_email = f"synthetic-unknown-{uuid4().hex}@example.invalid"
    client_ip = "192.0.2.70"
    actor = SessionPrincipal(
        session_id=uuid4(),
        user_id=actor_id,
        display_name="Synthetic Staging Admin",
        roles=("admin",),
        authenticated_at=now,
        idle_expires_at=now + timedelta(minutes=30),
        absolute_expires_at=now + timedelta(hours=8),
        csrf_token_hash=b"c" * 32,
    )
    bucket_hashes = {
        keyed_digest(
            f"invitation_issue:account:{invitation_email}", RATE_LIMIT_KEY
        ),
        keyed_digest(f"invitation_issue:ip:{client_ip}", RATE_LIMIT_KEY),
        keyed_digest(
            f"password_reset_request:account:{reset_email}", RATE_LIMIT_KEY
        ),
        keyed_digest(
            f"password_reset_request:account:{unknown_email}", RATE_LIMIT_KEY
        ),
        keyed_digest(f"password_reset_request:ip:{client_ip}", RATE_LIMIT_KEY),
    }

    try:
        password_hash = PasswordService(PasswordPolicy(frozenset())).hash(
            "synthetic staging password"
        )
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.portal_users (
                        id, display_name, email, active
                    ) VALUES
                        (:actor_id, 'Synthetic Staging Admin', :actor_email, true),
                        (:reset_user_id, 'Synthetic Reset User', :reset_email, true)
                    """
                ),
                {
                    "actor_id": actor_id,
                    "actor_email": f"synthetic-admin-{uuid4().hex}@example.invalid",
                    "reset_user_id": reset_user_id,
                    "reset_email": reset_email,
                },
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.user_roles (user_id, role_id)
                    SELECT candidate.user_id, role.id
                    FROM (VALUES
                        (CAST(:actor_id AS uuid), 'admin'),
                        (CAST(:reset_user_id AS uuid), 'internal')
                    ) AS candidate(user_id, role_code)
                    JOIN competence_hub.roles AS role
                      ON role.code = candidate.role_code
                    """
                ),
                {"actor_id": actor_id, "reset_user_id": reset_user_id},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.auth_password_credentials (
                        portal_user_id, password_hash
                    ) VALUES (:user_id, :password_hash)
                    """
                ),
                {"user_id": reset_user_id, "password_hash": password_hash},
            )

        invitation = await service.issue_invitation(
            actor=actor,
            email=invitation_email,
            display_name="Synthetic Invitee",
            role_codes=("internal",),
            idempotency_key=IDEMPOTENCY_KEY,
            client_ip=client_ip,
            now=now,
        )
        assert isinstance(invitation, LifecycleQueued)
        assert invitation.recipient_user_id is not None

        replay = await service.issue_invitation(
            actor=actor,
            email=invitation_email,
            display_name="Synthetic Invitee",
            role_codes=("internal",),
            idempotency_key=IDEMPOTENCY_KEY,
            client_ip=client_ip,
            now=now,
        )
        assert isinstance(replay, LifecycleQueued)
        assert replay.replayed is True
        assert replay.recipient_user_id == invitation.recipient_user_id

        with pytest.raises(IdempotencyConflictError):
            await service.issue_invitation(
                actor=actor,
                email=f"changed-{invitation_email}",
                display_name="Changed Invitee",
                role_codes=("internal",),
                idempotency_key=IDEMPOTENCY_KEY,
                client_ip=client_ip,
                now=now,
            )

        adapter = CapturingAdapter()
        worker = TokenDeliveryWorker(outbox_repository, adapter, cipher)
        assert await worker.run_once(now=now) is True
        assert len(adapter.messages) == 1

        async with admin_engine.connect() as connection:
            invitation_state = (
                await connection.execute(
                    text(
                        """
                        SELECT
                            outbox.status,
                            outbox.recipient_email,
                            outbox.encrypted_payload,
                            token.token_hash
                        FROM competence_hub.auth_token_delivery_outbox AS outbox
                        JOIN competence_hub.auth_one_time_tokens AS token
                          ON token.id = outbox.one_time_token_id
                        WHERE token.portal_user_id = :user_id
                          AND token.purpose = 'invitation'
                        """
                    ),
                    {"user_id": invitation.recipient_user_id},
                )
            ).mappings().one()
        assert invitation_state["status"] == "delivered"
        assert invitation_state["recipient_email"] is None
        assert invitation_state["encrypted_payload"] is None
        assert digest_token(adapter.messages[0]["token"]) == bytes(
            invitation_state["token_hash"]
        )

        invitation_token = adapter.messages[0]["token"]
        invitation_token_hash = digest_token(invitation_token)
        bucket_hashes.update(
            {
                keyed_digest(
                    f"invitation_confirm:token:{invitation_token_hash.hex()}",
                    RATE_LIMIT_KEY,
                ),
                keyed_digest(f"invitation_confirm:ip:{client_ip}", RATE_LIMIT_KEY),
                keyed_digest(
                    f"mfa:user:{invitation.recipient_user_id}",
                    RATE_LIMIT_KEY,
                ),
                keyed_digest(f"mfa:ip:{client_ip}", RATE_LIMIT_KEY),
            }
        )
        accepted = await service.accept_invitation(
            token=invitation_token,
            password="synthetic onboarding password",
            client_ip=client_ip,
            now=now,
        )
        assert isinstance(accepted, LifecycleAccepted)
        assert accepted.login_token is not None
        assert accepted.csrf_token is not None

        replayed_acceptance = await service.accept_invitation(
            token=invitation_token,
            password="synthetic onboarding password",
            client_ip=client_ip,
            now=now,
        )
        assert isinstance(replayed_acceptance, LifecycleRejected)

        enrollment = await mfa_service.start_totp_enrollment(
            login_token=accepted.login_token,
            csrf_token=accepted.csrf_token,
            now=now,
        )
        assert isinstance(enrollment, TotpEnrollmentCreated)
        totp = pyotp.parse_uri(enrollment.provisioning_uri)
        assert isinstance(totp, pyotp.TOTP)
        session = await mfa_service.confirm_totp_enrollment(
            login_token=accepted.login_token,
            csrf_token=accepted.csrf_token,
            code=totp.at(now.timestamp()),
            client_ip=client_ip,
            now=now,
        )
        assert isinstance(session, MfaSessionCreated)
        assert session.session_token
        assert session.csrf_token
        assert len(session.recovery_codes) == 10

        async with admin_engine.connect() as connection:
            onboarding_state = (
                await connection.execute(
                    text(
                        """
                        SELECT
                            portal_user.active,
                            count(DISTINCT role.code) AS roles,
                            count(DISTINCT credential.portal_user_id) AS credentials,
                            count(DISTINCT totp_credential.portal_user_id) AS totp_credentials,
                            count(DISTINCT session.id) AS sessions
                        FROM competence_hub.portal_users AS portal_user
                        JOIN competence_hub.user_roles AS user_role
                          ON user_role.user_id = portal_user.id
                        JOIN competence_hub.roles AS role
                          ON role.id = user_role.role_id
                        LEFT JOIN competence_hub.auth_password_credentials AS credential
                          ON credential.portal_user_id = portal_user.id
                        LEFT JOIN competence_hub.auth_totp_credentials AS totp_credential
                          ON totp_credential.portal_user_id = portal_user.id
                        LEFT JOIN competence_hub.auth_sessions AS session
                          ON session.portal_user_id = portal_user.id
                         AND session.revoked_at IS NULL
                        WHERE portal_user.id = :user_id
                        GROUP BY portal_user.active
                        """
                    ),
                    {"user_id": invitation.recipient_user_id},
                )
            ).mappings().one()
        assert onboarding_state == {
            "active": True,
            "roles": 1,
            "credentials": 1,
            "totp_credentials": 1,
            "sessions": 1,
        }

        known_reset = await service.request_password_reset(
            email=reset_email,
            client_ip=client_ip,
            now=now,
        )
        unknown_reset = await service.request_password_reset(
            email=unknown_email,
            client_ip=client_ip,
            now=now,
        )
        assert known_reset.recipient_user_id == reset_user_id
        assert unknown_reset.recipient_user_id is None

        claim = await outbox_repository.claim_next(
            now=now,
            lease=OUTBOX_LEASE,
            max_attempts=OUTBOX_MAX_ATTEMPTS,
        )
        assert claim is not None
        assert claim.purpose == "password_reset"
        await outbox_repository.record_failure(
            claim,
            now=now,
            error_code="synthetic_terminal_failure",
            retry_at=None,
        )

        async with admin_engine.connect() as connection:
            reset_state = (
                await connection.execute(
                    text(
                        """
                        SELECT
                            outbox.status,
                            outbox.recipient_email,
                            outbox.encrypted_payload,
                            token.revoked_at
                        FROM competence_hub.auth_token_delivery_outbox AS outbox
                        JOIN competence_hub.auth_one_time_tokens AS token
                          ON token.id = outbox.one_time_token_id
                        WHERE token.portal_user_id = :user_id
                          AND token.purpose = 'password_reset'
                        """
                    ),
                    {"user_id": reset_user_id},
                )
            ).mappings().one()
            unknown_outbox_count = await connection.scalar(
                text(
                    """
                    SELECT count(*)
                    FROM competence_hub.auth_token_delivery_outbox AS outbox
                    JOIN competence_hub.auth_one_time_tokens AS token
                      ON token.id = outbox.one_time_token_id
                    JOIN competence_hub.portal_users AS portal_user
                      ON portal_user.id = token.portal_user_id
                    WHERE portal_user.email = :unknown_email
                    """
                ),
                {"unknown_email": unknown_email},
            )
        assert reset_state["status"] == "failed"
        assert reset_state["recipient_email"] is None
        assert reset_state["encrypted_payload"] is None
        assert reset_state["revoked_at"] == now
        assert unknown_outbox_count == 0

        cleanup = await outbox_repository.purge_retained_metadata(
            completed_before=now + timedelta(seconds=1),
            idempotency_expired_before=now + timedelta(days=2),
        )
        assert cleanup.deleted_outbox_records == 2
        assert cleanup.deleted_idempotency_records == 1
    finally:
        try:
            async with admin_engine.begin() as connection:
                await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
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
                        DELETE FROM competence_hub.audit_events
                        WHERE occurred_at = :now
                          AND action IN (
                              'auth.invitation.issue',
                              'auth.password_reset.request',
                              'auth.invitation.accept',
                              'auth.mfa.enrollment'
                          )
                        """
                    ),
                    {"now": now},
                )
                await connection.execute(
                    text(
                        """
                        DELETE FROM competence_hub.portal_users
                        WHERE id = ANY(:user_ids)
                           OR email = :invitation_email
                        """
                    ),
                    {
                        "user_ids": [actor_id, reset_user_id],
                        "invitation_email": invitation_email,
                    },
                )
        finally:
            await app_engine.dispose()
            await admin_engine.dispose()
