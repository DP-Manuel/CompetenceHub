#requires -Version 7.2
<#
Private human-only resume. No key initialization/rotation. No execution by default.
Real key data stay in the local operator process; never transcript/debug/record.
#>
[CmdletBinding()]
param([switch]$Execute, [string]$ExpectedSourceCommit)

function Assert-ResumeUsb {
    param([string]$Path = 'D:\CompetenceHub')
    if ([IO.Path]::GetFullPath($Path).TrimEnd('\') -cne 'D:\CompetenceHub') { throw 'APPROVED_USB_DIRECTORY_REQUIRED' }
    if (-not [IO.Directory]::Exists($Path)) { throw 'UNLOCKED_USB_DIRECTORY_REQUIRED' }
    $cursor = $Path
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'USB_REPARSE_PATH_REJECTED' }
        }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
}

function Copy-ResumeEncryptedKeyBackup {
    param([string]$StorageDirectory, [string]$UsbDirectory = 'D:\CompetenceHub',
          [Parameter(Mandatory)][ValidatePattern('^[a-f0-9]{64}$')][string]$ExpectedSha256)
    Assert-ResumeUsb -Path $UsbDirectory
    $source = Join-Path $StorageDirectory 'staging-operator.keys.json.gpg'
    Assert-StagingPrivateAcl $source
    $hash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -cne $ExpectedSha256) { throw 'VERIFIED_KEY_BACKUP_BINDING_CHANGED' }
    $directory = Join-Path $UsbDirectory 'staging-operator-key-backups'
    if (Test-Path -LiteralPath $directory) {
        if (-not [IO.Directory]::Exists($directory) -or (Get-Item -LiteralPath $directory -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'USB_REPARSE_PATH_REJECTED' }
    } else { $null = New-Item -ItemType Directory -Path $directory }
    $target = Join-Path $directory ($hash + '.keys.json.gpg')
    if (Test-Path -LiteralPath $target) {
        if ((Get-Item -LiteralPath $target -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'USB_REPARSE_PATH_REJECTED' }
    } else {
        $inputStream = [IO.File]::OpenRead($source)
        $outputStream = $null
        try {
            $outputStream = [IO.File]::Open($target,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
            $inputStream.CopyTo($outputStream); $outputStream.Flush($true)
        } finally { if ($outputStream) { $outputStream.Dispose() }; $inputStream.Dispose() }
    }
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -cne $hash -or
        (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedSha256) { throw 'USB_ENCRYPTED_COPY_HASH_MISMATCH_NO_OVERWRITE' }
    Write-Host 'KEY_BACKUP_USB=PASS ENCRYPTED_ONLY=PASS EXISTING_KEYS_PRESERVED=PASS'
}

function Invoke-ExistingStagingResume {
    param([string]$Commit)
    $ErrorActionPreference = 'Stop'
    $script:ResumePhase = 'preflight'
    Set-StrictMode -Version Latest
    if (-not $IsWindows) { throw 'WINDOWS_OPERATOR_REQUIRED' }
    . (Join-Path $PSScriptRoot 'run-staging-admin-window.ps1')
    Assert-WindowNoDiagnostics
    if (@(Get-ChildItem Env: | Where-Object { $_.Name -like 'COMPETENCE_HUB_*' -or $_.Name -like 'DOCKER_*' }).Count) { throw 'CLEAN_OPERATOR_PROCESS_REQUIRED' }
    $git = (Get-Command git.exe -CommandType Application -ErrorAction Stop).Source
    Assert-WindowSource $Commit $git
    Assert-ResumeUsb
    $base = Join-Path $env:LOCALAPPDATA 'CompetenceHub'
    $custody = Join-Path $base 'staging-operator'
    $initializer = Join-Path $script:WindowRoot 'deploy/scripts/initialize-staging-operator-config.ps1'
    . $initializer
    Assert-StagingPrivateAcl $custody -Directory
    Assert-WindowNoPriorAttempt (Join-Path $custody 'bootstrap-attempt.json')
    foreach ($name in @('staging-operator.keys.clixml','staging-operator.keys.json.gpg')) {
        $path = Join-Path $custody $name
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw 'EXISTING_KEY_PAIR_REQUIRED_NO_INITIALIZATION' }
        Assert-StagingPrivateAcl $path
    }
    Write-Host 'PRIVATE WINDOW: no transcript, recording, shared screen or pasted secrets in chat.'
    Write-Host 'LOCAL PLAN: verify existing DPAPI/GPG pair only; add verification metadata only if absent; copy existing encrypted key backup to D:\CompetenceHub.'
    Write-Host 'No key replacement/rotation. No server or account action in this first block.'
    if ((Read-Host 'Confirm private window and ONLY existing-key verification/copy by typing VERIFY') -cne 'VERIFY') { throw 'OPERATION_BLOCK_NOT_APPROVED' }
    $script:ResumePhase = 'key_verification'
    $metadata = Join-Path $custody 'staging-operator.metadata.json'
    if (-not (Test-Path -LiteralPath $metadata)) {
        $null = Complete-StagingOperatorConfig -StorageDirectory $custody `
            -FingerprintPath (Join-Path $base 'staging-operator-corpus-20261030/compromised-password-fingerprints.sha256') `
            -ExpectedCorpusSha256 $script:WindowCorpusHash -AllowedOrigin 'https://127.0.0.1:443' `
            -GpgHome (Join-Path $base 'backup-gnupg') -GpgExecutable 'C:\Program Files\GnuPG\bin\gpg.exe' `
            -AcknowledgeProtectedStorage -AcknowledgeOperatorCustody
    }
    Use-StagingOperatorEnvironment -StorageDirectory $custody -AcknowledgeOperatorCustody -Action { }
    $script:ResumePhase = 'encrypted_usb_copy'
    # Non-secret verification metadata only; never read either keyfile here.
    $verified = Get-Content -Raw -LiteralPath $metadata | ConvertFrom-Json -AsHashtable
    Copy-ResumeEncryptedKeyBackup -StorageDirectory $custody -ExpectedSha256 $verified.backup_sha256
    Write-Host 'CUSTODY=PASS. Following BACKUP and ADMIN blocks each require their own explicit terminal confirmation.'
    $script:ResumePhase = 'protected_window'
    $result = Invoke-StagingAdminWindow -Commit $Commit -PrivateWindow -QuietDatabase -OperatorCustody
    return $result
}

if ($MyInvocation.InvocationName -ne '.') {
    if (-not $Execute) {
        Write-Output 'STAGING_RESUME=NOT_EXECUTED EXISTING_KEYS_ONLY=YES REAL_COACH_APPLY=DISABLED'
    } else {
        try { Invoke-ExistingStagingResume -Commit $ExpectedSourceCommit }
        catch {
            $phase = if ($script:ResumePhase -cin @('preflight','key_verification','encrypted_usb_copy','protected_window')) { $script:ResumePhase } else { 'unknown' }
            [Console]::Error.WriteLine("STAGING_RESUME=STOP PHASE=$phase PRIVATE_MANUAL_REVIEW_REQUIRED EXISTING_KEYS_PRESERVED REAL_COACH_APPLY=DISABLED")
            exit 1
        }
    }
}
