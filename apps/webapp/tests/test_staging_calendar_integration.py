import asyncio
from datetime import UTC, datetime, timedelta
import os
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.portal.calendar import CalendarDraft, CalendarTimeConflictError
from competence_hub_api.portal.postgres_calendar import PostgresCalendarRepository

APP_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_APP_DATABASE_URL"
MIGRATOR_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL"

pytestmark = [pytest.mark.anyio, pytest.mark.staging_integration]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _required_database_urls() -> tuple[str, str]:
    app_url = os.environ.get(APP_DATABASE_URL_ENV, "")
    migrator_url = os.environ.get(MIGRATOR_DATABASE_URL_ENV, "")
    if not app_url or not migrator_url:
        pytest.skip(
            "isolated staging URLs were not supplied through the process environment"
        )
    return app_url, migrator_url


def _draft(topic_id: UUID, *, start: datetime, title: str) -> CalendarDraft:
    return CalendarDraft(
        topic_id=topic_id,
        title=title,
        summary="Synthetic calendar integration data only",
        starts_at=start,
        ends_at=start + timedelta(hours=2),
        time_zone="Europe/Berlin",
        format_code="praesenz",
        public_location="Synthetic location",
        capacity=30,
        review_threshold=10,
        decision_deadline=start - timedelta(days=2),
        price_display_text="Synthetic price",
    )


@pytest.mark.anyio
async def test_staging_calendar_concurrency_revisions_audit_and_zero_residue() -> None:
    app_url, migrator_url = _required_database_urls()
    app_engine = create_async_engine(app_url, pool_pre_ping=True, hide_parameters=True)
    admin_engine = create_async_engine(
        migrator_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    repository = PostgresCalendarRepository(app_engine)
    coach_user_id = uuid4()
    reviewer_user_id = uuid4()
    foreign_user_id = uuid4()
    coach_id = uuid4()
    topic_id = uuid4()
    offer_ids: list[UUID] = []
    operation_time: datetime | None = None

    try:
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            database_time = await connection.scalar(text("SELECT clock_timestamp()"))
            assert isinstance(database_time, datetime)
            operation_time = database_time.astimezone(UTC) - timedelta(minutes=5)
            for user_id, label in (
                (coach_user_id, "Coach"),
                (reviewer_user_id, "Reviewer"),
                (foreign_user_id, "Foreign"),
            ):
                await connection.execute(
                    text(
                        """
                        INSERT INTO competence_hub.portal_users (
                            id, display_name, email, active
                        ) VALUES (:id, :label, :email, true)
                        """
                    ),
                    {
                        "id": user_id,
                        "label": f"Synthetic Calendar {label}",
                        "email": f"synthetic-calendar-{user_id.hex}@example.invalid",
                    },
                )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.coaches (
                        id, portal_user_id, display_name, public_profile_status
                    ) VALUES (:coach_id, :user_id, 'Synthetic Coach', 'draft')
                    """
                ),
                {"coach_id": coach_id, "user_id": coach_user_id},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.topics (id, name, active)
                    VALUES (:topic_id, :name, true)
                    """
                ),
                {"topic_id": topic_id, "name": f"Synthetic {uuid4().hex}"},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.coach_topics (coach_id, topic_id)
                    VALUES (:coach_id, :topic_id)
                    """
                ),
                {"coach_id": coach_id, "topic_id": topic_id},
            )

        assert operation_time is not None
        start = operation_time + timedelta(days=20)
        first = await repository.create_offer(
            actor_user_id=coach_user_id,
            allow_any_coach=False,
            requested_coach_id=None,
            client_request_id=uuid4(),
            draft=_draft(topic_id, start=start, title="Synthetic A"),
            now=operation_time,
        )
        offer_ids.append(first.offer.id)
        second = await repository.create_offer(
            actor_user_id=coach_user_id,
            allow_any_coach=False,
            requested_coach_id=None,
            client_request_id=uuid4(),
            draft=_draft(
                topic_id,
                start=start + timedelta(minutes=30),
                title="Synthetic B",
            ),
            now=operation_time,
        )
        offer_ids.append(second.offer.id)

        results = await asyncio.gather(
            repository.submit_offer(
                actor_user_id=coach_user_id,
                allow_any_coach=False,
                offer_id=first.offer.id,
                expected_version=1,
                now=operation_time,
            ),
            repository.submit_offer(
                actor_user_id=coach_user_id,
                allow_any_coach=False,
                offer_id=second.offer.id,
                expected_version=1,
                now=operation_time,
            ),
            return_exceptions=True,
        )
        successes = [item for item in results if not isinstance(item, Exception)]
        conflicts = [item for item in results if isinstance(item, CalendarTimeConflictError)]
        if len(successes) != 1 or len(conflicts) != 1:
            outcomes = " | ".join(
                (
                    type(item).__name__
                    if not isinstance(item, Exception)
                    else f"{type(item).__name__}: {item}"
                )
                for item in results
            )
            pytest.fail(f"unexpected concurrent submit outcomes: {outcomes}")

        submitted = successes[0]
        assert submitted.current_revision.workflow_status == "in_review"
        published = await repository.review_offer(
            actor_user_id=reviewer_user_id,
            offer_id=submitted.offer.id,
            expected_version=2,
            outcome="published",
            note=None,
            now=operation_time + timedelta(minutes=1),
        )
        assert published.current_revision.workflow_status == "published"
        assert published.published_revision is not None

        revised = await repository.update_draft(
            actor_user_id=coach_user_id,
            allow_any_coach=False,
            offer_id=published.offer.id,
            expected_version=3,
            draft=_draft(topic_id, start=start, title="Synthetic A revised"),
            now=operation_time + timedelta(minutes=2),
        )
        assert revised.current_revision.revision_number == 2
        assert revised.current_revision.workflow_status == "draft"
        assert revised.published_revision is not None
        assert revised.published_revision.revision_number == 1

        foreign = await repository.get_offer(
            actor_user_id=foreign_user_id,
            allow_any_coach=False,
            offer_id=published.offer.id,
        )
        assert foreign is None

        async with admin_engine.connect() as connection:
            audit_actions = tuple(
                (
                    await connection.execute(
                        text(
                            """
                            SELECT action
                            FROM competence_hub.audit_events
                            WHERE actor_user_id IN (:coach_user_id, :reviewer_user_id)
                              AND entity_id = ANY(:offer_ids)
                            ORDER BY id
                            """
                        ),
                        {
                            "coach_user_id": coach_user_id,
                            "reviewer_user_id": reviewer_user_id,
                            "offer_ids": offer_ids,
                        },
                    )
                ).scalars()
            )
        assert "calendar.offer.submitted" in audit_actions
        assert "calendar.offer.published" in audit_actions
        assert "calendar.offer.draft_updated" in audit_actions
    finally:
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await connection.execute(
                text(
                    "DELETE FROM competence_hub.audit_events "
                    "WHERE actor_user_id IN (:coach, :reviewer, :foreign)"
                ),
                {
                    "coach": coach_user_id,
                    "reviewer": reviewer_user_id,
                    "foreign": foreign_user_id,
                },
            )
            if offer_ids:
                await connection.execute(
                    text(
                        "DELETE FROM competence_hub.calendar_review_decisions "
                        "WHERE revision_id IN (SELECT id FROM "
                        "competence_hub.calendar_offer_revisions "
                        "WHERE offer_id = ANY(:offer_ids))"
                    ),
                    {"offer_ids": offer_ids},
                )
                await connection.execute(
                    text(
                        "DELETE FROM competence_hub.calendar_offer_revisions "
                        "WHERE offer_id = ANY(:offer_ids)"
                    ),
                    {"offer_ids": offer_ids},
                )
                await connection.execute(
                    text(
                        "DELETE FROM competence_hub.calendar_offers "
                        "WHERE id = ANY(:offer_ids)"
                    ),
                    {"offer_ids": offer_ids},
                )
            await connection.execute(
                text(
                    "DELETE FROM competence_hub.coach_topics "
                    "WHERE coach_id = :coach_id"
                ),
                {"coach_id": coach_id},
            )
            await connection.execute(
                text("DELETE FROM competence_hub.topics WHERE id = :topic_id"),
                {"topic_id": topic_id},
            )
            await connection.execute(
                text("DELETE FROM competence_hub.coaches WHERE id = :coach_id"),
                {"coach_id": coach_id},
            )
            await connection.execute(
                text(
                    "DELETE FROM competence_hub.portal_users "
                    "WHERE id IN (:coach, :reviewer, :foreign)"
                ),
                {
                    "coach": coach_user_id,
                    "reviewer": reviewer_user_id,
                    "foreign": foreign_user_id,
                },
            )
        async with admin_engine.connect() as connection:
            residue = await connection.scalar(
                text(
                    """
                    SELECT
                        (SELECT count(*) FROM competence_hub.portal_users
                         WHERE id IN (:coach, :reviewer, :foreign))
                      + (SELECT count(*) FROM competence_hub.coaches
                         WHERE id = :coach_id)
                      + (SELECT count(*) FROM competence_hub.topics
                         WHERE id = :topic_id)
                      + (SELECT count(*) FROM competence_hub.audit_events
                         WHERE actor_user_id IN (:coach, :reviewer, :foreign))
                    """
                ),
                {
                    "coach": coach_user_id,
                    "reviewer": reviewer_user_id,
                    "foreign": foreign_user_id,
                    "coach_id": coach_id,
                    "topic_id": topic_id,
                },
            )
            assert residue == 0
        await app_engine.dispose()
        await admin_engine.dispose()
