"""Real local PG + native Login/MFA + Edge; outputs no passwords, cookies or tokens."""

import importlib.util
import base64
import json
import math
from pathlib import Path
import tempfile
from uuid import uuid4

import pyotp
from playwright.sync_api import sync_playwright, expect
from sqlalchemy import text

from coach_management_fixture import LocalCoachManagementFixture

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "release-artifacts/coach2-local-20261023"
spec = importlib.util.spec_from_file_location(
    "cal1_qa", ROOT / "scripts/run-cal1-browser-acceptance.py"
)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
READ = "/api/v1/admin/coach-management"
WRITE = "/api/v1/admin/coaches"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fixture = LocalCoachManagementFixture()
    fixture.prepare()
    checks = []
    report = {"checks": checks, "data": "synthetic_only", "server_changed": False}

    def check(label, value):
        if not value:
            raise AssertionError(label)
        checks.append(label)
        print("PASS | " + label)

    def tab(page, name):
        page.get_by_role("tab", name=name, exact=True).click()

    def saved(page, button="Profilentwurf speichern"):
        page.get_by_role("button", name=button, exact=True).click()
        expect(page.locator("#coach-management-workspace .form-success")).to_have_text(
            "Gespeichert."
        )

    def confirm(page, label):
        page.get_by_role("button", name=label, exact=True).click()
        page.get_by_role("dialog").get_by_role(
            "button", name="Bestätigen", exact=True
        ).click()
        expect(page.locator("#coach-management-workspace .form-success")).to_have_text(
            "Gespeichert."
        )

    def approval(page, label):
        tab(page, "Veröffentlichung")
        page.get_by_role("button", name=label, exact=True).click()
        page.get_by_label("Nachweisreferenz", exact=True).fill(
            "synthetic-local-acceptance"
        )
        page.get_by_role("dialog").get_by_role(
            "button", name="Bestätigen", exact=True
        ).click()
        expect(page.locator("#coach-management-workspace .form-success")).to_have_text(
            "Gespeichert."
        )

    def revision(page):
        tab(page, "Profil")
        saved(page, "Neue Profilrevision")

    def submit_review(page):
        confirm(page, "Zur Prüfung einreichen")
        approval(page, "Inhalt geprüft")
        approval(page, "Einwilligung belegt")

    def login(page, base, key):
        page.goto(base + "/portal/", wait_until="domcontentloaded")
        page.locator("#login-email").fill(fixture.emails[key])
        page.locator("#login-password").fill(fixture.password)
        page.get_by_role("button", name="Anmelden", exact=True).click()
        if key == "contact":
            expect(page.locator("#login-error")).to_be_visible()
            check(
                "Company-contact admission remains denied before MFA",
                page.locator("#login-view").is_visible(),
            )
            return
        page.locator("#enrollment-code").wait_for(state="visible")
        secret = page.locator("#provisioning-secret").inner_text()
        page.locator("#enrollment-code").fill(
            pyotp.TOTP(secret).at(fixture.now.timestamp())
        )
        page.get_by_role("button", name="Einrichtung abschließen", exact=True).click()
        page.locator("#recovery-view").wait_for(state="visible")
        page.locator("#recovery-confirmed").check()
        page.get_by_role("button", name="Portal öffnen", exact=True).click()
        expect(page.locator("#portal-view")).to_be_visible()

    def json_get(context, base, path):
        response = context.request.get(base + path)
        assert response.status == 200
        return response.json()

    def enter(page, base):
        page.goto(base + "/portal/coaches/", wait_until="domcontentloaded")
        expect(
            page.get_by_role("button", name="Coach anlegen", exact=True)
        ).to_be_visible()
        page.locator(".cm-list").wait_for(state="attached")

    def geometry(page, label):
        check(
            label + " no horizontal overflow",
            page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),
        )
        check(
            label + " visible text not clipped",
            page.locator("#coach-management-workspace").evaluate("""root=>{
          const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT); let t;
          while(t=walker.nextNode()) {
            const p=t.parentElement;if(!t.textContent.trim()||!p.checkVisibility()||p.closest('select,textarea'))continue;
            const range=document.createRange();range.selectNodeContents(t);
            for(const r of range.getClientRects()) {if(!r.width)continue;if(r.left < -1 || r.right>innerWidth+1)return false;
              for(let a=p;a&&a!==document.body;a=a.parentElement){const s=getComputedStyle(a),b=a.getBoundingClientRect();
                if(['hidden','clip'].includes(s.overflowX)&&(r.left<b.left-1||r.right>b.right+1))return false;
                if(['hidden','clip'].includes(s.overflowY)&&(r.top<b.top-1||r.bottom>b.bottom+1))return false;}}
          }return true;}"""),
        )
        check(
            label + " separate text blocks do not overlap",
            page.locator("#coach-management-workspace").evaluate(
                """root=>{
          const nodes=[...root.querySelectorAll('h2,h3,legend,label,button,dt,dd')].filter(n=>n.checkVisibility());
          const rects=nodes.map(n=>{const r=document.createRange();r.selectNodeContents(n);return [...r.getClientRects()].filter(x=>x.width&&x.height);});
          return nodes.every((n,i)=>nodes.slice(i+1).every((m,j)=>n.contains(m)||m.contains(n)||rects[i].every(a=>rects[i+j+1].every(b=>
            Math.min(a.right,b.right)-Math.max(a.left,b.left)<=1 || Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)<=1))));}"""
            ),
        )

    try:
        with qa.synthetic_server(fixture.app) as base, sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            try:
                context = browser.new_context(
                    ignore_https_errors=True,
                    viewport={"width": 1440, "height": 1000},
                    reduced_motion="reduce",
                )
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(error.name))
                check(
                    "Unauthenticated direct Admin URL denied",
                    context.request.get(base + "/portal/coaches/").status == 401,
                )
                login(page, base, "admin")
                expect(
                    page.get_by_role("button", name="Coaches", exact=True)
                ).to_be_visible()
                check(
                    "Authenticated direct Admin URL allowed",
                    context.request.get(base + "/portal/coaches/").status == 200,
                )
                enter(page, base)
                check(
                    "Empty state is business readable",
                    page.get_by_text(
                        "Noch keine Coaches vorhanden.", exact=True
                    ).is_visible(),
                )

                def lose_creation_response(route):
                    if route.request.method == "POST":
                        response = route.fetch()
                        assert response.status == 201
                        route.abort()
                    else:
                        route.continue_()

                page.route("**/api/v1/admin/coaches", lose_creation_response)
                page.get_by_role("button", name="Coach anlegen", exact=True).click()
                page.get_by_role("dialog").get_by_label("Anzeigename", exact=True).fill(
                    "Coach Delta"
                )
                page.get_by_role("dialog").get_by_role(
                    "button", name="Anlegen", exact=True
                ).click()
                expect(
                    page.locator("#coach-management-workspace .form-error")
                ).to_be_visible()
                page.unroute("**/api/v1/admin/coaches", lose_creation_response)
                page.get_by_role("button", name="Coach anlegen", exact=True).click()
                expect(
                    page.get_by_role("dialog").get_by_label("Anzeigename", exact=True)
                ).to_have_value("Coach Delta")
                page.get_by_role("dialog").get_by_role(
                    "button", name="Anlegen", exact=True
                ).click()
                expect(
                    page.locator("#coach-management-workspace .form-success")
                ).to_have_text("Gespeichert.")
                check(
                    "Lost creation response retries same request without duplicate person",
                    len(json_get(context, base, READ)["items"]) == 1,
                )
                created = json_get(context, base, READ)["items"][0]
                delta = created["id"]
                check(
                    "Create requires only name and is unpublished draft",
                    created["lifecycle"] == "draft"
                    and created["preview"] == "not_published"
                    and created["revision_number"] is None,
                )
                revision(page)
                tab(page, "Profil")
                page.get_by_label("Kurzbeschreibung", exact=True).fill(
                    "Synthetic <img src=x onerror=alert(1)> text"
                )
                page.get_by_label("Öffentlicher Profilpfad", exact=True).fill(
                    "/coaches/coach-delta/"
                )
                tab(page, "Themen")
                page.get_by_label("Synthetic Kommunikation", exact=False).check()
                page.get_by_label("Synthetic Stressmanagement", exact=False).check()
                check(
                    "Canonical topics show multiple categories",
                    set(
                        page.locator(".cm-topic-categories")
                        .first.inner_text()
                        .split(" · ")
                    )
                    == {"Personalentwicklung", "Persönlichkeitsentwicklung"},
                )
                tab(page, "Kompetenzen")
                page.get_by_role("textbox", name="Kompetenzen", exact=True).fill(
                    "Synthetic Kompetenz Eins\nSynthetic Kompetenz Zwei"
                )
                tab(page, "Angebote")
                page.get_by_role(
                    "button", name="Angebot hinzufügen", exact=True
                ).click()
                page.get_by_label("Titel", exact=True).fill("Synthetic Vortrag Delta")
                page.get_by_label("Typ", exact=True).select_option("lecture")
                saved(page)
                result = json_get(context, base, READ + "/" + delta)
                check(
                    "Profile topics competencies and offering persisted through native UI",
                    len(result["revision"]["content"]["topic_ids"]) == 2
                    and len(result["revision"]["content"]["competencies"]) == 2
                    and result["revision"]["content"]["offerings"][0]["type"]
                    == "lecture",
                )
                check(
                    "XSS is literal text, not executable markup",
                    page.locator("#coach-management-workspace img").count() == 0
                    and "<img" in result["revision"]["content"]["short_intro"],
                )
                submit_review(page)
                check(
                    "Submitted profile is immutable in UI",
                    not json_get(context, base, READ + "/" + delta)["capabilities"][
                        "editable"
                    ],
                )
                confirm(page, "Aktivieren")
                approval(page, "Preview freigegeben")
                tab(page, "Veröffentlichung")
                confirm(page, "GitHub Preview veröffentlichen")
                result = json_get(context, base, READ + "/" + delta)
                check(
                    "Preview and Production independent",
                    result["publications"]["preview"]["state"] == "published"
                    and "production" not in result["publications"],
                )
                tab(page, "Veröffentlichung")
                check(
                    "Production publication action absent without scoped approval",
                    page.get_by_role(
                        "button", name="Production veröffentlichen", exact=True
                    ).count()
                    == 0,
                )
                approval(page, "Production freigegeben")
                tab(page, "Veröffentlichung")
                confirm(page, "Production veröffentlichen")
                check(
                    "Production is only a local state",
                    json_get(context, base, READ + "/" + delta)["publications"][
                        "production"
                    ]["state"]
                    == "published",
                )
                revision(page)
                tab(page, "Angebote")
                page.get_by_label("Angebot aktiv", exact=True).uncheck()
                saved(page)
                check(
                    "Offering deactivated without deleting history",
                    not json_get(context, base, READ + "/" + delta)["revision"][
                        "content"
                    ]["offerings"][0]["active"],
                )
                confirm(page, "Pausieren")
                result = json_get(context, base, READ + "/" + delta)
                check(
                    "Pause withdraws both states and abandons pending draft",
                    result["lifecycle"] == "paused"
                    and result["revision"]["status"] == "abandoned"
                    and all(
                        x["state"] == "withdrawn"
                        for x in result["publications"].values()
                    ),
                )
                check(
                    "No stale reactivation without fresh revision",
                    page.get_by_role("button", name="Reaktivieren", exact=True).count()
                    == 0,
                )
                revision(page)
                submit_review(page)
                confirm(page, "Reaktivieren")
                check(
                    "Reactivation keeps UUID and does not republish",
                    json_get(context, base, READ + "/" + delta)["id"] == delta
                    and not json_get(context, base, READ + "/" + delta)["capabilities"][
                        "publish"
                    ],
                )
                confirm(page, "Deaktivieren")
                check(
                    "Offboarding is lifecycle, not deletion",
                    json_get(context, base, READ + "/" + delta)["lifecycle"]
                    == "inactive",
                )
                revision(page)
                submit_review(page)
                confirm(page, "Reaktivieren")
                check(
                    "Second reentry retains revisions and identity",
                    json_get(context, base, READ + "/" + delta)["revision"]["number"]
                    == 4,
                )
                revision(page)
                tab(page, "Profil")
                original = page.get_by_label(
                    "Kurzbeschreibung", exact=True
                ).input_value()
                page.get_by_label("Kurzbeschreibung", exact=True).fill(
                    "Synthetic pending tab A"
                )
                page.once("dialog", lambda d: d.dismiss())
                page.get_by_role("button", name="Zur Coachliste", exact=True).click()
                check(
                    "Dirty navigation cancellation preserves input",
                    page.get_by_label("Kurzbeschreibung", exact=True).input_value()
                    == "Synthetic pending tab A",
                )
                second = context.new_page()
                enter(second, base)
                second.get_by_role("button", name="Coach Delta", exact=True).click()
                tab(second, "Profil")
                second.get_by_label("Kurzbeschreibung", exact=True).fill(
                    "Synthetic saved tab B"
                )
                saved(second)
                page.get_by_role(
                    "button", name="Profilentwurf speichern", exact=True
                ).click()
                expect(
                    page.locator("#coach-management-workspace .form-error")
                ).to_contain_text("Datensatz wurde inzwischen geändert")
                check(
                    "Stale two-tab write rejected without losing draft",
                    page.get_by_label("Kurzbeschreibung", exact=True).input_value()
                    == "Synthetic pending tab A",
                )
                check(
                    "Conflict alert receives focus",
                    page.locator("#coach-management-workspace .form-error").evaluate(
                        "e=>e===document.activeElement"
                    ),
                )
                page.once("dialog", lambda d: d.accept())
                page.get_by_role(
                    "button", name="Aktuellen Stand laden", exact=True
                ).click()
                expect(page.locator("#cm-tab-profile")).to_be_visible()
                tab(page, "Profil")
                expect(page.get_by_label("Kurzbeschreibung", exact=True)).to_have_value(
                    "Synthetic saved tab B"
                )
                check("Explicit reload recovers latest state", True)
                second.close()
                page.get_by_label("Kurzbeschreibung", exact=True).fill("")
                page.get_by_role(
                    "button", name="Profilentwurf speichern", exact=True
                ).click()
                check(
                    "Invalid field is focused and marked",
                    page.get_by_label("Kurzbeschreibung", exact=True).evaluate(
                        "e=>e===document.activeElement && e.getAttribute('aria-invalid')==='true'"
                    ),
                )
                page.get_by_label("Kurzbeschreibung", exact=True).fill(
                    "Synthetic saved tab B"
                )
                saved(page)
                tab(page, "Profil")
                page.evaluate("scrollTo(0, 0)")
                page.screenshot(path=str(OUT / "desktop-profile.png"), full_page=True)
                geometry(page, "Desktop profile")
                tab(page, "Übersicht")
                page.get_by_role("tab", name="Übersicht", exact=True).focus()
                page.keyboard.press("ArrowRight")
                check(
                    "Arrow-key tabs select and focus panel tab",
                    page.locator("#cm-tab-profile").evaluate(
                        "e=>e===document.activeElement && e.getAttribute('aria-selected')==='true'"
                    ),
                )
                page.get_by_role("button", name="Zur Coachliste", exact=True).click()
                fixture.seed_states()
                enter(page, base)
                check(
                    "Representative Alpha Beta Gamma fixtures visible",
                    all(
                        page.get_by_role(
                            "button", name="Coach " + n, exact=True
                        ).is_visible()
                        for n in ("Alpha", "Beta", "Gamma")
                    ),
                )
                page.get_by_label("Lifecycle", exact=True).select_option("paused")
                expect(
                    page.get_by_role("button", name="Coach Beta", exact=True)
                ).to_be_visible()
                check(
                    "Lifecycle filter is server applied",
                    len(json_get(context, base, READ + "?lifecycle=paused")["items"])
                    == 1,
                )
                page.get_by_label("Lifecycle", exact=True).select_option("")
                page.get_by_label("Veröffentlichung", exact=True).select_option(
                    "preview"
                )
                expect(
                    page.get_by_role("button", name="Coach Alpha", exact=True)
                ).to_be_visible()
                check(
                    "Publication filter is server applied",
                    len(json_get(context, base, READ + "?publication=preview")["items"])
                    == 1,
                )
                page.get_by_label("Veröffentlichung", exact=True).select_option("")
                page.get_by_role("button", name="Coach Gamma", exact=True).click()
                tab(page, "Historie")
                history = page.locator("#cm-panel-history > section").first
                check(
                    "Revision history is bounded to ten entries",
                    history.get_by_role("button", name="Revision", exact=False).count()
                    == 10,
                )
                history.get_by_role("button", name="Weitere", exact=True).click()
                expect(
                    history.get_by_role(
                        "button", name="Revision 1 · Eingereicht", exact=True
                    )
                ).to_be_visible()
                history.get_by_role(
                    "button", name="Revision 1 · Eingereicht", exact=True
                ).click()
                tab(page, "Profil")
                check(
                    "Historical revision opens as immutable",
                    page.get_by_label("Kurzbeschreibung", exact=True).is_disabled(),
                )
                bounded = json_get(
                    context, base, READ + "/" + str(fixture.ids["Gamma"])
                )
                check(
                    "Workspace returns one selected profile without unbounded revision content",
                    bounded["revision"]["number"] == 13 and "revisions" not in bounded,
                )
                check(
                    "Bounded reads retain older valid reactivation approval",
                    "active" in bounded["capabilities"]["lifecycles"],
                )
                page.get_by_role("button", name="Zur Coachliste", exact=True).click()
                page.get_by_role("button", name="Coach Alpha", exact=True).click()
                csrf = context.request.post(
                    base + "/api/v1/portal/access/session/csrf",
                    headers={"Origin": base},
                ).headers["x-csrf-token"]
                headers = {"Origin": base, "X-CSRF-Token": csrf}
                alpha = json_get(context, base, READ + "/" + str(fixture.ids["Alpha"]))
                path = WRITE + "/" + alpha["id"] + "/lifecycle"
                payload = {"expected_version": alpha["version"], "lifecycle": "paused"}
                for label, changed in (
                    ("CSRF", {"X-CSRF-Token": "wrong"}),
                    ("Origin", {"Origin": "https://foreign.example.invalid"}),
                ):
                    check(
                        label + " rejects native mutation",
                        context.request.patch(
                            base + path, data=payload, headers={**headers, **changed}
                        ).status
                        == 403,
                    )
                check(
                    "Unknown payload fields rejected",
                    context.request.patch(
                        base + path,
                        data={**payload, "portal_user_id": str(uuid4())},
                        headers=headers,
                    ).status
                    == 400,
                )
                check(
                    "Oversized payload rejected",
                    context.request.post(
                        base + WRITE,
                        data={
                            "display_name": "x" * 40000,
                            "client_request_id": str(uuid4()),
                        },
                        headers=headers,
                    ).status
                    == 400,
                )
                check(
                    "Unknown Coach ID not disclosed",
                    context.request.get(base + READ + "/" + str(uuid4())).status == 404,
                )
                check(
                    "Cross-Coach revision ID denied",
                    context.request.get(
                        base
                        + READ
                        + "/"
                        + alpha["id"]
                        + "?revision_id="
                        + json_get(context, base, READ + "/" + delta)["revision"]["id"]
                    ).status
                    == 404,
                )
                check(
                    "Production scope escalation denied",
                    context.request.post(
                        base + WRITE + "/" + alpha["id"] + "/publications/production",
                        data={
                            "expected_version": alpha["version"],
                            "revision_id": alpha["revision"]["id"],
                        },
                        headers=headers,
                    ).status
                    == 409,
                )

                async def future_calendar(c):
                    offer = await c.scalar(
                        text(
                            "INSERT INTO competence_hub.calendar_offers(coach_id,created_by_user_id,client_request_id) VALUES (:coach,:actor,:request) RETURNING id"
                        ),
                        {
                            "coach": fixture.ids["Alpha"],
                            "actor": fixture.users["admin"],
                            "request": uuid4(),
                        },
                    )
                    await c.execute(
                        text(
                            """INSERT INTO competence_hub.calendar_offer_revisions(offer_id,revision_number,topic_id,title,starts_at,ends_at,format_code,capacity,review_threshold,decision_deadline,price_display_text,created_by_user_id)
              VALUES (:offer,1,:topic,'Synthetic Future',now()+interval '7 days',now()+interval '7 days 1 hour','online',10,1,now()+interval '6 days','Synthetic',:actor)"""
                        ),
                        {
                            "offer": offer,
                            "topic": fixture.topics[0],
                            "actor": fixture.users["admin"],
                        },
                    )

                fixture.inspect(future_calendar)
                page.get_by_role(
                    "button", name="Aktuellen Stand laden", exact=True
                ).click()
                expect(
                    page.get_by_text(
                        "Vorhanden; vor Pause oder Ausscheiden zurückziehen", exact=True
                    )
                ).to_be_visible()
                check(
                    "Future Calendar offer removes offboarding actions",
                    page.get_by_role("button", name="Deaktivieren", exact=True).count()
                    == 0
                    and page.get_by_role("button", name="Pausieren", exact=True).count()
                    == 0,
                )
                check(
                    "Future Calendar offer also blocks crafted lifecycle API",
                    context.request.patch(
                        base + path, data=payload, headers=headers
                    ).status
                    == 409,
                )

                async def projection(_c):
                    from sqlalchemy.ext.asyncio import create_async_engine
                    from competence_hub_api.portal.coach_registry import (
                        public_projection,
                    )
                    from competence_hub_api.portal.postgres_coach_registry import (
                        PostgresCoachRegistryRepository,
                    )

                    engine = create_async_engine(fixture.app_url, hide_parameters=True)
                    try:
                        coach = await PostgresCoachRegistryRepository(engine).get(
                            fixture.ids["Alpha"]
                        )
                        return public_projection(
                            (coach,), "preview"
                        ), public_projection((coach,), "production")
                    finally:
                        await engine.dispose()

                preview, production = fixture.inspect(projection)
                check(
                    "Approved synthetic data produces scoped allowlisted projection",
                    len(preview["coaches"]) == 1
                    and not production["coaches"]
                    and "actor_id" not in json.dumps(preview)
                    and "evidence_ref" not in json.dumps(preview),
                )
                check(
                    "No auth material in Web Storage",
                    page.evaluate(
                        "localStorage.length===0 && sessionStorage.length===0"
                    ),
                )
                cookies = context.cookies()
                for key in ("internal", "coach", "reviewer", "contact"):
                    restricted = browser.new_context(ignore_https_errors=True)
                    other = restricted.new_page()
                    login(other, base, key)
                    # Existing Admin admission accepts internal/admin sessions only;
                    # other Portal roles are rejected as401 before the Admin role check.
                    denied_status = 403 if key == "internal" else 401
                    check(
                        key + " has no Admin navigation",
                        other.get_by_role("button", name="Coaches", exact=True).count()
                        == 0,
                    )
                    check(
                        key + " direct URL denied",
                        restricted.request.get(base + "/portal/coaches/").status
                        == denied_status,
                    )
                    check(
                        key + " direct read denied",
                        restricted.request.get(base + READ).status == denied_status,
                    )
                    check(
                        key + " direct mutation denied",
                        restricted.request.post(
                            base + WRITE,
                            data={
                                "display_name": "Forbidden",
                                "client_request_id": str(uuid4()),
                            },
                        ).status
                        == denied_status,
                    )
                    restricted.close()
                mobile = browser.new_context(
                    ignore_https_errors=True,
                    viewport={"width": 390, "height": 844},
                    reduced_motion="reduce",
                )
                mobile.add_cookies(cookies)
                small = mobile.new_page()
                enter(small, base)
                small.get_by_role("button", name="Coach Delta", exact=True).click()
                for name in (
                    "Übersicht",
                    "Profil",
                    "Themen",
                    "Kompetenzen",
                    "Angebote",
                    "Veröffentlichung",
                    "Historie",
                ):
                    tab(small, name)
                    geometry(small, "390 " + name)
                tab(small, "Profil")
                small.evaluate("scrollTo(0, 0)")
                small.screenshot(path=str(OUT / "mobile-profile.png"), full_page=True)
                small.get_by_role("button", name="Zur Coachliste", exact=True).click()
                small.get_by_role("button", name="Coach anlegen", exact=True).click()
                check(
                    "Mobile dialog contained",
                    small.get_by_role("dialog").evaluate(
                        "e=>{const b=e.getBoundingClientRect();return b.left>=0&&b.right<=innerWidth&&b.height<=innerHeight;}"
                    ),
                )
                small.get_by_role("dialog").get_by_role(
                    "button", name="Abbrechen", exact=True
                ).focus()
                small.keyboard.press("Enter")
                check(
                    "Dialog close restores focus",
                    small.get_by_role(
                        "button", name="Coach anlegen", exact=True
                    ).evaluate("e=>e===document.activeElement"),
                )
                small.keyboard.press("Enter")
                small.get_by_role("dialog").get_by_label(
                    "Anzeigename", exact=True
                ).wait_for(state="visible")
                small.keyboard.type("Coach Tastatur")
                small.keyboard.press("Tab")
                small.keyboard.press("Enter")
                expect(
                    small.locator("#coach-management-workspace .form-success")
                ).to_have_text("Gespeichert.")
                profile_tab = small.get_by_role("tab", name="Profil", exact=True)
                profile_tab.focus()
                small.keyboard.press("Enter")
                small.get_by_role(
                    "button", name="Neue Profilrevision", exact=True
                ).focus()
                small.keyboard.press("Enter")
                expect(
                    small.locator("#coach-management-workspace .form-success")
                ).to_have_text("Gespeichert.")
                small.get_by_role("tab", name="Themen", exact=True).focus()
                small.keyboard.press("Enter")
                topic = small.get_by_label("Synthetic Kommunikation", exact=False)
                topic.focus()
                small.keyboard.press("Space")
                small.get_by_role(
                    "button", name="Profilentwurf speichern", exact=True
                ).focus()
                small.keyboard.press("Enter")
                expect(
                    small.locator("#coach-management-workspace .form-success")
                ).to_have_text("Gespeichert.")
                check("Keyboard creates Coach revision checks topic and saves", True)
                mobile.close()
                with tempfile.TemporaryDirectory(
                    prefix="competencehub-coach2-zoom-"
                ) as folder:
                    defaults = Path(folder) / "Default"
                    defaults.mkdir()
                    (defaults / "Preferences").write_text(
                        json.dumps(
                            {
                                "partition": {
                                    "default_zoom_level": {
                                        "x": math.log(2) / math.log(1.2),
                                        "0": math.log(2) / math.log(1.2),
                                    }
                                }
                            }
                        ),
                        encoding="utf-8",
                    )
                    zoom = p.chromium.launch_persistent_context(
                        folder,
                        channel="msedge",
                        headless=True,
                        ignore_https_errors=True,
                        no_viewport=True,
                        args=[
                            "--window-size=1440,1000",
                            "--force-device-scale-factor=1",
                        ],
                        reduced_motion="reduce",
                    )
                    try:
                        zoom.add_cookies(cookies)
                        large = zoom.pages[0]
                        enter(large, base)
                        check(
                            "Actual 200 percent browser zoom",
                            large.evaluate(
                                "Math.abs(devicePixelRatio-2)<.05 && innerWidth<800"
                            ),
                        )
                        large.get_by_role(
                            "button", name="Coach Delta", exact=True
                        ).click()
                        for name in (
                            "Übersicht",
                            "Profil",
                            "Themen",
                            "Kompetenzen",
                            "Angebote",
                            "Veröffentlichung",
                            "Historie",
                        ):
                            tab(large, name)
                            geometry(large, "200 percent " + name)
                        large.evaluate("scrollTo(0, 0)")
                        session = zoom.new_cdp_session(large)
                        metrics = session.send("Page.getLayoutMetrics")["contentSize"]
                        shot = session.send(
                            "Page.captureScreenshot",
                            {
                                "format": "png",
                                "captureBeyondViewport": True,
                                "clip": {
                                    "x": 0,
                                    "y": 0,
                                    "width": metrics["width"],
                                    "height": metrics["height"],
                                    "scale": 1,
                                },
                            },
                        )
                        (OUT / "zoom-history.png").write_bytes(
                            base64.b64decode(shot["data"])
                        )
                        session.detach()
                    finally:
                        zoom.close()
                check("No JavaScript runtime errors", not errors)
                context.close()
            finally:
                browser.close()
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["failure_type"] = type(error).__name__
        raise
    finally:
        (OUT / "acceptance.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
    print(f"COACH2_NATIVE_BROWSER=PASS CHECKS={len(checks)}")


if __name__ == "__main__":
    main()
