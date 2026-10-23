from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import UTC, datetime
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from competence_hub_api.portal.coach_registry import (
    Asset,
    CoachAggregate,
    CoachRegistryService,
    Offering,
    ProfileContent,
    RegistryConflict,
    RegistryDenied,
    TopicSnapshot,
    public_projection,
)

NOW = datetime(2026, 10, 23, 10, tzinfo=UTC)
ACTOR = SimpleNamespace(user_id=uuid4(), roles=("admin",))
TOPIC_ID = uuid4()


@pytest.fixture
def anyio_backend():
    return "asyncio"


class MemoryRegistry:
    def __init__(self):
        self.items = {}
        self.catalogue = {
            TOPIC_ID: TopicSnapshot(
                TOPIC_ID,
                "Synthetic communication",
                ("personalentwicklung", "persoenlichkeitsentwicklung"),
            )
        }
        self.future = False
        self.audit = []

    async def create(self, *, display_name, request_id, actor_id, now):
        for item in self.items.values():
            if item.request_id == request_id:
                if item.display_name != display_name:
                    raise RegistryConflict("retry conflict")
                return deepcopy(item)
        item = CoachAggregate(uuid4(), display_name, request_id)
        self.items[item.id] = item
        self.audit.append(("coach_registry.create", actor_id, now, item.id))
        return deepcopy(item)

    async def get(self, coach_id):
        return deepcopy(self.items.get(coach_id))

    async def list_coaches(self, *, limit, offset):
        return tuple(deepcopy(list(self.items.values())[offset : offset + limit]))

    @asynccontextmanager
    async def edit(self, coach_id, expected_version):
        current = self.items.get(coach_id)
        if current is None:
            raise LookupError()
        if current.version != expected_version:
            raise RegistryConflict("stale")
        working = deepcopy(current)
        yield working
        self.audit.extend(working.events)
        working.events.clear()
        self.items[coach_id] = deepcopy(working)

    async def topics(self, ids):
        if any(id not in self.catalogue for id in ids):
            raise RegistryConflict("unknown topic")
        return tuple(self.catalogue[id] for id in ids)

    async def has_future_calendar(self, coach_id, now):
        return self.future


def profile(**changes):
    return ProfileContent(
        display_name="Synthetic Coach",
        short_intro="Synthetic public introduction",
        profile_path="/coaches/synthetic-coach/",
        topic_ids=(TOPIC_ID,),
        competencies=("Synthetic competence",),
        target_groups=("Synthetic teams",),
        offerings=(
            Offering(title="Synthetic workshop", type="workshop", ordering=0),
            Offering(title="Synthetic lecture", type="lecture", ordering=1),
            Offering(title="Synthetic individual", type="individual", ordering=2),
        ),
        **changes,
    )


async def change(service, coach, operation, **kwargs):
    return await service.mutate(
        actor=ACTOR,
        coach_id=coach.id,
        expected_version=coach.version,
        operation=operation,
        now=NOW,
        **kwargs,
    )


async def prepared(repository=None):
    repository = repository or MemoryRegistry()
    service = CoachRegistryService(repository)
    coach = await service.create(
        actor=ACTOR, display_name="Synthetic Coach", request_id=uuid4(), now=NOW
    )
    coach = await change(service, coach, "revision", content=profile())
    coach = await change(service, coach, "submit", revision_id=coach.revisions[-1].id)
    for kind in ("content_review", "person_consent", "preview"):
        coach = await change(
            service,
            coach,
            "approve",
            revision_id=coach.revisions[-1].id,
            kind=kind,
            evidence_ref="synthetic-evidence",
        )
    coach = await change(service, coach, "lifecycle", lifecycle="active")
    return service, coach


@pytest.mark.anyio
async def test_create_retry_duplicate_names_and_account_optional():
    repo = MemoryRegistry()
    service = CoachRegistryService(repo)
    request = uuid4()
    a = await service.create(
        actor=ACTOR, display_name="Synthetic", request_id=request, now=NOW
    )
    b = await service.create(
        actor=ACTOR, display_name="Synthetic", request_id=request, now=NOW
    )
    c = await service.create(
        actor=ACTOR, display_name="Synthetic", request_id=uuid4(), now=NOW
    )
    assert a.id == b.id != c.id
    assert a.lifecycle == "draft" and not a.publications
    assert not hasattr(a, "portal_user_id")
    with pytest.raises(RegistryConflict):
        await service.create(
            actor=ACTOR, display_name="Different", request_id=request, now=NOW
        )


@pytest.mark.anyio
async def test_draft_edit_submit_immutability_and_stale_mutation():
    service, coach = await prepared()
    with pytest.raises(RegistryConflict):
        await change(
            service,
            coach,
            "draft",
            revision_id=coach.revisions[-1].id,
            content=profile(),
        )
    with pytest.raises(RegistryConflict):
        await service.mutate(
            actor=ACTOR,
            coach_id=coach.id,
            expected_version=1,
            operation="revision",
            content=profile(),
            now=NOW,
        )
    coach = await change(
        service,
        coach,
        "revision",
        content=profile().model_copy(update={"display_name": "New name"}),
    )
    coach = await change(
        service, coach, "draft", revision_id=coach.revisions[-1].id, content=profile()
    )
    assert coach.revisions[-1].number == 2
    assert not coach.revisions[-1].approvals
    with pytest.raises(RegistryConflict):
        await change(service, coach, "revision", content=profile())


@pytest.mark.anyio
async def test_preview_production_separate_approvals_and_payload_free_export():
    service, coach = await prepared()
    assert public_projection((coach,), "preview")["coaches"] == []
    coach = await change(
        service,
        coach,
        "publish",
        revision_id=coach.revisions[-1].id,
        environment="preview",
    )
    projection = public_projection((coach,), "preview")
    assert len(projection["coaches"]) == 1
    assert public_projection((coach,), "production")["coaches"] == []
    assert len(projection["coaches"][0]["offerings"]) == 3
    assert len(projection["coaches"][0]["topics"][0]["categories"]) == 2
    assert all(
        secret not in json.dumps(projection)
        for secret in (
            str(coach.id),
            str(ACTOR.user_id),
            "synthetic-evidence",
            "actor_id",
            "evidence_ref",
            "topic_ids",
        )
    )
    with pytest.raises(RegistryConflict):
        await change(
            service,
            coach,
            "publish",
            revision_id=coach.revisions[-1].id,
            environment="production",
        )
    coach = await change(
        service,
        coach,
        "approve",
        revision_id=coach.revisions[-1].id,
        kind="production",
        evidence_ref="synthetic-prod-evidence",
    )
    coach = await change(
        service,
        coach,
        "publish",
        revision_id=coach.revisions[-1].id,
        environment="production",
    )
    coach = await change(service, coach, "withdraw", environment="production")
    with pytest.raises(RegistryConflict, match="newer"):
        await change(
            service,
            coach,
            "publish",
            revision_id=coach.revisions[-1].id,
            environment="production",
        )
    assert public_projection((coach,), "production")["coaches"] == []
    assert len(public_projection((coach,), "preview")["coaches"]) == 1


@pytest.mark.anyio
async def test_asset_scope_and_offering_changes_require_new_approval():
    service, coach = await prepared()
    asset = Asset(
        reference="images/coaches/synthetic.webp",
        sha256="a" * 64,
        alt_text="Synthetic portrait",
    )
    coach = await change(service, coach, "revision", content=profile(assets=(asset,)))
    coach = await change(service, coach, "submit", revision_id=coach.revisions[-1].id)
    for kind in ("content_review", "person_consent", "preview", "production"):
        coach = await change(
            service,
            coach,
            "approve",
            revision_id=coach.revisions[-1].id,
            kind=kind,
            evidence_ref="synthetic-scoped",
        )
    coach = await change(
        service,
        coach,
        "publish",
        revision_id=coach.revisions[-1].id,
        environment="preview",
    )
    with pytest.raises(RegistryConflict, match="asset"):
        await change(
            service,
            coach,
            "publish",
            revision_id=coach.revisions[-1].id,
            environment="production",
        )
    updated = profile().model_copy(
        update={"offerings": (Offering(title="New offer", type="coaching"),)}
    )
    coach = await change(service, coach, "revision", content=updated)
    assert not coach.revisions[-1].approvals
    exported = public_projection((coach,), "preview")["coaches"][0]
    assert len(exported["offerings"]) == 3  # Last approved snapshot remains unchanged.
    assert exported["assets"][0]["sha256"] == "a" * 64


@pytest.mark.anyio
async def test_legacy_coach_cannot_be_adopted_by_incidental_api_edit():
    repo = MemoryRegistry()
    coach = CoachAggregate(uuid4(), "Synthetic legacy", None)
    repo.items[coach.id] = coach
    with pytest.raises(RegistryConflict, match="adoption"):
        await change(CoachRegistryService(repo), coach, "revision", content=profile())


@pytest.mark.anyio
async def test_pause_retains_and_closes_pending_draft_before_reactivation():
    service, coach = await prepared()
    coach = await change(service, coach, "revision", content=profile())
    pending = coach.revisions[-1].id
    coach = await change(service, coach, "lifecycle", lifecycle="paused")
    assert coach.revision(pending).status == "abandoned"
    with pytest.raises(RegistryConflict):
        await change(service, coach, "draft", revision_id=pending, content=profile())
    coach = await change(service, coach, "revision", content=profile())
    assert coach.revisions[-1].number == 3 and coach.revisions[-1].status == "draft"
    assert coach.revisions[1].id == pending


@pytest.mark.parametrize("count", [8, 17])
def test_source_case_catalogue_shapes_without_importing_real_people(count):
    types = ("lecture", "workshop", "individual", "coaching")
    content = profile().model_copy(update={"offerings": ()}).model_dump()
    content["offerings"] = [
        Offering(
            title=f"Synthetic offering {index}",
            type=types[index % len(types)],
            ordering=index,
        )
        for index in range(count)
    ]
    assert len(ProfileContent.model_validate(content).offerings) == count


@pytest.mark.anyio
async def test_multiple_coaches_reuse_canonical_topics_and_many_to_many_categories():
    repo = MemoryRegistry()
    service, first = await prepared(repo)
    _, second = await prepared(repo)
    second_topic = uuid4()
    repo.catalogue[second_topic] = TopicSnapshot(
        second_topic, "Other synthetic topic", ("karrierecoaching",)
    )
    second = await change(
        service,
        second,
        "revision",
        content=profile().model_copy(update={"topic_ids": (TOPIC_ID, second_topic)}),
    )
    assert first.id != second.id
    assert first.revisions[0].topics[0].id == second.revisions[-1].topics[0].id
    assert len(second.revisions[-1].topics) == 2
    assert len(first.revisions[0].topics[0].categories) == 2
    assert len(repo.catalogue) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("state", ["paused", "inactive", "archived"])
async def test_offboard_and_reactivation_require_fresh_revision_same_uuid(state):
    service, coach = await prepared()
    identity = coach.id
    coach = await change(
        service,
        coach,
        "publish",
        revision_id=coach.revisions[-1].id,
        environment="preview",
    )
    coach = await change(service, coach, "lifecycle", lifecycle=state)
    assert coach.publications["preview"].state == "withdrawn"
    assert public_projection((coach,), "preview")["coaches"] == []
    if state == "archived":
        coach = await change(service, coach, "lifecycle", lifecycle="inactive")
    with pytest.raises(RegistryConflict):
        await change(service, coach, "lifecycle", lifecycle="active")
    coach = await change(
        service,
        coach,
        "revision",
        content=profile().model_copy(
            update={
                "display_name": "Returning name",
                "profile_path": "/coaches/returning-name/",
            }
        ),
    )
    coach = await change(service, coach, "submit", revision_id=coach.revisions[-1].id)
    for kind in ("content_review", "person_consent", "preview"):
        coach = await change(
            service,
            coach,
            "approve",
            revision_id=coach.revisions[-1].id,
            kind=kind,
            evidence_ref="new-evidence",
        )
    coach = await change(service, coach, "lifecycle", lifecycle="active")
    coach = await change(
        service,
        coach,
        "publish",
        revision_id=coach.revisions[-1].id,
        environment="preview",
    )
    assert coach.id == identity and len(coach.revisions) == 2
    assert coach.revisions[0].content.profile_path == "/coaches/synthetic-coach/"
    assert (
        public_projection((coach,), "preview")["coaches"][0]["display_name"]
        == "Returning name"
    )


@pytest.mark.anyio
async def test_offboard_calendar_conflict_is_atomic_and_audit_has_no_payload():
    service, coach = await prepared()
    service.repository.future = True
    with pytest.raises(RegistryConflict):
        await change(service, coach, "lifecycle", lifecycle="inactive")
    assert (await service.repository.get(coach.id)).lifecycle == "active"
    assert all(
        len(event) == 4 and event[0].startswith("coach_registry.")
        for event in service.repository.audit
    )


@pytest.mark.anyio
async def test_unknown_topic_and_duplicate_approval_fail_without_mutation():
    service, coach = await prepared()
    with pytest.raises(RegistryConflict):
        await change(
            service,
            coach,
            "revision",
            content=profile().model_copy(update={"topic_ids": (uuid4(),)}),
        )
    with pytest.raises(RegistryConflict):
        await change(
            service,
            coach,
            "approve",
            revision_id=coach.revisions[-1].id,
            kind="preview",
            evidence_ref="other",
        )
    assert (await service.repository.get(coach.id)).version == coach.version


@pytest.mark.anyio
@pytest.mark.parametrize(
    "roles",
    [("internal",), ("coach",), ("calendar_reviewer",), ("company_contact",), ()],
)
async def test_domain_admin_boundary(roles):
    service = CoachRegistryService(MemoryRegistry())
    with pytest.raises(RegistryDenied):
        await service.create(
            actor=SimpleNamespace(user_id=uuid4(), roles=roles),
            display_name="Synthetic",
            request_id=uuid4(),
            now=NOW,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("email", "private@example.invalid"),
        ("profile_path", "/coaches/../other/"),
        ("topic_ids", [TOPIC_ID, TOPIC_ID]),
        ("competencies", ["", "anything"]),
    ],
)
def test_strict_public_model_rejects_private_fields_and_bad_paths(field, value):
    data = profile().model_dump()
    data[field] = value
    with pytest.raises(ValidationError):
        ProfileContent.model_validate(data)


@pytest.mark.anyio
async def test_submitted_topic_snapshot_survives_topic_rename():
    service, coach = await prepared()
    service.repository.catalogue[TOPIC_ID] = TopicSnapshot(
        TOPIC_ID, "Renamed topic", ("karrierecoaching",)
    )
    coach = await change(
        service,
        coach,
        "publish",
        revision_id=coach.revisions[-1].id,
        environment="preview",
    )
    assert (
        public_projection((coach,), "preview")["coaches"][0]["topics"][0]["name"]
        == "Synthetic communication"
    )
    coach = await change(service, coach, "revision", content=profile())
    assert coach.revisions[-1].topics[0].name == "Renamed topic"
