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
            {
                "id": f"topic-{i}",
                "label": f"Synthetic canonical topic {i}",
                "categories": ["personalentwicklung"],
            }
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


def test_target_preparation_constructs_real_models_without_io_or_readiness_invention(
    monkeypatch,
):
    from competence_hub_api.portal.coach_registry import ProfileContent

    source, review = inputs()
    record = source["coaches"][0]
    record.update(
        text="Synthetic introduction",
        previewRole="Synthetic preview label",
        sections=[
            {
                "source_key": "section-1",
                "kind": "coach-profile-hero",
                "headings": ["Synthetic heading"],
                "paragraphs": ["Synthetic paragraph"],
            }
        ],
        quotes=["Synthetic quote"],
        topic_cards=[{"title": "Synthetic card", "text": "Synthetic card text"}],
        external_links=[
            {
                "kind": "quoted",
                "target": "https://example.invalid/",
                "label": "Synthetic link",
            }
        ],
    )
    before = deepcopy(source)

    def forbidden(*args, **kwargs):
        raise AssertionError("target preparation must remain in memory")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    result = policy.prepare_target(source, review)
    actual = result["coaches"][0]
    content = ProfileContent.model_validate(actual["target_content"])
    assert content.target_version == 1 and not content.topic_ids
    assert content.public_roles[0].code == "trainer"
    assert content.qualifications[0].canonical_title == "Synthetic degree"
    assert content.presentation.quote == "Synthetic quote"
    assert content.presentation.sections[0].paragraphs == ("Synthetic paragraph",)
    assert (
        content.presentation.external_links[0].preview_url == "https://example.invalid/"
    )
    assert actual["object_evidence"] == []
    assert (
        actual["mapping_status"]
        == actual["evidence_scope_status"]
        == actual["source_scope_status"]
        == "REVIEW_REQUIRED"
    )
    assert result["mapping_status_counts"] == {
        "READY": 0,
        "REVIEW_REQUIRED": 1,
        "BLOCKED": 0,
    }
    assert result["target_validation_counts"] == {"PASS": 1, "FAIL": 0}
    assert "Synthetic canonical topic 0" in content.presentation.focus_labels
    assert result["field_loss_counts"]["unmapped_or_changed"] == 0
    assert result["field_loss_counts"]["canonical_topic_labels_preserved"] == 1
    assert any(
        a["field"] == "topics/approved_uuid_mapping" for a in actual["mapping_reviews"]
    )
    assert (
        source == before
        and result["business_mutations"] == result["publication_side_effects"] == 0
    )
    assert result["go_no_go"] == "NO_GO_APPLY"
    assert result == policy.prepare_target(source, review)


def test_target_preparation_rejects_model_overflow_and_reports_unresolved_expressions():
    source, review = inputs()
    source["coaches"][0]["quotes"] = ["x" * 3001]
    result = policy.prepare_target(source, review)
    assert result["target_validation_counts"]["FAIL"] == 1
    assert result["coaches"][0]["mapping_status"] == "BLOCKED"
    assert "target_content" not in result["coaches"][0]
    assert any(
        a["field"] == "presentation/quote" for a in result["coaches"][0]["field_loss"]
    )
    source["coaches"][0]["quotes"] = []
    source["coaches"][0]["dynamic_text_expressions"] = [
        {"expression": "unknown.doNotEvaluate()", "line": 1}
    ]
    result = policy.prepare_target(source, review)
    assert any(
        a["field"] == "dynamic_text_expressions/0/unresolved"
        for a in result["coaches"][0]["mapping_reviews"]
    )
    assert result["coaches"][0]["mapping_status"] == "BLOCKED"


def test_environment_conditional_links_are_explicit_not_evaluated_or_flattened():
    links, issues = policy.target_links(
        [
            {
                "kind": "expression",
                "target": 'import.meta.env.PUBLIC_REVIEW_MODE === "true"\n ? "https://example.invalid/preview" : "https://example.invalid/production"',
                "label": "Synthetic",
            }
        ]
    )
    assert not issues
    assert links[0]["preview_url"] != links[0]["production_url"]
    links, issues = policy.target_links(
        [{"kind": "expression", "target": "call.arbitraryCode()", "label": "Synthetic"}]
    )
    assert not links and issues == ["external_links/0/unresolved_expression"]


def test_target_new_families_remain_inactive_and_unread_details_are_not_invented():
    source, review = inputs()
    review["new_offering_families"] = [
        {
            "key": "family/synthetic",
            "coach_key": "coach/one",
            "title": "Synthetic family",
            "target_group": "Synthetic teams",
            "boundary_ref": "synthetic:boundary",
            "excluded_services": ["therapy"],
            "service_domains": ["training"],
            "module_count": 6,
            "formats": [
                {
                    "key": "synthetic/day",
                    "label": "Synthetic day",
                    "kind": "workshop",
                    "clock_window": "10:00-16:30",
                    "source_status": "SOURCE_REPLACEMENT_REQUIRED",
                    "confirmed_ref": "synthetic:cross-reference",
                    "detail_fields": None,
                }
            ],
            "options": [
                {
                    "key": "community",
                    "kind": "optional_add_on",
                    "label": "Synthetic community",
                }
            ],
        }
    ]
    result = policy.prepare_target(source, review)
    candidate = result["coaches"][0]["target_content"]
    assert candidate["offering_families"][0]["active"] is False
    assert candidate["offering_families"][0]["variants"][0]["kind"] == "add_on"
    assert candidate["offerings"][0]["family_key"] == "family/synthetic"
    assert (
        candidate["offerings"][0]["active"] is False
        and candidate["offerings"][0]["program_modules"] == []
    )
    assert candidate["offerings"][0]["duration"]["clock_start"] == "10:00"
    assert candidate["offering_families"][0]["boundaries"] == []
    assert any(
        a["field"].endswith("excluded_services_public_text")
        for a in result["coaches"][0]["mapping_reviews"]
    )
    assert (
        result["new_offering_families"][0]["protected_source_status"]
        == "REVIEW_REQUIRED"
    )


def test_target_audit_never_classifies_unknown_fields_or_lost_values_as_mapped():
    source, review = inputs()
    source["coaches"][0]["new_unknown_field"] = "must not disappear"
    with pytest.raises(ValueError, match="FIELD_LOSS"):
        policy.prepare_target(source, review)
    source, review = inputs()
    source["coaches"][0]["source_identity"][
        "new_unknown_nested_field"
    ] = "must not disappear"
    result = policy.prepare_target(source, review)
    assert result["coaches"][0]["mapping_status"] == "BLOCKED"
    assert {
        "field": "source_identity/new_unknown_nested_field",
        "classification": "unmapped_or_changed",
    } in result["coaches"][0]["source_field_audit"]
    source, review = inputs()
    content, _ = policy.target_candidate(
        source["coaches"][0],
        review["coaches"]["synthetic"],
        topic_catalogue={t["id"]: t for t in source["topics"]},
    )
    damaged = content.model_copy(update={"display_name": "Incorrect output"})
    audit = policy.source_target_audit(
        source["coaches"][0],
        review["coaches"]["synthetic"],
        damaged,
        {t["id"]: t for t in source["topics"]},
    )
    assert {"field": "name", "classification": "unmapped_or_changed"} in audit
