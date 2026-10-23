"""Source-approved Susanne Preview acceptance, including actual Edge zoom."""

import importlib.util
import base64
import json
import math
import struct
from pathlib import Path
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "hub_qa", ROOT / "scripts/run-hub-ux-acceptance.py"
)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
OUT = ROOT / "release-artifacts/susanne-20261023"


def capture_actual_zoom(page, path, *, full_page=False):
    # Native zoom uses physical CDP layout metrics; Playwright's CSS clip cuts the image in half.
    session = page.context.new_cdp_session(page)
    try:
        metrics = session.send("Page.getLayoutMetrics")
        box = metrics["contentSize"] if full_page else metrics["layoutViewport"]
        width = box.get("width", box.get("clientWidth"))
        height = box.get("height", box.get("clientHeight"))
        result = session.send(
            "Page.captureScreenshot",
            {
                "format": "png",
                "captureBeyondViewport": True,
                "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1},
            },
        )
        data = base64.b64decode(result["data"])
        if struct.unpack(">I", data[16:20])[0] != int(width):
            raise AssertionError(
                "native zoom capture width differs from physical viewport"
            )
        path.write_bytes(data)
    finally:
        session.detach()


def text_is_visible(node):
    # Font glyph ranges may exceed a line box with visible overflow; test actual clipping ancestors.
    return node.evaluate("""root => {
      const range = document.createRange(); range.selectNodeContents(root);
      for (const r of range.getClientRects()) {
        if (!r.width || !r.height) continue;
        if (r.left < -1 || r.right > innerWidth + 1) return false;
        for (let parent=root; parent; parent=parent.parentElement) {
          const s=getComputedStyle(parent), b=parent.getBoundingClientRect();
          if (['hidden','clip'].includes(s.overflowX) && (r.left<b.left-1 || r.right>b.right+1)) return false;
          if (['hidden','clip'].includes(s.overflowY) && (r.top<b.top-1 || r.bottom>b.bottom+1)) return false;
        }
      }
      return true;
    }""")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(label, condition):
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    def profile(page, base, name):
        page.goto(base + "/coaches/susanne-klemm/", wait_until="networkidle")
        check(
            name + " correct identity",
            page.locator("h1").inner_text() == "Frau Susanne Klemm",
        )
        check(name + " workshop catalogue", page.locator(".workshops li").count() == 8)
        check(
            name + " image loaded",
            page.locator(".coach-profile-portrait img").evaluate(
                "i => i.complete && i.naturalWidth===1200 && i.naturalHeight===1800"
            ),
        )
        check(
            name + " preview noindex",
            "noindex" in page.locator('meta[name="robots"]').get_attribute("content"),
        )
        check(
            name + " no false canonical",
            page.locator('link[rel="canonical"]').count() == 0,
        )
        check(name + " no document overflow", not qa.preview.overflow(page))
        for index, node in enumerate(
            page.locator(
                "main h1, main h2, main h3, .workshops li, .coach-profile-lead"
            ).all()
        ):
            check(f"{name} text {index} not clipped", text_is_visible(node))
        check(
            name + " separate text blocks do not overlap",
            page.locator(
                "main h1, main h2, main h3, .workshops li, .coach-profile-lead"
            ).evaluate_all(
                """nodes => {
          const blocks=nodes.map(n=>{let r=document.createRange();r.selectNodeContents(n);return [...r.getClientRects()];});
          return blocks.every((a,i)=>blocks.slice(i+1).every(b=>a.every(x=>b.every(y=>
            Math.min(x.right,y.right)-Math.max(x.left,y.left)<=1 || Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)<=1))));
        }"""
            ),
        )
        action = page.get_by_role("link", name="Passung und Anfrage besprechen")
        action.focus()
        page.keyboard.press("Tab")
        page.keyboard.press("Shift+Tab")
        check(
            name + " keyboard focus",
            action.evaluate(
                "e => e.matches(':focus-visible') && getComputedStyle(e).outlineStyle !== 'none'"
            ),
        )
        check(
            name + " contact link",
            action.get_attribute("href") == "/CompetenceHub/kontakt",
        )
        page.keyboard.press("Enter")
        page.wait_for_url(lambda target: target.rstrip("/") == base + "/kontakt")
        check(
            name + " keyboard contact handoff",
            page.locator('a[href^="mailto:"]').count() > 0,
        )
        page.go_back(wait_until="networkidle")
        page.evaluate("scrollTo(0, 0)")
        if name == "actual-200-percent":
            capture_actual_zoom(page, OUT / f"profile-{name}.png", full_page=True)
            capture_actual_zoom(page, OUT / f"hero-{name}.png")
            check("native zoom physical capture calibrated", True)
        else:
            page.screenshot(path=str(OUT / f"profile-{name}.png"), full_page=True)
            page.screenshot(path=str(OUT / f"hero-{name}.png"))
            page.locator(".workshops").screenshot(
                path=str(OUT / f"workshops-{name}.png")
            )
        page.goto(base + "/coaches/", wait_until="networkidle")
        page.locator("[data-hub-toggle]").click()
        for category in ("personalentwicklung", "persoenlichkeitsentwicklung"):
            page.locator(f'[data-category="{category}"]').click()
            page.locator('[data-topic="gesundheit-praevention"]').click()
            card = page.locator("[data-preview-coach]").filter(
                has=page.get_by_role("heading", name="Frau Susanne Klemm", exact=True)
            )
            check(name + " filter " + category, card.is_visible())
        page.evaluate("scrollTo(0, 0)")
        if name == "actual-200-percent":
            capture_actual_zoom(page, OUT / f"directory-{name}.png", full_page=True)
        else:
            page.screenshot(path=str(OUT / f"directory-{name}.png"), full_page=True)

    with qa.preview.static_server() as origin, sync_playwright() as p:
        base = origin + "/CompetenceHub"
        browser = p.chromium.launch(channel="msedge", headless=True)
        try:
            for name, width in (("desktop", 1440), ("mobile-390", 390)):
                context = browser.new_context(
                    viewport={"width": width, "height": 1000}, reduced_motion="reduce"
                )
                try:
                    profile(context.new_page(), base, name)
                finally:
                    context.close()
            with tempfile.TemporaryDirectory(
                prefix="competencehub-susanne-zoom-"
            ) as folder:
                path = Path(folder) / "Default"
                path.mkdir()
                level = math.log(2) / math.log(1.2)
                (path / "Preferences").write_text(
                    json.dumps(
                        {"partition": {"default_zoom_level": {"x": level, "0": level}}}
                    ),
                    encoding="utf-8",
                )
                context = p.chromium.launch_persistent_context(
                    folder,
                    channel="msedge",
                    headless=True,
                    no_viewport=True,
                    args=["--window-size=1440,1000", "--force-device-scale-factor=1"],
                    reduced_motion="reduce",
                )
                try:
                    page = context.pages[0]
                    page.goto(
                        base + "/coaches/susanne-klemm/", wait_until="networkidle"
                    )
                    check(
                        "actual 200 percent browser zoom",
                        page.evaluate(
                            "Math.abs(devicePixelRatio-2)<.05 && innerWidth<800"
                        ),
                    )
                    profile(page, base, "actual-200-percent")
                finally:
                    context.close()
        finally:
            browser.close()
    (OUT / "acceptance.json").write_text(
        json.dumps({"checks": checks, "production_changed": False}, indent=2),
        encoding="utf-8",
    )
    print(f"COACH_ONBOARDING_BROWSER=PASS CHECKS={len(checks)}")


if __name__ == "__main__":
    main()
