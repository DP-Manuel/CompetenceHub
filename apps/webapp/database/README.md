# Competence Hub Database

## Status

- PostgreSQL 16 staging exists on the VPS and is localhost-only.
- `bootstrap-staging.sql` creates database roles, database and schema without
  credentials.
- `migrations/0001_portal_core.sql` is the first portal-core migration.
- Migration `0001` was applied to the empty VPS staging database on
  2026-08-13 and verified with the rollback-only synthetic smoke test.
- Migration `0002_internal_auth.sql` was applied to VPS staging on 2026-08-13
  and verified with its rollback-only synthetic smoke test.
- Migration `0003_totp_replay_and_recovery_keys.sql` is applied to the empty
  Staging database. Its protected pre-dump, schema columns and rollback-only
  synthetic smoke are verified. The complete synthetic MFA integration passed
  12/12 paths. The 74-KiB post-dump is catalog-readable and protected with mode
  `0600`. The independent zero-residue check passed, migrations `0001`-`0003`
  remain registered, all four co-hosted services are active and PostgreSQL
  remains bound only to loopback.
- Migration `0004_auth_token_outbox_and_idempotency.sql` was applied to
  isolated Staging on 2026-08-14 after separate approval. Its rollback-only
  smoke passed, the complete synthetic harness passed 13/13 paths and all
  eleven checked data areas remained empty. Protected 74-KiB pre- and 86-KiB
  post-dumps are catalog-readable, owned by `postgres` and mode `0600`.
- The migrated schema contains no business, company or personal data.
- Only synthetic test data is allowed while the external-backup and privacy
  gates remain open.

## Migration 0001

The migration implements the confirmed B2B-first core:

- portal users and multiple roles
- companies and company contacts
- coaches, topics and services
- coaching requests with topic/service links
- append-oriented audit events

It intentionally does not implement authentication, final request transitions,
orders, appointments, documents, feedback, reporting, B2C or participant data.

## Migration 0002

The migration adds persistence foundations for internal authentication:

- Argon2id password credentials
- short-lived login/MFA challenges
- server-side sessions
- invitation and password-reset token digests
- encrypted TOTP credentials and recovery-code HMAC digests
- HMAC-pseudonymized rate-limit buckets

It stores no raw tokens, recovery codes, TOTP secrets, email/IP bucket keys or
real accounts. The approved staging run used protected pre/post dumps and
`verification/0002_internal_auth_smoke.sql`. Both dumps are owned by `postgres`
with mode `0600`; the post-dump catalog is readable.

## Migration 0004

The applied migration adds:

- HMAC-pseudonymized Admin invitation idempotency records
- a unique outbox record per invitation/reset token
- AES-256-GCM encrypted token payloads with external key versions
- pending/processing/delivered/failed/canceled state constraints
- worker claim leases, bounded-attempt metadata and cleanup indexes
- terminal-state minimization that removes recipient address and payload

It does not configure a worker, mail adapter, provider, sender domain, retention
period or runtime secret. The Staging proof completed protected pre/post dumps,
rollback-only smoke, synthetic idempotency/delivery/failure/cleanup tests,
zero-residue verification and unchanged service/network health.

## Safe Staging Procedure

1. Review the migration and current database state.
2. Create a protected pre-migration dump.
3. Transfer the SQL file to a non-public temporary path on the VPS.
4. Set each temporary file to `0600` and make its intended execution account
   the owner (`manuel` for password-prompted migrator execution, `postgres` for
   an administrative rollback-only smoke).
5. Run it as `competence_hub_migrator` with `ON_ERROR_STOP`.
6. Run the matching verification SQL as an administrative database
   session. The test uses synthetic data and ends with `ROLLBACK`.
7. Verify Chatbot health and that port 5432 remains localhost-only.
8. Record the migration and verification result in `PROJECT_LOG.md`.

The latest 2026-08-14 staging run completed all eight steps. It produced protected
pre- and post-migration dumps on the VPS. The post-migration dump is readable,
but it is not a substitute for the still-open encrypted off-server backup and
restore gate. Both dump files are owned by `postgres` with mode `0600`; their
backup directory is owned by `postgres` with mode `0700`.

Do not put passwords in command arguments, scripts, Git or shell history. Do
not apply this migration to a database containing real data without a separate
release plan and verified external restore point.

## Prepared Backup And Restore Operations

The repository now contains secret-free backup, monitor, restore-check and
systemd examples under `deploy/`. They encrypt database and globals payloads to
an approved public GPG fingerprint, keep provisional 30-daily/12-monthly restore
points, detect stale/incomplete/plaintext backup state and restore only into a
temporary local check database. The complete operating and gate procedure is
documented in `docs/architecture/postgresql-backup-restore-runbook.md`.

These files are prepared but not installed or enabled. Real data remains
prohibited until an encrypted external copy is restored successfully and
retention, active alerting and recovery ownership are approved.
