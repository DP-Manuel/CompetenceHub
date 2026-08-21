[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ArtifactPath,

    [Parameter(Mandatory = $true)]
    [string]$ManifestPath,

    [Parameter(Mandatory = $true)]
    [string]$TargetContractPath,

    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"
$expectedCanonicalUrl = "https://competencehub.donner-partner.de"
$expectedRedirectUrl = "https://competence-hub.donner-partner.de"
$maximumArchiveEntries = 10000
$maximumExpandedBytes = 250MB

function Resolve-ExistingFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label does not exist or is not a file: $Path"
    }

    return (Resolve-Path -LiteralPath $Path).Path
}

function Assert-PlainValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if ([string]::IsNullOrWhiteSpace($Value) -or
        $Value.Contains("__") -or
        $Value -match '[\x00-\x1f\x7f]') {
        throw "$Label is missing, still contains a placeholder, or contains control characters."
    }
}

function Assert-RequiredProperty {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Object,
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if ($null -eq $Object.PSObject.Properties[$Name]) {
        throw "$Label is missing required property: $Name"
    }
}

function Assert-BooleanProperty {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Object,
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    Assert-RequiredProperty -Object $Object -Name $Name -Label $Label
    if ($Object.$Name -isnot [bool]) {
        throw "$Label property must be a JSON boolean: $Name"
    }
}

function Assert-RemoteWebRoot {
    param([Parameter(Mandatory = $true)][string]$Value)

    Assert-PlainValue -Value $Value -Label "remote_web_root"
    if ($Value -ne "." -and $Value -notmatch '^/(?:[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*)?$') {
        throw "remote_web_root must be '.' or an absolute POSIX path without traversal, spaces, wildcards, or shell metacharacters."
    }
    if ($Value -match '(^|/)\.\.?(?:/|$)' -or $Value.Contains("\")) {
        throw "remote_web_root contains an unsafe path segment."
    }
}

function Assert-SafeArchiveEntry {
    param([Parameter(Mandatory = $true)][System.IO.Compression.ZipArchiveEntry]$Entry)

    $name = $Entry.FullName.Replace("\", "/")
    if ([string]::IsNullOrWhiteSpace($name) -or
        $name.StartsWith("/") -or
        $name -match '^[A-Za-z]:' -or
        $name -match '(^|/)\.\.?(?:/|$)' -or
        $name -match '[\x00-\x1f\x7f]') {
        throw "Archive contains an unsafe entry path: $($Entry.FullName)"
    }

    foreach ($segment in ($name -split '/')) {
        if ($segment -like ".env*" -or
            $segment -in @(".tmp", "Quellen", "node_modules")) {
            throw "Archive contains a forbidden entry segment: $segment"
        }
    }

    $unixFileType = (($Entry.ExternalAttributes -shr 16) -band 0xF000)
    if ($unixFileType -eq 0xA000) {
        throw "Archive contains a symbolic link: $($Entry.FullName)"
    }

    return $name
}

$artifact = Resolve-ExistingFile -Path $ArtifactPath -Label "Artifact"
$manifestFile = Resolve-ExistingFile -Path $ManifestPath -Label "Manifest"
$targetFile = Resolve-ExistingFile -Path $TargetContractPath -Label "Target contract"

$manifest = Get-Content -LiteralPath $manifestFile -Raw | ConvertFrom-Json
$target = Get-Content -LiteralPath $targetFile -Raw | ConvertFrom-Json

foreach ($property in @(
    "artifact", "sha256", "commit", "dirty", "canonical_url",
    "deployment_authorized"
)) {
    Assert-RequiredProperty -Object $manifest -Name $property -Label "Manifest"
}
Assert-BooleanProperty -Object $manifest -Name "dirty" -Label "Manifest"
Assert-BooleanProperty -Object $manifest -Name "deployment_authorized" -Label "Manifest"
foreach ($property in @(
    "schema_version", "canonical_url", "redirect_url", "sftp_host",
    "sftp_port", "sftp_host_key_sha256", "remote_web_root",
    "remote_web_root_verified", "expected_entrypoint"
)) {
    Assert-RequiredProperty -Object $target -Name $property -Label "Target contract"
}
Assert-BooleanProperty -Object $target -Name "remote_web_root_verified" -Label "Target contract"

if ([int]$target.schema_version -ne 1) {
    throw "Unsupported target contract schema_version."
}
Assert-PlainValue -Value ([string]$target.sftp_host) -Label "sftp_host"
if ([System.Uri]::CheckHostName([string]$target.sftp_host) -eq [System.UriHostNameType]::Unknown) {
    throw "sftp_host is not a valid DNS name or IP address."
}
Assert-PlainValue -Value ([string]$target.sftp_host_key_sha256) -Label "sftp_host_key_sha256"
if ([string]$target.sftp_host_key_sha256 -notmatch '^SHA256:[A-Za-z0-9+/]{43}=?$') {
    throw "sftp_host_key_sha256 must be a verified SHA-256 host-key fingerprint."
}
Assert-RemoteWebRoot -Value ([string]$target.remote_web_root)
if (-not [bool]$target.remote_web_root_verified) {
    throw "remote_web_root_verified must be true after a read-only remote inventory."
}
if ([int]$target.sftp_port -lt 1 -or [int]$target.sftp_port -gt 65535) {
    throw "sftp_port must be between 1 and 65535."
}
if ([string]$target.canonical_url -cne $expectedCanonicalUrl) {
    throw "Target canonical_url does not match the approved Website domain."
}
if ([string]$target.redirect_url -cne $expectedRedirectUrl) {
    throw "Target redirect_url does not match the approved redirect domain."
}
if ([string]$target.expected_entrypoint -cne "index.html") {
    throw "Target expected_entrypoint must be index.html."
}

$artifactName = Split-Path -Leaf $artifact
if ([System.IO.Path]::GetExtension($artifactName) -cne ".zip") {
    throw "Website artifact must be a ZIP archive."
}
if ([string]$manifest.artifact -cne $artifactName) {
    throw "Manifest artifact name does not match the supplied archive."
}
if ([string]$manifest.sha256 -notmatch '^[0-9a-f]{64}$') {
    throw "Manifest sha256 is missing or invalid."
}
if ([string]$manifest.commit -notmatch '^[0-9a-f]{7,40}$') {
    throw "Manifest commit is missing or invalid."
}
if ([bool]$manifest.dirty) {
    throw "Dirty Website artifacts are not eligible for an SFTP rehearsal package."
}
if ([string]$manifest.canonical_url -cne $expectedCanonicalUrl) {
    throw "Manifest canonical_url does not match the approved Website domain."
}
if ([bool]$manifest.deployment_authorized) {
    throw "The build manifest must not claim deployment authorization."
}

$actualHash = (Get-FileHash -LiteralPath $artifact -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -cne [string]$manifest.sha256) {
    throw "Artifact SHA-256 does not match the manifest."
}

if (-not $OutputDirectory) {
    $repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $OutputDirectory = Join-Path $repoRoot "release-artifacts\website-sftp-rehearsal"
}
$resolvedOutputParent = [System.IO.Path]::GetFullPath($OutputDirectory)
$packageName = "website-$($manifest.commit)-sftp-rehearsal"
$packageRoot = Join-Path $resolvedOutputParent $packageName
if (Test-Path -LiteralPath $packageRoot) {
    throw "Rehearsal package already exists: $packageRoot"
}

$releaseRoot = Join-Path $packageRoot "release"
New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null
$releaseRootFull = [System.IO.Path]::GetFullPath($releaseRoot)
$releasePrefix = $releaseRootFull.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($artifact)
try {
    if ($zip.Entries.Count -eq 0 -or $zip.Entries.Count -gt $maximumArchiveEntries) {
        throw "Archive entry count is outside the allowed range."
    }

    $expandedBytes = [int64]0
    $seenEntries = @{}
    foreach ($entry in $zip.Entries) {
        $safeName = Assert-SafeArchiveEntry -Entry $entry
        $comparisonKey = $safeName.ToLowerInvariant()
        if ($seenEntries.ContainsKey($comparisonKey)) {
            throw "Archive contains duplicate or case-colliding entries: $safeName"
        }
        $seenEntries[$comparisonKey] = $true

        $expandedBytes += [int64]$entry.Length
        if ($expandedBytes -gt $maximumExpandedBytes) {
            throw "Expanded archive exceeds the 250 MiB safety limit."
        }

        $destination = [System.IO.Path]::GetFullPath((Join-Path $releaseRoot $safeName))
        if (-not $destination.StartsWith($releasePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Archive entry escapes the rehearsal directory: $safeName"
        }
        if ($safeName.EndsWith("/")) {
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
            continue
        }

        $destinationParent = Split-Path -Parent $destination
        New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
        $sourceStream = $entry.Open()
        $destinationStream = [System.IO.File]::Create($destination)
        try {
            $sourceStream.CopyTo($destinationStream)
        }
        finally {
            $destinationStream.Dispose()
            $sourceStream.Dispose()
        }
    }
}
catch {
    if (Test-Path -LiteralPath $packageRoot) {
        Remove-Item -LiteralPath $packageRoot -Recurse -Force
    }
    throw
}
finally {
    $zip.Dispose()
}

$entrypoint = Join-Path $releaseRoot "index.html"
if (-not (Test-Path -LiteralPath $entrypoint -PathType Leaf)) {
    Remove-Item -LiteralPath $packageRoot -Recurse -Force
    throw "Verified archive does not contain index.html at its root."
}

$inventory = Get-ChildItem -LiteralPath $releaseRoot -File -Recurse | Sort-Object FullName | ForEach-Object {
    $relative = $_.FullName.Substring($releasePrefix.Length).Replace("\", "/")
    $fileHash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "$fileHash  $relative"
}
$inventoryPath = Join-Path $packageRoot "release-files.sha256"
$inventory | Set-Content -LiteralPath $inventoryPath -Encoding ascii

$plan = [ordered]@{
    schema_version = 1
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    artifact = $artifactName
    artifact_sha256 = $actualHash
    commit = [string]$manifest.commit
    canonical_url = $expectedCanonicalUrl
    redirect_url = $expectedRedirectUrl
    sftp_host = [string]$target.sftp_host
    sftp_port = [int]$target.sftp_port
    sftp_host_key_sha256 = [string]$target.sftp_host_key_sha256
    remote_web_root = [string]$target.remote_web_root
    remote_web_root_verified = $true
    release_file_count = @($inventory).Count
    release_expanded_bytes = $expandedBytes
    artifact_verified = $true
    remote_inventory_verified = $false
    remote_backup_verified = $false
    remote_change_authorized = $false
    legal_release_gate_closed = $false
    production_smoke_verified = $false
    rollback_verified = $false
}
$plan | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $packageRoot "release-plan.json") -Encoding utf8

$checklist = @"
# Website SFTP Rehearsal Checklist

This package is local preparation only. It does not authorize or perform an
SFTP connection, upload, deletion, rename, DNS change, or deployment.

## Verified locally

- [x] Artifact filename: `$artifactName`
- [x] Artifact SHA-256: `$actualHash`
- [x] Source commit: `$($manifest.commit)`
- [x] Canonical URL: `$expectedCanonicalUrl`
- [x] Expected entrypoint: `index.html`
- [x] Remote target pinned to `$($target.sftp_host):$($target.sftp_port)` and `$($target.remote_web_root)`

## Required before any remote change

- [ ] Final operator and legal pages are approved.
- [ ] Contact mailbox routing is tested.
- [ ] Thomas Ross has granted the production/rehearsal approval.
- [ ] The SFTP host key is verified through a second trusted channel.
- [ ] A read-only remote inventory confirms the exact document root.
- [ ] Unknown remote files are classified; none are silently deleted.
- [ ] The complete existing web root is downloaded to a dated local rollback directory.
- [ ] The rollback copy has a local SHA-256 inventory and opens successfully.
- [ ] The exact artifact hash and commit are recorded in the release ticket.

## Production smoke after an approved upload

- [ ] Both HTTPS hostnames respond; the hyphenated hostname redirects permanently.
- [ ] `/`, `/leistungen`, `/unternehmen`, `/coaches`, `/mindforge`, `/kontakt` and `/ueber-uns` load.
- [ ] Impressum, Datenschutz and AGB links load.
- [ ] Canonical, robots and sitemap behavior match production.
- [ ] Contact address and mail link are correct.
- [ ] Mobile navigation and the Living Hub work without blocking console errors.
- [ ] No review banner or public prototype/login indexing remains.

## Rollback gate

- [ ] Rollback owner and decision channel are available.
- [ ] The pre-release Webspace copy can be restored without guessing paths.
- [ ] Core routes and both hostnames are rechecked after restoration.
- [ ] Cause, restored artifact and timestamps are recorded.
"@
$checklist | Set-Content -LiteralPath (Join-Path $packageRoot "OPERATOR-CHECKLIST.md") -Encoding utf8

Write-Output "Rehearsal package: $packageRoot"
Write-Output "Artifact verified: $artifactName"
Write-Output "Pinned remote root: $($target.remote_web_root)"
Write-Output "No network connection or deployment was performed."
