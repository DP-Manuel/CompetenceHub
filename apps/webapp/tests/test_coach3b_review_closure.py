from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import socket
import sys
import uuid

import pytest

from test_coach3b_preparation import ROOT, inputs as base_inputs

spec = importlib.util.spec_from_file_location(
    "coach3b_review_closure", ROOT / "scripts/coach3b_review_closure.py"
)
closure = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = closure
spec.loader.exec_module(closure)


def inputs():
    source, review = base_inputs()
    review["source_snapshot_sha256"] = "a" * 64
    return source, review


def run(source=None, review=None):
    if source is None:
        source, review = inputs()
    return closure._evaluate_review(source, review, dict(closure.DOCUMENT_HASHES))


def family_inputs():
    source, review = inputs()
    record = source["coaches"][0]
    record["profilePath"] = "coaches/guelcan-elmas-brandes"
    record["profile_path"] = "/coaches/guelcan-elmas-brandes/"
    record["source_identity"]["source_key"] = "coach/guelcan-elmas-brandes"
    review["coaches"]["guelcan-elmas-brandes"] = review["coaches"].pop("synthetic")
    review["coaches"]["guelcan-elmas-brandes"]["project_evidence"][
        "production"
    ] = "APPROVED"
    review["new_offering_families"] = [
        {
            "key": "family/business-balance",
            "coach_key": "coach/guelcan-elmas-brandes",
            "title": "Synthetic family",
            "target_group": "Synthetic teams",
            "boundary_ref": "synthetic:scope",
            "service_domains": ["coaching", "training"],
            "excluded_services": [
                "psychotherapy",
                "medical_treatment",
                "legal_advice",
                "tax_advice",
            ],
            "module_count": 6,
            "options": [
                {
                    "key": "community",
                    "kind": "optional_add_on",
                    "label": "Synthetic community",
                }
            ],
            "formats": [
                {
                    "key": "synthetic/day",
                    "label": "Synthetic day",
                    "kind": "workshop",
                    "source_status": "SOURCE_REPLACEMENT_REQUIRED",
                    "detail_fields": None,
                    "confirmed_ref": "synthetic:cross-reference",
                    "clock_window": "10:00-16:30",
                },
                {
                    "key": "synthetic/program",
                    "label": "Synthetic six weeks",
                    "kind": "coaching",
                    "weeks": 6,
                    "sessions_per_week": 1,
                    "session_minutes": 60,
                    "delivery_mode": "LIVE_UNSPECIFIED_OR_ONLINE",
                    "delivery_label": "online oder live",
                    "standalone_or_extension": True,
                    "source_status": "READY",
                    "confirmed_ref": "synthetic:program",
                },
            ],
            "offering_content_approval": "APPROVED",
            "public_copy_approval": "APPROVED",
            "publication_scopes": ["preview", "production"],
            "approval_reference": "synthetic:approval",
        }
    ]
    review["source_quality"] = [
        {"key": "synthetic-replacement", "status": "SOURCE_REPLACEMENT_REQUIRED"}
    ]
    return source, review


def test_missing_optional_portrait_offers_and_historical_originals_do_not_block():
    result = run()
    assert result["mapping_status_counts"] == {
        "READY": 1,
        "REVIEW_REQUIRED": 0,
        "BLOCKED": 0,
    }
    row = result["coaches"][0]
    assert row["content"]["assets"] == row["content"]["offerings"] == []
    assert result["counts_conditional_on_empty_target"]["production_scope_unknown"] == 1
    assert all(
        e["approved_at"] is None
        and e["basis"]["original_personal_consent_at"] is None
        and e["basis"]["original_personal_consent_by"] is None
        for e in row["evidence_plan"]
    )
    assert all(a["historical_at"] is None for a in row["attestation_plan"])
    assert not result["decisions_required_from_manuel"]


def test_preview_approval_never_escalates_unknown_production():
    result = run()
    row = result["coaches"][0]
    assert {e["environment"] for e in row["evidence_plan"]} == {"preview"}
    assert row["projection_production"] is None
    assert result["counts_conditional_on_empty_target"]["preview_publications"] == 1
    assert result["counts_conditional_on_empty_target"]["production_publications"] == 0


@pytest.mark.parametrize("subject", ["profile", "portrait", "preview"])
def test_missing_documented_required_rights_remain_review_required(subject):
    source, review = inputs()
    if subject == "portrait":
        source["coaches"][0]["asset"] = {
            "reference": "images/coaches/synthetic.webp",
            "sha256": "a" * 64,
            "alt_text": "Synthetic portrait",
            "source": "apps/website/public/images/coaches/synthetic.webp",
        }
        source["coaches"][0]["image"] = "images/coaches/synthetic.webp"
    review["coaches"]["synthetic"]["project_evidence"][subject] = "UNKNOWN"
    result = run(source, review)
    assert result["mapping_status_counts"]["REVIEW_REQUIRED"] == 1
    assert result["go_no_go"] == "CONDITIONAL_NO_GO"
    assert len(result["decisions_required_from_manuel"]) == 1
    assert result["counts_conditional_on_empty_target"]["preview_publications"] == 0


def test_guelcan_confirmed_short_copy_ready_without_missing_optional_details():
    source, review = family_inputs()
    result = run(source, review)
    row = result["coaches"][0]
    assert row["mapping_status"] == "READY"
    assert row["replacement_sources"] == "OPTIONAL_FOR_APPROVED_SHORT_COPY"
    assert row["content"]["offering_families"][0]["active"]
    offers = row["content"]["offerings"]
    assert len(offers) == 2 and all(o["active"] and not o["bookable"] for o in offers)
    assert offers[1]["program_modules"] == []
    assert offers[1]["delivery_mode"] == "live_unspecified"
    assert offers[1]["delivery_label"] == "online oder live"
    assert offers[0]["description"] is None
    assert {e["environment"] for e in row["evidence_plan"]} == {"preview", "production"}
    assert row["content"]["offering_families"][0]["boundaries"][0][
        "excluded_services"
    ] == ["psychotherapy", "medical_treatment", "legal_advice", "tax_advice"]
    public = json.dumps(row["projection_preview"], ensure_ascii=False)
    for forbidden in (
        "synthetic:program",
        "synthetic:scope",
        "evidence_reference",
        "internal_note",
        "price",
        "protected_source_reference",
    ):
        assert forbidden not in public
    assert (
        result["would_keep_internal"]["prices"] == "INTERNAL_UNCONFIRMED_NOT_IMPORTED"
    )
    assert (
        result["would_keep_internal"]["protected_workshop_content"]
        == "EXCLUDED_NOT_IMPORTED"
    )


@pytest.mark.parametrize(
    "field", ["public_copy_approval", "offering_content_approval", "publication_scopes"]
)
def test_profile_approval_cannot_replace_new_offering_copy_or_scope_rights(field):
    source, review = family_inputs()
    review["new_offering_families"][0][field] = (
        ["preview"] if field == "publication_scopes" else "UNKNOWN"
    )
    result = run(source, review)
    assert result["mapping_status_counts"]["REVIEW_REQUIRED"] == 1
    assert result["coaches"][0]["evidence_plan"] == []


def test_therapy_source_mention_kept_separate_and_nonbookable_not_lost():
    source, review = inputs()
    source["coaches"][0]["offerings"] = [
        {
            "key": "weitere/1",
            "title": "Synthetic psychotherapy source mention",
            "source_group": "weitere",
            "kind": None,
            "service_domain": "psychotherapy",
            "active": False,
        }
    ]
    result = run(source, review)
    row = result["coaches"][0]
    assert row["mapping_status"] == "READY"
    assert row["content"]["offerings"][0]["service_domains"] == ["psychotherapy"]
    assert not row["content"]["offerings"][0]["bookable"]
    assert row["projection_preview"]["offerings"] == []
    assert "Synthetic psychotherapy source mention" in json.dumps(
        row["projection_preview"]
    )
    assert not row["content"]["offering_families"]


def test_evidence_subject_changes_and_document_changes_fail_closed():
    source, review = inputs()
    first = run(source, review)["coaches"][0]
    source["coaches"][0]["credentials"][0] = "Changed synthetic degree"
    second = run(source, review)["coaches"][0]

    def qhash(row):
        return next(
            e["candidate_subject_sha256"]
            for e in row["evidence_plan"]
            if e["subject_type"] == "qualification"
        )

    assert qhash(first) != qhash(second)
    with pytest.raises(ValueError, match="documentary evidence changed"):
        closure.close_review(
            source, review, {**closure.DOCUMENT_HASHES, closure.MATRIX: "0" * 64}
        )
    assert all(
        "subject_hash" not in e and e["binding_stage"].startswith("LOGICAL_REVIEW_ONLY")
        for e in first["evidence_plan"]
    )
    assert first["content"]["topic_ids"] == []


def test_pure_batch_closure_has_no_io_database_uuid_writes_or_input_changes(
    monkeypatch,
):
    source, review = family_inputs()
    before = deepcopy((source, review))

    def forbidden(*args, **kwargs):
        raise AssertionError("review closure is pure")

    for name in ("read_bytes", "write_bytes", "write_text"):
        monkeypatch.setattr(Path, name, forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(uuid, "uuid4", forbidden)
    first = run(source, review)
    assert first == run(source, review)
    assert (source, review) == before
    assert (
        first["business_mutations"] == 0
        and first["database_snapshot"] == "NOT_READ"
        and first["uuid_allocation"] is False
    )


def test_canonical_topic_aliases_not_fuzzy_and_all_topics_not_persisted():
    source, review = inputs()
    source["topics"][1]["label"] = source["topics"][0]["label"]
    with pytest.raises(ValueError, match="ambiguous"):
        run(source, review)
    result = run()
    assert result["all_topics"] == "COMPUTED_NOT_STORED"
    assert all(
        "uuid" not in t and t["resolution"].startswith("MATCH_ONLY")
        for t in result["topic_rules"]
    )


def test_unknown_dynamic_expression_not_silently_closed():
    source, review = inputs()
    source["coaches"][0]["dynamic_text_expressions"] = [
        {"expression": "unknown.call()", "line": 1}
    ]
    result = run(source, review)
    assert result["coaches"][0]["remaining_reviews"]
    assert result["mapping_status_counts"]["READY"] == 0


def test_missing_required_field_fails_typed_validation():
    source, review = inputs()
    source["coaches"][0]["name"] = ""
    with pytest.raises(ValueError):
        run(source, review)


def test_nine_coach_mapping_is_pure_and_does_not_allocate_uuid(monkeypatch):
    source, review = inputs()
    base = source["coaches"].pop()
    decisions = review["coaches"].pop("synthetic")
    for index in range(9):
        record = deepcopy(base)
        slug = f"synthetic-{index}"
        record.update(
            profilePath="coaches/" + slug, profile_path="/coaches/" + slug + "/"
        )
        record["source_identity"]["source_key"] = "coach/" + slug
        source["coaches"].append(record)
        review["coaches"][slug] = deepcopy(decisions)

    def forbidden(*args, **kwargs):
        raise AssertionError("no I/O or UUIDs in review")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(uuid, "uuid4", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    result = run(source, review)
    assert result["mapping_status_counts"] == {
        "READY": 9,
        "REVIEW_REQUIRED": 0,
        "BLOCKED": 0,
    }
    assert len({r["source_identity"]["source_key"] for r in result["coaches"]}) == 9
    assert result["uuid_allocation"] is False and result["business_mutations"] == 0


def test_public_label_parity_is_against_source_not_against_itself():
    source, review = inputs()
    content, _, _ = closure.completed_content(
        source["coaches"][0],
        review["coaches"]["synthetic"],
        [],
        {t["id"]: t for t in source["topics"]},
    )
    q = content.qualifications[0].model_copy(
        update={"public_display_label": "Incorrect visible title"}
    )
    content = content.model_copy(update={"qualifications": (q,)})
    checked = closure.parity(
        source["coaches"][0],
        review["coaches"]["synthetic"],
        content,
        {t["id"]: t for t in source["topics"]},
    )
    assert checked["status"] == "FAIL"
    assert any(
        c["field"] == "public_qualification/credential/1"
        for c in checked["unintended_changes"]
    )


def test_callable_closure_rejects_modified_input_even_with_claimed_old_hash():
    source, review = inputs()
    source["coaches"][0]["credentials"][
        0
    ] = "Changed qualification must not receive real-input GO"
    review["source_snapshot_sha256"] = closure.SOURCE_HASH
    with pytest.raises(ValueError, match="provenance changed"):
        closure.close_review(source, review, dict(closure.DOCUMENT_HASHES))
    result = run(source, review)
    assert result["go_no_go"] == "POLICY_EVALUATION_ONLY_NO_APPROVAL"


def test_orphaned_family_cannot_disappear_from_ready_counts():
    source, review = family_inputs()
    review["new_offering_families"][0]["coach_key"] = "coach/unknown"
    with pytest.raises(ValueError, match="family ownership"):
        run(source, review)
