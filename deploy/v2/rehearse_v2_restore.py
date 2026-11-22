"""Synthetic-only source or recovery on a fresh network-none Linux container."""

import argparse
import base64
from contextlib import contextmanager
from http.client import HTTPConnection
from http.cookies import SimpleCookie
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
import time

import v2_clone as clone
import v2_host as host
import v2_package as package


DATABASE = clone.DATABASE
BOOTSTRAP = Path("/database/bootstrap-staging.sql")
TRANSFER = Path("/transfer")
PG = Path("/usr/lib/postgresql/16/bin")
ACCESS = "/api/v1/portal/access"
REQUESTS = "/api/v1/portal/requests"
ORIGIN = package.TARGET["origin"]
EMAIL = "restore-operator@example.invalid"
PASSWORD = "Synthetic-only offline restore probe 9318"
COMPANY = "00000000-0000-4000-8000-000000000123"
NOTE = "Synthetic confidential reference note"
KEYRINGS = (("TOTP_KEYRING", "TOTP_ACTIVE_KEY_VERSION"),
            ("OUTBOX_KEYRING", "OUTBOX_ACTIVE_KEY_VERSION"),
            ("RECOVERY_HMAC_KEYRING", "RECOVERY_HMAC_ACTIVE_KEY_VERSION"))
RUNTIME_KEYS = {"COMPETENCE_HUB_" + name for name in (
    "RATE_LIMIT_HMAC_KEY", "IDEMPOTENCY_HMAC_KEY", *(item for pair in KEYRINGS for item in pair),
)}


def postgres(program, *args, data=None):
    process = subprocess.run(["runuser", "-u", "postgres", "--", str(PG / program), *args],
                             cwd="/", input=data, capture_output=True, timeout=60, check=True)
    return process.stdout


def sql(database, statement):
    return postgres("psql", "-XqAt", "-v", "ON_ERROR_STOP=1", "-d", database, data=statement)


@contextmanager
def cluster():
    with tempfile.TemporaryDirectory(prefix="ch-offline-pg-") as directory:
        subprocess.run(["chown", "postgres:postgres", directory], check=True)
        data = str(Path(directory) / "data")
        postgres("initdb", "--auth-local=peer", "--auth-host=scram-sha-256", "-D", data)
        postgres("pg_ctl", "-D", data, "-l", str(Path(directory) / "server.log"), "-w", "-o",
                 "-c listen_addresses=127.0.0.1 -c unix_socket_directories=/var/run/postgresql -p 5432", "start")
        try:
            yield sql("postgres", b"SELECT system_identifier::text FROM pg_control_system();").decode().strip()
        finally:
            postgres("pg_ctl", "-D", data, "-m", "fast", "-w", "stop")


def bootstrap(*, objects):
    payload = BOOTSTRAP.read_bytes().replace(b"competence_hub_staging", DATABASE.encode())
    sql("postgres", payload if objects else payload.split(b"\\connect", 1)[0])


def runtime_fixture():
    def key():
        return base64.b64encode(secrets.token_bytes(32)).decode()
    config = {"RATE_LIMIT_HMAC_KEY": key(), "IDEMPOTENCY_HMAC_KEY": key()}
    for ring, active in KEYRINGS:
        config[ring] = json.dumps({"rehearsal": key()})
        config[active] = "rehearsal"
    return {"COMPETENCE_HUB_" + k: v for k, v in config.items()}


@contextmanager
def api(config):
    package.require(set(config) == RUNTIME_KEYS and all(isinstance(value, str) for value in config.values()),
                    "REHEARSAL_RUNTIME_KEYS_ONLY")
    database_password = secrets.token_hex(32)
    sql("postgres", f"ALTER ROLE competence_hub_app PASSWORD '{database_password}';".encode())
    fingerprints = host.V2_RUNTIME.parent / "synthetic-password-fingerprints"
    fingerprints.write_text("0" * 64 + "\n", encoding="ascii")
    fingerprints.chmod(0o644)
    env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1", **config,
           "COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH": str(fingerprints),
           "COMPETENCE_HUB_DATABASE_URL": f"postgresql+asyncpg://competence_hub_app:{database_password}@127.0.0.1:5432/{DATABASE}",
           "COMPETENCE_HUB_ALLOWED_ORIGIN": ORIGIN, "COMPETENCE_HUB_CAL2_MODE": "synthetic-pilot",
           "COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED": "false"}
    with subprocess.Popen([str(host.V2_RUNTIME / "bin/uvicorn"),
                           "competence_hub_api.runtime:create_runtime_app_from_environment", "--factory",
                           "--host", "127.0.0.1", "--port", "8002", "--no-access-log"],
                          env=env, user="nobody", group="nogroup", stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL) as process:
        try:
            client = Client()
            for _ in range(160):
                package.require(process.poll() is None, "REHEARSAL_API_STARTUP_FAILED")
                try:
                    client.call("GET", "/health/ready", 200)
                except OSError:
                    time.sleep(.125)
                else:
                    break
            else:
                raise ValueError("REHEARSAL_API_TIMEOUT")
            yield client
        finally:
            process.terminate()
            try:
                process.wait(timeout=12)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=4)


class Client:
    def __init__(self):
        self.cookies = {}
        self.csrf = ""

    def call(self, method, path, expected, payload=None, *, csrf=None, origin=ORIGIN):
        headers = {"Host": "localhost:8447", "Origin": origin, "X-Forwarded-Proto": "https",
                   "Content-Type": "application/json", "X-CSRF-Token": self.csrf if csrf is None else csrf,
                   "Cookie": "; ".join(f"{k}={v}" for k, v in self.cookies.items())}
        connection = HTTPConnection("127.0.0.1", 8002, timeout=10)
        try:
            connection.request(method, path, body=json.dumps(payload) if payload is not None else None, headers=headers)
            response = connection.getresponse()
            data = response.read()
            if response.status != expected:
                raise ValueError(f"REHEARSAL_HTTP_{method}_EXPECTED_{expected}_GOT_{response.status}")
            for key, value in response.getheaders():
                if key.lower() == "set-cookie":
                    for name, cookie in SimpleCookie(value).items():
                        package.require(cookie["secure"] and cookie["httponly"] and not cookie["domain"]
                                        and cookie["path"] == "/" and cookie["samesite"] == "lax", "SESSION_COOKIE_FLAGS")
                        self.cookies[name] = cookie.value
                if key.lower() == "x-csrf-token":
                    self.csrf = value
            return json.loads(data) if data else None
        finally:
            connection.close()

    def password(self):
        result = self.call("POST", ACCESS + "/login", 202, {"email": EMAIL, "password": PASSWORD})
        self.csrf = result["csrf_token"]
        return result["state"]


def signature():
    dump = postgres("pg_dump", "--quote-all-identifiers", DATABASE)
    dump = re.sub(rb"(?m)^\\(?:un)?restrict .*\n", b"", dump)
    # The SQL parser flattens these two equivalent predicates on restore.
    for name, expression, low, high in (
        ("private_customers_email_check", '"char_length"("email")', 3, 254),
        ("coaching_request_events_changed_fields_check", '"cardinality"("changed_fields")', 1, 13),
    ):
        prefix = f'    CONSTRAINT "{name}" CHECK ('
        bounds = f"({expression} >= {low}) AND ({expression} <= {high})"
        dump = dump.replace(f"{prefix}(({bounds}) AND ".encode(), f"{prefix}({bounds} AND ".encode(), 1)
    return package.sha(dump)


def source(system_id, migrations):
    bootstrap(objects=True)
    baseline = sorted(Path("/database/migrations").glob("*.sql"))[:6]
    package.require([file.name[:4] for file in baseline] == [f"{i:04}" for i in range(1, 7)], "MISSING_BASELINE")
    for file in baseline:
        sql(DATABASE, file.read_bytes())
    sql(DATABASE, f"INSERT INTO competence_hub.companies(id,name,status) VALUES ('{COMPANY}','Synthetic restore','pilot');".encode())
    before = json.loads(sql(DATABASE, clone.plan(migrations).encode()))
    package.require(json.loads(sql(DATABASE, clone.plan(migrations, before).encode())) == before, "BASELINE_DRIFT")
    sql(DATABASE, b"INSERT INTO competence_hub.portal_users(display_name,email) VALUES ('Restore reviewer','restore-operator@example.invalid');")
    sql(DATABASE, b"""INSERT INTO competence_hub.user_roles (user_id,role_id)
        SELECT u.id,r.id FROM competence_hub.portal_users u, competence_hub.roles r
        WHERE u.email='restore-operator@example.invalid' AND r.code='calendar_reviewer';""")
    pw_hash = host.command(str(host.V2_RUNTIME / "bin/python"), "-I", "-c",
                           "from competence_hub_api.security.passwords import PasswordPolicy,PasswordService; "
                           f"print(PasswordService(PasswordPolicy(frozenset())).hash({PASSWORD!r}))").strip()
    package.require(re.fullmatch(r"[A-Za-z0-9$=,./+_-]+", pw_hash), "SYNTHETIC_PASSWORD_HASH")
    sql(DATABASE, f"""INSERT INTO competence_hub.auth_password_credentials (portal_user_id,password_hash)
        SELECT id,'{pw_hash}' FROM competence_hub.portal_users WHERE email='{EMAIL}';""".encode())
    config = runtime_fixture()
    with api(config) as client:
        package.require(client.password() == "mfa_enrollment_required", "SYNTHETIC_ENROLLMENT")
        uri = client.call("POST", ACCESS + "/mfa/totp/enrollment", 201)["provisioning_uri"]
        code = host.command(str(host.V2_RUNTIME / "bin/python"), "-I", "-c",
                            "import sys,pyotp; print(pyotp.parse_uri(sys.stdin.read()).now())", input=uri).strip()
        result = client.call("POST", ACCESS + "/mfa/totp/enrollment/confirm", 200, {"code": code})
        path = REQUESTS + "/" + client.call("POST", REQUESTS, 201, {
            "subject": "Synthetic restore request", "description": "No real data", "company_id": COMPANY,
        })["id"]
        item = client.call("POST", path + "/notes", 201, {"version": 1, "visibility": "internal", "body": NOTE})
        package.require(item["version"] == 2, "SOURCE_CASE_VERSION")
        client.call("DELETE", ACCESS + "/session", 204)
    dump = postgres("pg_dump", "--format=custom", DATABASE)
    (TRANSFER / "database.dump").write_bytes(dump)
    (TRANSFER / "runtime.json").write_bytes(package.json_bytes(config))
    # Synthetic operator input only, kept apart from the database/runtime ciphertexts.
    (TRANSFER / "fixture.json").write_bytes(package.json_bytes({"path": path, "recovery": result["recovery_codes"][0],
                                                               "source_cluster": system_id, "signature": signature()}))
    print("LINUX_SOURCE=PASS; migrated, MFA enrolled, request and audit saved", flush=True)


def restore(system_id):
    fixture = package.json_read((TRANSFER / "fixture.json").read_bytes())
    package.require(system_id != fixture["source_cluster"], "RESTORE_MUST_USE_FRESH_CLUSTER")
    bootstrap(objects=False)
    postgres("pg_restore", "--exit-on-error", "--single-transaction", "-d", DATABASE,
             data=(TRANSFER / "database.dump").read_bytes())
    package.require(signature() == fixture["signature"], "RESTORED_DB_PARITY")
    config = package.json_read((TRANSFER / "runtime.json").read_bytes())
    with api(config) as client:
        client.call("GET", fixture["path"], 401)
        package.require(client.password() != "mfa_enrollment_required", "MFA_STATE_NOT_RESTORED")
        client.call("POST", ACCESS + "/mfa/recovery/verify", 204, {"code": fixture["recovery"]})
        package.require(client.call("GET", ACCESS + "/session", 200)["user"]["roles"] == ["calendar_reviewer"],
                        "RESTORED_ROLE_SCOPE")
        item = client.call("GET", fixture["path"], 200)
        package.require(item["version"] == 2 and item["notes"][0]["body"] == NOTE and len(item["audit"]) == 2,
                        "RESTORED_CASE_OR_AUDIT")
        client.call("PATCH", fixture["path"], 403, {"version": 2, "status": "closed"}, csrf="invalid")
        client.call("PATCH", fixture["path"], 403, {"version": 2, "status": "closed"}, origin="https://denied.invalid")
        updated = client.call("PATCH", fixture["path"], 200, {"version": 2, "status": "closed"})
        package.require(updated["version"] == 3 and updated["status"] == "closed", "RESTORED_CASE_WRITE")
        client.call("PATCH", fixture["path"], 409, {"version": 2, "status": "open"})
        client.call("DELETE", ACCESS + "/session", 204)
        client.call("GET", fixture["path"], 401)
    print("LINUX_RESTORE=PASS; independent cluster, data/schema/ACL parity, recovered MFA and guarded write", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("source", "restore"))
    package.add_package_arguments(parser)
    args = parser.parse_args()
    package.require(os.environ.get("CH_V2_OWN_DISPOSABLE_CONTAINER") == "1" and TRANSFER.is_mount(), "LOCAL_REHEARSAL_ONLY")
    host.linux_verify(args)
    _, migrations = package.verify_arguments(args)
    os.umask(0o077)
    with cluster() as identifier:
        source(identifier, migrations) if args.phase == "source" else restore(identifier)


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, KeyError, TypeError, IndexError, OSError, subprocess.SubprocessError) as exc:
        print(f"LINUX_REHEARSAL=STOP ({package.rejection_code(exc)})", file=sys.stderr)
        sys.exit(1)
