#requires -Version 7.2
# Disposable local synthetic gate only. No VPS tunnel, real keys or account data.
[CmdletBinding()]
param([switch]$NativeOperator)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$webapp = Join-Path $root 'apps/webapp'
$python = Join-Path $webapp '.venv/Scripts/python.exe'
$image = 'postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825'
$names = @('POSTGRES_PASSWORD', 'COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_APP_URL',
    'COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_OWNER_URL', 'COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_NONCE')
$savedPath = [Environment]::GetEnvironmentVariable('PYTHONPATH', 'Process')
$savedLocation = Get-Location
$container = $null
$nonce = [Guid]::NewGuid().ToString('N')
foreach ($name in $names) {
    if (Test-Path -LiteralPath "Env:$name") { throw "Existing $name must not be replaced." }
}
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Existing local webapp virtual environment required; no install is attempted.' }
if (Get-NetTCPConnection -LocalPort 55438 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 55438 must be unused; never reuse a database/tunnel listener.'
}
$probe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, 55438)
try { $probe.Start() } finally { $probe.Stop() }
$cached = & docker image inspect $image --format '{{.Id}}' 2>$null
if ($LASTEXITCODE -ne 0 -or $cached -cne 'sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825') {
    throw 'The exact reviewed PostgreSQL 16 image must already be cached; no pull is attempted.'
}
$endpoint = & docker context inspect --format '{{json .Endpoints.docker.Host}}'
if ($LASTEXITCODE -ne 0 -or $endpoint -cnotmatch '^"npipe:////\./pipe/(docker_engine|dockerDesktopLinuxEngine)"$') { throw 'Local Docker Desktop engine required; never use a remote context.' }
try {
    Set-Location -LiteralPath $webapp
    $env:POSTGRES_PASSWORD = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $env:COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_NONCE = $nonce
    $container = (& docker run --detach --pull never --name "competence-hub-initial-admin-local-$nonce" `
        --label "competence-hub-initial-admin-local-nonce=$nonce" --publish '127.0.0.1:55438:5432' `
        --env POSTGRES_PASSWORD --tmpfs '/var/lib/postgresql/data' $image).Trim()
    if ($LASTEXITCODE -ne 0 -or $container -notmatch '^[a-f0-9]{64}$') { throw 'Owned local container failed.' }
    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        & docker exec $container sh -c 'test "$(cat /proc/1/comm)" = postgres && pg_isready -U postgres' 1>$null 2>$null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw 'Owned local PostgreSQL did not become ready.' }
    Get-Content -Raw -LiteralPath './database/bootstrap-staging.sql' | & docker exec -i $container psql -X -v ON_ERROR_STOP=1 -U postgres -d postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic bootstrap failed.' }
    "COMMENT ON DATABASE competence_hub_staging IS 'synthetic-initial-admin-owned:$nonce';" |
        & docker exec -i $container psql -X -v ON_ERROR_STOP=1 -U postgres -d postgres 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'Owned synthetic database marker failed.' }
    $migrations = @(Get-ChildItem -LiteralPath './database/migrations' -Filter '*.sql' -File |
        Where-Object Name -Match '^000[1-9]_' | Sort-Object Name)
    if ($migrations.Count -ne 9) { throw 'Exactly nine reviewed local migrations required.' }
    foreach ($migration in $migrations) {
        Get-Content -Raw -LiteralPath $migration.FullName |
            & docker exec -i $container psql -X -v ON_ERROR_STOP=1 -U postgres -d competence_hub_staging 1>$null
        if ($LASTEXITCODE -ne 0) { throw "Synthetic migration failed: $($migration.Name)" }
    }
    $password = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    "ALTER ROLE competence_hub_app PASSWORD '$password'; ALTER ROLE competence_hub_migrator PASSWORD '$password';" |
        & docker exec -i $container psql -X -v ON_ERROR_STOP=1 -U postgres 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic role initialization failed.' }
    $env:COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_APP_URL = "postgresql+asyncpg://competence_hub_app:${password}@127.0.0.1:55438/competence_hub_staging"
    $env:COMPETENCE_HUB_INITIAL_ADMIN_LOCAL_OWNER_URL = "postgresql+asyncpg://competence_hub_migrator:${password}@127.0.0.1:55438/competence_hub_staging"
    $env:PYTHONPATH = (Join-Path $webapp 'src') + ';' + $webapp
    $testFiles = @('tests/test_initial_admin_postgres_local.py')
    if ($NativeOperator) { $testFiles += 'tests/test_staging_admin_operator_native_local.py' }
    & $python -m pytest -o addopts='' -q --tb=short @testFiles
    if ($LASTEXITCODE -ne 0) { throw 'Initial-admin synthetic PostgreSQL gate failed.' }
} finally {
    if ($null -eq $savedPath) { [Environment]::SetEnvironmentVariable('PYTHONPATH', [NullString]::Value, 'Process') }
    else { [Environment]::SetEnvironmentVariable('PYTHONPATH', $savedPath, 'Process') }
    foreach ($name in $names) { Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue }
    $password = $null
    try {
        if ($container -match '^[a-f0-9]{64}$') {
            $label = & docker inspect --format '{{index .Config.Labels "competence-hub-initial-admin-local-nonce"}}' $container
            if ($LASTEXITCODE -ne 0 -or $label -cne $nonce) { throw 'Container ownership label is unproven; no removal attempted.' }
            & docker rm --force $container 1>$null
            if ($LASTEXITCODE -ne 0) { throw 'Owned rehearsal container removal failed.' }
            $remaining = @(& docker ps -aq --filter "id=$container")
            if ($LASTEXITCODE -ne 0 -or $remaining.Count) { throw 'Owned rehearsal container absence not proven.' }
            Write-Output 'OWNED_INITIAL_ADMIN_CONTAINER_REMOVED=PASS'
        }
    } finally { Set-Location -LiteralPath $savedLocation.Path }
}
Write-Output 'INITIAL_ADMIN_LOCAL=PASS REAL_DATA=NOT_USED VPS=UNCHANGED'
