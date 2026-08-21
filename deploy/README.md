# Deployment Templates

These files are secret-free examples for the controlled Competence Hub release.
They do not authorize or perform a deployment.

- `systemd/competence-hub-api.service.example`: dedicated FastAPI service.
- `systemd/competence-hub-token-worker.service.example`: one-shot E-Mail outbox
  worker; it fails closed unless all SMTP and encryption values are supplied.
- `systemd/competence-hub-token-worker.timer.example`: bounded worker schedule.
- `nginx/competence-hub-app.conf.example`: same-origin Portal/API reverse proxy.

Replace every `__PLACEHOLDER__` during a reviewed server installation. Runtime
secrets belong in `/etc/competence-hub/webapp.env` with owner-only permissions,
never in this repository. API and worker deliberately share only this external
configuration source; systemd must expose it to the dedicated service identity,
not to interactive users. Installing or enabling these examples requires a
separate reviewed deployment approval.

The executable release and rollback sequence is documented in
`docs/architecture/production-release-plan-2026-09-25.md`. Exact rehearsal
commands and stop criteria are in
`docs/architecture/webapp-release-rehearsal-runbook.md`.
