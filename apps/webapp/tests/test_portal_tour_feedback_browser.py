"""Feedback 19.11: four-role tour in Firefox with synthetic data only."""
from contextlib import contextmanager
from unittest.mock import patch

from playwright.sync_api import expect, sync_playwright
import pytest

from test_calendar_v12_browser import EVIDENCE, qa
from vps_pilot_acceptance import zoom_profile
import browser_acceptance_app as synthetic
from competence_hub_api.auth.admission import AdmissionPolicy


EVIDENCE = EVIDENCE.parent / "portal-feedback-20261120"
ROLES = {
    "Admin": (qa.ADMIN_EMAIL, 6),
    "Coach": (qa.COACH_EMAIL, 9),
    "Prüfer": (qa.REVIEWER_EMAIL, 7),
    "Unternehmens": (qa.COMPANY_CONTACT_EMAIL, 6),
}


def mock_company_capabilities(page):
    def answer(route):
        path = route.request.url.split("?")[0]
        if path.endswith("/capabilities"):
            route.fulfill(json={"can_request": True, "company": {"name": "Demo-Firma"}})
        else:
            route.fulfill(json={"items": [], "next_after": None})
    page.route("**/api/v1/portal/reservations**", answer)


def company_fixture(port):
    """Match the local-pilot admission opt-in, within the memory fixture only."""
    policy = AdmissionPolicy(synthetic.PORTAL_ADMISSION.roles | {"company_contact"})
    with patch.object(synthetic, "PORTAL_ADMISSION", policy):
        return synthetic.create_acceptance_app(port)


@contextmanager
def context(pw, width, tmp_path):
    options = {"ignore_https_errors": True, "reduced_motion": "reduce"}
    if width == "native200":
        zoom_profile(pw, tmp_path)
        browser = pw.firefox.launch_persistent_context(tmp_path, headless=True, no_viewport=True, **options)
        try:
            yield browser.pages[0]
        finally:
            browser.close()
    else:
        browser = pw.firefox.launch(headless=True)
        try:
            yield browser.new_page(viewport={"width": width, "height": 844}, has_touch=width == 390, **options)
        finally:
            browser.close()


def start(page, role):
    help_summary = page.locator("#pilot-help summary")
    help_summary.press("Enter")
    page.get_by_role("button", name=f"{role}-Einführung starten").press("Enter")


def sign_in(page, base, email):
    page.goto(base + "/portal/")
    page.locator("#login-email").fill(email)
    page.locator("#login-password").fill(qa.SYNTHETIC_PASSWORD)
    page.locator("#login-password").press("Enter")
    page.locator("#mfa-code").fill(qa.TOTP_CODE)
    page.locator("#mfa-code").press("Enter")
    expect(page.locator("#portal-view")).to_be_visible()
    expect(page.locator("#pilot-overview-title")).to_be_visible()


def visible_step(page, step, total):
    tour = page.get_by_role("dialog")
    expect(tour.locator("#tour-progress")).to_have_text(f"Schritt {step} von {total}", timeout=1800)
    heading = tour.locator("#tour-title")
    expect(heading).to_be_focused()
    copy = tour.locator("#tour-copy").inner_text()
    expect(tour).to_have_accessible_name(heading.inner_text())
    expect(heading).to_have_accessible_description(f"Schritt {step} von {total} {copy}")
    assert tour.evaluate("""node => {
        const box = node.getBoundingClientRect();
        return box.left >= 0 && box.top >= 0 && box.right <= innerWidth + 1
            && box.bottom <= innerHeight + 1 && node.scrollWidth <= node.clientWidth + 1;
    }""")
    geometry = page.evaluate("""() => {
        const target = document.querySelector('.tour-target');
        const panel = document.querySelector('#product-tour');
        if (!target || !target.getClientRects().length) return {ok: false, target: target?.id};
        const a = target.getBoundingClientRect(), b = panel.getBoundingClientRect();
        return {ok: a.bottom > 0 && a.top < innerHeight &&
            (b.right <= a.left || a.right <= b.left || b.bottom <= a.top || a.bottom <= b.top),
            target: target.id || target.tagName, target_box: a.toJSON(), panel_box: b.toJSON(),
            viewport: [innerWidth, innerHeight]};
    }""")
    assert geometry["ok"], (step, geometry)


@pytest.mark.parametrize("width", [1440, 390, "native200"])
@pytest.mark.parametrize("role", ROLES)
def test_all_tour_steps_interactive_and_keyboard_safe(width, role, tmp_path):
    email, total = ROLES[role]
    application = company_fixture if role == "Unternehmens" else synthetic.create_acceptance_app
    with qa.synthetic_server(application) as base, sync_playwright() as pw, context(pw, width, tmp_path) as page:
        errors = []
        page.on("pageerror", lambda error: errors.append(error.name))
        if role == "Unternehmens":
            mock_company_capabilities(page)
        sign_in(page, base, email)
        expect(page.get_by_role("button", name=f"{role}-Einführung starten")).to_have_count(0)
        start(page, role)
        if width == "native200":
            assert page.evaluate("devicePixelRatio") == 2
        for step in range(1, total + 1):
            visible_step(page, step, total)
            if step == 2:
                page.locator("#tour-back").press("Enter")
                visible_step(page, 1, total)
                page.locator("#tour-next").press("Enter")
                visible_step(page, 2, total)
                EVIDENCE.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(EVIDENCE / f"tour-{list(ROLES).index(role)}-{width}.png"))
            page.keyboard.press("Tab")
            assert page.locator("#product-tour").evaluate("e => e.contains(document.activeElement)")
            next_step = page.locator("#tour-next")
            if step == 1 and width == 390:
                next_step.tap()
            elif step == 1 and width == 1440:
                next_step.click()
            else:
                next_step.press("Enter")
        expect(page.locator("#product-tour")).to_be_hidden()
        expect(page.locator("#pilot-help summary")).to_be_focused()
        assert page.locator(".tour-target").count() == 0
        start(page, role)
        visible_step(page, 1, total)
        page.keyboard.press("Escape")
        expect(page.locator("#pilot-help summary")).to_be_focused()
        assert not errors


def test_active_tour_resumes_at_precise_step_but_skip_survives_reload(tmp_path):
    with qa.synthetic_server() as base, sync_playwright() as pw, context(pw, 390, tmp_path) as page:
        sign_in(page, base, qa.COACH_EMAIL)
        start(page, "Coach")
        page.locator("#tour-next").press("Enter")
        visible_step(page, 2, 9)
        page.reload()
        visible_step(page, 2, 9)
        page.locator("#tour-skip").press("Enter")
        page.reload()
        expect(page.locator("#pilot-overview-title")).to_be_visible()
        expect(page.locator("#product-tour")).to_be_hidden()
        start(page, "Coach")
        visible_step(page, 1, 9)
        page.keyboard.press("Escape")
        expect(page.locator("#pilot-help summary")).to_be_focused()


@pytest.mark.parametrize(("role", "route_suffix", "fallback"), [
    ("Admin", "/api/v1/admin/users?*", "#pilot-accounts-title"),
    ("Coach", "/api/v1/portal/calendar/offers", "#calendar-offer-search"),
    ("Prüfer", "/api/v1/portal/calendar/review-queue", "#review-calendar-title"),
])
def test_tour_advances_before_requests_finish_and_handles_replaced_targets(role, route_suffix, fallback, tmp_path):
    email, total = ROLES[role]
    with qa.synthetic_server() as base, sync_playwright() as pw, context(pw, 390, tmp_path) as page:
        sign_in(page, base, email)
        pending = []
        if role == "Prüfer":
            expect(page.locator("#review-calendar-loading")).to_be_hidden()
            page.locator("#review-calendar-list").evaluate("element => element.replaceChildren()")
        page.route("**" + route_suffix, lambda route: pending.append(route))
        start(page, role)
        visible_step(page, 1, total)
        with page.expect_request("**" + route_suffix):
            page.locator("#tour-next").press("Enter")
        visible_step(page, 2, total)
        expect(page.locator(f"{fallback}.tour-target")).to_be_visible()
        page.locator("#tour-next").press("Enter")
        visible_step(page, 3, total)
        assert pending
        if role == "Prüfer":
            expect(page.locator("#review-calendar-title.tour-target")).to_be_visible()
            pending.pop().continue_()
            expect(page.locator("#review-calendar-list button.tour-target")).to_be_visible()
            visible_step(page, 3, total)
            expect(page.locator("#tour-title")).to_be_focused()
        else:
            pending.pop().fulfill(status=503, json={"code": "test_unavailable"})
        page.locator("#tour-skip").press("Enter")
        expect(page.locator("#pilot-help summary")).to_be_focused()
        assert page.locator(".tour-target").count() == 0
