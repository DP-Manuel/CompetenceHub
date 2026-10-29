"""Pure business-review closure; no DB, UUID allocation or real APPLY interface."""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import coach3b_preparation as preparation
from competence_hub_api.portal.coach_import import topic_token
from competence_hub_api.portal.coach_registry import ProfileContent
from competence_hub_api.portal.coach_target import (
    ObjectEvidenceInput,
    digest,
    public_offering,
    public_target,
    requirements,
    subjects,
)

SOURCE_HASH = "e3feda67b2bdb681b080e2336d82fd9c9eb39128735f2955c47773fed5e743a9"
REVIEW_HASH = "19c8c1cc0a8c1688729dd3ebcfeab7076fe032dd9bed684d9ace4cee16ebb497"
CANONICAL_PAYLOAD_HASH = (
    "88852911f1a9c48f4e29edab51718e97a5e27e05c632c986793f2b763a348e61"
)
REVIEW_PAYLOAD_HASH = "fff805aef8012bbeee3f27dc3bf0c16e2c131c99de6467adbea1e7da0e9d9657"
MATRIX = "docs/content/coach-publication-matrix-2026-09-24.md"
SUSANNE = "docs/content/susanne-klemm-preview-2026-10-23.md"
DOCUMENT_HASHES = {
    MATRIX: "5274b7fa14edb54ce9a9d9eb7075ff14e990514f31548a1172eb7eb3f0e81414",
    SUSANNE: "9677ad60ced152f8dd1c5fe540e03ea49a5f403dd0c0cb16c970f5e8595e0f73",
}
# Approved scope summaries from Manuel's current review-closure instruction,
# not copied concepts, exercises, prices, or invented replacement-file details.
BOUNDARIES = {
    "family/business-balance": "Coaching und Training, keine Therapie, ärztliche oder psychotherapeutische Behandlung, Rechtsberatung oder Steuerberatung.",
    "family/gesundheit-im-unternehmensalltag": "Gesundheitsförderung und Training, keine ärztliche Behandlung, Psychotherapie, Heilbehandlung, Diagnostik oder individuelle Ernährungstherapie.",
    "family/konfliktklaerung-teamreflexion": "Coaching und Moderation, keine Mediation, Supervision, Rechtsberatung oder rechtsverbindliche Streitbeilegung.",
}
GROUPS = {
    "vortraege": "Vorträge",
    "workshops": "Workshops",
    "individuell": "Individuelle Angebote",
    "weitere": "Coaching / weitere Angebote",
}
OPTIONAL_FAMILY_FIELDS = {
    "excluded_services_public_text",
    "module_labels",
    "source_replacement_and_format_review",
    "standalone_or_extension",
    "delivery_location",
}


def taxonomy(canonical):
    result, tokens = [], {}
    for topic in canonical["topics"]:
        aliases = [topic["id"], topic["label"]]
        for alias in aliases:
            token = topic_token(alias)
            if token in tokens and tokens[token] != topic["id"]:
                raise ValueError("ambiguous canonical topic alias")
            tokens[token] = topic["id"]
        result.append(
            {
                "reference": topic["id"],
                "name": topic["label"],
                "categories": sorted(topic["categories"]),
                "accepted_labels": aliases,
                "resolution": "MATCH_ONLY_AT_APPROVED_PREFLIGHT_NO_UUID_ASSIGNED",
            }
        )
    return result


def completed_content(source, decisions, families, catalogue):
    original, issues = preparation.target_candidate(
        source, decisions, families, catalogue
    )
    value = original.model_dump(mode="json")
    for asset in value["assets"]:
        asset["scopes"] = (
            ["preview", "production"]
            if decisions["project_evidence"]["production"] == "APPROVED"
            else ["preview"]
        )
    unknown = []
    for family, source_family in zip(value["offering_families"], families):
        family.update(
            active=True,
            boundaries=[
                {
                    "key": "scope",
                    "text": BOUNDARIES[source_family["key"]],
                    "excluded_services": source_family["excluded_services"],
                }
            ],
        )
        for offer in value["offerings"]:
            if offer["family_key"] == family["key"]:
                offer["active"] = True
                unknown.append(
                    {
                        "subject_key": offer["key"],
                        "fields": "unconfirmed_details",
                        "status": "UNKNOWN_NOT_IMPORTED",
                    }
                )
        unknown.extend(
            {
                "subject_key": family["key"],
                "fields": field,
                "status": "UNKNOWN_NOT_IMPORTED",
            }
            for field in (
                "module_labels",
                "standalone_or_extension",
                "unconfirmed_live_location",
            )
            if (field == "module_labels" and source_family.get("module_count"))
            or (
                field != "module_labels"
                and any(
                    f.get("standalone_or_extension")
                    or f.get("delivery_mode") == "LIVE_UNSPECIFIED_OR_ONLINE"
                    for f in source_family["formats"]
                )
            )
        )
    # Editorial source groups are presentation, not new commercial families.
    # Inactive therapy stays visible only in its separate nonbookable source context.
    for key in dict.fromkeys(
        o.get("source_group") for o in source["offerings"] if o.get("source_group")
    ):
        if key not in GROUPS:
            raise ValueError("unreviewed catalogue display group")
        value["presentation"]["sections"].append(
            {
                "key": "catalogue-group/" + key,
                "kind": "formats",
                "headings": [GROUPS[key]],
                "paragraphs": [
                    o["title"]
                    for o in source["offerings"]
                    if o.get("source_group") == key
                ],
            }
        )
    content = ProfileContent.model_validate(value)
    remaining = []
    known_subjects = {f["key"] for f in families} | {
        o["key"] for f in families for o in f["formats"]
    }
    for issue in issues:
        if issue == "topics/approved_uuid_mapping":
            continue  # Business references are approved; no database UUID is guessed.
        if issue.startswith("offerings/") and issue.endswith("/source_group_display"):
            continue
        if issue.startswith("review_families/"):
            subject, field = issue[len("review_families/") :].rsplit("/", 1)
            if subject in known_subjects and field in OPTIONAL_FAMILY_FIELDS:
                continue
        remaining.append(issue)
    for family in families:
        if (
            family.get("public_copy_approval") != "APPROVED"
            or family.get("offering_content_approval") != "APPROVED"
        ):
            remaining.append("family_short_copy_scope/" + family["key"])
        if not {"preview", "production"} <= set(family.get("publication_scopes", [])):
            remaining.append("family_environment_scope/" + family["key"])
    return content, remaining, unknown


def approval_basis(slug, environment, document_hashes):
    document = SUSANNE if slug == "susanne-klemm" else MATRIX
    day = "2026-10-23" if slug == "susanne-klemm" else "2026-10-21"
    if slug == "guelcan-elmas-brandes":
        day = "2026-10-29"
    if environment == "production":
        day = {
            "manuela-rodriguez": "2026-09-24",
            "guelcan-elmas-brandes": "2026-10-29",
        }.get(slug)
    return {
        "document": document,
        "document_sha256": document_hashes[document],
        "approved_by": "Manuel",
        "approved_on": day,
        "basis": "DOCUMENTED_PROJECT_APPROVAL_NOT_PERSONAL_SIGNATURE",
        "original_personal_consent_at": None,
        "original_personal_consent_by": None,
    }


def evidence_plan(content, topic_bindings, slug, decisions, documents):
    hashes = subjects(content)
    # This is intentionally NOT an executable runtime profile hash: real topic
    # UUIDs/revision/operator/time are still unknown until the approved window.
    hashes["profile", "profile"] = digest(
        {
            "logical_content": content.model_dump(mode="json"),
            "canonical_topics": topic_bindings,
        }
    )
    required = requirements(content) | {
        ("offering", o.key, "offering_content") for o in content.offerings
    }
    result, attestations = [], []
    for env, state in (
        ("preview", decisions["project_evidence"]["preview"]),
        ("production", decisions["project_evidence"]["production"]),
    ):
        if state != "APPROVED":
            continue
        basis = approval_basis(slug, env, documents)
        for subject_type, key, kind in sorted(required):
            evidence = ObjectEvidenceInput(
                key=f"{env}/{subject_type}/{key}/{kind}",
                subject_type=subject_type,
                subject_key=key,
                subject_hash=hashes[subject_type, key],
                kind=kind,
                environment=env,
                status="approved",
                evidence_reference="project:coach3b-reviewed-approval",
                approved_by=basis["approved_by"],
                approved_on=basis["approved_on"],
            )
            row = evidence.model_dump(mode="json")
            row["candidate_subject_sha256"] = row.pop("subject_hash")
            row.update(
                binding_stage="LOGICAL_REVIEW_ONLY_REBIND_AT_APPROVED_APPLY",
                **{"basis": basis},
            )
            result.append(row)
        attestations.append(
            {"kind": env, "reference": basis["document"], "historical_at": None}
        )
    if result:
        attestations[:0] = [
            {
                "kind": kind,
                "reference": MATRIX if slug != "susanne-klemm" else SUSANNE,
                "historical_at": None,
                "meaning": "CURRENT_OPERATOR_ATTESTATION_OF_DOCUMENTED_PROJECT_RIGHTS",
            }
            for kind in ("content_review", "person_consent")
        ]
    return result, attestations


def dry_projection(content, topic_bindings, environment):
    result = content.model_dump(
        mode="json",
        include={
            "display_name",
            "academic_suffix",
            "short_intro",
            "description",
            "professional_background",
            "target_groups",
            "profile_path",
            "competencies",
        },
    )
    result.update(public_target(content, environment))
    result["topics"] = [
        {"name": t["name"], "categories": t["categories"]} for t in topic_bindings
    ]
    result["assets"] = [
        a.model_dump(mode="json", include={"type", "reference", "sha256", "alt_text"})
        for a in content.assets
        if a.active and environment in a.scopes
    ]
    result["offerings"] = [
        public_offering(o)
        for o in sorted(content.offerings, key=lambda v: v.ordering)
        if o.active and not o.family_key
    ]
    return result


def parity(source, decisions, content, catalogue):
    audit = preparation.source_target_audit(source, decisions, content, catalogue)
    changes = [row for row in audit if row["classification"] == "unmapped_or_changed"]
    public = dry_projection(
        content,
        [
            {
                "name": catalogue[r]["label"],
                "categories": sorted(catalogue[r]["categories"]),
            }
            for r in source["topics"]
        ],
        "preview",
    )
    text = json.dumps(public, ensure_ascii=False)
    for offer in source["offerings"]:
        if offer["title"] not in text:
            changes.append(
                {
                    "field": "public_offering/" + offer["key"],
                    "classification": "missing_public_title",
                }
            )
    public_labels = {q["label"] for q in public["qualifications"]}
    for index, label in enumerate(source["credentials"]):
        if (
            decisions["credential_kinds"][index] == "qualification"
            and label not in public_labels
        ):
            changes.append(
                {
                    "field": "public_qualification/credential/" + str(index + 1),
                    "classification": "missing_public_label",
                }
            )
    expected_roles = [
        {"code": r["canonical"], "label": r["display"]} for r in decisions["roles"]
    ]
    if public["roles"] != expected_roles:
        changes.append(
            {"field": "public_roles", "classification": "changed_public_role"}
        )
    if source["asset"] and not any(
        a["reference"] == source["asset"]["reference"]
        and a["sha256"] == source["asset"]["sha256"]
        for a in public["assets"]
    ):
        changes.append(
            {"field": "public_portrait", "classification": "missing_public_asset"}
        )
    return {
        "status": "PASS" if not changes else "FAIL",
        "source_leaf_audit": audit,
        "unintended_changes": changes,
        "kind": "SEMANTIC_DTO_PARITY_NOT_RENDERED_WEBSITE_ACCEPTANCE",
    }


def close_review(canonical, review, document_hashes):
    """Only the actually inspected frozen inputs can receive this approval GO."""
    if document_hashes != DOCUMENT_HASHES:
        raise ValueError("documentary evidence changed; inspect scope before rebinding")
    if (
        digest(canonical) != CANONICAL_PAYLOAD_HASH
        or digest(review) != REVIEW_PAYLOAD_HASH
    ):
        raise ValueError(
            "canonical/review provenance changed; current approval does not bind this input"
        )
    report = _evaluate_review(canonical, review, document_hashes)
    report["mode"] = "REVIEW_CLOSURE_VALIDATE_DRY_MAPPING_NO_DATABASE"
    report["verified_input_binding"] = {
        "canonical_payload_sha256": CANONICAL_PAYLOAD_HASH,
        "review_payload_sha256": REVIEW_PAYLOAD_HASH,
    }
    if report["go_no_go"] == "POLICY_EVALUATION_ONLY_NO_APPROVAL":
        report["go_no_go"] = "GO_FOR_COACH_3B_APPLY_PENDING_SEPARATE_APPROVAL"
    return report


def _evaluate_review(canonical, review, document_hashes):
    """Pure policy evaluation for tests; never issues the frozen real-input GO."""
    if document_hashes != DOCUMENT_HASHES:
        raise ValueError("documentary evidence changed; inspect scope before rebinding")
    owners = {s["source_identity"]["source_key"] for s in canonical["coaches"]}
    families = review["new_offering_families"]
    if any(f["coach_key"] not in owners for f in families) or len(
        {f["key"] for f in families}
    ) != len(families):
        raise ValueError("unmatched or duplicate offering family ownership")
    baseline = preparation.prepare_target(canonical, review)
    catalogue = {t["id"]: t for t in canonical["topics"]}
    topic_rules = taxonomy(canonical)
    by_ref = {t["reference"]: t for t in topic_rules}
    rows = []
    for source, previous in zip(canonical["coaches"], baseline["coaches"]):
        slug = source["profilePath"].split("/")[-1]
        decisions = review["coaches"][slug]
        families = [
            f
            for f in review["new_offering_families"]
            if f["coach_key"] == source["source_identity"]["source_key"]
        ]
        content, remaining, unknown = completed_content(
            source, decisions, families, catalogue
        )
        bindings = [by_ref[ref] for ref in source["topics"]]
        rights = decisions["project_evidence"]
        if rights["profile"] != "APPROVED" or rights["preview"] != "APPROVED":
            remaining.append("documented_preview_profile_scope")
        if content.assets and rights["portrait"] != "APPROVED":
            remaining.append("documented_portrait_scope")
        checked = parity(source, decisions, content, catalogue)
        status = (
            "BLOCKED"
            if checked["status"] != "PASS"
            else "REVIEW_REQUIRED" if remaining else "READY"
        )
        evidence, attestations = (
            evidence_plan(content, bindings, slug, decisions, document_hashes)
            if status == "READY"
            else ([], [])
        )
        rows.append(
            {
                "source_identity": deepcopy(source["source_identity"]),
                "display_name": content.display_name,
                "profile_path": content.profile_path,
                "mapping_status": status,
                "topics": bindings,
                "content": content.model_dump(mode="json"),
                "candidate_content_sha256": digest(content.model_dump(mode="json")),
                "evidence_plan": evidence,
                "attestation_plan": attestations,
                "rights": deepcopy(rights),
                "remaining_reviews": remaining,
                "optional_unknowns": unknown,
                "replacement_sources": (
                    "OPTIONAL_FOR_APPROVED_SHORT_COPY" if families else "NOT_APPLICABLE"
                ),
                "parity": checked,
                "projection_preview": dry_projection(content, bindings, "preview"),
                "projection_production": (
                    dry_projection(content, bindings, "production")
                    if rights["production"] == "APPROVED"
                    else None
                ),
                "qualifications_display_heading": "Qualifikationen & beruflicher Hintergrund",
            }
        )
    counts = {
        "coaches": len(rows),
        "profile_revisions": len(rows),
        "would_match_existing_coaches": 0,
        "canonical_topic_lookups": len(topic_rules),
        "topic_category_links": sum(len(t["categories"]) for t in topic_rules),
        "topic_links": sum(len(r["topics"]) for r in rows),
        "competencies": sum(len(r["content"]["competencies"]) for r in rows),
        "public_qualifications": sum(
            q["public"] for r in rows for q in r["content"]["qualifications"]
        ),
        "internal_qualifications": sum(
            not q["public"] for r in rows for q in r["content"]["qualifications"]
        ),
        "roles": sum(len(r["content"]["public_roles"]) for r in rows),
        "offering_families": sum(len(r["content"]["offering_families"]) for r in rows),
        "offering_formats": sum(len(r["content"]["offerings"]) for r in rows),
        "active_formats": sum(
            o["active"] for r in rows for o in r["content"]["offerings"]
        ),
        "variants_add_ons": sum(
            len(f["variants"]) for r in rows for f in r["content"]["offering_families"]
        ),
        "assets": sum(len(r["content"]["assets"]) for r in rows),
        "preview_publications": sum(
            r["mapping_status"] == "READY" and r["rights"]["preview"] == "APPROVED"
            for r in rows
        ),
        "production_publications": sum(
            r["mapping_status"] == "READY" and r["rights"]["production"] == "APPROVED"
            for r in rows
        ),
        "production_scope_unknown": sum(
            r["rights"]["production"] == "UNKNOWN" for r in rows
        ),
        "object_evidence_records": sum(len(r["evidence_plan"]) for r in rows),
        "current_attestation_records": sum(len(r["attestation_plan"]) for r in rows),
        "unintended_field_loss": sum(
            len(r["parity"]["unintended_changes"]) for r in rows
        ),
    }
    counts["internal_only_domain_evidence_records"] = (
        counts["object_evidence_records"] + counts["current_attestation_records"]
    )
    statuses = {
        s: sum(r["mapping_status"] == s for r in rows)
        for s in ("READY", "REVIEW_REQUIRED", "BLOCKED")
    }
    return {
        "schema": 1,
        "mode": "REVIEW_POLICY_EVALUATION_NOT_APPROVAL",
        "source_snapshot_sha256": review["source_snapshot_sha256"],
        "documentary_evidence": document_hashes,
        "mapping_status_counts": statuses,
        "counts_conditional_on_empty_target": counts,
        "coaches": rows,
        "topic_rules": topic_rules,
        "all_topics": "COMPUTED_NOT_STORED",
        "would_keep_internal": {
            "evidence_records": counts["internal_only_domain_evidence_records"],
            "private_exclusion_classes": review["private_exclusions"],
            "prices": "INTERNAL_UNCONFIRMED_NOT_IMPORTED",
            "protected_workshop_content": "EXCLUDED_NOT_IMPORTED",
            "new_susanne_scan_ideas": "EXCLUDED_NOT_CANONICAL",
        },
        "would_skip": {
            "missing_portrait": sum(not r["content"]["assets"] for r in rows),
            "replacement_file_details": sum(
                s["status"] == "SOURCE_REPLACEMENT_REQUIRED"
                for s in review["source_quality"]
            ),
            "unconfirmed_price_records": 0,
        },
        "business_mutations": 0,
        "database_snapshot": "NOT_READ",
        "uuid_allocation": False,
        "runtime_binding": "PENDING_APPROVED_EXECUTION_AND_EXACT_TOPIC_REVISION_HASH_VERIFICATION",
        "decisions_required_from_manuel": [
            {
                "coach": r["source_identity"]["source_key"],
                "fields": r["remaining_reviews"],
            }
            for r in rows
            if r["remaining_reviews"]
        ],
        "go_no_go": (
            "NO_GO"
            if statuses["BLOCKED"]
            else (
                "CONDITIONAL_NO_GO"
                if statuses["REVIEW_REQUIRED"]
                else "POLICY_EVALUATION_ONLY_NO_APPROVAL"
            )
        ),
    }


def verify_public_files(root, canonical):
    references = [(d["path"], d["sha256"]) for d in canonical["dependencies"]]
    references += [(c["template"], c["template_sha256"]) for c in canonical["coaches"]]
    references += [
        (c["asset"]["source"], c["asset"]["sha256"])
        for c in canonical["coaches"]
        if c["asset"]
    ]
    for path, expected in references:
        target = (root / path).resolve()
        if not (
            target.is_relative_to(root / "apps/website") or path in DOCUMENT_HASHES
        ):
            raise ValueError("only frozen public files are eligible")
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError(
                "current public source differs from frozen review snapshot"
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if not args.validate:
        parser.error("explicit --validate required; no APPLY option exists")
    root = Path(__file__).resolve().parents[1]
    raw = (root / ".tmp/coach3b-canonical-inputs-2026-10-29.json").read_bytes()
    review_raw = (root / "scripts/coach3b-review-map.json").read_bytes()
    if (
        hashlib.sha256(raw).hexdigest() != SOURCE_HASH
        or hashlib.sha256(review_raw).hexdigest() != REVIEW_HASH
    ):
        raise ValueError("frozen canonical input/review mapping changed")
    documents = {
        p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in DOCUMENT_HASHES
    }
    canonical = json.loads(raw)
    verify_public_files(root, canonical)
    report = close_review(canonical, json.loads(review_raw), documents)
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "mode",
                    "mapping_status_counts",
                    "counts_conditional_on_empty_target",
                    "go_no_go",
                    "business_mutations",
                    "database_snapshot",
                    "uuid_allocation",
                    "decisions_required_from_manuel",
                )
            }
            | {"report_sha256": digest(report)},
            ensure_ascii=False,
        )
    )
    return (
        0
        if not report["counts_conditional_on_empty_target"]["unintended_field_loss"]
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
