"""Fourteen V1.2 user cases shared by isolated memory and native-PG proofs."""
from datetime import timedelta
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
from uuid import uuid4

from icalendar import Calendar
from playwright.sync_api import expect


def disclose(page, section):
    details = page.locator("#calendar-" + section)
    if details.count() and details.get_attribute("open") is None:
        details.locator(":scope > summary").click()


def fill_datetime(page,name,value):
    """Date-only German control plus exactly one24h clock."""
    disclose(page, "scheduling")
    page.locator('#calendar-'+name).fill(value.strftime('%d.%m.%Y'))
    page.locator('#calendar-'+name+'-hour').select_option(value.strftime('%H'))
    page.locator('#calendar-'+name+'-minute').select_option(value.strftime('%M'))


def select_date(page,field,value):
    page.locator('[data-pick-date="'+field+'"]').click()
    panel=page.locator('#calendar-date-panel');expect(panel).to_be_visible()
    target=value.year*12+value.month-1
    for _ in range(25):
        current=panel.locator('.datepicker-cell.day:not(.prev):not(.next)').first.evaluate('e=>{const d=new Date(Number(e.dataset.date));return d.getFullYear()*12+d.getMonth();}')
        if current==target:break
        panel.get_by_role('button',name='Nächster Monat' if current<target else 'Vorheriger Monat',exact=True).click()
    stamp=page.evaluate('([y,m,d])=>new Date(y,m-1,d).getTime()',[value.year,value.month,value.day])
    panel.locator(f'.datepicker-cell.day[data-date="{stamp}"]').click()
    expect(page.locator('#calendar-'+{'starts_at':'starts-at','ends_at':'ends-at','decision_deadline':'decision-deadline'}[field])).to_have_value(value.strftime('%d.%m.%Y'))


def exercise(page,base,pw,login,now,report,evidence,zoom_profile,*,strict_tls=False):
    evidence.mkdir(parents=True,exist_ok=True);cases={};report['cases_14']=cases;errors=[]
    page.on('pageerror',lambda error:errors.append(error.name))
    start=(now+timedelta(days=7)).replace(hour=9,minute=0,second=0,microsecond=0)
    title='DEMO V12 '+uuid4().hex[:8]
    tls_options={} if strict_tls else {'ignore_https_errors':True}
    def get(actor,path):
        if not strict_tls:return actor.request.get(base+path)
        # Use the browser's explicitly installed CA, never a Node TLS bypass.
        response=actor.evaluate('''async path=>{const r=await fetch(path,{cache:'no-store'});
          return {status:r.status,body:await r.json()};}''',path)
        return SimpleNamespace(status=response['status'],json=lambda:response['body'])
    def case(number,label,condition=True,result='PASS'):
        report['last_case']=number
        if not condition:raise AssertionError(label)
        cases[str(number)]={'result':result,'label':label};print(result+' | V12-'+str(number)+' '+label,flush=True)
    def card(title,actor=page,review=False):
        return actor.locator('#review-calendar-list .calendar-card' if review else '#coach-calendar-list .calendar-card').filter(has=actor.get_by_role('heading',name=title,exact=True))
    def open_form(text,begins=start,ends=None):
        page.locator('#open-calendar-offer-dialog').click();expect(page.locator('#calendar-title')).to_be_focused()
        page.locator('#calendar-title').fill(text);page.locator('#calendar-topic').select_option(index=1)
        fill_datetime(page,'starts-at',begins);fill_datetime(page,'ends-at',ends or begins.replace(hour=16))
        fill_datetime(page,'decision-deadline',begins-timedelta(days=2))
        page.locator('#calendar-price').fill('DEMO Preis nach Abstimmung')
    def save():
        page.locator('#save-calendar-offer').click();expect(page.locator('#calendar-offer-dialog')).to_be_hidden(timeout=15000)
        expect(page.locator('#coach-calendar-loading')).to_be_hidden()
    def discard():
        page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
        expect(page.locator('#calendar-discard-dialog')).to_be_visible()
        page.get_by_role('button',name='Änderungen verwerfen',exact=True).click();expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
    def layout(actor):
        return actor.evaluate('''()=>document.documentElement.scrollWidth<=innerWidth+1 &&
        [...document.querySelectorAll('dialog[open] input,dialog[open] select,dialog[open] button')].filter(e=>e.getClientRects().length)
        .every(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.left>=-1&&r.right<=innerWidth+1;})''')
    # Clean and dirty cancellation, including one choice rather than native confirm.
    page.locator('#open-calendar-offer-dialog').click()
    compact = bool(page.locator('#calendar-scheduling').count())
    if compact:
        expect(page.locator('#calendar-starts-at')).to_be_visible()
        expect(page.locator('#calendar-starts-at-hour')).to_be_hidden()
        expect(page.locator('#calendar-summary')).to_be_hidden()
        expect(page.locator('#calendar-clock-preview')).to_contain_text('09:00 Uhr')
        page.screenshot(path=str(evidence/'compact-editor-desktop.png'))
    page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
    expect(page.locator('#calendar-offer-dialog')).to_be_hidden();expect(page.locator('#calendar-discard-dialog')).to_be_hidden()
    open_form(title)
    page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
    expect(page.locator('#calendar-discard-dialog')).to_be_visible()
    page.get_by_role('button',name='Weiter bearbeiten',exact=True).click()
    expect(page.locator('#calendar-title')).to_have_value(title)
    case(8,'Clean cancel direct; dirty cancel has one explicit choice and preserves input')
    # Actual pointer date selection; same date is a valid one-day interval.
    select_date(page,'starts_at',start);select_date(page,'ends_at',start)
    page.locator('[data-close-picker]').click()
    expect(page.locator('#calendar-starts-at')).to_have_value(start.strftime('%d.%m.%Y'))
    for name,hour in [('starts-at','09'),('ends-at','16')]:
        expect(page.locator('#calendar-'+name+'-hour')).to_have_value(hour)
        page.locator('#calendar-'+name+'-minute').select_option('15');page.locator('#calendar-'+name+'-minute').select_option('00')
    case(4,'Exactly one24h hour/minute pair per endpoint; quarter-hour selection')
    # Advance guidance before invalid submission, compact location and minute errors.
    page.locator('#calendar-format').select_option('praesenz')
    expect(page.locator('#calendar-location-label')).to_have_text('Veranstaltungsort *')
    expect(page.locator('#calendar-location-hint')).to_contain_text('Würzburg')
    assert page.locator('#calendar-location').get_attribute('required') is not None
    case(5,'Presence location requirement, example and200-character count before submit')
    page.locator('#save-calendar-offer').click();expect(page.locator('#calendar-location')).to_be_focused()
    expect(page.locator('#calendar-location-error')).to_have_text('Bitte Veranstaltungsort angeben.')
    assert page.locator('#calendar-location-error').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')<=14
    page.locator('#calendar-location').fill('Würzburg, Seminarraum')
    expect(page.locator('#calendar-location')).not_to_have_attribute('aria-invalid','true')
    case(6,'Short location-only error clears immediately on correction')
    page.locator('#calendar-starts-at-minute').select_option('')
    if compact:
        page.locator('#calendar-scheduling > summary').click()
        expect(page.locator('#calendar-starts-at-minute')).to_be_hidden()
    page.locator('#save-calendar-offer').click()
    expect(page.locator('#calendar-starts-at-minute')).to_be_focused()
    expect(page.locator('#calendar-starts-at-minute-error')).to_have_text('Bitte Minute wählen.')
    expect(page.locator('#calendar-starts-at')).not_to_have_attribute('aria-invalid','true')
    expect(page.locator('#calendar-starts-at-hour')).not_to_have_attribute('aria-invalid','true')
    page.screenshot(path=str(evidence/'desktop-validation.png'),full_page=True)
    case(7,'Only missing minute is marked; valid date/hour are not red')
    discard();expect(page.locator('#open-calendar-offer-dialog')).to_be_focused()
    case(9,'Cancel still works after validation failure without deleting drafts')
    open_form(title);select_date(page,'starts_at',start);select_date(page,'ends_at',start);page.locator('[data-close-picker]').click()
    save();expect(card(title)).to_be_visible()
    rows=get(page,'/api/v1/portal/calendar/offers').json()['items'];offer=next(row for row in rows if row['title']==title)
    offer_id=offer['id'];saved=get(page,'/api/v1/portal/calendar/offers/'+offer_id).json()['current_revision']
    case(1,'One-day workshop selected in Calendar and saved09-16 with optional summary',
         saved['summary'] is None and saved['starts_at']!=saved['ends_at'])
    # Multi-day range, explicit endpoints and intermediate highlight.
    multi=title+' Mehrtage';multi_start=(start+timedelta(days=2)).replace(hour=10)
    if (multi_start + timedelta(days=3)).month != multi_start.month:
        multi_start = (multi_start + timedelta(days=3)).replace(day=1)
    open_form(multi,multi_start,multi_start+timedelta(days=3,hours=2))
    select_date(page,'starts_at',multi_start);select_date(page,'ends_at',multi_start+timedelta(days=3))
    expect(page.locator('#calendar-date-panel .cal-range-middle')).to_have_count(2)
    assert page.locator('#calendar-date-panel .cal-range-start').count()==1 and page.locator('#calendar-date-panel .cal-range-end').count()==1
    page.screenshot(path=str(evidence/'desktop-range.png'),full_page=True)
    page.locator('[data-close-picker]').click();save();expect(card(multi)).to_be_visible()
    case(2,'Multi-day start/end and turquoise intermediate days saved as one offer')
    case(3,'Drag intentionally omitted; equivalent pointer/keyboard start-end selection exists',result='NOT_APPLICABLE')
    # Escape first closes the picker, then one discard modal; browser Back uses UI history.
    open_form(title+' Escape')
    page.locator('[data-pick-date="starts_at"]').click();page.keyboard.press('Escape')
    expect(page.locator('#calendar-date-panel')).to_be_hidden();expect(page.locator('#calendar-offer-dialog')).to_be_visible()
    page.keyboard.press('Escape');expect(page.locator('#calendar-discard-dialog')).to_be_visible()
    page.keyboard.press('Escape');expect(page.locator('#calendar-title')).to_have_value(title+' Escape')
    page.go_back();expect(page.locator('#calendar-discard-dialog')).to_be_visible()
    page.get_by_role('button',name='Weiter bearbeiten',exact=True).click()
    page.go_back();expect(page.locator('#calendar-discard-dialog')).to_be_visible()
    page.get_by_role('button',name='Änderungen verwerfen',exact=True).click();expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
    case(10,'Escape layers and Browser Back: keep/discard once, return to overview')
    card(title).get_by_role('button',name='Entwurf bearbeiten',exact=True).click()
    expect(page.locator('#calendar-starts-at')).to_have_value(start.strftime('%d.%m.%Y'))
    disclose(page, "description")
    description = 'Zielgruppe: Demo-Team.\n\nInhalte und Ablauf: ' + 'Beispiel und Reflexion. ' * 39
    page.locator('#calendar-summary').fill(description)
    if compact:
        expect(page.locator('#calendar-summary-count')).to_have_text(f'{len(description)} / 1200 Zeichen')
        assert page.locator('#calendar-summary').get_attribute('maxlength') == '1200'
        page.locator('#calendar-description > summary').click()
        expect(page.locator('#calendar-summary')).to_be_hidden()
    save()
    assert get(page,'/api/v1/portal/calendar/offers/'+offer_id).json()['current_revision']['summary'] == description.strip()
    case(11,'Saved draft reopens and updates without losing date/time')
    # Normal Reviewer workflow, not an approval bypass.
    with page.expect_response(lambda response:response.request.method=='POST' and response.url.endswith('/submit')) as sent:
        card(title).get_by_role('button',name='Zur Prüfung einreichen',exact=True).click()
    assert sent.value.status==200
    reviewer_context=page.context.browser.new_context(**tls_options,viewport={'width':1440,'height':1000})
    try:
        reviewer=reviewer_context.new_page();reviewer.on('pageerror',lambda error:errors.append(error.name));login(reviewer,'reviewer')
        def review(outcome):
            reviewer.reload();row=card(title,reviewer,True);row.get_by_role('button',name='Angebot prüfen',exact=True).click()
            expect(reviewer.locator('#calendar-review-dialog')).to_be_visible()
            expect(reviewer.locator('#calendar-review-summary')).to_contain_text(title)
            note = reviewer.locator('#calendar-review-note')
            if compact:
                expect(note).to_be_hidden()
                if outcome == 'changes_requested':
                    expect(reviewer.locator('#calendar-review-description-text')).to_be_hidden()
                    reviewer.locator('#calendar-review-description > summary').press('Enter')
                    expect(reviewer.locator('#calendar-review-description-text')).to_have_text(description.strip(), use_inner_text=True)
            reviewer.locator('input[name="outcome"][value="'+outcome+'"]').check()
            if outcome=='changes_requested':
                if compact:
                    expect(note).to_be_visible()
                    reviewer.get_by_role('button',name='Entscheidung speichern',exact=True).click()
                    expect(note).to_be_focused()
                    expect(reviewer.locator('#calendar-review-error')).to_contain_text('gewünschte Änderung')
                note.fill('DEMO Kurzbeschreibung präzisieren')
            elif compact:
                expect(note).to_be_hidden()
                toggle=reviewer.locator('#calendar-review-note-toggle')
                toggle.press('Enter')
                expect(toggle).to_have_attribute('aria-expanded','true')
                expect(note).to_be_visible()
                assert note.get_attribute('required') is None
                note.fill('DEMO nur lokal, nicht mitgesendet')
                toggle.press('Enter')
                expect(note).to_be_hidden()
            with reviewer.expect_response(lambda response:response.request.method=='POST' and response.url.endswith('/review-decisions')) as result:
                reviewer.get_by_role('button',name='Entscheidung speichern',exact=True).click()
            assert result.value.status==200;expect(reviewer.locator('#calendar-review-dialog')).to_be_hidden()
            if compact and outcome=='published':
                assert result.value.request.post_data_json['note'] is None
        review('changes_requested');page.reload();card(title).get_by_role('button',name='Neue Revision bearbeiten',exact=True).click()
        disclose(page, "description")
        page.locator('#calendar-summary').fill('DEMO fachlich präzisierte Kurzbeschreibung');save()
        with page.expect_response(lambda response:response.request.method=='POST' and response.url.endswith('/submit')):
            card(title).get_by_role('button',name='Zur Prüfung einreichen',exact=True).click()
        review('published')
        assert get(page,'/api/v1/calendar/offers/'+offer_id).status==200
        public=page.context.browser.new_page(**tls_options,viewport={'width':390,'height':844})
        try:
            public.goto(base+'/portal/calendar-public.html');expect(public.locator('#loading')).to_be_hidden()
            expected=public.evaluate('([y,m])=>new Intl.DateTimeFormat("de-DE",{month:"long",year:"numeric"}).format(new Date(y,m-1,1))',[start.year,start.month])
            for _ in range(3):
                if public.locator('#month-label').inner_text()==expected:break
                public.locator('#next').click()
            public.locator('[data-offer="'+offer_id+'"]').click();expect(public.locator('#detail-title')).to_have_text(title)
            with public.expect_download() as download:public.locator('#ics').click()
            event=Calendar.from_ical(Path(download.value.path()).read_bytes()).walk('VEVENT')[0]
            assert int(event['SEQUENCE'])==2
            case(12,'Native changes-requested/revision2/Reviewer publication visible in Calendar')
            report['denied_statuses']=[get(page,'/api/v1/admin/users').status,
                                       get(reviewer,'/api/v1/portal/companies').status]
            # Internal-only endpoints may reject a pure Calendar principal at
            # admission(401) or authorization(403); both are the existing contract.
            assert all(status in (401,403) for status in report['denied_statuses'])
            assert get(page,'/api/v1/portal/access/session').status==200
            case(13,'ICS actual download/sequence, native role/session checks and MFA logins preserved')
        finally:public.close()
    finally:reviewer_context.close()
    # Mobile/touch-independent keyboard path; real full-page zoom uses existing helper.
    page.set_viewport_size({'width':390,'height':844})
    if compact:
        page.locator('#open-calendar-offer-dialog').click()
        expect(page.locator('#calendar-starts-at-hour')).to_be_hidden()
        assert layout(page)
        page.screenshot(path=str(evidence/'compact-editor-390.png'))
        page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
        expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
    open_form(title+' Mobil',start+timedelta(days=4))
    page.locator('#calendar-starts-at-minute').select_option('');page.locator('#save-calendar-offer').click()
    expect(page.locator('#calendar-starts-at-minute')).to_be_focused();assert layout(page)
    assert page.locator('#calendar-starts-at-minute').get_attribute('aria-describedby')=='calendar-starts-at-minute-error'
    page.screenshot(path=str(evidence/'mobile-validation.png'))
    page.locator('#calendar-starts-at-minute').select_option('00')
    page.locator('[data-pick-date="starts_at"]').click();day=page.locator('#calendar-date-panel .datepicker-cell.day[tabindex="0"]')
    expect(day).to_be_focused();page.keyboard.press('ArrowRight');page.keyboard.press('ArrowLeft');page.keyboard.press('Enter')
    page.keyboard.press('Escape');assert layout(page)
    discard();page.set_viewport_size({'width':1440,'height':1000})
    with tempfile.TemporaryDirectory(dir=evidence) as profile:
        zoom_profile(pw,Path(profile));zoom=pw.firefox.launch_persistent_context(profile,headless=True,**tls_options,no_viewport=True)
        try:
            zoom.add_cookies(page.context.cookies());z=zoom.pages[0];z.goto(base+'/portal/');expect(z.locator('#portal-view')).to_be_visible()
            z.locator('#open-calendar-offer-dialog').focus();z.keyboard.press('Enter')
            assert z.evaluate('devicePixelRatio')==2 and layout(z)
            z.locator('[data-pick-date="starts_at"]').focus();z.keyboard.press('Enter')
            expect(z.locator('#calendar-date-panel .datepicker-cell.day[tabindex="0"]')).to_be_focused()
            assert layout(z);z.screenshot(path=str(evidence/'native200-picker.png'))
        finally:zoom.close()
    page.reload();expect(page.locator('#portal-view')).to_be_visible()
    assert not errors and page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
    case(14,'390px, day-arrow keyboard/semantics, Reduced Motion, real200% zoom; no JavaScript errors')
    report['javascript_errors']=errors
    report['tls_scope']='STRICT_ORIGINAL_CA_HOSTNAME_AND_LEAF' if strict_tls else 'EPHEMERAL_LOCAL_FIXTURE_ONLY'
    return {'offer_id':offer_id,'title':title,'start':start}
