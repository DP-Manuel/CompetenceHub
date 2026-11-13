"""Bound incremental update profile; historical V1 defaults remain unchanged."""
import importlib.util
import io
from pathlib import Path
import subprocess
from types import SimpleNamespace
import zipfile

import pytest

ROOT=Path(__file__).resolve().parents[3]


def load(path):
    spec=importlib.util.spec_from_file_location('v11_profile_test',ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.configure_v11();return module


def test_exact_v11_package_and_previous_v1_rollback_match():
    client=load('apps/webapp/scripts/run_vps_update.py');agent=load('deploy/scripts/vps_update_agent.py')
    assert client.PACKAGE_SHA==agent.PACKAGE_SHA==client.sha(client.PACKAGE.read_bytes())
    assert client.PACKAGE_COMMIT==agent.SOURCE=='38153c12159e'
    assert client.PROFILE=='V11' and client.REPORT_DIRECTORY=='vps-v11-update'
    assert client.sha((client.WHEELS/'INVENTORY.json').read_bytes())==client.INVENTORY_SHA
    with zipfile.ZipFile(ROOT/'release-artifacts/webapp/competence-hub-webapp-0.1.0-bc53775b08dc-20261110T184433Z.zip') as archive:
        wheel=next(name for name in archive.namelist() if name.endswith('.whl'))
        assert client.sha(archive.read(wheel))==agent.OLD_WHEEL_SHA
    assert agent.PREVIOUS_RUNTIME_DROP.name=='20-v1-runtime.conf'
    assert agent.RUNTIME_DROP.name=='22-v11-runtime.conf'
    assert not agent.SYNTHETIC_INVITATION_CAPTURE
    assert "u['configure_v11']()" in client.BOOTSTRAP


def test_v11_uses_existing_cal_and_ux_without_invitation_capture(monkeypatch):
    client=load('apps/webapp/scripts/run_vps_update.py');calls=[]
    private={'synthetic':'only'}
    def cal(*args,**kwargs):calls.append(kwargs['tour_counts']);return private
    def ux(*args):calls.append(args[5]);return private
    monkeypatch.setattr(client.pilot.acceptance,'run',cal)
    monkeypatch.setattr(client.v1,'run',lambda *args:pytest.fail('No repeated invitation capture'))
    monkeypatch.setattr(client,'module',lambda *args:SimpleNamespace(run=ux))
    assert client.native_acceptance(None,{},None,None,{}) is private
    assert calls==[{'coach':9,'reviewer':7,'admin':6},private]


def test_v11_historical_resume_blocked_before_directory_access(monkeypatch):
    client=load('apps/webapp/scripts/run_vps_update.py')
    monkeypatch.setattr(client.os,'name','nt');monkeypatch.setattr(client.sys.stdin,'isatty',lambda:True)
    with pytest.raises(client.backup.protocol.SnapshotStop,match='V11_RESUME_REQUIRES_SEPARATE_EVIDENCE'):
        client.main(SimpleNamespace(execute=True,quiet=True,resume=client.RESUME_RUN))


def test_v11_changed_previous_receipt_stops_before_ca_or_private_files(monkeypatch):
    client=load('apps/webapp/scripts/run_vps_update.py')
    monkeypatch.setattr(Path,'read_bytes',lambda self:b'changed-public-receipt')
    with pytest.raises(client.backup.protocol.SnapshotStop,match='ACCEPTED_PREVIOUS_V1_RECEIPT_REQUIRED'):
        client.accepted_ca()


def test_final_runtime_compares_all_ux_assets_byte_for_byte(monkeypatch):
    client=load('apps/webapp/scripts/run_vps_update.py');assets={}
    with zipfile.ZipFile(client.PACKAGE) as archive:
        with zipfile.ZipFile(io.BytesIO(archive.read(next(name for name in archive.namelist() if name.endswith('.whl'))))) as wheel:
            for name in ('user-management.js','app.js','calendar-form.mjs','calendar-public.html','product-tour.js','product-tour.css','styles.css'):
                assets['/portal/'+name]=wheel.read('competence_hub_api/portal_ui/'+name)
    seen=[]
    def call(path):seen.append(path);return 200,{},assets[path]
    monkeypatch.setattr(client.pilot.acceptance,'HTTPS',lambda ca:SimpleNamespace(call=call))
    client.verify_final_assets(None)
    assert set(seen)==set(assets)
    assets['/portal/calendar-form.mjs']=b'old-asset'
    with pytest.raises(client.backup.protocol.SnapshotStop,match='FINAL_RUNTIME_ASSET_MISMATCH'):
        client.verify_final_assets(None)


def test_v11_rollback_removes_only_new_drop_and_keeps_previous(tmp_path,monkeypatch):
    agent=load('deploy/scripts/vps_update_agent.py')
    snapshot=load_protocol()
    drop=tmp_path/'22-v11-runtime.conf';previous=tmp_path/'20-v1-runtime.conf'
    drop.write_bytes(b'new');previous.write_bytes(b'original-v1')
    monkeypatch.setattr(agent,'RUNTIME_DROP',drop)
    monkeypatch.setattr(snapshot,'run',lambda *args,**kw:b'inactive' if 'show' in args else b'')
    value=agent.UpdateAgent(SimpleNamespace(),snapshot,SimpleNamespace())
    value.changed=value.runtime_drop_owned=True
    value.start_api=lambda:None;value.collect=lambda:{}
    result=value.rollback()
    assert result['status']=='PASS' and not result['source_restore_performed']
    assert not drop.exists() and previous.read_bytes()==b'original-v1'


def load_protocol():
    path=ROOT/'deploy/scripts/staging_snapshot_agent.py'
    spec=importlib.util.spec_from_file_location('v11_snapshot_test',path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


@pytest.mark.parametrize('arguments,expected',[
    ([], 'VPS_V11_UPDATE=NOT_EXECUTED'),
    (['-Execute'],'QUIET_REFERENCE_WINDOW_REQUIRED'),
    (['-Execute','-AcknowledgeQuietPilot','-ExpectedSourceCommit','0'*40],'SOURCE_CHANGED_NO_SERVER_ACTION'),
])
def test_actual_v11_entry_fails_closed_without_side_effects(arguments,expected):
    result=subprocess.run(['pwsh','-NoProfile','-File',str(ROOT/'deploy/scripts/run-vps-v11-update.ps1'),*arguments],capture_output=True,timeout=30)
    assert expected in result.stdout.decode('utf8')


def test_v11_preflight_rejects_extra_or_changed_drop_before_config_read(tmp_path,monkeypatch):
    agent=load('deploy/scripts/vps_update_agent.py');snapshot=load_protocol()
    drop=tmp_path/'drops';drop.mkdir();previous=drop/'20-v1-runtime.conf';previous.write_bytes(b'changed')
    monkeypatch.setattr(agent,'DROP',drop);monkeypatch.setattr(agent,'PREVIOUS_RUNTIME_DROP',previous)
    monkeypatch.setattr(agent,'RELEASE',tmp_path/'absent')
    value=agent.UpdateAgent(SimpleNamespace(),snapshot,SimpleNamespace());value.collect=lambda:{}
    value.private_file=lambda *args:pytest.fail('No private read before exact V1 runtime')
    extra=drop/'unexpected.conf';extra.write_bytes(b'unexpected')
    with pytest.raises(snapshot.SnapshotStop,match='EXACT_PREVIOUS_V1_RUNTIME_REQUIRED'):value.preflight({})
    extra.unlink()
    # Simulate trusted Unix metadata without reading any real private file.
    original=Path.lstat
    monkeypatch.setattr(Path,'lstat',lambda path:SimpleNamespace(st_mode=0o100644,st_uid=0) if path==previous else original(path))
    with pytest.raises(snapshot.SnapshotStop,match='PREVIOUS_V1_OVERRIDE_CHANGED'):value.preflight({})


@pytest.mark.parametrize('mode,owner',[(0o120777,0),(0o100666,0),(0o100644,1)])
def test_previous_override_bad_custody_rejected_before_contents(tmp_path,monkeypatch,mode,owner):
    agent=load('deploy/scripts/vps_update_agent.py');snapshot=load_protocol()
    drop=tmp_path/'drops';drop.mkdir();previous=drop/'20-v1-runtime.conf';previous.write_bytes(b'do-not-read')
    monkeypatch.setattr(agent,'DROP',drop);monkeypatch.setattr(agent,'PREVIOUS_RUNTIME_DROP',previous)
    monkeypatch.setattr(agent,'RELEASE',tmp_path/'absent')
    original=Path.lstat
    monkeypatch.setattr(Path,'lstat',lambda path:SimpleNamespace(st_mode=mode,st_uid=owner) if path==previous else original(path))
    monkeypatch.setattr(Path,'read_bytes',lambda path:pytest.fail('Do not read an untrusted override'))
    value=agent.UpdateAgent(SimpleNamespace(),snapshot,SimpleNamespace());value.collect=lambda:{}
    with pytest.raises(snapshot.SnapshotStop,match='PREVIOUS_V1_OVERRIDE_CUSTODY_REQUIRED'):value.preflight({})


def test_manual_access_error_does_not_misreport_accepted_deployment(monkeypatch,capsys):
    client=load('apps/webapp/scripts/run_vps_update.py');report={'deployment':'PASS'}
    def unavailable():raise ValueError('synthetic-sensitive-value-not-to-print')
    monkeypatch.setattr(client,'module',lambda *args:SimpleNamespace(read_existing_logins=unavailable))
    assert client.open_manual_access(None,None,report) is None
    assert report=={'deployment':'PASS','manual_access':'STOP','manual_access_code':'ValueError'}
    output=capsys.readouterr().out
    assert 'DEPLOYMENT=PASS' in output and 'sensitive' not in output


def test_manual_access_uses_existing_roles_and_identifier_only_guide(monkeypatch,tmp_path,capsys):
    client=load('apps/webapp/scripts/run_vps_update.py');report={};calls=[];demo=('driver','browser')
    access=SimpleNamespace(read_existing_logins=lambda:('synthetic-logins','synthetic-mfa'),
        open_roles=lambda *args:(calls.append(args) or demo),
        private_role_guide=lambda *args:tmp_path/'identifier-only-guide.md')
    monkeypatch.setattr(client,'module',lambda *args:access)
    assert client.open_manual_access('test-ca',tmp_path,report)==demo
    assert calls==[('synthetic-logins','synthetic-mfa','test-ca',tmp_path)]
    assert report['manual_access']=='PASS' and 'POST' not in capsys.readouterr().out


@pytest.mark.parametrize('initial',[0,1,2])
@pytest.mark.parametrize('target',[0,1,2])
def test_month_selection_waits_for_load_and_uses_month_identity(monkeypatch,initial,target):
    from datetime import datetime
    path=ROOT/'apps/webapp/scripts/vps_v11_acceptance.py'
    spec=importlib.util.spec_from_file_location('v11_month_test',path)
    ux=importlib.util.module_from_spec(spec);spec.loader.exec_module(ux)
    state={'month':initial,'loaded':False};labels=['November 2026','Dezember 2026','Januar 2027']
    class Control:
        def __init__(self,name):self.name=name
        def is_disabled(self):assert state['loaded'];return state['month']==0
        def click(self):
            assert state['loaded']
            state['month']+=-1 if self.name=='#previous' else 1
        def inner_text(self):assert state['loaded'];return labels[state['month']]
    class Assertion:
        def __init__(self,control):self.control=control
        def to_be_hidden(self,**kwargs):assert self.control.name=='#loading';state['loaded']=True
        def to_have_text(self,value):assert self.control.inner_text()==value
    page=SimpleNamespace(locator=Control,evaluate=lambda *args:labels[target])
    monkeypatch.setattr(ux,'expect',Assertion)
    ux.show_month(page,datetime(2026,11,20))
    assert state=={'month':target,'loaded':True}
