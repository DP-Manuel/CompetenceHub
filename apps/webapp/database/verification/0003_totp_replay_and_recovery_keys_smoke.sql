\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM competence_hub.schema_migrations
        WHERE version = '0003'
    ) THEN
        RAISE EXCEPTION 'Migration 0003 is not registered';
    END IF;
END;
$$;

WITH synthetic_user AS (
    INSERT INTO competence_hub.portal_users (display_name, email)
    VALUES ('Synthetic TOTP User', 'synthetic-totp@example.invalid')
    RETURNING id
), totp_credential AS (
    INSERT INTO competence_hub.auth_totp_credentials (
        portal_user_id,
        encrypted_secret,
        key_version,
        enabled_at,
        last_accepted_time_step
    )
    SELECT
        id,
        decode(repeat('61', 48), 'hex'),
        'synthetic-totp-v1',
        now(),
        123456
    FROM synthetic_user
)
INSERT INTO competence_hub.auth_recovery_codes (
    portal_user_id,
    code_hash,
    key_version
)
SELECT
    id,
    decode(repeat('62', 32), 'hex'),
    'synthetic-recovery-v1'
FROM synthetic_user;

DO $$
DECLARE
    synthetic_user_id uuid;
    accepted_time_step bigint;
    recovery_key_version text;
BEGIN
    SELECT id
    INTO synthetic_user_id
    FROM competence_hub.portal_users
    WHERE email = 'synthetic-totp@example.invalid';

    SELECT last_accepted_time_step
    INTO accepted_time_step
    FROM competence_hub.auth_totp_credentials
    WHERE portal_user_id = synthetic_user_id;

    SELECT key_version
    INTO recovery_key_version
    FROM competence_hub.auth_recovery_codes
    WHERE portal_user_id = synthetic_user_id;

    IF accepted_time_step <> 123456 THEN
        RAISE EXCEPTION 'TOTP replay counter was not persisted';
    END IF;

    IF recovery_key_version <> 'synthetic-recovery-v1' THEN
        RAISE EXCEPTION 'Recovery key version was not persisted';
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
