from contextlib import contextmanager
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import subprocess
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


agent = module('snapshot_agent_tests', 'deploy/scripts/staging_snapshot_agent.py')
dpapi = module('snapshot_dpapi_tests', 'deploy/scripts/windows_dpapi.py')
client = module('snapshot_client_tests', 'apps/webapp/scripts/protected_staging_backup.py')


def inventory():
    return {
        'status': 'PASS', 'scope': 'READ_ONLY',
        'database': {'database': 'competence_hub_staging', 'migrations': [f'{i:04}' for i in range(1, 7)],
                     'database_bytes': 10485760, 'table_owners': [{}] * 27,
                     'counts': {'roles': 5, 'schema_migrations': 6, 'portal_users': 0}, 'other_sessions': 0},
        'services': {'competence-hub-api.service': {'LoadState': 'not-found'}},
        'paths': {'/etc/competence-hub/webapp.env': {'exists': False}, '/opt/competence-hub': {'exists': False}},
    }


def test_protocol_roundtrip_preserves_binary_safe_structured_values():
    stream = io.BytesIO()
    agent.write_frame(stream, {'action': 'capture', 'label': 'synthetic ü'})
    stream.seek(0)
    assert agent.read_frame(stream) == {'action': 'capture', 'label': 'synthetic ü'}


@pytest.mark.parametrize('payload', [b'', b'\x00', struct.pack('!I', 10) + b'{}',
                                     struct.pack('!I', 0), struct.pack('!I', agent.FRAME_BOUND + 1)])
def test_truncated_or_oversized_frame_fails_without_reflecting_input(payload):
    with pytest.raises(agent.SnapshotStop):
        agent.read_frame(io.BytesIO(payload))


def test_actual_empty_0006_inventory_is_eligible_only_for_backup():
    agent.validate_inventory(inventory())
    assert not hasattr(agent.BackupAgent, 'deploy')
    assert not hasattr(agent.BackupAgent, 'migrate')


@pytest.mark.parametrize('change', ['accounts', 'busy', 'new_schema', 'too_large', 'installed', 'env'])
def test_changed_target_or_real_data_blocks_capture_before_any_mutation(change):
    value = inventory()
    if change == 'accounts': value['database']['counts']['portal_users'] = 1
    if change == 'busy': value['database']['other_sessions'] = 1
    if change == 'new_schema': value['database']['migrations'].append('0007')
    if change == 'too_large': value['database']['database_bytes'] = agent.MAX_BYTES + 1
    if change == 'installed': value['paths']['/opt/competence-hub']['exists'] = True
    if change == 'env': value['paths']['/etc/competence-hub/webapp.env']['exists'] = True
    with pytest.raises(agent.SnapshotStop):
        agent.validate_inventory(value)


def test_dump_and_signature_share_live_exported_snapshot(monkeypatch):
    events = []
    class Connection:
        def query(self, query):
            if 'pg_export_snapshot' in query: return b'00000001-00000002-1'
            return json.dumps({'owner': 'competence_hub_owner', 'encoding': 'UTF8'}).encode()
    @contextmanager
    def connection(database):
        events.append('open')
        yield Connection()
        events.append('close')
    monkeypatch.setattr(agent, 'snapshot_connection', connection)
    monkeypatch.setattr(agent, 'signature', lambda c: events.append('signature') or {'tables': {}})
    def dump(*args):
        assert events == ['open', 'signature']
        assert '--snapshot=00000001-00000002-1' in args
        assert '-Fc' in args and '-d' in args and args[-1] == 'competence_hub_staging'
        assert '--file' not in args and '-f' not in args
        events.append('dump')
        return b'PGDMP_SYNTHETIC'
    monkeypatch.setattr(agent, 'run', dump)
    operation = agent.BackupAgent(SimpleNamespace(collect=inventory))
    result = operation.capture()
    assert result['dump_sha256'] == agent.sha(b'PGDMP_SYNTHETIC')
    assert events == ['open', 'signature', 'dump', 'close']


@pytest.mark.parametrize('payload', [{}, {'encrypted_copy_verified': False},
                                     {'encrypted_copy_verified': True, 'ciphertext_sha256': 'invalid'}])
def test_restore_requires_verified_exact_external_copy_before_sql(monkeypatch, payload):
    operation = agent.BackupAgent(None)
    operation.baseline = {}
    monkeypatch.setattr(agent, 'sql', lambda *a, **kw: pytest.fail('SQL must not run'))
    with pytest.raises(agent.SnapshotStop):
        operation.restore(payload)


def test_cleanup_refuses_source_database_and_does_not_force_other_sessions(monkeypatch):
    operation = agent.BackupAgent(None)
    operation.probe = agent.DATABASE
    monkeypatch.setattr(agent, 'sql', lambda *a, **kw: pytest.fail('SQL must not run'))
    with pytest.raises(agent.SnapshotStop, match='OWNED_PROBE_ID_REQUIRED'):
        operation.cleanup()


def test_changed_recovery_bytes_are_rejected_before_probe_creation(monkeypatch):
    operation = agent.BackupAgent(None)
    operation.baseline = {}
    operation.dump_sha256 = agent.sha(b'PGDMP_EXPECTED_SYNTHETIC')
    monkeypatch.setattr(agent, 'sql', lambda *a, **kw: pytest.fail('No database creation allowed'))
    import base64
    payload = {'encrypted_copy_verified': True, 'ciphertext_sha256': 'a' * 64,
               'dump': base64.b64encode(b'PGDMP_DIFFERENT_SYNTHETIC').decode()}
    with pytest.raises(agent.SnapshotStop, match='EXACT_REREAD_DUMP_REQUIRED'):
        operation.restore(payload)
    assert operation.probe is None


def test_restore_does_not_repeat_after_a_prior_attempt(monkeypatch):
    operation = agent.BackupAgent(None)
    operation.baseline = {}
    operation.restore_attempted = True
    monkeypatch.setattr(agent, 'sql', lambda *a, **kw: pytest.fail('No repeat allowed'))
    with pytest.raises(agent.SnapshotStop, match='BOUND_BACKUP_REQUIRED'):
        operation.restore({})


def test_uncertain_probe_creation_can_be_reconciled_without_existing_database_deletion(monkeypatch):
    operation = agent.BackupAgent(None)
    operation.probe = 'ch_restore_' + 'a' * 32
    calls = []
    def sql(statement):
        calls.append(statement)
        return b'0'
    monkeypatch.setattr(agent, 'sql', sql)
    operation.cleanup()
    assert operation.probe is None
    assert not any('DROP' in statement for statement in calls)


@pytest.mark.skipif(os.name != 'nt', reason='Windows DPAPI private worker')
def test_native_dpapi_fresh_process_and_tamper_rejection():
    clear = b'SYNTHETIC_POSTGRES_ARCHIVE_NO_EXISTING_KEYS'
    cipher = dpapi.transform(clear)
    worker = [os.sys.executable, str(ROOT / 'deploy/scripts/windows_dpapi.py'), '--decrypt-stdin']
    restored = subprocess.run(worker, input=cipher, capture_output=True)
    assert restored.returncode == 0 and restored.stdout == clear and restored.stderr == b''
    modified = bytearray(cipher)
    modified[-1] ^= 1
    rejected = subprocess.run(worker, input=modified, capture_output=True)
    assert rejected.returncode == 1 and rejected.stdout == b'' and rejected.stderr == b''


def test_private_writer_refuses_cleartext_or_overwrite_before_starting_process(monkeypatch, tmp_path):
    monkeypatch.setattr(client, 'checked', lambda *a, **kw: pytest.fail('process must not run'))
    with pytest.raises(client.protocol.SnapshotStop):
        client.private_ciphertext_file(tmp_path / 'never-created', b'PGDMP_plaintext')
    assert not (tmp_path / 'never-created').exists()
    existing = tmp_path / 'keep.dpapi'
    existing.write_bytes(b'KEEP_SYNTHETIC')
    with pytest.raises(RuntimeError):
        client.private_ciphertext_file(existing, bytes.fromhex('01000000d08c9ddf0115d1118c7a00c04fc297eb'))
    assert existing.read_bytes() == b'KEEP_SYNTHETIC'


@pytest.mark.skipif(os.name != 'nt', reason='PowerShell guarded operator entry')
def test_entry_default_never_runs_gpg_backup_or_remote_operation():
    result = subprocess.run(['pwsh', '-NoProfile', '-NonInteractive', '-File',
                             str(ROOT / 'deploy/scripts/run-protected-staging-backup.ps1')], capture_output=True)
    assert result.returncode == 0 and b'PROTECTED_BACKUP=NOT_EXECUTED' in result.stdout
    assert result.stderr == b''


def test_root_bootstrap_is_bounded_and_receives_code_only_after_authentication():
    assert 'CH_ROOT_READY_1' in client.BOOTSTRAP and '131072' in client.BOOTSTRAP
    source = (ROOT / 'apps/webapp/scripts/protected_staging_backup.py').read_text(encoding='utf8')
    assert source.index("b'CH_ROOT_READY_1\\n'") < source.index("'preflight': (SCRIPTS")
    assert 'StrictHostKeyChecking=yes' in client.SSH
    assert 'ForwardAgent=no' in client.SSH
    assert 'GNUPGHOME' not in source and 'webapp.env' not in source


def test_accidental_encrypted_backup_copy_is_excluded_from_git():
    result = subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '--no-index', 'baseline.json.dpapi'], capture_output=True)
    assert result.returncode == 0 and result.stdout.strip() == b'baseline.json.dpapi'


@pytest.mark.skipif(os.name != 'nt', reason='Actual PowerShell native-output regression')
@pytest.mark.parametrize('exit_code', [0, 7])
def test_child_progress_and_receipt_remain_visible_inside_outer_exit_expression(tmp_path, exit_code):
    child = tmp_path / 'synthetic_child.py'
    child.write_text(f"import sys\nprint('SYNTHETIC_PROGRESS')\nprint('REPORT=SYNTHETIC_ONLY')\nsys.exit({exit_code})\n", encoding='utf8')
    entry = ROOT / 'deploy/scripts/run-protected-staging-backup.ps1'
    script = (f". '{entry}'; function Test-Caller {{ "
              f"try {{ Invoke-ProtectedBackupProcess '{os.sys.executable}' '{child}' synthetic synthetic; return 0 }} "
              "catch { return 3 } }; exit (Test-Caller)")
    result = subprocess.run(['pwsh', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True)
    assert result.returncode == (0 if exit_code == 0 else 3)
    assert b'SYNTHETIC_PROGRESS' in result.stdout and b'REPORT=SYNTHETIC_ONLY' in result.stdout
    assert result.stderr == b''


def receipt_fixture():
    proof = {name: True for name in ('all_row_hashes_equal', 'schema_rights_equal', 'sequence_state_equal',
             'database_format_equal', 'probe_app_migrator_connect_denied', 'probe_removed', 'source_unchanged')}
    return {
        'scope': 'STAGING_BACKUP_RESTORE_ONLY', 'status': 'PASS', 'backup': 'PASS', 'restore': 'PASS',
        'postflight': 'PASS', 'phase': 'complete', 'source_commit': 'c' * 40, 'run_id': 'b' * 32,
        'ciphertext_sha256': 'a' * 64, 'baseline_ciphertext_sha256': 'd' * 64, 'table_count': 27,
        'migration': 'NOT_RUN', 'deployment': 'NOT_RUN', 'accounts': 'NOT_RUN',
        'portable_recovery': False, 'application_keyfiles_touched': False,
        'source_unchanged': True, 'own_probe_removed': True, 'ciphertext_tamper_rejected': True,
        'restore_proof': {**proof, 'status': 'PASS', 'table_count': 27},
        'migrations': [f'{i:04}' for i in range(1, 7)],
    }


@pytest.mark.skipif(os.name != 'nt', reason='Actual PowerShell receipt gate')
@pytest.mark.parametrize('change', [None, 'hash', 'run', 'commit', 'cleanup', 'string_bool', 'key_rotation', 'tables', 'restore'])
def test_zero_exit_and_private_files_alone_cannot_claim_restore_pass(change):
    receipt = receipt_fixture()
    if change == 'hash': receipt['ciphertext_sha256'] = 'f' * 64
    if change == 'run': receipt['run_id'] = 'e' * 32
    if change == 'commit': receipt['source_commit'] = 'f' * 40
    if change == 'cleanup': receipt['restore_proof']['probe_removed'] = False
    if change == 'string_bool': receipt['source_unchanged'] = 'true'
    if change == 'key_rotation': receipt['application_keyfiles_touched'] = True
    if change == 'tables': receipt['restore_proof']['table_count'] = 26
    if change == 'restore': receipt['restore'] = 'NOT_RUN'
    entry = ROOT / 'deploy/scripts/run-protected-staging-backup.ps1'
    payload = json.dumps(receipt)
    script = (f". '{entry}'; $r=ConvertFrom-Json -AsHashtable '{payload}'; "
              f"try {{ Assert-ProtectedBackupReceipt $r '{'c' * 40}' '{'b' * 32}' '{'a' * 64}' '{'d' * 64}'; exit 0 }} "
              "catch { exit 1 }")
    result = subprocess.run(['pwsh', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True)
    assert (result.returncode == 0) == (change is None)
    assert result.stdout == b'' and result.stderr == b''
