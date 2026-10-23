"""Opt-in disposable local DB only: never accepts the native VPS tunnel/URL."""

import asyncio
from dataclasses import replace
from datetime import UTC, datetime
import os
import secrets
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import pytest
import pyotp
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.portal.coach_registry import (
    Asset,
    CoachRegistryService,
    RegistryConflict,
    public_projection,
)
from competence_hub_api.portal.postgres_coach_registry import (
    PostgresCoachRegistryRepository,
)
from competence_hub_api.runtime import create_runtime_app
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from test_runtime import runtime_settings
from test_coach_registry import ACTOR, TOPIC_ID, change, profile


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_registry_real_postgres_transactions_freezes_and_lifecycle():
    urls = [
        os.environ.get(name, "")
        for name in (
            "COMPETENCE_HUB_COACH_REGISTRY_LOCAL_DATABASE_URL",
            "COMPETENCE_HUB_COACH_REGISTRY_LOCAL_OWNER_URL",
        )
    ]
    if not all(urls):
        pytest.skip("requires the owned disposable Registry container")
    for raw in urls:
        url = make_url(raw)
        assert (
            url.host == "127.0.0.1"
            and url.port == 55434
            and url.database == "competence_hub_staging"
        )
    engine, owner = [create_async_engine(url, hide_parameters=True) for url in urls]
    try:
        async with owner.begin() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await c.execute(
                text(
                    "INSERT INTO competence_hub.portal_users(id,display_name,email) VALUES (:id,'Synthetic Registry Admin','synthetic-registry@example.invalid')"
                ),
                {"id": ACTOR.user_id},
            )
            await c.execute(
                text(
                    "INSERT INTO competence_hub.topics(id,name) VALUES (:id,'Synthetic Registry Topic')"
                ),
                {"id": TOPIC_ID},
            )
            await c.execute(
                text(
                    "INSERT INTO competence_hub.topic_category_assignments VALUES (:id,'personalentwicklung'),(:id,'persoenlichkeitsentwicklung')"
                ),
                {"id": TOPIC_ID},
            )
        repo = PostgresCoachRegistryRepository(engine)
        service = CoachRegistryService(repo)
        now = datetime.now(UTC)
        request_id = uuid4()
        create = dict(
            actor=ACTOR,
            display_name="Synthetic Registry",
            request_id=request_id,
            now=now,
        )
        a, b = await asyncio.gather(service.create(**create), service.create(**create))
        assert a.id == b.id
        coach = a
        # Multiple offerings are catalogue entries, not Calendar offers.
        asset = Asset(
            reference="images/coaches/synthetic.webp",
            sha256="a" * 64,
            alt_text="Synthetic portrait",
        )
        content = profile(assets=(asset,))
        results = await asyncio.gather(
            change(service, coach, "revision", content=content),
            change(service, coach, "revision", content=content),
            return_exceptions=True,
        )
        assert sum(isinstance(r, RegistryConflict) for r in results) == 1
        coach = next(r for r in results if not isinstance(r, Exception))
        coach = await change(
            service,
            coach,
            "draft",
            revision_id=coach.revisions[0].id,
            content=content.model_copy(update={"short_intro": "Edited introduction"}),
        )
        coach = await change(
            service, coach, "submit", revision_id=coach.revisions[0].id
        )
        for kind in ("content_review", "person_consent", "preview"):
            coach = await change(
                service,
                coach,
                "approve",
                revision_id=coach.revisions[0].id,
                kind=kind,
                evidence_ref="synthetic-evidence",
            )
        coach = await change(service, coach, "lifecycle", lifecycle="active")
        coach = await change(
            service,
            coach,
            "publish",
            revision_id=coach.revisions[0].id,
            environment="preview",
        )
        loaded = await repo.get(coach.id)
        assert (
            public_projection((loaded,), "preview")["coaches"][0]["short_intro"]
            == "Edited introduction"
        )
        assert len(loaded.revisions[0].content.offerings) == 3
        assert len(loaded.revisions[0].topics[0].categories) == 2
        assert loaded.revisions[0].content.assets[0].scopes == ("preview",)
        assert public_projection((loaded,), "production")["coaches"] == []
        async with engine.connect() as c:
            assert (
                await c.execute(
                    text(
                        "SELECT portal_user_id,public_profile_path FROM competence_hub.coaches WHERE id=:id"
                    ),
                    {"id": coach.id},
                )
            ).one() == (None, None)
        # DB enforcement, not merely service-level checks.
        statements = [
            ("DELETE FROM competence_hub.coaches WHERE id=:id", {"id": coach.id}),
            (
                "UPDATE competence_hub.coaches SET id=:new WHERE id=:id",
                {"id": coach.id, "new": uuid4()},
            ),
            (
                "UPDATE competence_hub.coach_profile_revisions SET short_intro='tampered' WHERE id=:id",
                {"id": loaded.revisions[0].id},
            ),
            (
                "UPDATE competence_hub.coach_offerings SET title='tampered' WHERE revision_id=:id",
                {"id": loaded.revisions[0].id},
            ),
            (
                "DELETE FROM competence_hub.coach_profile_approvals WHERE revision_id=:id",
                {"id": loaded.revisions[0].id},
            ),
            (
                "INSERT INTO competence_hub.coach_publications VALUES (:coach,'production',:revision,'published','/coaches/synthetic-coach/',:actor,now())",
                {
                    "coach": coach.id,
                    "revision": loaded.revisions[0].id,
                    "actor": ACTOR.user_id,
                },
            ),
        ]
        for statement, values in statements:
            with pytest.raises(DBAPIError):
                async with engine.begin() as c:
                    await c.execute(text(statement), values)
        coach = await change(
            service,
            coach,
            "approve",
            revision_id=coach.revisions[0].id,
            kind="production",
            evidence_ref="synthetic-prod",
        )
        with pytest.raises(DBAPIError):
            async with engine.begin() as c:
                await c.execute(
                    text(
                        "INSERT INTO competence_hub.coach_publications VALUES (:coach,'production',:revision,'published','/coaches/synthetic-coach/',:actor,now())"
                    ),
                    {
                        "coach": coach.id,
                        "revision": loaded.revisions[0].id,
                        "actor": ACTOR.user_id,
                    },
                )
        with pytest.raises(RegistryConflict):
            await service.mutate(
                actor=ACTOR,
                coach_id=coach.id,
                expected_version=1,
                operation="lifecycle",
                lifecycle="paused",
                now=now,
            )
        async with engine.begin() as c:
            await c.execute(
                text(
                    "UPDATE competence_hub.topics SET name='Renamed Registry Topic' WHERE id=:id"
                ),
                {"id": TOPIC_ID},
            )
            offer_id = await c.scalar(
                text(
                    "INSERT INTO competence_hub.calendar_offers(coach_id,created_by_user_id,client_request_id) VALUES (:id,:actor,:request) RETURNING id"
                ),
                {"id": coach.id, "actor": ACTOR.user_id, "request": uuid4()},
            )
            await c.execute(
                text(
                    """INSERT INTO competence_hub.calendar_offer_revisions(offer_id,revision_number,topic_id,title,starts_at,ends_at,format_code,capacity,review_threshold,decision_deadline,price_display_text,created_by_user_id)
                VALUES (:offer,1,:topic,'Synthetic future offer',now()+interval '7 days',now()+interval '7 days 1 hour','online',10,1,now()+interval '6 days','Synthetic',:actor)"""
                ),
                {"offer": offer_id, "topic": TOPIC_ID, "actor": ACTOR.user_id},
            )
        with pytest.raises(RegistryConflict):
            await change(service, coach, "lifecycle", lifecycle="paused")
        assert (await repo.get(coach.id)).lifecycle == "active"
        async with engine.begin() as c:
            await c.execute(
                text(
                    "UPDATE competence_hub.calendar_offers SET lifecycle_status='withdrawn',withdrawn_at=now() WHERE id=:id"
                ),
                {"id": offer_id},
            )
        coach = await change(service, coach, "revision", content=content)
        coach = await change(service, coach, "lifecycle", lifecycle="paused")
        assert coach.revisions[-1].status == "abandoned"
        with pytest.raises(DBAPIError):
            async with engine.begin() as c:
                await c.execute(
                    text(
                        "INSERT INTO competence_hub.calendar_offers(coach_id,created_by_user_id,client_request_id) VALUES (:id,:actor,:request)"
                    ),
                    {"id": coach.id, "actor": ACTOR.user_id, "request": uuid4()},
                )
        assert (
            public_projection((await repo.get(coach.id),), "preview")["coaches"] == []
        )
        with pytest.raises(RegistryConflict):
            await change(service, coach, "lifecycle", lifecycle="active")
        returning_content = content.model_copy(
            update={
                "display_name": "Returning Synthetic",
                "profile_path": "/coaches/returning-synthetic/",
                "assets": (
                    asset.model_copy(update={"scopes": ("preview", "production")}),
                ),
            }
        )
        coach = await change(service, coach, "revision", content=returning_content)
        assert coach.revisions[-1].topics[0].name == "Renamed Registry Topic"
        assert coach.revisions[0].topics[0].name == "Synthetic Registry Topic"
        coach = await change(
            service, coach, "submit", revision_id=coach.revisions[-1].id
        )
        for kind in ("content_review", "person_consent", "preview", "production"):
            coach = await change(
                service,
                coach,
                "approve",
                revision_id=coach.revisions[-1].id,
                kind=kind,
                evidence_ref="new-evidence",
            )
        coach = await change(service, coach, "lifecycle", lifecycle="active")
        coach = await change(
            service,
            coach,
            "publish",
            revision_id=coach.revisions[-1].id,
            environment="production",
        )
        assert coach.id == a.id
        retained = await repo.get(coach.id)
        assert [r.number for r in retained.revisions] == [1, 2, 3]
        assert [r.status for r in retained.revisions] == ["submitted", "abandoned", "submitted"]
        assert (
            public_projection((await repo.get(coach.id),), "production")["coaches"][0][
                "display_name"
            ]
            == "Returning Synthetic"
        )
        coach = await change(service, coach, "withdraw", environment="production")
        with pytest.raises(DBAPIError):
            async with engine.begin() as c:
                await c.execute(
                    text(
                        "UPDATE competence_hub.coach_publications SET state='published' WHERE coach_id=:id AND environment='production'"
                    ),
                    {"id": coach.id},
                )
        async with engine.connect() as c:
            assert (
                await c.scalar(
                    text(
                        "SELECT count(*) FROM competence_hub.audit_events WHERE action LIKE 'coach_registry.%'"
                    )
                )
                > 10
            )
            assert (
                await c.scalar(
                    text(
                        "SELECT count(*) FROM information_schema.columns WHERE table_schema='competence_hub' AND table_name='audit_events' AND column_name IN ('payload','profile','description')"
                    )
                )
                == 0
            )
            assert (
                await c.scalar(
                    text("SELECT count(*) FROM competence_hub.topic_categories")
                )
                == 3
            )
        await verify_native_admin_api(engine, owner, service, urls[0])
    finally:
        await engine.dispose()
        await owner.dispose()


async def verify_native_admin_api(engine, owner, service, app_url):
    password = secrets.token_urlsafe(32)
    password_hash = PasswordService(PasswordPolicy(frozenset())).hash(password)
    async with owner.begin() as c:
        await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
        await c.execute(
            text(
                "INSERT INTO competence_hub.user_roles(user_id,role_id) SELECT :id,id FROM competence_hub.roles WHERE code='admin'"
            ),
            {"id": ACTOR.user_id},
        )
        await c.execute(
            text(
                "INSERT INTO competence_hub.auth_password_credentials(portal_user_id,password_hash) VALUES (:id,:hash)"
            ),
            {"id": ACTOR.user_id, "hash": password_hash},
        )
    origin = "https://127.0.0.1"
    settings = replace(runtime_settings(), database_url=app_url, allowed_origin=origin)
    app = create_runtime_app(settings, engine_factory=lambda _: engine)
    # Deliberate local-only injection; the normal runtime remains unconfigured.
    app.state.coach_registry_service = service
    async with AsyncClient(transport=ASGITransport(app=app), base_url=origin) as client:
        assert (await client.get("/api/v1/admin/coaches")).status_code == 401
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "synthetic-registry@example.invalid", "password": password},
            headers={"Origin": origin},
        )
        assert response.status_code == 202
        headers = {"Origin": origin, "X-CSRF-Token": response.json()["csrf_token"]}
        response = await client.post(
            "/api/v1/auth/mfa/totp/enrollment", json={}, headers=headers
        )
        assert response.status_code == 201
        secret = parse_qs(urlsplit(response.json()["provisioning_uri"]).query)[
            "secret"
        ][0]
        response = await client.post(
            "/api/v1/auth/mfa/totp/enrollment/confirm",
            json={"code": pyotp.TOTP(secret).now()},
            headers=headers,
        )
        assert response.status_code == 200
        headers["X-CSRF-Token"] = response.headers["X-CSRF-Token"]
        response = await client.get("/api/v1/admin/coaches")
        assert (
            response.status_code == 200
            and response.headers["Cache-Control"] == "no-store"
        )
        payload = {
            "display_name": "Synthetic native intake",
            "client_request_id": str(uuid4()),
        }
        assert (
            await client.post(
                "/api/v1/admin/coaches",
                json=payload,
                headers={**headers, "Origin": "https://foreign.example.invalid"},
            )
        ).status_code == 403
        assert (
            await client.post(
                "/api/v1/admin/coaches",
                json=payload,
                headers={**headers, "X-CSRF-Token": "wrong"},
            )
        ).status_code == 403
        response = await client.post(
            "/api/v1/admin/coaches", json=payload, headers=headers
        )
        assert response.status_code == 201 and response.json()["lifecycle"] == "draft"
        async with owner.begin() as c:
            await c.execute(text("SET LOCAL ROLE competence_hub_owner"))
            await c.execute(
                text("DELETE FROM competence_hub.user_roles WHERE user_id=:id"),
                {"id": ACTOR.user_id},
            )
        assert (await client.get("/api/v1/admin/coaches")).status_code == 401
