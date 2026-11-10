from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from competence_hub_api.auth.user_management import AccountManagementError, UserManagement
from competence_hub_api.web.admin import _admin_principal, MAX_ADMIN_REQUEST_BYTES
from competence_hub_api.web.problems import problem_response

router = APIRouter(prefix='/api/v1/admin/users', tags=['user-management'])
mapping_router = APIRouter(prefix='/api/v1/admin',tags=['coach-mapping'])


class AccountChange(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: Literal['suspend','deactivate','enable','set_role','revoke_invitation']
    expected_version: datetime
    role: Literal['admin','internal','coach','calendar_reviewer'] | None = None
    coach_id: UUID | None = None

    @field_validator('expected_version')
    @classmethod
    def aware_version(cls,value):
        if value.tzinfo is None:raise ValueError('Timezone required')
        return value


async def service(request: Request, csrf: bool):
    actor = await _admin_principal(request,require_csrf=csrf)
    if isinstance(actor,Response):return actor,None
    engine = getattr(request.app.state,'database_engine',None)
    if engine is None:
        return problem_response(status=503,code='portal_unavailable',title='Verwaltung derzeit nicht verfügbar'),None
    return actor,UserManagement(engine)


@router.patch('/{user_id}')
async def change_account(user_id:UUID,request:Request):
    actor,manager=await service(request,True)
    if isinstance(actor,Response):return actor
    if request.headers.get('content-type','').split(';',1)[0].strip().lower()!='application/json':
        return problem_response(status=400,code='invalid_request',title='Anfrage ist ungültig')
    raw=bytearray()
    async for part in request.stream():
        if len(raw)+len(part)>MAX_ADMIN_REQUEST_BYTES:
            return problem_response(status=400,code='invalid_request',title='Anfrage ist ungültig')
        raw.extend(part)
    try:
        body=AccountChange.model_validate_json(bytes(raw))
    except ValidationError:
        return problem_response(status=400,code='invalid_request',title='Anfrage ist ungültig')
    try:
        await manager.change(actor,target=user_id,now=request.app.state.clock(),**body.model_dump())
    except AccountManagementError as error:
        status=404 if error.code=='account_not_found' else 403 if error.code in ('reauthentication_required','authorization_failed') else 400 if error.code=='invalid_request' else 409
        return problem_response(status=status,code=error.code,title='Änderung nicht möglich; Berechtigung und aktuellen Kontostand prüfen')
    return JSONResponse({'status':'accepted'})


@router.get('/{user_id}/audit')
async def account_audit(user_id:UUID,request:Request):
    actor,manager=await service(request,False)
    if isinstance(actor,Response):return actor
    return JSONResponse(jsonable_encoder({'items':await manager.audit(user_id)}))


@mapping_router.get('/coach-mappings')
async def coach_mapping_candidates(request:Request):
    actor,manager=await service(request,False)
    if isinstance(actor,Response):return actor
    from sqlalchemy import text
    async with manager.engine.connect() as connection:
        await connection.execute(text('SET TRANSACTION READ ONLY'))
        rows=(await connection.execute(text("""SELECT id,display_name,portal_user_id,
            COALESCE(to_jsonb(c)->>'lifecycle_status','active') AS lifecycle_status
            FROM competence_hub.coaches c ORDER BY display_name,id LIMIT 100"""))).mappings().all()
    return JSONResponse(jsonable_encoder({'items':[dict(row) for row in rows],'limit':100}))
