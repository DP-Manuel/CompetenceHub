from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID


@dataclass(frozen=True)
class MfaChallenge:
    challenge_id: UUID
    user_id: UUID
    email: str
    state: Literal["mfa_required", "mfa_enrollment_required"]
    csrf_token_hash: bytes = field(repr=False)
    encrypted_totp_secret: bytes | None = field(default=None, repr=False)
    totp_key_version: str | None = None
    totp_enabled_at: datetime | None = None
    last_accepted_time_step: int | None = None


@dataclass(frozen=True)
class RecoveryCodeRecord:
    digest: bytes = field(repr=False)
    key_version: str


@dataclass(frozen=True)
class SessionRecord:
    token_hash: bytes = field(repr=False)
    csrf_token_hash: bytes = field(repr=False)
    idle_expires_at: datetime
    absolute_expires_at: datetime


class MfaRepository(Protocol):
    async def find_active_challenge(
        self,
        token_hash: bytes,
        *,
        now: datetime,
    ) -> MfaChallenge | None: ...

    async def save_pending_totp(
        self,
        *,
        challenge_id: UUID,
        user_id: UUID,
        encrypted_secret: bytes,
        key_version: str,
        now: datetime,
    ) -> bool: ...

    async def find_mfa_rate_limit(
        self,
        user_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        *,
        now: datetime,
    ) -> datetime | None: ...

    async def record_failed_mfa(
        self,
        *,
        challenge_id: UUID,
        user_id: UUID,
        user_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        now: datetime,
    ) -> datetime | None: ...

    async def complete_totp(
        self,
        *,
        challenge_id: UUID,
        user_id: UUID,
        accepted_time_step: int,
        enrollment: bool,
        recovery_codes: tuple[RecoveryCodeRecord, ...],
        session: SessionRecord,
        user_bucket_hash: bytes,
        now: datetime,
    ) -> bool: ...

    async def complete_recovery(
        self,
        *,
        challenge_id: UUID,
        user_id: UUID,
        candidate_digests: tuple[RecoveryCodeRecord, ...],
        session: SessionRecord,
        user_bucket_hash: bytes,
        now: datetime,
    ) -> bool: ...
