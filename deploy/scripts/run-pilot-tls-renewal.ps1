#requires -Version 7.2
[CmdletBinding()]
param([switch]$Execute,[switch]$AcknowledgeQuietPilot,[string]$ExpectedSourceCommit)
$ErrorActionPreference='Stop'
$tlsExecute=$Execute;$tlsQuiet=$AcknowledgeQuietPilot;$tlsSource=$ExpectedSourceCommit
. (Join-Path $PSScriptRoot 'run-protected-staging-preflight.ps1')
. (Join-Path $PSScriptRoot 'initialize-staging-operator-config.ps1')
try {
    if(-not $tlsExecute){Write-Host 'PILOT_TLS=NOT_EXECUTED';exit 0}
    if(-not $tlsQuiet){throw 'QUIET_PILOT_REQUIRED'}
    $root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
    $head=Invoke-PrivateReadCommand 'git' @('-C',$root,'rev-parse','HEAD')
    $dirty=Invoke-PrivateReadCommand 'git' @('-C',$root,'status','--porcelain','--untracked-files=all','--','deploy/scripts','apps/webapp/scripts','apps/webapp/src')
    if($tlsSource -cnotmatch '^[a-f0-9]{40}$' -or $head.exit -ne 0 -or $head.output.Trim() -cne $tlsSource -or $dirty.exit -ne 0 -or $dirty.output.Trim()){throw 'SOURCE_CHANGED'}
    if($env:USERPROFILE -ine [IO.Path]::GetFullPath((Join-Path $root '../../../..'))){throw 'SAME_WINDOWS_PROFILE_REQUIRED'}
    foreach($name in [Environment]::GetEnvironmentVariables('Process').Keys){
        if($name -match '^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON(INSPECT|STARTUP|BREAKPOINT|HOME|USERBASE|PATH|ASYNCIODEBUG)$)'){throw 'CLEAN_PRIVATE_TERMINAL_REQUIRED'}
    }
    $parent=Join-Path $env:LOCALAPPDATA 'CompetenceHub/pilot-tls'
    $null=Assert-StagingExternalPath $parent
    if(Test-Path -LiteralPath $parent){Assert-StagingPrivateAcl $parent -Directory}else{New-StagingPrivateDirectory $parent}
    $directory=Join-Path $parent ([Guid]::NewGuid().ToString('N'));New-StagingPrivateDirectory $directory
    Write-Host 'TLS ONLY: existing private V1.2. Keep other pilot windows quiet.'
    Write-Host 'Only the VPS sudo password may be requested here, hidden. No GPG/USB/DB password.'
    Write-Host 'No recording/transcript. Never send passwords, MFA or recovery values to chat.'
    $old=[Console]::OutputEncoding
    try {
        [Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
        & (Join-Path $root 'apps/webapp/.venv/Scripts/python.exe') -I -X utf8 `
            (Join-Path $root 'apps/webapp/scripts/run_pilot_tls_renewal.py') --execute --quiet --source $tlsSource --directory $directory | Out-Host
        if($LASTEXITCODE -ne 0){throw 'PRIVATE_TLS_NOT_ACCEPTED'}
    }finally{[Console]::OutputEncoding=$old}
}catch{
    $code=if($_.Exception.Message -cmatch '^[A-Z0-9_]+$'){$_.Exception.Message}else{'PRIVATE_TLS_GATE_FAILED'}
    Write-Host ('PILOT_TLS=STOP CODE='+$code+' NO_AUTOMATIC_RETRY=TRUE');exit 1
}
