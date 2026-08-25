from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
DEPLOY_ROOT = REPO_ROOT / "deploy"
SCRIPTS_ROOT = DEPLOY_ROOT / "scripts"
SYSTEMD_ROOT = DEPLOY_ROOT / "systemd"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_backup_script_fails_closed_and_encrypts_before_publication() -> None:
    script = read(SCRIPTS_ROOT / "competence-hub-postgres-backup")

    assert "set -Eeuo pipefail" in script
    assert 'BACKUP_ROOT="/var/backups/competence-hub/automated"' in script
    assert "--globals-only --no-role-passwords" in script
    assert script.count("--encrypt") == 2
    assert "private GPG keys are not allowed" in script
    assert "duplicate configuration key" in script
    assert 'rm -f -- "$plain_dump" "$plain_globals"' in script
    assert 'touch "$work_dir/COMPLETE"' in script
    assert 'chmod 0500 "$work_dir"' not in script
    assert script.index('mv -- "$work_dir" "$final_set"') < script.index(
        'chmod 0500 "$final_set"'
    )
    assert 'fail "published backup set permissions could not be secured"' in script
    assert script.index('rm -f -- "$plain_dump" "$plain_globals"') < script.index(
        'touch "$work_dir/COMPLETE"'
    )
    assert "prune_sets" in script
    assert "source " not in script
    assert "eval " not in script
    assert "rm -rf" not in script


def test_backup_monitor_checks_age_integrity_encryption_and_plaintext() -> None:
    script = read(SCRIPTS_ROOT / "competence-hub-postgres-backup-monitor")

    assert "BACKUP_MAX_AGE_HOURS" in script
    assert "sha256sum --check --strict" in script
    assert "--no-tty --list-only" in script
    assert "--list-packets" in script
    assert "unencrypted database material" in script
    assert "exactly two encrypted payloads" in script
    assert "duplicate configuration key" in script
    assert "checksum manifest contains a path" in script


def test_restore_check_is_local_temporary_and_explicit() -> None:
    script = read(SCRIPTS_ROOT / "competence-hub-postgres-restore-check")

    assert "--confirm-isolated-restore" in script
    assert 'PG_SOCKET="/var/run/postgresql"' in script
    assert script.count('--host "$PG_SOCKET"') >= 6
    assert "competence_hub_restore_check_" in script
    assert "--exit-on-error --no-owner --no-privileges" in script
    assert "backup set contains a symlink" in script
    assert "checksum manifest contains a path" in script
    assert '--if-exists -- "$target_database"' in script
    assert "pg_restore --clean" not in script
    assert "dropdb --if-exists competence_hub_staging" not in script


@pytest.mark.parametrize(
    "unit_name",
    [
        "competence-hub-postgres-backup.service.example",
        "competence-hub-postgres-backup-monitor.service.example",
    ],
)
def test_backup_services_use_restricted_postgres_identity(unit_name: str) -> None:
    unit = read(SYSTEMD_ROOT / unit_name)

    assert "User=postgres" in unit
    assert "Group=postgres" in unit
    assert "UMask=0077" in unit
    assert "NoNewPrivileges=true" in unit
    assert "PrivateNetwork=true" in unit
    assert "ProtectSystem=strict" in unit
    assert "RestrictAddressFamilies=AF_UNIX" in unit


def test_backup_timers_are_persistent_and_separated() -> None:
    backup_timer = read(SYSTEMD_ROOT / "competence-hub-postgres-backup.timer.example")
    monitor_timer = read(
        SYSTEMD_ROOT / "competence-hub-postgres-backup-monitor.timer.example"
    )

    assert "OnCalendar=*-*-* 02:15:00 UTC" in backup_timer
    assert "OnCalendar=*-*-* 08:00:00 UTC" in monitor_timer
    assert "Persistent=true" in backup_timer
    assert "Persistent=true" in monitor_timer


def test_backup_configuration_contains_no_secret_value() -> None:
    config = read(DEPLOY_ROOT / "postgresql" / "backup.conf.example")

    assert "__GPG_RECIPIENT_FINGERPRINT__" in config
    assert "PASSWORD" not in config
    assert "SECRET" not in config
    assert "BACKUP_KEEP_DAILY=30" in config
    assert "BACKUP_KEEP_MONTHLY=12" in config


def test_release_builder_packages_operations_contract() -> None:
    builder = read(REPO_ROOT / "scripts" / "build-webapp-release.ps1")

    assert "postgresql-backup-restore-runbook.md" in builder
    assert '"deploy\\postgresql\\backup.conf.example"' in builder
    assert '"__GPG_RECIPIENT_FINGERPRINT__"' in builder
    assert "competence-hub-postgres-backup-monitor.timer.example" in builder


def test_windows_pull_is_guarded_and_never_deletes_remote_data() -> None:
    script = read(SCRIPTS_ROOT / "pull-competence-hub-backup.ps1")

    assert "ConfirmProtectedDestination" in script
    assert "competence-hub-backup-export/${BackupDate}" in script
    assert "Backup destination must be separate from the repository" in script
    assert "must contain exactly two encrypted payloads" in script
    assert "contains plaintext database material" in script
    assert "contains a reparse point or symlink" in script
    assert "Get-FileHash" in script
    assert "The remote export was not deleted" in script
    assert "ssh " not in script.lower()


def test_windows_docker_restore_is_pinned_isolated_and_cleans_up() -> None:
    script = read(SCRIPTS_ROOT / "restore-competence-hub-backup-docker.ps1")

    assert "ConfirmProtectedSource" in script
    assert "ConfirmIsolatedRestore" in script
    assert "Restore source must be separate from the repository" in script
    assert "SHA256SUMS must contain exactly three entries" in script
    assert "contains plaintext database material" in script
    assert "this script never pulls images" in script
    assert "--pull never" in script
    assert "--network none" in script
    assert "--exit-on-error --no-owner" in script
    assert "--no-privileges" in script
    assert "finally" in script
    assert "Remove-Item -LiteralPath $plainDump -Force" in script
    assert "Remove-Item -LiteralPath $restoreRoot -Recurse -Force" in script
    assert "docker pull" not in script.lower()


def test_operations_shell_scripts_have_valid_bash_syntax() -> None:
    candidates: list[Path] = []
    if os.name == "nt":
        for variable in ("ProgramFiles", "LocalAppData"):
            base = os.environ.get(variable)
            if base:
                candidates.append(Path(base) / "Git" / "bin" / "bash.exe")
                candidates.append(Path(base) / "Programs" / "Git" / "bin" / "bash.exe")
    else:
        candidates.extend(
            Path(path) / "bash" for path in os.environ.get("PATH", "").split(os.pathsep)
        )

    bash = next((candidate for candidate in candidates if candidate.is_file()), None)
    if bash is None:
        pytest.skip("A native Bash executable is unavailable for syntax validation")

    scripts = sorted(path for path in SCRIPTS_ROOT.iterdir() if path.is_file())
    result = subprocess.run(
        [str(bash), "-n", *(str(path) for path in scripts)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_linux_operations_files_keep_lf_line_endings_after_checkout() -> None:
    attributes = read(REPO_ROOT / ".gitattributes")

    for name in (
        "competence-hub-postgres-backup",
        "competence-hub-postgres-backup-monitor",
        "competence-hub-postgres-restore-check",
    ):
        assert f"deploy/scripts/{name} text eol=lf" in attributes
    assert "deploy/systemd/*.example text eol=lf" in attributes
    assert "deploy/postgresql/*.example text eol=lf" in attributes
