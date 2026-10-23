"""Actual packaged runtime, local PG and Nginx HTTPS in an owned container only."""
import asyncio
from datetime import timedelta
from http.cookiejar import CookieJar
import json
from pathlib import Path
import secrets
import ssl
import subprocess
import threading
import time
import traceback
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import build_opener, HTTPCookieProcessor, HTTPSHandler, HTTPRedirectHandler, Request
from uuid import uuid4

import pyotp
import uvicorn
from competence_hub_api.config import RuntimeSettings
from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.tokens import keyed_digest

ROOT = Path("/work")
ORIGIN = "https://localhost:8443"
ACCESS = "/api/v1/portal/access"


def command(*args, input=None):
    result = subprocess.run(args, input=input, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Local command failed: " + Path(args[0]).name)
    return result.stdout


def sql(statement, database="competence_hub_staging"):
    return command("runuser", "-u", "postgres", "--", "psql", "-X", "-v", "ON_ERROR_STOP=1", "-At", "-d", database, input=statement)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def main(report):
    if not Path("/.dockerenv").exists() or not (ROOT / "LOCAL_REHEARSAL_ONLY").exists():
        raise RuntimeError("Local container guard missing")
    checks = report["checks"]
    def check(label, condition):
        report["last_check"] = label
        if not condition:
            raise AssertionError(label)
        checks.append(label)
    command("pg_ctlcluster", "16", "main", "start", "-o", "-c listen_addresses=127.0.0.1")
    bundle = ROOT / "bundle"
    sql((bundle / "database/bootstrap-staging.sql").read_text(), "postgres")
    for migration in sorted((bundle / "database/migrations").glob("*.sql")):
        sql(migration.read_text())
    password, db_password = secrets.token_urlsafe(32), secrets.token_hex(32)
    sql(f"ALTER ROLE competence_hub_app PASSWORD '{db_password}';", "postgres")
    users = {role: uuid4() for role in ("coach", "calendar_reviewer")}
    coach_id = uuid4()
    password_hash = PasswordService(PasswordPolicy(frozenset())).hash(password)
    for role, user in users.items():
        sql(f"SET ROLE competence_hub_owner; INSERT INTO competence_hub.portal_users(id,display_name,email,active) VALUES('{user}','Synthetic {role}','{user}@example.invalid',true); INSERT INTO competence_hub.user_roles(user_id,role_id) SELECT '{user}',id FROM competence_hub.roles WHERE code='{role}'; INSERT INTO competence_hub.auth_password_credentials(portal_user_id,password_hash) VALUES('{user}','{password_hash}');")
    sql(f"SET ROLE competence_hub_owner; INSERT INTO competence_hub.coaches(id,portal_user_id,display_name,public_profile_status,public_profile_path) VALUES('{coach_id}','{users['coach']}','Synthetic Coach','synthetic',NULL);")
    key = secrets.token_bytes(32)
    settings = RuntimeSettings(database_url=f"postgresql+asyncpg://competence_hub_app:{db_password}@127.0.0.1:5432/competence_hub_staging",
        allowed_origin=ORIGIN, session_idle_timeout=timedelta(minutes=30), readiness_timeout_seconds=5,
        rate_limit_hmac_key=key, idempotency_hmac_key=secrets.token_bytes(32),
        outbox_encryption_keys={"local": secrets.token_bytes(32)}, outbox_active_key_version="local",
        compromised_password_fingerprints=frozenset({"0" * 64}),
        totp_encryption_keys={"local": secrets.token_bytes(32)}, totp_active_key_version="local",
        recovery_hmac_keys={"local": secrets.token_bytes(32)}, recovery_hmac_active_key_version="local")
    app = create_runtime_app(settings)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8001, proxy_headers=True,
        forwarded_allow_ips="127.0.0.1", access_log=False, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 20
    while not server.started:
        if time.monotonic() > deadline or not thread.is_alive():
            raise RuntimeError("Local API startup failed")
        time.sleep(.1)
    # Self-signed localhost certificate is a disposable test fixture, not ACME issuance.
    command("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=localhost",
        "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1", "-keyout", str(ROOT / "localhost.key"), "-out", str(ROOT / "localhost.crt"))
    (ROOT / "localhost.key").chmod(0o600)
    template = (bundle / "deploy/nginx/competence-hub-app.conf.example").read_text()
    rendered = template.replace("__APP_HOSTNAME__", "localhost").replace("__PORT__", "8001").replace("__TLS_FULLCHAIN_PATH__", "/work/localhost.crt").replace("__TLS_PRIVATE_KEY_PATH__", "/work/localhost.key")
    rendered = rendered.replace("listen 80;", "listen 127.0.0.1:8080;").replace("listen [::]:80;", "").replace("listen 443 ssl http2;", "listen 127.0.0.1:8443 ssl http2;").replace("listen [::]:443 ssl http2;", "")
    (ROOT / "nginx.conf").write_text("pid /work/nginx.pid; error_log /work/nginx-error.log; events {} http {" + rendered + "}")
    command("nginx", "-t", "-c", "/work/nginx.conf")
    unit = (bundle / "deploy/systemd/competence-hub-api.service.example").read_text().replace("__PORT__", "8001")
    (ROOT / "competence-hub-api.service").write_text(unit)
    command("systemd-analyze", "verify", str(ROOT / "competence-hub-api.service"))
    check("Nginx syntax and systemd unit verification", True)
    nginx = subprocess.Popen(["nginx", "-c", "/work/nginx.conf", "-g", "daemon off;"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        jar = CookieJar()
        opener = build_opener(HTTPCookieProcessor(jar), HTTPSHandler(context=ssl._create_unverified_context()), NoRedirect())
        def request(path, method="GET", data=None, headers=None, origin=ORIGIN):
            all_headers = {"Accept": "application/json", **(headers or {})}
            payload = None if data is None else json.dumps(data).encode()
            if payload is not None:
                all_headers["Content-Type"] = "application/json"
            try:
                response = opener.open(Request(origin + path, data=payload, headers=all_headers, method=method), timeout=20)
            except HTTPError as error:
                response = error
            return response.status, response.headers, response.read()
        for _ in range(50):
            try:
                status, headers, body = request("/health/ready")
                if status == 200:
                    break
            except OSError:
                pass
            time.sleep(.1)
        check("Actual packaged Linux runtime and PG readiness through HTTPS proxy", status == 200 and json.loads(body) == {"status": "ready"})
        status, headers, body = request("/health/live")
        check("Liveness returns minimal status only", status == 200 and json.loads(body) == {"status": "ok"})
        check("No-store and CSP survive reverse proxy", headers.get("Cache-Control") == "no-store" and "frame-ancestors 'none'" in headers.get("Content-Security-Policy", ""))
        check("Existing scoped HSTS policy retained", headers.get("Strict-Transport-Security") == "max-age=31536000")
        status, headers, _ = request("/portal", headers={"X-Forwarded-Proto": "http", "X-Forwarded-Host": "forged.example.invalid"})
        check("Forwarded proto/host spoof does not downgrade redirect", status in (307, 308) and headers.get("Location", "").startswith("https://localhost/"))
        status, headers, _ = request("/portal/", origin="http://localhost:8080")
        check("HTTP redirects to fixed HTTPS hostname", status == 301 and headers.get("Location") == "https://localhost/portal/")
        status, _, _ = request(ACCESS + "/session")
        check("Unauthenticated session denied through proxy", status == 401)
        for role, user in users.items():
            status, headers, body = request(ACCESS + "/login", "POST", {"email": f"{user}@example.invalid", "password": password},
                {"Origin": ORIGIN, "X-Forwarded-For": "198.51.100.88"})
            check(role + " actual password factor", status == 202)
            cookie = headers.get("Set-Cookie", "")
            check(role + " challenge cookie scope", all(value in cookie for value in ("Secure", "HttpOnly", "SameSite=lax", "Path=/")) and "Domain=" not in cookie)
            challenge = json.loads(body)["csrf_token"]
            status, _, _ = request(ACCESS + "/mfa/totp/enrollment", "POST", {}, {"Origin": "https://forged.example.invalid", "X-CSRF-Token": challenge})
            check(role + " foreign Origin denied", status == 403)
            status, _, body = request(ACCESS + "/mfa/totp/enrollment", "POST", {}, {"Origin": ORIGIN, "X-CSRF-Token": "wrong"})
            check(role + " wrong challenge CSRF denied", status == 401 and json.loads(body)["code"] == "authentication_failed")
            status, _, body = request(ACCESS + "/mfa/totp/enrollment", "POST", {}, {"Origin": ORIGIN, "X-CSRF-Token": challenge})
            check(role + " actual enrollment", status == 201)
            secret = parse_qs(urlsplit(json.loads(body)["provisioning_uri"]).query)["secret"][0]
            status, headers, body = request(ACCESS + "/mfa/totp/enrollment/confirm", "POST", {"code": pyotp.TOTP(secret).now()}, {"Origin": ORIGIN, "X-CSRF-Token": challenge})
            check(role + " actual TOTP completion", status == 200 and len(json.loads(body)["recovery_codes"]) == 10)
            cookies = headers.get_all("Set-Cookie", [])
            check(role + " Secure Host-only session cookie", any("__Host-" in cookie and "HttpOnly" in cookie and "Secure" in cookie and "SameSite=lax" in cookie and "Domain=" not in cookie for cookie in cookies))
            csrf = headers["X-CSRF-Token"]
            status, _, body = request(ACCESS + "/session")
            check(role + " session resume keeps exact role", status == 200 and json.loads(body)["user"]["roles"] == [role])
            status, _, _ = request("/api/v1/portal/companies")
            check(role + " no company rights", status in (401, 403))
            path = "/api/v1/portal/calendar/" + ("offers" if role == "coach" else "review-queue")
            status, _, _ = request(path)
            check(role + " correct Calendar workspace", status == 200)
            status, _, _ = request(ACCESS + "/session", "DELETE", headers={"Origin": ORIGIN, "X-CSRF-Token": "wrong"})
            check(role + " wrong logout CSRF denied", status == 403)
            status, _, _ = request(ACCESS + "/session", "DELETE", headers={"Origin": ORIGIN, "X-CSRF-Token": csrf})
            check(role + " actual logout", status == 204)
            status, _, _ = request(ACCESS + "/session")
            check(role + " revoked session denied", status == 401)
        forged = keyed_digest("login:ip:198.51.100.88", key).hex()
        check("Client X-Forwarded-For cannot create forged rate bucket", sql(f"SELECT count(*) FROM competence_hub.auth_rate_limit_buckets WHERE bucket_key_hash=decode('{forged}','hex');").strip() == "0")
        check("App and DB bound only to local addresses", all("127.0.0.1:" in line for line in command("ss", "-ltnH").splitlines() if ":8001 " in line or ":5432 " in line))
        ids = ",".join(f"'{user}'" for user in users.values())
        buckets = [keyed_digest(f"login:account:{user}@example.invalid", key) for user in users.values()]
        buckets += [keyed_digest(f"mfa:user:{user}", key) for user in users.values()]
        buckets += [keyed_digest(f"{action}:ip:127.0.0.1", key) for action in ("login", "mfa")]
        bucket_sql = ",".join(f"decode('{bucket.hex()}','hex')" for bucket in buckets)
        sql(f"SET ROLE competence_hub_owner; DELETE FROM competence_hub.audit_events WHERE actor_user_id IN ({ids}) OR entity_id IN ({ids}); DELETE FROM competence_hub.coaches WHERE id='{coach_id}'; DELETE FROM competence_hub.auth_rate_limit_buckets WHERE bucket_key_hash IN ({bucket_sql}); DELETE FROM competence_hub.portal_users WHERE id IN ({ids});")
        counts = {}
        for table in ("portal_users", "user_roles", "auth_password_credentials", "auth_login_challenges", "auth_sessions", "auth_one_time_tokens", "auth_totp_credentials", "auth_recovery_codes", "auth_rate_limit_buckets", "auth_idempotency_records", "auth_token_delivery_outbox", "companies", "company_contacts", "coaches", "topics", "coach_topics", "calendar_offers", "calendar_offer_revisions", "calendar_review_decisions", "audit_events"):
            counts[table] = int(sql(f"SELECT count(*) FROM competence_hub.{table};"))
        check("Exact synthetic cleanup: all 20 local tables zero", not any(counts.values()))
        report["after_counts"] = counts
        report["status"] = "PASS"
    finally:
        nginx.terminate()
        nginx.wait(timeout=15)
        server.should_exit = True
        thread.join(timeout=15)
        command("pg_ctlcluster", "16", "main", "stop")


if __name__ == "__main__":
    report = {"environment": "local-disposable-Ubuntu-container", "status": "NOT_RUN", "checks": [], "vps_changed": False}
    try:
        main(report)
    except Exception as error:
        report["status"] = "FAIL"
        report["failure_type"] = type(error).__name__
        report["failure_frames"] = [{"function": frame.name, "line": frame.lineno} for frame in traceback.extract_tb(error.__traceback__)
                                    if Path(frame.filename).name == Path(__file__).name]
    (ROOT / "proxy-result.json").write_text(json.dumps(report, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
