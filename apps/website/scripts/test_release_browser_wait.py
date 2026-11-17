"""Regression for network image readiness; synthetic localhost responses only."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
from pathlib import Path
import threading
import struct
import zlib

from playwright.sync_api import TimeoutError, sync_playwright
import pytest

spec = importlib.util.spec_from_file_location('release_browser', Path(__file__).with_name('run-website-release-acceptance.py'))
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
def png_chunk(kind, data):
    return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))


PIXEL = (b'\x89PNG\r\n\x1a\n' + png_chunk(b'IHDR', struct.pack('!2I5B', 1, 1, 8, 6, 0, 0, 0))
         + png_chunk(b'IDAT', zlib.compress(b'\x00\x00\x00\x00\xff')) + png_chunk(b'IEND', b''))


@contextmanager
def portrait_server(payload):
    release = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/portrait.png':
                release.wait(3)
                body, mime = payload, 'image/png'
            else:
                body, mime = b'<main class="coach-profile-portrait"><img src="/portrait.png" alt="Synthetic"></main>', 'text/html'
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', release
    finally:
        release.set()
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize('payload,success', [(PIXEL, True), (b'not a valid image', False)], ids=['delayed-valid', 'broken'])
def test_portrait_wait_accepts_delayed_valid_image_but_rejects_broken_image(payload, success):
    with portrait_server(payload) as (origin, release), sync_playwright() as pw:
        browser = pw.firefox.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(origin, wait_until='domcontentloaded')
            assert not page.locator('img').evaluate('e=>e.complete')
            timer = threading.Timer(.15, release.set)
            timer.start()
            try:
                if success:
                    qa.wait_for_portrait(page)
                    assert page.locator('img').evaluate('e=>e.naturalWidth') == 1
                else:
                    with pytest.raises(TimeoutError):
                        qa.wait_for_portrait(page, timeout=700)
            finally:
                timer.join()
        finally:
            browser.close()
