import importlib.util
import io
import json
from pathlib import Path
import subprocess
import zipfile
from types import SimpleNamespace

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('synthetic_access_test',ROOT/'apps/webapp/scripts/open_vps_pilot.py')
access=importlib.util.module_from_spec(spec);spec.loader.exec_module(access)
Stop=access.update.backup.protocol.SnapshotStop


def synthetic():
    return access.pilot.fixture(),{role:{'totp':'A'*32,'recovery':['SYNTHETIC-ONLY']} for role in access.ROLES}


@pytest.mark.parametrize('change',['email','role','duplicate','missing','mfa'])
def test_only_exact_existing_synthetic_roles_are_admitted(change):
    data,private=synthetic();access.validate_logins(data,private)
    if change=='email':data['accounts']['admin']['email']='real@example.org'
    if change=='role':data['accounts']['coach']['role']='admin'
    if change=='duplicate':data['accounts']['coach_two']=dict(data['accounts']['coach'])
    if change=='missing':private.pop('reviewer')
    if change=='mfa':private['admin']['totp']='invalid-secret'
    with pytest.raises(Stop):access.validate_logins(data,private)


def test_original_copies_are_read_only_and_values_never_printed(tmp_path,monkeypatch,capsys):
    data,private=synthetic()
    directory=tmp_path/'CompetenceHub/pilot-runs'/access.update.ACCEPTED_RUN
    directory.mkdir(parents=True)
    for name,value in [('synthetic-logins.json.dpapi',data),('synthetic-mfa-recovery.json.dpapi',private)]:
        (directory/name).write_bytes(b'SYNTHETIC-SEAL'+json.dumps(value).encode())
    before={p.name:p.read_bytes() for p in directory.iterdir()}
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path))
    acl=[];monkeypatch.setattr(access.pilot,'powershell',lambda script:acl.append(script))
    def decrypt(*args,**kwargs):
        assert '--decrypt-stdin' in args and kwargs['timeout']==30
        return kwargs['data'][len(b'SYNTHETIC-SEAL'):]
    monkeypatch.setattr(access.update.backup,'checked',decrypt)
    result=access.read_existing_logins()
    assert result==[data,private] and len(acl)==1
    assert before=={p.name:p.read_bytes() for p in directory.iterdir()}
    assert not capsys.readouterr().out


@pytest.mark.parametrize('wrong_role',[False,True])
def test_auto_login_uses_fresh_mfa_and_exact_isolated_roles(monkeypatch,wrong_role):
    data,private=synthetic();titles={}
    contexts=[SimpleNamespace(key=role,pages=[SimpleNamespace(url=access.pilot.acceptance.ORIGIN+'/portal/',
              evaluate=lambda code,label,key=role:titles.update({key:label}))]) for role in reversed(access.ROLES)]
    contexts.insert(0,SimpleNamespace(pages=[SimpleNamespace(url=access.pilot.acceptance.ORIGIN+'/portal/calendar-public.html')]))
    closed=[];demo=(SimpleNamespace(stop=lambda:closed.append('driver')),SimpleNamespace(contexts=contexts,close=lambda:closed.append('browser')))
    class HTTPS:
        def __init__(self,ca,context=None):self.context=context
        def call(self,path):
            if not self.context:return 200,{'Date':'Wed, 11 Nov 2026 12:00:00 GMT'},b''
            role='internal' if wrong_role else access.EXPECTED[self.context.key]
            return 200,{},json.dumps({'user':{'roles':[role],'id':data['accounts'][self.context.key]['id']}}).encode()
    monkeypatch.setattr(access.pilot.acceptance,'HTTPS',HTTPS)
    sleeps=[];monkeypatch.setattr(access.time,'sleep',sleeps.append)
    monkeypatch.setattr(access.time,'time',lambda:1794398400)
    def open_demo(*args,**kwargs):
        assert args[:2]==(data,private) and kwargs['roles']==access.ROLES and kwargs['headless']
        kwargs['progress']('admin','password')
        return demo
    monkeypatch.setattr(access.pilot,'open_demo',open_demo)
    if wrong_role:
        with pytest.raises(Stop,match='EXACT_ROLE_LOGIN_FAILED'):access.open_roles(data,private,None,None,headless=True)
        assert closed==['browser','driver']
    else:
        assert access.open_roles(data,private,None,None,headless=True)==demo and not closed
        assert titles==access.TITLES
    assert len(sleeps)==1 and 1<=sleeps[0]<=31


@pytest.mark.parametrize('args,expected',[
    ([],b'PILOT_ACCESS=NOT_OPENED'),
    (['-Open','-ExpectedSourceCommit','0'*40],b'PILOT_ACCESS=STOP CODE=SOURCE_CHANGED'),
])
def test_access_entry_has_no_side_effects_without_explicit_current_open(args,expected):
    result=subprocess.run(['pwsh','-NoProfile','-File',str(ROOT/'deploy/scripts/open-vps-pilot.ps1'),*args],capture_output=True,timeout=30)
    assert expected in result.stdout


def test_access_does_not_call_installer_root_or_recovery_consumption():
    source=(ROOT/'apps/webapp/scripts/open_vps_pilot.py').read_text(encoding='utf8')
    assert 'RootSession(' not in source and 'existing_keys(' not in source and 'package_payload(' not in source
    assert "['recovery'].pop" not in source and 'getpass' not in source
    assert 'ignore_https_errors' not in source and 'IgnoreHTTPSErrors' not in source


def test_current_runtime_pin_matches_accepted_wheel(monkeypatch):
    with zipfile.ZipFile(access.update.PACKAGE) as z:
        with zipfile.ZipFile(io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('.whl'))))) as wheel:
            raw=wheel.read('competence_hub_api/portal_ui/calendar-form.mjs')
    assert access.update.sha(raw)==access.RUNTIME_ASSET_SHA
    monkeypatch.setattr(access.pilot.acceptance,'HTTPS',lambda ca:SimpleNamespace(call=lambda path:(200,{},raw)))
    access.verify_access_runtime(None)


def test_wrong_current_runtime_is_rejected_before_login(monkeypatch):
    monkeypatch.setattr(access.pilot.acceptance,'HTTPS',lambda ca:SimpleNamespace(call=lambda path:(404,{},b'NOT V1')))
    with pytest.raises(Stop,match='ACCEPTED_V11_RUNTIME_REQUIRED'):access.verify_access_runtime(None)


def test_v11_actual_receipt_hash_is_bound_before_private_access(monkeypatch):
    monkeypatch.setattr(Path,'read_bytes',lambda path:b'changed-public-receipt')
    with pytest.raises(Stop,match='ACCEPTED_V11_RECEIPT_CHANGED'):access.accepted_access()


@pytest.mark.parametrize('field',['status','deployment','cal1','v11_ux','server_commit','package_sha256','package_commit',None])
def test_v11_receipt_rejects_wrong_acceptance_or_release(monkeypatch,field):
    record={'status':'PASS','deployment':'PASS','cal1':'PASS','v11_ux':'PASS','server_commit':'ACKNOWLEDGED',
            'package_sha256':access.update.PACKAGE_SHA,'package_commit':access.update.PACKAGE_COMMIT}
    if field:record[field]='WRONG'
    raw=json.dumps(record).encode()
    monkeypatch.setattr(Path,'read_bytes',lambda path:raw);monkeypatch.setattr(access,'FINAL_SHA',access.update.sha(raw))
    monkeypatch.setattr(access.update,'accepted_ca',lambda:'public-ca-only')
    if field:
        with pytest.raises(Stop,match='ACCEPTED_V11_REQUIRED'):access.accepted_access()
    else:assert access.accepted_access()=='public-ca-only'


def test_browser_timeout_has_safe_step_without_exception_or_secret_output(monkeypatch,capsys):
    from playwright.sync_api import TimeoutError as BrowserTimeout
    data,private=synthetic()
    monkeypatch.setattr(access.pilot.acceptance,'HTTPS',lambda ca:SimpleNamespace(
        call=lambda path:(200,{'Date':'Wed, 11 Nov 2026 12:00:00 GMT'},b'')))
    monkeypatch.setattr(access.time,'sleep',lambda seconds:None)
    def fail(*args,**kwargs):
        kwargs['progress']('reviewer','mfa')
        raise BrowserTimeout('SYNTHETIC-SENSITIVE-EXCEPTION-MUST-NOT-PRINT')
    monkeypatch.setattr(access.pilot,'open_demo',fail)
    with pytest.raises(Stop,match='^BROWSER_TIMEOUT_REVIEWER_MFA$'):
        access.open_roles(data,private,None,None,headless=True)
    output=capsys.readouterr().out
    assert 'ROLE=reviewer STEP=mfa' in output
    assert 'SENSITIVE' not in output and private['reviewer']['totp'] not in output


def test_private_role_guide_contains_confirmed_identifiers_but_no_credentials(tmp_path,monkeypatch,capsys):
    data,private=synthetic();calls=[]
    monkeypatch.setattr(access.pilot,'powershell',lambda script,**options:calls.append((script,options['data'])))
    path=access.private_role_guide(data,tmp_path)
    script,raw=calls[0];text=raw.decode('utf8')
    assert path.name=='PORTAL_TESTZUGAENGE.local.md'
    assert 'New-StagingPrivateFileStream' in script and 'Assert-StagingPrivateAcl' in script
    for role in access.ROLES:
        assert data['accounts'][role]['email'] in text
        assert data['accounts'][role]['password'] not in text and private[role]['totp'] not in text
    assert not capsys.readouterr().out
