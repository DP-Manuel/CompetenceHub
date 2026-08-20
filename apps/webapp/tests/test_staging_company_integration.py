from datetime import UTC, datetime
import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.portal.companies import NewCompanyContact
from competence_hub_api.portal.postgres_companies import PostgresCompanyRepository

APP_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_APP_DATABASE_URL"
MIGRATOR_DATABASE_URL_ENV = "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL"
NOW = datetime(2026, 8, 20, 13, 0, tzinfo=UTC)

pytestmark = [pytest.mark.anyio, pytest.mark.staging_integration]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _required_database_urls() -> tuple[str, str]:
    app_url = os.environ.get(APP_DATABASE_URL_ENV, "")
    migrator_url = os.environ.get(MIGRATOR_DATABASE_URL_ENV, "")
    if not app_url or not migrator_url:
        pytest.skip(
            "isolated staging URLs were not supplied through the process environment"
        )
    return app_url, migrator_url


@pytest.mark.anyio
async def test_staging_company_contact_crud_audit_and_zero_residue() -> None:
    app_url, migrator_url = _required_database_urls()
    app_engine = create_async_engine(app_url, pool_pre_ping=True, hide_parameters=True)
    admin_engine = create_async_engine(
        migrator_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    repository = PostgresCompanyRepository(app_engine)
    actor_id = uuid4()
    company_id = None
    contact_ids = []

    try:
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.portal_users (
                        id, display_name, email, active
                    ) VALUES (
                        :actor_id,
                        'Synthetic Company Staging User',
                        :email,
                        true
                    )
                    """
                ),
                {
                    "actor_id": actor_id,
                    "email": f"synthetic-company-{uuid4().hex}@example.invalid",
                },
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO competence_hub.user_roles (user_id, role_id)
                    SELECT :actor_id, id
                    FROM competence_hub.roles
                    WHERE code = 'internal'
                    """
                ),
                {"actor_id": actor_id},
            )

        created = await repository.create_company(
            actor_user_id=actor_id,
            name=f"Synthetic Staging Company {uuid4().hex}",
            industry="Synthetic testing",
            status="prospect",
            internal_notes="Synthetic staging data only",
            initial_contact=NewCompanyContact(
                first_name="Initial",
                last_name="Contact",
                email=f"synthetic-contact-{uuid4().hex}@example.invalid",
            ),
            now=NOW,
        )
        company_id = created.company.id
        contact_ids.append(created.contacts[0].id)

        listed = await repository.list_companies(
            query=created.company.name,
            limit=10,
        )
        detail = await repository.get_company(company_id)
        updated_company = await repository.update_company(
            actor_user_id=actor_id,
            company_id=company_id,
            changes={"industry": None, "internal_notes": "Corrected synthetic note"},
            now=NOW,
        )
        added_contact = await repository.add_contact(
            actor_user_id=actor_id,
            company_id=company_id,
            contact=NewCompanyContact(
                first_name="Second",
                last_name="Contact",
                email=f"synthetic-contact-{uuid4().hex}@example.invalid",
                phone="0000",
            ),
            now=NOW,
        )
        assert added_contact is not None
        contact_ids.append(added_contact.id)
        updated_contact = await repository.update_contact(
            actor_user_id=actor_id,
            company_id=company_id,
            contact_id=added_contact.id,
            changes={"phone": None, "job_function": "Synthetic role"},
            now=NOW,
        )

        assert [item.id for item in listed] == [company_id]
        assert detail is not None
        assert detail.contacts[0].id == contact_ids[0]
        assert updated_company is not None
        assert updated_company.industry is None
        assert updated_company.internal_notes == "Corrected synthetic note"
        assert updated_contact is not None
        assert updated_contact.phone is None
        assert updated_contact.job_function == "Synthetic role"

        async with app_engine.connect() as connection:
            privileges = (
                await connection.execute(
                    text(
                        """
                        SELECT
                            has_schema_privilege(
                                current_user,
                                'competence_hub',
                                'CREATE'
                            ) AS can_create_schema_objects,
                            has_table_privilege(
                                current_user,
                                'competence_hub.schema_migrations',
                                'SELECT'
                            ) AS can_read_migrations,
                            has_table_privilege(
                                current_user,
                                'competence_hub.companies',
                                'DELETE'
                            ) AS can_delete_companies,
                            has_table_privilege(
                                current_user,
                                'competence_hub.company_contacts',
                                'DELETE'
                            ) AS can_delete_contacts,
                            has_table_privilege(
                                current_user,
                                'competence_hub.audit_events',
                                'UPDATE'
                            ) AS can_update_audit_events,
                            has_table_privilege(
                                current_user,
                                'competence_hub.audit_events',
                                'DELETE'
                            ) AS can_delete_audit_events
                        """
                    )
                )
            ).mappings().one()

        assert not any(privileges.values())

        async with admin_engine.connect() as connection:
            audit_count = await connection.scalar(
                text(
                    """
                    SELECT count(*)
                    FROM competence_hub.audit_events
                    WHERE actor_user_id = :actor_id
                      AND action LIKE 'portal.company%'
                    """
                ),
                {"actor_id": actor_id},
            )
            assert audit_count == 5
    finally:
        async with admin_engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await connection.execute(
                text(
                    "DELETE FROM competence_hub.audit_events "
                    "WHERE actor_user_id = :actor_id"
                ),
                {"actor_id": actor_id},
            )
            if company_id is not None:
                await connection.execute(
                    text(
                        "DELETE FROM competence_hub.company_contacts "
                        "WHERE company_id = :company_id"
                    ),
                    {"company_id": company_id},
                )
                await connection.execute(
                    text(
                        "DELETE FROM competence_hub.companies "
                        "WHERE id = :company_id"
                    ),
                    {"company_id": company_id},
                )
            await connection.execute(
                text(
                    "DELETE FROM competence_hub.portal_users "
                    "WHERE id = :actor_id"
                ),
                {"actor_id": actor_id},
            )
        await app_engine.dispose()
        await admin_engine.dispose()

    verification_engine = create_async_engine(
        migrator_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    try:
        async with verification_engine.connect() as connection:
            residue = await connection.scalar(
                text(
                    """
                    SELECT
                        (SELECT count(*) FROM competence_hub.portal_users
                         WHERE id = :actor_id)
                      + (SELECT count(*) FROM competence_hub.companies
                         WHERE id = :company_id)
                      + (SELECT count(*) FROM competence_hub.audit_events
                         WHERE actor_user_id = :actor_id)
                    """
                ),
                {"actor_id": actor_id, "company_id": company_id},
            )
            assert residue == 0
    finally:
        await verification_engine.dispose()
