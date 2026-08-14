from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.mfa_repository import (
    RecoveryCodeRecord,
    SessionRecord,
)
from competence_hub_api.auth.postgres_mfa_repository import PostgresMfaRepository

NOW = datetime(2026, 8, 14, 12, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000001")
CHALLENGE_ID = UUID("00000000-0000-4000-8000-000000000002")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeResult:
    def __init__(self, *, row=None, scalar=None, rowcount=1) -> None:
        self.row = row
        self.scalar = scalar
        self.rowcount = rowcount

    def mappings(self):
        return self

    def one_or_none(self):
        return self.row

    def scalar_one_or_none(self):
        return self.scalar


class FakeConnection:
    def __init__(self, results=()) -> None:
        self.results = iter(results)
        self.executed: list[tuple[object, dict]] = []

    async def execute(self, statement, parameters):
        self.executed.append((statement, parameters))
        return next(self.results, FakeResult())


class FakeConnectionContext:
    def __init__(self, connection) -> None:
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class FakeEngine:
    def __init__(self, results=()) -> None:
        self.connection = FakeConnection(results)

    def connect(self):
        return FakeConnectionContext(self.connection)

    def begin(self):
        return FakeConnectionContext(self.connection)


def session_record() -> SessionRecord:
    return SessionRecord(
        token_hash=b"s" * 32,
        csrf_token_hash=b"c" * 32,
        idle_expires_at=NOW + timedelta(minutes=30),
        absolute_expires_at=NOW + timedelta(hours=8),
    )


@pytest.mark.anyio
async def test_active_challenge_maps_encrypted_fields_without_repr_leak() -> None:
    row = {
        "challenge_id": CHALLENGE_ID,
        "user_id": USER_ID,
        "email": "synthetic@example.invalid",
        "state": "mfa_required",
        "csrf_token_hash": memoryview(b"c" * 32),
        "encrypted_secret": memoryview(b"encrypted-secret"),
        "key_version": "totp-v1",
        "enabled_at": NOW - timedelta(days=1),
        "last_accepted_time_step": 123,
    }
    engine = FakeEngine([FakeResult(row=row)])

    challenge = await PostgresMfaRepository(engine).find_active_challenge(
        b"t" * 32,
        now=NOW,
    )

    assert challenge is not None
    assert challenge.encrypted_totp_secret == b"encrypted-secret"
    assert challenge.last_accepted_time_step == 123
    assert "encrypted-secret" not in repr(challenge)
    assert engine.connection.executed[0][1] == {
        "token_hash": b"t" * 32,
        "now": NOW,
    }


@pytest.mark.anyio
async def test_pending_totp_requires_one_authorized_row() -> None:
    accepted_engine = FakeEngine([FakeResult(rowcount=1)])
    rejected_engine = FakeEngine([FakeResult(rowcount=0)])

    accepted = await PostgresMfaRepository(accepted_engine).save_pending_totp(
        challenge_id=CHALLENGE_ID,
        user_id=USER_ID,
        encrypted_secret=b"encrypted-secret",
        key_version="totp-v1",
        now=NOW,
    )
    rejected = await PostgresMfaRepository(rejected_engine).save_pending_totp(
        challenge_id=CHALLENGE_ID,
        user_id=USER_ID,
        encrypted_secret=b"encrypted-secret",
        key_version="totp-v1",
        now=NOW,
    )

    assert accepted is True
    assert rejected is False


@pytest.mark.anyio
async def test_failed_mfa_updates_buckets_challenge_and_audit() -> None:
    blocked_until = NOW + timedelta(seconds=30)
    engine = FakeEngine(
        [
            FakeResult(scalar=None),
            FakeResult(scalar=blocked_until),
            FakeResult(),
            FakeResult(),
        ]
    )

    result = await PostgresMfaRepository(engine).record_failed_mfa(
        challenge_id=CHALLENGE_ID,
        user_id=USER_ID,
        user_bucket_hash=b"z" * 32,
        ip_bucket_hash=b"a" * 32,
        now=NOW,
    )

    assert result == blocked_until
    calls = engine.connection.executed
    assert calls[0][1]["bucket_key_hash"] == b"a" * 32
    assert calls[1][1]["bucket_key_hash"] == b"z" * 32
    assert calls[2][1] == {"challenge_id": CHALLENGE_ID, "user_id": USER_ID}
    assert calls[3][1] == {
        "challenge_id": CHALLENGE_ID,
        "user_id": USER_ID,
        "now": NOW,
    }


@pytest.mark.anyio
async def test_totp_completion_rotates_session_and_stores_recovery_digests() -> None:
    engine = FakeEngine([FakeResult() for _ in range(16)])
    recovery_codes = tuple(
        RecoveryCodeRecord(bytes([index]) * 32, "recovery-v1")
        for index in range(1, 11)
    )

    completed = await PostgresMfaRepository(engine).complete_totp(
        challenge_id=CHALLENGE_ID,
        user_id=USER_ID,
        accepted_time_step=123456,
        enrollment=True,
        recovery_codes=recovery_codes,
        session=session_record(),
        user_bucket_hash=b"u" * 32,
        now=NOW,
    )

    assert completed is True
    calls = engine.connection.executed
    assert len(calls) == 16
    assert calls[0][1]["accepted_time_step"] == 123456
    assert calls[1][1]["state"] == "mfa_enrollment_required"
    assert [calls[index][1]["code_hash"] for index in range(3, 13)] == [
        item.digest for item in recovery_codes
    ]
    assert calls[13][1]["token_hash"] == b"s" * 32
    assert calls[14][1]["action"] == "auth.mfa.enrollment"
    assert calls[15][1] == {"user_bucket_hash": b"u" * 32}


@pytest.mark.anyio
async def test_replayed_totp_fails_before_session_creation() -> None:
    engine = FakeEngine([FakeResult(rowcount=0)])

    completed = await PostgresMfaRepository(engine).complete_totp(
        challenge_id=CHALLENGE_ID,
        user_id=USER_ID,
        accepted_time_step=123456,
        enrollment=False,
        recovery_codes=(),
        session=session_record(),
        user_bucket_hash=b"u" * 32,
        now=NOW,
    )

    assert completed is False
    assert len(engine.connection.executed) == 1


@pytest.mark.anyio
async def test_recovery_completion_consumes_one_code_then_rotates_session() -> None:
    engine = FakeEngine(
        [
            FakeResult(rowcount=0),
            FakeResult(rowcount=1),
            FakeResult(),
            FakeResult(),
            FakeResult(),
            FakeResult(),
        ]
    )

    completed = await PostgresMfaRepository(engine).complete_recovery(
        challenge_id=CHALLENGE_ID,
        user_id=USER_ID,
        candidate_digests=(
            RecoveryCodeRecord(b"1" * 32, "recovery-v1"),
            RecoveryCodeRecord(b"2" * 32, "recovery-v2"),
        ),
        session=session_record(),
        user_bucket_hash=b"u" * 32,
        now=NOW,
    )

    assert completed is True
    calls = engine.connection.executed
    assert calls[0][1]["key_version"] == "recovery-v1"
    assert calls[1][1]["key_version"] == "recovery-v2"
    assert calls[2][1]["state"] == "mfa_required"
    assert calls[3][1]["token_hash"] == b"s" * 32
