[CmdletBinding()]
param(
    [string]$UserName = $env:COMPETENCE_HUB_SFTP_USER,
    [string]$KnownHostsPath,
    [string]$CommandFile
)

$ErrorActionPreference = "Stop"
$hostName = "home101506010.1and1-data.host"
$port = 22
$expectedFingerprint = "SHA256:1gx2w8Rtv3wCgi7Jh8myf/KVd72cRQbow03UP8P095Q"

if ([string]::IsNullOrWhiteSpace($UserName)) {
    throw "Pass -UserName or set COMPETENCE_HUB_SFTP_USER. The password is never stored."
}
if ($UserName -notmatch '^[A-Za-z0-9._-]+$') {
    throw "UserName contains unsupported characters."
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $KnownHostsPath) {
    $KnownHostsPath = Join-Path $repoRoot ".tmp\sftp-observed-known-hosts"
}
if (-not (Test-Path -LiteralPath $KnownHostsPath -PathType Leaf)) {
    throw "Pinned known-hosts file is missing: $KnownHostsPath"
}
$knownHosts = (Resolve-Path -LiteralPath $KnownHostsPath).Path

if ($CommandFile) {
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
        if ($line -notmatch '^\s*(?:lcd|lpwd|mkdir|put|chmod|ls|rm|rmdir)\b') {
            throw "SFTP command file contains an unsupported command: $line"
        }
    }
    Set-Clipboard -Value $commands
    Write-Host "Verified SFTP commands copied to the clipboard before login."
    Write-Host "Enter the password manually. At the sftp> prompt, paste once with Ctrl+V."
}

$sshKeygen = Get-Command ssh-keygen -ErrorAction Stop
$sftp = Get-Command sftp -ErrorAction Stop
$fingerprintOutput = & $sshKeygen.Source -lf $knownHosts -E sha256 2>&1
if ($LASTEXITCODE -ne 0 -or ($fingerprintOutput -join "`n") -notmatch [regex]::Escape($expectedFingerprint)) {
    throw "Pinned SFTP host key does not match the approved ED25519 fingerprint."
}

& $sftp.Source @(
    "-P", [string]$port,
    "-o", "KexAlgorithms=curve25519-sha256",
    "-o", "HostKeyAlgorithms=ssh-ed25519",
    "-o", "StrictHostKeyChecking=yes",
    "-o", "UserKnownHostsFile=$knownHosts",
    "-o", "GlobalKnownHostsFile=NUL",
    "-o", "PreferredAuthentications=password",
    "-o", "PubkeyAuthentication=no",
    "$UserName@$hostName"
)
exit $LASTEXITCODE
