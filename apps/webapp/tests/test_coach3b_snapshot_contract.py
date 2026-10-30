"""Offline contract/fake-command tests, NOT evidence of encryption or DB restore.

Only a disposable copy has its fixed paths/PATH redirected. No real psql, GPG,
SSH, Docker, credential files or network command may run in this test suite.
POSIX ownership is simulated on Windows; actual Linux permissions remain a gate.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "deploy/scripts/competence-hub-postgres-snapshot"
FINGERPRINT = "2E44306121629A100F76A8B08CCA3D9186A28D4C"


def bash_path() -> str:
    candidates = []
    if os.name == "nt":
        for variable in ("ProgramFiles", "LocalAppData"):
            if base := os.environ.get(variable):
                candidates.extend(
                    [Path(base) / "Git/bin/bash.exe", Path(base) / "Programs/Git/bin/bash.exe"]
                )
    else:
        if executable := shutil.which("bash"):
            candidates.append(Path(executable))
    if not (found := next((path for path in candidates if path.is_file()), None)):
        pytest.skip("Native Bash unavailable; do not substitute WSL or a real server")
    return str(found)


def test_fixed_target_no_credentials_retention_install_or_network() -> None:
    source = SCRIPT.read_text(encoding="ascii")
    assert source.startswith("#!/usr/bin/env bash\n")
    assert b"\r" not in SCRIPT.read_bytes()
    for setting in (
        'BACKUP_ROOT="/var/backups/competence-hub"',
        'GPG_HOME="/var/lib/competence-hub-backup/gnupg"',
        'PG_SOCKET="/var/run/postgresql"',
        'DATABASE="competence_hub_staging"',
        f'RECIPIENT="{FINGERPRINT}"',
    ):
        assert setting in source
    for forbidden in ("backup.conf", ".env", "--decrypt", "--list-secret-keys", "prune_sets", "rm -rf"):
        assert forbidden not in source
    assert not re.search(r"^\s*(?:ssh|scp|sftp|curl|wget|systemctl|sudo|createdb|dropdb)\s", source, re.M)
    assert "for variable in ${!PG@}; do unset" in source
    assert "PGPASSFILE=/dev/null PGSERVICEFILE=/dev/null" in source
    assert source.count("--no-password") == 3
    assert "--no-options" in source and "--no-auto-key-retrieve" in source
    assert "--globals-only --no-role-passwords" in source
    assert "NOT blanket execution approval" in source
    assert "OFF the VPS" in source and "NOT a full restore PASS" in source


def test_baseline_is_counts_versions_and_owners_bound_to_dump_snapshot() -> None:
    source = SCRIPT.read_text(encoding="ascii")
    assert "BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY" in source
    assert "SELECT pg_export_snapshot();" in source
    assert '--snapshot "$snapshot" --format=custom' in source
    assert "json_agg(version ORDER BY version)" in source
    assert "FROM competence_hub.schema_migrations" in source
    assert "pg_get_userbyid(datdba)" in source
    assert "pg_get_userbyid(nspowner)" in source
    assert "pg_get_userbyid(c.relowner)" in source
    assert "''row_count'',count(*)" in source
    assert "%I.%I" in source and "%L" in source  # quoted identifiers and literals
    assert "SELECT *" not in source and "pg_authid" not in source
    assert "reltuples" not in source
    assert "WHERE schemaname = 'competence_hub'" not in source
    assert source.index('wait "$snapshot_pid"') < source.index('snapshot_pid=""', source.index('wait "$snapshot_pid"'))
    assert source.index('--snapshot "$snapshot"') < source.index("'COMMIT;'")
    assert source.index('rm -- "$work_dir/database.dump"') < source.index('touch "$work_dir/COMPLETE"')
    assert source.index('mv -T -n -- "$work_dir" "$final_set"') < source.index('chmod 0500 "$final_set"')
    for signal in ("HUP", "INT", "TERM"):
        assert re.search(rf"trap 'exit \d+' {signal}", source)
    assert "-type f -delete" in source and "operator review required" in source


FAKE_COMMAND = r'''#!/bin/bash
set -eu
tool="${0##*/}"
printf '%s\n' "$tool" >> "$TEST_TRACE"
case "$tool" in
id)
    if [[ "$TEST_CASE" == root-user ]]; then printf 'root\n'
    else printf 'postgres\n'; fi ;;
flock) [[ "$TEST_CASE" != locked ]] ;;
stat)
    case "$2" in
        %U) printf 'postgres\n' ;;
        %h) printf '1\n' ;;
        %a)
            if [[ "$TEST_CASE" == unsafe-root && "$3" == "$TEST_ROOT/backup" ]]; then
                printf '777\n'
            elif [[ "$3" == *.snapshot.lock ]]; then printf '600\n'
            else printf '700\n'; fi ;;
        *) exec /usr/bin/stat "$@" ;;
    esac ;;
gpg)
    if [[ " $* " == *' --fingerprint '* ]]; then
        if [[ "$TEST_CASE" == wrong-key ]]; then
            printf 'fpr:::::::::0000000000000000000000000000000000000000:\n'
        else printf 'fpr:::::::::2E44306121629A100F76A8B08CCA3D9186A28D4C:\n'; fi
    else
        output=''
        while (( $# )); do
            if [[ "$1" == --output ]]; then output="$2"; shift 2; else shift; fi
        done
        if [[ "$TEST_CASE" == encrypt-fail && "$output" == *globals* ]]; then exit 1; fi
        printf 'FAKE ENCRYPTED PAYLOAD\n' > "$output"
    fi ;;
psql|pg_dump|pg_dumpall)
    [[ "${PGHOST-unset}" == unset && "${PGPASSWORD-unset}" == unset && "${PGSERVICE-unset}" == unset ]]
    [[ "$PGPASSFILE" == /dev/null && "$PGSERVICEFILE" == /dev/null ]]
    [[ " $* " == *' --host /var/run/postgresql '* && " $* " == *' --no-password '* ]]
    case "$tool" in
    psql)
        while IFS= read -r line; do
            case "$line" in
                'SELECT current_database()'*)
                    if [[ "$TEST_CASE" == wrong-db ]]; then printf 'other|1|0\n'
                    else printf 'competence_hub_staging|1|0\n'; fi ;;
                'SELECT pg_export_snapshot();') printf '00000003-00000001-1\n' ;;
                "SELECT 'BASELINE_END';")
                    if [[ "$TEST_CASE" == baseline-fail ]]; then exit 1; fi
                    printf '%s\n' \
                        '{"kind":"database","name":"competence_hub_staging","owner":"competence_hub_owner"}' \
                        '{"kind":"migrations","versions":["0001","0006"]}' \
                        '{"kind":"schema","name":"competence_hub","owner":"competence_hub_owner"}' \
                        '{"kind":"relation","schema":"competence_hub","name":"users","relkind":"r","owner":"competence_hub_owner"}' \
                        '{"kind":"table","schema":"competence_hub","name":"users","row_count":0}' \
                        BASELINE_END ;;
                '\q') exit 0 ;;
            esac
        done ;;
    pg_dump)
        output=''
        while (( $# )); do
            if [[ "$1" == --file ]]; then output="$2"; shift 2; else shift; fi
        done
        printf 'FAKE PLAINTEXT DATABASE\n' > "$output"
        if [[ "$TEST_CASE" == dump-fail ]]; then exit 1; fi
        if [[ "$TEST_CASE" == signal ]]; then kill -TERM "$PPID"; fi ;;
    pg_dumpall)
        printf 'FAKE PASSWORD-FREE GLOBALS\n'
        if [[ "$TEST_CASE" == globals-fail ]]; then exit 1; fi ;;
    esac ;;
chmod)
    if [[ "$1" == 0500 ]]; then
        printf 'publish-mode-0500\n' >> "$TEST_TRACE"
        if [[ "$TEST_CASE" == chmod-fail ]]; then exit 1; fi
    fi
    exec /usr/bin/chmod "$@" ;;
sha256sum)
    if [[ "$TEST_CASE" == checksum-fail && "$1" == --check ]]; then exit 1; fi
    exec /usr/bin/sha256sum "$@" ;;
mv)
    if [[ "$TEST_CASE" == collision ]]; then
        target="${@: -1}"
        mkdir -- "$target"
        printf 'unowned\n' > "$target/KEEP"
    fi
    exec /usr/bin/mv "$@" ;;
*) exit 90 ;;
esac
'''


@pytest.fixture
def sandbox(tmp_path: Path):
    bash = bash_path()
    root = subprocess.run(
        [bash, "--noprofile", "--norc", "-c", 'cd "$1" && pwd -P', "sandbox", str(tmp_path)],
        check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()
    for directory in ("bin", "backup", "gnupg"):
        (tmp_path / directory).mkdir(mode=0o700)
    for tool in ("id", "stat", "flock", "gpg", "psql", "pg_dump", "pg_dumpall", "chmod", "sha256sum", "mv"):
        path = tmp_path / "bin" / tool
        path.write_text(FAKE_COMMAND, encoding="ascii", newline="\n")
        path.chmod(0o700)
    source = SCRIPT.read_text(encoding="ascii")
    source = source.replace('readonly PATH="/usr/sbin:/usr/bin:/sbin:/bin"', f'readonly PATH="{root}/bin:/usr/bin:/bin"')
    source = source.replace('BACKUP_ROOT="/var/backups/competence-hub"', f'BACKUP_ROOT="{root}/backup"')
    source = source.replace('GPG_HOME="/var/lib/competence-hub-backup/gnupg"', f'GPG_HOME="{root}/gnupg"')
    candidate = tmp_path / "candidate"
    candidate.write_text(source, encoding="utf-8", newline="\n")
    environment = dict(os.environ, TEST_ROOT=root, TEST_TRACE=f"{root}/trace", TEST_CASE="ok",
                       PGHOST="do-not-use", PGPASSWORD="FAKE-NEVER-LOG", PGSERVICE="do-not-use")
    # No inherited Bash startup hook is permitted in the offline harness.
    for name in ("BASH_ENV", "ENV", "SHELLOPTS", "BASHOPTS"):
        environment.pop(name, None)

    def run(*arguments: str, case: str = "ok"):
        return subprocess.run(
            [bash, "--noprofile", "--norc", str(candidate), *arguments],
            env=dict(environment, TEST_CASE=case), capture_output=True, text=True, encoding="utf-8", timeout=20,
        )

    return tmp_path, root, run


def test_bash_syntax() -> None:
    result = subprocess.run([bash_path(), "-n", str(SCRIPT)], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("arguments", [
    (), ("--run-id", "run1"), ("--confirm-staging-snapshot",),
    ("--confirm-staging-snapshot", "--run-id", "../escape"),
    ("--confirm-staging-snapshot", "--run-id", "/absolute"),
    ("--confirm-staging-snapshot", "--run-id", "unsafe space"),
    ("--confirm-staging-snapshot", "--run-id", "x\ninjection"),
    ("--confirm-staging-snapshot", "--run-id", "A"),
    ("--confirm-staging-snapshot", "--run-id", "a" * 65),
    ("--confirm-staging-snapshot", "--run-id", "-bad"),
    ("--confirm-staging-snapshot", "--run-id", "ok", "--run-id", "other"),
    ("--confirm-staging-snapshot", "--confirm-staging-snapshot", "--run-id", "ok"),
    ("--confirm-staging-snapshot", "--run-id", "ok", "--database", "other"),
])
def test_bad_cli_stops_before_any_command(sandbox, arguments) -> None:
    path, _, run = sandbox
    result = run(*arguments)
    assert result.returncode != 0 and result.stdout == ""
    assert not (path / "trace").exists()


def test_success_manifest_hashes_baseline_and_no_overwrite(sandbox) -> None:
    path, root, run = sandbox
    arguments = ("--confirm-staging-snapshot", "--run-id", "window-20261030_01")
    result = run(*arguments)
    assert result.returncode == 0, result.stderr
    manifest = json.loads(result.stdout)
    expected_keys = {"snapshot_path"} | {f"{name}_{suffix}" for name in (
        "dump", "globals", "metadata", "checksums", "complete") for suffix in ("path", "sha256")}
    assert set(manifest) == expected_keys
    final = path / "backup/prechange-window-20261030_01"
    assert manifest["snapshot_path"] == f"{root}/backup/{final.name}"
    assert {item.name for item in final.iterdir()} == {
        "database.dump.gpg", "globals.sql.gpg", "METADATA", "SHA256SUMS", "COMPLETE"}
    for name, filename in (("dump", "database.dump.gpg"), ("globals", "globals.sql.gpg"),
                           ("metadata", "METADATA"), ("checksums", "SHA256SUMS"), ("complete", "COMPLETE")):
        assert manifest[f"{name}_path"] == f"{manifest['snapshot_path']}/{filename}"
        assert manifest[f"{name}_sha256"] == hashlib.sha256((final / filename).read_bytes()).hexdigest()
    records = [json.loads(line) for line in (final / "METADATA").read_text().splitlines()]
    assert records[0]["format"] == "competence-hub.prechange.v1"
    assert records[0]["restore_verified"] is False
    assert records[0]["recipient"] == FINGERPRINT
    assert records[2] == {"kind": "migrations", "versions": ["0001", "0006"]}
    assert records[-1]["row_count"] == 0
    lines = (final / "SHA256SUMS").read_text().splitlines()
    assert len(lines) == 3
    for line in lines:
        digest, filename = line.split("  ")
        assert filename in {"database.dump.gpg", "globals.sql.gpg", "METADATA"}
        assert hashlib.sha256((final / filename).read_bytes()).hexdigest() == digest
    trace = (path / "trace").read_text().splitlines()
    assert trace.index("pg_dump") < trace.index("mv") < trace.index("publish-mode-0500")
    assert not list((path / "backup").glob(".snapshot-*-*"))
    before = {item.name: item.read_bytes() for item in final.iterdir()}
    repeated = run(*arguments)
    assert repeated.returncode != 0 and repeated.stdout == ""
    assert before == {item.name: item.read_bytes() for item in final.iterdir()}
    second = run("--confirm-staging-snapshot", "--run-id", "window-20261030_02")
    assert second.returncode == 0, second.stderr
    assert json.loads(second.stdout)["snapshot_path"] != manifest["snapshot_path"]
    if os.name != "nt":
        assert final.stat().st_mode & 0o777 == 0o500
        assert all(item.stat().st_mode & 0o777 == 0o400 for item in final.iterdir())


@pytest.mark.parametrize(("case", "diagnostic", "reached"), [
    ("root-user", "run as the postgres OS user", "id"),
    ("wrong-key", "primary public fingerprint", "gpg"),
    ("unsafe-root", "must already be postgres-owned", "stat"),
    ("locked", "another snapshot is active", "flock"),
    ("wrong-db", "unexpected database/schema", "psql"),
    ("baseline-fail", "baseline read failed", "psql"),
    ("globals-fail", "globals export failed", "pg_dumpall"),
    ("dump-fail", "custom dump failed", "pg_dump"),
    ("encrypt-fail", "encryption failed", "gpg"),
    ("checksum-fail", "", "sha256sum"),
    ("chmod-fail", "permissions could not be secured", "publish-mode-0500"),
    ("signal", "", "pg_dump"),
    ("collision", "publication refused", "mv"),
])
def test_failures_never_report_success_and_remove_owned_plaintext(sandbox, case, diagnostic, reached) -> None:
    path, _, run = sandbox
    result = run("--confirm-staging-snapshot", "--run-id", "failure", case=case)
    assert result.returncode != 0 and result.stdout == "", result.stderr
    assert diagnostic in result.stderr
    assert reached in (path / "trace").read_text().splitlines()
    if case == "signal":
        assert result.returncode == 143
    assert "FAKE-NEVER-LOG" not in result.stderr
    assert not list((path / "backup").glob(".snapshot-*-*"))
    assert not list((path / "backup").rglob("*.dump"))
    assert not list((path / "backup").rglob("*.sql"))
    final = path / "backup/prechange-failure"
    if case == "collision":
        assert (final / "KEEP").read_text() == "unowned\n"
        assert {entry.name for entry in final.iterdir()} == {"KEEP"}
    else:
        assert not final.exists()


def test_private_key_presence_is_rejected_without_reading_it(sandbox) -> None:
    path, _, run = sandbox
    private = path / "gnupg/private-keys-v1.d"
    private.mkdir()
    (private / "unread-key-marker").touch()
    result = run("--confirm-staging-snapshot", "--run-id", "blocked")
    assert result.returncode != 0 and result.stdout == ""
    assert "private keys or key stubs" in result.stderr
    assert "gpg" not in (path / "trace").read_text().splitlines()
    assert not list((path / "backup").iterdir())


def test_legacy_private_keyring_is_rejected_without_opening_it(sandbox) -> None:
    path, _, run = sandbox
    (path / "gnupg/secring.gpg").touch()
    result = run("--confirm-staging-snapshot", "--run-id", "blocked")
    assert result.returncode != 0 and result.stdout == ""
    assert "legacy private keyring" in result.stderr
    assert "gpg" not in (path / "trace").read_text().splitlines()
    assert not list((path / "backup").iterdir())


@pytest.mark.parametrize("target", ["lock", "destination", "root", "keyhome"])
def test_symlinks_are_refused_without_following_or_deleting(sandbox, target) -> None:
    path, _, run = sandbox
    outside = path / "outside"
    outside.mkdir()
    (outside / "KEEP").write_text("unowned", encoding="ascii")
    location = {"lock": path / "backup/.snapshot.lock", "destination": path / "backup/prechange-blocked",
                "root": path / "backup", "keyhome": path / "gnupg"}[target]
    if location.is_dir():
        location.rmdir()
    try:
        location.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("OS does not permit local symlink creation")
    result = run("--confirm-staging-snapshot", "--run-id", "blocked")
    assert result.returncode != 0 and result.stdout == ""
    assert (outside / "KEEP").read_text() == "unowned"
    assert {item.name for item in outside.iterdir()} == {"KEEP"}
    trace = (path / "trace").read_text().splitlines()
    assert "psql" not in trace and "pg_dump" not in trace
