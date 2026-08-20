from pathlib import Path

from cryptography import x509
from httpx import ASGITransport, AsyncClient
import pytest

from scripts.browser_acceptance_app import (
    ENROLLMENT_EMAIL,
    HOST,
    INTERNAL_EMAIL,
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
