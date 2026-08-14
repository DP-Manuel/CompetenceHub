from datetime import UTC, datetime
from uuid import UUID

import pytest

from competence_hub_api import admin_cli
from competence_hub_api.security.passwords import password_fingerprint

NOW = datetime(2026, 8, 14, 14, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-4000-8000-000000000081")
DATABASE_URL = (
    "postgresql+asyncpg://competence_hub_app:synthetic@"
    "127.0.0.1:55432/competence_hub_staging"
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeEngine:
    def __init__(self) -> None:
        self.disposed = False

    async def dispose(self) -> None:
        self.disposed = True


class FakeRepository:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.created: list[dict] = []

    async def create_initial_admin(self, **values):
        self.created.append(values)
        return USER_ID


@pytest.mark.anyio
async def test_interactive_cli_keeps_password_out_of_arguments_and_repository(
    tmp_path,
    monkeypatch,
) -> None:
    fingerprint_source = tmp_path / "compromised.sha256"
    fingerprint_source.write_text(
        password_fingerprint("synthetic compromised password") + "\n",
        encoding="ascii",
    )
    environment = {
        admin_cli.DATABASE_URL_ENV: DATABASE_URL,
        admin_cli.COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV: str(
            fingerprint_source
        ),
    }
    engine = FakeEngine()
    engine_calls: list[tuple[str, dict]] = []
    repository_holder: list[FakeRepository] = []

    def engine_factory(database_url: str, **options):
        engine_calls.append((database_url, options))
        return engine

    def repository_factory(value):
        repository = FakeRepository(value)
        repository_holder.append(repository)
        return repository

    monkeypatch.setattr(
        admin_cli,
        "PostgresInitialAdminRepository",
        repository_factory,
    )
    inputs = iter(("admin@example.invalid", "Synthetic Admin"))
    passwords = iter(("synthetic secure passphrase", "synthetic secure passphrase"))

    await admin_cli.create_initial_admin_interactively(
        environment=environment,
        input_reader=lambda _: next(inputs),
        password_reader=lambda _: next(passwords),
        engine_factory=engine_factory,
        terminal_check=lambda: True,
        now=NOW,
    )

    assert engine_calls == [
        (
            DATABASE_URL,
            {"pool_pre_ping": True, "hide_parameters": True},
        )
    ]
    assert engine.disposed
    created = repository_holder[0].created[0]
    assert created["normalized_email"] == "admin@example.invalid"
    assert created["display_name"] == "Synthetic Admin"
    assert created["password_hash"].startswith("$argon2id$")
    assert "synthetic secure passphrase" not in repr(created)


@pytest.mark.anyio
async def test_password_mismatch_stops_before_database_connection(
    tmp_path,
) -> None:
    fingerprint_source = tmp_path / "compromised.sha256"
    fingerprint_source.write_text("a" * 64 + "\n", encoding="ascii")
    environment = {
        admin_cli.DATABASE_URL_ENV: DATABASE_URL,
        admin_cli.COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV: str(
            fingerprint_source
        ),
    }
    inputs = iter(("admin@example.invalid", "Synthetic Admin"))
    passwords = iter(("first synthetic password", "different synthetic password"))

    with pytest.raises(ValueError, match="confirmation"):
        await admin_cli.create_initial_admin_interactively(
            environment=environment,
            input_reader=lambda _: next(inputs),
            password_reader=lambda _: next(passwords),
            engine_factory=lambda *_args, **_kwargs: pytest.fail(
                "database engine must not be created"
            ),
            terminal_check=lambda: True,
            now=NOW,
        )


@pytest.mark.anyio
async def test_non_interactive_execution_fails_before_reading_configuration() -> None:
    with pytest.raises(admin_cli.RuntimeConfigurationError, match="interactive"):
        await admin_cli.create_initial_admin_interactively(
            environment={},
            input_reader=lambda _: pytest.fail("input must not be read"),
            password_reader=lambda _: pytest.fail("password must not be read"),
            terminal_check=lambda: False,
        )


def test_main_reports_generic_failure_without_exception_details(monkeypatch) -> None:
    async def fail(**_kwargs):
        raise ValueError("synthetic secure passphrase")

    monkeypatch.setattr(admin_cli, "create_initial_admin_interactively", fail)
    output: list[str] = []

    exit_code = admin_cli.main(
        ["create-initial-admin"],
        environment={},
        output=output.append,
    )

    assert exit_code == 2
    assert output == [
        "Initial administrator was not created: configuration or input failed."
    ]
    assert "synthetic secure passphrase" not in repr(output)
