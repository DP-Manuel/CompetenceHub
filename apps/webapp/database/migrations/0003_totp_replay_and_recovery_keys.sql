\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

ALTER TABLE competence_hub.auth_totp_credentials
    ADD COLUMN last_accepted_time_step bigint;

ALTER TABLE competence_hub.auth_totp_credentials
    ADD CONSTRAINT auth_totp_credentials_last_time_step_ck
    CHECK (
        last_accepted_time_step IS NULL
        OR last_accepted_time_step >= 0
    );

ALTER TABLE competence_hub.auth_recovery_codes
    ADD COLUMN key_version text;

UPDATE competence_hub.auth_recovery_codes
SET key_version = 'legacy-unversioned-v1'
WHERE key_version IS NULL;

ALTER TABLE competence_hub.auth_recovery_codes
    ALTER COLUMN key_version SET NOT NULL;

ALTER TABLE competence_hub.auth_recovery_codes
    ADD CONSTRAINT auth_recovery_codes_key_version_ck
    CHECK (btrim(key_version) <> '');

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0003', 'TOTP replay protection and recovery key versions');

COMMENT ON COLUMN competence_hub.auth_totp_credentials.last_accepted_time_step
    IS 'Highest accepted TOTP counter; atomically prevents replay.';
COMMENT ON COLUMN competence_hub.auth_recovery_codes.key_version
    IS 'External HMAC key version used for this recovery-code digest.';

COMMIT;
