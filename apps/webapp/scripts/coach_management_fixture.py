"""Disposable localhost55434 only; no source content or real Coach identity."""

import os
import secrets
from datetime import UTC
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from native_calendar_fixture import NativeCalendarFixture, TABLES
from competence_hub_api.portal.coach_registry import (
    CoachRegistryService,
    ProfileContent,
    Offering,
)
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)
from competence_hub_api.portal.coach_management import CoachManagementQueries
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService


class LocalCoachManagementFixture:
    database = NativeCalendarFixture.database

    def __init__(self):
        self.app_url = os.environ.get(
            "COMPETENCE_HUB_COACH_REGISTRY_LOCAL_DATABASE_URL", ""
        )
        self.owner_url = os.environ.get(
            "COMPETENCE_HUB_COACH_REGISTRY_LOCAL_OWNER_URL", ""
        )
        for raw, role in (
            (self.app_url, "competence_hub_app"),
            (self.owner_url, "competence_hub_migrator"),
        ):
            u = make_url(raw)
            if (
                u.drivername != "postgresql+asyncpg"
                or (u.host, u.port, u.database, u.username)
                != ("127.0.0.1", 55434, "competence_hub_staging", role)
                or not u.password
                or u.query
            ):
                raise ValueError(
                    "Only the owned disposable local Coach database is allowed"
                )
        self.roles = {
            "admin": "admin",
            "internal": "internal",
            "coach": "coach",
            "reviewer": "calendar_reviewer",
            "contact": "company_contact",
        }
        self.users = {key: uuid4() for key in self.roles}
        self.emails = {
            key: f"synthetic-coach2-{value.hex}@example.invalid"
            for key, value in self.users.items()
        }
        self.password = secrets.token_urlsafe(32)
        self.rate_key = secrets.token_bytes(32)
        self.topics = [uuid4(), uuid4()]
        self.actor = SimpleNamespace(user_id=self.users["admin"], roles=("admin",))
        self.ids = {}
        self.now = None

    def prepare(self):
        password_hash = PasswordService(PasswordPolicy(frozenset())).hash(self.password)

        async def seed(c):
            versions = (
                (
                    await c.execute(
                        text(
                            "SELECT version FROM competence_hub.schema_migrations ORDER BY version"
                        )
                    )
                )
                .scalars()
                .all()
            )
            if versions != [f"000{i}" for i in range(1, 8)]:
                raise RuntimeError("Expected only the seven local migrations")
            for table in TABLES:
                if await c.scalar(text(f"SELECT count(*) FROM competence_hub.{table}")):
                    raise RuntimeError("Disposable database was not empty")
            self.now = (await c.scalar(text("SELECT clock_timestamp()"))).astimezone(
                UTC
            )
            for key, user in self.users.items():
                await c.execute(
                    text(
                        "INSERT INTO competence_hub.portal_users(id,display_name,email) VALUES (:id,:name,:email)"
                    ),
                    {
                        "id": user,
                        "name": "Synthetic " + self.roles[key],
                        "email": self.emails[key],
                    },
                )
                await c.execute(
                    text(
                        "INSERT INTO competence_hub.user_roles SELECT :id,id FROM competence_hub.roles WHERE code=:role AND active"
                    ),
                    {"id": user, "role": self.roles[key]},
                )
                await c.execute(
                    text(
                        "INSERT INTO competence_hub.auth_password_credentials(portal_user_id,password_hash) VALUES (:id,:hash)"
                    ),
                    {"id": user, "hash": password_hash},
                )
            for i, topic in enumerate(self.topics):
                await c.execute(
                    text(
                        "INSERT INTO competence_hub.topics(id,name) VALUES (:id,:name)"
                    ),
                    {
                        "id": topic,
                        "name": [
                            "Synthetic Kommunikation",
                            "Synthetic Stressmanagement",
                        ][i],
                    },
                )
                await c.execute(
                    text(
                        "INSERT INTO competence_hub.topic_category_assignments VALUES (:id,'personalentwicklung'),(:id,'persoenlichkeitsentwicklung')"
                    ),
                    {"id": topic},
                )

        self.database(seed)

    def seed_states(self):
        async def seed(_c):
            engine = create_async_engine(self.app_url, hide_parameters=True)
            service = CoachRegistryService(PostgresCoachRegistryRepository(engine))
            try:
                for name in ("Alpha", "Beta", "Gamma"):
                    coach = await service.create(
                        actor=self.actor,
                        display_name="Coach " + name,
                        request_id=uuid4(),
                        now=self.now,
                    )
                    self.ids[name] = coach.id

                    async def mutate(operation, **values):
                        nonlocal coach
                        coach = await service.mutate(
                            actor=self.actor,
                            coach_id=coach.id,
                            expected_version=coach.version,
                            operation=operation,
                            now=self.now,
                            **values,
                        )

                    content = ProfileContent(
                        display_name="Coach " + name,
                        short_intro="Synthetic public introduction",
                        profile_path="/coaches/coach-" + name.lower() + "/",
                        topic_ids=tuple(self.topics),
                        competencies=("Synthetic Kommunikation",),
                        offerings=(
                            Offering(
                                title="Synthetic Workshop", type="workshop", ordering=0
                            ),
                            Offering(
                                title="Synthetic Vortrag", type="lecture", ordering=1
                            ),
                        ),
                    )
                    await mutate("revision", content=content)
                    revision = coach.revisions[-1].id
                    await mutate("submit", revision_id=revision)
                    for kind in ("content_review", "person_consent", "preview"):
                        await mutate(
                            "approve",
                            revision_id=revision,
                            kind=kind,
                            evidence_ref="synthetic-coach2-fixture",
                        )
                    await mutate("lifecycle", lifecycle="active")
                    if name == "Alpha":
                        await mutate(
                            "publish", revision_id=revision, environment="preview"
                        )
                    elif name == "Beta":
                        await mutate("lifecycle", lifecycle="paused")
                    else:
                        await mutate("lifecycle", lifecycle="inactive")
                        for i in range(12):
                            await mutate("revision", content=content)
                            await mutate("submit", revision_id=coach.revisions[-1].id)
                            if i == 0:
                                for kind in ("content_review", "person_consent"):
                                    await mutate(
                                        "approve",
                                        revision_id=coach.revisions[-1].id,
                                        kind=kind,
                                        evidence_ref="synthetic-older-activation",
                                    )
            finally:
                await engine.dispose()

        self.database(seed)

    def app(self, port):
        app = NativeCalendarFixture.app(self, port)
        repository = PostgresCoachRegistryRepository(app.state.database_engine)
        app.state.coach_registry_service = CoachRegistryService(repository)
        app.state.coach_management_queries = CoachManagementQueries(repository)
        return app

    def inspect(self, action):
        return self.database(action)
