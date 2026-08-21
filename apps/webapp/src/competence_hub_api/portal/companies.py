from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from competence_hub_api.auth.login_service import normalize_email
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.security.email_addresses import is_single_email_address

PROVISIONAL_COMPANY_STATUS = "prospect"
INTERNAL_ROLES = frozenset({"admin", "internal"})


class CompanyAccessDeniedError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompanyRecord:
    id: UUID
    name: str
    industry: str | None
    status: str
    internal_notes: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CompanySummary:
    id: UUID
    name: str
    industry: str | None
    status: str
    updated_at: datetime


@dataclass(frozen=True)
class CompanyContactRecord:
    id: UUID
    company_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    job_function: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CompanyDetail:
    company: CompanyRecord
    contacts: tuple[CompanyContactRecord, ...]


@dataclass(frozen=True)
class NewCompanyContact:
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    job_function: str | None = None


class CompanyRepository(Protocol):
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
    ) -> CompanyDetail: ...

    async def list_companies(
        self,
        *,
        query: str | None,
        limit: int,
    ) -> tuple[CompanySummary, ...]: ...

    async def get_company(self, company_id: UUID) -> CompanyDetail | None: ...

    async def update_company(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        changes: Mapping[str, str | None],
        now: datetime,
    ) -> CompanyRecord | None: ...

    async def add_contact(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        contact: NewCompanyContact,
        now: datetime,
    ) -> CompanyContactRecord | None: ...

    async def update_contact(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        contact_id: UUID,
        changes: Mapping[str, str | None],
        now: datetime,
    ) -> CompanyContactRecord | None: ...


class CompanyService:
    def __init__(self, repository: CompanyRepository) -> None:
        self._repository = repository

    async def create_company(
        self,
        *,
        actor: SessionPrincipal,
        name: str,
        industry: str | None,
        internal_notes: str | None,
        initial_contact: NewCompanyContact,
        now: datetime,
    ) -> CompanyDetail:
        _require_internal(actor)
        _validate_now(now)
        return await self._repository.create_company(
            actor_user_id=actor.user_id,
            name=_required_text(name, "name", 200),
            industry=_optional_text(industry, "industry", 200),
            status=PROVISIONAL_COMPANY_STATUS,
            internal_notes=_optional_text(internal_notes, "internal_notes", 4000),
            initial_contact=_normalize_contact(initial_contact),
            now=now,
        )

    async def list_companies(
        self,
        *,
        actor: SessionPrincipal,
        query: str | None,
        limit: int,
    ) -> tuple[CompanySummary, ...]:
        _require_internal(actor)
        if not 1 <= limit <= 100:
            raise ValueError("invalid company list limit")
        return await self._repository.list_companies(
            query=_optional_text(query, "query", 200),
            limit=limit,
        )

    async def get_company(
        self,
        *,
        actor: SessionPrincipal,
        company_id: UUID,
    ) -> CompanyDetail | None:
        _require_internal(actor)
        return await self._repository.get_company(company_id)

    async def update_company(
        self,
        *,
        actor: SessionPrincipal,
        company_id: UUID,
        changes: Mapping[str, str | None],
        now: datetime,
    ) -> CompanyRecord | None:
        _require_internal(actor)
        _validate_now(now)
        allowed = {"name", "industry", "internal_notes"}
        if not changes or not set(changes).issubset(allowed):
            raise ValueError("invalid company changes")
        normalized: dict[str, str | None] = {}
        if "name" in changes:
            value = changes["name"]
            if value is None:
                raise ValueError("name must not be null")
            normalized["name"] = _required_text(value, "name", 200)
        if "industry" in changes:
            normalized["industry"] = _optional_text(
                changes["industry"], "industry", 200
            )
        if "internal_notes" in changes:
            normalized["internal_notes"] = _optional_text(
                changes["internal_notes"], "internal_notes", 4000
            )
        return await self._repository.update_company(
            actor_user_id=actor.user_id,
            company_id=company_id,
            changes=normalized,
            now=now,
        )

    async def add_contact(
        self,
        *,
        actor: SessionPrincipal,
        company_id: UUID,
        contact: NewCompanyContact,
        now: datetime,
    ) -> CompanyContactRecord | None:
        _require_internal(actor)
        _validate_now(now)
        return await self._repository.add_contact(
            actor_user_id=actor.user_id,
            company_id=company_id,
            contact=_normalize_contact(contact),
            now=now,
        )

    async def update_contact(
        self,
        *,
        actor: SessionPrincipal,
        company_id: UUID,
        contact_id: UUID,
        changes: Mapping[str, str | None],
        now: datetime,
    ) -> CompanyContactRecord | None:
        _require_internal(actor)
        _validate_now(now)
        allowed = {"first_name", "last_name", "email", "phone", "job_function"}
        if not changes or not set(changes).issubset(allowed):
            raise ValueError("invalid contact changes")
        normalized: dict[str, str | None] = {}
        for field_name in ("first_name", "last_name"):
            if field_name in changes:
                value = changes[field_name]
                if value is None:
                    raise ValueError(f"{field_name} must not be null")
                normalized[field_name] = _required_text(value, field_name, 100)
        if "email" in changes:
            value = changes["email"]
            if value is None:
                raise ValueError("email must not be null")
            normalized["email"] = _email(value)
        if "phone" in changes:
            normalized["phone"] = _optional_text(changes["phone"], "phone", 50)
        if "job_function" in changes:
            normalized["job_function"] = _optional_text(
                changes["job_function"], "job_function", 200
            )
        return await self._repository.update_contact(
            actor_user_id=actor.user_id,
            company_id=company_id,
            contact_id=contact_id,
            changes=normalized,
            now=now,
        )


def _require_internal(actor: SessionPrincipal) -> None:
    if not set(actor.roles).intersection(INTERNAL_ROLES):
        raise CompanyAccessDeniedError("internal portal role required")


def _normalize_contact(contact: NewCompanyContact) -> NewCompanyContact:
    return NewCompanyContact(
        first_name=_required_text(contact.first_name, "first_name", 100),
        last_name=_required_text(contact.last_name, "last_name", 100),
        email=_email(contact.email),
        phone=_optional_text(contact.phone, "phone", 50),
        job_function=_optional_text(contact.job_function, "job_function", 200),
    )


def _email(value: str) -> str:
    normalized = normalize_email(value)
    if not is_single_email_address(normalized):
        raise ValueError("invalid email")
    return normalized


def _required_text(value: str, name: str, maximum: int) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > maximum:
        raise ValueError(f"invalid {name}")
    return normalized


def _optional_text(value: str | None, name: str, maximum: int) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > maximum:
        raise ValueError(f"invalid {name}")
    return normalized


def _validate_now(now: datetime) -> None:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
