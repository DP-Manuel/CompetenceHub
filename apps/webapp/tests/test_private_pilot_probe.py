import importlib.util
import os
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('probe_dpapi',ROOT/'deploy/rehearsal/synthetic_dpapi.py')
dpapi=importlib.util.module_from_spec(spec);spec.loader.exec_module(dpapi)
runner_spec=importlib.util.spec_from_file_location('private_local_probe',ROOT/'apps/webapp/scripts/run-private-pilot-local-proof.py')
runner=importlib.util.module_from_spec(runner_spec);runner_spec.loader.exec_module(runner)


@pytest.mark.parametrize('sid',['S-1-5-21-100-200-300-1001','S-1-12-1-100-200-300-400'])
def test_acl_accepts_actual_local_domain_and_entra_identity_families(sid):
    assert runner.validate_sid(' '+sid+'\n')==sid


@pytest.mark.parametrize('sid',['Everyone','S-1-5;unsafe','S-1-5 F',''])
def test_acl_rejects_non_sid_or_injected_identity_text(sid):
    with pytest.raises(ValueError):runner.validate_sid(sid)


def test_catalog_comparison_is_order_independent_without_dropping_trigger_state():
    rows=[{'relation':'a','name':'freeze','enabled':'O','definition':'definition a'},
          {'relation':'b','name':'freeze','enabled':'O','definition':'definition b'}]
    original={'triggers':rows,'empty':None}
    assert runner.canonical_catalog(original)==runner.canonical_catalog({'triggers':list(reversed(rows)),'empty':None})
    for field,value in [('enabled','D'),('definition','different'),('relation','other')]:
        changed=[{**rows[0],field:value},rows[1]]
        assert runner.canonical_catalog(original)!=runner.canonical_catalog({'triggers':changed,'empty':None})
    assert original['triggers']==rows


@pytest.mark.skipif(os.name!='nt',reason='Windows CurrentUser DPAPI only')
def test_native_synthetic_dpapi_roundtrip_and_tampering():
    payload=b'SYNTHETIC_NO_EXISTING_KEYS\x00'+bytes(range(256))
    encrypted=dpapi.transform(payload)
    assert encrypted!=payload
    assert dpapi.transform(encrypted,decrypt=True)==payload
    modified=bytearray(encrypted);modified[-1]^=1
    with pytest.raises(dpapi.ProtectionError):dpapi.transform(bytes(modified),decrypt=True)


def test_dpapi_refuses_empty_or_oversized_payload_before_os_work():
    for payload in (b'',b'x'*(64*1024*1024+1)):
        with pytest.raises(dpapi.ProtectionError):dpapi.transform(payload)


def test_private_ssh_probe_is_loopback_pinned_and_never_disables_tls_verification():
    source=(ROOT/'deploy/rehearsal/private_tunnel_smoke.py').read_text(encoding='utf8')
    proxy=(ROOT/'deploy/rehearsal/linux_proxy_smoke.py').read_text(encoding='utf8')
    assert 'StrictHostKeyChecking=yes' in source
    assert 'ExitOnForwardFailure=yes' in source
    assert '127.0.0.1:8447:127.0.0.1:8443' in source
    assert 'GatewayPorts no' in source
    assert 'PermitOpen 127.0.0.1:8443' in source
    assert 'ssl.create_default_context(cafile=' in proxy
    assert '_create_unverified_context' not in proxy
    assert 'ignore_https_errors' not in source


def test_restore_probe_uses_exclusive_local_engine_and_no_existing_keys():
    source=(ROOT/'apps/webapp/scripts/run-private-pilot-local-proof.py').read_text(encoding='utf8')
    assert 'npipe:////./pipe/dockerDesktopLinuxEngine' in source
    assert '217.160.255.86' not in source
    assert "'--exit-on-error','--single-transaction'" in source
    assert "'xb'" in source
    assert 'GNUPGHOME' not in source
    assert 'AppData' not in source
