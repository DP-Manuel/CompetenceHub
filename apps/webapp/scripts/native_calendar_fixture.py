"""Opt-in isolated Staging data, exact-ID cleanup and a real runtime app."""
import asyncio
from contextlib import asynccontextmanager, suppress
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, timedelta
import os
import secrets
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.config import RuntimeSettings
from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.tokens import keyed_digest

TABLES = (
    "portal_users", "user_roles", "auth_password_credentials", "auth_login_challenges",
    "auth_sessions", "auth_one_time_tokens", "auth_totp_credentials", "auth_recovery_codes",
    "auth_rate_limit_buckets", "auth_idempotency_records", "auth_token_delivery_outbox",
    "companies", "company_contacts", "coaches", "topics", "coach_topics", "calendar_offers",
    "calendar_offer_revisions", "calendar_review_decisions", "audit_events",
)


def staging_urls(environment):
    urls = []
    for name, role in (
        ("COMPETENCE_HUB_TEST_APP_DATABASE_URL", "competence_hub_app"),
        ("COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL", "competence_hub_migrator"),
    ):
        value = environment.get(name)
        if not value:
            raise ValueError("Supply isolated Staging process configuration through the interactive runner")
        url = make_url(value)
        if (url.drivername != "postgresql+asyncpg" or url.host != "127.0.0.1"
                or url.database != "competence_hub_staging" or url.username != role
                or not url.password or url.query):
            raise ValueError("Refusing non-isolated Staging configuration")
        urls.append(value)
    left, right = map(make_url, urls)
    if left.port != right.port:
        raise ValueError("Staging connections must share one tunnel")
    return tuple(urls)


class NativeCalendarFixture:
    def __init__(self, *, local_container_rehearsal=False):
        self.app_url, self.owner_url = staging_urls(os.environ)
        self.local_container_rehearsal = local_container_rehearsal
        if local_container_rehearsal and make_url(self.app_url).port != 55433:
            raise ValueError("Container rehearsal is restricted to loopback port 55433")
        self.roles = {"coach": "coach", "coach_two": "coach", "reviewer": "calendar_reviewer",
                      "admin": "admin", "internal": "internal", "contact": "company_contact"}
        self.users = {key: uuid4() for key in self.roles}
        self.coaches = {key: uuid4() for key in ("coach", "coach_two")}
        self.emails = {key: f"synthetic-native-ui-{value.hex}@example.invalid" for key, value in self.users.items()}
        self.topic = uuid4()
        self.password = secrets.token_urlsafe(32)
        self.rate_key = secrets.token_bytes(32)
        self.now = None
        self.provisioned = False
        self.cleanup_pass = False
        self.baseline = None
        self.after = None

    def database(self, action):
        async def run():
            engine = create_async_engine(self.owner_url, hide_parameters=True, pool_pre_ping=True)
            try:
                async with engine.begin() as connection:
                    await connection.execute(text("SET LOCAL ROLE competence_hub_owner"))
                    return await action(connection)
            finally:
                await engine.dispose()
        # Playwright's sync driver owns a loop on the caller thread.
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(lambda: asyncio.run(run())).result()

    async def counts(self, connection):
        return {table: await connection.scalar(text(f"SELECT count(*) FROM competence_hub.{table}"))
                for table in TABLES}

    def prepare(self):
        password_hash = PasswordService(PasswordPolicy(frozenset())).hash(self.password)
        async def seed(connection):
            self.baseline = await self.counts(connection)
            if any(self.baseline.values()):
                raise RuntimeError("Staging dynamic tables are not empty; no fixture will be created")
            versions = (await connection.execute(text("SELECT version FROM competence_hub.schema_migrations ORDER BY version"))).scalars().all()
            if versions != ["0001", "0002", "0003", "0004", "0005", "0006"]:
                raise RuntimeError("Staging migration preflight failed; no migration is performed")
            listen = await connection.scalar(text("SHOW listen_addresses"))
            if listen != "localhost" and not (self.local_container_rehearsal and listen == "*"):
                raise RuntimeError("PostgreSQL must remain localhost-only")
            self.now = (await connection.scalar(text("SELECT clock_timestamp()"))).astimezone(UTC)
            for key, user in self.users.items():
                await connection.execute(text("INSERT INTO competence_hub.portal_users (id,display_name,email,active) VALUES (:id,:name,:email,true)"),
                    {"id": user, "name": {"coach": "Coach A", "coach_two": "Coach B", "reviewer": "Reviewer A", "admin": "Admin A", "internal": "Internal A", "contact": "Company Contact A"}[key], "email": self.emails[key]})
                result = await connection.execute(text("INSERT INTO competence_hub.user_roles (user_id,role_id) SELECT :id,id FROM competence_hub.roles WHERE code=:role AND active"), {"id": user, "role": self.roles[key]})
                if result.rowcount != 1:
                    raise RuntimeError("Required static role is missing or inactive")
                await connection.execute(text("INSERT INTO competence_hub.auth_password_credentials (portal_user_id,password_hash) VALUES (:id,:hash)"), {"id": user, "hash": password_hash})
            for key, coach in self.coaches.items():
                await connection.execute(text("INSERT INTO competence_hub.coaches (id,portal_user_id,display_name,public_profile_status,public_profile_path) VALUES (:id,:user,:name,'synthetic',NULL)"), {"id": coach, "user": self.users[key], "name": "Coach A" if key == "coach" else "Coach B"})
            await connection.execute(text("INSERT INTO competence_hub.topics (id,name,active) VALUES (:id,:name,true)"), {"id": self.topic, "name": "Führung und Zusammenarbeit"})
            for coach in self.coaches.values():
                await connection.execute(text("INSERT INTO competence_hub.coach_topics (coach_id,topic_id) VALUES (:coach,:topic)"), {"coach": coach, "topic": self.topic})
        self.database(seed)
        self.provisioned = True

    def app(self, port):
        settings = RuntimeSettings(
            database_url=self.app_url, allowed_origin=f"https://127.0.0.1:{port}",
            session_idle_timeout=timedelta(minutes=30), readiness_timeout_seconds=15,
            rate_limit_hmac_key=self.rate_key, idempotency_hmac_key=secrets.token_bytes(32),
            outbox_encryption_keys={"native-ui": secrets.token_bytes(32)}, outbox_active_key_version="native-ui",
            compromised_password_fingerprints=frozenset({"0" * 64}),
            totp_encryption_keys={"native-ui": secrets.token_bytes(32)}, totp_active_key_version="native-ui",
            recovery_hmac_keys={"native-ui": secrets.token_bytes(32)}, recovery_hmac_active_key_version="native-ui",
        )
        app = create_runtime_app(settings)
        app.state.clock = lambda: self.now
        original_lifespan = app.router.lifespan_context

        async def synchronize_database_clock():
            while True:
                async with app.state.database_engine.connect() as connection:
                    self.now = (await connection.scalar(text("SELECT clock_timestamp()"))).astimezone(UTC)
                await asyncio.sleep(.1)

        @asynccontextmanager
        async def lifespan(application):
            async with original_lifespan(application):
                task = asyncio.create_task(synchronize_database_clock())
                try:
                    yield
                finally:
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task
        app.router.lifespan_context = lifespan
        return app

    def inspect_audit(self):
        async def inspect(connection):
            columns = (await connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='competence_hub' AND table_name='audit_events'"))).scalars().all()
            if set(columns) != {"id", "actor_user_id", "occurred_at", "action", "entity_type", "entity_id", "outcome"}:
                raise RuntimeError("Unexpected audit schema; do not read unknown fields")
            rows = (await connection.execute(text("SELECT id,actor_user_id,occurred_at,action,entity_type,entity_id,outcome FROM competence_hub.audit_events WHERE actor_user_id=ANY(:users)"), {"users": list(self.users.values())})).mappings().all()
            return [dict(row) for row in rows]
        return self.database(inspect)

    def remove_role(self, key):
        async def remove(connection):
            await connection.execute(text("DELETE FROM competence_hub.user_roles WHERE user_id=:id"), {"id": self.users[key]})
        self.database(remove)

    def expire(self, key, *, challenges=False):
        table = "auth_login_challenges" if challenges else "auth_sessions"
        field = "expires_at" if challenges else "idle_expires_at"
        async def expire_rows(connection):
            await connection.execute(text(f"UPDATE competence_hub.{table} SET {field}=created_at + interval '1 millisecond' WHERE portal_user_id=:id"), {"id": self.users[key]})
        self.database(expire_rows)

    def cleanup(self):
        if not self.provisioned:
            return
        users = list(self.users.values())
        coaches = list(self.coaches.values())
        buckets = [keyed_digest(f"login:account:{email}", self.rate_key) for email in self.emails.values()]
        buckets += [keyed_digest(f"mfa:user:{user}", self.rate_key) for user in users]
        buckets += [keyed_digest(f"{action}:ip:127.0.0.1", self.rate_key) for action in ("login", "mfa")]
        async def clean(connection):
            await connection.execute(text("DELETE FROM competence_hub.audit_events WHERE actor_user_id=ANY(:users) OR entity_id=ANY(:users)"), {"users": users})
            await connection.execute(text("DELETE FROM competence_hub.calendar_review_decisions WHERE reviewer_user_id=ANY(:users) OR revision_id IN (SELECT r.id FROM competence_hub.calendar_offer_revisions r JOIN competence_hub.calendar_offers o ON o.id=r.offer_id WHERE o.coach_id=ANY(:coaches))"), {"users": users, "coaches": coaches})
            await connection.execute(text("DELETE FROM competence_hub.calendar_offer_revisions WHERE offer_id IN (SELECT id FROM competence_hub.calendar_offers WHERE coach_id=ANY(:coaches))"), {"coaches": coaches})
            await connection.execute(text("DELETE FROM competence_hub.calendar_offers WHERE coach_id=ANY(:coaches)"), {"coaches": coaches})
            await connection.execute(text("DELETE FROM competence_hub.coach_topics WHERE coach_id=ANY(:coaches)"), {"coaches": coaches})
            await connection.execute(text("DELETE FROM competence_hub.coaches WHERE id=ANY(:coaches)"), {"coaches": coaches})
            await connection.execute(text("DELETE FROM competence_hub.topics WHERE id=:topic"), {"topic": self.topic})
            await connection.execute(text("DELETE FROM competence_hub.auth_rate_limit_buckets WHERE bucket_key_hash=ANY(:buckets)"), {"buckets": buckets})
            await connection.execute(text("DELETE FROM competence_hub.portal_users WHERE id=ANY(:users)"), {"users": users})
        self.database(clean)
        async def verify(connection):
            self.after = await self.counts(connection)
            return self.after
        self.database(verify)
        self.cleanup_pass = self.after == self.baseline and not any(self.after.values())
        if not self.cleanup_pass:
            raise RuntimeError("Staging cleanup verification failed; retain tunnel and investigate")
