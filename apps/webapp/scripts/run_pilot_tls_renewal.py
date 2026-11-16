"""One approved private TLS window; existing V1.2 and synthetic logins only."""
import argparse
import base64
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import socket
import ssl
import subprocess
import sys
import time

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import ExtendedKeyUsageOID

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
import open_vps_pilot as access
import pilot_tls_state as state

update, pilot = access.update, access.pilot
backup, require, sha = update.backup, update.require, update.sha
RESUME_RUN = '8c05c255269b4e5d994ef3053cdafc4f'
RESUME_SHA = 'e69c475a472cfdfda084983df6d3af180954b4e2441e94daef6f90968eaa7a79'
BOOTSTRAP = backup.BOOTSTRAP.replace("a['serve'](types.SimpleNamespace(**p))", """t={'__name__':'private_tls_agent'}
exec(compile(s['tls'],'<reviewed-tls-agent>','exec'),t)
t['serve'](types.SimpleNamespace(**a))""")


def validate_pair(ca_raw, leaf_raw, key_raw):
    ca = x509.load_pem_x509_certificate(ca_raw)
    leaf = x509.load_pem_x509_certificate(leaf_raw)
    key = serialization.load_pem_private_key(key_raw, password=None)
    leaf.verify_directly_issued_by(ca)
    now = datetime.now(timezone.utc)
    require(ca.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
            and not leaf.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
            and leaf.not_valid_before_utc <= now < leaf.not_valid_after_utc < ca.not_valid_after_utc
            and leaf.not_valid_after_utc > now + timedelta(days=10)
            and leaf.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName) == ['localhost']
            and ExtendedKeyUsageOID.SERVER_AUTH in leaf.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
            and leaf.public_key().public_numbers() == key.public_key().public_numbers(), 'TLS_CHAIN_KEY_HOST_VALIDITY_REQUIRED')
    return {'hostname': 'localhost', 'not_before_utc': leaf.not_valid_before_utc.isoformat(),
            'not_after_utc': leaf.not_valid_after_utc.isoformat(), 'ca_not_after_utc': ca.not_valid_after_utc.isoformat(),
            'ca_sha256': sha(ca_raw), 'certificate_sha256': sha(leaf_raw)}


def verify_leaf(ca, expected):
    context = ssl.create_default_context(cafile=str(ca))
    with socket.create_connection(('127.0.0.1', 8447), timeout=5) as connection:
        with context.wrap_socket(connection, server_hostname='localhost') as secured:
            pem = ssl.DER_cert_to_PEM_cert(secured.getpeercert(binary_form=True)).encode()
            require(sha(pem) == expected, 'TLS_SERVED_LEAF_MISMATCH')


def policy(directory, ca, name):
    path = directory / name
    path.write_bytes(update.canonical({'policies': {'Certificates': {'Install': [str(ca)]}, 'DisableTelemetry': True}}))
    os.environ['PLAYWRIGHT_FIREFOX_POLICIES_JSON'] = str(path)


def check_context(ca, context):
    cookies = [row for row in context.cookies() if row['name'].startswith('__Host-')]
    require(bool(cookies) and all(row['secure'] and row['httpOnly'] and row['sameSite'] == 'Lax'
                                 and row['domain'] == 'localhost' for row in cookies), 'TLS_SECURE_HOST_ONLY_COOKIE_REQUIRED')
    status, headers, _ = pilot.acceptance.HTTPS(ca, context).call(pilot.acceptance.ACCESS + '/session')
    require(status == 200 and 'no-store' in headers.get('Cache-Control', ''), 'TLS_PRIVATE_SESSION_REQUIRED')
    for page in context.pages:
        require(page.evaluate('localStorage.length===0 && sessionStorage.length===0'), 'TLS_NO_WEB_STORAGE_TOKENS_REQUIRED')


def portal_context(browser):
    matches = [context for context in browser.contexts if any(
        page.url.split('#', 1)[0].rstrip('/') == pilot.acceptance.ORIGIN + '/portal' for page in context.pages)]
    require(len(matches) == 1, 'TLS_EXACT_PRESWITCH_COACH_CONTEXT_REQUIRED')
    return matches[0]


def check_calendar(page):
    from playwright.sync_api import expect
    expect(page.locator('#month-label')).not_to_be_empty()
    expect(page.locator('#loading')).to_be_hidden()
    expect(page.locator('#error')).to_be_hidden()
    # Direct children are week bands, not days in the shared multi-day view.
    days = page.locator('#grid .day[data-date]').evaluate_all('nodes=>nodes.map(e=>e.dataset.date)')
    require(28 <= len(days) <= 31 and len(set(days)) == len(days), 'TLS_CALENDAR_RENDER_REQUIRED')


def root_progress(record, phase):
    record['phase'] = phase
    if phase == 'private_sudo_input':
        print('VPS_SUDO_INPUT=READY. Enter the existing VPS sudo password below; input stays hidden. No GPG/DB password.', flush=True)


def resume_tls_material():
    raw = (ROOT / 'release-artifacts/pilot-tls' / (RESUME_RUN + '.json')).read_bytes()
    require(sha(raw) == RESUME_SHA, 'TLS_EXACT_RESUME_RECEIPT_REQUIRED')
    previous = json.loads(raw)
    require(previous['status'] == 'STOP' and previous['code'] == 'TLS_CALENDAR_RENDER_REQUIRED'
            and previous['rollback'] == previous['rollback_https'] == 'PASS'
            and previous['all_27_exact_immediately_after_switch'] and previous['session_survives_proxy_restart'],
            'TLS_EXACT_ROLLED_BACK_WINDOW_REQUIRED')
    directory = Path(os.environ['LOCALAPPDATA']) / 'CompetenceHub/pilot-tls' / RESUME_RUN
    path = directory / 'new-tls.json.dpapi'
    script = ". '__ACL__';$null=Assert-StagingExternalPath '__DIR__';Assert-StagingPrivateAcl '__DIR__' -Directory;Assert-StagingPrivateAcl '__FILE__'"
    for marker, value in {'__ACL__': pilot.SCRIPTS / 'initialize-staging-operator-config.ps1', '__DIR__': directory, '__FILE__': path}.items():
        script = script.replace(marker, str(value).replace("'", "''"))
    pilot.powershell(script)
    require(path.is_file() and not path.is_symlink(), 'TLS_EXISTING_PAIR_REQUIRED')
    sealed = path.read_bytes()
    require(sha(sealed) == previous['new_tls_ciphertext_sha256'], 'TLS_EXISTING_PAIR_CIPHERTEXT_CHANGED')
    values = json.loads(backup.checked(sys.executable, '-I', str(pilot.SCRIPTS / 'windows_dpapi.py'), '--decrypt-stdin', data=sealed, timeout=30))
    require(set(values) == {'ca', 'certificate', 'key'} and sha(path.read_bytes()) == sha(sealed), 'TLS_EXISTING_PAIR_CHANGED')
    material = tuple(base64.b64decode(values[name], validate=True) for name in ('ca', 'certificate', 'key'))
    metadata = validate_pair(*material)
    require(metadata['ca_sha256'] == previous['ca_sha256'] and metadata['certificate_sha256'] == previous['certificate_sha256'], 'TLS_EXISTING_PUBLIC_IDENTITY_CHANGED')
    return material


def main(options):
    require(os.name == 'nt' and options.execute and options.quiet and sys.stdin.isatty(), 'PRIVATE_TLS_WINDOWS_WINDOW_REQUIRED')
    require(backup.checked('git', '-C', str(ROOT), 'rev-parse', 'HEAD').decode().strip() == options.source, 'SOURCE_CHANGED')
    require(not state.ACCEPTED_RUN, 'TLS_ALREADY_ROLLED_NO_AUTOMATIC_REPEAT')
    directory = options.directory
    require(directory.parent.resolve() == (Path(os.environ['LOCALAPPDATA']) / 'CompetenceHub/pilot-tls').resolve()
            and re.fullmatch('[a-f0-9]{32}', directory.name) and directory.is_dir() and not any(directory.iterdir()),
            'TLS_OWN_EMPTY_PRIVATE_DIRECTORY_REQUIRED')
    pilot.qualify_directory(directory)
    record = {'scope': 'PRIVATE_TLS_ONLY', 'status': 'STOP', 'phase': 'preflight', 'source_commit': options.source,
              'run': directory.name, 'runtime': '5a555e9a9aae', 'migrations': [], 'app_update': 'NONE',
              'real_accounts': 'NONE', 'mail': 'NOT_SENT', 'gpg': 'NOT_USED', 'ionos': 'UNCHANGED', 'pages': 'UNCHANGED',
              'https': 'NOT_RUN', 'mfa_session': 'NOT_RUN', 'services': 'NOT_RUN', 'preservation': 'NOT_RUN', 'rollback': 'NOT_NEEDED'}
    root = tunnel = before_demo = demo = None
    changed = committed = False
    old_ca = None
    names = ('TMP', 'TEMP', 'PLAYWRIGHT_FIREFOX_POLICIES_JSON')
    previous = {name: os.environ.get(name) for name in names}
    report_dir = ROOT / 'release-artifacts/pilot-tls'
    report_dir.mkdir(exist_ok=True)
    report = report_dir / (directory.name + '.json')
    require(not report.exists(), 'TLS_RECEIPT_NO_OVERWRITE')
    try:
        os.environ.update(TMP=str(directory), TEMP=str(directory))
        old_ca = access.accepted_access()
        material = resume_tls_material() if RESUME_RUN else None
        with socket.socket() as check: occupied = check.connect_ex(('127.0.0.1', 8447)) == 0
        if not occupied:
            tunnel = subprocess.Popen([*backup.SSH[:-1], '-N', '-o', 'ExitOnForwardFailure=yes', '-L',
                '127.0.0.1:8447:127.0.0.1:8443', backup.SSH[-1]], stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        update.wait_ready(old_ca); update.verify_leaf(old_ca); access.verify_access_runtime(old_ca)
        record['phase'] = 'existing_coach_session'
        print('PILOT_TLS_PHASE=existing_coach_session. Checking the retained Coach login; MFA may wait up to 31 seconds. No input yet.', flush=True)
        policy(directory, old_ca, 'old-firefox-policy.json')
        data, private = access.read_existing_logins()
        status, headers, _ = pilot.acceptance.HTTPS(old_ca).call('/health/ready')
        require(status == 200, 'TLS_EXISTING_READY_REQUIRED')
        from email.utils import parsedate_to_datetime
        server_time = parsedate_to_datetime(headers['Date']).timestamp()
        offset = server_time - time.time()
        time.sleep(31 - server_time % 30)
        before_demo = pilot.open_demo(data, private, offset, headless=True, roles=('coach',))
        coach_context = portal_context(before_demo[1])
        coach_context.pages[0].wait_for_load_state('networkidle')
        check_context(old_ca, coach_context)
        print('PILOT_TLS_PHASE=existing_coach_session PASS. Opening the protected server channel next.', flush=True)
        record['phase'] = 'protected_root_channel'
        root = backup.RootSession(bootstrap_source=BOOTSTRAP, reviewed_sources={
            'preflight': (pilot.SCRIPTS / 'staging_readonly_preflight.py').read_text(encoding='utf8'),
            'agent': (pilot.SCRIPTS / 'staging_snapshot_agent.py').read_text(encoding='utf8'),
            'tls': (pilot.SCRIPTS / 'pilot_tls_agent.py').read_text(encoding='utf8')},
            progress=lambda phase: root_progress(record, phase))
        old = root.request('inspect', run=directory.name)['old_tls']
        record['old_tls_ciphertext_sha256'] = pilot.protected_copy(directory, 'previous-tls.json.dpapi', update.canonical(old))
        record['phase'] = 'new_tls_material'
        ca_raw, leaf_raw, key_raw = material if material is not None else pilot.certificates()
        if material is not None: record['reused_tls_run'] = RESUME_RUN
        record.update(validate_pair(ca_raw, leaf_raw, key_raw))
        ca = directory / 'pilot-ca.pem'; ca.write_bytes(ca_raw)
        new = {'ca': base64.b64encode(ca_raw).decode(), 'certificate': base64.b64encode(leaf_raw).decode(),
               'key': base64.b64encode(key_raw).decode()}
        record['new_tls_ciphertext_sha256'] = pilot.protected_copy(directory, 'new-tls.json.dpapi', update.canonical(new))
        root.request('stage', **new, old_ca=base64.b64encode(old_ca.read_bytes()).decode(), protected_old_copy_verified=True)
        record['phase'] = 'switch_own_proxy'
        changed = True
        root.request('activate')
        update.wait_ready(ca); verify_leaf(ca, record['certificate_sha256']); pilot.tls_negatives(ca)
        root.request('verify', after_login=False)
        record['all_27_exact_immediately_after_switch'] = True
        record['phase'] = 'strict_browser_acceptance'
        check_context(ca, coach_context)
        record['session_survives_proxy_restart'] = True
        before_demo[1].close(); before_demo[0].stop(); before_demo = None
        policy(directory, ca, 'new-firefox-policy.json')
        demo = access.open_roles(data, private, ca, directory)
        for context in demo[1].contexts:
            if any('/calendar-public.html' in page.url for page in context.pages):
                check_calendar(context.pages[0])
            else: check_context(ca, context)
        access.verify_access_runtime(ca)
        require(pilot.acceptance.HTTPS(ca).call(pilot.acceptance.ACCESS + '/session')[0] == 401, 'TLS_ANONYMOUS_SESSION_DENIED')
        root.request('verify', after_login=True)
        record.update(https='PASS', mfa_session='PASS', services='PASS', preservation='PASS',
                      auth_audit_changes='NORMAL_EXISTING_SYNTHETIC_LOGINS_ONLY', rollback_files_retained=True)
        record['phase'] = 'commit'
        root.request('commit', client_checks=True); committed = True
        root.close(); root = None
        record.update(status='PASS', phase='accepted', completed_at_utc=datetime.now(timezone.utc).isoformat())
    except BaseException as error:
        record['code'] = str(error) if isinstance(error, backup.protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+', str(error)) else type(error).__name__
        if root is not None:
            try: record['rollback'] = root.request('rollback')['status']
            except BaseException:
                record['rollback'] = getattr(root, 'last_failure', {}).get('pilot_rollback', {}).get('status', 'REVIEW_REQUIRED')
            root.close(); root = None
        if changed and not committed:
            try:
                update.wait_ready(old_ca); update.verify_leaf(old_ca)
                record['rollback_https'] = 'PASS'
            except BaseException: record['rollback_https'] = 'REVIEW_REQUIRED'
    finally:
        with report.open('xb') as stream: stream.write(update.canonical(record))
        print('REPORT=' + str(report), flush=True)
        print('REPORT_SHA256=' + sha(report.read_bytes()), flush=True)
        if record['status'] == 'PASS':
            print('PILOT_TLS=PASS HTTPS=PASS HOSTNAME_CHAIN=PASS MFA_SESSION=PASS SIX_SERVICES=PASS BUSINESS_DATA=UNCHANGED', flush=True)
            print('TLS_NOT_AFTER_UTC=' + record['not_after_utc'], flush=True)
            print('ACCESS_PIN_UPDATE=PENDING_VERIFIED_RECEIPT Protected access: https://localhost:8447/portal/', flush=True)
            print('Keep this terminal open for the existing role windows and SSH tunnel. Enter closes only local access.', flush=True)
            try: input()
            except (EOFError, KeyboardInterrupt): pass
        else: print('PILOT_TLS=STOP CODE=' + record.get('code', 'PRIVATE_TLS_NOT_ACCEPTED') + ' NO_AUTOMATIC_RETRY=TRUE', flush=True)
        if root is not None: root.close()
        for session in (before_demo, demo):
            if session is not None: session[1].close(); session[0].stop()
        if tunnel is not None:
            tunnel.terminate()
            try: tunnel.wait(timeout=10)
            except subprocess.TimeoutExpired: tunnel.kill(); tunnel.wait()
        for name, value in previous.items():
            if value is None: os.environ.pop(name, None)
            else: os.environ[name] = value
    require(record['status'] == 'PASS', 'PRIVATE_TLS_NOT_ACCEPTED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true'); parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--source', required=True); parser.add_argument('--directory', required=True, type=Path)
    try: main(parser.parse_args())
    except BaseException as error:
        code = str(error) if isinstance(error, backup.protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+', str(error)) else type(error).__name__
        print('PILOT_TLS=STOP CODE=' + code + ' NO_AUTOMATIC_RETRY=TRUE', flush=True)
        raise SystemExit(1) from None
