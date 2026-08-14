import argparse
import asyncio
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
import getpass
import os
from pathlib import Path
import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from competence_hub_api.auth.account_administration import (
    InitialAdminAlreadyExistsError,
    InitialAdminConfigurationError,
    InitialAdminService,
)
from competence_hub_api.auth.postgres_account_administration import (
    PostgresInitialAdminRepository,
)
from competence_hub_api.config import (
    DATABASE_URL_ENV,
    RuntimeConfigurationError,
    validate_app_database_url,
)
from competence_hub_api.security.passwords import (
    PasswordPolicy,
    PasswordPolicyError,
    PasswordService,
    load_compromised_password_fingerprints,
)

COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV = (
    "COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH"
)
InputReader = Callable[[str], str]
PasswordReader = Callable[[str], str]
OutputWriter = Callable[[str], None]
EngineFactory = Callable[[str], AsyncEngine]
TerminalCheck = Callable[[], bool]


def _has_interactive_terminal() -> bool:
    return sys.stdin.isatty() and sys.stderr.isatty()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="competence-hub-admin")
    parser.add_argument(
        "command",
        choices=("create-initial-admin",),
        help="run a bounded interactive administration command",
    )
    return parser


def _required_environment(values: Mapping[str, str], name: str) -> str:
    value = values.get(name, "").strip()
    if not value:
        raise RuntimeConfigurationError(f"{name} is required")
    return value


async def create_initial_admin_interactively(
    *,
    environment: Mapping[str, str],
    input_reader: InputReader = input,
    password_reader: PasswordReader = getpass.getpass,
    engine_factory: EngineFactory = create_async_engine,
    terminal_check: TerminalCheck = _has_interactive_terminal,
    now: datetime | None = None,
) -> None:
    if not terminal_check():
        raise RuntimeConfigurationError("an interactive terminal is required")
    database_url = _required_environment(environment, DATABASE_URL_ENV)
    validate_app_database_url(database_url)
    fingerprint_path = Path(
        _required_environment(
            environment,
            COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV,
        )
    )
    if not fingerprint_path.is_absolute() or not fingerprint_path.is_file():
        raise RuntimeConfigurationError(
            f"{COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV} must identify "
            "an absolute regular file"
        )
    compromised_fingerprints = load_compromised_password_fingerprints(
        fingerprint_path
    )

    email = input_reader("Initial admin email: ")
    display_name = input_reader("Initial admin display name: ")
    password = password_reader("Initial admin password: ")
    password_confirmation = password_reader("Repeat initial admin password: ")
    if password != password_confirmation:
        raise ValueError("password confirmation does not match")

    engine = engine_factory(
        database_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    try:
        service = InitialAdminService(
            PostgresInitialAdminRepository(engine),
            PasswordService(PasswordPolicy(compromised_fingerprints)),
        )
        await service.create_initial_admin(
            email=email,
            display_name=display_name,
            password=password,
            now=now or datetime.now(UTC),
        )
    finally:
        password = ""
        password_confirmation = ""
        await engine.dispose()


def main(
    argv: Sequence[str] | None = None,
    *,
    environment: Mapping[str, str] | None = None,
    output: OutputWriter = print,
) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.command != "create-initial-admin":
        return 2

    try:
        asyncio.run(
            create_initial_admin_interactively(
                environment=os.environ if environment is None else environment,
            )
        )
    except InitialAdminAlreadyExistsError:
        output("Initial administrator was not created: bootstrap is closed.")
        return 3
    except (
        InitialAdminConfigurationError,
        PasswordPolicyError,
        RuntimeConfigurationError,
        SQLAlchemyError,
        OSError,
        ValueError,
    ):
        output("Initial administrator was not created: configuration or input failed.")
        return 2

    output("Initial administrator created. Complete MFA enrollment before use.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
