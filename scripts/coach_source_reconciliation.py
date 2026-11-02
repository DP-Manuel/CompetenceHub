"""Private incremental source annex; never an executable import/public approval.

The policy seam is synthetic-testable. The actual CLI binds the preserved sealed
manifest and current authorized source bytes before issuing a private report.
It never writes a changed Coach, approval, mapping or static Website source.
"""

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from coach_source_ingestion import (
    ROOT,
    SOURCE,
    OUTPUT,
    MAX_BYTES,
    digest,
    encoded,
    no_links,
)

MANIFEST = ROOT / ".tmp/coach3b-real-2026-10-30/manifest.json"
MANIFEST_SHA256 = "872b4df0610ae54ceec1688f323e4d99001befd87d7a3d2395a0001fc82c02fc"
CLASSIFICATIONS = {
    "COACH_PROFILE",
    "COACH_OFFERING",
    "QUALIFICATION",
    "ROLE",
    "PUBLICATION_EVIDENCE",
    "PORTRAIT_ASSET",
    "CONTENT_UPDATE",
    "BUSINESS_PROCESS",
    "PRIVATE_CUSTOMER_BUSINESS_INPUT",
    "FINANCE_INFORMATION_INTERNAL_ONLY",
    "LEGAL_PRIVACY",
    "OPERATIONS",
    "OTHER_REVIEW_REQUIRED",
}
RELATIONSHIPS = {"SUPPLEMENTS", "SUPERSEDES", "CONFLICT", "UNCLEAR"}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(rows, field):
    require(len({r[field] for r in rows}) == len(rows), "duplicate stable key")
    return {r[field]: r for r in rows}


def evaluate(review, frozen, inventory):
    """Policy evaluation only. Caller metadata can never enable real APPLY."""
    from competence_hub_api.portal.coach_registry import Offering
    from competence_hub_api.portal.coach_target import OfferingFamily

    require(
        review["scope"] == "PRIVATE_INCREMENTAL_ANNEX_FROZEN_SHORT_SCOPE_UNCHANGED",
        "private unchanged-short-scope annex required",
    )
    original = deepcopy(frozen)
    require(
        not inventory.get("removed"),
        "removed processed sources need explicit reconciliation",
    )
    rows = frozen["coaches"]
    matches = [r for r in rows if r["source_identity"] == review["source_identity"]]
    require(len(matches) == 1, "existing immutable source identity required")
    require(
        review["identity"]
        == {
            "existing_source_identity_confirmed": True,
            "new_coach": False,
            "real_uuid_allocated": False,
            "route_change": False,
        },
        "new identity/path prohibited in this annex",
    )
    require(review["relationship"] in RELATIONSHIPS, "explicit relationship required")
    sources = unique(review["source_files"], "key")
    changed = {
        r["relative_path"]: r
        for r in inventory["files"]
        if r["change"] in {"NEW", "MODIFIED"}
    }
    require(
        {r["relative_path"] for r in sources.values()} == set(changed),
        "every changed source needs classification",
    )
    for row in sources.values():
        current = changed[row["relative_path"]]
        require(
            row["sha256"] == current["sha256"] and current["technically_readable"],
            "source binding/readability mismatch",
        )
        require(
            bool(row["classification"])
            and set(row["classification"]) <= CLASSIFICATIONS,
            "invalid source classification",
        )
        require(row["relationship"] in RELATIONSHIPS, "source relationship missing")

    publication = review["publication"]
    require(
        set(publication)
        == {
            "profile_content",
            "portrait_asset",
            "new_qualification_labels",
            "offering_content",
            "preview",
            "production",
            "evidence_created",
        },
        "explicit object-specific publication state required",
    )
    require(
        publication["evidence_created"] is False
        and all(
            v == "UNKNOWN" for k, v in publication.items() if k != "evidence_created"
        ),
        "source access does not grant new publication consent",
    )
    require(
        review["excluded"]["raw_values_copied_to_registry_or_public_artifacts"]
        is False,
        "protected data must not be propagated",
    )
    require(
        not review["assets"]["portrait_replaced"]
        and review["assets"]["reuse_approval"] == "UNKNOWN",
        "embedded image is not replacement approval",
    )
    from competence_hub_api.portal.coach_target import Qualification, PublicRole

    require(
        review["profile_delta"]["qualification_review"][
            "automatic_background_to_qualification_conversion"
        ]
        is False,
        "no automatic credential conversion",
    )
    require(
        review["profile_delta"]["automatic_taxonomy_changes"] is False,
        "no automatic topic assignment",
    )
    for index, role in enumerate(review["profile_delta"]["roles"]):
        require(
            role["verification"] == "source_asserted"
            and role["public_approval"] == "UNKNOWN",
            "new role assertion is not verified/public",
        )
        PublicRole(
            key=role["key"],
            code=role["key"],
            display_label=role["label"],
            ordering=index,
        )
    qualifications = unique(review.get("qualification_candidates", []), "key")
    for index, row in enumerate(qualifications.values()):
        require(
            row["status"] == "SOURCE_ASSERTED_REVIEW_ONLY" and row["public"] is False,
            "candidate qualification is not canonical/public",
        )
        require(row["source"] in sources, "qualification source missing")
        Qualification(
            key=row["key"],
            canonical_title=row["canonical_title"],
            issuer=row["issuer"],
            verification_state="source_asserted",
            public=False,
            ordering=index,
        )

    families = unique(review["families"], "key")
    formats = unique(review["formats"], "key")
    for index, family in enumerate(families.values()):
        OfferingFamily(
            key=family["key"], title=family["title"], ordering=index, active=False
        )
        require(
            len(family["formats"]) == len(set(family["formats"])),
            "duplicate grouped formats",
        )
        require(
            all(
                k in formats and formats[k]["family"] == family["key"]
                for k in family["formats"]
            ),
            "family/format mismatch",
        )
    for index, item in enumerate(formats.values()):
        require(
            item["family"] in families
            and item["key"] in families[item["family"]]["formats"],
            "orphaned source format",
        )
        require(item["source"] in sources, "unbound format source")
        source = sources[item["source"]]
        if "physical_pages" in source:
            require(
                bool(item["pages"])
                and all(
                    type(p) is int and 1 <= p <= source["physical_pages"]
                    for p in item["pages"]
                ),
                "physical PDF page out of range",
            )
        else:
            require(item["pages"] == [], "DOCX paragraphs are not physical PDF pages")
        require(
            item["status"] in {"UNAPPROVED_PUBLIC_CANDIDATE", "REVIEW_REQUIRED_SOURCE"},
            "candidate cannot be marked approved",
        )
        Offering(
            key=item["key"],
            family_key=item["family"],
            title=families[item["family"]]["title"],
            type=item["type"],
            ordering=index,
            delivery_mode=item["delivery_mode"],
            duration=item["duration"],
            active=False,
            bookable=False,
        )

    clarifications = unique(review["clarifications"], "key")
    for item in clarifications.values():
        require(
            item["kind"] in {"CONTRACT_GAP", "UNCLEAR", "CONFLICT"},
            "source uncertainty must be explicit",
        )
        require(
            type(item["required_for_current_short_scope"]) is bool,
            "required scope flag must be boolean",
        )
        require(
            item["status"] in {"DEFERRED_NOT_IMPORTED", "REVIEW_REQUIRED_SOURCE"},
            "uncertainty cannot be silently closed",
        )
        require(
            all(s in formats or s == "all-format-options" for s in item["subjects"]),
            "unbound clarification subject",
        )

    impacted = next(
        i
        for i, r in enumerate(rows)
        if r["source_identity"] == review["source_identity"]
    )
    states = [r["mapping_status"] for r in rows]
    required = [
        c for c in clarifications.values() if c["required_for_current_short_scope"]
    ]
    if required:
        states[impacted] = (
            "BLOCKED"
            if any(c["kind"] == "CONTRACT_GAP" for c in required)
            else "REVIEW_REQUIRED"
        )
    require(
        set(states) <= {"READY", "REVIEW_REQUIRED", "BLOCKED"},
        "invalid legacy mapping state",
    )
    require(
        review["scope_impact"]["canonical_field_loss"] == 0
        and review["scope_impact"]["new_annex_items_not_imported"] is True,
        "explicit preservation/deferred model gaps required",
    )
    require(
        review["scope_impact"]["frozen_manifest_change"] is False
        and review["scope_impact"]["public_projection_change"] is False
        and review["scope_impact"]["new_customer_or_finance_module"] is False,
        "frozen public scope must remain unchanged",
    )
    require(frozen == original, "frozen manifest was mutated")
    return {
        "schema": 1,
        "scope": "PRIVATE_REVIEW_ANNEX_NOT_EXECUTABLE",
        "review_sha256": digest(encoded(review)),
        "source_bindings": {k: r["sha256"] for k, r in sources.items()},
        "inventory_sha256": digest(encoded(inventory)),
        "coaches_affected": 1,
        "new_coaches": 0,
        "mapping_status_counts": {
            k: Counter(states)[k] for k in ("READY", "REVIEW_REQUIRED", "BLOCKED")
        },
        "frozen_manifest_changed": False,
        "existing_counts_unchanged": deepcopy(frozen["counts"]),
        "canonical_field_loss": 0,
        "candidate_families": len(families),
        "source_format_candidates": len(formats),
        "additional_role_assertions": len(review["profile_delta"]["roles"]),
        "training_label_assertions_for_review": len(qualifications),
        "optional_source_clarifications": len(clarifications) - len(required),
        "contract_gaps_not_imported": sum(
            c["kind"] == "CONTRACT_GAP" for c in clarifications.values()
        ),
        "new_publication_approvals": 0,
        "approved_new_assets": 0,
        "public_projection_action": "KEEP_FROZEN_PUBLIC_SCOPE",
        "source_relationship": review["relationship"],
        "private_customer_business_information_present": review["excluded"][
            "private_customer_business_information_present"
        ],
        "private_contact_information_present": review["excluded"][
            "private_contact_information_present"
        ],
        "internal_price_present": review["excluded"]["internal_price_present"],
        "no_raw_values_in_receipt": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-name", default="readiness-annex.json")
    args = parser.parse_args(argv)
    require(
        bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.json", args.report_name)),
        "safe private report name required",
    )
    from coach3b_real_manifest import verify_manifest

    review_path = OUTPUT / "review.json"
    inventory_path = OUTPUT / "inventory.json"
    for path in (review_path, inventory_path, MANIFEST):
        no_links(path)
    body = MANIFEST.read_bytes()
    require(digest(body) == MANIFEST_SHA256, "exact preserved manifest required")
    frozen = json.loads(body)
    verify_manifest(frozen)
    review = json.loads(review_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    require(
        review["baseline_manifest_sha256"] == MANIFEST_SHA256,
        "review baseline mismatch",
    )
    for row in inventory["files"]:
        path = SOURCE / row["relative_path"]
        require(
            path.resolve().is_relative_to(SOURCE.resolve()),
            "source escaped authorized directory",
        )
        no_links(path)
        require(
            path.suffix.lower() in {".pdf", ".docx"}
            and path.stat().st_size <= MAX_BYTES,
            "only bounded authorized document types may be hashed",
        )
        require(
            digest(path.read_bytes()) == row["sha256"],
            "current source no longer matches inventory",
        )
    result = evaluate(review, frozen, inventory)
    target = OUTPUT / args.report_name
    no_links(target)
    with target.open("xb") as stream:
        stream.write(encoded(result))
    require(digest(MANIFEST.read_bytes()) == MANIFEST_SHA256, "frozen manifest changed")
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in {"source_bindings", "existing_counts_unchanged"}
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
