from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta
import base64
import binascii
import json
import os
import re
from types import MappingProxyType
from urllib.parse import urlsplit

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

DATABASE_URL_ENV = "COMPETENCE_HUB_DATABASE_URL"
ALLOWED_ORIGIN_ENV = "COMPETENCE_HUB_ALLOWED_ORIGIN"
SESSION_IDLE_MINUTES_ENV = "COMPETENCE_HUB_SESSION_IDLE_MINUTES"
READINESS_TIMEOUT_SECONDS_ENV = "COMPETENCE_HUB_READINESS_TIMEOUT_SECONDS"
RATE_LIMIT_HMAC_KEY_ENV = "COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY"
TOTP_KEYRING_ENV = "COMPETENCE_HUB_TOTP_KEYRING"
TOTP_ACTIVE_KEY_VERSION_ENV = "COMPETENCE_HUB_TOTP_ACTIVE_KEY_VERSION"
RECOVERY_HMAC_KEYRING_ENV = "COMPETENCE_HUB_RECOVERY_HMAC_KEYRING"
RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV = (
    "COMPETENCE_HUB_RECOVERY_HMAC_ACTIVE_KEY_VERSION"
)
KEY_VERSION_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class RuntimeConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class RuntimeSettings:
    database_url: str = field(repr=False)
    allowed_origin: str
    session_idle_timeout: timedelta
    readiness_timeout_seconds: int = 5
    rate_limit_hmac_key: bytes = field(default=b"", repr=False)
    totp_encryption_keys: Mapping[str, bytes] = field(
        default_factory=dict,
        repr=False,
    )
    totp_active_key_version: str = ""
    recovery_hmac_keys: Mapping[str, bytes] = field(
        default_factory=dict,
        repr=False,
    )
    recovery_hmac_active_key_version: str = ""

    def __post_init__(self) -> None:
        _validate_database_url(self.database_url)
        _validate_allowed_origin(self.allowed_origin)
        idle_seconds = self.session_idle_timeout.total_seconds()
        if not 60 <= idle_seconds <= 60 * 60:
            raise RuntimeConfigurationError(
                "session idle timeout must be between 1 and 60 minutes"
            )
        if not 1 <= self.readiness_timeout_seconds <= 30:
            raise RuntimeConfigurationError(
                "readiness timeout must be between 1 and 30 seconds"
            )
        if len(self.rate_limit_hmac_key) < 32:
            raise RuntimeConfigurationError(
                f"{RATE_LIMIT_HMAC_KEY_ENV} must decode to at least 256 bits"
            )
        normalized_keyring = dict(self.totp_encryption_keys)
        if not normalized_keyring:
            raise RuntimeConfigurationError(f"{TOTP_KEYRING_ENV} must not be empty")
        for version, key in normalized_keyring.items():
            _validate_key_version(version, TOTP_KEYRING_ENV)
            if len(key) != 32:
                raise RuntimeConfigurationError(
                    f"{TOTP_KEYRING_ENV} values must decode to exactly 256 bits"
                )
        _validate_key_version(
            self.totp_active_key_version,
            TOTP_ACTIVE_KEY_VERSION_ENV,
        )
        if self.totp_active_key_version not in normalized_keyring:
            raise RuntimeConfigurationError(
                f"{TOTP_ACTIVE_KEY_VERSION_ENV} must identify a configured key"
            )
        normalized_recovery_keys = dict(self.recovery_hmac_keys)
        if not normalized_recovery_keys:
            raise RuntimeConfigurationError(
                f"{RECOVERY_HMAC_KEYRING_ENV} must not be empty"
            )
        for version, key in normalized_recovery_keys.items():
            _validate_key_version(version, RECOVERY_HMAC_KEYRING_ENV)
            if len(key) < 32:
                raise RuntimeConfigurationError(
                    f"{RECOVERY_HMAC_KEYRING_ENV} values must decode to at least 256 bits"
                )
        _validate_key_version(
            self.recovery_hmac_active_key_version,
            RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV,
        )
        if self.recovery_hmac_active_key_version not in normalized_recovery_keys:
            raise RuntimeConfigurationError(
                f"{RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV} must identify a configured key"
            )
        object.__setattr__(
            self,
            "totp_encryption_keys",
            MappingProxyType(normalized_keyring),
        )
        object.__setattr__(
            self,
            "recovery_hmac_keys",
            MappingProxyType(normalized_recovery_keys),
        )

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
    ) -> "RuntimeSettings":
        values = os.environ if environment is None else environment
        database_url = _required(values, DATABASE_URL_ENV)
        allowed_origin = _required(values, ALLOWED_ORIGIN_ENV)
        idle_minutes = _positive_integer(
            values.get(SESSION_IDLE_MINUTES_ENV, "30"),
            SESSION_IDLE_MINUTES_ENV,
            maximum=60,
        )
        readiness_timeout_seconds = _positive_integer(
            values.get(READINESS_TIMEOUT_SECONDS_ENV, "5"),
            READINESS_TIMEOUT_SECONDS_ENV,
            maximum=30,
        )
        rate_limit_hmac_key = _base64_key(
            _required(values, RATE_LIMIT_HMAC_KEY_ENV),
            RATE_LIMIT_HMAC_KEY_ENV,
        )
        totp_encryption_keys = _base64_keyring(
            _required(values, TOTP_KEYRING_ENV),
        )
        totp_active_key_version = _required(
            values,
            TOTP_ACTIVE_KEY_VERSION_ENV,
        )
        recovery_hmac_keys = _base64_keyring(
            _required(values, RECOVERY_HMAC_KEYRING_ENV),
            name=RECOVERY_HMAC_KEYRING_ENV,
            exact_bytes=None,
        )
        recovery_hmac_active_key_version = _required(
            values,
            RECOVERY_HMAC_ACTIVE_KEY_VERSION_ENV,
        )

        return cls(
            database_url=database_url,
            allowed_origin=allowed_origin,
            session_idle_timeout=timedelta(minutes=idle_minutes),
            readiness_timeout_seconds=readiness_timeout_seconds,
            rate_limit_hmac_key=rate_limit_hmac_key,
            totp_encryption_keys=totp_encryption_keys,
            totp_active_key_version=totp_active_key_version,
            recovery_hmac_keys=recovery_hmac_keys,
            recovery_hmac_active_key_version=recovery_hmac_active_key_version,
        )


def _required(values: Mapping[str, str], name: str) -> str:
    value = values.get(name, "").strip()
    if not value:
        raise RuntimeConfigurationError(f"{name} is required")
    return value


def _positive_integer(value: str, name: str, *, maximum: int) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise RuntimeConfigurationError(
            f"{name} must be an integer between 1 and {maximum}"
        ) from error

    if not 1 <= parsed <= maximum:
        raise RuntimeConfigurationError(
            f"{name} must be an integer between 1 and {maximum}"
        )
    return parsed


def _base64_key(value: str, name: str) -> bytes:
    try:
        decoded = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as error:
        raise RuntimeConfigurationError(
            f"{name} must be valid base64 encoding"
        ) from error

    if len(decoded) < 32:
        raise RuntimeConfigurationError(
            f"{name} must decode to at least 256 bits"
        )
    return decoded


def _base64_keyring(
    value: str,
    *,
    name: str = TOTP_KEYRING_ENV,
    exact_bytes: int | None = 32,
) -> Mapping[str, bytes]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise RuntimeConfigurationError(
            f"{name} must be a JSON object of base64 keys"
        ) from error
    if not isinstance(parsed, dict) or not parsed:
        raise RuntimeConfigurationError(
            f"{name} must be a non-empty JSON object"
        )

    keyring: dict[str, bytes] = {}
    for version, encoded_key in parsed.items():
        if not isinstance(version, str) or not isinstance(encoded_key, str):
            raise RuntimeConfigurationError(
                f"{name} must map key versions to base64 strings"
            )
        _validate_key_version(version, name)
        decoded = _base64_key(encoded_key, name)
        if exact_bytes is not None and len(decoded) != exact_bytes:
            raise RuntimeConfigurationError(
                f"{name} values must decode to exactly {exact_bytes * 8} bits"
            )
        keyring[version] = decoded
    return keyring


def _validate_key_version(value: str, name: str) -> None:
    if not KEY_VERSION_PATTERN.fullmatch(value):
        raise RuntimeConfigurationError(
            f"{name} must use a 1-64 character key version"
        )


def _validate_database_url(value: str) -> None:
    try:
        url = make_url(value)
    except ArgumentError as error:
        raise RuntimeConfigurationError(
            f"{DATABASE_URL_ENV} must be a valid SQLAlchemy URL"
        ) from error

    if url.drivername != "postgresql+asyncpg":
        raise RuntimeConfigurationError(
            f"{DATABASE_URL_ENV} must use postgresql+asyncpg"
        )
    if url.host not in {"localhost", "127.0.0.1", "::1"}:
        raise RuntimeConfigurationError(
            f"{DATABASE_URL_ENV} must use a loopback database host"
        )
    if not url.username or not url.password or not url.database:
        raise RuntimeConfigurationError(
            f"{DATABASE_URL_ENV} must include user, password and database"
        )
    if url.username != "competence_hub_app":
        raise RuntimeConfigurationError(
            f"{DATABASE_URL_ENV} must use the restricted competence_hub_app role"
        )


def validate_app_database_url(value: str) -> None:
    _validate_database_url(value)


def _validate_allowed_origin(value: str) -> None:
    try:
        origin = urlsplit(value)
        origin.port
    except ValueError as error:
        raise RuntimeConfigurationError(
            f"{ALLOWED_ORIGIN_ENV} must be an exact HTTPS origin"
        ) from error

    if (
        origin.scheme != "https"
        or not origin.hostname
        or origin.username is not None
        or origin.password is not None
        or origin.path
        or origin.query
        or origin.fragment
        or "*" in value
    ):
        raise RuntimeConfigurationError(
            f"{ALLOWED_ORIGIN_ENV} must be an exact HTTPS origin"
        )
