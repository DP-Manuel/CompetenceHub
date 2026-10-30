"""Synthetic policy fixtures cannot acquire the pinned real-input approval."""

import builtins
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime
import importlib.util
from pathlib import Path
import socket
import sys
import uuid

import pytest

from competence_hub_api.portal.coach_import import validate_records
from competence_hub_api.portal.coach_registry import (
    Approval,
    CoachAggregate,
    ObjectEvidence,
    ProfileRevision,
    Publication,
    TopicSnapshot,
    public_projection,
)
from competence_hub_api.portal.coach_target import subjects
from test_coach3b_review_closure import ROOT, closure, family_inputs, inputs, run

spec = importlib.util.spec_from_file_location(
    "coach3b_real_manifest", ROOT / "scripts/coach3b_real_manifest.py"
)
manifest_api = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = manifest_api
spec.loader.exec_module(manifest_api)

NOW = datetime(2026, 10, 30, tzinfo=UTC)
COMMIT = "a" * 40


def policy_fixture(*, family=False, portrait=False, two_topics=False):
    source, review = family_inputs() if family else inputs()
    assets = {}
    if two_topics:
        source["coaches"][0]["topics"] = ["topic-1", "topic-0"]
    if portrait:
        import hashlib

        reference = "images/coaches/synthetic.webp"
        assets[reference] = b"synthetic portrait bytes"
        source["coaches"][0]["asset"] = {
            "reference": reference,
            "sha256": hashlib.sha256(assets[reference]).hexdigest(),
            "alt_text": "Synthetic portrait",
            "source": "apps/website/public/" + reference,
        }
        source["coaches"][0]["image"] = reference
        slug = source["coaches"][0]["profilePath"].split("/")[-1]
        review["coaches"][slug]["project_evidence"]["portrait"] = "APPROVED"
    report = run(source, review)
    assert report["go_no_go"] == "POLICY_EVALUATION_ONLY_NO_APPROVAL"
    catalogue = [
        manifest_api.RuntimeTopicSnapshot(
            uuid.UUID(int=index + 1), topic["name"], tuple(topic["categories"]), True
        )
        for index, topic in enumerate(report["topic_rules"])
    ]
    return report, catalogue, assets


def bind_policy(report, catalogue, assets):
    return manifest_api._bind_review(report, catalogue, assets, now=NOW)


def unapproved_envelope(report):
    """A caller's claimed hash and resealing must never grant real approval."""
    result = {
        "coaches": deepcopy(report["coaches"]),
        "topic_rules": deepcopy(report["topic_rules"]),
        "counts": deepcopy(report["counts_conditional_on_empty_target"]),
        "review_context": {
            key: deepcopy(value)
            for key, value in report.items()
            if key not in manifest_api.REVIEW_COLLECTIONS
        },
        "technical": {"git_commit": COMMIT, "generated_at": NOW.isoformat()},
        "target": dict(manifest_api.TARGET),
        "review_report_sha256": manifest_api.APPROVED_REVIEW_SHA256,
    }
    result["manifest_sha256"] = closure.digest(result)
    return result


def test_exact_approved_review_hash_and_target_are_fixed_not_caller_metadata():
    assert manifest_api.APPROVED_REVIEW_SHA256 == (
        "7d79a9d1b91d959459e2c3a525a6c5763024dc15656c6f5890dfc89562dd0f59"
    )
    assert manifest_api.TARGET == {
        "database": "competence_hub_staging",
        "schema": "competence_hub",
        "environment": "staging",
        "import_contract": "coach-import-v2",
    }
    report, _, _ = policy_fixture()
    before = deepcopy(report)
    with pytest.raises(ValueError, match="exact approved review hash"):
        manifest_api.build_manifest(report, git_commit=COMMIT, generated_at=NOW)
    assert report == before


@pytest.mark.parametrize(
    "mutation", ["content", "rights", "evidence", "topic", "counts"]
)
def test_rehashing_business_mutations_or_claimed_approval_never_authorizes(mutation):
    report, catalogue, assets = policy_fixture()
    value = unapproved_envelope(report)
    row = value["coaches"][0]
    if mutation == "content":
        row["content"]["display_name"] = "Changed person"
        row["candidate_content_sha256"] = closure.digest(row["content"])
    elif mutation == "rights":
        row["rights"]["production"] = "APPROVED"
    elif mutation == "evidence":
        row["evidence_plan"][0]["approved_on"] = "2026-10-30"
    elif mutation == "topic":
        value["topic_rules"][0]["categories"] = ["karrierecoaching"]
    else:
        value["counts"] = dict(manifest_api.EXPECTED_COUNTS)
    value["reviewed_payload_sha256"] = closure.digest(
        {
            key: value[key]
            for key in ("coaches", "topic_rules", "counts", "review_context")
        }
    )
    value["manifest_sha256"] = closure.digest(
        {key: item for key, item in value.items() if key != "manifest_sha256"}
    )
    with pytest.raises(ValueError, match="exact approved review hash"):
        manifest_api.verify_manifest(value)
    with pytest.raises(ValueError, match="exact approved review hash"):
        manifest_api.bind_manifest(value, catalogue, assets, now=NOW)


def test_policy_binding_uses_v2_typed_sections_and_existing_object_keys():
    report, catalogue, assets = policy_fixture(family=True, portrait=True)
    records, contract = bind_policy(report, catalogue, assets)
    assert contract.version == "coach-import-v2"
    assert {rule.topic_id for rule in contract.topics} == {
        topic.id for topic in catalogue
    }
    row, record = report["coaches"][0], records[0]
    assert record["expected_coach_id"] is None
    assert record["profile"]["topic_ids"] == []
    for section, source in (
        ("roles", "public_roles"),
        ("qualifications", "qualifications"),
        ("offering_families", "offering_families"),
        ("boundaries", "boundaries"),
    ):
        assert [item["key"] for item in record[section]] == [
            item["key"] for item in row["content"][source]
        ]
    assert [item["key"] for item in record["offerings"]] == [
        item["key"] for item in row["content"]["offerings"]
    ]
    assert record["presentation"] == row["content"]["presentation"]
    assert record["publication"]["lifecycle"] == "active"
    assert record["publication"]["published"] == ["preview", "production"]


def test_actual_normalized_topic_subject_hashes_and_unknown_originals_are_preserved():
    report, catalogue, assets = policy_fixture(family=True, portrait=True)
    # Force normalization of a literal field; approval is still synthetic only.
    row = report["coaches"][0]
    row["content"]["short_intro"] = "  Synthetic   normalized intro  "
    row["candidate_content_sha256"] = closure.digest(row["content"])
    records, contract = bind_policy(report, catalogue, assets)
    result = validate_records(
        records, contract, {topic.id: topic for topic in catalogue}, assets, now=NOW
    )
    assert not result.issues
    prepared = result.records[0]
    assert prepared.content.short_intro == "Synthetic normalized intro"
    hashes = subjects(prepared.content, [catalogue[0]])
    for evidence in records[0]["object_evidence"]:
        assert (
            evidence["subject_hash"]
            == hashes[evidence["subject_type"], evidence["subject_key"]]
        )
        assert evidence["approved_at"] is None
        assert evidence["approved_on"] == "2026-10-29"
        assert "basis" not in evidence and "candidate_subject_sha256" not in evidence
    profile_evidence = next(
        e for e in records[0]["object_evidence"] if e["subject_type"] == "profile"
    )
    candidate = next(
        e for e in row["evidence_plan"] if e["key"] == profile_evidence["key"]
    )
    assert profile_evidence["subject_hash"] != candidate["candidate_subject_sha256"]
    for original, current in zip(
        row["attestation_plan"], records[0]["publication"]["evidence"]
    ):
        assert current["source"] == original["reference"]
        assert current["historical_at"] is None
    assert all(
        e["basis"]["original_personal_consent_at"] is None for e in row["evidence_plan"]
    )
    assert all(
        e["basis"]["original_personal_consent_by"] is None for e in row["evidence_plan"]
    )


def test_preview_rights_do_not_escalate_to_production_or_create_history():
    report, catalogue, assets = policy_fixture(portrait=True)
    records, _ = bind_policy(report, catalogue, assets)
    record = records[0]
    assert record["publication"]["published"] == ["preview"]
    assert {e["environment"] for e in record["object_evidence"]} == {"preview"}
    assert {e["kind"] for e in record["publication"]["evidence"]} == {
        "content_review",
        "person_consent",
        "preview",
    }
    assert record["assets"][0]["content"]["scopes"] == ["preview"]
    assert all(e["approved_at"] is None for e in record["object_evidence"])


@pytest.mark.parametrize(
    "mutation",
    [
        "absent",
        "ambiguous",
        "inactive",
        "missing_active",
        "category",
        "duplicate_uuid",
        "fuzzy",
    ],
)
def test_match_only_rejects_unproven_or_ambiguous_existing_topics(mutation):
    report, catalogue, assets = policy_fixture()
    if mutation == "absent":
        catalogue.pop(0)
    elif mutation == "ambiguous":
        catalogue.append(replace(catalogue[0], id=uuid.UUID(int=100)))
    elif mutation == "inactive":
        catalogue[0] = replace(catalogue[0], active=False)
    elif mutation == "missing_active":
        topic = catalogue[0]
        catalogue[0] = TopicSnapshot(topic.id, topic.name, topic.categories)
    elif mutation == "category":
        catalogue[0] = replace(catalogue[0], categories=("karrierecoaching",))
    elif mutation == "duplicate_uuid":
        catalogue[1] = replace(catalogue[1], id=catalogue[0].id)
    else:
        catalogue[0] = replace(catalogue[0], name="Synthetic near-match topic")
    with pytest.raises(ValueError):
        bind_policy(report, catalogue, assets)


def test_match_only_uses_existing_curated_normalization_not_topic_allocation():
    report, catalogue, assets = policy_fixture()
    catalogue[0] = replace(
        catalogue[0], name=catalogue[0].name.upper().replace(" ", "-")
    )
    records, mapping = bind_policy(report, catalogue, assets)
    assert records and mapping.topics[0].topic_id == catalogue[0].id
    changed = list(catalogue)
    changed[0] = replace(changed[0], id=uuid.UUID(int=100))
    rebound, _ = bind_policy(report, changed, assets)
    first = next(
        e for e in records[0]["object_evidence"] if e["subject_type"] == "profile"
    )
    second = next(e for e in rebound[0]["object_evidence"] if e["key"] == first["key"])
    assert first["subject_hash"] != second["subject_hash"]


@pytest.mark.parametrize(
    "bad_assets", [{}, {"images/coaches/synthetic.webp": b"wrong"}]
)
def test_asset_bytes_are_required_and_hash_checked_without_reading_files(bad_assets):
    report, catalogue, _ = policy_fixture(portrait=True)
    with pytest.raises(ValueError, match="ASSET_MAPPING_REQUIRED"):
        bind_policy(report, catalogue, bad_assets)


def test_date_in_future_and_naive_clock_are_not_accepted():
    report, catalogue, assets = policy_fixture(family=True)
    with pytest.raises(ValueError, match="timezone-aware"):
        manifest_api._bind_review(
            report, catalogue, assets, now=NOW.replace(tzinfo=None)
        )
    report["coaches"][0]["evidence_plan"][0]["approved_on"] = "2026-10-31"
    with pytest.raises(ValueError, match="historical_date"):
        bind_policy(report, catalogue, assets)


def test_pure_policy_is_deterministic_without_io_uuid_allocation_or_input_mutation(
    monkeypatch,
):
    report, catalogue, assets = policy_fixture(family=True, portrait=True)
    before = deepcopy((report, catalogue, assets))

    def forbidden(*args, **kwargs):
        raise AssertionError("pure binder must not perform I/O or allocate UUIDs")

    for name in ("read_bytes", "read_text", "write_bytes", "write_text", "open"):
        monkeypatch.setattr(Path, name, forbidden)
    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(uuid, "uuid4", forbidden)
    first = bind_policy(report, catalogue, assets)
    assert first == bind_policy(report, list(reversed(catalogue)), assets)
    assert (report, catalogue, assets) == before
    first[0][0]["profile"]["display_name"] = "Local caller mutation"
    assert (report, catalogue, assets) == before


def runtime_projection(report, catalogue, assets):
    records, contract = bind_policy(report, catalogue, assets)
    by_id = {topic.id: topic for topic in catalogue}
    prepared = validate_records(records, contract, by_id, assets, now=NOW)
    assert not prepared.issues
    item = prepared.records[0]
    fixed_id = uuid.UUID(int=100)
    revision = ProfileRevision(
        fixed_id,
        1,
        item.content,
        fixed_id,
        NOW,
        status="submitted",
        topics=tuple(by_id[id] for id in reversed(item.content.topic_ids)),
        approvals=[
            Approval(e.kind, fixed_id, NOW, e.source)
            for e in item.source.publication.evidence
        ],
        object_evidence=[
            ObjectEvidence(uuid.UUID(int=index + 200), e, fixed_id, NOW)
            for index, e in enumerate(item.object_evidence)
        ],
    )
    coach = CoachAggregate(
        fixed_id,
        item.content.display_name,
        None,
        lifecycle="active",
        revisions=[revision],
        publications={
            env: Publication(fixed_id, "published", fixed_id, NOW)
            for env in item.source.publication.published
        },
    )
    return tuple(public_projection((coach,), env) for env in ("preview", "production"))


@pytest.mark.parametrize("family", [False, True])
def test_semantic_parity_matches_real_public_projection_and_independent_scopes(family):
    report, catalogue, assets = policy_fixture(
        family=family, portrait=True, two_topics=True
    )
    preview, production = runtime_projection(report, catalogue, assets)
    before = deepcopy((report, preview, production))
    manifest_api._verify_projection_rows(report, preview, production)
    assert len(preview["coaches"]) == 1
    assert len(production["coaches"]) == int(family)
    preview["coaches"][0]["topics"].reverse()
    manifest_api._verify_projection_rows(report, preview, production)
    preview["coaches"][0]["topics"].reverse()
    assert (report, preview, production) == before


@pytest.mark.parametrize(
    "mutation", ["missing", "extra", "content", "private", "environment", "production"]
)
def test_semantic_parity_rejects_field_loss_changes_leaks_and_production_escalation(
    mutation,
):
    report, catalogue, assets = policy_fixture(portrait=True)
    preview, production = runtime_projection(report, catalogue, assets)
    if mutation == "missing":
        preview["coaches"].clear()
    elif mutation == "extra":
        preview["coaches"].append(deepcopy(preview["coaches"][0]))
    elif mutation == "content":
        preview["coaches"][0]["qualifications"][0]["label"] = "Unreviewed qualification"
    elif mutation == "private":
        preview["coaches"][0]["internal_note"] = "Not public"
    elif mutation == "environment":
        preview["environment"] = "production"
    else:
        production["coaches"] = deepcopy(preview["coaches"])
    with pytest.raises(ValueError, match="parity mismatch"):
        manifest_api._verify_projection_rows(report, preview, production)


def test_asset_loader_reads_only_fixed_reviewed_public_paths_and_checks_hash(
    monkeypatch,
):
    import hashlib

    raw = b"synthetic bytes, not actual approved source material"
    reference = "images/coaches/christian-galvano.webp"
    rows = [
        {
            "content": {
                "assets": [
                    {
                        "reference": reference,
                        "sha256": hashlib.sha256(raw).hexdigest(),
                    }
                ]
            }
        }
    ]
    paths = []

    def read(path):
        paths.append(path)
        return raw

    monkeypatch.setattr(Path, "read_bytes", read)
    assert manifest_api._load_assets(ROOT, rows) == {reference: raw}
    assert paths == [ROOT / "apps/website/public/images/coaches/christian-galvano.webp"]
    rows[0]["content"]["assets"][0]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="asset hash mismatch"):
        manifest_api._load_assets(ROOT, rows)


@pytest.mark.parametrize(
    "reference",
    [
        "../private",
        "images/coaches/../../../private",
        "C:/private",
        "images/coaches/unreviewed.webp",
    ],
)
def test_unknown_asset_paths_are_rejected_before_read(reference, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("unapproved paths must not be read")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError, match="approved frozen public source"):
        manifest_api._load_assets(
            ROOT,
            [
                {
                    "content": {
                        "assets": [
                            {
                                "reference": reference,
                                "sha256": "0" * 64,
                            }
                        ]
                    }
                }
            ],
        )


def test_linked_asset_source_is_rejected_before_read(monkeypatch):
    original = Path.resolve
    target = ROOT / "apps/website/public/images/coaches/christian-galvano.webp"

    def resolved(path, *args, **kwargs):
        if path == target:
            return ROOT / ".tmp/redirected-asset"
        return original(path, *args, **kwargs)

    def forbidden(*args, **kwargs):
        raise AssertionError("linked paths must not be read")

    monkeypatch.setattr(Path, "resolve", resolved)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError, match="traverse links"):
        manifest_api._load_assets(
            ROOT,
            [
                {
                    "content": {
                        "assets": [
                            {
                                "reference": "images/coaches/christian-galvano.webp",
                                "sha256": "0" * 64,
                            }
                        ]
                    }
                }
            ],
        )


def test_public_asset_and_parity_helpers_require_real_approval_before_any_io(
    monkeypatch,
):
    report, _, _ = policy_fixture()
    envelope = unapproved_envelope(report)

    def forbidden(*args, **kwargs):
        raise AssertionError("approval must precede asset I/O")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError, match="exact approved review hash"):
        manifest_api.load_asset_bytes(ROOT, envelope)
    with pytest.raises(ValueError, match="exact approved review hash"):
        manifest_api.verify_projection_parity(envelope, {}, {})
