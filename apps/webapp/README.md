# Webapp

Reserved workspace for the later Competence Hub administration application.

## Status

FastAPI plus PostgreSQL on the existing VPS is the accepted direction in ADR
0002. PostgreSQL 16 staging is installed and empty; no backend runtime or real
data exists yet. Keep webapp decisions separate from the public Astro website.
The website must never connect directly to the database.

`database/bootstrap-staging.sql` reproducibly creates the secret-free role,
database and schema structure. Login passwords are set only through interactive
`psql` prompts and never belong in this script.

## Local Configuration

- `.env.example` contains placeholders only and may be committed.
- Copy it to `.env` only when a backend implementation starts.
- `.env` is ignored by Git and must contain no shared or production credentials.
- Do not store SSH passwords in `.env`; use an SSH key/agent or an interactive
  password prompt.
- Do not copy the existing IONOS MySQL credentials into this workspace. That
  database is not reachable by the VPS backend.

See `docs/architecture/server-database-bootstrap.md` and
`docs/architecture/initial-data-model.md` before server or database changes.
