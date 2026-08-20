from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.portal.companies import (
    CompanyAccessDeniedError,
    CompanyService,
    NewCompanyContact,
    PROVISIONAL_COMPANY_STATUS,
)

NOW = datetime(2026, 8, 20, 10, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000101")
COMPANY_ID = UUID("00000000-0000-4000-8000-000000000102")
CONTACT_ID = UUID("00000000-0000-4000-8000-000000000103")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def principal(*roles: str) -> SessionPrincipal:
    return SessionPrincipal(
        session_id=UUID("00000000-0000-4000-8000-000000000104"),
        user_id=USER_ID,
        display_name="Synthetic User",
        roles=roles,
        authenticated_at=NOW,
        idle_expires_at=NOW + timedelta(minutes=30),
        absolute_expires_at=NOW + timedelta(hours=8),
        csrf_token_hash=b"c" * 32,
    )


class FakeRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.result = None

    async def create_company(self, **values):
        self.calls.append(("create_company", values))
        return self.result

    async def list_companies(self, **values):
        self.calls.append(("list_companies", values))
        return self.result or ()

    async def get_company(self, company_id):
        self.calls.append(("get_company", {"company_id": company_id}))
        return self.result

    async def update_company(self, **values):
        self.calls.append(("update_company", values))
        return self.result

    async def add_contact(self, **values):
        self.calls.append(("add_contact", values))
        return self.result

    async def update_contact(self, **values):
        self.calls.append(("update_contact", values))
        return self.result


@pytest.mark.anyio
async def test_create_company_normalizes_pilot_fields_and_status() -> None:
    repository = FakeRepository()
    service = CompanyService(repository)

    await service.create_company(
        actor=principal("internal"),
        name="  Synthetic GmbH  ",
        industry="  Beratung ",
        internal_notes="  Nur synthetische Daten. ",
        initial_contact=NewCompanyContact(
            first_name="  Jan ",
            last_name=" Beispiel  ",
            email=" CONTACT@EXAMPLE.INVALID ",
            phone="  0931 0000 ",
            job_function="  Einkauf ",
        ),
        now=NOW,
    )

    _, values = repository.calls[0]
    assert values["name"] == "Synthetic GmbH"
    assert values["industry"] == "Beratung"
    assert values["status"] == PROVISIONAL_COMPANY_STATUS
    assert values["initial_contact"] == NewCompanyContact(
        first_name="Jan",
        last_name="Beispiel",
        email="contact@example.invalid",
        phone="0931 0000",
        job_function="Einkauf",
    )


@pytest.mark.anyio
async def test_company_service_denies_noninternal_roles_before_repository() -> None:
    repository = FakeRepository()
    service = CompanyService(repository)

    with pytest.raises(CompanyAccessDeniedError):
        await service.list_companies(actor=principal("coach"), query=None, limit=50)

    assert repository.calls == []


@pytest.mark.anyio
async def test_company_patch_allows_nullable_optional_fields_but_not_null_name() -> None:
    repository = FakeRepository()
    service = CompanyService(repository)

    await service.update_company(
        actor=principal("admin"),
        company_id=COMPANY_ID,
        changes={"industry": "", "internal_notes": None},
        now=NOW,
    )

    _, values = repository.calls[0]
    assert values["changes"] == {"industry": None, "internal_notes": None}
    with pytest.raises(ValueError, match="name"):
        await service.update_company(
            actor=principal("admin"),
            company_id=COMPANY_ID,
            changes={"name": None},
            now=NOW,
        )


@pytest.mark.anyio
async def test_contact_patch_normalizes_email_and_rejects_empty_change() -> None:
    repository = FakeRepository()
    service = CompanyService(repository)

    await service.update_contact(
        actor=principal("internal"),
        company_id=COMPANY_ID,
        contact_id=CONTACT_ID,
        changes={"email": " NEW@EXAMPLE.INVALID ", "phone": ""},
        now=NOW,
    )

    _, values = repository.calls[0]
    assert values["changes"] == {
        "email": "new@example.invalid",
        "phone": None,
    }
    with pytest.raises(ValueError, match="changes"):
        await service.update_contact(
            actor=principal("internal"),
            company_id=COMPANY_ID,
            contact_id=CONTACT_ID,
            changes={},
            now=NOW,
        )


@pytest.mark.anyio
async def test_company_list_is_bounded_and_query_is_normalized() -> None:
    repository = FakeRepository()
    service = CompanyService(repository)

    await service.list_companies(
        actor=principal("admin"),
        query="  Synthetic  ",
        limit=25,
    )

    assert repository.calls[0][1] == {"query": "Synthetic", "limit": 25}
    with pytest.raises(ValueError, match="limit"):
        await service.list_companies(
            actor=principal("admin"), query=None, limit=101
        )
