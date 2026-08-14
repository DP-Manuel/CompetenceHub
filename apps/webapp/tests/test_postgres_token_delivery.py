from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.postgres_token_delivery import (
    PostgresTokenDeliveryOutboxRepository,
)
from competence_hub_api.auth.token_delivery import (
    ClaimedTokenDelivery,
    StaleOutboxClaimError,
)

NOW = datetime(2026, 8, 14, 16, 0, tzinfo=UTC)
OUTBOX_ID = UUID("00000000-0000-4000-8000-000000000401")
CLAIM_ID = UUID("00000000-0000-4000-8000-000000000402")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeResult:
    def __init__(self, *, scalar=None, row=None, rowcount=0) -> None:
        self.scalar = scalar
        self.row = row
        self.rowcount = rowcount

    def scalar_one_or_none(self):
        return self.scalar

    def mappings(self):
        return self

    def one_or_none(self):
        return self.row


class FakeConnection:
    def __init__(self, results=()) -> None:
        self.results = iter(results)
        self.executed = []

    async def execute(self, statement, parameters=None):
        self.executed.append((statement, parameters))
        return next(self.results, FakeResult())


class FakeContext:
    def __init__(self, connection) -> None:
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class FakeEngine:
    def __init__(self, results=()) -> None:
        self.connection = FakeConnection(results)

    def begin(self):
        return FakeContext(self.connection)


def _claimed() -> ClaimedTokenDelivery:
    return ClaimedTokenDelivery(
        outbox_id=OUTBOX_ID,
        claim_id=CLAIM_ID,
        purpose="password_reset",
        recipient_email="person@example.invalid",
        encrypted_payload=b"encrypted",
        key_version="outbox-v1",
        attempt_count=1,
        expires_at=NOW + timedelta(minutes=30),
    )


@pytest.mark.anyio
async def test_claim_expires_old_messages_then_atomically_claims_next() -> None:
    row = {
        "id": OUTBOX_ID,
        "purpose": "password_reset",
        "recipient_email": "person@example.invalid",
        "encrypted_payload": b"encrypted",
        "key_version": "outbox-v1",
        "attempt_count": 2,
        "expires_at": NOW + timedelta(minutes=30),
    }
    engine = FakeEngine([FakeResult(), FakeResult(), FakeResult(row=row)])
    repository = PostgresTokenDeliveryOutboxRepository(engine)

    delivery = await repository.claim_next(
        now=NOW,
        lease=timedelta(minutes=5),
        max_attempts=5,
    )

    assert delivery is not None
    assert delivery.outbox_id == OUTBOX_ID
    assert delivery.attempt_count == 2
    assert len(engine.connection.executed) == 3
    assert "attempt_count >= :max_attempts" in str(
        engine.connection.executed[1][0]
    )
    claim_parameters = engine.connection.executed[2][1]
    assert claim_parameters["lease_expires_at"] == NOW + timedelta(minutes=5)
    assert claim_parameters["max_attempts"] == 5
    assert delivery.claim_id == claim_parameters["claim_id"]


@pytest.mark.anyio
async def test_delivered_claim_uses_claim_id_and_clears_sensitive_state_in_sql() -> None:
    engine = FakeEngine([FakeResult(scalar=OUTBOX_ID)])
    repository = PostgresTokenDeliveryOutboxRepository(engine)

    await repository.mark_delivered(_claimed(), now=NOW)

    statement, parameters = engine.connection.executed[0]
    sql = str(statement)
    assert "recipient_email = NULL" in sql
    assert "encrypted_payload = NULL" in sql
    assert parameters["claim_id"] == CLAIM_ID


@pytest.mark.anyio
async def test_terminal_failure_revokes_token_and_rejects_stale_claim() -> None:
    engine = FakeEngine([FakeResult(scalar=None)])
    repository = PostgresTokenDeliveryOutboxRepository(engine)

    with pytest.raises(StaleOutboxClaimError):
        await repository.record_failure(
            _claimed(),
            now=NOW,
            error_code="adapter_delivery_failed",
            retry_at=None,
        )

    statement = str(engine.connection.executed[0][0])
    assert "UPDATE competence_hub.auth_one_time_tokens" in statement
    assert "encrypted_payload = NULL" in statement


@pytest.mark.anyio
async def test_retry_preserves_payload_but_releases_claim() -> None:
    engine = FakeEngine([FakeResult(scalar=OUTBOX_ID)])
    repository = PostgresTokenDeliveryOutboxRepository(engine)
    retry_at = NOW + timedelta(minutes=1)

    await repository.record_failure(
        _claimed(),
        now=NOW,
        error_code="adapter_delivery_failed",
        retry_at=retry_at,
    )

    statement, parameters = engine.connection.executed[0]
    sql = str(statement)
    assert "status = 'pending'" in sql
    assert "encrypted_payload = NULL" not in sql
    assert parameters["retry_at"] == retry_at


@pytest.mark.anyio
async def test_cleanup_uses_explicit_retention_cutoffs() -> None:
    engine = FakeEngine(
        [
            FakeResult(rowcount=3),
            FakeResult(rowcount=2),
        ]
    )
    repository = PostgresTokenDeliveryOutboxRepository(engine)
    completed_before = NOW - timedelta(days=7)
    idempotency_before = NOW - timedelta(days=1)

    result = await repository.purge_retained_metadata(
        completed_before=completed_before,
        idempotency_expired_before=idempotency_before,
    )

    assert result.deleted_outbox_records == 3
    assert result.deleted_idempotency_records == 2
    assert engine.connection.executed[0][1] == {
        "completed_before": completed_before
    }
    assert engine.connection.executed[1][1] == {
        "expired_before": idempotency_before
    }
