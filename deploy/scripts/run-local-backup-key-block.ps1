#requires -Version 7.2
<#
Manuel's explicitly approved LOCAL key block only. Native Pinentry owns all
passphrase entry. No server, DB, bootstrap, scheduler, deletion or activation.
Private artifacts live outside Git; resume never regenerates an existing home.
#>
[CmdletBinding()]
param([switch]$Execute,[string]$ExpectedSourceCommit,
      [ValidatePattern('^([A-F0-9]{40})?$')][string]$ExistingFingerprint,
      [ValidateSet('','PasswordManager','ProtectedOffline')][string]$PassphraseCustody)

$entryExecute=$Execute; $entryCommit=$ExpectedSourceCommit
$entryFingerprint=$ExistingFingerprint; $entryCustody=$PassphraseCustody
. (Join-Path $PSScriptRoot 'prepare-backup-key-rebase.ps1')
. (Join-Path $PSScriptRoot '../../apps/webapp/scripts/verify-staging-keys.ps1')

function Get-LocalBackupBlockPaths {
    $base=Join-Path $env:LOCALAPPDATA 'CompetenceHub'
    $root=Join-Path $base 'backup-key-rebase-20261104'
    return @{
        root=$root; source=(Join-Path $base 'staging-operator')
        live=(Join-Path $root 'live-gnupg'); recovered=(Join-Path $root 'recovered-gnupg')
        candidate=(Join-Path $root 'application-candidate'); usb='D:\CompetenceHub'
        corpus=(Join-Path $base 'staging-operator-corpus-20261030/compromised-password-fingerprints.sha256')
        gpg='C:\Program Files\GnuPG\bin\gpg.exe'; gpgconf='C:\Program Files\GnuPG\bin\gpgconf.exe'
    }
}

function Assert-LocalKeyVolumes {
    param([string]$LocalDirectory,[string]$UsbDirectory)
    Assert-ResumeUsb $UsbDirectory
    foreach ($path in @($LocalDirectory,$UsbDirectory)) {
        $mount=[IO.Path]::GetPathRoot($path)
        try { $volume=Get-BitLockerVolume -MountPoint $mount -ErrorAction Stop }
        catch { throw 'KEY_VOLUME_STATUS_UNAVAILABLE_USE_SAME_USER_ELEVATED_POWERSHELL' }
        if ([string]$volume.VolumeStatus -cne 'FullyEncrypted' -or [string]$volume.ProtectionStatus -cne 'On' -or
            [string]$volume.LockStatus -cne 'Unlocked') { throw 'KEY_VOLUME_PROTECTION_REQUIRED_NO_UNLOCK_ATTEMPT' }
        if ([IO.DriveInfo]::new($mount).AvailableFreeSpace -lt 16MB) { throw 'KEY_VOLUME_SPACE_REQUIRED' }
    }
}

function Write-KeyBlockFile {
    param([string]$Path,[byte[]]$Bytes,[switch]$PrivateFile)
    $stream=if ($PrivateFile) { New-StagingPrivateFileStream $Path } else { [IO.File]::Open($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None) }
    try { $stream.Write($Bytes,0,$Bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    if ($PrivateFile) { Assert-StagingPrivateAcl $Path }
}

function Write-KeyBlockReceipt {
    param([string]$Path,[Collections.IDictionary]$Record)
    Write-KeyBlockFile $Path ([Text.Encoding]::UTF8.GetBytes(($Record | ConvertTo-Json -Depth 6 -Compress))) -PrivateFile
    Assert-StagingPrivateAcl $Path
}

function Read-KeyBlockReceipt {
    param([string]$Path)
    Assert-StagingPrivateAcl $Path
    if ((Get-Item -LiteralPath $Path).Length -gt 65536) { throw 'KEY_RECEIPT_SIZE_REJECTED' }
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -AsHashtable
}

function Read-KeyBlockAuthorization {
    param([string]$Root)
    Assert-StagingPrivateAcl $Root -Directory
    $path=Join-Path $Root 'authorization.json'
    $null=Assert-StagingExternalPath $path
    $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if ($item.PSIsContainer -or $item.Length -gt 65536) { throw 'KEY_AUTHORIZATION_INVALID' }
    $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl=Get-Acl -LiteralPath $path -ErrorAction Stop
    $owner=$acl.GetOwner([Security.Principal.SecurityIdentifier]).Value
    if ($owner -cnotin @($sid.Value,'S-1-5-32-544')) { throw 'KEY_AUTHORIZATION_OWNER_UNTRUSTED' }
    Assert-StagingPrivateAccessRules $acl $sid
    $record=Get-Content -Raw -LiteralPath $path | ConvertFrom-Json -AsHashtable
    if (@(Compare-Object @($record.Keys) @('schema','scope','source_commit','source_hashes') -CaseSensitive).Count -or
        $record.schema -ne 1 -or $record.scope -cne 'LOCAL_KEY_REBASE_ONLY' -or
        $record.source_commit -cnotmatch '^[a-f0-9]{40}$' -or
        $record.source_hashes -isnot [Collections.IDictionary]) { throw 'KEY_AUTHORIZATION_INVALID' }
    # Read-only exception solely for this known non-secret failed receipt.
    # Private-key/application files and generic receipt validation stay strict.
    if ($owner -ceq 'S-1-5-32-544' -and
        $record.source_commit -cne '5b0f7ab24f1179b2b8c330bc37d3581f77e1b55a') { throw 'KEY_AUTHORIZATION_LEGACY_OWNER_NOT_BOUND' }
    foreach ($name in $record.source_hashes.Keys) {
        if ($name -cnotin @($script:OperatorStoreName,$script:OperatorBackupName,$script:OperatorMetadataName) -or
            $record.source_hashes[$name] -cnotmatch '^[A-F0-9]{64}$') { throw 'KEY_AUTHORIZATION_INVALID' }
    }
    return $record
}

function Confirm-KeyBlockCustody {
    param([string]$Root,[string]$Fingerprint,
          [ValidateSet('','PasswordManager','ProtectedOffline')][string]$Method)
    $legacy=Join-Path $Root 'passphrase-custody.json'
    $path=Join-Path $Root 'passphrase-custody-v2.json'
    $legacyHash=$null
    if (Test-Path -LiteralPath $legacy) {
        $previous=Read-KeyBlockReceipt $legacy
        if ($previous.schema -ne 1 -or $previous.fingerprint -cne $Fingerprint -or
            $previous.password_manager_confirmed -isnot [bool] -or -not $previous.password_manager_confirmed) { throw 'KEY_CUSTODY_RECEIPT_INVALID' }
        $legacyHash=(Get-FileHash -LiteralPath $legacy -Algorithm SHA256).Hash
    }
    if (Test-Path -LiteralPath $path) {
        $receipt=Read-KeyBlockReceipt $path
        if ($receipt.schema -ne 2 -or $receipt.fingerprint -cne $Fingerprint -or
            $receipt.method -cnotin @('PasswordManager','ProtectedOffline') -or
            $receipt.confirmed -isnot [bool] -or -not $receipt.confirmed -or
            $receipt.second_recovery -cne 'OPEN' -or $receipt.legacy_receipt_sha256 -cne $legacyHash -or
            ($Method -and $receipt.method -cne $Method)) { throw 'KEY_CUSTODY_RECEIPT_INVALID' }
        return
    }
    # An explicit non-secret method confirms custody without another prompt.
    # Preserve the old receipt; the new record corrects its manager-only wording.
    if (-not $Method -and $legacyHash) { $Method='PasswordManager' }
    if (-not $Method) {
        $answer=Read-Host 'Passphrase sicher verwahrt? PASSWORTMANAGER oder OFFLINE (geschuetzt und getrennt vom USB); leer = Abbruch. Kein Passwort eingeben'
        $Method=switch (([string]$answer).Trim().ToUpperInvariant()) {
            'PASSWORTMANAGER' { 'PasswordManager' }
            'OFFLINE' { 'ProtectedOffline' }
            default { '' }
        }
        if (-not $Method) {
            Write-Host 'Nicht bestaetigt. Erwartet: PASSWORTMANAGER oder OFFLINE; Dateien bleiben unveraendert.'
            throw 'KEY_PASSPHRASE_CUSTODY_NOT_CONFIRMED'
        }
    }
    Write-KeyBlockReceipt $path @{
        schema=2;fingerprint=$Fingerprint;method=$Method;confirmed=$true
        legacy_receipt_sha256=$legacyHash;second_recovery='OPEN'
    }
}

function Invoke-LocalKeyGpg {
    param([Collections.IDictionary]$Paths,[string]$KeyHome,
          [ValidateSet('Generate','Metadata','SecretExport','PublicExport','Packets','Import')][string]$Operation,
          [string]$Fingerprint,[string]$File,[byte[]]$InputBytes)
    $script:KeyGpgFailureCode=0
    if ($KeyHome -cnotin @($Paths.live,$Paths.recovered)) { throw 'KEY_GPG_HOME_NOT_OWNED' }
    Assert-StagingPrivateAcl $KeyHome -Directory
    $start=[Diagnostics.ProcessStartInfo]::new()
    $start.FileName=$Paths.gpg; $start.UseShellExecute=$false; $start.CreateNoWindow=$true
    $start.RedirectStandardInput=$true; $start.RedirectStandardOutput=$true; $start.RedirectStandardError=$true
    foreach ($argument in @('--no-options','--homedir',$KeyHome,'--no-auto-key-retrieve','--auto-key-locate','clear','--no-auto-key-import','--pinentry-mode','ask','--status-fd','2')) { $start.ArgumentList.Add($argument) }
    $arguments=switch ($Operation) {
        Generate {
            $uid=if ($Paths.Contains('uid')) { $Paths.uid } else { 'Competence Hub Staging Backup 2026-11' }
            if ($uid -cnotin @('Competence Hub Staging Backup 2026-11','Competence Hub Staging Backup Recovery 2026-11-05 R2')) { throw 'KEY_DEDICATED_UID_REQUIRED' }
            @('--batch','--quick-generate-key',$uid,'rsa4096','encr','2y')
        }
        Metadata { @('--batch','--with-colons','--fingerprint','--list-secret-keys') }
        SecretExport { @('--export-secret-keys',$Fingerprint) }
        PublicExport { @('--batch','--armor','--export',$Fingerprint) }
        Packets { if ($InputBytes) { @('--batch','--list-packets') } else { @('--batch','--list-packets',$File) } }
        Import { @('--batch','--import',$File) }
    }
    foreach ($argument in $arguments) { $start.ArgumentList.Add($argument) }
    $process=[Diagnostics.Process]::new(); $process.StartInfo=$start
    $output=[IO.MemoryStream]::new(); $started=$false
    try {
        $null=$process.Start(); $started=$true
        $stderr=$process.StandardError.ReadToEndAsync()
        $copy=$process.StandardOutput.BaseStream.CopyToAsync($output)
        if ($InputBytes) { $process.StandardInput.BaseStream.Write($InputBytes,0,$InputBytes.Length) }
        $process.StandardInput.Close()
        if (-not $process.WaitForExit(900000)) { throw 'KEY_GPG_DIALOG_TIMEOUT' }
        $null=$copy.GetAwaiter().GetResult(); $diagnostics=$stderr.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0 -or $output.Length -gt 1MB) {
            # Fixed numeric libgpg-error status only; never expose raw diagnostics.
            $failure=[regex]::Match($diagnostics,'(?m)^\[GNUPG:\] (?:FAILURE|ERROR) \S+ ([0-9]+)')
            $script:KeyGpgFailureCode=if ($failure.Success) { [int]([long]$failure.Groups[1].Value -band 65535) } else { 0 }
            throw 'KEY_GPG_OPERATION_NOT_COMPLETE'
        }
        # The caller owns/clears the byte array. Never stringify secret export.
        return ,$output.ToArray()
    } finally {
        if ($started -and -not $process.HasExited) { $process.Kill($true); $process.WaitForExit() }
        [Array]::Clear($output.GetBuffer(),0,[int]$output.Length); $output.Dispose(); $process.Dispose()
    }
}

function Get-LocalBackupFingerprint {
    param([byte[]]$Metadata,
          [ValidateSet('Competence Hub Staging Backup 2026-11','Competence Hub Staging Backup Recovery 2026-11-05 R2')]
          [string]$ExpectedUid='Competence Hub Staging Backup 2026-11')
    $lines=[Text.Encoding]::UTF8.GetString($Metadata) -split '\r?\n'
    $primary=@($lines | Where-Object { $_.StartsWith('sec:') })
    $users=@($lines | Where-Object { $_.StartsWith('uid:') })
    $fingerprints=@($lines | Where-Object { $_.StartsWith('fpr:') })
    if ($primary.Count -ne 1 -or $users.Count -ne 1 -or $fingerprints.Count -ne 1) { throw 'KEY_PROFILE_NOT_SINGLE_DEDICATED_IDENTITY' }
    $fields=$primary[0].Split(':')
    if ($fields.Count -lt 12 -or $fields[1] -cin @('r','e','d') -or $fields[2] -cne '4096' -or
        $fields[3] -cne '1' -or $fields[11] -cnotmatch '[eE]' -or
        $users[0].Split(':')[9] -cne $ExpectedUid) { throw 'KEY_DEDICATED_RSA4096_ENCRYPTION_REQUIRED' }
    $fingerprint=$fingerprints[0].Split(':')[9]
    if ($fingerprint -cnotmatch '^[A-F0-9]{40}$' -or $fingerprint -ceq $script:OperatorRecipient) { throw 'KEY_NEW_FULL_FINGERPRINT_REQUIRED' }
    return $fingerprint
}

function Assert-ProtectedSecretExport {
    param([byte[]]$PacketMetadata)
    # GPG's diagnostic packet format is fail-closed and version-bounded here;
    # no key packet is parsed/reimplemented and none of its text is logged.
    $blocks=[regex]::Split([Text.Encoding]::UTF8.GetString($PacketMetadata),'(?m)^:')
    $secret=@($blocks | Where-Object { $_ -cmatch '^secret (sub )?key packet:' })
    if ($secret.Count -lt 1) { throw 'KEY_PROTECTED_SECRET_EXPORT_REQUIRED' }
    foreach ($block in $secret) {
        if ($block -cnotmatch '(?m)^\s*skey\[[0-9]+\]: \[v4 protected\]\s*$' -or
            $block -cnotmatch 'S2K, algo: [789],') { throw 'KEY_UNPROTECTED_OR_UNKNOWN_EXPORT_REJECTED' }
    }
}

function Copy-KeyBlockCiphertext {
    param([string]$Source,[string]$Target,[string]$ExpectedHash)
    $parent=Split-Path -Parent $Target
    foreach ($path in @($parent,$Target)) {
        if (Test-Path -LiteralPath $path) {
            if ((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'KEY_USB_REPARSE_REJECTED' }
        }
    }
    if ((Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash -cne $ExpectedHash) { throw 'KEY_COPY_SOURCE_CHANGED' }
    if (-not (Test-Path -LiteralPath $Target)) { [IO.File]::Copy($Source,$Target,$false) }
    if ((Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash -cne $ExpectedHash -or
        (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash -cne $ExpectedHash) { throw 'KEY_COPY_HASH_CONFLICT_NO_OVERWRITE' }
}

function Assert-KeyBlockOriginals {
    param([string]$Source,[Collections.IDictionary]$Hashes)
    foreach ($name in $Hashes.Keys) {
        if ((Get-FileHash -LiteralPath (Join-Path $Source $name) -Algorithm SHA256).Hash -cne $Hashes[$name]) { throw 'KEY_ORIGINAL_ARTIFACT_CHANGED' }
    }
}

function Test-KeyBlockDpapi {
    param([string]$Store)
    $secret=$null; $pointer=[IntPtr]::Zero; $text=$null; $payload=$null
    try {
        $secret=Import-Clixml -LiteralPath $Store -ErrorAction Stop
        if ($secret -isnot [Security.SecureString]) { throw 'KEY_EXISTING_DPAPI_REQUIRED' }
        $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
        $text=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
        $payload=$text | ConvertFrom-Json -AsHashtable -ErrorAction Stop
        Assert-StagingOperatorPayload $payload $script:OperatorKeyVersions
    } finally {
        if ($pointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
        if ($secret -is [Security.SecureString]) { $secret.Dispose() }
        $text=$null; $payload=$null
    }
}

function Test-KeyBlockApplicationRecovery {
    param([Collections.IDictionary]$Paths,[string]$Fingerprint)
    $store=Join-Path $Paths.source $script:OperatorStoreName
    $secret=$null; $pointer=[IntPtr]::Zero; $plain=$null; $restored=$null
    $stream=[IO.MemoryStream]::new()
    try {
        $secret=Import-Clixml -LiteralPath $store -ErrorAction Stop
        if ($secret -isnot [Security.SecureString]) { throw 'KEY_EXISTING_DPAPI_REQUIRED' }
        $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
        $plain=[Text.Encoding]::UTF8.GetBytes([Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer))
        Invoke-StagingGpg -Executable $Paths.gpg -KeyHome $Paths.recovered -Mode Decrypt -Recipient $Fingerprint -EncryptedPath (Join-Path $Paths.candidate $script:OperatorBackupName) -OutputStream $stream
        $restored=$stream.ToArray()
        if (-not [Security.Cryptography.CryptographicOperations]::FixedTimeEquals($plain,$restored)) { throw 'KEY_APPLICATION_RECOVERY_MISMATCH' }
    } finally {
        if ($pointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
        if ($secret -is [Security.SecureString]) { $secret.Dispose() }
        if ($plain) { [Array]::Clear($plain,0,$plain.Length) }
        if ($restored) { [Array]::Clear($restored,0,$restored.Length) }
        [Array]::Clear($stream.GetBuffer(),0,[int]$stream.Length); $stream.Dispose()
    }
}

function Write-KeyBlockUsbNotes {
    param([string]$Usb,[string]$Fingerprint,[string]$PrivateHash,[string]$ApplicationHash)
    $lf=[string][char]10
    $notes=@('Competence Hub - lokale Schluessel-Recovery',
        ('Fingerprint: '+$Fingerprint),
        'Passphrase separat im Passwortmanager oder geschuetzt schriftlich offline, nicht auf diesem Stick.',
        'backup-private-key.gpg nur in ein neues geschuetztes GPG-Profil importieren.',
        'application-keys.json.gpg enthaelt die unveraenderten Portal-Anwendungsschluessel.',
        'Kein Datenbankbackup. Zweite unabhaengige Recovery-Kopie noch OFFEN.')
    $texts=@{
        SHA256SUMS=($PrivateHash.ToLowerInvariant()+'  backup-private-key.gpg'+$lf+$ApplicationHash.ToLowerInvariant()+'  application-keys.json.gpg'+$lf)
        'RECOVERY-NOTES-v2.txt'=(($notes -join $lf)+$lf)
    }
    foreach ($name in $texts.Keys) {
        $path=Join-Path $Usb $name
        $bytes=[Text.Encoding]::UTF8.GetBytes($texts[$name])
        if (-not (Test-Path -LiteralPath $path)) { Write-KeyBlockFile $path $bytes }
        if ((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint -or
            (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -cne [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))) { throw 'KEY_USB_NOTES_CONFLICT_NO_OVERWRITE' }
    }
}

function Stop-OwnedRecoveryAgent {
    param([Collections.IDictionary]$Paths)
    Assert-StagingPrivateAcl $Paths.recovered -Directory
    $start=[Diagnostics.ProcessStartInfo]::new()
    $start.FileName=$Paths.gpgconf; $start.UseShellExecute=$false; $start.CreateNoWindow=$true
    $start.RedirectStandardOutput=$true; $start.RedirectStandardError=$true
    foreach ($argument in @('--homedir',$Paths.recovered,'--kill','gpg-agent')) { $start.ArgumentList.Add($argument) }
    $process=[Diagnostics.Process]::new(); $process.StartInfo=$start
    try {
        $null=$process.Start()
        $out=$process.StandardOutput.ReadToEndAsync(); $err=$process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit(30000)) { $process.Kill($true); throw 'KEY_OWNED_AGENT_STOP_FAILED' }
        $null=$out.GetAwaiter().GetResult(); $null=$err.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0) { throw 'KEY_OWNED_AGENT_STOP_FAILED' }
    } finally { $process.Dispose() }
}

function Invoke-LocalBackupKeyBlock {
    param([string]$Commit,
          [ValidatePattern('^([A-F0-9]{40})?$')][string]$ExistingFingerprint,
          [ValidateSet('','PasswordManager','ProtectedOffline')][string]$PassphraseCustody)
    $ErrorActionPreference='Stop'; Set-StrictMode -Version Latest
    $script:KeyBlockPhase='preflight'
    $script:KeyBlockStep='source'
    Assert-LocalKeyEnvironment
    Assert-LocalKeySource $Commit
    if ($ExistingFingerprint -ceq '22C82A2F175DAFB04B019502E92DE7854AF99C1F') { throw 'KEY_EXPORT_ON_HOLD_NO_UNLOCK' }
    $paths=Get-LocalBackupBlockPaths
    if ($ExistingFingerprint -and -not [IO.Directory]::Exists($paths.live)) { throw 'KEY_EXISTING_PROFILE_REQUIRED_NO_GENERATION' }
    $script:KeyBlockStep='source_acl'
    $null=Assert-StagingExternalPath $paths.root
    Assert-StagingPrivateAcl $paths.source -Directory
    $script:KeyBlockStep='corpus'
    $null=Assert-StagingCorpus $paths.corpus '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da'
    $script:KeyBlockStep='tools'
    foreach ($tool in @($paths.gpg,$paths.gpgconf)) { $null=Assert-StagingExternalPath (Get-Command $tool -CommandType Application -ErrorAction Stop).Source }
    $script:KeyBlockStep='volume_status'
    Assert-LocalKeyVolumes $paths.root $paths.usb
    $script:KeyBlockStep='source_hashes'
    $hashes=@{}
    foreach ($name in @($script:OperatorStoreName,$script:OperatorBackupName,$script:OperatorMetadataName)) {
        $file=Join-Path $paths.source $name
        if (Test-Path -LiteralPath $file) { Assert-StagingPrivateAcl $file; $hashes[$name]=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash }
    }
    if (-not $hashes.ContainsKey($script:OperatorStoreName) -or (Test-Path -LiteralPath (Join-Path $paths.source 'bootstrap-attempt.json'))) { throw 'KEY_SOURCE_CUSTODY_REVIEW_REQUIRED' }
    $script:KeyBlockStep='dpapi_payload'
    Test-KeyBlockDpapi (Join-Path $paths.source $script:OperatorStoreName)
    $script:KeyBlockStep='authorization_receipt'
    $authorization=Join-Path $paths.root 'authorization.json'
    if (-not (Test-Path -LiteralPath $paths.root)) {
        New-StagingPrivateDirectory $paths.root
        Write-KeyBlockReceipt $authorization @{schema=1;scope='LOCAL_KEY_REBASE_ONLY';source_commit=$Commit;source_hashes=$hashes}
    } else {
        Assert-StagingPrivateAcl $paths.root -Directory
        $previous=Read-KeyBlockAuthorization $paths.root
        if ($previous.schema -ne 1 -or $previous.scope -cne 'LOCAL_KEY_REBASE_ONLY') { throw 'KEY_EXISTING_ROOT_NOT_OWNED' }
        Assert-KeyBlockOriginals $paths.source $previous.source_hashes
        if ((@($previous.source_hashes.Keys).Count) -ne $hashes.Count) { throw 'KEY_ORIGINAL_SET_CHANGED' }
    }
    Write-Host 'Nur lokaler Backupschluessel, USB-Recovery und unveraenderte Anwendungsschluessel. Danach STOP.'
    Write-Host 'Passphrase separat im Passwortmanager oder geschuetzt schriftlich offline verwahren. Eingabe nur im GPG-Dialog, niemals im Terminal/Chat.'
    $script:KeyBlockPhase='new_key'
    $script:KeyBlockStep='key_workflow'
    $policy=(@('enforce-passphrase-constraints','min-passphrase-len 20','min-passphrase-nonalpha 1','default-cache-ttl 300','max-cache-ttl 900') -join [char]10)+[char]10
    if (-not (Test-Path -LiteralPath $paths.live)) {
        if ($ExistingFingerprint) { throw 'KEY_EXISTING_PROFILE_REQUIRED_NO_GENERATION' }
        Write-Host 'Neue starke Passphrase im GPG-Dialog festlegen: mindestens 20 Zeichen.'
        New-StagingPrivateDirectory $paths.live
        Write-KeyBlockFile (Join-Path $paths.live 'gpg-agent.conf') ([Text.Encoding]::ASCII.GetBytes($policy)) -PrivateFile
        $null=Invoke-LocalKeyGpg $paths $paths.live Generate
    }
    $policyPath=Join-Path $paths.live 'gpg-agent.conf'
    Assert-StagingPrivateAcl $policyPath
    if ((Get-FileHash -LiteralPath $policyPath -Algorithm SHA256).Hash -cne [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::ASCII.GetBytes($policy)))) { throw 'KEY_PROFILE_POLICY_REVIEW_REQUIRED' }
    $metadata=Invoke-LocalKeyGpg $paths $paths.live Metadata
    $fingerprint=Get-LocalBackupFingerprint $metadata
    if ($fingerprint -ceq '22C82A2F175DAFB04B019502E92DE7854AF99C1F') { throw 'KEY_EXPORT_ON_HOLD_NO_UNLOCK' }
    if ($ExistingFingerprint -and $fingerprint -cne $ExistingFingerprint) { throw 'KEY_EXISTING_FINGERPRINT_MISMATCH' }
    $primary=([Text.Encoding]::UTF8.GetString($metadata) -split '\r?\n' | Where-Object { $_.StartsWith('sec:') })
    $expires=[DateTimeOffset]::FromUnixTimeSeconds([long]$primary.Split(':')[6]).ToString('yyyy-MM-dd')
    Write-Host ('Oeffentlicher Fingerprint fuer die getrennte Verwahrung: '+$fingerprint)
    Write-Host ('Ablaufdatum: '+$expires)
    $identity=Join-Path $paths.root 'identity.json'
    if (-not (Test-Path -LiteralPath $identity)) {
        Write-KeyBlockReceipt $identity @{schema=1;fingerprint=$fingerprint;expires=$expires}
    } elseif ((Read-KeyBlockReceipt $identity).fingerprint -cne $fingerprint) { throw 'KEY_IDENTITY_CHANGED' }
    $usb=Join-Path $paths.usb ('backup-key-rebase-20261104-'+$fingerprint)
    if (-not (Test-Path -LiteralPath $usb)) { $null=New-Item -ItemType Directory -Path $usb -ErrorAction Stop }
    if (-not [IO.Directory]::Exists($usb) -or (Get-Item -LiteralPath $usb -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'KEY_USB_DIRECTORY_UNSAFE' }
    $script:KeyBlockPhase='passphrase_custody'
    Confirm-KeyBlockCustody $paths.root $fingerprint $PassphraseCustody
    $script:KeyBlockPhase='protected_private_export'
    $export=Join-Path $paths.root 'backup-private-key.gpg'
    if (-not (Test-Path -LiteralPath $export)) {
        $bytes=Invoke-LocalKeyGpg $paths $paths.live SecretExport $fingerprint
        try {
            Assert-ProtectedSecretExport (Invoke-LocalKeyGpg -Paths $paths -KeyHome $paths.live -Operation Packets -InputBytes $bytes)
            Write-KeyBlockFile $export $bytes -PrivateFile
        } finally { [Array]::Clear($bytes,0,$bytes.Length) }
    }
    Assert-StagingPrivateAcl $export
    Assert-ProtectedSecretExport (Invoke-LocalKeyGpg $paths $paths.live Packets $fingerprint $export)
    $exportHash=(Get-FileHash -LiteralPath $export -Algorithm SHA256).Hash
    $usbExport=Join-Path $usb 'backup-private-key.gpg'
    Copy-KeyBlockCiphertext $export $usbExport $exportHash
    $script:KeyBlockPhase='isolated_usb_import'
    $completion=Join-Path $paths.root 'completion.json'
    if (-not (Test-Path -LiteralPath $completion)) {
        $comparison=Join-Path $paths.root 'recovery-comparison.json'
        if (-not (Test-Path -LiteralPath $comparison)) {
        if (-not (Test-Path -LiteralPath $paths.recovered)) { New-StagingPrivateDirectory $paths.recovered }
        Stop-OwnedRecoveryAgent $paths
        Write-Host 'Jetzt echte Wiederherstellungsprobe nur mit dem USB-Export: die vorhandene Passphrase aus der getrennten Verwahrung im GPG-Dialog eingeben.'
        $null=Invoke-LocalKeyGpg $paths $paths.recovered Import $fingerprint $usbExport
        if ((Get-LocalBackupFingerprint (Invoke-LocalKeyGpg $paths $paths.recovered Metadata)) -cne $fingerprint) { throw 'KEY_USB_RECOVERED_IDENTITY_MISMATCH' }
        $script:KeyBlockPhase='application_rewrap'
        if (-not (Test-Path -LiteralPath $paths.candidate)) {
            $null=New-StagingOperatorRebaseCandidate -SourceStorageDirectory $paths.source -DestinationStorageDirectory $paths.candidate -NewGpgHome $paths.live -RecoveredGpgHome $paths.recovered -NewRecipient $fingerprint -GpgExecutable $paths.gpg -FingerprintPath $paths.corpus -ExpectedCorpusSha256 '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da' -AllowedOrigin 'https://127.0.0.1:443' -AcknowledgeProtectedStorage -AcknowledgeRecoveredPrivateKey -AcknowledgePassphraseCustody
        } elseif (-not (Test-Path -LiteralPath (Join-Path $paths.candidate $script:OperatorMetadataName))) {
            Assert-StagingPrivateAcl $paths.candidate -Directory
            if ((Get-FileHash -LiteralPath (Join-Path $paths.candidate $script:OperatorStoreName) -Algorithm SHA256).Hash -cne $hashes[$script:OperatorStoreName]) { throw 'KEY_CANDIDATE_DPAPI_CHANGED' }
            $null=Complete-StagingOperatorConfig -StorageDirectory $paths.candidate -FingerprintPath $paths.corpus -ExpectedCorpusSha256 '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da' -AllowedOrigin 'https://127.0.0.1:443' -GpgHome $paths.recovered -GpgExecutable $paths.gpg -ExpectedRecipient $fingerprint -AcknowledgeProtectedStorage -AcknowledgeOperatorCustody
        } else {
            Test-KeyBlockApplicationRecovery $paths $fingerprint
        }
        Use-StagingOperatorEnvironment -StorageDirectory $paths.candidate -ExpectedRecipient $fingerprint -AcknowledgeOperatorCustody -Action { }
        $binding=Read-KeyBlockReceipt (Join-Path $paths.candidate $script:OperatorMetadataName)
        Write-KeyBlockReceipt $comparison @{
            schema=1;fingerprint=$fingerprint;private_export_sha256=$exportHash
            application_backup_sha256=$binding.backup_sha256.ToUpperInvariant()
            dpapi_sha256=$hashes[$script:OperatorStoreName]
        }
        } else {
            $previous=Read-KeyBlockReceipt $comparison
            $binding=Read-KeyBlockReceipt (Join-Path $paths.candidate $script:OperatorMetadataName)
            if ($previous.schema -ne 1 -or $previous.fingerprint -cne $fingerprint -or
                $previous.private_export_sha256 -cne $exportHash -or $previous.dpapi_sha256 -cne $hashes[$script:OperatorStoreName] -or
                $previous.application_backup_sha256 -cne $binding.backup_sha256.ToUpperInvariant()) { throw 'KEY_COMPARISON_BINDING_CHANGED' }
            Use-StagingOperatorEnvironment -StorageDirectory $paths.candidate -ExpectedRecipient $fingerprint -AcknowledgeOperatorCustody -Action { }
            Write-Host 'Gueltiger hashgebundener Recovery-Nachweis wiederverwendet; keine erneute Passphrase-Abfrage fuer die Kopie.'
        }
        Copy-KeyBlockCiphertext (Join-Path $paths.candidate $script:OperatorBackupName) (Join-Path $usb 'application-keys.json.gpg') $binding.backup_sha256.ToUpperInvariant()
        Write-KeyBlockUsbNotes $usb $fingerprint $exportHash $binding.backup_sha256.ToUpperInvariant()
        Assert-KeyBlockOriginals $paths.source $hashes
        Write-KeyBlockReceipt $completion @{
            schema=1;status='PASS';scope='LOCAL_KEYS_ONLY';fingerprint=$fingerprint;expires=$expires
            usb_directory=$usb;private_export_sha256=$exportHash
            application_backup_sha256=$binding.backup_sha256.ToUpperInvariant()
            dpapi_sha256=$hashes[$script:OperatorStoreName]
            recovery='USB_EXPORT_IMPORTED_AND_APPLICATION_PAYLOAD_COMPARED'
            completed_at_utc=[DateTime]::UtcNow.ToString('o');second_recovery='OPEN'
        }
    }
    $script:KeyBlockPhase='final_hash_check'
    $proof=Read-KeyBlockReceipt $completion
    if ($proof.schema -ne 1 -or $proof.status -cne 'PASS' -or $proof.fingerprint -cne $fingerprint -or
        $proof.usb_directory -cne $usb -or $proof.private_export_sha256 -cne $exportHash -or
        $proof.dpapi_sha256 -cne $hashes[$script:OperatorStoreName]) { throw 'KEY_COMPLETION_BINDING_CHANGED' }
    foreach ($pair in @(@($usbExport,$proof.private_export_sha256),@((Join-Path $usb 'application-keys.json.gpg'),$proof.application_backup_sha256),@((Join-Path $paths.candidate $script:OperatorStoreName),$proof.dpapi_sha256))) {
        if ((Get-FileHash -LiteralPath $pair[0] -Algorithm SHA256).Hash -cne $pair[1]) { throw 'KEY_FINAL_HASH_CONFLICT' }
    }
    Use-StagingOperatorEnvironment -StorageDirectory $paths.candidate -ExpectedRecipient $fingerprint -AcknowledgeOperatorCustody -Action { }
    Write-KeyBlockUsbNotes $usb $fingerprint $exportHash $proof.application_backup_sha256
    Assert-KeyBlockOriginals $paths.source $hashes
    Assert-LocalKeyVolumes $paths.root $paths.usb
    if ([IO.Directory]::Exists($paths.recovered)) { Stop-OwnedRecoveryAgent $paths }
    Write-Host ('Neuer oeffentlicher Fingerprint: '+$fingerprint)
    Write-Host ('Geschuetzte Recovery-Kopie: '+$usb)
    Write-Host 'Zweite unabhaengige Recovery-Kopie: OFFEN. Keine Datenbank-/Adminaktion wurde gestartet.'
    $script:KeyBlockPhase='complete'
    return [pscustomobject]@{status='PASS';fingerprint=$fingerprint;dpapi='UNCHANGED';recovery='PASS';second_recovery='OPEN';server_actions='NONE'}
}

if ($MyInvocation.InvocationName -ne '.') {
    if (-not $entryExecute) {
        Write-Output 'LOCAL_BACKUP_KEYS=NOT_EXECUTED SERVER_ACTIONS=NONE'
    } else {
        try {
            $null=Invoke-LocalBackupKeyBlock $entryCommit $entryFingerprint $entryCustody
            Write-Output 'LOCAL_BACKUP_KEYS=PASS RECOVERY=PASS DPAPI=UNCHANGED SECOND_RECOVERY=OPEN SERVER_ACTIONS=NONE'
        } catch {
            $phase=if ($script:KeyBlockPhase -cin @('preflight','new_key','passphrase_custody','protected_private_export','isolated_usb_import','application_rewrap','final_hash_check','complete')) {$script:KeyBlockPhase} else {'unknown'}
            $step=if ($script:KeyBlockStep -cin @('source','source_acl','corpus','tools','volume_status','source_hashes','dpapi_payload','authorization_receipt','key_workflow')) {$script:KeyBlockStep} else {'unknown'}
            $known=@('LOCAL_REVIEWED_COMMIT_REQUIRED','LOCAL_KEY_SOURCE_MUST_BE_CLEAN',
                'CLEAN_PRIVATE_KEY_ENVIRONMENT_REQUIRED','KEY_VOLUME_STATUS_UNAVAILABLE_USE_SAME_USER_ELEVATED_POWERSHELL',
                'KEY_VOLUME_PROTECTION_REQUIRED_NO_UNLOCK_ATTEMPT','KEY_VOLUME_SPACE_REQUIRED',
                'KEY_SOURCE_CUSTODY_REVIEW_REQUIRED','KEY_EXISTING_ROOT_NOT_OWNED','KEY_ORIGINAL_ARTIFACT_CHANGED',
                'KEY_PROFILE_POLICY_REVIEW_REQUIRED','KEY_PROFILE_NOT_SINGLE_DEDICATED_IDENTITY',
                'KEY_GPG_OPERATION_NOT_COMPLETE','KEY_GPG_DIALOG_TIMEOUT',
                'KEY_PASSPHRASE_CUSTODY_NOT_CONFIRMED','KEY_PROTECTED_SECRET_EXPORT_REQUIRED',
                'KEY_UNPROTECTED_OR_UNKNOWN_EXPORT_REJECTED','KEY_COPY_HASH_CONFLICT_NO_OVERWRITE',
                'KEY_COMPLETION_BINDING_CHANGED','KEY_COMPARISON_BINDING_CHANGED','KEY_FINAL_HASH_CONFLICT')
            $known+=@('KEY_AUTHORIZATION_INVALID','KEY_AUTHORIZATION_OWNER_UNTRUSTED','KEY_AUTHORIZATION_LEGACY_OWNER_NOT_BOUND')
            $known+=@('KEY_EXISTING_PROFILE_REQUIRED_NO_GENERATION','KEY_EXISTING_FINGERPRINT_MISMATCH','KEY_CUSTODY_RECEIPT_INVALID')
            $known+='KEY_EXPORT_ON_HOLD_NO_UNLOCK'
            $code=if ($_.Exception.Message -cin $known) {$_.Exception.Message} else {'PRIVATE_LOCAL_KEY_CHECK_NOT_COMPLETE'}
            [Console]::Error.WriteLine('Lokaler Schluesselblock gestoppt. Dateien bleiben erhalten; nicht neu erzeugen oder ueberschreiben. Keine Serveraktion.')
            if ($phase -ceq 'preflight') { [Console]::Error.WriteLine('Quellstand, gleicher Windows-Benutzer und aktueller BitLocker-Schutz muessen pruefbar sein. PowerShell7 bei Bedarf als Administrator mit demselben Benutzer starten; kein Laufwerk erneut entsperren.') }
            [Console]::Error.WriteLine("LOCAL_BACKUP_KEYS=STOP PHASE=$phase STEP=$step CODE=$code SERVER_ACTIONS=NONE SECOND_RECOVERY=OPEN")
            exit 1
        }
    }
}
