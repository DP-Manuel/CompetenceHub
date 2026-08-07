# ADR 0002 - PostgreSQL For The Competence Hub Backend

Date: 2026-08-06

## Status

Accepted by Manuel on 2026-08-06. Implemented for isolated staging on
2026-08-07 with PostgreSQL 16.14, localhost-only binding, separated roles and a
successful synthetic local dump/restore rehearsal. Productive data is not yet
approved.

## Context

The public Astro website will be hosted as static files on the IONOS webspace.
IONOS has already provisioned a MySQL database and Manuel holds its credentials,
but EDV confirmed that this database is reachable only from the IONOS webspace.
It cannot be used directly by a backend running on the separate VPS.

The approved read-only VPS inventory found no active database. Ubuntu 24.04 LTS
offers PostgreSQL 16 and MariaDB 10.11 from its package repositories. The VPS
has sufficient capacity for a small isolated database and backend pilot.

ADR 0001 already preferred PostgreSQL when the application is hosted on the
existing VPS. The initial data model is relational and requires transactions,
constraints, many-to-many relations, audit events and later controlled
reporting.

## Decision

Use a dedicated PostgreSQL database on the VPS for the future Competence Hub
backend, subject to the operational gates below.

- PostgreSQL listens only on localhost or a private Unix socket.
- The database is not reachable from the public internet.
- Competence Hub receives a separate database, owner/migration role and
  restricted application role.
- The backend accesses the database; the public Astro website never connects
  directly.
- Schema migrations are versioned with the backend, with Alembic as the
  proposed migration tool for a FastAPI/SQLAlchemy implementation.
- The existing IONOS MySQL database is not used for this VPS architecture and
  its credentials are not copied into the repository or VPS configuration.

## Rationale

- It follows the preference already recorded in ADR 0001.
- PostgreSQL fits the relational model, transactional workflows, constraints,
  auditability and later reporting without requiring a new external provider.
- Ubuntu provides security-maintained packages and the server already operates
  a Python/FastAPI/systemd pattern.
- A local database avoids public database exposure and the unreachable IONOS
  boundary.
- The decision remains reversible before productive data is stored because the
  first implementation uses migrations and synthetic test data only.

## Alternatives

### MariaDB/MySQL on the VPS

Technically viable and closer to the original placeholder model. It offers no
meaningful operational advantage on the current VPS, because no database engine
is installed and the IONOS database cannot be reused from there.

### PHP Backend Plus IONOS MySQL

Would use the existing IONOS database, but introduces a second backend stack
and constrains the longer-term authenticated application. Rejected for the
current architecture unless the VPS direction is later abandoned.

### Direct External Access To IONOS MySQL

Not viable under the confirmed IONOS network boundary.

## Implementation Gates

1. Completed: apply pending VPS system/kernel updates and the required reboot.
2. Completed: verify firewall and Fail2ban rules with administrative access.
3. Open before productive data: select an encrypted off-server backup target
   and define retention.
4. Partially complete: local synthetic restore rehearsal passed. Backup
   monitoring and restore from the external copy remain open.
5. Open before backend runtime: create a dedicated Competence-Hub system user
   and secret storage path.
6. Active boundary: keep the first environment staging-only with synthetic test
   data.

## Consequences

- The IONOS database can remain unused or be removed later through IONOS after
  confirming it contains no required data.
- PostgreSQL patching, monitoring, backup and restore become part of Manuel's
  server responsibilities.
- Production deployments require coordinated schema migration and rollback
  planning.
- The initial data model and `.env.example` use PostgreSQL-oriented placeholders.

## Follow-Up

- Verify the scheduled Chatbot crawl after the completed change window.
- Create and restore an encrypted off-server copy before real data.
- Define authentication and authorization before real records.
- Turn `initial-data-model.md` into an implementation schema after the first
  backend slice is confirmed.
- Create the isolated backend system user, runtime and secret path in a separate
  approved change.
