"""Root-only, read-only VPS inventory. No secrets, backups or activation.

Sent through the existing pinned SSH connection as source, not installed on VPS.
Only allowlisted metadata enters stdout; subprocess errors never leave this file.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import subprocess


DATABASE = "competence_hub_staging"
SERVICES = (
    "dp-chatbot.service", "nginx.service", "fail2ban.service", "postgresql.service",
    "competence-hub-api.service",
)
PATHS = (
    "/opt/competence-hub", "/opt/competence-hub/current",
    "/etc/competence-hub", "/etc/competence-hub/webapp.env",
    "/etc/systemd/system/competence-hub-api.service",
    "/etc/nginx/nginx.conf", "/etc/nginx/sites-enabled",
)


class PreflightStop(RuntimeError):
    pass


def command(*args, data=None):
    result = subprocess.run(args, input=data, capture_output=True, timeout=45)
    if result.returncode:
        raise PreflightStop("READONLY_COMMAND_UNAVAILABLE")
    return result.stdout.decode("utf-8")


def sql(query):
    # PostgreSQL, not a caller convention, rejects writes in every connection.
    statement = (
        "BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY; "
        "SET LOCAL statement_timeout='10s'; SET LOCAL lock_timeout='2s'; "
        + query + "; COMMIT;"
    )
    return command(
        "runuser", "-u", "postgres", "--", "psql", "-X", "-qAt",
        "-v", "ON_ERROR_STOP=1", "-d", DATABASE, data=statement.encode("utf-8"),
    ).strip()


def path_metadata(path):
    try:
        info = Path(path).lstat()
    except FileNotFoundError:
        return {"exists": False}
    return {
        "exists": True, "mode": format(stat.S_IMODE(info.st_mode), "04o"),
        "uid": info.st_uid, "gid": info.st_gid, "bytes": info.st_size,
        "is_link": stat.S_ISLNK(info.st_mode),
        "is_directory": stat.S_ISDIR(info.st_mode),
    }


def database_metadata():
    tables = json.loads(sql(
        "SELECT COALESCE(json_agg(tablename ORDER BY tablename),'[]'::json) "
        "FROM pg_tables WHERE schemaname='competence_hub'"
    ))
    if not tables or len(tables) > 100 or any(
        not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name)
        for name in tables
    ):
        raise PreflightStop("SCHEMA_TABLE_METADATA_REJECTED")
    # Identifiers came from pg_tables and must pass the strict identifier bound.
    counts = " UNION ALL ".join(
        f"SELECT '{name}' AS name, count(*) AS rows FROM competence_hub.{name}"
        for name in tables
    )
    return json.loads(sql("""SELECT json_build_object(
        'database',current_database(),
        'server_version',current_setting('server_version'),
        'listen_addresses',current_setting('listen_addresses'),
        'port',current_setting('port'),
        'database_bytes',pg_database_size(current_database()),
        'migrations',(SELECT json_agg(version ORDER BY version) FROM competence_hub.schema_migrations),
        'table_owners',(SELECT json_agg(x ORDER BY tablename) FROM
            (SELECT tablename,tableowner FROM pg_tables WHERE schemaname='competence_hub') x),
        'roles',(SELECT json_agg(x ORDER BY rolname) FROM
            (SELECT rolname,rolsuper,rolcreaterole,rolcreatedb,rolcanlogin,rolbypassrls
             FROM pg_roles WHERE rolname IN ('competence_hub_owner','competence_hub_app','competence_hub_migrator')) x),
        'role_memberships',(SELECT json_agg(x ORDER BY member,role) FROM
            (SELECT pg_get_userbyid(member) AS member,pg_get_userbyid(roleid) AS role
             FROM pg_auth_members WHERE pg_get_userbyid(member) IN
             ('competence_hub_owner','competence_hub_app','competence_hub_migrator')) x),
        'privileges',json_build_object(
            'app_owner_member',pg_has_role('competence_hub_app','competence_hub_owner','MEMBER'),
            'app_migrator_member',pg_has_role('competence_hub_app','competence_hub_migrator','MEMBER'),
            'app_schema_create',has_schema_privilege('competence_hub_app','competence_hub','CREATE'),
            'app_migrations_select',has_table_privilege('competence_hub_app','competence_hub.schema_migrations','SELECT'),
            'app_offers_select',has_table_privilege('competence_hub_app','competence_hub.calendar_offers','SELECT'),
            'app_offers_insert',has_table_privilege('competence_hub_app','competence_hub.calendar_offers','INSERT'),
            'app_offers_delete',has_table_privilege('competence_hub_app','competence_hub.calendar_offers','DELETE'),
            'app_decisions_update',has_table_privilege('competence_hub_app','competence_hub.calendar_review_decisions','UPDATE')),
        'other_sessions',(SELECT count(*) FROM pg_stat_activity
            WHERE datname=current_database() AND pid<>pg_backend_pid()),
        'counts',(SELECT json_object_agg(name,rows) FROM (""" + counts + ") x))"))


def assess(report):
    database = report["database"]
    versions = database.get("migrations")
    supported = any(versions == [f"{i:04}" for i in range(1, count + 1)] for count in range(6, 10))
    roles = {row["rolname"]: row for row in database.get("roles") or []}
    rights = database.get("privileges", {})
    listen = database.get("listen_addresses", "").split(",")
    sockets = [value for value in report.get("listeners", []) if value.endswith(":5432")]
    return {
        "database_identity": database.get("database") == DATABASE,
        "supported_migrations": supported,
        "postgres_loopback_setting": bool(listen) and all(value.strip() in {"localhost", "127.0.0.1", "::1"} for value in listen)
            and database.get("port") == "5432",
        "postgres_loopback_sockets": bool(sockets) and all(value in {"127.0.0.1:5432", "[::1]:5432", "::1:5432"} for value in sockets),
        "owners": all(row["tableowner"] == "competence_hub_owner" for row in database.get("table_owners") or []) and bool(database.get("table_owners")),
        "bounded_roles": set(roles) == {"competence_hub_owner", "competence_hub_app", "competence_hub_migrator"}
            and not any(row[flag] for row in roles.values() for flag in ("rolsuper", "rolcreaterole", "rolcreatedb", "rolbypassrls"))
            and not roles["competence_hub_owner"]["rolcanlogin"],
        "app_rights": rights.get("app_offers_select") is True and rights.get("app_offers_insert") is True
            and all(rights.get(name) is False for name in
                    ("app_schema_create", "app_migrations_select", "app_offers_delete", "app_decisions_update",
                     "app_owner_member", "app_migrator_member")),
        "foreign_services_active": all(report["services"].get(name, {}).get("ActiveState") == "active" for name in SERVICES[:4]),
    }


def collect():
    if os.name != "posix" or os.geteuid() != 0:
        raise PreflightStop("ROOT_READONLY_CONTEXT_REQUIRED")
    report = {
        "schema": "competence-hub.readonly-staging-preflight.v1",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "READ_ONLY", "server_mutations": False,
        "services": {}, "paths": {path: path_metadata(path) for path in PATHS},
    }
    for name in SERVICES:
        raw = command("systemctl", "show", name, "-p", "LoadState", "-p", "ActiveState", "-p", "SubState", "-p", "User", "-p", "Group")
        report["services"][name] = dict(line.split("=", 1) for line in raw.splitlines() if "=" in line)
    report["listeners"] = [line.split()[3] for line in command("ss", "-ltnH").splitlines()]
    report["database"] = database_metadata()
    # Do not parse/dump Nginx configuration or read certificate/private-key files.
    # nginx -t reads its own configuration under root and emits only PASS here.
    report["nginx_syntax_ok"] = subprocess.run(
        ["nginx", "-t"], capture_output=True, timeout=30,
    ).returncode == 0
    report["checks"] = assess(report)
    report["status"] = "PASS" if all(report["checks"].values()) and report["nginx_syntax_ok"] else "REVIEW_REQUIRED"
    report["backup_restore"] = "NOT_RUN"
    report["pilot"] = "NOT_INSTALLED"
    return report


if __name__ == "__main__":
    try:
        print(json.dumps(collect(), separators=(",", ":")))
    except Exception:
        print(json.dumps({"status": "STOP", "code": "PRIVATE_READONLY_PREFLIGHT_FAILED", "server_mutations": False}))
        raise SystemExit(1) from None
