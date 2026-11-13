#requires -Version 7.2
[CmdletBinding()]
param([switch]$Execute,[switch]$AcknowledgeQuietPilot,[string]$ExpectedSourceCommit)
& (Join-Path $PSScriptRoot 'run-vps-v1-update.ps1') -ReleaseProfile V11 `
    -Execute:$Execute -AcknowledgeQuietPilot:$AcknowledgeQuietPilot -ExpectedSourceCommit $ExpectedSourceCommit
exit $LASTEXITCODE
