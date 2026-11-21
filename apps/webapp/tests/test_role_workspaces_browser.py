"""Focused Portal workspace checks against an isolated synthetic browser fixture."""
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import expect, sync_playwright

from test_portal_tour_feedback_browser import company_fixture, context, qa, sign_in


RESERVATIONS = "/api/v1/portal/reservations"
OFFER_ID = "10000000-0000-4000-8000-000000000001"
RESERVATION_ID = "10000000-0000-4000-8000-000000000002"
DATE = "2035-01-03T11:00:00Z"


@pytest.mark.parametrize("width", [390, "native200"])
def test_reviewer_shortcuts_filter_queue_and_refresh_is_recoverable(width, tmp_path):
    title = "DEMO Frist & Pr\u00fcfung"
    snapshot = {"calendar": {}, "business": {"review": {
        "counts": {"calendar_in_review": 1, "pending": 2, "reply_ready": 1, "overdue": 1},
        "tasks": [{"kind": "reservation_review", "title": title, "decision_deadline": DATE,
                   "capacity": 5, "occupied_seats": 3, "overdue": True},
                  {"kind": "calendar_review", "title": "DEMO Pr\u00fcfen", "submitted_at": DATE}],
    }}}
    failure = False
    queries = []

    def overview(route):
        route.fulfill(status=503 if failure else 200, json=snapshot)

    def reservations(route):
        url = urlsplit(route.request.url)
        if url.path.endswith("/capabilities"):
            route.fulfill(json={"can_review": True})
        else:
            queries.append(parse_qs(url.query))
            route.fulfill(json={"items": []})

    with qa.synthetic_server() as base, sync_playwright() as pw, context(pw, width, tmp_path) as page:
        page.route("**/api/v1/portal/pilot/overview", overview)
        page.route(f"**{RESERVATIONS}**", reservations)
        sign_in(page, base, qa.REVIEWER_EMAIL)
        board = page.locator('[data-business-section="review"]')
        expect(board).to_be_visible()
        if width == "native200":
            assert page.evaluate("devicePixelRatio") == 2
        assert board.evaluate("node => node.scrollWidth <= node.clientWidth + 1")
        board.get_by_role("button", name=f"Vorg\u00e4nge zum Titel suchen: {title}").press("Enter")
        expect(page.locator("#reservations-title")).to_be_focused()
        expect(page.locator("#cal2-filter-offer")).to_have_value(title)
        expect(page.locator("#cal2-filter-deadline")).to_have_value("overdue")
        expect(page.get_by_text("Keine Vorg\u00e4nge f\u00fcr diese Auswahl.")).to_be_visible()
        assert queries[-1] == {"review": ["true"], "status": ["open"], "offer": [title], "deadline": ["overdue"]}
        board.get_by_role("button", name="Vormerkungen zur Entscheidung: 3").press("Enter")
        expect(page.locator("#cal2-filter-offer")).to_have_value("")
        expect(page.get_by_text("Keine Vorg\u00e4nge f\u00fcr diese Auswahl.")).to_be_visible()
        assert queries[-1] == {"review": ["true"], "status": ["decision"]}

        failure = True
        refresh = page.locator("#refresh-pilot-overview")
        refresh.press("Enter")
        expect(page.locator("#pilot-overview-state")).to_contain_text("momentan nicht verf\u00fcgbar")
        expect(board).to_be_hidden()
        expect(refresh).to_be_focused()
        expect(page.locator("#reservations-workspace")).to_be_visible()
        failure = False
        refresh.press("Enter")
        expect(board).to_be_visible()
        expect(refresh).to_be_focused()


def test_firm_website_selection_and_read_only_drafts_stay_in_company_scope(tmp_path):
    draft_queries = []

    def reservations(route):
        url = urlsplit(route.request.url)
        if url.path.endswith("/capabilities"):
            route.fulfill(json={"can_request": True, "company": {"name": "DEMO Firma"}})
        elif url.path.endswith("/communication-drafts"):
            draft_queries.append((route.request.method, parse_qs(url.query)))
            route.fulfill(json={"delivery_enabled": False, "items": [{
                "reservation_id": RESERVATION_ID, "kind": "clarification_requested", "occurred_at": DATE,
            }]})
        elif url.path.endswith(RESERVATION_ID):
            assert parse_qs(url.query) == {"review": ["false"]}
            route.fulfill(json={"title": "DEMO Firmenvorgang", "status": "approved", "history": [],
                                "starts_at": DATE, "ends_at": DATE, "decision_deadline": DATE})
        else:
            route.fulfill(json={"items": []})

    with qa.synthetic_server(company_fixture) as base, sync_playwright() as pw, context(pw, 390, tmp_path) as page:
        page.route(f"**{RESERVATIONS}**", reservations)
        page.route("**/api/v1/portal/pilot/overview", lambda route: route.fulfill(json={
            "calendar": {}, "business": {"company": {"counts": {}, "tasks": []}},
        }))
        page.goto(f"{base}/portal/?offer={OFFER_ID}")
        page.locator("#login-email").fill(qa.COMPANY_CONTACT_EMAIL)
        page.locator("#login-password").fill(qa.SYNTHETIC_PASSWORD)
        page.locator("#login-password").press("Enter")
        page.locator("#mfa-code").fill(qa.TOTP_CODE)
        page.locator("#mfa-code").press("Enter")
        expect(page.locator("#reservation-catalogue h3")).to_have_text("Ausgew\u00e4hlte Veranstaltung")
        assert page.locator("#reservation-catalogue").evaluate(
            "node => node.nextElementSibling.id === 'reservation-own'"
        )
        page.get_by_role("button", name="Veranstaltungen finden").press("Enter")
        expect(page.locator("#cal2-search")).to_be_focused()
        assert not draft_queries
        page.get_by_text("Kommunikationsentw\u00fcrfe", exact=True).press("Enter")
        expect(page.get_by_text("Nur Entw\u00fcrfe. Es wird nichts versendet.")).to_be_visible()
        page.get_by_role("button", name="Zum Vorgang: R\u00fcckfrage gestellt", exact=False).press("Enter")
        expect(page.get_by_role("heading", name="DEMO Firmenvorgang")).to_be_visible()
        assert draft_queries == [("GET", {"review": ["false"]})]
