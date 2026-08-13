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

## Safe Staging Procedure

1. Review the migration and current database state.
2. Create a protected pre-migration dump.
3. Transfer the SQL file to a non-public temporary path on the VPS.
4. Run it as `competence_hub_migrator` with `ON_ERROR_STOP`.
5. Run `verification/0001_portal_core_smoke.sql` as an administrative database
   session. The test uses synthetic data and ends with `ROLLBACK`.
6. Verify Chatbot health and that port 5432 remains localhost-only.
7. Record the migration and verification result in `PROJECT_LOG.md`.

The 2026-08-13 staging run completed all seven steps. It produced protected
pre- and post-migration dumps on the VPS. The post-migration dump is readable,
but it is not a substitute for the still-open encrypted off-server backup and
restore gate. Both dump files are owned by `postgres` with mode `0600`; their
backup directory is owned by `postgres` with mode `0700`.

Do not put passwords in command arguments, scripts, Git or shell history. Do
not apply this migration to a database containing real data without a separate
release plan and verified external restore point.
