"""Shared V1.2 browser cases on the installed runtime, strict TLS, own cohort."""
from datetime import datetime
import importlib.util
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import expect,sync_playwright

spec=importlib.util.spec_from_file_location('shared_v12_cases',Path(__file__).with_name('calendar_v12_acceptance.py'))
cases=importlib.util.module_from_spec(spec);spec.loader.exec_module(cases)
exercise,fill_datetime=cases.exercise,cases.fill_datetime


def fill_legacy_datetime(page,name,value):
    # The historical suite passes ISO values; only its UI entry adapter changes.
    fill_datetime(page,name,value)


def run(root,fixture,ca,directory,report,private,qa):
    with sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',locale='en-US')
            page=context.new_page()
            def login(actor,role):
                account=fixture['accounts'][role]
                with actor.expect_response(lambda response:response.url==qa.ORIGIN+qa.ACCESS+'/session'):
                    actor.goto(qa.ORIGIN+'/portal/')
                expect(actor.locator('#login-email')).to_be_focused()
                actor.locator('#login-email').fill(account['email']);actor.locator('#login-password').fill(account['password'])
                actor.get_by_role('button',name='Anmelden',exact=True).click()
                actor.get_by_text('Recovery-Code',exact=True).click()
                actor.locator('#mfa-code').fill(private[role]['recovery'].pop())
                actor.get_by_role('button',name='Bestätigen',exact=True).click()
                expect(actor.locator('#portal-view')).to_be_visible()
                status,_,raw=qa.HTTPS(ca,actor.context).call(qa.ACCESS+'/session')
                assert status==200 and json.loads(raw)['user']['roles']==[account['role']]
            login(page,'coach')
            now=datetime.fromtimestamp(root.request('clock')['server_time'],ZoneInfo('Europe/Berlin'))
            exercise(page,qa.ORIGIN,pw,login,now,report,directory,qa.zoom_profile,strict_tls=True)
            touch=browser.new_context(viewport={'width':390,'height':844},has_touch=True)
            try:
                touch.add_cookies(context.cookies());mobile=touch.new_page();mobile.goto(qa.ORIGIN+'/portal/')
                expect(mobile.locator('#portal-view')).to_be_visible()
                mobile.locator('#open-calendar-offer-dialog').tap()
                mobile.locator('[data-pick-date="starts_at"]').tap()
                mobile.locator('#calendar-date-panel .datepicker-cell.day[tabindex="0"]').tap()
                expect(mobile.locator('#calendar-starts-at')).not_to_have_value('')
                mobile.locator('[data-close-picker]').tap()
                mobile.locator('#calendar-offer-dialog [data-dialog-close]').last.tap()
                mobile.get_by_role('button',name='Änderungen verwerfen',exact=True).tap()
                expect(mobile.locator('#calendar-offer-dialog')).to_be_hidden()
                report['v12_touch']='PASS'
            finally:touch.close()
            assert len(report['cases_14'])==14
            assert sum(row['result']=='PASS' for row in report['cases_14'].values())==13
            assert report['cases_14']['3']['result']=='NOT_APPLICABLE'
            report.update(v12_ux='PASS',invitation_delivery='CLOSED_THROUGHOUT')
            return private
        finally:browser.close()
