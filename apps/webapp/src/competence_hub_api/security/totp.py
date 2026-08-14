from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import time

import pyotp

TOTP_DIGITS = 6
TOTP_INTERVAL_SECONDS = 30
TOTP_SECRET_CHARACTERS = 32
TOTP_WINDOW_STEPS = 1


@dataclass(frozen=True)
class TotpMatch:
    time_step: int


def generate_totp_secret() -> str:
    return pyotp.random_base32(length=TOTP_SECRET_CHARACTERS)


def provisioning_uri(
    secret: str,
    *,
    account_name: str,
    issuer_name: str = "Competence Hub",
) -> str:
    if not account_name.strip() or not issuer_name.strip():
        raise ValueError("account name and issuer must not be empty")
    return _totp(secret).provisioning_uri(
        name=account_name.strip(),
        issuer_name=issuer_name.strip(),
    )


def verify_totp(
    secret: str,
    code: str,
    *,
    at: datetime | int | float | None = None,
    last_accepted_time_step: int | None = None,
) -> TotpMatch | None:
    normalized_code = code.strip()
    if (
        len(normalized_code) != TOTP_DIGITS
        or not normalized_code.isascii()
        or not normalized_code.isdigit()
    ):
        return None
    if last_accepted_time_step is not None and last_accepted_time_step < 0:
        raise ValueError("last accepted TOTP time step must not be negative")

    timestamp = _timestamp(at)
    current_step = int(timestamp // TOTP_INTERVAL_SECONDS)
    totp = _totp(secret)
    matched_steps: list[int] = []
    for offset in range(-TOTP_WINDOW_STEPS, TOTP_WINDOW_STEPS + 1):
        candidate_step = current_step + offset
        expected = totp.at(candidate_step * TOTP_INTERVAL_SECONDS)
        if hmac.compare_digest(expected, normalized_code):
            matched_steps.append(candidate_step)

    if not matched_steps:
        return None
    matched_step = max(matched_steps)
    if last_accepted_time_step is not None and matched_step <= last_accepted_time_step:
        return None
    return TotpMatch(time_step=matched_step)


def _totp(secret: str) -> pyotp.TOTP:
    normalized_secret = secret.strip().replace(" ", "").upper()
    if not normalized_secret:
        raise ValueError("TOTP secret must not be empty")
    return pyotp.TOTP(
        normalized_secret,
        digits=TOTP_DIGITS,
        interval=TOTP_INTERVAL_SECONDS,
        digest=hashlib.sha1,
    )


def _timestamp(value: datetime | int | float | None) -> float:
    if value is None:
        return time.time()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError("TOTP verification time must be timezone-aware")
        return value.astimezone(timezone.utc).timestamp()
    return float(value)
