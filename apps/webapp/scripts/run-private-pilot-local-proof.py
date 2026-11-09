"""Local-only SSH/HTTPS/native MFA and DPAPI/PostgreSQL restore feasibility.

Uses an exact reviewed package in a disposable Linux container, no host mounts
or published ports. Never connects to the VPS, real DBs, USB or existing keys.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[3]
DOCKER=['docker','--host','npipe:////./pipe/dockerDesktopLinuxEngine']


def digest(data):return hashlib.sha256(data).hexdigest()


def validate_sid(value):
    # Entra accounts use S-1-12, local/domain accounts commonly S-1-5.
    sid=value.strip()
    if not re.fullmatch(r'S-1-[0-9]+(?:-[0-9]+)+',sid):
        raise ValueError('Current Windows user SID unavailable')
    return sid


def canonical_catalog(schema):
    # Catalog collections are sets of complete records, not display order.
    # Repeated trigger names on different tables must not reorder the digest.
    return {key:None if rows is None else sorted(rows,key=lambda row:json.dumps(row,sort_keys=True))
            for key,rows in schema.items()}


def command(*args,data=None,timeout=180,allow_failure=False):
    result=subprocess.run([*DOCKER,*args],input=data,capture_output=True,timeout=timeout)
    if result.returncode and not allow_failure:
        raise RuntimeError('Owned local probe operation failed')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    options=parser.parse_args()
    release=options.release.resolve()
    if (release.parent != ROOT/'release-artifacts/webapp' or not re.fullmatch('[a-f0-9]{64}',options.sha256)
        or digest(release.read_bytes())!=options.sha256):
        raise ValueError('Reviewed local artifact/hash required')
    spec=importlib.util.spec_from_file_location('synthetic_dpapi',ROOT/'deploy/rehearsal/synthetic_dpapi.py')
    dpapi=importlib.util.module_from_spec(spec);spec.loader.exec_module(dpapi)
    evidence=ROOT/'release-artifacts/private-pilot-local-20261109'
    evidence.mkdir(exist_ok=True)
    report={'scope':'LOCAL_SYNTHETIC_ONLY','status':'RUNNING','vps_changed':False,
            'real_backup_target':'NOT_QUALIFIED','checks':[],'release_sha256':options.sha256}
    container=None;restore_name='probe_'+uuid4().hex
    def check(label,ok):
        report['last_check']=label
        if not ok:raise AssertionError(label)
        report['checks'].append(label)
        print('PASS | '+label,flush=True)
    def sql(statement,database='competence_hub_staging'):
        return command('exec','-i',container,'runuser','-u','postgres','--','psql','-X','-q','-v','ON_ERROR_STOP=1','-At','-d',database,data=statement.encode()).stdout
    def snapshot(database):
        tables=json.loads(sql("SELECT json_agg(tablename ORDER BY tablename) FROM pg_tables WHERE schemaname='competence_hub';",database))
        rows={}
        for table in tables:
            if not re.fullmatch('[a-z0-9_]+',table):raise ValueError('Unexpected synthetic table')
            data=sql(f'''COPY (SELECT row_to_json(t)::text FROM competence_hub.{table} t ORDER BY row_to_json(t)::text COLLATE "C") TO STDOUT;''',database)
            rows[table]={'sha256':digest(data),'count':int(sql(f'SELECT count(*) FROM competence_hub.{table};',database))}
        catalog=sql("""SELECT json_build_object(
          'columns',(SELECT json_agg(x ORDER BY table_name,ordinal_position) FROM (SELECT table_name,ordinal_position,column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='competence_hub') x),
          'constraints',(SELECT json_agg(x ORDER BY relation,name) FROM (SELECT conrelid::regclass::text AS relation,conname AS name,pg_get_constraintdef(c.oid) AS definition FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname='competence_hub') x),
          'indexes',(SELECT json_agg(x ORDER BY indexname) FROM (SELECT indexname,indexdef FROM pg_indexes WHERE schemaname='competence_hub') x),
          'owners_acl',(SELECT json_agg(x ORDER BY relname) FROM (SELECT relname,pg_get_userbyid(relowner) AS owner,
            (SELECT json_agg(a ORDER BY grantor,grantee,privilege_type,is_grantable) FROM
              (SELECT pg_get_userbyid(grantor) AS grantor,CASE WHEN grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(grantee) END AS grantee,
                      privilege_type,is_grantable FROM aclexplode(COALESCE(c.relacl,acldefault(CASE WHEN c.relkind='S' THEN 'S'::"char" ELSE 'r'::"char" END,c.relowner)))) a) AS grants
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='competence_hub' AND c.relkind IN ('r','p','S','v','m','f')) x),
          'functions',(SELECT json_agg(x ORDER BY name) FROM (SELECT p.oid::regprocedure::text AS name,pg_get_functiondef(p.oid) AS definition FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='competence_hub') x),
          'triggers',(SELECT json_agg(x ORDER BY relation,name) FROM (SELECT c.relname AS relation,tgname AS name,tgenabled AS enabled,pg_get_triggerdef(t.oid) AS definition FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='competence_hub' AND NOT t.tgisinternal) x));""",database)
        schema=canonical_catalog(json.loads(catalog))
        return {'tables':rows,'schema_sha256':digest(json.dumps(schema,sort_keys=True).encode()),'schema':schema}
    try:
        image='sha256:17228a886f219fb43029846aa744aa7b5a2e7885cb1dae7a8efcb55519e16543'
        command('image','inspect',image)
        container=command('run','-d','--pull','never','--memory','2g','--cpus','2','--label','competence-hub.scope=private-local-proof',image).stdout.decode().strip()
        if not re.fullmatch('[a-f0-9]{64}',container):raise RuntimeError('Owned identity unconfirmed')
        command('cp',str(release),container+':/work/release.zip')
        for name in ('prepare_linux.py','linux_proxy_smoke.py','private_tunnel_smoke.py'):
            command('cp',str(ROOT/'deploy/rehearsal'/name),container+':/work/'+name)
        command('exec',container,'touch','/work/LOCAL_REHEARSAL_ONLY')
        command('exec',container,'apt-get','update',timeout=240)
        command('exec',container,'apt-get','install','-y','--no-install-recommends','openssh-server',timeout=240)
        command('exec',container,'python3','/work/prepare_linux.py',options.sha256,timeout=300)
        command('network','disconnect','bridge',container)
        check('Owned Linux runtime network disconnected; no host mounts or published ports',True)
        command('exec','-d',container,'/opt/competence-hub/current/venv/bin/python','/work/private_tunnel_smoke.py')
        deadline=time.monotonic()+90
        while True:
            if command('exec',container,'test','-f','/work/PRIVATE_FAILED',allow_failure=True).returncode==0:
                raise RuntimeError('Private synthetic tunnel proof failed')
            if command('exec',container,'test','-f','/work/PRIVATE_READY',allow_failure=True).returncode==0:break
            if time.monotonic()>deadline:raise TimeoutError('Private local readiness timed out')
            time.sleep(.3)
        check('Actual OpenSSH + certificate-verified HTTPS + native MFA proof completed',True)
        before=snapshot('competence_hub_staging')
        check('Source snapshot contains synthetic rows, not merely an empty schema',sum(r['count'] for r in before['tables'].values())>20)
        dump=command('exec',container,'runuser','-u','postgres','--','pg_dump','-Fc','-d','competence_hub_staging').stdout
        check('Native pg_dump custom archive held in memory only',dump.startswith(b'PGDMP') and len(dump)<64*1024*1024)
        with tempfile.TemporaryDirectory(prefix='owned-synthetic-',dir=evidence) as temp:
            temp=Path(temp)
            report['phase']='synthetic_snapshot_acl'
            # Current-user ACL only, no inherited broad directory grants.
            sid=validate_sid(subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',
                '[Security.Principal.WindowsIdentity]::GetCurrent().User.Value'],capture_output=True,check=True,text=True).stdout)
            protected=subprocess.run(['icacls',str(temp),'/inheritance:r','/grant:r',f'*{sid}:(OI)(CI)F'],capture_output=True)
            check('Synthetic encrypted snapshot directory restricted to current user',protected.returncode==0)
            encrypted=dpapi.transform(dump)
            report['phase']='synthetic_dpapi_recovery'
            target=temp/'synthetic-only.dump.dpapi'
            with target.open('xb') as stream:stream.write(encrypted)
            stored=target.read_bytes()
            check('Only CurrentUser-DPAPI ciphertext written; SHA-256 reread matches',digest(stored)==digest(encrypted) and not stored.startswith(b'PGDMP'))
            worker=[sys.executable,str(ROOT/'deploy/rehearsal/synthetic_dpapi.py'),'--synthetic-decrypt-stdin']
            recovered=subprocess.run(worker,input=stored,capture_output=True,timeout=30)
            check('Fresh process decrypts exact archive without passphrase dialog',recovered.returncode==0 and digest(recovered.stdout)==digest(dump))
            corrupted=bytearray(stored);corrupted[-1]^=1
            rejected=subprocess.run(worker,input=bytes(corrupted),capture_output=True,timeout=30)
            check('Modified ciphertext rejected without plaintext output',rejected.returncode!=0 and not rejected.stdout)
            command('exec',container,'runuser','-u','postgres','--','createdb','-T','template0',restore_name)
            report['phase']='isolated_restore'
            sql(f'REVOKE ALL ON DATABASE {restore_name} FROM PUBLIC;','postgres')
            command('exec','-i',container,'runuser','-u','postgres','--','pg_restore','--exit-on-error','--single-transaction','-d',restore_name,data=recovered.stdout)
            restored=snapshot(restore_name)
            report['schema_mismatch_parts']=[key for key in before['schema'] if before['schema'][key]!=restored['schema'][key]]
            if report['schema_mismatch_parts']:
                # Static synthetic catalog only; never dump application rows.
                report['synthetic_catalog_differences']={key:{'source':before['schema'][key],'restored':restored['schema'][key]}
                    for key in report['schema_mismatch_parts']}
            check('Restored schema/constraints/indexes/functions/triggers/owners/ACLs match',before['schema_sha256']==restored['schema_sha256'])
            check('Every table count and canonical complete-row hash matches',before['tables']==restored['tables'])
            check('Original source database unchanged by isolated restore',snapshot('competence_hub_staging')==before)
            report.update(archive_bytes=len(dump),ciphertext_bytes=len(stored),archive_sha256=digest(dump),ciphertext_sha256=digest(stored),table_count=len(before['tables']))
            command('exec',container,'runuser','-u','postgres','--','dropdb',restore_name)
            check('Only owned probe database removed; original source remains',snapshot('competence_hub_staging')==before)
        check('Owned synthetic ciphertext directory removed',not temp.exists())
        command('exec',container,'touch','/work/CONTINUE')
        deadline=time.monotonic()+40
        while command('exec',container,'test','-f','/work/private-tunnel-result.json',allow_failure=True).returncode:
            if time.monotonic()>deadline:raise TimeoutError('Local native cleanup timeout')
            time.sleep(.2)
        remote=json.loads(command('exec',container,'cat','/work/private-tunnel-result.json').stdout)
        check('SSH and native proxy cleanup report PASS',remote['status']=='PASS')
        report['tunnel']=remote
        report['status']='PASS'
    except BaseException as error:
        report.update(status='INCOMPLETE',failure_type=type(error).__name__)
        raise
    finally:
        if container and re.fullmatch('[a-f0-9]{64}',container):
            command('rm','-f',container)
            report['container_removed']=not command('ps','-a','-q','--no-trunc','--filter','id='+container).stdout.strip()
        (evidence/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print('PRIVATE_LOCAL_PROOF='+report['status']+' REAL_BACKUP_TARGET=NOT_QUALIFIED VPS_ACTIONS=NONE',flush=True)


if __name__=='__main__':
    try:main()
    except BaseException as error:
        print('LOCAL_STOP='+type(error).__name__+' NO_SECRET_OUTPUT',flush=True)
        raise SystemExit(1) from None
