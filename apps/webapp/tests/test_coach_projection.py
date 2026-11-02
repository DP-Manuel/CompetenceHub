from copy import deepcopy
import hashlib
import json

import pytest

from competence_hub_api.portal.coach_projection import (
    canonical_bytes,
    generate_projection,
    projection_diff,
    projection_parity,
    read_projection,
    registry_safety_report,
    review_markdown,
    validate_projection,
    verify_assets,
    write_projection,
    checked_local_path,
)
from competence_hub_api.portal.coach_registry import RegistryConflict
from scripts.coach_projection_fixture import (
    ASSET_REFERENCE,
    PORTRAIT,
    synthetic_registry,
)


def projection(mode="preview"):
    return generate_projection(synthetic_registry(), mode)


def test_preview_production_unknown_and_inactive_fail_closed():
    preview, production = projection(), projection("production")
    assert len(preview["coaches"]) == 2 and len(production["coaches"]) == 1
    assert preview != production
    assert all(
        "Unknown" not in c["display_name"] and "Inactive" not in c["display_name"]
        for c in preview["coaches"]
    )
    with pytest.raises(ValueError):
        generate_projection(synthetic_registry(), "staging")
    registry = synthetic_registry()
    registry[1].publications["production"] = deepcopy(
        registry[0].publications["production"]
    )
    registry[1].publications["production"].revision_id = registry[1].revisions[0].id
    with pytest.raises(RegistryConflict):
        generate_projection(registry, "production")


def test_public_allowlist_grouping_and_missing_portrait():
    output = projection()
    a, b = output["coaches"]
    assert a["assets"] and b["assets"] == []
    assert a["offerings"] == []
    assert len(a["offering_families"]) == 1
    assert len(a["offering_families"][0]["formats"]) == 2
    assert len(a["offering_families"][0]["formats"][0]["variants"]) == 1
    assert len(a["qualifications"]) == 1
    text = canonical_bytes(output).decode()
    for private in (
        "PRIVATE",
        "private:",
        "verification_state",
        "internal_note",
        "evidence_reference",
        "source_path",
        "protected_source",
        "actor_id",
        "00000000-0000",
        "price",
    ):
        assert private not in text


def test_unknown_or_rejected_production_object_evidence_blocks_export():
    from dataclasses import replace

    for decision in ("unknown", "rejected"):
        registry = synthetic_registry()
        revision = registry[0].revisions[0]
        index = next(
            i
            for i, e in enumerate(revision.object_evidence)
            if e.value.environment == "production"
        )
        original = revision.object_evidence[index]
        revision.object_evidence[index] = replace(
            original, value=original.value.model_copy(update={"status": decision})
        )
        with pytest.raises(RegistryConflict):
            generate_projection(registry, "production")
        assert len(generate_projection(registry, "preview")["coaches"]) == 2


def test_multiple_public_qualifications_and_nonbookable_therapy():
    from scripts.coach_target_cases import approvals_for
    from competence_hub_api.portal.coach_registry import ObjectEvidence
    from scripts.coach_projection_fixture import ACTOR, NOW
    from uuid import uuid4

    registry = synthetic_registry()
    r = registry[0].revisions[0]
    p = r.content.model_dump(mode="json")
    p["qualifications"][1].update(
        public=True, public_display_label="Second public label"
    )
    p["offerings"].append(
        dict(
            key="therapy",
            title="Synthetic psychotherapy boundary",
            type="other",
            ordering=3,
            service_domains=["psychotherapy"],
            bookable=False,
        )
    )
    r.content = type(r.content).model_validate(p)
    r.object_evidence = [
        ObjectEvidence(uuid4(), e, ACTOR, NOW) for e in approvals_for(r)
    ]
    output = generate_projection(registry, "preview")["coaches"][0]
    assert len(output["qualifications"]) == 2
    assert output["offerings"][0]["bookable"] is False


def test_deterministic_bytes_and_no_timestamps():
    registry = synthetic_registry()
    first = canonical_bytes(generate_projection(registry, "preview"))
    for _ in range(3):
        assert first == canonical_bytes(
            generate_projection(tuple(reversed(deepcopy(registry))), "preview")
        )
    assert b"2026-" not in first


def test_local_paths_reject_escape_and_reparse_before_access(tmp_path, monkeypatch):
    import stat
    from pathlib import Path
    from types import SimpleNamespace

    outside = tmp_path.parent / "escape.json"
    with pytest.raises(ValueError, match="outside"):
        checked_local_path(outside, root=tmp_path)
    child = tmp_path / "linked" / "image.png"
    original = Path.lstat

    def lstat(path):
        if path == tmp_path / "linked":
            return SimpleNamespace(
                st_mode=stat.S_IFDIR,
                st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT,
            )
        return original(path)

    monkeypatch.setattr(Path, "lstat", lstat)
    with pytest.raises(ValueError, match="linked/reparse"):
        checked_local_path(child, root=tmp_path)
    assert not child.exists() and not outside.exists()


def test_cli_parity_mismatch_fails_process_and_reparse_precedes_fixture_io(
    tmp_path, monkeypatch, capsys
):
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "coach_projection_cli",
        Path(__file__).resolve().parents[1] / "scripts/coach-projection.py",
    )
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    a, b = projection(), projection()
    b["coaches"][0]["short_intro"] = "Changed synthetic intro"
    monkeypatch.setattr(
        cli, "read_projection", lambda path: a if str(path) == "a.json" else b
    )
    monkeypatch.setattr(cli, "checked_local_path", lambda path, **kwargs: Path(path))
    output = tmp_path / "report.json"
    assert (
        cli.main(
            [
                "parity",
                "--current",
                "a.json",
                "--candidate",
                "b.json",
                "--output",
                str(output),
            ]
        )
        == 1
    )
    assert "DIFFERENT" in capsys.readouterr().out
    calls = []

    def deny(path, **kwargs):
        calls.append(path)
        raise ValueError("linked/reparse")

    monkeypatch.setattr(cli, "checked_local_path", deny)

    def forbidden(*args, **kwargs):
        pytest.fail("fixture I/O before path validation")

    monkeypatch.setattr(Path, "mkdir", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    with pytest.raises(ValueError, match="linked/reparse"):
        cli.main(
            [
                "synthetic",
                "--environment",
                "preview",
                "--output",
                str(tmp_path / "out.json"),
                "--assets",
                str(tmp_path / "assets"),
            ]
        )
    assert calls


def test_native_linked_fixture_output_never_writes_outside_workspace(
    tmp_path, monkeypatch
):
    import importlib.util
    import os
    from pathlib import Path
    import subprocess

    script = Path(__file__).resolve().parents[1] / "scripts/coach-projection.py"
    spec = importlib.util.spec_from_file_location(
        "coach_projection_native_link_cli", script
    )
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    # Give the CLI an owned synthetic repository; no real project/output touched.
    monkeypatch.setattr(
        cli, "__file__", str(tmp_path / "apps/webapp/scripts/coach-projection.py")
    )
    root = tmp_path / ".tmp/coach4"
    root.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "sentinel.txt"
    sentinel.write_text("untouched")
    link = root / "linked"
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
            check=True,
            capture_output=True,
        )
    else:
        link.symlink_to(outside, target_is_directory=True)
    for output, assets in (
        (link / "out.json", root / "assets"),
        (root / "out.json", link / "assets"),
    ):
        with pytest.raises(ValueError, match="linked/reparse"):
            cli.main(
                [
                    "synthetic",
                    "--environment",
                    "preview",
                    "--output",
                    str(output),
                    "--assets",
                    str(assets),
                ]
            )
        assert list(outside.iterdir()) == [sentinel]
        assert sentinel.read_text() == "untouched"
        assert not (root / "out.json").exists()


@pytest.mark.parametrize(
    "path",
    [
        "/coaches/../x/",
        "https://evil.invalid/",
        "/coaches/%2e%2e/",
        "/coaches/test/?x=1",
        "/coaches/a\\b/",
    ],
)
def test_path_injection_rejected(path):
    value = projection()
    value["coaches"][0]["profile_path"] = path
    with pytest.raises(ValueError):
        validate_projection(value)


@pytest.mark.parametrize("value", [None, [], {"schema": True}, {"schema": "1"}])
def test_root_requires_exact_json_object_and_integer_schema(value):
    with pytest.raises(ValueError):
        validate_projection(value)


@pytest.mark.parametrize(
    "target,field",
    [
        ("root", "evidence"),
        ("coach", "source_path"),
        ("asset", "private_contact"),
        ("qualification", "verification_state"),
        ("format", "price"),
        ("family", "protected_source_text"),
        ("variant", "worksheet"),
    ],
)
def test_nested_allowlist_rejects_leaks(target, field):
    value = projection()
    coach = value["coaches"][0]
    targets = {
        "root": value,
        "coach": coach,
        "asset": coach["assets"][0],
        "qualification": coach["qualifications"][0],
        "family": coach["offering_families"][0],
        "format": coach["offering_families"][0]["formats"][0],
        "variant": coach["offering_families"][0]["formats"][0]["variants"][0],
    }
    targets[target][field] = "PRIVATE"
    with pytest.raises(ValueError):
        validate_projection(value)


@pytest.mark.parametrize(
    "reference",
    [
        "../private.key",
        "images/coaches/a.svg",
        "images/coaches/%2f.png",
        "images/coaches/a.png/extra",
        "C:/private.png",
    ],
)
def test_unsafe_asset_reference_rejected(reference):
    value = projection()
    value["coaches"][0]["assets"][0]["reference"] = reference
    with pytest.raises(ValueError):
        validate_projection(value)


def test_asset_hash_exact_exclusive_file_and_duplicate_json(tmp_path):
    value = projection()
    asset = tmp_path / ASSET_REFERENCE
    asset.parent.mkdir(parents=True)
    asset.write_bytes(PORTRAIT)
    output = tmp_path / "preview.json"
    digest = write_projection(value, output, asset_root=tmp_path)
    assert digest == hashlib.sha256(output.read_bytes()).hexdigest()
    assert read_projection(output, "preview") == value
    with pytest.raises(FileExistsError):
        write_projection(value, output, asset_root=tmp_path)
    with pytest.raises(ValueError):
        read_projection(output, "production")
    asset.write_bytes(b"wrong")
    with pytest.raises(ValueError):
        verify_assets(value, tmp_path)
    output.write_text('{"schema":1,"schema":1}')
    with pytest.raises(ValueError, match="duplicate"):
        read_projection(output)


def test_diff_attention_and_parity_dimensions():
    a = projection()
    b = deepcopy(a)
    coach = b["coaches"][0]
    coach["assets"][0]["sha256"] = "0" * 64
    coach["topics"][0]["name"] = "Changed topic"
    coach["offering_families"][0]["boundaries"][0]["text"] = "Changed boundary"
    coach["offerings"] = [
        dict(
            title="Therapy",
            type="other",
            ordering=4,
            description=None,
            service_domains=["psychotherapy"],
            bookable=False,
        )
    ]
    b["coaches"][1]["profile_path"] = "/coaches/renamed/"
    report = projection_diff(a, b)
    assert (
        report["changed_assets"]
        and report["changed_topics"]
        and report["changed_offerings"]
        and report["changed_routes"]
    )
    assert {x["code"] for x in report["high_attention"]} >= {
        "PORTRAIT_CHANGED",
        "OFFERING_BOUNDARY_CHANGED",
        "THERAPEUTIC_CONTENT_CHANGED",
        "NEW_COACH_OR_ROUTE",
        "REMOVED_COACH_OR_ROUTE",
    }
    assert "High Attention" in review_markdown(report)
    assert projection_parity(a, a)["status"] == "PASS"
    parity = projection_parity(a, b)
    assert parity["status"] == "DIFFERENT"
    assert set(parity["checks"]) == {
        "coach_count",
        "routes",
        "names",
        "topics",
        "categories",
        "qualifications",
        "offerings",
        "assets",
        "boundaries",
        "full_public_dto",
    }


def test_production_visibility_and_private_approval_changes():
    registry = synthetic_registry()
    a = generate_projection(registry, "production")
    changed = deepcopy(registry)
    changed[0].revisions[0].approvals = []
    report = registry_safety_report(registry, changed)
    assert report["high_attention"][0]["code"] == "PRODUCTION_APPROVAL_LOST"
    assert "00000000" not in json.dumps(report)
    empty = {"schema": 1, "environment": "production", "coaches": []}
    diff = projection_diff(a, empty)
    assert "PRODUCTION_VISIBILITY_CHANGED_VERIFY_APPROVAL" in {
        x["code"] for x in diff["high_attention"]
    }


def test_lifecycle_removal_and_same_identity_fresh_reactivation():
    registry = synthetic_registry()
    old_id = registry[0].id
    registry[0].lifecycle = "paused"
    assert len(generate_projection(registry, "preview")["coaches"]) == 1
    registry[0].lifecycle = "inactive"
    assert len(generate_projection(registry, "preview")["coaches"]) == 1
    registry[0].lifecycle = "active"
    registry[0].publication_floor = 1
    with pytest.raises(RegistryConflict):
        generate_projection(registry, "preview")
    # Domain lifecycle tests separately prove fresh revisions/approvals. Never
    # treat a manual active flag as sufficient to undo the publication floor.
    assert registry[0].id == old_id


@pytest.mark.anyio
async def test_domain_offboard_return_requires_fresh_revision_and_keeps_identity():
    from scripts.coach_target_cases import approvals_for
    from test_coach_target import rich_ready
    from test_coach_registry import change

    service, coach = await rich_ready()
    identity = coach.id
    original = coach.revisions[-1]
    for evidence in approvals_for(original):
        coach = await change(
            service, coach, "evidence", revision_id=original.id, evidence=evidence
        )
    coach = await change(
        service, coach, "publish", revision_id=original.id, environment="preview"
    )
    assert len(generate_projection((coach,), "preview")["coaches"]) == 1
    for lifecycle in ("paused", "inactive"):
        coach = await change(service, coach, "lifecycle", lifecycle=lifecycle)
        assert generate_projection((coach,), "preview")["coaches"] == []
    with pytest.raises(RegistryConflict):
        await change(service, coach, "lifecycle", lifecycle="active")
    coach = await change(service, coach, "revision", content=original.content)
    fresh = coach.revisions[-1]
    assert not fresh.approvals and not fresh.object_evidence
    coach = await change(service, coach, "submit", revision_id=fresh.id)
    for kind in ("content_review", "person_consent", "preview"):
        coach = await change(
            service,
            coach,
            "approve",
            revision_id=fresh.id,
            kind=kind,
            evidence_ref="synthetic:return",
        )
    for evidence in approvals_for(fresh):
        coach = await change(
            service, coach, "evidence", revision_id=fresh.id, evidence=evidence
        )
    coach = await change(service, coach, "lifecycle", lifecycle="active")
    coach = await change(
        service, coach, "publish", revision_id=fresh.id, environment="preview"
    )
    assert coach.id == identity and len(coach.revisions) == 2
    assert len(generate_projection((coach,), "preview")["coaches"]) == 1
    assert generate_projection((coach,), "production")["coaches"] == []
