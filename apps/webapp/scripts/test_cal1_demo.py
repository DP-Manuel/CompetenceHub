"""Focused local contracts; no PostgreSQL, runtime config or real identities."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from scripts.browser_acceptance_app import (
    COACH_EMAIL, EMPTY_COACH_EMAIL, REVIEWER_EMAIL, INTERNAL_EMAIL,
    SyntheticSessionRepository, SYNTHETIC_IDENTITIES, utc_now,
)
from scripts.cal1_demo_app import create_demo_app, DemoCalendarRepository
from competence_hub_api.portal.calendar import (
    CalendarService, CalendarAccessDeniedError, CalendarVersionConflictError,
    CalendarTimeConflictError, CalendarIdempotencyConflictError,
    CalendarTransitionConflictError, CalendarTopicUnavailableError,
)
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def actor(email):
    from competence_hub_api.auth.admission import PORTAL_ADMISSION
    repo = SyntheticSessionRepository(policy=PORTAL_ADMISSION)
    token, _ = repo.activate(email)
    from competence_hub_api.security.tokens import digest_token
    return repo._principal(digest_token(token), utc_now())


def seeded(repo, status):
    return next(d for d in repo._offers.values() if d.current_revision.workflow_status == status)


def args(detail):
    return dict(actor=actor(COACH_EMAIL), offer_id=detail.offer.id,
                expected_version=detail.offer.lock_version, now=utc_now())


async def test_public_calendar_module_has_portable_javascript_mime():
    async with AsyncClient(transport=ASGITransport(app=create_demo_app()), base_url="https://127.0.0.1:8446") as client:
        response = await client.get("/demo-assets/calendar-month.mjs")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/javascript")
        assert "export function buildMonthLayout" in response.text
        assert 'type="module"' in (await client.get("/demo/")).text


async def test_publication_retains_old_revision_during_draft_and_change_request():
    repo = DemoCalendarRepository()
    service = CalendarService(repo)
    original = seeded(repo, "published")
    changed = await service.update_draft(**args(original), draft=replace(original.current_revision.draft,
        title="Private replacement", public_location="PRIVATE DRAFT MARKER"))
    assert changed.current_revision.revision_number == 2
    assert changed.published_revision == original.published_revision
    assert (await service.get_public_offer(offer_id=original.offer.id)).title == original.current_revision.draft.title
    submitted = await service.submit_offer(**args(changed))
    reviewed = await service.review_offer(**{**args(submitted), "actor": actor(REVIEWER_EMAIL)},
        outcome="changes_requested", note="PRIVATE REVIEW MARKER")
    assert (await service.get_public_offer(offer_id=reviewed.offer.id)).public_location != "PRIVATE DRAFT MARKER"
    assert reviewed.current_revision.workflow_status == "changes_requested"


async def test_revised_publication_then_withdrawal():
    repo = DemoCalendarRepository(); service = CalendarService(repo)
    original = seeded(repo, "changes_requested")
    draft = await service.update_draft(**args(original), draft=replace(original.current_revision.draft, title="DEMO corrected"))
    submitted = await service.submit_offer(**args(draft))
    published = await service.review_offer(**{**args(submitted), "actor": actor(REVIEWER_EMAIL)}, outcome="published", note=None)
    assert (await service.get_public_offer(offer_id=published.offer.id)).title == "DEMO corrected"
    withdrawn = await service.withdraw_offer(**args(published))
    assert await service.get_public_offer(offer_id=withdrawn.offer.id) is None
    with pytest.raises(CalendarTransitionConflictError):
        await service.update_draft(**args(withdrawn), draft=withdrawn.current_revision.draft)


async def test_stale_update_does_not_mutate_revision_or_history():
    repo = DemoCalendarRepository(); service = CalendarService(repo)
    d = seeded(repo, "draft")
    await service.update_draft(**args(d), draft=replace(d.current_revision.draft, title="A"))
    before = list(repo.history)
    with pytest.raises(CalendarVersionConflictError):
        await service.update_draft(**args(d), draft=replace(d.current_revision.draft, title="B"))
    assert repo.history == before
    assert repo._offers[d.offer.id].current_revision.draft.title == "A"


@pytest.mark.parametrize("email", [REVIEWER_EMAIL, INTERNAL_EMAIL])
async def test_non_coach_cannot_create(email):
    service = CalendarService(DemoCalendarRepository())
    with pytest.raises(CalendarAccessDeniedError):
        await service.create_offer(actor=actor(email), coach_id=None, client_request_id=uuid4(),
            draft=seeded(service._repository, "draft").current_revision.draft, now=utc_now())


async def test_coach_cannot_review_or_see_other_coach_draft():
    repo = DemoCalendarRepository(); service = CalendarService(repo)
    own = seeded(repo, "draft")
    assert await service.get_offer(actor=actor(EMPTY_COACH_EMAIL), offer_id=own.offer.id) is None
    with pytest.raises(CalendarAccessDeniedError):
        await service.review_offer(**args(seeded(repo, "in_review")), outcome="published", note=None)


async def test_overlap_same_coach_is_denied_but_drafts_can_overlap():
    repo = DemoCalendarRepository(); service = CalendarService(repo)
    d = seeded(repo, "draft"); pub = seeded(repo, "published")
    revised = await service.update_draft(**args(d), draft=pub.current_revision.draft)
    with pytest.raises(CalendarTimeConflictError):
        await service.submit_offer(**args(revised))
    # Two different Coaches have already published overlapping workshops.
    rows = [d for d in repo._offers.values() if d.published_revision]
    assert len(rows) == 2 and rows[0].offer.coach_id != rows[1].offer.coach_id


async def test_idempotent_creation_and_conflicting_replay():
    repo = DemoCalendarRepository(); service = CalendarService(repo)
    values = dict(actor=actor(COACH_EMAIL), coach_id=None, client_request_id=uuid4(),
                  draft=seeded(repo, "draft").current_revision.draft, now=utc_now())
    first = await service.create_offer(**values)
    assert (await service.create_offer(**values)).offer.id == first.offer.id
    with pytest.raises(CalendarIdempotencyConflictError):
        await service.create_offer(**{**values, "draft": replace(values["draft"], title="different")})
    with pytest.raises(CalendarTopicUnavailableError):
        await service.update_draft(**args(first), draft=replace(values["draft"], topic_id=uuid4()))


async def test_real_api_public_projection_pagination_filter_and_no_write_route():
    app = create_demo_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://127.0.0.1:8446") as client:
        query = {"from": (utc_now() + timedelta(minutes=1)).isoformat(),
                 "to": (utc_now() + timedelta(days=80)).isoformat(), "limit": 1}
        response = await client.get("/api/v1/calendar/offers", params=query)
        assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
        first = response.json(); assert first["next_cursor"]
        second = (await client.get("/api/v1/calendar/offers", params={**query, "cursor": first["next_cursor"]})).json()
        assert first["items"][0]["id"] != second["items"][0]["id"]
        item = first["items"][0]
        assert set(item) == {"id", "coach", "topic", "title", "summary", "starts_at", "ends_at", "time_zone", "format", "public_location", "capacity", "decision_deadline", "price_display_text", "updated_at"}
        assert set(item["coach"]) == {"display_name", "profile_path"}
        assert (await client.get(item["coach"]["profile_path"])).status_code == 200
        assert (await client.get("/api/v1/calendar/offers", params={**query, "topic_id": str(uuid4())})).json()["items"] == []
        assert (await client.post("/api/v1/calendar/offers", json={})).status_code == 405
        assert (await client.get("/demo/api/history")).status_code == 401


async def test_history_obeys_existing_session_and_ownership():
    app = create_demo_app()
    sessions = app.state.calendar_session_repository
    token, _ = sessions.activate(EMPTY_COACH_EMAIL)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://127.0.0.1:8446",
                           cookies={SESSION_COOKIE_NAME: token}) as client:
        response = await client.get("/demo/api/history")
        assert response.status_code == 200
        rows = response.json()["items"]
        assert len(rows) == 1 and rows[0]["title"] == "DEMO: Parallelworkshop"
        assert (await client.get("/portal/")).text.count("Nur synthetische Daten") == 1


async def test_independent_app_reset_does_not_keep_state():
    app = create_demo_app(); repo = app.state.demo_repository
    repo._offers.clear()
    fresh = create_demo_app()
    assert len(fresh.state.demo_repository._offers) == 5
    assert not fresh.state.account_lifecycle_service
    assert not getattr(fresh.state, "database_engine", None)


async def test_month_adapter_uses_only_approved_projection_and_signed_pagination():
    app = create_demo_app()
    month = utc_now().astimezone(ZoneInfo("Europe/Berlin")).strftime("%Y-%m")
    repo = app.state.demo_repository
    now = utc_now()
    published = seeded(repo, "published")
    replacement = await app.state.calendar_service.update_draft(**args(published),
        draft=replace(published.current_revision.draft, title="PRIVATE REPLACEMENT", summary="PRIVATE SUMMARY"))
    assert replacement.published_revision == published.published_revision
    # Pin seed dates to visible month; do not infer visibility from the test runner's day.
    start = datetime.fromisoformat(month + "-01T10:00:00+01:00")
    for key, detail in list(repo._offers.items()):
        if detail.published_revision:
            approved = replace(detail.published_revision, draft=replace(detail.published_revision.draft,
                starts_at=start, ends_at=start + timedelta(hours=2)))
            repo._offers[key] = replace(detail, published_revision=approved)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://127.0.0.1:8446") as client:
        response = await client.get("/demo/api/public-calendar", params={"month": month, "limit": 1})
        assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
        first = response.json()
        assert len(first["items"]) == 1 and first["next_cursor"]
        second = (await client.get("/demo/api/public-calendar", params={"month": month, "limit": 1, "cursor": first["next_cursor"]})).json()
        assert first["items"][0]["id"] != second["items"][0]["id"]
        assert second["next_cursor"] is None
        for item in first["items"] + second["items"]:
            assert set(item) == {"id", "coach", "topic", "title", "summary", "starts_at", "ends_at", "time_zone", "format", "public_location", "capacity", "decision_deadline", "price_display_text", "updated_at"}
        assert "PRIVATE" not in response.text + str(second)
        assert (await client.post("/demo/api/public-calendar", json={})).status_code == 405
        assert (await client.get("/demo/api/public-calendar", params={"month": month, "cursor": "tampered"})).status_code == 400
        assert (await client.get("/demo/api/public-calendar", params={"month": month, "topic_id": str(uuid4())})).json()["items"] == []
        # Native API now accepts the bounded current month, not unbounded history.
        assert (await client.get("/api/v1/calendar/offers", params={"from": (now - timedelta(days=1)).isoformat(), "to": (now + timedelta(days=20)).isoformat()})).status_code == 200


@pytest.mark.parametrize("month", ["2026-00", "2026-13", "2020-01", "3000-01", "2026-1", "bad", "2026-11-01"])
async def test_month_adapter_rejects_invalid_or_unbounded_window(month):
    async with AsyncClient(transport=ASGITransport(app=create_demo_app()), base_url="https://127.0.0.1:8446") as client:
        assert (await client.get("/demo/api/public-calendar", params={"month": month})).status_code == 400


@pytest.mark.parametrize("start_delta,end_delta,visible", [(-10, 2, True), (-2, 0, False), (0, 2, True), (31, 32, False)])
async def test_month_adapter_returns_overlap_not_only_start_date(start_delta, end_delta, visible):
    app = create_demo_app()
    app.state.clock = lambda: datetime(2026, 11, 6, tzinfo=timezone.utc)
    repo = app.state.demo_repository
    original = seeded(repo, "published")
    start = datetime(2026, 11, 1, tzinfo=ZoneInfo("Europe/Berlin"))
    revision = replace(original.published_revision, draft=replace(original.published_revision.draft,
        starts_at=start + timedelta(days=start_delta), ends_at=start + timedelta(days=end_delta)))
    repo._offers = {original.offer.id: replace(original, published_revision=revision)}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://127.0.0.1:8446") as client:
        response = await client.get("/demo/api/public-calendar", params={"month": "2026-11"})
        assert response.status_code == 200
        assert bool(response.json()["items"]) == visible
        # No duplication of the single underlying event.
        assert len(repo._offers) == 1
        withdrawn = replace(original.offer, lifecycle_status="withdrawn")
        repo._offers[original.offer.id] = replace(repo._offers[original.offer.id], offer=withdrawn)
        assert (await client.get("/demo/api/public-calendar", params={"month": "2026-11"})).json()["items"] == []
