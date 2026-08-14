from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.token_delivery import (
    ClaimedTokenDelivery,
    TokenDeliveryError,
    TokenDeliveryWorker,
)
from competence_hub_api.security.secret_encryption import SecretCipher

NOW = datetime(2026, 8, 14, 16, 0, tzinfo=UTC)
OUTBOX_ID = UUID("00000000-0000-4000-8000-000000000401")
CLAIM_ID = UUID("00000000-0000-4000-8000-000000000402")
OUTBOX_KEY = b"o" * 32
TOKEN = "synthetic-one-time-token"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _cipher() -> SecretCipher:
    return SecretCipher(
        {"outbox-v1": OUTBOX_KEY},
        "outbox-v1",
        context="auth-token-outbox",
    )


def _delivery(*, attempt_count: int = 1, tampered: bool = False):
    encrypted = _cipher().encrypt(
        TOKEN,
        subject_id=f"invitation:{OUTBOX_ID}",
    )
    envelope = encrypted.envelope
    if tampered:
        envelope = envelope[:-1] + bytes([envelope[-1] ^ 1])
    return ClaimedTokenDelivery(
        outbox_id=OUTBOX_ID,
        claim_id=CLAIM_ID,
        purpose="invitation",
        recipient_email="person@example.invalid",
        encrypted_payload=envelope,
        key_version=encrypted.key_version,
        attempt_count=attempt_count,
        expires_at=NOW + timedelta(hours=1),
    )


class FakeRepository:
    def __init__(self, delivery) -> None:
        self.delivery = delivery
        self.claims = []
        self.delivered = []
        self.failures = []

    async def claim_next(self, **values):
        self.claims.append(values)
        delivery, self.delivery = self.delivery, None
        return delivery

    async def mark_delivered(self, delivery, *, now):
        self.delivered.append((delivery, now))

    async def record_failure(self, delivery, **values):
        self.failures.append((delivery, values))


class FakeAdapter:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.messages = []

    async def deliver(self, **values):
        self.messages.append(values)
        if self.fail:
            raise TokenDeliveryError("synthetic adapter failure")


@pytest.mark.anyio
async def test_worker_decrypts_delivers_and_marks_claim_complete() -> None:
    repository = FakeRepository(_delivery())
    adapter = FakeAdapter()

    processed = await TokenDeliveryWorker(repository, adapter, _cipher()).run_once(
        now=NOW
    )

    assert processed is True
    assert adapter.messages == [
        {
            "delivery_id": OUTBOX_ID,
            "purpose": "invitation",
            "recipient_email": "person@example.invalid",
            "token": TOKEN,
            "expires_at": NOW + timedelta(hours=1),
        }
    ]
    assert len(repository.delivered) == 1
    assert repository.failures == []
    assert TOKEN not in repr(repository.delivered)


@pytest.mark.anyio
async def test_adapter_failure_schedules_bounded_retry_without_exposing_token() -> None:
    repository = FakeRepository(_delivery(attempt_count=2))
    adapter = FakeAdapter(fail=True)

    await TokenDeliveryWorker(repository, adapter, _cipher()).run_once(now=NOW)

    assert repository.delivered == []
    assert repository.failures[0][1]["error_code"] == "adapter_delivery_failed"
    assert repository.failures[0][1]["retry_at"] == NOW + timedelta(minutes=2)
    assert TOKEN not in repr(repository.failures)


@pytest.mark.anyio
async def test_last_attempt_fails_terminally_without_retry() -> None:
    repository = FakeRepository(_delivery(attempt_count=5))

    await TokenDeliveryWorker(repository, FakeAdapter(fail=True), _cipher()).run_once(
        now=NOW
    )

    assert repository.failures[0][1]["retry_at"] is None


@pytest.mark.anyio
async def test_tampered_payload_fails_terminally_before_adapter_call() -> None:
    repository = FakeRepository(_delivery(tampered=True))
    adapter = FakeAdapter()

    await TokenDeliveryWorker(repository, adapter, _cipher()).run_once(now=NOW)

    assert adapter.messages == []
    assert repository.failures[0][1] == {
        "now": NOW,
        "error_code": "payload_authentication_failed",
        "retry_at": None,
    }


@pytest.mark.anyio
async def test_empty_outbox_is_a_clean_noop() -> None:
    repository = FakeRepository(None)

    assert (
        await TokenDeliveryWorker(repository, FakeAdapter(), _cipher()).run_once(
            now=NOW
        )
        is False
    )
