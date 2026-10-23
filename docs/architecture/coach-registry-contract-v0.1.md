# COACH-1: Registry And Lifecycle Contract

Status: authorized local implementation, 23.10.2026. No server migration,
public API activation, IONOS update, bulk import or real account mapping.
Decision: [ADR0008](../decisions/0008-coach-registry-and-static-publication.md).

## Existing Schema And Gap Analysis

Reuse `coaches.id` (random UUID), optional unique `portal_user_id`,
`public_profile_path` from 0006, `topics`, `coach_topics`, `audit_events` and
the Calendar `coach_id` foreign key. Existing `services/coach_services` describe
platform services, not a person's versioned workshop/lecture catalogue.
Missing: explicit lifecycle, immutable profile revisions, topic categories,
versioned competencies/offerings/assets, environment approvals/publications.
Do not create another Coach identity table, duplicate topics, or derive IDs
from a name, email or route. Duplicate names are legitimate. Client request
UUIDs provide retry identity, not person matching.

## Ownership And States

- Lifecycle: draft, active, paused, inactive, archived. Independent of publication.
- Profile: draft -> submitted (immutable); amendments require a new revision.
  Pause/offboarding closes an existing draft as abandoned (also immutable),
  retaining it without blocking a fresh reactivation draft.
- Publication per environment preview/production: published or withdrawn;
  absent row means not_published. Preview does not confer production rights.
- An active Coach is not necessarily public; a public Coach has no automatic
  Portal account/role or Calendar mapping. Preserve current CAL-1 ownership.
- Existing legacy `public_profile_status` is not an approval and is not silently
  migrated. New Registry publication is a separate explicit contract.

## Revision And Approval

Typed, bounded public-only fields: display name, optional academic suffix,
intro, description, professional background, target groups, optional validated
profile path. Relational snapshot children: topic UUID references, competencies,
offerings (lecture/workshop/coaching/individual/other), and image references.
Assets are paths + SHA-256 + alt text + environment scope, never binary DB blobs.
No private email/address, contracts, invoice fields or original certificate files.
Field allowlisting is not automatic PII detection in free text; human source,
privacy and consent review is mandatory before publication approval.

Submission freezes content, including topic labels/categories and asset hashes.
Each revision needs content_review, person_consent and the exact environment's
publication approval, each with actor, timestamp and opaque evidence reference.
These are evidence attestations, not a mechanism that generates legal consent.
No draft or unapproved revision may enter a public projection. New revision,
new assets or reactivation cannot reuse previous approvals.

## Persistence And Concurrency

Local migration 0007 extends existing schema. Aggregate operations take the
existing Coach row lock used by CAL-1; optimistic lock_version rejects stale
mutations. Revision numbers increase under that lock. Mutation and payload-free
audit commit in one transaction. Do not PUT an arbitrary unstructured JSON
profile into the database. SQL grants deny normal hard delete of Coach/history.
Only a never-submitted draft's children may be replaced by a draft edit.

Onboarding: authorized source -> privacy/source audit -> random Coach UUID ->
draft -> taxonomy/offer/assets -> submit -> attestations -> active -> publication.
Offboarding: remove publication, retain revisions/history and same UUID.
If live/future Calendar offers exist, fail closed with a coordination conflict:
withdraw through existing CAL-1 first, never delete historical offers silently.
Portal access changes remain explicit, separately authorized operations.
New Registry Coaches have no operational `coach_topics` grants automatically:
profile topic snapshots are public editorial content, not CAL-1 permissions.
`coaches.public_profile_path` retains its separate explicit 0006 Calendar mapping;
revision paths allow environment-specific content without silently changing it.
Legacy Coaches (no registry_request_id) cannot be adopted by incidental API edits.
Migration 0007 adds Calendar write guards only for explicitly enrolled Registry
Coaches; the existing Coach row lock serializes writes with pause/offboarding.
Withdrawals remain possible and historical Calendar data is retained.
Reactivation: existing UUID -> new revision -> fresh review/consent/environment
approval -> active -> publish. Pausing also withdraws both environments.
Withdrawing one environment prevents reusing that revision's old approval there;
republishing requires a newer submitted and freshly approved revision. Other
environments remain independent. Source evidence and approval rows are retained.

## Local Admin Contract

Use `/api/v1/admin/coaches`, personal MFA-backed admin sessions, same-origin
and CSRF on mutations, 32 KiB body limit, strict unknown-field rejection.
Registry is optional/injected and unavailable by default in the existing runtime
until migration/activation are approved. No large Admin UI in this slice.
Reads bounded; mutation commands carry expected_version; no DELETE endpoint.
Conflict responses never expose DB DETAIL, profile payloads or source documents.

## Static Public Projection And Migration

Explicit environment parameter; allowlist only approved revision fields.
No internal UUIDs, evidence refs, audit actors, accounts or original sources in
the export. Static Astro consumes an approved generated artifact later; it must
never connect to PostgreSQL. This local implementation must not change existing
Astro ingestion/production content or claim a completed content migration.
Withdrawal removes a profile from the NEXT artifact; a static website still
requires a separately approved rebuild/deploy to remove already served bytes.
No false promise of instant remote withdrawal.

Susanne and Elisabeth are shape/offer-catalogue reality checks only, not automatic
DB imports. Synthetic fixture covers new intake and multiple offering types.
Real import, UUID approval and existing-Coach migration need an explicit mapping
review before any server writes. FIN-01 remains a separate future consumer of
Coach UUIDs; CAL-2 and invoice fields are not part of this model.

## Verification And Next Gate

Required: create/retry/conflict, versioned draft/submit, approvals for both
environments, withdrawal, pause/offboard/reactivate same UUID, taxonomy M:N,
multiple offerings, asset scope, account independence, stale mutations,
admin/CSRF boundaries, payload-free audit and real local PostgreSQL constraints.
Implemented and actually verified locally:

| Gate | Evidence |
| --- | --- |
| Domain/Admin API | 33 tests: create/retry/duplicate-name handling, draft/submit/stale rejection, scoped approvals/publication, withdraw/new approval, pause/offboard/reactivate same UUID, abandoned pending draft, assets, shared topics/categories,8/17 synthetic catalogue shapes, admin-only/CSRF/body/privacy boundaries |
| Real local PostgreSQL16 | Dedicated opt-in scenario PASS: migration0001-0007, real repository, concurrent create/revision, retained snapshots, DB-enforced freezes, path/asset/environment guards, future Calendar conflict/withdrawal/pause guard, reactivation and payload-free audit |
| Native local Admin API | Same real-PG scenario uses actual password/Login/MFA/session, no-store Admin list/create, CSRF/foreign-Origin rejection and immediately effective role revocation; no fake MFA bypass |
| Isolation | Only owned localhost55434 container, process-only generated credentials, no host data mount, tmpfs data; entire owned container removed after PASS/failure, VPS untouched |
| Regression | Full local suite 488 PASS,18 opt-in skips (17 Staging + dedicated local Registry scenario); current actual native-local CAL-1 result is linked from the checkpoint. Staging0006 evidence is not relabeled as0007 deployment |

Run from repository root in PowerShell:

```powershell
.\apps\webapp\scripts\run-coach-registry-local.ps1 -PythonPath '.\apps\webapp\.venv\Scripts\python.exe'
```

Requires Docker Desktop and an unused55434. Success:
`COACH_REGISTRY_LOCAL=PASS CONTAINER_REMOVED=PASS SERVER_UNCHANGED=PASS`.
No real passwords are requested; generated fixture credentials remain in process
memory and must not be copied to chat. Never pass a VPS URL to this harness.

## Remaining Boundaries

No Admin UI, server migration, real data/import, account/Calendar mapping,
asset upload service or active Website projection importer is included.
The pure public_projection generator is tested; asset hash verification and
approved-source ingestion must be added before replacing static Astro data.
List reads are paginated; detail/aggregate history currently loads all revisions
and needs a history-pagination/load review before productive management at scale.
Privacy erasure/exceptional hard delete needs a separate retention/admin contract;
it is deliberately not a normal business operation or API DELETE endpoint.

Recommended next block: local synthetic Coach-management UI, using this contract
and existing MFA/Admin API, with history pagination and native local E2E proof;
no new source import, server write or IONOS change. Separate implementation scope
is needed; this completed block does not authorize that UI automatically.
