"""Opt-in disposable PG16 proof of the real adapter, NOT real-import approval.

Only this test substitutes synthetic policy approval and window metadata. It
does not test/claim a real encrypted backup or restore, read a real manifest,
contact the VPS, or change production guards. The parent destroys the entire
owned container; this test deliberately performs no cleanup DELETE/TRUNCATE.
"""

from copy import deepcopy
import os
import re
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.portal.coach_registry import ProfileContent, public_projection
from competence_hub_api.portal.coach_target import subjects
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)
from test_coach3b_real_apply import runner
from test_coach3b_real_manifest import NOW, closure, manifest_api, policy_fixture


@pytest.fixture
def anyio_backend():
    return "asyncio"


def nine_coach_fixture(*, reviewed_on):
    """Derived synthetic counts, never the actual reviewed manifest/hash."""
    preview, catalogue, assets = policy_fixture(portrait=True)
    production, _, production_assets = policy_fixture(family=True, portrait=True)
    assert assets == production_assets
    rows = []
    for index in range(9):
        row = deepcopy((production if index < 3 else preview)["coaches"][0])
        name = f"Synthetic local Coach {index + 1}"
        path = f"/coaches/synthetic-real-local-{index + 1}/"
        row["source_identity"] = {
            "source_system": "synthetic-local-coach3b",
            "source_key": f"coach/local-{index + 1}",
        }
        row.update(display_name=name, profile_path=path)
        row["content"].update(display_name=name, profile_path=path)
        row["topics"] = [
            deepcopy(preview["topic_rules"][i % 8]) for i in (index, index + 1)
        ]
        content = ProfileContent.model_validate(row["content"])
        row["candidate_content_sha256"] = closure.digest(row["content"])
        hashes = subjects(content)
        hashes["profile", "profile"] = closure.digest(
            {
                "logical_content": row["content"],
                "canonical_topics": row["topics"],
            }
        )
        for evidence in row["evidence_plan"]:
            evidence.update(
                candidate_subject_sha256=hashes[
                    evidence["subject_type"], evidence["subject_key"]
                ],
                approved_by="Synthetic local reviewer",
                approved_on=reviewed_on.isoformat(),
                approved_at=None,
                evidence_reference="synthetic:local-policy-review",
            )
            evidence["basis"].update(
                approved_by="Synthetic local reviewer",
                approved_on=reviewed_on.isoformat(),
            )
        for attestation in row["attestation_plan"]:
            attestation.update(
                reference="synthetic:local-policy-attestation/" + attestation["kind"],
                historical_at=None,
            )
        for environment in ("preview", "production"):
            row["projection_" + environment] = (
                closure.dry_projection(content, row["topics"], environment)
                if row["rights"][environment] == "APPROVED"
                else None
            )
        rows.append(row)
    contents = [row["content"] for row in rows]
    counts = {
        "coaches": len(rows),
        "profile_revisions": len(rows),
        "topic_links": sum(len(row["topics"]) for row in rows),
        "competencies": sum(len(c["competencies"]) for c in contents),
        "public_qualifications": sum(
            sum(q["public"] for q in c["qualifications"]) for c in contents
        ),
        "offering_families": sum(len(c["offering_families"]) for c in contents),
        "offering_formats": sum(len(c["offerings"]) for c in contents),
        "variants_add_ons": sum(
            sum(len(v["variants"]) for v in c["offering_families"] + c["offerings"])
            for c in contents
        ),
        "assets": sum(len(c["assets"]) for c in contents),
        "object_evidence_records": sum(len(row["evidence_plan"]) for row in rows),
        "current_attestation_records": sum(
            len(row["attestation_plan"]) for row in rows
        ),
        "canonical_topic_lookups": len(preview["topic_rules"]),
        "preview_publications": sum(
            row["projection_preview"] is not None for row in rows
        ),
        "production_publications": sum(
            row["projection_production"] is not None for row in rows
        ),
    }
    return (
        {
            "schema": "SYNTHETIC_LOCAL_ADAPTER_TEST_ONLY",
            "approval": "POLICY_ONLY_NO_REAL_APPROVAL",
            "target": dict(manifest_api.TARGET),
            "coaches": rows,
            "topic_rules": deepcopy(preview["topic_rules"]),
            "counts": counts,
        },
        catalogue,
        assets,
    )


def test_nine_coach_fixture_is_bindable_but_has_no_real_approval():
    manifest, catalogue, assets = nine_coach_fixture(reviewed_on=NOW.date())
    with pytest.raises(ValueError):
        manifest_api.verify_manifest(manifest)
    records, contract = manifest_api._bind_review(manifest, catalogue, assets, now=NOW)
    assert contract.version == "coach-import-v2" and len(records) == 9
    assert len({r["source_identity"]["source_key"] for r in records}) == 9
    assert len({r["profile"]["profile_path"] for r in records}) == 9
    assert sum("production" in r["publication"]["published"] for r in records) == 3
    assert manifest["counts"]["public_qualifications"] == 9
    assert manifest["counts"]["assets"] == 9


@pytest.mark.anyio
async def test_real_adapter_local_atomic_apply_and_exact_repeat(monkeypatch):
    app_url = os.environ.get("COMPETENCE_HUB_COACH3B_LOCAL_APP_URL", "")
    owner_url = os.environ.get("COMPETENCE_HUB_COACH3B_LOCAL_OWNER_URL", "")
    nonce = os.environ.get("COMPETENCE_HUB_COACH3B_LOCAL_NONCE", "")
    if not any((app_url, owner_url, nonce)):
        pytest.skip(
            "requires both URLs from the owned disposable COACH-3B local harness"
        )
    assert app_url and owner_url and re.fullmatch(r"[a-f0-9]{32}", nonce)
    # Exact loopback/port/database/role guards run before constructing engines.
    # Never print either URL; these two explicit variables are the local opt-in.
    runner.target_url(app_url, "competence_hub_app")
    runner.target_url(owner_url, "competence_hub_migrator")
    engine = create_async_engine(app_url, hide_parameters=True)
    owner = create_async_engine(owner_url, hide_parameters=True)
    try:
        async with owner.connect() as c:
            marker = await c.scalar(
                text(
                    "SELECT shobj_description(oid,'pg_database') FROM pg_database WHERE datname=current_database()"
                )
            )
            assert (
                marker == "synthetic-coach3b-owned:" + nonce
            ), "Refuse non-owned DB or VPS tunnel before any synthetic write"
            now = await c.scalar(text("SELECT clock_timestamp()"))
        manifest, _, assets = nine_coach_fixture(reviewed_on=now.date())

        def policy_only(value):
            assert value is manifest
            assert value["approval"] == "POLICY_ONLY_NO_REAL_APPROVAL"
            assert value["target"] == manifest_api.TARGET

        def bind_policy(value, catalogue, asset_bytes, *, now):
            policy_only(value)
            return manifest_api._bind_review(value, catalogue, asset_bytes, now=now)

        def parity_policy(value, preview, production):
            policy_only(value)
            manifest_api._verify_projection_rows(value, preview, production)

        # Fixture-scoped substitutions exercise the actual adapter/SQL writer.
        # Pinned real approval remains tested separately; no production code edits.
        monkeypatch.setattr(manifest_api, "verify_manifest", policy_only)
        monkeypatch.setattr(manifest_api, "bind_manifest", bind_policy)
        monkeypatch.setattr(manifest_api, "verify_projection_parity", parity_policy)
        importer = runner.RealCoachImporter(
            engine, owner, manifest, assets, closure.digest(manifest)
        )
        preflight = await importer.target_preflight(require_schema9=True)
        assert preflight["migrations"] == runner.MIGRATIONS
        assert preflight["active_admin_candidates"] == preflight["active_topics"] == 0
        assert (
            "EXISTING_ACTIVE_ADMIN_REQUIRED_NO_ONBOARDING"
            in preflight["execution_blockers"]
        )
        assert all(
            value["count"] == 0
            for name, value in preflight["row_versions"].items()
            if name not in {"roles", "topic_categories"}
        ), "local test requires a fresh empty owned schema before any seed writes"
        async with owner.begin() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            operator_id = await c.scalar(text("""
                INSERT INTO competence_hub.portal_users(display_name,email)
                VALUES ('Synthetic local adapter operator','coach3b-local@example.invalid')
                RETURNING id
            """))
            role_id = await c.scalar(
                text("""
                INSERT INTO competence_hub.user_roles(user_id,role_id)
                SELECT :id,id FROM competence_hub.roles WHERE code='admin' AND active
                RETURNING role_id
            """),
                {"id": operator_id},
            )
            assert role_id is not None
            for topic in manifest["topic_rules"]:
                topic_id = await c.scalar(
                    text("""
                    INSERT INTO competence_hub.topics(name,active) VALUES (:name,true) RETURNING id
                """),
                    {"name": topic["name"]},
                )
                for category in topic["categories"]:
                    await c.execute(
                        text("""
                        INSERT INTO competence_hub.topic_category_assignments(topic_id,category_code)
                        VALUES (:id,:category)
                    """),
                        {"id": topic_id, "category": category},
                    )

        async def snapshot():
            async with owner.connect() as c:
                return await runner.row_versions(c)

        initial = await snapshot()
        preflight = await importer.target_preflight(require_schema9=True)
        assert (
            preflight["active_admin_candidates"] == 1
            and preflight["active_topics"] == 8
        )
        assert preflight["writes"] == 0 and await snapshot() == initial
        assert preflight["execution_blockers"] == []
        dry = await importer.dry_run_real()
        assert dry["result"] == "PASS" and dry["counts"]["CREATE"] == 9
        assert dry["business_mutations"] == 0 and await snapshot() == initial
        async with engine.begin() as c:
            with pytest.raises(
                runner.GateError, match="EXISTING_ACTIVE_ADMIN_REQUIRED"
            ):
                await importer._operator(c, UUID(int=0))
        arguments = {
            "operator_id": operator_id,
            "plan_sha256": dry["plan_sha256"],
            "window_proof": None,
            "window_proof_sha256": None,
        }
        with pytest.raises((runner.GateError, TypeError)):
            await importer._apply_transaction_candidate(**arguments)
        assert await snapshot() == initial

        proof_calls = []

        def synthetic_window(path, sha, *, manifest_sha256, operator_id, now):
            assert path == "SYNTHETIC_LOCAL_WINDOW_ONLY"
            assert sha == closure.digest({"scope": path})
            assert manifest_sha256 == importer.manifest_sha256
            assert now.utcoffset() is not None
            proof_calls.append(operator_id)
            return {"scope": path, "actual_backup_restore_evidence": False}

        # This substitutes only the proof reader, NOT an actual restore PASS.
        monkeypatch.setattr(runner, "read_window_proof", synthetic_window)
        arguments.update(
            window_proof="SYNTHETIC_LOCAL_WINDOW_ONLY",
            window_proof_sha256=closure.digest(
                {"scope": "SYNTHETIC_LOCAL_WINDOW_ONLY"}
            ),
        )
        with pytest.raises(runner.GateError, match="EXISTING_ACTIVE_ADMIN_REQUIRED"):
            await importer._apply_transaction_candidate(
                **{**arguments, "operator_id": UUID(int=0)}
            )
        with pytest.raises(runner.GateError, match="STALE_DRY_RUN"):
            await importer._apply_transaction_candidate(
                **{**arguments, "plan_sha256": "0" * 64}
            )
        assert await snapshot() == initial
        original_apply = importer._apply_record
        calls = 0

        async def fail_second(c, step, actor, now):
            nonlocal calls
            await original_apply(c, step, actor, now)
            calls += 1
            if calls == 2:
                raise RuntimeError("SYNTHETIC_SECOND_RECORD_INTERRUPTION")

        monkeypatch.setattr(importer, "_apply_record", fail_second)
        with pytest.raises(RuntimeError, match="SYNTHETIC_SECOND_RECORD_INTERRUPTION"):
            await importer._apply_transaction_candidate(**arguments)
        assert calls == 2 and await snapshot() == initial
        monkeypatch.setattr(importer, "_apply_record", original_apply)
        applied = await importer._apply_transaction_candidate(**arguments)
        assert applied["result"] == "PASS" and applied["counts"]["CREATE"] == 9
        assert applied["business_mutations"] == 9 and applied["parity"] == "PASS"
        assert all(
            manifest["counts"][k] == v for k, v in applied["verified_counts"].items()
        )
        committed = await snapshot()
        assert runner.unchanged_outside_registry(initial, committed)
        assert (
            committed["portal_users"]["count"] == committed["user_roles"]["count"] == 1
        )
        async with owner.connect() as c:
            identities = await runner.rows(
                c,
                """
                SELECT s.source_system,s.source_key,s.coach_id,s.profile_path,r.profile_path AS revision_path
                FROM competence_hub.coach_import_sources s
                JOIN competence_hub.coach_profile_revisions r ON r.id=s.last_revision_id
            """,
            )
            assert len(identities) == len({r["coach_id"] for r in identities}) == 9
            assert {
                (r["source_system"], r["source_key"], r["profile_path"])
                for r in identities
            } == {
                (
                    r["source_identity"]["source_system"],
                    r["source_identity"]["source_key"],
                    r["profile_path"],
                )
                for r in manifest["coaches"]
            }
            assert all(r["profile_path"] == r["revision_path"] for r in identities)
            assert (
                await c.scalar(text("""SELECT count(*) FROM competence_hub.coaches
                WHERE portal_user_id IS NOT NULL OR public_profile_path IS NOT NULL"""))
                == 0
            )
            assert (
                await c.scalar(
                    text("""SELECT count(*) FROM competence_hub.coach_import_evidence
                WHERE historical_at IS NOT NULL""")
                )
                == 0
            )
            assert (
                await c.scalar(
                    text("SELECT count(*) FROM competence_hub.coach_import_evidence")
                )
                == manifest["counts"]["current_attestation_records"]
            )
            evidence = await runner.rows(
                c,
                "SELECT approved_at,approved_on FROM competence_hub.coach_object_evidence",
            )
            assert len(evidence) == manifest["counts"]["object_evidence_records"]
            assert all(
                r["approved_at"] is None and r["approved_on"] == now.date()
                for r in evidence
            )
            repo = PostgresCoachRegistryRepository(engine, connection=c)
            coaches = tuple([await repo.get(row["coach_id"]) for row in identities])
            preview, production = [
                public_projection(coaches, env) for env in ("preview", "production")
            ]
            assert len(preview["coaches"]) == 9 and len(production["coaches"]) == 3
            manifest_api._verify_projection_rows(manifest, preview, production)
        for _ in range(2):
            repeated_dry = await importer.dry_run_real()
            assert repeated_dry["counts"]["UNCHANGED"] == 9
            repeated = await importer._apply_transaction_candidate(
                **{**arguments, "plan_sha256": repeated_dry["plan_sha256"]}
            )
            assert (
                repeated["counts"]["UNCHANGED"] == 9
                and repeated["business_mutations"] == 0
            )
            assert (
                repeated["preview_projection_sha256"]
                == applied["preview_projection_sha256"]
            )
            assert (
                repeated["production_projection_sha256"]
                == applied["production_projection_sha256"]
            )
            assert await snapshot() == committed
        assert len(proof_calls) == 6
        print(
            "PASS | synthetic local real-adapter CREATE9, rollback, repeat2/3 MVCC no-op, Preview9/Production3; NOT real approval or backup/restore evidence"
        )
    finally:
        await engine.dispose()
        await owner.dispose()
