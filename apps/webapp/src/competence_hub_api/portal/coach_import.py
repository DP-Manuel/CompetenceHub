"""Typed, pure import validation/planning; Coach content remains owned by COACH-1."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
import hashlib
import json
import re
from typing import Literal
import unicodedata
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    ValidationError,
    model_validator,
)

from competence_hub_api.portal.coach_registry import (
    Asset,
    Offering,
    ProfileContent,
)

Category = Literal[
    "personalentwicklung", "persoenlichkeitsentwicklung", "karrierecoaching"
]
Environment = Literal["preview", "production"]
KEY = r"^[a-z0-9][a-z0-9/_-]{0,119}$"
REF = r"^[a-zA-Z0-9][a-zA-Z0-9:._/-]{0,199}$"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceIdentity(StrictModel):
    source_system: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,79}$")
    source_key: str = Field(pattern=KEY)

    @property
    def key(self):
        return self.source_system, self.source_key


class SourceText(StrictModel):
    key: str = Field(pattern=KEY)
    text: str = Field(min_length=1, max_length=1000)
    visibility: Literal["public", "internal"] = "public"


class SourceTopic(StrictModel):
    reference: str = Field(pattern=KEY)
    label: str = Field(min_length=1, max_length=200)


class SourceOffering(StrictModel):
    key: str = Field(pattern=KEY)
    content: Offering


class SourceAsset(StrictModel):
    key: str = Field(pattern=KEY)
    content: Asset


class SourceEvidence(StrictModel):
    key: str = Field(pattern=KEY)
    kind: Literal["content_review", "person_consent", "preview", "production"]
    environment: Environment | None = None
    source: str = Field(pattern=REF)
    historical_at: datetime | None = None

    @model_validator(mode="after")
    def valid_binding(self):
        if (
            self.kind in {"preview", "production"}
            and self.environment != self.kind
            or self.kind in {"content_review", "person_consent"}
            and self.environment is not None
        ):
            raise ValueError("explicit evidence environment required")
        if self.historical_at and self.historical_at.tzinfo is None:
            raise ValueError("known evidence dates must be timezone-aware")
        if self.historical_at:
            object.__setattr__(
                self, "historical_at", self.historical_at.astimezone(UTC)
            )
        return self


class InitialPublication(StrictModel):
    lifecycle: Literal["draft", "active"] = "draft"
    published: tuple[Environment, ...] = Field(default=(), max_length=2)
    evidence: tuple[SourceEvidence, ...] = Field(default=(), max_length=4)


class Provenance(StrictModel):
    source_ref: str = Field(pattern=REF)
    observed_at: datetime | None = None
    technical_revision: str | None = Field(default=None, max_length=100)


class CoachImportRecord(StrictModel):
    source_identity: SourceIdentity
    expected_coach_id: UUID | None = None
    profile: ProfileContent
    topics: tuple[SourceTopic, ...] = Field(default=(), max_length=50)
    competencies: tuple[SourceText, ...] = Field(default=(), max_length=50)
    target_groups: tuple[SourceText, ...] = Field(default=(), max_length=30)
    offerings: tuple[SourceOffering, ...] = Field(default=(), max_length=100)
    assets: tuple[SourceAsset, ...] = Field(default=(), max_length=1)
    qualifications: tuple[SourceText, ...] = Field(default=(), max_length=30)
    roles: tuple[SourceText, ...] = Field(default=(), max_length=20)
    boundaries: tuple[SourceText, ...] = Field(default=(), max_length=10)
    publication: InitialPublication = InitialPublication()
    provenance: Provenance

    @model_validator(mode="before")
    @classmethod
    def exact_scalar_types(cls, value):
        def visit(node):
            if isinstance(node, dict):
                for key, item in node.items():
                    if key == "active" and type(item) is not bool:
                        raise ValueError("active requires a JSON boolean")
                    if key == "ordering" and type(item) is not int:
                        raise ValueError("ordering requires a JSON integer")
                    visit(item)
            elif isinstance(node, (list, tuple)):
                for item in node:
                    visit(item)

        visit(value)
        return value

    @model_validator(mode="after")
    def no_parallel_collections(self):
        if any(
            (
                self.profile.topic_ids,
                self.profile.competencies,
                self.profile.target_groups,
                self.profile.offerings,
                self.profile.assets,
            )
        ):
            raise ValueError("collections belong only in the typed import sections")
        return self


class TopicRule(StrictModel):
    reference: str = Field(pattern=KEY)
    topic_id: UUID
    accepted_labels: tuple[str, ...] = Field(min_length=1, max_length=20)
    categories: tuple[Category, ...] = Field(min_length=1, max_length=3)


class ImportMappingContract(StrictModel):
    version: Literal["coach-import-v1"] = "coach-import-v1"
    topics: tuple[TopicRule, ...] = Field(default=(), max_length=100)
    role_mapping: Literal["unmapped", "literal_background_v1"] = "unmapped"
    qualification_mapping: Literal["unmapped", "literal_background_v1"] = "unmapped"
    boundary_mapping: Literal["unmapped", "literal_description_v1"] = "unmapped"
    review_ref: str | None = Field(default=None, pattern=REF)
    attest_initial_publication: StrictBool = False


@dataclass(frozen=True)
class ImportIssue:
    code: str
    record_ref: str
    field: str


@dataclass
class PreparedRecord:
    source: CoachImportRecord
    content: ProfileContent
    source_hash: str
    profile_hash: str
    contract_hash: str
    publication_hash: str
    items: dict[tuple[str, str], str]


@dataclass
class ValidationResult:
    records: list[PreparedRecord] = field(default_factory=list)
    issues: list[ImportIssue] = field(default_factory=list)


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def fingerprint(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def profile_fingerprint(content, topics):
    return fingerprint(
        {
            "content": content.model_dump(mode="json"),
            "topics": [
                {"id": str(t.id), "name": t.name, "categories": sorted(t.categories)}
                for t in sorted(topics, key=lambda t: str(t.id))
            ],
        }
    )


def text_value(value):
    lines = (
        unicodedata.normalize("NFC", value)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
    )
    return "\n".join(" ".join(line.split()) for line in lines).strip()


def normalized_input(value, key=""):
    if isinstance(value, dict):
        return {k: normalized_input(v, k) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalized_input(v, key) for v in value]
    if isinstance(value, str):
        result = text_value(value)
        if (
            key
            in {
                "academic_suffix",
                "description",
                "professional_background",
                "profile_path",
            }
            and not result
        ):
            return None
        if key == "profile_path" and result.startswith(("coaches/", "/coaches/")):
            result = "/" + result.strip("/") + "/"
        return result
    return value


def topic_token(value):
    # Curated aliases only: this is collision detection, not a semantic classifier.
    return re.sub(r"[\s-]+", "", unicodedata.normalize("NFC", value).casefold())


def record_ref(identity):
    return fingerprint(list(identity.key))[:16]


def validate_records(values, contract, catalogue, asset_bytes, *, now):
    result = ValidationResult()
    if len(values) > 50:
        result.issues.append(ImportIssue("VALIDATION_ERROR", "batch", "batch_size"))
        return result
    contract_data = contract.model_dump(mode="json")
    contract_data["topics"] = [
        {
            **r.model_dump(mode="json"),
            "accepted_labels": sorted({topic_token(a) for a in r.accepted_labels}),
            "categories": sorted(set(r.categories)),
        }
        for r in sorted(contract.topics, key=lambda r: r.reference)
    ]
    contract_hash = fingerprint(contract_data)
    identities, paths = set(), set()
    for index, raw in enumerate(values):
        try:
            source = CoachImportRecord.model_validate(normalized_input(raw))
        except ValidationError:
            result.issues.append(
                ImportIssue("VALIDATION_ERROR", f"record-{index}", "schema")
            )
            continue
        ref = record_ref(source.source_identity)
        start = len(result.issues)

        def issue(code, name):
            result.issues.append(ImportIssue(code, ref, name))

        if source.source_identity.key in identities:
            issue("IDENTITY_CONFLICT", "source_identity")
        identities.add(source.source_identity.key)
        path = source.profile.profile_path
        if path and path in paths:
            issue("PROFILE_PATH_CONFLICT", "profile.profile_path")
        if path:
            paths.add(path)
        items, mapped_topics = {}, {}
        rules = {r.reference: r for r in contract.topics}
        tokens = {}
        for rule in contract.topics:
            for alias in rule.accepted_labels:
                tokens.setdefault(topic_token(alias), set()).add(rule.topic_id)
        if len(rules) != len(contract.topics) or len(
            {r.topic_id for r in contract.topics}
        ) != len(contract.topics):
            issue("TOPIC_CONFLICT", "mapping.topics")
        for topic in source.topics:
            rule = rules.get(topic.reference)
            snapshot = catalogue.get(rule.topic_id) if rule else None
            if (
                not rule
                or not snapshot
                or tokens.get(topic_token(topic.label)) != {rule.topic_id}
                or topic_token(topic.label)
                not in {topic_token(a) for a in rule.accepted_labels}
                or set(snapshot.categories) != set(rule.categories)
            ):
                issue("TOPIC_CONFLICT", "topics")
                continue
            mapped_topics[rule.topic_id] = snapshot
            items[("topic", rule.reference)] = fingerprint(
                {
                    "id": str(rule.topic_id),
                    "name": snapshot.name,
                    "categories": sorted(snapshot.categories),
                }
            )
        content = source.profile.model_dump(mode="json")
        for kind, collection in (
            ("competency", source.competencies),
            ("target_group", source.target_groups),
            ("role", source.roles),
            ("qualification", source.qualifications),
            ("boundary", source.boundaries),
        ):
            for item in collection:
                if (kind, item.key) in items:
                    issue("IDENTITY_CONFLICT", kind)
                if item.visibility != "public":
                    issue(
                        {
                            "qualification": "QUALIFICATION_MAPPING_REQUIRED",
                            "role": "ROLE_MAPPING_REQUIRED",
                            "boundary": "BOUNDARY_REVIEW_REQUIRED",
                        }.get(kind, "UNSUPPORTED_INFORMATION"),
                        kind,
                    )
                items[(kind, item.key)] = fingerprint(item.model_dump(mode="json"))
        background = content.get("professional_background") or ""
        for name, collection, mode, code in (
            (
                "Rollenbezeichnungen",
                source.roles,
                contract.role_mapping,
                "ROLE_MAPPING_REQUIRED",
            ),
            (
                "Qualifikationen",
                source.qualifications,
                contract.qualification_mapping,
                "QUALIFICATION_MAPPING_REQUIRED",
            ),
        ):
            if collection:
                if mode != "literal_background_v1" or not contract.review_ref:
                    issue(code, name)
                else:
                    section = (
                        name
                        + "\n"
                        + "\n".join(
                            "- " + i.text
                            for i in sorted(collection, key=lambda i: i.key)
                        )
                    )
                    background = "\n\n".join(filter(None, (background, section)))
        content["professional_background"] = background or None
        if source.boundaries:
            if (
                contract.boundary_mapping != "literal_description_v1"
                or not contract.review_ref
            ):
                issue("BOUNDARY_REVIEW_REQUIRED", "boundaries")
            else:
                section = "Leistungsgrenzen\n" + "\n".join(
                    i.text for i in sorted(source.boundaries, key=lambda i: i.key)
                )
                content["description"] = "\n\n".join(
                    filter(None, (content.get("description"), section))
                )
        content["topic_ids"] = sorted(mapped_topics, key=str)
        content["competencies"] = [
            i.text for i in sorted(source.competencies, key=lambda i: i.key)
        ]
        content["target_groups"] = [
            i.text for i in sorted(source.target_groups, key=lambda i: i.key)
        ]
        content["offerings"] = []
        for offer in sorted(source.offerings, key=lambda o: o.content.ordering):
            if ("offering", offer.key) in items:
                issue("IDENTITY_CONFLICT", "offerings")
            items[("offering", offer.key)] = fingerprint(
                offer.content.model_dump(mode="json")
            )
            content["offerings"].append(offer.content.model_dump(mode="json"))
        content["assets"] = []
        for asset in source.assets:
            data = asset_bytes.get(asset.content.reference)
            if data is None or hashlib.sha256(data).hexdigest() != asset.content.sha256:
                issue("ASSET_MAPPING_REQUIRED", "assets")
            asset_data = {
                **asset.content.model_dump(mode="json"),
                "scopes": sorted(asset.content.scopes),
            }
            items[("asset", asset.key)] = fingerprint(asset_data)
            content["assets"].append(asset_data)
        pub = source.publication
        kinds = {e.kind for e in pub.evidence}
        if (
            len(kinds) != len(pub.evidence)
            or len({e.key for e in pub.evidence}) != len(pub.evidence)
            or len(set(pub.published)) != len(pub.published)
        ):
            issue("PUBLICATION_EVIDENCE_REQUIRED", "publication")
        if pub.published and (pub.lifecycle != "active" or not path):
            issue("PUBLICATION_EVIDENCE_REQUIRED", "publication")
        if pub.lifecycle == "active" and (
            not contract.attest_initial_publication
            or not contract.review_ref
            or not {"content_review", "person_consent", *pub.published} <= kinds
        ):
            issue("PUBLICATION_EVIDENCE_REQUIRED", "publication")
        if any(e.historical_at and e.historical_at > now for e in pub.evidence):
            issue("PUBLICATION_EVIDENCE_REQUIRED", "historical_at")
        if any(
            a.content.active and any(e not in a.content.scopes for e in pub.published)
            for a in source.assets
        ):
            issue("ASSET_MAPPING_REQUIRED", "asset.scopes")
        try:
            mapped = ProfileContent.model_validate(content)
        except ValidationError:
            issue("UNSUPPORTED_INFORMATION", "mapped_profile")
            continue
        if len(result.issues) == start:
            publication_hash = fingerprint(
                {
                    **pub.model_dump(mode="json"),
                    "published": sorted(pub.published),
                    "evidence": [
                        e.model_dump(mode="json")
                        for e in sorted(pub.evidence, key=lambda e: e.key)
                    ],
                }
            )
            profile_hash = profile_fingerprint(mapped, mapped_topics.values())
            source_hash = fingerprint(
                {
                    "profile": profile_hash,
                    "publication": publication_hash,
                    "source_ref": source.provenance.source_ref,
                    "items": [
                        [kind, key, value]
                        for (kind, key), value in sorted(items.items())
                    ],
                }
            )
            result.records.append(
                PreparedRecord(
                    source,
                    mapped,
                    source_hash,
                    profile_hash,
                    contract_hash,
                    publication_hash,
                    items,
                )
            )
    return result
