#requires -Version 7.2
<#
Local keys ONLY. No backup, admin, import, server or key initialization/rotation.
Real key data stay in the local operator process; never transcript/debug/record.
#>
[CmdletBinding()]
param([switch]$Execute, [string]$ExpectedSourceCommit)

$script:LocalKeyRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
. (Join-Path $script:LocalKeyRoot 'deploy/scripts/initialize-staging-operator-config.ps1')

function Confirm-LocalKeyOperation {
    try { $answer = Read-Host 'Zur lokalen Schluesselpruefung VERIFY eingeben (leer = Abbruch)' }
    catch {
        Write-Host 'Bestaetigung abgebrochen. Es wurde nichts geprueft oder kopiert.'
        throw 'KEY_CONFIRMATION_CANCELLED'
    }
    if ([string]::IsNullOrWhiteSpace($answer)) {
        Write-Host 'Abgebrochen. Es wurde nichts geprueft oder kopiert.'
        throw 'KEY_CONFIRMATION_CANCELLED'
    }
    if (-not [string]::Equals($answer.Trim(), 'VERIFY', [StringComparison]::OrdinalIgnoreCase)) {
        Write-Host 'Ungueltige Bestaetigung: Bitte VERIFY oder verify eingeben; Leerzeichen am Rand sind erlaubt. Kein Passwort eingeben.'
        throw 'KEY_CONFIRMATION_INVALID'
    }
}

function Assert-LocalKeySource {
    param([string]$Commit)
    if ($Commit -cnotmatch '^[a-f0-9]{40}$') { throw 'LOCAL_REVIEWED_COMMIT_REQUIRED' }
    $git = (Get-Command git.exe -CommandType Application -ErrorAction Stop).Source
    $head = & $git -C $script:LocalKeyRoot rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $head -cne $Commit) { throw 'LOCAL_REVIEWED_COMMIT_REQUIRED' }
    $dirty = & $git -C $script:LocalKeyRoot status --porcelain --untracked-files=all -- apps/webapp/src apps/webapp/scripts apps/webapp/tests deploy/scripts
    if ($LASTEXITCODE -ne 0 -or $dirty) { throw 'LOCAL_KEY_SOURCE_MUST_BE_CLEAN' }
}

function Assert-LocalKeyEnvironment {
    foreach ($name in [Environment]::GetEnvironmentVariables('Process').Keys) {
        if ($name -match '^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON(INSPECT|STARTUP|BREAKPOINT|HOME|USERBASE|PATH|ASYNCIODEBUG)$)' -or $name -like 'COMPETENCE_HUB_*') { throw 'CLEAN_PRIVATE_KEY_ENVIRONMENT_REQUIRED' }
    }
}

function Get-LocalKeyPaths {
    $base = Join-Path $env:LOCALAPPDATA 'CompetenceHub'
    return @{ custody=(Join-Path $base 'staging-operator'); corpus=(Join-Path $base 'staging-operator-corpus-20261030/compromised-password-fingerprints.sha256'); gpg=(Join-Path $base 'backup-gnupg'); usb='D:\CompetenceHub' }
}

function Get-LocalKeyCapacity {
    param([string]$Source, [string]$UsbDirectory)
    $item = Get-Item -LiteralPath $Source -Force -ErrorAction Stop
    $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($UsbDirectory))
    if (-not $drive.IsReady -or $item.Length -le 0 -or $drive.AvailableFreeSpace -lt ($item.Length + 1MB)) { throw 'USB_KEY_COPY_SPACE_REQUIRED' }
    return @{ bytes=$item.Length; free_bytes=$drive.AvailableFreeSpace }
}

function Assert-ResumeUsb {
    param([string]$Path = 'D:\CompetenceHub')
    if ([IO.Path]::GetFullPath($Path).TrimEnd('\') -cne 'D:\CompetenceHub') { throw 'APPROVED_USB_DIRECTORY_REQUIRED' }
    if (-not [IO.Directory]::Exists($Path)) { throw 'UNLOCKED_USB_DIRECTORY_REQUIRED' }
    $cursor = $Path
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'USB_REPARSE_PATH_REJECTED' }
        }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
}

function Copy-ResumeEncryptedKeyBackup {
    param([string]$StorageDirectory, [string]$UsbDirectory = 'D:\CompetenceHub',
          [Parameter(Mandatory)][ValidatePattern('^[a-f0-9]{64}$')][string]$ExpectedSha256)
    Assert-ResumeUsb -Path $UsbDirectory
    $source = Join-Path $StorageDirectory 'staging-operator.keys.json.gpg'
    Assert-StagingPrivateAcl $source
    $hash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -cne $ExpectedSha256) { throw 'VERIFIED_KEY_BACKUP_BINDING_CHANGED' }
    $directory = Join-Path $UsbDirectory 'staging-operator-key-backups'
    if (Test-Path -LiteralPath $directory) {
        if (-not [IO.Directory]::Exists($directory) -or (Get-Item -LiteralPath $directory -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'USB_REPARSE_PATH_REJECTED' }
    } else { $null = New-Item -ItemType Directory -Path $directory }
    $target = Join-Path $directory ($hash + '.keys.json.gpg')
    if (Test-Path -LiteralPath $target) {
        if ((Get-Item -LiteralPath $target -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'USB_REPARSE_PATH_REJECTED' }
    } else {
        $inputStream = [IO.File]::OpenRead($source)
        $outputStream = $null
        try {
            $outputStream = [IO.File]::Open($target,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
            $inputStream.CopyTo($outputStream); $outputStream.Flush($true)
        } finally { if ($outputStream) { $outputStream.Dispose() }; $inputStream.Dispose() }
    }
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -cne $hash -or
        (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedSha256) { throw 'USB_ENCRYPTED_COPY_HASH_MISMATCH_NO_OVERWRITE' }
    Write-Host 'KEY_BACKUP_USB=PASS ENCRYPTED_ONLY=PASS EXISTING_KEYS_PRESERVED=PASS'
}

function Invoke-ExistingStagingResume {
    param([string]$Commit)
    $ErrorActionPreference = 'Stop'
    $script:ResumePhase = 'preflight'
    Set-StrictMode -Version Latest
    if (-not $IsWindows) { throw 'WINDOWS_OPERATOR_REQUIRED' }
    $VerbosePreference = 'SilentlyContinue'; $DebugPreference = 'SilentlyContinue'
    Assert-LocalKeyEnvironment
    Assert-LocalKeySource $Commit
    $paths = Get-LocalKeyPaths
    Assert-ResumeUsb -Path $paths.usb
    $custody = $paths.custody
    Assert-StagingPrivateAcl $custody -Directory
    if (Test-Path -LiteralPath (Join-Path $custody 'bootstrap-attempt.json')) { throw 'PRIOR_ADMIN_ATTEMPT_REQUIRES_REVIEW' }
    foreach ($name in @('staging-operator.keys.clixml','staging-operator.keys.json.gpg')) {
        $path = Join-Path $custody $name
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw 'EXISTING_KEY_PAIR_REQUIRED_NO_INITIALIZATION' }
        Assert-StagingPrivateAcl $path
    }
    $space = Get-LocalKeyCapacity -Source (Join-Path $custody 'staging-operator.keys.json.gpg') -UsbDirectory $paths.usb
    Write-Host 'Nur lokale Schluesselpruefung und verschluesselte Kopie. Kein Datenbankbackup, Admin, Import oder Serverzugriff.'
    Write-Host 'Bitte ohne Aufzeichnung oder Bildschirmfreigabe arbeiten. Schluessel werden nicht neu angelegt oder ersetzt.'
    Write-Host ("Verschluesselte Kopie: " + $space.bytes + " Byte. Freier Zielplatz: " + $space.free_bytes + ' Byte. Der Stick ist bereits entsperrt.')
    $script:ResumePhase = 'confirmation'
    Confirm-LocalKeyOperation
    $script:ResumePhase = 'key_verification'
    $metadata = Join-Path $custody 'staging-operator.metadata.json'
    $gpgStatus = 'EXISTING_BOUND_PROOF'
    if (-not (Test-Path -LiteralPath $metadata)) {
        Write-Host 'Die vorhandene GPG-Kopie wird einmalig im Speicher mit dem DPAPI-Original verglichen. Eine Passphrase nur im GPG-Dialog eingeben.'
        $null = Complete-StagingOperatorConfig -StorageDirectory $custody `
            -FingerprintPath $paths.corpus `
            -ExpectedCorpusSha256 '80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da' -AllowedOrigin 'https://127.0.0.1:443' `
            -GpgHome $paths.gpg -GpgExecutable 'C:\Program Files\GnuPG\bin\gpg.exe' `
            -AcknowledgeProtectedStorage -AcknowledgeOperatorCustody
        $gpgStatus = 'VERIFIED_NOW'
    } else {
        Write-Host 'Vorhandener Pruefbeleg wird an beiden aktuellen Dateihashes und DPAPI geprueft. Keine erneute GPG-Abfrage bei unveraendertem gueltigem Beleg.'
    }
    Use-StagingOperatorEnvironment -StorageDirectory $custody -AcknowledgeOperatorCustody -Action { }
    $script:ResumePhase = 'encrypted_usb_copy'
    # Non-secret verification metadata only; never read either keyfile here.
    $verified = Get-Content -Raw -LiteralPath $metadata | ConvertFrom-Json -AsHashtable
    Copy-ResumeEncryptedKeyBackup -StorageDirectory $custody -UsbDirectory $paths.usb -ExpectedSha256 $verified.backup_sha256
    Write-Host 'Fertig. Nur die vorhandene verschluesselte Schluesseldatei wurde gesichert. Keine weiteren Betriebsaktionen starten.'
    $script:ResumePhase = 'complete'
    return [pscustomobject]@{ status='PASS'; scope='LOCAL_KEYS_ONLY'; gpg_verification=$gpgStatus; encrypted_usb_copy='PASS'; server_actions='NONE'; real_coach_apply='DISABLED' }
}

if ($MyInvocation.InvocationName -ne '.') {
    if (-not $Execute) {
        Write-Output 'STAGING_KEYS=NOT_EXECUTED LOCAL_ONLY=YES REAL_COACH_APPLY=DISABLED'
    } else {
        try {
            $null = Invoke-ExistingStagingResume -Commit $ExpectedSourceCommit
            Write-Output 'STAGING_KEYS=PASS KEY_COPY=PASS SERVER_ACTIONS=NONE REAL_COACH_APPLY=DISABLED'
        }
        catch {
            $phase = if ($script:ResumePhase -cin @('preflight','confirmation','key_verification','encrypted_usb_copy','complete')) { $script:ResumePhase } else { 'unknown' }
            $code = if ($_.Exception.Message -cin @('KEY_CONFIRMATION_INVALID','KEY_CONFIRMATION_CANCELLED','USB_KEY_COPY_SPACE_REQUIRED','PRIOR_ADMIN_ATTEMPT_REQUIRES_REVIEW','LOCAL_REVIEWED_COMMIT_REQUIRED','LOCAL_KEY_SOURCE_MUST_BE_CLEAN','CLEAN_PRIVATE_KEY_ENVIRONMENT_REQUIRED','USB_ENCRYPTED_COPY_HASH_MISMATCH_NO_OVERWRITE','VERIFIED_KEY_BACKUP_BINDING_CHANGED')) { $_.Exception.Message } else { 'PRIVATE_KEY_CHECK_NOT_COMPLETE' }
            if ($phase -cne 'confirmation') { [Console]::Error.WriteLine('Die lokale Schluesselpruefung ist nicht abgeschlossen. Bestehende Dateien bleiben erhalten; kein automatischer Wiederholungsversuch.') }
            [Console]::Error.WriteLine("STAGING_KEYS=STOP PHASE=$phase CODE=$code SERVER_ACTIONS=NONE REAL_COACH_APPLY=DISABLED")
            exit 1
        }
    }
}
