from __future__ import annotations

import asyncio
import socket
import ssl
import tempfile
import threading
import time
import urllib.request
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import uvicorn
from playwright.sync_api import Browser, Page, Playwright, expect, sync_playwright

from browser_acceptance_app import (
    ADMIN_EMAIL,
    COMPANY_CONTACT_EMAIL,
    COACH_EMAIL,
    EMPTY_COACH_EMAIL,
    ENROLLMENT_EMAIL,
    HOST,
    INTERNAL_EMAIL,
    RECOVERY_CODE,
    REVIEWER_EMAIL,
    SYNTHETIC_PASSWORD,
    TOTP_CODE,
    create_acceptance_app,
    create_loopback_certificate,
)


class Acceptance:
    def __init__(self) -> None:
        self.checks: list[str] = []

    def check(self, label: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(label)
        self.checks.append(label)
        print(f"PASS | {label}")


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind((HOST, 0))
        return int(probe.getsockname()[1])


def wait_until_ready(url: str) -> None:
    context = ssl._create_unverified_context()
    for _ in range(50):
        try:
            with urllib.request.urlopen(f"{url}/health/live", context=context, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("synthetic browser fixture did not become ready")


@contextmanager
def synthetic_server():
    port = free_port()
    with tempfile.TemporaryDirectory(prefix="competence-hub-cal1-browser-") as run_root:
        certificate, key = create_loopback_certificate(Path(run_root) / "certificate")
        config = uvicorn.Config(
            create_acceptance_app(port),
            host=HOST,
            port=port,
            ssl_certfile=str(certificate),
            ssl_keyfile=str(key),
            log_level="warning",
            access_log=False,
        )
        server = uvicorn.Server(config)

        def run_server() -> None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            def handle_loop_error(_loop, context) -> None:
                if isinstance(context.get("exception"), ConnectionResetError):
                    return
                _loop.default_exception_handler(context)

            loop.set_exception_handler(handle_loop_error)
            try:
                loop.run_until_complete(server.serve())
            finally:
                loop.close()

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        url = f"https://{HOST}:{port}"
        wait_until_ready(url)
        try:
            yield url
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            if thread.is_alive():
                raise RuntimeError("synthetic browser fixture did not stop")


def login(page: Page, base_url: str, email: str) -> None:
    page.goto(f"{base_url}/portal/", wait_until="domcontentloaded")
    page.locator("#login-email").fill(email)
    page.locator("#login-password").fill(SYNTHETIC_PASSWORD)
    page.get_by_role("button", name="Anmelden").click()
    page.locator("#mfa-code").fill(TOTP_CODE)
    page.get_by_role("button", name="Bestätigen").click()
    page.locator("#portal-view").wait_for(state="visible")


def logout(page: Page) -> None:
    page.locator("#logout-button").click()
    page.locator("#login-view").wait_for(state="visible")


def open_area(page: Page, name: str) -> None:
    button = page.get_by_role("button", name=name, exact=True)
    if button.count():
        button.click()


def card(page: Page, title: str):
    return page.locator("#coach-calendar-list .calendar-card").filter(has_text=title)


def review_card(page: Page, title: str):
    return page.locator("#review-calendar-list .calendar-card").filter(has_text=title)


def tab_to_button(page: Page, label: str, card_title: str | None = None) -> None:
    for _ in range(80):
        active = page.evaluate(
            """({label, cardTitle}) => {
              const element = document.activeElement;
              const card = element?.closest('.calendar-card');
              return element?.tagName === 'BUTTON'
                && element.textContent.trim() === label
                && (!cardTitle || card?.textContent.includes(cardTitle));
            }""",
            {"label": label, "cardTitle": card_title},
        )
        if active:
            return
        page.keyboard.press("Tab")
    raise AssertionError(f"keyboard focus did not reach {label!r}")


def future_values(offset_days: int = 30) -> dict[str, str]:
    start = (datetime.now(UTC) + timedelta(days=offset_days)).replace(
        hour=9, minute=30, second=0, microsecond=0
    )
    end = start + timedelta(hours=2)
    deadline = start - timedelta(days=5)
    return {
        "start": start.strftime("%Y-%m-%dT%H:%M"),
        "end": end.strftime("%Y-%m-%dT%H:%M"),
        "deadline": deadline.strftime("%Y-%m-%dT%H:%M"),
    }


def fill_offer(page: Page, title: str, offset_days: int = 30) -> None:
    values = future_values(offset_days)
    page.locator("#calendar-title").fill(title)
    page.locator("#calendar-topic").select_option(index=1)
    page.locator("#calendar-summary").fill("Synthetische Browserabnahme.")
    page.locator("#calendar-starts-at").fill(values["start"])
    page.locator("#calendar-ends-at").fill(values["end"])
    page.locator("#calendar-format").select_option("online")
    page.locator("#calendar-location").fill("Synthetischer Zugangslink")
    page.locator("#calendar-capacity").fill("12")
    page.locator("#calendar-review-threshold").fill("6")
    page.locator("#calendar-decision-deadline").fill(values["deadline"])
    page.locator("#calendar-price").fill("Preis nach Abstimmung")


def create_offer(page: Page, title: str, offset_days: int = 30) -> None:
    page.locator("#open-calendar-offer-dialog").click()
    fill_offer(page, title, offset_days)
    page.locator("#save-calendar-offer").dblclick()
    page.locator("#calendar-offer-dialog").wait_for(state="hidden")


def submit_offer(page: Page, title: str) -> None:
    card(page, title).get_by_role("button", name="Zur Prüfung einreichen").click()
    expect(card(page, title)).to_contain_text("Zur Prüfung eingereicht")


def api_offers(page: Page) -> list[dict[str, object]]:
    return page.evaluate(
        """async () => {
          const response = await fetch('/api/v1/portal/calendar/offers', {
            credentials: 'same-origin', headers: {Accept: 'application/json'}
          });
          if (!response.ok) throw new Error(`offers ${response.status}`);
          return (await response.json()).items;
        }"""
    )


def api_topics(page: Page) -> list[dict[str, object]]:
    return page.evaluate(
        """async () => {
          const response = await fetch('/api/v1/portal/calendar/topics', {
            credentials: 'same-origin', headers: {Accept: 'application/json'}
          });
          if (!response.ok) throw new Error(`topics ${response.status}`);
          return (await response.json()).items;
        }"""
    )


def api_offer_detail(page: Page, offer_id: str) -> dict[str, object]:
    return page.evaluate(
        """async (offerId) => {
          const response = await fetch(`/api/v1/portal/calendar/offers/${offerId}`, {
            credentials: 'same-origin', headers: {Accept: 'application/json'}
          });
          if (!response.ok) throw new Error(`offer detail ${response.status}`);
          return await response.json();
        }""",
        offer_id,
    )


def api_review_queue(page: Page) -> list[dict[str, object]]:
    return page.evaluate(
        """async () => {
          const response = await fetch('/api/v1/portal/calendar/review-queue', {
            credentials: 'same-origin', headers: {Accept: 'application/json'}
          });
          if (!response.ok) throw new Error(`review queue ${response.status}`);
          return (await response.json()).items;
        }"""
    )


def company_regression(page: Page, acceptance: Acceptance) -> None:
    page.locator("#open-company-dialog").click()
    page.locator("#create-company-name").fill("Synthetische Browserfirma")
    page.locator("#create-company-industry").fill("Softwaretest")
    page.locator("#create-company-notes").fill("Keine Echtdaten.")
    page.locator("#create-contact-first-name").fill("Test")
    page.locator("#create-contact-last-name").fill("Kontakt")
    page.locator("#create-contact-email").fill("synthetic.contact@example.invalid")
    page.get_by_role("button", name="Firma anlegen", exact=True).last.click()
    page.locator("#company-dialog").wait_for(state="hidden")
    expect(page.locator("#detail-company-name")).to_have_text("Synthetische Browserfirma")
    acceptance.check(
        "Firmenanlage mit Erstkontakt bleibt funktionsfaehig",
        "synthetic.contact@example.invalid" in page.locator("#contact-list").inner_text(),
    )


def admin_contract(page: Page, base_url: str, acceptance: Acceptance) -> None:
    login(page, base_url, ADMIN_EMAIL)
    acceptance.check(
        "Admin sieht nur dokumentierte Portalbereiche",
        page.locator("#portal-navigation button").all_text_contents()
        == ["Firmen", "Kalenderangebote", "Prüfliste"],
    )
    open_area(page, "Kalenderangebote")
    offers = api_offers(page)
    topics = api_topics(page)
    acceptance.check("Admin API liefert freigegebenes Thema", len(topics) == 1)
    by_status = {str(item["workflow_status"]): item for item in offers}
    for status in ("draft", "published", "changes_requested"):
        item = by_status[status]
        acceptance.check(f"Admin API {status}: lifecycle active", item["lifecycle_status"] == "active")
        acceptance.check(f"Admin API {status}: revision 1", item["revision_number"] == 1)
    acceptance.check(
        "Draft ist direkt editierbar",
        card(page, "Synthetisches Angebot 1").get_by_role("button", name="Entwurf bearbeiten").count() == 1,
    )
    acceptance.check(
        "Published bietet nur neue Revision",
        card(page, "Synthetisches Angebot 3").get_by_role("button", name="Neue Revision bearbeiten").count() == 1,
    )
    acceptance.check(
        "Changes requested bietet nur neue Revision",
        card(page, "Synthetisches Angebot 4").get_by_role("button", name="Neue Revision bearbeiten").count() == 1,
    )
    in_review = card(page, "Synthetisches Angebot 2")
    acceptance.check("In review ist nicht direkt editierbar", in_review.get_by_text("bearbeiten").count() == 0)
    acceptance.check("In review darf zurueckgezogen werden", in_review.get_by_role("button", name="Angebot zurückziehen").count() == 1)
    draft_offer = by_status["draft"]
    draft_detail = api_offer_detail(page, str(draft_offer["id"]))
    topic_id = str(topics[0]["id"])
    acceptance.check(
        "Admin-Detail referenziert freigegebenes Thema",
        str(draft_detail["current_revision"]["topic_id"]) == topic_id,
    )
    option_values = page.locator("#calendar-topic option").evaluate_all(
        "options => options.map(option => option.value)",
    )
    acceptance.check("Admin-Formular rendert freigegebenes Thema", topic_id in option_values)
    card(page, "Synthetisches Angebot 1").get_by_role("button", name="Entwurf bearbeiten").click()
    page.locator("#calendar-offer-dialog").wait_for(state="visible")
    acceptance.check(
        "Admin-Dialog enthaelt freigegebenes Thema",
        page.locator("#calendar-topic").input_value() == topic_id,
    )
    page.get_by_role("button", name="Abbrechen").last.click()

    for original_title, revised_title in (
        ("Synthetisches Angebot 3", "Published Revision im Browser"),
        ("Synthetisches Angebot 4", "Changes Requested Revision im Browser"),
    ):
        card(page, original_title).get_by_role("button", name="Neue Revision bearbeiten").click()
        page.locator("#calendar-offer-dialog").wait_for(state="visible")
        if original_title == "Synthetisches Angebot 4":
            acceptance.check(
                "Changes Requested zeigt Reviewhinweis",
                page.locator("#calendar-review-feedback").is_visible(),
            )
        page.locator("#calendar-title").fill(revised_title)
        page.locator("#save-calendar-offer").click()
        page.locator("#calendar-offer-dialog").wait_for(state="hidden")
        revised = card(page, revised_title)
        acceptance.check(
            f"{original_title} erzeugt Revision 2 als Draft",
            "Aktuelle Revision: 2" in revised.inner_text()
            and "Entwurf" in revised.inner_text()
            and revised.get_by_role("button", name="Entwurf bearbeiten").count() == 1,
        )
        revised_offer = next(item for item in api_offers(page) if item["title"] == revised_title)
        revised_detail = api_offer_detail(page, str(revised_offer["id"]))
        acceptance.check(
            f"{original_title} behaelt korrekte Revisionsprojektion",
            revised_detail["current_revision"]["revision_number"] == 2
            and revised_detail["current_revision"]["workflow_status"] == "draft",
        )
        if original_title == "Synthetisches Angebot 3":
            acceptance.check(
                "Published Revision 1 bleibt unveraendert erhalten",
                revised_detail["published_revision"]["revision_number"] == 1
                and revised_detail["published_revision"]["title"] == original_title,
            )

    open_area(page, "Firmen")
    company_regression(page, acceptance)
    logout(page)


def coach_workflow(page: Page, browser: Browser, base_url: str, acceptance: Acceptance) -> None:
    login(page, base_url, COACH_EMAIL)
    title = "Automatischer Browserentwurf"
    create_offer(page, title)
    acceptance.check("Doppelklick erzeugt genau einen Draft", page.get_by_role("heading", name=title, exact=True).count() == 1)

    own_card = card(page, title)
    own_card.get_by_role("button", name="Entwurf bearbeiten").click()
    page.locator("#calendar-title").fill(f"{title} bearbeitet")
    page.locator("#save-calendar-offer").click()
    page.locator("#calendar-offer-dialog").wait_for(state="hidden")
    edited_title = f"{title} bearbeitet"
    acceptance.check("Draft bearbeiten und speichern", page.get_by_role("heading", name=edited_title, exact=True).count() == 1)

    tab_to_button(page, "Entwurf bearbeiten", edited_title)
    page.keyboard.press("Enter")
    page.locator("#calendar-offer-dialog").wait_for(state="visible")
    acceptance.check(
        "Dialog setzt Tastaturfokus auf den Titel",
        page.locator("#calendar-title").evaluate("element => element === document.activeElement"),
    )
    keyboard_title = f"{edited_title} Tastatur"
    page.keyboard.press("Control+A")
    page.keyboard.insert_text(keyboard_title)
    tab_to_button(page, "Entwurf speichern")
    focused_outline = page.evaluate(
        """() => {
          const style = getComputedStyle(document.activeElement);
          return `${style.outlineStyle} ${style.outlineWidth}`;
        }"""
    )
    acceptance.check("Tastaturfokus ist sichtbar", "none" not in focused_outline and "0px" not in focused_outline)
    page.keyboard.press("Enter")
    page.locator("#calendar-offer-dialog").wait_for(state="hidden")
    acceptance.check(
        "Draft vollstaendig per Tastatur bearbeitet",
        page.get_by_role("heading", name=keyboard_title, exact=True).count() == 1,
    )
    edited_title = keyboard_title

    stale_title = "Stale Ausgang"
    create_offer(page, stale_title, 40)
    second_context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000})
    second = second_context.new_page()
    login(second, base_url, COACH_EMAIL)
    open_area(second, "Kalenderangebote")
    card(page, stale_title).get_by_role("button", name="Entwurf bearbeiten").click()
    card(second, stale_title).get_by_role("button", name="Entwurf bearbeiten").click()
    page.locator("#calendar-title").fill("Stale Stand A")
    page.locator("#save-calendar-offer").click()
    page.locator("#calendar-offer-dialog").wait_for(state="hidden")
    second.locator("#calendar-title").fill("Stale Stand B")
    second.locator("#save-calendar-offer").click()
    second.locator("#calendar-offer-error").wait_for(state="visible")
    acceptance.check("Stale ETag zeigt Konflikt", "geändert" in second.locator("#calendar-offer-error").inner_text())
    acceptance.check("Stale Mutation wird nicht automatisch wiederholt", second.locator("#calendar-offer-dialog").is_visible())
    second.locator("#reload-calendar-offer").click()
    expect(second.locator("#calendar-title")).to_have_value("Stale Stand A")
    acceptance.check("Stale Recovery laedt Serverstand", second.locator("#calendar-title").input_value() == "Stale Stand A")
    second.get_by_role("button", name="Abbrechen").last.click()
    second_context.close()

    tab_to_button(page, "Zur Prüfung einreichen", edited_title)
    page.keyboard.press("Enter")
    expect(card(page, edited_title)).to_contain_text("Zur Prüfung eingereicht")
    acceptance.check("Submit aktualisiert Textstatus", "Zur Prüfung eingereicht" in card(page, edited_title).inner_text())

    withdraw_title = "Zum Zurückziehen"
    create_offer(page, withdraw_title, 45)
    card(page, withdraw_title).get_by_role("button", name="Angebot zurückziehen").click()
    expect(card(page, withdraw_title)).to_contain_text("Zurückgezogen")
    withdrawn = card(page, withdraw_title)
    acceptance.check(
        "Zurueckgezogenes Angebot hat keine Mutation mehr",
        "Zurückgezogen" in withdrawn.inner_text()
        and withdrawn.locator(".calendar-card-actions button").count() == 0,
    )

    publish_title = "Zur Veröffentlichung"
    create_offer(page, publish_title, 50)
    submit_offer(page, publish_title)
    logout(page)


def reviewer_workflow(page: Page, base_url: str, acceptance: Acceptance) -> None:
    login(page, base_url, REVIEWER_EMAIL)
    acceptance.check(
        "Reviewer sieht nur Pruefliste",
        page.locator("#review-calendar-workspace").is_visible()
        and not page.locator("#company-workspace").is_visible()
        and page.locator("#coach-calendar-workspace").count() == 0,
    )
    queue = page.locator("#review-calendar-list .calendar-card")
    acceptance.check("Reviewer Queue ist nicht leer", queue.count() >= 2)
    tab_to_button(page, "Angebot prüfen", "Synthetisches Angebot 2")
    page.keyboard.press("Enter")
    page.locator("#calendar-review-dialog").wait_for(state="visible")
    review_summary = page.locator("#calendar-review-summary").inner_text()
    acceptance.check(
        "Reviewer-Projektion zeigt Coach, Thema und keine UUID",
        "Coach A" in review_summary
        and "Führung und Zusammenarbeit" in review_summary
        and "Synthetisches Angebot 2" in review_summary
        and "Präsenz" in review_summary
        and "Würzburg" in review_summary
        and "Kapazität" in review_summary
        and "Revision" in review_summary
        and "00000000-" not in review_summary,
    )
    acceptance.check(
        "Reviewer-Dialog fokussiert die erste Entscheidung",
        page.get_by_label("Veröffentlichen").evaluate("element => element === document.activeElement"),
    )
    page.keyboard.press("ArrowDown")
    tab_to_button(page, "Entscheidung speichern")
    page.keyboard.press("Enter")
    acceptance.check("Aenderungshinweis ist verpflichtend", page.locator("#calendar-review-note").evaluate("el => el === document.activeElement"))
    page.keyboard.insert_text("Bitte synthetisch präzisieren.")
    tab_to_button(page, "Entscheidung speichern")
    page.keyboard.press("Enter")
    page.locator("#calendar-review-dialog").wait_for(state="hidden")
    acceptance.check("Aenderungsentscheidung entfernt Angebot aus Queue", review_card(page, "Synthetisches Angebot 2").count() == 0)

    publish_item = next(item for item in api_review_queue(page) if item["title"] == "Zur Veröffentlichung")
    tab_to_button(page, "Angebot prüfen", "Zur Veröffentlichung")
    page.keyboard.press("Enter")
    page.locator("#calendar-review-dialog").wait_for(state="visible")
    page.keyboard.press("Space")
    tab_to_button(page, "Entscheidung speichern")
    page.keyboard.press("Enter")
    page.locator("#calendar-review-dialog").wait_for(state="hidden")
    acceptance.check("Veroeffentlichung entfernt Angebot aus Queue", review_card(page, "Zur Veröffentlichung").count() == 0)
    published_detail = api_offer_detail(page, str(publish_item["id"]))
    acceptance.check(
        "Reviewentscheidung projiziert Published-Status",
        published_detail["current_revision"]["workflow_status"] == "published",
    )
    logout(page)


def role_and_accessibility_checks(browser: Browser, base_url: str, acceptance: Acceptance) -> None:
    context = browser.new_context(ignore_https_errors=True, viewport={"width": 390, "height": 844})
    page = context.new_page()
    login(page, base_url, EMPTY_COACH_EMAIL)
    acceptance.check("Coach Empty State", page.locator("#coach-calendar-empty").is_visible())
    acceptance.check("390 px ohne horizontale Ueberbreite", page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
    mobile_geometry = page.locator("h1, h2, h3, p, button, input, select, textarea").evaluate_all(
        """elements => elements
          .filter(element => element.getClientRects().length && getComputedStyle(element).visibility !== 'hidden')
          .every(element => {
            const rect = element.getBoundingClientRect();
            return rect.left >= -1 && rect.right <= window.innerWidth + 1
              && element.scrollWidth <= element.clientWidth + 1;
          })"""
    )
    acceptance.check("390 px ohne abgeschnittene sichtbare Texte", mobile_geometry)
    mobile_targets = page.locator("button:visible").evaluate_all(
        "buttons => buttons.every(button => button.getBoundingClientRect().height >= 38)",
    )
    acceptance.check("390 px Hauptziele bleiben ausreichend gross", mobile_targets)
    page.emulate_media(reduced_motion="reduce")
    acceptance.check("Reduced Motion wird vom Browser gemeldet", page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"))
    acceptance.check(
        "Reduced Motion minimiert UI-Transitionen",
        page.locator("#logout-button").evaluate(
            "element => parseFloat(getComputedStyle(element).transitionDuration) <= 0.001",
        ),
    )
    page.keyboard.press("Tab")
    acceptance.check("Tastaturfokus bleibt sichtbar adressierbar", page.evaluate("document.activeElement !== document.body"))
    logout(page)

    login(page, base_url, INTERNAL_EMAIL)
    acceptance.check("Internal sieht Firmen", page.locator("#company-workspace").is_visible())
    acceptance.check("Internal sieht keine Pruefliste", page.locator("#review-calendar-workspace").count() == 0)
    logout(page)

    login(page, base_url, COMPANY_CONTACT_EMAIL)
    acceptance.check("Firmenkontakt bleibt ohne CAL-1-Verwaltung", page.locator("#coach-calendar-workspace").count() == 0 and page.locator("#review-calendar-workspace").count() == 0)
    logout(page)
    context.close()

    context = browser.new_context(
        ignore_https_errors=True,
        viewport={"width": 640, "height": 500},
        device_scale_factor=2,
    )
    page = context.new_page()
    login(page, base_url, ADMIN_EMAIL)
    open_area(page, "Kalenderangebote")
    acceptance.check(
        "200 Prozent Zoom ohne Dokument-Ueberbreite",
        page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"),
    )
    card(page, "Synthetisches Angebot 1").get_by_role("button", name="Entwurf bearbeiten").click()
    page.locator("#calendar-offer-dialog").wait_for(state="visible")
    zoom_dialog_fits = page.locator("#calendar-offer-dialog").evaluate(
        "element => element.scrollWidth <= element.clientWidth + 1 && element.getBoundingClientRect().width <= window.innerWidth",
    )
    acceptance.check("200 Prozent Zoom haelt Dialog und Aktionen erreichbar", zoom_dialog_fits)
    page.keyboard.press("Escape")
    acceptance.check("Dialog schliesst per Escape", not page.locator("#calendar-offer-dialog").is_visible())
    context.close()


def enrollment_check(browser: Browser, base_url: str, acceptance: Acceptance) -> None:
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    page.goto(f"{base_url}/portal/", wait_until="domcontentloaded")
    page.locator("#login-email").fill(ENROLLMENT_EMAIL)
    page.locator("#login-password").fill(SYNTHETIC_PASSWORD)
    page.get_by_role("button", name="Anmelden").click()
    page.locator("#enrollment-code").fill(TOTP_CODE)
    page.get_by_role("button", name="Einrichtung abschließen").click()
    expect(page.locator("#recovery-codes li")).to_have_count(10)
    acceptance.check("MFA Enrollment zeigt Recovery Codes", page.locator("#recovery-codes li").count() == 10)
    context.close()


def recovery_check(browser: Browser, base_url: str, acceptance: Acceptance) -> None:
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    page.goto(f"{base_url}/portal/", wait_until="domcontentloaded")
    page.locator("#login-email").fill(INTERNAL_EMAIL)
    page.locator("#login-password").fill(SYNTHETIC_PASSWORD)
    page.get_by_role("button", name="Anmelden").click()
    page.get_by_text("Recovery-Code", exact=True).click()
    page.locator("#mfa-code").fill(RECOVERY_CODE)
    page.get_by_role("button", name="Bestätigen").click()
    page.locator("#portal-view").wait_for(state="visible")
    acceptance.check("Recovery-Code eroeffnet autorisierten Portalbereich", page.locator("#company-workspace").is_visible())
    context.close()


def generic_error_check(browser: Browser, base_url: str, acceptance: Acceptance) -> None:
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    page.goto(f"{base_url}/portal/", wait_until="domcontentloaded")
    page.locator("#login-email").fill(COACH_EMAIL)
    page.locator("#login-password").fill("absichtlich-falsch")
    page.get_by_role("button", name="Anmelden").click()
    page.locator("#login-error").wait_for(state="visible")
    message = page.locator("#login-error").inner_text()
    acceptance.check(
        "Fehlerzustand bleibt generisch und ohne Technikdetails",
        bool(message.strip())
        and not any(fragment in message.lower() for fragment in ("traceback", "exception", "sql", "stack", "uuid")),
    )
    context.close()


def run(playwright: Playwright, base_url: str) -> Acceptance:
    acceptance = Acceptance()
    browser = playwright.chromium.launch(channel="msedge", headless=True)
    print(f"Browser | Microsoft Edge {browser.version}")
    try:
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        admin_contract(page, base_url, acceptance)
        coach_workflow(page, browser, base_url, acceptance)
        reviewer_workflow(page, base_url, acceptance)
        context.close()
        role_and_accessibility_checks(browser, base_url, acceptance)
        enrollment_check(browser, base_url, acceptance)
        recovery_check(browser, base_url, acceptance)
        generic_error_check(browser, base_url, acceptance)
        return acceptance
    finally:
        browser.close()


def main() -> None:
    with synthetic_server() as base_url, sync_playwright() as playwright:
        acceptance = run(playwright, base_url)
    print(f"CAL-1 browser acceptance complete: {len(acceptance.checks)} checks passed")


if __name__ == "__main__":
    main()
