"""Public, non-booking iCalendar snapshot; never accepts protected offer DTOs."""
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

from competence_hub_api.portal.calendar import PublicCalendarOffer


def public_calendar_ics(offer: PublicCalendarOffer) -> bytes:
    calendar = Calendar()
    calendar.add("prodid", "-//Competence Hub//Public Event Snapshot//DE")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")
    event = Event()
    event.add("uid", f"calendar-offer-{offer.id}@competencehub.donner-partner.de")
    published = offer.published_at or offer.updated_at
    event.add("dtstamp", published.astimezone(timezone.utc))
    event.add("last-modified", published.astimezone(timezone.utc))
    event.add("sequence", offer.publication_sequence)
    zone = ZoneInfo(offer.time_zone)
    start, end = offer.starts_at.astimezone(zone), offer.ends_at.astimezone(zone)
    # RFC5545 local repeated hours denote their FIRST occurrence. UTC preserves
    # a second-occurrence instant that TZID alone cannot express.
    if any(value.fold and value.utcoffset() != value.replace(fold=0).utcoffset() for value in (start,end)):
        start, end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    event.add("dtstart", start)
    event.add("dtend", end)
    event.add("summary", offer.title)
    event.add("description", "\n".join(filter(None, [offer.summary,
        f"Coach: {offer.coach_display_name}", f"Thema: {offer.topic_name}",
        f"Zeitzone: {offer.time_zone}", offer.price_display_text,
        "Öffentliche Terminangabe. Keine Buchungs- oder Teilnahmebestätigung."])))
    if offer.public_location:
        event.add("location", offer.public_location)
    event.add("transp", "TRANSPARENT")
    calendar.add_component(event)
    calendar.add_missing_timezones(first_date=(offer.starts_at - timedelta(days=366)).date(),
                                   last_date=(offer.ends_at + timedelta(days=366)).date())
    return calendar.to_ical()
