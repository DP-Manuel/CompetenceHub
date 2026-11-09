"""Bounded, same-origin role overview. No credentials, tokens or audit payloads."""
from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import text

from competence_hub_api.web.admin import _admin_principal
from competence_hub_api.web.calendar import _protected_context
from competence_hub_api.web.problems import problem_response

router = APIRouter(tags=["pilot-overview"])

_COUNTS = text("""
    SELECT CASE WHEN o.lifecycle_status='withdrawn' THEN 'withdrawn'
                ELSE r.workflow_status END AS status, count(*) AS count
    FROM competence_hub.calendar_offers o
    JOIN competence_hub.coaches c ON c.id=o.coach_id
    JOIN LATERAL (SELECT workflow_status FROM competence_hub.calendar_offer_revisions
                  WHERE offer_id=o.id ORDER BY revision_number DESC LIMIT 1) r ON true
    WHERE (:admin OR (:reviewer AND r.workflow_status IN
           ('in_review','changes_requested','published')) OR c.portal_user_id=:actor)
    GROUP BY 1
""")
_USERS = text("""
    SELECT u.id, u.display_name, u.email,
      CASE WHEN NOT u.active AND NOT EXISTS
        (SELECT 1 FROM competence_hub.auth_password_credentials p WHERE p.portal_user_id=u.id)
        THEN 'pending_activation' WHEN NOT u.active THEN 'inactive'
        WHEN NOT EXISTS (SELECT 1 FROM competence_hub.auth_totp_credentials t
                         WHERE t.portal_user_id=u.id AND t.enabled_at IS NOT NULL)
        THEN 'mfa_required' ELSE 'active' END AS status,
      ARRAY(SELECT r.code FROM competence_hub.user_roles ur JOIN competence_hub.roles r
            ON r.id=ur.role_id WHERE ur.user_id=u.id AND r.active ORDER BY r.code) AS roles,
      (SELECT c.id FROM competence_hub.coaches c WHERE c.portal_user_id=u.id) AS coach_id
    FROM competence_hub.portal_users u ORDER BY u.created_at, u.id
    LIMIT :limit OFFSET :offset
""")


def unavailable():
    return problem_response(status=503, code="portal_unavailable", title="Übersicht derzeit nicht verfügbar")


@router.get("/api/v1/portal/pilot/overview")
async def overview(request: Request):
    context = await _protected_context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    actor, _ = context
    if not set(actor.roles).intersection({"admin", "coach", "calendar_reviewer"}):
        return problem_response(status=403, code="authorization_failed", title="Berechtigung nicht vorhanden")
    engine = getattr(request.app.state, "database_engine", None)
    if engine is None:
        return unavailable()
    async with engine.connect() as connection:
        await connection.execute(text("SET TRANSACTION READ ONLY"))
        rows = (await connection.execute(_COUNTS, {
            "admin": "admin" in actor.roles, "reviewer": "calendar_reviewer" in actor.roles,
            "actor": actor.user_id,
        })).mappings().all()
    return JSONResponse({"calendar": {r["status"]: r["count"] for r in rows},
                         "database": "reachable", "scope": "authorized_current_revisions"})


@router.get("/api/v1/admin/users")
async def users(request: Request, offset: int = Query(default=0, ge=0, le=100000),
                limit: int = Query(default=25, ge=1, le=100)):
    actor = await _admin_principal(request, require_csrf=False)
    if isinstance(actor, Response):
        return actor
    engine = getattr(request.app.state, "database_engine", None)
    if engine is None:
        return unavailable()
    async with engine.connect() as connection:
        await connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        total = await connection.scalar(text("SELECT count(*) FROM competence_hub.portal_users"))
        totals = (await connection.execute(text("""SELECT
            count(*) FILTER (WHERE u.active) AS active,
            count(*) FILTER (WHERE NOT u.active AND NOT EXISTS
              (SELECT 1 FROM competence_hub.auth_password_credentials p WHERE p.portal_user_id=u.id)) AS pending_activation
            FROM competence_hub.portal_users u"""))).mappings().one()
        items = (await connection.execute(_USERS, {"limit": limit, "offset": offset})).mappings().all()
        missing = await connection.scalar(text("""SELECT count(*) FROM competence_hub.portal_users u
            WHERE EXISTS (SELECT 1 FROM competence_hub.user_roles ur JOIN competence_hub.roles r
                          ON r.id=ur.role_id WHERE ur.user_id=u.id AND r.code='coach' AND r.active)
            AND NOT EXISTS (SELECT 1 FROM competence_hub.coaches c WHERE c.portal_user_id=u.id
                            AND COALESCE(to_jsonb(c)->>'lifecycle_status','active')='active')"""))
    return JSONResponse(jsonable_encoder({"items": [dict(row) for row in items],
        "total": total, "next_offset": offset+limit if offset+limit < total else None,
        "unmapped_coaches": missing,
        "totals": dict(totals),
        "invitations_enabled": getattr(request.app.state, "invitation_delivery_enabled", False)}))
