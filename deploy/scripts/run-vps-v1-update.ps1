#requires -Version 7.2
<# One existing-pilot update window. No installer, real identities or GPG. #>
[CmdletBinding()]
param([switch]$Execute,[switch]$AcknowledgeQuietPilot,[string]$ExpectedSourceCommit,[string]$ResumeRun)
$ErrorActionPreference='Stop'
$v1Execute=$Execute
$v1Quiet=$AcknowledgeQuietPilot
$v1Source=$ExpectedSourceCommit
$v1Resume=$ResumeRun
. (Join-Path $PSScriptRoot 'run-protected-staging-preflight.ps1')
. (Join-Path $PSScriptRoot 'initialize-staging-operator-config.ps1')

function Invoke-V1UpdateProcess {
    param([string]$Python,[string]$Script,[string]$Commit,[string]$Directory,[string]$Resume='')
    $previousEncoding=[Console]::OutputEncoding
    try {
        [Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
        $arguments=@('--execute','--quiet','--source',$Commit,'--directory',$Directory)
        if ($Resume) {$arguments+=@('--resume',$Resume)}
        & $Python -I -X utf8 $Script @arguments | Out-Host
        if ($LASTEXITCODE -ne 0) {throw 'PRIVATE_PILOT_NOT_ACCEPTED'}
    } finally {[Console]::OutputEncoding=$previousEncoding}
}

function Invoke-ExistingPilotV1Update {
    if (-not $v1Execute) {Write-Host 'VPS_V1_UPDATE=NOT_EXECUTED';return 0}
    if (-not $v1Quiet) {throw 'QUIET_REFERENCE_WINDOW_REQUIRED'}
    if ($v1Resume -and $v1Resume -cne '2b834613c4204c1d98a37cbd43134fa1') {throw 'EXACT_ACCEPTED_RESUME_REQUIRED'}
    $root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
    if ($v1Source -cnotmatch '^[a-f0-9]{40}$') {throw 'EXACT_REVIEWED_COMMIT_REQUIRED'}
    $head=Invoke-PrivateReadCommand 'git' @('-C',$root,'rev-parse','HEAD')
    $dirty=Invoke-PrivateReadCommand 'git' @('-C',$root,'status','--porcelain','--untracked-files=all','--','deploy/scripts','deploy/rehearsal','apps/webapp/scripts','apps/webapp/src')
    if ($head.exit -ne 0 -or $head.output.Trim() -cne $v1Source -or $dirty.exit -ne 0 -or $dirty.output.Trim()) {throw 'SOURCE_CHANGED_NO_SERVER_ACTION'}
    $identity=[Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not [Security.Principal.WindowsPrincipal]::new($identity).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {throw 'SAME_USER_ELEVATED_POWERSHELL_REQUIRED'}
    if ($env:USERPROFILE -ine [IO.Path]::GetFullPath((Join-Path $root '../../../..'))) {throw 'SAME_WINDOWS_PROFILE_REQUIRED'}
    foreach ($name in [Environment]::GetEnvironmentVariables('Process').Keys) {
        if ($name -match '^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON(INSPECT|STARTUP|BREAKPOINT|HOME|USERBASE|PATH|ASYNCIODEBUG)$)') {throw 'CLEAN_PRIVATE_TERMINAL_REQUIRED'}
    }
    $parent=Join-Path $env:LOCALAPPDATA 'CompetenceHub/pilot-updates'
    $null=Assert-StagingExternalPath $parent
    if (Test-Path -LiteralPath $parent) {Assert-StagingPrivateAcl $parent -Directory} else {New-StagingPrivateDirectory $parent}
    $directory=Join-Path $parent ([Guid]::NewGuid().ToString('N'))
    New-StagingPrivateDirectory $directory
    Write-Host 'TARGET: existing competence_hub_staging 0001-0006; preserve all four original synthetic users.'
    if ($v1Resume) {
        Write-Host 'RESUME: verify retained current backup/restore and all original rows; reuse identical installed V1; finalize only.'
        Write-Host 'No new backup, restore, install, synthetic account or repeated native acceptance. Existing protected copies remain unchanged.'
    } else {
        Write-Host 'PLAN: current protected backup + isolated exact restore; V1 runtime; separate synthetic cohort; exact scoped cleanup.'
    }
    Write-Host 'No migration, real identity, mail dispatch, public port, GPG or Website change.'
    Write-Host 'Do not use the existing pilot windows during this operation. Existing tunnel may remain open.'
    Write-Host 'Only VPS sudo may be requested, hidden here. Never enter passwords, MFA or recovery in chat.'
    Invoke-V1UpdateProcess (Join-Path $root 'apps/webapp/.venv/Scripts/python.exe') `
        (Join-Path $root 'apps/webapp/scripts/run_vps_update.py') $v1Source $directory $v1Resume
    return 0
}

if ($MyInvocation.InvocationName -ne '.') {
    try {exit (Invoke-ExistingPilotV1Update)}
    catch {
        $allowed=@('QUIET_REFERENCE_WINDOW_REQUIRED','EXACT_REVIEWED_COMMIT_REQUIRED','SOURCE_CHANGED_NO_SERVER_ACTION',
            'SAME_USER_ELEVATED_POWERSHELL_REQUIRED','SAME_WINDOWS_PROFILE_REQUIRED','CLEAN_PRIVATE_TERMINAL_REQUIRED','PRIVATE_PILOT_NOT_ACCEPTED','EXACT_ACCEPTED_RESUME_REQUIRED')
        $code=if($_.Exception.Message -cin $allowed){$_.Exception.Message}else{'PRIVATE_UPDATE_GATE_FAILED'}
        Write-Host ('VPS_V1_UPDATE=STOP CODE='+$code+' NO_AUTOMATIC_RETRY=TRUE');exit 1
    }
}
