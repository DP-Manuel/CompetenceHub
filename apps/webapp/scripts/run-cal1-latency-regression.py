"""Browser-harness regression: successful slow mutations plus list reloads.

This is a visual persistence double, never native PostgreSQL/MFA evidence.
"""
import asyncio
import importlib.util
from pathlib import Path

from playwright.sync_api import sync_playwright

spec = importlib.util.spec_from_file_location("cal1_qa", Path(__file__).with_name("run-cal1-browser-acceptance.py"))
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


def delayed_app(port):
    app = qa.create_acceptance_app(port)
    submitted = False

    async def delayed(scope, receive, send):
        nonlocal submitted
        async def delayed_send(message):
            nonlocal submitted
            if message["type"] == "http.response.start":
                path = scope.get("path", "")
                if scope.get("method") == "POST" and path.endswith("/submit"):
                    submitted = True
                    await asyncio.sleep(6)
                elif submitted and scope.get("method") == "GET" and path.endswith("/calendar/offers"):
                    await asyncio.sleep(1)
            await send(message)
        await app(scope, receive, delayed_send)
    return delayed


def main():
    with qa.synthetic_server(delayed_app) as base, sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        try:
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            qa.login(page, base, qa.COACH_EMAIL)
            qa.submit_offer(page, "Synthetisches Angebot 1")
            assert qa.card(page, "Synthetisches Angebot 1").get_by_text("Zur Prüfung eingereicht", exact=True).is_visible()
            print("PASS | Successful six-second submit and delayed list reload preserve original status assertion")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
