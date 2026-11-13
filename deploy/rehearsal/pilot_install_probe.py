"""Owned disposable Ubuntu only: real package/PG/TLS with a process service shim.

The shim substitutes unavailable container systemd; it is never sent to the VPS.
"""
import base64
import importlib.util
import json
import os
from pathlib import Path
import shlex
import socket
import socketserver
import subprocess
import sys
import threading

ROOT=Path('/work')


def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def main():
    if not Path('/.dockerenv').exists() or not (ROOT/'LOCAL_REHEARSAL_ONLY').exists():
        raise SystemExit(2)
    p,s,v=load('staging_readonly_preflight'),load('staging_snapshot_agent'),load('vps_pilot_agent')
    update=(ROOT/'UPDATE_REHEARSAL_ONLY').exists()
    u=load('vps_update_agent') if update else None
    original=s.run
    processes={}
    def run(*args,data=None):
        if args[0]=='journalctl':
            return b'\n'.join((ROOT/(name+'.log')).read_bytes() for name in (v.API,v.PROXY) if (ROOT/(name+'.log')).exists())
        if args[0]!='systemctl':return original(*args,data=data)
        operation=args[1]
        if operation=='show':
            if 'DropInPaths' in args:
                return (' '.join(str(path) for path in sorted(u.DROP.glob('*.conf')))+'\n').encode()
            name=next((value for value in args if value.endswith('.service') or value.endswith('.timer')),None)
            process=processes.get(name)
            state=b'active' if process is not None and process.poll() is None else b'inactive'
            if '--value' in args:return state
            return b'LoadState=loaded\nActiveState='+state+b'\nSubState=running\n'
        for name in args[2:]:
            if name not in (v.API,v.PROXY):raise RuntimeError('Only own service shim')
            if operation in ('stop','restart') and name in processes:
                processes[name].terminate();processes[name].wait(timeout=15);del processes[name]
            if operation in ('start','restart'):
                if name==v.API:
                    env=dict(os.environ)
                    for line in (v.CONFIG/'runtime.env').read_text().splitlines():
                        key,value=line.split('=',1);env[key]=shlex.split(value)[0]
                    runtime=v.ROOT/'venv/bin/uvicorn'
                    if update:
                        # Match systemd's ordered overrides, including the retained
                        # V1 runtime when the V1.1 drop-in is compensated.
                        for drop in sorted(u.DROP.glob('*-runtime.conf')):
                            lines=drop.read_text().splitlines()
                            command_line=next(line for line in lines if line.startswith('ExecStart=') and line!='ExecStart=')
                            runtime=Path(shlex.split(command_line.split('=',1)[1])[0])
                            if runtime not in (v.ROOT/'venv/bin/uvicorn',v.ROOT/'releases/bc53775b08dc/venv/bin/uvicorn',v.ROOT/'releases/38153c12159e/venv/bin/uvicorn'):
                                raise RuntimeError('Unknown rehearsal runtime')
                    if update and u.CAPTURE_ENV.exists():env['COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED']='true'
                    command=[str(runtime),'competence_hub_api.runtime:create_runtime_app_from_environment',
                             '--factory','--host','127.0.0.1','--port','8001','--proxy-headers','--forwarded-allow-ips=127.0.0.1','--no-access-log']
                else:
                    credentials=Path('/run/credentials')/v.PROXY
                    credentials.mkdir(parents=True,exist_ok=True)
                    (credentials/'tls.key').write_bytes((v.CONFIG/'tls.key').read_bytes())
                    command=['nginx','-c',str(v.ROOT/'nginx.conf'),'-g','daemon off;'];env=dict(os.environ)
                log=open(ROOT/(name+'.log'),'ab')
                processes[name]=subprocess.Popen(command,env=env,stdout=log,stderr=log);log.close()
            if operation=='is-active' and (name not in processes or processes[name].poll() is not None):
                raise RuntimeError('Own local process not healthy')
        return b'active\n'
    s.run=run
    original_command=p.command
    def metadata_command(*args,**kwargs):
        if args[0]=='systemctl':return run(*args).decode()
        return original_command(*args,**kwargs)
    if update:p.command=metadata_command
    def collect():
        listeners=['127.0.0.1:5432']
        for name,port in ((v.API,8001),(v.PROXY,8443)):
            if name in processes and processes[name].poll() is None:listeners.append('127.0.0.1:'+str(port))
        return {'status':'PASS','scope':'READ_ONLY','database':p.database_metadata(),'listeners':listeners,
                'services':{**{name:{'ActiveState':'active'} for name in p.SERVICES[:4]},
                            'competence-hub-api.service':{'LoadState':'not-found'}},
                'paths':{'/etc/competence-hub/webapp.env':{'exists':False},'/opt/competence-hub':{'exists':False}}}
    p.collect=collect
    os.umask(0o077)  # Production must not depend on sudo's inherited umask.
    class Forward(socketserver.BaseRequestHandler):
        def handle(self):
            import select
            with socket.create_connection(('127.0.0.1',8443),timeout=10) as destination:
                peers=[self.request,destination]
                while True:
                    ready,_,_=select.select(peers,[],[],30)
                    if not ready:return
                    for source in ready:
                        block=source.recv(65536)
                        if not block:return
                        (destination if source is self.request else self.request).sendall(block)
    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address=True
        daemon_threads=True
    server=Server(('0.0.0.0',18443),Forward)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    sys.stdout.buffer.write(b'LOCAL_PROBE_READY\n');sys.stdout.buffer.flush()
    try:
        v.serve(p,s)
        if update:
            u.LEAF_SHA=s.sha((v.ROOT/'pilot.crt').read_bytes())
            u.serve(p,s,v)
            if (ROOT/'UPDATE_RESUME_REHEARSAL').exists():u.serve(p,s,v)
            if (ROOT/'UPDATE_V11_REHEARSAL').exists():
                u.configure_v11()
                u.LEAF_SHA=s.sha((v.ROOT/'pilot.crt').read_bytes())
                u.serve(p,s,v)
            # Real systemd services outlive the operator channel. Keep this local
            # process shim alive until the client finishes its final HTTPS probe.
            sys.stdin.buffer.read(1)
    finally:
        for process in processes.values():
            process.terminate();process.wait(timeout=15)
        server.shutdown();server.server_close()


if __name__=='__main__':main()
