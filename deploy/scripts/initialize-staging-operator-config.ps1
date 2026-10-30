#requires -Version 7.2
<#
Local Windows operator preparation only; no database, account or server changes.
Run privately with native GPG pinentry. Never transcript, debug or record this
window. Dot-sourcing defines APIs only. Failed preparations retain their private
directory for operator review; there is no automatic deletion or key replacement.
DPAPI is tied to the current Windows user/machine. The verified GPG backup is the
portable recovery artifact; keep an approved encrypted off-machine copy too.
#>
[CmdletBinding()]
param(
    [string]$StorageDirectory = (Join-Path $env:LOCALAPPDATA 'CompetenceHub/staging-operator'),
    [string]$FingerprintPath = (Join-Path $env:LOCALAPPDATA 'CompetenceHub/staging-operator-corpus-20261030/compromised-password-fingerprints.sha256'),
    [string]$ExpectedCorpusSha256 = '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da',
    [string]$AllowedOrigin,
    [string]$GpgHome = (Join-Path $env:LOCALAPPDATA 'CompetenceHub/backup-gnupg'),
    [string]$GpgExecutable = 'gpg.exe',
    [switch]$AcknowledgeProtectedStorage,
    [switch]$AcknowledgeOperatorCustody
)

$script:OperatorRepositoryRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$script:OperatorRecipient = '2E44306121629A100F76A8B08CCA3D9186A28D4C'
$script:OperatorKeyVersions = [ordered]@{ totp = 'staging-totp-v1'; outbox = 'staging-outbox-v1'; recovery = 'staging-recovery-v1' }
$script:OperatorStoreName = 'staging-operator.keys.clixml'
$script:OperatorBackupName = 'staging-operator.keys.json.gpg'
$script:OperatorMetadataName = 'staging-operator.metadata.json'

function Assert-StagingExternalPath {
    param([Parameter(Mandatory)][string]$Path)
    if (-not $IsWindows -or -not [IO.Path]::IsPathFullyQualified($Path) -or $Path.StartsWith('\\')) {
        throw 'A fully qualified local Windows path is required.'
    }
    if ($Path.Substring(2).Contains(':') -or $Path -match '[. ]([\\/]|$)' -or $Path -match '(^|[\\/])\.\.?([\\/]|$)') {
        throw 'Ambiguous paths and alternate streams are not allowed.'
    }
    $full = [IO.Path]::GetFullPath($Path).TrimEnd([char[]]'\/')
    $root = [IO.Path]::GetPathRoot($full)
    $repo = $script:OperatorRepositoryRoot.TrimEnd([char[]]'\/')
    if ($full -eq $root.TrimEnd('\') -or $full -eq $repo -or
        $full.StartsWith($repo + '\', [StringComparison]::OrdinalIgnoreCase) -or
        $repo.StartsWith($full + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Filesystem roots, repository paths and repository ancestors are forbidden.'
    }
    if ([IO.DriveInfo]::new($root).DriveType -ne [IO.DriveType]::Fixed) { throw 'A fixed local drive is required.' }
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force -ErrorAction Stop
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse points are forbidden.' }
        }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
    return $full
}

function Assert-StagingOrigin {
    param([string]$Origin)
    $uri = $null
    if (-not [Uri]::TryCreate($Origin, [UriKind]::Absolute, [ref]$uri) -or
        $uri.Scheme -ne 'https' -or -not $uri.Host -or $uri.UserInfo -or
        $Origin -notmatch '^https://[^/?#*]+$') { throw 'An exact HTTPS origin without a trailing slash is required.' }
}

function Assert-StagingCorpus {
    param([string]$Path, [string]$ExpectedSha256)
    $full = Assert-StagingExternalPath $Path
    if ($ExpectedSha256 -cnotmatch '^[a-f0-9]{64}$' -or $ExpectedSha256 -match '^(.)\1{63}$') { throw 'An explicit non-placeholder SHA-256 is required.' }
    if (-not [IO.File]::Exists($full)) { throw 'The approved external corpus is missing.' }
    # Lock the exact bytes through hash and format checks; never load raw passwords.
    $stream = [IO.File]::Open($full, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $reader = $null
    try {
        $hash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stream)).ToLowerInvariant()
        if ($hash -cne $ExpectedSha256) { throw 'The approved corpus SHA-256 does not match.' }
        $stream.Position = 0
        $reader = [IO.StreamReader]::new($stream, [Text.Encoding]::ASCII, $false, 4096, $true)
        $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        while ($null -ne ($line = $reader.ReadLine())) {
            if ($line -cnotmatch '^[a-f0-9]{64}$' -or $line -match '^(.)\1{63}$' -or -not $seen.Add($line)) {
                throw 'Invalid, duplicate or placeholder corpus fingerprints.'
            }
        }
        if ($seen.Count -lt 90000) { throw 'An operational corpus, not a small test corpus, is required.' }
    } finally {
        if ($reader) { $reader.Dispose() }
        $stream.Dispose()
    }
    return $full
}

function Assert-StagingPrivateAcl {
    param([string]$Path, [switch]$Directory)
    $null = Assert-StagingExternalPath $Path
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl = Get-Acl -LiteralPath $Path -ErrorAction Stop
    if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $sid.Value -or
        ($Directory -and -not $acl.AreAccessRulesProtected)) { throw 'Operator ownership/protected directory ACL is required.' }
    $allowed = @($sid.Value, 'S-1-5-18')
    $found = [Collections.Generic.HashSet[string]]::new()
    foreach ($rule in $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])) {
        if ($rule.IdentityReference.Value -notin $allowed -or $rule.AccessControlType -ne 'Allow' -or
            $rule.FileSystemRights -ne [Security.AccessControl.FileSystemRights]::FullControl) {
            throw 'Only the operator and SYSTEM may have full-control access.'
        }
        $null = $found.Add($rule.IdentityReference.Value)
    }
    if ($found.Count -ne 2) { throw 'Both operator and SYSTEM ACL entries are required.' }
}

function New-StagingPrivateDirectory {
    param([string]$Path)
    $full = Assert-StagingExternalPath $Path
    if (Test-Path -LiteralPath $full) { throw 'Storage already exists; no files or keys will be overwritten.' }
    if (-not [IO.Directory]::Exists([IO.Path]::GetDirectoryName($full))) { throw 'The external parent directory must already exist.' }
    $null = New-Item -ItemType Directory -Path $full -ErrorAction Stop
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl = [Security.AccessControl.DirectorySecurity]::new()
    $acl.SetOwner($sid)
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($identity in @($sid, [Security.Principal.SecurityIdentifier]::new('S-1-5-18'))) {
        $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new(
            $identity, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow'))
    }
    Set-Acl -LiteralPath $full -AclObject $acl -ErrorAction Stop
    Assert-StagingPrivateAcl $full -Directory
}

function New-StagingOperatorSecret {
    # Key strings exist only in process memory. Neither the JSON nor its keys may
    # enter arguments, plaintext files, output streams, transcripts or debug logs.
    $keys = @{}
    $bytes = [byte[]]::new(32)
    $json = $null
    try {
        foreach ($purpose in @('totp', 'outbox', 'recovery', 'rate', 'idempotency')) {
            do {
                [Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
                $encoded = [Convert]::ToBase64String($bytes)
            } while ($keys.Values -contains $encoded)
            $keys[$purpose] = $encoded
        }
        $variables = [ordered]@{
            COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY = $keys.rate
            COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY = $keys.idempotency
        }
        foreach ($purpose in @('totp', 'outbox', 'recovery')) {
            $stem = @{totp = 'TOTP'; outbox = 'OUTBOX'; recovery = 'RECOVERY_HMAC'}[$purpose]
            $version = $script:OperatorKeyVersions[$purpose]
            $variables["COMPETENCE_HUB_${stem}_KEYRING"] = (@{ $version = $keys[$purpose] } | ConvertTo-Json -Compress)
            $variables["COMPETENCE_HUB_${stem}_ACTIVE_KEY_VERSION"] = $version
        }
        $json = [ordered]@{ schema = 1; environment = 'staging'; variables = $variables } | ConvertTo-Json -Depth 5 -Compress
        return ConvertTo-SecureString -String $json -AsPlainText -Force
    } finally {
        [Array]::Clear($bytes, 0, $bytes.Length)
        $keys.Clear()
        $variables = $null; $encoded = $null; $json = $null
    }
}

function Invoke-StagingGpg {
    param([string]$Executable, [string]$KeyHome, [ValidateSet('Encrypt', 'Decrypt')][string]$Mode,
          [byte[]]$InputBytes, [string]$EncryptedPath, [IO.Stream]$OutputStream)
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $Executable
    $start.UseShellExecute = $false
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    foreach ($argument in @('--no-options', '--homedir', $KeyHome, '--no-auto-key-retrieve', '--auto-key-locate', 'clear', '--no-auto-key-import')) {
        $start.ArgumentList.Add($argument)
    }
    if ($Mode -eq 'Encrypt') {
        foreach ($argument in @('--batch', '--no-tty', '--trust-model', 'always', '--recipient', $script:OperatorRecipient, '--encrypt')) { $start.ArgumentList.Add($argument) }
    } else {
        # Native pinentry only. No loopback/passphrase arguments or plaintext output.
        foreach ($argument in @('--pinentry-mode', 'ask', '--decrypt', $EncryptedPath)) { $start.ArgumentList.Add($argument) }
    }
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    $started = $false
    try {
        $null = $process.Start()
        $started = $true
        $stderr = $process.StandardError.ReadToEndAsync()
        $stdout = $process.StandardOutput.BaseStream.CopyToAsync($OutputStream)
        if ($Mode -eq 'Encrypt') { $process.StandardInput.BaseStream.Write($InputBytes, 0, $InputBytes.Length) }
        $process.StandardInput.Close()
        $stdout.GetAwaiter().GetResult()
        $process.WaitForExit()
        $null = $stderr.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0) { throw 'GPG failed; no verified custody set was created.' }
    } finally {
        if ($started -and -not $process.HasExited) { $process.Kill($true); $process.WaitForExit() }
        $process.Dispose()
    }
}

function Initialize-StagingOperatorConfig {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$StorageDirectory,
        [Parameter(Mandatory)][string]$FingerprintPath,
        [string]$ExpectedCorpusSha256 = '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da',
        [Parameter(Mandatory)][string]$AllowedOrigin,
        [Parameter(Mandatory)][string]$GpgHome,
        [string]$GpgExecutable = 'gpg.exe',
        [switch]$AcknowledgeProtectedStorage,
        [switch]$AcknowledgeOperatorCustody
    )
    $ErrorActionPreference = 'Stop'
    if (-not $IsWindows -or -not $AcknowledgeProtectedStorage -or -not $AcknowledgeOperatorCustody) { throw 'Windows, protected-storage and operator-custody acknowledgments are required.' }
    Assert-StagingOrigin $AllowedOrigin
    $directory = Assert-StagingExternalPath $StorageDirectory
    if (Test-Path -LiteralPath $directory) { throw 'Storage already exists; never replace or regenerate these keys.' }
    $corpus = Assert-StagingCorpus $FingerprintPath $ExpectedCorpusSha256
    $keyDirectory = Assert-StagingExternalPath $GpgHome
    if (-not [IO.Directory]::Exists($keyDirectory) -or $keyDirectory.StartsWith($directory + '\', [StringComparison]::OrdinalIgnoreCase) -or
        $directory -eq $keyDirectory -or $directory.StartsWith($keyDirectory + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'An existing, separate local GPG home is required.' }
    $executable = Assert-StagingExternalPath (Get-Command $GpgExecutable -CommandType Application -ErrorAction Stop).Source
    $secret = $null; $plain = $null; $text = $null; $restored = $null
    $bstr = [IntPtr]::Zero; $backupStream = $null; $verification = $null
    try {
        New-StagingPrivateDirectory $directory
        $store = Join-Path $directory $script:OperatorStoreName
        $backup = Join-Path $directory $script:OperatorBackupName
        $metadata = Join-Path $directory $script:OperatorMetadataName
        $secret = New-StagingOperatorSecret
        $secret | Export-Clixml -LiteralPath $store -NoClobber -Encoding utf8 -ErrorAction Stop
        Assert-StagingPrivateAcl $store
        $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
        $text = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
        $plain = [Text.Encoding]::UTF8.GetBytes($text)
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr); $bstr = [IntPtr]::Zero; $text = $null
        $backupStream = [IO.File]::Open($backup, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        Invoke-StagingGpg -Executable $executable -KeyHome $keyDirectory -Mode Encrypt -InputBytes $plain -OutputStream $backupStream
        $backupStream.Dispose(); $backupStream = $null
        Assert-StagingPrivateAcl $backup
        if ((Get-Item -LiteralPath $backup).Length -eq 0) { throw 'Empty encrypted backup.' }
        $verification = [IO.MemoryStream]::new()
        Invoke-StagingGpg -Executable $executable -KeyHome $keyDirectory -Mode Decrypt -EncryptedPath $backup -OutputStream $verification
        $restored = $verification.ToArray()
        if (-not [Security.Cryptography.CryptographicOperations]::FixedTimeEquals($plain, $restored)) { throw 'Portable key backup verification failed.' }
        $null = Assert-StagingCorpus $corpus $ExpectedCorpusSha256
        $record = [ordered]@{
            schema = 1; status = 'READY'; environment = 'staging'
            created_at = [DateTime]::UtcNow.ToString('o')
            source = 'CompetenceHub staging operator initializer v1'
            corpus_path = $corpus; corpus_sha256 = $ExpectedCorpusSha256
            corpus_provenance_path = (Join-Path ([IO.Path]::GetDirectoryName($corpus)) 'corpus-provenance.json')
            allowed_origin = $AllowedOrigin; key_versions = $script:OperatorKeyVersions
            recipient = $script:OperatorRecipient; portable_backup_verified = $true
            store_sha256 = (Get-FileHash -LiteralPath $store -Algorithm SHA256).Hash.ToLowerInvariant()
            backup_sha256 = (Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        $metadataStream = [IO.File]::Open($metadata, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try {
            $data = [Text.Encoding]::UTF8.GetBytes(($record | ConvertTo-Json -Depth 5))
            $metadataStream.Write($data, 0, $data.Length)
        } finally { $metadataStream.Dispose() }
        Assert-StagingPrivateAcl $metadata
        return [pscustomobject]@{ status = 'READY'; directory = $directory; store_path = $store; backup_path = $backup; metadata_path = $metadata; store_sha256 = $record.store_sha256; backup_sha256 = $record.backup_sha256 }
    } catch {
        throw 'Staging operator preparation failed. Any new private artifacts are retained; operator review is required. Never rerun with overwrite or new ephemeral keys.'
    } finally {
        if ($backupStream) { $backupStream.Dispose() }
        if ($verification) { [Array]::Clear($verification.GetBuffer(), 0, [int]$verification.Length); $verification.Dispose() }
        if ($plain) { [Array]::Clear($plain, 0, $plain.Length) }
        if ($restored) { [Array]::Clear($restored, 0, $restored.Length) }
        if ($bstr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
        if ($secret) { $secret.Dispose() }
        $text = $null
    }
}

function Use-StagingOperatorEnvironment {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$StorageDirectory,
          [Parameter(Mandatory)][scriptblock]$Action, [switch]$AcknowledgeOperatorCustody)
    $ErrorActionPreference = 'Stop'
    if (-not $AcknowledgeOperatorCustody) { throw 'Private operator custody acknowledgment is required.' }
    $directory = Assert-StagingExternalPath $StorageDirectory
    Assert-StagingPrivateAcl $directory -Directory
    $store = Join-Path $directory $script:OperatorStoreName
    $backup = Join-Path $directory $script:OperatorBackupName
    $metadata = Join-Path $directory $script:OperatorMetadataName
    foreach ($file in @($store, $backup, $metadata)) { Assert-StagingPrivateAcl $file }
    $record = Get-Content -Raw -LiteralPath $metadata -ErrorAction Stop | ConvertFrom-Json -AsHashtable
    if ($record.schema -ne 1 -or $record.environment -cne 'staging' -or $record.status -cne 'READY' -or
        $record.portable_backup_verified -ne $true -or $record.recipient -cne $script:OperatorRecipient -or
        (Get-FileHash -LiteralPath $store -Algorithm SHA256).Hash.ToLowerInvariant() -cne $record.store_sha256 -or
        (Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant() -cne $record.backup_sha256) { throw 'Verified custody metadata/hash gate failed.' }
    Assert-StagingOrigin $record.allowed_origin
    $corpus = Assert-StagingCorpus $record.corpus_path $record.corpus_sha256
    $secret = $null; $text = $null; $payload = $null
    $bstr = [IntPtr]::Zero; $previous = @{}
    try {
        $secret = Import-Clixml -LiteralPath $store -ErrorAction Stop
        if ($secret -isnot [Security.SecureString]) { throw 'The DPAPI store must contain one SecureString.' }
        $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
        $text = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
        $payload = $text | ConvertFrom-Json -AsHashtable -ErrorAction Stop
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr); $bstr = [IntPtr]::Zero; $text = $null
        $expected = @('COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY', 'COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY')
        foreach ($stem in @('TOTP', 'OUTBOX', 'RECOVERY_HMAC')) {
            $expected += "COMPETENCE_HUB_${stem}_KEYRING", "COMPETENCE_HUB_${stem}_ACTIVE_KEY_VERSION"
        }
        if ($payload.schema -ne 1 -or $payload.environment -cne 'staging' -or
            $payload.variables -isnot [Collections.IDictionary] -or
            (@(Compare-Object @($payload.variables.Keys) $expected)).Count) { throw 'Unexpected secret payload schema.' }
        $variables = $payload.variables
        $unique = [Collections.Generic.HashSet[string]]::new()
        foreach ($name in @('COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY', 'COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY')) {
            $decoded = [Convert]::FromBase64String($variables[$name])
            try { if ($decoded.Length -ne 32 -or -not $unique.Add($variables[$name])) { throw 'Invalid distinct-key contract.' } }
            finally { [Array]::Clear($decoded, 0, $decoded.Length) }
        }
        foreach ($purpose in @('totp', 'outbox', 'recovery')) {
            $stem = @{totp = 'TOTP'; outbox = 'OUTBOX'; recovery = 'RECOVERY_HMAC'}[$purpose]
            $version = $script:OperatorKeyVersions[$purpose]
            $ring = $variables["COMPETENCE_HUB_${stem}_KEYRING"] | ConvertFrom-Json -AsHashtable -ErrorAction Stop
            if ($ring.Count -ne 1 -or -not $ring.ContainsKey($version) -or
                $record.key_versions[$purpose] -cne $version -or
                $variables["COMPETENCE_HUB_${stem}_ACTIVE_KEY_VERSION"] -cne $version) { throw 'Invalid key-version contract.' }
            $decoded = [Convert]::FromBase64String($ring[$version])
            try { if ($decoded.Length -ne 32 -or -not $unique.Add($ring[$version])) { throw 'Invalid distinct-key contract.' } }
            finally { [Array]::Clear($decoded, 0, $decoded.Length) }
        }
        $variables['COMPETENCE_HUB_ALLOWED_ORIGIN'] = $record.allowed_origin
        $variables['COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH'] = $corpus
        foreach ($name in $variables.Keys) {
            $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
            [Environment]::SetEnvironmentVariable($name, $variables[$name], 'Process')
        }
        # This loader has no pipeline output, even if a callback returns a value.
        # The caller may explicitly write non-secret operator status to the host.
        $null = & $Action
    } catch {
        throw 'Private operator environment failed; secret details are suppressed.'
    } finally {
        foreach ($name in $previous.Keys) {
            # Preserve absent versus empty variables on PowerShell/.NET versions
            # that otherwise coerce $null to an empty string at this boundary.
            if ($null -eq $previous[$name]) { [Environment]::SetEnvironmentVariable($name, [NullString]::Value, 'Process') }
            else { [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process') }
        }
        if ($bstr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
        if ($secret -is [Security.SecureString]) { $secret.Dispose() }
        $previous.Clear(); $payload = $null; $text = $null; $variables = $null; $ring = $null; $unique = $null
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    Initialize-StagingOperatorConfig -StorageDirectory $StorageDirectory -FingerprintPath $FingerprintPath `
        -ExpectedCorpusSha256 $ExpectedCorpusSha256 -AllowedOrigin $AllowedOrigin -GpgHome $GpgHome `
        -GpgExecutable $GpgExecutable -AcknowledgeProtectedStorage:$AcknowledgeProtectedStorage `
        -AcknowledgeOperatorCustody:$AcknowledgeOperatorCustody
}
