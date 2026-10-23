[CmdletBinding()]
param([string]$PythonPath)
$ErrorActionPreference = 'Stop'
$python = if ($PythonPath) { (Resolve-Path -LiteralPath $PythonPath).Path } else { Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe' }
$webapp = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$container = $null
$savedLocation = Get-Location
$savedPythonPath = $env:PYTHONPATH
if (Get-NetTCPConnection -LocalPort 55433 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Loopback port 55433 is occupied; refusing to reuse another database.'
}
try {
    Set-Location -LiteralPath $webapp
    $env:PYTHONPATH = Join-Path $webapp 'src'
    $env:POSTGRES_PASSWORD = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $container = (& docker run --detach --name "competence-hub-cal1-local-$([Guid]::NewGuid().ToString('N'))" `
        --publish '127.0.0.1:55433:5432' --env POSTGRES_PASSWORD `
        --tmpfs '/var/lib/postgresql/data' postgres:16-bookworm).Trim()
    if ($LASTEXITCODE -ne 0 -or $container -notmatch '^[a-f0-9]{64}$') {
        throw 'Could not create the dedicated local rehearsal container.'
    }
    $ready = $false
    for ($i = 0; $i -lt 40; $i++) {
        & docker exec $container pg_isready -U postgres 1>$null 2>$null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw 'Local PostgreSQL did not become ready.' }
    Get-Content -Raw '.\database\bootstrap-staging.sql' | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d postgres
    if ($LASTEXITCODE -ne 0) { throw 'Local bootstrap failed.' }
    Get-ChildItem '.\database\migrations' -Filter '*.sql' -File | Sort-Object Name | ForEach-Object {
        Get-Content -Raw -LiteralPath $_.FullName | & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d competence_hub_staging
        if ($LASTEXITCODE -ne 0) { throw "Existing local migration failed: $($_.Name)" }
    }
    $app = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $migrator = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    "ALTER ROLE competence_hub_app PASSWORD '$app'; ALTER ROLE competence_hub_migrator PASSWORD '$migrator';" |
        & docker exec -i $container psql -v ON_ERROR_STOP=1 -U postgres -d postgres
    if ($LASTEXITCODE -ne 0) { throw 'Local role setup failed.' }
    $env:COMPETENCE_HUB_TEST_APP_DATABASE_URL = "postgresql+asyncpg://competence_hub_app:${app}@127.0.0.1:55433/competence_hub_staging"
    $env:COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL = "postgresql+asyncpg://competence_hub_migrator:${migrator}@127.0.0.1:55433/competence_hub_staging"
    & $python '.\scripts\run-native-cal1-browser-acceptance.py' --local-container-rehearsal
    if ($LASTEXITCODE -ne 0) { throw 'Local PostgreSQL browser rehearsal failed; inspect sanitized evidence.' }
    & $python -m pytest -m staging_integration
    if ($LASTEXITCODE -ne 0) { throw 'Local PostgreSQL API regression failed.' }
}
finally {
    Remove-Item Env:POSTGRES_PASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:COMPETENCE_HUB_TEST_APP_DATABASE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL -ErrorAction SilentlyContinue
    $app = $null
    $migrator = $null
    $env:PYTHONPATH = $savedPythonPath
    if ($container -match '^[a-f0-9]{64}$') {
        & docker rm --force $container
        if ($LASTEXITCODE -ne 0) { Write-Warning 'Dedicated local rehearsal container needs cleanup.' }
    }
    Set-Location -LiteralPath $savedLocation.Path
}
