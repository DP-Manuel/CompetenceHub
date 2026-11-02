"""Offline PS contract/fake-process checks, never the actual operator window.

Subprocesses inherit only platform paths plus synthetic temporary APPDATA roots.
No private login, real corpus, GPG home, keys, Docker, SSH or database is opened.
"""

import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "apps/webapp/scripts/run-staging-admin-window.ps1"


def test_window_has_fixed_scope_secret_and_source_contracts():
    source = SCRIPT.read_text(encoding="ascii")
    for required in (
        "#requires -Version 7.2",
        "manuel@217.160.255.86",
        "StrictHostKeyChecking=yes",
        "BatchMode=yes",
        "ForwardAgent=no",
        "PasswordAuthentication=no",
        "'NUL'",
        "127.0.0.1:55432:127.0.0.1:5432",
        "PORT55432_ALREADY_IN_USE_NEVER_REUSE_OR_KILL",
        "OwningProcess -eq $tunnel.Id",
        "$tunnel.Kill($true)",
        "CreateNoWindow = $true",
        "https://github.com/DP-Manuel/CompetenceHub.git",
        "ls-remote",
        "--untracked-files=all",
        ".tmp/backend-sprint-20261030/operator-login.json",
        "bootstrap-attempt.json",
        "LOCALAPPDATA",
        "New-StagingPrivateDirectory",
        "Assert-StagingPrivateAcl",
        "Initialize-StagingOperatorConfig",
        "Use-StagingOperatorEnvironment",
        "Assert-WindowNoPriorAttempt",
        "PRIOR_ACCOUNT_ATTEMPT_REQUIRES_MANUAL_RECONCILIATION_NO_RETRY",
        "https://127.0.0.1:443",
        "backup-gnupg",
        "FixedTimeEquals",
        "80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da",
        "2E44306121629A100F76A8B08CCA3D9186A28D4C",
        "image', 'inspect'",
        "LOCAL_DOCKER_ENGINE_REQUIRED",
        "CACHED_PINNED_RESTORE_IMAGE_REQUIRED_NO_PULL",
        "restore-competence-hub-snapshot.ps1",
        "RESTORE_API_NOT_INTEGRATED",
        "runuser -u postgres",
        "--confirm-staging-snapshot",
        "REMOTE_REVIEWED_SCRIPT_HASH_MISMATCH",
        "EXACT_FIVE_FILE_SET_REQUIRED",
        "EXACT_ENCRYPTED_COPY_HASH_MISMATCH",
        "--login-file",
        "--restore-proof",
        "--backup-set",
        "--binding-output",
        "ZeroFreeBSTR",
        "[NullString]::Value",
        "SANITIZED_COMMAND_FAILURE",
        "READINESS_ONLY REAL_COACH_APPLY=DISABLED",
        "[IO.FileMode]::CreateNew",
        "$stream.Flush($true)",
        "service-before-admin.json",
        "service-final.json",
    ):
        assert required in source
    assert source.count(" -AsSecureString") == 3
    assert "$process.StandardInput.WriteLine($plain)" in source
    assert "ArgumentList.Add($plain)" not in source
    for forbidden in (
        "run-native-cal1-staging-batch",
        "coach3b_real_apply.py",
        "Start-Transcript",
        "StrictHostKeyChecking=no",
        "ssh-add",
        "ssh-keygen",
        "Get-Clipboard",
        "rm -rf",
        "Remove-Item -Recurse",
        "--passphrase",
        "--pinentry-mode loopback",
        "systemctl restart",
        "systemctl stop",
        "SkipBackup",
        "BypassBackup",
        "ALTER ROLE",
        "CREATE USER",
        "--pull always",
    ):
        assert forbidden not in source
    body = source[source.index("function Invoke-StagingAdminWindow") :]
    ordered = [
        "Assert-WindowSource $Commit",
        "Initialize-StagingOperatorConfig",
        "LOCAL_GPG_ROUNDTRIP_REQUIRED",
        "Get-WindowHealth $ssh",
        "encrypted_prechange_snapshot",
        "Get-WindowSnapshotPlan $snapshot",
        "EXACT_FIVE_FILE_SET_REQUIRED",
        "isolated_restore",
        "ACTUAL_RESTORE_PROOF_REQUIRED",
        "Read-Host 'Password for competence_hub_app",
        "Write-WindowRecord $attempt",
        "Invoke-WindowConsoleOperator $python",
        "$account.status",
    ]
    positions = [body.index(item) for item in ordered]
    assert positions == sorted(positions)
    assert re.search(r"postgres@sha256:[a-f0-9]{64}", source)


@pytest.fixture
def powershell():
    executable = shutil.which("pwsh")
    if os.name != "nt" or not executable:
        pytest.skip("requires native Windows PowerShell 7")
    return executable


def run_private(powershell, tmp_path, body):
    allowed = (
        "SystemRoot",
        "SystemDrive",
        "WINDIR",
        "PATH",
        "TEMP",
        "TMP",
        "USERPROFILE",
        "COMSPEC",
        "ProgramFiles",
        "PSModulePath",
        "ProgramData",
    )
    environment = {name: os.environ[name] for name in allowed if name in os.environ}
    environment.update(
        {
            "LOCALAPPDATA": str(tmp_path),
            "APPDATA": str(tmp_path),
            "WINDOW_TEST_ROOT": str(tmp_path),
            "WINDOW_TEST_SCRIPT": str(SCRIPT),
            "WINDOW_TEST_PWSH": powershell,
        }
    )
    command = (
        r"""
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$errors = $null; $tokens = $null
$null = [Management.Automation.Language.Parser]::ParseFile($env:WINDOW_TEST_SCRIPT, [ref]$tokens, [ref]$errors)
if ($errors.Count) { exit 2 }
. $env:WINDOW_TEST_SCRIPT
try {
"""
        + body
        + r"""
} catch { Write-Output ('FAILED_LINE=' + $_.InvocationInfo.ScriptLineNumber); exit 1 }
Write-Output 'OFFLINE_WINDOW_CONTRACT=PASS'
"""
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        env=environment,
        capture_output=True,
        text=True,
        timeout=40,
    )
    if (
        result.returncode != 0
        or result.stdout.strip() != "OFFLINE_WINDOW_CONTRACT=PASS"
    ):
        location = re.search(r"FAILED_LINE=\d+", result.stdout)
        pytest.fail(
            "Offline window check failed; subprocess output suppressed. "
            + (location[0] if location else ""),
            pytrace=False,
        )


def test_parser_dot_source_and_default_are_definition_only(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
function Get-NetTCPConnection { throw 'Must not probe the actual host' }
function Read-Host { throw 'Must not ask for any credential' }
function Invoke-WindowCommand { throw 'Must not launch a command' }
$readiness = & $env:WINDOW_TEST_SCRIPT
if ($readiness -cne 'STAGING_ADMIN_WINDOW=NOT_EXECUTED READINESS_ONLY REAL_COACH_APPLY=DISABLED') { throw 'Wrong default' }
if (@(Get-ChildItem -LiteralPath $env:WINDOW_TEST_ROOT -Force).Count) { throw 'Default created files' }
foreach ($name in @('Invoke-StagingAdminWindow','Get-WindowSnapshotPlan','Use-WindowDatabaseEnvironment')) {
    if (-not (Get-Command $name -CommandType Function)) { throw 'Missing API' }
}
""",
    )


def test_existing_listener_and_prior_attempt_fail_closed_without_modification(
    powershell, tmp_path
):
    run_private(
        powershell,
        tmp_path,
        r"""
function Get-NetTCPConnection { return [pscustomobject]@{ OwningProcess = 123; LocalAddress = '127.0.0.1' } }
$rejected = $false
try { Assert-WindowPortFree } catch { $rejected = $_.Exception.Message -ceq 'PORT55432_ALREADY_IN_USE_NEVER_REUSE_OR_KILL' }
if (-not $rejected) { throw 'Existing listener accepted' }
$marker = Join-Path $env:WINDOW_TEST_ROOT 'attempt.json'
Write-WindowRecord $marker @{ status = 'SYNTHETIC_ATTEMPT_CHECK_REQUIRED' }
$before = [IO.File]::ReadAllBytes($marker)
$rejected = $false
try { Assert-WindowNoPriorAttempt $marker } catch { $rejected = $true }
if (-not $rejected -or [Convert]::ToBase64String([IO.File]::ReadAllBytes($marker)) -cne [Convert]::ToBase64String($before)) { throw 'Prior attempt changed' }
$rejected = $false
try { Write-WindowRecord $marker @{ status = 'overwrite' } } catch { $rejected = $true }
if (-not $rejected) { throw 'Record overwrite accepted' }
""",
    )


def test_exact_five_snapshot_paths_and_hashes_not_arbitrary_exports(
    powershell, tmp_path
):
    run_private(
        powershell,
        tmp_path,
        r"""
$run = 'admin-' + ('a' * 32)
$root = '/var/backups/competence-hub/prechange-' + $run
$record = @{ snapshot_path = $root }
foreach ($name in $script:WindowFiles.Keys) {
    $stem = $script:WindowFiles[$name]
    $record[$stem + '_path'] = $root + '/' + $name
    $record[$stem + '_sha256'] = 'b' * 64
}
$plan = @(Get-WindowSnapshotPlan $record $run)
if ($plan.Count -ne 5 -or @($plan | Where-Object { $_.name -match '[/\\*]' }).Count) { throw 'Wrong set' }
foreach ($mutation in @('path','hash','extra','missing')) {
    $changed = $record.Clone()
    switch ($mutation) {
        path { $changed.dump_path = '/arbitrary/database.dump.gpg' }
        hash { $changed.dump_sha256 = 'not-a-sha' }
        extra { $changed.extra_path = '/arbitrary/private' }
        missing { $changed.Remove('complete_path') }
    }
    $rejected = $false
    try { $null = Get-WindowSnapshotPlan $changed $run } catch { $rejected = $true }
    if (-not $rejected) { throw 'Arbitrary export accepted' }
}
""",
    )


def test_pushed_source_gate_uses_exact_origin_clean_source_and_remote_commit(
    powershell, tmp_path
):
    run_private(
        powershell,
        tmp_path,
        r"""
$script:mode = 'good'; $script:calls = 0
function Invoke-WindowCommand {
    param($Executable, [string[]]$Arguments)
    $script:calls++
    if ($Arguments -contains 'rev-parse') { return 'a' * 40 }
    if ($Arguments -contains 'get-url') { if ($script:mode -ceq 'origin') { return 'https://other.invalid/repo' }; return 'https://github.com/DP-Manuel/CompetenceHub.git' }
    if ($Arguments -contains 'status') { if ($script:mode -ceq 'dirty') { return ' M synthetic.py' }; return '' }
    if ($Arguments -contains 'symbolic-ref') { return 'main' }
    if ($Arguments -contains 'ls-remote') { if ($script:mode -ceq 'unpushed') { return ('b' * 40) + "`trefs/heads/main" }; return ('a' * 40) + "`trefs/heads/main" }
    throw 'Unexpected command'
}
Assert-WindowSource ('a' * 40) 'FAKE_GIT'
if ($script:calls -ne 5) { throw 'Wrong source gates' }
foreach ($mode in @('origin','dirty','unpushed')) {
    $script:mode = $mode; $rejected = $false
    try { Assert-WindowSource ('a' * 40) 'FAKE_GIT' } catch { $rejected = $true }
    if (-not $rejected) { throw 'Unreviewed source accepted' }
}
""",
    )


def test_health_checks_do_not_accept_public_pg_or_failed_cohost(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
$script:mode = 'good'
function Invoke-WindowCommand {
    param($Executable, [string[]]$Arguments)
    if ($Arguments -notcontains 'manuel@217.160.255.86' -or $Arguments -notcontains 'StrictHostKeyChecking=yes') { throw 'Unbounded SSH' }
    if ($Arguments[-1].StartsWith('systemctl')) {
        if ($script:mode -ceq 'service') { return "active`nfailed`nactive`nactive" }
        return "active`nactive`nactive`nactive"
    }
    if ($script:mode -ceq 'public') { return 'LISTEN 0 128 0.0.0.0:5432 0.0.0.0:*' }
    return 'LISTEN 0 128 127.0.0.1:5432 0.0.0.0:*'
}
$health = Get-WindowHealth 'FAKE_SSH'
if (-not $health.postgres_loopback) { throw 'Healthy case failed' }
foreach ($mode in @('service','public')) {
    $script:mode = $mode; $rejected = $false
    try { $null = Get-WindowHealth 'FAKE_SSH' } catch { $rejected = $true }
    if (-not $rejected) { throw 'Bad service/listener accepted' }
}
""",
    )


def test_fake_child_process_stdin_and_failure_diagnostics_are_private(
    powershell, tmp_path
):
    run_private(
        powershell,
        tmp_path,
        r"""
$secret = ConvertTo-SecureString 'SYNTHETIC_TEST_INPUT' -AsPlainText -Force
try {
    $body = 'if ([Console]::ReadLine() -cne ''SYNTHETIC_TEST_INPUT'') { exit 4 }; [Console]::Write(''CHILD_OK'')'
    $result = Invoke-WindowCommand -Executable $env:WINDOW_TEST_PWSH -Arguments @('-NoProfile','-NonInteractive','-Command',$body) -SecureInput $secret
    if ($result -cne 'CHILD_OK') { throw 'Input pipe failed' }
    $body = '[Console]::Error.Write(''SYNTHETIC_DIAGNOSTIC_MUST_NOT_LEAK''); exit 7'
    $rejected = $false
    try { $null = Invoke-WindowCommand -Executable $env:WINDOW_TEST_PWSH -Arguments @('-NoProfile','-NonInteractive','-Command',$body) }
    catch { $rejected = $_.Exception.Message -ceq 'SANITIZED_COMMAND_FAILURE' }
    if (-not $rejected) { throw 'Unredacted process failure' }
} finally { $secret.Dispose() }
""",
    )


def test_database_environment_is_process_only_and_restored_on_exception(
    powershell, tmp_path
):
    run_private(
        powershell,
        tmp_path,
        r"""
$env:PYTHONPATH = 'SYNTHETIC_PREVIOUS_PATH'
$env:COMPETENCE_HUB_OPERATOR_APP_URL = 'SYNTHETIC_PREVIOUS_URL'
$app = ConvertTo-SecureString 'synthetic:/@' -AsPlainText -Force
$owner = ConvertTo-SecureString 'synthetic?#' -AsPlainText -Force
$rejected = $false
try {
    try {
        Use-WindowDatabaseEnvironment $app $owner -Action {
            if ($env:COMPETENCE_HUB_OPERATOR_APP_URL -cne 'postgresql+asyncpg://competence_hub_app:synthetic%3A%2F%40@127.0.0.1:55432/competence_hub_staging') { throw 'Encoding failed' }
            if ($env:COMPETENCE_HUB_OPERATOR_OWNER_URL -cne 'postgresql+asyncpg://competence_hub_migrator:synthetic%3F%23@127.0.0.1:55432/competence_hub_staging') { throw 'Owner scope failed' }
            throw 'SYNTHETIC_ACTION_INTERRUPTED'
        }
    } catch { $rejected = $_.Exception.Message -ceq 'SYNTHETIC_ACTION_INTERRUPTED' }
    if (-not $rejected -or $env:PYTHONPATH -cne 'SYNTHETIC_PREVIOUS_PATH' -or $env:COMPETENCE_HUB_OPERATOR_APP_URL -cne 'SYNTHETIC_PREVIOUS_URL' -or
        $null -ne [Environment]::GetEnvironmentVariable('COMPETENCE_HUB_OPERATOR_OWNER_URL','Process')) { throw 'Environment cleanup failed' }
} finally { $app.Dispose(); $owner.Dispose() }
""",
    )


def test_timeout_terminates_only_the_owned_fake_process(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
$marker = Join-Path $env:WINDOW_TEST_ROOT 'fake-child.pid'
$body = '[IO.File]::WriteAllText(''' + $marker.Replace("'", "''") + ''', [string]$PID); Start-Sleep -Seconds 30'
$rejected = $false
try { $null = Invoke-WindowCommand -Executable $env:WINDOW_TEST_PWSH -Arguments @('-NoProfile','-NonInteractive','-Command',$body) -TimeoutMilliseconds 2000 }
catch { $rejected = $_.Exception.Message -ceq 'SANITIZED_COMMAND_FAILURE' }
if (-not $rejected -or -not (Test-Path -LiteralPath $marker)) { throw 'Fake process timeout not exercised' }
$childId = [int][IO.File]::ReadAllText($marker)
if (Get-Process -Id $childId -ErrorAction SilentlyContinue) { throw 'Owned child survived timeout' }
""",
    )


def test_remote_cleanup_only_names_owned_files_never_original_snapshot(
    powershell, tmp_path
):
    run_private(
        powershell,
        tmp_path,
        r"""
$script:calls = 0
function Invoke-WindowCommand {
    param($Executable, [string[]]$Arguments)
    $script:calls++
    $command = $Arguments[-1]
    if ($command -notmatch '/tmp/competence-hub-admin-[a-f0-9]{32}' -or $command -match '/var/backups|rm -rf|\*' -or
        $command -notmatch 'database.dump.gpg globals.sql.gpg METADATA SHA256SUMS COMPLETE' -or
        $command -notmatch 'snapshot-helper window-root.sh') { throw 'Cleanup scope invalid' }
    return ''
}
Remove-WindowRemoteArtifacts 'FAKE_SSH' ('admin-' + ('a' * 32))
$rejected = $false
try { Remove-WindowRemoteArtifacts 'FAKE_SSH' '../not-owned' } catch { $rejected = $true }
if (-not $rejected -or $script:calls -ne 1) { throw 'Cleanup input accepted' }
""",
    )


def test_human_console_child_discards_stdout_and_reports_its_own_exit(
    powershell, tmp_path
):
    source = SCRIPT.read_text(encoding="ascii")
    body = source.split("function Invoke-WindowConsoleOperator", 1)[1].split(
        "function Invoke-StagingAdminWindow", 1
    )[0]
    assert "RedirectStandardInput = $false" in body
    assert "RedirectStandardError = $false" in body
    assert "RedirectStandardOutput = $true" in body
    assert "$process.ExitCode" in body and "$LASTEXITCODE" not in body
    run_private(
        powershell,
        tmp_path,
        r"""
$body = '[Console]::Write(''SYNTHETIC_OUTPUT_MUST_NOT_LEAK''); exit 0'
$value = Invoke-WindowConsoleOperator $env:WINDOW_TEST_PWSH @('-NoProfile','-NonInteractive','-Command',$body)
if ($null -ne $value) { throw 'Console child stdout leaked' }
$rejected = $false
try { Invoke-WindowConsoleOperator $env:WINDOW_TEST_PWSH @('-NoProfile','-NonInteractive','-Command','exit 9') }
catch { $rejected = $_.Exception.Message -ceq 'OPERATOR_NOT_COMPLETE_NO_BLIND_RETRY' }
if (-not $rejected) { throw 'Child failure was accepted' }
""",
    )


def test_diagnostic_environment_is_denied_without_loading_any_secret(
    powershell, tmp_path
):
    run_private(
        powershell,
        tmp_path,
        r"""
Assert-WindowNoDiagnostics
foreach ($name in @('DEBUG','DEBUG_FILE','DEBUGP','PWDEBUG','PLAYWRIGHT_DRIVER_PATH','PW_TEST_CONNECT_WS_ENDPOINT','NODE_OPTIONS','PYTHONPATH','PYTHONINSPECT')) {
    try {
        [Environment]::SetEnvironmentVariable($name,'SYNTHETIC_DIAGNOSTIC_ONLY','Process')
        $rejected=$false
        try { Assert-WindowNoDiagnostics } catch { $rejected = $_.Exception.Message -ceq 'CLEAN_PRIVATE_DIAGNOSTIC_ENVIRONMENT_REQUIRED' }
        if (-not $rejected) { throw 'Diagnostic context accepted' }
    } finally { [Environment]::SetEnvironmentVariable($name,[NullString]::Value,'Process') }
}
""",
    )


def test_partial_custody_is_reported_without_reading_or_replacing_any_keys(powershell, tmp_path):
    run_private(powershell, tmp_path, r"""
function Get-Content { throw 'Key contents must not be opened' }
function Import-Clixml { throw 'Existing keys must not be imported' }
function Invoke-StagingGpg { throw 'GPG must not be started' }
function Read-Host { throw 'No password prompts in presence check' }
$directory = Join-Path $env:WINDOW_TEST_ROOT 'synthetic-partial'
Assert-WindowCustodyComplete $directory
$null = New-Item -ItemType Directory -Path $directory
foreach ($name in @('staging-operator.keys.clixml','staging-operator.keys.json.gpg')) {
    [IO.File]::WriteAllText((Join-Path $directory $name), 'SYNTHETIC_PRESERVE_EXISTING_BYTES')
}
$rejected = $false
try { Assert-WindowCustodyComplete $directory }
catch { $rejected = $_.Exception.Message -ceq 'CUSTODY_INCOMPLETE_REQUIRES_PRIVATE_RECONCILIATION' }
if (-not $rejected -or @(Get-ChildItem -LiteralPath $directory).Count -ne 2) { throw 'Partial set accepted or modified' }
foreach ($file in Get-ChildItem -LiteralPath $directory) {
    if ([IO.File]::ReadAllText($file.FullName) -cne 'SYNTHETIC_PRESERVE_EXISTING_BYTES') { throw 'Existing file changed' }
}
# Presence is not cryptographic verification: no file content is consulted here.
[IO.File]::WriteAllText((Join-Path $directory 'staging-operator.metadata.json'), 'SYNTHETIC_NOT_A_VALID_PROOF')
Assert-WindowCustodyComplete $directory
""")


def test_stop_diagnostics_emit_only_exact_allowlisted_codes(powershell, tmp_path):
    run_private(powershell, tmp_path, r"""
$code = 'CUSTODY_INCOMPLETE_REQUIRES_PRIVATE_RECONCILIATION'
if ((Get-WindowStopCode $code) -cne $code) { throw 'Known reason hidden' }
foreach ($message in @('SYNTHETIC_SECRET_MUST_NOT_LEAK', ('prefix ' + $code), $code.ToLowerInvariant())) {
    if ((Get-WindowStopCode $message) -cne 'PRIVATE_MANUAL_REVIEW_REQUIRED') { throw 'Untrusted error text escaped' }
}
""")


def test_partial_custody_guard_precedes_any_key_initialization_or_server_activity():
    source = SCRIPT.read_text(encoding="ascii")
    body = source.split("function Invoke-StagingAdminWindow", 1)[1]
    assert body.index("Assert-WindowCustodyComplete $custody") < body.index("New-StagingPrivateDirectory $output")
    assert body.index("Assert-WindowCustodyComplete $custody") < body.index("Initialize-StagingOperatorConfig")
    assert body.index("Assert-WindowCustodyComplete $custody") < body.index("Get-WindowHealth $ssh")
