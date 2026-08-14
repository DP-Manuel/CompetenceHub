import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal, Protocol

from competence_hub_api.auth.login_repository import LoginAccount, LoginRepository
from competence_hub_api.security.tokens import issue_token, keyed_digest

INTERNAL_LOGIN_ROLES = frozenset({"admin", "internal"})
LOGIN_CHALLENGE_LIFETIME = timedelta(minutes=5)


class PasswordVerifier(Protocol):
    def verify(self, encoded_hash: str, password: str) -> bool: ...


@dataclass(frozen=True)
class LoginAccepted:
    state: Literal["mfa_required", "mfa_enrollment_required"]
    login_token: str = field(repr=False)
    csrf_token: str = field(repr=False)
    status: Literal["accepted"] = "accepted"

    def __post_init__(self) -> None:
        if self.state not in {"mfa_required", "mfa_enrollment_required"}:
            raise ValueError("invalid login state")
        if not self.login_token or not self.csrf_token:
            raise ValueError("login and CSRF tokens must not be empty")


@dataclass(frozen=True)
class LoginRejected:
    status: Literal["rejected"] = "rejected"


@dataclass(frozen=True)
class LoginRateLimited:
    retry_after_seconds: int
    status: Literal["rate_limited"] = "rate_limited"

    def __post_init__(self) -> None:
        if self.retry_after_seconds <= 0:
            raise ValueError("retry-after must be positive")


LoginOutcome = LoginAccepted | LoginRejected | LoginRateLimited


class LoginService:
    def __init__(
        self,
        repository: LoginRepository,
        password_verifier: PasswordVerifier,
        *,
        dummy_password_hash: str,
        rate_limit_hmac_key: bytes,
    ) -> None:
        if not dummy_password_hash:
            raise ValueError("dummy password hash must not be empty")
        if len(rate_limit_hmac_key) < 32:
            raise ValueError("rate-limit HMAC key must contain at least 256 bits")

        self._repository = repository
        self._password_verifier = password_verifier
        self._dummy_password_hash = dummy_password_hash
        self._rate_limit_hmac_key = rate_limit_hmac_key

    async def authenticate(
        self,
        *,
        normalized_email: str,
        password: str,
        client_ip: str,
        now: datetime,
    ) -> LoginOutcome:
        account_bucket_hash = keyed_digest(
            f"login:account:{normalized_email}",
            self._rate_limit_hmac_key,
        )
        ip_bucket_hash = keyed_digest(
            f"login:ip:{client_ip}",
            self._rate_limit_hmac_key,
        )

        blocked_until = await self._repository.find_login_rate_limit(
            account_bucket_hash,
            ip_bucket_hash,
            now=now,
        )
        if blocked_until is not None:
            return LoginRateLimited(_retry_after_seconds(blocked_until, now))

        account = await self._repository.find_login_account(normalized_email)
        password_hash = (
            account.password_hash
            if account is not None and account.password_hash
            else self._dummy_password_hash
        )
        password_matches = await asyncio.to_thread(
            self._password_verifier.verify,
            password_hash,
            password,
        )

        if not password_matches or not _eligible_for_internal_login(account):
            blocked_until = await self._repository.record_failed_login(
                account_bucket_hash,
                ip_bucket_hash,
                user_id=account.user_id if account is not None else None,
                now=now,
            )
            if blocked_until is not None:
                return LoginRateLimited(_retry_after_seconds(blocked_until, now))
            return LoginRejected()

        login_token = issue_token()
        csrf_token = issue_token()
        state: Literal["mfa_required", "mfa_enrollment_required"] = (
            "mfa_required" if account.mfa_enrolled else "mfa_enrollment_required"
        )
        await self._repository.create_login_challenge(
            user_id=account.user_id,
            token_hash=login_token.digest,
            csrf_token_hash=csrf_token.digest,
            state=state,
            account_bucket_hash=account_bucket_hash,
            now=now,
            expires_at=now + LOGIN_CHALLENGE_LIFETIME,
        )
        return LoginAccepted(
            state=state,
            login_token=login_token.plaintext,
            csrf_token=csrf_token.plaintext,
        )


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def _eligible_for_internal_login(account: LoginAccount | None) -> bool:
    return bool(
        account is not None
        and account.active
        and INTERNAL_LOGIN_ROLES.intersection(account.roles)
    )


def _retry_after_seconds(blocked_until: datetime, now: datetime) -> int:
    return max(1, int((blocked_until - now).total_seconds() + 0.999))
