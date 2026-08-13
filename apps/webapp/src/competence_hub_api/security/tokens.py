import hashlib
import hmac
import secrets
from dataclasses import dataclass

TOKEN_BYTES = 32


@dataclass(frozen=True)
class IssuedToken:
    plaintext: str
    digest: bytes


def digest_token(token: str) -> bytes:
    if not token:
        raise ValueError("token must not be empty")
    return hashlib.sha256(token.encode("ascii")).digest()


def keyed_digest(value: str, key: bytes) -> bytes:
    if not value:
        raise ValueError("value must not be empty")
    if len(key) < TOKEN_BYTES:
        raise ValueError("HMAC key must contain at least 256 bits")
    return hmac.new(key, value.encode("utf-8"), hashlib.sha256).digest()


def issue_token() -> IssuedToken:
    plaintext = secrets.token_urlsafe(TOKEN_BYTES)
    return IssuedToken(plaintext=plaintext, digest=digest_token(plaintext))
