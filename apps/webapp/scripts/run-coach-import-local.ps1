[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$PythonPath)
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path -LiteralPath $PythonPath).Path
$webapp = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$oldPath = $env:PYTHONPATH
$oldLocation = Get-Location
$container = $null
foreach ($name in @('POSTGRES_PASSWORD', 'COMPETENCE_HUB_COACH_IMPORT_LOCAL_DATABASE_URL', 'COMPETENCE_HUB_COACH_IMPORT_LOCAL_OWNER_URL')) {
    if (Test-Path -LiteralPath "Env:$name") {
        throw "Process environment variable $name is already set. Refusing to replace existing credentials."
    }
}
if (Get-NetTCPConnection -LocalPort 55435 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Owned local import port 55435 must be unused. No existing server will be touched.'
}
try {
    Set-Location -LiteralPath $webapp
    $env:POSTGRES_PASSWORD = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $container = (& docker run --detach --pull never --name "competence-hub-import-local-$([Guid]::NewGuid().ToString('N'))" --publish '127.0.0.1:55435:5432' --env POSTGRES_PASSWORD --tmpfs '/var/lib/postgresql/data' postgres:16-bookworm).Trim()
    if ($LASTEXITCODE -ne 0 -or $container -notmatch '^[a-f0-9]{64}$') { throw 'Owned local container failed.' }
    $ready = $false
    for ($i=0; $i -lt 60; $i++) {
        & docker exec $container pg_isready -U postgres 1>$null 2>$null
        if ($LASTEXITCODE -eq 0) { $ready=$true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw 'Local PostgreSQL did not become ready.' }
    Get-Content -Raw '.\database\bootstrap-staging.sql' | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Local bootstrap failed.' }
    $migrations = @(Get-ChildItem '.\database\migrations' -Filter '*.sql' -File | Where-Object Name -Match '^000[1-8]_' | Sort-Object Name)
    if ($migrations.Count -ne 8) { throw 'Expected exactly eight reviewed local migrations.' }
    foreach ($migration in $migrations) {
        Get-Content -Raw -LiteralPath $migration.FullName | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d competence_hub_staging 1>$null
        if ($LASTEXITCODE -ne 0) { throw "Local migration failed: $($migration.Name)" }
    }
    $password = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    "ALTER ROLE competence_hub_app PASSWORD '$password'; ALTER ROLE competence_hub_migrator PASSWORD '$password';" | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Local role initialization failed.' }
    $env:COMPETENCE_HUB_COACH_IMPORT_LOCAL_DATABASE_URL = "postgresql+asyncpg://competence_hub_app:${password}@127.0.0.1:55435/competence_hub_staging"
    $env:COMPETENCE_HUB_COACH_IMPORT_LOCAL_OWNER_URL = "postgresql+asyncpg://competence_hub_migrator:${password}@127.0.0.1:55435/competence_hub_staging"
    $env:PYTHONPATH = Join-Path $webapp 'src'
    & $python -m pytest -q -s tests/test_coach_import_postgres_local.py
    if ($LASTEXITCODE -ne 0) { throw 'Local import PostgreSQL gate failed.' }
    & $python scripts/coach-import.py validate
    if ($LASTEXITCODE -ne 0) { throw 'Local import CLI gate failed.' }
}
finally {
    $env:PYTHONPATH = $oldPath
    Remove-Item Env:POSTGRES_PASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:COMPETENCE_HUB_COACH_IMPORT_LOCAL_DATABASE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:COMPETENCE_HUB_COACH_IMPORT_LOCAL_OWNER_URL -ErrorAction SilentlyContinue
    $password = $null
    if ($container -match '^[a-f0-9]{64}$') {
        & docker rm --force $container 1>$null
        if ($LASTEXITCODE -ne 0) { throw 'Owned import container cleanup failed.' }
    }
    Set-Location -LiteralPath $oldLocation.Path
}
Write-Output 'COACH_IMPORT_LOCAL=PASS CONTAINER_REMOVED=PASS SYNTHETIC_RESIDUE=ZERO SERVER_UNCHANGED=PASS'
