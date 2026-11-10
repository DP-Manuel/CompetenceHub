from contextlib import asynccontextmanager
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import text

from competence_hub_api.auth.user_management import UserManagement, AccountManagementError, validate_management
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from test_admin_invitation_api import FakeSessionRepository, _client, _headers, SESSION_TOKEN, NOW, USER_ID


@pytest.fixture
def anyio_backend():return 'asyncio'


TARGET=uuid4()


@pytest.mark.parametrize('action,role,coach',[
    ('suspend',None,None),('deactivate',None,None),('enable',None,None),('revoke_invitation',None,None),
    ('set_role','internal',None),('set_role','admin',None),('set_role','calendar_reviewer',None),('set_role','coach',uuid4())])
def test_exact_management_policy_accepts_fresh_admin(action,role,coach):
    validate_management(FakeSessionRepository().principal,target=TARGET,action=action,role=role,coach_id=coach,now=NOW,expected_version=NOW)


@pytest.mark.parametrize('roles,age,target,action,role,coach',[
    (('coach',),0,TARGET,'suspend',None,None),(('calendar_reviewer',),0,TARGET,'suspend',None,None),
    (('internal',),0,TARGET,'set_role','admin',None),(('admin',),601,TARGET,'suspend',None,None),
    (('admin',),-1,TARGET,'suspend',None,None),(('admin',),0,USER_ID,'deactivate',None,None),
    (('admin',),0,TARGET,'set_role','coach',None),(('admin',),0,TARGET,'set_role','admin',uuid4()),
    (('admin',),0,TARGET,'set_role','company_contact',None),(('admin',),0,TARGET,'enable','admin',None),
    (('admin',),0,TARGET,'delete',None,None)])
def test_management_policy_rejects_escalation_stale_auth_and_self_lockout(roles,age,target,action,role,coach):
    principal=replace(FakeSessionRepository().principal,roles=roles,authenticated_at=NOW-timedelta(seconds=age))
    with pytest.raises(AccountManagementError):
        validate_management(principal,target=target,action=action,role=role,coach_id=coach,now=NOW,expected_version=NOW)


class Result:
    def __init__(self,row=None,rows=()):self.row=row;self.rows=rows
    def mappings(self):return self
    def one_or_none(self):return self.row
    def all(self):return self.rows


class Engine:
    def __init__(self,user=None,coaches=(),admins=2):
        self.user=user if user is not None else {'id':TARGET,'active':True,'updated_at':NOW,'has_password':True,'roles':['coach']}
        self.coaches=coaches;self.admins=admins;self.calls=[];self.outcome=None
    @asynccontextmanager
    async def begin(self):
        try:yield self
        except BaseException:self.outcome='rollback';raise
        else:self.outcome='commit'
    async def scalar(self,statement,values=None):
        sql=str(statement);self.calls.append((sql,values))
        if 'count(*)' in sql:return self.admins
        if 'SELECT id FROM competence_hub.roles' in sql:return uuid4()
        return True
    async def execute(self,statement,values=None):
        sql=str(statement);self.calls.append((sql,values))
        if 'SELECT u.id,u.active' in sql:return Result(row=self.user)
        if 'FROM competence_hub.coaches c' in sql:return Result(rows=self.coaches)
        return Result()


@pytest.mark.anyio
@pytest.mark.parametrize('action',['suspend','deactivate','enable','set_role'])
async def test_access_mutations_revoke_sessions_challenges_tokens_and_audit_atomically(action):
    engine=Engine()
    await UserManagement(engine).change(FakeSessionRepository().principal,target=TARGET,action=action,
        expected_version=NOW,now=NOW,role='calendar_reviewer' if action=='set_role' else None)
    assert engine.outcome=='commit'
    sql='\n'.join(call[0] for call in engine.calls)
    assert 'FOR UPDATE OF u' in sql and 'pg_advisory_xact_lock' in sql
    assert 'UPDATE competence_hub.auth_sessions SET revoked_at' in sql
    assert 'UPDATE competence_hub.auth_login_challenges SET revoked_at' in sql
    assert 'encrypted_payload = NULL' in sql and 'claim_id = NULL' in sql
    audit=[values for query,values in engine.calls if 'INSERT INTO competence_hub.audit_events' in query]
    assert audit[0]['actor']==USER_ID and audit[0]['target']==TARGET and audit[0]['action']=='auth.account.'+action


@pytest.mark.anyio
@pytest.mark.parametrize('variant,code',[
    ('stale','account_version_conflict'),('pending','activation_required'),
    ('contact','account_scope_conflict'),('last_admin','last_admin_protection'),('foreign_coach','coach_mapping_conflict')])
async def test_invalid_target_never_mutates_roles_or_active_flags(variant,code):
    engine=Engine();action='enable';role=None;coach=None
    if variant=='stale':engine.user['updated_at']=NOW-timedelta(seconds=1)
    if variant=='pending':engine.user.update(active=False,has_password=False)
    if variant=='contact':engine.user['roles']=['company_contact']
    if variant=='last_admin':engine.user['roles']=['admin'];engine.admins=1;action='suspend'
    if variant=='foreign_coach':action='set_role';role='coach';coach=uuid4();engine.coaches=[{'id':coach,'portal_user_id':uuid4(),'lifecycle':'active'}]
    with pytest.raises(AccountManagementError,match=code):
        await UserManagement(engine).change(FakeSessionRepository().principal,target=TARGET,action=action,
            expected_version=NOW,now=NOW,role=role,coach_id=coach)
    assert engine.outcome=='rollback'
    assert not any(query.startswith(('UPDATE','DELETE','INSERT')) for query,_ in engine.calls)


@pytest.mark.anyio
@pytest.mark.parametrize('role',['internal','coach','calendar_reviewer'])
async def test_management_and_mapping_admin_only(role):
    async with _client(FakeSessionRepository((role,))) as client:
        client.cookies.set(SESSION_COOKIE_NAME,SESSION_TOKEN)
        assert (await client.patch('/api/v1/admin/users/'+str(TARGET),json={'action':'suspend','expected_version':NOW.isoformat()},headers=_headers())).status_code==403
        assert (await client.get('/api/v1/admin/coach-mappings')).status_code==403
        assert (await client.get('/api/v1/admin/users/'+str(TARGET)+'/audit')).status_code==403


@pytest.mark.anyio
@pytest.mark.parametrize('headers',[{'Origin':'https://foreign.invalid'},{'X-CSRF-Token':'bad'}])
async def test_admin_mutation_rejects_wrong_origin_or_csrf(headers):
    async with _client(FakeSessionRepository()) as client:
        client.cookies.set(SESSION_COOKIE_NAME,SESSION_TOKEN)
        response=await client.patch('/api/v1/admin/users/'+str(TARGET),json={'action':'suspend','expected_version':NOW.isoformat()},headers=_headers(**headers))
        assert response.status_code==403


def test_existing_schema_only_no_password_or_recovery_changes():
    from pathlib import Path
    from competence_hub_api.auth import user_management
    source=Path(user_management.__file__).read_text(encoding='utf8')
    assert 'CREATE TABLE' not in source and 'password_hash' not in source
    assert 'auth_recovery_codes' not in source and 'auth_totp_credentials' not in source


@pytest.mark.anyio
async def test_invitation_rechecks_actor_after_concurrent_role_removal():
    from test_postgres_account_lifecycle import FakeEngine
    from competence_hub_api.auth.postgres_account_lifecycle import PostgresAccountLifecycleRepository
    from competence_hub_api.auth.account_lifecycle import InvitationConflictError
    engine=FakeEngine();engine.connection.management_actor_authorized=False
    with pytest.raises(InvitationConflictError):
        await PostgresAccountLifecycleRepository(engine).issue_invitation(
            actor_user_id=USER_ID,normalized_email='synthetic.concurrent@example.invalid',
            display_name='Synthetic',role_codes=('internal',),token_hash=b't'*32,
            outbox_id=uuid4(),encrypted_payload=b'synthetic-only',payload_key_version='synthetic',
            idempotency_key_hash=b'i'*32,request_fingerprint=b'f'*32,now=NOW,
            expires_at=NOW+timedelta(hours=24),idempotency_expires_at=NOW+timedelta(hours=24))
    assert len(engine.connection.executed)==1


def test_recent_dashboard_projection_is_bounded_approved_and_scoped():
    from competence_hub_api.web.pilot import _RECENT_PUBLICATIONS
    query=str(_RECENT_PUBLICATIONS)
    assert 'LIMIT 5' in query and "r.workflow_status='published'" in query
    assert "o.lifecycle_status='active'" in query and 'c.portal_user_id=:actor' in query
    assert 'review_feedback' not in query and 'email' not in query


@pytest.mark.anyio
@pytest.mark.parametrize('payload',[
    {'action':'delete','expected_version':NOW.isoformat()},
    {'action':'enable','expected_version':'2026-11-10T12:00:00'},
    {'action':'set_role','role':'company_contact','expected_version':NOW.isoformat()},
    {'action':'enable','expected_version':NOW.isoformat(),'password':'not-supported'},
    {'action':'enable','expected_version':NOW.isoformat(),'padding':'x'*33000},
])
async def test_management_api_rejects_invalid_and_oversized_input_before_writes(payload):
    engine=Engine()
    async with _client(FakeSessionRepository()) as client:
        client._transport.app.state.database_engine=engine
        client.cookies.set(SESSION_COOKIE_NAME,SESSION_TOKEN)
        response=await client.patch('/api/v1/admin/users/'+str(TARGET),json=payload,headers=_headers())
    assert response.status_code==400 and not engine.calls


@pytest.mark.anyio
async def test_management_api_success_is_minimal_and_protected():
    engine=Engine()
    async with _client(FakeSessionRepository()) as client:
        client._transport.app.state.database_engine=engine
        client.cookies.set(SESSION_COOKIE_NAME,SESSION_TOKEN)
        response=await client.patch('/api/v1/admin/users/'+str(TARGET),
            json={'action':'suspend','expected_version':NOW.isoformat()},headers=_headers())
    assert response.status_code==200 and response.json()=={'status':'accepted'}
    assert response.headers['cache-control']=='no-store' and engine.outcome=='commit'
