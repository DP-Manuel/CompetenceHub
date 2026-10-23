from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from pydantic import ValidationError

from scripts.coach_import_fixture import NOW, fixture
from competence_hub_api.portal.coach_import import (
    ImportMappingContract,
    SourceEvidence,
    validate_records,
)
from competence_hub_api.portal.postgres_coach_import import (
    ImportBinding,
    ImportSnapshot,
    local_import_url,
    plan_records,
)
from competence_hub_api.portal.coach_registry import CoachAggregate, ProfileRevision


def validate(records=None, mapping=None, catalogue=None, assets=None):
    values, contract, topics, data = fixture()
    return validate_records(
        values if records is None else records,
        mapping or contract,
        topics if catalogue is None else catalogue,
        data if assets is None else assets,
        now=NOW,
    )


def test_fixture_maps_without_loss_or_taxonomy_mutation():
    values, contract, topics, _ = fixture()
    result = validate()
    assert not result.issues and len(result.records) == 4
    a, b, c, d = result.records
    assert len(a.content.topic_ids) == 3 and len(a.content.offerings) == 2
    assert (
        len(a.content.competencies) == 2
        and not b.content.assets
        and not b.content.offerings
    )
    assert c.source.boundaries[0].text in c.content.description
    assert not c.content.offerings[0].active and c.content.offerings[0].type == "other"
    for text in (*d.source.roles, *d.source.qualifications):
        assert text.text in d.content.professional_background
    assert not d.content.competencies
    assert len(topics) == 8 and sum(len(t.categories) for t in topics.values()) == 18
    assert len(set(c for t in topics.values() for c in t.categories)) == 3
    assert plan_records(result, ImportSnapshot()).report()["counts"]["CREATE"] == 4
    assert "Synthetic Coach Alpha" not in json.dumps(
        plan_records(result, ImportSnapshot()).report()
    )


@pytest.mark.parametrize(
    "variant",
    [
        "json_keys",
        "whitespace",
        "line_endings",
        "optional",
        "slug",
        "sets",
        "aliases",
        "technical",
    ],
)
def test_semantically_identical_inputs_have_identical_hashes(variant):
    records, mapping, topics, assets = fixture()
    records[1]["profile"]["description"] = "Synthetic café\nSecond line"
    before = validate(records)
    if variant == "json_keys":
        records = json.loads(json.dumps(records, sort_keys=True))
    elif variant == "whitespace":
        records[0]["profile"]["short_intro"] = "  Synthetic   introduction.  "
    elif variant == "line_endings":
        records[1]["profile"]["description"] = "Synthetic cafe\u0301\r\nSecond line"
    elif variant == "optional":
        records[0]["profile"]["academic_suffix"] = "  "
    elif variant == "slug":
        records[0]["profile"]["profile_path"] = "coaches/synthetic-alpha"
    elif variant == "sets":
        for key in ("topics", "competencies", "offerings"):
            records[0][key].reverse()
        mapping = mapping.model_copy(update={"topics": tuple(reversed(mapping.topics))})
    elif variant == "aliases":
        records[0]["topics"][1]["label"] = "stress Management"
        records[0]["topics"].append(deepcopy(records[0]["topics"][1]))
    else:
        records[0]["provenance"].update(
            observed_at=NOW.isoformat(), technical_revision="run-999"
        )
    after = validate_records(records, mapping, topics, assets, now=NOW)
    assert not before.issues and not after.issues
    assert [
        (r.source_hash, r.profile_hash, r.contract_hash) for r in before.records
    ] == [(r.source_hash, r.profile_hash, r.contract_hash) for r in after.records]


@pytest.mark.parametrize(
    "case,code",
    [
        ("identity", "IDENTITY_CONFLICT"),
        ("path", "PROFILE_PATH_CONFLICT"),
        ("unknown_topic", "TOPIC_CONFLICT"),
        ("alias", "TOPIC_CONFLICT"),
        ("category", "TOPIC_CONFLICT"),
        ("ambiguous", "TOPIC_CONFLICT"),
        ("role", "ROLE_MAPPING_REQUIRED"),
        ("qualification", "QUALIFICATION_MAPPING_REQUIRED"),
        ("private_qualification", "QUALIFICATION_MAPPING_REQUIRED"),
        ("boundary", "BOUNDARY_REVIEW_REQUIRED"),
        ("evidence", "PUBLICATION_EVIDENCE_REQUIRED"),
        ("future_date", "PUBLICATION_EVIDENCE_REQUIRED"),
        ("production", "PUBLICATION_EVIDENCE_REQUIRED"),
        ("asset", "ASSET_MAPPING_REQUIRED"),
        ("scope", "ASSET_MAPPING_REQUIRED"),
        ("unknown_field", "VALIDATION_ERROR"),
        ("parallel_topics", "VALIDATION_ERROR"),
        ("coerced_bool", "VALIDATION_ERROR"),
        ("coerced_order", "VALIDATION_ERROR"),
        ("empty_label", "VALIDATION_ERROR"),
    ],
)
def test_classified_fail_closed_mapping(case, code):
    records, mapping, topics, assets = fixture()
    if case == "identity":
        records[1]["source_identity"] = records[0]["source_identity"]
    elif case == "path":
        records[1]["profile"]["profile_path"] = records[0]["profile"]["profile_path"]
    elif case == "unknown_topic":
        records[0]["topics"][0]["reference"] = "not-curated"
    elif case == "alias":
        records[0]["topics"][0]["label"] = "Guessed meaning"
    elif case == "category":
        topics[mapping.topics[0].topic_id] = replace(
            topics[mapping.topics[0].topic_id], categories=("karrierecoaching",)
        )
    elif case == "ambiguous":
        mapping = mapping.model_copy(
            update={
                "topics": (
                    *mapping.topics,
                    mapping.topics[0].model_copy(update={"reference": "collision"}),
                )
            }
        )
    elif case in {"role", "qualification", "boundary"}:
        mapping = mapping.model_copy(update={case + "_mapping": "unmapped"})
    elif case == "private_qualification":
        records[3]["qualifications"][0]["visibility"] = "internal"
    elif case == "evidence":
        records[0]["publication"]["evidence"].pop()
    elif case == "future_date":
        records[0]["publication"]["evidence"][0][
            "historical_at"
        ] = "2099-01-01T00:00:00Z"
    elif case == "production":
        records[0]["publication"]["published"].append("production")
    elif case == "asset":
        assets.clear()
    elif case == "scope":
        records[0]["assets"][0]["content"]["scopes"] = ["production"]
    elif case == "unknown_field":
        records[0]["profile"]["invented_credential"] = "private payload never echoed"
    elif case == "parallel_topics":
        records[0]["profile"]["topic_ids"] = [str(mapping.topics[0].topic_id)]
    elif case == "coerced_bool":
        records[0]["offerings"][0]["content"]["active"] = "false"
    elif case == "coerced_order":
        records[0]["offerings"][0]["content"]["ordering"] = "2"
    else:
        records[0]["competencies"][0]["text"] = " "
    result = validate_records(records, mapping, topics, assets, now=NOW)
    assert code in {i.code for i in result.issues}
    report = plan_records(result, ImportSnapshot()).report()
    assert report["result"] == "CONFLICT" and report["business_mutations_planned"] == 0
    assert "private payload" not in json.dumps(report)


def test_same_name_is_not_identity_and_new_content_changes_fingerprint():
    records, *_ = fixture()
    records[1]["profile"]["display_name"] = records[0]["profile"]["display_name"]
    assert not validate(records).issues
    changed = deepcopy(records)
    changed[0]["profile"]["short_intro"] = "Changed synthetic introduction."
    assert (
        validate(changed).records[0].profile_hash
        != validate(records).records[0].profile_hash
    )


@pytest.mark.parametrize(
    "date,environment,kind",
    [
        ("2026-01-01T00:00:00", None, "content_review"),
        (None, None, "preview"),
        (None, "production", "preview"),
        (None, "preview", "person_consent"),
    ],
)
def test_evidence_never_infers_date_or_environment(date, environment, kind):
    with pytest.raises(ValidationError):
        SourceEvidence(
            key="a",
            kind=kind,
            environment=environment,
            source="synthetic:evidence",
            historical_at=date,
        )


def test_evidence_unknown_stays_null_and_offset_normalizes():
    assert (
        SourceEvidence(
            key="a", kind="content_review", source="synthetic:evidence"
        ).historical_at
        is None
    )
    a = SourceEvidence(
        key="a",
        kind="preview",
        environment="preview",
        source="synthetic:evidence",
        historical_at="2026-01-01T01:00:00+01:00",
    )
    assert a.historical_at.isoformat() == "2026-01-01T00:00:00+00:00"


def test_mapping_attestation_is_not_a_coerced_string():
    with pytest.raises(ValidationError):
        ImportMappingContract(attest_initial_publication="true")


@pytest.mark.parametrize(
    "change",
    [
        "55432",
        "localhost",
        "competence_hub_migrator",
        "other_db",
        "remote.invalid",
        "sslmode",
    ],
)
def test_operator_database_guard_rejects_every_nonowned_target(change):
    raw = "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55435/competence_hub_staging"
    replacements = {
        "55432": ("55435", "55432"),
        "localhost": ("127.0.0.1", "localhost"),
        "competence_hub_migrator": ("competence_hub_app", "competence_hub_migrator"),
        "other_db": ("competence_hub_staging", "other_db"),
        "remote.invalid": ("127.0.0.1", "remote.invalid"),
    }
    bad = (
        raw + "?sslmode=require"
        if change == "sslmode"
        else raw.replace(*replacements[change])
    )
    with pytest.raises(ValueError):
        local_import_url(bad)
    local_import_url(raw)


@pytest.mark.parametrize(
    "args,expected",
    [
        ([], "PASS"),
        (["dry-run"], "PASS"),
        (["apply"], "CONFLICT"),
        (["apply", "--synthetic-apply"], "CONFLICT"),
        (["dry-run", "--local-database"], "CONFLICT"),
    ],
)
def test_cli_safe_default_and_sanitized_reports(args, expected):
    env = {**os.environ, "PYTHONPATH": str(Path("src").resolve())}
    env.pop("COMPETENCE_HUB_COACH_IMPORT_LOCAL_DATABASE_URL", None)
    result = subprocess.run(
        [sys.executable, "scripts/coach-import.py", *args],
        env=env,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["result"] == expected
    assert result.returncode == (0 if expected == "PASS" else 1)
    assert (
        "postgresql" not in result.stdout
        and "Synthetic Coach Alpha" not in result.stdout
    )
    assert not result.stderr


@pytest.mark.parametrize(
    "case,expected",
    [
        ("no_op", "UNCHANGED"),
        ("metadata", "METADATA"),
        ("edit", "EDIT_DRAFT"),
        ("submitted", "REVISION"),
        ("abandoned", "REVISION"),
        ("version", "STATE_CONFLICT"),
        ("foreign_draft", "STATE_CONFLICT"),
        ("missing", "MISSING_ITEM_REVIEW_REQUIRED"),
        ("route_owner", "PROFILE_PATH_CONFLICT"),
    ],
)
def test_planner_respects_import_ownership_and_revision_state(case, expected):
    records, mapping, catalogue, assets = fixture()
    prepared = validate().records[0]
    coach = CoachAggregate(uuid4(), prepared.content.display_name, uuid4())
    revision = ProfileRevision(
        uuid4(),
        1,
        prepared.content,
        uuid4(),
        NOW,
        topics=tuple(catalogue[t] for t in prepared.content.topic_ids),
    )
    coach.revisions.append(revision)
    ledger = dict(
        profile_path=prepared.content.profile_path,
        source_content_hash=prepared.source_hash,
        profile_content_hash=prepared.profile_hash,
        mapping_contract_hash=prepared.contract_hash,
        publication_intent_hash=prepared.publication_hash,
        last_revision_id=revision.id,
        last_registry_version=coach.version,
    )
    binding = ImportBinding(coach, ledger, set(prepared.items))
    snapshot = ImportSnapshot(bindings={prepared.source.source_identity.key: binding})
    if case == "metadata":
        records[0]["provenance"]["source_ref"] = "synthetic:new-reference"
    elif case in {"edit", "submitted", "abandoned", "foreign_draft"}:
        records[0]["profile"]["short_intro"] = "Changed introduction"
        if case != "edit":
            revision.status = "abandoned" if case == "abandoned" else "submitted"
        if case == "foreign_draft":
            coach.revisions.append(
                ProfileRevision(uuid4(), 2, prepared.content, uuid4(), NOW)
            )
    elif case == "version":
        coach.version += 1
    elif case == "missing":
        records[0]["competencies"].pop()
    elif case == "route_owner":
        snapshot.paths[prepared.content.profile_path] = {uuid4()}
    plan = plan_records(
        validate_records(records[:1], mapping, catalogue, assets, now=NOW), snapshot
    )
    if expected.endswith("CONFLICT") or expected.endswith("REQUIRED"):
        assert expected in {i.code for i in plan.issues}
        assert plan.report()["business_mutations_planned"] == 0
    else:
        assert not plan.issues and plan.steps[0].operation == expected
