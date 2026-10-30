"""Real disposable PostgreSQL restore orchestration with an explicitly FAKE GPG.

This verifies SQL/owners/counts/cleanup, NOT encryption, pinentry or real backup
readiness. No real GPG executable/home/key, DB URL, SSH or VPS is accessed.
"""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[3]
IMAGE = (
    "postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825"
)
spec = importlib.util.spec_from_file_location(
    "synthetic_restore_baseline",
    ROOT / "deploy/scripts/verify-prechange-restore-baseline.py",
)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def test_owned_pg16_restore_preserves_owners_exact_baseline_and_removes_resources(
    tmp_path,
):
    if os.environ.get("COMPETENCE_HUB_PRECHANGE_LOCAL_REHEARSAL") != "1":
        pytest.skip(
            "requires explicit owned-container restore rehearsal; fake GPG only"
        )
    assert os.name == "nt" and shutil.which("pwsh") and shutil.which("docker")
    assert not any(
        name in os.environ
        for name in ("POSTGRES_PASSWORD", "DOCKER_HOST", "DOCKER_CONTEXT")
    )
    assert not tmp_path.resolve().is_relative_to(ROOT)
    nonce = uuid4().hex
    container = None

    def command(arguments, *, data=None, environment=None):
        result = subprocess.run(
            arguments, input=data, env=environment, capture_output=True, timeout=120
        )
        assert result.returncode == 0, (
            "synthetic restore command failed: "
            + result.stderr.decode(errors="replace")[:1000]
        )
        return result.stdout

    base = tmp_path / "synthetic-restore"
    base.mkdir()
    backup, keyhome, evidence = [
        base / name for name in ("snapshot", "empty-fake-key-home", "evidence")
    ]
    environment = {
        name: os.environ[name]
        for name in (
            "PATH",
            "SystemRoot",
            "SystemDrive",
            "WINDIR",
            "TEMP",
            "TMP",
            "USERPROFILE",
            "COMSPEC",
            "ProgramFiles",
            "LOCALAPPDATA",
            "APPDATA",
            "ProgramData",
        )
        if name in os.environ
    }
    environment["SYNTHETIC_CUSTODY_HELPER"] = str(
        ROOT / "deploy/scripts/initialize-staging-operator-config.ps1"
    )
    for directory in (backup, keyhome, evidence):
        command(
            [
                "pwsh",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                ". $env:SYNTHETIC_CUSTODY_HELPER; New-StagingPrivateDirectory $env:SYNTHETIC_PRIVATE_DIRECTORY",
            ],
            environment={**environment, "SYNTHETIC_PRIVATE_DIRECTORY": str(directory)},
        )
    fake = base / "synthetic-gpg.exe"
    shim = base / "synthetic-gpg.cs"
    shim.write_text(
        """using System; using System.IO; using System.Text;
class SyntheticGpg {
static int Main(string[] a) { try {
if (Environment.GetEnvironmentVariable("SYNTHETIC_RESTORE_ONLY") != "FAKE_GPG_NO_ENCRYPTION") return 91;
int h=Array.IndexOf(a,"--homedir"), o=Array.IndexOf(a,"--output");
if (h<0 || o<0 || Array.IndexOf(a,"--decrypt")<0) return 92;
if (Path.GetFileName(a[h+1]) != "empty-fake-key-home" || Directory.GetFileSystemEntries(a[h+1]).Length != 0) return 93;
string source=a[a.Length-1], name=Path.GetFileName(source);
if (name != "database.dump.gpg" && name != "globals.sql.gpg") return 94;
byte[] data=File.ReadAllBytes(source);
string prefix=Encoding.ASCII.GetString(data,0,Math.Min(data.Length,12));
if (name == "database.dump.gpg" ? !prefix.StartsWith("PGDMP") : !prefix.StartsWith("-- SYNTHETIC")) return 95;
using (FileStream f=new FileStream(a[o+1],FileMode.CreateNew)) f.Write(data,0,data.Length);
return 0; } catch { return 99; } }
}""",
        encoding="ascii",
    )
    command(
        [
            r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
            "/nologo",
            "/target:exe",
            "/out:" + str(fake),
            str(shim),
        ]
    )
    environment.update(
        SYNTHETIC_RESTORE_ONLY="FAKE_GPG_NO_ENCRYPTION",
        SYNTHETIC_RESTORE_PYTHON=sys.executable,
    )
    try:
        endpoint = json.loads(
            command(
                [
                    "docker",
                    "context",
                    "inspect",
                    "--format",
                    "{{json .Endpoints.docker.Host}}",
                ]
            )
        )
        assert endpoint in (
            "npipe:////./pipe/docker_engine",
            "npipe:////./pipe/dockerDesktopLinuxEngine",
        )
        command(["docker", "image", "inspect", IMAGE])
        source_environment = {
            **environment,
            "POSTGRES_PASSWORD": secrets.token_urlsafe(40),
        }
        container = (
            command(
                [
                    "docker",
                    "run",
                    "--detach",
                    "--pull",
                    "never",
                    "--network",
                    "none",
                    "--tmpfs",
                    "/var/lib/postgresql/data",
                    "--label",
                    "competence-hub.synthetic-restore=" + nonce,
                    "--env",
                    "POSTGRES_PASSWORD",
                    IMAGE,
                ],
                environment=source_environment,
            )
            .decode()
            .strip()
        )
        assert len(container) == 64 and all(c in "0123456789abcdef" for c in container)
        import time

        for attempt in range(60):
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    container,
                    "sh",
                    "-c",
                    'test "$(cat /proc/1/comm)" = postgres && pg_isready -U postgres',
                ],
                capture_output=True,
            )
            if result.returncode == 0:
                break
            time.sleep(0.25)
        else:
            pytest.fail("owned synthetic PostgreSQL did not start")

        def sql(data, database="competence_hub_staging"):
            return command(
                [
                    "docker",
                    "exec",
                    "-i",
                    container,
                    "psql",
                    "-XqAt",
                    "-v",
                    "ON_ERROR_STOP=1",
                    "-U",
                    "postgres",
                    "-d",
                    database,
                ],
                data=data,
            )

        sql(
            (ROOT / "apps/webapp/database/bootstrap-staging.sql").read_bytes(),
            "postgres",
        )
        for migration in sorted(
            (ROOT / "apps/webapp/database/migrations").glob("000[1-9]_*.sql")
        ):
            sql(migration.read_bytes())
        sql(
            b"SET ROLE competence_hub_owner; INSERT INTO competence_hub.topics(name) VALUES ('Synthetic restore count sentinel');"
        )
        actual = sql(verifier.query_sql(current=True).encode())
        header = {
            "kind": "header",
            "format": "competence-hub.prechange.v1",
            "run_id": "synthetic-" + nonce,
            "created_at_utc": "20261030T123456Z",
            "database": "competence_hub_staging",
            "recipient": verifier.RECIPIENT,
            "encryption": "openpgp",
            "role_passwords_included": False,
            "baseline_scope": "all_non_system_schemas",
            "consistency": "exported_mvcc_snapshot",
            "restore_verified": False,
        }
        metadata = json.dumps(header).encode() + b"\n" + actual
        expected = verifier.validate_metadata(metadata)
        assert expected["row_counts"]["competence_hub.topics"] == 1
        dump = command(
            [
                "docker",
                "exec",
                container,
                "pg_dump",
                "-U",
                "postgres",
                "-d",
                "competence_hub_staging",
                "-Fc",
            ]
        )
        assert dump.startswith(b"PGDMP")
        payloads = {
            "database.dump.gpg": dump,
            "globals.sql.gpg": b"-- SYNTHETIC password-free globals never executed\n",
            "METADATA": metadata,
        }
        for name, data in payloads.items():
            (backup / name).write_bytes(data)
        (backup / "COMPLETE").touch()
        (backup / "SHA256SUMS").write_text(
            "".join(
                hashlib.sha256(data).hexdigest() + "  " + name + "\n"
                for name, data in payloads.items()
            ),
            encoding="ascii",
            newline="\n",
        )
        proof = evidence / "synthetic-proof-not-encryption-evidence.json"
        command(
            [
                sys.executable,
                str(ROOT / "deploy/scripts/verify-prechange-restore-baseline.py"),
                "validate",
                "--expected",
                str(backup / "METADATA"),
            ],
            environment=environment,
        )
        command(["docker", "image", "inspect", IMAGE], environment=environment)
        # Exercise the actual PowerShell native-command adapter with only the
        # synthetic metadata before invoking the complete restore supervisor.
        probe_env = {
            **environment,
            "SYNTHETIC_RESTORE_HELPER": str(
                ROOT / "deploy/scripts/restore-competence-hub-snapshot.ps1"
            ),
            "SYNTHETIC_VERIFIER": str(
                ROOT / "deploy/scripts/verify-prechange-restore-baseline.py"
            ),
            "SYNTHETIC_METADATA": str(backup / "METADATA"),
        }
        command(
            [
                "pwsh",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                r"""$ErrorActionPreference='Stop'; Set-StrictMode -Version Latest
$errors=$null; $tokens=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($env:SYNTHETIC_RESTORE_HELPER,[ref]$tokens,[ref]$errors)
$fn=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq 'Invoke-Native'},$true)
. ([scriptblock]::Create($fn.Extent.Text))
try { $null=Invoke-Native $env:SYNTHETIC_RESTORE_PYTHON @($env:SYNTHETIC_VERIFIER,'validate','--expected',$env:SYNTHETIC_METADATA) }
catch { [Console]::Error.WriteLine($_.Exception.ToString()); exit 1 }
""",
            ],
            environment=probe_env,
        )
        output = command(
            [
                "pwsh",
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(ROOT / "deploy/scripts/restore-competence-hub-snapshot.ps1"),
                "-BackupSet",
                str(backup),
                "-ProofPath",
                str(proof),
                "-GpgHome",
                str(keyhome),
                "-PythonPath",
                sys.executable,
                "-GpgPath",
                str(fake),
                "-ConfirmProtectedSource",
                "-ConfirmIsolatedRestore",
            ],
            environment=environment,
        )
        result = json.loads(output)
        assert result == json.loads(proof.read_bytes())
        assert (
            result["status"] == "PASS"
            and result["baseline_sha256"] == expected["baseline_sha256"]
        )
        assert result["row_counts"] == expected["row_counts"]
        assert all(
            result[key] is True
            for key in (
                "owners_verified",
                "temporary_database_removed",
                "container_removed",
                "plaintext_removed",
            )
        )
    finally:
        if container:
            assert (
                command(
                    [
                        "docker",
                        "inspect",
                        "--format",
                        '{{index .Config.Labels "competence-hub.synthetic-restore"}}',
                        container,
                    ]
                )
                .decode()
                .strip()
                == nonce
            )
            command(["docker", "rm", "--force", container])
            assert (
                command(["docker", "ps", "-aq", "--filter", "id=" + container]).strip()
                == b""
            )
