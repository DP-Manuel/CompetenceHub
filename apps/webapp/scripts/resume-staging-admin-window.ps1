#requires -Version 7.2
<# Compatibility entry: now local keys ONLY, never continues to server/admin. #>
[CmdletBinding()]
param([switch]$Execute, [string]$ExpectedSourceCommit)
$entry = Join-Path $PSScriptRoot 'verify-staging-keys.ps1'
if ($MyInvocation.InvocationName -eq '.') {
    . $entry
} else {
    & $entry @PSBoundParameters
    if (-not $?) { exit 1 }
}
