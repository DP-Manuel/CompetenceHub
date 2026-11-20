"""Local tooling tests; the optional native test owns an unpublished Linux cluster."""

from datetime import datetime, timedelta, timezone
import io
import os
from pathlib import Path
import re
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import v2_clone as clone
import v2_host as host
import v2_package as package


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DATABASE_FILES = Path(os.environ.get("CH_V2_TEST_DATABASE_FILES", ROOT / "apps/webapp/database"))
CACHE = Path(os.environ.get("CH_V2_TEST_WHEELHOUSE", ROOT /
            "release-artifacts/webapp-linux/20261113T151559Z-1a2ef9ab/wheelhouse"))
COMMIT = "1" * 40
EVIDENCE = "2" * 64
ARCHIVE_SHA = "3" * 64
NOW = datetime(2026, 11, 19, tzinfo=timezone.utc)


def receipt(observed=None):
    return {"action": clone.ACTION, "commit": COMMIT, "archive_sha256": ARCHIVE_SHA, "source_evidence_sha256": EVIDENCE,
            "database": clone.DATABASE, "real_coach_import_authorized": False, "protected_restore_receipt_sha256": "4" * 64,
            "clone_parity_receipt_sha256": "5" * 64, "reference_sha256": "6" * 64, "system_identifier": "7",
            "clone_oid": "8", "expires_utc": (NOW + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"), **(observed or {})}


def archive_bytes(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, data in files.items():
            archive.writestr(path, data)
    return stream.getvalue()


def fixture_files():
    app = {"competence_hub_api/runtime.py": b"# COMPETENCE_HUB_CAL2_MODE\ndef create_runtime_app_from_environment(): pass\n",
           "competence_hub_api/__init__.py": b"",
           "competence_hub_api/portal_ui/index.html": b"test"}
    wheel_name = "packages/competence_hub_api-0.1.0-py3-none-any.whl"
    dist = "competence_hub_api-0.1.0.dist-info/"
    wheel = {**app, dist + "METADATA": b"Metadata-Version: 2.1\nName: competence-hub-api\nVersion: 0.1.0\n",
             dist + "WHEEL": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n"}
    wheel[dist + "RECORD"] = "".join(f"{name},,\n" for name in (*wheel, dist + "RECORD")).encode("ascii")
    paths = [package.INVENTORY, package.HASH_LOCK]
    paths.extend("wheelhouse/" + row["file"] for row in package.json_read((CACHE / "INVENTORY.json").read_bytes())["files"])
    files = {wheel_name: archive_bytes(wheel),
             **{path: (CACHE / path.removeprefix("wheelhouse/")).read_bytes() for path in paths},
             package.VERSION_LOCK: (DATABASE_FILES.parent / package.VERSION_LOCK).read_bytes(),
             **{path: (DATABASE_FILES / path.removeprefix("database/")).read_bytes() for path in package.MIGRATIONS},
             **{name: ((HERE / Path(name).name).read_bytes() if name.endswith(".service") else b"offline test only")
                for name in package.HELPERS}}
    manifest = {"format": package.FORMAT, "commit": COMMIT, "source_mode": "committed-git-export",
                "tested_source_evidence_sha256": EVIDENCE, "deployment_authorized": False,
                "real_coach_import_authorized": False, "target": package.TARGET, "baseline": package.BASELINE,
                "required_migrations_before": [f"{i:04}" for i in range(1, 7)], "ordered_migrations": package.MIGRATIONS,
                "runtime_source_sha256": {name: package.sha(data) for name, data in app.items()}}
    return files, manifest


class ReleaseContracts(unittest.TestCase):
    def test_approval_rejects_scope_tamper_wrong_hash_and_expiry(self):
        args = SimpleNamespace(commit=COMMIT, sha256=ARCHIVE_SHA, source_evidence_sha256=EVIDENCE)
        approval = receipt()

        def confirm(data, now=NOW, digest=None):
            serialized = package.json_bytes(data)
            return clone.approval_from(serialized, digest or package.sha(serialized), args, now)

        self.assertEqual(confirm(approval), approval)
        for field, value in (("database", "competence_hub_staging"), ("commit", "f" * 40),
                             ("archive_sha256", "a" * 64), ("real_coach_import_authorized", True),
                             ("clone_oid", "'"), ("clone_parity_receipt_sha256", None)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                confirm({**approval, field: value})
        with self.assertRaises(ValueError):
            confirm(approval, NOW + timedelta(hours=1))
        with self.assertRaises(ValueError):
            confirm(approval, digest="f" * 64)

    def test_migration_body_and_psql_redirect_rejection(self):
        for path in package.MIGRATIONS:
            self.assertIn("SET LOCAL ROLE competence_hub_owner;", clone.migration_body(
                (DATABASE_FILES / path.removeprefix("database/")).read_bytes()))
        for sql in (b"\\connect competence_hub_staging", b"COMMIT;", b"ROLLBACK;"):
            with self.assertRaises(ValueError):
                clone.migration_body(b"\\set ON_ERROR_STOP on\nBEGIN;\nSET LOCAL ROLE competence_hub_owner;\n"
                                     + sql + b"\nCOMMIT;\n")

    @unittest.skipUnless(CACHE.is_dir(), "accepted offline cache not present")
    def test_exact_archive_extract_and_tamper_cases(self):
        files, manifest = fixture_files()

        def write(path, members, controls, extra=None):
            inventory = {name: {"sha256": package.sha(data), "bytes": len(data)} for name, data in members.items()}
            data = archive_bytes({**members, "MANIFEST.json": package.json_bytes({**controls, "files": inventory}),
                                  **(extra or {})})
            path.write_bytes(data)
            return package.sha(data)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "package.zip"
            digest = write(path, files, manifest)
            extracted = Path(folder) / "verified"
            accepted, ordered = package.verify(path, digest, COMMIT, EVIDENCE, extracted)
            self.assertEqual(tuple(accepted["ordered_migrations"]), package.MIGRATIONS)
            self.assertEqual(ordered, [files[name] for name in package.MIGRATIONS])
            with self.assertRaises(FileExistsError):
                package.verify(path, digest, COMMIT, EVIDENCE, extracted)
            for sha, commit, evidence in (("f" * 64, COMMIT, EVIDENCE), (digest, "f" * 40, EVIDENCE),
                                          (digest, COMMIT, "f" * 64)):
                with self.assertRaises(ValueError):
                    package.verify(path, sha, commit, evidence)
            for changed, controls, extra in (
                (files, {**manifest, "ordered_migrations": package.MIGRATIONS[::-1]}, None),
                (files, {**manifest, "deployment_authorized": True}, None),
                (files, manifest, {"../escape": b"x"}),
                ({**files, package.INVENTORY: b"{}"}, manifest, None),
                ({**files, "unexpected.txt": b"x"}, manifest, None),
                (files, {**manifest, "runtime_source_sha256": {}}, None),
            ):
                with self.assertRaises(ValueError):
                    package.verify(path, write(path, changed, controls, extra), COMMIT, EVIDENCE)

    def test_host_preservation_rejects_different_invocation_or_extra_listener(self):
        scope = {"commit": COMMIT, "archive_sha256": ARCHIVE_SHA,
                 "source_evidence_sha256": EVIDENCE, "deployment_authorized": False}
        before = {"six_invocation_ids": dict.fromkeys(package.BASELINE["services"], "a" * 32),
                  "reference_listeners_sha256": "b" * 64, "v2_listeners": []}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "before.json"
            data = package.json_bytes({**before, **scope, "phase": "before"})
            path.write_bytes(data)
            args = SimpleNamespace(archive=Path("unchecked"), sha256=ARCHIVE_SHA, commit=COMMIT,
                                   source_evidence_sha256=EVIDENCE, phase="active", before=path,
                                   before_sha256=package.sha(data))
            args.phase = "fallback"
            with patch.object(host, "verify", return_value=({}, None)), \
                    patch.object(host, "properties", return_value={"ActiveState": "inactive"}), \
                    patch.object(host, "inventory") as inventory, patch("builtins.print"):
                inventory.return_value = before
                host.host_check(args)
                for modified in ({"six_invocation_ids": {}}, {"v2_listeners": ["*:8444"]}):
                    with self.assertRaises(ValueError):
                        with patch.object(host, "inventory", return_value={**inventory.return_value, **modified}):
                            host.host_check(args)


@unittest.skipUnless(os.environ.get("CH_V2_OWN_DISPOSABLE_CONTAINER") == "1", "requires owned offline Linux container")
class NativeClone(unittest.TestCase):
    def test_fresh_offline_install_with_pinned_wheels(self):
        self.assertTrue(Path("/.dockerenv").is_file())
        self.assertEqual(sorted(path.name for path in Path("/sys/class/net").iterdir()), ["lo"])
        files, manifest = fixture_files()
        manifest["files"] = {name: {"sha256": package.sha(data), "bytes": len(data)} for name, data in files.items()}
        data = archive_bytes({**files, "MANIFEST.json": package.json_bytes(manifest)})
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / "test.zip"
            archive.write_bytes(data)
            args = SimpleNamespace(archive=archive, sha256=package.sha(data), commit=COMMIT,
                                   source_evidence_sha256=EVIDENCE, runtime=host.V2_RUNTIME)
            host.linux_verify(args)
            self.assertEqual(package.json_read((host.V2_RUNTIME / "V2-INSTALL.json").read_bytes())["commit"], COMMIT)
            self.assertEqual((host.V2_RUNTIME.stat().st_mode & 0o777), 0o755)
            with self.assertRaises(ValueError):
                host.install(args)

    def test_native_transaction_and_fallback_reference(self):
        self.assertTrue(Path("/.dockerenv").is_file())
        self.assertEqual(sorted(path.name for path in Path("/sys/class/net").iterdir()), ["lo"])
        self.assertFalse(Path("/var/run/postgresql/.s.PGSQL.5432").exists())
        bin_dir = "/usr/lib/postgresql/16/bin/"

        def run(*args, data=None):
            return subprocess.run(["runuser", "-u", "postgres", "--", *args], check=True, cwd="/",
                                  input=data, capture_output=True, timeout=60).stdout

        def psql(database, data):
            return run("/usr/bin/psql", "-XqAt", "-v", "ON_ERROR_STOP=1", "-d", database, data=data)

        with tempfile.TemporaryDirectory(prefix="ch-v2-own-pg-") as folder:
            subprocess.run(["chown", "postgres:postgres", folder], check=True)
            data_dir = str(Path(folder) / "data")
            run(bin_dir + "initdb", "--auth-local=peer", "--auth-host=reject", "-D", data_dir)
            run(bin_dir + "pg_ctl", "-D", data_dir, "-l", str(Path(folder) / "postgres.log"), "-w",
                "-o", "-c listen_addresses='' -c unix_socket_directories=/var/run/postgresql -p 5432", "start")
            try:
                bootstrap = (DATABASE_FILES / "bootstrap-staging.sql").read_bytes()
                psql("postgres", bootstrap)
                original = package.BASELINE["source_database"]
                for path in sorted((DATABASE_FILES / "migrations").glob("*.sql"))[:6]:
                    psql(original, path.read_bytes())
                psql(original, b"""
                    INSERT INTO competence_hub.portal_users(display_name,email)
                    SELECT 'Synthetic' || i, 'synthetic' || i || '@example.invalid' FROM generate_series(1,4) i;
                    INSERT INTO competence_hub.coaches(display_name,public_profile_status)
                    SELECT 'Synthetic coach ' || i, 'draft' FROM generate_series(1,2) i;
                    SELECT nextval('competence_hub.audit_events_id_seq');
                """)
                psql("postgres", f"CREATE DATABASE {clone.DATABASE} TEMPLATE {original} OWNER competence_hub_owner;".encode())
                # The clone inherits object ACLs from its template, not database ACLs.
                psql("postgres", bootstrap.replace(b"competence_hub_staging", clone.DATABASE.encode()))

                def native(sql):
                    return package.json_read(psql(clone.DATABASE, sql.encode("utf-8")))

                migrations = [(DATABASE_FILES / path.removeprefix("database/")).read_bytes() for path in package.MIGRATIONS]
                original_before = run(bin_dir + "pg_dump", "--data-only", original)
                before = native(clone.plan(migrations))
                approval = receipt(before)
                failed = migrations.copy()
                failed[2] = re.sub(rb"COMMIT;\s*$", b"SELECT 1/0;\nCOMMIT;\n", failed[2])
                with self.assertRaises(subprocess.CalledProcessError) as failure:
                    native(clone.plan(failed, approval))
                self.assertIn(b"division by zero", failure.exception.stderr)
                self.assertEqual(native(clone.plan(migrations)), before)
                with self.assertRaises(subprocess.CalledProcessError):
                    native(clone.plan(migrations, {**approval, "clone_oid": "1"}))
                self.assertEqual(native(clone.plan(migrations, approval)), before)
                self.assertEqual(native(clone.plan(migrations, ready=True)), before)
                with self.assertRaises(subprocess.CalledProcessError):
                    native(clone.plan(migrations, approval))
                psql(clone.DATABASE, b"""
                    INSERT INTO competence_hub.auth_sessions
                      (portal_user_id, token_hash, csrf_token_hash, authenticated_at, mfa_completed_at,
                       idle_expires_at, absolute_expires_at)
                    SELECT id, sha256('session'), sha256('csrf'), now(), now(), now() + interval '5 minutes',
                           now() + interval '1 hour' FROM competence_hub.portal_users LIMIT 1;
                """)
                with self.assertRaises(subprocess.CalledProcessError) as failure:
                    native(clone.plan(migrations, ready=True))
                self.assertIn(b"CLONED_AUTH_STATE_MUST_NOT_BE_REPLAYABLE", failure.exception.stderr)
                original_after = run(bin_dir + "pg_dump", "--data-only", original)
                self.assertEqual(re.sub(rb"(?m)^\\(?:un)?restrict .*\n", b"", original_before),
                                 re.sub(rb"(?m)^\\(?:un)?restrict .*\n", b"", original_after))
            finally:
                run(bin_dir + "pg_ctl", "-D", data_dir, "-m", "immediate", "-w", "stop")


if __name__ == "__main__":
    unittest.main()
