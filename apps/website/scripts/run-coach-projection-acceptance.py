"""Offline projected Astro acceptance. Intercept every request; no HTTP server or fetch."""

import argparse
import base64
import json
import hashlib
import math
import mimetypes
from pathlib import Path
import struct
import tempfile
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
LOCAL = ROOT / ".tmp/coach4"
BUILD = ROOT / "apps/website/.tmp/coach4"
ORIGIN = "http://coach4.invalid"


def local_path(value, root=LOCAL):
    path = Path(value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("QA path must stay in its explicit local workspace")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", default=str(BUILD / "site-preview"))
    parser.add_argument("--fixture", default=str(LOCAL / "synthetic-preview.json"))
    parser.add_argument("--out", default=str(LOCAL / "browser-preview"))
    args = parser.parse_args()
    dist = local_path(args.dist, BUILD)
    fixture, out = map(local_path, (args.fixture, args.out))
    for forbidden in (
        "data-store.json",
        "settings.json",
        "content-assets.mjs",
        "content-modules.mjs",
    ):
        if (dist / forbidden).exists():
            raise ValueError("Astro cache material must not enter the comparison build")
    out.mkdir(parents=True, exist_ok=True)
    artifact = json.loads(fixture.read_text(encoding="utf-8"))
    coaches = artifact["coaches"]
    base = "/CompetenceHub" if artifact["environment"] == "preview" else ""
    checks, errors, requests = [], [], []
    fixture_hash = hashlib.sha256(fixture.read_bytes()).hexdigest()

    def check(label, condition):
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    def install(context):
        def route(request_route):
            request = request_route.request
            target = urlsplit(request.url)
            if (
                f"{target.scheme}://{target.netloc}" != ORIGIN
                or request.method != "GET"
            ):
                errors.append("unexpected external or write request")
                request_route.abort()
                return
            path = unquote(target.path)
            if base and not path.startswith(base + "/"):
                errors.append("base path escaped")
                request_route.abort()
                return
            path = path[len(base) :].lstrip("/")
            file = (dist / path).resolve()
            if file.is_dir():
                file /= "index.html"
            if not file.is_relative_to(dist) or not file.is_file():
                errors.append("missing or unsafe local resource: " + path)
                request_route.abort()
                return
            requests.append(path)
            content_type = mimetypes.guess_type(file)[0] or "application/octet-stream"
            request_route.fulfill(
                status=200, body=file.read_bytes(), content_type=content_type
            )

        context.route("**/*", route)
        context.on(
            "page",
            lambda page: page.on("pageerror", lambda error: errors.append(str(error))),
        )

    def fit(page, label):
        check(
            label + " document fits",
            page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"),
        )
        check(
            label + " text not clipped or overlapping",
            page.locator(
                "main h1, main h2, main h3, main h4, main p, main dt, main dd, main label, main li > strong"
            ).evaluate_all(
                """nodes => {
          const blocks=[];
          for (const node of nodes) {
            if (!node.checkVisibility()) continue;
            const range=document.createRange(); range.selectNodeContents(node);
            const rects=[...range.getClientRects()].filter(r=>r.width && r.height);
            for (const r of rects) {
              if (r.left < -1 || r.right > innerWidth+1) return false;
              for (let p=node;p;p=p.parentElement) {
                const s=getComputedStyle(p), b=p.getBoundingClientRect();
                if (['hidden','clip'].includes(s.overflowX) && (r.left<b.left-1 || r.right>b.right+1)) return false;
                if (['hidden','clip'].includes(s.overflowY) && (r.top<b.top-1 || r.bottom>b.bottom+1)) return false;
              }
            }
            blocks.push({node,rects});
          }
          return blocks.every((a,i)=>blocks.slice(i+1).every(b=>
            a.node.contains(b.node) || b.node.contains(a.node) || a.rects.every(x=>b.rects.every(y=>
              Math.min(x.right,y.right)-Math.max(x.left,y.left)<=1 || Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)<=1))));
        }"""
            ),
        )
        check(
            label + " every visible text glyph fits; no empty-list zeros",
            page.locator("main").evaluate("""root => {
          const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
          const rectangles=[];
          for (let node=walker.nextNode();node;node=walker.nextNode()) {
            const parent=node.parentElement;
            if (!node.textContent.trim() || !parent.checkVisibility() || parent.closest('.projection-sr-only,select')) continue;
            if (node.textContent.trim()==='0') return false;
            const range=document.createRange();range.selectNodeContents(node);
            const rs=[...range.getClientRects()].filter(r=>r.width && r.height);
            for(const r of rs) {
              if(r.left < -1 || r.right > innerWidth+1) return false;
              for(let p=parent;p;p=p.parentElement) {
                const s=getComputedStyle(p),b=p.getBoundingClientRect();
                if(['hidden','clip'].includes(s.overflowX) && (r.left<b.left-1 || r.right>b.right+1)) return false;
                if(['hidden','clip'].includes(s.overflowY) && (r.top<b.top-1 || r.bottom>b.bottom+1)) return false;
              }
            }
            rectangles.push(rs);
          }
          return rectangles.every((a,i)=>rectangles.slice(i+1).every(b=>a.every(x=>b.every(y=>
            Math.min(x.right,y.right)-Math.max(x.left,y.left)<=1 || Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)<=1))));
        }"""),
        )

    def capture(page, path, native=False):
        page.evaluate("scrollTo(0,0)")
        if not native:
            page.screenshot(path=str(path), full_page=True)
            return
        session = page.context.new_cdp_session(page)
        try:
            box = session.send("Page.getLayoutMetrics")["contentSize"]
            data = base64.b64decode(
                session.send(
                    "Page.captureScreenshot",
                    {
                        "format": "png",
                        "captureBeyondViewport": True,
                        "clip": {
                            "x": 0,
                            "y": 0,
                            "width": box["width"],
                            "height": box["height"],
                            "scale": 1,
                        },
                    },
                )["data"]
            )
            check(
                "native screenshot physical width",
                struct.unpack(">I", data[16:20])[0] == int(box["width"]),
            )
            path.write_bytes(data)
        finally:
            session.detach()

    def run(page, label, native=False):
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "dialog",
            lambda dialog: (
                errors.append("unexpected executable dialog"),
                dialog.dismiss(),
            ),
        )
        directory_url = ORIGIN + base + "/projected-coaches/"
        page.goto(directory_url, wait_until="networkidle")
        check(
            label + " generated directory count",
            page.locator("[data-projected-coach]").count() == len(coaches),
        )
        check(
            label + " no false canonical",
            page.locator("link[rel=canonical]").count() == 0,
        )
        check(
            label + " noindex",
            "noindex" in page.locator("meta[name=robots]").get_attribute("content"),
        )
        check(
            label + " portraits loaded",
            page.locator("main img").evaluate_all(
                "nodes=>nodes.every(i=>i.complete && i.naturalWidth>0)"
            ),
        )
        category = page.locator('[name="category"]')
        topic = page.locator('[name="topic"]')
        category.focus()
        page.keyboard.press("Tab")
        check(
            label + " native keyboard select",
            topic.evaluate("e=>e===document.activeElement"),
        )
        page.keyboard.press("Shift+Tab")
        check(
            label + " visible keyboard focus",
            category.evaluate(
                "e=>e.matches(':focus-visible') && getComputedStyle(e).outlineStyle!=='none'"
            ),
        )
        for cat in (
            "",
            "personalentwicklung",
            "persoenlichkeitsentwicklung",
            "karrierecoaching",
        ):
            category.select_option(cat)
            for selected in (
                "",
                *sorted({t["name"] for c in coaches for t in c["topics"]}),
            ):
                topic.select_option(selected)
                expected = sum(
                    (not cat and not selected)
                    or any(
                        (not cat or cat in t["categories"])
                        and (not selected or selected == t["name"])
                        for t in c["topics"]
                    )
                    for c in coaches
                )
                check(
                    label + f" intersection filter {cat}/{selected}",
                    page.locator("[data-projected-coach]:visible").count() == expected,
                )
                check(
                    label + " live count",
                    page.locator("[data-results-status]").inner_text()
                    == f"{expected} Coach-Profile",
                )
                check(
                    label + " empty state",
                    page.locator("[data-empty]").is_visible() == (expected == 0),
                )
        category.select_option("")
        topic.select_option("")
        fit(page, label + " directory")
        capture(page, out / f"directory-{label}.png", native)
        if coaches:
            link = page.locator("[data-projected-coach] a").first
            link.focus()
            page.keyboard.press("Enter")
            page.wait_for_url(
                ORIGIN
                + base
                + "/projected-coaches/"
                + coaches[0]["profile_path"].split("/")[2]
                + "/"
            )
            check(
                label + " keyboard profile navigation",
                page.locator("[data-projection-profile]").count() == 1,
            )
        for coach in coaches:
            slug = coach["profile_path"].split("/")[2]
            page.goto(
                ORIGIN + base + f"/projected-coaches/{slug}/", wait_until="networkidle"
            )
            check(
                label + slug + " identity",
                page.locator("h1").inner_text()
                == coach["display_name"]
                + (", " + coach["academic_suffix"] if coach["academic_suffix"] else ""),
            )
            check(
                label + slug + " families",
                page.locator("[data-family]").count()
                == len(coach.get("offering_families", [])),
            )
            formats = coach["offerings"] + [
                f
                for family in coach.get("offering_families", [])
                for f in family["formats"]
            ]
            check(
                label + slug + " formats not duplicated",
                page.locator("[data-offering]").count() == len(formats),
            )
            variants = sum(len(o.get("variants", [])) for o in formats) + sum(
                len(f["variants"]) for f in coach.get("offering_families", [])
            )
            check(
                label + slug + " variants stay subordinate",
                page.locator("[data-variant]").count() == variants,
            )
            check(
                label + slug + " qualifications",
                page.locator("[data-qualifications] > li").count()
                == len(coach.get("qualifications", [])),
            )
            check(
                label + slug + " nonbookable boundary",
                page.locator("[data-nonbookable]").count()
                == sum(o.get("bookable") is False for o in formats),
            )
            if coach["assets"]:
                check(
                    label + slug + " exact portrait reference",
                    page.locator("main img").get_attribute("src")
                    == base + "/" + coach["assets"][0]["reference"],
                )
                check(
                    label + slug + " portrait decoded",
                    page.locator("main img").evaluate(
                        "i=>i.complete && i.naturalWidth>0"
                    ),
                )
            else:
                check(
                    label + slug + " missing portrait is not invented",
                    page.locator("main img").count() == 0
                    and page.locator(".projection-monogram[role=img]").count() == 1,
                )
            text = " ".join(page.locator("main").inner_text().split())
            expected_text = [
                coach["short_intro"],
                coach["description"],
                coach["professional_background"],
                *coach["competencies"],
                *coach["target_groups"],
            ]
            expected_text += [r["label"] for r in coach.get("roles", [])]
            expected_text += [q["label"] for q in coach.get("qualifications", [])]
            expected_text += [t["name"] for t in coach["topics"]]
            expected_text += [o["title"] for o in formats]
            expected_text += [o.get("description") for o in formats]
            expected_text += [
                v["title"] for o in formats for v in o.get("variants", [])
            ]
            expected_text += [f["title"] for f in coach.get("offering_families", [])]
            boundaries = (
                coach.get("boundaries", [])
                + [
                    b
                    for f in coach.get("offering_families", [])
                    for b in f["boundaries"]
                ]
                + [b for o in formats for b in o.get("boundaries", [])]
            )
            expected_text += [b["text"] for b in boundaries]
            presentation = coach.get("presentation", {})
            expected_text += [presentation.get("quote"), presentation.get("teaser")]
            expected_text += [
                t
                for s in presentation.get("sections", [])
                for t in s["headings"] + s["paragraphs"]
            ]
            for index, value in enumerate(filter(None, expected_text)):
                check(
                    label + slug + f" escaped public text {index}",
                    " ".join(value.split()) in text,
                )
            check(
                label + slug + " no executable public markup",
                page.locator(
                    "main script, main iframe, main [onerror], main [onclick]"
                ).count()
                == 0,
            )
            check(
                label + slug + " XSS sentinel never executed",
                page.evaluate("typeof window.__coachProjectionXss==='undefined'"),
            )
            try:
                fit(page, label + slug)
            except AssertionError:
                capture(page, out / f"failure-{slug}-{label}.png", native)
                diagnostic = page.locator(
                    "main h1,main h2,main h3,main h4,main p,main dt,main dd,main label,main li > strong"
                ).evaluate_all(
                    """nodes=>{
                  const blocks=nodes.filter(n=>n.checkVisibility()).map(n=>{const r=document.createRange();r.selectNodeContents(n);return {text:n.textContent,rs:[...r.getClientRects()]};});
                  const failures=[];
                  for(const [i,a] of blocks.entries())for(const b of blocks.slice(i+1))for(const x of a.rs)for(const y of b.rs)
                    if(Math.min(x.right,y.right)-Math.max(x.left,y.left)>1 && Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)>1)failures.push([a.text,b.text,{a:x.toJSON(),b:y.toJSON()}]);
                  return failures;
                }"""
                )
                (out / "failure-geometry.json").write_text(
                    json.dumps(diagnostic, indent=2), encoding="utf-8"
                )
                raise
            capture(page, out / f"{slug}-{label}.png", native)
        check(label + " zero network or resource errors", not errors)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        try:
            for label, width in (("desktop", 1440), ("mobile-390", 390)):
                context = browser.new_context(
                    viewport={"width": width, "height": 1000},
                    reduced_motion="reduce",
                    service_workers="block",
                )
                try:
                    install(context)
                    run(context.new_page(), label)
                finally:
                    context.close()
        finally:
            browser.close()
        with tempfile.TemporaryDirectory(prefix="native-zoom-", dir=out) as folder:
            default = Path(folder) / "Default"
            default.mkdir()
            level = math.log(2) / math.log(1.2)
            (default / "Preferences").write_text(
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
                service_workers="block",
            )
            try:
                install(context)
                page = context.pages[0]
                page.goto(
                    ORIGIN + base + "/projected-coaches/", wait_until="networkidle"
                )
                metrics = page.evaluate(
                    "({width:innerWidth,dpr:devicePixelRatio,scale:visualViewport.scale,cssZoom:getComputedStyle(document.documentElement).zoom})"
                )
                check(
                    "actual native 200 percent, not CSS or viewport scale",
                    abs(metrics["dpr"] - 2) < 0.05
                    and 600 < metrics["width"] < 800
                    and metrics["scale"] == 1
                    and metrics["cssZoom"] == "1",
                )
                run(page, "native-200", native=True)
            finally:
                context.close()
    check(
        "tested artifact stayed immutable",
        hashlib.sha256(fixture.read_bytes()).hexdigest() == fixture_hash,
    )
    html_hashes = {
        str(path.relative_to(dist))
        .replace("\\", "/"): hashlib.sha256(path.read_bytes())
        .hexdigest()
        for path in (dist / "projected-coaches").rglob("*.html")
    }
    (out / "acceptance.json").write_text(
        json.dumps(
            {
                "checks": checks,
                "native_zoom": metrics,
                "errors": errors,
                "fixture_sha256": fixture_hash,
                "projected_html_sha256": html_hashes,
                "screenshots_sha256": {
                    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in out.glob("*.png")
                },
                "requests_fulfilled_from_disk": len(requests),
                "network_fetches": 0,
                "server_started": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"COACH_PROJECTION_BROWSER=PASS CHECKS={len(checks)} NETWORK=0 SERVER=NONE")


if __name__ == "__main__":
    main()
