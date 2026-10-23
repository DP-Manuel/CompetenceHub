"""Optional, admin-only local Registry API; no public live DB projection."""

from dataclasses import asdict
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from competence_hub_api.portal.coach_registry import (
    CoachRegistryService,
    ProfileContent,
    RegistryConflict,
    RegistryDenied,
)
from competence_hub_api.web.admin import _admin_principal
from competence_hub_api.web.problems import problem_response

router = APIRouter(prefix="/api/v1/admin/coaches", tags=["coach-registry"])


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateRequest(StrictRequest):
    display_name: str = Field(min_length=1, max_length=200)
    client_request_id: UUID


class VersionRequest(StrictRequest):
    expected_version: int = Field(ge=1)


class RevisionRequest(VersionRequest):
    content: ProfileContent


class LifecycleRequest(VersionRequest):
    lifecycle: Literal["draft", "active", "paused", "inactive", "archived"]


class ApprovalRequest(VersionRequest):
    kind: Literal["content_review", "person_consent", "preview", "production"]
    evidence_ref: str = Field(min_length=1, max_length=200)


class PublishRequest(VersionRequest):
    revision_id: UUID


def failure(status, code):
    return problem_response(
        status=status, code=code, title="Coach-Anfrage derzeit nicht moeglich"
    )


async def context(request):
    actor = await _admin_principal(request, require_csrf=request.method != "GET")
    if isinstance(actor, Response):
        return actor
    service = request.app.state.coach_registry_service
    if service is None:
        return failure(503, "registry_unavailable")
    return actor, service


async def payload(request, model):
    if (
        request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        != "application/json"
    ):
        return None
    body = bytearray()
    async for part in request.stream():
        if len(body) + len(part) > 32768:
            return None
        body.extend(part)
    try:
        return model.model_validate_json(bytes(body))
    except ValidationError:
        return None


def summary(coach):
    return {
        "id": coach.id,
        "display_name": coach.display_name,
        "lifecycle": coach.lifecycle,
        "version": coach.version,
    }


def detail(coach):
    return {
        **summary(coach),
        "revisions": [
            {
                "id": r.id,
                "number": r.number,
                "status": r.status,
                "content": r.content.model_dump(mode="json"),
                "approvals": [asdict(a) for a in r.approvals],
            }
            for r in coach.revisions
        ],
        "publications": {e: asdict(p) for e, p in coach.publications.items()},
    }


@router.get("")
async def list_coaches(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=10000),
):
    found = await context(request)
    if isinstance(found, Response):
        return found
    _, service = found
    items = await service.repository.list_coaches(limit=limit, offset=offset)
    return JSONResponse(
        jsonable_encoder(
            {"items": [summary(c) for c in items], "limit": limit, "offset": offset}
        )
    )


@router.get("/{coach_id}")
async def get_coach(coach_id: UUID, request: Request):
    found = await context(request)
    if isinstance(found, Response):
        return found
    coach = await found[1].repository.get(coach_id)
    return (
        JSONResponse(jsonable_encoder(detail(coach)))
        if coach
        else failure(404, "not_found")
    )


@router.post("", status_code=201)
async def create_coach(request: Request):
    found = await context(request)
    if isinstance(found, Response):
        return found
    value = await payload(request, CreateRequest)
    if value is None:
        return failure(400, "invalid_request")
    actor, service = found
    try:
        coach = await service.create(
            actor=actor,
            display_name=value.display_name,
            request_id=value.client_request_id,
            now=request.app.state.clock(),
        )
    except RegistryConflict:
        return failure(409, "registry_conflict")
    except ValueError:
        return failure(400, "invalid_request")
    return JSONResponse(status_code=201, content=jsonable_encoder(detail(coach)))


async def mutate(request, coach_id, model, operation, **fixed):
    found = await context(request)
    if isinstance(found, Response):
        return found
    value = await payload(request, model)
    if value is None:
        return failure(400, "invalid_request")
    actor, service = found
    args = {k: getattr(value, k) for k in type(value).model_fields}
    try:
        coach = await service.mutate(
            actor=actor,
            coach_id=coach_id,
            operation=operation,
            now=request.app.state.clock(),
            **args,
            **fixed,
        )
    except RegistryConflict:
        return failure(409, "registry_conflict")
    except LookupError:
        return failure(404, "not_found")
    except RegistryDenied:
        return failure(403, "authorization_failed")
    except ValueError:
        return failure(400, "invalid_request")
    return JSONResponse(jsonable_encoder(detail(coach)))


@router.post("/{coach_id}/revisions")
async def new_revision(coach_id: UUID, request: Request):
    return await mutate(request, coach_id, RevisionRequest, "revision")


@router.patch("/{coach_id}/revisions/{revision_id}")
async def edit_draft(coach_id: UUID, revision_id: UUID, request: Request):
    return await mutate(
        request, coach_id, RevisionRequest, "draft", revision_id=revision_id
    )


@router.post("/{coach_id}/revisions/{revision_id}/submit")
async def submit(coach_id: UUID, revision_id: UUID, request: Request):
    return await mutate(
        request, coach_id, VersionRequest, "submit", revision_id=revision_id
    )


@router.post("/{coach_id}/revisions/{revision_id}/approvals")
async def approve(coach_id: UUID, revision_id: UUID, request: Request):
    return await mutate(
        request, coach_id, ApprovalRequest, "approve", revision_id=revision_id
    )


@router.patch("/{coach_id}/lifecycle")
async def lifecycle(coach_id: UUID, request: Request):
    return await mutate(request, coach_id, LifecycleRequest, "lifecycle")


@router.post("/{coach_id}/publications/{environment}")
async def publish(
    coach_id: UUID, environment: Literal["preview", "production"], request: Request
):
    return await mutate(
        request, coach_id, PublishRequest, "publish", environment=environment
    )


@router.post("/{coach_id}/publications/{environment}/withdraw")
async def withdraw(
    coach_id: UUID, environment: Literal["preview", "production"], request: Request
):
    return await mutate(
        request, coach_id, VersionRequest, "withdraw", environment=environment
    )
