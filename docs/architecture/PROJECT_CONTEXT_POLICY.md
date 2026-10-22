# Project Context Policy

Effective: 2026-10-21. Primary home for context loading and memory ownership.

## Boot Sequence / Progressive Disclosure

1. AGENTS: project identity, durable boundaries, task router.
2. PROJECT_CONTEXT: current milestone, production checkpoint, blockers, next work.
3. One relevant domain index; then only the canonical documents and implementation needed for the task.
4. Active ExecPlan for substantial work. Read cold history only for a specific unresolved question.

Do not load full LOG/PLAN/STATUS, all ADRs, evidence or private sources as a routine precaution.
The local project policy specializes generic skill templates that recommend updating all root files.

## Context Tiers And Canonical Ownership

| Tier / information | Primary home | Update trigger |
| --- | --- | --- |
| Hot / durable operating rules | AGENTS | Changed boundary or workflow rule |
| Warm / current checkpoint | PROJECT_CONTEXT | Milestone, gate, central blocker, workstream or production-state change |
| Active execution and rolling 4-8-step horizon | docs/exec-plans/active | Task progress, evidence, dependency or sequence change |
| Long-term roadmap | PROJECT_PLAN | Product scope or roadmap change |
| Architecture decisions | docs/decisions ADRs; technical designs in docs/architecture | Accepted decision or design change |
| Requirements | docs/requirements | Supplied input reconciled into testable scope |
| Content/rights | docs/content | Approved facts, rights or publication boundaries |
| Operations | docs/operations; existing architecture runbooks remain canonical | Operational evidence or contract changes |
| Significant milestone log | PROJECT_LOG | Important decision, regression, gate, release |
| Cold context | docs/history, completed ExecPlans, dated handoffs, Git | Archive / completion |

STATUS is a thin compatibility pointer, never another current-state copy.
Indexes are navigation, not replacement specifications. Existing canonical runbooks and ADR paths are not renamed just to fit a new folder rule.
PROJECT_CONTEXT must never be the sole record of a permanent decision.

## Read Strategy Examples

- Website feedback: AGENTS + CONTEXT + content/index + authorized feedback + impacted source; environment policy for preview/release.
- CAL-1 continuation: AGENTS + CONTEXT + requirements/index calendar row + CAL-1 handoff/contract + affected implementation/tests.
- FIN-01 planning: AGENTS + CONTEXT + requirements/index finance row + FIN-01 epic + explicitly provided bookkeeping input.
These are distinct read sets; no full root history, unrelated Auth reviews or backup runbooks are required.

## Updating And Archiving

Replace current facts in CONTEXT; preserve superseded evidence in domain documents/history/Git.
Finish larger work by moving its ExecPlan to completed; keep unresolved work in a new bounded plan.
Hash-bind snapshots before substantial root migration. Verify complete byte preservation before replacement.
Historical documents keep their original wording and dates; supersession is stated in the current router.
Do not classify all locally implemented skill proposals as globally completed.
Keep feedback input separate from accepted requirements; source authorization and publication authorization are distinct.

## Compatibility And Verification

Retain root filenames and existing domain paths. Search scripts/tests/CI/helpers before removing any expected path.
Validate router targets, archive hashes, current-state consistency, representative read sets and cold-start comprehension.
Docs-only migration requires no full application suite; application work receives its own appropriate tests.
Measure mandatory default context separately from optional history and disclose byte/line approximation rather than claiming exact token savings.
