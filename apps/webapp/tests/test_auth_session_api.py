from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token

NOW = datetime(2026, 8, 13, 14, 0, tzinfo=UTC)
SESSION_TOKEN = "synthetic-session-token"
CSRF_TOKEN = "synthetic-csrf-token"
ALLOWED_ORIGIN = "https://app.test.invalid"


class FakeSessionRepository:
    def __init__(self, principal: SessionPrincipal | None) -> None:
        self.principal = principal
        self.refreshed: list[tuple[bytes, datetime, timedelta]] = []
        self.found: list[tuple[bytes, datetime]] = []
        self.revoked: list[tuple[bytes, datetime, str]] = []

    async def refresh_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        idle_timeout: timedelta,
    ) -> SessionPrincipal | None:
        self.refreshed.append((token_hash, now, idle_timeout))
        return self.principal

    async def find_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
    ) -> SessionPrincipal | None:
        self.found.append((token_hash, now))
        return self.principal

    async def revoke_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        reason: str,
    ) -> None:
        self.revoked.append((token_hash, now, reason))


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def principal() -> SessionPrincipal:
    return SessionPrincipal(
        session_id=UUID("00000000-0000-4000-8000-000000000001"),
        user_id=UUID("00000000-0000-4000-8000-000000000002"),
        display_name="Synthetic Internal User",
        roles=("admin", "internal"),
        authenticated_at=NOW - timedelta(minutes=5),
        idle_expires_at=NOW + timedelta(minutes=30),
        absolute_expires_at=NOW + timedelta(hours=7),
        csrf_token_hash=digest_token(CSRF_TOKEN),
    )


def test_session_principal_repr_does_not_expose_csrf_digest(
    principal: SessionPrincipal,
) -> None:
    assert principal.csrf_token_hash.hex() not in repr(principal)


def _app(repository: FakeSessionRepository | None = None):
    return create_app(
        session_repository=repository,
        allowed_origin=ALLOWED_ORIGIN,
        clock=lambda: NOW,
    )


def _client(repository: FakeSessionRepository | None = None) -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=_app(repository)),
        base_url=ALLOWED_ORIGIN,
    )


@pytest.mark.anyio
async def test_session_endpoint_denies_access_without_runtime_repository() -> None:
    async with _client() as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.get("/api/v1/auth/session")

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "authentication_failed"


@pytest.mark.anyio
async def test_active_session_returns_only_safe_identity_fields(
    principal: SessionPrincipal,
) -> None:
    repository = FakeSessionRepository(principal)
    async with _client(repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.get("/api/v1/auth/session")

    assert response.status_code == 200
    assert response.json() == {
        "user": {
            "id": str(principal.user_id),
            "display_name": principal.display_name,
            "roles": ["admin", "internal"],
        },
        "authenticated_at": "2026-08-13T13:55:00+00:00",
        "idle_expires_at": "2026-08-13T14:30:00+00:00",
        "absolute_expires_at": "2026-08-13T21:00:00+00:00",
    }
    assert repository.refreshed == [
        (digest_token(SESSION_TOKEN), NOW, timedelta(minutes=30))
    ]
    assert SESSION_TOKEN.encode("ascii") not in repository.refreshed[0][0]


@pytest.mark.anyio
async def test_unknown_or_expired_session_gets_generic_unauthorized() -> None:
    repository = FakeSessionRepository(None)
    async with _client(repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.get("/api/v1/auth/session")

    assert response.status_code == 401
    assert response.json()["code"] == "authentication_failed"


@pytest.mark.anyio
async def test_logout_without_session_is_idempotent_and_clears_cookie() -> None:
    repository = FakeSessionRepository(None)
    async with _client(repository) as client:
        response = await client.delete("/api/v1/auth/session")

    assert response.status_code == 204
    assert f"{SESSION_COOKIE_NAME}=" in response.headers["set-cookie"]
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert repository.found == []
    assert repository.revoked == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("origin", "csrf_token"),
    [
        (None, CSRF_TOKEN),
        ("https://wrong.test.invalid", CSRF_TOKEN),
        (ALLOWED_ORIGIN, None),
        (ALLOWED_ORIGIN, "wrong-csrf-token"),
    ],
)
async def test_logout_rejects_bad_origin_or_csrf_without_revocation(
    principal: SessionPrincipal,
    origin: str | None,
    csrf_token: str | None,
) -> None:
    repository = FakeSessionRepository(principal)
    headers = {}
    if origin is not None:
        headers["Origin"] = origin
    if csrf_token is not None:
        headers["X-CSRF-Token"] = csrf_token

    async with _client(repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.delete(
            "/api/v1/auth/session",
            headers=headers,
        )

    assert response.status_code == 403
    assert response.json()["code"] == "request_verification_failed"
    assert repository.revoked == []
    assert repository.refreshed == []


@pytest.mark.anyio
async def test_logout_revokes_active_session_and_clears_cookie(
    principal: SessionPrincipal,
) -> None:
    repository = FakeSessionRepository(principal)
    async with _client(repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.delete(
            "/api/v1/auth/session",
            headers={"Origin": ALLOWED_ORIGIN, "X-CSRF-Token": CSRF_TOKEN},
        )

    assert response.status_code == 204
    assert repository.revoked == [
        (digest_token(SESSION_TOKEN), NOW, "user_logout")
    ]
    assert repository.refreshed == []
    assert "Max-Age=0" in response.headers["set-cookie"]
