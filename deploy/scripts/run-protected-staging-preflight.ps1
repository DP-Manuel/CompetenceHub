#requires -Version 7.2
<#
Read-only prerequisite for Manuel's approved private Staging window.
No backup, restore, install, GPG, key read, migration or account action.
Only one hidden sudo prompt if the existing noninteractive authorization fails.
#>
[CmdletBinding()]
param([string]$ExpectedSourceCommit)
$ErrorActionPreference = 'Stop'

function Invoke-PrivateReadCommand {
    param([string]$File, [string[]]$Arguments, [Security.SecureString]$InputSecret)
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $File
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    foreach ($argument in $Arguments) { $start.ArgumentList.Add($argument) }
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    $pointer = [IntPtr]::Zero
    try {
        $null = $process.Start()
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if ($InputSecret) {
            $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($InputSecret)
            $process.StandardInput.WriteLine([Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer))
        }
        $process.StandardInput.Close()
        if (-not $process.WaitForExit(120000)) { throw 'PRIVATE_READ_TIMEOUT' }
        $output = $stdout.GetAwaiter().GetResult()
        $null = $stderr.GetAwaiter().GetResult()
        return @{ exit = $process.ExitCode; output = $output }
    } finally {
        if ($pointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
        if ($process.Id -and -not $process.HasExited) { $process.Kill($true); $process.WaitForExit() }
        $process.Dispose()
    }
}

function Assert-PreflightVolume {
    param($Volume)
    if ($Volume.volume -cne 'FullyEncrypted' -or $Volume.protection -cne 'On' -or $Volume.lock -cne 'Unlocked') {
        throw 'LOCAL_ENCRYPTED_TARGET_NOT_VERIFIED'
    }
    if ([long]$Volume.free_bytes -lt 1GB) { throw 'LOCAL_TARGET_CAPACITY_INSUFFICIENT' }
}

function Invoke-ProtectedReadOnlyPreflight {
    $root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
    if ($ExpectedSourceCommit -cnotmatch '^[a-f0-9]{40}$') { throw 'EXACT_REVIEWED_COMMIT_REQUIRED' }
    $head = Invoke-PrivateReadCommand 'git' @('-C', $root, 'rev-parse', 'HEAD')
    $dirty = Invoke-PrivateReadCommand 'git' @('-C', $root, 'status', '--porcelain', '--untracked-files=all', '--', 'deploy/scripts', 'deploy/rehearsal', 'apps/webapp/src', 'apps/webapp/scripts')
    if ($head.exit -ne 0 -or $head.output.Trim() -cne $ExpectedSourceCommit -or $dirty.exit -ne 0 -or $dirty.output.Trim()) {
        throw 'SOURCE_CHANGED_NO_SERVER_ACTION'
    }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not [Security.Principal.WindowsPrincipal]::new($identity).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'SAME_USER_ELEVATED_POWERSHELL_REQUIRED'
    }
    if ([IO.Path]::GetPathRoot($root) -cne 'C:\' -or $env:USERPROFILE -ine [IO.Path]::GetFullPath((Join-Path $root '../../../..'))) {
        throw 'SAME_WINDOWS_PROFILE_REQUIRED'
    }
    # Native Windows PowerShell hosts the BitLocker module; no compatibility
    # serialization ambiguity, no protectors/recovery values and no unlock call.
    $volumeQuery = @'
$ErrorActionPreference='Stop'
try {
    $v=Get-BitLockerVolume -MountPoint 'C:'
    @{ volume=[string]$v.VolumeStatus; protection=[string]$v.ProtectionStatus;
       lock=[string]$v.LockStatus; method=[string]$v.EncryptionMethod;
       free_bytes=[IO.DriveInfo]::new('C:\').AvailableFreeSpace } | ConvertTo-Json -Compress
} catch { exit 1 }
'@
    $volumeResult = Invoke-PrivateReadCommand "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" @('-NoProfile', '-NonInteractive', '-Command', $volumeQuery)
    if ($volumeResult.exit -ne 0) { throw 'BITLOCKER_READ_UNAVAILABLE_NO_UNLOCK_ATTEMPT' }
    $volume = $volumeResult.output | ConvertFrom-Json -AsHashtable
    Assert-PreflightVolume $volume
    Write-Host 'PASS | C: fully encrypted, protection on, capacity sufficient.'
    $target = Join-Path $env:LOCALAPPDATA 'CompetenceHub/pilot-snapshots'
    # Presence/reparse check only. Do not create or alter this proposed target.
    $candidate = $target
    while ($candidate) {
        if (Test-Path -LiteralPath $candidate) {
            if ((Get-Item -Force -LiteralPath $candidate).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw 'LOCAL_TARGET_REPARSE_POINT_REJECTED'
            }
        }
        $candidate = Split-Path -Parent $candidate
    }
    $helper = Join-Path $PSScriptRoot 'staging_readonly_preflight.py'
    $bytes = [IO.File]::ReadAllBytes($helper)
    $encoded = [Convert]::ToBase64String($bytes)
    $code = "import base64;exec(compile(base64.b64decode('$encoded'),'<readonly-preflight>','exec'))"
    $ssh = @('-F', 'NUL', '-T', '-o', 'BatchMode=yes', '-o', 'PasswordAuthentication=no',
        '-o', 'KbdInteractiveAuthentication=no', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'ForwardAgent=no', '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=30',
        'manuel@217.160.255.86')
    $remote = 'python3 -I -c "' + $code + '"'
    $connection = Invoke-PrivateReadCommand 'ssh' ($ssh + @('true'))
    if ($connection.exit -ne 0) { throw 'PINNED_SSH_CONNECTION_UNAVAILABLE_NO_PASSWORD_PROMPT' }
    $result = Invoke-PrivateReadCommand 'ssh' ($ssh + @('sudo -n -- ' + $remote))
    if ($result.exit -ne 0) {
        # Separate authentication from inventory failure. Never retry a password.
        $auth = Invoke-PrivateReadCommand 'ssh' ($ssh + @('sudo -n -- true'))
        if ($auth.exit -eq 0) { throw 'PRIVATE_READONLY_INVENTORY_FAILED_NO_PASSWORD_RETRY' }
        Write-Host 'Read-only VPS inventory only. No backup, deployment, migration or accounts.'
        $password = Read-Host 'VPS sudo password for manuel (hidden; never paste into chat)' -AsSecureString
        try { $result = Invoke-PrivateReadCommand 'ssh' ($ssh + @('sudo -S -p "" -- ' + $remote)) $password }
        finally { if ($password) { $password.Dispose(); $password = $null } }
    }
    if ($result.exit -ne 0) { throw 'SUDO_OR_READONLY_INVENTORY_FAILED_NO_RETRY' }
    $inventory = $result.output | ConvertFrom-Json -AsHashtable
    if ($inventory.schema -cne 'competence-hub.readonly-staging-preflight.v1' -or $inventory.server_mutations -ne $false) {
        throw 'READONLY_REPORT_REJECTED'
    }
    $inventory.local_volume = $volume
    $inventory.source_commit = $ExpectedSourceCommit
    $inventory.backup_target = @{ proposed = '%LOCALAPPDATA%\CompetenceHub\pilot-snapshots'; created = $false; acl_qualified = $false }
    $folder = Join-Path $root 'release-artifacts/protected-staging-preflight'
    $null = New-Item -ItemType Directory -Force -Path $folder
    $report = Join-Path $folder ([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ') + '.json')
    $payload = [Text.UTF8Encoding]::new($false).GetBytes(($inventory | ConvertTo-Json -Depth 12))
    $stream = [IO.File]::Open($report, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($payload); $stream.Flush($true) } finally { $stream.Dispose() }
    Write-Host ('PREFLIGHT=' + $inventory.status + ' BACKUP=NOT_RUN RESTORE=NOT_RUN PILOT=NOT_INSTALLED SERVER_MUTATIONS=NONE')
    Write-Host ('REPORT=' + $report)
    Write-Host ('REPORT_SHA256=' + (Get-FileHash -LiteralPath $report -Algorithm SHA256).Hash)
    Write-Host 'Stop here. This report is not backup/restore or pilot acceptance; existing approval remains scoped by those gates.'
    if ($inventory.status -cne 'PASS') { return 2 }
    return 0
}

if ($MyInvocation.InvocationName -ne '.') {
    try { exit (Invoke-ProtectedReadOnlyPreflight) }
    catch {
        $safe = @('EXACT_REVIEWED_COMMIT_REQUIRED', 'SOURCE_CHANGED_NO_SERVER_ACTION',
            'SAME_USER_ELEVATED_POWERSHELL_REQUIRED', 'SAME_WINDOWS_PROFILE_REQUIRED',
            'BITLOCKER_READ_UNAVAILABLE_NO_UNLOCK_ATTEMPT', 'LOCAL_ENCRYPTED_TARGET_NOT_VERIFIED',
            'LOCAL_TARGET_CAPACITY_INSUFFICIENT', 'LOCAL_TARGET_REPARSE_POINT_REJECTED',
            'PRIVATE_READONLY_INVENTORY_FAILED_NO_PASSWORD_RETRY', 'SUDO_OR_READONLY_INVENTORY_FAILED_NO_RETRY',
            'READONLY_REPORT_REJECTED', 'PRIVATE_READ_TIMEOUT', 'PINNED_SSH_CONNECTION_UNAVAILABLE_NO_PASSWORD_PROMPT')
        $code = if ($_.Exception.Message -cin $safe) { $_.Exception.Message } else { 'PRIVATE_PREFLIGHT_NOT_COMPLETE' }
        Write-Host ('PREFLIGHT=STOP CODE=' + $code + ' SERVER_MUTATIONS=NONE')
        Write-Host 'No automatic retry, key action or server change. Send only this status or the sanitized report, never a password.'
        exit 1
    }
}
