# Calendar Quality Plan v0.1

Business baseline:11.09.2026. Risk-based test decision by Manuel:15.11.2026.

Historical11.09 status: test-ready baseline under accepted ADR 0007 and CAL-T01 through
CAL-T06. Migration `0005` is applied and rollback-smoke-tested on isolated
Staging; no productive calendar, reservation or notification is active.
Current private V1.2 acceptance is recorded in the
[operating evidence](../operations/portal-v12-calendar-ux-2026-11-13.md#v12-tatsächlich-abgenommen);
the baseline above is not a claim that deployment is still pending.

## Purpose

This plan turns the accepted visual direction and the approved CAL-D01 through
CAL-D08 rules into release gates. Per-offer values remain configurable; every
migration and activation gate remains separately decidable.

## Risk-Based Evidence Reuse

Binding Owner decision15.11: choose tests from the actual diff and risk, not the
number of tests available. No default full-suite/full-browser replay for a small
update, no new test infrastructure and no extra test-only approval loop.

- Reuse passing evidence when its source/artifact, relevant dependencies,
  contracts, environment assumptions and tested behavior still match, with no
  known regression. Cite commit/hash, scope and dated result; do not count reused
  evidence as newly executed. An unrelated commit or a new session alone does
  not invalidate it. Skips and N/A remain visible, never converted to PASS.
- Identify changed behavior, necessary integration paths and realistic failure
  modes before running tests. Prefer focused regression tests and one coherent
  workflow; do not replay equivalent scenarios at every layer without a reason.
- Docs-only changes need link/context/integrity/diff checks, not app/browser/VPS
  tests. Small UI changes need the affected interactions; repeat responsive,
  zoom/focus checks when layout or interaction changed.
- Repeat full Calendar year-boundary, DST or multi-year matrices only when the
  relevant date/time/interval logic, dependencies or configuration changed, or
  a concrete failure suspicion exists. A visual picker/label change does not
  automatically invalidate unchanged domain date logic.
- Expand verification for changed shared auth/RBAC, persistence, migrations,
  serialization, dependencies or deployment/rollback behavior as their actual
  blast radius requires. Run a full suite when justified by cross-cutting change,
  uncertain impact or concrete failures, and record that reason briefly.

### Compact Private VPS Smoke

For a bounded Calendar UX update, use the existing approved synthetic workflow
and tools; no real-user activation, new accounts or new harness by implication.

1. Check approved package/hash, strict HTTPS, existing data and suitable rollback
   evidence. Preserve the previous runtime; do not restore an older data state.
2. Log in with MFA, confirm Coach/Reviewer separation and denied unauthorized
   access. Use existing accepted auth evidence for unchanged deeper edge cases.
3. In the changed form, select a one-/multi-day interval, save and reload the
   draft; verify persisted values. Check clean/dirty Cancel and exit after a
   validation error without losing a saved draft.
4. Submit, review and publish; check the public event and necessary ICS path.
   Exercise a revision/change request if that integration is affected.
5. Confirm original data preservation, scoped synthetic cleanup, retained
   rollback and all six service states. Check persistence across a backend restart
   when runtime/service change requires one; do not restart unrelated services.

Reuse backup/restore and rollback proofs only when suitable for the current data
and intervention. If not, obtain the necessary protected current recovery proof
inside the already authorized operating scope; never waive recovery safeguards.
Do not repeat a restore or a rollback rehearsal merely because a new UI update
exists. Test selection adds no authorization for a different release or real data.

### V1.2 Baseline And No-Rerun Decision

Reuse the existing1763 local passes/30 expected skips and13 browser user cases
(optional drag N/A) as development evidence, bound to application5a555e9 and
ZIP SHA754322cd… in the linked operating report. The actual15.11 remote acceptance
also remains valid; its61-check run is historical evidence, not the minimum for
every future update. V1.2 is already accepted: this policy change requires no new
VPS smoke, installation, backup, restore, restart or password interaction.

## Test Levels

| Level | Evidence |
| --- | --- |
| Domain/unit | status transitions, thresholds, capacities, expiry, stable event IDs and permission decisions |
| Repository/integration | PostgreSQL constraints, transactions, audit events, migrations, rollback and cleanup |
| API/contract | validated bodies, generic failures, CSRF/origin, rate limits, idempotency and no-store responses |
| Browser/accessibility | keyboard operation, focus, text-plus-color status, 390-pixel layout, zoom and error recovery |
| Calendar compatibility | `.ics` import, update and cancellation in Outlook plus at least one non-Outlook client |
| Operations | backup/restore, worker failure, retry visibility, monitoring, rollback and service isolation |

## CAL-1: Coach Availability And Internal Publication

- A Coach can create, change and withdraw only their own availability.
- Another Coach receives no read or write access to private availability.
- The assigned internal permission can review and publish; a named person is
  never hard-coded as the authorization rule.
- Admin operations remain authenticated, status-bound and audited.
- Multiple Coaches can publish overlapping offers on the same day.
- Drafts may overlap. Submission and publication reject overlapping intervals
  for the same Coach, permit back-to-back intervals and never block another
  Coach merely because date/time overlap.
- Public responses expose only approved fields and never private notes,
  customer identities or unpublished availability.

## CAL-2: Non-Binding Seat Reservations

- Concurrent reservations cannot exceed the offer capacity.
- Repeated submission, browser retry and double click do not create duplicate
  reservations.
- Cancellation releases capacity exactly once and follows the approved expiry
  rule.
- Capacity reduction has an explicit, tested outcome for existing interests.
- Required personal data matches the approved minimum; optional fields remain
  optional.
- Public or authenticated write access follows CAL-D01 and is protected by
  server-side authorization, rate limiting and abuse controls.
- No UI wording, status or notification represents an interest as a contract.

## CAL-3: Threshold And Internal Decision

- Crossing the configured threshold creates one internal review task, even
  under concurrent submissions.
- Capacity and threshold remain separate per-offer values.
- A threshold notification does not publish, confirm or contract an offer.
- Only the approved role can confirm or reject; substitution uses role
  assignment rather than shared credentials.
- Janay initially receives one Portal task plus one E-Mail. No substitute is
  currently named, so tests must cover the explicit unassigned-cover state.
- Notification failure is visible and retryable without duplicate tasks.
- Confirmation, rejection, material change and cancellation produce
  payload-minimized audit evidence.

## CAL-4: Calendar Delivery

- A confirmed appointment has one stable UID across invitation, update and
  cancellation.
- Date, time zone and daylight-saving transitions use `Europe/Berlin` unless
  an explicitly approved event rule says otherwise.
- Import is verified in Outlook and at least one of Google Calendar, Apple
  Calendar or another standards-compatible client.
- Updates and cancellations change the existing event instead of creating a
  duplicate.
- Organizer, attendees and description expose only approved data.
- The authoritative appointment remains in Competence Hub; attendees and the
  Coach receive the provider-neutral invitation only after explicit internal
  confirmation.
- Delivery failure is visible to the responsible internal role and never
  reported as successful.
- Direct Microsoft Graph synchronization remains outside CAL-4 until its own
  OAuth, tenant, privacy, secret, monitoring and support gates pass.

## Cross-Cutting Negative Tests

- unauthenticated, expired, revoked and wrong-role sessions;
- cross-Coach writes and guessed identifiers;
- over-capacity races and threshold races;
- invalid date ranges, past dates and dates outside the configured window;
- scripted mass submissions, CSRF and unapproved origins;
- sensitive values in logs, audit metadata, URLs, errors or public responses;
- stale browser state after reauthentication or a concurrent update;
- migration failure, rollback and restore from the approved external copy;
- disabled or failing mail/calendar delivery worker;
- reduced-motion, keyboard-only, zoom and narrow-screen behavior.

## Release Evidence Per Increment

Each increment records the affected scope/risk, reused proof and reasons for its
focused new checks, actual results and remaining gaps. Apply data/API/RBAC,
security, browser, migration/rollback and operations verification only as relevant
under the evidence-reuse rules above; no automatic exhaustive rerun. Existing
requirements and stakeholder acceptance remain binding. Staging migration, real
accounts, real availability, real contact data, external messages and production
deployment remain separately scoped approvals, without repeated approval for
unchanged steps already authorized.
