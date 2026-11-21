"""Business Operations on the portal's original coaching requests, independent of CAL-2."""

from contextlib import asynccontextmanager
from typing import Literal
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.session_repository import SessionPrincipal

MANAGER_ROLES = frozenset({"admin", "internal", "calendar_reviewer"})
RequestStatus = Literal["open", "in_progress", "waiting", "closed"]
OptionBucket = Literal["companies", "private_customers", "services", "offers", "coaches", "responsible_users"]
Scope = Literal["internal", "coach", "company"]
HISTORY_LIMIT = 50
MAX_VERSION = 2_147_483_647

_FIELDS = (
    "subject", "description", "status", "company_id", "private_customer_id",
    "service_id", "offer_id", "coach_id", "responsible_user_id", "follow_up_on",
    "desired_period", "preferred_format", "coach_summary",
)
_INTERNAL_LIST = ", ".join(
    f"r.{field}" for field in ("id", "version", "created_at", "updated_at", *_FIELDS)
    if field not in {"description", "coach_summary"}
)
_PROJECTIONS = {
    "internal": _INTERNAL_LIST,
    "company": "r.id, r.subject, r.status, r.created_at, r.company_id",
    "coach": "r.id, r.coach_summary",
}
_PREDICATES = {
    "internal": "true",
    "company": "r.company_id = :scope_id",
    "coach": """
        r.coach_id = :scope_id AND (
            r.coach_summary IS NOT NULL OR EXISTS (
                SELECT 1 FROM competence_hub.coaching_request_notes n
                WHERE n.request_id = r.id AND n.coach_release_id = r.coach_release_id
                  AND n.visibility = 'coach'
            )
        )
    """,
}
_OPTION_SOURCES = {
    "companies": ("p.name", "competence_hub.companies p", "true"),
    "private_customers": ("p.first_name || ' ' || p.last_name", "competence_hub.private_customers p", "true"),
    "services": ("p.name", "competence_hub.services p", "p.active"),
    "offers": ("revision.title", """
        competence_hub.calendar_offers p
        JOIN LATERAL (
            SELECT title FROM competence_hub.calendar_offer_revisions
            WHERE offer_id = p.id ORDER BY revision_number DESC LIMIT 1
        ) AS revision ON true""", "p.lifecycle_status = 'active'"),
    "coaches": ("p.display_name", "competence_hub.coaches p", "true"),
    "responsible_users": ("p.display_name", "competence_hub.portal_users p", """
        p.active AND EXISTS (
            SELECT 1 FROM competence_hub.user_roles ur
            JOIN competence_hub.roles role ON role.id = ur.role_id
            WHERE ur.user_id = p.id AND role.active
              AND role.code IN ('admin', 'internal', 'calendar_reviewer')
        )"""),
}
_REFERENCES = {
    "company_id": "companies", "private_customer_id": "private_customers",
    "service_id": "services", "offer_id": "offers", "coach_id": "coaches",
    "responsible_user_id": "responsible_users",
}


class RequestError(Exception):
    def __init__(self, code: str, status: int, field: str | None = None) -> None:
        super().__init__(code)
        self.status = status
        self.code = code
        self.field = field


def require_manager(actor: SessionPrincipal) -> None:
    if not MANAGER_ROLES.intersection(actor.roles):
        raise RequestError("request_forbidden", 403)


def _page(rows, limit: int) -> dict:
    return {
        "items": [dict(row) for row in rows[:limit]],
        "next_after": rows[limit - 1]["id"] if len(rows) > limit else None,
    }


async def _rows(connection, statement, **params):
    return (await connection.execute(text(statement), params)).mappings()


async def _scope(connection, actor: SessionPrincipal) -> tuple[Scope | None, UUID | None]:
    if MANAGER_ROLES.intersection(actor.roles):
        return "internal", None
    if "coach" in actor.roles:
        coach_id = await connection.scalar(text("""
            SELECT id FROM competence_hub.coaches WHERE portal_user_id = :actor
        """), {"actor": actor.user_id})
        return ("coach", coach_id) if coach_id is not None else (None, None)
    if "company_contact" in actor.roles:
        # Match CAL-2's fail-closed policy for missing or ambiguous contact mappings.
        mappings = (await connection.execute(text("""
            SELECT company_id FROM competence_hub.company_contacts
            WHERE portal_user_id = :actor LIMIT 2
        """), {"actor": actor.user_id})).scalars().all()
        if len(mappings) == 1:
            return "company", mappings[0]
    return None, None


def _require_scope(scope: Scope | None) -> Scope:
    if scope is None:
        raise RequestError("request_forbidden", 403)
    return scope


async def _validate_changes(connection, candidate, changes) -> None:
    if (candidate["company_id"] is None) == (candidate["private_customer_id"] is None):
        raise RequestError("request_customer_required", 400, "company_id")
    if candidate["service_id"] is not None and candidate["offer_id"] is not None:
        raise RequestError("request_offer_exclusive", 400, "offer_id")
    if candidate["coach_id"] is None and candidate["coach_summary"] is not None:
        raise RequestError("request_coach_required", 400, "coach_summary")
    for field, bucket in _REFERENCES.items():
        if field not in changes:
            continue
        target = candidate[field]
        if target is None:
            continue
        _, source, condition = _OPTION_SOURCES[bucket]
        if await connection.scalar(text(f"""
            SELECT 1 FROM {source} WHERE p.id = :target AND ({condition})
        """), {"target": target}) is None:
            raise RequestError("request_invalid_reference", 400, field)


async def _event(connection, actor, item, action, fields, now) -> None:
    await connection.execute(text("""
        INSERT INTO competence_hub.coaching_request_events
            (request_id, version, actor_user_id, action, changed_fields, occurred_at)
        VALUES (:id, :version, :actor, :action, CAST(:fields AS text[]), :now)
    """), {"id": item["id"], "version": item["version"], "actor": actor.user_id,
           "action": action, "fields": sorted(fields), "now": now})


async def _lock_current(connection, request_id, version) -> dict:
    current = (await _rows(connection, f"""
        SELECT id, version, coach_release_id, {", ".join(_FIELDS)}
        FROM competence_hub.coaching_requests WHERE id = :id FOR UPDATE
    """, id=request_id)).one_or_none()
    if current is None:
        raise RequestError("request_not_found", 404)
    if current["version"] != version:
        raise RequestError("request_version_conflict", 409)
    return dict(current)


async def _detail(connection, scope: Scope, scope_id, request_id) -> dict:
    extra = ", r.description, r.coach_summary, r.created_by_user_id" if scope == "internal" else ""
    # Release token is needed for the scoped note query, never for response serialization.
    if scope == "coach":
        extra = ", r.coach_release_id"
    row = (await _rows(connection, f"""
        SELECT {_PROJECTIONS[scope]}{extra}
        FROM competence_hub.coaching_requests r
        WHERE r.id = :id AND ({_PREDICATES[scope]})
    """, id=request_id, scope_id=scope_id)).one_or_none()
    if row is None:
        raise RequestError("request_not_found", 404)
    item = dict(row)
    if scope == "company":
        return item

    columns = "id, body, created_at"
    note_scope = ""
    release_id = None
    if scope == "internal":
        columns += ", visibility, author_user_id"
    else:
        release_id = item.pop("coach_release_id")
        note_scope = "AND visibility = 'coach' AND coach_release_id = :release_id"
    notes = (await _rows(connection, f"""
        SELECT {columns} FROM competence_hub.coaching_request_notes
        WHERE request_id = :id {note_scope}
        ORDER BY request_version DESC LIMIT :limit
    """, id=request_id, release_id=release_id, limit=HISTORY_LIMIT + 1)).all()
    item.update(notes=[dict(note) for note in notes[:HISTORY_LIMIT]], has_more_notes=len(notes) > HISTORY_LIMIT)
    if scope == "internal":
        events = (await _rows(connection, """
            SELECT version, action, changed_fields, actor_user_id, occurred_at
            FROM competence_hub.coaching_request_events
            WHERE request_id = :id ORDER BY version DESC LIMIT :limit
        """, id=request_id, limit=HISTORY_LIMIT + 1)).all()
        item.update(audit=[dict(event) for event in events[:HISTORY_LIMIT]], has_more_audit=len(events) > HISTORY_LIMIT)
    return item


class CoachingRequestRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @asynccontextmanager
    async def _read(self):
        # Mapping, base row and its scoped notes must describe one database snapshot.
        async with self._engine.begin() as connection:
            await connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
            yield connection

    async def capabilities(self, actor: SessionPrincipal) -> dict:
        async with self._read() as connection:
            scope, _ = await _scope(connection, actor)
        return {"enabled": True, "can_read": scope is not None, "can_manage": scope == "internal", "scope": scope}

    async def options(self, actor: SessionPrincipal, *, bucket: OptionBucket, after: UUID | None, limit: int) -> dict:
        require_manager(actor)
        label, source, condition = _OPTION_SOURCES[bucket]
        async with self._read() as connection:
            rows = (await _rows(connection, f"""
                SELECT p.id, left({label}, 201) AS label FROM {source}
                WHERE ({condition}) AND (CAST(:after AS uuid) IS NULL OR p.id > :after)
                ORDER BY p.id LIMIT :take
            """, after=after, take=limit + 1)).all()
        return _page(rows, limit)

    async def list(self, actor: SessionPrincipal, *, status: RequestStatus | None, after: UUID | None, limit: int) -> dict:
        async with self._read() as connection:
            scope, scope_id = await _scope(connection, actor)
            scope = _require_scope(scope)
            # Applying a hidden status filter to the coach projection would reveal status.
            if scope == "coach" and status is not None:
                raise RequestError("request_forbidden", 403)
            rows = (await _rows(connection, f"""
                SELECT {_PROJECTIONS[scope]} FROM competence_hub.coaching_requests r
                WHERE ({_PREDICATES[scope]})
                  AND (CAST(:after AS uuid) IS NULL OR r.id > :after)
                  AND (CAST(:status AS text) IS NULL OR r.status = :status)
                ORDER BY r.id LIMIT :take
            """, after=after, status=status, scope_id=scope_id, take=limit + 1)).all()
        return _page(rows, limit)

    async def detail(self, actor: SessionPrincipal, request_id: UUID) -> dict:
        async with self._read() as connection:
            scope, scope_id = await _scope(connection, actor)
            return await _detail(connection, _require_scope(scope), scope_id, request_id)

    async def create(self, actor: SessionPrincipal, data: dict, now) -> dict:
        require_manager(actor)
        values = {field: data[field] for field in _FIELDS}
        release_id = uuid4() if values["coach_id"] is not None else None
        async with self._engine.begin() as connection:
            await _validate_changes(connection, values, values)
            item = (await _rows(connection, f"""
                INSERT INTO competence_hub.coaching_requests
                    ({", ".join(_FIELDS)}, coach_release_id, created_by_user_id)
                VALUES ({", ".join(":" + field for field in _FIELDS)}, :release_id, :actor)
                RETURNING id, version
            """, **values, release_id=release_id, actor=actor.user_id)).one()
            await _event(connection, actor, item, "created", [key for key, value in values.items() if value is not None], now)
            return await _detail(connection, "internal", None, item["id"])

    async def update(self, actor: SessionPrincipal, request_id: UUID, version: int, changes: dict, now) -> dict:
        require_manager(actor)
        async with self._engine.begin() as connection:
            current = await _lock_current(connection, request_id, version)
            changes = {field: changes[field] for field in _FIELDS if field in changes and current[field] != changes[field]}
            for field in ("company_id", "private_customer_id"):
                if field in changes:
                    raise RequestError("request_customer_immutable", 400, field)
            release_changed = "coach_id" in changes
            if release_changed and "coach_summary" not in changes and current["coach_summary"] is not None:
                changes["coach_summary"] = None
            candidate = current | changes
            await _validate_changes(connection, candidate, changes)
            if changes:
                writes = dict(changes)
                if release_changed:
                    writes["coach_release_id"] = uuid4() if candidate["coach_id"] is not None else None
                item = await self._update_row(connection, request_id, version, writes)
                await _event(connection, actor, item, "updated", changes, now)
            return await _detail(connection, "internal", None, request_id)

    async def add_note(self, actor: SessionPrincipal, request_id: UUID, version: int, visibility: str, body: str, now) -> dict:
        require_manager(actor)
        async with self._engine.begin() as connection:
            current = await _lock_current(connection, request_id, version)
            release_id = current["coach_release_id"] if visibility == "coach" else None
            if visibility == "coach" and release_id is None:
                raise RequestError("request_coach_required", 400, "visibility")
            item = await self._update_row(connection, request_id, version, {})
            await connection.execute(text("""
                INSERT INTO competence_hub.coaching_request_notes
                    (request_id, request_version, author_user_id, visibility, body, coach_release_id, created_at)
                VALUES (:id, :version, :actor, :visibility, :body, :release_id, :now)
            """), {"id": request_id, "version": item["version"], "actor": actor.user_id,
                   "visibility": visibility, "body": body, "release_id": release_id, "now": now})
            await _event(connection, actor, item, "note_added", ["notes"], now)
            return await _detail(connection, "internal", None, request_id)

    async def _update_row(self, connection, request_id, version, writes):
        if version >= MAX_VERSION:
            raise RequestError("request_version_exhausted", 409)
        assignments = ", ".join([*(f"{key} = :{key}" for key in writes), "version = version + 1"])
        return (await _rows(connection, f"""
            UPDATE competence_hub.coaching_requests SET {assignments}
            WHERE id = :id AND version = :expected RETURNING id, version
        """, **writes, id=request_id, expected=version)).one()
