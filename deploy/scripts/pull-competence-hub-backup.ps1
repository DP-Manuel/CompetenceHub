[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9.-]+$')]
    [string]$RemoteHost,

    [ValidatePattern('^[a-z_][a-z0-9_-]{0,31}$')]
    [string]$RemoteUser = 'manuel',

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')]
    [string]$BackupDate,

    [Parameter(Mandatory = $true)]
    [string]$DestinationRoot,

    [Parameter(Mandatory = $true)]
    [switch]$ConfirmProtectedDestination,

    [string]$ScpPath = 'scp.exe'
)

$ErrorActionPreference = 'Stop'

if (-not $ConfirmProtectedDestination) {
    throw 'ConfirmProtectedDestination is required after verifying encryption, access control and available space.'
}

$repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot))).TrimEnd('\')
$destination = [IO.Path]::GetFullPath($DestinationRoot).TrimEnd('\')
if (-not (Test-Path -LiteralPath $destination -PathType Container)) {
    throw "Destination root does not exist: $destination"
}
$destinationItem = Get-Item -LiteralPath $destination -Force
if (($destinationItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Destination root must not be a reparse point or symlink.'
}

$separator = [IO.Path]::DirectorySeparatorChar
$destinationPrefix = $destination + $separator
$repoPrefix = $repoRoot + $separator
if ($destination.Equals($repoRoot, [StringComparison]::OrdinalIgnoreCase) -or
    $destination.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase) -or
    $repoRoot.StartsWith($destinationPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Backup destination must be separate from the repository and must not contain it.'
}

$scpCommand = Get-Command $ScpPath -ErrorAction Stop
$productRoot = Join-Path $destination 'competence-hub-backups'
$target = Join-Path $productRoot $BackupDate
if (Test-Path -LiteralPath $target) {
    throw "Refusing to overwrite an existing backup set: $target"
}
New-Item -ItemType Directory -Path $productRoot -Force | Out-Null

$remoteSource = "${RemoteUser}@${RemoteHost}:/home/${RemoteUser}/competence-hub-backup-export/${BackupDate}"
try {
    & $scpCommand.Source -r -- $remoteSource $productRoot
    if ($LASTEXITCODE -ne 0) {
        throw "SCP failed with exit code $LASTEXITCODE."
    }

    $resolvedTarget = [IO.Path]::GetFullPath($target)
    if (-not $resolvedTarget.StartsWith(([IO.Path]::GetFullPath($productRoot).TrimEnd('\') + $separator), [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Downloaded target escaped the approved destination root.'
    }
    foreach ($requiredName in @('COMPLETE', 'METADATA', 'SHA256SUMS')) {
        if (-not (Test-Path -LiteralPath (Join-Path $target $requiredName) -PathType Leaf)) {
            throw "Downloaded backup set is incomplete: $requiredName is missing."
        }
    }

    $reparseEntries = @(Get-ChildItem -LiteralPath $target -Force | Where-Object {
        ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
    })
    if ($reparseEntries.Count -ne 0) {
        throw 'Downloaded backup set contains a reparse point or symlink.'
    }

    $encryptedFiles = @(Get-ChildItem -LiteralPath $target -File -Filter '*.gpg')
    if ($encryptedFiles.Count -ne 2) {
        throw 'Downloaded backup set must contain exactly two encrypted payloads.'
    }
    $plaintext = @(Get-ChildItem -LiteralPath $target -File | Where-Object {
        $_.Extension -in @('.dump', '.sql')
    })
    if ($plaintext.Count -ne 0) {
        throw 'Downloaded backup set contains plaintext database material.'
    }

    $checksumLines = @(Get-Content -LiteralPath (Join-Path $target 'SHA256SUMS'))
    if ($checksumLines.Count -ne 3) {
        throw 'SHA256SUMS must contain exactly three entries.'
    }
    foreach ($line in $checksumLines) {
        if ($line -notmatch '^([a-fA-F0-9]{64})  ([A-Za-z0-9._-]+)$') {
            throw 'SHA256SUMS contains an unsafe or malformed entry.'
        }
        $expected = $matches[1].ToLowerInvariant()
        $name = $matches[2]
        $file = Join-Path $target $name
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw "Checksummed file is missing: $name"
        }
        $actual = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $expected) {
            throw "Checksum mismatch: $name"
        }
    }

    Write-Output "Verified encrypted off-server copy: $target"
    Write-Output 'The remote export was not deleted. Remove it only after the supervised restore gate.'
}
catch {
    if (Test-Path -LiteralPath $target) {
        $resolvedTarget = [IO.Path]::GetFullPath($target)
        $safePrefix = [IO.Path]::GetFullPath($productRoot).TrimEnd('\') + $separator
        if ($resolvedTarget.StartsWith($safePrefix, [StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
        }
    }
    throw
}
