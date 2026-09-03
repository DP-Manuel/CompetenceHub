[CmdletBinding()]
param(
    [string]$OutputDirectory,
    [switch]$InstallDependencies,
    [switch]$AllowDirty
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$websiteRoot = Join-Path $repoRoot "apps\website"
$nodeRoot = Join-Path $repoRoot "tools\node-v22.16.0-win-x64"

if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $repoRoot "release-artifacts\website"
}

$statusLines = @(git -C $repoRoot status --porcelain --untracked-files=normal)
if ($LASTEXITCODE -ne 0) {
    throw "Git status could not be determined."
}
$dirty = @($statusLines | Where-Object { $_ -ne '?? .tmp/' })
if ($dirty.Count -gt 0 -and -not $AllowDirty) {
    throw "Release builds require a clean tracked worktree. Commit or stash changes first."
}

if (-not (Test-Path -LiteralPath (Join-Path $nodeRoot "node.exe"))) {
    throw "Repository-local Node.js runtime is missing: $nodeRoot"
}

$env:PATH = "$nodeRoot;$env:PATH"
$env:ASTRO_TELEMETRY_DISABLED = "1"
$env:GITHUB_PAGES_REVIEW = "false"
$env:PUBLIC_REVIEW_MODE = "false"

Push-Location $websiteRoot
try {
    if ($InstallDependencies) {
        & npm ci
        if ($LASTEXITCODE -ne 0) {
            throw "npm ci failed with exit code $LASTEXITCODE."
        }
    }

    & npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "Website build failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

$commit = (git -C $repoRoot rev-parse --short=12 HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or -not $commit) {
    throw "Git commit could not be determined."
}
$timestamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$suffix = if ($dirty.Count -gt 0) { "-dirty" } else { "" }
$artifactBase = "competence-hub-website-$commit-$timestamp$suffix"

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$archive = Join-Path $OutputDirectory "$artifactBase.zip"
$manifest = Join-Path $OutputDirectory "$artifactBase.json"
$distRoot = Join-Path $websiteRoot "dist"

foreach ($requiredFile in @("index.html", "404.html", ".htaccess")) {
    if (-not (Test-Path -LiteralPath (Join-Path $distRoot $requiredFile) -PathType Leaf)) {
        throw "Website build is missing required production file: $requiredFile"
    }
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $distRoot,
    $archive,
    [System.IO.Compression.CompressionLevel]::Optimal,
    $false
)

$zip = [System.IO.Compression.ZipFile]::OpenRead($archive)
try {
    $entryNames = @($zip.Entries | ForEach-Object { $_.FullName.Replace("\", "/") })
    foreach ($requiredEntry in @("index.html", "404.html", ".htaccess")) {
        if ($requiredEntry -cnotin $entryNames) {
            throw "Website release archive is missing required entry: $requiredEntry"
        }
    }
}
catch {
    if (Test-Path -LiteralPath $archive) {
        Remove-Item -LiteralPath $archive -Force
    }
    throw
}
finally {
    $zip.Dispose()
}

$hash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()

[ordered]@{
    artifact = Split-Path -Leaf $archive
    sha256 = $hash
    commit = $commit
    dirty = ($dirty.Count -gt 0)
    built_at_utc = [DateTime]::UtcNow.ToString("o")
    canonical_url = "https://competencehub.donner-partner.de"
    deployment_authorized = $false
} | ConvertTo-Json | Set-Content -LiteralPath $manifest -Encoding utf8

Write-Output "Artifact: $archive"
Write-Output "Manifest: $manifest"
Write-Output "SHA256: $hash"
Write-Output "Deployment was not performed."
