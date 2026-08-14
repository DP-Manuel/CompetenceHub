from datetime import datetime, timezone

import pyotp
import pytest

from competence_hub_api.security.totp import (
    TOTP_INTERVAL_SECONDS,
    generate_totp_secret,
    provisioning_uri,
    verify_totp,
)

SYNTHETIC_SECRET = "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"
CURRENT_TIME = datetime(2026, 8, 14, 12, 0, tzinfo=timezone.utc)


def code_at(offset_steps: int = 0) -> str:
    timestamp = CURRENT_TIME.timestamp() + offset_steps * TOTP_INTERVAL_SECONDS
    return pyotp.TOTP(SYNTHETIC_SECRET).at(timestamp)


def test_generated_totp_secret_has_160_bits() -> None:
    first = generate_totp_secret()
    second = generate_totp_secret()

    assert len(first) == 32
    assert first != second


def test_provisioning_uri_contains_issuer_and_account_without_secret_repr() -> None:
    uri = provisioning_uri(
        SYNTHETIC_SECRET,
        account_name="synthetic@example.invalid",
    )

    assert uri.startswith("otpauth://totp/Competence%20Hub:synthetic%40example.invalid")
    assert "issuer=Competence%20Hub" in uri


@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_totp_accepts_only_the_configured_clock_window(offset: int) -> None:
    result = verify_totp(SYNTHETIC_SECRET, code_at(offset), at=CURRENT_TIME)

    assert result is not None
    assert result.time_step == int(CURRENT_TIME.timestamp() // TOTP_INTERVAL_SECONDS) + offset


def test_totp_rejects_outside_window_and_replayed_time_step() -> None:
    outside = verify_totp(SYNTHETIC_SECRET, code_at(2), at=CURRENT_TIME)
    accepted = verify_totp(SYNTHETIC_SECRET, code_at(), at=CURRENT_TIME)

    assert outside is None
    assert accepted is not None
    assert verify_totp(
        SYNTHETIC_SECRET,
        code_at(),
        at=CURRENT_TIME,
        last_accepted_time_step=accepted.time_step,
    ) is None


@pytest.mark.parametrize("code", ["", "12345", "1234567", "12A456", "１２３４５６"])
def test_totp_rejects_invalid_codes(code: str) -> None:
    assert verify_totp(SYNTHETIC_SECRET, code, at=CURRENT_TIME) is None


def test_totp_rejects_naive_time_and_negative_replay_counter() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        verify_totp(SYNTHETIC_SECRET, code_at(), at=datetime(2026, 8, 14, 12, 0))
    with pytest.raises(ValueError, match="must not be negative"):
        verify_totp(
            SYNTHETIC_SECRET,
            code_at(),
            at=CURRENT_TIME,
            last_accepted_time_step=-1,
        )
