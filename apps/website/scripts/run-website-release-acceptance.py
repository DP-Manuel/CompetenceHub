"""Focused Website journeys against both local artifacts or approved public Preview."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'release-artifacts/website-release-20261117'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


qa = load('website_release_static', 'apps/website/scripts/run-preview-browser-acceptance.py')
zoom = load('website_release_zoom', 'apps/webapp/scripts/vps_pilot_acceptance.py')


def fit(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'Horizontal overflow'
    assert page.locator('main .actions .button, .preview-journey-links a').evaluate_all('''nodes=>nodes.every(e=>{
        const b=e.getBoundingClientRect();if(!b.width||!b.height)return true;
        const range=document.createRange();range.selectNodeContents(e);
        return Array.from(range.getClientRects()).every(r=>r.left>=b.left-1&&r.right<=b.right+1&&r.top>=b.top-1&&r.bottom<=b.bottom+1);
    })'''), 'New navigation text escapes its control'


def mailto(link, expected):
    target = urlsplit(link.get_attribute('href'))
    assert target.scheme == 'mailto' and target.path == 'competencehub@donner-partner.de'
    query = parse_qs(target.query)
    assert expected in query['subject'][0] and expected in query['body'][0]


def wait_for_portrait(page, timeout=15000):
    page.wait_for_function('''() => {
        const image = document.querySelector('.coach-profile-portrait img');
        return image?.complete && image.naturalWidth > 0;
    }''', timeout=timeout)


def journey(context, base, mode, label, page=None):
    page = page if page is not None else context.new_page()
    errors = []; external = []; writes = []
    page.on('pageerror', lambda error: errors.append(error.name))
    def guard(route):
        request = route.request
        if request.method not in ('GET', 'HEAD'): writes.append(request.method); route.abort()
        elif urlsplit(request.url).netloc != urlsplit(base).netloc: external.append(request.url); route.abort()
        else: route.continue_()
    page.route('**/*', guard)
    page.goto(base + '/unternehmen/'); fit(page)
    page.get_by_role('link', name='Workshops finden', exact=True).focus(); page.keyboard.press('Enter')
    expect(page.locator('[data-finder-status]')).to_contain_text('3 passende Angebote' if mode == 'production' else '27 passende Angebote')
    page.locator('#finder-coach').select_option('coaches/guelcan-elmas-brandes')
    expect(page.locator('[data-finder-entry]:visible')).to_have_count(3)
    page.locator('[data-finder-entry]:visible summary').first.focus()
    page.keyboard.press('Enter')
    mailto(page.locator('[data-finder-entry]:visible a[href^="mailto:"]').first, 'Gülcan Elmas-Brandes')
    fit(page); page.screenshot(path=str(EVIDENCE / (label + '-finder.png')))
    page.locator('[data-finder-entry]:visible [data-finder-profile]').first.focus()
    page.keyboard.press('Enter')
    expect(page.locator('h1')).to_have_text('Frau Gülcan Elmas-Brandes')
    expect(page.locator('[data-offer-family]')).to_have_count(3)
    expect(page.locator('[data-offer-format]')).to_have_count(5)
    wait_for_portrait(page)
    fit(page); page.screenshot(path=str(EVIDENCE / (label + '-guelcan.png')))
    page.get_by_role('navigation', name='Passendes Angebot und nächster Schritt').get_by_role('link', name='Angebote dieses Coaches').focus()
    page.keyboard.press('Enter')
    expect(page.locator('#finder-coach')).to_have_value('coaches/guelcan-elmas-brandes')
    page.locator('#finder-audience').select_option('private')
    # Unknown/unsupported audience is never replaced by invented offers.
    expect(page.locator('[data-finder-empty]')).to_be_visible()
    page.get_by_role('button', name='Filter zurücksetzen', exact=True).focus()
    page.keyboard.press('Enter')
    page.goto(base + '/unternehmen/')
    page.get_by_role('link', name='Coaches für Führung', exact=True).focus()
    page.keyboard.press('Enter')
    heading = page.get_by_role('heading', name='Herr Christian Galvano', exact=True)
    expect(heading).to_be_visible()
    heading.locator('xpath=ancestor::article').get_by_role('link', name='Profil ansehen', exact=True).focus()
    page.keyboard.press('Enter')
    mailto(page.get_by_role('link', name='Coaching per E-Mail anfragen', exact=True), 'Christian Galvano')
    fit(page)
    page.goto(base + '/coaches/manuela-rodriguez/')
    mailto(page.get_by_role('link', name='Anfrage per E-Mail', exact=True), 'Manuela Rodríguez, M.A.')
    page.goto(base + '/kalender/')
    expect(page.locator('.calendar-preview__scope')).to_contain_text('Ausschließlich Beispieldaten')
    page.get_by_role('navigation', name='Passendes Angebot und nächster Schritt').get_by_role('link', name='Bedarf besprechen').focus()
    page.keyboard.press('Enter')
    expect(page.locator('.form-note')).to_contain_text('E-Mail-Programm')
    assert page.locator('a[href^="tel:+491726799972"]').count() == 1
    assert page.locator('a[href^="mailto:competencehub@donner-partner.de"]').count() >= 1
    page.locator('[name=company]').focus(); page.keyboard.press('Tab')
    expect(page.locator('[name=contact]')).to_be_focused()
    assert not page.locator('form').evaluate('e=>e.checkValidity()')
    page.locator('[name=contact]').fill('Synthetischer Website-Test')
    page.locator('[name=email]').fill('synthetic.website@example.invalid')
    page.locator('[name=topic]').select_option(label='Workshop oder Vortrag')
    assert page.locator('form').evaluate('e=>e.checkValidity()')
    fit(page)
    for route in ('datenschutz', 'impressum'):
        page.goto(base + '/' + route + '/')
        assert page.locator('a[href="https://donner-partner.de/dp/' + route + '/"]').count() >= 1
    missing = page.goto(base + '/coaches/carolin-hupp/')
    assert missing.status == 404 and 'Carolin Hupp' not in page.locator('body').inner_text()
    assert not errors and not external and not writes
    page.close()


def run(live=None):
    EVIDENCE.mkdir(parents=True, exist_ok=True); completed = []
    with sync_playwright() as pw:
        for mode in (('preview',) if live else ('production', 'preview')):
            with qa.static_server(mode) if live is None else __import__('contextlib').nullcontext(live) as origin:
                base = origin + ('/CompetenceHub' if mode == 'preview' else '')
                browser = pw.firefox.launch(headless=True)
                try:
                    for width in (1440, 390):
                        context = browser.new_context(viewport={'width': width, 'height': 1000}, reduced_motion='reduce')
                        try: journey(context, base, mode, f'{mode}-{width}'); completed.append(f'{mode}-{width}')
                        finally: context.close()
                    context = browser.new_context(java_script_enabled=False, viewport={'width':390,'height':900})
                    try:
                        page = context.new_page(); page.goto(base + '/leistungen/')
                        expect(page.locator('[data-finder-entry]')).to_have_count(3 if mode == 'production' else 27)
                        expect(page.locator('[data-finder-form]')).to_be_hidden()
                        page.locator('summary').filter(has_text='Business & Balance').first.click()
                        mailto(page.locator('a[aria-label*="Tagesworkshop"][href^="mailto:"]').first, 'Gülcan Elmas-Brandes')
                        completed.append(mode + '-no-js')
                    finally: context.close()
                finally: browser.close()
                with tempfile.TemporaryDirectory() as temporary:
                    zoom.zoom_profile(pw, Path(temporary))
                    context = pw.firefox.launch_persistent_context(temporary, headless=True, no_viewport=True, reduced_motion='reduce')
                    try:
                        native_page, = context.pages
                        native_page.goto(base + '/unternehmen/')
                        assert native_page.evaluate('devicePixelRatio') == 2
                        journey(context, base, mode, mode + '-native200', page=native_page)
                        completed.append(mode + '-native200')
                    finally: context.close()
    result = {'status':'PASS','journeys':completed,'scope':'public Website only; no VPS/SFTP/account action'}
    (EVIDENCE / ('public-preview.json' if live else 'local-browser.json')).write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--live-preview', action='store_true')
    options = parser.parse_args()
    run('https://dp-manuel.github.io' if options.live_preview else None)
