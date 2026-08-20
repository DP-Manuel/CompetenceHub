# Webapp

Reserved workspace for the later Competence Hub administration application.

## Status

FastAPI plus PostgreSQL on the existing VPS is the accepted direction in ADR
0002. PostgreSQL 16 staging is installed and contains the empty portal-core
schema; no backend service is deployed and no real data exists. Keep webapp
decisions separate from the public Astro website.
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
  migration `0002`, PostgreSQL login/session repositories, first-factor login
  with account/network-peer rate limiting and the protected current-session/
  logout endpoints. Migration `0002` is applied and verified on the empty VPS
  staging database.

The default application remains deny-by-default: no repository or allowed
browser origin is wired into `app`, and readiness stays false. The runtime
factory validates external process configuration, creates a dedicated async
  PostgreSQL engine and auth repositories, reports database-backed readiness and
  disposes the engine on shutdown. No real account, secret file or deployable
  service configuration exists. Repository and API tests use
  synthetic data only. The session repository/API and runtime readiness passed
seven opt-in integration tests against isolated Staging on 2026-08-14; cleanup
left no users, sessions or audit rows and all co-hosted services remained active.
The focused review in
`../../docs/architecture/session-runtime-security-review-2026-08-14.md` found
no open high or critical issue in this slice. Runtime settings now validate on
every construction path, require the restricted app role and suppress token and
  SQL-parameter representations. The local first-factor slice adds generic
  failures, Argon2id timing parity, HMAC-pseudonymized account/network-peer
  buckets, progressive blocking and five-minute pre-auth challenges. The
  combined Auth harness passed 11/11 paths against isolated PostgreSQL Staging;
  cleanup left all checked Auth tables empty and co-hosted services active. The
  focused review is documented in
  `../../docs/architecture/first-factor-login-security-review-2026-08-14.md`.
  The complete local MFA slice adds versioned AES-GCM TOTP storage, standard
  TOTP enrollment/verification, HMAC-only recovery codes, atomic challenge/code
  consumption and full-session rotation. Its full local suite passes 148 tests
  with 12 opt-in Staging tests skipped when no tunnel is present. ADR 0004 is
  accepted, migration `0003` is applied and rollback-smoke-tested on isolated
  Staging, and the synthetic MFA harness passed all 12 paths in 134.98 seconds.
  No persistent MFA runtime secrets or real accounts exist. See
  `../../docs/architecture/mfa-runtime-security-review-2026-08-14.md`.

## Local Verification

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m compileall -q src tests
.\.venv\Scripts\python.exe -m pip check
```

The default `/health/ready` response is deliberately `503`. The runtime factory
returns ready only after a successful minimal PostgreSQL query. This prevents
the scaffold from pretending to be operational.

## Runtime Configuration

The runtime reads only process environment variables. It does not load a
secret file:

- `COMPETENCE_HUB_DATABASE_URL`: SQLAlchemy `postgresql+asyncpg` URL using a
  loopback host, dedicated app role and external password.
- `COMPETENCE_HUB_ALLOWED_ORIGIN`: exact HTTPS browser origin without wildcard,
  path or credentials.
- `COMPETENCE_HUB_SESSION_IDLE_MINUTES`: optional integer from 1 through 60;
  default is 30.
- `COMPETENCE_HUB_READINESS_TIMEOUT_SECONDS`: optional integer from 1 through
  30; default is 5. Longer values are intended only for controlled diagnostic
  paths such as an SSH-tunneled Staging check.
- `COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY`: required standard-base64 value decoding
  to at least 32 random bytes. It pseudonymizes rate-limit identifiers and must
  be supplied through the approved external service configuration, never Git.
- `COMPETENCE_HUB_TOTP_KEYRING`: required JSON object mapping non-secret key
  version labels to standard-base64 AES-256 keys. Old keys remain present only
  while credentials encrypted with them still exist.
- `COMPETENCE_HUB_TOTP_ACTIVE_KEY_VERSION`: required version label from the
  TOTP key ring; all new TOTP secrets use this version.
- `COMPETENCE_HUB_RECOVERY_HMAC_KEYRING`: required JSON object mapping
  non-secret version labels to standard-base64 HMAC keys with at least 32
  random bytes each. It is separate from TOTP and rate-limit keys.
- `COMPETENCE_HUB_RECOVERY_HMAC_ACTIVE_KEY_VERSION`: required version label
  from that key ring; newly generated recovery codes use this version.

The opt-in Staging harness prompts only for the two database passwords and
keeps them in the current process:

```powershell
.\scripts\run-staging-session-integration.ps1 -LocalPort 55432
```

## Initial Admin CLI

The local package exposes `competence-hub-admin create-initial-admin`. It has no
default credentials, rejects non-interactive execution and reads the password
twice through a hidden terminal prompt. It requires external process values for
`COMPETENCE_HUB_DATABASE_URL` and
`COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH`. The latter must be an
absolute path to a non-empty ASCII file containing one SHA-256 password
fingerprint per line. No fingerprint source is committed to this repository.

Implementation does not authorize execution. Creating a real privileged user
requires separate approval, a reviewed offline fingerprint source, protected
database backups and an immediate MFA-enrollment handoff. The local review is
documented in
`../../docs/architecture/initial-admin-cli-security-review-2026-08-14.md`.

## Invitation And Password Reset Lifecycle

The local account-lifecycle service now covers internal invitations, generic
password-reset requests, token acceptance, rate limiting, Argon2id password
replacement, MFA-enrollment challenge rotation and all-session revocation. The
public request/confirm/accept routes use strict bodies, exact Origin checks and
generic errors. Runtime wiring remains absent, so these routes fail closed.

No productive token delivery exists. The contracted Admin invitation route is
now implemented locally with MFA-session, fresh-auth, Admin-role, Origin, CSRF,
non-privileged-role and `Idempotency-Key` enforcement. Accepted ADR 0005 is
implemented through prepared migration `0004`, HMAC-only idempotency records,
an AES-256-GCM encrypted transactional outbox, leased worker claims, bounded
retries, terminal token revocation and explicit metadata cleanup cutoffs. Raw
tokens never appear in API responses or normal persistence. Runtime wiring is
still absent, so all account-lifecycle routes remain fail-closed by default.

No mail adapter, provider, sender domain, runtime key or worker service is
configured. Migration `0004` is applied and rollback-smoke-tested on isolated
Staging; the complete synthetic harness passed 13/13 paths in 156.91 seconds,
left all eleven checked data areas empty and produced protected catalog-readable
pre/post dumps. Selecting retention periods, wiring external keys and enabling
any worker or real delivery remain separate gates. See
`../../docs/architecture/auth-token-outbox-security-review-2026-08-14.md`.

Start the configured app through the factory only after supplying those values
through an approved local or service-manager mechanism:

```powershell
python -m uvicorn competence_hub_api.runtime:create_runtime_app_from_environment --factory
```

Do not store SSH credentials in application configuration. Do not copy the
existing IONOS MySQL credentials into this workspace; that database is not
reachable by the VPS backend.

See `docs/architecture/server-database-bootstrap.md` and
`docs/architecture/initial-data-model.md` before server or database changes.

## Company And Contact Pilot API

The first protected business slice is implemented locally under
`/api/v1/portal/companies`. Active `admin` and `internal` MFA sessions can
create a company with its first contact atomically, list/read company details,
add contacts and correct the bounded pilot fields. Mutations require exact
Origin plus session CSRF; all responses remain `no-store`, audit records omit
payload details and no delete endpoint exists.

The runtime factory wires this repository, but no persistent backend service,
portal UI, real user or real company data has been deployed. The company status
starts with the provisional internal value `prospect`; it is not a final
workflow vocabulary. The opt-in Staging harness now also covers real
PostgreSQL CRUD, audit and zero-residue cleanup. See
`../../docs/architecture/company-contact-api-contract-v0.1.md` and the focused
review in
`../../docs/architecture/company-contact-security-review-2026-08-20.md`.
