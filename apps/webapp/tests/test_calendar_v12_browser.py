"""Real Portal UI, isolated synthetic HTTP fixture; never the open VPS tunnel."""
from contextlib import contextmanager
from datetime import datetime,timedelta
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile
from zoneinfo import ZoneInfo
import time

from playwright.sync_api import expect,sync_playwright
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'apps/webapp/scripts'))
spec=importlib.util.spec_from_file_location('calendar_v12_qa',ROOT/'apps/webapp/scripts/run-cal1-browser-acceptance.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
EVIDENCE=ROOT/'release-artifacts/portal-v12-ux'


@contextmanager
def browser_site(packaged_v11=False):
    with qa.synthetic_server() as base,sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        context=browser.new_context(ignore_https_errors=True,viewport={'width':1440,'height':1000},reduced_motion='reduce')
        page=context.new_page()
        if packaged_v11:
            archive=ROOT/'release-artifacts/webapp/competence-hub-webapp-0.1.0-38153c12159e-20261113T125945Z.zip'
            with zipfile.ZipFile(archive) as release:
                with zipfile.ZipFile(io.BytesIO(release.read(next(name for name in release.namelist() if name.endswith('.whl'))))) as wheel:
                    prefix='competence_hub_api/portal_ui/'
                    files={name[len(prefix):]:wheel.read(name) for name in wheel.namelist() if name.startswith(prefix)}
            def asset(route):
                name=route.request.url.split('/portal/',1)[1] or 'index.html'
                if name not in files:route.abort();return
                kind='text/javascript' if name.endswith(('.js','.mjs')) else 'text/css' if name.endswith('.css') else 'text/html'
                route.fulfill(status=200,body=files[name],content_type=kind)
            page.route(base+'/portal/**',asset)
        try:
            qa.login(page,base,qa.COACH_EMAIL)
            expect(page.locator('#coach-calendar-loading')).to_be_hidden()
            yield page,base,pw
        finally:context.close();browser.close()


def test_packaged_v11_held_save_proves_cancel_and_escape_are_blocked():
    with browser_site(packaged_v11=True) as (page,base,pw):
        page.locator('#open-calendar-offer-dialog').click()
        future=(datetime.now(ZoneInfo('Europe/Berlin'))+timedelta(days=10)).replace(hour=9,minute=0)
        for name,value in {'title':'DEMO blockierte Speicherung','starts-at':future.strftime('%d.%m.%Y %H:%M'),
            'ends-at':future.replace(hour=16).strftime('%d.%m.%Y %H:%M'),
            'decision-deadline':(future-timedelta(days=2)).strftime('%d.%m.%Y %H:%M'),'price':'DEMO Preis'}.items():
            page.locator('#calendar-'+name).fill(value)
        page.locator('#calendar-topic').select_option(index=1)
        held=[]
        def hold(route):
            if route.request.method=='POST':held.append(route)
            else:route.continue_()
        page.route('**/api/v1/portal/calendar/offers',hold)
        with page.expect_request(lambda request:request.method=='POST' and request.url.endswith('/calendar/offers')):
            page.locator('#save-calendar-offer').click()
        expect(page.locator('#calendar-offer-form')).to_have_attribute('aria-busy','true')
        expect(page.locator('#calendar-offer-dialog [data-dialog-close]').last).to_be_disabled()
        page.keyboard.press('Escape');expect(page.locator('#calendar-offer-dialog')).to_be_visible()
        assert len(held)==1
        EVIDENCE.mkdir(parents=True,exist_ok=True)
        page.screenshot(path=str(EVIDENCE/'before-v11-held-save.png'))


def test_source_clean_and_dirty_cancel_with_one_confirmation():
    with browser_site() as (page,base,pw):
        page.locator('#open-calendar-offer-dialog').click()
        expect(page.locator('#calendar-title')).to_be_focused()
        page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
        expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
        expect(page.locator('#calendar-discard-dialog')).to_be_hidden()
        page.locator('#open-calendar-offer-dialog').click()
        page.locator('#calendar-title').fill('DEMO Änderungen')
        page.keyboard.press('Escape')
        expect(page.locator('#calendar-discard-dialog')).to_be_visible()
        page.get_by_role('button',name='Weiter bearbeiten',exact=True).click()
        expect(page.locator('#calendar-title')).to_have_value('DEMO Änderungen')
        page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
        page.get_by_role('button',name='Änderungen verwerfen',exact=True).click()
        expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
        expect(page.locator('#open-calendar-offer-dialog')).to_be_focused()


def test_v12_fourteen_real_browser_cases():
    from calendar_v12_acceptance import exercise
    from vps_pilot_acceptance import zoom_profile
    with browser_site() as (page,base,pw):
        report={'scope':'LOCAL_SYNTHETIC_MEMORY_ONLY','cases_14':{}}
        try:
            exercise(page,base,pw,lambda actor,role:qa.login(actor,base,qa.REVIEWER_EMAIL),
                     datetime.now(ZoneInfo('Europe/Berlin')),report,EVIDENCE,zoom_profile)
            assert set(report['cases_14'])=={str(number) for number in range(1,15)}
        finally:
            EVIDENCE.mkdir(parents=True,exist_ok=True)
            (EVIDENCE/'memory-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')


@pytest.mark.parametrize('timeout',[False,True])
def test_held_save_can_be_discarded_and_late_reply_never_closes_a_new_form(timeout):
    from calendar_v12_acceptance import fill_datetime
    with browser_site() as (page,base,pw):
        errors=[];page.on('pageerror',lambda error:errors.append(error.name))
        page.locator('#open-calendar-offer-dialog').click()
        page.locator('#calendar-title').fill('DEMO Speicherung vor Antwort bereits erfolgt')
        page.locator('#calendar-topic').select_option(index=1)
        future=(datetime.now(ZoneInfo('Europe/Berlin'))+timedelta(days=8)).replace(hour=9,minute=0)
        for name,value in [('starts-at',future),('ends-at',future.replace(hour=16)),('decision-deadline',future-timedelta(days=2))]:fill_datetime(page,name,value)
        page.locator('#calendar-price').fill('DEMO Preis');held=[]
        def delay_reply(route):
            if route.request.method!='POST':route.continue_();return
            response=route.fetch();held.append((route,response))
        page.route('**/api/v1/portal/calendar/offers',delay_reply)
        if timeout:page.clock.install()
        page.locator('#save-calendar-offer').click()
        deadline=time.monotonic()+10
        while not held and time.monotonic()<deadline:page.wait_for_timeout(20)
        assert held and held[0][1].status==201
        expect(page.locator('#calendar-offer-form')).to_have_attribute('aria-busy','true')
        expect(page.locator('#calendar-offer-dialog [data-dialog-close]').last).to_be_enabled()
        if timeout:
            page.clock.fast_forward(31000)
            expect(page.locator('#calendar-offer-form')).to_have_attribute('aria-busy','false')
            expect(page.locator('#calendar-offer-error')).to_contain_text('Speicherung dauert zu lange')
        page.keyboard.press('Escape');expect(page.locator('#calendar-discard-dialog')).to_be_visible()
        if not timeout:expect(page.locator('[data-saving-note]')).to_be_visible()
        page.get_by_role('button',name='Änderungen verwerfen',exact=True).click()
        expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
        expect(page.get_by_role('heading',name='DEMO Speicherung vor Antwort bereits erfolgt',exact=True)).to_be_visible()
        page.locator('#open-calendar-offer-dialog').click();page.locator('#calendar-title').fill('DEMO Neuer unabhängiger Entwurf')
        held[0][0].fulfill(response=held[0][1])
        page.evaluate('async()=>{await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);}')
        expect(page.locator('#calendar-title')).to_have_value('DEMO Neuer unabhängiger Entwurf')
        expect(page.locator('#calendar-offer-dialog')).to_be_visible()
        assert not errors


def test_repeated_cancel_is_one_dialog_and_internal_logout_can_leave():
    with browser_site() as (page,base,pw):
        page.locator('#open-calendar-offer-dialog').click();page.locator('#calendar-title').fill('DEMO Keine Fokusfalle')
        page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
        page.locator('#calendar-offer-dialog [data-dialog-close]').last.evaluate('button=>{button.click();button.click();button.click();}')
        expect(page.get_by_role('alertdialog',name='Änderungen verwerfen?')).to_have_count(1)
        expect(page.get_by_role('button',name='Weiter bearbeiten',exact=True)).to_be_focused()
        page.get_by_role('button',name='Weiter bearbeiten',exact=True).click()
        expect(page.locator('#calendar-title')).to_have_value('DEMO Keine Fokusfalle')
        # Header is intentionally inert behind a modal; exercise the existing
        # navigation event path without pretending a pointer can click through it.
        page.locator('#logout-button').evaluate('button=>button.click()')
        expect(page.locator('#calendar-discard-dialog')).to_be_visible()
        page.get_by_role('button',name='Änderungen verwerfen',exact=True).click()
        expect(page.locator('#login-view')).to_be_visible()
        assert page.request.get(base+'/api/v1/portal/access/session').status==401


def test_picker_year_boundary_and_legacy_minutes_without_rounding():
    from calendar_v12_acceptance import select_date,fill_datetime
    with browser_site() as (page,base,pw):
        page.locator('#open-calendar-offer-dialog').click()
        starts=datetime(2026,12,31,9,tzinfo=ZoneInfo('Europe/Berlin'));ends=datetime(2027,1,2,16,tzinfo=ZoneInfo('Europe/Berlin'))
        select_date(page,'starts_at',starts);select_date(page,'ends_at',ends)
        expect(page.locator('#calendar-date-panel .cal-range-middle')).to_have_count(1)
        expect(page.locator('#calendar-ends-at')).to_have_value('02.01.2027')
        page.locator('[data-close-picker]').click()
        page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
        page.get_by_role('button',name='Änderungen verwerfen',exact=True).click()
        # Create an owned synthetic historical-minute record through the real API.
        # No original VPS credentials or database is used by this test.
        from uuid import uuid4
        csrf=page.request.post(base+'/api/v1/portal/access/session/csrf',headers={'Origin':base}).headers['x-csrf-token']
        original='2026-12-31T08:18:27.123456Z'
        payload={'client_request_id':str(uuid4()),'draft':{'title':'DEMO Historische Minuten','topic_id':'00000000-0000-4000-8000-000000000920',
            'summary':None,'starts_at':original,'ends_at':'2026-12-31T15:18:27.123456Z',
            'decision_deadline':'2026-12-29T11:00:00Z','time_zone':'Europe/Berlin','format':'online',
            'public_location':None,'capacity':10,'review_threshold':5,'price_display_text':'DEMO Preis'}}
        created=page.request.post(base+'/api/v1/portal/calendar/offers',data=payload,headers={'Origin':base,'X-CSRF-Token':csrf})
        assert created.status==201;identifier=created.json()['id']
        page.reload();expect(page.locator('#coach-calendar-loading')).to_be_hidden()
        row=page.locator('#coach-calendar-list .calendar-card').filter(has=page.get_by_role('heading',name='DEMO Historische Minuten',exact=True))
        row.get_by_role('button',name='Entwurf bearbeiten',exact=True).click()
        expect(page.locator('#calendar-starts-at-minute')).to_have_value('18')
        expect(page.locator('#calendar-ends-at-minute')).to_have_value('18')
        assert page.locator('#calendar-starts-at-hour').count()==1 and page.locator('#calendar-starts-at-minute').count()==1
        page.locator('#save-calendar-offer').click();expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
        after=page.request.get(base+'/api/v1/portal/calendar/offers/'+identifier).json()['current_revision']
        assert datetime.fromisoformat(after['starts_at'])==datetime.fromisoformat(original)
        assert datetime.fromisoformat(after['ends_at'])==datetime.fromisoformat(payload['draft']['ends_at'])


def test_390_touch_selects_date_without_drag_or_keyboard_dependency():
    with browser_site() as (page,base,pw):
        context=page.context.browser.new_context(ignore_https_errors=True,has_touch=True,viewport={'width':390,'height':844})
        try:
            touch=context.new_page();qa.login(touch,base,qa.COACH_EMAIL)
            touch.locator('#open-calendar-offer-dialog').tap()
            touch.evaluate('document.addEventListener("pointerdown",event=>window.lastPointerType=event.pointerType)')
            touch.locator('[data-pick-date="starts_at"]').tap()
            touch.locator('#calendar-date-panel .datepicker-cell.day[tabindex="0"]').tap()
            assert touch.evaluate('lastPointerType')=='touch'
            assert len(touch.locator('#calendar-starts-at').input_value())==10
            assert touch.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            touch.screenshot(path=str(EVIDENCE/'touch390-picker.png'))
        finally:context.close()


def test_local_calendar_demo_prefill_uses_the_same_date_and_clock_controls():
    from cal1_demo_app import create_demo_app
    with qa.synthetic_server(create_demo_app) as base,sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            page=browser.new_page(ignore_https_errors=True);qa.login(page,base,qa.COACH_EMAIL)
            page.locator('#open-calendar-offer-dialog').click();page.get_by_role('button',name='Demo-Werte einsetzen',exact=True).click()
            assert len(page.locator('#calendar-starts-at').input_value())==10
            assert page.locator('#calendar-starts-at-hour').input_value() and page.locator('#calendar-starts-at-minute').input_value()=='00'
            page.locator('#save-calendar-offer').click();expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
            expect(page.get_by_role('heading',name='DEMO: Teamworkshop',exact=True)).to_be_visible()
        finally:browser.close()
