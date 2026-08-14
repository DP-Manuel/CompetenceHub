from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pyotp
import pytest

from competence_hub_api.auth.mfa_repository import (
    MfaChallenge,
    RecoveryCodeRecord,
    SessionRecord,
)
from competence_hub_api.auth.mfa_service import MfaService
from competence_hub_api.security.recovery_codes import recovery_code_matches
from competence_hub_api.security.secret_encryption import SecretCipher
from competence_hub_api.security.tokens import digest_token

NOW = datetime(2026, 8, 14, 12, 0, tzinfo=UTC)
USER_ID = uuid4()
CHALLENGE_ID = uuid4()
LOGIN_TOKEN = "synthetic-login-token"
CSRF_TOKEN = "synthetic-csrf-token"
TOTP_KEY = b"t" * 32
RECOVERY_KEY = b"r" * 32
RATE_KEY = b"l" * 32
TOTP_SECRET = "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"


class FakeMfaRepository:
    def __init__(self, challenge: MfaChallenge | None) -> None:
        self.challenge = challenge
        self.pending_saved = False
        self.failed_attempts = 0
        self.blocked_until = None
        self.complete_totp_result = True
        self.complete_recovery_result = True
        self.last_recovery_codes: tuple[RecoveryCodeRecord, ...] = ()
        self.last_session: SessionRecord | None = None

    async def find_active_challenge(self, token_hash, *, now):
        if token_hash != digest_token(LOGIN_TOKEN):
            return None
        return self.challenge

    async def save_pending_totp(self, **kwargs):
        self.pending_saved = True
        self.pending_kwargs = kwargs
        return True

    async def find_mfa_rate_limit(self, user_bucket_hash, ip_bucket_hash, *, now):
        return self.blocked_until

    async def record_failed_mfa(self, **kwargs):
        self.failed_attempts += 1
        return self.blocked_until

    async def complete_totp(self, **kwargs):
        self.last_recovery_codes = kwargs["recovery_codes"]
        self.last_session = kwargs["session"]
        self.complete_totp_kwargs = kwargs
        return self.complete_totp_result

    async def complete_recovery(self, **kwargs):
        self.last_session = kwargs["session"]
        self.complete_recovery_kwargs = kwargs
        return self.complete_recovery_result


def challenge(*, enrollment: bool, enabled: bool) -> MfaChallenge:
    cipher = SecretCipher({"totp-v1": TOTP_KEY}, "totp-v1")
    encrypted = cipher.encrypt(TOTP_SECRET, subject_id=str(USER_ID))
    return MfaChallenge(
        challenge_id=CHALLENGE_ID,
        user_id=USER_ID,
        email="synthetic@example.invalid",
        state="mfa_enrollment_required" if enrollment else "mfa_required",
        csrf_token_hash=digest_token(CSRF_TOKEN),
        encrypted_totp_secret=encrypted.envelope,
        totp_key_version=encrypted.key_version,
        totp_enabled_at=NOW - timedelta(days=1) if enabled else None,
    )


def service(repository: FakeMfaRepository) -> MfaService:
    return MfaService(
        repository,
        SecretCipher({"totp-v1": TOTP_KEY}, "totp-v1"),
        recovery_hmac_keys={"recovery-v1": RECOVERY_KEY},
        recovery_active_key_version="recovery-v1",
        rate_limit_hmac_key=RATE_KEY,
        session_idle_timeout=timedelta(minutes=30),
    )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_start_enrollment_returns_uri_and_persists_only_encrypted_secret() -> None:
    repository = FakeMfaRepository(challenge(enrollment=True, enabled=False))

    outcome = await service(repository).start_totp_enrollment(
        login_token=LOGIN_TOKEN,
        csrf_token=CSRF_TOKEN,
        now=NOW,
    )

    assert outcome.status == "enrollment_created"
    assert outcome.provisioning_uri.startswith("otpauth://totp/")
    assert repository.pending_saved is True
    assert b"otpauth" not in repository.pending_kwargs["encrypted_secret"]
    assert TOTP_SECRET.encode("ascii") not in repository.pending_kwargs["encrypted_secret"]
    assert outcome.provisioning_uri not in repr(outcome)


@pytest.mark.anyio
async def test_enrollment_confirmation_rotates_session_and_returns_recovery_once() -> None:
    repository = FakeMfaRepository(challenge(enrollment=True, enabled=False))
    code = pyotp.TOTP(TOTP_SECRET).at(NOW.timestamp())

    outcome = await service(repository).confirm_totp_enrollment(
        login_token=LOGIN_TOKEN,
        csrf_token=CSRF_TOKEN,
        code=code,
        client_ip="192.0.2.10",
        now=NOW,
    )

    assert outcome.status == "session_created"
    assert len(outcome.recovery_codes) == 10
    assert len(repository.last_recovery_codes) == 10
    assert repository.last_session is not None
    assert repository.complete_totp_kwargs["enrollment"] is True
    assert all(code not in repr(outcome) for code in outcome.recovery_codes)
    assert recovery_code_matches(
        outcome.recovery_codes[0],
        repository.last_recovery_codes[0].digest,
        RECOVERY_KEY,
        key_version="recovery-v1",
    )


@pytest.mark.anyio
async def test_enabled_totp_verification_creates_session_without_new_recovery_codes() -> None:
    repository = FakeMfaRepository(challenge(enrollment=False, enabled=True))

    outcome = await service(repository).verify_totp(
        login_token=LOGIN_TOKEN,
        csrf_token=CSRF_TOKEN,
        code=pyotp.TOTP(TOTP_SECRET).at(NOW.timestamp()),
        client_ip="192.0.2.11",
        now=NOW,
    )

    assert outcome.status == "session_created"
    assert outcome.recovery_codes == ()
    assert repository.complete_totp_kwargs["enrollment"] is False
    assert repository.last_session is not None


@pytest.mark.anyio
async def test_wrong_totp_records_failure_and_never_creates_session() -> None:
    repository = FakeMfaRepository(challenge(enrollment=False, enabled=True))

    outcome = await service(repository).verify_totp(
        login_token=LOGIN_TOKEN,
        csrf_token=CSRF_TOKEN,
        code="000000",
        client_ip="192.0.2.12",
        now=NOW,
    )

    assert outcome.status == "rejected"
    assert repository.failed_attempts == 1
    assert repository.last_session is None


@pytest.mark.anyio
async def test_wrong_csrf_or_challenge_state_fails_without_sensitive_work() -> None:
    repository = FakeMfaRepository(challenge(enrollment=False, enabled=True))

    outcome = await service(repository).start_totp_enrollment(
        login_token=LOGIN_TOKEN,
        csrf_token="wrong-csrf",
        now=NOW,
    )

    assert outcome.status == "rejected"
    assert repository.pending_saved is False
    assert repository.failed_attempts == 0


@pytest.mark.anyio
async def test_rate_limit_prevents_totp_verification() -> None:
    repository = FakeMfaRepository(challenge(enrollment=False, enabled=True))
    repository.blocked_until = NOW + timedelta(seconds=45)

    outcome = await service(repository).verify_totp(
        login_token=LOGIN_TOKEN,
        csrf_token=CSRF_TOKEN,
        code=pyotp.TOTP(TOTP_SECRET).at(NOW.timestamp()),
        client_ip="192.0.2.13",
        now=NOW,
    )

    assert outcome.status == "rate_limited"
    assert outcome.retry_after_seconds == 45
    assert repository.last_session is None


@pytest.mark.anyio
async def test_recovery_verification_passes_all_key_versions_to_atomic_repository() -> None:
    repository = FakeMfaRepository(challenge(enrollment=False, enabled=True))
    mfa_service = MfaService(
        repository,
        SecretCipher({"totp-v1": TOTP_KEY}, "totp-v1"),
        recovery_hmac_keys={
            "recovery-v1": RECOVERY_KEY,
            "recovery-v2": b"s" * 32,
        },
        recovery_active_key_version="recovery-v2",
        rate_limit_hmac_key=RATE_KEY,
        session_idle_timeout=timedelta(minutes=30),
    )

    outcome = await mfa_service.verify_recovery_code(
        login_token=LOGIN_TOKEN,
        csrf_token=CSRF_TOKEN,
        code="ABCD-EFGH-JKLM-NPQR",
        client_ip="192.0.2.14",
        now=NOW,
    )

    assert outcome.status == "session_created"
    candidates = repository.complete_recovery_kwargs["candidate_digests"]
    assert {candidate.key_version for candidate in candidates} == {
        "recovery-v1",
        "recovery-v2",
    }
    assert repository.last_session is not None


@pytest.mark.anyio
async def test_malformed_recovery_code_records_failure_without_repository_match() -> None:
    repository = FakeMfaRepository(challenge(enrollment=False, enabled=True))

    outcome = await service(repository).verify_recovery_code(
        login_token=LOGIN_TOKEN,
        csrf_token=CSRF_TOKEN,
        code="invalid-1",
        client_ip="192.0.2.16",
        now=NOW,
    )

    assert outcome.status == "rejected"
    assert repository.failed_attempts == 1
    assert not hasattr(repository, "complete_recovery_kwargs")


@pytest.mark.anyio
async def test_atomic_repository_rejection_is_treated_as_failed_mfa() -> None:
    repository = FakeMfaRepository(challenge(enrollment=False, enabled=True))
    repository.complete_totp_result = False

    outcome = await service(repository).verify_totp(
        login_token=LOGIN_TOKEN,
        csrf_token=CSRF_TOKEN,
        code=pyotp.TOTP(TOTP_SECRET).at(NOW.timestamp()),
        client_ip="192.0.2.15",
        now=NOW,
    )

    assert outcome.status == "rejected"
    assert repository.failed_attempts == 1
