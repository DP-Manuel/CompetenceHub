"""V1.2 is an explicit incremental profile, never a historical installer retry."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import zipfile

import pytest

ROOT=Path(__file__).resolve().parents[3]


def load(path,configure=True):
    spec=importlib.util.spec_from_file_location('v12_bound_profile',ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    if configure:value.configure_v12()
    return value


def test_exact_candidate_previous_wheel_and_linux_hashes():
    client=load('apps/webapp/scripts/run_vps_update.py');agent=load('deploy/scripts/vps_update_agent.py')
    assert client.PACKAGE_SHA==agent.PACKAGE_SHA==client.sha(client.PACKAGE.read_bytes())
    assert client.PACKAGE_COMMIT==agent.SOURCE=='5a555e9a9aae'
    assert client.PROFILE=='V12' and client.REPORT_DIRECTORY=='vps-v12-update'
    assert client.sha((client.WHEELS/'INVENTORY.json').read_bytes())==client.INVENTORY_SHA
    with zipfile.ZipFile(ROOT/'release-artifacts/webapp/competence-hub-webapp-0.1.0-38153c12159e-20261113T125945Z.zip') as archive:
        assert client.sha(archive.read(next(n for n in archive.namelist() if n.endswith('.whl'))))==agent.OLD_WHEEL_SHA
    assert agent.PREVIOUS_RUNTIME_DROP.name=='22-v11-runtime.conf'
    assert [p.name for p in agent.EXTRA_PREVIOUS_DROPS]==['20-v1-runtime.conf']
    assert agent.RUNTIME_DROP.name=='24-v12-runtime.conf'
    assert not agent.SYNTHETIC_INVITATION_CAPTURE
    assert "u['configure_v12']()" in client.BOOTSTRAP


def test_previous_receipt_bound_before_any_ca_or_credential_access(monkeypatch):
    client=load('apps/webapp/scripts/run_vps_update.py')
    monkeypatch.setattr(Path,'read_bytes',lambda path:b'changed-public-evidence')
    with pytest.raises(client.backup.protocol.SnapshotStop,match='ACCEPTED_PREVIOUS_V11_RECEIPT_REQUIRED'):
        client.accepted_ca()


def test_remote_acceptance_reuses_calendar_and_strict_shared_v12_cases(monkeypatch):
    client=load('apps/webapp/scripts/run_vps_update.py');calls=[];private={'owned':'synthetic'}
    monkeypatch.setattr(client.pilot.acceptance,'run',lambda *args,**kw:calls.append(kw) or private)
    monkeypatch.setattr(client,'module',lambda *args:SimpleNamespace(fill_legacy_datetime='date-only-adapter',
        run=lambda *args:calls.append(args[5]) or private))
    assert client.native_acceptance(None,{},None,None,{}) is private
    assert calls==[{'tour_counts':{'coach':9,'reviewer':7,'admin':6},'datetime_fill':'date-only-adapter'},private]


def test_final_runtime_requires_every_new_browser_asset(monkeypatch):
    client=load('apps/webapp/scripts/run_vps_update.py');assets={}
    with zipfile.ZipFile(client.PACKAGE) as archive:
        with zipfile.ZipFile(io.BytesIO(archive.read(next(n for n in archive.namelist() if n.endswith('.whl'))))) as wheel:
            for name in wheel.namelist():
                if name.startswith('competence_hub_api/portal_ui/') and not name.endswith('/'):
                    assets['/portal/'+name.split('/portal_ui/')[1]]=wheel.read(name)
    seen=[]
    def call(path):seen.append(path);return 200,{},assets[path]
    monkeypatch.setattr(client.pilot.acceptance,'HTTPS',lambda ca:SimpleNamespace(call=call))
    client.verify_final_assets(None)
    assert len(seen)==13
    assert {'/portal/calendar-picker.js','/portal/calendar-dialogs.js','/portal/datepicker-v134.js','/portal/datepicker-de-v134.js','/portal/datepicker-v134.css'}<=set(seen)
    assets['/portal/calendar-dialogs.js']=b'old'
    with pytest.raises(client.backup.protocol.SnapshotStop,match='FINAL_RUNTIME_ASSET_MISMATCH'):
        client.verify_final_assets(None)


def test_v12_rollback_removes_only_owned_override_not_v1_or_v11(tmp_path,monkeypatch):
    agent=load('deploy/scripts/vps_update_agent.py')
    snapshot=load('deploy/scripts/staging_snapshot_agent.py',False)
    old=tmp_path/'20-v1-runtime.conf';previous=tmp_path/'22-v11-runtime.conf';new=tmp_path/'24-v12-runtime.conf'
    old.write_bytes(b'v1');previous.write_bytes(b'v11');new.write_bytes(b'v12')
    monkeypatch.setattr(agent,'RUNTIME_DROP',new)
    monkeypatch.setattr(snapshot,'run',lambda *args,**kw:b'inactive' if 'show' in args else b'')
    value=agent.UpdateAgent(SimpleNamespace(),snapshot,SimpleNamespace());value.changed=value.runtime_drop_owned=True
    value.start_api=lambda:None;value.collect=lambda:{}
    assert value.rollback()['status']=='PASS'
    assert not new.exists() and old.read_bytes()==b'v1' and previous.read_bytes()==b'v11'


@pytest.mark.parametrize('mutation',['missing-v1','extra-drop','changed-v1','changed-v11'])
def test_both_predecessor_overrides_checked_before_private_files(tmp_path,monkeypatch,mutation):
    agent=load('deploy/scripts/vps_update_agent.py');snapshot=load('deploy/scripts/staging_snapshot_agent.py',False)
    drop=tmp_path/'drops';drop.mkdir();old=drop/'20-v1-runtime.conf';previous=drop/'22-v11-runtime.conf'
    v1=tmp_path/'v1';v11=tmp_path/'v11';v11.mkdir()
    old.write_bytes(agent.runtime_override(v1));previous.write_bytes(agent.runtime_override(v11))
    monkeypatch.setattr(agent,'DROP',drop);monkeypatch.setattr(agent,'PREVIOUS_RUNTIME_DROP',previous)
    monkeypatch.setattr(agent,'PREVIOUS_RELEASE',v11);monkeypatch.setattr(agent,'EXTRA_PREVIOUS_DROPS',{old:v1})
    monkeypatch.setattr(agent,'RELEASE',tmp_path/'absent')
    if mutation=='missing-v1':old.unlink()
    elif mutation=='extra-drop':(drop/'unknown.conf').write_bytes(b'unknown')
    elif mutation=='changed-v1':old.write_bytes(b'changed')
    else:previous.write_bytes(b'changed')
    original=Path.lstat
    monkeypatch.setattr(Path,'lstat',lambda path:SimpleNamespace(st_mode=0o100644,st_uid=0) if path in (old,previous) and path.exists() else original(path))
    value=agent.UpdateAgent(SimpleNamespace(),snapshot,SimpleNamespace());value.collect=lambda:{}
    value.private_file=lambda *args:pytest.fail('No private access on predecessor mismatch')
    with pytest.raises(snapshot.SnapshotStop,match='EXACT_PREVIOUS_V1_RUNTIME_REQUIRED|PREVIOUS_V1_OVERRIDE_CHANGED'):
        value.preflight({})


@pytest.mark.parametrize('arguments,expected',[
    ([], 'VPS_V12_UPDATE=NOT_EXECUTED'),
    (['-Execute'],'QUIET_REFERENCE_WINDOW_REQUIRED'),
    (['-Execute','-AcknowledgeQuietPilot','-ExpectedSourceCommit','0'*40],'SOURCE_CHANGED_NO_SERVER_ACTION'),
])
def test_entry_fails_closed_without_real_actions(arguments,expected):
    result=subprocess.run(['pwsh','-NoProfile','-File',str(ROOT/'deploy/scripts/run-vps-v12-update.ps1'),*arguments],capture_output=True,timeout=30)
    assert expected in result.stdout.decode('utf8')


def test_v12_remote_contexts_never_opt_out_of_tls():
    source=(ROOT/'apps/webapp/scripts/vps_v12_acceptance.py').read_text(encoding='utf8')
    assert 'strict_tls=True' in source and 'ignore_https_errors' not in source
    assert "has_touch=True" in source and '.tap()' in source


def test_shared_remote_cases_load_with_actual_isolated_operator_flags():
    path=ROOT/'apps/webapp/scripts/vps_v12_acceptance.py'
    code="import importlib.util;from pathlib import Path;p=Path("+repr(str(path))+");s=importlib.util.spec_from_file_location('isolated_v12',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);assert callable(m.exercise)"
    result=subprocess.run([sys.executable,'-I','-X','utf8','-c',code],capture_output=True,timeout=30)
    assert result.returncode==0,result.stderr.decode('utf8')
