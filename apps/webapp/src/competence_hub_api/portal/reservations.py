"""CAL-2 local slice. All seat-changing commands serialize on the CAL-1 offer row."""
from dataclasses import dataclass
import hashlib
import json
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.portal.calendar import CalendarReservationConflictError

OPEN = ("pending", "clarification")
OCCUPIED = (*OPEN, "approved")
REVIEW_ROLES = frozenset({"calendar_reviewer", "admin"})
BOOKER_ROLE = "company_contact"


@dataclass
class ReservationError(Exception):
    code: str
    status: int = 409
    field: str | None = None


_OFFER = """
    SELECT o.id, r.title, r.starts_at, r.ends_at, r.format_code, r.public_location,
           r.capacity, r.review_threshold, r.decision_deadline, r.revision_number,
           o.lifecycle_status, r.workflow_status, t.active AS active_topic
    FROM competence_hub.calendar_offers o
    JOIN competence_hub.calendar_offer_revisions r ON r.offer_id = o.id
    JOIN competence_hub.topics t ON t.id = r.topic_id
"""
_TOTAL = """
    SELECT coalesce(sum(seats) FILTER (WHERE status = ANY(:occupied)), 0) AS occupied_seats,
           coalesce(sum(seats) FILTER (WHERE status = ANY(:open)), 0) AS requested_seats
    FROM competence_hub.calendar_reservations WHERE offer_id = :offer
"""
_EVENT = """
    INSERT INTO competence_hub.calendar_reservation_events (
        reservation_id, version, actor_id, occurred_at, event, from_status, to_status,
        seats_before, seats_after, occupied_delta, threshold_reached, reason,
        request_id, request_digest
    ) VALUES (
        :id, :version, :actor, :now, :event, :before, :status,
        :old_seats, :seats, :delta, :threshold, :reason, :request, :digest
    )
"""

# Only reviewers can see the unpublished comparison. The booking still points to the old revision.
_REVISION_FIELDS = (
    "starts_at", "ends_at", "time_zone", "capacity", "review_threshold", "decision_deadline",
    "format_code", "public_location", "topic_id", "title", "summary", "price_display_text",
)
_REVISION_DIFF = "array_remove(ARRAY[" + ", ".join(
    f"CASE WHEN proposed.{field} IS DISTINCT FROM r.{field} THEN '{field}' END"
    for field in _REVISION_FIELDS
) + "], NULL)"
_DAY_FILTER = """
    AND (CAST(:day AS date) IS NULL OR (
        r.starts_at < (CAST(CAST(:day AS date) + 1 AS timestamp) AT TIME ZONE 'Europe/Berlin')
        AND r.ends_at > (CAST(:day AS timestamp) AT TIME ZONE 'Europe/Berlin')
    ))
"""
_LAST_CLARIFICATION = """
    LEFT JOIN LATERAL (
        SELECT event FROM competence_hub.calendar_reservation_events
        WHERE reservation_id = s.id AND event IN ('clarification_requested', 'clarification_answered')
        ORDER BY version DESC LIMIT 1
    ) clarification ON s.status = 'clarification'
"""


async def _rows(connection, sql, **params):
    return (await connection.execute(text(sql), params)).mappings()


async def _totals(connection, offer):
    return (await _rows(connection, _TOTAL, offer=offer, occupied=list(OCCUPIED), open=list(OPEN))).one()


async def _company(connection, actor, *, lock=False):
    if BOOKER_ROLE not in actor.roles:
        raise ReservationError("forbidden", 403)
    suffix = " FOR SHARE OF c" if lock else ""
    contacts = (await _rows(connection, """
        SELECT c.id, c.company_id, c.first_name, c.last_name, b.name
        FROM competence_hub.company_contacts c
        JOIN competence_hub.companies b ON b.id = c.company_id
        WHERE c.portal_user_id = :user ORDER BY c.id LIMIT 2
    """ + suffix, user=actor.user_id)).all()
    if len(contacts) != 1:
        raise ReservationError("contact_mapping", 403)
    return contacts[0]


def _reviewer(actor):
    if not REVIEW_ROLES.intersection(actor.roles):
        raise ReservationError("forbidden", 403)


async def _write_event(connection, **params):
    await connection.execute(text(_EVENT), params)
    await connection.execute(text("""
        INSERT INTO competence_hub.audit_events
            (actor_user_id, occurred_at, action, entity_type, entity_id, outcome)
        VALUES (:actor, :now, :action, 'calendar_reservation', :id, 'success')
    """), {**params, "action": "calendar.reservation." + params["event"]})


async def ensure_republishable(connection, offer_id):
    # The caller already holds the offer row lock. Never silently rebase agreed terms.
    if (await _totals(connection, offer_id)).occupied_seats:
        raise CalendarReservationConflictError("active reservations protect the published revision")


async def cancel_for_offer(connection, offer_id, actor, now):
    rows = await _rows(connection, """
        SELECT id, version, status, seats FROM competence_hub.calendar_reservations
        WHERE offer_id = :offer AND status = ANY(:occupied)
    """, offer=offer_id, occupied=list(OCCUPIED))
    for row in rows:
        await connection.execute(text("""
            UPDATE competence_hub.calendar_reservations SET status = 'cancelled', version = version + 1
            WHERE id = :id
        """), {"id": row.id})
        await _write_event(
            connection, id=row.id, version=row.version + 1, actor=actor, now=now,
            event="offer_cancelled", before=row.status, status="cancelled",
            old_seats=row.seats, seats=row.seats, delta=-row.seats, threshold=False,
            reason=None, request=None, digest=None,
        )


class ReservationRepository:
    def __init__(self, engine: AsyncEngine, request_key: bytes):
        self.engine = engine
        self.request_key = request_key

    async def capabilities(self, actor):
        company = None
        async with self.engine.connect() as connection:
            if BOOKER_ROLE in actor.roles:
                try:
                    contact = await _company(connection, actor)
                    company = {"name": contact.name, "contact": f"{contact.first_name} {contact.last_name}"}
                except ReservationError:
                    pass
        return {"company": company, "can_request": BOOKER_ROLE in actor.roles,
                "can_review": bool(REVIEW_ROLES.intersection(actor.roles))}

    async def catalogue(self, actor, after, *, search="", day=None):
        async with self.engine.connect() as connection:
            company = await _company(connection, actor, lock=True)
            rows = (await _rows(connection, """
                SELECT o.id, r.revision_number, r.title, t.name AS topic_name,
                       r.starts_at, r.ends_at, r.format_code, r.summary, coach.display_name AS coach_name,
                       r.public_location, r.capacity, r.decision_deadline, r.price_display_text,
                       r.capacity - coalesce(totals.seats, 0) AS free_seats,
                       coalesce(totals.has_reservation, false) AS has_reservation
                FROM competence_hub.calendar_offers o
                JOIN competence_hub.calendar_offer_revisions r ON r.offer_id = o.id
                JOIN competence_hub.topics t ON t.id = r.topic_id
                JOIN competence_hub.coaches coach ON coach.id = o.coach_id
                LEFT JOIN LATERAL (
                    SELECT sum(seats) AS seats, bool_or(company_id = :company) AS has_reservation
                    FROM competence_hub.calendar_reservations
                    WHERE offer_id = o.id AND status = ANY(:occupied)
                ) totals ON true
                WHERE o.lifecycle_status = 'active' AND r.workflow_status = 'published'
                  AND t.active AND r.decision_deadline > statement_timestamp()
                  AND (CAST(:after AS uuid) IS NULL OR o.id > :after)
                  AND (:search = '' OR strpos(lower(r.title || ' ' || t.name), lower(:search)) > 0)
            """ + _DAY_FILTER + """
                ORDER BY o.id LIMIT 26
            """, after=after, company=company.company_id, occupied=list(OCCUPIED),
                search=search, day=day)).all()
        return self._page(rows)

    async def list(self, actor, *, review, after=None, open_only=False, reservation_id=None,
                   status="", deadline="", offer="", coach="", day=None):
        if review:
            _reviewer(actor)
        elif offer or coach or deadline or status or day:
            raise ReservationError("forbidden", 403)
        async with self.engine.connect() as connection:
            company_id = None if review else (await _company(connection, actor, lock=True)).company_id
            rows = (await _rows(connection, f"""
                SELECT s.id, s.offer_id, s.revision_number, s.seats, s.status, s.version,
                       r.title, r.starts_at, r.ends_at, r.capacity, r.decision_deadline,
                       r.decision_deadline <= statement_timestamp() AS deadline_passed,
                       r.decision_deadline > statement_timestamp() AND
                         r.decision_deadline <= statement_timestamp() + interval '48 hours' AS deadline_soon,
                       coalesce(clarification.event = 'clarification_answered', false) AS clarification_answered,
                       o.lifecycle_status = 'active' AND t.active AND r.workflow_status = 'published'
                           AS offer_available,
                       CASE WHEN :review THEN presenter.display_name END AS coach_name,
                       proposed.revision_number AS proposed_revision,
                       CASE WHEN proposed.id IS NOT NULL THEN {_REVISION_DIFF} END AS changed_fields,
                       CASE WHEN :review THEN b.name ELSE NULL END AS company_name,
                       CASE WHEN :review THEN c.first_name || ' ' || c.last_name ELSE NULL END AS contact_name,
                       CASE WHEN :review THEN r.review_threshold ELSE NULL END AS review_threshold,
                       CASE WHEN CAST(:id AS uuid) IS NOT NULL AND
                           (:review OR s.requested_by = :actor) THEN s.phone ELSE NULL END AS phone,
                       CASE WHEN CAST(:id AS uuid) IS NOT NULL AND
                           (:review OR s.requested_by = :actor) THEN s.message ELSE NULL END AS message,
                       CASE WHEN :review THEN coalesce(totals.occupied_seats, 0) END AS occupied_seats,
                       totals.requested_seats, totals.open_count
                FROM competence_hub.calendar_reservations s
                JOIN competence_hub.companies b ON b.id = s.company_id
                JOIN competence_hub.company_contacts c ON c.id = s.contact_id
                JOIN competence_hub.calendar_offers o ON o.id = s.offer_id
                JOIN competence_hub.calendar_offer_revisions r
                  ON (r.offer_id, r.revision_number) = (s.offer_id, s.revision_number)
                JOIN competence_hub.topics t ON t.id = r.topic_id
                JOIN competence_hub.coaches presenter ON presenter.id = o.coach_id
                LEFT JOIN LATERAL (
                    SELECT sum(seats) AS occupied_seats,
                           coalesce(sum(seats) FILTER (WHERE status = ANY(:open)), 0) AS requested_seats,
                           count(*) FILTER (WHERE status = ANY(:open)) AS open_count
                    FROM competence_hub.calendar_reservations
                    WHERE offer_id = s.offer_id AND status = ANY(:occupied) AND :review
                ) totals ON :review
                LEFT JOIN competence_hub.calendar_offer_revisions proposed ON :review AND
                    o.lifecycle_status = 'active' AND s.status = ANY(:occupied) AND
                    proposed.offer_id = o.id AND proposed.workflow_status = 'in_review'
                {_LAST_CLARIFICATION}
                WHERE (:review OR s.company_id = CAST(:company AS uuid))
                  AND (NOT :open_only OR s.status = ANY(:open))
                  AND (CAST(:id AS uuid) IS NULL OR s.id = :id)
                  AND (CAST(:after AS uuid) IS NULL OR s.id > :after)
                  AND (:status = '' OR
                       (:status = 'open' AND s.status = ANY(:open)) OR
                       (:status = 'decision' AND (s.status = 'pending' OR
                            (s.status = 'clarification' AND clarification.event = 'clarification_answered'))) OR
                       (:status = 'past' AND r.ends_at <= statement_timestamp()) OR s.status = :status)
                  AND (:deadline = '' OR (s.status = ANY(:open) AND (
                      (:deadline = 'overdue' AND r.decision_deadline <= statement_timestamp()) OR
                      (:deadline = 'soon' AND r.decision_deadline > statement_timestamp() AND
                       r.decision_deadline <= statement_timestamp() + interval '48 hours') OR
                      (:deadline = 'later' AND r.decision_deadline > statement_timestamp() + interval '48 hours')
                  )))
                  AND (:offer = '' OR strpos(lower(r.title), lower(:offer)) > 0)
                  AND (:coach = '' OR strpos(lower(presenter.display_name), lower(:coach)) > 0)
                {_DAY_FILTER}
                ORDER BY s.id LIMIT 26
            """, review=review, company=company_id, open_only=open_only, id=reservation_id,
                after=after, actor=actor.user_id, open=list(OPEN), occupied=list(OCCUPIED),
                status=status, deadline=deadline, offer=offer, coach=coach, day=day)).all()
            result = self._page(rows)
            if reservation_id is not None:
                if not rows:
                    raise ReservationError("not_found", 404)
                item = result["items"][0]
                item["history"] = [dict(row) for row in await _rows(connection, """
                    SELECT occurred_at, event, from_status, to_status, seats_before, seats_after,
                           occupied_delta, reason, CASE WHEN :review THEN threshold_reached END AS threshold_reached
                    FROM competence_hub.calendar_reservation_events
                    WHERE reservation_id = :id AND version <= :version ORDER BY version DESC LIMIT 50
                """, id=reservation_id, review=review, version=item["version"])]
                return item
            return result

    async def activity(self, actor, *, review):
        if review:
            _reviewer(actor)
        async with self.engine.connect() as connection:
            company = None if review else (await _company(connection, actor, lock=True)).company_id
            params = {"scope": review, "company": company, "open": list(OPEN), "occupied": list(OCCUPIED)}
            # Events are observed, never copied to a second notification store.
            events = (await _rows(connection, """
                SELECT s.id AS reservation_id, s.offer_id, r.title, e.event AS kind,
                       e.version, e.occurred_at, e.seats_after
                FROM competence_hub.calendar_reservation_events e
                JOIN competence_hub.calendar_reservations s ON s.id = e.reservation_id
                JOIN competence_hub.calendar_offer_revisions r
                    ON (r.offer_id, r.revision_number) = (s.offer_id, s.revision_number)
                WHERE :scope OR s.company_id = CAST(:company AS uuid)
                ORDER BY e.occurred_at DESC, s.id, e.version DESC LIMIT 30
            """, **params)).all()
            tasks = (await _rows(connection, f"""
                WITH scoped AS (
                    SELECT s.id AS reservation_id, s.offer_id, r.title, r.decision_deadline,
                           s.status, clarification.event AS clarification_event,
                           proposed.revision_number AS proposed_revision
                    FROM competence_hub.calendar_reservations s
                    JOIN competence_hub.calendar_offers o ON o.id = s.offer_id
                    JOIN competence_hub.calendar_offer_revisions r
                        ON (r.offer_id, r.revision_number) = (s.offer_id, s.revision_number)
                    LEFT JOIN competence_hub.calendar_offer_revisions proposed ON :scope AND
                        o.lifecycle_status = 'active' AND proposed.offer_id = o.id
                        AND proposed.workflow_status = 'in_review'
                    {_LAST_CLARIFICATION}
                    WHERE s.status = ANY(:occupied) AND (:scope OR s.company_id = CAST(:company AS uuid))
                ),
                deadlines AS (
                    SELECT DISTINCT ON (offer_id) reservation_id, offer_id, title, decision_deadline,
                           CASE WHEN decision_deadline <= statement_timestamp() THEN 'overdue' ELSE 'deadline_soon' END AS kind,
                           NULL::integer AS proposed_revision
                    FROM scoped WHERE :scope AND status = ANY(:open)
                      AND decision_deadline <= statement_timestamp() + interval '48 hours'
                    ORDER BY offer_id, decision_deadline, reservation_id
                ),
                revisions AS (
                    SELECT DISTINCT ON (offer_id) reservation_id, offer_id, title, decision_deadline,
                           'revision_pending' AS kind, proposed_revision
                    FROM scoped WHERE proposed_revision IS NOT NULL
                    ORDER BY offer_id, reservation_id
                ),
                replies AS (
                    SELECT reservation_id, offer_id, title, decision_deadline,
                           'reply_needed' AS kind, NULL::integer AS proposed_revision
                    FROM scoped WHERE NOT :scope AND clarification_event = 'clarification_requested'
                )
                SELECT * FROM (TABLE deadlines UNION ALL TABLE revisions UNION ALL TABLE replies) tasks
                ORDER BY decision_deadline, offer_id, kind, reservation_id LIMIT 30
            """, **params)).all()
            return {"events": [dict(row) for row in events], "tasks": [dict(row) for row in tasks]}

    @staticmethod
    def _page(rows):
        items = [dict(row) for row in rows[:25]]
        return {"items": items, "next_after": items[-1]["id"] if len(rows) > 25 else None}

    async def command(self, actor: SessionPrincipal, *, action, target, request_id,
                      expected, review=False, seats=None, reason=None, phone=None, message=None):
        if review:
            _reviewer(actor)
        digest = hashlib.blake2b(json.dumps(
            [action, str(target), expected, seats, reason, phone, message], ensure_ascii=False
        ).encode(), key=self.request_key[:64], digest_size=32).hexdigest()
        async with self.engine.begin() as connection:
            company = None if review else await _company(connection, actor, lock=True)
            # Retry keys are actor-scoped even when conflicting requests target different offers.
            await connection.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
                                     {"key": f"cal2:{actor.user_id}:{request_id}"})
            prior = (await _rows(connection, """
                SELECT e.reservation_id, e.request_digest, s.company_id
                FROM competence_hub.calendar_reservation_events e
                JOIN competence_hub.calendar_reservations s ON s.id = e.reservation_id
                WHERE actor_id = :actor AND request_id = :request
            """, actor=actor.user_id, request=request_id)).one_or_none()
            if prior:
                if company is not None and company.company_id != prior.company_id:
                    raise ReservationError("not_found", 404)
                if prior.request_digest != digest:
                    raise ReservationError("idempotency_conflict")
                return prior.reservation_id

            if action == "submitted":
                offer_id = target
            else:
                scoped = (await _rows(connection, """
                    SELECT offer_id FROM competence_hub.calendar_reservations
                    WHERE id = :id AND (:review OR company_id = CAST(:company AS uuid))
                """, id=target, review=review, company=company.company_id if company else None)).one_or_none()
                offer_id = scoped.offer_id if scoped else None
            if offer_id is None or not (await _rows(connection, """
                SELECT id FROM competence_hub.calendar_offers WHERE id = :offer FOR UPDATE
            """, offer=offer_id)).one_or_none():
                raise ReservationError("not_found", 404)

            now = (await connection.execute(text("SELECT clock_timestamp()"))).scalar_one()
            offer = (await _rows(connection, _OFFER + """
                WHERE o.id = :offer AND r.workflow_status = 'published'
            """, offer=offer_id)).one_or_none()
            available = offer and offer.lifecycle_status == "active" and offer.active_topic
            row = None if action == "submitted" else (await _rows(connection, """
                SELECT id, version, status, seats, revision_number FROM competence_hub.calendar_reservations
                WHERE id = :id
            """, id=target)).one()
            total = (await _totals(connection, offer_id)).occupied_seats
            old_seats = row.seats if row else 0

            if row and row.version != expected:
                raise ReservationError("stale_version")
            if row and row.status not in OPEN:
                raise ReservationError("invalid_transition")
            if action == "submitted":
                if not available:
                    raise ReservationError("not_found", 404)
                if offer.revision_number != expected:
                    raise ReservationError("stale_version")
                if (await _rows(connection, """
                    SELECT id FROM competence_hub.calendar_reservations
                    WHERE offer_id = :offer AND company_id = :company AND status = ANY(:occupied)
                """, offer=offer_id, company=company.company_id, occupied=list(OCCUPIED))).first():
                    raise ReservationError("already_requested")
            if action in ("submitted", "seats_changed", "approved"):
                if not available or (row and row.revision_number != offer.revision_number):
                    raise ReservationError("invalid_transition")
            if action in ("submitted", "seats_changed"):
                if seats > old_seats and now >= offer.decision_deadline:
                    raise ReservationError("deadline")
                if action == "seats_changed" and seats == old_seats:
                    raise ReservationError("unchanged_seats", field="seats")
                if total - old_seats + seats > offer.capacity:
                    raise ReservationError("capacity", field="seats")
            if action == "approved" and now >= offer.starts_at:
                raise ReservationError("started")
            if action in ("clarification_requested", "clarification_answered") and row.status == "clarification":
                latest = (await _rows(connection, """
                    SELECT event FROM competence_hub.calendar_reservation_events
                    WHERE reservation_id = :id AND event IN ('clarification_requested', 'clarification_answered')
                    ORDER BY version DESC LIMIT 1
                """, id=target)).one_or_none()
                required = "clarification_answered" if review else "clarification_requested"
                if latest is None or latest.event != required:
                    raise ReservationError("invalid_transition")
            elif action == "clarification_answered":
                raise ReservationError("invalid_transition")

            status = {"submitted": "pending", "clarification_requested": "clarification",
                      "clarification_answered": "clarification",
                      "seats_changed": row.status if row else "pending"}.get(action, action)
            new_seats = old_seats if seats is None else seats
            delta = (new_seats if status in OCCUPIED else 0) - old_seats
            threshold = bool(available and total < offer.review_threshold <= total + delta)
            if row is None:
                reservation_id = (await _rows(connection, """
                    INSERT INTO competence_hub.calendar_reservations
                        (offer_id, revision_number, company_id, contact_id, requested_by, seats, status, phone, message)
                    VALUES (:offer, :revision, :company, :contact, :actor, :seats, :status, :phone, :message)
                    RETURNING id
                """, offer=offer_id, revision=offer.revision_number, company=company.company_id,
                    contact=company.id, actor=actor.user_id, seats=new_seats,
                    status=status, phone=phone, message=message)).one().id
                version = 1
            else:
                reservation_id, version = row.id, row.version + 1
                await connection.execute(text("""
                    UPDATE competence_hub.calendar_reservations SET status = :status, seats = :seats,
                        version = :version WHERE id = :id
                """), {"id": reservation_id, "status": status, "seats": new_seats, "version": version})
            await _write_event(
                connection, id=reservation_id, version=version, actor=actor.user_id, now=now,
                event=action, before=row.status if row else None, status=status, old_seats=old_seats,
                seats=new_seats, delta=delta, threshold=threshold, reason=reason, request=request_id, digest=digest,
            )
            return reservation_id
