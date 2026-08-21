from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta
import base64
import binascii
import json
import os
from pathlib import Path
import re
from types import MappingProxyType
from urllib.parse import SplitResult, urlsplit

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from competence_hub_api.security.email_addresses import is_single_email_address
from competence_hub_api.security.passwords import load_compromised_password_fingerprints

DATABASE_URL_ENV = "COMPETENCE_HUB_DATABASE_URL"
ALLOWED_ORIGIN_ENV = "COMPETENCE_HUB_ALLOWED_ORIGIN"
SESSION_IDLE_MINUTES_ENV = "COMPETENCE_HUB_SESSION_IDLE_MINUTES"
READINESS_TIMEOUT_SECONDS_ENV = "COMPETENCE_HUB_READINESS_TIMEOUT_SECONDS"
RATE_LIMIT_HMAC_KEY_ENV = "COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY"
IDEMPOTENCY_HMAC_KEY_ENV = "COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY"
OUTBOX_KEYRING_ENV = "COMPETENCE_HUB_OUTBOX_KEYRING"
OUTBOX_ACTIVE_KEY_VERSION_ENV = "COMPETENCE_HUB_OUTBOX_ACTIVE_KEY_VERSION"
COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV = (
    "COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH"
)
ACCOUNT_ACTION_BASE_URL_ENV = "COMPETENCE_HUB_ACCOUNT_ACTION_BASE_URL"
SMTP_HOST_ENV = "COMPETENCE_HUB_SMTP_HOST"
SMTP_PORT_ENV = "COMPETENCE_HUB_SMTP_PORT"
SMTP_TLS_MODE_ENV = "COMPETENCE_HUB_SMTP_TLS_MODE"
SMTP_USERNAME_ENV = "COMPETENCE_HUB_SMTP_USERNAME"
SMTP_PASSWORD_ENV = "COMPETENCE_HUB_SMTP_PASSWORD"
SMTP_FROM_ENV = "COMPETENCE_HUB_SMTP_FROM"
SMTP_REPLY_TO_ENV = "COMPETENCE_HUB_SMTP_REPLY_TO"
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
    idempotency_hmac_key: bytes = field(default=b"", repr=False)
    outbox_encryption_keys: Mapping[str, bytes] = field(
        default_factory=dict,
        repr=False,
    )
    outbox_active_key_version: str = ""
    compromised_password_fingerprints: frozenset[str] = field(
        default_factory=frozenset,
        repr=False,
    )
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
        if len(self.idempotency_hmac_key) < 32:
            raise RuntimeConfigurationError(
                f"{IDEMPOTENCY_HMAC_KEY_ENV} must decode to at least 256 bits"
            )
        normalized_outbox_keys = dict(self.outbox_encryption_keys)
        if not normalized_outbox_keys:
            raise RuntimeConfigurationError(f"{OUTBOX_KEYRING_ENV} must not be empty")
        for version, key in normalized_outbox_keys.items():
            _validate_key_version(version, OUTBOX_KEYRING_ENV)
            if len(key) != 32:
                raise RuntimeConfigurationError(
                    f"{OUTBOX_KEYRING_ENV} values must decode to exactly 256 bits"
                )
        _validate_key_version(
            self.outbox_active_key_version,
            OUTBOX_ACTIVE_KEY_VERSION_ENV,
        )
        if self.outbox_active_key_version not in normalized_outbox_keys:
            raise RuntimeConfigurationError(
                f"{OUTBOX_ACTIVE_KEY_VERSION_ENV} must identify a configured key"
            )
        if not self.compromised_password_fingerprints:
            raise RuntimeConfigurationError(
                f"{COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV} must contain fingerprints"
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
            "outbox_encryption_keys",
            MappingProxyType(normalized_outbox_keys),
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
        idempotency_hmac_key = _base64_key(
            _required(values, IDEMPOTENCY_HMAC_KEY_ENV),
            IDEMPOTENCY_HMAC_KEY_ENV,
        )
        outbox_encryption_keys = _base64_keyring(
            _required(values, OUTBOX_KEYRING_ENV),
            name=OUTBOX_KEYRING_ENV,
        )
        outbox_active_key_version = _required(
            values,
            OUTBOX_ACTIVE_KEY_VERSION_ENV,
        )
        fingerprint_path_value = _required(
            values,
            COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV,
        )
        fingerprint_path = Path(fingerprint_path_value)
        if not fingerprint_path.is_absolute():
            raise RuntimeConfigurationError(
                f"{COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV} must be absolute"
            )
        try:
            compromised_password_fingerprints = (
                load_compromised_password_fingerprints(fingerprint_path)
            )
        except (OSError, ValueError) as error:
            raise RuntimeConfigurationError(
                f"{COMPROMISED_PASSWORD_FINGERPRINTS_PATH_ENV} is not a valid fingerprint source"
            ) from error
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
            idempotency_hmac_key=idempotency_hmac_key,
            outbox_encryption_keys=outbox_encryption_keys,
            outbox_active_key_version=outbox_active_key_version,
            compromised_password_fingerprints=compromised_password_fingerprints,
            totp_encryption_keys=totp_encryption_keys,
            totp_active_key_version=totp_active_key_version,
            recovery_hmac_keys=recovery_hmac_keys,
            recovery_hmac_active_key_version=recovery_hmac_active_key_version,
        )


@dataclass(frozen=True)
class TokenDeliverySettings:
    database_url: str = field(repr=False)
    outbox_encryption_keys: Mapping[str, bytes] = field(repr=False)
    outbox_active_key_version: str
    allowed_origin: str
    account_action_base_url: str
    smtp_host: str
    smtp_port: int
    smtp_tls_mode: str
    smtp_username: str = field(repr=False)
    smtp_password: str = field(repr=False)
    smtp_from: str
    smtp_reply_to: str

    def __post_init__(self) -> None:
        _validate_database_url(self.database_url)
        normalized_outbox_keys = dict(self.outbox_encryption_keys)
        if not normalized_outbox_keys:
            raise RuntimeConfigurationError(f"{OUTBOX_KEYRING_ENV} must not be empty")
        for version, key in normalized_outbox_keys.items():
            _validate_key_version(version, OUTBOX_KEYRING_ENV)
            if len(key) != 32:
                raise RuntimeConfigurationError(
                    f"{OUTBOX_KEYRING_ENV} values must decode to exactly 256 bits"
                )
        _validate_key_version(self.outbox_active_key_version, OUTBOX_ACTIVE_KEY_VERSION_ENV)
        if self.outbox_active_key_version not in normalized_outbox_keys:
            raise RuntimeConfigurationError(
                f"{OUTBOX_ACTIVE_KEY_VERSION_ENV} must identify a configured key"
            )
        _validate_allowed_origin(self.allowed_origin)
        _validate_account_action_base_url(
            self.account_action_base_url,
            allowed_origin=self.allowed_origin,
        )
        _validate_smtp_host(self.smtp_host)
        if not 1 <= self.smtp_port <= 65535:
            raise RuntimeConfigurationError(
                f"{SMTP_PORT_ENV} must be an integer between 1 and 65535"
            )
        if self.smtp_tls_mode not in {"starttls", "implicit"}:
            raise RuntimeConfigurationError(
                f"{SMTP_TLS_MODE_ENV} must be starttls or implicit"
            )
        if not self.smtp_username or not self.smtp_password:
            raise RuntimeConfigurationError("SMTP authentication is required")
        _validate_email_address(self.smtp_from, SMTP_FROM_ENV)
        _validate_email_address(self.smtp_reply_to, SMTP_REPLY_TO_ENV)
        object.__setattr__(
            self,
            "outbox_encryption_keys",
            MappingProxyType(normalized_outbox_keys),
        )

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
    ) -> "TokenDeliverySettings":
        values = os.environ if environment is None else environment
        return cls(
            database_url=_required(values, DATABASE_URL_ENV),
            outbox_encryption_keys=_base64_keyring(
                _required(values, OUTBOX_KEYRING_ENV),
                name=OUTBOX_KEYRING_ENV,
            ),
            outbox_active_key_version=_required(
                values,
                OUTBOX_ACTIVE_KEY_VERSION_ENV,
            ),
            allowed_origin=_required(values, ALLOWED_ORIGIN_ENV),
            account_action_base_url=_required(values, ACCOUNT_ACTION_BASE_URL_ENV),
            smtp_host=_required(values, SMTP_HOST_ENV),
            smtp_port=_positive_integer(
                _required(values, SMTP_PORT_ENV),
                SMTP_PORT_ENV,
                maximum=65535,
            ),
            smtp_tls_mode=_required(values, SMTP_TLS_MODE_ENV).casefold(),
            smtp_username=_required(values, SMTP_USERNAME_ENV),
            smtp_password=_required(values, SMTP_PASSWORD_ENV),
            smtp_from=_required(values, SMTP_FROM_ENV),
            smtp_reply_to=_required(values, SMTP_REPLY_TO_ENV),
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


def _validate_account_action_base_url(value: str, *, allowed_origin: str) -> None:
    try:
        target = urlsplit(value)
        target.port
    except ValueError as error:
        raise RuntimeConfigurationError(
            f"{ACCOUNT_ACTION_BASE_URL_ENV} must be a valid HTTPS portal URL"
        ) from error
    if (
        target.scheme != "https"
        or not target.hostname
        or target.username is not None
        or target.password is not None
        or target.query
        or target.fragment
        or target.path != "/portal/"
        or _origin_identity(target) != _origin_identity(urlsplit(allowed_origin))
    ):
        raise RuntimeConfigurationError(
            f"{ACCOUNT_ACTION_BASE_URL_ENV} must be a valid HTTPS portal URL"
        )


def _validate_smtp_host(value: str) -> None:
    if (
        not value
        or any(character.isspace() for character in value)
        or "://" in value
        or "/" in value
    ):
        raise RuntimeConfigurationError(f"{SMTP_HOST_ENV} must be a hostname")


def _validate_email_address(value: str, name: str) -> None:
    if not is_single_email_address(value):
        raise RuntimeConfigurationError(f"{name} must be a single email address")


def _origin_identity(value: SplitResult) -> tuple[str, str, int]:
    return (
        value.scheme.casefold(),
        (value.hostname or "").casefold(),
        value.port or 443,
    )
