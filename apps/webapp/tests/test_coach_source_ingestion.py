"""Synthetic-only incremental source/annex policy. No real sources or network."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import socket
import sys
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[3]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


ingestion = module("coach_source_ingestion")
reconciliation = module("coach_source_reconciliation")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("source tests must stay offline")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)


def inputs():
    identity = {"source_system": "synthetic", "source_key": "coach/one"}
    frozen = {
        "coaches": [
            {
                "source_identity": (
                    identity
                    if i == 0
                    else {"source_system": "synthetic", "source_key": f"coach/{i + 1}"}
                ),
                "mapping_status": "READY",
            }
            for i in range(9)
        ],
        "counts": {"coaches": 9, "public_qualifications": 2},
    }
    inventory = {
        "files": [
            {
                "relative_path": "synthetic.pdf",
                "sha256": "1" * 64,
                "change": "NEW",
                "technically_readable": True,
            },
            {
                "relative_path": "supplement.docx",
                "sha256": "2" * 64,
                "change": "MODIFIED",
                "technically_readable": True,
            },
        ]
    }
    review = {
        "scope": "PRIVATE_INCREMENTAL_ANNEX_FROZEN_SHORT_SCOPE_UNCHANGED",
        "source_identity": identity,
        "identity": {
            "existing_source_identity_confirmed": True,
            "new_coach": False,
            "real_uuid_allocated": False,
            "route_change": False,
        },
        "relationship": "SUPPLEMENTS",
        "source_files": [
            {
                "key": "pdf",
                "relative_path": "synthetic.pdf",
                "sha256": "1" * 64,
                "physical_pages": 2,
                "classification": ["COACH_PROFILE", "COACH_OFFERING"],
                "relationship": "SUPPLEMENTS",
            },
            {
                "key": "docx",
                "relative_path": "supplement.docx",
                "sha256": "2" * 64,
                "classification": ["COACH_OFFERING"],
                "relationship": "SUPPLEMENTS",
            },
        ],
        "publication": {
            **{
                k: "UNKNOWN"
                for k in (
                    "profile_content",
                    "portrait_asset",
                    "new_qualification_labels",
                    "offering_content",
                    "preview",
                    "production",
                )
            },
            "evidence_created": False,
        },
        "profile_delta": {
            "roles": [
                {
                    "key": "speaker",
                    "label": "Synthetic speaker",
                    "verification": "source_asserted",
                    "public_approval": "UNKNOWN",
                }
            ],
            "qualification_review": {
                "automatic_background_to_qualification_conversion": False
            },
            "automatic_taxonomy_changes": False,
        },
        "qualification_candidates": [
            {
                "key": "training",
                "canonical_title": "Synthetic source assertion",
                "issuer": None,
                "source": "pdf",
                "status": "SOURCE_ASSERTED_REVIEW_ONLY",
                "public": False,
            }
        ],
        "assets": {"portrait_replaced": False, "reuse_approval": "UNKNOWN"},
        "families": [
            {"key": "family", "title": "Synthetic family", "formats": ["format"]}
        ],
        "formats": [
            {
                "key": "format",
                "family": "family",
                "source": "pdf",
                "pages": [2],
                "type": "workshop",
                "delivery_mode": "unknown",
                "duration": None,
                "status": "UNAPPROVED_PUBLIC_CANDIDATE",
            }
        ],
        "clarifications": [
            {
                "key": "legal",
                "kind": "CONTRACT_GAP",
                "subjects": ["format"],
                "required_for_current_short_scope": False,
                "status": "DEFERRED_NOT_IMPORTED",
            }
        ],
        "excluded": {
            "raw_values_copied_to_registry_or_public_artifacts": False,
            "private_customer_business_information_present": True,
            "private_contact_information_present": True,
            "internal_price_present": True,
        },
        "scope_impact": {
            "canonical_field_loss": 0,
            "new_annex_items_not_imported": True,
            "frozen_manifest_change": False,
            "public_projection_change": False,
            "new_customer_or_finance_module": False,
        },
        "private_note": "SYNTHETIC_PRICE_CUSTOMER_CONTACT_WORKSHEET_DO_NOT_EXPORT",
    }
    return review, frozen, inventory


def test_incremental_bytes_not_modified_timestamp_or_name_similarity():
    records = [
        {"relative_path": "known.pdf", "sha256": "a", "modified_utc": "new timestamp"},
        {"relative_path": "modified.docx", "sha256": "b"},
        {"relative_path": "renamed.pdf", "sha256": "a"},
    ]
    result = ingestion.diff_inventory(
        records, {"known.pdf": "a", "modified.docx": "c", "removed.pdf": "d"}
    )
    assert {r["relative_path"]: r["change"] for r in result["files"]} == {
        "known.pdf": "UNCHANGED",
        "modified.docx": "MODIFIED",
        "renamed.pdf": "NEW",
    }
    assert result["removed"] == ["removed.pdf"]
    with pytest.raises(ValueError, match="duplicate"):
        ingestion.diff_inventory([records[0], records[0]], {})


def test_unchanged_bytes_never_reparsed_or_extracted(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    path = source / "known.pdf"
    path.write_bytes(b"synthetic known bytes")

    def forbidden(*args, **kwargs):
        pytest.fail("unchanged source was reinterpreted")

    monkeypatch.setattr(ingestion, "technical_check", forbidden)
    report = ingestion.inventory(
        source, {"known.pdf": ingestion.digest(path.read_bytes())}
    )
    assert report["files"][0]["change"] == "UNCHANGED"
    assert report["files"][0]["technical_check"] == "KNOWN_PROCESSED_HASH_MATCH"
    monkeypatch.setattr(ingestion.subprocess, "run", forbidden)
    ingestion.extract_changed(source, report, tmp_path / "extract")
    assert list((tmp_path / "extract").iterdir()) == []


def test_docx_structured_text_keeps_table_order_and_refuses_declarations(tmp_path):
    path = tmp_path / "synthetic.docx"
    body = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Heading</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Table row</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", body)
    assert ingestion.docx_text(path) == "Heading\nTable row"
    with ZipFile(path, "w") as archive:
        archive.writestr(
            "word/document.xml", '<!DOCTYPE x [<!ENTITY data "boom">]>' + body
        )
    with pytest.raises(ValueError, match="declarations"):
        ingestion.docx_text(path)


def test_unreadable_docx_and_credential_type_fail_closed(tmp_path):
    path = tmp_path / "bad.docx"
    path.write_bytes(b"not a zip archive")
    assert ingestion.technical_check(path, ".docx")[0] is False
    report = ingestion.inventory(tmp_path, {})
    assert report["files"][0]["technically_readable"] is False
    path.unlink()
    (tmp_path / ".env").write_text("SYNTHETIC_NOT_A_SECRET")
    with pytest.raises(ValueError, match="unsupported"):
        ingestion.inventory(tmp_path, {})


@pytest.mark.parametrize(
    "path", ["../escape.pdf", "/absolute.pdf", "C:/private.pdf", "folder\\file.pdf"]
)
def test_baseline_paths_cannot_expand_source_access(tmp_path, path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "scope": "PROCESSED_SOURCE_BYTES_NOT_PUBLICATION_APPROVAL",
                "files": [{"relative_path": path, "sha256": "a" * 64}],
            }
        )
    )
    with pytest.raises(ValueError):
        ingestion.load_baseline(baseline)


def test_annex_preserves_short_scope_counts_and_excludes_raw_private_material():
    review, frozen, inventory = inputs()
    before = deepcopy((review, frozen, inventory))
    result = reconciliation.evaluate(review, frozen, inventory)
    assert result["mapping_status_counts"] == {
        "READY": 9,
        "REVIEW_REQUIRED": 0,
        "BLOCKED": 0,
    }
    assert result["existing_counts_unchanged"] == frozen["counts"]
    assert result["contract_gaps_not_imported"] == 1
    assert result["new_publication_approvals"] == 0
    assert "DO_NOT_EXPORT" not in json.dumps(result)
    assert result["scope"] == "PRIVATE_REVIEW_ANNEX_NOT_EXECUTABLE"
    assert (review, frozen, inventory) == before
    assert result == reconciliation.evaluate(review, frozen, inventory)


@pytest.mark.parametrize(
    "field",
    [
        "profile_content",
        "portrait_asset",
        "new_qualification_labels",
        "offering_content",
        "preview",
        "production",
        "evidence_created",
    ],
)
def test_new_source_or_old_preview_never_becomes_new_approval(field):
    review, frozen, inventory = inputs()
    review["publication"][field] = True if field == "evidence_created" else "APPROVED"
    with pytest.raises(ValueError):
        reconciliation.evaluate(review, frozen, inventory)


@pytest.mark.parametrize("field", ["new_coach", "real_uuid_allocated", "route_change"])
def test_new_coach_or_inferred_mapping_is_not_smuggled_into_nine(field):
    review, frozen, inventory = inputs()
    review["identity"][field] = True
    with pytest.raises(ValueError):
        reconciliation.evaluate(review, frozen, inventory)


@pytest.mark.parametrize(
    "fault",
    [
        "unbound-file",
        "hash",
        "unreadable",
        "classification",
        "orphan-format",
        "duplicate-format",
        "page-77",
        "public-format",
        "field-loss",
        "portrait",
        "public-qualification",
        "credential-inference",
        "automatic-topic",
    ],
)
def test_bad_binding_mapping_or_data_promotion_rejected(fault):
    review, frozen, inventory = inputs()
    if fault == "unbound-file":
        review["source_files"].pop()
    elif fault == "hash":
        review["source_files"][0]["sha256"] = "f" * 64
    elif fault == "unreadable":
        inventory["files"][0]["technically_readable"] = False
    elif fault == "classification":
        review["source_files"][0]["classification"] = ["APPROVED"]
    elif fault == "orphan-format":
        review["formats"][0]["family"] = "missing"
    elif fault == "duplicate-format":
        review["formats"].append(deepcopy(review["formats"][0]))
    elif fault == "page-77":
        review["formats"][0]["pages"] = [77]
    elif fault == "public-format":
        review["formats"][0]["status"] = "READY"
    elif fault == "field-loss":
        review["scope_impact"]["canonical_field_loss"] = 1
    elif fault == "portrait":
        review["assets"]["portrait_replaced"] = True
    elif fault == "public-qualification":
        review["qualification_candidates"][0]["public"] = True
    elif fault == "credential-inference":
        review["profile_delta"]["qualification_review"][
            "automatic_background_to_qualification_conversion"
        ] = True
    else:
        review["profile_delta"]["automatic_taxonomy_changes"] = True
    with pytest.raises(ValueError):
        reconciliation.evaluate(review, frozen, inventory)


@pytest.mark.parametrize(
    "kind,expected", [("CONTRACT_GAP", "BLOCKED"), ("CONFLICT", "REVIEW_REQUIRED")]
)
def test_required_uncertainty_cannot_still_report_nine_ready(kind, expected):
    review, frozen, inventory = inputs()
    review["clarifications"][0].update(kind=kind, required_for_current_short_scope=True)
    result = reconciliation.evaluate(review, frozen, inventory)
    assert result["mapping_status_counts"][expected] == 1
    assert result["mapping_status_counts"]["READY"] == 8


def test_removed_processed_source_requires_explicit_review_not_silent_success():
    review, frozen, inventory = inputs()
    inventory["removed"] = ["synthetic-old.pdf"]
    with pytest.raises(ValueError, match="removed"):
        reconciliation.evaluate(review, frozen, inventory)


def test_changed_source_during_extraction_never_publishes_text(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    path = source / "synthetic.docx"
    path.write_bytes(b"before")
    report = {
        "files": [
            {
                "relative_path": "synthetic.docx",
                "change": "NEW",
                "type": "docx",
                "technically_readable": True,
                "sha256": ingestion.digest(b"before"),
            }
        ]
    }

    def mutate(path):
        path.write_bytes(b"after")
        return "SYNTHETIC_PRIVATE_TEXT"

    monkeypatch.setattr(ingestion, "docx_text", mutate)
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="during extraction"):
        ingestion.extract_changed(source, report, output)
    assert list(output.iterdir()) == []


def test_verification_checks_receipt_path_before_read(tmp_path, monkeypatch):
    monkeypatch.setattr(ingestion, "ROOT", tmp_path)
    checked = []

    def guard(path):
        checked.append(path)
        if path.name == "inventory.json":
            raise ValueError("linked metadata forbidden")

    def denied(*args, **kwargs):
        pytest.fail("receipt read before its link guard")

    monkeypatch.setattr(ingestion, "no_links", guard)
    monkeypatch.setattr(Path, "read_text", denied)
    with pytest.raises(ValueError, match="linked metadata"):
        ingestion.main(["--verify-existing"])
    assert checked[-1].name == "inventory.json"
