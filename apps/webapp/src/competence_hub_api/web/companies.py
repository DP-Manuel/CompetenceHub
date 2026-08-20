import hmac
from dataclasses import asdict
from typing import TypeVar
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.portal.companies import (
    CompanyAccessDeniedError,
    CompanyContactRecord,
    CompanyDetail,
    CompanyRecord,
    CompanySummary,
    CompanyService,
    INTERNAL_ROLES,
    NewCompanyContact,
)
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token
from competence_hub_api.web.problems import problem_response

router = APIRouter(prefix="/api/v1/portal/companies", tags=["portal-companies"])
MAX_PORTAL_REQUEST_BYTES = 32 * 1024


class ContactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    phone: str | None = Field(default=None, max_length=50)
    job_function: str | None = Field(default=None, max_length=200)


class CompanyCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    industry: str | None = Field(default=None, max_length=200)
    internal_notes: str | None = Field(default=None, max_length=4000)
    initial_contact: ContactRequest


class CompanyPatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=200)
    industry: str | None = Field(default=None, max_length=200)
    internal_notes: str | None = Field(default=None, max_length=4000)


class ContactPatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=50)
    job_function: str | None = Field(default=None, max_length=200)


RequestModel = TypeVar("RequestModel", bound=BaseModel)


@router.get("")
async def list_companies(
    request: Request,
    query: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=50, ge=1, le=100),
) -> Response:
    context = await _context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    principal, service = context
    try:
        companies = await service.list_companies(
            actor=principal,
            query=query,
            limit=limit,
        )
    except (CompanyAccessDeniedError, ValueError):
        return _authorization_failed()
    return JSONResponse(
        jsonable_encoder({"items": [_company_summary(item) for item in companies]})
    )


@router.get("/{company_id}")
async def get_company(company_id: UUID, request: Request) -> Response:
    context = await _context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    principal, service = context
    try:
        detail = await service.get_company(actor=principal, company_id=company_id)
    except CompanyAccessDeniedError:
        return _authorization_failed()
    if detail is None:
        return _not_found()
    return JSONResponse(jsonable_encoder(_detail(detail)))


@router.post("", status_code=201)
async def create_company(request: Request) -> Response:
    context = await _context(request, require_csrf=True)
    if isinstance(context, Response):
        return context
    payload = await _read_json(request, CompanyCreateRequest)
    if payload is None:
        return _invalid_request()
    principal, service = context
    try:
        detail = await service.create_company(
            actor=principal,
            name=payload.name,
            industry=payload.industry,
            internal_notes=payload.internal_notes,
            initial_contact=_new_contact(payload.initial_contact),
            now=request.app.state.clock(),
        )
    except CompanyAccessDeniedError:
        return _authorization_failed()
    except ValueError:
        return _invalid_request()
    return JSONResponse(status_code=201, content=jsonable_encoder(_detail(detail)))


@router.patch("/{company_id}")
async def update_company(company_id: UUID, request: Request) -> Response:
    context = await _context(request, require_csrf=True)
    if isinstance(context, Response):
        return context
    payload = await _read_json(request, CompanyPatchRequest)
    if payload is None or not payload.model_fields_set:
        return _invalid_request()
    changes = {
        name: getattr(payload, name)
        for name in payload.model_fields_set
    }
    principal, service = context
    try:
        company = await service.update_company(
            actor=principal,
            company_id=company_id,
            changes=changes,
            now=request.app.state.clock(),
        )
    except CompanyAccessDeniedError:
        return _authorization_failed()
    except ValueError:
        return _invalid_request()
    if company is None:
        return _not_found()
    return JSONResponse(jsonable_encoder(_company(company)))


@router.post("/{company_id}/contacts", status_code=201)
async def add_contact(company_id: UUID, request: Request) -> Response:
    context = await _context(request, require_csrf=True)
    if isinstance(context, Response):
        return context
    payload = await _read_json(request, ContactRequest)
    if payload is None:
        return _invalid_request()
    principal, service = context
    try:
        contact = await service.add_contact(
            actor=principal,
            company_id=company_id,
            contact=_new_contact(payload),
            now=request.app.state.clock(),
        )
    except CompanyAccessDeniedError:
        return _authorization_failed()
    except ValueError:
        return _invalid_request()
    if contact is None:
        return _not_found()
    return JSONResponse(status_code=201, content=jsonable_encoder(_contact(contact)))


@router.patch("/{company_id}/contacts/{contact_id}")
async def update_contact(
    company_id: UUID,
    contact_id: UUID,
    request: Request,
) -> Response:
    context = await _context(request, require_csrf=True)
    if isinstance(context, Response):
        return context
    payload = await _read_json(request, ContactPatchRequest)
    if payload is None or not payload.model_fields_set:
        return _invalid_request()
    changes = {
        name: getattr(payload, name)
        for name in payload.model_fields_set
    }
    principal, service = context
    try:
        contact = await service.update_contact(
            actor=principal,
            company_id=company_id,
            contact_id=contact_id,
            changes=changes,
            now=request.app.state.clock(),
        )
    except CompanyAccessDeniedError:
        return _authorization_failed()
    except ValueError:
        return _invalid_request()
    if contact is None:
        return _not_found()
    return JSONResponse(jsonable_encoder(_contact(contact)))


async def _context(
    request: Request,
    *,
    require_csrf: bool,
) -> tuple[SessionPrincipal, CompanyService] | Response:
    service: CompanyService | None = request.app.state.company_service
    repository = request.app.state.session_repository
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if service is None:
        return problem_response(
            status=503,
            code="portal_unavailable",
            title="Portal derzeit nicht verfuegbar",
        )
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
    if not set(principal.roles).intersection(INTERNAL_ROLES):
        return _authorization_failed()
    if not require_csrf:
        return principal, service
    allowed_origin = request.app.state.allowed_origin
    csrf_token = request.headers.get("x-csrf-token")
    if (
        allowed_origin is None
        or request.headers.get("origin") != allowed_origin
        or csrf_token is None
    ):
        return _request_verification_failed()
    try:
        csrf_matches = hmac.compare_digest(
            digest_token(csrf_token),
            principal.csrf_token_hash,
        )
    except ValueError:
        csrf_matches = False
    if not csrf_matches:
        return _request_verification_failed()
    return principal, service


async def _read_json(
    request: Request,
    model: type[RequestModel],
) -> RequestModel | None:
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


def _new_contact(payload: ContactRequest) -> NewCompanyContact:
    return NewCompanyContact(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        job_function=payload.job_function,
    )


def _detail(detail: CompanyDetail) -> dict[str, object]:
    return {
        **_company(detail.company),
        "contacts": [_contact(item) for item in detail.contacts],
    }


def _company(company: CompanyRecord) -> dict[str, object]:
    return asdict(company)


def _company_summary(company: CompanySummary) -> dict[str, object]:
    return asdict(company)


def _contact(contact: CompanyContactRecord) -> dict[str, object]:
    return asdict(contact)


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
        status=400,
        code="invalid_request",
        title="Anfrage ist ungueltig",
    )


def _not_found() -> Response:
    return problem_response(
        status=404,
        code="company_record_not_found",
        title="Datensatz nicht gefunden",
    )
