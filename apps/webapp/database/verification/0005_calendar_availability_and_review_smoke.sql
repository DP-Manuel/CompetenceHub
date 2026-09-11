\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM competence_hub.schema_migrations
        WHERE version = '0005'
    ) THEN
        RAISE EXCEPTION 'Migration 0005 is not registered';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM competence_hub.roles
        WHERE code = 'calendar_reviewer' AND active
    ) THEN
        RAISE EXCEPTION 'Calendar reviewer role is not active';
    END IF;
END;
$$;

WITH synthetic_user AS (
    INSERT INTO competence_hub.portal_users (display_name, email)
    VALUES ('Synthetic Calendar Coach', 'calendar-coach@example.invalid')
    RETURNING id
), synthetic_coach AS (
    INSERT INTO competence_hub.coaches (
        portal_user_id,
        display_name,
        public_profile_status
    )
    SELECT id, 'Synthetic Calendar Coach', 'synthetic'
    FROM synthetic_user
    RETURNING id, portal_user_id
), synthetic_topic AS (
    INSERT INTO competence_hub.topics (name)
    VALUES ('Synthetic Calendar Topic')
    RETURNING id
), linked_topic AS (
    INSERT INTO competence_hub.coach_topics (coach_id, topic_id)
    SELECT coach.id, topic.id
    FROM synthetic_coach coach
    CROSS JOIN synthetic_topic topic
), first_offer AS (
    INSERT INTO competence_hub.calendar_offers (
        coach_id,
        created_by_user_id,
        client_request_id
    )
    SELECT
        coach.id,
        coach.portal_user_id,
        '00000000-0000-4000-8000-000000000501'::uuid
    FROM synthetic_coach coach
    RETURNING id, coach_id, created_by_user_id
), first_revision AS (
    INSERT INTO competence_hub.calendar_offer_revisions (
        offer_id,
        revision_number,
        topic_id,
        title,
        summary,
        starts_at,
        ends_at,
        format_code,
        capacity,
        review_threshold,
        decision_deadline,
        price_display_text,
        created_by_user_id
    )
    SELECT
        offer.id,
        1,
        topic.id,
        'Synthetic Calendar Offer One',
        'Synthetic data for a rollback-only smoke test.',
        '2099-01-15 09:00:00+01'::timestamptz,
        '2099-01-15 10:00:00+01'::timestamptz,
        'online',
        25,
        20,
        '2099-01-10 12:00:00+01'::timestamptz,
        'Synthetic price on request',
        offer.created_by_user_id
    FROM first_offer offer
    CROSS JOIN synthetic_topic topic
    RETURNING id
), second_offer AS (
    INSERT INTO competence_hub.calendar_offers (
        coach_id,
        created_by_user_id,
        client_request_id
    )
    SELECT
        coach.id,
        coach.portal_user_id,
        '00000000-0000-4000-8000-000000000502'::uuid
    FROM synthetic_coach coach
    RETURNING id, created_by_user_id
)
INSERT INTO competence_hub.calendar_offer_revisions (
    offer_id,
    revision_number,
    topic_id,
    title,
    starts_at,
    ends_at,
    format_code,
    public_location,
    capacity,
    review_threshold,
    decision_deadline,
    price_display_text,
    created_by_user_id
)
SELECT
    offer.id,
    1,
    topic.id,
    'Synthetic Overlapping Draft',
    '2099-01-15 09:30:00+01'::timestamptz,
    '2099-01-15 10:30:00+01'::timestamptz,
    'hybrid',
    'Synthetic venue',
    30,
    15,
    '2099-01-10 12:00:00+01'::timestamptz,
    'Synthetic price on request',
    offer.created_by_user_id
FROM second_offer offer
CROSS JOIN synthetic_topic topic;

DO $$
DECLARE
    synthetic_offer_id uuid;
    synthetic_topic_id uuid;
    synthetic_user_id uuid;
BEGIN
    SELECT offer.id, offer.created_by_user_id
    INTO synthetic_offer_id, synthetic_user_id
    FROM competence_hub.calendar_offers offer
    WHERE offer.client_request_id =
        '00000000-0000-4000-8000-000000000501'::uuid;

    SELECT id INTO synthetic_topic_id
    FROM competence_hub.topics
    WHERE name = 'Synthetic Calendar Topic';

    BEGIN
        INSERT INTO competence_hub.calendar_offer_revisions (
            offer_id,
            revision_number,
            topic_id,
            title,
            starts_at,
            ends_at,
            format_code,
            capacity,
            review_threshold,
            decision_deadline,
            price_display_text,
            created_by_user_id
        ) VALUES (
            synthetic_offer_id,
            2,
            synthetic_topic_id,
            'Invalid Format',
            '2099-02-01 09:00:00+01'::timestamptz,
            '2099-02-01 10:00:00+01'::timestamptz,
            'telephone',
            10,
            5,
            '2099-01-25 12:00:00+01'::timestamptz,
            'Synthetic price',
            synthetic_user_id
        );
        RAISE EXCEPTION 'Invalid format code was accepted';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE competence_hub.calendar_offer_revisions
        SET review_threshold = capacity + 1
        WHERE offer_id = synthetic_offer_id
          AND revision_number = 1;
        RAISE EXCEPTION 'Review threshold above capacity was accepted';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE competence_hub.calendar_offers
        SET lifecycle_status = 'withdrawn'
        WHERE id = synthetic_offer_id;
        RAISE EXCEPTION 'Withdrawal without timestamp was accepted';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;

    IF (
        SELECT count(*)
        FROM competence_hub.calendar_offer_revisions revision
        JOIN competence_hub.calendar_offers offer
          ON offer.id = revision.offer_id
        WHERE offer.coach_id = (
            SELECT coach_id
            FROM competence_hub.calendar_offers
            WHERE id = synthetic_offer_id
        )
          AND revision.workflow_status = 'draft'
          AND tstzrange(revision.starts_at, revision.ends_at, '[)')
              && tstzrange(
                  '2099-01-15 09:00:00+01'::timestamptz,
                  '2099-01-15 10:00:00+01'::timestamptz,
                  '[)'
              )
    ) <> 2 THEN
        RAISE EXCEPTION 'Overlapping drafts were not retained';
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

    IF NOT (
        has_table_privilege(
            'competence_hub_app',
            'competence_hub.calendar_offers',
            'SELECT,INSERT,UPDATE'
        )
        AND has_table_privilege(
            'competence_hub_app',
            'competence_hub.calendar_offer_revisions',
            'SELECT,INSERT,UPDATE'
        )
        AND has_table_privilege(
            'competence_hub_app',
            'competence_hub.calendar_review_decisions',
            'SELECT,INSERT'
        )
    ) THEN
        RAISE EXCEPTION 'Runtime role lacks required Calendar DML privileges';
    END IF;

    IF has_table_privilege(
        'competence_hub_app',
        'competence_hub.calendar_offers',
        'DELETE'
    ) OR has_table_privilege(
        'competence_hub_app',
        'competence_hub.calendar_offer_revisions',
        'DELETE'
    ) OR has_table_privilege(
        'competence_hub_app',
        'competence_hub.calendar_review_decisions',
        'UPDATE'
    ) OR has_table_privilege(
        'competence_hub_app',
        'competence_hub.calendar_review_decisions',
        'DELETE'
    ) THEN
        RAISE EXCEPTION 'Runtime role has forbidden Calendar mutation rights';
    END IF;
END;
$$;

WITH reviewer AS (
    INSERT INTO competence_hub.portal_users (display_name, email)
    VALUES ('Synthetic Calendar Reviewer', 'calendar-reviewer@example.invalid')
    RETURNING id
), submitted_revision AS (
    UPDATE competence_hub.calendar_offer_revisions revision
    SET
        workflow_status = 'in_review',
        submitted_at = now()
    FROM competence_hub.calendar_offers offer
    WHERE revision.offer_id = offer.id
      AND offer.client_request_id =
          '00000000-0000-4000-8000-000000000501'::uuid
    RETURNING revision.id
)
INSERT INTO competence_hub.calendar_review_decisions (
    revision_id,
    reviewer_user_id,
    outcome,
    note
)
SELECT
    revision.id,
    reviewer.id,
    'changes_requested',
    'Synthetic internal review note'
FROM submitted_revision revision
CROSS JOIN reviewer;

DO $$
BEGIN
    IF (SELECT count(*) FROM competence_hub.calendar_review_decisions) <> 1 THEN
        RAISE EXCEPTION 'Synthetic review evidence was not created';
    END IF;

    IF (SELECT count(*) FROM competence_hub.calendar_offers) <> 2
       OR (SELECT count(*) FROM competence_hub.calendar_offer_revisions) <> 2 THEN
        RAISE EXCEPTION 'Synthetic Calendar graph is incomplete';
    END IF;
END;
$$;

ROLLBACK;
