"""Exercise the actual Pages-compatible build or the deployed Pages URL."""
import argparse
from contextlib import closing
from pathlib import Path
import re
import sqlite3
import tempfile
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright


VISIBLE = ("christian-galvano", "manuela-rodriguez")
DEFERRED = (
    "elisabeth-schwabauer", "goran-celic", "guelcan-elmas-brandes",
    "stefanie-becker", "wegner-ney", "susanne-klemm", "carolin-hupp",
    *(f"demoprofil-{number:02}" for number in range(1, 7)),
)
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)


def fit(page):
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"), page.url


def hub_geometry(page):
    expect(page.locator("[data-hub-graph] [data-node]")).to_have_count(9)
    assert page.evaluate("""() => {
      const hero = document.querySelector('.living-hero--homepage');
      const nodes = [...hero.querySelectorAll('[data-hub-graph] [data-node]')];
      const copy = [...hero.querySelectorAll('.living-hero__homepage-intro, .living-hero__actions a')];
      const circles = getComputedStyle(hero.querySelector('.hub-graph__connections')).display !== 'none';
      const box = node => node.getBoundingClientRect();
      const overlaps = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1 &&
        Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1;
      const errors = [];
      for (const [i, node] of nodes.entries()) {
        const a = box(node), id = node.dataset.node;
        if (a.width < 44 || a.height < 44 || a.left < -1 ||
          a.right > document.documentElement.clientWidth + 1) errors.push([id, 'target']);
        for (const other of [...nodes.slice(i + 1), ...copy]) {
          const b = box(other);
          const collision = circles && other.dataset.node
            ? Math.hypot(a.x + a.width/2 - b.x - b.width/2, a.y + a.height/2 - b.y - b.height/2) + 1 < (a.width+b.width)/2
            : overlaps(a,b);
          if (collision) errors.push([id, other.dataset.node ?? other.textContent.trim()]);
        }
        const texts = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
        for (let text; (text = texts.nextNode());) {
          if (!text.data.trim()) continue;
          const range = document.createRange();
          range.selectNodeContents(text);
          if (text.data.trim() === 'Competence' && range.getClientRects().length !== 1)
            errors.push([id, 'brand broken across lines']);
          for (const rect of range.getClientRects()) {
            if (rect.left < a.left - 1 || rect.right > a.right + 1 ||
                rect.top < a.top - 1 || rect.bottom > a.bottom + 1) errors.push([id, text.data.trim()]);
          }
        }
      }
      if (errors.length) throw Error(JSON.stringify(errors));
      return true;
    }""")


def enter(page, base, route="", *, bust=""):
    response = page.goto(base + route + ("?review=" + bust if bust else ""), wait_until="load")
    assert response and response.status == 200, page.url
    expect(page.locator("h1")).to_have_count(1)
    expect(page.locator("main")).to_have_count(1)
    expect(page.locator("[data-portal-login]")).to_have_count(0)
    expect(page.locator('meta[name="robots"]')).to_have_attribute("content", "noindex, nofollow, noarchive")
    fit(page)


def home(page, base, bust=""):
    enter(page, base, bust=bust)
    assert page.locator("[data-spotlight-coach]").evaluate_all(
        "(nodes) => nodes.map(node => node.dataset.spotlightCoach)"
    ) == list(VISIBLE)
    hub_geometry(page)
    audience = page.get_by_role("navigation", name="Direkte Einstiege")
    expect(audience.get_by_role("link", name="Für Unternehmen")).to_have_attribute(
        "href", re.compile(r"/CompetenceHub/unternehmen/?(?:#anlaesse)?$")
    )
    expect(audience.get_by_role("link", name="Für Privatpersonen")).to_have_attribute("href", "/CompetenceHub/mindforge#privatpersonen")
    portrait_sizes = []
    for slug in VISIBLE:
        card = page.locator(f'[data-spotlight-coach="{slug}"]')
        expect(card.locator("h3 a")).to_have_attribute("href", f"/CompetenceHub/coaches/{slug}")
        card.locator("img").scroll_into_view_if_needed()
        expect(card.locator("img")).to_have_js_property("complete", True)
        assert card.locator("img").evaluate("(img) => img.naturalWidth > 0")
        box = card.locator(".portrait-story__image").bounding_box()
        portrait_sizes.append((box["width"], box["height"]))
    assert all(abs(a - b) < 0.1 for a, b in zip(*portrait_sizes)), portrait_sizes
    page.evaluate("window.scrollTo(0, 0)")
    expect(page.locator("#anfrage a.button")).to_have_attribute("href", "/CompetenceHub/kontakt")


def profile(page, base, slug, bust=""):
    enter(page, base, f"coaches/{slug}/", bust=bust)
    expect(page.locator(f'main[data-coach-profile="{slug}"]')).to_be_visible()
    image = page.locator("main figure img").first
    expect(image).to_have_js_property("complete", True)
    assert image.evaluate("(img) => img.naturalWidth > 0 && Boolean(img.alt)")
    expect(page.locator("#angebote")).to_be_visible()
    expect(page.locator("#aktuelle-termine")).to_contain_text("keine Termine veröffentlicht")
    expect(page.locator("main a[href^='mailto:']").first).to_be_visible()
    topic = page.locator("#angebote details > summary").first
    topic.focus()
    topic.press("Enter")
    expect(topic.locator("xpath=..")).to_have_attribute("open", "")
    fit(page)


def drag_network(page, base, folder, prefix):
    graph = page.locator(".hub-graph--homepage")
    graph.scroll_into_view_if_needed()
    expect(graph).to_have_attribute("data-hub-draggable", "")
    node = graph.locator('[data-node="unternehmen"]')
    reset = page.get_by_role("button", name="Ansicht zurücksetzen")
    starting_path = graph.locator('[data-from="core"][data-to="unternehmen"]').get_attribute("d")
    start = page.url

    def center():
        rect = node.bounding_box()
        return rect["x"] + rect["width"] / 2, rect["y"] + rect["height"] / 2

    def geometry():
        graph.evaluate("""(graph) => {
          const svg = graph.querySelector('svg.hub-graph__connections');
          const bounds = graph.getBoundingClientRect();
          const points = new Map([...graph.querySelectorAll('[data-node]')].map((node) => {
            const rect = node.getBoundingClientRect();
            return [node.dataset.node, {x:rect.x + rect.width/2, y:rect.y + rect.height/2, r:rect.width/2}];
          }));
          for (const [id, p] of points) {
            if (p.x - p.r < bounds.left || p.x + p.r > bounds.right ||
                p.y - p.r < bounds.top || p.y + p.r > bounds.bottom) throw Error('outside: ' + id);
            for (const [other, q] of points) {
              if (other !== id && Math.hypot(p.x-q.x, p.y-q.y) < p.r+q.r) throw Error(id+' overlaps '+other);
            }
          }
          for (const path of svg.querySelectorAll('[data-edge]')) {
            for (const [id, distance] of [[path.dataset.from,0],[path.dataset.to,path.getTotalLength()]]) {
              const actual = path.getPointAtLength(distance).matrixTransform(svg.getScreenCTM());
              const target = points.get(id);
              if (Math.hypot(actual.x-target.x, actual.y-target.y)>1.5) throw Error('edge detached from '+id);
            }
          }
        }""")

    geometry()
    ox, oy = center()
    page.mouse.move(ox, oy)
    page.mouse.down()
    page.mouse.move(ox + 38, oy - 51, steps=6)
    expect(graph).to_have_attribute("data-dragging", "unternehmen")
    expect(graph.locator('[data-from="core"][data-to="unternehmen"]')).not_to_have_attribute("d", starting_path)
    geometry()
    assert node.evaluate("(node) => getComputedStyle(node).cursor") == "grabbing"
    if page.viewport_size["width"] == 1440:
        graph.screenshot(path=folder / f"{prefix}-hub-drag-1440.png", animations="disabled")
    page.mouse.up()
    assert page.url == start
    expect(reset).to_have_attribute("aria-disabled", "false")
    assert abs(center()[0] - ox) > 20
    geometry()

    # A coarse event which ends outside the canvas must stay captured and not navigate.
    x, y = center()
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(1, y, steps=1)
    page.mouse.up()
    assert page.url == start
    assert center()[0] < x - 10
    geometry()

    width = page.viewport_size["width"]
    x, y = center()
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(width - 2, y, steps=1)
    page.mouse.up()
    assert page.url == start
    assert center()[0] < width / 2
    geometry()

    page.set_viewport_size({"width": 768, "height": 900})
    expect(reset).to_be_hidden()
    hub_geometry(page)
    page.set_viewport_size({"width": width, "height": 900})
    expect(reset).to_be_visible()
    geometry()
    reset.focus()
    reset.press("Enter")
    expect(reset).to_have_attribute("aria-disabled", "true")
    expect(reset).to_be_focused()
    expect(graph.locator('[data-from="core"][data-to="unternehmen"]')).to_have_attribute("d", starting_path)
    graph.scroll_into_view_if_needed()
    x, y = center()
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 3, y)
    page.mouse.up()
    expect(page).to_have_url(re.compile(re.escape(base + "unternehmen") + "/?$"))


def keyboard_and_hover(page, base, width):
    graph = page.locator(".hub-graph--homepage")
    core = graph.locator('[data-node="core"]')
    first = graph.locator(".hub-graph__node").first
    core.focus()
    page.keyboard.press("Tab")
    expect(first).to_be_focused()
    assert first.evaluate("""element => {
      const style = getComputedStyle(element);
      return element.matches(':focus-visible') && style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) >= 2;
    }"""), "hub link has no visible keyboard focus"
    expect(graph).to_have_attribute("data-active", "unternehmen")
    if width == 1440:
        workshop = graph.locator('[data-node="gruppenformate"]')
        workshop.hover()
        expect(graph).to_have_attribute("data-active", "gruppenformate")
        expect(graph.locator("path.is-active").first).to_be_visible()
        page.mouse.move(0, 0)
    page.keyboard.press("Enter")
    expect(page).to_have_url(re.compile(re.escape(base + "unternehmen") + "/?$"))
    home(page, base)
    expect(page.locator(".hub-journey--compact [data-journey-step]")).to_have_count(4)


def navigation(page, base, folder, prefix, width):
    enter(page, base, "leistungen/")
    expect(page.locator("#finder-coach option")).to_have_count(3)
    expect(page.locator("[data-finder-entry]:visible")).to_have_count(4)
    page.locator("#finder-query").fill("Rodriguez")
    expect(page.locator("[data-finder-entry]:visible")).to_have_count(1)
    summary = page.locator("[data-finder-entry]:visible summary")
    summary.focus()
    page.keyboard.press("Enter")
    expect(page.locator("[data-finder-profile]:visible")).to_have_attribute(
        "href", "/CompetenceHub/coaches/manuela-rodriguez#angebote"
    )
    request = page.locator("[data-finder-entry]:visible a[href^='mailto:']").first
    assert "Rodríguez" in parse_qs(urlsplit(request.get_attribute("href")).query)["subject"][0]
    page.locator("#finder-query").fill("zzzznotfound")
    expect(page.locator("[data-finder-empty]")).to_be_visible()
    page.locator(".finder-reset").click()
    expect(page.locator("[data-finder-entry]:visible")).to_have_count(4)
    page.screenshot(path=folder / f"{prefix}-leistungen-{width}.png", full_page=True, animations="disabled")
    page.locator("#finder-query").fill("Rhetorik & Vertrieb")
    expect(page.locator("[data-finder-entry]:visible")).to_have_count(0)
    expect(page.locator("[data-finder-empty] a[href='/CompetenceHub/kontakt']")).to_be_visible()
    for anchor in ("recruiting", "personalentwicklung", "gruppenformate"):
        expect(page.locator("#" + anchor)).to_be_visible()
    enter(page, base, "coaches/")
    expect(page.locator("[data-preview-coach]:visible")).to_have_count(2)
    page.locator("#preview-coach-search").fill("Galvano")
    expect(page.locator("[data-preview-coach]:visible")).to_have_count(1)
    page.locator("#preview-coach-search").fill("Wegner")
    expect(page.locator("[data-preview-empty]")).to_be_visible()
    if page.viewport_size["width"] < 768:
        menu = page.locator("details.nav-menu > summary")
        menu.focus()
        page.keyboard.press("Enter")
        expect(page.get_by_role("navigation", name="Mobile Hauptnavigation")).to_be_visible()
        expect(page.get_by_role("navigation", name="Mobile Hauptnavigation").get_by_text("Coaches", exact=True)).to_have_attribute("aria-current", "page")
        page.keyboard.press("Enter")
    else:
        expect(page.get_by_role("navigation", name="Hauptnavigation", exact=True).get_by_text("Coaches", exact=True)).to_have_attribute("aria-current", "page")
    for route in ("unternehmen/", "mindforge/", "kontakt/"):
        enter(page, base, route)
        if route == "unternehmen/":
            page.locator("img").evaluate_all("(imgs) => imgs.forEach((img) => img.loading = 'eager')")
            page.wait_for_function("Array.from(document.images).every((img) => img.complete)")
            page.screenshot(path=folder / f"{prefix}-unternehmen-{width}.png", full_page=True, animations="disabled")
    for scheme in ("mailto", "tel"):
        expect(page.locator(f'.contact-direct-links a[href^="{scheme}:"]').first).to_be_visible()
    for label, target in (
        ("Impressum", "https://donner-partner.de/dp/impressum/"),
        ("Datenschutz", "https://donner-partner.de/dp/datenschutz/"),
    ):
        expect(page.get_by_role("navigation", name="Footer").get_by_role("link", name=label)).to_have_attribute("href", target)


def public_artifact(page, base, bust):
    for slug in DEFERRED:
        response = page.request.get(f"{base}coaches/{slug}/?review={bust}")
        assert response.status == 404, (slug, response.status)
    for file in (
        "elisabeth-schwabauer.webp", "goran-celic.png", "guelcan-elmas-brandes.png",
        "stefanie-becker.webp", "wegner-ney.jpg", "susanne-klemm.webp",
    ):
        assert page.request.get(f"{base}images/coaches/{file}?review={bust}").status == 404, file
    assert "<url>" not in page.request.get(base + "sitemap.xml").text()
    assert "Disallow: /" in page.request.get(base + "robots.txt").text()
    print("Direct routes, portrait assets, sitemap and robots: PASS")


def native_zoom(playwright, base, folder, prefix):
    with tempfile.TemporaryDirectory(prefix="competence-zoom-") as temp:
        context = playwright.firefox.launch_persistent_context(temp, no_viewport=True, reduced_motion="reduce")
        ratio = context.pages[0].evaluate("devicePixelRatio")
        context.close()
        with closing(sqlite3.connect(Path(temp) / "content-prefs.sqlite")) as db:
            db.execute("INSERT INTO settings(name) VALUES (?)", ("browser.content.full-zoom",))
            setting = db.execute("SELECT id FROM settings WHERE name = ?", ("browser.content.full-zoom",)).fetchone()[0]
            db.execute("INSERT INTO prefs(groupID,settingID,value,timestamp) VALUES (NULL,?,?,0)", (setting, 2.0))
            db.commit()
        context = playwright.firefox.launch_persistent_context(temp, no_viewport=True, reduced_motion="reduce")
        try:
            page = context.pages[0]
            home(page, base)
            assert 1.95 < page.evaluate("devicePixelRatio") / ratio < 2.05, "native Firefox zoom did not apply"
            page.screenshot(path=folder / f"{prefix}-home-native-200.png", full_page=True, animations="disabled")
            for slug in VISIBLE:
                profile(page, base, slug)
            enter(page, base, "leistungen/")
        finally:
            context.close()
    print("Native Firefox 200% zoom: PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--screenshots", required=True, type=Path)
    parser.add_argument("--prefix", default="after")
    parser.add_argument("--bust", default="website-evolution")
    parser.add_argument("--browser", choices=("firefox", "edge"), default="firefox")
    args = parser.parse_args()
    base = args.base.rstrip("/") + "/"
    args.screenshots.mkdir(exist_ok=True, parents=True)
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch() if args.browser == "firefox" else playwright.chromium.launch(channel="msedge")
        for width in WIDTHS:
            context = browser.new_context(viewport={"width": width, "height": 900}, reduced_motion="reduce")
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("requestfailed", lambda request: errors.append(f"{request.url}: {request.failure}"))
            page.on("response", lambda response: errors.append(f"{response.url}: HTTP {response.status}")
                    if response.status >= 400 else None)
            home(page, base, args.bust)
            assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
            if width in (390, 1440):
                page.screenshot(path=args.screenshots / f"{args.prefix}-home-{width}.png", full_page=True, animations="disabled")
                keyboard_and_hover(page, base, width)
            if width in (1024, 1440, 1920):
                drag_network(page, base, args.screenshots, args.prefix)
            else:
                expect(page.locator("[data-hub-tools]")).to_be_hidden()
            for slug in VISIBLE:
                profile(page, base, slug, args.bust)
                if width in (390, 1440):
                    label = "galvano" if slug.startswith("christian") else "rodriguez"
                    page.screenshot(path=args.screenshots / f"{args.prefix}-{label}-{width}.png", full_page=True, animations="disabled")
            if width in (390, 1440):
                navigation(page, base, args.screenshots, args.prefix, width)
            if width == 1440:
                public_artifact(page, base, args.bust)
            context.close()
            print(f"{args.browser} {width}px: PASS")
        if args.browser == "edge":
            with browser.new_context(viewport={"width": 768, "height": 900}, has_touch=True, is_mobile=True) as context:
                touch = context.new_page()
                home(touch, base, args.bust)
                expect(touch.locator("[data-hub-tools]")).to_be_hidden()
                touch.locator('[data-node="unternehmen"]').tap()
                expect(touch).to_have_url(re.compile(re.escape(base + "unternehmen") + "/?$"))
            print("Touch navigation: PASS")
        browser.close()
        if args.browser == "firefox":
            native_zoom(playwright, base, args.screenshots, args.prefix)
    failures = [error for error in errors if "NS_BINDING_ABORTED" not in error]
    assert not failures, failures
    print("WEBSITE_EVOLUTION_BROWSER=PASS")


if __name__ == "__main__":
    main()
