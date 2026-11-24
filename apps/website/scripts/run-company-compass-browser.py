"""Check the company experience in real Firefox and Edge against a preview build."""

import argparse
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import expect, sync_playwright


TOPICS = (
    "Führung",
    "Teams und Zusammenarbeit",
    "Recruiting und Personal",
    "Personalentwicklung",
    "Veränderung und Transformation",
    "Gesundheit und Prävention",
)
HEADINGS = (
    "In Führung hineinwachsen",
    "Zusammenarbeit gezielt verbessern",
    "Passende Mitarbeitende finden",
    "Stärken erkennen und weiterentwickeln",
    "Orientierung im Wandel schaffen",
    "Belastung im Arbeitsalltag ansprechen",
)
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
HERO = "Was möchten Sie in Ihrem Unternehmen bewegen?"


def open_company(page, base):
    response = page.goto(urljoin(base, "unternehmen/?qa=business-compass"), wait_until="load")
    assert response and response.ok
    expect(page.get_by_role("heading", name=HERO)).to_be_visible()
    expect(page.get_by_role("heading", name="Was beschäftigt Sie gerade?")).to_be_visible()


def check_layout(page):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    violations = page.locator(".company-business").evaluate(
        """root => {
            const visible = element => element.getClientRects().length
                && getComputedStyle(element).visibility === 'visible';
            const result = [];
            const nodes = root.querySelectorAll('h1,h2,h3,p,summary,.compass-option span,.business-link-list a');
            for (const element of nodes) {
                if (element.closest('details:not([open])') && !element.closest('summary')) continue;
                if (!visible(element)) continue;
                const bounds = element.getBoundingClientRect();
                const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                    const range = document.createRange();
                    range.selectNodeContents(walker.currentNode);
                    for (const rect of range.getClientRects()) {
                        if (rect.width && (rect.left < Math.max(0, bounds.left) - 1
                            || rect.right > Math.min(innerWidth, bounds.right) + 1))
                            result.push(walker.currentNode.textContent.trim());
                    }
                }
            }
            return result;
        }"""
    )
    assert not violations, violations


def compass(page, *, touch=False, use_keyboard=False):
    tabs = page.get_by_role("tab")
    expect(tabs).to_have_count(6)
    assert tabs.all_text_contents() and [text.strip() for text in tabs.all_text_contents()] == list(TOPICS)
    panels = page.get_by_role("tabpanel")
    below = page.locator(".business-worlds")
    y = below.evaluate("el => el.offsetTop")
    links = set()
    if use_keyboard:
        tabs.first.focus()
    for index, heading in enumerate(HEADINGS):
        tab = tabs.nth(index)
        assert tab.bounding_box()["height"] >= 44
        if use_keyboard:
            page.keyboard.press("ArrowRight" if index else "Home")
            expect(tab).to_be_focused()
        else:
            (tab.tap if touch else tab.click)()
        expect(tab).to_have_attribute("aria-selected", "true")
        expect(panels).to_have_count(1)
        expect(panels).to_have_accessible_name(TOPICS[index])
        expect(panels.get_by_role("heading", name=heading)).to_be_visible()
        assert 2 <= panels.get_by_role("link").count() <= 4
        links.update(panels.get_by_role("link").evaluate_all("links => links.map(link => link.href)"))
        assert abs(below.evaluate("el => el.offsetTop") - y) <= 1, "topic switch changed layout"
        check_layout(page)
    return links


def keyboard(page):
    tabs = page.get_by_role("tab")
    tabs.first.focus()
    page.keyboard.press("End")
    expect(tabs.last).to_be_focused()
    expect(tabs.last).to_have_attribute("aria-selected", "true")
    page.keyboard.press("ArrowRight")
    expect(tabs.first).to_be_focused()
    page.keyboard.press("ArrowLeft")
    expect(tabs.last).to_be_focused()
    page.keyboard.press("Home")
    expect(tabs.first).to_be_focused()
    assert tabs.first.evaluate("el => getComputedStyle(el).outlineStyle") != "none"
    page.keyboard.press("Space")
    page.keyboard.press("Tab")
    expect(page.get_by_role("tabpanel")).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.get_by_role("tabpanel").get_by_role("link").first).to_be_focused()


def disclosures_and_contact(page, base, *, use_keyboard=False):
    def activate(control):
        control.press("Enter") if use_keyboard else control.click()

    price = page.get_by_text("2.500–3.800 €", exact=True)
    expect(price).to_be_hidden()
    details = page.get_by_text("Leistungsstufen und Preise", exact=True)
    details.focus()
    page.keyboard.press("Enter")
    expect(price).to_be_visible()
    expect(page.get_by_text("4.500–7.500 €", exact=True)).to_be_visible()
    expect(page.get_by_text("zzgl. MwSt. · pro Assessment-Center-Tag", exact=True)).to_be_visible()
    activate(details)
    expect(price).to_be_hidden()
    expect(page.locator("#feedback-concept-clean blockquote")).to_have_text(
        "„Von der ersten Anfrage bis zur Durchführung lief alles absolut reibungslos. "
        "Besonders begeistert hat uns das flexible Matching.“"
    )
    activate(page.locator("#feedback-concept-clean").get_by_role("link"))
    story = page.locator("details", has=page.locator("#concept-clean-kommunikation"))
    expect(story).to_have_attribute("open", "")
    other = page.locator("details", has=page.locator("#fuehrung-neue-rolle"))
    expect(other).not_to_have_attribute("open", "")
    activate(other.locator("summary"))
    expect(other.get_by_text("Es ist ein Beispiel", exact=False)).to_be_visible()
    check_layout(page)
    activate(story.locator("summary"))
    activate(other.locator("summary"))
    faq = page.locator(".business-faq summary").first
    activate(faq)
    expect(faq.locator("..")).to_have_attribute("open", "")
    activate(faq)
    activate(page.get_by_role("link", name="Persönlich beraten lassen"))
    contact = page.locator("#unternehmenskontakt")
    portrait = contact.get_by_role("img", name="Frau Rappelt")
    expect(portrait).to_be_visible()
    portrait.scroll_into_view_if_needed()
    expect(portrait).to_have_js_property("complete", True)
    assert portrait.evaluate("img => img.naturalWidth") > 0
    expect(contact.get_by_role("link", name="0172 6799972 anrufen")).to_have_attribute("href", "tel:+491726799972")
    expect(contact.get_by_role("link", name="Bedarf besprechen")).to_have_attribute("href", urlsplit(urljoin(base, "kontakt")).path)


def verify_links(page, urls):
    for target in sorted(urls):
        parts = urlsplit(target)
        if parts.scheme not in ("http", "https"):
            continue
        response = page.request.get(target, timeout=15_000)
        assert response.ok, (target, response.status)
        if parts.fragment:
            assert page.evaluate(
                "([html, id]) => !!new DOMParser().parseFromString(html, 'text/html').getElementById(id)",
                [response.text(), parts.fragment],
            ), target


def no_script(browser, base):
    page = browser.new_page(java_script_enabled=False, viewport={"width": 390, "height": 900}, reduced_motion="reduce")
    page.set_default_timeout(7000)
    try:
        open_company(page, base)
        expect(page.get_by_role("tab")).to_have_count(0)
        for title, heading in zip(TOPICS, HEADINGS):
            page.locator(".compass-options").get_by_role("link", name=title, exact=True).click()
            expect(page.get_by_role("heading", name=heading, exact=True)).to_be_in_viewport()
        page.locator(".business-assessment summary").click()
        expect(page.get_by_text("2.500–3.800 €", exact=True)).to_be_visible()
        page.locator("details[data-business-story] summary").last.click()
        expect(page.locator("#concept-clean-kommunikation")).to_be_visible()
    finally:
        page.close()


def native_zoom(playwright, base, output, prefix):
    with tempfile.TemporaryDirectory(prefix="competence-company-zoom-") as path:
        context = playwright.firefox.launch_persistent_context(path, no_viewport=True)
        ratio = context.pages[0].evaluate("devicePixelRatio")
        context.close()
        with closing(sqlite3.connect(Path(path) / "content-prefs.sqlite")) as db:
            db.execute("INSERT INTO settings(name) VALUES ('browser.content.full-zoom')")
            setting = db.execute("SELECT id FROM settings WHERE name = 'browser.content.full-zoom'").fetchone()[0]
            db.execute("INSERT INTO prefs(groupID,settingID,value,timestamp) VALUES (NULL,?,?,0)", (setting, 2.0))
            db.commit()
        context = playwright.firefox.launch_persistent_context(path, no_viewport=True, reduced_motion="reduce")
        try:
            page = context.pages[0]
            page.set_default_timeout(7000)
            open_company(page, base)
            assert 1.95 < page.evaluate("devicePixelRatio") / ratio < 2.05
            compass(page, use_keyboard=True)
            keyboard(page)
            disclosures_and_contact(page, base, use_keyboard=True)
            page.screenshot(path=output / f"{prefix}-firefox-native-200.png", full_page=True, animations="disabled")
        finally:
            context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--screenshots", type=Path, required=True)
    parser.add_argument("--prefix", default="local")
    parser.add_argument("--browser", choices=("firefox", "edge"), required=True)
    args = parser.parse_args()
    base = args.base.rstrip("/") + "/"
    args.screenshots.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        is_edge = args.browser == "edge"
        browser = playwright.chromium.launch(channel="msedge") if is_edge else playwright.firefox.launch()
        try:
            for width in WIDTHS:
                touch = is_edge and width == 390
                page = browser.new_page(
                    viewport={"width": width, "height": 900}, reduced_motion="reduce", has_touch=touch
                )
                page.set_default_timeout(7000)
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                open_company(page, base)
                expect(page.get_by_role("tab").first).to_have_attribute("aria-selected", "true")
                if width in (390, 1440):
                    page.screenshot(path=args.screenshots / f"{args.prefix}-{args.browser}-{width}.png", full_page=True, animations="disabled")
                links = compass(page, touch=touch)
                assert page.locator(".compass-panel[data-active=true] > div").evaluate("el => getComputedStyle(el).animationName") == "none"
                if width in (390, 1440):
                    keyboard(page)
                    disclosures_and_contact(page, base)
                if width == 1440:
                    links.update(page.locator(".business-worlds a, .business-process a, .business-assessment a, .business-contact a, footer a").evaluate_all("links => links.map(link => link.href)"))
                    verify_links(page, links)
                assert not errors, errors
                page.close()
                print(f"{args.browser} {width}px: PASS", flush=True)

            no_script(browser, base)
            page = browser.new_page(reduced_motion="no-preference")
            open_company(page, base)
            page.get_by_role("tab").nth(1).click()
            expect(page.get_by_role("tabpanel")).to_have_accessible_name(TOPICS[1])
            assert page.locator(".compass-panel[data-active=true] > div").evaluate("el => getComputedStyle(el).animationName") != "none"
            page.close()
            print(f"{args.browser} no JavaScript and motion preferences: PASS", flush=True)
        finally:
            browser.close()
        if not is_edge:
            native_zoom(playwright, base, args.screenshots, args.prefix)
            print("Firefox native 200%: PASS", flush=True)


if __name__ == "__main__":
    main()
