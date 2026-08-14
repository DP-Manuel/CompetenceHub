from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.auth.mfa_service import (
    MfaRateLimited,
    MfaRejected,
    MfaSessionCreated,
    TotpEnrollmentCreated,
)
from competence_hub_api.main import create_app
from competence_hub_api.security.cookies import LOGIN_COOKIE_NAME, SESSION_COOKIE_NAME

NOW = datetime(2026, 8, 14, 12, 0, tzinfo=UTC)
ALLOWED_ORIGIN = "https://portal.example.invalid"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeMfaService:
    def __init__(self, outcome) -> None:
        self.outcome = outcome
        self.calls: list[tuple[str, dict]] = []

    async def start_totp_enrollment(self, **values):
        self.calls.append(("start_totp_enrollment", values))
        return self.outcome

    async def confirm_totp_enrollment(self, **values):
        self.calls.append(("confirm_totp_enrollment", values))
        return self.outcome

    async def verify_totp(self, **values):
        self.calls.append(("verify_totp", values))
        return self.outcome

    async def verify_recovery_code(self, **values):
        self.calls.append(("verify_recovery_code", values))
        return self.outcome


def _client(service=None) -> AsyncClient:
    app = create_app(
        mfa_service=service,
        allowed_origin=ALLOWED_ORIGIN,
        clock=lambda: NOW,
    )
    client = AsyncClient(
        transport=ASGITransport(app=app, client=("192.0.2.30", 43123)),
        base_url=ALLOWED_ORIGIN,
    )
    client.cookies.set(LOGIN_COOKIE_NAME, "synthetic-login-token")
    return client


def _headers() -> dict[str, str]:
    return {"Origin": ALLOWED_ORIGIN, "X-CSRF-Token": "synthetic-csrf-token"}


@pytest.mark.anyio
async def test_mfa_fails_closed_without_runtime_service() -> None:
    async with _client() as client:
        response = await client.post("/api/v1/auth/mfa/totp/enrollment", headers=_headers())

    assert response.status_code == 503
    assert response.json()["code"] == "authentication_unavailable"


@pytest.mark.anyio
async def test_enrollment_requires_exact_origin_and_csrf() -> None:
    service = FakeMfaService(MfaRejected())
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/mfa/totp/enrollment",
            headers={"Origin": "https://wrong.example.invalid"},
        )

    assert response.status_code == 403
    assert service.calls == []


@pytest.mark.anyio
async def test_enrollment_returns_provisioning_uri_without_session() -> None:
    service = FakeMfaService(
        TotpEnrollmentCreated("otpauth://totp/synthetic-secret-uri")
    )
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/mfa/totp/enrollment",
            headers=_headers(),
        )

    assert response.status_code == 201
    assert response.json() == {
        "provisioning_uri": "otpauth://totp/synthetic-secret-uri"
    }
    assert SESSION_COOKIE_NAME not in "".join(response.headers.get_list("set-cookie"))
    assert service.calls[0][1] == {
        "login_token": "synthetic-login-token",
        "csrf_token": "synthetic-csrf-token",
        "now": NOW,
    }


@pytest.mark.anyio
async def test_enrollment_confirmation_returns_recovery_once_and_rotates_cookie() -> None:
    service = FakeMfaService(
        MfaSessionCreated(
            session_token="synthetic-session-token",
            csrf_token="synthetic-session-csrf",
            recovery_codes=("AAAA-BBBB-CCCC-DDDD", "EEEE-FFFF-GGGG-HHHH"),
        )
    )
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/mfa/totp/enrollment/confirm",
            json={"code": "123456"},
            headers=_headers(),
        )

    assert response.status_code == 200
    assert response.json()["recovery_codes"] == [
        "AAAA-BBBB-CCCC-DDDD",
        "EEEE-FFFF-GGGG-HHHH",
    ]
    assert response.headers["x-csrf-token"] == "synthetic-session-csrf"
    cookies = "".join(response.headers.get_list("set-cookie"))
    assert SESSION_COOKIE_NAME in cookies
    assert "synthetic-session-token" in cookies
    assert f'{LOGIN_COOKIE_NAME}=""' in cookies
    assert "HttpOnly" in cookies and "Secure" in cookies and "SameSite=lax" in cookies


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("path", "method"),
    [
        ("/api/v1/auth/mfa/totp/verify", "verify_totp"),
        ("/api/v1/auth/mfa/recovery/verify", "verify_recovery_code"),
    ],
)
async def test_mfa_verification_returns_empty_rotated_session_response(
    path: str,
    method: str,
) -> None:
    service = FakeMfaService(
        MfaSessionCreated(
            session_token="synthetic-session-token",
            csrf_token="synthetic-session-csrf",
        )
    )
    async with _client(service) as client:
        response = await client.post(
            path,
            json={"code": "123456"},
            headers=_headers(),
        )

    assert response.status_code == 204
    assert response.content == b""
    assert service.calls[0][0] == method
    assert service.calls[0][1]["client_ip"] == "192.0.2.30"


@pytest.mark.anyio
async def test_mfa_rejects_unknown_fields_without_service_call() -> None:
    service = FakeMfaService(MfaRejected())
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/mfa/totp/verify",
            json={"code": "123456", "unexpected": True},
            headers=_headers(),
        )

    assert response.status_code == 400
    assert service.calls == []


@pytest.mark.anyio
async def test_mfa_rejection_is_generic_and_rate_limit_has_retry_after() -> None:
    rejected_service = FakeMfaService(MfaRejected())
    limited_service = FakeMfaService(MfaRateLimited(30))
    async with _client(rejected_service) as client:
        rejected = await client.post(
            "/api/v1/auth/mfa/totp/verify",
            json={"code": "000000"},
            headers=_headers(),
        )
    async with _client(limited_service) as client:
        limited = await client.post(
            "/api/v1/auth/mfa/totp/verify",
            json={"code": "000000"},
            headers=_headers(),
        )

    assert rejected.status_code == 401
    assert rejected.json()["code"] == "authentication_failed"
    assert limited.status_code == 429
    assert limited.headers["retry-after"] == "30"
