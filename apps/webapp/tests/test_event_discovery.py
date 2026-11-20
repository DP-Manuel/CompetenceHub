from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from competence_hub_api.portal.calendar import PublicCalendarOffer, UpcomingEvent
from competence_hub_api.portal.event_discovery import Locality, distance_km, project_event, region_labels, seat_status


NOW = datetime(2026, 11, 20, 12, tzinfo=timezone.utc)


@pytest.mark.parametrize(("count", "expected"), [
    (None, "unknown"), (-1, "unknown"), (11, "unknown"),
    (0, "none"), (1, "limited"), (4, "limited"), (5, "many"), (10, "many"),
])
def test_seat_status_uses_real_counts_and_a_strict_half_threshold(count, expected):
    assert seat_status(remaining=count, capacity=10, deadline=NOW + timedelta(hours=1), now=NOW) == expected
    assert seat_status(remaining=count, capacity=10, deadline=NOW, now=NOW) == "closed"


def test_locality_match_requires_curated_key_city_or_postal_alias():
    a = Locality("a", "Synthetic A", 0, 179.9, ("00000",))
    b = Locality("b", "Synthetic B", 0, -179.9)
    assert 22 < distance_km(a, b) < 23
    assert region_labels(" 00000 ", 25, (a, b)) == (a.label, b.label)
    assert region_labels("synthetic A", 10, (a, b)) == (a.label,)
    with pytest.raises(ValueError):
        region_labels("missing", 100, (a, b))
    with pytest.raises(ValueError):
        region_labels("00000", 100, (a, replace(b, aliases=("00000",))))
    with pytest.raises(ValueError):
        Locality("invalid", "Invalid", float("nan"), 3)


def test_public_reuse_projection_has_only_approved_public_facts():
    offer = PublicCalendarOffer(
        id=uuid4(), coach_display_name="Demo", coach_profile_path="/coaches/demo/",
        topic_id=uuid4(), topic_name="Demo", title="Demo", summary=None,
        starts_at=NOW + timedelta(days=5), ends_at=NOW + timedelta(days=6),
        time_zone="Europe/Berlin", format_code="online", public_location=None, capacity=10,
        decision_deadline=NOW - timedelta(minutes=1), price_display_text="Preis nach Abstimmung", updated_at=NOW,
    )
    value = project_event(UpcomingEvent(offer, 3), NOW)
    assert set(value) == {"id", "title", "summary", "coach", "topic", "starts_at", "ends_at",
                          "time_zone", "format", "public_location", "decision_deadline", "publication_status",
                          "availability", "price", "detail_path"}
    assert set(value["coach"]) == {"display_name", "profile_path"}
    assert value["availability"] == {"status": "closed", "remaining": None}
    assert value["price"] == {"status": "display_text", "text": "Preis nach Abstimmung"}
    assert value["detail_path"].endswith(f"?event={offer.id}")
    blank = project_event(UpcomingEvent(replace(offer, price_display_text=""), None), NOW)
    assert blank["price"] == {"status": "unspecified", "text": None}
