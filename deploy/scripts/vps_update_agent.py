"""One private V1 update. No installer, source restore, migration or real users."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import socket
import stat
import sys
import time
import venv
import zipfile
from urllib.parse import urlsplit

SOURCE = 'bc53775b08dc'
PACKAGE_SHA = '21849d1e2f33b6044e6a93fdc27fb3ab39f5b5bd7bea047ba73fed99e8d5df97'
ROOT = Path('/opt/competence-hub-pilot')
CONFIG = Path('/etc/competence-hub-pilot')
API = 'competence-hub-pilot-api.service'
PROXY = 'competence-hub-pilot-proxy.service'
DROP = Path('/etc/systemd/system') / (API + '.d')
RELEASE = ROOT / 'releases' / SOURCE
RUNTIME_DROP = DROP / '20-v1-runtime.conf'
CAPTURE_DROP = DROP / '21-v1-synthetic-capture.conf'
CAPTURE_ENV = CONFIG / 'v1-synthetic-capture.env'
LEAF_SHA = 'aecd310881202f9438b14a9d57d7f3e033bf947416a460fa3263fa44cf71d27a'
OLD_WHEEL_SHA = 'a614ff69100641419a47cc068543bd65c31ff20c56989adaadffe9460f0dd646'
RESUME_RUN = '2b834613c4204c1d98a37cbd43134fa1'
PREVIOUS_RELEASE = ROOT
PREVIOUS_RUNTIME_DROP = None
SYNTHETIC_INVITATION_CAPTURE = True


def configure_v11():
    """Only the explicitly approved immutable V1 -> V1.1 transition."""
    global SOURCE, PACKAGE_SHA, RELEASE, RUNTIME_DROP, CAPTURE_DROP, CAPTURE_ENV
    global OLD_WHEEL_SHA, PREVIOUS_RELEASE, PREVIOUS_RUNTIME_DROP, SYNTHETIC_INVITATION_CAPTURE
    SOURCE='38153c12159e'
    PACKAGE_SHA='2a1a7c6109fb2011411297b91a4ff673ac312a561cb847963357df08b80b8ab5'
    RELEASE=ROOT/'releases'/SOURCE
    PREVIOUS_RELEASE=ROOT/'releases'/'bc53775b08dc'
    PREVIOUS_RUNTIME_DROP=DROP/'20-v1-runtime.conf'
    RUNTIME_DROP=DROP/'22-v11-runtime.conf'
    CAPTURE_DROP=DROP/'23-v11-synthetic-capture.conf'
    CAPTURE_ENV=CONFIG/'v11-synthetic-capture.env'
    OLD_WHEEL_SHA='30b211b07a45ae99154808deb46092b19ddcc1caab22364d58fc6ac4eb299dcf'
    SYNTHETIC_INVITATION_CAPTURE=False


def runtime_override(release):
    return ('[Service]\nExecStart=\nExecStart='+str(release/'venv/bin/uvicorn')+
            ' competence_hub_api.runtime:create_runtime_app_from_environment --factory --host 127.0.0.1 --port 8001 --proxy-headers --forwarded-allow-ips=127.0.0.1 --no-access-log\n').encode()


def parse_environment(raw):
    result={}
    for line in raw.decode().splitlines():
        key,separator,value=line.partition('=')
        words=shlex.split(value)
        if not separator or not re.fullmatch('COMPETENCE_HUB_[A-Z_]+',key) or len(words)!=1 or key in result:
            raise ValueError('PRIVATE_ENVIRONMENT_FORMAT')
        result[key]=words[0]
    return result


class UpdateAgent:
    def __init__(self, preflight, snapshot, legacy):
        self.p, self.s, self.legacy = preflight, snapshot, legacy
        self.snapshot = snapshot.BackupAgent(preflight, inventory_validator=self.validate_inventory)
        self.ready = self.recovered = self.changed = self.committed = False
        self.runtime_drop_owned = self.capture_drop_owned = self.capture_env_owned = False
        self.fixture = None
        self.seeded = False
        self.worker = None
        self.started = time.time()

    def require(self, value, code):
        self.s.require(value, code)

    def validate_inventory(self, value):
        db = value['database']
        self.require(value['status']=='PASS' and db['migrations']==[f'{n:04}' for n in range(1,7)]
                     and db['database']==self.s.DATABASE and len(db['table_owners'])==27
                     and db['database_bytes']<self.s.MAX_BYTES, 'CURRENT_0006_REQUIRED')
        self.require(db['counts']['portal_users']==4 and db['counts']['coaches']==2,
                     'EXACT_EXISTING_SYNTHETIC_REFERENCE_REQUIRED')

    def private_file(self, path):
        info=path.lstat()
        self.require(stat.S_ISREG(info.st_mode) and info.st_uid==0 and stat.S_IMODE(info.st_mode)==0o600,
                     'ORIGINAL_PRIVATE_FILE_CUSTODY_REQUIRED')
        return path.read_bytes()

    def collect(self):
        value=self.p.collect()
        self.validate_inventory(value)
        for name in (API,PROXY):
            raw=self.p.command('systemctl','show',name,'-p','LoadState','-p','ActiveState','-p','SubState')
            record=dict(line.split('=',1) for line in raw.splitlines() if '=' in line)
            self.require(record.get('ActiveState')=='active', 'EXISTING_PILOT_SERVICE_REQUIRED')
            value['services'][name]=record
        self.require({'127.0.0.1:8001','127.0.0.1:8443'} <= set(value['listeners']), 'EXISTING_LOOPBACK_PILOT_REQUIRED')
        for port in (':8001',':8443'):
            self.require(all(x.startswith('127.0.0.1:') for x in value['listeners'] if x.endswith(port)), 'PUBLIC_PILOT_REJECTED')
        for name in ('competence-hub-token-worker.service','competence-hub-token-worker.timer'):
            state=self.s.run('systemctl','show',name,'-p','ActiveState','--value').strip()
            self.require(state in (b'inactive',b'failed'), 'NO_DELIVERY_WORKER_REQUIRED')
        value['pilot']='EXISTING_PRIVATE_PILOT'
        return value

    def preflight(self, request):
        self.require(not self.ready, 'NO_AUTOMATIC_REPEAT')
        value=self.collect()
        resume=request.get('resume_run')==RESUME_RUN
        if PREVIOUS_RUNTIME_DROP is not None:
            self.require(not request.get('resume_run') and not RELEASE.exists() and DROP.is_dir() and not DROP.is_symlink()
                         and set(DROP.iterdir())=={PREVIOUS_RUNTIME_DROP},'EXACT_PREVIOUS_V1_RUNTIME_REQUIRED')
            info=PREVIOUS_RUNTIME_DROP.lstat()
            self.require(stat.S_ISREG(info.st_mode) and info.st_uid==0 and stat.S_IMODE(info.st_mode)==0o644,
                         'PREVIOUS_V1_OVERRIDE_CUSTODY_REQUIRED')
            self.require(PREVIOUS_RUNTIME_DROP.read_bytes()==runtime_override(PREVIOUS_RELEASE), 'PREVIOUS_V1_OVERRIDE_CHANGED')
            self.require(not (CONFIG/'v1-synthetic-capture.env').exists() and not CAPTURE_ENV.exists(), 'DELIVERY_CAPTURE_MUST_BE_ABSENT')
            self.require(not PREVIOUS_RELEASE.is_symlink() and PREVIOUS_RELEASE.is_dir(), 'PREVIOUS_V1_RELEASE_REQUIRED')
            active=self.p.command('systemctl','show',API,'-p','DropInPaths','--value').strip()
            self.require(active==str(PREVIOUS_RUNTIME_DROP),'PREVIOUS_V1_ACTIVE_OVERRIDE_REQUIRED')
        else:
            self.require(resume or not RELEASE.exists() and not DROP.exists(), 'EXISTING_UPDATE_REQUIRES_REVIEW')
        if resume:
            self.require(RELEASE.is_dir() and not RELEASE.is_symlink() and DROP.is_dir() and not DROP.is_symlink()
                         and not any(DROP.iterdir()) and not CAPTURE_ENV.exists(), 'ROLLED_BACK_RUNTIME_REQUIRED')
        for name, expected in self.legacy.units().items():
            self.require((Path('/etc/systemd/system')/name).read_bytes()==expected.encode(), 'ORIGINAL_SERVICE_UNIT_CHANGED')
        self.require(self.s.sha((ROOT/'pilot.crt').read_bytes())==LEAF_SHA, 'ORIGINAL_TLS_CHANGED')
        for path in (CONFIG,ROOT):
            self.require(not path.is_symlink() and path.is_dir(), 'ORIGINAL_DIRECTORY_REQUIRED')
        custody=CONFIG.stat()
        self.require(custody.st_uid==0 and stat.S_IMODE(custody.st_mode)==0o700,'ORIGINAL_CONFIG_DIRECTORY_CUSTODY_REQUIRED')
        for path in (ROOT,ROOT/'releases',DROP.parent,PREVIOUS_RELEASE,*((DROP,) if PREVIOUS_RUNTIME_DROP else ()),*((RELEASE,) if resume else ())):
            if path.exists():
                info=path.lstat()
                self.require(stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not stat.S_IMODE(info.st_mode)&0o022,
                             'ORIGINAL_RUNTIME_DIRECTORY_CUSTODY_REQUIRED')
        config={name:base64.b64encode(self.private_file(CONFIG/name)).decode()
                for name in ('runtime.env','tls.key','owned-identities.json','worker.sha256')}
        self.original_config={name:self.s.sha(base64.b64decode(data)) for name,data in config.items()}
        environment=parse_environment(base64.b64decode(config['runtime.env']))
        url=urlsplit(environment.get('COMPETENCE_HUB_DATABASE_URL','').replace('postgresql+asyncpg:','postgresql:'))
        self.require((url.hostname,url.port,url.path,url.username)==('127.0.0.1',5432,'/competence_hub_staging','competence_hub_app')
                     and url.password and not url.query and not any(k.startswith('COMPETENCE_HUB_SMTP') for k in environment), 'EXACT_PRIVATE_STAGING_CONFIG_REQUIRED')
        self.require(environment.get('COMPETENCE_HUB_ALLOWED_ORIGIN')=='https://localhost:8447'
                     and environment.get('COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED')=='false', 'ORIGINAL_PRIVATE_CONFIG_REQUIRED')
        owned=json.loads(base64.b64decode(config['owned-identities.json']))
        ids=','.join("'"+str(__import__('uuid').UUID(x))+"'" for x in owned['users'].values())
        count=self.p.sql("SELECT count(*) FROM competence_hub.portal_users WHERE id IN ("+ids+") AND email ~ '^synthetic-vps-[a-f0-9]{32}@example[.]invalid$'")
        self.require(count=='4', 'NON_SYNTHETIC_REFERENCE_REJECTED')
        wheels=list((PREVIOUS_RELEASE/'bundle/packages').glob('*.whl'))
        self.require(len(wheels)==1 and self.s.sha(wheels[0].read_bytes())==OLD_WHEEL_SHA,'ORIGINAL_ROLLBACK_WHEEL_REQUIRED')
        self.require(sys.version_info[:2]==(3,12),'ORIGINAL_PYTHON_RUNTIME_REQUIRED')
        with zipfile.ZipFile(wheels[0]) as wheel:
            for name in wheel.namelist():
                if name.startswith('competence_hub_api/') and not name.endswith('/'):
                    installed=PREVIOUS_RELEASE/'venv/lib/python3.12/site-packages'/name
                    self.require(not installed.is_symlink() and self.s.sha(installed.read_bytes())==self.s.sha(wheel.read(name)), 'ORIGINAL_ROLLBACK_CODE_CHANGED')
        self.before=value
        self.ready=True
        # This opaque copy goes only through the protected operator pipe/DPAPI.
        return {'status':'PASS','inventory':value,'configuration':config,'configuration_hashes':self.original_config,
                'migrations_required':[],'rollback_wheel_sha256':OLD_WHEEL_SHA,'server_time':time.time()}

    def capture(self, request):
        self.require(self.ready and not self.changed, 'PREFLIGHT_FIRST')
        result=self.snapshot.capture()
        result['configuration_capture']='EXISTING_ORIGINAL_CONFIGURATION_PROTECTED_SEPARATELY'
        self.baseline=self.snapshot.baseline
        return result

    def restore(self, request):
        self.require(self.ready and not self.changed, 'RECOVERY_BEFORE_UPDATE')
        result=self.snapshot.restore(request)
        self.recovered=result['status']=='PASS' and self.snapshot.probe is None
        result['probe_removed']=self.snapshot.probe is None
        return result

    def write_new(self,path,data,mode=0o644):
        allowed=path.is_relative_to(RELEASE) or path in (RUNTIME_DROP,CAPTURE_DROP,CAPTURE_ENV)
        self.require(allowed and not path.is_symlink(), 'OWNED_UPDATE_PATH_ONLY')
        self.require(not any(parent.is_symlink() for parent in path.parents),'UPDATE_PARENT_LINK_REJECTED')
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o755)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
        for owned,flag in ((RUNTIME_DROP,'runtime_drop_owned'),(CAPTURE_DROP,'capture_drop_owned'),(CAPTURE_ENV,'capture_env_owned')):
            if path==owned:setattr(self,flag,True)
        with os.fdopen(fd,'wb') as stream:
            os.fchmod(stream.fileno(),mode);stream.write(data);stream.flush();os.fsync(stream.fileno())

    def stage(self, request):
        self.require(self.recovered and not self.changed and not RELEASE.exists(), 'VERIFIED_CURRENT_RESTORE_FIRST')
        self.require(re.fullmatch('[a-f0-9]{64}',request.get('protected_configuration_sha256','')), 'PROTECTED_CONFIGURATION_COPY_REQUIRED')
        with self.s.snapshot_connection(self.s.DATABASE) as c:
            self.require(self.s.signature(c)==self.baseline, 'SOURCE_CHANGED_BEFORE_UPDATE')
        package=base64.b64decode(request['package'],validate=True)
        self.require(self.s.sha(package)==PACKAGE_SHA, 'EXACT_V1_PACKAGE_REQUIRED')
        previous=os.umask(0o022)
        try:
            with zipfile.ZipFile(io.BytesIO(package)) as archive:
                manifest=json.loads(archive.read('MANIFEST.json').decode('utf-8-sig'))
                self.require(manifest['commit']==SOURCE and not manifest['dirty'], 'EXACT_V1_SOURCE_REQUIRED')
                files={row['path']:row for row in manifest['files']}
                self.require(set(archive.namelist())==set(files)|{'MANIFEST.json'}, 'EXACT_PACKAGE_INVENTORY_REQUIRED')
                for name in archive.namelist():
                    p=PurePosixPath(name)
                    self.require(not p.is_absolute() and '..' not in p.parts and '\\' not in name, 'PACKAGE_PATH_REJECTED')
                    data=archive.read(name)
                    if name in files:self.require(len(data)==files[name]['bytes'] and self.s.sha(data)==files[name]['sha256'], 'PACKAGE_FILE_HASH')
                    self.write_new(RELEASE/'bundle'/name,data)
            pins={re.sub('[-_.]+','-',line.split('==')[0]).lower():line.split('==')[1]
                  for line in (RELEASE/'bundle/requirements-production.lock').read_text().splitlines() if line and not line.startswith('#')}
            seen=set();requirements=[]
            for wheel in request['wheels']:
                name=wheel['file'];data=base64.b64decode(wheel['data'],validate=True)
                self.require(re.fullmatch(r'[A-Za-z0-9_.+-]+\.whl',name) and wheel['name'] not in seen
                             and pins.get(wheel['name'])==wheel['version'] and self.s.sha(data)==wheel['sha256'], 'LOCKED_WHEEL_REQUIRED')
                self.write_new(RELEASE/'wheels'/name,data);seen.add(wheel['name'])
                requirements.append(wheel['name']+'=='+wheel['version']+' --hash=sha256:'+wheel['sha256'])
            self.require(seen==set(pins), 'COMPLETE_WHEELHOUSE_REQUIRED')
            self.write_new(RELEASE/'wheels/runtime.hashes',('\n'.join(requirements)+'\n').encode())
            venv.create(RELEASE/'venv',with_pip=True)
            python=str(RELEASE/'venv/bin/python')
            self.s.run(python,'-m','pip','--isolated','install','--no-index','--require-hashes','--find-links',str(RELEASE/'wheels'),'-r',str(RELEASE/'wheels/runtime.hashes'))
            wheels=list((RELEASE/'bundle/packages').glob('*.whl'))
            self.require(len(wheels)==1,'ONE_APPLICATION_WHEEL_REQUIRED')
            self.s.run(python,'-m','pip','--isolated','install','--no-index','--no-deps',str(wheels[0]))
            self.s.run(python,'-m','pip','check')
        finally:os.umask(previous)
        self.worker=request['worker']
        self.fixture=request['fixture']
        self.rate_reference=self.worker_action('reference_rates')['sha256']
        self.changed=True
        self.write_new(RUNTIME_DROP,runtime_override(RELEASE))
        self.runtime_drop_owned=True
        if SYNTHETIC_INVITATION_CAPTURE:
            self.write_new(CAPTURE_ENV,b'COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED=true\n',0o600);self.capture_env_owned=True
            self.write_new(CAPTURE_DROP,('[Service]\nEnvironmentFile='+str(CAPTURE_ENV)+'\n').encode());self.capture_drop_owned=True
        self.s.run('systemd-analyze','verify',str(Path('/etc/systemd/system')/API))
        self.worker_action('seed')
        self.seeded=True
        self.s.run('systemctl','daemon-reload');self.s.run('systemctl','restart',API)
        return {'status':'PASS','migrations':[],'original_configuration':'UNCHANGED','mail_worker':'ABSENT'}

    def worker_action(self, action, **values):
        self.require(self.worker is not None and self.fixture is not None, 'OWNED_COHORT_REQUIRED')
        code='import base64;exec(compile(base64.b64decode('+repr(base64.b64encode(self.worker.encode()).decode())+"),'<reviewed-v1-worker>','exec'))"
        # Existing application keys are passed only in this root-owned process pipe.
        environment=parse_environment(self.private_file(CONFIG/'runtime.env'))
        raw=self.s.run('runuser','-u','postgres','--',str(RELEASE/'venv/bin/python'),'-I','-c',code,
                       data=self.s.canonical({'action':action,'fixture':self.fixture,'environment':environment,**values}))
        return json.loads(raw)

    def disable_capture(self):
        for path,flag in ((CAPTURE_DROP,'capture_drop_owned'),(CAPTURE_ENV,'capture_env_owned')):
            if getattr(self,flag):path.unlink();setattr(self,flag,False)

    def start_api(self):
        self.s.run('systemctl','start',API)
        deadline=time.monotonic()+45
        while True:
            try:
                with socket.create_connection(('127.0.0.1',8001),timeout=.5):return
            except OSError:
                self.require(time.monotonic()<deadline,'PILOT_API_LISTENER_NOT_READY')
                time.sleep(.2)

    def resume(self, request):
        self.require(request.get('resume_run')==RESUME_RUN,'EXACT_ACCEPTED_RESUME_REQUIRED')
        result=self.preflight(request)
        self.require(result['configuration_hashes']==request['configuration_hashes'],'RESUME_CONFIGURATION_CHANGED')
        expected=request['baseline']
        self.require(len(expected['tables'])==27 and expected['tables']['auth_rate_limit_buckets']['count']==0,
                     'RESUME_EMPTY_FOREIGN_RATE_BASELINE_REQUIRED')
        with self.s.snapshot_connection(self.s.DATABASE) as c:current=self.s.signature(c)
        without_rates=lambda tables:{k:v for k,v in tables.items() if k!='auth_rate_limit_buckets'}
        self.require(current['schema_sha256']==expected['schema_sha256']
                     and current['database_format']==expected['database_format']
                     and without_rates(current['tables'])==without_rates(expected['tables']), 'RESUME_REFERENCE_CHANGED')
        self.require(all(current['sequence_state'][k]['last_value']>=v['last_value']
                         for k,v in expected['sequence_state'].items()),'SEQUENCE_REWIND_REJECTED')
        package=base64.b64decode(request['package'],validate=True)
        self.require(self.s.sha(package)==PACKAGE_SHA,'EXACT_V1_PACKAGE_REQUIRED')
        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            manifest=json.loads(archive.read('MANIFEST.json').decode('utf-8-sig'))
            self.require(manifest['commit']==SOURCE and not manifest['dirty'],'EXACT_V1_SOURCE_REQUIRED')
            for row in manifest['files']:
                name=PurePosixPath(row['path'])
                self.require(not name.is_absolute() and '..' not in name.parts and '\\' not in row['path'],'PACKAGE_PATH_REJECTED')
                path=RELEASE/'bundle'/row['path']
                self.require(not any(p.is_symlink() for p in (path,*path.parents)),'STAGED_LINK_REJECTED')
                self.require(self.s.sha(path.read_bytes())==row['sha256'],'STAGED_RELEASE_CHANGED')
        wheels=list((RELEASE/'bundle/packages').glob('*.whl'))
        self.require(len(wheels)==1,'ONE_APPLICATION_WHEEL_REQUIRED')
        with zipfile.ZipFile(wheels[0]) as wheel:
            for name in wheel.namelist():
                if name.startswith('competence_hub_api/') and not name.endswith('/'):
                    path=RELEASE/'venv/lib/python3.12/site-packages'/name
                    self.require(not any(p.is_symlink() for p in (path,*path.parents))
                                 and self.s.sha(path.read_bytes())==self.s.sha(wheel.read(name)),'STAGED_APPLICATION_CHANGED')
        self.s.run(str(RELEASE/'venv/bin/python'),'-m','pip','check')
        self.worker=request['worker'];self.fixture=request['fixture'];self.baseline=current
        self.resume_log_since=request['previous_start']
        self.require(isinstance(self.resume_log_since,(int,float)) and time.time()-7*86400<=self.resume_log_since<=time.time(),
                     'RESUME_LOG_WINDOW_REJECTED')
        self.rate_reference=self.worker_action('reference_rates')['sha256']
        self.require(self.rate_reference==hashlib.sha256(b'[]').hexdigest(),'RESUME_FOREIGN_RATE_BUCKET_CHANGED')
        self.changed=True;self.resume_mode=True
        self.write_new(RUNTIME_DROP,('[Service]\nExecStart=\nExecStart='+str(RELEASE/'venv/bin/uvicorn')+
            ' competence_hub_api.runtime:create_runtime_app_from_environment --factory --host 127.0.0.1 --port 8001 --proxy-headers --forwarded-allow-ips=127.0.0.1 --no-access-log\n').encode())
        self.s.run('systemd-analyze','verify',str(Path('/etc/systemd/system')/API))
        self.s.run('systemctl','daemon-reload');self.s.run('systemctl','restart',API)
        return {'status':'PASS','reference':'VERIFIED','installation':'REUSED_UNCHANGED','database_writes':'NONE',
                'backup_restore':'REUSED_ACCEPTED','original_configuration':'UNCHANGED'}

    def finalize_resume(self, request):
        self.require(self.changed and getattr(self,'resume_mode',False),'ACTIVE_RESUME_REQUIRED')
        with self.s.snapshot_connection(self.s.DATABASE) as c:
            self.require(self.s.signature(c)==self.baseline,'RESUME_DATABASE_CHANGED')
        inventory=self.collect()
        self.require(set(inventory['listeners'])==set(self.before['listeners']),'UNEXPECTED_LISTENER_CHANGE')
        for name,digest in self.original_config.items():
            self.require(self.s.sha(self.private_file(CONFIG/name))==digest,'ORIGINAL_CONFIGURATION_CHANGED')
        self.check_logs(request.get('secret_needles',[]),self.resume_log_since)
        self.postflight_passed=True
        return {'status':'PASS','database_unchanged':True,'reference':'PASS','services':'PASS','configuration':'UNCHANGED',
                'invitation_delivery':'CLOSED','logs_secret_scan':'PASS','migrations':[],'inventory':inventory}

    def check_logs(self, needles, since):
        journal=self.s.run('journalctl','-q','-u',API,'-u',PROXY,'--since','@'+str(int(since)),'-n','1000','-o','cat')
        environment=parse_environment(self.private_file(CONFIG/'runtime.env'))
        self.require(not any(x.encode() in journal for x in list(environment.values())+needles
                             if isinstance(x,str) and len(x)>=16),'SECRET_IN_OWN_LOG')

    def reference_check(self):
        with self.s.snapshot_connection(self.s.DATABASE) as c:after=self.s.signature(c)
        self.require(after['schema_sha256']==self.baseline['schema_sha256'],'SCHEMA_CHANGED')
        self.require({k:v for k,v in after['tables'].items() if k!='auth_rate_limit_buckets'}==
                     {k:v for k,v in self.baseline['tables'].items() if k!='auth_rate_limit_buckets'}, 'REFERENCE_ROWS_CHANGED_NO_SOURCE_RESTORE')
        self.require(all(after['sequence_state'][k]['last_value']>=v['last_value'] for k,v in self.baseline['sequence_state'].items()),'SEQUENCE_REWIND_REJECTED')
        self.require(self.worker_action('reference_rates')['sha256']==self.rate_reference,'FOREIGN_RATE_BUCKET_CHANGED')
        return {'status':'PASS','tables_preserved':26,'shared_synthetic_ip_rate_counters':'RETAINED_NOT_RESET','sequences':'NOT_REWOUND'}

    def commit(self, request):
        self.require(self.changed and not self.committed, 'UPDATE_REQUIRED')
        self.s.run('systemctl','stop',API)
        self.require(self.seeded,'OWNED_SEED_ACK_REQUIRED')
        self.worker_action('cleanup')
        self.seeded=False
        preserved=self.reference_check()
        self.disable_capture()
        self.s.run('systemctl','daemon-reload');self.start_api()
        inventory=self.collect()
        self.require(set(inventory['listeners'])==set(self.before['listeners']),'UNEXPECTED_LISTENER_CHANGE')
        for name in self.original_config:
            self.require(self.s.sha(self.private_file(CONFIG/name))==self.original_config[name], 'ORIGINAL_CONFIGURATION_CHANGED')
        self.check_logs(request.get('secret_needles',[]),self.started)
        self.postflight_passed=True
        return {'status':'PASS','reference':preserved,'services':'PASS','configuration':'UNCHANGED','migrations':[],
                'listeners_unchanged':True,'logs_secret_scan':'PASS','invitation_delivery':'CLOSED'}

    def rollback(self):
        if not self.changed:return {'status':'NO_MUTATION','staged_files_retained':RELEASE.exists()}
        failures=[]
        try:
            self.s.run('systemctl','stop',API)
            self.require(self.s.run('systemctl','show',API,'-p','ActiveState','--value').strip() in (b'inactive',b'failed'),'API_STOP_UNPROVEN')
            if self.seeded:
                self.worker_action('cleanup');self.seeded=False
            if hasattr(self,'rate_reference'):self.reference_check()
        except Exception:failures.append('DATA_COMPENSATION_REVIEW_REQUIRED')
        try:
            self.disable_capture()
            if self.runtime_drop_owned:RUNTIME_DROP.unlink();self.runtime_drop_owned=False
            self.s.run('systemctl','daemon-reload');self.start_api()
            self.collect()
        except Exception:failures.append('CODE_ROLLBACK_REVIEW_REQUIRED')
        return {'status':'REVIEW_REQUIRED' if failures else 'PASS','failures':failures,
                'source_restore_performed':False,'owned_files_retained':True,'sequences_not_rewound':True}


def serve(preflight,snapshot,legacy):
    snapshot.require(os.name=='posix' and os.geteuid()==0,'PRIVATE_ROOT_REQUIRED')
    agent=UpdateAgent(preflight,snapshot,legacy)
    try:
        while True:
            request=snapshot.read_frame(sys.stdin.buffer);action=request.get('action')
            if action in ('preflight','capture','restore','stage','commit','resume','finalize_resume'):
                result=getattr(agent,action)(request)
            elif action=='clock':result={'server_time':time.time()}
            elif action=='restart':
                agent.require(agent.changed,'ACTIVE_UPDATE_REQUIRED');snapshot.run('systemctl','restart',API);result={'status':'PASS'}
            elif action in ('expire','invitation_token'):
                result=agent.worker_action(action,**{k:v for k,v in request.items() if k!='action'})
            elif action=='accept':
                agent.require(getattr(agent,'postflight_passed',False),'FINAL_POSTFLIGHT_REQUIRED')
                agent.committed=True;result={'status':'PASS'}
            elif action=='close':
                result={'status':'PASS','committed':agent.committed}
                if agent.changed and not agent.committed:result['rollback']=agent.rollback();agent.changed=False
                snapshot.write_frame(sys.stdout.buffer,{'ok':True,'result':result});return
            else:raise snapshot.SnapshotStop('UPDATE_ACTION_REJECTED')
            snapshot.write_frame(sys.stdout.buffer,{'ok':True,'result':result})
    except Exception as error:
        if agent.committed:return
        code=str(error) if isinstance(error,snapshot.SnapshotStop) and re.fullmatch('[A-Z0-9_]+',str(error)) else 'PRIVATE_UPDATE_FAILED'
        try:rollback=agent.rollback();agent.changed=False
        except Exception:rollback={'status':'REVIEW_REQUIRED'}
        snapshot.write_frame(sys.stdout.buffer,{'ok':False,'code':code,'rollback':rollback,'owned_probe':agent.snapshot.probe})
    finally:
        agent.snapshot.cleanup()
        if agent.changed and not agent.committed:agent.rollback()
