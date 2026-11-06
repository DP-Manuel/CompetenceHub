from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from icalendar import Calendar
import pytest

from competence_hub_api.portal.calendar import PublicCalendarOffer, public_calendar_month_window, validate_public_calendar_window
from competence_hub_api.portal.calendar_export import public_calendar_ics


def offer(start="2026-11-28T17:18+01:00", end="2026-11-29T17:18+01:00"):
    published = datetime(2026, 11, 6, 10, tzinfo=timezone.utc)
    return PublicCalendarOffer(id=uuid4(), coach_display_name="Demo-Coach", coach_profile_path=None,
        topic_id=uuid4(), topic_name="Demo-Thema", title="Öffentlicher Workshop",
        summary="Nur freigegebene Beschreibung", starts_at=datetime.fromisoformat(start),
        ends_at=datetime.fromisoformat(end), time_zone="Europe/Berlin", format_code="hybrid",
        public_location="Demo-Raum", capacity=12, decision_deadline=published,
        price_display_text="Preis nach Abstimmung", updated_at=published,
        publication_sequence=1, published_at=published)


@pytest.mark.parametrize("start,end", [
    ("2026-11-28T17:18+01:00", "2026-11-29T17:18+01:00"),
    ("2026-03-28T17:18+01:00", "2026-03-29T17:18+02:00"),
    ("2026-10-24T17:18+02:00", "2026-10-25T17:18+01:00"),
    ("2026-12-31T20:00+01:00", "2027-01-01T00:00+01:00"),
])
def test_icalendar_roundtrip_preserves_instants_timezone_and_exclusive_end(start, end):
    original = offer(start, end)
    payload = public_calendar_ics(original)
    calendar = Calendar.from_ical(payload)
    event = calendar.walk("VEVENT")[0]
    assert calendar.errors == [] and event.errors == []
    assert len(calendar.walk("VEVENT")) == 1
    assert len(calendar.walk("VTIMEZONE")) == 1
    assert event.decoded("dtstart") == original.starts_at
    assert event.decoded("dtend") == original.ends_at
    assert event["DTSTART"].params["TZID"] == "Europe/Berlin"
    assert event.decoded("dtstamp") == original.published_at
    assert not {"METHOD", "ORGANIZER", "ATTENDEE"}.intersection(calendar.keys() | event.keys())
    assert calendar.walk("VALARM") == []
    assert payload.endswith(b"\r\n")
    assert all(len(line) <= 75 for line in payload.split(b"\r\n"))


def test_stable_uid_sequence_and_no_internal_update_side_effect():
    first = offer()
    original = public_calendar_ics(first)
    assert public_calendar_ics(first) == original
    changed_private_timestamp = replace(first, updated_at=datetime(2026, 11, 7, tzinfo=timezone.utc))
    assert public_calendar_ics(changed_private_timestamp) == original
    published = replace(first, publication_sequence=2, title="Geprüfte Revision 2",
                        published_at=datetime(2026, 11, 8, tzinfo=timezone.utc))
    old = Calendar.from_ical(original).walk("VEVENT")[0]
    new = Calendar.from_ical(public_calendar_ics(published)).walk("VEVENT")[0]
    assert old["UID"] == new["UID"]
    assert old["SEQUENCE"] == 1 and new["SEQUENCE"] == 2
    assert new.decoded("LAST-MODIFIED") > old.decoded("LAST-MODIFIED")
    assert new["SUMMARY"] == published.title


def test_repeated_autumn_hour_uses_utc_to_preserve_distinct_instants():
    original=offer("2026-10-25T02:30+02:00","2026-10-25T02:30+01:00")
    event=Calendar.from_ical(public_calendar_ics(original)).walk("VEVENT")[0]
    assert "TZID" not in event["DTSTART"].params
    assert event.decoded("DTSTART")==datetime(2026,10,25,0,30,tzinfo=timezone.utc)
    assert event.decoded("DTEND")==datetime(2026,10,25,1,30,tzinfo=timezone.utc)


def test_ics_text_escaping_cannot_inject_components_or_reviewer_fields():
    original = replace(offer(), title="Ä" * 160 + ";,\\\r\nBEGIN:VEVENT\r\nATTENDEE:attacker",
                       summary="Ö" * 1200 + "\r\nX-PRIVATE: pretend")
    data = public_calendar_ics(original)
    calendar = Calendar.from_ical(data)
    event = calendar.walk("VEVENT")[0]
    assert len(calendar.walk("VEVENT")) == 1
    assert str(event["SUMMARY"]) == original.title.replace("\r\n", "\n")
    assert "ATTENDEE" not in event and "X-PRIVATE" not in event
    assert all(len(line) <= 75 for line in data.split(b"\r\n"))


def test_month_window_uses_berlin_midnight_and_keeps_three_month_planning_limit():
    now = datetime(2026, 11, 6, 10, tzinfo=timezone.utc)
    start, end = public_calendar_month_window(month="2026-12", now=now)
    assert start.isoformat() == "2026-11-30T23:00:00+00:00"
    assert end.isoformat() == "2026-12-31T23:00:00+00:00"
    first, last = public_calendar_month_window(month="2027-02", now=now)
    assert last == datetime(2027, 2, 6, 10, tzinfo=timezone.utc)
    validate_public_calendar_window(from_at=first, to_at=last, now=now)
    with pytest.raises(ValueError):
        public_calendar_month_window(month="2027-03", now=now)
    with pytest.raises(ValueError):
        validate_public_calendar_window(from_at=datetime(2026, 10, 31, tzinfo=timezone.utc), to_at=end, now=now)
