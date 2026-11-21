from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from competence_hub_api.portal.reservations import ReservationError
from competence_hub_api.web.calendar import _expected_version, _invalid_request, _read_json, calendar_principal
from competence_hub_api.web.problems import problem_response

router = APIRouter(prefix="/api/v1/portal/reservations", tags=["portal-reservations"])


class Command(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    request_id: UUID


class SeatsCommand(Command):
    seats: int = Field(strict=True, ge=1, le=500)


class CreateReservation(SeatsCommand):
    revision_number: int = Field(strict=True, ge=1, le=2_147_483_647)
    contact_confirmed: StrictBool
    phone: str | None = Field(default=None, max_length=50)
    message: str | None = Field(default=None, max_length=500)


class ReviewReservation(Command):
    outcome: Literal["clarification_requested", "approved", "rejected"]
    reason: str = Field(min_length=1, max_length=500)

    @field_validator("reason")
    @classmethod
    def non_blank(cls, value):
        if not value.strip():
            raise ValueError("reason required")
        return value


class ReplyReservation(Command):
    reason: str = Field(min_length=1, max_length=500)


async def _context(request, *, write=False):
    repo = request.app.state.reservation_repository
    if repo is None:
        return problem_response(status=404, code="reservation_not_found", title="Nicht verfuegbar")
    actor = await calendar_principal(request, require_csrf=write)
    return actor if isinstance(actor, Response) else (repo, actor)


def _error(error):
    return problem_response(
        status=error.status, code=f"reservation_{error.code}", title="Vormerkung nicht moeglich",
        field_errors=[{"field": error.field, "code": error.code}] if error.field else None,
    )


@router.get("/capabilities")
async def capabilities(request: Request):
    if request.app.state.reservation_repository is None:
        return JSONResponse({})
    context = await _context(request)
    if isinstance(context, Response):
        return context
    repo, actor = context
    return JSONResponse(await repo.capabilities(actor))


@router.get("/catalogue")
async def catalogue(request: Request, after: UUID | None = None,
                    search: str = Query(default="", max_length=100), day: date | None = None,
                    offer_id: UUID | None = None):
    context = await _context(request)
    if isinstance(context, Response):
        return context
    repo, actor = context
    try:
        return JSONResponse(jsonable_encoder(await repo.catalogue(
            actor, after, search=search.strip(), day=day, offer_id=offer_id,
        )))
    except ReservationError as error:
        return _error(error)


@router.get("/activity")
async def activity(request: Request, review: bool = False):
    context = await _context(request)
    if isinstance(context, Response):
        return context
    repo, actor = context
    try:
        return JSONResponse(jsonable_encoder(await repo.activity(actor, review=review)))
    except ReservationError as error:
        return _error(error)


@router.get("/communication-drafts")
async def communication_drafts(request: Request, review: bool = False):
    context = await _context(request)
    if isinstance(context, Response):
        return context
    repo, actor = context
    try:
        return JSONResponse(jsonable_encoder(await repo.communication_drafts(actor, review=review)))
    except ReservationError as error:
        return _error(error)


@router.get("")
async def reservations(request: Request, review: bool = False, open_only: bool = False,
                       after: UUID | None = None, day: date | None = None,
                       offer: str = Query(default="", max_length=100),
                       coach: str = Query(default="", max_length=100),
                       status: Literal["", "open", "decision", "clarification", "pending", "approved",
                                       "rejected", "withdrawn", "cancelled", "past"] = "",
                       deadline: Literal["", "overdue", "soon", "later"] = ""):
    return await _list(request, review=review, open_only=open_only, after=after, day=day,
                       offer=offer.strip(), coach=coach.strip(), status=status, deadline=deadline)


@router.get("/{reservation_id}")
async def detail(request: Request, reservation_id: UUID, review: bool = False):
    return await _list(request, review=review, reservation_id=reservation_id)


async def _list(request, **filters):
    context = await _context(request)
    if isinstance(context, Response):
        return context
    repo, actor = context
    try:
        item = await repo.list(actor, **filters)
    except ReservationError as error:
        return _error(error)
    headers = {"ETag": f'"v{item["version"]}"'} if "version" in item else None
    return JSONResponse(jsonable_encoder(item), headers=headers)


@router.post("/offers/{offer_id}", status_code=201)
async def submit(request: Request, offer_id: UUID):
    return await _command(request, offer_id, CreateReservation, action="submitted")


@router.patch("/{reservation_id}/seats")
async def change_seats(request: Request, reservation_id: UUID):
    return await _command(request, reservation_id, SeatsCommand, action="seats_changed")


@router.post("/{reservation_id}/withdraw")
async def withdraw(request: Request, reservation_id: UUID):
    return await _command(request, reservation_id, Command, action="withdrawn")


@router.post("/{reservation_id}/decide")
async def decide(request: Request, reservation_id: UUID):
    return await _command(request, reservation_id, ReviewReservation, review=True)


@router.post("/{reservation_id}/reply")
async def reply(request: Request, reservation_id: UUID):
    return await _command(request, reservation_id, ReplyReservation, action="clarification_answered")


async def _command(request, target, model, *, action=None, review=False):
    context = await _context(request, write=True)
    if isinstance(context, Response):
        return context
    repo, actor = context
    data = await _read_json(request, model, field_names=model.model_fields)
    if data is None:
        return _invalid_request(getattr(request.state, "calendar_field_errors", None))
    if isinstance(data, CreateReservation):
        if not data.contact_confirmed:
            return _invalid_request([{"field": "contact_confirmed", "code": "required"}])
        expected = data.revision_number
    else:
        expected = _expected_version(request) if len(request.headers.get("if-match", "")) <= 15 else None
        if expected is None:
            return _error(ReservationError("stale_version"))
    try:
        reservation_id = await repo.command(
            actor, action=data.outcome if review else action, target=target, request_id=data.request_id,
            expected=expected, review=review, seats=getattr(data, "seats", None),
            reason=getattr(data, "reason", None), phone=getattr(data, "phone", None) or None,
            message=getattr(data, "message", None) or None,
        )
    except ReservationError as error:
        return _error(error)
    return JSONResponse({"id": str(reservation_id)}, status_code=201 if action == "submitted" else 200)
