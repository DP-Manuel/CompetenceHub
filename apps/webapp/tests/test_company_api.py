from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.portal.companies import (
    CompanyContactRecord,
    CompanyDetail,
    CompanyRecord,
    CompanySummary,
)
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token

NOW = datetime(2026, 8, 20, 11, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000111")
COMPANY_ID = UUID("00000000-0000-4000-8000-000000000112")
CONTACT_ID = UUID("00000000-0000-4000-8000-000000000113")
SESSION_TOKEN = "synthetic-company-session-token"
CSRF_TOKEN = "synthetic-company-csrf-token"
ALLOWED_ORIGIN = "https://portal.example.invalid"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def company() -> CompanyRecord:
    return CompanyRecord(
        id=COMPANY_ID,
        name="Synthetic GmbH",
        industry="Beratung",
        status="prospect",
        internal_notes="Synthetic only",
        created_at=NOW,
        updated_at=NOW,
    )


def contact() -> CompanyContactRecord:
    return CompanyContactRecord(
        id=CONTACT_ID,
        company_id=COMPANY_ID,
        first_name="Jan",
        last_name="Beispiel",
        email="contact@example.invalid",
        phone=None,
        job_function="Einkauf",
        created_at=NOW,
        updated_at=NOW,
    )


def company_summary() -> CompanySummary:
    return CompanySummary(
        id=COMPANY_ID,
        name="Synthetic GmbH",
        industry="Beratung",
        status="prospect",
        updated_at=NOW,
    )


class FakeSessionRepository:
    def __init__(self, roles=("internal",), principal=True) -> None:
        self.value = None
        if principal:
            self.value = SessionPrincipal(
                session_id=UUID("00000000-0000-4000-8000-000000000114"),
                user_id=USER_ID,
                display_name="Synthetic Internal",
                roles=roles,
                authenticated_at=NOW,
                idle_expires_at=NOW + timedelta(minutes=30),
                absolute_expires_at=NOW + timedelta(hours=8),
                csrf_token_hash=digest_token(CSRF_TOKEN),
            )

    async def refresh_active_session(self, *args, **kwargs):
        return self.value


class FakeCompanyService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.detail = CompanyDetail(company(), (contact(),))
        self.company_result = company()
        self.contact_result = contact()

    async def list_companies(self, **values):
        self.calls.append(("list_companies", values))
        return (company_summary(),)

    async def get_company(self, **values):
        self.calls.append(("get_company", values))
        return self.detail

    async def create_company(self, **values):
        self.calls.append(("create_company", values))
        return self.detail

    async def update_company(self, **values):
        self.calls.append(("update_company", values))
        return self.company_result

    async def add_contact(self, **values):
        self.calls.append(("add_contact", values))
        return self.contact_result

    async def update_contact(self, **values):
        self.calls.append(("update_contact", values))
        return self.contact_result


def client(repository=None, service=None) -> AsyncClient:
    app = create_app(
        session_repository=repository,
        company_service=service,
        allowed_origin=ALLOWED_ORIGIN,
        clock=lambda: NOW,
    )
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url=ALLOWED_ORIGIN,
    )


def headers(**extra) -> dict[str, str]:
    return {
        "Origin": ALLOWED_ORIGIN,
        "X-CSRF-Token": CSRF_TOKEN,
        **extra,
    }


def create_payload() -> dict[str, object]:
    return {
        "name": "Synthetic GmbH",
        "industry": "Beratung",
        "internal_notes": "Synthetic only",
        "initial_contact": {
            "first_name": "Jan",
            "last_name": "Beispiel",
            "email": "contact@example.invalid",
            "job_function": "Einkauf",
        },
    }


@pytest.mark.anyio
async def test_company_api_fails_closed_without_runtime_service() -> None:
    async with client(FakeSessionRepository()) as api:
        api.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await api.get("/api/v1/portal/companies")

    assert response.status_code == 503
    assert response.json()["code"] == "portal_unavailable"


@pytest.mark.anyio
async def test_company_list_requires_internal_session_and_is_no_store() -> None:
    service = FakeCompanyService()
    async with client(FakeSessionRepository(("coach",)), service) as api:
        api.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        forbidden = await api.get("/api/v1/portal/companies")
    async with client(FakeSessionRepository(), service) as api:
        api.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await api.get("/api/v1/portal/companies?query=Synthetic&limit=10")

    assert forbidden.status_code == 403
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json()["items"][0]["name"] == "Synthetic GmbH"
    assert "internal_notes" not in response.json()["items"][0]
    assert service.calls[0][1]["query"] == "Synthetic"


@pytest.mark.anyio
async def test_company_create_requires_exact_origin_and_csrf() -> None:
    service = FakeCompanyService()
    async with client(FakeSessionRepository(), service) as api:
        api.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        bad_origin = await api.post(
            "/api/v1/portal/companies",
            json=create_payload(),
            headers=headers(Origin="https://attacker.example.invalid"),
        )
        bad_csrf = await api.post(
            "/api/v1/portal/companies",
            json=create_payload(),
            headers=headers(**{"X-CSRF-Token": "wrong"}),
        )

    assert bad_origin.status_code == 403
    assert bad_csrf.status_code == 403
    assert service.calls == []


@pytest.mark.anyio
async def test_company_create_returns_company_and_initial_contact() -> None:
    service = FakeCompanyService()
    async with client(FakeSessionRepository(), service) as api:
        api.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await api.post(
            "/api/v1/portal/companies",
            json=create_payload(),
            headers=headers(),
        )

    assert response.status_code == 201
    assert response.json()["id"] == str(COMPANY_ID)
    assert response.json()["contacts"][0]["id"] == str(CONTACT_ID)
    assert service.calls[0][0] == "create_company"
    assert service.calls[0][1]["actor"].user_id == USER_ID


@pytest.mark.anyio
async def test_company_and_contact_corrections_pass_only_explicit_fields() -> None:
    service = FakeCompanyService()
    async with client(FakeSessionRepository(), service) as api:
        api.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        company_response = await api.patch(
            f"/api/v1/portal/companies/{COMPANY_ID}",
            json={"industry": None},
            headers=headers(),
        )
        contact_response = await api.patch(
            f"/api/v1/portal/companies/{COMPANY_ID}/contacts/{CONTACT_ID}",
            json={"phone": "0931 0000"},
            headers=headers(),
        )

    assert company_response.status_code == 200
    assert contact_response.status_code == 200
    assert service.calls[0][1]["changes"] == {"industry": None}
    assert service.calls[1][1]["changes"] == {"phone": "0931 0000"}


@pytest.mark.anyio
async def test_empty_patch_and_missing_company_are_generic() -> None:
    service = FakeCompanyService()
    service.company_result = None
    async with client(FakeSessionRepository(), service) as api:
        api.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        empty = await api.patch(
            f"/api/v1/portal/companies/{COMPANY_ID}",
            json={},
            headers=headers(),
        )
        missing = await api.patch(
            f"/api/v1/portal/companies/{COMPANY_ID}",
            json={"name": "Missing"},
            headers=headers(),
        )

    assert empty.status_code == 400
    assert missing.status_code == 404
    assert missing.json()["code"] == "company_record_not_found"
