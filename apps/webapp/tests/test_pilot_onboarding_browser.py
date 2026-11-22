"""Opt-in pilot onboarding over loopback HTTPS and disposable local PostgreSQL."""

from email.message import EmailMessage
import os
from urllib.parse import urlsplit
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright
import pyotp
import pytest
from sqlalchemy import text

from competence_hub_api.auth.postgres_token_delivery import (
    PostgresTokenDeliveryOutboxRepository,
)
from competence_hub_api.auth.smtp_token_delivery import SmtpTokenMessageAdapter
from competence_hub_api.auth.token_delivery import TokenDeliveryWorker
from competence_hub_api.runtime import create_database_engine
from scripts.local_calendar_postgres import LocalCalendarPostgres
from scripts.native_calendar_fixture import NativeCalendarFixture
from test_calendar_v12_browser import qa


pytestmark = pytest.mark.skipif(
    os.environ.get("COMPETENCE_HUB_RUN_LOCAL_PILOT_ONBOARDING") != "1",
    reason="requires an owned local PostgreSQL container and Playwright Firefox",
)

PORTAL = "/portal/"
SESSION = "/api/v1/portal/access/session"
INVITATIONS = "/api/v1/admin/users/invitations"
ACCEPT = "/api/v1/auth/invitations/accept"
REVIEW_QUEUE = "/api/v1/portal/calendar/review-queue"


class MemoryMailbox(SmtpTokenMessageAdapter):
    def __init__(self, portal_url: str) -> None:
        super().__init__(
            host="unused.example.invalid",
            port=465,
            tls_mode="implicit",
            username="",
            password="",
            sender="synthetic-sender@example.invalid",
            reply_to="synthetic-reply@example.invalid",
            account_action_base_url=portal_url,
        )
        self.messages: list[EmailMessage] = []

    def _send(self, message: EmailMessage) -> None:
        self.messages.append(message)


def capture_invitation(fixture, cipher, portal_url, recipient):
    mailbox = MemoryMailbox(portal_url)

    async def dispatch(connection):
        now = await connection.scalar(text("SELECT clock_timestamp()"))
        engine = create_database_engine(fixture.app_url)
        try:
            worker = TokenDeliveryWorker(
                PostgresTokenDeliveryOutboxRepository(engine), mailbox, cipher
            )
            assert await worker.run_once(now=now)
            assert not await worker.run_once(now=now)
        finally:
            await engine.dispose()

    fixture.database(dispatch)
    assert len(mailbox.messages) == 1
    message = mailbox.messages[0]
    assert str(message["To"]) == recipient
    body = message.get_body(preferencelist=("plain",))
    assert body is not None
    links = [line for line in body.get_content().splitlines() if line.startswith("https://")]
    assert len(links) == 1
    parsed = urlsplit(links[0])
    assert parsed._replace(fragment="").geturl() == portal_url
    assert parsed.fragment.startswith("/einladung?token=")
    return links[0]


def submit_password_login(page, email, password):
    page.locator("#login-email").fill(email)
    page.locator("#login-password").fill(password)
    page.get_by_role("button", name="Anmelden", exact=True).click()


def browser_status(page, path):
    return page.evaluate("async path => (await fetch(path)).status", path)


def enroll_and_acknowledge_recovery(page, fixture):
    enrollment = page.locator("#enrollment-code")
    expect(enrollment).to_be_focused()
    totp = pyotp.TOTP(page.locator("#provisioning-secret").inner_text())
    issued_at = fixture.now.timestamp()
    enrollment.fill(totp.at(issued_at))
    enrollment.press("Enter")

    expect(page.locator("#recovery-view")).to_be_visible()
    codes = page.locator("#recovery-codes li").all_text_contents()
    assert len(codes) == len(set(codes)) == 10
    enter = page.locator("#enter-portal")
    expect(enter).to_be_disabled()
    page.locator("#recovery-confirmed").check()
    enter.click()
    expect(page.locator("#portal-view")).to_be_visible()
    return totp, issued_at


def test_synthetic_reviewer_onboarding_from_invitation_to_first_review_queue():
    blocked, page_errors = [], []
    email = f"synthetic-pilot-{uuid4().hex}@example.invalid"
    display_name = "Synthetic Pilot Reviewer"
    password = "Pilot-Reviewer-" + uuid4().hex
    db = LocalCalendarPostgres()
    cipher = None

    with db, sync_playwright() as pw:
        fixture = NativeCalendarFixture(local_container_rehearsal=True)
        fixture.prepare()

        def application(port):
            nonlocal cipher
            app = fixture.app(port)
            # Enable queuing only on this owned app; the worker has no SMTP transport.
            app.state.invitation_delivery_enabled = True
            cipher = app.state.outbox_cipher
            return app

        with qa.synthetic_server(application) as base:
            browser = pw.firefox.launch(headless=True)
            try:
                def open_page(width):
                    context = browser.new_context(
                        ignore_https_errors=True,
                        viewport={"width": width, "height": 900},
                        service_workers="block",
                        reduced_motion="reduce",
                    )

                    def only_loopback(route):
                        if route.request.url.startswith(base + "/"):
                            route.continue_()
                        else:
                            blocked.append(True)
                            route.abort()

                    context.set_default_timeout(10_000)
                    context.route("**/*", only_loopback)
                    page = context.new_page()
                    page.on("pageerror", lambda error: page_errors.append(error.name))
                    return page

                admin = open_page(1440)
                admin.goto(base + PORTAL)
                submit_password_login(admin, fixture.emails["admin"], fixture.password)
                enroll_and_acknowledge_recovery(admin, fixture)
                expect(admin.locator("#tour-title")).to_have_text("Administrationsübersicht")
                admin.locator("#tour-skip").press("Enter")
                admin.get_by_role("button", name="Zugänge", exact=True).click()
                admin.locator("#invitation-display-name").fill(display_name)
                admin.locator("#invitation-email").fill(email)
                admin.locator("#invitation-role").select_option("calendar_reviewer")
                admin.locator("#prepare-invitation").click()
                expect(admin.locator("#invitation-preview")).to_contain_text(email)
                with admin.expect_response(base + INVITATIONS) as invitation:
                    admin.locator("#admin-invitation-form [type=submit]").click()
                assert invitation.value.status == 202
                receipt = invitation.value.json()
                assert set(receipt) == {"status", "user_id"}
                assert receipt["status"] == "accepted"
                expect(admin.locator("#status-message")).to_contain_text("kein Zustellnachweis")

                link = capture_invitation(fixture, cipher, base + PORTAL, email)
                reviewer = open_page(390)
                reviewer.goto(link)
                expect(reviewer.locator("#account-token-password")).to_be_focused()
                assert reviewer.url == base + PORTAL
                reviewer.locator("#account-token-password").fill(password)
                reviewer.locator("#account-token-password-confirm").fill(password)
                with reviewer.expect_response(base + ACCEPT) as activation:
                    reviewer.locator("#account-token-submit").click()
                assert activation.value.status == 202
                expect(reviewer.locator("#enrollment-code")).to_be_visible()
                assert browser_status(reviewer, REVIEW_QUEUE) == 401
                totp, enrolled_at = enroll_and_acknowledge_recovery(reviewer, fixture)

                tour_title = reviewer.locator("#tour-title")
                expect(tour_title).to_have_text("Willkommen im Prüfbereich")
                expect(tour_title).to_be_focused()
                with reviewer.expect_response(base + REVIEW_QUEUE) as tour_queue:
                    reviewer.locator("#tour-next").press("Enter")
                assert tour_queue.value.status == 200
                expect(tour_title).to_have_text("Eingereichte Angebote")
                reviewer.locator("#tour-skip").press("Enter")
                expect(reviewer.locator("#pilot-help summary")).to_be_focused()
                expect(reviewer.locator("#review-calendar-empty")).to_be_visible()

                reviewer.locator("#logout-button").click()
                expect(reviewer.locator("#login-view")).to_be_visible()
                assert browser_status(reviewer, SESSION) == 401
                submit_password_login(reviewer, email, password)
                mfa = reviewer.locator("#mfa-code")
                expect(mfa).to_be_focused()
                # The verifier rejects the enrollment counter, allowing one adjacent step.
                mfa.fill(totp.at(max(fixture.now.timestamp(), enrolled_at + totp.interval)))
                # The only authorized workspace is loaded directly after sign-in.
                with (
                    reviewer.expect_response(base + SESSION) as current_session,
                    reviewer.expect_response(base + REVIEW_QUEUE) as queue,
                ):
                    mfa.press("Enter")
                expect(reviewer.locator("#session-user")).to_have_text(display_name)
                expect(reviewer.locator("#product-tour")).to_be_hidden()
                session = current_session.value
                assert session.status == 200
                assert session.json()["user"] == {
                    "id": receipt["user_id"],
                    "display_name": display_name,
                    "roles": ["calendar_reviewer"],
                }
                assert queue.value.status == 200
                assert queue.value.json() == {"items": []}
                expect(reviewer.locator("#review-calendar-empty")).to_be_visible()
                # The admin endpoint does not admit reviewer sessions at all.
                assert browser_status(reviewer, "/api/v1/admin/users") == 401
                assert not blocked and not page_errors
            finally:
                browser.close()

    assert db.removed and db.volume_removed
