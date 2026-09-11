# CAL-1 Technical Design v0.1

Stand: 11.09.2026

Status: implementation-ready design draft after acceptance of ADR 0007. This
document authorizes no migration, account, real availability, notification or
deployment.

## Purpose And Sources

CAL-1 lets an authenticated Coach maintain their own planned group offers and
lets an explicitly authorized internal reviewer approve the public version.
It implements only Coach availability, review and controlled publication.
Reservations, threshold notifications, binding booking and calendar delivery
remain CAL-2 through CAL-4.

Binding inputs are accepted ADR 0007, accepted CAL-D01 through CAL-D08, the
Calendar requirements and quality plan, and the existing PostgreSQL 16,
FastAPI, session, CSRF/Origin, RBAC and audit conventions.

## Current-State Facts

- `coaches` links at most one Coach profile to a `portal_user`.
- `topics` and `coach_topics` provide controlled Coach topics.
- `portal_users`, `roles` and `user_roles` provide multiple roles per account.
- `audit_events` is append-oriented and contains no raw payload.
- Protected writes require an active MFA session, exact Origin and the
  session-bound CSRF token. Responses use `Cache-Control: no-store`.
- Migration ownership remains separate from the restricted runtime role.

## Scope Boundary

Included:

- private own-offer list for a Coach;
- draft creation/editing in a rolling three-month window;
- submission into an internal review queue;
- request for changes and approval by a dedicated permission;
- revisions that keep the last approved public version stable;
- public read-only list/detail containing approved fields only;
- withdrawal, optimistic concurrency and minimized audit evidence.

Excluded:

- seat reservations and company/contact data;
- threshold tasks or E-Mail;
- contract, offer, invoice or payment status;
- `.ics` delivery or direct Outlook/Graph access;
- meeting links, attendee lists and private calendar synchronization;
- hard deletion and final retention periods.

## Component Shape

1. A calendar domain service owns validation, transitions, authorization and
   public projection rules.
2. A PostgreSQL repository owns atomic revision publication, optimistic
   locking and audit writes.
3. A protected Portal router serves Coach and review workflows.
4. A separate public router serves approved projections only and never
   serializes repository rows directly.
5. The existing same-origin Portal client consumes the protected router. The
   Astro calendar remains synthetic until a separately approved integration.

No new service, queue or external integration is needed for CAL-1.

## Proposed Data Model

Migration `0005` is reserved as the likely next number but must not be created
or applied without separate approval.

### `calendar_offers`

Stable identity and ownership of one planned offer.

| Field | Type | Rule |
| --- | --- | --- |
| `id` | UUID | primary key, generated server-side |
| `coach_id` | UUID | required FK to `coaches`, delete restricted |
| `created_by_user_id` | UUID | required FK to `portal_users`, delete restricted |
| `client_request_id` | UUID | retry key unique per actor |
| `lifecycle_status` | text | `active` or `withdrawn` |
| `lock_version` | bigint | starts at 1 and increments on every command |
| `created_at`, `updated_at` | timestamptz | server controlled |
| `withdrawn_at` | timestamptz nullable | present only when withdrawn |

There is no uniqueness on date or time. Different Coaches may overlap. A
same-Coach conflict rule remains a pre-migration decision and must not be
silently encoded as a global exclusion constraint.

### `calendar_offer_revisions`

Content revision that becomes immutable on submission. Editing a published
offer creates a new draft while the prior published revision remains visible.

| Field | Type | Rule |
| --- | --- | --- |
| `id` | UUID | primary key |
| `offer_id` | UUID | required FK, delete restricted |
| `revision_number` | integer | positive; unique per offer |
| `workflow_status` | text | `draft`, `in_review`, `changes_requested`, `published`, `superseded` |
| `topic_id` | UUID | required active topic linked to the Coach |
| `title` | text | required, trimmed and bounded |
| `summary` | text nullable | bounded public copy |
| `starts_at`, `ends_at` | timestamptz | timezone-aware; end after start |
| `time_zone` | text | pilot default `Europe/Berlin`; validated IANA identifier |
| `format_code` | text | controlled; final vocabulary required before migration |
| `public_location` | text nullable | never a secret meeting URL |
| `capacity` | integer | positive; business maximum still open |
| `review_threshold` | integer | positive and distinct from capacity |
| `decision_deadline` | timestamptz | before start; public after publication |
| `price_display_text` | text | public amount/note, not a finance record |
| `created_by_user_id` | UUID | required FK to `portal_users` |
| `submitted_at`, `published_at` | timestamptz nullable | state-dependent |
| `created_at`, `updated_at` | timestamptz | server controlled |

Required constraints/indexes:

- unique `(offer_id, revision_number)`;
- at most one `draft`, one `in_review` and one `published` revision per offer;
- own-Coach, review-queue, public time-range and topic/time indexes;
- state-dependent timestamp and positive-number checks;
- no runtime cascade deletion of offers or revisions.

Whether `review_threshold <= capacity` is a business rule is still open. CAL-1
stores both values but does not invent that constraint.

### `calendar_review_decisions`

Append-only evidence for review outcomes.

| Field | Type | Rule |
| --- | --- | --- |
| `id` | bigint identity | primary key |
| `revision_id` | UUID | required FK, delete restricted |
| `reviewer_user_id` | UUID | required FK, delete restricted |
| `outcome` | text | `published` or `changes_requested` |
| `note` | text nullable | private, bounded, never public or in audit metadata |
| `decided_at` | timestamptz | server controlled |

The runtime may insert but not update/delete decisions. Existing
`audit_events` additionally records action, entity ID and outcome without
copying titles, notes, times or prices.

### Authorization Role

Add the non-admin role code `calendar_reviewer`. It is additive to `internal`
and grants only review-queue access and review transitions. Janay is the
initial intended assignee, but her name/account ID never appears in code,
schema or migration. For the Pilot only an Admin assigns/removes this role
until the general role-assignment policy is approved.

## Lifecycle And Transactions

| Current state | Command | Actor | Result |
| --- | --- | --- | --- |
| none | create | linked Coach or Admin | draft revision 1 |
| draft | edit | owning Coach or Admin | draft/version updated |
| changes requested | revise | owning Coach or Admin | prior revision `superseded`; next draft created |
| published | revise | owning Coach or Admin | next draft created; published revision remains public |
| draft | submit | owning Coach or Admin | `in_review` |
| in review | request changes | reviewer or Admin | `changes_requested` |
| in review | publish | reviewer or Admin | new `published`; prior one `superseded` atomically |
| active | withdraw | owning Coach, reviewer or Admin | offer `withdrawn`; no public projection |

Submitted, changes-requested and published revisions are never edited in
place. Revision starts from the reviewed content but creates the next draft.
The old public revision stays visible until approval, except withdrawal
immediately removes the offer. Notification consequences remain disabled until
CAL-2/CAL-4.

Each write locks the stable offer row, checks `lock_version`, applies the
transition and appends audit evidence in one transaction. Stale clients must
reload. Retrying a completed transition with the same expected version returns
the current state without a duplicate revision or decision.

## Public Projection

Only active offers with one published revision are public. Responses include
the offer ID, approved Coach display/profile reference, topic, title/summary,
start/end/time zone, format/public location, capacity, decision deadline, price
display text and public update time.

They never include portal-user IDs, draft/review states, reviewer identity,
review notes, internal review thresholds, internal availability, contact data
or audit rows.

## Security, Privacy And Operations

- Protected operations reuse active-session, MFA, exact-Origin and CSRF checks.
- Coach ownership is resolved through `coaches.portal_user_id`; a client Coach
  ID never establishes access.
- Unknown/foreign IDs use generic responses without confirming private data.
- Bodies reject unknown fields and retain the existing 32 KiB limit.
- Reviewer notes need approved retention/deletion before real data.
- Logs/audit contain no bodies, notes, price text or personal data.
- Runtime DDL and hard deletion stay denied; migration ownership stays split.
- Backup, restore, monitoring, rollback and Chatbot checks remain production
  gates. CAL-1 introduces no timer or external network dependency.

## Migration And Rollback Plan

Before SQL is authored:

1. approve same-Coach overlap behavior;
2. approve format codes and numeric/text bounds;
3. decide whether threshold may exceed capacity;
4. confirm reviewer-role assignment policy and retention owner.

The migration must be additive, transactional and empty-data safe. Its smoke
test runs inside a rollback transaction and proves ownership, constraints,
runtime DML and denied DDL/update/delete privileges.

Before data use, rollback may reverse the Staging migration. After any real
availability exists, rollback preserves tables and uses application rollback;
destructive down-migration is forbidden.

## Verification Matrix

| Area | Required evidence |
| --- | --- |
| Domain | all transitions, rolling window and field invariants |
| RBAC | own/foreign Coach, reviewer, internal without reviewer, Admin, company contact and anonymous |
| Repository | atomic publication, prior revision, stale conflict and no partial audit |
| Public API | published-only projection and forbidden-field regressions |
| Migration | rollback smoke, owner/grant checks, indexes and zero residue |
| Browser | keyboard/focus, 390 px, 200% zoom, stale-edit recovery and text status |
| Security | ID guessing, CSRF/Origin, body limits, audit/log minimization and no high/critical finding |

## Definition Of Done For The Design Gate

- architecture, ownership, projections and transitions are explicit;
- API and RBAC contracts are versioned;
- unresolved values are migration gates rather than guesses;
- no migration, code, account, real data, message or deployment was created.
