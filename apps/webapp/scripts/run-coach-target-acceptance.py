"""Real local schema9 + native password/MFA + Edge, never fixture-only success.

Invoke through run-coach-target-local.ps1 -Browser for a fresh disposable DB.
Standalone: PYTHONPATH=src; supply ONLY the two COACH_TARGET_LOCAL process URLs,
then run this script from apps/webapp. Existing business rows are refused, never
reset. The caller owns database destruction even after failure. No VPS access.
Screenshots contain post-login synthetic business UI only; no traces/HAR/tokens.
"""

import base64
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import traceback
from uuid import uuid4

import pyotp
from playwright.sync_api import expect, sync_playwright
from sqlalchemy import text

from coach_target_fixture import LocalCoachTargetFixture

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "release-artifacts/coach3c-local-20261029"
READ = "/api/v1/admin/coach-management"
WRITE = "/api/v1/admin/coaches"
WORKSPACE = "#coach-management-workspace"
TABS = (
    "overview",
    "profile",
    "topics",
    "competencies",
    "qualifications",
    "families",
    "offerings",
    "evidence",
    "publication",
    "history",
)
XSS = '<img src=x onerror="window.coachTargetXss=1">Synthetic literal text'


def tab(page, key):
    page.locator("#cm-tab-" + key).click()


def panel(page, key):
    return page.locator("#cm-panel-" + key)


def expand(container):
    # Opening real disclosures is presentation only, never a data/API substitute.
    container.locator("details").evaluate_all("nodes=>nodes.forEach(n=>n.open=true)")


def saved(page, button="Profilentwurf speichern"):
    page.get_by_role("button", name=button, exact=True).click()
    expect(page.locator(WORKSPACE + " .form-success")).to_have_text("Gespeichert.")


def confirm(page, label):
    page.get_by_role("button", name=label, exact=True).click()
    page.get_by_role("dialog").get_by_role(
        "button", name="Best\u00e4tigen", exact=True
    ).click()
    expect(page.locator(WORKSPACE + " .form-success")).to_have_text("Gespeichert.")


def detail(context, base, coach_id):
    response = context.request.get(base + READ + "/" + str(coach_id))
    if response.status != 200:
        raise AssertionError("Native management read failed")
    return response.json()


def csrf(context, base):
    response = context.request.post(
        base + "/api/v1/portal/access/session/csrf",
        headers={"Origin": base},
    )
    if response.status != 204:
        raise AssertionError("Native CSRF refresh failed")
    return {"Origin": base, "X-CSRF-Token": response.headers["x-csrf-token"]}


def login(page, base, fixture, role):
    page.goto(base + "/portal/", wait_until="domcontentloaded")
    page.locator("#login-email").fill(fixture.emails[role])
    page.locator("#login-password").fill(fixture.password)
    page.get_by_role("button", name="Anmelden", exact=True).click()
    if role == "contact":
        expect(page.locator("#login-error")).to_be_visible()
        expect(page.locator("#login-view")).to_be_visible()
        return
    page.locator("#enrollment-code").wait_for(state="visible")
    secret = page.locator("#provisioning-secret").inner_text()
    page.locator("#enrollment-code").fill(
        pyotp.TOTP(secret).at(fixture.now.timestamp())
    )
    page.get_by_role("button", name="Einrichtung abschlie\u00dfen", exact=True).click()
    page.locator("#recovery-view").wait_for(state="visible")
    page.locator("#recovery-confirmed").check()
    page.get_by_role("button", name="Portal \u00f6ffnen", exact=True).click()
    expect(page.locator("#portal-view")).to_be_visible()


def enter(page, base, name="Coach Target Alpha"):
    page.goto(base + "/portal/coaches/", wait_until="domcontentloaded")
    page.get_by_role("button", name=name, exact=True).click()
    expect(page.locator("#cm-tab-profile")).to_be_visible()


def geometry(page, label, check):
    check(
        label + " no horizontal overflow",
        page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),
    )
    check(
        label + " visible text not clipped",
        page.locator(WORKSPACE).evaluate("""root=>{
      const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT); let t;
      while(t=walker.nextNode()) {
        const p=t.parentElement;
        if(!t.textContent.trim()||!p.checkVisibility()||p.closest('select,textarea'))continue;
        const range=document.createRange();range.selectNodeContents(t);
        for(const r of range.getClientRects()) {
          if(!r.width)continue;if(r.left < -1 || r.right>innerWidth+1)return false;
          for(let a=p;a&&a!==document.body;a=a.parentElement){
            const s=getComputedStyle(a),b=a.getBoundingClientRect();
            if(['hidden','clip'].includes(s.overflowX)&&(r.left<b.left-1||r.right>b.right+1))return false;
            if(['hidden','clip'].includes(s.overflowY)&&(r.top<b.top-1||r.bottom>b.bottom+1))return false;
          }
        }
      }return true;}"""),
    )
    check(
        label + " text blocks do not overlap",
        page.locator(WORKSPACE).evaluate("""root=>{
      const nodes=[...root.querySelectorAll('h2,h3,h4,legend,label,button,dt,dd,summary')]
        .filter(n=>n.checkVisibility());
      const rects=nodes.map(n=>{const r=document.createRange();r.selectNodeContents(n);
        return [...r.getClientRects()].filter(x=>x.width&&x.height);});
      return nodes.every((n,i)=>nodes.slice(i+1).every((m,j)=>n.contains(m)||m.contains(n)||
        rects[i].every(a=>rects[i+j+1].every(b=>
          Math.min(a.right,b.right)-Math.max(a.left,b.left)<=1 ||
          Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)<=1))));}"""),
    )


def screenshot(page, destination, *, physical_zoom=False, focus_selector=None):
    page.evaluate("scrollTo(0,0)")
    if not physical_zoom:
        page.screenshot(path=str(destination), full_page=True)
    session = page.context.new_cdp_session(page)
    try:
        if physical_zoom:
            size = session.send("Page.getLayoutMetrics")["contentSize"]
            shot = session.send(
                "Page.captureScreenshot",
                {
                    "format": "png",
                    "captureBeyondViewport": True,
                    "clip": {
                        "x": 0,
                        "y": 0,
                        "width": size["width"],
                        "height": size["height"],
                        "scale": 1,
                    },
                },
            )
            destination.write_bytes(base64.b64decode(shot["data"]))
        if focus_selector:
            page.locator(focus_selector).evaluate(
                "e=>e.scrollIntoView({block:'start'})"
            )
        # No clip: native zoom uses physical viewport pixels. Playwright's CSS
        # viewport clip can cut away half the screen; tall compositor captures can
        # duplicate bands. Viewport shots plus line-geometry are authoritative.
        shot = session.send(
            "Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False}
        )
        pixels = base64.b64decode(shot["data"])
        physical_width = session.send("Page.getLayoutMetrics")["layoutViewport"][
            "clientWidth"
        ]
        if int.from_bytes(pixels[16:20], "big") < physical_width - 2:
            raise AssertionError("Viewport screenshot cropped physical browser width")
        destination.with_stem(destination.stem + "-viewport").write_bytes(pixels)
    finally:
        session.detach()


def responsive(page, base, prefix, check, *, physical_zoom=False):
    enter(page, base)
    for key in TABS:
        tab(page, key)
        expand(panel(page, key))
        if key in ("profile", "qualifications", "families", "offerings", "evidence"):
            screenshot(
                page,
                OUT / f"{prefix}-{key}.png",
                physical_zoom=physical_zoom,
                focus_selector="#cm-panel-" + key,
            )
        geometry(page, prefix + " " + key, check)


def record_evidence(
    page,
    context,
    base,
    coach_id,
    subject,
    kind,
    *,
    environment="preview",
    scope="public_content",
    status="approved",
):
    tab(page, "evidence")
    area = panel(page, "evidence")
    area.locator("summary").filter(has_text="Nachweis erfassen").click()
    area.get_by_label("Objekt", exact=True).select_option(
        label=(
            f"{subject['subject_type']} \u00b7 {subject['subject_key']} \u00b7 {subject['label']}"
        )
    )
    area.get_by_label("Nachweisart", exact=True).select_option(kind)
    area.get_by_label("Umgebung", exact=True).select_option(environment)
    area.get_by_label("Scope", exact=True).select_option(scope)
    area.get_by_label("Status", exact=True).select_option(status)
    area.get_by_label("Nachweisreferenz", exact=True).fill("synthetic:browser-consent")
    area.get_by_label("Freigebende Person", exact=True).fill("Synthetic reviewer")
    area.get_by_label("Historischer Freigabetag (optional)", exact=True).fill(
        "2026-01-02"
    )
    area.get_by_label("Interne Notiz", exact=True).fill(
        "INTERNAL_BROWSER_EVIDENCE_NOTE"
    )
    before = len(detail(context, base, coach_id)["revision"]["object_evidence"])
    area.get_by_role("button", name="Nachweis erfassen", exact=True).click()
    expect(page.locator(WORKSPACE + " .form-success")).to_have_text("Gespeichert.")
    data = detail(context, base, coach_id)["revision"]["object_evidence"]
    if len(data) != before + 1:
        raise AssertionError("UI evidence was not persisted")
    return data[-1]


def business_checks(page, context, base, fixture, check):
    coach_id = fixture.ids["Alpha"]
    enter(page, base)
    before = detail(context, base, coach_id)["revision"]["content"]
    tab(page, "qualifications")
    area = panel(page, "qualifications")
    expand(area)
    expect(
        area.get_by_label("Kanonischer Titel (intern)", exact=True).first
    ).to_have_value("INTERNAL_CANONICAL_TITLE")
    area.get_by_label("\u00d6ffentliche Bezeichnung", exact=True).first.fill(
        "Synthetic UI certificate"
    )
    area.get_by_label("Pr\u00fcfstatus (intern)", exact=True).first.select_option(
        "verified"
    )
    add = area.get_by_role("button", name="Qualifikationen hinzuf\u00fcgen", exact=True)
    add.focus()
    page.keyboard.press("Enter")
    title = area.get_by_label("Kanonischer Titel (intern)", exact=True).last
    expect(title).to_be_focused()
    stable_key = area.get_by_label("Stabiler Schl\u00fcssel", exact=True).last
    qualification_key = stable_key.input_value()
    check(
        "Keyboard add qualification focuses editable title and protects stable key",
        title.evaluate("e=>e===document.activeElement && !e.readOnly && !e.disabled")
        and stable_key.evaluate("e=>e.readOnly")
        and bool(qualification_key),
    )
    title.fill("Synthetic keyboard qualification")
    area.get_by_label("Interne Notiz", exact=True).last.fill(
        "INTERNAL_NEW_QUALIFICATION"
    )
    saved(page)
    after = detail(context, base, coach_id)["revision"]["content"]
    check(
        "Native UI qualification edits persisted with public/internal separation",
        len(after["qualifications"]) == 3
        and after["qualifications"][0]["public_display_label"]
        == "Synthetic UI certificate"
        and after["qualifications"][0]["verification_state"] == "verified"
        and after["qualifications"][-1]["key"] == qualification_key
        and not after["qualifications"][-1]["public"],
    )
    check(
        "Qualification edit preserves unrelated rich data",
        all(before[k] == after[k] for k in before if k != "qualifications"),
    )

    tab(page, "families")
    area = panel(page, "families")
    expand(area)
    area.get_by_label("Titel", exact=True).first.fill(XSS)
    area.get_by_label("Titel", exact=True).nth(1).fill("Synthetic edited family option")
    area.get_by_role(
        "button", name="Angebotsfamilien hinzuf\u00fcgen", exact=True
    ).click()
    family = area.locator("section").filter(
        has=page.get_by_role("heading", name="Angebotsfamilien", exact=True)
    )
    # Direct children distinguish family items from their nested variants/boundaries.
    family_items = family.locator(":scope > div > details")
    expect(family_items).to_have_count(2)
    new_family = family_items.last
    family_title = new_family.get_by_label("Titel", exact=True)
    expect(new_family).to_have_js_property("open", True)
    expect(family_title).to_be_focused()
    check(
        "Adding family opens new direct-child disclosure and focuses editable title",
        family_title.evaluate(
            "e=>e===document.activeElement && !e.readOnly && !e.disabled"
        ),
    )
    family_title.fill("Synthetic UI second family")
    new_family.get_by_label("Training", exact=True).check()
    family_key = new_family.get_by_label(
        "Stabiler Schl\u00fcssel", exact=True
    ).input_value()
    saved(page)
    content = detail(context, base, coach_id)["revision"]["content"]
    check(
        "Family and option edits persisted with immutable stable keys",
        content["offering_families"][0]["key"] == "family-communication"
        and content["offering_families"][0]["title"] == XSS
        and content["offering_families"][0]["variants"][0]["title"]
        == "Synthetic edited family option"
        and content["offering_families"][1]["key"] == family_key,
    )
    tab(page, "families")
    check(
        "Untrusted family summary is literal textContent, no HTML execution",
        panel(page, "families").locator("summary").first.text_content() == XSS
        and page.locator(WORKSPACE + " img").count() == 0
        and page.evaluate("window.coachTargetXss===undefined"),
    )

    tab(page, "offerings")
    area = panel(page, "offerings")
    expand(area)
    original = area.locator(".cm-offering").first
    original.get_by_label("Dauer in Minuten", exact=True).first.fill("210")
    original.get_by_label("Durchf\u00fchrung", exact=True).select_option("hybrid")
    original.get_by_label("Programmmodule", exact=True).fill(
        "Synthetic edited module\nSynthetic practice"
    )
    original.get_by_label("Titel", exact=True).nth(1).fill(
        "Synthetic edited format option"
    )
    area.get_by_role("button", name="Angebot hinzuf\u00fcgen", exact=True).click()
    new_offer = area.locator(".cm-offering").last
    expand(new_offer)
    new_offer.get_by_label("Titel", exact=True).fill("Synthetic UI second format")
    new_offer.get_by_label("Angebotsfamilie", exact=True).focus()
    new_offer.get_by_label("Angebotsfamilie", exact=True).select_option(family_key)
    new_offer.get_by_role(
        "button", name="Varianten und Optionen hinzuf\u00fcgen", exact=True
    ).click()
    new_offer.get_by_label("Titel", exact=True).last.fill("Synthetic UI format variant")
    new_offer.get_by_label("Art", exact=True).select_option("option")
    saved(page)
    content = detail(context, base, coach_id)["revision"]["content"]
    check(
        "Native format duration delivery modules variant and family link persist",
        len(content["offerings"]) == 2
        and content["offerings"][0]["duration"]["minutes"] == 210
        and content["offerings"][0]["delivery_mode"] == "hybrid"
        and content["offerings"][0]["program_modules"][0] == "Synthetic edited module"
        and content["offerings"][0]["variants"][0]["title"]
        == "Synthetic edited format option"
        and content["offerings"][1]["family_key"] == family_key
        and content["offerings"][1]["variants"][0]["kind"] == "option",
    )

    # A traditional tab must carry every new field, even if its disclosure is closed.
    before = content
    tab(page, "profile")
    page.get_by_label("Kurzbeschreibung", exact=True).fill(XSS)
    saved(page)
    page.reload(wait_until="domcontentloaded")
    page.get_by_role("button", name="Coach Target Alpha", exact=True).click()
    tab(page, "profile")
    expect(page.get_by_label("Kurzbeschreibung", exact=True)).to_have_value(XSS)
    after = detail(context, base, coach_id)["revision"]["content"]
    check(
        "Legacy profile tab save and reload loses no rich fields",
        all(before[k] == after[k] for k in before if k != "short_intro"),
    )
    check(
        "Short-description XSS sentinel displays literally without execution",
        page.get_by_label("Kurzbeschreibung", exact=True).is_visible()
        and page.locator(WORKSPACE + " img").count() == 0
        and page.evaluate("window.coachTargetXss===undefined"),
    )
    tab(page, "competencies")
    panel(page, "competencies").get_by_label("Kompetenzen", exact=True).fill(
        "Synthetic legacy tab edit"
    )
    saved(page)
    content = detail(context, base, coach_id)["revision"]["content"]
    check(
        "Legacy competencies tab also preserves full target payload",
        all(after[k] == content[k] for k in after if k != "competencies"),
    )

    # Independent native tabs share cookies but retain distinct optimistic versions.
    tab(page, "profile")
    page.get_by_label("Kurzbeschreibung", exact=True).fill("Synthetic unsaved A")
    other = context.new_page()
    try:
        enter(other, base)
        tab(other, "profile")
        other.get_by_label("Kurzbeschreibung", exact=True).fill("Synthetic saved B")
        saved(other)
        page.get_by_role("button", name="Profilentwurf speichern", exact=True).click()
        alert = page.locator(WORKSPACE + " .form-error")
        expect(alert).to_contain_text("Datensatz wurde inzwischen ge\u00e4ndert")
        check(
            "Stale two-tab write preserves unsaved input and focuses alert",
            page.get_by_label("Kurzbeschreibung", exact=True).input_value()
            == "Synthetic unsaved A"
            and alert.evaluate("e=>e===document.activeElement"),
        )
        page.once("dialog", lambda d: d.accept())
        page.get_by_role("button", name="Aktuellen Stand laden", exact=True).click()
        tab(page, "profile")
        expect(page.get_by_label("Kurzbeschreibung", exact=True)).to_have_value(
            "Synthetic saved B"
        )
        check("Conflict reload explicitly recovers persisted content", True)
    finally:
        other.close()

    for key, expected in (
        ("ArrowRight", "profile"),
        ("End", "history"),
        ("Home", "overview"),
        ("ArrowLeft", "history"),
    ):
        if key == "ArrowRight":
            page.locator("#cm-tab-overview").focus()
        page.keyboard.press(key)
        check(
            "Keyboard tab " + key,
            page.locator("#cm-tab-" + expected).evaluate(
                "e=>e===document.activeElement && e.getAttribute('aria-selected')==='true'"
            ),
        )

    data = detail(context, base, coach_id)
    draft_url = WRITE + f"/{coach_id}/revisions/{data['revision']['id']}"
    body = {"expected_version": data["version"], "content": data["revision"]["content"]}
    headers = csrf(context, base)
    for label, altered in (
        ("missing CSRF", {"Origin": base}),
        ("wrong CSRF", {**headers, "X-CSRF-Token": "wrong"}),
        ("foreign Origin", {**headers, "Origin": "https://foreign.example.invalid"}),
    ):
        check(
            label + " denies native target mutation",
            context.request.patch(base + draft_url, data=body, headers=altered).status
            == 403,
        )
    legacy = {
        "display_name": "Coach Target Alpha",
        "short_intro": "Synthetic destructive legacy write",
    }
    check(
        "Legacy API payload cannot downgrade richer revision",
        context.request.patch(
            base + draft_url, headers=headers, data={**body, "content": legacy}
        ).status
        == 409,
    )
    check(
        "Denied requests change no target data or version",
        detail(context, base, coach_id) == data,
    )

    enter(page, base)
    tab(page, "profile")
    page.get_by_label("Kurzbeschreibung", exact=True).fill(
        "Synthetic pending CSRF recovery"
    )

    def corrupt_csrf(route):
        route.continue_(headers={**route.request.headers, "x-csrf-token": "wrong"})

    page.route("**" + draft_url, corrupt_csrf)
    try:
        with page.expect_response(
            lambda response: response.request.method == "PATCH"
            and response.url == base + draft_url
        ) as denied:
            page.get_by_role(
                "button", name="Profilentwurf speichern", exact=True
            ).click()
        expect(page.locator(WORKSPACE + " .form-error")).to_be_visible()
        check(
            "Real CSRF denial preserves draft and focuses UI error",
            denied.value.status == 403
            and page.get_by_label("Kurzbeschreibung", exact=True).input_value()
            == "Synthetic pending CSRF recovery"
            and page.locator(WORKSPACE + " .form-error").evaluate(
                "e=>e===document.activeElement"
            ),
        )
    finally:
        page.unroute("**" + draft_url, corrupt_csrf)
    saved(page)
    check(
        "Explicit save after CSRF recovery persists draft",
        detail(context, base, coach_id)["revision"]["content"]["short_intro"]
        == "Synthetic pending CSRF recovery",
    )

    # Refresh browser after API CSRF rotation, then submit and record real UI evidence.
    enter(page, base)
    tab(page, "profile")
    confirm(page, "Zur Pr\u00fcfung einreichen")
    for label in (
        "Inhalt gepr\u00fcft",
        "Einwilligung belegt",
        "Preview freigegeben",
        "Production freigegeben",
    ):
        tab(page, "publication")
        page.get_by_role("button", name=label, exact=True).click()
        page.get_by_role("dialog").get_by_label("Nachweisreferenz", exact=True).fill(
            "synthetic:browser-approval"
        )
        page.get_by_role("dialog").get_by_role(
            "button", name="Best\u00e4tigen", exact=True
        ).click()
        expect(page.locator(WORKSPACE + " .form-success")).to_have_text("Gespeichert.")
    confirm(page, "Aktivieren")
    data = detail(context, base, coach_id)
    check(
        "Legacy approvals alone cannot authorize target publication",
        not data["capabilities"]["publish"],
    )
    subjects = data["revision"]["evidence_subjects"]
    private = next(s for s in subjects if s["subject_key"] == "qualification-private")
    entry = record_evidence(
        page,
        context,
        base,
        coach_id,
        private,
        "qualification",
        scope="internal_verification",
    )
    check(
        "Native UI records typed internal evidence envelope",
        entry["value"]["scope"] == "internal_verification"
        and entry["value"]["subject_hash"] == private["subject_hash"]
        and entry["recorded_at"]
        and entry["recorded_by"] == str(fixture.users["admin"]),
    )
    family_subject = next(
        s for s in subjects if s["subject_key"] == "family-communication"
    )
    record_evidence(
        page,
        context,
        base,
        coach_id,
        family_subject,
        "protected_source",
        scope="protected_source_content",
    )
    check(
        "Protected-source consent does not replace short-copy consent",
        not detail(context, base, coach_id)["capabilities"]["publish"],
    )
    public_keys = {
        q["key"] for q in data["revision"]["content"]["qualifications"] if q["public"]
    }
    for subject in subjects:
        kind = subject["subject_type"]
        if kind == "qualification" and subject["subject_key"] not in public_keys:
            continue
        for evidence_kind in {
            "profile": ("profile_content", "publication"),
            "qualification": ("qualification",),
            "family": ("offering_content",),
            "offering": ("offering_content",),
            "portrait": ("portrait_asset",),
        }[kind]:
            entry = record_evidence(
                page, context, base, coach_id, subject, evidence_kind
            )
            check(
                "UI persisted preview evidence "
                + kind
                + "/"
                + subject["subject_key"]
                + "/"
                + evidence_kind,
                entry["value"]["kind"] == evidence_kind
                and entry["value"]["environment"] == "preview",
            )
    data = detail(context, base, coach_id)
    check(
        "Exact preview evidence permits only preview",
        data["capabilities"]["publish"] == ["preview"],
    )

    evidence = {
        **data["revision"]["object_evidence"][-1]["value"],
        "key": "bad-hash",
        "subject_hash": "0" * 64,
    }
    evidence_url = WRITE + f"/{coach_id}/revisions/{data['revision']['id']}/evidence"
    headers = csrf(context, base)
    for label, altered in (
        ("wrong object hash", evidence),
        ("unknown evidence field", {**evidence, "unexpected": True}),
    ):
        check(
            label + " rejected by real target API",
            context.request.post(
                base + evidence_url,
                headers=headers,
                data={"expected_version": data["version"], "evidence": altered},
            ).status
            == (409 if label == "wrong object hash" else 400),
        )
    check(
        "Stale evidence cannot append duplicate approval",
        context.request.post(
            base + evidence_url,
            headers=headers,
            data={
                "expected_version": data["version"] - 1,
                "evidence": {**evidence, "subject_hash": subjects[0]["subject_hash"]},
            },
        ).status
        == 409,
    )
    check(
        "Rejected evidence leaves exact version unchanged",
        detail(context, base, coach_id) == data,
    )
    enter(page, base)
    tab(page, "publication")
    confirm(page, "GitHub Preview ver\u00f6ffentlichen")
    preview, production = fixture.projection()
    public = json.dumps(preview)
    check(
        "Real PG public projection exposes only approved preview",
        len(preview["coaches"]) == 1 and not production["coaches"],
    )
    check(
        "Public projection strips internal qualification source evidence and identities",
        all(
            marker not in public
            for marker in (
                "INTERNAL_",
                "PROTECTED_",
                "synthetic:browser",
                "evidence_reference",
                "recorded_by",
                "subject_hash",
                "verification_state",
                str(coach_id),
                str(fixture.users["admin"]),
            )
        ),
    )
    public_coach = preview["coaches"][0]
    check(
        "Public rich families formats variants qualifications survive projection",
        len(public_coach["qualifications"]) == 1
        and len(public_coach["offering_families"]) == 2
        and public_coach["offering_families"][0]["formats"][0]["duration"]["minutes"]
        == 210,
    )
    tab(page, "profile")
    saved(page, "Neue Profilrevision")
    latest = detail(context, base, coach_id)["revision"]
    check(
        "New rich revision copies content but never object evidence",
        latest["content"] == data["revision"]["content"]
        and not latest["object_evidence"],
    )
    tab(page, "qualifications")
    expand(panel(page, "qualifications"))
    check(
        "New revision qualification controls remain editable",
        panel(page, "qualifications")
        .get_by_label("Kanonischer Titel (intern)", exact=True)
        .first.is_enabled(),
    )


def restricted_checks(browser, base, fixture, check):
    for role in ("internal", "coach", "reviewer", "contact"):
        context = browser.new_context(ignore_https_errors=True)
        try:
            page = context.new_page()
            login(page, base, fixture, role)
            status = 403 if role == "internal" else 401
            check(
                role + " has no Admin navigation",
                page.get_by_role("button", name="Coaches", exact=True).count() == 0,
            )
            for path in (
                "/portal/coaches/",
                READ,
                READ + "/" + str(fixture.ids["Alpha"]),
            ):
                check(
                    role + " native read denied " + path.split("/")[-1],
                    context.request.get(base + path).status == status,
                )
            check(
                role + " evidence mutation denied",
                context.request.post(
                    base
                    + WRITE
                    + f"/{fixture.ids['Alpha']}/revisions/{uuid4()}/evidence",
                    data={"expected_version": 1, "evidence": {}},
                ).status
                == status,
            )
        finally:
            context.close()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []
    report = {
        "status": "FAIL",
        "checks": checks,
        "data": "synthetic_only",
        "database_port": 55436,
        "schema": "0001-0009",
        "server_changed": False,
        "database_cleanup": "caller_owned",
        "visual_review": "pending_parent_image_inspection",
        "stage": "preflight",
    }

    def check(label, value):
        report["last_check"] = label
        if not value:
            raise AssertionError(label)
        checks.append(label)
        print("PASS | " + label)

    try:
        fixture = LocalCoachTargetFixture()
        fixture.prepare()
        fixture.seed_states()
        check("Strict loopback55436 fresh schema1-9 preflight and synthetic seed", True)
        spec = importlib.util.spec_from_file_location(
            "cal1_qa", ROOT / "scripts/run-cal1-browser-acceptance.py"
        )
        qa = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(qa)
        with qa.synthetic_server(fixture.app) as base, sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            try:
                context = browser.new_context(
                    ignore_https_errors=True,
                    viewport={"width": 1440, "height": 1000},
                    reduced_motion="reduce",
                )
                try:
                    page = context.new_page()
                    errors = []
                    context.on(
                        "page",
                        lambda new: new.on(
                            "pageerror", lambda error: errors.append(error.name)
                        ),
                    )
                    page.on("pageerror", lambda error: errors.append(error.name))
                    check(
                        "Unauthenticated Admin URL denied",
                        context.request.get(base + "/portal/coaches/").status == 401,
                    )
                    report["stage"] = "native_login"
                    login(page, base, fixture, "admin")
                    expect(
                        page.get_by_role("button", name="Coaches", exact=True)
                    ).to_be_visible()
                    check(
                        "Real native password and MFA enrollment opens Admin Portal",
                        page.get_by_role(
                            "button", name="Coaches", exact=True
                        ).is_visible(),
                    )
                    report["stage"] = "rich_business_workflow"
                    business_checks(page, context, base, fixture, check)
                    report["stage"] = "legacy_upgrade"
                    enter(page, base, "Coach Target Legacy")
                    tab(page, "profile")
                    page.get_by_role(
                        "button", name="Erweiterte Profilfelder aktivieren", exact=True
                    ).click()
                    saved(page)
                    check(
                        "Legacy revision explicitly opts into target1",
                        detail(context, base, fixture.ids["Legacy"])["revision"][
                            "content"
                        ]["target_version"]
                        == 1,
                    )
                    enter(page, base, "Synthetic Coach Epsilon")
                    tab(page, "families")
                    expand(panel(page, "families"))
                    check(
                        "Parent three-family synthetic case renders all families",
                        panel(page, "families")
                        .get_by_label(
                            "Gesch\u00fctzte Quellreferenz (intern)", exact=True
                        )
                        .count()
                        == 3,
                    )
                    tab(page, "offerings")
                    check(
                        "Parent three-family synthetic case renders five formats",
                        panel(page, "offerings").locator(".cm-offering").count() == 5,
                    )
                    report["stage"] = "desktop_geometry"
                    responsive(page, base, "desktop", check)
                    cookies = context.cookies()
                    report["stage"] = "restricted_roles"
                    restricted_checks(browser, base, fixture, check)
                    report["stage"] = "mobile_geometry_keyboard"
                    mobile = browser.new_context(
                        ignore_https_errors=True,
                        viewport={"width": 390, "height": 844},
                        reduced_motion="reduce",
                    )
                    try:
                        mobile.add_cookies(cookies)
                        small = mobile.new_page()
                        small.on("pageerror", lambda error: errors.append(error.name))
                        responsive(small, base, "mobile390", check)
                        small.get_by_role(
                            "button", name="Zur Coachliste", exact=True
                        ).click()
                        create = small.get_by_role(
                            "button", name="Coach anlegen", exact=True
                        )
                        create.focus()
                        small.keyboard.press("Enter")
                        dialog = small.get_by_role("dialog")
                        expect(dialog).to_be_visible()
                        check(
                            "390px modal fits viewport",
                            dialog.evaluate(
                                "e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.height<=innerHeight;}"
                            ),
                        )
                        check(
                            "Keyboard modal focuses display name",
                            dialog.get_by_label("Anzeigename", exact=True).evaluate(
                                "e=>e===document.activeElement"
                            ),
                        )
                        small.keyboard.press("Escape")
                        expect(dialog).not_to_be_visible()
                        check(
                            "Dialog dismissal restores opener focus",
                            create.evaluate("e=>e===document.activeElement"),
                        )
                    finally:
                        mobile.close()
                    report["stage"] = "native_zoom200"
                    with tempfile.TemporaryDirectory(
                        prefix="competencehub-coach3c-zoom-"
                    ) as folder:
                        defaults = Path(folder) / "Default"
                        defaults.mkdir()
                        (defaults / "Preferences").write_text(
                            json.dumps(
                                {
                                    "partition": {
                                        "default_zoom_level": {
                                            "x": math.log(2) / math.log(1.2),
                                            "0": math.log(2) / math.log(1.2),
                                        }
                                    }
                                }
                            ),
                            encoding="utf-8",
                        )
                        zoom = p.chromium.launch_persistent_context(
                            folder,
                            channel="msedge",
                            headless=True,
                            ignore_https_errors=True,
                            no_viewport=True,
                            reduced_motion="reduce",
                            args=[
                                "--window-size=1440,1000",
                                "--force-device-scale-factor=1",
                            ],
                        )
                        try:
                            zoom.add_cookies(cookies)
                            large = zoom.pages[0]
                            large.on(
                                "pageerror", lambda error: errors.append(error.name)
                            )
                            large.goto(
                                base + "/portal/coaches/", wait_until="domcontentloaded"
                            )
                            check(
                                "Actual native Edge 200 percent zoom not CSS emulation",
                                large.evaluate(
                                    "Math.abs(devicePixelRatio-2)<.05 && innerWidth<800 && visualViewport.scale===1"
                                ),
                            )
                            responsive(
                                large, base, "zoom200", check, physical_zoom=True
                            )
                        finally:
                            zoom.close()
                    check(
                        "No auth material in Web Storage",
                        page.evaluate(
                            "localStorage.length===0 && sessionStorage.length===0"
                        ),
                    )
                    check("No JavaScript runtime errors", not errors)
                except Exception:
                    if not page.is_closed() and page.locator(WORKSPACE).is_visible():
                        screenshot(page, OUT / "failure-business-ui.png")
                    raise
                finally:
                    context.close()
            finally:
                browser.close()
        report["stage"] = "complete"
        report["status"] = "PASS"
    except Exception as error:
        # Never echo SQLAlchemy URLs, MFA secrets, response bodies or native tokens.
        report["failure_type"] = type(error).__name__
        report["failure_frames"] = [
            {"file": Path(f.filename).name, "line": f.lineno, "function": f.name}
            for f in traceback.extract_tb(error.__traceback__)[-8:]
        ]
        print(
            "COACH3C_NATIVE_BROWSER=FAIL STAGE="
            + report["stage"]
            + " TYPE="
            + type(error).__name__
        )
        return 1
    finally:
        (OUT / "acceptance.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
    print(f"COACH3C_NATIVE_BROWSER=PASS CHECKS={len(checks)} VISUAL_REVIEW=PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
