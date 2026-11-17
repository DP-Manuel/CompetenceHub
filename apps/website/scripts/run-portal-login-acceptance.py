"""Local header-only acceptance. Synthetic destination is intercepted, never contacted."""
import importlib.util
import json
from pathlib import Path
import tempfile
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / '.tmp/portal-login-20261117'
DESIGN = 'http://127.0.0.1:4327'
ACTIVE = 'http://127.0.0.1:4328'
SYNTHETIC_TARGET = 'https://portal.example.invalid/portal/'


def load_zoom():
    spec = importlib.util.spec_from_file_location('header_zoom', ROOT / 'apps/webapp/scripts/vps_pilot_acceptance.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_layout(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
    assert page.locator('.site-header').evaluate('''header => {
        const visible = [...header.querySelectorAll('.brand, .nav--desktop, .nav-menu > summary, .header-actions > a, .header-actions > button')]
          .filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
        const rects = visible.map(e => e.getBoundingClientRect());
        const h = header.getBoundingClientRect();
        return rects.every(r => r.left >= h.left && r.right <= h.right + 1)
          && rects.every((a,i) => rects.slice(i+1).every(b => !(a.left < b.right-1 && a.right > b.left+1 && a.top < b.bottom-1 && a.bottom > b.top+1)));
    }'''), 'Header controls overlap or escape'


def check_control(page, control):
    expect(control).to_be_focused()
    assert control.evaluate('e=>e.matches(":focus-visible") && getComputedStyle(e).outlineStyle!=="none"')
    assert control.locator('svg').get_attribute('aria-hidden') == 'true'
    assert control.evaluate('''e=>{
      const b=e.getBoundingClientRect(), r=document.createRange();r.selectNodeContents(e.querySelector('span'));
      const rects=[...r.getClientRects()];
      return b.width>=44 && b.height>=44 && rects.every(t=>t.left>=b.left && t.right<=b.right && t.top>=b.top && t.bottom<=b.bottom);
    }''')
    assert control.evaluate('''e=>{
      const color = value => value.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{
        v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;
      }).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
      const s=getComputedStyle(e), a=color(s.color), b=color(s.backgroundColor);
      return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)>=4.5;
    }'''), 'Login label contrast below 4.5:1'


def case(context, origin, label, active=False, page=None):
    page = page or context.new_page()
    errors, external, writes = [], [], []
    page.on('pageerror', lambda error: errors.append(error.name))

    def guard(route):
        request = route.request
        if request.method != 'GET':
            writes.append(request.method); route.abort()
        elif active and request.url == SYNTHETIC_TARGET:
            route.fulfill(status=200, content_type='text/html', body='<h1>Synthetischer gemeinsamer Portal-Einstieg</h1>')
        elif urlsplit(request.url).netloc == urlsplit(origin).netloc:
            route.continue_()
        else:
            external.append(request.url); route.abort()

    page.route('**/*', guard)
    page.goto(origin + '/kontakt/')
    check_layout(page)
    mobile = page.evaluate('innerWidth <= 1240')
    if mobile:
        expect(page.locator('[data-portal-login]:visible')).to_have_count(0)
        menu = page.locator('.nav-menu > summary')
        menu.focus(); page.keyboard.press('Enter'); page.keyboard.press('Tab')
        # Firefox may give an overflowing scroll region its own native Tab stop.
        region = page.get_by_role('navigation', name='Mobile Hauptnavigation')
        if region.evaluate('e=>e===document.activeElement'):
            page.keyboard.press('Tab')
        control = page.locator('.portal-login--mobile')
        expect(page.get_by_role('navigation', name='Mobile Hauptnavigation').locator('> :first-child')).to_have_attribute('data-portal-login', 'enabled' if active else 'design')
    else:
        control = page.locator('.portal-login--desktop')
        control.focus(); page.keyboard.press('Tab'); page.keyboard.press('Shift+Tab')
    expect(page.locator('[data-portal-login]:visible')).to_have_count(1)
    check_control(page, control)
    page.screenshot(path=str(EVIDENCE / (label + '.png')))
    if active:
        expect(control).to_have_attribute('href', SYNTHETIC_TARGET)
        assert page.locator('a[data-portal-login]').evaluate_all('(nodes)=>nodes.every(e=>e.href===' + json.dumps(SYNTHETIC_TARGET) + ')')
        page.keyboard.press('Enter')
        expect(page).to_have_url(SYNTHETIC_TARGET)
        expect(page.get_by_role('heading')).to_have_text('Synthetischer gemeinsamer Portal-Einstieg')
    else:
        expect(control).to_have_attribute('aria-disabled', 'true')
        assert control.get_attribute('href') is None
        page.keyboard.press('Enter'); page.keyboard.press('Space')
        expect(page).to_have_url(origin + '/kontakt/')
        assert page.locator('input[type=password]').count() == 0
        if mobile:
            page.keyboard.press('Shift+Tab')
            if region.evaluate('e=>e===document.activeElement'):
                page.keyboard.press('Shift+Tab')
            expect(menu).to_be_focused()
            page.keyboard.press('Enter')
            expect(page.locator('.nav-menu')).not_to_have_attribute('open', '')
            page.locator('.nav-menu > summary').focus(); page.keyboard.press('Enter')
            contact = page.get_by_role('navigation', name='Mobile Hauptnavigation').get_by_role('link', name='Kontakt', exact=True)
            contact.focus(); page.keyboard.press('Enter')
            expect(page).to_have_url(origin + '/kontakt')
    assert not errors and not external and not writes
    page.close()


def run():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    completed = []
    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=True)
        try:
            for width in (1440, 1280, 1241, 1240, 1100, 768, 390, 320):
                context = browser.new_context(viewport={'width':width,'height':844}, reduced_motion='reduce')
                try:
                    case(context, DESIGN, 'design-' + str(width)); completed.append('design-' + str(width))
                finally:
                    context.close()
            for width in (1440, 390):
                context = browser.new_context(viewport={'width':width,'height':844})
                try:
                    case(context, ACTIVE, 'synthetic-active-' + str(width), active=True); completed.append('synthetic-active-' + str(width))
                finally:
                    context.close()
            context = browser.new_context(java_script_enabled=False, viewport={'width':390,'height':844})
            try:
                case(context, DESIGN, 'design-no-js'); completed.append('design-no-js')
            finally:
                context.close()
        finally:
            browser.close()
        edge = pw.chromium.launch(channel='msedge', headless=True)
        try:
            for width in (1440, 390):
                context = edge.new_context(viewport={'width':width,'height':844}, reduced_motion='reduce')
                try:
                    case(context, DESIGN, 'design-edge-' + str(width)); completed.append('design-edge-' + str(width))
                finally:
                    context.close()
        finally:
            edge.close()
        with tempfile.TemporaryDirectory() as profile:
            load_zoom().zoom_profile(pw, Path(profile))
            context = pw.firefox.launch_persistent_context(profile, headless=True, no_viewport=True, reduced_motion='reduce')
            try:
                page, = context.pages
                page.goto(DESIGN + '/kontakt/')
                assert page.evaluate('devicePixelRatio') == 2
                case(context, DESIGN, 'design-native200', page=page); completed.append('design-native200')
            finally:
                context.close()
    result = {'status':'PASS','cases':completed,'external_requests':0,'backend_or_accounts':'NOT_CONTACTED','login':'native future link; current design inert'}
    (EVIDENCE / 'browser.json').write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    run()
