"""Offline local custody tests, never real operator preparation or GPG access.

DPAPI/ACL tests use freshly generated synthetic memory and isolated temp files.
The initializer flow is called programmatically with GPG/corpus stubs, not a
production rehearsal flag. A fake round trip is NOT real GPG/pinentry evidence.
Subprocess output is suppressed on failure as well as success; no keys printed.
"""

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "deploy/scripts/initialize-staging-operator-config.ps1"
CORPUS_SHA = "80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da"


def test_local_admin_runner_is_cached_owned_and_fixed_loopback_only():
    source = (ROOT / "scripts/run-initial-admin-local.ps1").read_text(encoding="ascii")
    for required in (
        "postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825",
        "--pull never",
        "'127.0.0.1:55438:5432'",
        "--tmpfs '/var/lib/postgresql/data'",
        "COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_APP_URL",
        "COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_OWNER_URL",
        "COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_NONCE",
        "synthetic-initial-admin-owned:$nonce",
        "$migrations.Count -ne 9",
        "test_initial_admin_postgres_local.py",
        "competence-hub-initial-admin-local-nonce",
        "docker rm --force $container",
        'docker ps -aq --filter "id=$container"',
        "OWNED_INITIAL_ADMIN_CONTAINER_REMOVED=PASS",
    ):
        assert required in source
    for forbidden in (
        "docker pull",
        "ssh ",
        "scp ",
        "sftp ",
        "staging_admin_operator.py --login-file",
        "backup-gnupg",
    ):
        assert forbidden not in source


def test_initializer_is_bounded_dpapi_and_stream_only_portable_custody():
    source = SCRIPT.read_text(encoding="ascii")
    for required in (
        "Export-Clixml",
        "-NoClobber",
        "Import-Clixml",
        "SecureStringToBSTR",
        "ZeroFreeBSTR",
        "[IO.FileMode]::CreateNew",
        "SetAccessRuleProtection($true, $false)",
        "'S-1-5-18'",
        "ReparsePoint",
        "AcknowledgeProtectedStorage",
        "AcknowledgeOperatorCustody",
        "'--pinentry-mode', 'ask'",
        "'--no-auto-key-retrieve'",
        "'--auto-key-locate', 'clear'",
        "'--no-options'",
        "StandardInput.BaseStream.Write($InputBytes",
        "RedirectStandardOutput = $true",
        "FixedTimeEquals($plain, $restored)",
        "if ($MyInvocation.InvocationName -ne '.')",
        CORPUS_SHA,
        "2E44306121629A100F76A8B08CCA3D9186A28D4C",
    ):
        assert required in source
    for forbidden in (
        "SyntheticRehearsal",
        "--passphrase",
        "--pinentry-mode loopback",
        "Out-File",
        "Set-Content",
        "Remove-Item",
        "Invoke-WebRequest",
        "Invoke-RestMethod",
        "list-secret-keys",
        "ssh ",
        "scp ",
        "sftp ",
        "DATABASE_URL",
        "Read-Host",
    ):
        assert forbidden not in source
    assert source.index("FixedTimeEquals($plain, $restored)") < source.index(
        "status = 'READY'"
    )
    assert "$start.ArgumentList.Add($plain)" not in source
    assert "$start.ArgumentList.Add($text)" not in source


@pytest.fixture
def powershell():
    executable = shutil.which("pwsh")
    if os.name != "nt" or not executable:
        pytest.skip("requires native Windows PowerShell 7 DPAPI/ACL support")
    return executable


def run_private(powershell, tmp_path, body):
    # Explicit non-secret platform environment only; do not inherit runtime keys,
    # DB URLs, GPG home overrides or actual operator configuration.
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
            "CUSTODY_TEST_ROOT": str(tmp_path),
            "CUSTODY_TEST_SCRIPT": str(SCRIPT),
            "CUSTODY_TEST_POWERSHELL": powershell,
            "CUSTODY_TEST_PYTHON": sys.executable,
            "CUSTODY_TEST_SOURCE": str(ROOT / "apps/webapp/src"),
            "CUSTODY_TEST_RUNTIME_CHECK": str(tmp_path / "runtime-check.py"),
        }
    )
    command = (
        r"""
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$parseErrors = $null; $tokens = $null
$null = [Management.Automation.Language.Parser]::ParseFile($env:CUSTODY_TEST_SCRIPT, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'PowerShell syntax failed.' }
. $env:CUSTODY_TEST_SCRIPT
$script:CheckStage = 0
try {
"""
        + body
        + r"""
} catch {
    Write-Output ('CHECK_FAILURE_STAGE=' + $script:CheckStage + ';LINE=' + $_.InvocationInfo.ScriptLineNumber)
    exit 1
}
Write-Output 'PRIVATE_CUSTODY_CHECK=PASS'
"""
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0 or result.stdout.strip() != "PRIVATE_CUSTODY_CHECK=PASS":
        location = re.search(r"CHECK_FAILURE_STAGE=\d+;LINE=\d+", result.stdout)
        pytest.fail(
            "Isolated custody check failed; output suppressed. "
            + (location[0] if location else ""),
            pytrace=False,
        )


def test_dot_source_is_definition_only(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
if (@(Get-ChildItem -LiteralPath $env:CUSTODY_TEST_ROOT -Force).Count) { throw 'Dot source created artifacts.' }
foreach ($name in @('Initialize-StagingOperatorConfig', 'Use-StagingOperatorEnvironment')) {
    if (-not (Get-Command $name -CommandType Function)) { throw 'Missing API.' }
}
""",
    )


def test_path_origin_and_acknowledgment_guards(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
foreach ($bad in @([IO.Path]::GetPathRoot($env:CUSTODY_TEST_ROOT), $script:OperatorRepositoryRoot,
    [IO.Path]::GetDirectoryName($script:OperatorRepositoryRoot), (Join-Path $script:OperatorRepositoryRoot 'private'),
    '\\server\share\private', (Join-Path $env:CUSTODY_TEST_ROOT 'private:stream'),
    (Join-Path $env:CUSTODY_TEST_ROOT 'trailing.'))) {
    $rejected = $false
    try { $null = Assert-StagingExternalPath $bad } catch { $rejected = $true }
    if (-not $rejected) { throw 'Unsafe path accepted.' }
}
foreach ($bad in @('http://portal.invalid', 'https://portal.invalid/', 'https://portal.invalid/path',
    'https://user:password@portal.invalid', 'https://*.invalid', 'https://portal.invalid?x=1')) {
    $rejected = $false
    try { Assert-StagingOrigin $bad } catch { $rejected = $true }
    if (-not $rejected) { throw 'Unsafe origin accepted.' }
}
Assert-StagingOrigin 'https://127.0.0.1:8443'
$target = Join-Path $env:CUSTODY_TEST_ROOT 'not-created'
foreach ($ack in @(@{}, @{AcknowledgeProtectedStorage=$true}, @{AcknowledgeOperatorCustody=$true})) {
    $rejected = $false
    try {
        $null = Initialize-StagingOperatorConfig -StorageDirectory $target -FingerprintPath 'absent' `
            -AllowedOrigin 'https://portal.invalid' -GpgHome 'absent' @ack
    } catch { $rejected = $true }
    if (-not $rejected -or (Test-Path -LiteralPath $target)) { throw 'Acknowledgment gate failed.' }
}
""",
    )


def test_reparse_collision_and_real_private_acl(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
$target = Join-Path $env:CUSTODY_TEST_ROOT 'private'
New-StagingPrivateDirectory $target
Assert-StagingPrivateAcl $target -Directory
$marker = Join-Path $target 'existing.txt'
[IO.File]::WriteAllText($marker, 'owned synthetic marker')
$rejected = $false
try { New-StagingPrivateDirectory $target } catch { $rejected = $true }
if (-not $rejected -or [IO.File]::ReadAllText($marker) -cne 'owned synthetic marker') { throw 'Collision changed existing data.' }
$junction = Join-Path $env:CUSTODY_TEST_ROOT 'junction'
$null = New-Item -ItemType Junction -Path $junction -Target $target
try {
    foreach ($bad in @($junction, (Join-Path $junction 'child'))) {
        $rejected = $false
        try { $null = Assert-StagingExternalPath $bad } catch { $rejected = $true }
        if (-not $rejected) { throw 'Reparse path accepted.' }
    }
} finally { Remove-Item -LiteralPath $junction -Force }
""",
    )


def test_actual_synthetic_dpapi_roundtrip_and_five_distinct_keys(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
$directory = Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-dpapi'
New-StagingPrivateDirectory $directory
$path = Join-Path $directory 'synthetic.clixml'
$secret = New-StagingOperatorSecret
$secret | Export-Clixml -LiteralPath $path -NoClobber -Encoding utf8
$loaded = Import-Clixml -LiteralPath $path
if ($loaded -isnot [Security.SecureString]) { throw 'DPAPI type contract failed.' }
$left = [IntPtr]::Zero; $right = [IntPtr]::Zero
try {
    $left = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    $right = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($loaded)
    $a = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($left)
    $b = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($right)
    if ($a -cne $b -or [IO.File]::ReadAllText($path).Contains($a)) { throw 'DPAPI persistence failed.' }
    $payload = $b | ConvertFrom-Json -AsHashtable
    if ($payload.schema -ne 1 -or $payload.environment -cne 'staging' -or $payload.variables.Count -ne 8) { throw 'Payload contract failed.' }
    $values = @($payload.variables.COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY, $payload.variables.COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY)
    foreach ($stem in @('TOTP', 'OUTBOX', 'RECOVERY_HMAC')) {
        $ring = $payload.variables["COMPETENCE_HUB_${stem}_KEYRING"] | ConvertFrom-Json -AsHashtable
        $version = $payload.variables["COMPETENCE_HUB_${stem}_ACTIVE_KEY_VERSION"]
        if ($ring.Count -ne 1 -or -not $ring.ContainsKey($version)) { throw 'Versioned ring failed.' }
        $values += $ring[$version]
    }
    if (@($values | Select-Object -Unique).Count -ne 5) { throw 'Keys are not distinct.' }
    foreach ($value in $values) {
        $bytes = [Convert]::FromBase64String($value)
        try {
            if ($bytes.Length -ne 32 -or [IO.File]::ReadAllText($path).Contains($value)) { throw 'Invalid persisted key.' }
        } finally { [Array]::Clear($bytes, 0, $bytes.Length) }
    }
    Assert-StagingPrivateAcl $path
} finally {
    if ($left -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($left) }
    if ($right -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($right) }
    $secret.Dispose(); $loaded.Dispose(); $a=$null; $b=$null; $payload=$null; $values=$null
}
""",
    )


def test_corpus_checks_reject_zero_small_changed_and_duplicate_lists(
    powershell, tmp_path
):
    # Synthetic PUBLIC parser inputs only, never an operational corpus substitute.
    fingerprint = hashlib.sha256(b"synthetic parser entry").hexdigest() + "\n"
    cases = ["0" * 64 + "\n", fingerprint, fingerprint * 2]
    for number, value in enumerate(cases):
        (tmp_path / f"parser-{number}.sha256").write_text(value, encoding="ascii")
    run_private(
        powershell,
        tmp_path,
        r"""
foreach ($path in (Get-ChildItem -LiteralPath $env:CUSTODY_TEST_ROOT -Filter '*.sha256').FullName) {
    $sha = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    foreach ($expected in @($sha, ('1' * 64))) {
        $rejected=$false
        try { $null = Assert-StagingCorpus $path $expected } catch { $rejected=$true }
        if (-not $rejected) { throw 'Invalid corpus accepted.' }
    }
}
""",
    )


def test_large_public_parser_fixture_accepts_only_its_exact_hash(powershell, tmp_path):
    # Parser-only fixture, never used by the initializer or a real account.
    data = "".join(
        hashlib.sha256(f"public-parser-{n}".encode()).hexdigest() + "\n"
        for n in range(90000)
    )
    (tmp_path / "large-parser.sha256").write_text(data, encoding="ascii", newline="\n")
    run_private(
        powershell,
        tmp_path,
        r"""
$path = Join-Path $env:CUSTODY_TEST_ROOT 'large-parser.sha256'
$sha = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
if ((Assert-StagingCorpus $path $sha) -cne $path) { throw 'Hash-bound public parser validation failed.' }
""",
    )


STUBBED_FLOW = r"""
# Only freshly created synthetic paths are used. No actual GPG executable/home.
function Assert-StagingCorpus { param($Path, $ExpectedSha256); return (Assert-StagingExternalPath $Path) }
function Invoke-StagingGpg {
    param($Executable, $KeyHome, $Mode, $InputBytes, $EncryptedPath, $OutputStream)
    if ($Mode -eq 'Encrypt') {
        $script:SyntheticMemory = $InputBytes.Clone()
        $cipher = [Text.Encoding]::UTF8.GetBytes('FAKE-CIPHERTEXT-TEST-ONLY')
        $OutputStream.Write($cipher, 0, $cipher.Length)
    } else {
        if ($script:FailDecrypt) { throw 'Synthetic decryption refusal.' }
        if ($script:CorruptDecrypt) { $OutputStream.WriteByte(1) }
        else { $OutputStream.Write($script:SyntheticMemory, 0, $script:SyntheticMemory.Length) }
    }
}
$script:FailDecrypt = $false
$script:CorruptDecrypt = $false
$script:SyntheticMemory = $null
$keyHome = Join-Path $env:CUSTODY_TEST_ROOT 'empty-fake-gpg-home'
$null = New-Item -ItemType Directory -Path $keyHome
$directory = Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-flow'
$corpus = Join-Path $env:CUSTODY_TEST_ROOT 'public-parser-only.sha256'
[IO.File]::WriteAllText($corpus, ('f' * 64))
$inputs = @{StorageDirectory=$directory; FingerprintPath=$corpus; AllowedOrigin='https://portal.invalid';
    GpgHome=$keyHome; GpgExecutable=[Environment]::ProcessPath;
    AcknowledgeProtectedStorage=$true; AcknowledgeOperatorCustody=$true}
"""


def test_stubbed_initializer_ready_metadata_scoped_environment_and_no_overwrite(
    powershell, tmp_path
):
    (tmp_path / "runtime-check.py").write_text(
        """from competence_hub_api.config import RuntimeSettings
settings = RuntimeSettings.from_environment()
assert len(settings.recovery_hmac_keys[settings.recovery_hmac_active_key_version]) == 32
""",
        encoding="ascii",
    )
    run_private(
        powershell,
        tmp_path,
        STUBBED_FLOW + r"""
try {
    $script:CheckStage=1
    $result = Initialize-StagingOperatorConfig @inputs
    $script:CheckStage=2
    if ($result.status -cne 'READY') { throw 'Missing READY.' }
    if (@($result.PSObject.Properties.Name).Count -ne 7) { throw 'Unexpected status output.' }
    $metadata = [IO.File]::ReadAllText($result.metadata_path)
    $record = $metadata | ConvertFrom-Json -AsHashtable
    if ($record.corpus_sha256 -cne '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da' -or
        $record.key_versions.totp -cne 'staging-totp-v1' -or -not $record.portable_backup_verified) { throw 'Metadata contract failed.' }
    $plain = [Text.Encoding]::UTF8.GetString($script:SyntheticMemory) | ConvertFrom-Json -AsHashtable
    $secretValues = @($plain.variables.COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY, $plain.variables.COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY)
    foreach ($stem in @('TOTP', 'OUTBOX', 'RECOVERY_HMAC')) {
        $ring = $plain.variables["COMPETENCE_HUB_${stem}_KEYRING"] | ConvertFrom-Json -AsHashtable
        $secretValues += @($ring.Values)
    }
    foreach ($value in $secretValues) {
        if ($metadata.Contains($value)) { throw 'Metadata contains a key value.' }
    }
    $env:COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY='synthetic-previous-value'
    $script:CheckStage=3
    Use-StagingOperatorEnvironment -StorageDirectory $directory -AcknowledgeOperatorCustody -Action {
        $script:CheckStage=31
        if ($env:COMPETENCE_HUB_ALLOWED_ORIGIN -cne 'https://portal.invalid' -or
            $env:COMPETENCE_HUB_TOTP_ACTIVE_KEY_VERSION -cne 'staging-totp-v1' -or
            $env:COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH -cne $corpus -or
            $env:COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY -ceq 'synthetic-previous-value') { throw 'Scoped environment failed.' }
        $env:PYTHONPATH=$env:CUSTODY_TEST_SOURCE
        $env:COMPETENCE_HUB_DATABASE_URL='postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:5432/competence_hub_staging'
        $script:CheckStage=32
        $child = [Diagnostics.Process]::new()
        $child.StartInfo.FileName = $env:CUSTODY_TEST_PYTHON
        $child.StartInfo.ArgumentList.Add($env:CUSTODY_TEST_RUNTIME_CHECK)
        $child.StartInfo.UseShellExecute = $false
        $child.StartInfo.RedirectStandardOutput = $true
        $child.StartInfo.RedirectStandardError = $true
        try {
            $null = $child.Start()
            $childOut = $child.StandardOutput.ReadToEndAsync()
            $childError = $child.StandardError.ReadToEndAsync()
            $child.WaitForExit()
            $script:CheckStage=3300+$child.ExitCode
            if ($child.ExitCode -ne 0 -or $childOut.GetAwaiter().GetResult()) {
                throw 'Native RuntimeSettings compatibility failed.'
            }
            $null = $childError.GetAwaiter().GetResult()
        } finally { $child.Dispose() }
        # Deliberate synthetic return: the loader must suppress pipeline output.
        $env:COMPETENCE_HUB_TOTP_KEYRING
    }
    if ($env:COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY -cne 'synthetic-previous-value' -or
        (Test-Path Env:COMPETENCE_HUB_TOTP_KEYRING)) { throw 'Environment leaked after success.' }
    $rejected=$false
    $script:CheckStage=4
    try {
        Use-StagingOperatorEnvironment -StorageDirectory $directory -AcknowledgeOperatorCustody -Action { throw 'Synthetic callback refusal.' }
    } catch { $rejected=$true }
    if (-not $rejected -or $env:COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY -cne 'synthetic-previous-value' -or
        (Test-Path Env:COMPETENCE_HUB_TOTP_KEYRING)) { throw 'Environment leaked after failure.' }
    $rejected=$false
    $script:CheckStage=5
    try { $null = Initialize-StagingOperatorConfig @inputs } catch { $rejected=$true }
    if (-not $rejected -or (Get-FileHash $result.store_path).Hash.ToLowerInvariant() -cne $record.store_sha256) { throw 'Store was overwritten.' }
    [IO.File]::AppendAllText($result.backup_path, 'synthetic tamper')
    $script:CheckStage=6
    $rejected=$false
    $script:UnexpectedAction=$false
    try { Use-StagingOperatorEnvironment -StorageDirectory $directory -AcknowledgeOperatorCustody -Action { $script:UnexpectedAction=$true } } catch { $rejected=$true }
    if (-not $rejected -or $script:UnexpectedAction) { throw 'Tampered backup accepted.' }
} finally {
    if ($script:SyntheticMemory) { [Array]::Clear($script:SyntheticMemory, 0, $script:SyntheticMemory.Length) }
    $plain=$null; $secretValues=$null; $ring=$null
}
""",
    )


@pytest.mark.parametrize("failure", ["FailDecrypt", "CorruptDecrypt"])
def test_stubbed_failed_decryption_retains_private_store_without_ready(
    powershell, tmp_path, failure
):
    run_private(
        powershell,
        tmp_path,
        STUBBED_FLOW + f"\n$script:{failure}=$true\n" + r"""
try {
    $rejected=$false
    try { $null = Initialize-StagingOperatorConfig @inputs } catch { $rejected=$true }
    if (-not $rejected -or -not (Test-Path -LiteralPath (Join-Path $directory $script:OperatorStoreName)) -or
        (Test-Path -LiteralPath (Join-Path $directory $script:OperatorMetadataName))) { throw 'Failed verification published READY or removed the private store.' }
    Assert-StagingPrivateAcl $directory -Directory
} finally {
    if ($script:SyntheticMemory) { [Array]::Clear($script:SyntheticMemory, 0, $script:SyntheticMemory.Length) }
}
""",
    )
