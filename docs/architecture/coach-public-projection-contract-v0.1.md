# COACH-4: Static Publication Pipeline

Status:02.11.2026 local continuation. Real Registry import/Admin/backup remain
paused. No server, live export, public Preview update, IONOS release or actual
Coach10 creation. Authority/evidence scope: [execution plan](../exec-plans/completed/coach-4-local-readiness-2026-11-02.md).

## One Publication Boundary

Canonical Registry aggregate -> existing lifecycle/revision/environment/evidence
filter -> strict public DTO -> deterministic JSON plus verified local assets ->
explicit local Astro comparison build. Neither Astro nor browser connects to
PostgreSQL. No new API, no arbitrary Admin JSON export, no import side effect.

`generate_projection(coaches, environment)` reuses the existing
[Registry filter](../../apps/webapp/src/competence_hub_api/portal/coach_registry.py)
and [rich target allowlist](../../apps/webapp/src/competence_hub_api/portal/coach_target.py).
The new [export/review module](../../apps/webapp/src/competence_hub_api/portal/coach_projection.py)
requires an explicit `preview` or `production`. Only active Coaches with a
published, submitted, fresh and exactly approved revision are included. A
published-but-inconsistent row aborts the whole export, not a partial silent
success. Unknown/rejected Production evidence or Preview approval never grants
Production. Paused/inactive/archived Coaches are excluded; history is retained.

The export function takes an already obtained consistent Registry snapshot.
The03.11 [read-only export adapter](coach-read-only-export-contract-v0.1.md)
now seals existing aggregates, exposes a minimized internal review and reuses this
public filter unchanged. Its fixed local synthetic SQL seam is tested with a
transaction double, not actual PostgreSQL or a live DB CLI/session. Any later
real export still needs its own scoped target/read-only-role gate after actual
backup/restore/Admin/import; never concatenate mutable paginated reads and call
that a snapshot. Frozen simulation is not actual DB acceptance.

## Artifact And Assets

Schema1 contains exactly `schema`, `environment`, `coaches`. Coach fields are
positive public allowlists, recursively validated with unknown-field rejection.
No internal UUID, evidence/reference, source path, audit/import object, private
qualification title, verification state/note, protected original/worksheet or
price field. Missing portrait is valid. Public labels/roles/qualifications,
topic/category snapshots, grouped families/formats/options and boundaries are
retained; grouped formats do not also appear as standalone offerings. Therapy
remains a separate nonbookable domain, never a coaching format.

Free text is still human-reviewed public copy: field allowlisting cannot prove
that a person did not put an email, unapproved price or protected paragraph into
an allowed description. Exact revision/object/environment evidence and privacy
review remain mandatory, not replaced by keyword filtering or a generated PASS.
Astro renders literal text without `set:html`; HTTPS links and paths are checked.

Canonical UTF-8 JSON uses sorted object keys, route-sorted Coaches, sorted
noneditorial topic/category sets and stable editorial item order. No generation
timestamp or random identity enters the artifact. Equal state yields equal
bytes/SHA-256. Exclusive output creation never overwrites frozen/current JSON.
The reader rejects duplicate JSON keys, unsafe routes and nested unknown fields.

Assets are PNG/JPEG/WebP in explicit `images/coaches/...` paths, no traversal,
SVG/HTML, external URL or private-source filename. Verify actual bytes against
each submitted SHA-256 in a separately selected public-only tree. Reject link/
reparse paths, nonfiles, oversized images and mismatched bytes. Review dimensions,
alt text and actual image rendering too; hashes alone do not establish consent.

## Change Review

`projection_diff` compares same-environment public artifacts and reports added/
removed Coaches, changed profiles/topics/offerings/assets/routes and projection
visibility changes. High attention includes new/removed route or Coach, portrait,
offering boundary and therapeutic-content changes. Production visibility changes
are explicitly marked for approval review, not asserted to be approval events.
`review_markdown` provides a bounded human summary rather than raw profile JSON.
Incremental review additionally breaks down ADDED/REMOVED/CHANGED by profile
route for Coaches/profiles, qualifications, topics, offerings, assets, boundaries,
publication visibility and routes. These are route-level field changes, not
invented stable identities for public qualification items. Empty nested boundary
containers do not generate false additions. Source-ingestion evidence is owned
by the [incremental review](source-ingestion-20261030-2026-11-02.md).

Public JSON intentionally contains no UUID or approval history. A removed and
added route therefore cannot be automatically declared the same person. The
private in-process `registry_safety_report` compares real stable identities when
provided by the trusted Registry snapshot: route changes and Production approval
readiness gained/lost, even for unpublished profiles. It emits no identities or
evidence payload; keep the report private. No tool infers a qualification, UUID,
rights decision or redirect from a similar name.

Review route changes explicitly before publication: retain identity, new revision
and exact approvals; list old/new path, old cached/static links and rollback scope.
Plan a redirect through the existing release/.htaccess contract if required; no
new redirect infrastructure or automatic remote rewrite is introduced here.
Old assets/routes remain a separate deployed-byte cleanup responsibility.

## Local Commands

For developers only, PowerShell at `apps/webapp`, no passwords/real keys required:

```powershell
$env:PYTHONPATH = 'src;.'
.\.venv\Scripts\python.exe scripts/coach-projection.py synthetic --environment preview --output ../../.tmp/coach4/synthetic-preview.json --assets ../../.tmp/coach4/assets
.\.venv\Scripts\python.exe scripts/coach-projection.py synthetic --environment production --output ../../.tmp/coach4/synthetic-production.json --assets ../../.tmp/coach4/assets
Remove-Item Env:PYTHONPATH
```

Output parents must exist; use fresh filenames, not rerun-overwrite. The command
is deliberately named `synthetic`: its technical attestations are fake fixture
consent, never real publication proof. Existing synthetic assets are reused only
when their bytes match. No general JSON Registry-dump ingestion is offered.

For same-environment review use `diff --current <public.json> --candidate
<public.json> --output <new-report.md>` or `parity` with a new JSON-report path.
Never use Preview-vs-Production as a same-environment change review. Output is
local/private; neither command publishes. Preserve actual published release
manifests as the release baseline; this slice creates no new rollback target.

## Astro And Transition

The build-only [consumer](../../apps/website/config/coach-projection.mjs) is
opt-in via `COACH_PROJECTION_FILE` and optional `COACH_PROJECTION_ASSET_ROOT`.
It checks exact Website mode, DTO allowlists, routes and SHA-256 assets, restricts
input to repository `.tmp/coach4` and output to `apps/website/.tmp/coach4`, and creates parallel
`/projected-coaches/` comparison routes. It never replaces the existing Coach
routes, directory, Hub or production model in this phase. No dev/live ingestion.

1. Current phase1: manual static source remains canonical for published builds.
2. This phase2: generated artifact is compared in an isolated local build;
   default Preview/Production build and all existing public routes stay unchanged.
3. Future phase3: only after actual import/export parity, consistent real snapshot,
   asset verification, privacy/content/right review and release approval, adopt
   generated JSON as canonical build input across directory, details and Hub.
4. Future phase4: deprecate manual source only after proven rollback/transition;
   no deletion in this task. Calendar integration is a separate gate.

The local projection output must not be passed to Pages/IONOS release tooling.
Output stays INSIDE Astro's Website working directory: an outside-CWD output can
cause Astro to copy intermediate content/cache files into the build. The local
guard rejects outside-CWD destinations and linked output ancestors before any
build/empty operation; browser acceptance also rejects known cache artifacts.
Default push does not publish: the existing Pages workflow is manual only.
Static withdrawal affects the NEXT artifact; already served bytes require a
separately approved rebuild/deploy. No instant remote removal claim.

## Parity And Verification

`projection_parity` explicitly checks count/routes/names/topics/categories/
qualifications/offerings/assets/boundaries and full DTO. Differences are reported,
never converted to a synthetic PASS. The pure
[frozen comparison](../../scripts/coach4_frozen_parity.py) binds the exact30.10
review manifest, builds temporary in-memory simulated identities/evidence, and
compares generated JSON against the frozen reviewed DTO: Preview9/Production3,
all ten dimensions PASS. The reviewed short candidate includes the separately
approved additional formats; it is not a claim that the public23.10 Website has
those additions or that the VPS Registry now matches it. No private original is
read again. The sealed private manifest and generated artifacts stay out of Git.

Synthetic cases cover Preview+Production, Preview-only/unknown Production,
inactive/pause/return with same UUID and new revision, missing portrait, multiple
public qualifications, private verification, family/variants, protected source
references, nonbookable therapy, deterministic bytes, nested injection, unsafe
route/filename/links, asset mutation and readable diff. The real nine-Coach
post-import/live-public parity remains a later actual gate.

Final local test/browser/build-isolation evidence is recorded in the execution
plan. Historical Staging gates are not rerun or relabeled as this local result.

## Operations

[Normal onboarding](../operations/coach-post-migration-onboarding.md) and the
[blank worksheet](../content/coach-onboarding-template.json) prepare future
Coach10 without creating or prefilling a real person. UUID, accounts/roles,
operational Calendar mapping and public presentation remain independent.
Offboarding/return uses existing domain actions, no destructive SQL.
[Stick checklist](../operations/staging-stick-resume-checklist.md) owns the
compact manual restart; the [Admin runbook](../operations/staging-admin-bootstrap-2026-10-30.md)
owns preserved-custody verification and real backup/restore-before-write gates.

No Analytics expansion in this block: complete core/publication readiness first;
19.11 is an operating goal, not authorization for Customer-1, tracking or FIN-01.
