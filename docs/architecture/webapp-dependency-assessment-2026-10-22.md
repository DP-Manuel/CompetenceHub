# Webapp Dependency Gate: 22.10.2026

Historical finding. The separately authorized 23.10 maintenance and current
verification are owned by the [maintenance report](../operations/cryptography-maintenance-2026-10-23.md).
The original stopped artifacts below must not be reused.

Status: **LINUX PACKAGE GATE BLOCKED**, not a finding of an exposed production
Portal. No dependency upgrade, risk waiver or server installation is authorized
by this report. Native CAL-1 evidence remains dated evidence for its tested code.

## Observed Gate

The new local Ubuntu preparation downloaded the 24 exact runtime wheel pins,
cross-checked their SHA-256 against PyPI release metadata and emitted an offline
hashed lock. Before creating/installing the runtime venv or starting PostgreSQL,
the advisory guard stopped on cryptography 49.0.0. The owned container was then
removed. No test user/data/runtime/proxy was created by that failed preparation.
The public wheelhouse is retained only as blocked local evidence, not an approved
installation source.

PyPI lists GHSA-g6cj-pr64-35w5 and PYSEC-2026-3552 for that version. These are
aliases for one reviewed issue, not two independent vulnerabilities. The
[maintainer advisory](https://github.com/pyca/cryptography/security/advisories/GHSA-g6cj-pr64-35w5)
identifies PKCS#7 EnvelopedData decryption and a fix in 50.0.0. Its displayed
severity is Moderate, while the [GitHub reviewed database](https://github.com/advisories/GHSA-g6cj-pr64-35w5)
displays High/8.2. Preserve that source discrepancy; do not silently choose a
lower rating or convert an advisory count into an application exploit claim.

## Bounded Reachability Review

Application imports use cryptography's AESGCM and InvalidTag in
apps/webapp/src/competence_hub_api/security/secret_encryption.py for the
authenticated, versioned TOTP/outbox envelope. Static search of current runtime
source found no pkcs7, pkcs7_decrypt or S/MIME/EnvelopedData processing. The
maintainer describes exploit preconditions involving untrusted EnvelopedData
decryption; no such ingress/code path was found in this bounded application
inspection. That is an inference from inspected code, not a universal security
proof or permission to ignore the package advisory.

## Required Next Slice

The current project metadata deliberately requires cryptography >=49,<50 and
the runtime lock fixes 49.0.0. Moving to 50 is therefore a reviewed major-version
maintenance slice, not a harmless installer flag. Do not bypass the local guard,
silently change the lock, install latest, or declare the blocked wheelhouse safe.

Recommended separate authorization: update to an explicitly reviewed patched
version, reconcile metadata/runtime pins and platform wheels, verify envelope
compatibility/key versions, rerun secret-encryption/TOTP/recovery/outbox and full
local tests, rebuild reproducibly and repeat affected native Staging gates in
one prepared window. Preserve previous encrypted data compatibility. No real
data, productive keys, deployment or migration is needed for that maintenance.

If a risk exception is requested instead, the security owner must explicitly
approve its scope/expiry/evidence; no exception is recorded or implemented here.
After resolution regenerate the release and Linux wheelhouse before asking for
the Linux/proxy execution approval. Existing blocked ZIPs are not rollout or
rollback candidates.

## Evidence

Ignored local evidence directory:
release-artifacts/webapp-linux/20261022T131402Z-fe909313.
preparation-failure.json records RuntimeError at the advisory guard; no exception
contents, credentials or raw database data are retained. local-summary.json
records package failure, proxy not run, owned-container removal PASS and no VPS
change. Wheelhouse inventory/hashed lock identify exact public downloads.
Their hashes and measured build results are in the
[Linux readiness report](../operations/cal1-linux-proxy-readiness-2026-10-22.md).
