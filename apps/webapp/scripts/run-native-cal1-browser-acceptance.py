"""One opt-in real PostgreSQL/HTTPS/Edge acceptance batch. Never imports secrets."""
import importlib.util
import argparse
import json
import math
from datetime import timedelta
from pathlib import Path
import tempfile
import time
import re
from uuid import uuid4
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit

import pyotp
from playwright.sync_api import expect, sync_playwright

from native_calendar_fixture import NativeCalendarFixture

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT.parents[1] / "release-artifacts/cal1-native-ui-20261022"
spec = importlib.util.spec_from_file_location("cal1_qa", ROOT / "scripts/run-cal1-browser-acceptance.py")
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
ACCESS = "/api/v1/portal/access"
OFFERS = "/api/v1/portal/calendar/offers"


def exercise(fixture, report):
    class NativeAcceptance(qa.Acceptance):
        def check(self, label, condition):
            report["last_check"] = label
            super().check(label, condition)
    checks = NativeAcceptance()
    report["checks"] = checks.checks
    for attr, key in (("COACH_EMAIL", "coach"), ("EMPTY_COACH_EMAIL", "coach_two"),
                      ("ADMIN_EMAIL", "admin"), ("REVIEWER_EMAIL", "reviewer"),
                      ("INTERNAL_EMAIL", "internal"), ("COMPANY_CONTACT_EMAIL", "contact")):
        setattr(qa, attr, fixture.emails[key])
    qa.SYNTHETIC_PASSWORD = fixture.password
    totps = {}
    recovery = {}
    last_steps = {}

    def values(offset_days=30):
        start = (fixture.now + timedelta(days=offset_days)).astimezone(ZoneInfo("Europe/Berlin")).replace(hour=10, minute=0, second=0, microsecond=0)
        return {"start": start.strftime("%Y-%m-%dT%H:%M"),
                "end": (start + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
                "deadline": (start - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M")}
    qa.future_values = values

    def login(page, base, email):
        role_key = next(k for k, value in fixture.emails.items() if value == email)
        report["phase"] = "login:" + role_key
        page.on("pageerror", lambda error: report.setdefault("javascript_errors", []).append({
            "type": error.name, "locations": re.findall(r"app\.js:\d+:\d+", error.stack or "")
        }))
        page.on("response", lambda response: report.setdefault("access_responses", []).append({
            "path": urlsplit(response.url).path, "status": response.status
        }) if "/access/" in response.url else None)
        deadline = time.monotonic() + 35
        while email in last_steps and int(fixture.now.timestamp()) // 30 <= last_steps[email]:
            if time.monotonic() > deadline:
                raise RuntimeError("Database clock did not advance to the next TOTP step")
            time.sleep(.2)
        page.goto(base + "/portal/", wait_until="domcontentloaded")
        page.locator("#login-email").fill(email)
        page.locator("#login-password").fill(fixture.password)
        page.get_by_role("button", name="Anmelden", exact=True).click()
        if email not in totps:
            page.locator("#enrollment-code").wait_for(state="visible")
            secret = page.locator("#provisioning-secret").inner_text()
            totps[email] = pyotp.TOTP(secret)
            page.locator("#enrollment-code").fill(totps[email].at(fixture.now.timestamp()))
            last_steps[email] = int(fixture.now.timestamp()) // 30
            page.get_by_role("button", name="Einrichtung abschließen").click()
            page.locator("#recovery-view").wait_for(state="visible")
            recovery[email] = page.locator("#recovery-codes li").all_text_contents()
            checks.check("Native MFA enrollment returns ten one-time recovery codes", len(recovery[email]) == 10)
            report["phase"] = "recovery-confirm:" + role_key
            page.locator("#recovery-confirmed").check()
            page.get_by_role("button", name="Portal öffnen").click()
        else:
            page.locator("#mfa-code").fill(totps[email].at(fixture.now.timestamp()))
            last_steps[email] = int(fixture.now.timestamp()) // 30
            page.get_by_role("button", name="Bestätigen", exact=True).click()
        report["phase"] = "portal-visible:" + role_key
        try:
            page.locator("#portal-view").wait_for(state="visible")
        except Exception:
            page.screenshot(path=str(EVIDENCE / "login-failure-masked.png"), full_page=True, mask=[
                page.locator(selector) for selector in ("#recovery-codes", "#provisioning-secret", "#login-password", "#mfa-code", "#enrollment-code")
            ])
            raise
        report["phase"] = "session-resume:" + role_key
        try:
            endpoint = OFFERS if role_key in ("coach", "coach_two") else "/api/v1/portal/calendar/review-queue" if role_key == "reviewer" else "/api/v1/portal/companies"
            with page.expect_response(lambda response: response.url.split("?")[0].endswith(endpoint)
                                      and response.request.method == "GET") as loaded:
                page.reload(wait_until="domcontentloaded")
            assert loaded.value.status == 200
            expect(page.locator("#portal-view")).to_be_visible()
            if role_key in ("coach", "coach_two", "reviewer"):
                page.locator("#review-calendar-loading" if role_key == "reviewer" else "#coach-calendar-loading").wait_for(state="hidden")
        except Exception:
            page.screenshot(path=str(EVIDENCE / "resume-failure-masked.png"), full_page=True, mask=[
                page.locator(selector) for selector in ("#recovery-codes", "#provisioning-secret", "#login-password", "#mfa-code", "#enrollment-code")
            ])
            raise
        response = page.context.request.get(base + ACCESS + "/session")
        role = fixture.roles[next(k for k, value in fixture.emails.items() if value == email)]
        checks.check("Native session resume retains exact role " + role, response.status == 200 and response.json()["user"]["roles"] == [role])
        checks.check("No token in Web Storage", page.evaluate("localStorage.length === 0 && sessionStorage.length === 0"))
        checks.check("Protected responses no-store", response.headers.get("cache-control") == "no-store")
    qa.login = login

    def csrf(page, base):
        response = page.context.request.post(base + ACCESS + "/session/csrf", headers={"Origin": base})
        assert response.status == 204
        return response.headers["x-csrf-token"]

    def decide(page, title, outcome):
        qa.review_card(page, title).get_by_role("button", name="Angebot prüfen").click()
        page.locator("#calendar-review-dialog").wait_for(state="visible")
        page.get_by_label("Veröffentlichen" if outcome == "published" else "Änderungen anfordern", exact=True).check()
        if outcome == "changes_requested":
            page.locator("#calendar-review-note").fill("Synthetic private change request")
        page.get_by_role("button", name="Entscheidung speichern").click()
        page.locator("#calendar-review-dialog").wait_for(state="hidden")

    with qa.synthetic_server(fixture.app) as base, sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        report["browser"] = "Microsoft Edge " + browser.version
        try:
            context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000}, timezone_id="Europe/Berlin")
            page = context.new_page()
            checks.check("Unauthenticated Calendar blocked", context.request.get(base + OFFERS).status == 401)
            login(page, base, fixture.emails["coach"])
            checks.check("Native own Coach empty state", page.locator("#coach-calendar-empty").is_visible())
            for index in range(1, 5):
                page.locator("#open-calendar-offer-dialog").click()
                qa.fill_offer(page, f"Synthetisches Angebot {index}", 7 + index * 4)
                if index % 2 == 0:
                    page.locator("#calendar-format").select_option("praesenz")
                    page.locator("#calendar-location").fill("Würzburg")
                page.locator("#save-calendar-offer").dblclick()
                page.locator("#calendar-offer-dialog").wait_for(state="hidden")
                if index > 1:
                    qa.submit_offer(page, f"Synthetisches Angebot {index}")
            checks.check("Four UI creations, no duplicate submit", len(qa.api_offers(page)) == 4)
            qa.logout(page)
            login(page, base, fixture.emails["reviewer"])
            decide(page, "Synthetisches Angebot 3", "published")
            decide(page, "Synthetisches Angebot 4", "changes_requested")
            qa.logout(page)
            qa.admin_contract(page, base, checks, include_company_regression=False)
            qa.coach_workflow(page, browser, base, checks)
            qa.reviewer_workflow(page, base, checks)
            qa.role_and_accessibility_checks(browser, base, checks)
            qa.generic_error_check(browser, base, checks)

            login(page, base, fixture.emails["coach"])
            own = qa.api_offers(page)
            detail_response = context.request.get(base + OFFERS + "/" + own[0]["id"])
            detail = detail_response.json()
            draft = {key: detail["current_revision"][key] for key in (
                "topic_id", "title", "summary", "starts_at", "ends_at", "time_zone",
                "format", "public_location", "capacity", "review_threshold", "decision_deadline", "price_display_text")}
            token = csrf(page, base)
            headers = {"Origin": base, "X-CSRF-Token": token, "Content-Type": "application/json", "If-Match": detail_response.headers["etag"]}
            wrong_origin = {**headers, "Origin": "https://other.example.invalid"}
            for label, bad in (("Origin", wrong_origin), ("CSRF", {**headers, "X-CSRF-Token": "wrong"})):
                response = context.request.patch(base + OFFERS + "/" + own[0]["id"] + "/draft", headers=bad, data=draft)
                checks.check("Native " + label + " fail-closed", response.status == 403)
            unknown = context.request.post(base + OFFERS, headers=headers, data={"client_request_id": str(uuid4()), "draft": draft, "role": "admin"})
            checks.check("Unknown fields rejected", unknown.status == 400)
            forged_coach = context.request.post(base + OFFERS, headers=headers,
                data={"client_request_id": str(uuid4()), "coach_id": str(fixture.coaches["coach_two"]), "draft": draft})
            checks.check("Client Coach ID cannot create ownership", forged_coach.status == 403)
            checks.check("Coach filter cannot widen scope", context.request.get(base + OFFERS, params={"coach_id": str(fixture.coaches["coach_two"])}).status == 403)
            oversized = context.request.post(base + OFFERS, headers={**headers, "Content-Type": "application/json"}, data=json.dumps({"unexpected": "x" * (33 * 1024)}))
            checks.check("32 KiB body limit", oversized.status == 400)
            for path, method in (("/api/v1/portal/companies", "post"), ("/api/v1/portal/companies/" + str(uuid4()) + "/contacts", "post"), ("/api/v1/admin/users/invitations", "post"), ("/api/v1/portal/calendar/review-queue", "get")):
                response = getattr(context.request, method)(base + path, headers=headers, **({"data": {}} if method == "post" else {}))
                checks.check("Coach denied " + path.split("/")[-1], response.status in (401, 403))

            foreign_context = browser.new_context(ignore_https_errors=True)
            foreign = foreign_context.new_page()
            login(foreign, base, fixture.emails["coach_two"])
            qa.create_offer(foreign, '<img src=x onerror="window.nativeXss=1">', 60)
            checks.check("Stored text cannot inject DOM or run script", foreign.locator("#coach-calendar-list img").count() == 0
                         and foreign.evaluate("window.nativeXss === undefined"))
            foreign_offer = qa.api_offers(foreign)[0]
            for suffix, method, body in (("", "get", None), ("/draft", "patch", draft), ("/submit", "post", None), ("/withdraw", "post", None)):
                extra = {"data": body} if body else {}
                response = getattr(context.request, method)(base + OFFERS + "/" + foreign_offer["id"] + suffix, headers=headers, **extra)
                checks.check("Native foreign offer denied " + (suffix or "read"), response.status == 404)
            unknown_id = context.request.get(base + OFFERS + "/" + str(uuid4()))
            invisible = context.request.get(base + OFFERS + "/" + foreign_offer["id"])
            checks.check("Invisible and unknown IDs indistinguishable", invisible.json() == unknown_id.json())
            fixture.expire("coach_two")
            checks.check("Expired session cannot resume", foreign_context.request.get(base + ACCESS + "/session").status == 401)
            foreign_context.close()

            public = context.request.get(base + "/api/v1/calendar/offers", params={"from": fixture.now.isoformat(), "to": (fixture.now + timedelta(days=80)).isoformat()})
            checks.check("Native public projection reads published only", public.status == 200 and len(public.json()["items"]) == 2)
            private_ids = [str(value) for value in (*fixture.users.values(), *fixture.coaches.values())]
            public_text = public.text()
            checks.check("Public projection excludes private fields and identities", not any(value in public_text for value in private_ids)
                         and not any(key in public_text for key in ("review_threshold", "lock_version", "workflow_status", "review_decisions", "Synthetic private", "Published Revision im Browser")))
            allowed = {"id", "coach", "topic", "title", "summary", "starts_at", "ends_at", "time_zone", "format", "public_location", "capacity", "decision_deadline", "price_display_text", "updated_at"}
            for item in public.json()["items"]:
                checks.check("Exact public DTO allowlist", set(item) == allowed and set(item["coach"]) == {"display_name", "profile_path"} and item["coach"]["profile_path"] is None)

            with tempfile.TemporaryDirectory(prefix="native-cal1-zoom-") as temp:
                profile = Path(temp) / "Default"
                profile.mkdir()
                level = math.log(2) / math.log(1.2)
                (profile / "Preferences").write_text(json.dumps({"partition": {"default_zoom_level": {"x": level, "0": level}}}), encoding="utf-8")
                zoom = p.chromium.launch_persistent_context(temp, channel="msedge", headless=True, no_viewport=True,
                    ignore_https_errors=True, args=["--window-size=1440,1000", "--force-device-scale-factor=1"])
                try:
                    zoom_page = zoom.pages[0]
                    login(zoom_page, base, fixture.emails["admin"])
                    qa.open_area(zoom_page, "Kalenderangebote")
                    checks.check("Actual 200 percent browser zoom", zoom_page.evaluate("Math.abs(devicePixelRatio - 2) < .05 && innerWidth < 800"))
                    checks.check("Actual zoom no horizontal overflow", zoom_page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
                    zoom_page.screenshot(path=str(EVIDENCE / "native-actual-200-percent.png"))
                finally:
                    zoom.close()

            reviewer_context = browser.new_context(ignore_https_errors=True)
            try:
                reviewer_page = reviewer_context.new_page()
                login(reviewer_page, base, fixture.emails["reviewer"])
                reviewer_headers = {"Origin": base, "X-CSRF-Token": csrf(reviewer_page, base), "If-Match": headers["If-Match"]}
                for path, method, data in (
                    (OFFERS, "post", {"client_request_id": str(uuid4()), "draft": draft}),
                    (OFFERS + "/" + own[0]["id"] + "/draft", "patch", draft),
                    ("/api/v1/portal/companies", "post", {}),
                    ("/api/v1/portal/companies/" + str(uuid4()) + "/contacts", "post", {}),
                    ("/api/v1/admin/users/invitations", "post", {}),
                ):
                    response = getattr(reviewer_context.request, method)(base + path, headers=reviewer_headers, data=data)
                    checks.check("MFA-backed Reviewer has no foreign mutation right " + path.split("/")[-1], response.status in (401, 403))
                fixture.remove_role("reviewer")
                checks.check("Revoked Reviewer role effective immediately", reviewer_context.request.get(base + "/api/v1/portal/calendar/review-queue").status == 401)
            finally:
                reviewer_context.close()

            security = browser.new_context(ignore_https_errors=True)
            try:
                def first_factor():
                    result = security.request.post(base + ACCESS + "/login", headers={"Origin": base},
                        data={"email": fixture.emails["coach"], "password": fixture.password})
                    assert result.status == 202
                    return {"Origin": base, "X-CSRF-Token": result.json()["csrf_token"]}
                challenge_headers = first_factor()
                checks.check("Password factor alone creates no session", security.request.get(base + ACCESS + "/session").status == 401)
                invalid = security.request.post(base + ACCESS + "/mfa/totp/verify", headers=challenge_headers, data={"code": "invalid"})
                checks.check("Invalid MFA creates no session", invalid.status == 401 and security.request.get(base + ACCESS + "/session").status == 401)
                replay = security.request.post(base + ACCESS + "/mfa/totp/verify", headers=challenge_headers, data={"code": totps[fixture.emails["coach"]].at(last_steps[fixture.emails["coach"]] * 30)})
                checks.check("Accepted TOTP cannot be replayed", replay.status == 401)
                fixture.expire("coach", challenges=True)
                expired = security.request.post(base + ACCESS + "/mfa/totp/verify", headers=challenge_headers, data={"code": totps[fixture.emails["coach"]].at(fixture.now.timestamp())})
                checks.check("Expired challenge denied", expired.status == 401)
                challenge_headers = first_factor()
                code = recovery[fixture.emails["coach"]][0]
                recovered = security.request.post(base + ACCESS + "/mfa/recovery/verify", headers=challenge_headers, data={"code": code})
                checks.check("Calendar-only recovery creates MFA-backed session", recovered.status == 204 and security.request.get(base + ACCESS + "/session").status == 200)
                old_csrf = recovered.headers["x-csrf-token"]
                rotated = security.request.post(base + ACCESS + "/session/csrf", headers={"Origin": base})
                checks.check("CSRF rotates on native session", rotated.status == 204 and rotated.headers["x-csrf-token"] != old_csrf)
                stale = security.request.delete(base + ACCESS + "/session", headers={"Origin": base, "X-CSRF-Token": old_csrf})
                checks.check("Stale CSRF cannot revoke session", stale.status == 403)
                logged_out = security.request.delete(base + ACCESS + "/session", headers={"Origin": base, "X-CSRF-Token": rotated.headers["x-csrf-token"]})
                checks.check("Logout invalidates native session", logged_out.status == 204 and security.request.get(base + ACCESS + "/session").status == 401)
                reused = security.request.post(base + ACCESS + "/mfa/recovery/verify", headers=first_factor(), data={"code": code})
                checks.check("Recovery code is single-use", reused.status == 401)
            finally:
                security.close()

            # Mutating role state is confined to exact synthetic UUIDs; no UI cache is trusted.
            fixture.remove_role("coach")
            checks.check("Revoked Coach role effective immediately", context.request.get(base + OFFERS).status == 401)
            context.close()
            audit = fixture.inspect_audit()
            allowed_audit = {"id", "actor_user_id", "occurred_at", "action", "entity_type", "entity_id", "outcome"}
            checks.check("Audit stores identifiers, no payload columns", bool(audit) and all(set(row) == allowed_audit for row in audit))
            required_actions = {"calendar.offer." + action for action in ("created", "draft_updated", "submitted", "published", "changes_requested", "withdrawn")}
            checks.check("Every Calendar mutation type audited", required_actions <= {row["action"] for row in audit})
            report["audit_events"] = len(audit)
        finally:
            browser.close()


def main():
    global EVIDENCE
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-container-rehearsal", action="store_true")
    args = parser.parse_args()
    if args.local_container_rehearsal:
        EVIDENCE = EVIDENCE.with_name("cal1-local-pg-rehearsal-20261022")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    report = {"environment": "local-container-rehearsal" if args.local_container_rehearsal else "native-staging", "status": "NOT_RUN", "cleanup": "NOT_RUN", "checks": [], "production_changed": False, "preview_changed": False}
    fixture = None
    exit_code = 1
    try:
        fixture = NativeCalendarFixture(local_container_rehearsal=args.local_container_rehearsal)
        report["fixture_ids"] = {"users": {key: str(value) for key, value in fixture.users.items()}, "coaches": [str(value) for value in fixture.coaches.values()], "topic": str(fixture.topic)}
        (EVIDENCE / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        fixture.prepare()
        report["baseline_counts"] = fixture.baseline
        exercise(fixture, report)
        report["status"] = "PASS"
        exit_code = 0
    except Exception as error:
        report["status"] = "FAIL"
        report["failure_type"] = type(error).__name__
        # Never serialize exception text: driver/browser messages may contain credentials.
        print("Native batch failed; sanitized failure type: " + type(error).__name__)
    finally:
        if fixture is not None and fixture.provisioned:
            try:
                fixture.cleanup()
                report["cleanup"] = "PASS" if fixture.cleanup_pass else "FAIL"
                report["after_counts"] = fixture.after
            except Exception as error:
                report["cleanup"] = "FAIL"
                report["cleanup_failure_type"] = type(error).__name__
                exit_code = 1
        else:
            report["cleanup"] = "NO_DATA_CREATED"
        (EVIDENCE / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("NATIVE_UI=" + report["status"] + " CLEANUP=" + report["cleanup"])
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
