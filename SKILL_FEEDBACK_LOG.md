# Skill Feedback Router

Updated: 2026-10-23. This file is on-demand, not part of routine boot context.

## Active / Open Proposals

[Full prior feedback](docs/history/context-migration-2026-10-21/SKILL_FEEDBACK_LOG.md) retains every proposal and its recorded status.
Project-local implementation does not mean a canonical CodexSkills proposal is closed.

| Proposal | Recorded state | Evidence home |
| --- | --- | --- |
| Actual text-line geometry, not only container bounds | Project regression implemented; global proposal open.23.10 additionally distinguishes unclipped glyphs from visible-overflow line boxes, and calibrates native zoom screenshots against physical CDP/PNG width | Archive: browser-visual-geometry; Susanne Preview QA |
| Clipboard passwords / two-terminal SFTP / ASCII paths | Project workflow implemented; global proposal open | Archive: sftp-one-terminal-ascii-path |
| Calendar-relative fixture acceptance | Project test corrected; global proposal open | Archive: browser-acceptance |
| Further proposed improvements | Review individual Status fields before promoting | Archive: Open Feedback |
| Current checkpoint versus full history | Proven root-context duplication; project migration implemented, reusable skill proposal open | Context policy and migration audit |
| Hash-preserved instruction archives | Use non-active snapshot filenames for old AGENTS and disable Git newline conversion; reusable proposal open | Context migration manifest and archive attributes |
| Batch authenticated operator windows | Prepare/rehearse locally, then one hidden-credential entry, native tests, cleanup, independent SQL/health before closing only owned tunnel; project runner implemented, global proposal open | 22.10 CAL-1 access/batch report and staging batch script |
| Authentication evidence versus fixtures | Follow actual Login/MFA/session admission, not only endpoint RBAC or fake browser success; project admission and real-PG harness implemented, global proposal open | CAL1-NATIVE-AUTH-01 and 22.10 access supplement |
| DB-clock authority in native browser tests | Sample actual DB clock; do not alter server time.23.10 public query at exact sampled now intermittently became past: use one sample and a valid future window, with101ms/30s regression. Global proposal open | 22.10 local rehearsal; native fixture public_query_window and regression |
| Semantic browser readiness | Native latency exposed network-idle/early-state assumptions; await real response and rendered state, not fixed sleeps; project assertions retained, global proposal open | CAL-1 shared browser helpers and native harness |
| Existing SSH capability before new setup | Two existing-key connections worked although agent disabled; do not create keys/change services unnecessarily; global proposal open | 22.10 access/batch report |
| Safe failure diagnostics and repair window | Type-only error lost exact assertion location; retain file/function/line without exception/locals. After verified clean failure, allow deliberate same-window R/Q retry rather than new credential round; project implementation, global proposal open | First 22.10 native attempt and repaired batch |
| Close the actual gate, not a larger deployment claim | 142 browser checks against VPS persistence plus API/cleanup PASS closes native runtime/UI, not Linux/systemd/public proxy/SMTP or real-data readiness. Follow-on readiness package records the difference; global proposal open | Verified 22.10 native reports and CAL-1 readiness package |
| Committed package allowlist and pre-install advisory gate | Project exporter/guard implemented.23.10 closure adds usage audit -> isolated patched-major trial -> crypto/full/native-local regression -> deterministic rebuild -> actual local proxy gate; never bypass guard or equate local evidence with VPS activation. Global proposal open | Backend assessment and23.10 security close-out |
| Coach source approval, publication and lifecycle are separate | Reusable candidate: concrete-source access -> privacy/issuer-attribution audit -> revision/environment approval -> preview -> independent production gate; stable UUID, no account/Calendar auto-grants, fresh reactivation approval. Global skills unchanged | ADR0008, Registry contract and Susanne source/QA report |
| Multi-tab auth, version conflicts and lost responses | COACH-2 native proof: another tab rotates CSRF; refresh once before writing but retain original optimistic version, never blind-retry mutations. Creation retains request identity across lost response. Include real Login/MFA and negative admission, not fake-session403 alone. Global proposal open | COACH-2 UI contract and native browser runner |
| Bounded views must retain authoritative action inputs | History pagination must not hide older still-valid activation evidence; bounded loader includes latest eligible revision plus selected/publication references. Browser readiness awaits rendered lists, not network idle. Capture scrolled fixed-element/zoom artifacts before diagnosing layout. Global proposal open | COACH-2 bounded-read and13-revision regression |
| Prove import no-op, do not only count entities | Compare all domain/ledger/audit rows and xmin; separate logical source IDs from revision snapshot rows. Inject cancellation/SQL failure after writes; preserve unknown historic dates and stop typed mapping gaps. Project implemented, global proposal open | [Import contract](docs/architecture/coach-import-contract-v0.1.md), [COACH-3 evidence](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md#coach-3a-nachweis) |

## Implemented / Historical

The archive's Implemented Feedback section preserves authoritative-clock-integration-tests and design-system-derivation.
Its Rejected Or Deferred section and all older evidence remain unchanged.
Do not copy all historical proposals into this router or change global skills without an actual skill task.
