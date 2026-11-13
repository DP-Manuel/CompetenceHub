"""Onboarding V1 native acceptance in the owned local PostgreSQL fixture only."""
import json
import math
from pathlib import Path
import tempfile
import sys
import asyncio
from uuid import UUID,uuid4

import pyotp
from playwright.sync_api import expect,sync_playwright
from sqlalchemy import text
from scripts.cal1_pilot_acceptance import qa,demo


def run(fixture,options,report,evidence):
    if not fixture.local_container_rehearsal:raise RuntimeError('Owned local fixture only')
    class Checks(qa.Acceptance):
        def check(self,label,value):
            report['last_onboarding_check']=label
            super().check(label,value)
            sys.stdout.flush()
    checks=Checks();report['onboarding_checks']=checks.checks
    state={};private={};errors=[]
    def app(port):
        value=fixture.app(port);state['app']=value
        @value.middleware('http')
        async def delayed_inventory(request,call_next):
            order=None
            if request.url.path=='/api/v1/admin/users' and state.get('delay_inventory'):
                state['inventory_requests']=state.get('inventory_requests',0)+1
                order=state['inventory_requests']
                if order==1:await asyncio.sleep(.25)
            response=await call_next(request)
            if order is not None:response.headers['x-synthetic-inventory-order']=str(order)
            return response
        return value
    def user_row(page,user):return page.locator('#pilot-users > li').filter(has_text=fixture.emails[user])
    def finish_enrollment(page,key):
        expect(page.locator('#enrollment-code')).to_be_visible()
        private[key]={'totp':pyotp.TOTP(page.locator('#provisioning-secret').inner_text())}
        page.locator('#enrollment-code').fill(private[key]['totp'].at(fixture.now.timestamp()))
        page.get_by_role('button',name='Einrichtung abschließen').click()
        expect(page.locator('#recovery-view')).to_be_visible()
        private[key]['recovery']=page.locator('#recovery-codes li').all_text_contents()
        checks.check(key+' ten native one-time recovery codes',len(private[key]['recovery'])==10)
        page.locator('#recovery-confirmed').check();page.locator('#enter-portal').click()
        expect(page.locator('#product-tour')).to_be_visible()
        checks.check(key+' first-onboarding automatic introduction',True)
        page.locator('#tour-skip').click()
    def login(page,key,base):
        page.goto(base+'/portal/');page.locator('#login-email').fill(fixture.emails[key]);page.locator('#login-password').fill(fixture.password)
        page.get_by_role('button',name='Anmelden',exact=True).click()
        if key not in private:finish_enrollment(page,key)
        else:
            page.get_by_text('Recovery-Code',exact=True).click();page.locator('#mfa-code').fill(private[key]['recovery'].pop())
            page.get_by_role('button',name='Bestätigen',exact=True).click();expect(page.locator('#portal-view')).to_be_visible()
    def manage(admin,key,action,role=None,coach=None,expect_error=None):
        user_row(admin,key).get_by_role('button',name='Zugang verwalten').click()
        admin.locator('#user-management-action').select_option(action)
        if role:
            admin.locator('#user-management-role').select_option(role)
            if coach:admin.locator('#user-management-coach').fill(str(coach))
        admin.locator('#user-management-confirm').check()
        admin.get_by_role('button',name='Änderung übernehmen').click()
        if expect_error:
            expect(admin.locator('#user-management-error')).to_contain_text(expect_error)
            admin.locator('#user-management-dialog').get_by_role('button',name='Abbrechen').click()
        else:expect(admin.locator('#user-management-dialog')).to_be_hidden()
    def token_for(user):
        async def read(c):
            return (await c.execute(text("""SELECT o.id,o.encrypted_payload,o.key_version
                FROM competence_hub.auth_token_delivery_outbox o JOIN competence_hub.auth_one_time_tokens t ON t.id=o.one_time_token_id
                WHERE t.portal_user_id=:id AND t.purpose='invitation' AND t.revoked_at IS NULL AND t.consumed_at IS NULL"""),{'id':user})).mappings().one()
        row=fixture.database(read)
        return state['app'].state.outbox_cipher.decrypt(bytes(row['encrypted_payload']),key_version=row['key_version'],subject_id=f"invitation:{row['id']}")
    def tour(page,label,count):
        page.locator('#pilot-help summary').click();page.locator('#tour-options button').filter(has_text=label).click()
        for index in range(count):
            expect(page.locator('#tour-progress')).to_have_text(f'Schritt {index+1} von {count}')
            expect(page.locator('#tour-title')).to_be_focused()
            if index==0:
                checks.check(label+' positioned arrow is visible',page.locator('.tour-pointer').is_visible())
                page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
                checks.check(label+' keyboard focus remains in introduction',page.evaluate("document.querySelector('#product-tour').contains(document.activeElement)"))
                tag={'Admin':'admin','Coach':'coach','Prüfer':'reviewer'}[label]
                size='native200' if page.evaluate('devicePixelRatio===2') else str(page.viewport_size['width'])
                demo.screenshot(page,evidence/(tag+'-tour-'+size+'.png'),'native-200' if size=='native200' else size)
            demo.geometry(page,checks,label+' tour geometry '+str(index+1))
            checks.check(label+' tour target not covered '+str(index+1),page.evaluate("""() => {
              const target=document.querySelector('.tour-target'),tip=document.querySelector('#product-tour');
              if(!target || document.querySelector('.tour-pointer').hidden)return true;
              const a=target.getBoundingClientRect(),b=tip.getBoundingClientRect();
              return a.right<=b.left || b.right<=a.left || a.bottom<=b.top || b.bottom<=a.top;
            }"""))
            page.locator('#tour-next').click()
        expect(page.locator('#product-tour')).to_be_hidden()
        page.reload();expect(page.locator('#portal-view')).to_be_visible()
        checks.check(label+' completed tour does not repeat',page.locator('#product-tour').is_hidden())
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=str(options.browser_executable))
        contexts=[]
        def context(**kwargs):
            value=browser.new_context(ignore_https_errors=True,**kwargs);contexts.append(value)
            value.set_default_timeout(15000)
            value.on('page',lambda p:p.on('pageerror',lambda e:errors.append(e.name)))
            return value
        with qa.synthetic_server(app) as base:
            try:
                ctx=context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
                admin=ctx.new_page();login(admin,'admin',base)
                csrf_capture={}
                def capture_management(request):
                    if request.method=='PATCH' and '/api/v1/admin/users/' in request.url:
                        csrf_capture['value']=request.headers.get('x-csrf-token')
                admin.on('request',capture_management)
                tour(admin,'Admin',6)
                admin.get_by_role('button',name='Zugänge',exact=True).click()
                checks.check('Own administrative account UI protected',user_row(admin,'admin').get_by_role('button',name='Zugang verwalten').is_disabled())
                admin.locator('#invitation-display-name').fill('DEMO Neuer Coach')
                admin.locator('#invitation-email').fill('synthetic.onboarding-coach@example.invalid')
                admin.locator('#prepare-invitation').click()
                expect(admin.locator('#invitation-preview')).to_contain_text('Noch nicht vorgemerkt oder versendet')
                checks.check('Preparation without dispatch has no account creation',ctx.request.get(base+'/api/v1/admin/users').json()['total']==6)
                state['app'].state.invitation_delivery_enabled=True # Local capture only, no SMTP.
                coach_id=uuid4();fixture.coaches['onboarding']=coach_id
                async def seed(c):
                    await c.execute(text("INSERT INTO competence_hub.coaches(id,display_name,public_profile_status) VALUES(:id,'DEMO Onboarding Coach','synthetic')"),{'id':coach_id})
                fixture.database(seed)
                checks.check('Owned unassigned synthetic Coach seeded',True)
                pages={}
                for key,role in (('onboarding-reviewer','calendar_reviewer'),('onboarding-coach','coach')):
                    fixture.emails[key]='synthetic.'+key+'@example.invalid'
                    admin.get_by_role('button',name='Zugänge',exact=True).click()
                    admin.locator('#invitation-display-name').fill('DEMO '+key)
                    admin.locator('#invitation-email').fill(fixture.emails[key]);admin.locator('#invitation-role').select_option(role)
                    if role=='coach':admin.locator('#invitation-coach-id').fill(str(coach_id))
                    checks.check(role+' invitation form ready',True)
                    with admin.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/admin/users/invitations'),timeout=15000) as response:
                        admin.locator('#admin-invitation-form button[type=submit]').click()
                    checks.check(role+' invitation response received',True)
                    checks.check(role+' native invitation accepted',response.value.status==202)
                    inventory=ctx.request.get(base+'/api/v1/admin/users',timeout=15000).json()
                    pending=next(u for u in inventory['items'] if u['email']==fixture.emails[key])
                    user=UUID(pending['id']);fixture.users[key]=user
                    expect(user_row(admin,key)).to_be_visible()
                    checks.check(role+' pending inventory has no token',not any('token' in name or 'secret' in name for name in pending))
                    token=token_for(user)
                    if role=='calendar_reviewer':
                        manage(admin,key,'revoke_invitation')
                        async def revoked_delivery(c):
                            return await c.scalar(text("""SELECT bool_and(o.status='canceled' AND o.encrypted_payload IS NULL AND o.recipient_email IS NULL)
                                FROM competence_hub.auth_token_delivery_outbox o JOIN competence_hub.auth_one_time_tokens t ON t.id=o.one_time_token_id
                                WHERE t.portal_user_id=:id"""),{'id':user})
                        checks.check('Native revoked delivery is cancelled and scrubbed',fixture.database(revoked_delivery) is True)
                        invalid=ctx.request.post(base+'/api/v1/auth/invitations/accept',data={'token':token,'password':fixture.password},headers={'Origin':base})
                        checks.check('Revoked native invitation cannot activate',invalid.status==400)
                        user_row(admin,key).get_by_role('button',name='Einladung neu vorbereiten').click()
                        with admin.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/admin/users/invitations')) as reissued:
                            admin.locator('#admin-invitation-form button[type=submit]').click()
                        expect(user_row(admin,key)).to_be_visible()
                        reissued_user=next(u for u in ctx.request.get(base+'/api/v1/admin/users',timeout=15000).json()['items'] if u['email']==fixture.emails[key])
                        checks.check('Native reissue retains same inactive user',reissued.value.status==202 and reissued_user['id']==str(user))
                        replacement=token_for(user);checks.check('Reissued token is distinct',replacement!=token);token=replacement
                    page=context(viewport={'width':390,'height':844},reduced_motion='reduce').new_page();pages[key]=page
                    page.goto(base+'/portal/#/einladung?token='+token)
                    expect(page.locator('#account-token-view')).to_be_visible()
                    page.locator('#account-token-password').fill(fixture.password);page.locator('#account-token-password-confirm').fill(fixture.password)
                    page.locator('#account-token-submit').click();finish_enrollment(page,key)
                    checks.check(role+' exact role after activation',page.request.get(base+'/api/v1/portal/access/session').json()['user']['roles']==[role])
                    tour(page,'Coach' if role=='coach' else 'Prüfer',9 if role=='coach' else 7)
                    page.screenshot(path=str(evidence/(role+'-390.png')),full_page=True)
                    consumed=ctx.request.post(base+'/api/v1/auth/invitations/accept',data={'token':token,'password':fixture.password},headers={'Origin':base})
                    checks.check('Consumed invitation stays one-time, including rate-limit denial',consumed.status in (400,429))
                    del token
                coach=pages['onboarding-coach'];key='onboarding-coach'
                coach.locator('#pilot-help summary').click();coach.locator('#tour-options button').filter(has_text='Coach').click()
                coach.locator('#tour-next').click();expect(coach.locator('#tour-progress')).to_have_text('Schritt 2 von 9')
                coach.reload();expect(coach.locator('#tour-progress')).to_have_text('Schritt 2 von 9')
                coach.keyboard.press('Escape');checks.check('Tab-local progress resumes and Escape closes',coach.locator('#product-tour').is_hidden())
                admin.get_by_role('button',name='Zugänge',exact=True).click()
                manage(admin,key,'suspend');checks.check('Suspension immediately denies existing native session',coach.request.get(base+'/api/v1/portal/access/session').status==401)
                expect(user_row(admin,key)).to_contain_text('Gesperrt')
                manage(admin,key,'enable');checks.check('Reenable never revives revoked session',coach.request.get(base+'/api/v1/portal/access/session').status==401)
                login(coach,key,base)
                # Keep the editor open while another authorized request advances its version.
                user_row(admin,key).get_by_role('button',name='Zugang verwalten').click()
                current=next(u for u in ctx.request.get(base+'/api/v1/admin/users').json()['items'] if u['id']==str(fixture.users[key]))
                csrf=csrf_capture['value']
                changed=ctx.request.patch(base+'/api/v1/admin/users/'+current['id'],data={'action':'enable','expected_version':current['version']},headers={'Origin':base,'X-CSRF-Token':csrf})
                checks.check('Concurrent native Admin change succeeds',changed.status==200)
                admin.locator('#user-management-confirm').check();admin.get_by_role('button',name='Änderung übernehmen').click()
                expect(admin.locator('#user-management-error')).to_contain_text('zwischenzeitlich geändert')
                expect(admin.locator('#user-management-reload')).to_be_visible()
                demo.geometry(admin,checks,'Native stale administration dialog')
                admin.locator('#user-management-reload').click();expect(admin.locator('#user-management-dialog')).to_be_hidden()
                checks.check('Native stale Admin editor rejects overwrite and offers reload',True)
                login(coach,key,base)
                manage(admin,key,'set_role','calendar_reviewer')
                checks.check('Role change revokes existing native session',coach.request.get(base+'/api/v1/portal/access/session').status==401)
                login(coach,key,base)
                checks.check('New session has exact replacement role',coach.request.get(base+'/api/v1/portal/access/session').json()['user']['roles']==['calendar_reviewer'])
                manage(admin,key,'set_role','coach',fixture.coaches['coach'],expect_error='anderweitig vergeben')
                manage(admin,key,'set_role','coach',coach_id)
                checks.check('Stable Coach UUID preserved',next(u for u in ctx.request.get(base+'/api/v1/admin/users').json()['items'] if u['id']==str(fixture.users[key]))['coach_id']==str(coach_id))
                audit=ctx.request.get(base+'/api/v1/admin/users/'+str(fixture.users[key])+'/audit').json()['items']
                checks.check('Native bounded minimal administration audit',0<len(audit)<=20 and all(set(row)=={'occurred_at','action','outcome','actor_user_id'} for row in audit))
                state['inventory_requests']=0;state['delay_inventory']=True
                with admin.expect_response(lambda response:response.headers.get('x-synthetic-inventory-order')=='1'):
                    admin.evaluate("""() => {const tab=[...document.querySelectorAll('#portal-navigation button')].find(e=>e.textContent==='Zugänge');tab.click();tab.click();}""")
                admin.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
                expect(admin.locator('#pilot-users > li')).to_have_count(8)
                checks.check('Out-of-order native inventory responses never duplicate users',state['inventory_requests']>=2 and user_row(admin,key).count()==1)
                state['delay_inventory']=False
                admin.screenshot(path=str(evidence/'admin-desktop.png'),full_page=True)
                admin.set_viewport_size({'width':390,'height':844})
                user_row(admin,key).get_by_role('button',name='Zugang verwalten').click()
                demo.geometry(admin,checks,'Admin management mobile390')
                admin.keyboard.press('Tab');admin.keyboard.press('Shift+Tab')
                checks.check('Administration keyboard focus stays in modal',admin.evaluate("document.querySelector('#user-management-dialog').contains(document.activeElement)"))
                admin.screenshot(path=str(evidence/'admin-management-390.png'))
                admin.keyboard.press('Escape');expect(admin.locator('#user-management-dialog')).to_be_hidden()
                admin.set_viewport_size({'width':1440,'height':1000})
                with tempfile.TemporaryDirectory(prefix='onboarding-zoom-',dir=evidence) as folder:
                    default=Path(folder)/'Default';default.mkdir()
                    (default/'Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2),'0':math.log(2)/math.log(1.2)}}}))
                    zoom=pw.chromium.launch_persistent_context(folder,headless=True,executable_path=str(options.browser_executable),ignore_https_errors=True,no_viewport=True,args=['--window-size=1440,1000','--force-device-scale-factor=1'])
                    try:
                        zoom.add_cookies(ctx.cookies());page=zoom.new_page();page.goto(base+'/portal/')
                        expect(page.locator('#portal-view')).to_be_visible();tour(page,'Admin',6)
                        checks.check('Native 200 percent admin introduction',page.evaluate('devicePixelRatio===2 && innerWidth>600 && innerWidth<800'))
                        page.get_by_role('button',name='Zugänge',exact=True).click()
                        target=user_row(page,key)
                        expect(target).to_have_count(1)
                        buttons=target.get_by_role('button',name='Zugang verwalten',exact=True)
                        report['zoom_management_targets']=buttons.count()
                        demo.screenshot(page,evidence/'admin-native200-before-management.png','native-200')
                        buttons.click()
                        demo.geometry(page,checks,'Admin management native200')
                        demo.screenshot(page,evidence/'admin-native200.png','native-200')
                        page.locator('#user-management-dialog [data-close]').first.focus()
                        for _ in range(12):
                            page.keyboard.press('Tab')
                            if page.locator('#user-management-form [type=submit]').evaluate('e => e===document.activeElement'):break
                        checks.check('Native200 management save reached by keyboard without clipping',page.locator('#user-management-form [type=submit]').evaluate('e => {const r=e.getBoundingClientRect();return e===document.activeElement && r.top>=0 && r.bottom<=innerHeight;}'))
                        demo.screenshot(page,evidence/'admin-native200-actions.png','native-200')
                    finally:zoom.close()
                checks.check('No credentials or preferences in Web Storage',admin.evaluate('localStorage.length===0 && sessionStorage.length===0'))
                checks.check('No browser JavaScript errors',not errors)
            finally:
                for value in contexts:value.close()
                browser.close()
                async def buckets(c):await c.execute(text('DELETE FROM competence_hub.auth_rate_limit_buckets'))
                fixture.database(buckets)
