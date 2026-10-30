"""Pure synthetic metadata tests. No database, GPG or restore execution/evidence."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "deploy/scripts/verify-prechange-restore-baseline.py"
spec = importlib.util.spec_from_file_location("prechange_restore_baseline", SCRIPT)
assert spec and spec.loader
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


def records(version=6):
    return [
        {
            "kind": "header",
            "format": "competence-hub.prechange.v1",
            "run_id": "synthetic-window",
            "created_at_utc": "20261030T123456Z",
            "database": "competence_hub_staging",
            "recipient": "2E44306121629A100F76A8B08CCA3D9186A28D4C",
            "encryption": "openpgp",
            "role_passwords_included": False,
            "baseline_scope": "all_non_system_schemas",
            "consistency": "exported_mvcc_snapshot",
            "restore_verified": False,
        },
        {
            "kind": "database",
            "name": "competence_hub_staging",
            "owner": "competence_hub_owner",
        },
        {"kind": "migrations", "versions": [f"{i:04d}" for i in range(1, version + 1)]},
        {"kind": "schema", "name": "competence_hub", "owner": "competence_hub_owner"},
        {"kind": "schema", "name": "public", "owner": "pg_database_owner"},
        {
            "kind": "relation",
            "schema": "competence_hub",
            "name": "schema_migrations",
            "relkind": "r",
            "owner": "competence_hub_owner",
        },
        {
            "kind": "relation",
            "schema": "competence_hub",
            "name": "portal_users",
            "relkind": "r",
            "owner": "competence_hub_owner",
        },
        {
            "kind": "table",
            "schema": "competence_hub",
            "name": "schema_migrations",
            "row_count": version,
        },
        {
            "kind": "table",
            "schema": "competence_hub",
            "name": "portal_users",
            "row_count": 0,
        },
    ]


def encode(values):
    return ("\n".join(json.dumps(value) for value in values) + "\n").encode("utf-8")


def restored(values):
    actual = copy.deepcopy(values[1:])
    actual[0]["name"] = "competence_hub_restore_check_synthetic_123"
    return actual


@pytest.mark.parametrize("version", [6, 7, 8, 9])
def test_exact_match_and_canonical_hash_independent_of_record_order(version):
    expected = records(version)
    actual = restored(expected)
    result = baseline.compare(encode(expected), encode(list(reversed(actual))))
    assert result["status"] == "PASS"  # comparator match only, not a restore proof
    assert result["owners_verified"] is True
    assert result["migrations"] == [f"{i:04d}" for i in range(1, version + 1)]
    assert result["row_counts"] == {
        "competence_hub.portal_users": 0,
        "competence_hub.schema_migrations": version,
    }
    assert result["metadata_sha256"] == hashlib.sha256(encode(expected)).hexdigest()
    canonical = baseline.canonical_bytes(
        baseline.parse_baseline(encode(expected), expected=True)
    )
    assert result["baseline_sha256"] == hashlib.sha256(canonical).hexdigest()
    assert set(result) == {
        "schema",
        "status",
        "owners_verified",
        "migrations",
        "row_counts",
        "metadata_sha256",
        "actual_sha256",
        "baseline_sha256",
        "schema_count",
        "relation_count",
        "table_count",
    }
    assert (
        result["schema_count"] == result["relation_count"] == result["table_count"] == 2
    )


def test_validate_metadata_is_early_callable_api_not_restore_evidence():
    data = encode(records())
    value = baseline.validate_metadata(data)
    assert value["status"] == "VALID"
    assert "restore_verified" not in value
    assert (
        value["baseline_sha256"]
        == baseline.compare(data, encode(restored(records())))["baseline_sha256"]
    )


def test_header_is_validated_but_not_in_canonical_baseline_hash():
    first = records()
    second = records()
    second[0]["created_at_utc"] = "20261101T010203Z"
    second[0]["run_id"] = "next-synthetic-window"
    a, b = (baseline.validate_metadata(encode(value)) for value in (first, second))
    assert a["baseline_sha256"] == b["baseline_sha256"]
    assert a["metadata_sha256"] != b["metadata_sha256"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("format", 1),
        ("format", "competence-hub.prechange.v2"),
        ("database", "postgres"),
        ("recipient", "0" * 40),
        ("recipient", baseline.RECIPIENT.lower()),
        ("encryption", "none"),
        ("baseline_scope", "competence_hub_only"),
        ("consistency", "best_effort"),
        ("role_passwords_included", True),
        ("role_passwords_included", 0),
        ("restore_verified", True),
        ("restore_verified", 0),
        ("restore_verified", "false"),
        ("run_id", "../escape"),
        ("run_id", "Upper"),
        ("run_id", "a" * 65),
        ("created_at_utc", "2026-10-30T12:34:56Z"),
        ("created_at_utc", "20260230T123456Z"),
        ("created_at_utc", "20261030T250000Z"),
        ("created_at_utc", "20261030T123456+0100"),
        ("created_at_utc", False),
    ],
)
def test_header_changes_fail_closed(field, value):
    values = records()
    values[0][field] = value
    with pytest.raises(baseline.ContractError):
        baseline.validate_metadata(encode(values))


@pytest.mark.parametrize("value", [True, False, -1, 0.0, "0", None, 2**63, {}, []])
def test_noninteger_or_negative_row_counts_rejected(value):
    values = records()
    values[-1]["row_count"] = value
    with pytest.raises(baseline.ContractError, match="invalid_row_count"):
        baseline.parse_baseline(encode(values), expected=True)


@pytest.mark.parametrize(
    "versions",
    [
        [],
        ["0001"],
        [f"{i:04d}" for i in range(1, 6)],
        [f"{i:04d}" for i in range(1, 11)],
        ["0001", "0002", "0003", "0004", "0005", "0007"],
        ["0001", "0002", "0003", "0004", "0005", "0005"],
        ["0002", "0001", "0003", "0004", "0005", "0006"],
        "0001..0006",
        [1, 2, 3, 4, 5, 6],
    ],
)
def test_migrations_are_contiguous_known_versions(versions):
    values = records()
    values[2]["versions"] = versions
    with pytest.raises(baseline.ContractError, match="invalid_migrations"):
        baseline.parse_baseline(encode(values), expected=True)


@pytest.mark.parametrize(
    "name",
    [
        "x.y",
        "x;DROP TABLE users",
        "x'",
        'x"',
        "x\ny",
        "x\ty",
        "../users",
        "Users",
        "\u00fc",
        "x" * 64,
        "",
        "0users",
        True,
    ],
)
def test_unsafe_sql_identifiers_rejected_even_if_both_inputs_agree(name):
    values = records()
    values[6]["name"] = values[-1]["name"] = name
    with pytest.raises(baseline.ContractError):
        baseline.compare(encode(values), encode(restored(values)))


@pytest.mark.parametrize(
    ("index", "field", "value"),
    [
        (1, "owner", "postgres"),
        (3, "owner", "competence_hub_app"),
        (3, "name", "chatbot"),
        (4, "owner", "foreign_owner"),
        (5, "owner", "competence_hub_migrator"),
        (6, "owner", "chatbot_owner"),
        (6, "schema", "chatbot"),
        (6, "relkind", "f"),
        (6, "relkind", "unknown"),
        (6, "owner", []),
        (6, "relkind", []),
    ],
)
def test_foreign_owners_schemas_and_relation_kinds_fail_closed(index, field, value):
    values = records()
    values[index][field] = value
    with pytest.raises(baseline.ContractError):
        baseline.validate_metadata(encode(values))


@pytest.mark.parametrize("index", range(9))
def test_duplicate_record_of_every_kind_rejected(index):
    values = records()
    values.append(copy.deepcopy(values[index]))
    with pytest.raises(baseline.ContractError):
        baseline.validate_metadata(encode(values))


@pytest.mark.parametrize("index", range(9))
def test_missing_records_rejected(index):
    values = records()
    del values[index]
    with pytest.raises(baseline.ContractError):
        baseline.validate_metadata(encode(values))


@pytest.mark.parametrize(
    "mode",
    [
        "missing_pair",
        "extra_pair",
        "count",
        "migrations",
        "schema_owner",
        "relation_kind",
    ],
)
def test_no_subset_positive_count_or_owner_normalization(mode):
    source = records()
    actual = restored(source)
    if mode == "missing_pair":
        actual = [r for r in actual if r.get("name") != "portal_users"]
    elif mode == "extra_pair":
        actual.extend(
            [
                {
                    "kind": "relation",
                    "schema": "competence_hub",
                    "name": "extra",
                    "relkind": "r",
                    "owner": baseline.OWNER,
                },
                {
                    "kind": "table",
                    "schema": "competence_hub",
                    "name": "extra",
                    "row_count": 0,
                },
            ]
        )
    elif mode == "count":
        actual[-1]["row_count"] = 1
    elif mode == "migrations":
        actual = restored(records(7))
    elif mode == "schema_owner":
        actual[3][
            "owner"
        ] = "postgres"  # allowed public owner, but NOT the source owner
    else:
        actual[5]["relkind"] = "p"
    with pytest.raises(baseline.ContractError, match="baseline_mismatch"):
        baseline.compare(encode(source), encode(actual))


@pytest.mark.parametrize(
    "name",
    [
        "competence_hub_staging",
        "postgres",
        "competence_hub_restore_check_",
        "competence_hub_restore_check_BAD",
        "competence_hub_restore_check_x;drop",
        "competence_hub_restore_check_" + "x" * 50,
    ],
)
def test_actual_requires_owned_isolated_database_name(name):
    actual = restored(records())
    actual[0]["name"] = name
    with pytest.raises(baseline.ContractError, match="invalid_database_name"):
        baseline.compare(encode(records()), encode(actual))


def test_explicit_current_staging_mode_is_match_not_restore_pass():
    data = encode(records())
    actual = encode(records()[1:])
    with pytest.raises(baseline.ContractError, match="invalid_database_name"):
        baseline.compare(data, actual)
    assert baseline.compare(data, actual, current=True)["status"] == "MATCH"
    with pytest.raises(baseline.ContractError, match="invalid_database_name"):
        baseline.compare(data, encode(restored(records())), current=True)
    assert "current_database() = 'competence_hub_staging'" in baseline.query_sql(
        current=True
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown",
        "extra_field",
        "missing_field",
        "duplicate_json_key",
        "nonfinite",
        "blank",
        "empty",
        "bom",
        "array",
        "invalid_utf8",
        "header_actual",
        "misplaced_header",
    ],
)
def test_strict_jsonl_format(mutation):
    source = records()
    data = encode(source)
    if mutation == "unknown":
        source.append({"kind": "auth_secret", "payload": "NEVER_ECHO"})
        data = encode(source)
    elif mutation == "extra_field":
        source[-1]["password"] = "NEVER_ECHO"
        data = encode(source)
    elif mutation == "missing_field":
        del source[-1]["row_count"]
        data = encode(source)
    elif mutation == "duplicate_json_key":
        data = data.replace(b'"row_count": 0', b'"row_count": 0, "row_count": 0')
    elif mutation == "nonfinite":
        data = data.replace(b'"row_count": 0', b'"row_count": NaN')
    elif mutation == "blank":
        data += b"\n"
    elif mutation == "empty":
        data = b""
    elif mutation == "bom":
        data = b"\xef\xbb\xbf" + data
    elif mutation == "array":
        data += b"[]\n"
    elif mutation == "invalid_utf8":
        data += b"\xff\n"
    elif mutation == "header_actual":
        with pytest.raises(baseline.ContractError):
            baseline.parse_baseline(data, expected=False)
        return
    else:
        source[0], source[1] = source[1], source[0]
        data = encode(source)
    with pytest.raises(baseline.ContractError):
        baseline.parse_baseline(data, expected=True)


def test_size_limits_and_migration_count_consistency():
    with pytest.raises(baseline.ContractError):
        baseline.validate_metadata(b"x" * (baseline.MAX_BYTES + 1))
    source = records()
    source[-2]["row_count"] = 5
    with pytest.raises(baseline.ContractError, match="migration_count_mismatch"):
        baseline.validate_metadata(encode(source))


def test_sequence_view_materialized_and_partition_coverage():
    values = records()
    for name, kind in [
        ("seq", "S"),
        ("view", "v"),
        ("materialized", "m"),
        ("partitioned", "p"),
    ]:
        values.append(
            {
                "kind": "relation",
                "schema": "competence_hub",
                "name": name,
                "relkind": kind,
                "owner": baseline.OWNER,
            }
        )
        if kind in {"m", "p"}:
            values.append(
                {
                    "kind": "table",
                    "schema": "competence_hub",
                    "name": name,
                    "row_count": 0,
                }
            )
    assert (
        baseline.compare(encode(values), encode(restored(values)))["table_count"] == 4
    )


def test_query_reuses_pinned_producer_sql_and_never_executes_it(monkeypatch):
    query = baseline.query_sql()
    assert "READ ONLY" in query and "ON_ERROR_STOP on" in query and "\\gexec" in query
    assert "pg_get_userbyid" in query and "count(*)" in query
    assert "BASELINE_END" not in query and "pg_export_snapshot" not in query
    assert "INSERT " not in query and "UPDATE " not in query and "DELETE " not in query
    assert "^competence_hub_restore_check_[a-z0-9_]+$" in query
    monkeypatch.setattr(baseline, "SQL_BODY_SHA256", "0" * 64)
    with pytest.raises(baseline.ContractError, match="unapproved_producer_sql"):
        baseline.query_sql()


def test_regular_file_reader_rejects_symlink_metadata_without_os_symlink_permission(
    tmp_path, monkeypatch
):
    file = tmp_path / "METADATA"
    file.write_bytes(encode(records()))
    original = Path.lstat

    def lstat(path):
        return (
            SimpleNamespace(st_mode=stat.S_IFLNK, st_file_attributes=0)
            if path == file
            else original(path)
        )

    monkeypatch.setattr(Path, "lstat", lstat)
    with pytest.raises(baseline.ContractError, match="unsafe_input_path"):
        baseline.regular_bytes(file)


def test_cli_compare_validate_query_and_sanitized_failure(tmp_path):
    expected = tmp_path / "METADATA"
    actual = tmp_path / "actual.jsonl"
    expected.write_bytes(encode(records()))
    actual.write_bytes(encode(restored(records())))

    def run(*args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            capture_output=True,
            text=True,
            timeout=10,
        )

    result = run("compare", "--expected", expected, "--actual", actual)
    assert result.returncode == 0 and json.loads(result.stdout)["status"] == "PASS"
    validated = run("validate", "--expected", expected)
    assert (
        validated.returncode == 0 and json.loads(validated.stdout)["status"] == "VALID"
    )
    query = run("query")
    assert query.returncode == 0 and query.stdout.startswith("\\set ON_ERROR_STOP on")
    actual.write_bytes(b'{"kind":"NEVER_ECHO"}\n')
    failed = run("compare", "--expected", expected, "--actual", actual)
    assert failed.returncode == 1 and failed.stdout == ""
    assert json.loads(failed.stderr)["status"] == "FAIL"
    assert "NEVER_ECHO" not in failed.stderr
    missing = run("compare", "--expected", tmp_path / "NEVER_ECHO", "--actual", actual)
    assert missing.returncode == 1 and "NEVER_ECHO" not in missing.stderr
