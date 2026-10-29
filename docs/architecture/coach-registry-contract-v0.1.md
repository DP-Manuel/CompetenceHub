# COACH-1: Registry And Lifecycle Contract

Status: authorized local implementation, 23.10.2026. No server migration,
public API activation, IONOS update, bulk import or real account mapping.
Decision: [ADR0008](../decisions/0008-coach-registry-and-static-publication.md).

Follow-on23.10: [COACH-2 local Admin UI](coach-admin-ui-contract-v0.1.md) is
separately authorized and accepted with synthetic data. The original COACH-1
slice/evidence below stays dated; [COACH-3 analysis](coach3-existing-content-migration-plan-2026-10-23.md)
now owns the proposed import gate, not an actual migration.

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

## COACH-3C Additive Target Contract

Authorized29.10, local synthetic implementation only. Migration
[0009](../../apps/webapp/database/migrations/0009_coach_lossless_target.sql)
extends the same Coach UUID/profile revisions/offerings; it does not introduce a
second Coach aggregate. Actual acceptance is tracked in the
[COACH-3C execution plan](../exec-plans/completed/coach-3c-target-2026-10-29.md).

`ProfileContent.target_version=0` retains the existing contract and historical
approval semantics. Existing rows gain only empty/NULL optional target fields;
no historical consent, person, timestamp or verification is inferred. Version1
opts into the richer typed contract and exact object evidence. An existing rich
Coach cannot be downgraded to0. Full-snapshot clients must explicitly retain or
change populated fields, including matching nested qualification/family/format
fields; omission conflicts rather than silently erasing unknown data.

### Qualifications And Roles

`public_roles` are editorial role labels, not Portal permissions. They remain
separate from topics, competencies, qualifications and offerings.
`coach_qualifications` stores a stable item key, canonical title, optional explicit
public display label, issuer/type, ordering, public visibility, active/historical
status and separate internal verification state/reference/note. Identity is
`(Coach UUID, item key)` across immutable revision snapshots, not a mutable title.
Public qualifications require an explicitly supplied public label. Canonical
titles and internal verification metadata never become public by default.
There is no automatic conversion from a role or experience into a qualification.

### Families And Formats

`coach_offering_families` groups existing `coach_offerings` by stable family key
within the same revision/Coach. Renaming a family/format does not change its key.
Inactive formats remain in their revision history. An active family is projected
only when it has active formats. Formats of inactive families are not projected.
Grouped formats are not duplicated in the standalone public offering list.

Typed bounded metadata holds variants/options/add-ons (not duplicate main
offerings), target groups/focus, service domains, duration and delivery mode.
Duration supports same-day clock windows, minutes or weeks/session schedules;
`Live` can remain `live_unspecified`, not guessed as online or in-person.
Program modules are brief public module names, never a workshop-document copy
and never automatically global topics. Profile/family/format boundaries are
explicit text and excluded-service codes. Psychotherapy is a separate domain,
cannot be a coaching format and remains nonbookable. Conflict work does not
infer mediation/supervision; health promotion does not infer medical treatment.
There is no price field or protected source body in this contract.

### Exact Evidence

Admin-only `coach_object_evidence` is append-only. Each entry binds a stable
evidence key to Coach, revision, subject type/key, exact server-calculated SHA-256,
evidence kind, environment, scope and approved/unknown/rejected decision.
Subjects are profile, portrait, qualification, family or format. Kinds distinguish
profile content, portrait asset, qualification, offering content and publication.
`public_content`, `internal_verification` and `protected_source_content` are
separate scopes. Consent for a protected original is never consent for short
public copy, or vice versa. Private source references are opaque, not file reads.

Optional historical approver/time/day remain NULL when unknown. A day-only
source is not converted into an invented timestamp. Recording actor/time are
separate technical metadata. Future historical dates and wrong subject/hash/kind
bindings are rejected. New revisions inherit no evidence. Latest matching
decision wins; a rejection of required consent withdraws that environment's
publication, while retaining all history. Re-publication still requires a newer
approved revision under the existing withdrawal contract.

Rich publication requires the original reviewed/consented/environment approvals
AND matching public evidence for profile content/publication, active portrait,
public active qualifications, visible families and formats. Preview and
Production are independent; internal verification and unknown evidence cannot
satisfy a public gate. Domain guards and additive PostgreSQL guards enforce this.

### Public Allowlist

Projection positively selects legacy public fields and safe asset fields. Rich
output adds role labels, explicitly public active qualification labels/issuer/type,
family/format short descriptions, metadata and boundaries. Typed presentation
preserves teaser, section text, cards, quotes, languages, image dimensions and
environment-specific HTTPS links. All text is data, never executable HTML.
No generic Admin serialization is a public export: evidence objects/references,
verification states, internal notes, source paths, protected originals, prices,
audit/import metadata and internal UUIDs are absent. This does not switch Astro
to DB output or remove already deployed static bytes automatically.

### Local Upgrade Operation

0009 is an offline local gate: reconnect/restart database pools after DDL so
cached prepared statements cannot retain the old row shape. No blind retry of
failed writes. Previous Registry7/Import8 runners retain their exact baselines;
the new owned localhost55436 runner alone exercises target9. No VPS migration,
real import or publication follows from these checks.

## Historical Remaining Boundaries

COACH-1 itself did not include Admin UI; the subsequent COACH-2 link above owns
that completed local scope. No server migration, real data/import,
account/Calendar mapping, asset upload service or active Website importer.
The pure public_projection generator is tested; asset hash verification and
approved-source ingestion must be added before replacing static Astro data.
COACH-2 adds bounded management reads/history and minimal mutation responses.
Legacy detail responses and internal write aggregates still load all revisions;
load review of those paths remains necessary before productive management at scale.
Privacy erasure/exceptional hard delete needs a separate retention/admin contract;
it is deliberately not a normal business operation or API DELETE endpoint.

The earlier UI recommendation is completed by COACH-2. Current recommended
next slice is COACH-3A lossless import contract/synthetic dry-run; separate scope
approval and content/evidence decisions required, no real import/server/Website change.
