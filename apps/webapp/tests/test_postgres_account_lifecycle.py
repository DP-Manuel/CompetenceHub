from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.account_lifecycle import (
    IdempotencyConflictError,
    InvitationConflictError,
)
from competence_hub_api.auth.postgres_account_lifecycle import (
    PostgresAccountLifecycleRepository,
)

NOW = datetime(2026, 8, 14, 15, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000091")
ACTOR_ID = UUID("00000000-0000-4000-8000-000000000092")
ROLE_ID = UUID("00000000-0000-4000-8000-000000000094")
TOKEN_ID = UUID("00000000-0000-4000-8000-000000000095")
OUTBOX_ID = UUID("00000000-0000-4000-8000-000000000096")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeResult:
    def __init__(self, *, scalar=None, row=None, rows=()) -> None:
        self.scalar = scalar
        self.row = row
        self.rows = list(rows)

    def scalar_one(self):
        return self.scalar

    def scalar_one_or_none(self):
        return self.scalar

    def mappings(self):
        return self

    def one_or_none(self):
        return self.row

    def all(self):
        return self.rows


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

    def connect(self):
        return FakeContext(self.connection)

    def begin(self):
        return FakeContext(self.connection)


@pytest.mark.anyio
async def test_rate_limit_attempts_are_stable_and_action_bounded() -> None:
    blocked_until = NOW + timedelta(seconds=30)
    engine = FakeEngine([FakeResult(scalar=None), FakeResult(scalar=blocked_until)])
    repository = PostgresAccountLifecycleRepository(engine)

    result = await repository.record_rate_limit_attempt(
        "password_reset",
        (b"z" * 32, b"a" * 32),
        now=NOW,
    )

    assert result == blocked_until
    calls = engine.connection.executed
    assert calls[0][1]["bucket_hash"] == b"a" * 32
    assert calls[1][1]["bucket_hash"] == b"z" * 32
    assert calls[0][1]["threshold"] == 5
    with pytest.raises(ValueError, match="action"):
        await repository.find_rate_limit("login", (b"a" * 32,), now=NOW)


@pytest.mark.anyio
async def test_idempotency_lookup_returns_stable_result_without_mutation() -> None:
    engine = FakeEngine(
        [
            FakeResult(
                row={
                    "request_fingerprint": b"f" * 32,
                    "result_entity_id": USER_ID,
                }
            )
        ]
    )
    repository = PostgresAccountLifecycleRepository(engine)

    result = await repository.find_invitation_idempotency(
        actor_user_id=ACTOR_ID,
        idempotency_key_hash=b"i" * 32,
        request_fingerprint=b"f" * 32,
        now=NOW,
    )

    assert result is not None
    assert result.user_id == USER_ID
    assert result.replayed is True
    assert len(engine.connection.executed) == 1


@pytest.mark.anyio
async def test_new_invitation_creates_inactive_user_role_token_and_audit() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(),
            FakeResult(row=None),
            FakeResult(),
            FakeResult(row=None),
            FakeResult(scalar=USER_ID),
            FakeResult(rows=[{"id": ROLE_ID, "code": "internal"}]),
            FakeResult(),
            FakeResult(),
            FakeResult(scalar=TOKEN_ID),
            FakeResult(),
            FakeResult(),
            FakeResult(),
        ]
    )
    repository = PostgresAccountLifecycleRepository(engine)

    result = await repository.issue_invitation(
        actor_user_id=ACTOR_ID,
        normalized_email="person@example.invalid",
        display_name="Synthetic Person",
        role_codes=("internal",),
        token_hash=b"t" * 32,
        outbox_id=OUTBOX_ID,
        encrypted_payload=b"encrypted-token",
        payload_key_version="outbox-v1",
        idempotency_key_hash=b"i" * 32,
        request_fingerprint=b"f" * 32,
        now=NOW,
        expires_at=NOW + timedelta(hours=24),
        idempotency_expires_at=NOW + timedelta(hours=24),
    )

    assert result.user_id == USER_ID
    assert result.replayed is False
    calls = engine.connection.executed
    assert len(calls) == 13
    assert calls[5][1] == {
        "normalized_email": "person@example.invalid",
        "display_name": "Synthetic Person",
        "now": NOW,
    }
    role_lookup_sql = str(calls[6][0]).upper()
    assert "FROM COMPETENCE_HUB.ROLES" in role_lookup_sql
    assert "FOR SHARE" not in role_lookup_sql
    assert calls[7][1]["actor_user_id"] == ACTOR_ID
    assert calls[9][1]["token_hash"] == b"t" * 32
    assert calls[10][1]["encrypted_payload"] == b"encrypted-token"
    assert calls[11][1]["action"] == "auth.invitation.issue"
    assert calls[12][1]["key_hash"] == b"i" * 32


@pytest.mark.anyio
async def test_existing_provisioned_account_rejects_reinvitation_before_writes() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(),
            FakeResult(row=None),
            FakeResult(),
            FakeResult(
                row={"id": USER_ID, "active": True, "has_credential": True}
            ),
        ]
    )
    repository = PostgresAccountLifecycleRepository(engine)

    with pytest.raises(InvitationConflictError):
        await repository.issue_invitation(
            actor_user_id=ACTOR_ID,
            normalized_email="person@example.invalid",
            display_name="Synthetic Person",
            role_codes=("internal",),
            token_hash=b"t" * 32,
            outbox_id=OUTBOX_ID,
            encrypted_payload=b"encrypted-token",
            payload_key_version="outbox-v1",
            idempotency_key_hash=b"i" * 32,
            request_fingerprint=b"f" * 32,
            now=NOW,
            expires_at=NOW + timedelta(hours=24),
            idempotency_expires_at=NOW + timedelta(hours=24),
        )

    assert len(engine.connection.executed) == 5


@pytest.mark.anyio
async def test_same_idempotency_request_replays_without_new_token_or_outbox() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(),
            FakeResult(
                row={
                    "request_fingerprint": b"f" * 32,
                    "result_entity_id": USER_ID,
                }
            ),
        ]
    )
    repository = PostgresAccountLifecycleRepository(engine)

    result = await repository.issue_invitation(
        actor_user_id=ACTOR_ID,
        normalized_email="person@example.invalid",
        display_name="Synthetic Person",
        role_codes=("internal",),
        token_hash=b"t" * 32,
        outbox_id=OUTBOX_ID,
        encrypted_payload=b"encrypted-token",
        payload_key_version="outbox-v1",
        idempotency_key_hash=b"i" * 32,
        request_fingerprint=b"f" * 32,
        now=NOW,
        expires_at=NOW + timedelta(hours=24),
        idempotency_expires_at=NOW + timedelta(hours=24),
    )

    assert result.user_id == USER_ID
    assert result.replayed is True
    assert len(engine.connection.executed) == 3


@pytest.mark.anyio
async def test_idempotency_key_reuse_with_other_request_is_rejected() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(),
            FakeResult(
                row={
                    "request_fingerprint": b"x" * 32,
                    "result_entity_id": USER_ID,
                }
            ),
        ]
    )
    repository = PostgresAccountLifecycleRepository(engine)

    with pytest.raises(IdempotencyConflictError):
        await repository.issue_invitation(
            actor_user_id=ACTOR_ID,
            normalized_email="other@example.invalid",
            display_name="Other Person",
            role_codes=("internal",),
            token_hash=b"t" * 32,
            outbox_id=OUTBOX_ID,
            encrypted_payload=b"encrypted-token",
            payload_key_version="outbox-v1",
            idempotency_key_hash=b"i" * 32,
            request_fingerprint=b"f" * 32,
            now=NOW,
            expires_at=NOW + timedelta(hours=24),
            idempotency_expires_at=NOW + timedelta(hours=24),
        )

    assert len(engine.connection.executed) == 3


@pytest.mark.anyio
@pytest.mark.parametrize("user_id", [USER_ID, None])
async def test_reset_request_keeps_unknown_and_known_paths_data_minimal(
    user_id: UUID | None,
) -> None:
    results = [FakeResult(scalar=user_id)]
    if user_id is not None:
        results.extend(
            (
                FakeResult(),
                FakeResult(scalar=TOKEN_ID),
                FakeResult(),
            )
        )
    results.append(FakeResult())
    engine = FakeEngine(results)
    repository = PostgresAccountLifecycleRepository(engine)

    result = await repository.request_password_reset(
        normalized_email="person@example.invalid",
        token_hash=b"r" * 32,
        outbox_id=OUTBOX_ID,
        encrypted_payload=b"encrypted-token",
        payload_key_version="outbox-v1",
        now=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )

    assert result == user_id
    audit = engine.connection.executed[-1][1]
    assert audit["action"] == "auth.password_reset.request"
    assert audit["user_id"] == user_id
    assert "person@example.invalid" not in repr(audit)
    if user_id is not None:
        outbox = engine.connection.executed[-2][1]
        assert outbox["one_time_token_id"] == TOKEN_ID
        assert outbox["recipient_email"] == "person@example.invalid"


@pytest.mark.anyio
async def test_accept_invitation_consumes_token_and_creates_enrollment_challenge() -> None:
    engine = FakeEngine([FakeResult(scalar=USER_ID)])
    repository = PostgresAccountLifecycleRepository(engine)

    result = await repository.accept_invitation(
        token_hash=b"t" * 32,
        password_hash="synthetic-argon2id-hash",
        login_token_hash=b"l" * 32,
        csrf_token_hash=b"c" * 32,
        now=NOW,
        challenge_expires_at=NOW + timedelta(minutes=5),
    )

    assert result == USER_ID
    calls = engine.connection.executed
    assert len(calls) == 8
    assert calls[1][1]["password_hash"] == "synthetic-argon2id-hash"
    assert calls[3][1]["token_hash"] == b"t" * 32
    assert calls[6][1]["login_token_hash"] == b"l" * 32
    assert calls[7][1]["action"] == "auth.invitation.accept"


@pytest.mark.anyio
async def test_invalid_token_stops_before_mutation() -> None:
    engine = FakeEngine([FakeResult(scalar=None)])
    repository = PostgresAccountLifecycleRepository(engine)

    result = await repository.confirm_password_reset(
        token_hash=b"x" * 32,
        password_hash="synthetic-argon2id-hash",
        now=NOW,
    )

    assert result is None
    assert len(engine.connection.executed) == 1


@pytest.mark.anyio
async def test_password_reset_revokes_tokens_sessions_and_challenges_atomically() -> None:
    engine = FakeEngine([FakeResult(scalar=USER_ID)])
    repository = PostgresAccountLifecycleRepository(engine)

    result = await repository.confirm_password_reset(
        token_hash=b"r" * 32,
        password_hash="synthetic-argon2id-hash",
        now=NOW,
    )

    assert result == USER_ID
    calls = engine.connection.executed
    assert len(calls) == 7
    assert calls[1][1]["password_hash"] == "synthetic-argon2id-hash"
    assert calls[2][1]["token_hash"] == b"r" * 32
    assert calls[4][1]["reason"] == "password_reset"
    assert calls[6][1]["action"] == "auth.password_reset.confirm"
