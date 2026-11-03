"""In-memory synthetic Registry cases. Not a DB fixture or real consent."""

from base64 import b64decode
from datetime import UTC, datetime
from hashlib import sha256
from uuid import UUID

from competence_hub_api.portal.coach_registry import (
    Approval,
    Asset,
    CoachAggregate,
    ObjectEvidence,
    ProfileRevision,
    Publication,
    TopicSnapshot,
)
from scripts.coach_target_cases import approvals_for, target_profile

NOW = datetime(2026, 11, 2, tzinfo=UTC)
ACTOR = UUID(int=90)
PORTRAIT = b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="
)
ASSET_REFERENCE = "images/coaches/synthetic-alpha.png"


def synthetic_registry():
    result = []
    for index, (name, environments) in enumerate(
        (
            ("Alpha", ("preview", "production")),
            ("Beta", ("preview",)),
            ("Unknown", ()),
            ("Inactive", ("preview", "production")),
        ),
        1,
    ):
        content = target_profile(
            name,
            description="Synthetic public profile. No real person.",
            competencies=("Synthetic facilitation",),
            topic_ids=(UUID(int=40),),
        )
        if index == 1:
            content = content.model_copy(
                update={
                    "assets": (
                        Asset(
                            reference=ASSET_REFERENCE,
                            sha256=sha256(PORTRAIT).hexdigest(),
                            alt_text="Synthetic fixture portrait",
                            scopes=("preview", "production"),
                        ),
                    )
                }
            )
        revision = ProfileRevision(
            UUID(int=100 + index),
            1,
            content,
            ACTOR,
            NOW,
            status="submitted",
            topics=(
                TopicSnapshot(
                    UUID(int=40),
                    "Synthetic communication",
                    ("personalentwicklung", "karrierecoaching"),
                ),
            ),
        )
        for environment in environments:
            revision.object_evidence.extend(
                ObjectEvidence(
                    UUID(
                        int=1000
                        + index * 100
                        + j
                        + (50 if environment == "production" else 0)
                    ),
                    e,
                    ACTOR,
                    NOW,
                )
                for j, e in enumerate(
                    approvals_for(revision, environment, prefix=environment)
                )
            )
        revision.approvals = [
            Approval(kind, ACTOR, NOW, "synthetic:approval")
            for kind in ("content_review", "person_consent", *environments)
        ]
        coach = CoachAggregate(
            UUID(int=index),
            content.display_name,
            UUID(int=200 + index),
            lifecycle="inactive" if name == "Inactive" else "active",
            revisions=[revision],
            publications={
                e: Publication(revision.id, "published", ACTOR, NOW)
                for e in environments
            },
        )
        result.append(coach)
    return tuple(result)
