"""Offline local/SMB evidence only; no network path used or credentials created."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "backup_destination_contract", ROOT / "deploy/scripts/backup_destination_contract.py"
)
contract = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = contract
spec.loader.exec_module(contract)
NOW = datetime(2026, 11, 4, 12, tzinfo=UTC)


def fixture(kind="local"):
    # Synthetic lexical examples only, never configured or connected targets.
    path = r"C:\synthetic-only\backup" if kind == "local" else r"\\synthetic.invalid\backup\synthetic-only"
    target = contract.DestinationSpec(kind, path, approved=True)
    proof = contract.DestinationEvidence(
        target_sha256=target.validate(), collected_at=NOW,
        free_bytes=2 * 1024**3, required_bytes=1024**3,
        **{field: True for field in contract.DestinationEvidence.__dataclass_fields__
           if field.endswith(("_verified", "_approved", "_only", "_overlap", "_reviewed"))},
    )
    return target, proof


@pytest.mark.parametrize("kind", ["local", "smb"])
def test_complete_plan_is_not_copy_or_actual_restore_acceptance(kind):
    target, proof = fixture(kind)
    result = contract.evaluate_destination_plan(target, proof, now=NOW)
    assert result["transfer_executed"] is False
    assert result["credentials_created"] is False
    assert result["actual_database_restore"] == "PENDING_SEPARATE_GATE"
    assert result["status"] == "PLAN_EVIDENCE_COMPLETE_NOT_RUNTIME_ACCEPTANCE"


@pytest.mark.parametrize("field", [
    "permissions_verified", "at_rest_encryption_verified", "retention_approved",
    "ciphertext_only", "exclusive_copy_and_sha256_verified",
    "destination_probe_roundtrip_verified", "restore_procedure_reviewed",
    "no_repo_or_reparse_overlap", "existing_smb_identity_only",
    "smb3_or_later_verified", "smb_encryption_verified", "smb_signing_verified",
])
def test_each_missing_smb_gate_blocks_even_with_capacity(field):
    target, proof = fixture("smb")
    with pytest.raises(contract.DestinationStop):
        contract.evaluate_destination_plan(target, replace(proof, **{field: False}), now=NOW)


@pytest.mark.parametrize("change", ["unapproved", "wrong-target", "expired", "future", "capacity", "mapped-local"])
def test_evidence_must_bind_current_approved_target(change):
    target, proof = fixture()
    if change == "unapproved":
        target = replace(target, approved=False)
    elif change == "wrong-target":
        proof = replace(proof, target_sha256="0" * 64)
    elif change == "expired":
        proof = replace(proof, collected_at=NOW - timedelta(hours=2))
    elif change == "future":
        proof = replace(proof, collected_at=NOW + timedelta(seconds=1))
    elif change == "capacity":
        proof = replace(proof, free_bytes=1)
    else:
        proof = replace(proof, fixed_local_volume_verified=False)
    with pytest.raises(contract.DestinationStop):
        contract.evaluate_destination_plan(target, proof, now=NOW)


@pytest.mark.parametrize("path", [
    "", r"C:\\", "C:relative", r"\\synthetic.invalid\share",
    r"\\?\C:\backup", r"C:\a\..\b", r"C:\backup:stream", r"C:\backup\*",
])
def test_ambiguous_roots_devices_or_streams_are_not_destinations(path):
    with pytest.raises(contract.DestinationStop):
        contract.DestinationSpec("local", path).validate()
