"""Actual source form/stylesheet in Firefox; no server or private credentials."""
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright, expect
import pytest

ASSETS=Path(__file__).parents[1]/'src/competence_hub_api/portal_ui'


@pytest.mark.parametrize('width',[1440,390])
def test_field_error_keeps_visual_marking_on_focus_and_explains_optional_summary(width):
    with sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            page=browser.new_page(viewport={'width':width,'height':900},locale='en-US')
            def asset(route):
                name=urlsplit(route.request.url).path.removeprefix('/portal/') or 'index.html'
                if name not in ('index.html','styles.css','product-tour.css','calendar-form.mjs'):
                    route.abort();return
                raw=(ASSETS/name).read_text(encoding='utf8')
                if name=='index.html':
                    raw=raw.replace('<script type="module" src="/portal/app.js"></script>',
                        '<script type="module">import {createCalendarForm} from "./calendar-form.mjs";window.formFixture=createCalendarForm(document.querySelector("#calendar-offer-form"));</script>')
                route.fulfill(status=200,body=raw,content_type='text/javascript' if name.endswith('.mjs') else 'text/css' if name.endswith('.css') else 'text/html')
            page.route('**/*',asset);page.goto('https://calendar-ui.example.invalid/portal/')
            page.wait_for_function('Boolean(window.formFixture)')
            page.evaluate('''()=>{document.querySelector('#calendar-offer-dialog').showModal();
              formFixture.show([{field:'review_threshold',code:'threshold'},{field:'title',code:'required_text'}]);}''')
            title=page.locator('#calendar-title');expect(title).to_be_focused()
            assert title.evaluate('e=>getComputedStyle(e).borderTopColor')=='rgb(159, 34, 25)'
            assert 'calendar-title-error' in title.get_attribute('aria-describedby')
            expect(page.locator('#calendar-title-error')).to_contain_text('160')
            expect(page.locator('label[for="calendar-summary"]')).to_contain_text('optional')
            assert page.locator('#calendar-summary').get_attribute('required') is None
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.evaluate('formFixture.clear()');assert title.get_attribute('aria-invalid') is None
        finally:browser.close()
