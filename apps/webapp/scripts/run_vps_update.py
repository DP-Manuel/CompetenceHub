"""One private update window: current backup/restore, V1, native tests, compensation."""
import argparse
import base64
from datetime import datetime,timezone
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
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[3]
SCRIPTS=ROOT/'deploy/scripts'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


pilot=module('v1_private_pilot',Path(__file__).with_name('run_vps_pilot.py'))
backup=pilot.backup
v1=module('v1_remote_acceptance',Path(__file__).with_name('vps_user_readiness_acceptance.py'))
require,sha,canonical=pilot.require,pilot.sha,pilot.canonical
PACKAGE=ROOT/'release-artifacts/webapp/competence-hub-webapp-0.1.0-bc53775b08dc-20261110T184433Z.zip'
PACKAGE_SHA='21849d1e2f33b6044e6a93fdc27fb3ab39f5b5bd7bea047ba73fed99e8d5df97'
WHEELS=ROOT/'release-artifacts/webapp-linux/20261110T184522Z-4efed9db/wheelhouse'
INVENTORY_SHA='98e85f0832b2769408cabcaf531b875913cd775e7961e5c52cdfb2e37a8b609f'
ACCEPTED_RUN='e89ce1ef18b14ad38bff9fcbf0199854'
ACCEPTED_SHA='2becd577f08e3e13cb8e429ec2f8451f50bdabe479be33e4866950f1fd80b5fa'
CA_SHA='14827c63424b87f7b40aa04019e720872e241e5a8f7a4a5b495cdcb3c89b302d'
LEAF_SHA='aecd310881202f9438b14a9d57d7f3e033bf947416a460fa3263fa44cf71d27a'
RESUME_RUN='2b834613c4204c1d98a37cbd43134fa1'
RESUME_SHA='822c5ddba0163be88327ec160c0544994e63494b4d21626dc16243092f6737d4'
BOOTSTRAP=backup.BOOTSTRAP.replace('131072','262144').replace("a['serve'](types.SimpleNamespace(**p))", """v={'__name__':'legacy_service_contract'}
exec(compile(s['legacy'],'<reviewed-service-contract>','exec'),v)
u={'__name__':'v1_update_agent'}
exec(compile(s['update'],'<reviewed-v1-update>','exec'),u)
u['serve'](types.SimpleNamespace(**p),types.SimpleNamespace(**a),types.SimpleNamespace(**v))""")


def fixture():
    value=pilot.fixture();value['coaches']['invited']=str(uuid4())
    value['automatic_onboarding']=value['preserve_reference']=True
    value['invites']={name:{'nonce':str(uuid4()),'password':secrets.token_urlsafe(32)+'Aa9!'} for name in ('reviewer','coach')}
    for item in value['invites'].values():item['email']='synthetic-v1-'+item['nonce'].replace('-','')+'@example.invalid'
    return value


def payload():
    raw=PACKAGE.read_bytes();require(sha(raw)==PACKAGE_SHA,'EXACT_V1_PACKAGE_REQUIRED')
    inventory=(WHEELS/'INVENTORY.json').read_bytes();require(sha(inventory)==INVENTORY_SHA,'BOUND_LINUX_WHEELS_REQUIRED')
    wheels=[]
    for row in json.loads(inventory)['files']:
        require(re.fullmatch(r'[A-Za-z0-9_.+-]+\.whl',row['file']),'WHEEL_PATH_REJECTED')
        data=(WHEELS/row['file']).read_bytes();require(sha(data)==row['sha256'],'WHEEL_HASH')
        wheels.append({**row,'data':base64.b64encode(data).decode()})
    return {'package':base64.b64encode(raw).decode(),'wheels':wheels,'worker':(SCRIPTS/'vps_update_worker.py').read_text(encoding='utf8')}


def accepted_ca():
    raw=(ROOT/'release-artifacts/vps-pilot'/(ACCEPTED_RUN+'.json')).read_bytes()
    require(sha(raw)==ACCEPTED_SHA and json.loads(raw)['status']=='PASS','ACCEPTED_PILOT_RECEIPT_REQUIRED')
    path=Path(os.environ['LOCALAPPDATA'])/'CompetenceHub/pilot-runs'/ACCEPTED_RUN/'pilot-ca.pem'
    require(sha(path.read_bytes())==CA_SHA,'ORIGINAL_PUBLIC_CA_REQUIRED')
    return path


def wait_ready(ca):
    deadline=time.monotonic()+45
    for _ in range(100):
        try:
            if pilot.acceptance.HTTPS(ca,timeout=2).call('/health/ready')[0]==200:return
        except OSError:pass
        if time.monotonic()>=deadline:break
        time.sleep(.2)
    raise backup.protocol.SnapshotStop('STRICT_TLS_READINESS_FAILED')


def verify_leaf(ca):
    context=ssl.create_default_context(cafile=str(ca))
    with socket.create_connection(('127.0.0.1',8447),timeout=5) as sock:
        with context.wrap_socket(sock,server_hostname='localhost') as tls:
            # Accepted leaf hash was recorded over PEM bytes; normalize to PEM.
            require(sha(ssl.DER_cert_to_PEM_cert(tls.getpeercert(binary_form=True)).encode())==LEAF_SHA,'ORIGINAL_SERVED_CERTIFICATE_REQUIRED')


def private_recovery(directory,name,data):
    digest=pilot.protected_copy(directory,name,data)
    stored=(directory/name).read_bytes()
    recovered=backup.checked(sys.executable,'-I',str(SCRIPTS/'windows_dpapi.py'),'--decrypt-stdin',data=stored)
    require(sha(recovered)==sha(data),'EXACT_PRIVATE_REREAD_REQUIRED')
    return digest,recovered


def resume_material(run):
    require(run==RESUME_RUN,'EXACT_ACCEPTED_RESUME_REQUIRED')
    raw=(ROOT/'release-artifacts/vps-v1-update'/(run+'.json')).read_bytes()
    require(sha(raw)==RESUME_SHA,'ACCEPTED_RESUME_RECEIPT_CHANGED')
    previous=json.loads(raw)
    require(previous['package_sha256']==PACKAGE_SHA and previous['backup']==previous['restore']=='PASS'
            and previous['cal1']==previous['mfa_rbac']==previous['user_management']==previous['invitation_workflow']=='PASS'
            and previous['restore_proof']['source_unchanged'] and previous['restore_proof']['probe_removed']
            and previous['failure_code']=='EXISTING_LOOPBACK_PILOT_REQUIRED','ACCEPTED_RESUME_GATES_REQUIRED')
    directory=Path(os.environ['LOCALAPPDATA'])/'CompetenceHub/pilot-updates'/run
    pilot.qualify_directory(directory)
    def read_existing(name,digest=None):
        path=directory/name
        require(path.is_file() and not path.is_symlink(),'EXISTING_PRIVATE_COPY_REQUIRED')
        sealed=path.read_bytes()
        if digest:require(sha(sealed)==digest,'EXISTING_CIPHERTEXT_CHANGED')
        return backup.checked(sys.executable,'-I',str(SCRIPTS/'windows_dpapi.py'),'--decrypt-stdin',data=sealed,timeout=30)
    capture=json.loads(read_existing('baseline.json.dpapi',previous['baseline_ciphertext_sha256']))
    dump=read_existing('database.dump.dpapi',previous['ciphertext_sha256'])
    require(sha(dump)==capture['dump_sha256'],'EXISTING_RECOVERY_COPY_CHANGED');del dump
    configuration=json.loads(read_existing('original-configuration.json.dpapi',previous['configuration_ciphertext_sha256']))
    hashes={name:sha(base64.b64decode(value,validate=True)) for name,value in configuration.items()}
    require(hashes==previous['preflight']['configuration_hashes'],'EXISTING_CONFIGURATION_COPY_CHANGED')
    data=json.loads(read_existing('owned-synthetic-logins.json.dpapi'))
    private=json.loads(read_existing('owned-synthetic-recovery.json.dpapi'))
    needles=[x['password'] for x in data['accounts'].values()]+[x['password'] for x in data['invites'].values()]
    needles += [v['totp'] for v in private.values()]+[code for v in private.values() for code in v['recovery']]
    return previous,{'resume_run':run,'baseline':capture['baseline'],'configuration_hashes':hashes,
                     'previous_start':previous['preflight']['server_time']},needles


def verify_login_shell(directory):
    with v1.sync_playwright() as pw:
        browser=pw.firefox.launch(headless=True)
        try:
            page=browser.new_page(viewport={'width':390,'height':844});errors=[]
            page.on('pageerror',lambda error:errors.append(error.name))
            page.goto(pilot.acceptance.ORIGIN+'/portal/');v1.expect(page.locator('#login-view')).to_be_visible()
            require(not errors and page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'RESUME_LOGIN_SHELL_FAILED')
            page.screenshot(path=str(directory/'resume-login-390.png'),full_page=True)
        finally:browser.close()


def main(options):
    require(os.name=='nt' and options.execute and options.quiet and sys.stdin.isatty(),'PRIVATE_QUIET_WINDOWS_OPERATOR_REQUIRED')
    require(backup.checked('git','-C',str(ROOT),'rev-parse','HEAD').decode().strip()==options.source,'SOURCE_CHANGED')
    directory=options.directory
    require(directory.parent.resolve()==(Path(os.environ['LOCALAPPDATA'])/'CompetenceHub/pilot-updates').resolve()
            and re.fullmatch('[a-f0-9]{32}',directory.name) and directory.is_dir() and not any(directory.iterdir()),'OWN_EMPTY_PRIVATE_DIRECTORY_REQUIRED')
    pilot.qualify_directory(directory)
    report={'scope':'PRIVATE_EXISTING_VPS_V1_UPDATE','status':'STOP','phase':'local_preflight','source_commit':options.source,
            'package_sha256':PACKAGE_SHA,'package_commit':'bc53775b08dc','migrations':[],'real_accounts':'NONE',
            'ionos':'UNCHANGED','pages':'UNCHANGED','gpg':'NOT_USED','mail':'NOT_SENT',
            'backup':'NOT_RUN','restore':'NOT_RUN','deployment':'NOT_RUN'}
    root=tunnel=None
    try:
        report['phase']='package_validation'
        data=fixture();content=payload();resume=None
        if options.resume:
            report['phase']='accepted_resume_recovery'
            previous,resume,needles=resume_material(options.resume)
            report.update(backup='PASS',restore='PASS',backup_restore_reused=True,acceptance_reused_from=options.resume,
                          acceptance_receipt_sha256=RESUME_SHA,cal1='PASS',mfa_rbac='PASS',
                          checks=previous['checks'],v1_checks=previous['v1_checks'],native_checks_repeated=False,
                          user_management=previous['user_management'],invitation_workflow=previous['invitation_workflow'],
                          onboarding=previous['onboarding'],postgres_persistence=previous['postgres_persistence'],restart=previous['restart'])
        report['phase']='accepted_public_ca'
        ca=accepted_ca()
        report['phase']='private_tunnel'
        with socket.socket() as check:occupied=check.connect_ex(('127.0.0.1',8447))==0
        if not occupied:
            tunnel=subprocess.Popen([*backup.SSH[:-1],'-N','-o','ExitOnForwardFailure=yes','-L','127.0.0.1:8447:127.0.0.1:8443',backup.SSH[-1]],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        report['phase']='strict_tls_readiness';wait_ready(ca)
        report['phase']='strict_tls_leaf';verify_leaf(ca)
        report['phase']='strict_tls_negative_controls';pilot.tls_negatives(ca)
        policy=directory/'firefox-policy.json';policy.write_bytes(canonical({'policies':{'Certificates':{'Install':[str(ca)]},'DisableTelemetry':True}}))
        os.environ['PLAYWRIGHT_FIREFOX_POLICIES_JSON']=str(policy)
        root=backup.RootSession(bootstrap_source=BOOTSTRAP,progress=lambda phase:report.update(phase=phase),reviewed_sources={
            'preflight':(SCRIPTS/'staging_readonly_preflight.py').read_text(encoding='utf8'),
            'agent':(SCRIPTS/'staging_snapshot_agent.py').read_text(encoding='utf8'),
            'legacy':(SCRIPTS/'vps_pilot_agent.py').read_text(encoding='utf8'),
            'update':(SCRIPTS/'vps_update_agent.py').read_text(encoding='utf8')})
        report['phase']='current_remote_preflight'
        if resume:
            report['phase']='resume_verification_and_runtime_switch';report['deployment']='RESUME_REQUESTED'
            report['stage']=root.request('resume',**content,fixture=data,**resume)
            print('PASS | Accepted current backup/restore and native checks reused; original rows and staged package verified.',flush=True)
            report['deployment']='REUSED_PENDING_FINAL_ACCEPTANCE';wait_ready(ca)
            verify_login_shell(directory);report['resume_login_shell']='PASS'
            report['phase']='resume_postflight';report['postflight']=root.request('finalize_resume',secret_needles=needles)
        else:
            current=root.request('preflight');configuration=current.pop('configuration')
            report['preflight']=current
            config_sha,config_copy=private_recovery(directory,'original-configuration.json.dpapi',canonical(configuration));del config_copy,configuration
            report['configuration_ciphertext_sha256']=config_sha
            report['phase']='current_backup_restore'
            capture=root.request('capture');dump=base64.b64decode(capture.pop('dump'),validate=True)
            require(sha(dump)==capture['dump_sha256'],'CURRENT_DUMP_TRANSFER_HASH')
            dump_sha,recovered=private_recovery(directory,'database.dump.dpapi',dump);del dump
            baseline_sha,_=private_recovery(directory,'baseline.json.dpapi',canonical(capture))
            report.update(backup='PASS',ciphertext_sha256=dump_sha,baseline_ciphertext_sha256=baseline_sha)
            altered=bytearray((directory/'database.dump.dpapi').read_bytes());altered[-1]^=1
            rejected=subprocess.run([sys.executable,'-I',str(SCRIPTS/'windows_dpapi.py'),'--decrypt-stdin'],input=altered,capture_output=True,timeout=30)
            require(rejected.returncode!=0 and not rejected.stdout,'DPAPI_TAMPER_MUST_FAIL')
            result=root.request('restore',dump=base64.b64encode(recovered).decode(),encrypted_copy_verified=True,ciphertext_sha256=dump_sha)
            del recovered
            require(result['status']=='PASS' and result['probe_removed'],'CURRENT_RESTORE_REQUIRED')
            report.update(restore='PASS',restore_proof=result)
            print('PASS | Current populated reference backup and exact isolated restore; original data unchanged.',flush=True)
            pilot.protected_copy(directory,'owned-synthetic-logins.json.dpapi',canonical(data))
            report['phase']='v1_installation';report['stage']=root.request('stage',**content,fixture=data,protected_configuration_sha256=config_sha)
            report['deployment']='INSTALLED_PENDING_ACCEPTANCE';wait_ready(ca)
            report['phase']='native_acceptance'
            private=pilot.acceptance.run(root,data,ca,directory,report)
            private=v1.run(root,data,ca,directory,report,private,pilot.acceptance)
            pilot.protected_copy(directory,'owned-synthetic-recovery.json.dpapi',canonical(private))
            needles=[x['password'] for x in data['accounts'].values()]+[x['password'] for x in data['invites'].values()]
            needles += [v['totp'] for v in private.values()]+[code for v in private.values() for code in v['recovery']]
            report['phase']='compensation_postflight';report['postflight']=root.request('commit',secret_needles=needles)
        wait_ready(ca);verify_leaf(ca)
        import io,zipfile
        with zipfile.ZipFile(PACKAGE) as archive:
            wheel=next(n for n in archive.namelist() if n.endswith('.whl'))
            with zipfile.ZipFile(io.BytesIO(archive.read(wheel))) as application:
                expected=application.read('competence_hub_api/portal_ui/user-management.js')
        require(pilot.acceptance.HTTPS(ca).call('/portal/user-management.js')[2]==expected,'V1_FINAL_RUNTIME_ASSET_MISMATCH')
        closed=pilot.acceptance.HTTPS(ca).call('/api/v1/admin/users/invitations','POST',{})
        require(closed[0]==503 and json.loads(closed[2]).get('code')=='invitation_delivery_unavailable','FINAL_DELIVERY_MUST_BE_CLOSED')
        root.request('accept');report['server_commit']='ACKNOWLEDGED'
        root.request('close');root.close();root=None
        report.update(status='PASS',phase='complete',deployment='PASS',tls='PASS',completed_at_utc=datetime.now(timezone.utc).isoformat())
        print('VPS_V1_UPDATE=PASS BACKUP_RESTORE=PASS MFA_RBAC=PASS CAL1=PASS REFERENCE=PASS SERVICES=PASS',flush=True)
        print('Protected access: https://localhost:8447/portal/ . Existing reference accounts preserved; no real invitations.',flush=True)
    except BaseException as error:
        report['failure_type']=type(error).__name__
        if isinstance(error,backup.protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+',str(error)):report['failure_code']=str(error)
        if root is not None:report['remote_failure']=getattr(root,'last_failure',None)
        raise
    finally:
        if root is not None:
            try:report['close']=root.request('close')
            except Exception:report['remote_failure']=getattr(root,'last_failure',None)
            finally:root.close()
        output=ROOT/'release-artifacts/vps-v1-update';output.mkdir(exist_ok=True)
        path=output/(directory.name+'.json')
        with path.open('xb') as stream:stream.write(canonical(report))
        print('REPORT='+str(path),flush=True)
        if report['status']=='PASS' and tunnel is not None:
            try:input('Enter closes only this local tunnel; keep open while viewing the private pilot. ')
            except (EOFError,KeyboardInterrupt):pass
        if tunnel is not None:
            tunnel.terminate()
            try:tunnel.wait(timeout=10)
            except subprocess.TimeoutExpired:tunnel.kill();tunnel.wait()
        os.environ.pop('PLAYWRIGHT_FIREFOX_POLICIES_JSON',None)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--quiet',action='store_true')
    parser.add_argument('--source',required=True);parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--resume',default='')
    try:main(parser.parse_args())
    except BaseException as error:
        code=str(error) if isinstance(error,backup.protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+',str(error)) else type(error).__name__
        print('VPS_V1_UPDATE=STOP CODE='+code+' NO_AUTOMATIC_RETRY=TRUE',flush=True);raise SystemExit(1) from None
