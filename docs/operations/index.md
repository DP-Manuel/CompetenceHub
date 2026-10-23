# Operations Router

| Topic | Canonical home | Purpose |
| --- | --- | --- |
| Environment boundaries | [Environment policy](../architecture/environment-policy.md) | Preview does not authorize production |
| Production checkpoint | [SB-54 handoff](../handoffs/2026-09-25-mindforge-notice-layout-p0-handoff.md) | Source/artifact/hash and rollback evidence |
| Release/operating history | [Evidence index](go-live-evidence-index.md) | Dated proof, not current uptime |
| Website SFTP | [SFTP runbook](../architecture/website-sftp-release-rehearsal-runbook.md) | Backup, two-terminal workflow, upload/rollback |
| Backend packaging | [Webapp rehearsal](../architecture/webapp-release-rehearsal-runbook.md) | Synthetic installation/health/rollback |
| Current CAL-1 readiness | [22.10 readiness package](cal1-production-readiness-2026-10-22.md) | Native gate closed; input matrix and Linux/proxy rollout/rollback gates, not execution approval |
| Linux/proxy preparation | [22.10 Linux report](cal1-linux-proxy-readiness-2026-10-22.md) | Domain/TLS/port/package/templates, actual versus blocked local smokes and consolidated inputs |
| Security maintenance / local Linux proof | [23.10 close-out](cryptography-maintenance-2026-10-23.md) | Cryptography50.0.2, reproducible baseline, actual local proxy/auth proof and one EDV request; no VPS deployment |
| Backup/restore | [Backup runbook](../architecture/postgresql-backup-restore-runbook.md), [Wuerzburg evidence](sb23-wuerzburg-execution.md) | External exact-copy restore and remaining scheduling gates |
| Roles/notifications | [Operating decisions](pilot-account-operations-decisions-2026-09-11.md) | Manuel, Janay, Thomas and notification boundary |
| Activation inputs | [Input contract](../requirements/activation-input-contract-2026-08-24.md) | Required DNS/SMTP/runtime/data inputs |
| Previous holiday handover | [Messe handover](../handoffs/2026-09-25-website-messe-handover.md) | Historical incident procedure; freeze window ended |
