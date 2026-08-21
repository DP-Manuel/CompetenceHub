# Webapp Release Rehearsal Runbook

Stand: 21.08.2026

This runbook covers a controlled rehearsal for the Competence Hub API and
token-delivery worker. It does not authorize DNS changes, SMTP delivery,
production accounts, real data or deployment. Commands use placeholders and
must be reviewed against the target host before execution.

## Release Contract

The release ZIP contains:

- the versioned application wheel;
- exact runtime dependency versions;
- migrations and database smoke scripts;
- systemd and Nginx templates;
- the production release plan and this runbook;
- an internal file inventory with SHA-256 hashes.

The accompanying `.sha256` file verifies the complete ZIP. Dependencies are
version-locked but are not yet shipped as an approved Linux wheelhouse. A
reviewed, hashed Linux wheelhouse or an approved package-index installation is
therefore still a production gate.

## Required Decisions and Inputs

- approved app hostname, DNS target and TLS issuance path;
- dedicated internal loopback port;
- SMTP host, port, TLS mode, authentication identity, authorized From and
  monitored Reply-To addresses;
- database name and restricted runtime/migrator roles;
- dedicated Linux identity `competencehub`;
- approved release artifact hash and previous release ID;
- external restore evidence and an available rollback owner.

Secret values are entered interactively into the root-controlled server
configuration. They must not appear in Git, shell history, tickets, e-mail or
the release archive.

## 1. Verify and Stage the Artifact

Run from the directory containing the ZIP and checksum file:

```bash
sha256sum -c competence-hub-webapp-<version>-<commit>-<timestamp>.sha256
unzip -p competence-hub-webapp-<version>-<commit>-<timestamp>.zip MANIFEST.json
```

Expected: `OK`, the approved commit, `dirty: false` and
`deployment_authorized: false`. The latter is deliberate: deployment needs a
separate human approval even when the artifact is valid.

Create a release-specific directory without changing the active symlink:

```bash
export RELEASE_ID='<version>-<commit>'
sudo install -d -o root -g root -m 0755 /opt/competence-hub/releases
sudo unzip -q competence-hub-webapp-<version>-<commit>-<timestamp>.zip \
  -d "/opt/competence-hub/releases/${RELEASE_ID}"
sudo chown -R root:root "/opt/competence-hub/releases/${RELEASE_ID}"
```

## 2. Build the Release-Specific Runtime

Use Ubuntu's supported Python 3.12 runtime. Do not reuse the Chatbot virtual
environment.

```bash
sudo python3.12 -m venv "/opt/competence-hub/releases/${RELEASE_ID}/venv"
sudo "/opt/competence-hub/releases/${RELEASE_ID}/venv/bin/python" -m pip --version
sudo "/opt/competence-hub/releases/${RELEASE_ID}/venv/bin/python" -m pip install \
  -r "/opt/competence-hub/releases/${RELEASE_ID}/requirements-production.lock"
sudo "/opt/competence-hub/releases/${RELEASE_ID}/venv/bin/python" -m pip install \
  --no-deps "/opt/competence-hub/releases/${RELEASE_ID}/packages/competence_hub_api-<version>-py3-none-any.whl"
sudo "/opt/competence-hub/releases/${RELEASE_ID}/venv/bin/python" -m pip check
```

Expected: installation succeeds and `pip check` reports no broken
requirements. Stop if an unapproved package source, unexpected version or
dependency conflict appears.

## 3. Prepare External Configuration

The API and worker share `/etc/competence-hub/webapp.env`. The file remains
outside every release and is read by systemd. Create it only during the
approved rehearsal with owner `root:root` and mode `0600`.

Required API names:

```text
COMPETENCE_HUB_DATABASE_URL
COMPETENCE_HUB_ALLOWED_ORIGIN
COMPETENCE_HUB_SESSION_IDLE_MINUTES
COMPETENCE_HUB_READINESS_TIMEOUT_SECONDS
COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY
COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY
COMPETENCE_HUB_OUTBOX_KEYRING
COMPETENCE_HUB_OUTBOX_ACTIVE_KEY_VERSION
COMPETENCE_HUB_COMPROMISED_PASSWORD_FINGERPRINTS_PATH
COMPETENCE_HUB_TOTP_KEYRING
COMPETENCE_HUB_TOTP_ACTIVE_KEY_VERSION
COMPETENCE_HUB_RECOVERY_HMAC_KEYRING
COMPETENCE_HUB_RECOVERY_HMAC_ACTIVE_KEY_VERSION
```

Additional worker names:

```text
COMPETENCE_HUB_ACCOUNT_ACTION_BASE_URL
COMPETENCE_HUB_SMTP_HOST
COMPETENCE_HUB_SMTP_PORT
COMPETENCE_HUB_SMTP_TLS_MODE
COMPETENCE_HUB_SMTP_USERNAME
COMPETENCE_HUB_SMTP_PASSWORD
COMPETENCE_HUB_SMTP_FROM
COMPETENCE_HUB_SMTP_REPLY_TO
```

`COMPETENCE_HUB_ALLOWED_ORIGIN` is the exact HTTPS app origin without a path.
`COMPETENCE_HUB_ACCOUNT_ACTION_BASE_URL` is the same origin ending in
`/portal/`; startup rejects a cross-origin action URL. Key values are generated
independently, versioned and never reused
across purposes. The compromised-password fingerprint file is external,
absolute, non-empty and readable by the service.

## 4. Database Gate

Before applying any migration, take and verify a database dump. Query
`competence_hub.schema_migrations` and apply only missing, approved migrations
in numeric order with the migrator role and `ON_ERROR_STOP=1`. Migration
`0001` through `0004` are already present in Staging as of 21.08.2026 and must
not be replayed there.

The included `bootstrap-staging.sql` is reference material for the isolated
Staging setup. It is not a production bootstrap and must not be executed in a
production database.

After migration, run its matching smoke SQL, confirm all application tables
are owned by `competence_hub_owner`, and verify that the runtime role cannot
create schemas or read `schema_migrations`.

## 5. Validate Service and Proxy Configuration

Copy the templates to a review directory, replace every `__PLACEHOLDER__`, and
validate before touching active units:

```bash
grep -R '__[A-Z_]*__' /path/to/rendered/competence-hub-*
sudo systemd-analyze verify /path/to/rendered/competence-hub-api.service
sudo systemd-analyze verify /path/to/rendered/competence-hub-token-worker.service
sudo systemd-analyze verify /path/to/rendered/competence-hub-token-worker.timer
sudo nginx -t
```

Expected: `grep` returns no placeholder, systemd reports no unit errors and
Nginx configuration is valid. The app binds only to `127.0.0.1`; PostgreSQL
continues listening only on localhost.

## 6. Activate for Rehearsal

Record the current target first, then switch the release symlink atomically:

```bash
readlink -f /opt/competence-hub/current || true
sudo ln -sfnT "/opt/competence-hub/releases/${RELEASE_ID}" /opt/competence-hub/current
sudo systemctl daemon-reload
sudo systemctl restart competence-hub-api.service
sudo systemctl start competence-hub-token-worker.service
```

Enable the worker timer only after a successful one-shot delivery test against
an approved synthetic mailbox. Enabling the timer or Nginx site is a separate
deployment action.

## 7. Smoke and Residue Checks

Verify direct loopback first, then HTTPS through Nginx:

```bash
curl --fail --silent --show-error http://127.0.0.1:<port>/health/live
curl --fail --silent --show-error http://127.0.0.1:<port>/health/ready
curl --fail --silent --show-error https://<app-hostname>/health/ready
systemctl is-active competence-hub-api.service postgresql.service nginx.service dp-chatbot.service fail2ban.service
sudo journalctl -u competence-hub-api.service -u competence-hub-token-worker.service --since '-10 minutes' --no-pager
```

Then execute the synthetic invitation, password, TOTP, Recovery-Code, active
session, company/contact and logout acceptance path. Confirm no token, password,
cookie, personal payload or database URL appears in logs. Clean synthetic rows
and verify the outbox has no pending or failed residue.

## 8. Rollback or Stop

Stop and keep the previous release active if health/readiness, TLS, SMTP,
authorization, migration, backup, Chatbot health or secret handling differs
from the approved expectation.

For an application-only rollback:

```bash
sudo ln -sfnT /opt/competence-hub/releases/<previous-release-id> /opt/competence-hub/current
sudo systemctl restart competence-hub-api.service
sudo systemctl start competence-hub-token-worker.service
curl --fail --silent --show-error http://127.0.0.1:<port>/health/ready
```

Do not reverse database migrations blindly. Use the pre-migration dump only
after a documented restore/repair decision. Disable the timer if delivery is
unsafe, preserve operational evidence without secrets and record the Go/No-Go.
