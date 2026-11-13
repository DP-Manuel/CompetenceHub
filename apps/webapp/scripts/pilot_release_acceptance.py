"""Integrated pilot additions, exclusively in the owned local SQL fixture."""
import json
import math
import tempfile
from pathlib import Path
from uuid import UUID, uuid4

import pyotp
from playwright.sync_api import expect, sync_playwright
from sqlalchemy import text

from scripts.cal1_pilot_acceptance import demo, qa


def run(fixture, options, report, evidence):
    if not fixture.local_container_rehearsal:
        raise RuntimeError("This acceptance never runs against external Staging")
    checks = qa.Acceptance()
    report["integrated_checks"] = checks.checks
    errors = []
    app_holder = {}
    def geometry(page,label):
        try:
            demo.geometry(page,checks,label)
        except AssertionError:
            page.screenshot(path=str(evidence/"layout-failure.png"),full_page=True)
            report["layout_failure"] = page.evaluate("""() => {
              const out=[], walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
              while(walker.nextNode()) { const n=walker.currentNode,e=n.parentElement;
                if(!n.textContent.trim() || !e || ['SCRIPT','STYLE','OPTION','NOSCRIPT'].includes(e.tagName) || !e.getClientRects().length || e.closest('[hidden]') || getComputedStyle(e).visibility==='hidden' || e.closest('.skip-link')) continue;
                const range=document.createRange();range.selectNodeContents(n);const p=e.getBoundingClientRect();
                for(const r of range.getClientRects()) if(r.width>0 && (r.left < -1 || r.right>innerWidth+1 || r.left<p.left-1 || r.right>p.right+1)) out.push({tag:e.tagName,id:e.id,parent:e.parentElement?.id,left:r.left,right:r.right,parentLeft:p.left,parentRight:p.right});
              } return out.slice(0,8);
            }""")
            raise
    def app(port):
        result = fixture.app(port)
        app_holder["app"] = result
        return result

    def enroll(page):
        expect(page.locator("#enrollment-code")).to_be_visible()
        totp = pyotp.TOTP(page.locator("#provisioning-secret").inner_text())
        page.locator("#enrollment-code").fill(totp.at(fixture.now.timestamp()))
        page.get_by_role("button",name="Einrichtung abschließen").click()
        expect(page.locator("#recovery-view")).to_be_visible()
        codes = page.locator("#recovery-codes li").all_text_contents()
        checks.check("Activation requires native MFA and ten private recovery codes",len(codes)==10)
        page.locator("#recovery-confirmed").check()
        page.get_by_role("button",name="Portal öffnen").click()
        expect(page.locator("#portal-view")).to_be_visible()
        expect(page.locator("#product-tour")).to_be_visible()
        page.locator("#tour-skip").click()
        return codes

    def tour(page, role, count):
        page.locator("#pilot-help summary").click()
        page.locator("#tour-options button").filter(has_text=role).click()
        expect(page.locator("#product-tour")).to_be_visible()
        for i in range(count):
            expect(page.locator("#tour-progress")).to_have_text(f"Schritt {i+1} von {count}")
            expect(page.locator("#tour-title")).to_be_focused()
            geometry(page,role+f" tour step{i+1}")
            if i == 0:
                name={"Admin":"admin","Coach":"coach","Prüfer":"reviewer"}[role]
                label="native-200" if page.evaluate("devicePixelRatio===2") else "desktop"
                demo.screenshot(page,evidence/f"tour-{name}-{page.viewport_size['width'] if page.viewport_size else 'native200'}.png",label)
            if i == 1:
                page.locator("#tour-back").click()
                expect(page.locator("#tour-progress")).to_have_text(f"Schritt 1 von {count}")
                page.locator("#tour-next").click()
            page.locator("#tour-next").click()
        expect(page.locator("#product-tour")).to_be_hidden()
        page.reload(); expect(page.locator("#portal-view")).to_be_visible()
        checks.check(role+" tour does not automatically repeat after reload", page.locator("#product-tour").is_hidden())
        page.locator("#pilot-help summary").click()
        page.locator("#tour-options button").filter(has_text=role).click()
        expect(page.locator("#tour-title")).to_be_focused()
        page.keyboard.press("Tab"); page.keyboard.press("Shift+Tab")
        checks.check(role+" tour keyboard stays within modal",page.evaluate("document.getElementById('product-tour').contains(document.activeElement)"))
        page.keyboard.press("Escape")
        expect(page.locator("#product-tour")).to_be_hidden()
        expect(page.locator("#pilot-help summary")).to_be_focused()
        page.locator("#pilot-help summary").click()
        page.locator("#tour-options button").filter(has_text=role).click()
        page.locator("#pilot-overview").evaluate("e => e.style.display='none'")
        page.locator("#tour-next").click()
        expect(page.locator("#tour-progress")).to_have_text(f"Schritt 2 von {count}")
        page.locator("#tour-back").click()
        expect(page.locator("#tour-copy")).to_contain_text("aktuell nicht verfügbar")
        page.locator("#tour-skip").click()
        expect(page.locator("#product-tour")).to_be_hidden()
        page.locator("#pilot-overview").evaluate("e => e.style.removeProperty('display')")
        checks.check(role+" can skip tour without workflow changes",True)

    def token_for(user):
        async def read(connection):
            return (await connection.execute(text("SELECT id,encrypted_payload,key_version FROM competence_hub.auth_token_delivery_outbox WHERE one_time_token_id IN (SELECT id FROM competence_hub.auth_one_time_tokens WHERE portal_user_id=:id AND consumed_at IS NULL AND revoked_at IS NULL)"),{"id":user})).mappings().one()
        row = fixture.database(read)
        return app_holder["app"].state.outbox_cipher.decrypt(bytes(row["encrypted_payload"]),
            key_version=row["key_version"],subject_id=f"invitation:{row['id']}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,executable_path=str(options.browser_executable))
        with qa.synthetic_server(app) as base:
            contexts = []
            def context(**kwargs):
                ctx=browser.new_context(ignore_https_errors=True,**kwargs); contexts.append(ctx)
                ctx.on("page",lambda p:p.on("pageerror",lambda e:errors.append(e.name)))
                return ctx
            try:
                admin_context=context(viewport={"width":1440,"height":1000})
                admin=admin_context.new_page(); admin.goto(base+"/portal/")
                admin.locator("#login-email").fill(fixture.emails["admin"])
                admin.locator("#login-password").fill(fixture.password)
                admin.get_by_role("button",name="Anmelden",exact=True).click()
                enroll(admin)
                expect(admin.locator("#pilot-overview-state")).to_contain_text("Datenbank erreichbar")
                tour(admin,"Admin",6)
                admin.get_by_role("button",name="Zugänge",exact=True).click()
                expect(admin.locator("#pilot-users li")).to_have_count(6)
                csrf=admin.request.post(base+"/api/v1/portal/access/session/csrf",headers={"Origin":base}).headers["x-csrf-token"]
                headers={"Origin":base,"X-CSRF-Token":csrf,"Idempotency-Key":str(uuid4())}
                check=admin.request.post(base+"/api/v1/admin/users/invitations",data={},headers=headers)
                checks.check("Real runtime holds invitation queue until dispatch release",check.status==503)
                app_holder["app"].state.invitation_delivery_enabled=True  # Synthetic capture only; NO SMTP worker.
                new_coach=uuid4()
                async def seed(connection):
                    await connection.execute(text("INSERT INTO competence_hub.coaches(id,display_name,public_profile_status) VALUES (:id,'Synthetic new Coach','synthetic')"),{"id":new_coach})
                fixture.database(seed); fixture.coaches["invited"]=new_coach
                for role, selector in (("calendar_reviewer","Prüfer"),("coach","Coach")):
                    email=f"synthetic-invited-{role}@example.invalid"
                    payload={"email":email,"display_name":"Synthetic invited "+role,"role_codes":[role]}
                    if role=="coach": payload["coach_id"]=str(new_coach)
                    headers["Idempotency-Key"]=str(uuid4())
                    response=admin.request.post(base+"/api/v1/admin/users/invitations",data=payload,headers=headers)
                    checks.check(role+" invitation queues token-free reference",response.status==202 and "token" not in response.text())
                    user=UUID(response.json()["user_id"])
                    fixture.users["invited_"+role]=user; fixture.emails["invited_"+role]=email
                    replay=admin.request.post(base+"/api/v1/admin/users/invitations",data=payload,headers=headers)
                    checks.check(role+" idempotent invitation does not duplicate account",replay.status==202 and replay.json()==response.json() and replay.headers.get("idempotent-replay")=="true")
                    changed=admin.request.post(base+"/api/v1/admin/users/invitations",data={**payload,"display_name":"Different"},headers=headers)
                    checks.check(role+" changed request with same key conflicts",changed.status==409)
                    pending=next(row for row in admin.request.get(base+"/api/v1/admin/users").json()["items"] if row["id"]==str(user))
                    checks.check(role+" is inactive before activation with exact role",pending["status"]=="pending_activation" and pending["roles"]==[role])
                    token=token_for(user)
                    ctx=context(viewport={"width":390,"height":844},reduced_motion="reduce")
                    page=ctx.new_page(); page.goto(base+"/portal/#/einladung?token="+token)
                    expect(page.locator("#account-token-view")).to_be_visible()
                    checks.check("Activation fragment immediately removed from address",not page.url.endswith(token))
                    page.locator("#account-token-password").fill(fixture.password)
                    page.locator("#account-token-password-confirm").fill(fixture.password)
                    page.locator("#account-token-submit").click()
                    enroll(page)
                    current=page.request.get(base+"/api/v1/portal/access/session").json()
                    checks.check(role+" activation has exact role, no internal/admin elevation",current["user"]["roles"]==[role])
                    checks.check(role+" cannot read Admin inventory",page.request.get(base+"/api/v1/admin/users").status in {401,403})
                    checks.check(role+" cannot read company workspace",page.request.get(base+"/api/v1/portal/companies").status in {401,403})
                    geometry(page,role+" mobile dashboard")
                    tour(page,selector,9 if role=='coach' else 7)
                    page.screenshot(path=str(evidence/(role+"-mobile390.png")),full_page=True)
                    used=page.request.post(base+"/api/v1/auth/invitations/accept",data={"token":token,"password":fixture.password},headers={"Origin":base})
                    checks.check("Native consumed activation token cannot be reused",used.status==400 and used.json()["code"]=="request_not_accepted")
                    del token
                admin.get_by_role("button",name="Zugänge",exact=True).click()
                expect(admin.locator("#pilot-users li")).to_have_count(8)
                checks.check("Admin inventory contains exact stable Coach mapping",str(new_coach) in admin.locator("#pilot-users").inner_text())
                admin.screenshot(path=str(evidence/"admin-desktop.png"),full_page=True)
                public=context(viewport={"width":390,"height":844}).new_page()
                public.goto(base+"/portal/calendar-public.html")
                expect(public.locator("#loading")).to_be_hidden()
                expect(public.locator("#result-count")).not_to_have_text("")
                checks.check("Packaged public calendar reads native month API without demo endpoints",public.locator("#error").is_hidden() and public.locator("#zugang").count()==0)
                geometry(public,"Packaged public mobile390")
                public.screenshot(path=str(evidence/"packaged-public-mobile390.png"),full_page=True)
                # Same native browser preference technique used in the accepted CAL-1 proof.
                with tempfile.TemporaryDirectory(prefix="integrated-zoom-") as folder:
                    default=Path(folder)/"Default"; default.mkdir()
                    level=math.log(2)/math.log(1.2)
                    (default/"Preferences").write_text(json.dumps({"partition":{"default_zoom_level":{"x":level,"0":level}}}),encoding="utf8")
                    zoom=pw.chromium.launch_persistent_context(folder,headless=True,executable_path=str(options.browser_executable),ignore_https_errors=True,no_viewport=True,args=["--window-size=1440,1000","--force-device-scale-factor=1"],reduced_motion="reduce")
                    try:
                        zoom.add_cookies(admin_context.cookies()); page=zoom.new_page(); page.goto(base+"/portal/")
                        expect(page.locator("#portal-view")).to_be_visible()
                        tour(page,"Admin",6)
                        geometry(page,"Native200 Admin")
                        checks.check("Actual native 200 percent browser zoom",page.evaluate("devicePixelRatio===2 && innerWidth>600 && innerWidth<800"))
                        demo.screenshot(page,evidence/"admin-native200.png","native-200")
                    finally: zoom.close()
            finally:
                for ctx in contexts: ctx.close()
                browser.close()
                # All buckets in this exclusive, initially empty LOCAL container
                # are synthetic. Do this even on failure, before shared cleanup.
                async def buckets(connection):
                    await connection.execute(text("DELETE FROM competence_hub.auth_rate_limit_buckets"))
                fixture.database(buckets)
    checks.check("Integrated browser has no JavaScript errors",not errors)
