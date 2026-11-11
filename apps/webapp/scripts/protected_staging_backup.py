"""Approved temporary rollback copy + isolated exact-file restore, never deployment.

Run only through the reviewed elevated PowerShell entry. No GPG, credentials in
arguments, real accounts, keyfile reads, migration, source restore or service edit.
"""
import argparse
import base64
from datetime import datetime, timezone
import getpass
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / 'deploy/scripts'
spec = importlib.util.spec_from_file_location('backup_agent_protocol', SCRIPTS / 'staging_snapshot_agent.py')
protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)
spec = importlib.util.spec_from_file_location('backup_dpapi', SCRIPTS / 'windows_dpapi.py')
dpapi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dpapi)
SSH = ['ssh', '-F', 'NUL', '-T', '-o', 'BatchMode=yes', '-o', 'PasswordAuthentication=no',
       '-o', 'KbdInteractiveAuthentication=no', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'ForwardAgent=no', '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=30',
       'manuel@217.160.255.86']
PREFLIGHT_SHA256 = '1a939f60b7a0e9fd91d6a84e70072bfb5f2ca343de1858865903941a97e37124'

# A short bootstrap avoids Windows command-line length limits. No script file is
# placed on the VPS. Password input ends before the ROOT_READY handshake.
BOOTSTRAP = """import sys,json,struct,types
sys.stdout.buffer.write(b'CH_ROOT_READY_1\\n');sys.stdout.buffer.flush()
def exact(n):
 b=bytearray()
 while len(b)<n:
  x=sys.stdin.buffer.read(n-len(b))
  if not x:raise SystemExit(1)
  b.extend(x)
 return bytes(b)
n=struct.unpack('!I',exact(4))[0]
if not 0<n<131072:raise SystemExit(1)
s=json.loads(exact(n))
p={'__name__':'private_readonly_preflight'}
exec(compile(s['preflight'],'<reviewed-preflight>','exec'),p)
a={'__name__':'private_snapshot_agent'}
exec(compile(s['agent'],'<reviewed-snapshot-agent>','exec'),a)
a['serve'](types.SimpleNamespace(**p))
"""


def require(value, code):
    protocol.require(value, code)


def checked(*args, data=None, timeout=180):
    result = subprocess.run(args, input=data, capture_output=True, timeout=timeout)
    require(result.returncode == 0, 'PRIVATE_LOCAL_COMMAND_FAILED')
    return result.stdout


class RootSession:
    def __init__(self, *, bootstrap_source=None, reviewed_sources=None, progress=None):
        self.process = None
        require(sys.stdin.isatty(), 'PRIVATE_INTERACTIVE_TERMINAL_REQUIRED')
        step=progress or (lambda phase:None)
        step('ssh_connectivity')
        try:
            checked(*SSH, 'true', data=b'', timeout=20)
        except subprocess.TimeoutExpired:
            raise protocol.SnapshotStop('SSH_CONNECTIVITY_TIMEOUT_NO_MUTATION') from None
        step('sudo_capability_probe')
        try:
            probe=subprocess.run([*SSH, 'sudo -n -- true'], input=b'', capture_output=True, timeout=20)
        except subprocess.TimeoutExpired:
            raise protocol.SnapshotStop('SUDO_CAPABILITY_TIMEOUT_NO_MUTATION') from None
        require(probe.returncode in (0,1), 'SUDO_PROBE_TRANSPORT_UNAVAILABLE_NO_MUTATION')
        available = probe.returncode == 0
        step('private_sudo_input' if not available else 'private_root_channel')
        password = None if available else getpass.getpass('VPS sudo password for manuel (hidden; no GPG/USB password): ')
        bootstrap = 'import base64;exec(base64.b64decode(' + repr(base64.b64encode((bootstrap_source or BOOTSTRAP).encode()).decode()) + '))'
        sudo = 'sudo -n -- ' if available else 'sudo -S -p "" -- '
        try:
            step('private_root_channel')
            self.process = subprocess.Popen([*SSH, sudo + 'python3 -I -c "' + bootstrap + '"'],
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if password is not None:
                self.process.stdin.write((password + '\n').encode('utf8'))
                self.process.stdin.flush()
            with self.deadline(30):
                require(self.process.stdout.readline(64) == b'CH_ROOT_READY_1\n', 'SUDO_OR_PRIVATE_CHANNEL_FAILED_NO_RETRY')
            protocol.write_frame(self.process.stdin, reviewed_sources if reviewed_sources is not None else {
                'preflight': (SCRIPTS / 'staging_readonly_preflight.py').read_text(encoding='utf8'),
                'agent': (SCRIPTS / 'staging_snapshot_agent.py').read_text(encoding='utf8'),
            })
        except BaseException:
            self.close()
            raise
        finally:
            password = None

    def deadline(self, seconds):
        from contextlib import contextmanager
        @contextmanager
        def timeout():
            timer = threading.Timer(seconds, self.process.kill)
            timer.start()
            try:
                yield
            finally:
                timer.cancel()
        return timeout()

    def request(self, action, **values):
        with self.deadline(300):
            protocol.write_frame(self.process.stdin, {'action': action, **values})
            result = protocol.read_frame(self.process.stdout)
        code = result.get('code', 'PRIVATE_REMOTE_BACKUP_RESTORE_STOP')
        if result.get('ok') is not True:
            probe = result.get('owned_probe')
            self.last_failure = {'owned_probe': probe if isinstance(probe, str) and re.fullmatch('ch_restore_[a-f0-9]{32}', probe) else None}
            rollback = result.get('rollback')
            if isinstance(rollback, dict) and rollback.get('status') in ('PASS','REVIEW_REQUIRED','NO_MUTATION'):
                self.last_failure['pilot_rollback'] = {
                    key: rollback[key] for key in ('status','owned_files_retained','source_restore_performed','sequences_not_rewound') if key in rollback}
        require(result.get('ok') is True, code if isinstance(code, str) and re.fullmatch('[A-Z0-9_]+', code) else 'PRIVATE_REMOTE_BACKUP_RESTORE_STOP')
        return result['result']

    def close(self):
        if self.process is not None:
            # EOF asks the remote finally block to remove only its own probe DB.
            if self.process.stdin and not self.process.stdin.closed:
                self.process.stdin.close()
            try:
                self.process.wait(timeout=25)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process.stdout.close()


def private_ciphertext_file(path, ciphertext):
    require(ciphertext.startswith(bytes.fromhex('01000000d08c9ddf0115d1118c7a00c04fc297eb')), 'DPAPI_CIPHERTEXT_REQUIRED')
    require(not path.exists(), 'NO_BACKUP_OVERWRITE')
    # Reuse the existing ACL primitive; only this function is invoked, never any
    # key initialization/verification/GPG API from that file. CreateNew sets owner
    # explicitly to the operator even with an elevated Windows token.
    script = """$ErrorActionPreference='Stop'
try {
 . '__ACL__'
 $memory=[IO.MemoryStream]::new()
 $inputStream=[Console]::OpenStandardInput()
 $buffer=[byte[]]::new(65536)
 while (($count=$inputStream.Read($buffer,0,$buffer.Length)) -gt 0) {
   if ($memory.Length+$count -gt 67108864) { exit 2 }
   $memory.Write($buffer,0,$count)
 }
 $stream=New-StagingPrivateFileStream '__PATH__'
 try { $memory.Position=0; $memory.CopyTo($stream); $stream.Flush($true) } finally { $stream.Dispose();$memory.Dispose() }
 Assert-StagingPrivateAcl '__PATH__'
} catch { exit 1 }
""".replace('__ACL__', str(SCRIPTS / 'initialize-staging-operator-config.ps1').replace("'", "''"))
    script = script.replace('__PATH__', str(path).replace("'", "''"))
    checked('pwsh', '-NoProfile', '-NonInteractive', '-EncodedCommand', base64.b64encode(script.encode('utf-16-le')).decode(), data=ciphertext)
    stored = path.read_bytes()
    require(protocol.sha(stored) == protocol.sha(ciphertext), 'CIPHERTEXT_DISK_HASH_MISMATCH')
    return stored


def validate_target(path):
    expected = Path(os.environ['LOCALAPPDATA']) / 'CompetenceHub/pilot-snapshots'
    require(path.drive.casefold() == 'c:', 'QUALIFIED_C_VOLUME_REQUIRED')
    require(path.parent.resolve() == expected.resolve() and re.fullmatch(r'[a-f0-9]{32}', path.name), 'EXACT_APPROVED_DESTINATION_REQUIRED')
    require(path.is_dir() and not any(path.iterdir()), 'OWN_NEW_EMPTY_DIRECTORY_REQUIRED')
    require(not path.is_relative_to(ROOT), 'NO_REPOSITORY_BACKUP')
    # Direct Python invocation cannot bypass the wrapper's current volume gate.
    check = """$ErrorActionPreference='Stop';try {
 $v=Get-BitLockerVolume -MountPoint 'C:'
 if ([string]$v.VolumeStatus -cne 'FullyEncrypted' -or [string]$v.ProtectionStatus -cne 'On' -or
     [string]$v.LockStatus -cne 'Unlocked' -or [IO.DriveInfo]::new('C:\\').AvailableFreeSpace -lt 1GB) {exit 1}
} catch {exit 1}"""
    checked(str(Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'),
            '-NoProfile', '-NonInteractive', '-Command', check)


def main(options):
    require(os.name == 'nt' and options.execute, 'EXPLICIT_WINDOWS_OPERATION_REQUIRED')
    require(re.fullmatch('[a-f0-9]{40}', options.source), 'EXACT_SOURCE_REQUIRED')
    require(checked('git', '-C', str(ROOT), 'rev-parse', 'HEAD').decode().strip() == options.source, 'SOURCE_CHANGED')
    preflight_path = ROOT / 'release-artifacts/protected-staging-preflight/20261109T2013097595103Z.json'
    raw = preflight_path.read_bytes()
    require(protocol.sha(raw) == PREFLIGHT_SHA256, 'APPROVED_PREFLIGHT_CHANGED')
    preflight = json.loads(raw)
    stamp = datetime.fromisoformat(preflight['checked_at_utc'])
    # The hash binds the owner's historical input; fresh root inventory and
    # BitLocker checks below, not this old receipt, authorize current operations.
    require(stamp.tzinfo is not None and datetime.now(timezone.utc) >= stamp, 'PREFLIGHT_CLOCK_REJECTED')
    validate_target(options.directory)
    report = {'scope': 'STAGING_BACKUP_RESTORE_ONLY', 'status': 'STOP', 'phase': 'remote_preflight',
              'run_id': options.directory.name,
              'source_commit': options.source, 'backup': 'NOT_RUN', 'restore': 'NOT_RUN',
              'deployment': 'NOT_RUN', 'migration': 'NOT_RUN', 'accounts': 'NOT_RUN',
              'protection': 'CURRENT_USER_DPAPI_ON_VERIFIED_BITLOCKER',
              'portable_recovery': False, 'temporary_same_user_machine_rollback_only': True,
              'restore_scope': 'ISOLATED_RESTRICTED_DATABASE_SAME_VPS_CLUSTER',
              'global_role_passwords_exported': False, 'application_keyfiles_touched': False}
    session = None
    public = ROOT / 'release-artifacts/protected-staging-backup'
    public.mkdir(exist_ok=True)
    receipt = public / (options.directory.name + '.json')
    require(not receipt.exists(), 'NO_RECEIPT_OVERWRITE')
    try:
        session = RootSession()
        capture = session.request('capture')
        dump = base64.b64decode(capture.pop('dump'), validate=True)
        require(protocol.sha(dump) == capture['dump_sha256'] and len(dump) <= protocol.MAX_BYTES, 'DUMP_TRANSFER_HASH_MISMATCH')
        report['phase'] = 'encrypted_external_copy'
        print('PASS | Current 0006 source captured using one exported PostgreSQL snapshot.', flush=True)
        stored = private_ciphertext_file(options.directory / 'database.dump.dpapi', dpapi.transform(dump))
        baseline_stored = private_ciphertext_file(options.directory / 'baseline.json.dpapi', dpapi.transform(protocol.canonical(capture)))
        report.update(backup='PASS', dump_sha256=protocol.sha(dump), ciphertext_sha256=protocol.sha(stored),
                      baseline_ciphertext_sha256=protocol.sha(baseline_stored),
                      archive_bytes=len(dump), ciphertext_bytes=len(stored), table_count=len(capture['baseline']['tables']))
        recovered = checked(sys.executable, '-I', str(SCRIPTS / 'windows_dpapi.py'), '--decrypt-stdin', data=stored, timeout=30)
        require(protocol.sha(recovered) == capture['dump_sha256'], 'FRESH_PROCESS_RECOVERY_MISMATCH')
        altered = bytearray(stored)
        altered[-1] ^= 1
        rejected = subprocess.run([sys.executable, '-I', str(SCRIPTS / 'windows_dpapi.py'), '--decrypt-stdin'],
                                  input=altered, capture_output=True, timeout=30)
        require(rejected.returncode != 0 and not rejected.stdout, 'CIPHERTEXT_INTEGRITY_REJECTION_FAILED')
        report['ciphertext_tamper_rejected'] = True
        del dump
        print('PASS | Ciphertext-only copy, private ACL, reread SHA-256 and fresh-process recovery.', flush=True)
        report['phase'] = 'isolated_restore'
        result = session.request('restore', dump=base64.b64encode(recovered).decode(),
                                 encrypted_copy_verified=True, ciphertext_sha256=report['ciphertext_sha256'])
        del recovered
        require(result.get('status') == 'PASS' and result.get('probe_removed') is True, 'RESTORE_OR_CLEANUP_UNPROVEN')
        report['restore'] = 'PASS'
        report['restore_proof'] = result
        print('PASS | Exact stored copy restored, data/schema/rights match; private probe removed.', flush=True)
        report['phase'] = 'postflight'
        postflight = session.request('postflight')
        protocol.validate_inventory(postflight)
        require(sorted(postflight['listeners']) == sorted(capture['source_inventory']['listeners']), 'UNEXPECTED_LISTENER_CHANGE')
        require(postflight['database']['roles'] == capture['source_inventory']['database']['roles']
                and postflight['database']['role_memberships'] == capture['source_inventory']['database']['role_memberships'],
                'GLOBAL_ROLE_STATE_CHANGED')
        require(protocol.sha((options.directory / 'database.dump.dpapi').read_bytes()) == report['ciphertext_sha256'],
                'STORED_COPY_CHANGED_DURING_RESTORE')
        report.update(status='PASS', phase='complete', postflight='PASS', source_unchanged=True,
                      migrations=postflight['database']['migrations'], own_probe_removed=True,
                      completed_at_utc=datetime.now(timezone.utc).isoformat())
    except BaseException as error:
        # Fixed type only; no driver/local variables/SSH/password/dump output.
        report['failure_type'] = type(error).__name__
        if isinstance(error, protocol.SnapshotStop) and re.fullmatch('[A-Z0-9_]+', str(error)):
            report['failure_code'] = str(error)
        if session is not None and getattr(session, 'last_failure', None):
            report['remote_cleanup_context'] = session.last_failure
        raise
    finally:
        if session is not None:
            session.close()
        with receipt.open('xb') as stream:
            stream.write(protocol.canonical(report))
            stream.flush()
            os.fsync(stream.fileno())
        print('BACKUP=' + report['backup'] + ' RESTORE=' + report['restore'] + ' STATUS=' + report['status']
              + ' PILOT=NOT_INSTALLED MIGRATIONS=NONE REAL_ACCOUNTS=NONE', flush=True)
        print('REPORT=' + str(receipt), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--source', required=True)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    try:
        main(args)
    except BaseException:
        print('PROTECTED_BACKUP=STOP NO_AUTOMATIC_RETRY NO_SECRET_OUTPUT', flush=True)
        raise SystemExit(1) from None
