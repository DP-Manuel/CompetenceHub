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

## Existing VPS Update Window

New10.11 owner task: perform the scoped existing-pilot V1 update, not an installer.
Current code/packagebc53775 stays bound; no migration is required or permitted.

1. DONE: local package/source binding and fresh read-only six-service health.
2. DONE LOCAL: one private operator entry; current populated snapshot/isolated
   restore, unchanged original code/config, own runtime drop-in and compensation.
3. DONE LOCAL11.11: native Ubuntu process-shim rehearsal. Full CAL61
   and V1 browser33 checks plus final update acceptance PASS; harness lifetime,
   readiness deadline and final probe order corrected without runtime changes.
   Separate actual scoped rollback PASS, old runtime/reference preserved, own
   container removed.103 focused checks PASS; full1,663/31 suite green (one extra
   protected-port skip). No real VPS/DPAPI/recovery acceptance inferred locally.
4. DONE ACTUAL11.11: actualbb7794c attempt timed out before
   Root agent dispatch; backup/restore/deployment NOT_RUN. Exact old SSH/sudo
   probe unknown, no password retry. Closed-stdin probes, distinct safe timeout/
   transport codes and report phases fixed;108 focused checks and actual read-only
   SSH/sudo/strict TLS proof PASS. One sudo input only after local gates; verified C:
   BitLocker/operator ACL and fresh-process DPAPI recovery before server update.
5. DONE ACTUAL11.11, receipt2b834613…: separate additive synthetic cohort on the actual VPS; CAL/Admin/invite/
   MFA/tours/390px/native200 checks, then own-cohort cleanup, retained original
   row hashes, nonrewound sequences and retained shared synthetic-IP protection
   counters. Unknown changes cause review, never automatic source restoration.
6. DONE ACTUAL11.11, resumeeed9aed9…: final strict HTTPS/runtime asset and six-service checks before commit;
   failure restores only the previous own runtime, not old user/security state.

Actual update11.11, run2b834613…: steps4/5 executed. Current27-table recovery
PASS, remote native CAL61/V1 access33 PASS and own cohort cleanup reached. Step6
STOP in collect after immediate systemd start; rollback REVIEW_REQUIRED. Original
ExecStart and six healthy services independently read; data reconciliation not
assumed. Full installer/update must not be retried against retained release.

Closed11.11: bound listener-wait repair ->117 targeted tests/local resume proof
-> actual resume38bd4cd -> actual receipteed9aed9… PASS, independently bound,
all27 tables unchanged, V1 ExecStart/TLS/asset/closed delivery/six services verified.
No repeat backup/restore/install/cohort. Technical window DONE, not WAITING.
Open terminal now only holds the private tunnel; never rerun to reconnect.

Current narrow horizon: usability demonstration with existing synthetic roles
(purpose: understandable Admin/Coach/Reviewer flow; inputs: guides/private V1;
deliverable: short feedback and explicit usability result; DoD: workflows reviewed,
no real activation) -> confirmed EDV DNS/TLS/delivery -> durable recovery/personal
mapping decisions -> separately approved first real access. Later steps remain
gated, no new public exposure or assumed roles. TLS expiry24.11 is unchanged.

Use existing private tunnel if strict original CA/leaf/hostname proof passes.
Never stop an unowned tunnel. Temporary synthetic outbox capture has no SMTP
worker or real recipient, is removed before final acceptance; normal delivery
remains closed. GPG, public hosting and real activation stay excluded.
