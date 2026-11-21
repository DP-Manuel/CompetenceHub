# V2 integrated product and pilot readiness

Scope: local synthetic integration only. Build on the accepted 20 November
workflow; no new booking, pricing or publication policy. IONOS, GitHub Pages,
VPS, real accounts, mail and the GPG key hold are unchanged.

| Step | Exit condition | State |
| --- | --- | --- |
| 1. Reconcile | Git, deployed reference and migration ledger distinguished from local state. | Local and recorded baseline checked; current VPS inventory blocked by access |
| 2. Close product gaps | Coach and reviewer can act from the same workflow; customers and operations see only their own scope. No extra workspaces or stores. | Passed |
| 3. Prove the workflow | One isolated local PostgreSQL run through Coach, Reviewer, two companies, Admin, public projection and restart. Include communication drafts without transport, desktop, 390 px, keyboard and 200% zoom. | 37 integrated checks passed |
| 4. Rehearse migration | Checksum and restore a populated V1.2-shaped dump into a separate local DB, preserve rows/rights/sequences, migrate atomically through 0012 and prove rollback on failure. | Passed in offline Linux; not independent live recovery |
| 5. Package and hand off | Exact-commit ZIP, offline install proof, one joint walkthrough with decisions and failure stops. | Reproducible ZIP and offline install passed |
| 6. Joint acceptance | Manuel and Frau Rappelt repeat the linked workflow from one command. No operational grant inferred. | Pending |
| 7. Pilot preparation | Reconcile EDV response and decide private TLS before expiry. Bind fresh baseline and independent recovery before separately approved clone or activation. | External/Owner gate |

See the [joint walkthrough and proof](../../handoffs/2026-11-21-v2-master-acceptance.md)
and [operating gates and EDV](../../operations/portal-v2-pilot-gates-2026-11-21.md).
The native restoration proof uses real dump bytes, a synthetic source and
preprovisioned roles in an owned disposable cluster; it cannot prove recovery
of an encrypted live backup on a different workstation.
