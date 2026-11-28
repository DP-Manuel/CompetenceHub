"""Public visitor journeys against a local build or deployed Pages, without sending mail."""

import argparse
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import runpy
from shutil import copytree
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright


REFERENCE = runpy.run_path(str(Path(__file__).with_name("run-premium-journey-browser.py")))
WORKSHOPS = runpy.run_path(str(Path(__file__).with_name("run-workshop-offers-browser.py")))
HUB = runpy.run_path(str(Path(__file__).with_name("run-website-evolution-browser.py")))
VISIT, ZOOM = REFERENCE["visit"], REFERENCE["native_zoom"]
WIDTHS = (320, 390, 768, 1024, 1440, 1920)
SYNTHETIC_TEXT = "Lokaler Browser-Smoke & kein Versand"

@contextmanager
def preview(base, artifact):
    if not artifact:
        yield base.rstrip("/") + "/"
        return
    with TemporaryDirectory(prefix="competence-premium2-static-") as tmp:
        copytree(artifact, Path(tmp) / "CompetenceHub")
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                pass
        with ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=tmp)) as server:
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                yield f"http://127.0.0.1:{server.server_port}/CompetenceHub/"
            finally:
                server.shutdown()
                thread.join()


def journey(page, base, *, keyboard=False, touch=False):
    errors, requests = [], []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.on("request", lambda request: requests.append((request.method, request.url, request.post_data)))

    def activate(control):
        expect(control).to_be_visible()
        if keyboard:
            control.focus()
            expect(control).to_be_focused()
            control.press("Enter")
        elif touch:
            control.tap()
        else:
            control.click()

    VISIT(page, base, "")
    expect(page.locator("[data-hub-graph] [data-node]")).to_have_count(9)
    start = page.get_by_role("navigation", name="Direkte Einstiege")
    activate(start.get_by_role("link", name="Für Unternehmen"))
    page.wait_for_url(re.compile(r"/unternehmen/?#anlaesse$"))
    tab = page.get_by_role("tab", name="Führung", exact=True)
    expect(tab).to_have_attribute("aria-selected", "true")
    panel = page.get_by_role("tabpanel")
    rows = panel.locator("[data-direction]")
    expect(rows).to_have_count(3)
    expect(rows.first).to_have_attribute("data-direction", "business")
    expect(panel.get_by_role("link", name="Neuroleadership", exact=True)).to_be_visible()
    expect(panel.get_by_role("link", name="Herr Christian Galvano", exact=True)).to_be_visible()
    expect(page.locator("[data-solution-guide]")).to_have_count(0)
    activate(panel.locator("summary"))
    panel.get_by_label("Für wen?").select_option("team")
    expect(rows.first).to_have_attribute("data-direction", "workshop")
    expect(panel.get_by_role("status")).to_contain_text("Workshops")
    panel.get_by_label("Für wen?").select_option("")
    expect(rows.first).to_have_attribute("data-direction", "business")

    activate(page.get_by_role("tab", name="Recruiting und Personal"))
    expect(rows).to_have_count(2)
    expect(rows.first.get_by_role("link", name="Recruiting für Unternehmen", exact=True)).to_be_visible()
    activate(panel.locator("summary"))
    panel.get_by_label("Was möchten Sie erreichen?").select_option("auswahl")
    expect(rows.first).to_have_attribute("data-direction", "assessment")
    activate(rows.first.get_by_role("link", name="Assessment Center", exact=True))
    assessment = page.get_by_role("heading", name="Assessment Center für Unternehmen")
    expect(assessment).to_be_visible()
    activate(page.get_by_role("link", name="Assessment Center anfragen"))
    expect(page.locator("#contact-request-form").get_by_label("Thema")).to_have_value("Assessment Center")

    VISIT(page, base, "")
    activate(start.get_by_role("link", name="Für Privatpersonen"))
    page.wait_for_url(re.compile(r"/mindforge/?#privatpersonen$"))
    activate(page.get_by_role("link", name="Persönliche Beratung anfragen"))
    expect(page.locator("#contact-request-form").get_by_label("Thema")).to_have_value("Beratungsgespräche für Privatpersonen")

    VISIT(page, base, "coaches/#workshop-themen")
    activate(page.locator("#workshop-themen").get_by_role("link", name=re.compile("^Neuroleadership")))
    expect(page.get_by_role("heading", name="Darum geht es")).to_be_visible()
    expect(page.locator(".workshop-focus li")).to_have_count(3)
    expect(page.get_by_role("heading", name="Was Sie mitnehmen können")).to_be_visible()
    activate(page.get_by_role("link", name="Thema mit Frau Rappelt besprechen"))
    form = page.locator("#contact-request-form")
    expect(form.get_by_label("Thema")).to_have_value("Neuroleadership")
    expect(form.locator("[required]")).to_have_count(0)
    form.get_by_label("Anliegen").fill(SYNTHETIC_TEXT)
    activate(form.get_by_role("button", name="Entwurf vorbereiten"))
    expect(form.get_by_role("heading", name="Ihr Entwurf")).to_be_focused()
    expect(form.get_by_role("status")).to_have_text("Entwurf vorbereitet. Es wurde nichts gesendet.")
    mail = urlsplit(form.get_by_role("link", name="Im E-Mail-Programm öffnen").get_attribute("href"))
    assert (mail.scheme, mail.path) == ("mailto", "competencehub@donner-partner.de")
    assert parse_qs(mail.query) == {"subject": ["Anfrage: Neuroleadership"], "body": [SYNTHETIC_TEXT]}
    assert not any(method != "GET" or SYNTHETIC_TEXT in (payload or "") for method, _, payload in requests)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    assert not errors, errors


def fallback(browser, base):
    page = browser.new_page(viewport={"width": 390, "height": 900})
    page.add_init_script("""Object.defineProperty(navigator, 'clipboard', {
      configurable: true, value: {writeText: async () => { throw new Error('blocked'); }}
    });""")
    VISIT(page, base, "kontakt/?workshop=unerlaubt&thema=__proto__")
    form = page.locator("#contact-request-form")
    expect(form.get_by_label("Thema")).to_have_value("")
    expect(page.get_by_role("link", name="0172 6799972")).to_have_attribute("href", "tel:+491726799972")
    page.get_by_role("button", name="E-Mail-Adresse kopieren").click()
    address = page.get_by_role("textbox", name="E-Mail-Adresse zum manuellen Kopieren")
    expect(address).to_be_focused()
    assert address.evaluate("field => field.selectionEnd === field.value.length")
    form.get_by_label("Anliegen").fill("ä" * 900)
    form.get_by_role("button", name="Entwurf vorbereiten").click()
    expect(form.locator("[data-open-mail]")).to_be_hidden()
    form.get_by_role("button", name="Entwurf kopieren").click()
    draft = form.get_by_role("textbox", name="Text zum Übernehmen")
    expect(draft).to_be_focused()
    assert draft.evaluate("field => field.selectionEnd === field.value.length")
    page.close()
    page = browser.new_page(java_script_enabled=False, viewport={"width": 390, "height": 900})
    page.set_default_timeout(7000)
    VISIT(page, base, "unternehmen/#anlaesse")
    no_js_link = page.get_by_role("link", name="Recruiting und Personal", exact=True)
    expect(no_js_link).to_have_attribute("href", "#kompass-recruiting")
    no_js_link.focus()
    page.keyboard.press("Enter")
    expect(page).to_have_url(re.compile(r"#kompass-recruiting$"))
    expect(page.locator("#kompass-recruiting").get_by_role("link", name="Recruiting für Unternehmen", exact=True)).to_be_visible()
    VISIT(page, base, "kontakt/")
    expect(page.locator(".contact-direct-links").get_by_role("link", name="competencehub@donner-partner.de")).to_be_visible()
    expect(page.locator("#contact-request-form")).to_be_hidden()
    page.close()


def lab_samples(browser, base, output):
    collected = {}
    for route in ("unternehmen/", "kontakt/"):
        rows = []
        for _ in range(3):
            page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
            page.add_init_script("""window.lab = { lcp: null, cls: 0 };
              for (const type of ['largest-contentful-paint','layout-shift']) {
                new PerformanceObserver((list) => {
                  for (const e of list.getEntries()) {
                    if (type === 'largest-contentful-paint') window.lab.lcp = Math.round(e.startTime);
                    else if (!e.hadRecentInput) window.lab.cls += e.value;
                  }
                }).observe({type, buffered:true});
              }""")
            VISIT(page, base, route)
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(800)
            rows.append(page.evaluate("({ ...window.lab, htmlBytes: performance.getEntriesByType('navigation')[0].encodedBodySize })"))
            page.close()
        collected[route] = rows
    output.write_text(json.dumps(collected, indent=2) + "\n", encoding="ascii")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--base")
    target.add_argument("--artifact", type=Path)
    parser.add_argument("--browser", choices=("edge", "firefox"), default="edge")
    parser.add_argument("--screenshots", type=Path)
    parser.add_argument("--before", action="store_true")
    args = parser.parse_args()
    with preview(args.base, args.artifact) as base, sync_playwright() as play:
        edge = args.browser == "edge"
        browser = play.chromium.launch(channel="msedge") if edge else play.firefox.launch()
        if args.screenshots:
            args.screenshots.mkdir(parents=True, exist_ok=True)
            for width in (390, 1440):
                page = browser.new_page(viewport={"width": width, "height": 900}, reduced_motion="reduce")
                for route, name, selector in (
                    ("unternehmen/#anlaesse", "compass", "[data-company-compass]"),
                    ("kontakt/", "contact", ".contact-page"),
                    ("coaches/christian-galvano/angebote/neuroleadership/", "workshop", "main"),
                ):
                    VISIT(page, base, route)
                    dest = args.screenshots / f"{name}-{width}.png"
                    if name == "contact":
                        page.screenshot(path=dest, full_page=True, animations="disabled")
                    else:
                        page.locator(selector).screenshot(path=dest, animations="disabled")
                page.close()
            if edge:
                lab_samples(browser, base, args.screenshots / "lab-edge-desktop.json")
        if not args.before:
            for width in WIDTHS:
                touch = edge and width == 390
                page = browser.new_page(viewport={"width": width, "height": 900}, has_touch=touch, reduced_motion="reduce")
                page.set_default_timeout(7000)
                journey(page, base, keyboard=width == 320, touch=touch)
                page.close()
                print(f"{args.browser} {width}px: PASS", flush=True)
            fallback(browser, base)
            page = browser.new_page(reduced_motion="reduce")
            REFERENCE["verify_public"](page, base)
            if edge:
                WORKSHOPS["preview_journey"](page, base, None)
            page.close()
            if edge and args.screenshots:
                page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
                VISIT(page, base, "")
                HUB["drag_network"](page, base, args.screenshots, "premium2")
                page.close()
                print("Hub drag, lines and reset: PASS", flush=True)
            if not edge:
                ZOOM(play, base, verify=journey)
                print("Firefox native 200%: PASS", flush=True)
            print("Fallback, no-mail and publication boundaries: PASS", flush=True)
        browser.close()


if __name__ == "__main__":
    main()
