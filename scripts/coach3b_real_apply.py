"""Phase-A real Registry candidate; public APPLY is currently hard-disabled.

Default VALIDATE is offline. Database modes require the dedicated operator's
process-only app/owner URLs. Backup/restore and native UI acceptance belong to
the enclosing approved maintenance window, not this database writer.
The private transaction candidate is exercised only by the owned local harness.
No account/taxonomy/site provisioning or enabling switch exists here.
"""

import argparse
import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import re
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.portal.coach_registry import (
    RegistryConflict,
    TopicSnapshot,
    public_projection,
)
from competence_hub_api.portal.coach_target import digest
from competence_hub_api.portal.postgres_coach_import import (
    PostgresCoachImporter,
    plan_records,
)
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
    rows,
)

DATABASE = "competence_hub_staging"
SCHEMA = "competence_hub"
MIGRATIONS = tuple(f"{i:04}" for i in range(1, 10))
HEX = re.compile(r"^[a-f0-9]{64}$")
ROOT = Path(__file__).resolve().parents[1]
REGISTRY_TABLES = frozenset(
    {
        "coaches",
        "coach_profile_revisions",
        "coach_profile_labels",
        "coach_profile_topics",
        "coach_profile_topic_categories",
        "coach_offerings",
        "coach_assets",
        "coach_profile_approvals",
        "coach_publications",
        "coach_import_sources",
        "coach_import_items",
        "coach_import_evidence",
        "coach_public_roles",
        "coach_qualifications",
        "coach_offering_families",
        "coach_object_evidence",
        "audit_events",
    }
)


class GateError(ValueError):
    """Only the fixed code is exposed, never SQL/URL/input exception text."""


def require(condition, code):
    if not condition:
        raise GateError(code)


def target_url(raw, role):
    try:
        url = make_url(raw)
        valid = (
            url.drivername == "postgresql+asyncpg"
            and url.host == "127.0.0.1"
            and url.port == 55432
            and url.database == DATABASE
            and url.username == role
            and bool(url.password)
            and not url.query
        )
    except Exception:
        valid = False
    require(valid, "TARGET_URL_REJECTED")


def read_manifest(path, expected_sha256):
    target = Path(path).resolve()
    require(
        target.is_relative_to(ROOT / ".tmp")
        and not Path(path).is_symlink()
        and bool(HEX.fullmatch(expected_sha256)),
        "MANIFEST_PATH_OR_HASH_REJECTED",
    )
    require(target.stat().st_size <= 4 * 1024 * 1024, "MANIFEST_SIZE_REJECTED")
    raw = target.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected_sha256, "MANIFEST_HASH_CHANGED")
    from coach3b_real_manifest import verify_manifest

    manifest = json.loads(raw)
    verify_manifest(manifest)
    return manifest


def read_window_proof(path, expected_sha256, *, manifest_sha256, operator_id, now):
    """Accept only a fresh, exact protected window record, not arbitrary hashes.

    This record must be produced from actual backup/restore verification by the
    surrounding operator. It is not an alternative to executing those checks.
    """
    target = Path(path).resolve()
    require(
        target.is_relative_to(ROOT / ".tmp") and not Path(path).is_symlink(),
        "WINDOW_PROOF_PATH_REJECTED",
    )
    require(target.stat().st_size <= 65536, "WINDOW_PROOF_SIZE_REJECTED")
    raw = target.read_bytes()
    require(
        bool(HEX.fullmatch(expected_sha256 or ""))
        and hashlib.sha256(raw).hexdigest() == expected_sha256,
        "WINDOW_PROOF_HASH_CHANGED",
    )
    value = json.loads(raw)
    require(
        value.get("schema") == 1
        and value.get("purpose") == "COACH3B_ONE_WINDOW_READINESS"
        and value.get("target_database") == DATABASE
        and value.get("environment") == "staging"
        and value.get("server") == "manuel@217.160.255.86"
        and value.get("manifest_sha256") == manifest_sha256
        and value.get("operator_id") == str(operator_id),
        "WINDOW_SCOPE_REJECTED",
    )
    started = datetime.fromisoformat(value["verified_at"])
    require(
        started.tzinfo is not None and 0 <= (now - started).total_seconds() <= 14400,
        "WINDOW_PROOF_EXPIRED",
    )
    checks = value.get("checks", {})
    require(
        set(checks)
        == {
            "target",
            "host_key",
            "pushed_clean_runner",
            "backup",
            "restore",
            "restore_cleanup",
            "service_health",
            "postgres_localhost",
        }
        and all(v == "PASS" for v in checks.values()),
        "WINDOW_CHECKS_INCOMPLETE",
    )
    backup, restore = value["backup"], value["restore"]
    require(
        backup.get("database") == DATABASE
        and backup.get("recipient") == "2E44306121629A100F76A8B08CCA3D9186A28D4C"
        and bool(
            re.fullmatch(
                r"/var/backups/competence-hub/[a-zA-Z0-9/_-]+",
                backup.get("remote_directory", ""),
            )
        )
        and all(
            HEX.fullmatch(backup.get(k, ""))
            for k in (
                "dump_gpg_sha256",
                "globals_gpg_sha256",
                "metadata_sha256",
                "baseline_sha256",
            )
        )
        and backup.get("private_key_on_vps") is False
        and restore.get("encrypted_dump_sha256") == backup["dump_gpg_sha256"]
        and restore.get("baseline_sha256") == backup["baseline_sha256"]
        and restore.get("isolated") is True
        and restore.get("temporary_database_removed") is True
        and restore.get("plaintext_residue") == 0
        and restore.get("container_residue") == 0,
        "EXACT_ENCRYPTED_RESTORE_PROOF_REQUIRED",
    )
    return value


@dataclass(frozen=True)
class ImportOperator:
    # Trusted CLI operator, not a fabricated browser SessionPrincipal/MFA claim.
    user_id: UUID
    roles: tuple[str, ...] = ("admin",)


async def row_versions(connection):
    """Count/MVCC-only: never read auth secrets or dump business row payloads."""
    tables = await rows(
        connection,
        "SELECT tablename FROM pg_tables WHERE schemaname='competence_hub' AND tablename<>'schema_migrations' ORDER BY tablename",
    )
    state = {}
    for item in tables:
        name = item["tablename"]
        require(bool(re.fullmatch(r"[a-z][a-z0-9_]*", name)), "UNSAFE_TABLE_METADATA")
        found = await rows(
            connection,
            f'''SELECT count(*) AS count,
                md5(coalesce(string_agg(ctid::text || ':' || xmin::text, ',' ORDER BY ctid),'')) AS versions
                FROM competence_hub."{name}"''',
        )
        state[name] = dict(found[0])
    return state


def unchanged_outside_registry(before, after):
    return {k: v for k, v in before.items() if k not in REGISTRY_TABLES} == {
        k: v for k, v in after.items() if k not in REGISTRY_TABLES
    }


def plan_binding(plan, prepared, manifest_sha256):
    return digest(
        {
            "manifest_sha256": manifest_sha256,
            "plan": plan.report(),
            "records": [
                {
                    "source": r.source.source_identity.model_dump(),
                    "source_hash": r.source_hash,
                    "profile_hash": r.profile_hash,
                    "contract_hash": r.contract_hash,
                    "publication_hash": r.publication_hash,
                }
                for r in prepared.records
            ],
        }
    )


class RealCoachImporter(PostgresCoachImporter):
    """Reuse existing planner/domain writer, never relax apply_synthetic guards."""

    def __init__(self, engine, owner_engine, manifest, assets, manifest_sha256):
        target_url(
            engine.url.render_as_string(hide_password=False), "competence_hub_app"
        )
        target_url(
            owner_engine.url.render_as_string(hide_password=False),
            "competence_hub_migrator",
        )
        from coach3b_real_manifest import verify_manifest

        verify_manifest(manifest)
        require(bool(HEX.fullmatch(manifest_sha256)), "MANIFEST_HASH_REQUIRED")
        super().__init__(engine, target_v2=True)
        self.owner_engine = owner_engine
        self.manifest = manifest
        self.assets = assets
        self.manifest_sha256 = manifest_sha256

    async def target_preflight(self, *, require_schema9=True):
        async with self.owner_engine.begin() as c:
            await c.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            found = await rows(
                c,
                "SELECT current_database() AS db,current_user AS role,inet_server_port() AS port,current_setting('server_version_num')::integer AS version",
            )
            identity = found[0]
            require(
                identity["db"] == DATABASE
                and identity["role"] == "competence_hub_migrator"
                and identity["port"] == 5432
                and 160000 <= identity["version"] < 170000,
                "TARGET_IDENTITY_REJECTED",
            )
            versions = tuple(
                r["version"]
                for r in await rows(
                    c,
                    "SELECT version FROM competence_hub.schema_migrations ORDER BY version",
                )
            )
            require(
                versions
                in (MIGRATIONS[:6], MIGRATIONS[:7], MIGRATIONS[:8], MIGRATIONS),
                "SCHEMA_HISTORY_REJECTED",
            )
            if require_schema9:
                require(versions == MIGRATIONS, "MIGRATIONS_REQUIRED")
            owners = await rows(
                c,
                "SELECT tableowner,count(*) AS count FROM pg_tables WHERE schemaname='competence_hub' GROUP BY tableowner",
            )
            require(
                len(owners) == 1 and owners[0]["tableowner"] == "competence_hub_owner",
                "SCHEMA_OWNER_REJECTED",
            )
            admins = await c.scalar(
                text("""SELECT count(DISTINCT u.id) FROM competence_hub.portal_users u
                JOIN competence_hub.user_roles ur ON ur.user_id=u.id
                JOIN competence_hub.roles r ON r.id=ur.role_id
                WHERE u.active AND r.active AND r.code='admin'""")
            )
            topic_count = await c.scalar(
                text("SELECT count(*) FROM competence_hub.topics WHERE active")
            )
            blockers = []
            if not admins:
                blockers.append("EXISTING_ACTIVE_ADMIN_REQUIRED_NO_ONBOARDING")
            if topic_count < 8:
                blockers.append("EXISTING_TAXONOMY_PREFLIGHT_REQUIRED")
            if versions != MIGRATIONS:
                blockers.append("APPROVED_MIGRATIONS_NOT_APPLIED")
            return {
                "target_database": DATABASE,
                "host": "127.0.0.1:5432 via dedicated known-VPS tunnel55432",
                "environment": "staging",
                "migrations": versions,
                "missing_migrations": MIGRATIONS[len(versions) :],
                "active_admin_candidates": admins,
                "active_topics": topic_count,
                "execution_blockers": blockers,
                "row_versions": await row_versions(c),
                "writes": 0,
            }

    async def _operator(self, c, operator_id):
        require(operator_id is not None, "EXISTING_APPROVED_OPERATOR_REQUIRED")
        found = await rows(
            c,
            """SELECT u.id FROM competence_hub.portal_users u
            JOIN competence_hub.user_roles ur ON ur.user_id=u.id
            JOIN competence_hub.roles r ON r.id=ur.role_id
            WHERE u.id=:id AND u.active AND r.active AND r.code='admin'
            FOR SHARE OF u,ur""",
            id=operator_id,
        )
        require(len(found) == 1, "EXISTING_ACTIVE_ADMIN_REQUIRED_NO_ONBOARDING")
        return ImportOperator(operator_id)

    async def _plan(self, c, *, lock=False):
        from coach3b_real_manifest import RuntimeTopicSnapshot, bind_manifest

        if lock:
            # Taxonomy is MATCH_ONLY; no guessed UUIDs or silent topic bootstrap.
            await rows(c, "SELECT id FROM competence_hub.topics ORDER BY id FOR SHARE")
            await rows(
                c,
                "SELECT topic_id FROM competence_hub.topic_category_assignments ORDER BY topic_id FOR SHARE",
            )
        topics = await rows(
            c,
            """SELECT t.id,t.name,t.active,array_remove(array_agg(a.category_code ORDER BY a.category_code),NULL) AS categories
            FROM competence_hub.topics t LEFT JOIN competence_hub.topic_category_assignments a ON a.topic_id=t.id
            WHERE t.active GROUP BY t.id,t.name ORDER BY t.id""",
        )
        catalogue = [
            RuntimeTopicSnapshot(
                t["id"], t["name"], tuple(t["categories"]), t["active"]
            )
            for t in topics
        ]
        now = await c.scalar(text("SELECT clock_timestamp()"))
        records, contract = bind_manifest(
            self.manifest, catalogue, self.assets, now=now
        )
        prepared = await self._validate(c, records, contract, self.assets, now)
        plan = plan_records(
            prepared, await self._snapshot(c, prepared.records, lock=lock)
        )
        require(
            not plan.issues and len(plan.steps) == 9, "REVIEW_OR_DATABASE_PLAN_CONFLICT"
        )
        require(
            {s.operation for s in plan.steps} in ({"CREATE"}, {"UNCHANGED"}),
            "INITIAL_OR_IDENTICAL_BATCH_ONLY",
        )
        count = await c.scalar(text("SELECT count(*) FROM competence_hub.coaches"))
        require(
            count == (0 if plan.steps[0].operation == "CREATE" else 9),
            "UNEXPECTED_EXISTING_COACHES",
        )
        return plan, prepared, now

    async def dry_run_real(self):
        await self.target_preflight()
        async with self.engine.begin() as c:
            await c.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            plan, prepared, _ = await self._plan(c)
            return {
                **plan.report(),
                "plan_sha256": plan_binding(plan, prepared, self.manifest_sha256),
                "business_mutations": 0,
            }

    async def apply_real(self, **arguments):
        # No public enabling switch until actual backup/restore/source/target
        # verification is implemented in the complete maintenance orchestrator.
        raise GateError("REAL_APPLY_DISABLED_WINDOW_ORCHESTRATOR_REQUIRED")

    async def _apply_transaction_candidate(
        self, *, operator_id, plan_sha256, window_proof, window_proof_sha256
    ):
        require(
            bool(HEX.fullmatch(plan_sha256 or "")) and operator_id is not None,
            "VERIFIED_PLAN_OPERATOR_REQUIRED",
        )
        read_window_proof(
            window_proof,
            window_proof_sha256,
            manifest_sha256=self.manifest_sha256,
            operator_id=operator_id,
            now=datetime.now(UTC),
        )
        await self.target_preflight()
        async with self.engine.begin() as c:
            await c.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
            await c.execute(text("SET LOCAL lock_timeout='5s'"))
            await c.execute(text("SET LOCAL statement_timeout='120s'"))
            await c.execute(text("SELECT pg_advisory_xact_lock(64731,3)"))
            await c.execute(
                text("LOCK TABLE competence_hub.coaches IN SHARE ROW EXCLUSIVE MODE")
            )
            operator = await self._operator(c, operator_id)
            before = await row_versions(c)
            plan, prepared, now = await self._plan(c, lock=True)
            require(
                plan_binding(plan, prepared, self.manifest_sha256) == plan_sha256,
                "STALE_DRY_RUN",
            )
            for step in plan.steps:
                await self._apply_record(c, step, operator, now)
            after = await row_versions(c)
            require(unchanged_outside_registry(before, after), "NON_REGISTRY_MUTATION")
            if plan.steps[0].operation == "UNCHANGED":
                require(before == after, "IDENTICAL_RUN_MUTATED_ROWS")
            report = await self.verify_registry(c)
            return {
                **plan.report(),
                **report,
                "business_mutations": plan.report()["business_mutations_planned"],
            }

    async def verify_registry(self, c):
        repo = PostgresCoachRegistryRepository(self.engine, connection=c)
        bound = await rows(
            c,
            "SELECT coach_id FROM competence_hub.coach_import_sources ORDER BY source_system,source_key",
        )
        require(len(bound) == 9, "IDENTITY_COUNT_CONFLICT")
        coaches = tuple([await repo.get(r["coach_id"]) for r in bound])
        require(
            all(v and len(v.revisions) == 1 for v in coaches), "REVISION_COUNT_CONFLICT"
        )
        preview, production = [
            public_projection(coaches, e) for e in ("preview", "production")
        ]
        from coach3b_real_manifest import verify_projection_parity

        verify_projection_parity(self.manifest, preview, production)
        unmapped = await c.scalar(
            text(
                "SELECT count(*) FROM competence_hub.coaches WHERE portal_user_id IS NOT NULL OR public_profile_path IS NOT NULL"
            )
        )
        require(unmapped == 0, "UNAUTHORIZED_CALENDAR_OR_ACCOUNT_MAPPING")
        counts = {
            "coaches": len(coaches),
            "profile_revisions": sum(len(v.revisions) for v in coaches),
            "topic_links": sum(len(v.revisions[0].content.topic_ids) for v in coaches),
            "competencies": sum(
                len(v.revisions[0].content.competencies) for v in coaches
            ),
            "public_qualifications": sum(
                len(v.revisions[0].content.qualifications) for v in coaches
            ),
            "offering_families": sum(
                len(v.revisions[0].content.offering_families) for v in coaches
            ),
            "offering_formats": sum(
                len(v.revisions[0].content.offerings) for v in coaches
            ),
            "variants_add_ons": sum(
                sum(len(f.variants) for f in v.revisions[0].content.offering_families)
                + sum(len(o.variants) for o in v.revisions[0].content.offerings)
                for v in coaches
            ),
            "assets": sum(len(v.revisions[0].content.assets) for v in coaches),
            "object_evidence_records": sum(
                len(v.revisions[0].object_evidence) for v in coaches
            ),
            "current_attestation_records": sum(
                len(v.revisions[0].approvals) for v in coaches
            ),
        }
        expected = self.manifest["counts"]
        require(
            all(expected[k] == v for k, v in counts.items()),
            "POST_APPLY_COUNTS_CONFLICT",
        )
        return {
            "verified_counts": counts,
            "preview_projection_sha256": digest(preview),
            "production_projection_sha256": digest(production),
            "parity": "PASS",
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("validate", "preflight", "dry-run", "apply"),
        default="validate",
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--operator-id", type=UUID)
    parser.add_argument("--plan-sha256")
    parser.add_argument("--window-proof")
    parser.add_argument("--window-proof-sha256")
    args = parser.parse_args(argv)
    if args.mode == "apply":
        print(
            json.dumps(
                {
                    "result": "STOP",
                    "gate": "REAL_APPLY_DISABLED_WINDOW_ORCHESTRATOR_REQUIRED",
                    "acceptance": "NOT_COMPLETE",
                }
            )
        )
        return 1
    engines = []

    async def run():
        from coach3b_real_manifest import load_asset_bytes, verify_local_inputs

        manifest = read_manifest(args.manifest, args.manifest_sha256)
        verify_local_inputs(ROOT, manifest)
        assets = load_asset_bytes(ROOT, manifest)
        if args.mode == "validate":
            return {
                "result": "PASS",
                "mode": "OFFLINE_MANIFEST_VALIDATION",
                "counts": manifest["counts"],
                "database": "NOT_READ",
                "business_mutations": 0,
            }
        urls = [
            os.environ.get("COMPETENCE_HUB_REAL_IMPORT_" + role + "_URL", "")
            for role in ("APP", "OWNER")
        ]
        for url, role in zip(urls, ("competence_hub_app", "competence_hub_migrator")):
            target_url(url, role)
        engines.extend(create_async_engine(url, hide_parameters=True) for url in urls)
        importer = RealCoachImporter(*engines, manifest, assets, args.manifest_sha256)
        try:
            if args.mode == "preflight":
                result = await importer.target_preflight(require_schema9=False)
                return {
                    "result": "STOP" if result["execution_blockers"] else "PASS",
                    "target_metadata_read": "PASS",
                    "acceptance": "NOT_COMPLETE",
                    **result,
                }
            if args.mode == "dry-run":
                return await importer.dry_run_real()
            return await importer.apply_real(
                operator_id=args.operator_id,
                plan_sha256=args.plan_sha256,
                window_proof=args.window_proof,
                window_proof_sha256=args.window_proof_sha256,
            )
        finally:
            for engine in engines:
                await engine.dispose()

    try:
        result = asyncio.run(run())
    except GateError as error:
        result = {"result": "STOP", "gate": str(error), "acceptance": "NOT_COMPLETE"}
    except Exception:
        result = {
            "result": "STOP",
            "gate": "SANITIZED_OPERATOR_FAILURE",
            "acceptance": "NOT_COMPLETE",
        }
    print(json.dumps(result, sort_keys=True, default=str))
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
