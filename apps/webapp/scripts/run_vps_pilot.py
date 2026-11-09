"""Private operator: bound existing restore -> isolated VPS install -> acceptance.

No new backup, GPG, migration, mail, real identities or public listener.
Secrets only in protected process pipes, root files and CurrentUser ciphertext.
"""
import argparse
import base64
from datetime import datetime, timedelta, timezone
import getpass
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import socket
import ssl
import subprocess
import sys
import time
from urllib.parse import quote
from uuid import uuid4

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / 'deploy/scripts'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


backup = module('pilot_private_transport', Path(__file__).with_name('protected_staging_backup.py'))
acceptance = module('pilot_native_acceptance', Path(__file__).with_name('vps_pilot_acceptance.py'))
require, sha, canonical = backup.require, backup.protocol.sha, backup.protocol.canonical
RECEIPT = '6db91e37eaac4cc8a87c430d1ca7a462'
RECEIPT_SHA = 'ffb7a809b25e3e4b72d8961e874d9d6de3fb5bff8d51e39c108cbecb35093710'
PACKAGE = ROOT / 'release-artifacts/webapp/competence-hub-webapp-0.1.0-0080195755e3-20261109T182244Z.zip'
PACKAGE_SHA = 'f3478fc34de4647fd182a9c7262678b8de2e6b194428ec7dbcc0a116d9c51c41'
WHEELS = ROOT / 'release-artifacts/webapp-linux/20261109T182331Z-7c8e9560/wheelhouse'
INVENTORY_SHA = '98e85f0832b2769408cabcaf531b875913cd775e7961e5c52cdfb2e37a8b609f'

BOOTSTRAP = backup.BOOTSTRAP.replace('131072', '262144').replace(
    "a['serve'](types.SimpleNamespace(**p))",
    "v={'__name__':'private_pilot_agent'}\nexec(compile(s['pilot'],'<reviewed-pilot-agent>','exec'),v)\nv['serve'](types.SimpleNamespace(**p),types.SimpleNamespace(**a))")


def powershell(script, *, data=None):
    return backup.checked('pwsh', '-NoProfile', '-NonInteractive', '-EncodedCommand',
                          base64.b64encode(script.encode('utf-16-le')).decode(), data=data)


def existing_keys():
    # Existing DPAPI file is used only in this private child, never displayed.
    script = """$ErrorActionPreference='Stop'
try {
 . '__ACL__'
 $path=Join-Path $env:LOCALAPPDATA 'CompetenceHub/staging-operator/staging-operator.keys.clixml'
 $null=Assert-StagingExternalPath $path
 Assert-StagingPrivateAcl $path
 $before=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
 $secret=Import-Clixml -LiteralPath $path
 if ($secret -isnot [Security.SecureString]) {exit 2}
 $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
 try {
  $payload=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)|ConvertFrom-Json -AsHashtable
  Assert-StagingOperatorPayload $payload $script:OperatorKeyVersions
  if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -cne $before) {exit 3}
  [Console]::Out.Write(($payload.variables|ConvertTo-Json -Depth 8 -Compress))
 } finally {[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer);$secret.Dispose();$payload=$null}
} catch {exit 1}
""".replace('__ACL__', str(SCRIPTS / 'initialize-staging-operator-config.ps1').replace("'", "''"))
    return json.loads(powershell(script))


def qualify_directory(directory):
    script="""$ErrorActionPreference='Stop'
try {
 . '__ACL__'
 $null=Assert-StagingExternalPath '__PATH__'
 Assert-StagingPrivateAcl '__PATH__' -Directory
} catch {exit 1}
""".replace('__ACL__',str(SCRIPTS/'initialize-staging-operator-config.ps1')).replace('__PATH__',str(directory))
    powershell(script)
    volume="""$ErrorActionPreference='Stop';try {
 $v=Get-BitLockerVolume -MountPoint 'C:'
 if ([string]$v.VolumeStatus -cne 'FullyEncrypted' -or [string]$v.ProtectionStatus -cne 'On' -or
     [string]$v.LockStatus -cne 'Unlocked' -or [IO.DriveInfo]::new('C:\\').AvailableFreeSpace -lt 1GB) {exit 1}
} catch {exit 1}"""
    backup.checked(str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'),
                   '-NoProfile','-NonInteractive','-Command',volume)


def accepted_baseline():
    receipt = ROOT / ('release-artifacts/protected-staging-backup/' + RECEIPT + '.json')
    require(sha(receipt.read_bytes()) == RECEIPT_SHA, 'BOUND_RESTORE_RECEIPT_REQUIRED')
    record = json.loads(receipt.read_bytes())
    require(all(record.get(name) == 'PASS' for name in ('status', 'backup', 'restore', 'postflight'))
            and record.get('source_unchanged') is True and record.get('own_probe_removed') is True,
            'COMPLETED_RESTORE_REQUIRED')
    directory = Path(os.environ['LOCALAPPDATA']) / 'CompetenceHub/pilot-snapshots' / RECEIPT
    for name, field in (('database.dump.dpapi', 'ciphertext_sha256'), ('baseline.json.dpapi', 'baseline_ciphertext_sha256')):
        path = directory / name
        script = ". '__ACL__'; $null=Assert-StagingExternalPath '__PATH__'; Assert-StagingPrivateAcl '__PATH__'"
        powershell(script.replace('__ACL__', str(SCRIPTS / 'initialize-staging-operator-config.ps1')).replace('__PATH__', str(path)))
        require(sha(path.read_bytes()) == record[field], 'EXISTING_ROLLBACK_COPY_CHANGED')
    recovered = backup.checked(sys.executable, '-I', str(SCRIPTS / 'windows_dpapi.py'), '--decrypt-stdin',
                               data=(directory / 'baseline.json.dpapi').read_bytes())
    return json.loads(recovered)['baseline']


def package_payload():
    raw = PACKAGE.read_bytes()
    require(sha(raw) == PACKAGE_SHA, 'EXACT_RELEASE_REQUIRED')
    inventory = (WHEELS / 'INVENTORY.json').read_bytes()
    require(sha(inventory) == INVENTORY_SHA, 'BOUND_LINUX_WHEELS_REQUIRED')
    wheels = []
    for item in json.loads(inventory)['files']:
        require(re.fullmatch('[A-Za-z0-9_.+-]+\\.whl', item['file']), 'WHEEL_PATH_REJECTED')
        data = (WHEELS / item['file']).read_bytes()
        require(sha(data) == item['sha256'], 'WHEEL_HASH')
        wheels.append({**item, 'data': base64.b64encode(data).decode()})
    corpus = Path(os.environ['LOCALAPPDATA']) / 'CompetenceHub/staging-operator-corpus-20261030/compromised-password-fingerprints.sha256'
    return {'package': base64.b64encode(raw).decode(), 'wheels': wheels,
            'corpus': base64.b64encode(corpus.read_bytes()).decode(),
            'worker': (SCRIPTS / 'vps_pilot_worker.py').read_text(encoding='utf8')}


def certificates():
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Competence Hub private pilot ' + uuid4().hex)])
    ca = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(ca_key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=5))
          .not_valid_after(now+timedelta(days=30)).add_extension(x509.BasicConstraints(ca=True,path_length=0),True)
          .add_extension(x509.KeyUsage(False,False,False,False,False,True,True,False,False),True)
          .sign(ca_key,hashes.SHA256()))
    leaf = (x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'localhost')]))
            .issuer_name(name).public_key(leaf_key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now-timedelta(minutes=5)).not_valid_after(now+timedelta(days=14))
            .add_extension(x509.BasicConstraints(ca=False,path_length=None),True)
            .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost')]),False)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),False)
            .sign(ca_key,hashes.SHA256()))
    return (ca.public_bytes(serialization.Encoding.PEM),
            leaf.public_bytes(serialization.Encoding.PEM),
            leaf_key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))


def fixture():
    values = {'accounts': {}, 'topic': str(uuid4()), 'coaches': {name: str(uuid4()) for name in ('coach','coach_two')}}
    for key, role in {'admin':'admin','reviewer':'calendar_reviewer','coach':'coach','coach_two':'coach'}.items():
        user = uuid4()
        values['accounts'][key] = {'id': str(user), 'email': 'synthetic-vps-'+user.hex+'@example.invalid',
                                   'role': role, 'password': secrets.token_urlsafe(32)+'aA9!'}
    return values


def protected_copy(directory, name, data):
    stored = backup.private_ciphertext_file(directory / name, backup.dpapi.transform(data))
    recovered = backup.checked(sys.executable, '-I', str(SCRIPTS / 'windows_dpapi.py'), '--decrypt-stdin', data=stored)
    require(sha(recovered) == sha(data), 'PRIVATE_CONFIGURATION_RECOVERY_FAILED')
    return sha(stored)


def tls_negatives(ca):
    for context, hostname in ((ssl.create_default_context(), 'localhost'),
                              (ssl.create_default_context(cafile=str(ca)), 'not-localhost.invalid')):
        try:
            with socket.create_connection(('127.0.0.1',8447),timeout=5) as sock:
                with context.wrap_socket(sock,server_hostname=hostname):
                    pass
        except ssl.SSLCertVerificationError:
            continue
        raise backup.protocol.SnapshotStop('TLS_NEGATIVE_CONTROL_FAILED')


def open_demo(data, private, offset, *, headless=False):
    """Three separate role contexts; no passwords or recovery values displayed."""
    import pyotp
    from playwright.sync_api import sync_playwright, expect
    driver=sync_playwright().start()
    browser=None
    try:
        browser=driver.firefox.launch(headless=headless)
        for key in ('coach','reviewer','admin'):
            context=browser.new_context(viewport={'width':1366,'height':900})
            page=context.new_page();page.goto(acceptance.ORIGIN+'/portal/')
            page.locator('#login-email').fill(data['accounts'][key]['email'])
            page.locator('#login-password').fill(data['accounts'][key]['password'])
            page.get_by_role('button',name='Anmelden',exact=True).click()
            page.locator('#mfa-code').fill(pyotp.TOTP(private[key]['totp']).at(time.time()+offset))
            page.get_by_role('button',name='Bestätigen',exact=True).click()
            expect(page.locator('#portal-view')).to_be_visible()
        page=browser.new_page();page.goto(acceptance.ORIGIN+'/portal/calendar-public.html')
        return driver,browser
    except BaseException:
        if browser is not None:browser.close()
        driver.stop()
        raise


def close_committed(root):
    result={'status':'ACKNOWLEDGED'}
    try:root.request('close')
    except Exception:result['status']='CLOSE_ACK_NOT_RECEIVED'
    finally:
        try:root.close()
        except Exception:result['status']='CLIENT_CHANNEL_CLOSE_REVIEW_REQUIRED'
    return result


def main(options):
    require(os.name == 'nt' and options.execute and sys.stdin.isatty(), 'PRIVATE_WINDOWS_OPERATOR_REQUIRED')
    require(backup.checked('git','-C',str(ROOT),'rev-parse','HEAD').decode().strip() == options.source, 'SOURCE_CHANGED')
    directory = options.directory
    expected = Path(os.environ['LOCALAPPDATA']) / 'CompetenceHub/pilot-runs'
    require(directory.parent.resolve() == expected.resolve() and re.fullmatch('[a-f0-9]{32}',directory.name)
            and directory.is_dir() and not any(directory.iterdir()), 'OWN_NEW_PRIVATE_DIRECTORY_REQUIRED')
    report = {'scope':'PRIVATE_VPS_SYNTHETIC_PILOT','status':'STOP','phase':'local_preflight',
              'source_commit':options.source,'package_sha256':PACKAGE_SHA,'restore_receipt_sha256':RECEIPT_SHA,
              'migrations':[],'real_accounts':'NONE','ionos':'UNCHANGED','gpg':'NOT_USED',
              'backup_repeated':False,'deployment':'NOT_RUN','cal1':'NOT_RUN','mfa_rbac':'NOT_RUN',
              'restart':'NOT_RUN','postgres_persistence':'NOT_RUN','onboarding':'NOT_RUN'}
    root = tunnel = None
    demo = None
    key_store = Path(os.environ['LOCALAPPDATA'])/'CompetenceHub/staging-operator/staging-operator.keys.clixml'
    key_hash = sha(key_store.read_bytes())
    receipt_dir = ROOT/'release-artifacts/vps-pilot'
    receipt_dir.mkdir(exist_ok=True)
    try:
        qualify_directory(directory)
        baseline = accepted_baseline()
        payload = package_payload()
        keys = existing_keys()
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',8447))
        password = getpass.getpass('Existing PostgreSQL password for competence_hub_app (hidden; never chat): ')
        variables = {**keys, 'COMPETENCE_HUB_DATABASE_URL':'postgresql+asyncpg://competence_hub_app:'+quote(password,safe='')+'@127.0.0.1:5432/competence_hub_staging',
                     'COMPETENCE_HUB_ALLOWED_ORIGIN':acceptance.ORIGIN,'COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED':'false',
                     'COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH':'/opt/competence-hub-pilot/corpus.sha256'}
        password = None
        ca, leaf, tls_key = certificates()
        ca_path = directory/'pilot-ca.pem'
        ca_path.write_bytes(ca)  # Public certificate in an already private directory.
        policy = directory/'firefox-policy.json'
        policy.write_bytes(canonical({'policies':{'Certificates':{'Install':[str(ca_path)]},'DisableTelemetry':True}}))
        os.environ['PLAYWRIGHT_FIREFOX_POLICIES_JSON'] = str(policy)
        configuration = {'variables':variables,'tls_key':tls_key.decode(),'tls_certificate':leaf.decode()}
        config_sha = sha(canonical(configuration))
        protected_sha = protected_copy(directory,'runtime-configuration.json.dpapi',canonical(configuration))
        report.update(configuration_ciphertext_sha256=protected_sha,tls_ca_sha256=sha(ca),tls_certificate_sha256=sha(leaf))
        data = fixture()
        protected_copy(directory,'synthetic-logins.json.dpapi',canonical(data))
        root = backup.RootSession(bootstrap_source=BOOTSTRAP,reviewed_sources={
            'preflight':(SCRIPTS/'staging_readonly_preflight.py').read_text(encoding='utf8'),
            'agent':(SCRIPTS/'staging_snapshot_agent.py').read_text(encoding='utf8'),
            'pilot':(SCRIPTS/'vps_pilot_agent.py').read_text(encoding='utf8')})
        report['phase']='remote_preflight'
        report['preflight']=root.request('preflight',baseline=baseline)
        print('PASS | Existing restore proof reused; current 0006 database exactly matches.',flush=True)
        report['phase']='installation'
        report['stage']=root.request('stage',**payload)
        configured=root.request('configure',**configuration)
        require(configured['configuration_sha256']==config_sha,'CONFIGURATION_TRANSFER_MISMATCH')
        root.request('activate',configuration_sha256=config_sha,protected_configuration_sha256=protected_sha,
                     fixture=data,rate_key=keys['COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY'])
        report['deployment']='INSTALLED_PENDING_ACCEPTANCE'
        tunnel=subprocess.Popen([*backup.SSH[:-1],'-N','-o','ExitOnForwardFailure=yes','-L','127.0.0.1:8447:127.0.0.1:8443',backup.SSH[-1]],
                                stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(100):
            require(tunnel.poll() is None,'OWN_SSH_TUNNEL_FAILED')
            try:
                if acceptance.HTTPS(ca_path).call('/health/ready')[0]==200:break
            except OSError:pass
            time.sleep(.2)
        else:raise backup.protocol.SnapshotStop('NATIVE_READINESS_FAILED')
        tls_negatives(ca_path)
        report['tls']='PASS'
        report['phase']='native_acceptance'
        private=acceptance.run(root,data,ca_path,directory,report)
        protected_copy(directory,'synthetic-mfa-recovery.json.dpapi',canonical(private))
        report['phase']='postflight'
        needles=[item['totp'] for item in private.values()]+[code for item in private.values() for code in item['recovery']]
        require(sha(key_store.read_bytes())==key_hash,'ORIGINAL_APPLICATION_KEYS_CHANGED')
        offset=root.request('clock')['server_time']-time.time()
        report['postflight']=root.request('commit',secret_needles=needles)
        report['server_commit']='ACKNOWLEDGED'
        report.update(status='PASS',phase='complete',deployment='PASS',original_application_keys='UNCHANGED',
                      access=acceptance.ORIGIN,completed_at_utc=datetime.now(timezone.utc).isoformat())
        report['channel_close']=close_committed(root);root=None
        try:
            demo=open_demo(data,private,offset)
            report['interactive_role_windows']='OPEN'
        except Exception:
            report['interactive_role_windows']='NOT_OPENED'
            print('Automatic role windows not opened; acceptance evidence and encrypted logins retained. Do not rerun installation.',flush=True)
        print('VPS_PILOT=PASS CAL1=PASS MFA_RBAC=PASS PERSISTENCE=PASS RESTART=PASS FOREIGN_SERVICES=PASS',flush=True)
        print('Protected pilot: '+acceptance.ORIGIN+'/portal/ and /portal/calendar-public.html',flush=True)
        print('Keep this private terminal open for the SSH tunnel. No public access or real accounts.',flush=True)
        print('Private evidence directory: '+str(directory),flush=True)
    except BaseException as error:
        report['failure_type']=type(error).__name__
        if isinstance(error,backup.protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+',str(error)):
            report['failure_code']=str(error)
        if root is not None:
            report['remote_failure']=getattr(root,'last_failure',None)
        raise
    finally:
        try:
            if root is not None:
                try:report['close_acknowledgment']=root.request('close')
                except Exception:
                    report['remote_failure']=getattr(root,'last_failure',None)
                finally:root.close()
            path=receipt_dir/(directory.name+'.json')
            with path.open('xb') as stream:stream.write(canonical(report))
            print('REPORT='+str(path),flush=True)
            if report['status']=='PASS':
                try:input('Press Enter to close this local tunnel; VPS pilot services remain private and running. ')
                except (EOFError,KeyboardInterrupt):pass
        finally:
            try:
                if tunnel is not None:
                    tunnel.terminate()
                    try:tunnel.wait(timeout=10)
                    except subprocess.TimeoutExpired:tunnel.kill();tunnel.wait()
            finally:
                if demo is not None:
                    demo[1].close();demo[0].stop()
                os.environ.pop('PLAYWRIGHT_FIREFOX_POLICIES_JSON',None)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--source',required=True)
    parser.add_argument('--directory',type=Path,required=True)
    options=parser.parse_args()
    try:main(options)
    except BaseException as error:
        code=str(error) if isinstance(error,backup.protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+',str(error)) else type(error).__name__
        print('VPS_PILOT=STOP CODE='+code+' REAL_ACCOUNTS=NONE IONOS=UNCHANGED',flush=True)
        raise SystemExit(1) from None
