#requires -Version 7.2
<#
Preparation only. The public entry never generates a key. Future execution of
the candidate function requires a separate scoped approval and pinned source.
No real application keys, DB, server, old key home or automatic retries.
#>
[CmdletBinding()]
param()

. (Join-Path $PSScriptRoot 'run-local-backup-key-block.ps1')

function Get-BackupKeyLifecyclePaths {
    $root=Join-Path $env:LOCALAPPDATA 'CompetenceHub/backup-key-rebase-20261105-r2'
    return @{
        root=$root; live=(Join-Path $root 'live-gnupg'); recovered=(Join-Path $root 'recovered-gnupg')
        usb='D:\CompetenceHub'; uid='Competence Hub Staging Backup Recovery 2026-11-05 R2'
        gpg='C:\Program Files\GnuPG\bin\gpg.exe'; gpgconf='C:\Program Files\GnuPG\bin\gpgconf.exe'
        pinentry='C:\Program Files\Gpg4win\bin\pinentry.exe'
    }
}

function Stop-BackupKeyLifecycleAgent {
    param([Collections.IDictionary]$Paths,[string]$KeyHome)
    if ($KeyHome -cnotin @($Paths.live,$Paths.recovered)) { throw 'KEY_LIFECYCLE_AGENT_NOT_OWNED' }
    # Reuse the bounded process wrapper, not a process-name/global agent kill.
    Stop-OwnedRecoveryAgent @{recovered=$KeyHome;gpgconf=$Paths.gpgconf}
}

function New-BackupKeyLifecycleCandidate {
    param([string]$ExpectedSourceCommit,
          [ValidateSet('PasswordManager','ProtectedOffline')][Parameter(Mandatory)][string]$PassphraseCustody,
          [switch]$AcknowledgeNewKeyGeneration)
    $ErrorActionPreference='Stop'; Set-StrictMode -Version Latest
    $script:KeyLifecyclePhase='preflight'
    if (-not $AcknowledgeNewKeyGeneration) { throw 'SEPARATE_NEW_KEY_APPROVAL_REQUIRED' }
    Assert-LocalKeyEnvironment
    Assert-LocalKeySource $ExpectedSourceCommit
    $paths=Get-BackupKeyLifecyclePaths
    $null=Assert-StagingExternalPath $paths.root
    if (Test-Path -LiteralPath $paths.root) { throw 'KEY_LIFECYCLE_EXISTS_NO_REGENERATION' }
    if ($paths.live -cne (Join-Path $paths.root 'live-gnupg') -or
        $paths.recovered -cne (Join-Path $paths.root 'recovered-gnupg') -or
        $paths.uid -cne 'Competence Hub Staging Backup Recovery 2026-11-05 R2') { throw 'KEY_LIFECYCLE_PATH_BINDING_REQUIRED' }
    foreach ($tool in @($paths.gpg,$paths.gpgconf,$paths.pinentry)) {
        $null=Assert-StagingExternalPath (Get-Command $tool -CommandType Application -ErrorAction Stop).Source
    }
    Assert-LocalKeyVolumes $paths.root $paths.usb
    New-StagingPrivateDirectory $paths.root
    New-StagingPrivateDirectory $paths.live
    $policy=@('enforce-passphrase-constraints','min-passphrase-len 20','min-passphrase-nonalpha 1',
        'default-cache-ttl 300','max-cache-ttl 900','no-allow-external-cache',('pinentry-program "'+$paths.pinentry.Replace('\','/')+'"'))
    Write-KeyBlockFile (Join-Path $paths.live 'gpg-agent.conf') ([Text.Encoding]::UTF8.GetBytes(($policy -join [char]10)+[char]10)) -PrivateFile
    $fingerprint=$null; $probe=$null; $plain=$null; $cipher=$null; $output=$null; $agentsStopped=$false
    try {
        Write-Host 'Neue Identitaet ist NUR ein Kandidat. Passphrase im GPG-Dialog festlegen und separat geschuetzt verwahren.'
        $script:KeyLifecyclePhase='generation'
        $null=Invoke-LocalKeyGpg $paths $paths.live Generate
        $fingerprint=Get-LocalBackupFingerprint (Invoke-LocalKeyGpg $paths $paths.live Metadata) $paths.uid
        Write-KeyBlockReceipt (Join-Path $paths.root 'identity.json') @{schema=1;fingerprint=$fingerprint;uid=$paths.uid;status='CANDIDATE_NOT_ACCEPTED'}
        Confirm-KeyBlockCustody $paths.root $fingerprint $PassphraseCustody
        # Generation-cache success is not an independent unlock proof.
        Stop-BackupKeyLifecycleAgent $paths $paths.live
        $script:KeyLifecyclePhase='cold_export'
        Write-Host 'Sofortige Exportprobe OHNE Erzeugungs-Cache: dieselbe notierte Passphrase im GPG-Dialog eingeben.'
        $probe=Invoke-LocalKeyGpg $paths $paths.live SecretExport $fingerprint
        Assert-ProtectedSecretExport (Invoke-LocalKeyGpg -Paths $paths -KeyHome $paths.live -Operation Packets -InputBytes $probe)
        $export=Join-Path $paths.root 'backup-private-key.gpg'
        Write-KeyBlockFile $export $probe -PrivateFile
        $hash=(Get-FileHash -LiteralPath $export -Algorithm SHA256).Hash
        $usb=Join-Path $paths.usb ('backup-key-rebase-20261105-r2-'+$fingerprint)
        if (Test-Path -LiteralPath $usb) { throw 'KEY_LIFECYCLE_USB_EXISTS_NO_OVERWRITE' }
        $null=New-Item -ItemType Directory -Path $usb
        $usbExport=Join-Path $usb 'backup-private-key.gpg'
        Copy-KeyBlockCiphertext $export $usbExport $hash
        New-StagingPrivateDirectory $paths.recovered
        $script:KeyLifecyclePhase='isolated_import'
        Write-KeyBlockFile (Join-Path $paths.recovered 'gpg-agent.conf') ([Text.Encoding]::UTF8.GetBytes(($policy -join [char]10)+[char]10)) -PrivateFile
        $null=Invoke-LocalKeyGpg $paths $paths.recovered Import $fingerprint $usbExport
        if ((Get-LocalBackupFingerprint (Invoke-LocalKeyGpg $paths $paths.recovered Metadata) $paths.uid) -cne $fingerprint) { throw 'KEY_LIFECYCLE_RECOVERY_IDENTITY_MISMATCH' }
        # Prove the recovered key, not a cache warmed by its import dialog.
        Stop-BackupKeyLifecycleAgent $paths $paths.recovered
        $plain=[Text.Encoding]::UTF8.GetBytes('Competence Hub non-secret independent key recovery probe v1: '+$fingerprint)
        $cipher=[IO.MemoryStream]::new()
        Invoke-StagingGpg -Executable $paths.gpg -KeyHome $paths.live -Mode Encrypt -Recipient $fingerprint -InputBytes $plain -OutputStream $cipher
        $cipherPath=Join-Path $paths.root 'key-recovery-probe.gpg'
        Write-KeyBlockFile $cipherPath $cipher.ToArray() -PrivateFile
        $output=[IO.MemoryStream]::new()
        $script:KeyLifecyclePhase='cold_decrypt'
        Write-Host 'Isolierte Recovery-Probe OHNE Import-Cache: notierte Passphrase im GPG-Dialog eingeben.'
        Invoke-StagingGpg -Executable $paths.gpg -KeyHome $paths.recovered -Mode Decrypt -Recipient $fingerprint -EncryptedPath $cipherPath -OutputStream $output
        $restored=$output.ToArray()
        try {
            if (-not [Security.Cryptography.CryptographicOperations]::FixedTimeEquals($plain,$restored)) { throw 'KEY_LIFECYCLE_PROBE_MISMATCH' }
        } finally { [Array]::Clear($restored,0,$restored.Length) }
        if ((Get-FileHash -LiteralPath $export -Algorithm SHA256).Hash -cne $hash -or
            (Get-FileHash -LiteralPath $usbExport -Algorithm SHA256).Hash -cne $hash) { throw 'KEY_LIFECYCLE_EXPORT_CHANGED' }
        Assert-LocalKeyVolumes $paths.root $paths.usb
        foreach ($keyHome in @($paths.live,$paths.recovered)) { Stop-BackupKeyLifecycleAgent $paths $keyHome }
        $agentsStopped=$true
        Write-KeyBlockReceipt (Join-Path $paths.root 'key-lifecycle-proof.json') @{
            schema=1;status='PASS';uid=$paths.uid;fingerprint=$fingerprint;private_export_sha256=$hash
            probe_sha256=(Get-FileHash -LiteralPath $cipherPath -Algorithm SHA256).Hash
            recovery='COLD_EXPORT_EXACT_USB_IMPORT_COLD_DECRYPT';second_recovery='OPEN'
            application_keys='NOT_ACCESSED';database_backup='NOT_EXECUTED';server_actions='NONE'
        }
        $script:KeyLifecyclePhase='complete'
        return [pscustomobject]@{status='PASS';fingerprint=$fingerprint;second_recovery='OPEN';application_keys='NOT_ACCESSED';server_actions='NONE'}
    } finally {
        if ($probe) { [Array]::Clear($probe,0,$probe.Length) }
        if ($plain) { [Array]::Clear($plain,0,$plain.Length) }
        foreach ($stream in @($cipher,$output)) { if ($stream) { [Array]::Clear($stream.GetBuffer(),0,[int]$stream.Length); $stream.Dispose() } }
        foreach ($keyHome in @($paths.live,$paths.recovered)) {
            if (-not $agentsStopped -and [IO.Directory]::Exists($keyHome)) { Stop-BackupKeyLifecycleAgent $paths $keyHome }
        }
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    Write-Output 'GPG_LIFECYCLE=PREPARATION_ONLY NEW_REAL_KEY=NOT_AUTHORIZED SERVER_ACTIONS=NONE'
}
