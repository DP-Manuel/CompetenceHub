[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 8443
)

$ErrorActionPreference = "Stop"
$workspace = Split-Path -Parent $PSScriptRoot
$python = Join-Path $workspace ".venv\Scripts\python.exe"
$serverScript = Join-Path $PSScriptRoot "browser_acceptance_app.py"
$edgeCandidates = @(
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)
$edge = $edgeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not (Test-Path -LiteralPath $python)) {
    throw "Webapp virtual environment not found. Run the documented local setup first."
}
if (-not $edge) {
    throw "Microsoft Edge was not found on this workstation."
}
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    throw "Local port $Port is already in use. Choose another port with -Port."
}

$runRoot = Join-Path ([IO.Path]::GetTempPath()) (
    "competence-hub-browser-acceptance-" + [guid]::NewGuid().ToString("N")
)
$certificateDirectory = Join-Path $runRoot "certificate"
$profileDirectory = Join-Path $runRoot "edge-profile"
$stdout = Join-Path $runRoot "server.out.log"
$stderr = Join-Path $runRoot "server.err.log"
$server = $null
$browser = $null

New-Item -ItemType Directory -Path $certificateDirectory -Force | Out-Null
New-Item -ItemType Directory -Path $profileDirectory -Force | Out-Null

try {
    $serverStart = @{
        FilePath = $python
        ArgumentList = @(
            $serverScript,
            "--port", "$Port",
            "--certificate-directory", $certificateDirectory
        )
        WorkingDirectory = $workspace
        WindowStyle = "Hidden"
        RedirectStandardOutput = $stdout
        RedirectStandardError = $stderr
        PassThru = $true
    }
    $server = Start-Process @serverStart

    $url = "https://127.0.0.1:$Port/portal/"
    $ready = $false
    foreach ($attempt in 1..30) {
        Start-Sleep -Milliseconds 300
        & curl.exe --insecure --silent --fail $url | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $ready = $true
            break
        }
        if ($server.HasExited) {
            break
        }
    }
    if (-not $ready) {
        $details = Get-Content -LiteralPath $stderr -ErrorAction SilentlyContinue
        throw "Synthetic portal did not become ready. $details"
    }

    Write-Host ""
    Write-Host "Synthetic Competence Hub browser acceptance" -ForegroundColor Cyan
    Write-Host "URL: $url"
    Write-Host "Existing-MFA user: synthetic.internal@example.invalid"
    Write-Host "Enrollment user:   synthetic.enrollment@example.invalid"
    Write-Host "Password:          Synthetic-Portal-2026!"
    Write-Host "TOTP code:         123456"
    Write-Host "Recovery code:     AAAA-BBBB-CCCC-DDDD"
    Write-Host ""
    Write-Host "Only example.invalid identities and volatile in-memory records are used."
    Write-Host "Use Edge DevTools device emulation for an exact 390 px viewport."
    Write-Host "Use this isolated Edge window only for the local acceptance test."
    Write-Host "Close the Edge window before returning here and pressing Enter."

    $browserStart = @{
        FilePath = $edge
        ArgumentList = @(
            "--new-window",
            "--ignore-certificate-errors",
            "--user-data-dir=$profileDirectory",
            $url
        )
        PassThru = $true
    }
    $browser = Start-Process @browserStart

    Read-Host "Press Enter after completing the checklist and closing Edge"
}
finally {
    if ($browser -and -not $browser.HasExited) {
        Stop-Process -Id $browser.Id -Force -ErrorAction SilentlyContinue
        $browser.WaitForExit(5000) | Out-Null
    }
    if ($server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
        $server.WaitForExit(5000) | Out-Null
    }
    if (Test-Path -LiteralPath $runRoot) {
        $resolvedRunRoot = (Resolve-Path -LiteralPath $runRoot).Path
        $expectedPrefix = [IO.Path]::GetFullPath(
            (Join-Path ([IO.Path]::GetTempPath()) "competence-hub-browser-acceptance-")
        )
        if (-not $resolvedRunRoot.StartsWith($expectedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove unexpected temporary path: $resolvedRunRoot"
        }
        Remove-Item -LiteralPath $resolvedRunRoot -Recurse -Force
    }
}
