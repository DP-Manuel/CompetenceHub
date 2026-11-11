"""In-memory root agent for approved prechange backup + own isolated restore only.

No arbitrary SQL/RPC, file writes, migrations, accounts, configuration or services.
Source DB is always read-only. Never run directly: private operator injects the
reviewed read-only preflight module and owns the binary SSH pipe.
"""
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import threading
from uuid import uuid4

DATABASE = 'competence_hub_staging'
MAX_BYTES = 64 * 1024 * 1024 - 4096
FRAME_BOUND = 96 * 1024 * 1024


class SnapshotStop(RuntimeError):
    pass


def require(value, code):
    if not value:
        raise SnapshotStop(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def exact(stream, length):
    result = bytearray()
    while len(result) < length:
        block = stream.read(min(length - len(result), 65536))
        if not block:
            raise SnapshotStop('PRIVATE_CHANNEL_CLOSED')
        result.extend(block)
    return bytes(result)


def read_frame(stream):
    size = struct.unpack('!I', exact(stream, 4))[0]
    require(0 < size <= FRAME_BOUND, 'PRIVATE_FRAME_BOUND')
    return json.loads(exact(stream, size))


def write_frame(stream, value):
    data = canonical(value)
    require(len(data) <= FRAME_BOUND, 'PRIVATE_FRAME_BOUND')
    stream.write(struct.pack('!I', len(data)) + data)
    stream.flush()


ENVIRONMENT = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C.UTF-8'}


def run(*args, data=None):
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=180, env=ENVIRONMENT, cwd='/')
    require(result.returncode == 0, 'PRIVATE_POSTGRES_COMMAND_FAILED')
    if 'pg_dump' in args or 'pg_restore' in args:
        require(not result.stderr, 'POSTGRES_ARCHIVE_WARNING_REQUIRES_REVIEW')
    return result.stdout


def sql(statement, database='postgres'):
    return run('runuser', '-u', 'postgres', '--', 'psql', '-X', '-qAt', '-w',
               '-v', 'ON_ERROR_STOP=1', '-d', database, data=statement.encode()).strip()


class ReadSnapshot:
    def __init__(self, database):
        require(database == DATABASE or re.fullmatch(r'ch_restore_[a-f0-9]{32}', database), 'DATABASE_SCOPE')
        self.process = subprocess.Popen(
            ['runuser', '-u', 'postgres', '--', 'psql', '-X', '-qAt', '-w', '-v', 'ON_ERROR_STOP=1', '-d', database],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=ENVIRONMENT, cwd='/',
        )
        self.timer = threading.Timer(180, self.process.kill)
        self.timer.start()
        try:
            self.query("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY; SET LOCAL statement_timeout='30s'; SET LOCAL lock_timeout='3s'")
        except Exception:
            self.close()
            raise

    def lines(self, statement):
        marker = ('CH_END_' + uuid4().hex).encode()
        self.process.stdin.write(statement.encode() + b';\n\\echo ' + marker + b'\n')
        self.process.stdin.flush()
        total = 0
        while True:
            line = self.process.stdout.readline(8 * 1024 * 1024 + 1)
            require(bool(line), 'PRIVATE_SQL_SESSION_CLOSED')
            if line.rstrip(b'\r\n') == marker:
                break
            total += len(line)
            require(len(line) <= 8 * 1024 * 1024 and total <= 256 * 1024 * 1024, 'PRIVATE_SQL_RESULT_BOUND')
            yield line

    def query(self, statement):
        return b''.join(self.lines(statement)).strip()

    def close(self):
        self.timer.cancel()
        if self.process.poll() is None:
            self.process.stdin.close()  # EOF rolls back the read-only transaction.
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process.stdout.close()


@contextmanager
def snapshot_connection(database):
    connection = ReadSnapshot(database)
    try:
        yield connection
    finally:
        connection.close()


CATALOG = """SELECT json_build_object(
 'schemas',(SELECT json_agg(x) FROM (SELECT nspname,pg_get_userbyid(nspowner) AS owner,
   (SELECT json_agg(a ORDER BY grantor,grantee,privilege_type,is_grantable) FROM
    (SELECT pg_get_userbyid(grantor) AS grantor,CASE WHEN grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(grantee) END AS grantee,
     privilege_type,is_grantable FROM aclexplode(COALESCE(nspacl,acldefault('n',nspowner)))) a) AS grants,
   obj_description(oid,'pg_namespace') AS comment FROM pg_namespace WHERE nspname IN ('public','competence_hub')) x),
 'relations',(SELECT json_agg(x) FROM (SELECT n.nspname,c.relname,c.relkind,pg_get_userbyid(c.relowner) AS owner,
   c.relrowsecurity,c.relforcerowsecurity,c.reloptions,obj_description(c.oid,'pg_class') AS comment,
   (SELECT json_agg(a ORDER BY grantor,grantee,privilege_type,is_grantable) FROM
    (SELECT pg_get_userbyid(grantor) AS grantor,CASE WHEN grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(grantee) END AS grantee,
     privilege_type,is_grantable FROM aclexplode(COALESCE(c.relacl,acldefault(CASE WHEN c.relkind='S' THEN 'S'::"char" ELSE 'r'::"char" END,c.relowner)))) a) AS grants
   FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
   WHERE n.nspname IN ('public','competence_hub') AND c.relkind IN ('r','p','v','m','S','f')) x),
 'columns',(SELECT json_agg(x) FROM (SELECT n.nspname,c.relname,a.attname,a.attnum,format_type(a.atttypid,a.atttypmod) AS type,
   a.attnotnull,a.attidentity,a.attgenerated,pg_get_expr(d.adbin,d.adrelid) AS expression,col_description(c.oid,a.attnum) AS comment
   FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace
   LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
   WHERE n.nspname IN ('public','competence_hub') AND c.relkind IN ('r','p','v','m') AND a.attnum>0 AND NOT a.attisdropped) x),
 'constraints',(SELECT json_agg(x) FROM (SELECT n.nspname,c.relname,k.conname,pg_get_constraintdef(k.oid) AS definition
   FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
   WHERE n.nspname IN ('public','competence_hub')) x),
 'indexes',(SELECT json_agg(x) FROM (SELECT schemaname,tablename,indexname,indexdef FROM pg_indexes
   WHERE schemaname IN ('public','competence_hub')) x),
 'functions',(SELECT json_agg(x) FROM (SELECT n.nspname,p.oid::regprocedure::text AS name,pg_get_functiondef(p.oid) AS definition,
   pg_get_userbyid(p.proowner) AS owner,
   (SELECT json_agg(a ORDER BY grantor,grantee,privilege_type,is_grantable) FROM
    (SELECT pg_get_userbyid(grantor) AS grantor,CASE WHEN grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(grantee) END AS grantee,
     privilege_type,is_grantable FROM aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner)))) a) AS grants
   FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
   WHERE n.nspname IN ('public','competence_hub') AND p.prokind IN ('f','p')) x),
 'triggers',(SELECT json_agg(x) FROM (SELECT n.nspname,c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid) AS definition
   FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
   WHERE n.nspname IN ('public','competence_hub') AND NOT t.tgisinternal) x),
 'sequences',(SELECT json_agg(x) FROM (SELECT schemaname,sequencename,sequenceowner,data_type,start_value,
   min_value,max_value,increment_by,cycle,cache_size FROM pg_sequences WHERE schemaname IN ('public','competence_hub')) x),
 'defaults',(SELECT json_agg(x) FROM (SELECT pg_get_userbyid(d.defaclrole) AS role,n.nspname,d.defaclobjtype,
   (SELECT json_agg(a ORDER BY grantor,grantee,privilege_type,is_grantable) FROM
    (SELECT pg_get_userbyid(grantor) AS grantor,CASE WHEN grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(grantee) END AS grantee,
     privilege_type,is_grantable FROM aclexplode(d.defaclacl)) a) AS grants
   FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace
   WHERE d.defaclrole IN (SELECT oid FROM pg_roles WHERE rolname LIKE 'competence_hub_%')) x)
)"""


def signature(connection):
    schemas = json.loads(connection.query("SELECT json_agg(nspname ORDER BY nspname) FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname<>'information_schema'"))
    require(schemas == ['competence_hub', 'public'], 'UNREVIEWED_SCHEMA')
    # Current 0006 is intentionally bounded; unknown storage/features need review.
    unsupported = int(connection.query("""SELECT
      (SELECT count(*) FROM pg_largeobject_metadata) +
      (SELECT count(*) FROM pg_extension WHERE extname<>'plpgsql') +
      (SELECT count(*) FROM pg_tables WHERE schemaname='public') +
      (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname IN ('public','competence_hub') AND c.relkind IN ('f','m','v','p')) +
      (SELECT count(*) FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
        WHERE n.nspname IN ('public','competence_hub') AND t.typtype IN ('d','e','r','m'))"""))
    require(unsupported == 0, 'UNREVIEWED_DATABASE_FEATURE')
    tables = json.loads(connection.query("SELECT json_agg(tablename ORDER BY tablename) FROM pg_tables WHERE schemaname='competence_hub'"))
    rows = {}
    for name in tables:
        require(re.fullmatch('[a-z][a-z0-9_]*', name), 'UNREVIEWED_IDENTIFIER')
        digest = hashlib.sha256()
        for line in connection.lines(f'''COPY (SELECT row_to_json(t)::text FROM competence_hub.{name} t ORDER BY row_to_json(t)::text COLLATE "C") TO STDOUT'''):
            digest.update(line)
        rows[name] = {'count': int(connection.query(f'SELECT count(*) FROM competence_hub.{name}')),
                      'sha256': digest.hexdigest()}
    catalog = json.loads(connection.query(CATALOG))
    sequence_state = {}
    for sequence in catalog['sequences'] or []:
        schema, name = sequence['schemaname'], sequence['sequencename']
        require(re.fullmatch('[a-z][a-z0-9_]*', name) and schema in {'public', 'competence_hub'}, 'UNREVIEWED_SEQUENCE')
        sequence_state[schema + '.' + name] = json.loads(connection.query(
            f"SELECT json_build_object('last_value',last_value,'is_called',is_called) FROM {schema}.{name}"))
    # Compare effective grants and complete records, never array order or OIDs.
    normalized = {key: None if value is None else sorted(value, key=lambda row: canonical(row))
                  for key, value in catalog.items()}
    database_format = json.loads(connection.query("""SELECT json_build_object(
      'encoding',pg_encoding_to_char(encoding),'collate',datcollate,'ctype',datctype,
      'locale_provider',datlocprovider) FROM pg_database WHERE datname=current_database()"""))
    return {'tables': rows, 'schema_sha256': sha(canonical(normalized)),
            'database_format': database_format, 'sequence_state': sequence_state}


def validate_inventory(inventory):
    require(inventory.get('status') == 'PASS' and inventory.get('scope') == 'READ_ONLY', 'CURRENT_PREFLIGHT_REQUIRED')
    db = inventory['database']
    require(db['database'] == DATABASE and db['migrations'] == [f'{i:04}' for i in range(1, 7)]
            and len(db['table_owners']) == 27 and db['database_bytes'] < MAX_BYTES,
            'EXACT_CURRENT_0006_TARGET_REQUIRED')
    require(all(count == 0 for name, count in db['counts'].items() if name not in {'roles', 'schema_migrations'})
            and db['other_sessions'] == 0, 'QUIET_EMPTY_DYNAMIC_DATABASE_REQUIRED')
    require(inventory['services']['competence-hub-api.service']['LoadState'] == 'not-found'
            and not inventory['paths']['/etc/competence-hub/webapp.env']['exists']
            and not inventory['paths']['/opt/competence-hub']['exists'], 'UNREVIEWED_EXISTING_APPLICATION')


class BackupAgent:
    def __init__(self, preflight, *, inventory_validator=None):
        self.preflight = preflight
        self.inventory_validator = inventory_validator or validate_inventory
        self.baseline = None
        self.dump_sha256 = None
        self.probe = None
        self.restore_attempted = False

    def capture(self):
        require(self.baseline is None, 'NO_AUTOMATIC_REPEAT')
        inventory = self.preflight.collect()
        self.inventory_validator(inventory)
        with snapshot_connection(DATABASE) as connection:
            exported = connection.query('SELECT pg_export_snapshot()').decode()
            require(re.fullmatch('[0-9A-Fa-f-]+', exported), 'EXPORTED_SNAPSHOT_REQUIRED')
            properties = json.loads(connection.query("""SELECT json_build_object(
              'owner',pg_get_userbyid(datdba),'encoding',pg_encoding_to_char(encoding),
              'collate',datcollate,'ctype',datctype,'acl',datacl::text)
              FROM pg_database WHERE datname=current_database()"""))
            require(properties['owner'] == 'competence_hub_owner' and properties['encoding'] == 'UTF8',
                    'UNREVIEWED_DATABASE_PROPERTIES')
            baseline = signature(connection)
            dump = run('runuser', '-u', 'postgres', '--', 'pg_dump', '-w', '-Fc',
                       '--snapshot=' + exported, '--lock-wait-timeout=5s', '-d', DATABASE)
        require(dump.startswith(b'PGDMP') and len(dump) <= MAX_BYTES, 'DUMP_FORMAT_OR_BOUND')
        self.baseline, self.dump_sha256 = baseline, sha(dump)
        return {'dump': base64.b64encode(dump).decode(), 'dump_sha256': self.dump_sha256,
                'baseline': baseline, 'source_inventory': inventory,
                'rollback_database_properties': properties, 'global_role_passwords_exported': False,
                'configuration_capture': 'API_UNIT_ENV_ABSENT_KEYFILES_UNTOUCHED'}

    def restore(self, request):
        require(self.baseline is not None and self.probe is None and not self.restore_attempted, 'BOUND_BACKUP_REQUIRED')
        self.restore_attempted = True
        require(request.get('encrypted_copy_verified') is True
                and re.fullmatch('[a-f0-9]{64}', request.get('ciphertext_sha256', '')), 'EXACT_ENCRYPTED_COPY_REQUIRED')
        dump = base64.b64decode(request['dump'], validate=True)
        require(len(dump) <= MAX_BYTES and sha(dump) == self.dump_sha256, 'EXACT_REREAD_DUMP_REQUIRED')
        with snapshot_connection(DATABASE) as connection:
            require(signature(connection) == self.baseline, 'SOURCE_CHANGED_SINCE_SNAPSHOT')
        data_directory = Path(sql('SHOW data_directory').decode())
        require(data_directory.is_absolute(), 'POSTGRES_STORAGE_METADATA_REQUIRED')
        require(min(shutil.disk_usage(data_directory).free,
                    shutil.disk_usage(data_directory / 'pg_wal').free) >= 1024 ** 3,
                'VPS_RESTORE_CAPACITY_INSUFFICIENT')
        name = 'ch_restore_' + uuid4().hex
        # Created without connections; revoke before opening, owner is postgres
        # so app/migrator cannot inherit database-owner CONNECT through a role.
        require(sql(f"SELECT count(*) FROM pg_database WHERE datname='{name}'") == b'0', 'PROBE_NAME_ALREADY_EXISTS')
        self.probe = name
        try:
            sql(f'CREATE DATABASE {name} WITH TEMPLATE template0 OWNER postgres ALLOW_CONNECTIONS false')
            sql(f'REVOKE ALL ON DATABASE {name} FROM PUBLIC; ALTER DATABASE {name} ALLOW_CONNECTIONS true')
            private = sql(f"SELECT NOT has_database_privilege('competence_hub_app','{name}','CONNECT') AND NOT has_database_privilege('competence_hub_migrator','{name}','CONNECT')")
            require(private == b't', 'RESTORE_DATABASE_NOT_PRIVATE')
            run('runuser', '-u', 'postgres', '--', 'pg_restore', '-w', '--exit-on-error',
                '--single-transaction', '-d', name, data=dump)
            require(sql(f"SELECT NOT has_database_privilege('competence_hub_app','{name}','CONNECT') AND NOT has_database_privilege('competence_hub_migrator','{name}','CONNECT')") == b't',
                    'RESTORED_DATABASE_NOT_PRIVATE')
            with snapshot_connection(name) as connection:
                restored = signature(connection)
            require(restored == self.baseline, 'RESTORE_DATA_SCHEMA_RIGHTS_MISMATCH')
            with snapshot_connection(DATABASE) as connection:
                require(signature(connection) == self.baseline, 'SOURCE_CHANGED_DURING_RESTORE')
            return {'status': 'PASS', 'table_count': len(restored['tables']),
                    'all_row_hashes_equal': True, 'schema_rights_equal': True,
                    'sequence_state_equal': True, 'database_format_equal': True,
                    'server_capacity_checked': True,
                    'source_unchanged': True, 'probe_app_migrator_connect_denied': True,
                    'database_acl_intentionally_private': True}
        finally:
            self.cleanup()

    def cleanup(self):
        if self.probe is not None:
            require(re.fullmatch('ch_restore_[a-f0-9]{32}', self.probe), 'OWNED_PROBE_ID_REQUIRED')
            exists = sql(f"SELECT count(*) FROM pg_database WHERE datname='{self.probe}'")
            if exists == b'1':
                sql(f'DROP DATABASE {self.probe}')  # No FORCE/termination or source restore.
            exists = sql(f"SELECT count(*) FROM pg_database WHERE datname='{self.probe}'")
            require(exists == b'0', 'PROBE_CLEANUP_UNPROVEN')
            self.probe = None


def serve(preflight):
    require(os.name == 'posix' and os.geteuid() == 0, 'PRIVATE_ROOT_REQUIRED')
    agent = BackupAgent(preflight)
    try:
        while True:
            request = read_frame(sys.stdin.buffer)
            action = request.get('action')
            if action == 'capture':
                result = agent.capture()
            elif action == 'restore':
                result = agent.restore(request)
                result['probe_removed'] = agent.probe is None
            elif action == 'postflight':
                result = preflight.collect()
            elif action == 'close':
                write_frame(sys.stdout.buffer, {'status': 'CLOSED'})
                break
            else:
                raise SnapshotStop('ACTION_OUTSIDE_BACKUP_RESTORE_SCOPE')
            write_frame(sys.stdout.buffer, {'ok': True, 'result': result})
    except Exception as error:
        # No exception, row value, SQL driver diagnostic, dump or secret output.
        try:
            code = str(error) if isinstance(error, SnapshotStop) and re.fullmatch('[A-Z0-9_]+', str(error)) else 'PRIVATE_BACKUP_RESTORE_STOP'
            write_frame(sys.stdout.buffer, {'ok': False, 'code': code, 'owned_probe': agent.probe})
        except Exception:
            pass
    finally:
        agent.cleanup()
