import pytest

from competence_hub_api.security.recovery_codes import (
    RECOVERY_CODE_COUNT,
    issue_recovery_codes,
    normalize_recovery_code,
    recovery_code_digest,
    recovery_code_matches,
)

FIRST_KEY = b"a" * 32
SECOND_KEY = b"b" * 32


def test_recovery_codes_are_unique_human_readable_and_hidden_from_repr() -> None:
    issued = issue_recovery_codes(FIRST_KEY, key_version="recovery-v1")

    assert len(issued) == RECOVERY_CODE_COUNT
    assert len({item.plaintext for item in issued}) == RECOVERY_CODE_COUNT
    assert all(len(item.plaintext) == 19 for item in issued)
    assert all(item.key_version == "recovery-v1" for item in issued)
    assert all(item.plaintext not in repr(item) for item in issued)
    assert all(item.digest.hex() not in repr(item) for item in issued)


def test_recovery_code_normalization_and_hmac_matching() -> None:
    code = "ABCD-EFGH-JKLM-NPQR"
    digest = recovery_code_digest(code, FIRST_KEY, key_version="recovery-v1")

    assert normalize_recovery_code("abcd efgh-jklm npqr") == "ABCDEFGHJKLMNPQR"
    assert recovery_code_matches(
        "abcd efgh-jklm npqr",
        digest,
        FIRST_KEY,
        key_version="recovery-v1",
    )
    assert not recovery_code_matches(
        "ABCD-EFGH-JKLM-NPQT",
        digest,
        FIRST_KEY,
        key_version="recovery-v1",
    )


def test_recovery_digest_is_key_and_version_specific() -> None:
    code = "ABCD-EFGH-JKLM-NPQR"

    assert recovery_code_digest(code, FIRST_KEY, key_version="v1") != recovery_code_digest(
        code,
        SECOND_KEY,
        key_version="v1",
    )
    assert recovery_code_digest(code, FIRST_KEY, key_version="v1") != recovery_code_digest(
        code,
        FIRST_KEY,
        key_version="v2",
    )


@pytest.mark.parametrize("code", ["", "ABCD", "ABCD-EFGH-JKLM-NPQ1", "äBCD-EFGH-JKLM-NPQR"])
def test_invalid_recovery_codes_fail_closed(code: str) -> None:
    assert not recovery_code_matches(
        code,
        b"x" * 32,
        FIRST_KEY,
        key_version="v1",
    )


def test_recovery_code_configuration_rejects_short_keys_and_empty_versions() -> None:
    with pytest.raises(ValueError, match="256 bits"):
        issue_recovery_codes(b"short", key_version="v1")
    with pytest.raises(ValueError, match="must not be empty"):
        issue_recovery_codes(FIRST_KEY, key_version="")
