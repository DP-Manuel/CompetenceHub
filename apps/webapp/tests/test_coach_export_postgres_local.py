"""Actual PostgreSQL acceptance, opt-in owned disposable loopback55437 only."""

from copy import deepcopy
import hashlib
import os
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.portal import coach_export as export
from competence_hub_api.portal.coach_projection import (
    canonical_bytes,
    generate_projection,
    projection_diff,
)
from competence_hub_api.portal.coach_registry import CoachAggregate, ProfileRevision
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)
from scripts.coach_projection_fixture import (
    synthetic_registry,
    ACTOR,
    PORTRAIT,
    ASSET_REFERENCE,
)
from test_coach_import_postgres_local import database_state


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def seed(owner):
    values = synthetic_registry()
    async with owner.begin() as connection:
        await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
        await connection.execute(
            text(
                "INSERT INTO competence_hub.portal_users(id,display_name,email) VALUES (:id,'Synthetic export operator','synthetic-export@example.invalid')"
            ),
            {"id": ACTOR},
        )
        topic = values[0].revisions[0].topics[0]
        await connection.execute(
            text("INSERT INTO competence_hub.topics(id,name) VALUES (:id,:name)"),
            {"id": topic.id, "name": topic.name},
        )
        for code in topic.categories:
            await connection.execute(
                text(
                    "INSERT INTO competence_hub.topic_category_assignments(topic_id,category_code) VALUES (:id,:code)"
                ),
                {"id": topic.id, "code": code},
            )
        for value in values:
            await connection.execute(
                text(
                    "INSERT INTO competence_hub.coaches(id,display_name,registry_request_id,public_profile_status) VALUES (:id,:name,:request,'not_published')"
                ),
                {
                    "id": value.id,
                    "name": value.display_name,
                    "request": value.request_id,
                },
            )
            staged = deepcopy(value)
            # Publish while active, then pause/offboard through a valid row update;
            # no trigger is disabled to construct this historical snapshot case.
            staged.lifecycle = "active"
            await PostgresCoachRegistryRepository(None)._save(
                connection,
                CoachAggregate(value.id, value.display_name, value.request_id),
                staged,
            )
            if value.lifecycle != "active":
                await connection.execute(
                    text(
                        "UPDATE competence_hub.coaches SET lifecycle_status=:state WHERE id=:id"
                    ),
                    {"state": value.lifecycle, "id": value.id},
                )
    return values


def engines():
    values = [
        os.environ.get("COMPETENCE_HUB_COACH_EXPORT_LOCAL_" + suffix, "")
        for suffix in ("DATABASE_URL", "OWNER_URL")
    ]
    if not all(values):
        pytest.skip("requires owned disposable export PostgreSQL")
    for raw, role in zip(values, ("competence_hub_app", "competence_hub_migrator")):
        url = make_url(raw)
        assert (url.drivername, url.host, url.port, url.database, url.username) == (
            "postgresql+asyncpg",
            "127.0.0.1",
            55437,
            "competence_hub_export_synthetic",
            role,
        )
        assert not url.query
    return tuple(create_async_engine(v, hide_parameters=True) for v in values)


@pytest.mark.anyio
async def test_actual_readonly_snapshot_determinism_and_coach4_parity(
    tmp_path, monkeypatch
):
    engine, owner = engines()
    asset = tmp_path / ASSET_REFERENCE
    asset.parent.mkdir(parents=True)
    asset.write_bytes(PORTRAIT)
    try:
        values = await seed(owner)
        before = await database_state(owner)
        snapshots = []
        for _ in range(3):
            async with engine.connect() as connection:
                snapshots.append(await export.read_postgres_snapshot(connection))
                assert not connection.in_transaction()
        for mode in ("internal", "preview", "production"):
            outputs = [
                canonical_bytes(export.export_registry(s, mode, asset_root=tmp_path))
                for s in snapshots
            ]
            assert outputs[0] == outputs[1] == outputs[2]
            assert len({hashlib.sha256(b).hexdigest() for b in outputs}) == 1
            expected = export.export_registry(
                export.RegistrySnapshot.capture(values), mode, asset_root=tmp_path
            )
            assert outputs[0] == canonical_bytes(expected)
            if mode != "internal":
                public = export.export_registry(snapshots[0], mode, asset_root=tmp_path)
                assert public == generate_projection(values, mode)
                assert not projection_diff(generate_projection(values, mode), public)[
                    "high_attention"
                ]
        assert await database_state(owner) == before  # all relations AND xmin
        print(
            "PASS | Native snapshot repeats: all rows/xmin unchanged; internal/public hashes and COACH-4 parity exact"
        )

        original = export.ReadOnlyRows.fetch

        async def settings_read(reader, table):
            if table == "coaches":
                connection = reader._ReadOnlyRows__connection
                state = (
                    (await connection.execute(text(export.CHECK_SQL))).mappings().one()
                )
                assert dict(state) == {
                    "read_only": "on",
                    "isolation": "repeatable read",
                }
            return await original(reader, table)

        monkeypatch.setattr(export.ReadOnlyRows, "fetch", settings_read)
        async with engine.connect() as connection:
            await export.read_postgres_snapshot(connection)
        monkeypatch.setattr(export.ReadOnlyRows, "fetch", original)
        print("PASS | Actual PostgreSQL transaction is repeatable-read and read-only")

        for statement in (
            "INSERT INTO competence_hub.coaches(display_name) VALUES ('Denied synthetic insertion')",
            "UPDATE competence_hub.coaches SET display_name=display_name",
            "DELETE FROM competence_hub.coaches WHERE false",
            "INSERT INTO competence_hub.audit_events(action,entity_type,outcome) VALUES ('denied','synthetic','success')",
            "UPDATE competence_hub.coach_publications SET state=state",
            "UPDATE competence_hub.coach_assets SET alt_text=alt_text",
            "UPDATE competence_hub.coach_profile_revisions SET status=status",
        ):

            async def attack(reader, table):
                await reader._ReadOnlyRows__connection.execute(text(statement))
                raise AssertionError("write unexpectedly accepted")

            monkeypatch.setattr(export.ReadOnlyRows, "fetch", attack)
            async with engine.connect() as connection:
                with pytest.raises(DBAPIError) as caught:
                    await export.read_postgres_snapshot(connection)
                assert caught.value.orig.sqlstate == "25006"
                assert not connection.in_transaction()
            monkeypatch.setattr(export.ReadOnlyRows, "fetch", original)
        assert await database_state(owner) == before
        print(
            "PASS | PostgreSQL denies INSERT/UPDATE/DELETE, audit/revision/publication/asset writes with SQLSTATE25006; every attempt rolls back"
        )

        # Commit a new draft AND its children after the Coach read but before
        # revision/child reads. READ COMMITTED would mix old version/new children.
        updated = False

        async def concurrent(reader, table):
            nonlocal updated
            rows = await original(reader, table)
            if table == "coaches" and not updated:
                async with owner.begin() as writer:
                    await writer.execute(text("SET LOCAL ROLE competence_hub_owner"))
                    before_coach = deepcopy(values[0])
                    after_coach = deepcopy(before_coach)
                    after_coach.version += 1
                    after_coach.revisions.append(
                        ProfileRevision(
                            UUID(int=902),
                            2,
                            before_coach.revisions[0].content.model_copy(
                                update={
                                    "short_intro": "NEW_CONCURRENT_UNAPPROVED_DRAFT"
                                }
                            ),
                            ACTOR,
                            before_coach.revisions[0].created_at,
                            topics=before_coach.revisions[0].topics,
                        )
                    )
                    await PostgresCoachRegistryRepository(None)._save(
                        writer, before_coach, after_coach
                    )
                updated = True
            return rows

        monkeypatch.setattr(export.ReadOnlyRows, "fetch", concurrent)
        async with engine.connect() as connection:
            concurrent_snapshot = await export.read_postgres_snapshot(connection)
        monkeypatch.setattr(export.ReadOnlyRows, "fetch", original)
        assert updated
        assert canonical_bytes(
            export.export_registry(concurrent_snapshot, "internal", asset_root=tmp_path)
        ) == canonical_bytes(
            export.export_registry(snapshots[0], "internal", asset_root=tmp_path)
        )
        async with engine.connect() as connection:
            fresh = await export.read_postgres_snapshot(connection)
        assert (
            next(c for c in fresh.coaches() if c.id == values[0].id).version
            == values[0].version + 1
        )
        assert (
            next(c for c in fresh.coaches() if c.id == values[0].id)
            .revisions[-1]
            .content.short_intro
            == "NEW_CONCURRENT_UNAPPROVED_DRAFT"
        )
        assert (
            len(
                next(
                    c for c in concurrent_snapshot.coaches() if c.id == values[0].id
                ).revisions
            )
            == 1
        )
        assert (
            len(next(c for c in fresh.coaches() if c.id == values[0].id).revisions) == 2
        )
        print(
            "PASS | Real second-connection commit cannot mix snapshot generations; later export observes committed state"
        )
    finally:
        await engine.dispose()
        await owner.dispose()
