from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import AsyncContextManager

from fastapi import FastAPI

from competence_hub_api.auth.account_lifecycle import (
    AccountLifecycleService,
)
from competence_hub_api.auth.login_service import LoginService
from competence_hub_api.auth.mfa_service import MfaService
from competence_hub_api.auth.session_repository import SessionRepository
from competence_hub_api.portal.companies import CompanyService
from competence_hub_api.web.auth import (
    DEFAULT_SESSION_IDLE_TIMEOUT,
    router as auth_router,
    utc_now,
)
from competence_hub_api.web.admin import router as admin_router
from competence_hub_api.web.companies import router as companies_router
from competence_hub_api.web.health import router as health_router
from competence_hub_api.web.middleware import SecurityHeadersMiddleware

ReadinessProbe = Callable[[], Awaitable[bool]]
Clock = Callable[[], datetime]
Lifespan = Callable[[FastAPI], AsyncContextManager[None]]


async def not_ready() -> bool:
    return False


def create_app(
    readiness_probe: ReadinessProbe | None = None,
    *,
    session_repository: SessionRepository | None = None,
    login_service: LoginService | None = None,
    mfa_service: MfaService | None = None,
    account_lifecycle_service: AccountLifecycleService | None = None,
    company_service: CompanyService | None = None,
    allowed_origin: str | None = None,
    session_idle_timeout: timedelta = DEFAULT_SESSION_IDLE_TIMEOUT,
    clock: Clock = utc_now,
    lifespan: Lifespan | None = None,
) -> FastAPI:
    if session_idle_timeout.total_seconds() <= 0:
        raise ValueError("session idle timeout must be positive")

    app = FastAPI(
        title="Competence Hub API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.state.readiness_probe = readiness_probe or not_ready
    app.state.session_repository = session_repository
    app.state.login_service = login_service
    app.state.mfa_service = mfa_service
    app.state.account_lifecycle_service = account_lifecycle_service
    app.state.company_service = company_service
    app.state.allowed_origin = allowed_origin
    app.state.session_idle_timeout = session_idle_timeout
    app.state.clock = clock
    app.add_middleware(SecurityHeadersMiddleware)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(companies_router)
    return app


app = create_app()
