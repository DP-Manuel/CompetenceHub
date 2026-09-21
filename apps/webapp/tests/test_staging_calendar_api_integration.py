from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import os
import secrets
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from competence_hub_api.auth.postgres_session_repository import (
    PostgresSessionRepository,
)
from competence_hub_api.main import create_app
from competence_hub_api.portal.calendar import CalendarService
from competence_hub_api.portal.postgres_calendar import PostgresCalendarRepository
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token

APP_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_APP_DATABASE_URL"
MIGRATOR_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL"
ALLOWED_ORIGIN = "https://staging-test.example.invalid"
CURSOR_KEY = b"synthetic-staging-calendar-cursor-key"
CALENDAR_SESSION_ROLES = frozenset(
    {"admin", "calendar_reviewer", "coach", "company_contact", "internal"}
)

pytestmark = [pytest.mark.anyio, pytest.mark.staging_integration]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@dataclass(frozen=True)
class SyntheticSession:
    token: str = field(repr=False)
    csrf_token: str = field(repr=False)


@dataclass
class CalendarApiFixture:
    app: object = field(repr=False)
    admin_engine: AsyncEngine = field(repr=False)
    now: datetime
    users: dict[str, UUID]
    sessions: dict[str, SyntheticSession] = field(repr=False)
    coaches: dict[str, UUID]
    topic_id: UUID
    offer_ids: list[UUID]


def _required_database_urls() -> tuple[str, str]:
    app_url = os.environ.get(APP_DATABASE_URL_ENV, "")
    migrator_url = os.environ.get(MIGRATOR_DATABASE_URL_ENV, "")
    if not app_url or not migrator_url:
        pytest.skip(
            "isolated staging URLs were not supplied through the process environment"
        )
    return app_url, migrator_url


async def _insert_user_and_session(
    connection,
    *,
    user_id: UUID,
    role: str,
    session: SyntheticSession,
    now: datetime,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO competence_hub.portal_users (
                id, display_name, email, active
            ) VALUES (:id, :display_name, :email, true)
            """
        ),
        {
            "id": user_id,
            "display_name": f"Synthetic Calendar {role}",
            "email": f"synthetic-calendar-api-{user_id.hex}@example.invalid",
        },
    )
    await connection.execute(
        text(
            """
            INSERT INTO competence_hub.user_roles (user_id, role_id)
            SELECT :user_id, id FROM competence_hub.roles WHERE code = :role
            """
        ),
        {"user_id": user_id, "role": role},
    )
    await connection.execute(
        text(
            """
            INSERT INTO competence_hub.auth_sessions (
                portal_user_id, token_hash, csrf_token_hash,
                created_at, authenticated_at, mfa_completed_at, last_seen_at,
                idle_expires_at, absolute_expires_at
            ) VALUES (
                :user_id, :token_hash, :csrf_token_hash,
                :now, :now, :now, :now,
                :idle_expires_at, :absolute_expires_at
            )
            """
        ),
        {
            "user_id": user_id,
            "token_hash": digest_token(session.token),
            "csrf_token_hash": digest_token(session.csrf_token),
            "now": now,
            "idle_expires_at": now + timedelta(minutes=30),
            "absolute_expires_at": now + timedelta(hours=8),
        },
    )


@pytest.fixture
async def calendar_api_fixture() -> CalendarApiFixture:
    app_url, migrator_url = _required_database_urls()
    app_engine = create_async_engine(app_url, pool_pre_ping=True, hide_parameters=True)
    admin_engine = create_async_engine(
        migrator_url, pool_pre_ping=True, hide_parameters=True
    )
    roles = ("coach", "coach_two", "calendar_reviewer", "admin", "internal", "company_contact")
    users = {role: uuid4() for role in roles}
    sessions = {
        role: SyntheticSession(secrets.token_urlsafe(32), secrets.token_urlsafe(32))
        for role in roles
    }
    coaches = {"coach": uuid4(), "coach_two": uuid4()}
    topic_id = uuid4()
    offer_ids: list[UUID] = []

    try:
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            database_now = await connection.scalar(text("SELECT clock_timestamp()"))
            assert isinstance(database_now, datetime)
            now = database_now.astimezone(UTC)
            for key, role in (
                ("coach", "coach"),
                ("coach_two", "coach"),
                ("calendar_reviewer", "calendar_reviewer"),
                ("admin", "admin"),
                ("internal", "internal"),
                ("company_contact", "company_contact"),
            ):
                await _insert_user_and_session(
                    connection,
                    user_id=users[key],
                    role=role,
                    session=sessions[key],
                    now=now,
                )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.coaches (
                        id, portal_user_id, display_name, public_profile_status,
                        public_profile_path
                    ) VALUES
                        (:coach_one, :user_one, 'Synthetic Coach One', 'synthetic',
                         '/coaches/synthetic-one/'),
                        (:coach_two, :user_two, 'Synthetic Coach Two', 'synthetic',
                         NULL)
                    """
                ),
                {
                    "coach_one": coaches["coach"],
                    "user_one": users["coach"],
                    "coach_two": coaches["coach_two"],
                    "user_two": users["coach_two"],
                },
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.topics (id, name, active)
                    VALUES (:id, :name, true)
                    """
                ),
                {"id": topic_id, "name": f"Synthetic API {uuid4().hex}"},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.coach_topics (coach_id, topic_id)
                    VALUES (:coach_one, :topic_id), (:coach_two, :topic_id)
                    """
                ),
                {
                    "coach_one": coaches["coach"],
                    "coach_two": coaches["coach_two"],
                    "topic_id": topic_id,
                },
            )

        app = create_app(
            session_repository=PostgresSessionRepository(app_engine),
            calendar_session_repository=PostgresSessionRepository(
                app_engine,
                accepted_roles=CALENDAR_SESSION_ROLES,
            ),
            calendar_service=CalendarService(PostgresCalendarRepository(app_engine)),
            calendar_cursor_hmac_key=CURSOR_KEY,
            allowed_origin=ALLOWED_ORIGIN,
            clock=lambda: now,
        )
        yield CalendarApiFixture(
            app=app,
            admin_engine=admin_engine,
            now=now,
            users=users,
            sessions=sessions,
            coaches=coaches,
            topic_id=topic_id,
            offer_ids=offer_ids,
        )
    finally:
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await connection.execute(
                text(
                    "DELETE FROM competence_hub.audit_events "
                    "WHERE actor_user_id = ANY(:user_ids)"
                ),
                {"user_ids": list(users.values())},
            )
            await connection.execute(
                text(
                    """
                    DELETE FROM competence_hub.calendar_review_decisions
                    WHERE revision_id IN (
                        SELECT revision.id
                        FROM competence_hub.calendar_offer_revisions AS revision
                        JOIN competence_hub.calendar_offers AS offer
                          ON offer.id = revision.offer_id
                        WHERE offer.created_by_user_id = ANY(:user_ids)
                    )
                    """
                ),
                {"user_ids": list(users.values())},
            )
            await connection.execute(
                text(
                    """
                    DELETE FROM competence_hub.calendar_offer_revisions
                    WHERE offer_id IN (
                        SELECT id FROM competence_hub.calendar_offers
                        WHERE created_by_user_id = ANY(:user_ids)
                    )
                    """
                ),
                {"user_ids": list(users.values())},
            )
            await connection.execute(
                text(
                    "DELETE FROM competence_hub.calendar_offers "
                    "WHERE created_by_user_id = ANY(:user_ids)"
                ),
                {"user_ids": list(users.values())},
            )
            await connection.execute(
                text(
                    "DELETE FROM competence_hub.coach_topics "
                    "WHERE coach_id = ANY(:coach_ids)"
                ),
                {"coach_ids": list(coaches.values())},
            )
            await connection.execute(
                text("DELETE FROM competence_hub.topics WHERE id = :topic_id"),
                {"topic_id": topic_id},
            )
            await connection.execute(
                text("DELETE FROM competence_hub.coaches WHERE id = ANY(:coach_ids)"),
                {"coach_ids": list(coaches.values())},
            )
            await connection.execute(
                text("DELETE FROM competence_hub.portal_users WHERE id = ANY(:user_ids)"),
                {"user_ids": list(users.values())},
            )
        async with admin_engine.connect() as connection:
            residue = await connection.scalar(
                text(
                    """
                    SELECT
                        (SELECT count(*) FROM competence_hub.portal_users
                         WHERE id = ANY(:user_ids))
                      + (SELECT count(*) FROM competence_hub.auth_sessions
                         WHERE portal_user_id = ANY(:user_ids))
                      + (SELECT count(*) FROM competence_hub.user_roles
                         WHERE user_id = ANY(:user_ids))
                      + (SELECT count(*) FROM competence_hub.coaches
                         WHERE id = ANY(:coach_ids))
                      + (SELECT count(*) FROM competence_hub.topics
                         WHERE id = :topic_id)
                      + (SELECT count(*) FROM competence_hub.calendar_offers
                         WHERE created_by_user_id = ANY(:user_ids))
                      + (SELECT count(*) FROM competence_hub.audit_events
                         WHERE actor_user_id = ANY(:user_ids))
                    """
                ),
                {
                    "user_ids": list(users.values()),
                    "coach_ids": list(coaches.values()),
                    "topic_id": topic_id,
                },
            )
            assert residue == 0
        await app_engine.dispose()
        await admin_engine.dispose()


def _set_session(
    client: AsyncClient, fixture: CalendarApiFixture, role: str
) -> SyntheticSession:
    session = fixture.sessions[role]
    client.cookies.delete(SESSION_COOKIE_NAME)
    client.cookies.set(SESSION_COOKIE_NAME, session.token)
    return session


def _headers(session: SyntheticSession, *, version: int | None = None) -> dict[str, str]:
    headers = {"Origin": ALLOWED_ORIGIN, "X-CSRF-Token": session.csrf_token}
    if version is not None:
        headers["If-Match"] = f'"v{version}"'
    return headers


def _draft(
    fixture: CalendarApiFixture,
    *,
    start: datetime,
    title: str,
) -> dict[str, object]:
    return {
        "topic_id": str(fixture.topic_id),
        "title": title,
        "summary": "Synthetic staging calendar API data only",
        "starts_at": start.isoformat(),
        "ends_at": (start + timedelta(hours=2)).isoformat(),
        "time_zone": "Europe/Berlin",
        "format": "praesenz",
        "public_location": "Synthetic location",
        "capacity": 30,
        "review_threshold": 10,
        "decision_deadline": (start - timedelta(days=2)).isoformat(),
        "price_display_text": "Synthetic price",
    }


async def _create(
    client: AsyncClient,
    fixture: CalendarApiFixture,
    session: SyntheticSession,
    *,
    start: datetime,
    title: str,
    coach_id: UUID | None = None,
    request_id: UUID | None = None,
) -> tuple[dict[str, object], UUID]:
    request_id = request_id or uuid4()
    payload: dict[str, object] = {
        "client_request_id": str(request_id),
        "draft": _draft(fixture, start=start, title=title),
    }
    if coach_id is not None:
        payload["coach_id"] = str(coach_id)
    response = await client.post(
        "/api/v1/portal/calendar/offers",
        json=payload,
        headers=_headers(session),
    )
    assert response.status_code == 201, response.text
    offer_id = UUID(response.json()["id"])
    fixture.offer_ids.append(offer_id)
    return payload, offer_id


async def _publish(
    client: AsyncClient,
    fixture: CalendarApiFixture,
    *,
    offer_id: UUID,
    owner_role: str,
    version: int = 1,
) -> dict[str, object]:
    owner = _set_session(client, fixture, owner_role)
    submitted = await client.post(
        f"/api/v1/portal/calendar/offers/{offer_id}/submit",
        headers=_headers(owner, version=version),
    )
    assert submitted.status_code == 200, submitted.text
    reviewer = _set_session(client, fixture, "calendar_reviewer")
    published = await client.post(
        f"/api/v1/portal/calendar/offers/{offer_id}/review-decisions",
        json={"outcome": "published", "note": None},
        headers=_headers(reviewer, version=version + 1),
    )
    assert published.status_code == 200, published.text
    return published.json()


async def test_staging_protected_calendar_api_security_workflow_and_conflicts(
    calendar_api_fixture: CalendarApiFixture,
) -> None:
    fixture = calendar_api_fixture
    start = fixture.now + timedelta(days=20)
    async with AsyncClient(
        transport=ASGITransport(app=fixture.app), base_url=ALLOWED_ORIGIN
    ) as client:
        unauthenticated = await client.get("/api/v1/portal/calendar/offers")
        client.cookies.set(SESSION_COOKIE_NAME, secrets.token_urlsafe(32))
        pre_mfa = await client.get("/api/v1/portal/calendar/offers")
        for role in ("internal", "company_contact"):
            _set_session(client, fixture, role)
            denied = await client.get("/api/v1/portal/calendar/offers")
            assert denied.status_code == 403

        coach = _set_session(client, fixture, "coach")
        payload = {
            "client_request_id": str(uuid4()),
            "draft": _draft(fixture, start=start, title="Synthetic protected"),
        }
        bad_origin = await client.post(
            "/api/v1/portal/calendar/offers",
            json=payload,
            headers={**_headers(coach), "Origin": "https://attacker.example.invalid"},
        )
        bad_csrf = await client.post(
            "/api/v1/portal/calendar/offers",
            json=payload,
            headers={**_headers(coach), "X-CSRF-Token": "wrong"},
        )
        unknown_field = await client.post(
            "/api/v1/portal/calendar/offers",
            json={**payload, "public_profile_path": "/coaches/forbidden/"},
            headers=_headers(coach),
        )
        oversized = await client.post(
            "/api/v1/portal/calendar/offers",
            content=b"{" + (b'\"padding\":\"x\",' * 3000) + b"}",
            headers={**_headers(coach), "Content-Type": "application/json"},
        )

        request_id = uuid4()
        create_payload, offer_id = await _create(
            client,
            fixture,
            coach,
            start=start,
            title="Synthetic protected",
            request_id=request_id,
        )
        retry = await client.post(
            "/api/v1/portal/calendar/offers",
            json=create_payload,
            headers=_headers(coach),
        )
        own_list = await client.get("/api/v1/portal/calendar/offers")
        coach_two = _set_session(client, fixture, "coach_two")
        foreign = await client.get(f"/api/v1/portal/calendar/offers/{offer_id}")
        coach = _set_session(client, fixture, "coach")
        stale = await client.patch(
            f"/api/v1/portal/calendar/offers/{offer_id}/draft",
            json=_draft(fixture, start=start, title="Synthetic changed"),
            headers=_headers(coach, version=99),
        )
        changed = await client.patch(
            f"/api/v1/portal/calendar/offers/{offer_id}/draft",
            json=_draft(fixture, start=start, title="Synthetic changed"),
            headers=_headers(coach, version=1),
        )
        submitted = await client.post(
            f"/api/v1/portal/calendar/offers/{offer_id}/submit",
            headers=_headers(coach, version=2),
        )
        reviewer = _set_session(client, fixture, "calendar_reviewer")
        queue = await client.get("/api/v1/portal/calendar/review-queue")
        changes_requested = await client.post(
            f"/api/v1/portal/calendar/offers/{offer_id}/review-decisions",
            json={"outcome": "changes_requested", "note": "Synthetic correction"},
            headers=_headers(reviewer, version=3),
        )
        coach = _set_session(client, fixture, "coach")
        revised = await client.patch(
            f"/api/v1/portal/calendar/offers/{offer_id}/draft",
            json=_draft(fixture, start=start, title="Synthetic revision two"),
            headers=_headers(coach, version=4),
        )
        resubmitted = await client.post(
            f"/api/v1/portal/calendar/offers/{offer_id}/submit",
            headers=_headers(coach, version=5),
        )
        reviewer = _set_session(client, fixture, "calendar_reviewer")
        published = await client.post(
            f"/api/v1/portal/calendar/offers/{offer_id}/review-decisions",
            json={"outcome": "published", "note": None},
            headers=_headers(reviewer, version=6),
        )

        coach = _set_session(client, fixture, "coach")
        _, adjacent_id = await _create(
            client,
            fixture,
            coach,
            start=start + timedelta(hours=2),
            title="Synthetic adjacent",
        )
        adjacent_submit = await client.post(
            f"/api/v1/portal/calendar/offers/{adjacent_id}/submit",
            headers=_headers(coach, version=1),
        )
        _, overlap_id = await _create(
            client,
            fixture,
            coach,
            start=start + timedelta(hours=1),
            title="Synthetic overlap",
        )
        overlap_submit = await client.post(
            f"/api/v1/portal/calendar/offers/{overlap_id}/submit",
            headers=_headers(coach, version=1),
        )
        admin = _set_session(client, fixture, "admin")
        _, other_coach_offer_id = await _create(
            client,
            fixture,
            admin,
            coach_id=fixture.coaches["coach_two"],
            start=start,
            title="Synthetic other coach",
        )
        other_submit = await client.post(
            f"/api/v1/portal/calendar/offers/{other_coach_offer_id}/submit",
            headers=_headers(admin, version=1),
        )
        admin_list = await client.get(
            "/api/v1/portal/calendar/offers",
            params={"coach_id": str(fixture.coaches["coach"])},
        )
        withdrawn = await client.post(
            f"/api/v1/portal/calendar/offers/{adjacent_id}/withdraw",
            headers=_headers(admin, version=2),
        )

    assert unauthenticated.status_code == 401
    assert pre_mfa.status_code == 401
    assert [bad_origin.status_code, bad_csrf.status_code] == [403, 403]
    assert [unknown_field.status_code, oversized.status_code] == [400, 400]
    assert retry.status_code == 201 and retry.json()["id"] == str(offer_id)
    assert own_list.status_code == 200
    assert own_list.headers["Cache-Control"] == "no-store"
    assert foreign.status_code == 404
    assert stale.status_code == 409
    assert changed.headers["ETag"] == '"v2"'
    assert submitted.json()["current_revision"]["workflow_status"] == "in_review"
    assert queue.status_code == 200 and queue.json()["items"]
    assert changes_requested.json()["review_decision"]["note"] == "Synthetic correction"
    assert revised.json()["current_revision"]["revision_number"] == 2
    assert resubmitted.status_code == 200
    assert published.json()["current_revision"]["workflow_status"] == "published"
    assert adjacent_submit.status_code == 200
    assert overlap_submit.status_code == 409
    assert overlap_submit.json()["code"] == "calendar_time_conflict"
    assert other_submit.status_code == 200
    assert admin_list.status_code == 200
    assert withdrawn.json()["lifecycle_status"] == "withdrawn"

    async with fixture.admin_engine.connect() as connection:
        audit_columns = tuple(
            (
                await connection.execute(
                    text(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = 'competence_hub'
                          AND table_name = 'audit_events'
                        ORDER BY ordinal_position
                        """
                    )
                )
            ).scalars()
        )
    assert audit_columns == (
        "id",
        "actor_user_id",
        "occurred_at",
        "action",
        "entity_type",
        "entity_id",
        "outcome",
    )


async def test_staging_public_calendar_api_is_published_only_minimized_and_signed(
    calendar_api_fixture: CalendarApiFixture,
) -> None:
    fixture = calendar_api_fixture
    first_start = fixture.now + timedelta(days=10)
    second_start = fixture.now + timedelta(days=11)
    async with AsyncClient(
        transport=ASGITransport(app=fixture.app), base_url=ALLOWED_ORIGIN
    ) as client:
        coach = _set_session(client, fixture, "coach")
        _, first_id = await _create(
            client,
            fixture,
            coach,
            start=first_start,
            title="Synthetic published one",
        )
        first_publication = await _publish(
            client, fixture, offer_id=first_id, owner_role="coach"
        )
        coach = _set_session(client, fixture, "coach")
        next_draft = await client.patch(
            f"/api/v1/portal/calendar/offers/{first_id}/draft",
            json=_draft(
                fixture,
                start=first_start,
                title="Synthetic unpublished replacement",
            ),
            headers=_headers(coach, version=3),
        )

        admin = _set_session(client, fixture, "admin")
        _, second_id = await _create(
            client,
            fixture,
            admin,
            coach_id=fixture.coaches["coach_two"],
            start=second_start,
            title="Synthetic published two",
        )
        await _publish(client, fixture, offer_id=second_id, owner_role="admin")

        coach = _set_session(client, fixture, "coach")
        _, draft_id = await _create(
            client,
            fixture,
            coach,
            start=fixture.now + timedelta(days=15),
            title="Synthetic hidden draft",
        )
        _, review_id = await _create(
            client,
            fixture,
            coach,
            start=fixture.now + timedelta(days=16),
            title="Synthetic hidden review",
        )
        review_submit = await client.post(
            f"/api/v1/portal/calendar/offers/{review_id}/submit",
            headers=_headers(coach, version=1),
        )

        params = {
            "from": fixture.now.isoformat(),
            "to": (fixture.now + timedelta(days=30)).isoformat(),
            "limit": 1,
        }
        first_page = await client.get("/api/v1/calendar/offers", params=params)
        cursor = first_page.json()["next_cursor"]
        second_page = await client.get(
            "/api/v1/calendar/offers", params={**params, "cursor": cursor}
        )
        tampered = f"{'A' if cursor[0] != 'A' else 'B'}{cursor[1:]}"
        bad_cursor = await client.get(
            "/api/v1/calendar/offers", params={**params, "cursor": tampered}
        )
        bad_window = await client.get(
            "/api/v1/calendar/offers",
            params={
                "from": fixture.now.isoformat(),
                "to": (fixture.now + timedelta(days=100)).isoformat(),
            },
        )
        too_large = await client.get(
            "/api/v1/calendar/offers", params={**params, "limit": 101}
        )
        detail = await client.get(f"/api/v1/calendar/offers/{first_id}")
        unknown = await client.get(f"/api/v1/calendar/offers/{uuid4()}")

    assert first_publication["current_revision"]["workflow_status"] == "published"
    assert next_draft.json()["current_revision"]["workflow_status"] == "draft"
    assert review_submit.status_code == 200
    items = first_page.json()["items"] + second_page.json()["items"]
    assert {item["id"] for item in items} == {str(first_id), str(second_id)}
    by_id = {item["id"]: item for item in items}
    assert by_id[str(first_id)]["title"] == "Synthetic published one"
    assert by_id[str(first_id)]["coach"]["profile_path"] == "/coaches/synthetic-one/"
    assert by_id[str(second_id)]["coach"]["profile_path"] is None
    assert str(draft_id) not in by_id and str(review_id) not in by_id
    forbidden = {
        "coach_id",
        "portal_user_id",
        "reviewer_user_id",
        "review_threshold",
        "review_decision",
        "internal_notes",
        "audit_events",
        "client_request_id",
        "lock_version",
    }
    for item in items:
        assert forbidden.isdisjoint(item)
        assert forbidden.isdisjoint(item["coach"])
    assert first_page.headers["Cache-Control"] == "no-store"
    assert len(first_page.json()["items"]) == 1
    assert bad_cursor.status_code == 400
    assert bad_window.status_code == 400
    assert too_large.status_code == 422
    assert detail.status_code == 200
    assert detail.json()["title"] == "Synthetic published one"
    assert set(detail.json()) == set(items[0])
    assert unknown.status_code == 404
    assert unknown.json()["code"] == "calendar_offer_not_found"
