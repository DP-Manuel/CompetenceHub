# Integrated Staging Pilot: Delivery Record

Date:09.11.2026. **LOCAL CANDIDATE VERIFIED; VPS ACTIVATION HELD.**

## Source And Package

- Application source: `0080195755e3d0fff97c5442bd5e6a09ea0fbf8c`.
- Package: `release-artifacts/webapp/competence-hub-webapp-0.1.0-0080195755e3-20261109T182244Z.zip`.
- ZIP SHA-256: `f3478fc34de4647fd182a9c7262678b8de2e6b194428ec7dbcc0a116d9c51c41`.
- Wheel SHA-256: `a614ff69100641419a47cc068543bd65c31ff20c56989adaadffe9460f0dd646`.
-119 allowlisted committed Git inputs. No private sources, secrets, fixture
  scripts or unknown working-tree inputs. Manifest dirty=false and
  deployment_authorized=false: the actual operating gates are not closed.
- Later evidence-only commit adds this record and tour screenshot capture;
  it does not change the application source contained in the package.

## Implemented Versus Active

| Area | Actual result |
| --- | --- |
| Coach/Reviewer/Admin introductions | Three optional native modal tours, local SQL/browser PASS; no automatic startup or personal storage |
| Role dashboards | Scoped current-revision SQL counts; Admin paginated account/role/UUID/status list, not a complete audit viewer |
| First access | Inactive invitations for exactly Intern/Reviewer/explicit UUID-linked Coach; one-time token, personal password, native MFA/recovery; default delivery hold |
| First real Admin | Not created; existing protected CLI is not a newly implemented token-first Admin bootstrap. Reconcile actual first-Admin activation before live operation |
| Full Calendar workflow | Real local SQL and packaged public page: create, review, publish, multiday/month overlap, ICS, request draft, revision, withdrawal, restart PASS |
| VPS application / Staging URL | Not installed; no working Staging Portal URL claimed |
| Existing VPS services | Read-only pre/post checks PASS, unchanged by this batch |
| Current remote backup/restore | Not executed or proven; protected operating gate remains OPEN |
| Real accounts / dispatch | None created/activated/sent; Janay recipient/channel and per-Coach UUID ownership still need confirmation |
| IONOS / Pages / R2 / import | No deployment, key action, migration or real import |

No shared passwords or general activation links are delivered. In the synthetic
proof alone, encrypted outbox payloads were consumed in memory without SMTP or
token output. That mechanism is NOT a manual real-user delivery workaround.

## Executed Verification

- Final release build: **1481 PASS,30 expected external opt-in skips**; pip check,
  compile, fresh wheel installation/import and fail-closed configuration PASS.
- Earlier full run1476/30 and later focused89/0 are separate dated runs, not
  additional unique test totals. One intervening focused run88/1 skipped only
  its occupied dedicated local port while the owned SQL fixture was running.
- **98 integrated +46 Calendar native SQL/browser checks**, plus **3 real
  PostgreSQL API tests**. Actual390px, native200% (707 CSSpx/DPR2), keyboard,
  focus, absent tour targets, close/skip/restart, Reduced Motion and text-range
  geometry tested. Published API fields only; no customer request persistence.
- Existing multiday renderer26 JS tests and34 Website contracts PASS. Website,
  Pages workflow, deployed Nginx/systemd templates and migrations unchanged.
- Native report: `release-artifacts/integrated-pilot-20261109/report.json`.
  SHA-256: `c51939a84abf5270d18f33e4b69ff9b9828dc2ef143360f852756b6d53d51e72`.
  Own PostgreSQL16.15 container/volume removed,20 dynamic areas zero, temporary
  browser/TLS contexts removed. Native restart preserves data within the run.
- Actual current-package Ubuntu24.04/Python3.12 fresh install/offline dependencies,
  exact upstream wheel hashes/advisory snapshot, real HTTPS Nginx/PG/runtime:
  **37 checks PASS**. Cookie scope, Origin/CSRF, revoked sessions, pure-role MFA,
  spoofed forwarded headers, loopback and zero residue included.
- Linux evidence: `release-artifacts/webapp-linux/20261109T182331Z-7c8e9560`.
  proxy-result SHA-256: `ebbd1fff13a5312a2cdd14e630492da858e3cc433bd9b79c4dd97a16cf4e3530`.
  wheelhouse INVENTORY SHA-256: `98e85f0832b2769408cabcaf531b875913cd775e7961e5c52cdfb2e37a8b609f`.
  Own container removed; no host mount/published port, runtime network disconnected.
  systemd unit syntax is proven, **not** activation/hardening under VPS PID1.
- Real Screenreader-product acceptance and Outlook Desktop import/reimport remain
  open. RFC/ICS parsing and actual browser download are proven, not client sync.

## Short Guides And Janay PDF

[Manuel](../operations/pilot-admin-guide.md),
[Janay](../operations/pilot-janay-guide.md),
[Coaches](../operations/pilot-coach-guide.md),
[first activation/support](../operations/pilot-first-activation.md).

Sendable local PDF: `release-artifacts/integrated-pilot-20261109/Janay-Kalenderpruefung.pdf`.
One A4 page, tagged PDF, no JavaScript, visually rendered/inspected. Generated
from the single canonical Janay guide, not an independently maintained copy.
SHA-256: `bfba4a758614768f34063616d60dc79b2cb397a8708c768642670413f86f56a9`.
Actual tour screenshots include mobile Reviewer/Coach, Desktop Admin and native200%.

## Optional Local Demonstration

Terminal A: one PowerShell window, any working directory, Docker Desktop running.
Existing project Python/Node/browser dependencies required. No real passwords.

```powershell
& 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp\.venv\Scripts\python.exe' 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp\scripts\run-cal1-pilot.py'
```

Expected: `LOCAL_POSTGRES_DEMO: https://127.0.0.1:8447/demo/public/`.
Packaged pilot Calendar: `https://127.0.0.1:8447/portal/calendar-public.html`.
Only this generated loopback test certificate may need the existing local test
exception; never apply a general certificate bypass. Synthetic users/password
are available under `/demo/#zugang`; native MFA uses an authenticator app,
not123456. No personal passwords or real customer data. Keep Terminal A open.
Ctrl+C intentionally removes this owned demonstration DB/container/volume;
it does not stop or alter any VPS service. This is not the deployed Staging URL.

The existing [six-step demonstration](2026-11-06-cal1-pilot-readiness.md#vorführung-in-sechs-schritten)
remains the functional acceptance sequence. Tours are optional under Help.

## One Next Block

LATEST ACTUAL20:48 UTC: current temporary backup+exact-file isolated VPS restore
accepted, report/ciphertext hashes and private ACLs independently verified;
27 tables/schema/rights/data/sequences equal, source unchanged/probe removed.
Four foreign services healthy20:52. **Do not repeat the backup or GPG workflow.**
Next is own private pilot installation + native synthetic acceptance, using the
same bound source package and retained configuration. Reals/IONOS/Pages held.
The [actual evidence and precise next scope](../operations/integrated-staging-pilot-2026-11-09.md#echter-sicherungs-und-restorenachweis-akzeptiert)
supersedes the same-day missing-real-restore observations immediately below.

Latest same-day reply resolves the prior input question: no external domain/TLS,
network destination or current real restore proof exists. The subsequently
verified [one private technical-pilot proposal](../operations/integrated-staging-pilot-2026-11-09.md#ein-vorschlag-begrenzter-privater-technischer-pilot)
now owns the precise next scope. Local-only proof: 14 recovery + 5 SSH/TLS + 37 native
checks and 159 targeted tests PASS; 40 tables/data/schema/effective rights match.
No real backup target is qualified; DPAPI is only a temporary user/machine-bound
candidate, not permanent independent recovery. Existing package remains unchanged.

**Protected Staging operating window**, not another architecture/key sprint.
Inputs: confirmed HTTPS/access path, current suitable protected snapshot and
isolated restore path, safe retained application configuration and one private
sudo window. Deliverable/DoD: actual schema/rights inventory, proven recovery,
own-service install, synthetic remote end-to-end checks, unchanged co-hosts and
explicit real-recipient/first-Admin gates. The consolidated Manuel question has
been asked; no password requested. [Exact ordered release/rollback boundary](../operations/integrated-staging-pilot-2026-11-09.md).
