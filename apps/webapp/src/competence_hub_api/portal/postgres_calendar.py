from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from competence_hub_api.portal.calendar import (
    CalendarDraft,
    CalendarIdempotencyConflictError,
    CalendarOfferDetail,
    CalendarOfferNotFoundError,
    CalendarOfferRecord,
    CalendarRevisionRecord,
    CalendarTimeConflictError,
    CalendarTopicUnavailableError,
    CalendarTransitionConflictError,
    CalendarVersionConflictError,
    normalize_calendar_draft,
)

_CREATE_REQUEST_LOCK = text(
    """
    SELECT pg_advisory_xact_lock(
        hashtext(
            CAST(CAST(:actor_user_id AS uuid) AS text)
            || ':' ||
            CAST(CAST(:client_request_id AS uuid) AS text)
        )
    )
    """
)

_RESOLVE_CREATE_COACH = text(
    """
    SELECT id
    FROM competence_hub.coaches
    WHERE (
        :allow_any_coach
        AND CAST(:requested_coach_id AS uuid) IS NOT NULL
        AND id = CAST(:requested_coach_id AS uuid)
    ) OR (
        CAST(:requested_coach_id AS uuid) IS NULL
        AND portal_user_id = :actor_user_id
    )
    FOR UPDATE
    """
)

_FIND_IDEMPOTENT_OFFER = text(
    """
    SELECT id
    FROM competence_hub.calendar_offers
    WHERE created_by_user_id = :actor_user_id
      AND client_request_id = :client_request_id
    """
)

_CREATE_OFFER = text(
    """
    INSERT INTO competence_hub.calendar_offers (
        coach_id, created_by_user_id, client_request_id, created_at, updated_at
    ) VALUES (
        :coach_id, :actor_user_id, :client_request_id, :now, :now
    )
    RETURNING id
    """
)

_INSERT_REVISION = text(
    """
    INSERT INTO competence_hub.calendar_offer_revisions (
        offer_id, revision_number, workflow_status, topic_id, title, summary,
        starts_at, ends_at, time_zone, format_code, public_location, capacity,
        review_threshold, decision_deadline, price_display_text,
        created_by_user_id, submitted_at, published_at, created_at, updated_at
    ) VALUES (
        :offer_id, :revision_number, :workflow_status, :topic_id, :title, :summary,
        :starts_at, :ends_at, :time_zone, :format_code, :public_location, :capacity,
        :review_threshold, :decision_deadline, :price_display_text,
        :actor_user_id, :submitted_at, :published_at, :now, :now
    )
    RETURNING id
    """
)

_VISIBLE_OFFER = text(
    """
    SELECT
        offer.id, offer.coach_id, offer.created_by_user_id,
        offer.client_request_id, offer.lifecycle_status, offer.lock_version,
        offer.withdrawn_at, offer.created_at, offer.updated_at
    FROM competence_hub.calendar_offers AS offer
    JOIN competence_hub.coaches AS coach ON coach.id = offer.coach_id
    WHERE offer.id = :offer_id
      AND (:allow_any_coach OR coach.portal_user_id = :actor_user_id)
    """
)

_LOCK_VISIBLE_OFFER = text(str(_VISIBLE_OFFER) + " FOR UPDATE OF offer")

_OFFER_BY_ID = text(
    """
    SELECT
        id, coach_id, created_by_user_id, client_request_id, lifecycle_status,
        lock_version, withdrawn_at, created_at, updated_at
    FROM competence_hub.calendar_offers
    WHERE id = :offer_id
    """
)

_LATEST_REVISION = text(
    """
    SELECT *
    FROM competence_hub.calendar_offer_revisions
    WHERE offer_id = :offer_id
    ORDER BY revision_number DESC
    LIMIT 1
    """
)

_PUBLISHED_REVISION = text(
    """
    SELECT *
    FROM competence_hub.calendar_offer_revisions
    WHERE offer_id = :offer_id
      AND workflow_status = 'published'
    LIMIT 1
    """
)

_TOPIC_AVAILABLE = text(
    """
    SELECT EXISTS (
        SELECT 1
        FROM competence_hub.topics AS topic
        JOIN competence_hub.coach_topics AS coach_topic
          ON coach_topic.topic_id = topic.id
        WHERE topic.id = :topic_id
          AND topic.active
          AND coach_topic.coach_id = :coach_id
    )
    """
)

_UPDATE_DRAFT = text(
    """
    UPDATE competence_hub.calendar_offer_revisions
    SET topic_id = :topic_id, title = :title, summary = :summary,
        starts_at = :starts_at, ends_at = :ends_at, time_zone = :time_zone,
        format_code = :format_code, public_location = :public_location,
        capacity = :capacity, review_threshold = :review_threshold,
        decision_deadline = :decision_deadline,
        price_display_text = :price_display_text, updated_at = :now
    WHERE id = :revision_id AND workflow_status = 'draft'
    """
)

_SUPERSEDE_REVISION = text(
    """
    UPDATE competence_hub.calendar_offer_revisions
    SET workflow_status = 'superseded', updated_at = :now
    WHERE id = :revision_id
    """
)

_SUBMIT_REVISION = text(
    """
    UPDATE competence_hub.calendar_offer_revisions
    SET workflow_status = 'in_review', submitted_at = :now, updated_at = :now
    WHERE id = :revision_id AND workflow_status = 'draft'
    """
)

_REQUEST_CHANGES = text(
    """
    UPDATE competence_hub.calendar_offer_revisions
    SET workflow_status = 'changes_requested', updated_at = :now
    WHERE id = :revision_id AND workflow_status = 'in_review'
    """
)

_PUBLISH_REVISION = text(
    """
    UPDATE competence_hub.calendar_offer_revisions
    SET workflow_status = 'published', published_at = :now, updated_at = :now
    WHERE id = :revision_id AND workflow_status = 'in_review'
    """
)

_SUPERSEDE_PRIOR_PUBLICATION = text(
    """
    UPDATE competence_hub.calendar_offer_revisions
    SET workflow_status = 'superseded', updated_at = :now
    WHERE offer_id = :offer_id
      AND workflow_status = 'published'
      AND id <> :revision_id
    """
)

_LOCK_COACH = text(
    "SELECT id FROM competence_hub.coaches WHERE id = :coach_id FOR UPDATE"
)

_OVERLAP_EXISTS = text(
    """
    SELECT EXISTS (
        SELECT 1
        FROM competence_hub.calendar_offer_revisions AS revision
        JOIN competence_hub.calendar_offers AS offer ON offer.id = revision.offer_id
        WHERE offer.coach_id = :coach_id
          AND offer.lifecycle_status = 'active'
          AND offer.id <> :offer_id
          AND revision.workflow_status IN ('in_review', 'published')
          AND revision.starts_at < :ends_at
          AND revision.ends_at > :starts_at
    )
    """
)

_INSERT_DECISION = text(
    """
    INSERT INTO competence_hub.calendar_review_decisions (
        revision_id, reviewer_user_id, outcome, note, decided_at
    ) VALUES (
        :revision_id, :actor_user_id, :outcome, :note, :now
    )
    """
)

_DECISION_OUTCOME = text(
    """
    SELECT outcome
    FROM competence_hub.calendar_review_decisions
    WHERE revision_id = :revision_id
      AND reviewer_user_id = :actor_user_id
    """
)

_BUMP_VERSION = text(
    """
    UPDATE competence_hub.calendar_offers
    SET lock_version = lock_version + 1, updated_at = :now
    WHERE id = :offer_id
    """
)

_WITHDRAW_OFFER = text(
    """
    UPDATE competence_hub.calendar_offers
    SET lifecycle_status = 'withdrawn', withdrawn_at = :now,
        lock_version = lock_version + 1, updated_at = :now
    WHERE id = :offer_id AND lifecycle_status = 'active'
    """
)

_AUDIT = text(
    """
    INSERT INTO competence_hub.audit_events (
        actor_user_id, occurred_at, action, entity_type, entity_id, outcome
    ) VALUES (
        :actor_user_id, :now, :action, 'calendar_offer', :offer_id, 'success'
    )
    """
)


class PostgresCalendarRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create_offer(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        requested_coach_id: UUID | None,
        client_request_id: UUID,
        draft: CalendarDraft,
        now: datetime,
    ) -> CalendarOfferDetail:
        async with self._engine.begin() as connection:
            await connection.execute(
                _CREATE_REQUEST_LOCK,
                {
                    "actor_user_id": actor_user_id,
                    "client_request_id": client_request_id,
                },
            )
            existing = await connection.scalar(
                _FIND_IDEMPOTENT_OFFER,
                {
                    "actor_user_id": actor_user_id,
                    "client_request_id": client_request_id,
                },
            )
            if existing is not None:
                detail = await _load_detail(connection, existing)
                same_coach = (
                    requested_coach_id is None
                    or detail.offer.coach_id == requested_coach_id
                )
                if same_coach and _same_draft(detail.current_revision.draft, draft):
                    return detail
                raise CalendarIdempotencyConflictError(
                    "client_request_id was already used with different content"
                )

            coach_id = await connection.scalar(
                _RESOLVE_CREATE_COACH,
                {
                    "actor_user_id": actor_user_id,
                    "allow_any_coach": allow_any_coach,
                    "requested_coach_id": requested_coach_id,
                },
            )
            if coach_id is None:
                raise CalendarOfferNotFoundError("coach is unavailable")
            await _require_topic(connection, coach_id=coach_id, topic_id=draft.topic_id)
            offer_id = await connection.scalar(
                _CREATE_OFFER,
                {
                    "coach_id": coach_id,
                    "actor_user_id": actor_user_id,
                    "client_request_id": client_request_id,
                    "now": now,
                },
            )
            await connection.execute(
                _INSERT_REVISION,
                _revision_parameters(
                    offer_id=offer_id,
                    revision_number=1,
                    workflow_status="draft",
                    draft=draft,
                    actor_user_id=actor_user_id,
                    now=now,
                ),
            )
            await _write_audit(
                connection,
                actor_user_id=actor_user_id,
                offer_id=offer_id,
                action="calendar.offer.created",
                now=now,
            )
            return await _load_detail(connection, offer_id)

    async def get_offer(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
    ) -> CalendarOfferDetail | None:
        async with self._engine.connect() as connection:
            row = (
                await connection.execute(
                    _VISIBLE_OFFER,
                    {
                        "actor_user_id": actor_user_id,
                        "allow_any_coach": allow_any_coach,
                        "offer_id": offer_id,
                    },
                )
            ).mappings().one_or_none()
            if row is None:
                return None
            return await _load_detail(connection, offer_id, offer_row=row)

    async def update_draft(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
        expected_version: int,
        draft: CalendarDraft,
        now: datetime,
    ) -> CalendarOfferDetail:
        async with self._engine.begin() as connection:
            detail = await _lock_detail(
                connection, actor_user_id, allow_any_coach, offer_id
            )
            if detail.offer.lock_version != expected_version:
                if (
                    detail.offer.lock_version == expected_version + 1
                    and detail.current_revision.workflow_status == "draft"
                    and _same_draft(detail.current_revision.draft, draft)
                ):
                    return detail
                raise CalendarVersionConflictError("stale calendar offer version")
            _require_active(detail)
            current = detail.current_revision
            if current.workflow_status not in {
                "draft",
                "changes_requested",
                "published",
            }:
                raise CalendarTransitionConflictError("offer cannot be edited")
            await _require_topic(
                connection,
                coach_id=detail.offer.coach_id,
                topic_id=draft.topic_id,
            )
            if current.workflow_status == "draft":
                await connection.execute(
                    _UPDATE_DRAFT,
                    {
                        **_draft_parameters(draft),
                        "revision_id": current.id,
                        "now": now,
                    },
                )
            else:
                if current.workflow_status == "changes_requested":
                    await connection.execute(
                        _SUPERSEDE_REVISION,
                        {"revision_id": current.id, "now": now},
                    )
                await connection.execute(
                    _INSERT_REVISION,
                    _revision_parameters(
                        offer_id=offer_id,
                        revision_number=current.revision_number + 1,
                        workflow_status="draft",
                        draft=draft,
                        actor_user_id=actor_user_id,
                        now=now,
                    ),
                )
            await _bump_and_audit(
                connection,
                actor_user_id=actor_user_id,
                offer_id=offer_id,
                action="calendar.offer.draft_updated",
                now=now,
            )
            return await _load_detail(connection, offer_id)

    async def submit_offer(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
        expected_version: int,
        now: datetime,
    ) -> CalendarOfferDetail:
        async with self._engine.begin() as connection:
            detail = await _lock_detail(
                connection, actor_user_id, allow_any_coach, offer_id
            )
            if detail.offer.lock_version != expected_version:
                if (
                    detail.offer.lock_version == expected_version + 1
                    and detail.current_revision.workflow_status == "in_review"
                ):
                    return detail
                raise CalendarVersionConflictError("stale calendar offer version")
            _require_active(detail)
            revision = detail.current_revision
            if revision.workflow_status != "draft":
                raise CalendarTransitionConflictError("only a draft may be submitted")
            normalize_calendar_draft(revision.draft, now=now)
            await _require_topic(
                connection,
                coach_id=detail.offer.coach_id,
                topic_id=revision.draft.topic_id,
            )
            await _lock_coach_and_reject_overlap(connection, detail)
            await connection.execute(
                _SUBMIT_REVISION,
                {"revision_id": revision.id, "now": now},
            )
            await _bump_and_audit(
                connection,
                actor_user_id=actor_user_id,
                offer_id=offer_id,
                action="calendar.offer.submitted",
                now=now,
            )
            return await _load_detail(connection, offer_id)

    async def review_offer(
        self,
        *,
        actor_user_id: UUID,
        offer_id: UUID,
        expected_version: int,
        outcome: str,
        note: str | None,
        now: datetime,
    ) -> CalendarOfferDetail:
        async with self._engine.begin() as connection:
            detail = await _lock_detail(connection, actor_user_id, True, offer_id)
            if detail.offer.lock_version != expected_version:
                if (
                    detail.offer.lock_version == expected_version + 1
                    and detail.current_revision.workflow_status == outcome
                ):
                    prior_outcome = await connection.scalar(
                        _DECISION_OUTCOME,
                        {
                            "revision_id": detail.current_revision.id,
                            "actor_user_id": actor_user_id,
                        },
                    )
                    if prior_outcome == outcome:
                        return detail
                raise CalendarVersionConflictError("stale calendar offer version")
            _require_active(detail)
            revision = detail.current_revision
            if revision.workflow_status != "in_review":
                raise CalendarTransitionConflictError("offer is not in review")
            if outcome == "published":
                normalize_calendar_draft(revision.draft, now=now)
                await _require_topic(
                    connection,
                    coach_id=detail.offer.coach_id,
                    topic_id=revision.draft.topic_id,
                )
                await _lock_coach_and_reject_overlap(connection, detail)
                await connection.execute(
                    _SUPERSEDE_PRIOR_PUBLICATION,
                    {"offer_id": offer_id, "revision_id": revision.id, "now": now},
                )
                await connection.execute(
                    _PUBLISH_REVISION,
                    {"revision_id": revision.id, "now": now},
                )
                action = "calendar.offer.published"
            else:
                await connection.execute(
                    _REQUEST_CHANGES,
                    {"revision_id": revision.id, "now": now},
                )
                action = "calendar.offer.changes_requested"
            await connection.execute(
                _INSERT_DECISION,
                {
                    "revision_id": revision.id,
                    "actor_user_id": actor_user_id,
                    "outcome": outcome,
                    "note": note,
                    "now": now,
                },
            )
            await _bump_and_audit(
                connection,
                actor_user_id=actor_user_id,
                offer_id=offer_id,
                action=action,
                now=now,
            )
            return await _load_detail(connection, offer_id)

    async def withdraw_offer(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
        expected_version: int,
        now: datetime,
    ) -> CalendarOfferDetail:
        async with self._engine.begin() as connection:
            detail = await _lock_detail(
                connection, actor_user_id, allow_any_coach, offer_id
            )
            if detail.offer.lock_version != expected_version:
                if (
                    detail.offer.lock_version == expected_version + 1
                    and detail.offer.lifecycle_status == "withdrawn"
                ):
                    return detail
                raise CalendarVersionConflictError("stale calendar offer version")
            _require_active(detail)
            await connection.execute(
                _WITHDRAW_OFFER,
                {"offer_id": offer_id, "now": now},
            )
            await _write_audit(
                connection,
                actor_user_id=actor_user_id,
                offer_id=offer_id,
                action="calendar.offer.withdrawn",
                now=now,
            )
            return await _load_detail(connection, offer_id)


async def _lock_detail(
    connection: AsyncConnection,
    actor_user_id: UUID,
    allow_any_coach: bool,
    offer_id: UUID,
) -> CalendarOfferDetail:
    row = (
        await connection.execute(
            _LOCK_VISIBLE_OFFER,
            {
                "actor_user_id": actor_user_id,
                "allow_any_coach": allow_any_coach,
                "offer_id": offer_id,
            },
        )
    ).mappings().one_or_none()
    if row is None:
        raise CalendarOfferNotFoundError("calendar offer was not found")
    return await _load_detail(connection, offer_id, offer_row=row)


async def _load_detail(
    connection: AsyncConnection,
    offer_id: UUID,
    *,
    offer_row: Mapping[str, object] | None = None,
) -> CalendarOfferDetail:
    if offer_row is None:
        offer_row = (
            await connection.execute(_OFFER_BY_ID, {"offer_id": offer_id})
        ).mappings().one()
    current_row = (
        await connection.execute(_LATEST_REVISION, {"offer_id": offer_id})
    ).mappings().one()
    published_row = (
        await connection.execute(_PUBLISHED_REVISION, {"offer_id": offer_id})
    ).mappings().one_or_none()
    return CalendarOfferDetail(
        offer=_offer(offer_row),
        current_revision=_revision(current_row),
        published_revision=(
            _revision(published_row) if published_row is not None else None
        ),
    )


async def _require_topic(
    connection: AsyncConnection, *, coach_id: UUID, topic_id: UUID
) -> None:
    available = await connection.scalar(
        _TOPIC_AVAILABLE,
        {"coach_id": coach_id, "topic_id": topic_id},
    )
    if not available:
        raise CalendarTopicUnavailableError("topic is unavailable for this coach")


async def _lock_coach_and_reject_overlap(
    connection: AsyncConnection, detail: CalendarOfferDetail
) -> None:
    await connection.execute(_LOCK_COACH, {"coach_id": detail.offer.coach_id})
    draft = detail.current_revision.draft
    overlap = await connection.scalar(
        _OVERLAP_EXISTS,
        {
            "coach_id": detail.offer.coach_id,
            "offer_id": detail.offer.id,
            "starts_at": draft.starts_at,
            "ends_at": draft.ends_at,
        },
    )
    if overlap:
        raise CalendarTimeConflictError("calendar offer overlaps another offer")


async def _bump_and_audit(
    connection: AsyncConnection,
    *,
    actor_user_id: UUID,
    offer_id: UUID,
    action: str,
    now: datetime,
) -> None:
    await connection.execute(_BUMP_VERSION, {"offer_id": offer_id, "now": now})
    await _write_audit(
        connection,
        actor_user_id=actor_user_id,
        offer_id=offer_id,
        action=action,
        now=now,
    )


async def _write_audit(
    connection: AsyncConnection,
    *,
    actor_user_id: UUID,
    offer_id: UUID,
    action: str,
    now: datetime,
) -> None:
    await connection.execute(
        _AUDIT,
        {
            "actor_user_id": actor_user_id,
            "offer_id": offer_id,
            "action": action,
            "now": now,
        },
    )


def _require_active(detail: CalendarOfferDetail) -> None:
    if detail.offer.lifecycle_status != "active":
        raise CalendarTransitionConflictError("calendar offer is withdrawn")


def _draft_parameters(draft: CalendarDraft) -> dict[str, object]:
    return {
        "topic_id": draft.topic_id,
        "title": draft.title,
        "summary": draft.summary,
        "starts_at": draft.starts_at,
        "ends_at": draft.ends_at,
        "time_zone": draft.time_zone,
        "format_code": draft.format_code,
        "public_location": draft.public_location,
        "capacity": draft.capacity,
        "review_threshold": draft.review_threshold,
        "decision_deadline": draft.decision_deadline,
        "price_display_text": draft.price_display_text,
    }


def _revision_parameters(
    *,
    offer_id: UUID,
    revision_number: int,
    workflow_status: str,
    draft: CalendarDraft,
    actor_user_id: UUID,
    now: datetime,
) -> dict[str, object]:
    return {
        **_draft_parameters(draft),
        "offer_id": offer_id,
        "revision_number": revision_number,
        "workflow_status": workflow_status,
        "actor_user_id": actor_user_id,
        "submitted_at": None,
        "published_at": None,
        "now": now,
    }


def _offer(row: Mapping[str, object]) -> CalendarOfferRecord:
    return CalendarOfferRecord(
        id=row["id"],
        coach_id=row["coach_id"],
        created_by_user_id=row["created_by_user_id"],
        client_request_id=row["client_request_id"],
        lifecycle_status=row["lifecycle_status"],
        lock_version=row["lock_version"],
        withdrawn_at=row["withdrawn_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _revision(row: Mapping[str, object]) -> CalendarRevisionRecord:
    return CalendarRevisionRecord(
        id=row["id"],
        offer_id=row["offer_id"],
        revision_number=row["revision_number"],
        workflow_status=row["workflow_status"],
        draft=CalendarDraft(
            topic_id=row["topic_id"],
            title=row["title"],
            summary=row["summary"],
            starts_at=row["starts_at"],
            ends_at=row["ends_at"],
            time_zone=row["time_zone"],
            format_code=row["format_code"],
            public_location=row["public_location"],
            capacity=row["capacity"],
            review_threshold=row["review_threshold"],
            decision_deadline=row["decision_deadline"],
            price_display_text=row["price_display_text"],
        ),
        created_by_user_id=row["created_by_user_id"],
        submitted_at=row["submitted_at"],
        published_at=row["published_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _same_draft(left: CalendarDraft, right: CalendarDraft) -> bool:
    return left == right
