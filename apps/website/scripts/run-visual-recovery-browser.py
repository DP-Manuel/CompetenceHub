"""Exercise rendered contrast and scroll-driven progress in Firefox and Edge."""

import argparse
from contextlib import closing
from pathlib import Path
import re
import sqlite3
import tempfile

from playwright.sync_api import expect, sync_playwright


CONTRAST = """elements => {
  const channels = value => value.match(/[\d.]+/g).map(Number);
  const blend = (over, under) => under.map((c, i) =>
    c * (1 - (over[3] ?? 1)) + over[i] * (over[3] ?? 1));
  const light = rgb => rgb.map(c => c / 255).map(c =>
    c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4
  ).reduce((sum, c, i) => sum + c * [.2126, .7152, .0722][i], 0);
  return elements.map(el => {
    const stack = [];
    for (let node = el; node; node = node.parentElement) {
      stack.push(channels(getComputedStyle(node).backgroundColor));
    }
    const bg = stack.reverse().reduce((color, over) => blend(over, color), [255, 255, 255]);
    const fg = blend(channels(getComputedStyle(el).color), bg);
    const [low, high] = [light(bg), light(fg)].sort((a, b) => a - b);
    return [el.innerText.trim(), (high + .05) / (low + .05)];
  });
}"""


def contrast(locator):
    samples = locator.evaluate_all(CONTRAST)
    assert samples, f"No contrast samples for {locator}"
    assert all(ratio >= 4.5 for _, ratio in samples), samples
    return min(ratio for _, ratio in samples)


def bounds(page):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")


def company(page, base, shots=None, zoom=False):
    response = page.goto(base + "unternehmen/?qa=visual-recovery", wait_until="load")
    assert response and response.ok
    summary = page.locator("#use-case-trigger-concept-clean-kommunikation")
    story = summary.locator("..")
    other = page.locator("#use-case-trigger-fuehrung-neue-rolle").locator("..")
    minimums = []

    def state(name, rendered):
        minimums.append(contrast(rendered))
        bounds(page)
        if shots:
            # Capture the full accordion once open, without obscuring its keyboard focus state.
            target = story if name == "open" else page if name == "focus" else summary
            target.screenshot(path=shots / f"concept-clean-{name}.png")

    summary.scroll_into_view_if_needed()
    state("normal", summary.locator(".story-label, strong"))
    if not zoom:
        summary.hover()
        expect(summary).to_have_css("background-color", "rgb(243, 248, 248)")
        state("hover", summary.locator(".story-label, strong"))
        page.mouse.move(4, 4)
    summary.focus()
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Tab")
    expect(summary).to_be_focused()
    assert summary.evaluate("el => el.matches(':focus-visible') && getComputedStyle(el).outlineStyle !== 'none'")
    state("focus", summary.locator(".story-label, strong"))

    page.keyboard.press("Enter")
    expect(story).to_have_attribute("open", "")
    expect(other).not_to_have_attribute("open", "")
    state("open", story.locator("summary strong, .story-label, p, h3, small, a, .case-story__marker"))
    print(f"  Concept Clean contrast minimum: {min(minimums):.2f}:1", flush=True)
    other.locator("summary").press("Enter")
    minimums.append(contrast(other.locator("summary strong, .story-label, p, h3, small, .case-story__marker")))
    expect(story).to_have_attribute("open", "")
    for selector in (".business-assessment", ".business-faq"):
        disclosure = page.locator(selector).locator("details").first
        disclosure.locator("summary").press("Enter")
        expect(disclosure).to_have_attribute("open", "")
        minimums.append(contrast(disclosure.locator("summary, h3, p, small, a")))

    for tab in page.get_by_role("tab").all():
        tab.press("Enter")
        expect(tab).to_have_attribute("aria-selected", "true")
        minimums.append(contrast(tab))
        minimums.append(contrast(page.get_by_role("tabpanel").locator("h3,p,a")))
    inactive = page.locator("[role=tab][aria-selected=false]").first
    if not zoom:
        inactive.hover()
        minimums.append(contrast(inactive))
        page.locator(".business-contact .button").hover()
    minimums.append(contrast(page.locator(".business-contact .button, .business-contact .text-link")))
    bounds(page)
    print(f"  Company contrast minimum: {min(minimums):.2f}:1", flush=True)


def destination(page, index):
    return page.locator("[data-journey-step]").nth(index).evaluate(
        "el => Math.round(scrollY + el.getBoundingClientRect().top - parseFloat(getComputedStyle(el).scrollMarginTop))"
    )


def wheel_to(page, y, scale=1):
    previous = page.evaluate("scrollY")
    assert abs(y - previous) > 3
    current = previous
    while abs(y - current) > 3:
        distance = y - current
        if scale != 1:
            distance = max(-140, min(140, distance))
        page.mouse.wheel(0, round(distance * scale))
        page.wait_for_function("y => Math.abs(scrollY - y) <= 3", arg=current + distance, timeout=5000)
        current = page.evaluate("scrollY")
    assert (current - previous) * (y - previous) > 0


def progression(page, base, shots=None, zoom_scale=1):
    response = page.goto(base + "?qa=visual-recovery", wait_until="load")
    assert response and response.ok
    journey = page.locator(".hub-journey--compact")
    steps = journey.locator("[data-journey-step]")
    fills = journey.locator("[data-journey-fill]")
    markers = journey.locator(".hub-journey__milestone")
    current = journey.locator('[aria-current="step"]')
    markers_colors = (
        "rgb(255, 127, 87)",
        "rgb(233, 244, 244)",
    )

    def assert_step(index):
        expect(current).to_have_count(1)
        expect(current).to_have_attribute("data-journey-step", str(index + 1))
        expect(markers.nth(index)).to_have_css("background-color", markers_colors[0])
        assert markers.nth(index).evaluate("el => getComputedStyle(el).outlineStyle") == "solid"
        for other in range(4):
            if other != index:
                expect(markers.nth(other)).to_have_css("background-color", markers_colors[1])
        contrast(journey.locator(".hub-journey__milestone, h3, p, .text-link"))
        bounds(page)

    def fraction(segment, expected):
        page.wait_for_function(
            """([i, expected]) => {
              const el = document.querySelectorAll('[data-journey-fill]')[i];
              const transform = new DOMMatrixReadOnly(getComputedStyle(el).transform);
              const value = matchMedia('(min-width: 48rem)').matches ? transform.a : transform.d;
              return Math.abs(value - expected) < .12;
            }""",
            arg=[segment, expected],
            timeout=5000,
        )

    expect(current).to_have_count(0)
    expect(markers.last).to_have_css("background-color", markers_colors[1])
    reduced = page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
    if reduced:
        expect(fills.first).to_have_css("transition-duration", "0s")
    else:
        assert fills.first.evaluate("el => parseFloat(getComputedStyle(el).transitionDuration)") > 0
    expect(fills.first).to_have_css("background-color", "rgb(0, 156, 166)")
    baseline_tops = steps.evaluate_all("items => items.map(i => i.getBoundingClientRect().top + scrollY)")

    # Use actual wheel input, not scrollTo or a synthetic scroll event.
    positions = [destination(page, index) for index in range(4)]
    assert positions == sorted(set(positions))
    page.mouse.move(5, 250)
    for index, position in enumerate(positions):
        wheel_to(page, position + 4, zoom_scale)
        assert_step(index)
        if index:
            fraction(index - 1, 1)
        if shots:
            page.screenshot(path=shots / f"journey-step-{index + 1:02d}.png")
        if index < 3:
            wheel_to(page, round((position + positions[index + 1]) / 2), zoom_scale)
            assert_step(index)
            fraction(index, .5)

    wheel_to(page, round((positions[1] + positions[2]) / 2), zoom_scale)
    assert_step(1)
    fraction(1, .5)
    fraction(2, 0)
    if shots:
        page.screenshot(path=shots / "journey-reverse-02.png")
    final_tops = steps.evaluate_all("items => items.map(i => i.getBoundingClientRect().top + scrollY)")
    assert all(abs(before - after) < 1 for before, after in zip(baseline_tops, final_tops)), (baseline_tops, final_tops)

    response = page.goto(base + "?qa=visual-recovery-anchor#hub-journey-step-3", wait_until="load")
    assert response and response.ok
    assert_step(2)
    fraction(1, 1)
    fraction(2, 0)
    if zoom_scale == 1:
        width = page.viewport_size["width"]
        page.set_viewport_size({"width": 390 if width > 700 else 1000, "height": 820})
        page.mouse.move(5, 250)
        wheel_to(page, destination(page, 1) + 4)
        assert_step(1)
        fraction(0, 1)
    link = steps.nth(1).get_by_role("link", name="Coaches kennenlernen")
    link.focus()
    assert link.evaluate("el => getComputedStyle(el).outlineStyle") != "none"
    if zoom_scale != 1:
        link.press("Enter")
    else:
        link.click()
    page.wait_for_url(re.compile(r"/coaches/?$"))
    expect(page.get_by_role("heading", level=1)).to_be_visible()


def native_zoom(playwright, base):
    with tempfile.TemporaryDirectory(prefix="competence-recovery-zoom-") as tmp:
        profile = playwright.firefox.launch_persistent_context(tmp, no_viewport=True)
        original = profile.pages[0].evaluate("devicePixelRatio")
        profile.close()
        with closing(sqlite3.connect(Path(tmp) / "content-prefs.sqlite")) as db:
            db.execute("INSERT INTO settings(name) VALUES ('browser.content.full-zoom')")
            setting = db.execute("SELECT id FROM settings WHERE name = 'browser.content.full-zoom'").fetchone()[0]
            db.execute("INSERT INTO prefs(groupID,settingID,value,timestamp) VALUES (NULL,?,?,0)", (setting, 2.0))
            db.commit()
        profile = playwright.firefox.launch_persistent_context(tmp, no_viewport=True, reduced_motion="reduce")
        try:
            page = profile.pages[0]
            page.set_default_timeout(8000)
            progression(page, base, zoom_scale=2)
            assert 1.95 < page.evaluate("devicePixelRatio") / original < 2.05
            company(page, base, zoom=True)
        finally:
            profile.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--screenshots", required=True, type=Path)
    parser.add_argument("--browser", choices=("firefox", "edge"), required=True)
    args = parser.parse_args()
    base = args.base.rstrip("/") + "/"
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch() if args.browser == "firefox" else playwright.chromium.launch(channel="msedge")
        for width, motion in ((1440, "no-preference"), (390, "reduce"), (320, "reduce")):
            page = browser.new_page(viewport={"width": width, "height": 950}, reduced_motion=motion)
            page.set_default_timeout(8000)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            shots = args.screenshots / args.browser / str(width) if width in (1440, 390) else None
            if shots:
                shots.mkdir(parents=True, exist_ok=True)
            company(page, base, shots)
            progression(page, base, shots)
            assert not errors, errors
            page.close()
            print(f"{args.browser} {width}px ({motion}): PASS", flush=True)
        page = browser.new_page(java_script_enabled=False)
        page.goto(base)
        expect(page.locator(".hub-journey--compact li a")).to_have_count(4)
        expect(page.locator(".hub-journey--compact [aria-current=step]")).to_have_count(0)
        browser.close()
        if args.browser == "firefox":
            native_zoom(playwright, base)
            print("Firefox native 200%: PASS", flush=True)


if __name__ == "__main__":
    main()
