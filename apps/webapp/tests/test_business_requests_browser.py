"""Business Ops journeys in the real Portal shell with a synthetic API."""

from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright
import pytest

from test_portal_tour_feedback_browser import company_fixture, context, qa


REQUESTS = "/api/v1/portal/requests"
REQUEST_ID = "10000000-0000-4000-8000-000000000001"
COMPANY_ID = "10000000-0000-4000-8000-000000000002"
STAFF_ID = "10000000-0000-4000-8000-000000000003"
COACH_ID = "10000000-0000-4000-8000-000000000004"
PRIVATE_ID = "10000000-0000-4000-8000-000000000005"
SERVICE_ID = "10000000-0000-4000-8000-000000000006"
OFFER_ID = "10000000-0000-4000-8000-000000000007"
SUBJECT = "DEMO Planung <b>Nord</b>"
DESCRIPTION = "Vertraulicher DEMO Bedarf <b>als Text</b>"
INTERNAL = "DEMO interne Notiz <b>als Text</b>"
RELEASE = "DEMO Freigabetext <b>als Text</b>"
COACH_NOTE = "DEMO freigegebene Notiz"
CAPABILITIES = {"enabled": True, "can_read": True}
OPTIONS = {
    "companies": (COMPANY_ID, "DEMO Firma"), "private_customers": (PRIVATE_ID, "DEMO Privatkunde"),
    "responsible_users": (STAFF_ID, "DEMO Team"), "coaches": (COACH_ID, "DEMO Coach"),
    "services": (SERVICE_ID, "DEMO Leistung"), "offers": (OFFER_ID, "DEMO Angebot"),
}


def sign_in(page, base, email):
    page.goto(base + "/portal/")
    page.locator("#login-email").fill(email)
    page.locator("#login-password").fill(qa.SYNTHETIC_PASSWORD)
    page.locator("#login-password").press("Enter")
    page.locator("#mfa-code").fill(qa.TOTP_CODE)
    page.locator("#mfa-code").press("Enter")
    expect(page.locator("#portal-view")).to_be_visible()


def enter_workspace(page, label="Anfragen"):
    entry = page.get_by_role("navigation", name="Portalbereiche").get_by_role("button", name=label, exact=True)
    expect(entry).to_be_visible()
    if entry.get_attribute("aria-current") != "page":
        entry.press("Enter")
        expect(page.locator("#requests-title")).to_be_focused()
    expect(entry).to_have_attribute("aria-current", "page")
    return page.locator("#requests-workspace")


def open_detail(page, workspace, title=SUBJECT):
    workspace.get_by_role("button", name=f"Details öffnen: {title}").press("Enter")
    expect(workspace.get_by_role("heading", name=title)).to_be_focused()
    assert workspace.locator("b").count() == 0
    if page.viewport_size and page.viewport_size["width"] == 390:
        assert workspace.evaluate("node => node.scrollWidth <= node.clientWidth + 1")


def detail_data():
    return {
        "id": REQUEST_ID, "subject": SUBJECT, "description": DESCRIPTION, "status": "open", "version": 1,
        "company_id": COMPANY_ID, "company_label": "DEMO Firma",
        "responsible_user_id": None, "coach_id": None, "follow_up_on": None,
        "created_at": "2035-01-03T11:00:00Z", "notes": [{"body": INTERNAL, "visibility": "internal"}],
        "audit": [{"action": "created", "changed_fields": ["subject", "description"]}],
    }


def serve_options(route, url):
    key = parse_qs(url.query)["bucket"][0]
    id_, label = OPTIONS[key]
    return route.fulfill(json={"items": [{"id": id_, "label": label}], "next_after": None})


@pytest.mark.parametrize("width", [390, "native200"])
def test_staff_updates_assignment_and_notes_with_stale_edit_recovery(width, tmp_path):
    data = detail_data()
    mutations = []

    def answer(route):
        url = urlsplit(route.request.url)
        path = url.path
        method = route.request.method
        if path.endswith("/capabilities"):
            return route.fulfill(json={**CAPABILITIES, "can_manage": True, "scope": "internal"})
        if path.endswith("/options"):
            return serve_options(route, url)
        if path == REQUESTS and method == "GET":
            return route.fulfill(json={"items": [data], "next_after": None})
        if method == "GET":
            return route.fulfill(json=data)
        mutations.append((path, method, route.request.post_data_json, route.request.headers))
        if len(mutations) == 1:
            data["version"] += 1
            return route.fulfill(status=409, json={"code": "request_version_conflict"})
        body = route.request.post_data_json
        if method == "PATCH":
            data.update(body, responsible_user_label="DEMO Team", coach_label="DEMO Coach")
        else:
            data["notes"].append({"body": body["body"], "visibility": body["visibility"]})
        data["version"] += 1
        return route.fulfill(json=data)

    with qa.synthetic_server() as base, sync_playwright() as pw, context(pw, width, tmp_path) as page:
        page.route(f"**{REQUESTS}**", answer)
        sign_in(page, base, qa.ADMIN_EMAIL)
        workspace = enter_workspace(page)
        if width == "native200":
            assert page.evaluate("devicePixelRatio") == 2
        open_detail(page, workspace)
        expect(workspace.get_by_text(INTERNAL, exact=True)).to_be_visible()
        workspace.get_by_text("Verlauf", exact=True).press("Enter")
        expect(workspace.get_by_text("Anfrage erstellt", exact=True)).to_be_visible()

        def edit():
            workspace.get_by_role("button", name="Bearbeiten", exact=True).press("Enter")
            expect(workspace.get_by_role("heading", name="Anfrage bearbeiten")).to_be_focused()
            workspace.get_by_label("Status", exact=True).select_option("in_progress")
            workspace.get_by_label("Interne Zuständigkeit").select_option(STAFF_ID)
            workspace.get_by_label("Coach", exact=True).select_option(COACH_ID)
            workspace.get_by_label("Wiedervorlage am").fill("2035-01-08")
            workspace.get_by_label("Coach-Freigabetext").fill(RELEASE)
            workspace.get_by_label("Leistung", exact=True).select_option(SERVICE_ID)
            expect(workspace.get_by_label("Unternehmen", exact=True)).to_have_count(0)

        edit()
        page.once("dialog", lambda dialog: dialog.dismiss())
        page.get_by_role("navigation", name="Portalbereiche").get_by_role("button", name="Zugänge").press("Enter")
        expect(workspace.get_by_label("Wiedervorlage am")).to_have_value("2035-01-08")
        workspace.get_by_label("Kalenderangebot", exact=True).select_option(OFFER_ID)
        workspace.get_by_role("button", name="Änderungen speichern").press("Enter")
        expect(workspace.get_by_role("alert")).to_contain_text("entweder eine Leistung oder ein Kalenderangebot")
        assert not mutations
        workspace.get_by_label("Kalenderangebot", exact=True).select_option("")
        workspace.get_by_role("button", name="Änderungen speichern").press("Enter")
        expect(workspace.get_by_role("alert")).to_contain_text("Datenstand")
        expect(workspace.get_by_label("Wiedervorlage am")).to_have_value("2035-01-08")
        expect(workspace.get_by_role("button", name="Änderungen speichern")).to_be_disabled()
        page.once("dialog", lambda dialog: dialog.accept())
        workspace.get_by_role("button", name="Aktuellen Stand laden").press("Enter")
        edit()
        workspace.get_by_role("button", name="Änderungen speichern").press("Enter")
        expect(workspace.get_by_text("DEMO Team", exact=True)).to_be_visible()
        expect(workspace.get_by_text(RELEASE, exact=True)).to_be_visible()
        workspace.get_by_role("button", name="Notiz hinzufügen").press("Enter")
        expect(workspace.get_by_label("Sichtbarkeit")).to_have_value("internal")
        workspace.get_by_label("Notiz", exact=True).fill("DEMO gespeichert")
        workspace.get_by_role("button", name="Notiz speichern").press("Enter")
        expect(workspace.get_by_text("DEMO gespeichert", exact=True)).to_be_visible()
        workspace.get_by_role("button", name="Notiz hinzufügen").press("Enter")
        workspace.get_by_label("Sichtbarkeit").select_option("coach")
        workspace.get_by_label("Notiz", exact=True).fill(COACH_NOTE)
        workspace.get_by_role("button", name="Notiz speichern").press("Enter")
        expect(workspace.get_by_text(COACH_NOTE, exact=True)).to_be_visible()
        assert [entry[1] for entry in mutations] == ["PATCH", "PATCH", "POST", "POST"]
        assert mutations[1][2] == {
            "version": 2, "status": "in_progress", "responsible_user_id": STAFF_ID,
            "coach_id": COACH_ID, "follow_up_on": "2035-01-08", "coach_summary": RELEASE, "service_id": SERVICE_ID,
        }
        assert mutations[2][2] == {"version": 3, "visibility": "internal", "body": "DEMO gespeichert"}
        assert mutations[3][2] == {"version": 4, "visibility": "coach", "body": COACH_NOTE}
        assert all(headers.get("x-csrf-token") for _, _, _, headers in mutations)


def test_staff_creates_company_and_private_requests(tmp_path):
    items = []
    creates = []

    def answer(route):
        url = urlsplit(route.request.url)
        path = url.path
        if path.endswith("/capabilities"):
            return route.fulfill(json={**CAPABILITIES, "can_manage": True, "scope": "internal"})
        if path.endswith("/options"):
            return serve_options(route, url)
        if route.request.method == "POST" and path == REQUESTS:
            creates.append(route.request.post_data_json)
            data = {**detail_data(), **creates[-1], "id": REQUEST_ID if not items else PRIVATE_ID}
            items.append(data)
            return route.fulfill(status=201, json=data)
        if path == REQUESTS:
            return route.fulfill(json={"items": items, "next_after": None})
        return route.fulfill(json=next(item for item in items if path.endswith(item["id"])))

    with qa.synthetic_server() as base, sync_playwright() as pw, context(pw, 390, tmp_path) as page:
        page.route(f"**{REQUESTS}**", answer)
        sign_in(page, base, qa.REVIEWER_EMAIL)
        workspace = enter_workspace(page)
        expect(workspace.get_by_text("Keine Anfragen vorhanden.")).to_be_visible()
        for title, customer, id_ in [(SUBJECT, "Unternehmen", COMPANY_ID), ("DEMO Privatanfrage", "Privatkunde", PRIVATE_ID)]:
            workspace.get_by_role("button", name="Anfrage erstellen").press("Enter")
            workspace.get_by_label("Betreff").fill(title)
            workspace.get_by_label("Beschreibung").fill(DESCRIPTION)
            if customer == "Unternehmen":
                workspace.get_by_role("button", name="Anfrage speichern").press("Enter")
                expect(workspace.get_by_role("alert")).to_contain_text("entweder ein Unternehmen oder einen Privatkunden")
                assert not creates
            workspace.get_by_label(customer, exact=True).select_option(id_)
            workspace.get_by_role("button", name="Anfrage speichern").press("Enter")
            expect(workspace.get_by_role("heading", name=title)).to_be_focused()
            expect(workspace.get_by_text(DESCRIPTION, exact=True)).to_be_visible()
            workspace.get_by_role("button", name="Zur Übersicht").press("Enter")
            expect(workspace.get_by_role("button", name=f"Details öffnen: {title}")).to_be_focused()
        assert [(item["company_id"], item["private_customer_id"]) for item in creates] == [
            (COMPANY_ID, None), (None, PRIVATE_ID),
        ]


@pytest.mark.parametrize("scope", ["company", "coach"])
def test_read_only_projections_do_not_expose_staff_fields(scope, tmp_path):
    factory = company_fixture if scope == "company" else qa.create_acceptance_app
    email = qa.COMPANY_CONTACT_EMAIL if scope == "company" else qa.COACH_EMAIL
    seen = []
    with qa.synthetic_server(factory) as base, sync_playwright() as pw, context(pw, 390, tmp_path) as page:
        enabled = True

        def answer(route):
            url = urlsplit(route.request.url)
            path = url.path
            seen.append((route.request.method, path, parse_qs(url.query)))
            if path.endswith("/capabilities"):
                return route.fulfill(json={**CAPABILITIES, "enabled": enabled, "can_manage": False, "scope": scope})
            data = detail_data()
            if scope == "coach":
                data.update(coach_summary=RELEASE, notes=[{"body": INTERNAL, "visibility": "internal"}, {"body": COACH_NOTE}])
            if path == REQUESTS:
                return route.fulfill(json={"items": [data], "next_after": None})
            return route.fulfill(json=data)

        page.route(f"**{REQUESTS}**", answer)
        sign_in(page, base, email)
        workspace = enter_workspace(page)
        expect(workspace.get_by_role("button", name="Anfrage erstellen")).to_have_count(0)
        if scope == "coach":
            expect(workspace.get_by_text("Freigegebene Anfragen")).to_be_visible()
            expect(workspace.get_by_label("Status filtern")).to_have_count(0)
            open_detail(page, workspace, "Freigegebene Anfrage")
            expect(workspace.get_by_text(SUBJECT, exact=True)).to_have_count(0)
            expect(workspace.get_by_text("Offen", exact=True)).to_have_count(0)
            expect(workspace.get_by_text(RELEASE, exact=True)).to_be_visible()
            expect(workspace.get_by_text(COACH_NOTE, exact=True)).to_be_visible()
        else:
            expect(workspace.get_by_text("Anfragen Ihres Unternehmens")).to_be_visible()
            workspace.get_by_label("Status filtern").select_option("open")
            workspace.get_by_role("button", name="Filtern").press("Enter")
            open_detail(page, workspace)
            expect(workspace.get_by_text("Offen", exact=True)).to_be_visible()
        expect(workspace.get_by_text(DESCRIPTION, exact=True)).to_have_count(0)
        expect(workspace.get_by_text(INTERNAL, exact=True)).to_have_count(0)
        expect(workspace.get_by_text("Verlauf", exact=True)).to_have_count(0)
        expect(workspace.get_by_role("button", name="Bearbeiten")).to_have_count(0)
        expect(workspace.get_by_role("button", name="Notiz hinzufügen")).to_have_count(0)
        assert all(method == "GET" and not path.endswith("/options") for method, path, _ in seen)
        if scope == "company":
            assert ("GET", REQUESTS, {"status": ["open"]}) in seen
        else:
            assert not any(query for _, _, query in seen)

        enabled = False
        page.reload()
        expect(page.locator("#coach-calendar-workspace" if scope == "coach" else "#portal-empty")).to_be_visible()
        expect(page.locator('[data-portal-area="requests"]')).to_have_count(0)
        expect(workspace).to_be_hidden()
