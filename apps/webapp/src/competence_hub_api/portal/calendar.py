from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from competence_hub_api.auth.session_repository import SessionPrincipal

CALENDAR_FORMATS = frozenset({"online", "praesenz", "hybrid"})
CALENDAR_OWNER_ROLES = frozenset({"admin", "coach"})
CALENDAR_REVIEW_ROLES = frozenset({"admin", "calendar_reviewer"})


class CalendarAccessDeniedError(RuntimeError):
    pass


class CalendarOfferNotFoundError(RuntimeError):
    pass


class CalendarIdempotencyConflictError(RuntimeError):
    pass


class CalendarVersionConflictError(RuntimeError):
    pass


class CalendarTransitionConflictError(RuntimeError):
    pass


class CalendarTimeConflictError(RuntimeError):
    pass


class CalendarTopicUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class CalendarDraft:
    topic_id: UUID
    title: str
    summary: str | None
    starts_at: datetime
    ends_at: datetime
    time_zone: str
    format_code: str
    public_location: str | None
    capacity: int
    review_threshold: int
    decision_deadline: datetime
    price_display_text: str


@dataclass(frozen=True)
class CalendarOfferRecord:
    id: UUID
    coach_id: UUID
    created_by_user_id: UUID
    client_request_id: UUID
    lifecycle_status: str
    lock_version: int
    withdrawn_at: datetime | None
    created_at: datetime
    updated_at: datetime
    coach_display_name: str | None = None


@dataclass(frozen=True)
class CalendarRevisionRecord:
    id: UUID
    offer_id: UUID
    revision_number: int
    workflow_status: str
    draft: CalendarDraft
    created_by_user_id: UUID
    submitted_at: datetime | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    topic_name: str | None = None


@dataclass(frozen=True)
class CalendarOfferDetail:
    offer: CalendarOfferRecord
    current_revision: CalendarRevisionRecord
    published_revision: CalendarRevisionRecord | None


@dataclass(frozen=True)
class CalendarReviewDecision:
    outcome: str
    note: str | None
    decided_at: datetime


@dataclass(frozen=True)
class CalendarTopic:
    id: UUID
    name: str


@dataclass(frozen=True)
class PublicCalendarOffer:
    id: UUID
    coach_display_name: str
    coach_profile_path: str | None
    topic_id: UUID
    topic_name: str
    title: str
    summary: str | None
    starts_at: datetime
    ends_at: datetime
    time_zone: str
    format_code: str
    public_location: str | None
    capacity: int
    decision_deadline: datetime
    price_display_text: str
    updated_at: datetime


@dataclass(frozen=True)
class PublicCalendarPage:
    items: tuple[PublicCalendarOffer, ...]
    next_position: tuple[datetime, UUID] | None


class CalendarRepository(Protocol):
    async def list_topics(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
    ) -> tuple[CalendarTopic, ...]: ...

    async def create_offer(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        requested_coach_id: UUID | None,
        client_request_id: UUID,
        draft: CalendarDraft,
        now: datetime,
    ) -> CalendarOfferDetail: ...

    async def get_offer(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
    ) -> CalendarOfferDetail | None: ...

    async def list_offers(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        requested_coach_id: UUID | None,
        limit: int,
    ) -> tuple[CalendarOfferDetail, ...]: ...

    async def list_review_queue(
        self,
        *,
        limit: int,
    ) -> tuple[CalendarOfferDetail, ...]: ...

    async def get_review_decision(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
    ) -> CalendarReviewDecision | None: ...

    async def list_public_offers(
        self,
        *,
        from_at: datetime,
        to_at: datetime,
        topic_id: UUID | None,
        after_starts_at: datetime | None,
        after_offer_id: UUID | None,
        limit: int,
    ) -> tuple[PublicCalendarOffer, ...]: ...

    async def get_public_offer(
        self,
        *,
        offer_id: UUID,
    ) -> PublicCalendarOffer | None: ...

    async def update_draft(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
        expected_version: int,
        draft: CalendarDraft,
        now: datetime,
    ) -> CalendarOfferDetail: ...

    async def submit_offer(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
        expected_version: int,
        now: datetime,
    ) -> CalendarOfferDetail: ...

    async def review_offer(
        self,
        *,
        actor_user_id: UUID,
        offer_id: UUID,
        expected_version: int,
        outcome: str,
        note: str | None,
        now: datetime,
    ) -> CalendarOfferDetail: ...

    async def withdraw_offer(
        self,
        *,
        actor_user_id: UUID,
        allow_any_coach: bool,
        offer_id: UUID,
        expected_version: int,
        now: datetime,
    ) -> CalendarOfferDetail: ...


class CalendarService:
    def __init__(self, repository: CalendarRepository) -> None:
        self._repository = repository

    @staticmethod
    def capabilities(actor: SessionPrincipal) -> dict[str, bool]:
        roles = set(actor.roles)
        can_manage = bool(roles.intersection(CALENDAR_OWNER_ROLES))
        can_review = bool(roles.intersection(CALENDAR_REVIEW_ROLES))
        if not can_manage and not can_review:
            raise CalendarAccessDeniedError("calendar role required")
        return {
            "can_manage_own_offers": "coach" in roles,
            "can_review_offers": can_review,
            "can_administer_offers": "admin" in roles,
        }

    async def list_topics(
        self, *, actor: SessionPrincipal
    ) -> tuple[CalendarTopic, ...]:
        capabilities = self.capabilities(actor)
        return await self._repository.list_topics(
            actor_user_id=actor.user_id,
            allow_any_coach=capabilities["can_administer_offers"],
        )

    async def create_offer(
        self,
        *,
        actor: SessionPrincipal,
        coach_id: UUID | None,
        client_request_id: UUID,
        draft: CalendarDraft,
        now: datetime,
    ) -> CalendarOfferDetail:
        is_admin = _require_owner(actor)
        if coach_id is not None and not is_admin:
            raise CalendarAccessDeniedError("only admin may select a coach")
        if is_admin and coach_id is None and "coach" not in actor.roles:
            raise ValueError("coach_id is required for a non-coach admin")
        normalized = normalize_calendar_draft(draft, now=now)
        return await self._repository.create_offer(
            actor_user_id=actor.user_id,
            allow_any_coach=is_admin,
            requested_coach_id=coach_id,
            client_request_id=client_request_id,
            draft=normalized,
            now=now,
        )

    async def get_offer(
        self,
        *,
        actor: SessionPrincipal,
        offer_id: UUID,
    ) -> CalendarOfferDetail | None:
        allow_any = _require_calendar_reader(actor)
        return await self._repository.get_offer(
            actor_user_id=actor.user_id,
            allow_any_coach=allow_any,
            offer_id=offer_id,
        )

    async def list_offers(
        self,
        *,
        actor: SessionPrincipal,
        coach_id: UUID | None,
        limit: int,
    ) -> tuple[CalendarOfferDetail, ...]:
        is_admin = _require_owner(actor)
        if coach_id is not None and not is_admin:
            raise CalendarAccessDeniedError("only admin may filter by coach")
        _validate_limit(limit)
        return await self._repository.list_offers(
            actor_user_id=actor.user_id,
            allow_any_coach=is_admin,
            requested_coach_id=coach_id,
            limit=limit,
        )

    async def list_review_queue(
        self,
        *,
        actor: SessionPrincipal,
        limit: int,
    ) -> tuple[CalendarOfferDetail, ...]:
        _require_reviewer(actor)
        _validate_limit(limit)
        return await self._repository.list_review_queue(limit=limit)

    async def get_visible_review_decision(
        self,
        *,
        actor: SessionPrincipal,
        detail: CalendarOfferDetail,
    ) -> CalendarReviewDecision | None:
        roles = set(actor.roles)
        can_review = bool(roles.intersection(CALENDAR_REVIEW_ROLES))
        if not can_review and "coach" not in roles:
            raise CalendarAccessDeniedError("calendar role required")
        decision = await self._repository.get_review_decision(
            actor_user_id=actor.user_id,
            allow_any_coach=can_review,
            offer_id=detail.offer.id
        )
        if decision is None:
            return None
        if can_review or decision.outcome == "changes_requested":
            return decision
        return None

    async def list_public_offers(
        self,
        *,
        from_at: datetime,
        to_at: datetime,
        topic_id: UUID | None,
        after_starts_at: datetime | None,
        after_offer_id: UUID | None,
        limit: int,
        now: datetime,
    ) -> PublicCalendarPage:
        validate_public_calendar_window(from_at=from_at, to_at=to_at, now=now)
        _validate_limit(limit)
        if (after_starts_at is None) != (after_offer_id is None):
            raise ValueError("incomplete calendar cursor")
        if after_starts_at is not None:
            _validate_aware(after_starts_at, "cursor")
        rows = await self._repository.list_public_offers(
            from_at=from_at,
            to_at=to_at,
            topic_id=topic_id,
            after_starts_at=after_starts_at,
            after_offer_id=after_offer_id,
            limit=limit + 1,
        )
        items = rows[:limit]
        next_position = None
        if len(rows) > limit and items:
            last = items[-1]
            next_position = (last.starts_at, last.id)
        return PublicCalendarPage(items=items, next_position=next_position)

    async def get_public_offer(self, *, offer_id: UUID) -> PublicCalendarOffer | None:
        return await self._repository.get_public_offer(offer_id=offer_id)

    async def update_draft(
        self,
        *,
        actor: SessionPrincipal,
        offer_id: UUID,
        expected_version: int,
        draft: CalendarDraft,
        now: datetime,
    ) -> CalendarOfferDetail:
        is_admin = _require_owner(actor)
        _validate_version(expected_version)
        return await self._repository.update_draft(
            actor_user_id=actor.user_id,
            allow_any_coach=is_admin,
            offer_id=offer_id,
            expected_version=expected_version,
            draft=normalize_calendar_draft(draft, now=now),
            now=now,
        )

    async def submit_offer(
        self,
        *,
        actor: SessionPrincipal,
        offer_id: UUID,
        expected_version: int,
        now: datetime,
    ) -> CalendarOfferDetail:
        is_admin = _require_owner(actor)
        _validate_now(now)
        _validate_version(expected_version)
        return await self._repository.submit_offer(
            actor_user_id=actor.user_id,
            allow_any_coach=is_admin,
            offer_id=offer_id,
            expected_version=expected_version,
            now=now,
        )

    async def review_offer(
        self,
        *,
        actor: SessionPrincipal,
        offer_id: UUID,
        expected_version: int,
        outcome: str,
        note: str | None,
        now: datetime,
    ) -> CalendarOfferDetail:
        _require_reviewer(actor)
        _validate_now(now)
        _validate_version(expected_version)
        normalized_outcome = outcome.strip().lower()
        if normalized_outcome not in {"published", "changes_requested"}:
            raise ValueError("invalid review outcome")
        normalized_note = _optional_text(note, "note", 1000)
        if normalized_outcome == "changes_requested" and normalized_note is None:
            raise ValueError("a change request requires a note")
        return await self._repository.review_offer(
            actor_user_id=actor.user_id,
            offer_id=offer_id,
            expected_version=expected_version,
            outcome=normalized_outcome,
            note=normalized_note,
            now=now,
        )

    async def withdraw_offer(
        self,
        *,
        actor: SessionPrincipal,
        offer_id: UUID,
        expected_version: int,
        now: datetime,
    ) -> CalendarOfferDetail:
        roles = set(actor.roles)
        if not roles.intersection(CALENDAR_OWNER_ROLES | CALENDAR_REVIEW_ROLES):
            raise CalendarAccessDeniedError("calendar role required")
        _validate_now(now)
        _validate_version(expected_version)
        return await self._repository.withdraw_offer(
            actor_user_id=actor.user_id,
            allow_any_coach=bool(roles.intersection(CALENDAR_REVIEW_ROLES)),
            offer_id=offer_id,
            expected_version=expected_version,
            now=now,
        )


def normalize_calendar_draft(draft: CalendarDraft, *, now: datetime) -> CalendarDraft:
    _validate_now(now)
    for value, name in (
        (draft.starts_at, "starts_at"),
        (draft.ends_at, "ends_at"),
        (draft.decision_deadline, "decision_deadline"),
    ):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{name} must be timezone-aware")
    if draft.ends_at <= draft.starts_at:
        raise ValueError("ends_at must be after starts_at")
    if draft.decision_deadline < now or draft.decision_deadline >= draft.starts_at:
        raise ValueError("invalid decision_deadline")
    if draft.starts_at < now or draft.ends_at > _add_months(now, 3):
        raise ValueError("offer must be inside the rolling three-month window")
    time_zone = _required_text(draft.time_zone, "time_zone", 64)
    try:
        ZoneInfo(time_zone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("invalid time_zone") from exc
    format_code = draft.format_code.strip().lower()
    if format_code not in CALENDAR_FORMATS:
        raise ValueError("invalid format_code")
    location = _optional_text(draft.public_location, "public_location", 200)
    if format_code != "online" and location is None:
        raise ValueError("public_location is required for this format")
    if not 1 <= draft.capacity <= 500:
        raise ValueError("invalid capacity")
    if not 1 <= draft.review_threshold <= draft.capacity:
        raise ValueError("invalid review_threshold")
    return CalendarDraft(
        topic_id=draft.topic_id,
        title=_required_text(draft.title, "title", 160),
        summary=_optional_text(draft.summary, "summary", 1200),
        starts_at=draft.starts_at,
        ends_at=draft.ends_at,
        time_zone=time_zone,
        format_code=format_code,
        public_location=location,
        capacity=draft.capacity,
        review_threshold=draft.review_threshold,
        decision_deadline=draft.decision_deadline,
        price_display_text=_required_text(
            draft.price_display_text, "price_display_text", 200
        ),
    )


def validate_public_calendar_window(
    *, from_at: datetime, to_at: datetime, now: datetime
) -> None:
    _validate_now(now)
    _validate_aware(from_at, "from")
    _validate_aware(to_at, "to")
    if from_at < now or to_at <= from_at or to_at > _add_months(now, 3):
        raise ValueError("invalid public calendar window")


def _require_owner(actor: SessionPrincipal) -> bool:
    roles = set(actor.roles)
    if not roles.intersection(CALENDAR_OWNER_ROLES):
        raise CalendarAccessDeniedError("coach or admin role required")
    return "admin" in roles


def _require_reviewer(actor: SessionPrincipal) -> None:
    if not set(actor.roles).intersection(CALENDAR_REVIEW_ROLES):
        raise CalendarAccessDeniedError("calendar reviewer role required")


def _require_calendar_reader(actor: SessionPrincipal) -> bool:
    roles = set(actor.roles)
    if not roles.intersection(CALENDAR_OWNER_ROLES | CALENDAR_REVIEW_ROLES):
        raise CalendarAccessDeniedError("calendar role required")
    return bool(roles.intersection(CALENDAR_REVIEW_ROLES))


def _required_text(value: str, name: str, maximum: int) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > maximum:
        raise ValueError(f"invalid {name}")
    return normalized


def _optional_text(value: str | None, name: str, maximum: int) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > maximum:
        raise ValueError(f"invalid {name}")
    return normalized


def _validate_now(now: datetime) -> None:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")


def _validate_version(version: int) -> None:
    if version < 1:
        raise ValueError("expected_version must be positive")


def _validate_limit(limit: int) -> None:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")


def _validate_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


def _add_months(value: datetime, months: int) -> datetime:
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    day = value.day
    while day > 28:
        try:
            return value.replace(year=year, month=month, day=day)
        except ValueError:
            day -= 1
    return value.replace(year=year, month=month, day=day)
