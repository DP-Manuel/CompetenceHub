# Cryptography Maintenance: 23.10.2026

Scope: isolated security maintenance and local Linux/proxy preparation only.
No VPS installation, DNS/ACME operation, real identity/data or IONOS change.

## Usage And Compatibility

Direct runtime dependency: 49.0.0 -> reviewed candidate 50.0.2; project range
>=50.0.2,<51. Classification B: AESGCM/InvalidTag for authenticated CHT1
TOTP/outbox envelopes; affected PKCS#7 application path not found in current
runtime. No Fernet, RSA PKCS1v1.5 decrypt or external certificate/key loading
ingress found. Local browser fixtures generate RSA/PKCS8 and parse X.509.

Primary sources checked 23.10:
- [Maintainer advisory](https://github.com/pyca/cryptography/security/advisories/GHSA-g6cj-pr64-35w5):
  GHSA-g6cj-pr64-35w5 / CVE-2026-69247; fixed from 50.0.0. Distinguishable
  unwrap errors/timing on attacker-controlled PKCS#7 EnvelopedData are the
  relevant precondition, not ordinary AES-GCM use.
- [Release notes](https://cryptography.io/en/latest/changelog/#v50-0-2):
  50.0.2 wheels use OpenSSL 4.0.3. FFDH deprecation and stricter DER/SCT
  parsing do not affect the inspected runtime. No FIPS/legacy-provider
  deployment claim is made. We use binary wheels, not an unreviewed Rust build.
- [Exact release metadata](https://pypi.org/pypi/cryptography/50.0.2/json):
  compatible CPython Windows and Linux wheels; Python >=3.9 versus project
  >=3.11,<3.14. Linux target remains Ubuntu24.04/Python3.12 x86_64.

Existing 49.x severity-source discrepancy and failed 22.10 artifacts remain
historical evidence in the [original assessment](../architecture/webapp-dependency-assessment-2026-10-22.md).
No exploitability claim or advisory waiver follows from the bounded search.

## Isolated Evidence

Fresh Windows Python3.11.15 venv `.tmp/crypto-50-review`; original `.venv`
was left unchanged at 49.0.0 until isolated compatibility/regression passed.
After that proof the normal local `.venv` was promoted to 50.0.2 and its
editable application metadata refreshed without changing other dependencies;
pip check PASS. Runtime pins unchanged except cryptography; pip26.2.1,
setuptools79.0.1, pytest8.4.2, Playwright1.63.0 and httpx0.28.1.
Initial full suite: 450 PASS,17 opt-in skips. Targeted crypto/auth/MFA/session/
token/lifecycle/TLS-helper regression:87 PASS, including an actual 49.0.0
synthetic envelope read under 50.0.2 with retained old-key support.

Disposable local PG16: actual factory/Login/MFA/CAL-1 Edge acceptance142 PASS,
native API17 PASS, cleanup PASS and owned container removed. This is new local
50.0.2 evidence, NOT a rerun against the remote VPS or a deployed Linux unit.
Runner now accepts an explicit isolated Python and sets/restores its source
import path instead of relying on the old editable venv installation.

Final security-only Windows suite:451 PASS,17 opt-in skips;57 existing visual
Edge checks and the explicit six-second submit latency regression PASS.
Compileall, pip check and Portal JS syntax PASS. Subsequent COACH-1 local tests
are separate evidence, not retroactively added to the security package's count.

## Reproducible Package And Local Linux Result

Both clean Git-source builds from `99c81cce0923cf38a75b57edc6f7836bbb611ccd`
exported90 allowlisted inputs and produced identical app wheels and ZIPs:

- Build A: `competence-hub-webapp-0.1.0-99c81cce0923-20261023T082735Z.zip`
- Build B: `competence-hub-webapp-0.1.0-99c81cce0923-20261023T082902Z.zip`
- Both ZIP SHA-256: `34b250d9e147f234087353feff78fd0aff9bc48ce509f202f859a57773b5a241`
- App wheel SHA-256: `98abcb67ff1cb7c5c7b53c5ea2aec5a7da1f49777fd95b6190928b29f3bb8c4c`

These are security-baseline test candidates, with deployment_authorized=false;
they do NOT contain the following COACH-1 implementation/migration0007.
Do not use old vulnerable22.10 packages as rollout/rollback targets.

Successful local evidence: `release-artifacts/webapp-linux/20261023T083203Z-49e1a955`.
Exact release inventory,23 runtime binary wheels, their published PyPI hashes
and advisory metadata PASS; no advisory entries in that snapshot, including
no remaining GHSA-g6cj-pr64-35w5 entry. This is a dated feed check, not an
absolute claim that no vulnerability exists. No new scanner/global tool added.

Fresh Ubuntu24.04/Python3.12.3 venv, offline hash-required install, pip check,
actual packaged API+PG startup and Nginx1.24 HTTPS proxy: PASS,37 checks.
Native MFA/enrollment/recovery generation, Secure/HttpOnly/Host-only cookies,
session resume, CSRF/Origin rejection, unchanged Calendar role boundaries,
forwarded-header spoof resistance, minimal health/no-store/security headers,
loopback binding and exact20-table zero-residue checks all passed.
The Docker network was disconnected before runtime tests; no published host
port or host filesystem mount. Owned container removed PASS.

systemd255 unit syntax verification PASS, NOT service activation or effective
hardening under systemd PID1. TLS used a disposable localhost self-signed test
certificate only; no ACME request/public certificate/host configuration.
Actual tested image: `sha256:17228a886f219fb43029846aa744aa7b5a2e7885cb1dae7a8efcb55519e16543`.

Evidence SHA-256:
- proxy-result.json: `ebbd1fff13a5312a2cdd14e630492da858e3cc433bd9b79c4dd97a16cf4e3530`
- wheelhouse/INVENTORY.json: `a116bed4fe5ab1f54c6a71d9a9fb2f2932980c02ed3ed827824e21b07c1bcea8`
- platform hashed lock: `0bfe5c3e53b6818ac55e60093310c106c73dab1ceea942eae92b64e32bf81263`

First local Linux attempt failed on a harness expectation: wrong MFA challenge
CSRF is generically401/authentication_failed in the existing contract, not403.
Updated the harness to assert exact401/code; no application permission weakened.
The repaired complete run passed. Earlier failed evidence is retained separately.
The final CAL-1 rerun also exposed a query-time race at the exact sampled-now
boundary. The API correctly rejects past public windows. The harness now samples
once and requests days1..80, with101ms/30s clock-advance regression; no server
clock or application validation changed. Repaired native-local142 and API17
checks passed with all20 counts zero and owned-container removal.

23.10 read-only VPS recheck: four co-hosted services active, Python3.12.3,
Chatbot127.0.0.1:8000 and PG127.0.0.1:5432;8001 still unused at that instant.
No VPS files/services/users/network configuration changed. Port suitability
still needs a collision check immediately before any later approved start.
Proposed hostname A lookup via1.1.1.1 remains NXDOMAIN; no hostname is finalized.

## Gate Conclusion

Cryptography compatibility, advisory guard, reproducible builds and LOCAL
Linux/proxy runtime gate are complete. The next VPS rehearsal remains separate
and unexecuted; domain/TLS/ownership inputs remain open. The actual source,
artifact, privilege and rollback scope must be approved for that later window.
This report does not authorize deployment of either candidate or COACH-1.

## EDV: One Input Package

Betreff: App-Domain und TLS für das Competence-Hub-Portal abstimmen

Hallo Herr Roß,

für die getrennte Portal-Webapp benötigen wir bitte eine Rückmeldung zu:

1. Hostname: Vorschlag `competencehub-app.donner-partner.de`; bitte final bestätigen.
2. DNS-Eintrag: A-Record; AAAA nur nach gesondert bestätigtem IPv6-Betriebsweg.
3. Ziel-IP: `217.160.255.86` (VPS, nicht der IONOS-Website-Webspace).
4. TLS-Modell: eigenes Zertifikat per ACME am VPS oder ein von Ihnen vorgegebenes Modell?
5. Erneuerung: Wer übernimmt automatische Verlängerung und Fehlerbenachrichtigung?
6. Reverse Proxy: Wer verantwortet den eigenen Nginx-Host und dessen Freigabe?

Vielen Dank und viele Grüße
Manuel Rödel

## Remaining Gate

The final app hostname, DNS and TLS/renewal/proxy ownership remain external.
An isolated later VPS loopback/header probe would be technically useful before
public DNS, but is NOT executed or approved here. A localhost test certificate
inside a disposable local container is not a public certificate order.
Activation additionally retains separate mail/backup/privacy/account gates;
domain/TLS are not the only outstanding production inputs.
