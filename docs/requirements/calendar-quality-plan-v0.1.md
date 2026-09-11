# Calendar Quality Plan v0.1

Stand: 11.09.2026

Status: test-ready baseline under accepted ADR 0007 and CAL-T01 through
CAL-T06. Migration `0005` is prepared locally but not authorized for Staging;
no productive calendar, reservation or notification is active.

## Purpose

This plan turns the accepted visual direction and the approved CAL-D01 through
CAL-D08 rules into release gates. Per-offer values remain configurable; every
migration and activation gate remains separately decidable.

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

Each increment needs approved requirements, a reviewed data/API/RBAC change,
green automated tests, browser evidence, a security review, migration and
rollback evidence where applicable, operations evidence and named stakeholder
acceptance. Staging migration, real accounts, real availability, real contact
data, external messages and production deployment each remain separate gates.
