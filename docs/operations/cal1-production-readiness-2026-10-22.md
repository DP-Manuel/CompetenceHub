# CAL-1 Production Readiness Package

Date: 2026-10-22. Status: **PREPARED, NOT DEPLOYMENT-READY**.
Owner: Manuel for release coordination; EDV for hosting/mail inputs; business
role approvals remain with Manuel/Janay. Thomas Ross is the named technical
break-glass contact; an exercised access path is still required.

Authority: the batched-development addendum explicitly permits this preparation
after native CAL-1 acceptance. It does not authorize installation, proxy changes,
productive users, mail, tracking or business data. No new live commands are
requested from Manuel by this document.

## Proven Baseline And Remaining Gap

Candidate application source: `87844d1`, with additive access from `40a7574`.
[Native evidence](../architecture/calendar-cal1-access-batch-2026-10-22.md):
142 real-runtime browser checks against VPS Staging PostgreSQL, 17-test API
gate, 424-test post-regression, all cleanup/health gates PASS. No migration
was added. Staging has migrations 0001-0006, 27 owner tables and zero rows in
all 20 dynamic areas after cleanup.

The runtime/UI ran locally via HTTPS and a tunnel to the VPS database. This
does not prove installation/startup as a Linux service or public proxy behavior.
Existing templates are references, not installed/validated service evidence.
IONOS and Pages are independent; this package changes neither.

## Current Gate Matrix

| Gate | State / evidence | Required closure / owner |
| --- | --- | --- |
| CAL1-NATIVE | PASS | Dated evidence above; rerun only for material changes |
| DB-STAGING | PASS | 0001-0006, owner 27, zero residue; no migration replay |
| RUNTIME-INPUT | OPEN | Exact app FQDN/origin, DNS/TLS path, unused loopback port, service identity and release owner; EDV/Manuel |
| PACKAGE-LINUX | OPEN | Clean source ZIP/wheel/inventory SHA, approved Linux dependency source or hashed wheelhouse, supported Python install/import/config smoke; Manuel/EDV |
| PROXY-REHEARSAL | OPEN | Separately approved synthetic Linux/systemd/Nginx/TLS rehearsal on dedicated paths, actual browser cookie/Origin/CSRF checks; Manuel/EDV |
| DB-PRODUCTION | OPEN | Confirm separate target database, bootstrap contract, restricted roles and migration inventory; never reuse Staging identity/data; Manuel/EDV |
| KEYS-CONFIG | OPEN | External root-controlled configuration, per-purpose/versioned keys, exact origin and compromised-password corpus, secure recovery custody; authorized operator only |
| BACKUP-OPS | OPEN CURRENT OPERATIONS | Retain historical encrypted off-server restore proof; prove current production scheduling, monitor, owner and actual success/failure notification receipt before real data; Manuel/EDV |
| MAIL | OPEN | SMTP/TLS/From/Reply-To, target origin, mailbox ownership and synthetic receipt/retry proof; EDV/Janay |
| ROLES-MAPPING | OPEN REAL-DATA GATE | Approved named users, exact roles, Coach UUID ownership, publication paths and onboarding method; Manuel/Janay |
| PRIVACY-REAL-DATA | OPEN | Document approved purpose, fields, retention/access and required notice for the Portal; central Website links alone do not cover new processing |
| BREAK-GLASS | OPEN PROOF | Exercise authorized recovery/MFA/access and incident handover for Thomas; custody separate from repository |
| RELEASE-GO | CLOSED TO EXECUTION | New explicit environment/source/artifact/time/rollback approval; no inherited production permission |

The Website's working DNS/SFTP and legal decisions do not close app-origin,
Portal processing, SMTP or backend operation gates. Missing inputs must not be
guessed. Neither a health endpoint nor this matrix substitutes for Go/No-Go.

## Role And Mapping Input Contract

Request only approved metadata/decisions, never passwords, private keys,
recovery codes, credential exports or real records in chat/Git. Actual user
emails and UUID mappings belong to the authorized restricted operator workflow,
not this public handoff. Do not infer a person from a display name or profile URL.

| Access need | Implemented boundary | Required explicit input |
| --- | --- | --- |
| Coach offers | coach; server ownership via coaches.portal_user_id | Approved user-to-Coach UUID pair, active status, exact approved public profile path or NULL |
| Calendar review | calendar_reviewer; no company/contact/Admin rights alone | Named reviewer and grant approval; no automatic grant to internal |
| Company operations plus review | internal + calendar_reviewer, explicit mixed grants | Confirm Janay's exact mixed role set; do not assign it from job title |
| Administration | admin; Calendar and company/admin capabilities | Named admin approval and recovery owner; not the default reviewer assignment |
| Internal only | Company workspace, no Calendar review by default | Business owner confirms whether review is also needed |
| Company Contact only | No admission through current Portal access contract | Do not onboard as a working Portal login; future scope, not a role workaround |

An empty Coach/profile mapping is an empty/denied ownership state, not permission
to manufacture a mapping. Existing internal invitation/reset lifecycle is not
broadened to pure Coach/Reviewer onboarding by CAL-1 access. Their real initial
credential/onboarding procedure needs a scoped design/approval before use.
No generic user-management or role-assignment UI is assumed to exist.

## Safe Packaging And Migration Plan

Use the existing [release rehearsal runbook](../architecture/webapp-release-rehearsal-runbook.md)
and `scripts/build-webapp-release.ps1` only after a reviewed clean-source build
is selected. Do not stash/delete unfamiliar local files or use AllowDirty to
label a candidate production-ready. If local unrelated files block cleanliness,
prepare a separately owned clean export/worktree, not a destructive cleanup.

Before a future bundle, review the builder's deployed-document list: it still
copies the dated Website production plan alongside the backend runbook and does
not automatically include this package. Its deploy-directory copy also needs
an explicit secret-exclusion/file-inventory review. These are packaging gates,
not reasons to run an unreviewed archive. No release ZIP or Linux wheelhouse was
created in this documentation slice. Future bundle acceptance must include this
package, additive access contract, exact source, file hashes and no secrets.

CAL-1 access adds no migration. On Staging, never replay 0001-0006. For a future
production database, inventory first and separately review a production bootstrap
and missing migrations; `bootstrap-staging.sql` is NOT that approval. Before any
approved data change: protected dump, checksum/catalog validation, restoration
decision/owner, matching rollback-only SQL smoke and owner/runtime privilege
checks. Keep schema owner/migrator/runtime identities distinct.

## Ordered Rehearsal And Rollout Plan

This is a plan, not an execution instruction or approval. Each stage stops if
its preconditions fail. No Chatbot service, database, venv, nginx site or port
may be reused or restarted for convenience.

1. Close RUNTIME-INPUT and PACKAGE-LINUX. Identify artifact SHA, dedicated release
   path/venv/identity/loopback port, prior backend state and rollback owner. Obtain
   separate approval for one synthetic Linux/proxy rehearsal, not production.
2. Inspect four service healths/PG loopback; take authorized metadata-only backup
   of changed unit/proxy/symlink configuration. Do not read secret files. Install
   the reviewed artifact into an inactive dedicated release directory.
3. Have the authorized operator supply external configuration without exposing
   values. Validate placeholders, dependency versions/imports, fail-closed config
   and systemd definitions; validate nginx syntax before any approved reload.
4. Start only the separately approved synthetic candidate. Verify bounded startup
   readiness on loopback before exposing any synthetic HTTPS route. No worker
   timer, production database, real accounts or public Website change.
5. In the same window, test exact HTTPS-origin/cookies, native pure-role MFA and
   scopes, workflow/concurrency/public DTO and error/log privacy through the actual
   proxy. Mail-worker delivery is a separate authorized synthetic-mailbox step;
   leave the worker/timer off otherwise. Never treat a queued outbox as receipt.
6. Exact-ID cleanup, independent SQL zero/owner/migration proof, all service healths,
   PG loopback and required rollback exercise before closing the owned window.
   Preserve sanitized evidence and stop/remove only the owned rehearsal runtime.
7. Review remaining data/privacy/backup/mail/onboarding gates. Only a separately
   scoped production Go/No-Go may permit promotion, followed by its approved
   smoke/monitoring period. No approval means no activation.

## Smoke And Stop Matrix

| Check | Expected result | Stop condition |
| --- | --- | --- |
| Artifact/source | Approved source/SHA, clean manifest, locked approved dependencies | Wrong hash, dirty build, unknown dependency source or secret in bundle |
| Startup health | /health/live and /health/ready succeed after bounded readiness polling | Timeout, dependency failure, crash loop or leaked configuration |
| App HTTPS path | Correct hostname/TLS, exact Origin, Secure/HttpOnly/Host-only cookie and no-store | Cookie/redirect/Origin mismatch, insecure transport or caching |
| Roles/MFA | Pure Coach/Reviewer admitted after MFA; no internal grants; foreign/roleless/revoked denied | Privilege expansion, cross-Coach data, session before MFA |
| Workflow | Draft edit; published/change-requested new revision; review not directly editable | Lost published revision, stale-write overwrite or duplicate transition |
| Public projection | Published allowlist only, no internal fields or invented profile mapping | Draft/private data or personal mapping leak |
| Privacy/logs | Generic errors, identifier-only audit, no passwords/tokens/row DETAIL | Any sensitive payload or credential in response/log/export |
| Co-host health | Chatbot/nginx/fail2ban/postgresql remain active; PG loopback | Any unrelated service degradation or exposed PG |
| Cleanup | Exact synthetic UUIDs only, independent zero/baseline counts | Incomplete cleanup; retain investigation access, never broad DELETE |
| Operations | Approved backup/restore and notification proof before real data | Unproven restore, missing operator or silent monitoring |

## Rollback And Repair Contract

- Before activation record whether a backend service/symlink already exists.
  This project has no proven prior productive Portal release. On first install,
  rollback is to the recorded inactive state, not an invented previous version.
- For a synthetic rehearsal stop only the owned API/worker/timer if installed,
  restore only backed-up owned unit/proxy/symlink changes, syntax-check before
  any approved reload, then prove all pre-existing services and PG loopback.
- For a future application-only rollback use a separately verified compatible
  backend artifact, same schema/config/key versions and approved old target.
  Compatibility must include the new Portal access paths used by the packaged UI.
- Keep MFA/session/outbox key versions needed by retained data; rollback must not
  silently replace/lose external keyrings. Do not loosen admission to bypass an
  old version's missing Coach/Reviewer access.
- Never down-migrate or restore a database dump as an automatic application
  rollback. Restore can lose later writes and invalidate sessions/outbox state;
  require a separate owner-approved repair/restore plan and evidence.
- SMTP is an external side effect: an email cannot be unsent. Stop only the owned
  worker/timer if unsafe, inspect sanitized outbox state and preserve idempotency;
  do not blindly replay or erase delivery evidence.
- No rollback may point IONOS at this backend candidate or republish a historical
  personal Website release. Website rollback remains its own SB-54 contract.

## Operations And Release Notes

User-visible candidate change: pure Coaches and Calendar reviewers can log in,
complete real MFA and resume the Portal without internal company permissions.
No role is granted by login. Existing internal Auth remains compatible. Native
runtime evidence is closed; deployed operational readiness remains open.

Before real operation define a monitoring owner/window, health/readiness failure
thresholds, error/latency signals, resource headroom, pending/failed outbox state,
backup freshness/integrity and actual success/failure notification receipt.
Manuel requested brief automatic outcome messages; provider/channel are still
inputs, not implemented mail. Janay's mailbox has no confirmed absence cover;
do not promise a response SLA. Thomas's recovery procedure must be exercised.

The local package is a planning deliverable. No runtime, feature flag, account,
role, database, systemd unit, nginx configuration, SMTP timer or tracking was
changed here. Disabled state is operational absence/inactive services and no
approved data/exposure, not a newly invented software feature flag.

## Exactly One Recommended Next Block

**Runtime/operations input closure for a controlled synthetic Linux/proxy rehearsal.**
Purpose: make the next execution window deployable and reversible without
repeated credential requests. Inputs: non-secret RUNTIME-INPUT/PACKAGE-LINUX
decisions, deployment owner/window and separately scoped rehearsal approval;
productive data/roles/SMTP need not be activated to do that rehearsal.
Deliverables: reviewed clean-source bundle/docs, rendered non-secret host/port
plan, approved supply-chain source and stop/rollback record. Done means every
prerequisite for steps 1-6 is explicit and the rehearsal has its own approval;
missing facts stay OPEN. No SSH/password action is currently required.
