#requires -Version 7.2
<# Private authorized VPS pilot; existing restore proof reused, no new backup. #>
[CmdletBinding()]
param([switch]$Execute, [string]$ExpectedSourceCommit)
$ErrorActionPreference = 'Stop'
$entryExecute = $Execute
$entryCommit = $ExpectedSourceCommit
. (Join-Path $PSScriptRoot 'run-protected-staging-preflight.ps1') -ExpectedSourceCommit $entryCommit
. (Join-Path $PSScriptRoot 'initialize-staging-operator-config.ps1')

function Invoke-VpsPilotProcess {
    param([string]$Python, [string]$Script, [string]$Commit, [string]$Directory)
    $previousEncoding = [Console]::OutputEncoding
    try {
        # Python -X utf8 emits UTF-8 into this native stdout pipe, not OEM text.
        [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
        & $Python -I -X utf8 $Script --execute --source $Commit --directory $Directory | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'PRIVATE_PILOT_NOT_ACCEPTED' }
    } finally { [Console]::OutputEncoding = $previousEncoding }
}

function Invoke-VpsPilot {
    if (-not $entryExecute) { Write-Host 'VPS_PILOT=NOT_EXECUTED'; return 0 }
    $root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
    if ($entryCommit -cnotmatch '^[a-f0-9]{40}$') { throw 'EXACT_REVIEWED_COMMIT_REQUIRED' }
    $head = Invoke-PrivateReadCommand 'git' @('-C', $root, 'rev-parse', 'HEAD')
    $dirty = Invoke-PrivateReadCommand 'git' @('-C', $root, 'status', '--porcelain', '--untracked-files=all', '--', 'deploy/scripts', 'apps/webapp/scripts', 'apps/webapp/src')
    if ($head.exit -ne 0 -or $head.output.Trim() -cne $entryCommit -or $dirty.exit -ne 0 -or $dirty.output.Trim()) { throw 'SOURCE_CHANGED_NO_SERVER_ACTION' }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not [Security.Principal.WindowsPrincipal]::new($identity).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'SAME_USER_ELEVATED_POWERSHELL_REQUIRED' }
    if ($env:USERPROFILE -ine [IO.Path]::GetFullPath((Join-Path $root '../../../..'))) { throw 'SAME_WINDOWS_PROFILE_REQUIRED' }
    foreach ($name in [Environment]::GetEnvironmentVariables('Process').Keys) {
        if ($name -match '^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON(INSPECT|STARTUP|BREAKPOINT|HOME|USERBASE|PATH|ASYNCIODEBUG)$)') { throw 'CLEAN_PRIVATE_TERMINAL_REQUIRED' }
    }
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
    $destination = Join-Path $env:LOCALAPPDATA 'CompetenceHub/pilot-runs'
    $null = Assert-StagingExternalPath $destination
    if (Test-Path -LiteralPath $destination) { Assert-StagingPrivateAcl $destination -Directory }
    else { New-StagingPrivateDirectory $destination }
    $run = Join-Path $destination ([Guid]::NewGuid().ToString('N'))
    New-StagingPrivateDirectory $run
    Write-Host 'TARGET: competence_hub_staging 0001-0006. No migration, real account, mail or public port.'
    Write-Host 'PLAN: verify accepted restore/current state; install own loopback API/TLS; synthetic browser acceptance and own restart.'
    Write-Host 'Existing application keys remain unchanged. Hidden inputs: PostgreSQL app password and VPS sudo only.'
    Write-Host 'Do not transcript, record or share passwords, MFA or recovery values. Leave this terminal open after PASS.'
    Invoke-VpsPilotProcess (Join-Path $root 'apps/webapp/.venv/Scripts/python.exe') `
        (Join-Path $root 'apps/webapp/scripts/run_vps_pilot.py') $entryCommit $run
    return 0
}

if ($MyInvocation.InvocationName -ne '.') {
    try { exit (Invoke-VpsPilot) }
    catch {
        $allowed = @('EXACT_REVIEWED_COMMIT_REQUIRED','SOURCE_CHANGED_NO_SERVER_ACTION',
            'SAME_USER_ELEVATED_POWERSHELL_REQUIRED','SAME_WINDOWS_PROFILE_REQUIRED',
            'CLEAN_PRIVATE_TERMINAL_REQUIRED','CURRENT_VOLUME_PROOF_UNAVAILABLE',
            'LOCAL_ENCRYPTED_TARGET_NOT_VERIFIED','LOCAL_TARGET_CAPACITY_INSUFFICIENT','PRIVATE_PILOT_NOT_ACCEPTED')
        $code = if ($_.Exception.Message -cin $allowed) { $_.Exception.Message } else { 'PRIVATE_LOCAL_GATE_FAILED' }
        Write-Host ('VPS_PILOT=STOP CODE=' + $code + ' NO_AUTOMATIC_RETRY=TRUE')
        exit 1
    }
}
