"""Preview-only progressive disclosure and actual text/Hub clearance checks."""
import argparse
import importlib.util
import json
import math
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preview_qa", ROOT / "scripts/run-preview-browser-acceptance.py")
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)
OUT = ROOT / "release-artifacts/hub-ux-20261022"


def geometry(page):
    return page.evaluate("""() => {
      const rect = s => document.querySelector(s).getBoundingClientRect();
      const mind = rect('[data-node="mindforge"]');
      const contact = rect('[data-node="kontakt"]');
      const copy = rect('.living-hero__copy--centered');
      const actions = rect('.living-hero__actions--centered');
      return {top_gap: mind.top - copy.bottom, bottom_gap: actions.top - contact.bottom,
        width: innerWidth, dpr: devicePixelRatio,
        overflow: document.documentElement.scrollWidth > innerWidth + 1};
    }""")


def text_fits(locator):
    return locator.evaluate("""root => {
      const nodes = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      while (nodes.nextNode()) {
        const node = nodes.currentNode;
        if (!node.textContent.trim()) continue;
        const range = document.createRange(); range.selectNodeContents(node);
        const box = node.parentElement.getBoundingClientRect();
        for (const r of range.getClientRects()) {
          if (r.width > 0 && (r.left < box.left - 1 || r.right > box.right + 1
            || r.top < box.top - 1 || r.bottom > box.bottom + 1)) return false;
        }
      }
      return root.scrollWidth <= root.clientWidth + 1 && root.scrollHeight <= root.clientHeight + 1;
    }""")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []
    metrics = []
    def check(label, valid):
        if not valid:
            raise AssertionError(label)
        checks.append(label)
    with preview.static_server("production" if args.baseline else "preview") as origin, sync_playwright() as p:
        base = origin + ("" if args.baseline else "/CompetenceHub")
        browser = p.chromium.launch(channel="msedge", headless=True)
        try:
            for width in (2048, 1440, 1280, 960, 390):
                context = browser.new_context(viewport={"width": width, "height": 1000}, reduced_motion="reduce")
                page = context.new_page()
                page.goto(base + "/", wait_until="networkidle")
                metric = geometry(page)
                metrics.append(metric)
                page.screenshot(path=str(OUT / f"home-{'before' if args.baseline else 'after'}-{width}.png"), full_page=True)
                if not args.baseline:
                    check(f"{width} Hub top clearance", metric["top_gap"] >= 24)
                    check(f"{width} Hub CTA clearance", metric["bottom_gap"] >= 24)
                    check(f"{width} home no overflow", not metric["overflow"])
                    page.goto(base + "/coaches/", wait_until="networkidle")
                    toggle = page.locator("[data-hub-toggle]")
                    check(f"{width} initial central bubble only", toggle.is_visible()
                          and not page.locator("#preview-categories").is_visible()
                          and not page.locator("#preview-topic-options").is_visible())
                    toggle.focus()
                    page.keyboard.press("Tab")
                    page.keyboard.press("Shift+Tab")
                    check(f"{width} visible focus", toggle.evaluate("e => e.matches(':focus-visible') && getComputedStyle(e).outlineStyle !== 'none'"))
                    page.keyboard.press("Enter")
                    expect(toggle).to_have_attribute("aria-expanded", "true")
                    check(f"{width} three satellites only", page.locator("[data-category]:visible").count() == 3
                          and not page.locator("#preview-topic-options").is_visible())
                    boxes = page.locator(".preview-topic-hub button:visible").evaluate_all("nodes => nodes.map(n => { const r=n.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; })")
                    for i, box in enumerate(boxes):
                        check(f"{width} bubble {i} target", box["w"] >= 44 and box["h"] >= 44)
                        check(f"{width} bubble {i} text", text_fits(page.locator(".preview-topic-hub button:visible").nth(i)))
                        for other in boxes[i + 1:]:
                            check(f"{width} bubble separation", box["x"] + box["w"] <= other["x"] or other["x"] + other["w"] <= box["x"]
                                  or box["y"] + box["h"] <= other["y"] or other["y"] + other["h"] <= box["y"])
                    page.locator('[data-category="personalentwicklung"]').click()
                    check(f"{width} relevant topics visible", page.locator("#preview-topic-options").is_visible())
                    health = page.locator('[data-topic="gesundheit-praevention"]')
                    health.click()
                    expected = page.locator("[data-preview-coach]:visible h2").all_text_contents()
                    page.locator('[data-category="persoenlichkeitsentwicklung"]').click()
                    health.click()
                    check(f"{width} many-to-many remains canonical", page.locator("[data-topic='gesundheit-praevention']").count() == 1
                          and page.locator("[data-preview-coach]:visible h2").all_text_contents() == expected)
                    page.reload(wait_until="networkidle")
                    expect(health).to_have_attribute("aria-pressed", "true")
                    toggle.click()
                    check(f"{width} return to All", page.locator("[data-preview-coach]:visible").count() == 8
                          and not page.locator("#preview-topic-options").is_visible())
                    toggle.click()
                    expect(toggle).to_have_attribute("aria-expanded", "false")
                    check(f"{width} no overflow", not page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"))
                    check(f"{width} reduced motion", toggle.evaluate("e => getComputedStyle(e).animationName === 'none'"))
                    page.emulate_media(reduced_motion="no-preference")
                    page.locator("#preview-topics-title").click()
                    page.mouse.move(0, 0)
                    check(f"{width} gentle motion enabled", toggle.evaluate("e => e.getAnimations().some(a => a.playState === 'running')"))
                    page.emulate_media(reduced_motion="reduce")
                    toggle.click()
                    page.evaluate("""() => scrollTo({top: document.querySelector('.coach-topic-explorer').getBoundingClientRect().top
                      + scrollY - document.querySelector('.site-header').getBoundingClientRect().height - 20, behavior: 'instant'})""")
                    page.screenshot(path=str(OUT / f"topics-after-{width}.png"))
                context.close()
            if not args.baseline:
                touch = browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
                try:
                    page = touch.new_page()
                    page.goto(base + "/coaches/", wait_until="networkidle")
                    page.locator("[data-hub-toggle]").tap()
                    page.locator('[data-category="personalentwicklung"]').tap()
                    check("touch progressive disclosure", page.locator("#preview-topic-options").is_visible())
                finally:
                    touch.close()
                with tempfile.TemporaryDirectory(prefix="competence-hub-zoom-") as temp:
                    profile = Path(temp) / "Default"
                    profile.mkdir()
                    level = math.log(2) / math.log(1.2)
                    (profile / "Preferences").write_text(json.dumps({"partition": {"default_zoom_level": {"x": level, "0": level}}}), encoding="utf-8")
                    zoom = p.chromium.launch_persistent_context(temp, channel="msedge", headless=True,
                        no_viewport=True, args=["--window-size=1440,1000", "--force-device-scale-factor=1"], reduced_motion="reduce")
                    try:
                        page = zoom.pages[0]
                        page.goto(base + "/", wait_until="networkidle")
                        metric = geometry(page)
                        metrics.append({"zoom": "200%", **metric})
                        check("actual browser zoom 200%, not DPR emulation", abs(metric["dpr"] - 2) < .05 and metric["width"] < 800)
                        check("zoom Hub clearance", metric["top_gap"] >= 24 and metric["bottom_gap"] >= 24 and not metric["overflow"])
                        page.goto(base + "/coaches/", wait_until="networkidle")
                        page.locator("[data-hub-toggle]").click()
                        page.locator('[data-category="personalentwicklung"]').click()
                        check("actual zoom topics fit", not page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"))
                        page.screenshot(path=str(OUT / "topics-actual-200-percent.png"))
                    finally:
                        zoom.close()
        finally:
            browser.close()
    result = {"baseline": args.baseline, "baseline_source": "unchanged local production artifact, same Hub layout" if args.baseline else None, "checks": checks, "metrics": metrics}
    (OUT / ("baseline.json" if args.baseline else "acceptance.json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"checks": len(checks), "metrics": metrics}))


if __name__ == "__main__":
    main()
