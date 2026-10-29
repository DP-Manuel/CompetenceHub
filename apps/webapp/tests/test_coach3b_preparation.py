from copy import deepcopy
from datetime import date, datetime
import importlib.util
from pathlib import Path
import socket
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "coach3b_preparation", ROOT / "scripts/coach3b_preparation.py"
)
policy = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = policy
spec.loader.exec_module(policy)


def inputs():
    source = {
        "mode": "READ_ONLY_CANONICAL_NO_DB",
        "categories": [
            {"id": s}
            for s in (
                "personalentwicklung",
                "persoenlichkeitsentwicklung",
                "karrierecoaching",
            )
        ],
        "topics": [
            {"id": f"topic-{i}", "categories": ["personalentwicklung"]}
            for i in range(8)
        ],
        "coaches": [
            {
                "profilePath": "coaches/synthetic",
                "source_identity": {
                    "source_system": "synthetic",
                    "source_key": "coach/one",
                },
                "profile_path": "/coaches/synthetic/",
                "name": "Synthetic",
                "role": "Trainer and Coach",
                "credentials": ["Synthetic degree", "Synthetic practice"],
                "quotes": [],
                "external_links": [],
                "offerings": [],
                "topics": ["topic-0"],
                "focus": ["A source focus, not a qualification"],
                "asset": None,
                "template": "synthetic-profile",
            }
        ],
    }
    review = {
        "scope": "PREPARATION_ONLY_NO_DATABASE_OR_PUBLICATION",
        "coaches": {
            "synthetic": {
                "credential_kinds": ["qualification", "competency"],
                "roles": [
                    {"canonical": "trainer", "display": "Trainer"},
                    {"canonical": "coach", "display": "Coach"},
                ],
                "project_evidence": {
                    "profile": "APPROVED",
                    "portrait": "NOT_REQUIRED",
                    "preview": "APPROVED",
                    "production": "UNKNOWN",
                },
                "background_note": "Synthetic",
            }
        },
        "new_offering_families": [],
        "source_quality": [],
        "private_exclusions": ["certificate_numbers"],
        "scan_review": {},
    }
    return source, review


@pytest.mark.parametrize("public", [True, False])
def test_public_qualification_never_exports_evidence_or_internal_fields(public):
    q = policy.Qualification(
        "Internal canonical name",
        public,
        "Public label",
        "private-certificate-reference",
        "VERIFIED",
    )
    assert q.public_projection() == ({"label": "Public label"} if public else None)


def test_no_inferred_roles_or_qualification_from_focus_or_topic():
    source, review = inputs()
    record = policy.prepare(source, review)["coaches"][0]
    assert record["roles"] == review["coaches"]["synthetic"]["roles"]
    assert record["competencies"] == ["Synthetic practice"]
    assert record["public_projection_candidate"]["qualifications"] == [
        {"label": "Synthetic degree"}
    ]
    assert record["focus_labels"] != record["competencies"]


def test_existing_portrait_and_approved_profile_do_not_infer_portrait_approval():
    source, review = inputs()
    source["coaches"][0]["asset"] = {"reference": "synthetic.png", "sha256": "a" * 64}
    review["coaches"]["synthetic"]["project_evidence"]["portrait"] = "UNKNOWN"
    record = policy.prepare(source, review)["coaches"][0]
    assert record["evidence"]["profile_content"] == "APPROVED"
    assert record["evidence"]["portrait"] == "UNKNOWN"
    assert not policy.Evidence(
        "portrait", "a" * 64, "preview", record["evidence"]["portrait"], None
    ).permits("portrait", "a" * 64, "preview")


@pytest.mark.parametrize("bad", ["false", "true", None])
def test_qualification_visibility_does_not_coerce_strings(bad):
    with pytest.raises(ValueError):
        policy.Qualification("Synthetic", bad, "Public label").public_projection()


@pytest.mark.parametrize("kind,bookable", [("coaching", False), ("other", True)])
def test_therapy_cannot_become_coaching_or_bookable(kind, bookable):
    with pytest.raises(ValueError):
        policy.validate_offering(
            kind, ["psychotherapy"], bookable=bookable, source_status="READY"
        )
    policy.validate_offering(
        None, ["psychotherapy"], bookable=False, source_status="READY"
    )


@pytest.mark.parametrize(
    "subject,subject_key,environment,allowed",
    [
        ("profile", "rev-1", "preview", True),
        ("portrait", "rev-1", "preview", False),
        ("profile", "new-revision", "preview", False),
        ("profile", "rev-1", "production", False),
    ],
)
def test_profile_approval_is_not_asset_new_revision_or_production_approval(
    subject, subject_key, environment, allowed
):
    evidence = policy.Evidence(
        "profile", "rev-1", "preview", "APPROVED", "synthetic:evidence"
    )
    assert evidence.permits(subject, subject_key, environment) == allowed
    assert evidence.historical_at is None and evidence.historical_date is None


def test_date_precision_and_unknown_approval_are_not_fabricated():
    evidence = policy.Evidence(
        "portrait",
        "sha256-a",
        "preview",
        "APPROVED",
        "synthetic:evidence",
        historical_date=date(2026, 10, 21),
    )
    assert evidence.historical_at is None
    unknown = policy.Evidence("portrait", "sha256-a", "preview", "UNKNOWN", None)
    assert not unknown.permits("portrait", "sha256-a", "preview")
    with pytest.raises(ValueError):
        policy.Evidence(
            "profile",
            "r",
            "preview",
            "APPROVED",
            "x",
            historical_at=datetime(2026, 10, 21),
        ).permits("profile", "r", "preview")


def test_pure_dry_mapping_no_io_no_input_mutation_missing_portrait_valid(monkeypatch):
    source, review = inputs()
    before = deepcopy((source, review))

    def denied(*args, **kwargs):
        raise AssertionError("unexpected IO")

    monkeypatch.setattr("builtins.open", denied)
    monkeypatch.setattr(socket, "socket", denied)
    first = policy.prepare(source, review)
    assert first == policy.prepare(source, review)
    assert (source, review) == before
    assert first["business_mutations"] == 0 and first["database_snapshot"] == "NOT_READ"
    assert first["actions"]["WOULD_SKIP_PORTRAIT"] == 1
    assert (
        first["go_no_go"] == "NO_GO_APPLY"
        and first["mapping_status_counts"]["BLOCKED"] == 1
    )


def test_field_loss_classifies_all_four_cases_and_never_drops_unknown_fields():
    rows = policy.field_loss(
        ["public_roles", "unknown_field", "private_contacts", "image_dimensions"]
    )
    assert {r["classification"] for r in rows} == {
        "needs_model_extension",
        "manual_decision",
        "intentionally_excluded_private_data",
        "harmless_presentation_only",
    }


def test_unread_source_never_supplies_details_or_conceptually_new_topics():
    with pytest.raises(ValueError):
        policy.validate_offering(
            "workshop",
            ["training"],
            bookable=False,
            source_status="SOURCE_REPLACEMENT_REQUIRED",
            detail_fields={"invented": "duration"},
        )
    policy.validate_offering(
        "workshop",
        ["training"],
        bookable=False,
        source_status="SOURCE_REPLACEMENT_REQUIRED",
    )
    source, review = inputs()
    source["coaches"][0]["topics"] = ["exercise-not-a-global-topic"]
    with pytest.raises(ValueError):
        policy.prepare(source, review)


def test_family_formats_and_options_do_not_become_flat_independent_offers():
    source, review = inputs()
    review["new_offering_families"] = [
        {
            "key": "synthetic-family",
            "service_domains": ["coaching", "moderation"],
            "formats": [{"key": "day", "kind": "workshop", "source_status": "READY"}],
            "options": [{"key": "follow-up", "kind": "optional_add_on"}],
        }
    ]
    result = policy.prepare(source, review)
    assert result["counts_conditional_on_approved_empty_target"]["offerings"] == 0
    assert (
        result["counts_conditional_on_approved_empty_target"][
            "new_offering_formats_held"
        ]
        == 1
    )
    review["new_offering_families"][0]["service_domains"] = ["mediation"]
    with pytest.raises(ValueError):
        policy.prepare(source, review)


def test_explicit_short_copy_approval_closes_rights_not_missing_details_or_deployment():
    source, review = inputs()
    review["source_quality"] = [
        {"key": "synthetic-unread", "status": "SOURCE_REPLACEMENT_REQUIRED"}
    ]
    review["new_offering_families"] = [
        {
            "key": "synthetic",
            "service_domains": ["training"],
            "formats": [
                {
                    "key": "unread",
                    "kind": "workshop",
                    "source_status": "SOURCE_REPLACEMENT_REQUIRED",
                    "detail_fields": None,
                }
            ],
            "public_copy_approval": "APPROVED",
            "offering_content_approval": "APPROVED",
            "publication_scopes": ["preview", "production"],
            "approval_reference": "synthetic:explicit-scope",
        }
    ]
    result = policy.prepare(source, review)
    assert not any(
        r["kind"] in {"COPYRIGHT_PUBLIC_COPY_APPROVAL", "OFFERING_CONTENT_APPROVAL"}
        for r in result["manual_reviews"]
    )
    assert (
        result["counts_conditional_on_approved_empty_target"][
            "source_replacements_required"
        ]
        == 1
    )
    assert (
        result["publication_side_effects"] == 0 and result["go_no_go"] == "NO_GO_APPLY"
    )
    assert result["new_offering_families"][0]["formats"][0]["detail_fields"] is None


def test_short_copy_approval_requires_exact_environment_scope_and_reference():
    source, review = inputs()
    review["new_offering_families"] = [
        {
            "key": "synthetic",
            "service_domains": ["training"],
            "formats": [],
            "public_copy_approval": "APPROVED",
        }
    ]
    with pytest.raises(ValueError):
        policy.prepare(source, review)


@pytest.mark.parametrize(
    "mutation",
    [
        "credential_count",
        "qualification_as_role",
        "duplicate_source",
        "fourth_category",
        "unknown_field",
    ],
)
def test_changed_or_unclassified_inputs_stop_preparation(mutation):
    source, review = inputs()
    if mutation == "credential_count":
        source["coaches"][0]["credentials"].append("Unexpected")
    elif mutation == "qualification_as_role":
        review["coaches"]["synthetic"]["credential_kinds"][0] = "invented_role"
    elif mutation == "duplicate_source":
        source["coaches"].append(deepcopy(source["coaches"][0]))
    elif mutation == "unknown_field":
        source["coaches"][0]["unknown_source_field"] = "must not disappear"
    else:
        source["categories"].append({"id": "all"})
    with pytest.raises(ValueError):
        policy.prepare(source, review)
