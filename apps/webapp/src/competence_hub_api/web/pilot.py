"""Bounded, same-origin role overview. No credentials, tokens or audit payloads."""
from fastapi import APIRouter, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import text

from competence_hub_api.portal.calendar import CALENDAR_REVIEW_ROLES
from competence_hub_api.portal.reservations import (
    BOOKER_ROLE, OCCUPIED, OPEN, ReservationError, _LAST_CLARIFICATION, _company,
)
from competence_hub_api.web.admin import _admin_principal
from competence_hub_api.web.calendar import _protected_context, _request_verification_failed
from competence_hub_api.web.problems import problem_response

router = APIRouter(tags=["pilot-overview"])

_COUNTS = text("""
    SELECT CASE WHEN o.lifecycle_status='withdrawn' THEN 'withdrawn'
                ELSE r.workflow_status END AS status, count(*) AS count,
           count(*) FILTER (WHERE r.workflow_status='in_review' AND r.revision_number>1
                           AND o.lifecycle_status='active') AS resubmitted
    FROM competence_hub.calendar_offers o
    JOIN competence_hub.coaches c ON c.id=o.coach_id
    JOIN LATERAL (SELECT workflow_status,revision_number FROM competence_hub.calendar_offer_revisions
                  WHERE offer_id=o.id ORDER BY revision_number DESC LIMIT 1) r ON true
    WHERE (:admin OR (:reviewer AND r.workflow_status IN
           ('in_review','changes_requested','published')) OR (:coach AND c.portal_user_id=:actor))
    GROUP BY 1
""")
_USERS = text("""
    SELECT u.id, u.display_name, u.email,u.updated_at AS version,
      CASE WHEN NOT u.active AND NOT EXISTS
        (SELECT 1 FROM competence_hub.auth_password_credentials p WHERE p.portal_user_id=u.id)
        THEN 'pending_activation' WHEN NOT u.active THEN CASE WHEN
          (SELECT a.action FROM competence_hub.audit_events a WHERE a.entity_type='portal_user'
           AND a.entity_id=u.id AND a.action IN ('auth.account.suspend','auth.account.deactivate','auth.account.enable')
           ORDER BY a.occurred_at DESC,a.id DESC LIMIT 1)='auth.account.suspend'
          THEN 'blocked' ELSE 'inactive' END
        WHEN NOT EXISTS (SELECT 1 FROM competence_hub.auth_totp_credentials t
                         WHERE t.portal_user_id=u.id AND t.enabled_at IS NOT NULL)
        THEN 'mfa_required' ELSE 'active' END AS status,
      ARRAY(SELECT r.code FROM competence_hub.user_roles ur JOIN competence_hub.roles r
            ON r.id=ur.role_id WHERE ur.user_id=u.id AND r.active ORDER BY r.code) AS roles,
      (SELECT c.id FROM competence_hub.coaches c WHERE c.portal_user_id=u.id) AS coach_id,
      EXISTS(SELECT 1 FROM competence_hub.auth_totp_credentials t WHERE t.portal_user_id=u.id
             AND t.enabled_at IS NOT NULL) AS mfa_enabled,
      (SELECT max(s.authenticated_at) FROM competence_hub.auth_sessions s WHERE s.portal_user_id=u.id) AS last_authenticated_at,
      (SELECT json_build_object('expires_at',t.expires_at,'status',
           CASE WHEN t.revoked_at IS NOT NULL THEN 'revoked' WHEN t.consumed_at IS NOT NULL THEN 'consumed'
                WHEN t.expires_at<=CURRENT_TIMESTAMP THEN 'expired' ELSE 'pending' END)
       FROM competence_hub.auth_one_time_tokens t WHERE t.portal_user_id=u.id AND t.purpose='invitation'
       ORDER BY t.created_at DESC,t.id DESC LIMIT 1) AS invitation
    FROM competence_hub.portal_users u ORDER BY u.created_at, u.id
    LIMIT :limit OFFSET :offset
""")

_RECENT_PUBLICATIONS = text("""
    SELECT o.id,r.title,r.starts_at,r.published_at,c.display_name AS coach_name
    FROM competence_hub.calendar_offers o
    JOIN competence_hub.coaches c ON c.id=o.coach_id
    JOIN competence_hub.calendar_offer_revisions r ON r.offer_id=o.id
    WHERE o.lifecycle_status='active' AND r.workflow_status='published'
      AND (:admin OR :reviewer OR (:coach AND c.portal_user_id=:actor))
    ORDER BY r.published_at DESC,o.id LIMIT 5
""")

_CALENDAR_REVIEW = text("""
    WITH queue AS (
        SELECT o.id, r.title, r.submitted_at, r.revision_number
        FROM competence_hub.calendar_offers o
        JOIN competence_hub.calendar_offer_revisions r ON r.offer_id = o.id
        WHERE o.lifecycle_status = 'active' AND r.workflow_status = 'in_review'
    )
    SELECT count(*) AS calendar_in_review,
           count(*) FILTER (WHERE revision_number > 1) AS calendar_resubmitted,
           (SELECT coalesce(json_agg(task ORDER BY task.submitted_at, task.title, sample.id), '[]')
            FROM (SELECT * FROM queue ORDER BY submitted_at, id LIMIT 4) sample
            CROSS JOIN LATERAL (
                SELECT 'calendar_review' AS kind, sample.title, sample.submitted_at
            ) task) AS tasks
    FROM queue
""")

# Match the CAL-2 workspaces: each reservation references its agreed revision,
# and only the latest clarification event determines whose turn it is.
_SCOPED_RESERVATIONS = f"""
    SELECT s.id, s.offer_id, s.revision_number, s.status, s.seats,
           r.title, r.starts_at, r.ends_at, r.decision_deadline, r.capacity, r.review_threshold,
           o.lifecycle_status = 'active' AND t.active AND r.workflow_status = 'published' AS available,
           clarification.event AS clarification_event
    FROM competence_hub.calendar_reservations s
    JOIN competence_hub.calendar_offers o ON o.id = s.offer_id
    JOIN competence_hub.calendar_offer_revisions r
        ON (r.offer_id, r.revision_number) = (s.offer_id, s.revision_number)
    JOIN competence_hub.topics t ON t.id = r.topic_id
    {_LAST_CLARIFICATION}
"""

_REVIEW_RESERVATIONS = text(f"""
    WITH scoped AS ({_SCOPED_RESERVATIONS}),
    load AS (
        SELECT s.offer_id, s.revision_number, s.title, s.starts_at, s.decision_deadline,
               s.capacity, s.review_threshold, s.available, sum(s.seats) AS occupied_seats,
               count(*) FILTER (WHERE s.status = 'pending') AS pending,
               count(*) FILTER (WHERE s.clarification_event = 'clarification_answered') AS reply_ready,
               count(*) FILTER (WHERE s.status = ANY(:open)) AS open_count,
               EXISTS (
                   SELECT 1 FROM competence_hub.calendar_offer_revisions proposed
                   JOIN competence_hub.calendar_offers o ON o.id = proposed.offer_id
                   WHERE proposed.offer_id = s.offer_id AND o.lifecycle_status = 'active'
                     AND proposed.workflow_status = 'in_review'
               ) AS revision_pending
        FROM scoped s
        WHERE s.status = ANY(:occupied)
        GROUP BY s.offer_id, s.revision_number, s.title, s.starts_at, s.decision_deadline,
                 s.capacity, s.review_threshold, s.available
    ),
    flags AS (
        SELECT *,
               open_count > 0 AND decision_deadline <= CURRENT_TIMESTAMP AS overdue,
               open_count > 0 AND decision_deadline > CURRENT_TIMESTAMP
                   AND decision_deadline <= CURRENT_TIMESTAMP + interval '48 hours' AS deadline_soon,
               available AND starts_at > CURRENT_TIMESTAMP AND occupied_seats >= capacity AS is_full,
               available AND starts_at > CURRENT_TIMESTAMP
                   AND occupied_seats >= review_threshold AS threshold_reached
        FROM load
    ),
    ranked AS (
        SELECT *, CASE WHEN overdue THEN 1 WHEN revision_pending THEN 2 WHEN deadline_soon THEN 3
                       WHEN reply_ready > 0 THEN 4 WHEN pending > 0 THEN 5 ELSE 6 END AS priority
        FROM flags
        WHERE overdue OR revision_pending OR deadline_soon OR reply_ready > 0 OR pending > 0
            OR is_full OR threshold_reached
        ORDER BY priority, decision_deadline, offer_id, revision_number LIMIT 8
    )
    SELECT count(*) FILTER (WHERE status = 'pending') AS pending,
           count(*) FILTER (WHERE status = 'clarification' AND
                            clarification_event IS DISTINCT FROM 'clarification_answered') AS clarification,
           count(*) FILTER (WHERE clarification_event = 'clarification_answered') AS reply_ready,
           count(*) FILTER (WHERE status = 'approved') AS approved,
           count(*) FILTER (WHERE status = 'rejected') AS rejected,
           count(*) FILTER (WHERE status = 'withdrawn') AS withdrawn,
           count(*) FILTER (WHERE status = 'cancelled') AS cancelled,
           count(*) FILTER (WHERE ends_at <= CURRENT_TIMESTAMP) AS past,
           (SELECT count(DISTINCT offer_id) FROM flags WHERE overdue) AS overdue,
           (SELECT count(DISTINCT offer_id) FROM flags WHERE deadline_soon) AS deadline_soon,
           (SELECT count(DISTINCT offer_id) FROM flags WHERE is_full) AS full,
           (SELECT count(DISTINCT offer_id) FROM flags WHERE threshold_reached) AS threshold_reached,
           (SELECT count(DISTINCT offer_id) FROM flags WHERE revision_pending) AS revision_pending,
           (SELECT coalesce(json_agg(task ORDER BY ranked.priority, ranked.decision_deadline,
                                    ranked.offer_id, ranked.revision_number), '[]')
            FROM ranked CROSS JOIN LATERAL (
                SELECT 'reservation_review' AS kind, ranked.title, ranked.decision_deadline,
                       ranked.occupied_seats, ranked.capacity, ranked.review_threshold,
                       ranked.pending, ranked.reply_ready, ranked.overdue, ranked.deadline_soon,
                       ranked.is_full AS full, ranked.threshold_reached, ranked.revision_pending
            ) task) AS tasks
    FROM scoped
""")

_COMPANY_RESERVATIONS = text(f"""
    WITH scoped AS (
        {_SCOPED_RESERVATIONS} WHERE s.company_id = :company
    ),
    classified AS (
        SELECT *,
               clarification_event = 'clarification_requested' AS reply_needed,
               coalesce(clarification_event = 'clarification_answered', false) AS reply_ready,
               available AND status = ANY(:occupied) AND starts_at > CURRENT_TIMESTAMP AS upcoming,
               ends_at <= CURRENT_TIMESTAMP AS past
        FROM scoped
    ),
    ranked AS (
        SELECT *, row_number() OVER (
            PARTITION BY kind ORDER BY
                CASE WHEN kind = 'reply_needed' THEN decision_deadline END,
                CASE WHEN kind = 'upcoming' THEN starts_at END,
                CASE WHEN kind = 'past' THEN ends_at END DESC, id
        ) AS position
        FROM classified
        CROSS JOIN LATERAL (VALUES (1, 'reply_needed', reply_needed, 4),
                                   (2, 'upcoming', upcoming, 3),
                                   (3, 'past', past, 3)) bucket(priority, kind, visible, cap)
        WHERE bucket.visible
    )
    SELECT count(*) FILTER (WHERE reply_needed) AS reply_needed,
           count(*) FILTER (WHERE status = 'pending' OR
                                  clarification_event = 'clarification_answered') AS awaiting_decision,
           count(*) FILTER (WHERE upcoming) AS upcoming,
           count(*) FILTER (WHERE past) AS past,
           count(*) FILTER (WHERE status = 'approved') AS approved,
           count(*) FILTER (WHERE status = 'rejected') AS rejected,
           count(*) FILTER (WHERE status = 'withdrawn') AS withdrawn,
           count(*) FILTER (WHERE status = 'cancelled') AS cancelled,
           (SELECT coalesce(json_agg(task ORDER BY ranked.priority, ranked.position), '[]')
            FROM ranked CROSS JOIN LATERAL (
                SELECT ranked.kind, ranked.title, ranked.starts_at, ranked.ends_at,
                       ranked.decision_deadline, ranked.status, ranked.reply_ready, ranked.seats
            ) task WHERE ranked.position <= ranked.cap) AS tasks
    FROM classified
""")

_COACH_BUSINESS = text("""
    WITH own AS (
        SELECT o.id, r.title, r.starts_at, r.ends_at, r.decision_deadline, r.capacity, r.review_threshold,
               totals.occupied_seats, totals.open_count,
               EXISTS (SELECT 1 FROM competence_hub.calendar_offer_revisions proposed
                       WHERE proposed.offer_id = o.id AND proposed.workflow_status = 'in_review') AS in_review
        FROM competence_hub.calendar_offers o
        JOIN competence_hub.coaches c ON c.id = o.coach_id
        JOIN competence_hub.calendar_offer_revisions r ON r.offer_id = o.id
        JOIN competence_hub.topics t ON t.id = r.topic_id
        CROSS JOIN LATERAL (
            SELECT coalesce(sum(seats), 0) AS occupied_seats,
                   count(*) FILTER (WHERE status = ANY(:open)) AS open_count
            FROM competence_hub.calendar_reservations
            WHERE offer_id = o.id AND status = ANY(:occupied)
        ) totals
        WHERE c.portal_user_id = :actor AND o.lifecycle_status = 'active'
          AND r.workflow_status = 'published' AND t.active
    )
    SELECT count(*) AS published,
           count(*) FILTER (WHERE starts_at > CURRENT_TIMESTAMP) AS upcoming,
           count(*) FILTER (WHERE ends_at <= CURRENT_TIMESTAMP) AS past,
           count(*) FILTER (WHERE open_count > 0 AND decision_deadline <= CURRENT_TIMESTAMP) AS overdue,
           count(*) FILTER (WHERE open_count > 0 AND decision_deadline > CURRENT_TIMESTAMP
                               AND decision_deadline <= CURRENT_TIMESTAMP + interval '48 hours') AS deadline_soon,
           count(*) FILTER (WHERE starts_at > CURRENT_TIMESTAMP AND occupied_seats >= capacity) AS full,
           count(*) FILTER (WHERE starts_at > CURRENT_TIMESTAMP AND occupied_seats >= review_threshold) AS threshold_reached,
           count(*) FILTER (WHERE occupied_seats > 0 AND in_review) AS revision_pending,
           (SELECT coalesce(json_agg(item ORDER BY item.starts_at, item.id), '[]')
            FROM (
                SELECT id, title, starts_at, capacity, occupied_seats, review_threshold,
                       occupied_seats > 0 AND in_review AS revision_pending
                FROM own WHERE starts_at > CURRENT_TIMESTAMP ORDER BY starts_at, id LIMIT 5
            ) item) AS upcoming_offers
    FROM own
""")

_ADMIN_COUNTS = text("""
    SELECT count(*) AS accounts, count(*) FILTER (WHERE u.active) AS active,
           count(*) FILTER (WHERE NOT u.active AND NOT EXISTS (
               SELECT 1 FROM competence_hub.auth_password_credentials p WHERE p.portal_user_id = u.id
           )) AS pending_activation,
           (SELECT count(*) FROM competence_hub.companies) AS companies,
           (SELECT count(*) FROM competence_hub.company_contacts WHERE portal_user_id IS NOT NULL) AS linked_contacts
    FROM competence_hub.portal_users u
""")

_ADMIN_AUDIT = text("""
    SELECT allowed.category, a.occurred_at,
           CASE WHEN a.outcome IN ('success', 'accepted') THEN 'success'
                WHEN a.outcome IN ('denied', 'failed', 'rejected', 'rate_limited') THEN 'denied'
                ELSE 'recorded' END AS status
    FROM competence_hub.audit_events a
    JOIN (VALUES
        ('auth.initial_admin.create', 'account_access'),
        ('auth.account.set_role', 'account_access'),
        ('auth.account.enable', 'account_access'),
        ('auth.account.suspend', 'account_access'),
        ('auth.account.deactivate', 'account_access'),
        ('auth.account.revoke_invitation', 'account_activation'),
        ('auth.invitation.issue', 'account_activation'),
        ('auth.invitation.accept', 'account_activation'),
        ('auth.mfa.recovery', 'account_recovery'),
        ('auth.password_reset.confirm', 'account_recovery'),
        ('calendar.offer.published', 'calendar_publication'),
        ('calendar.offer.changes_requested', 'calendar_review'),
        ('calendar.offer.withdrawn', 'calendar_withdrawal'),
        ('calendar.reservation.clarification_requested', 'reservation_clarification'),
        ('calendar.reservation.clarification_answered', 'reservation_clarification'),
        ('calendar.reservation.approved', 'reservation_decision'),
        ('calendar.reservation.rejected', 'reservation_decision'),
        ('calendar.reservation.withdrawn', 'reservation_withdrawal'),
        ('calendar.reservation.offer_cancelled', 'reservation_withdrawal')
    ) allowed(action, category) ON allowed.action = a.action
    ORDER BY a.occurred_at DESC, a.id DESC LIMIT 8
""")


async def _one(connection, query, parameters=None):
    return dict((await connection.execute(query, parameters)).mappings().one())


async def _business_overview(connection, actor, roles):
    business = {}
    seats = {"open": list(OPEN), "occupied": list(OCCUPIED)}
    if CALENDAR_REVIEW_ROLES.intersection(roles):
        calendar = await _one(connection, _CALENDAR_REVIEW)
        reservations = await _one(connection, _REVIEW_RESERVATIONS, seats)
        tasks = calendar.pop("tasks") + reservations.pop("tasks")
        business["review"] = {"counts": {**calendar, **reservations}, "tasks": tasks}
    if BOOKER_ROLE in roles:
        try:
            # Use the reservation repository's unique contact rule in the same read snapshot.
            company = await _company(connection, actor)
        except ReservationError as error:
            if error.code != "contact_mapping":
                raise
        else:
            counts = await _one(connection, _COMPANY_RESERVATIONS, {"company": company.company_id, **seats})
            tasks = counts.pop("tasks")
            business["company"] = {"counts": counts, "tasks": tasks}
    if "coach" in roles:
        counts = await _one(connection, _COACH_BUSINESS, {"actor": actor.user_id, **seats})
        business["coach"] = {"upcoming_offers": counts.pop("upcoming_offers", []), "counts": counts}
    if "admin" in roles:
        counts = await _one(connection, _ADMIN_COUNTS)
        audit = (await connection.execute(_ADMIN_AUDIT)).mappings().all()
        business["admin"] = {"counts": counts, "audit": [dict(row) for row in audit]}
    return business


def unavailable():
    return problem_response(status=503, code="portal_unavailable", title="Übersicht derzeit nicht verfügbar")


@router.get("/api/v1/portal/pilot/overview")
async def overview(request: Request):
    origin = request.headers.get("origin")
    if (request.headers.get("sec-fetch-site") in {"cross-site", "same-site"}
            or (origin is not None and origin != getattr(request.app.state, "allowed_origin", None))):
        return _request_verification_failed()
    context = await _protected_context(request, require_csrf=False)
    if isinstance(context, Response):
        return context
    actor, _ = context
    roles = set(actor.roles)
    legacy_access = bool(roles.intersection(CALENDAR_REVIEW_ROLES | {"coach"}))
    repository = getattr(request.app.state, "reservation_repository", None)
    if not legacy_access and not (repository is not None and BOOKER_ROLE in roles):
        return problem_response(status=403, code="authorization_failed", title="Berechtigung nicht vorhanden")
    engine = getattr(request.app.state, "database_engine", None)
    if engine is None:
        return unavailable()
    async with engine.connect() as connection:
        await connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        rows, recent = [], []
        if legacy_access:
            parameters = {
                "admin": "admin" in roles, "reviewer": "calendar_reviewer" in roles,
                "coach": "coach" in roles, "actor": actor.user_id,
            }
            rows = (await connection.execute(_COUNTS, parameters)).mappings().all()
            recent = (await connection.execute(_RECENT_PUBLICATIONS, parameters)).mappings().all()
        business = await _business_overview(connection, actor, roles) if repository is not None else {}
    if not legacy_access and not business:
        return problem_response(status=403, code="authorization_failed", title="Berechtigung nicht vorhanden")
    payload = {
        "calendar": {row["status"]: row["count"] for row in rows},
        "resubmitted": sum(row["resubmitted"] for row in rows),
        "recent_publications": [dict(row) for row in recent],
        "database": "reachable",
        "scope": "authorized_current_revisions",
    }
    if business:
        payload["business"] = business
    return JSONResponse(jsonable_encoder(payload))


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
