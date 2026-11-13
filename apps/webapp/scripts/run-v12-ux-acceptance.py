"""Owned local PostgreSQL native V1.2 acceptance. No VPS, original login or key access."""
from datetime import datetime
import json
from pathlib import Path
import sys
from uuid import uuid4
from zoneinfo import ZoneInfo

import pyotp
from playwright.sync_api import expect,sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from local_calendar_postgres import LocalCalendarPostgres
from native_calendar_fixture import NativeCalendarFixture
from cal1_pilot_acceptance import qa
from calendar_v12_acceptance import exercise
from vps_pilot_acceptance import zoom_profile


def main():
    evidence=ROOT.parents[1]/'release-artifacts/portal-v12-ux'/uuid4().hex;evidence.mkdir(parents=True)
    report={'scope':'OWNED_LOCAL_SYNTHETIC_POSTGRES_ONLY','status':'RUNNING','server_changed':False}
    db=fixture=None;private={}
    try:
        with LocalCalendarPostgres() as db:
            fixture=NativeCalendarFixture(local_container_rehearsal=True);fixture.prepare()
            try:
                with qa.synthetic_server(fixture.app) as base,sync_playwright() as pw:
                    browser=pw.firefox.launch(headless=True)
                    try:
                        context=browser.new_context(ignore_https_errors=True,viewport={'width':1440,'height':1000},reduced_motion='reduce',locale='en-US')
                        page=context.new_page()
                        def login(actor,role):
                            with actor.expect_response(lambda response:response.url==base+'/api/v1/portal/access/session'):
                                actor.goto(base+'/portal/')
                            expect(actor.locator('#login-email')).to_be_focused()
                            actor.locator('#login-email').fill(fixture.emails[role]);actor.locator('#login-password').fill(fixture.password)
                            actor.get_by_role('button',name='Anmelden',exact=True).click()
                            if role not in private:
                                expect(actor.locator('#enrollment-code')).to_be_visible()
                                secret=actor.locator('#provisioning-secret').inner_text()
                                actor.locator('#enrollment-code').fill(pyotp.TOTP(secret).at(fixture.now.timestamp()))
                                actor.get_by_role('button',name='Einrichtung abschließen',exact=True).click()
                                expect(actor.locator('#recovery-view')).to_be_visible()
                                codes=actor.locator('#recovery-codes li').all_text_contents();assert len(codes)==10
                                private[role]=codes;actor.locator('#recovery-confirmed').check();actor.locator('#enter-portal').click()
                                expect(actor.locator('#product-tour')).to_be_visible();actor.locator('#tour-skip').click()
                            else:
                                actor.get_by_text('Recovery-Code',exact=True).click();actor.locator('#mfa-code').fill(private[role].pop())
                                actor.get_by_role('button',name='Bestätigen',exact=True).click()
                            expect(actor.locator('#portal-view')).to_be_visible()
                        login(page,'coach')
                        result=exercise(page,base,pw,login,fixture.now.astimezone(ZoneInfo('Europe/Berlin')),report,evidence,zoom_profile)
                        other=browser.new_page(ignore_https_errors=True);login(other,'coach_two')
                        assert other.request.get(base+'/api/v1/portal/calendar/offers/'+result['offer_id']).status==404
                        report['native_coach_isolation']='PASS'
                        page.reload();expect(page.locator('#portal-view')).to_be_visible()
                        page.locator('#logout-button').click();expect(page.locator('#login-view')).to_be_visible()
                        assert page.request.get(base+'/api/v1/portal/access/session').status==401
                        login(page,'coach');report['native_logout_recovery_resume']='PASS'
                        report['mfa_rbac']='PASS'
                    finally:browser.close()
            finally:
                fixture.cleanup();report['zero_residue']=fixture.cleanup_pass
        assert db.removed and db.volume_removed
        report['status']='PASS'
    except BaseException as error:
        report.update(status='FAIL',failure_type=type(error).__name__);raise
    finally:
        report.update(container_removed=bool(db and db.removed),volume_removed=bool(db and db.volume_removed))
        (evidence/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
        print('V12_UX='+report['status']+' REPORT='+str(evidence/'report.json'),flush=True)


if __name__=='__main__':main()
