"""Pure preparation policy. No Registry adapter, DB credentials or APPLY path."""

import argparse
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re


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


SECTION_KINDS = {
    "coach-profile-hero": "profile",
    "coach-profile-section": "topics",
    "coach-credentials": "background",
    "coach-format-band": "formats",
    "coach-profile-section coach-profile-section--pending": "pending",
    "notice-panel": "boundary",
    "showcase-strip coach-profile-cta": "contact",
}


def target_links(values):
    links, issues = [], []
    for index, value in enumerate(values):
        if set(value) != {"kind", "target", "label"}:
            issues.append(f"external_links/{index}/unclassified_fields")
            continue
        if value["kind"] == "quoted":
            preview = production = value["target"]
        elif value["kind"] == "expression":
            match = re.fullmatch(
                r'import\.meta\.env\.PUBLIC_REVIEW_MODE === "true"\s*\?\s*"([^"\r\n]+)"\s*:\s*"([^"\r\n]+)"',
                value["target"],
            )
            if not match:
                issues.append(f"external_links/{index}/unresolved_expression")
                continue
            preview, production = match.groups()
        else:
            issues.append(f"external_links/{index}/unknown_kind")
            continue
        links.append(
            {
                "key": f"link/{index + 1}",
                "label": value["label"],
                "preview_url": preview,
                "production_url": production,
            }
        )
    return links, issues


def target_candidate(source, decisions, reviewed_families=(), topic_catalogue=None):
    """Construct the real target model, never a dict-shaped readiness assertion."""
    from competence_hub_api.portal.coach_registry import ProfileContent

    issues = []
    sections = []
    for section in source.get("sections", []):
        kind = SECTION_KINDS.get(section["kind"])
        if kind is None or set(section) != {
            "source_key",
            "kind",
            "headings",
            "paragraphs",
        }:
            issues.append("sections/" + section["source_key"] + "/unclassified")
            continue
        sections.append(
            {
                "key": section["source_key"],
                "kind": kind,
                "headings": section["headings"],
                "paragraphs": section["paragraphs"],
            }
        )
    # The index's compound role is public literal copy, not an additional role code.
    sections.append(
        {"key": "index-role", "kind": "profile", "paragraphs": [source["role"]]}
    )
    links, link_issues = target_links(source.get("external_links", []))
    issues.extend(link_issues)
    rows = list(zip(source["credentials"], decisions["credential_kinds"]))
    qualifications = [
        {
            "key": f"credential/{index + 1}",
            "canonical_title": label,
            "public_display_label": label,
            "public": True,
            "ordering": index,
            "verification_state": "source_asserted",
            "evidence_reference": source["template"],
            "internal_note": (
                "Prior project review recorded; no new certificate verification asserted."
                if source["source_identity"]["source_key"] == "coach/susanne-klemm"
                else None
            ),
        }
        for index, (label, kind) in enumerate(rows)
        if kind == "qualification"
    ]
    offerings = []
    for index, offer in enumerate(source["offerings"]):
        if set(offer) - {
            "key",
            "title",
            "source_group",
            "kind",
            "service_domain",
            "active",
        }:
            issues.append("offerings/" + offer["key"] + "/unclassified")
        therapy = offer["service_domain"] == "psychotherapy"
        offerings.append(
            {
                "key": offer["key"],
                "title": offer["title"],
                "type": "other" if therapy and offer["kind"] is None else offer["kind"],
                "active": offer["active"],
                "ordering": index,
                "bookable": False,
                "service_domains": (
                    [offer["service_domain"]] if offer["service_domain"] else []
                ),
            }
        )
    families = []
    for ordering, family in enumerate(reviewed_families):
        options = [
            {
                "key": option["key"],
                "kind": (
                    "add_on" if option["kind"] == "optional_add_on" else option["kind"]
                ),
                "title": option["label"],
                "ordering": index,
                "duration": (
                    {"minutes": option["duration_minutes"]}
                    if option.get("duration_minutes")
                    else None
                ),
            }
            for index, option in enumerate(family["options"])
        ]
        families.append(
            {
                "key": family["key"],
                "title": family["title"],
                "description": family.get("subtitle"),
                "ordering": ordering,
                "active": False,
                "service_domains": family["service_domains"],
                "target_groups": [family["target_group"]],
                "target_focus": (
                    [family["target_focus"]]
                    if family.get("target_focus")
                    else family.get("core_areas", [])
                ),
                "variants": options,
                "protected_source_reference": family["boundary_ref"],
            }
        )
        # Codes/reference are confirmed, but this snapshot has no exact boundary copy.
        # Do not invent public prose to make the field-loss report green.
        issues.append(
            "review_families/" + family["key"] + "/excluded_services_public_text"
        )
        if family.get("module_count"):
            issues.append("review_families/" + family["key"] + "/module_labels")
        for fmt in family["formats"]:
            duration = {
                name: fmt[name]
                for name in ("weeks", "sessions_per_week", "session_minutes")
                if name in fmt
            }
            if fmt.get("clock_window"):
                duration["clock_start"], duration["clock_end"] = fmt[
                    "clock_window"
                ].split("-")
            if fmt.get("duration_minutes"):
                duration["minutes"] = fmt["duration_minutes"]
            delivery = {
                "IN_PERSON": "in_person",
                "LIVE_UNSPECIFIED_OR_ONLINE": "live_unspecified",
            }.get(fmt.get("delivery_mode"), "unknown")
            offerings.append(
                {
                    "key": fmt["key"],
                    "family_key": family["key"],
                    "title": fmt["label"],
                    "type": fmt["kind"] or "other",
                    "ordering": len(offerings),
                    "active": False,
                    "bookable": False,
                    "service_domains": family["service_domains"],
                    "duration": duration or None,
                    "delivery_mode": delivery,
                    "delivery_label": fmt.get(
                        "delivery_label", fmt.get("location_label")
                    ),
                    "protected_source_reference": fmt["confirmed_ref"],
                }
            )
            if fmt["source_status"] != "READY" or fmt["kind"] is None:
                issues.append(
                    "review_families/"
                    + fmt["key"]
                    + "/source_replacement_and_format_review"
                )
            if fmt.get("standalone_or_extension"):
                issues.append(
                    "review_families/" + fmt["key"] + "/standalone_or_extension"
                )
            if delivery == "live_unspecified":
                issues.append("review_families/" + fmt["key"] + "/delivery_location")
    asset = source["asset"]
    if asset and set(asset) - {"reference", "sha256", "alt_text", "source"}:
        issues.append("asset/unclassified")
    boundaries = [
        {"key": s["source_key"], "text": "\n\n".join(s["paragraphs"])}
        for s in source.get("sections", [])
        if s["kind"] == "notice-panel"
    ]
    focus_labels = list(source["focus"])
    for reference in source["topics"]:
        label = (topic_catalogue or {}).get(reference, {}).get("label")
        if label and label not in focus_labels:
            focus_labels.append(label)
    presentation = {
        "teaser": source.get("previewRole"),
        "focus_labels": focus_labels,
        "background_labels": [
            label
            for label, kind in rows
            if kind in {"background", "role_descriptor", "format_description"}
        ],
        "languages": [label for label, kind in rows if kind == "languages"],
        "sections": sections,
        "topic_cards": source.get("topic_cards", []),
        "quote": "\n\n".join(source.get("quotes", [])) or None,
        "external_links": links,
        "initials": source.get("initials"),
        "portrait_width": source.get("imageWidth"),
        "portrait_height": source.get("imageHeight"),
    }
    content = ProfileContent.model_validate(
        {
            "target_version": 1,
            "display_name": source["name"],
            "short_intro": source.get("text", source["name"]),
            "profile_path": source["profile_path"],
            "topic_ids": [],
            "public_roles": [
                {
                    "key": "role/" + r["canonical"],
                    "code": r["canonical"],
                    "display_label": r["display"],
                    "ordering": i,
                }
                for i, r in enumerate(decisions["roles"])
            ],
            "qualifications": qualifications,
            "competencies": [label for label, kind in rows if kind == "competency"],
            "offerings": offerings,
            "offering_families": families,
            "boundaries": boundaries,
            "presentation": presentation,
            "assets": (
                []
                if not asset
                else [
                    {
                        "reference": asset["reference"],
                        "sha256": asset["sha256"],
                        "alt_text": asset["alt_text"],
                        "scopes": ["preview"],
                    }
                ]
            ),
        }
    )
    if source["topics"]:
        issues.append("topics/approved_uuid_mapping")
    if source.get("image") and (not asset or source["image"] != asset["reference"]):
        issues.append("image/asset_reference_mismatch")
    if source["profile_path"] != "/" + source["profilePath"].strip("/") + "/":
        issues.append("profile_path/source_route_mismatch")
    # Expressions are inventory metadata, but unresolved ones must not disappear.
    known_expressions = {
        "topics.map((topic) => ( ))",
        "topic.title",
        "topic.text",
        "coach.role",
        "coach.name",
        "coach.text",
        "coach.previewRole",
        "qualifications.map((qualification) => )",
        "qualification",
        "workshops.map((workshop) => )",
        "workshop",
    }
    for index, value in enumerate(source.get("dynamic_text_expressions", [])):
        if (
            set(value) != {"expression", "line"}
            or value["expression"] not in known_expressions
        ):
            issues.append(f"dynamic_text_expressions/{index}/unresolved")
    return content, issues


def source_target_audit(source, decisions, content, topic_catalogue):
    """Prove each source leaf against the validated target or an explicit metadata rule."""
    p = content.presentation
    actual = {
        "name": content.display_name,
        "text": content.short_intro,
        "role": next(s.paragraphs[0] for s in p.sections if s.key == "index-role"),
        "previewRole": p.teaser,
        "focus": list(p.focus_labels[: len(source["focus"])]),
        "profile_path": content.profile_path,
        "image": content.assets[0].reference if content.assets else None,
        "imageWidth": p.portrait_width,
        "imageHeight": p.portrait_height,
        "initials": p.initials,
        "asset": (
            {
                k: getattr(content.assets[0], k)
                for k in ("reference", "sha256", "alt_text")
            }
            if content.assets
            else None
        ),
        "topic_cards": [v.model_dump(mode="json") for v in p.topic_cards],
        "quotes": (
            source["quotes"]
            if p.quote == ("\n\n".join(source["quotes"]) or None)
            else []
        ),
    }
    actual["topics"] = [
        ref if topic_catalogue.get(ref, {}).get("label") in p.focus_labels else None
        for ref in source["topics"]
    ]
    actual["credentials"] = []
    indexes = {"competency": 0, "languages": 0, "background": 0}
    for index, kind in enumerate(decisions["credential_kinds"]):
        if kind == "qualification":
            value = next(
                q.canonical_title
                for q in content.qualifications
                if q.key == f"credential/{index+1}"
            )
        else:
            category = kind if kind in {"competency", "languages"} else "background"
            values = {
                "competency": content.competencies,
                "languages": p.languages,
                "background": p.background_labels,
            }[category]
            value = values[indexes[category]]
            indexes[category] += 1
        actual["credentials"].append(value)
    actual["sections"] = []
    for value in source.get("sections", []):
        matches = [s for s in p.sections if s.key == value["source_key"]]
        if not matches:
            actual["sections"].append({})
            continue
        section = matches[0]
        actual["sections"].append(
            {
                "source_key": section.key,
                "kind": (
                    value["kind"]
                    if section.kind == SECTION_KINDS.get(value["kind"])
                    else None
                ),
                "headings": list(section.headings),
                "paragraphs": list(section.paragraphs),
            }
        )
    actual["external_links"] = []
    for index, value in enumerate(source.get("external_links", [])):
        expected, _ = target_links([value])
        matches = [link for link in p.external_links if link.key == f"link/{index+1}"]
        if expected and matches:
            link = matches[0]
            actual["external_links"].append(
                {
                    "label": link.label,
                    "target": (
                        value["target"]
                        if (link.preview_url, link.production_url)
                        == (expected[0]["preview_url"], expected[0]["production_url"])
                        else None
                    ),
                    "kind": value["kind"],
                }
            )
        else:
            actual["external_links"].append({})
    actual["offerings"] = []
    for value, offer in zip(source["offerings"], content.offerings):
        therapy = value["service_domain"] == "psychotherapy" and offer.type == "other"
        actual["offerings"].append(
            {
                "key": offer.key,
                "title": offer.title,
                "kind": None if therapy and value["kind"] is None else offer.type,
                "service_domain": (
                    offer.service_domains[0]
                    if len(offer.service_domains) == 1
                    else None
                ),
                "active": offer.active,
            }
        )

    def leaves(value, prefix=""):
        if isinstance(value, dict) and value:
            for key, child in value.items():
                yield from leaves(child, prefix + "/" + key if prefix else key)
        elif isinstance(value, list) and value:
            for index, child in enumerate(value):
                yield from leaves(child, prefix + "/" + str(index))
        else:
            yield prefix, value

    def metadata(path):
        if path in {
            "kind",
            "template",
            "template_sha256",
            "profilePath",
            "source_identity/source_system",
            "source_identity/source_key",
            "asset/source",
        }:
            return True
        if re.fullmatch(r"offerings/\d+/source_group", path):
            return True
        if path == "dynamic_text_expressions" and not source.get(
            "dynamic_text_expressions"
        ):
            return True
        if re.fullmatch(r"dynamic_text_expressions/\d+/(expression|line)", path):
            index = int(path.split("/")[1])
            return source["dynamic_text_expressions"][index]["expression"] in {
                "topics.map((topic) => ( ))",
                "topic.title",
                "topic.text",
                "coach.role",
                "coach.name",
                "coach.text",
                "coach.previewRole",
                "qualifications.map((qualification) => )",
                "qualification",
                "workshops.map((workshop) => )",
                "workshop",
            }
        return False

    actual_leaves = dict(leaves(actual))
    audit = []
    for path, value in leaves(source):
        classification = (
            "source_metadata"
            if metadata(path)
            else (
                "mapped_to_validated_target"
                if path in actual_leaves and actual_leaves[path] == value
                else "unmapped_or_changed"
            )
        )
        audit.append({"field": path, "classification": classification})
    # Topic references and their exact public labels are separate from DB UUIDs.
    for index, reference in enumerate(source["topics"]):
        label = topic_catalogue.get(reference, {}).get("label")
        audit.append(
            {
                "field": f"canonical_topic_labels/{index}",
                "classification": (
                    "mapped_to_validated_target"
                    if label and label in p.focus_labels
                    else "unmapped_or_changed"
                ),
            }
        )
    return audit


def prepare_target(canonical, review):
    """VALIDATE only: no DB, inferred UUIDs, file writes or publication effects."""
    from pydantic import ValidationError
    from competence_hub_api.portal.coach_target import public_target

    result = prepare(canonical, review)
    result["schema"] = 2
    result["mode"] = "VALIDATE_TARGET_V1_IN_MEMORY_NO_DATABASE"
    catalogue = {topic["id"]: topic for topic in canonical["topics"]}
    for source, record in zip(canonical["coaches"], result["coaches"]):
        slug = source["profilePath"].split("/")[-1]
        try:
            content, issues = target_candidate(
                source,
                review["coaches"][slug],
                [
                    f
                    for f in review["new_offering_families"]
                    if f.get("coach_key") == source["source_identity"]["source_key"]
                ],
                catalogue,
            )
        except ValidationError as error:
            record["target_validation"] = "FAIL"
            record["mapping_status"] = "BLOCKED"
            record["field_loss_status"] = "FAIL"
            record["source_field_audit"] = []
            record["field_loss"] = [
                {
                    "field": "/".join(map(str, e["loc"])),
                    "classification": "needs_model_extension",
                }
                for e in error.errors()
            ]
            continue
        record["target_validation"] = "PASS"
        record["target_content"] = content.model_dump(mode="json")
        record["target_content_sha256"] = hashlib.sha256(
            json.dumps(
                record["target_content"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        record["public_projection_candidate"] = public_target(content, "preview")
        record["source_field_audit"] = source_target_audit(
            source, review["coaches"][slug], content, catalogue
        )
        record["field_loss"] = [
            row
            for row in record["source_field_audit"]
            if row["classification"] == "unmapped_or_changed"
        ]
        record["field_loss_status"] = "FAIL" if record["field_loss"] else "PASS"
        record["mapping_reviews"] = [
            {"field": field, "classification": "manual_decision"} for field in issues
        ]
        record["mapping_status"] = (
            "BLOCKED" if record["field_loss"] else "REVIEW_REQUIRED"
        )
        record["evidence"]["registry_subject_binding"] = "REVIEW_REQUIRED"
        if record["asset"]:
            record["asset"]["mapping_status"] = "REVIEW_REQUIRED"
        record["evidence_scope_status"] = "REVIEW_REQUIRED"
        record["source_scope_status"] = "REVIEW_REQUIRED"
        record["object_evidence"] = []
    result["mapping_status_counts"] = {
        status: sum(c["mapping_status"] == status for c in result["coaches"])
        for status in ("READY", "REVIEW_REQUIRED", "BLOCKED")
    }
    result["target_validation_counts"] = {
        status: sum(c["target_validation"] == status for c in result["coaches"])
        for status in ("PASS", "FAIL")
    }
    result["field_loss_counts"] = {
        "unmapped_or_changed": sum(len(c["field_loss"]) for c in result["coaches"]),
        "audited_source_fields": sum(
            len(c["source_field_audit"]) for c in result["coaches"]
        ),
        "canonical_topic_labels_preserved": sum(
            sum(
                a["field"].startswith("canonical_topic_labels/")
                and a["classification"] == "mapped_to_validated_target"
                for a in c["source_field_audit"]
            )
            for c in result["coaches"]
        ),
    }
    result["field_loss_scope"] = "CANONICAL_PROFILE_SOURCE_FIELDS"
    result["review_family_field_gaps"] = sum(
        sum(
            r["field"].startswith("review_families/")
            for r in c.get("mapping_reviews", [])
        )
        for c in result["coaches"]
    )
    for family in result["new_offering_families"]:
        family["mapping_status"] = "REVIEW_REQUIRED"
        family["evidence_scope_status"] = "REVIEW_REQUIRED"
        family["protected_source_status"] = "REVIEW_REQUIRED"
    result["technical_gates"] = [
        "APPROVE_TOPIC_UUID_MAPPING",
        "BIND_SUBJECT_EVIDENCE",
        "REVIEW_NEW_FAMILY_COPY_AND_SOURCE_DETAILS",
        "CHOOSE_AND_APPROVE_TARGET_MIGRATIONS_BACKUP_ROLLBACK",
    ]
    result["actions"]["BLOCKED_CURRENT_TARGET"] = result["target_validation_counts"][
        "FAIL"
    ]
    result["actions"]["REVIEW_REQUIRED_TARGET"] = result["mapping_status_counts"][
        "REVIEW_REQUIRED"
    ]
    return result


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate fixed canonical preparation inputs; never APPLY",
    )
    args = parser.parse_args()
    if not args.validate:
        parser.error("explicit --validate required; no APPLY or report-file writer")
    raw = (root / ".tmp/coach3b-canonical-inputs-2026-10-29.json").read_bytes()
    review = json.loads(
        (root / "scripts/coach3b-review-map.json").read_text(encoding="utf-8")
    )
    if hashlib.sha256(raw).hexdigest() != review["source_snapshot_sha256"]:
        raise ValueError(
            "canonical input changed; consolidated mapping review required"
        )
    result = prepare_target(json.loads(raw), review)
    print(
        json.dumps(
            {
                "validation": (
                    "PASS"
                    if result["target_validation_counts"]["FAIL"] == 0
                    and result["field_loss_counts"]["unmapped_or_changed"] == 0
                    else "FAIL"
                ),
                "mode": result["mode"],
                "target_validation_counts": result["target_validation_counts"],
                "field_loss_counts": result["field_loss_counts"],
                "go_no_go": result["go_no_go"],
                "mapping_status_counts": result["mapping_status_counts"],
                "conditional_counts": result[
                    "counts_conditional_on_approved_empty_target"
                ],
                "business_mutations": 0,
                "report_sha256": hashlib.sha256(
                    json.dumps(result, ensure_ascii=False, sort_keys=True).encode()
                ).hexdigest(),
            }
        )
    )
    return (
        1
        if result["target_validation_counts"]["FAIL"]
        or result["field_loss_counts"]["unmapped_or_changed"]
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
