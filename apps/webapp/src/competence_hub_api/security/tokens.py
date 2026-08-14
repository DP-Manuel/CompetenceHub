import hashlib
import hmac
import secrets
from dataclasses import dataclass, field as dataclass_field

TOKEN_BYTES = 32
MAX_TOKEN_CHARACTERS = 128


@dataclass(frozen=True)
class IssuedToken:
    plaintext: str = dataclass_field(repr=False)
    digest: bytes = dataclass_field(repr=False)


def digest_token(token: str) -> bytes:
    if not token:
        raise ValueError("token must not be empty")
    if len(token) > MAX_TOKEN_CHARACTERS:
        raise ValueError("token is too long")

    try:
        encoded_token = token.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError("token must contain ASCII characters only") from error

    return hashlib.sha256(encoded_token).digest()


def keyed_digest(value: str, key: bytes) -> bytes:
    if not value:
        raise ValueError("value must not be empty")
    if len(key) < TOKEN_BYTES:
        raise ValueError("HMAC key must contain at least 256 bits")
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).digest()


def issue_token() -> IssuedToken:
    plaintext = secrets.token_urlsafe(TOKEN_BYTES)
    return IssuedToken(plaintext=plaintext, digest=digest_token(plaintext))
