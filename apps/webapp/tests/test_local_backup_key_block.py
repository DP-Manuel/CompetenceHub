"""Local operator orchestration: actual synthetic DPAPI, no real key/home/USB."""

import subprocess

import pytest

from test_staging_operator_custody import ROOT, STUBBED_FLOW, powershell, run_private

SCRIPT = ROOT / "deploy/scripts/run-local-backup-key-block.ps1"
FP = "1234567890ABCDEF1234567890ABCDEF12345678"


FLOW = STUBBED_FLOW + r"""
$script:CorruptDecrypt=$true
try { $null=Initialize-StagingOperatorConfig @inputs } catch { }
$source=$directory
$originalHashes=@{}
foreach ($file in (Get-ChildItem -LiteralPath $source -File)) { $originalHashes[$file.Name]=(Get-FileHash -LiteralPath $file.FullName).Hash }
. (Join-Path $script:OperatorRepositoryRoot 'deploy/scripts/run-local-backup-key-block.ps1')
$script:BlockPaths=@{
    root=(Join-Path $env:CUSTODY_TEST_ROOT 'block'); source=$source
    live=(Join-Path $env:CUSTODY_TEST_ROOT 'block/live')
    recovered=(Join-Path $env:CUSTODY_TEST_ROOT 'block/recovered')
    candidate=(Join-Path $env:CUSTODY_TEST_ROOT 'block/candidate')
    usb=(Join-Path $env:CUSTODY_TEST_ROOT 'usb'); corpus=$corpus
    gpg=[Environment]::ProcessPath; gpgconf=[Environment]::ProcessPath
}
New-StagingPrivateDirectory $script:BlockPaths.usb
function Get-LocalBackupBlockPaths { return $script:BlockPaths }
function Assert-LocalKeyEnvironment { }
function Assert-LocalKeySource { param($Commit); if ($Commit -cne ('ab'*20)) { throw 'Bad synthetic source' } }
function Assert-LocalKeyVolumes { param($LocalDirectory,$UsbDirectory); if ($case -ceq 'volume') { throw 'Synthetic unverified volume' } }
function Assert-StagingCorpus { param($Path,$ExpectedSha256); return $Path }
$script:GenerationCount=0; $script:Imports=0; $script:ManagerPrompts=0; $script:Decrypts=0
function Stop-OwnedRecoveryAgent { param($Paths) }
function Read-Host {
    param($Prompt)
    $script:ManagerPrompts++
    if ($case -ceq 'manager') { return 'nein' }
    return ' JA '
}
function Invoke-LocalKeyGpg {
    param($Paths,$KeyHome,$Operation,$Fingerprint,$File,$InputBytes)
    if ($KeyHome -cnotin @($Paths.live,$Paths.recovered)) { throw 'Foreign key profile' }
    if ($Operation -ceq 'Generate') {
        $script:GenerationCount++
        if ($script:GenerationCount -ne 1) { throw 'Regeneration forbidden' }
        if ($case -ceq 'partial-generation') { throw 'Synthetic partial key generation' }
        [IO.File]::WriteAllText((Join-Path $KeyHome 'synthetic-key.marker'),'SYNTHETIC')
        return ,[byte[]]@()
    }
    if ($Operation -ceq 'Metadata') {
        if (-not (Test-Path -LiteralPath (Join-Path $KeyHome 'synthetic-key.marker'))) { throw 'No synthetic key' }
        $sec=@('sec','u','4096','1','ABCDEF','1','9999999999','','','','','ecEC','','','+')
        $text=($sec -join ':')+[char]10+'fpr:::::::::1234567890ABCDEF1234567890ABCDEF12345678:'+ [char]10+'uid:::::::::Competence Hub Staging Backup 2026-11:'+ [char]10
        return ,[Text.Encoding]::ASCII.GetBytes($text)
    }
    if ($Operation -ceq 'SecretExport') { return ,[Text.Encoding]::ASCII.GetBytes('FAKE-PROTECTED-EXPORT') }
    if ($Operation -ceq 'Packets') {
        $protected=if ($case -ceq 'unprotected') {'[1024 bits]'} else {'[v4 protected]'}
        return ,[Text.Encoding]::ASCII.GetBytes((':secret key packet:'+[char]10+' iter+salt S2K, algo: 9, hash: 2'+[char]10+' skey[2]: '+$protected+[char]10))
    }
    if ($Operation -ceq 'Import') {
        $script:Imports++
        if (-not $File.StartsWith($Paths.usb+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Import not from exact USB copy' }
        if ($case -ceq 'import-cancel') { throw 'Synthetic private dialog cancel' }
        [IO.File]::WriteAllText((Join-Path $KeyHome 'synthetic-key.marker'),'SYNTHETIC')
        return ,[byte[]]@()
    }
    throw 'Unexpected GPG action'
}
function Invoke-StagingGpg {
    param($Executable,$KeyHome,$Mode,$InputBytes,$EncryptedPath,$OutputStream,$Recipient)
    if ($Recipient -cne '1234567890ABCDEF1234567890ABCDEF12345678') { throw 'August recipient forbidden' }
    if ($Mode -ceq 'Encrypt') {
        $script:PortableMemory=$InputBytes.Clone()
        $cipher=[Text.Encoding]::ASCII.GetBytes('NEW-APPLICATION-CIPHERTEXT')
        $OutputStream.Write($cipher,0,$cipher.Length)
    } else {
        $script:Decrypts++
        if ($KeyHome -cne $script:BlockPaths.recovered) { throw 'Recovery not isolated' }
        if ($case -ceq 'decrypt-cancel') { throw 'Synthetic decrypt cancel' }
        $OutputStream.Write($script:PortableMemory,0,$script:PortableMemory.Length)
    }
}
"""


@pytest.mark.parametrize("mode", [
    "success", "manager", "volume", "unprotected", "partial-generation",
    "import-cancel", "decrypt-cancel", "copy-resume", "hash-conflict",
])
def test_local_block_is_bounded_resumable_and_preserves_realistic_dpapi(
    powershell, tmp_path, mode
):
    run_private(
        powershell, tmp_path,
        "\n$case='" + mode + "'\n" + FLOW + r"""
$script:PortableMemory=$null
$script:OriginalCopy=$null
if ($case -ceq 'copy-resume') {
    $script:OriginalCopy=(Get-Item Function:Copy-KeyBlockCiphertext).ScriptBlock
    function Copy-KeyBlockCiphertext {
        param($Source,$Target,$ExpectedHash)
        if ($Target.EndsWith('application-keys.json.gpg')) { throw 'Synthetic USB write failure' }
        & $script:OriginalCopy $Source $Target $ExpectedHash
    }
}
$result=$null; $failed=$false
try { $result=Invoke-LocalBackupKeyBlock ('ab'*20) 6>$null } catch { $failed=$true }
if ($case -cin @('success','hash-conflict')) {
    if ($failed -or $result.status -cne 'PASS' -or $result.dpapi -cne 'UNCHANGED' -or
        $result.second_recovery -cne 'OPEN' -or $result.server_actions -cne 'NONE') { throw 'Missing bounded success' }
    if ($script:GenerationCount -ne 1 -or $script:ManagerPrompts -ne 1 -or $script:Imports -ne 1 -or $script:Decrypts -ne 1) { throw 'Unexpected dialog/crypto attempts' }
    if ($case -ceq 'hash-conflict') {
        $target=Join-Path $script:BlockPaths.usb 'backup-key-rebase-20261104-1234567890ABCDEF1234567890ABCDEF12345678/backup-private-key.gpg'
        [IO.File]::AppendAllText($target,'synthetic-corruption')
        $hash=(Get-FileHash -LiteralPath $target).Hash
        $rejected=$false
        try { $null=Invoke-LocalBackupKeyBlock ('ab'*20) 6>$null } catch { $rejected=$true }
        if (-not $rejected -or (Get-FileHash -LiteralPath $target).Hash -cne $hash) { throw 'Conflict overwritten' }
    } else {
        $again=Invoke-LocalBackupKeyBlock ('ab'*20) 6>$null
        if ($again.status -cne 'PASS' -or $script:GenerationCount -ne 1 -or $script:ManagerPrompts -ne 1 -or $script:Imports -ne 1 -or $script:Decrypts -ne 1) { throw 'Completed resume repeated secret prompts' }
    }
} else {
    if (-not $failed -or (Test-Path -LiteralPath (Join-Path $script:BlockPaths.root 'completion.json'))) { throw 'Failure claimed PASS' }
    if ($case -ceq 'volume' -and (Test-Path -LiteralPath $script:BlockPaths.root)) { throw 'Failed volume check created key files' }
    if ($case -ceq 'unprotected' -and (Test-Path -LiteralPath (Join-Path $script:BlockPaths.root 'backup-private-key.gpg'))) { throw 'Unprotected export written to disk' }
    if ($case -ceq 'partial-generation') {
        $rejected=$false
        try { $null=Invoke-LocalBackupKeyBlock ('ab'*20) 6>$null } catch { $rejected=$true }
        if (-not $rejected -or $script:GenerationCount -ne 1) { throw 'Partial generation blindly regenerated' }
    } elseif ($case -cin @('manager','import-cancel','decrypt-cancel','copy-resume')) {
        if ($case -ceq 'copy-resume') { Set-Item Function:Copy-KeyBlockCiphertext $script:OriginalCopy }
        $case='success'
        $recovered=Invoke-LocalBackupKeyBlock ('ab'*20) 6>$null
        if ($recovered.status -cne 'PASS' -or $script:GenerationCount -ne 1) { throw 'Manual resume failed/regenerated keys' }
        if ($script:OriginalCopy -and $script:Decrypts -ne 1) { throw 'Copy resume repeated recovered-key unlock' }
    }
}
foreach ($name in $originalHashes.Keys) {
    if ((Get-FileHash -LiteralPath (Join-Path $script:BlockPaths.source $name)).Hash -cne $originalHashes[$name]) { throw 'Original custody changed' }
}
if ($script:PortableMemory) { [Array]::Clear($script:PortableMemory,0,$script:PortableMemory.Length) }
if ($script:SyntheticMemory) { [Array]::Clear($script:SyntheticMemory,0,$script:SyntheticMemory.Length) }
""",
    )


@pytest.mark.parametrize("execute", [False, True])
def test_entrypoint_preserves_cli_intent_before_dot_sourced_parameters(powershell, execute):
    args = [powershell, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)]
    if execute:
        args += ["-Execute", "-ExpectedSourceCommit", "invalid-source"]
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    assert result.returncode == (1 if execute else 0)
    output = result.stdout + result.stderr
    assert ("LOCAL_BACKUP_KEYS=STOP" if execute else "LOCAL_BACKUP_KEYS=NOT_EXECUTED") in output
    assert "SERVER_ACTIONS=NONE" in output


def test_runner_never_includes_server_admin_or_plaintext_export_commands():
    source = SCRIPT.read_text(encoding="ascii")
    for denied in ("ssh ", "scp ", "sftp ", "Invoke-StagingAdminWindow", "pg_dump",
                   "--passphrase", "loopback", "Export-Clixml", "Remove-Item"):
        assert denied not in source
    assert "Assert-ProtectedSecretExport" in source
    assert source.index("Assert-ProtectedSecretExport (Invoke-LocalKeyGpg -Paths") < source.index("Write-KeyBlockFile $export $bytes")
    assert "enforce-passphrase-constraints" in source


@pytest.mark.parametrize("case", ["none", "plain", "second-plain", "cipher", "format"])
def test_unknown_or_unprotected_secret_packet_is_rejected_before_file_write(
    powershell, tmp_path, case
):
    run_private(
        powershell, tmp_path,
        ". (Join-Path $script:OperatorRepositoryRoot 'deploy/scripts/run-local-backup-key-block.ps1')\n"
        + "$case='" + case + "'\n" + r"""
$good=':secret key packet:'+ [char]10+' iter+salt S2K, algo: 9, hash: 2'+ [char]10+' skey[2]: [v4 protected]'+[char]10
$bad=switch ($case) {
    none {':public key packet:'}
    plain {$good.Replace('[v4 protected]','[2048 bits]')}
    second-plain {$good+':secret sub key packet:'+ [char]10+' skey[2]: [2048 bits]'+[char]10}
    cipher {$good.Replace('algo: 9,','algo: 2,')}
    format {$good.Replace('[v4 protected]','[unknown protected]')}
}
$rejected=$false
try { Assert-ProtectedSecretExport ([Text.Encoding]::ASCII.GetBytes($bad)) } catch { $rejected=$true }
if (-not $rejected) { throw 'Unsafe secret export accepted' }
Assert-ProtectedSecretExport ([Text.Encoding]::ASCII.GetBytes($good))
""",
    )
