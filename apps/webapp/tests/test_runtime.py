from contextlib import AbstractAsyncContextManager
from dataclasses import replace
from datetime import timedelta
from types import TracebackType
from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from competence_hub_api.auth.postgres_session_repository import (
    PostgresSessionRepository,
)
from competence_hub_api.auth.login_service import LoginService
from competence_hub_api.auth.account_lifecycle import AccountLifecycleService
from competence_hub_api.portal.companies import CompanyService
from competence_hub_api.config import RuntimeConfigurationError, RuntimeSettings
from competence_hub_api import runtime
from competence_hub_api.portal.requests import CoachingRequestRepository
from competence_hub_api.runtime import (
    create_database_engine,
    create_runtime_app,
    database_is_ready,
)
from competence_hub_api.auth.admission import INTERNAL_ADMISSION, PORTAL_ADMISSION


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeConnection:
    def __init__(self) -> None:
        self.statements: list[str] = []

    async def execute(self, statement: Any) -> None:
        self.statements.append(str(statement))


class ConnectionContext(AbstractAsyncContextManager[FakeConnection]):
    def __init__(
        self,
        connection: FakeConnection,
        error: BaseException | None = None,
    ) -> None:
        self.connection = connection
        self.error = error

    async def __aenter__(self) -> FakeConnection:
        if self.error is not None:
            raise self.error
        return self.connection

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class FakeEngine:
    def __init__(self, error: BaseException | None = None) -> None:
        self.connection = FakeConnection()
        self.error = error
        self.disposed = False

    def connect(self) -> ConnectionContext:
        return ConnectionContext(self.connection, self.error)

    async def dispose(self) -> None:
        self.disposed = True


def runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        database_url=(
            "postgresql+asyncpg://competence_hub_app:synthetic-password@"
            "127.0.0.1:5432/competence_hub_staging"
        ),
        allowed_origin="https://portal.example.invalid",
        session_idle_timeout=timedelta(minutes=30),
        readiness_timeout_seconds=5,
        rate_limit_hmac_key=b"synthetic-rate-limit-key-32-bytes",
        idempotency_hmac_key=b"synthetic-idempotency-key-32bytes",
        outbox_encryption_keys={"synthetic-v1": b"o" * 32},
        outbox_active_key_version="synthetic-v1",
        compromised_password_fingerprints=frozenset({"0" * 64}),
        totp_encryption_keys={"synthetic-v1": b"t" * 32},
        totp_active_key_version="synthetic-v1",
        recovery_hmac_keys={"synthetic-v1": b"r" * 32},
        recovery_hmac_active_key_version="synthetic-v1",
    )


def test_private_cal2_mode_only_accepts_the_isolated_database_and_origin():
    base = runtime_settings()
    pilot_url = base.database_url.replace("competence_hub_staging", "competence_hub_v2_pilot")
    expected = {"database_url": pilot_url, "allowed_origin": "https://localhost:8447",
                "cal2_mode": "synthetic-pilot"}
    assert replace(base, **expected).cal2_mode == "synthetic-pilot"
    for forbidden in (
        {"database_url": base.database_url},
        {"allowed_origin": base.allowed_origin},
        {"invitation_delivery_enabled": True},
        {"database_url": pilot_url + "?application_name=override"},
        {"cal2_mode": "production"},
    ):
        with pytest.raises(RuntimeConfigurationError):
            replace(base, **{**expected, **forbidden})


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mode, schema_ready, enabled",
    [
        ("default", True, False), ("local", True, True), ("local_override", True, False),
        ("pilot", True, True), ("pilot", False, False),
    ],
)
async def test_requests_requires_a_synthetic_runtime_and_schema(monkeypatch, mode, schema_ready, enabled):
    base = runtime_settings()
    local = mode in {"local", "local_override"}
    if local:
        url = base.database_url.replace(":5432/", ":55433/")
        if mode == "local_override":
            url += "?host=127.0.0.2"
        base = replace(base, database_url=url, allowed_origin="https://127.0.0.1:8447")
    elif mode == "pilot":
        base = replace(
            base, database_url=base.database_url.replace("competence_hub_staging", "competence_hub_v2_pilot"),
            allowed_origin="https://localhost:8447", cal2_mode="synthetic-pilot",
        )
    engine = FakeEngine()
    pilot_check = AsyncMock()
    schema_check = AsyncMock(return_value=schema_ready)
    monkeypatch.setattr(runtime, "_verify_cal2_pilot", pilot_check)
    monkeypatch.setattr(runtime, "_customer_schema_ready", AsyncMock(return_value=True))
    monkeypatch.setattr(runtime, "_request_schema_ready", schema_check)

    app = create_runtime_app(base, engine_factory=lambda _url: engine, local_reservations=local)
    assert app.state.coaching_request_repository is None
    async with app.router.lifespan_context(app):
        assert isinstance(app.state.coaching_request_repository, CoachingRequestRepository) is enabled
        assert (app.state.reservation_repository is not None) is (mode != "default")
        assert (app.state.customer_administration is not None) is (mode != "default")
    assert app.state.coaching_request_repository is None
    assert engine.disposed
    assert schema_check.await_count == int(mode in {"local", "pilot"})
    assert pilot_check.await_count == int(mode == "pilot")


@pytest.mark.anyio
async def test_database_engine_hides_parameters_in_errors_and_logs() -> None:
    engine = create_database_engine(runtime_settings().database_url)

    assert engine.sync_engine.hide_parameters is True

    await engine.dispose()


@pytest.mark.anyio
async def test_database_readiness_executes_a_minimal_query() -> None:
    engine = FakeEngine()

    assert await database_is_ready(engine) is True  # type: ignore[arg-type]
    assert engine.connection.statements == ["SELECT 1"]


@pytest.mark.anyio
async def test_database_readiness_reports_dependency_failure() -> None:
    engine = FakeEngine(SQLAlchemyError("synthetic database failure"))

    assert await database_is_ready(engine) is False  # type: ignore[arg-type]


@pytest.mark.anyio
async def test_database_readiness_reports_socket_failure() -> None:
    engine = FakeEngine(OSError("synthetic connection refusal"))

    assert await database_is_ready(engine) is False  # type: ignore[arg-type]


@pytest.mark.anyio
async def test_database_readiness_respects_runtime_timeout() -> None:
    engine = FakeEngine()

    assert await database_is_ready(
        engine,  # type: ignore[arg-type]
        timeout_seconds=1,
    ) is True


@pytest.mark.anyio
async def test_runtime_app_wires_repository_origin_and_readiness() -> None:
    engine = FakeEngine()
    app = create_runtime_app(
        runtime_settings(),
        engine_factory=lambda _: engine,  # type: ignore[arg-type,return-value]
    )

    assert isinstance(app.state.session_repository, PostgresSessionRepository)
    assert isinstance(
        app.state.calendar_session_repository, PostgresSessionRepository
    )
    assert app.state.session_repository.accepted_roles == ("admin", "internal")
    assert app.state.login_service.admission_policy == INTERNAL_ADMISSION
    assert app.state.portal_login_service.admission_policy == PORTAL_ADMISSION
    assert app.state.portal_session_repository.accepted_roles == (
        "admin", "calendar_reviewer", "coach", "internal"
    )
    assert app.state.portal_mfa_service._repository.admission_policy == PORTAL_ADMISSION
    assert app.state.mfa_service._repository.admission_policy == INTERNAL_ADMISSION
    assert app.state.calendar_session_repository.accepted_roles == (
        "admin",
        "calendar_reviewer",
        "coach",
        "company_contact",
        "internal",
    )
    assert isinstance(app.state.login_service, LoginService)
    assert isinstance(app.state.account_lifecycle_service, AccountLifecycleService)
    assert isinstance(app.state.company_service, CompanyService)
    assert app.state.allowed_origin == "https://portal.example.invalid"
    assert app.state.totp_secret_cipher.active_key_version == "synthetic-v1"
    assert app.state.outbox_cipher.active_key_version == "synthetic-v1"
    assert app.state.recovery_hmac_active_key_version == "synthetic-v1"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://test.invalid",
    ) as client:
        response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.anyio
async def test_runtime_app_disposes_engine_on_shutdown() -> None:
    engine = FakeEngine()
    app = create_runtime_app(
        runtime_settings(),
        engine_factory=lambda _: engine,  # type: ignore[arg-type,return-value]
    )

    async with app.router.lifespan_context(app):
        assert engine.disposed is False

    assert engine.disposed is True


@pytest.mark.anyio
async def test_database_errors_never_log_row_payload_or_return_details(caplog) -> None:
    app = create_runtime_app(runtime_settings(), engine_factory=lambda _: FakeEngine())

    @app.get("/synthetic-database-failure")
    async def fail():
        raise SQLAlchemyError("DETAIL: Failing row contains synthetic-private-token-payload")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test.invalid") as client:
        response = await client.get("/synthetic-database-failure")
    assert response.status_code == 503
    assert response.json()["code"] == "portal_unavailable"
    assert "synthetic-private" not in response.text
    assert "synthetic-private" not in caplog.text
    assert "database_operation_failed" in caplog.text
