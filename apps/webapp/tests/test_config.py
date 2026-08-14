from datetime import timedelta
import base64
import json

import pytest

from competence_hub_api.config import (
    ALLOWED_ORIGIN_ENV,
    DATABASE_URL_ENV,
    RATE_LIMIT_HMAC_KEY_ENV,
    READINESS_TIMEOUT_SECONDS_ENV,
    RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV,
    RECOVERY_HMAC_KEYRING_ENV,
    SESSION_IDLE_MINUTES_ENV,
    TOTP_ACTIVE_KEY_VERSION_ENV,
    TOTP_KEYRING_ENV,
    RuntimeConfigurationError,
    RuntimeSettings,
)

DATABASE_URL = (
    "postgresql+asyncpg://competence_hub_app:synthetic-password@"
    "127.0.0.1:5432/competence_hub_staging"
)
RATE_LIMIT_HMAC_KEY = b"synthetic-rate-limit-key-32-bytes"
TOTP_KEY = b"t" * 32
RECOVERY_HMAC_KEY = b"r" * 32


def valid_environment() -> dict[str, str]:
    return {
        DATABASE_URL_ENV: DATABASE_URL,
        ALLOWED_ORIGIN_ENV: "https://portal.example.invalid",
        RATE_LIMIT_HMAC_KEY_ENV: base64.b64encode(RATE_LIMIT_HMAC_KEY).decode("ascii"),
        TOTP_KEYRING_ENV: json.dumps(
            {"synthetic-v1": base64.b64encode(TOTP_KEY).decode("ascii")}
        ),
        TOTP_ACTIVE_KEY_VERSION_ENV: "synthetic-v1",
        RECOVERY_HMAC_KEYRING_ENV: json.dumps(
            {
                "synthetic-v1": base64.b64encode(RECOVERY_HMAC_KEY).decode(
                    "ascii"
                )
            }
        ),
        RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV: "synthetic-v1",
    }


def test_runtime_settings_accept_safe_loopback_configuration() -> None:
    environment = valid_environment()
    environment[SESSION_IDLE_MINUTES_ENV] = "15"

    settings = RuntimeSettings.from_environment(environment)

    assert settings.database_url == DATABASE_URL
    assert settings.allowed_origin == "https://portal.example.invalid"
    assert settings.session_idle_timeout == timedelta(minutes=15)
    assert settings.readiness_timeout_seconds == 5
    assert settings.rate_limit_hmac_key == RATE_LIMIT_HMAC_KEY
    assert settings.totp_encryption_keys == {"synthetic-v1": TOTP_KEY}
    assert settings.totp_active_key_version == "synthetic-v1"
    assert settings.recovery_hmac_keys == {"synthetic-v1": RECOVERY_HMAC_KEY}
    assert settings.recovery_hmac_active_key_version == "synthetic-v1"
    assert "synthetic-password" not in repr(settings)
    assert RATE_LIMIT_HMAC_KEY.hex() not in repr(settings)
    assert TOTP_KEY.hex() not in repr(settings)
    assert RECOVERY_HMAC_KEY.hex() not in repr(settings)


def test_direct_runtime_settings_cannot_bypass_validation() -> None:
    with pytest.raises(RuntimeConfigurationError, match="loopback"):
        RuntimeSettings(
            database_url=(
                "postgresql+asyncpg://competence_hub_app:synthetic-password@"
                "db.example.invalid/competence_hub_staging"
            ),
            allowed_origin="https://portal.example.invalid",
            session_idle_timeout=timedelta(minutes=30),
            rate_limit_hmac_key=RATE_LIMIT_HMAC_KEY,
            totp_encryption_keys={"synthetic-v1": TOTP_KEY},
            totp_active_key_version="synthetic-v1",
            recovery_hmac_keys={"synthetic-v1": RECOVERY_HMAC_KEY},
            recovery_hmac_active_key_version="synthetic-v1",
        )


@pytest.mark.parametrize(
    "missing_name",
    [
        DATABASE_URL_ENV,
        ALLOWED_ORIGIN_ENV,
        RATE_LIMIT_HMAC_KEY_ENV,
        TOTP_KEYRING_ENV,
        TOTP_ACTIVE_KEY_VERSION_ENV,
        RECOVERY_HMAC_KEYRING_ENV,
        RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV,
    ],
)
def test_runtime_settings_fail_closed_when_required_values_are_missing(
    missing_name: str,
) -> None:
    environment = valid_environment()
    del environment[missing_name]

    with pytest.raises(RuntimeConfigurationError, match=missing_name):
        RuntimeSettings.from_environment(environment)


@pytest.mark.parametrize(
    "database_url",
    [
        "not-a-url",
        "postgresql://user:password@127.0.0.1/database",
        "postgresql+asyncpg://user:password@db.example.invalid/database",
        "postgresql+asyncpg://user@127.0.0.1/database",
        "postgresql+asyncpg://user:password@127.0.0.1",
        "postgresql+asyncpg://competence_hub_migrator:password@127.0.0.1/database",
    ],
)
def test_runtime_settings_reject_unsafe_database_urls(database_url: str) -> None:
    environment = valid_environment()
    environment[DATABASE_URL_ENV] = database_url

    with pytest.raises(RuntimeConfigurationError) as error:
        RuntimeSettings.from_environment(environment)

    assert database_url not in str(error.value)


@pytest.mark.parametrize(
    "origin",
    [
        "http://portal.example.invalid",
        "https://*.example.invalid",
        "https://portal.example.invalid/",
        "https://portal.example.invalid/path",
        "https://user:password@portal.example.invalid",
    ],
)
def test_runtime_settings_reject_non_exact_https_origins(origin: str) -> None:
    environment = valid_environment()
    environment[ALLOWED_ORIGIN_ENV] = origin

    with pytest.raises(RuntimeConfigurationError, match=ALLOWED_ORIGIN_ENV):
        RuntimeSettings.from_environment(environment)


@pytest.mark.parametrize("idle_minutes", ["0", "61", "1.5", "not-a-number"])
def test_runtime_settings_reject_invalid_idle_timeouts(idle_minutes: str) -> None:
    environment = valid_environment()
    environment[SESSION_IDLE_MINUTES_ENV] = idle_minutes

    with pytest.raises(RuntimeConfigurationError, match=SESSION_IDLE_MINUTES_ENV):
        RuntimeSettings.from_environment(environment)


@pytest.mark.parametrize("timeout_seconds", ["0", "31", "1.5", "not-a-number"])
def test_runtime_settings_reject_invalid_readiness_timeouts(
    timeout_seconds: str,
) -> None:
    environment = valid_environment()
    environment[READINESS_TIMEOUT_SECONDS_ENV] = timeout_seconds

    with pytest.raises(
        RuntimeConfigurationError,
        match=READINESS_TIMEOUT_SECONDS_ENV,
    ):
        RuntimeSettings.from_environment(environment)


@pytest.mark.parametrize(
    "encoded_key",
    ["not valid base64", base64.b64encode(b"too-short").decode("ascii")],
)
def test_runtime_settings_reject_invalid_rate_limit_hmac_keys(
    encoded_key: str,
) -> None:
    environment = valid_environment()
    environment[RATE_LIMIT_HMAC_KEY_ENV] = encoded_key

    with pytest.raises(RuntimeConfigurationError, match=RATE_LIMIT_HMAC_KEY_ENV):
        RuntimeSettings.from_environment(environment)


@pytest.mark.parametrize(
    "keyring",
    [
        "not-json",
        "{}",
        json.dumps({"invalid version": base64.b64encode(TOTP_KEY).decode("ascii")}),
        json.dumps({"v1": base64.b64encode(b"too-short").decode("ascii")}),
    ],
)
def test_runtime_settings_reject_invalid_totp_keyrings(keyring: str) -> None:
    environment = valid_environment()
    environment[TOTP_KEYRING_ENV] = keyring

    with pytest.raises(RuntimeConfigurationError, match=TOTP_KEYRING_ENV):
        RuntimeSettings.from_environment(environment)


def test_runtime_settings_reject_unknown_active_totp_key_version() -> None:
    environment = valid_environment()
    environment[TOTP_ACTIVE_KEY_VERSION_ENV] = "missing-v2"

    with pytest.raises(
        RuntimeConfigurationError,
        match=TOTP_ACTIVE_KEY_VERSION_ENV,
    ):
        RuntimeSettings.from_environment(environment)


@pytest.mark.parametrize(
    "encoded_key",
    ["not valid base64", base64.b64encode(b"too-short").decode("ascii")],
)
def test_runtime_settings_reject_invalid_recovery_hmac_keyrings(
    encoded_key: str,
) -> None:
    environment = valid_environment()
    environment[RECOVERY_HMAC_KEYRING_ENV] = (
        encoded_key
        if encoded_key == "not valid base64"
        else json.dumps({"v1": encoded_key})
    )

    with pytest.raises(RuntimeConfigurationError, match=RECOVERY_HMAC_KEYRING_ENV):
        RuntimeSettings.from_environment(environment)


def test_runtime_settings_reject_unknown_active_recovery_key_version() -> None:
    environment = valid_environment()
    environment[RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV] = "missing-v2"

    with pytest.raises(
        RuntimeConfigurationError,
        match=RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV,
    ):
        RuntimeSettings.from_environment(environment)
