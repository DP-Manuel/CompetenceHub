\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM competence_hub.schema_migrations
        WHERE version = '0004'
    ) THEN
        RAISE EXCEPTION 'Migration 0004 is not registered';
    END IF;
END;
$$;

WITH synthetic_actor AS (
    INSERT INTO competence_hub.portal_users (display_name, email)
    VALUES ('Synthetic Outbox Actor', 'outbox-actor@example.invalid')
    RETURNING id
), synthetic_recipient AS (
    INSERT INTO competence_hub.portal_users (display_name, email, active)
    VALUES ('Synthetic Outbox Recipient', 'outbox-recipient@example.invalid', false)
    RETURNING id
), synthetic_token AS (
    INSERT INTO competence_hub.auth_one_time_tokens (
        portal_user_id,
        purpose,
        token_hash,
        created_by_user_id,
        expires_at
    )
    SELECT
        recipient.id,
        'invitation',
        decode(repeat('71', 32), 'hex'),
        actor.id,
        now() + interval '24 hours'
    FROM synthetic_recipient recipient
    CROSS JOIN synthetic_actor actor
    RETURNING id, portal_user_id, created_by_user_id, expires_at
), synthetic_outbox AS (
    INSERT INTO competence_hub.auth_token_delivery_outbox (
        id,
        one_time_token_id,
        purpose,
        template_code,
        recipient_email,
        encrypted_payload,
        key_version,
        expires_at
    )
    SELECT
        '00000000-0000-4000-8000-000000000401'::uuid,
        token.id,
        'invitation',
        'auth_invitation_v1',
        'outbox-recipient@example.invalid',
        decode(repeat('72', 48), 'hex'),
        'synthetic-outbox-v1',
        token.expires_at
    FROM synthetic_token token
)
INSERT INTO competence_hub.auth_idempotency_records (
    actor_user_id,
    scope,
    key_hash,
    request_fingerprint,
    result_entity_type,
    result_entity_id,
    expires_at
)
SELECT
    token.created_by_user_id,
    'auth.invitation.issue',
    decode(repeat('73', 32), 'hex'),
    decode(repeat('74', 32), 'hex'),
    'portal_user',
    token.portal_user_id,
    now() + interval '24 hours'
FROM synthetic_token token;

DO $$
DECLARE
    outbox_count integer;
    idempotency_count integer;
BEGIN
    SELECT count(*) INTO outbox_count
    FROM competence_hub.auth_token_delivery_outbox
    WHERE id = '00000000-0000-4000-8000-000000000401'::uuid
      AND status = 'pending';

    SELECT count(*) INTO idempotency_count
    FROM competence_hub.auth_idempotency_records
    WHERE scope = 'auth.invitation.issue';

    IF outbox_count <> 1 OR idempotency_count <> 1 THEN
        RAISE EXCEPTION 'Synthetic outbox/idempotency records are incomplete';
    END IF;

    IF has_schema_privilege('competence_hub_app', 'competence_hub', 'CREATE') THEN
        RAISE EXCEPTION 'Runtime role must not create schema objects';
    END IF;

    IF NOT (
        has_table_privilege(
            'competence_hub_app',
            'competence_hub.auth_token_delivery_outbox',
            'SELECT'
        )
        AND has_table_privilege(
            'competence_hub_app',
            'competence_hub.auth_token_delivery_outbox',
            'INSERT'
        )
        AND has_table_privilege(
            'competence_hub_app',
            'competence_hub.auth_token_delivery_outbox',
            'UPDATE'
        )
        AND has_table_privilege(
            'competence_hub_app',
            'competence_hub.auth_token_delivery_outbox',
            'DELETE'
        )
    ) THEN
        RAISE EXCEPTION 'Runtime role lacks required outbox DML privileges';
    END IF;

    IF has_table_privilege(
        'competence_hub_app',
        'competence_hub.schema_migrations',
        'SELECT'
    ) THEN
        RAISE EXCEPTION 'Runtime role must not read migration metadata';
    END IF;
END;
$$;

ROLLBACK;
