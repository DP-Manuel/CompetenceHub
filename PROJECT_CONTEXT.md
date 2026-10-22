# Competence Hub Current Context

Updated: 2026-10-22.

## Current Milestone

Post-Messe product consolidation is complete for the authorized scope: Context V2, official frontend preview and Analytics discovery.
The 17.10 Messe succeeded per Manuel; the temporary Messe freeze is historical.
The additive Calendar access path is implemented and locally green; the real-runtime/local-PostgreSQL rehearsal passed. First VPS attempt passed Coach MFA/resume, then failed during offer setup; cleanup/SQL/health PASS. A repaired native retry remains the gate, not another content approval.

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
- [CAL-1 handoff](docs/handoffs/2026-09-18-cal1-browser-acceptance-handoff.md) owns accepted local UI scope; prior native API/Staging evidence is dated, not rerun in October.
- [Native UI preflight](docs/architecture/calendar-cal1-native-staging-ui-acceptance-2026-10-21.md) owns the authentication integration finding and actual check matrix; no Staging data was created.
- [22.10 access/batch report](docs/architecture/calendar-cal1-access-batch-2026-10-22.md): 424 local tests, 17 expected skips, 57 visual checks, 142 real-runtime/local-PG browser checks and 17 local-PG integration tests. First VPS attempt: six checks then failure; independent 20-table zero residue/owners/migrations/health PASS. Slow-response harness repair locally reverified; native retry needed.
- [Context audit](docs/architecture/context-migration-audit-2026-10-21.md): hash-preserved history, small read sets and cold-start PASS.

## Protected / Current Blockers

Secrets, private sources, production systems and real Portal identities remain protected by AGENTS.
Public preview and the later synthetic CAL-1 Staging UI task are authorized; no real-data or production authorization follows.
Manuel confirmed no additional Messefeedback is currently available; Elisabeth's spelling is confirmed.
SMTP/app-origin, mailbox receipt, backup scheduling/notifications, runtime and named-account gates remain unproven.
The [toolchain assessment](docs/architecture/preview-dependency-assessment-2026-10-21.md) scopes inherited advisories; a separate maintenance upgrade remains backlog.
Existing SSH key works in two independent connections; no SSH/agent/host security changes needed. Native runner requests the two DB-role passwords only at local hidden prompts; never read credential files.

## Next Actions

1. Recommended next block: execute/inspect the single prepared native Staging batch. Exact operator commands, passwords-only-in-terminal warning and expected result are in the [batch report](docs/architecture/calendar-cal1-access-batch-2026-10-22.md). Purpose/DoD and six-step horizon are in the [active plan](docs/exec-plans/active/post-messe-backend-horizon-2026-10.md).
2. Resolve parallel operational inputs when available; do not silently expand the UI gate.
3. Review [Analytics proposal and consent decision](docs/requirements/analytics-01-discovery-2026-10-21.md); architecture/retention remain proposals and consent is OPEN.
4. Any later IONOS promotion needs its own bundled review and production approval.

## Domain References

[Website/content/rights](docs/content/index.md) | [Portal/Auth](docs/architecture/index.md) | [Calendar/Finance/Future](docs/requirements/index.md) | [Operations](docs/operations/index.md).
[Roadmap](PROJECT_PLAN.md) | [History](docs/history/index.md).

## Explicitly Not Active

IONOS release, backend deployment, productive tracking, CAL-2, real reservations, FIN-01 implementation and PWA.
