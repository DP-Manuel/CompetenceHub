"""Tamper-evident COACH-3B manifest and pure existing-topic v2 binding.

Only the explicit public-asset loader reads files. No database, network, actor
or UUID-allocation interface lives here; builder/binder/parity checks are pure.
Manifests contain private review material and must not be committed.
"""

from copy import deepcopy
import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

import coach3b_review_closure as closure
from competence_hub_api.portal.coach_import import (
    CoachTargetImportRecord,
    ImportMappingContract,
    TopicRule,
    normalized_input,
    topic_token,
    validate_records,
)
from competence_hub_api.portal.coach_registry import ProfileContent, TopicSnapshot
from competence_hub_api.portal.coach_target import subjects

APPROVED_REVIEW_SHA256 = (
    "7d79a9d1b91d959459e2c3a525a6c5763024dc15656c6f5890dfc89562dd0f59"
)
EXPECTED_COUNTS = {
    "coaches": 9,
    "profile_revisions": 9,
    "topic_links": 22,
    "competencies": 14,
    "public_qualifications": 30,
    "offering_families": 3,
    "offering_formats": 30,
    "variants_add_ons": 5,
    "assets": 8,
    "object_evidence_records": 120,
    "current_attestation_records": 30,
    "canonical_topic_lookups": 8,
    "preview_publications": 9,
    "production_publications": 3,
    "unintended_field_loss": 0,
}
TARGET = {
    "database": "competence_hub_staging",
    "schema": "competence_hub",
    "environment": "staging",
    "import_contract": "coach-import-v2",
}
REVIEW_COLLECTIONS = {"coaches", "topic_rules", "counts_conditional_on_empty_target"}
PUBLIC_ASSET_SOURCES = {
    "images/coaches/christian-galvano.webp": "apps/website/public/images/coaches/christian-galvano.webp",
    "images/coaches/manuela-rodriguez.webp": "apps/website/public/images/coaches/manuela-rodriguez.webp",
    **{
        "images/coaches/" + filename: "apps/website/src/preview/portraits/" + filename
        for filename in (
            "elisabeth-schwabauer.webp",
            "guelcan-elmas-brandes.png",
            "wegner-ney.jpg",
            "goran-celic.png",
            "stefanie-becker.webp",
            "susanne-klemm.webp",
        )
    },
}


@dataclass(frozen=True)
class RuntimeTopicSnapshot(TopicSnapshot):
    """Adapter supplies the actual active flag; ordinary snapshots lack proof."""

    active: bool


def _utc(value, field):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"{field} must be a timezone-aware datetime") from error
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{field} must be a timezone-aware datetime")
    return value.astimezone(UTC)


def build_manifest(report, *, git_commit, generated_at) -> dict:
    """Seal only the exact reviewed closure; timestamps are technical, not consent."""
    report = deepcopy(report)
    if closure.digest(report) != APPROVED_REVIEW_SHA256:
        raise ValueError("report does not match the exact approved review hash")
    if report["mapping_status_counts"] != {
        "READY": 9,
        "REVIEW_REQUIRED": 0,
        "BLOCKED": 0,
    } or any(
        report["counts_conditional_on_empty_target"].get(key) != value
        for key, value in EXPECTED_COUNTS.items()
    ):
        raise ValueError("approved review counts changed")
    if not isinstance(git_commit, str) or not re.fullmatch(r"[a-f0-9]{40}", git_commit):
        raise ValueError("git_commit must be a full lowercase Git commit hash")
    payload = {
        "coaches": report["coaches"],
        "topic_rules": report["topic_rules"],
        "counts": report["counts_conditional_on_empty_target"],
        "review_context": {
            key: value for key, value in report.items() if key not in REVIEW_COLLECTIONS
        },
    }
    manifest = {
        "schema": "coach3b-real-manifest-v1",
        "approval": "EXACT_REVIEWED_COACH_3B_PHASE_A_ONLY",
        "target": dict(TARGET),
        "review_report_sha256": APPROVED_REVIEW_SHA256,
        "reviewed_payload_sha256": closure.digest(payload),
        **payload,
        "technical": {
            "git_commit": git_commit,
            "generated_at": _utc(generated_at, "generated_at").isoformat(),
        },
    }
    manifest["manifest_sha256"] = closure.digest(manifest)
    return manifest


def verify_manifest(manifest) -> None:
    """Reconstruct pinned business input, not merely a caller-resealable digest."""
    try:
        report = {
            **manifest["review_context"],
            "coaches": manifest["coaches"],
            "topic_rules": manifest["topic_rules"],
            "counts_conditional_on_empty_target": manifest["counts"],
        }
        expected = build_manifest(report, **manifest["technical"])
        if manifest != expected:
            raise ValueError("manifest digest or content binding changed")
    except (KeyError, TypeError) as error:
        raise ValueError("invalid manifest structure") from error


def bind_manifest(manifest, catalogue: list[TopicSnapshot], asset_bytes, *, now):
    """Return validated v2 record dictionaries and contract, without persistence.

    Catalogue entries must carry explicit ``active=True`` (RuntimeTopicSnapshot).
    Assets are supplied in memory as reference -> bytes. No implicit file reads.
    The publication intent concerns Registry states only, not external deployment.
    """
    manifest = deepcopy(manifest)
    verify_manifest(manifest)
    return _bind_review(
        manifest,
        catalogue,
        asset_bytes,
        now=now,
    )


def load_asset_bytes(root, manifest) -> dict[str, bytes]:
    """Read only the eight frozen public/preview portrait sources, after approval."""
    manifest = deepcopy(manifest)
    verify_manifest(manifest)
    return _load_assets(root, manifest["coaches"])


def verify_local_inputs(root, manifest):
    """Recheck frozen public sources/review docs, without rereading Quellen."""
    verify_manifest(manifest)
    root = Path(root).resolve()
    raw = (root / ".tmp/coach3b-canonical-inputs-2026-10-29.json").read_bytes()
    review_raw = (root / "scripts/coach3b-review-map.json").read_bytes()
    if (
        hashlib.sha256(raw).hexdigest() != closure.SOURCE_HASH
        or hashlib.sha256(review_raw).hexdigest() != closure.REVIEW_HASH
    ):
        raise ValueError("frozen input bytes changed")
    canonical = json.loads(raw)
    closure.verify_public_files(root, canonical)
    documents = {
        path: hashlib.sha256((root / path).read_bytes()).hexdigest()
        for path in closure.DOCUMENT_HASHES
    }
    report = closure.close_review(canonical, json.loads(review_raw), documents)
    if closure.digest(report) != manifest["review_report_sha256"]:
        raise ValueError("local inputs differ from reviewed manifest")


def _load_assets(root, rows):
    root = Path(root).resolve()
    result = {}
    for row in rows:
        for asset in row["content"]["assets"]:
            reference = asset["reference"]
            relative = PUBLIC_ASSET_SOURCES.get(reference)
            if relative is None:
                raise ValueError("asset is not an approved frozen public source")
            path = root / relative
            if path.resolve() != path or not path.resolve().is_relative_to(root):
                raise ValueError(
                    "asset source may not traverse links or leave repository"
                )
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != asset["sha256"]:
                raise ValueError("frozen public asset hash mismatch")
            if reference in result and result[reference] != raw:
                raise ValueError("conflicting asset source")
            result[reference] = raw
    return result


def verify_projection_parity(manifest, preview, production) -> None:
    """Require exact semantic public DTO parity, with no publication side effects."""
    manifest = deepcopy(manifest)
    verify_manifest(manifest)
    _verify_projection_rows(manifest, preview, production)


def _semantic_projection(value, field=""):
    if isinstance(value, dict):
        return {key: _semantic_projection(item, key) for key, item in value.items()}
    if isinstance(value, list):
        items = [_semantic_projection(item) for item in value]
        if field in {"categories", "service_domains", "excluded_services"}:
            return sorted(items)
        if field in {"topics", "coaches"}:
            return sorted(items, key=closure.digest)
        return items
    return value


def _verify_projection_rows(logical, preview, production):
    """Synthetic semantic policy seam; not a real approval or public export."""
    for environment, actual in (("preview", preview), ("production", production)):
        expected = {
            "schema": 1,
            "environment": environment,
            "coaches": [
                row["projection_" + environment]
                for row in logical["coaches"]
                if row["projection_" + environment] is not None
            ],
        }
        # The importer owns whitespace normalization; semantic set order and
        # topic UUID ordering must not invent a public-content discrepancy.
        expected = _semantic_projection(normalized_input(expected))
        if closure.digest(_semantic_projection(actual)) != closure.digest(expected):
            raise ValueError(environment + " public projection parity mismatch")


def _topic_contract(logical_rules, catalogue):
    if len(logical_rules) != 8:
        raise ValueError("exactly eight logical topic rules required")
    ids = [topic.id for topic in catalogue]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate catalogue topic UUID")
    rules, seen_references, seen_ids = [], set(), set()
    for logical in logical_rules:
        # Token matching is the existing curated alias rule, never fuzzy matching.
        matches = [
            topic
            for topic in catalogue
            if topic_token(topic.name) == topic_token(logical["name"])
        ]
        if len(matches) != 1:
            raise ValueError("absent or ambiguous existing topic name")
        topic = matches[0]
        if getattr(topic, "active", None) is not True:
            raise ValueError("inactive topic or missing explicit active status")
        if sorted(topic.categories) != sorted(logical["categories"]):
            raise ValueError("existing topic categories mismatch")
        if logical["reference"] in seen_references or topic.id in seen_ids:
            raise ValueError("ambiguous logical topic mapping")
        if (
            logical.get("resolution")
            != "MATCH_ONLY_AT_APPROVED_PREFLIGHT_NO_UUID_ASSIGNED"
        ):
            raise ValueError("MATCH_ONLY logical topic resolution required")
        seen_references.add(logical["reference"])
        seen_ids.add(topic.id)
        rules.append(
            TopicRule(
                reference=logical["reference"],
                topic_id=topic.id,
                accepted_labels=tuple(logical["accepted_labels"]),
                categories=tuple(logical["categories"]),
            )
        )
    return ImportMappingContract(
        version="coach-import-v2",
        topics=tuple(rules),
        review_ref="project:coach3b-reviewed-closure",
        attest_initial_publication=True,
    )


def _record(row):
    content = deepcopy(row["content"])
    if row["candidate_content_sha256"] != closure.digest(content):
        raise ValueError("logical content hash mismatch")
    if row["mapping_status"] != "READY" or row["remaining_reviews"]:
        raise ValueError("logical review is not ready")
    if content["topic_ids"]:
        raise ValueError("logical review must not contain executable topic UUIDs")
    ProfileContent.model_validate(content)
    sections = {}
    for source, target in (
        ("public_roles", "roles"),
        ("qualifications", "qualifications"),
        ("offering_families", "offering_families"),
        ("presentation", "presentation"),
        ("boundaries", "boundaries"),
    ):
        sections[target] = content.pop(source)
    for field in ("competencies", "target_groups"):
        # These source collections have no object keys. Retain their source order
        # using zero-padded positional keys, not title-derived or random identity.
        sections[field] = [
            {"key": f"{field}/{index:03d}", "text": text}
            for index, text in enumerate(content.pop(field), 1)
        ]
    sections["offerings"] = [
        {"key": offer["key"], "content": offer} for offer in content.pop("offerings")
    ]
    sections["assets"] = [
        {"key": "asset/portrait", "content": asset} for asset in content.pop("assets")
    ]
    published = [
        environment
        for environment in ("preview", "production")
        if row["rights"][environment] == "APPROVED"
    ]
    evidence = []
    for attestation in row["attestation_plan"]:
        kind = attestation["kind"]
        evidence.append(
            {
                "key": "attestation/" + kind,
                "kind": kind,
                "environment": kind if kind in {"preview", "production"} else None,
                "source": attestation["reference"],
                "historical_at": attestation["historical_at"],
            }
        )
    return {
        "source_identity": deepcopy(row["source_identity"]),
        "profile": content,
        **sections,
        "topics": [
            {"reference": topic["reference"], "label": topic["name"]}
            for topic in row["topics"]
        ],
        "publication": {
            "lifecycle": "active",
            "published": published,
            "evidence": evidence,
        },
        "provenance": {"source_ref": "project:coach3b-reviewed-closure"},
        "object_evidence": [],
    }


def _validated(records, contract, catalogue, asset_bytes, now):
    result = validate_records(records, contract, catalogue, asset_bytes, now=now)
    if result.issues:
        fields = sorted({issue.code + ":" + issue.field for issue in result.issues})
        raise ValueError("v2 validation failed: " + ", ".join(fields))
    return result.records


def _bind_review(logical, catalogue, asset_bytes, *, now):
    """Policy-only test seam. Does not verify/issue any real-import approval.

    Only bind_manifest is the approved operator entry point. No synthetic APPLY
    helper or importer guard is invoked or bypassed here.
    """
    now = _utc(now, "now")
    contract = _topic_contract(logical["topic_rules"], catalogue)
    catalogue = {topic.id: topic for topic in catalogue}
    rows = logical["coaches"]
    records = [_record(row) for row in rows]
    # First normalize and map using the real validator without publication intent
    # or candidate evidence. Only then calculate actual runtime subject hashes.
    drafts = deepcopy(records)
    for draft in drafts:
        draft["publication"] = {}
    prepared = _validated(drafts, contract, catalogue, asset_bytes, now)
    for row, record, mapped in zip(rows, records, prepared):
        hashes = subjects(
            mapped.content, [catalogue[id] for id in mapped.content.topic_ids]
        )
        for planned in row["evidence_plan"]:
            evidence = {
                key: deepcopy(value)
                for key, value in planned.items()
                if key not in {"candidate_subject_sha256", "binding_stage", "basis"}
            }
            evidence["subject_hash"] = hashes[
                evidence["subject_type"], evidence["subject_key"]
            ]
            record["object_evidence"].append(evidence)
    final = _validated(records, contract, catalogue, asset_bytes, now)
    # Return the exact normalized typed inputs validated by v2, not the drafts.
    return [
        CoachTargetImportRecord.model_validate(item.source.model_dump()).model_dump(
            mode="json"
        )
        for item in final
    ], contract


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve()
    if not output.is_relative_to(root / ".tmp") or output.exists():
        parser.error("new output inside ignored .tmp required; no overwrite")
    raw = (root / ".tmp/coach3b-canonical-inputs-2026-10-29.json").read_bytes()
    review_raw = (root / "scripts/coach3b-review-map.json").read_bytes()
    if (
        hashlib.sha256(raw).hexdigest() != closure.SOURCE_HASH
        or hashlib.sha256(review_raw).hexdigest() != closure.REVIEW_HASH
    ):
        raise ValueError("frozen input bytes changed")
    canonical = json.loads(raw)
    closure.verify_public_files(root, canonical)
    documents = {
        path: hashlib.sha256((root / path).read_bytes()).hexdigest()
        for path in closure.DOCUMENT_HASHES
    }
    report = closure.close_review(canonical, json.loads(review_raw), documents)
    git_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    manifest = build_manifest(
        report, git_commit=git_commit, generated_at=datetime.now(UTC)
    )
    load_asset_bytes(root, manifest)
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    data = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2).encode()
    with output.open("xb") as handle:
        handle.write(data)
    print(
        json.dumps(
            {
                "result": "PASS",
                "mode": "PHASE_A_OFFLINE_ONLY",
                "manifest_sha256": hashlib.sha256(data).hexdigest(),
                "review_report_sha256": APPROVED_REVIEW_SHA256,
                "source_commit": git_commit,
                "counts": manifest["counts"],
                "database": "NOT_READ",
                "uuid_allocation": False,
                "business_mutations": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
