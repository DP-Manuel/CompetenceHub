# Post-Messe Restart Completion

Stand: 21.10.2026. Authorized scope complete; stop boundary reached.

## Result / Environments

| Environment | Result |
| --- | --- |
| IONOS production | Unchanged SB-54, source 1b4e33efa5e1; no SFTP, release or backend change |
| Official preview | https://dp-manuel.github.io/CompetenceHub/ published from b02ded1 |
| Portal/backend | Existing synthetic CAL-1 foundation, not productively activated |

Preview commit/push: b02ded1, Restore isolated post-Messe GitHub preview; exactly 41 scoped files.
[Existing manual Pages workflow 39632211909](https://github.com/DP-Manuel/CompetenceHub/actions/runs/39632211909) completed successfully.
No second deployment mechanism or environment-policy change was introduced.
The separate context migration/archives, requirements and Analytics documentation remain local/uncommitted, outside the narrow preview commit authorization.
Pre-existing .vscode and the untracked 25.09 weekly update were preserved.

## Context V2

Old default memory mixed state, active work and history across AGENTS/STATUS/PLAN/LOG, with another full-root read sequence in the external brief.
The conservative default baseline was 4 files / 5,420 lines / 399,927 bytes; the new default is two small files, approximately 98% fewer bytes. Exact final metrics come from scripts/validate-project-context.ps1.
This reduces mandatory context exposure, not merely filenames or disk size; no token-count precision is claimed.

Boot: AGENTS -> PROJECT_CONTEXT -> relevant domain index -> canonical task documents / active plan.
AGENTS owns durable rules/router; CONTEXT the current snapshot; STATUS compatibility; PLAN roadmap; active ExecPlan execution/horizon; LOG significant milestones only.
Seven original root files are SHA-256 preserved in docs/history/context-migration-2026-10-21, including the former external brief and full skill feedback.
Old AGENTS is a non-active snapshot filename; archive attributes preserve bytes across Git line-ending conversion.
No historical knowledge was deleted. Existing ADR/runbook/domain paths remain unchanged; prior deep knowledge is reconstructible from canonical files, hash-bound history and Git.
Architecture, requirements, content, operations and history indexes route small, distinct read sets.
No script/CI dependency on old root contents was found; root paths remain compatible and their consumers can follow archive pointers.
Cold-start test PASS: a fresh agent read only AGENTS and CONTEXT and correctly identified identity, milestone, production, active scope, protected actions, domain routing and next/stop boundaries.
Website feedback, CAL-1 and FIN-01 read-set tests are recorded in the [migration audit](../architecture/context-migration-audit-2026-10-21.md).

## Post-Messe Rebaseline

Manuel confirms Messe 17.10.2026 successful. Holiday cutlines, prior demo priorities and temporary Messe freeze are historical.
This does not invent a past Messe-preflight result or authorize a new production release.
The supplied feedback was triaged into [accepted requirements](../requirements/post-messe-product-2026-10-21.md); Manuel confirms no further Messefeedback currently exists.
Elisabeth spelling was explicitly clarified to Schwabauer; no source-directory access or real Coach UUID mapping was needed.
The [consolidation plan](../exec-plans/completed/post-messe-konsolidierung-2026-10.md) is completed; the [six-step backend horizon](../exec-plans/active/post-messe-backend-horizon-2026-10.md) distinguishes proposed execution, parallel organizational gates and product backlog.

## Preview Content / Product Contract

- Eight approved real Coach profiles are visible in preview; five historical portraits were restored from their exact Git blobs. Carolin retains an honest monogram because no portrait was supplied.
- Production still builds only its two real profiles and six explicit demos; preview-only routes and portraits never enter its artifact.
- Elisabeth has the 17 supplied titles in four keyboard-operable offer groups: talks 3, workshops 7, individual 5, further 2. No missing numbered item, clinical promise or new qualification is invented.
- Psychotherapie (HeilprG) remains a separate source mention with the existing Competence-Hub/Mindforge boundary.
- Personalentwicklung, Persoenlichkeitsentwicklung and Karrierecoaching are the three category IDs with German display names; Alle Themen is computed.
- Each canonical topic owns a categories array; the browser proves the same health topic works in two categories without duplicate source/DOM topics. Offer format, Coach and category remain separate.
- Manuela's preview Advisory href is https://advisory.donner-partner.de/; production retains its existing href.
- Every preview HTML page has noindex/nofollow/noarchive and the preview label. Production-equivalent canonicals stay on production; preview-only profiles omit nonexistent canonicals; preview sitemap is empty.
- Preview robots.txt blocks crawling, but a project-subpath robots file cannot govern the account root. Page-level noindex is essential; preview is public, not confidential.
- Calendar examples remain synthetic/non-binding and generated Coach links resolve; no productive API/form or analytics action was added.

## Verification

| Check | Actual result |
| --- | --- |
| Model/provenance/environment tests | 8/8 |
| Astro both modes | 58 checked files, zero errors/warnings/hints; 33 HTML pages each |
| Internal link/privacy gates | 1,237 production; 1,243 preview |
| Existing production Edge | 865/865 |
| Preview Edge | 1,213/1,213, 33 routes at desktop/390px/200%-equivalent reflow |
| Full production artifact comparison | 52/52 filenames and bytes identical to pre-edit baseline |
| GitHub Actions | Build and deploy success, run 39632211909 |
| Public preview Edge smoke | 205/205, all 33 routes plus actual filter/profile/offer/Advisory/calendar interactions |
| Browser failures / network | No JavaScript page/resource failure, no off-origin requests, no network writes in tested scope |
| Production spot-check, before and after | Mindforge HTML/CSS 200, exact September hashes retained |

Keyboard selection, visible focus, live result text, Many-to-Many membership, All, empty Mediation, source titles, images and runtime links were tested.
200% means 640 CSS pixels at device scale 2, equivalent reflow for a 1280px window; this is not automated browser-toolbar zoom.
Screenreader-facing roles/pressed state/status semantics were checked; no manual NVDA/VoiceOver speech test is claimed.
Local and public screenshots were visually inspected, including corrected category word fit.
Production filename-and-byte digest: 0a23f7f354cba72ac3a1f465ef709ebfba38055f723a01903433238b5feb5959; this is not a release ZIP hash.
Public report/screenshots: [public-smoke.json](../../release-artifacts/post-messe-preview-20261021/public-smoke.json) and [desktop screenshot](../../release-artifacts/post-messe-preview-20261021/live-directory-desktop.png).
Local QA is retained in release-artifacts/post-messe-preview-20261021/local-qa; generated evidence is ignored, never committed.

## Analytics Discovery / Privacy

[ANALYTICS-01](../requirements/analytics-01-discovery-2026-10-21.md) compares own aggregation, Matomo On-Premise and Plausible CE using current primary sources.
Recommendation: bounded aggregate counters on the existing backend, conditional on product/security/privacy/operations approval; no final tool decision is assumed.
Planned data: allowlisted page/event/target/category IDs, server day bucket and counters; no visitor/session ID, raw URL/query, form content, stored IP or user-agent.
Cookies, LocalStorage, SessionStorage and fingerprinting are not part of the proposed Level 1. IP still exists transiently at transport/security layers and hoster/log handling must be reviewed.
No reliable unique visitors, sessions, entry/exit journeys or average dwell time are promised without an additional measurement/privacy design.
Suggested 90-day aggregates and minimum counts are proposals, not approved retention rules.
PRIV-ANALYTICS-01 records consent as OFFEN. Product Owner, privacy/legal and operations review remain gates; no banner, collector, service, schema or tracking was activated.
The future cockpit is server-protected Admin-only; internal/Coach/reviewer/company-contact do not inherit global metrics.

## Current Backend / Remaining Gates

CAL-1 domain/repository, protected/public API, migrations 0005/0006 and the local Coach/Reviewer UI remain the accepted baseline.
Historical evidence is 384 local passes, 17 expected Staging skips, 17/17 native integration paths and a complete 26-point local browser checklist; no October database rerun is claimed.
Native Staging UI acceptance, app-origin/SMTP, real mailbox receipt, runtime/backup scheduling/alerts, named accounts/roles and productive data/activation remain open.
CAL-2 reservations and FIN-01 implementation are not started; Finance still needs bookkeeping discovery. PWA and deeper Analytics remain future scope.
Inherited npm advisories remain a maintenance item: 17 affected tooling packages (1 critical/11 high). The [scoped assessment](../architecture/preview-dependency-assessment-2026-10-21.md) found no reachable high/critical path in this static slice, not a patched dependency tree.

## Exactly One Recommended Next Backend Block

Native CAL-1 UI acceptance against isolated synthetic PostgreSQL Staging.
Purpose: verify the complete browser/session/role/revision flow against the already-proven native repository/API before broadening features.
Inputs: separate execution window approval, CAL-1 contracts/handoff, synthetic fixture and operator-supplied process configuration/tunnel.
Deliverables: browser acceptance/finding report, focused regressions if required, complete cleanup and service/network postflight.
Done: accepted cases pass, no real identities/mappings, zero test residue and unchanged co-hosted services. No further backend work was begun in this session.
