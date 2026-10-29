from copy import deepcopy
from datetime import timedelta
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from competence_hub_api.portal.coach_registry import (
    CoachRegistryService,
    ProfileContent,
    RegistryConflict,
    RegistryDenied,
    public_projection,
)
from competence_hub_api.portal.coach_target import (
    ObjectEvidenceInput,
    subjects,
    public_target,
)
from scripts.coach_target_cases import (
    target_profile,
    three_family_profile,
    approvals_for,
)
from test_coach_registry import MemoryRegistry, ACTOR, NOW, change


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def rich_ready(content=None, repo=None):
    repo = repo or MemoryRegistry()
    service = CoachRegistryService(repo)
    coach = await service.create(
        actor=ACTOR, display_name="Synthetic", request_id=uuid4(), now=NOW
    )
    coach = await change(
        service, coach, "revision", content=content or target_profile()
    )
    coach = await change(service, coach, "submit", revision_id=coach.revisions[-1].id)
    for kind in ("content_review", "person_consent", "preview", "production"):
        coach = await change(
            service,
            coach,
            "approve",
            revision_id=coach.revisions[-1].id,
            kind=kind,
            evidence_ref="synthetic:approval",
        )
    coach = await change(service, coach, "lifecycle", lifecycle="active")
    return service, coach


@pytest.mark.parametrize("name", ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])
def test_synthetic_lossless_validation_roundtrip(name):
    p = target_profile(name)
    assert ProfileContent.model_validate_json(p.model_dump_json()) == p
    assert len(p.qualifications) == 2 and p.qualifications[0].key == "q-public"
    assert p.qualifications[1].public is False
    assert p.offerings[0].delivery_mode == "live_unspecified"


def test_three_families_five_formats_no_add_on_duplication():
    p = three_family_profile()
    output = public_target(p, "preview")
    assert len(output["offering_families"]) == 3
    assert sum(len(f["formats"]) for f in output["offering_families"]) == 5
    assert len(p.offerings) == 5 and len(p.offerings[2].variants) == 2
    assert p.offerings[1].duration.weeks == 6
    assert {b.excluded_services for f in p.offering_families for b in f.boundaries}
    assert "private:" not in json.dumps(output)


@pytest.mark.parametrize(
    "patch",
    [
        {"target_version": 0},
        {"qualifications": [dict(key="q", canonical_title="Unconfirmed", public=True)]},
        {
            "offerings": [
                dict(
                    key="therapy",
                    title="Therapy",
                    type="coaching",
                    service_domains=["psychotherapy"],
                )
            ]
        },
        {
            "offerings": [
                dict(
                    key="therapy",
                    title="Therapy",
                    type="other",
                    service_domains=["psychotherapy"],
                    bookable=True,
                )
            ]
        },
        {
            "offerings": [
                dict(key="x", title="X", type="workshop", family_key="missing")
            ]
        },
        {"offerings": [dict(title="X", type="other")]},
        {
            "qualifications": [
                dict(key="q", canonical_title="A"),
                dict(key="q", canonical_title="B", ordering=1),
            ]
        },
        {
            "presentation": {
                "external_links": [
                    dict(key="x", label="X", preview_url="javascript:alert(1)")
                ]
            }
        },
        {"offerings": [dict(key="x", title="X", type="other", price=999)]},
        {
            "offerings": [
                dict(key="x", title="X", type="other", protected_source_text="PRIVATE")
            ]
        },
    ],
)
def test_invalid_or_privilege_escalating_target_rejected(patch):
    with pytest.raises(ValidationError):
        target_profile(**patch)


@pytest.mark.anyio
async def test_exact_object_environment_consent_projection_and_revocation():
    service, coach = await rich_ready(three_family_profile())
    rid = coach.revisions[-1].id
    with pytest.raises(RegistryConflict):
        await change(service, coach, "publish", revision_id=rid, environment="preview")
    for e in approvals_for(coach.revisions[-1]):
        coach = await change(service, coach, "evidence", revision_id=rid, evidence=e)
    assert all(
        e.value.approved_at is None
        and e.value.approved_on is None
        and e.value.approved_by is None
        for e in coach.revisions[-1].object_evidence
    )
    coach = await change(
        service, coach, "publish", revision_id=rid, environment="preview"
    )
    output = public_projection((coach,), "preview")
    assert json.dumps(output, sort_keys=True) == json.dumps(
        public_projection((deepcopy(coach),), "preview"), sort_keys=True
    )
    assert len(output["coaches"][0]["qualifications"]) == 1
    assert len(output["coaches"][0]["offering_families"]) == 3
    assert output["coaches"][0]["offerings"] == []
    for secret in (
        "PRIVATE",
        "private:",
        "internal_note",
        "verification_state",
        "evidence_reference",
        "subject_hash",
        str(ACTOR.user_id),
        str(rid),
        "999",
    ):
        assert secret not in json.dumps(output)
    with pytest.raises(RegistryConflict):
        await change(
            service, coach, "publish", revision_id=rid, environment="production"
        )
    e = approvals_for(coach.revisions[-1])[0].model_copy(
        update={"key": "revoke", "status": "rejected"}
    )
    coach = await change(service, coach, "evidence", revision_id=rid, evidence=e)
    assert coach.publications["preview"].state == "withdrawn"
    assert not public_projection((coach,), "preview")["coaches"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "fault", ["wrong-object", "wrong-hash", "future", "duplicate", "draft", "idor"]
)
async def test_evidence_wrong_subject_rejected(fault):
    service, coach = await rich_ready()
    rid = coach.revisions[-1].id
    e = approvals_for(coach.revisions[-1])[0]
    if fault == "wrong-object":
        e = e.model_copy(update={"subject_key": "absent"})
    if fault == "wrong-hash":
        e = e.model_copy(update={"subject_hash": "0" * 64})
    if fault == "future":
        e = e.model_copy(update={"approved_at": NOW + timedelta(days=1)})
    if fault == "duplicate":
        coach = await change(service, coach, "evidence", revision_id=rid, evidence=e)
    if fault == "draft":
        coach = await change(service, coach, "revision", content=target_profile())
        rid = coach.revisions[-1].id
    if fault == "idor":
        rid = uuid4()
    with pytest.raises((RegistryConflict, ValueError, LookupError)):
        await change(service, coach, "evidence", revision_id=rid, evidence=e)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "role", ["coach", "internal", "calendar_reviewer", "company_contact"]
)
async def test_admin_only_evidence_and_qualification_edits(role):
    service, coach = await rich_ready()
    for op, kwargs in [
        (
            "evidence",
            dict(
                revision_id=coach.revisions[-1].id,
                evidence=approvals_for(coach.revisions[-1])[0],
            ),
        ),
        ("revision", dict(content=target_profile())),
    ]:
        with pytest.raises(RegistryDenied):
            await service.mutate(
                actor=SimpleNamespace(user_id=uuid4(), roles=(role,)),
                coach_id=coach.id,
                expected_version=coach.version,
                operation=op,
                now=NOW,
                **kwargs,
            )


@pytest.mark.anyio
async def test_no_silent_downgrade_renames_keep_identity_and_new_revision_no_evidence():
    service, coach = await rich_ready()
    old = coach.revisions[-1]
    for e in approvals_for(old):
        coach = await change(service, coach, "evidence", revision_id=old.id, evidence=e)
    with pytest.raises(RegistryConflict):
        await change(
            service,
            coach,
            "revision",
            content=ProfileContent(display_name="X", short_intro="X"),
        )
    value = old.content.model_dump(mode="json")
    value["qualifications"][0]["canonical_title"] = "Changed title"
    value["offering_families"][0]["title"] = "Changed family"
    value["offerings"][0]["active"] = False
    coach = await change(
        service, coach, "revision", content=ProfileContent.model_validate(value)
    )
    new = coach.revisions[-1]
    assert not new.object_evidence and not new.approvals
    assert new.content.qualifications[0].key == old.content.qualifications[0].key
    assert new.content.offering_families[0].key == old.content.offering_families[0].key
    assert new.content.offerings[0].key == old.content.offerings[0].key
    value.pop("qualifications")
    with pytest.raises(RegistryConflict):
        await change(
            service,
            coach,
            "draft",
            revision_id=new.id,
            content=ProfileContent.model_validate(value),
        )


def test_protected_scope_and_internal_verification_not_public_copy_consent():
    p = target_profile()
    e = dict(
        key="e",
        subject_type="family",
        subject_key="family-one",
        subject_hash=subjects(p)["family", "family-one"],
        kind="protected_source",
        environment="preview",
        scope="protected_source_content",
        status="unknown",
    )
    assert ObjectEvidenceInput(**e).approved_at is None
    with pytest.raises(ValidationError):
        ObjectEvidenceInput(**{**e, "scope": "public_content"})
    with pytest.raises(ValidationError):
        ObjectEvidenceInput(**{**e, "kind": "qualification"})


def test_nonbookable_therapy_keeps_distinct_domain():
    p = target_profile(
        offerings=[
            dict(
                key="therapy",
                title="Psychotherapy",
                type="other",
                service_domains=["psychotherapy"],
                bookable=False,
            )
        ]
    )
    assert p.offerings[0].service_domains == ("psychotherapy",)
    assert not p.qualifications[-1].public


@pytest.mark.anyio
@pytest.mark.parametrize(
    "field", ["duration", "variants", "family_key", "protected_source_reference"]
)
async def test_full_snapshot_rejects_omitted_nested_rich_fields(field):
    service, coach = await rich_ready()
    value = coach.revisions[-1].content.model_dump(mode="json")
    value["offerings"][0]["protected_source_reference"] = "private:original"
    # Establish the populated private reference in the immutable source snapshot.
    original = ProfileContent.model_validate(value)
    coach = await change(service, coach, "revision", content=original)
    value["offerings"][0].pop(field)
    with pytest.raises(RegistryConflict, match="omitted"):
        await change(
            service,
            coach,
            "draft",
            revision_id=coach.revisions[-1].id,
            content=ProfileContent.model_validate(value),
        )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "field", ["quote", "languages", "session_minutes", "description"]
)
async def test_recursive_omissions_conflict_but_explicit_clears_are_allowed(field):
    p = target_profile().model_dump(mode="json")
    p["offerings"][0]["variants"][0]["description"] = "Synthetic option description"
    original = ProfileContent.model_validate(p)
    service, coach = await rich_ready(original)

    def nested(value):
        if field in {"quote", "languages"}:
            return value["presentation"]
        if field == "session_minutes":
            return value["offerings"][1]["duration"]
        return value["offerings"][0]["variants"][0]

    value = original.model_dump(mode="json")
    nested(value).pop(field)
    with pytest.raises(RegistryConflict, match="omitted"):
        await change(
            service, coach, "revision", content=ProfileContent.model_validate(value)
        )
    nested(value)[field] = [] if field == "languages" else None
    coach = await change(
        service, coach, "revision", content=ProfileContent.model_validate(value)
    )
    assert nested(coach.revisions[-1].content.model_dump(mode="json"))[field] in (
        None,
        [],
    )
