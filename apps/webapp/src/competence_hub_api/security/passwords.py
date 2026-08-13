import hashlib
from collections.abc import Collection
from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError


class PasswordPolicyError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def password_fingerprint(password: str) -> str:
    normalized = password.casefold().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


@dataclass(frozen=True)
class PasswordPolicy:
    compromised_fingerprints: Collection[str]
    minimum_length: int = 12
    maximum_length: int = 128

    def validate(self, password: str) -> None:
        if len(password) < self.minimum_length:
            raise PasswordPolicyError("password_too_short")
        if len(password) > self.maximum_length:
            raise PasswordPolicyError("password_too_long")
        if password_fingerprint(password) in self.compromised_fingerprints:
            raise PasswordPolicyError("password_compromised")


class PasswordService:
    def __init__(self, policy: PasswordPolicy) -> None:
        self._policy = policy
        self._hasher = PasswordHasher()

    def hash(self, password: str) -> str:
        self._policy.validate(password)
        return self._hasher.hash(password)

    def verify(self, encoded_hash: str, password: str) -> bool:
        try:
            return self._hasher.verify(encoded_hash, password)
        except (InvalidHashError, VerifyMismatchError):
            return False

    def needs_rehash(self, encoded_hash: str) -> bool:
        try:
            return self._hasher.check_needs_rehash(encoded_hash)
        except InvalidHashError:
            return True
