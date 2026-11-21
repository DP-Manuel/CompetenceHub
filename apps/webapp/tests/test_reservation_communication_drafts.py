from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
import pytest

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.portal.reservations import ReservationRepository
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token


BASE = "/api/v1/portal/reservations"
DRAFTS = BASE + "/communication-drafts"
NOW = datetime(2026, 11, 21, 12, tzinfo=UTC)
SESSION = "synthetic-caldrafts-session"
COMPANY_A, COMPANY_B = UUID(int=1), UUID(int=2)
RESERVATION_A, RESERVATION_B = UUID(int=3), UUID(int=4)
OFFER = UUID(int=5)
ACTOR = UUID(int=6)


class Rows(list):
    def mappings(self):
        return self

    def all(self):
        return self


class Row(dict):
    __getattr__ = dict.__getitem__


def event(company, reservation, version, kind="submitted"):
    return company, Row(
        reservation_id=reservation, offer_id=OFFER, version=version, kind=kind,
        occurred_at=NOW, title="Synthetic title not included in drafts", seats_after=2,
    )


class ReadOnlyEngine:
    def __init__(self, contacts=(), events=()):
        self.contacts = contacts
        self.events = events
        self.reads = []

    @asynccontextmanager
    async def connect(self):
        yield self

    async def execute(self, statement, params):
        sql = " ".join(str(statement).split())
        assert sql.startswith(("SELECT ", "WITH scoped AS ("))
        if "FROM competence_hub.company_contacts c" in sql:
            assert "WHERE c.portal_user_id = :user" in sql
            assert "FOR SHARE OF c" in sql
            assert params == {"user": ACTOR}
            self.reads.append("mapping")
            return Rows(Row(company_id=company) for company in self.contacts)
        if sql.startswith("WITH scoped AS ("):
            self.reads.append("tasks")
            return Rows()
        assert "FROM competence_hub.calendar_reservation_events e" in sql
        assert "JOIN competence_hub.calendar_reservations s ON s.id = e.reservation_id" in sql
        assert "WHERE :scope OR s.company_id = CAST(:company AS uuid)" in sql
        assert sql.endswith("ORDER BY e.occurred_at DESC, s.id, e.version DESC LIMIT 30")
        self.reads.append("history")
        rows = [row for company, row in self.events if params["scope"] or company == params["company"]]
        return Rows(sorted(rows, key=lambda row: (-row.occurred_at.timestamp(), row.reservation_id, -row.version))[:30])


class Sessions:
    def __init__(self, role):
        self.role = role

    async def refresh_active_session(self, token_hash, *, now, idle_timeout):
        if not self.role or token_hash != digest_token(SESSION):
            return None
        return SessionPrincipal(UUID(int=7), ACTOR, "Synthetic", (self.role,), now,
                                now + idle_timeout, now + timedelta(hours=8), b"synthetic")


def client(engine, role, *, session=True):
    return TestClient(
        create_app(reservation_repository=ReservationRepository(engine, b"synthetic"),
                   calendar_session_repository=Sessions(role), clock=lambda: NOW),
        base_url="https://portal.example.invalid",
        cookies={SESSION_COOKIE_NAME: SESSION} if session else None,
    )


def test_drafts_stay_off_without_cal2_and_are_read_only():
    with TestClient(create_app()) as browser:
        response = browser.get(DRAFTS)
        assert response.status_code == 404
        assert response.headers["cache-control"] == "no-store"
        assert browser.post(DRAFTS, json={}).status_code == 405


@pytest.mark.parametrize(("role", "review", "session", "expected"), [
    ("admin", True, False, 401),
    (None, True, True, 401),  # No active MFA session returned by the session boundary.
    ("coach", False, True, 403),
    ("coach", True, True, 403),
    ("internal", True, True, 403),
    ("company_contact", True, True, 403),
    ("calendar_reviewer", False, True, 403),
])
def test_drafts_deny_reads_outside_the_selected_authorized_scope(role, review, session, expected):
    engine = ReadOnlyEngine()
    with client(engine, role, session=session) as browser:
        response = browser.get(DRAFTS, params={"review": str(review).lower()})
    assert response.status_code == expected
    assert response.headers["cache-control"] == "no-store"
    assert engine.reads == []


@pytest.mark.parametrize("contacts", [(), (COMPANY_A, COMPANY_B)])
def test_company_scope_requires_an_unambiguous_contact(contacts):
    engine = ReadOnlyEngine(contacts)
    with client(engine, "company_contact") as browser:
        response = browser.get(DRAFTS)
    assert response.status_code == 403
    assert response.json()["code"] == "reservation_contact_mapping"
    assert engine.reads == ["mapping"]


def test_company_reads_are_scoped_and_project_only_dedup_identity_and_event_metadata():
    events = [event(COMPANY_A, RESERVATION_A, 1), event(COMPANY_B, RESERVATION_B, 1),
              event(COMPANY_A, RESERVATION_A, 2, "offer_cancelled")]
    engine = ReadOnlyEngine((COMPANY_A,), events)
    with client(engine, "company_contact") as browser:
        response = browser.get(DRAFTS, params={"company_id": str(COMPANY_B), "limit": 1000})
        repeat = browser.get(DRAFTS)
        activity = browser.get(BASE + "/activity")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == repeat.json() == {"delivery_enabled": False, "items": [
        {"draft_id": f"cal2:{RESERVATION_A}:{version}", "reservation_id": str(RESERVATION_A),
         "offer_id": str(OFFER), "event_version": version, "kind": kind, "occurred_at": NOW.isoformat()}
        for version, kind in [(2, "offer_cancelled"), (1, "submitted")]
    ]}
    assert engine.reads == ["mapping", "history"] * 3 + ["tasks"]
    assert set(activity.json()) == {"events", "tasks"}
    assert len(activity.json()["events"]) == 2
    assert activity.json()["events"][0]["title"] == events[0][1].title

    with client(ReadOnlyEngine((COMPANY_B,), events), "company_contact") as browser:
        items = browser.get(DRAFTS).json()["items"]
    assert [item["draft_id"] for item in items] == [f"cal2:{RESERVATION_B}:1"]


@pytest.mark.parametrize("role", ["calendar_reviewer", "admin"])
def test_review_scope_is_bounded_and_shares_dedup_identity_across_roles(role):
    events = [event(COMPANY_A, RESERVATION_A, version) for version in range(1, 31)]
    events.append(event(COMPANY_B, RESERVATION_B, 30))
    events[-1][1]["occurred_at"] += timedelta(seconds=1)
    engine = ReadOnlyEngine(events=events)
    with client(engine, role) as browser:
        response = browser.get(DRAFTS, params={"review": "true"})
    assert response.status_code == 200
    assert response.json()["delivery_enabled"] is False
    ids = [item["draft_id"] for item in response.json()["items"]]
    assert ids == [f"cal2:{RESERVATION_B}:30"] + [f"cal2:{RESERVATION_A}:{v}" for v in range(30, 1, -1)]
    assert engine.reads == ["history"]


def test_authorized_empty_scope_has_no_drafts():
    with client(ReadOnlyEngine((COMPANY_A,)), "company_contact") as browser:
        response = browser.get(DRAFTS)
    assert response.status_code == 200
    assert response.json() == {"delivery_enabled": False, "items": []}
