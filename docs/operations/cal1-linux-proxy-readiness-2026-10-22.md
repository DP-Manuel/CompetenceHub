# CAL-1 Linux / Reverse-Proxy Preparation

Date: 2026-10-22. Status: **PREPARED WITH OPEN GATES; LINUX RUNTIME DRY-RUN BLOCKED**.
Scope: local preparation only; Linux/proxy execution on the VPS is NOT authorized.
This document owns domain/TLS/port/package/service preparation.
The closed native runtime gate remains in the [acceptance report](../architecture/calendar-cal1-access-batch-2026-10-22.md);
the broader [production readiness gates](cal1-production-readiness-2026-10-22.md)
remain separate. No new product behavior, data, frontend or SMTP work.

## Target And Read-Only Findings

```text
Browser -> HTTPS app hostname :443 -> dedicated Nginx vhost
        -> HTTP 127.0.0.1:8001 -> competence-hub-api.service
        -> PostgreSQL 127.0.0.1:5432, isolated Competence Hub database/roles
```

The application port is between Nginx and the app, not a second hop after the
app. Portal assets and /api/v1 share the same origin. No new API subdomain/CORS
architecture is needed. IONOS Website and Pages preview remain untouched.

22.10 read-only SSH checks (existing key, no sudo/password prompts or writes):

| Fact | Observed / implication |
| --- | --- |
| Existing Chatbot | active, working directory /home/manuel/apps/dp-chatbot, user/group manuel; its configuration contents were NOT read |
| Listeners | Chatbot 127.0.0.1:8000; PG 127.0.0.1:5432; public 22/80/443 on IPv4/IPv6; local DNS resolver ports |
| Chosen internal app port | 127.0.0.1:8001, currently unused; matches the existing installation runbook's suggested separate port |
| Webapp process | Not installed/started by this task; future dedicated competencehub user, /opt/competence-hub tree and venv |
| VPS runtime | Ubuntu inventory baseline 24.04; observed Python 3.12.3, x86_64, Nginx 1.24.0 |
| Health | dp-chatbot/nginx/postgresql/fail2ban active |
| ACME | /usr/bin/certbot exists; certbot.timer active/waiting |
| Certificate directory metadata | /etc/letsencrypt root:root 0755; live/archive root:root 0700; no certificate/private-key or renewal config contents read |

Port availability is a point-in-time check, NOT reservation. Recheck all IPv4/
IPv6 listeners and the specific port immediately before the later start. On any
collision stop; do not kill another process or silently pick 8000/8080 instead.
Actual firewall rules and per-certificate renewal/hook/private-key metadata are
not proven by a timer/directory check; privileged review remains in the later
approved window, never permission widening to inspect a key.

## Domain And DNS Decision

The [sent EDV request](../architecture/edv-app-dns-smtp-request-2026-08-21.md)
and [pilot cutline](../requirements/pilot-cutline-2026-08-28.md) consistently name
`competencehub-app.donner-partner.de` as the proposed hostname, explicitly pending
Thomas Ross' DNS/TLS approval. No final approval was found. Do not promote the
example portal.competencehub.donner-partner.de from the task into a decision.

Current lookup: no A or AAAA for the proposed hostname through 1.1.1.1; A lookup
against authoritative ns1025.ui-dns.biz also returns name-not-found. A direct
VPS dig CAA query for donner-partner.de returned no value, which is not an EDV
issuance approval or proof about every inherited/alias policy at a future name.

Required change AFTER approval: A record for the final app hostname to
217.160.255.86, directly to the VPS, no IONOS forwarding or CNAME to the Website.
No AAAA until EDV confirms a routed/tested VPS IPv6 address and equivalent
firewall/proxy/TLS coverage. Preserve both existing public Website records.
Approved exact HTTPS origin then becomes COMPETENCE_HUB_ALLOWED_ORIGIN;
the worker action URL, when separately enabled, uses that same origin + /portal/.

## TLS Preparation

Use a dedicated VPS certificate/lineage after DNS and TLS responsibility are
confirmed. Do not copy the IONOS wildcard private key or assume its presence on
this VPS. No certificate order, ACME challenge or renewal dry-run was performed
against the VPS in this task. A disposable localhost self-signed test fixture
may be generated only inside the owned local container, never for the app name.

Preferred later sequence: dedicated HTTP-only ACME bootstrap vhost, controlled
webroot /var/lib/competence-hub-acme, certonly/webroot issuance after approval,
then reviewed TLS vhost and one validated reload. The bootstrap returns 503 on
all non-challenge paths, not a public Portal. Never use standalone ACME by
stopping the shared Nginx. Renewal must reuse the managed timer, verify the
specific new lineage, test renewal and validate its scoped reload hook. No
global plugin rewrite of the Chatbot site. DNS-01 is an alternative only if EDV
mandates it and provides an authorized separate credential strategy.

The template retains existing HSTS max-age=31536000 only on the TLS vhost;
no includeSubDomains/preload extension. New policy broadening needs review.
Nginx master must be able to read the restricted private-key file; the app user
does not need it. Future operator may verify stat/namei metadata, never copy
private key content to Git/chat. Confirm fullchain/SAN/expiry/trust and renewal
behavior, not merely that a file exists.

## Service And Proxy Templates

Keep existing names and paths instead of creating a competing webapp service:

- Unit: deploy/systemd/competence-hub-api.service.example, user/group competencehub.
- Release root: /opt/competence-hub/releases/<approved-release-id>; own venv.
- Active link: /opt/competence-hub/current; root-owned release/config, not Chatbot's venv.
- Configuration: /etc/competence-hub/webapp.env, server-only root:root 0600.
- Binding: --host 127.0.0.1 --port 8001; /health/live and DB-backed /health/ready.
- Restart=on-failure, delay 5 seconds, 60-second/5-start limit; journald identifier,
  explicit WorkingDirectory/ExecStart, existing filesystem/privilege hardening.
- Only loopback trusted for Uvicorn proxy headers. No wildcard trusted proxy.
- Dedicated Nginx app site and certificate bootstrap templates; no default-server
  takeover, Chatbot configuration edit or shared service identity.

At the public Nginx edge, overwrite Host/forwarded host with the configured
hostname, X-Forwarded-Proto=https, and X-Forwarded-For/X-Real-IP=$remote_addr.
Never append arbitrary client forwarding headers as an authoritative identity.
This assumes direct Internet -> Nginx; a later CDN/load balancer needs a separately
reviewed trusted-hop policy. Keep HTTP/1.1 upstream, 5-second connect/30-second
read/send timeouts and 32 KiB body limit. Preserve application CSP/no-store and
cookie headers without rewriting Domain, Path, Secure or SameSite.

Uvicorn and app-vhost access logging are off to avoid request-query/identity
leakage. Application errors use the already-sanitized journald path. Nginx error
logging/retention still needs host review for sensitive request-context leakage;
do not claim access_log off sanitizes all possible proxy error logs. No debug
headers or endpoint with environment/version/DB contents are introduced.

## Config Names, Network And Isolation

Only these existing API names are needed, values stay with the authorized operator:

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

Versioned per-purpose keys and compromised-password corpus are external; no
invented SESSION_SECRET/CSRF_SECRET setting. No EnvironmentFile with values is
generated here. Worker-only SMTP/action-base names remain in the existing
runbook; worker and timer stay inactive in this rehearsal scope.

Expected public exposure stays 22 under existing SSH policy and 80/443 for
Nginx. Never open 8001 or 5432 on IPv4 OR IPv6. Binding and firewall are separate
checks. No firewall or SSH changes in this task. Chatbot retains port 8000,
its own /home/manuel/apps/dp-chatbot tree/venv/unit/config/log namespace and
dependencies. No restart/reload of it, no dependency install into its venv.

## Release And Dependency Contract

Use scripts/build-webapp-release.ps1 from committed tracked inputs. It exports
reviewed files via scripts/webapp_release_source.py from Git bytes, not a
recursive worktree/deploy copy. Unknown .vscode/material stays untouched and
cannot enter the artifact. AllowDirty is explicitly development-only; never
select its dirty artifact as a rehearsal/production candidate. Git-export mode
does not assert that unrelated untracked workstation files do not exist.

Artifact: one application wheel including HTML/CSS/JS, runtime/build pins,
approved migrations/verification SQL, explicitly named operations templates/
tools and current CAL-1/runbook documentation. SOURCE.json binds original file
hashes to full commit; MANIFEST.json inventories bundle hashes/bytes and keeps
deployment_authorized=false. ZIP has its own SHA-256 and commit/version identity.
Excluded: .env/keys/credentials, Quellen, Website assets/SFTP tools, tests,
browser fixtures, local databases, bytecode and untracked files. Selected Git
symlinks/reparse-point development inputs are rejected before following them.

Python 3.12 is the Linux target, separate venv under each immutable release.
Runtime requirements-production.lock pins the complete dependency set; project
metadata ranges are NOT the installation lock. Build pins are pip 26.2.1 and
setuptools 79.0.1; pyproject build backend is pinned too. Wheel build is no-index,
no-deps, no-build-isolation against those tools. No global pip install/latest.

The local Ubuntu tool prepares exact Linux binary wheels from official PyPI,
cross-checks published SHA-256, emits a platform/Python-specific hashed lock and
records the PyPI advisory snapshot. Fresh runtime venv installation then uses
--no-index --only-binary=:all: --require-hashes and the reviewed app wheel.
Hashing a fresh download alone is not provenance approval; this snapshot is a
reviewable candidate, not an unrestricted future package-index permission.
No matching binary wheel, unknown version, advisory requiring review or hash
mismatch stops preparation. The same wheelhouse must be reverified on transfer.

Ubuntu base digest is pinned in deploy/rehearsal/Dockerfile. APT packages are
signature-verified Ubuntu packages but not a bit-for-bit frozen APT snapshot;
record actual image/runtime versions, do not claim that rebuilding that image
months later reproduces its package patch set. Rebuild two ZIPs from the same
commit/toolchain to measure artifact reproducibility, not merely assume it.

## Migration And Rollback

No new migration. Existing Staging 0001-0006 are never replayed there. The local
container alone may bootstrap its disposable database and apply those migrations.
Future production bootstrap/target/roles need their own approval; the packaged
bootstrap-staging.sql is reference only. Before any approved DB change: protected
pre-dump, hash/catalog validation, migration inventory, matching SQL smoke,
owner/runtime privilege check and post-dump.

Application rollback restores only a previously recorded compatible release
link; first-install rollback is back to the inactive baseline, not a fictional
previous backend. Restore only the candidate's backed-up Nginx/unit/link changes,
syntax-check before any approved shared Nginx reload, and stop/remove only owned
candidate processes. Code rollback is NOT a down-migration or DB restore.
Restore can lose later writes; it needs a separate repair decision, backup and
post-restore evidence. Preserve external key versions used by retained data.
See the broader readiness package for outbox side effects and Website boundaries.

## Local Dry-Run Contract

scripts/run-webapp-linux-dry-run.ps1 requires ConfirmLocalOnly, uses an existing
reviewed local image, no host mount or published port, exact owned container ID,
and finally removes only that container. No SSH/VPS command is part of it.
Download only public dependency artifacts in its preparation phase; disconnect
container networking before runtime/DB/proxy tests. Only generated synthetic
identities/MFA material live in its disposable filesystem/memory. Copy out only
sanitized result metadata and the public dependency wheelhouse.

The Ubuntu test verifies exact archive contents, fresh Linux venv/dependencies,
systemd-analyze verify and nginx -t, then starts the packaged real runtime,
disposable PostgreSQL and Nginx HTTPS locally. Exercise health, redirects,
spoofed forwarded headers, actual Coach/Reviewer password/TOTP/enrollment,
cookie flags, resume, Origin/CSRF, role isolation, logout and exact cleanup.
This cannot prove systemd PID-1 hardening activation, host firewall, public DNS,
trusted app certificate, renewal or real-user onboarding. Those remain later.

## One Future Server Window: NOT AUTHORIZED TO EXECUTE

1. Obtain scoped approval with exact artifact/hash, final hostname/TLS/port/path,
   synthetic-only DB scope, change window/owner and approved dependency source.
2. Open one key-authenticated SSH/operator window, record original service health,
   PG loopback and metadata-only unit/site/link baseline; do not read secrets.
3. Recheck port 8001 and host firewall rules; stop on conflict/exposure, never
   stop another process or open an application/database public port.
4. Transfer only the reviewed archive/wheelhouse; verify all SHA/inventory before
   extraction. Create dedicated inactive release directory and venv.
5. Validate Ubuntu/Python compatibility and offline hash-pinned installation;
   operator supplies root-controlled configuration separately in hidden input.
6. Confirm synthetic target/migration versions, protected backup and privilege
   boundaries; no unapproved bootstrap/migration or production role grants.
7. Render dedicated unit/site placeholders, verify systemd and Nginx syntax,
   record exact candidate paths and original symlink/absent-state rollback.
8. Install/start only the explicitly approved synthetic candidate on loopback.
   Poll /health/live and /health/ready with a bounded timeout.
9. After DNS approval verify A/AAAA/CAA; if new cert is required use the reviewed
   HTTP-only challenge configuration and scoped certonly/webroot procedure.
10. Verify SAN/chain/expiry/restricted metadata and the specific renewal hook.
    Activate only the authorized dedicated HTTPS proxy after nginx -t.
11. Run actual HTTPS Login/MFA/session/cookie/Origin/CSRF/redirect/forwarded-header
    and RBAC smokes. No worker/timer, live mail or real-user data.
12. Inspect sanitized errors/log behavior, exercise code/site/unit rollback to
    the recorded baseline, re-prove health and stop only owned test processes.
13. Exact-ID cleanup, independent SQL zero/baseline counts, migration/owner checks,
    four co-host service healths and PG loopback; never broad-delete real data.
14. Preserve sanitized evidence, remove only approved temporary candidate context
    and close only the owned window after cleanup/health. Stop if unproven.

## MANUEL / EDV INPUT REQUIRED

One consolidated input request, no password or server action now:

- Thomas/EDV: final app hostname; confirm or replace the existing proposal
  competencehub-app.donner-partner.de and approve A -> 217.160.255.86. No AAAA
  without a specifically confirmed IPv6 target and full-path test.
- Thomas/EDV: confirm VPS-managed dedicated certificate via existing Certbot/
  ACME renewal, any CAA/DNS restrictions and who owns issuance/renewal alerts.
- Existing /opt/competence-hub, /etc/competence-hub, competencehub identity and
  selected 127.0.0.1:8001 are the prepared convention. Manuel/EDV need only supply
  a different mandatory path/mirror if organisation policy requires one; no
  redundant separate confirmation of these technical defaults is requested.
- Manuel: separate execution approval naming artifact SHA, synthetic environment,
  window and rollback owner. This preparation authorization is not that approval.
- Manuel: separate dependency-maintenance approval for the reviewed cryptography
  major update before rebuilding/retrying the Linux runtime gate; see the
  [dependency assessment](../architecture/webapp-dependency-assessment-2026-10-22.md).
  No automatic exception or update was applied.

## Actual Local Results And Artifact Identity

Source/tool commit: cb95db017dc452380ce8d5ec81a89dca2eaff94a. The application
runtime implementation is unchanged from native acceptance; changes are
packaging/build metadata, infrastructure templates, tests and local tools.

- Full local regression: **450 passed, 17 expected Staging skips**. Targeted
  package/operations checks passed. Python compilation and PowerShell parsing
  passed. No additional VPS database/browser run was necessary for this scope.
- Git export selected 88 reviewed files; Windows wheel build, isolated package
  install/import/assets/fail-closed configuration smoke passed. No recursive
  deploy/worktree copy or untracked input was used.
- Two independent ZIP builds from the same commit/toolchain are byte-identical.
  Source manifest uses full Git commit; bundle manifest keeps dirty=false and
  deployment_authorized=false. The app wheel SHA-256 is
  901ee983550439a80d3e55eb7ded5dc367817e5cd8808f1ac9a6e5c134c13d40.
- Ubuntu image built locally from the pinned base, with Python 3.12/NGinx 1.24
  tooling. The preparation verified the exact ZIP inventory, downloaded the
  24 exact Linux runtime wheels and verified upstream hashes. It then stopped
  at the cryptography advisory guard BEFORE fresh runtime installation/startup.
- Therefore **NOT RUN**: Linux runtime venv install/pip check, systemd-analyze
  verify against installed executable, nginx -t with fixture TLS, actual Linux
  health/proxy/auth/DB cleanup tests. Templates have static/unit-test review,
  not a fabricated executed PASS. Their local harness is prepared, not proven
  end-to-end until the dependency gate is resolved.
- Container removal PASS, confirmed no remaining owned Linux-dryrun container.
  No host mount/published port, VPS install, DB seed, DNS/ACME action, Nginx
  change, Chatbot restart or frontend/preview release. Downloaded wheels are
  public dependencies only; blocked wheelhouse is not approved for deployment.

The two **blocked, non-deployable rehearsal samples** are:

```text
release-artifacts/webapp/competence-hub-webapp-0.1.0-cb95db017dc4-20261022T131333Z.zip
release-artifacts/webapp/competence-hub-webapp-0.1.0-cb95db017dc4-20261022T131425Z.zip
SHA-256 (both): 61281a880b4d7c10b2b6c4d617a7057825a9298c7e670a6e3cbbb950010fa6d5
```

Ignored local Linux evidence:
release-artifacts/webapp-linux/20261022T131402Z-fe909313.
The Linux hashed lock SHA-256 is
7a5dfc6829ada6aef639381ebc460695acaf0eec542e16fa0934f5b897dacf59;
wheelhouse INVENTORY.json SHA-256 is
e7d953d2b49569967affc2923e26a1b9a1768657a87ad19533df109140576e16.
These bind the blocked snapshot, not an advisory waiver or a Linux PASS.

## Requested Close-Out Matrix

| # | Question | Actual state |
| --- | --- | --- |
| 1 | App domain | Existing proposal found; final EDV approval OPEN |
| 2 | DNS | Name-not-found observed; A -> 217.160.255.86 required only after approval |
| 3 | TLS | Existing Certbot timer and safe webroot/renewal plan; no issuance |
| 4 | Internal port | 127.0.0.1:8001 selected under existing convention |
| 5 | Port collision | None at read-only check; mandatory recheck before later start |
| 6 | Package source | Allowlisted committed Git export plus verified exact PyPI Linux wheels; advisory gate BLOCKED |
| 7 | Python/venv | Linux Python 3.12, own per-release venv, never Chatbot/global Python |
| 8 | Reproducibility | Pins/build backend fixed; two byte-identical ZIPs; offline hash lock generated, not approved |
| 9 | systemd | Existing service identity/path retained; start limits/journald/hardening prepared, static tests PASS, native service verification NOT RUN |
| 10 | Nginx | Dedicated HTTP challenge/TLS templates prepared; canonical forwarded headers; static tests PASS, nginx -t NOT RUN |
| 11 | Health | Existing minimal /health/live and DB-backed /health/ready; no new runtime route |
| 12 | Firewall/binding | Public 22/80/443 only, app/PG loopback; actual firewall review remains later |
| 13 | Chatbot isolation | Different port/path/user/venv/unit/config/logs, no change/restart |
| 14 | Configuration | Actual API variable names only, external root-controlled config, no values/secret files created |
| 15 | Migration | No new migration; future backup/inventory/smoke/restore sequence documented |
| 16 | Release artifact | Two clean-source rehearsal sample ZIPs, explicitly non-deployable due advisory |
| 17 | SHA/manifest | SOURCE.json + MANIFEST.json + ZIP checksum; exact hashes above |
| 18 | Rollback | App/site/unit versus DB restore distinguished; inactive first-install baseline |
| 19 | Dry-runs | Windows package/import and unit tests PASS; Linux hash/advisory phase stopped safely before runtime tests |
| 20 | External inputs | Consolidated section above; no current credential action |
| 21 | Needed execution approval | Only after dependency/local gates close: exact rebuilt SHA, final hostname/TLS/port/path, synthetic-only target, owner/window/rollback |
| 22 | One next block | Separately reviewed cryptography maintenance and its crypto/compatibility/local/affected-Staging regression; EDV input collection can proceed in parallel |

## Recommended Next Block

Resolve the package security gate through a separately scoped cryptography
maintenance approval, then regenerate/test a clean artifact and retry the
prepared local Linux/proxy harness. Inputs: reviewed patched version and
compatibility plan; deliverables: reconciled pins, envelope/MFA/outbox regression,
fresh hashed wheels and an actually passing local Linux report. Done means the
advisory gate and those tests are green, not merely that installation succeeds.
No VPS Linux/proxy execution is authorized by that recommendation.

## Primary References

[Nginx proxy headers](https://nginx.org/en/docs/http/ngx_http_proxy_module.html),
[Nginx HTTPS/key access](https://nginx.org/en/docs/http/configuring_https_servers.html),
[Certbot webroot and renewals](https://eff-certbot.readthedocs.io/en/stable/using.html),
[pip hash-checked binary installs](https://pip.pypa.io/en/stable/topics/secure-installs/),
[systemd unit start limits](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html).
These support the preparation, not a claim that the VPS was reconfigured.
