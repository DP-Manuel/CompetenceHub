"""Private entry contract tested with synthetic files only; no USB/key/GPG/SSH."""

from pathlib import Path

import pytest

from test_staging_admin_window_contract import powershell, run_private, SCRIPT as WINDOW
from test_staging_operator_custody import run_private as custody_private, STUBBED_FLOW

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/verify-staging-keys.ps1"


def test_resume_default_definition_and_no_secret_read(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
$resume = Join-Path (Split-Path $env:WINDOW_TEST_SCRIPT) 'resume-staging-admin-window.ps1'
function Get-Content { throw 'Must not open any private input' }
function Import-Clixml { throw 'Must not load keys by default' }
function Read-Host { throw 'Must not prompt by default' }
$output = & $resume
if ($output -cne 'STAGING_KEYS=NOT_EXECUTED LOCAL_ONLY=YES REAL_COACH_APPLY=DISABLED') { throw 'Unsafe default' }
$newEntry = Join-Path (Split-Path $env:WINDOW_TEST_SCRIPT) 'verify-staging-keys.ps1'
if ((& $newEntry) -cne $output) { throw 'Canonical default differs' }
. $resume
if (-not (Get-Command Invoke-ExistingStagingResume -CommandType Function)) { throw 'Missing entry function' }
if (@(Get-ChildItem -LiteralPath $env:WINDOW_TEST_ROOT -Force).Count) { throw 'Default created files' }
""",
    )


@pytest.mark.parametrize(
    "block,answer,accepted",
    [
        ("BACKUP", "BACKUP", True),
        ("ADMIN", "ADMIN", True),
        ("BACKUP", "ADMIN", False),
        ("ADMIN", "BACKUP", False),
        ("ADMIN", "admin", False),
        ("ADMIN", "", False),
    ],
)
def test_distinct_runtime_approval_tokens(
    powershell, tmp_path, block, answer, accepted
):
    run_private(
        powershell,
        tmp_path,
        r"""
function Write-Host { }
"""
        + f"function Read-Host {{ return '{answer}' }}\n"
        + r"""
$denied=$false
"""
        + f"try {{ Confirm-WindowOperation -Block {block} }} catch {{ $denied=$_.Exception.Message -ceq 'OPERATION_BLOCK_NOT_APPROVED' }}\n"
        + f"if ($denied -eq ${str(accepted).lower()}) {{ throw 'Wrong approval decision' }}\n",
    )


@pytest.mark.parametrize("case", ["new", "repeat", "corrupt-existing"])
def test_usb_copy_is_exclusive_encrypted_only_and_hash_bound(
    powershell, tmp_path, case
):
    run_private(
        powershell,
        tmp_path,
        r"""
. (Join-Path (Split-Path $env:WINDOW_TEST_SCRIPT) 'resume-staging-admin-window.ps1')
function Write-Host { }
$directory = Join-Path $env:WINDOW_TEST_ROOT 'synthetic-store'
$usb = Join-Path $env:WINDOW_TEST_ROOT 'synthetic-usb'
$null = New-Item -ItemType Directory -Path $directory,$usb
function Assert-ResumeUsb { param($Path) if ($Path -cne $usb) { throw 'Must remain in isolated test path' } }
function Assert-StagingPrivateAcl { param($Path) if ($Path -cne (Join-Path $directory 'staging-operator.keys.json.gpg')) { throw 'Wrong source' } }
$source = Join-Path $directory 'staging-operator.keys.json.gpg'
[IO.File]::WriteAllText($source,'SYNTHETIC_ENCRYPTED_BYTES_NOT_REAL_GPG')
$hash = (Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant()
$target = Join-Path (Join-Path $usb 'staging-operator-key-backups') ($hash + '.keys.json.gpg')
$bindingRejected=$false
try { Copy-ResumeEncryptedKeyBackup -StorageDirectory $directory -UsbDirectory $usb -ExpectedSha256 ('0' * 64) } catch { $bindingRejected=$true }
if (-not $bindingRejected -or (Test-Path -LiteralPath (Split-Path $target))) { throw 'Unverified ciphertext was copied' }
Copy-ResumeEncryptedKeyBackup -StorageDirectory $directory -UsbDirectory $usb -ExpectedSha256 $hash
if ((Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant() -cne $hash) { throw 'Copy mismatch' }
"""
        + (
            r"""
Copy-ResumeEncryptedKeyBackup -StorageDirectory $directory -UsbDirectory $usb -ExpectedSha256 $hash
"""
            if case == "repeat"
            else (
                r"""
[IO.File]::WriteAllText($target,'SYNTHETIC_CORRUPT_EXISTING_DO_NOT_OVERWRITE')
$failed=$false
try { Copy-ResumeEncryptedKeyBackup -StorageDirectory $directory -UsbDirectory $usb -ExpectedSha256 $hash } catch { $failed=$true }
if (-not $failed -or [IO.File]::ReadAllText($target) -cne 'SYNTHETIC_CORRUPT_EXISTING_DO_NOT_OVERWRITE') { throw 'Existing copy overwritten or ignored' }
"""
                if case == "corrupt-existing"
                else ""
            )
        )
        + r"""
if ((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -cne $hash) { throw 'Original encrypted key backup changed' }
if (@(Get-ChildItem -LiteralPath (Split-Path $target)).Count -ne 1) { throw 'Unexpected files copied' }
""",
    )


@pytest.mark.parametrize(
    "entry", ["verify-staging-keys.ps1", "resume-staging-admin-window.ps1"]
)
def test_both_cli_entries_fail_safely_before_private_io_for_unreviewed_source(
    powershell, tmp_path, entry
):
    run_private(
        powershell,
        tmp_path,
        r"""
function Read-Host { throw 'No dialog allowed for invalid source' }
function Import-Clixml { throw 'No private data allowed for invalid source' }
"""
        + f"$entry=Join-Path (Split-Path $env:WINDOW_TEST_SCRIPT) '{entry}'\n"
        + r"""
$value=& $entry -Execute -ExpectedSourceCommit 'not-a-reviewed-commit'
if ($LASTEXITCODE -ne 1 -or $value) { throw 'Wrong CLI failure status or unexpected output' }
if (@(Get-ChildItem -LiteralPath $env:WINDOW_TEST_ROOT -Force).Count) { throw 'Invalid source created files' }
""",
    )


def test_resume_order_and_scope_are_explicit():
    source = SCRIPT.read_text(encoding="ascii")
    body = source.split("function Invoke-ExistingStagingResume", 1)[1]
    stages = [
        "Assert-LocalKeySource $Commit",
        "Assert-ResumeUsb",
        "PRIOR_ADMIN_ATTEMPT_REQUIRES_REVIEW",
        "EXISTING_KEY_PAIR_REQUIRED_NO_INITIALIZATION",
        "Confirm-LocalKeyOperation",
        "Complete-StagingOperatorConfig",
        "Use-StagingOperatorEnvironment",
        "Copy-ResumeEncryptedKeyBackup",
        "scope='LOCAL_KEYS_ONLY'",
    ]
    assert [body.index(s) for s in stages] == sorted(body.index(s) for s in stages)
    for forbidden in (
        "Initialize-StagingOperatorConfig",
        "New-StagingOperatorSecret",
        "Remove-Item",
        "Import-Clixml",
        "ReadAllText",
        "Get-Clipboard",
        "Start-Transcript",
        "--passphrase",
        "CREATE USER",
        "coach3b_real_apply",
        "Invoke-StagingAdminWindow",
        "run-staging-admin-window.ps1",
        "ls-remote",
        "docker.exe",
        "ssh.exe",
    ):
        assert forbidden not in source
    assert "[IO.FileMode]::CreateNew" in source
    assert source.count("Get-Content") == 1
    assert "Get-Content -Raw -LiteralPath $metadata" in source
    assert "-ExpectedSha256 $verified.backup_sha256" in source
    assert "$answer.Trim()" in source and "OrdinalIgnoreCase" in source
    assert "Existing metadata" not in source  # presence -> verify, never replace
    window = WINDOW.read_text(encoding="ascii").split(
        "function Invoke-StagingAdminWindow", 1
    )[1]
    assert window.index("Confirm-WindowOperation -Block BACKUP") < window.index(
        "Get-WindowHealth $ssh"
    )
    assert (
        window.index("ACTUAL_RESTORE_PROOF_REQUIRED")
        < window.index("Confirm-WindowOperation -Block ADMIN")
        < window.index("Write-WindowRecord $attempt")
    )


def test_usb_rejects_unknown_target_before_lookup(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
. (Join-Path (Split-Path $env:WINDOW_TEST_SCRIPT) 'resume-staging-admin-window.ps1')
function Test-Path { throw 'Path must reject before probing' }
$denied=$false
try { Assert-ResumeUsb -Path 'C:\Unexpected' } catch { $denied=$_.Exception.Message -ceq 'APPROVED_USB_DIRECTORY_REQUIRED' }
if (-not $denied) { throw 'Unapproved USB path accepted' }
""",
    )


@pytest.mark.parametrize(
    "answer,code",
    [
        ("VERIFY", None),
        ("verify", None),
        (" VerIfY  ", None),
        ("\tVERIFY\t", None),
        ("", "KEY_CONFIRMATION_CANCELLED"),
        ("   ", "KEY_CONFIRMATION_CANCELLED"),
        ("yes", "KEY_CONFIRMATION_INVALID"),
        ("VERIFY NOW", "KEY_CONFIRMATION_INVALID"),
        ("NOT_VERIFY", "KEY_CONFIRMATION_INVALID"),
    ],
)
def test_local_verify_normalizes_only_exact_confirmation_and_explains_failure(
    powershell, tmp_path, answer, code
):
    encoded = answer.replace("\t", "`t")
    run_private(
        powershell,
        tmp_path,
        r"""
. (Join-Path (Split-Path $env:WINDOW_TEST_SCRIPT) 'verify-staging-keys.ps1')
$script:Messages = @()
function Write-Host { param($Object) $script:Messages += [string]$Object }
"""
        + f'function Read-Host {{ return "{encoded}" }}\n'
        + r"""
$caught = $null
try { Confirm-LocalKeyOperation } catch { $caught=$_.Exception.Message }
"""
        + (
            f"if ($caught -cne '{code}' -or $script:Messages.Count -ne 1) {{ throw 'Missing safe explanation' }}\n"
            if code
            else "if ($caught -or $script:Messages.Count) { throw 'Valid confirmation rejected' }\n"
        )
        + (
            "if ($script:Messages[0] -notmatch 'VERIFY.*verify' -or $script:Messages[0] -notmatch 'Kein Passwort') { throw 'Expected input is unclear' }\n"
            if code == "KEY_CONFIRMATION_INVALID"
            else ""
        ),
    )


def test_local_verify_interrupt_has_message_and_no_retry(powershell, tmp_path):
    run_private(
        powershell,
        tmp_path,
        r"""
. (Join-Path (Split-Path $env:WINDOW_TEST_SCRIPT) 'verify-staging-keys.ps1')
$script:Prompts=0; $script:Messages=0
function Read-Host { $script:Prompts++; throw 'SYNTHETIC_PRIVATE_ERROR_NEVER_ECHO' }
function Write-Host { param($Object) if ($Object -match 'SYNTHETIC_PRIVATE') { throw 'Private error leaked' }; $script:Messages++ }
$cancelled=$false
try { Confirm-LocalKeyOperation } catch { $cancelled=$_.Exception.Message -ceq 'KEY_CONFIRMATION_CANCELLED' }
if (-not $cancelled -or $script:Prompts -ne 1 -or $script:Messages -ne 1) { throw 'Missing cancellation or repeated prompt' }
""",
    )


@pytest.mark.parametrize(
    "case",
    [
        "success-repeat",
        "confirmation-cancel",
        "gpg-cancel",
        "copy-resume",
        "existing-proof",
        "changed-proof",
    ],
)
def test_complete_local_key_block_resume_without_any_server_or_new_keys(
    powershell, tmp_path, case
):
    prefix = f". '{SCRIPT.as_posix()}'\n"
    custody_private(
        powershell,
        tmp_path,
        prefix
        + STUBBED_FLOW
        + r"""
function Write-Host { }
$script:CorruptDecrypt=$true
try { $null=Initialize-StagingOperatorConfig @inputs } catch { }
$script:CorruptDecrypt=$false
$inputs.AllowedOrigin='https://127.0.0.1:443'
$store=Join-Path $directory 'staging-operator.keys.clixml'
$backup=Join-Path $directory 'staging-operator.keys.json.gpg'
$metadata=Join-Path $directory 'staging-operator.metadata.json'
$storeHash=(Get-FileHash -LiteralPath $store).Hash
$backupHash=(Get-FileHash -LiteralPath $backup).Hash.ToLowerInvariant()
$usb=Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-usb'
$null=New-Item -ItemType Directory -Path $usb
$target=Join-Path (Join-Path $usb 'staging-operator-key-backups') ($backupHash + '.keys.json.gpg')
$script:Prompts=0; $script:Decrypts=0; $script:Completions=0; $script:CopyFail=$false
$script:Answer=' verify '
function Read-Host { $script:Prompts++; return $script:Answer }
function Assert-LocalKeySource { param($Commit) if ($Commit -cne ('a' * 40)) { throw 'Unreviewed test source' } }
function Get-LocalKeyPaths { return @{custody=$directory;corpus=$corpus;gpg=$keyHome;usb=$usb} }
function Assert-ResumeUsb { param($Path) if ($Path -cne $usb) { throw 'Real USB must not be accessed' } }
function New-StagingOperatorSecret { throw 'Existing keys must never be regenerated' }
function Invoke-StagingAdminWindow { throw 'LOCAL BLOCK MUST NOT REACH ADMIN' }
function Invoke-WindowCommand { throw 'LOCAL BLOCK MUST NOT REACH A SERVER' }
function Invoke-StagingGpg {
    param($Executable,$KeyHome,$Mode,$InputBytes,$EncryptedPath,$OutputStream)
    if ($Mode -cne 'Decrypt' -or $InputBytes) { throw 'No encryption, rotation or new keys' }
    $script:Decrypts++
    if ($script:FailDecrypt) { throw 'SYNTHETIC_PRIVATE_GPG_CANCELLATION' }
    $OutputStream.Write($script:SyntheticMemory,0,$script:SyntheticMemory.Length)
}
$script:OriginalComplete=(Get-Command Complete-StagingOperatorConfig).ScriptBlock
function Complete-StagingOperatorConfig {
    param($StorageDirectory,$FingerprintPath,$ExpectedCorpusSha256,$AllowedOrigin,$GpgHome,$GpgExecutable,
          [switch]$AcknowledgeProtectedStorage,[switch]$AcknowledgeOperatorCustody)
    if ($StorageDirectory -cne $directory -or $FingerprintPath -cne $corpus -or $GpgHome -cne $keyHome -or
        $AllowedOrigin -cne 'https://127.0.0.1:443' -or -not $AcknowledgeProtectedStorage -or -not $AcknowledgeOperatorCustody) { throw 'Wrong completion contract' }
    $script:Completions++
    $argsForTest=$inputs.Clone(); $argsForTest.AllowedOrigin=$AllowedOrigin
    & $script:OriginalComplete @argsForTest
}
$script:OriginalCopy=(Get-Command Copy-ResumeEncryptedKeyBackup).ScriptBlock
function Copy-ResumeEncryptedKeyBackup {
    param($StorageDirectory,$UsbDirectory,$ExpectedSha256)
    if ($script:CopyFail) { throw 'Synthetic USB disconnection' }
    & $script:OriginalCopy -StorageDirectory $StorageDirectory -UsbDirectory $UsbDirectory -ExpectedSha256 $ExpectedSha256
}
"""
        + f"$case='{case}'\n"
        + r"""
try {
    if ($case -ceq 'existing-proof') { $null=Complete-StagingOperatorConfig @inputs -ExpectedCorpusSha256 ('f' * 64) }
    if ($case -ceq 'confirmation-cancel') { $script:Answer='' }
    if ($case -ceq 'gpg-cancel') { $script:FailDecrypt=$true }
    if ($case -ceq 'copy-resume') { $script:CopyFail=$true }
    $failed=$false; $result=$null
    try { $result=Invoke-ExistingStagingResume -Commit ('a' * 40) } catch { $failed=$true }
    if ($case -cin @('confirmation-cancel','gpg-cancel','copy-resume')) {
        if (-not $failed -or (Test-Path -LiteralPath $target)) { throw 'Cancelled step copied a file' }
        if ($case -ceq 'confirmation-cancel' -and ($script:Completions -or $script:Decrypts)) { throw 'Cancel opened keys' }
        if ($case -ceq 'gpg-cancel' -and ((Test-Path -LiteralPath $metadata) -or $script:Decrypts -ne 1)) { throw 'GPG cancellation retried or published metadata' }
        $script:Answer='VERIFY'; $script:FailDecrypt=$false; $script:CopyFail=$false
        $result=Invoke-ExistingStagingResume -Commit ('a' * 40)
    } elseif ($failed) { throw 'Local run failed' }
    if ($result.status -cne 'PASS' -or $result.scope -cne 'LOCAL_KEYS_ONLY' -or
        $result.server_actions -cne 'NONE' -or $result.real_coach_apply -cne 'DISABLED') { throw 'Local scope not proven' }
    if ((Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant() -cne $backupHash) { throw 'Copy hash mismatch' }
    $decrypts=$script:Decrypts; $completions=$script:Completions
    if ($case -ceq 'changed-proof') {
        $record=Get-Content -Raw -LiteralPath $metadata | ConvertFrom-Json -AsHashtable
        $record.backup_sha256='0' * 64
        [IO.File]::WriteAllText($metadata,($record | ConvertTo-Json -Depth 8))
        $rejected=$false
        try { $null=Invoke-ExistingStagingResume -Commit ('a' * 40) } catch { $rejected=$true }
        if (-not $rejected) { throw 'Changed proof accepted' }
    } else {
        $result=Invoke-ExistingStagingResume -Commit ('a' * 40)
        if ($result.gpg_verification -cne 'EXISTING_BOUND_PROOF') { throw 'Existing proof not reused' }
    }
    if ($script:Decrypts -ne $decrypts -or $script:Completions -ne $completions) { throw 'Repeated GPG/password workflow' }
    if ((Get-FileHash -LiteralPath $store).Hash -cne $storeHash -or (Get-FileHash -LiteralPath $backup).Hash.ToLowerInvariant() -cne $backupHash) { throw 'Original keys changed' }
    if (@(Get-ChildItem -LiteralPath (Split-Path $target)).Count -ne 1) { throw 'Duplicate copies created' }
} finally { if ($script:SyntheticMemory) { [Array]::Clear($script:SyntheticMemory,0,$script:SyntheticMemory.Length) } }
""",
    )
