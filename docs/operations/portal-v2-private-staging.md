# Portal V2 Private Staging

**Local preparation only.** Exact-source ZIP and Linux proof:
[consolidated V2 report](../handoffs/2026-11-19-v2-platform-acceptance.md#testnachweise).
No VPS probe, deployment, migration of the original database or real Coach import.
The only candidate scope is the synthetic private pilot. `deployment_authorized`
is always `false` in package/preflight metadata, not a release approval.

## Baseline and Target

Use only the [actual V1.2 acceptance](portal-v12-calendar-ux-2026-11-13.md#v12-tats%C3%A4chlich-abgenommen)
and [actual TLS acceptance](pilot-tls-renewal-2026-11-16.md#actual-acceptance) as
historical evidence: V1.2 `5a555e9a9aae`, 27 tables at ledger `0001..0006`, and the
16 November localhost leaf valid until **30 November 2026 18:09:39 UTC**. The
manifest pins their exact public receipt hashes. This does not certify present
uptime, live data, or today's TLS. A different or expired leaf is a STOP until a
currently accepted baseline and corresponding package contract are available.

| | Retain, do not switch or overwrite | V2 private pilot |
| --- | --- | --- |
| DB | `competence_hub_staging` | `competence_hub_v2_pilot`, PG16, `127.0.0.1:5432`, app role `competence_hub_app` |
| Services | Existing private API and TLS proxy, Chatbot, Nginx, Fail2ban, PostgreSQL | New V2-only API `127.0.0.1:8002`, V2-only TLS proxy `127.0.0.1:8444`; no worker/timer |
| Client | Tunnel `localhost:8447` to VPS `127.0.0.1:8443` | Same exact origin `https://localhost:8447`, tunnel to VPS `127.0.0.1:8444`, dedicated browser profile |
| Runtime | Accepted V1.2 and its retained V1.1/V1 overrides | `COMPETENCE_HUB_CAL2_MODE=synthetic-pilot`, invitations disabled; never start in default-off as a fallback |

No V1 unit, drop-in, listener, source DB, role/global configuration, TLS pair,
existing tunnel starter, public DNS, SMTP, Website or Chatbot is modified. V2's
proxy uses the accepted TLS files through a separate systemd credential load;
the private key never enters Git, package, commands or receipts. Keep owner-only
SSH access. Only one tunnel owns local `8447` at a time; cookies ignore ports,
so do not reuse the V1.2 browser profile or copy storage between profiles.

## 1. Build and Verify Locally

Input is the **final tested full SHA**, including the V2 helpers and final runtime
contract. Prepare a nonsecret owner-attested JSON receipt with exactly `commit`,
`result` (`PASS`), and `integration_report_sha256` (hash of the retained actual
test evidence for that commit). No self-attestation from an earlier build. Pin
the receipt hash independently. The builder does not rerun integration checks,
fetch Git objects, read the dirty tree, or contact an index. Commit objects must
already be present. Example in **workstation PowerShell**, repository root:

```powershell
$py = 'apps/webapp/.venv/Scripts/python.exe'
$cache = 'release-artifacts/webapp-linux/20261113T151559Z-1a2ef9ab/wheelhouse'
& $py scripts/build-webapp-v2-staging.py --commit $testedCommit `
  --tested-source-receipt $testedReceipt --source-evidence-sha256 $testedReceiptSha `
  --wheelhouse $cache --output-directory $freshOutputDirectory
& $py deploy/v2/v2_package.py --archive $zip --sha256 $approvedArchiveSha `
  --commit $testedCommit --source-evidence-sha256 $testedReceiptSha
.\scripts\verify-webapp-v2-linux.ps1 -Archive $zip -Sha256 $approvedArchiveSha `
  -Commit $testedCommit -SourceEvidenceSha256 $testedReceiptSha
```

Use the actual fresh ZIP path and the separately recorded SHA printed on build
as `$zip`/`$approvedArchiveSha`. Expected: `V2_PACKAGE=PASS`; exact application
wheel/source content, 25 accepted Ubuntu 24.04 x86_64 Python 3.12 dependencies
and the pinned hash lock, exactly five migration files plus the listed helpers.
The dependency cache is the [accepted V1.2 Linux proof](portal-v12-calendar-ux-2026-11-13.md#bound-local-release),
not a fresh advisory check. A changed dependency lock or wheel byte is a STOP,
not a network fallback. No source backup, fixture, operator inputs or secrets
belong in the ZIP.

Expected Linux result: `V2_LINUX_PACKAGE=PASS` and `owned container removed`.
The wrapper uses the already present, pinned local image, `--pull never`,
`--network none`, and no published ports. It verifies and installs the exact
archive in a fresh Linux venv, runs `pip check`, matches the installed app files
to the committed source inventory and checks unit syntax. It neither starts
services nor replaces exact-commit native runtime/DB tests. A missing image is
a STOP, not permission to pull another image.

## 2. Future Window: Read-Only Gate and Clone Provisioning

**Do not execute this or the following sections under local packaging scope.**
Future Owner grants must name the tested SHA, ZIP SHA, target, allowed action,
and timing. Obtain current V1.2 host/strict HTTPS proof through the approved
operator access. In a private operator work directory on Linux, use reviewed
copies of `deploy/v2/v2_{package,host,clone}.py` from the same tested commit;
never execute a helper from an unverified ZIP. Use Bash, `umask 077` and
`set -euo pipefail`; initialize pins from the independently recorded values:

```bash
pkg=(--archive "$ZIP" --sha256 "$ZIP_SHA" --commit "$COMMIT" --source-evidence-sha256 "$TEST_RECEIPT_SHA")
python3.12 deploy/v2/v2_package.py "${pkg[@]}" --extract-to "$FRESH_VERIFIED_DIR"
python3.12 deploy/v2/v2_host.py host-check "${pkg[@]}" --phase before > host-before.json
sha256sum host-before.json
```

Review exact V1.2 `ExecStart`, active six service invocation IDs, preserved
listeners, accepted proxy unit and both unused V2 ports. `host-check` does not
test TLS or snapshot reference data. Those are separate required checks. The
V1.2 protected backup/restore contract requires a **current** off-server
encrypted copy and restore of that exact copy in isolation with 27-table data,
schema/rights and sequence parity. Follow the [accepted restore procedure](../architecture/postgresql-backup-restore-runbook.md#isolated-restore-gate)
and [V1.2 preservation scope](portal-v12-calendar-ux-2026-11-13.md#granted-window1511).
Do not treat a past receipt or an unused clone name as proof. Do not restore
in place, capture credentials, restore globals, or hand-run a raw dump.

The existing exact-restore probe verifies and removes its own scratch DB; it
does **not** provision the durable named clone. Before any durable clone action,
approve the specific provisioning procedure and named target in a separate
window, from the verified protected copy only. Record independent exact clone
parity to the quiet original immediately before schema work, including the
four original synthetic users, two Coach identities and manual offers (counts,
row/schema/permission/sequence digests only). Verify synthetic-only provenance,
clone-local owner/roles/default grants compatible with the existing baseline,
no unexpected DB/object privileges, and a quiet, unserved clone; no alteration
of shared roles, source, or service configuration. The package deliberately
cannot provision, dump, restore, drop, revoke on, or connect to the source DB.

## 3. Future Window: Schema-Only Grant

On the approved PostgreSQL host, run from a private operator working directory.
For peer authentication, provide `postgres` traversal/read access **only** to
the reviewed helper copies, verified ZIP and nonsecret approval file in a
separate directory (not any keys or protected backups). Use absolute paths and
the same `pkg` pins. No passwords on the command line or in receipts.

```bash
sudo -u postgres python3.12 "$TOOLS/v2_clone.py" inspect "${pkg[@]}" > clone-0006.json
# STOP here until Owner approves the exact observed database, hash and window.
sudo -u postgres python3.12 "$TOOLS/v2_clone.py" migrate "${pkg[@]}" \
  --approval "$OWNER_APPROVAL_JSON" --approval-sha256 "$OWNER_APPROVAL_SHA" > clone-0011.json
sudo -u postgres python3.12 "$TOOLS/v2_clone.py" ready "${pkg[@]}" > clone-ready.json
```

Owner approval JSON is nonsecret, supplied after inspection: `action`
`V2_SCHEMA_ONLY_0007_TO_0011`; `commit`, `archive_sha256`,
`source_evidence_sha256`; `database` `competence_hub_v2_pilot`;
`system_identifier`, `clone_oid` and `reference_sha256` from `clone-0006.json`;
`protected_restore_receipt_sha256` and `clone_parity_receipt_sha256` from the
accepted current proofs; `expires_utc` in `YYYY-MM-DDTHH:MM:SSZ` (within 24h);
`real_coach_import_authorized` `false`. Check proof documents separately; the
hash pins bind the human decisions and do not certify their truth. `migrate`
rechecks the clone identity and reference, then runs the approved SQL bodies in
one PostgreSQL transaction, checking each ledger in order: `0007` Registry,
`0008` import ledger, `0009` lossless schema, `0010` reservations, `0011` replies.
The helper preserves the original 27-table row projection and both sequences;
the additive Coach metadata, taxonomy seeds and new ledger entries are expected.
The SQL does not include an import or identity mapping. A real Coach import
always requires its own approval, manifest, mappings and operating procedure.

`ready` is nonmutating and refuses replayable cloned sessions, challenges,
one-time tokens or unfinished delivery. If these remain, wait for expiry where
appropriate, or seek a distinct approval for clone-only auth isolation. Never
invalidate V1.2 sessions/credentials to clear this gate. Compare `clone-0011`
and the earlier clone receipt; for failure/uncertain commit, inspect under a
fresh operating decision before retry. Do not apply down migrations.

## 4. Future Window: Private Activation and No-Drop Rollback

Only after a separate activation grant, after verifying `0011`, clone readiness,
reference parity and current strict V1.2 TLS, stage in the fresh root-owned
namespace. Do not overwrite files or an existing V2 unit. Review externally
managed root-only `/etc/competence-hub-v2/runtime.env` with the authorized
operator: correct clone DSN and approved synthetic credential/key custody; no
SMTP, no default origin, no implicit use of V1.2's environment file. The API
unit forces the nonsecret mode, origin and invitations-off settings. No config
value is read or installed by the package tooling. From the approved Linux
operator terminal, after confirming paths do not already exist:

```bash
sudo mkdir -m 0755 /opt/competence-hub-v2
sudo python3.12 "$TOOLS/v2_host.py" offline-install "${pkg[@]}" --runtime /opt/competence-hub-v2/runtime
sudo install -m 0644 "$FRESH_VERIFIED_DIR/deploy/v2/nginx.conf" /opt/competence-hub-v2/nginx.conf
for unit in competence-hub-v2-api.service competence-hub-v2-proxy.service; do
  sudo test ! -e "/etc/systemd/system/$unit"
  sudo test ! -L "/etc/systemd/system/$unit"
done
sudo install -m 0644 "$FRESH_VERIFIED_DIR"/deploy/v2/competence-hub-v2-{api,proxy}.service /etc/systemd/system/
sudo systemd-analyze verify /etc/systemd/system/competence-hub-v2-{api,proxy}.service
sudo systemctl daemon-reload
sudo systemctl start competence-hub-v2-proxy.service
python3.12 deploy/v2/v2_host.py host-check "${pkg[@]}" --phase active \
  --before host-before.json --before-sha256 "$HOST_BEFORE_SHA"
```

Do not enable either unit. Verify strict CA/hostname, pinned current leaf, wrong
host/untrusted CA rejection, `/health/ready`, Portal assets against the wheel,
anonymous session `401`, invitations closed, fresh synthetic MFA, RBAC and
Origin/CSRF denial, one company reservation/reviewer reply and persistence after
restarting only V2. Check the original reference (no source write beyond
explicitly permitted normal V1.2 authentication) and all six invocations. Keep
the authorized scope limited to the accepted, disposable synthetic test cohort.
Do not use production/real logins. Record actual results and stop on drift.

For the future client smoke in a **separate workstation terminal**, close only
the V1.2 local tunnel if it owns `8447`. Using the approved SSH destination and
known-hosts policy, open V2 with `ssh -N -o ExitOnForwardFailure=yes -L
127.0.0.1:8447:127.0.0.1:8444 "$approvedSshTarget"`. Keep the accepted CA
scoped to the V2 browser profile. Do not use a TLS bypass, global root install,
or certificate/key value on the command line. For CLI HTTPS trust/readiness from
that workstation use `curl --fail --cacert "$acceptedPublicCa"
https://localhost:8447/health/ready` and separately compare the peer leaf to the
accepted pin. The approved V1.2 access path remains the return route.

**Rollback:** close the V2 tunnel/profile, stop only the named V2 units in the
approved operator terminal, and reopen V1.2 using the [fixed starter](../handoffs/PORTAL_TESTZUGAENGE.md):

```bash
sudo systemctl stop competence-hub-v2-proxy.service competence-hub-v2-api.service
python3.12 deploy/v2/v2_host.py host-check "${pkg[@]}" --phase fallback \
  --before host-before.json --before-sha256 "$HOST_BEFORE_SHA"
```

Prove strict V1.2 HTTPS/readiness, exact V1.2 runtime and six services, original
27-table reference on the untouched `competence_hub_staging` and no V2
listeners. No database restore, drop, key rotation or deletion is part of
rollback. Retain the clone under the original protected custody; investigate
unexpected original DB drift under the accepted incident/restore procedure.

## Rehearsal Evidence and Handoff

Tooling verification is distinct from a release: the isolated Linux test uses a
disposable PG16 Unix socket, no network and no published ports. It seeds only
synthetic 0006 rows, proves an injected 0009 failure leaves no partial migration,
rejects a wrong clone and replayable cloned auth, applies 0007..0011, and verifies
the original DB dump is unchanged. The additional archive and offline Linux
install tests use a synthetic application wheel and the 25 real pinned cached
dependency wheels; unit syntax is checked without starting services. Six local
tests passed in 13.7 seconds; a separate wrapper run against the test ZIP passed
in 6.6 seconds. Host checks use simulated inventory; they do not prove actual
systemd state or VPS TLS. Both containers were removed. No shared test DB
or port 55433 is used. Reusable pattern: treat rollback to an unchanged original
and preservation of an additive clone as separate proofs, and bind both to the
exact verified bytes before handling operator approval.

The final archive was built from the exact tested Git object and passed the
independent offline Linux install check. The consolidated report pins the byte
hashes and identifies the source. The joint product acceptance is next;
any VPS preflight, durable clone, schema or activation scope still waits for
explicit grants and current evidence.
