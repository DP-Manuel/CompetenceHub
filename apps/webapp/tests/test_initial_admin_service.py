from datetime import UTC, datetime
from uuid import UUID

import pytest

from competence_hub_api.auth.account_administration import InitialAdminService

NOW = datetime(2026, 8, 14, 14, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000081")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakePasswordHasher:
    def __init__(self) -> None:
        self.passwords: list[str] = []

    def hash(self, password: str) -> str:
        self.passwords.append(password)
        return "synthetic-argon2id-hash"


class FakeInitialAdminRepository:
    def __init__(self) -> None:
        self.created: list[dict] = []

    async def create_initial_admin(self, **values):
        self.created.append(values)
        return USER_ID


@pytest.mark.anyio
async def test_initial_admin_normalizes_input_and_passes_only_hash_to_repository() -> None:
    repository = FakeInitialAdminRepository()
    hasher = FakePasswordHasher()
    service = InitialAdminService(repository, hasher)

    result = await service.create_initial_admin(
        email="  ADMIN@Example.Invalid ",
        display_name="  Synthetic Admin  ",
        password="synthetic secure passphrase",
        now=NOW,
    )

    assert result == USER_ID
    assert hasher.passwords == ["synthetic secure passphrase"]
    assert repository.created == [
        {
            "normalized_email": "admin@example.invalid",
            "display_name": "Synthetic Admin",
            "password_hash": "synthetic-argon2id-hash",
            "now": NOW,
        }
    ]
    assert "synthetic secure passphrase" not in repr(service)


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("email", "display_name", "now"),
    [
        ("invalid", "Synthetic Admin", NOW),
        ("admin@example.invalid", "   ", NOW),
        ("admin@example.invalid", "x" * 201, NOW),
        ("admin@example.invalid", "Synthetic Admin", datetime(2026, 8, 14)),
    ],
)
async def test_initial_admin_rejects_invalid_identity_before_hashing(
    email: str,
    display_name: str,
    now: datetime,
) -> None:
    repository = FakeInitialAdminRepository()
    hasher = FakePasswordHasher()

    with pytest.raises(ValueError):
        await InitialAdminService(repository, hasher).create_initial_admin(
            email=email,
            display_name=display_name,
            password="synthetic secure passphrase",
            now=now,
        )

    assert hasher.passwords == []
    assert repository.created == []
