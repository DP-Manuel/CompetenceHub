from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.portal.calendar import (
    CalendarAccessDeniedError,
    CalendarDraft,
    CalendarService,
    normalize_calendar_draft,
)

NOW = datetime(2026, 9, 17, 10, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000501")
COACH_ID = UUID("00000000-0000-4000-8000-000000000502")
TOPIC_ID = UUID("00000000-0000-4000-8000-000000000503")
OFFER_ID = UUID("00000000-0000-4000-8000-000000000504")
REQUEST_ID = UUID("00000000-0000-4000-8000-000000000505")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def principal(*roles: str) -> SessionPrincipal:
    return SessionPrincipal(
        session_id=UUID("00000000-0000-4000-8000-000000000506"),
        user_id=USER_ID,
        display_name="Synthetic Calendar User",
        roles=roles,
        authenticated_at=NOW,
        idle_expires_at=NOW + timedelta(minutes=30),
        absolute_expires_at=NOW + timedelta(hours=8),
        csrf_token_hash=b"c" * 32,
    )


def draft(**changes) -> CalendarDraft:
    values = {
        "topic_id": TOPIC_ID,
        "title": "  Synthetic Workshop  ",
        "summary": "  Synthetic summary  ",
        "starts_at": NOW + timedelta(days=14),
        "ends_at": NOW + timedelta(days=14, hours=2),
        "time_zone": "Europe/Berlin",
        "format_code": " PRAESENZ ",
        "public_location": "  Wuerzburg  ",
        "capacity": 30,
        "review_threshold": 10,
        "decision_deadline": NOW + timedelta(days=7),
        "price_display_text": "  Preis nach Abstimmung  ",
    }
    values.update(changes)
    return CalendarDraft(**values)


class FakeRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.result = None

    async def create_offer(self, **values):
        self.calls.append(("create_offer", values))
        return self.result

    async def get_offer(self, **values):
        self.calls.append(("get_offer", values))
        return self.result

    async def update_draft(self, **values):
        self.calls.append(("update_draft", values))
        return self.result

    async def submit_offer(self, **values):
        self.calls.append(("submit_offer", values))
        return self.result

    async def review_offer(self, **values):
        self.calls.append(("review_offer", values))
        return self.result

    async def withdraw_offer(self, **values):
        self.calls.append(("withdraw_offer", values))
        return self.result


@pytest.mark.anyio
async def test_coach_create_normalizes_fields_and_cannot_select_another_coach() -> None:
    repository = FakeRepository()
    service = CalendarService(repository)

    await service.create_offer(
        actor=principal("coach"),
        coach_id=None,
        client_request_id=REQUEST_ID,
        draft=draft(),
        now=NOW,
    )

    values = repository.calls[0][1]
    assert values["allow_any_coach"] is False
    assert values["requested_coach_id"] is None
    assert values["draft"].title == "Synthetic Workshop"
    assert values["draft"].format_code == "praesenz"
    assert values["draft"].public_location == "Wuerzburg"

    with pytest.raises(CalendarAccessDeniedError):
        await service.create_offer(
            actor=principal("coach"),
            coach_id=COACH_ID,
            client_request_id=REQUEST_ID,
            draft=draft(),
            now=NOW,
        )


@pytest.mark.anyio
async def test_admin_must_select_coach_unless_admin_is_also_a_coach() -> None:
    repository = FakeRepository()
    service = CalendarService(repository)

    with pytest.raises(ValueError, match="coach_id"):
        await service.create_offer(
            actor=principal("admin"),
            coach_id=None,
            client_request_id=REQUEST_ID,
            draft=draft(),
            now=NOW,
        )

    await service.create_offer(
        actor=principal("admin"),
        coach_id=COACH_ID,
        client_request_id=REQUEST_ID,
        draft=draft(),
        now=NOW,
    )
    assert repository.calls[0][1]["allow_any_coach"] is True


@pytest.mark.anyio
async def test_internal_role_alone_has_no_calendar_access() -> None:
    repository = FakeRepository()
    service = CalendarService(repository)

    with pytest.raises(CalendarAccessDeniedError):
        await service.get_offer(actor=principal("internal"), offer_id=OFFER_ID)
    with pytest.raises(CalendarAccessDeniedError):
        await service.review_offer(
            actor=principal("internal"),
            offer_id=OFFER_ID,
            expected_version=1,
            outcome="published",
            note=None,
            now=NOW,
        )

    assert repository.calls == []


@pytest.mark.anyio
async def test_reviewer_can_review_and_withdraw_but_change_request_needs_note() -> None:
    repository = FakeRepository()
    service = CalendarService(repository)
    reviewer = principal("internal", "calendar_reviewer")

    with pytest.raises(ValueError, match="requires a note"):
        await service.review_offer(
            actor=reviewer,
            offer_id=OFFER_ID,
            expected_version=2,
            outcome="changes_requested",
            note="  ",
            now=NOW,
        )

    await service.review_offer(
        actor=reviewer,
        offer_id=OFFER_ID,
        expected_version=2,
        outcome="changes_requested",
        note="  Bitte Ort konkretisieren.  ",
        now=NOW,
    )
    await service.withdraw_offer(
        actor=reviewer,
        offer_id=OFFER_ID,
        expected_version=3,
        now=NOW,
    )

    assert repository.calls[0][1]["note"] == "Bitte Ort konkretisieren."
    assert repository.calls[1][1]["allow_any_coach"] is True


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"format_code": "phone"}, "format_code"),
        ({"format_code": "hybrid", "public_location": ""}, "public_location"),
        ({"capacity": 0}, "capacity"),
        ({"capacity": 5, "review_threshold": 6}, "review_threshold"),
        ({"decision_deadline": NOW + timedelta(days=15)}, "decision_deadline"),
        ({"time_zone": "Mars/Olympus"}, "time_zone"),
    ],
)
def test_draft_validation_rejects_invalid_publication_fields(changes, message) -> None:
    with pytest.raises(ValueError, match=message):
        normalize_calendar_draft(draft(**changes), now=NOW)


def test_rolling_window_uses_three_calendar_months() -> None:
    month_end = datetime(2026, 1, 31, 10, 0, tzinfo=UTC)
    valid = draft(
        starts_at=datetime(2026, 4, 30, 8, 0, tzinfo=UTC),
        ends_at=datetime(2026, 4, 30, 9, 0, tzinfo=UTC),
        decision_deadline=datetime(2026, 4, 20, 8, 0, tzinfo=UTC),
    )
    assert normalize_calendar_draft(valid, now=month_end).title

    outside = draft(
        starts_at=datetime(2026, 4, 30, 23, 30, tzinfo=UTC),
        ends_at=datetime(2026, 5, 1, 0, 30, tzinfo=UTC),
        decision_deadline=datetime(2026, 4, 20, 8, 0, tzinfo=UTC),
    )
    with pytest.raises(ValueError, match="three-month"):
        normalize_calendar_draft(outside, now=month_end)


@pytest.mark.anyio
async def test_company_contact_cannot_mutate_calendar() -> None:
    repository = FakeRepository()
    service = CalendarService(repository)

    with pytest.raises(CalendarAccessDeniedError):
        await service.withdraw_offer(
            actor=principal("company_contact"),
            offer_id=OFFER_ID,
            expected_version=1,
            now=NOW,
        )

    assert repository.calls == []
