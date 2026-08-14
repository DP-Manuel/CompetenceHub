import pytest

from competence_hub_api.security.secret_encryption import (
    ENVELOPE_MAGIC,
    EncryptedSecret,
    SecretCipher,
    SecretEncryptionError,
)

FIRST_KEY = b"a" * 32
SECOND_KEY = b"b" * 32
SUBJECT_ID = "00000000-0000-0000-0000-000000000001"


def test_secret_cipher_encrypts_and_authenticates_subject_binding() -> None:
    cipher = SecretCipher({"v1": FIRST_KEY}, "v1")

    encrypted = cipher.encrypt("SYNTHETICTOTPSECRET", subject_id=SUBJECT_ID)

    assert encrypted.envelope.startswith(ENVELOPE_MAGIC)
    assert b"SYNTHETICTOTPSECRET" not in encrypted.envelope
    assert encrypted.key_version == "v1"
    assert cipher.decrypt(
        encrypted.envelope,
        key_version=encrypted.key_version,
        subject_id=SUBJECT_ID,
    ) == "SYNTHETICTOTPSECRET"
    assert "SYNTHETICTOTPSECRET" not in repr(encrypted)
    assert FIRST_KEY.hex() not in repr(cipher)


def test_secret_cipher_uses_random_nonce_for_each_encryption() -> None:
    cipher = SecretCipher({"v1": FIRST_KEY}, "v1")

    first = cipher.encrypt("SYNTHETICTOTPSECRET", subject_id=SUBJECT_ID)
    second = cipher.encrypt("SYNTHETICTOTPSECRET", subject_id=SUBJECT_ID)

    assert first.envelope != second.envelope


def test_secret_cipher_reads_old_key_during_rotation_and_writes_active_key() -> None:
    old_cipher = SecretCipher({"v1": FIRST_KEY}, "v1")
    old_secret = old_cipher.encrypt("SYNTHETICTOTPSECRET", subject_id=SUBJECT_ID)
    rotated_cipher = SecretCipher({"v1": FIRST_KEY, "v2": SECOND_KEY}, "v2")

    assert rotated_cipher.decrypt(
        old_secret.envelope,
        key_version="v1",
        subject_id=SUBJECT_ID,
    ) == "SYNTHETICTOTPSECRET"
    assert rotated_cipher.encrypt(
        "SYNTHETICTOTPSECRET",
        subject_id=SUBJECT_ID,
    ).key_version == "v2"


def test_secret_cipher_context_prevents_cross_domain_decryption() -> None:
    totp_cipher = SecretCipher({"v1": FIRST_KEY}, "v1", context="totp")
    outbox_cipher = SecretCipher(
        {"v1": FIRST_KEY},
        "v1",
        context="auth-token-outbox",
    )
    encrypted = totp_cipher.encrypt("SYNTHETICTOTPSECRET", subject_id=SUBJECT_ID)

    with pytest.raises(SecretEncryptionError, match="authenticated"):
        outbox_cipher.decrypt(
            encrypted.envelope,
            key_version=encrypted.key_version,
            subject_id=SUBJECT_ID,
        )


@pytest.mark.parametrize("subject_id", ["different-user", ""])
def test_secret_cipher_rejects_wrong_or_empty_subject(subject_id: str) -> None:
    cipher = SecretCipher({"v1": FIRST_KEY}, "v1")
    encrypted = cipher.encrypt("SYNTHETICTOTPSECRET", subject_id=SUBJECT_ID)

    with pytest.raises(SecretEncryptionError):
        cipher.decrypt(
            encrypted.envelope,
            key_version="v1",
            subject_id=subject_id,
        )


def test_secret_cipher_rejects_tampering_unknown_keys_and_invalid_key_sizes() -> None:
    cipher = SecretCipher({"v1": FIRST_KEY}, "v1")
    encrypted = cipher.encrypt("SYNTHETICTOTPSECRET", subject_id=SUBJECT_ID)
    tampered = encrypted.envelope[:-1] + bytes([encrypted.envelope[-1] ^ 1])

    with pytest.raises(SecretEncryptionError, match="authenticated"):
        cipher.decrypt(tampered, key_version="v1", subject_id=SUBJECT_ID)
    with pytest.raises(SecretEncryptionError, match="unavailable"):
        cipher.decrypt(encrypted.envelope, key_version="missing", subject_id=SUBJECT_ID)
    with pytest.raises(SecretEncryptionError, match="256 bits"):
        SecretCipher({"v1": b"short"}, "v1")


def test_encrypted_secret_repr_never_contains_envelope() -> None:
    encrypted = EncryptedSecret(envelope=b"private-envelope", key_version="v1")

    assert b"private-envelope" != repr(encrypted).encode("utf-8")
