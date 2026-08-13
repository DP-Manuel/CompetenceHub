import pytest

from competence_hub_api.security.passwords import (
    PasswordPolicy,
    PasswordPolicyError,
    PasswordService,
    password_fingerprint,
)


@pytest.fixture
def service() -> PasswordService:
    compromised = {password_fingerprint("synthetic compromised password")}
    return PasswordService(PasswordPolicy(compromised))


def test_password_hash_is_argon2id_and_verifiable(service: PasswordService) -> None:
    password = "synthetic passphrase with spaces"

    encoded = service.hash(password)

    assert encoded.startswith("$argon2id$")
    assert password not in encoded
    assert service.verify(encoded, password)
    assert not service.verify(encoded, "wrong synthetic passphrase")


@pytest.mark.parametrize(
    ("password", "expected_code"),
    [
        ("too short", "password_too_short"),
        ("x" * 129, "password_too_long"),
        ("Synthetic Compromised Password", "password_compromised"),
    ],
)
def test_password_policy_rejects_unsafe_input(
    service: PasswordService,
    password: str,
    expected_code: str,
) -> None:
    with pytest.raises(PasswordPolicyError) as error:
        service.hash(password)

    assert error.value.code == expected_code


def test_invalid_hash_fails_closed(service: PasswordService) -> None:
    assert not service.verify("not-an-argon2-hash", "synthetic passphrase")
    assert service.needs_rehash("not-an-argon2-hash")
