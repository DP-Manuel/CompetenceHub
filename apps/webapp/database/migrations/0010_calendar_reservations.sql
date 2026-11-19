\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

CREATE TABLE competence_hub.calendar_reservations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    offer_id uuid NOT NULL REFERENCES competence_hub.calendar_offers(id),
    revision_number integer NOT NULL,
    company_id uuid NOT NULL REFERENCES competence_hub.companies(id),
    contact_id uuid NOT NULL REFERENCES competence_hub.company_contacts(id),
    requested_by uuid NOT NULL REFERENCES competence_hub.portal_users(id),
    seats integer NOT NULL CHECK (seats BETWEEN 1 AND 500),
    status text NOT NULL CHECK (
        status IN ('pending', 'clarification', 'approved', 'rejected', 'withdrawn', 'cancelled')
    ),
    phone text CHECK (char_length(phone) <= 50),
    message text CHECK (char_length(message) <= 500),
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    FOREIGN KEY (offer_id, revision_number)
        REFERENCES competence_hub.calendar_offer_revisions(offer_id, revision_number)
);

CREATE UNIQUE INDEX calendar_reservations_one_occupied_company_offer
    ON competence_hub.calendar_reservations (offer_id, company_id)
    WHERE status IN ('pending', 'clarification', 'approved');
CREATE INDEX calendar_reservations_company_idx
    ON competence_hub.calendar_reservations (company_id, id);

CREATE TABLE competence_hub.calendar_reservation_events (
    reservation_id uuid NOT NULL REFERENCES competence_hub.calendar_reservations(id),
    version integer NOT NULL,
    actor_id uuid NOT NULL REFERENCES competence_hub.portal_users(id),
    occurred_at timestamptz NOT NULL,
    event text NOT NULL CHECK (event IN (
        'submitted', 'seats_changed', 'clarification_requested', 'approved',
        'rejected', 'withdrawn', 'offer_cancelled'
    )),
    from_status text,
    to_status text NOT NULL,
    seats_before integer NOT NULL,
    seats_after integer NOT NULL,
    occupied_delta integer NOT NULL,
    threshold_reached boolean NOT NULL DEFAULT false,
    reason text CHECK (char_length(reason) <= 500),
    request_id uuid,
    request_digest text,
    PRIMARY KEY (reservation_id, version),
    UNIQUE (actor_id, request_id),
    CHECK ((request_id IS NULL) = (request_digest IS NULL))
);

REVOKE ALL ON competence_hub.calendar_reservations,
    competence_hub.calendar_reservation_events FROM PUBLIC, competence_hub_app;
GRANT SELECT, INSERT ON competence_hub.calendar_reservations,
    competence_hub.calendar_reservation_events TO competence_hub_app;
GRANT UPDATE (seats, status, version) ON competence_hub.calendar_reservations
    TO competence_hub_app;

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0010', 'Calendar reservation requests and append-only decisions');
COMMIT;
