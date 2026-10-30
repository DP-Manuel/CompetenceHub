"""One named Staging Admin, human MFA, durable operator-supplied key custody.

No fixture, Coach import, role expansion, public service or captured secrets.
The enclosing reviewed operator window must create/verify the current encrypted
snapshot and external restore before invoking this interactive command.
"""

import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
import getpass
import hashlib
import ipaddress
import importlib.util
import json
import logging
import os
from pathlib import Path
import re
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
from uuid import uuid4

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from playwright.sync_api import sync_playwright
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
import uvicorn

from competence_hub_api.auth.account_administration import InitialAdminService
from competence_hub_api.auth.postgres_account_administration import (
    PostgresInitialAdminRepository,
)
from competence_hub_api.config import RuntimeSettings
from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.email_addresses import is_single_email_address
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService

ROOT = Path(__file__).resolve().parents[3]
DATABASE = "competence_hub_staging"
ACCESS = "/api/v1/portal/access"
PROOF_SCHEMA = "competence-hub.prechange-restore-proof.v1"
NATIVE_WAIT_SECONDS = 900
RESTORE_IMAGE = (
    "postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825"
)
_baseline_spec = importlib.util.spec_from_file_location(
    "operator_restore_baseline",
    ROOT / "deploy/scripts/verify-prechange-restore-baseline.py",
)
baseline_verifier = importlib.util.module_from_spec(_baseline_spec)
_baseline_spec.loader.exec_module(baseline_verifier)


class OperatorStop(ValueError):
    pass


def require(value, code):
    if not value:
        raise OperatorStop(code)


def target_urls(environment):
    values = [
        environment.get("COMPETENCE_HUB_OPERATOR_" + kind + "_URL", "")
        for kind in ("APP", "OWNER")
    ]
    for raw, role in zip(values, ("competence_hub_app", "competence_hub_migrator")):
        url = make_url(raw)
        require(
            (url.drivername, url.host, url.port, url.database, url.username)
            == ("postgresql+asyncpg", "127.0.0.1", 55432, DATABASE, role)
            and url.password
            and not url.query,
            "STAGING_TARGET_REQUIRED",
        )
    return values


def require_private_environment(environment):
    pattern = re.compile(
        r"^(DEBUG|PWDEBUG|PW_|PLAYWRIGHT_|NODE_|PYTHON(INSPECT|STARTUP|BREAKPOINT|HOME|USERBASE|ASYNCIODEBUG)$)",
        re.IGNORECASE,
    )
    require(
        not any(pattern.match(name) for name in environment),
        "PRIVATE_DIAGNOSTIC_ENVIRONMENT_REQUIRED",
    )
    if "PYTHONPATH" in environment:
        require(
            environment["PYTHONPATH"] == str(ROOT / "apps" / "webapp" / "src"),
            "REVIEWED_PYTHON_IMPORT_PATH_REQUIRED",
        )


def read_login(path):
    path = Path(path).resolve()
    require(
        path.is_relative_to(ROOT / ".tmp") and path.stat().st_size < 4096,
        "PRIVATE_APPROVED_LOGIN_FILE_REQUIRED",
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    require(
        set(value)
        == {
            "schema",
            "display_name",
            "email",
            "roles",
            "target_database",
            "environment",
            "source",
            "coach_mapping",
            "calendar_mapping",
        },
        "STRICT_APPROVED_LOGIN_FIELDS_REQUIRED",
    )
    require(
        value.get("schema") == 1
        and value.get("display_name") == "Manuel"
        and value.get("roles") == ["admin"]
        and value.get("target_database") == DATABASE
        and value.get("environment") == "staging"
        and value.get("coach_mapping") is None
        and value.get("calendar_mapping") is None,
        "NAMED_ADMIN_ONLY_SCOPE",
    )
    require(
        is_single_email_address(value.get("email", "")), "EXPLICIT_LOGIN_EMAIL_REQUIRED"
    )
    return value


def verify_restore_proof(path, backup_set, now):
    directory, proof_path = Path(backup_set).resolve(), Path(path).resolve()
    require(
        not directory.is_relative_to(ROOT)
        and not ROOT.is_relative_to(directory)
        and not proof_path.is_relative_to(ROOT),
        "PROTECTED_EXTERNAL_RESTORE_REQUIRED",
    )
    require(proof_path.stat().st_size <= 1024 * 1024, "RESTORE_PROOF_SIZE")
    proof = json.loads(
        baseline_verifier.regular_bytes(proof_path).decode("utf-8-sig"),
        object_pairs_hook=baseline_verifier.unique_object,
    )
    require(
        proof.get("schema") == PROOF_SCHEMA
        and proof.get("status") == "PASS"
        and Path(proof.get("source_directory", "")).resolve() == directory,
        "ACTUAL_RESTORE_PROOF_REQUIRED",
    )
    require(
        all(
            proof.get(key) is True
            for key in (
                "owners_verified",
                "encrypted_copy_verified",
                "temporary_database_removed",
                "container_removed",
                "plaintext_removed",
            )
        ),
        "RESTORE_OR_CLEANUP_INCOMPLETE",
    )
    finished = datetime.fromisoformat(proof["finished_at_utc"])
    require(
        finished.tzinfo is not None and 0 <= (now - finished).total_seconds() <= 14400,
        "CURRENT_RESTORE_REQUIRED",
    )
    metadata = baseline_verifier.regular_bytes(directory / "METADATA")
    summary = baseline_verifier.validate_metadata(metadata)
    header = json.loads(metadata.splitlines()[0])
    snapshot_time = datetime.strptime(
        header["created_at_utc"], "%Y%m%dT%H%M%SZ"
    ).replace(tzinfo=UTC)
    require(
        0 <= (now - snapshot_time).total_seconds() <= 14400
        and snapshot_time <= finished,
        "CURRENT_SNAPSHOT_REQUIRED",
    )
    require(
        proof.get("restore_image") == RESTORE_IMAGE
        and all(
            proof.get(field) == summary[field]
            for field in ("baseline_sha256", "migrations", "row_counts")
        ),
        "RESTORE_BASELINE_BINDING_REQUIRED",
    )
    for filename, field in (
        ("database.dump.gpg", "dump_gpg_sha256"),
        ("METADATA", "metadata_sha256"),
    ):
        # Dumps can exceed the baseline reader's 8 MiB limit; stream the ciphertext.
        require(
            (directory / filename).is_file()
            and not (directory / filename).is_symlink(),
            "RESTORE_INPUT_UNSAFE",
        )
        with (directory / filename).open("rb") as handle:
            actual = hashlib.file_digest(handle, "sha256").hexdigest()
        require(actual == proof.get(field), "RESTORED_COPY_CHANGED")
    require(
        proof.get("migrations")
        in [[f"{i:04}" for i in range(1, count + 1)] for count in range(6, 10)],
        "SCHEMA_HISTORY_REJECTED",
    )
    return proof


def run_async(action):
    # Sync Playwright owns an event loop in its caller thread. Database work
    # belongs on a separate worker, as in the existing native fixture.
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(lambda: asyncio.run(action())).result()


def reserve_receipt(output):
    require(
        not output.is_relative_to(ROOT)
        and output.parent.is_dir()
        and not output.exists(),
        "NEW_PROTECTED_OPERATOR_BINDING_REQUIRED",
    )
    if os.name == "nt":
        environment = {
            key: os.environ[key]
            for key in (
                "PATH",
                "SystemRoot",
                "SystemDrive",
                "WINDIR",
                "TEMP",
                "TMP",
                "LOCALAPPDATA",
                "USERPROFILE",
                "COMSPEC",
                "ProgramFiles",
                "ProgramData",
            )
            if key in os.environ
        }
        environment.update(
            OPERATOR_CUSTODY_HELPER=str(
                ROOT / "deploy/scripts/initialize-staging-operator-config.ps1"
            ),
            OPERATOR_RECEIPT_PARENT=str(output.parent),
        )
        checked = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                ". $env:OPERATOR_CUSTODY_HELPER; Assert-StagingPrivateAcl $env:OPERATOR_RECEIPT_PARENT -Directory",
            ],
            env=environment,
            capture_output=True,
        )
        require(checked.returncode == 0, "PROTECTED_RECEIPT_DIRECTORY_REQUIRED")
    else:
        require(
            output.parent.stat().st_mode & 0o077 == 0,
            "PROTECTED_RECEIPT_DIRECTORY_REQUIRED",
        )
    initial = {
        "status": "NOT_COMPLETE",
        "phase": "preflight",
        "account_creation": "NOT_ATTEMPTED",
        "real_coach_apply": "DISABLED",
    }
    with output.open("x", encoding="utf-8") as handle:
        json.dump(initial, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    return initial


def persist_receipt(output, result):
    temporary = output.with_name(output.name + "." + uuid4().hex + ".pending")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)


async def inspect(owner_url, *, email=None, expected_baseline=None):
    engine = create_async_engine(owner_url, hide_parameters=True)
    try:
        async with engine.begin() as c:
            await c.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            require(
                await c.scalar(text("SELECT current_database()")) == DATABASE,
                "WRONG_DATABASE",
            )
            require(
                await c.scalar(text("SHOW listen_addresses")) == "localhost",
                "POSTGRES_NOT_LOCALHOST",
            )
            versions = list(
                (
                    await c.execute(
                        text(
                            "SELECT version FROM competence_hub.schema_migrations ORDER BY version"
                        )
                    )
                ).scalars()
            )
            require(
                versions
                in [[f"{i:04}" for i in range(1, count + 1)] for count in range(6, 10)],
                "UNEXPECTED_SCHEMA",
            )
            counts = {}
            table_names = (
                await c.execute(
                    text(
                        "SELECT n.nspname,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname<>'information_schema' AND n.nspname !~ '^pg_' AND c.relkind IN ('r','p','m')"
                    )
                )
            ).all()
            for schema, name in table_names:
                require(
                    re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", schema)
                    and re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name),
                    "UNEXPECTED_IDENTIFIER",
                )
                counts[schema + "." + name] = await c.scalar(
                    text(f'SELECT count(*) FROM "{schema}"."{name}"')
                )
            if expected_baseline is not None:
                require(
                    versions == expected_baseline["migrations"]
                    and counts == expected_baseline["row_counts"],
                    "DATABASE_CHANGED_AFTER_BACKUP",
                )
            result = {
                "migrations": versions,
                "row_counts": counts,
                "now": await c.scalar(text("SELECT clock_timestamp()")),
            }
            if email:
                found = (
                    (
                        await c.execute(
                            text(
                                "SELECT id,active FROM competence_hub.portal_users WHERE lower(email)=:email"
                            ),
                            {"email": email.casefold()},
                        )
                    )
                    .mappings()
                    .all()
                )
                require(
                    len(found) == 1 and found[0]["active"],
                    "EXACT_ACTIVE_ADMIN_NOT_FOUND",
                )
                user = found[0]["id"]
                roles = list(
                    (
                        await c.execute(
                            text(
                                "SELECT r.code FROM competence_hub.user_roles ur JOIN competence_hub.roles r ON r.id=ur.role_id WHERE ur.user_id=:id AND r.active ORDER BY r.code"
                            ),
                            {"id": user},
                        )
                    ).scalars()
                )
                require(roles == ["admin"], "UNEXPECTED_ADDITIONAL_ROLE")
                require(
                    await c.scalar(
                        text(
                            "SELECT count(*) FROM competence_hub.coaches WHERE portal_user_id=:id"
                        ),
                        {"id": user},
                    )
                    == 0,
                    "UNAUTHORIZED_COACH_MAPPING",
                )
                result.update(
                    user_id=str(user),
                    roles=roles,
                    enrolled=bool(
                        await c.scalar(
                            text(
                                "SELECT count(*) FROM competence_hub.auth_totp_credentials WHERE portal_user_id=:id AND enabled_at IS NOT NULL"
                            ),
                            {"id": user},
                        )
                    ),
                    recovery_count=await c.scalar(
                        text(
                            "SELECT count(*) FROM competence_hub.auth_recovery_codes WHERE portal_user_id=:id"
                        ),
                        {"id": user},
                    ),
                    recovery_used=await c.scalar(
                        text(
                            "SELECT count(*) FROM competence_hub.auth_recovery_codes WHERE portal_user_id=:id AND used_at IS NOT NULL"
                        ),
                        {"id": user},
                    ),
                )
            return result
    finally:
        await engine.dispose()


async def bootstrap(app_url, settings, login, password, now, *, deadline):
    engine = create_async_engine(app_url, hide_parameters=True)
    try:
        service = InitialAdminService(
            PostgresInitialAdminRepository(
                engine, require_empty_target=True, bootstrap_deadline=deadline
            ),
            PasswordService(PasswordPolicy(settings.compromised_password_fingerprints)),
        )
        return await service.create_initial_admin(
            email=login["email"], display_name="Manuel", password=password, now=now
        )
    finally:
        await engine.dispose()


def verify_postconditions(baseline, state):
    require(
        state["enrolled"]
        and state["recovery_count"] == 10
        and state["roles"] == ["admin"],
        "NATIVE_POSTCONDITIONS_FAILED",
    )
    expected = {
        "competence_hub.portal_users": 1,
        "competence_hub.user_roles": 1,
        "competence_hub.auth_password_credentials": 1,
        "competence_hub.auth_totp_credentials": 1,
        "competence_hub.auth_recovery_codes": 10,
    }
    require(
        all(state["row_counts"].get(name) == count for name, count in expected.items()),
        "EXACT_ONE_ADMIN_SCOPE_FAILED",
    )
    require(state["migrations"] == baseline["migrations"], "UNAUTHORIZED_MIGRATION")
    require(
        set(state["row_counts"]) == set(baseline["row_counts"]),
        "UNAUTHORIZED_SCHEMA_CHANGE",
    )
    for name, count in baseline["row_counts"].items():
        if name in {
            "competence_hub.portal_users",
            "competence_hub.user_roles",
            "competence_hub.audit_events",
        } or name.startswith("competence_hub.auth_"):
            continue
        require(state["row_counts"][name] == count, "UNAUTHORIZED_BUSINESS_MUTATION")


@contextmanager
def operator_server(settings_factory):
    # Only TLS keys are temporary; the actual MFA/recovery keys come from durable
    # protected operator configuration, never a synthetic fixture or this helper.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    base = f"https://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(
        prefix="competence-hub-operator-tls-"
    ) as temporary:
        root = Path(temporary)
        if os.name == "nt":
            import subprocess

            sid = subprocess.check_output(
                ["whoami", "/user", "/fo", "csv", "/nh"], text=True
            )
            import csv, io

            sid = next(csv.reader(io.StringIO(sid)))[1]
            subprocess.run(
                [
                    "icacls",
                    str(root),
                    "/inheritance:r",
                    "/grant:r",
                    f"*{sid}:(OI)(CI)F",
                    "*S-1-5-18:(OI)(CI)F",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = x509.Name(
            [
                x509.NameAttribute(
                    NameOID.COMMON_NAME, "Competence Hub private Staging operator"
                )
            ]
        )
        now = datetime.now(UTC)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(private.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(hours=8))
            .add_extension(
                x509.SubjectAlternativeName(
                    [x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
                ),
                critical=False,
            )
            .sign(private, hashes.SHA256())
        )
        cert, key = root / "certificate.pem", root / "key.pem"
        cert.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        key.write_bytes(
            private.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        key.chmod(0o600)
        settings = settings_factory(base)
        server = uvicorn.Server(
            uvicorn.Config(
                create_runtime_app(settings),
                host="127.0.0.1",
                port=port,
                ssl_certfile=str(cert),
                ssl_keyfile=str(key),
                access_log=False,
                log_level="critical",
            )
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 30
            while not server.started:
                require(
                    thread.is_alive() and time.monotonic() < deadline,
                    "PRIVATE_RUNTIME_DID_NOT_START",
                )
                time.sleep(0.1)
            yield base
        finally:
            server.should_exit = True
            thread.join(timeout=15)
            require(not thread.is_alive(), "PRIVATE_RUNTIME_CLEANUP_FAILED")


def manual_native(base, login, password, *, owner_url):
    def notice(message):
        # The key-custody scope deliberately suppresses stdout to avoid key
        # disclosure. Human instructions use the inherited private terminal.
        print(message, file=sys.stderr, flush=True)

    def wait_for(page, predicate, code):
        deadline = time.monotonic() + NATIVE_WAIT_SECONDS
        while time.monotonic() < deadline and not page.is_closed():
            if predicate():
                return
            page.wait_for_timeout(250)
        raise ValueError(code)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=False)
        context = browser.new_context(
            ignore_https_errors=True, timezone_id="Europe/Berlin"
        )
        # Certificate exception exists ONLY in this isolated context and no
        # request may leave the owned loopback origin. No machine trust changes.
        context.route(
            "**/*",
            lambda route: (
                route.continue_()
                if route.request.url.startswith(base + "/")
                else route.abort()
            ),
        )
        page = context.new_page()
        try:
            require(
                context.request.get(base + "/api/v1/admin/coaches").status == 401,
                "UNAUTHENTICATED_ADMIN_ROUTE_NOT_BLOCKED",
            )

            def sign_in():
                page.goto(base + "/portal/", wait_until="domcontentloaded")
                page.locator("#login-email").fill(login["email"])
                page.locator("#login-password").fill(password)
                page.get_by_role("button", name="Anmelden", exact=True).click()

            def logout():
                page.get_by_role("button", name="Abmelden", exact=True).click()
                wait_for(
                    page,
                    lambda: page.locator("#login-view").is_visible(),
                    "LOGOUT_NOT_PROVEN",
                )
                require(
                    context.request.get(base + ACCESS + "/session").status == 401,
                    "LOGOUT_SESSION_STILL_ACTIVE",
                )

            def session():
                response = context.request.get(base + ACCESS + "/session")
                require(
                    response.status == 200
                    and response.headers.get("cache-control") == "no-store",
                    "SESSION_OR_NO_STORE_FAILED",
                )
                require(
                    response.json()["user"]["roles"] == ["admin"],
                    "NATIVE_ADMIN_ROLE_NOT_EXACT",
                )

            sign_in()
            notice(
                "Im eigenen Edge-Fenster Authenticator einrichten. Recovery-Codes nur lokal sicher ablegen und bestaetigen. Keine Codes in Chat/Terminal senden."
            )
            wait_for(
                page,
                lambda: page.locator("#portal-view").is_visible(),
                "HUMAN_MFA_NOT_COMPLETED",
            )
            session()
            page.reload(wait_until="domcontentloaded")
            wait_for(
                page,
                lambda: page.locator("#portal-view").is_visible(),
                "SESSION_RESUME_FAILED",
            )
            session()
            require(
                context.request.get(base + "/api/v1/portal/companies").status == 200,
                "ADMIN_ROUTE_FAILED",
            )
            registry = context.request.get(base + "/api/v1/admin/coaches")
            require(
                registry.status == 503
                and registry.json().get("code") == "registry_unavailable",
                "ADMIN_AUTHORIZATION_OR_INACTIVE_REGISTRY_BOUNDARY_FAILED",
            )
            require(
                page.evaluate(
                    "localStorage.length === 0 && sessionStorage.length === 0"
                ),
                "TOKEN_STORAGE_REJECTED",
            )
            logout()
            sign_in()
            notice(
                "Bitte im Browser den aktuellen Authenticator-Code eingeben (gegebenenfalls den naechsten 30-Sekunden-Code abwarten)."
            )
            wait_for(
                page,
                lambda: page.locator("#portal-view").is_visible(),
                "MFA_CHALLENGE_NOT_COMPLETED",
            )
            session()
            logout()
            sign_in()
            wait_for(
                page,
                lambda: page.locator("#mfa-view").is_visible(),
                "RECOVERY_CHALLENGE_NOT_SHOWN",
            )
            page.get_by_role("radio", name="Recovery-Code", exact=True).check()
            notice(
                "Recovery-Test: im Browser EINEN sicher abgelegten Recovery-Code verwenden. Dieser Code wird dabei verbraucht."
            )
            wait_for(
                page,
                lambda: page.locator("#portal-view").is_visible(),
                "RECOVERY_LOGIN_NOT_COMPLETED",
            )
            session()
            after_recovery = run_async(lambda: inspect(owner_url, email=login["email"]))
            require(after_recovery["recovery_used"] >= 1, "RECOVERY_USE_NOT_PROVEN")
            logout()
            sign_in()
            wait_for(
                page,
                lambda: page.locator("#mfa-view").is_visible(),
                "RECOVERY_CHALLENGE_NOT_SHOWN",
            )
            page.get_by_role("radio", name="Recovery-Code", exact=True).check()
            notice(
                "Wiederholungspruefung: denselben gerade verbrauchten Recovery-Code nochmals im Browser eingeben. Die Ablehnung ist hier erwartet."
            )
            wait_for(
                page,
                lambda: page.locator("#mfa-error").is_visible(),
                "RECOVERY_REPLAY_NOT_REJECTED",
            )
            require(
                context.request.get(base + ACCESS + "/session").status == 401,
                "REPLAY_CREATED_SESSION",
            )
            return {
                key: "PASS"
                for key in (
                    "login",
                    "mfa_enrollment",
                    "mfa_challenge",
                    "recovery_login",
                    "recovery_single_use",
                    "session",
                    "session_resume",
                    "logout",
                    "admin_rbac",
                    "registry_remains_inactive",
                    "no_web_storage",
                )
            }
        finally:
            # Never read provisioning-seed/recovery-code DOM, screenshots, traces,
            # response-body dumps or storage-state exports for the real operator.
            context.close()
            browser.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--login-file", required=True)
    parser.add_argument("--restore-proof", required=True)
    parser.add_argument("--backup-set", required=True)
    parser.add_argument("--binding-output", required=True)
    args = parser.parse_args(argv)
    require_private_environment(os.environ)
    output = Path(args.binding_output).resolve()
    require(
        __import__("sys").stdin.isatty() and __import__("sys").stderr.isatty(),
        "INTERACTIVE_OPERATOR_TERMINAL_REQUIRED",
    )
    for name in ("sqlalchemy.engine", "uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
    app_url, owner_url = target_urls(os.environ)
    login = read_login(args.login_file)
    proof = verify_restore_proof(args.restore_proof, args.backup_set, datetime.now(UTC))
    baseline = asyncio.run(inspect(owner_url, expected_baseline=proof))
    require(
        abs((datetime.now(UTC) - baseline["now"]).total_seconds()) <= 10,
        "CLOCK_SYNCHRONIZATION_REQUIRED",
    )
    require(
        baseline["row_counts"].get("competence_hub.portal_users") == 0
        and baseline["row_counts"].get("competence_hub.coaches") == 0,
        "FRESH_ADMIN_BOOTSTRAP_SCOPE_ONLY",
    )
    values = {
        **os.environ,
        "COMPETENCE_HUB_DATABASE_URL": app_url,
        "COMPETENCE_HUB_ALLOWED_ORIGIN": "https://127.0.0.1:443",
    }
    RuntimeSettings.from_environment(values)
    result = reserve_receipt(output)
    password = ""
    try:
        password = getpass.getpass("Neues starkes Passwort fuer den Staging-Admin: ")
        confirmation = getpass.getpass("Passwort wiederholen: ")
        require(password == confirmation, "PASSWORD_CONFIRMATION_MISMATCH")
        confirmation = ""
        # Human prompts have no bounded duration. Recheck all counts and both
        # snapshot/restore ages immediately before the guarded transaction.
        proof = verify_restore_proof(
            args.restore_proof, args.backup_set, datetime.now(UTC)
        )
        baseline = asyncio.run(inspect(owner_url, expected_baseline=proof))
        require(
            abs((datetime.now(UTC) - baseline["now"]).total_seconds()) <= 10,
            "CLOCK_SYNCHRONIZATION_REQUIRED",
        )
        result["phase"] = "bootstrap"
        result["account_creation"] = "ATTEMPTED_CHECK_REQUIRED"
        persist_receipt(output, result)
        deadline = min(
            datetime.fromisoformat(proof["finished_at_utc"]),
            datetime.strptime(
                json.loads(
                    (Path(args.backup_set) / "METADATA").read_bytes().splitlines()[0]
                )["created_at_utc"],
                "%Y%m%dT%H%M%SZ",
            ).replace(tzinfo=UTC),
        ) + timedelta(hours=4)
        user_id = asyncio.run(
            bootstrap(
                app_url,
                RuntimeSettings.from_environment(values),
                login,
                password,
                baseline["now"],
                deadline=deadline,
            )
        )
        result.update(
            account_creation="CONFIRMED",
            account_created=True,
            operator_user_id=str(user_id),
            roles=["admin"],
            coach_mapping=None,
            calendar_mapping=None,
        )
        persist_receipt(output, result)
        result["phase"] = "private_native_authentication"
        with operator_server(
            lambda base: RuntimeSettings.from_environment(
                {**values, "COMPETENCE_HUB_ALLOWED_ORIGIN": base}
            )
        ) as base:
            result["native"] = manual_native(base, login, password, owner_url=owner_url)
        state = asyncio.run(inspect(owner_url, email=login["email"]))
        verify_postconditions(baseline, state)
        result.update(
            status="PASS",
            phase="complete",
            mfa_enrolled=True,
            recovery_count=10,
            recovery_used=state["recovery_used"],
        )
    except Exception as error:
        result["failure_type"] = type(error).__name__
        if isinstance(error, OperatorStop):
            result["gate"] = str(error)
    finally:
        password = ""
        persist_receipt(output, result)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "operator_user_id"}, sort_keys=True
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(
            json.dumps(
                {
                    "status": "STOP",
                    "failure_type": type(error).__name__,
                    "gate": (
                        str(error)
                        if isinstance(error, OperatorStop)
                        else "SANITIZED_OPERATOR_FAILURE"
                    ),
                    "acceptance": "NOT_COMPLETE",
                }
            )
        )
        raise SystemExit(1)
