"""Single approved TLS rollover over the existing private root pipe. No app writes."""
import base64
import hashlib
import os
from pathlib import Path
import re
import ssl
import stat
import subprocess
import sys
from uuid import uuid4

ROOT = Path('/opt/competence-hub-pilot')
CONFIG = Path('/etc/competence-hub-pilot')
API = 'competence-hub-pilot-api.service'
PROXY = 'competence-hub-pilot-proxy.service'
SERVICES = (API, PROXY, 'dp-chatbot.service', 'nginx.service', 'fail2ban.service', 'postgresql.service')
OLD_LEAF = 'aecd310881202f9438b14a9d57d7f3e033bf947416a460fa3263fa44cf71d27a'
OLD_CA = '14827c63424b87f7b40aa04019e720872e241e5a8f7a4a5b495cdcb3c89b302d'
AUTH_CHANGES = {'auth_sessions', 'auth_login_challenges', 'auth_totp_credentials',
                'auth_rate_limit_buckets', 'auth_idempotency_records', 'audit_events'}


class TLSAgent:
    def __init__(self, protocol):
        self.s = protocol
        self.before = self.old = self.directory = self.new_sha = None
        self.changed = self.committed = False

    def run(self, *args, data=None):
        result = subprocess.run(args, input=data, capture_output=True, timeout=45, cwd='/')
        self.s.require(result.returncode == 0, 'TLS_PRIVATE_COMMAND_FAILED')
        return result.stdout

    def file(self, path, mode):
        info = path.lstat()
        self.s.require(stat.S_ISREG(info.st_mode) and info.st_uid == 0
                       and stat.S_IMODE(info.st_mode) == mode, 'TLS_FILE_CUSTODY_REQUIRED')
        return path.read_bytes()

    def directory_custody(self, path):
        info = path.lstat()
        self.s.require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0
                       and not stat.S_IMODE(info.st_mode) & 0o022, 'TLS_DIRECTORY_CUSTODY_REQUIRED')

    def write_new(self, path, data, mode):
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
        with os.fdopen(descriptor, 'wb') as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(data); stream.flush(); os.fsync(stream.fileno())

    def replace(self, path, data, mode):
        temporary = path.parent / ('.tls-' + uuid4().hex)
        self.write_new(temporary, data, mode)
        os.replace(temporary, path)

    def guard(self):
        services = {}
        for name in SERVICES:
            raw = self.run('systemctl', 'show', name, '-p', 'ActiveState', '-p', 'InvocationID').decode()
            record = dict(line.split('=', 1) for line in raw.splitlines() if '=' in line)
            self.s.require(record['ActiveState'] == 'active', 'TLS_SIX_HEALTHY_SERVICES_REQUIRED')
            services[name] = record
        runtime = self.run('systemctl', 'show', API, '-p', 'ExecStart', '--value').decode()
        self.s.require(str(ROOT / 'releases/5a555e9a9aae/venv/bin/uvicorn') in runtime
                       and '--host 127.0.0.1 --port 8001' in runtime, 'TLS_EXISTING_V12_REQUIRED')
        proxy = self.run('systemctl', 'show', PROXY, '-p', 'LoadCredential', '--value').decode()
        self.s.require('tls.key:' + str(CONFIG / 'tls.key') in proxy, 'TLS_EXISTING_CREDENTIAL_REQUIRED')
        listeners = sorted(line.split()[3] for line in self.run('ss', '-ltnH').decode().splitlines())
        self.s.require({'127.0.0.1:8001', '127.0.0.1:8443'} <= set(listeners)
                       and all(x.startswith('127.0.0.1:') for x in listeners if x.endswith((':8001', ':8443'))),
                       'TLS_LOOPBACK_ONLY_REQUIRED')
        files = [ROOT / 'nginx.conf', CONFIG / 'runtime.env']
        units = Path('/etc/systemd/system')
        files += [units / name for name in (API, PROXY)]
        files += [units / (API + '.d') / name for name in
                  ('20-v1-runtime.conf', '22-v11-runtime.conf', '24-v12-runtime.conf')]
        hashes = {}
        for path in files:
            self.s.require(path.is_file() and not path.is_symlink(), 'TLS_FIXED_CONFIGURATION_REQUIRED')
            hashes[str(path)] = self.s.sha(path.read_bytes())
        with self.s.snapshot_connection(self.s.DATABASE) as connection:
            database = self.s.signature(connection)
            audit_max = int(connection.query('SELECT COALESCE(max(id),0) FROM competence_hub.audit_events'))
            bound = self.before['audit_max'] if self.before is not None else audit_max
            prefix = hashlib.sha256()
            for line in connection.lines(f'''COPY (SELECT row_to_json(t)::text FROM competence_hub.audit_events t
                WHERE id<={bound} ORDER BY row_to_json(t)::text COLLATE "C") TO STDOUT'''):
                prefix.update(line)
        self.s.require(len(database['tables']) == 27 and database['tables']['portal_users']['count'] == 4
                       and database['tables']['coaches']['count'] == 2, 'TLS_EXISTING_REFERENCE_REQUIRED')
        return {'services': services, 'runtime': runtime, 'listeners': listeners,
                'configuration': hashes, 'database': database, 'audit_max': audit_max, 'audit_prefix_sha256': prefix.hexdigest()}

    def inspect(self, request):
        self.s.require(self.old is None, 'TLS_NO_AUTOMATIC_REPEAT')
        self.s.require(re.fullmatch('[a-f0-9]{32}', request['run']), 'TLS_EXACT_RUN_REQUIRED')
        self.directory_custody(ROOT); self.directory_custody(CONFIG)
        self.initial = self.guard()
        leaf, key = self.file(ROOT / 'pilot.crt', 0o644), self.file(CONFIG / 'tls.key', 0o600)
        self.s.require(self.s.sha(leaf) == OLD_LEAF, 'TLS_ORIGINAL_CERTIFICATE_REQUIRED')
        self.old = {'certificate': base64.b64encode(leaf).decode(), 'key': base64.b64encode(key).decode()}
        self.run('openssl', 'x509', '-in', str(ROOT / 'pilot.crt'), '-checkend', '600', '-noout')
        self.run_id = request['run']
        return {'old_tls': self.old, 'services': 'PASS', 'runtime': '5a555e9a9aae'}

    def stage(self, request):
        self.s.require(self.old is not None and self.directory is None, 'TLS_INSPECT_FIRST')
        self.s.require(request.get('protected_old_copy_verified') is True, 'TLS_PROTECTED_RECOVERY_REQUIRED')
        self.before = self.guard()
        self.s.require(self.before['configuration'] == self.initial['configuration'], 'TLS_CONFIGURATION_DRIFT')
        self.s.require(self.file(ROOT / 'pilot.crt', 0o644) == base64.b64decode(self.old['certificate'])
                       and self.file(CONFIG / 'tls.key', 0o600) == base64.b64decode(self.old['key']), 'TLS_PAIR_DRIFT')
        parent = CONFIG / 'tls-rollbacks'
        if not parent.exists(): parent.mkdir(mode=0o700)
        self.directory_custody(parent)
        self.directory = parent / self.run_id
        self.directory.mkdir(mode=0o700)
        self.directory_custody(self.directory)
        for name, raw in self.old.items(): self.write_new(self.directory / ('old-' + name), base64.b64decode(raw), 0o600)
        values = {name: base64.b64decode(request[name], validate=True) for name in ('ca', 'certificate', 'key')}
        old_ca = base64.b64decode(request['old_ca'], validate=True)
        self.s.require(self.s.sha(old_ca) == OLD_CA, 'TLS_ORIGINAL_CA_REQUIRED')
        for name, data in {**values, 'old-ca': old_ca}.items(): self.write_new(self.directory / name, data, 0o600)
        self.run('openssl', 'verify', '-purpose', 'sslserver', '-verify_hostname', 'localhost',
                 '-CAfile', str(self.directory / 'ca'), str(self.directory / 'certificate'))
        self.run('openssl', 'verify', '-purpose', 'sslserver', '-verify_hostname', 'localhost',
                 '-CAfile', str(self.directory / 'old-ca'), str(self.directory / 'old-certificate'))
        ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(self.directory / 'certificate', self.directory / 'key')
        self.new_sha = self.s.sha(values['certificate'])
        self.s.require(self.new_sha != OLD_LEAF, 'TLS_NEW_IDENTITY_REQUIRED')
        return {'status': 'PASS', 'certificate_sha256': self.new_sha}

    def activate(self, request):
        self.s.require(self.directory is not None and self.new_sha and not self.changed, 'TLS_STAGE_FIRST')
        self.s.require(self.file(ROOT / 'pilot.crt', 0o644) == self.file(self.directory / 'old-certificate', 0o600)
                       and self.file(CONFIG / 'tls.key', 0o600) == self.file(self.directory / 'old-key', 0o600), 'TLS_PAIR_DRIFT')
        self.changed = True
        self.replace(ROOT / 'pilot.crt', self.file(self.directory / 'certificate', 0o600), 0o644)
        self.replace(CONFIG / 'tls.key', self.file(self.directory / 'key', 0o600), 0o600)
        self.run('systemctl', 'restart', PROXY)
        return {'status': 'PASS'}

    def verify(self, request):
        self.s.require(self.changed and not self.committed, 'TLS_ACTIVE_WINDOW_REQUIRED')
        after = self.guard()
        for field in ('runtime', 'listeners', 'configuration'):
            self.s.require(after[field] == self.before[field], 'TLS_UNRELATED_STATE_CHANGED')
        self.s.require(all(after['services'][name] == self.before['services'][name]
                           for name in SERVICES if name != PROXY), 'TLS_FOREIGN_SERVICE_RESTARTED')
        self.s.require(self.s.sha(self.file(ROOT / 'pilot.crt', 0o644)) == self.new_sha
                       and self.file(CONFIG / 'tls.key', 0o600) == self.file(self.directory / 'key', 0o600), 'TLS_INSTALLED_PAIR_CHANGED')
        left, right = self.before['database'], after['database']
        self.s.require(all(left[name] == right[name] for name in ('schema_sha256', 'database_format')), 'TLS_SCHEMA_CHANGED')
        allowed = AUTH_CHANGES if request.get('after_login') is True else set()
        self.s.require(left['tables'].keys() == right['tables'].keys()
                       and all(left['tables'][name] == row for name, row in right['tables'].items() if name not in allowed),
                       'TLS_PRESERVED_DATA_CHANGED')
        if not allowed: self.s.require(left == right, 'TLS_EXACT_DATABASE_CHANGED')
        else:
            self.s.require(after['audit_prefix_sha256'] == self.before['audit_prefix_sha256']
                           and after['audit_max'] >= self.before['audit_max'], 'TLS_EXISTING_AUDIT_CHANGED')
            for name, previous in left['sequence_state'].items():
                current = right['sequence_state'].get(name)
                self.s.require(current is not None and (current == previous or
                    name == 'competence_hub.audit_events_id_seq' and current['last_value'] >= previous['last_value']),
                    'TLS_UNRELATED_SEQUENCE_CHANGED')
        self.verified = request.get('after_login') is True
        return {'status': 'PASS', 'data': 'BUSINESS_IDENTITY_SCHEMA_UNCHANGED' if allowed else 'ALL_27_TABLES_EXACT',
                'services': 'PASS', 'rollback_files_retained': True}

    def rollback(self):
        if not self.changed or self.committed: return {'status': 'NO_MUTATION'}
        self.run('openssl', 'x509', '-in', str(self.directory / 'old-certificate'), '-checkend', '0', '-noout')
        self.replace(ROOT / 'pilot.crt', self.file(self.directory / 'old-certificate', 0o600), 0o644)
        self.replace(CONFIG / 'tls.key', self.file(self.directory / 'old-key', 0o600), 0o600)
        self.run('systemctl', 'restart', PROXY)
        self.s.require(self.s.sha(self.file(ROOT / 'pilot.crt', 0o644)) == OLD_LEAF, 'TLS_ROLLBACK_CERTIFICATE_MISMATCH')
        self.guard()
        self.changed = False
        return {'status': 'PASS', 'old_files_retained': True}

    def commit(self, request):
        self.s.require(self.changed and getattr(self, 'verified', False) and request.get('client_checks') is True,
                       'TLS_COMPLETE_ACCEPTANCE_REQUIRED')
        self.committed = True
        return {'status': 'ACKNOWLEDGED'}


def serve(protocol):
    agent = TLSAgent(protocol)
    try:
        while True:
            request = protocol.read_frame(sys.stdin.buffer)
            action = request.get('action')
            if action == 'close': break
            try:
                protocol.require(action in {'inspect', 'stage', 'activate', 'verify', 'commit', 'rollback'}, 'TLS_ACTION_REJECTED')
                result = agent.rollback() if action == 'rollback' else getattr(agent, action)(request)
                protocol.write_frame(sys.stdout.buffer, {'ok': True, 'result': result})
            except BaseException as error:
                try: rollback = agent.rollback()
                except BaseException: rollback = {'status': 'REVIEW_REQUIRED'}
                code = str(error) if isinstance(error, protocol.SnapshotStop) else 'TLS_PRIVATE_OPERATION_FAILED'
                protocol.write_frame(sys.stdout.buffer, {'ok': False, 'code': code, 'rollback': rollback})
                break
    finally:
        if agent.changed and not agent.committed:
            agent.rollback()
