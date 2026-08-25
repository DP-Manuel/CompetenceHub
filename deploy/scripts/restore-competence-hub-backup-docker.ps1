[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BackupSet,

    [Parameter(Mandatory = $true)]
    [string]$GpgHome,

    [Parameter(Mandatory = $true)]
    [switch]$ConfirmProtectedSource,

    [Parameter(Mandatory = $true)]
    [switch]$ConfirmIsolatedRestore,

    [ValidatePattern('^postgres@sha256:[a-f0-9]{64}$')]
    [string]$ImageRef = 'postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825',

    [string]$GpgPath = 'C:\Program Files\GnuPG\bin\gpg.exe',

    [string]$DockerPath = 'docker.exe'
)

$ErrorActionPreference = 'Stop'

if (-not $ConfirmProtectedSource -or -not $ConfirmIsolatedRestore) {
    throw 'Protected-source and isolated-restore confirmations are required.'
}

$repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot))).TrimEnd('\')
$source = [IO.Path]::GetFullPath($BackupSet).TrimEnd('\')
$sourcePrefix = $source + [IO.Path]::DirectorySeparatorChar
$repoPrefix = $repoRoot + [IO.Path]::DirectorySeparatorChar
if ($source.Equals($repoRoot, [StringComparison]::OrdinalIgnoreCase) -or
    $source.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase) -or
    $repoRoot.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Restore source must be separate from the repository and must not contain it.'
}
if (-not (Test-Path -LiteralPath $source -PathType Container)) {
    throw "Backup set does not exist: $source"
}
$sourceItem = Get-Item -LiteralPath $source -Force
if (($sourceItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Backup set must not be a reparse point or symlink.'
}
if (-not (Test-Path -LiteralPath $GpgHome -PathType Container)) {
    throw 'Protected GnuPG home does not exist.'
}
$gpg = Get-Command $GpgPath -ErrorAction Stop
$docker = Get-Command $DockerPath -ErrorAction Stop

foreach ($requiredName in @('COMPLETE', 'METADATA', 'SHA256SUMS')) {
    if (-not (Test-Path -LiteralPath (Join-Path $source $requiredName) -PathType Leaf)) {
        throw "Backup set is incomplete: $requiredName is missing."
    }
}
$reparseEntries = @(Get-ChildItem -LiteralPath $source -Force | Where-Object {
    ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
})
if ($reparseEntries.Count -ne 0) {
    throw 'Backup set contains a reparse point or symlink.'
}
$encryptedFiles = @(Get-ChildItem -LiteralPath $source -File -Filter '*.gpg')
if ($encryptedFiles.Count -ne 2) {
    throw 'Backup set must contain exactly two encrypted payloads.'
}
$encryptedDump = @($encryptedFiles | Where-Object { $_.Name -match '\.dump\.gpg$' })
if ($encryptedDump.Count -ne 1) {
    throw 'Backup set must contain exactly one encrypted custom-format database dump.'
}
$plaintext = @(Get-ChildItem -LiteralPath $source -File | Where-Object {
    $_.Extension -in @('.dump', '.sql')
})
if ($plaintext.Count -ne 0) {
    throw 'Backup set contains plaintext database material.'
}

$checksumLines = @(Get-Content -LiteralPath (Join-Path $source 'SHA256SUMS'))
if ($checksumLines.Count -ne 3) {
    throw 'SHA256SUMS must contain exactly three entries.'
}
foreach ($line in $checksumLines) {
    if ($line -notmatch '^([a-fA-F0-9]{64})  ([A-Za-z0-9._-]+)$') {
        throw 'SHA256SUMS contains an unsafe or malformed entry.'
    }
    $expected = $matches[1].ToLowerInvariant()
    $name = $matches[2]
    $file = Join-Path $source $name
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Checksummed file is missing: $name"
    }
    $actual = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) {
        throw "Checksum mismatch: $name"
    }
}

& $docker.Source image inspect $ImageRef *> $null
if ($LASTEXITCODE -ne 0) {
    throw 'Pinned PostgreSQL image is not available locally; this script never pulls images.'
}

$container = 'competence-hub-restore-check-' + (Get-Date -Format 'yyyyMMddHHmmss')
$restoreRoot = Join-Path $env:LOCALAPPDATA (
    'CompetenceHub\restore-check-' + [guid]::NewGuid().ToString('N')
)
$plainDump = Join-Path $restoreRoot 'database.dump'
$containerStarted = $false

try {
    New-Item -ItemType Directory -Path $restoreRoot | Out-Null
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    & icacls.exe $restoreRoot '/inheritance:r' '/grant:r' "${identity}:(OI)(CI)F" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not restrict temporary restore directory ACL.'
    }

    & $gpg.Source --homedir $GpgHome --no-tty --output $plainDump --decrypt $encryptedDump[0].FullName
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $plainDump -PathType Leaf)) {
        throw 'Local decryption failed.'
    }

    $passwordBytes = New-Object byte[] 36
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($passwordBytes)
    }
    finally {
        $rng.Dispose()
    }
    $databasePassword = [Convert]::ToBase64String($passwordBytes)
    $mount = "type=bind,source=$restoreRoot,target=/restore,readonly"
    & $docker.Source run -d --pull never --name $container --network none `
        -e "POSTGRES_PASSWORD=$databasePassword" --mount $mount $ImageRef *> $null
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not start isolated PostgreSQL container.'
    }
    $containerStarted = $true

    $ready = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        & $docker.Source exec $container pg_isready -U postgres *> $null
        if ($LASTEXITCODE -eq 0) {
            $ready = $true
            break
        }
        Start-Sleep -Seconds 1
    }
    if (-not $ready) {
        throw 'Isolated PostgreSQL container did not become ready.'
    }

    & $docker.Source exec $container pg_restore --list /restore/database.dump *> $null
    if ($LASTEXITCODE -ne 0) {
        throw 'pg_restore archive validation failed.'
    }
    & $docker.Source exec $container createdb -U postgres competence_hub_restore_check
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not create isolated restore database.'
    }
    & $docker.Source exec $container pg_restore --exit-on-error --no-owner `
        --no-privileges -U postgres -d competence_hub_restore_check /restore/database.dump
    if ($LASTEXITCODE -ne 0) {
        throw 'Isolated pg_restore failed.'
    }

    $schemaCount = (& $docker.Source exec $container psql -U postgres `
        -d competence_hub_restore_check -Atc `
        "SELECT count(*) FROM information_schema.schemata WHERE schema_name = 'competence_hub';").Trim()
    $tableCount = (& $docker.Source exec $container psql -U postgres `
        -d competence_hub_restore_check -Atc `
        "SELECT count(*) FROM pg_tables WHERE schemaname = 'competence_hub';").Trim()
    if ($schemaCount -ne '1' -or [int]$tableCount -lt 1) {
        throw "Restore verification failed: schema=$schemaCount tables=$tableCount"
    }

    Write-Output "Verified isolated restore from external copy: $source"
    Write-Output "Restored application tables: $tableCount"
    Write-Output "Pinned restore image: $ImageRef"
}
finally {
    if ($containerStarted) {
        & $docker.Source rm -f $container *> $null
    }
    if (Test-Path -LiteralPath $plainDump) {
        Remove-Item -LiteralPath $plainDump -Force
    }
    if (Test-Path -LiteralPath $restoreRoot) {
        Remove-Item -LiteralPath $restoreRoot -Recurse -Force
    }
}
