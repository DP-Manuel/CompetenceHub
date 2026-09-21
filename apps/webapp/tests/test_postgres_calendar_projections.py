from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from competence_hub_api.portal.postgres_calendar import (
    PostgresCalendarRepository,
    _AUDIT,
    _LATEST_REVIEW_DECISION,
    _PUBLIC_OFFER,
    _PUBLIC_OFFERS,
    _REVIEW_QUEUE,
    _VISIBLE_OFFERS,
    _VISIBLE_TOPICS,
)

NOW = datetime(2026, 9, 17, 10, 0, tzinfo=UTC)
OFFER_ID = UUID("00000000-0000-4000-8000-000000000721")
TOPIC_ID = UUID("00000000-0000-4000-8000-000000000722")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class Result:
    def __init__(self, rows=(), row=None) -> None:
        self.rows = tuple(rows)
        self.row = row

    def mappings(self):
        return self

    def all(self):
        return self.rows

    def one_or_none(self):
        return self.row


class Connection:
    def __init__(self, results) -> None:
        self.results = iter(results)
        self.calls = []

    async def execute(self, statement, parameters=None):
        self.calls.append((statement, parameters))
        return next(self.results)


class Context:
    def __init__(self, connection) -> None:
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, *args):
        return False


class Engine:
    def __init__(self, results) -> None:
        self.connection = Connection(results)

    def connect(self):
        return Context(self.connection)


def public_row(profile_path=None):
    return {
        "id": OFFER_ID,
        "coach_display_name": "Synthetic Coach",
        "coach_profile_path": profile_path,
        "topic_id": TOPIC_ID,
        "topic_name": "Synthetic Topic",
        "title": "Synthetic Offer",
        "summary": None,
        "starts_at": NOW + timedelta(days=14),
        "ends_at": NOW + timedelta(days=14, hours=2),
        "time_zone": "Europe/Berlin",
        "format_code": "online",
        "public_location": None,
        "capacity": 10,
        "decision_deadline": NOW + timedelta(days=7),
        "price_display_text": "Synthetic price",
        "updated_at": NOW,
    }


@pytest.mark.anyio
async def test_public_repository_maps_explicit_or_null_profile_without_internal_fields() -> None:
    engine = Engine([Result(rows=(public_row(None),))])
    repository = PostgresCalendarRepository(engine)

    items = await repository.list_public_offers(
        from_at=NOW,
        to_at=NOW + timedelta(days=30),
        topic_id=None,
        after_starts_at=None,
        after_offer_id=None,
        limit=51,
    )

    assert items[0].coach_profile_path is None
    assert not hasattr(items[0], "coach_id")
    assert engine.connection.calls[0][1]["limit"] == 51


@pytest.mark.anyio
async def test_public_repository_rejects_invalid_database_profile_path() -> None:
    engine = Engine([Result(row=public_row("https://attacker.example.invalid/"))])
    repository = PostgresCalendarRepository(engine)

    with pytest.raises(ValueError, match="public_profile_path"):
        await repository.get_public_offer(offer_id=OFFER_ID)


@pytest.mark.anyio
async def test_protected_topics_are_projected_as_controlled_id_and_name() -> None:
    engine = Engine([Result(rows=({"id": TOPIC_ID, "name": "Synthetic Topic"},))])
    repository = PostgresCalendarRepository(engine)

    topics = await repository.list_topics(
        actor_user_id=UUID("00000000-0000-4000-8000-000000000723"),
        allow_any_coach=False,
    )

    assert topics[0].id == TOPIC_ID
    assert topics[0].name == "Synthetic Topic"
    assert engine.connection.calls[0][1]["allow_any_coach"] is False


def test_projection_sql_is_fail_closed_and_audit_is_payload_free() -> None:
    public_list = str(_PUBLIC_OFFERS)
    public_detail = str(_PUBLIC_OFFER)
    protected_list = str(_VISIBLE_OFFERS)
    review_queue = str(_REVIEW_QUEUE)
    review_decision = str(_LATEST_REVIEW_DECISION)
    audit = str(_AUDIT)
    topics = str(_VISIBLE_TOPICS)

    for sql in (public_list, public_detail):
        assert "offer.lifecycle_status = 'active'" in sql
        assert "revision.workflow_status = 'published'" in sql
        assert "created_by_user_id" not in sql
        assert "review_threshold" not in sql
        assert "reviewer_user_id" not in sql
        assert "client_request_id" not in sql
    assert "coach.portal_user_id = :actor_user_id" in protected_list
    assert "coach.display_name AS coach_display_name" in protected_list
    assert "revision.workflow_status = 'in_review'" in review_queue
    assert "coach.display_name AS coach_display_name" in review_queue
    assert "coach.portal_user_id = :actor_user_id" in topics
    assert "coach.portal_user_id = :actor_user_id" in review_decision
    assert "payload" not in audit.casefold()
