\set ON_ERROR_STOP on
BEGIN;
SET LOCAL ROLE competence_hub_owner;

ALTER TABLE competence_hub.coaches
    ADD COLUMN lifecycle_status text NOT NULL DEFAULT 'draft'
        CHECK (lifecycle_status IN ('draft','active','paused','inactive','archived')),
    ADD COLUMN registry_lock_version integer NOT NULL DEFAULT 1 CHECK (registry_lock_version > 0),
    ADD COLUMN registry_request_id uuid UNIQUE,
    ADD COLUMN publication_floor integer NOT NULL DEFAULT 0 CHECK (publication_floor >= 0);

CREATE TABLE competence_hub.topic_categories (
    code text PRIMARY KEY CHECK (code IN ('personalentwicklung','persoenlichkeitsentwicklung','karrierecoaching')),
    display_name text NOT NULL CHECK (btrim(display_name) <> '')
);
INSERT INTO competence_hub.topic_categories VALUES
    ('personalentwicklung','Personalentwicklung'),
    ('persoenlichkeitsentwicklung','Persönlichkeitsentwicklung'),
    ('karrierecoaching','Karrierecoaching');
CREATE TABLE competence_hub.topic_category_assignments (
    topic_id uuid NOT NULL REFERENCES competence_hub.topics(id) ON DELETE RESTRICT,
    category_code text NOT NULL REFERENCES competence_hub.topic_categories(code),
    PRIMARY KEY (topic_id,category_code)
);

CREATE TABLE competence_hub.coach_profile_revisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    coach_id uuid NOT NULL REFERENCES competence_hub.coaches(id) ON DELETE RESTRICT,
    revision_number integer NOT NULL CHECK (revision_number > 0),
    status text NOT NULL CHECK (status IN ('draft','submitted','abandoned')),
    display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 200),
    academic_suffix text CHECK (length(academic_suffix) <= 100),
    short_intro text NOT NULL CHECK (length(btrim(short_intro)) BETWEEN 1 AND 1000),
    description text CHECK (length(description) <= 10000),
    professional_background text CHECK (length(professional_background) <= 4000),
    profile_path text CHECK (profile_path IS NULL OR (length(profile_path) <= 200 AND profile_path ~ '^/coaches/[a-z0-9]+(-[a-z0-9]+)*/$')),
    created_by uuid NOT NULL REFERENCES competence_hub.portal_users(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (coach_id,revision_number),
    UNIQUE (id,coach_id)
);
CREATE UNIQUE INDEX coach_profile_one_draft ON competence_hub.coach_profile_revisions(coach_id) WHERE status='draft';
CREATE TABLE competence_hub.coach_profile_labels (
    revision_id uuid NOT NULL REFERENCES competence_hub.coach_profile_revisions(id) ON DELETE RESTRICT,
    kind text NOT NULL CHECK (kind IN ('target_group','competency')),
    ordering integer NOT NULL CHECK (ordering >= 0),
    label text NOT NULL CHECK (length(btrim(label)) BETWEEN 1 AND 250),
    PRIMARY KEY (revision_id,kind,ordering),
    UNIQUE (revision_id,kind,label)
);
CREATE TABLE competence_hub.coach_profile_topics (
    revision_id uuid NOT NULL REFERENCES competence_hub.coach_profile_revisions(id) ON DELETE RESTRICT,
    topic_id uuid NOT NULL REFERENCES competence_hub.topics(id) ON DELETE RESTRICT,
    snapshot_name text NOT NULL CHECK (btrim(snapshot_name) <> ''),
    PRIMARY KEY (revision_id,topic_id)
);
CREATE TABLE competence_hub.coach_profile_topic_categories (
    revision_id uuid NOT NULL,
    topic_id uuid NOT NULL,
    category_code text NOT NULL REFERENCES competence_hub.topic_categories(code),
    FOREIGN KEY (revision_id,topic_id) REFERENCES competence_hub.coach_profile_topics(revision_id,topic_id),
    PRIMARY KEY (revision_id,topic_id,category_code)
);
CREATE TABLE competence_hub.coach_offerings (
    revision_id uuid NOT NULL,
    coach_id uuid NOT NULL,
    ordering integer NOT NULL CHECK (ordering >= 0),
    title text NOT NULL CHECK (length(btrim(title)) BETWEEN 1 AND 250),
    type text NOT NULL CHECK (type IN ('lecture','workshop','coaching','individual','other')),
    description text CHECK (length(description) <= 2000),
    active boolean NOT NULL DEFAULT true,
    FOREIGN KEY (revision_id,coach_id) REFERENCES competence_hub.coach_profile_revisions(id,coach_id),
    PRIMARY KEY (revision_id,ordering)
);
CREATE TABLE competence_hub.coach_assets (
    revision_id uuid NOT NULL REFERENCES competence_hub.coach_profile_revisions(id),
    type text NOT NULL CHECK (type='portrait'),
    reference text NOT NULL CHECK (reference ~ '^images/coaches/[a-z0-9]+([-.][a-z0-9]+)*\.(webp|jpg|jpeg|png)$' AND length(reference)<=200),
    sha256 text NOT NULL CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    alt_text text NOT NULL CHECK (length(btrim(alt_text)) BETWEEN 1 AND 250),
    preview_allowed boolean NOT NULL,
    production_allowed boolean NOT NULL,
    active boolean NOT NULL DEFAULT true,
    CHECK (preview_allowed OR production_allowed),
    PRIMARY KEY (revision_id,type)
);
CREATE TABLE competence_hub.coach_profile_approvals (
    revision_id uuid NOT NULL REFERENCES competence_hub.coach_profile_revisions(id),
    kind text NOT NULL CHECK (kind IN ('content_review','person_consent','preview','production')),
    actor_id uuid NOT NULL REFERENCES competence_hub.portal_users(id),
    occurred_at timestamptz NOT NULL DEFAULT now(),
    evidence_ref text NOT NULL CHECK (length(btrim(evidence_ref)) BETWEEN 1 AND 200),
    PRIMARY KEY (revision_id,kind)
);
CREATE TABLE competence_hub.coach_publications (
    coach_id uuid NOT NULL REFERENCES competence_hub.coaches(id),
    environment text NOT NULL CHECK (environment IN ('preview','production')),
    revision_id uuid NOT NULL,
    state text NOT NULL CHECK (state IN ('published','withdrawn')),
    profile_path text NOT NULL,
    actor_id uuid NOT NULL REFERENCES competence_hub.portal_users(id),
    occurred_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (revision_id,coach_id) REFERENCES competence_hub.coach_profile_revisions(id,coach_id),
    PRIMARY KEY (coach_id,environment)
);
CREATE UNIQUE INDEX coach_publications_path_uq ON competence_hub.coach_publications(environment,profile_path) WHERE state='published';

CREATE FUNCTION competence_hub.guard_coach_revision()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF OLD.id <> NEW.id OR OLD.coach_id <> NEW.coach_id OR OLD.revision_number <> NEW.revision_number
       OR OLD.created_by <> NEW.created_by OR OLD.created_at <> NEW.created_at
       OR (OLD.status IN ('submitted','abandoned') AND NEW IS DISTINCT FROM OLD) THEN
        RAISE EXCEPTION 'immutable Coach revision';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_revision_immutable BEFORE UPDATE ON competence_hub.coach_profile_revisions
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_revision();

CREATE FUNCTION competence_hub.guard_coach_revision_child()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
DECLARE revision_status text;
BEGIN
    IF TG_OP <> 'INSERT' THEN
        SELECT status INTO revision_status FROM competence_hub.coach_profile_revisions WHERE id=OLD.revision_id FOR UPDATE;
        IF revision_status IS DISTINCT FROM 'draft' THEN RAISE EXCEPTION 'immutable Coach revision child'; END IF;
    END IF;
    IF TG_OP <> 'DELETE' THEN
        SELECT status INTO revision_status FROM competence_hub.coach_profile_revisions WHERE id=NEW.revision_id FOR UPDATE;
        IF revision_status IS DISTINCT FROM 'draft' THEN RAISE EXCEPTION 'immutable Coach revision child'; END IF;
        RETURN NEW;
    END IF;
    RETURN OLD;
END;
$$;
DO $$ DECLARE t text; BEGIN
    FOREACH t IN ARRAY ARRAY['coach_profile_labels','coach_profile_topics','coach_profile_topic_categories','coach_offerings','coach_assets'] LOOP
        EXECUTE format('CREATE TRIGGER freeze_revision_child BEFORE INSERT OR UPDATE OR DELETE ON competence_hub.%I FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_revision_child()',t);
    END LOOP;
END $$;

CREATE FUNCTION competence_hub.guard_coach_publication()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF TG_OP='UPDATE' AND OLD.state='withdrawn' AND NEW.state='published' AND
       (SELECT revision_number FROM competence_hub.coach_profile_revisions WHERE id=NEW.revision_id) <=
       (SELECT revision_number FROM competence_hub.coach_profile_revisions WHERE id=OLD.revision_id)
    THEN RAISE EXCEPTION 'withdrawn publication requires newer revision'; END IF;
    IF NEW.state='published' AND NOT EXISTS (
        SELECT 1 FROM competence_hub.coach_profile_revisions r JOIN competence_hub.coaches c ON c.id=r.coach_id
        WHERE r.id=NEW.revision_id AND r.coach_id=NEW.coach_id AND r.status='submitted'
        AND c.lifecycle_status='active' AND r.revision_number>c.publication_floor AND r.profile_path=NEW.profile_path
        AND (SELECT count(*) FROM competence_hub.coach_profile_approvals a WHERE a.revision_id=r.id
             AND a.kind IN ('content_review','person_consent',NEW.environment))=3
        AND NOT EXISTS (SELECT 1 FROM competence_hub.coach_assets a WHERE a.revision_id=r.id AND a.active
            AND NOT CASE WHEN NEW.environment='preview' THEN a.preview_allowed ELSE a.production_allowed END)
    ) THEN RAISE EXCEPTION 'unapproved Coach publication'; END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_publication_guard BEFORE INSERT OR UPDATE ON competence_hub.coach_publications
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_publication();

CREATE FUNCTION competence_hub.guard_coach_identity()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF OLD.id <> NEW.id OR OLD.registry_request_id IS DISTINCT FROM NEW.registry_request_id THEN
        RAISE EXCEPTION 'immutable Coach identity';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_identity_immutable BEFORE UPDATE ON competence_hub.coaches
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_identity();

CREATE FUNCTION competence_hub.guard_coach_approval()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    PERFORM 1 FROM competence_hub.coach_profile_revisions WHERE id=NEW.revision_id AND status='submitted' FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'submitted Coach revision required'; END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_approval_guard BEFORE INSERT ON competence_hub.coach_profile_approvals
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_approval();

-- Local migration only. Legacy CAL-1 Coaches are not silently adopted.
CREATE FUNCTION competence_hub.guard_registry_calendar_coach()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
DECLARE coach_key uuid; coach_state text; registry_key uuid;
BEGIN
    IF TG_TABLE_NAME='calendar_offers' THEN
        IF NEW.lifecycle_status='withdrawn' THEN RETURN NEW; END IF;
        coach_key := NEW.coach_id;
    ELSE
        SELECT coach_id INTO coach_key FROM competence_hub.calendar_offers WHERE id=NEW.offer_id;
    END IF;
    SELECT lifecycle_status,registry_request_id INTO coach_state,registry_key
        FROM competence_hub.coaches WHERE id=coach_key FOR UPDATE;
    IF registry_key IS NOT NULL AND coach_state <> 'active' THEN
        RAISE EXCEPTION 'Registry Coach is not active';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER registry_calendar_offer_guard BEFORE INSERT OR UPDATE ON competence_hub.calendar_offers
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_registry_calendar_coach();
CREATE TRIGGER registry_calendar_revision_guard BEFORE INSERT OR UPDATE ON competence_hub.calendar_offer_revisions
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_registry_calendar_coach();

REVOKE DELETE ON competence_hub.coach_profile_revisions,competence_hub.coach_publications FROM competence_hub_app;
REVOKE UPDATE,DELETE ON competence_hub.coach_profile_approvals,competence_hub.topic_categories FROM competence_hub_app;
REVOKE INSERT ON competence_hub.topic_categories FROM competence_hub_app;
INSERT INTO competence_hub.schema_migrations(version,description) VALUES ('0007','Coach Registry revisions lifecycle and scoped publication');
COMMENT ON TABLE competence_hub.coach_profile_revisions IS 'Public-only allowlisted content; private source documents and account credentials prohibited.';
COMMENT ON TABLE competence_hub.coach_profile_approvals IS 'Revision-bound evidence attestations, not automatic consent or publication.';
COMMIT;
