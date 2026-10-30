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
    assert "pg_advisory_xact_lock" in str(calls[0][0])
    assert "FOR SHARE" not in str(calls[2][0])
    assert "FOR UPDATE" not in str(calls[2][0])
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


@pytest.mark.anyio
async def test_strict_bootstrap_locks_and_checks_before_any_write() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(),
            FakeResult(True),
            FakeResult(True),
            FakeResult(False),
            FakeResult(ROLE_ID),
            FakeResult(USER_ID),
            FakeResult(),
            FakeResult(),
            FakeResult(),
        ]
    )
    repository = PostgresInitialAdminRepository(
        engine,
        require_empty_target=True,
        bootstrap_deadline=NOW,
    )
    assert (
        await repository.create_initial_admin(
            normalized_email="admin@example.invalid",
            display_name="Synthetic Admin",
            password_hash="synthetic-argon2id-hash",
            now=NOW,
        )
        == USER_ID
    )
    calls = engine.connection.executed
    assert len(calls) == 10
    assert "pg_advisory_xact_lock" in str(calls[0][0])
    lock_sql = str(calls[1][0])
    assert lock_sql == (
        "LOCK TABLE competence_hub.portal_users, competence_hub.user_roles, "
        "competence_hub.coaches IN SHARE ROW EXCLUSIVE MODE"
    )
    assert "NOT EXISTS (SELECT 1 FROM competence_hub.portal_users)" in str(calls[2][0])
    assert "NOT EXISTS (SELECT 1 FROM competence_hub.coaches)" in str(calls[2][0])
    assert str(calls[3][0]) == "SELECT clock_timestamp() <= :bootstrap_deadline"
    assert calls[3][1] == {"bootstrap_deadline": NOW}
    assert all(
        not str(statement).lstrip().startswith("INSERT") for statement, _ in calls[:6]
    )
    assert str(calls[6][0]).lstrip().startswith("INSERT")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "empty,fresh,expected_calls", [(False, True, 3), (True, False, 4)]
)
async def test_strict_bootstrap_rejects_nonempty_or_expired_before_writes(
    empty,
    fresh,
    expected_calls,
) -> None:
    engine = FakeEngine(
        [FakeResult(), FakeResult(), FakeResult(empty), FakeResult(fresh)]
    )
    repository = PostgresInitialAdminRepository(
        engine,
        require_empty_target=True,
        bootstrap_deadline=NOW,
    )
    with pytest.raises(InitialAdminConfigurationError):
        await repository.create_initial_admin(
            normalized_email="admin@example.invalid",
            display_name="Synthetic Admin",
            password_hash="synthetic-argon2id-hash",
            now=NOW,
        )
    assert len(engine.connection.executed) == expected_calls
    assert all(
        not str(statement).lstrip().startswith("INSERT")
        for statement, _ in engine.connection.executed
    )


@pytest.mark.anyio
async def test_deadline_can_be_required_without_changing_default_empty_target_policy() -> (
    None
):
    engine = FakeEngine([FakeResult(), FakeResult(False)])
    repository = PostgresInitialAdminRepository(engine, bootstrap_deadline=NOW)
    with pytest.raises(InitialAdminConfigurationError, match="deadline has expired"):
        await repository.create_initial_admin(
            normalized_email="admin@example.invalid",
            display_name="Synthetic Admin",
            password_hash="synthetic-argon2id-hash",
            now=NOW,
        )
    assert len(engine.connection.executed) == 2
    assert (
        str(engine.connection.executed[1][0])
        == "SELECT clock_timestamp() <= :bootstrap_deadline"
    )


@pytest.mark.parametrize("deadline", [NOW.replace(tzinfo=None), "not-a-datetime"])
def test_invalid_deadline_rejected_before_transaction(deadline) -> None:
    engine = FakeEngine()
    with pytest.raises(InitialAdminConfigurationError, match="timezone-aware"):
        PostgresInitialAdminRepository(engine, bootstrap_deadline=deadline)
    assert engine.connection.executed == []
