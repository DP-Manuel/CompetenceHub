\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

CREATE TABLE competence_hub.schema_migrations (
    version text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now(),
    description text NOT NULL CHECK (btrim(description) <> '')
);

CREATE FUNCTION competence_hub.touch_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TABLE competence_hub.portal_users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name text NOT NULL CHECK (btrim(display_name) <> ''),
    email text NOT NULL CHECK (btrim(email) <> '' AND position('@' IN email) > 1),
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX portal_users_email_ci_uq
    ON competence_hub.portal_users (lower(email));

CREATE TABLE competence_hub.roles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL CHECK (btrim(code) <> ''),
    display_name text NOT NULL CHECK (btrim(display_name) <> ''),
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT roles_code_uq UNIQUE (code)
);

CREATE TABLE competence_hub.user_roles (
    user_id uuid NOT NULL REFERENCES competence_hub.portal_users(id) ON DELETE CASCADE,
    role_id uuid NOT NULL REFERENCES competence_hub.roles(id) ON DELETE RESTRICT,
    assigned_at timestamptz NOT NULL DEFAULT now(),
    assigned_by_user_id uuid REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE competence_hub.companies (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL CHECK (btrim(name) <> ''),
    industry text,
    status text NOT NULL CHECK (btrim(status) <> ''),
    internal_notes text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX companies_name_ci_idx
    ON competence_hub.companies (lower(name));
CREATE INDEX companies_status_idx
    ON competence_hub.companies (status);

CREATE TABLE competence_hub.company_contacts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid NOT NULL REFERENCES competence_hub.companies(id) ON DELETE RESTRICT,
    portal_user_id uuid REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    first_name text NOT NULL CHECK (btrim(first_name) <> ''),
    last_name text NOT NULL CHECK (btrim(last_name) <> ''),
    email text NOT NULL CHECK (btrim(email) <> '' AND position('@' IN email) > 1),
    phone text,
    job_function text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX company_contacts_company_idx
    ON competence_hub.company_contacts (company_id);
CREATE INDEX company_contacts_email_ci_idx
    ON competence_hub.company_contacts (lower(email));
CREATE INDEX company_contacts_portal_user_idx
    ON competence_hub.company_contacts (portal_user_id)
    WHERE portal_user_id IS NOT NULL;

CREATE TABLE competence_hub.coaches (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    portal_user_id uuid UNIQUE REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    display_name text NOT NULL CHECK (btrim(display_name) <> ''),
    public_profile_status text NOT NULL CHECK (btrim(public_profile_status) <> ''),
    internal_availability text,
    region text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX coaches_profile_status_idx
    ON competence_hub.coaches (public_profile_status);
CREATE INDEX coaches_region_idx
    ON competence_hub.coaches (region)
    WHERE region IS NOT NULL;

CREATE TABLE competence_hub.topics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL CHECK (btrim(name) <> ''),
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX topics_name_ci_uq
    ON competence_hub.topics (lower(name));

CREATE TABLE competence_hub.coach_topics (
    coach_id uuid NOT NULL REFERENCES competence_hub.coaches(id) ON DELETE CASCADE,
    topic_id uuid NOT NULL REFERENCES competence_hub.topics(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (coach_id, topic_id)
);

CREATE INDEX coach_topics_topic_idx
    ON competence_hub.coach_topics (topic_id);

CREATE TABLE competence_hub.services (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL CHECK (btrim(name) <> ''),
    target_group text NOT NULL CHECK (btrim(target_group) <> ''),
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX services_name_ci_uq
    ON competence_hub.services (lower(name));

CREATE TABLE competence_hub.coach_services (
    coach_id uuid NOT NULL REFERENCES competence_hub.coaches(id) ON DELETE CASCADE,
    service_id uuid NOT NULL REFERENCES competence_hub.services(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (coach_id, service_id)
);

CREATE INDEX coach_services_service_idx
    ON competence_hub.coach_services (service_id);

CREATE TABLE competence_hub.coaching_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid NOT NULL REFERENCES competence_hub.companies(id) ON DELETE RESTRICT,
    responsible_user_id uuid REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    created_by_user_id uuid REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    subject text NOT NULL CHECK (btrim(subject) <> ''),
    description text NOT NULL CHECK (btrim(description) <> ''),
    status text NOT NULL CHECK (btrim(status) <> ''),
    desired_period text,
    preferred_format text
);

CREATE INDEX coaching_requests_company_created_idx
    ON competence_hub.coaching_requests (company_id, created_at DESC);
CREATE INDEX coaching_requests_status_created_idx
    ON competence_hub.coaching_requests (status, created_at DESC);
CREATE INDEX coaching_requests_responsible_idx
    ON competence_hub.coaching_requests (responsible_user_id)
    WHERE responsible_user_id IS NOT NULL;

CREATE TABLE competence_hub.request_topics (
    request_id uuid NOT NULL REFERENCES competence_hub.coaching_requests(id) ON DELETE CASCADE,
    topic_id uuid NOT NULL REFERENCES competence_hub.topics(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (request_id, topic_id)
);

CREATE INDEX request_topics_topic_idx
    ON competence_hub.request_topics (topic_id);

CREATE TABLE competence_hub.request_services (
    request_id uuid NOT NULL REFERENCES competence_hub.coaching_requests(id) ON DELETE CASCADE,
    service_id uuid NOT NULL REFERENCES competence_hub.services(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (request_id, service_id)
);

CREATE INDEX request_services_service_idx
    ON competence_hub.request_services (service_id);

CREATE TABLE competence_hub.audit_events (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_user_id uuid REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    action text NOT NULL CHECK (btrim(action) <> ''),
    entity_type text NOT NULL CHECK (btrim(entity_type) <> ''),
    entity_id uuid,
    outcome text NOT NULL CHECK (btrim(outcome) <> '')
);

CREATE INDEX audit_events_occurred_idx
    ON competence_hub.audit_events (occurred_at DESC);
CREATE INDEX audit_events_actor_idx
    ON competence_hub.audit_events (actor_user_id, occurred_at DESC)
    WHERE actor_user_id IS NOT NULL;
CREATE INDEX audit_events_entity_idx
    ON competence_hub.audit_events (entity_type, entity_id, occurred_at DESC)
    WHERE entity_id IS NOT NULL;

CREATE TRIGGER portal_users_touch_updated_at
    BEFORE UPDATE ON competence_hub.portal_users
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER roles_touch_updated_at
    BEFORE UPDATE ON competence_hub.roles
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER companies_touch_updated_at
    BEFORE UPDATE ON competence_hub.companies
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER company_contacts_touch_updated_at
    BEFORE UPDATE ON competence_hub.company_contacts
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER coaches_touch_updated_at
    BEFORE UPDATE ON competence_hub.coaches
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER topics_touch_updated_at
    BEFORE UPDATE ON competence_hub.topics
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER services_touch_updated_at
    BEFORE UPDATE ON competence_hub.services
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER coaching_requests_touch_updated_at
    BEFORE UPDATE ON competence_hub.coaching_requests
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();

INSERT INTO competence_hub.roles (code, display_name)
VALUES
    ('admin', 'Admin'),
    ('internal', 'Intern'),
    ('coach', 'Coach'),
    ('company_contact', 'Firmenkontakt');

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0001', 'B2B-first portal core');

REVOKE ALL ON TABLE competence_hub.schema_migrations FROM competence_hub_app;
REVOKE INSERT, UPDATE, DELETE ON TABLE competence_hub.roles FROM competence_hub_app;
REVOKE DELETE ON TABLE competence_hub.portal_users FROM competence_hub_app;
REVOKE DELETE ON TABLE competence_hub.companies FROM competence_hub_app;
REVOKE DELETE ON TABLE competence_hub.company_contacts FROM competence_hub_app;
REVOKE DELETE ON TABLE competence_hub.coaches FROM competence_hub_app;
REVOKE DELETE ON TABLE competence_hub.topics FROM competence_hub_app;
REVOKE DELETE ON TABLE competence_hub.services FROM competence_hub_app;
REVOKE DELETE ON TABLE competence_hub.coaching_requests FROM competence_hub_app;
REVOKE UPDATE, DELETE ON TABLE competence_hub.audit_events FROM competence_hub_app;

COMMENT ON TABLE competence_hub.portal_users IS 'Personal data; authenticated NO_CACHE.';
COMMENT ON TABLE competence_hub.company_contacts IS 'Business contact personal data; authenticated NO_CACHE.';
COMMENT ON COLUMN competence_hub.companies.internal_notes IS 'Confidential internal notes; never expose by default.';
COMMENT ON COLUMN competence_hub.coaching_requests.description IS 'Confidential coaching need; minimize content and never cache offline.';
COMMENT ON TABLE competence_hub.audit_events IS 'Append-oriented security audit; no secrets, tokens or raw personal payloads.';

COMMIT;
