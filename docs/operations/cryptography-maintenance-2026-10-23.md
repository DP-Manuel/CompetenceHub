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
unchanged at 49.0.0. Runtime pins unchanged except cryptography; pip26.2.1,
setuptools79.0.1, pytest8.4.2, Playwright1.63.0 and httpx0.28.1.
Initial full suite: 450 PASS,17 opt-in skips. Targeted crypto/auth/MFA/session/
token/lifecycle/TLS-helper regression:87 PASS, including an actual 49.0.0
synthetic envelope read under 50.0.2 with retained old-key support.

Disposable local PG16: actual factory/Login/MFA/CAL-1 Edge acceptance142 PASS,
native API17 PASS, cleanup PASS and owned container removed. This is new local
50.0.2 evidence, NOT a rerun against the remote VPS or a deployed Linux unit.
Runner now accepts an explicit isolated Python and sets/restores its source
import path instead of relying on the old editable venv installation.

Final Windows gates, artifact hashes and local Linux results are recorded below
after execution. Until then this document is preparation, not a completed gate.

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
