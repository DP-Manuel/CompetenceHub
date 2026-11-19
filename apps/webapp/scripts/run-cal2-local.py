"""Run the CAL-2 demonstration or its acceptance against an owned throwaway database."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from datetime import timedelta
from pathlib import Path
import sys
import tempfile
from uuid import uuid4

import httpx
from playwright.sync_api import expect, sync_playwright
import pyotp
from sqlalchemy import text

from cal1_pilot_acceptance import qa
from local_calendar_postgres import LocalCalendarPostgres
from native_calendar_fixture import NativeCalendarFixture
from vps_pilot_acceptance import zoom_profile

ROOT = Path(__file__).resolve().parents[1]
RES = "/api/v1/portal/reservations"
CAL = "/api/v1/portal/calendar/offers"
PUBLIC = "/api/v1/calendar/offers"
UI = "/portal/"


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


def login(page, base, fixture, actor, recovery):
    first = actor not in recovery
    page.goto(base + UI)
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
    if first and fixture.roles[actor] in {"coach", "calendar_reviewer", "admin"}:
        expect(tour).to_be_visible()
        page.locator("#tour-skip").click()
    elif tour.is_visible():
        page.locator("#tour-skip").click()


def live_page(browser, base, fixture, actor, recovery, external, errors, *, mobile=False):
    page = browser.new_page(ignore_https_errors=True, reduced_motion="reduce",
                            viewport={"width": 390 if mobile else 1440, "height": 920})
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


def browser_workflow(company, reviewer, zoom, base):
    catalogue_button = company.get_by_role("button", name="Plätze vormerken: Demo-Workshop über zwei Tage")
    expect(catalogue_button).to_be_visible()
    catalogue_button.focus()
    company.keyboard.press("Enter")
    expect(company.get_by_role("button", name="Zur Übersicht")).to_be_focused()
    company.keyboard.press("Tab")
    field = company.get_by_role("spinbutton", name="Teilnehmerzahl")
    expect(field).to_be_focused()
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
    check("390 px, keyboard, per-field errors and actual multi-day request", True)

    reviewer.get_by_role("button", name="Vormerkungen prüfen", exact=True).click()
    expect(reviewer.get_by_text("Prüfschwelle noch nicht erreicht")).to_be_visible()
    reviewer.get_by_role("button", name="Vorgang ansehen").click()
    reviewer.get_by_label("Entscheidung", exact=True).select_option("clarification_requested")
    reviewer.get_by_role("button", name="Entscheidung speichern").click()
    expect(reviewer.get_by_label("Begründung für die Firma")).to_be_focused()
    reviewer.get_by_label("Begründung für die Firma").fill("Bitte bestätigen Sie drei Plätze.")
    reviewer.get_by_role("button", name="Entscheidung speichern").click()
    expect(reviewer.get_by_text("Klärung nötig", exact=True)).to_be_visible()

    company.reload()
    expect(company.get_by_text("Klärung nötig", exact=True)).to_be_visible()
    company.get_by_role("button", name="Vorgang ansehen").click()
    expect(company.get_by_text("Bitte bestätigen Sie drei Plätze.")).to_be_visible()
    company.get_by_label("Teilnehmerzahl").fill("3")
    company.get_by_role("button", name="Platzzahl ändern").click()
    expect(company.get_by_text("Platzzahl geändert.", exact=True)).to_be_visible()

    # The isolated 200% browser intentionally takes over the reviewer's current session.
    zoom.add_cookies(reviewer.context.cookies())
    page = zoom.pages[0]
    page.goto(base + UI)
    expect(page.get_by_role("button", name="Vormerkungen prüfen", exact=True)).to_be_visible()
    keyboard_activate(page, page.get_by_role("button", name="Vormerkungen prüfen", exact=True))
    expect(page.get_by_text("Prüfschwelle erreicht", exact=True)).to_be_visible()
    assert 1.9 <= page.evaluate("devicePixelRatio") <= 2.1
    detail = page.get_by_role("button", name="Vorgang ansehen")
    keyboard_activate(page, detail)
    expect(page.get_by_text("Prüfschwelle bei diesem Schritt erreicht.")).to_be_visible()
    assert_layout(page)
    page.get_by_label("Entscheidung", exact=True).select_option("approved")
    page.get_by_label("Begründung für die Firma").fill("Fachlich geprüft, keine verbindliche Buchung.")
    keyboard_activate(page, page.get_by_role("button", name="Entscheidung speichern"))
    expect(page.get_by_text("Entscheidung gespeichert.", exact=True)).to_be_visible()
    toggle = page.get_by_role("checkbox", name="Auch abgeschlossene Vorgänge anzeigen")
    expect(toggle).to_be_visible()
    keyboard_activate(page, toggle)
    expect(page.get_by_text("Positiv geprüft", exact=True)).to_be_visible()
    company.reload()
    expect(company.get_by_text("Positiv geprüft", exact=True)).to_be_visible()
    check("Reviewer clarification, threshold task, approval and company history at native 200% zoom", True)
    return page


def api_workflow(fixture, base, actors, main_id, main_draft, offers):
    a, b, reviewer, coach, internal, admin = (Session(actors[key], base) for key in
        ("contact", "contact_two", "reviewer", "coach", "internal", "admin"))
    request_main = a.send("GET", RES).json()["items"][0]
    id_main = request_main["id"]
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
    offer_last, offer_repeat, offer_deadline = offers
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

    deadline_path = RES + "/offers/" + offer_deadline
    in_time = a.send("POST", deadline_path, request_data(2))
    assert in_time.status_code == 201
    deadline_detail = RES + "/" + in_time.json()["id"]
    async def pass_deadline(connection):
        await connection.execute(text("""
            UPDATE competence_hub.calendar_offer_revisions
            SET decision_deadline = clock_timestamp() - interval '1 second'
            WHERE offer_id = CAST(:id AS uuid)
        """), {"id": offer_deadline})
    fixture.database(pass_deadline)
    check("Passed deadline: new/increased seats fail, existing items stay visible and may decrease/withdraw", (
        b.send("POST", deadline_path, request_data(1)).json()["code"] == "reservation_deadline"
        and a.send("PATCH", deadline_detail + "/seats",
                   {"request_id": str(uuid4()), "seats": 3}, version=1).json()["code"] == "reservation_deadline"
        and reviewer.send("GET", deadline_detail + "?review=true").json()["deadline_passed"]
        and a.send("PATCH", deadline_detail + "/seats",
                   {"request_id": str(uuid4()), "seats": 1}, version=1).status_code == 200
        and a.send("POST", deadline_detail + "/withdraw", {"request_id": str(uuid4())}, version=2).status_code == 200
    ))
    cal_path = CAL + "/" + main_id
    revised = coach.send("PATCH", cal_path + "/draft", {**main_draft, "capacity": 2, "review_threshold": 2}, version=3)
    assert revised.status_code == 200
    submitted = coach.send("POST", cal_path + "/submit", version=4)
    assert submitted.status_code == 200
    blocked = reviewer.send("POST", cal_path + "/review-decisions", {"outcome": "published"}, version=5)
    check("Active reservations prevent replacing approved terms", blocked.status_code == 409)
    check("Offer cancellation releases seats atomically and adds a customer-visible event", (
        coach.send("POST", cal_path + "/withdraw", version=5).status_code == 200
        and a.send("GET", PUBLIC + "/" + main_id).status_code == 404
        and (cancelled := a.send("GET", RES + "/" + id_main).json())["status"] == "cancelled"
        and cancelled["history"][0]["event"] == "offer_cancelled"
        and cancelled["history"][0]["occupied_delta"] == -3
    ))
    return id_main


def run(db, verify):
    fixture = NativeCalendarFixture(local_container_rehearsal=True)
    fixture.roles["contact_two"] = "company_contact"
    fixture.users["contact_two"] = uuid4()
    fixture.emails["contact_two"] = f"synthetic-cal2-{fixture.users['contact_two'].hex}@example.invalid"
    fixture.prepare()
    for number in (7, 8, 9, 10):
        migration, = (ROOT / "database/migrations").glob(f"{number:04d}_*.sql")
        db.sql(migration.read_text(encoding="utf8"))
    seed_companies(fixture)
    recovery, external, errors = {}, [], []

    def application(port):
        return fixture.app(port, local_reservations=True)

    def start(browser, base, key, mobile=False):
        return live_page(browser, base, fixture, key, recovery, external, errors, mobile=mobile)

    with sync_playwright() as pw:
        with qa.synthetic_server(application) as base:
            browser = pw.firefox.launch(headless=verify)
            coach, reviewer = start(browser, base, "coach"), start(browser, base, "reviewer")
            coach_api, reviewer_api = Session(coach, base), Session(reviewer, base)
            main_id, main_draft = create_offer(coach_api, reviewer_api, fixture,
                "Demo-Workshop über zwei Tage", 8, 5, 3, multi=True)
            if not verify:
                coach.close()
                reviewer.close()
                company = start(browser, base, "contact")
                reviewer = start(browser, base, "reviewer")
                reviewer.get_by_role("button", name="Vormerkungen prüfen", exact=True).click()
                print("CAL2_DEMO=READY | Zwei Firefox-Fenster: Demo-Firma A und Reviewer.", flush=True)
                print("Nur synthetische lokale Daten. Enter beendet die Demo und entfernt Container und Volume.", flush=True)
                with suppress(EOFError):
                    input()
                browser.close()
                return
            offers = [create_offer(coach_api, reviewer_api, fixture, title, day, capacity, threshold)[0]
                      for title, day, capacity, threshold in (
                          ("Demo: letzter Platz", 14, 1, 1), ("Demo: Wiederholung", 18, 2, 2),
                          ("Demo: Frist", 22, 4, 3),
                      )]
            # Seeding rotated the reviewer CSRF; reload the authentic UI session before using it.
            reviewer.reload()
            company = start(browser, base, "contact", mobile=True)
            with tempfile.TemporaryDirectory(prefix="competence-hub-cal2-zoom-") as profile:
                zoom_profile(pw, Path(profile))
                zoom = pw.firefox.launch_persistent_context(profile, headless=True, no_viewport=True, ignore_https_errors=True)
                try:
                    guard_page(zoom.pages[0], base, external, errors)
                    zoom_page = browser_workflow(company, reviewer, zoom, base)
                    actors = {"coach": coach, "reviewer": zoom_page, "contact": company}
                    for key in ("contact_two", "admin", "internal"):
                        actors[key] = start(browser, base, key)
                    check("Only company and reviewer/admin see their CAL-2 areas",
                          actors["internal"].get_by_role("button", name="Vormerkungen prüfen", exact=True).count() == 0
                          and coach.get_by_role("button", name="Vormerkungen", exact=True).count() == 0)
                    reservation_id = api_workflow(fixture, base, actors, main_id, main_draft, offers)
                finally:
                    zoom.close()
            browser.close()

        db.restart()
        with qa.synthetic_server(application) as base:
            browser = pw.firefox.launch()
            try:
                company = start(browser, base, "contact")
                expect(company.get_by_text("Veranstaltung abgesagt", exact=True)).to_be_visible()
                details = Session(company, base).send("GET", RES + "/" + reservation_id).json()
                check("Backend and PostgreSQL restart: status and five append-only events persisted",
                      details["status"] == "cancelled" and len(details["history"]) == 5)
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


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: run-cal2-local.py [--verify]")
    db = LocalCalendarPostgres()
    try:
        with db:
            run(db, "--verify" in sys.argv)
    finally:
        if db.removed and db.volume_removed:
            print("CAL2_CLEANUP=PASS | Owned container and volume removed.", flush=True)
    if "--verify" in sys.argv:
        print("CAL2_ACCEPTANCE=PASS", flush=True)
