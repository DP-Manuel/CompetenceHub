from datetime import date
from typing import Annotated, Literal
from unicodedata import category
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from competence_hub_api.portal.requests import MAX_VERSION, OptionBucket, RequestError, RequestStatus, require_manager
from competence_hub_api.web.calendar import calendar_principal
from competence_hub_api.web.companies import read_company_json
from competence_hub_api.web.problems import problem_response

router = APIRouter(prefix="/api/v1/portal/requests", tags=["portal-requests"])
Version = Annotated[int, Field(strict=True, ge=1, le=MAX_VERSION)]
Subject = Annotated[str, Field(min_length=1, max_length=160)]
Description = Annotated[str, Field(min_length=1, max_length=4000)]
PageLimit = Annotated[int, Query(ge=1, le=100)]


def _safe_text(value: str | None) -> str | None:
    if value is not None and any(category(char) in {"Cc", "Cs"} and char not in "\t\r\n" for char in value):
        raise ValueError("invalid text")
    return value


class Command(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RequestFields(Command):
    subject: Subject | None = None
    description: Description | None = None
    status: RequestStatus | None = None
    company_id: UUID | None = None
    private_customer_id: UUID | None = None
    service_id: UUID | None = None
    offer_id: UUID | None = None
    coach_id: UUID | None = None
    responsible_user_id: UUID | None = None
    follow_up_on: Annotated[date, Field(strict=True)] | None = None
    desired_period: Annotated[str, Field(min_length=1, max_length=160)] | None = None
    preferred_format: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    coach_summary: Annotated[str, Field(min_length=1, max_length=1200)] | None = None

    @field_validator("subject", "description", "desired_period", "preferred_format", "coach_summary")
    @classmethod
    def safe_text(cls, value):
        return _safe_text(value)


class CreateRequest(RequestFields):
    subject: Subject
    description: Description
    status: RequestStatus = "open"


class UpdateRequest(RequestFields):
    version: Version

    @model_validator(mode="after")
    def validate_patch(self):
        changes = self.model_fields_set - {"version"}
        if not changes or any(getattr(self, name) is None for name in changes & {"subject", "description", "status"}):
            raise ValueError("invalid patch")
        return self


class AddNote(Command):
    version: Version
    visibility: Literal["internal", "coach"]
    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body")
    @classmethod
    def safe_text(cls, value):
        return _safe_text(value)


def _error(error: RequestError) -> Response:
    titles = {
        400: "Bitte pruefen Sie die eingegebenen Daten",
        403: "Aktion nicht erlaubt",
        404: "Anfrage nicht verfuegbar",
        409: "Bitte laden Sie die Anfrage neu",
    }
    return problem_response(
        status=error.status,
        code=error.code,
        title=titles[error.status],
        field_errors=[{"field": error.field, "code": error.code}] if error.field else None,
    )


async def _context(request: Request, *, write: bool = False, manage: bool = False):
    actor = await calendar_principal(request, require_csrf=write)
    if isinstance(actor, Response):
        return actor
    repository = request.app.state.coaching_request_repository
    if repository is None:
        return _error(RequestError("request_not_found", 404))
    if manage:
        try:
            require_manager(actor)
        except RequestError as error:
            return _error(error)
    return actor, repository


async def _result(operation, *, status: int = 200) -> Response:
    try:
        item = await operation
    except RequestError as error:
        return _error(error)
    return JSONResponse(jsonable_encoder(item), status_code=status)


@router.get("/capabilities")
async def capabilities(request: Request) -> Response:
    actor = await calendar_principal(request, require_csrf=False)
    if isinstance(actor, Response):
        return actor
    repository = request.app.state.coaching_request_repository
    if repository is None:
        return JSONResponse({"enabled": False, "can_read": False, "can_manage": False, "scope": None})
    return await _result(repository.capabilities(actor))


@router.get("/options")
async def options(request: Request, bucket: OptionBucket, after: UUID | None = None, limit: PageLimit = 50) -> Response:
    context = await _context(request, manage=True)
    if isinstance(context, Response):
        return context
    actor, repository = context
    return await _result(repository.options(actor, bucket=bucket, after=after, limit=limit))


@router.get("")
async def list_requests(request: Request, status: RequestStatus | None = None,
                        after: UUID | None = None, limit: PageLimit = 50) -> Response:
    context = await _context(request)
    if isinstance(context, Response):
        return context
    actor, repository = context
    return await _result(repository.list(actor, status=status, after=after, limit=limit))


@router.get("/{request_id}")
async def detail(request: Request, request_id: UUID) -> Response:
    context = await _context(request)
    if isinstance(context, Response):
        return context
    actor, repository = context
    return await _result(repository.detail(actor, request_id))


async def _command(request: Request, model, *, request_id: UUID | None = None) -> Response:
    context = await _context(request, write=True, manage=True)
    if isinstance(context, Response):
        return context
    actor, repository = context
    data = await read_company_json(request, model)
    if data is None:
        return _error(RequestError("invalid_request", 400))
    now = request.app.state.clock()
    if isinstance(data, CreateRequest):
        return await _result(repository.create(actor, data.model_dump(), now), status=201)
    if isinstance(data, UpdateRequest):
        changes = data.model_dump(exclude_unset=True, exclude={"version"})
        return await _result(repository.update(actor, request_id, data.version, changes, now))
    return await _result(repository.add_note(actor, request_id, data.version, data.visibility, data.body, now), status=201)


@router.post("", status_code=201)
async def create(request: Request) -> Response:
    return await _command(request, CreateRequest)


@router.patch("/{request_id}")
async def update(request: Request, request_id: UUID) -> Response:
    return await _command(request, UpdateRequest, request_id=request_id)


@router.post("/{request_id}/notes", status_code=201)
async def add_note(request: Request, request_id: UUID) -> Response:
    return await _command(request, AddNote, request_id=request_id)
