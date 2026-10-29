[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$PythonPath, [switch]$Browser, [switch]$UpgradeOnly)
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path -LiteralPath $PythonPath).Path
$webapp = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$oldPath = $env:PYTHONPATH
$oldLocation = Get-Location
$container = $null
$names = @('POSTGRES_PASSWORD','COMPETENCE_HUB_COACH_TARGET_LOCAL_DATABASE_URL','COMPETENCE_HUB_COACH_TARGET_LOCAL_OWNER_URL')
foreach ($name in $names) {
    if (Test-Path -LiteralPath "Env:$name") { throw "Existing $name will not be replaced." }
}
if (Get-NetTCPConnection -LocalPort 55436 -State Listen -ErrorAction SilentlyContinue) { throw 'Owned local target port55436 must be unused.' }
try {
    Set-Location -LiteralPath $webapp
    $env:POSTGRES_PASSWORD = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $container = (& docker run --detach --pull never --name "competence-hub-target-local-$([Guid]::NewGuid().ToString('N'))" --publish '127.0.0.1:55436:5432' --env POSTGRES_PASSWORD --tmpfs '/var/lib/postgresql/data' postgres:16-bookworm).Trim()
    if ($LASTEXITCODE -ne 0 -or $container -notmatch '^[a-f0-9]{64}$') { throw 'Owned local container failed.' }
    $ready = $false
    for ($i=0; $i -lt 60; $i++) {
        & docker exec $container pg_isready -U postgres 1>$null 2>$null
        if ($LASTEXITCODE -eq 0) { $ready=$true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw 'Local PostgreSQL unavailable.' }
    Get-Content -Raw '.\database\bootstrap-staging.sql' | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Local bootstrap failed.' }
    $migrations = @(Get-ChildItem '.\database\migrations' -Filter '*.sql' -File | Where-Object Name -Match '^000[1-9]_' | Sort-Object Name)
    if ($migrations.Count -ne 9) { throw 'Expected nine local migrations.' }
    foreach ($migration in $migrations) {
        if (-not $Browser -and $migration.Name -like '0009_*') { continue }
        Get-Content -Raw -LiteralPath $migration.FullName | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d competence_hub_staging 1>$null
        if ($LASTEXITCODE -ne 0) { throw "Local migration failed: $($migration.Name)" }
    }
    $password = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    "ALTER ROLE competence_hub_app PASSWORD '$password'; ALTER ROLE competence_hub_migrator PASSWORD '$password';" | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Local role initialization failed.' }
    $env:COMPETENCE_HUB_COACH_TARGET_LOCAL_DATABASE_URL = "postgresql+asyncpg://competence_hub_app:${password}@127.0.0.1:55436/competence_hub_staging"
    $env:COMPETENCE_HUB_COACH_TARGET_LOCAL_OWNER_URL = "postgresql+asyncpg://competence_hub_migrator:${password}@127.0.0.1:55436/competence_hub_staging"
    $env:PYTHONPATH = (Join-Path $webapp 'src') + ';' + $webapp
    if ($Browser) { & $python -u scripts/run-coach-target-acceptance.py }
    elseif ($UpgradeOnly) { & $python -m pytest -q -s -o addopts='' tests/test_coach_target_postgres_local.py }
    else { & $python -m pytest -q -s -o addopts='' tests/test_coach_target_postgres_local.py tests/test_coach_target_import.py }
    if ($LASTEXITCODE -ne 0) { throw 'Local target gate failed.' }
}
finally {
    $env:PYTHONPATH = $oldPath
    foreach ($name in $names) { Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue }
    $password = $null
    if ($container -match '^[a-f0-9]{64}$') {
        & docker rm --force $container 1>$null
        if ($LASTEXITCODE -ne 0) { throw 'Owned target container cleanup failed.' }
    }
    Set-Location -LiteralPath $oldLocation.Path
}
Write-Output 'COACH_TARGET_LOCAL=PASS CONTAINER_REMOVED=PASS SYNTHETIC_RESIDUE=ZERO SERVER_UNCHANGED=PASS'
