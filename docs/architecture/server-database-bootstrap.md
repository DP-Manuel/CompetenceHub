# Server And Database Bootstrap

Last updated: 2026-07-16

## Goal

Prepare the blank server for a later authenticated Competence Hub backend and an
independent MySQL/MariaDB database without affecting the public Astro website.

## Current Boundary

- No server login or server change has been performed in this work block.
- No credential document was opened.
- No deployment is approved.
- `apps/webapp/.env.example` contains placeholders only.
- The backend runtime and framework are still undecided.

## Access Rules

- Prefer an SSH key and local SSH agent.
- If password authentication is temporarily required, enter the password only in
  an interactive SSH prompt. Do not store it in ENV, shell history, docs, or Git.
- Never use database root credentials as application credentials.
- Do not expose port 3306 publicly. The future backend should reach the database
  locally or over a private network/SSH tunnel.
- Keep production and development credentials separate.

## First Server Session: Read-Only Inventory

After Manuel confirms the target environment and access method:

1. Confirm host identity, operating system, version, time, and hostname.
2. Inspect CPU, memory, disk capacity, and mounted filesystems.
3. Inspect active services and listening ports without changing them.
4. Check firewall status and pending operating-system updates.
5. Check whether MySQL or MariaDB is installed and record its version.
6. Check available backup locations and current backup policy.
7. Stop and prepare a change plan before installing or reconfiguring anything.

## Database Bootstrap Sequence

1. Confirm MySQL versus MariaDB and supported version.
2. Define development/staging/production boundaries and backup target.
3. Install and harden the selected database only after approval.
4. Bind the database to localhost/private interfaces.
5. Create a dedicated database and migration owner.
6. Create a separate least-privilege application user.
7. Apply versioned migrations from the future backend repository code.
8. Create an encrypted backup and prove a restore before real data is stored.
9. Add health checks and failure logging without logging credentials or personal data.

## Required Decisions Before Changes

- Server purpose: development/staging or production.
- Operating-system maintenance owner.
- Database engine and version.
- Backup destination, encryption, retention, and restore owner.
- Final backend runtime and migration tool.
- Domain/TLS/reverse-proxy ownership.
- Authentication and first internal role model.

## Verification Gates

- SSH host fingerprint is verified through a trusted channel.
- Database port is not publicly reachable.
- App user cannot create users/databases or grant privileges.
- Migrations can run forward on an empty database.
- Backup restore succeeds in a separate test database.
- No `.env`, keys, dumps, or credentials are tracked by Git.
