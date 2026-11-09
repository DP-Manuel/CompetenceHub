"""One native SQL/API/Portal/public-view proof, using existing browser helpers."""
from datetime import datetime, timedelta
from contextlib import contextmanager
import importlib.util
import json
import math
from pathlib import Path
import tempfile
from zoneinfo import ZoneInfo

from icalendar import Calendar
import pyotp
from playwright.sync_api import expect, sync_playwright
from sqlalchemy import text
from competence_hub_api.portal.postgres_calendar import _PUBLIC_OFFERS

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pilot_demo_qa", ROOT / "scripts/run-cal1-demo-acceptance.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
qa = demo.qa
OFFERS = "/api/v1/portal/calendar/offers"
PUBLIC = "/api/v1/calendar/offers"


def sql_boundaries(fixture, offer_id, checks, report):
    # Rollback-only owner fixture setup models historical records. The production
    # service still forbids creating past events or changing published revisions.
    cases = [
        ("single", "2026-11-28T10:00+01:00", "2026-11-28T11:00+01:00", "2026-11-28T00:00+01:00", "2026-11-29T00:00+01:00", True),
        ("reported Nov28-29", "2026-11-28T17:18+01:00", "2026-11-29T17:18+01:00", "2026-11-29T00:00+01:00", "2026-11-30T00:00+01:00", True),
        ("prior month still running", "2026-10-30T10:00+01:00", "2026-11-08T10:00+01:00", "2026-11-01T00:00+01:00", "2026-12-01T00:00+01:00", True),
        ("both month boundaries", "2026-11-28T10:00+01:00", "2027-01-02T10:00+01:00", "2026-12-01T00:00+01:00", "2027-01-01T00:00+01:00", True),
        ("exclusive midnight", "2026-11-30T10:00+01:00", "2026-12-01T00:00+01:00", "2026-12-01T00:00+01:00", "2027-01-01T00:00+01:00", False),
        ("exclusive next start", "2027-01-01T00:00+01:00", "2027-01-02T10:00+01:00", "2026-12-01T00:00+01:00", "2027-01-01T00:00+01:00", False),
        ("year boundary", "2026-12-31T20:00+01:00", "2027-01-02T10:00+01:00", "2027-01-01T00:00+01:00", "2027-02-01T00:00+01:00", True),
        ("spring DST", "2026-03-28T17:18+01:00", "2026-03-29T17:18+02:00", "2026-03-29T00:00+01:00", "2026-03-30T00:00+02:00", True),
        ("autumn DST", "2026-10-24T17:18+02:00", "2026-10-25T17:18+01:00", "2026-10-25T00:00+02:00", "2026-10-26T00:00+01:00", True),
    ]
    async def exercise(connection):
        for label, starts, ends, left, right, expected in cases:
            savepoint = await connection.begin_nested()
            try:
                start, end = datetime.fromisoformat(starts), datetime.fromisoformat(ends)
                await connection.execute(text("UPDATE competence_hub.calendar_offer_revisions SET starts_at=:start, ends_at=:end, decision_deadline=:deadline WHERE offer_id=:id AND workflow_status='published'"),
                    {"start":start,"end":end,"deadline":start-timedelta(days=1),"id":offer_id})
                params = {"from_at":datetime.fromisoformat(left),"to_at":datetime.fromisoformat(right),
                    "topic_id":None,"after_starts_at":None,"after_offer_id":None,"limit":101}
                rows = (await connection.execute(_PUBLIC_OFFERS,params)).mappings().all()
                checks.check("Actual PostgreSQL half-open overlap: " + label, len(rows)==int(expected))
            finally:
                await savepoint.rollback()
        indexes = (await connection.execute(text("SELECT indexname FROM pg_indexes WHERE schemaname='competence_hub' AND tablename='calendar_offer_revisions'"))).scalars().all()
        checks.check("Existing partial public interval index is present; no migration needed", "calendar_offer_revisions_public_time_idx" in indexes)
        params = {"from_at":datetime.fromisoformat("2026-11-01T00:00+01:00"),"to_at":datetime.fromisoformat("2027-01-01T00:00+01:00"),"topic_id":None,"after_starts_at":None,"after_offer_id":None,"limit":101}
        plan = await connection.scalar(text("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + str(_PUBLIC_OFFERS)),params)
        if isinstance(plan,str): plan=json.loads(plan)
        def names(node):
            return ([node["Index Name"]] if "Index Name" in node else []) + [name for child in node.get("Plans",[]) for name in names(child)]
        report["sql_plan"] = {"rows":plan[0]["Plan"]["Actual Rows"],"indexes":names(plan[0]["Plan"]),"execution_ms":plan[0]["Execution Time"],"fixture_scale_only":True}
    from uuid import UUID
    # UUID is supplied only by this owned synthetic fixture's successful API write.
    offer_id = UUID(offer_id)
    fixture.database(exercise)


def run(fixture, database, options, report, evidence):
    class PilotChecks(qa.Acceptance):
        def check(self, label, condition):
            report["last_check"] = label
            super().check(label, condition)
    checks = PilotChecks()
    report["checks"] = checks.checks
    errors, external, totps, recovery = [], [], {}, {}
    approved_id = None
    saved_cookies = None
    owned_contexts = []
    public_path = "/portal/calendar-public.html" if getattr(options,"integrated_acceptance",False) else "/demo/public/"
    request_label = "Anfrageentwurf vorbereiten" if getattr(options,"integrated_acceptance",False) else "Anfrage simulieren"

    @contextmanager
    def server():
        with qa.synthetic_server(fixture.app) as base:
            try:
                yield base
            finally:
                while owned_contexts:
                    owned_contexts.pop().close()

    def login(page, base, key):
        page.goto(base + "/portal/")
        page.locator("#login-email").fill(fixture.emails[key])
        page.locator("#login-password").fill(fixture.password)
        page.get_by_role("button", name="Anmelden", exact=True).click()
        if key not in totps:
            page.locator("#enrollment-code").wait_for(state="visible")
            totps[key] = pyotp.TOTP(page.locator("#provisioning-secret").inner_text())
            page.locator("#enrollment-code").fill(totps[key].at(fixture.now.timestamp()))
            page.get_by_role("button", name="Einrichtung abschließen").click()
            page.locator("#recovery-view").wait_for(state="visible")
            recovery[key] = page.locator("#recovery-codes li").all_text_contents()
            checks.check("Native " + key + " MFA/recovery enrollment", len(recovery[key]) == 10)
            page.locator("#recovery-confirmed").check()
            page.get_by_role("button", name="Portal öffnen").click()
        else:
            page.get_by_text("Recovery-Code", exact=True).click()
            page.locator("#mfa-code").fill(recovery[key].pop())
            page.get_by_role("button", name="Bestätigen", exact=True).click()
        expect(page.locator("#portal-view")).to_be_visible()
        expect(page.locator("#coach-calendar-loading" if key.startswith("coach") else "#review-calendar-loading")).to_be_hidden()
        if key.startswith("coach"):
            expect(page.locator("#calendar-filter-count")).not_to_have_text("")

    def create(page, title, start, end):
        page.locator("#open-calendar-offer-dialog").click()
        page.get_by_role("button", name="Demo-Werte einsetzen").click()
        page.locator("#calendar-title").fill(title)
        for control, value in (("starts-at", start), ("ends-at", end), ("decision-deadline", start - timedelta(days=3))):
            page.locator("#calendar-" + control).fill(value.strftime("%Y-%m-%dT%H:%M"))
        with qa.calendar_refresh(page):
            page.locator("#save-calendar-offer").click()
            expect(page.locator("#calendar-offer-dialog")).to_be_hidden()
        return next(item["id"] for item in qa.api_offers(page) if item["title"] == title)

    def contexts(browser, base):
        def new(**values):
            context = browser.new_context(ignore_https_errors=True, **values)
            owned_contexts.append(context)
            context.on("page", lambda p: p.on("pageerror", lambda e: errors.append(e.name)))
            def guard(route):
                if not route.request.url.startswith(base + "/"):
                    external.append("external_request"); route.abort()
                else:
                    route.continue_()
            context.route("**/*", guard)
            return context
        return new

    def month_page(page, base, month):
        demo.public_load(page, base, public_path)
        for _ in range(3):
            if page.locator("#month-label").inner_text() == demo_month_label(month):
                return
            page.locator("#next").click()

    def demo_month_label(month):
        # Same month label as the browser's de-DE Intl rendering.
        names = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
        return f"{names[int(month[5:])-1]} {month[:4]}"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=str(options.browser_executable))
        report["browser"] = browser.version
        try:
            with server() as base:
                new = contexts(browser, base)
                coach_context = new(viewport={"width":1440,"height":1000})
                reviewer_context = new(viewport={"width":1440,"height":1000})
                public_context = new(viewport={"width":1440,"height":1000})
                coach = coach_context.new_page(); reviewer = reviewer_context.new_page()
                login(coach, base, "coach"); login(reviewer, base, "reviewer")
                checks.check("Native Coach and Reviewer have separated UI", coach.locator("#review-calendar-workspace").count() == 0 and reviewer.locator("#coach-calendar-workspace").count() == 0)
                now = fixture.now.astimezone(ZoneInfo("Europe/Berlin"))
                first = (now.replace(day=1) + timedelta(days=40)).replace(day=1, hour=17, minute=18, second=0, microsecond=0)
                start, end = first - timedelta(days=1), first + timedelta(days=1)
                if start <= now + timedelta(days=3):
                    first = (first + timedelta(days=40)).replace(day=1)
                    start, end = first - timedelta(days=1), first + timedelta(days=1)
                title = "DEMO: PostgreSQL Mehrtagesworkshop"
                approved_id = create(coach, title, start, end)
                month = first.strftime("%Y-%m")
                checks.check("Native SQL draft is not public or downloadable", public_context.request.get(base + PUBLIC + "/" + approved_id).status == 404 and public_context.request.get(base + PUBLIC + "/" + approved_id + "/calendar.ics").status == 404)

                # Dirty-state guard: explicit cancel preserves, explicit discard closes.
                qa.card(coach, title).get_by_role("button", name="Entwurf bearbeiten").click()
                coach.locator("#calendar-title").fill("UNSAVED")
                coach.once("dialog", lambda dialog: dialog.dismiss())
                coach.keyboard.press("Escape")
                checks.check("Native unsaved Escape cancel preserves input", coach.locator("#calendar-offer-dialog").is_visible() and coach.locator("#calendar-title").input_value() == "UNSAVED")
                coach.once("dialog", lambda dialog: dialog.accept())
                coach.get_by_role("button", name="Abbrechen", exact=True).click()
                checks.check("Native explicit discard keeps stored draft unchanged", qa.api_offer_detail(coach, approved_id)["current_revision"]["title"] == title)

                # Concurrent native sessions, optimistic locking, no guessed ownership.
                stale_context = new(); stale = stale_context.new_page(); login(stale, base, "coach")
                qa.card(coach, title).get_by_role("button", name="Entwurf bearbeiten").click()
                qa.card(stale, title).get_by_role("button", name="Entwurf bearbeiten").click()
                coach.locator("#calendar-summary").fill("Öffentliche geprüfte Beschreibung")
                with qa.calendar_refresh(coach):
                    coach.locator("#save-calendar-offer").click()
                    expect(coach.locator("#calendar-offer-dialog")).to_be_hidden()
                stale.locator("#calendar-summary").fill("STALE PRIVATE MARKER")
                stale.locator("#save-calendar-offer").click()
                expect(stale.locator("#reload-calendar-offer")).to_be_visible()
                checks.check("Concurrent PostgreSQL edit receives safe stale error", "Stack" not in stale.locator("#calendar-offer-error").inner_text() and qa.api_offer_detail(coach, approved_id)["current_revision"]["summary"] == "Öffentliche geprüfte Beschreibung")
                stale_context.close()

                qa.submit_offer(coach, title)
                reviewer.reload(); expect(qa.review_card(reviewer,title)).to_be_visible()
                demo.review(reviewer, title, "changes_requested", "PRIVATE REVIEW: Ort konkretisieren")
                coach.reload(); qa.card(coach, title).get_by_role("button", name="Neue Revision bearbeiten").click()
                expect(coach.locator("#calendar-review-feedback")).to_contain_text("Ort konkretisieren")
                coach.locator("#calendar-location").fill("Fiktiver Demo-Raum A")
                with qa.calendar_refresh(coach):
                    coach.locator("#save-calendar-offer").click()
                    expect(coach.locator("#calendar-offer-dialog")).to_be_hidden()
                qa.submit_offer(coach, title)
                public = public_context.new_page(); month_page(public, base, month)
                checks.check("Native submitted revision not public", public.locator(f'[data-offer="{approved_id}"]').count() == 0)
                reviewer.reload(); demo.review(reviewer, title, "published")
                expect(public.locator(f'[data-offer="{approved_id}"]')).to_have_count(2,timeout=15000)
                checks.check("Native earlier-starting event appears automatically on both next-month days", public.locator(f'[data-offer="{approved_id}"]').first.get_attribute("data-segment-role") == "continue")
                response = public_context.request.get(base + f"/api/v1/calendar/months/{month}/offers")
                projection = response.json()["items"]
                checks.check("Native month API uses overlap without duplicated rows", response.status == 200 and len(projection) == 1 and projection[0]["id"] == approved_id)
                checks.check("Native public HTTP excludes reviewer data and threshold", "PRIVATE" not in response.text() and "review_threshold" not in response.text())
                sql_boundaries(fixture,approved_id,checks,report)
                public.locator(f'[data-offer="{approved_id}"]').last.focus(); public.keyboard.press("Enter")
                expect(public.locator("#detail")).to_be_focused()
                first_ics = public_context.request.get(base + PUBLIC + "/" + approved_id + "/calendar.ics")
                event = Calendar.from_ical(first_ics.body()).walk("VEVENT")[0]
                checks.check("Native ICS is an attachment with Berlin interval and published sequence", first_ics.status == 200 and "attachment" in first_ics.headers["content-disposition"] and event["DTSTART"].params["TZID"] == "Europe/Berlin" and event.decoded("dtstart") == start and event.decoded("dtend") == end and event["SEQUENCE"] == 2)
                with public.expect_download() as download:
                    public.locator("#ics").click()
                failure=download.value.failure()
                report["ics_download"]="PASS" if failure is None else "DOWNLOAD_FAILED"
                checks.check("Actual local browser downloads only public ICS", download.value.suggested_filename.endswith(".ics") and failure is None and Path(download.value.path()).read_bytes()==first_ics.body())
                writes = []
                public.on("request", lambda r: writes.append(r.method) if r.method not in {"GET","HEAD"} else None)
                public.locator("#seats").fill("2"); public.get_by_role("button", name=request_label, exact=True).click()
                checks.check("Native public request draft contains approved event context, no customer record or send", title in public.locator("#request-draft").input_value() and "PRIVATE" not in public.locator("#request-draft").input_value() and writes == [])
                demo.geometry(public, checks, "Native desktop public")
                public.screenshot(path=str(evidence / "desktop-public.png"),full_page=True)
                coach.reload()
                expect(qa.card(coach,title)).to_be_visible()
                expect(coach.locator("#coach-calendar-loading")).to_be_hidden()
                coach.locator("#calendar-offer-search").fill("not present")
                checks.check("Native list search has honest zero results", coach.locator("#coach-calendar-list .calendar-card").count() == 0)
                coach.locator("#calendar-offer-search").fill("")
                coach.locator("#calendar-offer-status").select_option("published")
                checks.check("Native status filter retains published offer", qa.card(coach,title).count() == 1)
                coach.locator("#calendar-offer-status").select_option("")
                collision = "DEMO: Zeitkonflikt desselben Coaches"
                create(coach,collision,start,end)
                qa.card(coach,collision).get_by_role("button",name="Zur Prüfung einreichen").click()
                expect(coach.locator("#coach-calendar-error")).to_contain_text("überschneidet")
                checks.check("Native same-Coach conflict is understandable and keeps draft", next(i for i in qa.api_offers(coach) if i["title"]==collision)["workflow_status"]=="draft")
                qa.card(coach,title).get_by_role("button",name="Neue Revision bearbeiten").click()
                coach.locator("#calendar-title").fill("PRIVATE UNPUBLISHED REVISION")
                with qa.calendar_refresh(coach):
                    coach.locator("#save-calendar-offer").click()
                    expect(coach.locator("#calendar-offer-dialog")).to_be_hidden()
                checks.check("Native private replacement leaves ICS bytes unchanged", public_context.request.get(base+PUBLIC+"/"+approved_id+"/calendar.ics").body() == first_ics.body())
                saved_cookies = coach_context.cookies()
                saved_reviewer = reviewer_context.cookies()
                report["offer_count_before_restart"] = len(projection)

                # Native permissions: a different Coach cannot read this draft.
                other_context = new(); other = other_context.new_page(); login(other,base,"coach_two")
                checks.check("Native Coach B cannot read Coach A offer", other_context.request.get(base+OFFERS+"/"+approved_id).status == 404)
                parallel="DEMO: Paralleler Workshop Coach B"
                create(other,parallel,start,end); qa.submit_offer(other,parallel)
                reviewer.reload(); demo.review(reviewer,parallel,"published")
                page_one=public_context.request.get(base+f"/api/v1/calendar/months/{month}/offers?limit=1").json()
                page_two=public_context.request.get(base+f"/api/v1/calendar/months/{month}/offers",params={"limit":1,"cursor":page_one["next_cursor"]}).json()
                checks.check("Native parallel Coaches and signed pagination preserve distinct offers", page_one["next_cursor"] is not None and page_one["items"][0]["id"] != page_two["items"][0]["id"] and page_two["next_cursor"] is None)
                other_context.close()
                saved = {"uid":str(event["UID"]), "ics":first_ics.body()}
                for ctx in (coach_context,reviewer_context,public_context): ctx.close()

            # New FastAPI application and engine; database rows, credentials,
            # sessions and fixture-only key configuration survive application restart.
            database.restart()
            report["postgres_volume_restart"] = "PASS"
            with server() as base:
                new = contexts(browser,base)
                context = new(viewport={"width":390,"height":844},reduced_motion="reduce")
                context.add_cookies(saved_cookies)
                coach=context.new_page(); coach.goto(base+"/portal/")
                expect(coach.locator("#portal-view")).to_be_visible()
                expect(qa.card(coach,"PRIVATE UNPUBLISHED REVISION")).to_be_visible()
                checks.check("Fresh native app resumes existing PostgreSQL session and revision", qa.api_offer_detail(coach,approved_id)["current_revision"]["revision_number"] == 3)
                public=context.new_page(); month_page(public,base,month)
                checks.check("Fresh native app re-reads approved SQL snapshot, not process memory", public.locator(f'[data-offer="{approved_id}"]').count()==2 and context.request.get(base+PUBLIC+"/"+approved_id+"/calendar.ics").body()==saved["ics"])
                public.locator(f'[data-offer="{approved_id}"]').last.click()
                demo.geometry(public,checks,"Native mobile390")
                public.screenshot(path=str(evidence/"mobile390-public.png"),full_page=True)
                qa.card(coach,"PRIVATE UNPUBLISHED REVISION").get_by_role("button",name="Entwurf bearbeiten").click()
                demo.geometry(coach,checks,"Native mobile390 edit")
                coach.screenshot(path=str(evidence/"mobile390-edit.png"),full_page=True)
                coach.keyboard.press("Escape")
                revised="DEMO: Geprüfte Revision 3"
                qa.card(coach,"PRIVATE UNPUBLISHED REVISION").get_by_role("button",name="Entwurf bearbeiten").click()
                coach.locator("#calendar-title").fill(revised)
                with qa.calendar_refresh(coach):
                    coach.locator("#save-calendar-offer").click()
                    expect(coach.locator("#calendar-offer-dialog")).to_be_hidden()
                qa.submit_offer(coach,revised)
                reviewer_context=new(); reviewer_context.add_cookies(saved_reviewer)
                reviewer=reviewer_context.new_page(); reviewer.goto(base+"/portal/")
                expect(qa.review_card(reviewer,revised)).to_be_visible()
                public.get_by_role("button",name=request_label,exact=True).click()
                demo.review(reviewer,revised,"published")
                expect(public.locator("#detail-title")).to_have_text(revised,timeout=15000)
                revised_ics=Calendar.from_ical(context.request.get(base+PUBLIC+"/"+approved_id+"/calendar.ics").body()).walk("VEVENT")[0]
                checks.check("Native revised publication keeps UID and advances SEQUENCE", str(revised_ics["UID"])==saved["uid"] and revised_ics["SEQUENCE"]==3 and str(revised_ics["SUMMARY"])==revised)
                checks.check("Updated public event clears stale request draft", public.locator("#request-draft-panel").is_hidden())
                reviewer_context.close()
                with tempfile.TemporaryDirectory(prefix="native-pilot-zoom-") as folder:
                    default=Path(folder)/"Default"; default.mkdir()
                    level=math.log(2)/math.log(1.2)
                    (default/"Preferences").write_text(json.dumps({"partition":{"default_zoom_level":{"x":level,"0":level}}}),encoding="utf8")
                    zoom=pw.chromium.launch_persistent_context(folder,headless=True,executable_path=str(options.browser_executable),ignore_https_errors=True,no_viewport=True,args=["--window-size=1440,1000","--force-device-scale-factor=1"],reduced_motion="reduce")
                    try:
                        zoom.on("page",lambda p:p.on("pageerror",lambda e:errors.append(e.name)))
                        zoom.route("**/*",lambda route:route.continue_() if route.request.url.startswith(base+"/") else (external.append("external_request"),route.abort())[-1])
                        page=zoom.new_page(); month_page(page,base,month)
                        report["native_zoom"]=page.evaluate("({width:innerWidth,dpr:devicePixelRatio,cssZoom:getComputedStyle(document.documentElement).zoom})")
                        checks.check("Native PostgreSQL view uses real 200 percent zoom", report["native_zoom"]["dpr"]==2 and 600<report["native_zoom"]["width"]<800 and report["native_zoom"]["cssZoom"]=="1")
                        page.locator(f'[data-offer="{approved_id}"]').last.focus();page.keyboard.press("Enter")
                        expect(page.locator("#detail")).to_be_focused()
                        demo.geometry(page,checks,"Native PostgreSQL200")
                        demo.screenshot(page,evidence/"native200-public.png","native-200")
                    finally:zoom.close()
                with qa.calendar_refresh(coach):
                    qa.card(coach,revised).get_by_role("button",name="Angebot zurückziehen").click()
                expect(public.locator(f'[data-offer="{approved_id}"]')).to_have_count(0,timeout=15000)
                checks.check("Native withdrawal removes view and ICS", context.request.get(base+PUBLIC+"/"+approved_id+"/calendar.ics").status==404)
                context.close()
            report["native_restart"] = "PASS"
        finally:
            browser.close()
    checks.check("Native browser has no JavaScript errors or external requests", not errors and not external)
    report["native_mfa"] = "PASS"
    report["calendar_records"] = "POSTGRESQL_NOT_MEMORY"
