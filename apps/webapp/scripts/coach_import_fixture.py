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


def target_fixture():
    """Fixed Alpha-Epsilon v2 data for the separate schema9/55436 proof."""
    from competence_hub_api.portal.coach_import import validate_records
    from competence_hub_api.portal.coach_target import requirements, subjects

    records, old_mapping, catalogue, assets = fixture()
    mapping = ImportMappingContract(
        version="coach-import-v2",
        topics=old_mapping.topics,
        review_ref="synthetic:review-3c",
        attest_initial_publication=True,
    )
    alpha_publication = records[0].pop("publication")
    for record in records:
        record["source_identity"]["source_system"] = "synthetic-coach3c"
        record["profile"]["target_version"] = 1
        for i, role in enumerate(record.get("roles", [])):
            record["roles"][i] = {
                "key": role["key"],
                "code": role["key"],
                "display_label": role["text"],
                "ordering": i,
            }
        for i, qualification in enumerate(record.get("qualifications", [])):
            record["qualifications"][i] = {
                "key": qualification["key"],
                "canonical_title": qualification["text"],
                "public_display_label": qualification["text"],
                "public": True,
                "ordering": i,
                "verification_state": "source_asserted",
                "evidence_reference": "synthetic:qualification",
            }
        for offer in record.get("offerings", []):
            offer["content"]["key"] = offer["key"]
    records[2]["offerings"][0]["content"]["service_domains"] = ["psychotherapy"]
    records.append(
        {
            "source_identity": {
                "source_system": "synthetic-coach3c",
                "source_key": "coach/epsilon",
            },
            "profile": {
                "target_version": 1,
                "display_name": "Synthetic Coach Epsilon",
                "short_intro": "Synthetic rich target.",
                "profile_path": "/coaches/synthetic-epsilon/",
            },
            "roles": [
                {
                    "key": "trainer",
                    "code": "trainer",
                    "display_label": "Synthetic Trainer",
                }
            ],
            "qualifications": [
                {
                    "key": "degree",
                    "canonical_title": "Synthetic degree",
                    "public_display_label": "Synthetic degree",
                    "public": True,
                    "ordering": 0,
                },
                {
                    "key": "private",
                    "canonical_title": "Synthetic internal verification",
                    "public": False,
                    "internal_note": "Synthetic private note",
                    "ordering": 1,
                },
            ],
            "offering_families": [
                {
                    "key": "balance",
                    "title": "Synthetic balance family",
                    "service_domains": ["training", "coaching"],
                    "target_groups": ["Synthetic teams"],
                    "target_focus": ["Synthetic focus"],
                    "boundaries": [
                        {
                            "key": "scope",
                            "text": "Synthetic development, no therapy.",
                            "excluded_services": ["therapy", "medical_treatment"],
                        }
                    ],
                    "variants": [
                        {
                            "key": "community",
                            "kind": "add_on",
                            "title": "Synthetic community",
                        }
                    ],
                    "protected_source_reference": "synthetic:protected-concept",
                }
            ],
            "offerings": [
                {
                    "key": "balance/day",
                    "content": {
                        "key": "balance/day",
                        "family_key": "balance",
                        "title": "Synthetic day",
                        "type": "workshop",
                        "ordering": 0,
                        "service_domains": ["training"],
                        "duration": {"clock_start": "10:00", "clock_end": "16:30"},
                        "bookable": False,
                        "delivery_mode": "in_person",
                        "delivery_label": "Synthetic location",
                        "target_groups": ["Synthetic teams"],
                        "variants": [
                            {
                                "key": "practice",
                                "kind": "option",
                                "title": "Synthetic practice",
                            }
                        ],
                    },
                },
                {
                    "key": "balance/six-weeks",
                    "content": {
                        "key": "balance/six-weeks",
                        "family_key": "balance",
                        "title": "Synthetic six-week format",
                        "type": "coaching",
                        "ordering": 1,
                        "service_domains": ["coaching"],
                        "duration": {
                            "weeks": 6,
                            "sessions_per_week": 1,
                            "session_minutes": 60,
                        },
                        "delivery_mode": "live_unspecified",
                        "delivery_label": "Synthetic online or live, location unresolved",
                        "program_modules": [
                            "Synthetic module one",
                            "Synthetic module two",
                        ],
                        "protected_source_reference": "synthetic:protected-format",
                    },
                },
            ],
            "presentation": {
                "teaser": "Synthetic teaser",
                "focus_labels": ["Synthetic focus"],
                "languages": ["Synthetic language"],
                "sections": [
                    {
                        "key": "profile",
                        "kind": "profile",
                        "headings": ["Synthetic heading"],
                        "paragraphs": ["Synthetic paragraph"],
                    }
                ],
                "quote": "Synthetic quote",
                "external_links": [
                    {
                        "key": "website",
                        "label": "Synthetic website",
                        "preview_url": "https://example.invalid/preview",
                        "production_url": "https://example.invalid/production",
                    }
                ],
            },
            "boundaries": [{"key": "scope", "text": "Synthetic service boundary."}],
            "provenance": {"source_ref": "synthetic:fixture/epsilon"},
        }
    )
    prepared = validate_records(records, mapping, catalogue, assets, now=NOW)
    assert not prepared.issues
    for index in (0, 4):
        content = prepared.records[index].content
        hashes = subjects(content, [catalogue[t] for t in content.topic_ids])
        records[index]["object_evidence"] = [
            {
                "key": f"preview/{kind}/{key}/{evidence_kind}",
                "subject_type": kind,
                "subject_key": key,
                "subject_hash": hashes[(kind, key)],
                "kind": evidence_kind,
                "environment": "preview",
                "status": "approved",
                "evidence_reference": "synthetic:explicit-public-copy",
                "approved_by": "Synthetic reviewer",
            }
            for kind, key, evidence_kind in sorted(requirements(content))
        ]
    epsilon = prepared.records[4].content
    records[4]["object_evidence"].append(
        {
            "key": "protected/balance",
            "subject_type": "family",
            "subject_key": "balance",
            "subject_hash": subjects(epsilon)[("family", "balance")],
            "kind": "protected_source",
            "environment": "preview",
            "scope": "protected_source_content",
            "status": "unknown",
        }
    )
    records[0]["publication"] = alpha_publication
    return records, mapping, catalogue, assets
