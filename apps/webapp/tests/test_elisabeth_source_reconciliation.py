from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "elisabeth_source_reconciliation",
    ROOT / "scripts/elisabeth_source_reconciliation.py",
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def fixture():
    identity = {"source_system": "synthetic", "source_key": "coach/synthetic"}
    source = {
        "source_identity": identity,
        "offerings": [
            {"key": f"offer/{i}", "title": f"Synthetic old {i}", "active": True}
            for i in range(16)
        ]
        + [
            {"key": "weitere/2", "title": "Synthetic separate therapy", "active": False}
        ],
    }
    families = [
        {"key": f"family/{i}", "title": f"Synthetic family {i}", "pages": [3]}
        for i in range(3)
    ]
    concepts = [
        {
            "key": f"concept/{i}",
            "family_key": f"family/{i % 3}",
            "title": f"Synthetic concept {i}",
            "groups": ["FK", "MA"],
            "pages": [3],
        }
        for i in range(12)
    ]
    formats = [
        {
            "key": f"format/{i}/{kind}",
            "concept_key": f"concept/{i}",
            "kind": kind,
            "duration_label": "Synthetic duration",
            "minutes": None,
            "pages": [3],
        }
        for i in range(9)
        for kind in ("lecture", "workshop")
    ]
    formats += [
        {
            "key": f"format/{i}",
            "concept_key": f"concept/{i}",
            "kind": kind,
            "duration_label": "Synthetic duration",
            "minutes": None,
            "pages": [12],
        }
        for i, kind in (
            (9, "lecture"),
            (10, "consulting_process"),
            (11, "moderated_analysis"),
        )
    ]
    packages = [
        {
            "key": f"package/{i}",
            "label": f"Synthetic package {i}",
            "components": ["format/0/workshop", "format/1/workshop"],
            "groups": ["FK"],
            "duration_label": "Synthetic total",
            "pages": [3],
        }
        for i in range(9)
    ]
    review = {
        "source": {"pages": 13, "new_publication_rights": "UNKNOWN"},
        "source_identity": identity,
        "scope": "PRIVATE_RECONCILIATION_EXISTING_PUBLIC_SHORT_SCOPE_UNCHANGED",
        "families": families,
        "concepts": concepts,
        "formats": formats,
        "packages": packages,
        "extensions": [],
        "conflicts": [
            {
                "key": f"C{i}",
                "kind": "SOURCE_CONFLICT",
                "status": "REVIEW_REQUIRED_SOURCE",
                "required_for_current_short_scope": False,
            }
            for i in range(8)
        ],
        "legacy_links": [
            {
                "key": x["key"],
                "status": (
                    "RETAIN_INACTIVE_THERAPY_BOUNDARY"
                    if not x["active"]
                    else "RETAIN_OUTSIDE_PDF"
                ),
                "target": None,
            }
            for x in source["offerings"]
        ],
        "boundaries": sorted(module.BOUNDARIES),
    }
    return review, source


def test_formats_are_not_new_topics_and_packages_only_reference_existing_formats():
    review, source = fixture()
    before = deepcopy((review, source))
    result = module.evaluate(review, source)
    assert result["new_source_concepts"] == 12 and result["new_source_formats"] == 21
    assert result["format_classification"] == {
        "consulting_process": 1,
        "lecture": 10,
        "moderated_analysis": 1,
        "workshop": 9,
    }
    assert result["packages"] == 9 and result["legacy_titles_preserved"] == 17
    assert result["current_import_field_loss"] == 0
    assert result["new_source_fields_imported"] == 0
    assert result["public_projection_changed"] is False
    assert result["real_apply_enabled"] is False
    assert result["full_structured_model_supported"] is False
    assert len(result["deferred_not_imported"]) == 4
    assert (review, source) == before


def test_optional_source_conflicts_preserve_unknown_duration_not_a_selected_value():
    review, source = fixture()
    review["formats"][0].update(
        duration_label=None,
        duration_candidates=[{"minutes": 90}, {"minutes": 120}],
        conflicts=["C0"],
    )
    result = module.evaluate(review, source)
    assert result["result"] == "PASS" and result["source_conflicts_optional"] == 8
    review["formats"][0]["minutes"] = 90
    with pytest.raises(ValueError, match="remain unresolved"):
        module.evaluate(review, source)


@pytest.mark.parametrize(
    "change",
    [
        "identity",
        "publication",
        "orphan",
        "duplicate",
        "package_ref",
        "package_copy",
        "category",
        "required_conflict",
        "conflict_ref",
        "therapy",
        "missing_old",
        "project_as_workshop",
        "boundary",
    ],
)
def test_incorrect_source_mapping_fails_without_modifying_legacy(change):
    review, source = fixture()
    original = deepcopy(source)
    if change == "identity":
        review["source_identity"] = {
            "source_system": "synthetic",
            "source_key": "coach/other",
        }
    elif change == "publication":
        review["source"]["new_publication_rights"] = "APPROVED"
    elif change == "orphan":
        review["concepts"][0]["family_key"] = "absent"
    elif change == "duplicate":
        review["formats"][1]["key"] = review["formats"][0]["key"]
    elif change == "package_ref":
        review["packages"][0]["components"][0] = "absent"
    elif change == "package_copy":
        review["packages"][0]["components"] *= 2
    elif change == "category":
        review["concepts"][0]["groups"] = ["Alle Themen"]
    elif change == "required_conflict":
        review["conflicts"][0]["required_for_current_short_scope"] = True
    elif change == "conflict_ref":
        review["formats"][0]["conflicts"] = ["missing"]
    elif change == "therapy":
        review["legacy_links"][-1]["status"] = "EXACT_FORMAT"
        review["legacy_links"][-1]["target"] = review["formats"][0]["key"]
    elif change == "missing_old":
        review["legacy_links"].pop()
    elif change == "project_as_workshop":
        review["formats"][-2].update(
            kind="workshop", range_months=[6, 12], phases=["analyse"]
        )
    else:
        review["boundaries"].pop()
    with pytest.raises(ValueError):
        module.evaluate(review, source)
    assert source == original


def test_process_month_range_stays_literal_and_never_becomes_invented_workshop_minutes():
    review, source = fixture()
    row = review["formats"][-2]
    row.update(
        duration_label="ca. 6-12 Monate",
        range_months=[6, 12],
        phases=["analyse", "evaluation"],
    )
    result = module.evaluate(review, source)
    assert result["project_phases"] == 2
    assert row["minutes"] is None and row["kind"] == "consulting_process"
