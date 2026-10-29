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
from competence_hub_api.portal.coach_target import (
    Boundary,
    ObjectEvidenceInput,
    OfferingFamily,
    Presentation,
    PublicRole,
    Qualification,
    requirements,
    subjects,
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
                    if (
                        key in {"active", "bookable", "public"}
                        and type(item) is not bool
                    ):
                        raise ValueError("actual JSON boolean required")
                    if (
                        key
                        in {
                            "ordering",
                            "target_version",
                            "minutes",
                            "weeks",
                            "sessions_per_week",
                            "session_minutes",
                            "portrait_width",
                            "portrait_height",
                        }
                        and item is not None
                        and type(item) is not int
                    ):
                        raise ValueError("actual JSON integer required")
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
        if any(
            (
                self.profile.public_roles,
                self.profile.qualifications,
                self.profile.offering_families,
                self.profile.presentation,
                self.profile.boundaries,
            )
        ):
            raise ValueError("target collections belong in the typed import sections")
        if (
            not isinstance(self, CoachTargetImportRecord)
            and self.profile.target_version
        ):
            raise ValueError("target_version 1 requires the v2 import contract")
        if not isinstance(self, CoachTargetImportRecord):
            ProfileContent.model_validate(
                {
                    **self.profile.model_dump(),
                    "offerings": [o.content for o in self.offerings],
                }
            )
        return self


class CoachTargetImportRecord(CoachImportRecord):
    """Selected only by an explicit coach-import-v2 mapping contract."""

    roles: tuple[PublicRole, ...] = Field(default=(), max_length=20)
    qualifications: tuple[Qualification, ...] = Field(default=(), max_length=50)
    boundaries: tuple[Boundary, ...] = Field(default=(), max_length=10)
    offering_families: tuple[OfferingFamily, ...] = Field(default=(), max_length=30)
    presentation: Presentation | None = None
    object_evidence: tuple[ObjectEvidenceInput, ...] = Field(default=(), max_length=500)

    @model_validator(mode="after")
    def explicit_target(self):
        if self.profile.target_version != 1:
            raise ValueError("v2 requires target_version 1")
        if any(o.content.key != o.key for o in self.offerings):
            raise ValueError("offering source and target keys must match exactly")
        return self


class TopicRule(StrictModel):
    reference: str = Field(pattern=KEY)
    topic_id: UUID
    accepted_labels: tuple[str, ...] = Field(min_length=1, max_length=20)
    categories: tuple[Category, ...] = Field(min_length=1, max_length=3)


class ImportMappingContract(StrictModel):
    version: Literal["coach-import-v1", "coach-import-v2"] = "coach-import-v1"
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
    object_evidence: tuple[ObjectEvidenceInput, ...] = ()


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
            "content": import_profile_data(content),
            "topics": [
                {"id": str(t.id), "name": t.name, "categories": sorted(t.categories)}
                for t in sorted(topics, key=lambda t: str(t.id))
            ],
        }
    )


def import_offering_data(offer, *, target_version):
    data = offer.model_dump(mode="json")
    if not target_version:
        data = {
            k: data[k] for k in ("title", "type", "description", "active", "ordering")
        }
    return data


def import_profile_data(content):
    """Keep schema8 ledger hashes byte-compatible after additive domain defaults."""
    data = content.model_dump(mode="json")
    if not content.target_version:
        for name in (
            "target_version",
            "public_roles",
            "qualifications",
            "offering_families",
            "presentation",
            "boundaries",
        ):
            data.pop(name, None)
        data["offerings"] = [
            import_offering_data(o, target_version=0) for o in content.offerings
        ]
    return data


def normalized_target(content):
    """Order keyed collections and semantic sets, preserving literal sequence fields."""
    if not content.get("target_version"):
        return content

    def visit(value, name=""):
        if isinstance(value, dict):
            return {k: visit(v, k) for k, v in value.items()}
        if isinstance(value, list):
            result = [visit(v) for v in value]
            if name in {"service_domains", "excluded_services", "scopes"}:
                return sorted(result)
            if (
                name not in {"sections", "external_links"}
                and result
                and all(isinstance(v, dict) and "key" in v for v in result)
            ):
                return sorted(result, key=lambda v: (v.get("ordering", 0), v["key"]))
            return result
        return value

    return visit(content)


def target_items(source, items, issue):
    """Nested identity includes its stable parent, never the current display title."""

    def add(kind, key, value):
        if len(key) > 120:
            issue("VALIDATION_ERROR", "nested_item_key")
        if (kind, key) in items:
            issue("IDENTITY_CONFLICT", kind)
        items[(kind, key)] = fingerprint(
            normalized_target({"target_version": 1, "value": value})["value"]
        )

    def nested(owner, value):
        for variant in value.variants:
            add("variant", owner + "/" + variant.key, variant.model_dump(mode="json"))
        for boundary in value.boundaries:
            add(
                "boundary", owner + "/" + boundary.key, boundary.model_dump(mode="json")
            )

    for family in source.offering_families:
        add(
            "family",
            family.key,
            normalized_target(
                {"target_version": 1, "value": family.model_dump(mode="json")}
            )["value"],
        )
        nested("family/" + family.key, family)
    for offer in source.offerings:
        nested("offering/" + offer.key, offer.content)
    if source.presentation:
        add(
            "presentation",
            "presentation",
            normalized_target(
                {
                    "target_version": 1,
                    "value": source.presentation.model_dump(mode="json"),
                }
            )["value"],
        )
        for section in source.presentation.sections:
            add("presentation_section", section.key, section.model_dump(mode="json"))
        for link in source.presentation.external_links:
            add("presentation_link", link.key, link.model_dump(mode="json"))
    for evidence in source.object_evidence:
        add("object_evidence", evidence.key, evidence.model_dump(mode="json"))


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
            model = (
                CoachTargetImportRecord
                if contract.version == "coach-import-v2"
                else CoachImportRecord
            )
            source = model.model_validate(normalized_input(raw))
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
        rich = isinstance(source, CoachTargetImportRecord)
        content = source.profile.model_dump(mode="json", exclude_unset=rich)
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
                if (
                    not (rich and kind in {"role", "qualification", "boundary"})
                    and item.visibility != "public"
                ):
                    issue(
                        {
                            "qualification": "QUALIFICATION_MAPPING_REQUIRED",
                            "role": "ROLE_MAPPING_REQUIRED",
                            "boundary": "BOUNDARY_REVIEW_REQUIRED",
                        }.get(kind, "UNSUPPORTED_INFORMATION"),
                        kind,
                    )
                item_data = item.model_dump(mode="json")
                if rich:
                    item_data = normalized_target(
                        {"target_version": 1, "value": item_data}
                    )["value"]
                items[(kind, item.key)] = fingerprint(item_data)
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
            if collection and not rich:
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
        if source.boundaries and not rich:
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
            offer_data = import_offering_data(
                offer.content, target_version=source.profile.target_version
            )
            if rich:
                offer_data = normalized_target(
                    {"target_version": 1, "value": offer_data}
                )["value"]
            items[("offering", offer.key)] = fingerprint(offer_data)
            content["offerings"].append(
                offer.content.model_dump(mode="json", exclude_unset=True)
                if rich
                else offer_data
            )
        if rich:
            content.update(
                public_roles=[
                    v.model_dump(mode="json", exclude_unset=True) for v in source.roles
                ],
                qualifications=[
                    v.model_dump(mode="json", exclude_unset=True)
                    for v in source.qualifications
                ],
                offering_families=[
                    v.model_dump(mode="json", exclude_unset=True)
                    for v in source.offering_families
                ],
                boundaries=[
                    v.model_dump(mode="json", exclude_unset=True)
                    for v in source.boundaries
                ],
                presentation=(
                    source.presentation.model_dump(mode="json", exclude_unset=True)
                    if source.presentation
                    else None
                ),
            )
            content = normalized_target(content)
            target_items(source, items, issue)
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
            content["assets"].append(
                asset.content.model_dump(mode="json", exclude_unset=True)
                if rich
                else asset_data
            )
        if rich:
            # Expanded defaults must not turn omitted populated fields into clears.
            sections = {
                "public_roles": "roles",
                "qualifications": "qualifications",
                "offering_families": "offering_families",
                "presentation": "presentation",
                "boundaries": "boundaries",
                "topic_ids": "topics",
                "competencies": "competencies",
                "target_groups": "target_groups",
                "offerings": "offerings",
                "assets": "assets",
            }
            present = (source.profile.model_fields_set - sections.keys()) | {
                target
                for target, original in sections.items()
                if original in source.model_fields_set
            }
            content = normalized_target(
                {k: v for k, v in content.items() if k in present}
            )
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
        object_evidence = ()
        if rich:
            hashes = subjects(mapped, mapped_topics.values())
            object_evidence = tuple(source.object_evidence)
            for evidence in object_evidence:
                if (
                    hashes.get((evidence.subject_type, evidence.subject_key))
                    != evidence.subject_hash
                ):
                    issue(
                        "OBJECT_EVIDENCE_REVIEW_REQUIRED",
                        "object_evidence.subject_hash",
                    )
                if (evidence.approved_at and evidence.approved_at > now) or (
                    evidence.approved_on and evidence.approved_on > now.date()
                ):
                    issue(
                        "OBJECT_EVIDENCE_REVIEW_REQUIRED",
                        "object_evidence.historical_date",
                    )
            for env in pub.published:
                for kind, key, evidence_kind in requirements(mapped):
                    matches = [
                        e
                        for e in object_evidence
                        if (
                            e.subject_type,
                            e.subject_key,
                            e.kind,
                            e.environment,
                            e.scope,
                        )
                        == (kind, key, evidence_kind, env, "public_content")
                    ]
                    if not matches or matches[-1].status != "approved":
                        issue(
                            "OBJECT_EVIDENCE_REVIEW_REQUIRED",
                            "publication.object_evidence",
                        )
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
            source_data = {
                "profile": profile_hash,
                "publication": publication_hash,
                "source_ref": source.provenance.source_ref,
                "items": [
                    [kind, key, value] for (kind, key), value in sorted(items.items())
                ],
            }
            if rich:
                # Evidence order is append-only history; the latest exact slot wins.
                source_data["object_evidence"] = [
                    e.model_dump(mode="json") for e in object_evidence
                ]
            source_hash = fingerprint(source_data)
            result.records.append(
                PreparedRecord(
                    source,
                    mapped,
                    source_hash,
                    profile_hash,
                    contract_hash,
                    publication_hash,
                    items,
                    object_evidence,
                )
            )
    return result
