[CmdletBinding()]
param(
    [string]$OutputDirectory,
    [string]$PythonPath,
    [switch]$AllowDirty
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$webappRoot = Join-Path $repoRoot "apps\webapp"

function Get-RelativeBundlePath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$FullName
    )

    $rootPrefix = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    $filePath = [IO.Path]::GetFullPath($FullName)
    if (-not $filePath.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Bundle file is outside the expected root: $filePath"
    }
    return $filePath.Substring($rootPrefix.Length).Replace('\', '/')
}

if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $repoRoot "release-artifacts\webapp"
}
if (-not $PythonPath) {
    $PythonPath = Join-Path $webappRoot ".venv\Scripts\python.exe"
}

$statusLines = @(git -C $repoRoot status --porcelain --untracked-files=normal)
if ($LASTEXITCODE -ne 0) {
    throw "Git status could not be determined."
}
$dirty = @($statusLines | Where-Object { $_ -ne '?? .tmp/' })
if ($dirty.Count -gt 0 -and -not $AllowDirty) {
    throw "Release builds require a clean tracked worktree. Commit or stash changes first."
}
if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "Project Python runtime is missing: $PythonPath"
}

$commit = (git -C $repoRoot rev-parse --short=12 HEAD).Trim()
$sourceDateEpoch = (git -C $repoRoot show -s --format=%ct HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or -not $commit -or $sourceDateEpoch -notmatch '^\d+$') {
    throw "Git release metadata could not be determined."
}

$versionCommand = "import tomllib, pathlib; print(tomllib.loads(pathlib.Path(r'$webappRoot\pyproject.toml').read_text(encoding='utf-8'))['project']['version'])"
$version = (& $PythonPath -c $versionCommand).Trim()
if ($LASTEXITCODE -ne 0 -or $version -notmatch '^\d+\.\d+\.\d+([.-][A-Za-z0-9.]+)?$') {
    throw "A valid project version could not be read from pyproject.toml."
}

Write-Output "Running local Webapp release gates..."
Push-Location $webappRoot
try {
    & $PythonPath -m pip check
    if ($LASTEXITCODE -ne 0) {
        throw "pip check failed with exit code $LASTEXITCODE."
    }
    $installedPackages = & $PythonPath -m pip list --format=json | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) {
        throw "Installed package inventory could not be read."
    }
    $installedVersions = @{}
    foreach ($package in $installedPackages) {
        $normalizedName = $package.name.ToLowerInvariant().Replace('_', '-').Replace('.', '-')
        $installedVersions[$normalizedName] = $package.version
    }
    foreach ($line in (Get-Content -LiteralPath (Join-Path $webappRoot "requirements-production.lock"))) {
        if ($line -match '^([^#][^=]+)==(.+)$') {
            $normalizedName = $matches[1].Trim().ToLowerInvariant().Replace('_', '-').Replace('.', '-')
            $lockedVersion = $matches[2].Trim()
            if (-not $installedVersions.ContainsKey($normalizedName)) {
                throw "Locked runtime dependency is not installed locally: $normalizedName"
            }
            if ($installedVersions[$normalizedName] -ne $lockedVersion) {
                throw "Runtime dependency $normalizedName is installed as $($installedVersions[$normalizedName]), expected $lockedVersion."
            }
        }
    }
    & $PythonPath -m pytest
    if ($LASTEXITCODE -ne 0) {
        throw "Webapp tests failed with exit code $LASTEXITCODE."
    }
    & $PythonPath -m compileall -q src
    if ($LASTEXITCODE -ne 0) {
        throw "Python bytecode compilation failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

$timestamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$suffix = if ($dirty.Count -gt 0) { "-dirty" } else { "" }
$artifactBase = "competence-hub-webapp-$version-$commit-$timestamp$suffix"
$outputFullPath = [IO.Path]::GetFullPath($OutputDirectory)
$buildRoot = Join-Path $outputFullPath ".build-$artifactBase"
$bundleRoot = Join-Path $buildRoot "bundle"
$wheelRoot = Join-Path $bundleRoot "packages"
$smokeRoot = Join-Path $buildRoot "install-smoke"
$packageSourceRoot = Join-Path $buildRoot "package-source"

New-Item -ItemType Directory -Force -Path $wheelRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $packageSourceRoot "src") | Out-Null
Copy-Item -LiteralPath (Join-Path $webappRoot "pyproject.toml") -Destination $packageSourceRoot
Copy-Item -LiteralPath (Join-Path $webappRoot "src\competence_hub_api") -Destination (Join-Path $packageSourceRoot "src") -Recurse
$oldTemp = $env:TEMP
$oldTmp = $env:TMP
$oldSourceDateEpoch = $env:SOURCE_DATE_EPOCH
$env:TEMP = Join-Path $buildRoot "temp"
$env:TMP = $env:TEMP
$env:SOURCE_DATE_EPOCH = $sourceDateEpoch
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null

try {
    Write-Output "Building application wheel..."
    & $PythonPath -m pip wheel --no-deps --no-build-isolation --wheel-dir $wheelRoot $packageSourceRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Application wheel build failed with exit code $LASTEXITCODE."
    }
    $wheel = @(Get-ChildItem -LiteralPath $wheelRoot -Filter '*.whl' -File)
    if ($wheel.Count -ne 1) {
        throw "Expected exactly one application wheel, found $($wheel.Count)."
    }

    Copy-Item -LiteralPath (Join-Path $webappRoot "requirements-production.lock") -Destination $bundleRoot
    Copy-Item -LiteralPath (Join-Path $webappRoot "database") -Destination $bundleRoot -Recurse
    Copy-Item -LiteralPath (Join-Path $repoRoot "deploy") -Destination $bundleRoot -Recurse
    $docsRoot = Join-Path $bundleRoot "docs\architecture"
    New-Item -ItemType Directory -Force -Path $docsRoot | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot "docs\architecture\production-release-plan-2026-09-25.md") -Destination $docsRoot
    Copy-Item -LiteralPath (Join-Path $repoRoot "docs\architecture\webapp-release-rehearsal-runbook.md") -Destination $docsRoot
    Copy-Item -LiteralPath (Join-Path $repoRoot "docs\architecture\postgresql-backup-restore-runbook.md") -Destination $docsRoot

    $templateContracts = @{
        "deploy\systemd\competence-hub-api.service.example" = @("__PORT__")
        "deploy\systemd\competence-hub-token-worker.service.example" = @()
        "deploy\systemd\competence-hub-token-worker.timer.example" = @()
        "deploy\systemd\competence-hub-postgres-backup.service.example" = @()
        "deploy\systemd\competence-hub-postgres-backup.timer.example" = @()
        "deploy\systemd\competence-hub-postgres-backup-monitor.service.example" = @()
        "deploy\systemd\competence-hub-postgres-backup-monitor.timer.example" = @()
        "deploy\postgresql\backup.conf.example" = @("__GPG_RECIPIENT_FINGERPRINT__")
        "deploy\nginx\competence-hub-app.conf.example" = @(
            "__APP_HOSTNAME__",
            "__PORT__",
            "__TLS_FULLCHAIN_PATH__",
            "__TLS_PRIVATE_KEY_PATH__"
        )
    }
    foreach ($template in $templateContracts.Keys) {
        $templatePath = Join-Path $bundleRoot $template
        $found = @(
            [regex]::Matches((Get-Content -LiteralPath $templatePath -Raw), '__[A-Z_]+__') |
                ForEach-Object Value |
                Sort-Object -Unique
        )
        $expected = @($templateContracts[$template] | Sort-Object -Unique)
        if (@(Compare-Object -ReferenceObject $expected -DifferenceObject $found).Count -ne 0) {
            throw "Deployment placeholder contract changed unexpectedly: $template"
        }
    }

    Write-Output "Verifying wheel installation in an isolated environment..."
    New-Item -ItemType Directory -Force -Path $smokeRoot | Out-Null
    & $PythonPath -m pip install --target $smokeRoot --no-deps --no-index $wheel[0].FullName
    if ($LASTEXITCODE -ne 0) {
        throw "Application wheel install smoke failed."
    }
    $smokeCode = @'
import pathlib
import sys

target = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(target))

import competence_hub_api
from importlib.resources import files
from competence_hub_api.config import RuntimeConfigurationError, TokenDeliverySettings
from competence_hub_api.runtime import create_runtime_app_from_environment

assert pathlib.Path(competence_hub_api.__file__).resolve().is_relative_to(target)
assert files("competence_hub_api").joinpath("portal_ui/index.html").is_file()
try:
    TokenDeliverySettings.from_environment({})
except RuntimeConfigurationError:
    pass
else:
    raise AssertionError("Token worker configuration did not fail closed")
try:
    create_runtime_app_from_environment({})
except RuntimeConfigurationError:
    pass
else:
    raise AssertionError("API runtime configuration did not fail closed")
'@
    $smokeScript = Join-Path $buildRoot "installed-package-smoke.py"
    Set-Content -LiteralPath $smokeScript -Value $smokeCode -Encoding utf8
    & $PythonPath -I $smokeScript $smokeRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Installed application import/configuration smoke failed."
    }

    $inventory = @()
    Get-ChildItem -LiteralPath $bundleRoot -File -Recurse |
        Sort-Object FullName |
        ForEach-Object {
            $relative = Get-RelativeBundlePath -Root $bundleRoot -FullName $_.FullName
            $inventory += [ordered]@{
                path = $relative
                sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                bytes = $_.Length
            }
        }
    [ordered]@{
        schema = 1
        product = "Competence Hub Webapp"
        version = $version
        commit = $commit
        dirty = ($dirty.Count -gt 0)
        source_date_epoch = [int64]$sourceDateEpoch
        python = (& $PythonPath --version 2>&1).ToString().Trim()
        deployment_authorized = $false
        files = $inventory
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $bundleRoot "MANIFEST.json") -Encoding utf8

    New-Item -ItemType Directory -Force -Path $outputFullPath | Out-Null
    $archive = Join-Path $outputFullPath "$artifactBase.zip"
    $manifest = Join-Path $outputFullPath "$artifactBase.json"
    $checksum = Join-Path $outputFullPath "$artifactBase.sha256"

    Add-Type -AssemblyName System.IO.Compression
    $archiveStream = [IO.File]::Open($archive, [IO.FileMode]::CreateNew)
    try {
        $zip = [IO.Compression.ZipArchive]::new(
            $archiveStream,
            [IO.Compression.ZipArchiveMode]::Create,
            $false
        )
        try {
            $entryTimestamp = [DateTimeOffset]::FromUnixTimeSeconds([int64]$sourceDateEpoch)
            foreach ($file in (Get-ChildItem -LiteralPath $bundleRoot -File -Recurse | Sort-Object FullName)) {
                $relative = Get-RelativeBundlePath -Root $bundleRoot -FullName $file.FullName
                $entry = $zip.CreateEntry($relative, [IO.Compression.CompressionLevel]::Optimal)
                $entry.LastWriteTime = $entryTimestamp
                $inputStream = [IO.File]::OpenRead($file.FullName)
                $outputStream = $entry.Open()
                try {
                    $inputStream.CopyTo($outputStream)
                }
                finally {
                    $outputStream.Dispose()
                    $inputStream.Dispose()
                }
            }
        }
        finally {
            $zip.Dispose()
        }
    }
    finally {
        $archiveStream.Dispose()
    }

    $archiveHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    [ordered]@{
        artifact = Split-Path -Leaf $archive
        sha256 = $archiveHash
        version = $version
        commit = $commit
        dirty = ($dirty.Count -gt 0)
        built_at_utc = [DateTime]::UtcNow.ToString("o")
        deployment_authorized = $false
        dependency_mode = "exact-version lock; Linux wheelhouse still required before production"
    } | ConvertTo-Json | Set-Content -LiteralPath $manifest -Encoding utf8
    "$archiveHash  $(Split-Path -Leaf $archive)" | Set-Content -LiteralPath $checksum -Encoding ascii

    Write-Output "Artifact: $archive"
    Write-Output "Manifest: $manifest"
    Write-Output "Checksum: $checksum"
    Write-Output "SHA256: $archiveHash"
    Write-Output "Deployment was not performed."
}
finally {
    $env:TEMP = $oldTemp
    $env:TMP = $oldTmp
    $env:SOURCE_DATE_EPOCH = $oldSourceDateEpoch
    $buildRootFullPath = [IO.Path]::GetFullPath($buildRoot)
    if ($buildRootFullPath.StartsWith($outputFullPath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $buildRootFullPath -Recurse -Force -ErrorAction SilentlyContinue
    }
}
