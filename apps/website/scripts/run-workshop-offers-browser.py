"""Check the workshop journey in both real static build targets without opening mail."""

import argparse
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright


THEMES = (
    ("christian-galvano", "neuroleadership", "Neuroleadership", "Herr Christian Galvano"),
    ("christian-galvano", "konfliktmanagement", "Konfliktmanagement", "Herr Christian Galvano"),
    ("christian-galvano", "stresspraevention", "Stress- und Burnoutpr\u00e4vention", "Herr Christian Galvano"),
    ("manuela-rodriguez", "ki-kompetenz", "KI-Kompetenz und Verantwortung", "Manuela Rodr\u00edguez, M.A."),
)


def enter(page, url):
    response = page.goto(url)
    assert response is None or response.status in (200, 304), url
    expect(page).to_have_url(url)
    expect(page.locator("main h1")).to_have_count(1)


def fit(container):
    assert container.evaluate("""node => {
      const box = node.getBoundingClientRect();
      return node.scrollWidth <= node.clientWidth + 1 && box.left >= -1
        && box.right <= document.documentElement.clientWidth + 1;
    }""")


def preview_journey(page, base, screenshots):
    discovery_url = base + "coaches/#workshop-themen"
    for width in (320, 390, 1440):
        page.set_viewport_size({"width": width, "height": 900})
        enter(page, discovery_url)
        topics = page.locator("#workshop-themen")
        fit(topics)
        expect(topics.get_by_role("link", name="Workshop-Bedarf mit Frau Rappelt besprechen")).to_have_attribute(
            "href", urlsplit(base + "kontakt/").path
        )
        assert topics.locator(".workshop-topic strong").all_text_contents() == [theme[2] for theme in THEMES]
        if screenshots and width != 320:
            topics.screenshot(path=screenshots / f"discovery-{width}.png")
        for slug, key, title, coach in THEMES:
            detail_url = base + f"coaches/{slug}/angebote/{key}/"
            link = topics.get_by_role("link", name=title)
            assert link.bounding_box()["height"] >= 44
            link.focus()
            expect(link).to_be_focused()
            assert link.evaluate("node => getComputedStyle(node).outlineStyle === 'solid'")
            link.press("Enter")
            expect(page).to_have_url(detail_url)
            expect(page.get_by_role("heading", name=title, level=1)).to_be_visible()
            expect(page.locator('meta[name="robots"]')).to_have_attribute("content", "noindex, nofollow, noarchive")
            expect(page.locator('link[rel="canonical"]')).to_have_count(0)
            main = page.locator("main")
            fit(main)
            portrait = main.get_by_role("img")
            expect(portrait).to_have_js_property("complete", True)
            assert portrait.evaluate("node => node.naturalWidth > 0")
            expect(main.get_by_role("link", name=coach)).to_have_attribute("href", urlsplit(base + f"coaches/{slug}/").path)
            expect(main.get_by_role("link", name="Thema mit Frau Rappelt besprechen")).to_have_attribute(
                "href", urlsplit(base + "kontakt/").path + f"?workshop={key}"
            )
            draft = urlsplit(main.get_by_role("link", name="Direkt per E-Mail anfragen").get_attribute("href"))
            assert (draft.scheme, draft.path) == ("mailto", "competencehub@donner-partner.de")
            fields = parse_qs(draft.query)
            assert title in fields["subject"][0] and coach in fields["subject"][0]
            assert title in fields["body"][0] and coach in fields["body"][0]
            detail_copy = main.locator(".workshop-lede").inner_text()
            if screenshots and key == "stresspraevention" and width != 320:
                main.screenshot(path=screenshots / f"detail-{width}.png")
            main.get_by_role("link", name=coach).click()
            disclosure = page.locator("#angebote details").filter(has_text=title)
            disclosure.locator("summary").press("Enter")
            expect(disclosure.locator("p")).to_have_text(detail_copy)
            disclosure.get_by_role("link", name=f"{title}: Details und Anfrage").press("Enter")
            expect(page).to_have_url(detail_url)
            page.locator("main").get_by_role("link", name="Alle Workshop-Themen").click()
            expect(page).to_have_url(discovery_url)

    for path in (
        "coaches/carolin-hupp/angebote/neuroleadership/",
        "coaches/susanne-klemm/angebote/neuroleadership/",
        "coaches/manuela-rodriguez/angebote/neuroleadership/",
        "coaches/christian-galvano/angebote/erfunden/",
    ):
        assert page.request.get(base + path).status == 404, path


def production_isolation(page, base):
    enter(page, base + "coaches/")
    expect(page.locator("#workshop-themen")).to_have_count(0)
    expect(page.locator(".coach-card__name")).to_have_count(8)
    for slug in {theme[0] for theme in THEMES}:
        enter(page, base + f"coaches/{slug}/")
        expect(page.locator("main a[href*='/angebote/'], main a[href*='#workshop-themen']")).to_have_count(0)
    for slug, key, *_ in THEMES:
        assert page.request.get(base + f"coaches/{slug}/angebote/{key}/").status == 404, key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preview_url")
    parser.add_argument("production_url")
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge")
        page = browser.new_page(reduced_motion="reduce")
        preview_journey(page, args.preview_url.rstrip("/") + "/", args.screenshots)
        production_isolation(page, args.production_url.rstrip("/") + "/")
        browser.close()
    print("PASS: four workshop detail journeys at 320, 390 and 1440 px; publication boundaries intact.")


if __name__ == "__main__":
    main()
