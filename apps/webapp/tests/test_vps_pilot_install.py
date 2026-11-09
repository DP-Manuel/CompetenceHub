from contextlib import contextmanager
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

from cryptography import x509
from cryptography.x509.oid import ExtendedKeyUsageOID
import pytest

ROOT=Path(__file__).resolve().parents[3]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


agent=load('vps_agent_test','deploy/scripts/vps_pilot_agent.py')
protocol=load('vps_protocol_test','deploy/scripts/staging_snapshot_agent.py')
client=load('vps_client_test','apps/webapp/scripts/run_vps_pilot.py')


def test_pilot_uses_existing_bound_release_and_recovery_no_backup_repeat():
    assert client.PACKAGE_SHA==agent.PACKAGE_SHA
    assert len(client.RECEIPT_SHA)==64
    source=(ROOT/'apps/webapp/scripts/run_vps_pilot.py').read_text()
    assert "root.request('capture'" not in source
    assert "root.request('restore'" not in source
    assert 'gpg.exe' not in source
    assert 'Use-StagingOperatorEnvironment' not in source
    assert "sha(key_store.read_bytes())==key_hash" in source


@pytest.fixture
def legacy_store(tmp_path,monkeypatch):
    root=tmp_path/'repository'
    receipt=root/'release-artifacts/protected-staging-backup'/(client.RECEIPT+'.json')
    receipt.parent.mkdir(parents=True)
    storage=tmp_path/'local/CompetenceHub/pilot-snapshots'/client.RECEIPT
    storage.mkdir(parents=True)
    encrypted={'database.dump.dpapi':b'SYNTHETIC_ENCRYPTED_DUMP',
               'baseline.json.dpapi':b'SYNTHETIC_ENCRYPTED_BASELINE'}
    for name,data in encrypted.items():(storage/name).write_bytes(data)
    # The original accepted receipt predates baseline_ciphertext_sha256.
    record={'status':'PASS','backup':'PASS','restore':'PASS','postflight':'PASS',
            'source_unchanged':True,'own_probe_removed':True,
            'ciphertext_sha256':client.sha(encrypted['database.dump.dpapi'])}
    receipt.write_bytes(client.canonical(record))
    monkeypatch.setattr(client,'ROOT',root)
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path/'local'))
    monkeypatch.setattr(client,'RECEIPT_SHA',client.sha(receipt.read_bytes()))
    monkeypatch.setattr(client,'ACCEPTED_CIPHERTEXTS',
                        {name:client.sha(data) for name,data in encrypted.items()},raising=False)
    calls=[]
    monkeypatch.setattr(client,'powershell',lambda script:calls.append('acl') or b'')
    def checked(*args,data=None):
        calls.append('decrypt_baseline')
        assert data==encrypted['baseline.json.dpapi']
        return b'{"baseline":{"tables":{"synthetic":0},"schema_sha256":"synthetic"}}'
    monkeypatch.setattr(client.backup,'checked',checked)
    return receipt,storage,encrypted,calls


def test_actual_legacy_receipt_shape_reuses_separately_bound_baseline_hash(legacy_store):
    _,_,_,calls=legacy_store
    assert client.accepted_baseline()=={'tables':{'synthetic':0},'schema_sha256':'synthetic'}
    assert calls==['acl','acl','decrypt_baseline']


@pytest.mark.parametrize('name',['database.dump.dpapi','baseline.json.dpapi'])
def test_changed_legacy_ciphertext_is_rejected_before_any_decryption(legacy_store,name):
    _,storage,_,calls=legacy_store
    (storage/name).write_bytes(b'SYNTHETIC_CHANGED_CIPHERTEXT')
    with pytest.raises(client.backup.protocol.SnapshotStop,match='EXISTING_ROLLBACK_COPY_CHANGED'):
        client.accepted_baseline()
    assert 'decrypt_baseline' not in calls


def test_altered_legacy_receipt_is_not_a_generic_schema_bypass(legacy_store):
    receipt,_,_,calls=legacy_store
    receipt.write_bytes(receipt.read_bytes()+b' ')
    with pytest.raises(client.backup.protocol.SnapshotStop,match='BOUND_RESTORE_RECEIPT_REQUIRED'):
        client.accepted_baseline()
    assert calls==[]


@pytest.mark.parametrize('field',['ciphertext_sha256','baseline_ciphertext_sha256'])
def test_receipt_hash_fields_cannot_override_independently_accepted_hashes(legacy_store,monkeypatch,field):
    receipt,_,_,calls=legacy_store
    record=json.loads(receipt.read_bytes());record[field]='0'*64
    receipt.write_bytes(client.canonical(record))
    monkeypatch.setattr(client,'RECEIPT_SHA',client.sha(receipt.read_bytes()))
    with pytest.raises(client.backup.protocol.SnapshotStop,match='BOUND_RESTORE_CIPHERTEXT_MISMATCH'):
        client.accepted_baseline()
    assert 'decrypt_baseline' not in calls


def test_missing_dump_hash_fails_with_sanitized_code_not_keyerror(legacy_store,monkeypatch):
    receipt,_,_,calls=legacy_store
    record=json.loads(receipt.read_bytes());del record['ciphertext_sha256']
    receipt.write_bytes(client.canonical(record))
    monkeypatch.setattr(client,'RECEIPT_SHA',client.sha(receipt.read_bytes()))
    with pytest.raises(client.backup.protocol.SnapshotStop,match='BOUND_RESTORE_CIPHERTEXT_MISMATCH'):
        client.accepted_baseline()
    assert 'decrypt_baseline' not in calls


@pytest.mark.parametrize('value',[{}, {'baseline':None}, {'baseline':[]}])
def test_malformed_recovered_baseline_fails_without_unhandled_keyerror(legacy_store,monkeypatch,value):
    monkeypatch.setattr(client.backup,'checked',lambda *args,**values:client.canonical(value))
    with pytest.raises(client.backup.protocol.SnapshotStop,match='BOUND_BASELINE_REQUIRED'):
        client.accepted_baseline()


def test_immutable_restore_bindings_match_existing_canonical_operations_record():
    record=(ROOT/'docs/operations/integrated-staging-pilot-2026-11-09.md').read_text(encoding='utf8')
    assert client.RECEIPT_SHA in record
    assert all(value in record for value in client.ACCEPTED_CIPHERTEXTS.values())


@pytest.mark.parametrize('exit_code',[0,4])
def test_operator_native_utf8_output_and_failure_preserve_console_encoding(tmp_path,exit_code):
    import base64
    import subprocess
    import sys
    child=tmp_path/'synthetic-child.py'
    child.write_text("import sys\nprint('REPORT=C:/Users/RödelManuel/synthetic.json',flush=True)\nsys.exit("+str(exit_code)+")\n",encoding='utf8')
    command="""$ErrorActionPreference='Stop'
. '__ENTRY__'
[Console]::OutputEncoding=[Text.Encoding]::GetEncoding(850)
$failed=$false
try { Invoke-VpsPilotProcess '__PYTHON__' '__CHILD__' 'synthetic' 'synthetic' }
catch { if ($_.Exception.Message -cne 'PRIVATE_PILOT_NOT_ACCEPTED') {exit 9};$failed=$true }
if ([Console]::OutputEncoding.CodePage -ne 850) {exit 8}
if ($failed -ne __FAIL__) {exit 7}
Write-Host 'ENCODING_RESTORED'
""".replace('__ENTRY__',str(ROOT/'deploy/scripts/run-vps-pilot.ps1')).replace('__PYTHON__',sys.executable).replace('__CHILD__',str(child)).replace('__FAIL__','$true' if exit_code else '$false')
    result=subprocess.run(['pwsh','-NoProfile','-EncodedCommand',base64.b64encode(command.encode('utf-16-le')).decode()],capture_output=True,timeout=30)
    assert result.returncode==0
    assert 'REPORT=C:/Users/RödelManuel/synthetic.json' in result.stdout.decode('utf8')
    assert b'ENCODING_RESTORED' in result.stdout


def test_private_tls_only_exact_host_no_global_nginx_or_public_listeners():
    value=agent.proxy_config()
    assert 'listen 127.0.0.1:8443 ssl;' in value
    assert '$http_host != "localhost:8447"' in value
    assert 'TLSv1.2 TLSv1.3' in value
    assert 'proxy_set_header X-Forwarded-Proto https;' in value
    assert 'listen 443' not in value and 'listen 80' not in value
    assert 'access_log off;' in value


def test_service_namespaces_and_private_key_custody():
    values=agent.units()
    assert set(values)=={agent.API,agent.PROXY}
    for text in values.values():
        for expected in ('DynamicUser=yes','ProtectSystem=strict','NoNewPrivileges=true','UMask=0077'):
            assert expected in text
    assert '--host 127.0.0.1 --port 8001' in values[agent.API]
    assert 'LoadCredential=tls.key:/etc/competence-hub-pilot/tls.key' in values[agent.PROXY]
    assert 'EnvironmentFile=/etc/competence-hub-pilot/runtime.env' in values[agent.API]


def test_isolated_ca_signs_only_localhost_leaf_with_bounded_validity():
    ca,leaf,key=client.certificates()
    root=x509.load_pem_x509_certificate(ca);certificate=x509.load_pem_x509_certificate(leaf)
    certificate.verify_directly_issued_by(root)
    assert certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)==['localhost']
    assert certificate.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value==x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH])
    assert (certificate.not_valid_after_utc-certificate.not_valid_before_utc).days<=15
    assert b'PRIVATE KEY' not in ca and b'PRIVATE KEY' not in leaf and b'PRIVATE KEY' in key


def test_synthetic_fixture_roles_identities_and_passwords_are_distinct():
    first,second=client.fixture(),client.fixture()
    assert first!=second
    assert [x['role'] for x in first['accounts'].values()]==['admin','calendar_reviewer','coach','coach']
    assert len(set(x['password'] for x in first['accounts'].values()))==4
    for item in first['accounts'].values():
        assert item['email']=='synthetic-vps-'+UUID(item['id']).hex+'@example.invalid'
        assert len(item['password'])>=40


@pytest.mark.parametrize('path',['/etc/nginx/nginx.conf','/etc/systemd/system/dp-chatbot.service','/root/secret','/opt/competence-hub/application'])
def test_write_rejects_foreign_paths_before_any_mutation(path):
    value=agent.PilotAgent(SimpleNamespace(),protocol)
    with pytest.raises(protocol.SnapshotStop,match='OWNED_PATH_ONLY'):
        value.write(Path(path),b'not written')


def test_existing_pilot_requires_reconciliation_not_overwrite(tmp_path,monkeypatch):
    monkeypatch.setattr(agent,'ROOT',tmp_path)
    monkeypatch.setattr(agent.sys,'version_info',(3,12))
    monkeypatch.setattr(agent.platform,'machine',lambda:'x86_64')
    snapshot=SimpleNamespace(validate_inventory=lambda i:None,require=protocol.require)
    value=agent.PilotAgent(SimpleNamespace(collect=lambda:{'listeners':[]}),snapshot)
    with pytest.raises(protocol.SnapshotStop,match='PRIOR_PILOT_REQUIRES_RECONCILIATION'):
        value.preflight({'baseline':{}})


def test_snapshot_drift_prevents_staging(tmp_path,monkeypatch):
    monkeypatch.setattr(agent,'ROOT',tmp_path/'absent')
    monkeypatch.setattr(agent,'CONFIG',tmp_path/'also-absent')
    monkeypatch.setattr(agent.sys,'version_info',(3,12))
    monkeypatch.setattr(agent.platform,'machine',lambda:'x86_64')
    monkeypatch.setattr(agent.shutil,'disk_usage',lambda p:SimpleNamespace(free=2*1024**3))
    original=Path.read_text
    monkeypatch.setattr(Path,'read_text',lambda p,*a,**kw:'MemAvailable: 2097152 kB' if str(p).replace('\\','/')=='/proc/meminfo' else original(p,*a,**kw))
    @contextmanager
    def connection(db):yield object()
    snapshot=SimpleNamespace(validate_inventory=lambda i:None,require=protocol.require,
                             snapshot_connection=connection,DATABASE='competence_hub_staging',signature=lambda c:{'changed':True})
    value=agent.PilotAgent(SimpleNamespace(collect=lambda:{'listeners':[]}),snapshot)
    with pytest.raises(protocol.SnapshotStop,match='ACCEPTED_SNAPSHOT_NO_LONGER_MATCHES'):
        value.preflight({'baseline':{'changed':False}})
    assert not value.ready and not (tmp_path/'absent').exists()


def test_bad_release_rejected_before_owned_directory(tmp_path,monkeypatch):
    monkeypatch.setattr(agent,'ROOT',tmp_path/'absent')
    value=agent.PilotAgent(SimpleNamespace(),protocol);value.ready=True
    with pytest.raises(protocol.SnapshotStop,match='EXACT_RELEASE_REQUIRED'):
        value.stage({'package':'eA=='})
    assert not (tmp_path/'absent').exists()


def test_rollback_only_owns_pilot_services_and_exact_fixture(monkeypatch):
    calls=[]
    def run(*args):
        calls.append(args)
        return b'inactive'
    snapshot=SimpleNamespace(require=protocol.require,run=run)
    value=agent.PilotAgent(SimpleNamespace(),snapshot);value.owned=True;value.fixture={}
    monkeypatch.setattr(Path,'exists',lambda p:True)
    value.worker_action=lambda a:calls.append(('fixture',a))
    result=value.rollback()
    assert calls==[('systemctl','stop',agent.PROXY),('systemctl','disable',agent.PROXY),
                   ('systemctl','show','--property=ActiveState','--value',agent.PROXY),
                   ('systemctl','stop',agent.API),('systemctl','disable',agent.API),
                   ('systemctl','show','--property=ActiveState','--value',agent.API),('fixture','cleanup')]
    assert result['source_restore_performed'] is False and result['sequences_not_rewound'] is True


@pytest.mark.parametrize('running',[True,False])
def test_failed_proxy_stop_still_attempts_api_stop_and_never_cleans_live_fixture(monkeypatch,running):
    calls=[]
    def run(*args):
        calls.append(args)
        if args[1]=='stop' and args[-1]==agent.PROXY:raise RuntimeError('synthetic failure')
        if args[1]=='show':return b'active' if running and args[-1]==agent.PROXY else b'inactive'
        return b''
    value=agent.PilotAgent(SimpleNamespace(),SimpleNamespace(require=protocol.require,run=run))
    value.owned=True;value.fixture={}
    value.worker_action=lambda action:calls.append(('fixture',action))
    monkeypatch.setattr(Path,'exists',lambda p:True)
    result=value.rollback()
    assert result['status']=='REVIEW_REQUIRED'
    assert ('systemctl','stop',agent.API) in calls
    assert (('fixture','cleanup') in calls) is (not running)


def test_committed_disconnect_never_rolls_back(monkeypatch):
    class FakeAgent:
        def __init__(self,p,s):self.committed=True;self.owned=True
        def rollback(self):raise AssertionError('Must not undo accepted pilot')
    monkeypatch.setattr(agent,'PilotAgent',FakeAgent)
    monkeypatch.setattr(agent.os,'name','posix')
    monkeypatch.setattr(agent.os,'geteuid',lambda:0,raising=False)
    def eof(stream):raise protocol.SnapshotStop('PRIVATE_CHANNEL_CLOSED')
    agent.serve(SimpleNamespace(),SimpleNamespace(require=protocol.require,read_frame=eof))


def test_postflight_rejects_removed_chatbot_listener(monkeypatch):
    services={'dp-chatbot.service':{'ActiveState':'active'}}
    db={name:None for name in ('migrations','roles','role_memberships','table_owners','privileges','listen_addresses')}
    p=SimpleNamespace(collect=lambda:{'status':'PASS','database':db,'services':services,'listeners':['127.0.0.1:8001','127.0.0.1:8443']},SERVICES=['dp-chatbot.service'])
    value=agent.PilotAgent(p,protocol)
    value.before={'database':db,'listeners':['127.0.0.1:8000']}
    with pytest.raises(protocol.SnapshotStop,match='EXISTING_LISTENER_REMOVED'):
        value.postflight({})


def test_actual_operator_has_no_browser_certificate_bypass_or_os_trust_change():
    source=(ROOT/'apps/webapp/scripts/run_vps_pilot.py').read_text()
    acceptance=(ROOT/'apps/webapp/scripts/vps_pilot_acceptance.py').read_text()
    for forbidden in ('ignore_https_errors','_create_unverified_context','Import-Certificate','--ignore-certificate-errors'):
        assert forbidden not in source+acceptance
    assert 'PLAYWRIGHT_FIREFOX_POLICIES_JSON' in source
    assert "ssl.create_default_context(cafile=" in acceptance
    assert 'browser.content.full-zoom' in acceptance


def test_private_bootstrap_compiles_and_injects_only_reviewed_modules():
    compile(client.BOOTSTRAP,'<synthetic-bootstrap>','exec')
    assert "v['serve'](types.SimpleNamespace(**p),types.SimpleNamespace(**a))" in client.BOOTSTRAP
    assert '262144' in client.BOOTSTRAP


@pytest.mark.parametrize('fail_close',[False,True])
def test_committed_channel_finalization_does_not_claim_installation_failure(fail_close):
    calls=[]
    class Session:
        def request(self,action):
            calls.append(action)
            if fail_close:raise BrokenPipeError()
        def close(self):calls.append('transport_closed')
    result=client.close_committed(Session())
    assert calls==['close','transport_closed']
    assert result['status']==('CLOSE_ACK_NOT_RECEIVED' if fail_close else 'ACKNOWLEDGED')


def test_public_runtime_creation_mask_is_restored_after_failure(monkeypatch):
    masks=[]
    monkeypatch.setattr(agent.os,'umask',lambda value:masks.append(value) or 0o077)
    @agent.readable_runtime
    def failure():raise RuntimeError('synthetic')
    with pytest.raises(RuntimeError):failure()
    assert masks==[0o022,0o077]


def test_inert_operator_without_execute_has_no_side_effects():
    import subprocess
    result=subprocess.run(['pwsh','-NoProfile','-File',str(ROOT/'deploy/scripts/run-vps-pilot.ps1')],capture_output=True,text=True)
    assert result.returncode==0 and result.stdout.strip()=='VPS_PILOT=NOT_EXECUTED'
