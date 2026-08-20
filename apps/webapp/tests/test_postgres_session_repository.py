from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.postgres_session_repository import (
    PostgresSessionRepository,
)

NOW = datetime(2026, 8, 13, 14, 0, tzinfo=UTC)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeResult:
    def __init__(self, row):
        self._row = row

    def mappings(self):
        return self

    def one_or_none(self):
        return self._row


class FakeConnection:
    def __init__(self, rows):
        self._rows = iter(rows)
        self.executed = []

    async def execute(self, statement, parameters):
        self.executed.append((statement, parameters))
        return FakeResult(next(self._rows, None))


class FakeConnectionContext:
    def __init__(self, connection):
        self._connection = connection

    async def __aenter__(self):
        return self._connection

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class FakeEngine:
    def __init__(self, rows=()):
        self.connection = FakeConnection(rows)

    def begin(self):
        return FakeConnectionContext(self.connection)

    def connect(self):
        return FakeConnectionContext(self.connection)


def _row():
    return {
        "session_id": UUID("00000000-0000-4000-8000-000000000001"),
        "user_id": UUID("00000000-0000-4000-8000-000000000002"),
        "display_name": "Synthetic Internal User",
        "roles": ["admin", "internal"],
        "authenticated_at": NOW - timedelta(minutes=5),
        "idle_expires_at": NOW + timedelta(minutes=30),
        "absolute_expires_at": NOW + timedelta(hours=7),
        "csrf_token_hash": memoryview(b"c" * 32),
    }


@pytest.mark.anyio
async def test_refresh_maps_database_row_and_uses_digest_only() -> None:
    engine = FakeEngine([_row()])
    repository = PostgresSessionRepository(engine)
    token_hash = b"s" * 32

    principal = await repository.refresh_active_session(
        token_hash,
        now=NOW,
        idle_timeout=timedelta(minutes=30),
    )

    assert principal is not None
    assert principal.roles == ("admin", "internal")
    assert principal.csrf_token_hash == b"c" * 32
    assert engine.connection.executed[0][1] == {
        "token_hash": token_hash,
        "now": NOW,
        "idle_timeout_seconds": 1800,
    }


@pytest.mark.anyio
async def test_find_returns_none_for_unknown_or_inactive_session() -> None:
    engine = FakeEngine([None])
    repository = PostgresSessionRepository(engine)

    principal = await repository.find_active_session(b"s" * 32, now=NOW)

    assert principal is None


@pytest.mark.anyio
async def test_csrf_rotation_is_atomic_and_uses_only_digests() -> None:
    row = _row()
    row["csrf_token_hash"] = memoryview(b"n" * 32)
    engine = FakeEngine([row])
    repository = PostgresSessionRepository(engine)

    principal = await repository.rotate_active_session_csrf(
        b"s" * 32,
        csrf_token_hash=b"n" * 32,
        now=NOW,
        idle_timeout=timedelta(minutes=30),
    )

    assert principal is not None
    assert principal.csrf_token_hash == b"n" * 32
    assert engine.connection.executed[0][1] == {
        "token_hash": b"s" * 32,
        "csrf_token_hash": b"n" * 32,
        "now": NOW,
        "idle_timeout_seconds": 1800,
    }


@pytest.mark.anyio
async def test_revoke_uses_fixed_reason_and_session_digest() -> None:
    engine = FakeEngine()
    repository = PostgresSessionRepository(engine)
    token_hash = b"s" * 32

    await repository.revoke_session(
        token_hash,
        now=NOW,
        reason="user_logout",
    )

    assert engine.connection.executed[0][1] == {
        "token_hash": token_hash,
        "now": NOW,
        "reason": "user_logout",
    }


@pytest.mark.anyio
async def test_revoke_rejects_empty_reason() -> None:
    repository = PostgresSessionRepository(FakeEngine())

    with pytest.raises(ValueError):
        await repository.revoke_session(
            b"s" * 32,
            now=NOW,
            reason=" ",
        )
