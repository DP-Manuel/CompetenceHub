[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$ReleaseZip,
    [switch]$ConfirmLocalOnly
)
$ErrorActionPreference = 'Stop'
if (-not $ConfirmLocalOnly) { throw 'Explicit -ConfirmLocalOnly is required; this tool never connects to the VPS.' }
$repo = Split-Path $PSScriptRoot -Parent
$archive = (Resolve-Path -LiteralPath $ReleaseZip).Path
$hash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
$output = Join-Path $repo ('release-artifacts\webapp-linux\' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Path $output -Force | Out-Null
$image = (& docker image inspect competence-hub-local-linux:20261022 --format '{{.Id}}').Trim()
if ($LASTEXITCODE -ne 0 -or $image -notmatch '^sha256:[a-f0-9]{64}$') { throw 'Build the reviewed local rehearsal image first.' }
$container = $null
$result = [ordered]@{ environment='local-disposable-Ubuntu-container'; image=$image; release_sha256=$hash; package_exit=-1; proxy_exit=-1; cleanup='NOT_RUN'; vps_changed=$false; deployment_authorized=$false }
try {
    $container = (& docker run --detach --pull never --memory 2g --cpus 2 --name "competence-hub-linux-dryrun-$([Guid]::NewGuid().ToString('N'))" $image).Trim()
    if ($LASTEXITCODE -ne 0 -or $container -notmatch '^[a-f0-9]{64}$') { throw 'Could not create owned local container.' }
    & docker cp $archive "${container}:/work/release.zip"
    if ($LASTEXITCODE -ne 0) { throw 'Local archive copy failed.' }
    foreach ($name in @('prepare_linux.py','linux_proxy_smoke.py')) {
        & docker cp (Join-Path $repo "deploy\rehearsal\$name") "${container}:/work/$name"
        if ($LASTEXITCODE -ne 0) { throw 'Local rehearsal-tool copy failed.' }
    }
    & docker exec $container touch /work/LOCAL_REHEARSAL_ONLY
    if ($LASTEXITCODE -ne 0) { throw 'Local guard setup failed.' }
    & docker exec $container python3 /work/prepare_linux.py $hash
    $result.package_exit = $LASTEXITCODE
    if ($result.package_exit -eq 0) {
        & docker network disconnect bridge $container
        if ($LASTEXITCODE -ne 0) { throw 'Could not isolate local runtime networking.' }
        & docker exec $container /opt/competence-hub/current/venv/bin/python /work/linux_proxy_smoke.py
        $result.proxy_exit = $LASTEXITCODE
    }
    foreach ($name in @('package-result.json','proxy-result.json','preparation-failure.json','wheelhouse')) {
        & docker cp "${container}:/work/$name" $output 2>$null
    }
    if ($result.package_exit -ne 0 -or $result.proxy_exit -ne 0) { throw 'Local Linux gate failed; inspect sanitized result files.' }
}
finally {
    if ($container -match '^[a-f0-9]{64}$') {
        & docker rm --force $container
        $result.cleanup = if ($LASTEXITCODE -eq 0) { 'PASS' } else { 'FAIL' }
    }
    $result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'local-summary.json') -Encoding UTF8
    Write-Host "Sanitized local evidence: $output"
}
if ($result.cleanup -ne 'PASS') { throw 'Owned local container cleanup is unproven.' }
Write-Host 'LOCAL_LINUX=PASS PACKAGE=PASS PROXY_AUTH=PASS CONTAINER_REMOVED=PASS VPS_UNCHANGED=PASS'
