from datetime import timedelta
import base64
import json
from pathlib import Path

import pytest

from competence_hub_api.config import (
    ALLOWED_ORIGIN_ENV,
    ACCOUNT_ACTION_BASE_URL_ENV,
    COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV,
    DATABASE_URL_ENV,
    IDEMPOTENCY_HMAC_KEY_ENV,
    OUTBOX_ACTIVE_KEY_VERSION_ENV,
    OUTBOX_KEYRING_ENV,
    RATE_LIMIT_HMAC_KEY_ENV,
    READINESS_TIMEOUT_SECONDS_ENV,
    RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV,
    RECOVERY_HMAC_KEYRING_ENV,
    SESSION_IDLE_MINUTES_ENV,
    TOTP_ACTIVE_KEY_VERSION_ENV,
    TOTP_KEYRING_ENV,
    RuntimeConfigurationError,
    RuntimeSettings,
    SMTP_FROM_ENV,
    SMTP_HOST_ENV,
    SMTP_PASSWORD_ENV,
    SMTP_PORT_ENV,
    SMTP_REPLY_TO_ENV,
    SMTP_TLS_MODE_ENV,
    SMTP_USERNAME_ENV,
    TokenDeliverySettings,
)

DATABASE_URL = (
    "postgresql+asyncpg://competence_hub_app:synthetic-password@"
    "127.0.0.1:5432/competence_hub_staging"
)
RATE_LIMIT_HMAC_KEY = b"synthetic-rate-limit-key-32-bytes"
TOTP_KEY = b"t" * 32
RECOVERY_HMAC_KEY = b"r" * 32
IDEMPOTENCY_HMAC_KEY = b"i" * 32
OUTBOX_KEY = b"o" * 32
FINGERPRINT_PATH = Path(__file__).with_name("fixtures").joinpath(
    "compromised-password-fingerprints.txt"
)


def valid_environment() -> dict[str, str]:
    return {
        DATABASE_URL_ENV: DATABASE_URL,
        ALLOWED_ORIGIN_ENV: "https://portal.example.invalid",
        RATE_LIMIT_HMAC_KEY_ENV: base64.b64encode(RATE_LIMIT_HMAC_KEY).decode("ascii"),
        IDEMPOTENCY_HMAC_KEY_ENV: base64.b64encode(IDEMPOTENCY_HMAC_KEY).decode(
            "ascii"
        ),
        OUTBOX_KEYRING_ENV: json.dumps(
            {"synthetic-v1": base64.b64encode(OUTBOX_KEY).decode("ascii")}
        ),
        OUTBOX_ACTIVE_KEY_VERSION_ENV: "synthetic-v1",
        COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV: str(FINGERPRINT_PATH),
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


def valid_delivery_environment() -> dict[str, str]:
    return {
        DATABASE_URL_ENV: DATABASE_URL,
        ALLOWED_ORIGIN_ENV: "https://portal.example.invalid",
        OUTBOX_KEYRING_ENV: json.dumps(
            {"synthetic-v1": base64.b64encode(OUTBOX_KEY).decode("ascii")}
        ),
        OUTBOX_ACTIVE_KEY_VERSION_ENV: "synthetic-v1",
        ACCOUNT_ACTION_BASE_URL_ENV: "https://portal.example.invalid/portal/",
        SMTP_HOST_ENV: "smtp.example.invalid",
        SMTP_PORT_ENV: "587",
        SMTP_TLS_MODE_ENV: "starttls",
        SMTP_USERNAME_ENV: "synthetic-user",
        SMTP_PASSWORD_ENV: "synthetic-password",
        SMTP_FROM_ENV: "portal@example.invalid",
        SMTP_REPLY_TO_ENV: "support@example.invalid",
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
    assert settings.idempotency_hmac_key == IDEMPOTENCY_HMAC_KEY
    assert settings.outbox_encryption_keys == {"synthetic-v1": OUTBOX_KEY}
    assert settings.outbox_active_key_version == "synthetic-v1"
    assert settings.compromised_password_fingerprints == frozenset({"0" * 64})
    assert settings.totp_encryption_keys == {"synthetic-v1": TOTP_KEY}
    assert settings.totp_active_key_version == "synthetic-v1"
    assert settings.recovery_hmac_keys == {"synthetic-v1": RECOVERY_HMAC_KEY}
    assert settings.recovery_hmac_active_key_version == "synthetic-v1"
    assert "synthetic-password" not in repr(settings)
    assert RATE_LIMIT_HMAC_KEY.hex() not in repr(settings)
    assert IDEMPOTENCY_HMAC_KEY.hex() not in repr(settings)
    assert OUTBOX_KEY.hex() not in repr(settings)
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
            idempotency_hmac_key=IDEMPOTENCY_HMAC_KEY,
            outbox_encryption_keys={"synthetic-v1": OUTBOX_KEY},
            outbox_active_key_version="synthetic-v1",
            compromised_password_fingerprints=frozenset({"0" * 64}),
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
        IDEMPOTENCY_HMAC_KEY_ENV,
        OUTBOX_KEYRING_ENV,
        OUTBOX_ACTIVE_KEY_VERSION_ENV,
        COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV,
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
    "environment_name",
    [IDEMPOTENCY_HMAC_KEY_ENV],
)
@pytest.mark.parametrize(
    "encoded_key",
    ["not valid base64", base64.b64encode(b"too-short").decode("ascii")],
)
def test_runtime_settings_reject_invalid_lifecycle_hmac_keys(
    environment_name: str,
    encoded_key: str,
) -> None:
    environment = valid_environment()
    environment[environment_name] = encoded_key

    with pytest.raises(RuntimeConfigurationError, match=environment_name):
        RuntimeSettings.from_environment(environment)


@pytest.mark.parametrize(
    "keyring",
    [
        "not-json",
        "{}",
        json.dumps({"invalid version": base64.b64encode(OUTBOX_KEY).decode("ascii")}),
        json.dumps({"v1": base64.b64encode(b"too-short").decode("ascii")}),
    ],
)
def test_runtime_settings_reject_invalid_outbox_keyrings(keyring: str) -> None:
    environment = valid_environment()
    environment[OUTBOX_KEYRING_ENV] = keyring

    with pytest.raises(RuntimeConfigurationError, match=OUTBOX_KEYRING_ENV):
        RuntimeSettings.from_environment(environment)


def test_runtime_settings_reject_unknown_active_outbox_key_version() -> None:
    environment = valid_environment()
    environment[OUTBOX_ACTIVE_KEY_VERSION_ENV] = "missing-v2"

    with pytest.raises(
        RuntimeConfigurationError,
        match=OUTBOX_ACTIVE_KEY_VERSION_ENV,
    ):
        RuntimeSettings.from_environment(environment)


@pytest.mark.parametrize("path", ["relative.txt", "C:/missing/fingerprints.txt"])
def test_runtime_settings_reject_invalid_fingerprint_sources(path: str) -> None:
    environment = valid_environment()
    environment[COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV] = path

    with pytest.raises(
        RuntimeConfigurationError,
        match=COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV,
    ):
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


def test_token_delivery_settings_accept_strict_smtp_configuration() -> None:
    settings = TokenDeliverySettings.from_environment(valid_delivery_environment())

    assert settings.account_action_base_url == "https://portal.example.invalid/portal/"
    assert settings.allowed_origin == "https://portal.example.invalid"
    assert settings.smtp_port == 587
    assert settings.smtp_tls_mode == "starttls"
    assert settings.outbox_encryption_keys == {"synthetic-v1": OUTBOX_KEY}
    assert "synthetic-password" not in repr(settings)
    assert "synthetic-user" not in repr(settings)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        (ACCOUNT_ACTION_BASE_URL_ENV, "http://portal.example.invalid/portal/"),
        (ACCOUNT_ACTION_BASE_URL_ENV, "https://portal.example.invalid/"),
        (ACCOUNT_ACTION_BASE_URL_ENV, "https://other.example.invalid/portal/"),
        (ACCOUNT_ACTION_BASE_URL_ENV, "https://portal.example.invalid/other/portal/"),
        (ACCOUNT_ACTION_BASE_URL_ENV, "https://portal.example.invalid/portal/?token=x"),
        (SMTP_HOST_ENV, "https://smtp.example.invalid"),
        (SMTP_PORT_ENV, "0"),
        (SMTP_TLS_MODE_ENV, "plain"),
        (SMTP_FROM_ENV, "not-an-email"),
        (SMTP_FROM_ENV, "portal@example.invalid,attacker@example.invalid"),
        (SMTP_REPLY_TO_ENV, "support@example.invalid\r\nBcc: attacker@example.invalid"),
    ],
)
def test_token_delivery_settings_reject_unsafe_values(name: str, value: str) -> None:
    environment = valid_delivery_environment()
    environment[name] = value

    with pytest.raises(RuntimeConfigurationError):
        TokenDeliverySettings.from_environment(environment)
