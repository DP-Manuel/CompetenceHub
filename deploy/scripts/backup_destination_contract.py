"""Offline destination adapter contract, not a copier or approval/probe substitute.

No default path, credentials, filesystem access or network connection. A complete
plan must still be revalidated by the separately approved runtime copy/restore.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
from pathlib import PureWindowsPath


class DestinationStop(ValueError):
    """Fixed codes only; never echo paths, shares, account names or evidence."""


@dataclass(frozen=True)
class DestinationSpec:
    kind: str
    path: str
    approved: bool = False

    def validate(self):
        if type(self.path) is not str or not self.path or len(self.path) > 240:
            raise DestinationStop("explicit_destination_required")
        if (
            any(ord(char) < 32 for char in self.path)
            or any(char in self.path for char in "*?<>|\"")
            or self.path.startswith(("\\\\?\\", "\\\\.\\"))
            or "/" in self.path
            or any(part in (".", "..") or part.endswith((" ", ".")) for part in self.path.split("\\"))
        ):
            raise DestinationStop("unsafe_destination_path")
        path = PureWindowsPath(self.path)
        if not path.is_absolute() or path == PureWindowsPath(path.anchor):
            raise DestinationStop("dedicated_absolute_directory_required")
        if any(PureWindowsPath(part).is_reserved() for part in path.parts[1:]):
            raise DestinationStop("reserved_destination_component")
        if self.kind == "local":
            if not path.drive or len(path.drive) != 2 or path.drive[1] != ":" or ":" in self.path[2:]:
                raise DestinationStop("fixed_local_path_required")
        elif self.kind == "smb":
            if not path.drive.startswith("\\\\") or ":" in self.path:
                raise DestinationStop("explicit_smb_share_required")
        else:
            raise DestinationStop("unsupported_destination_kind")
        return hashlib.sha256(self.path.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DestinationEvidence:
    target_sha256: str
    collected_at: datetime
    free_bytes: int
    required_bytes: int
    permissions_verified: bool = False
    at_rest_encryption_verified: bool = False
    retention_approved: bool = False
    ciphertext_only: bool = False
    exclusive_copy_and_sha256_verified: bool = False
    destination_probe_roundtrip_verified: bool = False
    restore_procedure_reviewed: bool = False
    no_repo_or_reparse_overlap: bool = False
    fixed_local_volume_verified: bool = False
    existing_smb_identity_only: bool = False
    smb3_or_later_verified: bool = False
    smb_encryption_verified: bool = False
    smb_signing_verified: bool = False


def evaluate_destination_plan(
    spec: DestinationSpec, evidence: DestinationEvidence, *, now: datetime
) -> dict:
    token = spec.validate()
    if spec.approved is not True:
        raise DestinationStop("destination_not_approved")
    if evidence.target_sha256 != token:
        raise DestinationStop("destination_evidence_binding_mismatch")
    if (
        not isinstance(evidence.collected_at, datetime)
        or not isinstance(now, datetime)
        or evidence.collected_at.tzinfo is None
        or now.tzinfo is None
        or not 0 <= (now.astimezone(UTC) - evidence.collected_at.astimezone(UTC)).total_seconds() <= 3600
    ):
        raise DestinationStop("current_destination_evidence_required")
    if (
        type(evidence.free_bytes) is not int
        or type(evidence.required_bytes) is not int
        or evidence.required_bytes < 512 * 1024**2
        or evidence.free_bytes < evidence.required_bytes
    ):
        raise DestinationStop("destination_capacity_not_proven")
    required = (
        "permissions_verified", "at_rest_encryption_verified", "retention_approved",
        "ciphertext_only", "exclusive_copy_and_sha256_verified",
        "destination_probe_roundtrip_verified", "restore_procedure_reviewed",
        "no_repo_or_reparse_overlap",
    )
    required += (
        ("fixed_local_volume_verified",) if spec.kind == "local" else
        ("existing_smb_identity_only", "smb3_or_later_verified",
         "smb_encryption_verified", "smb_signing_verified")
    )
    if any(getattr(evidence, name) is not True for name in required):
        raise DestinationStop("destination_protection_or_recovery_gate_open")
    return {
        "status": "PLAN_EVIDENCE_COMPLETE_NOT_RUNTIME_ACCEPTANCE",
        "kind": spec.kind,
        "target_sha256": token,
        "credentials_created": False,
        "transfer_executed": False,
        "actual_database_restore": "PENDING_SEPARATE_GATE",
    }
