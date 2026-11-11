"""Actual remote Portal/Calendar acceptance with isolated Firefox certificate trust.

No global trust-store change, certificate bypass, mail, real identities or traces.
"""
from contextlib import closing
from datetime import datetime, timedelta, timezone
from http.cookiejar import CookieJar
import json
from pathlib import Path
import sqlite3
import ssl
import time
from urllib.error import HTTPError
from urllib.request import build_opener, HTTPCookieProcessor, HTTPSHandler, Request
from zoneinfo import ZoneInfo

from icalendar import Calendar
from playwright.sync_api import expect, sync_playwright
import pyotp

ORIGIN = 'https://localhost:8447'
ACCESS = '/api/v1/portal/access'
OFFERS = '/api/v1/portal/calendar/offers'


class HTTPS:
    def __init__(self, ca, context=None, timeout=30):
        self.context = context
        self.timeout = timeout
        self.opener = build_opener(HTTPSHandler(context=ssl.create_default_context(cafile=str(ca))), HTTPCookieProcessor(CookieJar()))

    def call(self, path, method='GET', data=None, headers=None):
        values = {'Accept': 'application/json', **(headers or {})}
        if self.context:
            values['Cookie'] = '; '.join(row['name'] + '=' + row['value'] for row in self.context.cookies())
        if method not in ('GET', 'HEAD'):
            values.setdefault('Origin', ORIGIN)
        payload = None if data is None else json.dumps(data).encode()
        if payload is not None:
            values['Content-Type'] = 'application/json'
        try:
            response = self.opener.open(Request(ORIGIN + path, data=payload, method=method, headers=values), timeout=self.timeout)
        except HTTPError as error:
            response = error
        return response.status, response.headers, response.read()


def zoom_profile(pw, directory):
    # Firefox's own global full-zoom content preference, not CSS or viewport scaling.
    context = pw.firefox.launch_persistent_context(str(directory), headless=True, no_viewport=True)
    context.close()
    with closing(sqlite3.connect(directory / 'content-prefs.sqlite')) as database:
        database.execute('INSERT INTO settings(name) VALUES(?)', ('browser.content.full-zoom',))
        setting = database.execute('SELECT id FROM settings WHERE name=?', ('browser.content.full-zoom',)).fetchone()[0]
        database.execute('INSERT INTO prefs(groupID,settingID,value,timestamp) VALUES(NULL,?,?,?)', (setting, 2.0, int(time.time())))
        database.commit()


def run(root, fixture, ca, directory, report):
    checks, private, contexts, errors = [], {}, {}, []
    report['checks'] = checks
    def check(name, value):
        report['last_check'] = name
        if not value:
            raise AssertionError(name)
        checks.append(name)
        print('PASS | ' + name, flush=True)
    def now():
        return root.request('clock')['server_time']
    def card(page, title):
        return page.locator('#coach-calendar-list .calendar-card').filter(has=page.get_by_role('heading', name=title, exact=True))
    def wait_list(page):
        expect(page.locator('#coach-calendar-loading')).to_be_hidden()
    def geometry(page, name):
        check(name, page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'))
    def month(page, target, keyboard=False):
        label=page.evaluate('([year,month]) => new Intl.DateTimeFormat("de-DE",{month:"long",year:"numeric"}).format(new Date(year,month-1,1))',[target.year,target.month])
        for _ in range(3):
            expect(page.locator('#loading')).to_be_hidden()
            if page.locator('#month-label').inner_text()==label:break
            previous=page.locator('#month-label').inner_text()
            if keyboard:
                page.locator('#next').focus();page.keyboard.press('Enter')
            else:page.locator('#next').click()
            expect(page.locator('#month-label')).not_to_have_text(previous)
        expect(page.locator('#month-label')).to_have_text(label)
        expect(page.locator('#loading')).to_be_hidden()
    def login(page, key):
        account = fixture['accounts'][key]
        page.goto(ORIGIN + '/portal/')
        page.locator('#login-email').fill(account['email'])
        page.locator('#login-password').fill(account['password'])
        page.get_by_role('button', name='Anmelden', exact=True).click()
        if key not in private:
            expect(page.locator('#enrollment-code')).to_be_visible()
            secret = page.locator('#provisioning-secret').inner_text()
            page.locator('#enrollment-code').fill(pyotp.TOTP(secret).at(now()))
            page.get_by_role('button', name='Einrichtung abschließen').click()
            expect(page.locator('#recovery-view')).to_be_visible()
            codes = page.locator('#recovery-codes li').all_text_contents()
            check(key + ' native MFA and ten recovery codes', len(codes) == 10)
            private[key] = {'totp': secret, 'recovery': codes}
            page.locator('#recovery-confirmed').check()
            page.get_by_role('button', name='Portal öffnen').click()
            if fixture.get('automatic_onboarding'):
                expect(page.locator('#product-tour')).to_be_visible()
                page.locator('#tour-skip').click()
        else:
            page.get_by_text('Recovery-Code', exact=True).click()
            page.locator('#mfa-code').fill(private[key]['recovery'].pop())
            page.get_by_role('button', name='Bestätigen', exact=True).click()
        expect(page.locator('#portal-view')).to_be_visible()
    def tour(page, role, count):
        page.locator('#pilot-help summary').click()
        page.locator('#tour-options button').filter(has_text=role).click()
        for index in range(count):
            expect(page.locator('#tour-progress')).to_have_text(f'Schritt {index+1} von {count}')
            expect(page.locator('#tour-title')).to_be_focused()
            page.locator('#tour-next').click()
        expect(page.locator('#product-tour')).to_be_hidden()
        check(role + ' complete optional onboarding tour and focus', True)
    def create(page, title, start, end):
        page.locator('#open-calendar-offer-dialog').click()
        for name, value in {'title': title, 'summary': 'DEMO: Nur synthetische Testdaten',
                            'starts-at': start.strftime('%Y-%m-%dT%H:%M'), 'ends-at': end.strftime('%Y-%m-%dT%H:%M'),
                            'decision-deadline': (start-timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
                            'location': 'DEMO Raum', 'price': 'DEMO Keine Buchung'}.items():
            page.locator('#calendar-' + name).fill(value)
        page.locator('#calendar-topic').select_option(fixture['topic'])
        page.locator('#save-calendar-offer').click()
        expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
        expect(card(page, title)).to_be_visible()
        api = HTTPS(ca, page.context)
        return next(row['id'] for row in json.loads(api.call(OFFERS)[2])['items'] if row['title'] == title)
    def submit(page, title):
        card(page, title).get_by_role('button', name='Zur Prüfung einreichen').click()
        expect(card(page, title)).to_contain_text('Zur Prüfung eingereicht')
    def review(page, title, outcome):
        page.reload()
        row = page.locator('#review-calendar-list .calendar-card').filter(has=page.get_by_role('heading', name=title, exact=True))
        expect(row).to_be_visible()
        row.get_by_role('button', name='Angebot prüfen').click()
        page.get_by_label('Änderungen anfordern' if outcome == 'changes_requested' else 'Veröffentlichen', exact=True).check()
        if outcome == 'changes_requested':
            page.locator('#calendar-review-note').fill('PRIVATE REVIEW: Demo-Ort genauer')
        page.get_by_role('button', name='Entscheidung speichern', exact=True).click()
        expect(page.locator('#calendar-review-dialog')).to_be_hidden()
    api = HTTPS(ca)
    check('Strict TLS native readiness', api.call('/health/ready')[0] == 200)
    check('Unauthenticated portal API denied', api.call(OFFERS)[0] == 401)
    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=True)
        report['browser'] = browser.version
        try:
            for key in ('coach', 'reviewer', 'admin', 'coach_two'):
                context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
                context.on('page', lambda page: page.on('pageerror', lambda error: errors.append(error.name)))
                contexts[key] = context
                page = context.new_page()
                login(page, key)
                actor = HTTPS(ca, context)
                status, headers, raw = actor.call(ACCESS + '/session')
                check(key + ' exact role after native login', status == 200 and json.loads(raw)['user']['roles'] == [fixture['accounts'][key]['role']])
                host_cookies = [row for row in context.cookies() if row['name'].startswith('__Host-')]
                check(key + ' secure host-only cookie', bool(host_cookies) and all(row['secure'] and row['httpOnly'] and row['sameSite'] == 'Lax' and row['domain'] == 'localhost' for row in host_cookies))
                check(key + ' no Web Storage tokens', page.evaluate('localStorage.length===0 && sessionStorage.length===0'))
                check(key + ' protected response no-store', headers.get('Cache-Control') == 'no-store')
                if key != 'admin':
                    check(key + ' Admin inventory denied', actor.call('/api/v1/admin/users')[0] in (401,403))
                    check(key + ' company API denied', actor.call('/api/v1/portal/companies')[0] in (401,403))
                else:
                    check('Admin inventory available', actor.call('/api/v1/admin/users')[0] == 200)
                check(key + ' wrong Origin rejected', actor.call(ACCESS + '/session/csrf', 'POST', headers={'Origin':'https://wrong.invalid'})[0] == 403)
                check(key + ' wrong CSRF rejected', actor.call(ACCESS + '/session', 'DELETE', headers={'X-CSRF-Token':'wrong'})[0] == 403)
                if key in ('admin', 'coach', 'reviewer'):
                    tour(page, {'admin':'Admin','coach':'Coach','reviewer':'Prüfer'}[key], 6 if key == 'admin' else 7)
            coach, reviewer = contexts['coach'].pages[0], contexts['reviewer'].pages[0]
            if fixture.get('reference_seed_only'):
                start=datetime.fromtimestamp(now(),ZoneInfo('Europe/Berlin'))+timedelta(days=10)
                start=start.replace(second=0,microsecond=0)
                reference=create(coach,'DEMO preserved reference',start,start+timedelta(hours=2))
                submit(coach,'DEMO preserved reference');review(reviewer,'DEMO preserved reference','published')
                check('Existing reference has native MFA sessions and published event',api.call('/api/v1/calendar/offers/'+reference)[0]==200)
                return private
            start = datetime.fromtimestamp(now(), ZoneInfo('Europe/Berlin')).replace(day=1, hour=17, minute=18, second=0, microsecond=0)
            first = (start+timedelta(days=40)).replace(day=1)
            start, end = first-timedelta(days=1), first+timedelta(days=1)
            if start <= datetime.fromtimestamp(now(), ZoneInfo('Europe/Berlin'))+timedelta(days=5):
                first=(first+timedelta(days=40)).replace(day=1)
                start,end=first-timedelta(days=1),first+timedelta(days=1)
            title = 'DEMO VPS Mehrtagesworkshop'
            offer = create(coach, title, start, end)
            check('Draft has no public projection or ICS', api.call('/api/v1/calendar/offers/'+offer)[0] == 404 and api.call('/api/v1/calendar/offers/'+offer+'/calendar.ics')[0] == 404)
            other_api = HTTPS(ca, contexts['coach_two'])
            check('Native PostgreSQL Coach isolation', other_api.call(OFFERS+'/'+offer)[0] == 404)
            submit(coach,title); review(reviewer,title,'changes_requested')
            coach.reload(); card(coach,title).get_by_role('button', name='Neue Revision bearbeiten').click()
            expect(coach.locator('#calendar-review-feedback')).to_contain_text('Demo-Ort genauer')
            coach.locator('#calendar-location').fill('DEMO Geprüfter Raum')
            coach.locator('#save-calendar-offer').click(); expect(coach.locator('#calendar-offer-dialog')).to_be_hidden()
            submit(coach,title); review(reviewer,title,'published')
            status, _, raw = api.call('/api/v1/calendar/months/'+first.strftime('%Y-%m')+'/offers')
            check('Native PostgreSQL month overlap and public-only fields', status == 200 and any(row['id'] == offer for row in json.loads(raw)['items']) and b'PRIVATE REVIEW' not in raw and b'review_threshold' not in raw)
            ics_path = '/api/v1/calendar/offers/'+offer+'/calendar.ics'
            status, headers, ics = api.call(ics_path)
            event = Calendar.from_ical(ics).walk('VEVENT')[0]
            check('Published ICS interval and sequence', status == 200 and 'attachment' in headers['Content-Disposition'] and event.decoded('dtstart') == start and event.decoded('dtend') == end and int(event['SEQUENCE']) == 2)
            public = browser.new_page(viewport={'width':390,'height':844})
            public.goto(ORIGIN+'/portal/calendar-public.html')
            month(public,first)
            expect(public.locator(f'[data-offer="{offer}"]')).to_have_count(2, timeout=15000)
            public.locator(f'[data-offer="{offer}"]').last.focus(); public.keyboard.press('Enter')
            expect(public.locator('#detail')).to_be_focused()
            with public.expect_download() as download:
                public.locator('#ics').click()
            check('Actual browser ICS download', download.value.failure() is None and Path(download.value.path()).read_bytes() == ics)
            public.get_by_role('button',name='Anfrageentwurf vorbereiten',exact=True).click()
            check('Request draft only approved public data', title in public.locator('#request-draft').input_value() and 'PRIVATE REVIEW' not in public.locator('#request-draft').input_value())
            geometry(public,'Mobile 390 keyboard/detail layout'); public.screenshot(path=str(directory/'mobile390.png'),full_page=True)
            original_uid = str(event['UID'])
            coach.reload();wait_list(coach)
            card(coach,title).get_by_role('button',name='Neue Revision bearbeiten').click()
            revised='DEMO VPS Revision 3'
            coach.locator('#calendar-title').fill(revised)
            coach.locator('#save-calendar-offer').click();expect(coach.locator('#calendar-offer-dialog')).to_be_hidden()
            check('Unpublished revision preserves approved ICS',api.call(ics_path)[2]==ics)
            submit(coach,revised);review(reviewer,revised,'published')
            ics=api.call(ics_path)[2]; event=Calendar.from_ical(ics).walk('VEVENT')[0]
            check('Published revision preserves UID and increases sequence',str(event['UID'])==original_uid and int(event['SEQUENCE'])==3)
            title=revised
            other=contexts['coach_two'].pages[0]
            parallel=create(other,'DEMO VPS Paralleltermin',start,end)
            submit(other,'DEMO VPS Paralleltermin');review(reviewer,'DEMO VPS Paralleltermin','published')
            parallel_rows=json.loads(api.call('/api/v1/calendar/months/'+first.strftime('%Y-%m')+'/offers')[2])['items']
            check('Parallel Coaches remain distinct native rows', {offer,parallel}<={row['id'] for row in parallel_rows}
                  and (fixture.get('preserve_reference') or len(parallel_rows)==2))
            stale_title='DEMO VPS Versionsstand'
            create(coach,stale_title,end+timedelta(days=1),end+timedelta(days=1,hours=2))
            stale_context=browser.new_context(viewport={'width':1440,'height':1000})
            stale=stale_context.new_page();login(stale,'coach')
            expect(card(stale,stale_title)).to_be_visible()
            card(stale,stale_title).get_by_role('button',name='Entwurf bearbeiten').click()
            card(coach,stale_title).get_by_role('button',name='Entwurf bearbeiten').click()
            coach.locator('#calendar-summary').fill('DEMO aktuelle gespeicherte Version')
            coach.locator('#save-calendar-offer').click();expect(coach.locator('#calendar-offer-dialog')).to_be_hidden()
            stale.locator('#calendar-summary').fill('DEMO veralteter Stand darf nicht ueberschreiben')
            stale.locator('#save-calendar-offer').click()
            expect(stale.locator('#reload-calendar-offer')).to_be_visible()
            check('Native stale edit rejected; explicit reload available',stale.locator('#calendar-offer-dialog').is_visible())
            stale_context.close()
            collision='DEMO VPS Konflikt'
            create(coach,collision,start,end)
            card(coach,collision).get_by_role('button',name='Zur Prüfung einreichen').click()
            expect(coach.locator('#coach-calendar-error')).to_contain_text('überschneidet')
            check('Same-Coach overlap is rejected without publishing',True)
            root.request('restart')
            for _ in range(60):
                try:
                    if api.call('/health/ready')[0] == 200: break
                except OSError: pass
                time.sleep(.2)
            coach.reload(); expect(coach.locator('#portal-view')).to_be_visible()
            check('PostgreSQL publication and session survive own backend restart', api.call(ics_path)[2] == ics and HTTPS(ca,contexts['coach']).call(ACCESS+'/session')[0] == 200)
            report['postgres_persistence'] = report['restart'] = 'PASS'
            public.locator('#format').select_option('praesenz')
            expect(public.locator(f'[data-offer="{offer}"]')).to_have_count(0)
            public.locator('#format').select_option('')
            expect(public.locator(f'[data-offer="{offer}"]')).to_have_count(2,timeout=15000)
            public.locator('#topic').select_option(fixture['topic'])
            check('Public format/topic filtering',public.locator(f'[data-offer="{offer}"]').count()==2)
            zoom_dir = directory/'zoom-profile'
            zoom_profile(pw,zoom_dir)
            zoom = pw.firefox.launch_persistent_context(str(zoom_dir),headless=True,no_viewport=True)
            try:
                z=zoom.new_page();z.goto(ORIGIN+'/portal/calendar-public.html')
                check('Native full-page 200 percent zoom', z.evaluate('devicePixelRatio===2 && innerWidth>600 && innerWidth<800 && getComputedStyle(document.documentElement).zoom==="1"'))
                month(z,first,keyboard=True)
                expect(z.locator(f'[data-offer="{offer}"]')).to_have_count(2)
                z.locator(f'[data-offer="{offer}"]').first.focus();z.keyboard.press('Enter')
                expect(z.locator('#detail')).to_be_focused()
                geometry(z,'Native 200 layout');z.screenshot(path=str(directory/'native200.png'),full_page=True)
            finally:zoom.close()
            card(coach,title).get_by_role('button',name='Angebot zurückziehen').click()
            expect(public.locator(f'[data-offer="{offer}"]')).to_have_count(0,timeout=15000)
            check('Withdrawal removes public API and ICS', api.call(ics_path)[0] == 404)
            root.request('expire', actor='coach_two')
            check('Native session expiry denied', other_api.call(ACCESS+'/session')[0] == 401)
            admin_api = HTTPS(ca,contexts['admin'])
            csrf = admin_api.call(ACCESS+'/session/csrf','POST')[1]['X-CSRF-Token']
            check('Native logout revokes session', admin_api.call(ACCESS+'/session','DELETE',headers={'X-CSRF-Token':csrf})[0] == 204 and admin_api.call(ACCESS+'/session')[0] == 401)
            login(contexts['admin'].pages[0],'admin')
            check('Native one-time recovery login', HTTPS(ca,contexts['admin']).call(ACCESS+'/session')[0] == 200)
            check('Browser JavaScript healthy', not errors)
            report['cal1'] = report['mfa_rbac'] = report['onboarding'] = 'PASS'
            return private
        finally:
            browser.close()
