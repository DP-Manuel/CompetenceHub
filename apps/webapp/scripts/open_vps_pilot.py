"""Private existing synthetic login only. No installer, sudo, seed or secret output."""
import argparse
from email.utils import parsedate_to_datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
from uuid import UUID

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('existing_pilot_access',Path(__file__).with_name('run_vps_update.py'))
update=importlib.util.module_from_spec(spec);spec.loader.exec_module(update)
pilot=update.pilot
require=update.require
ROLES=('admin','reviewer','coach','coach_two')
EXPECTED={'admin':'admin','reviewer':'calendar_reviewer','coach':'coach','coach_two':'coach'}
TITLES={'admin':'Admin','reviewer':'Pr\u00fcfer','coach':'Coach 1','coach_two':'Coach 2'}
FINAL_RUN='eed9aed9a83c45fd948203e04a53c824'
FINAL_SHA='d5f4847ebc852c19dcc8775f3e443a58ed32e67d794b431ff87452e1a25f11d0'
V1_ASSET_SHA='e75971a7bd3cdd97459b72ad78605a8b6342b41a8886a6a4a1186ae7405737ab'


def validate_logins(data,private):
    require(set(data['accounts'])==set(ROLES) and set(private)==set(ROLES),'EXACT_SYNTHETIC_ROLES_REQUIRED')
    ids=[]
    for key in ROLES:
        item=data['accounts'][key];identifier=UUID(item['id']);ids.append(identifier)
        require(item['email']=='synthetic-vps-'+identifier.hex+'@example.invalid'
                and item['role']==EXPECTED[key] and isinstance(item['password'],str) and len(item['password'])>=20,
                'SYNTHETIC_LOGINS_ONLY')
        require(isinstance(private[key]['totp'],str) and re.fullmatch('[A-Z2-7]{16,128}',private[key]['totp']),
                'EXISTING_SYNTHETIC_MFA_REQUIRED')
    require(len(set(ids))==4,'DISTINCT_SYNTHETIC_LOGINS_REQUIRED')


def read_existing_logins():
    directory=Path(os.environ['LOCALAPPDATA'])/'CompetenceHub/pilot-runs'/update.ACCEPTED_RUN
    files=[directory/name for name in ('synthetic-logins.json.dpapi','synthetic-mfa-recovery.json.dpapi')]
    # Exact operator-owned paths only, checked without requiring BitLocker admin APIs.
    script="""$ErrorActionPreference='Stop';try {
 . '__ACL__'
 foreach($p in @('__DIR__','__LOGIN__','__MFA__')) {
  $null=Assert-StagingExternalPath $p
  if($p -eq '__DIR__'){Assert-StagingPrivateAcl $p -Directory}else{Assert-StagingPrivateAcl $p}
 }
}catch{exit 1}"""
    for old,value in {'__ACL__':pilot.SCRIPTS/'initialize-staging-operator-config.ps1','__DIR__':directory,
                      '__LOGIN__':files[0],'__MFA__':files[1]}.items():script=script.replace(old,str(value).replace("'","''"))
    pilot.powershell(script)
    values=[]
    for path in files:
        require(path.is_file() and not path.is_symlink(),'EXISTING_PRIVATE_LOGIN_COPY_REQUIRED')
        sealed=path.read_bytes();digest=update.sha(sealed)
        raw=update.backup.checked(sys.executable,'-I',str(pilot.SCRIPTS/'windows_dpapi.py'),'--decrypt-stdin',data=sealed,timeout=30)
        values.append(json.loads(raw))
        require(update.sha(path.read_bytes())==digest,'PRIVATE_LOGIN_COPY_CHANGED')
    validate_logins(*values)
    return values


def accepted_access():
    raw=(ROOT/'release-artifacts/vps-v1-update'/(FINAL_RUN+'.json')).read_bytes()
    require(update.sha(raw)==FINAL_SHA,'ACCEPTED_V1_RECEIPT_CHANGED')
    record=json.loads(raw)
    require(record['status']==record['deployment']=='PASS' and record['server_commit']=='ACKNOWLEDGED',
            'ACCEPTED_V1_REQUIRED')
    return update.accepted_ca()


def verify_access_runtime(ca):
    status,_,raw=pilot.acceptance.HTTPS(ca).call('/portal/user-management.js')
    require(status==200 and update.sha(raw)==V1_ASSET_SHA,'ACCEPTED_V1_RUNTIME_REQUIRED')


def open_roles(data,private,ca,directory,*,headless=False):
    status,headers,_=pilot.acceptance.HTTPS(ca).call('/health/ready')
    require(status==200,'PRIVATE_PILOT_NOT_READY')
    server=parsedate_to_datetime(headers['Date']).timestamp()
    offset=server-time.time()
    print('Opening four existing synthetic roles. Waiting at most 31 seconds for a fresh MFA window; no password input needed.',flush=True)
    time.sleep(31-(server%30))
    phase=['browser','launch']
    def progress(role,step):
        require(role in (*ROLES,'browser','calendar') and step in
                ('launch','initial_session','password','mfa','portal','public_view'),'INVALID_ACCESS_STEP')
        phase[:]=[role,step]
        print('PILOT_ACCESS_STEP ROLE='+role+' STEP='+step,flush=True)
    try:
        demo=pilot.open_demo(data,private,offset,headless=headless,roles=ROLES,progress=progress)
    except BaseException as error:
        from playwright.sync_api import TimeoutError as BrowserTimeout
        if isinstance(error,BrowserTimeout):
            raise update.backup.protocol.SnapshotStop('BROWSER_TIMEOUT_'+phase[0].upper()+'_'+phase[1].upper()) from None
        raise
    try:
        require(len(demo[1].contexts)==len(ROLES)+1,'FOUR_ISOLATED_WINDOWS_REQUIRED')
        expected={data['accounts'][key]['id']:key for key in ROLES};seen=set()
        for context in demo[1].contexts:
            pages=[p for p in context.pages if p.url.split('#',1)[0].rstrip('/')==pilot.acceptance.ORIGIN+'/portal']
            if not pages:continue
            status,_,raw=pilot.acceptance.HTTPS(ca,context).call(pilot.acceptance.ACCESS+'/session')
            require(status==200,'EXACT_ROLE_LOGIN_FAILED')
            actor=json.loads(raw)['user'];key=expected.get(actor['id'])
            require(key is not None and key not in seen and actor['roles']==[EXPECTED[key]],'EXACT_ROLE_LOGIN_FAILED')
            seen.add(key)
            pages[0].evaluate('label=>{document.title=label+" | Competence Hub Test"}',TITLES[key])
        require(seen==set(ROLES),'FOUR_ISOLATED_WINDOWS_REQUIRED')
        return demo
    except BaseException:
        demo[1].close();demo[0].stop();raise


def main(options):
    require(os.name=='nt' and options.open and sys.stdin.isatty(),'PRIVATE_WINDOWS_ACCESS_REQUIRED')
    require(update.backup.checked('git','-C',str(ROOT),'rev-parse','HEAD').decode().strip()==options.source,'SOURCE_CHANGED')
    directory=options.directory
    require(directory.parent.resolve()==(Path(os.environ['LOCALAPPDATA'])/'CompetenceHub/pilot-views').resolve()
            and re.fullmatch('[a-f0-9]{32}',directory.name) and directory.is_dir() and not any(directory.iterdir()),
            'OWN_EMPTY_PRIVATE_VIEW_DIRECTORY_REQUIRED')
    tunnel=demo=None
    names=('PLAYWRIGHT_FIREFOX_POLICIES_JSON','TMP','TEMP')
    previous={name:os.environ.get(name) for name in names}
    try:
        ca=accepted_access()
        with socket.socket() as check:occupied=check.connect_ex(('127.0.0.1',8447))==0
        if not occupied:
            tunnel=subprocess.Popen([*update.backup.SSH[:-1],'-N','-o','ExitOnForwardFailure=yes','-L',
                '127.0.0.1:8447:127.0.0.1:8443',update.backup.SSH[-1]],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        update.wait_ready(ca);update.verify_leaf(ca);verify_access_runtime(ca)
        data,private=read_existing_logins()
        policy=directory/'firefox-policy.json'
        policy.write_bytes(update.canonical({'policies':{'Certificates':{'Install':[str(ca)]},'DisableTelemetry':True}}))
        os.environ.update(PLAYWRIGHT_FIREFOX_POLICIES_JSON=str(policy),TMP=str(directory),TEMP=str(directory))
        demo=open_roles(data,private,ca,directory)
        print('PILOT_ACCESS=PASS ADMIN=OPEN REVIEWER=OPEN COACH_1=OPEN COACH_2=OPEN PUBLIC_CALENDAR=OPEN',flush=True)
        print('Keep this terminal open. Enter closes these test windows and only a tunnel created by this starter. VPS services stay running.',flush=True)
        try:input()
        except (EOFError,KeyboardInterrupt):pass
    finally:
        if demo is not None:demo[1].close();demo[0].stop()
        if tunnel is not None:
            tunnel.terminate()
            try:tunnel.wait(timeout=10)
            except subprocess.TimeoutExpired:tunnel.kill();tunnel.wait()
        for name,value in previous.items():
            if value is None:os.environ.pop(name,None)
            else:os.environ[name]=value


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--open',action='store_true')
    parser.add_argument('--source',required=True);parser.add_argument('--directory',type=Path,required=True)
    try:main(parser.parse_args())
    except BaseException as error:
        code=str(error) if isinstance(error,update.backup.protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+',str(error)) else type(error).__name__
        print('PILOT_ACCESS=STOP CODE='+code+' NO_AUTOMATIC_RETRY=TRUE',flush=True);raise SystemExit(1) from None
