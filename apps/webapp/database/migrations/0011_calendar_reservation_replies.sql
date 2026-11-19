\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

ALTER TABLE competence_hub.calendar_reservation_events
    DROP CONSTRAINT calendar_reservation_events_event_check,
    ADD CONSTRAINT calendar_reservation_events_event_check CHECK (event IN (
        'submitted', 'seats_changed', 'clarification_requested', 'clarification_answered',
        'approved', 'rejected', 'withdrawn', 'offer_cancelled'
    ));

CREATE INDEX calendar_reservation_events_activity_idx
    ON competence_hub.calendar_reservation_events (occurred_at DESC, reservation_id, version DESC);
CREATE INDEX calendar_reservations_offer_idx
    ON competence_hub.calendar_reservations (offer_id, id);

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0011', 'Calendar clarification replies and activity lookup');
COMMIT;
