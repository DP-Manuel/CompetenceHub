"""Full approved-backup code path against synthetic PG in an owned local container.

No VPS/SSH authentication, real target directory, user secrets or real key reads.
Systemd health is explicitly simulated; PostgreSQL/DPAPI/ACL/restore are actual.
"""
import argparse
import base64
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
DOCKER = ['docker', '--host', 'npipe:////./pipe/dockerDesktopLinuxEngine']
IMAGE = 'sha256:17228a886f219fb43029846aa744aa7b5a2e7885cb1dae7a8efcb55519e16543'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-local-synthetic', action='store_true')
    options = parser.parse_args()
    if os.name != 'nt' or not options.execute_local_synthetic:
        raise ValueError('EXPLICIT_LOCAL_SYNTHETIC_WINDOWS_PROBE_REQUIRED')
    spec = importlib.util.spec_from_file_location('synthetic_backup_client', ROOT / 'apps/webapp/scripts/protected_staging_backup.py')
    client = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(client)
    container = None
    session = None
    private = Path(tempfile.gettempdir()) / ('ch-synthetic-backup-' + uuid4().hex)
    assert private.parent.resolve() == Path(tempfile.gettempdir()).resolve()
    evidence = ROOT / 'release-artifacts/protected-backup-restore-local'
    evidence.mkdir(exist_ok=True)
    report = {'scope': 'LOCAL_SYNTHETIC_ONLY', 'status': 'STOP', 'phase': 'setup',
              'systemd_health': 'SIMULATED_NOT_VPS_EVIDENCE', 'vps_actions': False}
    def run(*args, data=None):
        result = subprocess.run([*DOCKER, *args], input=data, capture_output=True, timeout=120)
        if result.returncode:
            raise RuntimeError('OWNED_LOCAL_PROBE_COMMAND_FAILED')
        return result.stdout
    try:
        container = run('run', '-d', '--pull', 'never', '--network', 'none', '--memory', '2g',
                        '--label', 'competence-hub.scope=protected-backup-restore-proof', IMAGE).decode().strip()
        assert re.fullmatch('[a-f0-9]{64}', container)
        run('exec', container, 'pg_ctlcluster', '16', 'main', 'start', '-o', '-c listen_addresses=127.0.0.1')
        def sql(data, database):
            return run('exec', '-i', container, 'runuser', '-u', 'postgres', '--', 'psql', '-X', '-q',
                       '-v', 'ON_ERROR_STOP=1', '-d', database, data=data)
        sql((ROOT / 'apps/webapp/database/bootstrap-staging.sql').read_bytes(), 'postgres')
        for path in sorted((ROOT / 'apps/webapp/database/migrations').glob('*.sql')):
            if path.name[:4] <= '0006':
                sql(path.read_bytes(), 'competence_hub_staging')
        session = client.RootSession.__new__(client.RootSession)
        session.process = subprocess.Popen([*DOCKER, 'exec', '-i', container, 'python3', '-I', '-c', client.BOOTSTRAP],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        assert session.process.stdout.readline(64) == b'CH_ROOT_READY_1\n'
        synthetic = '''
def collect():
 db=database_metadata()
 r={'scope':'READ_ONLY','status':'PASS','database':db,
    'services':{name:{'LoadState':'loaded','ActiveState':'active'} for name in SERVICES[:4]},
    'paths':{'/etc/competence-hub/webapp.env':{'exists':False},'/opt/competence-hub':{'exists':False}},
    'listeners':[line.split()[3] for line in command('ss','-ltnH').splitlines()]}
 r['services']['competence-hub-api.service']={'LoadState':'not-found'}
 r['checks']=assess(r)
 if not all(r['checks'].values()):r['status']='STOP'
 return r
'''
        client.protocol.write_frame(session.process.stdin, {
            'preflight': (ROOT / 'deploy/scripts/staging_readonly_preflight.py').read_text(encoding='utf8') + synthetic,
            'agent': (ROOT / 'deploy/scripts/staging_snapshot_agent.py').read_text(encoding='utf8'),
        })
        report['phase'] = 'mvcc_capture'
        capture = session.request('capture')
        dump = base64.b64decode(capture.pop('dump'), validate=True)
        assert client.protocol.sha(dump) == capture['dump_sha256']
        assert len(capture['baseline']['tables']) == 27
        report['phase'] = 'private_acl_dpapi_file'
        acl = str(ROOT / 'deploy/scripts/initialize-staging-operator-config.ps1').replace("'", "''")
        path = str(private).replace("'", "''")
        client.checked('pwsh', '-NoProfile', '-NonInteractive', '-Command',
                       f". '{acl}'; New-StagingPrivateDirectory '{path}'")
        stored = client.private_ciphertext_file(private / 'database.dump.dpapi', client.dpapi.transform(dump))
        baseline = client.private_ciphertext_file(private / 'baseline.json.dpapi', client.dpapi.transform(client.protocol.canonical(capture)))
        restored = client.checked(os.sys.executable, str(ROOT / 'deploy/scripts/windows_dpapi.py'), '--decrypt-stdin', data=stored)
        assert client.protocol.sha(restored) == capture['dump_sha256']
        assert client.dpapi.transform(baseline, decrypt=True) == client.protocol.canonical(capture)
        report['phase'] = 'isolated_restore'
        result = session.request('restore', dump=base64.b64encode(restored).decode(),
                                 encrypted_copy_verified=True, ciphertext_sha256=client.protocol.sha(stored))
        assert result['status'] == 'PASS' and result['probe_removed'] is True
        report['phase'] = 'postflight'
        post = session.request('postflight')
        client.protocol.validate_inventory(post)
        assert post['database']['counts'] == capture['source_inventory']['database']['counts']
        report.update(status='PASS', phase='complete', proof=result,
                      archive_bytes=len(dump), ciphertext_bytes=len(stored),
                      ciphertext_sha256=client.protocol.sha(stored))
    except BaseException as error:
        report['failure_type'] = type(error).__name__
        if isinstance(error, client.protocol.SnapshotStop):
            report['code'] = str(error)
        raise
    finally:
        if session is not None:
            session.close()
        if container and re.fullmatch('[a-f0-9]{64}', container):
            run('rm', '-f', container)
            report['container_removed'] = not run('ps', '-a', '-q', '--no-trunc', '--filter', 'id=' + container).strip()
        # Only these two owned synthetic files; no recursive delete or real target.
        if private.is_dir():
            for name in ('database.dump.dpapi', 'baseline.json.dpapi'):
                (private / name).unlink(missing_ok=True)
            private.rmdir()
        report['synthetic_files_removed'] = not private.exists()
        receipt = evidence / (uuid4().hex + '.json')
        with receipt.open('x', encoding='utf8') as stream:
            json.dump(report, stream, indent=2)
        print(json.dumps(report))
        print('REPORT=' + str(receipt))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        print('LOCAL_SYNTHETIC_BACKUP_PROBE=STOP NO_SECRET_OUTPUT')
        raise SystemExit(1) from None
