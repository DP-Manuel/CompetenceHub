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
    "/coaches/carolin-hupp/",
    "/coaches/christian-galvano/",
    "/coaches/elisabeth-schwabauer/",
    "/coaches/goran-celic/",
    "/coaches/guelcan-elmas-brandes/",
    "/coaches/stefanie-becker/",
    "/coaches/wegner-ney/",
    "/kalender/",
    "/ueber-uns/",
    "/kontakt/",
    "/impressum/",
    "/datenschutz/",
    "/404.html",
)

NOINDEX_ROUTES = {"/kalender/", "/impressum/", "/datenschutz/", "/404.html"}


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
        before = page.locator("[data-coach-viewport]").evaluate("element => element.scrollLeft")
        page.locator("[data-coach-next]").click()
        page.wait_for_timeout(700)
        after = page.locator("[data-coach-viewport]").evaluate("element => element.scrollLeft")
        acceptance.check("Coach rail next control moves the viewport", after != before)

        page.goto(f"{base_url}/unternehmen/", wait_until="networkidle")
        acceptance.check("approved Concept Clean feedback is visible", page.get_by_text("Concept Clean", exact=True).count() >= 1)
        trigger = page.locator("[data-case-story-trigger]").first
        trigger.click()
        acceptance.check("Use Case opens independently", trigger.get_attribute("aria-expanded") == "true")
        faq = page.locator(".faq-grid details").first
        faq.locator("summary").click()
        acceptance.check("company FAQ opens", faq.get_attribute("open") is not None)

        page.goto(f"{base_url}/kalender/", wait_until="networkidle")
        acceptance.check(
            "calendar states that all entries are examples",
            page.get_by_text("Ausschließlich Beispieldaten:", exact=True).count() == 1,
        )
        first_event = page.locator(".calendar-event").first
        first_event.click()
        acceptance.check("calendar detail opens", page.locator("[data-detail-content]").is_visible())
        page.locator("[data-reservation-submit]").click()
        acceptance.check(
            "calendar simulation remains explicitly local",
            "vorschau:" in page.locator("[data-reservation-status]").inner_text().lower()
            and "würde" in page.locator("[data-reservation-status]").inner_text().lower(),
        )

        page.goto(f"{base_url}/kontakt/", wait_until="networkidle")
        acceptance.check("contact route exposes approved mailbox", page.get_by_text("competencehub@donner-partner.de", exact=True).count() >= 1)
        acceptance.check("contact route explains mail-client handoff", page.get_by_text("Ihr E-Mail-Programm", exact=False).count() >= 1)
        acceptance.check("footer exposes central Impressum", page.locator('footer a[href="https://donner-partner.de/dp/impressum/"]').count() == 1)
        acceptance.check("footer exposes central Datenschutz", page.locator('footer a[href="https://donner-partner.de/dp/datenschutz/"]').count() == 1)
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
        acceptance.check("mobile navigation includes calendar preview", page.get_by_role("link", name="Kalender-Vorschau").count() >= 1)
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
        finally:
            browser.close()
    print(f"Messe browser acceptance complete: {acceptance.count} checks passed")


if __name__ == "__main__":
    main()
