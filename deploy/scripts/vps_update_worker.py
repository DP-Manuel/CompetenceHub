"""Owned additive synthetic cohort. Never delete/reset existing pilot identities."""
import asyncio
import hashlib
import json
import sys
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from competence_hub_api.config import RuntimeSettings
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.secret_encryption import SecretCipher
from competence_hub_api.security.tokens import keyed_digest

URL='postgresql+asyncpg://postgres@/competence_hub_staging?host=/var/run/postgresql'
ROLES={'admin':'admin','reviewer':'calendar_reviewer','coach':'coach','coach_two':'coach'}


def shared_rate_hashes(key):
    return [keyed_digest(scope,key) for scope in ('login:ip:127.0.0.1','mfa:ip:127.0.0.1',
            'invitation_issue:ip:127.0.0.1','invitation_confirm:ip:127.0.0.1')]


def owned_rate_hashes(fixture,users,token_hashes,key):
    emails=[x['email'] for x in fixture['invites'].values()]
    scopes=['login:account:'+x['email'] for x in fixture['accounts'].values()]+['login:account:'+email for email in emails]
    scopes+=['mfa:user:'+str(user) for user in users]
    scopes+=['invitation_issue:account:'+email for email in emails]
    scopes+=['invitation_confirm:token:'+bytes(token).hex() for token in token_hashes]
    return [keyed_digest(scope,key) for scope in scopes]


def validate(fixture):
    if set(fixture['accounts'])!=set(ROLES) or set(fixture['coaches'])!={'coach','coach_two','invited'}:
        raise ValueError('OWNED_COHORT_REQUIRED')
    ids=[UUID(row['id']) for row in fixture['accounts'].values()]
    if len(set(ids))!=4:raise ValueError('DISTINCT_SYNTHETIC_USERS_REQUIRED')
    for key,row in fixture['accounts'].items():
        if row['role']!=ROLES[key] or row['email']!='synthetic-vps-'+UUID(row['id']).hex+'@example.invalid':
            raise ValueError('SYNTHETIC_IDENTITIES_ONLY')
    if set(fixture['invites'])!={'reviewer','coach'}:raise ValueError('OWNED_INVITATIONS_ONLY')
    for role,row in fixture['invites'].items():
        if row['email']!='synthetic-v1-'+UUID(row['nonce']).hex+'@example.invalid':
            raise ValueError('SYNTHETIC_INVITATIONS_ONLY')
    coaches=[UUID(x) for x in fixture['coaches'].values()]
    if len(set(coaches))!=3:raise ValueError('DISTINCT_COACHES_REQUIRED')
    return ids,coaches,UUID(fixture['topic'])


async def action(data):
    f=data['fixture'];users,coaches,topic=validate(f)
    settings=RuntimeSettings.from_environment(data['environment'])
    key=settings.rate_limit_hmac_key
    shared=shared_rate_hashes(key)
    engine=create_async_engine(URL,hide_parameters=True)
    try:
        async with engine.begin() as c:
            await c.execute(text('SET LOCAL ROLE competence_hub_owner'))
            emails=[v['email'] for v in f['invites'].values()]
            invited=(await c.execute(text('SELECT id,email FROM competence_hub.portal_users WHERE email=ANY(:emails)'),{'emails':emails})).mappings().all()
            all_users=users+[row['id'] for row in invited]
            parameters={'users':all_users,'coaches':coaches,'topic':topic}
            if data['action']=='seed':
                collision=await c.scalar(text('SELECT count(*) FROM competence_hub.portal_users WHERE id=ANY(:users) OR email=ANY(:emails)'),{'users':users,'emails':emails+[v['email'] for v in f['accounts'].values()]})
                if collision:raise ValueError('EXISTING_COHORT_REJECTED')
                if await c.scalar(text('SELECT count(*) FROM competence_hub.coaches WHERE id=ANY(:coaches)'),parameters) or await c.scalar(text('SELECT count(*) FROM competence_hub.topics WHERE id=:topic'),parameters):
                    raise ValueError('EXISTING_COACH_TOPIC_REJECTED')
                for name,item in f['accounts'].items():
                    await c.execute(text('INSERT INTO competence_hub.portal_users(id,display_name,email,active) VALUES(:id,:name,:email,true)'),{'id':UUID(item['id']),'name':'DEMO V1 '+name,'email':item['email']})
                    result=await c.execute(text('INSERT INTO competence_hub.user_roles(user_id,role_id) SELECT :id,id FROM competence_hub.roles WHERE code=:role AND active'),{'id':UUID(item['id']),'role':item['role']})
                    if result.rowcount!=1:raise ValueError('EXACT_ROLE_REQUIRED')
                    await c.execute(text('INSERT INTO competence_hub.auth_password_credentials(portal_user_id,password_hash) VALUES(:id,:hash)'),{'id':UUID(item['id']),'hash':PasswordService(PasswordPolicy(frozenset())).hash(item['password'])})
                await c.execute(text("INSERT INTO competence_hub.topics(id,name,active) VALUES(:topic,'DEMO V1 Fuehrung',true)"),{'topic':topic})
                for name,identifier in f['coaches'].items():
                    user=UUID(f['accounts'][name]['id']) if name in f['accounts'] else None
                    await c.execute(text("INSERT INTO competence_hub.coaches(id,portal_user_id,display_name,public_profile_status) VALUES(:id,:user,:name,'synthetic')"),{'id':UUID(identifier),'user':user,'name':'DEMO V1 '+name})
                    await c.execute(text('INSERT INTO competence_hub.coach_topics(coach_id,topic_id) VALUES(:coach,:topic)'),{'coach':UUID(identifier),'topic':topic})
            elif data['action']=='expire':
                actor=f['accounts'][data['actor']]
                await c.execute(text("UPDATE competence_hub.auth_sessions SET idle_expires_at=created_at+interval '1 millisecond' WHERE portal_user_id=:id"),{'id':UUID(actor['id'])})
            elif data['action']=='invitation_token':
                email=f['invites'][data['role']]['email']
                row=(await c.execute(text("""SELECT o.id,o.encrypted_payload,o.key_version FROM competence_hub.auth_token_delivery_outbox o
                    JOIN competence_hub.auth_one_time_tokens t ON t.id=o.one_time_token_id
                    JOIN competence_hub.portal_users u ON u.id=t.portal_user_id
                    WHERE u.email=:email AND NOT u.active AND t.purpose='invitation' AND t.revoked_at IS NULL AND t.consumed_at IS NULL"""),{'email':email})).mappings().one()
                cipher=SecretCipher(settings.outbox_encryption_keys,settings.outbox_active_key_version,context='auth-token-outbox')
                return {'token':cipher.decrypt(bytes(row['encrypted_payload']),key_version=row['key_version'],subject_id='invitation:'+str(row['id']))}
            elif data['action']=='cleanup':
                token_hashes=(await c.execute(text('SELECT token_hash FROM competence_hub.auth_one_time_tokens WHERE portal_user_id=ANY(:users)'),parameters)).scalars().all()
                own_keys=owned_rate_hashes(f,all_users,token_hashes,key)
                await c.execute(text('DELETE FROM competence_hub.auth_rate_limit_buckets WHERE bucket_key_hash=ANY(:keys)'),{'keys':own_keys})
                for statement in (
                    'DELETE FROM competence_hub.audit_events WHERE actor_user_id=ANY(:users) OR entity_id=ANY(:users)',
                    'DELETE FROM competence_hub.calendar_review_decisions WHERE reviewer_user_id=ANY(:users) OR revision_id IN (SELECT r.id FROM competence_hub.calendar_offer_revisions r JOIN competence_hub.calendar_offers o ON o.id=r.offer_id WHERE o.coach_id=ANY(:coaches))',
                    'DELETE FROM competence_hub.calendar_offer_revisions WHERE offer_id IN (SELECT id FROM competence_hub.calendar_offers WHERE coach_id=ANY(:coaches))',
                    'DELETE FROM competence_hub.calendar_offers WHERE coach_id=ANY(:coaches)',
                    'DELETE FROM competence_hub.coach_topics WHERE coach_id=ANY(:coaches)',
                    'DELETE FROM competence_hub.coaches WHERE id=ANY(:coaches)',
                    'DELETE FROM competence_hub.topics WHERE id=:topic',
                    'DELETE FROM competence_hub.portal_users WHERE id=ANY(:users)',
                ):await c.execute(text(statement),parameters)
            elif data['action']=='reference_rates':
                raw=await c.scalar(text("""SELECT COALESCE(json_agg(r ORDER BY r.action,r.bucket_key_hash)::text,'[]')
                    FROM competence_hub.auth_rate_limit_buckets r WHERE NOT(bucket_key_hash=ANY(:keys))"""),{'keys':shared})
                return {'sha256':hashlib.sha256(raw.encode()).hexdigest()}
            else:raise ValueError('OWNED_ACTION_ONLY')
            return {'status':'PASS'}
    finally:await engine.dispose()


if __name__=='__main__':
    try:print(json.dumps(asyncio.run(action(json.loads(sys.stdin.buffer.read(1024*1024))))))
    except Exception:raise SystemExit(1) from None
