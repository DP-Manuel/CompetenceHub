"""Private entry contract tested with synthetic files only; no USB/key/GPG/SSH."""

from pathlib import Path

import pytest

from test_staging_admin_window_contract import powershell, run_private, SCRIPT as WINDOW

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/resume-staging-admin-window.ps1"


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
if ($output -cne 'STAGING_RESUME=NOT_EXECUTED EXISTING_KEYS_ONLY=YES REAL_COACH_APPLY=DISABLED') { throw 'Unsafe default' }
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


def test_resume_order_and_scope_are_explicit():
    source = SCRIPT.read_text(encoding="ascii")
    body = source.split("function Invoke-ExistingStagingResume", 1)[1]
    stages = [
        "Assert-WindowSource $Commit",
        "Assert-ResumeUsb",
        "Assert-WindowNoPriorAttempt",
        "EXISTING_KEY_PAIR_REQUIRED_NO_INITIALIZATION",
        "typing VERIFY",
        "Complete-StagingOperatorConfig",
        "Use-StagingOperatorEnvironment",
        "Copy-ResumeEncryptedKeyBackup",
        "Invoke-StagingAdminWindow -Commit",
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
    ):
        assert forbidden not in source
    assert "[IO.FileMode]::CreateNew" in source
    assert source.count("Get-Content") == 1
    assert "Get-Content -Raw -LiteralPath $metadata" in source
    assert "-ExpectedSha256 $verified.backup_sha256" in source
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
