"""V1 browser acceptance against the protected remote API, owned users only."""
import json

import pyotp
from playwright.sync_api import expect,sync_playwright


def run(root,fixture,ca,directory,report,private,calendar):
    checks=[];report['v1_checks']=checks
    def check(label,value):
        report['last_v1_check']=label
        if not value:raise AssertionError(label)
        checks.append(label);print('PASS | '+label,flush=True)
    origin=calendar.ORIGIN
    def inventory(context):return json.loads(calendar.HTTPS(ca,context).call('/api/v1/admin/users')[2])['items']
    def row(page,email):return page.locator('#pilot-users > li').filter(has_text=email)
    def tour(page,label,count,automatic=False):
        if not automatic:
            page.locator('#pilot-help summary').click();page.locator('#tour-options button').filter(has_text=label).click()
        expect(page.locator('#product-tour')).to_be_visible()
        for step in range(count):
            expect(page.locator('#tour-progress')).to_have_text(f'Schritt {step+1} von {count}')
            expect(page.locator('#tour-title')).to_be_focused()
            page.locator('#tour-next').click()
        check(label+' remote guided tour and focus',page.locator('#product-tour').is_hidden())
    def manage(page,email,action,role=None,coach=None,conflict=False):
        row(page,email).get_by_role('button',name='Zugang verwalten',exact=True).click()
        page.locator('#user-management-action').select_option(action)
        if role:
            page.locator('#user-management-role').select_option(role)
            if coach:page.locator('#user-management-coach').fill(coach)
        page.locator('#user-management-confirm').check();page.get_by_role('button',name='Änderung übernehmen',exact=True).click()
        if conflict:
            expect(page.locator('#user-management-error')).to_contain_text('zwischenzeitlich geändert')
            page.locator('#user-management-reload').click()
            check('Remote stale administration rejects overwrite and reloads',True)
        expect(page.locator('#user-management-dialog')).to_be_hidden()
        expect(row(page,email)).to_be_visible()
    with sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True);contexts=[]
        try:
            admin_context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');contexts.append(admin_context)
            admin=admin_context.new_page();admin.goto(origin+'/portal/')
            admin.locator('#login-email').fill(fixture['accounts']['admin']['email']);admin.locator('#login-password').fill(fixture['accounts']['admin']['password'])
            admin.get_by_role('button',name='Anmelden',exact=True).click()
            admin.get_by_text('Recovery-Code',exact=True).click();admin.locator('#mfa-code').fill(private['admin']['recovery'].pop())
            admin.get_by_role('button',name='Bestätigen',exact=True).click();expect(admin.locator('#portal-view')).to_be_visible()
            tour(admin,'Admin',6)
            expect(admin.locator('#pilot-overview-state')).to_contain_text('Datenbank erreichbar')
            check('Remote Admin dashboard loaded',admin.locator('#pilot-metrics dd').count()>0)
            admin.get_by_role('button',name='Zugänge',exact=True).click()
            check('Remote original plus owned account inventory',len(inventory(admin_context))==8)
            for name in ('reviewer','coach'):
                item=fixture['invites'][name];role='calendar_reviewer' if name=='reviewer' else 'coach'
                admin.locator('#invitation-display-name').fill('DEMO V1 invited '+name)
                admin.locator('#invitation-email').fill(item['email']);admin.locator('#invitation-role').select_option(role)
                if name=='coach':admin.locator('#invitation-coach-id').fill(fixture['coaches']['invited'])
                with admin.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/admin/users/invitations')) as issued:
                    admin.locator('#admin-invitation-form [type=submit]').click()
                check('Remote '+name+' invitation queued without mail',issued.value.status==202)
                token=root.request('invitation_token',role=name)['token']
                if name=='reviewer':
                    manage(admin,item['email'],'revoke_invitation')
                    check('Remote revoked invitation denied',calendar.HTTPS(ca).call('/api/v1/auth/invitations/accept','POST',{'token':token,'password':item['password']})[0]==400)
                    row(admin,item['email']).get_by_role('button',name='Einladung neu vorbereiten').click()
                    with admin.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/admin/users/invitations')) as again:
                        admin.locator('#admin-invitation-form [type=submit]').click()
                    check('Remote invitation reissue accepted',again.value.status==202)
                    replacement=root.request('invitation_token',role=name)['token'];check('Remote reissue replaces token',replacement!=token);token=replacement
                context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');contexts.append(context)
                page=context.new_page();page.goto(origin+'/portal/#/einladung?token='+token)
                expect(page.locator('#account-token-view')).to_be_visible()
                check('Remote invitation fragment removed',not page.url.endswith(token))
                page.locator('#account-token-password').fill(item['password']);page.locator('#account-token-password-confirm').fill(item['password'])
                page.locator('#account-token-submit').click();expect(page.locator('#enrollment-code')).to_be_visible()
                totp=pyotp.TOTP(page.locator('#provisioning-secret').inner_text())
                page.locator('#enrollment-code').fill(totp.at(root.request('clock')['server_time']))
                page.get_by_role('button',name='Einrichtung abschließen').click();expect(page.locator('#recovery-view')).to_be_visible()
                codes=page.locator('#recovery-codes li').all_text_contents();check('Remote invited '+name+' ten recovery codes',len(codes)==10)
                private['invited_'+name]={'totp':totp.secret,'recovery':codes}
                page.locator('#recovery-confirmed').check();page.locator('#enter-portal').click()
                tour(page,'Prüfer' if name=='reviewer' else 'Coach',7,automatic=True)
                expect(page.locator('#pilot-overview-state')).to_contain_text('Datenbank erreichbar')
                check('Remote '+name+' dashboard loaded',page.locator('#pilot-metrics dd').count()>0)
                actor=calendar.HTTPS(ca,context)
                check('Remote invited '+name+' exact role',json.loads(actor.call(calendar.ACCESS+'/session')[2])['user']['roles']==[role])
                denied=actor.call('/api/v1/admin/users')[0]
                check('Remote invited '+name+' no Admin rights',denied in (401,403))
                check('Remote invited '+name+' mobile layout',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
                page.screenshot(path=str(directory/('v1-'+name+'-390.png')),full_page=True)
                if name=='coach':
                    manage(admin,item['email'],'suspend',conflict=True)
                    manage(admin,item['email'],'suspend')
                    check('Remote suspension revokes session',actor.call(calendar.ACCESS+'/session')[0]==401)
                    manage(admin,item['email'],'enable')
                    check('Remote reenable does not revive session',actor.call(calendar.ACCESS+'/session')[0]==401)
                    manage(admin,item['email'],'set_role','calendar_reviewer')
                    check('Remote exact role replacement',next(x for x in inventory(admin_context) if x['email']==item['email'])['roles']==['calendar_reviewer'])
                    manage(admin,item['email'],'set_role','coach',fixture['coaches']['invited'])
                    check('Remote Coach UUID remains stable',next(x for x in inventory(admin_context) if x['email']==item['email'])['coach_id']==fixture['coaches']['invited'])
                    row(admin,item['email']).get_by_role('button',name='Zugang verwalten',exact=True).click()
                    admin.locator('#user-management-dialog details summary').click()
                    admin.locator('#user-management-audit-load').click()
                    expect(admin.locator('#user-management-audit li').first).to_be_visible()
                    check('Remote bounded administration audit available',1<=admin.locator('#user-management-audit li').count()<=20)
                    admin.keyboard.press('Escape')
                del token
            check('Remote dashboard and MFA inventory',all('mfa_enabled' in x and 'last_authenticated_at' in x for x in inventory(admin_context)))
            report['v1_phase']='native200_profile'
            zoom_dir=directory/'v1-zoom';calendar.zoom_profile(pw,zoom_dir)
            zoom=pw.firefox.launch_persistent_context(str(zoom_dir),headless=True,no_viewport=True)
            try:
                report['v1_phase']='native200_session'
                zoom.add_cookies(admin_context.cookies());page=zoom.new_page();page.goto(origin+'/portal/');expect(page.locator('#portal-view')).to_be_visible()
                report['v1_phase']='native200_inventory'
                access=page.get_by_role('button',name='Zugänge',exact=True)
                access.scroll_into_view_if_needed()
                hit=access.evaluate('''button => {
                    const range=document.createRange();range.selectNodeContents(button);
                    return [...range.getClientRects()].filter(r=>r.width&&r.height).every(r=>{
                        const node=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
                        const box=button.getBoundingClientRect();
                        return node && button.contains(node) && r.left>=box.left-1 && r.right<=box.right+1;
                    });
                }''')
                check('Remote native200 tab text hit-test and bounds',hit)
                # Native Firefox zoom has Playwright mouse coordinate drift;
                # use real keyboard activation, never force-click through overlap.
                access.focus();page.keyboard.press('Enter')
                report['v1_phase']='native200_management_dialog'
                manage_button=row(page,fixture['invites']['coach']['email']).get_by_role('button',name='Zugang verwalten',exact=True)
                manage_button.focus();page.keyboard.press('Enter')
                page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
                check('Remote native200 Admin keyboard focus',page.evaluate('devicePixelRatio===2 && innerWidth>600 && innerWidth<800 && document.querySelector("#user-management-dialog").contains(document.activeElement)'))
                check('Remote native200 no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
                submit=page.get_by_role('button',name='Änderung übernehmen',exact=True)
                submit.focus();expect(submit).to_be_focused()
                check('Remote native200 submit scrolls into viewport',submit.evaluate('el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight+1&&r.left>=0&&r.right<=innerWidth+1}'))
                page.screenshot(path=str(directory/'v1-native200-actions.png'))
                page.locator('#user-management-title').focus()
                page.screenshot(path=str(directory/'v1-native200.png'))
            finally:zoom.close()
            report['v1_phase']='complete'
            report['user_management']=report['invitation_workflow']='PASS'
            return private
        finally:
            for context in contexts:context.close()
            browser.close()
