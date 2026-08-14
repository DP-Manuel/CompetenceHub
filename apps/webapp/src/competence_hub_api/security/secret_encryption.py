from collections.abc import Mapping
from dataclasses import dataclass, field
import secrets
from types import MappingProxyType

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENVELOPE_MAGIC = b"CHT1"
NONCE_BYTES = 12
AES_256_KEY_BYTES = 32


class SecretEncryptionError(ValueError):
    pass


@dataclass(frozen=True)
class EncryptedSecret:
    envelope: bytes = field(repr=False)
    key_version: str


class SecretCipher:
    def __init__(
        self,
        keys: Mapping[str, bytes],
        active_key_version: str,
        *,
        context: str = "totp",
    ) -> None:
        normalized_keys = dict(keys)
        if not normalized_keys:
            raise SecretEncryptionError("at least one encryption key is required")
        if not active_key_version or active_key_version not in normalized_keys:
            raise SecretEncryptionError("active encryption key version is unavailable")
        for version, key in normalized_keys.items():
            if not version.strip():
                raise SecretEncryptionError("encryption key versions must not be empty")
            if len(key) != AES_256_KEY_BYTES:
                raise SecretEncryptionError("encryption keys must contain 256 bits")
        normalized_context = context.strip()
        if not normalized_context or len(normalized_context) > 64:
            raise SecretEncryptionError("encryption context is invalid")

        self._keys = MappingProxyType(normalized_keys)
        self._active_key_version = active_key_version
        self._context = normalized_context

    def __repr__(self) -> str:
        return (
            f"SecretCipher(context={self._context!r}, "
            f"active_key_version={self._active_key_version!r}, "
            f"key_count={len(self._keys)})"
        )

    @property
    def active_key_version(self) -> str:
        return self._active_key_version

    @property
    def context(self) -> str:
        return self._context

    def encrypt(self, plaintext: str, *, subject_id: str) -> EncryptedSecret:
        if not plaintext:
            raise SecretEncryptionError("secret plaintext must not be empty")
        associated_data = _associated_data(
            self._context,
            subject_id,
            self._active_key_version,
        )
        nonce = secrets.token_bytes(NONCE_BYTES)
        ciphertext = AESGCM(self._keys[self._active_key_version]).encrypt(
            nonce,
            plaintext.encode("ascii"),
            associated_data,
        )
        return EncryptedSecret(
            envelope=ENVELOPE_MAGIC + nonce + ciphertext,
            key_version=self._active_key_version,
        )

    def decrypt(
        self,
        envelope: bytes,
        *,
        key_version: str,
        subject_id: str,
    ) -> str:
        key = self._keys.get(key_version)
        if key is None:
            raise SecretEncryptionError("secret encryption key version is unavailable")
        if (
            len(envelope) <= len(ENVELOPE_MAGIC) + NONCE_BYTES
            or not envelope.startswith(ENVELOPE_MAGIC)
        ):
            raise SecretEncryptionError("encrypted secret envelope is invalid")

        nonce_start = len(ENVELOPE_MAGIC)
        nonce_end = nonce_start + NONCE_BYTES
        nonce = envelope[nonce_start:nonce_end]
        ciphertext = envelope[nonce_end:]
        try:
            plaintext = AESGCM(key).decrypt(
                nonce,
                ciphertext,
                _associated_data(self._context, subject_id, key_version),
            )
            return plaintext.decode("ascii")
        except (InvalidTag, UnicodeDecodeError) as error:
            raise SecretEncryptionError("encrypted secret could not be authenticated") from error


def _associated_data(context: str, subject_id: str, key_version: str) -> bytes:
    normalized_subject = subject_id.strip()
    if not normalized_subject:
        raise SecretEncryptionError("secret subject ID must not be empty")
    return (
        f"competence-hub:{context}:v1:{key_version}:{normalized_subject}"
    ).encode("utf-8")
