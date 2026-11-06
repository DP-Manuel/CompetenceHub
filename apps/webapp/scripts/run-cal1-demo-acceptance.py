"""Actual browser/HTTPS acceptance of the isolated local synthetic Calendar demo."""
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
import hashlib
import base64
import argparse
import os
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from zoneinfo import ZoneInfo

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.cal1_demo_app import create_demo_app
from scripts.cal1_public_build import build_public_calendar
from scripts.browser_acceptance_app import COACH_EMAIL, EMPTY_COACH_EMAIL, REVIEWER_EMAIL, INTERNAL_EMAIL

spec = importlib.util.spec_from_file_location("cal1_qa", ROOT / "scripts/run-cal1-browser-acceptance.py")
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
EVIDENCE = ROOT.parents[1] / "release-artifacts/cal1-cal01-integration-20261106"
PUBLIC = "/api/v1/calendar/offers"
OFFERS = "/api/v1/portal/calendar/offers"


def production_manifest():
    folder = ROOT.parent / "website/dist"
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file()}


def geometry(page, checks, label):
    checks.check(label + " no horizontal overflow", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
    checks.check(label + " actual text ranges fit viewport and text containers", page.evaluate("""() => {
      const nodes = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (nodes.nextNode()) {
        const n = nodes.currentNode, e = n.parentElement;
        if (!n.textContent.trim() || !e || ['SCRIPT','STYLE','OPTION','NOSCRIPT'].includes(e.tagName)
            || !e.getClientRects().length || e.closest('[hidden]') || getComputedStyle(e).visibility === 'hidden'
            || e.closest('.skip-link')) continue;
        const range = document.createRange(); range.selectNodeContents(n);
        const parent = e.getBoundingClientRect();
        for (const r of range.getClientRects()) {
          if (r.width > 0 && (r.left < -1 || r.right > innerWidth + 1 || r.left < parent.left - 1 || r.right > parent.right + 1)) return false;
        }
      }
      return true;
    }"""))


def public_load(page, base, path="/demo/"):
    page.goto(base + path, wait_until="networkidle")
    expect(page.locator("#month-label")).not_to_have_text("")
    expect(page.locator("#loading")).to_be_hidden()
    expect(page.locator("#error")).to_be_hidden()


def screenshot(page, path, label):
    if "native-200" in label:
        # Capture the real browser surface. Playwright's CSS-sized clip loses
        # half the bitmap at Chromium's native (not emulated) zoom level.
        cdp = page.context.new_cdp_session(page)
        try:
            result = cdp.send("Page.captureScreenshot", {"format": "png", "fromSurface": True,
                "captureBeyondViewport": False})
            nonblank = page.evaluate("""async data => {
              const img = await createImageBitmap(new Blob([Uint8Array.from(atob(data), c => c.charCodeAt(0))], {type:'image/png'}));
              const canvas = document.createElement('canvas'); canvas.width=img.width; canvas.height=img.height;
              const ctx=canvas.getContext('2d'); ctx.drawImage(img,0,0); img.close();
              const pixels=ctx.getImageData(0,0,canvas.width,canvas.height).data;
              let visible=0; for(let i=0;i<pixels.length;i+=4) if(pixels[i]<220 || pixels[i+1]<220 || pixels[i+2]<220) visible++;
              return visible>1280;
            }""", result["data"])
            if not nonblank:
                raise AssertionError("Native zoom screenshot has no visible content")
            path.write_bytes(base64.b64decode(result["data"]))
        finally:
            cdp.detach()
    else:
        page.screenshot(path=str(path), full_page=True)


def review(page, title, outcome, note=None):
    qa.review_card(page, title).get_by_role("button", name="Angebot prüfen").click()
    page.get_by_label("Änderungen anfordern" if outcome == "changes_requested" else "Veröffentlichen", exact=True).check()
    if note:
        page.locator("#calendar-review-note").fill(note)
    with qa.calendar_refresh(page, reviewing=True):
        page.get_by_role("button", name="Entscheidung speichern", exact=True).click()
        page.locator("#calendar-review-dialog").wait_for(state="hidden")


def exercise(browser, base, checks, report):
    coach_context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000})
    coach = coach_context.new_page()
    qa.login(coach, base, COACH_EMAIL)
    expect(coach.locator("#coach-calendar-loading")).to_be_hidden()
    checks.check("Coach only own four seeded offers", len(qa.api_offers(coach)) == 4)
    checks.check("Coach cannot see reviewer area", coach.locator("#review-calendar-workspace").count() == 0)
    checks.check("Synthetic banner on actual Portal", coach.get_by_text("DEMO · Nur synthetische Daten", exact=True).is_visible())
    coach.locator("#open-calendar-offer-dialog").click()
    coach.get_by_role("button", name="Demo-Werte einsetzen").click()
    coach.locator("#calendar-ends-at").evaluate("e => {const d = new Date(e.value); d.setDate(d.getDate()+1); e.value = new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,16);}")
    expect(coach.locator("#calendar-title")).to_have_value("DEMO: Teamworkshop")
    checks.check("Demo form only populates values, no draft yet", len(qa.api_offers(coach)) == 4)
    checks.check("Capacity and threshold are separate fields", coach.locator("#calendar-capacity").input_value() == "12" and coach.locator("#calendar-review-threshold").input_value() == "6")
    geometry(coach, checks, "Desktop create dialog")
    with qa.calendar_refresh(coach):
        coach.locator("#save-calendar-offer").click()
        coach.locator("#calendar-offer-dialog").wait_for(state="hidden")
    title = "DEMO: Teamworkshop"
    item = next(i for i in qa.api_offers(coach) if i["title"] == title)
    offer_id = item["id"]
    checks.check("New offer saved as draft", item["workflow_status"] == "draft" and item["revision_number"] == 1)
    checks.check("Draft public detail is 404", coach_context.request.get(base + PUBLIC + "/" + offer_id).status == 404)

    # Native stale edit: same synthetic identity, independent sessions and ETags.
    stale_context = browser.new_context(ignore_https_errors=True)
    stale = stale_context.new_page(); qa.login(stale, base, COACH_EMAIL)
    qa.card(coach, title).get_by_role("button", name="Entwurf bearbeiten").click()
    qa.card(stale, title).get_by_role("button", name="Entwurf bearbeiten").click()
    coach.locator("#calendar-summary").fill("DEMO: abgestimmter Workshop")
    with qa.calendar_refresh(coach):
        coach.locator("#save-calendar-offer").click()
        coach.locator("#calendar-offer-dialog").wait_for(state="hidden")
    stale.locator("#calendar-summary").fill("STALE MUST NOT WIN")
    stale.locator("#save-calendar-offer").click()
    expect(stale.locator("#calendar-offer-error")).to_be_visible()
    checks.check("Real API stale 409 retains dialog and retry is explicit", stale.locator("#reload-calendar-offer").is_visible())
    stale.locator("#reload-calendar-offer").click()
    expect(stale.locator("#calendar-summary")).to_have_value("DEMO: abgestimmter Workshop")
    stale.keyboard.press("Escape"); stale_context.close()
    checks.check("In-memory API prevented stale overwrite", qa.api_offer_detail(coach, offer_id)["current_revision"]["summary"] == "DEMO: abgestimmter Workshop")
    qa.submit_offer(coach, title)
    checks.check("In review not directly editable", qa.card(coach, title).get_by_role("button", name="Entwurf bearbeiten").count() == 0)
    checks.check("In review may be withdrawn", qa.card(coach, title).get_by_role("button", name="Angebot zurückziehen").is_visible())

    reviewer_context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000})
    reviewer = reviewer_context.new_page(); qa.login(reviewer, base, REVIEWER_EMAIL)
    expect(qa.review_card(reviewer, title)).to_be_visible()
    checks.check("Reviewer scope not identity-coded, no Coach editor", reviewer.locator("#coach-calendar-workspace").count() == 0)
    review(reviewer, title, "changes_requested", "PRIVATE: Demo-Ort genauer beschreiben")
    coach.reload(); expect(qa.card(coach, title)).to_contain_text("Änderung angefordert")
    qa.card(coach, title).get_by_role("button", name="Neue Revision bearbeiten").click()
    expect(coach.locator("#calendar-review-feedback")).to_contain_text("Demo-Ort")
    coach.locator("#calendar-location").fill("Demo-Raum A (rein fiktiv)")
    with qa.calendar_refresh(coach):
        coach.locator("#save-calendar-offer").click()
        coach.locator("#calendar-offer-dialog").wait_for(state="hidden")
    checks.check("Change request creates revision two", next(i for i in qa.api_offers(coach) if i["id"] == offer_id)["revision_number"] == 2)
    qa.submit_offer(coach, title)
    reviewer.reload(); expect(qa.review_card(reviewer, title)).to_be_visible()
    public_context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000})
    cal01 = public_context.new_page(); public_load(cal01, base, "/demo/public/")
    checks.check("CAL-0.1 uses existing Astro component but no static-data initializer", cal01.locator(".calendar-preview").count() == 1 and cal01.locator("[data-calendar-preview]").count() == 0)
    checks.check("In-review offer is absent in CAL-0.1", cal01.locator(f'[data-offer="{offer_id}"]').count() == 0)
    review(reviewer, title, "published")
    expect(cal01.locator(f'[data-offer="{offer_id}"]')).to_have_count(2, timeout=15000)
    checks.check("Reviewer publication automatically appears on both occupied CAL-0.1 days without reload", cal01.locator(f'[data-offer="{offer_id}"]').count() == 2)
    cal01.locator(f'[data-offer="{offer_id}"]').last.focus(); cal01.keyboard.press("Enter")
    expect(cal01.locator("#detail-title")).to_have_text(title)
    checks.check("CAL-0.1 keyboard segment opens same public detail", cal01.locator("#detail").get_attribute("data-event-id") == offer_id)
    public = public_context.new_page(); public_load(public, base)
    published = public_context.request.get(base + PUBLIC + "/" + offer_id)
    checks.check("Anonymous real API receives reviewed revision", published.status == 200 and published.json()["public_location"] == "Demo-Raum A (rein fiktiv)")
    projection = published.json()
    checks.check("Public DTO excludes internal threshold, review, user, revision and lock", not any(k in projection for k in ["review_threshold", "workflow_status", "current_revision", "lock_version", "review_decision", "coach_id"]) and "PRIVATE:" not in published.text())
    # Navigate to this actual DTO's month, not a separately invented static dataset.
    for _ in range(4):
        if public.get_by_role("button", name=title, exact=False).count(): break
        public.locator("#previous" if public.locator("#previous").is_enabled() else "#next").click()
    public.locator(f'[data-offer="{offer_id}"]').first.click()
    checks.check("CAL-1 and CAL-0.1 share identical multiday segments", public.locator(f'[data-offer="{offer_id}"]').evaluate_all("es => es.map(e=>[e.dataset.date,e.dataset.segmentRole,e.getAttribute('aria-label')])") == cal01.locator(f'[data-offer="{offer_id}"]').evaluate_all("es => es.map(e=>[e.dataset.date,e.dataset.segmentRole,e.getAttribute('aria-label')])"))
    expect(public.locator("#detail-title")).to_have_text(title)
    checks.check("Public calendar is actually bridged to submitted offer", title in public.locator("#detail").inner_text())
    checks.check("No invented free-seat count", "Höchstens 12" in public.locator("#meta").inner_text() and "Kein Stand freier Plätze" in public.locator("#meta").inner_text())
    profile = public.locator("#coach").get_attribute("href")
    checks.check("Profile is explicitly synthetic, not a real Coach association", profile == "/coaches/demo-coach-a/" and "Fiktive Person" in public_context.request.get(base + profile).text())
    writes = []
    public.on("request", lambda r: writes.append(r.url) if r.method not in {"GET", "HEAD"} else None)
    public.locator("#seats").fill("2"); public.get_by_role("button", name="Anfrage simulieren", exact=True).click()
    expect(public.locator("#request-status")).to_contain_text("Nichts gesendet oder reserviert")
    checks.check("Request simulation causes zero network writes", writes == [])
    geometry(public, checks, "Desktop public calendar")
    public.screenshot(path=str(EVIDENCE / "desktop-public.png"), full_page=True)

    coach.reload(); expect(qa.card(coach, title)).to_contain_text("Veröffentlicht")
    cal01.locator("#seats").fill("3")
    qa.card(coach, title).get_by_role("button", name="Neue Revision bearbeiten").click()
    coach.locator("#calendar-title").fill("PRIVATE: unpublished replacement")
    with qa.calendar_refresh(coach):
        coach.locator("#save-calendar-offer").click()
        coach.locator("#calendar-offer-dialog").wait_for(state="hidden")
    checks.check("Published version remains unchanged during replacement draft", public_context.request.get(base + PUBLIC + "/" + offer_id).json()["title"] == title)
    cal01.wait_for_timeout(5500)
    checks.check("Automatic refresh does not leak replacement or lose focused request input", "PRIVATE:" not in cal01.locator("main").inner_text() and cal01.locator("#detail").is_visible() and cal01.locator("#seats").input_value() == "3" and cal01.locator("#seats").evaluate("e => e === document.activeElement"))
    coach.goto(base + "/demo/history"); expect(coach.locator("#history-list")).to_contain_text("Revision 3")
    checks.check("Protected status history is actually available", "Änderung angefordert" in coach.locator("#history-list").inner_text() and "Veröffentlicht" in coach.locator("#history-list").inner_text())
    checks.check("Anonymous history API denied", public_context.request.get(base + "/demo/api/history").status == 401)
    coach.goto(base + "/portal/"); expect(qa.card(coach, "PRIVATE: unpublished replacement")).to_be_visible()
    with qa.calendar_refresh(coach):
        qa.card(coach, "PRIVATE: unpublished replacement").get_by_role("button", name="Angebot zurückziehen").click()
    checks.check("Withdrawal removes actual public projection immediately", public_context.request.get(base + PUBLIC + "/" + offer_id).status == 404)
    expect(cal01.locator(f'[data-offer="{offer_id}"]')).to_have_count(0, timeout=15000)
    checks.check("Automatic withdrawal removes CAL-0.1 segments and stale details", cal01.locator("#detail").is_hidden())
    coach_context.close(); reviewer_context.close(); public_context.close()

    for email, denied in [(EMPTY_COACH_EMAIL, 404), (INTERNAL_EMAIL, 403), (REVIEWER_EMAIL, 200), (COACH_EMAIL, 200)]:
        ctx = browser.new_context(ignore_https_errors=True); page = ctx.new_page(); qa.login(page, base, email)
        response = ctx.request.get(base + OFFERS + "/" + offer_id)
        checks.check(f"API role/ownership read {email}", response.status == denied)
        if email == INTERNAL_EMAIL:
            checks.check("Internal has no review permission", ctx.request.get(base + "/api/v1/portal/calendar/review-queue").status == 403)
        if email in {EMPTY_COACH_EMAIL, REVIEWER_EMAIL}:
            # Separate context, so CSRF rotation cannot stale the demonstration UI.
            csrf = ctx.request.post(base + "/api/v1/portal/access/session/csrf", headers={"Origin": base}).headers["x-csrf-token"]
            response = ctx.request.post(base + OFFERS + "/" + offer_id + "/submit",
                headers={"Origin": base, "X-CSRF-Token": csrf, "If-Match": '"v1"'}, data={})
            checks.check(f"API role/ownership write denied {email}", response.status in {403, 404})
        if email == COACH_EMAIL:
            csrf = ctx.request.post(base + "/api/v1/portal/access/session/csrf", headers={"Origin": base}).headers["x-csrf-token"]
            response = ctx.request.post(base + OFFERS + "/" + offer_id + "/review-decisions",
                headers={"Origin": base, "X-CSRF-Token": csrf, "If-Match": '"v1"'}, data={"outcome": "published", "note": None})
            checks.check("Coach cannot self-publish through actual API", response.status == 403)
        ctx.close()


def responsive(page, base, checks, label, path="/demo/"):
    public_load(page, base, path)
    checks.check(label + " two simultaneous real synthetic API items in same day", page.locator(".day").filter(has=page.locator("button")).filter(has_text="Parallelworkshop").locator("button").count() == 2)
    page.locator("#format").select_option("online")
    expect(page.locator("#result-count")).to_have_text("1 freigegebene Demo-Termine")
    checks.check(label + " format filter", page.locator("[data-offer]").count() == 1)
    page.locator("#format").select_option("praesenz")
    expect(page.locator("#empty")).to_be_visible()
    checks.check(label + " empty filtered state", page.locator("[data-offer]").count() == 0)
    page.locator("#format").select_option("")
    page.locator("#topic").select_option(index=1)
    checks.check(label + " topic filter based on approved public DTOs", page.locator("[data-offer]").count() == 2)
    page.locator("[data-offer]").first.focus(); page.keyboard.press("Enter")
    expect(page.locator("#detail")).to_be_focused()
    checks.check(label + " keyboard event activation and focus", page.locator("#detail").is_visible())
    page.keyboard.press("Tab"); expect(page.locator("#coach")).to_be_focused()
    outline = page.locator("#coach").evaluate("e => getComputedStyle(e).outlineStyle")
    checks.check(label + " keyboard visible focus", outline != "none")
    page.locator("#format").select_option("praesenz")
    checks.check(label + " changing filter clears selected out-of-filter detail", page.locator("#detail").is_hidden())
    page.locator("#format").select_option("")
    page.locator("[data-offer]").first.focus(); page.keyboard.press("Enter")
    geometry(page, checks, label + " public")
    # Chromium full-page capture at native browser zoom can crop the bitmap;
    # keep the real viewport for that evidence rather than changing layout/zoom.
    screenshot(page, EVIDENCE / (label + "-public.png"), label)
    if path == "/demo/public/":
        checks.check(label + " reduced motion respected", page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"))
        return
    qa.login(page, base, COACH_EMAIL)
    expect(page.locator("#coach-calendar-loading")).to_be_hidden()
    page.locator("#open-calendar-offer-dialog").click()
    expect(page.locator("#calendar-title")).to_be_focused()
    page.get_by_role("button", name="Demo-Werte einsetzen").click()
    geometry(page, checks, label + " form")
    checks.check(label + " native dialog and form controls stay within viewport", page.locator("#calendar-offer-dialog").evaluate("e => e.getBoundingClientRect().right <= innerWidth + 1 && e.scrollWidth <= e.clientWidth + 1"))
    screenshot(page, EVIDENCE / (label + "-form.png"), label)
    qa.tab_to_button(page, "Entwurf anlegen")
    checks.check(label + " save action reachable by keyboard and scrolled into view", page.evaluate("document.activeElement.getBoundingClientRect().bottom <= innerHeight + 1"))
    page.once("dialog", lambda dialog: dialog.accept())
    page.keyboard.press("Escape")
    checks.check(label + " Escape closes native dialog", page.locator("#calendar-offer-dialog").is_hidden())
    checks.check(label + " reduced motion respected", page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"))


def reviewer_responsive(page, base, checks, label):
    # The persistent native-zoom profile previously hosted the Coach scenario.
    # Test the Reviewer with a fresh fixture session, never a shared identity.
    page.context.clear_cookies()
    qa.login(page,base,REVIEWER_EMAIL)
    expect(page.locator("#review-calendar-list .calendar-card").first).to_be_visible()
    page.locator("#review-calendar-list .calendar-card").first.get_by_role("button",name="Angebot prüfen").click()
    page.get_by_label("Änderungen anfordern",exact=True).check()
    page.locator("#calendar-review-note").fill("Unveröffentlichte Prüfeingabe")
    geometry(page,checks,label+" reviewer")
    page.once("dialog",lambda dialog:dialog.dismiss()); page.keyboard.press("Escape")
    checks.check(label+" reviewer dirty cancel preserves note",page.locator("#calendar-review-dialog").is_visible() and page.locator("#calendar-review-note").input_value()=="Unveröffentlichte Prüfeingabe")
    screenshot(page,EVIDENCE/(label+"-reviewer.png"),label)
    page.once("dialog",lambda dialog:dialog.accept()); page.get_by_role("button",name="Abbrechen",exact=True).click()
    checks.check(label+" reviewer discard closes without publication",page.locator("#calendar-review-dialog").is_hidden())


def states(browser, base, checks, path="/demo/"):
    ctx = browser.new_context(ignore_https_errors=True); page = ctx.new_page()
    held = []
    page.route("**/demo/api/public-calendar?*", lambda route: held.append(route))
    page.goto(base + path, wait_until="domcontentloaded")
    expect(page.locator("#loading")).to_be_visible()
    checks.check("Public loading state and disabled reload", page.locator("#reload").is_disabled())
    page.wait_for_timeout(100)
    held[0].fulfill(status=503, content_type="application/json", body='{"code":"portal_unavailable"}')
    expect(page.locator("#error")).to_be_focused()
    checks.check("Public error clears stale events and detail", page.locator("[data-offer]").count() == 0 and page.locator("#detail").is_hidden())
    page.unroute("**/demo/api/public-calendar?*")
    page.locator("#reload").click(); expect(page.locator("[data-offer]")).to_have_count(2)
    checks.check("Public error recovery without page restart", page.locator("#error").is_hidden())
    page.route("**/demo/api/public-calendar?*", lambda route: route.fulfill(status=200, content_type="application/json", body='{"items":[],"next_cursor":null}'))
    page.locator("#reload").click(); expect(page.locator("#empty")).to_be_visible()
    checks.check("Empty API data never fabricated", page.locator("[data-offer]").count() == 0)
    page.unroute("**/demo/api/public-calendar?*")
    if path == "/demo/public/":
        ctx.close()
        return
    qa.login(page, base, COACH_EMAIL)
    page.route("**/api/v1/portal/calendar/offers", lambda route: route.fulfill(status=503, content_type="application/json", body='{"code":"portal_unavailable"}'))
    page.reload(); expect(page.locator("#coach-calendar-error")).to_be_visible()
    checks.check("Existing Coach error state", page.locator("#coach-calendar-error").inner_text().strip() != "")
    page.unroute("**/api/v1/portal/calendar/offers")
    page.reload(); expect(page.locator("#coach-calendar-loading")).to_be_hidden()
    ctx.close()
    ctx = browser.new_context(ignore_https_errors=True); page = ctx.new_page()
    held = []
    page.route("**/api/v1/portal/calendar/review-queue", lambda route: held.append(route))
    qa.login(page, base, REVIEWER_EMAIL)
    expect(page.locator("#review-calendar-loading")).to_be_visible()
    checks.check("Existing Reviewer loading state", page.locator("#review-calendar-loading").is_visible())
    page.wait_for_timeout(100)
    held[0].fulfill(status=200, content_type="application/json", body='{"items":[]}')
    expect(page.locator("#review-calendar-empty")).to_be_visible()
    checks.check("Existing Reviewer empty state (injected read response)", page.locator("#review-calendar-list .calendar-card").count() == 0)
    page.unroute("**/api/v1/portal/calendar/review-queue")
    page.route("**/api/v1/portal/calendar/review-queue", lambda route: route.fulfill(status=503, content_type="application/json", body='{"code":"portal_unavailable"}'))
    page.reload(); expect(page.locator("#review-calendar-error")).to_be_visible()
    checks.check("Existing Reviewer error state (injected service failure)", page.locator("#review-calendar-error").inner_text().strip() != "")
    page.unroute("**/api/v1/portal/calendar/review-queue")
    page.reload(); expect(page.locator("#review-calendar-loading")).to_be_hidden()
    ctx.close()


def multiday_data():
    def item(key, title, start, end):
        return {"id": key, "title": "DEMO: " + title, "summary": "Synthetischer Darstellungstest",
            "starts_at": start, "ends_at": end, "time_zone": "Europe/Berlin", "format": "praesenz",
            "capacity": 12, "public_location": "Demo-Raum", "price_display_text": "Demo: nach Abstimmung",
            "decision_deadline": "2026-11-20T10:00:00+01:00",
            "topic": {"id": "3d362761-18b6-4360-b9ca-497dce38ffbb", "name": "Demo-Thema"},
            "coach": {"display_name": "Demo-Coach A", "profile_path": "/coaches/demo-coach-a/"}}
    return [
        item("reported", "Workshop 28.–29. November", "2026-11-28T17:18+01:00", "2026-11-29T17:18+01:00"),
        item("long", "Vier Tage", "2026-11-27T10:00+01:00", "2026-11-30T16:00+01:00"),
        item("midnight", "Ende Mitternacht", "2026-11-29T22:00+01:00", "2026-11-30T00:00+01:00"),
        item("month", "Monatswechsel", "2026-11-30T22:00+01:00", "2026-12-02T03:00+01:00"),
        item("year", "Jahreswechsel", "2026-12-31T22:00+01:00", "2027-01-02T03:00+01:00"),
        item("parallel", "Paralleltermin", "2026-11-28T19:00+01:00", "2026-11-29T09:00+01:00"),
        item("single", "Eintägig", "2026-11-28T10:00+01:00", "2026-11-28T11:00+01:00"),
        item("year-midnight", "Jahresende Mitternacht", "2026-12-31T22:00+01:00", "2027-01-01T00:00+01:00"),
    ]


def multiday(page, base, checks, label, path="/demo/"):
    # Explicit read-response injection tests the renderer, not new API semantics.
    # Fake browser clock keeps the named regression deterministic after November.
    page.clock.install(time=datetime(2026, 11, 6, 12, tzinfo=timezone.utc))
    writes = []
    page.on("request", lambda request: writes.append(request.method) if request.method not in {"GET", "HEAD"} else None)
    payload = json.dumps({"items": multiday_data(), "next_cursor": None})
    handler = lambda route: route.fulfill(status=200, content_type="application/json", body=payload)
    page.route("**/demo/api/public-calendar?*", handler)
    try:
        public_load(page, base, path)
        expect(page.locator("#month-label")).to_have_text("November 2026")
        reported = page.locator('button[data-offer="reported"]')
        checks.check(label + " reported interval occupies exactly Nov28 and Nov29", reported.count() == 2
            and reported.evaluate_all("nodes => nodes.map(n => n.dataset.date)") == ["2026-11-28", "2026-11-29"])
        checks.check(label + " begin and end retain 17:18", reported.nth(0).locator(".event-segment__phase").inner_text() == "Beginn 17:18 Uhr"
            and reported.nth(1).locator(".event-segment__phase").inner_text() == "Ende 17:18 Uhr")
        for button in reported.all():
            button.focus(); page.keyboard.press("Enter")
            expect(page.locator("#detail")).to_be_focused()
            checks.check(label + " every segment opens identical event detail", page.locator("#detail").get_attribute("data-event-id") == "reported"
                and page.locator("#detail-title").inner_text() == "DEMO: Workshop 28.–29. November")
        checks.check(label + " segment accessible name has topic date phase and full range", all(
            text in reported.first.get_attribute("aria-label") for text in ("Demo-Thema", "28. November 2026", "Beginn 17:18", "Gesamtzeitraum", "Europe/Berlin")))
        reported.first.focus()
        checks.check(label + " native button has accessible name and visible keyboard focus", page.get_by_role("button", name=reported.first.get_attribute("aria-label"), exact=True).count() == 1
            and reported.first.get_attribute("aria-controls") == "detail"
            and reported.first.evaluate("e => e === document.activeElement && getComputedStyle(e).outlineStyle !== 'none'"))
        long = page.locator('button[data-offer="long"]')
        checks.check(label + " four civil days cross week row without wrong phases", long.count() == 4
            and long.evaluate_all("nodes => nodes.map(n => n.dataset.segmentRole)") == ["start", "continue", "continue", "end"])
        checks.check(label + " Sunday to Monday is a meaningful band break", not long.nth(2).evaluate("e => e.classList.contains('is-connected-after')")
            and not long.nth(3).evaluate("e => e.classList.contains('is-connected-before')"))
        checks.check(label + " midnight excludes Nov30", page.locator('button[data-offer="midnight"]').count() == 1
            and page.locator('button[data-offer="midnight"]').get_attribute("data-date") == "2026-11-29"
            and "Folgetag" in page.locator('button[data-offer="midnight"]').inner_text())
        checks.check(label + " single day remains one segment", page.locator('button[data-offer="single"]').count() == 1)
        if label.endswith("desktop"):
            first, last = reported.nth(0).bounding_box(), reported.nth(1).bounding_box()
            checks.check("desktop turquoise band connects adjacent days in same lane", abs(first["y"] - last["y"]) < 1
                and abs(first["height"] - last["height"]) < 1 and abs(first["x"] + first["width"] - last["x"]) < 1.5)
            checks.check("desktop turquoise is visible and not only color-coded", reported.first.evaluate("e => getComputedStyle(e).backgroundColor === 'rgb(220, 239, 240)'")
                and "Beginn" in reported.first.inner_text() and "Ende" in reported.last.inner_text())
        checks.check(label + " all parallel buttons avoid geometric overlap", page.locator("#grid").evaluate("""root => {
            const rects = [...root.querySelectorAll('button')].map(e => e.getBoundingClientRect());
            return rects.every((a, i) => rects.slice(i+1).every(b =>
              Math.min(a.right,b.right)-Math.max(a.left,b.left) < 1 || Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top) < 1));
        }"""))
        geometry(page, checks, label + " multiday")
        if "native-200" in label:
            checks.check("multiday view actually uses native 200 percent", page.evaluate("devicePixelRatio === 2 && innerWidth > 600 && innerWidth < 800 && getComputedStyle(document.documentElement).zoom === '1'"))
        page.locator("#grid").evaluate("e => window.scrollTo(0,e.getBoundingClientRect().top+scrollY-20)")
        screenshot(page, EVIDENCE / (label + "-multiday.png"), label)
        page.locator("#next").click()
        checks.check(label + " December keeps month continuation and year start", page.locator('button[data-offer="month"]').count() == 2
            and page.locator('button[data-offer="month"]').first.get_attribute("data-segment-role") == "continue"
            and page.locator('button[data-offer="year"]').count() == 1)
        page.locator("#next").click()
        checks.check(label + " January keeps year continuation and excludes midnight end", page.locator('button[data-offer="year"]').count() == 2
            and page.locator('button[data-offer="year"]').first.get_attribute("data-segment-role") == "continue"
            and page.locator('button[data-offer="year-midnight"]').count() == 0)
        page.locator('button[data-offer="year"]').last.click()
        checks.check(label + " cross-month segment detail still has original record", page.locator("#detail").get_attribute("data-event-id") == "year")
        checks.check(label + " display-only test writes no data", not writes)
    finally:
        page.unroute("**/demo/api/public-calendar?*", handler)


def daylight_saving(browser, base, checks):
    for label, clock, start, end, expected in [
        ("spring", datetime(2026, 3, 1, tzinfo=timezone.utc), "2026-03-28T17:18+01:00", "2026-03-29T17:18+02:00", ["2026-03-28", "2026-03-29"]),
        ("autumn", datetime(2026, 10, 1, tzinfo=timezone.utc), "2026-10-24T17:18+02:00", "2026-10-25T17:18+01:00", ["2026-10-24", "2026-10-25"]),
    ]:
        ctx = browser.new_context(ignore_https_errors=True, timezone_id="America/Los_Angeles")
        try:
            page = ctx.new_page(); page.clock.install(time=clock)
            item = {**multiday_data()[0], "starts_at": start, "ends_at": end}
            page.route("**/demo/api/public-calendar?*", lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps({"items": [item], "next_cursor": None})))
            public_load(page, base)
            checks.check(label + " actual browser uses Berlin civil days not client timezone", page.locator('button[data-offer="reported"]').evaluate_all("nodes => nodes.map(n => n.dataset.date)") == expected)
            labels = page.locator('button[data-offer="reported"] .event-segment__phase').all_text_contents()
            expected_zones = ["(MEZ)", "(MESZ)"] if label == "spring" else ["(MESZ)", "(MEZ)"]
            checks.check(label + " DST labels distinguish seasonal time offsets", all(zone in value for zone, value in zip(expected_zones, labels)))
        finally: ctx.close()


def overlap_browser(new_context, observe, checks):
    def fixture(port):
        app = create_demo_app(port)
        repo = app.state.demo_repository
        original = next(d for d in repo._offers.values() if d.published_revision)
        now = app.state.clock().astimezone(ZoneInfo("Europe/Berlin"))
        first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        approved = replace(original.published_revision, draft=replace(original.published_revision.draft,
            title="DEMO: Bereits laufender Monatswechsel", starts_at=first - timedelta(hours=3),
            ends_at=now + timedelta(days=1)))
        repo._offers = {original.offer.id: replace(original, current_revision=approved, published_revision=approved)}
        return app

    with qa.synthetic_server(fixture) as base:
        context = new_context(ignore_https_errors=True)
        observe(context, base)
        try:
            for path in ("/demo/", "/demo/public/"):
                page = context.new_page()
                with page.expect_response(lambda r: "/demo/api/public-calendar?" in r.url) as response:
                    public_load(page, base, path)
                projection = response.value.json()["items"]
                checks.check(path + " actual month endpoint includes earlier-starting approved event", len(projection) == 1 and projection[0]["title"] == "DEMO: Bereits laufender Monatswechsel")
                buttons = page.locator("button[data-offer]")
                checks.check(path + " actual overlapping event starts visible month with continuation", buttons.first.get_attribute("data-segment-role") == "continue" and buttons.count() > 1)
                buttons.last.click()
                expect(page.locator("#detail-title")).to_have_text("DEMO: Bereits laufender Monatswechsel")
                checks.check(path + " overlap detail keeps original event identity", page.locator("#detail").get_attribute("data-event-id") == projection[0]["id"])
                page.close()
        finally:
            context.close()


def run(options):
    browser_options = ({"executable_path": str(options.browser_executable)} if options.browser_executable
                       else {"channel": "msedge"} if options.browser == "msedge" else {})
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    baseline = production_manifest()
    build_public_calendar()
    checks = qa.Acceptance(); report = {"scope": "LOCAL_SYNTHETIC_ONLY", "checks": checks.checks,
                                      "browser_channel": options.browser}
    errors, external = [], []
    with qa.synthetic_server(create_demo_app) as base, sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **browser_options)
        report["browser"] = browser.version
        def observe(context, origin=base):
            def page_events(page):
                page.on("pageerror", lambda e: errors.append(e.name))
                def console_error(message):
                    if message.type == "error" and ("module script" in message.text.lower()
                            or "/demo-assets/" in message.location.get("url", "")):
                        errors.append("asset_or_module_error")
                page.on("console", console_error)
            context.on("page", page_events)
            def guard(route):
                if not route.request.url.startswith(origin + "/"):
                    external.append(route.request.url); route.abort()
                else: route.continue_()
            context.route("**/*", guard)
        original_context = browser.new_context
        def new_context(**options):
            context = original_context(**options)
            observe(context)
            return context
        browser.new_context = new_context
        try:
            exercise(browser, base, checks, report)
            states(browser, base, checks)
            states(browser, base, checks, "/demo/public/")
            ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
            multiday(ctx.new_page(), base, checks, "desktop"); ctx.close()
            ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
            multiday(ctx.new_page(), base, checks, "cal01-desktop", "/demo/public/"); ctx.close()
            daylight_saving(browser, base, checks)
            overlap_browser(original_context, observe, checks)
            ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            responsive(ctx.new_page(), base, checks, "mobile-390"); ctx.close()
            ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            reviewer_responsive(ctx.new_page(),base,checks,"mobile-390"); ctx.close()
            ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            multiday(ctx.new_page(), base, checks, "mobile-390"); ctx.close()
            ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            responsive(ctx.new_page(), base, checks, "cal01-mobile-390", "/demo/public/")
            multiday(ctx.new_page(), base, checks, "cal01-mobile-390", "/demo/public/"); ctx.close()
        finally:
            print("PHASE=close-functional-browser", flush=True)
            browser.close()
        with tempfile.TemporaryDirectory(prefix="cal-demo-native-zoom-") as folder:
            default = Path(folder) / "Default"; default.mkdir()
            level = math.log(2) / math.log(1.2)
            (default / "Preferences").write_text(json.dumps({"partition": {"default_zoom_level": {"x": level, "0": level}}}), encoding="utf8")
            print("PHASE=native-200-browser", flush=True)
            ctx = pw.chromium.launch_persistent_context(folder, headless=True, **browser_options,
                no_viewport=True, ignore_https_errors=True, args=["--window-size=1440,1000", "--force-device-scale-factor=1"], reduced_motion="reduce")
            observe(ctx)
            try:
                page = ctx.pages[0]; page.goto(base + "/demo/")
                report["native_zoom"] = page.evaluate("({width:innerWidth,dpr:devicePixelRatio,scale:visualViewport.scale,cssZoom:getComputedStyle(document.documentElement).zoom})")
                metrics = report["native_zoom"]
                checks.check("Actual native 200 percent zoom, not CSS zoom or DPR emulation", abs(metrics["dpr"] - 2) < .05 and 600 < metrics["width"] < 800 and metrics["scale"] == 1 and metrics["cssZoom"] == "1")
                responsive(page, base, checks, "native-200")
                reviewer_responsive(ctx.new_page(),base,checks,"native-200")
                multiday(ctx.new_page(), base, checks, "native-200")
                responsive(ctx.new_page(), base, checks, "cal01-native-200", "/demo/public/")
                multiday(ctx.new_page(), base, checks, "cal01-native-200", "/demo/public/")
            finally: ctx.close()
    checks.check("All owned fixture/server/browser contexts stopped", True)
    checks.check("No external network traffic", not external)
    checks.check("No JavaScript page errors", not errors)
    checks.check("Local demo build/runtime leaves existing 52 Production files byte-identical", len(baseline) == 52 and production_manifest() == baseline)
    for name in ("dist", "dist-preview"):
        folder = ROOT.parent / "website" / name
        public_files = [p for p in folder.rglob("*") if p.is_file() and p.suffix in {".html", ".js", ".css", ".xml"}]
        checks.check(name + " excludes local Portal adapter, accounts, assets and demo routes", bool(public_files)
            and not any(marker in p.read_text(encoding="utf8") for p in public_files for marker in
                ("/demo/api/public-calendar", "/demo-assets/", "synthetic.coach@example.invalid", "/demo/public/")))
    report["status"] = "FUNCTIONAL_PASS_CLEANUP_PENDING"
    (EVIDENCE / "browser-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf8")
    return len(checks.checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", choices=("chromium", "msedge"), default="msedge")
    parser.add_argument("--browser-executable", type=Path)
    options = parser.parse_args()
    if options.browser_executable and not options.browser_executable.is_file():
        parser.error("Explicit local browser executable does not exist")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    report_path = EVIDENCE / "browser-report.json"
    report_path.write_text('{"status":"RUNNING"}', encoding="utf8")
    previous = {name: os.environ.get(name) for name in ("TEMP", "TMP")}
    previous_cache = tempfile.tempdir
    # Windows' global TEMP can have a non-inheriting DACL. Use an owned test
    # directory with normal project inheritance, never reset any ACL or user profile.
    try:
        with tempfile.TemporaryDirectory(prefix="run-temp-", dir=EVIDENCE) as folder:
            for name in previous:
                os.environ[name] = folder
            tempfile.tempdir = None
            count = run(options)
        if Path(folder).exists():
            raise RuntimeError("Owned QA temporary directory cleanup incomplete")
        report = json.loads(report_path.read_text(encoding="utf8"))
        report.update(status="PASS", owned_temporary_directory_removed=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf8")
        print(f"CAL1_DEMO=PASS BROWSER_CHECKS={count} LOCAL_BUILD_ISOLATED=PASS PUBLIC_ARTIFACTS_ISOLATED=PASS SERVER_STOPPED=PASS TEMP_CLEANUP=PASS")
    except BaseException:
        report_path.write_text('{"status":"INCOMPLETE"}', encoding="utf8")
        raise
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        tempfile.tempdir = previous_cache


if __name__ == "__main__":
    main()
