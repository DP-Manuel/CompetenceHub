from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.postgres_login_repository import (
    PostgresLoginRepository,
)

NOW = datetime(2026, 8, 14, 10, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000001")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeResult:
    def __init__(self, *, row=None, scalar=None) -> None:
        self.row = row
        self.scalar = scalar

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


@pytest.mark.anyio
async def test_login_account_maps_only_required_auth_fields() -> None:
    row = {
        "user_id": USER_ID,
        "active": True,
        "password_hash": "synthetic-argon-hash",
        "roles": ["admin", "internal"],
        "mfa_enrolled": True,
    }
    engine = FakeEngine([FakeResult(row=row)])
    repository = PostgresLoginRepository(engine)

    account = await repository.find_login_account("person@example.invalid")

    assert account is not None
    assert account.user_id == USER_ID
    assert account.active is True
    assert account.roles == ("admin", "internal")
    assert account.mfa_enrolled is True
    assert "synthetic-argon-hash" not in repr(account)
    assert engine.connection.executed[0][1] == {
        "normalized_email": "person@example.invalid"
    }


@pytest.mark.anyio
async def test_login_account_returns_none_for_unknown_email() -> None:
    repository = PostgresLoginRepository(FakeEngine([FakeResult(row=None)]))

    assert await repository.find_login_account("unknown@example.invalid") is None


@pytest.mark.anyio
async def test_rate_limit_lookup_uses_only_hmac_digests() -> None:
    blocked_until = NOW + timedelta(seconds=30)
    engine = FakeEngine([FakeResult(scalar=blocked_until)])
    repository = PostgresLoginRepository(engine)

    result = await repository.find_login_rate_limit(
        b"a" * 32,
        b"i" * 32,
        now=NOW,
    )

    assert result == blocked_until
    assert engine.connection.executed[0][1] == {
        "account_bucket_hash": b"a" * 32,
        "ip_bucket_hash": b"i" * 32,
        "now": NOW,
    }


@pytest.mark.anyio
async def test_failed_login_updates_buckets_in_stable_order_and_audits() -> None:
    blocked_until = NOW + timedelta(seconds=30)
    engine = FakeEngine(
        [
            FakeResult(scalar=None),
            FakeResult(scalar=blocked_until),
            FakeResult(),
        ]
    )
    repository = PostgresLoginRepository(engine)

    result = await repository.record_failed_login(
        b"z" * 32,
        b"a" * 32,
        user_id=USER_ID,
        now=NOW,
    )

    assert result == blocked_until
    calls = engine.connection.executed
    assert calls[0][1]["bucket_key_hash"] == b"a" * 32
    assert calls[1][1]["bucket_key_hash"] == b"z" * 32
    assert calls[0][1]["threshold"] == 5
    assert calls[0][1]["window_cutoff"] == NOW - timedelta(minutes=15)
    assert calls[2][1] == {"user_id": USER_ID, "now": NOW}


@pytest.mark.anyio
async def test_success_creates_challenge_and_clears_only_account_bucket() -> None:
    engine = FakeEngine([FakeResult(), FakeResult()])
    repository = PostgresLoginRepository(engine)

    await repository.create_login_challenge(
        user_id=USER_ID,
        token_hash=b"t" * 32,
        csrf_token_hash=b"c" * 32,
        state="mfa_required",
        account_bucket_hash=b"a" * 32,
        now=NOW,
        expires_at=NOW + timedelta(minutes=5),
    )

    calls = engine.connection.executed
    assert calls[0][1] == {
        "user_id": USER_ID,
        "token_hash": b"t" * 32,
        "csrf_token_hash": b"c" * 32,
        "state": "mfa_required",
        "now": NOW,
        "expires_at": NOW + timedelta(minutes=5),
    }
    assert calls[1][1] == {"account_bucket_hash": b"a" * 32}


@pytest.mark.anyio
async def test_challenge_rejects_invalid_state_or_expiry() -> None:
    repository = PostgresLoginRepository(FakeEngine())

    with pytest.raises(ValueError, match="state"):
        await repository.create_login_challenge(
            user_id=USER_ID,
            token_hash=b"t" * 32,
            csrf_token_hash=b"c" * 32,
            state="complete",
            account_bucket_hash=b"a" * 32,
            now=NOW,
            expires_at=NOW + timedelta(minutes=5),
        )

    with pytest.raises(ValueError, match="expiry"):
        await repository.create_login_challenge(
            user_id=USER_ID,
            token_hash=b"t" * 32,
            csrf_token_hash=b"c" * 32,
            state="mfa_required",
            account_bucket_hash=b"a" * 32,
            now=NOW,
            expires_at=NOW,
        )
