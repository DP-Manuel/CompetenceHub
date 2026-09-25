from __future__ import annotations

import os
import socket
import subprocess
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright


SCRIPT = Path(__file__).resolve()
WEBSITE_ROOT = SCRIPT.parents[1]
REPO_ROOT = SCRIPT.parents[3]
NODE = REPO_ROOT / "tools" / "node-v22.16.0-win-x64" / "node.exe"

CORE_ROUTES = (
    "/",
    "/unternehmen/",
    "/leistungen/",
    "/mindforge/",
    "/businesscoaching/",
    "/coaches/",
    "/coaches/christian-galvano/",
    "/coaches/manuela-rodriguez/",
    "/coaches/demoprofil-01/",
    "/coaches/demoprofil-02/",
    "/coaches/demoprofil-03/",
    "/coaches/demoprofil-04/",
    "/coaches/demoprofil-05/",
    "/coaches/demoprofil-06/",
    "/kalender/",
    "/ueber-uns/",
    "/kontakt/",
    "/impressum/",
    "/datenschutz/",
    "/404.html",
)

NOINDEX_ROUTES = {
    "/kalender/",
    "/impressum/",
    "/datenschutz/",
    "/404.html",
    *(f"/coaches/demoprofil-{number:02d}/" for number in range(1, 7)),
}

REMOVED_COACH_ROUTES = (
    "/coaches/carolin-hupp/",
    "/coaches/elisabeth-schwabauer/",
    "/coaches/goran-celic/",
    "/coaches/guelcan-elmas-brandes/",
    "/coaches/stefanie-becker/",
    "/coaches/wegner-ney/",
)


class Acceptance:
    def __init__(self) -> None:
        self.count = 0
        self.verbose = os.environ.get("MESSE_ACCEPTANCE_VERBOSE") == "1"

    def check(self, label: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(label)
        self.count += 1
        if self.verbose:
            print(f"PASS | {label}")


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


@contextmanager
def static_server():
    if not NODE.is_file():
        raise RuntimeError(f"repository-local Node.js is missing: {NODE}")
    port = free_port()
    env = os.environ.copy()
    env["PORT"] = str(port)
    process = subprocess.Popen(
        [str(NODE), "scripts/serve-dist.mjs"],
        cwd=WEBSITE_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                raise RuntimeError(f"static server stopped early: {output}")
            try:
                with urllib.request.urlopen(base_url, timeout=0.3) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(0.05)
        else:
            raise RuntimeError("static Website server did not become ready")
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def no_horizontal_overflow(page: Page) -> bool:
    return bool(
        page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth + 1"
        )
    )


def route_checks(
    browser: Browser,
    base_url: str,
    acceptance: Acceptance,
    *,
    name: str,
    width: int,
    height: int,
    device_scale_factor: float = 1,
) -> None:
    context = browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=device_scale_factor,
    )
    try:
        page = context.new_page()
        console_errors: list[str] = []
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        for route in CORE_ROUTES:
            console_errors.clear()
            response = page.goto(f"{base_url}{route}", wait_until="networkidle")
            acceptance.check(f"{name} {route} returns 200", response is not None and response.status == 200)
            acceptance.check(f"{name} {route} has one H1", page.locator("h1").count() == 1)
            acceptance.check(f"{name} {route} has no horizontal overflow", no_horizontal_overflow(page))
            acceptance.check(f"{name} {route} has no review banner", page.locator(".review-banner").count() == 0)
            acceptance.check(f"{name} {route} has image alternatives", page.locator("img:not([alt])").count() == 0)
            acceptance.check(
                f"{name} {route} has no duplicate IDs",
                page.evaluate(
                    """
                    () => {
                      const ids = [...document.querySelectorAll('[id]')].map((node) => node.id);
                      return new Set(ids).size === ids.length;
                    }
                    """
                ),
            )
            acceptance.check(
                f"{name} {route} has named interactive controls",
                page.evaluate(
                    """
                    () => [...document.querySelectorAll('a, button, summary, input, select, textarea')]
                      .every((node) => {
                        if (node.matches('a:not([href])') || node.closest('[hidden]')) return true;
                        const labelled = node.getAttribute('aria-label')
                          || node.getAttribute('aria-labelledby')
                          || node.getAttribute('title')
                          || node.textContent?.trim();
                        if (labelled) return true;
                        return 'labels' in node && node.labels && node.labels.length > 0;
                      })
                    """
                ),
            )

            robots = page.locator('meta[name="robots"]')
            if route in NOINDEX_ROUTES:
                acceptance.check(
                    f"{name} {route} is noindex",
                    robots.count() == 1 and "noindex" in (robots.get_attribute("content") or ""),
                )
            else:
                canonical = page.locator('link[rel="canonical"]')
                acceptance.check(
                    f"{name} {route} has production canonical",
                    canonical.count() == 1
                    and (canonical.get_attribute("href") or "").startswith(
                        "https://competencehub.donner-partner.de"
                    ),
                )
                acceptance.check(
                    f"{name} {route} has OpenGraph basics",
                    page.locator('meta[property="og:title"]').count() == 1
                    and page.locator('meta[property="og:description"]').count() == 1
                    and page.locator('meta[property="og:url"]').count() == 1,
                )
            acceptance.check(
                f"{name} {route} browser console has no errors"
                + (f": {' | '.join(console_errors)}" if console_errors else ""),
                not console_errors,
            )
    finally:
        context.close()


def interaction_checks(browser: Browser, base_url: str, acceptance: Acceptance) -> None:
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    try:
        page = context.new_page()
        page.goto(base_url, wait_until="networkidle")
        acceptance.check("public header has no unfinished Login link", page.get_by_role("link", name="Login").count() == 0)
        acceptance.check("Living Hub is present", page.locator("[data-living-hero]").count() == 1)
        audience_routes = page.locator('.living-hero__routes[aria-label="Direkte Einstiege"]')
        acceptance.check("desktop audience routes are visible", audience_routes.is_visible())
        acceptance.check(
            "desktop company and private entries are in the first viewport",
            all(
                (audience_routes.get_by_role("link", name=name, exact=True).bounding_box() or {}).get("y", 1001) < 1000
                for name in ("Für Unternehmen", "Mindforge · Life Coaching")
            ),
        )
        before = page.locator("[data-coach-viewport]").evaluate("element => element.scrollLeft")
        page.locator("[data-coach-next]").click()
        page.wait_for_timeout(700)
        after = page.locator("[data-coach-viewport]").evaluate("element => element.scrollLeft")
        acceptance.check("Coach rail next control moves the viewport", after != before)

        page.goto(f"{base_url}/coaches/", wait_until="networkidle")
        acceptance.check("Coach directory exposes exactly six demo profiles", page.locator('[data-demo-profile="true"]').count() == 6)
        acceptance.check("Coach directory labels demo status", page.get_by_text("Keine reale Coachperson.", exact=True).count() == 6)
        acceptance.check("Christian Galvano remains an approved real profile", page.get_by_role("heading", name="Herr Christian Galvano", exact=True).count() == 1)
        acceptance.check("Manuela Rodríguez, M.A. is present as the second real profile", page.get_by_role("heading", name="Manuela Rodríguez, M.A.", exact=True).count() == 1)
        manuela_card = page.get_by_role("heading", name="Manuela Rodríguez, M.A.", exact=True).locator("xpath=ancestor::article")
        acceptance.check("Manuela overview uses Erwachsenenbildung", manuela_card.get_by_text("Erwachsenenbildung", exact=True).count() == 1)
        acceptance.check("Manuela overview omits the specialized Bildercoaching tag", manuela_card.get_by_text("NLP- und Bildercoaching", exact=True).count() == 0)
        page.get_by_role("button", name="KI & Transformation").click()
        acceptance.check("KI filter shows only Manuela Rodríguez", page.locator("[data-coach-card]:visible").count() == 1 and page.get_by_role("heading", name="Manuela Rodríguez, M.A.", exact=True).is_visible())

        page.goto(f"{base_url}/coaches/manuela-rodriguez/", wait_until="networkidle")
        acceptance.check("Manuela profile exposes approved KI focus", page.get_by_text("Zertifizierte KI-Managerin mit Fokus auf Human Intelligence", exact=True).count() == 1)
        portrait = page.locator('.coach-profile-portrait img[alt="Porträt von Manuela Rodríguez"]')
        acceptance.check("Manuela profile uses the approved portrait", portrait.count() == 1 and portrait.evaluate("image => image.complete && image.naturalWidth === 1200 && image.naturalHeight === 1200"))

        page.goto(f"{base_url}/coaches/demoprofil-01/", wait_until="networkidle")
        acceptance.check("Demo detail identifies itself as fictional", page.get_by_text("Fiktives Demoprofil zur Veranschaulichung der Plattform. Keine reale Coachperson.", exact=True).count() == 1)

        page.goto(f"{base_url}/unternehmen/", wait_until="networkidle")
        acceptance.check("approved Concept Clean feedback is visible", page.get_by_text("Concept Clean", exact=True).count() >= 1)
        acceptance.check("company hero routes Assessment Center through Personalentwicklung", page.get_by_text("Personalentwicklung · Assessment Center", exact=True).count() == 1)
        acceptance.check("company hero gives Personalentwicklung an intentional wrap point", page.locator('.connected-page-hero__node[aria-label^="Personalentwicklung:"] wbr').count() == 1)
        trigger = page.locator("[data-case-story-trigger]").first
        trigger.click()
        acceptance.check("Use Case opens independently", trigger.get_attribute("aria-expanded") == "true")
        faq = page.locator(".faq-grid details").first
        faq.locator("summary").click()
        acceptance.check("company FAQ opens", faq.get_attribute("open") is not None)

        page.goto(f"{base_url}/leistungen/", wait_until="networkidle")
        acceptance.check("service overview separates Recruiting", page.get_by_role("heading", name="Menschen und Aufgaben passend verbinden", exact=True).count() == 1)
        acceptance.check("service overview explains Personalentwicklung", page.get_by_role("heading", name="Potenziale erkennen und Entwicklung begleiten", exact=True).count() == 1)
        acceptance.check("service hero gives Personalentwicklung an intentional wrap point", page.locator('.connected-page-hero__node[aria-label^="Personalentwicklung:"] wbr').count() == 1)
        personalentwicklung = page.locator("#personalentwicklung")
        acceptance.check("Personalentwicklung groups Assessment Center", personalentwicklung.get_by_text("Development Assessment Center", exact=False).count() == 1)
        acceptance.check("Personalentwicklung groups Supervision", personalentwicklung.get_by_text("Supervision", exact=False).count() == 1)
        acceptance.check("Personalentwicklung keeps Mediation qualification-gated", personalentwicklung.get_by_text("Mediation wird nur bei bestätigter Qualifikation", exact=False).count() == 1)
        service_menu = page.locator(".services-menu__panel")
        acceptance.check("service menu no longer exposes Assessment Center as its own item", service_menu.get_by_role("link", name="Assessment Center", exact=True).count() == 0)
        acceptance.check("service menu no longer exposes Supervision and Mediation as its own item", service_menu.get_by_role("link", name="Supervision & Mediation", exact=True).count() == 0)
        faq_copy = page.locator(".faq-section").inner_text()
        acceptance.check("general service FAQ is not led by Mindforge", "Welche Angebote bündelt Mindforge?" not in faq_copy and "Wie finde ich die passende Leistung?" in faq_copy)

        page.goto(f"{base_url}/mindforge/", wait_until="networkidle")
        acceptance.check("Mindforge no longer duplicates Assessment Center", page.get_by_text("Assessment Center", exact=False).count() == 0)

        page.goto(f"{base_url}/kalender/", wait_until="networkidle")
        acceptance.check(
            "calendar states that all entries are examples",
            page.get_by_text("Ausschließlich Beispieldaten:", exact=True).count() == 1,
        )
        first_event = page.locator(".calendar-event").first
        for _ in range(2):
            if first_event.count() > 0:
                break
            page.locator("[data-next-month]").click()
        acceptance.check("calendar exposes an example event within its bounded window", first_event.count() > 0)
        first_event.click()
        acceptance.check("calendar detail opens", page.locator("[data-detail-content]").is_visible())
        acceptance.check("calendar uses an approved or fictional Coach identity", page.locator("[data-detail-coach]").inner_text() in {"Herr Christian Galvano", "Demoprofil 05", "Demoprofil 06"})
        page.locator("[data-reservation-submit]").click()
        acceptance.check(
            "calendar simulation remains explicitly local",
            "vorschau:" in page.locator("[data-reservation-status]").inner_text().lower()
            and "würde" in page.locator("[data-reservation-status]").inner_text().lower(),
        )

        page.goto(f"{base_url}/kontakt/", wait_until="networkidle")
        acceptance.check("contact route exposes approved mailbox", page.get_by_text("competencehub@donner-partner.de", exact=True).count() >= 1)
        acceptance.check("contact route explains mail-client handoff", page.get_by_text("Ihr E-Mail-Programm", exact=False).count() >= 1)
        topic_options = page.locator('select[name="topic"] option')
        acceptance.check("contact route offers Recruiting separately", topic_options.filter(has_text="Recruiting").count() == 1)
        acceptance.check("contact route offers Personalentwicklung separately", topic_options.filter(has_text="Personalentwicklung").count() == 1)
        acceptance.check("footer exposes central Impressum", page.locator('footer a[href="https://donner-partner.de/dp/impressum/"]').count() == 1)
        acceptance.check("footer exposes central Datenschutz", page.locator('footer a[href="https://donner-partner.de/dp/datenschutz/"]').count() == 1)
    finally:
        context.close()


def removed_profile_checks(browser: Browser, base_url: str, acceptance: Acceptance) -> None:
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    try:
        page = context.new_page()
        for route in REMOVED_COACH_ROUTES:
            response = page.goto(f"{base_url}{route}", wait_until="networkidle")
            acceptance.check(
                f"removed personal route {route} returns controlled 404",
                response is not None and response.status == 404,
            )
            acceptance.check(
                f"removed personal route {route} exposes no former identity",
                page.locator("body").inner_text().find(route.split("/")[-2]) == -1,
            )
    finally:
        context.close()


def accessibility_checks(browser: Browser, base_url: str, acceptance: Acceptance) -> None:
    mobile = browser.new_context(viewport={"width": 390, "height": 844})
    try:
        page = mobile.new_page()
        page.goto(base_url, wait_until="networkidle")
        menu = page.get_by_text("Menü", exact=True)
        menu.focus()
        acceptance.check("mobile menu receives visible keyboard focus", page.evaluate("document.activeElement?.matches(':focus-visible')"))
        page.keyboard.press("Enter")
        acceptance.check("mobile navigation opens from keyboard", page.locator(".nav-menu").get_attribute("open") is not None)
        acceptance.check("mobile navigation includes calendar", page.get_by_role("link", name="Kalender", exact=True).count() >= 1)
        audience_routes = page.locator('.living-hero__routes[aria-label="Direkte Einstiege"]')
        acceptance.check("mobile audience routes are visible", audience_routes.is_visible())
        acceptance.check(
            "mobile company and private entries are in the first viewport",
            all(
                (audience_routes.get_by_role("link", name=name, exact=True).bounding_box() or {}).get("y", 845) < 844
                for name in ("Für Unternehmen", "Mindforge · Life Coaching")
            ),
        )
        page.goto(f"{base_url}/kontakt/", wait_until="networkidle")
        contact_portrait = page.locator('.contact-person img[src*="janay-rappelt.jpg"]')
        acceptance.check("contact page shows Janay portrait", contact_portrait.count() == 1)
        acceptance.check(
            "contact page Janay portrait loads",
            contact_portrait.evaluate("image => image.complete && image.naturalWidth > 0"),
        )
        acceptance.check(
            "contact page exposes Janay phone link",
            page.locator('a[href="tel:+491726799972"]').count() == 1,
        )
    finally:
        mobile.close()

    reduced = browser.new_context(
        viewport={"width": 1440, "height": 1000},
        reduced_motion="reduce",
    )
    try:
        page = reduced.new_page()
        page.goto(base_url, wait_until="networkidle")
        acceptance.check("Reduced Motion preference reaches the page", page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"))
        acceptance.check("Coach rail starts paused for Reduced Motion", page.locator("[data-coach-carousel]").get_attribute("data-paused") == "true")
    finally:
        reduced.close()


def main() -> None:
    acceptance = Acceptance()
    with static_server() as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        try:
            print(f"Browser | Microsoft Edge {browser.version}")
            route_checks(browser, base_url, acceptance, name="desktop", width=1440, height=1000)
            route_checks(browser, base_url, acceptance, name="tablet", width=960, height=900)
            route_checks(browser, base_url, acceptance, name="mobile-390", width=390, height=844)
            route_checks(
                browser,
                base_url,
                acceptance,
                name="200-percent-reflow",
                width=640,
                height=720,
                device_scale_factor=2,
            )
            interaction_checks(browser, base_url, acceptance)
            accessibility_checks(browser, base_url, acceptance)
            removed_profile_checks(browser, base_url, acceptance)
        finally:
            browser.close()
    print(f"Messe browser acceptance complete: {acceptance.count} checks passed")


if __name__ == "__main__":
    main()
