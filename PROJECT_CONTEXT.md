# Competence Hub Current Context

Updated: 2026-10-22.

## Current Milestone

Post-Messe product consolidation is complete for the authorized scope: Context V2, official frontend preview and Analytics discovery.
The 17.10 Messe succeeded per Manuel; the temporary Messe freeze is historical.
The additive Calendar access/native runtime gate is complete. Linux/proxy preparation now has allowlisted reproducible packages and reviewed templates, but the local Linux install/startup stopped on a cryptography dependency advisory. Next gate is separately reviewed dependency maintenance; app-domain/TLS decisions remain open in parallel. No VPS installation is authorized.

## Production State

- IONOS: https://competencehub.donner-partner.de/ remains at verified SB-54 source `1b4e33efa5e1` (25.09).
- 21.10 read-only checks before and after Pages publication: Mindforge HTML/CSS return 200 and match the September hashes; this is a spot-check, not a full production retest.
- Official preview: https://dp-manuel.github.io/CompetenceHub/ is published from `1cc481de9210`; topic Hub/satellites and home Bubble clearances now included. Eight approved real Coaches and prior approved content remain.
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
- [Linux/proxy preparation](docs/operations/cal1-linux-proxy-readiness-2026-10-22.md): proposed app hostname has no A/AAAA; 127.0.0.1:8001 free at read-only check; two identical clean-source ZIPs, hashes/pins and local Ubuntu tools prepared. Canonical results distinguish completed checks from blocked Linux runtime validation.
- [Backend dependency assessment](docs/architecture/webapp-dependency-assessment-2026-10-22.md): cryptography 49.0.0 advisory blocks candidate use; affected PKCS#7 path not found in current AES-GCM runtime. No waiver or major upgrade applied.
- [Context audit](docs/architecture/context-migration-audit-2026-10-21.md): hash-preserved history, small read sets and cold-start PASS.

## Protected / Current Blockers

Secrets, private sources, production systems and real Portal identities remain protected by AGENTS.
Public preview and the completed synthetic CAL-1 Staging UI task are authorized; no real-data or production authorization follows.
Manuel confirmed no additional Messefeedback is currently available; Elisabeth's spelling is confirmed.
SMTP/app-origin, mailbox receipt, backup scheduling/notifications, runtime and named-account gates remain unproven.
Both current Webapp ZIP samples and Linux wheelhouse are blocked test artifacts, not deployable/rollback candidates. The local container was removed; no DB/runtime/proxy smoke ran after the advisory stop.
The [toolchain assessment](docs/architecture/preview-dependency-assessment-2026-10-21.md) scopes inherited advisories; a separate maintenance upgrade remains backlog.
Existing SSH key works in two independent connections; no SSH/agent/host security changes needed. Native runner requests the two DB-role passwords only at local hidden prompts; never read credential files.

## Next Actions

1. Recommended next block: obtain separately scoped cryptography maintenance approval, reconcile a reviewed patched version/pins, prove crypto compatibility and affected regression, then regenerate/retry the local Linux package/proxy gate. Inputs/DoD are in the [dependency assessment](docs/architecture/webapp-dependency-assessment-2026-10-22.md); seven-step horizon in the [active plan](docs/exec-plans/active/post-messe-backend-horizon-2026-10.md). No SSH/password action is required now.
2. Resolve parallel operational inputs when available; do not silently expand the UI gate.
3. Review [Analytics proposal and consent decision](docs/requirements/analytics-01-discovery-2026-10-21.md); architecture/retention remain proposals and consent is OPEN.
4. Any later IONOS promotion needs its own bundled review and production approval.

## Domain References

[Website/content/rights](docs/content/index.md) | [Portal/Auth](docs/architecture/index.md) | [Calendar/Finance/Future](docs/requirements/index.md) | [Operations](docs/operations/index.md).
[Roadmap](PROJECT_PLAN.md) | [History](docs/history/index.md).

## Explicitly Not Active

IONOS release, backend deployment, productive tracking, CAL-2, real reservations, FIN-01 implementation and PWA.
