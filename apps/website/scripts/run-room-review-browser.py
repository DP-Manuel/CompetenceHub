"""Exercise approved venue journeys in the static artifact and on Pages."""

import argparse
from contextlib import closing
from pathlib import Path
import json
import re
import runpy
import sqlite3
import tempfile
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright


WIDTHS = (320, 390, 768, 1024, 1440, 1920)
ROUTE = "veranstaltungsorte/"
PREVIEW = runpy.run_path(str(Path(__file__).with_name("run-premium2-browser.py")))


def check_images(pictures):
    for picture in pictures.all():
        picture.scroll_into_view_if_needed()
        expect(picture).to_have_js_property("complete", True)
        assert picture.evaluate(
            "img => img.naturalWidth > 0 && img.currentSrc.endsWith('.webp') && "
            "img.alt && img.hasAttribute('width') && img.hasAttribute('height')"
        )
        assert picture.get_attribute("loading") == "lazy"


def open_gallery(page, base, *, touch=False, keyboard=False, shot=None):
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    assert page.goto(base + ROUTE).ok
    expect(page.get_by_role("heading", name="Veranstaltungsorte", exact=True)).to_have_count(1)
    expect(page.get_by_role("heading", name="Würzburg", exact=True)).to_have_count(1)
    expect(page.get_by_role("navigation", name="Standorte", exact=True)).to_have_count(0)
    hero = page.locator(".venue-hero img")
    expect(hero).to_have_js_property("complete", True)
    assert hero.evaluate("img => img.naturalWidth > 0 && img.getAttribute('fetchpriority') === 'high'")
    assert hero.evaluate("""img => {
      const area = img.closest('.venue-hero').getBoundingClientRect();
      const photo = img.getBoundingClientRect();
      const intro = document.querySelector('.venue-intro').getBoundingClientRect();
      return Math.abs(area.height - photo.height) <= 1 && intro.top >= area.bottom - 1
        && photo.bottom <= intro.top + 1 && area.width >= document.documentElement.clientWidth - 1;
    }""")
    expect(page.locator('meta[name="robots"]')).to_have_attribute("content", "noindex, nofollow, noarchive")
    expect(page.locator('link[rel="canonical"]')).to_have_count(0)
    gallery = page.get_by_role("region", name="Räume entdecken", exact=True)
    previews = gallery.locator(".room-gallery__featured img")
    more = gallery.locator("details")
    expect(gallery).to_be_visible()
    expect(previews).to_have_count(5)
    expect(more).not_to_have_attribute("open", "")
    expect(gallery.locator('[data-room-group="seminar-window"]')).to_have_count(2)
    expect(page.locator("h3", has_text="Planen Sie mit Frau Rappelt")).to_be_visible()
    assert "Schreinerei" not in page.content()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    check_images(previews)

    first = gallery.get_by_role("link", name="Raumfoto vergrößern: Austausch am gemeinsamen Tisch")
    first.scroll_into_view_if_needed()
    if shot:
        overview = page.add_style_tag(content=".site-header { position: static !important; }")
        try:
            gallery.screenshot(path=shot / "overview.png")
        finally:
            overview.evaluate("style => style.remove()")
    if keyboard:
        first.focus()
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Tab")
        expect(first).to_be_focused()
        assert first.evaluate("el => el.matches(':focus-visible') && getComputedStyle(el).outlineStyle === 'solid'")
        first.press("Enter")
    elif touch:
        first.tap()
    else:
        first.click()

    dialog = page.get_by_role("dialog", name="Raumansicht")
    expect(dialog).to_be_visible()
    close = dialog.get_by_role("button", name="Schließen")
    expect(close).to_be_focused()
    expect(dialog.get_by_role("status")).to_contain_text("1 / 12")
    expect(dialog.get_by_role("img")).to_have_js_property("complete", True)
    assert dialog.get_by_role("img").evaluate("img => img.naturalWidth > 0 && getComputedStyle(img).objectFit === 'contain'")
    for button in dialog.get_by_role("button").all():
        box = button.bounding_box()
        assert min(box["width"], box["height"]) >= 43.9, box
    assert dialog.evaluate(
        "el => el.getBoundingClientRect().left >= 0 && el.getBoundingClientRect().right <= innerWidth + 1"
    )
    if page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"):
        assert dialog.evaluate("el => getComputedStyle(el).animationName === 'none'")
    page.keyboard.press("Tab")
    expect(dialog.get_by_role("button", name="Vorheriges Foto")).to_be_focused()
    page.keyboard.press("ArrowLeft")
    expect(dialog.get_by_role("status")).to_contain_text("12 / 12")
    page.keyboard.press("ArrowRight")
    expect(dialog.get_by_role("status")).to_contain_text("1 / 12")
    next_button = dialog.get_by_role("button", name="Nächstes Foto")
    if keyboard:
        next_button.press("Enter")
    elif touch:
        next_button.tap()
    else:
        next_button.click()
    expect(dialog.get_by_role("status")).to_contain_text("2 / 12")
    expect(dialog.get_by_role("status")).to_contain_text("Seminarraum mit Fensterfront")
    page.keyboard.press("ArrowRight")
    expect(dialog.get_by_role("status")).to_contain_text("3 / 12")
    expect(dialog.get_by_role("status")).to_contain_text("Seminarraum mit Fensterfront")
    expect(dialog.get_by_role("img")).to_have_js_property("complete", True)
    if shot:
        page.screenshot(path=shot / "dialog.png")
    if touch:
        close.tap()
    else:
        page.keyboard.press("Escape")
    expect(dialog).to_be_hidden()
    expect(first).to_be_focused()
    summary = more.locator("summary")
    summary.scroll_into_view_if_needed()
    summary.focus()
    expect(summary).to_be_focused()
    page.keyboard.press("Space")
    expect(more).to_have_attribute("open", "")
    expect(more.get_by_role("link")).to_have_count(7)
    check_images(more.locator("img"))
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    page.get_by_role("link", name="Workshop in Würzburg anfragen").press("Enter")
    expect(page.locator("#contact-request-form").get_by_label("Thema")).to_have_value("Veranstaltungsplanung in Würzburg")
    page.get_by_role("button", name="Entwurf vorbereiten").press("Enter")
    expect(page.get_by_role("textbox", name="Text zum Übernehmen")).to_have_value(re.compile("Veranstaltungsplanung in Würzburg"))
    assert page.goto(base + "unternehmen/").ok
    teaser = page.locator("[data-venue-teaser]")
    expect(teaser.locator("img")).to_have_count(3)
    expect(page.locator("[data-room-gallery]")).to_have_count(0)
    assert teaser.evaluate("el => el.previousElementSibling.matches('.business-worlds')")
    expect(teaser.get_by_role("link", name="Veranstaltungsorte entdecken")).to_have_attribute("href", urlparse(base).path + ROUTE)
    if shot:
        teaser.screenshot(path=shot / "unternehmen-nachher.png", animations="disabled")
    assert page.goto(base + "leistungen/#gruppenformate").ok
    expect(page.locator("#gruppenformate").get_by_role("link", name="Veranstaltungsorte entdecken")).to_be_visible()
    assert page.goto(base + "coaches/christian-galvano/angebote/neuroleadership/").ok
    expect(page.get_by_role("link", name="Mögliche Veranstaltungsorte")).to_have_attribute("href", urlparse(base).path + ROUTE)
    assert not errors, errors


def no_js(browser, base):
    page = browser.new_page(java_script_enabled=False, viewport={"width": 390, "height": 900})
    assert page.goto(base + ROUTE).ok
    more = page.locator(".room-gallery__more")
    more.locator("summary").focus()
    page.keyboard.press("Space")
    expect(more).to_have_attribute("open", "")
    with page.expect_navigation() as image:
        more.get_by_role("link").first.focus()
        page.keyboard.press("Enter")
    assert image.value.ok and image.value.headers["content-type"].startswith("image/jpeg")
    page.close()


def zoom(playwright, base, shots):
    with tempfile.TemporaryDirectory(prefix="competence-room-zoom-") as path:
        ctx = playwright.firefox.launch_persistent_context(path, no_viewport=True)
        baseline = ctx.pages[0].evaluate("devicePixelRatio")
        ctx.close()
        with closing(sqlite3.connect(Path(path) / "content-prefs.sqlite")) as db:
            db.execute("INSERT INTO settings(name) VALUES ('browser.content.full-zoom')")
            setting = db.execute("SELECT id FROM settings WHERE name = 'browser.content.full-zoom'").fetchone()[0]
            db.execute("INSERT INTO prefs(groupID,settingID,value,timestamp) VALUES (NULL,?,?,0)", (setting, 2))
            db.commit()
        ctx = playwright.firefox.launch_persistent_context(path, no_viewport=True, reduced_motion="reduce")
        try:
            page = ctx.pages[0]
            assert page.goto(base).ok
            assert 1.95 < page.evaluate("devicePixelRatio") / baseline < 2.05
            shots.mkdir(parents=True, exist_ok=True)
            open_gallery(page, base, keyboard=True, shot=shots)
        finally:
            ctx.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--base")
    target.add_argument("--artifact", type=Path)
    parser.add_argument("--screenshots", type=Path, required=True)
    parser.add_argument("--browser", choices=("edge", "firefox"), required=True)
    parser.add_argument("--before", action="store_true")
    args = parser.parse_args()
    if args.base:
        assert args.base.rstrip("/") == "https://dp-manuel.github.io/CompetenceHub"
    with PREVIEW["preview"](args.base, args.artifact) as base, sync_playwright() as p:
        edge = args.browser == "edge"
        browser = p.chromium.launch(channel="msedge") if edge else p.firefox.launch()
        args.screenshots.mkdir(parents=True, exist_ok=True)
        if args.before:
            for width in (390, 1440):
                page = browser.new_page(viewport={"width": width, "height": 900}, reduced_motion="reduce")
                assert page.goto(base + "unternehmen/").ok
                expect(page.locator("[data-venue-teaser]")).to_have_count(0)
                page.locator(".business-worlds").screenshot(path=args.screenshots / f"unternehmen-vorher-{width}.png", animations="disabled")
                page.close()
            browser.close()
            return
        if edge:
            samples = []
            for width in (390, 1440):
                page = browser.new_page(viewport={"width": width, "height": 900}, reduced_motion="reduce")
                page.add_init_script("""window.shifts = 0;
                    new PerformanceObserver(list => {
                      for (const e of list.getEntries()) if (!e.hadRecentInput) window.shifts += e.value;
                    }).observe({type:'layout-shift',buffered:true});""")
                assert page.goto(base + ROUTE).ok
                expect(page.locator(".venue-hero img")).to_have_js_property("complete", True)
                page.evaluate("document.fonts.ready")
                samples.append(page.evaluate("""() => {
                  const hero = document.querySelector('.venue-hero img');
                  return {viewport:innerWidth, cls:window.shifts, heroBytes:performance.getEntriesByName(hero.currentSrc)[0]?.encodedBodySize};
                }"""))
                page.screenshot(path=args.screenshots / f"standort-{width}.png", animations="disabled")
                page.close()
            assert all(item["cls"] <= .05 for item in samples), samples
            (args.screenshots / "media-lab.json").write_text(json.dumps(samples, indent=2) + "\n", encoding="ascii")
        for width in WIDTHS:
            touch = edge and width == 390
            page = browser.new_page(viewport={"width": width, "height": 900}, reduced_motion="reduce", has_touch=touch)
            page.set_default_timeout(8000)
            shot = None
            if width in (390, 1440):
                shot = args.screenshots / args.browser / str(width)
                shot.mkdir(parents=True, exist_ok=True)
            open_gallery(page, base, touch=touch, keyboard=width == 320, shot=shot)
            page.close()
            print(f"{args.browser} {width}px: PASS", flush=True)
        no_js(browser, base)
        if edge:
            page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
            assert page.goto(base).ok
            PREVIEW["HUB"]["drag_network"](page, base, args.screenshots, "venues")
            PREVIEW["REFERENCE"]["verify_public"](page, base)
            page.close()
            print("Hub drag, connection lines and Coach route limits: PASS", flush=True)
        browser.close()
        print(f"{args.browser} JavaScript-free image fallback: PASS", flush=True)
        if not edge:
            zoom(p, base, args.screenshots / "firefox" / "native-200")
            print("Firefox native 200%: PASS", flush=True)


if __name__ == "__main__":
    main()
