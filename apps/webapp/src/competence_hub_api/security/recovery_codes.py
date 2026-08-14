import base64
from dataclasses import dataclass, field
import hashlib
import hmac
import secrets

RECOVERY_CODE_BYTES = 10
RECOVERY_CODE_CHARACTERS = 16
RECOVERY_CODE_COUNT = 10
RECOVERY_CODE_GROUP = 4
MINIMUM_HMAC_KEY_BYTES = 32


@dataclass(frozen=True)
class IssuedRecoveryCode:
    plaintext: str = field(repr=False)
    digest: bytes = field(repr=False)
    key_version: str


def issue_recovery_codes(
    hmac_key: bytes,
    *,
    key_version: str,
    count: int = RECOVERY_CODE_COUNT,
) -> tuple[IssuedRecoveryCode, ...]:
    _validate_key(hmac_key, key_version)
    if not 1 <= count <= 20:
        raise ValueError("recovery code count must be between 1 and 20")

    issued: list[IssuedRecoveryCode] = []
    normalized_seen: set[str] = set()
    while len(issued) < count:
        normalized = base64.b32encode(secrets.token_bytes(RECOVERY_CODE_BYTES)).decode(
            "ascii"
        )
        if normalized in normalized_seen:
            continue
        normalized_seen.add(normalized)
        issued.append(
            IssuedRecoveryCode(
                plaintext=_format(normalized),
                digest=recovery_code_digest(
                    normalized,
                    hmac_key,
                    key_version=key_version,
                ),
                key_version=key_version,
            )
        )
    return tuple(issued)


def recovery_code_digest(
    code: str,
    hmac_key: bytes,
    *,
    key_version: str,
) -> bytes:
    _validate_key(hmac_key, key_version)
    normalized = normalize_recovery_code(code)
    message = f"competence-hub:recovery:v1:{key_version}:{normalized}".encode("ascii")
    return hmac.new(hmac_key, message, hashlib.sha256).digest()


def normalize_recovery_code(code: str) -> str:
    normalized = "".join(character for character in code.upper() if not character.isspace() and character != "-")
    if (
        len(normalized) != RECOVERY_CODE_CHARACTERS
        or not normalized.isascii()
        or any(character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567" for character in normalized)
    ):
        raise ValueError("recovery code format is invalid")
    return normalized


def recovery_code_matches(
    code: str,
    expected_digest: bytes,
    hmac_key: bytes,
    *,
    key_version: str,
) -> bool:
    try:
        candidate = recovery_code_digest(code, hmac_key, key_version=key_version)
    except ValueError:
        candidate = b"\x00" * hashlib.sha256().digest_size
    return hmac.compare_digest(candidate, expected_digest)


def _format(normalized: str) -> str:
    return "-".join(
        normalized[index : index + RECOVERY_CODE_GROUP]
        for index in range(0, len(normalized), RECOVERY_CODE_GROUP)
    )


def _validate_key(hmac_key: bytes, key_version: str) -> None:
    if len(hmac_key) < MINIMUM_HMAC_KEY_BYTES:
        raise ValueError("recovery HMAC key must contain at least 256 bits")
    if not key_version.strip():
        raise ValueError("recovery HMAC key version must not be empty")
