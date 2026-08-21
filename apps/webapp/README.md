# Webapp

Workspace for the protected Competence Hub administration pilot.

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
browser origin is wired into `app`, and readiness stays false. The configured
runtime factory validates external process configuration, creates a dedicated
async PostgreSQL engine and auth repositories, reports database-backed readiness
and disposes the engine on shutdown. No real account, secret file or deployable
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
- `COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY`: separate standard-base64 HMAC key with
  at least 32 random bytes for invitation request identities.
- `COMPETENCE_HUB_OUTBOX_KEYRING`: JSON object of versioned standard-base64
  AES-256 keys for invitation/reset tokens held briefly in the outbox.
- `COMPETENCE_HUB_OUTBOX_ACTIVE_KEY_VERSION`: configured outbox key version for
  newly queued tokens.
- `COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH`: absolute path to the
  protected, non-empty SHA-256 fingerprint source used by password changes.
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
generic errors. The configured runtime now wires the PostgreSQL lifecycle
repository, password policy and encrypted outbox; the unconfigured default app
continues to fail closed.

No productive token delivery exists. The contracted Admin invitation route is
now implemented locally with MFA-session, fresh-auth, Admin-role, Origin, CSRF,
non-privileged-role and `Idempotency-Key` enforcement. Accepted ADR 0005 is
implemented through prepared migration `0004`, HMAC-only idempotency records,
an AES-256-GCM encrypted transactional outbox, leased worker claims, bounded
retries, terminal token revocation and explicit metadata cleanup cutoffs. Raw
tokens never appear in API responses or normal persistence.

The local provider-neutral SMTP adapter, one-shot worker entry point and
secret-free systemd service/timer examples are implemented. They require an
approved SMTP contract and every external setting below, otherwise startup
fails closed. No real mail server, sender, runtime key or worker service is
configured. Migration `0004` is applied and rollback-smoke-tested on isolated
Staging; the complete synthetic harness passed 13/13 paths in 156.91 seconds,
left all eleven checked data areas empty and produced protected catalog-readable
pre/post dumps. Selecting retention periods, wiring external keys and enabling
any worker or real delivery remain separate gates. See
`../../docs/architecture/auth-token-outbox-security-review-2026-08-14.md`.

The worker additionally requires:

- `COMPETENCE_HUB_ACCOUNT_ACTION_BASE_URL`: exact HTTPS Portal URL ending in
  `/portal/` on the exact `COMPETENCE_HUB_ALLOWED_ORIGIN`; action tokens are
  appended after `#` and removed from the browser address immediately.
- `COMPETENCE_HUB_SMTP_HOST`, `COMPETENCE_HUB_SMTP_PORT` and
  `COMPETENCE_HUB_SMTP_TLS_MODE`: approved SMTP endpoint using `starttls` or
  implicit TLS; plaintext SMTP is rejected.
- `COMPETENCE_HUB_SMTP_USERNAME` and `COMPETENCE_HUB_SMTP_PASSWORD`: external
  service credentials, never repository values.
- `COMPETENCE_HUB_SMTP_FROM`: authorized system sender.
- `COMPETENCE_HUB_SMTP_REPLY_TO`: monitored mailbox for user questions.

The Portal now contains password-reset request/confirmation, invitation
acceptance followed by MFA enrollment, and an Admin-only internal invitation
form. It does not expose a token in query strings or browser storage.

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
real user or real company data has been deployed. The company status
starts with the provisional internal value `prospect`; it is not a final
workflow vocabulary. The opt-in Staging harness now also covers real
PostgreSQL CRUD, audit and zero-residue cleanup. See
`../../docs/architecture/company-contact-api-contract-v0.1.md` and the focused
review in
`../../docs/architecture/company-contact-security-review-2026-08-20.md`.

## Same-Origin Pilot Portal

ADR 0006 and the 2026-08-28 pilot cutline are accepted for local synthetic
implementation. FastAPI now packages a build-free HTML/CSS/JavaScript portal
under `/portal/`; `/` redirects there. The same origin serves the existing
login/MFA/session APIs and the protected company/contact pilot API. The client
keeps challenge and session CSRF material only in page memory and never uses
browser storage. After a page reload, `POST /api/v1/auth/session/csrf` rotates
the active session's CSRF digest and returns the new plaintext once in the
response header.

The portal covers login, TOTP/recovery, first MFA enrollment, session restore,
logout, company search/detail/create/correction and contact create/correction.
It uses local assets only, a restrictive CSP, `no-store`, explicit empty/error
states, duplicate-submit guards, semantic labels, visible focus and responsive
layouts. The complete local suite passes 248 tests, with 14 additional opt-in
Staging tests skipped when no tunnel is present. On 2026-08-20 all 14
opt-in paths passed against isolated PostgreSQL Staging in 171.95 seconds,
including session CSRF rotation; cleanup left users, sessions, companies,
contacts and audit events at zero and all four co-hosted services active. No
DNS, Nginx, systemd, account, real-data or deployment action is authorized by
this implementation. See
`../../docs/architecture/pilot-portal-ui-security-accessibility-review-2026-08-20.md`.

### Local Browser Acceptance

The opt-in browser harness runs the production portal shell against a synthetic,
volatile in-memory backend over loopback HTTPS. It does not read environment
files, connect to PostgreSQL, persist records or use real identities:

```powershell
cd apps\webapp
.\scripts\run-browser-acceptance.ps1
```

The runner creates a one-day self-signed loopback certificate and an isolated
temporary Edge profile, opens `https://127.0.0.1:8443/portal/`, and prints only
public `example.invalid` test identities. The certificate exception applies to
that isolated Edge window; do not use it for other websites. Close the window
before confirming the prompt. The runner then stops the local fixture and
removes its temporary certificate, profile and logs.

Use another unused port when necessary:

```powershell
.\scripts\run-browser-acceptance.ps1 -Port 8444
```

The durable desktop, 390-pixel, keyboard, zoom and reduced-motion checklist is
`../../docs/architecture/pilot-portal-browser-acceptance-checklist-2026-08-20.md`.
This harness is acceptance tooling only and must never be wired into a deployed
runtime or used with real company or personal data.

For the pilot, a user confirms each new login with the current six-digit code
from their authenticator app. The default session remains active for up to 30
minutes without activity and no longer than eight hours in total; ordinary
company and contact operations do not prompt for MFA individually. Recovery
codes are single-use emergency substitutes when the authenticator is
unavailable. They must be stored separately and securely.

## Release bundle

From the repository root, `scripts/build-webapp-release.ps1` runs the local
tests, dependency check and compile check, builds the application wheel,
installs it into an isolated smoke environment, verifies fail-closed runtime
configuration and creates a ZIP plus manifest and SHA-256 checksum under
`release-artifacts/webapp`. Tracked changes are rejected unless the explicit
`-AllowDirty` development switch is used.

The bundle includes `requirements-production.lock`, migrations, verification
SQL, deployment templates and the rehearsal runbook. Runtime dependencies are
exact-version locked; an approved, hashed Linux wheelhouse or approved package
index remains a separate production supply-chain gate.
