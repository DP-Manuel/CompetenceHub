[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Archive,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-f]{64}$')][string]$Sha256,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-f]{40}$')][string]$Commit,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-f]{64}$')][string]$SourceEvidenceSha256
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$archiveFile = Get-Item -LiteralPath $Archive
if ($archiveFile.PSIsContainer -or $archiveFile.Attributes -band [IO.FileAttributes]::ReparsePoint) {
    throw 'Provide the regular release ZIP; links and directories are not accepted.'
}
$tools = Join-Path $root 'deploy/v2'
$name = 'ch-v2-package-proof-' + [Guid]::NewGuid().ToString('N')
$image = 'sha256:17228a886f219fb43029846aa744aa7b5a2e7885cb1dae7a8efcb55519e16543'
$elapsed = [Diagnostics.Stopwatch]::StartNew()
& docker run --rm --pull never --network none --name $name --label com.competencehub.scope=v2-release-tooling `
    --mount "type=bind,source=$($archiveFile.FullName),target=/release.zip,readonly" `
    --mount "type=bind,source=$tools,target=/v2-tools,readonly" `
    --env PYTHONDONTWRITEBYTECODE=1 $image python3.12 /v2-tools/v2_host.py linux-verify `
    --archive /release.zip --sha256 $Sha256 --commit $Commit --source-evidence-sha256 $SourceEvidenceSha256
if ($LASTEXITCODE -ne 0) { throw 'V2 Linux package proof stopped. Do not pull or substitute an image automatically.' }
$remaining = & docker ps -a --filter "name=^/$name$" --format '{{.Names}}'
if ($LASTEXITCODE -ne 0 -or $remaining) { throw 'Could not prove removal of the owned verification container.' }
Write-Output ('V2_LINUX_PACKAGE_ELAPSED_SECONDS={0:N1}; owned container removed' -f $elapsed.Elapsed.TotalSeconds)
