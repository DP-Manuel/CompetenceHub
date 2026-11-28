"""Synthetic public journeys with link, privacy and responsive checks."""

import argparse
from contextlib import closing
from pathlib import Path
import re
import sqlite3
import tempfile
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import expect, sync_playwright


WIDTHS = (320, 390, 768, 1024, 1440, 1920)


def visit(page, base, path):
    response = page.goto(urljoin(base, path), wait_until="load")
    assert response and (response.ok or response.status == 304), (path, response.status if response else None)
    expect(page.locator("h1")).to_have_count(1)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), path


def verify_public(page, base):
    response = page.request.get(base + "robots.txt")
    assert response.ok and "Disallow: /" in response.text()
    assert "<url>" not in page.request.get(base + "sitemap.xml").text()
    for slug in ("guelcan-elmas-brandes", "carolin-hupp", "elisabeth-schwabauer", "goran-celic",
                 "stefanie-becker", "wegner-ney", "susanne-klemm", "v2-demo-coach"):
        assert page.request.get(base + f"coaches/{slug}/").status == 404, slug
    for file in ("guelcan-elmas-brandes.png", "carolin-hupp.webp"):
        assert page.request.get(base + f"images/coaches/{file}").status == 404, file
    assert page.request.get(base + "images/room-experience/workshop-island-800.webp").status == 404
    for route in ("unternehmen/", "leistungen/", "kontakt/", "kalender/"):
        visit(page, base, route)
        assert not page.locator("[data-room-gallery], .service-room").count()
        canonical = page.locator("link[rel=canonical]").get_attribute("href")
        assert canonical == "https://competencehub.donner-partner.de/" + route
        expect(page.locator("meta[name=robots]")).to_have_attribute("content", "noindex, nofollow, noarchive")


def journey(page, base, *, shots=None, keyboard=False, touch=False):
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))

    def activate(control):
        if keyboard:
            control.press("Enter")
        elif touch:
            control.tap()
        else:
            control.click()

    visit(page, base, "")
    hero = page.get_by_role("navigation", name="Direkte Einstiege")
    expect(hero.get_by_role("link", name="Für Privatpersonen")).to_be_visible()
    expect(page.get_by_text("Expertise, die persönlich verbindet", exact=True)).to_be_visible()
    if shots:
        page.screenshot(path=shots / "home.png")
    activate(hero.get_by_role("link", name="Für Unternehmen"))
    page.wait_for_url(re.compile(r"/unternehmen/?#anlaesse$"))
    guide = page.locator("[data-solution-guide]")
    expect(guide).to_be_visible()
    tabs = page.get_by_role("tab")
    expect(tabs.first).to_have_accessible_name("Führung")
    expect(tabs.first).to_have_attribute("aria-selected", "true")
    form = guide.get_by_role("form")
    audience = form.get_by_label("Für wen?")
    goal = form.get_by_label("Was möchten Sie erreichen?")
    audience.select_option("einzel")
    goal.select_option("entwickeln")
    activate(form.get_by_role("button", name="Passende Wege zeigen"))
    result = guide.get_by_role("region", name="Diese Wege könnten zu Ihrem Anliegen passen.")
    expect(result.get_by_role("heading")).to_be_focused()
    links = result.locator("ol").get_by_role("link")
    expect(links).to_have_count(3)
    expect(links.first).to_have_text("Businesscoaching für Unternehmen")
    expect(links.first).to_have_css("text-decoration-line", "underline")
    assert urlsplit(page.url).query == ""
    if shots:
        page.screenshot(path=shots / "finder.png")
    audience.select_option("team")
    expect(links.first).to_have_text("Workshops & Vorträge")

    activate(page.get_by_role("tab", name="Recruiting und Personal"))
    audience.select_option("organisation")
    goal.select_option("auswahl")
    expect(links).to_have_count(2)
    expect(links.first).to_have_text("Assessment Center")
    expect(links.last).to_have_text("Recruiting für Unternehmen")
    activate(links.first)
    expect(page.get_by_role("heading", name="Assessment Center für Unternehmen")).to_be_visible()
    activate(result.get_by_role("link", name="Anliegen mit Frau Rappelt besprechen"))
    page.wait_for_url(re.compile(r"/kontakt/?\?thema=assessment$"))
    draft = page.locator("#contact-request-form")
    expect(draft).to_be_visible()
    expect(draft).to_have_attribute("method", "dialog")
    expect(draft.get_by_label("Thema")).to_have_value("Assessment Center")
    expect(draft.get_by_role("button", name="E-Mail-Entwurf öffnen")).to_be_enabled()
    expect(page.get_by_role("link", name="0172 6799972")).to_have_attribute("href", "tel:+491726799972")

    visit(page, base, "")
    activate(page.get_by_role("navigation", name="Direkte Einstiege").get_by_role("link", name="Für Privatpersonen"))
    page.wait_for_url(re.compile(r"/mindforge/?#privatpersonen$"))
    activate(page.get_by_role("link", name="Persönliche Beratung anfragen"))
    expect(page.locator("#contact-request-form").get_by_label("Thema")).to_have_value("Beratungsgespräche für Privatpersonen")
    if shots:
        page.screenshot(path=shots / "kontakt.png", full_page=True)

    visit(page, base, "kalender/")
    expect(page.get_by_text("Derzeit sind keine Termine veröffentlicht.", exact=True)).to_be_visible()
    activate(page.get_by_role("link", name="Veranstaltung anfragen"))
    expect(page.locator("#contact-request-form").get_by_label("Thema")).to_have_value("Workshop oder Vortrag")
    visit(page, base, "leistungen/#gruppenformate")
    activate(page.get_by_role("link", name="Workshop-Themen und Coaches ansehen"))
    page.wait_for_url(re.compile(r"/coaches/?#workshop-themen$"))
    activate(page.locator("#workshop-themen").get_by_role("link", name=re.compile("^Neuroleadership")))
    expect(page.get_by_role("heading", name="Neuroleadership", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Thema per E-Mail anfragen")).to_have_attribute("href", re.compile(r"^mailto:"))
    assert not errors, errors


def no_javascript(browser, base):
    page = browser.new_page(java_script_enabled=False, viewport={"width": 390, "height": 900})
    visit(page, base, "unternehmen/")
    expect(page.locator("[data-solution-guide]")).to_be_hidden()
    expect(page.locator(".compass-option").first).to_be_visible()
    expect(page.get_by_role("link", name="Businesscoaching für Unternehmen").first).to_be_visible()
    visit(page, base, "kontakt/")
    expect(page.locator("#contact-request-form")).to_be_hidden()
    expect(page.locator(".contact-direct-links").get_by_role("link", name="competencehub@donner-partner.de")).to_be_visible()
    page.close()


def native_zoom(playwright, base, verify=journey):
    with tempfile.TemporaryDirectory(prefix="competence-premium-zoom-") as tmp:
        context = playwright.firefox.launch_persistent_context(tmp, no_viewport=True)
        old_ratio = context.pages[0].evaluate("devicePixelRatio")
        context.close()
        with closing(sqlite3.connect(Path(tmp) / "content-prefs.sqlite")) as db:
            db.execute("INSERT INTO settings(name) VALUES ('browser.content.full-zoom')")
            setting = db.execute("SELECT id FROM settings WHERE name = 'browser.content.full-zoom'").fetchone()[0]
            db.execute("INSERT INTO prefs(groupID,settingID,value,timestamp) VALUES (NULL,?,?,0)", (setting, 2))
            db.commit()
        context = playwright.firefox.launch_persistent_context(tmp, no_viewport=True, reduced_motion="reduce")
        try:
            page = context.pages[0]
            visit(page, base, "")
            assert 1.95 < page.evaluate("devicePixelRatio") / old_ratio < 2.05
            verify(page, base, keyboard=True)
        finally:
            context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--screenshots", type=Path, required=True)
    parser.add_argument("--browser", choices=("edge", "firefox"), required=True)
    args = parser.parse_args()
    base = args.base.rstrip("/") + "/"
    with sync_playwright() as p:
        edge = args.browser == "edge"
        browser = p.chromium.launch(channel="msedge") if edge else p.firefox.launch()
        for width in WIDTHS:
            touch = edge and width == 390
            page = browser.new_page(viewport={"width": width, "height": 900}, has_touch=touch, reduced_motion="reduce")
            page.set_default_timeout(7000)
            shots = args.screenshots / args.browser / str(width) if width in (390, 1440) else None
            if shots:
                shots.mkdir(parents=True, exist_ok=True)
            journey(page, base, touch=touch, keyboard=width == 320, shots=shots)
            if width == 1440:
                verify_public(page, base)
            page.close()
            print(f"{args.browser} {width}px: PASS", flush=True)
        no_javascript(browser, base)
        browser.close()
        print(f"{args.browser} without JS: PASS", flush=True)
        if not edge:
            native_zoom(p, base)
            print("Firefox native 200%: PASS", flush=True)


if __name__ == "__main__":
    main()
