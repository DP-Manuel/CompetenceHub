from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.auth.account_lifecycle import (
    LifecycleAccepted,
    LifecycleQueued,
    LifecycleRateLimited,
    LifecycleRejected,
)
from competence_hub_api.main import create_app
from competence_hub_api.security.cookies import LOGIN_COOKIE_NAME
from competence_hub_api.security.passwords import PasswordPolicyError

NOW = datetime(2026, 8, 14, 15, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000091")
ALLOWED_ORIGIN = "https://portal.example.invalid"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeLifecycleService:
    def __init__(self) -> None:
        self.reset_request_outcome = LifecycleQueued(
            recipient_user_id=None,
        )
        self.reset_confirm_outcome = LifecycleRejected()
        self.invitation_outcome = LifecycleRejected()
        self.calls: list[tuple[str, dict]] = []

    async def request_password_reset(self, **values):
        self.calls.append(("request_password_reset", values))
        return self.reset_request_outcome

    async def confirm_password_reset(self, **values):
        self.calls.append(("confirm_password_reset", values))
        if isinstance(self.reset_confirm_outcome, Exception):
            raise self.reset_confirm_outcome
        return self.reset_confirm_outcome

    async def accept_invitation(self, **values):
        self.calls.append(("accept_invitation", values))
        return self.invitation_outcome


def _client(service=None) -> AsyncClient:
    app = create_app(
        account_lifecycle_service=service,
        allowed_origin=ALLOWED_ORIGIN,
        clock=lambda: NOW,
    )
    return AsyncClient(
        transport=ASGITransport(app=app, client=("192.0.2.50", 43123)),
        base_url=ALLOWED_ORIGIN,
    )


@pytest.mark.anyio
async def test_reset_request_fails_closed_without_service() -> None:
    async with _client() as client:
        response = await client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "person@example.invalid"},
            headers={"Origin": ALLOWED_ORIGIN},
        )

    assert response.status_code == 503
    assert response.json()["code"] == "authentication_unavailable"


@pytest.mark.anyio
async def test_reset_request_requires_exact_origin_before_service_call() -> None:
    service = FakeLifecycleService()
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "person@example.invalid"},
            headers={"Origin": "https://attacker.example.invalid"},
        )

    assert response.status_code == 403
    assert service.calls == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "body",
    [
        {"email": "invalid"},
        {"email": "person@example.invalid", "unexpected": True},
    ],
)
async def test_reset_request_rejects_invalid_body_without_service_call(body) -> None:
    service = FakeLifecycleService()
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/password-reset/request",
            json=body,
            headers={"Origin": ALLOWED_ORIGIN},
        )

    assert response.status_code == 400
    assert service.calls == []


@pytest.mark.anyio
@pytest.mark.parametrize("known_account", [False, True])
async def test_reset_request_response_does_not_enumerate_accounts(
    known_account: bool,
) -> None:
    service = FakeLifecycleService()
    user_id = USER_ID if known_account else None
    service.reset_request_outcome = LifecycleQueued(
        recipient_user_id=user_id,
    )

    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "person@example.invalid"},
            headers={"Origin": ALLOWED_ORIGIN},
        )

    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    assert service.calls[0][1]["client_ip"] == "192.0.2.50"


@pytest.mark.anyio
async def test_reset_request_rate_limit_is_generic() -> None:
    service = FakeLifecycleService()
    service.reset_request_outcome = LifecycleRateLimited(45)
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "person@example.invalid"},
            headers={"Origin": ALLOWED_ORIGIN},
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "45"
    assert "person@example.invalid" not in response.text


@pytest.mark.anyio
async def test_queued_reset_response_contains_no_delivery_or_token_details() -> None:
    service = FakeLifecycleService()
    service.reset_request_outcome = LifecycleQueued(
        recipient_user_id=USER_ID,
    )
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "person@example.invalid"},
            headers={"Origin": ALLOWED_ORIGIN},
        )

    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    assert "delivery" not in response.text.casefold()
    assert str(USER_ID) not in response.text


@pytest.mark.anyio
async def test_password_reset_confirmation_returns_no_session() -> None:
    service = FakeLifecycleService()
    service.reset_confirm_outcome = LifecycleAccepted(user_id=USER_ID)
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "synthetic-reset-token",
                "password": "synthetic secure passphrase",
            },
            headers={"Origin": ALLOWED_ORIGIN},
        )

    assert response.status_code == 204
    assert LOGIN_COOKIE_NAME not in response.cookies
    assert "competence_hub_session=" in response.headers.get_list("set-cookie")[1]
    assert "Max-Age=0" in response.headers.get_list("set-cookie")[1]


@pytest.mark.anyio
async def test_invalid_token_and_password_policy_failure_share_generic_response() -> None:
    responses = []
    for outcome in (
        LifecycleRejected(),
        PasswordPolicyError("password_compromised"),
    ):
        service = FakeLifecycleService()
        service.reset_confirm_outcome = outcome
        async with _client(service) as client:
            responses.append(
                await client.post(
                    "/api/v1/auth/password-reset/confirm",
                    json={
                        "token": "synthetic-reset-token",
                        "password": "synthetic compromised password",
                    },
                    headers={"Origin": ALLOWED_ORIGIN},
                )
            )

    assert [response.status_code for response in responses] == [400, 400]
    assert [response.json()["code"] for response in responses] == [
        "request_not_accepted",
        "request_not_accepted",
    ]


@pytest.mark.anyio
async def test_invitation_acceptance_creates_only_mfa_enrollment_challenge() -> None:
    service = FakeLifecycleService()
    service.invitation_outcome = LifecycleAccepted(
        user_id=USER_ID,
        login_token="synthetic-login-token",
        csrf_token="synthetic-csrf-token",
    )
    async with _client(service) as client:
        response = await client.post(
            "/api/v1/auth/invitations/accept",
            json={
                "token": "synthetic-invitation-token",
                "password": "synthetic secure passphrase",
            },
            headers={"Origin": ALLOWED_ORIGIN},
        )

    assert response.status_code == 202
    assert response.json() == {
        "state": "mfa_enrollment_required",
        "csrf_token": "synthetic-csrf-token",
    }
    assert response.cookies[LOGIN_COOKIE_NAME] == "synthetic-login-token"
    assert any(
        "competence_hub_session=" in value and "Max-Age=0" in value
        for value in response.headers.get_list("set-cookie")
    )
    assert "synthetic-invitation-token" not in response.text
    assert "synthetic secure passphrase" not in response.text
