"""Narrow local finishing checks; synthetic UI only, never VPS/login copies."""
import importlib.util
from pathlib import Path
import sys
import tempfile

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import ExtendedKeyUsageOID
from playwright.sync_api import expect,sync_playwright
import pytest

ROOT=Path(__file__).resolve().parents[3]
EVIDENCE=ROOT/'release-artifacts/pilot-finishing-20261116'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


sys.path.insert(0,str(ROOT/'apps/webapp/scripts'))
qa=load('finishing_ui_qa','apps/webapp/scripts/run-cal1-browser-acceptance.py')
website=load('finishing_site_qa','apps/website/scripts/run-preview-browser-acceptance.py')


def test_existing_tls_builder_supplies_matching_localhost_chain():
    pilot=load('finishing_synthetic_tls','apps/webapp/scripts/run_vps_pilot.py')
    public_ca,public_leaf,private_leaf=pilot.certificates()
    ca=x509.load_pem_x509_certificate(public_ca);leaf=x509.load_pem_x509_certificate(public_leaf)
    key=serialization.load_pem_private_key(private_leaf,password=None)
    assert leaf.public_key().public_numbers()==key.public_key().public_numbers()
    leaf.verify_directly_issued_by(ca)
    assert ca.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
    assert not leaf.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
    assert leaf.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)==['localhost']
    assert ExtendedKeyUsageOID.SERVER_AUTH in leaf.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
    assert leaf.not_valid_after_utc<ca.not_valid_after_utc
    # Fresh synthetic material only, never exported to disk or installed.
    assert len((public_ca,public_leaf,private_leaf))==3


@pytest.mark.parametrize('width',[1440,390])
def test_coach_tour_matches_date_only_form_and_can_be_reopened(width):
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    with qa.synthetic_server() as base,sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            page=browser.new_page(ignore_https_errors=True,viewport={'width':width,'height':900},reduced_motion='reduce')
            qa.login(page,base,qa.COACH_EMAIL)
            page.locator('#pilot-help summary').click()
            page.locator('#tour-options button').filter(has_text='Coach').click()
            for _ in range(3):page.locator('#tour-next').click()
            expect(page.locator('#tour-title')).to_have_text('Datum und Uhrzeit')
            expect(page.locator('#tour-copy')).to_contain_text('Uhrzeit wählen Sie getrennt')
            assert 'HH:mm' not in page.locator('#tour-copy').inner_text()
            expect(page.locator('#tour-title')).to_be_focused()
            page.locator('#tour-next').click()
            expect(page.locator('#tour-copy')).to_contain_text('Gespeicherte Entwürfe bleiben erhalten')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.screenshot(path=str(EVIDENCE/('coach-tour-'+str(width)+'.png')))
            page.keyboard.press('Escape');expect(page.locator('#product-tour')).to_be_hidden()
            if not page.locator('#pilot-help').evaluate('e=>e.open'):page.locator('#pilot-help summary').click()
            page.locator('#tour-options button').filter(has_text='Coach').click()
            expect(page.locator('#tour-title')).to_have_text('Willkommen im Coach-Portal')
            page.locator('#tour-skip').click()
            page.locator('#open-calendar-offer-dialog').click()
            page.locator('#calendar-title').fill('DEMO finishing discard')
            page.locator('#calendar-offer-dialog [data-dialog-close]').last.click()
            page.get_by_role('button',name='Änderungen verwerfen',exact=True).click()
            expect(page.locator('#calendar-offer-dialog')).to_be_hidden()
        finally:browser.close()


def test_invitation_preview_requires_mapping_but_no_account_or_dispatch():
    with qa.synthetic_server() as base,sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            page=browser.new_page(ignore_https_errors=True,viewport={'width':1440,'height':1000})
            writes=[]
            def inventory(route):
                if route.request.method!='GET':writes.append(route.request.url);route.fulfill(status=503,json={'code':'invitation_delivery_unavailable'});return
                if '/coach-mappings' in route.request.url:
                    route.fulfill(json={'items':[{'id':'00000000-0000-4000-8000-000000000999','display_name':'DEMO bestätigter Coach','portal_user_id':None}]});return
                route.fulfill(json={'items':[],'total':0,'unmapped_coaches':0,'totals':{'active':0,'pending_activation':0},'next_offset':None,'invitations_enabled':False})
            page.route('**/api/v1/admin/**',inventory)
            qa.login(page,base,qa.ADMIN_EMAIL)
            page.get_by_role('button',name='Zugänge',exact=True).click()
            expect(page.locator('#invitation-delivery-state')).to_contain_text('noch nicht freigegeben')
            page.locator('#invitation-display-name').fill('DEMO neuer Coach')
            page.locator('#invitation-email').fill('synthetic.finishing@example.invalid')
            page.locator('#invitation-role').select_option('coach')
            page.locator('#prepare-invitation').click()
            expect(page.locator('#invitation-coach-id')).to_be_focused()
            expect(page.locator('#invitation-preview')).to_be_hidden()
            page.locator('#invitation-coach-id').fill('00000000-0000-4000-8000-000000000999')
            page.locator('#prepare-invitation').click()
            expect(page.locator('#invitation-preview')).to_contain_text('Noch nicht vorgemerkt oder versendet')
            expect(page.locator('#admin-invitation-form [type=submit]')).to_be_disabled()
            assert writes==[]
            assert page.evaluate('localStorage.length===0 && sessionStorage.length===0')
        finally:browser.close()


@pytest.mark.parametrize('width',[1440,960,390])
@pytest.mark.skipif(not (ROOT/'apps/website/dist-preview/index.html').is_file(),reason='Local Website preview build required')
def test_preview_journey_profile_finder_calendar_and_request(width):
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    with website.static_server() as origin,sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            page=browser.new_page(viewport={'width':width,'height':1000},reduced_motion='reduce');errors=[];external=[]
            page.on('pageerror',lambda error:errors.append(error.name))
            page.on('request',lambda request:external.append(request.url) if not request.url.startswith(origin) else None)
            base=origin+'/CompetenceHub'
            page.goto(base+'/coaches/susanne-klemm/')
            nav=page.get_by_role('navigation',name='Passendes Angebot und nächster Schritt')
            nav.get_by_role('link',name='Angebote dieses Coaches',exact=True).focus();page.keyboard.press('Enter')
            expect(page.locator('#finder-coach')).to_have_value('coaches/susanne-klemm')
            expect(page.locator('[data-finder-status]')).to_have_text('8 passende Angebote')
            assert page.locator('[data-finder-entry]:visible').count()==8
            page.locator('[data-finder-entry]:visible summary').first.click()
            link=page.locator('[data-finder-entry]:visible a[href^="mailto:"]').first
            assert 'Klemm' in link.get_attribute('href') and 'Becker' not in link.get_attribute('href')
            page.get_by_role('button',name='Filter zurücksetzen',exact=True).click()
            expect(page.locator('#finder-coach')).to_have_value('all')
            expect(page.locator('[data-finder-status]')).to_contain_text('27 passende Angebote')
            page.screenshot(path=str(EVIDENCE/('finder-'+str(width)+'.png')))
            page.get_by_role('navigation',name='Weitere Wege zum passenden Angebot').get_by_role('link',name='Kalender-Vorschau').click()
            expect(page.locator('.calendar-preview__scope')).to_contain_text('Ausschließlich Beispieldaten')
            page.get_by_role('navigation',name='Passendes Angebot und nächster Schritt').get_by_role('link',name='Bedarf besprechen').click()
            assert '/kontakt' in page.url
            assert page.locator('a[href^="mailto:"]').count()>0 and page.locator('a[href^="tel:"]').count()>0
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert not errors and not external
            page.goto(base+'/leistungen?coach=%3Cscript%3E#angebotsfinder')
            expect(page.locator('#finder-coach')).to_have_value('all')
        finally:browser.close()


@pytest.mark.skipif(not (ROOT/'apps/website/dist-preview/index.html').is_file(),reason='Local Website preview build required')
def test_preview_journey_keyboard_and_native200():
    with website.static_server() as origin,sync_playwright() as pw,tempfile.TemporaryDirectory() as folder:
        zoom=load('finishing_zoom','apps/webapp/scripts/vps_pilot_acceptance.py')
        zoom.zoom_profile(pw,Path(folder))
        context=pw.firefox.launch_persistent_context(folder,headless=True,no_viewport=True)
        try:
            page=context.pages[0];page.goto(origin+'/CompetenceHub/coaches/susanne-klemm/')
            assert page.evaluate('devicePixelRatio')==2
            link=page.get_by_role('navigation',name='Passendes Angebot und nächster Schritt').get_by_role('link',name='Angebote dieses Coaches')
            link.focus();page.keyboard.press('Enter')
            expect(page.locator('#finder-coach')).to_have_value('coaches/susanne-klemm')
            page.locator('#finder-coach').focus();page.keyboard.press('Home');page.keyboard.press('Enter')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.screenshot(path=str(EVIDENCE/'finder-native200.png'))
        finally:context.close()
