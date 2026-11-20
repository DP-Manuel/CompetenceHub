import asyncio
from collections.abc import Callable, Mapping
from contextlib import asynccontextmanager
import hashlib
import hmac
import secrets

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from competence_hub_api.auth.login_service import LoginService
from competence_hub_api.auth.admission import AdmissionPolicy, PORTAL_ADMISSION
from competence_hub_api.auth.mfa_service import MfaService
from competence_hub_api.auth.account_lifecycle import AccountLifecycleService
from competence_hub_api.auth.postgres_account_lifecycle import (
    PostgresAccountLifecycleRepository,
)
from competence_hub_api.auth.postgres_login_repository import PostgresLoginRepository
from competence_hub_api.auth.postgres_mfa_repository import PostgresMfaRepository
from competence_hub_api.auth.postgres_session_repository import (
    PostgresSessionRepository,
)
from competence_hub_api.config import CAL2_PILOT_DATABASE, RuntimeSettings
from competence_hub_api.main import create_app
from competence_hub_api.portal.companies import CompanyService
from competence_hub_api.portal.customers import CustomerAdministration
from competence_hub_api.portal.calendar import CalendarService
from competence_hub_api.portal.postgres_calendar import PostgresCalendarRepository
from competence_hub_api.portal.reservations import ReservationRepository
from competence_hub_api.portal.postgres_companies import PostgresCompanyRepository
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.secret_encryption import SecretCipher

EngineFactory = Callable[[str], AsyncEngine]
CALENDAR_SESSION_ROLES = frozenset(
    {"admin", "calendar_reviewer", "coach", "company_contact", "internal"}
)


async def _verify_cal2_pilot(engine: AsyncEngine) -> None:
    async with engine.connect() as connection:
        verified = await connection.scalar(text("""
            SELECT current_database() = :database
                AND to_regclass('competence_hub.calendar_reservations') IS NOT NULL
                AND to_regclass('competence_hub.calendar_reservation_events_activity_idx') IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM competence_hub.portal_users
                    WHERE email NOT ILIKE '%@example.invalid'
                )
        """), {"database": CAL2_PILOT_DATABASE})
    if not verified:
        raise RuntimeError("CAL-2 pilot database, schema or synthetic cohort did not pass")


async def _customer_schema_ready(engine: AsyncEngine) -> bool:
    # The two tables and their grants are installed atomically by 0012. The
    # app role deliberately cannot read the migration ledger.
    async with engine.connect() as connection:
        return bool(await connection.scalar(text("""
            SELECT has_table_privilege(
                       to_regclass('competence_hub.private_customers'), 'SELECT'
                   )
               AND has_table_privilege(
                       to_regclass('competence_hub.company_customer_details'), 'SELECT'
                   )
        """)))


def create_database_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(
        database_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )


async def database_is_ready(
    engine: AsyncEngine,
    *,
    timeout_seconds: float = 5.0,
) -> bool:
    try:
        async with asyncio.timeout(timeout_seconds):
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, OSError, TimeoutError):
        return False


def create_runtime_app(
    settings: RuntimeSettings,
    *,
    engine_factory: EngineFactory = create_database_engine,
    local_reservations: bool = False,
) -> FastAPI:
    if local_reservations:
        database = make_url(settings.database_url)
        if (database.host, database.port, database.database) != (
            "127.0.0.1", 55433, "competence_hub_staging"
        ) or not settings.allowed_origin.startswith("https://127.0.0.1:") or settings.invitation_delivery_enabled:
            raise ValueError("CAL-2 is restricted to the owned local synthetic fixture")
    pilot_reservations = settings.cal2_mode == "synthetic-pilot"
    reservations_enabled = local_reservations or pilot_reservations
    portal_admission = (
        AdmissionPolicy(PORTAL_ADMISSION.roles | {"company_contact"})
        if reservations_enabled else PORTAL_ADMISSION
    )
    engine = engine_factory(settings.database_url)
    session_repository = PostgresSessionRepository(engine)
    calendar_session_repository = PostgresSessionRepository(
        engine,
        accepted_roles=CALENDAR_SESSION_ROLES,
    )
    login_repository = PostgresLoginRepository(engine)
    password_service = PasswordService(
        PasswordPolicy(settings.compromised_password_fingerprints)
    )
    dummy_password_hash = password_service.hash(secrets.token_urlsafe(32))
    login_service = LoginService(
        login_repository,
        password_service,
        dummy_password_hash=dummy_password_hash,
        rate_limit_hmac_key=settings.rate_limit_hmac_key,
    )
    portal_login_service = LoginService(
        login_repository,
        password_service,
        dummy_password_hash=dummy_password_hash,
        rate_limit_hmac_key=settings.rate_limit_hmac_key,
        admission_policy=portal_admission,
    )
    totp_secret_cipher = SecretCipher(
        settings.totp_encryption_keys,
        settings.totp_active_key_version,
    )
    mfa_service = MfaService(
        PostgresMfaRepository(engine),
        totp_secret_cipher,
        recovery_hmac_keys=settings.recovery_hmac_keys,
        recovery_active_key_version=settings.recovery_hmac_active_key_version,
        rate_limit_hmac_key=settings.rate_limit_hmac_key,
        session_idle_timeout=settings.session_idle_timeout,
    )
    portal_mfa_service = MfaService(
        PostgresMfaRepository(engine, admission_policy=portal_admission),
        totp_secret_cipher,
        recovery_hmac_keys=settings.recovery_hmac_keys,
        recovery_active_key_version=settings.recovery_hmac_active_key_version,
        rate_limit_hmac_key=settings.rate_limit_hmac_key,
        session_idle_timeout=settings.session_idle_timeout,
    )
    company_service = CompanyService(PostgresCompanyRepository(engine))
    calendar_service = CalendarService(PostgresCalendarRepository(engine, reservation_checks=reservations_enabled))
    calendar_cursor_hmac_key = hmac.new(
        settings.idempotency_hmac_key,
        b"competence-hub:calendar-public-cursor:v1",
        hashlib.sha256,
    ).digest()
    outbox_cipher = SecretCipher(
        settings.outbox_encryption_keys,
        settings.outbox_active_key_version,
        context="auth-token-outbox",
    )
    account_lifecycle_service = AccountLifecycleService(
        PostgresAccountLifecycleRepository(engine),
        password_service,
        rate_limit_hmac_key=settings.rate_limit_hmac_key,
        idempotency_hmac_key=settings.idempotency_hmac_key,
        outbox_cipher=outbox_cipher,
    )

    async def readiness_probe() -> bool:
        return await database_is_ready(
            engine,
            timeout_seconds=settings.readiness_timeout_seconds,
        )

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        try:
            if pilot_reservations:
                try:
                    await _verify_cal2_pilot(engine)
                except (SQLAlchemyError, OSError):
                    raise RuntimeError("CAL-2 pilot database verification failed") from None
            if reservations_enabled and await _customer_schema_ready(engine):
                application.state.customer_administration = CustomerAdministration(engine)
            yield
        finally:
            application.state.customer_administration = None
            await engine.dispose()

    app = create_app(
        readiness_probe=readiness_probe,
        session_repository=session_repository,
        calendar_session_repository=calendar_session_repository,
        portal_session_repository=PostgresSessionRepository(
            engine, accepted_roles=portal_admission.roles
        ),
        portal_login_service=portal_login_service,
        portal_mfa_service=portal_mfa_service,
        login_service=login_service,
        mfa_service=mfa_service,
        account_lifecycle_service=account_lifecycle_service,
        company_service=company_service,
        calendar_service=calendar_service,
        reservation_repository=ReservationRepository(engine, settings.idempotency_hmac_key) if reservations_enabled else None,
        calendar_cursor_hmac_key=calendar_cursor_hmac_key,
        allowed_origin=settings.allowed_origin,
        session_idle_timeout=settings.session_idle_timeout,
        lifespan=lifespan,
    )
    app.state.database_engine = engine
    # Enabling dispatch is an explicit runtime release decision, not inferred
    # from the presence of keys or an SMTP password.
    app.state.invitation_delivery_enabled = settings.invitation_delivery_enabled
    app.state.totp_secret_cipher = totp_secret_cipher
    app.state.outbox_cipher = outbox_cipher
    app.state.recovery_hmac_active_key_version = (
        settings.recovery_hmac_active_key_version
    )
    return app


def create_runtime_app_from_environment(
    environment: Mapping[str, str] | None = None,
) -> FastAPI:
    return create_runtime_app(RuntimeSettings.from_environment(environment))
