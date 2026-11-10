"""Bounded Admin lifecycle operations on the existing authentication schema."""
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.postgres_account_lifecycle import _REVOKE_OPEN_TOKENS
from competence_hub_api.auth.session_repository import SessionPrincipal

ROLES = frozenset({'admin', 'internal', 'coach', 'calendar_reviewer'})
ACTIONS = frozenset({'suspend', 'deactivate', 'enable', 'set_role', 'revoke_invitation'})


class AccountManagementError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def validate_management(actor: SessionPrincipal, *, target: UUID, action: str,
                        role: str | None, coach_id: UUID | None, now: datetime,
                        expected_version: datetime) -> None:
    if ('admin' not in actor.roles or now.tzinfo is None or expected_version.tzinfo is None
            or not timedelta(0) <= now - actor.authenticated_at <= timedelta(minutes=10)):
        raise AccountManagementError('reauthentication_required')
    if action not in ACTIONS:
        raise AccountManagementError('invalid_request')
    if target == actor.user_id:
        raise AccountManagementError('account_self_protection')
    if action == 'set_role':
        if role not in ROLES or (role == 'coach') != (coach_id is not None):
            raise AccountManagementError('invalid_request')
    elif role is not None or coach_id is not None:
        raise AccountManagementError('invalid_request')


class UserManagement:
    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def change(self, actor: SessionPrincipal, *, target: UUID, action: str,
                     expected_version: datetime, now: datetime,
                     role: str | None = None, coach_id: UUID | None = None) -> None:
        validate_management(actor, target=target, action=action, role=role,
                            coach_id=coach_id, now=now, expected_version=expected_version)
        async with self.engine.begin() as connection:
            # Serialize privilege changes and last-admin checks, including other targets.
            await connection.execute(text("SELECT pg_advisory_xact_lock(hashtext('competence_hub.admin_management'))"))
            valid_actor = await connection.scalar(text("""SELECT EXISTS(SELECT 1
                FROM competence_hub.portal_users u JOIN competence_hub.user_roles ur ON ur.user_id=u.id
                JOIN competence_hub.roles r ON r.id=ur.role_id
                WHERE u.id=:actor AND u.active AND r.active AND r.code='admin')"""), {'actor': actor.user_id})
            if not valid_actor:
                raise AccountManagementError('authorization_failed')
            user = (await connection.execute(text("""SELECT u.id,u.active,u.updated_at,
                EXISTS(SELECT 1 FROM competence_hub.auth_password_credentials p WHERE p.portal_user_id=u.id) AS has_password,
                ARRAY(SELECT r.code FROM competence_hub.user_roles ur JOIN competence_hub.roles r
                      ON r.id=ur.role_id WHERE ur.user_id=u.id ORDER BY r.code) AS roles
                FROM competence_hub.portal_users u WHERE u.id=:target FOR UPDATE OF u"""), {'target': target})).mappings().one_or_none()
            if user is None:
                raise AccountManagementError('account_not_found')
            if user['updated_at'] != expected_version:
                raise AccountManagementError('account_version_conflict')
            if not set(user['roles']) <= ROLES:
                raise AccountManagementError('account_scope_conflict')
            if user['active'] and 'admin' in user['roles'] and (action in ('suspend','deactivate') or action == 'set_role' and role != 'admin'):
                admins = await connection.scalar(text("""SELECT count(*) FROM competence_hub.portal_users u
                    JOIN competence_hub.user_roles ur ON ur.user_id=u.id JOIN competence_hub.roles r ON r.id=ur.role_id
                    WHERE u.active AND r.active AND r.code='admin'"""))
                if admins <= 1:
                    raise AccountManagementError('last_admin_protection')
            if action == 'enable' and not user['has_password']:
                raise AccountManagementError('activation_required')
            if action == 'revoke_invitation' and (user['active'] or user['has_password']):
                raise AccountManagementError('account_scope_conflict')
            values = {'target': target, 'now': now, 'actor': actor.user_id}
            if action == 'set_role':
                role_id = await connection.scalar(text('SELECT id FROM competence_hub.roles WHERE code=:role AND active'), {'role': role})
                if role_id is None:
                    raise AccountManagementError('account_scope_conflict')
                if coach_id is not None:
                    coaches = (await connection.execute(text("""SELECT id,portal_user_id,
                        COALESCE(to_jsonb(c)->>'lifecycle_status','active') AS lifecycle
                        FROM competence_hub.coaches c WHERE id=:coach OR portal_user_id=:target ORDER BY id FOR UPDATE"""),
                        {'coach':coach_id,'target':target})).mappings().all()
                    selected = next((row for row in coaches if row['id']==coach_id),None)
                    if (selected is None or selected['lifecycle']!='active'
                            or selected['portal_user_id'] not in (None,target)
                            or any(row['id']!=coach_id and row['portal_user_id']==target for row in coaches)):
                        raise AccountManagementError('coach_mapping_conflict')
                    await connection.execute(text('UPDATE competence_hub.coaches SET portal_user_id=:target WHERE id=:coach'),
                                             {'target':target,'coach':coach_id})
                await connection.execute(text('DELETE FROM competence_hub.user_roles WHERE user_id=:target'),values)
                await connection.execute(text("""INSERT INTO competence_hub.user_roles(user_id,role_id,assigned_at,assigned_by_user_id)
                    VALUES(:target,:role,:now,:actor)"""), {**values,'role':role_id})
            active = user['active'] if action in ('set_role','revoke_invitation') else action == 'enable'
            await connection.execute(text('UPDATE competence_hub.portal_users SET active=:active,updated_at=:now WHERE id=:target'),
                                     {**values,'active':active})
            await connection.execute(text("""UPDATE competence_hub.auth_sessions SET revoked_at=:now,revoke_reason='admin_access_change'
                WHERE portal_user_id=:target AND revoked_at IS NULL"""), values)
            await connection.execute(text('UPDATE competence_hub.auth_login_challenges SET revoked_at=:now WHERE portal_user_id=:target AND revoked_at IS NULL'), values)
            for purpose in ('invitation',) if action=='revoke_invitation' else ('invitation','password_reset'):
                await connection.execute(_REVOKE_OPEN_TOKENS,{'user_id':target,'purpose':purpose,'now':now})
            await connection.execute(text("""INSERT INTO competence_hub.audit_events
                (actor_user_id,occurred_at,action,entity_type,entity_id,outcome)
                VALUES(:actor,:now,:action,'portal_user',:target,'success')"""),
                {**values,'action':'auth.account.'+action})

    async def audit(self, target: UUID):
        async with self.engine.connect() as connection:
            await connection.execute(text('SET TRANSACTION READ ONLY'))
            rows = await connection.execute(text("""SELECT occurred_at,action,outcome,actor_user_id
                FROM competence_hub.audit_events WHERE entity_type='portal_user' AND entity_id=:target
                ORDER BY occurred_at DESC,id DESC LIMIT 20"""),{'target':target})
            return [dict(row) for row in rows.mappings()]
