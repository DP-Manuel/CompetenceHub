"""Inspect an existing private clone or apply only the bound V2 schema, locally."""

import argparse
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

from v2_package import (
    MIGRATION_HEAD, TARGET, add_package_arguments, json_bytes, json_read, matches, rejection_code,
    require, sha, sha_valid, verify_arguments,
)


DATABASE = TARGET["database"]
TABLES = tuple(sorted("""
    schema_migrations portal_users roles user_roles companies company_contacts coaches topics coach_topics
    services coach_services coaching_requests request_topics request_services audit_events auth_password_credentials
    auth_login_challenges auth_sessions auth_one_time_tokens auth_totp_credentials auth_recovery_codes
    auth_rate_limit_buckets auth_idempotency_records auth_token_delivery_outbox calendar_offers
    calendar_offer_revisions calendar_review_decisions
""".split()))
SEQUENCES = ("audit_events_id_seq", "calendar_review_decisions_id_seq")
ACTION = f"V2_SCHEMA_ONLY_0007_TO_{MIGRATION_HEAD:04}"


def sql_list(items):
    return ",".join("'" + item + "'" for item in items)


def check(predicate, code):
    return f"DO $$BEGIN IF ({predicate}) IS DISTINCT FROM true THEN RAISE EXCEPTION '{code}'; END IF; END$$;\n"


def ledger(upper):
    versions = sql_list(f"{i:04}" for i in range(1, upper + 1))
    return check(f"(SELECT array_agg(version::text ORDER BY version) FROM competence_hub.schema_migrations)"
                 f" = ARRAY[{versions}]", "EXACT_MIGRATION_LEDGER_REQUIRED")


def clone_snapshot():
    # Keep only pre-0007 Coach columns and ledger rows, permitting the additive target schema.
    rows = []
    for name in TABLES:
        row = "to_jsonb(t)"
        filter_ = ""
        if name == "coaches":
            row += " - ARRAY['lifecycle_status','registry_lock_version','registry_request_id','publication_floor']"
        if name == "schema_migrations":
            filter_ = " WHERE version <= '0006'"
        rows.append(f"SELECT '{name}' AS name, count(*)::text || ':' || encode(sha256(convert_to("
                    f"coalesce(string_agg(v, E'\\n' ORDER BY v COLLATE \"C\"), ''), 'UTF8')), 'hex') AS value "
                    f"FROM (SELECT ({row})::text AS v FROM competence_hub.{name} t{filter_}) s")
    rows.extend(f"SELECT '{name}', last_value::text || ':' || is_called::text FROM competence_hub.{name}"
                for name in SEQUENCES)
    inner = " UNION ALL ".join(rows)
    return f"encode(sha256(convert_to((SELECT jsonb_object_agg(name,value)::text FROM ({inner}) q), 'UTF8')), 'hex')"


def migration_body(data):
    # Preserve the reviewed SQL body and per-file role; replace only the outer transaction framing.
    match = re.fullmatch(rb"\\set ON_ERROR_STOP on\r?\n\s*BEGIN;\r?\n(SET LOCAL ROLE competence_hub_owner;.*)\r?\nCOMMIT;\s*",
                         data, re.DOTALL)
    require(match and not re.search(rb"(?im)^\s*(?:\\|COMMIT\b|ROLLBACK\b|START TRANSACTION\b|END\s*;)",
                                    # Procedure-body END is legal SQL, not a top-level transaction statement.
                                    re.sub(rb"\$\$.*?\$\$", b"", match[1], flags=re.DOTALL)),
            "UNREVIEWED_MIGRATION_WRAPPER")
    return match[1].decode("utf-8") + "\nRESET ROLE;\n"


def plan(migrations, approval=None, *, ready=False):
    mode = "READ ONLY" if approval is None else "READ WRITE"
    return_sql = f"SELECT json_build_object('database',current_database(),'clone_oid',(SELECT oid::text FROM pg_database " \
                 f"WHERE datname=current_database()),'system_identifier',(SELECT system_identifier::text FROM pg_control_system())," \
                 f"'reference_sha256',{clone_snapshot()});\n"
    script = (f"BEGIN ISOLATION LEVEL REPEATABLE READ {mode};\n"
              "SET LOCAL search_path = pg_catalog, public;\nSET LOCAL timezone='UTC';\n"
              "SET LOCAL lock_timeout='5s';\nSET LOCAL statement_timeout='45s';\n")
    script += check(f"current_database() = '{DATABASE}' AND session_user = 'postgres' AND inet_server_addr() IS NULL"
                    " AND current_setting('server_version_num')::int BETWEEN 160000 AND 169999"
                    " AND current_setting('port') = '5432'", "PRIVATE_POSTGRES16_CLONE_REQUIRED")
    script += check("EXISTS (SELECT FROM pg_database WHERE datname=current_database() AND datallowconn"
                    " AND pg_get_userbyid(datdba)='competence_hub_owner'"
                    " AND NOT EXISTS (SELECT FROM aclexplode(coalesce(datacl,acldefault('d',datdba)))"
                    " WHERE grantee=0 AND privilege_type IN ('CONNECT','CREATE','TEMPORARY')))"
                    " AND has_database_privilege('competence_hub_app',current_database(),'CONNECT')"
                    " AND has_database_privilege('competence_hub_migrator',current_database(),'CONNECT')"
                    " AND pg_has_role('competence_hub_migrator','competence_hub_owner','MEMBER')"
                    " AND NOT pg_has_role('competence_hub_app','competence_hub_owner','MEMBER')"
                    " AND NOT has_database_privilege('competence_hub_app',current_database(),'CREATE')"
                    " AND NOT has_schema_privilege('competence_hub_app','public','CREATE')"
                    " AND NOT has_schema_privilege('competence_hub_app','competence_hub','CREATE')"
                    " AND NOT has_table_privilege('competence_hub_app','competence_hub.schema_migrations','SELECT')"
                    " AND (SELECT count(*) FROM pg_roles WHERE rolname IN ('competence_hub_app','competence_hub_migrator')"
                    " AND rolcanlogin AND NOT (rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls))=2",
                    "CLONE_CUSTODY_OR_PRIVILEGES")
    if approval is not None:
        script += check("pg_try_advisory_xact_lock(782791011)", "V2_MIGRATION_LOCK_BUSY")
        script += "LOCK TABLE " + ",".join(f"competence_hub.{name}" for name in TABLES) + " IN ACCESS EXCLUSIVE MODE;\n"
    script += check("NOT EXISTS (SELECT FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid())",
                    "CLONE_MUST_BE_QUIET")
    if ready:
        script += ledger(MIGRATION_HEAD)
        script += check("NOT EXISTS (SELECT FROM competence_hub.auth_sessions WHERE revoked_at IS NULL"
                        " AND idle_expires_at>now() AND absolute_expires_at>now())"
                        " AND NOT EXISTS (SELECT FROM competence_hub.auth_login_challenges"
                        " WHERE revoked_at IS NULL AND consumed_at IS NULL AND expires_at>now())"
                        " AND NOT EXISTS (SELECT FROM competence_hub.auth_one_time_tokens"
                        " WHERE revoked_at IS NULL AND consumed_at IS NULL AND expires_at>now())"
                        " AND NOT EXISTS (SELECT FROM competence_hub.auth_token_delivery_outbox"
                        " WHERE status IN ('pending','processing','failed'))", "CLONED_AUTH_STATE_MUST_NOT_BE_REPLAYABLE")
        return script + return_sql + "ROLLBACK;\n"
    script += ledger(6)
    script += check(f"(SELECT array_agg(c.relname::text ORDER BY c.relname::text COLLATE \"C\") FROM pg_class c "
                    "WHERE relnamespace='competence_hub'::regnamespace AND relkind IN ('r','p','f'))"
                    f" = ARRAY[{sql_list(TABLES)}] AND NOT EXISTS (SELECT FROM pg_class WHERE"
                    " relnamespace='competence_hub'::regnamespace AND relkind IN ('r','S')"
                    " AND pg_get_userbyid(relowner)<>'competence_hub_owner')", "BASELINE_TABLES_OR_OWNERS")
    if approval is None:
        return script + return_sql + "ROLLBACK;\n"
    script += check(f"(SELECT system_identifier::text FROM pg_control_system())='{approval['system_identifier']}'"
                    f" AND (SELECT oid::text FROM pg_database WHERE datname=current_database())='{approval['clone_oid']}'"
                    f" AND {clone_snapshot()}='{approval['reference_sha256']}'", "CLONE_CHANGED_SINCE_APPROVAL")
    for i, migration in enumerate(migrations, start=7):
        script += "SET SESSION AUTHORIZATION competence_hub_migrator;\n" + migration_body(migration)
        script += "RESET SESSION AUTHORIZATION;\n" + ledger(i)
    script += check(f"{clone_snapshot()}='{approval['reference_sha256']}'", "ORIGINAL_CLONE_REFERENCE_CHANGED")
    script += check("(SELECT count(*) FROM pg_tables WHERE schemaname='competence_hub')=48"
                    " AND NOT EXISTS(SELECT FROM pg_tables WHERE schemaname='competence_hub'"
                    " AND tableowner<>'competence_hub_owner')"
                    " AND NOT EXISTS (SELECT FROM competence_hub.coach_import_sources)"
                    " AND NOT EXISTS (SELECT FROM competence_hub.coach_import_items)"
                    " AND NOT EXISTS (SELECT FROM competence_hub.coach_import_evidence)"
                    " AND NOT EXISTS (SELECT FROM competence_hub.calendar_reservations)"
                    " AND NOT EXISTS (SELECT FROM competence_hub.calendar_reservation_events)"
                    " AND NOT EXISTS (SELECT FROM competence_hub.private_customers)"
                    " AND NOT EXISTS (SELECT FROM competence_hub.company_customer_details)"
                    " AND has_table_privilege('competence_hub_app','competence_hub.calendar_reservations','SELECT')"
                    " AND has_column_privilege('competence_hub_app','competence_hub.calendar_reservations','seats','UPDATE')"
                    " AND has_table_privilege('competence_hub_app','competence_hub.private_customers','SELECT')"
                    " AND NOT has_table_privilege('competence_hub_app','competence_hub.private_customers','DELETE')"
                    " AND NOT has_table_privilege('competence_hub_app','competence_hub.calendar_reservation_events','DELETE')",
                    "V2_POST_MIGRATION_INVARIANTS")
    return script + "COMMIT;\n" + return_sql


def approval_from(data, approval_sha, args, now):
    require(sha_valid(approval_sha) and sha(data) == approval_sha, "EXACT_OWNER_APPROVAL_SHA_REQUIRED")
    approval = json_read(data)
    fixed = {"action": ACTION, "commit": args.commit, "archive_sha256": args.sha256,
             "source_evidence_sha256": args.source_evidence_sha256, "database": DATABASE,
             "real_coach_import_authorized": False}
    digests = {"reference_sha256", "protected_restore_receipt_sha256", "clone_parity_receipt_sha256"}
    require(set(approval) == set(fixed) | digests | {"system_identifier", "clone_oid", "expires_utc"}
            and all(approval[key] == value for key, value in fixed.items())
            and approval["real_coach_import_authorized"] is False
            and all(sha_valid(approval[key]) for key in digests)
            and matches(r"[1-9][0-9]{0,19}", approval["system_identifier"])
            and matches(r"[1-9][0-9]{0,9}", approval["clone_oid"])
            and matches(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", approval["expires_utc"]),
            "OWNER_APPROVAL_SCOPE")
    expires = datetime.fromisoformat(approval["expires_utc"])
    require(now < expires <= now + timedelta(hours=24), "OWNER_APPROVAL_WINDOW")
    return approval


def run_plan(script):
    result = subprocess.run(["/usr/bin/psql", "-X", "-w", "-qAt", "-v", "ON_ERROR_STOP=1",
                             "-h", "/var/run/postgresql", "-p", "5432", "-U", "postgres", "-d", DATABASE],
                            input=script.encode("utf-8"), capture_output=True, cwd="/", timeout=180,
                            env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "PGCLIENTENCODING": "UTF8",
                                 "PGPASSFILE": "/dev/null", "HOME": "/nonexistent", "PGCONNECT_TIMEOUT": "5"})
    # Expose only one of the fixed guard codes, never driver/SQL data or connection details.
    label = re.search(rb"(?m)^ERROR:  ([A-Z][A-Z0-9_]+)\r?$", result.stderr)
    allow = set(re.findall(r"RAISE EXCEPTION '([A-Z][A-Z0-9_]+)'", script))
    safe_error = label[1].decode("ascii") if label and label[1].decode("ascii") in allow else "CLONE_SQL_REFUSED_OR_FAILED"
    require(result.returncode == 0, safe_error)
    return json_read(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_package_arguments(parser)
    parser.add_argument("command", choices=("inspect", "migrate", "ready"))
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--approval-sha256")
    args = parser.parse_args()
    _, migrations = verify_arguments(args)
    approval = None
    if args.command == "migrate":
        require(args.approval and args.approval_sha256, "SCHEMA_ONLY_OWNER_APPROVAL_REQUIRED")
        approval = approval_from(args.approval.read_bytes(), args.approval_sha256, args, datetime.now(timezone.utc))
    else:
        require(args.approval is None and args.approval_sha256 is None, "INSPECT_NEVER_CONSUMES_APPROVAL")
    result = run_plan(plan(migrations, approval, ready=args.command == "ready"))
    print(json_bytes({**result, "archive_sha256": args.sha256, "commit": args.commit,
                      "source_evidence_sha256": args.source_evidence_sha256,
                      "approval_sha256": args.approval_sha256,
                      "migration_head": "0006" if args.command == "inspect" else f"{MIGRATION_HEAD:04}",
                      "deployment_authorized": False}).decode(), end="")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        print(f"V2_CLONE=STOP ({rejection_code(error)}); do not activate or retry without fresh inspection", file=sys.stderr)
        sys.exit(1)
