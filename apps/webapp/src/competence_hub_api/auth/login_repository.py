from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class LoginAccount:
    user_id: UUID
    password_hash: str | None = field(repr=False)
    active: bool
    roles: tuple[str, ...]
    mfa_enrolled: bool


class LoginRepository(Protocol):
    async def find_login_account(self, normalized_email: str) -> LoginAccount | None: ...

    async def find_login_rate_limit(
        self,
        account_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        *,
        now: datetime,
    ) -> datetime | None: ...

    async def record_failed_login(
        self,
        account_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        *,
        user_id: UUID | None,
        now: datetime,
    ) -> datetime | None: ...

    async def create_login_challenge(
        self,
        *,
        user_id: UUID,
        token_hash: bytes,
        csrf_token_hash: bytes,
        state: str,
        account_bucket_hash: bytes,
        now: datetime,
        expires_at: datetime,
    ) -> None: ...
