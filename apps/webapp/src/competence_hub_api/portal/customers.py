from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from competence_hub_api.auth.login_service import normalize_email
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.portal.companies import INTERNAL_ROLES
from competence_hub_api.security.email_addresses import is_single_email_address


class CustomerError(Exception):
    def __init__(self, status: int, code: str, title: str) -> None:
        super().__init__(code)
        self.status, self.code, self.title = status, code, title


class CustomerInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("*", mode="before")
    @classmethod
    def no_control_characters(cls, value):
        if isinstance(value, str) and any(ord(character) < 32 or ord(character) == 127 for character in value):
            raise ValueError("control characters are not allowed")
        return value


class CustomerAddress(CustomerInput):
    street: str = Field(min_length=1, max_length=200)
    postal_code: str = Field(min_length=1, max_length=20)
    city: str = Field(min_length=1, max_length=120)
    country: str = Field(min_length=1, max_length=100)


class CompanyAddress(CustomerAddress):
    purpose: Literal["billing", "business"]


class PrivateCustomerInput(CustomerInput):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    phone: str | None = Field(default=None, min_length=1, max_length=50)
    billing_address: CustomerAddress | None = None

    @field_validator("email")
    @classmethod
    def email_address(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = normalize_email(value)
        if not is_single_email_address(normalized):
            raise ValueError("invalid email address")
        return normalized


Version = Annotated[int, Field(strict=True, le=2_147_483_647)]


class PrivateCustomerUpdate(PrivateCustomerInput):
    version: Version = Field(ge=1)


class CompanyCustomerInput(CustomerInput):
    version: Version = Field(ge=0)
    vat_id: str | None = Field(default=None, min_length=3, max_length=32, pattern="^[A-Z0-9]+$")
    address: CompanyAddress | None = None

    @field_validator("vat_id", mode="before")
    @classmethod
    def normalize_vat_id(cls, value):
        return value.upper() if isinstance(value, str) else value


class PrivateCustomerSearch(CustomerInput):
    name: str = Field(default="", max_length=200)
    after: UUID | None = None
    limit: int = Field(default=50, strict=True, ge=1, le=100)


_PRIVATE_DETAIL = """id, first_name, last_name, email, phone, address_street,
    address_postal_code, address_city, address_country, version"""
_PRIVATE_LIST = text("""
    SELECT id, first_name, last_name
    FROM competence_hub.private_customers
    WHERE (CAST(:after AS uuid) IS NULL OR id > :after)
      AND (strpos(lower(first_name || ' ' || last_name), lower(:name)) > 0
           OR strpos(lower(last_name || ' ' || first_name), lower(:name)) > 0)
    ORDER BY id
    LIMIT :limit
""")
_PRIVATE_GET = text(f"""
    SELECT {_PRIVATE_DETAIL} FROM competence_hub.private_customers WHERE id = :id
""")
_PRIVATE_INSERT = text(f"""
    INSERT INTO competence_hub.private_customers (
        first_name, last_name, email, phone, address_street, address_postal_code,
        address_city, address_country, created_at, updated_at
    ) VALUES (:first_name, :last_name, :email, :phone, :street, :postal_code,
              :city, :country, :now, :now)
    RETURNING {_PRIVATE_DETAIL}
""")
_PRIVATE_UPDATE = text(f"""
    UPDATE competence_hub.private_customers
    SET first_name = :first_name, last_name = :last_name, email = :email, phone = :phone,
        address_street = :street, address_postal_code = :postal_code,
        address_city = :city, address_country = :country, version = version + 1, updated_at = :now
    WHERE id = :id AND version = :version
    RETURNING {_PRIVATE_DETAIL}
""")
_COMPANY_GET = text("""
    SELECT company.id AS company_id, details.vat_id, details.address_purpose,
           details.address_street, details.address_postal_code, details.address_city,
           details.address_country, COALESCE(details.version, 0) AS version
    FROM competence_hub.companies AS company
    LEFT JOIN competence_hub.company_customer_details AS details ON details.company_id = company.id
    WHERE company.id = :id
""")
_COMPANY_DETAIL = """company_id, vat_id, address_purpose, address_street,
    address_postal_code, address_city, address_country, version"""
_COMPANY_INSERT = text(f"""
    INSERT INTO competence_hub.company_customer_details (
        company_id, vat_id, address_purpose, address_street, address_postal_code,
        address_city, address_country, updated_at
    )
    SELECT id, :vat_id, :purpose, :street, :postal_code, :city, :country, :now
    FROM competence_hub.companies WHERE id = :id
    ON CONFLICT (company_id) DO NOTHING
    RETURNING {_COMPANY_DETAIL}
""")
_COMPANY_UPDATE = text(f"""
    UPDATE competence_hub.company_customer_details
    SET vat_id = :vat_id, address_purpose = :purpose, address_street = :street,
        address_postal_code = :postal_code, address_city = :city, address_country = :country,
        version = version + 1, updated_at = :now
    WHERE company_id = :id AND version = :version
    RETURNING {_COMPANY_DETAIL}
""")
_AUDIT = text("""
    INSERT INTO competence_hub.audit_events (
        actor_user_id, occurred_at, action, entity_type, entity_id, outcome
    ) VALUES (:actor, :now, :action, :entity_type, :id, 'success')
""")
_ADDRESS_FIELDS = ("street", "postal_code", "city", "country")


def _require_internal(actor: SessionPrincipal) -> None:
    if not INTERNAL_ROLES.intersection(actor.roles):
        raise CustomerError(403, "authorization_failed", "Berechtigung nicht vorhanden")


def _not_found() -> CustomerError:
    return CustomerError(404, "customer_not_found", "Datensatz nicht gefunden")


def _stale() -> CustomerError:
    return CustomerError(409, "customer_version_conflict", "Datensatz wurde zwischenzeitlich geaendert")


def _address_bindings(address: CustomerAddress | None) -> dict:
    return {name: getattr(address, name, None) for name in _ADDRESS_FIELDS}


def _serialize(record, *, company: bool = False) -> dict:
    values = dict(record)
    address = {name: values.pop(f"address_{name}") for name in _ADDRESS_FIELDS}
    if company:
        address["purpose"] = values.pop("address_purpose")
    values["address" if company else "billing_address"] = address if address["street"] else None
    return values


async def _audit(connection: AsyncConnection, *, actor: SessionPrincipal, now: datetime,
                 action: str, entity_type: str, entity_id: UUID) -> None:
    await connection.execute(_AUDIT, {
        "actor": actor.user_id, "now": now, "action": action,
        "entity_type": entity_type, "id": entity_id,
    })


class CustomerAdministration:
    """Internal-only customer records, isolated from authorization and account data."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def search_private(self, actor: SessionPrincipal, criteria: PrivateCustomerSearch) -> dict:
        _require_internal(actor)
        values = criteria.model_dump()
        values["limit"] += 1
        async with self._engine.connect() as connection:
            result = await connection.execute(_PRIVATE_LIST, values)
            items = [dict(row) for row in result.mappings()]
        next_after = items[criteria.limit - 1]["id"] if len(items) > criteria.limit else None
        return {"items": items[:criteria.limit], "next_after": next_after}

    async def get_private(self, actor: SessionPrincipal, customer_id: UUID) -> dict:
        _require_internal(actor)
        async with self._engine.connect() as connection:
            row = (await connection.execute(_PRIVATE_GET, {"id": customer_id})).mappings().one_or_none()
        if row is None:
            raise _not_found()
        return _serialize(row)

    async def save_private(self, actor: SessionPrincipal, payload: PrivateCustomerInput,
                           now: datetime, *, customer_id: UUID | None = None) -> dict:
        _require_internal(actor)
        if (customer_id is not None) != isinstance(payload, PrivateCustomerUpdate):
            raise ValueError("private customer update requires an id and version")
        params = {**payload.model_dump(exclude={"billing_address"}),
                  **_address_bindings(payload.billing_address), "now": now, "id": customer_id}
        async with self._engine.begin() as connection:
            row = (await connection.execute(
                _PRIVATE_UPDATE if customer_id else _PRIVATE_INSERT, params,
            )).mappings().one_or_none()
            if row is None:
                exists = (await connection.execute(_PRIVATE_GET, params)).first() is not None
                raise _stale() if exists else _not_found()
            await _audit(connection, actor=actor, now=now, entity_type="private_customer",
                         action="portal.customer.private.update" if customer_id else "portal.customer.private.create",
                         entity_id=row["id"])
        return _serialize(row)

    async def get_company_details(self, actor: SessionPrincipal, company_id: UUID) -> dict:
        _require_internal(actor)
        async with self._engine.connect() as connection:
            row = (await connection.execute(_COMPANY_GET, {"id": company_id})).mappings().one_or_none()
        if row is None:
            raise _not_found()
        return _serialize(row, company=True)

    async def save_company_details(self, actor: SessionPrincipal, company_id: UUID,
                                   payload: CompanyCustomerInput, now: datetime) -> dict:
        _require_internal(actor)
        params = {"id": company_id, "now": now, "vat_id": payload.vat_id,
                  "purpose": payload.address.purpose if payload.address else None,
                  "version": payload.version, **_address_bindings(payload.address)}
        async with self._engine.begin() as connection:
            row = (await connection.execute(
                _COMPANY_INSERT if payload.version == 0 else _COMPANY_UPDATE, params,
            )).mappings().one_or_none()
            if row is None:
                exists = (await connection.execute(_COMPANY_GET, params)).first() is not None
                raise _stale() if exists else _not_found()
            await _audit(connection, actor=actor, now=now, entity_type="company",
                         action="portal.customer.company.details.update", entity_id=company_id)
        return _serialize(row, company=True)
