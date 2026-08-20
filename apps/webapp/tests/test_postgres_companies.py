from datetime import UTC, datetime
from uuid import UUID

import pytest

from competence_hub_api.portal.companies import NewCompanyContact
from competence_hub_api.portal.postgres_companies import PostgresCompanyRepository

NOW = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
ACTOR_ID = UUID("00000000-0000-4000-8000-000000000121")
COMPANY_ID = UUID("00000000-0000-4000-8000-000000000122")
CONTACT_ID = UUID("00000000-0000-4000-8000-000000000123")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def company_row() -> dict[str, object]:
    return {
        "id": COMPANY_ID,
        "name": "Synthetic GmbH",
        "industry": "Beratung",
        "status": "prospect",
        "internal_notes": "Synthetic only",
        "created_at": NOW,
        "updated_at": NOW,
    }


def company_summary_row() -> dict[str, object]:
    return {
        "id": COMPANY_ID,
        "name": "Synthetic GmbH",
        "industry": "Beratung",
        "status": "prospect",
        "updated_at": NOW,
    }


def contact_row() -> dict[str, object]:
    return {
        "id": CONTACT_ID,
        "company_id": COMPANY_ID,
        "first_name": "Jan",
        "last_name": "Beispiel",
        "email": "contact@example.invalid",
        "phone": None,
        "job_function": "Einkauf",
        "created_at": NOW,
        "updated_at": NOW,
    }


class FakeResult:
    def __init__(self, *, scalar=None, row=None, rows=()) -> None:
        self.scalar = scalar
        self.row = row
        self.rows = tuple(rows)

    def scalar_one(self):
        return self.scalar

    def mappings(self):
        return self

    def one(self):
        return self.row

    def one_or_none(self):
        return self.row

    def all(self):
        return self.rows


class FakeConnection:
    def __init__(self, results=()) -> None:
        self.results = iter(results)
        self.executed: list[tuple[object, dict | None]] = []

    async def execute(self, statement, parameters=None):
        self.executed.append((statement, parameters))
        return next(self.results, FakeResult())


class FakeContext:
    def __init__(self, connection) -> None:
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class FakeEngine:
    def __init__(self, results=()) -> None:
        self.connection = FakeConnection(results)

    def connect(self):
        return FakeContext(self.connection)

    def begin(self):
        return FakeContext(self.connection)


def new_contact() -> NewCompanyContact:
    return NewCompanyContact(
        first_name="Jan",
        last_name="Beispiel",
        email="contact@example.invalid",
        job_function="Einkauf",
    )


@pytest.mark.anyio
async def test_company_and_initial_contact_are_created_and_audited_atomically() -> None:
    engine = FakeEngine(
        [
            FakeResult(row=company_row()),
            FakeResult(row=contact_row()),
            FakeResult(),
            FakeResult(),
        ]
    )
    repository = PostgresCompanyRepository(engine)

    detail = await repository.create_company(
        actor_user_id=ACTOR_ID,
        name="Synthetic GmbH",
        industry="Beratung",
        status="prospect",
        internal_notes="Synthetic only",
        initial_contact=new_contact(),
        now=NOW,
    )

    assert detail.company.id == COMPANY_ID
    assert detail.contacts[0].id == CONTACT_ID
    calls = engine.connection.executed
    assert len(calls) == 4
    assert calls[0][1]["status"] == "prospect"
    assert calls[1][1]["company_id"] == COMPANY_ID
    assert calls[2][1]["action"] == "portal.company.create"
    assert calls[3][1]["action"] == "portal.company_contact.create"
    assert "internal_notes" not in calls[2][1]
    assert "email" not in calls[3][1]


@pytest.mark.anyio
async def test_company_detail_reads_contacts_without_writes() -> None:
    engine = FakeEngine(
        [FakeResult(row=company_row()), FakeResult(rows=[contact_row()])]
    )
    repository = PostgresCompanyRepository(engine)

    detail = await repository.get_company(COMPANY_ID)

    assert detail is not None
    assert detail.company.name == "Synthetic GmbH"
    assert detail.contacts[0].email == "contact@example.invalid"
    assert len(engine.connection.executed) == 2


@pytest.mark.anyio
async def test_company_list_does_not_select_or_return_internal_notes() -> None:
    engine = FakeEngine([FakeResult(rows=[company_summary_row()])])
    repository = PostgresCompanyRepository(engine)

    companies = await repository.list_companies(query=None, limit=50)

    assert companies[0].name == "Synthetic GmbH"
    assert not hasattr(companies[0], "internal_notes")
    sql = str(engine.connection.executed[0][0]).lower()
    assert "internal_notes" not in sql
    assert "cast(:query as text)" in sql


@pytest.mark.anyio
async def test_missing_company_update_does_not_write_audit() -> None:
    engine = FakeEngine([FakeResult(row=None)])
    repository = PostgresCompanyRepository(engine)

    result = await repository.update_company(
        actor_user_id=ACTOR_ID,
        company_id=COMPANY_ID,
        changes={"industry": None},
        now=NOW,
    )

    assert result is None
    assert len(engine.connection.executed) == 1


@pytest.mark.anyio
async def test_contact_is_not_created_for_missing_company() -> None:
    engine = FakeEngine([FakeResult(scalar=False)])
    repository = PostgresCompanyRepository(engine)

    result = await repository.add_contact(
        actor_user_id=ACTOR_ID,
        company_id=COMPANY_ID,
        contact=new_contact(),
        now=NOW,
    )

    assert result is None
    assert len(engine.connection.executed) == 1


@pytest.mark.anyio
async def test_contact_update_is_scoped_to_company_and_audited() -> None:
    engine = FakeEngine([FakeResult(row=contact_row()), FakeResult()])
    repository = PostgresCompanyRepository(engine)

    result = await repository.update_contact(
        actor_user_id=ACTOR_ID,
        company_id=COMPANY_ID,
        contact_id=CONTACT_ID,
        changes={"phone": "0931 0000"},
        now=NOW,
    )

    assert result is not None
    parameters = engine.connection.executed[0][1]
    assert parameters["company_id"] == COMPANY_ID
    assert parameters["contact_id"] == CONTACT_ID
    assert parameters["set_phone"] is True
    assert engine.connection.executed[1][1]["action"] == (
        "portal.company_contact.update"
    )
