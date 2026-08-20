from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.portal.companies import (
    CompanyContactRecord,
    CompanyDetail,
    CompanyRecord,
    CompanySummary,
    NewCompanyContact,
)

_CREATE_COMPANY = text(
    """
    INSERT INTO competence_hub.companies (
        name, industry, status, internal_notes, created_at, updated_at
    ) VALUES (
        :name, :industry, :status, :internal_notes, :now, :now
    )
    RETURNING id, name, industry, status, internal_notes, created_at, updated_at
    """
)

_CREATE_CONTACT = text(
    """
    INSERT INTO competence_hub.company_contacts (
        company_id,
        first_name,
        last_name,
        email,
        phone,
        job_function,
        created_at,
        updated_at
    ) VALUES (
        :company_id,
        :first_name,
        :last_name,
        :email,
        :phone,
        :job_function,
        :now,
        :now
    )
    RETURNING
        id,
        company_id,
        first_name,
        last_name,
        email,
        phone,
        job_function,
        created_at,
        updated_at
    """
)

_LIST_COMPANIES = text(
    """
    SELECT id, name, industry, status, updated_at
    FROM competence_hub.companies
    WHERE CAST(:query AS text) IS NULL
       OR lower(name) LIKE '%' || lower(CAST(:query AS text)) || '%'
    ORDER BY lower(name), id
    LIMIT :limit
    """
)

_GET_COMPANY = text(
    """
    SELECT id, name, industry, status, internal_notes, created_at, updated_at
    FROM competence_hub.companies
    WHERE id = :company_id
    """
)

_LIST_CONTACTS = text(
    """
    SELECT
        id,
        company_id,
        first_name,
        last_name,
        email,
        phone,
        job_function,
        created_at,
        updated_at
    FROM competence_hub.company_contacts
    WHERE company_id = :company_id
    ORDER BY lower(last_name), lower(first_name), id
    """
)

_UPDATE_COMPANY = text(
    """
    UPDATE competence_hub.companies
    SET
        name = CASE WHEN :set_name THEN :name ELSE name END,
        industry = CASE WHEN :set_industry THEN :industry ELSE industry END,
        internal_notes = CASE
            WHEN :set_internal_notes THEN :internal_notes
            ELSE internal_notes
        END,
        updated_at = :now
    WHERE id = :company_id
    RETURNING id, name, industry, status, internal_notes, created_at, updated_at
    """
)

_UPDATE_CONTACT = text(
    """
    UPDATE competence_hub.company_contacts
    SET
        first_name = CASE
            WHEN :set_first_name THEN :first_name
            ELSE first_name
        END,
        last_name = CASE WHEN :set_last_name THEN :last_name ELSE last_name END,
        email = CASE WHEN :set_email THEN :email ELSE email END,
        phone = CASE WHEN :set_phone THEN :phone ELSE phone END,
        job_function = CASE
            WHEN :set_job_function THEN :job_function
            ELSE job_function
        END,
        updated_at = :now
    WHERE id = :contact_id
      AND company_id = :company_id
    RETURNING
        id,
        company_id,
        first_name,
        last_name,
        email,
        phone,
        job_function,
        created_at,
        updated_at
    """
)

_COMPANY_EXISTS = text(
    "SELECT EXISTS (SELECT 1 FROM competence_hub.companies WHERE id = :company_id)"
)

_AUDIT = text(
    """
    INSERT INTO competence_hub.audit_events (
        actor_user_id, occurred_at, action, entity_type, entity_id, outcome
    ) VALUES (
        :actor_user_id, :now, :action, :entity_type, :entity_id, 'success'
    )
    """
)


class PostgresCompanyRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create_company(
        self,
        *,
        actor_user_id: UUID,
        name: str,
        industry: str | None,
        status: str,
        internal_notes: str | None,
        initial_contact: NewCompanyContact,
        now: datetime,
    ) -> CompanyDetail:
        async with self._engine.begin() as connection:
            company_result = await connection.execute(
                _CREATE_COMPANY,
                {
                    "name": name,
                    "industry": industry,
                    "status": status,
                    "internal_notes": internal_notes,
                    "now": now,
                },
            )
            company = _company(company_result.mappings().one())
            contact_result = await connection.execute(
                _CREATE_CONTACT,
                _contact_parameters(company.id, initial_contact, now),
            )
            contact = _contact(contact_result.mappings().one())
            await _write_audit(
                connection,
                actor_user_id=actor_user_id,
                now=now,
                action="portal.company.create",
                entity_type="company",
                entity_id=company.id,
            )
            await _write_audit(
                connection,
                actor_user_id=actor_user_id,
                now=now,
                action="portal.company_contact.create",
                entity_type="company_contact",
                entity_id=contact.id,
            )
        return CompanyDetail(company=company, contacts=(contact,))

    async def list_companies(
        self,
        *,
        query: str | None,
        limit: int,
    ) -> tuple[CompanySummary, ...]:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _LIST_COMPANIES,
                {"query": query, "limit": limit},
            )
            return tuple(_company_summary(row) for row in result.mappings().all())

    async def get_company(self, company_id: UUID) -> CompanyDetail | None:
        async with self._engine.connect() as connection:
            company_result = await connection.execute(
                _GET_COMPANY,
                {"company_id": company_id},
            )
            company_row = company_result.mappings().one_or_none()
            if company_row is None:
                return None
            contacts_result = await connection.execute(
                _LIST_CONTACTS,
                {"company_id": company_id},
            )
            contacts = tuple(
                _contact(row) for row in contacts_result.mappings().all()
            )
        return CompanyDetail(company=_company(company_row), contacts=contacts)

    async def update_company(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        changes: Mapping[str, str | None],
        now: datetime,
    ) -> CompanyRecord | None:
        parameters = {
            "company_id": company_id,
            "set_name": "name" in changes,
            "name": changes.get("name"),
            "set_industry": "industry" in changes,
            "industry": changes.get("industry"),
            "set_internal_notes": "internal_notes" in changes,
            "internal_notes": changes.get("internal_notes"),
            "now": now,
        }
        async with self._engine.begin() as connection:
            result = await connection.execute(_UPDATE_COMPANY, parameters)
            row = result.mappings().one_or_none()
            if row is None:
                return None
            company = _company(row)
            await _write_audit(
                connection,
                actor_user_id=actor_user_id,
                now=now,
                action="portal.company.update",
                entity_type="company",
                entity_id=company_id,
            )
            return company

    async def add_contact(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        contact: NewCompanyContact,
        now: datetime,
    ) -> CompanyContactRecord | None:
        async with self._engine.begin() as connection:
            exists = await connection.execute(
                _COMPANY_EXISTS,
                {"company_id": company_id},
            )
            if not exists.scalar_one():
                return None
            result = await connection.execute(
                _CREATE_CONTACT,
                _contact_parameters(company_id, contact, now),
            )
            created = _contact(result.mappings().one())
            await _write_audit(
                connection,
                actor_user_id=actor_user_id,
                now=now,
                action="portal.company_contact.create",
                entity_type="company_contact",
                entity_id=created.id,
            )
            return created

    async def update_contact(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        contact_id: UUID,
        changes: Mapping[str, str | None],
        now: datetime,
    ) -> CompanyContactRecord | None:
        parameters = {
            "company_id": company_id,
            "contact_id": contact_id,
            "set_first_name": "first_name" in changes,
            "first_name": changes.get("first_name"),
            "set_last_name": "last_name" in changes,
            "last_name": changes.get("last_name"),
            "set_email": "email" in changes,
            "email": changes.get("email"),
            "set_phone": "phone" in changes,
            "phone": changes.get("phone"),
            "set_job_function": "job_function" in changes,
            "job_function": changes.get("job_function"),
            "now": now,
        }
        async with self._engine.begin() as connection:
            result = await connection.execute(_UPDATE_CONTACT, parameters)
            row = result.mappings().one_or_none()
            if row is None:
                return None
            contact = _contact(row)
            await _write_audit(
                connection,
                actor_user_id=actor_user_id,
                now=now,
                action="portal.company_contact.update",
                entity_type="company_contact",
                entity_id=contact_id,
            )
            return contact


async def _write_audit(
    connection,
    *,
    actor_user_id: UUID,
    now: datetime,
    action: str,
    entity_type: str,
    entity_id: UUID,
) -> None:
    await connection.execute(
        _AUDIT,
        {
            "actor_user_id": actor_user_id,
            "now": now,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
        },
    )


def _contact_parameters(
    company_id: UUID,
    contact: NewCompanyContact,
    now: datetime,
) -> dict[str, object]:
    return {
        "company_id": company_id,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "email": contact.email,
        "phone": contact.phone,
        "job_function": contact.job_function,
        "now": now,
    }


def _company(row: Mapping[str, object]) -> CompanyRecord:
    return CompanyRecord(
        id=row["id"],
        name=row["name"],
        industry=row["industry"],
        status=row["status"],
        internal_notes=row["internal_notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _company_summary(row: Mapping[str, object]) -> CompanySummary:
    return CompanySummary(
        id=row["id"],
        name=row["name"],
        industry=row["industry"],
        status=row["status"],
        updated_at=row["updated_at"],
    )


def _contact(row: Mapping[str, object]) -> CompanyContactRecord:
    return CompanyContactRecord(
        id=row["id"],
        company_id=row["company_id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
        phone=row["phone"],
        job_function=row["job_function"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
