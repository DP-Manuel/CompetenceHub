[CmdletBinding()]
param(
    [string]$UserName = $env:COMPETENCE_HUB_SFTP_USER,
    [string]$KnownHostsPath
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
