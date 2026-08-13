# Webapp

Reserved workspace for the later Competence Hub administration application.

## Status

FastAPI plus PostgreSQL on the existing VPS is the accepted direction in ADR
0002. PostgreSQL 16 staging is installed and contains the empty portal-core
schema; no backend runtime or real data exists yet. Keep webapp decisions
separate from the public Astro website.
The website must never connect directly to the database.

`database/bootstrap-staging.sql` reproducibly creates the secret-free role,
database and schema structure. Login passwords are set only through interactive
`psql` prompts and never belong in this script.

The Product-Owner workbook from 2026-08-13 has been translated into the first
portal-core migration and a rollback-only synthetic smoke test. See
`database/README.md`. Migration `0001` was applied and verified on the VPS
staging database on 2026-08-13; auth and the final request workflow remain
gated decisions.

The internal authentication architecture was approved in ADR 0003 on
2026-08-13. Its testable requirements are documented in
`../../docs/requirements/internal-authentication-v0.1.md`. The current local
slice contains security primitives, honest health/readiness endpoints,
migration `0002` and synthetic tests. Migration `0002` is applied and verified
on the empty VPS staging database. The slice does not contain login routes, a
database repository, real accounts or a deployable service configuration.

## Local Verification

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest
```

The default `/health/ready` response is deliberately `503` until a real
database readiness adapter is connected. This prevents the scaffold from
pretending to be operational.

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
