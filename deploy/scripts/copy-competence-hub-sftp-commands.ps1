[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CommandFile
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $CommandFile -PathType Leaf)) {
    throw "SFTP command file is missing: $CommandFile"
}

$resolvedCommandFile = (Resolve-Path -LiteralPath $CommandFile).Path
$commands = Get-Content -LiteralPath $resolvedCommandFile -Raw
$commandLines = @($commands -split "`r?`n" | Where-Object { $_.Trim().Length -gt 0 })

if ($commandLines.Count -eq 0 -or $commandLines[0] -notmatch '^lcd\s+"?[\x20-\x7e]+"?$') {
    throw "SFTP command file must begin with an ASCII-only lcd preflight."
}
if ($commands -match '[^\x09\x0a\x0d\x20-\x7e]' -or
    $commands -match '(?im)^\s*(?:!|bye\s*$|exit\s*$|sftp\s+)') {
    throw "SFTP command file contains non-ASCII or unsupported interactive commands."
}
foreach ($line in $commandLines) {
    if ($line -notmatch '^\s*(?:lcd|lpwd|get|mkdir|put|chmod|ls|rm|rmdir)\b') {
        throw "SFTP command file contains an unsupported command: $line"
    }
}

Set-Clipboard -Value $commands
Write-Output "SFTP_COMMANDS_READY: $($commandLines.Count) verified commands copied after authentication."
