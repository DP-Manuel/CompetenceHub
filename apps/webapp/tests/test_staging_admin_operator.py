from copy import deepcopy
import asyncio
from datetime import UTC, datetime, timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "staging_admin_operator", ROOT / "apps/webapp/scripts/staging_admin_operator.py"
)
operator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = operator
spec.loader.exec_module(operator)
NOW = datetime(2026, 10, 30, 10, tzinfo=UTC)


def login():
    return {
        "schema": 1,
        "display_name": "Manuel",
        "email": "synthetic-operator@example.invalid",
        "roles": ["admin"],
        "target_database": "competence_hub_staging",
        "environment": "staging",
        "source": "synthetic explicit approval",
        "coach_mapping": None,
        "calendar_mapping": None,
    }


@pytest.mark.parametrize(
    "name",
    [
        "DEBUG",
        "DEBUG_FILE",
        "DEBUGP",
        "PWDEBUG",
        "PW_TEST_CONNECT_WS_ENDPOINT",
        "PLAYWRIGHT_DRIVER_PATH",
        "NODE_OPTIONS",
        "PYTHONINSPECT",
        "PYTHONASYNCIODEBUG",
    ],
)
def test_diagnostic_and_remote_driver_environment_is_rejected_before_secrets(name):
    with pytest.raises(ValueError, match="PRIVATE_DIAGNOSTIC"):
        operator.require_private_environment({name: "synthetic-diagnostic-value"})
    operator.require_private_environment(
        {"PYTHONPATH": str(operator.ROOT / "apps" / "webapp" / "src")}
    )
    with pytest.raises(ValueError, match="REVIEWED_PYTHON"):
        operator.require_private_environment(
            {"PYTHONPATH": "arbitrary-unreviewed-imports"}
        )


@pytest.mark.parametrize(
    "change", ["none", "email", "role", "display_name", "database", "coach", "extra"]
)
def test_only_named_admin_exact_approved_login_without_guessing(
    tmp_path, monkeypatch, change
):
    monkeypatch.setattr(operator, "ROOT", tmp_path)
    path = tmp_path / ".tmp" / "login.json"
    path.parent.mkdir()
    value = login()
    if change == "email":
        value["email"] = ""
    elif change == "role":
        value["roles"].append("coach")
    elif change == "display_name":
        value["display_name"] = "Other person"
    elif change == "database":
        value["target_database"] = "production"
    elif change == "coach":
        value["coach_mapping"] = "guessed-uuid"
    elif change == "extra":
        value["password"] = "synthetic unexpected value"
    path.write_text(json.dumps(value), encoding="utf-8")
    if change == "none":
        assert operator.read_login(path) == value
    else:
        with pytest.raises(ValueError):
            operator.read_login(path)


def proof_fixture(tmp_path, monkeypatch):
    repo = tmp_path / "repository"
    repo.mkdir()
    monkeypatch.setattr(operator, "ROOT", repo)
    backup = tmp_path / "protected-backup"
    backup.mkdir()
    (backup / "database.dump.gpg").write_bytes(b"synthetic encrypted fixture")
    records = [
        {
            "kind": "header",
            "format": "competence-hub.prechange.v1",
            "run_id": "synthetic-review",
            "created_at_utc": NOW.strftime("%Y%m%dT%H%M%SZ"),
            "database": "competence_hub_staging",
            "recipient": operator.baseline_verifier.RECIPIENT,
            "encryption": "openpgp",
            "baseline_scope": "all_non_system_schemas",
            "consistency": "exported_mvcc_snapshot",
            "role_passwords_included": False,
            "restore_verified": False,
        },
        {
            "kind": "database",
            "name": "competence_hub_staging",
            "owner": "competence_hub_owner",
        },
        {"kind": "migrations", "versions": [f"{i:04}" for i in range(1, 7)]},
        {"kind": "schema", "name": "competence_hub", "owner": "competence_hub_owner"},
        {"kind": "schema", "name": "public", "owner": "pg_database_owner"},
    ]
    for table, count in (("schema_migrations", 6), ("portal_users", 0), ("coaches", 0)):
        records.extend(
            [
                {
                    "kind": "relation",
                    "schema": "competence_hub",
                    "name": table,
                    "relkind": "r",
                    "owner": "competence_hub_owner",
                },
                {
                    "kind": "table",
                    "schema": "competence_hub",
                    "name": table,
                    "row_count": count,
                },
            ]
        )
    metadata = ("\n".join(json.dumps(row) for row in records) + "\n").encode()
    (backup / "METADATA").write_bytes(metadata)
    summary = operator.baseline_verifier.validate_metadata(metadata)
    proof = {
        "schema": operator.PROOF_SCHEMA,
        "status": "PASS",
        "source_directory": str(backup),
        "owners_verified": True,
        "encrypted_copy_verified": True,
        "temporary_database_removed": True,
        "container_removed": True,
        "plaintext_removed": True,
        "finished_at_utc": NOW.isoformat(),
        "dump_gpg_sha256": hashlib.sha256(
            (backup / "database.dump.gpg").read_bytes()
        ).hexdigest(),
        "metadata_sha256": hashlib.sha256(metadata).hexdigest(),
        "migrations": summary["migrations"],
        "row_counts": summary["row_counts"],
        "baseline_sha256": summary["baseline_sha256"],
        "restore_image": operator.RESTORE_IMAGE,
    }
    path = tmp_path / "restore-proof.json"
    return path, backup, proof


@pytest.mark.parametrize(
    "change",
    [
        "none",
        "cleanup",
        "expired",
        "future",
        "owner",
        "dump",
        "versions",
        "source",
        "status",
        "counts",
        "baseline",
        "image",
        "metadata-target",
        "metadata-owner",
        "old-snapshot",
    ],
)
def test_exact_fresh_external_restore_is_required_before_real_bootstrap(
    tmp_path, monkeypatch, change
):
    path, backup, proof = proof_fixture(tmp_path, monkeypatch)
    if change == "cleanup":
        proof["plaintext_removed"] = False
    elif change == "expired":
        proof["finished_at_utc"] = (NOW - timedelta(hours=5)).isoformat()
    elif change == "future":
        proof["finished_at_utc"] = (NOW + timedelta(seconds=5)).isoformat()
    elif change == "owner":
        proof["owners_verified"] = False
    elif change == "dump":
        proof["dump_gpg_sha256"] = "0" * 64
    elif change == "versions":
        proof["migrations"].pop(2)
    elif change == "source":
        proof["source_directory"] = str(tmp_path / "other")
    elif change == "status":
        proof["status"] = "NOT_RUN"
    elif change == "counts":
        proof["row_counts"]["competence_hub.portal_users"] = 2
    elif change == "baseline":
        proof["baseline_sha256"] = "0" * 64
    elif change == "image":
        proof["restore_image"] = "postgres:latest"
    elif change in ("metadata-target", "metadata-owner", "old-snapshot"):
        metadata = (backup / "METADATA").read_text()
        if change == "metadata-target":
            metadata = metadata.replace("competence_hub_staging", "production")
        elif change == "metadata-owner":
            metadata = metadata.replace("competence_hub_owner", "other_owner")
        else:
            metadata = metadata.replace(
                NOW.strftime("%Y%m%dT%H%M%SZ"),
                (NOW - timedelta(days=1)).strftime("%Y%m%dT%H%M%SZ"),
            )
        (backup / "METADATA").write_text(metadata, newline="")
        proof["metadata_sha256"] = hashlib.sha256(
            (backup / "METADATA").read_bytes()
        ).hexdigest()
    path.write_text(json.dumps(proof), encoding="utf-8")
    if change == "none":
        assert operator.verify_restore_proof(path, backup, NOW) == proof
    else:
        with pytest.raises(ValueError):
            operator.verify_restore_proof(path, backup, NOW)


def test_production_remote_or_wrong_role_is_never_a_staging_tunnel():
    values = {
        "COMPETENCE_HUB_OPERATOR_APP_URL": "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55432/competence_hub_staging",
        "COMPETENCE_HUB_OPERATOR_OWNER_URL": "postgresql+asyncpg://competence_hub_migrator:synthetic@127.0.0.1:55432/competence_hub_staging",
    }
    assert operator.target_urls(values) == list(values.values())
    for bad in (
        "postgresql+asyncpg://postgres:synthetic@127.0.0.1:55432/competence_hub_staging",
        "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55432/production",
        "postgresql+asyncpg://competence_hub_app:synthetic@217.160.255.86:5432/competence_hub_staging",
    ):
        with pytest.raises(ValueError):
            operator.target_urls({**values, "COMPETENCE_HUB_OPERATOR_APP_URL": bad})


def test_database_worker_is_compatible_with_a_running_playwright_event_loop():
    async def value():
        return "synthetic-database-result"

    async def caller():
        return operator.run_async(value)

    assert asyncio.run(caller()) == "synthetic-database-result"


def test_pending_receipt_is_durable_before_writes_and_never_blindly_replaced(
    tmp_path, monkeypatch
):
    repo = tmp_path / "repository"
    repo.mkdir()
    monkeypatch.setattr(operator, "ROOT", repo)
    protected = tmp_path / "protected"
    protected.mkdir(mode=0o700)
    # ACL enforcement is separately tested using the actual Windows custody API.
    if operator.os.name == "nt":
        from types import SimpleNamespace

        monkeypatch.setattr(
            operator.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0)
        )
    output = protected / "binding.json"
    result = operator.reserve_receipt(output)
    assert json.loads(output.read_text())["account_creation"] == "NOT_ATTEMPTED"
    with pytest.raises(ValueError):
        operator.reserve_receipt(output)
    result["account_creation"] = "ATTEMPTED_CHECK_REQUIRED"
    operator.persist_receipt(output, result)
    assert (
        json.loads(output.read_text())["account_creation"] == "ATTEMPTED_CHECK_REQUIRED"
    )
    result.update(account_creation="CONFIRMED", operator_user_id="synthetic-private-id")
    operator.persist_receipt(output, result)
    assert json.loads(output.read_text())["operator_user_id"] == "synthetic-private-id"
    assert list(protected.iterdir()) == [output]


def test_receipt_acl_rejection_happens_before_any_outcome_file_or_write(
    tmp_path, monkeypatch
):
    if operator.os.name != "nt":
        pytest.skip("native Windows ACL rejection")
    from types import SimpleNamespace

    monkeypatch.setattr(operator, "ROOT", tmp_path / "repository")
    monkeypatch.setattr(
        operator.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=1)
    )
    with pytest.raises(ValueError, match="PROTECTED_RECEIPT"):
        operator.reserve_receipt(tmp_path / "binding.json")
    assert not (tmp_path / "binding.json").exists()


@pytest.mark.parametrize(
    "change",
    [
        "none",
        "extra-user",
        "extra-role",
        "coach",
        "contact",
        "calendar",
        "schema",
        "migration",
    ],
)
def test_postflight_only_allows_exact_one_admin_and_no_business_scope_expansion(change):
    tables = (
        "portal_users",
        "user_roles",
        "auth_password_credentials",
        "auth_totp_credentials",
        "auth_recovery_codes",
        "coaches",
        "company_contacts",
        "calendar_offers",
        "roles",
        "audit_events",
    )
    baseline = {
        "migrations": ["0001", "0002", "0003", "0004", "0005", "0006"],
        "row_counts": {"competence_hub." + t: 0 for t in tables},
    }
    baseline["row_counts"]["competence_hub.roles"] = 5
    state = deepcopy(baseline)
    state.update(enrolled=True, recovery_count=10, roles=["admin"])
    for table in tables[:5]:
        state["row_counts"]["competence_hub." + table] = (
            10 if table == "auth_recovery_codes" else 1
        )
    if change == "extra-user":
        state["row_counts"]["competence_hub.portal_users"] = 2
    elif change == "extra-role":
        state["row_counts"]["competence_hub.user_roles"] = 2
    elif change == "coach":
        state["row_counts"]["competence_hub.coaches"] = 1
    elif change == "contact":
        state["row_counts"]["competence_hub.company_contacts"] = 1
    elif change == "calendar":
        state["row_counts"]["competence_hub.calendar_offers"] = 1
    elif change == "schema":
        state["row_counts"]["competence_hub.new_table"] = 0
    elif change == "migration":
        state["migrations"].append("0007")
    if change == "none":
        operator.verify_postconditions(baseline, state)
    else:
        with pytest.raises(ValueError):
            operator.verify_postconditions(baseline, state)
