from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.portal.customers import (
    CompanyCustomerInput,
    CustomerAdministration,
    CustomerError,
    PrivateCustomerInput,
)
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token


ORIGIN = "https://portal.example.invalid"
BASE = "/api/v1/portal/customers"
CSRF = "synthetic-customer-csrf-token"
NOW = datetime(2026, 11, 20, tzinfo=UTC)


def actor(role: str) -> SessionPrincipal:
    return SessionPrincipal(uuid4(), uuid4(), "Demo", (role,), NOW, NOW + timedelta(minutes=30),
                            NOW + timedelta(hours=8), digest_token(CSRF))


class Sessions:
    def __init__(self, role):
        self.principal = actor(role) if role else None

    async def refresh_active_session(self, *_args, **_options):
        return self.principal


class Administration:
    async def save_private(self, principal, payload, now):
        assert principal.roles == ("internal",)
        return payload.model_dump()

    async def search_private(self, _principal, criteria):
        return {"items": [], "next_after": None}


def client(role, *, enabled=True):
    return TestClient(
        create_app(
            session_repository=Sessions(role),
            allowed_origin=ORIGIN,
            customer_administration=Administration() if enabled else None,
            clock=lambda: NOW,
        ),
        base_url=ORIGIN,
        cookies={SESSION_COOKIE_NAME: "synthetic-customer-session-token"},
    )


def test_private_customer_requires_names_only_and_does_not_accept_a_tenant():
    names = {"first_name": " Demo  ", "last_name": "Kunde"}
    customer = PrivateCustomerInput.model_validate(names)
    assert customer.first_name == "Demo"
    assert customer.email is customer.phone is customer.billing_address is None
    for fields in (
        {"company_id": str(uuid4())}, {"last_name": " "}, {"first_name": "Name\x00"},
        {"email": "sender@example.invalid,another@example.invalid"},
        {"billing_address": {"street": "Unvollständig"}}, {"vat_id": "123"},
    ):
        with pytest.raises(ValidationError):
            PrivateCustomerInput.model_validate({**names, **fields})


def test_b2b_details_are_optional_and_require_one_explicit_address_purpose():
    assert CompanyCustomerInput(version=0).address is None
    assert CompanyCustomerInput(version=0, vat_id=" de123456 ").vat_id == "DE123456"
    address = {"street": "Demo 1", "postal_code": "00000", "city": "Demo-Ort", "country": "Demo-Land"}
    for invalid in (
        {"version": True}, {"version": -1}, {"vat_id": "USt-72"},
        {"address": address}, {"address": {**address, "purpose": "unknown"}},
        {"company_id": str(uuid4())},
    ):
        with pytest.raises(ValidationError):
            CompanyCustomerInput.model_validate({"version": 0, **invalid})
    assert CompanyCustomerInput(version=1, address={**address, "purpose": "billing"}).address.purpose == "billing"


@pytest.mark.parametrize("role,status", [
    (None, 401), ("company_contact", 403), ("coach", 403), ("calendar_reviewer", 403),
])
def test_other_roles_are_denied_for_every_customer_route(role, status):
    headers = {"Origin": ORIGIN, "X-CSRF-Token": CSRF}
    record_id = uuid4()
    http = client(role)
    for method, route in (
        ("GET", "/capabilities"), ("POST", "/private"), ("POST", "/private/search"),
        ("GET", f"/private/{record_id}"), ("PUT", f"/private/{record_id}"),
        ("GET", f"/companies/{record_id}/details"), ("PUT", f"/companies/{record_id}/details"),
    ):
        response = http.request(method, BASE + route, headers=headers)
        assert response.status_code == status
        assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("role", ["internal", "admin"])
def test_disabled_feature_reports_no_capability_and_routes_stay_closed(role):
    http = client(role, enabled=False)
    assert http.get(BASE + "/capabilities").json() == {"enabled": False}
    assert http.get(BASE + f"/private/{uuid4()}").status_code == 404


def test_create_and_search_require_csrf_and_validation_does_not_echo_sensitive_values():
    http = client("internal")
    payload = {"first_name": "Demo", "last_name": "Kunde"}
    headers = {"Origin": ORIGIN, "X-CSRF-Token": CSRF}
    assert http.get(BASE + "/capabilities").json() == {"enabled": True}
    for endpoint in ("/private", "/private/search"):
        assert http.post(BASE + endpoint, json=payload).status_code == 403
        assert http.post(BASE + endpoint, json=payload, headers={**headers, "Origin": "https://other.invalid"}).status_code == 403
    response = http.post(BASE + "/private", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["billing_address"] is None
    rejected = http.post(BASE + "/private", json={**payload, "email": "private-marker"}, headers=headers)
    assert rejected.status_code == 400
    assert "private-marker" not in rejected.text
    assert http.post(BASE + "/private/search", json={"name": "Demo"}, headers=headers).status_code == 200


@pytest.mark.anyio
async def test_domain_rejects_disallowed_actors_before_any_sql():
    for role in ("coach", "company_contact", "calendar_reviewer"):
        with pytest.raises(CustomerError) as rejection:
            await CustomerAdministration(None).get_private(actor(role), uuid4())
        assert rejection.value.status == 403
