from datetime import UTC, datetime, timedelta
import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.auth.account_lifecycle import (
    AccountLifecycleService,
    IdempotencyConflictError,
    LifecycleQueued,
)
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
NOW = datetime(2026, 8, 14, 16, 0, tzinfo=UTC)
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
        authenticated_at=NOW,
        idle_expires_at=NOW + timedelta(minutes=30),
        absolute_expires_at=NOW + timedelta(hours=8),
        csrf_token_hash=b"c" * 32,
    )
    bucket_hashes = tuple(
        {
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
    )

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
            now=NOW,
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
            now=NOW,
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
                now=NOW,
            )

        adapter = CapturingAdapter()
        worker = TokenDeliveryWorker(outbox_repository, adapter, cipher)
        assert await worker.run_once(now=NOW) is True
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

        known_reset = await service.request_password_reset(
            email=reset_email,
            client_ip=client_ip,
            now=NOW,
        )
        unknown_reset = await service.request_password_reset(
            email=unknown_email,
            client_ip=client_ip,
            now=NOW,
        )
        assert known_reset.recipient_user_id == reset_user_id
        assert unknown_reset.recipient_user_id is None

        claim = await outbox_repository.claim_next(
            now=NOW,
            lease=OUTBOX_LEASE,
            max_attempts=OUTBOX_MAX_ATTEMPTS,
        )
        assert claim is not None
        assert claim.purpose == "password_reset"
        await outbox_repository.record_failure(
            claim,
            now=NOW,
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
        assert reset_state["revoked_at"] == NOW
        assert unknown_outbox_count == 0

        cleanup = await outbox_repository.purge_retained_metadata(
            completed_before=NOW + timedelta(seconds=1),
            idempotency_expired_before=NOW + timedelta(days=2),
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
                              'auth.password_reset.request'
                          )
                        """
                    ),
                    {"now": NOW},
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
