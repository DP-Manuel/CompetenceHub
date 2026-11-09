#requires -Version 7.2
<#
Approved current 0006 Staging rollback copy + isolated restore only.
No deployment, migration, accounts, GPG, keyfile read or existing file overwrite.
#>
[CmdletBinding()]
param([switch]$Execute, [string]$ExpectedSourceCommit)
$ErrorActionPreference = 'Stop'
$entryCommit = $ExpectedSourceCommit
$entryExecute = $Execute
. (Join-Path $PSScriptRoot 'run-protected-staging-preflight.ps1') -ExpectedSourceCommit $entryCommit
. (Join-Path $PSScriptRoot 'initialize-staging-operator-config.ps1')

function Invoke-ProtectedStagingBackup {
    $script:ProtectedBackupPhase = 'preflight'
    $root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
    if (-not $entryExecute) { Write-Host 'PROTECTED_BACKUP=NOT_EXECUTED'; return 0 }
    foreach ($name in [Environment]::GetEnvironmentVariables('Process').Keys) {
        if ($name -match '^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON(INSPECT|STARTUP|BREAKPOINT|HOME|USERBASE|PATH|ASYNCIODEBUG)$)') {
            throw 'CLEAN_PRIVATE_TERMINAL_REQUIRED'
        }
    }
    if ($entryCommit -cnotmatch '^[a-f0-9]{40}$') { throw 'EXACT_REVIEWED_COMMIT_REQUIRED' }
    $head = Invoke-PrivateReadCommand 'git' @('-C', $root, 'rev-parse', 'HEAD')
    $dirty = Invoke-PrivateReadCommand 'git' @('-C', $root, 'status', '--porcelain', '--untracked-files=all', '--', 'deploy/scripts', 'apps/webapp/scripts', 'apps/webapp/src')
    if ($head.exit -ne 0 -or $head.output.Trim() -cne $entryCommit -or $dirty.exit -ne 0 -or $dirty.output.Trim()) { throw 'SOURCE_CHANGED_NO_SERVER_ACTION' }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not [Security.Principal.WindowsPrincipal]::new($identity).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'SAME_USER_ELEVATED_POWERSHELL_REQUIRED' }
    if ($env:USERPROFILE -ine [IO.Path]::GetFullPath((Join-Path $root '../../../..'))) { throw 'SAME_WINDOWS_PROFILE_REQUIRED' }
    $script:ProtectedBackupPhase = 'volume'
    $query = @'
$ErrorActionPreference='Stop'
try {
 $v=Get-BitLockerVolume -MountPoint 'C:'
 @{volume=[string]$v.VolumeStatus;protection=[string]$v.ProtectionStatus;lock=[string]$v.LockStatus;
 free_bytes=[IO.DriveInfo]::new('C:\').AvailableFreeSpace}|ConvertTo-Json -Compress
} catch {exit 1}
'@
    $result = Invoke-PrivateReadCommand "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" @('-NoProfile', '-NonInteractive', '-Command', $query)
    if ($result.exit -ne 0) { throw 'CURRENT_VOLUME_PROOF_UNAVAILABLE' }
    Assert-PreflightVolume ($result.output | ConvertFrom-Json -AsHashtable)
    $script:ProtectedBackupPhase = 'local_storage'
    $destination = Join-Path $env:LOCALAPPDATA 'CompetenceHub/pilot-snapshots'
    if ([IO.Path]::GetPathRoot($destination) -ine 'C:\') { throw 'QUALIFIED_C_VOLUME_REQUIRED' }
    $null = Assert-StagingExternalPath $destination
    if (Test-Path -LiteralPath $destination) { Assert-StagingPrivateAcl $destination -Directory }
    else { New-StagingPrivateDirectory $destination }
    $run = Join-Path $destination ([Guid]::NewGuid().ToString('N'))
    New-StagingPrivateDirectory $run
    Write-Host 'TARGET: competence_hub_staging, current 0001-0006 only; existing data remain unchanged.'
    Write-Host 'PLAN: temporary DPAPI/BitLocker copy; exact reread restored into private probe DB; only probe removed.'
    Write-Host 'No GPG/keyfile access, migration, service change or accounts. Copy remains machine/user-bound.'
    $python = Join-Path $root 'apps/webapp/.venv/Scripts/python.exe'
    $script:ProtectedBackupPhase = 'backup_restore'
    & $python -I -X utf8 (Join-Path $root 'apps/webapp/scripts/protected_staging_backup.py') --execute --source $entryCommit --directory $run
    if ($LASTEXITCODE -ne 0) { throw 'PRIVATE_BACKUP_RESTORE_NOT_COMPLETE' }
    $script:ProtectedBackupPhase = 'local_postflight'
    Assert-StagingPrivateAcl (Join-Path $run 'database.dump.dpapi')
    Assert-StagingPrivateAcl (Join-Path $run 'baseline.json.dpapi')
    Write-Host 'PROTECTED_BACKUP_RESTORE=PASS PILOT=NOT_INSTALLED REAL_ACCOUNTS=NONE GPG=NOT_USED'
    return 0
}

if ($MyInvocation.InvocationName -ne '.') {
    try { exit (Invoke-ProtectedStagingBackup) }
    catch {
        $allowed = @('EXACT_REVIEWED_COMMIT_REQUIRED', 'SOURCE_CHANGED_NO_SERVER_ACTION',
            'SAME_USER_ELEVATED_POWERSHELL_REQUIRED', 'SAME_WINDOWS_PROFILE_REQUIRED',
            'CURRENT_VOLUME_PROOF_UNAVAILABLE', 'LOCAL_ENCRYPTED_TARGET_NOT_VERIFIED',
            'LOCAL_TARGET_CAPACITY_INSUFFICIENT', 'QUALIFIED_C_VOLUME_REQUIRED',
            'CLEAN_PRIVATE_TERMINAL_REQUIRED', 'PRIVATE_BACKUP_RESTORE_NOT_COMPLETE')
        $code = if ($_.Exception.Message -cin $allowed) { $_.Exception.Message } else { 'PRIVATE_STORAGE_OR_OPERATION_NOT_COMPLETE' }
        Write-Host ('PROTECTED_BACKUP=STOP PHASE=' + $script:ProtectedBackupPhase + ' CODE=' + $code)
        Write-Host 'Files retained; no automatic retry or key regeneration. No deployment.'
        exit 1
    }
}
