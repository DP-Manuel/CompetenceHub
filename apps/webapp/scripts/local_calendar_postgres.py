"""Owned loopback-only PostgreSQL16 fixture. Never connects to existing databases."""
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
DOCKER = ["docker", "--host", "npipe:////./pipe/dockerDesktopLinuxEngine"]
ENV_NAMES = ("COMPETENCE_HUB_TEST_APP_DATABASE_URL", "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL")


class LocalCalendarPostgres:
    def __init__(self):
        self.container = None
        self.volume = None
        self.volume_removed = False
        self.removed = False

    def command(self, *args, data=None, environment=None, allow_failure=False):
        result = subprocess.run([*DOCKER, *args], input=data, text=True, encoding="utf8",
            capture_output=True, env=environment, timeout=90)
        if result.returncode and not allow_failure:
            raise RuntimeError("Owned local PostgreSQL operation failed; no external fallback")
        return result

    def sql(self, content, database="competence_hub_staging"):
        return self.command("exec", "-i", self.container, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "-U", "postgres", "-d", database, data=content).stdout

    def __enter__(self):
        if any(name in os.environ for name in ENV_NAMES):
            raise RuntimeError("Refusing existing database configuration; no value was inspected")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 55433))
        self.command("image", "inspect", "postgres:16-bookworm", "--format", "{{.Id}}")
        try:
            name = "competence-hub-cal1-pilot-" + uuid4().hex
            if self.command("volume", "inspect", name, "--format", "{{.Name}}", allow_failure=True).returncode == 0:
                raise RuntimeError("Refusing existing volume")
            created = self.command("volume", "create", "--label", "competence-hub.scope=local-synthetic-calendar", name).stdout.strip()
            if created != name:
                raise RuntimeError("Owned volume identity unconfirmed")
            self.volume = name
            environment = {**os.environ, "POSTGRES_PASSWORD": secrets.token_urlsafe(48)}
            result = self.command("run", "--detach", "--name", "competence-hub-cal1-pilot-" + uuid4().hex,
                "--label", "competence-hub.scope=local-synthetic-calendar", "--publish", "127.0.0.1:55433:5432",
                "--env", "POSTGRES_PASSWORD", "--mount", f"type=volume,source={self.volume},target=/var/lib/postgresql/data", "postgres:16-bookworm",
                environment=environment)
            self.container = result.stdout.strip()
            if not re.fullmatch(r"[a-f0-9]{64}", self.container):
                raise RuntimeError("Owned container identity was not confirmed")
            for _ in range(60):
                # The image's temporary init server accepts Unix sockets before
                # initialization finishes. Only the final server listens on TCP.
                if self.command("exec", self.container, "pg_isready", "-h", "127.0.0.1", "-U", "postgres", allow_failure=True).returncode == 0:
                    break
                time.sleep(.5)
            else:
                raise RuntimeError("Owned PostgreSQL did not become ready")
            self.sql((ROOT / "database/bootstrap-staging.sql").read_text(encoding="utf8"), "postgres")
            for version in range(1, 7):
                files = list((ROOT / "database/migrations").glob(f"{version:04d}_*.sql"))
                if len(files) != 1:
                    raise RuntimeError("Expected exactly six existing Calendar migrations")
                self.sql(files[0].read_text(encoding="utf8"))
            passwords = [secrets.token_hex(32), secrets.token_hex(32)]
            self.sql(f"ALTER ROLE competence_hub_app PASSWORD '{passwords[0]}'; ALTER ROLE competence_hub_migrator PASSWORD '{passwords[1]}';", "postgres")
            for name, role, password in zip(ENV_NAMES, ("competence_hub_app", "competence_hub_migrator"), passwords):
                os.environ[name] = f"postgresql+asyncpg://{role}:{password}@127.0.0.1:55433/competence_hub_staging"
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_):
        for name in ENV_NAMES:
            os.environ.pop(name, None)
        if self.container and re.fullmatch(r"[a-f0-9]{64}", self.container):
            self.command("rm", "--force", self.container)
            self.removed = not self.command("ps", "--all", "--quiet", "--no-trunc", "--filter", f"id={self.container}").stdout.strip()
            if not self.removed:
                raise RuntimeError("Owned local PostgreSQL cleanup unconfirmed")
        if self.volume and re.fullmatch(r"competence-hub-cal1-pilot-[a-f0-9]{32}", self.volume):
            self.command("volume", "rm", self.volume)
            self.volume_removed = self.volume not in self.command("volume", "ls", "--format", "{{.Name}}", "--filter", f"name={self.volume}").stdout.splitlines()
            if not self.volume_removed:
                raise RuntimeError("Owned local PostgreSQL volume cleanup unconfirmed")

    def restart(self):
        if not self.container or not self.volume:
            raise RuntimeError("Owned persistent fixture required")
        self.command("restart", self.container)
        for _ in range(60):
            if self.command("exec", self.container, "pg_isready", "-h", "127.0.0.1", "-U", "postgres", allow_failure=True).returncode == 0:
                return
            time.sleep(.5)
        raise RuntimeError("Owned PostgreSQL restart unconfirmed")
