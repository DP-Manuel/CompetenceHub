"""Pure preparation policy. No Registry adapter, DB credentials or APPLY path."""

import argparse
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class Qualification:
    canonical_label: str
    public: bool
    public_display: str | None
    evidence_reference: str | None = None
    verification_state: str = "SOURCE_ASSERTED"

    def public_projection(self):
        if type(self.public) is not bool:
            raise ValueError("public requires an actual boolean")
        if not self.canonical_label.strip():
            raise ValueError("canonical qualification label required")
        if self.verification_state not in {
            "UNKNOWN",
            "SOURCE_ASSERTED",
            "PRIOR_REVIEW_RECORDED",
            "VERIFIED",
        }:
            raise ValueError("unknown verification state")
        if not self.public:
            return None
        if not self.public_display or not self.public_display.strip():
            raise ValueError("explicit public display required")
        # Verification and source references are administration, never public copy.
        return {"label": self.public_display}


@dataclass(frozen=True)
class Evidence:
    subject_type: str
    subject_key: str
    environment: str
    status: str
    reference: str | None
    historical_date: date | None = None
    historical_at: datetime | None = None
    approved_by: str | None = None

    def permits(self, subject_type, subject_key, environment):
        if self.subject_type not in {
            "profile",
            "portrait",
            "offering",
            "publication",
            "person_consent",
        }:
            raise ValueError("unknown evidence subject")
        if self.environment not in {"preview", "production"}:
            raise ValueError("explicit environment required")
        if self.status not in {"APPROVED", "UNKNOWN", "BLOCKED", "NOT_REQUIRED"}:
            raise ValueError("unknown evidence status")
        if self.historical_at and self.historical_at.tzinfo is None:
            raise ValueError("timestamp without timezone")
        return (
            self.status == "APPROVED"
            and bool(self.reference)
            and (self.subject_type, self.subject_key, self.environment)
            == (subject_type, subject_key, environment)
        )


def validate_offering(
    kind, service_domains, *, bookable, source_status, detail_fields=None
):
    domains = set(service_domains)
    if not domains <= {
        "coaching",
        "consulting",
        "psychotherapy",
        "training",
        "moderation",
        "health_promotion",
    }:
        raise ValueError("unknown domain")
    if "psychotherapy" in domains and (kind == "coaching" or bookable):
        raise ValueError("psychotherapy is not a bookable Coaching offer")
    if source_status == "SOURCE_REPLACEMENT_REQUIRED" and detail_fields is not None:
        raise ValueError("unread source cannot supply invented details")
    if source_status not in {"READY", "SOURCE_REPLACEMENT_REQUIRED"}:
        raise ValueError("unknown source status")
    if source_status == "READY" and kind not in {
        "lecture",
        "workshop",
        "coaching",
        "individual",
        "other",
    }:
        # Psychotherapy requires a separately implemented domain/format contract.
        if domains != {"psychotherapy"}:
            raise ValueError("unknown format")


CURRENT_GAPS = {
    "public_roles": "needs_model_extension",
    "profile_sections": "needs_model_extension",
    "teaser_focus": "needs_model_extension",
    "scoped_evidence": "needs_model_extension",
    "qualifications": "needs_model_extension",
    "languages": "needs_model_extension",
    "quote": "needs_model_extension",
    "external_links": "needs_model_extension",
    "psychotherapy_domain": "needs_model_extension",
    "offering_families": "needs_model_extension",
}


SOURCE_FIELDS = frozenset(
    {
        "kind",
        "name",
        "role",
        "previewRole",
        "focus",
        "topics",
        "text",
        "profilePath",
        "image",
        "imageWidth",
        "imageHeight",
        "initials",
        "source_identity",
        "profile_path",
        "template",
        "template_sha256",
        "asset",
        "credentials",
        "topic_cards",
        "sections",
        "quotes",
        "dynamic_text_expressions",
        "external_links",
        "offerings",
    }
)


def field_loss(fields, supported=()):
    private = {
        "private_contacts",
        "certificate_numbers",
        "original_documents",
        "verification_notes",
        "unconfirmed_pricing",
    }
    presentation = {"image_dimensions", "initials"}
    return [
        {
            "field": field,
            "classification": (
                "intentionally_excluded_private_data"
                if field in private
                else (
                    "harmless_presentation_only"
                    if field in presentation
                    else CURRENT_GAPS.get(field, "manual_decision")
                )
            ),
        }
        for field in sorted(set(fields) - set(supported))
    ]


def prepare(canonical, review):
    """Deterministic in-memory mapping only. Return plans, not DB entities/UUIDs."""
    if (
        canonical["mode"] != "READ_ONLY_CANONICAL_NO_DB"
        or review["scope"] != "PREPARATION_ONLY_NO_DATABASE_OR_PUBLICATION"
    ):
        raise ValueError("preparation scope required")
    output = []
    topics = {t["id"]: t for t in canonical["topics"]}
    if len(topics) != 8 or {c["id"] for c in canonical["categories"]} != {
        "personalentwicklung",
        "persoenlichkeitsentwicklung",
        "karrierecoaching",
    }:
        raise ValueError("canonical taxonomy changed")
    seen = set()
    identities = set()
    for source in canonical["coaches"]:
        if set(source) - SOURCE_FIELDS:
            raise ValueError("FIELD_LOSS: unclassified source fields")
        slug = source["profilePath"].split("/")[-1]
        if slug in seen:
            raise ValueError("duplicate source identity")
        seen.add(slug)
        identity = (
            source["source_identity"]["source_system"],
            source["source_identity"]["source_key"],
        )
        if identity in identities:
            raise ValueError("duplicate technical source identity")
        identities.add(identity)
        decisions = review["coaches"][slug]
        if len(source["credentials"]) != len(decisions["credential_kinds"]):
            raise ValueError("credential mapping changed")
        kinds = set(decisions["credential_kinds"])
        if not kinds <= {
            "qualification",
            "competency",
            "background",
            "languages",
            "role_descriptor",
            "format_description",
        }:
            raise ValueError("unclassified credential field")
        fields = {"public_roles", "profile_sections", "teaser_focus", "scoped_evidence"}
        credentials = []
        for i, (label, kind) in enumerate(
            zip(source["credentials"], decisions["credential_kinds"]), 1
        ):
            row = {
                "key": f"credential/{i}",
                "source_label": label,
                "classification": kind,
                "canonical_label": label,
                "public": True,
                "public_display": label,
                "evidence_reference": source["template"],
                "verification_state": (
                    "PRIOR_REVIEW_RECORDED"
                    if slug == "susanne-klemm"
                    else "SOURCE_ASSERTED"
                ),
            }
            credentials.append(row)
        if "qualification" in kinds:
            fields.add("qualifications")
        if "languages" in kinds:
            fields.add("languages")
        if source["quotes"]:
            fields.add("quote")
        if source["external_links"]:
            fields.add("external_links")
        offers = deepcopy(source["offerings"])
        for offer in offers:
            if offer["service_domain"] == "psychotherapy":
                fields.add("psychotherapy_domain")
                validate_offering(
                    offer["kind"],
                    ["psychotherapy"],
                    bookable=False,
                    source_status="READY",
                )
            offer.update(
                publication_scope="preview",
                project_evidence="APPROVED_EXISTING_TITLE_ONLY",
                registry_evidence_binding="REVIEW_REQUIRED",
                bookable=False,
            )
        if slug == "guelcan-elmas-brandes":
            fields.add("offering_families")
        if any(t not in topics for t in source["topics"]):
            raise ValueError("unknown canonical topic")
        categories = sorted(
            {c for t in source["topics"] for c in topics[t]["categories"]}
        )
        has_asset = source["asset"] is not None
        project_evidence = decisions["project_evidence"]
        if set(project_evidence) != {
            "profile",
            "portrait",
            "preview",
            "production",
        } or any(
            v not in {"APPROVED", "UNKNOWN", "BLOCKED", "NOT_REQUIRED"}
            for v in project_evidence.values()
        ):
            raise ValueError("explicit subject evidence required")
        if has_asset and project_evidence["portrait"] == "NOT_REQUIRED":
            raise ValueError(
                "an existing asset still requires its own evidence decision"
            )
        evidence = {
            "profile_content": project_evidence["profile"],
            "portrait": project_evidence["portrait"],
            "preview": project_evidence["preview"],
            "production": project_evidence["production"],
            "historical_person_consent": "UNKNOWN",
            "registry_subject_binding": "REVIEW_REQUIRED",
            "approval_reference": "docs/content/coach-publication-matrix-2026-09-24.md",
            "approved_by": "Manuel",
            "preview_approval_date": (
                "2026-10-23" if slug == "susanne-klemm" else "2026-10-21"
            ),
            "historical_at": None,
            "date_precision": "DAY",
            "scope_confirmation_date": decisions.get("scope_confirmation_date"),
            "scope_confirmation_reference": decisions.get(
                "scope_confirmation_reference"
            ),
        }
        output.append(
            {
                "source_identity": source["source_identity"],
                "coach_uuid": None,
                "display_name": source["name"],
                "profile_path": source["profile_path"],
                "template": source["template"],
                "source_role": source["role"],
                "roles": decisions["roles"],
                "credential_matrix": credentials,
                "topics": source["topics"],
                "categories": categories,
                "focus_labels": source["focus"],
                "competencies": [
                    r["source_label"]
                    for r in credentials
                    if r["classification"] == "competency"
                ],
                "offerings": offers,
                "asset": (
                    None
                    if not has_asset
                    else {
                        **source["asset"],
                        "canonical_item_key": "asset/portrait",
                        "mapping_status": "READY",
                    }
                ),
                "evidence": evidence,
                "field_loss": field_loss(fields),
                "mapping_status": "BLOCKED",
                "mapping_fact_status": "READY",
                "public_projection_candidate": {
                    "qualifications": [
                        Qualification(
                            r["canonical_label"],
                            True,
                            r["public_display"],
                            r["evidence_reference"],
                            r["verification_state"],
                        ).public_projection()
                        for r in credentials
                        if r["classification"] == "qualification"
                    ]
                },
                "intentionally_excluded": review["private_exclusions"],
                "background_note": decisions["background_note"],
            }
        )
    if seen != set(review["coaches"]):
        raise ValueError("coach inventory changed")
    families = deepcopy(review["new_offering_families"])
    for family in families:
        if any(
            family.get(key) == "APPROVED"
            for key in ("offering_content_approval", "public_copy_approval")
        ):
            if (
                not family.get("approval_reference")
                or not family.get("publication_scopes")
                or not set(family["publication_scopes"]) <= {"preview", "production"}
            ):
                raise ValueError("explicit approved copy scope and reference required")
        if (
            "mediation" in family["service_domains"]
            or "supervision" in family["service_domains"]
        ):
            raise ValueError("forbidden inferred profession/domain")
        for fmt in family["formats"]:
            validate_offering(
                fmt["kind"],
                family["service_domains"],
                bookable=False,
                source_status=fmt["source_status"],
                detail_fields=fmt.get("detail_fields"),
            )
    reviews = [
        {
            "key": "person-consent/" + c["source_identity"]["source_key"],
            "kind": "PERSON_CONSENT_ATTESTATION",
        }
        for c in output
    ]
    for family in families:
        if family.get("public_copy_approval") != "APPROVED":
            reviews.append(
                {
                    "key": "public-copy/" + family["key"],
                    "kind": "COPYRIGHT_PUBLIC_COPY_APPROVAL",
                }
            )
        if family.get("offering_content_approval") != "APPROVED":
            reviews.extend(
                {
                    "key": "offering-content/" + f["key"],
                    "kind": "OFFERING_CONTENT_APPROVAL",
                }
                for f in family["formats"]
            )
    reviews.extend(
        {"key": "replacement/" + s["key"], "kind": "SOURCE_REPLACEMENT_REQUIRED"}
        for s in review["source_quality"]
        if s["status"] != "READY"
    )
    reviews.extend(
        [
            {"key": "delivery/business-balance", "kind": "LIVE_MODE_UNSPECIFIED"},
            {
                "key": "scope/susanne-scan-notes",
                "kind": "NEW_NOTES_NOT_CANONICAL_KEEP_EXISTING_OFFERS",
            },
        ]
    )
    counts = {
        "coaches_to_create": len(output),
        "existing_coaches_to_match": 0,
        "profile_revisions": len(output),
        "canonical_topic_lookups": len(topics),
        "topics_to_create_in_import": 0,
        "topic_links": sum(len(c["topics"]) for c in output),
        "competency_links": sum(len(c["competencies"]) for c in output),
        "public_qualification_records": sum(
            sum(r["classification"] == "qualification" for r in c["credential_matrix"])
            for c in output
        ),
        "offerings": sum(len(c["offerings"]) for c in output),
        "assets": sum(c["asset"] is not None for c in output),
        "preview_publications": 0,
        "production_publications": 0,
        "unknown_person_consent": sum(
            c["evidence"]["historical_person_consent"] == "UNKNOWN" for c in output
        ),
        "unknown_production_scope": sum(
            c["evidence"]["production"] == "UNKNOWN" for c in output
        ),
        "new_offering_families_held": len(families),
        "new_offering_formats_held": sum(len(f["formats"]) for f in families),
        "source_replacements_required": sum(
            s["status"] == "SOURCE_REPLACEMENT_REQUIRED"
            for s in review["source_quality"]
        ),
        "manual_review_subjects": len(reviews),
    }
    return {
        "schema": 1,
        "mode": "VALIDATE_DRY_MAPPING_NO_DATABASE",
        "database_snapshot": "NOT_READ",
        "go_no_go": "NO_GO_APPLY",
        "counts_conditional_on_approved_empty_target": counts,
        "mapping_status_counts": {
            s: sum(c["mapping_status"] == s for c in output)
            for s in ("READY", "REVIEW_REQUIRED", "BLOCKED")
        },
        "mapping_fact_status_counts": {"READY": len(output)},
        "coaches": output,
        "new_offering_families": families,
        "source_quality": review["source_quality"],
        "scan_review": review["scan_review"],
        "manual_reviews": reviews,
        "technical_gates": [
            "IMPLEMENT_AND_TEST_LOSSLESS_TARGET_CONTRACT",
            "APPROVE_TOPIC_UUID_MAPPING",
            "BIND_SUBJECT_EVIDENCE",
            "CHOOSE_AND_APPROVE_TARGET_MIGRATIONS_BACKUP_ROLLBACK",
        ],
        "actions": {
            "WOULD_CREATE_IF_GATES_PASS": len(output),
            "WOULD_MATCH_CANONICAL_TOPICS": len(topics),
            "WOULD_LINK_EDITORIAL_TOPICS": counts["topic_links"],
            "WOULD_SKIP_PORTRAIT": len(output) - counts["assets"],
            "REVIEW_REQUIRED_PERSON_CONSENT": counts["unknown_person_consent"],
            "BLOCKED_CURRENT_TARGET": len(output),
        },
        "business_mutations": 0,
        "publication_side_effects": 0,
    }


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate fixed canonical preparation inputs; never APPLY",
    )
    parser.parse_args()
    raw = (root / ".tmp/coach3b-canonical-inputs-2026-10-29.json").read_bytes()
    review = json.loads(
        (root / "scripts/coach3b-review-map.json").read_text(encoding="utf-8")
    )
    if hashlib.sha256(raw).hexdigest() != review["source_snapshot_sha256"]:
        raise ValueError(
            "canonical input changed; consolidated mapping review required"
        )
    result = prepare(json.loads(raw), review)
    output = root / ".tmp/coach3b-dry-mapping-2026-10-29.json"
    output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "validation": "PASS",
                "go_no_go": result["go_no_go"],
                "mapping_status_counts": result["mapping_status_counts"],
                "conditional_counts": result[
                    "counts_conditional_on_approved_empty_target"
                ],
                "business_mutations": 0,
                "report_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            }
        )
    )


if __name__ == "__main__":
    main()
