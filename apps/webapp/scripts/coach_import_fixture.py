"""Bundled synthetic COACH-3A inputs. Never loads website content or source folders."""

from datetime import UTC, datetime
import base64
import hashlib
from types import SimpleNamespace
from uuid import UUID

from competence_hub_api.portal.coach_import import ImportMappingContract, TopicRule
from competence_hub_api.portal.coach_registry import TopicSnapshot

NOW = datetime(2026, 10, 23, 12, tzinfo=UTC)
ACTOR = SimpleNamespace(
    user_id=UUID("00000000-0000-4000-8000-0000000003a0"), roles=("admin",)
)
CATEGORIES = ("personalentwicklung", "persoenlichkeitsentwicklung", "karrierecoaching")
ASSET_REF = "images/coaches/synthetic-alpha-v1.png"
# One synthetic pixel, not a person's photograph or a source-directory asset.
ASSET_BYTES = {
    ASSET_REF: base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l9sAAAAASUVORK5CYII="
    )
}


def fixture():
    names = (
        "Synthetic Leadership",
        "Stressmanagement",
        "Synthetic Communication",
        "Synthetic Career",
        "Synthetic Reflection",
        "Synthetic Team",
        "Synthetic Change",
        "Synthetic Learning",
    )
    catalogue = {}
    rules = []
    for i, name in enumerate(names):
        topic_id = UUID(f"00000000-0000-4000-8000-{i+1:012d}")
        categories = CATEGORIES if i < 2 else CATEGORIES[:2]
        catalogue[topic_id] = TopicSnapshot(topic_id, name, categories)
        rules.append(
            TopicRule(
                reference=f"topic-{i+1}",
                topic_id=topic_id,
                accepted_labels=(name, "Stress Management") if i == 1 else (name,),
                categories=categories,
            )
        )
    mapping = ImportMappingContract(
        topics=tuple(rules),
        role_mapping="literal_background_v1",
        qualification_mapping="literal_background_v1",
        boundary_mapping="literal_description_v1",
        review_ref="synthetic:review-3a",
        attest_initial_publication=True,
    )
    records = []
    for i, label in enumerate(("Alpha", "Beta", "Gamma", "Delta")):
        records.append(
            {
                "source_identity": {
                    "source_system": "synthetic-coach3a",
                    "source_key": f"coach/{label.lower()}",
                },
                "profile": {
                    "display_name": f"Synthetic Coach {label}",
                    "short_intro": "Synthetic introduction.",
                    "profile_path": f"/coaches/synthetic-{label.lower()}/",
                },
                "topics": [{"reference": f"topic-{i+1}", "label": names[i]}],
                "provenance": {"source_ref": f"synthetic:fixture/{label.lower()}"},
            }
        )
    records[0].update(
        {
            "topics": [
                {"reference": f"topic-{i+1}", "label": names[i]} for i in range(3)
            ],
            "competencies": [
                {"key": "listening", "text": "Synthetic active listening"},
                {"key": "facilitation", "text": "Synthetic facilitation"},
            ],
            "target_groups": [{"key": "teams", "text": "Synthetic teams"}],
            "offerings": [
                {
                    "key": "workshop",
                    "content": {
                        "title": "Synthetic workshop",
                        "type": "workshop",
                        "ordering": 0,
                    },
                },
                {
                    "key": "lecture",
                    "content": {
                        "title": "Synthetic lecture",
                        "type": "lecture",
                        "ordering": 1,
                    },
                },
            ],
            "assets": [
                {
                    "key": "portrait",
                    "content": {
                        "reference": ASSET_REF,
                        "sha256": hashlib.sha256(ASSET_BYTES[ASSET_REF]).hexdigest(),
                        "alt_text": "Synthetic placeholder",
                    },
                }
            ],
            "publication": {
                "lifecycle": "active",
                "published": ["preview"],
                "evidence": [
                    {
                        "key": "content",
                        "kind": "content_review",
                        "source": "synthetic:review",
                        "historical_at": "2026-01-01T00:00:00Z",
                    },
                    {
                        "key": "consent",
                        "kind": "person_consent",
                        "source": "synthetic:consent",
                    },
                    {
                        "key": "preview",
                        "kind": "preview",
                        "environment": "preview",
                        "source": "synthetic:preview",
                    },
                ],
            },
        }
    )
    records[2]["boundaries"] = [
        {
            "key": "scope",
            "text": "Synthetic coaching is not synthetic psychotherapy. Neither is a real treatment offer.",
        }
    ]
    records[2]["offerings"] = [
        {
            "key": "boundary-example",
            "content": {
                "title": "Synthetic therapy boundary example, not bookable",
                "type": "other",
                "active": False,
            },
        }
    ]
    records[3]["roles"] = [
        {"key": "coach", "text": "Synthetic Coach"},
        {"key": "moderator", "text": "Synthetic Moderator"},
    ]
    records[3]["qualifications"] = [
        {"key": "one", "text": "Synthetic qualification A"},
        {"key": "two", "text": "Synthetic qualification B"},
    ]
    return records, mapping, catalogue, dict(ASSET_BYTES)
