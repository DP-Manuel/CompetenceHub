from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
NODE = Path(os.environ.get("WEBSITE_NODE", str(ROOT.parents[1] / "tools/node-v22.16.0-win-x64/node.exe")))
EVIDENCE = ROOT / "release-artifacts/preview-qa"
RESTORED = ("carolin-hupp", "elisabeth-schwabauer", "goran-celic",
            "guelcan-elmas-brandes", "stefanie-becker", "wegner-ney")
count = 0


def check(label, condition):
    global count
    if not condition:
        raise AssertionError(label)
    count += 1


@contextmanager
def static_server(mode="preview"):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    env = os.environ.copy()
    env.update(WEBSITE_ENV=mode, PORT=str(port), BASE_PATH="/CompetenceHub" if mode == "preview" else "/")
    process = subprocess.Popen(
        [str(NODE), "scripts/serve-dist.mjs"], cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    origin = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("Preview server stopped")
            try:
                urllib.request.urlopen(origin + ("/CompetenceHub/" if mode == "preview" else "/"), timeout=0.3).close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("Preview server did not start")
        yield origin
    finally:
        process.terminate()
        process.wait(timeout=10)


def overflow(page):
    return page.evaluate("document.documentElement.scrollWidth > innerWidth + 1")


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    routes = []
    for file in sorted((ROOT / "dist-preview").rglob("*.html")):
        path = file.relative_to(ROOT / "dist-preview").as_posix()
        routes.append("/" if path == "index.html" else "/" + path.removesuffix("index.html"))
    with static_server() as origin, sync_playwright() as playwright:
        base = origin + "/CompetenceHub"
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        external = []
        writes = []
        failures = []
        console_errors = []
        screenshots = []
        try:
            for name, width, height, scale in (
                ("desktop", 1440, 1000, 1), ("mobile-390", 390, 844, 1),
                ("200-percent-reflow", 640, 720, 2),
            ):
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=scale, reduced_motion="reduce",
                )

                def guard(route):
                    request = route.request
                    if request.method not in ("GET", "HEAD"):
                        writes.append(request.method + " " + request.url)
                        route.abort()
                    elif urlsplit(request.url).netloc != urlsplit(origin).netloc:
                        external.append(request.url)
                        route.abort()
                    else:
                        route.continue_()

                context.route("**/*", guard)
                page = context.new_page()
                page.on("pageerror", lambda error: console_errors.append(str(error)))
                page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
                page.on("response", lambda response: failures.append(response.url) if response.status >= 400 else None)
                for route in routes:
                    response = page.goto(base + route, wait_until="networkidle")
                    check(f"{name} {route} 200", response.status == 200)
                    check(f"{name} {route} H1", page.locator("h1").count() == 1)
                    check(f"{name} {route} no overflow", not overflow(page))
                    check(f"{name} {route} noindex", page.locator('meta[name="robots"]').get_attribute("content") == "noindex, nofollow, noarchive")
                    check(f"{name} {route} label", page.locator(".review-banner").inner_text() == "Entwicklungs-/Vorschauversion")
                    check(f"{name} {route} no provisional spelling", "Schabbauer" not in page.locator("body").inner_text())
                    check(f"{name} {route} unique IDs", page.evaluate(
                        "() => { const ids = [...document.querySelectorAll('[id]')].map(n => n.id); return ids.length === new Set(ids).size; }"))
                    check(f"{name} {route} images load", page.evaluate("""async () => {
                        const images = [...document.images]; images.forEach(i => i.loading = 'eager');
                        await Promise.all(images.map(i => i.decode().catch(() => null)));
                        return images.every(i => i.naturalWidth > 0 && i.hasAttribute('alt'));
                    }"""))
                    canonical = page.locator('link[rel="canonical"]')
                    if route.startswith(tuple("/coaches/" + slug + "/" for slug in RESTORED)) or route == "/404.html":
                        check(f"{name} {route} no fake canonical", canonical.count() == 0)
                    else:
                        check(f"{name} {route} production canonical", canonical.count() == 1
                              and canonical.get_attribute("href") == "https://competencehub.donner-partner.de" + route)

                page.goto(base + "/coaches/", wait_until="networkidle")
                check(f"{name} eight coaches", page.locator("[data-preview-coach]").count() == 8)
                check(f"{name} progressive disclosure initial", not page.locator("#preview-categories").is_visible()
                      and not page.locator("#preview-topic-options").is_visible())
                page.locator("[data-hub-toggle]").click()
                check(f"{name} three category satellites", page.locator("[data-category]:visible").count() == 3)
                check(f"{name} no Messe privacy remnants", "Demoprofil" not in page.locator("main").inner_text()
                      and "Transparenter Messestand" not in page.locator("main").inner_text())
                category = page.locator('[data-category="personalentwicklung"]')
                category.focus()
                page.keyboard.press("Tab")
                page.keyboard.press("Shift+Tab")
                check(f"{name} visible keyboard focus", category.evaluate(
                    "e => e.matches(':focus-visible') && getComputedStyle(e).outlineStyle !== 'none'"))
                page.keyboard.press("Enter")
                check(f"{name} keyboard category selection", category.get_attribute("aria-pressed") == "true")
                health = page.locator('[data-topic="gesundheit-praevention"]')
                check(f"{name} health in personnel", health.is_visible())
                health.focus()
                page.keyboard.press("Space")
                first = page.locator("[data-preview-coach]:visible h2").all_text_contents()
                check(f"{name} sourced health coaches", first == [
                    "Herr Christian Galvano", "Frau Elisabeth Schwabauer",
                    "Frau Carolin Hupp", "Frau Gülcan Elmas-Brandes",
                ])
                page.locator('[data-category="persoenlichkeitsentwicklung"]').click()
                check(f"{name} health in personality", health.is_visible())
                health.click()
                check(f"{name} same canonical topic across categories", first == page.locator("[data-preview-coach]:visible h2").all_text_contents())
                check(f"{name} one canonical topic DOM node", page.locator('[data-topic="gesundheit-praevention"]').count() == 1)
                page.reload(wait_until="networkidle")
                check(f"{name} hash restored", health.get_attribute("aria-pressed") == "true")
                page.locator('[data-category="karrierecoaching"]').click()
                check(f"{name} irrelevant health hidden", not health.is_visible())
                page.locator('[data-hub-toggle]').click()
                check(f"{name} All computed", page.locator("[data-preview-coach]:visible").count() == 8)
                unassigned = page.locator("[data-preview-coach]").first
                original_topics = unassigned.get_attribute("data-topics")
                unassigned.evaluate("e => e.dataset.topics = ''")
                page.locator('[data-hub-toggle]').click()
                check(f"{name} All includes unassigned Coach", page.locator("[data-preview-coach]:visible").count() == 8)
                unassigned.evaluate("(e, value) => e.dataset.topics = value", original_topics)
                if not page.locator("#preview-categories").is_visible():
                    page.locator('[data-hub-toggle]').click()
                page.locator('[data-category="personalentwicklung"]').click()
                page.locator('[data-topic="mediation"]').click()
                check(f"{name} Mediation qualification empty", page.locator("[data-preview-coach]:visible").count() == 0
                      and page.locator("[data-preview-empty]").is_visible())
                check(f"{name} live status", "0 passende" in page.locator('[role="status"][data-preview-status]').inner_text())
                page.locator('[data-hub-toggle]').click()
                page.locator("#preview-topics-title").scroll_into_view_if_needed()
                path = EVIDENCE / f"directory-{name}.png"
                page.screenshot(path=str(path))
                screenshots.append(path.name)

                links = page.locator("[data-preview-coach] a").evaluate_all("nodes => nodes.map(n => n.href)")
                for link in links:
                    check(f"{name} profile prefix", link.startswith(base + "/coaches/"))
                    check(f"{name} profile link resolves", context.request.get(link).status == 200)
                carolin = page.locator('[data-preview-coach]').filter(has=page.get_by_role("heading", name="Frau Carolin Hupp", exact=True))
                check(f"{name} Carolin has no portrait", carolin.locator("img").count() == 0)

                page.goto(base + "/coaches/elisabeth-schwabauer/", wait_until="networkidle")
                check(f"{name} Elisabeth spelling", page.locator("h1").inner_text() == "Frau Elisabeth Schwabauer")
                check(f"{name} offer groups", page.locator(".offer-group").count() == 4)
                check(f"{name} 17 exact supplied titles", page.locator(".offer-group li").count() == 17)
                check(f"{name} psychotherapy boundary", "Über den Competence Hub wird derzeit keine Psychotherapie angeboten."
                      in page.locator(".elisabeth-offers").inner_text())
                summary = page.locator(".offer-group summary").first
                summary.focus()
                page.keyboard.press("Enter")
                check(f"{name} offer disclosure keyboard", page.locator(".offer-group").first.get_attribute("open") is None)
                page.keyboard.press("Enter")
                page.locator("#elisabeth-offers-title").scroll_into_view_if_needed()
                path = EVIDENCE / f"offers-{name}.png"
                page.screenshot(path=str(path))
                screenshots.append(path.name)

                page.goto(base + "/coaches/manuela-rodriguez/", wait_until="networkidle")
                advisory = page.get_by_role("link", name="D+P AI Advisory ansehen")
                check(f"{name} Advisory target", advisory.get_attribute("href") == "https://advisory.donner-partner.de/")
                check(f"{name} old Advisory absent", "firmenseminare" not in page.content())
                advisory.scroll_into_view_if_needed()
                path = EVIDENCE / f"advisory-{name}.png"
                page.screenshot(path=str(path))
                screenshots.append(path.name)

                for calendar in ("/kalender/", "/prototyp/kalender/"):
                    page.goto(base + calendar, wait_until="networkidle")
                    check(f"{name} {calendar} synthetic", "Ausschließlich Beispieldaten:" in page.locator("main").inner_text())
                    seen = 0
                    while True:
                        events = page.locator(".calendar-event")
                        for index in range(events.count()):
                            events.nth(index).click()
                            href = page.locator("[data-detail-coach]").get_attribute("href")
                            check(f"{name} calendar generated href prefix", href.startswith("/CompetenceHub/coaches#thema-"))
                            check(f"{name} calendar generated href resolves", context.request.get(origin + href).status == 200)
                            check(f"{name} calendar no real availability", "Beispielzuordnung" in page.locator("[data-detail-coach]").inner_text())
                            if page.locator("[data-reservation-submit]").is_enabled():
                                page.locator("[data-reservation-submit]").click()
                                check(f"{name} calendar nonbinding", "würde" in page.locator("[data-reservation-status]").inner_text())
                            seen += 1
                        next_month = page.locator("[data-next-month]")
                        if next_month.is_disabled():
                            break
                        next_month.click()
                    check(f"{name} {calendar} all synthetic events visited", seen == 7)

                page.goto(base + "/", wait_until="networkidle")
                rail_links = page.locator(".coach-preview__card").evaluate_all("nodes => nodes.map(n => n.href)")
                check(f"{name} eight home profiles", len(rail_links) == 8)
                for href in rail_links:
                    check(f"{name} rail link resolves", href.startswith(base + "/coaches/") and context.request.get(href).status == 200)
                context.close()

            check("no browser errors", not console_errors)
            check("no broken resource responses", not failures)
            check("no off-origin network / analytics", not external)
            check("no write requests", not writes)
            report = {"checks": count, "browser": "Microsoft Edge " + browser.version,
                      "routes": len(routes), "screenshots": screenshots,
                      "externalRequests": external, "writeRequests": writes,
                      "resourceFailures": failures, "consoleErrors": console_errors,
                      "reflow": "640 CSS px at device scale 2, equivalent to 1280px at 200 percent"}
            (EVIDENCE / "browser-report.json").write_text(json.dumps(report, indent=2), encoding="utf8")
            print(json.dumps(report, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
