# Competence Hub Roadmap

Priority: **WEBSITE FIRST; BACKUP KEY REBASE PAUSED** remains in force. The separately
authorized09./10.11 protected technical VPS pilot is now installed/accepted with
synthetic data only; this is not a general backend/real-account activation.
Preserve existing jobs/artifacts, do not resume GPG or repeat accepted backups.
IONOS retains its separate release approval; Preview stays public/approved.

Updated: 2026-11-10. Current state belongs to [PROJECT_CONTEXT](PROJECT_CONTEXT.md); the active technical-pilot horizon belongs to the [integrated Staging plan](docs/exec-plans/active/integrated-staging-pilot-2026-11-09.md#rolling-horizon). The [Website horizon](docs/exec-plans/active/coach5-offering-finder-2026-11-05.md#rollender-horizont) remains separate; real-user activation/import are held.

## Vision And Ownership

Competence Hub connects companies and private clients with approved Coaches, qualification and development offers, supported later by an independent protected Portal.
Manuel owns product decisions and technical delivery; Janay owns commercial practice/review; EDV supports hosting and technical approval.
Donner + Partner operates the public Website; Lars Donner is responsible; central D+P legal pages remain the legal targets.

## Roadmap

| Phase | Outcome | Gate / evidence | Confidence |
| --- | --- | --- | --- |
| COACH-5 / CAL demo |27 grouped offers/29 formats;1555 Website,76 local Calendar and141 public browser checks,37 CAL tests PASS | [Current scope/horizon](docs/exec-plans/active/coach5-offering-finder-2026-11-05.md); Pages78c3470 published; demo local, no real-data/IONOS activation | High |
| Website first | Approved static Preview offerings, Coach discovery and request UX;28 contracts/1377 local and171 public browser checks PASS | [Version inventory and sprint](docs/content/website-first-2026-11-05.md); Pages4daa9ad published05.11, IONOS unchanged | High |
| Post-Messe consolidation: complete | Stable IONOS, published preview, Context V2 and Analytics discovery | Completed scope, build isolation, public smoke | High |
| Private technical VPS pilot: accepted | Actual10.11 install,61 remote native MFA/RBAC/CAL/ICS/restart checks PASS; four synthetic users only | [Bound receipt/fresh SSH+HTTPS](docs/operations/integrated-staging-pilot-2026-11-09.md#echter-vps-pilot-abgenommen-am-10112026); no public ports/real accounts, fachliche Abnahme next | High |
| Coach Registry / lifecycle | COACH-1/2/3A/3C locally verified; COACH-3B review9 READY.30.10 approves Manuel as sole admin-only Staging operator; preparation locally verified, human window pending | [Current batch](docs/exec-plans/active/backend-sprint-2026-10-30.md); exact encrypted backup/restore before bootstrap, native MFA/recovery, actual target/topic gates before separate real APPLY; no real execution yet | Medium |
| Portal operation | Named accounts, mail, monitored backups, operational handover | DNS/SMTP/runtime/data/privacy/Go-No-Go evidence | Medium |
| Future calendar | CAL-2 reservations and provider-neutral .ics delivery | Business/concurrency/privacy/client-compatibility gates | Low |
| Analytics | Datensparse aggregate statistics in protected Admin cockpit | Architecture choice, privacy/legal and security approval | Medium |
| Finance | Outgoing company and incoming Coach invoice workflow | Bookkeeping discovery before specification/implementation | Low |
| Broader product | Requests, matching, documents, feedback, editorial workflows, PWA | Individually approved requirements and operations | Low |

## Execution Versus Product Backlog

The [current pilot horizon](docs/exec-plans/active/integrated-staging-pilot-2026-11-09.md#rolling-horizon) selects fachliche Abnahme using the installed synthetic VPS pilot. The [Website horizon](docs/exec-plans/active/coach5-offering-finder-2026-11-05.md#rollender-horizont) and later [backend horizon](docs/exec-plans/active/post-messe-backend-horizon-2026-10.md) remain separate, not a reason to resume GPG work or real import.
[Future ideas](docs/requirements/future-system-ideas-backlog.md), [FIN-01](docs/requirements/fin-01-invoice-management-epic.md) and [PWA strategy](docs/architecture/pwa-app-distribution-strategy-2026-08-11.md) remain product backlog.
First real coaching engagement:19.11.2026, business milestone only; no customer identity/data or invoice implementation. Manuel's Coach profile is a later standard post-migration onboarding case, not a tenth record in the reviewed batch. Janay unavailable approximately two weeks; prepare coherent blocks without new stakeholder decisions. Budget, broader pilot date and ongoing content ownership are not yet confirmed.

## Constraints And History

Production/preview/backend policy: [environment policy](docs/architecture/environment-policy.md).
Domain gates: [requirements index](docs/requirements/index.md) and [operations index](docs/operations/index.md).
The successful Messe on 17.10.2026 closes the holiday/Messe planning phase; the temporary freeze is historical.
The full prior roadmap, detailed SB-01..54 history, decisions, risks and open questions remain in the [hash-bound prior plan](docs/history/context-migration-2026-10-21/PROJECT_PLAN.md).
Read historical sections only for the relevant domain; newer canonical decisions take precedence.
