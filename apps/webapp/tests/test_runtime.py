from contextlib import AbstractAsyncContextManager
from datetime import timedelta
from types import TracebackType
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from competence_hub_api.auth.postgres_session_repository import (
    PostgresSessionRepository,
)
from competence_hub_api.auth.login_service import LoginService
from competence_hub_api.portal.companies import CompanyService
from competence_hub_api.config import RuntimeSettings
from competence_hub_api.runtime import (
    create_database_engine,
    create_runtime_app,
    database_is_ready,
)


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
        totp_encryption_keys={"synthetic-v1": b"t" * 32},
        totp_active_key_version="synthetic-v1",
        recovery_hmac_keys={"synthetic-v1": b"r" * 32},
        recovery_hmac_active_key_version="synthetic-v1",
    )


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
    assert isinstance(app.state.login_service, LoginService)
    assert isinstance(app.state.company_service, CompanyService)
    assert app.state.allowed_origin == "https://portal.example.invalid"
    assert app.state.totp_secret_cipher.active_key_version == "synthetic-v1"
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
