"""Private source reconciliation; never imports, grants consent or publishes.

Only the explicitly authorized concept and the existing frozen manifest are
eligible for the actual CLI. Test policy inputs cannot issue import approval.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt

from competence_hub_api.portal.coach_registry import Offering
from competence_hub_api.portal.coach_target import Duration, digest

ROOT = Path(__file__).resolve().parents[1]
PDF = "Quellen/20261030/Konzept_Schwabauer.pdf"
PDF_SHA256 = "04805b6e6b96313e68f285d01c922d9342bd692ce4ec2cce68b9b124191f4620"
REVIEW_SHA256 = "141320445920f0fd8f6f816cd6f1dca9f3744a0508996980a67f67cda77f6434"
KEY = r"^[a-z0-9][a-z0-9/_-]{0,119}$"
GROUPS = {"FK", "MA", "PA", "ASA"}
BOUNDARIES = {
    "psychotherapy_separate_inactive_not_coaching",
    "prevention_and_training_not_treatment",
    "occupational_assessment_not_psychotherapy",
    "no_legal_advice_or_statutory_compliance_guarantee",
}


class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    key: str = Field(pattern=KEY)
    title: str = Field(min_length=1, max_length=250)
    pages: list[StrictInt] = Field(min_length=1)


class Family(Fact):
    pass


class Concept(Fact):
    family_key: str = Field(pattern=KEY)
    groups: list[str] | None
    group_candidates: list[list[str]] = []
    conflicts: list[str] = []


class Format(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    key: str = Field(pattern=KEY)
    concept_key: str = Field(pattern=KEY)
    kind: str
    duration_label: str | None
    minutes: StrictInt | None = Field(ge=1)
    maximum_minutes: StrictInt | None = Field(default=None, ge=1)
    range_months: list[StrictInt] | None = None
    duration_candidates: list[dict] = []
    phases: list[str] = []
    supplements: str | None = None
    pages: list[StrictInt] = Field(min_length=1)
    conflicts: list[str] = []


class Package(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    key: str = Field(pattern=KEY)
    label: str
    components: list[str] = Field(min_length=2)
    groups: list[str] | None
    group_candidates: list[list[str]] = []
    duration_label: str
    pages: list[StrictInt] = Field(min_length=1)
    conflicts: list[str] = []


def unique(rows, label):
    by_key = {r["key"]: r for r in rows}
    if len(by_key) != len(rows):
        raise ValueError("duplicate " + label + " identity")
    return by_key


def evaluate(review, legacy):
    """Policy-only report: no DB, identities, consent or public-content mutation."""
    if (
        review.get("scope")
        != "PRIVATE_RECONCILIATION_EXISTING_PUBLIC_SHORT_SCOPE_UNCHANGED"
    ):
        raise ValueError("private unchanged-short-scope required")
    if review["source_identity"] != legacy["source_identity"]:
        raise ValueError("source identity conflict")
    if review["source"].get("new_publication_rights") != "UNKNOWN":
        raise ValueError("source processing is not new publication approval")
    families = unique(
        [Family.model_validate(x).model_dump() for x in review["families"]], "family"
    )
    concepts = unique(
        [Concept.model_validate(x).model_dump() for x in review["concepts"]], "concept"
    )
    formats = unique(
        [Format.model_validate(x).model_dump() for x in review["formats"]], "format"
    )
    packages = unique(
        [Package.model_validate(x).model_dump() for x in review["packages"]], "package"
    )
    conflicts = unique(review["conflicts"], "conflict")
    links = unique(review["legacy_links"], "legacy link")
    if (
        len(families) != 3
        or len(concepts) != 12
        or len(formats) != 21
        or len(packages) != 9
    ):
        raise ValueError("reconciled source shape changed")
    for conflict in conflicts.values():
        if (
            conflict["kind"] != "SOURCE_CONFLICT"
            or conflict["status"] != "REVIEW_REQUIRED_SOURCE"
            or type(conflict["required_for_current_short_scope"]) is not bool
        ):
            raise ValueError("explicit source conflict classification required")
    if any(c["required_for_current_short_scope"] for c in conflicts.values()):
        raise ValueError("required source conflict blocks short scope")
    for concept in concepts.values():
        if concept["family_key"] not in families:
            raise ValueError("orphaned concept")
    groups = set()
    for row in [*concepts.values(), *packages.values()]:
        groups.update(row["groups"] or [])
        for candidate in row["group_candidates"]:
            groups.update(candidate)
        if row["groups"] is None and not row["conflicts"]:
            raise ValueError("unknown group needs an explicit source conflict")
    if not groups <= GROUPS:
        raise ValueError("target groups must not invent topics or categories")
    classification = Counter()
    for row in formats.values():
        if row["concept_key"] not in concepts:
            raise ValueError("orphaned format")
        if row["duration_candidates"] and row["minutes"] is not None:
            raise ValueError("conflicting duration must remain unresolved")
        if (row["range_months"] or row["phases"]) and row[
            "kind"
        ] != "consulting_process":
            raise ValueError("project process must not become a workshop")
        if (row["range_months"] or row["maximum_minutes"] is not None) and row[
            "minutes"
        ] is not None:
            raise ValueError("range or maximum is not an exact duration")
        if row["range_months"] is not None and (
            len(row["range_months"]) != 2
            or not 1 <= row["range_months"][0] <= row["range_months"][1]
        ):
            raise ValueError("invalid month range")
        if row["kind"] in {"lecture", "workshop"}:
            kind, domains = row["kind"], ("training", "health_promotion")
        elif row["kind"] == "consulting_process":
            kind, domains = "other", ("consulting",)
        elif row["kind"] == "moderated_analysis":
            kind, domains = "other", ("moderation",)
        else:
            raise ValueError("unreviewed format classification")
        Offering(
            key=row["key"],
            title=concepts[row["concept_key"]]["title"],
            type=kind,
            active=False,
            bookable=False,
            service_domains=domains,
            duration=Duration(minutes=row["minutes"], label=row["duration_label"]),
        )
        classification[row["kind"]] += 1
        if row["supplements"] and row["supplements"] not in formats:
            raise ValueError("missing supplement parent")
    for package in packages.values():
        if len(set(package["components"])) != len(package["components"]) or any(
            key not in formats for key in package["components"]
        ):
            raise ValueError("package must reference existing formats, no copies")
        if any(formats[key]["kind"] != "workshop" for key in package["components"]):
            raise ValueError("reviewed workshop package contains wrong format")
    for row in [*concepts.values(), *formats.values(), *packages.values()]:
        if not set(row["conflicts"]) <= conflicts.keys():
            raise ValueError("missing source conflict evidence")
        if any(type(p) is not int or not 1 <= p <= 13 for p in row["pages"]):
            raise ValueError("invalid source page")
    if set(review["boundaries"]) != BOUNDARIES:
        raise ValueError("therapy/occupational/legal boundary changed")
    legacy_items = {o["key"]: o for o in legacy["offerings"]}
    if links.keys() != legacy_items.keys():
        raise ValueError("every old offering must be preserved and reconciled")
    valid_targets = families.keys() | concepts.keys() | formats.keys()
    for link in links.values():
        if link["status"] not in {
            "EXACT_FORMAT",
            "EXACT_CONCEPT_ONLY",
            "FAMILY_ONLY",
            "UNCONFIRMED_OPTIONAL",
            "RETAIN_OUTSIDE_PDF",
            "RETAIN_INACTIVE_THERAPY_BOUNDARY",
        }:
            raise ValueError("unknown legacy mapping classification")
        if link["target"] is not None and link["target"] not in valid_targets:
            raise ValueError("legacy target reference missing")
        if link["status"] == "EXACT_FORMAT" and link["target"] not in formats:
            raise ValueError("format crosswalk must not resolve a generic family")
    extensions = unique(review["extensions"], "extension")
    for extension in extensions.values():
        if extension["parent"] not in families.keys() | formats.keys() or extension[
            "kind"
        ] not in {"extended_format", "option"}:
            raise ValueError("extension must reference an existing reviewed parent")
    therapy = links.get("weitere/2")
    if (
        not therapy
        or therapy["status"] != "RETAIN_INACTIVE_THERAPY_BOUNDARY"
        or legacy_items["weitere/2"]["active"] is not False
    ):
        raise ValueError("psychotherapy must remain separate and inactive")
    return {
        "mode": "PRIVATE_SOURCE_RECONCILIATION_NOT_IMPORT_APPROVAL",
        "result": "PASS",
        "source_pages": review["source"]["pages"],
        "new_source_families": len(families),
        "new_source_concepts": len(concepts),
        "new_source_formats": len(formats),
        "format_classification": dict(sorted(classification.items())),
        "packages": len(packages),
        "extensions": len(review["extensions"]),
        "project_phases": sum(len(f["phases"]) for f in formats.values()),
        "source_conflicts_optional": len(conflicts),
        "legacy_titles_preserved": len(legacy_items),
        "legacy_links": dict(
            sorted(Counter(x["status"] for x in links.values()).items())
        ),
        "current_import_field_loss": 0,
        "current_import_counts_changed": False,
        "new_publication_rights": "UNKNOWN",
        "new_source_fields_imported": 0,
        "full_structured_model_supported": False,
        "deferred_not_imported": {
            "packages.component_references": "Variant has no component-reference graph; preserve source relationships privately, not repeated text",
            "formats.project_phases": "No typed ordered project-phase collection",
            "families.customization_capabilities": "No typed customization capability collection",
            "formats.duration_ranges": "Literal Duration.label preserves meaning, but no typed month/min/max interval; no invented exact minutes",
        },
        "migration_required_for_current_short_scope": False,
        "business_mutations": 0,
        "public_projection_changed": False,
        "real_apply_enabled": False,
    }


def verify_pdf(root, source):
    if (
        source["path"] != PDF
        or source["sha256"] != PDF_SHA256
        or source["pages"] != 13
        or source.get("processing_approved") is not True
    ):
        raise ValueError("authorized source identity changed")
    path = (root / PDF).resolve()
    if not path.is_relative_to(root / "Quellen/20261030"):
        raise ValueError("source outside authorized directory")
    if hashlib.sha256(path.read_bytes()).hexdigest() != PDF_SHA256:
        raise ValueError("source PDF bytes changed")
    raw = subprocess.check_output(
        ["pdftotext", "-enc", "UTF-8", "-layout", str(path), "-"]
    )
    text = raw.decode("utf-8")
    if text.count("\f") != 13:
        raise ValueError("source page extraction incomplete")
    # The original pages were also inspected visually; this protects key table
    # anomalies on subsequent local runs, not a heuristic correction of them.
    compact = re.sub(r"\s+", " ", text)
    for anchor in (
        "90 min",
        "Paket A.2",
        "Resiliente und leistungsfähige",
        "Wiedereingliederung nach psychi-",
        "Ca. 6-12 Monate",
    ):
        if anchor not in compact:
            raise ValueError("expected reviewed source anchor missing")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True)
    parser.add_argument("--base-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    review_path, base, output = [
        Path(p).resolve() for p in (args.review, args.base_manifest, args.output)
    ]
    if (
        any(not p.is_relative_to(ROOT / ".tmp") for p in (review_path, base, output))
        or output.exists()
    ):
        parser.error("private .tmp inputs/new output required; no overwrite")
    review_raw, manifest_raw = review_path.read_bytes(), base.read_bytes()
    if hashlib.sha256(review_raw).hexdigest() != REVIEW_SHA256:
        raise ValueError(
            "reviewed source reconciliation bytes changed; inspect before rebinding"
        )
    review, manifest = json.loads(review_raw), json.loads(manifest_raw)
    from coach3b_real_manifest import verify_local_inputs

    verify_local_inputs(ROOT, manifest)
    verify_pdf(ROOT, review["source"])
    canonical = json.loads(
        (ROOT / ".tmp/coach3b-canonical-inputs-2026-10-29.json").read_bytes()
    )
    legacy = next(
        x
        for x in canonical["coaches"]
        if x["source_identity"] == review["source_identity"]
    )
    report = evaluate(review, legacy)
    artifact = {
        "schema": "coach3b-source-readiness-manifest-v1",
        "base_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "source_review_sha256": hashlib.sha256(review_raw).hexdigest(),
        "source_pdf_sha256": PDF_SHA256,
        "base_review_report_sha256": manifest["review_report_sha256"],
        "current_import_counts": manifest["counts"],
        "source_reconciliation": report,
        "real_apply_enabled": False,
    }
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    data = json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2).encode()
    with output.open("xb") as handle:
        handle.write(data)
    print(
        json.dumps(
            {
                **report,
                "readiness_manifest_sha256": hashlib.sha256(data).hexdigest(),
                "source_review_sha256": artifact["source_review_sha256"],
                "source_pdf_sha256": PDF_SHA256,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
