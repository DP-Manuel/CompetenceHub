"""Typed optional COACH-3C fields; identity/lifecycle remain in COACH-1."""

from datetime import UTC, date, datetime
import hashlib
import json
from typing import Literal
from urllib.parse import urlsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    field_validator,
    model_validator,
)

KEY = r"^[a-z0-9][a-z0-9/_-]{0,119}$"
REF = r"^[a-zA-Z0-9][a-zA-Z0-9:._/-]{0,199}$"
Domain = Literal[
    "coaching",
    "consulting",
    "psychotherapy",
    "training",
    "moderation",
    "health_promotion",
]
Environment = Literal["preview", "production"]


class TargetModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class PublicRole(TargetModel):
    key: str = Field(pattern=KEY)
    code: str = Field(pattern=KEY)
    display_label: str = Field(min_length=1, max_length=250)
    ordering: StrictInt = Field(default=0, ge=0, le=1000)


class Qualification(TargetModel):
    key: str = Field(pattern=KEY)
    canonical_title: str = Field(min_length=1, max_length=1000)
    public_display_label: str | None = Field(
        default=None, min_length=1, max_length=1000
    )
    issuer: str | None = Field(default=None, max_length=250)
    qualification_type: str | None = Field(default=None, max_length=100)
    ordering: StrictInt = Field(default=0, ge=0, le=1000)
    public: StrictBool = False
    status: Literal["active", "historical"] = "active"
    verification_state: Literal["unknown", "source_asserted", "verified"] = "unknown"
    evidence_reference: str | None = Field(default=None, pattern=REF)
    internal_note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def explicit_public_label(self):
        if self.public and not self.public_display_label:
            raise ValueError(
                "public qualification requires an explicit public display label"
            )
        return self


class Boundary(TargetModel):
    key: str = Field(pattern=KEY)
    text: str = Field(min_length=1, max_length=2000)
    excluded_services: tuple[str, ...] = Field(default=(), max_length=15)

    @field_validator("excluded_services")
    @classmethod
    def bounded_codes(cls, values):
        if len(set(values)) != len(values) or any(
            not v or len(v) > 80 or not all(c.islower() or c == "_" for c in v)
            for v in values
        ):
            raise ValueError("unique exclusion codes required")
        return values


class Duration(TargetModel):
    clock_start: str | None = Field(
        default=None, pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$"
    )
    clock_end: str | None = Field(
        default=None, pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$"
    )
    minutes: StrictInt | None = Field(default=None, ge=1, le=10080)
    weeks: StrictInt | None = Field(default=None, ge=1, le=104)
    sessions_per_week: StrictInt | None = Field(default=None, ge=1, le=14)
    session_minutes: StrictInt | None = Field(default=None, ge=1, le=1440)
    label: str | None = Field(default=None, max_length=250)

    @model_validator(mode="after")
    def coherent(self):
        if bool(self.clock_start) != bool(self.clock_end) or (
            self.clock_start and self.clock_end <= self.clock_start
        ):
            raise ValueError("complete same-day clock window required")
        if (self.sessions_per_week or self.session_minutes) and not self.weeks:
            raise ValueError("program schedule requires number of weeks")
        return self


class Variant(TargetModel):
    key: str = Field(pattern=KEY)
    kind: Literal["variant", "add_on", "option"]
    title: str = Field(min_length=1, max_length=250)
    description: str | None = Field(default=None, max_length=500)
    ordering: StrictInt = Field(default=0, ge=0, le=1000)
    active: StrictBool = True
    duration: Duration | None = None


def unique_items(items, name):
    if len({i.key for i in items}) != len(items) or len(
        {i.ordering for i in items}
    ) != len(items):
        raise ValueError("unique keys and ordering required for " + name)


class OfferingFamily(TargetModel):
    key: str = Field(pattern=KEY)
    title: str = Field(min_length=1, max_length=250)
    description: str | None = Field(default=None, max_length=2000)
    ordering: StrictInt = Field(default=0, ge=0, le=1000)
    active: StrictBool = True
    target_groups: tuple[str, ...] = Field(default=(), max_length=20)
    target_focus: tuple[str, ...] = Field(default=(), max_length=20)
    service_domains: tuple[Domain, ...] = Field(default=(), max_length=6)
    boundaries: tuple[Boundary, ...] = Field(default=(), max_length=10)
    variants: tuple[Variant, ...] = Field(default=(), max_length=20)
    protected_source_reference: str | None = Field(default=None, pattern=REF)

    @model_validator(mode="after")
    def coherent(self):
        unique_items(self.variants, "variants")
        if len({b.key for b in self.boundaries}) != len(self.boundaries):
            raise ValueError("duplicate boundary key")
        if len(set(self.service_domains)) != len(self.service_domains):
            raise ValueError("duplicate service domain")
        if any(
            not x.strip() or len(x) > 250
            for x in (*self.target_groups, *self.target_focus)
        ):
            raise ValueError("invalid target group")
        return self


class PublicCard(TargetModel):
    title: str = Field(min_length=1, max_length=250)
    text: str = Field(min_length=1, max_length=2000)


class PublicSection(TargetModel):
    key: str = Field(pattern=KEY)
    kind: Literal[
        "profile", "topics", "background", "formats", "boundary", "contact", "pending"
    ]
    headings: tuple[str, ...] = Field(default=(), max_length=10)
    paragraphs: tuple[str, ...] = Field(default=(), max_length=12)

    @model_validator(mode="after")
    def bounded_text(self):
        if any(
            not t.strip() or len(t) > 2000 for t in (*self.headings, *self.paragraphs)
        ):
            raise ValueError("invalid public section text")
        return self


class PublicLink(TargetModel):
    key: str = Field(pattern=KEY)
    label: str = Field(min_length=1, max_length=250)
    preview_url: str | None = Field(default=None, max_length=1000)
    production_url: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def safe_url(self):
        if not self.preview_url and not self.production_url:
            raise ValueError("at least one explicit target required")
        for value in (self.preview_url, self.production_url):
            if value is None:
                continue
            parsed = urlsplit(value)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or any(ord(c) < 33 or c in '<>"' for c in value)
            ):
                raise ValueError("public HTTPS URL without credentials required")
        return self


class Presentation(TargetModel):
    teaser: str | None = Field(default=None, max_length=1000)
    focus_labels: tuple[str, ...] = Field(default=(), max_length=30)
    background_labels: tuple[str, ...] = Field(default=(), max_length=50)
    languages: tuple[str, ...] = Field(default=(), max_length=10)
    sections: tuple[PublicSection, ...] = Field(default=(), max_length=20)
    topic_cards: tuple[PublicCard, ...] = Field(default=(), max_length=20)
    quote: str | None = Field(default=None, max_length=3000)
    external_links: tuple[PublicLink, ...] = Field(default=(), max_length=10)
    initials: str | None = Field(default=None, max_length=8)
    portrait_width: StrictInt | None = Field(default=None, ge=1, le=20000)
    portrait_height: StrictInt | None = Field(default=None, ge=1, le=20000)

    @model_validator(mode="after")
    def coherent(self):
        for values in (self.focus_labels, self.background_labels, self.languages):
            if any(not t.strip() or len(t) > 1000 for t in values):
                raise ValueError("invalid public label")
        for values in (self.sections, self.external_links):
            if len({v.key for v in values}) != len(values):
                raise ValueError("duplicate public item key")
        return self


class ObjectEvidenceInput(TargetModel):
    key: str = Field(pattern=KEY)
    subject_type: Literal["profile", "portrait", "qualification", "family", "offering"]
    subject_key: str = Field(pattern=KEY)
    subject_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    kind: Literal[
        "profile_content",
        "portrait_asset",
        "qualification",
        "offering_content",
        "publication",
        "protected_source",
    ]
    environment: Environment
    scope: Literal[
        "public_content", "internal_verification", "protected_source_content"
    ] = "public_content"
    status: Literal["approved", "unknown", "rejected"] = "unknown"
    evidence_reference: str | None = Field(default=None, pattern=REF)
    approved_by: str | None = Field(default=None, max_length=200)
    approved_at: datetime | None = None
    approved_on: date | None = None
    internal_note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def coherent(self):
        kinds = {
            "profile": {"profile_content", "publication"},
            "portrait": {"portrait_asset"},
            "qualification": {"qualification"},
            "family": {"offering_content", "protected_source"},
            "offering": {"offering_content", "protected_source"},
        }
        if self.kind not in kinds[self.subject_type]:
            raise ValueError("wrong evidence kind for subject")
        if self.status == "approved" and not self.evidence_reference:
            raise ValueError("approved evidence requires an explicit reference")
        if self.kind == "protected_source" and self.scope != "protected_source_content":
            raise ValueError(
                "protected source consent is not short public copy consent"
            )
        if self.kind != "protected_source" and self.scope == "protected_source_content":
            raise ValueError("wrong scope")
        if (
            self.scope == "internal_verification"
            and self.subject_type != "qualification"
        ):
            raise ValueError("internal verification is qualification-only")
        if self.approved_at and (
            self.approved_at.tzinfo is None or self.approved_on is not None
        ):
            raise ValueError("explicit timestamp timezone or day-only date required")
        if self.approved_at:
            object.__setattr__(self, "approved_at", self.approved_at.astimezone(UTC))
        return self


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def subjects(content, topics=()):
    """Server-calculated exact revision subjects; keys never become public UUIDs."""
    if content.target_version == 0:
        return {}
    result = {}
    result[("profile", "profile")] = digest(
        {
            "content": content.model_dump(mode="json"),
            "topics": [
                {"id": str(t.id), "name": t.name, "categories": sorted(t.categories)}
                for t in sorted(topics, key=lambda t: str(t.id))
            ],
        }
    )
    for asset in content.assets:
        result[("portrait", "portrait")] = digest(asset.model_dump(mode="json"))
    for value in content.qualifications:
        result[("qualification", value.key)] = digest(value.model_dump(mode="json"))
    for family in content.offering_families:
        result[("family", family.key)] = digest(
            {
                "family": family.model_dump(mode="json"),
                "formats": [
                    o.model_dump(mode="json")
                    for o in sorted(content.offerings, key=lambda o: o.ordering)
                    if o.family_key == family.key
                ],
            }
        )
    for offer in content.offerings:
        result[("offering", offer.key)] = digest(offer.model_dump(mode="json"))
    return result


def requirements(content):
    if content.target_version == 0:
        return set()
    result = {
        ("profile", "profile", "profile_content"),
        ("profile", "profile", "publication"),
    }
    if any(a.active for a in content.assets):
        result.add(("portrait", "portrait", "portrait_asset"))
    result.update(
        ("qualification", q.key, "qualification")
        for q in content.qualifications
        if q.public and q.status == "active"
    )
    public_families = {
        f.key
        for f in content.offering_families
        if f.active
        and any(o.active and o.family_key == f.key for o in content.offerings)
    }
    result.update(("family", key, "offering_content") for key in public_families)
    result.update(
        ("offering", o.key, "offering_content")
        for o in content.offerings
        if o.active and (not o.family_key or o.family_key in public_families)
    )
    return result


def evidence_ready(revision, environment):
    hashes = subjects(revision.content, revision.topics)
    for kind, key, evidence_kind in requirements(revision.content):
        matches = [
            e
            for e in revision.object_evidence
            if (
                e.value.subject_type,
                e.value.subject_key,
                e.value.kind,
                e.value.environment,
                e.value.scope,
            )
            == (kind, key, evidence_kind, environment, "public_content")
        ]
        if (
            not matches
            or matches[-1].value.status != "approved"
            or matches[-1].value.subject_hash != hashes.get((kind, key))
        ):
            return False
    return True


def public_boundary(value):
    return {"text": value.text, "excluded_services": list(value.excluded_services)}


def public_variant(value):
    return {
        "kind": value.kind,
        "title": value.title,
        "description": value.description,
        "duration": (
            value.duration.model_dump(mode="json", exclude_none=True)
            if value.duration
            else None
        ),
    }


def public_target(content, environment):
    """Build positive public fields; never serialize an Admin model wholesale."""
    result = {
        "roles": [
            {"code": r.code, "label": r.display_label}
            for r in sorted(content.public_roles, key=lambda v: (v.ordering, v.key))
        ],
        "qualifications": [
            {
                "label": q.public_display_label,
                "issuer": q.issuer,
                "type": q.qualification_type,
            }
            for q in sorted(content.qualifications, key=lambda v: (v.ordering, v.key))
            if q.public and q.status == "active"
        ],
        "boundaries": [public_boundary(b) for b in content.boundaries],
    }
    if content.presentation:
        p = content.presentation
        result["presentation"] = {
            "teaser": p.teaser,
            "focus_labels": list(p.focus_labels),
            "background_labels": list(p.background_labels),
            "languages": list(p.languages),
            "sections": [
                {
                    "kind": s.kind,
                    "headings": list(s.headings),
                    "paragraphs": list(s.paragraphs),
                }
                for s in p.sections
            ],
            "topic_cards": [{"title": c.title, "text": c.text} for c in p.topic_cards],
            "quote": p.quote,
            "external_links": [
                {"label": v.label, "url": getattr(v, environment + "_url")}
                for v in p.external_links
                if getattr(v, environment + "_url")
            ],
            "initials": p.initials,
            "portrait_width": p.portrait_width,
            "portrait_height": p.portrait_height,
        }
    families = []
    for family in sorted(content.offering_families, key=lambda v: (v.ordering, v.key)):
        formats = [
            public_offering(o)
            for o in sorted(content.offerings, key=lambda v: v.ordering)
            if o.family_key == family.key and o.active
        ]
        if not family.active or not formats:
            continue
        families.append(
            {
                "title": family.title,
                "description": family.description,
                "target_groups": list(family.target_groups),
                "target_focus": list(family.target_focus),
                "service_domains": list(family.service_domains),
                "boundaries": [public_boundary(b) for b in family.boundaries],
                "variants": [
                    public_variant(v)
                    for v in sorted(family.variants, key=lambda v: (v.ordering, v.key))
                    if v.active
                ],
                "formats": formats,
            }
        )
    result["offering_families"] = families
    return result


def public_offering(offer):
    return {
        "title": offer.title,
        "type": offer.type,
        "description": offer.description,
        "ordering": offer.ordering,
        "service_domains": list(offer.service_domains),
        "bookable": offer.bookable,
        "duration": (
            offer.duration.model_dump(mode="json", exclude_none=True)
            if offer.duration
            else None
        ),
        "delivery_mode": offer.delivery_mode,
        "delivery_label": offer.delivery_label,
        "target_groups": list(offer.target_groups),
        "target_focus": list(offer.target_focus),
        "program_modules": list(offer.program_modules),
        "boundaries": [public_boundary(b) for b in offer.boundaries],
        "variants": [
            public_variant(v)
            for v in sorted(offer.variants, key=lambda v: (v.ordering, v.key))
            if v.active
        ],
    }
