\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

ALTER TABLE competence_hub.coaches
    ADD COLUMN public_profile_path text;

ALTER TABLE competence_hub.coaches
    ADD CONSTRAINT coaches_public_profile_path_ck CHECK (
        public_profile_path IS NULL
        OR (
            char_length(public_profile_path) <= 200
            AND public_profile_path ~ '^/coaches/[a-z0-9]+(-[a-z0-9]+)*/$'
        )
    );

CREATE UNIQUE INDEX coaches_public_profile_path_uq
    ON competence_hub.coaches (public_profile_path)
    WHERE public_profile_path IS NOT NULL;

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0006', 'Explicit public Coach profile path mapping');

COMMENT ON COLUMN competence_hub.coaches.public_profile_path
    IS 'Optional explicit mapping to /coaches/<slug>/; never derive from a name.';

COMMIT;
