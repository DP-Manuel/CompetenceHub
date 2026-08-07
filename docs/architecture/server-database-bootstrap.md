# Server And Database Bootstrap

Last updated: 2026-08-07

## Goal

Assess the existing VPS as a possible home for a later authenticated Competence
Hub backend and an independent database without affecting the public Astro
website or the already running Donner + Partner chatbot.

## Current Boundary

- The approved read-only inventory was followed by a controlled maintenance
  and database-staging change on 2026-08-07.
- No credential document was opened.
- No deployment is approved.
- `apps/webapp/.env.example` contains placeholders only.
- The backend runtime and framework are not finally decided; a separate
  FastAPI/systemd service is the current operational recommendation.
- The IONOS shared webspace is confirmed as production hosting for static/PHP
  files. It cannot run a permanent Node.js or Python backend.
- The IONOS MySQL database is reachable only from its own webspace and therefore
  cannot serve a backend running on the separate VPS.
- The VPS already runs the Donner + Partner chatbot using FastAPI and systemd.
  It remained healthy through patching and reboot. PostgreSQL 16.14 now runs as
  a separate localhost-only staging database. Manuel owns operations; encrypted
  off-server backup and backend-runtime gates remain.

See `hosting-runtime-decision-2026-08-06.md` for options, recommendation and
decision gates.

The original read-only inventory is documented in
`vps-read-only-inventory-2026-08-06.md`. The executed change and remaining
production gates are documented in `postgresql-16-installation-runbook.md`.

## Access Rules

- Prefer an SSH key and local SSH agent.
- If password authentication is temporarily required, enter the password only in
  an interactive SSH prompt. Do not store it in ENV, shell history, docs, or Git.
- Never use database root credentials as application credentials.
- Do not expose port 3306 publicly. The future backend should reach the database
  locally or over a private network/SSH tunnel.
- Keep production and development credentials separate.

## First Server Session: Read-Only Inventory

After Manuel confirms the target environment, EDV/governance approval and
access method:

1. Confirm host identity, operating system, version, time, and hostname.
2. Inspect CPU, memory, disk capacity, and mounted filesystems.
3. Inspect active services and listening ports without changing them.
4. Check firewall status and pending operating-system updates.
5. Record existing chatbot services, reverse proxy, timers and resource usage.
6. Check whether a database engine is installed and record its version without
   opening application credentials or existing data.
7. Check available backup locations and current backup policy.
8. Stop and prepare a change plan before installing or reconfiguring anything.

## Database Bootstrap Sequence

1. Completed: follow ADR 0002 and install PostgreSQL 16 on the VPS.
2. Completed: define the current database as staging-only.
3. Completed: bind PostgreSQL to localhost and verify UFW/Fail2ban.
4. Completed: create a dedicated database, NOLOGIN owner, migrator and
   least-privilege application role with
   `apps/webapp/database/bootstrap-staging.sql`.
5. Completed: create a protected local dump and prove a restore with synthetic
   data in a separate database.
6. Next: apply versioned migrations from the future backend code.
7. Next: create and restore an encrypted off-server backup before real data.
8. Next: add health checks and failure logging without credentials or personal
   data.

## Remaining Decisions Before Productive Use

- Server purpose: development/staging or production.
- EDV/governance approval for co-hosting beside the production chatbot.
- Operating-system maintenance owner.
- Backup destination, encryption, retention, and restore owner.
- Final backend runtime and migration tool.
- Domain/TLS/reverse-proxy ownership.
- Authentication and first internal role model.
- Resource isolation and failure boundaries between chatbot and Competence Hub.

## Verification Gates

- SSH host fingerprint is verified through a trusted channel.
- Database port is not publicly reachable.
- App user cannot create users/databases or grant privileges.
- Migrations can run forward on an empty database.
- Backup restore succeeds in a separate test database.
- No `.env`, keys, dumps, or credentials are tracked by Git.
