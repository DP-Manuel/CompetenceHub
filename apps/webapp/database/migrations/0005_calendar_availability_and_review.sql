\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

CREATE TABLE competence_hub.calendar_offers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    coach_id uuid NOT NULL
        REFERENCES competence_hub.coaches(id) ON DELETE RESTRICT,
    created_by_user_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE RESTRICT,
    client_request_id uuid NOT NULL,
    lifecycle_status text NOT NULL DEFAULT 'active' CHECK (
        lifecycle_status IN ('active', 'withdrawn')
    ),
    lock_version bigint NOT NULL DEFAULT 1 CHECK (lock_version > 0),
    withdrawn_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT calendar_offers_actor_request_uq
        UNIQUE (created_by_user_id, client_request_id),
    CONSTRAINT calendar_offers_withdrawal_state_ck CHECK (
        (lifecycle_status = 'active' AND withdrawn_at IS NULL)
        OR (lifecycle_status = 'withdrawn' AND withdrawn_at IS NOT NULL)
    ),
    CONSTRAINT calendar_offers_updated_at_ck CHECK (updated_at >= created_at)
);

CREATE INDEX calendar_offers_coach_lifecycle_idx
    ON competence_hub.calendar_offers (coach_id, lifecycle_status);

CREATE TABLE competence_hub.calendar_offer_revisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    offer_id uuid NOT NULL
        REFERENCES competence_hub.calendar_offers(id) ON DELETE RESTRICT,
    revision_number integer NOT NULL CHECK (revision_number > 0),
    workflow_status text NOT NULL DEFAULT 'draft' CHECK (
        workflow_status IN (
            'draft',
            'in_review',
            'changes_requested',
            'published',
            'superseded'
        )
    ),
    topic_id uuid NOT NULL
        REFERENCES competence_hub.topics(id) ON DELETE RESTRICT,
    title text NOT NULL CHECK (
        btrim(title) <> '' AND char_length(title) <= 160
    ),
    summary text CHECK (
        summary IS NULL
        OR (btrim(summary) <> '' AND char_length(summary) <= 1200)
    ),
    starts_at timestamptz NOT NULL,
    ends_at timestamptz NOT NULL,
    time_zone text NOT NULL DEFAULT 'Europe/Berlin' CHECK (
        btrim(time_zone) <> '' AND char_length(time_zone) <= 64
    ),
    format_code text NOT NULL CHECK (
        format_code IN ('online', 'praesenz', 'hybrid')
    ),
    public_location text CHECK (
        public_location IS NULL
        OR (
            btrim(public_location) <> ''
            AND char_length(public_location) <= 200
        )
    ),
    capacity integer NOT NULL CHECK (capacity BETWEEN 1 AND 500),
    review_threshold integer NOT NULL CHECK (
        review_threshold BETWEEN 1 AND capacity
    ),
    decision_deadline timestamptz NOT NULL,
    price_display_text text NOT NULL CHECK (
        btrim(price_display_text) <> ''
        AND char_length(price_display_text) <= 200
    ),
    created_by_user_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE RESTRICT,
    submitted_at timestamptz,
    published_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT calendar_offer_revisions_offer_number_uq
        UNIQUE (offer_id, revision_number),
    CONSTRAINT calendar_offer_revisions_time_ck CHECK (
        ends_at > starts_at AND decision_deadline < starts_at
    ),
    CONSTRAINT calendar_offer_revisions_location_ck CHECK (
        format_code = 'online' OR public_location IS NOT NULL
    ),
    CONSTRAINT calendar_offer_revisions_workflow_time_ck CHECK (
        (
            workflow_status = 'draft'
            AND submitted_at IS NULL
            AND published_at IS NULL
        )
        OR (
            workflow_status IN ('in_review', 'changes_requested')
            AND submitted_at IS NOT NULL
            AND published_at IS NULL
        )
        OR (
            workflow_status = 'published'
            AND submitted_at IS NOT NULL
            AND published_at IS NOT NULL
        )
        OR (
            workflow_status = 'superseded'
            AND submitted_at IS NOT NULL
        )
    ),
    CONSTRAINT calendar_offer_revisions_timestamp_order_ck CHECK (
        updated_at >= created_at
        AND (submitted_at IS NULL OR submitted_at >= created_at)
        AND (published_at IS NULL OR published_at >= submitted_at)
    )
);

CREATE UNIQUE INDEX calendar_offer_revisions_one_draft_uq
    ON competence_hub.calendar_offer_revisions (offer_id)
    WHERE workflow_status = 'draft';
CREATE UNIQUE INDEX calendar_offer_revisions_one_review_uq
    ON competence_hub.calendar_offer_revisions (offer_id)
    WHERE workflow_status = 'in_review';
CREATE UNIQUE INDEX calendar_offer_revisions_one_changes_requested_uq
    ON competence_hub.calendar_offer_revisions (offer_id)
    WHERE workflow_status = 'changes_requested';
CREATE UNIQUE INDEX calendar_offer_revisions_one_published_uq
    ON competence_hub.calendar_offer_revisions (offer_id)
    WHERE workflow_status = 'published';
CREATE INDEX calendar_offer_revisions_review_queue_idx
    ON competence_hub.calendar_offer_revisions (starts_at, offer_id)
    WHERE workflow_status = 'in_review';
CREATE INDEX calendar_offer_revisions_public_time_idx
    ON competence_hub.calendar_offer_revisions (starts_at, ends_at)
    WHERE workflow_status = 'published';
CREATE INDEX calendar_offer_revisions_topic_time_idx
    ON competence_hub.calendar_offer_revisions (topic_id, starts_at);

CREATE TABLE competence_hub.calendar_review_decisions (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    revision_id uuid NOT NULL
        REFERENCES competence_hub.calendar_offer_revisions(id)
        ON DELETE RESTRICT,
    reviewer_user_id uuid NOT NULL
        REFERENCES competence_hub.portal_users(id) ON DELETE RESTRICT,
    outcome text NOT NULL CHECK (
        outcome IN ('published', 'changes_requested')
    ),
    note text CHECK (
        note IS NULL
        OR (btrim(note) <> '' AND char_length(note) <= 1000)
    ),
    decided_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT calendar_review_decisions_revision_uq UNIQUE (revision_id)
);

CREATE INDEX calendar_review_decisions_revision_idx
    ON competence_hub.calendar_review_decisions (revision_id, decided_at DESC);
CREATE INDEX calendar_review_decisions_reviewer_idx
    ON competence_hub.calendar_review_decisions (
        reviewer_user_id,
        decided_at DESC
    );

CREATE TRIGGER calendar_offers_touch_updated_at
    BEFORE UPDATE ON competence_hub.calendar_offers
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();
CREATE TRIGGER calendar_offer_revisions_touch_updated_at
    BEFORE UPDATE ON competence_hub.calendar_offer_revisions
    FOR EACH ROW EXECUTE FUNCTION competence_hub.touch_updated_at();

INSERT INTO competence_hub.roles (code, display_name)
VALUES ('calendar_reviewer', 'Kalenderpruefung');

REVOKE ALL ON competence_hub.calendar_offers FROM competence_hub_app;
REVOKE ALL ON competence_hub.calendar_offer_revisions FROM competence_hub_app;
REVOKE ALL ON competence_hub.calendar_review_decisions FROM competence_hub_app;
GRANT SELECT, INSERT, UPDATE
    ON competence_hub.calendar_offers TO competence_hub_app;
GRANT SELECT, INSERT, UPDATE
    ON competence_hub.calendar_offer_revisions TO competence_hub_app;
GRANT SELECT, INSERT
    ON competence_hub.calendar_review_decisions TO competence_hub_app;
GRANT USAGE, SELECT
    ON SEQUENCE competence_hub.calendar_review_decisions_id_seq
    TO competence_hub_app;

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0005', 'Calendar availability and review foundation');

COMMENT ON TABLE competence_hub.calendar_offers
    IS 'Stable Coach-owned calendar offer identity; no reservations or attendees.';
COMMENT ON TABLE competence_hub.calendar_offer_revisions
    IS 'Versioned offer copy; public projection must expose published fields only.';
COMMENT ON COLUMN competence_hub.calendar_offer_revisions.review_threshold
    IS 'Internal review threshold; never expose in the public projection.';
COMMENT ON COLUMN competence_hub.calendar_offer_revisions.public_location
    IS 'Public venue or online label; never store meeting secrets or access tokens.';
COMMENT ON TABLE competence_hub.calendar_review_decisions
    IS 'Append-only internal review evidence; notes are private and never public.';

COMMIT;
