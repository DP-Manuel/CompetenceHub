"""TLS-only safety gates with synthetic material; no VPS or operator-copy access."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import ssl
import subprocess
import sys
from types import SimpleNamespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

import pytest

ROOT = Path(__file__).resolve().parents[3]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


client = load('tls_renewal_test_client', 'apps/webapp/scripts/run_pilot_tls_renewal.py')
agent = load('tls_renewal_test_agent', 'deploy/scripts/pilot_tls_agent.py')
protocol = client.backup.protocol


@pytest.fixture(scope='module')
def material():
    return client.pilot.certificates(), client.pilot.certificates()


def test_matching_chain_hostname_validity_and_independent_identity(material):
    first, second = material
    old, new = client.validate_pair(*first), client.validate_pair(*second)
    assert old['hostname'] == new['hostname'] == 'localhost'
    assert old['ca_sha256'] != new['ca_sha256'] and old['certificate_sha256'] != new['certificate_sha256']


def test_actual_tls_handshake_enforces_chain_hostname_and_leaf(tmp_path, monkeypatch, material):
    ca, leaf, key = material[0]
    paths = [tmp_path / name for name in ('ca.pem', 'leaf.pem', 'key.pem', 'other-ca.pem')]
    for path, raw in zip(paths, (ca, leaf, key, material[1][0])): path.write_bytes(raw)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); context.load_cert_chain(paths[1], paths[2])
    server.socket = context.wrap_socket(server.socket, server_side=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    connect = client.socket.create_connection
    monkeypatch.setattr(client.socket, 'create_connection', lambda address, **kw: connect(server.server_address, **kw))
    try:
        client.verify_leaf(paths[0], client.sha(leaf))
        with pytest.raises(protocol.SnapshotStop, match='TLS_SERVED_LEAF_MISMATCH'): client.verify_leaf(paths[0], '0' * 64)
        with pytest.raises(ssl.SSLCertVerificationError): client.verify_leaf(paths[3], client.sha(leaf))
        with connect(server.server_address, timeout=5) as connection:
            with pytest.raises(ssl.SSLCertVerificationError):
                ssl.create_default_context(cafile=str(paths[0])).wrap_socket(connection, server_hostname='wrong.invalid')
    finally: server.shutdown(); server.server_close(); thread.join(timeout=5)


def test_lost_private_pipe_rolls_back_uncommitted_tls(monkeypatch):
    calls = []
    value = SimpleNamespace(changed=True, committed=False, rollback=lambda: calls.append('rollback'))
    monkeypatch.setattr(agent, 'TLSAgent', lambda protocol: value)
    def eof(stream): raise protocol.SnapshotStop('PRIVATE_CHANNEL_CLOSED')
    monkeypatch.setattr(protocol, 'read_frame', eof)
    with pytest.raises(protocol.SnapshotStop, match='PRIVATE_CHANNEL_CLOSED'): agent.serve(protocol)
    assert calls == ['rollback']


def test_failed_activation_returns_only_sanitized_error_and_rolls_back(monkeypatch):
    calls = []; output = []
    value = SimpleNamespace(changed=True, committed=False)
    def failure(request): raise RuntimeError('PRIVATE-KEY-MUST-NOT-APPEAR')
    def rollback(): value.changed=False; calls.append('rollback'); return {'status':'PASS'}
    value.activate=failure; value.rollback=rollback
    monkeypatch.setattr(agent, 'TLSAgent', lambda protocol:value)
    monkeypatch.setattr(protocol, 'read_frame', lambda stream:{'action':'activate'})
    monkeypatch.setattr(protocol, 'write_frame', lambda stream,value:output.append(value))
    agent.serve(protocol)
    assert calls == ['rollback'] and output[0]['rollback']['status'] == 'PASS'
    assert output[0]['code'] == 'TLS_PRIVATE_OPERATION_FAILED' and 'PRIVATE-KEY' not in str(output)


@pytest.mark.parametrize('mismatch', ['key', 'ca'])
def test_mismatched_key_or_signing_ca_is_rejected(material, mismatch):
    values = list(material[0]); values[2 if mismatch == 'key' else 0] = material[1][2 if mismatch == 'key' else 0]
    with pytest.raises(Exception): client.validate_pair(*values)


def test_pinned_receipt_and_public_ca_cannot_be_replaced(tmp_path, monkeypatch, material):
    state = client.state
    run = 'a' * 32; ca_raw, leaf_raw, _ = material[0]
    ca_hash, leaf_hash = client.sha(ca_raw), client.sha(leaf_raw)
    directory = tmp_path / 'CompetenceHub/pilot-tls' / run; directory.mkdir(parents=True)
    path = directory / 'pilot-ca.pem'; path.write_bytes(ca_raw)
    record = {name: 'PASS' for name in ('status', 'https', 'mfa_session', 'services', 'preservation')}
    record.update(runtime='5a555e9a9aae', ca_sha256=ca_hash, certificate_sha256=leaf_hash)
    public = tmp_path / 'release-artifacts/pilot-tls'; public.mkdir(parents=True)
    receipt = public / (run + '.json'); receipt.write_bytes(client.update.canonical(record))
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    for name, value in {'ACCEPTED_RUN': run, 'RECEIPT_SHA': client.sha(receipt.read_bytes()), 'CA_SHA': ca_hash, 'LEAF_SHA': leaf_hash}.items():
        monkeypatch.setattr(state, name, value)
    assert "u['LEAF_SHA']='" + leaf_hash + "'" in state.bind_agent("u['serve'](p,a,v)")
    assert state.current_ca(tmp_path, None, client.require, client.sha) == path
    path.write_bytes(material[1][0])
    with pytest.raises(protocol.SnapshotStop, match='ACCEPTED_TLS_CA_REQUIRED'):
        state.current_ca(tmp_path, None, client.require, client.sha)
    receipt.write_bytes(b'{}')
    with pytest.raises(protocol.SnapshotStop, match='ACCEPTED_TLS_RECEIPT_CHANGED'):
        state.current_ca(tmp_path, None, client.require, client.sha)


@pytest.mark.parametrize('mutation', ['services', 'configuration', 'listeners', 'calendar', 'users', 'password', 'schema'])
def test_postflight_rejects_unrelated_changes(monkeypatch, mutation):
    value = agent.TLSAgent(protocol)
    value.changed = True; value.directory = Path('/synthetic'); value.new_sha = client.sha(b'new-leaf')
    before = {'runtime': 'unchanged', 'listeners': ['127.0.0.1:8443'], 'configuration': {'fixed': 'hash'},
              'services': {name: {'ActiveState': 'active', 'InvocationID': 'same'} for name in agent.SERVICES},
              'database': {'schema_sha256': 'same', 'database_format': 'same', 'sequence_state': {},
                           'tables': {name: {'sha256': 'same'} for name in ('calendar_offers', 'portal_users', 'auth_password_credentials', 'auth_sessions')}}}
    value.before = before; after = deepcopy(before)
    if mutation == 'services': after['services'][agent.API]['InvocationID'] = 'different'
    if mutation == 'configuration': after['configuration']['fixed'] = 'changed'
    if mutation == 'listeners': after['listeners'] = ['0.0.0.0:8443']
    if mutation in ('calendar', 'users', 'password'):
        name = {'calendar': 'calendar_offers', 'users': 'portal_users', 'password': 'auth_password_credentials'}[mutation]
        after['database']['tables'][name]['sha256'] = 'changed'
    if mutation == 'schema': after['database']['schema_sha256'] = 'changed'
    value.guard = lambda: after
    value.file = lambda path, mode: b'new-leaf' if path.name in ('pilot.crt', 'certificate') else b'new-key'
    with pytest.raises(protocol.SnapshotStop): value.verify({'after_login': True})


def test_normal_auth_changes_are_not_permission_to_change_accounts():
    assert {'auth_sessions', 'audit_events'} <= agent.AUTH_CHANGES
    assert not {'portal_users', 'user_roles', 'calendar_offers', 'auth_password_credentials',
                'auth_recovery_codes', 'auth_token_delivery_outbox'} & agent.AUTH_CHANGES
    value = agent.TLSAgent(protocol)
    with pytest.raises(protocol.SnapshotStop, match='TLS_COMPLETE_ACCEPTANCE_REQUIRED'):
        value.commit({'client_checks': True})
    assert value.rollback() == {'status': 'NO_MUTATION'}


@pytest.mark.parametrize('arguments,expected', [([], 'PILOT_TLS=NOT_EXECUTED'),
    (['-Execute'], 'QUIET_PILOT_REQUIRED'),
    (['-Execute', '-AcknowledgeQuietPilot', '-ExpectedSourceCommit', '0' * 40], 'SOURCE_CHANGED')])
def test_entry_has_no_implicit_server_action(arguments, expected):
    result = subprocess.run(['pwsh', '-NoProfile', '-File', str(ROOT / 'deploy/scripts/run-pilot-tls-renewal.ps1'), *arguments], capture_output=True, timeout=30)
    assert expected in result.stdout.decode('utf8')


def test_actual_isolated_operator_import_and_no_tls_bypass():
    path = ROOT / 'apps/webapp/scripts/run_pilot_tls_renewal.py'
    source = path.read_text(encoding='utf8')
    assert 'ignore_https_errors' not in source and 'CERT_NONE' not in source and 'check_hostname=False' not in source
    code = "import runpy;v=runpy.run_path(" + repr(str(path)) + ");assert callable(v['main'])"
    result = subprocess.run([sys.executable, '-I', '-X', 'utf8', '-c', code], capture_output=True, timeout=30)
    assert result.returncode == 0
