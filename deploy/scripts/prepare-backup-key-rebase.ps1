#requires -Version 7.2
<#
Additive LOCAL rewrap only, not key generation, activation, backup or bootstrap.
No real execution by default. New GPG homes must already be separately approved
and populated, including a distinct home recovered from the protected export.
Original application keys and old custody files remain unchanged.
#>
[CmdletBinding()]
param(
    [switch]$Execute,
    [string]$ExpectedSourceCommit,
    [string]$SourceStorageDirectory,
    [string]$DestinationStorageDirectory,
    [string]$NewGpgHome,
    [string]$RecoveredGpgHome,
    [string]$NewRecipient,
    [string]$GpgExecutable = 'C:\Program Files\GnuPG\bin\gpg.exe',
    [switch]$AcknowledgeProtectedStorage,
    [switch]$AcknowledgeRecoveredPrivateKey,
    [switch]$AcknowledgePassphraseCustody
)

. (Join-Path $PSScriptRoot 'initialize-staging-operator-config.ps1') -GpgExecutable $GpgExecutable -AcknowledgeProtectedStorage:$AcknowledgeProtectedStorage

function New-StagingOperatorRebaseCandidate {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$SourceStorageDirectory,
        [Parameter(Mandatory)][string]$DestinationStorageDirectory,
        [Parameter(Mandatory)][string]$NewGpgHome,
        [Parameter(Mandatory)][string]$RecoveredGpgHome,
        [Parameter(Mandatory)][string]$NewRecipient,
        [Parameter(Mandatory)][string]$GpgExecutable,
        [Parameter(Mandatory)][string]$FingerprintPath,
        [Parameter(Mandatory)][string]$ExpectedCorpusSha256,
        [Parameter(Mandatory)][string]$AllowedOrigin,
        [switch]$AcknowledgeProtectedStorage,
        [switch]$AcknowledgeRecoveredPrivateKey,
        [switch]$AcknowledgePassphraseCustody
    )
    $ErrorActionPreference = 'Stop'
    Set-StrictMode -Version Latest
    $script:RebasePhase='preflight'
    if (-not $IsWindows -or -not $AcknowledgeProtectedStorage -or
        -not $AcknowledgeRecoveredPrivateKey -or -not $AcknowledgePassphraseCustody) { throw 'REBASE_PRIVATE_CUSTODY_APPROVALS_REQUIRED' }
    foreach ($name in [Environment]::GetEnvironmentVariables('Process').Keys) {
        if ($name -match '^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON)' -or $name -like 'COMPETENCE_HUB_*') { throw 'REBASE_CLEAN_PRIVATE_PROCESS_REQUIRED' }
    }
    if ($NewRecipient -cnotmatch '^[A-F0-9]{40}$' -or $NewRecipient -ceq $script:OperatorRecipient -or
        $NewRecipient -cmatch '^(.)\1{39}$') { throw 'REBASE_NEW_FULL_FINGERPRINT_REQUIRED' }
    Assert-StagingOrigin $AllowedOrigin
    $corpus = Assert-StagingCorpus $FingerprintPath $ExpectedCorpusSha256
    $source = Assert-StagingExternalPath $SourceStorageDirectory
    $destination = Assert-StagingExternalPath $DestinationStorageDirectory
    $newHome = Assert-StagingExternalPath $NewGpgHome
    $recoveredHome = Assert-StagingExternalPath $RecoveredGpgHome
    $oldHome = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'CompetenceHub/backup-gnupg'))
    $paths = @($source,$destination,$newHome,$recoveredHome,$oldHome)
    for ($i=0; $i -lt $paths.Count; $i++) {
        for ($j=$i+1; $j -lt $paths.Count; $j++) {
            if ($paths[$i] -eq $paths[$j] -or $paths[$i].StartsWith($paths[$j]+'\',[StringComparison]::OrdinalIgnoreCase) -or
                $paths[$j].StartsWith($paths[$i]+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'REBASE_DISJOINT_PATHS_REQUIRED' }
        }
    }
    if (Test-Path -LiteralPath $destination) { throw 'REBASE_DESTINATION_EXISTS_NO_OVERWRITE' }
    foreach ($directory in @($source,$newHome,$recoveredHome)) { Assert-StagingPrivateAcl $directory -Directory }
    if (Test-Path -LiteralPath (Join-Path $source 'bootstrap-attempt.json')) { throw 'REBASE_PRIOR_ACCOUNT_ATTEMPT_REQUIRES_REVIEW' }
    $store = Join-Path $source $script:OperatorStoreName
    Assert-StagingPrivateAcl $store
    # Hash all existing flat custody artifacts; do not decrypt the August backup.
    $originals = @{}
    foreach ($name in @($script:OperatorStoreName,$script:OperatorBackupName,$script:OperatorMetadataName)) {
        $path = Join-Path $source $name
        if (Test-Path -LiteralPath $path) {
            Assert-StagingPrivateAcl $path
            $originals[$name] = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
        }
    }
    $executable = Assert-StagingExternalPath (Get-Command $GpgExecutable -CommandType Application -ErrorAction Stop).Source
    $secret=$null; $plain=$null; $restored=$null; $buffer=$null; $output=$null
    $bstr=[IntPtr]::Zero; $text=$null; $payload=$null
    try {
        $script:RebasePhase='dpapi_payload'
        $secret = Import-Clixml -LiteralPath $store -ErrorAction Stop
        if ($secret -isnot [Security.SecureString]) { throw 'REBASE_DPAPI_SECURESTRING_REQUIRED' }
        $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
        $text = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
        $plain = [Text.Encoding]::UTF8.GetBytes($text)
        $payload = $text | ConvertFrom-Json -AsHashtable -ErrorAction Stop
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr); $bstr=[IntPtr]::Zero; $text=$null
        Assert-StagingOperatorPayload $payload $script:OperatorKeyVersions
        New-StagingPrivateDirectory $destination
        $newStore = Join-Path $destination $script:OperatorStoreName
        # Copy DPAPI ciphertext verbatim, never generate or serialize new keys.
        $inputStream=[IO.File]::OpenRead($store)
        try {
            $output=New-StagingPrivateFileStream $newStore
            $inputStream.CopyTo($output); $output.Flush($true)
            $output.Dispose(); $output=$null
        } finally { $inputStream.Dispose() }
        Assert-StagingPrivateAcl $newStore
        if ((Get-FileHash -LiteralPath $newStore -Algorithm SHA256).Hash -cne $originals[$script:OperatorStoreName]) { throw 'REBASE_DPAPI_COPY_CHANGED' }
        $backup = Join-Path $destination $script:OperatorBackupName
        $script:RebasePhase='new_encryption'
        $output = New-StagingPrivateFileStream $backup
        Invoke-StagingGpg -Executable $executable -KeyHome $newHome -Mode Encrypt -Recipient $NewRecipient -InputBytes $plain -OutputStream $output
        $output.Flush($true); $output.Dispose(); $output=$null
        Assert-StagingPrivateAcl $backup
        if ((Get-Item -LiteralPath $backup).Length -eq 0) { throw 'REBASE_EMPTY_PORTABLE_BACKUP' }
        # Test recovery using the separately restored NEW key, not the live home.
        $buffer = [IO.MemoryStream]::new()
        $script:RebasePhase='recovered_key_comparison'
        Invoke-StagingGpg -Executable $executable -KeyHome $recoveredHome -Mode Decrypt -Recipient $NewRecipient -EncryptedPath $backup -OutputStream $buffer
        $restored = $buffer.ToArray()
        if (-not [Security.Cryptography.CryptographicOperations]::FixedTimeEquals($plain,$restored)) { throw 'REBASE_RECOVERY_PAIR_MISMATCH' }
        foreach ($name in $originals.Keys) {
            if ((Get-FileHash -LiteralPath (Join-Path $source $name) -Algorithm SHA256).Hash -cne $originals[$name]) { throw 'REBASE_ORIGINAL_CHANGED' }
        }
        $null = Assert-StagingCorpus $corpus $ExpectedCorpusSha256
        $record = [ordered]@{
            schema=1; status='READY'; environment='staging'; created_at=[DateTime]::UtcNow.ToString('o')
            source='CompetenceHub existing-DPAPI rewrap candidate v1'
            corpus_path=$corpus; corpus_sha256=$ExpectedCorpusSha256
            corpus_provenance_path=(Join-Path ([IO.Path]::GetDirectoryName($corpus)) 'corpus-provenance.json')
            allowed_origin=$AllowedOrigin; key_versions=$script:OperatorKeyVersions
            recipient=$NewRecipient; portable_backup_verified=$true
            store_sha256=$originals[$script:OperatorStoreName].ToLowerInvariant()
            backup_sha256=(Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        $metadata = Join-Path $destination $script:OperatorMetadataName
        $script:RebasePhase='candidate_metadata'
        $output = New-StagingPrivateFileStream $metadata
        $data = [Text.Encoding]::UTF8.GetBytes(($record | ConvertTo-Json -Depth 5))
        $output.Write($data,0,$data.Length); $output.Flush($true); $output.Dispose(); $output=$null
        $script:RebasePhase='candidate_loader'
        Use-StagingOperatorEnvironment -StorageDirectory $destination -ExpectedRecipient $NewRecipient -AcknowledgeOperatorCustody -Action { }
        return [pscustomobject]@{status='LOCAL_REWRAP_PASS'; application_keys='UNCHANGED'; recipient=$NewRecipient; database_backup='NOT_EXECUTED'; admin='NOT_EXECUTED'; activation='NOT_EXECUTED'}
    } catch {
        throw ('REBASE_NOT_COMPLETE_PHASE_' + $script:RebasePhase + '_ARTIFACTS_PRESERVED')
    } finally {
        if ($output) { $output.Dispose() }
        if ($buffer) { [Array]::Clear($buffer.GetBuffer(),0,[int]$buffer.Length); $buffer.Dispose() }
        if ($plain) { [Array]::Clear($plain,0,$plain.Length) }
        if ($restored) { [Array]::Clear($restored,0,$restored.Length) }
        if ($bstr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
        if ($secret -is [Security.SecureString]) { $secret.Dispose() }
        $text=$null; $payload=$null
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    if (-not $Execute) {
        Write-Output 'BACKUP_KEY_REBASE=PLAN_ONLY KEY_GENERATION=NOT_EXECUTED SERVER_ACTIONS=NONE REAL_COACH_APPLY=DISABLED'
    } else {
        try {
            $selectedGpg=$GpgExecutable; $rebaseCommit=$ExpectedSourceCommit; $storageApproved=$AcknowledgeProtectedStorage
            . (Join-Path $PSScriptRoot '../../apps/webapp/scripts/verify-staging-keys.ps1')
            Assert-LocalKeyEnvironment
            Assert-LocalKeySource $rebaseCommit
            $base = Join-Path $env:LOCALAPPDATA 'CompetenceHub'
            $inputs = @{
                SourceStorageDirectory=$SourceStorageDirectory; DestinationStorageDirectory=$DestinationStorageDirectory
                NewGpgHome=$NewGpgHome; RecoveredGpgHome=$RecoveredGpgHome; NewRecipient=$NewRecipient; GpgExecutable=$selectedGpg
                FingerprintPath=(Join-Path $base 'staging-operator-corpus-20261030/compromised-password-fingerprints.sha256')
                ExpectedCorpusSha256='80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da'; AllowedOrigin='https://127.0.0.1:443'
                AcknowledgeProtectedStorage=$storageApproved; AcknowledgeRecoveredPrivateKey=$AcknowledgeRecoveredPrivateKey
                AcknowledgePassphraseCustody=$AcknowledgePassphraseCustody
            }
            $null = New-StagingOperatorRebaseCandidate @inputs
            Write-Output 'BACKUP_KEY_REBASE=LOCAL_REWRAP_PASS APPLICATION_KEYS=UNCHANGED ACTIVATION=NONE SERVER_ACTIONS=NONE'
        } catch {
            [Console]::Error.WriteLine('BACKUP_KEY_REBASE=STOP PRIVATE_REVIEW_REQUIRED NO_OVERWRITE SERVER_ACTIONS=NONE')
            exit 1
        }
    }
}
