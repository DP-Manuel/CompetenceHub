"""Offline reviewed-input simulation, not consent, DB import or deployed parity.

Reads only the exact previously sealed local review manifest. All UUIDs and
technical attestations below are disposable in-memory simulation identities.
Never use these aggregates as import records or as evidence for real APPLY.
"""

import argparse
from copy import deepcopy
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
from uuid import UUID

from coach3b_real_manifest import verify_manifest
from competence_hub_api.portal.coach_import import normalized_input
from competence_hub_api.portal.coach_projection import (
    canonical_bytes,
    checked_local_path,
    generate_projection,
    projection_parity,
    validate_projection,
)
from competence_hub_api.portal.coach_registry import (
    Approval,
    CoachAggregate,
    ObjectEvidence,
    ProfileContent,
    ProfileRevision,
    Publication,
    TopicSnapshot,
)
from competence_hub_api.portal.coach_target import (
    ObjectEvidenceInput,
    requirements,
    subjects,
)

MANIFEST_SHA256 = "872b4df0610ae54ceec1688f323e4d99001befd87d7a3d2395a0001fc82c02fc"
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".tmp/coach3b-real-2026-10-30/manifest.json"
NOW = datetime(2026, 11, 2, tzinfo=UTC)


def simulate_reviewed_rows(rows, environment):
    """Pure test seam. Simulated consent does not become real approval."""
    coaches, expected = [], []
    actor = UUID(int=90000)
    for index, row in enumerate(rows, 1):
        content = ProfileContent.model_validate(
            normalized_input(deepcopy(row["content"]))
        )
        topics = tuple(
            TopicSnapshot(
                UUID(int=50000 + index * 50 + j), t["name"], tuple(t["categories"])
            )
            for j, t in enumerate(row["topics"])
        )
        revision = ProfileRevision(
            UUID(int=10000 + index),
            1,
            content,
            actor,
            NOW,
            status="submitted",
            topics=topics,
        )
        coach = CoachAggregate(
            UUID(int=index),
            content.display_name,
            UUID(int=20000 + index),
            lifecycle="active",
            revisions=[revision],
        )
        approved = row["projection_" + environment] is not None
        if approved:
            revision.approvals = [
                Approval(k, actor, NOW, "synthetic:simulation-only")
                for k in ("content_review", "person_consent", environment)
            ]
            hashes = subjects(content, topics)
            revision.object_evidence = [
                ObjectEvidence(
                    UUID(int=100000 + index * 1000 + j),
                    ObjectEvidenceInput(
                        key=f"simulation-{j}",
                        subject_type=t,
                        subject_key=k,
                        subject_hash=hashes[t, k],
                        kind=kind,
                        environment=environment,
                        status="approved",
                        evidence_reference="synthetic:simulation-only",
                    ),
                    actor,
                    NOW,
                )
                for j, (t, k, kind) in enumerate(sorted(requirements(content)))
            ]
            coach.publications[environment] = Publication(
                revision.id, "published", actor, NOW
            )
            expected.append(
                normalized_input(deepcopy(row["projection_" + environment]))
            )
        coaches.append(coach)
    frozen = {
        "schema": 1,
        "environment": environment,
        "coaches": sorted(expected, key=lambda c: c["profile_path"]),
    }
    for coach in frozen["coaches"]:
        for topic in coach["topics"]:
            topic["categories"].sort()
        coach["topics"].sort(key=lambda t: (t["name"], t["categories"]))
    validate_projection(frozen)
    generated = generate_projection(coaches, environment)
    return projection_parity(frozen, generated), generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    args.output_directory = checked_local_path(
        args.output_directory, root=ROOT / ".tmp/coach4"
    )
    body = MANIFEST.read_bytes()
    if hashlib.sha256(body).hexdigest() != MANIFEST_SHA256:
        raise ValueError("frozen local review manifest changed")
    manifest = json.loads(body)
    verify_manifest(manifest)
    # Exclusive directory avoids overwriting either review or prior proof.
    args.output_directory.mkdir(parents=True, exist_ok=False)
    result = {
        "scope": "OFFLINE_SYNTHETIC_IDENTITIES_NOT_REAL_REGISTRY_OR_LIVE_WEBSITE",
        "manifest_sha256": MANIFEST_SHA256,
        "environments": {},
    }
    for environment in ("preview", "production"):
        report, generated = simulate_reviewed_rows(manifest["coaches"], environment)
        (args.output_directory / (environment + ".json")).write_bytes(
            canonical_bytes(generated)
        )
        result["environments"][environment] = {
            "status": report["status"],
            "checks": report["checks"],
            "coaches": len(generated["coaches"]),
            "sha256": hashlib.sha256(canonical_bytes(generated)).hexdigest(),
        }
    (args.output_directory / "parity.json").write_bytes(canonical_bytes(result))
    print(json.dumps(result, sort_keys=True))
    return (
        0 if all(v["status"] == "PASS" for v in result["environments"].values()) else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
