import base64
from contextlib import nullcontext
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import threading
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


@pytest.mark.parametrize('resume',['',client.RESUME_RUN])
def test_actual_powershell_child_forwards_quiet_and_preserves_utf8(tmp_path,resume):
    script=tmp_path/'synthetic.py'
    script.write_text('import json,sys\nprint(json.dumps(sys.argv[1:]))\nprint("Pr\\u00fcfung")\n',encoding='utf8')
    def quoted(value):return "'"+str(value).replace("'","''")+"'"
    command='. '+quoted(ROOT/'deploy/scripts/run-vps-v1-update.ps1')+'; Invoke-V1UpdateProcess '+quoted(sys.executable)+' '+quoted(script)+" '"+'a'*40+"' 'synthetic-only' "+quoted(resume)
    result=subprocess.run(['pwsh','-NoProfile','-Command',command],capture_output=True,timeout=30)
    assert result.returncode==0
    lines=result.stdout.decode('utf8').splitlines()
    assert json.loads(lines[0])==['--execute','--quiet','--source','a'*40,'--directory','synthetic-only']+(['--resume',resume] if resume else [])
    assert lines[1]=='Pr\u00fcfung'


def test_failed_unacknowledged_seed_never_deletes_reference(monkeypatch):
    value=instance();value.changed=True;calls=[]
    monkeypatch.setattr(protocol,'run',lambda *args,**kw:b'inactive' if 'show' in args else b'')
    value.worker_action=lambda action,**kw:calls.append(action)
    value.collect=lambda:{}
    value.start_api=lambda:None
    value.rollback()
    assert not calls


def test_postflight_does_not_commit_before_final_https_check(monkeypatch):
    value=instance();value.changed=value.seeded=True;value.before={'listeners':[]};value.original_config={}
    monkeypatch.setattr(protocol,'run',lambda *args,**kw:b'')
    value.worker_action=lambda *args,**kw:{'status':'PASS'}
    value.reference_check=lambda:{'status':'PASS'}
    value.collect=lambda:{'listeners':[]}
    value.start_api=lambda:None
    value.private_file=lambda path:b"COMPETENCE_HUB_FLAG='false'\n"
    result=value.commit({})
    assert result['status']=='PASS' and value.postflight_passed and not value.committed


def test_systemd_start_waits_for_actual_api_listener(monkeypatch):
    calls=[];attempts=iter((False,False,True));clock=iter((0,1,2))
    monkeypatch.setattr(protocol,'run',lambda *args,**kw:calls.append(args))
    monkeypatch.setattr(agent.time,'monotonic',lambda:next(clock))
    monkeypatch.setattr(agent.time,'sleep',lambda duration:calls.append(('wait',duration)))
    def connect(address,timeout):
        assert address==('127.0.0.1',8001) and timeout==.5
        if not next(attempts):raise OSError('synthetic delayed bind')
        return nullcontext()
    monkeypatch.setattr(agent.socket,'create_connection',connect)
    instance().start_api()
    assert calls==[('systemctl','start',agent.API),('wait',.2),('wait',.2)]


def test_actual_listener_deadline_never_silently_passes(monkeypatch):
    monkeypatch.setattr(protocol,'run',lambda *args,**kw:b'')
    clock=iter((0,46));monkeypatch.setattr(agent.time,'monotonic',lambda:next(clock))
    def absent(*args,**kw):raise OSError('synthetic absent listener')
    monkeypatch.setattr(agent.socket,'create_connection',absent)
    with pytest.raises(protocol.SnapshotStop,match='PILOT_API_LISTENER_NOT_READY'):
        instance().start_api()


@pytest.mark.parametrize('run',['','other-run','0'*32])
def test_resume_rejects_unbound_run_before_private_files_or_server(run,monkeypatch):
    monkeypatch.setattr(client.pilot,'qualify_directory',lambda *args:pytest.fail('No private files'))
    with pytest.raises(protocol.SnapshotStop,match='EXACT_ACCEPTED_RESUME_REQUIRED'):
        client.resume_material(run)
    with pytest.raises(protocol.SnapshotStop,match='EXACT_ACCEPTED_RESUME_REQUIRED'):
        instance().resume({'resume_run':run})


def test_resume_receipt_changed_stops_before_private_recovery(monkeypatch):
    monkeypatch.setattr(Path,'read_bytes',lambda self:b'SYNTHETIC MODIFICATION')
    monkeypatch.setattr(client.pilot,'qualify_directory',lambda *args:pytest.fail('No private recovery'))
    with pytest.raises(protocol.SnapshotStop,match='ACCEPTED_RESUME_RECEIPT_CHANGED'):
        client.resume_material(client.RESUME_RUN)


def test_resume_private_recovery_uses_retained_copies_without_overwrite(tmp_path,monkeypatch):
    previous=json.loads((ROOT/'release-artifacts/vps-v1-update'/(client.RESUME_RUN+'.json')).read_bytes())
    external=tmp_path/'local/CompetenceHub/pilot-updates'/client.RESUME_RUN
    external.mkdir(parents=True)
    dump=b'SYNTHETIC-POSTGRES-ARCHIVE'
    configuration={'runtime.env':base64.b64encode(b'SYNTHETIC-NOT-A-REAL-KEY').decode()}
    hashes={k:client.sha(base64.b64decode(v)) for k,v in configuration.items()}
    capture={'dump_sha256':client.sha(dump),'baseline':{'synthetic':'only'}}
    login=client.fixture()
    recovery={'synthetic':{'totp':'SYNTHETIC-ONLY','recovery':['NOT-A-REAL-CODE']}}
    content={'database.dump.dpapi':dump,'baseline.json.dpapi':client.canonical(capture),
             'original-configuration.json.dpapi':client.canonical(configuration),
             'owned-synthetic-logins.json.dpapi':client.canonical(login),
             'owned-synthetic-recovery.json.dpapi':client.canonical(recovery)}
    for name,data in content.items():(external/name).write_bytes(b'SYNTHETIC-SEAL'+data)
    previous['preflight']['configuration_hashes']=hashes
    for field,name in [('ciphertext_sha256','database.dump.dpapi'),('baseline_ciphertext_sha256','baseline.json.dpapi'),
                       ('configuration_ciphertext_sha256','original-configuration.json.dpapi')]:
        previous[field]=client.sha((external/name).read_bytes())
    receipt=tmp_path/'release-artifacts/vps-v1-update'/(client.RESUME_RUN+'.json')
    receipt.parent.mkdir(parents=True);receipt.write_bytes(client.canonical(previous))
    monkeypatch.setattr(client,'ROOT',tmp_path);monkeypatch.setattr(client,'RESUME_SHA',client.sha(receipt.read_bytes()))
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path/'local'))
    qualified=[];monkeypatch.setattr(client.pilot,'qualify_directory',lambda p:qualified.append(p))
    def decrypt(*args,**kw):
        assert '--decrypt-stdin' in args and kw['timeout']==30
        assert kw['data'].startswith(b'SYNTHETIC-SEAL')
        return kw['data'][len(b'SYNTHETIC-SEAL'):]
    monkeypatch.setattr(client.backup,'checked',decrypt)
    before={p.name:p.read_bytes() for p in external.iterdir()}
    proof,values,needles=client.resume_material(client.RESUME_RUN)
    assert proof['restore']=='PASS' and values['baseline']==capture['baseline'] and values['configuration_hashes']==hashes
    assert qualified==[external] and 'NOT-A-REAL-CODE' in needles
    assert before=={p.name:p.read_bytes() for p in external.iterdir()}


def test_resume_cannot_accept_a_database_delta(monkeypatch):
    value=instance();value.changed=value.resume_mode=True;value.baseline={'synthetic':'before'}
    monkeypatch.setattr(protocol,'snapshot_connection',lambda database:nullcontext(None))
    monkeypatch.setattr(protocol,'signature',lambda c:{'synthetic':'after'})
    with pytest.raises(protocol.SnapshotStop,match='RESUME_DATABASE_CHANGED'):
        value.finalize_resume({})
    assert not getattr(value,'postflight_passed',False)


def test_tunnel_hold_message_reaches_piped_stdout_before_enter():
    code="import sys;sys.path.insert(0,'scripts');import run_vps_update as c;c.hold_private_tunnel()"
    process=subprocess.Popen([sys.executable,'-I','-X','utf8','-c',code],cwd=ROOT/'apps/webapp',
                             stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    deadline=threading.Timer(15,process.kill);deadline.start()
    try:
        line=process.stdout.readline()
        assert b'PILOT_TUNNEL=OPEN UPDATE=COMPLETE' in line and line.endswith(b'\n')
        assert process.poll() is None
        process.communicate(input=b'\n',timeout=10)
        assert process.returncode==0
    finally:
        deadline.cancel()
        if process.poll() is None:process.kill();process.communicate()


@pytest.mark.parametrize('interruption',[EOFError,KeyboardInterrupt])
def test_tunnel_hold_allows_safe_local_exit(monkeypatch,capsys,interruption):
    def end():raise interruption()
    monkeypatch.setattr('builtins.input',end)
    client.hold_private_tunnel()
    assert 'UPDATE=COMPLETE' in capsys.readouterr().out


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
