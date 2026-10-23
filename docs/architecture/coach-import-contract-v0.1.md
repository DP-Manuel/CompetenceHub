# Coach Import Contract v0.1

COACH-3A, 23.10.2026. Implemented for **synthetic local proof only**.
Real COACH-3B, server migration, account/Calendar mappings, static Website
integration and every deployment remain separate gates.

Owners: [Registry](coach-registry-contract-v0.1.md),
[Admin UI](coach-admin-ui-contract-v0.1.md),
[existing-content inventory/decision matrix](coach3-existing-content-migration-plan-2026-10-23.md).
Typed executable schema: [coach_import.py](../../apps/webapp/src/competence_hub_api/portal/coach_import.py).
Planner/adapter: [postgres_coach_import.py](../../apps/webapp/src/competence_hub_api/portal/postgres_coach_import.py).
No import HTTP API, automatic runtime activation or second Coach entity.

## Record And Mapping

| Section | Binding rule |
| --- | --- |
| source_identity | Immutable `(source_system, source_key)`; independent of display name, email, filename and current public route |
| expected_coach_id | Optional assertion against an existing import binding, never permission to adopt a legacy Coach |
| profile | Existing COACH-1 ProfileContent scalars: name, academic suffix, intro, description, background, explicit public path |
| topics | Explicit source reference and label -> reviewed canonical UUID, accepted aliases and exact category set |
| competencies / target_groups | Stable source item keys and public literal labels; never inferred from roles or qualifications |
| offerings | Stable item keys plus existing Offering: lecture/workshop/coaching/individual/other, title, description, active and explicit ordering |
| assets | At most one keyed portrait: existing Asset reference, actual SHA-256, alt text, active flag and environment scopes; no BLOB |
| qualifications / roles / boundaries | Separate keyed literal text, public/internal visibility; explicit reviewed representation or classified conflict |
| publication | Initial lifecycle intent, explicit environment set and separately keyed content/person/environment evidence |
| provenance | Opaque source_ref; optional observed_at and technical_revision are technical input metadata, never historical approval timestamps |

Children belong only to their typed sections, not duplicated inside profile.
Unknown fields are rejected. No silent dropping, truncation, inferred
qualifications, operative account roles or splitting of compound role text.
JSON active/ordering require actual boolean/integer scalars, not string coercion.
Maximum50 records/batch; existing field/collection bounds apply.

The reviewed mapping contract contains canonical topic rules, explicit literal
representation choices and an opaque review_ref. Defaults for roles,
qualifications and boundaries are **unmapped**. Public roles/qualifications may,
only under `literal_background_v1`, retain their exact strings under separate
background headings. Reviewed boundaries may use `literal_description_v1`.
Private/internal text has no supported destination and stops the record; it is
never appended to a public field. This is not a claim that current real profile
templates, quotations, language/format groups or external links are losslessly
renderable. Those gaps remain blocked before COACH-3B.

## Identity, Normalization And Hashes

First creation assigns a random Coach UUID and stores one unique source binding.
Later imports resolve only that binding; duplicate names are valid, duplicate
source identities are not. Explicit route slash normalization is allowed;
renaming a Coach never regenerates a slug. A bound route change or collision
requires review, never an automatically numbered alternative.

Normalize NFC, line endings, horizontal whitespace and empty optional text.
Sort semantic sets, keyed labels, explicit offer ordering, asset scopes, topic
snapshots/categories and JSON keys. Preserve paragraphs and literal meaning.
Curated topic aliases may differ by case/whitespace/hyphens; an unknown or
ambiguous alias conflicts rather than receiving semantic fuzzy matching.
No topic/category creation. The three category codes remain canonical and M:N;
"All topics" is never stored as a fourth category.

SHA-256 hashes cover normalized source content, mapped profile with **topic
name/category snapshots**, mapping contract and initial publication intent.
They support comparison, not a substitute for validation. Unknown source input
is still rejected on every run. Technical observation/run timestamps do not
enter the content hash. The opaque provenance source_ref is retained in the
ledger; changing only that reference updates technical metadata, not a revision.
Input technical_revision/observed_at are not copied into domain tables.

## Revision And Missing-Item Semantics

| Comparison | Action |
| --- | --- |
| New source identity, no conflicts | CREATE Coach and draft revision1; initial publication only under the explicit attestation contract below |
| Identical content, source and mapping | UNCHANGED: no domain, ledger, child, publication or business-audit writes |
| Same mapped profile, changed provenance/mapping metadata | METADATA: ledger hashes/reference only; no revision or business audit |
| Changed profile/topic snapshot; importer-owned revision still draft | EDIT_DRAFT using original optimistic version |
| Changed profile; previous revision submitted/abandoned | Exactly one new draft revision; no inherited approvals/publication |
| Concurrent/manual Registry change, foreign draft or lifecycle drift | STATE_CONFLICT; no overwrite or automatic reactivation |
| Previously imported keyed item absent | MISSING_ITEM_REVIEW_REQUIRED; keep existing state and block the whole batch |

Explicit `active:false` may deactivate an offering within a reviewed draft.
Removing/rekeying items, changing the initial consent intent or redirecting a
bound public route is not an implicit deletion/renewal workflow.

COACH-1 owns offers/assets as **revision snapshots**. A new profile revision
copies child snapshot rows, but does not create another logical source offering
or asset. `coach_import_items.logical_id` stays stable across revisions and
draft changes. Counts must distinguish canonical taxonomy rows, logical item
identities and physical snapshot rows. During draft editing existing COACH-1
may replace child rows; a genuine no-op does not call that writer at all.

## Publication, Assets And Lifecycle

Default lifecycle draft, unpublished. Initial active state requires an explicit
reviewed attestation mapping and content_review/person_consent evidence. Each
initial publication additionally requires its own preview/production evidence,
matching non-null environment, route and asset scopes. Preview never grants
Production. Changing imported content does not reuse old approvals or publish
the draft. Old published revision and its exact asset reference stay unchanged.

Evidence records retain source identity, Coach UUID, exact revision, kind,
environment, opaque evidence_source and historical_at, **nullable if unknown**.
recorded_at is technical import time. COACH-1's current attestation occurred_at
is deliberately separate, not relabelled as historical consent. Known historic
dates must have a timezone, normalize UTC and cannot be future dates.
No approval is synthesized from a flag, filename or existing public page.

No portrait is valid; Beta proves this. Verify actual supplied bytes against
the declared hash even when no asset is newly linked. Replacing bytes under a
previously used reference conflicts; provide a new explicit versioned reference
and retain old bytes for published revisions. This block validates references
and hashes, not storage deployment, image transcoding or real consent documents.

The importer never drives an existing Coach's lifecycle. The synthetic scenario
proves active2026 -> inactive2027 -> fresh reviewed revision/reactivation2028
through COACH-1, retaining the same UUID. An old import after manual lifecycle
changes conflicts and cannot re-enable a departed Coach or withdrawn publication.

## Transactions And Constraints

Whole bounded batch is atomic: shared source/path/taxonomy conflicts make partial
success misleading. VALIDATE is pure. Database DRY-RUN uses REPEATABLE READ,
READ ONLY; no ledger or audit logging there. APPLY takes a transaction-level
import lock, deterministic topic locks, source/Coach row locks and original
optimistic versions. The Registry adapter reuses that same connection; every
Coach/revision/approval/publication/item and audit write commits or rolls back
together. Domain rules remain in COACH-1.

[Local migration0008](../../apps/webapp/database/migrations/0008_coach_import_ledger.sql)
adds only `coach_import_sources`, `coach_import_items`, `coach_import_evidence`.
0007 alone cannot durably bind source identity, logical items or unknown historic
consent dates. Unique source/Coach/path/item identities, composite revision/Coach
FKs, append-only evidence grants and immutable identity triggers enforce the
contract. Path advisory locks serialize import versus Admin revision creation;
no blind release overwrite. Runtime has no hard-delete grant on the ledger.
Local migration only; VPS remains0006. Existing Calendar/Registry runners stay
at their explicitly reviewed0006/0007 baselines.

## Operator Workflow

CLI: [coach-import.py](../../apps/webapp/scripts/coach-import.py).
Default `validate`; optional `dry-run`; APPLY requires both `--local-database`
and `--synthetic-apply`. Only bundled Alpha/Beta/Gamma/Delta fixtures are exposed;
no file input, source directory, export of real payloads or account creation.
Without a DB, dry-run is labelled EMPTY_SYNTHETIC_MODEL_NOT_DATABASE, not native
persistence proof. Against a DB it reads the full actual Registry/ledger state.
Local targets require exact asyncpg app role, 127.0.0.1:55435 and the disposable
competence_hub_staging DB; VPS tunnel55432 and other hosts/roles/DBs fail closed.
The internal synthetic method also requires the synthetic namespace and an
active DB-backed Admin operator. A namespace is an execution guard, **not** an
automatic detector of real personal data. The CLI cannot ingest arbitrary data.

PowerShell, repo root (no secrets needed):

```powershell
$env:PYTHONPATH = (Resolve-Path '.\apps\webapp\src').Path
& '.\apps\webapp\.venv\Scripts\python.exe' '.\apps\webapp\scripts\coach-import.py' validate
& '.\apps\webapp\.venv\Scripts\python.exe' '.\apps\webapp\scripts\coach-import.py' dry-run
Remove-Item Env:PYTHONPATH
& '.\apps\webapp\scripts\run-coach-import-local.ps1' -PythonPath '.\apps\webapp\.venv\Scripts\python.exe'
```

Linux pure CLI, apps/webapp: `PYTHONPATH=src python3 scripts/coach-import.py validate`.
The disposable-container runner is PowerShell-specific; no Linux/VPS execution
is implied. It uses cached postgres:16-bookworm with --pull never, tmpfs,
loopback-only55435, random process-only passwords, explicit0001-0008 and exact
owned-container removal in finally. No user credential window, secret-file read
or persistent imported database. Error gates fail without printing DB details.

JSON reports show hashed record refs, CREATE/REVISION/EDIT_DRAFT/UNCHANGED/METADATA,
revision number, MATCH_ONLY taxonomy counts, offering count, portrait MATCH/SKIP
and classified conflicts. Mutation counts count **records**, not SQL statements.
Technical run_id/mode/start/finish/result is separate stdout JSON, not business
audit or a stored source payload. SQL/error text, URLs/passwords, source documents,
names, approval strings and full input objects are not echoed.

## Acceptance And Limits

Detailed actual results: [COACH-3 plan evidence](coach3-existing-content-migration-plan-2026-10-23.md#coach-3a-nachweis).
Unit/CLI tests cover normalization, ambiguity, strict fields, all conflict
classes, safe defaults/targets and planner ownership. Real PostgreSQL tests
cover repeat runs2/3, all-table row data **and xmin** equality, identical public
projection bytes, canonical taxonomy, revision/offer/assets/history, unknown dates,
metadata-only updates, parallel creation and complete rollback for exception,
cancellation and SQL failure. Constraint violations are exercised directly.
The original COACH-1 PostgreSQL gate is rerun because its adapter is shared.
All synthetic data are removed by destroying the whole owned tmpfs database,
not by disabling immutable-history guards. No real Coach or portrait imported.
