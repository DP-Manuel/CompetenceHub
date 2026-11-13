"""Actual packaged UI, delayed session HTTP and synthetic credentials only."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from threading import Event, Thread, Timer
from types import SimpleNamespace
import zipfile

from playwright.sync_api import expect, sync_playwright
import pytest

from test_vps_pilot_access import access, synthetic, Stop


@contextmanager
def packaged_site(monkeypatch, *, password_status=401, mfa_status=401, session_status=401, release_after=None):
    with zipfile.ZipFile(access.update.PACKAGE) as archive:
        with zipfile.ZipFile(io.BytesIO(archive.read(next(n for n in archive.namelist() if n.endswith('.whl'))))) as wheel:
            prefix='competence_hub_api/portal_ui/'
            files={n[len(prefix):]:wheel.read(n) for n in wheel.namelist() if n.startswith(prefix)}
    state=SimpleNamespace(release=Event(),initial_sent=Event(),password_calls=0,mfa_calls=0,
                          login_before_initial=False,timers=[])
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def reply(self,status,raw,kind='application/json'):
            self.send_response(status);self.send_header('Content-Type',kind)
            self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if self.path==access.pilot.acceptance.ACCESS+'/session':
                if release_after is not None:
                    timer=Timer(release_after,state.release.set);state.timers.append(timer);timer.start()
                if not state.release.wait(10):self.reply(504,b'{}');return
                self.reply(session_status,b'{}');state.initial_sent.set();return
            name=self.path.removeprefix('/portal/') or 'index.html'
            if self.path.startswith('/portal/') and name in files:
                kind='text/javascript' if name.endswith(('.js','.mjs')) else 'text/css' if name.endswith('.css') else 'text/html'
                self.reply(200,files[name],kind);return
            self.reply(404,b'{}')
        def do_POST(self):
            self.rfile.read(int(self.headers.get('Content-Length',0)))
            if self.path==access.pilot.acceptance.ACCESS+'/login':
                state.password_calls+=1;state.login_before_initial=not state.initial_sent.is_set()
                self.reply(password_status,json.dumps({'state':'mfa_required','csrf_token':'SYNTHETIC-ONLY'}).encode());return
            if self.path==access.pilot.acceptance.ACCESS+'/mfa/totp/verify':
                state.mfa_calls+=1;self.reply(mfa_status,b'{}');return
            self.reply(404,b'{}')
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=Thread(target=server.serve_forever,daemon=True);worker.start()
    monkeypatch.setattr(access.pilot.acceptance,'ORIGIN','http://127.0.0.1:'+str(server.server_port))
    try:yield state
    finally:
        state.release.set();server.shutdown();server.server_close();worker.join(timeout=5)
        for timer in state.timers:timer.cancel();timer.join(timeout=2)


def test_late_initial_session_reproduces_old_mfa_disappearance(monkeypatch):
    with packaged_site(monkeypatch,password_status=202) as state, sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            page=browser.new_page();page.goto(access.pilot.acceptance.ORIGIN+'/portal/')
            page.locator('#login-email').fill('synthetic@example.invalid')
            page.locator('#login-password').fill('SYNTHETIC-ONLY-NOT-A-REAL-PASSWORD')
            page.get_by_role('button',name='Anmelden',exact=True).click()
            expect(page.locator('#mfa-code')).to_be_visible(timeout=10000)
            assert state.login_before_initial
            state.release.set()
            expect(page.locator('#login-email')).to_be_focused(timeout=10000)
            expect(page.locator('#mfa-code')).to_be_hidden()
        finally:browser.close()


@pytest.mark.parametrize('stage,status', [('password',401),('password',429),('mfa',401),('mfa',429),('session',503)])
def test_opener_waits_for_initial_session_and_stops_once_without_retry(monkeypatch,stage,status):
    with packaged_site(monkeypatch,password_status=status if stage=='password' else 202,
                       mfa_status=status if stage=='mfa' else 204,
                       session_status=status if stage=='session' else 401,release_after=.8) as state:
        data,private=synthetic();steps=[]
        code='INITIAL_SESSION_NOT_ANONYMOUS' if stage=='session' else stage.upper()+'_LOGIN_HTTP_'+str(status)
        with pytest.raises(Stop,match='^'+code+'$'):
            access.pilot.open_demo(data,private,0,roles=('admin',),headless=True,
                                   progress=lambda role,step:steps.append((role,step)))
        assert not state.login_before_initial
        assert state.password_calls==(0 if stage=='session' else 1)
        assert state.mfa_calls==(1 if stage=='mfa' else 0)
        assert steps[-1]==('admin','initial_session' if stage=='session' else stage)
