"""Exercise 0012 and its UI in the owned, synthetic PostgreSQL fixture only."""
import secrets
from uuid import uuid4

from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient
from playwright.sync_api import expect, sync_playwright
from sqlalchemy import text

from cal1_pilot_acceptance import qa
from local_calendar_postgres import LocalCalendarPostgres, ROOT
from native_calendar_fixture import NativeCalendarFixture
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token

BASE = "/api/v1/portal/customers"
ORIGIN = "https://127.0.0.1:9443"
COMPANY = uuid4()
COMPANY_PATH = f"{BASE}/companies/{COMPANY}/details"
ADDRESS = {"street": "Demo-Straße 1", "postal_code": "00000", "city": "Demo-Ort", "country": "Demo-Land"}
ACTORS = ("admin", "internal", "coach", "reviewer", "contact")


def check(label, condition):
    if not condition:
        raise AssertionError(label)
    print(f"PASS | {label}", flush=True)


def apply_migration(db, number):
    migration, = (ROOT / "database/migrations").glob(f"{number:04d}_*.sql")
    db.sql(migration.read_text(encoding="utf8"))


def exercise_api(fixture, sessions, csrf):
    headers = {"Origin": ORIGIN, "X-CSRF-Token": csrf}
    names = {"first_name": "Demo", "last_name": "Privatkunde"}
    with TestClient(fixture.app(9443, local_reservations=True), base_url=ORIGIN) as http:
        def as_actor(method, route, actor="internal", **options):
            return http.request(method, route, headers={**headers, "Cookie":
                                f"{SESSION_COOKIE_NAME}={sessions[actor]}"}, **options)

        check("0012 enables the administration only in the owned V2 runtime",
              as_actor("GET", BASE + "/capabilities").json() == {"enabled": True})
        check("Anonymous customer access denied", http.get(COMPANY_PATH).status_code == 401)
        for role in ("coach", "reviewer", "contact"):
            for method, route in (("GET", COMPANY_PATH), ("POST", BASE + "/private/search"),
                                  ("PUT", COMPANY_PATH), ("POST", BASE + "/private")):
                check(f"{role}: {method} customer action denied",
                      as_actor(method, route, role).status_code in (401, 403))
        created = as_actor("POST", BASE + "/private", json=names)
        created_record = created.json()
        check("Private record needs no company, address, email or telephone",
              created.status_code == 201 and created_record.get("billing_address") is None
              and not set(created_record).intersection({"company_id", "portal_user_id", "vat_id"}))
        record_path = BASE + "/private/" + created_record["id"]
        patch = {**names, "email": "customer-demo@example.invalid", "billing_address": ADDRESS, "version": 1}
        edited = as_actor("PUT", record_path, "admin", json=patch)
        check("Admin edits a private record; Internal sees the same protected result",
              edited.status_code == 200 and edited.json()["billing_address"] == ADDRESS
              and as_actor("GET", record_path).json() == edited.json())
        check("Concurrent old private version rejected", as_actor("PUT", record_path, json=names | {"version": 1}).status_code == 409)
        check("Private summary searches either name order without exposing contact data",
              as_actor("POST", BASE + "/private/search", json={"name": "privatkunde demo"}).json() == {
                  "items": [names | {"id": created_record["id"]}], "next_after": None,
              } and as_actor("POST", BASE + "/private/search", json={"name": "%"}).json()["items"] == [])
        check("Customer details are not available for an unknown company",
              as_actor("GET", f"{BASE}/companies/{uuid4()}/details").status_code == 404)
        check("Existing company does not need a backfill", as_actor("GET", COMPANY_PATH).json() == {
            "company_id": str(COMPANY), "vat_id": None, "address": None, "version": 0,
        })
        company_data = {"vat_id": "DE123456789", "address": ADDRESS | {"purpose": "billing"}, "version": 0}
        stored = as_actor("PUT", COMPANY_PATH, "admin", json=company_data)
        check("B2B extras use original UUID and an explicit address purpose",
              stored.status_code == 200 and stored.json()["company_id"] == str(COMPANY)
              and stored.json()["address"] == company_data["address"])
        check("Concurrent initial company update rejected",
              as_actor("PUT", COMPANY_PATH, json=company_data).status_code == 409)
        cleared = as_actor("PUT", COMPANY_PATH, json={"version": 1})
        check("Optional B2B data can be cleared; audit uses no customer values",
              cleared.status_code == 200 and cleared.json()["address"] is None and cleared.json()["vat_id"] is None)


def exercise_browser(fixture, session, csrf):
    def application(port):
        app = fixture.app(port, local_reservations=True)

        @app.get("/customer-module-test")
        def harness():
            return HTMLResponse(
                '<!doctype html><html lang="de"><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                '<link rel="stylesheet" href="/portal/styles.css"><title>Lokaler Kundentest</title>'
                '<main><button id="create" type="button">Kunde anlegen</button>'
                '<div id="customers"></div><section id="companies"><div id="company-details"></div></section></main>'
            )
        return app

    with qa.synthetic_server(application) as base, sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        try:
            context = browser.new_context(viewport={"width": 390, "height": 860},
                                          ignore_https_errors=True, reduced_motion="reduce")
            context.add_cookies([{"name": SESSION_COOKIE_NAME, "value": session, "url": base, "secure": True,
                                  "httpOnly": True, "sameSite": "Strict"}])
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(error.name))
            page.goto(base + "/customer-module-test")
            assert page.evaluate("""async ({ csrf, company }) => {
                const { createCustomerAdministration } = await import('/portal/customer-administration.js');
                const byId = id => document.getElementById(id);
                const customers = createCustomerAdministration({
                    hasCsrf: () => true, expired: () => { throw new Error('Test session expired'); },
                    request: (path, options = {}) => fetch(path, {
                        method: options.method || 'GET',
                        headers: options.csrf ? { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf } : {},
                        body: options.body ? JSON.stringify(options.body) : undefined,
                    })
                });
                byId('create').addEventListener('click', event => customers.openPrivateCreate(event.target));
                const mounted = await customers.mount(byId('customers'), {
                    setBusinessVisible: visible => { byId('companies').hidden = !visible; }
                });
                customers.selectCompany(byId('company-details'), company);
                return mounted;
            }""", {"csrf": csrf, "company": str(COMPANY)})

            page.get_by_role("button", name="Privatkunden", exact=True).press("Enter")
            page.get_by_role("button", name="Kunde anlegen").press("Enter")
            form = page.get_by_role("form", name="Privatkunde anlegen")
            expect(form.get_by_label("Vorname")).to_be_focused()
            expect(form.get_by_label("Firmenname")).to_have_count(0)
            form.get_by_label("Vorname").fill("Demo")
            form.get_by_label("Nachname").fill("Browserzustand")
            form.get_by_text("Rechnungsanschrift (optional)", exact=True).press("Enter")
            form.get_by_label("Straße und Hausnummer").fill("Nur Teiladresse")
            form.get_by_role("button", name="Speichern").press("Enter")
            expect(form.get_by_role("alert")).to_contain_text("vollständig")
            expect(form.get_by_label("Postleitzahl")).to_be_focused()
            form.get_by_label("Straße und Hausnummer").fill("")
            form.get_by_role("button", name="Speichern").press("Enter")
            expect(page.get_by_role("status")).to_have_text("Privatkunde gespeichert.")
            row = page.get_by_role("button", name="Demo Browserzustand")
            expect(row).to_be_focused()
            row.press("Enter")
            edit = page.get_by_role("form", name="Privatkunde bearbeiten")
            edit.get_by_label("Nachname").fill("Verworfen")
            page.once("dialog", lambda dialog: dialog.dismiss())
            edit.get_by_role("button", name="Abbrechen").press("Enter")
            expect(edit).to_be_visible()
            page.once("dialog", lambda dialog: dialog.accept())
            edit.get_by_role("button", name="Abbrechen").press("Enter")
            expect(row).to_be_focused()
            page.get_by_role("button", name="Geschäftskunden").press("Enter")
            page.get_by_text("Anschrift und USt-IdNr.", exact=True).press("Enter")
            business = page.get_by_role("form", name="Anschrift und USt-IdNr.")
            business.get_by_label("Umsatzsteuer-ID").fill("DE123456789")
            business.get_by_role("button", name="Speichern").press("Enter")
            expect(page.locator("#company-details").get_by_role("status")).to_have_text("Gespeichert.")
            check("Firefox: 390px keyboard flow, optional address validation, discard, focus, B2B save",
                  not errors and page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
        finally:
            browser.close()


def run(db):
    fixture = NativeCalendarFixture(local_container_rehearsal=True)
    fixture.prepare()
    for number in range(7, 12):
        apply_migration(db, number)
    sessions = {key: secrets.token_urlsafe(32) for key in ACTORS}
    csrf = secrets.token_urlsafe(32)

    async def seed(connection):
        await connection.execute(text("""
            INSERT INTO competence_hub.companies (id, name, status) VALUES (:company, 'Demo-Unternehmen', 'prospect')
        """), {"company": COMPANY})
        await connection.execute(text("""
            INSERT INTO competence_hub.company_contacts (company_id, portal_user_id, first_name, last_name, email)
            VALUES (:company, :actor, 'Demo', 'Firmenkontakt', 'b2b@example.invalid')
        """), {"company": COMPANY, "actor": fixture.users["contact"]})
        for key, token in sessions.items():
            await connection.execute(text("""
                INSERT INTO competence_hub.auth_sessions (
                    portal_user_id, token_hash, csrf_token_hash, mfa_completed_at, idle_expires_at, absolute_expires_at
                ) VALUES (:actor, :token, :csrf, now(), now() + interval '30 minutes', now() + interval '8 hours')
            """), {"actor": fixture.users[key], "token": digest_token(token), "csrf": digest_token(csrf)})

    async def old_rows(connection):
        return [await connection.scalar(text(
            f"SELECT jsonb_agg(to_jsonb(record) ORDER BY to_jsonb(record)) FROM competence_hub.{table} AS record"
        )) for table in tables]

    tables = ("companies", "company_contacts", "portal_users", "user_roles", "auth_token_delivery_outbox")
    fixture.database(seed)
    before = fixture.database(old_rows)
    headers = {"Cookie": f"{SESSION_COOKIE_NAME}={sessions['admin']}"}
    with TestClient(fixture.app(9443, local_reservations=True), base_url=ORIGIN) as http:
        check("0011 local CAL-2 still starts but customer data are unavailable",
              http.get(BASE + "/capabilities", headers=headers).json() == {"enabled": False}
              and http.get(COMPANY_PATH, headers=headers).status_code == 404)
    apply_migration(db, 12)
    with TestClient(fixture.app(9443), base_url=ORIGIN) as http:
        check("Default V1 mode keeps customer data unavailable even with 0012 present",
              http.get(BASE + "/capabilities", headers=headers).json() == {"enabled": False}
              and http.get(COMPANY_PATH, headers=headers).status_code == 404)
    exercise_api(fixture, sessions, csrf)
    exercise_browser(fixture, sessions["admin"], csrf)
    check("Existing company IDs, contact/account mappings, roles and outbox unchanged", fixture.database(old_rows) == before)

    async def storage_boundaries(connection):
        return (await connection.execute(text("""
            SELECT count(*) FILTER (WHERE entity_type = 'private_customer') = 3
               AND count(*) FILTER (WHERE entity_type = 'company') = 3
               AND NOT has_table_privilege('competence_hub_app','competence_hub.private_customers','DELETE')
               AND NOT has_column_privilege('competence_hub_app','competence_hub.company_customer_details','company_id','UPDATE')
               AND NOT has_schema_privilege('competence_hub_app','competence_hub','CREATE')
            FROM competence_hub.audit_events WHERE action LIKE 'portal.customer.%'
        """))).scalar_one()

    check("Native audit, no new data deletion, tenant reassignment or DDL privileges", fixture.database(storage_boundaries))


if __name__ == "__main__":
    with LocalCalendarPostgres() as database:
        run(database)
    check("Owned synthetic container and volume removed", database.removed and database.volume_removed)
