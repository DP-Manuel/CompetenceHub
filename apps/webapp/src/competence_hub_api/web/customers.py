from uuid import UUID

from fastapi import APIRouter, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from competence_hub_api.portal.customers import (
    CompanyCustomerInput,
    CustomerError,
    PrivateCustomerInput,
    PrivateCustomerSearch,
    PrivateCustomerUpdate,
)
from competence_hub_api.web.companies import internal_company_principal, read_company_json
from competence_hub_api.web.problems import problem_response

router = APIRouter(prefix="/api/v1/portal/customers", tags=["portal-customers"])


async def _context(request: Request, *, verified: bool = False):
    actor = await internal_company_principal(request, require_csrf=verified)
    if isinstance(actor, Response):
        return actor
    administration = request.app.state.customer_administration
    if administration is None:
        return problem_response(status=404, code="customer_unavailable", title="Kundenverwaltung nicht verfuegbar")
    return actor, administration


async def _result(operation, *, status: int = 200) -> Response:
    try:
        value = await operation
    except CustomerError as error:
        return problem_response(status=error.status, code=error.code, title=error.title)
    return JSONResponse(jsonable_encoder(value), status_code=status)


def _invalid_request() -> Response:
    return problem_response(status=400, code="invalid_request", title="Bitte pruefen Sie die eingegebenen Daten")


@router.get("/capabilities")
async def customer_capabilities(request: Request) -> Response:
    actor = await internal_company_principal(request, require_csrf=False)
    if isinstance(actor, Response):
        return actor
    return JSONResponse({"enabled": request.app.state.customer_administration is not None})


@router.post("/private/search")
async def search_private(request: Request) -> Response:
    # Customer names belong in the protected body, never in request URLs.
    context = await _context(request, verified=True)
    if isinstance(context, Response):
        return context
    payload = await read_company_json(request, PrivateCustomerSearch)
    if payload is None:
        return _invalid_request()
    actor, administration = context
    return await _result(administration.search_private(actor, payload))


@router.get("/private/{customer_id}")
async def get_private(customer_id: UUID, request: Request) -> Response:
    context = await _context(request)
    if isinstance(context, Response):
        return context
    actor, administration = context
    return await _result(administration.get_private(actor, customer_id))


@router.post("/private", status_code=201)
async def create_private(request: Request) -> Response:
    context = await _context(request, verified=True)
    if isinstance(context, Response):
        return context
    payload = await read_company_json(request, PrivateCustomerInput)
    if payload is None:
        return _invalid_request()
    actor, administration = context
    return await _result(administration.save_private(actor, payload, request.app.state.clock()), status=201)


@router.put("/private/{customer_id}")
async def update_private(customer_id: UUID, request: Request) -> Response:
    context = await _context(request, verified=True)
    if isinstance(context, Response):
        return context
    payload = await read_company_json(request, PrivateCustomerUpdate)
    if payload is None:
        return _invalid_request()
    actor, administration = context
    return await _result(administration.save_private(actor, payload, request.app.state.clock(), customer_id=customer_id))


@router.get("/companies/{company_id}/details")
async def get_company_details(company_id: UUID, request: Request) -> Response:
    context = await _context(request)
    if isinstance(context, Response):
        return context
    actor, administration = context
    return await _result(administration.get_company_details(actor, company_id))


@router.put("/companies/{company_id}/details")
async def update_company_details(company_id: UUID, request: Request) -> Response:
    context = await _context(request, verified=True)
    if isinstance(context, Response):
        return context
    payload = await read_company_json(request, CompanyCustomerInput)
    if payload is None:
        return _invalid_request()
    actor, administration = context
    return await _result(administration.save_company_details(actor, company_id, payload, request.app.state.clock()))
