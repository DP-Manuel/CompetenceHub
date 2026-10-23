# Post-Messe Backend Horizon

Updated: 2026-10-23. Status: security/local Linux gate, COACH-1 core and COACH-2 synthetic local UI accepted; COACH-3 inventory/plan complete, no import. Domain/TLS inputs and any VPS execution remain separate open gates.
The [authorized consolidation block](../completed/post-messe-konsolidierung-2026-10.md) is complete.
Current checkpoint: [PROJECT_CONTEXT](../../../PROJECT_CONTEXT.md). Synthetic Staging acceptance is authorized; production and real-data activation are not.

## Recommended Next Block: COACH-3A Import Contract / Synthetic Dry-Run

Purpose: resolve lossless content/evidence mapping before any real migration.
Inputs: [COACH-3 inventory/plan](../../architecture/coach3-existing-content-migration-plan-2026-10-23.md), COACH-1/2, explicit field/therapy/evidence decisions and next-slice approval.
Deliverables: binding mapping, typed validation, tested idempotent import ledger/behavior and synthetic local projection.
Definition of Done: repeat runs without duplicate identities/topics/offerings/revisions, conflict/asset/privacy tests and full loss report; no real records, server migration or Website changes.
No manual credential window now. Domain/DNS/TLS inputs progress in parallel using exactly the consolidated request in the [security close-out](../../operations/cryptography-maintenance-2026-10-23.md).

## Current Execution

- 23.10 security maintenance closed: isolated49->50.0.2 compatibility, reproducible baseline ZIPs, exact Linux wheel/advisory check and actual local HTTPS/auth/proxy test. Full evidence and hashes live only in the close-out above; no VPS installation.
- 23.10 COACH-1 local slice: existing Coach identity extended, migration0007 tested only in owned local PG, revision/lifecycle/scoped publication and guarded Admin API. Default runtime remains unconfigured; no real Coach import or account mapping.
- 23.10 COACH-2 local management accepted: [UI contract/evidence](../../architecture/coach-admin-ui-contract-v0.1.md), [completed execution](../completed/coach-2-local-admin-2026-10-23.md). Native local PG/MFA/browser, bounded reads/history, lifecycle/publication, keyboard/zoom and conflict recovery; containers/servers removed.
- 23.10 COACH-3 inventory/plan complete: nine public/canonical Preview Coaches, no Quellen access/import/UUID mapping. Lossless content/qualification/therapy/evidence decisions remain open before importer implementation or real data.
- Susanne's approved source/profile/portrait published in Preview only from3e99e8e6151d, Pages39932275108 PASS;89 public onboarding and134 public Hub checks PASS. [Content evidence](../../content/susanne-klemm-preview-2026-10-23.md) owns publication details. Production's52 build files remain byte-identical.

- Complete locally: admission policy/real Login-MFA-session wiring, unchanged internal contract, fixture honesty and regression; dated native evidence remains in the batch report. No migration.
- Complete Preview: topic Hub/progressive disclosure and geometry corrections first published from1cc481de9210 on22.10; retained and publicly reverified in the23.10 publication above. All52 production build files unchanged.
- Native VPS: repaired source 87844d1 completed 142 browser checks, the 17-test API gate, 424 local post-tests and every cleanup/SQL/health check. All 20 dynamic tables zero, migrations 0001-0006, 27 owner tables, four services active, PG localhost-only. Evidence files independently inspected and hash-bound.
- First native failure and slow-response harness repair remain historical in the batch report; no application authorization was weakened. Native evidence uses real VPS PostgreSQL, not a deployed Linux service/public proxy.
- Follow-on safe slice complete: CAL-1 readiness package with role/mapping/activation inputs, package/migration/rollout/rollback/smoke/operations contracts. Local Linux packaging/install/proxy now verified; actual VPS installation/public origin/TLS, backup notifications and mail remain unproven. No VPS deployment.
- Linux preparation: read-only domain/port/runtime/cert-timer metadata, explicit Git-source allowlist and fixed build backend, service/proxy/bootstrap templates, reproducible ZIPs and guarded local Ubuntu harness prepared. Actual check counts/hashes are owned only by the Linux report.
- Historical22.10 Ubuntu phase stopped at the advisory guard. The separately approved23.10 run subsequently completed local runtime/Nginx/unit-syntax checks; this is not VPS systemd activation or public TLS proof.
- Preserve dated September native API evidence and local browser checklist; do not convert them into October native acceptance.

## Ordered Rolling Horizon

| # | Intended outcome / status | Gate / dependency | Planned evidence | Confidence |
| --- | --- | --- | --- | --- |
| 1 | COACH-3A lossless import contract and synthetic dry-run / recommended, not yet implemented | Existing inventory, explicit field/therapy/evidence decisions and separate scope approval | Repeated runs without duplicates, bounded conflicts, asset hashes and local projection/loss report | High priority; medium confidence |
| 2 | Runtime/operations input closure / parallel, waiting inputs | Non-secret origin/DNS/TLS/port/path and owner/window decisions | Completed consolidated input matrix and dedicated rehearsal plan | High priority, external timing unknown |
| 3 | Controlled synthetic VPS Linux/proxy rehearsal / waiting external gate | Final domain/TLS/owners and separate execution approval; exact reviewed artifact, not automatic Registry promotion | Real unit/HTTPS/cookies, rollback, cleanup and co-host health in one prepared window | Medium |
| 4 | Portal activation review / waiting | Rehearsal from 3 plus backup/alerts/mail/privacy/real-role/onboarding gates | Separate Go/No-Go and exact source/artifact/operations scope | Medium-low |
| 5 | Analytics Level-1 local POC / provisional, separate | Architecture choice, metrics/retention and privacy gates | Synthetic minimization, no storage/identifier, abuse/RBAC tests | Medium-low |
| 6 | CAL-2 reservations discovery / future | CAL-1 closure and separate product approval | Business transitions, concurrency and privacy acceptance | Low |
| 7 | FIN-01 bookkeeping discovery / future | Bookkeeping participation and authoritative-system decisions | Approved requirements and finance role/data boundaries | Low |

## Parallel Organizational Gates

EDV app-origin/SMTP/sender, actual mailbox receipt, named accounts/roles, operational break-glass access, production backup scheduling and notifications remain unproven.
These are tracked separately from the recommended UI block; they are not implied prerequisites for every local synthetic task.
No new pilot deadline, budget or stakeholder meeting date is invented.

## Product / Maintenance Backlog Outside Current WIP

Additional Messefeedback: none currently available per Manuel; reopen only with a concrete authorized source.
Website toolchain: [17 advisory packages and scoped reachability assessment](../../architecture/preview-dependency-assessment-2026-10-21.md); deliberate upgrade/compatibility block before untrusted content, SSR or exposed development tooling.
Preview stakeholder review, later bundled IONOS promotion, .ics delivery, deeper analytics, PWA and broader request/finance automation retain separate gates.
The 21.10 preflight was analysis-only. The separately authorized 22.10 batch implements additive access and sanitized database-error logging hardening; neither is deployed to production. Native acceptance and the following readiness-preparation slice are complete. Further activation needs the explicit open inputs and environment-specific gates above.
