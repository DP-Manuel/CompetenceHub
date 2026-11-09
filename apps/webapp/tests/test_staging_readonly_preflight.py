import importlib.util
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / 'deploy/scripts/staging_readonly_preflight.py'
ENTRY = ROOT / 'deploy/scripts/run-protected-staging-preflight.ps1'
spec = importlib.util.spec_from_file_location('readonly_preflight', HELPER)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def baseline():
    return {
        'database': {
            'database': preflight.DATABASE, 'migrations': [f'{i:04}' for i in range(1, 7)],
            'listen_addresses': 'localhost', 'port': '5432',
            'table_owners': [{'tablename': 'calendar_offers', 'tableowner': 'competence_hub_owner'}],
            'roles': [dict(rolname='competence_hub_' + name, rolsuper=False, rolcreaterole=False,
                           rolcreatedb=False, rolbypassrls=False, rolcanlogin=name != 'owner')
                      for name in ('owner', 'app', 'migrator')],
            'privileges': dict(app_schema_create=False, app_migrations_select=False,
                               app_offers_select=True, app_offers_insert=True,
                               app_offers_delete=False, app_decisions_update=False,
                               app_owner_member=False, app_migrator_member=False),
        },
        'listeners': ['127.0.0.1:5432', '0.0.0.0:443'],
        'services': {name: {'ActiveState': 'active'} for name in preflight.SERVICES[:4]},
    }


def test_sql_is_server_enforced_readonly_and_returns_no_subprocess_diagnostics(monkeypatch):
    calls = []
    monkeypatch.setattr(preflight, 'command', lambda *args, **kw: calls.append((args, kw)) or '42\n')
    assert preflight.sql('SELECT count(*) FROM competence_hub.portal_users') == '42'
    arguments, options = calls[0]
    assert arguments[-1] == 'competence_hub_staging'
    statement = options['data'].decode()
    assert statement.startswith('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;')
    assert "lock_timeout='2s'" in statement and statement.endswith('; COMMIT;')


def test_failed_command_never_reflects_raw_secret_diagnostics(monkeypatch):
    monkeypatch.setattr(preflight.subprocess, 'run', lambda *a, **kw: SimpleNamespace(
        returncode=1, stdout=b'synthetic-sensitive', stderr=b'synthetic-sensitive'))
    with pytest.raises(preflight.PreflightStop, match='^READONLY_COMMAND_UNAVAILABLE$'):
        preflight.command('psql')


def test_private_path_inventory_uses_only_lstat_not_file_content(tmp_path, monkeypatch):
    path = tmp_path / 'webapp.env'
    path.write_bytes(b'SYNTHETIC_NO_REAL_KEY')
    def forbidden(*a, **kw):
        raise AssertionError('content must not be opened')
    monkeypatch.setattr(Path, 'read_bytes', forbidden)
    monkeypatch.setattr(Path, 'read_text', forbidden)
    meta = preflight.path_metadata(path)
    assert meta['exists'] and meta['bytes'] == 21 and not meta['is_link']
    assert preflight.path_metadata(tmp_path / 'missing') == {'exists': False}


@pytest.mark.parametrize('count', [6, 7, 8, 9])
def test_supported_schema_history_does_not_authorize_writes(count):
    report = baseline()
    report['database']['migrations'] = [f'{i:04}' for i in range(1, count + 1)]
    assert all(preflight.assess(report).values())
    assert 'backup' not in preflight.assess(report)


@pytest.mark.parametrize('change,gate', [
    ('database', 'database_identity'), ('versions', 'supported_migrations'),
    ('listener', 'postgres_loopback_setting'), ('owner', 'owners'),
    ('superuser', 'bounded_roles'), ('ddl', 'app_rights'),
    ('delete', 'app_rights'), ('member', 'app_rights'), ('chatbot', 'foreign_services_active'),
    ('external_socket', 'postgres_loopback_sockets'),
])
def test_failed_identity_privilege_or_health_is_not_a_pass(change, gate):
    report = baseline()
    if change == 'database': report['database']['database'] = 'production'
    if change == 'versions': report['database']['migrations'] = ['0001', '0006']
    if change == 'listener': report['database']['listen_addresses'] = '*'
    if change == 'owner': report['database']['table_owners'][0]['tableowner'] = 'postgres'
    if change == 'superuser': report['database']['roles'][1]['rolsuper'] = True
    if change == 'ddl': report['database']['privileges']['app_schema_create'] = True
    if change == 'delete': report['database']['privileges']['app_offers_delete'] = True
    if change == 'member': report['database']['privileges']['app_owner_member'] = True
    if change == 'chatbot': report['services']['dp-chatbot.service']['ActiveState'] = 'failed'
    if change == 'external_socket': report['listeners'] = ['0.0.0.0:5432']
    assert preflight.assess(report)[gate] is False


@pytest.mark.parametrize('setting', ['localhost', '127.0.0.1', '127.0.0.1,::1'])
def test_equivalent_loopback_settings_are_accepted_but_need_actual_socket_proof(setting):
    report = baseline()
    report['database']['listen_addresses'] = setting
    assert all(preflight.assess(report).values())
    report['listeners'] = []
    assert not preflight.assess(report)['postgres_loopback_sockets']


def test_unsafe_catalog_identifier_rejected_before_dynamic_count_query(monkeypatch):
    calls = []
    monkeypatch.setattr(preflight, 'sql', lambda value: calls.append(value) or '["x; unsafe"]')
    with pytest.raises(preflight.PreflightStop, match='SCHEMA_TABLE_METADATA_REJECTED'):
        preflight.database_metadata()
    assert len(calls) == 1


@pytest.mark.skipif(os.name != 'nt', reason='PowerShell on operator workstation')
@pytest.mark.parametrize('volume,valid', [
    ({'volume': 'FullyEncrypted', 'protection': 'On', 'lock': 'Unlocked', 'free_bytes': 2**31}, True),
    ({'volume': 'FullyEncrypted', 'protection': 'Off', 'lock': 'Unlocked', 'free_bytes': 2**31}, False),
    ({'volume': 'FullyDecrypted', 'protection': 'On', 'lock': 'Unlocked', 'free_bytes': 2**31}, False),
    ({'volume': 'FullyEncrypted', 'protection': 'On', 'lock': 'Locked', 'free_bytes': 2**31}, False),
    ({'volume': 'FullyEncrypted', 'protection': 'On', 'lock': 'Unlocked', 'free_bytes': 10}, False),
])
def test_actual_powershell_volume_gate_does_not_unlock_or_mutate(volume, valid):
    script = f". '{ENTRY}'; $v=ConvertFrom-Json -AsHashtable '{json.dumps(volume)}'; try {{ Assert-PreflightVolume $v; exit 0 }} catch {{ exit 1 }}"
    result = subprocess.run(['pwsh', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True)
    assert (result.returncode == 0) == valid


@pytest.mark.skipif(os.name != 'nt', reason='PowerShell on operator workstation')
def test_preflight_requires_commit_before_any_privilege_or_password_prompt():
    result = subprocess.run(['pwsh', '-NoProfile', '-NonInteractive', '-File', str(ENTRY)], capture_output=True)
    assert result.returncode == 1
    assert b'EXACT_REVIEWED_COMMIT_REQUIRED' in result.stdout
    assert b'password' not in result.stderr


def test_windows_profile_path_resolves_to_user_not_parent():
    # Four parents: Website -> Firmendingsbums -> IT -> Documents -> user.
    assert ROOT.parents[3].name == 'RödelManuel'
    source = ENTRY.read_text(encoding='utf8')
    assert "Join-Path $root '../../../..'" in source
    assert 'LOCAL_TARGET_REPARSE_POINT_REJECTED' in source
    assert 'Get-BitLockerVolume' in source
    assert 'Read-Host' in source and '-AsSecureString' in source
    assert 'StrictHostKeyChecking=yes' in source and 'ForwardAgent=no' in source
    assert 'SERVER_MUTATIONS=NONE' in source
