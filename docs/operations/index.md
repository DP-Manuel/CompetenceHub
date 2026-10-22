# Operations Router

| Topic | Canonical home | Purpose |
| --- | --- | --- |
| Environment boundaries | [Environment policy](../architecture/environment-policy.md) | Preview does not authorize production |
| Production checkpoint | [SB-54 handoff](../handoffs/2026-09-25-mindforge-notice-layout-p0-handoff.md) | Source/artifact/hash and rollback evidence |
| Release/operating history | [Evidence index](go-live-evidence-index.md) | Dated proof, not current uptime |
| Website SFTP | [SFTP runbook](../architecture/website-sftp-release-rehearsal-runbook.md) | Backup, two-terminal workflow, upload/rollback |
| Backend packaging | [Webapp rehearsal](../architecture/webapp-release-rehearsal-runbook.md) | Synthetic installation/health/rollback |
| Backup/restore | [Backup runbook](../architecture/postgresql-backup-restore-runbook.md), [Wuerzburg evidence](sb23-wuerzburg-execution.md) | External exact-copy restore and remaining scheduling gates |
| Roles/notifications | [Operating decisions](pilot-account-operations-decisions-2026-09-11.md) | Manuel, Janay, Thomas and notification boundary |
| Activation inputs | [Input contract](../requirements/activation-input-contract-2026-08-24.md) | Required DNS/SMTP/runtime/data inputs |
| Previous holiday handover | [Messe handover](../handoffs/2026-09-25-website-messe-handover.md) | Historical incident procedure; freeze window ended |
