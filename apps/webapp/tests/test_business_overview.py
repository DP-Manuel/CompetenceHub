from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from competence_hub_api.main import create_app
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token
from competence_hub_api.web import pilot


PATH = "/api/v1/portal/pilot/overview"
ORIGIN = "https://portal.example.invalid"
TOKEN = "synthetic-business-overview-session"


class Result(list):
    def mappings(self):
        return self

    def all(self):
        return self

    def one(self):
        row, = self
        return row


class OverviewDatabase:
    def __init__(self, contacts):
        self.contacts = contacts
        self.calls = []

    def connect(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass

    async def execute(self, statement, params=None):
        query = str(statement)
        self.calls.append((query, params))
        if query == "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY":
            return Result()
        if "FROM competence_hub.company_contacts c" in query:
            return Result(self.contacts)
        samples = {
            str(pilot._COUNTS): [{"status": "published", "count": 1, "resubmitted": 0}],
            str(pilot._RECENT_PUBLICATIONS): [],
            str(pilot._CALENDAR_REVIEW): [{"calendar_in_review": 1, "tasks": [{"kind": "calendar_review"}]}],
            str(pilot._REVIEW_RESERVATIONS): [{"pending": 1, "reply_ready": 2, "tasks": [{"kind": "reservation_review"}]}],
            str(pilot._COMPANY_RESERVATIONS): [{"upcoming": 3, "past": 1, "tasks": [{"kind": "reply_needed"}]}],
            str(pilot._COACH_BUSINESS): [{"published": 1, "revision_pending": 1}],
            str(pilot._ADMIN_COUNTS): [{"accounts": 5, "active": 4, "pending_activation": 1}],
            str(pilot._ADMIN_AUDIT): [{"category": "account_access", "status": "success"}],
        }
        return Result(samples[query])


def client_for(*roles, booker=False, contacts=(), signed_in=True):
    actor = SimpleNamespace(user_id=uuid4(), roles=roles)
    database = OverviewDatabase(contacts)

    class Sessions:
        async def refresh_active_session(self, token_hash, **kwargs):
            return actor if token_hash == digest_token(TOKEN) else None

    app = create_app(
        calendar_service=object(),
        calendar_session_repository=Sessions(),
        reservation_repository=object() if booker else None,
        allowed_origin=ORIGIN,
    )
    app.state.database_engine = database
    client = TestClient(app)
    if signed_in:
        client.cookies.set(SESSION_COOKIE_NAME, TOKEN)
    return client, actor, database


def test_default_schema_executes_only_existing_calendar_reads():
    client, _, database = client_for("admin", "company_contact")
    with client:
        response = client.get(PATH)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {
        "calendar": {"published": 1},
        "resubmitted": 0,
        "recent_publications": [],
        "database": "reachable",
        "scope": "authorized_current_revisions",
    }
    assert [query for query, _ in database.calls[1:]] == list(map(str, (pilot._COUNTS, pilot._RECENT_PUBLICATIONS)))


@pytest.mark.parametrize("gate, contact_count", [(False, 1), (True, 0), (True, 2)])
def test_company_role_without_authoritative_scope_is_denied(gate, contact_count):
    contacts = [SimpleNamespace(company_id=uuid4()) for _ in range(contact_count)]
    client, _, database = client_for("company_contact", booker=gate, contacts=contacts)
    with client:
        response = client.get(PATH + f"?company_id={uuid4()}")
    assert response.status_code == 403
    assert response.json()["code"] == "authorization_failed"
    assert len(database.calls) == (2 if gate else 0)
    assert all(query != str(pilot._COMPANY_RESERVATIONS) for query, _ in database.calls)


def test_company_read_is_scoped_to_confirmed_mapping_not_query_parameters():
    company = SimpleNamespace(company_id=uuid4())
    client, actor, database = client_for("company_contact", booker=True, contacts=[company])
    with client:
        result = client.get(PATH + f"?review=true&company_id={uuid4()}", headers={"Origin": ORIGIN}).json()
    assert result["calendar"] == {} and not result["recent_publications"]
    assert result["business"] == {
        "company": {"counts": {"upcoming": 3, "past": 1}, "tasks": [{"kind": "reply_needed"}]},
    }
    assert database.calls[1][1] == {"user": actor.user_id}
    assert database.calls[2][1]["company"] == company.company_id
    assert len(database.calls) == 3


@pytest.mark.parametrize(("role", "sections"), [
    ("coach", {"coach"}), ("calendar_reviewer", {"review"}), ("admin", {"review", "admin"}),
])
def test_privileged_business_sections_are_role_specific(role, sections):
    client, actor, database = client_for(role, booker=True)
    with client:
        response = client.get(PATH)
    assert response.status_code == 200
    business = response.json()["business"]
    assert business.keys() == sections
    if role == "coach":
        assert business["coach"] == {"counts": {"published": 1, "revision_pending": 1}, "upcoming_offers": []}
        assert database.calls[-1][0] == str(pilot._COACH_BUSINESS)
        assert database.calls[-1][1]["actor"] == actor.user_id
    if "review" in sections:
        assert business["review"]["tasks"] == [
            {"kind": "calendar_review"}, {"kind": "reservation_review"},
        ]
        assert business["review"]["counts"]["reply_ready"] == 2
    if "admin" in sections:
        assert business["admin"]["audit"] == [{"category": "account_access", "status": "success"}]


def test_unmapped_second_role_does_not_disable_the_review_section():
    client, _, _ = client_for("calendar_reviewer", "company_contact", booker=True)
    with client:
        response = client.get(PATH)
    assert response.status_code == 200
    assert response.json()["business"].keys() == {"review"}


@pytest.mark.parametrize(("signed_in", "role", "headers", "status"), [
    (False, "admin", {}, 401),
    (True, "internal", {}, 403),
    (True, "admin", {"Origin": "https://other.example.invalid"}, 403),
    (True, "company_contact", {"Sec-Fetch-Site": "same-site"}, 403),
    (True, "calendar_reviewer", {"Sec-Fetch-Site": "cross-site"}, 403),
])
def test_unauthorized_overview_does_not_read_business_data(signed_in, role, headers, status):
    client, _, database = client_for(role, booker=True, signed_in=signed_in)
    with client:
        response = client.get(PATH, headers=headers)
    assert response.status_code == status
    assert database.calls == []
