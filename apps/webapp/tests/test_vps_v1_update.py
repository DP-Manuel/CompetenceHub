import base64
from contextlib import nullcontext
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT=Path(__file__).resolve().parents[3]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


agent=load('v1_agent_test','deploy/scripts/vps_update_agent.py')
client=load('v1_client_test','apps/webapp/scripts/run_vps_update.py')
worker=load('v1_worker_test','deploy/scripts/vps_update_worker.py')
protocol=client.backup.protocol


def instance():return agent.UpdateAgent(SimpleNamespace(),protocol,SimpleNamespace())


def test_bound_package_and_original_runtime_match_accepted_releases():
    assert agent.PACKAGE_SHA==client.PACKAGE_SHA
    assert client.sha(client.PACKAGE.read_bytes())==client.PACKAGE_SHA
    assert agent.SOURCE=='bc53775b08dc'
    assert client.CA_SHA and agent.LEAF_SHA==client.LEAF_SHA
    import zipfile
    with zipfile.ZipFile(client.pilot.PACKAGE) as archive:
        wheel=next(name for name in archive.namelist() if name.endswith('.whl'))
        assert agent.OLD_WHEEL_SHA==client.sha(archive.read(wheel))


@pytest.mark.parametrize('name',['admin','reviewer','coach','coach_two'])
def test_owned_cohort_rejects_real_or_wrong_role_identity(name):
    f=client.fixture();worker.validate(f)
    f['accounts'][name]['email']='real@example.org'
    with pytest.raises(ValueError):worker.validate(f)


def test_owned_invitation_rate_cleanup_matches_actual_service_contract():
    from competence_hub_api.auth.account_lifecycle import AccountLifecycleService
    service=AccountLifecycleService.__new__(AccountLifecycleService)
    key=b'synthetic-rate-key-only-32-bytes!!'
    service._rate_limit_hmac_key=key
    f=client.fixture()
    shared=set(worker.shared_rate_hashes(key))
    own=set(worker.owned_rate_hashes(f,[],[],key))
    assert not shared & own
    for invitation in f['invites'].values():
        actual=set(service._rate_limit_buckets('invitation_issue',invitation['email'],'127.0.0.1'))
        assert len(actual & shared)==1 and len(actual & own)==1 and actual<=shared|own


@pytest.mark.parametrize('raw',[
    b"COMPETENCE_HUB_FLAG='false'\nCOMPETENCE_HUB_FLAG='true'\n",
    b"BAD_NAME=value\n",b"COMPETENCE_HUB_FLAG='unterminated\n",b"COMPETENCE_HUB_FLAG=two words\n",
])
def test_original_environment_parser_fails_closed(raw):
    with pytest.raises(ValueError):agent.parse_environment(raw)


def test_readiness_has_total_deadline_and_short_individual_requests(monkeypatch):
    calls=[]
    def unavailable(*args,**kwargs):
        calls.append(kwargs['timeout']);raise OSError('synthetic transport unavailable')
    clock=iter((0,46))
    monkeypatch.setattr(client.time,'monotonic',lambda:next(clock))
    monkeypatch.setattr(client.pilot.acceptance,'HTTPS',unavailable)
    with pytest.raises(protocol.SnapshotStop,match='STRICT_TLS_READINESS_FAILED'):
        client.wait_ready(None)
    assert calls==[2]


@pytest.mark.parametrize('phase,code',[
    ('ssh_connectivity','SSH_CONNECTIVITY_TIMEOUT_NO_MUTATION'),
    ('sudo_capability_probe','SUDO_CAPABILITY_TIMEOUT_NO_MUTATION'),
])
def test_connection_timeouts_are_distinct_and_never_prompt_or_start_root(monkeypatch,phase,code):
    phases=[];module=client.backup
    monkeypatch.setattr(module.sys.stdin,'isatty',lambda:True)
    def checked(*args,**kwargs):
        assert kwargs['data']==b'' and kwargs['timeout']==20
        if phase=='ssh_connectivity':raise subprocess.TimeoutExpired('synthetic-sensitive-command',20)
        return b''
    def probe(*args,**kwargs):
        assert kwargs['input']==b'' and kwargs['timeout']==20
        raise subprocess.TimeoutExpired('synthetic-sensitive-command',20)
    monkeypatch.setattr(module,'checked',checked)
    monkeypatch.setattr(module.subprocess,'run',probe)
    monkeypatch.setattr(module.getpass,'getpass',lambda *args:pytest.fail('No password on a transport timeout'))
    monkeypatch.setattr(module.subprocess,'Popen',lambda *args,**kw:pytest.fail('No privileged channel on a timeout'))
    with pytest.raises(protocol.SnapshotStop,match='^'+code+'$'):
        module.RootSession(progress=phases.append)
    assert phases[-1]==phase


def test_sudo_probe_transport_failure_does_not_request_password(monkeypatch):
    module=client.backup
    monkeypatch.setattr(module.sys.stdin,'isatty',lambda:True)
    monkeypatch.setattr(module,'checked',lambda *args,**kw:b'')
    monkeypatch.setattr(module.subprocess,'run',lambda *args,**kw:SimpleNamespace(returncode=255))
    monkeypatch.setattr(module.getpass,'getpass',lambda *args:pytest.fail('SSH failure is not a password request'))
    with pytest.raises(protocol.SnapshotStop,match='SUDO_PROBE_TRANSPORT_UNAVAILABLE_NO_MUTATION'):
        module.RootSession()


@pytest.mark.parametrize('available',[True,False])
def test_root_channel_keeps_its_private_pipe_after_stdin_free_probes(monkeypatch,available):
    module=client.backup;phases=[];probes=[]
    monkeypatch.setattr(module.sys.stdin,'isatty',lambda:True)
    def checked(*args,**kw):probes.append(kw['data']);return b''
    def probe(*args,**kw):probes.append(kw['input']);return SimpleNamespace(returncode=0 if available else 1)
    monkeypatch.setattr(module,'checked',checked)
    monkeypatch.setattr(module.subprocess,'run',probe)
    prompts=[]
    def prompt(*args):prompts.append(True);return 'SYNTHETIC-ONLY-NOT-A-REAL-PASSWORD'
    monkeypatch.setattr(module.getpass,'getpass',prompt)
    process=SimpleNamespace(stdin=io.BytesIO(),stdout=io.BytesIO(b'CH_ROOT_READY_1\n'))
    def popen(*args,**kwargs):
        assert kwargs['stdin'] is subprocess.PIPE and kwargs['stdout'] is subprocess.PIPE
        return process
    monkeypatch.setattr(module.subprocess,'Popen',popen)
    monkeypatch.setattr(module.RootSession,'deadline',lambda self,seconds:nullcontext())
    session=module.RootSession(bootstrap_source='SYNTHETIC',reviewed_sources={'synthetic':'only'},progress=phases.append)
    assert session.process is process and probes==[b'',b''] and len(prompts)==(0 if available else 1)
    assert phases[:2]==['ssh_connectivity','sudo_capability_probe'] and phases[-1]=='private_root_channel'
    sent=process.stdin.getvalue()
    if not available:
        assert sent.startswith(b'SYNTHETIC-ONLY-NOT-A-REAL-PASSWORD\n')
        sent=sent.partition(b'\n')[2]
    assert protocol.read_frame(io.BytesIO(sent))=={'synthetic':'only'}


def test_original_systemd_single_quoted_environment_is_read_without_shell():
    assert agent.parse_environment(b"COMPETENCE_HUB_FLAG='false'\nCOMPETENCE_HUB_DATA='{\"v1\": \"synthetic\"}'\n")=={
        'COMPETENCE_HUB_FLAG':'false','COMPETENCE_HUB_DATA':'{"v1": "synthetic"}'}


@pytest.mark.parametrize('mutation',[
    {'portal_users':0},{'portal_users':5},{'coaches':3},
])
def test_populated_reference_is_specific_not_empty_guard_bypass(mutation):
    value={'status':'PASS','database':{'database':'competence_hub_staging','migrations':[f'{x:04}' for x in range(1,7)],
        'table_owners':[{}]*27,'database_bytes':100,'counts':{'portal_users':4,'coaches':2}}}
    instance().validate_inventory(value)
    value['database']['counts'].update(mutation)
    with pytest.raises(protocol.SnapshotStop):instance().validate_inventory(value)


def test_original_empty_backup_validator_is_not_weakened():
    value=instance()
    assert value.snapshot.inventory_validator==value.validate_inventory
    default=protocol.BackupAgent(SimpleNamespace())
    assert default.inventory_validator is protocol.validate_inventory


def test_stage_cannot_write_before_current_restore():
    with pytest.raises(protocol.SnapshotStop,match='VERIFIED_CURRENT_RESTORE_FIRST'):
        instance().stage({})


@pytest.mark.parametrize('path',['/etc/nginx/nginx.conf','/etc/competence-hub-pilot/runtime.env','/etc/systemd/system/dp-chatbot.service'])
def test_update_writer_rejects_original_or_foreign_files(path):
    with pytest.raises(protocol.SnapshotStop,match='OWNED_UPDATE_PATH_ONLY'):instance().write_new(Path(path),b'SYNTHETIC')


def test_existing_owned_file_never_overwritten(tmp_path,monkeypatch):
    monkeypatch.setattr(agent,'RELEASE',tmp_path)
    monkeypatch.setattr(agent.os,'O_NOFOLLOW',0,raising=False)
    path=tmp_path/'bundle/test.txt';path.parent.mkdir();path.write_bytes(b'ORIGINAL')
    with pytest.raises(FileExistsError):instance().write_new(path,b'REPLACEMENT')
    assert path.read_bytes()==b'ORIGINAL'


def test_writer_rejects_linked_parent_before_mkdir(tmp_path,monkeypatch):
    monkeypatch.setattr(agent,'RELEASE',tmp_path)
    linked=tmp_path/'linked'
    monkeypatch.setattr(Path,'is_symlink',lambda self:self==linked)
    with pytest.raises(protocol.SnapshotStop,match='UPDATE_PARENT_LINK_REJECTED'):
        instance().write_new(linked/'file',b'SYNTHETIC')
    assert not linked.exists()


def test_partial_capture_write_is_owned_for_compensation(tmp_path,monkeypatch):
    path=tmp_path/'capture.env'
    monkeypatch.setattr(agent,'CAPTURE_ENV',path)
    monkeypatch.setattr(agent.os,'O_NOFOLLOW',0,raising=False)
    if sys.platform=='win32':monkeypatch.setattr(agent.os,'fchmod',lambda fd,mode:None,raising=False)
    def interrupted(fd):raise OSError('synthetic interruption')
    monkeypatch.setattr(agent.os,'fsync',interrupted)
    value=instance()
    with pytest.raises(OSError,match='synthetic interruption'):
        value.write_new(path,b'SYNTHETIC',0o600)
    assert value.capture_env_owned and path.read_bytes()==b'SYNTHETIC'


def test_actual_powershell_child_forwards_quiet_and_preserves_utf8(tmp_path):
    script=tmp_path/'synthetic.py'
    script.write_text('import json,sys\nprint(json.dumps(sys.argv[1:]))\nprint("Pr\\u00fcfung")\n',encoding='utf8')
    def quoted(value):return "'"+str(value).replace("'","''")+"'"
    command='. '+quoted(ROOT/'deploy/scripts/run-vps-v1-update.ps1')+'; Invoke-V1UpdateProcess '+quoted(sys.executable)+' '+quoted(script)+" '"+'a'*40+"' 'synthetic-only'"
    result=subprocess.run(['pwsh','-NoProfile','-Command',command],capture_output=True,timeout=30)
    assert result.returncode==0
    lines=result.stdout.decode('utf8').splitlines()
    assert json.loads(lines[0])==['--execute','--quiet','--source','a'*40,'--directory','synthetic-only']
    assert lines[1]=='Pr\u00fcfung'


def test_failed_unacknowledged_seed_never_deletes_reference(monkeypatch):
    value=instance();value.changed=True;calls=[]
    monkeypatch.setattr(protocol,'run',lambda *args,**kw:b'inactive' if 'show' in args else b'')
    value.worker_action=lambda action,**kw:calls.append(action)
    value.collect=lambda:{}
    value.rollback()
    assert not calls


def test_postflight_does_not_commit_before_final_https_check(monkeypatch):
    value=instance();value.changed=value.seeded=True;value.before={'listeners':[]};value.original_config={}
    monkeypatch.setattr(protocol,'run',lambda *args,**kw:b'')
    value.worker_action=lambda *args,**kw:{'status':'PASS'}
    value.reference_check=lambda:{'status':'PASS'}
    value.collect=lambda:{'listeners':[]}
    value.private_file=lambda path:b"COMPETENCE_HUB_FLAG='false'\n"
    result=value.commit({})
    assert result['status']=='PASS' and value.postflight_passed and not value.committed


@pytest.mark.parametrize('arguments,expected',[
    ([], 'VPS_V1_UPDATE=NOT_EXECUTED'),
    (['-Execute'],'QUIET_REFERENCE_WINDOW_REQUIRED'),
    (['-Execute','-AcknowledgeQuietPilot','-ExpectedSourceCommit','0'*40],'SOURCE_CHANGED_NO_SERVER_ACTION'),
])
def test_actual_operator_entry_stops_before_side_effects(arguments,expected):
    result=subprocess.run(['pwsh','-NoProfile','-File',str(ROOT/'deploy/scripts/run-vps-v1-update.ps1'),*arguments],capture_output=True,timeout=30)
    assert expected in result.stdout.decode('utf8')


def test_no_reset_reinstall_gpg_or_real_mail_in_update_contract():
    source=(ROOT/'deploy/scripts/vps_update_agent.py').read_text(encoding='utf8')
    assert 'pg_restore' not in source and 'gpg' not in source.lower()
    worker_source=(ROOT/'deploy/scripts/vps_update_worker.py').read_text(encoding='utf8')
    assert 'TRUNCATE' not in worker_source and 'DELETE FROM competence_hub.auth_rate_limit_buckets WHERE' in worker_source
    assert 'RETAINED_NOT_RESET' in source and 'REFERENCE_ROWS_CHANGED_NO_SOURCE_RESTORE' in source
