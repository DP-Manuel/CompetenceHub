import base64

import pytest

from competence_hub_api.security.tokens import (
    TOKEN_BYTES,
    digest_token,
    issue_token,
    keyed_digest,
)


def test_issued_token_contains_256_bits_and_only_digest_is_for_storage() -> None:
    issued = issue_token()
    decoded = base64.urlsafe_b64decode(issued.plaintext + "==")

    assert len(decoded) == TOKEN_BYTES
    assert len(issued.digest) == 32
    assert issued.plaintext.encode("ascii") != issued.digest
    assert digest_token(issued.plaintext) == issued.digest


def test_tokens_are_unique() -> None:
    assert issue_token().plaintext != issue_token().plaintext


def test_empty_token_is_rejected() -> None:
    with pytest.raises(ValueError):
        digest_token("")


def test_low_entropy_identifier_uses_external_hmac_key() -> None:
    identifier = "synthetic-user@example.invalid|192.0.2.1"
    first_key = b"a" * TOKEN_BYTES
    second_key = b"b" * TOKEN_BYTES

    assert keyed_digest(identifier, first_key) == keyed_digest(identifier, first_key)
    assert keyed_digest(identifier, first_key) != keyed_digest(identifier, second_key)
    assert identifier.encode("utf-8") != keyed_digest(identifier, first_key)


def test_hmac_rejects_short_keys() -> None:
    with pytest.raises(ValueError):
        keyed_digest("synthetic identifier", b"too-short")
