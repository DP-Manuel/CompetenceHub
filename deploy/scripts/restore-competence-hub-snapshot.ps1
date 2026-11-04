#requires -Version 7.2
<#
Preparation only. Execute manually in the separately approved operator window,
from reviewed committed source, on the protected Windows restore workstation.
No private-key transfer, source deletion, real DB access or import authorization.
ProofPath is mandatory, new, outside the repository. GpgHome defaults to the
approved LOCALAPPDATA home; pinentry remains interactive, never a secret argument.
Only this helper's random container ID and private temporary directory are owned.
The password-free globals payload is decrypted for readability, NEVER replayed:
co-hosted roles are not restored. Only the three known roles are created NOLOGIN.
The proof covers the exact v1 migration/relation/count/owner baseline, not all
cluster roles, application encryption-key custody, or a real recovery execution.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BackupSet,
    [Parameter(Mandatory = $true)][string]$ProofPath,
    [string]$GpgHome = (Join-Path $env:LOCALAPPDATA 'CompetenceHub\backup-gnupg'),
    [string]$PythonPath = 'python.exe',
    [string]$GpgPath = 'C:\Program Files\GnuPG\bin\gpg.exe',
    [string]$DockerPath = 'docker.exe',
    [ValidatePattern('^[A-F0-9]{40}$')][string]$ExpectedRecipient = '2E44306121629A100F76A8B08CCA3D9186A28D4C',
    [Parameter(Mandatory = $true)][switch]$ConfirmProtectedSource,
    [Parameter(Mandatory = $true)][switch]$ConfirmIsolatedRestore
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$image = 'postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825'
$repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot))).TrimEnd('\')
$utf8 = New-Object Text.UTF8Encoding($false, $true)
$identity = [Security.Principal.WindowsIdentity]::GetCurrent().User
$allowedSids = @($identity.Value, 'S-1-5-18', 'S-1-5-32-544')
$verifier = Join-Path $PSScriptRoot 'verify-prechange-restore-baseline.py'

function Assert-NoReparse([string]$Path) {
    $cursor = $Path
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'unsafe_reparse_path' }
        }
        else {
            # Get-Item also detects a dangling link that Test-Path may hide.
            $item = Get-Item -LiteralPath $cursor -Force -ErrorAction SilentlyContinue
            if ($null -ne $item) { throw 'unsafe_missing_path' }
        }
        $parent = [IO.Path]::GetDirectoryName($cursor.TrimEnd('\'))
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
}

function Get-LocalPath([string]$Path) {
    if ($Path -notmatch '^[A-Za-z]:\\' -or $Path.Substring(2).Contains(':') -or
        $Path -match '[\\/]\.\.?([\\/]|$)' -or $Path.Contains('/')) { throw 'absolute_local_path_required' }
    $full = [IO.Path]::GetFullPath($Path).TrimEnd('\')
    if ($full.Length -lt 4) { throw 'drive_root_forbidden' }
    Assert-NoReparse $full
    return $full
}

function Test-Within([string]$Child, [string]$Parent) {
    return $Child.Equals($Parent, [StringComparison]::OrdinalIgnoreCase) -or
        $Child.StartsWith($Parent.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)
}

function Assert-OutsideRepo([string]$Path) {
    if ((Test-Within $Path $repoRoot) -or (Test-Within $repoRoot $Path)) { throw 'repository_overlap' }
}

function Assert-PrivateDirectory([string]$Path) {
    Assert-NoReparse $Path
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { throw 'private_directory_missing' }
    $acl = Get-Acl -LiteralPath $Path
    if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $identity.Value) { throw 'unexpected_directory_owner' }
    foreach ($rule in $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])) {
        if ($rule.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and
            $rule.IdentityReference.Value -notin $allowedSids) { throw 'directory_acl_not_private' }
    }
}

function Protect-OwnedDirectory([string]$Path) {
    $acl = New-Object Security.AccessControl.DirectorySecurity
    $acl.SetOwner($identity)
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($sid in @($identity.Value, 'S-1-5-18')) {
        $principal = New-Object Security.Principal.SecurityIdentifier($sid)
        $rule = New-Object Security.AccessControl.FileSystemAccessRule($principal, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
        $acl.AddAccessRule($rule)
    }
    Set-Acl -LiteralPath $Path -AclObject $acl
    Assert-PrivateDirectory $Path
}

function Resolve-Application([string]$Name) {
    $command = Get-Command $Name -CommandType Application -ErrorAction Stop
    return $command.Source
}

function Invoke-Native([string]$Executable, [string[]]$Arguments, [int]$TimeoutMilliseconds = 900000) {
    # Use an explicit child result, not inherited/scoped LASTEXITCODE. The venv
    # launcher did not set that automatic variable in the actual Windows probe.
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $Executable; $start.UseShellExecute = $false; $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true; $start.RedirectStandardOutput = $true; $start.RedirectStandardError = $true
    foreach ($argument in $Arguments) { $start.ArgumentList.Add($argument) }
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $start
    $started = $false
    try {
        $null = $process.Start(); $started = $true
        $stdout = $process.StandardOutput.ReadToEndAsync(); $stderr = $process.StandardError.ReadToEndAsync()
        $process.StandardInput.Close()
        if (-not $process.WaitForExit($TimeoutMilliseconds)) { throw 'native_command_timeout' }
        $output = $stdout.GetAwaiter().GetResult(); $null = $stderr.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0) { throw ('native_command_failed_exit_' + $process.ExitCode) }
        return $output.TrimEnd("`r", "`n")
    } finally {
        if ($started -and -not $process.HasExited) { $process.Kill($true); $process.WaitForExit() }
        $process.Dispose()
    }
}

function Assert-SourceSet([string]$Directory) {
    Assert-PrivateDirectory $Directory
    $names = @('database.dump.gpg', 'globals.sql.gpg', 'METADATA', 'SHA256SUMS', 'COMPLETE')
    $entries = @(Get-ChildItem -LiteralPath $Directory -Force)
    if ($entries.Count -ne 5) { throw 'unexpected_snapshot_entries' }
    foreach ($entry in $entries) {
        if ($entry.Name -cnotin $names -or $entry.PSIsContainer -or
            ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'unsafe_snapshot_entry' }
        # The copy is encrypted but must still be private, including child ACLs.
        $acl = Get-Acl -LiteralPath $entry.FullName
        foreach ($rule in $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])) {
            if ($rule.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and
                $rule.IdentityReference.Value -notin $allowedSids) { throw 'snapshot_file_acl_not_private' }
        }
        if ($entry.Name -ne 'COMPLETE' -and $entry.Length -eq 0) { throw 'empty_snapshot_entry' }
        if ($entry.Name -eq 'COMPLETE' -and $entry.Length -ne 0) { throw 'invalid_complete_marker' }
    }
    if ((Get-Item -LiteralPath (Join-Path $Directory 'SHA256SUMS')).Length -gt 4096) { throw 'oversized_checksums' }
    if ((Get-Item -LiteralPath (Join-Path $Directory 'METADATA')).Length -gt 8388608) { throw 'oversized_metadata' }
    $lines = @([IO.File]::ReadAllLines((Join-Path $Directory 'SHA256SUMS'), $utf8))
    if ($lines.Count -ne 3) { throw 'checksum_entry_count' }
    $hashes = @{}
    foreach ($line in $lines) {
        if ($line -cnotmatch '^([a-f0-9]{64})  (database\.dump\.gpg|globals\.sql\.gpg|METADATA)$') { throw 'invalid_checksum_line' }
        $name = $matches[2]
        $expectedHash = $matches[1]
        if ($hashes.ContainsKey($name)) { throw 'duplicate_checksum_entry' }
        $actualHash = (Get-FileHash -LiteralPath (Join-Path $Directory $name) -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -cne $expectedHash) { throw 'snapshot_checksum_mismatch' }
        $hashes[$name] = $actualHash
    }
    if ($hashes.Count -ne 3) { throw 'incomplete_checksums' }
    return $hashes
}

$restoreRoot = $null
$rootOwned = $false
$containerId = $null
$containerOwned = $false
$containerStarted = $false
$passwordOwned = $false
$databaseRemoved = $false
$containerRemoved = $false
$plaintextRemoved = $false
$comparison = $null
$failure = $false
$cleanupFailed = $false
$proofOwned = $false
$token = [guid]::NewGuid().ToString('N')
$containerName = 'ch-prechange-restore-' + $token
$restoreDatabase = 'competence_hub_restore_check_' + $token
$docker = $null
$proof = $null
$phase = 'input_validation'
$failureLine = 0
$failureCode = 'none'

function Assert-OwnedContainer([string]$Id) {
    if ($Id -cnotmatch '^[a-f0-9]{64}$') { throw 'invalid_owned_container_id' }
    $actual = Invoke-Native $docker @('container', 'inspect', '--format', '{{.Id}}|{{.Name}}|{{index .Config.Labels "competence-hub.prechange-run"}}', $Id)
    if ($actual -cne "$Id|/$containerName|$token") { throw 'container_ownership_mismatch' }
}

try {
    if (-not $ConfirmProtectedSource -or -not $ConfirmIsolatedRestore) { throw 'confirmations_required' }
    if ([Environment]::GetEnvironmentVariables('Process').Contains('POSTGRES_PASSWORD')) { throw 'existing_postgres_password_environment' }
    $source = Get-LocalPath $BackupSet
    $proof = Get-LocalPath $ProofPath
    $keyHome = Get-LocalPath $GpgHome
    foreach ($path in @($source, $proof, $keyHome)) { Assert-OutsideRepo $path }
    $proofParent = Split-Path -Parent $proof
    Assert-PrivateDirectory $proofParent
    Assert-PrivateDirectory $keyHome
    if ((Test-Within $proof $source) -or (Test-Within $proof $keyHome) -or
        (Test-Within $source $keyHome) -or (Test-Within $keyHome $source) -or
        (Test-Path -LiteralPath $proof)) { throw 'proof_or_source_overlap' }
    $hashes = Assert-SourceSet $source
    $python = Resolve-Application $PythonPath
    $gpg = Resolve-Application $GpgPath
    $docker = Resolve-Application $DockerPath
    $endpoint = Invoke-Native $docker @('context', 'inspect', '--format', '{{json .Endpoints.docker.Host}}')
    if ($endpoint -cnotmatch '^"npipe:////\./pipe/(docker_engine|dockerDesktopLinuxEngine)"$') { throw 'local_docker_engine_required' }
    $phase = 'source_baseline_validation'
    $validation = (Invoke-Native $python @($verifier, 'validate', '--expected', (Join-Path $source 'METADATA'), '--expected-recipient', $ExpectedRecipient)) | ConvertFrom-Json
    if ($validation.status -cne 'VALID' -or $validation.metadata_sha256 -cne $hashes['METADATA']) { throw 'source_baseline_invalid' }
    $null = Invoke-Native $docker @('image', 'inspect', $image)

    $phase = 'protected_external_copy'
    $tempParent = Get-LocalPath $env:LOCALAPPDATA
    $restoreRoot = Get-LocalPath (Join-Path $tempParent ('competence-hub-prechange-' + $token))
    Assert-OutsideRepo $restoreRoot
    if ((Test-Path -LiteralPath $restoreRoot) -or (Test-Within $restoreRoot $source) -or
        (Test-Within $restoreRoot $keyHome) -or (Test-Within $proof $restoreRoot)) { throw 'unsafe_temporary_directory' }
    New-Item -ItemType Directory -Path $restoreRoot -ErrorAction Stop | Out-Null
    $rootOwned = $true
    Protect-OwnedDirectory $restoreRoot
    foreach ($name in @('database.dump.gpg', 'globals.sql.gpg', 'METADATA', 'SHA256SUMS', 'COMPLETE')) {
        Copy-Item -LiteralPath (Join-Path $source $name) -Destination (Join-Path $restoreRoot $name) -ErrorAction Stop
    }
    $copiedHashes = Assert-SourceSet $restoreRoot
    foreach ($name in $hashes.Keys) {
        if ($copiedHashes[$name] -cne $hashes[$name]) { throw 'source_changed_during_copy' }
    }
    foreach ($payload in @('database.dump', 'globals.sql')) {
        $phase = 'local_decryption_' + $payload.Replace('.', '_')
        $output = Join-Path $restoreRoot $payload
        $null = Invoke-Native $gpg @('--no-options', '--homedir', $keyHome, '--no-tty', '--no-auto-key-retrieve', '--auto-key-locate', 'clear', '--no-auto-key-import', '--output', $output, '--decrypt', (Join-Path $restoreRoot ($payload + '.gpg')))
        if (-not (Test-Path -LiteralPath $output -PathType Leaf) -or (Get-Item -LiteralPath $output).Length -eq 0) { throw 'empty_decrypted_payload' }
    }
    # Never replay globals.sql: it can contain unrelated co-hosted cluster roles.
    $phase = 'restore_container_creation'
    $query = Invoke-Native $python @($verifier, 'query')
    [IO.File]::WriteAllText((Join-Path $restoreRoot 'baseline.sql'), $query + "`n", $utf8)
    $randomBytes = New-Object byte[] 36
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($randomBytes) } finally { $rng.Dispose() }
    $ephemeralPassword = [Convert]::ToBase64String($randomBytes)
    [Array]::Clear($randomBytes, 0, $randomBytes.Length)
    # Docker reads the process value; the secret is NEVER in a command argument.
    [Environment]::SetEnvironmentVariable('POSTGRES_PASSWORD', $ephemeralPassword, 'Process')
    $passwordOwned = $true
    $cidFile = Join-Path $restoreRoot 'container.id'
    $mount = "type=bind,source=$restoreRoot,target=/restore,readonly"
    $createdId = Invoke-Native $docker @('create', '--pull', 'never', '--name', $containerName, '--cidfile', $cidFile,
        '--label', "competence-hub.prechange-run=$token", '--network', 'none',
        '--tmpfs', '/var/lib/postgresql/data:rw,noexec,nosuid,size=1g', '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m',
        '--env', 'POSTGRES_PASSWORD', '--mount', $mount, $image)
    Assert-NoReparse $cidFile
    $containerId = [IO.File]::ReadAllText($cidFile).Trim()
    Assert-OwnedContainer $containerId
    $containerOwned = $true
    if ($createdId -cne $containerId) { throw 'container_id_output_mismatch' }
    [Environment]::SetEnvironmentVariable('POSTGRES_PASSWORD', $null, 'Process')
    $passwordOwned = $false
    $ephemeralPassword = $null
    $null = Invoke-Native $docker @('start', $containerId)
    $containerStarted = $true
    $ready = $false
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        # initdb briefly starts a temporary server too. Only PID1=postgres proves
        # the final owned runtime, not that transient initialization socket.
        try {
            $null = Invoke-Native $docker @('exec', $containerId, 'sh', '-c', 'test "$(cat /proc/1/comm)" = postgres && pg_isready --username postgres --host /var/run/postgresql') -TimeoutMilliseconds 5000
            $ready = $true; break
        } catch { }
        Start-Sleep -Seconds 1
    }
    if (-not $ready) { throw 'isolated_postgres_not_ready' }
    $version = Invoke-Native $docker @('exec', $containerId, 'psql', '-XqAt', '-U', 'postgres', '-d', 'postgres', '-v', 'ON_ERROR_STOP=1', '-c', 'SHOW server_version_num;')
    if ($version -cnotmatch '^16[0-9]{4}$') { throw 'postgres_major_version_mismatch' }
    $phase = 'isolated_roles_and_database'
    $null = Invoke-Native $docker @('exec', $containerId, 'psql', '-XqAt', '-U', 'postgres', '-d', 'postgres', '-v', 'ON_ERROR_STOP=1', '-c',
        'CREATE ROLE competence_hub_owner NOLOGIN; CREATE ROLE competence_hub_app NOLOGIN; CREATE ROLE competence_hub_migrator NOLOGIN;')
    if ($restoreDatabase -cnotmatch '^competence_hub_restore_check_[a-z0-9_]+$') { throw 'unsafe_restore_database' }
    $null = Invoke-Native $docker @('exec', $containerId, 'createdb', '-U', 'postgres', '--owner', 'competence_hub_owner', '--template', 'template0', '--encoding', 'UTF8', '--', $restoreDatabase)
    $phase = 'restore_archive'
    $null = Invoke-Native $docker @('exec', $containerId, 'pg_restore', '--list', '/restore/database.dump')
    $null = Invoke-Native $docker @('exec', $containerId, 'pg_restore', '--clean', '--if-exists', '--single-transaction', '--exit-on-error',
        '-U', 'postgres', '--dbname', $restoreDatabase, '/restore/database.dump')
    $phase = 'restored_baseline_comparison'
    $actual = Invoke-Native $docker @('exec', $containerId, 'psql', '-XqAt', '-U', 'postgres', '-d', $restoreDatabase, '-v', 'ON_ERROR_STOP=1', '-f', '/restore/baseline.sql')
    $actualFile = Join-Path $restoreRoot 'restored-baseline.jsonl'
    [IO.File]::WriteAllText($actualFile, $actual + "`n", $utf8)
    $comparison = (Invoke-Native $python @($verifier, 'compare', '--expected', (Join-Path $restoreRoot 'METADATA'), '--actual', $actualFile, '--expected-recipient', $ExpectedRecipient)) | ConvertFrom-Json
    if ($comparison.status -cne 'PASS' -or $comparison.metadata_sha256 -cne $hashes['METADATA'] -or
        $comparison.baseline_sha256 -cne $validation.baseline_sha256 -or -not $comparison.owners_verified) { throw 'baseline_comparison_failed' }
}
catch {
    $failure = $true; $failureLine = $_.InvocationInfo.ScriptLineNumber
    if ($_.Exception.Message -cmatch '^native_command_failed_exit_-?[0-9]+$') { $failureCode = $_.Exception.Message }
    else { $failureCode = 'bounded_restore_failure' }
}
finally {
    if ($passwordOwned) {
        if ([Environment]::GetEnvironmentVariable('POSTGRES_PASSWORD', 'Process') -ceq $ephemeralPassword) {
            [Environment]::SetEnvironmentVariable('POSTGRES_PASSWORD', $null, 'Process')
        }
        else { $cleanupFailed = $true }
        $ephemeralPassword = $null
    }
    # A failed create can still have produced an ID. Only recover our own cidfile.
    if ($rootOwned -and -not $containerOwned -and $null -ne $docker) {
        try {
            $recoverCid = Join-Path $restoreRoot 'container.id'
            Assert-NoReparse $recoverCid
            if (Test-Path -LiteralPath $recoverCid -PathType Leaf) {
                $containerId = [IO.File]::ReadAllText($recoverCid).Trim()
                Assert-OwnedContainer $containerId
                $containerOwned = $true
            }
        }
        catch { $cleanupFailed = $true }
    }
    if ($containerOwned) {
        try {
            Assert-OwnedContainer $containerId
            if ($containerStarted) {
                $null = Invoke-Native $docker @('exec', $containerId, 'dropdb', '-U', 'postgres', '--if-exists', '--', $restoreDatabase)
                $remaining = Invoke-Native $docker @('exec', $containerId, 'psql', '-XqAt', '-U', 'postgres', '-d', 'postgres', '-v', 'ON_ERROR_STOP=1', '-c', "SELECT count(*) FROM pg_database WHERE datname='$restoreDatabase';")
                if ($remaining -cne '0') { throw 'temporary_database_remains' }
                $databaseRemoved = $true
            }
        }
        catch { $cleanupFailed = $true }
        try {
            Assert-OwnedContainer $containerId
            $null = Invoke-Native $docker @('container', 'rm', '--force', $containerId)
            $remaining = Invoke-Native $docker @('container', 'ls', '--all', '--no-trunc', '--filter', "id=$containerId", '--format', '{{.ID}}')
            if ($remaining -ne '') { throw 'owned_container_remains' }
            $containerRemoved = $true
        }
        catch { $cleanupFailed = $true }
    }
    if ($rootOwned) {
        try {
            if ($restoreRoot -cne (Join-Path $tempParent ('competence-hub-prechange-' + $token))) { throw 'cleanup_path_mismatch' }
            Assert-OutsideRepo $restoreRoot
            Assert-PrivateDirectory $restoreRoot
            # Flat owned files only. No recursive deletion and no source/key path.
            $ownedNames = @('database.dump.gpg', 'globals.sql.gpg', 'METADATA', 'SHA256SUMS', 'COMPLETE',
                'database.dump', 'globals.sql', 'baseline.sql', 'container.id', 'restored-baseline.jsonl')
            $entries = @(Get-ChildItem -LiteralPath $restoreRoot -Force)
            foreach ($entry in $entries) {
                if ($entry.Name -cnotin $ownedNames -or $entry.PSIsContainer -or
                    ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'unexpected_cleanup_entry' }
            }
            foreach ($entry in $entries) { Remove-Item -LiteralPath $entry.FullName -Force -ErrorAction Stop }
            Remove-Item -LiteralPath $restoreRoot -ErrorAction Stop
            if (Test-Path -LiteralPath $restoreRoot) { throw 'plaintext_directory_remains' }
            foreach ($name in $ownedNames) {
                if (Test-Path -LiteralPath (Join-Path $restoreRoot $name)) { throw 'plaintext_file_remains' }
            }
            $plaintextRemoved = $true
        }
        catch { $cleanupFailed = $true }
    }
}

if ($failure -or $cleanupFailed -or $null -eq $comparison -or -not $databaseRemoved -or
    -not $containerRemoved -or -not $plaintextRemoved) {
    [Console]::Error.WriteLine((@{ schema='competence-hub.prechange-restore-proof.v1'; status='FAIL'; code='restore_or_cleanup_failed'; phase=$phase; source_line=$failureLine; failure_code=$failureCode } | ConvertTo-Json -Compress))
    exit 1
}

try {
    $result = [ordered]@{
        schema = 'competence-hub.prechange-restore-proof.v1'
        status = 'PASS'
        source_directory = $source
        dump_gpg_sha256 = $hashes['database.dump.gpg']
        metadata_sha256 = $hashes['METADATA']
        baseline_sha256 = $comparison.baseline_sha256
        migrations = @($comparison.migrations)
        row_counts = $comparison.row_counts
        owners_verified = $true
        encrypted_copy_verified = $true
        temporary_database_removed = $true
        container_removed = $true
        plaintext_removed = $true
        finished_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
        restore_image = $image
    }
    Assert-NoReparse $proof
    Assert-PrivateDirectory $proofParent
    $bytes = $utf8.GetBytes(($result | ConvertTo-Json -Depth 8 -Compress) + "`n")
    $stream = [IO.File]::Open($proof, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $proofOwned = $true
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    if ((Get-FileHash -LiteralPath $proof -Algorithm SHA256).Hash.ToLowerInvariant() -cne
        ([BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()) { throw 'proof_write_verification_failed' }
    # Identical JSON to the proof file, never subprocess diagnostics or rows.
    Write-Output ($utf8.GetString($bytes).TrimEnd("`n"))
}
catch {
    if ($proofOwned) {
        try { Assert-NoReparse $proof; Remove-Item -LiteralPath $proof -Force -ErrorAction Stop }
        catch { [Console]::Error.WriteLine('owned_proof_cleanup_failed') }
    }
    [Console]::Error.WriteLine('{"schema":"competence-hub.prechange-restore-proof.v1","status":"FAIL","code":"proof_publication_failed"}')
    exit 1
}
