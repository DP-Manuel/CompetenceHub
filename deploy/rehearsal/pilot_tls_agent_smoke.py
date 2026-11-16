"""Actual Linux file/SSL/OpenSSL TLS rollover+rollback, synthetic /tmp only."""
import base64
from copy import deepcopy
import importlib.util
from pathlib import Path
import ssl
import stat
import subprocess
import tempfile


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[2] / path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


agent = load('tls_smoke_agent', 'deploy/scripts/pilot_tls_agent.py')
protocol = load('tls_smoke_protocol', 'deploy/scripts/staging_snapshot_agent.py')


def certificates(directory, prefix):
    ca, ca_key, csr, leaf, key, extensions = [directory / (prefix + name) for name in ('-ca.pem', '-ca.key', '.csr', '.pem', '.key', '.ext')]
    extensions.write_text('basicConstraints=critical,CA:FALSE\nsubjectAltName=DNS:localhost\nextendedKeyUsage=serverAuth\n')
    commands = [
        ['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', str(ca_key), '-out', str(ca), '-days', '2', '-subj', '/CN=synthetic-' + prefix],
        ['openssl', 'req', '-newkey', 'rsa:2048', '-nodes', '-keyout', str(key), '-out', str(csr), '-subj', '/CN=localhost'],
        ['openssl', 'x509', '-req', '-in', str(csr), '-CA', str(ca), '-CAkey', str(ca_key), '-CAcreateserial', '-out', str(leaf), '-days', '1', '-extfile', str(extensions)],
    ]
    for command in commands: subprocess.run(command, check=True, capture_output=True)
    return {'ca': ca.read_bytes(), 'certificate': leaf.read_bytes(), 'key': key.read_bytes()}


with tempfile.TemporaryDirectory(prefix='synthetic-tls-') as temporary:
    directory = Path(temporary)
    agent.ROOT = directory / 'opt'; agent.ROOT.mkdir(mode=0o755)
    agent.CONFIG = directory / 'etc'; agent.CONFIG.mkdir(mode=0o700)
    old, new = certificates(directory, 'old'), certificates(directory, 'new')
    agent.OLD_LEAF = protocol.sha(old['certificate']); agent.OLD_CA = protocol.sha(old['ca'])
    value = agent.TLSAgent(protocol)
    value.write_new(agent.ROOT / 'pilot.crt', old['certificate'], 0o644)
    value.write_new(agent.CONFIG / 'tls.key', old['key'], 0o600)
    baseline = {'runtime': 'unchanged', 'configuration': {'fixture': 'same'}, 'listeners': ['127.0.0.1:8443'],
        'services': {name: {'ActiveState': 'active', 'InvocationID': 'same'} for name in agent.SERVICES},
        'database': {'schema_sha256': 'same', 'database_format': 'same', 'tables': {'calendar_offers': {'sha256': 'same'}}, 'sequence_state': {}}}
    value.guard = lambda: deepcopy(baseline)
    real_run = value.run; restarts = []
    def command(*args, **kwargs):
        if args[:2] == ('systemctl', 'restart'): restarts.append(args[2]); return b''
        return real_run(*args, **kwargs)
    value.run = command
    value.inspect({'run': 'b' * 32})
    request = {name: base64.b64encode(raw).decode() for name, raw in new.items()}
    request.update(old_ca=base64.b64encode(old['ca']).decode(), protected_old_copy_verified=True)
    value.stage(request); value.activate({}); value.verify({'after_login': False})
    assert (agent.ROOT / 'pilot.crt').read_bytes() == new['certificate']
    assert (agent.CONFIG / 'tls.key').read_bytes() == new['key']
    assert stat.S_IMODE((agent.CONFIG / 'tls.key').stat().st_mode) == 0o600
    assert value.rollback()['status'] == 'PASS'
    assert (agent.ROOT / 'pilot.crt').read_bytes() == old['certificate']
    assert (agent.CONFIG / 'tls.key').read_bytes() == old['key']
    assert restarts == [agent.PROXY, agent.PROXY]
    assert (value.directory / 'old-key').read_bytes() == old['key']
    assert stat.S_IMODE(value.directory.stat().st_mode) == 0o700
    try: value.write_new(value.directory / 'old-key', b'never replace', 0o600)
    except FileExistsError: pass
    else: raise AssertionError('Overwrite accepted')
    try: ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(value.directory / 'certificate', value.directory / 'old-key')
    except ssl.SSLError: pass
    else: raise AssertionError('Mismatched pair accepted')
print('LINUX_TLS_FILES_OPENSSL_SWITCH_ROLLBACK=PASS SYNTHETIC_ONLY')
