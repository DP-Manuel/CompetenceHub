#!/usr/bin/env python3
"""Offline prechange v1 validation; never executes SQL, GPG or a restore.

CLI: query -> canonical read-only psql script on stdout (no header/sentinel).
CLI: compare --expected METADATA --actual restored.jsonl -> JSON on stdout.
CLI: validate --expected METADATA -> VALID/header validation only, never PASS.
Exit 0/PASS means only that the supplied baselines match, NOT a restore proof.
Only the supervising operator can bind bytes to an actual restore and cleanup.
Canonical hash: SHA256(UTF8(json.dumps(sorted non-header records, sort_keys=True,
separators=(',', ':'), ensure_ascii=True))). Records sort by kind/schema/name;
only the restored database name becomes competence_hub_staging before hashing.
No timestamp freshness/window approval is inferred from a valid header date.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

DATABASE = "competence_hub_staging"
RECIPIENT = "2E44306121629A100F76A8B08CCA3D9186A28D4C"
OWNER = "competence_hub_owner"
MAX_BYTES = 8 * 1024 * 1024
MAX_RECORDS = 10000
IDENTIFIER = re.compile(r"[a-z_][a-z0-9_]{0,62}\Z", re.ASCII)
RESTORE_NAME = re.compile(r"competence_hub_restore_check_[a-z0-9_]+\Z", re.ASCII)
RUN_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z", re.ASCII)
SQL_BODY_SHA256 = "0a69beef77eb37ff128d87ba2a649a8febae09776ea044b783f0ccc5513289e5"
FIELDS = {
    "header": {
        "kind",
        "format",
        "run_id",
        "created_at_utc",
        "database",
        "recipient",
        "encryption",
        "role_passwords_included",
        "baseline_scope",
        "consistency",
        "restore_verified",
    },
    "database": {"kind", "name", "owner"},
    "migrations": {"kind", "versions"},
    "schema": {"kind", "name", "owner"},
    "relation": {"kind", "schema", "name", "relkind", "owner"},
    "table": {"kind", "schema", "name", "row_count"},
}
SCHEMA_OWNERS = {
    "competence_hub": {OWNER},
    # PG16 default plus explicitly recognized legacy/bootstrap ownership.
    "public": {"pg_database_owner", "postgres", OWNER},
}
RELATION_OWNERS = {"competence_hub": {OWNER}, "public": {"postgres", OWNER}}


class ContractError(ValueError):
    """Messages are fixed error codes, never untrusted contents or paths."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ContractError(code)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def reject_constant(_: str) -> None:
    raise ContractError("nonfinite_json_number")


def safe_identifier(value: object) -> bool:
    return type(value) is str and IDENTIFIER.fullmatch(value) is not None


def validate_recipient(recipient: str) -> None:
    require(
        type(recipient) is str
        and re.fullmatch(r"[A-F0-9]{40}", recipient) is not None
        and len(set(recipient)) > 1,
        "explicit_full_recipient_required",
    )


def validate_header(record: dict, *, expected_recipient: str = RECIPIENT) -> None:
    validate_recipient(expected_recipient)
    for key, expected in {
        "format": "competence-hub.prechange.v1",
        "database": DATABASE,
        "recipient": expected_recipient,
        "encryption": "openpgp",
        "baseline_scope": "all_non_system_schemas",
        "consistency": "exported_mvcc_snapshot",
    }.items():
        require(record[key] == expected, "invalid_header_" + key)
    require(record["role_passwords_included"] is False, "passwords_not_excluded")
    require(record["restore_verified"] is False, "source_claims_restore")
    require(
        type(record["run_id"]) is str
        and RUN_ID.fullmatch(record["run_id"]) is not None,
        "invalid_run_id",
    )
    stamp = record["created_at_utc"]
    require(
        type(stamp) is str and re.fullmatch(r"[0-9]{8}T[0-9]{6}Z", stamp) is not None,
        "invalid_header_date",
    )
    try:
        datetime.strptime(stamp, "%Y%m%dT%H%M%SZ")
    except ValueError:
        raise ContractError("invalid_header_date") from None


def parse_baseline(
    data: bytes,
    *,
    expected: bool,
    current: bool = False,
    expected_recipient: str = RECIPIENT,
) -> list[dict]:
    require(not (expected and current), "invalid_parse_mode")
    require(type(data) is bytes and 0 < len(data) <= MAX_BYTES, "invalid_input_size")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeError:
        raise ContractError("invalid_utf8") from None
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    require(0 < len(lines) <= MAX_RECORDS, "invalid_record_count")
    records = []
    seen = set()
    for index, line in enumerate(lines):
        require(0 < len(line) <= 65536 and line.strip() != "", "invalid_json_line")
        try:
            record = json.loads(
                line, object_pairs_hook=unique_object, parse_constant=reject_constant
            )
        except (ValueError, RecursionError) as exc:
            if isinstance(exc, ContractError):
                raise
            raise ContractError("invalid_json") from None
        require(type(record) is dict, "record_not_object")
        kind = record.get("kind")
        require(type(kind) is str and kind in FIELDS, "unknown_record_kind")
        require(set(record) == FIELDS[kind], "invalid_record_fields")
        if kind == "header":
            require(expected and index == 0, "unexpected_header")
            validate_header(record, expected_recipient=expected_recipient)
        elif kind == "database":
            name = record["name"]
            require(
                type(name) is str
                and len(name) <= 63
                and (
                    name == DATABASE
                    if expected or current
                    else RESTORE_NAME.fullmatch(name) is not None
                ),
                "invalid_database_name",
            )
            require(record["owner"] == OWNER, "unexpected_database_owner")
            record = dict(record, name=DATABASE)
        elif kind == "migrations":
            versions = record["versions"]
            require(
                type(versions) is list
                and 6 <= len(versions) <= 9
                and versions
                == [f"{number:04d}" for number in range(1, len(versions) + 1)],
                "invalid_migrations",
            )
        elif kind == "schema":
            require(
                safe_identifier(record["name"]) and record["name"] in SCHEMA_OWNERS,
                "unexpected_schema",
            )
            require(
                type(record["owner"]) is str
                and record["owner"] in SCHEMA_OWNERS[record["name"]],
                "unexpected_schema_owner",
            )
        else:
            require(
                safe_identifier(record["schema"])
                and record["schema"] in SCHEMA_OWNERS
                and safe_identifier(record["name"]),
                "unsafe_relation_identifier",
            )
            if kind == "relation":
                require(
                    type(record["relkind"]) is str
                    and record["relkind"] in {"r", "p", "m", "v", "S"},
                    "invalid_relation_kind",
                )
                require(
                    type(record["owner"]) is str
                    and record["owner"] in RELATION_OWNERS[record["schema"]],
                    "unexpected_relation_owner",
                )
            else:
                require(
                    type(record["row_count"]) is int
                    and 0 <= record["row_count"] <= 9223372036854775807,
                    "invalid_row_count",
                )
        key = (kind, record.get("schema", ""), record.get("name", ""))
        require(key not in seen, "duplicate_record")
        seen.add(key)
        records.append(record)
    headers = [r for r in records if r["kind"] == "header"]
    require(
        len(headers) == int(expected)
        and (not expected or records[0]["kind"] == "header"),
        "missing_header",
    )
    for singleton in ("database", "migrations"):
        require(sum(r["kind"] == singleton for r in records) == 1, "missing_singleton")
    schemas = {r["name"] for r in records if r["kind"] == "schema"}
    require(schemas == set(SCHEMA_OWNERS), "incomplete_schemas")
    relations = {
        (r["schema"], r["name"]): r for r in records if r["kind"] == "relation"
    }
    tables = {(r["schema"], r["name"]): r for r in records if r["kind"] == "table"}
    require(
        set(tables)
        == {key for key, r in relations.items() if r["relkind"] in {"r", "p", "m"}},
        "incomplete_table_set",
    )
    migration_key = ("competence_hub", "schema_migrations")
    require(
        migration_key in relations and relations[migration_key]["relkind"] == "r",
        "missing_migration_table",
    )
    versions = next(r["versions"] for r in records if r["kind"] == "migrations")
    require(
        tables[migration_key]["row_count"] == len(versions), "migration_count_mismatch"
    )
    return sorted(
        (r for r in records if r["kind"] != "header"),
        key=lambda r: (r["kind"], r.get("schema", ""), r.get("name", "")),
    )


def canonical_bytes(records: list[dict]) -> bytes:
    return json.dumps(
        records, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def baseline_summary(records: list[dict]) -> dict:
    return {
        "baseline_sha256": hashlib.sha256(canonical_bytes(records)).hexdigest(),
        "migrations": next(r["versions"] for r in records if r["kind"] == "migrations"),
        "row_counts": {
            r["schema"] + "." + r["name"]: r["row_count"]
            for r in records
            if r["kind"] == "table"
        },
        "schema_count": sum(r["kind"] == "schema" for r in records),
        "relation_count": sum(r["kind"] == "relation" for r in records),
        "table_count": sum(r["kind"] == "table" for r in records),
        "owners_verified": True,
    }


def validate_metadata(data: bytes, *, expected_recipient: str = RECIPIENT) -> dict:
    """Validate the complete source; no evidence of restore execution is implied."""
    return dict(
        baseline_summary(
            parse_baseline(data, expected=True, expected_recipient=expected_recipient)
        ),
        status="VALID",
        metadata_sha256=hashlib.sha256(data).hexdigest(),
    )


def compare(
    expected_data: bytes,
    actual_data: bytes,
    *,
    current: bool = False,
    expected_recipient: str = RECIPIENT,
) -> dict:
    """Default: isolated restore only. current=True: explicit pre-write staging check."""
    expected = parse_baseline(
        expected_data, expected=True, expected_recipient=expected_recipient
    )
    actual = parse_baseline(actual_data, expected=False, current=current)
    require(expected == actual, "baseline_mismatch")
    return dict(
        baseline_summary(expected),
        schema="competence-hub.prechange-baseline-comparison.v1",
        status="MATCH" if current else "PASS",
        metadata_sha256=hashlib.sha256(expected_data).hexdigest(),
        actual_sha256=hashlib.sha256(actual_data).hexdigest(),
    )


def regular_bytes(path: Path) -> bytes:
    for component in (path, *path.parents):
        info = component.lstat()
        require(
            not stat.S_ISLNK(info.st_mode)
            and not getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400),
            "unsafe_input_path",
        )
    require(
        stat.S_ISREG(path.stat().st_mode) and path.stat().st_size <= MAX_BYTES,
        "invalid_input_file",
    )
    with path.open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "invalid_input_size")
    return data


def query_sql(*, current: bool = False) -> str:
    producer = Path(__file__).with_name("competence-hub-postgres-snapshot")
    source = regular_bytes(producer).decode("ascii")
    start = "read -r -d '' baseline_sql <<'SQL' || true\n"
    require(source.count(start) == 1, "unapproved_producer_sql")
    body = source.split(start)[1].split("\nSQL\n")[0] + "\n"
    require(
        hashlib.sha256(body.encode("ascii")).hexdigest() == SQL_BODY_SHA256,
        "unapproved_producer_sql",
    )
    require(body.endswith("SELECT 'BASELINE_END';\n"), "unapproved_producer_sql")
    body = body.removesuffix("SELECT 'BASELINE_END';\n")
    guard = (
        "current_database() = 'competence_hub_staging'"
        if current
        else "current_database() ~ '^competence_hub_restore_check_[a-z0-9_]+$'"
    )
    return (
        "\\set ON_ERROR_STOP on\n\\set QUIET on\nBEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\n"
        f"SELECT 1 / CAST({guard} AS integer) AS database_guard \\gset\n"
        + body
        + "COMMIT;\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    query = commands.add_parser("query")
    query.add_argument("--current-staging", action="store_true")
    validator = commands.add_parser("validate")
    validator.add_argument("--expected", required=True, type=Path)
    validator.add_argument("--expected-recipient", default=RECIPIENT)
    comparator = commands.add_parser("compare")
    comparator.add_argument("--expected", required=True, type=Path)
    comparator.add_argument("--actual", required=True, type=Path)
    comparator.add_argument("--current-staging", action="store_true")
    comparator.add_argument("--expected-recipient", default=RECIPIENT)
    args = parser.parse_args(argv)
    try:
        if args.command == "query":
            sys.stdout.write(query_sql(current=args.current_staging))
        elif args.command == "validate":
            data = regular_bytes(args.expected.absolute())
            print(
                json.dumps(
                    validate_metadata(data, expected_recipient=args.expected_recipient),
                    sort_keys=True,
                )
            )
        else:
            result = compare(
                regular_bytes(args.expected.absolute()),
                regular_bytes(args.actual.absolute()),
                current=args.current_staging,
                expected_recipient=args.expected_recipient,
            )
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except (ContractError, OSError, UnicodeError) as exc:
        code = str(exc) if isinstance(exc, ContractError) else "input_unavailable"
        print(
            json.dumps(
                {
                    "schema": "competence-hub.prechange-baseline-comparison.v1",
                    "status": "FAIL",
                    "code": code,
                }
            ),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
