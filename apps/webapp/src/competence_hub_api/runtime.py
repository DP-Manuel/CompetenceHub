import asyncio
from collections.abc import Callable, Mapping
from contextlib import asynccontextmanager
import secrets

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from competence_hub_api.auth.login_service import LoginService
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
from competence_hub_api.config import RuntimeSettings
from competence_hub_api.main import create_app
from competence_hub_api.portal.companies import CompanyService
from competence_hub_api.portal.postgres_companies import PostgresCompanyRepository
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.secret_encryption import SecretCipher

EngineFactory = Callable[[str], AsyncEngine]


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
) -> FastAPI:
    engine = engine_factory(settings.database_url)
    session_repository = PostgresSessionRepository(engine)
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
    company_service = CompanyService(PostgresCompanyRepository(engine))
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
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            await engine.dispose()

    app = create_app(
        readiness_probe=readiness_probe,
        session_repository=session_repository,
        login_service=login_service,
        mfa_service=mfa_service,
        account_lifecycle_service=account_lifecycle_service,
        company_service=company_service,
        allowed_origin=settings.allowed_origin,
        session_idle_timeout=settings.session_idle_timeout,
        lifespan=lifespan,
    )
    app.state.database_engine = engine
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
