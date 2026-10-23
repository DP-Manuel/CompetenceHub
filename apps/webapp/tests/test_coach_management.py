from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.main import create_app
from competence_hub_api.portal.coach_registry import (
    CoachRegistryService,
    management_capabilities,
    publication_ready,
)
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from test_admin_invitation_api import FakeSessionRepository, ALLOWED_ORIGIN
from test_coach_registry import ACTOR, MemoryRegistry, change, profile


@pytest.fixture
def anyio_backend():
    return "asyncio"


class SyntheticQueries:
    async def index(self, **kwargs):
        return {"items": [], "has_more": False, **kwargs}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "roles,status",
    [
        (("admin",), 200),
        (("internal",), 403),
        (("coach",), 403),
        (("calendar_reviewer",), 403),
        (("company_contact",), 403),
    ],
)
async def test_management_direct_entry_and_reads_are_server_authorized(roles, status):
    app = create_app(
        session_repository=FakeSessionRepository(roles),
        coach_registry_service=CoachRegistryService(MemoryRegistry()),
        coach_management_queries=SyntheticQueries(),
        allowed_origin=ALLOWED_ORIGIN,
    )
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=ALLOWED_ORIGIN
    ) as c:
        c.cookies.set(SESSION_COOKIE_NAME, "synthetic-session")
        for path in ("/portal/coaches/", "/api/v1/admin/coach-management"):
            response = await c.get(path)
            assert response.status_code == status
            assert response.headers["cache-control"] == "no-store"
            if status == 403:
                assert "Coachverwaltung" not in response.text
        if status == 200:
            assert (
                await c.get("/api/v1/admin/coach-management?limit=51")
            ).status_code == 422
            assert (
                await c.get("/api/v1/admin/coach-management?offset=-1")
            ).status_code == 422
            assert (
                await c.get("/api/v1/admin/coach-management?lifecycle=other")
            ).status_code == 422


@pytest.mark.anyio
async def test_management_optional_and_mfa_session_required():
    for repository, status in ((None, 401), (FakeSessionRepository(("admin",)), 503)):
        app = create_app(session_repository=repository)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url=ALLOWED_ORIGIN
        ) as c:
            c.cookies.set(SESSION_COOKIE_NAME, "synthetic-session")
            assert (await c.get("/portal/coaches/")).status_code == status


@pytest.mark.anyio
async def test_management_mutations_return_minimal_without_relaxing_contract():
    from test_coach_registry_api import client, headers, BASE

    async with client() as c:
        result = await c.post(
            BASE,
            json={"display_name": "Coach Alpha", "client_request_id": str(uuid4())},
            headers={**headers(), "Prefer": "return=minimal"},
        )
        assert result.status_code == 201
        item = result.json()
        assert "revisions" not in item and item["latest_revision_id"] is None
        path = BASE + "/" + item["id"] + "/revisions"
        result = await c.post(
            path,
            json={
                "expected_version": item["version"],
                "content": profile()
                .model_copy(update={"topic_ids": ()})
                .model_dump(mode="json"),
            },
            headers={**headers(), "Prefer": "return=minimal"},
        )
        assert result.status_code == 200 and result.json()["latest_revision_id"]
        assert "content" not in result.text and "revisions" not in result.json()
        assert (
            await c.post(
                path,
                json={
                    "expected_version": 1,
                    "content": profile().model_dump(mode="json"),
                },
                headers=headers(),
            )
        ).status_code == 409


@pytest.mark.anyio
async def test_management_capabilities_follow_offboard_reactivate_fresh_revision_contract():
    repo = MemoryRegistry()
    service = CoachRegistryService(repo)
    coach = await service.create(
        actor=ACTOR,
        display_name="Coach Alpha",
        request_id=uuid4(),
        now=datetime(2026, 1, 1, tzinfo=UTC),
    )
    caps = management_capabilities(coach, None)
    assert caps["new_revision"] and "active" not in caps["lifecycles"]
    coach = await change(service, coach, "revision", content=profile())
    r = coach.revisions[-1]
    assert management_capabilities(coach, r)["editable"]
    coach = await change(service, coach, "submit", revision_id=r.id)
    for kind in ("content_review", "person_consent", "preview"):
        coach = await change(
            service,
            coach,
            "approve",
            revision_id=r.id,
            kind=kind,
            evidence_ref="synthetic-local",
        )
    assert "active" in management_capabilities(coach, coach.revisions[-1])["lifecycles"]
    coach = await change(service, coach, "lifecycle", lifecycle="active")
    r = coach.revisions[-1]
    assert management_capabilities(coach, r)["publish"] == ["preview"]
    assert not publication_ready(coach, r, "production")
    assert management_capabilities(coach, r, future_calendar=True)["lifecycles"] == []
    coach = await change(
        service, coach, "publish", revision_id=r.id, environment="preview"
    )
    original_id = coach.id
    coach = await service.mutate(
        actor=ACTOR,
        coach_id=coach.id,
        expected_version=coach.version,
        operation="lifecycle",
        lifecycle="inactive",
        now=datetime(2027, 1, 1, tzinfo=UTC),
    )
    assert coach.publications["preview"].state == "withdrawn"
    assert (
        "active"
        not in management_capabilities(coach, coach.revisions[-1])["lifecycles"]
    )

    async def reentry(current, operation, **values):
        return await service.mutate(
            actor=ACTOR,
            coach_id=current.id,
            expected_version=current.version,
            operation=operation,
            now=datetime(2028, 1, 1, tzinfo=UTC),
            **values,
        )

    coach = await reentry(coach, "revision", content=profile())
    r = coach.revisions[-1]
    coach = await reentry(coach, "submit", revision_id=r.id)
    for kind in ("content_review", "person_consent"):
        coach = await reentry(
            coach, "approve", revision_id=r.id, kind=kind, evidence_ref="synthetic-2028"
        )
    coach = await service.mutate(
        actor=ACTOR,
        coach_id=coach.id,
        expected_version=coach.version,
        operation="lifecycle",
        lifecycle="active",
        now=datetime(2028, 1, 1, tzinfo=UTC),
    )
    assert coach.id == original_id and len(coach.revisions) == 2
    assert [r.created_at.year for r in coach.revisions] == [2026, 2028]
    assert any(
        event[0] == "coach_registry.lifecycle.inactive" and event[2].year == 2027
        for event in repo.audit
    )
    assert management_capabilities(coach, coach.revisions[-1])["publish"] == []


@pytest.mark.anyio
async def test_revision_id_cannot_cross_coach_and_unknown_payload_never_expands_permissions():
    from test_coach_registry_api import client, headers, BASE

    async with client() as c:
        coaches = []
        for name in ("Alpha", "Beta"):
            item = (
                await c.post(
                    BASE,
                    json={"display_name": name, "client_request_id": str(uuid4())},
                    headers=headers(),
                )
            ).json()
            coaches.append(
                (
                    await c.post(
                        BASE + "/" + item["id"] + "/revisions",
                        json={
                            "expected_version": 1,
                            "content": profile()
                            .model_copy(update={"topic_ids": ()})
                            .model_dump(mode="json"),
                        },
                        headers=headers(),
                    )
                ).json()
            )
        a, b = coaches
        response = await c.patch(
            BASE + "/" + a["id"] + "/revisions/" + b["revisions"][0]["id"],
            json={
                "expected_version": a["version"],
                "content": profile().model_dump(mode="json"),
            },
            headers=headers(),
        )
        assert response.status_code == 404
        assert "Synthetic public" not in response.text
        response = await c.patch(
            BASE + "/" + a["id"] + "/lifecycle",
            json={
                "expected_version": a["version"],
                "lifecycle": "active",
                "roles": ["admin"],
            },
            headers=headers(),
        )
        assert response.status_code == 400


def test_management_module_uses_safe_dom_and_no_release_or_credential_persistence():
    from importlib.resources import files

    source = (
        files("competence_hub_api")
        .joinpath("portal_ui", "coach-management.js")
        .read_text(encoding="utf-8")
    )
    for forbidden in (
        "innerHTML",
        "localStorage",
        "sessionStorage",
        "eval(",
        "github.com",
        "sftp",
        "subprocess",
    ):
        assert forbidden not in source
    for required in (
        'role", "tablist"',
        '"beforeunload"',
        "expected_version",
        '"return=minimal"',
        '"aria-invalid"',
    ):
        assert required in source
