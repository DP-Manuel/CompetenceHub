\set ON_ERROR_STOP on
BEGIN;
SET LOCAL ROLE competence_hub_owner;

CREATE TABLE competence_hub.coach_import_sources (
    source_system text NOT NULL CHECK (source_system ~ '^[a-z0-9][a-z0-9_-]{0,79}$'),
    source_key text NOT NULL CHECK (source_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    source_ref text NOT NULL CHECK (source_ref ~ '^[a-zA-Z0-9][a-zA-Z0-9:._/-]{0,199}$'),
    coach_id uuid NOT NULL UNIQUE REFERENCES competence_hub.coaches(id),
    profile_path text UNIQUE CHECK (profile_path IS NULL OR (length(profile_path)<=200 AND profile_path ~ '^/coaches/[a-z0-9]+(-[a-z0-9]+)*/$')),
    source_content_hash text NOT NULL CHECK (source_content_hash ~ '^[a-f0-9]{64}$'),
    profile_content_hash text NOT NULL CHECK (profile_content_hash ~ '^[a-f0-9]{64}$'),
    mapping_contract_hash text NOT NULL CHECK (mapping_contract_hash ~ '^[a-f0-9]{64}$'),
    publication_intent_hash text NOT NULL CHECK (publication_intent_hash ~ '^[a-f0-9]{64}$'),
    last_revision_id uuid NOT NULL,
    last_registry_version integer NOT NULL CHECK (last_registry_version>0),
    PRIMARY KEY(source_system,source_key),
    UNIQUE(source_system,source_key,coach_id),
    FOREIGN KEY(last_revision_id,coach_id) REFERENCES competence_hub.coach_profile_revisions(id,coach_id)
);
CREATE TABLE competence_hub.coach_import_items (
    source_system text NOT NULL,
    source_key text NOT NULL,
    kind text NOT NULL CHECK (kind IN ('topic','competency','offering','asset','role','qualification','boundary','target_group')),
    item_key text NOT NULL CHECK (item_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    logical_id uuid NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    value_hash text NOT NULL CHECK (value_hash ~ '^[a-f0-9]{64}$'),
    PRIMARY KEY(source_system,source_key,kind,item_key),
    FOREIGN KEY(source_system,source_key) REFERENCES competence_hub.coach_import_sources(source_system,source_key)
);
CREATE TABLE competence_hub.coach_import_evidence (
    source_system text NOT NULL,
    source_key text NOT NULL,
    evidence_key text NOT NULL CHECK (evidence_key ~ '^[a-z0-9][a-z0-9/_-]{0,119}$'),
    coach_id uuid NOT NULL,
    revision_id uuid NOT NULL,
    kind text NOT NULL CHECK (kind IN ('content_review','person_consent','preview','production')),
    environment text CHECK (environment IN ('preview','production')),
    evidence_source text NOT NULL CHECK (length(evidence_source) BETWEEN 1 AND 200),
    historical_at timestamptz,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(source_system,source_key,evidence_key),
    UNIQUE(revision_id,kind),
    CHECK ((kind IN ('content_review','person_consent') AND environment IS NULL)
        OR (kind IN ('preview','production') AND environment IS NOT NULL AND kind=environment)),
    FOREIGN KEY(source_system,source_key,coach_id) REFERENCES competence_hub.coach_import_sources(source_system,source_key,coach_id),
    FOREIGN KEY(revision_id,coach_id) REFERENCES competence_hub.coach_profile_revisions(id,coach_id)
);

CREATE FUNCTION competence_hub.guard_coach_import_source()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF TG_OP='UPDATE' AND (OLD.source_system<>NEW.source_system OR OLD.source_key<>NEW.source_key
        OR OLD.coach_id<>NEW.coach_id OR OLD.profile_path IS DISTINCT FROM NEW.profile_path) THEN
        RAISE EXCEPTION 'immutable import identity';
    END IF;
    IF NEW.profile_path IS NOT NULL THEN
        PERFORM pg_advisory_xact_lock(hashtextextended('coach-import-path:' || NEW.profile_path,0));
        IF EXISTS(SELECT 1 FROM competence_hub.coach_profile_revisions WHERE profile_path=NEW.profile_path AND coach_id<>NEW.coach_id) THEN
            RAISE EXCEPTION 'import path already assigned';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_import_identity_guard BEFORE INSERT OR UPDATE ON competence_hub.coach_import_sources
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_import_source();

CREATE FUNCTION competence_hub.guard_coach_import_item()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF OLD.source_system<>NEW.source_system OR OLD.source_key<>NEW.source_key
        OR OLD.kind<>NEW.kind OR OLD.item_key<>NEW.item_key OR OLD.logical_id<>NEW.logical_id THEN
        RAISE EXCEPTION 'immutable import item identity';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_import_item_identity_guard BEFORE UPDATE ON competence_hub.coach_import_items
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_coach_import_item();

CREATE FUNCTION competence_hub.guard_imported_coach_path()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
BEGIN
    IF NEW.profile_path IS NOT NULL THEN
        PERFORM pg_advisory_xact_lock(hashtextextended('coach-import-path:' || NEW.profile_path,0));
        IF EXISTS(SELECT 1 FROM competence_hub.coach_import_sources WHERE profile_path=NEW.profile_path AND coach_id<>NEW.coach_id) THEN
            RAISE EXCEPTION 'import path already assigned';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER coach_import_path_guard BEFORE INSERT OR UPDATE OF profile_path ON competence_hub.coach_profile_revisions
    FOR EACH ROW EXECUTE FUNCTION competence_hub.guard_imported_coach_path();

REVOKE DELETE ON competence_hub.coach_import_sources,competence_hub.coach_import_items FROM competence_hub_app;
REVOKE UPDATE,DELETE ON competence_hub.coach_import_evidence FROM competence_hub_app;
INSERT INTO competence_hub.schema_migrations(version,description) VALUES ('0008','Controlled Coach import identity item ledger and historical evidence');
COMMENT ON TABLE competence_hub.coach_import_sources IS 'Technical source binding and hashes, not another Coach entity or implicit publication consent.';
COMMENT ON TABLE competence_hub.coach_import_items IS 'Import source item identity; logical item count is distinct from immutable revision snapshot rows.';
COMMENT ON TABLE competence_hub.coach_import_evidence IS 'Historical date may be unknown; recorded_at is not a historical approval date. No source document payloads.';
COMMIT;
