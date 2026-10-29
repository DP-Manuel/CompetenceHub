"""Real additive 0008 -> 0009 upgrade, owned disposable localhost55436 only."""

from datetime import UTC, datetime
from dataclasses import replace
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.portal.coach_registry import (
    CoachRegistryService,
    RegistryConflict,
    public_projection,
)
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)
from competence_hub_api.portal.postgres_coach_target import write_evidence
from scripts.coach_target_cases import (
    target_profile,
    three_family_profile,
    approvals_for,
)
from test_coach_registry import ACTOR, TOPIC_ID, change, profile
from test_coach_import_postgres_local import database_state


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_upgrade_existing_rows_and_lossless_postgres_target():
    values = [
        os.environ.get("COMPETENCE_HUB_COACH_TARGET_LOCAL_" + s, " ").strip()
        for s in ("DATABASE_URL", "OWNER_URL")
    ]
    if not all(values):
        pytest.skip("requires owned disposable target PostgreSQL")
    for raw, role in zip(values, ("competence_hub_app", "competence_hub_migrator")):
        u = make_url(raw)
        assert (u.drivername, u.host, u.port, u.database, u.username) == (
            "postgresql+asyncpg",
            "127.0.0.1",
            55436,
            "competence_hub_staging",
            role,
        )
        assert not u.query
    engine, owner = [create_async_engine(v, hide_parameters=True) for v in values]
    try:
        async with owner.begin() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await c.execute(
                text(
                    "INSERT INTO competence_hub.portal_users(id,display_name,email) VALUES (:id,'Synthetic upgrade admin','synthetic-target-upgrade@example.invalid')"
                ),
                {"id": ACTOR.user_id},
            )
            await c.execute(
                text(
                    "INSERT INTO competence_hub.topics(id,name) VALUES (:id,'Synthetic target topic')"
                ),
                {"id": TOPIC_ID},
            )
        repo = PostgresCoachRegistryRepository(engine)
        service = CoachRegistryService(repo)
        legacy = await service.create(
            actor=ACTOR,
            display_name="Synthetic legacy",
            request_id=uuid4(),
            now=datetime.now(UTC),
        )
        legacy = await change(service, legacy, "revision", content=profile())
        legacy = await change(
            service, legacy, "submit", revision_id=legacy.revisions[0].id
        )
        for kind in ("content_review", "person_consent", "preview"):
            legacy = await change(
                service,
                legacy,
                "approve",
                revision_id=legacy.revisions[0].id,
                kind=kind,
                evidence_ref="synthetic:legacy",
            )
        legacy = await change(service, legacy, "lifecycle", lifecycle="active")
        legacy = await change(
            service,
            legacy,
            "publish",
            revision_id=legacy.revisions[0].id,
            environment="preview",
        )
        before = await database_state(owner)
        projection_before = public_projection((legacy,), "preview")
        sql = (
            Path("database/migrations/0009_coach_lossless_target.sql")
            .read_text(encoding="utf-8")
            .split("\n", 1)[1]
        )
        async with owner.connect() as c:
            raw = await c.get_raw_connection()
            await raw.driver_connection.execute(sql)
        # A migration is an offline gate; reconnect exactly as a restarted runtime.
        await engine.dispose()
        await owner.dispose()
        after = await database_state(owner)
        for table, oldrows in before.items():
            if table == "schema_migrations":
                continue
            newrows = after[table]
            if table == "coach_profile_revisions":
                newrows = [
                    dict(
                        r,
                        data={
                            k: v
                            for k, v in r["data"].items()
                            if k
                            not in {
                                "target_version",
                                "presentation",
                                "boundaries",
                                "subject_hashes",
                            }
                        },
                    )
                    for r in newrows
                ]
            if table == "coach_offerings":
                newrows = [
                    dict(
                        r,
                        data={
                            k: v
                            for k, v in r["data"].items()
                            if k not in {"item_key", "family_key", "metadata"}
                        },
                    )
                    for r in newrows
                ]
            assert newrows == oldrows, table
        loaded = await repo.get(legacy.id)
        assert loaded.revisions[0].content.target_version == 0
        assert loaded.revisions[0].object_evidence == []
        assert public_projection((loaded,), "preview") == projection_before
        print(
            "PASS | Real schema0008->0009 preserves all old rows/xmin and legacy projection; no fabricated consent"
        )
        for name in ("Alpha", "Beta", "Gamma", "Delta", "Epsilon"):
            content = (
                three_family_profile() if name == "Epsilon" else target_profile(name)
            )
            coach = await service.create(
                actor=ACTOR,
                display_name=content.display_name,
                request_id=uuid4(),
                now=datetime.now(UTC),
            )
            coach = await change(service, coach, "revision", content=content)
            assert (await repo.get(coach.id)).revisions[0].content == content
            coach = await change(
                service, coach, "submit", revision_id=coach.revisions[0].id
            )
            rid = coach.revisions[0].id
            for kind in ("content_review", "person_consent", "preview", "production"):
                coach = await change(
                    service,
                    coach,
                    "approve",
                    revision_id=rid,
                    kind=kind,
                    evidence_ref="synthetic:review",
                )
            coach = await change(service, coach, "lifecycle", lifecycle="active")
            with pytest.raises(RegistryConflict):
                await change(
                    service, coach, "publish", revision_id=rid, environment="preview"
                )
            env = "production" if name == "Beta" else "preview"
            for e in approvals_for(coach.revisions[0], env):
                coach = await change(
                    service, coach, "evidence", revision_id=rid, evidence=e
                )
            coach = await change(
                service, coach, "publish", revision_id=rid, environment=env
            )
            loaded = await repo.get(coach.id)
            assert loaded.revisions[0].content == content
            assert len(loaded.revisions[0].object_evidence) == len(
                approvals_for(loaded.revisions[0], env)
            )
            out = public_projection((loaded,), env)
            assert out == public_projection((await repo.get(coach.id),), env)
            for token in (
                "PRIVATE",
                "private:",
                "evidence_reference",
                "internal_note",
                "subject_hash",
                "999",
            ):
                assert token not in json.dumps(out)
            otherenv = "preview" if env == "production" else "production"
            prototype = loaded.revisions[0].object_evidence[0]
            for patch in (
                {"key": "wrong-hash", "subject_hash": "0" * 64},
                {"key": "wrong-object", "subject_key": "missing"},
                {"key": "future-day", "approved_on": datetime(2099, 1, 1).date()},
            ):
                bad = replace(
                    loaded.revisions[0],
                    object_evidence=[
                        replace(
                            prototype,
                            id=uuid4(),
                            value=prototype.value.model_copy(update=patch),
                        )
                    ],
                )
                with pytest.raises(DBAPIError):
                    async with engine.begin() as c:
                        await write_evidence(c, coach.id, bad, None)
            bad = replace(
                loaded.revisions[0],
                object_evidence=[
                    replace(
                        prototype,
                        id=uuid4(),
                        value=prototype.value.model_copy(
                            update={"key": "foreign-coach"}
                        ),
                    )
                ],
            )
            with pytest.raises(DBAPIError):
                async with engine.begin() as c:
                    await write_evidence(c, legacy.id, bad, None)
            with pytest.raises(RegistryConflict):
                await change(
                    service, coach, "publish", revision_id=rid, environment=otherenv
                )
            for query in (
                "UPDATE competence_hub.coach_qualifications SET canonical_title='tampered' WHERE revision_id=:id",
                "DELETE FROM competence_hub.coach_offering_families WHERE revision_id=:id",
                "UPDATE competence_hub.coach_object_evidence SET status='approved' WHERE revision_id=:id",
                "DELETE FROM competence_hub.coach_object_evidence WHERE revision_id=:id",
                "UPDATE competence_hub.coach_profile_revisions SET target_version=0 WHERE id=:id",
            ):
                with pytest.raises(DBAPIError):
                    async with engine.begin() as c:
                        await c.execute(text(query), {"id": rid})
            with pytest.raises(DBAPIError):
                async with engine.begin() as c:
                    await c.execute(
                        text(
                            "INSERT INTO competence_hub.coach_publications(coach_id,environment,revision_id,state,profile_path,actor_id,occurred_at) VALUES (:coach,:env,:id,'published',:path,:actor,now())"
                        ),
                        {
                            "coach": coach.id,
                            "env": otherenv,
                            "id": rid,
                            "path": content.profile_path,
                            "actor": ACTOR.user_id,
                        },
                    )
            rejected = approvals_for(loaded.revisions[0], env)[0].model_copy(
                update={"key": "revoke", "status": "rejected"}
            )
            coach = await change(
                service, coach, "evidence", revision_id=rid, evidence=rejected
            )
            assert (await repo.get(coach.id)).publications[env].state == "withdrawn"
            coach = await change(service, coach, "revision", content=content)
            assert coach.revisions[-1].content.qualifications[0].key == "q-public"
            assert not (await repo.get(coach.id)).revisions[-1].object_evidence
        print(
            "PASS | Five synthetic rich Coaches round-trip roles/qualifications/families/formats/variants/unknown history and exact environment consent"
        )
    finally:
        await engine.dispose()
        await owner.dispose()
