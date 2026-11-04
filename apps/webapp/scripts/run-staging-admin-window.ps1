#requires -Version 7.2
<#
PRIVATE candidate. No execution by default, no transcripts/debug/recording.
Invoke with pwsh -NoProfile -File, never Windows PowerShell 5. Human GPG pinentry
and the Python operator's own Edge MFA/recovery window are intentional.
Readiness is NOT a backup, restore, account, deployment or real-APPLY PASS.
Partial keys, snapshots and account outcomes are retained for manual review.
#>
[CmdletBinding()]
param(
    [switch]$Execute,
    [string]$ExpectedSourceCommit,
    [switch]$AcknowledgePrivateWindow,
    [switch]$AcknowledgeQuietDatabase,
    [switch]$AcknowledgeOperatorCustody,
    [string]$RebasedStorageDirectory,
    [string]$RebasedGpgHome,
    [string]$ExpectedBackupRecipient,
    [string]$BackupDestinationDirectory,
    [long]$RequiredBackupFreeBytes,
    [switch]$AcknowledgeBackupKeyRebase
)

$script:WindowRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$script:WindowHost = 'manuel@217.160.255.86'
$script:WindowImage = 'postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825'
$script:WindowRecipient = '2E44306121629A100F76A8B08CCA3D9186A28D4C'
$script:WindowCorpusHash = '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da'
$script:WindowFiles = [ordered]@{
    'database.dump.gpg' = 'dump'; 'globals.sql.gpg' = 'globals'; 'METADATA' = 'metadata'
    'SHA256SUMS' = 'checksums'; 'COMPLETE' = 'complete'
}
$script:WindowSshOptions = @('-F', 'NUL', '-o', 'BatchMode=yes', '-o', 'PasswordAuthentication=no',
    '-o', 'KbdInteractiveAuthentication=no', '-o', 'StrictHostKeyChecking=yes', '-o', 'ForwardAgent=no',
    '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=3')

function Invoke-WindowCommand {
    param([string]$Executable, [string[]]$Arguments, [Security.SecureString]$SecureInput,
          [int]$TimeoutMilliseconds = 900000)
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $Executable; $start.UseShellExecute = $false; $start.CreateNoWindow = $true
    $start.Environment['GIT_TERMINAL_PROMPT'] = '0'; $start.Environment['GCM_INTERACTIVE'] = 'Never'
    $start.RedirectStandardInput = $true; $start.RedirectStandardOutput = $true; $start.RedirectStandardError = $true
    foreach ($argument in $Arguments) { $start.ArgumentList.Add($argument) }
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $start
    $pointer = [IntPtr]::Zero; $plain = $null; $started = $false
    try {
        $null = $process.Start(); $started = $true
        $stdout = $process.StandardOutput.ReadToEndAsync(); $stderr = $process.StandardError.ReadToEndAsync()
        if ($SecureInput) {
            $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureInput)
            $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
            $process.StandardInput.WriteLine($plain)
        }
        $process.StandardInput.Close()
        if (-not $process.WaitForExit($TimeoutMilliseconds)) { throw 'COMMAND_TIMEOUT' }
        $output = $stdout.GetAwaiter().GetResult(); $null = $stderr.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0) { throw 'COMMAND_FAILED' }
        return $output.Trim()
    } catch { throw 'SANITIZED_COMMAND_FAILURE' }
    finally {
        if ($started -and -not $process.HasExited) { $process.Kill($true); $process.WaitForExit() }
        $process.Dispose()
        if ($pointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
        $plain = $null
    }
}

function Write-WindowRecord {
    param([string]$Path, $Record)
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes(($Record | ConvertTo-Json -Depth 10))
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
}

function Assert-WindowSource {
    param([string]$Commit, [string]$Git)
    if ($Commit -cnotmatch '^[a-f0-9]{40}$') { throw 'REVIEWED_COMMIT_REQUIRED' }
    $head = Invoke-WindowCommand $Git @('-C', $script:WindowRoot, 'rev-parse', 'HEAD')
    $origin = Invoke-WindowCommand $Git @('-C', $script:WindowRoot, 'remote', 'get-url', 'origin')
    if ($head -cne $Commit -or $origin -cne 'https://github.com/DP-Manuel/CompetenceHub.git') { throw 'SOURCE_IDENTITY_REJECTED' }
    # Check every executable/import/schema/dependency surface. Non-executable
    # Windows cache artifacts and unrelated root notes are not runtime inputs.
    $dirty = Invoke-WindowCommand $Git @('-C', $script:WindowRoot, 'status', '--porcelain', '--untracked-files=all', '--',
        'apps/webapp/src', 'apps/webapp/scripts', 'apps/webapp/database', 'apps/webapp/tests',
        'apps/webapp/pyproject.toml', 'apps/webapp/requirements-build.lock', 'apps/webapp/requirements-production.lock', 'deploy/scripts')
    if ($dirty) { throw 'REVIEWED_SOURCE_MUST_BE_CLEAN_AND_TRACKED' }
    $branch = Invoke-WindowCommand $Git @('-C', $script:WindowRoot, 'symbolic-ref', '--short', 'HEAD')
    if ($branch -cnotmatch '^[a-zA-Z0-9][a-zA-Z0-9/_-]*$') { throw 'REVIEWED_BRANCH_REQUIRED' }
    $pushed = Invoke-WindowCommand $Git @('-C', $script:WindowRoot, 'ls-remote', '--exit-code', 'origin', ('refs/heads/' + $branch))
    if ($pushed -cnotmatch ('^' + $Commit + '\s+refs/heads/' + [regex]::Escape($branch) + '$')) { throw 'PUSHED_SOURCE_GATE_FAILED' }
}

function Assert-WindowPortFree {
    if (@(Get-NetTCPConnection -LocalPort 55432 -State Listen -ErrorAction SilentlyContinue).Count) {
        throw 'PORT55432_ALREADY_IN_USE_NEVER_REUSE_OR_KILL'
    }
}

function Assert-WindowNoPriorAttempt {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) { throw 'PRIOR_ACCOUNT_ATTEMPT_REQUIRES_MANUAL_RECONCILIATION_NO_RETRY' }
}

function Assert-WindowCustodyComplete {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return }
    $directory = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (-not $directory.PSIsContainer -or ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw 'CUSTODY_PATH_UNSAFE'
    }
    # Presence only: never open keys, decrypt, repair or regenerate a partial set.
    # Complete-looking sets still undergo the existing cryptographic validation.
    foreach ($name in @('staging-operator.keys.clixml', 'staging-operator.keys.json.gpg', 'staging-operator.metadata.json')) {
        $file = Join-Path $Path $name
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw 'CUSTODY_INCOMPLETE_REQUIRES_PRIVATE_RECONCILIATION'
        }
        if ((Get-Item -LiteralPath $file -Force -ErrorAction Stop).Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw 'CUSTODY_PATH_UNSAFE'
        }
    }
}

function Get-WindowStopCode {
    param([string]$Message)
    # Only exact fixed codes may leave the private error boundary, never the
    # original exception, path, subprocess diagnostics or credential values.
    $known = @(
        'CUSTODY_PATH_UNSAFE', 'CUSTODY_INCOMPLETE_REQUIRES_PRIVATE_RECONCILIATION',
        'PRIOR_ACCOUNT_ATTEMPT_REQUIRES_MANUAL_RECONCILIATION_NO_RETRY',
        'SOURCE_IDENTITY_REJECTED', 'REVIEWED_SOURCE_MUST_BE_CLEAN_AND_TRACKED',
        'PUSHED_SOURCE_GATE_FAILED', 'PORT55432_ALREADY_IN_USE_NEVER_REUSE_OR_KILL',
        'CLEAN_PRIVATE_DIAGNOSTIC_ENVIRONMENT_REQUIRED', 'CLEAN_OPERATOR_PROCESS_REQUIRED',
        'REVIEWED_INPUT_MISSING_OR_LINKED'
        'OPERATION_BLOCK_NOT_APPROVED'
        'EXPLICIT_VERIFIED_KEY_REBASE_AND_BACKUP_TARGET_REQUIRED'
        'EXPLICIT_BACKUP_RECIPIENT_REQUIRED', 'LEGACY_CUSTODY_NOT_A_REBASE'
        'REBASE_ORIGIN_AND_RECIPIENT_BINDING_REQUIRED'
        'VERIFIED_ENCRYPTED_BACKUP_TARGET_REQUIRED'
        'VERIFIED_ENCRYPTED_RESTORE_WORKSPACE_REQUIRED'
        'CURRENT_VOLUME_PROTECTION_STATUS_UNAVAILABLE'
    )
    if ($Message -cin $known) { return $Message }
    return 'PRIVATE_MANUAL_REVIEW_REQUIRED'
}

function Confirm-WindowOperation {
    param([ValidateSet('BACKUP','RESTORE','ADMIN')][string]$Block)
    if ($Block -ceq 'BACKUP') {
        Write-Host 'TARGET: manuel@217.160.255.86 / competence_hub_staging. No production DB.'
        Write-Host 'PLAN: new encrypted prechange backup and exact protected external copy; restore needs its own approval.'
        Write-Host 'BACKUP also confirms: no other operator/DDL/role/data changes during this quiet database window.'
        Write-Host 'Existing backup jobs/data stay unchanged. Rollback: retain backups; remove only owned temporary artifacts.'
    } elseif ($Block -ceq 'RESTORE') {
        Write-Host 'TARGET: owned isolated local PostgreSQL container, network none. Never replace Staging or replay cluster roles.'
        Write-Host 'PLAN: verify exact encrypted copy, restore database/schema/owners/counts, then remove owned plaintext/container.'
        Write-Host 'Rollback: original encrypted set and live database unchanged; stop if cleanup cannot be proved.'
    } else {
        Write-Host 'TARGET: competence_hub_staging. Exactly one Manuel account with existing approved private login, admin only.'
        Write-Host 'PLAN: first account write only after current exact backup/restore; native MFA/recovery/session/logout/audit/RBAC.'
        Write-Host 'No Coach/Reviewer/Contact/Internal roles, migrations/import or deployment. Uncertain commit: STOP, no retry/delete.'
        Write-Host 'Rollback: preserve pending outcome and prechange backup; any real DB restore needs separate approval.'
    }
    $answer = Read-Host ("Approve ONLY this block by typing " + $Block + '; otherwise stop')
    if ($answer -cne $Block) { throw 'OPERATION_BLOCK_NOT_APPROVED' }
}

function Assert-WindowNoDiagnostics {
    foreach ($name in [Environment]::GetEnvironmentVariables('Process').Keys) {
        if ($name -match '^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON(INSPECT|STARTUP|BREAKPOINT|HOME|USERBASE|PATH|ASYNCIODEBUG)$)') {
            throw 'CLEAN_PRIVATE_DIAGNOSTIC_ENVIRONMENT_REQUIRED'
        }
    }
}

function Get-WindowHealth {
    param([string]$Ssh)
    $services = Invoke-WindowCommand $Ssh ($script:WindowSshOptions + @('-T', $script:WindowHost,
        'systemctl is-active dp-chatbot.service nginx.service fail2ban.service postgresql.service'))
    if (@($services -split '\r?\n').Count -ne 4 -or @($services -split '\r?\n' | Where-Object { $_ -cne 'active' }).Count) { throw 'SERVICE_HEALTH_FAILED_NO_RESTART' }
    $listeners = Invoke-WindowCommand $Ssh ($script:WindowSshOptions + @('-T', $script:WindowHost, "ss -ltnH 'sport = :5432'"))
    if (-not $listeners) { throw 'POSTGRES_LISTENER_MISSING' }
    foreach ($line in ($listeners -split '\r?\n')) {
        $fields = $line.Trim() -split '\s+'
        if ($fields.Count -lt 4 -or $fields[3] -notmatch '^(127\.0\.0\.1|\[::1\]|::1):5432$') { throw 'POSTGRES_LOOPBACK_REQUIRED' }
    }
    return @{ services = 'active'; postgres_loopback = $true; checked_at_utc = [DateTime]::UtcNow.ToString('o') }
}

function Get-WindowSnapshotPlan {
    param([Collections.IDictionary]$Record, [string]$RunId)
    if ($RunId -cnotmatch '^admin-[a-f0-9]{32}$') { throw 'UNIQUE_RUN_ID_REQUIRED' }
    $snapshot = '/var/backups/competence-hub/prechange-' + $RunId
    $expectedKeys = @('snapshot_path')
    foreach ($stem in $script:WindowFiles.Values) { $expectedKeys += $stem + '_path'; $expectedKeys += $stem + '_sha256' }
    if (@(Compare-Object @($Record.Keys) $expectedKeys).Count -or $Record.snapshot_path -cne $snapshot) { throw 'EXACT_SNAPSHOT_RECORD_REQUIRED' }
    $plan = @()
    foreach ($filename in $script:WindowFiles.Keys) {
        $stem = $script:WindowFiles[$filename]
        if ($Record[$stem + '_path'] -cne ($snapshot + '/' + $filename) -or $Record[$stem + '_sha256'] -cnotmatch '^[a-f0-9]{64}$') { throw 'SNAPSHOT_PATH_OR_HASH_REJECTED' }
        $plan += [pscustomobject]@{ name = $filename; sha256 = $Record[$stem + '_sha256'] }
    }
    return $plan
}

function Get-WindowRootScript {
    param([string]$Recipient = $script:WindowRecipient)
    if ($Recipient -cnotmatch '^[A-F0-9]{40}$' -or $Recipient -cmatch '^(.)\1{39}$') { throw 'EXPLICIT_BACKUP_RECIPIENT_REQUIRED' }
    # Reviewed, fixed-scope root wrapper. Snapshot itself executes as postgres.
    # Export is encrypted-only: fixed five files, no globals replay or permissions
    # repair of any existing source. The protected original snapshot is retained.
    $template = @'
#!/bin/bash
set -Eeuo pipefail
set +x
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin LC_ALL=C
[[ $(id -u) == 0 && ${SUDO_USER:-} == manuel ]]
run=$1; expected=$2
[[ $run =~ ^admin-[a-f0-9]{32}$ && $expected =~ ^[a-f0-9]{64}$ ]]
work=/tmp/competence-hub-$run
[[ -d $work && ! -L $work && $(realpath -e "$work") == "$work" && $(stat -c %U "$work") == manuel ]]
helper=$work/snapshot-helper
[[ -f $helper && ! -L $helper && $(stat -c %h "$helper") == 1 ]]
[[ $(sha256sum "$helper" | cut -d ' ' -f1) == "$expected" ]]
for service in dp-chatbot.service nginx.service fail2ban.service postgresql.service; do systemctl is-active --quiet "$service"; done
result=$(runuser -u postgres -- /bin/bash "$helper" --confirm-staging-snapshot --run-id "$run")
source=/var/backups/competence-hub/prechange-$run
[[ -d $source && ! -L $source && $(realpath -e "$source") == "$source" && $(stat -c %U "$source") == postgres && $(stat -c %a "$source") == 500 ]]
export_dir=$work/export
[[ ! -e $export_dir && ! -L $export_dir ]]
mkdir -- "$export_dir"
for name in database.dump.gpg globals.sql.gpg METADATA SHA256SUMS COMPLETE; do
    [[ -f $source/$name && ! -L $source/$name && $(stat -c %h "$source/$name") == 1 ]]
    cp --no-clobber -- "$source/$name" "$export_dir/$name"
    cmp --silent -- "$source/$name" "$export_dir/$name"
    chown manuel -- "$export_dir/$name"
    chmod 0400 -- "$export_dir/$name"
done
chown manuel -- "$export_dir"
chmod 0700 -- "$export_dir"
for service in dp-chatbot.service nginx.service fail2ban.service postgresql.service; do systemctl is-active --quiet "$service"; done
printf '%s\n' "$result"
'@
    if ($Recipient -cne $script:WindowRecipient) {
        $template = $template.Replace('--run-id "$run")', ('--run-id "$run" --rebase-recipient ' + $Recipient + ')'))
    }
    return $template
}

function Assert-WindowEncryptedBackupTarget {
    param([string]$Path,[long]$RequiredFreeBytes)
    $full = Assert-StagingExternalPath $Path
    Assert-StagingPrivateAcl $full -Directory
    $mount = [IO.Path]::GetPathRoot($full)
    try {
        $volume = Get-Volume -DriveLetter $mount.Substring(0,1) -ErrorAction Stop
        $protection = Get-BitLockerVolume -MountPoint $mount -ErrorAction Stop
    } catch { throw 'CURRENT_VOLUME_PROTECTION_STATUS_UNAVAILABLE' }
    if ($volume.FileSystem -cne 'NTFS' -or [string]$protection.VolumeStatus -cne 'FullyEncrypted' -or
        [string]$protection.ProtectionStatus -cne 'On' -or [string]$protection.LockStatus -cne 'Unlocked' -or
        $RequiredFreeBytes -lt 512MB -or [IO.DriveInfo]::new($mount).AvailableFreeSpace -lt $RequiredFreeBytes) { throw 'VERIFIED_ENCRYPTED_BACKUP_TARGET_REQUIRED' }
    # Restore helper creates temporary plaintext under LOCALAPPDATA, also verify it.
    $tempMount = [IO.Path]::GetPathRoot($env:LOCALAPPDATA)
    try { $tempProtection = Get-BitLockerVolume -MountPoint $tempMount -ErrorAction Stop }
    catch { throw 'CURRENT_VOLUME_PROTECTION_STATUS_UNAVAILABLE' }
    if ([string]$tempProtection.VolumeStatus -cne 'FullyEncrypted' -or [string]$tempProtection.ProtectionStatus -cne 'On' -or
        [string]$tempProtection.LockStatus -cne 'Unlocked' -or [IO.DriveInfo]::new($tempMount).AvailableFreeSpace -lt $RequiredFreeBytes) { throw 'VERIFIED_ENCRYPTED_RESTORE_WORKSPACE_REQUIRED' }
    return $full
}

function Remove-WindowRemoteArtifacts {
    param([string]$Ssh, [string]$RunId)
    if ($RunId -cnotmatch '^admin-[a-f0-9]{32}$') { throw 'OWNED_CLEANUP_SCOPE_REJECTED' }
    $remote = '/tmp/competence-hub-' + $RunId
    # No recursive deletion, wildcards, retention or snapshot removal.
    $command = @'
set -eu
work=__WORK__
test ! -L "$work" && test "$(realpath -e "$work")" = "$work" && test "$(stat -c %U "$work")" = manuel
if test -e "$work/export"; then
    test ! -L "$work/export" && test "$(stat -c %U "$work/export")" = manuel
    for name in database.dump.gpg globals.sql.gpg METADATA SHA256SUMS COMPLETE; do
        if test -e "$work/export/$name"; then test -f "$work/export/$name" && test ! -L "$work/export/$name"; rm -- "$work/export/$name"; fi
    done
    rmdir -- "$work/export"
fi
for name in snapshot-helper window-root.sh; do
    if test -e "$work/$name"; then test -f "$work/$name" && test ! -L "$work/$name"; rm -- "$work/$name"; fi
done
rmdir -- "$work"
test ! -e "$work"
'@
    $null = Invoke-WindowCommand $Ssh ($script:WindowSshOptions + @('-T', $script:WindowHost, $command.Replace('__WORK__', $remote)))
}

function Use-WindowDatabaseEnvironment {
    param([Security.SecureString]$AppPassword, [Security.SecureString]$OwnerPassword, [scriptblock]$Action)
    $names = @('COMPETENCE_HUB_OPERATOR_APP_URL', 'COMPETENCE_HUB_OPERATOR_OWNER_URL', 'PYTHONPATH')
    $previous = @{}; $pointers = @(); $encoded = $null
    try {
        foreach ($name in $names) { $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
        $passwords = @($AppPassword, $OwnerPassword)
        $roles = @('competence_hub_app', 'competence_hub_migrator')
        for ($i = 0; $i -lt 2; $i++) {
            $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($passwords[$i]); $pointers += $pointer
            $encoded = [Uri]::EscapeDataString([Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer))
            [Environment]::SetEnvironmentVariable($names[$i], ('postgresql+asyncpg://' + $roles[$i] + ':' + $encoded + '@127.0.0.1:55432/competence_hub_staging'), 'Process')
        }
        [Environment]::SetEnvironmentVariable('PYTHONPATH', (Join-Path $script:WindowRoot 'apps/webapp/src'), 'Process')
        & $Action
    } finally {
        foreach ($name in $previous.Keys) {
            if ($null -eq $previous[$name]) { [Environment]::SetEnvironmentVariable($name, [NullString]::Value, 'Process') }
            else { [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process') }
        }
        foreach ($pointer in $pointers) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
        $encoded = $null; $passwords = $null; $previous.Clear()
    }
}

function Invoke-WindowConsoleOperator {
    param([string]$Python, [string[]]$Arguments)
    # Deliberate human-facing child: preserve the actual console handles for
    # hidden getpass/TTY checks and instructions, even inside a stdout-suppressing
    # custody scope. No shell, captured input, transcript or stderr redirection.
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $Python; $start.UseShellExecute = $false; $start.CreateNoWindow = $false
    $start.RedirectStandardInput = $false; $start.RedirectStandardError = $false
    $start.RedirectStandardOutput = $true
    foreach ($argument in $Arguments) { $start.ArgumentList.Add($argument) }
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $start
    $started = $false
    try {
        $null = $process.Start(); $started = $true
        $output = $process.StandardOutput.ReadToEndAsync()
        $process.WaitForExit(); $null = $output.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0) { throw 'OPERATOR_NOT_COMPLETE_NO_BLIND_RETRY' }
    } finally {
        if ($started -and -not $process.HasExited) { $process.Kill($true); $process.WaitForExit() }
        $process.Dispose()
    }
}

function Invoke-StagingAdminWindow {
    param([string]$Commit, [switch]$PrivateWindow, [switch]$QuietDatabase, [switch]$OperatorCustody,
          [string]$CustodyPath,[string]$KeyHome,[string]$Recipient,[string]$TargetDirectory,
          [long]$RequiredFreeBytes,[switch]$RebaseApproved)
    $ErrorActionPreference = 'Stop'; $VerbosePreference = 'SilentlyContinue'; $DebugPreference = 'SilentlyContinue'
    Set-StrictMode -Version Latest
    if (-not $IsWindows -or -not $PrivateWindow -or -not $QuietDatabase -or -not $OperatorCustody) { throw 'PRIVATE_QUIET_CUSTODY_ACKNOWLEDGMENTS_REQUIRED' }
    if (-not $RebaseApproved -or -not $CustodyPath -or -not $KeyHome -or -not $TargetDirectory -or
        $Recipient -cnotmatch '^[A-F0-9]{40}$' -or $Recipient -ceq $script:WindowRecipient -or
        $Recipient -cmatch '^(.)\1{39}$') { throw 'EXPLICIT_VERIFIED_KEY_REBASE_AND_BACKUP_TARGET_REQUIRED' }
    Assert-WindowNoDiagnostics
    if (@(Get-ChildItem Env: | Where-Object { $_.Name -like 'COMPETENCE_HUB_*' -or $_.Name -like 'DOCKER_*' }).Count) { throw 'CLEAN_OPERATOR_PROCESS_REQUIRED' }
    Assert-WindowPortFree
    $git = (Get-Command git.exe -CommandType Application -ErrorAction Stop).Source
    $ssh = (Get-Command ssh.exe -CommandType Application -ErrorAction Stop).Source
    $scp = (Get-Command scp.exe -CommandType Application -ErrorAction Stop).Source
    $gpg = (Get-Command 'C:\Program Files\GnuPG\bin\gpg.exe' -CommandType Application -ErrorAction Stop).Source
    $docker = (Get-Command docker.exe -CommandType Application -ErrorAction Stop).Source
    $pwsh = (Get-Process -Id $PID).Path
    $python = Join-Path $script:WindowRoot 'apps/webapp/.venv/Scripts/python.exe'
    $initializer = Join-Path $script:WindowRoot 'deploy/scripts/initialize-staging-operator-config.ps1'
    $restore = Join-Path $script:WindowRoot 'deploy/scripts/restore-competence-hub-snapshot.ps1'
    $producer = Join-Path $script:WindowRoot 'deploy/scripts/competence-hub-postgres-snapshot'
    $operator = Join-Path $script:WindowRoot 'apps/webapp/scripts/staging_admin_operator.py'
    $login = Join-Path $script:WindowRoot '.tmp/backend-sprint-20261030/operator-login.json'
    foreach ($path in @($python, $initializer, $restore, $producer, $operator, $login)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'REVIEWED_INPUT_MISSING_OR_LINKED' }
    }
    $restoreApi = Get-Command $restore -ErrorAction Stop
    foreach ($parameter in @('BackupSet', 'ProofPath', 'GpgHome', 'PythonPath', 'GpgPath', 'DockerPath', 'ExpectedRecipient', 'ConfirmProtectedSource', 'ConfirmIsolatedRestore')) {
        if (-not $restoreApi.Parameters.ContainsKey($parameter)) { throw 'RESTORE_API_NOT_INTEGRATED' }
    }
    Assert-WindowSource $Commit $git
    . $initializer
    $base = Join-Path $env:LOCALAPPDATA 'CompetenceHub'
    $null = Assert-StagingExternalPath $base
    # The initializer requires an existing external parent; creating that parent
    # is a separate local readiness gate, never an implicit permissive mkdir.
    if (-not [IO.Directory]::Exists($base)) { throw 'EXTERNAL_PROTECTED_PARENT_REQUIRED' }
    $custody = Assert-StagingExternalPath $CustodyPath
    $gpgHome = Assert-StagingExternalPath $KeyHome
    $legacyCustody = Join-Path $base 'staging-operator'
    $legacyGpgHome = Join-Path $base 'backup-gnupg'
    if ($custody -eq $legacyCustody -or $gpgHome -eq $legacyGpgHome) { throw 'LEGACY_CUSTODY_NOT_A_REBASE' }
    Assert-StagingPrivateAcl $gpgHome -Directory
    $target = Assert-WindowEncryptedBackupTarget $TargetDirectory $RequiredFreeBytes
    $corpus = Join-Path $base 'staging-operator-corpus-20261030/compromised-password-fingerprints.sha256'
    $attempt = Join-Path $custody 'bootstrap-attempt.json'
    Assert-WindowNoPriorAttempt $attempt
    Assert-WindowCustodyComplete $custody
    $keyBinding = Get-Content -Raw -LiteralPath (Join-Path $custody 'staging-operator.metadata.json') | ConvertFrom-Json -AsHashtable
    if ($keyBinding.allowed_origin -cne 'https://127.0.0.1:443' -or $keyBinding.recipient -cne $Recipient) { throw 'REBASE_ORIGIN_AND_RECIPIENT_BINDING_REQUIRED' }
    $null = Assert-StagingCorpus $corpus $script:WindowCorpusHash
    $context = Invoke-WindowCommand $docker @('context', 'inspect', '--format', '{{json .Endpoints.docker.Host}}')
    if ($context -cnotmatch '^"npipe:////\./pipe/(docker_engine|dockerDesktopLinuxEngine)"$') { throw 'LOCAL_DOCKER_ENGINE_REQUIRED' }
    $platform = Invoke-WindowCommand $docker @('image', 'inspect', '--format', '{{.Os}} {{.Architecture}}', $script:WindowImage)
    if ($platform -cne 'linux amd64') { throw 'CACHED_PINNED_RESTORE_IMAGE_REQUIRED_NO_PULL' }
    $run = 'admin-' + [Guid]::NewGuid().ToString('N')
    $output = Join-Path $target ('staging-window-' + $run)
    New-StagingPrivateDirectory $output
    $result = [ordered]@{ schema = 1; status = 'NOT_COMPLETE'; gate = 'PRIVATE_MANUAL_REVIEW_REQUIRED'; phase = 'local_readiness'; real_coach_apply = 'DISABLED'; account_creation = 'NOT_ATTEMPTED'; source_commit = $Commit; remote_cleanup = 'NOT_NEEDED'; tunnel_cleanup = 'NOT_NEEDED' }
    $tunnel = $null; $remoteOwned = $false; $sudo = $null; $appPassword = $null; $ownerPassword = $null
    try {
        Use-StagingOperatorEnvironment -StorageDirectory $custody -ExpectedRecipient $Recipient -AcknowledgeOperatorCustody -Action { }
        # Prove actual local key/pinentry availability BEFORE touching the server.
        $probe = [Text.Encoding]::ASCII.GetBytes('Competence Hub non-secret key availability probe v1')
        $probePath = Join-Path $output 'gpg-readiness-probe.gpg'
        $encrypted = [IO.File]::Open($probePath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        $memory = [IO.MemoryStream]::new()
        try {
            Invoke-StagingGpg -Executable $gpg -KeyHome $gpgHome -Mode Encrypt -Recipient $Recipient -InputBytes $probe -OutputStream $encrypted
            $encrypted.Dispose(); $encrypted = $null
            Invoke-StagingGpg -Executable $gpg -KeyHome $gpgHome -Mode Decrypt -Recipient $Recipient -EncryptedPath $probePath -OutputStream $memory
            if (-not [Security.Cryptography.CryptographicOperations]::FixedTimeEquals($probe, $memory.ToArray())) { throw 'LOCAL_GPG_ROUNDTRIP_REQUIRED' }
        } finally { if ($encrypted) { $encrypted.Dispose() }; $memory.Dispose(); [Array]::Clear($probe, 0, $probe.Length) }
        Assert-WindowSource $Commit $git
        Confirm-WindowOperation -Block BACKUP
        $result.phase = 'server_preflight'
        $health = Get-WindowHealth $ssh
        Write-WindowRecord (Join-Path $output 'service-preflight.json') $health
        $remote = '/tmp/competence-hub-' + $run
        $created = Invoke-WindowCommand $ssh ($script:WindowSshOptions + @('-T', $script:WindowHost,
            ('umask 077; test ! -e ' + $remote + ' && mkdir -- ' + $remote + ' && chmod 0711 -- ' + $remote + ' && printf ' + $run)))
        if ($created -cne $run) { throw 'OWNED_REMOTE_DIRECTORY_NOT_CONFIRMED' }
        $remoteOwned = $true; $result.remote_cleanup = 'PENDING'
        $wrapper = Join-Path $output 'window-root.sh'
        [IO.File]::WriteAllText($wrapper, ((Get-WindowRootScript -Recipient $Recipient).Replace("`r`n", "`n") + "`n"), [Text.Encoding]::ASCII)
        foreach ($pair in @(@($producer, 'snapshot-helper'), @($wrapper, 'window-root.sh'))) {
            $null = Invoke-WindowCommand $scp ($script:WindowSshOptions + @($pair[0], ($script:WindowHost + ':' + $remote + '/' + $pair[1])))
            $hash = (Get-FileHash -LiteralPath $pair[0] -Algorithm SHA256).Hash.ToLowerInvariant()
            $actual = Invoke-WindowCommand $ssh ($script:WindowSshOptions + @('-T', $script:WindowHost, ('sha256sum -- ' + $remote + '/' + $pair[1])))
            if ($actual -cne ($hash + '  ' + $remote + '/' + $pair[1])) { throw 'REMOTE_REVIEWED_SCRIPT_HASH_MISMATCH' }
        }
        $null = Invoke-WindowCommand $ssh ($script:WindowSshOptions + @('-T', $script:WindowHost, ('chmod 0444 -- ' + $remote + '/snapshot-helper ' + $remote + '/window-root.sh')))
        $result.phase = 'encrypted_prechange_snapshot'
        $sudo = Read-Host 'Sudo password (hidden, this private window only)' -AsSecureString
        try {
            $hash = (Get-FileHash -LiteralPath $producer -Algorithm SHA256).Hash.ToLowerInvariant()
            $raw = Invoke-WindowCommand $ssh ($script:WindowSshOptions + @('-T', $script:WindowHost,
                ("sudo -k -S -p '' -- /bin/bash " + $remote + '/window-root.sh ' + $run + ' ' + $hash))) -SecureInput $sudo
        } finally { $sudo.Dispose(); $sudo = $null }
        $snapshot = $raw | ConvertFrom-Json -AsHashtable
        $plan = @(Get-WindowSnapshotPlan $snapshot $run)
        $backup = Join-Path $output 'snapshot'
        New-StagingPrivateDirectory $backup
        foreach ($file in $plan) {
            $destination = Join-Path $backup $file.name
            $null = Invoke-WindowCommand $scp ($script:WindowSshOptions + @(($script:WindowHost + ':' + $remote + '/export/' + $file.name), $destination))
            Assert-StagingPrivateAcl $destination
            if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -cne $file.sha256) { throw 'EXACT_ENCRYPTED_COPY_HASH_MISMATCH' }
        }
        if (@(Get-ChildItem -LiteralPath $backup -Force).Count -ne 5) { throw 'EXACT_FIVE_FILE_SET_REQUIRED' }
        Write-WindowRecord (Join-Path $output 'snapshot-binding.json') $snapshot
        Confirm-WindowOperation -Block RESTORE
        $null = Assert-WindowEncryptedBackupTarget $TargetDirectory $RequiredFreeBytes
        $result.phase = 'isolated_restore'
        $proof = Join-Path $output 'restore-proof.json'
        $null = Invoke-WindowCommand $pwsh @('-NoProfile', '-File', $restore, '-BackupSet', $backup, '-ProofPath', $proof,
            '-GpgHome', $gpgHome, '-PythonPath', $python, '-GpgPath', $gpg, '-DockerPath', $docker, '-ExpectedRecipient', $Recipient, '-ConfirmProtectedSource', '-ConfirmIsolatedRestore')
        if (-not (Test-Path -LiteralPath $proof -PathType Leaf)) { throw 'ACTUAL_RESTORE_PROOF_REQUIRED' }
        $restored = Get-Content -Raw -LiteralPath $proof | ConvertFrom-Json -AsHashtable
        if ($restored.schema -cne 'competence-hub.prechange-restore-proof.v1' -or $restored.status -cne 'PASS') { throw 'ACTUAL_RESTORE_PROOF_REQUIRED' }
        Confirm-WindowOperation -Block ADMIN
        Write-WindowRecord (Join-Path $output 'service-before-admin.json') (Get-WindowHealth $ssh)
        Assert-WindowPortFree
        $start = [Diagnostics.ProcessStartInfo]::new(); $start.FileName = $ssh
        $start.UseShellExecute = $false; $start.CreateNoWindow = $true
        $start.RedirectStandardError = $true; $start.RedirectStandardOutput = $true
        foreach ($argument in ($script:WindowSshOptions + @('-T', '-o', 'ExitOnForwardFailure=yes', '-N', '-L', '127.0.0.1:55432:127.0.0.1:5432', $script:WindowHost))) { $start.ArgumentList.Add($argument) }
        $tunnel = [Diagnostics.Process]::new(); $tunnel.StartInfo = $start; $null = $tunnel.Start()
        $tunnelError = $tunnel.StandardError.ReadToEndAsync(); $tunnelOutput = $tunnel.StandardOutput.ReadToEndAsync()
        $result.tunnel_cleanup = 'PENDING'; $listening = $false
        for ($i = 0; $i -lt 40; $i++) {
            if ($tunnel.HasExited) { throw 'OWNED_TUNNEL_FAILED' }
            $listeners = @(Get-NetTCPConnection -LocalPort 55432 -State Listen -ErrorAction SilentlyContinue)
            if ($listeners.Count -eq 1 -and $listeners[0].OwningProcess -eq $tunnel.Id -and $listeners[0].LocalAddress -ceq '127.0.0.1') { $listening = $true; break }
            if ($listeners.Count) { throw 'UNOWNED_LISTENER_RACE' }
            Start-Sleep -Milliseconds 250
        }
        if (-not $listening) { throw 'OWNED_TUNNEL_NOT_READY' }
        $appPassword = Read-Host 'Password for competence_hub_app (hidden)' -AsSecureString
        $ownerPassword = Read-Host 'Password for competence_hub_migrator (hidden)' -AsSecureString
        Assert-WindowSource $Commit $git
        $result.phase = 'private_admin_operator'
        $binding = Join-Path $output 'operator-binding.json'
        Use-WindowDatabaseEnvironment $appPassword $ownerPassword -Action {
            Use-StagingOperatorEnvironment -StorageDirectory $custody -ExpectedRecipient $Recipient -AcknowledgeOperatorCustody -Action {
                Write-WindowRecord $attempt @{ schema = 1; status = 'ATTEMPTED_CHECK_REQUIRED'; window = $output; source_commit = $Commit; started_at_utc = [DateTime]::UtcNow.ToString('o') }
                $result.account_creation = 'ATTEMPTED_CHECK_REQUIRED'
                Invoke-WindowConsoleOperator $python @($operator, '--login-file', $login, '--restore-proof', $proof, '--backup-set', $backup, '--binding-output', $binding, '--expected-backup-recipient', $Recipient)
            }
        }
        $account = Get-Content -Raw -LiteralPath $binding | ConvertFrom-Json -AsHashtable
        if ($account.status -cne 'PASS' -or $account.account_creation -cne 'CONFIRMED' -or @($account.roles).Count -ne 1 -or $account.roles[0] -cne 'admin' -or $null -ne $account.coach_mapping -or $null -ne $account.calendar_mapping -or $account.real_coach_apply -cne 'DISABLED') { throw 'ACTUAL_ADMIN_POSTCHECK_REQUIRED' }
        $result.account_creation = 'CONFIRMED'; $result.phase = 'postflight'
        Write-WindowRecord (Join-Path $output 'service-postflight.json') (Get-WindowHealth $ssh)
        $result.status = 'PASS'; $result.gate = 'NONE'; $result.phase = 'complete'
    } catch {
        $result.status = 'STOP'; $result.gate = Get-WindowStopCode $_.Exception.Message
    } finally {
        foreach ($secret in @($sudo, $appPassword, $ownerPassword)) { if ($secret) { $secret.Dispose() } }
        if ($tunnel) {
            try {
                if (-not $tunnel.HasExited) { $tunnel.Kill($true); $tunnel.WaitForExit() }
                $null = $tunnelError.GetAwaiter().GetResult(); $null = $tunnelOutput.GetAwaiter().GetResult()
                if (@(Get-NetTCPConnection -LocalPort 55432 -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -eq $tunnel.Id }).Count) { throw 'OWNED_LISTENER_CLEANUP_NOT_PROVEN' }
                $result.tunnel_cleanup = 'PASS'
            } catch { $result.tunnel_cleanup = 'NOT_PROVEN'; $result.status = 'STOP' }
            finally { $tunnel.Dispose() }
        }
        if ($remoteOwned) {
            try { Write-WindowRecord (Join-Path $output 'service-final.json') (Get-WindowHealth $ssh) }
            catch { $result.status = 'STOP'; $result.service_final = 'NOT_PROVEN' }
            try { Remove-WindowRemoteArtifacts $ssh $run; $result.remote_cleanup = 'PASS' }
            catch { $result.remote_cleanup = 'NOT_PROVEN'; $result.status = 'STOP' }
        }
        Write-WindowRecord (Join-Path $output 'window-result.json') $result
    }
    if ($result.status -cne 'PASS') { throw $result.gate }
    return [pscustomobject]@{ status = $result.status; real_coach_apply = 'DISABLED'; private_evidence_directory = $output }
}

if ($MyInvocation.InvocationName -ne '.') {
    if (-not $Execute) {
        Write-Output 'STAGING_ADMIN_WINDOW=NOT_EXECUTED READINESS_ONLY REAL_COACH_APPLY=DISABLED'
    } else {
        try { Invoke-StagingAdminWindow -Commit $ExpectedSourceCommit -PrivateWindow:$AcknowledgePrivateWindow -QuietDatabase:$AcknowledgeQuietDatabase -OperatorCustody:$AcknowledgeOperatorCustody -CustodyPath $RebasedStorageDirectory -KeyHome $RebasedGpgHome -Recipient $ExpectedBackupRecipient -TargetDirectory $BackupDestinationDirectory -RequiredFreeBytes $RequiredBackupFreeBytes -RebaseApproved:$AcknowledgeBackupKeyRebase }
        catch {
            $code = Get-WindowStopCode $_.Exception.Message
            [Console]::Error.WriteLine("STAGING_ADMIN_WINDOW=STOP GATE=$code REAL_COACH_APPLY=DISABLED")
            exit 1
        }
    }
}
