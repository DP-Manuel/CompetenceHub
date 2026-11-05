# GPG Root Cause And Recovery Decision

Stand:05.11.2026. Local investigation/preparation only. No real passphrase entry,
secret-key read, export/import, new real key, server/data/Website action.

## Decision

The exact cause of the rejected passphrase is **not established**. A repair of
the existing secret key is not justified by the available evidence. Recommend a
controlled replacement candidate, keeping BOTH August and04.11 keys untouched.
New real generation requires a fresh explicit approval; none is inferred from
this investigation. No further attempt against the failed key is allowed.

The demonstrated process defect is different from the unknown input failure:
generation/identity/custody were recorded before cold export and independent
recovery had passed. Existing native tests used loopback input and a warmed
agent for the later ask-mode helper, not the human Ask generation/export path.
Those tests did not prove the handwritten passphrase would unlock a cold key.

## Actual Generation And Export Trace

The pinned04.11 runner used GnuPG2.5.21, gpg-agent2.5.21, libgcrypt1.12.2:

```text
gpg.exe --no-options --homedir <owned-live-home> --no-auto-key-retrieve
  --auto-key-locate clear --no-auto-key-import --pinentry-mode ask
  --batch --quick-generate-key "Competence Hub Staging Backup 2026-11"
  rsa4096 encr 2y

gpg.exe <same common options and home> --export-secret-keys
  22C82A2F175DAFB04B019502E92DE7854AF99C1F
```

Passphrase creation and later entry belong to native Pinentry. No passphrase
argument, environment secret, terminal Read-Host or script text normalization is
used. Standard input closing does not provide the native Pinentry's input.
The original Unicode/whitespace/case/layout state cannot be reconstructed from
these non-secret records. No comparison with Manuel's actual note was performed.

Both operations select exactly:
`%LOCALAPPDATA%\CompetenceHub\backup-key-rebase-20261104\live-gnupg`.
This overrides APPDATA/default home/registry; GNUPGHOME is unset. gpgconf maps
this home to a dedicated socket below LOCALAPPDATA\gnupg\d.m93aw3zjkjg6hejy.
The socket location outside the key home is normal Windows GnuPG behavior, not
proof of a different key profile. No agent or Pinentry process was running at
the05.11 inspection; the exact historical process/PID is not recoverable here.

The existing agent policy exactly matches the original five-line script policy:
enforced minimum20 characters, one non-letter, cache300/max900 seconds.
No explicit pinentry-program, logging or formatted-passphrase option was set in
that file. gpgconf resolves the installed default to Gpg4win\bin\pinentry.exe;
its signature is VALID and its version is pinentry-qt1.3.3. Historical per-window
keyboard state and the exact agent/Pinentry invocation were not logged.

## Non-secret Consistency Evidence

- Expected UID, RSA4096 primary, encryption capability ecEC and long ID
  E92DE7854AF99C1F all match. Full public fingerprint matches the identity receipt.
- Public self-signature verifies; created04.11.2026, expires03.11.2028.
- Exactly one private key object exists; its filename matches the public
  keygrip and its size is4024 bytes. Its contents were NOT opened or hashed.
- Presence/length/self-signature do not prove secret-key decryptability or rule
  out a private-object problem. No deep private-key validation was attempted.
- Read-only public inspection used no-autostart/no-auto-check-trustdb/lock-never;
  no true passphrase attempt, agent launch or key modification was performed.

No wrong-home/fingerprint/configuration discrepancy is demonstrated. Layout,
Caps Lock, visually similar characters, whitespace or Unicode normalization are
possible explanations, NOT diagnoses. GnuPG documents that secret export can
require unlocking because internal and OpenPGP export protection differ; seeing
an export dialog alone is normal. No matching vendor bug was established.

Primary references: [key creation](https://www.gnupg.org/documentation/manuals/gnupg/OpenPGP-Key-Management.html),
[agent/home/cache/Pinentry behavior](https://www.gnupg.org/documentation/manuals/gnupg/Agent-Options.html),
[why secret export requests the passphrase](https://gnupg.org/faq/whats-new-in-2.1.html).

## Dependency Assessment

| Relevant use | Evidence and conclusion |
| --- | --- |
| Current encrypted database backup | No such operation authorized/executed by this block. Authorization receipt scope LOCAL_KEY_REBASE_ONLY, original source5b0f7ab. The documented historical server configuration uses August recipient; it was not contacted or changed. No documented new-key DB dependency. |
| Portable existing-DPAPI backup | Local private export, application-candidate, recovery comparison and completion are absent. The source order cannot reach application encryption before successful secret export/exact USB import. No new-key portable application artifact in the reviewed flow. Original DPAPI/August ciphertext preserved. |
| Other permanent productive artifact | No matching fingerprint references outside incident/custody documentation; Portal and new backup configuration have not been activated. No documented productive use. This is not an inventory of unrelated private files or unseen servers. |
| USB artifacts | D: is not attached/accessible today; no fresh USB claim. Last04.11 metadata and source trace show export absent before the USB export/application copy steps. Availability/protection must be rechecked before any future execution. |

The failed key is therefore not a required recovery dependency in the reviewed
project process. Keep it anyway; absence outside reviewed scope is not assumed.

## Prepared Coupled Replacement Block

New identity proposal: `Competence Hub Staging Backup Recovery 2026-11-05 R2`.
New full fingerprint: NOT GENERATED/UNKNOWN, never invent one. Separate future
root: `%LOCALAPPDATA%\CompetenceHub\backup-key-rebase-20261105-r2`.
The date labels the prepared candidate, not a claim of actual generation.

[Prepared lifecycle helper](../../deploy/scripts/prepare-backup-key-lifecycle.ps1)
has an inert public entry: PREPARATION_ONLY/NEW_REAL_KEY=NOT_AUTHORIZED. It cannot
generate a real key by merely running the file. The candidate function additionally
requires explicit new-generation acknowledgment, clean pinned source, current
protected local/USB volumes and a fresh non-existing root. No database or app-key
input exists in this function. Do not invoke it before separate approval.

After approval, a single operator block must:

1. Prove the exact protected targets; name new UID/root and preserve old homes.
2. Generate in the fresh home using native Ask Pinentry, minimum20/non-letter
   policy and an explicit installed Pinentry path; disable external cache for
   this new profile only. Record candidate identity, not an accepted backup key.
3. Confirm protected offline or manager custody via the explicit non-secret
   method once. Stop ONLY the owned new live agent to clear generation cache.
4. Immediately export with the separately recorded passphrase. Inspect protected
   packets in memory; write exclusively and compare the exact USB copy's hash.
5. Import THAT export into a fresh isolated profile; verify identical fingerprint.
   Stop ONLY that recovered agent, clearing any import-warmed passphrase cache.
6. Encrypt a NON-SECRET fixed probe to the public key. Cold-decrypt with the
   recovered profile; validate native DECRYPTION_KEY recipient and exact bytes.
   Only then write key-lifecycle-proof.json with status PASS and bound hashes.
7. End with SECOND_RECOVERY=OPEN and no application-key, database or server action.
   Later DPAPI rewrap/DB snapshots must consume actual accepted identity/proof,
   never candidate name/existence. DB backup/restore/Admin remain separate gates.

A failed/cancelled block preserves all partial files and emits no acceptance
proof. Repeating generation against that root is refused. No blind retry,
deletion/reinitialization, weakened passphrase protection or fallback to old keys.
The earlier runner also now rejects the held04.11 fingerprint before unlock.
Unavoidable independent export/recovery entries are explained upfront; a native
bad-passphrase prompt means cancel and inspect, not a new password-guess loop.

## Verification And Limits

Focused80 tests PASS. Eight new cases cover inert entry, missing approval,
cancelled export/decrypt, no regeneration, no app-key access and held-fingerprint
denial. Two of these use REAL GPG Ask generation/export/import/decrypt with a
minimal synthetic-only Pinentry protocol executable, not loopback: ASCII and
Unicode/combining characters/leading-trailing spaces survive repeated cold
exports. A deliberately wrong synthetic input produces native bad-passphrase
code11; correct synthetic input works again and private-object bytes are unchanged.

The protocol double exercises the actual agent path but is NOT the Qt dialog or
Manuel's keyboard. It cannot exonerate every GUI/layout issue or identify what he
entered. It reads only generated synthetic test values. No operational passphrase
is captured, converted, compared or logged. All owned test homes, exports,
synthetic values/executable and agents are removed and absence asserted.

Full local regression:1441 PASS/30 expected opt-in skips in222.94s. Final
cleanup ordering then tightened to stop owned agents BEFORE recording PASS;
all8 lifecycle cases rerun afterwards PASS in33.43s. Two PowerShell parsers,
pip check,166 changed-document links,263 router links/archive hashes and diff
checks PASS. No Website/dependency/schema changes or production smoke needed.

Test-only fixture repair: .NET Console encoding setters failed when launched
without a console by libassuan (EOF/No Pinentry85). Using raw standard streams
fixed that emulator; it is not the real Qt bad-passphrase11 incident. No proposed
repair of the actual key is inferred from a synthetic harness defect.

## One Recommended Next Block

Obtain explicit approval for **R2 local key generation plus immediate isolated
recovery only**, with the protected stick reattached. Inputs: approval, available
protected USB/local storage and private offline passphrase custody. Deliverable:
actual cold export/exact-copy import/cold decrypt proof, originals preserved.
DoD: real key-only proof PASS; second independent copy honestly OPEN; STOP before
application rewrap/DB backup/restore/Admin/import/deployment. No execution command
is issued before that approval.
