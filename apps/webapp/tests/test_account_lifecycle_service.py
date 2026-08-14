from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.account_lifecycle import (
    AccountLifecycleService,
    InvitationIssueResult,
    LifecycleAccepted,
    LifecycleQueued,
    LifecycleRateLimited,
    LifecycleRejected,
)
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.security.secret_encryption import SecretCipher
from competence_hub_api.security.tokens import digest_token

NOW = datetime(2026, 8, 14, 15, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000091")
ACTOR_ID = UUID("00000000-0000-4000-8000-000000000092")
SESSION_ID = UUID("00000000-0000-4000-8000-000000000093")
HMAC_KEY = b"synthetic-lifecycle-rate-key-32b"
IDEMPOTENCY_HMAC_KEY = b"synthetic-idempotency-key-32bytes"
OUTBOX_KEY = b"o" * 32
IDEMPOTENCY_KEY = "synthetic-idempotency-key-0001"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakePasswordHasher:
    def __init__(self) -> None:
        self.passwords: list[str] = []

    def hash(self, password: str) -> str:
        self.passwords.append(password)
        return "synthetic-argon2id-hash"


class FakeLifecycleRepository:
    def __init__(self) -> None:
        self.preexisting_block = None
        self.recorded_block = None
        self.reset_user_id: UUID | None = USER_ID
        self.accepted_invitation_user_id: UUID | None = USER_ID
        self.reset_confirmed_user_id: UUID | None = USER_ID
        self.rate_lookups: list[dict] = []
        self.rate_attempts: list[dict] = []
        self.invitations: list[dict] = []
        self.reset_requests: list[dict] = []
        self.invitation_accepts: list[dict] = []
        self.reset_confirms: list[dict] = []
        self.idempotency_result = None

    async def find_invitation_idempotency(self, **values):
        return self.idempotency_result

    async def find_rate_limit(self, action, bucket_hashes, *, now):
        self.rate_lookups.append(
            {"action": action, "bucket_hashes": bucket_hashes, "now": now}
        )
        return self.preexisting_block

    async def record_rate_limit_attempt(self, action, bucket_hashes, *, now):
        self.rate_attempts.append(
            {"action": action, "bucket_hashes": bucket_hashes, "now": now}
        )
        return self.recorded_block

    async def issue_invitation(self, **values):
        self.invitations.append(values)
        return InvitationIssueResult(user_id=USER_ID, replayed=False)

    async def request_password_reset(self, **values):
        self.reset_requests.append(values)
        return self.reset_user_id

    async def accept_invitation(self, **values):
        self.invitation_accepts.append(values)
        return self.accepted_invitation_user_id

    async def confirm_password_reset(self, **values):
        self.reset_confirms.append(values)
        return self.reset_confirmed_user_id


def _actor(*, roles=("admin",), authenticated_at=NOW) -> SessionPrincipal:
    return SessionPrincipal(
        session_id=SESSION_ID,
        user_id=ACTOR_ID,
        display_name="Synthetic Admin",
        roles=roles,
        authenticated_at=authenticated_at,
        idle_expires_at=NOW + timedelta(minutes=30),
        absolute_expires_at=NOW + timedelta(hours=8),
        csrf_token_hash=b"c" * 32,
    )


def _service(repository=None, hasher=None) -> AccountLifecycleService:
    return AccountLifecycleService(
        repository or FakeLifecycleRepository(),
        hasher or FakePasswordHasher(),
        rate_limit_hmac_key=HMAC_KEY,
        idempotency_hmac_key=IDEMPOTENCY_HMAC_KEY,
        outbox_cipher=_service_cipher(),
    )


def _service_cipher() -> SecretCipher:
    return SecretCipher(
        {"outbox-v1": OUTBOX_KEY},
        "outbox-v1",
        context="auth-token-outbox",
    )


@pytest.mark.anyio
async def test_fresh_admin_queues_internal_invitation_without_exposing_token() -> None:
    repository = FakeLifecycleRepository()

    outcome = await _service(repository).issue_invitation(
        actor=_actor(),
        email=" PERSON@Example.Invalid ",
        display_name=" Synthetic Person ",
        role_codes=("internal",),
        idempotency_key=IDEMPOTENCY_KEY,
        client_ip="192.0.2.40",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleQueued)
    assert outcome.recipient_user_id == USER_ID
    invitation = repository.invitations[0]
    assert invitation["actor_user_id"] == ACTOR_ID
    assert invitation["normalized_email"] == "person@example.invalid"
    assert invitation["display_name"] == "Synthetic Person"
    assert invitation["role_codes"] == ("internal",)
    plaintext_token = _service_cipher().decrypt(
        invitation["encrypted_payload"],
        key_version=invitation["payload_key_version"],
        subject_id=f"invitation:{invitation['outbox_id']}",
    )
    assert digest_token(plaintext_token) == invitation["token_hash"]
    assert plaintext_token not in repr(outcome)
    assert plaintext_token not in repr(invitation)
    assert len(invitation["idempotency_key_hash"]) == 32
    assert len(invitation["request_fingerprint"]) == 32
    assert len(repository.rate_attempts[0]["bucket_hashes"]) == 2


@pytest.mark.anyio
async def test_idempotent_invitation_replay_bypasses_rate_limit_and_token_creation() -> None:
    repository = FakeLifecycleRepository()
    repository.idempotency_result = InvitationIssueResult(
        user_id=USER_ID,
        replayed=True,
    )

    outcome = await _service(repository).issue_invitation(
        actor=_actor(),
        email="person@example.invalid",
        display_name="Synthetic Person",
        role_codes=("internal",),
        idempotency_key=IDEMPOTENCY_KEY,
        client_ip="192.0.2.40",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleQueued)
    assert outcome.replayed is True
    assert repository.rate_lookups == []
    assert repository.invitations == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("actor", "roles"),
    [
        (_actor(roles=("internal",)), ("internal",)),
        (_actor(authenticated_at=NOW - timedelta(minutes=16)), ("internal",)),
        (_actor(), ("admin",)),
        (_actor(), ("coach",)),
    ],
)
async def test_invitation_rejects_insufficient_actor_or_roles_before_token_work(
    actor: SessionPrincipal,
    roles: tuple[str, ...],
) -> None:
    repository = FakeLifecycleRepository()

    outcome = await _service(repository).issue_invitation(
        actor=actor,
        email="person@example.invalid",
        display_name="Synthetic Person",
        role_codes=roles,
        idempotency_key=IDEMPOTENCY_KEY,
        client_ip="192.0.2.40",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleRejected)
    assert repository.rate_lookups == []
    assert repository.invitations == []


@pytest.mark.anyio
async def test_unknown_reset_request_has_generic_queued_shape() -> None:
    repository = FakeLifecycleRepository()
    repository.reset_user_id = None

    outcome = await _service(repository).request_password_reset(
        email="unknown@example.invalid",
        client_ip="192.0.2.41",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleQueued)
    assert outcome.recipient_user_id is None
    assert len(repository.reset_requests[0]["token_hash"]) == 32
    assert "unknown@example.invalid" not in repr(outcome)


@pytest.mark.anyio
async def test_existing_reset_request_only_passes_encrypted_token_to_repository() -> None:
    repository = FakeLifecycleRepository()

    outcome = await _service(repository).request_password_reset(
        email="person@example.invalid",
        client_ip="192.0.2.41",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleQueued)
    assert outcome.recipient_user_id == USER_ID
    values = repository.reset_requests[0]
    plaintext_token = _service_cipher().decrypt(
        values["encrypted_payload"],
        key_version=values["payload_key_version"],
        subject_id=f"password_reset:{values['outbox_id']}",
    )
    assert digest_token(plaintext_token) == values["token_hash"]
    assert plaintext_token not in repr(outcome)
    assert plaintext_token not in repr(values)


@pytest.mark.anyio
async def test_invitation_acceptance_hashes_password_and_rotates_to_enrollment() -> None:
    repository = FakeLifecycleRepository()
    hasher = FakePasswordHasher()

    outcome = await _service(repository, hasher).accept_invitation(
        token="synthetic-invitation-token",
        password="synthetic secure passphrase",
        client_ip="192.0.2.42",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleAccepted)
    assert outcome.login_token and outcome.csrf_token
    assert outcome.login_token not in repr(outcome)
    assert outcome.csrf_token not in repr(outcome)
    assert hasher.passwords == ["synthetic secure passphrase"]
    values = repository.invitation_accepts[0]
    assert values["password_hash"] == "synthetic-argon2id-hash"
    assert values["login_token_hash"] != outcome.login_token.encode("ascii")
    assert values["csrf_token_hash"] != outcome.csrf_token.encode("ascii")


@pytest.mark.anyio
async def test_consumed_or_unknown_invitation_is_generically_rejected() -> None:
    repository = FakeLifecycleRepository()
    repository.accepted_invitation_user_id = None

    outcome = await _service(repository).accept_invitation(
        token="synthetic-invalid-token",
        password="synthetic secure passphrase",
        client_ip="192.0.2.42",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleRejected)


@pytest.mark.anyio
async def test_password_reset_confirmation_has_no_session_or_token_output() -> None:
    repository = FakeLifecycleRepository()
    hasher = FakePasswordHasher()

    outcome = await _service(repository, hasher).confirm_password_reset(
        token="synthetic-reset-token",
        password="synthetic secure passphrase",
        client_ip="192.0.2.43",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleAccepted)
    assert outcome.login_token is None
    assert outcome.csrf_token is None
    assert repository.reset_confirms[0]["password_hash"] == (
        "synthetic-argon2id-hash"
    )


@pytest.mark.anyio
async def test_preexisting_rate_limit_stops_repository_mutation_and_hashing() -> None:
    repository = FakeLifecycleRepository()
    repository.preexisting_block = NOW + timedelta(seconds=45)
    hasher = FakePasswordHasher()

    outcome = await _service(repository, hasher).confirm_password_reset(
        token="synthetic-reset-token",
        password="synthetic secure passphrase",
        client_ip="192.0.2.43",
        now=NOW,
    )

    assert isinstance(outcome, LifecycleRateLimited)
    assert outcome.retry_after_seconds == 45
    assert hasher.passwords == []
    assert repository.reset_confirms == []
