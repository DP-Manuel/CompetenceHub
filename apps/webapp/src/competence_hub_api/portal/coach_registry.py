"""Local COACH-1 domain; publication never grants account or Calendar rights."""

from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    field_validator,
    model_validator,
)

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.portal.coach_profiles import validate_public_profile_path
from competence_hub_api.portal.coach_target import (
    KEY,
    REF,
    Boundary,
    Domain,
    Duration,
    ObjectEvidenceInput,
    OfferingFamily,
    Presentation,
    PublicRole,
    Qualification,
    Variant,
    evidence_ready,
    public_offering,
    public_target,
    subjects,
    unique_items,
)

Lifecycle = Literal["draft", "active", "paused", "inactive", "archived"]
Environment = Literal["preview", "production"]
ApprovalKind = Literal["content_review", "person_consent", "preview", "production"]
CATEGORIES = frozenset(
    {"personalentwicklung", "persoenlichkeitsentwicklung", "karrierecoaching"}
)
LIFECYCLE_TRANSITIONS = {
    "draft": {"active", "inactive", "archived"},
    "active": {"paused", "inactive", "archived"},
    "paused": {"active", "inactive", "archived"},
    "inactive": {"active", "archived"},
    "archived": {"inactive"},
}


class RegistryConflict(ValueError):
    pass


class RegistryDenied(PermissionError):
    pass


class PublicModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class Offering(PublicModel):
    title: str = Field(min_length=1, max_length=250)
    type: Literal["lecture", "workshop", "coaching", "individual", "other"]
    description: str | None = Field(default=None, max_length=2000)
    active: bool = True
    ordering: int = Field(default=0, ge=0, le=1000)
    key: str | None = Field(default=None, pattern=KEY)
    family_key: str | None = Field(default=None, pattern=KEY)
    service_domains: tuple[Domain, ...] = Field(default=(), max_length=6)
    bookable: StrictBool = False
    duration: Duration | None = None
    delivery_mode: Literal[
        "unknown",
        "online",
        "in_person",
        "online_or_in_person",
        "hybrid",
        "live_unspecified",
    ] = "unknown"
    delivery_label: str | None = Field(default=None, max_length=250)
    target_groups: tuple[str, ...] = Field(default=(), max_length=20)
    target_focus: tuple[str, ...] = Field(default=(), max_length=20)
    program_modules: tuple[str, ...] = Field(default=(), max_length=30)
    boundaries: tuple[Boundary, ...] = Field(default=(), max_length=10)
    variants: tuple[Variant, ...] = Field(default=(), max_length=20)
    protected_source_reference: str | None = Field(default=None, pattern=REF)

    @model_validator(mode="after")
    def coherent_target(self):
        unique_items(self.variants, "offering variants")
        if len(set(self.service_domains)) != len(self.service_domains):
            raise ValueError("duplicate service domain")
        if len({b.key for b in self.boundaries}) != len(self.boundaries):
            raise ValueError("duplicate boundary")
        if any(
            not s.strip() or len(s) > 500
            for s in (*self.target_groups, *self.target_focus, *self.program_modules)
        ):
            raise ValueError("invalid offering label")
        if "psychotherapy" in self.service_domains and (
            self.bookable
            or self.type == "coaching"
            or "coaching" in self.service_domains
        ):
            raise ValueError("psychotherapy remains separate and nonbookable")
        return self


class Asset(PublicModel):
    type: Literal["portrait"] = "portrait"
    reference: str = Field(
        pattern=r"^images/coaches/[a-z0-9]+(?:[-.][a-z0-9]+)*\.(?:webp|jpg|jpeg|png)$",
        max_length=200,
    )
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    alt_text: str = Field(min_length=1, max_length=250)
    scopes: tuple[Environment, ...] = ("preview",)
    active: bool = True

    @field_validator("scopes")
    @classmethod
    def scopes_unique(cls, value):
        if not value or len(value) != len(set(value)):
            raise ValueError("asset scopes must be nonempty and unique")
        return value


class ProfileContent(PublicModel):
    display_name: str = Field(min_length=1, max_length=200)
    academic_suffix: str | None = Field(default=None, max_length=100)
    short_intro: str = Field(min_length=1, max_length=1000)
    description: str | None = Field(default=None, max_length=10000)
    professional_background: str | None = Field(default=None, max_length=4000)
    target_groups: tuple[str, ...] = Field(default=(), max_length=30)
    profile_path: str | None = None
    topic_ids: tuple[UUID, ...] = Field(default=(), max_length=50)
    competencies: tuple[str, ...] = Field(default=(), max_length=50)
    offerings: tuple[Offering, ...] = Field(default=(), max_length=100)
    assets: tuple[Asset, ...] = Field(default=(), max_length=1)
    target_version: Literal[0, 1] = 0
    public_roles: tuple[PublicRole, ...] = Field(default=(), max_length=20)
    qualifications: tuple[Qualification, ...] = Field(default=(), max_length=50)
    offering_families: tuple[OfferingFamily, ...] = Field(default=(), max_length=30)
    presentation: Presentation | None = None
    boundaries: tuple[Boundary, ...] = Field(default=(), max_length=10)

    @field_validator("profile_path")
    @classmethod
    def valid_path(cls, value):
        return validate_public_profile_path(value)

    @field_validator("target_groups", "competencies")
    @classmethod
    def valid_labels(cls, values):
        if any(not value.strip() or len(value) > 250 for value in values):
            raise ValueError("invalid public label")
        if len({value.casefold().strip() for value in values}) != len(values):
            raise ValueError("duplicate public label")
        return tuple(value.strip() for value in values)

    @model_validator(mode="after")
    def unique_topics(self):
        if len(set(self.topic_ids)) != len(self.topic_ids):
            raise ValueError("duplicate topic")
        if len({o.ordering for o in self.offerings}) != len(self.offerings):
            raise ValueError("offering order must be unique")
        for name in ("public_roles", "qualifications", "offering_families"):
            unique_items(getattr(self, name), name)
        if len({b.key for b in self.boundaries}) != len(self.boundaries):
            raise ValueError("duplicate boundary")
        rich = any(
            (
                self.public_roles,
                self.qualifications,
                self.offering_families,
                self.presentation,
                self.boundaries,
            )
        )
        rich = rich or any(
            o.model_dump(exclude={"title", "type", "description", "active", "ordering"})
            != Offering(title=o.title, type=o.type).model_dump(
                exclude={"title", "type", "description", "active", "ordering"}
            )
            for o in self.offerings
        )
        if rich and not self.target_version:
            raise ValueError("rich fields require target_version 1")
        if self.target_version:
            if any(not o.key for o in self.offerings) or len(
                {o.key for o in self.offerings}
            ) != len(self.offerings):
                raise ValueError("stable offering keys required")
            families = {f.key for f in self.offering_families}
            if any(
                o.family_key and o.family_key not in families for o in self.offerings
            ):
                raise ValueError("unknown offering family")
        return self


@dataclass(frozen=True)
class TopicSnapshot:
    id: UUID
    name: str
    categories: tuple[str, ...]


@dataclass(frozen=True)
class Approval:
    kind: ApprovalKind
    actor_id: UUID
    occurred_at: datetime
    evidence_ref: str


@dataclass(frozen=True)
class ObjectEvidence:
    id: UUID
    value: ObjectEvidenceInput
    recorded_by: UUID
    recorded_at: datetime


@dataclass
class ProfileRevision:
    id: UUID
    number: int
    content: ProfileContent
    created_by: UUID
    created_at: datetime
    status: Literal["draft", "submitted", "abandoned"] = "draft"
    topics: tuple[TopicSnapshot, ...] = ()
    approvals: list[Approval] = field(default_factory=list)
    object_evidence: list[ObjectEvidence] = field(default_factory=list)


@dataclass
class Publication:
    revision_id: UUID
    state: Literal["published", "withdrawn"]
    actor_id: UUID
    occurred_at: datetime


@dataclass
class CoachAggregate:
    id: UUID
    display_name: str
    request_id: UUID | None
    lifecycle: Lifecycle = "draft"
    version: int = 1
    publication_floor: int = 0
    revisions: list[ProfileRevision] = field(default_factory=list)
    publications: dict[Environment, Publication] = field(default_factory=dict)
    events: list[tuple[str, UUID, datetime, UUID]] = field(default_factory=list)

    def revision(self, revision_id: UUID) -> ProfileRevision:
        for revision in self.revisions:
            if revision.id == revision_id:
                return revision
        raise LookupError("revision not found")


class RegistryRepository(Protocol):
    async def create(
        self, *, display_name: str, request_id: UUID, actor_id: UUID, now: datetime
    ) -> CoachAggregate: ...
    async def get(self, coach_id: UUID) -> CoachAggregate | None: ...
    async def list_coaches(
        self, *, limit: int, offset: int
    ) -> tuple[CoachAggregate, ...]: ...
    def edit(
        self, coach_id: UUID, expected_version: int
    ) -> AbstractAsyncContextManager[CoachAggregate]: ...
    async def topics(
        self, topic_ids: tuple[UUID, ...]
    ) -> tuple[TopicSnapshot, ...]: ...
    async def has_future_calendar(self, coach_id: UUID, now: datetime) -> bool: ...


def activation_ready(coach):
    return any(
        r.number > coach.publication_floor
        and r.status == "submitted"
        and {"content_review", "person_consent"} <= {a.kind for a in r.approvals}
        for r in coach.revisions
    )


def publication_ready(coach, revision, environment):
    previous = coach.publications.get(environment)
    return (
        coach.lifecycle == "active"
        and revision.status == "submitted"
        and revision.number > coach.publication_floor
        and {"content_review", "person_consent", environment}
        <= {a.kind for a in revision.approvals}
        and bool(revision.content.profile_path)
        and evidence_ready(revision, environment)
        and all(
            not a.active or environment in a.scopes for a in revision.content.assets
        )
        and not (
            previous
            and previous.state == "withdrawn"
            and revision.number <= coach.revision(previous.revision_id).number
        )
    )


def management_capabilities(coach, revision, *, future_calendar=False):
    """Business actions, not UI role guesses; mutations still recheck under the row lock."""
    if coach.request_id is None:
        return {
            "new_revision": False,
            "lifecycles": [],
            "editable": False,
            "submit": False,
            "approvals": [],
            "publish": [],
            "withdraw": [],
            "object_evidence": False,
        }
    return {
        "new_revision": coach.lifecycle != "archived"
        and not any(r.status == "draft" for r in coach.revisions),
        "lifecycles": sorted(
            s
            for s in LIFECYCLE_TRANSITIONS[coach.lifecycle]
            if (activation_ready(coach) if s == "active" else not future_calendar)
        ),
        "editable": bool(revision and revision.status == "draft"),
        "object_evidence": bool(
            revision
            and revision.status == "submitted"
            and revision.content.target_version == 1
        ),
        "submit": bool(revision and revision.status == "draft"),
        "approvals": (
            sorted(
                {"content_review", "person_consent", "preview", "production"}
                - {a.kind for a in revision.approvals}
            )
            if revision and revision.status == "submitted"
            else []
        ),
        "publish": [
            e
            for e in ("preview", "production")
            if revision
            and publication_ready(coach, revision, e)
            and not (
                coach.publications.get(e)
                and coach.publications[e].state == "published"
                and coach.publications[e].revision_id == revision.id
            )
        ],
        "withdraw": [
            e for e, p in coach.publications.items() if p.state == "published"
        ],
    }


def require_complete_target_update(previous, content):
    """Full-snapshot writes must not erase fields unknown to an older client."""
    if not previous.target_version:
        return
    if not content.target_version:
        raise RegistryConflict("rich contract downgrade forbidden")

    def complete(old, new, path=""):
        for name, spec in type(old).model_fields.items():
            old_value, new_value = getattr(old, name), getattr(new, name)
            if name not in new.model_fields_set and getattr(
                old, name
            ) != spec.get_default(call_default_factory=True):
                raise RegistryConflict("rich field omitted: " + path + name)
            if isinstance(old_value, BaseModel) and isinstance(new_value, BaseModel):
                complete(old_value, new_value, path + name + ".")
            elif isinstance(old_value, (tuple, list)) and isinstance(
                new_value, (tuple, list)
            ):
                keyed = {
                    v.key: v
                    for v in old_value
                    if isinstance(v, BaseModel) and hasattr(v, "key")
                }
                for index, value in enumerate(new_value):
                    if isinstance(value, BaseModel):
                        previous_item = (
                            keyed.get(value.key)
                            if hasattr(value, "key")
                            else (old_value[index] if index < len(old_value) else None)
                        )
                        if isinstance(previous_item, BaseModel):
                            complete(previous_item, value, path + name + ".")

    complete(previous, content)


class CoachRegistryService:
    def __init__(self, repository: RegistryRepository):
        self.repository = repository

    @staticmethod
    def authorize(actor: SessionPrincipal):
        if "admin" not in actor.roles:
            raise RegistryDenied("admin required")

    async def create(self, *, actor, display_name, request_id, now):
        self.authorize(actor)
        name = display_name.strip()
        if not name or len(name) > 200:
            raise ValueError("invalid name")
        return await self.repository.create(
            display_name=name, request_id=request_id, actor_id=actor.user_id, now=now
        )

    async def mutate(
        self,
        *,
        actor,
        coach_id,
        expected_version,
        operation,
        now,
        content=None,
        revision_id=None,
        lifecycle=None,
        kind=None,
        evidence_ref=None,
        environment=None,
        evidence=None,
    ):
        self.authorize(actor)
        async with self.repository.edit(coach_id, expected_version) as coach:
            if coach.request_id is None:
                raise RegistryConflict("controlled adoption of legacy Coach required")
            entity_id = coach.id
            if operation == "revision":
                if coach.lifecycle == "archived" or any(
                    r.status == "draft" for r in coach.revisions
                ):
                    raise RegistryConflict("existing draft or archived")
                if content is None:
                    raise ValueError("profile required")
                if (
                    any(r.content.target_version for r in coach.revisions)
                    and not content.target_version
                ):
                    raise RegistryConflict("rich contract downgrade forbidden")
                if coach.revisions:
                    require_complete_target_update(coach.revisions[-1].content, content)
                revision = ProfileRevision(
                    uuid4(), len(coach.revisions) + 1, content, actor.user_id, now
                )
                revision.topics = await self.repository.topics(content.topic_ids)
                coach.revisions.append(revision)
                entity_id = revision.id
            elif operation == "draft":
                revision = coach.revision(revision_id)
                if revision.status != "draft" or content is None:
                    raise RegistryConflict("immutable revision")
                require_complete_target_update(revision.content, content)
                revision.content = content
                revision.topics = await self.repository.topics(content.topic_ids)
                entity_id = revision.id
            elif operation == "submit":
                revision = coach.revision(revision_id)
                if revision.status != "draft":
                    raise RegistryConflict("already submitted")
                # Re-resolve once at submission, then retain the approved snapshot.
                revision.topics = await self.repository.topics(
                    revision.content.topic_ids
                )
                revision.status = "submitted"
                entity_id = revision.id
            elif operation == "approve":
                revision = coach.revision(revision_id)
                if revision.status != "submitted" or kind not in {
                    "content_review",
                    "person_consent",
                    "preview",
                    "production",
                }:
                    raise RegistryConflict("submitted revision required")
                if (
                    not evidence_ref
                    or not evidence_ref.strip()
                    or len(evidence_ref) > 200
                ):
                    raise ValueError("opaque evidence reference required")
                if any(a.kind == kind for a in revision.approvals):
                    raise RegistryConflict("approval already attested")
                revision.approvals.append(
                    Approval(kind, actor.user_id, now, evidence_ref.strip())
                )
                entity_id = revision.id
            elif operation == "evidence":
                revision = coach.revision(revision_id)
                if (
                    revision.status != "submitted"
                    or not revision.content.target_version
                ):
                    raise RegistryConflict("submitted target revision required")
                if not isinstance(evidence, ObjectEvidenceInput):
                    raise ValueError("typed object evidence required")
                if (
                    subjects(revision.content, revision.topics).get(
                        (evidence.subject_type, evidence.subject_key)
                    )
                    != evidence.subject_hash
                ):
                    raise RegistryConflict("evidence subject/hash mismatch")
                if any(e.value.key == evidence.key for e in revision.object_evidence):
                    raise RegistryConflict("evidence key already recorded")
                if (evidence.approved_at and evidence.approved_at > now) or (
                    evidence.approved_on and evidence.approved_on > now.date()
                ):
                    raise ValueError("future historical approval forbidden")
                revision.object_evidence.append(
                    ObjectEvidence(uuid4(), evidence, actor.user_id, now)
                )
                publication = coach.publications.get(evidence.environment)
                if (
                    publication
                    and publication.state == "published"
                    and publication.revision_id == revision.id
                    and not evidence_ready(revision, evidence.environment)
                ):
                    publication.state = "withdrawn"
                    publication.actor_id, publication.occurred_at = actor.user_id, now
                entity_id = revision.id
            elif operation == "lifecycle":
                if lifecycle not in LIFECYCLE_TRANSITIONS[coach.lifecycle]:
                    raise RegistryConflict("invalid lifecycle transition")
                if lifecycle == "active":
                    if not activation_ready(coach):
                        raise RegistryConflict("fresh reviewed revision required")
                else:
                    if await self.repository.has_future_calendar(coach.id, now):
                        raise RegistryConflict(
                            "withdraw current/future Calendar offers first"
                        )
                    for publication in coach.publications.values():
                        publication.state = "withdrawn"
                        publication.actor_id, publication.occurred_at = (
                            actor.user_id,
                            now,
                        )
                    coach.publication_floor = max(
                        (r.number for r in coach.revisions), default=0
                    )
                    for revision in coach.revisions:
                        if revision.status == "draft":
                            revision.status = "abandoned"
                            coach.events.append(
                                (
                                    "coach_registry.revision_abandoned",
                                    actor.user_id,
                                    now,
                                    revision.id,
                                )
                            )
                coach.lifecycle = lifecycle
            elif operation in {"publish", "withdraw"}:
                if environment not in {"preview", "production"}:
                    raise ValueError("explicit environment required")
                if operation == "publish":
                    revision = coach.revision(revision_id)
                    previous = coach.publications.get(environment)
                    if (
                        previous is not None
                        and previous.state == "withdrawn"
                        and revision.number
                        <= coach.revision(previous.revision_id).number
                    ):
                        raise RegistryConflict(
                            "withdrawn publication requires newer approved revision"
                        )
                    if (
                        coach.lifecycle != "active"
                        or revision.status != "submitted"
                        or revision.number <= coach.publication_floor
                    ):
                        raise RegistryConflict(
                            "active Coach and fresh submitted revision required"
                        )
                    if not {"content_review", "person_consent", environment} <= {
                        a.kind for a in revision.approvals
                    }:
                        raise RegistryConflict("missing revision/environment approval")
                    if not revision.content.profile_path or any(
                        a.active and environment not in a.scopes
                        for a in revision.content.assets
                    ):
                        raise RegistryConflict("path or scoped asset approval missing")
                    if not evidence_ready(revision, environment):
                        raise RegistryConflict(
                            "missing exact object/environment evidence"
                        )
                    coach.publications[environment] = Publication(
                        revision.id, "published", actor.user_id, now
                    )
                    entity_id = revision.id
                else:
                    publication = coach.publications.get(environment)
                    if publication is None or publication.state != "published":
                        raise RegistryConflict("not published")
                    publication.state = "withdrawn"
                    publication.actor_id, publication.occurred_at = actor.user_id, now
                    entity_id = publication.revision_id
            else:
                raise ValueError("unknown Registry operation")
            coach.version += 1
            action = "coach_registry." + operation
            if operation in {"publish", "withdraw"}:
                action += "." + environment
            if operation == "lifecycle":
                action += "." + lifecycle
            coach.events.append((action, actor.user_id, now, entity_id))
        return coach


def public_projection(
    coaches: tuple[CoachAggregate, ...], environment: Environment
) -> dict:
    """Allowlisted static export, not a public database endpoint or an Astro switch."""
    if environment not in {"preview", "production"}:
        raise ValueError("explicit environment required")
    items, paths = [], set()
    for coach in coaches:
        publication = coach.publications.get(environment)
        if (
            coach.lifecycle != "active"
            or publication is None
            or publication.state != "published"
        ):
            continue
        revision = coach.revision(publication.revision_id)
        if (
            revision.status != "submitted"
            or revision.number <= coach.publication_floor
            or not {"content_review", "person_consent", environment}
            <= {a.kind for a in revision.approvals}
            or not evidence_ready(revision, environment)
        ):
            raise RegistryConflict("inconsistent publication")
        content = revision.content
        if any(a.active and environment not in a.scopes for a in content.assets):
            raise RegistryConflict("asset scope inconsistent with publication")
        if not content.profile_path or content.profile_path in paths:
            raise RegistryConflict("missing/duplicate public path")
        paths.add(content.profile_path)
        item = content.model_dump(
            mode="json",
            include={
                "display_name",
                "academic_suffix",
                "short_intro",
                "description",
                "professional_background",
                "target_groups",
                "profile_path",
                "competencies",
            },
        )
        item["topics"] = [
            {"name": t.name, "categories": list(t.categories)} for t in revision.topics
        ]
        item["assets"] = [
            a.model_dump(
                mode="json", include={"type", "reference", "sha256", "alt_text"}
            )
            for a in content.assets
            if a.active and environment in a.scopes
        ]
        item["offerings"] = [
            (
                public_offering(o)
                if content.target_version
                else o.model_dump(
                    mode="json", include={"title", "type", "description", "ordering"}
                )
            )
            for o in sorted(content.offerings, key=lambda x: x.ordering)
            if o.active and (not content.target_version or not o.family_key)
        ]
        if content.target_version:
            item.update(public_target(content, environment))
        items.append(item)
    return {
        "schema": 1,
        "environment": environment,
        "coaches": sorted(items, key=lambda x: x["profile_path"]),
    }
