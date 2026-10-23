"""Controlled import planner and synthetic-only atomic application over COACH-1."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

from competence_hub_api.portal.coach_import import (
    ImportIssue,
    PreparedRecord,
    ValidationResult,
    profile_fingerprint,
    record_ref,
    validate_records,
)
from competence_hub_api.portal.coach_registry import (
    CoachAggregate,
    CoachRegistryService,
    RegistryConflict,
)
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
    rows,
)


@dataclass
class ImportBinding:
    coach: CoachAggregate
    ledger: dict
    items: set


@dataclass
class ImportSnapshot:
    bindings: dict = field(default_factory=dict)
    paths: dict = field(default_factory=dict)


@dataclass
class ImportStep:
    record: PreparedRecord
    operation: str
    binding: ImportBinding | None


@dataclass
class ImportPlan:
    steps: list = field(default_factory=list)
    issues: list = field(default_factory=list)

    def report(self):
        counts = {
            name: sum(step.operation == name for step in self.steps)
            for name in ("CREATE", "REVISION", "EDIT_DRAFT", "UNCHANGED", "METADATA")
        }
        return {
            "result": "CONFLICT" if self.issues else "PASS",
            "counts": counts,
            "issues": [asdict(i) for i in self.issues],
            "records": [
                {
                    "record_ref": record_ref(s.record.source.source_identity),
                    "action": s.operation,
                    "revision_number": (
                        1
                        if not s.binding
                        else len(s.binding.coach.revisions)
                        + (s.operation == "REVISION")
                    ),
                    "matched_topics": len(s.record.content.topic_ids),
                    "offerings": len(s.record.content.offerings),
                    "taxonomy_action": "MATCH_ONLY",
                    "portrait": (
                        "MATCH" if s.record.content.assets else "SKIP_NO_PORTRAIT"
                    ),
                }
                for s in self.steps
            ],
            "business_mutations_planned": (
                0
                if self.issues
                else sum(
                    s.operation not in {"UNCHANGED", "METADATA"} for s in self.steps
                )
            ),
        }


def plan_records(validated: ValidationResult, snapshot: ImportSnapshot):
    plan = ImportPlan(issues=list(validated.issues))
    for record in validated.records:
        source = record.source
        key = source.source_identity.key
        ref = record_ref(source.source_identity)
        bound = snapshot.bindings.get(key)

        def issue(code, field):
            plan.issues.append(ImportIssue(code, ref, field))

        if source.expected_coach_id is not None and (
            not bound or source.expected_coach_id != bound.coach.id
        ):
            issue("IDENTITY_CONFLICT", "expected_coach_id")
        owners = snapshot.paths.get(record.content.profile_path, set())
        if owners - ({bound.coach.id} if bound else set()):
            issue("PROFILE_PATH_CONFLICT", "profile.profile_path")
        if bound is None:
            plan.steps.append(ImportStep(record, "CREATE", None))
            continue
        ledger, coach = bound.ledger, bound.coach
        if record.content.profile_path != ledger["profile_path"]:
            issue("PROFILE_PATH_CONFLICT", "profile.profile_path")
        if bound.items - set(record.items):
            issue("MISSING_ITEM_REVIEW_REQUIRED", "source_items")
        if record.publication_hash != ledger["publication_intent_hash"]:
            issue("PUBLICATION_EVIDENCE_REQUIRED", "initial_publication")
        for asset in record.content.assets:
            if any(
                old.reference == asset.reference and old.sha256 != asset.sha256
                for rev in coach.revisions
                for old in rev.content.assets
            ):
                issue("ASSET_MAPPING_REQUIRED", "immutable_asset_reference")
        revision = coach.revision(ledger["last_revision_id"])
        if (
            coach.version != ledger["last_registry_version"]
            or profile_fingerprint(revision.content, revision.topics)
            != ledger["profile_content_hash"]
        ):
            issue("STATE_CONFLICT", "registry_version_or_content")
        if record.profile_hash == ledger["profile_content_hash"]:
            operation = (
                "UNCHANGED"
                if (
                    record.source_hash == ledger["source_content_hash"]
                    and record.contract_hash == ledger["mapping_contract_hash"]
                )
                else "METADATA"
            )
        elif revision.status == "draft":
            operation = "EDIT_DRAFT"
        elif any(r.status == "draft" for r in coach.revisions):
            issue("STATE_CONFLICT", "foreign_draft")
            operation = "REVISION"
        else:
            operation = "REVISION"
        plan.steps.append(ImportStep(record, operation, bound))
    return plan


def local_import_url(raw):
    url = make_url(raw)
    if (
        url.drivername != "postgresql+asyncpg"
        or url.host != "127.0.0.1"
        or url.port != 55435
        or url.database != "competence_hub_staging"
        or url.username != "competence_hub_app"
        or not url.password
        or url.query
    ):
        raise ValueError("Synthetic import requires the owned loopback55435 container")


class PostgresCoachImporter:
    def __init__(self, engine):
        self.engine = engine

    async def _snapshot(self, connection, records, *, lock=False):
        repo = PostgresCoachRegistryRepository(self.engine, connection=connection)
        result = ImportSnapshot()
        for record in records:
            identity = record.source.source_identity
            found = await rows(
                connection,
                "SELECT * FROM competence_hub.coach_import_sources WHERE source_system=:system AND source_key=:key"
                + (" FOR UPDATE" if lock else ""),
                system=identity.source_system,
                key=identity.source_key,
            )
            if found:
                ledger = dict(found[0])
                if lock:
                    await rows(
                        connection,
                        "SELECT id FROM competence_hub.coaches WHERE id=:id FOR UPDATE",
                        id=ledger["coach_id"],
                    )
                coach = await repo.get(ledger["coach_id"])
                item_rows = await rows(
                    connection,
                    "SELECT kind,item_key FROM competence_hub.coach_import_items WHERE source_system=:system AND source_key=:key",
                    system=identity.source_system,
                    key=identity.source_key,
                )
                result.bindings[identity.key] = ImportBinding(
                    coach, ledger, {(r["kind"], r["item_key"]) for r in item_rows}
                )
        paths = [r.content.profile_path for r in records if r.content.profile_path]
        for row in await rows(
            connection,
            "SELECT DISTINCT profile_path,coach_id FROM competence_hub.coach_profile_revisions WHERE profile_path=ANY(CAST(:paths AS text[]))",
            paths=paths,
        ):
            result.paths.setdefault(row["profile_path"], set()).add(row["coach_id"])
        return result

    async def _validate(self, connection, values, contract, asset_bytes, now):
        repo = PostgresCoachRegistryRepository(self.engine, connection=connection)
        try:
            topics = await repo.topics(tuple({r.topic_id for r in contract.topics}))
        except RegistryConflict:
            return ValidationResult(
                issues=[ImportIssue("TOPIC_CONFLICT", "batch", "catalogue")]
            )
        return validate_records(
            values, contract, {t.id: t for t in topics}, asset_bytes, now=now
        )

    async def dry_run(self, values, contract, asset_bytes):
        async with self.engine.begin() as c:
            await c.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            now = await c.scalar(text("SELECT clock_timestamp()"))
            validated = await self._validate(c, values, contract, asset_bytes, now)
            return plan_records(
                validated, await self._snapshot(c, validated.records)
            ).report()

    async def apply_synthetic(self, values, contract, asset_bytes, *, actor):
        local_import_url(str(self.engine.url.render_as_string(hide_password=False)))
        # No file-backed APPLY in this slice. The operator wrapper supplies only
        # the bundled fixtures; this guard also rejects real-source namespaces.
        if any(
            v.get("source_identity", {}).get("source_system") != "synthetic-coach3a"
            for v in values
        ):
            return {
                "result": "CONFLICT",
                "issues": [{"code": "SYNTHETIC_SCOPE_REQUIRED"}],
                "business_mutations": 0,
            }
        CoachRegistryService.authorize(actor)
        try:
            async with self.engine.begin() as c:
                await c.execute(text("SELECT pg_advisory_xact_lock(64731,3)"))
                allowed = await c.scalar(
                    text("""SELECT EXISTS(SELECT 1 FROM competence_hub.portal_users u
                    JOIN competence_hub.user_roles ur ON ur.user_id=u.id JOIN competence_hub.roles r ON r.id=ur.role_id
                    WHERE u.id=:id AND u.active AND r.active AND r.code='admin')"""),
                    {"id": actor.user_id},
                )
                if not allowed:
                    return {
                        "result": "CONFLICT",
                        "issues": [{"code": "OPERATOR_DENIED"}],
                        "business_mutations": 0,
                    }
                await rows(
                    c,
                    "SELECT id FROM competence_hub.topics WHERE id=ANY(CAST(:ids AS uuid[])) ORDER BY id FOR UPDATE",
                    ids=sorted({r.topic_id for r in contract.topics}, key=str),
                )
                await rows(
                    c,
                    "SELECT topic_id FROM competence_hub.topic_category_assignments WHERE topic_id=ANY(CAST(:ids AS uuid[])) FOR SHARE",
                    ids=sorted({r.topic_id for r in contract.topics}, key=str),
                )
                now = await c.scalar(text("SELECT clock_timestamp()"))
                validated = await self._validate(c, values, contract, asset_bytes, now)
                plan = plan_records(
                    validated, await self._snapshot(c, validated.records, lock=True)
                )
                report = plan.report()
                if plan.issues:
                    report["business_mutations"] = 0
                    return report
                for step in plan.steps:
                    await self._apply_record(c, step, actor, now)
                report["business_mutations"] = report["business_mutations_planned"]
                return report
        except (SQLAlchemyError, RegistryConflict, LookupError):
            # Never return PostgreSQL DETAIL or source payloads in operator errors.
            return {
                "result": "CONFLICT",
                "issues": [{"code": "TRANSACTION_CONFLICT"}],
                "business_mutations": 0,
            }

    async def _apply_record(self, c, step, actor, now):
        if step.operation == "UNCHANGED":
            return
        r = step.record
        service = CoachRegistryService(
            PostgresCoachRegistryRepository(self.engine, connection=c)
        )
        coach = (
            step.binding.coach
            if step.binding
            else await service.create(
                actor=actor,
                display_name=r.content.display_name,
                request_id=uuid4(),
                now=now,
            )
        )

        async def mutate(operation, **values):
            nonlocal coach
            coach = await service.mutate(
                actor=actor,
                coach_id=coach.id,
                expected_version=coach.version,
                operation=operation,
                now=now,
                **values,
            )

        if step.operation in {"CREATE", "REVISION"}:
            await mutate("revision", content=r.content)
        elif step.operation == "EDIT_DRAFT":
            await mutate(
                "draft",
                revision_id=step.binding.ledger["last_revision_id"],
                content=r.content,
            )
        revision_id = coach.revisions[-1].id
        if step.operation == "CREATE" and r.source.publication.lifecycle == "active":
            await mutate("submit", revision_id=revision_id)
            for evidence in r.source.publication.evidence:
                await mutate(
                    "approve",
                    revision_id=revision_id,
                    kind=evidence.kind,
                    evidence_ref=evidence.source,
                )
            await mutate("lifecycle", lifecycle="active")
            for environment in sorted(r.source.publication.published):
                await mutate(
                    "publish", revision_id=revision_id, environment=environment
                )
        params = {
            "system": r.source.source_identity.source_system,
            "key": r.source.source_identity.source_key,
            "coach": coach.id,
            "path": r.content.profile_path,
            "source_hash": r.source_hash,
            "profile_hash": r.profile_hash,
            "mapping_hash": r.contract_hash,
            "publication_hash": r.publication_hash,
            "revision": revision_id,
            "version": coach.version,
            "source_ref": r.source.provenance.source_ref,
        }
        await c.execute(
            text(
                """INSERT INTO competence_hub.coach_import_sources
            (source_system,source_key,coach_id,profile_path,source_content_hash,profile_content_hash,mapping_contract_hash,publication_intent_hash,last_revision_id,last_registry_version,source_ref)
            VALUES (:system,:key,:coach,:path,:source_hash,:profile_hash,:mapping_hash,:publication_hash,:revision,:version,:source_ref)
            ON CONFLICT(source_system,source_key) DO UPDATE SET source_content_hash=EXCLUDED.source_content_hash,
            profile_content_hash=EXCLUDED.profile_content_hash,mapping_contract_hash=EXCLUDED.mapping_contract_hash,
            publication_intent_hash=EXCLUDED.publication_intent_hash,last_revision_id=EXCLUDED.last_revision_id,last_registry_version=EXCLUDED.last_registry_version,source_ref=EXCLUDED.source_ref"""
            ),
            params,
        )
        for (kind, key), value in sorted(r.items.items()):
            await c.execute(
                text(
                    """INSERT INTO competence_hub.coach_import_items(source_system,source_key,kind,item_key,value_hash)
                VALUES (:system,:key,:kind,:item,:value) ON CONFLICT(source_system,source_key,kind,item_key)
                DO UPDATE SET value_hash=EXCLUDED.value_hash WHERE coach_import_items.value_hash<>EXCLUDED.value_hash"""
                ),
                {**params, "kind": kind, "item": key, "value": value},
            )
        if step.operation == "CREATE":
            for evidence in r.source.publication.evidence:
                await c.execute(
                    text(
                        """INSERT INTO competence_hub.coach_import_evidence
                    (source_system,source_key,evidence_key,coach_id,revision_id,kind,environment,evidence_source,historical_at)
                    VALUES (:system,:key,:evidence_key,:coach,:revision,:kind,:environment,:source,:historical_at)"""
                    ),
                    {
                        **params,
                        "evidence_key": evidence.key,
                        "kind": evidence.kind,
                        "environment": evidence.environment,
                        "source": evidence.source,
                        "historical_at": evidence.historical_at,
                    },
                )


def technical_run(mode, result, *, started):
    return {
        "run_id": str(uuid4()),
        "mode": mode,
        "started": started.isoformat(),
        "finished": datetime.now(UTC).isoformat(),
        **result,
    }
