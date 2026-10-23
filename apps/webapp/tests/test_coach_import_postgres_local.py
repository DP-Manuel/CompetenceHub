"""Opt-in, owned loopback55435 PostgreSQL proof; never the VPS tunnel."""

import asyncio
from copy import deepcopy
from datetime import UTC, datetime
import hashlib
import os
import json
import subprocess
import sys
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from scripts.coach_import_fixture import ACTOR, fixture
from competence_hub_api.portal.coach_import import canonical_bytes
from competence_hub_api.portal.coach_registry import (
    CoachRegistryService,
    RegistryDenied,
    public_projection,
)
from competence_hub_api.portal.postgres_coach_import import (
    PostgresCoachImporter,
    local_import_url,
)
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def database_state(owner):
    async with owner.connect() as c:
        tables = (
            (
                await c.execute(
                    text(
                        "SELECT tablename FROM pg_tables WHERE schemaname='competence_hub' ORDER BY tablename"
                    )
                )
            )
            .scalars()
            .all()
        )
        # Names come only from PostgreSQL's schema inventory, not import input.
        return {
            t: [
                dict(r)
                for r in (
                    await c.execute(
                        text(
                            f'SELECT to_jsonb(x) AS data,xmin::text AS row_version FROM competence_hub."{t}" x ORDER BY to_jsonb(x)::text'
                        )
                    )
                ).mappings()
            ]
            for t in tables
        }


@pytest.mark.anyio
async def test_synthetic_import_postgres_atomic_idempotent_revision_lifecycle(
    monkeypatch,
):
    raw = os.environ.get("COMPETENCE_HUB_COACH_IMPORT_LOCAL_DATABASE_URL", "")
    owner_url = os.environ.get("COMPETENCE_HUB_COACH_IMPORT_LOCAL_OWNER_URL", "")
    if not raw or not owner_url:
        pytest.skip("requires owned disposable COACH-3A PostgreSQL container")
    local_import_url(raw)
    u = make_url(owner_url)
    assert (u.drivername, u.host, u.port, u.database, u.username) == (
        "postgresql+asyncpg",
        "127.0.0.1",
        55435,
        "competence_hub_staging",
        "competence_hub_migrator",
    )
    engine = create_async_engine(raw, hide_parameters=True)
    owner = create_async_engine(owner_url, hide_parameters=True)
    records, mapping, topics, assets = fixture()
    importer = PostgresCoachImporter(engine)
    try:
        async with owner.begin() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await c.execute(
                text(
                    "INSERT INTO competence_hub.portal_users(id,display_name,email) VALUES (:id,'Synthetic import operator','synthetic-import@example.invalid')"
                ),
                {"id": ACTOR.user_id},
            )
            await c.execute(
                text(
                    "INSERT INTO competence_hub.user_roles(user_id,role_id) SELECT :id,id FROM competence_hub.roles WHERE code='admin'"
                ),
                {"id": ACTOR.user_id},
            )
            for topic in topics.values():
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
        non_synthetic = deepcopy(records)
        non_synthetic[0]["source_identity"]["source_system"] = "website-preview"
        denied = await importer.apply_synthetic(
            non_synthetic, mapping, assets, actor=ACTOR
        )
        assert denied["issues"] == [{"code": "SYNTHETIC_SCOPE_REQUIRED"}]
        with pytest.raises(RegistryDenied):
            await importer.apply_synthetic(
                records,
                mapping,
                assets,
                actor=SimpleNamespace(user_id=ACTOR.user_id, roles=("internal",)),
            )
        denied = await importer.apply_synthetic(
            records,
            mapping,
            assets,
            actor=SimpleNamespace(user_id=uuid4(), roles=("admin",)),
        )
        assert denied["issues"] == [{"code": "OPERATOR_DENIED"}]
        assert await database_state(owner) == initial
        dry = await importer.dry_run(records, mapping, assets)
        assert dry["result"] == "PASS" and dry["counts"]["CREATE"] == 4
        assert await database_state(owner) == initial
        collision = deepcopy(records)
        collision[3]["profile"]["profile_path"] = records[0]["profile"]["profile_path"]
        result = await importer.apply_synthetic(collision, mapping, assets, actor=ACTOR)
        assert result["result"] == "CONFLICT" and result["business_mutations"] == 0
        assert await database_state(owner) == initial

        original = importer._apply_record
        for failure in ("exception", "cancellation", "database"):
            calls = 0

            async def failing(c, step, actor, now):
                nonlocal calls
                await original(c, step, actor, now)
                calls += 1
                if calls == 2:
                    if failure == "database":
                        await c.execute(text("SELECT 1/0"))
                    elif failure == "cancellation":
                        raise asyncio.CancelledError()
                    else:
                        raise RuntimeError("synthetic interruption")

            monkeypatch.setattr(importer, "_apply_record", failing)
            if failure == "database":
                result = await importer.apply_synthetic(
                    records, mapping, assets, actor=ACTOR
                )
                assert result["issues"] == [{"code": "TRANSACTION_CONFLICT"}]
            else:
                with pytest.raises(
                    asyncio.CancelledError
                    if failure == "cancellation"
                    else RuntimeError
                ):
                    await importer.apply_synthetic(
                        records, mapping, assets, actor=ACTOR
                    )
            assert await database_state(owner) == initial
        monkeypatch.setattr(importer, "_apply_record", original)

        results = await asyncio.gather(
            *[
                importer.apply_synthetic(records, mapping, assets, actor=ACTOR)
                for _ in range(2)
            ]
        )
        assert all(r["result"] == "PASS" for r in results), results
        assert sorted(r["counts"]["CREATE"] for r in results) == [0, 4]
        applied = await database_state(owner)
        assert (
            len(applied["coaches"]) == 4
            and len(applied["coach_profile_revisions"]) == 4
        )
        assert len(applied["topics"]) == 8 and len(applied["topic_categories"]) == 3
        assert len(applied["topic_category_assignments"]) == 18
        assert (
            len(applied["coach_offerings"]) == 3 and len(applied["coach_assets"]) == 1
        )
        assert len(applied["coach_publications"]) == 1
        assert all(r["data"]["portal_user_id"] is None for r in applied["coaches"])
        assert not applied["calendar_offers"]
        sources = {
            r["data"]["source_key"]: r["data"] for r in applied["coach_import_sources"]
        }
        from uuid import UUID

        alpha_id = UUID(sources["coach/alpha"]["coach_id"])
        repo = PostgresCoachRegistryRepository(engine)

        async def projection(environment="preview"):
            coaches = tuple(
                [await repo.get(UUID(s["coach_id"])) for s in sources.values()]
            )
            return canonical_bytes(public_projection(coaches, environment))

        original_projection = await projection()
        assert original_projection == await projection()
        assert b"Synthetic Coach Alpha" in original_projection
        assert (
            public_projection((await repo.get(alpha_id),), "production")["coaches"]
            == []
        )
        dates = {
            r["data"]["kind"]: r["data"]["historical_at"]
            for r in applied["coach_import_evidence"]
        }
        assert dates["person_consent"] is None and dates["preview"] is None
        assert dates["content_review"].startswith("2026-01-01")
        for _ in range(2):
            assert (await importer.dry_run(records, mapping, assets))["counts"][
                "UNCHANGED"
            ] == 4
            result = await importer.apply_synthetic(
                records, mapping, assets, actor=ACTOR
            )
            assert (
                result["counts"]["UNCHANGED"] == 4 and result["business_mutations"] == 0
            )
            assert await database_state(owner) == applied
            assert await projection() == original_projection
        for mode in ("dry-run", "apply"):
            args = [sys.executable, "scripts/coach-import.py", mode, "--local-database"]
            if mode == "apply":
                args.append("--synthetic-apply")
            cli = await asyncio.to_thread(
                subprocess.run, args, capture_output=True, text=True
            )
            assert cli.returncode == 0, cli.stdout
            assert json.loads(cli.stdout)["counts"]["UNCHANGED"] == 4
            assert await database_state(owner) == applied
        normalized = deepcopy(records)
        normalized[0]["profile"]["short_intro"] = "  Synthetic   introduction. "
        normalized[0]["topics"][1]["label"] = "stress Management"
        normalized[0]["offerings"].reverse()
        normalized[0]["provenance"]["technical_revision"] = "run-2"
        assert (
            await importer.apply_synthetic(normalized, mapping, assets, actor=ACTOR)
        )["business_mutations"] == 0
        assert await database_state(owner) == applied

        changed = deepcopy(records)
        changed[0]["profile"]["short_intro"] = "Changed synthetic introduction."
        changed[0]["profile"]["display_name"] = "Renamed Synthetic Alpha"
        result = await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR)
        assert result["counts"]["REVISION"] == 1 and result["business_mutations"] == 1
        revised = await database_state(owner)
        alpha = await repo.get(alpha_id)
        assert (
            alpha.id == alpha_id
            and len(alpha.revisions) == 2
            and alpha.revisions[-1].status == "draft"
        )
        assert (
            alpha.revisions[-1].content.profile_path
            == records[0]["profile"]["profile_path"]
        )
        assert not alpha.revisions[-1].approvals
        assert (
            len(revised["coach_profile_revisions"]) == 5
            and len(revised["coaches"]) == 4
        )
        assert len(revised["coach_import_items"]) == len(applied["coach_import_items"])
        assert {(r["data"]["logical_id"]) for r in revised["coach_import_items"]} == {
            r["data"]["logical_id"] for r in applied["coach_import_items"]
        }
        # Offer and asset snapshots are copied into a revision, not new logical items.
        assert (
            len(revised["coach_offerings"]) == 5 and len(revised["coach_assets"]) == 2
        )
        assert await projection() == original_projection
        assert (await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR))[
            "business_mutations"
        ] == 0
        assert await database_state(owner) == revised

        changed[0]["offerings"][0]["content"].update(
            title="Changed synthetic workshop", active=False
        )
        changed[0]["offerings"].append(
            {
                "key": "new-offer",
                "content": {
                    "title": "New synthetic offer",
                    "type": "individual",
                    "ordering": 2,
                },
            }
        )
        result = await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR)
        assert result["counts"]["EDIT_DRAFT"] == 1
        assert len((await repo.get(alpha_id)).revisions) == 2
        after_offer = await database_state(owner)
        assert (
            len(after_offer["coach_import_items"])
            == len(applied["coach_import_items"]) + 1
        )
        assert (await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR))[
            "business_mutations"
        ] == 0
        assert await database_state(owner) == after_offer

        for conflict in (
            "missing",
            "path",
            "identity",
            "asset_bytes",
            "same_reference",
            "publication",
        ):
            bad = deepcopy(changed)
            bad_assets = dict(assets)
            if conflict == "missing":
                bad[0]["offerings"].pop()
            elif conflict == "path":
                bad[0]["profile"]["profile_path"] = "/coaches/renamed-alpha/"
            elif conflict == "identity":
                bad[0]["expected_coach_id"] = sources["coach/beta"]["coach_id"]
            elif conflict in {"asset_bytes", "same_reference"}:
                ref = bad[0]["assets"][0]["content"]["reference"]
                bad_assets[ref] = b"replacement synthetic bytes"
                if conflict == "same_reference":
                    bad[0]["assets"][0]["content"]["sha256"] = hashlib.sha256(
                        bad_assets[ref]
                    ).hexdigest()
            else:
                bad[0]["publication"]["evidence"][0][
                    "source"
                ] = "synthetic:other-consent"
            result = await importer.apply_synthetic(
                bad, mapping, bad_assets, actor=ACTOR
            )
            assert (
                result["result"] == "CONFLICT" and result["business_mutations"] == 0
            ), conflict
            assert await database_state(owner) == after_offer

        new_ref = "images/coaches/synthetic-alpha-v2.png"
        new_bytes = b"replacement synthetic bytes"
        assets[new_ref] = new_bytes
        changed[0]["assets"][0]["content"].update(
            reference=new_ref, sha256=hashlib.sha256(new_bytes).hexdigest()
        )
        assert (await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR))[
            "counts"
        ]["EDIT_DRAFT"] == 1
        alpha = await repo.get(alpha_id)
        assert (
            alpha.revisions[0].content.assets[0].reference
            != alpha.revisions[-1].content.assets[0].reference
        )
        assert await projection() == original_projection

        # Canonical taxonomy changes are revision-worthy, not mere technical metadata.
        async with owner.begin() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await c.execute(
                text(
                    "UPDATE competence_hub.topics SET name='Renamed synthetic theme' WHERE id=:id"
                ),
                {"id": mapping.topics[0].topic_id},
            )
        assert (await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR))[
            "counts"
        ]["EDIT_DRAFT"] == 1
        alpha = await repo.get(alpha_id)
        assert alpha.revisions[-1].topics[0].name == "Renamed synthetic theme"
        assert alpha.revisions[0].topics[0].name != "Renamed synthetic theme"
        assert (await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR))[
            "counts"
        ]["UNCHANGED"] == 4

        # Technical provenance-only changes never touch domain or business audit.
        before_metadata = await database_state(owner)
        changed[1]["provenance"]["source_ref"] = "synthetic:reviewed-revision"
        result = await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR)
        assert result["counts"]["METADATA"] == 1 and result["business_mutations"] == 0
        after_metadata = await database_state(owner)
        assert all(
            after_metadata[t] == v
            for t, v in before_metadata.items()
            if t != "coach_import_sources"
        )

        # Database constraints independently reject identity theft and evidence ambiguity.
        statements = [
            "UPDATE competence_hub.coach_import_sources SET source_key='stolen' WHERE source_key='coach/alpha'",
            "UPDATE competence_hub.coach_import_items SET logical_id=gen_random_uuid() WHERE source_key='coach/alpha'",
            "DELETE FROM competence_hub.coach_import_sources WHERE source_key='coach/alpha'",
            "UPDATE competence_hub.coach_import_evidence SET historical_at=now()",
            "INSERT INTO competence_hub.coach_import_evidence(source_system,source_key,evidence_key,coach_id,revision_id,kind,environment,evidence_source) SELECT source_system,source_key,'invalid-env',coach_id,last_revision_id,'production',NULL,'synthetic:bad' FROM competence_hub.coach_import_sources WHERE source_key='coach/alpha'",
            "UPDATE competence_hub.coach_profile_revisions SET profile_path='/coaches/synthetic-alpha/' WHERE coach_id=(SELECT coach_id FROM competence_hub.coach_import_sources WHERE source_key='coach/beta')",
        ]
        for sql in statements:
            with pytest.raises(DBAPIError):
                async with engine.begin() as c:
                    await c.execute(text(sql))
        assert await database_state(owner) == after_metadata

        # 2026 active -> 2027 inactive -> 2028 reactivated: domain workflow, never an import side effect.
        service = CoachRegistryService(repo)
        alpha = await repo.get(alpha_id)

        async def mutate(operation, year=2028, **kw):
            nonlocal alpha
            alpha = await service.mutate(
                actor=ACTOR,
                coach_id=alpha.id,
                expected_version=alpha.version,
                operation=operation,
                now=datetime(year, 1, 1, tzinfo=UTC),
                **kw,
            )

        await mutate("lifecycle", year=2027, lifecycle="inactive")
        assert (
            alpha.lifecycle == "inactive"
            and not public_projection((alpha,), "preview")["coaches"]
        )
        assert (await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR))[
            "result"
        ] == "CONFLICT"
        assert (await repo.get(alpha_id)).lifecycle == "inactive"
        await mutate("revision", content=alpha.revisions[-1].content)
        revision_id = alpha.revisions[-1].id
        await mutate("submit", revision_id=revision_id)
        for kind in ("content_review", "person_consent", "preview"):
            await mutate(
                "approve",
                revision_id=revision_id,
                kind=kind,
                evidence_ref="synthetic:2028-fresh",
            )
        await mutate("lifecycle", lifecycle="active")
        await mutate("publish", revision_id=revision_id, environment="preview")
        assert (
            alpha.id == alpha_id
            and alpha.lifecycle == "active"
            and len(alpha.revisions) == 3
        )
        assert (await importer.apply_synthetic(changed, mapping, assets, actor=ACTOR))[
            "result"
        ] == "CONFLICT"
        assert len((await database_state(owner))["coaches"]) == 4
        assert await projection() == await projection()
        print(
            "COACH3A_POSTGRES=PASS NOOP_2_3=PASS ROLLBACK_EXCEPTION_CANCEL_SQL=PASS LIFECYCLE_SAME_UUID=PASS"
        )
    finally:
        await engine.dispose()
        await owner.dispose()
