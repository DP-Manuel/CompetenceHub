[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$PythonPath, [switch]$ManagementBrowser)
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path -LiteralPath $PythonPath).Path
$webapp = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$oldPath = $env:PYTHONPATH
$oldLocation = Get-Location
$container = $null
if (Get-NetTCPConnection -LocalPort 55434 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Owned local Registry port 55434 must be unused.'
}
try {
    Set-Location -LiteralPath $webapp
    $env:POSTGRES_PASSWORD = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $container = (& docker run --detach --pull never --name "competence-hub-registry-local-$([Guid]::NewGuid().ToString('N'))" --publish '127.0.0.1:55434:5432' --env POSTGRES_PASSWORD --tmpfs '/var/lib/postgresql/data' postgres:16-bookworm).Trim()
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
    $migrations = @(Get-ChildItem '.\database\migrations' -Filter '*.sql' -File | Where-Object Name -Match '^000[1-7]_' | Sort-Object Name)
    if ($migrations.Count -ne 7) { throw 'Expected exactly the seven reviewed local migrations.' }
    $migrations | ForEach-Object {
        Get-Content -Raw -LiteralPath $_.FullName | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d competence_hub_staging 1>$null
        if ($LASTEXITCODE -ne 0) { throw "Local migration failed: $($_.Name)" }
    }
    $password = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    "ALTER ROLE competence_hub_app PASSWORD '$password'; ALTER ROLE competence_hub_migrator PASSWORD '$password';" | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Local role initialization failed.' }
    $env:COMPETENCE_HUB_COACH_REGISTRY_LOCAL_DATABASE_URL = "postgresql+asyncpg://competence_hub_app:${password}@127.0.0.1:55434/competence_hub_staging"
    $env:COMPETENCE_HUB_COACH_REGISTRY_LOCAL_OWNER_URL = "postgresql+asyncpg://competence_hub_migrator:${password}@127.0.0.1:55434/competence_hub_staging"
    $env:PYTHONPATH = Join-Path $webapp 'src'
    if ($ManagementBrowser) {
        & $python -u scripts/run-coach-management-acceptance.py
    } else {
        & $python -m pytest tests/test_coach_registry_postgres_local.py
    }
    if ($LASTEXITCODE -ne 0) { throw 'Local Registry database gate failed.' }
}
finally {
    $env:PYTHONPATH = $oldPath
    Remove-Item Env:POSTGRES_PASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:COMPETENCE_HUB_COACH_REGISTRY_LOCAL_DATABASE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:COMPETENCE_HUB_COACH_REGISTRY_LOCAL_OWNER_URL -ErrorAction SilentlyContinue
    $password = $null
    if ($container -match '^[a-f0-9]{64}$') {
        & docker rm --force $container
        if ($LASTEXITCODE -ne 0) { throw 'Owned Registry container cleanup failed.' }
    }
    Set-Location -LiteralPath $oldLocation.Path
}
Write-Output 'COACH_REGISTRY_LOCAL=PASS CONTAINER_REMOVED=PASS SERVER_UNCHANGED=PASS'
