import asyncio
from datetime import datetime
from typing import Protocol
from uuid import UUID

from competence_hub_api.auth.login_service import normalize_email


class InitialAdminAlreadyExistsError(RuntimeError):
    pass


class InitialAdminConfigurationError(RuntimeError):
    pass


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...


class InitialAdminRepository(Protocol):
    async def create_initial_admin(
        self,
        *,
        normalized_email: str,
        display_name: str,
        password_hash: str,
        now: datetime,
    ) -> UUID: ...


class InitialAdminService:
    def __init__(
        self,
        repository: InitialAdminRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher

    async def create_initial_admin(
        self,
        *,
        email: str,
        display_name: str,
        password: str,
        now: datetime,
    ) -> UUID:
        normalized_email = normalize_email(email)
        _validate_email(normalized_email)
        normalized_display_name = display_name.strip()
        if not normalized_display_name or len(normalized_display_name) > 200:
            raise ValueError("invalid display name")
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")

        password_hash = await asyncio.to_thread(self._password_hasher.hash, password)
        return await self._repository.create_initial_admin(
            normalized_email=normalized_email,
            display_name=normalized_display_name,
            password_hash=password_hash,
            now=now,
        )


def _validate_email(value: str) -> None:
    if (
        len(value) < 3
        or len(value) > 254
        or "@" not in value
        or value.startswith("@")
        or value.endswith("@")
        or any(character.isspace() for character in value)
    ):
        raise ValueError("invalid email")
