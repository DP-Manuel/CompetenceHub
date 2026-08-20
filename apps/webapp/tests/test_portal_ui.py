from importlib.resources import files
from html.parser import HTMLParser

import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.main import create_app


class PortalMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.label_targets: list[str] = []
        self.labelledby_targets: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        if element_id := attributes.get("id"):
            self.ids.append(element_id)
        if tag == "label" and (label_target := attributes.get("for")):
            self.label_targets.append(label_target)
        if labelledby := attributes.get("aria-labelledby"):
            self.labelledby_targets.extend(labelledby.split())


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_root_redirects_to_packaged_portal() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="https://test.invalid",
        follow_redirects=False,
    ) as client:
        response = await client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/portal/"
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.anyio
async def test_portal_shell_is_noindex_and_uses_only_external_local_assets() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="https://test.invalid",
    ) as client:
        response = await client.get("/portal/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.headers["cache-control"] == "no-store"
    csp = response.headers["content-security-policy"]
    assert "default-src 'none'" in csp
    assert "script-src 'self'" in csp
    assert "style-src 'self'" in csp
    assert "connect-src 'self'" in csp
    assert "'unsafe-inline'" not in csp
    assert '<meta name="robots" content="noindex, nofollow, noarchive">' in response.text
    assert '<link rel="stylesheet" href="./styles.css">' in response.text
    assert '<script type="module" src="./app.js"></script>' in response.text
    assert "<style" not in response.text
    assert "<script>" not in response.text
    assert 'autocomplete="current-password"' in response.text
    assert 'aria-live="polite"' in response.text
    assert 'id="provisioning-secret"' in response.text
    assert "Jeder Code funktioniert genau einmal" in response.text
    assert "Für Änderungen" in response.text


@pytest.mark.anyio
async def test_portal_assets_are_packaged_and_do_not_persist_auth_material() -> None:
    package = files("competence_hub_api").joinpath("portal_ui")
    assert package.joinpath("index.html").is_file()
    assert package.joinpath("styles.css").is_file()
    assert package.joinpath("app.js").is_file()

    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="https://test.invalid",
    ) as client:
        css_response = await client.get("/portal/styles.css")
        js_response = await client.get("/portal/app.js")

    assert css_response.status_code == 200
    assert css_response.headers["content-type"].startswith("text/css")
    assert js_response.status_code == 200
    assert "javascript" in js_response.headers["content-type"]
    assert "localStorage" not in js_response.text
    assert "sessionStorage" not in js_response.text
    assert "innerHTML" not in js_response.text
    assert "credentials: \"same-origin\"" in js_response.text
    assert 'headers.set("X-CSRF-Token"' in js_response.text


def test_portal_captures_form_values_before_disabling_controls() -> None:
    javascript = (
        files("competence_hub_api")
        .joinpath("portal_ui", "app.js")
        .read_text(encoding="utf-8")
    )

    capture = javascript.index("const data = new FormData(form);")
    disable = javascript.index("return setBusy(form, true) ? data : null;")

    assert capture < disable
    assert javascript.count("const data = beginFormSubmission(form);") == 7


def test_portal_recovers_mutation_state_after_reauthentication() -> None:
    javascript = (
        files("competence_hub_api")
        .joinpath("portal_ui", "app.js")
        .read_text(encoding="utf-8")
    )

    enter_portal = javascript.index("async function enterPortal()")
    clear_errors = javascript.index("clearPortalWorkflowErrors();", enter_portal)
    apply_permissions = javascript.index("applyMutationAvailability();", enter_portal)

    assert clear_errors < apply_permissions
    assert 'request(API.sessionCsrf, { method: "POST" })' in javascript
    assert 'setError("edit-company-error");' in javascript
    assert 'save.className = "button button-primary mutation-control";' in javascript


def test_portal_displays_only_manual_totp_secret_from_enrollment_uri() -> None:
    javascript = (
        files("competence_hub_api")
        .joinpath("portal_ui", "app.js")
        .read_text(encoding="utf-8")
    )

    assert 'searchParams.get("secret")' in javascript
    assert 'byId("provisioning-secret").textContent = secret;' in javascript
    assert 'byId("provisioning-uri")' not in javascript


@pytest.mark.anyio
async def test_api_routes_keep_priority_over_static_portal_mount() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="https://test.invalid",
    ) as client:
        live_response = await client.get("/health/live")
        session_response = await client.get("/api/v1/auth/session")

    assert live_response.status_code == 200
    assert live_response.json() == {"status": "ok"}
    assert session_response.status_code == 401
    assert session_response.json()["code"] == "authentication_failed"


def test_portal_markup_references_unique_existing_ids() -> None:
    markup = (
        files("competence_hub_api")
        .joinpath("portal_ui", "index.html")
        .read_text(encoding="utf-8")
    )
    parser = PortalMarkupParser()
    parser.feed(markup)

    assert len(parser.ids) == len(set(parser.ids))
    existing_ids = set(parser.ids)
    assert set(parser.label_targets) <= existing_ids
    assert set(parser.labelledby_targets) <= existing_ids
