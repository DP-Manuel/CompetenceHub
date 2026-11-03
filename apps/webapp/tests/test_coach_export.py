"""Offline synthetic acceptance. The SQL double is not live PostgreSQL proof."""

import asyncio
from copy import deepcopy
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from pydantic import ValidationError

from competence_hub_api.portal import coach_export as export
from competence_hub_api.portal.coach_projection import (
    canonical_bytes,
    generate_projection,
    projection_diff,
    read_projection,
)
from competence_hub_api.portal.coach_registry import (
    Approval,
    ObjectEvidence,
    ProfileContent,
    ProfileRevision,
    Publication,
    RegistryConflict,
)
from scripts.coach_projection_fixture import (
    synthetic_registry,
    ASSET_REFERENCE,
    PORTRAIT,
    ACTOR,
    NOW,
)
from scripts.coach_target_cases import approvals_for


@pytest.fixture
def assets(tmp_path):
    path = tmp_path / ASSET_REFERENCE
    path.parent.mkdir(parents=True)
    path.write_bytes(PORTRAIT)
    return tmp_path


def snapshot():
    return export.RegistrySnapshot.capture(synthetic_registry())


def approve(revision):
    revision.object_evidence = [
        ObjectEvidence(
            UUID(int=5000 + i + (100 if env == "production" else 0)), value, ACTOR, NOW
        )
        for env in ("preview", "production")
        for i, value in enumerate(approvals_for(revision, env, prefix=env))
    ]


@pytest.mark.parametrize(
    "mode,count", [("internal", 4), ("preview", 2), ("production", 1)]
)
def test_modes_and_frozen_public_compatibility(assets, mode, count):
    value = export.export_registry(snapshot(), mode, asset_root=assets)
    assert len(value["coaches"]) == count
    if mode != "internal":
        baseline = generate_projection(synthetic_registry(), mode)
        assert canonical_bytes(value) == canonical_bytes(baseline)
        assert projection_diff(baseline, value)["high_attention"] == []
    else:
        export.InternalExport.model_validate(value)
        assert value["export_schema_version"] == 1
        with pytest.raises(ValueError):
            from competence_hub_api.portal.coach_projection import validate_projection

            validate_projection(value)


@pytest.mark.parametrize("mode", ["internal", "preview", "production"])
def test_determinism_snapshot_isolation_and_zero_asset_mutation(assets, mode):
    original = synthetic_registry()
    before = deepcopy(original)
    sealed = export.RegistrySnapshot.capture(original)
    a = canonical_bytes(export.export_registry(sealed, mode, asset_root=assets))
    original[0].lifecycle = "inactive"
    sealed.coaches()[0].revisions.clear()
    b = canonical_bytes(export.export_registry(sealed, mode, asset_root=assets))
    assert a == b and hashlib.sha256(a).digest() == hashlib.sha256(b).digest()
    reversed_input = export.RegistrySnapshot.capture(tuple(reversed(before)))
    assert (
        canonical_bytes(export.export_registry(reversed_input, mode, asset_root=assets))
        == a
    )
    assert (assets / ASSET_REFERENCE).read_bytes() == PORTRAIT
    assert not any(
        x in a for x in (b"occurred_at", b"created_at", b"recorded_at", b"request_id")
    )


@pytest.mark.parametrize("mode", ["internal", "preview", "production"])
def test_minimization_source_price_notes_and_actor_never_serialized(assets, mode):
    value = export.export_registry(snapshot(), mode, asset_root=assets)
    data = canonical_bytes(value)
    for private in (
        b"PRIVATE_PRICE",
        b"private:workshop",
        b"private:certificate",
        b"synthetic:approval",
        b"synthetic:consent",
        b"internal_note",
        b"protected_source_reference",
        b"verification_state",
        b"evidence_reference",
        b"recorded_by",
        b"created_by",
        b"events",
        b"request_id",
    ):
        assert private not in data
    if mode != "internal":
        assert b"PRIVATE_QUALIFICATION" not in data
        assert b"coach_id" not in data and b"revision_id" not in data
    else:
        assert b"PRIVATE_QUALIFICATION" in data  # legitimate administrative title


def test_families_variants_duration_boundaries_and_qualification_visibility(assets):
    coaches = synthetic_registry()
    revision = coaches[0].revisions[0]
    data = revision.content.model_dump(mode="json")
    data["qualifications"][1].update(
        public=True, public_display_label="Second explicit qualification"
    )
    data["boundaries"] = [
        {"key": key, "text": text, "excluded_services": excluded}
        for key, text, excluded in (
            ("coaching", "Coaching != psychotherapy", ["psychotherapy"]),
            ("moderation", "Moderation != mediation", ["mediation"]),
            ("health", "Health promotion != medical treatment", ["medical_treatment"]),
            ("therapy", "HeilprG psychotherapy != coaching", ["coaching"]),
        )
    ]
    data["offerings"].append(
        dict(
            key="therapy",
            title="Synthetic therapy",
            type="other",
            ordering=2,
            service_domains=["psychotherapy"],
            bookable=False,
        )
    )
    revision.content = ProfileContent.model_validate(data)
    approve(revision)
    sealed = export.RegistrySnapshot.capture(coaches)
    value = export.export_registry(sealed, "preview", asset_root=assets)
    alpha, beta = value["coaches"]
    assert beta["assets"] == []
    assert len(alpha["qualifications"]) == 2
    assert len(alpha["boundaries"]) == 4
    assert len(alpha["offering_families"]) == 1
    day, program = alpha["offering_families"][0]["formats"]
    assert day["variants"][0]["kind"] == "add_on"
    assert program["duration"]["weeks"] == 6
    assert len(alpha["offerings"]) == 1
    assert alpha["offerings"][0]["service_domains"] == ["psychotherapy"]
    assert not alpha["offerings"][0]["bookable"]


@pytest.mark.parametrize("state", ["draft", "paused", "inactive", "archived"])
def test_nonactive_lifecycle_is_not_public_but_remains_internal(assets, state):
    values = synthetic_registry()
    values[0].lifecycle = state
    sealed = export.RegistrySnapshot.capture(values)
    public = export.export_registry(sealed, "production", asset_root=assets)
    assert public["coaches"] == []
    assert (
        export.export_registry(sealed, "internal", asset_root=assets)["coaches"][0][
            "lifecycle"
        ]
        == state
    )


def test_return_same_identity_fresh_revision_and_older_publication(assets):
    values = synthetic_registry()
    alpha = values[0]
    old_id = alpha.id
    alpha.publication_floor = 1
    alpha.lifecycle = "active"
    old = alpha.revisions[0]
    new = ProfileRevision(
        UUID(int=900),
        2,
        old.content,
        ACTOR,
        NOW,
        "submitted",
        old.topics,
        deepcopy(old.approvals),
    )
    approve(new)
    alpha.revisions.append(new)
    alpha.publications = {
        env: Publication(new.id, "published", ACTOR, NOW)
        for env in ("preview", "production")
    }
    internal = export.export_registry(
        export.RegistrySnapshot.capture(values), "internal", asset_root=assets
    )
    assert internal["coaches"][0]["coach_id"] == str(old_id)
    assert internal["coaches"][0]["current_profile_revision"] == str(new.id)
    assert (
        len(
            export.export_registry(
                export.RegistrySnapshot.capture(values), "production", asset_root=assets
            )["coaches"]
        )
        == 1
    )
    alpha.publications["production"].revision_id = old.id
    with pytest.raises(RegistryConflict, match="publication"):
        export.export_registry(
            export.RegistrySnapshot.capture(values), "production", asset_root=assets
        )


@pytest.mark.parametrize("decision", ["unknown", "rejected"])
def test_no_production_fallback_for_unknown_or_rejected_exact_evidence(
    assets, decision
):
    values = synthetic_registry()
    revision = values[0].revisions[0]
    index = next(
        i
        for i, e in enumerate(revision.object_evidence)
        if e.value.environment == "production"
    )
    evidence = revision.object_evidence[index]
    revision.object_evidence[index] = replace(
        evidence, value=evidence.value.model_copy(update={"status": decision})
    )
    sealed = export.RegistrySnapshot.capture(values)
    assert (
        len(export.export_registry(sealed, "preview", asset_root=assets)["coaches"])
        == 2
    )
    with pytest.raises(RegistryConflict):
        export.export_registry(sealed, "production", asset_root=assets)


@pytest.mark.parametrize(
    "bad",
    [
        "identity",
        "revision",
        "topic",
        "category",
        "publication",
        "family",
        "route",
        "qualification",
        "evidence",
    ],
)
def test_invalid_aggregate_relationships_fail_closed(bad):
    values = synthetic_registry()
    alpha, beta = values[:2]
    r = alpha.revisions[0]
    if bad == "identity":
        beta.id = alpha.id
    if bad == "revision":
        beta.revisions[0].id = r.id
    if bad == "topic":
        r.topics = ()
    if bad == "category":
        r.topics = (replace(r.topics[0], categories=("invented",)),)
    if bad == "publication":
        alpha.publications["production"].revision_id = beta.revisions[0].id
    if bad == "family":
        r.content = r.content.model_copy(update={"offering_families": ()})
    if bad == "route":
        beta.revisions[0].content = beta.revisions[0].content.model_copy(
            update={"profile_path": r.content.profile_path}
        )
    if bad == "qualification":
        r.content = r.content.model_copy(
            update={
                "qualifications": (
                    r.content.qualifications[0],
                    r.content.qualifications[0],
                )
            }
        )
    if bad == "evidence":
        r.object_evidence[0] = replace(
            r.object_evidence[0],
            value=r.object_evidence[0].value.model_copy(
                update={"subject_key": "missing"}
            ),
        )
    with pytest.raises((RegistryConflict, ValidationError)):
        export.RegistrySnapshot.capture(values)


def test_stable_ordering_respects_editorial_values(assets):
    values = synthetic_registry()
    baseline = export.export_registry(
        export.RegistrySnapshot.capture(values), "internal", asset_root=assets
    )
    r = values[0].revisions[0]
    r.content = r.content.model_copy(
        update={
            "offerings": tuple(reversed(r.content.offerings)),
            "qualifications": tuple(reversed(r.content.qualifications)),
        }
    )
    # Internal review ordering is independent of container insertion order.
    assert canonical_bytes(
        export.export_registry(
            export.RegistrySnapshot.capture(values), "internal", asset_root=assets
        )
    ) == canonical_bytes(baseline)


def test_new_draft_does_not_replace_exact_published_revision(assets):
    values = synthetic_registry()
    old = values[0].revisions[0]
    new = ProfileRevision(
        UUID(int=901),
        2,
        old.content.model_copy(update={"short_intro": "UNAPPROVED_DRAFT_COPY"}),
        ACTOR,
        NOW,
        "draft",
        old.topics,
    )
    values[0].revisions.append(new)
    sealed = export.RegistrySnapshot.capture(values)
    public = export.export_registry(sealed, "production", asset_root=assets)
    internal = export.export_registry(sealed, "internal", asset_root=assets)
    assert b"UNAPPROVED_DRAFT_COPY" not in canonical_bytes(public)
    assert internal["coaches"][0]["current_profile_revision"] == str(new.id)
    assert len(internal["coaches"][0]["revisions"]) == 2


@pytest.mark.parametrize("mode", ["internal", "preview", "production"])
def test_observation_and_audit_metadata_do_not_change_export_hash(assets, mode):
    from datetime import timedelta

    values = synthetic_registry()
    before = export.export_registry(
        export.RegistrySnapshot.capture(values), mode, asset_root=assets
    )
    for coach in values:
        coach.events.append(("PRIVATE_AUDIT_EVENT", ACTOR, NOW, UUID(int=8000)))
        coach.request_id = UUID(int=8001)
        for revision in coach.revisions:
            revision.created_at += timedelta(days=1)
            revision.approvals = [
                replace(a, occurred_at=a.occurred_at + timedelta(days=1))
                for a in revision.approvals
            ]
    after = export.export_registry(
        export.RegistrySnapshot.capture(values), mode, asset_root=assets
    )
    assert canonical_bytes(before) == canonical_bytes(after)


@pytest.mark.parametrize("mode", ["internal", "preview", "production"])
def test_empty_registry_is_valid_without_invented_identity(assets, mode):
    value = export.export_registry(
        export.RegistrySnapshot.capture(()), mode, asset_root=assets
    )
    assert value["coaches"] == []
    assert all(n == 0 for n in export.export_counts(value).values())


@pytest.mark.parametrize("attack", ["missing", "hash", "traversal", "type"])
def test_asset_fail_closed_without_copy_or_mutation(assets, attack):
    values = synthetic_registry()
    r = values[0].revisions[0]
    asset = r.content.assets[0]
    before = (assets / ASSET_REFERENCE).read_bytes()
    if attack == "missing":
        (assets / ASSET_REFERENCE).unlink()
    if attack == "hash":
        r.content = r.content.model_copy(
            update={"assets": (asset.model_copy(update={"sha256": "0" * 64}),)}
        )
    if attack in {"traversal", "type"}:
        r.content = r.content.model_copy(
            update={
                "assets": (
                    asset.model_copy(
                        update={
                            "reference": (
                                "../private.txt"
                                if attack == "traversal"
                                else "images/coaches/script.svg"
                            )
                        }
                    ),
                )
            }
        )
    with pytest.raises((ValueError, OSError)):
        export.export_registry(
            export.RegistrySnapshot.capture(values), "preview", asset_root=assets
        )
    if attack != "missing":
        assert (assets / ASSET_REFERENCE).read_bytes() == before


class Result:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return deepcopy(self.rows)

    def one(self):
        assert len(self.rows) == 1
        return self.rows[0]


class SyntheticConnection:
    """Simulate transaction snapshot and write denial; never claims real SQL proof."""

    def __init__(self, tables):
        self.engine = SimpleNamespace(
            url=SimpleNamespace(
                drivername="postgresql+asyncpg",
                host="127.0.0.1",
                port=55437,
                database="competence_hub_export_synthetic",
                username="competence_hub_app",
            )
        )
        self.live = tables
        self.active = False
        self.read_only = False
        self.rolled_back = False
        self.calls = []
        self.on_read = None
        self.settings = {"read_only": "on", "isolation": "repeatable read"}

    def in_transaction(self):
        return self.active

    async def begin(self):
        self.active = True
        self.frozen = deepcopy(self.live)
        return self

    async def rollback(self):
        self.active = False
        self.rolled_back = True

    async def execute(self, statement, parameters=None):
        sql = str(statement)
        self.calls.append((sql, parameters))
        assert self.active
        if sql == export.TRANSACTION_SQL:
            self.read_only = True
            return Result([])
        if sql == export.CHECK_SQL:
            return Result([self.settings])
        if not sql.startswith("SELECT ") and self.read_only:
            raise PermissionError("synthetic read-only SQL transaction rejects write")
        assert self.read_only
        table = next(k for k, value in export.READ_SQL.items() if value == sql)
        if self.on_read:
            self.on_read(table, self.live)
        return Result(self.frozen[table][: parameters["limit"]])


def relational_fixture():
    tables = {table: [] for table in export.TABLE_LIMITS}
    for coach in synthetic_registry():
        tables["coaches"].append(
            dict(
                id=coach.id,
                display_name=coach.display_name,
                registry_request_id=coach.request_id,
                lifecycle_status=coach.lifecycle,
                registry_lock_version=coach.version,
                publication_floor=coach.publication_floor,
            )
        )
        for r in coach.revisions:
            content = r.content.model_dump(mode="json")
            tables["coach_profile_revisions"].append(
                dict(
                    id=r.id,
                    coach_id=coach.id,
                    revision_number=r.number,
                    status=r.status,
                    created_by=r.created_by,
                    created_at=r.created_at,
                    **{
                        k: content[k]
                        for k in (
                            "display_name",
                            "academic_suffix",
                            "short_intro",
                            "description",
                            "professional_background",
                            "profile_path",
                            "target_version",
                            "presentation",
                            "boundaries",
                        )
                    },
                )
            )
            for kind, labels in (
                ("target_group", r.content.target_groups),
                ("competency", r.content.competencies),
            ):
                tables["coach_profile_labels"].extend(
                    dict(revision_id=r.id, kind=kind, ordering=i, label=label)
                    for i, label in enumerate(labels)
                )
            for topic in r.topics:
                tables["coach_profile_topics"].append(
                    dict(revision_id=r.id, topic_id=topic.id, snapshot_name=topic.name)
                )
                tables["coach_profile_topic_categories"].extend(
                    dict(revision_id=r.id, topic_id=topic.id, category_code=code)
                    for code in topic.categories
                )
            for item in r.content.offerings:
                data = item.model_dump(mode="json")
                base = {
                    k: data.pop(k)
                    for k in (
                        "title",
                        "type",
                        "description",
                        "active",
                        "ordering",
                        "key",
                        "family_key",
                    )
                }
                tables["coach_offerings"].append(
                    dict(
                        revision_id=r.id,
                        coach_id=coach.id,
                        item_key=base.pop("key"),
                        metadata=data,
                        **base,
                    )
                )
            for asset in r.content.assets:
                tables["coach_assets"].append(
                    dict(
                        revision_id=r.id,
                        **asset.model_dump(exclude={"scopes"}),
                        preview_allowed="preview" in asset.scopes,
                        production_allowed="production" in asset.scopes,
                    )
                )
            for a in r.approvals:
                tables["coach_profile_approvals"].append(
                    dict(
                        revision_id=r.id,
                        kind=a.kind,
                        actor_id=a.actor_id,
                        occurred_at=a.occurred_at,
                        evidence_ref=a.evidence_ref,
                    )
                )
            for field, table in (
                ("public_roles", "coach_public_roles"),
                ("qualifications", "coach_qualifications"),
                ("offering_families", "coach_offering_families"),
            ):
                for item in getattr(r.content, field):
                    data = item.model_dump(mode="json")
                    key = data.pop("key")
                    if field == "offering_families":
                        base = {
                            k: data.pop(k)
                            for k in ("title", "description", "active", "ordering")
                        }
                        data = dict(**base, metadata=data)
                    tables[table].append(
                        dict(revision_id=r.id, coach_id=coach.id, item_key=key, **data)
                    )
            for sequence, e in enumerate(r.object_evidence):
                data = e.value.model_dump()
                tables["coach_object_evidence"].append(
                    dict(
                        id=e.id,
                        revision_id=r.id,
                        coach_id=coach.id,
                        sequence=sequence,
                        evidence_key=data.pop("key"),
                        recorded_by=e.recorded_by,
                        recorded_at=e.recorded_at,
                        **data,
                    )
                )
        for env, p in coach.publications.items():
            tables["coach_publications"].append(
                dict(
                    coach_id=coach.id,
                    environment=env,
                    revision_id=p.revision_id,
                    state=p.state,
                    actor_id=p.actor_id,
                    occurred_at=p.occurred_at,
                    profile_path=coach.revision(p.revision_id).content.profile_path,
                )
            )
    return tables


def test_sql_snapshot_shared_hydration_parity_batch_no_n_plus_one(assets):
    connection = SyntheticConnection(relational_fixture())
    sealed = asyncio.run(export.read_postgres_snapshot(connection))
    for mode in ("internal", "preview", "production"):
        assert export.export_registry(
            sealed, mode, asset_root=assets
        ) == export.export_registry(snapshot(), mode, asset_root=assets)
    assert connection.rolled_back
    assert len(connection.calls) == 2 + len(export.TABLE_LIMITS)
    assert [call[0] for call in connection.calls[:2]] == [
        export.TRANSACTION_SQL,
        export.CHECK_SQL,
    ]
    assert not any("FOR UPDATE" in sql for sql, _ in connection.calls)


@pytest.mark.parametrize(
    "field,value",
    [
        ("host", "217.160.255.86"),
        ("host", "localhost"),
        ("port", 55432),
        ("port", 5432),
        ("database", "competence_hub_staging"),
        ("database", "competence_hub_production"),
        ("username", "postgres"),
        ("drivername", "postgresql"),
    ],
)
def test_remote_real_db_tunnel_and_wrong_role_rejected_before_any_query(field, value):
    connection = SyntheticConnection(relational_fixture())
    setattr(connection.engine.url, field, value)
    with pytest.raises(PermissionError, match="isolated synthetic"):
        asyncio.run(export.read_postgres_snapshot(connection))
    assert connection.calls == [] and not connection.active


def test_concurrent_update_cannot_mix_revisions_or_approvals(assets):
    connection = SyntheticConnection(relational_fixture())

    def alter(table, live):
        if table == "coaches":
            live["coach_profile_revisions"][0][
                "short_intro"
            ] = "Concurrent changed content"
            live["coach_profile_approvals"].clear()

    connection.on_read = alter
    sealed = asyncio.run(export.read_postgres_snapshot(connection))
    assert export.export_registry(
        sealed, "preview", asset_root=assets
    ) == export.export_registry(snapshot(), "preview", asset_root=assets)
    assert not connection.live["coach_profile_approvals"]


@pytest.mark.parametrize("mode", ["internal", "preview", "production"])
def test_unordered_sql_result_rows_preserve_deterministic_artifacts(assets, mode):
    tables = relational_fixture()
    for rows in tables.values():
        rows.reverse()
    connection = SyntheticConnection(tables)
    sealed = asyncio.run(export.read_postgres_snapshot(connection))
    assert canonical_bytes(
        export.export_registry(sealed, mode, asset_root=assets)
    ) == canonical_bytes(export.export_registry(snapshot(), mode, asset_root=assets))


@pytest.mark.parametrize(
    "operation",
    [
        "INSERT INTO x VALUES(1)",
        "UPDATE x SET a=1",
        "DELETE FROM x",
        "CREATE TABLE x(a int)",
        "SELECT dangerous_function()",
    ],
)
def test_read_capability_rejects_arbitrary_sql_before_connection(operation):
    connection = SyntheticConnection({})
    reader = export.ReadOnlyRows(connection)
    with pytest.raises(PermissionError):
        reader.execute(operation)
    for writer in (reader.create, reader.edit, reader.mutate):
        with pytest.raises(PermissionError):
            writer()
    assert connection.calls == []


@pytest.mark.parametrize(
    "table",
    ["audit_events", "portal_users", "coach_import_sources", "coaches;DELETE FROM x"],
)
def test_table_allowlist_rejects_noncoach_reads(table):
    connection = SyntheticConnection({})
    with pytest.raises(PermissionError):
        asyncio.run(export.ReadOnlyRows(connection).fetch(table))
    assert connection.calls == []


@pytest.mark.parametrize(
    "operation", ["INSERT INTO x VALUES(1)", "UPDATE x SET a=1", "DELETE FROM x"]
)
def test_bypassed_capability_write_attempt_aborts_readonly_transaction(
    monkeypatch, operation
):
    connection = SyntheticConnection(relational_fixture())

    async def attack(self, table):
        await connection.execute(operation)

    monkeypatch.setattr(export.ReadOnlyRows, "fetch", attack)
    with pytest.raises(PermissionError):
        asyncio.run(export.read_postgres_snapshot(connection))
    assert connection.rolled_back


@pytest.mark.parametrize(
    "bad",
    [
        "active",
        "settings",
        "bound",
        "owner",
        "qualification-owner",
        "category",
        "publication-route",
        "incomplete",
    ],
)
def test_transaction_or_row_inconsistency_aborts_without_artifact(bad):
    tables = relational_fixture()
    connection = SyntheticConnection(tables)
    if bad == "active":
        connection.active = True
    if bad == "settings":
        connection.settings["read_only"] = "off"
    if bad == "bound":
        tables["coaches"] *= 126
    if bad == "owner":
        tables["coach_offerings"][0]["coach_id"] = UUID(int=2)
    if bad == "qualification-owner":
        tables["coach_qualifications"][0]["coach_id"] = UUID(int=2)
    if bad == "category":
        tables["coach_profile_topic_categories"][0]["topic_id"] = UUID(int=999)
    if bad == "publication-route":
        tables["coach_publications"][0]["profile_path"] = "/coaches/wrong/"
    if bad == "incomplete":
        tables["coach_profile_revisions"].clear()
    with pytest.raises((PermissionError, RegistryConflict)):
        asyncio.run(export.read_postgres_snapshot(connection))
    assert connection.rolled_back == (bad != "active")


def test_cancellation_rolls_back(monkeypatch):
    connection = SyntheticConnection(relational_fixture())

    async def cancel(self, table):
        raise asyncio.CancelledError()

    monkeypatch.setattr(export.ReadOnlyRows, "fetch", cancel)
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(export.read_postgres_snapshot(connection))
    assert connection.rolled_back


def test_local_capture_rejects_concurrent_mutation(monkeypatch):
    values = synthetic_registry()
    original = export.deepcopy

    def race(data):
        result = original(data)
        data[0].version += 1
        return result

    monkeypatch.setattr(export, "deepcopy", race)
    with pytest.raises(RegistryConflict, match="concurrent"):
        export.RegistrySnapshot.capture(values)


@pytest.mark.parametrize(
    "bound", ["MAX_COACHES", "MAX_REVISIONS", "MAX_SNAPSHOT_BYTES"]
)
def test_local_snapshot_bounds_fail_closed(monkeypatch, bound):
    monkeypatch.setattr(export, bound, 1)
    with pytest.raises(RegistryConflict, match="bound"):
        snapshot()


def test_read_path_never_calls_repository_write_or_audit(monkeypatch, assets):
    def denied(*args, **kwargs):
        raise AssertionError("repository writer reached")

    for name in ("create", "edit", "_save", "_audit"):
        monkeypatch.setattr(export.PostgresCoachRegistryRepository, name, denied)
    connection = SyntheticConnection(relational_fixture())
    before = deepcopy(connection.live)
    sealed = asyncio.run(export.read_postgres_snapshot(connection))
    for mode in ("internal", "preview", "production"):
        export.export_registry(sealed, mode, asset_root=assets)
    assert connection.live == before


@pytest.mark.parametrize("mode", ["internal", "preview", "production"])
def test_manifest_exact_bytes_fixed_names_exclusive_and_separate(
    assets, tmp_path, monkeypatch, mode
):
    # Point only the artifact-location constant implicit in __file__ at a disposable
    # test repository, not arbitrary user paths or a real source directory.
    fake = tmp_path / "repo/apps/webapp/src/competence_hub_api/portal/coach_export.py"
    monkeypatch.setattr(export, "__file__", str(fake))
    root = tmp_path / "repo/.tmp/coach4/test-run"
    value = export.export_registry(snapshot(), mode, asset_root=assets)
    manifest = export.write_export(
        value, mode=mode, source_identifier="synthetic-test-v1", output_root=root
    )
    path = root / ("private-internal" if mode == "internal" else "public") / mode
    data = (path / "coaches.json").read_bytes()
    assert manifest["sha256"] == hashlib.sha256(data).hexdigest()
    assert (path / "manifest.json").read_bytes() == canonical_bytes(manifest)
    assert manifest["counts"]["coaches"] == len(value["coaches"])
    assert "timestamp" not in manifest
    with pytest.raises(FileExistsError):
        export.write_export(
            value, mode=mode, source_identifier="synthetic-test-v1", output_root=root
        )
    if mode == "internal":
        with pytest.raises(ValueError):
            read_projection(path / "coaches.json")


@pytest.mark.parametrize(
    "attack", ["root", "source", "internal-as-public", "unknown", "note"]
)
def test_artifact_writer_rejects_escape_secret_extension_and_wrong_mode(
    assets, tmp_path, attack
):
    value = export.export_registry(snapshot(), "internal", asset_root=assets)
    root = Path(export.__file__).resolve().parents[5] / ".tmp/coach4/export-denied-test"
    mode, source = "internal", "synthetic-test"
    if attack == "root":
        root = tmp_path / "outside"
    if attack == "source":
        source = "../../secret"
    if attack == "internal-as-public":
        mode = "preview"
    if attack == "unknown":
        value["secret"] = "DO_NOT_SERIALIZE"
    if attack == "note":
        value["coaches"][0]["revisions"][0]["content"]["qualifications"][0][
            "internal_note"
        ] = "DO_NOT_SERIALIZE"
    with pytest.raises((ValueError, OSError)):
        export.write_export(
            value, mode=mode, source_identifier=source, output_root=root
        )
    assert not root.exists()


def load_cli():
    spec = importlib.util.spec_from_file_location(
        "coach_export_cli",
        Path(__file__).resolve().parents[1] / "scripts/coach-export.py",
    )
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return cli


@pytest.mark.parametrize(
    "option", ["--apply", "--write", "--sync", "--database-url", "--source-file"]
)
def test_cli_has_no_real_data_or_write_switch(option):
    with pytest.raises(SystemExit) as error:
        load_cli().main(
            [
                "--mode",
                "preview",
                "--output-root",
                "unused",
                "--assets",
                "unused",
                option,
            ]
        )
    assert error.value.code != 0


def test_hostile_text_remains_literal_without_schema_injection(assets):
    values = synthetic_registry()
    r = values[0].revisions[0]
    r.content = r.content.model_copy(
        update={"short_intro": '<script>alert("synthetic")</script>'}
    )
    approve(r)
    value = export.export_registry(
        export.RegistrySnapshot.capture(values), "preview", asset_root=assets
    )
    assert (
        json.loads(canonical_bytes(value))["coaches"][0]["short_intro"]
        == '<script>alert("synthetic")</script>'
    )
