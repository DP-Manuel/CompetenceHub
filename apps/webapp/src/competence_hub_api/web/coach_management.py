"""Admin-authenticated management reads and direct UI entry; never deploys a site."""

from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse

from competence_hub_api.web.coach_registry import context, failure

router = APIRouter()
BASE = "/api/v1/admin/coach-management"


async def queries(request):
    found = await context(request)
    if isinstance(found, Response):
        return found
    reader = request.app.state.coach_management_queries
    return reader if reader is not None else failure(503, "registry_unavailable")


@router.get("/portal/coaches/", include_in_schema=False)
async def admin_entry(request: Request):
    reader = await queries(request)
    if isinstance(reader, Response):
        return reader
    return FileResponse(Path(__file__).parents[1] / "portal_ui" / "index.html")


@router.get(BASE)
async def index(
    request: Request,
    limit: int = Query(25, ge=1, le=50),
    offset: int = Query(0, ge=0, le=10000),
    lifecycle: (
        Literal["draft", "active", "paused", "inactive", "archived"] | None
    ) = None,
    publication: Literal["preview", "production", "unpublished"] | None = None,
):
    reader = await queries(request)
    if isinstance(reader, Response):
        return reader
    return JSONResponse(
        jsonable_encoder(
            await reader.index(
                limit=limit, offset=offset, lifecycle=lifecycle, publication=publication
            )
        )
    )


@router.get(BASE + "/topics")
async def topics(
    request: Request,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0, le=10000),
):
    reader = await queries(request)
    if isinstance(reader, Response):
        return reader
    return JSONResponse(
        jsonable_encoder(await reader.topics(limit=limit, offset=offset))
    )


@router.get(BASE + "/{coach_id}")
async def workspace(coach_id: UUID, request: Request, revision_id: UUID | None = None):
    reader = await queries(request)
    if isinstance(reader, Response):
        return reader
    try:
        result = await reader.workspace(
            coach_id, revision_id=revision_id, now=request.app.state.clock()
        )
    except LookupError:
        result = None
    return (
        JSONResponse(jsonable_encoder(result)) if result else failure(404, "not_found")
    )


@router.get(BASE + "/{coach_id}/{section}")
async def history(
    coach_id: UUID,
    section: Literal["history", "revisions"],
    request: Request,
    limit: int = Query(10, ge=1, le=25),
    offset: int = Query(0, ge=0, le=10000),
):
    reader = await queries(request)
    if isinstance(reader, Response):
        return reader
    if not await reader.workspace(coach_id, now=request.app.state.clock()):
        return failure(404, "not_found")
    return JSONResponse(
        jsonable_encoder(
            await reader.history(
                coach_id, limit=limit, offset=offset, revisions=section == "revisions"
            )
        )
    )
