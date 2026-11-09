"""Approved isolated service namespace; existing PostgreSQL 0006, synthetic only.

Loaded over the authenticated binary SSH pipe, not a public/admin API.
No backup, migration, real activation, global nginx reload or arbitrary SQL RPC.
"""
import base64
from datetime import datetime, timezone
from functools import wraps
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import sys
import time
from urllib.parse import urlsplit
from uuid import uuid4
import venv
import zipfile

PACKAGE_SHA = 'f3478fc34de4647fd182a9c7262678b8de2e6b194428ec7dbcc0a116d9c51c41'
SOURCE = '0080195755e3'
ROOT = Path('/opt/competence-hub-pilot')
CONFIG = Path('/etc/competence-hub-pilot')
API = 'competence-hub-pilot-api.service'
PROXY = 'competence-hub-pilot-proxy.service'
ORIGIN = 'https://localhost:8447'


def readable_runtime(function):
    @wraps(function)
    def call(*args,**values):
        previous=os.umask(0o022)
        try:return function(*args,**values)
        finally:os.umask(previous)
    return call


def proxy_config(key_path='/run/credentials/' + PROXY + '/tls.key'):
    return '''pid /run/competence-hub-pilot-proxy/nginx.pid;
error_log stderr crit;
worker_processes 1;
events { worker_connections 128; }
http {
 access_log off;
 client_body_temp_path /run/competence-hub-pilot-proxy/body;
 proxy_temp_path /run/competence-hub-pilot-proxy/proxy;
 fastcgi_temp_path /run/competence-hub-pilot-proxy/fastcgi;
 uwsgi_temp_path /run/competence-hub-pilot-proxy/uwsgi;
 scgi_temp_path /run/competence-hub-pilot-proxy/scgi;
 server {
  listen 127.0.0.1:8443 ssl;
  server_name localhost;
  server_tokens off;
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_certificate /opt/competence-hub-pilot/pilot.crt;
  ssl_certificate_key __KEY__;
  client_max_body_size 32k;
  if ($http_host != "localhost:8447") { return 421; }
  location / {
   proxy_pass http://127.0.0.1:8001;
   proxy_set_header Host localhost:8447;
   proxy_set_header X-Forwarded-Host localhost:8447;
   proxy_set_header X-Forwarded-Proto https;
   proxy_set_header X-Forwarded-For $remote_addr;
   proxy_set_header X-Real-IP $remote_addr;
   proxy_connect_timeout 5s;
   proxy_read_timeout 30s;
  }
 }
}
'''.replace('__KEY__', key_path)


def units():
    common = '''Type=simple
DynamicUser=yes
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
UMask=0077
Restart=on-failure
RestartSec=5s
TimeoutStopSec=30s
StandardOutput=journal
StandardError=journal
'''
    api = '''[Unit]
Description=Competence Hub PRIVATE synthetic pilot API
After=postgresql.service network.target
StartLimitBurst=3
[Service]
''' + common + '''User=competencehub-pilot
WorkingDirectory=/opt/competence-hub-pilot
EnvironmentFile=/etc/competence-hub-pilot/runtime.env
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart=/opt/competence-hub-pilot/venv/bin/uvicorn competence_hub_api.runtime:create_runtime_app_from_environment --factory --host 127.0.0.1 --port 8001 --proxy-headers --forwarded-allow-ips=127.0.0.1 --no-access-log
MemoryMax=384M
CPUQuota=50%
[Install]
WantedBy=multi-user.target
'''
    proxy = '''[Unit]
Description=Competence Hub PRIVATE loopback TLS proxy
After=competence-hub-pilot-api.service
StartLimitBurst=3
[Service]
''' + common + '''User=competencehub-pilot-proxy
RuntimeDirectory=competence-hub-pilot-proxy
LoadCredential=tls.key:/etc/competence-hub-pilot/tls.key
ExecStart=/usr/sbin/nginx -c /opt/competence-hub-pilot/nginx.conf -g "daemon off;"
MemoryMax=64M
[Install]
WantedBy=multi-user.target
'''
    return {API: api, PROXY: proxy}


class PilotAgent:
    def __init__(self, preflight, snapshot):
        self.p, self.s = preflight, snapshot
        self.ready = False
        self.staged = False
        self.configured = False
        self.activated = False
        self.committed = False
        self.owned = False
        self.fixture = None
        self.worker = None
        self.started = datetime.now(timezone.utc).isoformat()

    def require(self, value, code):
        self.s.require(value, code)

    def write(self, path, data, mode=0o600):
        self.require(path.is_relative_to(ROOT) or path.is_relative_to(CONFIG)
                     or path.parent == Path('/etc/systemd/system') and path.name in (API, PROXY), 'OWNED_PATH_ONLY')
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
        with os.fdopen(descriptor, 'wb') as stream:
            os.fchmod(stream.fileno(),mode)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())

    def preflight(self, request):
        inventory = self.p.collect()
        self.s.validate_inventory(inventory)
        self.require(sys.version_info[:2] == (3, 12) and platform.machine() == 'x86_64', 'MATCHED_LINUX_RUNTIME_REQUIRED')
        self.require(not ROOT.exists() and not CONFIG.exists()
                     and all(not (Path('/etc/systemd/system') / name).exists() for name in (API, PROXY)), 'PRIOR_PILOT_REQUIRES_RECONCILIATION')
        self.require(not any(value.endswith((':8001', ':8443')) for value in inventory['listeners']), 'OWN_PORTS_MUST_BE_FREE')
        self.require(shutil.disk_usage('/opt').free > 1024 ** 3, 'PILOT_CAPACITY_REQUIRED')
        memory=next(int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
        self.require(memory >= 512*1024,'COHOST_MEMORY_HEADROOM_REQUIRED')
        with self.s.snapshot_connection(self.s.DATABASE) as connection:
            self.require(self.s.signature(connection) == request['baseline'], 'ACCEPTED_SNAPSHOT_NO_LONGER_MATCHES')
        self.before = inventory
        self.baseline = request['baseline']
        self.ready = True
        return {'status': 'PASS', 'schema': inventory['database']['migrations'], 'original_unchanged': True,
                'migrations_required': [], 'server_time': time.time()}

    @readable_runtime
    def stage(self, request):
        self.require(self.ready and not self.staged, 'PREFLIGHT_FIRST_NO_REPEAT')
        package = base64.b64decode(request['package'], validate=True)
        self.require(self.s.sha(package) == PACKAGE_SHA, 'EXACT_RELEASE_REQUIRED')
        ROOT.mkdir(mode=0o755)
        self.owned = True
        CONFIG.mkdir(mode=0o700)
        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            manifest = json.loads(archive.read('MANIFEST.json').decode('utf-8-sig'))
            self.require(manifest['commit'] == SOURCE and not manifest['dirty'], 'RELEASE_SOURCE_REQUIRED')
            files = {row['path']: row for row in manifest['files']}
            self.require(set(archive.namelist()) == set(files) | {'MANIFEST.json'}, 'RELEASE_INVENTORY_REQUIRED')
            for name in archive.namelist():
                path = PurePosixPath(name)
                self.require(not path.is_absolute() and '..' not in path.parts and '\\' not in name, 'RELEASE_PATH_REJECTED')
                data = archive.read(name)
                if name in files:
                    self.require(len(data) == files[name]['bytes'] and self.s.sha(data) == files[name]['sha256'], 'RELEASE_FILE_HASH')
                self.write(ROOT / 'bundle' / name, data, 0o644)
        pins = {}
        for line in (ROOT / 'bundle/requirements-production.lock').read_text().splitlines():
            if line.strip() and not line.startswith('#'):
                name, version = line.split('==')
                pins[re.sub('[-_.]+', '-', name).lower()] = version
        seen, requirements = set(), []
        for wheel in request['wheels']:
            name = wheel['file']
            self.require(re.fullmatch('[A-Za-z0-9_.+-]+\\.whl', name) and wheel['name'] not in seen
                         and pins.get(wheel['name']) == wheel['version'], 'LOCKED_WHEEL_ONLY')
            data = base64.b64decode(wheel['data'], validate=True)
            self.require(self.s.sha(data) == wheel['sha256'], 'WHEEL_HASH')
            self.write(ROOT / 'wheels' / name, data, 0o644)
            seen.add(wheel['name'])
            requirements.append(wheel['name'] + '==' + wheel['version'] + ' --hash=sha256:' + wheel['sha256'])
        self.require(seen == set(pins), 'COMPLETE_LOCKED_WHEELHOUSE_REQUIRED')
        self.write(ROOT / 'wheels/runtime.hashes', ('\n'.join(requirements) + '\n').encode(), 0o644)
        corpus = base64.b64decode(request['corpus'], validate=True)
        self.require(self.s.sha(corpus) == '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da', 'CORPUS_BINDING')
        self.write(ROOT / 'corpus.sha256', corpus, 0o644)
        self.worker = request['worker']
        self.write(CONFIG / 'worker.sha256', self.s.sha(self.worker.encode()).encode())
        venv.create(ROOT / 'venv', with_pip=True)
        python = str(ROOT / 'venv/bin/python')
        self.s.run(python, '-m', 'pip', '--isolated', 'install', '--no-index', '--require-hashes',
                   '--find-links', str(ROOT / 'wheels'), '-r', str(ROOT / 'wheels/runtime.hashes'))
        wheels = list((ROOT / 'bundle/packages').glob('*.whl'))
        self.require(len(wheels) == 1, 'ONE_API_WHEEL_REQUIRED')
        self.s.run(python, '-m', 'pip', '--isolated', 'install', '--no-index', '--no-deps', str(wheels[0]))
        self.s.run(python, '-m', 'pip', 'check')
        self.staged = True
        return {'status': 'PASS', 'package_sha256': PACKAGE_SHA, 'dependencies': len(seen)}

    def configure(self, request):
        self.require(self.staged and not self.configured, 'STAGED_FIRST_NO_REPEAT')
        variables = request['variables']
        url = urlsplit(variables['COMPETENCE_HUB_DATABASE_URL'].replace('postgresql+asyncpg:', 'postgresql:'))
        self.require((url.hostname, url.port, url.path, url.username) == ('127.0.0.1', 5432, '/competence_hub_staging', 'competence_hub_app')
                     and bool(url.password) and not url.query, 'EXACT_APP_DATABASE_ONLY')
        self.require(variables['COMPETENCE_HUB_ALLOWED_ORIGIN'] == ORIGIN
                     and variables['COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED'] == 'false', 'PRIVATE_ORIGIN_DELIVERY_CLOSED')
        self.require(not any(name.startswith('COMPETENCE_HUB_SMTP') for name in variables), 'NO_MAIL_CONFIGURATION')
        variables['COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH'] = str(ROOT / 'corpus.sha256')
        for name, value in variables.items():
            self.require(re.fullmatch('COMPETENCE_HUB_[A-Z_]+', name) and isinstance(value, str)
                         and not any(char in value for char in "\r\n\x00'"), 'ENVIRONMENT_VALUE_BOUND')
        env = ''.join(name + "='" + value.replace('\\', '\\\\') + "'\n" for name, value in variables.items()).encode()
        self.write(CONFIG / 'runtime.env', env)
        self.write(CONFIG / 'tls.key', request['tls_key'].encode())
        self.write(ROOT / 'pilot.crt', request['tls_certificate'].encode(), 0o644)
        self.write(ROOT / 'nginx.conf', proxy_config().encode(), 0o644)
        self.write(CONFIG / 'nginx-preflight.conf', proxy_config(str(CONFIG / 'tls.key')).encode())
        Path('/run/competence-hub-pilot-proxy').mkdir(mode=0o755, exist_ok=False)
        self.s.run('nginx', '-t', '-c', str(CONFIG / 'nginx-preflight.conf'))
        for name, value in units().items():
            self.write(Path('/etc/systemd/system') / name, value.encode(), 0o644)
        self.s.run('systemd-analyze', 'verify', *[str(Path('/etc/systemd/system') / name) for name in (API, PROXY)])
        self.configuration_sha = self.s.sha(self.s.canonical({'variables': variables, 'tls_key': request['tls_key'], 'tls_certificate': request['tls_certificate']}))
        self.secret_needles = [value for value in variables.values() if len(value) >= 24]
        self.configured = True
        return {'status': 'PASS', 'configuration_sha256': self.configuration_sha}

    def worker_action(self, action, **values):
        self.require(self.fixture is not None, 'OWNED_SYNTHETIC_FIXTURE_REQUIRED')
        code = 'import base64;exec(compile(base64.b64decode(' + repr(base64.b64encode(self.worker.encode()).decode()) + "),'<reviewed-synthetic-worker>','exec'))"
        result = self.s.run('runuser', '-u', 'postgres', '--', str(ROOT / 'venv/bin/python'), '-I', '-c', code,
                            data=self.s.canonical({'action': action, 'fixture': self.fixture, **values}))
        return json.loads(result)

    def activate(self, request):
        self.require(self.configured and not self.activated and request['configuration_sha256'] == self.configuration_sha
                     and re.fullmatch('[a-f0-9]{64}', request.get('protected_configuration_sha256', '')), 'VERIFIED_CONFIGURATION_COPY_REQUIRED')
        with self.s.snapshot_connection(self.s.DATABASE) as connection:
            self.require(self.s.signature(connection)==self.baseline,'SOURCE_CHANGED_BEFORE_ACTIVATION')
        self.fixture = request['fixture']
        self.fixture['rate_key'] = request['rate_key']
        self.secret_needles.extend(item['password'] for item in self.fixture['accounts'].values())
        self.write(CONFIG / 'owned-identities.json', self.s.canonical({
            'users': {key: item['id'] for key, item in self.fixture['accounts'].items()},
            'coaches': self.fixture['coaches'], 'topic': self.fixture['topic']}))
        self.worker_action('seed')
        self.s.run('systemctl', 'daemon-reload')
        self.s.run('systemctl', 'start', API)
        self.s.run('systemctl', 'start', PROXY)
        self.activated = True
        return {'status': 'PASS', 'server_time': time.time()}

    def postflight(self, request):
        inventory = self.p.collect()
        self.require(inventory['status']=='PASS','CURRENT_DATABASE_AND_SERVICE_CHECKS_REQUIRED')
        for name in ('migrations','roles','role_memberships','table_owners','privileges','listen_addresses'):
            self.require(inventory['database'][name]==self.before['database'][name],'EXISTING_DATABASE_CONTRACT_CHANGED')
        self.require(all(inventory['services'][name]['ActiveState'] == 'active' for name in self.p.SERVICES[:4]), 'FOREIGN_SERVICE_HEALTH')
        before = set(self.before['listeners'])
        added = set(inventory['listeners']) - before
        self.require(before <= set(inventory['listeners']), 'EXISTING_LISTENER_REMOVED')
        self.require(added == {'127.0.0.1:8001', '127.0.0.1:8443'}, 'UNEXPECTED_LISTENER_CHANGE')
        self.s.run('systemctl', 'is-active', API, PROXY)
        journal = self.s.run('journalctl', '-q', '-u', API, '-u', PROXY, '--since', self.started, '-n', '500', '-o', 'cat')
        needles = self.secret_needles + request.get('secret_needles', [])
        self.require(not any(value.encode() in journal for value in needles if isinstance(value, str) and len(value) >= 16), 'SECRET_IN_OWN_LOGS')
        return {'status': 'PASS', 'services': 'PASS', 'ports': sorted(added),
                'migrations': inventory['database']['migrations'], 'logs_secret_scan': 'PASS',
                'fixture': self.worker_action('inspect')}

    def rollback(self):
        if not self.owned:
            return {'status': 'NO_MUTATION'}
        failures=[]
        stopped=True
        for name in (PROXY, API):
            if (Path('/etc/systemd/system') / name).exists():
                for operation in ('stop','disable'):
                    try:self.s.run('systemctl', operation, name)
                    except Exception:failures.append(operation+'_'+name)
                try:
                    state=self.s.run('systemctl','show','--property=ActiveState','--value',name).strip()
                    if state not in (b'inactive',b'failed'):
                        stopped=False
                except Exception:stopped=False
        if self.fixture is not None and stopped:
            try:self.worker_action('cleanup')
            except Exception:failures.append('fixture_cleanup')
        elif self.fixture is not None:
            failures.append('own_service_stop_unproven_fixture_retained')
        return {'status': 'REVIEW_REQUIRED' if failures else 'PASS', 'failures':failures,
                'owned_files_retained': True, 'source_restore_performed': False,
                'sequences_not_rewound': True}


def serve(preflight, snapshot):
    snapshot.require(os.name == 'posix' and os.geteuid() == 0, 'PRIVATE_ROOT_REQUIRED')
    agent = PilotAgent(preflight, snapshot)
    try:
        while True:
            request = snapshot.read_frame(sys.stdin.buffer)
            action = request.get('action')
            if action in ('preflight', 'stage', 'configure', 'activate', 'postflight'):
                result = getattr(agent, action)(request)
            elif action == 'clock':
                result = {'server_time': time.time()}
            elif action == 'restart':
                agent.require(agent.activated, 'ACTIVE_PILOT_REQUIRED')
                snapshot.run('systemctl', 'restart', API)
                result = {'status': 'PASS'}
            elif action == 'expire':
                result = agent.worker_action('expire', actor=request['actor'])
            elif action == 'commit':
                result = agent.postflight(request)
                snapshot.run('systemctl', 'enable', API, PROXY)
                agent.committed = True
            elif action == 'close':
                result={'status':'PASS','committed':agent.committed}
                if agent.owned and not agent.committed:
                    result['rollback']=agent.rollback()
                    agent.owned=False
                snapshot.write_frame(sys.stdout.buffer,{'ok':True,'result':result})
                return
            else:
                raise snapshot.SnapshotStop('PILOT_ACTION_REJECTED')
            snapshot.write_frame(sys.stdout.buffer, {'ok': True, 'result': result})
    except Exception as error:
        if agent.committed:
            # EOF is normal after acceptance; never undo a committed pilot.
            return
        code = str(error) if isinstance(error, snapshot.SnapshotStop) and re.fullmatch('[A-Z0-9_]+', str(error)) else 'PRIVATE_PILOT_OPERATION_FAILED'
        try:
            rollback = agent.rollback()
            agent.owned = False
        except Exception:
            rollback = {'status': 'REVIEW_REQUIRED', 'owned_files_retained': True}
        snapshot.write_frame(sys.stdout.buffer, {'ok': False, 'code': code, 'rollback': rollback})
    finally:
        if agent.owned and not agent.committed:
            agent.rollback()
