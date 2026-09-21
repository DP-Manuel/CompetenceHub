from pathlib import Path
from datetime import UTC, datetime, timedelta

from cryptography import x509
from httpx import ASGITransport, AsyncClient
import pytest

from scripts.browser_acceptance_app import (
    ENROLLMENT_EMAIL,
    ADMIN_EMAIL,
    COACH_EMAIL,
    COMPANY_CONTACT_EMAIL,
    EMPTY_COACH_EMAIL,
    HOST,
    INTERNAL_EMAIL,
    REVIEWER_EMAIL,
    RECOVERY_CODE,
    SYNTHETIC_PASSWORD,
    TOTP_CODE,
    create_acceptance_app,
    create_loopback_certificate,
)

PORT = 18443
ORIGIN = f"https://{HOST}:{PORT}"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def mutation_headers(csrf_token: str) -> dict[str, str]:
    return {"Origin": ORIGIN, "X-CSRF-Token": csrf_token}


async def login(client: AsyncClient, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": SYNTHETIC_PASSWORD},
    )
    assert response.status_code == 202
    challenge = response.json()
    verified = await client.post(
        "/api/v1/auth/mfa/totp/verify",
        json={"code": TOTP_CODE},
        headers=mutation_headers(challenge["csrf_token"]),
    )
    assert verified.status_code == 204
    return verified.headers["x-csrf-token"]


def calendar_draft(topic_id: str) -> dict[str, object]:
    now = datetime.now(UTC)
    starts_at = now + timedelta(days=21)
    return {
        "topic_id": topic_id,
        "title": "Neuer synthetischer Termin",
        "summary": "Nur für den lokalen Test.",
        "starts_at": starts_at.isoformat(),
        "ends_at": (starts_at + timedelta(hours=2)).isoformat(),
        "time_zone": "Europe/Berlin",
        "format": "online",
        "public_location": None,
        "capacity": 10,
        "review_threshold": 5,
        "decision_deadline": (starts_at - timedelta(days=4)).isoformat(),
        "price_display_text": "Preis nach Abstimmung",
    }


@pytest.mark.anyio
async def test_synthetic_fixture_exercises_existing_mfa_company_and_logout_flow() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_acceptance_app(PORT)),
        base_url=ORIGIN,
    ) as client:
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": INTERNAL_EMAIL, "password": SYNTHETIC_PASSWORD},
        )
        assert login.status_code == 202
        login_body = login.json()
        assert login_body["state"] == "mfa_required"

        mfa = await client.post(
            "/api/v1/auth/mfa/totp/verify",
            json={"code": TOTP_CODE},
            headers=mutation_headers(login_body["csrf_token"]),
        )
        assert mfa.status_code == 204
        session_csrf = mfa.headers["x-csrf-token"]

        session = await client.get("/api/v1/auth/session")
        assert session.status_code == 200
        assert session.json()["user"]["roles"] == ["internal"]

        rotated = await client.post(
            "/api/v1/auth/session/csrf",
            headers={"Origin": ORIGIN},
        )
        assert rotated.status_code == 204
        rotated_csrf = rotated.headers["x-csrf-token"]
        assert rotated_csrf != session_csrf

        empty = await client.get("/api/v1/portal/companies")
        assert empty.status_code == 200
        assert empty.json() == {"items": []}

        created = await client.post(
            "/api/v1/portal/companies",
            headers=mutation_headers(rotated_csrf),
            json={
                "name": "Synthetic Browser GmbH",
                "industry": "Testing",
                "internal_notes": "Volatile acceptance record",
                "initial_contact": {
                    "first_name": "Erika",
                    "last_name": "Beispiel",
                    "email": "erika.beispiel@example.invalid",
                    "job_function": "Einkauf",
                },
            },
        )
        assert created.status_code == 201
        company_id = created.json()["id"]

        listed = await client.get("/api/v1/portal/companies?query=Browser")
        assert listed.status_code == 200
        assert listed.json()["items"][0]["name"] == "Synthetic Browser GmbH"
        assert "internal_notes" not in listed.json()["items"][0]

        added = await client.post(
            f"/api/v1/portal/companies/{company_id}/contacts",
            headers=mutation_headers(rotated_csrf),
            json={
                "first_name": "Max",
                "last_name": "Muster",
                "email": "max.muster@example.invalid",
            },
        )
        assert added.status_code == 201

        logged_out = await client.delete(
            "/api/v1/auth/session",
            headers=mutation_headers(rotated_csrf),
        )
        assert logged_out.status_code == 204
        assert (await client.get("/api/v1/auth/session")).status_code == 401


@pytest.mark.anyio
async def test_synthetic_fixture_exercises_enrollment_and_recovery_codes() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_acceptance_app(PORT)),
        base_url=ORIGIN,
    ) as client:
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": ENROLLMENT_EMAIL, "password": SYNTHETIC_PASSWORD},
        )
        login_body = login.json()
        assert login_body["state"] == "mfa_enrollment_required"

        enrollment = await client.post(
            "/api/v1/auth/mfa/totp/enrollment",
            headers=mutation_headers(login_body["csrf_token"]),
        )
        assert enrollment.status_code == 201
        assert enrollment.json()["provisioning_uri"].startswith("otpauth://")

        confirmed = await client.post(
            "/api/v1/auth/mfa/totp/enrollment/confirm",
            json={"code": TOTP_CODE},
            headers=mutation_headers(login_body["csrf_token"]),
        )
        assert confirmed.status_code == 200
        recovery_codes = confirmed.json()["recovery_codes"]
        assert RECOVERY_CODE in recovery_codes
        assert len(recovery_codes) == 10
        assert len(set(recovery_codes)) == 10


def test_loopback_certificate_has_no_nonlocal_subject_alternative_name(
    tmp_path: Path,
) -> None:
    certificate_path, key_path = create_loopback_certificate(tmp_path)
    certificate = x509.load_pem_x509_certificate(certificate_path.read_bytes())
    alternatives = certificate.extensions.get_extension_for_class(
        x509.SubjectAlternativeName
    ).value

    assert alternatives.get_values_for_type(x509.DNSName) == ["localhost"]
    assert [str(value) for value in alternatives.get_values_for_type(x509.IPAddress)] == [
        HOST
    ]
    assert key_path.read_text(encoding="ascii").startswith("-----BEGIN PRIVATE KEY-----")


@pytest.mark.anyio
async def test_calendar_fixture_exposes_role_specific_surfaces_fail_closed() -> None:
    app = create_acceptance_app(PORT)
    async with AsyncClient(transport=ASGITransport(app=app), base_url=ORIGIN) as client:
        await login(client, COACH_EMAIL)
        coach_capabilities = await client.get("/api/v1/portal/calendar/capabilities")
        coach_offers = await client.get("/api/v1/portal/calendar/offers")
        assert coach_capabilities.json()["can_manage_own_offers"] is True
        assert coach_capabilities.json()["can_review_offers"] is False
        assert len(coach_offers.json()["items"]) == 4
        foreign_offer_id = coach_offers.json()["items"][0]["id"]

        await login(client, EMPTY_COACH_EMAIL)
        empty_offers = await client.get("/api/v1/portal/calendar/offers")
        foreign_detail = await client.get(
            f"/api/v1/portal/calendar/offers/{foreign_offer_id}"
        )
        assert empty_offers.json() == {"items": []}
        assert foreign_detail.status_code == 404

        await login(client, REVIEWER_EMAIL)
        reviewer_capabilities = await client.get(
            "/api/v1/portal/calendar/capabilities"
        )
        queue = await client.get("/api/v1/portal/calendar/review-queue")
        assert reviewer_capabilities.json()["can_review_offers"] is True
        assert len(queue.json()["items"]) == 1
        assert queue.json()["items"][0]["coach_display_name"] == "Coach A"
        assert queue.json()["items"][0]["topic_name"] == "Führung und Zusammenarbeit"

        await login(client, ADMIN_EMAIL)
        admin_capabilities = await client.get("/api/v1/portal/calendar/capabilities")
        assert admin_capabilities.json()["can_administer_offers"] is True
        assert admin_capabilities.json()["can_review_offers"] is True

        for email in (INTERNAL_EMAIL, COMPANY_CONTACT_EMAIL):
            await login(client, email)
            denied = await client.get("/api/v1/portal/calendar/capabilities")
            assert denied.status_code == 403


@pytest.mark.anyio
async def test_calendar_fixture_supports_draft_stale_submit_revision_and_withdraw() -> None:
    app = create_acceptance_app(PORT)
    async with AsyncClient(transport=ASGITransport(app=app), base_url=ORIGIN) as client:
        csrf = await login(client, COACH_EMAIL)
        topics = await client.get("/api/v1/portal/calendar/topics")
        draft = calendar_draft(topics.json()["items"][0]["id"])
        created = await client.post(
            "/api/v1/portal/calendar/offers",
            headers=mutation_headers(csrf),
            json={
                "client_request_id": "00000000-0000-4000-8000-000000009999",
                "draft": draft,
            },
        )
        assert created.status_code == 201
        offer_id = created.json()["id"]
        first_etag = created.headers["etag"]

        changed = {**draft, "title": "Bearbeiteter synthetischer Termin"}
        updated = await client.patch(
            f"/api/v1/portal/calendar/offers/{offer_id}/draft",
            headers={**mutation_headers(csrf), "If-Match": first_etag},
            json=changed,
        )
        assert updated.status_code == 200
        assert updated.json()["current_revision"]["title"] == changed["title"]

        stale = await client.patch(
            f"/api/v1/portal/calendar/offers/{offer_id}/draft",
            headers={**mutation_headers(csrf), "If-Match": first_etag},
            json={**changed, "title": "Veraltete Änderung"},
        )
        assert stale.status_code == 409
        assert stale.json()["code"] == "calendar_version_conflict"

        submitted = await client.post(
            f"/api/v1/portal/calendar/offers/{offer_id}/submit",
            headers={**mutation_headers(csrf), "If-Match": updated.headers["etag"]},
        )
        assert submitted.status_code == 200
        assert submitted.json()["current_revision"]["workflow_status"] == "in_review"

        seeded = (await client.get("/api/v1/portal/calendar/offers")).json()["items"]
        changes_requested = next(
            item for item in seeded if item["workflow_status"] == "changes_requested"
        )
        detail = await client.get(
            f"/api/v1/portal/calendar/offers/{changes_requested['id']}"
        )
        revised = await client.patch(
            f"/api/v1/portal/calendar/offers/{changes_requested['id']}/draft",
            headers={**mutation_headers(csrf), "If-Match": detail.headers["etag"]},
            json={**draft, "title": "Revision nach Rückmeldung"},
        )
        assert revised.status_code == 200
        assert revised.json()["current_revision"]["revision_number"] == 2
        assert revised.json()["current_revision"]["workflow_status"] == "draft"

        withdrawn = await client.post(
            f"/api/v1/portal/calendar/offers/{offer_id}/withdraw",
            headers={
                **mutation_headers(csrf),
                "If-Match": submitted.headers["etag"],
            },
        )
        assert withdrawn.status_code == 200
        assert withdrawn.json()["lifecycle_status"] == "withdrawn"


@pytest.mark.anyio
async def test_calendar_fixture_reviewer_can_decide_submitted_offer_only() -> None:
    app = create_acceptance_app(PORT)
    async with AsyncClient(transport=ASGITransport(app=app), base_url=ORIGIN) as client:
        csrf = await login(client, REVIEWER_EMAIL)
        queue = await client.get("/api/v1/portal/calendar/review-queue")
        offer = queue.json()["items"][0]
        detail = await client.get(f"/api/v1/portal/calendar/offers/{offer['id']}")
        decided = await client.post(
            f"/api/v1/portal/calendar/offers/{offer['id']}/review-decisions",
            headers={**mutation_headers(csrf), "If-Match": detail.headers["etag"]},
            json={"outcome": "changes_requested", "note": "Bitte ergänzen."},
        )
        assert decided.status_code == 200
        assert decided.json()["current_revision"]["workflow_status"] == "changes_requested"
        assert (await client.get("/api/v1/portal/calendar/review-queue")).json() == {
            "items": []
        }
