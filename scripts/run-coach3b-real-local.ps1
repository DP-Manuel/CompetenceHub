[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$webapp = Join-Path $root 'apps\webapp'
$python = Join-Path $webapp '.venv\Scripts\python.exe'
$names = @('POSTGRES_PASSWORD','COMPETENCE_HUB_COACH3B_LOCAL_APP_URL','COMPETENCE_HUB_COACH3B_LOCAL_OWNER_URL','COMPETENCE_HUB_COACH3B_LOCAL_NONCE')
$savedPath = $env:PYTHONPATH
$savedLocation = Get-Location
$container = $null
foreach ($name in $names) {
    if (Test-Path -LiteralPath "Env:$name") { throw "Existing $name must not be replaced." }
}
if (Get-NetTCPConnection -LocalPort 55432 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port55432 must be unused; never reuse a VPS tunnel for the local rehearsal.'
}
$endpoint = & docker context inspect --format '{{json .Endpoints.docker.Host}}'
if ($LASTEXITCODE -ne 0 -or $endpoint -cnotmatch '^"npipe:////\./pipe/(docker_engine|dockerDesktopLinuxEngine)"$') { throw 'Local Docker Desktop engine required; never use a remote context.' }
try {
    Set-Location -LiteralPath $webapp
    $env:POSTGRES_PASSWORD = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $container = (& docker run --detach --pull never --name "competence-hub-coach3b-local-$([Guid]::NewGuid().ToString('N'))" --publish '127.0.0.1:55432:5432' --env POSTGRES_PASSWORD --tmpfs '/var/lib/postgresql/data' postgres:16-bookworm).Trim()
    if ($LASTEXITCODE -ne 0 -or $container -notmatch '^[a-f0-9]{64}$') { throw 'Owned local container failed.' }
    $ready = $false
    for ($i=0; $i -lt 60; $i++) {
        & docker exec $container pg_isready -U postgres 1>$null 2>$null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw 'Owned local PostgreSQL did not become ready.' }
    Get-Content -Raw -LiteralPath '.\database\bootstrap-staging.sql' | & docker exec -i $container psql -X -v ON_ERROR_STOP=1 -U postgres -d postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic bootstrap failed.' }
    $env:COMPETENCE_HUB_COACH3B_LOCAL_NONCE = [Guid]::NewGuid().ToString('N')
    "COMMENT ON DATABASE competence_hub_staging IS 'synthetic-coach3b-owned:$env:COMPETENCE_HUB_COACH3B_LOCAL_NONCE';" | & docker exec -i $container psql -X -v ON_ERROR_STOP=1 -U postgres -d postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Owned synthetic database marker failed.' }
    $migrations = @(Get-ChildItem -LiteralPath '.\database\migrations' -Filter '*.sql' -File | Where-Object Name -Match '^000[1-9]_' | Sort-Object Name)
    if ($migrations.Count -ne 9) { throw 'Exactly nine reviewed local migrations required.' }
    foreach ($migration in $migrations) {
        Get-Content -Raw -LiteralPath $migration.FullName | & docker exec -i $container psql -X -v ON_ERROR_STOP=1 -U postgres -d competence_hub_staging 1>$null
        if ($LASTEXITCODE -ne 0) { throw "Synthetic migration failed: $($migration.Name)" }
    }
    $password = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    "ALTER ROLE competence_hub_app PASSWORD '$password'; ALTER ROLE competence_hub_migrator PASSWORD '$password';" | & docker exec -i $container psql -X -v ON_ERROR_STOP=1 -U postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic role initialization failed.' }
    $env:COMPETENCE_HUB_COACH3B_LOCAL_APP_URL = "postgresql+asyncpg://competence_hub_app:${password}@127.0.0.1:55432/competence_hub_staging"
    $env:COMPETENCE_HUB_COACH3B_LOCAL_OWNER_URL = "postgresql+asyncpg://competence_hub_migrator:${password}@127.0.0.1:55432/competence_hub_staging"
    $env:PYTHONPATH = (Join-Path $webapp 'src') + ';' + $webapp
    & $python -m pytest -o addopts='' -q -s tests/test_coach3b_real_postgres_local.py
    if ($LASTEXITCODE -ne 0) { throw 'New real-adapter synthetic PostgreSQL rehearsal failed.' }
}
finally {
    $env:PYTHONPATH = $savedPath
    foreach ($name in $names) { Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue }
    $password = $null
    if ($container -match '^[a-f0-9]{64}$') {
        & docker rm --force $container 1>$null
        if ($LASTEXITCODE -ne 0) { throw 'Owned rehearsal container removal failed.' }
        $remaining = @(& docker ps -aq --filter "id=$container")
        if ($LASTEXITCODE -ne 0 -or $remaining.Count) { throw 'Owned rehearsal container absence not proven.' }
    }
    Set-Location -LiteralPath $savedLocation.Path
}
Write-Output 'COACH3B_LOCAL_ADAPTER=PASS OWNED_CONTAINER_REMOVED=PASS REAL_DATA=NOT_USED VPS=UNCHANGED'
