"""Synthetic DPAPI/transport tests only; never real operator key/custody access."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest

from test_staging_operator_custody import ROOT, STUBBED_FLOW, powershell, run_private
from test_prechange_restore_baseline import baseline, encode, records, restored


SCRIPT = ROOT / "deploy/scripts/prepare-backup-key-rebase.ps1"
NEW = "1234567890ABCDEF1234567890ABCDEF12345678"


@pytest.mark.parametrize(
    "mode",
    ["success", "cancel", "mismatch", "race", "no-ack", "old", "overlap", "existing", "bad-dpapi"],
)
def test_rewrap_preserves_originals_and_stops_without_activation(
    powershell, tmp_path, mode
):
    run_private(
    powershell, tmp_path,
        STUBBED_FLOW + r"""
# Make an unfinished OLD synthetic pair; no valid old GPG/receipt is needed.
$script:CorruptDecrypt=$true
try { $null=Initialize-StagingOperatorConfig @inputs } catch { }
$sourceHashes=@{}
foreach ($file in (Get-ChildItem -LiteralPath $directory -File)) {
    $sourceHashes[$file.Name]=(Get-FileHash -LiteralPath $file.FullName).Hash
}
$rebaseScript=Join-Path $script:OperatorRepositoryRoot 'deploy/scripts/prepare-backup-key-rebase.ps1'
. $rebaseScript
function New-StagingOperatorSecret { throw 'Application key generation forbidden' }
function Export-Clixml { throw 'DPAPI recreation forbidden' }
function Assert-StagingCorpus { param($Path,$ExpectedSha256); return $Path }
$newHome=Join-Path $env:CUSTODY_TEST_ROOT 'new-gpg'
$recoveredHome=Join-Path $env:CUSTODY_TEST_ROOT 'recovered-gpg'
New-StagingPrivateDirectory $newHome
New-StagingPrivateDirectory $recoveredHome
$candidate=Join-Path $env:CUSTODY_TEST_ROOT 'new-custody'
$script:NewMemory=$null
$script:OriginalDirectory=$directory
$calls=[Collections.Generic.List[string]]::new()
function Invoke-StagingGpg {
    param($Executable,$KeyHome,$Mode,$InputBytes,$EncryptedPath,$OutputStream,$Recipient)
    if ($Recipient -cne '1234567890ABCDEF1234567890ABCDEF12345678') { throw 'Wrong new recipient' }
    $calls.Add($Mode)
    if ($Mode -ceq 'Encrypt') {
        if ($KeyHome -cne $newHome) { throw 'Wrong encryption home' }
        $script:NewMemory=$InputBytes.Clone()
        $cipher=[Text.Encoding]::ASCII.GetBytes('NEW-SYNTHETIC-CIPHERTEXT')
        $OutputStream.Write($cipher,0,$cipher.Length)
    } else {
        if ($KeyHome -cne $recoveredHome) { throw 'Live home used instead of recovered new key' }
        if ($case -ceq 'cancel') { throw 'Synthetic pinentry cancelled' }
        if ($case -ceq 'mismatch') { $OutputStream.WriteByte(1) }
        else { $OutputStream.Write($script:NewMemory,0,$script:NewMemory.Length) }
        if ($case -ceq 'race') { [IO.File]::AppendAllText((Join-Path $script:OriginalDirectory 'staging-operator.keys.json.gpg'),'race') }
    }
}
""" + f"\n$case='{mode}'\n" + r"""
$arguments=@{
    SourceStorageDirectory=$directory; DestinationStorageDirectory=$candidate
    NewGpgHome=$newHome; RecoveredGpgHome=$recoveredHome
    NewRecipient='1234567890ABCDEF1234567890ABCDEF12345678'; GpgExecutable=[Environment]::ProcessPath
    FingerprintPath=$corpus; ExpectedCorpusSha256=('a1'*32); AllowedOrigin='https://portal.invalid'
    AcknowledgeProtectedStorage=$true; AcknowledgeRecoveredPrivateKey=$true; AcknowledgePassphraseCustody=$true
}
if ($case -ceq 'no-ack') { $arguments.Remove('AcknowledgePassphraseCustody') }
if ($case -ceq 'old') { $arguments.NewRecipient=$script:OperatorRecipient }
if ($case -ceq 'overlap') { $arguments.RecoveredGpgHome=$newHome }
if ($case -ceq 'existing') { New-StagingPrivateDirectory $candidate }
if ($case -ceq 'bad-dpapi') { function Import-Clixml { throw 'Synthetic inaccessible DPAPI' } }
$failed=$false; $result=$null
try { $result=New-StagingOperatorRebaseCandidate @arguments } catch { $failed=$true }
if ($case -ceq 'success') {
    if ($failed -or $result.status -cne 'LOCAL_REWRAP_PASS' -or $result.application_keys -cne 'UNCHANGED' -or
        $result.activation -cne 'NOT_EXECUTED' -or $result.admin -cne 'NOT_EXECUTED') { throw 'Missing candidate' }
    if (($calls -join ',') -cne 'Encrypt,Decrypt') { throw 'Unexpected GPG attempts' }
    Use-StagingOperatorEnvironment -StorageDirectory $candidate -ExpectedRecipient $arguments.NewRecipient -AcknowledgeOperatorCustody -Action { }
    $blocked=$false
    try { Use-StagingOperatorEnvironment -StorageDirectory $candidate -AcknowledgeOperatorCustody -Action { } } catch { $blocked=$true }
    if (-not $blocked) { throw 'Legacy loader silently accepted new recipient' }
    $blocked=$false
    try { $null=New-StagingOperatorRebaseCandidate @arguments } catch { $blocked=$true }
    if (-not $blocked -or $calls.Count -ne 2) { throw 'Repeated invocation overwrote/retried' }
} else {
    if (-not $failed -or (Test-Path -LiteralPath (Join-Path $candidate 'staging-operator.metadata.json'))) { throw 'Failure published READY' }
    if ($case -cin @('no-ack','old','overlap','existing','bad-dpapi') -and $calls.Count) { throw 'Invalid preflight reached GPG' }
}
foreach ($name in $sourceHashes.Keys) {
    if ($case -ceq 'race' -and $name -ceq 'staging-operator.keys.json.gpg') { continue }
    if ((Get-FileHash -LiteralPath (Join-Path $directory $name)).Hash -cne $sourceHashes[$name]) { throw 'Original changed' }
}
if ($script:NewMemory) { [Array]::Clear($script:NewMemory,0,$script:NewMemory.Length) }
if ($script:SyntheticMemory) { [Array]::Clear($script:SyntheticMemory,0,$script:SyntheticMemory.Length) }
""",
    )


def test_new_recipient_is_pinned_not_inferred_from_untrusted_metadata():
    source = records()
    source[0]["recipient"] = NEW
    data = encode(source)
    with pytest.raises(baseline.ContractError, match="invalid_header_recipient"):
        baseline.validate_metadata(data)
    assert baseline.validate_metadata(data, expected_recipient=NEW)["status"] == "VALID"
    assert baseline.compare(data, encode(restored(source)), expected_recipient=NEW)["status"] == "PASS"
    with pytest.raises(baseline.ContractError, match="invalid_header_recipient"):
        baseline.validate_metadata(encode(records()), expected_recipient=NEW)


@pytest.mark.parametrize("bad", ["", "8CCA3D9186A28D4C", "a"*40, "A"*40, NEW+";true", None])
def test_new_recipient_rejects_missing_short_placeholder_or_injected_inputs(bad):
    with pytest.raises(baseline.ContractError, match="explicit_full_recipient_required"):
        baseline.validate_metadata(encode(records()), expected_recipient=bad)


def test_plan_only_cli_has_no_private_reads_or_generation(powershell, tmp_path):
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "BACKUP_KEY_REBASE=PLAN_ONLY KEY_GENERATION=NOT_EXECUTED SERVER_ACTIONS=NONE REAL_COACH_APPLY=DISABLED"


def test_additive_rebase_never_generates_deletes_or_contacts_server():
    source = SCRIPT.read_text(encoding="ascii")
    body = source.split("function New-StagingOperatorRebaseCandidate", 1)[1].split("if ($MyInvocation", 1)[0]
    for forbidden in ("New-StagingOperatorSecret", "Export-Clixml", "Remove-Item", "--generate", "--import", "--export-secret", "ssh ", "scp ", "Read-Host", "-Force"):
        assert forbidden not in body
    assert "-KeyHome $recoveredHome -Mode Decrypt" in body
    assert "New-StagingPrivateFileStream $newStore" in body
    assert "$inputStream.CopyTo($output)" in body
    assert "New-StagingPrivateFileStream $metadata" in body


def test_actual_synthetic_gpg_export_import_and_existing_dpapi_rewrap(powershell, tmp_path):
    """Real NEW disposable GPG key, not a real key/password/old-profile access."""
    gpg = Path("C:/Program Files/GnuPG/bin/gpg.exe")
    gpgconf = gpg.with_name("gpgconf.exe")
    if not gpg.is_file() or not gpgconf.is_file():
        pytest.skip("requires local GnuPG for an isolated synthetic key")
    run_private(powershell, tmp_path, r"""
foreach ($name in @('new-gpg','recovered-gpg')) {
    New-StagingPrivateDirectory (Join-Path $env:CUSTODY_TEST_ROOT $name)
}
""")
    home, recovery = tmp_path / "new-gpg", tmp_path / "recovered-gpg"
    (home / "gpg-agent.conf").write_text(
        "enforce-passphrase-constraints\nmin-passphrase-len 20\nmin-passphrase-nonalpha 1\n",
        encoding="ascii",
    )
    environment = {
        key: os.environ[key]
        for key in ("SystemRoot", "SystemDrive", "WINDIR", "PATH", "TEMP", "TMP", "COMSPEC")
        if key in os.environ
    }
    environment.update(APPDATA=str(tmp_path), LOCALAPPDATA=str(tmp_path), GNUPGHOME=str(home))
    passphrase = b"SYNTHETIC-ONLY-not-an-operational-password\n"

    def invoke(key_home, args, data=None):
        result = subprocess.run(
            [str(gpg), "--no-options", "--homedir", str(key_home), "--batch",
             "--pinentry-mode", "loopback", *args],
            input=data, capture_output=True, env=environment, timeout=60,
        )
        if result.returncode:
            pytest.fail("Isolated synthetic GPG step failed; all diagnostics suppressed", pytrace=False)
        return result.stdout

    try:
        invoke(home, ["--passphrase-fd", "0", "--quick-generate-key",
                      "Competence Hub Staging Backup 2026-11", "rsa4096", "encr", "1d"], passphrase)
        listing = invoke(home, ["--with-colons", "--fingerprint", "--list-secret-keys"])
        fingerprint = next(line.split(b":")[9].decode("ascii") for line in listing.splitlines() if line.startswith(b"fpr:"))
        archive = invoke(home, ["--passphrase-fd", "0", "--export-secret-keys", fingerprint], passphrase)
        assert archive
        packets = invoke(home, ["--list-packets"], archive)
        assert b"protected" in packets.lower() or b"protect count" in packets.lower()
        # Only this newly generated synthetic key export is written/imported.
        archive_path = tmp_path / "synthetic-private-export.gpg"
        archive_path.write_bytes(archive)
        # Exercise the real bounded runner's GPG packet inspection, never Pinentry.
        run_private(powershell, tmp_path, r"""
. (Join-Path $script:OperatorRepositoryRoot 'deploy/scripts/run-local-backup-key-block.ps1')
$paths=@{
    live=(Join-Path $env:CUSTODY_TEST_ROOT 'new-gpg')
    recovered=(Join-Path $env:CUSTODY_TEST_ROOT 'recovered-gpg')
    gpg='C:\Program Files\GnuPG\bin\gpg.exe'
    gpgconf='C:\Program Files\GnuPG\bin\gpgconf.exe'
}
Stop-OwnedRecoveryAgent $paths
$file=Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-private-export.gpg'
Assert-ProtectedSecretExport (Invoke-LocalKeyGpg $paths $paths.live Packets '' $file)
$fp=Get-LocalBackupFingerprint (Invoke-LocalKeyGpg $paths $paths.live Metadata)
if ($fp -cnotmatch '^[A-F0-9]{40}$') { throw 'Actual dedicated metadata rejected' }
$cipher=[IO.File]::ReadAllBytes($file)
try {
    Assert-ProtectedSecretExport (Invoke-LocalKeyGpg -Paths $paths -KeyHome $paths.live -Operation Packets -InputBytes $cipher)
} finally { [Array]::Clear($cipher,0,$cipher.Length) }
""")
        invoke(recovery, ["--passphrase-fd", "0", "--import", str(archive_path)], passphrase)
        encrypted = invoke(home, ["--trust-model", "always", "--recipient", fingerprint, "--encrypt"], b"synthetic probe")
        cipher_path = tmp_path / "synthetic-probe.gpg"
        cipher_path.write_bytes(encrypted)
        # Warm only the recovered synthetic agent, so the real ask-mode helper
        # needs no UI or password prompt in this automated test.
        recovered = invoke(recovery, ["--passphrase-fd", "0", "--decrypt", str(cipher_path)], passphrase)
        assert recovered == b"synthetic probe"
        run_private(powershell, tmp_path, r"""
$stream=[IO.MemoryStream]::new()
$rejected=$false
try {
    Invoke-StagingGpg -Executable 'C:\Program Files\GnuPG\bin\gpg.exe' -KeyHome (Join-Path $env:CUSTODY_TEST_ROOT 'recovered-gpg') -Mode Decrypt -Recipient $script:OperatorRecipient -EncryptedPath (Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-probe.gpg') -OutputStream $stream
} catch { $rejected=$true }
finally { [Array]::Clear($stream.GetBuffer(),0,[int]$stream.Length); $stream.Dispose() }
if (-not $rejected) { throw 'Actual new-key decrypt was relabelled as August recipient' }
""")
        run_private(powershell, tmp_path, r"""
function Assert-StagingCorpus { param($Path,$ExpectedSha256); return $Path }
$script:CheckStage=10
$source=Join-Path $env:CUSTODY_TEST_ROOT 'original-custody'
New-StagingPrivateDirectory $source
$store=Join-Path $source $script:OperatorStoreName
$secret=New-StagingOperatorSecret
try { $secret | Export-Clixml -LiteralPath $store -NoClobber } finally { $secret.Dispose() }
$original=(Get-FileHash -LiteralPath $store).Hash
$script:CheckStage=11
. (Join-Path $script:OperatorRepositoryRoot 'deploy/scripts/prepare-backup-key-rebase.ps1')
function Assert-StagingCorpus { param($Path,$ExpectedSha256); return $Path }
function New-StagingOperatorSecret { throw 'Must preserve existing application keys' }
function Export-Clixml { throw 'Must copy existing DPAPI bytes' }
$script:CheckStage=12
try {
    $result=New-StagingOperatorRebaseCandidate -SourceStorageDirectory $source -DestinationStorageDirectory (Join-Path $env:CUSTODY_TEST_ROOT 'new-custody') -NewGpgHome (Join-Path $env:CUSTODY_TEST_ROOT 'new-gpg') -RecoveredGpgHome (Join-Path $env:CUSTODY_TEST_ROOT 'recovered-gpg') -NewRecipient '""" + fingerprint + r"""' -GpgExecutable 'C:\Program Files\GnuPG\bin\gpg.exe' -FingerprintPath (Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-corpus.sha256') -ExpectedCorpusSha256 ('a1'*32) -AllowedOrigin 'https://portal.invalid' -AcknowledgeProtectedStorage -AcknowledgeRecoveredPrivateKey -AcknowledgePassphraseCustody
} catch {
    $script:CheckStage=switch ($script:RebasePhase) { preflight {1} dpapi_payload {2} new_encryption {3} recovered_key_comparison {4} candidate_metadata {5} candidate_loader {6} default {7} }
    throw 'Synthetic bounded phase failure'
}
$script:CheckStage=20
if (@($result).Count -ne 1) { $script:CheckStage=21; throw 'Native helper returned extra pipeline objects' }
if ($result.status -cne 'LOCAL_REWRAP_PASS') { $script:CheckStage=22; throw 'Native rewrap status failed' }
if ((Get-FileHash -LiteralPath $store).Hash -cne $original) { $script:CheckStage=23; throw 'Native original changed' }
""")
    finally:
        # Target ONLY the two owned synthetic agents, never the real user home.
        for key_home in (home, recovery):
            result = subprocess.run(
                [str(gpgconf), "--homedir", str(key_home), "--kill", "gpg-agent"],
                capture_output=True, env=environment, timeout=20,
            )
            if result.returncode:
                pytest.fail("Synthetic GPG-agent cleanup failed; diagnostics suppressed", pytrace=False)
        # Remove only the two newly owned synthetic profiles and their export.
        for key_home in (home, recovery):
            if key_home.resolve().parent != tmp_path.resolve():
                pytest.fail("Synthetic cleanup path mismatch", pytrace=False)
            shutil.rmtree(key_home)
            assert not key_home.exists()
        archive_path = tmp_path / "synthetic-private-export.gpg"
        if archive_path.exists():
            archive_path.unlink()
        assert not archive_path.exists()


@pytest.mark.parametrize("bad", ["", "8CCA3D9186A28D4C", "a"*40, "A"*40, NEW+";true", baseline.RECIPIENT])
def test_snapshot_rebase_bad_recipient_stops_before_any_server_action(bad):
    bash = Path("C:/Program Files/Git/bin/bash.exe")
    if not bash.is_file():
        pytest.skip("requires local Git Bash syntax runner")
    script = ROOT / "deploy/scripts/competence-hub-postgres-snapshot"
    result = subprocess.run(
        [str(bash), str(script), "--confirm-staging-snapshot",
         "--run-id", "synthetic-invalid-only", "--rebase-recipient", bad],
        capture_output=True, timeout=20,
    )
    assert result.returncode != 0
    assert not result.stdout
    assert b"recipient" in result.stderr


def test_new_recipient_restore_proof_reaches_existing_admin_gate(tmp_path, monkeypatch):
    import hashlib
    import json
    from test_staging_admin_operator import operator, proof_fixture, NOW

    proof_path, backup, proof = proof_fixture(tmp_path, monkeypatch)
    data = (backup / "METADATA").read_bytes()
    lines = data.splitlines()
    header = json.loads(lines[0])
    header["recipient"] = NEW
    data = b"\n".join([json.dumps(header).encode(), *lines[1:]]) + b"\n"
    (backup / "METADATA").write_bytes(data)
    proof["metadata_sha256"] = hashlib.sha256(data).hexdigest()
    proof_path.write_text(json.dumps(proof), encoding="utf-8")
    with pytest.raises(ValueError):
        operator.verify_restore_proof(proof_path, backup, NOW)
    assert operator.verify_restore_proof(
        proof_path, backup, NOW, expected_recipient=NEW,
    )["status"] == "PASS"


@pytest.mark.parametrize("mode", ["ok", "off", "locked", "fat", "unknown", "small", "temp-off"])
def test_backup_target_needs_current_encryption_not_only_capacity(powershell, tmp_path, mode):
    run_private(powershell, tmp_path, r"""
. (Join-Path $script:OperatorRepositoryRoot 'apps/webapp/scripts/run-staging-admin-window.ps1')
$target=Join-Path $env:CUSTODY_TEST_ROOT 'backup-target'
New-StagingPrivateDirectory $target
$script:ProtectionCalls=0
""" + f"\n$case='{mode}'\n" + r"""
function Get-Volume {
    param($DriveLetter,$ErrorAction)
    return @{FileSystem=$(if ($case -ceq 'fat') {'FAT'} else {'NTFS'})}
}
function Get-BitLockerVolume {
    param($MountPoint,$ErrorAction)
    $script:ProtectionCalls++
    if ($case -ceq 'unknown') { throw 'Synthetic permission denied' }
    return @{
        VolumeStatus='FullyEncrypted'
        ProtectionStatus=$(if ($case -ceq 'off' -or ($case -ceq 'temp-off' -and $script:ProtectionCalls -eq 2)) {'Off'} else {'On'})
        LockStatus=$(if ($case -ceq 'locked') {'Locked'} else {'Unlocked'})
    }
}
$required=$(if ($case -ceq 'small') {1} else {512MB})
$failed=$false
try { $null=Assert-WindowEncryptedBackupTarget $target $required } catch { $failed=$true }
if (($case -ceq 'ok') -eq $failed) { throw 'Encryption/space gate disagrees with contract' }
if ($case -ceq 'ok' -and $script:ProtectionCalls -ne 2) { throw 'Plaintext restore workspace not checked' }
""")


def test_admin_rebase_wrapper_pins_new_recipient_and_separate_restore_approval(powershell, tmp_path):
    run_private(powershell, tmp_path, r"""
. (Join-Path $script:OperatorRepositoryRoot 'apps/webapp/scripts/run-staging-admin-window.ps1')
$new='1234567890ABCDEF1234567890ABCDEF12345678'
$wrapper=Get-WindowRootScript -Recipient $new
if (-not $wrapper.Contains('--rebase-recipient '+$new)) { throw 'New fingerprint not pinned in remote wrapper' }
if ((Get-WindowRootScript).Contains('--rebase-recipient')) { throw 'Legacy snapshot default silently changed' }
$rejected=$false
try { $null=Get-WindowRootScript -Recipient 'invalid;injection' } catch { $rejected=$true }
if (-not $rejected) { throw 'Injected wrapper input accepted' }
function Read-Host { param($Prompt); return 'RESTORE' }
$old=$Host
$null=Confirm-WindowOperation -Block RESTORE 6>$null
""")
