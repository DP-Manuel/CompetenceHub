# Real User Readiness V1

Owner: Manuel. Started10.11.2026 from3fd7c24 after accepted private VPS pilot
and Manuel's explicit manual approval of function/layout. Janay acceptance OPEN.

## Scope And Contract

Synthetic local implementation/acceptance only, then a consolidated private-pilot
update candidate. No real identity/account/role/invitation, Coach import, Website
deployment, GPG, installer rerun or baseline reset. Preserve active four-account
VPS reference. External access/SMTP still unconfirmed per Manuel's reply10.11;
prepare send-ready EDV request early, pilot TLS expires24.11 18:20 MEZ.

Reuse0001–0006 tables, sessions, encrypted outbox, activation/MFA/recovery and
append-only audit. Admin V1 actions require fresh MFA session, exact target UUID,
optimistic user version and explicit confirmation. No self-demotion/deactivation,
no last-admin removal, no bypass activation of pending accounts, no implicit Coach
ownership transfer. Changing access revokes sessions/challenges/open tokens and
cancels encrypted pending delivery atomically. Existing qualifications untouched.

Role changes select one of admin/internal/coach/calendar_reviewer; Coach needs a
confirmed existing stable UUID, not a slug/name. Company-contact administration
outside V1. Preparation remains possible while actual dispatch is default closed.
No activation-token retrieval/copy in Admin UI and no SMTP fallback.

Tour enhancements reuse native controller. Automatic introduction only after new
MFA onboarding; routine logins never force a tour. Role/index/status only in tab
history, cleared on logout; no user IDs, Web Storage or external tracking.
Manual help/restart remains available; no cross-device progress claim.

## Execution

1. DONE: existing auth/API/UI/schema/rights audit; preserve reference;
   gaps: mutation UI/API, invitation revoke/status, tour placement/progress.
2. DONE: atomic Admin operations/status/audit and same-schema security tests.
3. DONE: usable management, task-focused dashboards, tours and onboarding.
4. DONE: isolated native PostgreSQL/MFA/browser acceptance incl390px/200%,
   conflicting edits, revocation, role change, tours, CAL workflow and restart.
  136 onboarding/management +46 CAL checks,3 native API tests, full1,635/30 suite;
   controlled out-of-order inventory regression and actual native200 screenshots.
5. DONE: cohort9 mapping matrix without invented identities/UUIDs, short guides,
   EDV mail, bound release/update candidate and risk-specific rollback evaluation.
6. DONE LOCAL / REMOTE GATED: reviewed sourcebc53775 committed/pushed; exact
   ZIP/hash and fresh Linux/proxy37 checks bound in canonical result. Release
   rerun1,635/30 PASS. Final documentation is a separate commit. Remote update NOT
   performed: current privileged state/rollback gate and preservation proof required.

Canonical result/access/release boundary: [Readiness V1](../../operations/real-user-readiness-v1-2026-11-10.md).
Read-only VPS19:23 MEZ: all six services active. No privilege input, installation,
DB mutation or new backup attempted. The old empty snapshot is not a snapshot of
the deliberately retained reference dataset; do not run the old installer.

## Rolling Horizon

Complete local readiness -> bound reversible update candidate -> protected update
acceptance if recovery/privilege gates close -> Janay usability acceptance ->
confirmed domain/TLS/delivery and durable recovery -> separately approved personal
Admin/Reviewer/Coach activation. Only local readiness is in immediate execution;
later gates cannot be inferred from technical pilot approval.
