\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

CREATE TABLE competence_hub.auth_idempotency_records (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    scope text NOT NULL CHECK (scope = 'auth.invitation.issue'),
    key_hash bytea NOT NULL CHECK (octet_length(key_hash) = 32),
    request_fingerprint bytea NOT NULL
        CHECK (octet_length(request_fingerprint) = 32),
    result_entity_type text NOT NULL CHECK (result_entity_type = 'portal_user'),
    result_entity_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    CONSTRAINT auth_idempotency_records_actor_scope_key_uq
        UNIQUE (actor_user_id, scope, key_hash),
    CONSTRAINT auth_idempotency_records_expiry_ck
        CHECK (expires_at > created_at)
);

CREATE INDEX auth_idempotency_records_expiry_idx
    ON competence_hub.auth_idempotency_records (expires_at);

CREATE TABLE competence_hub.auth_token_delivery_outbox (
    id uuid PRIMARY KEY,
    one_time_token_id uuid NOT NULL UNIQUE
        REFERENCES competence_hub.auth_one_time_tokens(id) ON DELETE CASCADE,
    purpose text NOT NULL CHECK (purpose IN ('invitation', 'password_reset')),
    template_code text NOT NULL CHECK (
        (purpose = 'invitation' AND template_code = 'auth_invitation_v1')
        OR (
            purpose = 'password_reset'
            AND template_code = 'auth_password_reset_v1'
        )
    ),
    recipient_email text,
    encrypted_payload bytea,
    key_version text,
    status text NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'processing', 'delivered', 'failed', 'canceled')
    ),
    attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    available_at timestamptz NOT NULL DEFAULT now(),
    claimed_at timestamptz,
    claim_id uuid,
    lease_expires_at timestamptz,
    completed_at timestamptz,
    last_error_code text CHECK (
        last_error_code IS NULL
        OR (
            btrim(last_error_code) <> ''
            AND length(last_error_code) <= 100
        )
    ),
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT auth_token_delivery_outbox_expiry_ck CHECK (
        expires_at > created_at
        AND available_at <= expires_at
    ),
    CONSTRAINT auth_token_delivery_outbox_state_ck CHECK (
        (
            status = 'pending'
            AND recipient_email IS NOT NULL
            AND btrim(recipient_email) <> ''
            AND length(recipient_email) <= 254
            AND encrypted_payload IS NOT NULL
            AND octet_length(encrypted_payload) > 0
            AND key_version IS NOT NULL
            AND btrim(key_version) <> ''
            AND claimed_at IS NULL
            AND claim_id IS NULL
            AND lease_expires_at IS NULL
            AND completed_at IS NULL
        )
        OR (
            status = 'processing'
            AND recipient_email IS NOT NULL
            AND btrim(recipient_email) <> ''
            AND length(recipient_email) <= 254
            AND encrypted_payload IS NOT NULL
            AND octet_length(encrypted_payload) > 0
            AND key_version IS NOT NULL
            AND btrim(key_version) <> ''
            AND claimed_at IS NOT NULL
            AND claim_id IS NOT NULL
            AND lease_expires_at IS NOT NULL
            AND lease_expires_at > claimed_at
            AND completed_at IS NULL
        )
        OR (
            status IN ('delivered', 'failed', 'canceled')
            AND recipient_email IS NULL
            AND encrypted_payload IS NULL
            AND key_version IS NULL
            AND claimed_at IS NULL
            AND claim_id IS NULL
            AND lease_expires_at IS NULL
            AND completed_at IS NOT NULL
        )
    )
);

CREATE INDEX auth_token_delivery_outbox_pending_idx
    ON competence_hub.auth_token_delivery_outbox (available_at, created_at)
    WHERE status = 'pending';
CREATE INDEX auth_token_delivery_outbox_lease_idx
    ON competence_hub.auth_token_delivery_outbox (lease_expires_at)
    WHERE status = 'processing';
CREATE INDEX auth_token_delivery_outbox_retention_idx
    ON competence_hub.auth_token_delivery_outbox (completed_at)
    WHERE status IN ('delivered', 'failed', 'canceled');

CREATE TRIGGER auth_token_delivery_outbox_touch_updated_at
    BEFORE UPDATE ON competence_hub.auth_token_delivery_outbox
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();

REVOKE ALL ON competence_hub.auth_idempotency_records
    FROM competence_hub_app;
REVOKE ALL ON competence_hub.auth_token_delivery_outbox
    FROM competence_hub_app;
GRANT SELECT, INSERT, UPDATE, DELETE
    ON competence_hub.auth_idempotency_records TO competence_hub_app;
GRANT SELECT, INSERT, UPDATE, DELETE
    ON competence_hub.auth_token_delivery_outbox TO competence_hub_app;

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0004', 'Transactional auth token outbox and idempotency');

COMMENT ON TABLE competence_hub.auth_idempotency_records
    IS 'HMAC-pseudonymized Admin request keys and request fingerprints; no raw keys.';
COMMENT ON TABLE competence_hub.auth_token_delivery_outbox
    IS 'Encrypted single-use auth-token delivery payloads; clear payload and recipient on terminal state.';

COMMIT;
