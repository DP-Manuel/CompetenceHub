"""Actual Edge/JS operator sequence with ONLY an owned synthetic PG fixture.

The human surrogate may read its own generated synthetic MFA material here.
Production operator code must never do so. No real key, credential or recording.
"""

import asyncio
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta
import importlib.util
from pathlib import Path
import secrets
from types import SimpleNamespace

import pyotp
from playwright.sync_api import sync_playwright
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from test_initial_admin_postgres_local import _local_configuration
from test_runtime import runtime_settings

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "synthetic_native_admin_operator",
    ROOT / "apps/webapp/scripts/staging_admin_operator.py",
)
operator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(operator)


def test_actual_edge_operator_enrollment_challenge_recovery_replay_and_cleanup(
    monkeypatch,
):
    app_url, owner_url, nonce = _local_configuration()
    login = {"email": "synthetic-browser-operator@example.invalid"}
    password = secrets.token_urlsafe(40)
    clock = {"now": datetime.now(UTC)}
    synthetic = {
        "seed": None,
        "codes": [],
        "enrollment": False,
        "mfa_logins": set(),
        "logins": 0,
    }

    async def database(action):
        engine = create_async_engine(owner_url, hide_parameters=True)
        try:
            async with engine.begin() as connection:
                assert (
                    await connection.scalar(
                        text(
                            "SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname=current_database()"
                        )
                    )
                    == "synthetic-initial-admin-owned:" + nonce
                )
                await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
                return await action(connection)
        finally:
            await engine.dispose()

    async def seed(connection):
        user = await connection.scalar(
            text(
                "INSERT INTO competence_hub.portal_users(display_name,email) VALUES ('Synthetic Browser Operator',:email) RETURNING id"
            ),
            login,
        )
        await connection.execute(
            text(
                "INSERT INTO competence_hub.user_roles(user_id,role_id) SELECT :user,id FROM competence_hub.roles WHERE code='admin' AND active"
            ),
            {"user": user},
        )
        await connection.execute(
            text(
                "INSERT INTO competence_hub.auth_password_credentials(portal_user_id,password_hash) VALUES (:user,:password)"
            ),
            {
                "user": user,
                "password": PasswordService(PasswordPolicy(frozenset())).hash(password),
            },
        )

    asyncio.run(database(seed))

    def app(settings):
        result = create_runtime_app(settings)
        result.state.clock = lambda: clock["now"]
        return result

    async def recovery_count(url, *, email):
        assert url == owner_url and email == login["email"]

        async def count(connection):
            return {
                "recovery_used": await connection.scalar(
                    text(
                        "SELECT count(*) FROM competence_hub.auth_recovery_codes rc JOIN competence_hub.portal_users u ON u.id=rc.portal_user_id WHERE u.email=:email AND used_at IS NOT NULL"
                    ),
                    login,
                )
            }

        return await database(count)

    def human(page):
        if (
            page.locator("#enrollment-view").is_visible()
            and not synthetic["enrollment"]
        ):
            value = page.locator("#provisioning-secret").inner_text()
            if not value:
                return
            synthetic["seed"] = value
            page.locator("#enrollment-code").fill(
                pyotp.TOTP(value).at(clock["now"].timestamp())
            )
            page.locator("#enrollment-form button[type=submit]").click()
            synthetic["enrollment"] = True
        elif page.locator("#recovery-view").is_visible():
            synthetic["codes"] = page.locator("#recovery-codes li").all_text_contents()
            assert len(set(synthetic["codes"])) == 10
            page.locator("#recovery-confirmed").check()
            page.locator("#enter-portal").click()
        elif (
            page.locator("#mfa-view").is_visible()
            and synthetic["logins"] not in synthetic["mfa_logins"]
        ):
            if page.get_by_role("radio", name="Recovery-Code", exact=True).is_checked():
                code = synthetic["codes"][0]
            else:
                clock["now"] += timedelta(seconds=60)
                code = pyotp.TOTP(synthetic["seed"]).at(clock["now"].timestamp())
            page.locator("#mfa-code").fill(code)
            page.locator("#mfa-form button[type=submit]").click()
            synthetic["mfa_logins"].add(synthetic["logins"])

    class Visibility:
        def __init__(self, page, locator):
            self.page, self.target = page, locator

        def is_visible(self):
            human(self.page)
            return self.target.is_visible()

    class Page:
        def __init__(self, value):
            self.page = value

        def __getattr__(self, name):
            return getattr(self.page, name)

        def goto(self, *args, **kwargs):
            synthetic["logins"] += 1
            return self.page.goto(*args, **kwargs)

        def locator(self, selector):
            target = self.page.locator(selector)
            return (
                Visibility(self.page, target)
                if selector in ("#portal-view", "#mfa-error")
                else target
            )

    class Context:
        def __init__(self, value):
            self.context = value

        def __getattr__(self, name):
            return getattr(self.context, name)

        def new_page(self):
            return Page(self.context.new_page())

    class Browser:
        def __init__(self, value):
            self.browser = value

        def __getattr__(self, name):
            return getattr(self.browser, name)

        def new_context(self, **kwargs):
            return Context(self.browser.new_context(**kwargs))

    @contextmanager
    def browser_driver():
        with sync_playwright() as driver:
            yield SimpleNamespace(
                chromium=SimpleNamespace(
                    launch=lambda **kwargs: Browser(
                        driver.chromium.launch(**{**kwargs, "headless": True})
                    )
                )
            )

    monkeypatch.setattr(operator, "create_runtime_app", app)
    monkeypatch.setattr(operator, "inspect", recovery_count)
    monkeypatch.setattr(operator, "sync_playwright", browser_driver)
    monkeypatch.setattr(operator, "NATIVE_WAIT_SECONDS", 30)
    settings = replace(runtime_settings(), database_url=app_url)
    with operator.operator_server(
        lambda base: replace(settings, allowed_origin=base)
    ) as origin:
        result = operator.manual_native(origin, login, password, owner_url=owner_url)
        assert set(result.values()) == {"PASS"}
        assert synthetic["logins"] == 4 and len(synthetic["mfa_logins"]) == 3

    async def after(connection):
        return await connection.scalar(
            text(
                "SELECT count(*) FROM competence_hub.coaches WHERE portal_user_id IN (SELECT id FROM competence_hub.portal_users WHERE email=:email)"
            ),
            login,
        )

    assert asyncio.run(database(after)) == 0
