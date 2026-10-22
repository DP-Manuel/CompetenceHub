[CmdletBinding()]
param([ValidateRange(1024,65535)][int]$LocalPort = 55432)
$ErrorActionPreference = 'Stop'
$webapp = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $webapp '.venv\Scripts\python.exe'
$evidence = Join-Path $webapp '..\..\release-artifacts\cal1-native-ui-20261022'
$sshOptions = @('-o','BatchMode=yes','-o','PasswordAuthentication=no','-o','StrictHostKeyChecking=yes',
    '-o','ConnectTimeout=10','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=3')
$hostTarget = 'manuel@217.160.255.86'
$ownedTunnel = $null
$appPointer = [IntPtr]::Zero
$migratorPointer = [IntPtr]::Zero
$cleanupVerified = $false
$savedLocation = Get-Location

function Get-ServiceEvidence {
    $active = @(& ssh @sshOptions $hostTarget 'systemctl is-active dp-chatbot.service nginx.service fail2ban.service postgresql.service')
    if ($LASTEXITCODE -ne 0 -or $active.Count -ne 4 -or @($active | Where-Object { $_ -ne 'active' }).Count) {
        throw 'Service health failed. Do not restart or modify any service.'
    }
    $listeners = @(& ssh @sshOptions $hostTarget "ss -ltnH 'sport = :5432'")
    if ($LASTEXITCODE -ne 0 -or $listeners.Count -eq 0) { throw 'PostgreSQL listener check failed.' }
    foreach ($line in $listeners) {
        $address = ($line.Trim() -split '\s+')[3]
        if ($address -notmatch '^(127\.0\.0\.1|\[::1\]|::1):5432$') {
            throw 'PostgreSQL is not exclusively listening on loopback.'
        }
    }
    return [pscustomobject]@{ services = $active; postgres_listeners = $listeners; status = 'PASS' }
}

try {
    if (-not (Test-Path -LiteralPath $python)) { throw 'Existing webapp virtual environment is required.' }
    New-Item -ItemType Directory -Path $evidence -Force | Out-Null
    Set-Location -LiteralPath $webapp
    $preflight = Get-ServiceEvidence
    $preflight | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $evidence 'service-preflight.json') -Encoding UTF8
    if (Get-NetTCPConnection -LocalPort $LocalPort -State Listen -ErrorAction SilentlyContinue) {
        $probe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, 0)
        $probe.Start()
        $LocalPort = $probe.LocalEndpoint.Port
        $probe.Stop()
        Write-Host "Existing tunnel left untouched; using dedicated loopback port $LocalPort."
    }
    $ownedTunnel = Start-Process -FilePath 'ssh.exe' -WindowStyle Hidden -PassThru `
        -ArgumentList ($sshOptions + @('-o','ExitOnForwardFailure=yes','-N','-L',"127.0.0.1:${LocalPort}:127.0.0.1:5432",$hostTarget))
    $listening = $false
    for ($i = 0; $i -lt 40; $i++) {
        if ($ownedTunnel.HasExited) { throw 'Dedicated key-authenticated tunnel stopped.' }
        $listener = Get-NetTCPConnection -LocalPort $LocalPort -State Listen -ErrorAction SilentlyContinue
        if ($listener -and $listener.OwningProcess -contains $ownedTunnel.Id) { $listening = $true; break }
        Start-Sleep -Milliseconds 250
    }
    if (-not $listening) { throw 'Dedicated tunnel did not become ready.' }
    Write-Host 'STAGING WINDOW OPEN. Enter DB passwords only at the hidden prompts. Never paste them into chat.'
    $appPassword = Read-Host 'Password for competence_hub_app' -AsSecureString
    $migratorPassword = Read-Host 'Password for competence_hub_migrator' -AsSecureString
    $appPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($appPassword)
    $migratorPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($migratorPassword)
    $appEncoded = [Uri]::EscapeDataString([Runtime.InteropServices.Marshal]::PtrToStringBSTR($appPointer))
    $migratorEncoded = [Uri]::EscapeDataString([Runtime.InteropServices.Marshal]::PtrToStringBSTR($migratorPointer))
    $env:COMPETENCE_HUB_TEST_APP_DATABASE_URL = "postgresql+asyncpg://competence_hub_app:${appEncoded}@127.0.0.1:${LocalPort}/competence_hub_staging"
    $env:COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL = "postgresql+asyncpg://competence_hub_migrator:${migratorEncoded}@127.0.0.1:${LocalPort}/competence_hub_staging"
    & $python '.\scripts\run-native-cal1-browser-acceptance.py'
    $browserExit = $LASTEXITCODE
    $result = Get-Content -Raw -LiteralPath (Join-Path $evidence 'result.json') | ConvertFrom-Json
    if ($result.cleanup -eq 'PASS') {
        if ($browserExit -eq 0) {
            & $python -m pytest -m staging_integration
            $apiExit = $LASTEXITCODE
        } else { $apiExit = -1 }
        & $python '.\scripts\verify-staging-zero-residue.py'
        $zeroExit = $LASTEXITCODE
        $postflight = Get-ServiceEvidence
        $postflight | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $evidence 'service-postflight.json') -Encoding UTF8
        $cleanupVerified = $zeroExit -eq 0
        & $python -m pytest -m 'not staging_integration'
        $localExit = $LASTEXITCODE
        & $python -m compileall -q src tests scripts
        $compileExit = $LASTEXITCODE
        & $python -m pip check
        $pipExit = $LASTEXITCODE
        & (Join-Path $webapp '..\..\tools\node-v22.16.0-win-x64\node.exe') --check '.\src\competence_hub_api\portal_ui\app.js'
        $jsExit = $LASTEXITCODE
        & git diff --check
        $diffExit = $LASTEXITCODE
        [pscustomobject]@{
            native_browser_exit = $browserExit; native_api_exit = $apiExit
            zero_residue_exit = $zeroExit; service_health = $postflight.status
            local_suite_exit = $localExit; compile_exit = $compileExit
            pip_check_exit = $pipExit; js_syntax_exit = $jsExit; diff_check_exit = $diffExit
        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $evidence 'batch-summary.json') -Encoding UTF8
        if ($localExit -ne 0 -or $compileExit -ne 0 -or $pipExit -ne 0 -or $jsExit -ne 0 -or $diffExit -ne 0) {
            throw 'Local post-regression did not pass. Native cleanup/health evidence remains recorded.'
        }
        if ($browserExit -ne 0 -or $apiExit -ne 0 -or $zeroExit -ne 0) {
            throw 'Batch did not pass every gate. Cleanup/health evidence was collected; do not mark acceptance complete.'
        }
        Write-Host 'NATIVE_UI=PASS API=PASS CLEANUP=PASS ZERO_RESIDUE=PASS SERVICES=PASS POSTGRES_LOCALHOST=PASS'
    } else {
        throw 'Cleanup was not proven. Dedicated tunnel remains open; inspect sanitized evidence before any further test.'
    }
}
finally {
    Remove-Item Env:COMPETENCE_HUB_TEST_APP_DATABASE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL -ErrorAction SilentlyContinue
    $appEncoded = $null
    $migratorEncoded = $null
    $appPassword = $null
    $migratorPassword = $null
    if ($appPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($appPointer) }
    if ($migratorPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($migratorPointer) }
    if ($ownedTunnel -and -not $ownedTunnel.HasExited) {
        if ($cleanupVerified) { Stop-Process -Id $ownedTunnel.Id }
        else { Write-Warning "Tunnel PID $($ownedTunnel.Id) intentionally retained until cleanup/health are proven." }
    }
    Set-Location -LiteralPath $savedLocation.Path
}
