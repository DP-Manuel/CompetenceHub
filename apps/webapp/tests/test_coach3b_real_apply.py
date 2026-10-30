"""Operator guards use synthetic metadata, never Staging or credential files."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from uuid import UUID

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "coach3b_real_apply", ROOT / "scripts/coach3b_real_apply.py"
)
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)
NOW = datetime(2026, 10, 30, 10, tzinfo=UTC)
OPERATOR = UUID("10000000-0000-0000-0000-000000000001")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.parametrize("role", ["competence_hub_app", "competence_hub_migrator"])
def test_exact_tunnel_target_only(role):
    runner.target_url(
        f"postgresql+asyncpg://{role}:synthetic@127.0.0.1:55432/competence_hub_staging",
        role,
    )


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not-a-url",
        "postgresql://competence_hub_app:synthetic@127.0.0.1:55432/competence_hub_staging",
        "postgresql+asyncpg://competence_hub_app:synthetic@localhost:55432/competence_hub_staging",
        "postgresql+asyncpg://competence_hub_app:synthetic@217.160.255.86:5432/competence_hub_staging",
        "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55436/competence_hub_staging",
        "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55432/competence_hub_production",
        "postgresql+asyncpg://postgres:synthetic@127.0.0.1:55432/competence_hub_staging",
        "postgresql+asyncpg://competence_hub_app@127.0.0.1:55432/competence_hub_staging",
        "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55432/competence_hub_staging?host=outside.invalid",
    ],
)
def test_unsafe_targets_rejected_without_echoing_urls(url):
    with pytest.raises(runner.GateError) as error:
        runner.target_url(url, "competence_hub_app")
    assert str(error.value) == "TARGET_URL_REJECTED"


def proof():
    return {
        "schema": 1,
        "purpose": "COACH3B_ONE_WINDOW_READINESS",
        "target_database": "competence_hub_staging",
        "environment": "staging",
        "server": "manuel@217.160.255.86",
        "manifest_sha256": "a" * 64,
        "operator_id": str(OPERATOR),
        "verified_at": NOW.isoformat(),
        "checks": {
            k: "PASS"
            for k in (
                "target",
                "host_key",
                "pushed_clean_runner",
                "backup",
                "restore",
                "restore_cleanup",
                "service_health",
                "postgres_localhost",
            )
        },
        "backup": {
            "database": "competence_hub_staging",
            "recipient": "2E44306121629A100F76A8B08CCA3D9186A28D4C",
            "remote_directory": "/var/backups/competence-hub/pre-coach3b/synthetic-window",
            "dump_gpg_sha256": "b" * 64,
            "globals_gpg_sha256": "c" * 64,
            "metadata_sha256": "d" * 64,
            "baseline_sha256": "e" * 64,
            "private_key_on_vps": False,
        },
        "restore": {
            "encrypted_dump_sha256": "b" * 64,
            "baseline_sha256": "e" * 64,
            "isolated": True,
            "temporary_database_removed": True,
            "plaintext_residue": 0,
            "container_residue": 0,
        },
    }


def store_proof(tmp_path, monkeypatch, value):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    target = tmp_path / ".tmp" / "window.json"
    target.parent.mkdir(exist_ok=True)
    raw = json.dumps(value, sort_keys=True).encode()
    target.write_bytes(raw)
    return target, hashlib.sha256(raw).hexdigest()


def read_proof(path, sha, **kwargs):
    return runner.read_window_proof(
        path, sha, manifest_sha256="a" * 64, operator_id=OPERATOR, now=NOW, **kwargs
    )


def test_exact_current_protected_window_metadata(tmp_path, monkeypatch):
    value = proof()
    path, sha = store_proof(tmp_path, monkeypatch, value)
    assert read_proof(path, sha) == value


@pytest.mark.parametrize(
    "mutation",
    [
        "database",
        "server",
        "environment",
        "manifest",
        "operator",
        "expired",
        "future",
        "no_timezone",
        "failed_gate",
        "missing_gate",
        "wrong_key",
        "plaintext",
        "container",
        "wrong_dump",
        "wrong_baseline",
        "private_key",
        "remote_path",
    ],
)
def test_incomplete_backup_or_restore_window_cannot_authorize_apply(
    tmp_path, monkeypatch, mutation
):
    value = proof()
    if mutation in {"database", "server", "environment", "manifest", "operator"}:
        key = {
            "database": "target_database",
            "manifest": "manifest_sha256",
            "operator": "operator_id",
        }.get(mutation, mutation)
        value[key] = "different"
    elif mutation == "expired":
        value["verified_at"] = (NOW - timedelta(hours=5)).isoformat()
    elif mutation == "future":
        value["verified_at"] = (NOW + timedelta(seconds=1)).isoformat()
    elif mutation == "no_timezone":
        value["verified_at"] = NOW.replace(tzinfo=None).isoformat()
    elif mutation == "failed_gate":
        value["checks"]["restore"] = "FAIL"
    elif mutation == "missing_gate":
        del value["checks"]["restore"]
    elif mutation == "wrong_key":
        value["backup"]["recipient"] = "0" * 40
    elif mutation in {"plaintext", "container"}:
        value["restore"][mutation + "_residue"] = 1
    elif mutation in {"wrong_dump", "wrong_baseline"}:
        value["restore"][
            "encrypted_dump_sha256" if mutation == "wrong_dump" else "baseline_sha256"
        ] = ("f" * 64)
    elif mutation == "private_key":
        value["backup"]["private_key_on_vps"] = True
    else:
        value["backup"]["remote_directory"] = "/home/manuel/unprotected"
    path, sha = store_proof(tmp_path, monkeypatch, value)
    with pytest.raises(runner.GateError):
        read_proof(path, sha)


def test_window_proof_must_be_exact_bytes_and_inside_private_context(
    tmp_path, monkeypatch
):
    path, sha = store_proof(tmp_path, monkeypatch, proof())
    with pytest.raises(runner.GateError, match="WINDOW_PROOF_HASH_CHANGED"):
        read_proof(path, "0" * 64)
    outside = tmp_path / "public.json"
    outside.write_bytes(path.read_bytes())
    with pytest.raises(runner.GateError, match="WINDOW_PROOF_PATH_REJECTED"):
        read_proof(outside, sha)


def test_non_registry_changes_include_calendar_auth_taxonomy():
    before = {
        k: {"count": 0, "versions": "synthetic"}
        for k in (
            "coaches",
            "audit_events",
            "calendar_offers",
            "coach_topics",
            "topics",
            "portal_users",
            "auth_sessions",
        )
    }
    after = deepcopy(before)
    after["coaches"]["count"] = 9
    after["audit_events"]["count"] = 50
    assert runner.unchanged_outside_registry(before, after)
    for name in (
        "calendar_offers",
        "coach_topics",
        "topics",
        "portal_users",
        "auth_sessions",
    ):
        changed = deepcopy(after)
        changed[name]["versions"] = "updated-even-if-count-still-zero"
        assert not runner.unchanged_outside_registry(before, changed)


@pytest.mark.anyio
async def test_no_operator_never_queries_or_creates_an_account():
    class Forbidden:
        async def execute(self, *args, **kwargs):
            pytest.fail("must reject missing operator before SQL")

    importer = object.__new__(runner.RealCoachImporter)
    with pytest.raises(runner.GateError, match="EXISTING_APPROVED_OPERATOR_REQUIRED"):
        await importer._operator(Forbidden(), None)


@pytest.mark.anyio
async def test_inactive_or_absent_admin_is_not_silently_onboarded(monkeypatch):
    statements = []

    async def empty(c, sql, **params):
        statements.append(sql)
        return []

    monkeypatch.setattr(runner, "rows", empty)
    importer = object.__new__(runner.RealCoachImporter)
    with pytest.raises(
        runner.GateError, match="EXISTING_ACTIVE_ADMIN_REQUIRED_NO_ONBOARDING"
    ):
        await importer._operator(object(), OPERATOR)
    assert len(statements) == 1 and statements[0].strip().startswith("SELECT")


@pytest.mark.anyio
async def test_apply_without_window_proof_does_not_open_target(monkeypatch):
    importer = object.__new__(runner.RealCoachImporter)
    importer.manifest_sha256 = "a" * 64

    async def forbidden(*args, **kwargs):
        pytest.fail("unverified backup must stop before DB access")

    importer.target_preflight = forbidden
    with pytest.raises((runner.GateError, TypeError)):
        await importer.apply_real(
            operator_id=OPERATOR,
            plan_sha256="a" * 64,
            window_proof=None,
            window_proof_sha256="b" * 64,
        )


def test_real_cli_apply_is_disabled_even_with_hand_authored_window(
    tmp_path, monkeypatch, capsys
):
    path, sha = store_proof(tmp_path, monkeypatch, proof())

    def forbidden(*args, **kwargs):
        pytest.fail("disabled APPLY must not read a manifest, secrets or a DB")

    monkeypatch.setattr(runner, "read_manifest", forbidden)
    result = runner.main(
        [
            "apply",
            "--manifest",
            "not-read.json",
            "--manifest-sha256",
            "a" * 64,
            "--window-proof",
            str(path),
            "--window-proof-sha256",
            sha,
        ]
    )
    assert result == 1
    assert json.loads(capsys.readouterr().out) == {
        "result": "STOP",
        "gate": "REAL_APPLY_DISABLED_WINDOW_ORCHESTRATOR_REQUIRED",
        "acceptance": "NOT_COMPLETE",
    }
