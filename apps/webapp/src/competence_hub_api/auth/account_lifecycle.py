import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from typing import Literal, Protocol
from uuid import UUID, uuid4

from competence_hub_api.auth.login_service import normalize_email
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.security.email_addresses import is_single_email_address
from competence_hub_api.security.secret_encryption import SecretCipher
from competence_hub_api.security.tokens import digest_token, issue_token, keyed_digest

INVITATION_LIFETIME = timedelta(hours=24)
PASSWORD_RESET_LIFETIME = timedelta(minutes=30)
FRESH_ADMIN_AUTH_MAX_AGE = timedelta(minutes=15)
IDEMPOTENCY_LIFETIME = timedelta(hours=24)
INTERNAL_INVITATION_ROLES = frozenset({"internal"})


class InvitationConflictError(RuntimeError):
    pass


class IdempotencyConflictError(RuntimeError):
    pass


class AccountLifecycleConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class LifecycleQueued:
    recipient_user_id: UUID | None
    replayed: bool = False
    status: Literal["queued"] = "queued"


@dataclass(frozen=True)
class InvitationIssueResult:
    user_id: UUID
    replayed: bool


@dataclass(frozen=True)
class LifecycleAccepted:
    user_id: UUID
    login_token: str | None = field(default=None, repr=False)
    csrf_token: str | None = field(default=None, repr=False)
    status: Literal["accepted"] = "accepted"


@dataclass(frozen=True)
class LifecycleRejected:
    status: Literal["rejected"] = "rejected"


@dataclass(frozen=True)
class LifecycleRateLimited:
    retry_after_seconds: int
    status: Literal["rate_limited"] = "rate_limited"


LifecycleOutcome = LifecycleAccepted | LifecycleRejected | LifecycleRateLimited


class AccountLifecycleRepository(Protocol):
    async def find_invitation_idempotency(
        self,
        *,
        actor_user_id: UUID,
        idempotency_key_hash: bytes,
        request_fingerprint: bytes,
        now: datetime,
    ) -> InvitationIssueResult | None: ...

    async def find_rate_limit(
        self,
        action: str,
        bucket_hashes: tuple[bytes, ...],
        *,
        now: datetime,
    ) -> datetime | None: ...

    async def record_rate_limit_attempt(
        self,
        action: str,
        bucket_hashes: tuple[bytes, ...],
        *,
        now: datetime,
    ) -> datetime | None: ...

    async def issue_invitation(
        self,
        *,
        actor_user_id: UUID,
        normalized_email: str,
        display_name: str,
        role_codes: tuple[str, ...],
        token_hash: bytes,
        outbox_id: UUID,
        encrypted_payload: bytes,
        payload_key_version: str,
        idempotency_key_hash: bytes,
        request_fingerprint: bytes,
        now: datetime,
        expires_at: datetime,
        idempotency_expires_at: datetime,
    ) -> InvitationIssueResult: ...

    async def request_password_reset(
        self,
        *,
        normalized_email: str,
        token_hash: bytes,
        outbox_id: UUID,
        encrypted_payload: bytes,
        payload_key_version: str,
        now: datetime,
        expires_at: datetime,
    ) -> UUID | None: ...

    async def accept_invitation(
        self,
        *,
        token_hash: bytes,
        password_hash: str,
        login_token_hash: bytes,
        csrf_token_hash: bytes,
        now: datetime,
        challenge_expires_at: datetime,
    ) -> UUID | None: ...

    async def confirm_password_reset(
        self,
        *,
        token_hash: bytes,
        password_hash: str,
        now: datetime,
    ) -> UUID | None: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...


class AccountLifecycleService:
    def __init__(
        self,
        repository: AccountLifecycleRepository,
        password_hasher: PasswordHasher,
        *,
        rate_limit_hmac_key: bytes,
        idempotency_hmac_key: bytes,
        outbox_cipher: SecretCipher,
    ) -> None:
        if len(rate_limit_hmac_key) < 32:
            raise ValueError("rate-limit HMAC key must contain at least 256 bits")
        if len(idempotency_hmac_key) < 32:
            raise ValueError("idempotency HMAC key must contain at least 256 bits")
        if outbox_cipher.context != "auth-token-outbox":
            raise ValueError("outbox cipher must use the auth-token-outbox context")
        self._repository = repository
        self._password_hasher = password_hasher
        self._rate_limit_hmac_key = rate_limit_hmac_key
        self._idempotency_hmac_key = idempotency_hmac_key
        self._outbox_cipher = outbox_cipher

    async def issue_invitation(
        self,
        *,
        actor: SessionPrincipal,
        email: str,
        display_name: str,
        role_codes: tuple[str, ...],
        idempotency_key: str,
        client_ip: str,
        now: datetime,
    ) -> LifecycleQueued | LifecycleRejected | LifecycleRateLimited:
        normalized_email = normalize_email(email)
        _validate_email(normalized_email)
        normalized_display_name = _normalize_display_name(display_name)
        normalized_roles = tuple(sorted(set(role_codes)))
        if not normalized_roles or not set(normalized_roles).issubset(
            INTERNAL_INVITATION_ROLES
        ):
            return LifecycleRejected()
        if (
            "admin" not in actor.roles
            or now - actor.authenticated_at > FRESH_ADMIN_AUTH_MAX_AGE
            or actor.authenticated_at > now
        ):
            return LifecycleRejected()
        normalized_idempotency_key = _validate_idempotency_key(idempotency_key)
        idempotency_key_hash = keyed_digest(
            f"auth.invitation.issue:key:{normalized_idempotency_key}",
            self._idempotency_hmac_key,
        )
        request_fingerprint = _invitation_request_fingerprint(
            normalized_email,
            normalized_display_name,
            normalized_roles,
            self._idempotency_hmac_key,
        )
        existing_result = await self._repository.find_invitation_idempotency(
            actor_user_id=actor.user_id,
            idempotency_key_hash=idempotency_key_hash,
            request_fingerprint=request_fingerprint,
            now=now,
        )
        if existing_result is not None:
            return LifecycleQueued(
                recipient_user_id=existing_result.user_id,
                replayed=True,
            )

        buckets = self._rate_limit_buckets(
            "invitation_issue",
            normalized_email,
            client_ip,
        )
        rate_limit = await self._check_and_record_rate_limit(
            "invitation", buckets, now=now
        )
        if rate_limit is not None:
            return rate_limit

        token = issue_token()
        expires_at = now + INVITATION_LIFETIME
        outbox_id = uuid4()
        encrypted_payload = self._outbox_cipher.encrypt(
            token.plaintext,
            subject_id=_outbox_subject("invitation", outbox_id),
        )
        result = await self._repository.issue_invitation(
            actor_user_id=actor.user_id,
            normalized_email=normalized_email,
            display_name=normalized_display_name,
            role_codes=normalized_roles,
            token_hash=token.digest,
            outbox_id=outbox_id,
            encrypted_payload=encrypted_payload.envelope,
            payload_key_version=encrypted_payload.key_version,
            idempotency_key_hash=idempotency_key_hash,
            request_fingerprint=request_fingerprint,
            now=now,
            expires_at=expires_at,
            idempotency_expires_at=now + IDEMPOTENCY_LIFETIME,
        )
        return LifecycleQueued(
            recipient_user_id=result.user_id,
            replayed=result.replayed,
        )

    async def request_password_reset(
        self,
        *,
        email: str,
        client_ip: str,
        now: datetime,
    ) -> LifecycleQueued | LifecycleRateLimited:
        normalized_email = normalize_email(email)
        _validate_email(normalized_email)
        buckets = self._rate_limit_buckets(
            "password_reset_request",
            normalized_email,
            client_ip,
        )
        rate_limit = await self._check_and_record_rate_limit(
            "password_reset", buckets, now=now
        )
        if rate_limit is not None:
            return rate_limit

        token = issue_token()
        expires_at = now + PASSWORD_RESET_LIFETIME
        outbox_id = uuid4()
        encrypted_payload = self._outbox_cipher.encrypt(
            token.plaintext,
            subject_id=_outbox_subject("password_reset", outbox_id),
        )
        user_id = await self._repository.request_password_reset(
            normalized_email=normalized_email,
            token_hash=token.digest,
            outbox_id=outbox_id,
            encrypted_payload=encrypted_payload.envelope,
            payload_key_version=encrypted_payload.key_version,
            now=now,
            expires_at=expires_at,
        )
        return LifecycleQueued(
            recipient_user_id=user_id,
        )

    async def accept_invitation(
        self,
        *,
        token: str,
        password: str,
        client_ip: str,
        now: datetime,
    ) -> LifecycleOutcome:
        return await self._consume_token(
            purpose="invitation",
            token=token,
            password=password,
            client_ip=client_ip,
            now=now,
        )

    async def confirm_password_reset(
        self,
        *,
        token: str,
        password: str,
        client_ip: str,
        now: datetime,
    ) -> LifecycleOutcome:
        return await self._consume_token(
            purpose="password_reset",
            token=token,
            password=password,
            client_ip=client_ip,
            now=now,
        )

    async def _consume_token(
        self,
        *,
        purpose: Literal["invitation", "password_reset"],
        token: str,
        password: str,
        client_ip: str,
        now: datetime,
    ) -> LifecycleOutcome:
        try:
            token_hash = digest_token(token)
        except ValueError:
            return LifecycleRejected()
        token_bucket = keyed_digest(
            f"{purpose}_confirm:token:{token_hash.hex()}",
            self._rate_limit_hmac_key,
        )
        ip_bucket = keyed_digest(
            f"{purpose}_confirm:ip:{client_ip}",
            self._rate_limit_hmac_key,
        )
        rate_limit = await self._check_and_record_rate_limit(
            purpose,
            tuple(sorted({token_bucket, ip_bucket})),
            now=now,
        )
        if rate_limit is not None:
            return rate_limit

        password_hash = await asyncio.to_thread(self._password_hasher.hash, password)
        if purpose == "password_reset":
            user_id = await self._repository.confirm_password_reset(
                token_hash=token_hash,
                password_hash=password_hash,
                now=now,
            )
            if user_id is None:
                return LifecycleRejected()
            return LifecycleAccepted(user_id=user_id)

        login_token = issue_token()
        csrf_token = issue_token()
        user_id = await self._repository.accept_invitation(
            token_hash=token_hash,
            password_hash=password_hash,
            login_token_hash=login_token.digest,
            csrf_token_hash=csrf_token.digest,
            now=now,
            challenge_expires_at=now + timedelta(minutes=5),
        )
        if user_id is None:
            return LifecycleRejected()
        return LifecycleAccepted(
            user_id=user_id,
            login_token=login_token.plaintext,
            csrf_token=csrf_token.plaintext,
        )

    def _rate_limit_buckets(
        self,
        action: str,
        normalized_email: str,
        client_ip: str,
    ) -> tuple[bytes, ...]:
        return tuple(
            sorted(
                {
                    keyed_digest(
                        f"{action}:account:{normalized_email}",
                        self._rate_limit_hmac_key,
                    ),
                    keyed_digest(
                        f"{action}:ip:{client_ip}",
                        self._rate_limit_hmac_key,
                    ),
                }
            )
        )

    async def _check_and_record_rate_limit(
        self,
        action: str,
        bucket_hashes: tuple[bytes, ...],
        *,
        now: datetime,
    ) -> LifecycleRateLimited | None:
        blocked_until = await self._repository.find_rate_limit(
            action,
            bucket_hashes,
            now=now,
        )
        if blocked_until is None:
            blocked_until = await self._repository.record_rate_limit_attempt(
                action,
                bucket_hashes,
                now=now,
            )
        if blocked_until is None:
            return None
        retry_after = max(1, int((blocked_until - now).total_seconds() + 0.999))
        return LifecycleRateLimited(retry_after)


def _validate_email(value: str) -> None:
    if not is_single_email_address(value):
        raise ValueError("invalid email")


def _normalize_display_name(value: str) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > 200:
        raise ValueError("invalid display name")
    return normalized


def _validate_idempotency_key(value: str) -> str:
    normalized = value.strip()
    if len(normalized) < 16 or len(normalized) > 128:
        raise ValueError("invalid idempotency key")
    try:
        normalized.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError("invalid idempotency key") from error
    return normalized


def _invitation_request_fingerprint(
    normalized_email: str,
    display_name: str,
    role_codes: tuple[str, ...],
    key: bytes,
) -> bytes:
    canonical_request = json.dumps(
        {
            "display_name": display_name,
            "email": normalized_email,
            "role_codes": list(role_codes),
        },
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return keyed_digest(
        f"auth.invitation.issue:request:{canonical_request}",
        key,
    )


def _outbox_subject(
    purpose: Literal["invitation", "password_reset"],
    outbox_id: UUID,
) -> str:
    return f"{purpose}:{outbox_id}"
