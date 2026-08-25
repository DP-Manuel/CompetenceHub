# PostgreSQL Backup And Restore Runbook

Stand: 21.08.2026

This runbook prepares the Competence Hub PostgreSQL backup, retention,
monitoring and restore gate. It does not authorize installation, timer
activation, network transfer, production data or deployment. The current VPS
Staging database remains synthetic and localhost-only.

## Operating Model

- PostgreSQL creates a custom-format database dump and globals export through
  the local Unix socket as the `postgres` operating-system user.
- Role password hashes are excluded from the globals export. Runtime passwords
  remain separately managed secrets and must be reset during a full recovery.
- Plaintext exists only in a mode-`0700` working directory below the protected
  backup root and is removed immediately after encryption.
- OpenPGP encryption uses an approved 40-character public-key fingerprint. The
  VPS needs only the public key; the private key stays on a separately
  controlled restore environment.
- A backup is complete only after encrypted payloads, metadata, checksums and
  the `COMPLETE` marker are atomically published as one daily set.
- The first successful daily set in a month also becomes that month's restore
  point. Retention is initially 30 daily and 12 monthly sets, subject to final
  privacy and business approval.
- The external workstation pulls encrypted sets from the VPS. The VPS does not
  receive an inbound path to the workstation.

## Prepared Files

- `deploy/scripts/competence-hub-postgres-backup`
- `deploy/scripts/competence-hub-postgres-backup-monitor`
- `deploy/scripts/competence-hub-postgres-restore-check`
- `deploy/scripts/pull-competence-hub-backup.ps1`
- `deploy/postgresql/backup.conf.example`
- matching systemd service/timer examples under `deploy/systemd`

The scripts use fixed server paths and reject symlinked configuration, unknown
configuration keys, unsafe database names, missing encryption recipients,
remote restore targets and non-isolated restore execution.

## Preconditions And Open Gates

Before installation:

1. Confirm the encrypted, access-controlled Wuerzburg target and available
   disk space.
2. Create the backup key on the controlled restore workstation. Transfer only
   its public key to the VPS and record the verified fingerprint.
3. Name a second D+P-controlled recovery owner and document emergency access.
4. Approve retention and deletion periods with the responsible business and
   privacy stakeholders.
5. Select an active alert channel after the EDV SMTP/mailbox response.
6. Approve a maintenance window for installation and a separate restore-test
   window.

Do not place the private key, passphrase, database URL, PostgreSQL password or
real data in Git, E-Mail, shell arguments or the Website webspace.

## Installation Rehearsal

During an approved VPS change, copy the reviewed scripts to
`/usr/local/libexec` as root-owned mode `0755`. Install the configuration as
`/etc/competence-hub/backup.conf` with owner `root:postgres` and mode `0640`.
Install the public-key-only GPG home at
`/var/lib/competence-hub-backup/gnupg` with owner `postgres:postgres` and mode
`0700`. The private key must not be imported there. Install rendered systemd
units only after `systemd-analyze verify` passes.

Run the backup service once manually before enabling either timer. Expected
evidence:

- one daily set below `/var/backups/competence-hub/automated/daily`;
- exactly two `.gpg` payloads and no `.dump` or `.sql` plaintext;
- valid `SHA256SUMS`, `METADATA` and `COMPLETE` files;
- successful monitor exit and clear journal output;
- PostgreSQL, Nginx, Fail2ban and the Chatbot remain active;
- PostgreSQL still listens only on localhost.

Stop if the service uses an unexpected database, cannot resolve the exact GPG
fingerprint, leaves plaintext, touches another backup root or affects another
service.

## External Copy Gate

The Wuerzburg workstation initiates the transfer after the local backup and
monitor are green. Transfer the complete dated directory, not individual dump
files. Verify `SHA256SUMS` again after transfer and record:

- UTC transfer time;
- source set name and checksum result;
- destination owner and protected location;
- source commit/runbook version;
- person performing the transfer.

An encrypted file that exists only on the VPS is not an off-server backup.
Successful transfer without a restore from that exact copy also leaves G-DATA
open.

For the pilot, an approved operator may stage only the completed encrypted set
in `/home/manuel/competence-hub-backup-export/<date>` with owner-only access.
The guarded PowerShell pull accepts only that dated path, rejects destinations
inside or above the repository, verifies all three checksums and refuses
plaintext. It never deletes the remote export. Remove that temporary server
copy manually only after the pull and restore evidence are accepted. A later
team setup should replace this supervised handoff with a restricted backup
transfer identity rather than broadening PostgreSQL-directory access.

## Isolated Restore Gate

Use `competence-hub-postgres-restore-check` only on an approved PostgreSQL host
with the external copy and a temporary private-key home owned by `postgres`
with mode `0700`. The command requires the literal
`--confirm-isolated-restore` flag, accepts no remote PostgreSQL host and creates
only a database named `competence_hub_restore_check_<timestamp>_<pid>`.

The check verifies encrypted checksums, decrypts into a temporary protected
directory, validates the archive catalog, restores without ownership or ACLs,
checks the `competence_hub` schema and a non-zero table count, then removes the
temporary database and plaintext. It deliberately does not restore globals or
role credentials.

The first external restore remains a supervised manual gate. Record the table
count, script exit status, source set, elapsed time and cleanup result without
recording data or secrets. Repeat at least quarterly once production data is
allowed, and before relying on a changed backup or encryption procedure.

On the controlled Windows restore workstation, use the guarded Docker variant
only after the external copy, BitLocker source and isolated execution are
confirmed. The PostgreSQL image is pinned by digest and must already be present;
the script never downloads an image. GnuPG requests the private-key passphrase
through local pinentry. No port or container network is enabled, and the
temporary plaintext plus container are removed in `finally`:

```powershell
.\deploy\scripts\restore-competence-hub-backup-docker.ps1 `
  -BackupSet 'D:\CompetenceHub\competence-hub-backups\YYYY-MM-DD' `
  -GpgHome "$env:LOCALAPPDATA\CompetenceHub\backup-gnupg" `
  -ConfirmProtectedSource `
  -ConfirmIsolatedRestore
```

Any image download is a separate network and supply-chain decision. Record its
exact digest and approval before the first use.

## Monitoring And Alerting

The monitor verifies:

- the newest daily set is younger than `BACKUP_MAX_AGE_HOURS`;
- its completion marker and checksums are valid;
- exactly two structurally valid OpenPGP payloads exist;
- no plaintext `.dump` or `.sql` exists below the automated backup root.

The prepared timer makes failures visible through systemd status and the
journal. Active notification is not yet implemented because the approved SMTP
contract and monitored routing are pending from EDV. Until that gate closes,
Manuel must include both backup units in the daily operational check. A silent
journal-only failure is not sufficient for production operation.

## Failure And Rollback

- A failed working set is removed by the script trap and never receives a
  `COMPLETE` marker.
- Retention runs only after a new complete set exists and removes only validated
  dated directories inside the fixed backup root.
- Disable both timers if backup or monitor behavior is uncertain. Preserve the
  latest valid encrypted sets and journal evidence.
- Do not delete database clusters, production data or prior backups as part of
  script rollback.
- Do not restore over the active database. Use the isolated check first and a
  separately approved recovery decision for any real incident.

## Definition Of Done For G-DATA/G-OPS

The gate closes only when all of the following are evidenced:

1. Daily encrypted backup and monitor execute under the restricted units.
2. No plaintext or secret remains in backup paths, logs or Git.
3. A complete encrypted set exists on the controlled off-server target.
4. The exact external copy restores successfully in isolation and is cleaned.
5. Retention, active failure notification, ownership and emergency access are
   approved and tested.
6. Co-hosted services and localhost-only PostgreSQL remain healthy.

Until then, use synthetic Staging data only.
