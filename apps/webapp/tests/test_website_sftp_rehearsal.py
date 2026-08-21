from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "deploy"
    / "scripts"
    / "prepare-competence-hub-website-sftp-rehearsal.ps1"
)
TARGET_EXAMPLE = REPO_ROOT / "deploy" / "website" / "sftp-target.example.json"
RUNBOOK = REPO_ROOT / "docs" / "architecture" / "website-sftp-release-rehearsal-runbook.md"


def powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def write_fixture(
    root: Path,
    *,
    dirty: bool = False,
    archive_entries: dict[str, bytes] | None = None,
    remote_web_root: str = "/approved-webroot",
) -> tuple[Path, Path, Path]:
    artifact = root / "competence-hub-website-abcdef123456-test.zip"
    entries = archive_entries or {
        "index.html": b"<!doctype html><title>Competence Hub</title>",
        "assets/site.css": b"body { color: #222; }",
    }
    with zipfile.ZipFile(artifact, "w") as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)

    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    manifest = root / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "artifact": artifact.name,
                "sha256": digest,
                "commit": "abcdef123456",
                "dirty": dirty,
                "canonical_url": "https://competencehub.donner-partner.de",
                "deployment_authorized": False,
            }
        ),
        encoding="utf-8",
    )
    target = root / "target.json"
    target.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "canonical_url": "https://competencehub.donner-partner.de",
                "redirect_url": "https://competence-hub.donner-partner.de",
                "sftp_host": "sftp.example.invalid",
                "sftp_port": 22,
                "sftp_host_key_sha256": "SHA256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                "remote_web_root": remote_web_root,
                "remote_web_root_verified": True,
                "expected_entrypoint": "index.html",
            }
        ),
        encoding="utf-8",
    )
    return artifact, manifest, target


def run_preparer(tmp_path: Path, **fixture_options: object) -> subprocess.CompletedProcess[str]:
    executable = powershell()
    if executable is None:
        pytest.skip("PowerShell is unavailable for Website SFTP rehearsal tests")
    artifact, manifest, target = write_fixture(tmp_path, **fixture_options)
    output = tmp_path / "output"
    return subprocess.run(
        [
            executable,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-ArtifactPath",
            str(artifact),
            "-ManifestPath",
            str(manifest),
            "-TargetContractPath",
            str(target),
            "-OutputDirectory",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_sftp_rehearsal_contract_is_secret_free_and_non_executing() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    target = json.loads(TARGET_EXAMPLE.read_text(encoding="utf-8"))
    runbook = RUNBOOK.read_text(encoding="utf-8")

    assert "deployment_authorized" in script
    assert "remote_change_authorized = $false" in script
    assert "remote_backup_verified = $false" in script
    assert "Get-FileHash" in script
    assert "ZipArchive" in script
    assert "& sftp" not in script.lower()
    assert "start-process" not in script.lower()
    assert "password" not in json.dumps(target).lower()
    assert target["remote_web_root"] == "__CONFIRMED_SFTP_WEB_ROOT__"
    assert target["remote_web_root_verified"] is False
    assert target["sftp_host_key_sha256"] == "__VERIFIED_SFTP_HOST_KEY_SHA256__"
    assert "vollstaendige datierte Webspace-Sicherung" in runbook
    assert "Unbekannte Remote-Dateien werden nie automatisch geloescht" in runbook


@pytest.mark.skipif(os.name != "nt", reason="PowerShell 5.1 behavior is tested on Windows")
def test_sftp_rehearsal_prepares_verified_local_package(tmp_path: Path) -> None:
    result = run_preparer(tmp_path)
    assert result.returncode == 0, result.stderr

    packages = list((tmp_path / "output").iterdir())
    assert len(packages) == 1
    package = packages[0]
    assert (package / "release" / "index.html").is_file()
    assert (package / "release" / "assets" / "site.css").is_file()
    plan = json.loads((package / "release-plan.json").read_text(encoding="utf-8-sig"))
    assert plan["artifact_verified"] is True
    assert plan["remote_inventory_verified"] is False
    assert plan["remote_backup_verified"] is False
    assert plan["remote_change_authorized"] is False
    assert plan["remote_web_root"] == "/approved-webroot"
    assert plan["remote_web_root_verified"] is True


@pytest.mark.skipif(os.name != "nt", reason="PowerShell 5.1 behavior is tested on Windows")
def test_sftp_rehearsal_rejects_dirty_artifact(tmp_path: Path) -> None:
    result = run_preparer(tmp_path, dirty=True)
    assert result.returncode != 0
    assert "Dirty Website artifacts" in (result.stdout + result.stderr)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell 5.1 behavior is tested on Windows")
def test_sftp_rehearsal_rejects_remote_path_traversal(tmp_path: Path) -> None:
    result = run_preparer(tmp_path, remote_web_root="/safe/../wrong")
    assert result.returncode != 0
    assert "remote_web_root" in (result.stdout + result.stderr)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell 5.1 behavior is tested on Windows")
def test_sftp_rehearsal_rejects_zip_traversal(tmp_path: Path) -> None:
    result = run_preparer(
        tmp_path,
        archive_entries={"index.html": b"ok", "../escape.txt": b"blocked"},
    )
    assert result.returncode != 0
    assert "unsafe entry path" in (result.stdout + result.stderr)
    assert not (tmp_path / "escape.txt").exists()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell 5.1 behavior is tested on Windows")
def test_sftp_rehearsal_rejects_nested_environment_file(tmp_path: Path) -> None:
    result = run_preparer(
        tmp_path,
        archive_entries={"index.html": b"ok", "assets/.env.production": b"blocked"},
    )
    assert result.returncode != 0
    assert "forbidden entry segment" in (result.stdout + result.stderr)
