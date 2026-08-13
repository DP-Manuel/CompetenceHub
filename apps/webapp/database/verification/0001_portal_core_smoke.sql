\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM competence_hub.schema_migrations
        WHERE version = '0001'
    ) THEN
        RAISE EXCEPTION 'Migration 0001 is not registered';
    END IF;

    IF (SELECT count(*) FROM competence_hub.roles WHERE active) <> 4 THEN
        RAISE EXCEPTION 'Expected four active working roles';
    END IF;
END;
$$;

WITH new_user AS (
    INSERT INTO competence_hub.portal_users (display_name, email)
    VALUES ('Synthetische Adminperson', 'synthetic-admin@example.invalid')
    RETURNING id
), assigned_role AS (
    INSERT INTO competence_hub.user_roles (user_id, role_id, assigned_by_user_id)
    SELECT new_user.id, roles.id, new_user.id
    FROM new_user
    JOIN competence_hub.roles ON roles.code = 'admin'
    RETURNING user_id
), new_company AS (
    INSERT INTO competence_hub.companies (name, industry, status)
    VALUES ('Synthetische Musterfirma', 'Testbranche', 'test')
    RETURNING id
), new_contact AS (
    INSERT INTO competence_hub.company_contacts (
        company_id,
        portal_user_id,
        first_name,
        last_name,
        email
    )
    SELECT
        new_company.id,
        new_user.id,
        'Synthetisch',
        'Kontakt',
        'synthetic-contact@example.invalid'
    FROM new_company
    CROSS JOIN new_user
    RETURNING company_id
), new_topic AS (
    INSERT INTO competence_hub.topics (name)
    VALUES ('Synthetisches Testthema')
    RETURNING id
), new_service AS (
    INSERT INTO competence_hub.services (name, target_group)
    VALUES ('Synthetisches Testformat', 'Unternehmen')
    RETURNING id
), new_request AS (
    INSERT INTO competence_hub.coaching_requests (
        company_id,
        responsible_user_id,
        created_by_user_id,
        subject,
        description,
        status,
        preferred_format
    )
    SELECT
        new_company.id,
        new_user.id,
        new_user.id,
        'Synthetische Testanfrage',
        'Ausschliesslich synthetischer Inhalt fuer den transaktionalen Smoke-Test.',
        'test',
        'Hybrid'
    FROM new_company
    CROSS JOIN new_user
    RETURNING id
), linked_topic AS (
    INSERT INTO competence_hub.request_topics (request_id, topic_id)
    SELECT new_request.id, new_topic.id
    FROM new_request
    CROSS JOIN new_topic
), linked_service AS (
    INSERT INTO competence_hub.request_services (request_id, service_id)
    SELECT new_request.id, new_service.id
    FROM new_request
    CROSS JOIN new_service
)
INSERT INTO competence_hub.audit_events (
    actor_user_id,
    action,
    entity_type,
    entity_id,
    outcome
)
SELECT
    new_user.id,
    'synthetic.create',
    'coaching_request',
    new_request.id,
    'success'
FROM new_user
CROSS JOIN new_request;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM competence_hub.coaching_requests request
        JOIN competence_hub.request_topics topic_link ON topic_link.request_id = request.id
        JOIN competence_hub.request_services service_link ON service_link.request_id = request.id
        WHERE request.subject = 'Synthetische Testanfrage'
    ) THEN
        RAISE EXCEPTION 'Synthetic request relationships were not created';
    END IF;

    IF has_schema_privilege('competence_hub_app', 'competence_hub', 'CREATE') THEN
        RAISE EXCEPTION 'Runtime role must not create schema objects';
    END IF;

    IF has_table_privilege('competence_hub_app', 'competence_hub.schema_migrations', 'SELECT') THEN
        RAISE EXCEPTION 'Runtime role must not read migration metadata';
    END IF;

    IF has_table_privilege('competence_hub_app', 'competence_hub.roles', 'INSERT')
       OR has_table_privilege('competence_hub_app', 'competence_hub.roles', 'UPDATE')
       OR has_table_privilege('competence_hub_app', 'competence_hub.roles', 'DELETE') THEN
        RAISE EXCEPTION 'Runtime role must not mutate role definitions';
    END IF;

    IF has_table_privilege('competence_hub_app', 'competence_hub.portal_users', 'DELETE')
       OR has_table_privilege('competence_hub_app', 'competence_hub.companies', 'DELETE')
       OR has_table_privilege('competence_hub_app', 'competence_hub.coaching_requests', 'DELETE') THEN
        RAISE EXCEPTION 'Runtime role must not physically delete core records';
    END IF;

    IF has_table_privilege('competence_hub_app', 'competence_hub.audit_events', 'UPDATE')
       OR has_table_privilege('competence_hub_app', 'competence_hub.audit_events', 'DELETE') THEN
        RAISE EXCEPTION 'Runtime role must not mutate existing audit events';
    END IF;
END;
$$;

ROLLBACK;
