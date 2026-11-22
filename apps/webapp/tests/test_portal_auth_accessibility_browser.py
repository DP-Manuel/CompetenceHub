"""Keyboard, focus and accessible descriptions for synthetic Portal sign-in."""

from playwright.sync_api import expect, sync_playwright

from test_portal_tour_feedback_browser import context, qa


def test_sign_in_errors_method_switch_and_logout_focus(tmp_path):
    with qa.synthetic_server() as base, sync_playwright() as pw, context(pw, 390, tmp_path) as page:
        page.goto(base + "/portal/")
        page.locator("#login-error, #mfa-error").evaluate_all("""alerts => {
          for (const alert of alerts) {
            alert.addEventListener("focus", () => {
              alert.dataset.formBusyOnFocus = alert.closest("form").getAttribute("aria-busy");
            });
          }
        }""")
        email = page.get_by_role("textbox", name="Arbeits-E-Mail")
        password = page.get_by_label("Passwort", exact=True)
        expect(email).to_be_focused()
        email.fill(qa.REVIEWER_EMAIL)
        password.fill("falsches synthetisches Passwort")
        password.press("Enter")
        login_error = page.get_by_role("alert")
        expect(login_error).to_be_focused()
        expect(login_error).to_have_attribute("data-form-busy-on-focus", "false")
        expect(login_error).not_to_be_empty()
        page.keyboard.press("Tab")
        expect(page.get_by_role("button", name="Anmelden", exact=True)).to_be_focused()

        password.fill(qa.SYNTHETIC_PASSWORD)
        password.press("Enter")
        code = page.get_by_role("textbox", name="Sechsstelliger Code")
        expect(code).to_be_focused()
        page.keyboard.press("Shift+Tab")
        totp = page.get_by_role("radio", name="Authenticator")
        expect(totp).to_be_focused()
        page.keyboard.press("ArrowRight")
        recovery = page.get_by_role("radio", name="Recovery-Code")
        expect(recovery).to_be_focused()
        expect(recovery).to_be_checked()
        expect(page.get_by_role("textbox", name="Recovery-Code")).to_be_visible()
        page.keyboard.press("ArrowLeft")
        expect(totp).to_be_focused()
        expect(totp).to_be_checked()
        page.keyboard.press("Tab")
        expect(code).to_be_focused()
        code.fill("000000")
        code.press("Enter")
        mfa_error = page.get_by_role("alert")
        expect(mfa_error).to_be_focused()
        expect(mfa_error).to_have_attribute("data-form-busy-on-focus", "false")
        expect(mfa_error).not_to_be_empty()
        page.keyboard.press("Tab")
        expect(page.get_by_role("button", name="Bestätigen", exact=True)).to_be_focused()

        code.fill(qa.TOTP_CODE)
        code.press("Enter")
        expect(page.locator("#portal-title")).to_be_focused()
        page.get_by_role("button", name="Abmelden", exact=True).press("Enter")
        expect(email).to_be_focused()
        expect(email).to_have_accessible_description("Sie wurden abgemeldet.")
