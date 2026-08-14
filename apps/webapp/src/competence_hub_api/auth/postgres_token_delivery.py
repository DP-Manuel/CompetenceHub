from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.token_delivery import (
    ClaimedTokenDelivery,
    OutboxCleanupResult,
    StaleOutboxClaimError,
)

_EXPIRE_UNDELIVERABLE = text(
    """
    WITH expired AS (
        UPDATE competence_hub.auth_token_delivery_outbox
        SET status = 'failed',
            recipient_email = NULL,
            encrypted_payload = NULL,
            key_version = NULL,
            claimed_at = NULL,
            claim_id = NULL,
            lease_expires_at = NULL,
            completed_at = :now,
            last_error_code = 'delivery_expired'
        WHERE status IN ('pending', 'processing')
          AND expires_at <= :now
        RETURNING one_time_token_id
    )
    UPDATE competence_hub.auth_one_time_tokens
    SET revoked_at = :now
    WHERE id IN (SELECT one_time_token_id FROM expired)
      AND consumed_at IS NULL
      AND revoked_at IS NULL
    """
)

_FAIL_EXHAUSTED_CLAIMS = text(
    """
    WITH exhausted AS (
        UPDATE competence_hub.auth_token_delivery_outbox
        SET status = 'failed',
            recipient_email = NULL,
            encrypted_payload = NULL,
            key_version = NULL,
            claimed_at = NULL,
            claim_id = NULL,
            lease_expires_at = NULL,
            completed_at = :now,
            last_error_code = 'delivery_attempts_exhausted'
        WHERE status = 'processing'
          AND lease_expires_at <= :now
          AND attempt_count >= :max_attempts
        RETURNING one_time_token_id
    )
    UPDATE competence_hub.auth_one_time_tokens
    SET revoked_at = :now
    WHERE id IN (SELECT one_time_token_id FROM exhausted)
      AND consumed_at IS NULL
      AND revoked_at IS NULL
    """
)

_CLAIM_NEXT = text(
    """
    WITH candidate AS (
        SELECT id
        FROM competence_hub.auth_token_delivery_outbox
        WHERE (
                (
                    status = 'pending'
                    AND available_at <= :now
                )
                OR (
                    status = 'processing'
                    AND lease_expires_at <= :now
                )
            )
          AND expires_at > :now
          AND attempt_count < :max_attempts
        ORDER BY available_at, created_at
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    UPDATE competence_hub.auth_token_delivery_outbox AS outbox
    SET status = 'processing',
        attempt_count = outbox.attempt_count + 1,
        claimed_at = :now,
        claim_id = :claim_id,
        lease_expires_at = :lease_expires_at,
        last_error_code = NULL
    FROM candidate
    WHERE outbox.id = candidate.id
    RETURNING
        outbox.id,
        outbox.purpose,
        outbox.recipient_email,
        outbox.encrypted_payload,
        outbox.key_version,
        outbox.attempt_count,
        outbox.expires_at
    """
)

_MARK_DELIVERED = text(
    """
    UPDATE competence_hub.auth_token_delivery_outbox
    SET status = 'delivered',
        recipient_email = NULL,
        encrypted_payload = NULL,
        key_version = NULL,
        claimed_at = NULL,
        claim_id = NULL,
        lease_expires_at = NULL,
        completed_at = :now,
        last_error_code = NULL
    WHERE id = :outbox_id
      AND status = 'processing'
      AND claim_id = :claim_id
    RETURNING id
    """
)

_RETRY_DELIVERY = text(
    """
    UPDATE competence_hub.auth_token_delivery_outbox
    SET status = 'pending',
        available_at = :retry_at,
        claimed_at = NULL,
        claim_id = NULL,
        lease_expires_at = NULL,
        last_error_code = :error_code
    WHERE id = :outbox_id
      AND status = 'processing'
      AND claim_id = :claim_id
    RETURNING id
    """
)

_FAIL_DELIVERY = text(
    """
    WITH failed AS (
        UPDATE competence_hub.auth_token_delivery_outbox
        SET status = 'failed',
            recipient_email = NULL,
            encrypted_payload = NULL,
            key_version = NULL,
            claimed_at = NULL,
            claim_id = NULL,
            lease_expires_at = NULL,
            completed_at = :now,
            last_error_code = :error_code
        WHERE id = :outbox_id
          AND status = 'processing'
          AND claim_id = :claim_id
        RETURNING id, one_time_token_id
    ), revoked AS (
        UPDATE competence_hub.auth_one_time_tokens
        SET revoked_at = :now
        WHERE id IN (SELECT one_time_token_id FROM failed)
          AND consumed_at IS NULL
          AND revoked_at IS NULL
    )
    SELECT id FROM failed
    """
)

_DELETE_RETAINED_OUTBOX = text(
    """
    DELETE FROM competence_hub.auth_token_delivery_outbox
    WHERE status IN ('delivered', 'failed', 'canceled')
      AND completed_at < :completed_before
    """
)

_DELETE_EXPIRED_IDEMPOTENCY = text(
    """
    DELETE FROM competence_hub.auth_idempotency_records
    WHERE expires_at < :expired_before
    """
)


class PostgresTokenDeliveryOutboxRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def claim_next(
        self,
        *,
        now: datetime,
        lease: timedelta,
        max_attempts: int,
    ) -> ClaimedTokenDelivery | None:
        if lease.total_seconds() <= 0 or max_attempts <= 0:
            raise ValueError("outbox claim limits must be positive")
        claim_id = uuid4()
        async with self._engine.begin() as connection:
            await connection.execute(_EXPIRE_UNDELIVERABLE, {"now": now})
            await connection.execute(
                _FAIL_EXHAUSTED_CLAIMS,
                {"now": now, "max_attempts": max_attempts},
            )
            result = await connection.execute(
                _CLAIM_NEXT,
                {
                    "now": now,
                    "claim_id": claim_id,
                    "lease_expires_at": now + lease,
                    "max_attempts": max_attempts,
                },
            )
            row = result.mappings().one_or_none()
        if row is None:
            return None
        return ClaimedTokenDelivery(
            outbox_id=row["id"],
            claim_id=claim_id,
            purpose=row["purpose"],
            recipient_email=row["recipient_email"],
            encrypted_payload=bytes(row["encrypted_payload"]),
            key_version=row["key_version"],
            attempt_count=row["attempt_count"],
            expires_at=row["expires_at"],
        )

    async def mark_delivered(
        self,
        delivery: ClaimedTokenDelivery,
        *,
        now: datetime,
    ) -> None:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _MARK_DELIVERED,
                {
                    "outbox_id": delivery.outbox_id,
                    "claim_id": delivery.claim_id,
                    "now": now,
                },
            )
            _require_claim(result.scalar_one_or_none())

    async def record_failure(
        self,
        delivery: ClaimedTokenDelivery,
        *,
        now: datetime,
        error_code: str,
        retry_at: datetime | None,
    ) -> None:
        if not error_code or len(error_code) > 100:
            raise ValueError("invalid outbox error code")
        if retry_at is not None and (
            retry_at <= now or retry_at >= delivery.expires_at
        ):
            raise ValueError("outbox retry time is outside the delivery window")
        statement = _RETRY_DELIVERY if retry_at is not None else _FAIL_DELIVERY
        parameters = {
            "outbox_id": delivery.outbox_id,
            "claim_id": delivery.claim_id,
            "now": now,
            "error_code": error_code,
            "retry_at": retry_at,
        }
        async with self._engine.begin() as connection:
            result = await connection.execute(statement, parameters)
            _require_claim(result.scalar_one_or_none())

    async def purge_retained_metadata(
        self,
        *,
        completed_before: datetime,
        idempotency_expired_before: datetime,
    ) -> OutboxCleanupResult:
        async with self._engine.begin() as connection:
            outbox_result = await connection.execute(
                _DELETE_RETAINED_OUTBOX,
                {"completed_before": completed_before},
            )
            idempotency_result = await connection.execute(
                _DELETE_EXPIRED_IDEMPOTENCY,
                {"expired_before": idempotency_expired_before},
            )
        return OutboxCleanupResult(
            deleted_outbox_records=max(0, outbox_result.rowcount),
            deleted_idempotency_records=max(0, idempotency_result.rowcount),
        )


def _require_claim(outbox_id: UUID | None) -> None:
    if outbox_id is None:
        raise StaleOutboxClaimError("outbox claim is no longer active")
