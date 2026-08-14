from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class SessionPrincipal:
    session_id: UUID
    user_id: UUID
    display_name: str
    roles: tuple[str, ...]
    authenticated_at: datetime
    idle_expires_at: datetime
    absolute_expires_at: datetime
    csrf_token_hash: bytes = field(repr=False)


class SessionRepository(Protocol):
    async def refresh_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        idle_timeout: timedelta,
    ) -> SessionPrincipal | None: ...

    async def find_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
    ) -> SessionPrincipal | None: ...

    async def revoke_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        reason: str,
    ) -> None: ...
