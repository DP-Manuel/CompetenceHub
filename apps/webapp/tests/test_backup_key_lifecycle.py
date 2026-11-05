"""Synthetic-only cold key lifecycle; no real operator key or passphrase access."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest

from test_local_backup_key_block import FLOW
from test_staging_operator_custody import ROOT, powershell, run_private


SCRIPT = ROOT / "deploy/scripts/prepare-backup-key-lifecycle.ps1"
UID = "Competence Hub Staging Backup Recovery 2026-11-05 R2"


def test_public_entry_cannot_generate_a_real_replacement(powershell):
    result = subprocess.run([powershell, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0
    assert result.stdout.strip() == "GPG_LIFECYCLE=PREPARATION_ONLY NEW_REAL_KEY=NOT_AUTHORIZED SERVER_ACTIONS=NONE"


@pytest.mark.parametrize("case", ["success", "export-cancel", "decrypt-cancel", "no-approval"])
def test_cold_lifecycle_gates_no_application_access_and_no_regeneration(powershell, tmp_path, case):
    run_private(powershell, tmp_path,
                ". (Join-Path $script:OperatorRepositoryRoot 'deploy/scripts/prepare-backup-key-lifecycle.ps1')\n"
                + "$case='" + case + "'\n" + FLOW + r"""
$script:BlockPaths.live=Join-Path $script:BlockPaths.root 'live-gnupg'
$script:BlockPaths.recovered=Join-Path $script:BlockPaths.root 'recovered-gnupg'
$script:BlockPaths.uid='Competence Hub Staging Backup Recovery 2026-11-05 R2'
$script:BlockPaths.pinentry=[Environment]::ProcessPath
function Get-BackupKeyLifecyclePaths { return $script:BlockPaths }
$script:ColdStops=[Collections.Generic.List[string]]::new()
function Stop-BackupKeyLifecycleAgent { param($Paths,$KeyHome); $script:ColdStops.Add($KeyHome) }
$script:FakeGpg=(Get-Item Function:Invoke-LocalKeyGpg).ScriptBlock
function Invoke-LocalKeyGpg {
    param($Paths,$KeyHome,$Operation,$Fingerprint,$File,$InputBytes)
    if ($Operation -ceq 'SecretExport' -and -not $script:ColdStops.Contains($Paths.live)) { throw 'Export used generation cache' }
    $value=& $script:FakeGpg @PSBoundParameters
    if ($Operation -ceq 'Metadata') {
        $value=[Text.Encoding]::UTF8.GetBytes([Text.Encoding]::UTF8.GetString($value).Replace('Competence Hub Staging Backup 2026-11',$Paths.uid))
    }
    return ,$value
}
function New-StagingOperatorRebaseCandidate { throw 'Application keys accessed before key gate' }
$approved=$case -cne 'no-approval'
$failed=$false
try { $result=New-BackupKeyLifecycleCandidate -ExpectedSourceCommit ('ab'*20) -PassphraseCustody ProtectedOffline -AcknowledgeNewKeyGeneration:$approved 6>$null } catch { $failed=$true }
$proof=Join-Path $script:BlockPaths.root 'key-lifecycle-proof.json'
if ($case -ceq 'success') {
    if ($failed -or $result.status -cne 'PASS' -or $result.application_keys -cne 'NOT_ACCESSED' -or $result.second_recovery -cne 'OPEN') { throw 'Lifecycle success missing' }
    $record=Read-KeyBlockReceipt $proof
    if ($record.recovery -cne 'COLD_EXPORT_EXACT_USB_IMPORT_COLD_DECRYPT' -or $script:ColdStops.Count -lt 4) { throw 'Independent cold proof missing' }
} elseif (-not $failed -or (Test-Path -LiteralPath $proof)) { throw 'Failed lifecycle accepted' }
if ($script:GenerationCount -ne [int]$approved -or $script:ManagerPrompts -ne 0) { throw 'Unexpected generation/custody prompt' }
if ($case -ceq 'no-approval') {
    if (Test-Path -LiteralPath $script:BlockPaths.root) { throw 'Missing approval wrote artifacts' }
} else {
    $again=$false
    try { $null=New-BackupKeyLifecycleCandidate -ExpectedSourceCommit ('ab'*20) -PassphraseCustody ProtectedOffline -AcknowledgeNewKeyGeneration 6>$null } catch { $again=$true }
    if (-not $again -or $script:GenerationCount -ne 1) { throw 'Existing candidate regenerated' }
}
foreach ($name in $originalHashes.Keys) {
    if ((Get-FileHash -LiteralPath (Join-Path $source $name)).Hash -cne $originalHashes[$name]) { throw 'Existing application keys changed' }
}
""")


def test_incident_fingerprint_stops_before_any_real_metadata_or_unlock(powershell, tmp_path):
    run_private(powershell, tmp_path, r"""
. (Join-Path $script:OperatorRepositoryRoot 'deploy/scripts/run-local-backup-key-block.ps1')
function Assert-LocalKeyEnvironment { }
function Assert-LocalKeySource { param($Commit) }
function Get-LocalBackupBlockPaths { throw 'Held key reached real filesystem/metadata' }
$expected=$false
try { $null=Invoke-LocalBackupKeyBlock -Commit ('ab'*20) -ExistingFingerprint '22C82A2F175DAFB04B019502E92DE7854AF99C1F' -PassphraseCustody ProtectedOffline }
catch { $expected=$_.Exception.Message -ceq 'KEY_EXPORT_ON_HOLD_NO_UNLOCK' }
if (-not $expected) { throw 'Incident key was not held before metadata access' }
""")


PINENTRY_SOURCE = r"""
using System;
using System.IO;
using System.Text;
public static class SyntheticPinentry {
    public static void Main() {
        string events = Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"synthetic-pinentry-events.txt");
        File.AppendAllText(events,"START\n");
        StreamReader input = new StreamReader(Console.OpenStandardInput(),new UTF8Encoding(false));
        StreamWriter output = new StreamWriter(Console.OpenStandardOutput(),new UTF8Encoding(false));
        output.AutoFlush = true;
        output.WriteLine("OK Synthetic test Pinentry only");
        string line;
        while ((line = input.ReadLine()) != null) {
            File.AppendAllText(events,line.Split(' ')[0]+"\n");
            if (line == "GETPIN") {
                byte[] data = File.ReadAllBytes(Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"synthetic-passphrase.txt"));
                StringBuilder encoded = new StringBuilder();
                foreach (byte b in data) {
                    if (b >= 32 && b < 127 && b != 37) encoded.Append((char)b);
                    else encoded.Append('%').Append(b.ToString("X2"));
                }
                output.WriteLine("D " + encoded.ToString());
                Array.Clear(data,0,data.Length);
            } else if (line.StartsWith("GETINFO pid")) {
                output.WriteLine("D " + System.Diagnostics.Process.GetCurrentProcess().Id.ToString());
            }
            output.WriteLine("OK");
            if (line == "BYE") break;
        }
    }
}
"""


@pytest.mark.parametrize("phrase_kind", ["ascii", "unicode-and-spaces"])
def test_native_ask_mode_cold_export_import_decrypt_and_repeated_unlock(
    powershell, tmp_path, phrase_kind
):
    """Real GPG ask-mode, protocol-only Pinentry double, no real GUI/keyboard claim."""
    gpg = Path("C:/Program Files/GnuPG/bin/gpg.exe")
    compiler = shutil.which("powershell.exe")
    if not gpg.is_file() or not compiler:
        pytest.skip("requires Windows GnuPG and native synthetic Pinentry compiler")
    source = tmp_path / "synthetic-pinentry.cs"
    executable = tmp_path / "synthetic-pinentry.exe"
    source.write_text(PINENTRY_SOURCE, encoding="ascii")
    compiled = subprocess.run(
        [compiler, "-NoProfile", "-NonInteractive", "-Command",
         "Add-Type -Path '" + str(source).replace("'", "''") + "' -OutputAssembly '"
         + str(executable).replace("'", "''") + "' -OutputType ConsoleApplication"],
        capture_output=True, timeout=30,
    )
    if compiled.returncode:
        pytest.fail("Synthetic Pinentry compilation failed; diagnostics suppressed", pytrace=False)
    handshake = subprocess.run([str(executable)], input=b"BYE\n", capture_output=True, timeout=10)
    if handshake.returncode or b"OK Synthetic test Pinentry only" not in handshake.stdout:
        pytest.fail("Synthetic Pinentry executable handshake failed", pytrace=False)
    (tmp_path / "synthetic-pinentry-events.txt").unlink()
    phrase = "SYNTHETIC-ONLY-native-ask-cold-recovery-2026!"
    if phrase_kind == "unicode-and-spaces":
        phrase = "  SYNTHETIC-Gr\u00fc\u00dfe-\u00e9-e\u0301-native-ask-2026!  "
    phrase_path = tmp_path / "synthetic-passphrase.txt"
    phrase_path.write_bytes(phrase.encode("utf-8"))
    try:
        run_private(powershell, tmp_path, r"""
. (Join-Path $script:OperatorRepositoryRoot 'deploy/scripts/prepare-backup-key-lifecycle.ps1')
$root=Join-Path $env:CUSTODY_TEST_ROOT 'fresh-lifecycle'
$usb=Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-usb'
New-StagingPrivateDirectory $usb
$script:NativePaths=@{
    root=$root;live=(Join-Path $root 'live-gnupg');recovered=(Join-Path $root 'recovered-gnupg')
    usb=$usb;uid='Competence Hub Staging Backup Recovery 2026-11-05 R2'
    gpg='C:\Program Files\GnuPG\bin\gpg.exe';gpgconf='C:\Program Files\GnuPG\bin\gpgconf.exe'
    pinentry=(Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-pinentry.exe')
}
Add-Type -Namespace SyntheticPaths -Name Native -MemberDefinition '[System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet=System.Runtime.InteropServices.CharSet.Unicode)] public static extern uint GetShortPathName(string path, System.Text.StringBuilder output, uint size);'
$short=[Text.StringBuilder]::new(4096)
if ([SyntheticPaths.Native]::GetShortPathName($script:NativePaths.pinentry,$short,4096) -eq 0) { throw 'Synthetic executable short path unavailable' }
$script:NativePaths.pinentry=$short.ToString()
function Get-BackupKeyLifecyclePaths { return $script:NativePaths }
function Assert-LocalKeySource { param($Commit) }
function Assert-LocalKeyVolumes { param($LocalDirectory,$UsbDirectory) }
function Read-Host { throw 'No redundant custody prompt allowed' }
$script:CheckStage=1
try { $result=New-BackupKeyLifecycleCandidate -ExpectedSourceCommit ('ab'*20) -PassphraseCustody ProtectedOffline -AcknowledgeNewKeyGeneration 6>$null }
catch {
    $script:CheckStage=switch($script:KeyLifecyclePhase) { preflight {10} generation {11} cold_export {12} isolated_import {13} cold_decrypt {14} default {15} }
    if (Get-Variable KeyGpgFailureCode -Scope Script -ErrorAction SilentlyContinue) { $script:CheckStage=1000+$script:KeyGpgFailureCode }
    throw 'Synthetic native lifecycle failed'
}
if ($result.status -cne 'PASS') { throw 'Native lifecycle failed' }
$script:CheckStage=2
for($i=0;$i -lt 2;$i++) {
    Stop-BackupKeyLifecycleAgent $script:NativePaths $script:NativePaths.live
    $bytes=Invoke-LocalKeyGpg $script:NativePaths $script:NativePaths.live SecretExport $result.fingerprint
    try { Assert-ProtectedSecretExport (Invoke-LocalKeyGpg -Paths $script:NativePaths -KeyHome $script:NativePaths.live -Operation Packets -InputBytes $bytes) }
    finally { [Array]::Clear($bytes,0,$bytes.Length) }
}
$script:CheckStage=4
$syntheticPhrasePath=Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-passphrase.txt'
$syntheticOriginal=[IO.File]::ReadAllBytes($syntheticPhrasePath)
$keyFile=Get-ChildItem -LiteralPath (Join-Path $script:NativePaths.live 'private-keys-v1.d') -File | Select-Object -First 1
$keyHash=(Get-FileHash -LiteralPath $keyFile.FullName -Algorithm SHA256).Hash
try {
    [IO.File]::WriteAllText($syntheticPhrasePath,'SYNTHETIC-ONLY-intentionally-wrong-input!')
    Stop-BackupKeyLifecycleAgent $script:NativePaths $script:NativePaths.live
    $rejected=$false
    try { $value=Invoke-LocalKeyGpg $script:NativePaths $script:NativePaths.live SecretExport $result.fingerprint }
    catch { $rejected=$_.Exception.Message -ceq 'KEY_GPG_OPERATION_NOT_COMPLETE' -and $script:KeyGpgFailureCode -eq 11 }
    if (-not $rejected) { throw 'Synthetic bad input did not produce native bad-passphrase status' }
} finally {
    [IO.File]::WriteAllBytes($syntheticPhrasePath,$syntheticOriginal)
    [Array]::Clear($syntheticOriginal,0,$syntheticOriginal.Length)
}
Stop-BackupKeyLifecycleAgent $script:NativePaths $script:NativePaths.live
$bytes=Invoke-LocalKeyGpg $script:NativePaths $script:NativePaths.live SecretExport $result.fingerprint
try { Assert-ProtectedSecretExport (Invoke-LocalKeyGpg -Paths $script:NativePaths -KeyHome $script:NativePaths.live -Operation Packets -InputBytes $bytes) }
finally { [Array]::Clear($bytes,0,$bytes.Length) }
if ((Get-FileHash -LiteralPath $keyFile.FullName -Algorithm SHA256).Hash -cne $keyHash) { throw 'Synthetic bad input changed the key' }
$events=[IO.File]::ReadAllLines((Join-Path $env:CUSTODY_TEST_ROOT 'synthetic-pinentry-events.txt'))
if (@($events|Where-Object {$_ -ceq 'GETPIN'}).Count -lt 5) { throw 'Cold native Pinentry paths not exercised' }
$script:CheckStage=3
$proof=Read-KeyBlockReceipt (Join-Path $root 'key-lifecycle-proof.json')
if ($proof.application_keys -cne 'NOT_ACCESSED' -or $proof.second_recovery -cne 'OPEN') { throw 'Lifecycle scope changed' }
foreach($keyHome in @($script:NativePaths.live,$script:NativePaths.recovered)) { Stop-BackupKeyLifecycleAgent $script:NativePaths $keyHome }
""")
    except BaseException:
        events = tmp_path / "synthetic-pinentry-events.txt"
        commands = events.read_text(encoding="utf-8").splitlines() if events.exists() else ["NOT_STARTED"]
        if all(command.replace("_", "").isupper() for command in commands):
            pytest.fail("Synthetic protocol command sequence only: " + ",".join(commands), pytrace=False)
        raise
    finally:
        # Only paths newly owned by this pytest invocation, never LOCALAPPDATA's real home.
        environment = {key: value for key, value in os.environ.items()
                       if key in ("SystemRoot", "SystemDrive", "WINDIR", "PATH", "TEMP", "TMP", "COMSPEC")}
        environment.update(APPDATA=str(tmp_path), LOCALAPPDATA=str(tmp_path))
        for name in ("live-gnupg", "recovered-gnupg"):
            key_home = tmp_path / "fresh-lifecycle" / name
            if key_home.exists():
                stopped = subprocess.run([str(gpg.with_name("gpgconf.exe")), "--homedir", str(key_home), "--kill", "gpg-agent"],
                                         capture_output=True, env=environment, timeout=20)
                if stopped.returncode:
                    pytest.fail("Owned synthetic agent cleanup failed", pytrace=False)
        for name in ("fresh-lifecycle", "synthetic-usb"):
            owned = tmp_path / name
            if owned.resolve().parent != tmp_path.resolve():
                pytest.fail("Synthetic cleanup escaped owned root", pytrace=False)
            if owned.exists():
                shutil.rmtree(owned)
            assert not owned.exists()
        for owned in (phrase_path, source, executable, tmp_path / "synthetic-pinentry-events.txt"):
            if owned.exists():
                owned.unlink()
            assert not owned.exists()
