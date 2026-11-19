"""Run the integrated V2 platform or its acceptance against an owned throwaway database."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
import asyncio
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
import sys
import tempfile
from threading import Event
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx
from fastapi.testclient import TestClient
from playwright.sync_api import expect, sync_playwright
import pyotp
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

from cal1_pilot_acceptance import qa
from local_calendar_postgres import LocalCalendarPostgres
from local_platform_website import SYNTHETIC_PROFILE, attach_website, build_website
from native_calendar_fixture import NativeCalendarFixture
from vps_pilot_acceptance import zoom_profile
from competence_hub_api.runtime import create_database_engine, create_runtime_app

ROOT = Path(__file__).resolve().parents[1]
RES = "/api/v1/portal/reservations"
CAL = "/api/v1/portal/calendar/offers"
PUBLIC = "/api/v1/calendar/offers"
UI = "/portal/"
OVERVIEW = "/api/v1/portal/pilot/overview"


def check(label, condition):
    if not condition:
        raise AssertionError(label)
    print("PASS | " + label, flush=True)


def seed_companies(fixture):
    async def seed(connection):
        for key, letter in (("contact", "A"), ("contact_two", "B")):
            company = await connection.scalar(text("""
                INSERT INTO competence_hub.companies (name,status)
                VALUES (:name,'pilot') RETURNING id
            """), {"name": f"Demo-Firma {letter}"})
            await connection.execute(text("""
                INSERT INTO competence_hub.company_contacts (company_id,portal_user_id,first_name,last_name,email)
                VALUES (:company,:user,'Demo',:letter,:email)
            """), {"company": company, "user": fixture.users[key], "letter": letter, "email": fixture.emails[key]})
    fixture.database(seed)


def login(page, base, fixture, actor, recovery, *, target=UI):
    first = actor not in recovery
    if page.url != base + target:
        with page.expect_response(lambda response: response.url.endswith("/portal/access/session")):
            page.goto(base + target)
    expect(page.locator("#login-email")).to_be_focused()
    page.locator("#login-email").fill(fixture.emails[actor])
    page.locator("#login-password").fill(fixture.password)
    page.get_by_role("button", name="Anmelden", exact=True).click()
    if first:
        expect(page.locator("#enrollment-code")).to_be_visible()
        totp = pyotp.TOTP(page.locator("#provisioning-secret").inner_text())
        page.locator("#enrollment-code").fill(totp.at(fixture.now.timestamp()))
        page.get_by_role("button", name="Einrichtung abschließen").click()
        expect(page.locator("#recovery-view")).to_be_visible()
        recovery[actor] = page.locator("#recovery-codes li").all_text_contents()
        assert len(recovery[actor]) == 10
        page.locator("#recovery-confirmed").check()
        page.locator("#enter-portal").click()
    else:
        page.get_by_text("Recovery-Code", exact=True).click()
        page.locator("#mfa-code").fill(recovery[actor].pop())
        page.get_by_role("button", name="Bestätigen", exact=True).click()
    expect(page.locator("#portal-view")).to_be_visible()
    expect(page.locator("#portal-navigation button").first).to_be_attached()
    tour = page.locator("#product-tour")
    if first and fixture.roles[actor] in {"coach", "calendar_reviewer", "admin", "company_contact"}:
        expect(tour).to_be_visible()
        page.locator("#tour-skip").click()
    elif tour.is_visible():
        page.locator("#tour-skip").click()


def live_page(browser, base, fixture, actor, recovery, external, errors, *, mobile=False):
    context = browser.new_context(ignore_https_errors=True, reduced_motion="reduce",
                                  viewport={"width": 390 if mobile else 1440, "height": 920})
    page = context.new_page()
    guard_page(page, base, external, errors)
    login(page, base, fixture, actor, recovery)
    return page


def guard_page(page, base, external, errors):
    def route(handler):
        if handler.request.url.startswith(base + "/"):
            handler.continue_()
        else:
            external.append("external request")
            handler.abort()
    page.route("**/*", route)
    page.on("pageerror", lambda error: errors.append(error.name))


def website_to_company(browser, base, fixture, recovery, external, errors, offer_id):
    page = browser.new_page(ignore_https_errors=True, reduced_motion="reduce",
                            viewport={"width": 390, "height": 920})
    guard_page(page, base, external, errors)
    response = page.goto(base + "/website/")
    assert response.headers["x-robots-tag"] == "noindex, nofollow, noarchive"
    assert "'unsafe-inline'" not in response.headers["content-security-policy"]
    page.get_by_role("link", name="Demo-Angebot", exact=True).click()
    expect(page.get_by_role("heading", name="Demo-Gruppenangebot")).to_be_visible()
    page.get_by_role("link", name="Profil des V2 Demo-Coaches").click()
    expect(page.get_by_role("heading", name="V2 Demo-Coach", exact=True)).to_be_visible()
    page.get_by_role("link", name="Termine dieses Demo-Coaches").click()
    expect(page.locator("#profile-filter")).to_be_visible()
    offer = page.locator(f"[data-offer='{offer_id}']").first
    while not offer.count() and not page.locator("#next").is_disabled():
        expect(page.locator("#loading")).to_be_hidden()
        if offer.count():
            break
        page.locator("#next").click()
    offer.click()
    expect(page.locator("#coach")).to_have_attribute("href", "/website" + SYNTHETIC_PROFILE)
    page.get_by_role("button", name="Anfrageentwurf vorbereiten").click()
    expect(page.locator("#request-status")).to_contain_text("Nichts gesendet oder reserviert")
    assert page.request.get(base + RES + "/catalogue").status == 401
    link = page.get_by_role("link", name="Im Portal unverbindlich vormerken")
    expect(link).to_have_attribute("href", UI + "?offer=" + offer_id)
    with page.expect_response(lambda response: response.url.endswith("/portal/access/session")):
        link.click()
    expect(page.get_by_role("heading", name="Willkommen im Competence Hub")).to_be_visible()
    assert "'unsafe-inline'" not in page.request.get(base + UI).headers["content-security-policy"]
    login(page, base, fixture, "contact", recovery, target=UI + "?offer=" + offer_id)
    expect(page.get_by_role("heading", name="Ausgewählte Veranstaltung")).to_be_visible()
    expect(page.locator("#reservation-catalogue .calendar-card")).to_have_count(1)
    expect(page.get_by_role("button", name="Plätze vormerken: Demo-Workshop über zwei Tage")).to_be_visible()
    check("One origin: Astro offer, synthetic Coach, published CAL-1 event, anonymous draft and authenticated CAL-2 deep link", True)
    page.get_by_role("button", name="Alle Veranstaltungen").click()
    return page


class Session:
    def __init__(self, page, base):
        self.base = base
        self.cookies = {row["name"]: row["value"] for row in page.context.cookies()}
        self.refresh()

    def refresh(self):
        # An API-only actor gets a fresh CSRF token; its page must reload before writing.
        response = httpx.post(
            self.base + "/api/v1/portal/access/session/csrf", cookies=self.cookies,
            headers={"Origin": self.base}, verify=False, trust_env=False, timeout=15,
        )
        assert response.status_code == 204
        self.csrf = response.headers["X-CSRF-Token"]

    def send(self, method, path, data=None, *, version=None, origin=None, csrf=None):
        headers = {"Origin": origin or self.base, "X-CSRF-Token": self.csrf if csrf is None else csrf}
        if version is not None:
            headers["If-Match"] = f'"v{version}"'
        return httpx.request(method, self.base + path, json=data, cookies=self.cookies,
                             headers=headers, verify=False, trust_env=False, timeout=15)


def create_offer(coach, reviewer, fixture, title, day, capacity, threshold, *, multi=False):
    start = (fixture.now + timedelta(days=day)).replace(second=0, microsecond=0)
    draft = {
        "title": title, "topic_id": str(fixture.topic), "format": "online",
        "starts_at": start.isoformat(), "ends_at": (start + timedelta(hours=26 if multi else 2)).isoformat(),
        "time_zone": "Europe/Berlin", "capacity": capacity, "review_threshold": threshold,
        "decision_deadline": (start - timedelta(days=2)).isoformat(), "price_display_text": "Preis nach Abstimmung",
    }
    created = coach.send("POST", CAL, {"client_request_id": str(uuid4()), "draft": draft})
    assert created.status_code == 201
    path = CAL + "/" + created.json()["id"]
    submitted = coach.send("POST", path + "/submit", version=1)
    assert submitted.status_code == 200
    published = reviewer.send("POST", path + "/review-decisions", {"outcome": "published"}, version=2)
    assert published.status_code == 200
    return created.json()["id"], draft


def request_data(seats, **extras):
    return {"request_id": str(uuid4()), "revision_number": 1, "contact_confirmed": True, "seats": seats, **extras}


def assert_layout(page):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    assert page.locator("#reservations-workspace").evaluate("""root => {
      const viewport = innerWidth;
      return [...root.querySelectorAll('button, input, select, textarea')].every(node => {
        if (!node.getClientRects().length) return true;
        const box = node.getBoundingClientRect();
        const range = document.createRange();
        range.selectNodeContents(node);
        return box.left >= 0 && box.right <= viewport + 1 &&
          [...range.getClientRects()].every(r => r.left >= box.left - 1 && r.right <= box.right + 1);
      });
    }""")


def keyboard_activate(page, control):
    control.scroll_into_view_if_needed()
    assert control.evaluate("""node => {
      const bounds = node.getBoundingClientRect();
      const hit = document.elementFromPoint(bounds.left + bounds.width / 2, bounds.top + bounds.height / 2);
      return hit === node || node.contains(hit);
    }"""), "Control center is covered"
    control.focus()
    page.keyboard.press("Space" if control.get_attribute("type") == "checkbox" else "Enter")


def browser_workflow(company, other_company, reviewer, zoom, base):
    workshop = "Demo-Workshop über zwei Tage"
    catalogue_button = company.get_by_role("button", name=f"Plätze vormerken: {workshop}")
    company.locator("#pilot-help summary").click()
    company.get_by_role("button", name="Unternehmens-Einführung starten").click()
    tour = company.locator("#product-tour")
    for step in range(1, 7):
        expect(tour.get_by_text(f"Schritt {step} von 6", exact=True)).to_be_visible()
        assert tour.evaluate("el => el.getBoundingClientRect().right <= innerWidth + 1")
        expect(tour.locator("#tour-title")).to_be_focused()
        tour.get_by_role("button", name="Abschließen" if step == 6 else "Weiter", exact=True).press("Enter")
    expect(tour).to_be_hidden()
    expect(company.locator("#pilot-help summary")).to_be_focused()
    check("Six-step company tour on mobile, optional, restartable and keyboard-usable", True)
    company.get_by_label("Titel oder Thema").fill("nicht vorhandener Titel")
    company.get_by_role("button", name="Suchen", exact=True).click()
    expect(company.get_by_text("Keine passenden Angebote für Vormerkungen gefunden.")).to_be_visible()
    company.get_by_label("Titel oder Thema").fill("über zwei Tage")
    company.get_by_role("button", name="Suchen", exact=True).click()
    company.locator("#reservation-catalogue summary").click()
    expect(company.get_by_text("Preis nach Abstimmung")).to_be_visible()
    expect(catalogue_button).to_be_visible()
    catalogue_button.focus()
    company.keyboard.press("Enter")
    expect(company.get_by_role("button", name="Zur Übersicht")).to_be_focused()
    company.keyboard.press("Tab")
    field = company.get_by_role("spinbutton", name="Teilnehmerzahl")
    expect(field).to_be_focused()
    field.fill("3")
    company.once("dialog", lambda dialog: dialog.dismiss())
    company.get_by_role("button", name="Abbrechen", exact=True).click()
    expect(field).to_have_value("3")
    company.once("dialog", lambda dialog: dialog.accept())
    company.get_by_role("button", name="Abbrechen", exact=True).click()
    catalogue_button.click()
    expect(field).to_have_value("1")
    check("Catalogue search, empty state, details and guarded cancel preserve/discard correctly", True)
    # B opens the form when it still shows space for four. A's write makes that view stale.
    other_company.get_by_role("button", name=f"Plätze vormerken: {workshop}").click()
    other_company.get_by_label("Teilnehmerzahl").fill("4")
    other_company.get_by_label("Kontaktperson bestätigen: Demo B").check()
    field.fill("6")
    company.get_by_role("button", name="Unverbindlich vormerken").click()
    expect(field).to_have_attribute("aria-invalid", "true")
    expect(field).to_be_focused()
    assert_layout(company)
    field.fill("2")
    company.get_by_role("button", name="Unverbindlich vormerken").click()
    expect(company.get_by_role("checkbox", name="Kontaktperson bestätigen: Demo A")).to_be_focused()
    company.keyboard.press("Space")
    company.get_by_role("textbox", name="Nachricht (optional)").fill("Synthetische Notiz")
    company.get_by_role("button", name="Unverbindlich vormerken").click()
    expect(company.get_by_text("Vormerkung eingereicht. Es wurde nichts verbindlich gebucht.")).to_be_visible()
    expect(company.get_by_text("Eingereicht", exact=True)).to_be_visible()
    other_company.get_by_role("button", name="Unverbindlich vormerken").click()
    expect(other_company.get_by_text("Es sind nicht genügend Plätze frei.", exact=False)).to_be_visible()
    expect(other_company.get_by_label("Teilnehmerzahl")).to_be_focused()
    other_company.get_by_label("Teilnehmerzahl").fill("2")
    other_company.get_by_role("button", name="Unverbindlich vormerken").click()
    expect(other_company.get_by_text("Eingereicht", exact=True)).to_be_visible()
    check("390 px and real two-company booking flow: stale four-seat request is blocked at the field", True)

    reviewer.locator("#portal-navigation").get_by_role("button", name="Vormerkungen prüfen", exact=True).click()
    reviewer.get_by_label("Veranstaltung", exact=True).fill("über zwei Tage")
    reviewer.get_by_label("Coach", exact=True).fill("Coach A")
    reviewer.get_by_role("button", name="Filtern", exact=True).click()
    company_a_card = reviewer.locator("#reservations-workspace .calendar-card").filter(
        has=reviewer.get_by_text("Demo-Firma A", exact=True))
    expect(company_a_card.get_by_text("Prüfschwelle erreicht", exact=True)).to_be_visible()
    company_a_card.get_by_role("button", name="Vorgang ansehen").click()
    reviewer.get_by_label("Entscheidung", exact=True).select_option("clarification_requested")
    reviewer.get_by_role("button", name="Entscheidung speichern").click()
    expect(reviewer.get_by_label("Begründung für die Firma")).to_be_focused()
    reviewer.get_by_label("Begründung für die Firma").fill("Bitte bestätigen Sie drei Plätze.")
    reviewer.get_by_role("button", name="Entscheidung speichern").click()
    expect(reviewer.get_by_text("Klärung nötig", exact=True)).to_be_visible()

    company.reload()
    expect(company.get_by_text("Klärung nötig", exact=True)).to_be_visible()
    company.locator(".reservation-activity summary").click()
    company.get_by_role("button", name=f"Ihre Antwort ist offen: {workshop}").click()
    expect(company.get_by_text("Bitte bestätigen Sie drei Plätze.")).to_be_visible()
    company.get_by_label("Antwort auf die Rückfrage").fill("Drei Plätze sind möglich.")
    with company.expect_response(lambda response: response.url.endswith("/reply")) as sent_reply:
        company.get_by_role("button", name="Antwort senden").click()
    reply_request = sent_reply.value.request
    reply_retry = (reply_request.url.removeprefix(base), reply_request.post_data_json, reply_request.headers["if-match"])
    expect(company.get_by_text("Antwort im Vorgang gespeichert.")).to_be_visible()
    company.get_by_role("button", name="Vorgang ansehen").click()
    company.get_by_label("Teilnehmerzahl").fill("3")
    company.get_by_role("button", name="Platzzahl ändern").click()
    expect(company.get_by_text("Platzzahl geändert.", exact=True)).to_be_visible()

    # The isolated 200% browser intentionally takes over the reviewer's current session.
    zoom.add_cookies(reviewer.context.cookies())
    page = zoom.pages[0]
    page.goto(base + UI)
    review_tab = page.locator("#portal-navigation").get_by_role("button", name="Vormerkungen prüfen", exact=True)
    expect(review_tab).to_be_visible()
    keyboard_activate(page, review_tab)
    company_a_card = page.locator("#reservations-workspace .calendar-card").filter(
        has=page.get_by_text("Demo-Firma A", exact=True))
    page.get_by_label("Status", exact=True).select_option("decision")
    keyboard_activate(page, page.get_by_role("button", name="Filtern", exact=True))
    expect(company_a_card.get_by_text("Prüfschwelle erreicht", exact=True)).to_be_visible()
    assert 1.9 <= page.evaluate("devicePixelRatio") <= 2.1
    detail = company_a_card.get_by_role("button", name="Vorgang ansehen")
    keyboard_activate(page, detail)
    expect(page.get_by_text("Drei Plätze sind möglich.")).to_be_visible()
    assert_layout(page)
    page.get_by_label("Entscheidung", exact=True).select_option("approved")
    page.get_by_label("Begründung für die Firma").fill("Fachlich geprüft, keine verbindliche Buchung.")
    keyboard_activate(page, page.get_by_role("button", name="Entscheidung speichern"))
    expect(page.get_by_text("Entscheidung gespeichert.", exact=True)).to_be_visible()
    page.get_by_label("Status", exact=True).select_option("approved")
    keyboard_activate(page, page.get_by_role("button", name="Filtern", exact=True))
    expect(company_a_card.get_by_text("Positiv geprüft", exact=True)).to_be_visible()
    company.reload()
    expect(company.get_by_text("Positiv geprüft", exact=True)).to_be_visible()
    other_company.get_by_role("button", name="Vorgang ansehen").click()
    other_company.get_by_role("button", name="Vormerkung zurücknehmen").click()
    other_company.get_by_role("button", name="Rücknahme bestätigen").click()
    expect(other_company.locator("#reservation-own").get_by_text("Zurückgenommen", exact=True)).to_be_visible()
    check("Reviewer filters, company reply, approval at native 200% zoom and withdrawal of B", True)
    return page, reply_retry


def api_workflow(fixture, base, actors, main_id, main_draft, offers, reply_retry):
    a, b, reviewer, coach, internal, admin = (Session(actors[key], base) for key in
        ("contact", "contact_two", "reviewer", "coach", "internal", "admin"))
    request_main = a.send("GET", RES).json()["items"][0]
    id_main = request_main["id"]
    scopes = {}
    for key, session, expected in (
        ("company", a, {"company"}), ("other_company", b, {"company"}),
        ("coach", coach, {"coach"}), ("review", reviewer, {"review"}),
        ("admin", admin, {"admin", "review"}),
    ):
        result = session.send("GET", OVERVIEW)
        assert result.status_code == 200, f"{key} business overview HTTP {result.status_code}"
        scopes[key] = result.json()["business"]
        assert set(scopes[key]) == expected
    check("Role dashboards share the live process without crossing company, coach or administrator scopes", (
        scopes["company"]["company"]["counts"]["approved"] == 1
        and scopes["other_company"]["company"]["counts"]["approved"] == 0
        and scopes["review"]["review"]["counts"]["approved"] == 1
        and scopes["coach"]["coach"]["counts"]["published"] == 6
        and internal.send("GET", OVERVIEW).status_code == 403
        and a.send("GET", OVERVIEW, origin="https://outside.example.invalid").status_code == 403
        and all(set(event) == {"occurred_at", "category", "status"} for event in scopes["admin"]["admin"]["audit"])
    ))
    check("Reviewer and admin may review; coach/internal/company cannot", (
        reviewer.send("GET", RES + "?review=true").status_code == 200
        and admin.send("GET", RES + "?review=true").status_code == 200
        and all(actor.send("GET", RES + "?review=true").status_code == 403 for actor in (a, b, coach, internal))
    ))
    check("Company isolation, no-store and anonymous protection", (
        b.send("GET", RES + "/" + id_main).status_code == 404
        and b.send("POST", RES + "/" + id_main + "/withdraw", {"request_id": str(uuid4())}, version=3).status_code == 404
        and a.send("GET", RES).headers["cache-control"] == "no-store"
        and httpx.get(base + RES, verify=False, trust_env=False).status_code == 401
    ))
    check("CAL-1 public/ICS unchanged by reservation; no private projection", (
        a.send("GET", PUBLIC + "/" + main_id + "/calendar.ics").status_code == 200
        and not {"message", "phone", "company_name", "occupied_seats", "review_threshold"}
        .intersection(a.send("GET", PUBLIC + "/" + main_id).json())
        and a.send("POST", PUBLIC + "/" + main_id, request_data(1)).status_code == 405
    ))
    offer_last, offer_repeat, offer_deadline, revision_race = offers
    path = RES + "/offers/" + offer_last
    check("Origin, CSRF, strict seat type and contact confirmation", (
        a.send("POST", path, request_data(1), origin="https://invalid.example.invalid").status_code == 403
        and a.send("POST", path, request_data(1), csrf="invalid").status_code == 403
        and a.send("POST", path, request_data(True)).status_code == 400
        and a.send("POST", path, request_data(1, contact_confirmed=False)).status_code == 400
        and a.send("POST", path, request_data(2)).json()["code"] == "reservation_capacity"
    ))
    with ThreadPoolExecutor(max_workers=2) as pool:
        replies = list(pool.map(lambda actor: actor.send("POST", path, request_data(1)), (a, b)))
        check("Two native concurrent requests: the last seat can be allocated only once",
              sorted(reply.status_code for reply in replies) == [201, 409])
        repeat_path = RES + "/offers/" + offer_repeat
        duplicate = request_data(2)
        repeats = list(pool.map(lambda _: a.send("POST", repeat_path, duplicate), range(2)))
        check("Parallel identical retries produce one reservation",
              all(reply.status_code == 201 for reply in repeats) and repeats[0].json() == repeats[1].json())
    id_repeat = repeats[0].json()["id"]
    detail = RES + "/" + id_repeat
    check("Changed retry rejected; stale update and unauthorized decision blocked", (
        a.send("POST", repeat_path, {**duplicate, "seats": 1}).json()["code"] == "reservation_idempotency_conflict"
        and a.send("PATCH", detail + "/seats", {"request_id": str(uuid4()), "seats": 1}, version=2).json()["code"] == "reservation_stale_version"
        and a.send("POST", detail + "/decide", {"request_id": str(uuid4()), "outcome": "approved", "reason": "Demo"},
                   version=1).status_code == 403
    ))
    withdrawn = a.send("POST", detail + "/withdraw", {"request_id": str(uuid4())}, version=1)
    assert withdrawn.status_code == 200
    other = b.send("POST", repeat_path, request_data(2))
    assert other.status_code == 201
    rejected = reviewer.send("POST", RES + "/" + other.json()["id"] + "/decide",
        {"request_id": str(uuid4()), "outcome": "rejected", "reason": "Synthetisch abgelehnt."}, version=1)
    check("Withdrawal and rejection release capacity",
          rejected.status_code == 200 and a.send("POST", repeat_path, request_data(2)).status_code == 201)
    check("Positive decision cannot be withdrawn by the company",
          a.send("POST", RES + "/" + id_main + "/withdraw", {"request_id": str(uuid4())},
                 version=request_main["version"]).json()["code"] == "reservation_invalid_transition")
    current = a.send("GET", detail).json()
    reply = {"request_id": str(uuid4()), "reason": "Interne synthetische Antwort"}
    check("Replies require a specific open question and exact company scope", (
        a.send("POST", detail + "/reply", reply, version=current["version"]).status_code == 409
        and b.send("POST", RES + "/" + id_main + "/reply", reply, version=request_main["version"]).status_code == 404
    ))
    retry_path, retry_body, retry_version = reply_retry
    retry = a.send("POST", retry_path, retry_body, version=int(retry_version.strip('"v')))
    a_events, b_events = (actor.send("GET", RES + "/activity").json()["events"] for actor in (a, b))
    check("Activity contains one scoped reply event and no message, contact or actor payloads", (
        retry.status_code == 200 and retry.json()["id"] == id_main
        and sum(e["reservation_id"] == id_main and e["kind"] == "clarification_answered" for e in a_events) == 1
        and all(e["reservation_id"] != id_main for e in b_events)
        and all(set(e) == {"reservation_id", "offer_id", "title", "kind", "version", "occurred_at", "seats_after"} for e in a_events)
        and b.send("GET", RES + "/activity?review=true").status_code == 403
        and coach.send("GET", RES + "/activity?review=true").status_code == 403
    ))

    deadline_path = RES + "/offers/" + offer_deadline
    in_time = a.send("POST", deadline_path, request_data(2))
    assert in_time.status_code == 201
    deadline_detail = RES + "/" + in_time.json()["id"]
    async def set_deadline(connection, hours):
        await connection.execute(text("""
            UPDATE competence_hub.calendar_offer_revisions
            SET decision_deadline = clock_timestamp() + make_interval(hours => :hours)
            WHERE offer_id = CAST(:id AS uuid)
        """), {"id": offer_deadline, "hours": hours})
    fixture.database(lambda connection: set_deadline(connection, 12))
    check("Upcoming decision deadline is scoped to active requests", (
        [item["offer_id"] for item in reviewer.send("GET", RES + "?review=true&deadline=soon").json()["items"]]
        == [offer_deadline] and
        any(t["kind"] == "deadline_soon" and t["offer_id"] == offer_deadline
            for t in reviewer.send("GET", RES + "/activity?review=true").json()["tasks"])
    ))
    fixture.database(lambda connection: set_deadline(connection, -1))
    check("Reviewer overdue task is unique and its date and offer filters work across the catalogue", (
        len([t for t in reviewer.send("GET", RES + "/activity?review=true").json()["tasks"]
             if t["offer_id"] == offer_deadline and t["kind"] == "overdue"]) == 1
        and [item["offer_id"] for item in reviewer.send("GET", RES +
             "?review=true&status=open&deadline=overdue&offer=Frist").json()["items"]] == [offer_deadline]
        and any(row["id"] == main_id for row in a.send("GET", RES + "/catalogue?day=" +
            (datetime.fromisoformat(main_draft["ends_at"]) - timedelta(microseconds=1))
            .astimezone(ZoneInfo("Europe/Berlin")).date().isoformat()).json()["items"])
    ))
    check("Passed deadline: new/increased seats fail, existing items stay visible and may decrease/withdraw", (
        b.send("POST", deadline_path, request_data(1)).json()["code"] == "reservation_deadline"
        and a.send("PATCH", deadline_detail + "/seats",
                   {"request_id": str(uuid4()), "seats": 3}, version=1).json()["code"] == "reservation_deadline"
        and reviewer.send("GET", deadline_detail + "?review=true").json()["deadline_passed"]
        and a.send("PATCH", deadline_detail + "/seats",
                   {"request_id": str(uuid4()), "seats": 1}, version=1).status_code == 200
        and a.send("POST", deadline_detail + "/withdraw", {"request_id": str(uuid4())}, version=2).status_code == 200
    ))
    async def make_past(connection):
        await connection.execute(text("""
            UPDATE competence_hub.calendar_offer_revisions
            SET starts_at = clock_timestamp() - interval '2 days',
                ends_at = clock_timestamp() - interval '1 day',
                decision_deadline = clock_timestamp() - interval '3 days'
            WHERE offer_id = CAST(:id AS uuid)
        """), {"id": offer_deadline})
    fixture.database(make_past)
    check("Past status filter retains withdrawn history without automatic deletion",
          [item["status"] for item in reviewer.send("GET", RES + "?review=true&status=past").json()["items"]]
          == ["withdrawn"])
    cal_path = CAL + "/" + main_id
    shifted = {name: (datetime.fromisoformat(main_draft[name]) + timedelta(days=1)).isoformat()
               for name in ("starts_at", "ends_at", "decision_deadline")}
    revised = coach.send("PATCH", cal_path + "/draft", {
        **main_draft, **shifted, "capacity": 2, "review_threshold": 2,
        "format": "hybrid", "public_location": "Synthetischer neuer Ort",
    }, version=3)
    assert revised.status_code == 200
    submitted = coach.send("POST", cal_path + "/submit", version=4)
    assert submitted.status_code == 200
    blocked = reviewer.send("POST", cal_path + "/review-decisions", {"outcome": "published"}, version=5)
    review_details = reviewer.send("GET", RES + "/" + id_main + "?review=true").json()
    company_details = a.send("GET", RES + "/" + id_main).json()
    check("Proposed changes are actionable, protected and never silently replace current terms", (
        blocked.status_code == 409 and blocked.json()["code"] == "calendar_reservations_open"
        and review_details["proposed_revision"] == 2
        and {"starts_at", "ends_at", "decision_deadline", "capacity", "format_code", "public_location"}
        <= set(review_details["changed_fields"])
        and company_details["proposed_revision"] is None and company_details["changed_fields"] is None
        and a.send("GET", PUBLIC + "/" + main_id).json()["capacity"] == 5
        and len([t for t in reviewer.send("GET", RES + "/activity?review=true").json()["tasks"]
                 if t["offer_id"] == main_id and t["kind"] == "revision_pending"]) == 1
    ))

    race_id, race_draft = revision_race
    race_path = CAL + "/" + race_id
    assert coach.send("PATCH", race_path + "/draft", {**race_draft, "capacity": 3}, version=3).status_code == 200
    assert coach.send("POST", race_path + "/submit", version=4).status_code == 200
    with ThreadPoolExecutor(max_workers=2) as pool:
        publish = pool.submit(reviewer.send, "POST", race_path + "/review-decisions",
                              {"outcome": "published"}, version=5)
        reserve = pool.submit(b.send, "POST", RES + "/offers/" + race_id, request_data(1))
        statuses = publish.result().status_code, reserve.result().status_code
    check("Concurrent new publication versus a reservation on the old revision has one winner",
          statuses in ((200, 409), (409, 201)) and
          b.send("GET", PUBLIC + "/" + race_id).json()["capacity"] == (3 if statuses[0] == 200 else 2))
    check("Offer cancellation releases seats atomically and adds a customer-visible event", (
        coach.send("POST", cal_path + "/withdraw", version=5).status_code == 200
        and a.send("GET", PUBLIC + "/" + main_id).status_code == 404
        and (cancelled := a.send("GET", RES + "/" + id_main).json())["status"] == "cancelled"
        and cancelled["history"][0]["event"] == "offer_cancelled"
        and cancelled["history"][0]["occupied_delta"] == -3
    ))
    return id_main


def verify_pilot_runtime(db, fixture):
    # The clone lives only in the owned test container. Keep the two database
    # names distinct even when testing the private mode on this workstation.
    db.sql("CREATE DATABASE competence_hub_v2_pilot TEMPLATE competence_hub_staging;", "postgres")
    db.sql("""
        REVOKE CONNECT ON DATABASE competence_hub_v2_pilot FROM PUBLIC;
        GRANT CONNECT ON DATABASE competence_hub_v2_pilot TO competence_hub_app;
    """, "postgres")
    private_url = make_url(fixture.app_url).set(port=5432, database="competence_hub_v2_pilot")
    settings = replace(fixture._runtime_settings, database_url=private_url.render_as_string(hide_password=False),
                       allowed_origin="https://localhost:8447", cal2_mode="synthetic-pilot")

    def fixture_engine(_):
        return create_database_engine(private_url.set(port=55433).render_as_string(hide_password=False))

    with TestClient(create_runtime_app(settings, engine_factory=fixture_engine)) as client:
        assert client.get("/api/v1/calendar/journey").json() == {
            "portal_reservations": True, "local_website": False,
        }
        assert client.get(RES).status_code == 401
        assert client.get("/website/").status_code == 404

    db.sql("""
        SET ROLE competence_hub_owner;
        INSERT INTO competence_hub.portal_users (id,display_name,email,active)
            VALUES (gen_random_uuid(),'Synthetic guard probe','synthetic@example.test',false);
    """, "competence_hub_v2_pilot")
    try:
        with TestClient(create_runtime_app(settings, engine_factory=fixture_engine)):
            raise AssertionError("Pilot startup admitted a non-demo account")
    except RuntimeError as error:
        assert str(error) == "CAL-2 pilot database, schema or synthetic cohort did not pass"
    check("Protected-mode clone starts only with migrated schema and a synthetic cohort", True)


def interrupt_request(db, fixture, session, offer_id):
    locked, release = Event(), Event()
    backend = {}
    data = request_data(1)
    path = RES + "/offers/" + offer_id

    async def hold(connection):
        await connection.execute(text("""
            SELECT id FROM competence_hub.calendar_offers WHERE id = CAST(:id AS uuid) FOR UPDATE
        """), {"id": offer_id})
        backend["pid"] = await connection.scalar(text("SELECT pg_backend_pid()"))
        locked.set()
        await asyncio.to_thread(release.wait, 35)
        await connection.execute(text("SELECT 1"))

    async def wait_for_request(connection):
        for _ in range(80):
            if await connection.scalar(text("""
                SELECT EXISTS(
                    SELECT 1 FROM pg_locks
                    WHERE NOT granted AND :pid = ANY(pg_blocking_pids(pid))
                )
            """), backend):
                return True
            await asyncio.sleep(.05)
        return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        guard = pool.submit(fixture.database, hold)
        try:
            assert locked.wait(10)
            request = pool.submit(session.send, "POST", path, data)
            assert fixture.database(wait_for_request), "No blocked reservation before restart"
            db.restart()
            try:
                assert request.result().status_code == 503
            except httpx.TransportError:
                pass
        finally:
            release.set()
            with suppress(SQLAlchemyError):
                guard.result()
    return path, data


def demo(db, application, start, pw):
    restarted = False
    while True:
        with qa.synthetic_server(application) as base:
            browser = pw.firefox.launch(headless=False)
            try:
                for actor, title in (
                    ("coach", "CAL-2 Demo | Coach A"), ("reviewer", "CAL-2 Demo | Reviewer"),
                    ("contact", "CAL-2 Demo | Firma A"), ("contact_two", "CAL-2 Demo | Firma B"),
                    ("admin", "Competence Hub V2 | Administration"),
                ):
                    page = start(browser, base, actor)
                    page.evaluate("(title) => { document.title = title; }", title)
                    if actor == "contact":
                        visitor = page.context.new_page()
                        visitor.route("**/*", lambda route: route.continue_() if route.request.url.startswith(base + "/") else route.abort())
                        if not visitor.goto(base + "/website/").ok:
                            raise RuntimeError("The local website did not load.")
                if restarted:
                    print("CAL2_RESTART=PASS | App und PostgreSQL sind wieder erreichbar.", flush=True)
                print("V2_PLATFORM=READY CAL2_DEMO=READY | Website im Fenster von Firma A; Coach, Prüfung und Administration.", flush=True)
                print("LOKALE_WEBSITE=" + base + "/website/", flush=True)
                print("R + Enter: App und PostgreSQL neu starten. Enter: Demo beenden und Testdaten entfernen.", flush=True)
                try:
                    restart = input().strip().lower() == "r"
                except EOFError:
                    restart = False
            finally:
                browser.close()
        if not restart:
            return
        db.restart()
        restarted = True


def run(db, verify, website):
    fixture = NativeCalendarFixture(local_container_rehearsal=True)
    fixture.roles["contact_two"] = "company_contact"
    fixture.users["contact_two"] = uuid4()
    fixture.emails["contact_two"] = f"synthetic-cal2-{fixture.users['contact_two'].hex}@example.invalid"
    fixture.coach_profile_paths["coach"] = SYNTHETIC_PROFILE
    fixture.prepare()
    for number in (7, 8, 9, 10, 11):
        migration, = (ROOT / "database/migrations").glob(f"{number:04d}_*.sql")
        db.sql(migration.read_text(encoding="utf8"))
    seed_companies(fixture)
    recovery, external, errors = {}, [], []

    def application(port):
        app = fixture.app(port, local_reservations=True)
        attach_website(app, website)
        return app

    def start(browser, base, key, mobile=False):
        return live_page(browser, base, fixture, key, recovery, external, errors, mobile=mobile)

    with sync_playwright() as pw:
        if not verify:
            demo(db, application, start, pw)
            return
        with qa.synthetic_server(application) as base:
            browser = pw.firefox.launch(headless=verify)
            coach, reviewer = start(browser, base, "coach"), start(browser, base, "reviewer")
            coach_api, reviewer_api = Session(coach, base), Session(reviewer, base)
            main_id, main_draft = create_offer(coach_api, reviewer_api, fixture,
                "Demo-Workshop über zwei Tage", 8, 5, 3, multi=True)
            offers = [create_offer(coach_api, reviewer_api, fixture, title, day, capacity, threshold)[0]
                      for title, day, capacity, threshold in (
                          ("Demo: letzter Platz", 14, 1, 1), ("Demo: Wiederholung", 18, 2, 2),
                          ("Demo: Frist", 22, 4, 3),
                      )]
            offers.append(create_offer(coach_api, reviewer_api, fixture, "Demo: Revisionsrennen", 25, 2, 1))
            interrupted, _ = create_offer(coach_api, reviewer_api, fixture, "Demo: Neustart", 29, 1, 1)
            # Seeding rotated the reviewer CSRF; reload the authentic UI session before using it.
            reviewer.reload()
            company = website_to_company(browser, base, fixture, recovery, external, errors, main_id)
            company_b = start(browser, base, "contact_two")
            with tempfile.TemporaryDirectory(prefix="competence-hub-cal2-zoom-") as profile:
                zoom_profile(pw, Path(profile))
                zoom = pw.firefox.launch_persistent_context(profile, headless=True, no_viewport=True, ignore_https_errors=True)
                try:
                    guard_page(zoom.pages[0], base, external, errors)
                    zoom_page, reply_retry = browser_workflow(company, company_b, reviewer, zoom, base)
                    actors = {"coach": coach, "reviewer": zoom_page, "contact": company, "contact_two": company_b}
                    for key in ("admin", "internal"):
                        actors[key] = start(browser, base, key)
                    expect(actors["admin"].get_by_role("heading", name="Zugänge und wichtige Änderungen")).to_be_visible()
                    expect(company.get_by_role("heading", name="Vormerkungen Ihrer Firma").first).to_be_visible()
                    check("Only company and reviewer/admin see their CAL-2 areas",
                          actors["internal"].get_by_role("button", name="Vormerkungen prüfen", exact=True).count() == 0
                          and coach.get_by_role("button", name="Vormerkungen", exact=True).count() == 0)
                    reservation_id = api_workflow(fixture, base, actors, main_id, main_draft, offers, reply_retry)
                    fixture.testing_database_restart = True
                    path, data = interrupt_request(db, fixture, Session(company, base), interrupted)
                finally:
                    zoom.close()
            browser.close()

        fixture.testing_database_restart = False
        with qa.synthetic_server(application) as base:
            browser = pw.firefox.launch()
            try:
                company = start(browser, base, "contact")
                expect(company.locator("#reservation-own").get_by_text("Veranstaltung abgesagt", exact=True)).to_be_visible()
                session = Session(company, base)
                details = session.send("GET", RES + "/" + reservation_id).json()
                check("Backend and PostgreSQL restart: status and six append-only events persisted",
                      details["status"] == "cancelled" and len(details["history"]) == 6)
                retry = session.send("POST", path, data)
                repeated = session.send("POST", path, data)
                check("In-flight locked write interrupted by restart; retry commits exactly one event",
                      retry.status_code == 201 and repeated.json() == retry.json() and
                      len(session.send("GET", RES + "/" + retry.json()["id"]).json()["history"]) == 1)
            finally:
                browser.close()

    async def verify_database(connection):
        totals = (await connection.execute(text("""
            SELECT
              (SELECT count(*) FROM competence_hub.calendar_reservation_events),
              (SELECT count(*) FROM competence_hub.audit_events WHERE entity_type='calendar_reservation'),
              (SELECT count(*) FROM competence_hub.auth_token_delivery_outbox)
        """))).one()
        return totals
    ledger, audit, outbox = fixture.database(verify_database)
    check("History and audit consistent, zero outbox entries, zero browser-external requests or JS errors",
          ledger == audit and ledger > 0 and outbox == 0 and not external and not errors)
    verify_pilot_runtime(db, fixture)


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: run-cal2-local.py [--verify]")
    db = LocalCalendarPostgres()
    try:
        with tempfile.TemporaryDirectory(prefix="competence-hub-v2-platform-") as work:
            website = Path(work) / "website"
            build_website(website)
            with db:
                run(db, "--verify" in sys.argv, website)
    finally:
        if db.removed and db.volume_removed:
            print("CAL2_CLEANUP=PASS | Owned container and volume removed.", flush=True)
    if "--verify" in sys.argv:
        print("CAL2_ACCEPTANCE=PASS", flush=True)
