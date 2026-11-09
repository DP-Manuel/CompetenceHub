"""Synthetic, container-loopback OpenSSH + verified TLS; never a VPS installer."""
import json
from pathlib import Path
import socket
import ssl
import subprocess
import time

import linux_proxy_smoke as proxy

ROOT=Path('/work')


def main():
    if not Path('/.dockerenv').exists() or not (ROOT/'LOCAL_REHEARSAL_ONLY').is_file():
        raise RuntimeError('Owned local container required')
    report={'scope':'LOCAL_SYNTHETIC_ONLY','status':'RUNNING','checks':[]}
    def check(label,ok):
        if not ok: raise AssertionError(label)
        report['checks'].append(label)
    proxy.command('mkdir','-p','/run/sshd')
    proxy.command('useradd','-m','-s','/bin/false','pilotprobe')
    proxy.command('passwd','-d','pilotprobe')
    for name in ('host','client'):
        proxy.command('ssh-keygen','-q','-t','ed25519','-N','','-f',str(ROOT/name))
        (ROOT/name).chmod(0o600)
    public=(ROOT/'client.pub').read_text().strip()
    (ROOT/'authorized').write_text('restrict,port-forwarding,permitopen="127.0.0.1:8443" '+public+'\n')
    (ROOT/'authorized').chmod(0o644)
    host_public=(ROOT/'host.pub').read_text().strip()
    (ROOT/'known_hosts').write_text('[127.0.0.1]:2222 '+host_public+'\n')
    (ROOT/'wrong_hosts').write_text('[127.0.0.1]:2222 '+public+'\n')
    (ROOT/'sshd.conf').write_text('''Port 2222
ListenAddress 127.0.0.1
HostKey /work/host
PidFile /work/sshd.pid
AuthorizedKeysFile /work/authorized
PasswordAuthentication no
KbdInteractiveAuthentication no
AuthenticationMethods publickey
UsePAM no
AllowUsers pilotprobe
AllowTcpForwarding local
PermitOpen 127.0.0.1:8443
GatewayPorts no
PermitTTY no
X11Forwarding no
AllowAgentForwarding no
ForceCommand /bin/false
LogLevel ERROR
''')
    sshd=subprocess.Popen(['/usr/sbin/sshd','-D','-e','-f',str(ROOT/'sshd.conf')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    tunnel=None
    args=['ssh','-F','/dev/null','-p','2222','-i',str(ROOT/'client'),'-o','BatchMode=yes',
          '-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','GlobalKnownHostsFile=/dev/null',
          '-o','ExitOnForwardFailure=yes','-o','ConnectTimeout=3']
    try:
        for _ in range(60):
            try:
                with socket.create_connection(('127.0.0.1',2222),timeout=.2): break
            except OSError: time.sleep(.1)
        bad=subprocess.run([*args,'-o','UserKnownHostsFile=/work/wrong_hosts','-N',
                            '-L','127.0.0.1:8447:127.0.0.1:8443','pilotprobe@127.0.0.1'],capture_output=True,timeout=10)
        check('OpenSSH rejects wrong pinned host key without password fallback',bad.returncode==255)
        tunnel=subprocess.Popen([*args,'-o','UserKnownHostsFile=/work/known_hosts','-N',
            '-L','127.0.0.1:8447:127.0.0.1:8443','pilotprobe@127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(60):
            if tunnel.poll() is not None: raise RuntimeError('Synthetic SSH tunnel failed')
            if ':8447 ' in proxy.command('ss','-ltnH'): break
            time.sleep(.1)
        check('SSH listener is loopback-only with authenticated pinned host',
              '127.0.0.1:8447 ' in proxy.command('ss','-ltnH') and tunnel.poll() is None)
        proxy.ORIGIN='https://localhost:8447'
        native={'environment':'local-container-over-SSH','status':'RUNNING','checks':[],'vps_changed':False}
        def verified():
            # Unknown certificate and wrong hostname must fail, not silently
            # fall back to unverified TLS. Positive native MFA already passed.
            for context,name in ((ssl.create_default_context(),'localhost'),
                    (ssl.create_default_context(cafile=str(ROOT/'localhost.crt')),'not-localhost.invalid')):
                try:
                    with socket.create_connection(('127.0.0.1',8447),timeout=5) as sock:
                        with context.wrap_socket(sock,server_hostname=name): pass
                except ssl.SSLCertVerificationError: pass
                else: raise AssertionError('TLS verification unexpectedly bypassed')
            check('Unknown certificate and wrong hostname both rejected through SSH',True)
            check('MFA/cookie/CSRF/session tests use trusted TLS across actual OpenSSH',len(native['checks'])==36)
            (ROOT/'PRIVATE_READY').write_text('SYNTHETIC_ONLY')
            deadline=time.monotonic()+180
            while not (ROOT/'CONTINUE').exists():
                if time.monotonic()>deadline: raise TimeoutError('Local snapshot probe timed out')
                time.sleep(.2)
        proxy.main(native,on_verified=verified)
        check('Native Linux exact cleanup still passes after snapshot/restore probe',native['status']=='PASS')
        report.update(status='PASS',native_checks=native['checks'])
    finally:
        for process in (tunnel,sshd):
            if process is not None:
                process.terminate()
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.kill();process.wait()
        (ROOT/'private-tunnel-result.json').write_text(json.dumps(report,indent=2))


if __name__=='__main__':
    try: main()
    except BaseException as error:
        # No key/passphrase/credential or raw OpenSSH exception output.
        (ROOT/'PRIVATE_FAILED').write_text(type(error).__name__)
        raise SystemExit(1) from None
