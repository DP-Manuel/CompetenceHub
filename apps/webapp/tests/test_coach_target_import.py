"""Pure v2 contract checks and opt-in owned schema9 PostgreSQL import proof."""

from copy import deepcopy
from datetime import UTC, datetime
import json
import os
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.portal.coach_import import (
    canonical_bytes,
    fingerprint,
    import_profile_data,
    profile_fingerprint,
    validate_records,
)
from competence_hub_api.portal.coach_registry import (
    CoachAggregate,
    ObjectEvidence,
    ProfileRevision,
    TopicSnapshot,
    public_projection,
)
from competence_hub_api.portal.coach_target import public_target, subjects
from competence_hub_api.portal.postgres_coach_import import (
    ImportBinding,
    ImportSnapshot,
    PostgresCoachImporter,
    local_import_url,
    plan_records,
)
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)
from scripts.coach_import_fixture import NOW, fixture, target_fixture


def validated(records=None):
    values, contract, topics, assets = target_fixture()
    return validate_records(
        values if records is None else records, contract, topics, assets, now=NOW
    )


def bound_snapshot(record, catalogue):
    coach = CoachAggregate(uuid4(), record.content.display_name, uuid4())
    revision = ProfileRevision(
        uuid4(),
        1,
        record.content,
        uuid4(),
        NOW,
        topics=tuple(catalogue[t] for t in record.content.topic_ids),
    )
    revision.object_evidence = [
        ObjectEvidence(uuid4(), value, uuid4(), NOW) for value in record.object_evidence
    ]
    coach.revisions.append(revision)
    ledger = dict(
        profile_path=record.content.profile_path,
        source_content_hash=record.source_hash,
        profile_content_hash=record.profile_hash,
        mapping_contract_hash=record.contract_hash,
        publication_intent_hash=record.publication_hash,
        last_revision_id=revision.id,
        last_registry_version=coach.version,
    )
    binding = ImportBinding(coach, ledger, set(record.items))
    return (
        ImportSnapshot(bindings={record.source.source_identity.key: binding}),
        revision,
    )


def rebind_evidence(records, mapping, catalogue, assets):
    """Synthetic fixture changes require new exact hashes, not reused consent."""
    copies = deepcopy(records)
    for record in copies:
        record.pop("object_evidence", None)
        record["publication"] = {}
    prepared = validate_records(copies, mapping, catalogue, assets, now=NOW)
    assert not prepared.issues
    for record, mapped in zip(records, prepared.records):
        hashes = subjects(
            mapped.content, [catalogue[t] for t in mapped.content.topic_ids]
        )
        for value in record.get("object_evidence", []):
            value["subject_hash"] = hashes[value["subject_type"], value["subject_key"]]


def test_v2_fixture_preserves_typed_internal_and_public_fields():
    result = validated()
    assert not result.issues and len(result.records) == 5
    rich = result.records[4]
    assert rich.content.target_version == 1
    assert rich.content.qualifications[1].public is False
    assert rich.content.qualifications[1].internal_note == "Synthetic private note"
    assert rich.content.offerings[1].duration.weeks == 6
    assert len(rich.content.offerings) == 2 and len(rich.content.offering_families) == 1
    assert {
        ("family", "balance"),
        ("variant", "family/balance/community"),
        ("variant", "offering/balance/day/practice"),
        ("presentation", "presentation"),
        ("presentation_section", "profile"),
        ("presentation_link", "website"),
    } <= set(rich.items)
    output = json.dumps(public_target(rich.content, "preview"))
    for private in (
        "Synthetic private note",
        "Synthetic internal verification",
        "synthetic:protected",
        "subject_hash",
        "evidence_reference",
    ):
        assert private not in output
    assert all(
        e.approved_at is None and e.approved_on is None for e in rich.object_evidence
    )
    assert (
        next(e for e in rich.object_evidence if e.kind == "protected_source").status
        == "unknown"
    )


@pytest.mark.parametrize(
    "change",
    [
        "coerced_bool",
        "coerced_number",
        "parallel",
        "unknown",
        "key",
        "family",
        "duplicate_role",
        "therapy",
        "evidence_hash",
        "evidence_subject",
        "future",
        "protected_scope",
        "production",
    ],
)
def test_v2_fails_closed_without_echoing_payloads(change):
    records, mapping, topics, assets = target_fixture()
    r = records[4]
    if change == "coerced_bool":
        r["offerings"][0]["content"]["bookable"] = "false"
    elif change == "coerced_number":
        r["offerings"][0]["content"]["duration"]["minutes"] = True
    elif change == "parallel":
        r["profile"]["qualifications"] = r["qualifications"]
    elif change == "unknown":
        r["private_payload_never_echoed"] = "private_payload_never_echoed"
    elif change == "key":
        r["offerings"][0]["content"]["key"] = "different"
    elif change == "family":
        r["offerings"][0]["content"]["family_key"] = "different"
    elif change == "duplicate_role":
        r["roles"].append(deepcopy(r["roles"][0]))
    elif change == "therapy":
        r["offerings"][1]["content"]["service_domains"] = ["psychotherapy"]
    elif change == "evidence_hash":
        r["object_evidence"][0]["subject_hash"] = "a" * 64
    elif change == "evidence_subject":
        r["object_evidence"][0]["subject_key"] = "missing"
    elif change == "future":
        r["object_evidence"][0]["approved_on"] = "2099-01-01"
    elif change == "protected_scope":
        r["object_evidence"][-1]["scope"] = "public_content"
    else:
        records[0]["publication"]["published"].append("production")
    result = validate_records(records, mapping, topics, assets, now=NOW)
    report = plan_records(result, ImportSnapshot()).report()
    assert result.issues and report["business_mutations_planned"] == 0
    assert "private_payload_never_echoed" not in json.dumps(report)


def test_v1_cannot_silently_drop_target_fields_and_schema8_hash_is_preserved():
    records, mapping, topics, assets = fixture()
    old = validate_records(records, mapping, topics, assets, now=NOW).records[0]
    data = import_profile_data(old.content)
    assert "target_version" not in data and "key" not in data["offerings"][0]
    assert old.profile_hash == fingerprint(
        {
            "content": data,
            "topics": [
                {"id": str(t.id), "name": t.name, "categories": sorted(t.categories)}
                for t in sorted(
                    [topics[t] for t in old.content.topic_ids], key=lambda t: str(t.id)
                )
            ],
        }
    )
    snapshot, _ = bound_snapshot(old, topics)
    assert (
        plan_records(
            validate_records(records[:1], mapping, topics, assets, now=NOW), snapshot
        )
        .steps[0]
        .operation
        == "UNCHANGED"
    )
    records[0]["offerings"][0]["content"]["bookable"] = True
    assert validate_records(records, mapping, topics, assets, now=NOW).issues


def test_keyed_reordering_is_exact_noop_and_titles_do_not_define_identity():
    records, mapping, topics, assets = target_fixture()
    original = validated().records[4]
    for name in ("roles", "qualifications", "offering_families", "offerings"):
        records[4][name].reverse()
    records[4]["offering_families"][0]["service_domains"].reverse()
    records[4]["offering_families"][0]["boundaries"][0]["excluded_services"].reverse()
    current = validate_records(records, mapping, topics, assets, now=NOW)
    assert not current.issues
    assert current.records[4].source_hash == original.source_hash
    snapshot, _ = bound_snapshot(original, topics)
    assert plan_records(current, snapshot).steps[4].operation == "UNCHANGED"
    records[4]["offering_families"][0]["title"] = "Changed literal title"
    rebind_evidence(records, mapping, topics, assets)
    renamed = validate_records(records, mapping, topics, assets, now=NOW)
    assert not renamed.issues and set(renamed.records[4].items) == set(original.items)


@pytest.mark.parametrize(
    "collection",
    [
        "qualifications",
        "offering_families",
        "variant",
        "presentation_section",
        "object_evidence",
    ],
)
def test_missing_stable_items_require_review(collection):
    records, mapping, topics, assets = target_fixture()
    original = validated().records[4]
    if collection == "variant":
        records[4]["offering_families"][0]["variants"] = []
    elif collection == "presentation_section":
        records[4]["presentation"]["sections"] = []
    elif collection == "offering_families":
        records[4]["offering_families"] = []
        for offer in records[4]["offerings"]:
            offer["content"]["family_key"] = None
        records[4]["object_evidence"] = [
            e for e in records[4]["object_evidence"] if e["subject_type"] != "family"
        ]
    else:
        records[4][collection] = []
    if collection == "qualifications":
        records[4]["object_evidence"] = [
            e
            for e in records[4]["object_evidence"]
            if e["subject_type"] != "qualification"
        ]
    rebind_evidence(records, mapping, topics, assets)
    current = validate_records(records, mapping, topics, assets, now=NOW)
    assert not current.issues
    snapshot, _ = bound_snapshot(original, topics)
    assert "MISSING_ITEM_REVIEW_REQUIRED" in {
        i.code for i in plan_records(current, snapshot).issues
    }


def test_evidence_only_append_is_not_metadata_and_same_key_cannot_be_rewritten():
    records, mapping, topics, assets = target_fixture()
    original = validated().records[4]
    snapshot, revision = bound_snapshot(original, topics)
    revision.status = "submitted"
    new = deepcopy(records[4]["object_evidence"][0])
    new["key"] = "new-explicit-evidence"
    records[4]["object_evidence"].append(new)
    result = validate_records(records, mapping, topics, assets, now=NOW)
    assert not result.issues
    plan = plan_records(result, snapshot)
    assert not plan.issues and plan.steps[4].operation == "EVIDENCE"
    records[4]["object_evidence"][0]["status"] = "rejected"
    result = validate_records(records, mapping, topics, assets, now=NOW)
    assert "STATE_CONFLICT" in {i.code for i in plan_records(result, snapshot).issues}


def test_evidence_history_and_public_section_order_are_not_semantic_sets():
    records, mapping, topics, assets = target_fixture()
    original = validated().records[4]
    snapshot, _ = bound_snapshot(original, topics)
    records[4]["object_evidence"].reverse()
    result = validate_records(records, mapping, topics, assets, now=NOW)
    assert not result.issues
    assert result.records[4].source_hash != original.source_hash
    assert "STATE_CONFLICT" in {i.code for i in plan_records(result, snapshot).issues}
    records, mapping, topics, assets = target_fixture()
    records[4]["presentation"]["sections"].append(
        {"key": "second", "kind": "contact", "paragraphs": ["Synthetic contact"]}
    )
    rebind_evidence(records, mapping, topics, assets)
    before = validate_records(records, mapping, topics, assets, now=NOW)
    records[4]["presentation"]["sections"].reverse()
    rebind_evidence(records, mapping, topics, assets)
    after = validate_records(records, mapping, topics, assets, now=NOW)
    assert not before.issues and not after.issues
    assert before.records[4].profile_hash != after.records[4].profile_hash


@pytest.mark.parametrize("explicit_clear", [False, True])
def test_import_preserves_field_presence_omission_is_not_an_explicit_clear(
    explicit_clear,
):
    records, mapping, topics, assets = target_fixture()
    original = validated().records[4]
    snapshot, revision = bound_snapshot(original, topics)
    revision.status = "submitted"
    if explicit_clear:
        records[4]["qualifications"][1]["internal_note"] = None
    else:
        del records[4]["qualifications"][1]["internal_note"]
    rebind_evidence(records, mapping, topics, assets)
    result = validate_records(records, mapping, topics, assets, now=NOW)
    assert not result.issues
    candidate = result.records[4].content.qualifications[1]
    assert ("internal_note" in candidate.model_fields_set) == explicit_clear
    plan = plan_records(result, snapshot)
    if explicit_clear:
        assert not plan.issues and plan.steps[4].operation == "REVISION"
        assert candidate.internal_note is None
    else:
        assert any(
            i.code == "STATE_CONFLICT" and i.field == "incomplete_target_snapshot"
            for i in plan.issues
        )
        assert plan.report()["business_mutations_planned"] == 0


def test_import_preserves_recursive_presence_for_presentation_duration_and_variants():
    records, mapping, topics, assets = target_fixture()
    records[4]["offerings"][0]["content"]["variants"][0][
        "description"
    ] = "Synthetic populated variant note"
    rebind_evidence(records, mapping, topics, assets)
    before = validate_records(records, mapping, topics, assets, now=NOW)
    assert not before.issues
    snapshot, revision = bound_snapshot(before.records[4], topics)
    revision.status = "submitted"
    del records[4]["offerings"][0]["content"]["variants"][0]["description"]
    rebind_evidence(records, mapping, topics, assets)
    after = validate_records(records, mapping, topics, assets, now=NOW)
    assert not after.issues
    candidate = after.records[4].content
    assert "description" not in candidate.offerings[0].variants[0].model_fields_set
    assert "minutes" not in candidate.offerings[0].duration.model_fields_set
    assert "portrait_width" not in candidate.presentation.model_fields_set
    assert "incomplete_target_snapshot" in {
        i.field for i in plan_records(after, snapshot).issues
    }


def test_target_database_is_separate_and_explicitly_opted_in():
    url = "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55436/competence_hub_staging"
    local_import_url(url, target_v2=True)
    with pytest.raises(ValueError):
        local_import_url(url)
    with pytest.raises(ValueError):
        local_import_url(url.replace("55436", "55435"), target_v2=True)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_default_importer_rejects_v2_before_database_access():
    values, mapping, _, assets = target_fixture()
    engine = SimpleNamespace(
        url=make_url(
            "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55435/competence_hub_staging"
        )
    )
    result = await PostgresCoachImporter(engine).apply_synthetic(
        values, mapping, assets, actor=None
    )
    assert result["issues"] == [{"code": "SYNTHETIC_SCOPE_REQUIRED"}]
    assert (await PostgresCoachImporter(engine).dry_run(values, mapping, assets))[
        "issues"
    ] == [{"code": "SYNTHETIC_SCOPE_REQUIRED"}]


@pytest.mark.anyio
async def test_v2_postgres_atomic_exact_noop_with_existing_rows(monkeypatch):
    raw = os.environ.get("COMPETENCE_HUB_COACH_TARGET_LOCAL_DATABASE_URL", "")
    owner_url = os.environ.get("COMPETENCE_HUB_COACH_TARGET_LOCAL_OWNER_URL", "")
    if not raw or not owner_url:
        pytest.skip("requires owned disposable upgraded schema9 localhost55436")
    local_import_url(raw, target_v2=True)
    owner_target = make_url(owner_url)
    assert (
        owner_target.drivername,
        owner_target.host,
        owner_target.port,
        owner_target.database,
        owner_target.username,
    ) == (
        "postgresql+asyncpg",
        "127.0.0.1",
        55436,
        "competence_hub_staging",
        "competence_hub_migrator",
    )
    assert not owner_target.query
    from test_coach_import_postgres_local import database_state

    engine = create_async_engine(raw, hide_parameters=True)
    owner = create_async_engine(owner_url, hide_parameters=True)
    actor = SimpleNamespace(user_id=uuid4(), roles=("admin",))
    suffix = uuid4().hex[:12]
    records, mapping, catalogue, assets = target_fixture()
    ids = {old: uuid4() for old in catalogue}
    catalogue = {
        ids[t.id]: TopicSnapshot(
            ids[t.id], "Synthetic import " + suffix + " " + t.name, t.categories
        )
        for t in catalogue.values()
    }
    mapping = mapping.model_copy(
        update={
            "topics": tuple(
                r.model_copy(update={"topic_id": ids[r.topic_id]})
                for r in mapping.topics
            )
        }
    )
    for record in records:
        label = record["source_identity"]["source_key"].split("/")[-1]
        record["source_identity"]["source_key"] = (
            "coach/target-import-" + suffix + "/" + label
        )
        record["profile"][
            "profile_path"
        ] = f"/coaches/synthetic-import-{suffix}-{label}/"
        record["profile"]["display_name"] = f"Synthetic Import {suffix} {label.title()}"
    rebind_evidence(records, mapping, catalogue, assets)
    importer = PostgresCoachImporter(engine, target_v2=True)
    repo = PostgresCoachRegistryRepository(engine)
    try:
        async with owner.begin() as c:
            assert await c.scalar(
                text(
                    "SELECT EXISTS(SELECT 1 FROM competence_hub.schema_migrations WHERE version='0009')"
                )
            )
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await c.execute(
                text(
                    "INSERT INTO competence_hub.portal_users(id,display_name,email) VALUES (:id,'Synthetic target import operator',:email)"
                ),
                {
                    "id": actor.user_id,
                    "email": f"synthetic-target-import-{suffix}@example.invalid",
                },
            )
            await c.execute(
                text(
                    "INSERT INTO competence_hub.user_roles(user_id,role_id) SELECT :id,id FROM competence_hub.roles WHERE code='admin'"
                ),
                {"id": actor.user_id},
            )
            for topic in catalogue.values():
                await c.execute(
                    text(
                        "INSERT INTO competence_hub.topics(id,name) VALUES (:id,:name)"
                    ),
                    {"id": topic.id, "name": topic.name},
                )
                for category in topic.categories:
                    await c.execute(
                        text(
                            "INSERT INTO competence_hub.topic_category_assignments VALUES (:id,:category)"
                        ),
                        {"id": topic.id, "category": category},
                    )
        initial = await database_state(owner)
        assert (await importer.dry_run(records, mapping, assets))["counts"][
            "CREATE"
        ] == 5
        assert await database_state(owner) == initial
        original_apply = importer._apply_record
        calls = 0

        async def fail_after_second(c, step, operator, now):
            nonlocal calls
            await original_apply(c, step, operator, now)
            calls += 1
            if calls == 2:
                raise RuntimeError("synthetic rollback proof")

        monkeypatch.setattr(importer, "_apply_record", fail_after_second)
        with pytest.raises(RuntimeError):
            await importer.apply_synthetic(records, mapping, assets, actor=actor)
        assert await database_state(owner) == initial
        monkeypatch.setattr(importer, "_apply_record", original_apply)
        applied = await importer.apply_synthetic(records, mapping, assets, actor=actor)
        assert applied["result"] == "PASS", applied
        assert applied["counts"]["CREATE"] == 5
        state = await database_state(owner)
        owned = [
            r["data"]
            for r in state["coach_import_sources"]
            if r["data"]["source_key"].startswith("coach/target-import-" + suffix)
        ]
        assert len(owned) == 5

        async def projection():
            coaches = [await repo.get(UUID(r["coach_id"])) for r in owned]
            return {
                env: canonical_bytes(public_projection(coaches, env))
                for env in ("preview", "production")
            }

        before = await projection()
        assert records[0]["profile"]["display_name"].encode() in before["preview"]
        for _ in range(2):
            assert (await importer.dry_run(records, mapping, assets))["counts"][
                "UNCHANGED"
            ] == 5
            result = await importer.apply_synthetic(
                records, mapping, assets, actor=actor
            )
            assert (
                result["counts"]["UNCHANGED"] == 5 and result["business_mutations"] == 0
            )
            assert await database_state(owner) == state
            assert await projection() == before
        epsilon_id = UUID(
            next(r["coach_id"] for r in owned if r["source_key"].endswith("/epsilon"))
        )
        epsilon = await repo.get(epsilon_id)
        assert epsilon.revisions[0].content == validated().records[
            4
        ].content.model_copy(
            update={
                "profile_path": records[4]["profile"]["profile_path"],
                "display_name": records[4]["profile"]["display_name"],
            }
        )
        assert any(
            e.value.kind == "protected_source" and e.value.status == "unknown"
            for e in epsilon.revisions[0].object_evidence
        )
        omitted = deepcopy(records[4])
        del omitted["qualifications"][1]["internal_note"]
        rebind_evidence([omitted], mapping, catalogue, assets)
        denied = await importer.apply_synthetic([omitted], mapping, assets, actor=actor)
        assert "incomplete_target_snapshot" in {i["field"] for i in denied["issues"]}
        assert (
            denied["business_mutations"] == 0 and await database_state(owner) == state
        )
        logical_before = {
            (r["data"]["kind"], r["data"]["item_key"]): r["data"]["logical_id"]
            for r in state["coach_import_items"]
            if r["data"]["source_key"] == records[4]["source_identity"]["source_key"]
        }
        old_content = epsilon.revisions[0].content
        old_evidence = epsilon.revisions[0].object_evidence
        changed = deepcopy(records)
        changed[4]["offering_families"][0]["title"] = "Synthetic reviewed family title"
        changed[4]["offerings"][0]["content"]["title"] = "Synthetic reviewed day title"
        rebind_evidence(changed, mapping, catalogue, assets)
        result = await importer.apply_synthetic(
            changed[4:], mapping, assets, actor=actor
        )
        assert result["result"] == "PASS" and result["counts"]["REVISION"] == 1, result
        epsilon = await repo.get(epsilon_id)
        assert len(epsilon.revisions) == 2
        assert (
            epsilon.revisions[0].content == old_content
            and epsilon.revisions[0].object_evidence == old_evidence
        )
        assert epsilon.revisions[1].content.offering_families[0].key == "balance"
        revised = await database_state(owner)
        logical_after = {
            (r["data"]["kind"], r["data"]["item_key"]): r["data"]["logical_id"]
            for r in revised["coach_import_items"]
            if r["data"]["source_key"] == records[4]["source_identity"]["source_key"]
        }
        assert logical_before == logical_after
        appended = deepcopy(changed[4])
        rejection = deepcopy(
            next(
                e for e in appended["object_evidence"] if e["kind"] == "profile_content"
            )
        )
        rejection.update(key="explicit-rejection", status="rejected")
        appended["object_evidence"].append(rejection)
        result = await importer.apply_synthetic(
            [appended], mapping, assets, actor=actor
        )
        assert result["result"] == "PASS" and result["counts"]["EVIDENCE"] == 1, result
        evidence_state = await database_state(owner)
        repeat = await importer.apply_synthetic(
            [appended], mapping, assets, actor=actor
        )
        assert repeat["counts"]["UNCHANGED"] == 1 and repeat["business_mutations"] == 0
        assert await database_state(owner) == evidence_state
        missing = deepcopy(appended)
        missing["offering_families"][0]["variants"] = []
        rebind_evidence([missing], mapping, catalogue, assets)
        denied = await importer.apply_synthetic([missing], mapping, assets, actor=actor)
        assert "MISSING_ITEM_REVIEW_REQUIRED" in {i["code"] for i in denied["issues"]}
        assert await database_state(owner) == evidence_state
        assert await projection() == before
        print(
            "PASS | v2 five-record APPLY, rollback and repeat2/3 preserve all schema9 rows/xmin and public projection bytes"
        )
        print(
            "PASS | v2 revision retains logical family/format/variant IDs and history; evidence-only append then exact no-op; missing item blocks without writes"
        )
    finally:
        await engine.dispose()
        await owner.dispose()
