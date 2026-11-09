"""Private synthetic seed/inspection worker, called via root's binary SSH pipe.

No real identities, migrations, arbitrary SQL input or production connection.
"""
import asyncio
import base64
import json
import sys
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.tokens import keyed_digest

URL = 'postgresql+asyncpg://postgres@/competence_hub_staging?host=/var/run/postgresql'


async def action(data):
    engine = create_async_engine(URL, hide_parameters=True)
    try:
        async with engine.begin() as connection:
            await connection.execute(text('SET LOCAL ROLE competence_hub_owner'))
            accounts = data['fixture']['accounts']
            expected = {'admin': 'admin', 'reviewer': 'calendar_reviewer', 'coach': 'coach', 'coach_two': 'coach'}
            if set(accounts) != set(expected):
                raise ValueError('SYNTHETIC_ROLES_ONLY')
            for key, item in accounts.items():
                UUID(item['id'])
                if item['role'] != expected[key] or item['email'] != 'synthetic-vps-' + UUID(item['id']).hex + '@example.invalid':
                    raise ValueError('SYNTHETIC_IDENTITIES_ONLY')
            if data['action'] == 'seed':
                if await connection.scalar(text('SELECT count(*) FROM competence_hub.portal_users')):
                    raise ValueError('EMPTY_TARGET_REQUIRED')
                for key, item in accounts.items():
                    user = UUID(item['id'])
                    await connection.execute(text("INSERT INTO competence_hub.portal_users(id,display_name,email,active) VALUES(:id,:name,:email,true)"),
                        {'id': user, 'name': 'DEMO ' + key, 'email': item['email']})
                    bound=await connection.execute(text("INSERT INTO competence_hub.user_roles(user_id,role_id) SELECT :id,id FROM competence_hub.roles WHERE code=:role AND active"),
                        {'id': user, 'role': item['role']})
                    if bound.rowcount!=1:raise ValueError('EXACT_ACTIVE_ROLE_REQUIRED')
                    password_hash = PasswordService(PasswordPolicy(frozenset())).hash(item['password'])
                    await connection.execute(text('INSERT INTO competence_hub.auth_password_credentials(portal_user_id,password_hash) VALUES(:id,:hash)'),
                        {'id': user, 'hash': password_hash})
                topic = UUID(data['fixture']['topic'])
                await connection.execute(text("INSERT INTO competence_hub.topics(id,name,active) VALUES(:id,'DEMO Fuehrung und Zusammenarbeit',true)"), {'id': topic})
                for key in ('coach', 'coach_two'):
                    coach = UUID(data['fixture']['coaches'][key])
                    await connection.execute(text("INSERT INTO competence_hub.coaches(id,portal_user_id,display_name,public_profile_status) VALUES(:id,:user,:name,'synthetic')"),
                        {'id': coach, 'user': UUID(accounts[key]['id']), 'name': 'DEMO ' + key})
                    await connection.execute(text('INSERT INTO competence_hub.coach_topics(coach_id,topic_id) VALUES(:coach,:topic)'), {'coach': coach, 'topic': topic})
            elif data['action'] == 'expire':
                item = accounts[data['actor']]
                await connection.execute(text("UPDATE competence_hub.auth_sessions SET idle_expires_at=created_at+interval '1 millisecond' WHERE portal_user_id=:id"), {'id': UUID(item['id'])})
            elif data['action'] == 'cleanup':
                users = [UUID(item['id']) for item in accounts.values()]
                coaches = [UUID(value) for value in data['fixture']['coaches'].values()]
                statements = [
                    'DELETE FROM competence_hub.audit_events WHERE actor_user_id=ANY(:users) OR entity_id=ANY(:users)',
                    'DELETE FROM competence_hub.calendar_review_decisions WHERE reviewer_user_id=ANY(:users) OR revision_id IN (SELECT r.id FROM competence_hub.calendar_offer_revisions r JOIN competence_hub.calendar_offers o ON o.id=r.offer_id WHERE o.coach_id=ANY(:coaches))',
                    'DELETE FROM competence_hub.calendar_offer_revisions WHERE offer_id IN (SELECT id FROM competence_hub.calendar_offers WHERE coach_id=ANY(:coaches))',
                    'DELETE FROM competence_hub.calendar_offers WHERE coach_id=ANY(:coaches)',
                    'DELETE FROM competence_hub.coach_topics WHERE coach_id=ANY(:coaches)',
                    'DELETE FROM competence_hub.coaches WHERE id=ANY(:coaches)',
                    'DELETE FROM competence_hub.topics WHERE id=:topic',
                    'DELETE FROM competence_hub.portal_users WHERE id=ANY(:users)',
                ]
                for statement in statements:
                    await connection.execute(text(statement), {'users': users, 'coaches': coaches, 'topic': UUID(data['fixture']['topic'])})
                rate_key = base64.b64decode(data['fixture']['rate_key'], validate=True)
                scopes = ['login:account:' + item['email'] for item in accounts.values()]
                scopes += ['mfa:user:' + item['id'] for item in accounts.values()]
                scopes += [name + ':ip:127.0.0.1' for name in ('login', 'mfa')]
                await connection.execute(text('DELETE FROM competence_hub.auth_rate_limit_buckets WHERE bucket_key_hash=ANY(:keys)'),
                                         {'keys': [keyed_digest(scope, rate_key) for scope in scopes]})
            elif data['action'] != 'inspect':
                raise ValueError('SYNTHETIC_ACTION_ONLY')
            counts = {}
            for table in ('portal_users', 'calendar_offers', 'calendar_offer_revisions', 'calendar_review_decisions'):
                counts[table] = await connection.scalar(text('SELECT count(*) FROM competence_hub.' + table))
            return {'status': 'PASS', 'counts': counts}
    finally:
        await engine.dispose()


if __name__ == '__main__':
    try:
        data = json.loads(sys.stdin.buffer.read(1024 * 1024))
        print(json.dumps(asyncio.run(action(data))))
    except Exception:
        raise SystemExit(1) from None
