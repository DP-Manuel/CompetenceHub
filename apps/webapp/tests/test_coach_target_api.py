"""Synthetic COACH-3C Admin contract and no-loss editor regressions."""

from importlib.resources import files
from uuid import uuid4

import pytest

from competence_hub_api.portal.coach_management import target_revision_detail
from competence_hub_api.portal.coach_registry import ProfileContent, ProfileRevision
from competence_hub_api.portal.coach_target import subjects
from test_coach_registry import ACTOR, NOW, TOPIC_ID, TopicSnapshot, profile
from test_coach_registry_api import BASE, client, headers


@pytest.fixture
def anyio_backend():
    return "asyncio"


def rich_content():
    content = profile().model_dump(mode="json")
    content.update(
        target_version=1,
        public_roles=[
            dict(key="role-alpha", code="coaching", display_label="Coach", ordering=0)
        ],
        qualifications=[
            dict(
                key="qualification-alpha",
                canonical_title="Synthetic qualification",
                public_display_label="Synthetic public qualification",
                public=True,
                ordering=0,
                issuer="Synthetic issuer",
                qualification_type="certificate",
                status="active",
                verification_state="source_asserted",
                evidence_reference="synthetic:qualification",
                internal_note="Internal qualification note",
            )
        ],
        offering_families=[
            dict(
                key="family-alpha",
                title="Synthetic family",
                ordering=0,
                description="Synthetic family description",
                service_domains=["training"],
                target_groups=["Synthetic teams"],
                target_focus=["Synthetic focus"],
                variants=[
                    dict(
                        key="family-option",
                        kind="option",
                        title="Synthetic option",
                        ordering=0,
                    )
                ],
                boundaries=[
                    dict(
                        key="family-boundary",
                        text="Synthetic family boundary",
                        excluded_services=["psychotherapy"],
                    )
                ],
                protected_source_reference="synthetic:protected",
            )
        ],
        boundaries=[
            dict(
                key="profile-boundary",
                text="Synthetic profile boundary",
                excluded_services=["psychotherapy"],
            )
        ],
        presentation=dict(
            teaser="Synthetic teaser",
            languages=["German"],
            sections=[
                dict(
                    key="profile-section",
                    kind="profile",
                    headings=["Synthetic heading"],
                    paragraphs=["Synthetic paragraph"],
                )
            ],
            external_links=[
                dict(
                    key="link-alpha",
                    label="Synthetic link",
                    preview_url="https://example.invalid/preview",
                    production_url="https://example.invalid/production",
                )
            ],
        ),
    )
    for n, offer in enumerate(content["offerings"]):
        offer.update(
            key=f"format-{n}",
            family_key="family-alpha",
            service_domains=["training"],
            bookable=False,
            duration=dict(weeks=8, sessions_per_week=1, session_minutes=90),
            delivery_mode="online",
            delivery_label="Synthetic live format",
            target_groups=["Synthetic teams"],
            target_focus=["Synthetic focus"],
            program_modules=["Synthetic module"],
            boundaries=[
                dict(
                    key="format-boundary",
                    text="Synthetic format boundary",
                    excluded_services=["psychotherapy"],
                )
            ],
            variants=[
                dict(
                    key="variant-alpha",
                    kind="add_on",
                    title="Synthetic add-on",
                    ordering=0,
                    duration=dict(minutes=30),
                )
            ],
            protected_source_reference="synthetic:format",
        )
    return ProfileContent.model_validate(content)


async def submitted(c):
    coach = (
        await c.post(
            BASE,
            json={"display_name": "Synthetic", "client_request_id": str(uuid4())},
            headers=headers(),
        )
    ).json()
    path = BASE + "/" + coach["id"]
    response = await c.post(
        path + "/revisions",
        json={
            "expected_version": coach["version"],
            "content": rich_content().model_dump(mode="json"),
        },
        headers=headers(),
    )
    assert response.status_code == 200
    coach = response.json()
    revision = coach["revisions"][-1]
    response = await c.post(
        path + "/revisions/" + revision["id"] + "/submit",
        json={"expected_version": coach["version"]},
        headers=headers(),
    )
    assert response.status_code == 200
    return path, response.json()


def evidence_for(coach, **changes):
    revision = coach["revisions"][-1]
    subject = next(
        s for s in revision["evidence_subjects"] if s["subject_type"] == "qualification"
    )
    evidence = {k: subject[k] for k in ("subject_type", "subject_key", "subject_hash")}
    evidence.update(
        key="evidence-" + str(uuid4()),
        kind="qualification",
        environment="preview",
        scope="internal_verification",
        status="approved",
        evidence_reference="synthetic:approval",
        approved_on="2026-10-01",
    )
    evidence.update(changes)
    return {"expected_version": coach["version"], "evidence": evidence}


@pytest.mark.anyio
async def test_target_api_evidence_exact_binding_historical_day_and_fresh_revision():
    async with client() as c:
        path, coach = await submitted(c)
        revision = coach["revisions"][-1]
        evidence_path = path + "/revisions/" + revision["id"] + "/evidence"
        body = evidence_for(coach)
        result = await c.post(evidence_path, json=body, headers=headers())
        assert result.status_code == 200
        assert result.headers["cache-control"] == "no-store"
        updated = result.json()
        record = updated["revisions"][-1]["object_evidence"][0]
        assert record["value"] == {
            **body["evidence"],
            "approved_at": None,
            "approved_by": None,
            "internal_note": None,
        }
        assert record["recorded_by"] and record["recorded_at"] and record["id"]
        assert record["value"]["approved_at"] is None
        assert (
            await c.post(evidence_path, json=body, headers=headers())
        ).status_code == 409
        for changes in ({"subject_hash": "0" * 64}, {"subject_key": "missing-object"}):
            assert (
                await c.post(
                    evidence_path,
                    json=evidence_for(updated, **changes),
                    headers=headers(),
                )
            ).status_code == 409
        foreign = await c.post(
            BASE,
            json={"display_name": "Other synthetic", "client_request_id": str(uuid4())},
            headers=headers(),
        )
        assert (
            await c.post(
                BASE
                + "/"
                + foreign.json()["id"]
                + "/revisions/"
                + revision["id"]
                + "/evidence",
                json={**evidence_for(updated), "expected_version": 1},
                headers=headers(),
            )
        ).status_code == 404
        response = await c.post(
            path + "/revisions",
            json={
                "expected_version": updated["version"],
                "content": revision["content"],
            },
            headers=headers(),
        )
        assert response.status_code == 200
        assert response.json()["revisions"][-1]["object_evidence"] == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "changes",
    [
        {"unexpected": True},
        {"kind": "publication"},
        {"scope": "protected_source_content"},
        {"environment": "staging"},
        {"subject_hash": "not-a-hash"},
        {"evidence_reference": None},
        {"approved_at": "2026-10-01T10:00:00"},
        {"approved_at": "2026-10-01T10:00:00Z"},
        {"approved_on": "2027-01-01"},
    ],
)
async def test_target_evidence_invalid_requests_never_mutate(changes):
    async with client() as c:
        path, coach = await submitted(c)
        evidence_path = (
            path + "/revisions/" + coach["revisions"][-1]["id"] + "/evidence"
        )
        response = await c.post(
            evidence_path, json=evidence_for(coach, **changes), headers=headers()
        )
        assert response.status_code == 400
        assert (await c.get(path)).json() == coach


@pytest.mark.anyio
@pytest.mark.parametrize(
    "roles,authenticated,status",
    [
        (("admin",), False, 401),
        (("internal",), True, 403),
        (("coach",), True, 403),
        (("calendar_reviewer",), True, 403),
        (("company_contact",), True, 403),
    ],
)
async def test_target_evidence_is_admin_only(roles, authenticated, status):
    async with client(roles, authenticated=authenticated) as c:
        path = BASE + "/" + str(uuid4()) + "/revisions/" + str(uuid4()) + "/evidence"
        response = await c.post(path, json={}, headers=headers())
        assert response.status_code == status


@pytest.mark.anyio
async def test_target_evidence_csrf_minimal_and_draft_guard():
    async with client() as c:
        path, coach = await submitted(c)
        revision = coach["revisions"][-1]
        url = path + "/revisions/" + revision["id"] + "/evidence"
        for extra in (
            {"X-CSRF-Token": "wrong"},
            {"Origin": "https://foreign.example.invalid"},
        ):
            assert (
                await c.post(url, json=evidence_for(coach), headers=headers(**extra))
            ).status_code == 403
        result = await c.post(
            url,
            json=evidence_for(coach),
            headers={**headers(), "Prefer": "return=minimal"},
        )
        assert result.status_code == 200 and "revisions" not in result.json()
        draft = (
            await c.post(
                path + "/revisions",
                json={
                    "expected_version": result.json()["version"],
                    "content": revision["content"],
                },
                headers=headers(),
            )
        ).json()
        url = path + "/revisions/" + draft["revisions"][-1]["id"] + "/evidence"
        assert (
            await c.post(url, json=evidence_for(draft), headers=headers())
        ).status_code == 409


@pytest.mark.anyio
async def test_target_evidence_keeps_existing_bounded_request_contract():
    async with client() as c:
        path, coach = await submitted(c)
        url = path + "/revisions/" + coach["revisions"][-1]["id"] + "/evidence"
        assert (
            await c.post(
                url,
                content=" " * 32769,
                headers={**headers(), "Content-Type": "application/json"},
            )
        ).status_code == 400
        body = evidence_for(coach)
        assert (
            await c.post(
                url, json={**body, "recorded_by": str(uuid4())}, headers=headers()
            )
        ).status_code == 400
        assert (await c.get(path)).json() == coach


@pytest.mark.anyio
async def test_target_evidence_unknown_does_not_infer_historical_approval_or_qualifications():
    async with client() as c:
        path, coach = await submitted(c)
        revision = coach["revisions"][-1]
        url = path + "/revisions/" + revision["id"] + "/evidence"
        body = evidence_for(
            coach, status="unknown", evidence_reference=None, approved_on=None
        )
        response = await c.post(url, json=body, headers=headers())
        assert response.status_code == 200
        updated = response.json()["revisions"][-1]
        evidence = updated["object_evidence"][0]["value"]
        assert evidence["status"] == "unknown"
        for field in (
            "approved_at",
            "approved_on",
            "approved_by",
            "evidence_reference",
        ):
            assert evidence[field] is None
        assert updated["content"] == revision["content"]


def test_target_admin_projection_uses_exact_topic_snapshot_and_safe_subject_labels():
    content = rich_content()
    topic = TopicSnapshot(TOPIC_ID, "Synthetic topic", ("personalentwicklung",))
    revision = ProfileRevision(uuid4(), 1, content, ACTOR.user_id, NOW, topics=(topic,))
    detail = target_revision_detail(revision)
    assert detail["object_evidence"] == []
    for subject in detail["evidence_subjects"]:
        assert (
            subject["subject_hash"]
            == subjects(content, (topic,))[
                (subject["subject_type"], subject["subject_key"])
            ]
        )
        assert set(subject) == {"label", "subject_type", "subject_key", "subject_hash"}
    assert (
        subjects(content, (topic,))[("profile", "profile")]
        != subjects(content)[("profile", "profile")]
    )
    assert "Internal qualification note" not in str(detail)


def test_target_editor_preserves_rich_fields_and_has_accessible_structured_controls(
    tmp_path,
):
    playwright = pytest.importorskip("playwright.sync_api")
    source = (
        files("competence_hub_api")
        .joinpath("portal_ui", "coach-management.js")
        .read_text(encoding="utf-8")
    )
    css = (
        files("competence_hub_api")
        .joinpath("portal_ui", "styles.css")
        .read_text(encoding="utf-8")
    )
    content = rich_content().model_dump(mode="json")
    content["qualifications"][0][
        "canonical_title"
    ] = '<img src=x onerror="window.injected=true"> Synthetic qualification'
    revision = ProfileRevision(
        uuid4(), 1, ProfileContent.model_validate(content), ACTOR.user_id, NOW
    )
    workspace = dict(
        id=str(uuid4()),
        display_name=content["display_name"],
        lifecycle="draft",
        version=2,
        revision=dict(
            id=str(revision.id),
            number=1,
            status="draft",
            content=content,
            topics=[],
            approvals=[],
            **target_revision_detail(revision),
        ),
        capabilities=dict(
            editable=True,
            new_revision=False,
            lifecycles=[],
            approvals=[],
            publish=[],
            withdraw=[],
            object_evidence=False,
        ),
        links=dict(
            portal_account="none",
            calendar_role=False,
            future_calendar=False,
            public_profile_path=None,
        ),
        publications={},
    )
    with playwright.sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
        except playwright.Error:
            pytest.skip(
                "Local Edge unavailable; native browser acceptance remains a separate gate"
            )
        with browser:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.route(
                "https://synthetic.example.invalid/**",
                lambda route: route.fulfill(
                    content_type="text/html",
                    body="<!doctype html><html lang='de'><head><title>Synthetic target QA</title></head><body><main id='root'></main></body></html>",
                ),
            )
            page.goto("https://synthetic.example.invalid/")
            page.add_style_tag(content=css)
            page.add_script_tag(
                content=source.replace(
                    "export function createCoachManagement",
                    "function createCoachManagement",
                )
            )
            page.evaluate(
                """async (workspace) => {
              window.workspace=workspace; window.writes=[];
              window.manager=createCoachManagement({refreshCsrf:async()=>({ok:true}), denied:()=>{}, request:async(path, options={})=>{
                let result;
                if(options.method) {window.writes.push({path,options}); return new Response('{}',{status:409});}
                if(path.includes('/topics?')) result={items:[],has_more:false};
                else if(path.includes('/revisions?') || path.includes('/history?')) result={items:[],has_more:false};
                else if(path.includes('/'+workspace.id)) result=workspace;
                else result={items:[{...workspace, revision_number:1, revision_status:'draft',preview:'not_published',production:'not_published',topic_count:0,offering_count:3}],has_more:false};
                return new Response(JSON.stringify(result),{status:200});
              }});
              document.querySelector('#root').append(manager.root); manager.root.hidden=false; await manager.index();
            }""",
                workspace,
            )
            page.get_by_role("button", name=content["display_name"], exact=True).click()
            page.get_by_role("tab", name="Profil", exact=True).click()
            page.get_by_label("Anzeigename", exact=True).fill("Synthetic renamed")
            page.get_by_role("tab", name="Angebote", exact=True).click()
            page.get_by_role("button", name="Angebot hinzufügen", exact=True).click()
            page.locator(".cm-offering").last.get_by_label(
                "Titel", exact=True
            ).first.fill("Synthetic added format")
            page.get_by_role(
                "button", name="Profilentwurf speichern", exact=True
            ).click()
            page.wait_for_function("window.writes.length===1")
            saved = page.evaluate("window.writes[0].options.body.content")
            assert saved["display_name"] == "Synthetic renamed"
            for key in (
                "target_version",
                "public_roles",
                "qualifications",
                "offering_families",
                "presentation",
                "boundaries",
            ):
                assert saved[key] == content[key]
            assert saved["offerings"][:3] == content["offerings"]
            assert saved["offerings"][3]["key"].startswith("format-")
            assert (
                page.get_by_label("Anzeigename", exact=True).input_value()
                == "Synthetic renamed"
            )
            for width in (1280, 390):
                page.set_viewport_size({"width": width, "height": 900})
                for tab in ("Qualifikationen", "Angebotsfamilien", "Angebote"):
                    page.get_by_role("tab", name=tab, exact=True).click()
                    page.locator('[role="tabpanel"]:visible details').evaluate_all(
                        "items=>items.forEach(i=>i.open=true)"
                    )
                    assert page.evaluate(
                        "document.documentElement.scrollWidth<=innerWidth"
                    ), (width, tab)
                page.screenshot(path=str(tmp_path / f"coach-target-{width}.png"))
            assert page.locator('input[type="checkbox"]').count() > 0
            assert page.locator("textarea").count() > 0
            assert page.locator('[aria-invalid="true"]').count() == 0
            assert page.locator("img").count() == 0
            assert page.evaluate("window.injected===undefined")
            page.evaluate("""async()=>{
              manager.reset(); workspace.revision.status='submitted'; workspace.capabilities.editable=false; workspace.capabilities.object_evidence=true;
              manager.root.hidden=false; await manager.index();
            }""")
            page.get_by_role("button", name=content["display_name"], exact=True).click()
            page.get_by_role("tab", name="Nachweise (Admin)", exact=True).click()
            page.locator("summary").filter(has_text="Nachweis erfassen").click()
            evidence_form = page.locator("#cm-panel-evidence form")
            qualifier_index = next(
                n
                for n, s in enumerate(workspace["revision"]["evidence_subjects"])
                if s["subject_type"] == "qualification"
            )
            evidence_form.get_by_label("Objekt", exact=True).select_option(
                str(qualifier_index)
            )
            evidence_form.get_by_label("Nachweisart", exact=True).select_option(
                "qualification"
            )
            evidence_form.get_by_label("Umgebung", exact=True).select_option("preview")
            evidence_form.get_by_label("Scope", exact=True).select_option(
                "internal_verification"
            )
            evidence_form.get_by_label("Status", exact=True).select_option("approved")
            evidence_form.get_by_label("Nachweisreferenz", exact=True).fill(
                "synthetic:approval"
            )
            evidence_form.get_by_label(
                "Historischer Freigabetag (optional)", exact=True
            ).fill("2026-10-01")
            evidence_form.get_by_role(
                "button", name="Nachweis erfassen", exact=True
            ).click()
            page.wait_for_function("window.writes.length===2")
            payload = page.evaluate("window.writes[1].options.body")
            assert payload["expected_version"] == 2
            for key in ("subject_type", "subject_key", "subject_hash"):
                assert (
                    payload["evidence"][key]
                    == workspace["revision"]["evidence_subjects"][qualifier_index][key]
                )
            assert payload["evidence"]["environment"] == "preview"
            assert payload["evidence"]["scope"] == "internal_verification"
            assert payload["evidence"]["status"] == "approved"
            assert payload["evidence"]["approved_on"] == "2026-10-01"
            assert "approved_at" not in payload["evidence"]
            assert (
                evidence_form.get_by_label("Nachweisreferenz", exact=True).input_value()
                == "synthetic:approval"
            )
            assert page.locator("img").count() == 0
            assert page.evaluate("window.injected===undefined")
            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
            page.screenshot(path=str(tmp_path / "coach-target-evidence-390.png"))
            legacy = profile().model_dump(mode="json")
            page.evaluate(
                """async(content)=>{
              manager.reset(); workspace.revision.content=content; workspace.revision.status='draft';
              workspace.capabilities.editable=true; workspace.capabilities.object_evidence=false;
              manager.root.hidden=false; await manager.index();
            }""",
                legacy,
            )
            page.get_by_role("button", name=content["display_name"], exact=True).click()
            page.get_by_role("tab", name="Profil", exact=True).click()
            page.get_by_label("Anzeigename", exact=True).fill(
                "Synthetic legacy renamed"
            )
            page.get_by_role(
                "button", name="Profilentwurf speichern", exact=True
            ).click()
            page.wait_for_function("window.writes.length===3")
            legacy_saved = page.evaluate("window.writes[2].options.body.content")
            assert legacy_saved == {
                **legacy,
                "display_name": "Synthetic legacy renamed",
            }
            print("Target UI screenshots:", tmp_path)
