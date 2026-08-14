[CmdletBinding()]
param(
    [int]$LocalPort = 55432
)

$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Webapp virtual environment not found. Run the documented local setup first."
}

$appPassword = Read-Host "Password for competence_hub_app" -AsSecureString
$migratorPassword = Read-Host "Password for competence_hub_migrator" -AsSecureString
$appPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($appPassword)
$migratorPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($migratorPassword)

try {
    $appPlain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($appPointer)
    $migratorPlain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($migratorPointer)
    $appEncoded = [Uri]::EscapeDataString($appPlain)
    $migratorEncoded = [Uri]::EscapeDataString($migratorPlain)

    $env:COMPETENCE_HUB_TEST_APP_DATABASE_URL =
        "postgresql+asyncpg://competence_hub_app:${appEncoded}@127.0.0.1:${LocalPort}/competence_hub_staging"
    $env:COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL =
        "postgresql+asyncpg://competence_hub_migrator:${migratorEncoded}@127.0.0.1:${LocalPort}/competence_hub_staging"

    & $python -m pytest -m staging_integration `
        tests/test_staging_session_integration.py `
        tests/test_staging_login_integration.py `
        tests/test_staging_mfa_integration.py `
        tests/test_staging_outbox_integration.py
    if ($LASTEXITCODE -ne 0) {
        throw "Staging integration test failed with exit code $LASTEXITCODE."
    }
}
finally {
    Remove-Item Env:COMPETENCE_HUB_TEST_APP_DATABASE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL -ErrorAction SilentlyContinue
    $appPlain = $null
    $migratorPlain = $null
    if ($appPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($appPointer)
    }
    if ($migratorPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($migratorPointer)
    }
}
