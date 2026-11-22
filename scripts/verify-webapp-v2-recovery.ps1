[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Archive,
    [Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{64}$')][string]$Sha256,
    [Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{40}$')][string]$Commit,
    [Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{64}$')][string]$SourceEvidenceSha256
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$archiveFile = Get-Item -LiteralPath $Archive
if ($archiveFile.PSIsContainer -or $archiveFile.Attributes -band [IO.FileAttributes]::ReparsePoint -or
    (Get-FileHash -LiteralPath $archiveFile.FullName).Hash -ne $Sha256) { throw 'Exact regular archive required.' }
$name = 'ch-v2-recovery-' + [Guid]::NewGuid().ToString('N')
$owned = [System.Collections.Generic.List[string]]::new()
$linux = 'sha256:17228a886f219fb43029846aa744aa7b5a2e7885cb1dae7a8efcb55519e16543'
$crypto = 'sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825'
$base = @('run', '--rm', '--network', 'none', '--pull', 'never', '-e', 'CH_V2_OWN_DISPOSABLE_CONTAINER=1',
    '-e', 'PYTHONDONTWRITEBYTECODE=1', '--mount', "type=bind,source=$root\deploy\v2,target=/tools,readonly")
$app = @('--mount', "type=bind,source=$($archiveFile.FullName),target=/release.zip,readonly",
    '--mount', "type=bind,source=$root\apps\webapp\database,target=/database,readonly")
$pins = @('--archive', '/release.zip', '--sha256', $Sha256, '--commit', $Commit, '--source-evidence-sha256', $SourceEvidenceSha256)

function Invoke-Docker([string[]]$Arguments) {
    & docker --host 'npipe:////./pipe/dockerDesktopLinuxEngine' @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Owned synthetic proof stopped at $($Arguments[0])." }
}

function Remove-ProofVolume([string]$Volume) {
    if (-not $owned.Contains($Volume) -or $Volume -notmatch '^ch-v2-recovery-[a-f0-9]{32}-(raw|sealed|custody|restore)$') {
        throw 'Unowned volume refused.'
    }
    Invoke-Docker @('volume', 'rm', $Volume) | Out-Null
    $owned.Remove($Volume) | Out-Null
}

try {
    foreach ($suffix in 'raw','sealed','custody','restore') {
        $volume = "$name-$suffix"
        $existing = Invoke-Docker @('volume','ls','--format','{{.Name}}','--filter',"name=$volume")
        if ($existing -contains $volume) { throw 'Fresh dedicated volume required.' }
        $created = Invoke-Docker @('volume', 'create', '--label', "competence-hub.scope=$name", $volume)
        if ($created -ne $volume) { throw 'Volume identity unconfirmed.' }
        $owned.Add($volume)
    }
    Invoke-Docker ($base + $app + @('--name', "$name-source", '--mount', "type=volume,source=$name-raw,target=/transfer",
        $linux, 'python3.12', '/tools/rehearse_v2_restore.py', 'source') + $pins)
    Invoke-Docker ($base + @('--name', "$name-seal", '--entrypoint', 'sh',
        '--mount', "type=volume,source=$name-raw,target=/input,readonly",
        '--mount', "type=volume,source=$name-sealed,target=/sealed",
        '--mount', "type=volume,source=$name-custody,target=/custody",
        $crypto, '/tools/rehearse_v2_openpgp.sh', 'seal'))
    Remove-ProofVolume "$name-raw"
    Invoke-Docker ($base + @('--name', "$name-open", '--entrypoint', 'sh',
        '--mount', "type=volume,source=$name-sealed,target=/sealed,readonly",
        '--mount', "type=volume,source=$name-custody,target=/custody,readonly",
        '--mount', "type=volume,source=$name-restore,target=/output",
        $crypto, '/tools/rehearse_v2_openpgp.sh', 'open'))
    Invoke-Docker ($base + $app + @('--name', "$name-target", '--mount', "type=volume,source=$name-restore,target=/transfer,readonly",
        $linux, 'python3.12', '/tools/rehearse_v2_restore.py', 'restore') + $pins)
} finally {
    foreach ($volume in $owned.ToArray()) { Remove-ProofVolume $volume }
    $containers = Invoke-Docker @('ps','-a','--format','{{.Names}}','--filter',"name=$name")
    $volumes = Invoke-Docker @('volume','ls','--format','{{.Name}}','--filter',"label=competence-hub.scope=$name")
    if ($containers -or $volumes) { throw 'Synthetic rehearsal resource removal not proved.' }
}
Write-Output 'INDEPENDENT_SYNTHETIC_RECOVERY=PASS; all owned containers and volumes removed'
