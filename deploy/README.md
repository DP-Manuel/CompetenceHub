# Deployment Templates

These files are secret-free examples for the controlled Competence Hub release.
They do not authorize or perform a deployment.

- `systemd/competence-hub-api.service.example`: dedicated FastAPI service.
- `systemd/competence-hub-token-worker.service.example`: one-shot E-Mail outbox
  worker; it fails closed unless all SMTP and encryption values are supplied.
- `systemd/competence-hub-token-worker.timer.example`: bounded worker schedule.
- `systemd/competence-hub-postgres-backup.*.example`: daily encrypted backup
  and freshness/integrity monitor units.
- `nginx/competence-hub-app.conf.example`: same-origin Portal/API reverse proxy.
- `postgresql/backup.conf.example`: secret-free backup policy and public GPG
  recipient fingerprint.
- `scripts/competence-hub-postgres-*`: backup, monitoring and isolated restore
  check commands. They are examples until separately installed and enabled.
- `scripts/pull-competence-hub-backup.ps1`: guarded Windows pull and checksum
  verification for a prepared encrypted export set.
- `website/sftp-target.example.json` and the Website rehearsal preparer: pin
  the verified SFTP target and validate a clean static artifact without opening
  a network connection.

Replace every `__PLACEHOLDER__` during a reviewed server installation. Runtime
secrets belong in `/etc/competence-hub/webapp.env` with owner-only permissions,
never in this repository. API and worker deliberately share only this external
configuration source; systemd must expose it to the dedicated service identity,
not to interactive users. Installing or enabling these examples requires a
separate reviewed deployment approval.

The executable release and rollback sequence is documented in
`docs/architecture/production-release-plan-2026-09-25.md`. Exact rehearsal
commands and stop criteria are in
`docs/architecture/webapp-release-rehearsal-runbook.md`. PostgreSQL backup,
restore and off-server transfer are documented in
`docs/architecture/postgresql-backup-restore-runbook.md`. Static Website SFTP
artifact validation, remote-inventory gates and backup-before-replace are in
`docs/architecture/website-sftp-release-rehearsal-runbook.md`; its preparation
script never opens a network connection.
