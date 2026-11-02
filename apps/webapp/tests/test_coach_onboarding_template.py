"""Offline worksheet contract: complete typed shapes, no real intake or consent."""

from copy import deepcopy
import json
from pathlib import Path
from typing import get_origin

import pytest
from pydantic import ValidationError

from competence_hub_api.portal.coach_import import CoachTargetImportRecord
from competence_hub_api.portal.coach_registry import Asset, Offering, ProfileContent
from competence_hub_api.portal.coach_target import (
    Boundary,
    Duration,
    ObjectEvidenceInput,
    OfferingFamily,
    Presentation,
    PublicCard,
    PublicLink,
    PublicRole,
    PublicSection,
    Qualification,
    Variant,
)
from competence_hub_api.web.coach_registry import RevisionRequest

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "docs/content/coach-onboarding-template.json"
MODELS = {
    "public_role": PublicRole,
    "qualification": Qualification,
    "offering_family": OfferingFamily,
    "offering": Offering,
    "variant": Variant,
    "duration": Duration,
    "boundary": Boundary,
    "asset": Asset,
    "presentation": Presentation,
    "public_section": PublicSection,
    "public_card": PublicCard,
    "public_link": PublicLink,
    "object_evidence": ObjectEvidenceInput,
}
REVIEW_GATES = {
    "identity_authorization",
    "source_access_authorization",
    "privacy_review",
    "content_scope_review",
    "taxonomy_review",
    "portrait_bytes_verified",
    "runtime_authorization",
}
APPROVALS = {"content_review", "person_consent", "preview", "production"}
ENVIRONMENTS = {"preview", "production"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate worksheet key: {key}"
        result[key] = value
    return result


@pytest.fixture
def worksheet():
    return json.loads(
        TEMPLATE.read_text(encoding="utf-8"), object_pairs_hook=unique_object
    )


def leaves(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, (*path, key))
    elif isinstance(value, list):
        assert value == [], f"Prefilled worksheet collection: {path}"
    else:
        yield path, value


def assert_blank_values(value):
    constants = {
        ("schema_version",): 1,
        ("document_type",): "coach_onboarding_review_worksheet",
        ("directly_importable",): False,
        ("profile", "target_version"): 1,
        ("item_templates", "qualification", "public"): False,
        ("item_templates", "qualification", "verification_state"): "unknown",
        ("item_templates", "offering", "bookable"): False,
        ("item_templates", "object_evidence", "status"): "unknown",
    }
    for gate in REVIEW_GATES:
        constants[("review", gate)] = "unknown"
    for kind in APPROVALS:
        constants[("revision_approvals", kind, "status")] = "unknown"
    for environment in ENVIRONMENTS:
        for key, default in (
            ("decision", "unknown"),
            ("publish_requested", False),
            ("release_approved", False),
        ):
            constants[("publication_review", environment, key)] = default
    for path, actual in leaves(value):
        expected = constants.get(path)
        assert (
            type(actual) is type(expected) and actual == expected
        ), f"Nonblank or unsafe worksheet value: {path}"


def test_worksheet_sections_are_complete_and_explicit(worksheet):
    assert set(worksheet) == {
        "schema_version",
        "document_type",
        "directly_importable",
        "identity",
        "review",
        "submission",
        "profile",
        "topic_review",
        "object_evidence",
        "revision_approvals",
        "publication_review",
        "item_templates",
    }
    assert worksheet["directly_importable"] is False
    assert set(worksheet["identity"]) == {
        "intent",
        "existing_coach_id",
        "duplicate_check_reference",
    }
    assert set(worksheet["submission"]) == {
        "coach_id",
        "revision_id",
        "expected_version",
        "status",
    }
    assert set(worksheet["review"]) == REVIEW_GATES | {"source_reference"}
    assert set(worksheet["profile"]) == set(ProfileContent.model_fields)
    assert worksheet["profile"]["target_version"] == 1
    assert set(worksheet["item_templates"]) == set(MODELS) | {"topic_review"}
    assert set(worksheet["item_templates"]["topic_review"]) == {
        "canonical_topic_id",
        "canonical_label",
        "categories",
        "review_reference",
    }
    assert worksheet["topic_review"] == []
    assert worksheet["object_evidence"] == []


@pytest.mark.parametrize("name,model", MODELS.items())
def test_repeatable_shapes_cover_all_current_typed_fields(worksheet, name, model):
    assert set(worksheet["item_templates"][name]) == set(model.model_fields)


@pytest.mark.parametrize("name,model", [("profile", ProfileContent), *MODELS.items()])
def test_blank_field_shapes_distinguish_collections_from_open_scalars(
    worksheet, name, model
):
    values = (
        worksheet["profile"] if name == "profile" else worksheet["item_templates"][name]
    )
    for field, definition in model.model_fields.items():
        if get_origin(definition.annotation) is tuple:
            assert values[field] == []
        else:
            assert not isinstance(values[field], (dict, list))


def test_review_and_publication_start_without_any_approval(worksheet):
    assert set(worksheet["revision_approvals"]) == APPROVALS
    for approval in worksheet["revision_approvals"].values():
        assert approval == {"status": "unknown", "evidence_ref": None}
    assert set(worksheet["publication_review"]) == ENVIRONMENTS
    for review in worksheet["publication_review"].values():
        assert review == {
            "decision": "unknown",
            "publish_requested": False,
            "release_approved": False,
        }
    assert worksheet["item_templates"]["asset"]["scopes"] == []
    evidence = worksheet["item_templates"]["object_evidence"]
    for field in (
        "subject_type",
        "subject_key",
        "subject_hash",
        "kind",
        "environment",
        "scope",
        "evidence_reference",
        "approved_by",
        "approved_at",
        "approved_on",
    ):
        assert evidence[field] is None


def test_universal_worksheet_has_no_personal_or_operational_prefills(worksheet):
    # A path-specific constant allowlist also rejects names, UUIDs, dates, hashes,
    # paths, invented labels and claims, rather than checking a few known names.
    assert_blank_values(worksheet)


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("profile", "display_name", "Synthetic person"),
        ("profile", "competencies", ["Synthetic claim"]),
        ("submission", "coach_id", "00000000-0000-4000-8000-000000000001"),
        ("production", "decision", "approved"),
        ("production", "release_approved", True),
        ("evidence", "approved_on", "2026-01-01"),
        ("evidence", "subject_hash", "a" * 64),
        ("asset", "reference", "images/coaches/synthetic.webp"),
    ],
)
def test_blank_guard_detects_accidental_prefills(worksheet, section, key, value):
    changed = deepcopy(worksheet)
    target = {
        "profile": changed["profile"],
        "submission": changed["submission"],
        "production": changed["publication_review"]["production"],
        "evidence": changed["item_templates"]["object_evidence"],
        "asset": changed["item_templates"]["asset"],
    }[section]
    target[key] = value
    with pytest.raises(AssertionError):
        assert_blank_values(changed)


@pytest.mark.parametrize(
    "model", [ProfileContent, RevisionRequest, CoachTargetImportRecord]
)
def test_worksheet_is_not_an_api_or_import_payload(worksheet, model):
    with pytest.raises(ValidationError):
        model.model_validate(worksheet)


def test_empty_profile_requires_real_reviewed_input_before_submission(worksheet):
    with pytest.raises(ValidationError):
        ProfileContent.model_validate(worksheet["profile"])
