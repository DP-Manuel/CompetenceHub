from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.portal.calendar import (
    CalendarDraft,
    CalendarOfferDetail,
    CalendarOfferRecord,
    CalendarReviewDecision,
    CalendarRevisionRecord,
    CalendarService,
    CalendarTopic,
    CalendarVersionConflictError,
    PublicCalendarOffer,
)
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token

NOW = datetime(2026, 9, 17, 10, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000711")
COACH_ID = UUID("00000000-0000-4000-8000-000000000712")
OTHER_COACH_ID = UUID("00000000-0000-4000-8000-000000000713")
TOPIC_ID = UUID("00000000-0000-4000-8000-000000000714")
OFFER_ID = UUID("00000000-0000-4000-8000-000000000715")
REVISION_ID = UUID("00000000-0000-4000-8000-000000000716")
REQUEST_ID = UUID("00000000-0000-4000-8000-000000000717")
SESSION_TOKEN = "synthetic-calendar-session"
CSRF_TOKEN = "synthetic-calendar-csrf"
ORIGIN = "https://portal.example.invalid"
CURSOR_KEY = b"synthetic-calendar-api-cursor-key"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def draft() -> CalendarDraft:
    return CalendarDraft(
        topic_id=TOPIC_ID,
        title="Synthetic Workshop",
        summary="Synthetic public summary",
        starts_at=NOW + timedelta(days=14),
        ends_at=NOW + timedelta(days=14, hours=2),
        time_zone="Europe/Berlin",
        format_code="praesenz",
        public_location="Wuerzburg",
        capacity=30,
        review_threshold=10,
        decision_deadline=NOW + timedelta(days=7),
        price_display_text="Preis nach Abstimmung",
    )


def detail(*, status: str = "draft", version: int = 1) -> CalendarOfferDetail:
    submitted_at = NOW if status != "draft" else None
    published_at = NOW if status == "published" else None
    revision = CalendarRevisionRecord(
        id=REVISION_ID,
        offer_id=OFFER_ID,
        revision_number=1,
        workflow_status=status,
        draft=draft(),
        created_by_user_id=USER_ID,
        submitted_at=submitted_at,
        published_at=published_at,
        created_at=NOW,
        updated_at=NOW,
        topic_name="Synthetic Topic",
    )
    return CalendarOfferDetail(
        offer=CalendarOfferRecord(
            id=OFFER_ID,
            coach_id=COACH_ID,
            created_by_user_id=USER_ID,
            client_request_id=REQUEST_ID,
            lifecycle_status="active",
            lock_version=version,
            withdrawn_at=None,
            created_at=NOW,
            updated_at=NOW,
            coach_display_name="Synthetic Coach",
        ),
        current_revision=revision,
        published_revision=revision if status == "published" else None,
    )


def public_offer(*, profile_path: str | None = "/coaches/synthetic-coach/") -> PublicCalendarOffer:
    value = draft()
    return PublicCalendarOffer(
        id=OFFER_ID,
        coach_display_name="Synthetic Coach",
        coach_profile_path=profile_path,
        topic_id=TOPIC_ID,
        topic_name="Synthetic Topic",
        title=value.title,
        summary=value.summary,
        starts_at=value.starts_at,
        ends_at=value.ends_at,
        time_zone=value.time_zone,
        format_code=value.format_code,
        public_location=value.public_location,
        capacity=value.capacity,
        decision_deadline=value.decision_deadline,
        price_display_text=value.price_display_text,
        updated_at=NOW,
    )


class FakeSessionRepository:
    def __init__(self, roles: tuple[str, ...] | None) -> None:
        self.value = None
        if roles is not None:
            self.value = SessionPrincipal(
                session_id=UUID("00000000-0000-4000-8000-000000000718"),
                user_id=USER_ID,
                display_name="Synthetic Calendar User",
                roles=roles,
                authenticated_at=NOW,
                idle_expires_at=NOW + timedelta(minutes=30),
                absolute_expires_at=NOW + timedelta(hours=8),
                csrf_token_hash=digest_token(CSRF_TOKEN),
            )

    async def refresh_active_session(self, *args, **kwargs):
        return self.value


class FakeCalendarRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.detail = detail()
        self.public_items: tuple[PublicCalendarOffer, ...] = (public_offer(),)
        self.public_detail: PublicCalendarOffer | None = public_offer()
        self.failure: Exception | None = None

    async def _result(self, name: str, values: dict):
        self.calls.append((name, values))
        if self.failure is not None:
            raise self.failure
        return self.detail

    async def list_topics(self, **values):
        self.calls.append(("list_topics", values))
        return (CalendarTopic(TOPIC_ID, "Synthetic Topic"),)

    async def create_offer(self, **values):
        return await self._result("create_offer", values)

    async def get_offer(self, **values):
        return await self._result("get_offer", values)

    async def list_offers(self, **values):
        self.calls.append(("list_offers", values))
        return (self.detail,)

    async def list_review_queue(self, **values):
        self.calls.append(("list_review_queue", values))
        return (self.detail,)

    async def get_review_decision(self, **values):
        self.calls.append(("get_review_decision", values))
        return CalendarReviewDecision("changes_requested", "Synthetic note", NOW)

    async def update_draft(self, **values):
        return await self._result("update_draft", values)

    async def submit_offer(self, **values):
        return await self._result("submit_offer", values)

    async def review_offer(self, **values):
        return await self._result("review_offer", values)

    async def withdraw_offer(self, **values):
        return await self._result("withdraw_offer", values)

    async def list_public_offers(self, **values):
        self.calls.append(("list_public_offers", values))
        return self.public_items

    async def get_public_offer(self, **values):
        self.calls.append(("get_public_offer", values))
        return self.public_detail


def api(roles: tuple[str, ...] | None, repository: FakeCalendarRepository) -> AsyncClient:
    app = create_app(
        session_repository=FakeSessionRepository(roles),
        calendar_service=CalendarService(repository),
        calendar_cursor_hmac_key=CURSOR_KEY,
        allowed_origin=ORIGIN,
        clock=lambda: NOW,
    )
    return AsyncClient(transport=ASGITransport(app=app), base_url=ORIGIN)


def mutation_headers(**changes: str) -> dict[str, str]:
    return {"Origin": ORIGIN, "X-CSRF-Token": CSRF_TOKEN, **changes}


def draft_payload() -> dict[str, object]:
    value = draft()
    return {
        "topic_id": str(value.topic_id),
        "title": value.title,
        "summary": value.summary,
        "starts_at": value.starts_at.isoformat(),
        "ends_at": value.ends_at.isoformat(),
        "time_zone": value.time_zone,
        "format": value.format_code,
        "public_location": value.public_location,
        "capacity": value.capacity,
        "review_threshold": value.review_threshold,
        "decision_deadline": value.decision_deadline.isoformat(),
        "price_display_text": value.price_display_text,
    }


@pytest.mark.anyio
async def test_protected_calendar_requires_completed_mfa_session() -> None:
    repository = FakeCalendarRepository()
    async with api(None, repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.get("/api/v1/portal/calendar/offers")

        assert response.status_code == 401
    assert repository.calls == []


@pytest.mark.anyio
async def test_calendar_capabilities_and_topics_follow_server_roles() -> None:
    repository = FakeCalendarRepository()
    async with api(("coach",), repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        capabilities = await client.get("/api/v1/portal/calendar/capabilities")
        topics = await client.get("/api/v1/portal/calendar/topics")

    assert capabilities.status_code == 200
    assert capabilities.json() == {
        "can_manage_own_offers": True,
        "can_review_offers": False,
        "can_administer_offers": False,
    }
    assert topics.status_code == 200
    assert topics.json() == {
        "items": [{"id": str(TOPIC_ID), "name": "Synthetic Topic"}]
    }
    assert repository.calls[-1] == (
        "list_topics",
        {"actor_user_id": USER_ID, "allow_any_coach": False},
    )


@pytest.mark.anyio
@pytest.mark.parametrize("roles", [("internal",), ("company_contact",)])
async def test_calendar_capabilities_fail_closed_for_non_calendar_roles(
    roles: tuple[str, ...],
) -> None:
    async with api(roles, FakeCalendarRepository()) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.get("/api/v1/portal/calendar/capabilities")

    assert response.status_code == 403
    assert response.json()["code"] == "authorization_failed"


@pytest.mark.anyio
async def test_coach_list_is_own_scope_and_cannot_filter_another_coach() -> None:
    repository = FakeCalendarRepository()
    async with api(("coach",), repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        allowed = await client.get("/api/v1/portal/calendar/offers")
        denied = await client.get(
            f"/api/v1/portal/calendar/offers?coach_id={OTHER_COACH_ID}"
        )

    assert allowed.status_code == 200
    assert allowed.headers["Cache-Control"] == "no-store"
    assert allowed.json()["items"][0]["coach_display_name"] == "Synthetic Coach"
    assert allowed.json()["items"][0]["topic_name"] == "Synthetic Topic"
    assert allowed.json()["items"][0]["revision_number"] == 1
    assert repository.calls[0][1]["allow_any_coach"] is False
    assert denied.status_code == 403


@pytest.mark.anyio
@pytest.mark.parametrize("roles", [("internal",), ("company_contact",)])
async def test_internal_and_company_contact_have_no_protected_calendar_access(
    roles: tuple[str, ...],
) -> None:
    repository = FakeCalendarRepository()
    async with api(roles, repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.get("/api/v1/portal/calendar/offers")

    assert response.status_code == 403
    assert repository.calls == []


@pytest.mark.anyio
async def test_admin_can_filter_and_reviewer_can_publish() -> None:
    admin_repository = FakeCalendarRepository()
    async with api(("admin",), admin_repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        admin_response = await client.get(
            f"/api/v1/portal/calendar/offers?coach_id={COACH_ID}"
        )
    reviewer_repository = FakeCalendarRepository()
    async with api(("calendar_reviewer",), reviewer_repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        review_response = await client.post(
            f"/api/v1/portal/calendar/offers/{OFFER_ID}/review-decisions",
            json={"outcome": "published", "note": None},
            headers={**mutation_headers(), "If-Match": '"v1"'},
        )

    assert admin_response.status_code == 200
    assert admin_repository.calls[0][1]["allow_any_coach"] is True
    assert review_response.status_code == 200
    assert reviewer_repository.calls[0][0] == "review_offer"


@pytest.mark.anyio
async def test_mutation_requires_exact_origin_csrf_and_rejects_unknown_fields() -> None:
    repository = FakeCalendarRepository()
    payload = {
        "client_request_id": str(REQUEST_ID),
        "draft": draft_payload(),
    }
    async with api(("coach",), repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        bad_origin = await client.post(
            "/api/v1/portal/calendar/offers",
            json=payload,
            headers=mutation_headers(Origin="https://attacker.example.invalid"),
        )
        bad_csrf = await client.post(
            "/api/v1/portal/calendar/offers",
            json=payload,
            headers=mutation_headers(**{"X-CSRF-Token": "wrong"}),
        )
        bad_body = await client.post(
            "/api/v1/portal/calendar/offers",
            json={
                **payload,
                "draft": {
                    **draft_payload(),
                    "public_profile_path": "/coaches/forbidden/",
                },
            },
            headers=mutation_headers(),
        )

    assert [bad_origin.status_code, bad_csrf.status_code, bad_body.status_code] == [
        403,
        403,
        400,
    ]
    assert repository.calls == []


@pytest.mark.anyio
async def test_calendar_mutation_enforces_32_kib_body_limit() -> None:
    repository = FakeCalendarRepository()
    async with api(("coach",), repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.post(
            "/api/v1/portal/calendar/offers",
            content=b'{' + (b'"padding":"x",' * 3000) + b'}',
            headers={**mutation_headers(), "Content-Type": "application/json"},
        )

    assert response.status_code == 400
    assert repository.calls == []


@pytest.mark.anyio
async def test_stale_version_is_generic_conflict_without_mutation_detail() -> None:
    repository = FakeCalendarRepository()
    repository.failure = CalendarVersionConflictError("private version detail")
    async with api(("coach",), repository) as client:
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.patch(
            f"/api/v1/portal/calendar/offers/{OFFER_ID}/draft",
            json=draft_payload(),
            headers={**mutation_headers(), "If-Match": '"v1"'},
        )

    assert response.status_code == 409
    assert response.json()["code"] == "calendar_version_conflict"
    assert "private version detail" not in response.text


@pytest.mark.anyio
async def test_public_projection_is_minimized_and_null_profile_has_no_fallback() -> None:
    repository = FakeCalendarRepository()
    repository.public_items = (public_offer(profile_path=None),)
    async with api(None, repository) as client:
        response = await client.get(
            "/api/v1/calendar/offers",
            params={
                "from": (NOW + timedelta(days=1)).isoformat(),
                "to": (NOW + timedelta(days=30)).isoformat(),
            },
        )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["coach"]["profile_path"] is None
    assert set(item) == {
        "id",
        "coach",
        "topic",
        "title",
        "summary",
        "starts_at",
        "ends_at",
        "time_zone",
        "format",
        "public_location",
        "capacity",
        "decision_deadline",
        "price_display_text",
        "updated_at",
    }
    forbidden = {
        "coach_id",
        "portal_user_id",
        "reviewer_user_id",
        "review_threshold",
        "lock_version",
        "client_request_id",
        "review_decision",
    }
    assert forbidden.isdisjoint(item)
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.anyio
async def test_public_cursor_is_bounded_signed_and_tampering_fails_closed() -> None:
    repository = FakeCalendarRepository()
    repository.public_items = (public_offer(), public_offer(profile_path=None))
    params = {
        "from": (NOW + timedelta(days=1)).isoformat(),
        "to": (NOW + timedelta(days=30)).isoformat(),
        "limit": "1",
    }
    async with api(None, repository) as client:
        first = await client.get("/api/v1/calendar/offers", params=params)
        token = first.json()["next_cursor"]
        tampered = f"{'A' if token[0] != 'A' else 'B'}{token[1:]}"
        rejected = await client.get(
            "/api/v1/calendar/offers", params={**params, "cursor": tampered}
        )

    assert first.status_code == 200
    assert len(first.json()["items"]) == 1
    assert token
    assert rejected.status_code == 400


@pytest.mark.anyio
async def test_public_unknown_offer_is_generic_not_found() -> None:
    repository = FakeCalendarRepository()
    repository.public_detail = None
    async with api(None, repository) as client:
        response = await client.get(f"/api/v1/calendar/offers/{OFFER_ID}")

    assert response.status_code == 404
    assert response.json()["code"] == "calendar_offer_not_found"
