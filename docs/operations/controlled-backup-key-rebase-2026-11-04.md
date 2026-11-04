# Controlled Backup Key Rebase

Stand:04.11.2026. **LOCAL CODE PREPARATION; operator-created new key exists; real recovery/backup/restore/Admin NOT ACCEPTED.**

Later04.11 approval: **K1/K2 real LOCAL key block is explicitly authorized**,
including protected USB export/import/recovery, unchanged-DPAPI rewrap and green
source commit/push. Manuel subsequently generated the new key in his elevated
operator window, then stopped at custody/export. He confirms handwritten
passphrase custody and no password manager. Private Pinentry recovery is still
required; the agent has not executed the real key workflow.
New [single local runner](../../deploy/scripts/run-local-backup-key-block.ps1)
replaces separate generation/copy commands. It ends after K, regardless of
success/failure; no database/Admin continuation. Second independent recovery
may remain OPEN by explicit user decision. The [planned SMB target](backup-destinations-2026-11-04.md)
does not delay K and is neither configured nor approved for DB or private keys.
Authority: Manuel's new controlled-rebase decision. This supersedes the prior
request to recover the August passphrase, not the preservation/approval gates.
Manuel is sole technical operator/key custodian. Janay has no technical backup,
key-management or recovery role; mailbox/business responsibilities are separate.
The25.08 synthetic backup is no longer authoritative and need not be retained
long term. It and the old keys remain untouched pending successful new recovery
and a distinct, exact-path deletion approval. No migration/import/Website action.

## Decision And Boundaries

- New dedicated OpenPGP identity, separate approved protected local home, new
  high-entropy passphrase in Manuel's password manager OR protected written
  offline custody, stored separately from the USB key export. Never reuse/guess the
  lost passphrase. Identity label proposal: Competence Hub Staging Backup2026-11.
- Preserve the existing DPAPI application's32-byte keys and all version labels.
  Rebase is **rewrapping**, not Portal TOTP/HMAC/outbox-key rotation. No new
  application-key generator, no overwrite of the old custody directory/metadata.
- Separate OpenPGP private-key recovery from portable application-key recovery.
  A public-key export or working DPAPI alone cannot replace a recoverable private
  OpenPGP key and its passphrase. File hashes prove bytes, not decryptability.
- A new local candidate is not active runtime configuration and not database
  recovery acceptance. Actual current exact-copy PostgreSQL restore closes that
  gate. Existing daily/monthly jobs, timers, retention and Chatbot stay unchanged.
- Current real DPAPI type/Windows assignment was previously confirmed. This
  preparation does not reopen its contents or claim a fresh real payload/GPG PASS.
  Actual structure, distinct keys, versions and byte integrity are checked only
  in the explicitly approved rewrap process, without output/plaintext files.

## August Dependencies And Prepared Replacement

Old primary fingerprint: `2E44306121629A100F76A8B08CCA3D9186A28D4C`;
key ID: `8CCA3D9186A28D4C`. The old user profile is LOCALAPPDATA, not APPDATA.

| Dependency | Local preparation / later activation |
| --- | --- |
| [Initializer/GPG/loader](../../deploy/scripts/initialize-staging-operator-config.ps1): old recipient default, old metadata binding | Explicit new full recipient for encryption and expected-recipient loader; legacy default unchanged. Existing DPAPI copied byte-for-byte into a NEW private candidate; new metadata only after actual recovered-key comparison. |
| [Old local VERIFY](../../apps/webapp/scripts/verify-staging-keys.ps1), compatible resume | Historical old-key entry; do not retry it for rebase. No silent fallback, imported old key, or replacement of its files. |
| [Admin window](../../apps/webapp/scripts/run-staging-admin-window.ps1): old home/recipient/implicit initialization | Now requires explicit acknowledged new custody/home/fingerprint and verified backup target. No automatic initialization. New fingerprint pinned into producer, restore and Admin checks. Separate BACKUP, RESTORE and ADMIN confirmations. |
| [Snapshot producer](../../deploy/scripts/competence-hub-postgres-snapshot): fixed August recipient/home | Explicit --rebase-recipient selects the NEW public-only `/var/lib/competence-hub-backup/rebase-20261104-gnupg`; fixed Staging DB unchanged. Empty/short/placeholder/legacy/injected rebase inputs fail before server work. Old invocation remains legacy, never the new window's selection. |
| [Baseline verifier](../../deploy/scripts/verify-prechange-restore-baseline.py), [restore](../../deploy/scripts/restore-competence-hub-snapshot.ps1), [Admin](../../apps/webapp/scripts/staging_admin_operator.py) | New expected-recipient parameter is pinned by operator input, never inferred from untrusted METADATA. Default still rejects new-recipient data, explicitly new mode rejects old data. Schema/owner/count/hash/freshness/cleanup guards retained. |
| Server automated backup.conf / public-only home | Historical last setup uses old key. No server config read/change in this task. One-off new snapshot can be independent; later scheduling/config promotion needs its OWN reviewed approval after actual restore. |
| Existing `.gpg` snapshots / old portable application-key backup | Cannot be unlocked by new key. Keep originals; the new current snapshot/rewrap replaces reliance, not their bytes. No claim that old archives are recoverable. |
| DPAPI store / actual Portal cryptographic material | Not an August OpenPGP dependency: same Windows assignment, bytes and validated payload retained. |
| Historical evidence/tests/constants | Preserve dated truth/legacy rejection cases. No global search-and-replace of fingerprint or old records. Current owner decision supersedes September Janay assignment. |

Producer SQL/snapshot consistency stays unchanged. No server install/public-key
import or file read was performed to infer today's operational configuration.

## One Consolidated Operating Sequence

**Not a command to execute now.** After scoped approvals and packaging, one
private PowerShell7 window coordinates the sequence; native GPG Pinentry and
the existing local Edge MFA window are intentional. No preloaded clipboard,
transcript/debugger/screen recording, secret arguments, credential files in Git
or repeated old commands. Present exact paths/full new fingerprint/source commit
before every authorized block. A failure stops; resumption is reviewed, never
automatic deletion, overwrite, recreation or an Admin retry.

| Gate | Necessary approval/input | Operations / acceptance |
| --- | --- | --- |
| K1 NEW KEY + RECOVERY | Explicit NEW key-generation/private recovery-copy approval; current protected local volume, confirmed manager OR protected written offline custody and approved separate recovery target | Native GPG wizard in a NEW non-existing disjoint private home, RSA4096 with encryption capability, bounded expiry and reminder30 days before expiry. New passphrase only in Pinentry, saved in the chosen separate custody. Existing-key resume never generates a replacement. Full fingerprint recorded as public metadata. No old-home access/import. |
| K2 RECOVERED KEY + REWRAP | Same scoped local block; explicit recovery/private storage acknowledgments | Export ONLY new secret key with its passphrase protection intact; verify protected export, copy exclusively to protected recovery storage and compare SHA-256. Import THAT exact copy into a NEW isolated private home. Retrieve passphrase from separate custody; prove decrypt there without original live home or old key. Then call existing-DPAPI rewrap candidate: preserve original hashes, copy DPAPI bytes, encrypt existing payload to new recipient, decrypt using recovered home, constant-time payload comparison, strict versions/schema, new READY metadata and loader acceptance. No plaintext key file. |
| B BACKUP | Separate BACKUP approval with fixed VPS217.160.255.86 / competence_hub_staging, new recipient, exact protected target/size and quiet-window confirmation | Provision only new PUBLIC key in separate postgres-owned0700 home; confirm primary fingerprint and absence of private material before snapshot. This provisioning is separately reviewed within B, not done by the snapshot script. New unique current exported-MVCC snapshot, password-free globals, encrypted five-file set, SHA checks. Exact external copy to approved target; old automated jobs unchanged. |
| R RESTORE | Separate RESTORE approval, protected plaintext workspace and cached pinned PostgreSQL16 image | Actual restore from THAT external copy in owned random container, network none/no ports, isolated DB only, no globals replay, expected migration/relation/count/owner baseline and hashes. Cleanup exact owned container/DB/plaintext and prove absence; retain encrypted source. Acceptance only after actual proof, not VALID/MATCH or synthetic PASS. |
| A ADMIN | Separate ADMIN approval after K/B/R PASS; existing approved private Manuel login, no invented identifier | Exactly one admin-only account; no Coach/Internal/Reviewer/Contact grant or mapping. Human MFA enrollment, privately stored recovery codes, login/resume/logout, one-time recovery/replay rejection, Audit/RBAC. Snapshot and restore fresh <=4 hours, unchanged target baseline immediately before write. Uncertain outcome stops without retry/delete. |
| O CLOSE | Read-only health and operator acceptance | PostgreSQL localhost-only, PostgreSQL/Nginx/Fail2ban/Chatbot and any actually installed Portal service checked, no unnecessary restart. Record actual outcome only. Later active backup config/scheduling/notifications and old-file deletion each require separate approval; no productive Portal activation implied. |

The new [local rewrap helper](../../deploy/scripts/prepare-backup-key-rebase.ps1)
defaults to PLAN_ONLY. It does not generate/import/export a real GPG key, run a
server command, activate a candidate or create an Admin. Its Execute mode only
rewraps after new/recovered homes, full recipient, reviewed clean source and
three explicit custody acknowledgments are supplied. It requires a fresh
destination; interrupted artifacts remain for review, never overwritten on retry.
The old portable GPG file need not decrypt or have a valid old READY record.

## Storage And Independent Recovery

The single runner uses one owned append-only state directory
`%LOCALAPPDATA%\CompetenceHub\backup-key-rebase-20261104` containing separate
`live-gnupg`, `recovered-gnupg` and `application-candidate` subdirectories.
This layout supersedes the following separate-path proposal. Non-existing homes
are created only in the approved operator process; preserved partial homes are
never regenerated. Current C:/D: BitLocker proof is mandatory before creation.
If the probe is refused, start PowerShell7 elevated as the SAME Windows user,
not another Admin account. No BitLocker unlock, sudo, DB or SMB credentials.

Proposed new external paths, **not created/approved by preparation**:

- Local new live home: `%LOCALAPPDATA%\CompetenceHub\backup-gnupg-rebase-20261104`.
- Recovered test home: `%LOCALAPPDATA%\CompetenceHub\backup-recovery-rebase-20261104`.
- Candidate: `%LOCALAPPDATA%\CompetenceHub\staging-operator-rebase-20261104`.
- Separate recovery copy candidate: a NEW subdirectory below the already known
  BitLocker stick `D:\CompetenceHub`. Only passphrase-protected OpenPGP private
  export/revocation recovery material and encrypted portable application keys;
  no plaintext secrets, DPAPI-only substitute, database dump or shared password.
  Do not assume a `.gpg` suffix proves protection. Never copy unprotected secret
  export to FAT. New key's public export may also be carried here.
- Passphrase custody: password manager OR protected written offline record,
  owned by Manuel, with full fingerprint/purpose/expiry and private passphrase.
  Offline paper belongs in controlled secure storage, separate from the USB
  export; never scan/copy it into Git, logs, Chat or recovery notes. Recovery
  must not depend on this GPG key, this Windows DPAPI profile or the same USB
  unlock secret. Passphrase and recovery media are stored separately. Record only
  a non-secret custody confirmation, never values. No access or role for Janay.

The1.9GB FAT stick has enough space for small encrypted key artifacts, not an
approved PostgreSQL destination. A DB target remains **unselected/unverified**.
Free C: capacity is not consent or volume-encryption proof. Before B, measure
current database plus globals/working space in an approved read-only preflight;
reserve at least4x expected payload plus512MiB, and verify free bytes again.
The guarded window requires existing private fixed NTFS target, current
FullyEncrypted/ProtectionOn/Unlocked metadata and explicit capacity reservation.
It independently checks encryption/free space of LOCALAPPDATA's volume because
the restore helper places temporary plaintext there. Unknown/permission-denied,
FAT, suspended protection or insufficient capacity STOP without elevation or
password retry. Do not create a target merely because it has free space.

A current off-VPS encrypted copy plus local restore is not proof against loss of
that workstation. Keep an accepted independent encrypted copy sized for real
backups before claiming durable unattended production protection. Quarterly
restore/recovery drill and expiry reminder belong to Manuel's technical process;
automated timer/alert activation is a later explicit change, not part of K.

## Failure, Rollback And Evidence

- Before new acceptance: old artifacts and server jobs unchanged. Losing a new
  candidate does not invalidate original DPAPI; don't generate replacement app
  keys. If DPAPI is unavailable, STOP: no substitute actor/key material.
- Failed new decrypt/protection/recovery/copy comparison: no READY/activation,
  no backup/Admin continuation; preserve partial private files for bounded review.
- After B/R: preserve exact encrypted snapshot and bound proof, including new
  recipient; a request to restore real Staging is not part of isolated R.
- Failed Admin/uncertain commit: preserve attempt marker and examine actual
  account state in separate approved check, never repeat blind or restore DB.
- Delete old exact named files only AFTER actual K/B/R acceptance and distinct
  deletion approval. The decision not to retain August long term is not deletion
  permission now. No rollback to an inaccessible August backup is promised.
- Synthetic tests use fresh DPAPI and new disposable GPG material, including an
  actual protected secret-key export/import, recovered-home decrypt and original
  byte preservation. They do not prove real key custody, BitLocker or DB recovery.
  Agents and test private profiles/secret export are removed only for these owned
  newly generated test resources. No actual Portal/server/Website operation.

Observed native GPG-helper bug: async stream completion could emit an internal
Task result into the PowerShell pipeline. Result is now explicitly discarded;
native synthetic rewrap asserts exactly one bounded result object. No crypto
algorithm/dependency change. Fixed old-flow behavior remains under regression.

Official GnuPG references: [key management](https://www.gnupg.org/documentation/manuals/gnupg/OpenPGP-Key-Management.html),
[secret export/import semantics](https://gnupg.org/documentation/manuals/gnupg/Operational-GPG-Commands.html).

## Verification Of This Preparation

- Full local suite1367 PASS/30 expected opt-in skips;34 new rebase cases.
  JUnit stays ignored at `.tmp/coach4/backup-key-rebase-20261104.xml`.
- Native disposable GPG test uses only fresh test identity/passphrase and
  private isolated homes. Test-only loopback/fd supplies only synthetic material;
  operational code keeps native Pinentry, never passphrase arguments. Protected
  export/import and actual recovered-key decrypt PASS; synthetic DPAPI remains
  byte-identical; original legacy recipient is not used to decrypt.
- Focused49 PASS after final bounded protection-status error handling. Unknown,
  Off, Locked, FAT, undersized reservation and unprotected temporary workspace
  fail. Default CLI is PLAN_ONLY and does not touch real private paths.
- Four affected PowerShell scripts parse; Bash producer syntax PASS; pip check,
  documentation links/context integrity and diff checks PASS. Formatter package
  is not installed; no dependency installation/update for this task.
- No fresh PostgreSQL/native Admin/browser/server test claimed. Existing DB
  restore tests run only when their separately owned opt-in environment exists;
  real current baseline/recovery remains pending B/R/A. Public Website, Portal
  application source, schema and systemd/backup.conf templates are unchanged.
- At that prior1367-test preparation checkpoint changes were local/uncommitted;
  no push, deployment, real key generation,
  original-file deletion or operational activation. Previous unknown worktree
  entries are preserved. Source packaging precedes any later pinned real run.

## Exactly One Next Block

Recommend **execute the approved K1/K2 local block in the private operator window**.
Real key/copy approval is granted. Inputs: protected Windows volume and separate
protected recovery target, accessible protected passphrase custody, preserved source pair,
reviewed packaged source. Deliverables: new independently recovered OpenPGP key,
protected export with matching copy hashes and validated byte-unchanged application
keys in a separate candidate. DoD: actual K proof and originals preserved; STOP
before B/R/A. Collect remaining DB-target and later block approvals together,
not one speculative command/password interruption at a time. REAL APPLY disabled.

## Approved Local Runner Handover

### Protected Offline Custody And Existing-Key Resume

Latest04.11 explicit decision: password-manager custody OR protected written
offline custody is acceptable. Manuel confirms the new passphrase is written
down; there is no password manager. Use the existing operator-created key only:
full public fingerprint `22C82A2F175DAFB04B019502E92DE7854AF99C1F`, expiry2028-11-03
per Manuel's native output. Never generate/rotate a replacement on this resume.

The runner's `-ExistingFingerprint` refuses a missing live home BEFORE creating
anything and refuses a different identity before custody/export/USB activity.
Existing homes are never reinitialized, even if incomplete. Resume with
`-PassphraseCustody ProtectedOffline` explicitly confirms protected separate
paper custody without another Read-Host; `PasswordManager` is the alternative.
Without an explicit method or valid prior receipt the single non-secret prompt
accepts PASSWORTMANAGER or OFFLINE (case/edge-whitespace tolerant), not a password.
Empty, unknown or generic ja stops with guidance, no receipt. Pinentry still
requests the existing passphrase ONLY for actual GPG export/recovery operations.

Append-only `passphrase-custody-v2.json` records the method, exact fingerprint,
confirmation and SECOND_RECOVERY=OPEN; it contains no secret or storage location.
An old manager-only receipt is preserved and SHA-bound, not rewritten. Explicit
ProtectedOffline corrects that historical method claim in a NEW v2 receipt.
Valid v2 resumes require no further custody prompt; method/identity/legacy-hash
conflicts STOP without overwrite. Legacy accepted receipts remain readable.
Versioned neutral `RECOVERY-NOTES-v2.txt` leaves old USB notes untouched.

Actual metadata-only inspection before edits: live home/identity/legacy custody
present; private export, recovered home, application candidate, comparison and
completion absent. No private key opened, crypto command or real file write.
This is partial operator progress, NOT completed recovery or a second copy.
Local tests cover both methods, denied/cancelled confirmation, legacy correction,
conflicts, cancelled export and exact-key resume, completed proof reuse and
missing/wrong/partial-home no-generation. Full native synthetic recovery remains
part of the regression; the real USB proof is still the operator's next gate.
Focused runner/rebase regression:72 PASS, including14 added custody/resume
cases. Full1433 PASS/30 expected opt-in skips in196.97s. Parser, inert CLI with
the new public parameters, dependency check,
135 changed-document links and256 context-router links/archive hashes PASS.

### Elevated Owner Fix

Later04.11 real operator attempts: first unavailable BitLocker status; agent's
read-only PS7 probe reproduced non-elevated CIM access denied, command available.
Manuel then confirms an elevated run; this returns a DIFFERENT generic preflight
STOP. Root/authorization exist, live/recovered key homes and candidate do not.
Actual ACL metadata identifies the cause: root owned by Manuel and protected;
new authorization.json owned by BUILTIN Administrators, with ONLY operator and
SYSTEM full-control entries. The old writer used the elevated token's default
owner, then rejected it in its stricter user-owner check. This is a script defect,
not a lost/new passphrase or another BitLocker unlock requirement.

New private files now use FileSystemAclExtensions.Create with explicit current
user owner, protected operator/SYSTEM DACL, CreateNew and exclusive stream at
creation. This covers receipts, agent policy, private encrypted export, copied
DPAPI ciphertext, new portable ciphertext/metadata and completion pending files.
No chmod/ACL repair or overwrite of existing keys or artifacts is performed.
The exact known failed authorization receipt can be read WITHOUT modifying its
bytes/owner/ACL only in its trusted user-owned root, with private DACL, exact
schema/scope/hash whitelist and buggy source commit5b0f7ab. Generic private-key
and receipt owner checks stay strict. Unknown group owner/source or broad ACL
still STOP. Native GPG-managed subfiles inherit the private home access rules;
the helper does not rewrite their existing private contents/security.

Real read-only probe confirms this receipt is accepted, original ciphertext
hashes match, and live key home remains absent. No GPG/key generation, file copy,
permission change, DB/Admin/server action in the diagnostic. The elevated run's
progress implies the configured volume and DPAPI checks completed before the
receipt failure; this is not a new unrestricted DB-target approval or an agent's
independent elevated volume measurement. B/R/A still excluded.

Preflight failures now include a bounded STEP (source/source_acl/corpus/tools/
volume_status/source_hashes/dpapi_payload/authorization_receipt), not just a
misleading generic phase. No submitted value, key or raw exception is printed.
Regression includes explicit native file security/no-overwrite, six simulated
elevated/foreign-owner and ACL/schema/source cases, unchanged on-disk metadata,
strict generic private checks, existing full local flow and native synthetic GPG.
Full regression:1419 PASS/30 expected opt-in skips in166.12s; focused76 PASS,
then24 owner/runner cases PASS. Native secure-file creation ran under the agent's
non-elevated token; elevated ownership rejection/recovery was simulated with ACL
metadata doubles. Actual elevated operator K1/K2 acceptance remains pending.
Fix packaged separately as `ef70418`. Three-script PowerShell parse, pip check,
122 changed-document links,253 router links/archive integrity and diff checks
PASS. Documentation packaging is separate; no private artifact is versioned.
Only next block remains the ALREADY APPROVED local private K1/K2 run from updated
pinned source. Keep the working directory/old receipt; do not delete/reset it.

Implementation packaged as `cbc4a14`; independent offline destination contract
as `d681088`. Documentation/checkpoint packaged separately. This is source
delivery, not actual key generation/custody/USB execution or Website deployment.

Current verification:1412 local tests PASS/30 expected opt-in skips, including
45 new window/destination cases in addition to the previous1367. Native
disposable test identity now uses RSA4096 and configured passphrase constraints;
packet inspection works on protected file AND memory, actual GPG decrypt cannot
be relabelled as the August primary fingerprint. No real Pinentry/USB outcome
is inferred. Final CLI default and invalid-commit intent are tested, including
dot-sourced parameter preservation; native plaintext/packet text is not logged.
Source/document packaging is explicitly approved; actual key/recovery artifacts
are external and also blocked by repository ignore rules.
Final focused46 tests also PASS after owned recovery-cache cleanup; five
PowerShell parsers, Bash syntax, pip check, compile/link/context/diff gates PASS.

One source-pinned absolute-path command is issued after green packaging, to run
in private PowerShell7 elevated under Manuel's same Windows identity. No cwd
change or second terminal, no clipboard-preloaded operations. GPG Pinentry owns
the new passphrase; new live agent enforces at least20 characters and one
non-letter, no bypass, with bounded cache. Only one necessary non-secret local
confirmation records protected manager OR written offline custody. The explicit
non-secret method parameter replaces that prompt; a valid receipt also skips it.
Never type the passphrase into the custody prompt or send it to the assistant.
See [GnuPG agent policy](https://www.gnupg.org/documentation/manuals/gnupg/Agent-Options.html).

The protected secret export is inspected IN MEMORY using GPG's packet metadata;
unknown/unprotected/unsupported secret packets fail before export bytes touch
disk or USB. Every secret packet must have the recognized v4 protection and AES
S2K, not just a filename or one matching word. No packet text/key bytes are logged.
GPG colon metadata pins a single RSA4096 encryption identity. Decryption uses
GPG's machine status DECRYPTION_KEY to bind the actual primary fingerprint,
not merely a caller-provided label. Old August key/home remain untouched.

USB destination is a NEW fingerprint-qualified folder below D:\CompetenceHub.
All copy operations refuse replacements and compare source/target SHA-256.
It receives protected private export, encrypted portable application keys,
SHA256SUMS and non-secret recovery notes; no DPAPI-only/private plaintext file.
FAT has no NTFS ACL model: USB protection is explicitly BitLocker plus protected
OpenPGP payload, not a fictional file-ACL PASS. Local originals/candidate/homes/
receipts require private operator+SYSTEM ACLs and protected volume.

Actual import reads the exact protected USB export in the isolated new profile;
no original live private-key access in that recovery step. GPG's native dialog
may be needed for import or decrypt; clearing only the owned recovery cache is
done BEFORE import, not between successful import and decrypt. Preserve valid
hash-bound crypto proof after a copy failure instead of asking the passphrase
again. Finished reruns verify bound proof/hashes without regeneration/dialogs.
At completion only the owned recovered profile's decrypted agent cache is
cleared; private files/old keys are not deleted. Passphrase expiry metadata is
printed for the separate custody record; active reminder scheduling is separate.
Partial encrypted/application files are preserved; only their explicit safe
completion can proceed, never re-encryption/overwrite or guessing old passwords.

The private non-secret completion receipt records fingerprint/hashes, original
DPAPI preservation, USB recovery outcome and SECOND_RECOVERY=OPEN. On success:

```text
LOCAL_BACKUP_KEYS=PASS RECOVERY=PASS DPAPI=UNCHANGED SECOND_RECOVERY=OPEN SERVER_ACTIONS=NONE
```

At this handover actual key/USB/native Pinentry proof remains **PENDING OPERATOR**,
not inferred from synthetic tests. Return only the safe final status/fingerprint
or bounded STOP phase/code, never passphrases, private exports or application keys.
STOP afterwards: no VPS backup/restore/Admin, migration/import/deployment/deletion.
