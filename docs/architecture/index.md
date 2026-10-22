# Architecture Router

| Topic | Canonical home | Purpose |
| --- | --- | --- |
| Context ownership | [Context policy](PROJECT_CONTEXT_POLICY.md) | Loading, updates and archive rules |
| Environment split | [Environment policy](environment-policy.md) | Production / preview / backend |
| Portal domain | [Domain model](portal-domain-model-v0.1.md) | Core entities and ownership |
| Auth | [ADR 0003](../decisions/0003-internal-authentication-and-session-model.md) | Session, MFA, role and CSRF decisions |
| MFA / Outbox | [ADR 0004](../decisions/0004-totp-cryptography-and-recovery-model.md), [ADR 0005](../decisions/0005-auth-token-delivery-and-idempotency.md) | Crypto and delivery |
| Portal UI | [ADR 0006](../decisions/0006-same-origin-pilot-portal-ui.md) | Same-origin protected frontend |
| Calendar | [CAL-1 technical design](calendar-cal1-technical-design-v0.1.md) | Load with targeted requirements/contract |
| Current Calendar acceptance | [22.10 access/batch report](calendar-cal1-access-batch-2026-10-22.md) | Local versus native evidence, one operator window and next gate |
| Backend package security | [22.10 dependency assessment](webapp-dependency-assessment-2026-10-22.md) | Cryptography advisory/limited reachability; no automatic waiver or major upgrade |
| Hosting | [Runtime decision](hosting-runtime-decision-2026-08-06.md) | IONOS static / independent VPS |
| Operations | [Operations index](../operations/index.md) | Runbooks and evidence |
