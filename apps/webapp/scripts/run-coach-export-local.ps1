#requires -Version 7.2
[CmdletBinding()]
param([Parameter(Mandatory)][string]$PythonPath)
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path -LiteralPath $PythonPath).Path
$webapp = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$oldPath = $env:PYTHONPATH
$oldLocation = Get-Location
$container = $null
$image = 'sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825'
$names = @('POSTGRES_PASSWORD','COMPETENCE_HUB_COACH_EXPORT_LOCAL_DATABASE_URL','COMPETENCE_HUB_COACH_EXPORT_LOCAL_OWNER_URL')
foreach ($name in $names) {
    if (Test-Path -LiteralPath "Env:$name") { throw "Existing $name will not be replaced." }
}
if (Get-NetTCPConnection -LocalPort 55437 -State Listen -ErrorAction SilentlyContinue) { throw 'Owned local export port55437 must be unused.' }
$context = (& docker context inspect --format '{{json .Endpoints.docker.Host}}').Trim()
if ($LASTEXITCODE -ne 0 -or $context -cnotmatch '^"npipe:////\./pipe/(docker_engine|dockerDesktopLinuxEngine)"$') { throw 'Local Docker Desktop engine required.' }
$platform = (& docker image inspect --format '{{.Os}} {{.Architecture}}' $image).Trim()
if ($LASTEXITCODE -ne 0 -or $platform -cne 'linux amd64') { throw 'Cached pinned PostgreSQL image required; no pull.' }
try {
    Set-Location -LiteralPath $webapp
    $env:POSTGRES_PASSWORD = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $container = (& docker run --detach --pull never --name "competence-hub-export-local-$([Guid]::NewGuid().ToString('N'))" --publish '127.0.0.1:55437:5432' --env POSTGRES_PASSWORD --tmpfs '/var/lib/postgresql/data' $image).Trim()
    if ($LASTEXITCODE -ne 0 -or $container -cnotmatch '^[a-f0-9]{64}$') { throw 'Owned export container creation failed.' }
    $ready = $false
    for ($i=0; $i -lt 80; $i++) {
        $pidOne = & docker exec $container cat /proc/1/comm 2>$null
        & docker exec $container pg_isready -U postgres 1>$null 2>$null
        if ($LASTEXITCODE -eq 0 -and $pidOne -ceq 'postgres') { $ready=$true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw 'Final PostgreSQL process is not ready.' }
    Get-Content -Raw '.\database\bootstrap-staging.sql' | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic bootstrap failed.' }
    'ALTER DATABASE competence_hub_staging RENAME TO competence_hub_export_synthetic;' | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Dedicated synthetic database naming failed.' }
    $migrations = @(Get-ChildItem '.\database\migrations' -File | Where-Object Name -Match '^000[1-9]_.+\.sql$' | Sort-Object Name)
    if ($migrations.Count -ne 9) { throw 'Exactly nine existing local migrations required.' }
    foreach ($migration in $migrations) {
        Get-Content -Raw -LiteralPath $migration.FullName | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d competence_hub_export_synthetic 1>$null
        if ($LASTEXITCODE -ne 0) { throw 'Local synthetic schema initialization failed.' }
    }
    $password = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    "ALTER ROLE competence_hub_app PASSWORD '$password'; ALTER ROLE competence_hub_migrator PASSWORD '$password';" | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic process-only roles failed.' }
    $env:COMPETENCE_HUB_COACH_EXPORT_LOCAL_DATABASE_URL = "postgresql+asyncpg://competence_hub_app:${password}@127.0.0.1:55437/competence_hub_export_synthetic"
    $env:COMPETENCE_HUB_COACH_EXPORT_LOCAL_OWNER_URL = "postgresql+asyncpg://competence_hub_migrator:${password}@127.0.0.1:55437/competence_hub_export_synthetic"
    $env:PYTHONPATH = (Join-Path $webapp 'src') + ';' + $webapp
    & $python -m pytest -q -s --tb=short --show-capture=no -o addopts='' tests/test_coach_export_postgres_local.py
    if ($LASTEXITCODE -ne 0) { throw 'Native export acceptance failed; no real operation started.' }
}
finally {
    $env:PYTHONPATH = $oldPath
    foreach ($name in $names) { Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue }
    $password = $null
    if ($container -cmatch '^[a-f0-9]{64}$') {
        & docker rm --force $container 1>$null
        if ($LASTEXITCODE -ne 0) { throw 'Owned export container removal failed.' }
        $remaining = @(& docker ps --all --quiet --no-trunc --filter "id=$container")
        if ($LASTEXITCODE -ne 0 -or $remaining.Count) { throw 'Exact container deletion not proven.' }
    }
    Set-Location -LiteralPath $oldLocation.Path
}
if (Get-NetTCPConnection -LocalPort 55437 -State Listen -ErrorAction SilentlyContinue) { throw 'Export listener cleanup not proven.' }
Write-Output 'COACH_EXPORT_NATIVE=PASS CONTAINER_REMOVED=PASS PORT55437_CLEAR=PASS REAL_DATA=NONE'
