"""Bounded read-only Registry snapshot -> private review or existing public DTO.

No engine creation, environment/configuration lookup, HTTP, audit or import path.
The optional borrowed SQL connection is for a separately gated future caller.
"""

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import re
from types import MappingProxyType
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator
from sqlalchemy import text

from .coach_projection import (
    MAX_ARTIFACT_BYTES,
    canonical_bytes,
    checked_local_path,
    generate_projection,
    verify_asset_references,
)
from .coach_registry import CATEGORIES, CoachAggregate, ProfileContent, RegistryConflict
from .coach_target import subjects
from .postgres_coach_registry import PostgresCoachRegistryRepository

MAX_COACHES = 500
MAX_REVISIONS = 5000
MAX_CHILDREN = 100000
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024
AGGREGATES = TypeAdapter(tuple[CoachAggregate, ...])
COACH_COLUMNS = (
    "id,display_name,registry_request_id,lifecycle_status,registry_lock_version,"
    "publication_floor"
)
TABLE_LIMITS = MappingProxyType(
    {
        "coaches": MAX_COACHES,
        "coach_profile_revisions": MAX_REVISIONS,
        "coach_publications": MAX_COACHES * 2,
        **{
            name: MAX_CHILDREN
            for name in (
                "coach_profile_labels",
                "coach_profile_topics",
                "coach_profile_topic_categories",
                "coach_offerings",
                "coach_assets",
                "coach_profile_approvals",
                "coach_public_roles",
                "coach_qualifications",
                "coach_offering_families",
                "coach_object_evidence",
            )
        },
    }
)
READ_SQL = MappingProxyType(
    {
        name: f"SELECT {COACH_COLUMNS if name == 'coaches' else '*'} "
        f"FROM competence_hub.{name} LIMIT :limit"
        for name in TABLE_LIMITS
    }
)
TRANSACTION_SQL = "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
CHECK_SQL = (
    "SELECT current_setting('transaction_read_only') AS read_only, "
    "current_setting('transaction_isolation') AS isolation"
)


class ReadOnlyRows:
    """Only fixed bounded SELECTs; never expose raw execute or repository writers."""

    def __init__(self, connection):
        self.__connection = connection

    async def fetch(self, table):
        if table not in READ_SQL:
            raise PermissionError("export table not allowed")
        limit = TABLE_LIMITS[table]
        result = (
            (
                await self.__connection.execute(
                    text(READ_SQL[table]), {"limit": limit + 1}
                )
            )
            .mappings()
            .all()
        )
        if len(result) > limit:
            raise RegistryConflict("snapshot bound exceeded; no partial export")
        return result

    def execute(self, *args, **kwargs):
        raise PermissionError("export capability forbids SQL execution/writes")

    create = edit = mutate = execute


def _unique(values, message):
    if len(values) != len(set(values)):
        raise RegistryConflict(message)


def _validate(coaches):
    if (
        len(coaches) > MAX_COACHES
        or sum(len(c.revisions) for c in coaches) > MAX_REVISIONS
    ):
        raise RegistryConflict("snapshot bound exceeded")
    _unique([c.id for c in coaches], "duplicate Coach identity")
    revision_ids, evidence_ids, paths = [], [], {}
    for coach in coaches:
        if coach.version < 1 or coach.publication_floor < 0:
            raise RegistryConflict("invalid Coach version/floor")
        _unique([r.number for r in coach.revisions], "duplicate revision number")
        if sum(r.status == "draft" for r in coach.revisions) > 1:
            raise RegistryConflict("multiple current drafts")
        for revision in coach.revisions:
            if revision.number < 1:
                raise RegistryConflict("invalid revision number")
            revision_ids.append(revision.id)
            content = ProfileContent.model_validate(revision.content.model_dump())
            if content.profile_path:
                owner = paths.setdefault(content.profile_path, coach.id)
                if owner != coach.id:
                    raise RegistryConflict("profile path belongs to multiple Coaches")
            _unique([t.id for t in revision.topics], "duplicate topic snapshot")
            if set(content.topic_ids) != {t.id for t in revision.topics}:
                raise RegistryConflict("incomplete topic snapshot")
            for topic in revision.topics:
                if not topic.name.strip() or not set(topic.categories) <= CATEGORIES:
                    raise RegistryConflict("invalid topic snapshot")
                _unique(list(topic.categories), "duplicate topic category")
            _unique(
                [e.id for e in revision.object_evidence], "duplicate evidence identity"
            )
            _unique(
                [e.value.key for e in revision.object_evidence],
                "duplicate evidence key",
            )
            _unique([a.kind for a in revision.approvals], "duplicate revision approval")
            subject_keys = subjects(content, revision.topics)
            for evidence in revision.object_evidence:
                evidence_ids.append(evidence.id)
                if (
                    evidence.value.subject_type,
                    evidence.value.subject_key,
                ) not in subject_keys:
                    raise RegistryConflict("orphan object evidence")
        for environment, publication in coach.publications.items():
            if environment not in {"preview", "production"}:
                raise RegistryConflict("invalid publication environment")
            try:
                coach.revision(publication.revision_id)
            except LookupError:
                raise RegistryConflict(
                    "publication references foreign/missing revision"
                ) from None
    _unique(revision_ids, "revision belongs to multiple Coaches")
    _unique(evidence_ids, "evidence belongs to multiple revisions")


@dataclass(frozen=True)
class RegistrySnapshot:
    """Sealed existing aggregates, not a second domain model or disk dump.

    Private full content/evidence exists ONLY in this in-memory seal so original
    subject hashes remain valid. The emitted internal review is deliberately
    minimized and is not a re-importable authorization/evidence interchange.
    """

    _payload: bytes = field(repr=False)

    @classmethod
    def capture(cls, coaches):
        values = tuple(coaches)
        if (
            len(values) > MAX_COACHES
            or sum(len(c.revisions) for c in values) > MAX_REVISIONS
        ):
            raise RegistryConflict("snapshot bound exceeded")
        before = AGGREGATES.dump_json(values)
        if len(before) > MAX_SNAPSHOT_BYTES:
            raise RegistryConflict("snapshot byte bound exceeded")
        copied = deepcopy(values)
        if before != AGGREGATES.dump_json(values) or before != AGGREGATES.dump_json(
            copied
        ):
            raise RegistryConflict("concurrent local snapshot mutation")
        # JSON round trip revalidates even model_copy(update=...) and mutable DTOs.
        validated = AGGREGATES.validate_json(before)
        _validate(validated)
        return cls(AGGREGATES.dump_json(validated))

    def coaches(self):
        if len(self._payload) > MAX_SNAPSHOT_BYTES:
            raise RegistryConflict("snapshot byte bound exceeded")
        values = AGGREGATES.validate_json(self._payload)
        _validate(values)
        return values


def _validate_rows(tables):
    coaches = {r["id"] for r in tables["coaches"]}
    revisions = {r["id"]: r["coach_id"] for r in tables["coach_profile_revisions"]}
    _unique([r["id"] for r in tables["coaches"]], "duplicate Coach row")
    _unique(
        [r["id"] for r in tables["coach_profile_revisions"]], "duplicate revision row"
    )
    if any(owner not in coaches for owner in revisions.values()):
        raise RegistryConflict("foreign revision owner")
    for table, rows in tables.items():
        if table in {"coaches", "coach_profile_revisions"}:
            continue
        for row in rows:
            owner = revisions.get(row["revision_id"])
            if owner is None or ("coach_id" in row and row["coach_id"] != owner):
                raise RegistryConflict("foreign/missing child owner")
    topic_keys = {
        (r["revision_id"], r["topic_id"]) for r in tables["coach_profile_topics"]
    }
    if any(
        (r["revision_id"], r["topic_id"]) not in topic_keys
        for r in tables["coach_profile_topic_categories"]
    ):
        raise RegistryConflict("orphan topic category")
    _unique(
        [(r["coach_id"], r["environment"]) for r in tables["coach_publications"]],
        "duplicate publication",
    )


async def read_postgres_snapshot(connection):
    """Borrow an idle connection. No URL/engine/secret/server discovery here.

    Transaction setup precedes EVERY data read. PostgreSQL rejects writes even
    if a future dependency bypasses the narrower SELECT capability. Always
    rollback; never join an existing writable transaction or page mutable reads.
    This entry point is NOT wired to runtime/CLI. Even a borrowed connection must
    target the fixed disposable synthetic DB, never the known VPS tunnel.
    """
    url = getattr(getattr(connection, "engine", None), "url", None)
    if tuple(
        getattr(url, key, None)
        for key in ("drivername", "host", "port", "database", "username")
    ) != (
        "postgresql+asyncpg",
        "127.0.0.1",
        55437,
        "competence_hub_export_synthetic",
        "competence_hub_app",
    ):
        raise PermissionError("only the fixed isolated synthetic SQL target is allowed")
    if connection.in_transaction():
        raise PermissionError("export requires an idle dedicated connection")
    transaction = await connection.begin()
    try:
        await connection.execute(text(TRANSACTION_SQL))
        settings = (await connection.execute(text(CHECK_SQL))).mappings().one()
        if dict(settings) != {"read_only": "on", "isolation": "repeatable read"}:
            raise PermissionError("read-only repeatable snapshot not confirmed")
        reader = ReadOnlyRows(connection)
        tables = {name: await reader.fetch(name) for name in TABLE_LIMITS}
        _validate_rows(tables)
        # One pass over rows; no repeated full-table scans per Coach.
        grouped = {
            row["id"]: {name: [] for name in TABLE_LIMITS} for row in tables["coaches"]
        }
        owners = {
            row["id"]: row["coach_id"] for row in tables["coach_profile_revisions"]
        }
        for table, records in tables.items():
            for row in records:
                owner = (
                    row["id"]
                    if table == "coaches"
                    else (
                        row["coach_id"]
                        if table in {"coach_profile_revisions", "coach_publications"}
                        else owners[row["revision_id"]]
                    )
                )
                grouped[owner][table].append(row)
        result = []
        for coach_row in tables["coaches"]:
            group = grouped[coach_row["id"]]
            revisions = sorted(
                group["coach_profile_revisions"],
                key=lambda r: r["revision_number"],
            )
            publications = group["coach_publications"]
            for publication in publications:
                revision = next(
                    r for r in revisions if r["id"] == publication["revision_id"]
                )
                if publication["profile_path"] != revision["profile_path"]:
                    raise RegistryConflict("publication route mismatch")
            result.append(
                PostgresCoachRegistryRepository.hydrate(
                    PostgresCoachRegistryRepository._coach(coach_row),
                    revisions,
                    group,
                    group,
                    publications,
                )
            )
        return RegistrySnapshot.capture(result)
    finally:
        await transaction.rollback()


def _internal_content(content):
    # Explicit field selection: no private note, source/evidence reference or
    # verification state. Protected original text and prices are not model fields.
    boundary = {"__all__": {"key", "text", "excluded_services"}}
    duration = {
        "clock_start",
        "clock_end",
        "minutes",
        "weeks",
        "sessions_per_week",
        "session_minutes",
        "label",
    }
    variants = {
        "__all__": {
            **{
                k: True
                for k in ("key", "kind", "title", "description", "ordering", "active")
            },
            "duration": duration,
        }
    }
    common = {
        **{
            k: True
            for k in (
                "key",
                "title",
                "description",
                "ordering",
                "active",
                "target_groups",
                "target_focus",
                "service_domains",
            )
        },
        "boundaries": boundary,
        "variants": variants,
    }
    value = content.model_dump(
        mode="json",
        include={
            **{
                k: True
                for k in (
                    "display_name",
                    "academic_suffix",
                    "short_intro",
                    "description",
                    "professional_background",
                    "target_groups",
                    "profile_path",
                    "topic_ids",
                    "competencies",
                    "target_version",
                )
            },
            "boundaries": boundary,
            "public_roles": {"__all__": {"key", "code", "display_label", "ordering"}},
            "qualifications": {
                "__all__": {
                    "key",
                    "canonical_title",
                    "public_display_label",
                    "issuer",
                    "qualification_type",
                    "ordering",
                    "public",
                    "status",
                }
            },
            "offering_families": {"__all__": common},
            "offerings": {
                "__all__": {
                    **common,
                    **{
                        k: True
                        for k in (
                            "type",
                            "family_key",
                            "bookable",
                            "delivery_mode",
                            "delivery_label",
                            "program_modules",
                        )
                    },
                    "duration": duration,
                }
            },
            "assets": {
                "__all__": {
                    "type",
                    "reference",
                    "sha256",
                    "alt_text",
                    "scopes",
                    "active",
                }
            },
            "presentation": {
                **{
                    k: True
                    for k in (
                        "teaser",
                        "focus_labels",
                        "background_labels",
                        "languages",
                        "quote",
                        "initials",
                        "portrait_width",
                        "portrait_height",
                    )
                },
                "topic_cards": {"__all__": {"title", "text"}},
                "sections": {"__all__": {"key", "kind", "headings", "paragraphs"}},
                "external_links": {
                    "__all__": {"key", "label", "preview_url", "production_url"}
                },
            },
        },
    )
    return _ordered(value)


def _ordered(value, key=""):
    if isinstance(value, dict):
        return {k: _ordered(v, k) for k, v in value.items()}
    if isinstance(value, list):
        items = [_ordered(v) for v in value]
        if key in {"topic_ids", "categories", "scopes", "competencies"}:
            return sorted(items)
        if key in {
            "public_roles",
            "qualifications",
            "offering_families",
            "offerings",
            "variants",
        }:
            return sorted(items, key=lambda v: (v["ordering"], v.get("key", "")))
        if key == "assets":
            return sorted(items, key=lambda v: (v["type"], v["reference"]))
        return items
    return value


def export_registry(snapshot, mode, *, asset_root):
    """No writes, including to assets. Return deterministic bytes-ready DTO."""
    if mode not in {"internal", "preview", "production"}:
        raise ValueError("explicit export mode required")
    coaches = snapshot.coaches()
    # Check ALL modeled asset references, including nonpublic/inactive ones in
    # internal review; no portrait is valid. No copying/transcoding/creation.
    verify_asset_references(
        [
            asset.model_dump(
                mode="json", include={"type", "reference", "sha256", "alt_text"}
            )
            for coach in coaches
            for revision in coach.revisions
            for asset in revision.content.assets
        ],
        asset_root,
    )
    if mode != "internal":
        return generate_projection(coaches, mode)
    records = []
    for coach in sorted(coaches, key=lambda c: str(c.id)):
        current = max(coach.revisions, key=lambda r: r.number, default=None)
        selected = {p.revision_id for p in coach.publications.values()}
        if current:
            selected.add(current.id)
        records.append(
            {
                "coach_id": str(coach.id),
                "display_name": coach.display_name,
                "lifecycle": coach.lifecycle,
                "version": coach.version,
                "publication_floor": coach.publication_floor,
                "current_profile_revision": str(current.id) if current else None,
                "revisions": [
                    {
                        "revision_id": str(r.id),
                        "revision_number": r.number,
                        "status": r.status,
                        "content": _internal_content(r.content),
                        "topics": sorted(
                            [
                                {
                                    "topic_id": str(t.id),
                                    "name": t.name,
                                    "categories": sorted(t.categories),
                                }
                                for t in r.topics
                            ],
                            key=lambda t: t["topic_id"],
                        ),
                        "approval_kinds": sorted(a.kind for a in r.approvals),
                    }
                    for r in sorted(coach.revisions, key=lambda r: r.number)
                    if r.id in selected
                ],
                "publications": {
                    env: {"revision_id": str(p.revision_id), "state": p.state}
                    for env, p in sorted(coach.publications.items())
                },
            }
        )
    return {
        "export_schema_version": 1,
        "artifact_kind": "coach_registry_internal_review",
        "coaches": records,
    }


class InternalValue(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InternalTopic(InternalValue):
    topic_id: UUID
    name: str
    categories: list[str]


class InternalRevision(InternalValue):
    revision_id: UUID
    revision_number: int = Field(gt=0)
    status: Literal["draft", "submitted", "abandoned"]
    content: dict
    topics: list[InternalTopic]
    approval_kinds: list[
        Literal["content_review", "person_consent", "preview", "production"]
    ]

    @field_validator("content")
    @classmethod
    def minimized(cls, value):
        if _internal_content(ProfileContent.model_validate(value)) != value:
            raise ValueError("internal content outside minimized allowlist")
        return value


class InternalPublication(InternalValue):
    revision_id: UUID
    state: Literal["published", "withdrawn"]


class InternalCoach(InternalValue):
    coach_id: UUID
    display_name: str
    lifecycle: Literal["draft", "active", "paused", "inactive", "archived"]
    version: int = Field(gt=0)
    publication_floor: int = Field(ge=0)
    current_profile_revision: UUID | None
    revisions: list[InternalRevision]
    publications: dict[Literal["preview", "production"], InternalPublication]


class InternalExport(InternalValue):
    export_schema_version: Literal[1]
    artifact_kind: Literal["coach_registry_internal_review"]
    coaches: list[InternalCoach] = Field(max_length=MAX_COACHES)


def export_counts(value):
    counts = {
        name: 0
        for name in (
            "coaches",
            "revisions",
            "roles",
            "topics",
            "qualifications",
            "families",
            "formats",
            "variants",
            "assets",
        )
    }
    for coach in value["coaches"]:
        counts["coaches"] += 1
        contents = (
            [r["content"] for r in coach["revisions"]]
            if "revisions" in coach
            else [coach]
        )
        counts["revisions"] += len(coach.get("revisions", []))
        counts["topics"] += (
            sum(len(r["topics"]) for r in coach["revisions"])
            if "revisions" in coach
            else len(coach["topics"])
        )
        for content in contents:
            counts["roles"] += len(
                content.get("public_roles", content.get("roles", []))
            )
            counts["qualifications"] += len(content.get("qualifications", []))
            counts["assets"] += len(content["assets"])
            families = content.get("offering_families", [])
            counts["families"] += len(families)
            formats = content["offerings"] + [
                o for f in families for o in f.get("formats", [])
            ]
            counts["formats"] += len(formats)
            counts["variants"] += sum(
                len(o.get("variants", [])) for o in [*formats, *families]
            )
    return counts


def write_export(value, *, mode, source_identifier, output_root):
    """Exclusive local artifacts; separate private/public trees, fixed filenames."""
    if mode not in {"internal", "preview", "production"} or not re.fullmatch(
        r"synthetic-[a-z0-9-]{1,64}", source_identifier
    ):
        raise ValueError("synthetic export identity/mode required")
    internal = value.get("artifact_kind") == "coach_registry_internal_review"
    if (mode == "internal") != internal:
        raise ValueError("internal/public artifact mismatch")
    if internal:
        if type(value.get("export_schema_version")) is not int:
            raise ValueError("integer export schema required")
        InternalExport.model_validate(value)
    else:
        from .coach_projection import validate_projection

        validate_projection(value, mode)
    data = canonical_bytes(value)
    if len(data) > MAX_ARTIFACT_BYTES:
        raise ValueError("export artifact too large")
    allowed = Path(__file__).resolve().parents[5] / ".tmp/coach4"
    root = checked_local_path(output_root, root=allowed)
    folder = checked_local_path(
        root / ("private-internal" if internal else "public") / mode, root=allowed
    )
    artifact = folder / "coaches.json"
    manifest_file = folder / "manifest.json"
    if artifact.exists() or manifest_file.exists():
        raise FileExistsError("export destination already exists")
    manifest = {
        "manifest_schema_version": 1,
        "mode": mode,
        "artifact_schema_version": value.get(
            "export_schema_version", value.get("schema")
        ),
        "source_identifier": source_identifier,
        "artifact_filename": artifact.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "counts": export_counts(value),
    }
    folder.mkdir(parents=True, exist_ok=True)
    with artifact.open("xb") as stream:
        stream.write(data)
    with manifest_file.open("xb") as stream:
        stream.write(canonical_bytes(manifest))
    return manifest
