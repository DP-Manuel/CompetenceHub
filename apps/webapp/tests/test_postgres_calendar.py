from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.portal.calendar import (
    CalendarDraft,
    CalendarIdempotencyConflictError,
    CalendarTimeConflictError,
)
from competence_hub_api.portal.postgres_calendar import (
    PostgresCalendarRepository,
    _AUDIT,
    _LOCK_COACH,
    _OVERLAP_EXISTS,
)

NOW = datetime(2026, 9, 17, 12, 0, tzinfo=UTC)
ACTOR_ID = UUID("00000000-0000-4000-8000-000000000601")
COACH_ID = UUID("00000000-0000-4000-8000-000000000602")
TOPIC_ID = UUID("00000000-0000-4000-8000-000000000603")
OFFER_ID = UUID("00000000-0000-4000-8000-000000000604")
REVISION_ID = UUID("00000000-0000-4000-8000-000000000605")
REQUEST_ID = UUID("00000000-0000-4000-8000-000000000606")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def draft() -> CalendarDraft:
    return CalendarDraft(
        topic_id=TOPIC_ID,
        title="Synthetic Workshop",
        summary=None,
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


def offer_row(*, version: int = 1, lifecycle: str = "active") -> dict[str, object]:
    return {
        "id": OFFER_ID,
        "coach_id": COACH_ID,
        "created_by_user_id": ACTOR_ID,
        "client_request_id": REQUEST_ID,
        "lifecycle_status": lifecycle,
        "lock_version": version,
        "withdrawn_at": NOW if lifecycle == "withdrawn" else None,
        "created_at": NOW,
        "updated_at": NOW,
    }


def revision_row(*, status: str = "draft", number: int = 1) -> dict[str, object]:
    value = draft()
    submitted_at = NOW if status != "draft" else None
    published_at = NOW if status == "published" else None
    return {
        "id": REVISION_ID,
        "offer_id": OFFER_ID,
        "revision_number": number,
        "workflow_status": status,
        "topic_id": value.topic_id,
        "title": value.title,
        "summary": value.summary,
        "starts_at": value.starts_at,
        "ends_at": value.ends_at,
        "time_zone": value.time_zone,
        "format_code": value.format_code,
        "public_location": value.public_location,
        "capacity": value.capacity,
        "review_threshold": value.review_threshold,
        "decision_deadline": value.decision_deadline,
        "price_display_text": value.price_display_text,
        "created_by_user_id": ACTOR_ID,
        "submitted_at": submitted_at,
        "published_at": published_at,
        "created_at": NOW,
        "updated_at": NOW,
    }


class FakeResult:
    def __init__(self, *, scalar=None, row=None, rows=()) -> None:
        self.scalar = scalar
        self.row = row
        self.rows = tuple(rows)

    def mappings(self):
        return self

    def one(self):
        return self.row

    def one_or_none(self):
        return self.row

    def all(self):
        return self.rows


class FakeConnection:
    def __init__(self, results=()) -> None:
        self.results = iter(results)
        self.executed: list[tuple[object, dict | None]] = []

    async def execute(self, statement, parameters=None):
        self.executed.append((statement, parameters))
        return next(self.results, FakeResult())

    async def scalar(self, statement, parameters=None):
        result = await self.execute(statement, parameters)
        return result.scalar


class FakeContext:
    def __init__(self, connection) -> None:
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class FakeEngine:
    def __init__(self, results=()) -> None:
        self.connection = FakeConnection(results)

    def connect(self):
        return FakeContext(self.connection)

    def begin(self):
        return FakeContext(self.connection)


@pytest.mark.anyio
async def test_create_is_serialized_idempotent_topic_scoped_and_audited() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(scalar=None),
            FakeResult(scalar=COACH_ID),
            FakeResult(scalar=True),
            FakeResult(scalar=OFFER_ID),
            FakeResult(scalar=REVISION_ID),
            FakeResult(),
            FakeResult(row=offer_row()),
            FakeResult(row=revision_row()),
            FakeResult(row=None),
        ]
    )
    repository = PostgresCalendarRepository(engine)

    created = await repository.create_offer(
        actor_user_id=ACTOR_ID,
        allow_any_coach=False,
        requested_coach_id=None,
        client_request_id=REQUEST_ID,
        draft=draft(),
        now=NOW,
    )

    assert created.offer.id == OFFER_ID
    assert created.current_revision.workflow_status == "draft"
    calls = engine.connection.executed
    assert "pg_advisory_xact_lock" in str(calls[0][0])
    assert calls[3][1] == {"coach_id": COACH_ID, "topic_id": TOPIC_ID}
    assert calls[6][1]["action"] == "calendar.offer.created"
    assert set(calls[6][1]) == {"actor_user_id", "offer_id", "action", "now"}


@pytest.mark.anyio
async def test_create_retry_returns_existing_offer_without_writes() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(scalar=OFFER_ID),
            FakeResult(row=offer_row()),
            FakeResult(row=revision_row()),
            FakeResult(row=None),
        ]
    )
    repository = PostgresCalendarRepository(engine)

    retried = await repository.create_offer(
        actor_user_id=ACTOR_ID,
        allow_any_coach=False,
        requested_coach_id=None,
        client_request_id=REQUEST_ID,
        draft=draft(),
        now=NOW,
    )

    assert retried.offer.id == OFFER_ID
    assert len(engine.connection.executed) == 5
    assert _AUDIT not in [call[0] for call in engine.connection.executed]


@pytest.mark.anyio
async def test_create_retry_rejects_changed_content() -> None:
    engine = FakeEngine(
        [
            FakeResult(),
            FakeResult(scalar=OFFER_ID),
            FakeResult(row=offer_row()),
            FakeResult(row=revision_row()),
            FakeResult(row=None),
        ]
    )
    repository = PostgresCalendarRepository(engine)
    changed = replace(draft(), title="Changed")

    with pytest.raises(CalendarIdempotencyConflictError):
        await repository.create_offer(
            actor_user_id=ACTOR_ID,
            allow_any_coach=False,
            requested_coach_id=None,
            client_request_id=REQUEST_ID,
            draft=changed,
            now=NOW,
        )

    assert _AUDIT not in [call[0] for call in engine.connection.executed]


@pytest.mark.anyio
async def test_submit_locks_coach_before_half_open_overlap_check_and_audits() -> None:
    engine = FakeEngine(
        [
            FakeResult(row=offer_row()),
            FakeResult(row=revision_row()),
            FakeResult(row=None),
            FakeResult(scalar=True),
            FakeResult(),
            FakeResult(scalar=False),
            FakeResult(),
            FakeResult(),
            FakeResult(),
            FakeResult(row=offer_row(version=2)),
            FakeResult(row=revision_row(status="in_review")),
            FakeResult(row=None),
        ]
    )
    repository = PostgresCalendarRepository(engine)

    submitted = await repository.submit_offer(
        actor_user_id=ACTOR_ID,
        allow_any_coach=False,
        offer_id=OFFER_ID,
        expected_version=1,
        now=NOW,
    )

    assert submitted.offer.lock_version == 2
    assert submitted.current_revision.workflow_status == "in_review"
    calls = engine.connection.executed
    lock_index = next(i for i, call in enumerate(calls) if call[0] is _LOCK_COACH)
    overlap_index = next(i for i, call in enumerate(calls) if call[0] is _OVERLAP_EXISTS)
    assert lock_index < overlap_index
    overlap_sql = str(_OVERLAP_EXISTS).lower()
    assert "revision.starts_at < :ends_at" in overlap_sql
    assert "revision.ends_at > :starts_at" in overlap_sql
    assert calls[8][1]["action"] == "calendar.offer.submitted"


@pytest.mark.anyio
async def test_submit_overlap_aborts_before_state_change_or_audit() -> None:
    engine = FakeEngine(
        [
            FakeResult(row=offer_row()),
            FakeResult(row=revision_row()),
            FakeResult(row=None),
            FakeResult(scalar=True),
            FakeResult(),
            FakeResult(scalar=True),
        ]
    )
    repository = PostgresCalendarRepository(engine)

    with pytest.raises(CalendarTimeConflictError):
        await repository.submit_offer(
            actor_user_id=ACTOR_ID,
            allow_any_coach=False,
            offer_id=OFFER_ID,
            expected_version=1,
            now=NOW,
        )

    statements = [call[0] for call in engine.connection.executed]
    assert _AUDIT not in statements
    assert not any("workflow_status = 'in_review'" in str(item) for item in statements)


@pytest.mark.anyio
async def test_submit_retry_returns_completed_transition_without_duplicate_audit() -> None:
    engine = FakeEngine(
        [
            FakeResult(row=offer_row(version=2)),
            FakeResult(row=revision_row(status="in_review")),
            FakeResult(row=None),
        ]
    )
    repository = PostgresCalendarRepository(engine)

    retried = await repository.submit_offer(
        actor_user_id=ACTOR_ID,
        allow_any_coach=False,
        offer_id=OFFER_ID,
        expected_version=1,
        now=NOW,
    )

    assert retried.current_revision.workflow_status == "in_review"
    assert len(engine.connection.executed) == 3
    assert _AUDIT not in [call[0] for call in engine.connection.executed]


def test_audit_statement_cannot_store_calendar_payload() -> None:
    sql = str(_AUDIT).lower()
    for forbidden in (
        "title",
        "summary",
        "starts_at",
        "price_display_text",
        "review_threshold",
        "note",
    ):
        assert forbidden not in sql
