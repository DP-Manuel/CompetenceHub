\set ON_ERROR_STOP on
BEGIN;
SET LOCAL ROLE competence_hub_owner;

-- Version zero preserves historical rows and never fabricates object consent.
ALTER TABLE competence_hub.coach_profile_revisions
    ADD COLUMN target_version smallint NOT NULL DEFAULT 0 CHECK (target_version IN (0,1)),
    ADD COLUMN presentation jsonb CHECK (presentation IS NULL OR jsonb_typeof(presentation)='object'),
    ADD COLUMN boundaries jsonb NOT NULL DEFAULT '[]' CHECK (jsonb_typeof(boundaries)='array'),
    ADD COLUMN subject_hashes jsonb NOT NULL DEFAULT '{}' CHECK (jsonb_typeof(subject_hashes)='object');

CREATE TABLE competence_hub.coach_public_roles (
    revision_id uuid NOT NULL,
    coach_id uuid NOT NULL,
    item_key text NOT NULL CHECK (item_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    ordering integer NOT NULL CHECK (ordering BETWEEN 0 AND 1000),
    code text NOT NULL CHECK (code ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    display_label text NOT NULL CHECK (length(btrim(display_label)) BETWEEN 1 AND 250),
    PRIMARY KEY (revision_id,item_key), UNIQUE(revision_id,ordering),
    FOREIGN KEY (revision_id,coach_id) REFERENCES competence_hub.coach_profile_revisions(id,coach_id)
);
CREATE TABLE competence_hub.coach_qualifications (
    revision_id uuid NOT NULL,
    coach_id uuid NOT NULL,
    item_key text NOT NULL CHECK (item_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    ordering integer NOT NULL CHECK (ordering BETWEEN 0 AND 1000),
    canonical_title text NOT NULL CHECK (length(btrim(canonical_title)) BETWEEN 1 AND 1000),
    public_display_label text CHECK (length(btrim(public_display_label)) BETWEEN 1 AND 1000),
    issuer text CHECK (length(issuer)<=250),
    qualification_type text CHECK (length(qualification_type)<=100),
    public boolean NOT NULL DEFAULT false,
    status text NOT NULL CHECK (status IN ('active','historical')),
    verification_state text NOT NULL DEFAULT 'unknown' CHECK (verification_state IN ('unknown','source_asserted','verified')),
    evidence_reference text CHECK (evidence_reference ~ '^[a-zA-Z0-9][a-zA-Z0-9:._/-]{0,199}$'),
    internal_note text CHECK (length(internal_note)<=1000),
    CHECK (NOT public OR public_display_label IS NOT NULL),
    PRIMARY KEY (revision_id,item_key), UNIQUE(revision_id,ordering),
    FOREIGN KEY (revision_id,coach_id) REFERENCES competence_hub.coach_profile_revisions(id,coach_id)
);
CREATE TABLE competence_hub.coach_offering_families (
    revision_id uuid NOT NULL,
    coach_id uuid NOT NULL,
    item_key text NOT NULL CHECK (item_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    ordering integer NOT NULL CHECK (ordering BETWEEN 0 AND 1000),
    title text NOT NULL CHECK (length(btrim(title)) BETWEEN 1 AND 250),
    description text CHECK (length(description)<=2000),
    active boolean NOT NULL DEFAULT true,
    metadata jsonb NOT NULL CHECK (jsonb_typeof(metadata)='object'),
    PRIMARY KEY (revision_id,item_key), UNIQUE(revision_id,ordering),
    FOREIGN KEY (revision_id,coach_id) REFERENCES competence_hub.coach_profile_revisions(id,coach_id)
);
ALTER TABLE competence_hub.coach_offerings
    ADD COLUMN item_key text CHECK (item_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    ADD COLUMN family_key text,
    ADD COLUMN metadata jsonb CHECK (metadata IS NULL OR jsonb_typeof(metadata)='object'),
    ADD UNIQUE(revision_id,item_key),
    ADD FOREIGN KEY(revision_id,family_key) REFERENCES competence_hub.coach_offering_families(revision_id,item_key);

CREATE TABLE competence_hub.coach_object_evidence (
    sequence bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    id uuid PRIMARY KEY,
    revision_id uuid NOT NULL,
    coach_id uuid NOT NULL,
    evidence_key text NOT NULL CHECK (evidence_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    subject_type text NOT NULL CHECK (subject_type IN ('profile','portrait','qualification','family','offering')),
    subject_key text NOT NULL CHECK (subject_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    subject_hash text NOT NULL CHECK (subject_hash ~ '^[a-f0-9]{64}$'),
    kind text NOT NULL CHECK (kind IN ('profile_content','portrait_asset','qualification','offering_content','publication','protected_source')),
    environment text NOT NULL CHECK (environment IN ('preview','production')),
    scope text NOT NULL CHECK (scope IN ('public_content','internal_verification','protected_source_content')),
    status text NOT NULL CHECK (status IN ('approved','unknown','rejected')),
    evidence_reference text CHECK (evidence_reference ~ '^[a-zA-Z0-9][a-zA-Z0-9:._/-]{0,199}$'),
    approved_by text CHECK (length(approved_by)<=200),
    approved_at timestamptz,
    approved_on date,
    internal_note text CHECK (length(internal_note)<=1000),
    recorded_by uuid NOT NULL REFERENCES competence_hub.portal_users(id),
    recorded_at timestamptz NOT NULL,
    UNIQUE(revision_id,evidence_key),
    FOREIGN KEY(revision_id,coach_id) REFERENCES competence_hub.coach_profile_revisions(id,coach_id),
    CHECK (status<>'approved' OR evidence_reference IS NOT NULL),
    CHECK (approved_at IS NULL OR approved_on IS NULL),
    CHECK ((kind='protected_source')=(scope='protected_source_content')),
    CHECK (scope<>'internal_verification' OR subject_type='qualification'),
    CHECK ((subject_type='profile' AND kind IN ('profile_content','publication'))
        OR (subject_type='portrait' AND kind='portrait_asset')
        OR (subject_type='qualification' AND kind='qualification')
        OR (subject_type IN ('offering','family') AND kind IN ('offering_content','protected_source')))
);
CREATE INDEX coach_evidence_revision_idx ON competence_hub.coach_object_evidence(revision_id,sequence);

CREATE FUNCTION competence_hub.guard_coach_target()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF NEW.target_version=0 AND (NEW.presentation IS NOT NULL OR NEW.boundaries<>'[]'::jsonb OR NEW.subject_hashes<>'{}'::jsonb
        OR EXISTS(SELECT 1 FROM competence_hub.coach_profile_revisions r WHERE r.coach_id=NEW.coach_id AND r.target_version=1))
    THEN RAISE EXCEPTION 'target downgrade or unversioned target data'; END IF;
    IF NEW.target_version=1 AND NEW.status='submitted' AND (
        NEW.subject_hashes->>'profile:profile' IS NULL
        OR EXISTS(SELECT 1 FROM competence_hub.coach_offerings o WHERE o.revision_id=NEW.id AND o.item_key IS NULL))
    THEN RAISE EXCEPTION 'complete target subjects required'; END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_target_guard BEFORE INSERT OR UPDATE ON competence_hub.coach_profile_revisions
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_target();

CREATE FUNCTION competence_hub.guard_coach_target_child()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF TG_TABLE_NAME='coach_offerings' THEN
        IF NEW.item_key IS NULL AND NEW.family_key IS NULL AND NEW.metadata IS NULL THEN RETURN NEW; END IF;
    END IF;
    PERFORM 1 FROM competence_hub.coach_profile_revisions WHERE id=NEW.revision_id AND target_version=1 FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'versioned rich target required'; END IF;
    RETURN NEW;
END;
$$;
DO $$ DECLARE t text; BEGIN
    FOREACH t IN ARRAY ARRAY['coach_public_roles','coach_qualifications','coach_offering_families'] LOOP
        EXECUTE format('CREATE TRIGGER freeze_revision_child BEFORE INSERT OR UPDATE OR DELETE ON competence_hub.%I FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_revision_child()',t);
        EXECUTE format('CREATE TRIGGER target_child_version BEFORE INSERT OR UPDATE ON competence_hub.%I FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_target_child()',t);
    END LOOP;
END $$;
CREATE TRIGGER target_child_version BEFORE INSERT OR UPDATE ON competence_hub.coach_offerings
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_target_child();

CREATE FUNCTION competence_hub.guard_coach_object_evidence()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
DECLARE hashes jsonb;
BEGIN
    SELECT subject_hashes INTO hashes FROM competence_hub.coach_profile_revisions
        WHERE id=NEW.revision_id AND coach_id=NEW.coach_id AND target_version=1 AND status='submitted' FOR UPDATE;
    IF NOT FOUND OR (hashes->>(NEW.subject_type||':'||NEW.subject_key)) IS DISTINCT FROM NEW.subject_hash
    THEN RAISE EXCEPTION 'exact submitted target subject required'; END IF;
    IF NEW.approved_at>NEW.recorded_at OR NEW.approved_on>(NEW.recorded_at AT TIME ZONE 'UTC')::date
    THEN RAISE EXCEPTION 'future historical approval forbidden'; END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_object_evidence_guard BEFORE INSERT ON competence_hub.coach_object_evidence
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_object_evidence();

CREATE FUNCTION competence_hub.coach_target_evidence_ready(revision uuid, env text)
RETURNS boolean LANGUAGE sql STABLE SECURITY INVOKER SET search_path=pg_catalog AS $$
    SELECT r.target_version=0 OR NOT EXISTS (
        SELECT 1 FROM (
            SELECT 'profile' AS subject_type,'profile' AS subject_key,'profile_content' AS kind
            UNION ALL SELECT 'profile','profile','publication'
            UNION ALL SELECT 'portrait','portrait','portrait_asset' FROM competence_hub.coach_assets WHERE revision_id=revision AND active
            UNION ALL SELECT 'qualification',item_key,'qualification' FROM competence_hub.coach_qualifications WHERE revision_id=revision AND public AND status='active'
            UNION ALL SELECT 'family',f.item_key,'offering_content' FROM competence_hub.coach_offering_families f
                WHERE f.revision_id=revision AND f.active AND EXISTS(SELECT 1 FROM competence_hub.coach_offerings o WHERE o.revision_id=revision AND o.family_key=f.item_key AND o.active)
            UNION ALL SELECT 'offering',o.item_key,'offering_content' FROM competence_hub.coach_offerings o WHERE o.revision_id=revision AND o.active
                AND (o.family_key IS NULL OR EXISTS(SELECT 1 FROM competence_hub.coach_offering_families f WHERE f.revision_id=revision AND f.item_key=o.family_key AND f.active))
        ) required
        LEFT JOIN LATERAL (
            SELECT e.status,e.subject_hash FROM competence_hub.coach_object_evidence e WHERE e.revision_id=revision
                AND e.subject_type=required.subject_type AND e.subject_key=required.subject_key AND e.kind=required.kind
                AND e.environment=env AND e.scope='public_content' ORDER BY e.sequence DESC LIMIT 1
        ) latest ON true
        WHERE latest.status IS DISTINCT FROM 'approved' OR latest.subject_hash IS DISTINCT FROM r.subject_hashes->>(required.subject_type||':'||required.subject_key)
    ) FROM competence_hub.coach_profile_revisions r WHERE r.id=revision;
$$;
CREATE FUNCTION competence_hub.guard_coach_target_publication()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF NEW.state='published' AND NOT competence_hub.coach_target_evidence_ready(NEW.revision_id,NEW.environment)
    THEN RAISE EXCEPTION 'object environment consent incomplete'; END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_target_publication_guard BEFORE INSERT OR UPDATE ON competence_hub.coach_publications
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_target_publication();

-- Revocation is append-only and fail-closed even for direct SQL evidence inserts.
CREATE FUNCTION competence_hub.withdraw_coach_target_on_evidence()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    UPDATE competence_hub.coach_publications SET state='withdrawn',actor_id=NEW.recorded_by,occurred_at=NEW.recorded_at
    WHERE revision_id=NEW.revision_id AND environment=NEW.environment AND state='published'
        AND NOT competence_hub.coach_target_evidence_ready(NEW.revision_id,NEW.environment);
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_target_evidence_withdraw AFTER INSERT ON competence_hub.coach_object_evidence
    FOR EACH ROW EXECUTE FUNCTION competence_hub.withdraw_coach_target_on_evidence();

REVOKE UPDATE,DELETE ON competence_hub.coach_object_evidence FROM competence_hub_app;
ALTER TABLE competence_hub.coach_import_items DROP CONSTRAINT coach_import_items_kind_check;
ALTER TABLE competence_hub.coach_import_items ADD CONSTRAINT coach_import_items_kind_check
    CHECK (kind IN ('topic','competency','offering','asset','role','qualification','boundary','target_group',
        'family','variant','presentation','presentation_section','presentation_link','object_evidence'));
INSERT INTO competence_hub.schema_migrations(version,description) VALUES ('0009','Lossless Coach target and exact object evidence');
COMMENT ON TABLE competence_hub.coach_qualifications IS 'Admin-only canonical qualifications; public labels require explicit visibility and revision consent.';
COMMENT ON TABLE competence_hub.coach_object_evidence IS 'Append-only object/hash/environment consent; NULL historical values remain unknown. Never public.';
COMMIT;
