# Post-Messe Consolidation ExecPlan

Updated: 2026-10-21. Owner: Manuel / Codex. WIP: one integration block.
Status: authorized scope completed. Future steering is in the [backend horizon](../active/post-messe-backend-horizon-2026-10.md); no backend execution began.
Goal: Context V2, approved preview updates and Analytics discovery while IONOS remains stable.
Input: supplied 21.10 Context V2 and Product Addendum; no additional Quellen path authorized.

## Baseline / Closed Milestones

- Messe 17.10 succeeded per Manuel; holiday cutline, Messe-demo priorities and temporary freeze are historical.
- Last accepted Website production SB-54, source 1b4e33efa5e1; preview/runtime does not advance IONOS.
- CAL-1 domain/API and migrations 0005/0006 were proven on isolated Staging; local UI/browser gate accepted.
- Historical backend evidence: 384 local passes, 17 expected Staging skips, 17/17 native API paths; not rerun on 21.10.
- Native Staging UI, real identities/mappings, SMTP, runtime and productive calendar activation remain gated.
- Existing .vscode/ and 25.09 weekly update are user/unrelated working-tree state; preserve them.

## Ordered Rolling Horizon

| # | Outcome / state | Gate or dependency | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| 1 | Context V2 and rebaseline / done | Hash-preserved root history and compatibility | Seven archive hashes, 17 routers/97 links, cold start and three read sets PASS | High |
| 2 | Existing Pages preview restoration / done | Environment isolation, clean bounded publication | Existing workflow, separate builds and crawler gates PASS | High |
| 3 | Approved Coach/topic/content update / done | Supplied addendum; historical approved content only | Eight Coaches, 17 offers, many-to-many filters, Advisory verified | High |
| 4 | Preview QA and publication / done | Desktop/390/200%, keyboard/focus, public noindex; clean isolated worktree | b02ded1 pushed; Actions 39632211909 success; 205 public checks | High |
| 5 | ANALYTICS-01 discovery / done for scope | Primary-source comparison and privacy gates | Comparison/design/PRIV record complete; consent OPEN, tracking OFF | High |
| 6 | Native CAL-1 synthetic Staging UI / proposed next backend gate | Separate execution approval and operational preflight | Full session/RBAC/UI, zero residue, service health | Medium |
| 7 | Portal operation inputs / waiting, parallel organizational gates | EDV app-origin/SMTP, backup schedule/alert route, roles/onboarding | Dated inputs and E2E delivery/restore evidence | Medium |
| 8 | Broader product / future | Later approved CAL-2, FIN discovery, reporting decisions | Separate requirements and acceptance plans | Low |

## Feedback And Priority

New workstream: supplied post-Messe feedback, with accepted content distinguished from unverified further source material.
Priority: P0 production/privacy/security -> concrete authorized feedback -> public P1 -> accepted product slice -> future.
A feedback matrix is recorded in the product requirements. Manuel confirmed no additional feedback is currently available; no source blocker remains for the supplied scope.
The accepted preview chain proceeds without repeated permission; no hidden requirement decisions are invented.

## Tests And Gates

Context: archive hashes, router references, no mandatory history load, script compatibility, git diff --check.
Preview: Astro check; production/preview build/link verification; robots/noindex/canonical separation; no API writes or analytics.
Browser: desktop, 390 CSS pixels, 200% reflow, keyboard/focus, Coach routes, Elisabeth groups, category many-to-many and Advisory href.
Publication: isolated clean worktree, reviewed owned diff, approved public content only, existing workflow and public preview smoke.
Analytics: primary-source options, cookies/storage/identifiers/IP/retention/RBAC/security decisions, explicit legal uncertainty.
Production gate remains closed for this work.

## Definition Of Done / Stop

Context archived and navigable; checkpoint current; preview QA/publish evidence recorded; Analytics comparison/design/decision record complete.
No IONOS upload, backend activation, tracking, real accounts/mappings, migration change, CAL-2 or Finance implementation.
Then recommend one evidence-based backend slice and stop.

## Progress And Evidence

- Root snapshots created and SHA-256 verified before modification.
- Context migration validation passed: seven SHA-256 snapshots, 17 router files, 97 local links and git diff --check; mandatory boot 399,927 -> 8,192 bytes (98.0% reduction at this checkpoint).
- Analytics discovery and PRIV-ANALYTICS-01 are drafted: own aggregate counters recommended, no active tracking, consent OPEN; retention and architecture choice remain proposals.
- Independent cold-start test passed using only AGENTS + PROJECT_CONTEXT.
- 21.10 read-only production spot-check: Mindforge HTML (19,013 bytes, SHA-256 d51ad6e43ae75a10ba01d4e369dbc18451762f9bc041dbdf2560ab4eb3b3b786) and CSS (85,857 bytes, SHA-256 1cf1770b7dcd83e0a16afcca96876a1b9c6381a4500f938ae2900496890ee0dc) return 200 and are byte-identical to the September checkpoint. No remote mutation.
- Preview: Astro 58 files/no diagnostics in both modes; 33 pages each; 1,237 production and 1,243 preview internal references; 8/8 model tests, 865/865 production Edge and 1,213/1,213 preview Edge.
- The full production inventory is 52/52 byte-identical to the clean pre-edit baseline; filename-and-byte digest 0a23f7f354cba72ac3a1f465ef709ebfba38055f723a01903433238b5feb5959.
- Public smoke: 205/205 over 33 routes and desktop/390/200%-equivalent reflow; no page/resource failures, external requests or writes. Report: release-artifacts/post-messe-preview-20261021/public-smoke.json.
- The read-only production hashes were checked again after Pages publication and remained unchanged.
- Dependency audit: 17 affected tooling packages; bounded static reachability assessment recorded in the preview security document, no reachable high/critical path found for this slice. Toolchain upgrade remains maintenance backlog.
- Only the isolated preview slice was committed/pushed. Context migration, archives, requirements and Analytics docs remain local, outside the narrow preview publication authorization. No IONOS, Staging DB, real Portal data or tracking activation occurred.
