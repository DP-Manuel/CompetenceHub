\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

-- Preserve all baseline row values; the version uses a constant default.
ALTER TABLE competence_hub.coaching_requests
    ALTER COLUMN company_id DROP NOT NULL,
    ADD COLUMN private_customer_id uuid REFERENCES competence_hub.private_customers(id) ON DELETE RESTRICT,
    ADD COLUMN service_id uuid REFERENCES competence_hub.services(id) ON DELETE RESTRICT,
    ADD COLUMN offer_id uuid REFERENCES competence_hub.calendar_offers(id) ON DELETE RESTRICT,
    ADD COLUMN coach_id uuid REFERENCES competence_hub.coaches(id) ON DELETE RESTRICT,
    ADD COLUMN follow_up_on date,
    ADD COLUMN coach_summary text,
    ADD COLUMN coach_release_id uuid,
    ADD COLUMN version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    ADD CONSTRAINT coaching_requests_exactly_one_customer_ck
        CHECK (num_nonnulls(company_id, private_customer_id) = 1),
    ADD CONSTRAINT coaching_requests_at_most_one_offer_source_ck
        CHECK (num_nonnulls(service_id, offer_id) <= 1),
    ADD CONSTRAINT coaching_requests_coach_release_ck
        CHECK ((coach_id IS NULL) = (coach_release_id IS NULL)
               AND (coach_summary IS NULL OR
                    (coach_release_id IS NOT NULL AND char_length(btrim(coach_summary)) BETWEEN 1 AND 1200)));

CREATE INDEX coaching_requests_company_page_idx ON competence_hub.coaching_requests (company_id, id)
    WHERE company_id IS NOT NULL;
CREATE INDEX coaching_requests_coach_page_idx ON competence_hub.coaching_requests (coach_id, id)
    WHERE coach_id IS NOT NULL;

CREATE TABLE competence_hub.coaching_request_notes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id uuid NOT NULL REFERENCES competence_hub.coaching_requests(id) ON DELETE RESTRICT,
    request_version integer NOT NULL CHECK (request_version > 1),
    author_user_id uuid REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    visibility text NOT NULL CHECK (visibility IN ('internal', 'coach')),
    body text NOT NULL CHECK (char_length(btrim(body)) BETWEEN 1 AND 2000),
    coach_release_id uuid,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (request_id, request_version),
    CHECK ((visibility = 'coach') = (coach_release_id IS NOT NULL))
);

CREATE INDEX coaching_request_notes_coach_release_idx
    ON competence_hub.coaching_request_notes (request_id, coach_release_id, request_version DESC)
    WHERE visibility = 'coach';

CREATE TABLE competence_hub.coaching_request_events (
    request_id uuid NOT NULL REFERENCES competence_hub.coaching_requests(id) ON DELETE RESTRICT,
    version integer NOT NULL CHECK (version >= 1),
    actor_user_id uuid REFERENCES competence_hub.portal_users(id) ON DELETE SET NULL,
    action text NOT NULL CHECK (action IN ('created', 'updated', 'note_added')),
    changed_fields text[] NOT NULL CHECK (
        cardinality(changed_fields) BETWEEN 1 AND 13 AND changed_fields <@ ARRAY[
            'subject', 'description', 'status', 'company_id', 'private_customer_id',
            'responsible_user_id', 'desired_period', 'preferred_format', 'service_id',
            'offer_id', 'coach_id', 'follow_up_on', 'coach_summary', 'notes'
        ]::text[]
    ),
    occurred_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (request_id, version)
);

REVOKE ALL ON competence_hub.coaching_request_notes, competence_hub.coaching_request_events
    FROM PUBLIC, competence_hub_app;
GRANT SELECT, INSERT ON competence_hub.coaching_request_notes, competence_hub.coaching_request_events
    TO competence_hub_app;

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0013', 'Additive coaching request operations, scoped releases, notes and history');
COMMIT;
