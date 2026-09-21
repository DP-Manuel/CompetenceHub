import hmac
import re
from datetime import datetime
from typing import TypeVar
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.portal.calendar import (
    CalendarAccessDeniedError,
    CalendarDraft,
    CalendarIdempotencyConflictError,
    CalendarOfferDetail,
    CalendarOfferNotFoundError,
    CalendarReviewDecision,
    CalendarService,
    CalendarTimeConflictError,
    CalendarTopicUnavailableError,
    CalendarTransitionConflictError,
    CalendarVersionConflictError,
    PublicCalendarOffer,
)
from competence_hub_api.security.calendar_cursor import CalendarCursorCodec
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token
from competence_hub_api.web.problems import problem_response

public_router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])
protected_router = APIRouter(
    prefix="/api/v1/portal/calendar", tags=["portal-calendar"]
)
MAX_PORTAL_REQUEST_BYTES = 32 * 1024
_ETAG = re.compile(r'"v([1-9][0-9]*)"', flags=re.ASCII)


class CalendarDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic_id: UUID
    title: str = Field(min_length=1, max_length=160)
    summary: str | None = Field(default=None, max_length=1200)
    starts_at: datetime
    ends_at: datetime
    time_zone: str = Field(min_length=1, max_length=64)
    format: str = Field(min_length=1, max_length=20)
    public_location: str | None = Field(default=None, max_length=200)
    capacity: int = Field(ge=1, le=500)
    review_threshold: int = Field(ge=1, le=500)
    decision_deadline: datetime
    price_display_text: str = Field(min_length=1, max_length=200)


class CalendarCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_request_id: UUID
    coach_id: UUID | None = None
    draft: CalendarDraftRequest


class CalendarReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: str = Field(min_length=1, max_length=32)
    note: str | None = Field(default=None, max_length=1000)


RequestModel = TypeVar("RequestModel", bound=BaseModel)


@public_router.get("/offers")
async def list_public_offers(
    request: Request,
    from_at: datetime = Query(alias="from"),
    to_at: datetime = Query(alias="to"),
    topic_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, max_length=1024),
) -> Response:
    context = _public_context(request)
    if isinstance(context, Response):
        return context
    service, codec = context
    try:
        after_starts_at, after_offer_id = (
            codec.decode(cursor) if cursor is not None else (None, None)
        )
        page = await service.list_public_offers(
            from_at=from_at,
            to_at=to_at,
            topic_id=topic_id,
            after_starts_at=after_starts_at,
            after_offer_id=after_offer_id,
            limit=limit,
            now=request.app.state.clock(),
        )
        next_cursor = (
            codec.encode(*page.next_position) if page.next_position is not None else None
        )
    except ValueError:
        return _invalid_request()
    return JSONResponse(
        jsonable_encoder(
            {"items": [_public_offer(item) for item in page.items], "next_cursor": next_cursor}
        )
    )


@public_router.get("/offers/{offer_id}")
async def get_public_offer(offer_id: UUID, request: Request) -> Response:
    context = _public_context(request)
    if isinstance(context, Response):
        return context
    service, _ = context
    result = await service.get_public_offer(offer_id=offer_id)
    if result is None:
        return _not_found()
    return JSONResponse(jsonable_encoder(_public_offer(result)))


@protected_router.get("/offers")
async def list_protected_offers(
    request: Request,
    coach_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
) -> Response:
    context = await _protected_context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    actor, service = context
    try:
        items = await service.list_offers(actor=actor, coach_id=coach_id, limit=limit)
    except CalendarAccessDeniedError:
        return _authorization_failed()
    return JSONResponse(
        jsonable_encoder({"items": [_protected_summary(item) for item in items]})
    )


@protected_router.get("/capabilities")
async def calendar_capabilities(request: Request) -> Response:
    context = await _protected_context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    actor, service = context
    try:
        capabilities = service.capabilities(actor)
    except CalendarAccessDeniedError:
        return _authorization_failed()
    return JSONResponse(capabilities)


@protected_router.get("/topics")
async def calendar_topics(request: Request) -> Response:
    context = await _protected_context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    actor, service = context
    try:
        topics = await service.list_topics(actor=actor)
    except CalendarAccessDeniedError:
        return _authorization_failed()
    return JSONResponse(
        jsonable_encoder({"items": [{"id": item.id, "name": item.name} for item in topics]})
    )


@protected_router.post("/offers")
async def create_offer(request: Request) -> Response:
    context = await _protected_context(request, require_csrf=True)
    if isinstance(context, Response):
        return context
    actor, service = context
    payload = await _read_json(request, CalendarCreateRequest)
    if payload is None:
        return _invalid_request()
    try:
        result = await service.create_offer(
            actor=actor,
            coach_id=payload.coach_id,
            client_request_id=payload.client_request_id,
            draft=_draft(payload.draft),
            now=request.app.state.clock(),
        )
    except Exception as exc:
        return _calendar_error(exc)
    return await _detail_response(service, actor, result, status=201)


@protected_router.get("/offers/{offer_id}")
async def get_protected_offer(offer_id: UUID, request: Request) -> Response:
    context = await _protected_context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    actor, service = context
    try:
        result = await service.get_offer(actor=actor, offer_id=offer_id)
    except CalendarAccessDeniedError:
        return _authorization_failed()
    if result is None:
        return _not_found()
    return await _detail_response(service, actor, result)


@protected_router.patch("/offers/{offer_id}/draft")
async def update_draft(offer_id: UUID, request: Request) -> Response:
    context = await _protected_context(request, require_csrf=True)
    if isinstance(context, Response):
        return context
    actor, service = context
    version = _expected_version(request)
    if version is None:
        return _version_conflict()
    payload = await _read_json(request, CalendarDraftRequest)
    if payload is None:
        return _invalid_request()
    try:
        result = await service.update_draft(
            actor=actor,
            offer_id=offer_id,
            expected_version=version,
            draft=_draft(payload),
            now=request.app.state.clock(),
        )
    except Exception as exc:
        return _calendar_error(exc)
    return await _detail_response(service, actor, result)


@protected_router.post("/offers/{offer_id}/submit")
async def submit_offer(offer_id: UUID, request: Request) -> Response:
    return await _versioned_command(request, offer_id, "submit")


@protected_router.post("/offers/{offer_id}/withdraw")
async def withdraw_offer(offer_id: UUID, request: Request) -> Response:
    return await _versioned_command(request, offer_id, "withdraw")


@protected_router.get("/review-queue")
async def review_queue(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
) -> Response:
    context = await _protected_context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    actor, service = context
    try:
        items = await service.list_review_queue(actor=actor, limit=limit)
    except CalendarAccessDeniedError:
        return _authorization_failed()
    return JSONResponse(
        jsonable_encoder({"items": [_protected_summary(item) for item in items]})
    )


@protected_router.post("/offers/{offer_id}/review-decisions")
async def review_offer(offer_id: UUID, request: Request) -> Response:
    context = await _protected_context(request, require_csrf=True)
    if isinstance(context, Response):
        return context
    actor, service = context
    version = _expected_version(request)
    if version is None:
        return _version_conflict()
    payload = await _read_json(request, CalendarReviewRequest)
    if payload is None:
        return _invalid_request()
    try:
        result = await service.review_offer(
            actor=actor,
            offer_id=offer_id,
            expected_version=version,
            outcome=payload.outcome,
            note=payload.note,
            now=request.app.state.clock(),
        )
    except Exception as exc:
        return _calendar_error(exc)
    return await _detail_response(service, actor, result)


async def _versioned_command(
    request: Request, offer_id: UUID, command: str
) -> Response:
    context = await _protected_context(request, require_csrf=True)
    if isinstance(context, Response):
        return context
    actor, service = context
    version = _expected_version(request)
    if version is None:
        return _version_conflict()
    try:
        if command == "submit":
            result = await service.submit_offer(
                actor=actor,
                offer_id=offer_id,
                expected_version=version,
                now=request.app.state.clock(),
            )
        else:
            result = await service.withdraw_offer(
                actor=actor,
                offer_id=offer_id,
                expected_version=version,
                now=request.app.state.clock(),
            )
    except Exception as exc:
        return _calendar_error(exc)
    return await _detail_response(service, actor, result)


async def _protected_context(
    request: Request, *, require_csrf: bool
) -> tuple[SessionPrincipal, CalendarService] | Response:
    service: CalendarService | None = request.app.state.calendar_service
    repository = request.app.state.calendar_session_repository
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if service is None:
        return _unavailable()
    if repository is None or token is None:
        return _authentication_failed()
    try:
        token_hash = digest_token(token)
    except ValueError:
        return _authentication_failed()
    principal = await repository.refresh_active_session(
        token_hash,
        now=request.app.state.clock(),
        idle_timeout=request.app.state.session_idle_timeout,
    )
    if principal is None:
        return _authentication_failed()
    if not require_csrf:
        return principal, service
    csrf_token = request.headers.get("x-csrf-token")
    if (
        request.app.state.allowed_origin is None
        or request.headers.get("origin") != request.app.state.allowed_origin
        or csrf_token is None
    ):
        return _request_verification_failed()
    try:
        matches = hmac.compare_digest(
            digest_token(csrf_token), principal.csrf_token_hash
        )
    except ValueError:
        matches = False
    if not matches:
        return _request_verification_failed()
    return principal, service


def _public_context(
    request: Request,
) -> tuple[CalendarService, CalendarCursorCodec] | Response:
    service: CalendarService | None = request.app.state.calendar_service
    codec: CalendarCursorCodec | None = request.app.state.calendar_cursor_codec
    if service is None or codec is None:
        return _unavailable()
    return service, codec


async def _read_json(request: Request, model: type[RequestModel]) -> RequestModel | None:
    content_type = request.headers.get("content-type", "")
    if content_type.split(";", 1)[0].strip().casefold() != "application/json":
        return None
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_PORTAL_REQUEST_BYTES:
                return None
        except ValueError:
            return None
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_PORTAL_REQUEST_BYTES:
            return None
        body.extend(chunk)
    try:
        return model.model_validate_json(bytes(body))
    except ValidationError:
        return None


async def _detail_response(
    service: CalendarService,
    actor: SessionPrincipal,
    detail: CalendarOfferDetail,
    *,
    status: int = 200,
) -> Response:
    decision = await service.get_visible_review_decision(actor=actor, detail=detail)
    return JSONResponse(
        jsonable_encoder(_protected_detail(detail, decision)),
        status_code=status,
        headers={"ETag": f'"v{detail.offer.lock_version}"'},
    )


def _draft(payload: CalendarDraftRequest) -> CalendarDraft:
    return CalendarDraft(
        topic_id=payload.topic_id,
        title=payload.title,
        summary=payload.summary,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        time_zone=payload.time_zone,
        format_code=payload.format,
        public_location=payload.public_location,
        capacity=payload.capacity,
        review_threshold=payload.review_threshold,
        decision_deadline=payload.decision_deadline,
        price_display_text=payload.price_display_text,
    )


def _protected_summary(detail: CalendarOfferDetail) -> dict[str, object]:
    revision = detail.current_revision
    return {
        "id": detail.offer.id,
        "coach_id": detail.offer.coach_id,
        "coach_display_name": detail.offer.coach_display_name,
        "lifecycle_status": detail.offer.lifecycle_status,
        "lock_version": detail.offer.lock_version,
        "workflow_status": revision.workflow_status,
        "revision_number": revision.revision_number,
        "title": revision.draft.title,
        "topic_name": revision.topic_name,
        "starts_at": revision.draft.starts_at,
        "ends_at": revision.draft.ends_at,
        "updated_at": detail.offer.updated_at,
    }


def _protected_detail(
    detail: CalendarOfferDetail, decision: CalendarReviewDecision | None
) -> dict[str, object]:
    return {
        "id": detail.offer.id,
        "coach_id": detail.offer.coach_id,
        "coach_display_name": detail.offer.coach_display_name,
        "lifecycle_status": detail.offer.lifecycle_status,
        "lock_version": detail.offer.lock_version,
        "withdrawn_at": detail.offer.withdrawn_at,
        "created_at": detail.offer.created_at,
        "updated_at": detail.offer.updated_at,
        "current_revision": _protected_revision(detail.current_revision),
        "published_revision": (
            _protected_revision(detail.published_revision)
            if detail.published_revision is not None
            else None
        ),
        "review_decision": (
            {
                "outcome": decision.outcome,
                "note": decision.note,
                "decided_at": decision.decided_at,
            }
            if decision is not None
            else None
        ),
    }


def _protected_revision(revision) -> dict[str, object]:
    draft = revision.draft
    return {
        "id": revision.id,
        "revision_number": revision.revision_number,
        "workflow_status": revision.workflow_status,
        "topic_id": draft.topic_id,
        "topic_name": revision.topic_name,
        "title": draft.title,
        "summary": draft.summary,
        "starts_at": draft.starts_at,
        "ends_at": draft.ends_at,
        "time_zone": draft.time_zone,
        "format": draft.format_code,
        "public_location": draft.public_location,
        "capacity": draft.capacity,
        "review_threshold": draft.review_threshold,
        "decision_deadline": draft.decision_deadline,
        "price_display_text": draft.price_display_text,
        "submitted_at": revision.submitted_at,
        "published_at": revision.published_at,
        "created_at": revision.created_at,
        "updated_at": revision.updated_at,
    }


def _public_offer(offer: PublicCalendarOffer) -> dict[str, object]:
    return {
        "id": offer.id,
        "coach": {
            "display_name": offer.coach_display_name,
            "profile_path": offer.coach_profile_path,
        },
        "topic": {"id": offer.topic_id, "name": offer.topic_name},
        "title": offer.title,
        "summary": offer.summary,
        "starts_at": offer.starts_at,
        "ends_at": offer.ends_at,
        "time_zone": offer.time_zone,
        "format": offer.format_code,
        "public_location": offer.public_location,
        "capacity": offer.capacity,
        "decision_deadline": offer.decision_deadline,
        "price_display_text": offer.price_display_text,
        "updated_at": offer.updated_at,
    }


def _expected_version(request: Request) -> int | None:
    value = request.headers.get("if-match")
    match = _ETAG.fullmatch(value) if value is not None else None
    return int(match.group(1)) if match is not None else None


def _calendar_error(exc: Exception) -> Response:
    if isinstance(exc, CalendarAccessDeniedError):
        return _authorization_failed()
    if isinstance(exc, CalendarOfferNotFoundError):
        return _not_found()
    if isinstance(exc, CalendarVersionConflictError):
        return _version_conflict()
    if isinstance(exc, CalendarTimeConflictError):
        return _conflict("calendar_time_conflict", "Termin ueberschneidet sich")
    if isinstance(exc, CalendarIdempotencyConflictError):
        return _conflict(
            "calendar_idempotency_conflict", "Anfrage kann nicht wiederholt werden"
        )
    if isinstance(exc, CalendarTransitionConflictError):
        return _conflict(
            "calendar_transition_conflict", "Statuswechsel ist nicht moeglich"
        )
    if isinstance(exc, (CalendarTopicUnavailableError, ValueError)):
        return _invalid_request()
    raise exc


def _authentication_failed() -> Response:
    return problem_response(
        status=401,
        code="authentication_failed",
        title="Authentifizierung erforderlich",
    )


def _authorization_failed() -> Response:
    return problem_response(
        status=403,
        code="authorization_failed",
        title="Berechtigung nicht vorhanden",
    )


def _request_verification_failed() -> Response:
    return problem_response(
        status=403,
        code="request_verification_failed",
        title="Anfrage konnte nicht verifiziert werden",
    )


def _invalid_request() -> Response:
    return problem_response(
        status=400, code="invalid_request", title="Anfrage ist ungueltig"
    )


def _not_found() -> Response:
    return problem_response(
        status=404,
        code="calendar_offer_not_found",
        title="Angebot nicht gefunden",
    )


def _version_conflict() -> Response:
    return _conflict("calendar_version_conflict", "Datenstand ist nicht mehr aktuell")


def _conflict(code: str, title: str) -> Response:
    return problem_response(status=409, code=code, title=title)


def _unavailable() -> Response:
    return problem_response(
        status=503, code="portal_unavailable", title="Portal derzeit nicht verfuegbar"
    )
