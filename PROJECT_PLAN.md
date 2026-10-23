# Competence Hub Roadmap

Updated: 2026-10-23. Current state belongs to [PROJECT_CONTEXT](PROJECT_CONTEXT.md); the next gate and rolling horizon belong to the [active plan](docs/exec-plans/active/post-messe-backend-horizon-2026-10.md).

## Vision And Ownership

Competence Hub connects companies and private clients with approved Coaches, qualification and development offers, supported later by an independent protected Portal.
Manuel owns product decisions and technical delivery; Janay owns commercial practice/review; EDV supports hosting and technical approval.
Donner + Partner operates the public Website; Lars Donner is responsible; central D+P legal pages remain the legal targets.

## Roadmap

| Phase | Outcome | Gate / evidence | Confidence |
| --- | --- | --- | --- |
| Post-Messe consolidation: complete | Stable IONOS, published preview, Context V2 and Analytics discovery | Completed scope, build isolation, public smoke | High |
| Backend continuation | Native CAL-1, cryptography maintenance and local Linux/proxy gates PASS | External domain/TLS/owners and separately authorized VPS rehearsal/activation remain | Medium |
| Coach Registry / lifecycle | COACH-1/2 and synthetic COACH-3A import/no-op/rollback verified; no real import | [COACH-3 plan/decision matrix](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md); real field/rendering, identity/evidence and server migration remain separate gates | Medium |
| Portal operation | Named accounts, mail, monitored backups, operational handover | DNS/SMTP/runtime/data/privacy/Go-No-Go evidence | Medium |
| Future calendar | CAL-2 reservations and provider-neutral .ics delivery | Business/concurrency/privacy/client-compatibility gates | Low |
| Analytics | Datensparse aggregate statistics in protected Admin cockpit | Architecture choice, privacy/legal and security approval | Medium |
| Finance | Outgoing company and incoming Coach invoice workflow | Bookkeeping discovery before specification/implementation | Low |
| Broader product | Requests, matching, documents, feedback, editorial workflows, PWA | Individually approved requirements and operations | Low |

## Execution Versus Product Backlog

Only the [active plan](docs/exec-plans/active/post-messe-backend-horizon-2026-10.md) selects the next proposed execution gate.
[Future ideas](docs/requirements/future-system-ideas-backlog.md), [FIN-01](docs/requirements/fin-01-invoice-management-epic.md) and [PWA strategy](docs/architecture/pwa-app-distribution-strategy-2026-08-11.md) remain product backlog.
Budget, new pilot date and ongoing content ownership are not yet confirmed.

## Constraints And History

Production/preview/backend policy: [environment policy](docs/architecture/environment-policy.md).
Domain gates: [requirements index](docs/requirements/index.md) and [operations index](docs/operations/index.md).
The successful Messe on 17.10.2026 closes the holiday/Messe planning phase; the temporary freeze is historical.
The full prior roadmap, detailed SB-01..54 history, decisions, risks and open questions remain in the [hash-bound prior plan](docs/history/context-migration-2026-10-21/PROJECT_PLAN.md).
Read historical sections only for the relevant domain; newer canonical decisions take precedence.
