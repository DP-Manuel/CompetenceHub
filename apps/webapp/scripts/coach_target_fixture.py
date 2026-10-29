"""Synthetic COACH-3C only, on a parent-owned fresh schema0009 at loopback55436.

No migrations, database reset, source files, real identities or server lifecycle.
The parent must replace its disposable database before running browser acceptance
after a unit-PG test. Native password/MFA/runtime behavior comes from COACH-2.
"""

from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine

from coach_management_fixture import LocalCoachManagementFixture
from coach_target_cases import three_family_profile
from competence_hub_api.portal.coach_registry import (
    CoachRegistryService,
    ProfileContent,
    public_projection,
)
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)


def target_content(topic_ids):
    """Fixed synthetic markers make lost fields and private projection leaks visible."""
    return ProfileContent.model_validate(
        {
            "target_version": 1,
            "display_name": "Coach Target Alpha",
            "short_intro": "Synthetic target profile, not a real person",
            "profile_path": "/coaches/target-alpha/",
            "topic_ids": list(topic_ids),
            "competencies": ["Synthetic communication"],
            "public_roles": [
                {
                    "key": "role-trainer",
                    "code": "trainer",
                    "display_label": "Synthetic Trainer",
                }
            ],
            "qualifications": [
                {
                    "key": "qualification-public",
                    "canonical_title": "INTERNAL_CANONICAL_TITLE",
                    "public_display_label": "Synthetic public certificate",
                    "public": True,
                    "issuer": "Synthetic Institute",
                    "qualification_type": "certificate",
                    "verification_state": "source_asserted",
                    "evidence_reference": "synthetic:qualification",
                    "internal_note": "INTERNAL_QUALIFICATION_NOTE",
                },
                {
                    "key": "qualification-private",
                    "canonical_title": "INTERNAL_PRIVATE_QUALIFICATION",
                    "ordering": 1,
                    "verification_state": "unknown",
                    "public": False,
                },
            ],
            "presentation": {
                "teaser": "Synthetic teaser",
                "languages": ["Deutsch"],
                "focus_labels": ["Synthetic focus"],
                "sections": [
                    {
                        "key": "background",
                        "kind": "background",
                        "paragraphs": ["Synthetic background paragraph"],
                    }
                ],
            },
            "boundaries": [
                {
                    "key": "profile-boundary",
                    "text": "Synthetic training is not therapy",
                    "excluded_services": ["psychotherapy"],
                }
            ],
            "offering_families": [
                {
                    "key": "family-communication",
                    "title": "Synthetic communication family",
                    "description": "Synthetic family copy",
                    "service_domains": ["training"],
                    "target_groups": ["Synthetic teams"],
                    "target_focus": ["Synthetic cooperation"],
                    "protected_source_reference": "synthetic:PROTECTED_FAMILY_SOURCE",
                    "boundaries": [
                        {"key": "family-boundary", "text": "No clinical treatment"}
                    ],
                    "variants": [
                        {
                            "key": "family-option",
                            "kind": "option",
                            "title": "Synthetic family option",
                        }
                    ],
                }
            ],
            "offerings": [
                {
                    "key": "format-workshop",
                    "family_key": "family-communication",
                    "title": "Synthetic workshop format",
                    "type": "workshop",
                    "description": "Synthetic format copy",
                    "service_domains": ["training"],
                    "duration": {
                        "clock_start": "09:00",
                        "clock_end": "12:00",
                        "minutes": 180,
                    },
                    "delivery_mode": "online_or_in_person",
                    "delivery_label": "Synthetic delivery",
                    "target_groups": ["Synthetic teams"],
                    "target_focus": ["Synthetic focus"],
                    "program_modules": ["Synthetic introduction", "Synthetic practice"],
                    "protected_source_reference": "synthetic:PROTECTED_FORMAT_SOURCE",
                    "boundaries": [
                        {"key": "format-boundary", "text": "Synthetic format boundary"}
                    ],
                    "variants": [
                        {
                            "key": "format-addon",
                            "kind": "add_on",
                            "title": "Synthetic follow-up",
                            "duration": {"minutes": 30},
                        }
                    ],
                }
            ],
        }
    )


class LocalCoachTargetFixture(LocalCoachManagementFixture):
    _DATABASE_ENV = "COMPETENCE_HUB_COACH_TARGET_LOCAL_DATABASE_URL"
    _OWNER_ENV = "COMPETENCE_HUB_COACH_TARGET_LOCAL_OWNER_URL"
    _DATABASE_PORT = 55436
    _MIGRATIONS = tuple(f"000{i}" for i in range(1, 10))
    _EMPTY_TABLES = LocalCoachManagementFixture._EMPTY_TABLES + (
        "services",
        "coach_services",
        "coaching_requests",
        "request_topics",
        "request_services",
        "topic_category_assignments",
        "coach_profile_revisions",
        "coach_profile_labels",
        "coach_profile_topics",
        "coach_profile_topic_categories",
        "coach_offerings",
        "coach_assets",
        "coach_profile_approvals",
        "coach_publications",
        "coach_import_sources",
        "coach_import_items",
        "coach_import_evidence",
        "coach_public_roles",
        "coach_qualifications",
        "coach_offering_families",
        "coach_object_evidence",
    )

    def seed_states(self):
        async def seed(_connection):
            engine = create_async_engine(self.app_url, hide_parameters=True)
            service = CoachRegistryService(PostgresCoachRegistryRepository(engine))
            try:
                for name, content in (
                    ("Alpha", target_content(self.topics)),
                    (
                        "Legacy",
                        ProfileContent(
                            display_name="Coach Target Legacy",
                            short_intro="Synthetic legacy profile",
                            profile_path="/coaches/target-legacy/",
                            topic_ids=tuple(self.topics),
                        ),
                    ),
                    ("Epsilon", three_family_profile()),
                ):
                    coach = await service.create(
                        actor=self.actor,
                        display_name=content.display_name,
                        request_id=uuid4(),
                        now=self.now,
                    )
                    self.ids[name] = coach.id
                    await service.mutate(
                        actor=self.actor,
                        coach_id=coach.id,
                        expected_version=coach.version,
                        operation="revision",
                        content=content,
                        now=self.now,
                    )
            finally:
                await engine.dispose()

        self.database(seed)

    def projection(self):
        async def read(_connection):
            engine = create_async_engine(self.app_url, hide_parameters=True)
            try:
                repository = PostgresCoachRegistryRepository(engine)
                coaches = tuple(
                    [await repository.get(coach_id) for coach_id in self.ids.values()]
                )
                return (
                    public_projection(coaches, "preview"),
                    public_projection(coaches, "production"),
                )
            finally:
                await engine.dispose()

        return self.inspect(read)
