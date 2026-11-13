"""V1.1 real-form acceptance in an owned disposable PostgreSQL fixture only."""
import json
import re
from pathlib import Path
import sys
import tempfile
from uuid import uuid4

import pyotp
from icalendar import Calendar
from playwright.sync_api import expect, sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts'))
from scripts.local_calendar_postgres import LocalCalendarPostgres
from scripts.native_calendar_fixture import NativeCalendarFixture
from scripts.cal1_pilot_acceptance import qa
from scripts.vps_pilot_acceptance import zoom_profile


def main():
    evidence=ROOT.parents[1]/'release-artifacts/portal-v11-ux'/uuid4().hex;evidence.mkdir(parents=True)
    report={'scope':'OWNED_LOCAL_SYNTHETIC_POSTGRES_ONLY','status':'RUNNING','checks':[]}
    db=fixture=None
    def check(label,value=True):
        report['last_check']=label
        if not value:raise AssertionError(label)
        report['checks'].append(label);print('PASS | '+label,flush=True)
    private={};errors=[]
    try:
        with LocalCalendarPostgres() as db:
            fixture=NativeCalendarFixture(local_container_rehearsal=True);fixture.prepare()
            try:
                with qa.synthetic_server(fixture.app) as base, sync_playwright() as pw:
                    browser=pw.firefox.launch(headless=True)
                    contexts=[]
                    def new():
                        context=browser.new_context(ignore_https_errors=True,locale='en-US',viewport={'width':1440,'height':1000})
                        contexts.append(context);page=context.new_page()
                        page.on('pageerror',lambda error:errors.append({'type':error.name,'locations':re.findall(r'/portal/[a-z0-9.-]+:\d+:\d+',error.stack or '')}))
                        return page
                    def login(page,key):
                        with page.expect_response(lambda r:r.url==base+'/api/v1/portal/access/session'):
                            page.goto(base+'/portal/')
                        expect(page.locator('#login-email')).to_be_focused()
                        page.locator('#login-email').fill(fixture.emails[key]);page.locator('#login-password').fill(fixture.password)
                        page.get_by_role('button',name='Anmelden',exact=True).click()
                        if key not in private:
                            expect(page.locator('#enrollment-code')).to_be_visible()
                            totp=pyotp.TOTP(page.locator('#provisioning-secret').inner_text())
                            page.locator('#enrollment-code').fill(totp.at(fixture.now.timestamp()))
                            page.get_by_role('button',name='Einrichtung abschließen').click()
                            expect(page.locator('#recovery-view')).to_be_visible()
                            private[key]=page.locator('#recovery-codes li').all_text_contents()
                            page.locator('#recovery-confirmed').check();page.locator('#enter-portal').click()
                            expect(page.locator('#product-tour')).to_be_visible();page.locator('#tour-skip').click()
                        else:
                            page.get_by_text('Recovery-Code',exact=True).click();page.locator('#mfa-code').fill(private[key].pop())
                            page.get_by_role('button',name='Bestätigen',exact=True).click()
                        expect(page.locator('#portal-view')).to_be_visible()
                    def card(page,title,review=False):
                        return page.locator('#review-calendar-list .calendar-card' if review else '#coach-calendar-list .calendar-card').filter(has=page.get_by_role('heading',name=title,exact=True))
                    def fill(page,title,start,end,deadline,keyboard=False):
                        if keyboard:
                            page.locator('#open-calendar-offer-dialog').focus();page.keyboard.press('Enter')
                        else:page.locator('#open-calendar-offer-dialog').click()
                        for control,value in {'title':title,'starts-at':start,'ends-at':end,'decision-deadline':deadline,
                            'capacity':'10','review-threshold':'5','price':'Preis nach Abstimmung'}.items():page.locator('#calendar-'+control).fill(value)
                        page.locator('#calendar-topic').select_option(str(fixture.topic))
                    def save(page):
                        page.locator('#save-calendar-offer').click();expect(page.locator('#calendar-offer-dialog')).to_be_hidden(timeout=15000)
                        expect(page.locator('#coach-calendar-loading')).to_be_hidden()
                    def submit(page,title):
                        with page.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/submit')) as sent:
                            card(page,title).get_by_role('button',name='Zur Prüfung einreichen',exact=True).click()
                        check('Native submit response200',sent.value.status==200)
                        expect(card(page,title)).to_contain_text('Zur Prüfung eingereicht',timeout=15000)
                    def review(page,title,outcome,note=''):
                        with page.expect_response(lambda r:r.request.method=='GET' and '/review-queue' in r.url):
                            page.locator('#refresh-review-queue').click()
                        expect(page.locator('#review-calendar-loading')).to_be_hidden()
                        card(page,title,True).get_by_role('button',name='Angebot prüfen',exact=True).click()
                        expect(page.locator('#calendar-review-dialog')).to_be_visible()
                        expect(page.locator('#calendar-review-summary')).to_contain_text(title)
                        page.locator(f'input[name="outcome"][value="{outcome}"]').check()
                        page.locator('#calendar-review-note').fill(note)
                        validity=page.locator('#calendar-review-form').evaluate('''form=>({valid:form.checkValidity(),busy:form.getAttribute('aria-busy'),controls:[...form.elements].map(e=>({name:e.name,type:e.type,checked:e.checked,disabled:e.disabled,valid:e.validity?.valid}))})''')
                        report.setdefault('review_form_states',[]).append(validity)
                        check('Review controls valid and enabled before submit',validity['valid'] and validity['busy']!='true')
                        with page.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/review-decisions'),timeout=30000) as submitted:
                            page.get_by_role('button',name='Entscheidung speichern',exact=True).click()
                        check('Native review response '+outcome+' '+str(submitted.value.status),submitted.value.status==200)
                        expect(page.locator('#calendar-review-dialog')).to_be_hidden(timeout=15000)
                    def tour(page,label,count):
                        if page.locator('#pilot-help').get_attribute('open') is None:page.locator('#pilot-help summary').click()
                        page.get_by_role('button',name=label,exact=True).click()
                        for number in range(1,count+1):
                            expect(page.locator('#tour-progress')).to_have_text(f'Schritt {number} von {count}')
                            expect(page.locator('#tour-title')).to_be_focused();page.locator('#tour-next').click()
                        expect(page.locator('#product-tour')).to_be_hidden()
                        if page.locator('#pilot-help').get_attribute('open') is None:page.locator('#pilot-help summary').click()
                        page.get_by_role('button',name=label,exact=True).click();page.locator('#tour-skip').click()
                        expect(page.locator('#pilot-help summary')).to_be_focused()
                    def layout(page,label):
                        check(label,page.evaluate('''() => {
                          if(document.documentElement.scrollWidth>innerWidth+1)return false;
                          return [...document.querySelectorAll('dialog[open] input,dialog[open] select,.product-tour[open]')]
                            .filter(e=>e.getClientRects().length).every(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.left>=0&&r.right<=innerWidth+1;});
                        }'''))
                    try:
                        coach=new();reviewer=new();admin=new();other=new()
                        for page,key in [(coach,'coach'),(reviewer,'reviewer'),(admin,'admin'),(other,'coach_two')]:login(page,key)
                        check('Native MFA and exact Coach/Reviewer/Admin logins',len(private)==4)
                        denied=[page.request.get(base+'/api/v1/admin/users').status for page in (coach,reviewer,other)]
                        report['non_admin_http_statuses']=denied
                        check('Reviewer and Coach cannot open Admin user API '+str(denied),all(status in (401,403) for status in denied))
                        check('Admin inventory remains available',admin.request.get(base+'/api/v1/admin/users').status==200)
                        coach.locator('#open-calendar-offer-dialog').click();coach.locator('#save-calendar-offer').click()
                        expect(coach.locator('#calendar-title')).to_be_focused()
                        expect(coach.locator('#calendar-title')).to_have_attribute('aria-invalid','true')
                        check('Multiple empty fields focus the first field in visual order')
                        coach.locator('#calendar-offer-dialog').get_by_role('button',name='Abbrechen',exact=True).click()
                        fill(coach,'V11 Eintägiger Workshop','20.11.2026 09:00','20.11.2026 16:00','19.11.2026 12:00')
                        check('Explicit German text controls even in en-US browser',coach.locator('#calendar-starts-at').get_attribute('type')=='text')
                        check('24 hours and quarter-hour choices',coach.locator('#calendar-starts-at-hour option').count()==25 and coach.locator('#calendar-starts-at-minute option').count()==5)
                        coach.locator('#calendar-review-threshold').fill('11');coach.locator('#save-calendar-offer').click()
                        expect(coach.locator('#calendar-review-threshold')).to_be_focused()
                        expect(coach.locator('#calendar-review-threshold-error')).to_contain_text('10')
                        expect(coach.locator('#calendar-title')).to_have_value('V11 Eintägiger Workshop')
                        check('Threshold error is field-specific, focused and preserves inputs')
                        coach.locator('#calendar-review-threshold').fill('5');coach.locator('#calendar-ends-at').fill('20.11.2026 08:00');coach.locator('#save-calendar-offer').click()
                        expect(coach.locator('#calendar-ends-at')).to_be_focused();expect(coach.locator('#calendar-ends-at-error')).to_contain_text('20.11.2026 10:00')
                        coach.locator('#calendar-ends-at').fill('20.11.2026 16:00')
                        coach.screenshot(path=str(evidence/'desktop-form.png'),full_page=True)
                        save(coach)
                        rows=qa.api_offers(coach);one=next(row for row in rows if row['title']=='V11 Eintägiger Workshop')
                        offer_id=one['id'];detail=coach.request.get(base+'/api/v1/portal/calendar/offers/'+offer_id).json()['current_revision']
                        check('20.11.2026 one-day draft saved with optional empty summary',detail['summary'] is None and detail['starts_at'].startswith('2026-11-20T08:00') and detail['ends_at'].startswith('2026-11-20T15:00'))
                        check('Draft ICS remains unavailable',new().request.get(base+'/api/v1/calendar/offers/'+offer_id+'/calendar.ics').status==404)
                        card(coach,one['title']).get_by_role('button',name='Entwurf bearbeiten',exact=True).click()
                        expect(coach.locator('#calendar-starts-at')).to_have_value('20.11.2026 09:00')
                        coach.locator('#calendar-starts-at-minute').select_option('15');expect(coach.locator('#calendar-starts-at')).to_have_value('20.11.2026 09:15')
                        coach.locator('#calendar-starts-at').fill('20.11.2026 09:18');save(coach)
                        card(coach,one['title']).get_by_role('button',name='Entwurf bearbeiten',exact=True).click()
                        expect(coach.locator('#calendar-starts-at-minute')).to_have_value('18');save(coach)
                        check('Keyboard minute18 survives saving and editing without rounding')
                        submit(coach,one['title'])
                        review(reviewer,one['title'],'changes_requested','Bitte die Kurzbeschreibung ergänzen.')
                        coach.reload();card(coach,one['title']).get_by_role('button',name='Neue Revision bearbeiten',exact=True).click()
                        coach.locator('#calendar-summary').fill('Eintägiger Workshop zur gesunden Mitarbeiterführung.')
                        coach.locator('#calendar-starts-at').fill('20.11.2026 09:00');save(coach)
                        submit(coach,one['title'])
                        review(reviewer,one['title'],'published');check('One-day course revision2 submitted, changes requested, revised and published')
                        check('Coach isolation remains native',other.request.get(base+'/api/v1/portal/calendar/offers/'+offer_id).status in (403,404))
                        fill(coach,'V11 Mehrtägiger Workshop','28.11.2026 17:18','29.11.2026 17:18','25.11.2026 12:00');save(coach)
                        submit(coach,'V11 Mehrtägiger Workshop')
                        review(reviewer,'V11 Mehrtägiger Workshop','published');check('Multiday course saved, submitted and published')
                        public=new();public.goto(base+'/portal/calendar-public.html');expect(public.locator('#loading')).to_be_hidden()
                        expect(public.locator('#grid [data-offer]').filter(has_text='V11 Eintägiger Workshop')).to_have_count(1)
                        single=public.request.get(base+'/api/v1/calendar/offers/'+offer_id).json()
                        check('Published one-day course retains exact09-16 interval and public-only projection',
                              single['starts_at'].startswith('2026-11-20T08:00') and single['ends_at'].startswith('2026-11-20T15:00')
                              and not {'review_threshold','review_decision','reviewer_id','workflow_status'}.intersection(single))
                        segments=public.locator('#grid [data-offer]').filter(has_text='V11 Mehrtägiger Workshop');expect(segments).to_have_count(2)
                        for index in range(2):segments.nth(index).click();expect(public.locator('#detail-title')).to_have_text('V11 Mehrtägiger Workshop')
                        expect(public.locator('#ics')).to_have_text('Zum Kalender hinzufügen (.ics)')
                        with public.expect_download() as downloaded:public.locator('#ics').click()
                        event=Calendar.from_ical(Path(downloaded.value.path()).read_bytes()).walk('VEVENT')[0]
                        check('Public multiday segments share details and actual ICS download',str(event['DTSTART'].dt).startswith('2026-11-28 17:18') and str(event['DTEND'].dt).startswith('2026-11-29 17:18'))
                        public.locator('#seats').fill('2');public.get_by_role('button',name='Anfrageentwurf vorbereiten',exact=True).click()
                        expect(public.locator('#request-draft')).to_have_value(re.compile('.*V11 Mehrtägiger Workshop.*',re.S));check('Public request draft created without sending')
                        public.locator('#calendar-help').click()
                        public.emulate_media(reduced_motion='reduce')
                        check('Reduced Motion preference is active',public.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'))
                        for number in range(3):public.locator('#tour-next').click()
                        expect(public.locator('#product-tour')).to_be_hidden();expect(public.locator('#calendar-help')).to_be_focused()
                        public.locator('#calendar-help').click();public.locator('#tour-skip').click();check('Calendar tour complete, restartable, skippable and returns focus')
                        tour(coach,'Coach-Einführung starten',9);tour(reviewer,'Prüfer-Einführung starten',7);check('Coach and Reviewer tours complete, restartable and keyboard focused')
                        fill(coach,'V11 API Validierung','24.11.2026 09:00','24.11.2026 16:00','23.11.2026 12:00')
                        coach.set_viewport_size({'width':390,'height':844})
                        def invalid_native(route):
                            if route.request.method!='POST':route.continue_();return
                            payload=route.request.post_data_json;payload['draft']['review_threshold']=11
                            route.continue_(post_data=json.dumps(payload))
                        coach.route('**/api/v1/portal/calendar/offers',invalid_native)
                        coach.locator('#save-calendar-offer').click();expect(coach.locator('#calendar-review-threshold')).to_be_focused()
                        check('Actual backend400 field error translated without losing title',coach.locator('#calendar-title').input_value()=='V11 API Validierung')
                        coach.unroute('**/api/v1/portal/calendar/offers',invalid_native)
                        layout(coach,'390px form controls fit')
                        check('Mobile invalid field and its example remain visible',coach.locator('#calendar-review-threshold').evaluate('e=>{const r=e.getBoundingClientRect(),m=document.querySelector("#calendar-review-threshold-error").getBoundingClientRect();return r.top>=0&&m.bottom<=innerHeight;}'))
                        coach.screenshot(path=str(evidence/'mobile-form-errors.png'))
                        coach.locator('#calendar-starts-at').focus();coach.keyboard.press('Tab');expect(coach.locator('#calendar-starts-at-hour')).to_be_focused();check('Date and time controls are keyboard reachable')
                        coach.once('dialog',lambda dialog:dialog.accept());coach.locator('#calendar-offer-dialog').get_by_role('button',name='Abbrechen',exact=True).click()
                        with tempfile.TemporaryDirectory(dir=evidence) as profile:
                            zoom_profile(pw,Path(profile));zoom=pw.firefox.launch_persistent_context(profile,headless=True,ignore_https_errors=True,no_viewport=True)
                            try:
                                zoom.add_cookies(coach.context.cookies());page=zoom.pages[0];page.goto(base+'/portal/');expect(page.locator('#portal-view')).to_be_visible()
                                page.screenshot(path=str(evidence/'zoom-before-form.png'),full_page=True)
                                fill(page,'V11 Zoom','26.11.2026 09:00','26.11.2026 16:00','25.11.2026 12:00',keyboard=True)
                                check('Native Firefox200 percent zoom',page.evaluate('devicePixelRatio')==2)
                                layout(page,'200 percent form layout')
                                page.keyboard.press('Tab');expect(page.locator('#save-calendar-offer')).to_be_focused()
                                page.screenshot(path=str(evidence/'zoom-form.png'))
                                page.keyboard.press('Enter');expect(page.locator('#calendar-offer-dialog')).to_be_hidden(timeout=15000)
                                check('Native200 draft saved by keyboard')
                            finally:zoom.close()
                        # The copied zoom session legitimately rotated CSRF on resume.
                        coach.reload();expect(coach.locator('#portal-view')).to_be_visible()
                        with coach.expect_response(lambda r:r.request.method=='DELETE' and r.url.endswith('/access/session')) as logged_out:
                            coach.locator('#logout-button').click()
                        check('Native logout response204',logged_out.value.status==204)
                        expect(coach.locator('#login-view')).to_be_visible();login(coach,'coach');check('Logout and renewed native recovery login')
                        held=[]
                        def late_capabilities(route):held.append((route,route.fetch()))
                        coach.route('**/api/v1/portal/calendar/capabilities',late_capabilities)
                        with coach.expect_request(lambda request:request.url.endswith('/calendar/capabilities')):
                            coach.reload(wait_until='domcontentloaded')
                        expect(coach.locator('#portal-view')).to_be_visible()
                        with coach.expect_response(lambda response:response.request.method=='DELETE' and response.url.endswith('/access/session')):
                            coach.locator('#logout-button').click()
                        expect(coach.locator('#login-view')).to_be_visible()
                        check('Delayed native capability response captured',len(held)==1 and held[0][1].status==200)
                        with coach.expect_response(lambda response:response.url.endswith('/calendar/capabilities')):
                            held[0][0].fulfill(response=held[0][1])
                        coach.evaluate('async()=>{await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);}')
                        expect(coach.locator('#login-view')).to_be_visible()
                        check('Late startup after logout cannot restore private Calendar DOM',coach.locator('#coach-calendar-workspace').count()==0 and coach.locator('#review-calendar-workspace').count()==0)
                        coach.unroute('**/api/v1/portal/calendar/capabilities',late_capabilities)
                        report['javascript_errors']=errors
                        check('Browser JavaScript healthy',not errors)
                        report['cases_15']='PASS';report['tls_scope']='EPHEMERAL_LOCAL_FIXTURE_ONLY_NOT_REMOTE_TLS_ACCEPTANCE'
                    finally:
                        for context in contexts:context.close()
                        browser.close()
            finally:
                fixture.cleanup();report['zero_residue']=fixture.cleanup_pass
        report.update(status='PASS',container_removed=db.removed,volume_removed=db.volume_removed)
    except BaseException as error:
        report.update(status='FAIL',failure_type=type(error).__name__)
        raise
    finally:
        report['container_removed']=bool(db and db.removed);report['volume_removed']=bool(db and db.volume_removed)
        (evidence/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
        print('V11_UX='+report['status']+' REPORT='+str(evidence/'report.json'),flush=True)


if __name__=='__main__':main()
