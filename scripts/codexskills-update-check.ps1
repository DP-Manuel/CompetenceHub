param(
    [string]$CodexSkillsPath = (Join-Path $env:USERPROFILE "Documents\IT\CodexSkills"),
    [string]$RepositoryUrl = "https://github.com/DP-Manuel/CodexSkills.git",
    [switch]$Validate,
    [switch]$PlanSync,
    [switch]$SyncActive,
    [string[]]$SyncSkill = @(),
    [switch]$BackupActive
)

$ErrorActionPreference = "Stop"

function Invoke-Python {
    param(
        [string[]]$Arguments,
        [switch]$AllowNonZero
    )
    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        if ($AllowNonZero) {
            Write-Host "Command reported differences with exit code $LASTEXITCODE; continuing for review."
            return
        }
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

Write-Host "CodexSkills update check"
Write-Host "Source path: $CodexSkillsPath"

if (-not (Test-Path -LiteralPath $CodexSkillsPath)) {
    Write-Host "Local CodexSkills source not found."
    Write-Host "Clone it with:"
    Write-Host "  git clone $RepositoryUrl `"$CodexSkillsPath`""
    exit 1
}

$gitDir = Join-Path $CodexSkillsPath ".git"
if (-not (Test-Path -LiteralPath $gitDir)) {
    Write-Host "The source path exists but is not a Git repository: $CodexSkillsPath"
    Write-Host "Use the canonical repo if exact source history is needed: $RepositoryUrl"
    exit 1
}

Write-Host ""
Write-Host "Local repository state"
git -C $CodexSkillsPath rev-parse --short HEAD
git -C $CodexSkillsPath status --short

if ($Validate) {
    Write-Host ""
    Write-Host "Validating repository skills"
    Invoke-Python -Arguments @(
        (Join-Path $CodexSkillsPath "scripts\validate_skills.py"),
        (Join-Path $CodexSkillsPath "skills")
    )

    Write-Host ""
    Write-Host "Checking active runtime drift"
    Invoke-Python -Arguments @(
        (Join-Path $CodexSkillsPath "scripts\check_active_install.py"),
        "--skills-root", (Join-Path $CodexSkillsPath "skills")
    ) -AllowNonZero
}

if ($BackupActive -and -not $SyncActive) {
    throw "-BackupActive requires -SyncActive."
}

function Get-SyncSelection {
    if ($SyncSkill.Count -gt 0) {
        $selection = @()
        foreach ($skillName in $SyncSkill) {
            $selection += "--skill"
            $selection += $skillName
        }
        return $selection
    }
    return @("--all")
}

if ($PlanSync) {
    $destination = Join-Path $env:USERPROFILE ".codex\skills"
    $syncArgs = @(
        (Join-Path $CodexSkillsPath "scripts\sync_skills.py"),
        "--skills-root", (Join-Path $CodexSkillsPath "skills"),
        "--destination", $destination
    ) + (Get-SyncSelection) + @("--overwrite", "--dry-run")

    Write-Host ""
    Write-Host "Planning active runtime sync without changing files: $destination"
    Invoke-Python -Arguments $syncArgs
}

if ($SyncActive) {
    $destination = Join-Path $env:USERPROFILE ".codex\skills"
    $syncArgs = @(
        (Join-Path $CodexSkillsPath "scripts\sync_skills.py"),
        "--skills-root", (Join-Path $CodexSkillsPath "skills"),
        "--destination", $destination
    ) + (Get-SyncSelection) + @("--overwrite")

    if ($BackupActive) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $backupDir = Join-Path $env:USERPROFILE ".codex\skill-backups\$timestamp"
        $syncArgs += @("--backup-dir", $backupDir)
        Write-Host ""
        Write-Host "Backing up replaced active skills to: $backupDir"
    }

    Write-Host ""
    Write-Host "Syncing approved repository skills to active runtime: $destination"
    Invoke-Python -Arguments $syncArgs

    Write-Host ""
    Write-Host "Checking active runtime drift after sync"
    Invoke-Python -Arguments @(
        (Join-Path $CodexSkillsPath "scripts\check_active_install.py"),
        "--skills-root", (Join-Path $CodexSkillsPath "skills")
    )
}

Write-Host ""
Write-Host "Done. To update the canonical source itself, review/pull the CodexSkills repository intentionally before running this check again."
