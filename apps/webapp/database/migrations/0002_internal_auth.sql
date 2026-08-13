\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

CREATE TABLE competence_hub.auth_password_credentials (
    portal_user_id uuid PRIMARY KEY
        REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    password_hash text NOT NULL CHECK (btrim(password_hash) <> ''),
    password_changed_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE competence_hub.auth_login_challenges (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_user_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    token_hash bytea NOT NULL CHECK (octet_length(token_hash) = 32),
    csrf_token_hash bytea NOT NULL CHECK (octet_length(csrf_token_hash) = 32),
    state text NOT NULL CHECK (
        state IN ('mfa_required', 'mfa_enrollment_required')
    ),
    failed_attempts integer NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    consumed_at timestamptz,
    revoked_at timestamptz,
    CONSTRAINT auth_login_challenges_token_hash_uq UNIQUE (token_hash),
    CONSTRAINT auth_login_challenges_expiry_ck CHECK (expires_at > created_at)
);

CREATE INDEX auth_login_challenges_user_active_idx
    ON competence_hub.auth_login_challenges (portal_user_id, expires_at DESC)
    WHERE consumed_at IS NULL AND revoked_at IS NULL;

CREATE TABLE competence_hub.auth_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_user_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    token_hash bytea NOT NULL CHECK (octet_length(token_hash) = 32),
    csrf_token_hash bytea NOT NULL CHECK (octet_length(csrf_token_hash) = 32),
    authentication_level text NOT NULL DEFAULT 'mfa'
        CHECK (authentication_level = 'mfa'),
    created_at timestamptz NOT NULL DEFAULT now(),
    authenticated_at timestamptz NOT NULL DEFAULT now(),
    mfa_completed_at timestamptz NOT NULL,
    last_seen_at timestamptz NOT NULL DEFAULT now(),
    idle_expires_at timestamptz NOT NULL,
    absolute_expires_at timestamptz NOT NULL,
    revoked_at timestamptz,
    revoke_reason text,
    CONSTRAINT auth_sessions_token_hash_uq UNIQUE (token_hash),
    CONSTRAINT auth_sessions_expiry_ck CHECK (
        idle_expires_at > created_at
        AND absolute_expires_at > created_at
        AND idle_expires_at <= absolute_expires_at
    ),
    CONSTRAINT auth_sessions_revocation_ck CHECK (
        (revoked_at IS NULL AND revoke_reason IS NULL)
        OR (
            revoked_at IS NOT NULL
            AND revoke_reason IS NOT NULL
            AND btrim(revoke_reason) <> ''
        )
    )
);

CREATE INDEX auth_sessions_user_active_idx
    ON competence_hub.auth_sessions (portal_user_id, absolute_expires_at DESC)
    WHERE revoked_at IS NULL;
CREATE INDEX auth_sessions_expiry_idx
    ON competence_hub.auth_sessions (absolute_expires_at)
    WHERE revoked_at IS NULL;

CREATE TABLE competence_hub.auth_one_time_tokens (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_user_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    purpose text NOT NULL CHECK (purpose IN ('invitation', 'password_reset')),
    token_hash bytea NOT NULL CHECK (octet_length(token_hash) = 32),
    created_by_user_id uuid
        REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    consumed_at timestamptz,
    revoked_at timestamptz,
    CONSTRAINT auth_one_time_tokens_token_hash_uq UNIQUE (token_hash),
    CONSTRAINT auth_one_time_tokens_expiry_ck CHECK (expires_at > created_at)
);

CREATE INDEX auth_one_time_tokens_user_purpose_active_idx
    ON competence_hub.auth_one_time_tokens (
        portal_user_id,
        purpose,
        expires_at DESC
    )
    WHERE consumed_at IS NULL AND revoked_at IS NULL;

CREATE TABLE competence_hub.auth_totp_credentials (
    portal_user_id uuid PRIMARY KEY
        REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    encrypted_secret bytea NOT NULL CHECK (octet_length(encrypted_secret) > 0),
    key_version text NOT NULL CHECK (btrim(key_version) <> ''),
    enabled_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE competence_hub.auth_recovery_codes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_user_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    code_hash bytea NOT NULL CHECK (octet_length(code_hash) = 32),
    created_at timestamptz NOT NULL DEFAULT now(),
    used_at timestamptz,
    CONSTRAINT auth_recovery_codes_user_hash_uq
        UNIQUE (portal_user_id, code_hash)
);

CREATE INDEX auth_recovery_codes_user_unused_idx
    ON competence_hub.auth_recovery_codes (portal_user_id)
    WHERE used_at IS NULL;

CREATE TABLE competence_hub.auth_rate_limit_buckets (
    action text NOT NULL CHECK (
        action IN ('login', 'invitation', 'password_reset', 'mfa_verify')
    ),
    bucket_key_hash bytea NOT NULL CHECK (octet_length(bucket_key_hash) = 32),
    window_started_at timestamptz NOT NULL,
    failed_attempts integer NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0),
    blocked_until timestamptz,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (action, bucket_key_hash)
);

CREATE INDEX auth_rate_limit_blocked_idx
    ON competence_hub.auth_rate_limit_buckets (blocked_until)
    WHERE blocked_until IS NOT NULL;

CREATE TRIGGER auth_password_credentials_touch_updated_at
    BEFORE UPDATE ON competence_hub.auth_password_credentials
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER auth_totp_credentials_touch_updated_at
    BEFORE UPDATE ON competence_hub.auth_totp_credentials
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER auth_rate_limit_buckets_touch_updated_at
    BEFORE UPDATE ON competence_hub.auth_rate_limit_buckets
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0002', 'Internal authentication foundation');

COMMENT ON TABLE competence_hub.auth_password_credentials
    IS 'Argon2id hashes only; authenticated NO_CACHE.';
COMMENT ON TABLE competence_hub.auth_login_challenges
    IS 'Short-lived pre-authentication challenges; token hashes only.';
COMMENT ON TABLE competence_hub.auth_sessions
    IS 'Server-side internal sessions; token and CSRF hashes only.';
COMMENT ON TABLE competence_hub.auth_one_time_tokens
    IS 'Invitation and password-reset token hashes; never store raw tokens.';
COMMENT ON TABLE competence_hub.auth_totp_credentials
    IS 'TOTP secrets encrypted by an application key held outside PostgreSQL.';
COMMENT ON TABLE competence_hub.auth_recovery_codes
    IS 'Single-use recovery-code HMAC digests; HMAC key remains outside PostgreSQL.';
COMMENT ON TABLE competence_hub.auth_rate_limit_buckets
    IS 'HMAC-pseudonymized account/IP buckets; HMAC key remains outside PostgreSQL.';

COMMIT;
