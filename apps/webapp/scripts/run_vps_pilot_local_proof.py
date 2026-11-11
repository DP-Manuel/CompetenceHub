"""Synthetic local Linux rehearsal, no VPS/DPAPI/keyfile/credential access."""
import argparse
import base64
import importlib.util
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import traceback
from uuid import uuid4
import zipfile

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('pilot_operator',Path(__file__).with_name('run_vps_pilot.py'))
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)


def main(v1_update=False,rollback_probe=False):
    name='ch-pilot-proof-'+uuid4().hex
    directory=ROOT/'.tmp'/name;directory.mkdir()
    docker=['docker','--host','npipe:////./pipe/dockerDesktopLinuxEngine']
    def command(*args,data=None):return pilot.backup.checked(*args,data=data,timeout=240)
    report={'scope':'OWNED_LOCAL_SYNTHETIC_ONLY','status':'STOP','service_manager':'PROCESS_SHIM_NOT_SYSTEMD',
            'vps_changed':False,'original_keyfiles_accessed':False}
    process=None
    try:
        port=18447 if v1_update else 8447
        if v1_update:pilot.acceptance.ORIGIN='https://localhost:18447'
        command(*docker,'run','-d','--name',name,'-p','127.0.0.1:'+str(port)+':18443',
                'sha256:17228a886f219fb43029846aa744aa7b5a2e7885cb1dae7a8efcb55519e16543')
        for path in ('staging_readonly_preflight.py','staging_snapshot_agent.py','vps_pilot_agent.py'):
            command(*docker,'cp',str(ROOT/'deploy/scripts'/path),name+':/work/'+path)
        if v1_update:
            command(*docker,'cp',str(ROOT/'deploy/scripts/vps_update_agent.py'),name+':/work/vps_update_agent.py')
            update_source=(ROOT/'deploy/scripts/vps_update_agent.py').read_text(encoding='utf8').replace('8447','18447')
            command(*docker,'exec','-i',name,'python3','-c',"import sys;from pathlib import Path;Path('/work/vps_update_agent.py').write_bytes(sys.stdin.buffer.read())",data=update_source.encode())
            command(*docker,'exec',name,'touch','/work/UPDATE_REHEARSAL_ONLY')
        command(*docker,'cp',str(ROOT/'deploy/rehearsal/pilot_install_probe.py'),name+':/work/probe.py')
        command(*docker,'exec',name,'touch','/work/LOCAL_REHEARSAL_ONLY')
        command(*docker,'exec',name,'pg_ctlcluster','16','main','start','-o','-c listen_addresses=127.0.0.1')
        with zipfile.ZipFile(pilot.PACKAGE) as archive:
            sql=[archive.read('database/bootstrap-staging.sql')]+[archive.read(path) for path in sorted(archive.namelist()) if path.startswith('database/migrations/000') and path.split('/')[-1][:4]<='0006']
        for index,statement in enumerate(sql):
            command(*docker,'exec','-i',name,'runuser','-u','postgres','--','psql','-X','-v','ON_ERROR_STOP=1','-d',
                    'postgres' if index==0 else 'competence_hub_staging',data=statement)
        password=secrets.token_hex(32)
        command(*docker,'exec','-i',name,'runuser','-u','postgres','--','psql','-X','-v','ON_ERROR_STOP=1','-d','postgres',
                data=("ALTER ROLE competence_hub_app PASSWORD '"+password+"';").encode())
        code="import sys;sys.path.insert(0,'/work');import staging_snapshot_agent as s;\nwith s.snapshot_connection(s.DATABASE) as c: print(s.canonical(s.signature(c)).decode())"
        baseline=json.loads(command(*docker,'exec',name,'python3','-c',code))
        process=subprocess.Popen([*docker,'exec','-i',name,'python3','-u','/work/probe.py'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        assert process.stdout.readline()==b'LOCAL_PROBE_READY\n'
        class Session:
            def request(self,action,**values):
                pilot.backup.protocol.write_frame(process.stdin,{'action':action,**values})
                result=pilot.backup.protocol.read_frame(process.stdout)
                if not result.get('ok'):raise AssertionError(result)
                return result['result']
        root=Session()
        root.request('preflight',baseline=baseline)
        inventory=json.loads((pilot.WHEELS/'INVENTORY.json').read_bytes())
        payload={'package':base64.b64encode(pilot.PACKAGE.read_bytes()).decode(),
                 'wheels':[{**row,'data':base64.b64encode((pilot.WHEELS/row['file']).read_bytes()).decode()} for row in inventory['files']],
                 'worker':(ROOT/'deploy/scripts/vps_pilot_worker.py').read_text(),
                 'corpus':base64.b64encode(b'0'*64+b'\n').decode()}
        # Corpus binding is fixed in production; inject synthetic expected hash
        # only into the owned local module, never the reviewed VPS payload.
        local=(ROOT/'deploy/scripts/vps_pilot_agent.py').read_text().replace(
            '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da',pilot.sha(b'0'*64+b'\n'))
        if v1_update:local=local.replace('8447','18447')
        # Module is already running; restart before the first owned mutation.
        process.stdin.close();process.wait(timeout=15);process.stdout.close();process.stderr.close()
        command(*docker,'exec','-i',name,'python3','-c',"import sys;from pathlib import Path;Path('/work/vps_pilot_agent.py').write_bytes(sys.stdin.buffer.read())",data=local.encode())
        process=subprocess.Popen([*docker,'exec','-i',name,'python3','-u','/work/probe.py'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        assert process.stdout.readline()==b'LOCAL_PROBE_READY\n'
        root.request('preflight',baseline=baseline)
        root.request('stage',**payload)
        keys={name:base64.b64encode(secrets.token_bytes(32)).decode() for name in ('COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY','COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY')}
        for stem in ('TOTP','OUTBOX','RECOVERY_HMAC'):
            keys['COMPETENCE_HUB_'+stem+'_KEYRING']=json.dumps({'probe':base64.b64encode(secrets.token_bytes(32)).decode()})
            keys['COMPETENCE_HUB_'+stem+'_ACTIVE_KEY_VERSION']='probe'
        ca,leaf,key=pilot.certificates();ca_path=directory/'ca.pem';ca_path.write_bytes(ca)
        policy=directory/'policy.json';policy.write_bytes(pilot.canonical({'policies':{'Certificates':{'Install':[str(ca_path)]}}}))
        os.environ['PLAYWRIGHT_FIREFOX_POLICIES_JSON']=str(policy)
        variables={**keys,'COMPETENCE_HUB_DATABASE_URL':'postgresql+asyncpg://competence_hub_app:'+password+'@127.0.0.1:5432/competence_hub_staging',
                   'COMPETENCE_HUB_ALLOWED_ORIGIN':pilot.acceptance.ORIGIN,'COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED':'false'}
        configuration={'variables':variables,'tls_key':key.decode(),'tls_certificate':leaf.decode()}
        configured=root.request('configure',**configuration)
        data=pilot.fixture()
        if v1_update:data['reference_seed_only']=True
        root.request('activate',configuration_sha256=configured['configuration_sha256'],protected_configuration_sha256='a'*64,
                     fixture=data,rate_key=keys['COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY'])
        for _ in range(100):
            try:
                if pilot.acceptance.HTTPS(ca_path).call('/health/ready')[0]==200:break
            except OSError:pass
            time.sleep(.2)
        else:raise AssertionError('Local native readiness')
        if not v1_update:pilot.tls_negatives(ca_path)
        private=pilot.acceptance.run(root,data,ca_path,directory,report)
        if not v1_update:
            demo=pilot.open_demo(data,private,root.request('clock')['server_time']-time.time(),headless=True)
            try:assert len(demo[1].contexts)==4
            finally:demo[1].close();demo[0].stop()
            report['automatic_role_login']='PASS'
        else:report['reference_checks']=list(report['checks'])
        report['postflight']=root.request('postflight')
        report['postflight']['services']='LOCAL_PROCESS_SHIM_ONLY_NOT_FOREIGN_VPS_HEALTH'
        if v1_update:
            updater=pilot.module('local_v1_operator',Path(__file__).with_name('run_vps_update.py'))
            updater.pilot.acceptance.ORIGIN=pilot.acceptance.ORIGIN
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            root.request('commit');root.request('close')
            old=root.request('preflight')
            capture=root.request('capture');dump=base64.b64decode(capture.pop('dump'))
            # Synthetic platform substitute only. Actual operator uses DPAPI/ACL/BitLocker.
            cipher=AESGCM(secrets.token_bytes(32));nonce=secrets.token_bytes(12)
            encrypted=nonce+cipher.encrypt(nonce,dump,b'local-synthetic-only')
            path=directory/'synthetic-probe.aes';path.write_bytes(encrypted)
            reread=path.read_bytes();recovered=cipher.decrypt(reread[:12],reread[12:],b'local-synthetic-only')
            assert recovered==dump
            restored=root.request('restore',dump=base64.b64encode(recovered).decode(),encrypted_copy_verified=True,ciphertext_sha256=pilot.sha(reread))
            assert restored['status']=='PASS' and restored['probe_removed']
            data=updater.fixture();payload=updater.payload()
            root.request('stage',**payload,fixture=data,protected_configuration_sha256=pilot.sha(pilot.canonical(old['configuration'])))
            updater.wait_ready(ca_path)
            if rollback_probe:
                rolled=root.request('close')
                assert rolled['rollback']['status']=='PASS'
                updater.wait_ready(ca_path)
                assert pilot.acceptance.HTTPS(ca_path).call('/portal/user-management.js')[0]==404
                report.update(status='PASS',v1_rollback=rolled['rollback'],recovery_platform='SYNTHETIC_AES_NOT_DPAPI')
                process.stdin.close();process.wait(timeout=30);process.stdout.close();process.stderr.close();process=None
                return
            private=pilot.acceptance.run(root,data,ca_path,directory,report)
            private=updater.v1.run(root,data,ca_path,directory,report,private,pilot.acceptance)
            report['v1_postflight']=root.request('commit',secret_needles=[v['totp'] for v in private.values()])
            assert report['v1_postflight']['reference']['status']=='PASS'
            # Final code is V1, source reference rows survived native MFA/CAL/Admin tests.
            updater.wait_ready(ca_path)
            assert b'createUserManagement' in pilot.acceptance.HTTPS(ca_path).call('/portal/user-management.js')[2]
            closed=pilot.acceptance.HTTPS(ca_path).call('/api/v1/admin/users/invitations','POST',{})
            assert closed[0]==503 and json.loads(closed[2])['code']=='invitation_delivery_unavailable'
            root.request('accept');root.request('close')
            report['v1_update']='PASS'
            process.stdin.close();process.wait(timeout=30);process.stdout.close();process.stderr.close();process=None
            report.update(status='PASS',exact_fixture_cleanup='OWNED_V1_ONLY_REFERENCE_RETAINED',recovery_platform='SYNTHETIC_AES_NOT_DPAPI')
            return
        # Do not commit local services: EOF exercises scoped rollback.
        process.stdin.close();process.wait(timeout=30);process.stdout.close();process.stderr.close();process=None
        after=json.loads(command(*docker,'exec',name,'python3','-c',code))
        assert after['tables']==baseline['tables'] and after['schema_sha256']==baseline['schema_sha256']
        report.update(status='PASS',exact_fixture_cleanup='PASS')
    except Exception as error:
        report['failure_type']=type(error).__name__
        report['failure_location']=[{'file':Path(frame.filename).name,'line':frame.lineno,'function':frame.name}
                                    for frame in traceback.extract_tb(error.__traceback__)][-8:]
        raise
    finally:
        if process is not None:
            if not process.stdin.closed:process.stdin.close()
            try:process.wait(timeout=30)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        command(*docker,'rm','-f',name)
        assert name not in command(*docker,'ps','-a','--format','{{.Names}}').decode().splitlines()
        report['owned_container_removed']=True
        os.environ.pop('PLAYWRIGHT_FIREFOX_POLICIES_JSON',None)
        (directory/'result.json').write_bytes(pilot.canonical(report))
        print('LOCAL_PROOF='+report['status']+' REPORT='+str(directory/'result.json'),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--v1-update',action='store_true')
    parser.add_argument('--v1-rollback',action='store_true');args=parser.parse_args()
    main(args.v1_update or args.v1_rollback,args.v1_rollback)
