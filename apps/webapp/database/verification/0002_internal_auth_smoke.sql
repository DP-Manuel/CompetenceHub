\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM competence_hub.schema_migrations
        WHERE version = '0002'
    ) THEN
        RAISE EXCEPTION 'Migration 0002 is not registered';
    END IF;
END;
$$;

WITH synthetic_user AS (
    INSERT INTO competence_hub.portal_users (display_name, email)
    VALUES ('Synthetische Authperson', 'synthetic-auth@example.invalid')
    RETURNING id
), password_credential AS (
    INSERT INTO competence_hub.auth_password_credentials (
        portal_user_id,
        password_hash
    )
    SELECT id, '$argon2id$v=19$m=65536,t=3,p=4$synthetic$not-a-real-hash'
    FROM synthetic_user
), login_challenge AS (
    INSERT INTO competence_hub.auth_login_challenges (
        portal_user_id,
        token_hash,
        csrf_token_hash,
        state,
        expires_at
    )
    SELECT
        id,
        decode(repeat('11', 32), 'hex'),
        decode(repeat('12', 32), 'hex'),
        'mfa_required',
        now() + interval '5 minutes'
    FROM synthetic_user
), auth_session AS (
    INSERT INTO competence_hub.auth_sessions (
        portal_user_id,
        token_hash,
        csrf_token_hash,
        mfa_completed_at,
        idle_expires_at,
        absolute_expires_at
    )
    SELECT
        id,
        decode(repeat('21', 32), 'hex'),
        decode(repeat('22', 32), 'hex'),
        now(),
        now() + interval '30 minutes',
        now() + interval '8 hours'
    FROM synthetic_user
), one_time_token AS (
    INSERT INTO competence_hub.auth_one_time_tokens (
        portal_user_id,
        purpose,
        token_hash,
        expires_at
    )
    SELECT
        id,
        'password_reset',
        decode(repeat('31', 32), 'hex'),
        now() + interval '30 minutes'
    FROM synthetic_user
), totp_credential AS (
    INSERT INTO competence_hub.auth_totp_credentials (
        portal_user_id,
        encrypted_secret,
        key_version,
        enabled_at
    )
    SELECT id, decode('01020304', 'hex'), 'synthetic-v1', now()
    FROM synthetic_user
), recovery_code AS (
    INSERT INTO competence_hub.auth_recovery_codes (
        portal_user_id,
        code_hash
    )
    SELECT id, decode(repeat('41', 32), 'hex')
    FROM synthetic_user
)
INSERT INTO competence_hub.auth_rate_limit_buckets (
    action,
    bucket_key_hash,
    window_started_at,
    failed_attempts
)
VALUES ('login', decode(repeat('51', 32), 'hex'), now(), 1);

DO $$
DECLARE
    synthetic_user_id uuid;
BEGIN
    SELECT id
    INTO synthetic_user_id
    FROM competence_hub.portal_users
    WHERE email = 'synthetic-auth@example.invalid';

    IF synthetic_user_id IS NULL THEN
        RAISE EXCEPTION 'Synthetic auth user was not created';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM competence_hub.auth_password_credentials
        WHERE portal_user_id = synthetic_user_id
    ) OR NOT EXISTS (
        SELECT 1
        FROM competence_hub.auth_login_challenges
        WHERE portal_user_id = synthetic_user_id
    ) OR NOT EXISTS (
        SELECT 1
        FROM competence_hub.auth_sessions
        WHERE portal_user_id = synthetic_user_id
    ) OR NOT EXISTS (
        SELECT 1
        FROM competence_hub.auth_one_time_tokens
        WHERE portal_user_id = synthetic_user_id
    ) OR NOT EXISTS (
        SELECT 1
        FROM competence_hub.auth_totp_credentials
        WHERE portal_user_id = synthetic_user_id
    ) OR NOT EXISTS (
        SELECT 1
        FROM competence_hub.auth_recovery_codes
        WHERE portal_user_id = synthetic_user_id
    ) THEN
        RAISE EXCEPTION 'Synthetic auth relationships are incomplete';
    END IF;

    IF has_schema_privilege('competence_hub_app', 'competence_hub', 'CREATE') THEN
        RAISE EXCEPTION 'Runtime role must not create schema objects';
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
