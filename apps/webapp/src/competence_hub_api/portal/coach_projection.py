"""Offline COACH-4 export/review boundary. No database or transport dependency."""

import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    model_validator,
)

from .coach_registry import Asset, CATEGORIES, Environment, public_projection
from .coach_profiles import validate_public_profile_path
from .coach_target import Domain, Duration, PublicLink

MAX_ARTIFACT_BYTES = 8 * 1024 * 1024


class PublicValue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class PublicBoundary(PublicValue):
    text: str
    excluded_services: list[str]


class PublicVariant(PublicValue):
    kind: Literal["variant", "add_on", "option"]
    title: str
    description: str | None
    duration: Duration | None


class PublicOffering(PublicValue):
    title: str
    type: Literal["lecture", "workshop", "coaching", "individual", "other"]
    description: str | None
    ordering: StrictInt
    service_domains: list[Domain] = Field(default_factory=list)
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
    delivery_label: str | None = None
    target_groups: list[str] = Field(default_factory=list)
    target_focus: list[str] = Field(default_factory=list)
    program_modules: list[str] = Field(default_factory=list)
    boundaries: list[PublicBoundary] = Field(default_factory=list)
    variants: list[PublicVariant] = Field(default_factory=list)

    @model_validator(mode="after")
    def separate_therapy(self):
        if "psychotherapy" in self.service_domains and (
            self.bookable
            or self.type == "coaching"
            or "coaching" in self.service_domains
        ):
            raise ValueError("therapy must remain separate and nonbookable")
        return self


class PublicFamily(PublicValue):
    title: str
    description: str | None
    target_groups: list[str]
    target_focus: list[str]
    service_domains: list[Domain]
    boundaries: list[PublicBoundary]
    variants: list[PublicVariant]
    formats: list[PublicOffering]


class PublicAsset(PublicValue):
    type: Literal["portrait"]
    reference: str
    sha256: str
    alt_text: str

    @model_validator(mode="after")
    def safe_file(self):
        Asset.model_validate(self.model_dump())
        return self


class PublicTopic(PublicValue):
    name: str
    categories: list[str]

    @model_validator(mode="after")
    def allowed_categories(self):
        if not set(self.categories) <= CATEGORIES:
            raise ValueError("unknown category")
        return self


class PublicQualification(PublicValue):
    label: str
    issuer: str | None
    type: str | None


class PublicRole(PublicValue):
    code: str
    label: str


class PublicSection(PublicValue):
    kind: Literal[
        "profile", "topics", "background", "formats", "boundary", "contact", "pending"
    ]
    headings: list[str]
    paragraphs: list[str]


class PublicCard(PublicValue):
    title: str
    text: str


class PublicExternalLink(PublicValue):
    label: str
    url: str

    @model_validator(mode="after")
    def safe_url(self):
        PublicLink(key="public-link", label=self.label, preview_url=self.url)
        return self


class PublicPresentation(PublicValue):
    teaser: str | None
    focus_labels: list[str]
    background_labels: list[str]
    languages: list[str]
    sections: list[PublicSection]
    topic_cards: list[PublicCard]
    quote: str | None
    external_links: list[PublicExternalLink]
    initials: str | None
    portrait_width: StrictInt | None
    portrait_height: StrictInt | None


class PublicCoach(PublicValue):
    display_name: str
    academic_suffix: str | None
    short_intro: str
    description: str | None
    professional_background: str | None
    target_groups: list[str]
    profile_path: str
    competencies: list[str]
    topics: list[PublicTopic]
    assets: list[PublicAsset] = Field(max_length=1)
    offerings: list[PublicOffering]
    roles: list[PublicRole] = Field(default_factory=list)
    qualifications: list[PublicQualification] = Field(default_factory=list)
    boundaries: list[PublicBoundary] = Field(default_factory=list)
    offering_families: list[PublicFamily] = Field(default_factory=list)
    presentation: PublicPresentation | None = None

    @model_validator(mode="after")
    def safe_route(self):
        if validate_public_profile_path(self.profile_path) != self.profile_path:
            raise ValueError("exact canonical route required")
        return self


class Projection(PublicValue):
    schema_version: Literal[1] = Field(alias="schema")
    environment: Environment
    coaches: list[PublicCoach] = Field(max_length=500)

    @model_validator(mode="after")
    def unique_paths(self):
        paths = [c.profile_path for c in self.coaches]
        if len(paths) != len(set(paths)):
            raise ValueError("duplicate public routes")
        return self


def validate_projection(value, environment=None):
    """Reject unknown fields at every level, never silently strip leaked fields."""
    if not isinstance(value, dict) or type(value.get("schema")) is not int:
        raise ValueError("integer schema required")
    Projection.model_validate(value)
    rich_fields = {"roles", "qualifications", "boundaries", "offering_families"}
    for coach in value["coaches"]:
        if rich_fields.intersection(coach) and not rich_fields.issubset(coach):
            raise ValueError("complete public rich projection required")
        if "presentation" in coach and (
            not rich_fields.issubset(coach) or coach["presentation"] is None
        ):
            raise ValueError("public presentation requires rich projection")
    if environment is not None and value["environment"] != environment:
        raise ValueError("projection environment mismatch")
    return value


def canonical_bytes(value):
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def checked_local_path(path, *, root=None):
    """Check lexical containment and every existing ancestor before any I/O.

    resolve() alone hides junctions/symlinks. Missing output descendants are
    valid, but their existing parents must not redirect a later mkdir/write.
    """
    path = Path(os.path.abspath(path))
    if str(path).startswith("\\\\"):
        raise ValueError("network paths forbidden")
    if root is not None:
        root = Path(os.path.abspath(root))
        if path == root or not path.is_relative_to(root):
            raise ValueError("outside explicit local workspace")
    for ancestor in (path, *path.parents):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            continue
        if (
            stat.S_ISLNK(info.st_mode)
            or getattr(info, "st_file_attributes", 0)
            & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise ValueError("linked/reparse paths forbidden")
    return path


def generate_projection(coaches, environment):
    """In-process registry seam, not a public API or an arbitrary Admin JSON dump."""
    value = public_projection(tuple(coaches), environment)
    # Category/topic order is not editorial. Array order of offerings/roles IS.
    for coach in value["coaches"]:
        for topic in coach["topics"]:
            topic["categories"].sort()
        coach["topics"].sort(key=lambda t: (t["name"], t["categories"]))
    return validate_projection(value, environment)


def verify_assets(value, asset_root):
    """Exact reviewed bytes in an explicit local public-only asset tree."""
    validate_projection(value)
    root = checked_local_path(asset_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("asset root must be a directory")
    hashes = {}
    for coach in value["coaches"]:
        for asset in coach["assets"]:
            reference = asset["reference"]
            current = root
            for part in Path(reference).parts:
                current = current / part
                if (
                    current.is_symlink()
                    or getattr(current.stat(), "st_file_attributes", 0)
                    & stat.FILE_ATTRIBUTE_REPARSE_POINT
                ):
                    raise ValueError("asset links forbidden")
            path = current.resolve(strict=True)
            if (
                not path.is_relative_to(root)
                or not path.is_file()
                or path.stat().st_size > 20 * 1024 * 1024
            ):
                raise ValueError("invalid local public asset")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != asset["sha256"] or (
                reference in hashes and hashes[reference] != digest
            ):
                raise ValueError("asset hash mismatch")
            hashes[reference] = digest
    return hashes


def write_projection(value, output, *, asset_root):
    """Exclusive creation; cannot overwrite a frozen/current artifact."""
    validate_projection(value)
    verify_assets(value, asset_root)
    data = canonical_bytes(value)
    if len(data) > MAX_ARTIFACT_BYTES:
        raise ValueError("projection too large")
    with checked_local_path(output).open("xb") as stream:
        stream.write(data)
    return hashlib.sha256(data).hexdigest()


def read_projection(path, environment=None):
    path = checked_local_path(path)
    if path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("projection too large")

    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate JSON key")
            value[key] = item
        return value

    return validate_projection(
        json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique),
        environment,
    )


def _offerings(coach):
    return {
        "standalone": coach["offerings"],
        "families": coach.get("offering_families", []),
    }


def _boundaries(coach):
    offers = [
        *coach["offerings"],
        *(o for f in coach.get("offering_families", []) for o in f["formats"]),
    ]
    return [
        coach.get("boundaries", []),
        *[f["boundaries"] for f in coach.get("offering_families", [])],
        *[o.get("boundaries", []) for o in offers],
    ]


def _therapy(coach):
    return [
        o
        for o in [
            *coach["offerings"],
            *(o for f in coach.get("offering_families", []) for o in f["formats"]),
        ]
        if "psychotherapy" in o.get("service_domains", [])
    ]


def projection_diff(current, candidate):
    """Public-only structured review. Route changes cannot infer person identity."""
    validate_projection(current)
    validate_projection(candidate, current["environment"])
    old = {c["profile_path"]: c for c in current["coaches"]}
    new = {c["profile_path"]: c for c in candidate["coaches"]}
    added, removed = sorted(new.keys() - old.keys()), sorted(old.keys() - new.keys())
    report = {
        "schema": 1,
        "environment": current["environment"],
        "current_sha256": hashlib.sha256(canonical_bytes(current)).hexdigest(),
        "candidate_sha256": hashlib.sha256(canonical_bytes(candidate)).hexdigest(),
        "added_coaches": added,
        "removed_coaches": removed,
        "changed_profiles": [],
        "changed_topics": [],
        "changed_offerings": [],
        "changed_assets": [],
        "changed_routes": bool(added or removed),
        "publication_state_changes": {
            "entered_projection": added,
            "left_projection": removed,
        },
        "high_attention": [],
    }

    def attention(code, route):
        report["high_attention"].append({"code": code, "route": route})

    for route in added:
        attention("NEW_COACH_OR_ROUTE", route)
    for route in removed:
        attention("REMOVED_COACH_OR_ROUTE", route)
    if current["environment"] == "production":
        for route in added + removed:
            attention("PRODUCTION_VISIBILITY_CHANGED_VERIFY_APPROVAL", route)
    for route in sorted(old.keys() & new.keys()):
        a, b = old[route], new[route]
        if a != b:
            report["changed_profiles"].append(route)
        for key, left, right in (
            ("changed_topics", a["topics"], b["topics"]),
            ("changed_offerings", _offerings(a), _offerings(b)),
            ("changed_assets", a["assets"], b["assets"]),
        ):
            if left != right:
                report[key].append(route)
        if a["assets"] != b["assets"]:
            attention("PORTRAIT_CHANGED", route)
        if _boundaries(a) != _boundaries(b):
            attention("OFFERING_BOUNDARY_CHANGED", route)
        if _therapy(a) != _therapy(b):
            attention("THERAPEUTIC_CONTENT_CHANGED", route)
    report["equal"] = current == candidate
    return report


PARITY_FIELDS = {
    "names": lambda c: (c["display_name"], c["academic_suffix"]),
    "topics": lambda c: c["topics"],
    "categories": lambda c: sorted({x for t in c["topics"] for x in t["categories"]}),
    "qualifications": lambda c: c.get("qualifications", []),
    "offerings": _offerings,
    "assets": lambda c: c["assets"],
    "boundaries": _boundaries,
}


def projection_parity(frozen, generated):
    """Compare all migration dimensions plus full public DTO, no fabricated PASS."""
    report = projection_diff(frozen, generated)
    old = {c["profile_path"]: c for c in frozen["coaches"]}
    new = {c["profile_path"]: c for c in generated["coaches"]}
    checks = {"coach_count": len(old) == len(new), "routes": old.keys() == new.keys()}
    for name, extract in PARITY_FIELDS.items():
        checks[name] = old.keys() == new.keys() and all(
            extract(old[p]) == extract(new[p]) for p in old.keys() & new.keys()
        )
    checks["full_public_dto"] = report["equal"]
    return {
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "DIFFERENT",
        "diff": report,
    }


def review_markdown(report):
    """No raw profiles/evidence dumped into the human review report."""
    lines = [
        "# Coach Projection Review",
        "",
        "Environment: " + report["environment"],
        "",
        "Current SHA-256: " + report["current_sha256"],
        "Candidate SHA-256: " + report["candidate_sha256"],
        "",
    ]
    for field in (
        "added_coaches",
        "removed_coaches",
        "changed_profiles",
        "changed_topics",
        "changed_offerings",
        "changed_assets",
    ):
        lines += [
            "## " + field.replace("_", " ").title(),
            *["- " + x for x in report[field]],
            "",
        ]
    lines += [
        "## High Attention",
        *["- " + a["code"] + ": " + a["route"] for a in report["high_attention"]],
        "",
        "A removed/added route is not an inferred UUID match. Review route redirects separately.",
        "Visibility is not approval metadata; exact Registry approval/evidence remains an operator gate.",
    ]
    return "\n".join(lines) + "\n"


def registry_safety_report(current, candidate):
    """Private operator comparison using stable UUIDs, never public artifact data.

    It reports approval changes even when a coach was/is unpublished. No evidence,
    internal identity, audit or source payload is serialized into the report.
    """
    from .coach_registry import publication_ready

    def state(coach):
        published = coach.publications.get("production")
        revision = (
            coach.revision(published.revision_id)
            if published
            else (coach.revisions[-1] if coach.revisions else None)
        )
        return {
            "route": revision.content.profile_path if revision else None,
            "production_ready": bool(
                revision and publication_ready(coach, revision, "production")
            ),
        }

    old = {c.id: state(c) for c in current}
    new = {c.id: state(c) for c in candidate}
    changes = []
    for identity in sorted(old.keys() | new.keys(), key=str):
        a, b = old.get(identity), new.get(identity)
        if a and b and a["route"] != b["route"]:
            changes.append(
                {
                    "code": "PUBLIC_PROFILE_PATH_CHANGED",
                    "previous": a["route"],
                    "candidate": b["route"],
                }
            )
        if bool(a and a["production_ready"]) != bool(b and b["production_ready"]):
            changes.append(
                {
                    "code": (
                        "PRODUCTION_APPROVAL_READY"
                        if b and b["production_ready"]
                        else "PRODUCTION_APPROVAL_LOST"
                    ),
                    "route": (b or a)["route"],
                }
            )
    return {
        "schema": 1,
        "scope": "PRIVATE_REVIEW_NOT_PUBLIC_ARTIFACT",
        "high_attention": changes,
    }
