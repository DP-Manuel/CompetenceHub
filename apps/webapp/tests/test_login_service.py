from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.login_repository import LoginAccount
from competence_hub_api.auth.login_service import (
    LoginAccepted,
    LoginRateLimited,
    LoginRejected,
    LoginService,
)

NOW = datetime(2026, 8, 14, 10, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000001")
HMAC_KEY = b"synthetic-rate-limit-key-32-bytes"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakePasswordVerifier:
    def __init__(self, matches: bool) -> None:
        self.matches = matches
        self.calls: list[tuple[str, str]] = []

    def verify(self, encoded_hash: str, password: str) -> bool:
        self.calls.append((encoded_hash, password))
        return self.matches


class FakeLoginRepository:
    def __init__(self, account: LoginAccount | None = None) -> None:
        self.account = account
        self.preexisting_block: datetime | None = None
        self.failure_block: datetime | None = None
        self.lookups: list[str] = []
        self.rate_checks: list[tuple[bytes, bytes, datetime]] = []
        self.failures: list[tuple[bytes, bytes, UUID | None, datetime]] = []
        self.challenges: list[dict] = []

    async def find_login_account(self, normalized_email: str):
        self.lookups.append(normalized_email)
        return self.account

    async def find_login_rate_limit(
        self,
        account_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        *,
        now: datetime,
    ):
        self.rate_checks.append((account_bucket_hash, ip_bucket_hash, now))
        return self.preexisting_block

    async def record_failed_login(
        self,
        account_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        *,
        user_id: UUID | None,
        now: datetime,
    ):
        self.failures.append((account_bucket_hash, ip_bucket_hash, user_id, now))
        return self.failure_block

    async def create_login_challenge(self, **values) -> None:
        self.challenges.append(values)


def _account(
    *,
    active: bool = True,
    roles: tuple[str, ...] = ("internal",),
    mfa_enrolled: bool = False,
) -> LoginAccount:
    return LoginAccount(
        user_id=USER_ID,
        password_hash="synthetic-real-hash",
        active=active,
        roles=roles,
        mfa_enrolled=mfa_enrolled,
    )


def _service(repository, verifier) -> LoginService:
    return LoginService(
        repository,
        verifier,
        dummy_password_hash="synthetic-dummy-hash",
        rate_limit_hmac_key=HMAC_KEY,
    )


@pytest.mark.anyio
async def test_unknown_account_uses_dummy_hash_and_generic_rejection() -> None:
    repository = FakeLoginRepository()
    verifier = FakePasswordVerifier(False)

    outcome = await _service(repository, verifier).authenticate(
        normalized_email="unknown@example.invalid",
        password="synthetic password",
        client_ip="192.0.2.10",
        now=NOW,
    )

    assert isinstance(outcome, LoginRejected)
    assert verifier.calls == [("synthetic-dummy-hash", "synthetic password")]
    assert repository.failures[0][2] is None
    assert b"unknown@example.invalid" not in repository.failures[0][0]
    assert b"192.0.2.10" not in repository.failures[0][1]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "account",
    [_account(active=False), _account(roles=("coach",))],
)
async def test_inactive_or_external_account_is_rejected_after_hash_check(
    account: LoginAccount,
) -> None:
    repository = FakeLoginRepository(account)
    verifier = FakePasswordVerifier(True)

    outcome = await _service(repository, verifier).authenticate(
        normalized_email="person@example.invalid",
        password="synthetic password",
        client_ip="192.0.2.10",
        now=NOW,
    )

    assert isinstance(outcome, LoginRejected)
    assert verifier.calls == [("synthetic-real-hash", "synthetic password")]
    assert repository.challenges == []


@pytest.mark.anyio
async def test_existing_rate_limit_avoids_account_and_password_work() -> None:
    repository = FakeLoginRepository(_account())
    repository.preexisting_block = NOW + timedelta(seconds=45)
    verifier = FakePasswordVerifier(True)

    outcome = await _service(repository, verifier).authenticate(
        normalized_email="person@example.invalid",
        password="synthetic password",
        client_ip="192.0.2.10",
        now=NOW,
    )

    assert isinstance(outcome, LoginRateLimited)
    assert outcome.retry_after_seconds == 45
    assert repository.lookups == []
    assert verifier.calls == []


@pytest.mark.anyio
async def test_failure_that_reaches_limit_returns_generic_rate_limit() -> None:
    repository = FakeLoginRepository(_account())
    repository.failure_block = NOW + timedelta(seconds=30)
    verifier = FakePasswordVerifier(False)

    outcome = await _service(repository, verifier).authenticate(
        normalized_email="person@example.invalid",
        password="wrong synthetic password",
        client_ip="192.0.2.10",
        now=NOW,
    )

    assert isinstance(outcome, LoginRateLimited)
    assert outcome.retry_after_seconds == 30
    assert repository.challenges == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("mfa_enrolled", "expected_state"),
    [(False, "mfa_enrollment_required"), (True, "mfa_required")],
)
async def test_valid_first_factor_creates_only_short_lived_challenge(
    mfa_enrolled: bool,
    expected_state: str,
) -> None:
    repository = FakeLoginRepository(_account(mfa_enrolled=mfa_enrolled))
    verifier = FakePasswordVerifier(True)

    outcome = await _service(repository, verifier).authenticate(
        normalized_email="person@example.invalid",
        password="synthetic password",
        client_ip="192.0.2.10",
        now=NOW,
    )

    assert isinstance(outcome, LoginAccepted)
    assert outcome.state == expected_state
    assert outcome.login_token
    assert outcome.csrf_token
    assert outcome.login_token not in repr(outcome)
    assert outcome.csrf_token not in repr(outcome)
    assert repository.failures == []
    assert len(repository.challenges) == 1
    challenge = repository.challenges[0]
    assert challenge["user_id"] == USER_ID
    assert challenge["state"] == expected_state
    assert challenge["expires_at"] == NOW + timedelta(minutes=5)
    assert outcome.login_token.encode("ascii") not in challenge["token_hash"]
    assert outcome.csrf_token.encode("ascii") not in challenge["csrf_token_hash"]
