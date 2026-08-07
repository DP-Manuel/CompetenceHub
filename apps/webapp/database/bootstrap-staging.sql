\set ON_ERROR_STOP on

-- This script contains no credentials. Set login passwords interactively in
-- psql after the bootstrap has completed.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'competence_hub_owner') THEN
        CREATE ROLE competence_hub_owner
            NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'competence_hub_migrator') THEN
        CREATE ROLE competence_hub_migrator
            LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'competence_hub_app') THEN
        CREATE ROLE competence_hub_app
            LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
END
$$;

GRANT competence_hub_owner TO competence_hub_migrator;

SELECT format(
    'CREATE DATABASE %I OWNER %I ENCODING %L TEMPLATE template0',
    'competence_hub_staging',
    'competence_hub_owner',
    'UTF8'
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'competence_hub_staging'
) \gexec

REVOKE ALL ON DATABASE competence_hub_staging FROM PUBLIC;
GRANT CONNECT ON DATABASE competence_hub_staging TO competence_hub_migrator;
GRANT CONNECT ON DATABASE competence_hub_staging TO competence_hub_app;

ALTER ROLE competence_hub_migrator IN DATABASE competence_hub_staging
    SET search_path TO competence_hub, public;
ALTER ROLE competence_hub_app IN DATABASE competence_hub_staging
    SET search_path TO competence_hub, public;

\connect competence_hub_staging

REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA IF NOT EXISTS competence_hub AUTHORIZATION competence_hub_owner;
ALTER SCHEMA competence_hub OWNER TO competence_hub_owner;

GRANT USAGE ON SCHEMA competence_hub TO competence_hub_app;

-- Migrations must SET ROLE competence_hub_owner before creating objects so
-- these least-privilege defaults apply to the runtime role.
ALTER DEFAULT PRIVILEGES FOR ROLE competence_hub_owner IN SCHEMA competence_hub
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO competence_hub_app;
ALTER DEFAULT PRIVILEGES FOR ROLE competence_hub_owner IN SCHEMA competence_hub
    GRANT USAGE, SELECT ON SEQUENCES TO competence_hub_app;
ALTER DEFAULT PRIVILEGES FOR ROLE competence_hub_owner IN SCHEMA competence_hub
    REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE competence_hub_owner IN SCHEMA competence_hub
    GRANT EXECUTE ON FUNCTIONS TO competence_hub_app;
