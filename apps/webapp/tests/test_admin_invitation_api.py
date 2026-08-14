from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.auth.account_lifecycle import (
    IdempotencyConflictError,
    LifecycleQueued,
)
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token

NOW = datetime(2026, 8, 14, 16, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000091")
SESSION_ID = UUID("00000000-0000-4000-8000-000000000093")
ALLOWED_ORIGIN = "https://portal.example.invalid"
SESSION_TOKEN = "synthetic-session-token"
CSRF_TOKEN = "synthetic-csrf-token"
IDEMPOTENCY_KEY = "synthetic-idempotency-key-0001"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeSessionRepository:
    def __init__(self, roles=("admin",)) -> None:
        self.principal = SessionPrincipal(
            session_id=SESSION_ID,
            user_id=USER_ID,
            display_name="Synthetic Admin",
            roles=roles,
            authenticated_at=NOW,
            idle_expires_at=NOW + timedelta(minutes=30),
            absolute_expires_at=NOW + timedelta(hours=8),
            csrf_token_hash=digest_token(CSRF_TOKEN),
        )

    async def refresh_active_session(self, *args, **kwargs):
        return self.principal


class FakeLifecycleService:
    def __init__(self, outcome=None) -> None:
        self.outcome = outcome or LifecycleQueued(recipient_user_id=USER_ID)
        self.calls = []

    async def issue_invitation(self, **values):
        self.calls.append(values)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def _client(repository=None, service=None) -> AsyncClient:
    app = create_app(
        session_repository=repository,
        account_lifecycle_service=service,
        allowed_origin=ALLOWED_ORIGIN,
        clock=lambda: NOW,
    )
    return AsyncClient(
        transport=ASGITransport(app=app, client=("192.0.2.60", 43123)),
        base_url=ALLOWED_ORIGIN,
    )


def _headers(**extra) -> dict[str, str]:
    return {
        "Origin": ALLOWED_ORIGIN,
        "X-CSRF-Token": CSRF_TOKEN,
        "Idempotency-Key": IDEMPOTENCY_KEY,
        **extra,
    }


def _payload(**extra):
    return {
        "email": "person@example.invalid",
        "display_name": "Synthetic Person",
        "role_codes": ["internal"],
        **extra,
    }


@pytest.mark.anyio
async def test_admin_invitation_requires_configured_service() -> None:
    async with _client(FakeSessionRepository()) as client:
        response = await client.post(
            "/api/v1/admin/users/invitations",
            json=_payload(),
            headers=_headers(),
        )

    assert response.status_code == 503


@pytest.mark.anyio
async def test_admin_invitation_requires_admin_session_and_exact_csrf_origin() -> None:
    service = FakeLifecycleService()
    async with _client(FakeSessionRepository(("internal",)), service) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        forbidden = await client.post(
            "/api/v1/admin/users/invitations",
            json=_payload(),
            headers=_headers(),
        )
    async with _client(FakeSessionRepository(), service) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        bad_origin = await client.post(
            "/api/v1/admin/users/invitations",
            json=_payload(),
            headers=_headers(Origin="https://attacker.example.invalid"),
        )

    assert forbidden.status_code == 403
    assert bad_origin.status_code == 403
    assert service.calls == []


@pytest.mark.anyio
async def test_admin_invitation_requires_idempotency_and_nonprivileged_role() -> None:
    service = FakeLifecycleService()
    async with _client(FakeSessionRepository(), service) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        missing_key = await client.post(
            "/api/v1/admin/users/invitations",
            json=_payload(),
            headers={"Origin": ALLOWED_ORIGIN, "X-CSRF-Token": CSRF_TOKEN},
        )
        privileged_role = await client.post(
            "/api/v1/admin/users/invitations",
            json=_payload(role_codes=["admin"]),
            headers=_headers(),
        )

    assert missing_key.status_code == 400
    assert privileged_role.status_code == 400
    assert service.calls == []


@pytest.mark.anyio
async def test_admin_invitation_returns_stable_token_free_reference() -> None:
    service = FakeLifecycleService(LifecycleQueued(USER_ID, replayed=True))
    async with _client(FakeSessionRepository(), service) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.post(
            "/api/v1/admin/users/invitations",
            json=_payload(),
            headers=_headers(),
        )

    assert response.status_code == 202
    assert response.json() == {"status": "accepted", "user_id": str(USER_ID)}
    assert response.headers["Idempotent-Replay"] == "true"
    assert service.calls[0]["idempotency_key"] == IDEMPOTENCY_KEY
    assert service.calls[0]["role_codes"] == ("internal",)
    assert "token" not in response.text.casefold()


@pytest.mark.anyio
async def test_admin_invitation_maps_idempotency_conflict_without_details() -> None:
    service = FakeLifecycleService(IdempotencyConflictError("private detail"))
    async with _client(FakeSessionRepository(), service) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.post(
            "/api/v1/admin/users/invitations",
            json=_payload(),
            headers=_headers(),
        )

    assert response.status_code == 409
    assert response.json()["code"] == "idempotency_conflict"
    assert "private detail" not in response.text
