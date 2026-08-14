from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hmac
from typing import Literal

from competence_hub_api.auth.mfa_repository import (
    MfaChallenge,
    MfaRepository,
    RecoveryCodeRecord,
    SessionRecord,
)
from competence_hub_api.security.recovery_codes import (
    issue_recovery_codes,
    recovery_code_digest,
)
from competence_hub_api.security.secret_encryption import (
    SecretCipher,
    SecretEncryptionError,
)
from competence_hub_api.security.tokens import digest_token, issue_token, keyed_digest
from competence_hub_api.security.totp import (
    generate_totp_secret,
    provisioning_uri,
    verify_totp,
)

SESSION_ABSOLUTE_LIFETIME = timedelta(hours=8)


@dataclass(frozen=True)
class TotpEnrollmentCreated:
    provisioning_uri: str = field(repr=False)
    status: Literal["enrollment_created"] = "enrollment_created"


@dataclass(frozen=True)
class MfaSessionCreated:
    session_token: str = field(repr=False)
    csrf_token: str = field(repr=False)
    recovery_codes: tuple[str, ...] = field(default=(), repr=False)
    status: Literal["session_created"] = "session_created"


@dataclass(frozen=True)
class MfaRejected:
    status: Literal["rejected"] = "rejected"


@dataclass(frozen=True)
class MfaRateLimited:
    retry_after_seconds: int
    status: Literal["rate_limited"] = "rate_limited"

    def __post_init__(self) -> None:
        if self.retry_after_seconds <= 0:
            raise ValueError("retry-after must be positive")


MfaOutcome = (
    TotpEnrollmentCreated | MfaSessionCreated | MfaRejected | MfaRateLimited
)


class MfaService:
    def __init__(
        self,
        repository: MfaRepository,
        secret_cipher: SecretCipher,
        *,
        recovery_hmac_keys: Mapping[str, bytes],
        recovery_active_key_version: str,
        rate_limit_hmac_key: bytes,
        session_idle_timeout: timedelta,
    ) -> None:
        normalized_recovery_keys = dict(recovery_hmac_keys)
        if recovery_active_key_version not in normalized_recovery_keys:
            raise ValueError("active recovery key version is unavailable")
        if any(len(key) < 32 for key in normalized_recovery_keys.values()):
            raise ValueError("recovery HMAC keys must contain at least 256 bits")
        if len(rate_limit_hmac_key) < 32:
            raise ValueError("rate-limit HMAC key must contain at least 256 bits")
        if not timedelta(minutes=1) <= session_idle_timeout <= timedelta(hours=1):
            raise ValueError("session idle timeout must be between 1 and 60 minutes")

        self._repository = repository
        self._secret_cipher = secret_cipher
        self._recovery_hmac_keys = normalized_recovery_keys
        self._recovery_active_key_version = recovery_active_key_version
        self._rate_limit_hmac_key = rate_limit_hmac_key
        self._session_idle_timeout = session_idle_timeout

    async def start_totp_enrollment(
        self,
        *,
        login_token: str,
        csrf_token: str,
        now: datetime,
    ) -> MfaOutcome:
        challenge = await self._challenge(login_token, now)
        if (
            challenge is None
            or challenge.state != "mfa_enrollment_required"
            or not _csrf_matches(challenge, csrf_token)
        ):
            return MfaRejected()

        secret = generate_totp_secret()
        encrypted = self._secret_cipher.encrypt(
            secret,
            subject_id=str(challenge.user_id),
        )
        saved = await self._repository.save_pending_totp(
            challenge_id=challenge.challenge_id,
            user_id=challenge.user_id,
            encrypted_secret=encrypted.envelope,
            key_version=encrypted.key_version,
            now=now,
        )
        if not saved:
            return MfaRejected()
        return TotpEnrollmentCreated(
            provisioning_uri=provisioning_uri(
                secret,
                account_name=challenge.email,
            )
        )

    async def confirm_totp_enrollment(
        self,
        *,
        login_token: str,
        csrf_token: str,
        code: str,
        client_ip: str,
        now: datetime,
    ) -> MfaOutcome:
        return await self._verify_totp(
            login_token=login_token,
            csrf_token=csrf_token,
            code=code,
            client_ip=client_ip,
            now=now,
            enrollment=True,
        )

    async def verify_totp(
        self,
        *,
        login_token: str,
        csrf_token: str,
        code: str,
        client_ip: str,
        now: datetime,
    ) -> MfaOutcome:
        return await self._verify_totp(
            login_token=login_token,
            csrf_token=csrf_token,
            code=code,
            client_ip=client_ip,
            now=now,
            enrollment=False,
        )

    async def verify_recovery_code(
        self,
        *,
        login_token: str,
        csrf_token: str,
        code: str,
        client_ip: str,
        now: datetime,
    ) -> MfaOutcome:
        challenge = await self._challenge(login_token, now)
        if (
            challenge is None
            or challenge.state != "mfa_required"
            or not _csrf_matches(challenge, csrf_token)
        ):
            return MfaRejected()

        buckets = self._rate_buckets(challenge, client_ip)
        limited = await self._limited_outcome(buckets, now)
        if limited is not None:
            return limited

        candidates: list[RecoveryCodeRecord] = []
        invalid_code = False
        for key_version, key in self._recovery_hmac_keys.items():
            try:
                digest = recovery_code_digest(
                    code,
                    key,
                    key_version=key_version,
                )
            except ValueError:
                invalid_code = True
                digest = recovery_code_digest(
                    "AAAA-AAAA-AAAA-AAAA",
                    key,
                    key_version=key_version,
                )
            candidates.append(RecoveryCodeRecord(digest, key_version))

        if invalid_code:
            return await self._failed(challenge, buckets, now)

        session_outcome, session_record = self._new_session(now)
        completed = await self._repository.complete_recovery(
            challenge_id=challenge.challenge_id,
            user_id=challenge.user_id,
            candidate_digests=tuple(candidates),
            session=session_record,
            user_bucket_hash=buckets[0],
            now=now,
        )
        if not completed:
            return await self._failed(challenge, buckets, now)
        return session_outcome

    async def _verify_totp(
        self,
        *,
        login_token: str,
        csrf_token: str,
        code: str,
        client_ip: str,
        now: datetime,
        enrollment: bool,
    ) -> MfaOutcome:
        challenge = await self._challenge(login_token, now)
        expected_state = "mfa_enrollment_required" if enrollment else "mfa_required"
        if (
            challenge is None
            or challenge.state != expected_state
            or not _csrf_matches(challenge, csrf_token)
            or challenge.encrypted_totp_secret is None
            or challenge.totp_key_version is None
            or (enrollment and challenge.totp_enabled_at is not None)
            or (not enrollment and challenge.totp_enabled_at is None)
        ):
            return MfaRejected()

        buckets = self._rate_buckets(challenge, client_ip)
        limited = await self._limited_outcome(buckets, now)
        if limited is not None:
            return limited

        try:
            secret = self._secret_cipher.decrypt(
                challenge.encrypted_totp_secret,
                key_version=challenge.totp_key_version,
                subject_id=str(challenge.user_id),
            )
            match = verify_totp(
                secret,
                code,
                at=now,
                last_accepted_time_step=challenge.last_accepted_time_step,
            )
        except (SecretEncryptionError, ValueError):
            match = None
        if match is None:
            return await self._failed(challenge, buckets, now)

        issued_recovery = ()
        recovery_records: tuple[RecoveryCodeRecord, ...] = ()
        if enrollment:
            issued_recovery = issue_recovery_codes(
                self._recovery_hmac_keys[self._recovery_active_key_version],
                key_version=self._recovery_active_key_version,
            )
            recovery_records = tuple(
                RecoveryCodeRecord(item.digest, item.key_version)
                for item in issued_recovery
            )

        session_outcome, session_record = self._new_session(now)
        completed = await self._repository.complete_totp(
            challenge_id=challenge.challenge_id,
            user_id=challenge.user_id,
            accepted_time_step=match.time_step,
            enrollment=enrollment,
            recovery_codes=recovery_records,
            session=session_record,
            user_bucket_hash=buckets[0],
            now=now,
        )
        if not completed:
            return await self._failed(challenge, buckets, now)
        return MfaSessionCreated(
            session_token=session_outcome.session_token,
            csrf_token=session_outcome.csrf_token,
            recovery_codes=tuple(item.plaintext for item in issued_recovery),
        )

    async def _challenge(
        self,
        login_token: str,
        now: datetime,
    ) -> MfaChallenge | None:
        try:
            token_hash = digest_token(login_token)
        except ValueError:
            return None
        return await self._repository.find_active_challenge(token_hash, now=now)

    def _rate_buckets(
        self,
        challenge: MfaChallenge,
        client_ip: str,
    ) -> tuple[bytes, bytes]:
        return (
            keyed_digest(
                f"mfa:user:{challenge.user_id}",
                self._rate_limit_hmac_key,
            ),
            keyed_digest(f"mfa:ip:{client_ip}", self._rate_limit_hmac_key),
        )

    async def _limited_outcome(
        self,
        buckets: tuple[bytes, bytes],
        now: datetime,
    ) -> MfaRateLimited | None:
        blocked_until = await self._repository.find_mfa_rate_limit(
            *buckets,
            now=now,
        )
        if blocked_until is None:
            return None
        return MfaRateLimited(_retry_after_seconds(blocked_until, now))

    async def _failed(
        self,
        challenge: MfaChallenge,
        buckets: tuple[bytes, bytes],
        now: datetime,
    ) -> MfaOutcome:
        blocked_until = await self._repository.record_failed_mfa(
            challenge_id=challenge.challenge_id,
            user_id=challenge.user_id,
            user_bucket_hash=buckets[0],
            ip_bucket_hash=buckets[1],
            now=now,
        )
        if blocked_until is not None:
            return MfaRateLimited(_retry_after_seconds(blocked_until, now))
        return MfaRejected()

    def _new_session(self, now: datetime) -> tuple[MfaSessionCreated, SessionRecord]:
        session_token = issue_token()
        csrf_token = issue_token()
        absolute_expires_at = now + SESSION_ABSOLUTE_LIFETIME
        return (
            MfaSessionCreated(
                session_token=session_token.plaintext,
                csrf_token=csrf_token.plaintext,
            ),
            SessionRecord(
                token_hash=session_token.digest,
                csrf_token_hash=csrf_token.digest,
                idle_expires_at=min(
                    now + self._session_idle_timeout,
                    absolute_expires_at,
                ),
                absolute_expires_at=absolute_expires_at,
            ),
        )


def _csrf_matches(challenge: MfaChallenge, csrf_token: str) -> bool:
    try:
        candidate = digest_token(csrf_token)
    except ValueError:
        candidate = b"\x00" * 32
    return hmac.compare_digest(candidate, challenge.csrf_token_hash)


def _retry_after_seconds(blocked_until: datetime, now: datetime) -> int:
    return max(1, int((blocked_until - now).total_seconds() + 0.999))
