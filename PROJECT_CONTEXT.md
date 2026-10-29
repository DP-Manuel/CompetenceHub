# Competence Hub Current Context

Updated: 2026-10-29.

## Current Milestone

Post-Messe product consolidation is complete for the authorized scope: Context V2, official frontend preview and Analytics discovery.
The 17.10 Messe succeeded per Manuel; the temporary Messe freeze is historical.
The additive Calendar/native runtime, local security/Linux and synthetic COACH-1/2/3A/3C gates remain complete. COACH-3B business review closure:9 READY/0 REVIEW_REQUIRED/0 BLOCKED,0 canonical field loss and0 additional Manuel decisions. GO for the reviewed real-import scope pending separate execution approval; no DB access/import occurred. Exact counts/evidence/parity and the one-window runbook live in the [canonical migration plan](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md#coach-3b-reviewabschluss-2910). App-domain/TLS inputs remain open independently.

## Production State

- IONOS: https://competencehub.donner-partner.de/ remains at verified SB-54 source `1b4e33efa5e1` (25.09).
- Rights only29.10: Manuel explicitly approves Gülcan's profile/portrait and short offering descriptions for Preview and IONOS; [scope](docs/content/coach-publication-matrix-2026-09-24.md#zusätzliche-rechtefreigabe-gülcan-vom-29102026). No website release, full workshop scripts or unread details implied.
- 21.10 read-only checks before and after Pages publication: Mindforge HTML/CSS return 200 and match the September hashes; this is a spot-check, not a full production retest.
- Official preview: https://dp-manuel.github.io/CompetenceHub/ is published from `3e99e8e6151d` through successful Pages run39932275108 (23.10). Nine Preview Coaches, including Susanne's approved profile/portrait; actual public89 onboarding and134 Hub checks PASS. [Publication evidence](docs/content/susanne-klemm-preview-2026-10-23.md).
- Preview-only isolation: production's entire 52-file build manifest remains byte-identical; no IONOS write or backend deployment.
- Portal/backend is not productively activated; real accounts/mappings, reservations, SMTP and Analytics remain inactive.
- Production changes retain a separate release gate; [environment policy](docs/architecture/environment-policy.md) owns the three-environment decision.

## Current Evidence

- [Preview contract/QA](docs/architecture/github-pages-preview-2026-10-21.md): build isolation and local acceptance; [restart report](docs/handoffs/2026-10-21-post-messe-restart.md): successful Actions/public smoke and remaining work.
- [SB-54 handoff](docs/handoffs/2026-09-25-mindforge-notice-layout-p0-handoff.md) owns production release/rollback evidence.
- [CAL-1 handoff](docs/handoffs/2026-09-18-cal1-browser-acceptance-handoff.md) owns the dated September local UI scope; current October native proof is separate below.
- [Native UI preflight](docs/architecture/calendar-cal1-native-staging-ui-acceptance-2026-10-21.md) owns the authentication integration finding and actual check matrix; no Staging data was created.
- [22.10 access/batch report](docs/architecture/calendar-cal1-access-batch-2026-10-22.md): repaired native run from 87844d1 PASS, 142 browser checks, API gate and 424-test post-regression; 20 tables zero, six migrations/27 owner tables, four services active and PG localhost-only. Hash-bound metadata distinguishes real VPS persistence from untested Linux/proxy deployment.
- [CAL-1 readiness package](docs/operations/cal1-production-readiness-2026-10-22.md): deployment/migration/rollback/smoke plan and role/mapping/operations gates prepared; no installation, public backend exposure or real-data activation.
- [23.10 security/Linux close-out](docs/operations/cryptography-maintenance-2026-10-23.md): isolated compatibility and baseline rebuilds pass; fresh Linux install, actual proxy/auth/cookies and cleanup verified. Unit syntax is not VPS systemd activation. One consolidated EDV request; old vulnerable packages remain blocked.
- [COACH-1 contract](docs/architecture/coach-registry-contract-v0.1.md) and [ADR0008](docs/decisions/0008-coach-registry-and-static-publication.md): stable UUID, revision/lifecycle, independent publication/account/Calendar boundaries, local PostgreSQL and real MFA-backed Admin API proof. Migration0007 remains local; normal runtime Registry is unavailable by default.
- [COACH-2 UI contract/acceptance](docs/architecture/coach-admin-ui-contract-v0.1.md): native local PG/MFA/browser management, bounded reads/history, scoped actions, stale-edit/CSRF recovery,390px/native200% zoom and keyboard; all owned test resources removed. [COACH-3 plan/evidence](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md) owns inventory, real mapping decisions and synthetic import acceptance; [import contract](docs/architecture/coach-import-contract-v0.1.md) owns identity, normalization, revisions, read-only modes and atomic synthetic APPLY. Migration0008 is local only, no real import or Website switch.
- [29.10 preparation/matrix/runbook](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md#bestätigte-entscheidungen-vom-2910): immutable source keys, field/role/qualification/offer/asset/evidence rows, actual source quality, minimal target proposal, parity/rollback and conditional counts. Historical preparation only:0008 lacked the richer target;3C and the review closure below subsequently resolved the model and confirmed short-copy gates. No DB connection, real UUIDs or writes.
- [COACH-3C local target](docs/exec-plans/completed/coach-3c-target-2026-10-29.md): additive0009 preserves old rows/xmin; rich import repeats leave all tables/projection bytes unchanged. Native local Auth/MFA/Admin controls,390px/actual200%, keyboard/conflicts and private-evidence boundaries verified. The9-profile recheck validates827 source fields and preserves22 topic labels; no real UUID mapping, DB import, source read or Website change. Canonical contracts own fields/evidence; the plan owns current acceptance and limits.
- [COACH-3B review closure](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md#coach-3b-reviewabschluss-2910): immutable canonical/documentary input binding, all9 mappings READY,3 Gülcan families/5 additional short formats, independent environment rights and unknown original dates. Read-only live Preview comparison confirms9 profiles/30 qualification labels/25 baseline titles/8 asset hashes/22 topic links. Logical evidence candidates require real revision/topic-hash rebinding only inside the separately approved execution window; no real UUIDs allocated.
- [Susanne source/Preview evidence](docs/content/susanne-klemm-preview-2026-10-23.md): only the authorized Coach07 directory read; profile/both portraits explicitly approved for public Preview. Actual390px/native200%-zoom, taxonomy, links and52-file production isolation verified.
- [Context audit](docs/architecture/context-migration-audit-2026-10-21.md): hash-preserved history, small read sets and cold-start PASS.

## Protected / Current Blockers

Secrets, private sources, production systems and real Portal identities remain protected by AGENTS.
The completed synthetic gates and29.10 real read-only preparation do not authorize real import or production. This block changes neither public Preview nor IONOS; scoped commit/push is authorized, deployment is not.
Only Quellen/20261029 was newly authorized/read during the preceding preparation; neither COACH-3C nor this review rereads a source directory. Gülcan's2 replacement files remain optional for the now-reviewed short-copy scope, required for later full details. Known boundaries/unknown Live location/module details are correctly represented, not new blockers.6 unknown Production scopes remain unapproved without blocking Preview. Actual DB UUID/hash binding, backups and the real runner remain execution preconditions, not unresolved business decisions. The existing CLI is still synthetic-only; no guard bypass. Unconfirmed prices/protected sources/Susanne's new scan ideas are not imported.
SMTP/app-origin, mailbox receipt, backup scheduling/notifications, VPS systemd/public TLS and named-account gates remain unproven.
23.10 security-baseline packages are verified local candidates, not deployment authorization and not the later Registry release. No current COACH-1 deployment artifact/real Coach import is approved. All owned local test containers removed;20-table CAL-1 cleanup passed, Registry's whole disposable database destroyed.
The [toolchain assessment](docs/architecture/preview-dependency-assessment-2026-10-21.md) scopes inherited advisories; a separate maintenance upgrade remains backlog.
Existing SSH key works in two independent connections; no SSH/agent/host security changes needed. Native runner requests the two DB-role passwords only at local hidden prompts; never read credential files.

## Next Actions

1. Recommended next block: COACH-3B REAL APPLY, only after separate scoped approval. Inputs: frozen reviewed manifest, target/operator/window, protected backup/rollback and actual schema/topic/source preflight. Deliverable: locally prepared/reviewed real runner, then one approved server window with atomic import/repeat-zero/parity/Admin/CAL-1/health evidence; done when the runbook passes and stops before Website deployment. No real runner exists yet and no SSH/password action is needed now. Ordered horizon: [active plan](docs/exec-plans/active/post-messe-backend-horizon-2026-10.md).
2. Resolve parallel operational inputs when available; do not silently expand the UI gate.
3. Review [Analytics proposal and consent decision](docs/requirements/analytics-01-discovery-2026-10-21.md); architecture/retention remain proposals and consent is OPEN.
4. Any later IONOS promotion needs its own bundled review and production approval.

## Domain References

[Website/content/rights](docs/content/index.md) | [Portal/Auth](docs/architecture/index.md) | [Calendar/Finance/Future](docs/requirements/index.md) | [Operations](docs/operations/index.md).
[Roadmap](PROJECT_PLAN.md) | [History](docs/history/index.md).

## Explicitly Not Active

IONOS release, backend deployment, productive tracking, CAL-2, real reservations, FIN-01 implementation and PWA.
