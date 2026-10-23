from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.main import create_app
from competence_hub_api.portal.coach_registry import CoachRegistryService
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from test_admin_invitation_api import FakeSessionRepository, ALLOWED_ORIGIN, CSRF_TOKEN
from test_coach_registry import MemoryRegistry, profile

BASE = "/api/v1/admin/coaches"
NOW = datetime(2026, 10, 23, tzinfo=UTC)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def client(roles=("admin",), configured=True, authenticated=True):
    app = create_app(
        session_repository=FakeSessionRepository(roles) if authenticated else None,
        coach_registry_service=(
            CoachRegistryService(MemoryRegistry()) if configured else None
        ),
        allowed_origin=ALLOWED_ORIGIN,
        clock=lambda: NOW,
    )
    result = AsyncClient(transport=ASGITransport(app=app), base_url=ALLOWED_ORIGIN)
    if authenticated:
        result.cookies.set(SESSION_COOKIE_NAME, "synthetic-session")
    return result


def headers(**changes):
    return {"Origin": ALLOWED_ORIGIN, "X-CSRF-Token": CSRF_TOKEN, **changes}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "roles", [("internal",), ("coach",), ("calendar_reviewer",), ("company_contact",)]
)
async def test_registry_reads_and_writes_require_admin(roles):
    async with client(roles) as c:
        assert (await c.get(BASE)).status_code == 403
        assert (
            await c.post(
                BASE,
                json={"display_name": "Synthetic", "client_request_id": str(uuid4())},
                headers=headers(),
            )
        ).status_code == 403


@pytest.mark.anyio
async def test_registry_unconfigured_or_unauthenticated_fail_closed():
    async with client(configured=False) as c:
        assert (await c.get(BASE)).status_code == 503
    async with client(authenticated=False) as c:
        assert (await c.get(BASE)).status_code == 401


@pytest.mark.anyio
@pytest.mark.parametrize(
    "extra", [{"Origin": "https://foreign.example.invalid"}, {"X-CSRF-Token": "wrong"}]
)
async def test_registry_csrf_and_origin_required_before_mutation(extra):
    async with client() as c:
        response = await c.post(
            BASE,
            json={"display_name": "Synthetic", "client_request_id": str(uuid4())},
            headers=headers(**extra),
        )
        assert response.status_code == 403
        assert (await c.get(BASE)).json()["items"] == []


@pytest.mark.anyio
async def test_registry_strict_payload_and_body_limit():
    async with client() as c:
        data = {
            "display_name": "Synthetic",
            "client_request_id": str(uuid4()),
            "portal_user_id": str(uuid4()),
        }
        assert (await c.post(BASE, json=data, headers=headers())).status_code == 400
        assert (
            await c.post(
                BASE,
                content='{"display_name":"' + "x" * 32769 + '"}',
                headers={**headers(), "Content-Type": "application/json"},
            )
        ).status_code == 400
        assert (await c.get(BASE + "?limit=101")).status_code == 422


@pytest.mark.anyio
async def test_complete_admin_revision_publication_and_no_delete_endpoint():
    async with client() as c:
        response = await c.post(
            BASE,
            json={"display_name": "Synthetic", "client_request_id": str(uuid4())},
            headers=headers(),
        )
        assert response.status_code == 201
        coach = response.json()
        path = BASE + "/" + coach["id"]
        assert response.headers["Cache-Control"] == "no-store"
        response = await c.post(
            path + "/revisions",
            json={
                "expected_version": coach["version"],
                "content": profile()
                .model_copy(update={"topic_ids": ()})
                .model_dump(mode="json"),
            },
            headers=headers(),
        )
        assert response.status_code == 200
        coach = response.json()
        revision = coach["revisions"][0]["id"]
        assert (
            await c.post(
                path + "/revisions/" + revision + "/submit",
                json={"expected_version": 1},
                headers=headers(),
            )
        ).status_code == 409
        coach = (
            await c.post(
                path + "/revisions/" + revision + "/submit",
                json={"expected_version": coach["version"]},
                headers=headers(),
            )
        ).json()
        for kind in ("content_review", "person_consent", "preview"):
            response = await c.post(
                path + "/revisions/" + revision + "/approvals",
                json={
                    "expected_version": coach["version"],
                    "kind": kind,
                    "evidence_ref": "synthetic-local",
                },
                headers=headers(),
            )
            assert response.status_code == 200
            coach = response.json()
        coach = (
            await c.patch(
                path + "/lifecycle",
                json={"expected_version": coach["version"], "lifecycle": "active"},
                headers=headers(),
            )
        ).json()
        response = await c.post(
            path + "/publications/preview",
            json={"expected_version": coach["version"], "revision_id": revision},
            headers=headers(),
        )
        assert response.status_code == 200
        assert response.json()["publications"]["preview"]["state"] == "published"
        assert (await c.delete(path, headers=headers())).status_code == 405
        assert (await c.get(path)).status_code == 200
