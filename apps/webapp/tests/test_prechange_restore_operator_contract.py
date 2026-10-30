"""Source/AST and isolated fake-manifest tests, NEVER actual restore evidence.

The only executed PowerShell function is the checksum/file-set validator with
ACL access stubbed. No helper main, Docker, GPG, private key or server is run.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "deploy/scripts/restore-competence-hub-snapshot.ps1"
IMAGE = (
    "postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825"
)


def source():
    return SCRIPT.read_text(encoding="ascii")


def powershell():
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if executable is None:
        pytest.skip("PowerShell unavailable for offline AST/file-validator tests")
    return executable


def test_public_operator_api_and_fixed_offline_image():
    text = source()
    for name in (
        "BackupSet",
        "GpgHome",
        "ProofPath",
        "PythonPath",
        "ConfirmProtectedSource",
        "ConfirmIsolatedRestore",
    ):
        assert "$" + name in text.split("Set-StrictMode")[0]
    assert "[Parameter(Mandatory = $true)][string]$ProofPath" in text
    assert "CompetenceHub\\backup-gnupg" in text
    assert text.count(IMAGE) == 1
    assert "'image', 'inspect', $image" in text
    assert "'context', 'inspect', '--format'" in text and "local_docker_engine_required" in text
    assert "'--pull', 'never'" in text and "'--network', 'none'" in text
    assert "'--tmpfs', '/var/lib/postgresql/data:" in text
    assert "'--tmpfs', '/tmp:" in text
    assert "target=/restore,readonly" in text
    assert not re.search(
        r"['\"](?:-p|--publish|--publish-all|--network=host|pull)['\"]", text
    )
    assert not re.search(
        r"\b(?:ssh|scp|sftp|Invoke-WebRequest|Invoke-RestMethod)\b", text
    )


def test_preserved_ownership_acl_and_no_globals_replay_or_password_arguments():
    text = source()
    assert "'--clean', '--if-exists', '--single-transaction', '--exit-on-error'" in text
    assert "--no-owner" not in text and "--no-privileges" not in text
    for role in ("owner", "app", "migrator"):
        assert f"CREATE ROLE competence_hub_{role} NOLOGIN;" in text
    assert "'--owner', 'competence_hub_owner'" in text
    assert "'--template', 'template0'" in text
    assert "^16[0-9]{4}$" in text
    assert "'--env', 'POSTGRES_PASSWORD'" in text
    assert '"POSTGRES_PASSWORD=' not in text and "'POSTGRES_PASSWORD=" not in text
    assert "GetEnvironmentVariables('Process').Contains('POSTGRES_PASSWORD')" in text
    assert (
        "--passphrase" not in text
        and "--pinentry-mode" not in text
        and "--batch" not in text
    )
    assert (
        "'--no-options', '--homedir', $keyHome, '--no-tty', '--no-auto-key-retrieve'"
        in text
    )
    assert "'--auto-key-locate', 'clear', '--no-auto-key-import', '--output'" in text
    assert not re.search(r"['\"](?:-f|--file)['\"],\s*['\"][^'\"]*globals", text)
    assert "Never replay globals.sql" in text
    assert "'compare', '--expected'" in text and "'--actual', $actualFile" in text
    assert "'validate', '--expected'" in text and "@($verifier, 'query')" in text
    assert "$comparison.metadata_sha256 -cne $hashes['METADATA']" in text
    assert "$comparison.baseline_sha256 -cne $validation.baseline_sha256" in text


def test_owned_id_cleanup_precedes_any_proof_and_never_ignores_cleanup_failure():
    text = source()
    assert "'--cidfile', $cidFile" in text
    assert "^[a-f0-9]{64}$" in text
    assert "competence-hub.prechange-run" in text
    assert '"$Id|/$containerName|$token"' in text
    assert "'container', 'rm', '--force', $containerId" in text
    assert "'container', 'ls', '--all', '--no-trunc'" in text
    assert "'dropdb', '-U', 'postgres', '--if-exists', '--', $restoreDatabase" in text
    assert "WHERE datname='$restoreDatabase'" in text
    assert "Assert-PrivateDirectory $restoreRoot" in text
    assert (
        "Assert-NoReparse" in text and "SetAccessRuleProtection($true, $false)" in text
    )
    assert "Remove-Item -LiteralPath $restoreRoot -ErrorAction Stop" in text
    assert "-Recurse" not in text
    assert "catch { $cleanupFailed = $true }" in text
    cleanup = text.index("finally {\n    if ($passwordOwned)")
    proof = text.index("$result = [ordered]@{")
    assert cleanup < text.index("if ($failure -or $cleanupFailed") < proof
    assert text.index("if (Test-Path -LiteralPath $restoreRoot)") < proof
    assert "[IO.FileMode]::CreateNew" in text
    assert not re.search(
        r"Remove-Item[^\n]*(?:\$source|\$keyHome|\$BackupSet|\$GpgHome)", text
    )


def test_proof_keys_are_exact_parent_contract():
    text = source()
    match = re.search(r"\$result = \[ordered\]@\{(.*?)\n    \}", text, re.S)
    assert match
    keys = set(re.findall(r"^\s*([a-z_][a-z0-9_]*) = ", match[1], re.M))
    assert keys == {
        "schema",
        "status",
        "source_directory",
        "dump_gpg_sha256",
        "metadata_sha256",
        "baseline_sha256",
        "migrations",
        "row_counts",
        "owners_verified",
        "encrypted_copy_verified",
        "temporary_database_removed",
        "container_removed",
        "plaintext_removed",
        "finished_at_utc",
        "restore_image",
    }
    assert "schema = 'competence-hub.prechange-restore-proof.v1'" in match[1]
    assert "[DateTimeOffset]::UtcNow.ToString('o')" in match[1]
    assert "dump_gpg_sha256 = $hashes['database.dump.gpg']" in match[1]
    assert "baseline_sha256 = $comparison.baseline_sha256" in match[1]


def test_powershell_ast_syntax_only(tmp_path):
    runner = tmp_path / "parse.ps1"
    runner.write_text(
        """param([string]$Source)
$errors=$null; $tokens=$null
$null=[System.Management.Automation.Language.Parser]::ParseFile($Source,[ref]$tokens,[ref]$errors)
if ($errors.Count -ne 0) { [Console]::Error.WriteLine('AST_PARSE_FAILED'); exit 1 }
Write-Output 'AST_ONLY_OK'
""",
        encoding="ascii",
    )
    result = subprocess.run(
        [
            powershell(),
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(runner),
            str(SCRIPT),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "AST_ONLY_OK"


@pytest.mark.parametrize(
    "mutation",
    [
        "valid",
        "duplicate",
        "missing",
        "extra",
        "directory",
        "path",
        "wronghash",
        "uppercase_name",
        "uppercase_hash",
        "nonempty_complete",
        "empty_payload",
        "oversized_checksums",
    ],
)
def test_manifest_validator_on_only_synthetic_files_and_no_native_apps(
    tmp_path, mutation
):
    directory = tmp_path / "synthetic"
    directory.mkdir()
    files = {
        "database.dump.gpg": b"SYNTHETIC_NOT_ENCRYPTED",
        "globals.sql.gpg": b"SYNTHETIC_NOT_ENCRYPTED_GLOBALS",
        "METADATA": b"SYNTHETIC_NO_AUTH_DATA",
    }
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / "COMPLETE").touch()
    lines = [
        hashlib.sha256(data).hexdigest() + "  " + name for name, data in files.items()
    ]
    if mutation == "duplicate":
        lines[-1] = lines[0]
    elif mutation == "missing":
        lines.pop()
    elif mutation == "extra":
        (directory / "UNOWNED").touch()
    elif mutation == "directory":
        (directory / "COMPLETE").unlink()
        (directory / "COMPLETE").mkdir()
    elif mutation == "path":
        lines[0] = lines[0].replace("database.dump.gpg", "../database.dump.gpg")
    elif mutation == "wronghash":
        lines[0] = "0" * 64 + "  database.dump.gpg"
    elif mutation == "uppercase_name":
        lines[0] = lines[0].replace("database.dump.gpg", "DATABASE.DUMP.GPG")
    elif mutation == "uppercase_hash":
        lines[0] = lines[0].upper().replace("DATABASE.DUMP.GPG", "database.dump.gpg")
    elif mutation == "nonempty_complete":
        (directory / "COMPLETE").write_bytes(b"not empty")
    elif mutation == "empty_payload":
        (directory / "database.dump.gpg").write_bytes(b"")
    elif mutation == "oversized_checksums":
        lines = ["x" * 4097, lines[1], lines[2]]
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="ascii")
    runner = tmp_path / "manifest-only.ps1"
    runner.write_text(
        r"""param([string]$Source,[string]$Directory)
$ErrorActionPreference='Stop'
$utf8=New-Object Text.UTF8Encoding($false,$true)
$allowedSids=@('SYNTHETIC')
$errors=$null; $tokens=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile($Source,[ref]$tokens,[ref]$errors)
if ($errors.Count -ne 0) { exit 2 }
$function=$ast.Find({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Assert-SourceSet'},$true)
if ($null -eq $function) { exit 3 }
# Deliberate stubs: only manifest validation runs, NOT ACL setup/helper main.
function Assert-PrivateDirectory([string]$Path) {}
function Get-Acl {
    param([string]$LiteralPath)
    $acl=[pscustomobject]@{}
    $acl | Add-Member -MemberType ScriptMethod -Name GetAccessRules -Value { param($a,$b,$c) return @() }
    return $acl
}
. ([scriptblock]::Create($function.Extent.Text))
try { $result=Assert-SourceSet $Directory; $result | ConvertTo-Json -Compress }
catch { [Console]::Error.WriteLine('EXPECTED_VALIDATION_FAILURE:' + $_.Exception.Message); exit 1 }
""",
        encoding="ascii",
    )
    result = subprocess.run(
        [
            powershell(),
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(runner),
            str(SCRIPT),
            str(directory),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    if mutation == "valid":
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == {
            name: hashlib.sha256(data).hexdigest() for name, data in files.items()
        }
    else:
        assert result.returncode == 1 and result.stdout == "", result.stderr
        assert "EXPECTED_VALIDATION_FAILURE" in result.stderr
    assert (directory / "METADATA").read_bytes() == files["METADATA"]
