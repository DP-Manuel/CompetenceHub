"""Reusable published-event facts, without customer or reviewer data."""
from dataclasses import dataclass
from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from urllib.parse import urlencode

from competence_hub_api.portal.calendar import UpcomingEvent


@dataclass(frozen=True)
class Locality:
    key: str
    label: str
    latitude: float
    longitude: float
    aliases: tuple[str, ...] = ()

    def __post_init__(self):
        if not (-90 <= self.latitude <= 90 and -180 <= self.longitude <= 180):
            raise ValueError("Invalid locality coordinates")


def distance_km(origin: Locality, destination: Locality) -> float:
    a, b = radians(origin.latitude), radians(destination.latitude)
    d = radians(destination.longitude - origin.longitude)
    haversine = sin((b - a) / 2) ** 2 + cos(a) * cos(b) * sin(d / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(min(1.0, max(0.0, haversine))))


def region_labels(query: str, radius: int, localities: tuple[Locality, ...]) -> tuple[str, ...]:
    value = query.strip().casefold()
    matches = [point for point in localities
               if value in {part.casefold() for part in (point.key, point.label, *point.aliases)}]
    if len(matches) != 1 or not 1 <= radius <= 500:
        raise ValueError("Unknown locality or radius")
    return tuple(point.label for point in localities if distance_km(matches[0], point) <= radius)


def seat_status(*, remaining: int | None, capacity: int, deadline: datetime, now: datetime) -> str:
    if deadline <= now:
        return "closed"
    if remaining is None or not 0 <= remaining <= capacity or capacity < 1:
        return "unknown"
    if remaining == 0:
        return "none"
    return "limited" if 2 * remaining < capacity else "many"


def project_event(event: UpcomingEvent, now: datetime) -> dict:
    offer = event.offer
    status = seat_status(remaining=event.remaining_seats, capacity=offer.capacity,
                         deadline=offer.decision_deadline, now=now)
    return {
        "id": offer.id,
        "title": offer.title,
        "summary": offer.summary,
        "coach": {"display_name": offer.coach_display_name, "profile_path": offer.coach_profile_path},
        "topic": {"id": offer.topic_id, "name": offer.topic_name},
        "starts_at": offer.starts_at,
        "ends_at": offer.ends_at,
        "time_zone": offer.time_zone,
        "format": offer.format_code,
        "public_location": offer.public_location,
        "decision_deadline": offer.decision_deadline,
        "publication_status": "published",
        "availability": {"status": status, "remaining": event.remaining_seats
                         if status in {"many", "limited", "none"} else None},
        "price": {"status": "display_text", "text": offer.price_display_text}
        if offer.price_display_text else {"status": "unspecified", "text": None},
        "detail_path": "/portal/calendar-public.html?" + urlencode({"event": offer.id}),
    }
