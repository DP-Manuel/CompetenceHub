# Backup Destinations

Stand:04.11.2026. Manuel's addendum plans a possible internal network target;
access is not configured. **No concrete share/path/identity or destination
approval exists.** Do not guess paths or create credentials, drives or sessions.
This concerns encrypted PostgreSQL backups, not the independent approved local
[key block](controlled-backup-key-rebase-2026-11-04.md).

## Current Targets

| Candidate | Evidence / status |
| --- | --- |
| Internal SMB/network drive | PLANNED / NOT APPROVED / NOT CONNECTED. Path, access, quotas, protection, owner and retention pending. No network I/O in this task. |
| Local C: transition candidate | Fixed NTFS,479323578368 bytes free in04.11 metadata probe. Current BitLocker status unavailable without elevated same-user process. Not an approved/proven DB target; no destination folder created. |
| Existing D: key medium | FAT,2012151808 bytes free, known physically unlocked. Current BitLocker metadata also not readable from this non-elevated process. Approved for small protected key/recovery artifacts after the local runner's own current check; NOT PostgreSQL destination. |

No safe currently qualified DB destination was found from those known available
volumes. Stop before a real DB backup. The local key runner can independently
verify its own C:/D: protection in Manuel's private elevated PowerShell; that
does not approve a DB path or prove DB backup capacity/restore. Do not request
another unlock or try another BitLocker/GPG password to perform this planning.

## Prepared Offline Adapter Contract

[backup_destination_contract.py](../../deploy/scripts/backup_destination_contract.py)
accepts an explicit `DestinationSpec(kind, path, approved)` for a dedicated
absolute local Windows directory or UNC SMB directory. No default/share/account
is supplied. It uses lexical structured Windows paths, never follows them or
connects. Device paths, roots, ADS/traversal/control/reserved names fail.
Mapped drive letters cannot silently count as fixed local volumes.

`DestinationEvidence` must bind the exact path hash and fresh timezone-aware
evidence (at most1 hour, no future timestamp), measured required/free bytes and
strict boolean protection/recovery facts. Unknown/missing/truthy substitutes
do not pass. An unapproved target remains blocked despite free capacity.
Required evidence before any separately approved use:

- Named approval for exact destination and existing authorized identity;
  share AND filesystem ACLs, least privilege, privacy and access/revocation proof.
- Actual capacity/quota plus current database/export/working-copy size and
  retained-set growth; reserve at least4x expected payload plus512MiB during the
  first local restore window. The key stick's capacity is unrelated to this.
- Protected at-rest storage and **encrypted payloads only**, no application
  plaintext, key/passphrase/DPAPI material, credentials or raw DB connection URLs.
- For SMB: verified SMB3+ session, encryption and signing policy/evidence; use
  only the existing approved Windows session. No Guest/plaintext/insecure
  fallback, credential prompt automation, `cmdkey`, `net use` or secret files.
- Retention/deletion and ownership approval (existing30 daily/12 monthly pilot
  proposal is not automatic authorization for a new share); no wipe/sync purge.
- No repository/reparse overlap; exclusive new set, no overwrite, SHA-256 before
  and after copy plus reread after close. Abort/partial-set handling reviewed.
- Authorized harmless destination read/write/integrity probe and reviewed
  exact-copy isolated restore procedure. Real PostgreSQL restore from the FIRST
  actual encrypted destination copy remains mandatory for actual acceptance.

The result is deliberately `PLAN_EVIDENCE_COMPLETE_NOT_RUNTIME_ACCEPTANCE`,
never a real transfer/restore PASS. This preparation is not an active SMB
connector or scheduler. Actual permission/session/quota/protection probes and
transfer are behind a later explicit known-target operating gate. The current
Admin window's fixed-local protection guard is NOT loosened to accept UNC.

Microsoft references: [SMB security hardening](https://learn.microsoft.com/windows-server/storage/file-server/smb-security-hardening),
[signing](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing-overview).
No global machine/SMB policy changes are made by this contract.

## Operating Horizon

1. Continue only the already approved local GPG/recovery/application-key block;
   second independent recovery copy stays OPEN if no separate target is set up.
2. When Manuel has access, receive the actual network target and named use
   approval; no credentials in chat/Git. Inspect only that authorized target.
3. Compare it with a separately approved encrypted local transition destination,
   using current protection, exact path permissions and capacity/probe evidence.
4. Separately approve current Staging backup and external ciphertext copy.
5. Separately approve isolated exact-copy restore and cleanup; only then allow
   the existing separate named-Admin gate. REAL APPLY stays separate/disabled.

The new SMB destination is not automatically approved for PRIVATE GPG recovery
material. A second independent key-recovery medium/custody method needs its own
explicit approval and protection; do not place private keys in a shared backup
folder merely because DB ciphertext may later be allowed there.
