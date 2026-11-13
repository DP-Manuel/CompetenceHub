"""V1.1 UX against the staged package and its owned synthetic cohort only.

Uses the existing strict browser CA policy; no original login copy, TLS bypass,
invitation capture or real identity. The enclosing update removes this cohort.
"""
from datetime import datetime,timedelta
import json
from pathlib import Path
import re
import tempfile
from zoneinfo import ZoneInfo

from icalendar import Calendar
from playwright.sync_api import expect,sync_playwright


def show_month(page,target):
    # Initial fetch may auto-select the first populated month. Finish it before
    # navigating, and navigate by the month identity, never a transient row count.
    expect(page.locator('#loading')).to_be_hidden(timeout=30000)
    expected=page.evaluate('([y,m])=>new Intl.DateTimeFormat("de-DE",{month:"long",year:"numeric"}).format(new Date(y,m-1,1))',
                           [target.year,target.month])
    for _ in range(3):
        if page.locator('#previous').is_disabled():break
        page.locator('#previous').click()
    for _ in range(3):
        if page.locator('#month-label').inner_text()==expected:break
        page.locator('#next').click()
    expect(page.locator('#month-label')).to_have_text(expected)


def run(root,fixture,ca,directory,report,private,qa):
    checks=[];errors=[];report['v11_checks']=checks
    def check(label,value=True):
        report['last_check']=label
        if not value:raise AssertionError(label)
        checks.append(label);print('PASS | '+label,flush=True)
    now=datetime.fromtimestamp(root.request('clock')['server_time'],ZoneInfo('Europe/Berlin'))
    start=(now+timedelta(days=7)).replace(hour=9,minute=0,second=0,microsecond=0)
    def date(value):return value.strftime('%d.%m.%Y %H:%M')
    def card(page,title,review=False):
        return page.locator('#review-calendar-list .calendar-card' if review else '#coach-calendar-list .calendar-card').filter(has=page.get_by_role('heading',name=title,exact=True))
    def fill(page,title,begins,ends,keyboard=False):
        page.locator('#open-calendar-offer-dialog').focus()
        if keyboard:page.keyboard.press('Enter')
        else:page.locator('#open-calendar-offer-dialog').click()
        for name,value in {'title':title,'starts-at':date(begins),'ends-at':date(ends),
                           'decision-deadline':date(begins-timedelta(days=2)),
                           'capacity':'10','review-threshold':'5','price':'DEMO Preis nach Abstimmung'}.items():
            page.locator('#calendar-'+name).fill(value)
        page.locator('#calendar-topic').select_option(fixture['topic'])
    def save(page):
        page.locator('#save-calendar-offer').click()
        expect(page.locator('#calendar-offer-dialog')).to_be_hidden(timeout=15000)
        expect(page.locator('#coach-calendar-loading')).to_be_hidden()
    def submit(page,title):
        with page.expect_response(lambda response:response.request.method=='POST' and response.url.endswith('/submit')) as sent:
            card(page,title).get_by_role('button',name='Zur Prüfung einreichen',exact=True).click()
        check('V11 native submit200',sent.value.status==200)
        expect(card(page,title)).to_contain_text('Zur Prüfung eingereicht')
    def review(page,title):
        page.reload()
        card(page,title,True).get_by_role('button',name='Angebot prüfen',exact=True).click()
        expect(page.locator('#calendar-review-dialog')).to_be_visible()
        expect(page.locator('#calendar-review-summary')).to_contain_text(title)
        page.get_by_label('Veröffentlichen',exact=True).check()
        with page.expect_response(lambda response:response.request.method=='POST' and response.url.endswith('/review-decisions')) as sent:
            page.get_by_role('button',name='Entscheidung speichern',exact=True).click()
        check('V11 native publication200',sent.value.status==200)
        expect(page.locator('#calendar-review-dialog')).to_be_hidden()
    def geometry(page):
        return page.evaluate('''()=>document.documentElement.scrollWidth<=innerWidth+1 &&
          [...document.querySelectorAll('dialog[open] input,dialog[open] select')].filter(e=>e.getClientRects().length)
            .every(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.left>=0&&r.right<=innerWidth+1;})''')
    with sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            pages={}
            for role in ('coach','reviewer'):
                context=browser.new_context(locale='en-US',viewport={'width':1440,'height':1000},reduced_motion='reduce')
                page=context.new_page();page.on('pageerror',lambda error:errors.append(error.name))
                with page.expect_response(lambda response:response.url==qa.ORIGIN+qa.ACCESS+'/session'):
                    page.goto(qa.ORIGIN+'/portal/')
                expect(page.locator('#login-email')).to_be_focused()
                page.locator('#login-email').fill(fixture['accounts'][role]['email'])
                page.locator('#login-password').fill(fixture['accounts'][role]['password'])
                page.get_by_role('button',name='Anmelden',exact=True).click()
                page.get_by_text('Recovery-Code',exact=True).click()
                page.locator('#mfa-code').fill(private[role]['recovery'].pop())
                page.get_by_role('button',name='Bestätigen',exact=True).click()
                expect(page.locator('#portal-view')).to_be_visible();pages[role]=page
            coach,reviewer=pages['coach'],pages['reviewer']
            title='DEMO V11 Eintageskurs'
            fill(coach,title,start,start.replace(hour=16))
            check('V11 German input and 24h quarter-hour controls',coach.locator('#calendar-starts-at').get_attribute('type')=='text'
                  and coach.locator('#calendar-starts-at-hour option').count()==25 and coach.locator('#calendar-starts-at-minute option').count()==5)
            coach.locator('#calendar-review-threshold').fill('11');coach.locator('#save-calendar-offer').click()
            expect(coach.locator('#calendar-review-threshold')).to_be_focused()
            expect(coach.locator('#calendar-review-threshold')).to_have_attribute('aria-invalid','true')
            expect(coach.locator('#calendar-review-threshold-error')).to_contain_text('10')
            expect(coach.locator('#calendar-title')).to_have_value(title)
            check('V11 specific threshold error preserves title and focus')
            coach.locator('#calendar-review-threshold').fill('5')
            coach.locator('#calendar-ends-at').fill(date(start.replace(hour=8)));coach.locator('#save-calendar-offer').click()
            expect(coach.locator('#calendar-ends-at')).to_be_focused()
            expect(coach.locator('#calendar-ends-at-error')).to_contain_text(date(start.replace(hour=10)))
            check('V11 end-before-start example and field focus')
            coach.locator('#calendar-ends-at').fill(date(start.replace(hour=16)))
            coach.screenshot(path=str(directory/'v11-form-desktop.png'),full_page=True);save(coach)
            api=qa.HTTPS(ca,coach.context);public_api=qa.HTTPS(ca)
            row=next(row for row in json.loads(api.call(qa.OFFERS)[2])['items'] if row['title']==title)
            offer=row['id'];detail=json.loads(api.call(qa.OFFERS+'/'+offer)[2])['current_revision']
            check('V11 one-day09-16 draft with optional summary',detail['summary'] is None
                  and datetime.fromisoformat(detail['starts_at'])==start and datetime.fromisoformat(detail['ends_at'])==start.replace(hour=16))
            check('V11 draft not public or ICS',public_api.call('/api/v1/calendar/offers/'+offer)[0]==404
                  and public_api.call('/api/v1/calendar/offers/'+offer+'/calendar.ics')[0]==404)
            card(coach,title).get_by_role('button',name='Entwurf bearbeiten',exact=True).click()
            coach.locator('#calendar-starts-at').fill(date(start.replace(minute=18)));save(coach)
            card(coach,title).get_by_role('button',name='Entwurf bearbeiten',exact=True).click()
            expect(coach.locator('#calendar-starts-at-minute')).to_have_value('18')
            check('V11 typed minute18 survives roundtrip')
            coach.locator('#calendar-starts-at').fill(date(start));save(coach)
            submit(coach,title);review(reviewer,title)
            ics=public_api.call('/api/v1/calendar/offers/'+offer+'/calendar.ics')
            event=Calendar.from_ical(ics[2]).walk('VEVENT')[0]
            check('V11 published exact one-day interval',ics[0]==200 and event.decoded('dtstart')==start and event.decoded('dtend')==start.replace(hour=16))
            public=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
            public.goto(qa.ORIGIN+'/portal/calendar-public.html')
            show_month(public,start)
            segment=public.locator('[data-offer="'+offer+'"]');expect(segment).to_have_count(1)
            segment.focus();public.keyboard.press('Enter');expect(public.locator('#detail')).to_be_focused()
            expect(public.locator('#ics')).to_have_text('Zum Kalender hinzufügen (.ics)')
            with public.expect_download() as download:public.locator('#ics').click()
            check('V11 actual labelled ICS download',Path(download.value.path()).read_bytes()==ics[2])
            public.get_by_role('button',name='Anfrageentwurf vorbereiten',exact=True).click()
            expect(public.locator('#request-draft')).to_have_value(re.compile('.*'+title+'.*',re.S))
            check('V11 request draft and390 public keyboard layout',geometry(public))
            public.locator('#calendar-help').click()
            for _ in range(3):expect(public.locator('#tour-title')).to_be_focused();public.locator('#tour-next').click()
            expect(public.locator('#calendar-help')).to_be_focused()
            public.locator('#calendar-help').click();public.locator('#tour-skip').click()
            check('V11 Calendar tour complete restart skip focus Reduced Motion',public.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'))
            fill(coach,'DEMO V11 Mobil',start+timedelta(days=2),start+timedelta(days=2,hours=2))
            coach.set_viewport_size({'width':390,'height':844})
            coach.locator('#calendar-review-threshold').fill('11');coach.locator('#save-calendar-offer').click()
            expect(coach.locator('#calendar-review-threshold')).to_be_focused()
            check('V11 mobile390 error and controls readable',geometry(coach)
                  and coach.locator('#calendar-review-threshold-error').evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight;}'))
            coach.screenshot(path=str(directory/'v11-form-mobile.png'))
            coach.locator('#calendar-review-threshold').fill('5');save(coach)
            with tempfile.TemporaryDirectory(dir=directory) as profile:
                qa.zoom_profile(pw,Path(profile));zoom=pw.firefox.launch_persistent_context(profile,headless=True,no_viewport=True)
                try:
                    zoom.add_cookies(coach.context.cookies());page=zoom.pages[0];page.goto(qa.ORIGIN+'/portal/')
                    expect(page.locator('#portal-view')).to_be_visible()
                    fill(page,'DEMO V11 Zoom',start+timedelta(days=3),start+timedelta(days=3,hours=2),keyboard=True)
                    check('V11 native200 form layout',page.evaluate('devicePixelRatio')==2 and geometry(page))
                    page.screenshot(path=str(directory/'v11-form-200.png'))
                    page.keyboard.press('Tab');expect(page.locator('#save-calendar-offer')).to_be_focused()
                    page.keyboard.press('Enter');expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
                    check('V11 native200 keyboard draft saved')
                finally:zoom.close()
            check('V11 browser JavaScript healthy',not errors)
            report['v11_ux']='PASS';report['invitation_delivery']='CLOSED_THROUGHOUT'
            return private
        finally:browser.close()
