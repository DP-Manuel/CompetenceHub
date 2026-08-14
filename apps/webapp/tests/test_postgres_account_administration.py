from datetime import UTC, datetime
from uuid import UUID

import pytest

from competence_hub_api.auth.account_administration import (
    InitialAdminAlreadyExistsError,
    InitialAdminConfigurationError,
)
from competence_hub_api.auth.postgres_account_administration import (
    PostgresInitialAdminRepository,
)

NOW = datetime(2026, 8, 14, 14, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000081")
ROLE_ID = UUID("00000000-0000-4000-8000-000000000082")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeResult:
    def __init__(self, scalar=None) -> None:
        self.scalar = scalar

    def scalar_one(self):
        return self.scalar

    def scalar_one_or_none(self):
        return self.scalar


class FakeConnection:
    def __init__(self, results=()) -> None:
        self.results = iter(results)
        self.executed: list[tuple[object, dict | None]] = []

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


@pytest.mark.anyio
async def test_initial_admin_is_created_and_audited_in_one_transaction() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(False),
            FakeResult(ROLE_ID),
            FakeResult(USER_ID),
            FakeResult(),
            FakeResult(),
            FakeResult(),
        ]
    )
    repository = PostgresInitialAdminRepository(engine)

    result = await repository.create_initial_admin(
        normalized_email="admin@example.invalid",
        display_name="Synthetic Admin",
        password_hash="synthetic-argon2id-hash",
        now=NOW,
    )

    assert result == USER_ID
    calls = engine.connection.executed
    assert len(calls) == 7
    assert calls[3][1] == {
        "normalized_email": "admin@example.invalid",
        "display_name": "Synthetic Admin",
        "now": NOW,
    }
    assert calls[4][1] == {"user_id": USER_ID, "role_id": ROLE_ID, "now": NOW}
    assert calls[5][1] == {
        "user_id": USER_ID,
        "password_hash": "synthetic-argon2id-hash",
        "now": NOW,
    }
    assert calls[6][1] == {"user_id": USER_ID, "now": NOW}


@pytest.mark.anyio
async def test_existing_active_admin_closes_bootstrap_before_writes() -> None:
    engine = FakeEngine([FakeResult(), FakeResult(True)])
    repository = PostgresInitialAdminRepository(engine)

    with pytest.raises(InitialAdminAlreadyExistsError):
        await repository.create_initial_admin(
            normalized_email="admin@example.invalid",
            display_name="Synthetic Admin",
            password_hash="synthetic-argon2id-hash",
            now=NOW,
        )

    assert len(engine.connection.executed) == 2


@pytest.mark.anyio
async def test_missing_active_admin_role_fails_closed_before_user_creation() -> None:
    engine = FakeEngine([FakeResult(), FakeResult(False), FakeResult(None)])
    repository = PostgresInitialAdminRepository(engine)

    with pytest.raises(InitialAdminConfigurationError):
        await repository.create_initial_admin(
            normalized_email="admin@example.invalid",
            display_name="Synthetic Admin",
            password_hash="synthetic-argon2id-hash",
            now=NOW,
        )

    assert len(engine.connection.executed) == 3
