# Read-only Coach Registry Export

Status:03.11.2026 LOCAL/SYNTHETIC implementation and regression complete.
No real DB connection, server/container, secret, source document, account, import,
Website switch or deployment. Commit/push authorized after green checks only.
Implementation packaged as `f2a080d`; this document/checkpoint is packaged separately.

Update04.11: the separately approved owned native PostgreSQL probe now PASS,
including actual write denial, concurrent new-draft/child isolation, no-op xmin
and repeated COACH-4 parity. Container/port removed; [current evidence and pending
private operator gate](../operations/staging-resume-2026-11-04.md). The03.11
no-native-server statements below retain their dated evidence scope, not today's
latest acceptance. Real Staging/live export/source switch remain disabled.

## Boundary And Models

[Adapter](../../apps/webapp/src/competence_hub_api/portal/coach_export.py):
existing `CoachAggregate` / `ProfileContent` / COACH-3C models -> sealed canonical
in-memory snapshot -> either minimized internal review or existing COACH-4
publication filter -> unchanged public Projection schema1 -> existing Astro
consumer. No second Coach business model, import/revision/evidence synthesis,
fuzzy identity mapping, qualification inference or alternate diff engine.

The in-memory seal retains original typed content/topics/evidence so exact
subject hashes remain verifiable. It is never written or printed. The internal
review artifact deliberately omits private references and is **not** a round-trip
Registry dump or an authorization source for public exports. Do not sanitize
content, recompute approval hashes and treat the changed subject as approved.
Public modes filter the original validated canonical snapshot, not the redacted
administrative JSON. The artifact DTOs are transport schemas, not domain models.

Inputs are complete owned synthetic aggregates or the separately guarded borrowed
SQL connection below. No mutable paginated listing is accepted as a snapshot.
The sealed bytes are immutable; each consumer receives newly reconstructed existing
domain objects. Local capture double-checks mutation during copying; it is not a
transaction guarantee for arbitrary concurrently shared Python object graphs.

## Read-only And Consistency

`export_registry` has no repository, SQL connection, transport, actor, audit or
writer. It validates/reads only; asset bytes are never copied or changed. Only
the separate artifact writer creates exclusive generated JSON/manifest files.

The prepared SQL seam creates no engine and reads no configuration or credentials.
Before starting a transaction it accepts ONLY `postgresql+asyncpg`,127.0.0.1:55437,
DB `competence_hub_export_synthetic`, role `competence_hub_app`. Known VPS/tunnel,
real Staging/Production DB names and other roles/drivers are rejected. The CLI
and runtime do not wire this seam to any DB. No native SQL was executed here.

For that isolated future connection it requires an idle connection, begins a
dedicated transaction, sets `REPEATABLE READ READ ONLY` before data reads and
checks both transaction settings. The narrow reader exposes fixed parameterized
bounded SELECTs only; arbitrary SQL and create/edit/mutate fail before execution.
The DB read-only transaction is the second barrier against dependent write
attempts. Success, failure and cancellation always roll back. No row/advisory
locks, audit/ledger writes, revision, consent, publication or asset mutations.

There are13 fixed table reads plus2 control statements, independent of Coach
count; no per-Coach network queries. Rows are grouped once and reconstructed by
the **same** `PostgresCoachRegistryRepository.hydrate` used by ordinary reads.
Coaches use an explicit column list, not inherited contact/account columns.
Bounds:500 Coaches,5000 revisions,1000 publications,100000 rows per child table,
32MiB sealed snapshot,8MiB emitted artifact. Read limit+1; exceeded limits abort
the whole export, never truncate a successful artifact. Smaller deployment
limits may be chosen in a later separately reviewed live gate.

Fail closed on duplicate Coach/revision/evidence identities, invalid version or
revision numbers, multiple drafts, cross-Coach revision/child/qualification/format
ownership, missing publication revision or route mismatch, missing/orphan topic
snapshots/categories, duplicate topic/approval keys, unknown families or subjects,
and duplicate public profile paths across different Coaches. Historic paths can
repeat for the same stable Coach. Variants are typed nested children of an
existing family/format, not independently flattened cross-Coach references.
Snapshot topic names/categories are historic approved values; no current-taxonomy
rewrite or secret lookup is performed.

## Export Modes And Privacy

| Mode | Artifact / included data | Forbidden interpretation |
| --- | --- | --- |
| `internal` | `export_schema_version:1`, `artifact_kind:coach_registry_internal_review`; stable Coach UUID/lifecycle/version/floor, current revision and any separately referenced published/withdrawn revisions, profile/content hierarchy, topics, public/private qualification titles and visibility, approval-kind names, publication pointers | Not Website data, evidence interchange, backup or re-import |
| `preview` | Existing positive public COACH-4 allowlist and exact Preview evidence | No Production permission |
| `production` | Existing positive public COACH-4 allowlist and exact Production evidence | Never Preview fallback |

Internal data includes stable technical IDs only for legitimate reconciliation;
no actors, account data, audit/events, request IDs, source/evidence references,
private verification states/notes, protected original material or prices. Public
data additionally omits internal identities, private qualification titles and
approval metadata. Schemas reject nested unknown fields; internal review has a
separate output tree and is rejected by both public readers, including Astro.
New fields require deliberate allowlist review; model-wide serialization is not
used for emitted content. No customer/business registry, source ingestion or
price model is introduced. Human-reviewed free text remains a trust boundary:
allowlisting cannot detect a customer name or price inserted into an allowed
description. Existing content/privacy/object/environment approvals stay mandatory.

Only active, submitted, fresh and exactly approved published revisions are public.
Paused/inactive/archived/draft Coaches remain internal. New drafts do not replace
older valid published revisions. Reactivation retains the Coach identity and
needs the existing fresh-revision/approval contract. Production UNKNOWN without
publication is excluded; a claimed publication lacking exact evidence aborts
instead of silently falling back. See [Registry contract](coach-registry-contract-v0.1.md)
and [COACH-4 contract](coach-public-projection-contract-v0.1.md).

Families, formats, variants/add-ons, duration/display duration, delivery, target
groups, roles, competencies, explicitly public qualifications and relevant
boundaries retain their existing semantics. No role/method/topic becomes a
qualification. Therapy stays separate and nonbookable; moderation/mediation,
health promotion/treatment and Coaching/therapy boundaries are not collapsed.
Only permitted PNG/JPEG/WebP references within an explicit public-only asset tree
are accepted, with existing file/type/path/link/size/hash verification. Missing
portrait is valid. All modeled revision assets are verified, including internal/
inactive historic references: missing old files require deliberate reconciliation,
not silently skipping a broken Registry reference. No portrait extraction/copy.

## Determinism, Artifacts And Review

Canonical UTF-8 JSON: sorted object keys, no generated UUID/timestamp/file name.
Internal Coaches sort by stable UUID, revisions by number, topics by UUID;
role/qualification/family/format/variant ordering uses existing `ordering`, then
stable key. Category/topic-ID/scope/competency sets are sorted; assets use type/
reference. Existing sequence-only presentation/paragraph/boundary/target-group
arrays retain their declared editorial sequence, not alphabetic reinterpretation.
Public ordering remains exactly the existing COACH-4 contract. Evidence append
sequence is preserved for latest-decision semantics, not reordered by status/date.

Only local repository `.tmp/coach4/<run>/` output is supported by the writer:

- `private-internal/internal/coaches.json` plus `manifest.json`;
- `public/preview/coaches.json` plus `manifest.json`;
- `public/production/coaches.json` plus `manifest.json`.

Every existing ancestor is checked for symlink/junction/containment before writes.
Files are exclusively created, never replace a baseline. Artifact creation and
manifest creation are not a two-file filesystem transaction: I/O failure yields
no success receipt and may leave an incomplete private run. Do not consume it;
use a new run directory, do not overwrite it. A manifest binds schema, synthetic
fixture identifier, mode, fixed artifact filename, exact-byte SHA-256 and counts
for Coaches/revisions/roles/topics/qualifications/families/formats/variants/assets.
Public revision count0 means no revision objects emitted, not an empty Registry.
No timestamp is needed. No artifact is a release or rollback authorization.

The synthetic-only [CLI](../../apps/webapp/scripts/coach-export.py) accepts `--mode`,
`--output-root`, `--assets` only. Assets must already exist; it never creates them.
No apply/write/sync/DB/source-file option. Existing `coach-projection.py diff` /
`parity` consume the public outputs directly; no duplicate diff implementation.
Developer PowerShell, `apps/webapp`, no passwords/keys:

```powershell
$env:PYTHONPATH = 'src;.'
.\.venv\Scripts\python.exe scripts/coach-export.py --mode preview --output-root ../../.tmp/coach4/new-export-run --assets ../../.tmp/coach4/assets
Remove-Item Env:PYTHONPATH
```

Choose a fresh run path; the existing COACH-4 synthetic portrait tree must already
be present and match. No command here asks Manuel to reopen an operator window.

## Actual Local Evidence And Limits

New synthetic tests: [adapter acceptance](../../apps/webapp/tests/test_coach_export.py).
The strict SQL double exercises transaction ordering, write denial even when the
narrow capability is bypassed, rollback/cancellation, concurrent change isolation,
all-table batching, shared hydration, row ownership/incomplete reads and target
rejection. This is **not actual PostgreSQL isolation/SQL acceptance**. No server
or test container was started, consistent with this task's STOP boundary.

All three CLI modes actually generated; repeated Preview hash identical and the
existing diff tool reports no attention. Exact output hashes under ignored
`.tmp/coach4/export-adapter-20261103/`:

| Artifact | Coaches | SHA-256 |
| --- | --- | --- |
| Internal synthetic review |4| `c70d7160bfe8c8625bb4b5e19ffb99f9c8ba6c5b0b8f02bf20cffa6e2442058a` |
| Preview synthetic |2| `0b291f05dae76a776763b7626eebfd596b53b0d95553d68e5cc866f32c621c99` |
| Production synthetic |1| `9b3a22dcbde4bd7b290de291e5417e2fa3ffaaae2d0b6132d82875a80f27de83` |

Actual public output bytes match the prior `a4ba869` synthetic fixture too, not
just two calls to the new adapter. That fixture's missing `topic_ids` link is
corrected for complete canonical validation; public bytes remain identical.
The actual existing Astro loader accepts both new public files and rejects the
internal file. Website code/default data/routes are untouched. No browser repeat
is needed: no public structure, bytes or rendering changed; previous755 offline
Edge checks remain dated COACH-4 evidence, not rerun claims.

Full final regression:1303 PASS/29 expected opt-in skips, including91 new adapter
cases. Python compilation, dependency consistency and document integrity PASS
(7 archived files,21 routers,224 routed links). Website25 contract tests and Astro71 files/0
diagnostics PASS. Private JUnit: `.tmp/coach4/export-regression-final-20261103.xml`.
Current9-Coach private manifest raw SHA remains
`872b4df0610ae54ceec1688f323e4d99001befd87d7a3d2395a0001fc82c02fc`;
metadata hash checked only, no new real-source interpretation/import. Frozen
9 READY/0 REVIEW_REQUIRED/0 BLOCKED scope is retained, not freshly read from DB.
Becker's provisional details and all new rights remain outside that scope.

## Live Gate And One Next Local Block

Actual live export stays STOP until protected custody/current encrypted backup/
isolated restore, real Admin and approved nine-Coach import are proven, followed
by its own scoped read-only connection/role/selection/parity review. The fixed
synthetic target guard must not be removed as an incidental configuration tweak.
No key access, backup bypass, real mappings, migration, remote read/write,
Website source switch, Pages/IONOS/backend deployment or new feature is authorized.

The03.11 recommended local block was separately authorized and completed04.11:
owned disposable PostgreSQL16/schema9/loopback55437, actual write denial,
concurrent draft/children, deterministic parity and exact container/port cleanup
PASS. [Current single recommended protected block](../operations/staging-resume-2026-11-04.md#genau-ein-naechster-block)
is existing-key verification/current backup/restore/Admin with Manuel's private
terminal interaction and individual block approvals, not a repeated local probe
or real Coach APPLY. No live target guard has been relaxed.
