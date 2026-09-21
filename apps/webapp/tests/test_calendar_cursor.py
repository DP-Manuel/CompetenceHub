from datetime import UTC, datetime
from uuid import UUID

import pytest

from competence_hub_api.security.calendar_cursor import CalendarCursorCodec


KEY = b"k" * 32
WHEN = datetime(2026, 10, 1, 8, 30, tzinfo=UTC)
OFFER_ID = UUID("00000000-0000-4000-8000-000000000701")


def test_calendar_cursor_round_trips_deterministically() -> None:
    codec = CalendarCursorCodec(KEY)

    token = codec.encode(WHEN, OFFER_ID)

    assert codec.encode(WHEN, OFFER_ID) == token
    assert codec.decode(token) == (WHEN, OFFER_ID)


def test_calendar_cursor_rejects_tampering_and_malformed_values() -> None:
    codec = CalendarCursorCodec(KEY)
    token = codec.encode(WHEN, OFFER_ID)

    payload, signature = token.split(".")
    tampered = f"{payload}.{'A' if signature[0] != 'A' else 'B'}{signature[1:]}"
    with pytest.raises(ValueError, match="calendar cursor"):
        codec.decode(tampered)
    with pytest.raises(ValueError, match="calendar cursor"):
        codec.decode("not-a-cursor")


def test_calendar_cursor_requires_domain_key() -> None:
    with pytest.raises(ValueError, match="256 bits"):
        CalendarCursorCodec(b"short")
