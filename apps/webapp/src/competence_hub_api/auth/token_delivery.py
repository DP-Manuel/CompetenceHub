from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal, Protocol
from uuid import UUID

from competence_hub_api.security.secret_encryption import (
    SecretCipher,
    SecretEncryptionError,
)

OUTBOX_LEASE = timedelta(minutes=5)
OUTBOX_MAX_ATTEMPTS = 5
OUTBOX_BASE_RETRY_DELAY = timedelta(minutes=1)
OUTBOX_MAX_RETRY_DELAY = timedelta(hours=1)


class TokenDeliveryError(RuntimeError):
    pass


class StaleOutboxClaimError(RuntimeError):
    pass


@dataclass(frozen=True)
class ClaimedTokenDelivery:
    outbox_id: UUID
    claim_id: UUID
    purpose: Literal["invitation", "password_reset"]
    recipient_email: str = field(repr=False)
    encrypted_payload: bytes = field(repr=False)
    key_version: str
    attempt_count: int
    expires_at: datetime


@dataclass(frozen=True)
class OutboxCleanupResult:
    deleted_outbox_records: int
    deleted_idempotency_records: int


class TokenDeliveryOutboxRepository(Protocol):
    async def claim_next(
        self,
        *,
        now: datetime,
        lease: timedelta,
        max_attempts: int,
    ) -> ClaimedTokenDelivery | None: ...

    async def mark_delivered(
        self,
        delivery: ClaimedTokenDelivery,
        *,
        now: datetime,
    ) -> None: ...

    async def record_failure(
        self,
        delivery: ClaimedTokenDelivery,
        *,
        now: datetime,
        error_code: str,
        retry_at: datetime | None,
    ) -> None: ...

    async def purge_retained_metadata(
        self,
        *,
        completed_before: datetime,
        idempotency_expired_before: datetime,
    ) -> OutboxCleanupResult: ...


class TokenMessageAdapter(Protocol):
    async def deliver(
        self,
        *,
        delivery_id: UUID,
        purpose: Literal["invitation", "password_reset"],
        recipient_email: str,
        token: str,
        expires_at: datetime,
    ) -> None: ...


class TokenDeliveryWorker:
    def __init__(
        self,
        repository: TokenDeliveryOutboxRepository,
        adapter: TokenMessageAdapter,
        cipher: SecretCipher,
    ) -> None:
        if cipher.context != "auth-token-outbox":
            raise ValueError("outbox cipher must use the auth-token-outbox context")
        self._repository = repository
        self._adapter = adapter
        self._cipher = cipher

    async def run_once(self, *, now: datetime) -> bool:
        delivery = await self._repository.claim_next(
            now=now,
            lease=OUTBOX_LEASE,
            max_attempts=OUTBOX_MAX_ATTEMPTS,
        )
        if delivery is None:
            return False

        try:
            token = self._cipher.decrypt(
                delivery.encrypted_payload,
                key_version=delivery.key_version,
                subject_id=_outbox_subject(delivery.purpose, delivery.outbox_id),
            )
        except SecretEncryptionError:
            await self._repository.record_failure(
                delivery,
                now=now,
                error_code="payload_authentication_failed",
                retry_at=None,
            )
            return True

        try:
            await self._adapter.deliver(
                delivery_id=delivery.outbox_id,
                purpose=delivery.purpose,
                recipient_email=delivery.recipient_email,
                token=token,
                expires_at=delivery.expires_at,
            )
        except TokenDeliveryError:
            retry_at = _retry_at(delivery, now=now)
            await self._repository.record_failure(
                delivery,
                now=now,
                error_code="adapter_delivery_failed",
                retry_at=retry_at,
            )
            return True

        await self._repository.mark_delivered(delivery, now=now)
        return True


def _retry_at(
    delivery: ClaimedTokenDelivery,
    *,
    now: datetime,
) -> datetime | None:
    if delivery.attempt_count >= OUTBOX_MAX_ATTEMPTS:
        return None
    multiplier = 2 ** max(0, delivery.attempt_count - 1)
    delay_seconds = min(
        OUTBOX_MAX_RETRY_DELAY.total_seconds(),
        OUTBOX_BASE_RETRY_DELAY.total_seconds() * multiplier,
    )
    retry_at = now + timedelta(seconds=delay_seconds)
    if retry_at >= delivery.expires_at:
        return None
    return retry_at


def _outbox_subject(
    purpose: Literal["invitation", "password_reset"],
    outbox_id: UUID,
) -> str:
    return f"{purpose}:{outbox_id}"
