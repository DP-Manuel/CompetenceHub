from importlib.resources import files
from uuid import uuid4

import pytest

from competence_hub_api.auth.account_lifecycle import LifecycleRejected, LifecycleQueued
from competence_hub_api.web.pilot import _COUNTS, _USERS
from test_account_lifecycle_service import _service, _actor, NOW, IDEMPOTENCY_KEY, FakeLifecycleRepository
from test_admin_invitation_api import _client, FakeSessionRepository, FakeLifecycleService, _headers, _payload, SESSION_TOKEN
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
@pytest.mark.parametrize("roles,coach,accepted", [
    (("calendar_reviewer",),None,True), (("coach",),uuid4(),True),
    (("coach",),None,False), (("internal",),uuid4(),False),
    (("admin",),None,False), (("coach","calendar_reviewer"),uuid4(),False),
    (("company_contact",),None,False),
])
async def test_pilot_invitation_exact_role_mapping_boundary(roles,coach,accepted):
    repo = FakeLifecycleRepository()
    outcome = await _service(repo).issue_invitation(actor=_actor(),email="pilot@example.invalid",
        display_name="Synthetic",role_codes=roles,coach_id=coach,idempotency_key=IDEMPOTENCY_KEY,
        client_ip="192.0.2.2",now=NOW)
    assert isinstance(outcome, LifecycleQueued if accepted else LifecycleRejected)
    if not accepted:
        assert not repo.invitations


@pytest.mark.anyio
async def test_invitation_mapping_bound_into_idempotency_fingerprint():
    fingerprints = []
    for coach in (uuid4(), uuid4()):
        repo = FakeLifecycleRepository()
        await _service(repo).issue_invitation(actor=_actor(),email="pilot@example.invalid",display_name="Synthetic",
            role_codes=("coach",),coach_id=coach,idempotency_key=IDEMPOTENCY_KEY,client_ip="192.0.2.2",now=NOW)
        fingerprints.append(repo.invitations[0]["request_fingerprint"])
    assert fingerprints[0] != fingerprints[1]


@pytest.mark.anyio
async def test_default_runtime_delivery_hold_prevents_queue_work():
    service = FakeLifecycleService(LifecycleQueued(uuid4()))
    async with _client(FakeSessionRepository(),service) as client:
        client._transport.app.state.invitation_delivery_enabled = False
        client.cookies.set(SESSION_COOKIE_NAME, SESSION_TOKEN)
        response = await client.post("/api/v1/admin/users/invitations",json=_payload(),headers=_headers())
    assert response.status_code == 503
    assert not service.calls


@pytest.mark.anyio
@pytest.mark.parametrize("role,status", [("coach",403),("calendar_reviewer",403),("internal",403)])
async def test_account_inventory_not_available_to_non_admin(role,status):
    from dataclasses import replace
    repository = FakeSessionRepository()
    # Same session fixture, exact role substitution, no credential material.
    original = repository.refresh_active_session
    async def session(*args,**kwargs):
        principal = await original(*args,**kwargs)
        return replace(principal,roles=(role,))
    repository.refresh_active_session = session
    async with _client(repository,FakeLifecycleService()) as client:
        client.cookies.set(SESSION_COOKIE_NAME,SESSION_TOKEN)
        response = await client.get("/api/v1/admin/users")
    assert response.status_code == status


def test_overview_queries_are_scoped_and_have_no_sensitive_columns():
    assert "c.portal_user_id=:actor" in str(_COUNTS)
    assert "r.workflow_status IN" in str(_COUNTS)
    assert "LIMIT :limit OFFSET :offset" in str(_USERS)
    assert "t.enabled_at IS NOT NULL" in str(_USERS)
    for secret in ("password_hash", "encrypted_secret", "token_hash", "code_hash"):
        assert secret not in str(_USERS)


@pytest.mark.parametrize("flag,enabled",[(None,False),("false",False),("true",True)])
def test_dispatch_release_flag_is_explicit_and_default_closed(flag,enabled):
    from test_config import valid_environment
    from competence_hub_api.config import RuntimeSettings
    environment = valid_environment()
    if flag is not None: environment["COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED"] = flag
    assert RuntimeSettings.from_environment(environment).invitation_delivery_enabled is enabled


@pytest.mark.parametrize("flag",["1","yes","TRUE"," true "])
def test_invalid_dispatch_flag_fails_closed(flag):
    from test_config import valid_environment
    from competence_hub_api.config import RuntimeSettings, RuntimeConfigurationError
    with pytest.raises(RuntimeConfigurationError):
        RuntimeSettings.from_environment({**valid_environment(),"COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED":flag})


@pytest.mark.anyio
@pytest.mark.parametrize("coach_row",[None,
    {"portal_user_id":uuid4(),"lifecycle_status":"active"},
    {"portal_user_id":None,"lifecycle_status":"paused"},
    {"portal_user_id":None,"lifecycle_status":"archived"}])
async def test_invitation_never_claims_missing_paused_or_foreign_coach(coach_row):
    from test_postgres_account_lifecycle import FakeEngine, FakeResult, USER_ID, ACTOR_ID, OUTBOX_ID
    from competence_hub_api.auth.postgres_account_lifecycle import PostgresAccountLifecycleRepository
    from competence_hub_api.auth.account_lifecycle import InvitationConflictError
    engine = FakeEngine([FakeResult(),FakeResult(),FakeResult(row=None),FakeResult(),
                         FakeResult(row=None),FakeResult(scalar=USER_ID),FakeResult(row=coach_row)])
    with pytest.raises(InvitationConflictError):
        await PostgresAccountLifecycleRepository(engine).issue_invitation(actor_user_id=ACTOR_ID,
            normalized_email="pilot@example.invalid",display_name="Synthetic",role_codes=("coach",),coach_id=uuid4(),
            token_hash=b"t"*32,outbox_id=OUTBOX_ID,encrypted_payload=b"synthetic-envelope",payload_key_version="synthetic",
            idempotency_key_hash=b"i"*32,request_fingerprint=b"f"*32,now=NOW,
            expires_at=NOW, idempotency_expires_at=NOW)
    statements=[str(sql) for sql,_ in engine.connection.executed]
    assert "FOR UPDATE" in statements[-1]
    assert not any("INSERT INTO competence_hub.auth_one_time_tokens" in sql for sql in statements)


@pytest.mark.anyio
async def test_pending_invitation_cannot_accumulate_unapproved_roles():
    from test_postgres_account_lifecycle import FakeEngine, FakeResult, USER_ID, ACTOR_ID, OUTBOX_ID
    from competence_hub_api.auth.postgres_account_lifecycle import PostgresAccountLifecycleRepository
    from competence_hub_api.auth.account_lifecycle import InvitationConflictError
    engine=FakeEngine([FakeResult(),FakeResult(),FakeResult(row=None),FakeResult(),
        FakeResult(row={"id":USER_ID,"active":False,"has_credential":False,"role_codes":["internal"]})])
    with pytest.raises(InvitationConflictError):
        await PostgresAccountLifecycleRepository(engine).issue_invitation(actor_user_id=ACTOR_ID,
            normalized_email="pilot@example.invalid",display_name="Synthetic",role_codes=("calendar_reviewer",),
            token_hash=b"t"*32,outbox_id=OUTBOX_ID,encrypted_payload=b"synthetic-envelope",payload_key_version="synthetic",
            idempotency_key_hash=b"i"*32,request_fingerprint=b"f"*32,now=NOW,
            expires_at=NOW, idempotency_expires_at=NOW)
    assert len(engine.connection.executed)==6


@pytest.mark.anyio
async def test_public_calendar_and_tours_are_packaged_without_demo_access():
    from competence_hub_api.main import create_app
    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=create_app()),base_url="https://test.invalid") as client:
        for asset in ("calendar-public.html","public-calendar.js","calendar-month.mjs","calendar-form.mjs","product-tour.js","product-tour.css"):
            response = await client.get("/portal/"+asset)
            assert response.status_code == 200
            assert response.headers["cache-control"] == "no-store"
        assert "javascript" in (await client.get("/portal/calendar-month.mjs")).headers["content-type"]
        assert "javascript" in (await client.get("/portal/calendar-form.mjs")).headers["content-type"]
    package = files("competence_hub_api").joinpath("portal_ui")
    markup = package.joinpath("calendar-public.html").read_text(encoding="utf8")
    assert "synthetic." not in markup and "123456" not in markup and "Testzugänge" not in markup
    tour = package.joinpath("product-tour.js").read_text(encoding="utf8")
    assert "localStorage" not in tour and "sessionStorage" not in tour
    assert "innerHTML" not in tour
