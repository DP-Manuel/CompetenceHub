from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.auth.login_service import (
    LoginAccepted,
    LoginRateLimited,
    LoginRejected,
)
from competence_hub_api.main import create_app
from competence_hub_api.security.cookies import LOGIN_COOKIE_NAME

NOW = datetime(2026, 8, 14, 10, 0, tzinfo=UTC)
ALLOWED_ORIGIN = "https://portal.example.invalid"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeLoginService:
    def __init__(self, outcome) -> None:
        self.outcome = outcome
        self.calls: list[dict] = []

    async def authenticate(self, **values):
        self.calls.append(values)
        return self.outcome


def _client(service=None) -> AsyncClient:
    app = create_app(login_service=service, clock=lambda: NOW)
    return AsyncClient(
        transport=ASGITransport(app=app, client=("192.0.2.20", 43123)),
        base_url=ALLOWED_ORIGIN,
    )


@pytest.mark.anyio
async def test_login_fails_closed_without_runtime_service() -> None:
    async with _client() as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "person@example.invalid", "password": "synthetic"},
        )

    assert response.status_code == 503
    assert response.json()["code"] == "authentication_unavailable"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "request_kwargs",
    [
        {"content": "not json", "headers": {"Content-Type": "text/plain"}},
        {"json": {"email": "invalid", "password": "synthetic"}},
        {
            "json": {
                "email": "person@example.invalid",
                "password": "synthetic",
                "unexpected": True,
            }
        },
        {
            "json": {
                "email": "person@example.invalid",
                "password": "x" * 129,
            }
        },
    ],
)
async def test_login_rejects_invalid_requests_without_service_call(
    request_kwargs: dict,
) -> None:
    service = FakeLoginService(LoginRejected())
    async with _client(service) as client:
        response = await client.post("/api/v1/auth/login", **request_kwargs)

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"
    assert service.calls == []


@pytest.mark.anyio
async def test_login_rejects_streamed_body_over_32_kib() -> None:
    service = FakeLoginService(LoginRejected())
    oversized_password = "x" * (32 * 1024)
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "person@example.invalid",
                "password": oversized_password,
            },
        )

    assert response.status_code == 400
    assert service.calls == []


@pytest.mark.anyio
async def test_rejected_login_is_generic_and_uses_network_peer() -> None:
    service = FakeLoginService(LoginRejected())
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": " Person@Example.Invalid ",
                "password": "synthetic password",
            },
            headers={"X-Forwarded-For": "203.0.113.99"},
        )

    assert response.status_code == 401
    assert response.json()["code"] == "authentication_failed"
    assert service.calls == [
        {
            "normalized_email": "person@example.invalid",
            "password": "synthetic password",
            "client_ip": "192.0.2.20",
            "now": NOW,
        }
    ]


@pytest.mark.anyio
async def test_rate_limited_login_returns_retry_after() -> None:
    service = FakeLoginService(LoginRateLimited(retry_after_seconds=30))
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "person@example.invalid", "password": "synthetic"},
        )

    assert response.status_code == 429
    assert response.headers["retry-after"] == "30"
    assert response.json()["code"] == "rate_limit_exceeded"


@pytest.mark.anyio
async def test_successful_first_factor_sets_secure_pre_auth_cookie() -> None:
    service = FakeLoginService(
        LoginAccepted(
            state="mfa_required",
            login_token="synthetic-login-token",
            csrf_token="synthetic-csrf-token",
        )
    )
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "person@example.invalid", "password": "synthetic"},
        )

    assert response.status_code == 202
    assert response.json() == {
        "state": "mfa_required",
        "csrf_token": "synthetic-csrf-token",
    }
    cookies = response.headers.get_list("set-cookie")
    login_cookie = next(value for value in cookies if value.startswith(LOGIN_COOKIE_NAME))
    assert "synthetic-login-token" in login_cookie
    assert "HttpOnly" in login_cookie
    assert "Secure" in login_cookie
    assert "SameSite=lax" in login_cookie
    assert "Path=/" in login_cookie
    assert "Max-Age=300" in login_cookie
    assert "competence_hub_session" not in "".join(cookies)
