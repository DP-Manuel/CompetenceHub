#requires -Version 7.2
<# Opens existing synthetic role windows. No sudo, install or credential output. #>
[CmdletBinding()]
param([switch]$Open,[string]$ExpectedSourceCommit)
$ErrorActionPreference='Stop'
$accessOpen=$Open;$accessSource=$ExpectedSourceCommit
. (Join-Path $PSScriptRoot 'run-protected-staging-preflight.ps1')
. (Join-Path $PSScriptRoot 'initialize-staging-operator-config.ps1')

try {
    if (-not $accessOpen) {Write-Host 'PILOT_ACCESS=NOT_OPENED';exit 0}
    $root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
    $head=Invoke-PrivateReadCommand 'git' @('-C',$root,'rev-parse','HEAD')
    $dirty=Invoke-PrivateReadCommand 'git' @('-C',$root,'status','--porcelain','--untracked-files=all','--','deploy/scripts','apps/webapp/scripts','apps/webapp/src')
    if ($accessSource -cnotmatch '^[a-f0-9]{40}$' -or $head.exit -ne 0 -or $head.output.Trim() -cne $accessSource -or $dirty.exit -ne 0 -or $dirty.output.Trim()) {throw 'SOURCE_CHANGED'}
    if ($env:USERPROFILE -ine [IO.Path]::GetFullPath((Join-Path $root '../../../..'))) {throw 'SAME_WINDOWS_PROFILE_REQUIRED'}
    foreach($name in [Environment]::GetEnvironmentVariables('Process').Keys) {
        if ($name -match '^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON(INSPECT|STARTUP|BREAKPOINT|HOME|USERBASE|PATH|ASYNCIODEBUG)$)') {throw 'CLEAN_PRIVATE_TERMINAL_REQUIRED'}
    }
    $parent=Join-Path $env:LOCALAPPDATA 'CompetenceHub/pilot-views'
    $null=Assert-StagingExternalPath $parent
    if(Test-Path -LiteralPath $parent){Assert-StagingPrivateAcl $parent -Directory}else{New-StagingPrivateDirectory $parent}
    $directory=Join-Path $parent ([Guid]::NewGuid().ToString('N'));New-StagingPrivateDirectory $directory
    Write-Host 'Opening existing Admin, Reviewer and two Coach windows. No installation, new accounts or sudo.'
    Write-Host 'Private stored logins stay inside this local process. Do not record/transcript this session.'
    $oldEncoding=[Console]::OutputEncoding
    try {
        [Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
        & (Join-Path $root 'apps/webapp/.venv/Scripts/python.exe') -I -X utf8 (Join-Path $root 'apps/webapp/scripts/open_vps_pilot.py') --open --source $accessSource --directory $directory | Out-Host
        if($LASTEXITCODE -ne 0){throw 'PRIVATE_ACCESS_NOT_OPENED'}
    }finally{[Console]::OutputEncoding=$oldEncoding}
}catch {
    $allowed=@('SOURCE_CHANGED','SAME_WINDOWS_PROFILE_REQUIRED','CLEAN_PRIVATE_TERMINAL_REQUIRED','PRIVATE_ACCESS_NOT_OPENED')
    $code=if($_.Exception.Message -cin $allowed){$_.Exception.Message}else{'PRIVATE_ACCESS_GATE_FAILED'}
    Write-Host ('PILOT_ACCESS=STOP CODE='+$code);exit 1
}
