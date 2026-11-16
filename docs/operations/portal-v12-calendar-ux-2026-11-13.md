# CAL-1 V1.2 Calendar UX

Owner Manuel,13.11.2026. Local implementation/test/Git/package authorized. The
existing private VPS initially remains on accepted38153c1/V1.1. The old V1.1
grant did not authorize this new release. On15.11 Manuel explicitly granted
the single V1.2 window below. No real account, migration, Website/Pages or
GPG/USB action; actual deployment status is recorded separately from preparation.

## Proven Cancellation Failure

Unchanged bound V1.1 wheel was served locally with only synthetic APIs. A held
POST reproduces `aria-busy=true`, disabled Cancel/X and blocked Escape. Code:
`setBusy()` disabled every form control; `calendarCanClose()` rejected a busy
form unconditionally, and fetch had neither cancellation nor deadline. This is
a proven lock-in path, not a claim to know every detail of Manuel's original
network/input state. No additional original screenshot accompanied this request.
Own before screenshot: `release-artifacts/portal-v12-ux/before-v11-held-save.png`.

V1.2 keeps exit controls enabled, has one explicit accessible discard dialog,
and serializes repeated close requests. Keep editing/Escape preserve all input;
confirmed discard returns to overview, never deletes a saved draft. A held
response and30-second timeout are covered. Request cancellation only cancels the
client wait, not a possibly committed server write: a short warning requests an
overview check. An already persisted synthetic draft survives; a late reply
cannot close/overwrite a subsequently opened form. Logout invalidates outstanding
operations. Browser Back uses a same-page dialog-history marker; leaving the
entire page retains the browser's native unsaved-page protection.

## Visible Changes

- Date-only German input with locally shipped German Calendar, pointer/touch and
  roving day focus. Explicit start/end labels and turquoise intermediate range;
  one-day and year-boundary cases. No automatic date swapping/normalization.
- One24-hour clock per endpoint and decision deadline; defaults09/10/12:00,
  quarter-hour choices. Original arbitrary minutes/seconds/microseconds and DST
  instants remain intact when reopened/saved. API/persistence contracts unchanged.
- Errors target the actual component, e.g. Minute only rather than a valid date.
  Short text, optional examples, live correction and preserved inputs. All former
  business rules remain, including the three-month horizon and deadline rules.
- Presence/Hybrid show required venue and example before submission, a200-character
  counter, and no private access information. Online public note remains optional.
- Stable form order, compact headings, scrollable native dialog and reachable
  sticky Save/Cancel actions; no sticky title covering Calendar rows at200%.
- Existing local demo prefill adapted to these same controls. No duplicate UI
  architecture; [pinned dependency/license](portal-datepicker-dependency.md).

## Actual Browser Cases

| Case | Evidence | Result |
| --- | --- | --- |
| 1 | Date selected by Calendar; optional-summary one-day09–16 course saved | PASS |
| 2 | Multi-day endpoints/intermediate days, one stored offer | PASS |
| 3 | Optional drag deliberately not implemented; equivalent endpoint selection | N/A |
| 4 | One24-hour clock, hours00–23 and quarter choices | PASS |
| 5 | Venue requirement/example/count visible on format change | PASS |
| 6 | Short venue-only error and immediate correction | PASS |
| 7 | Missing minute marked alone, valid date/hour unmarked | PASS |
| 8 | Clean immediate cancel, dirty single choice/keep/discard | PASS |
| 9 | Exit after validation failure, saved draft preserved | PASS |
| 10 | Picker/form Escape and Browser Back keep/discard | PASS |
| 11 | Draft reopen/update, separate legacy18-minute/microsecond roundtrip | PASS |
| 12 | Changes requested, revision2, Reviewer publication and public detail | PASS |
| 13 | Real ICS download/sequence, native MFA/role/session checks | PASS |
| 14 | 390px, touch, keyboard, semantic names/errors, Reduced Motion, native200% | PASS |

Native PostgreSQL run:
`release-artifacts/portal-v12-ux/8f9948ab68d348d8bdff5943af14c899/report.json`.
SHA-256 `063704d4ee830aafd902491406c4ba0052c32fc4c20128c1c74ab35b3d7a2b5f`.
Repeated on committed source5a555e9; the deterministic sanitized report matches
the preceding run byte for byte. Screenshots in that same directory:
`desktop-validation.png`, `desktop-range.png`, `mobile-validation.png` and
`native200-picker.png`. Mobile and native200 images visually reviewed; at200%
the form/picker scrolls, its reachable action footer does not cover focused days.
Exact own fixture cleanup, container and volume removed. Includes native Coach
isolation404, logout401 and one-time Recovery resume only in the owned fixture.
This local proof's ephemeral self-signed TLS allowance is not remote TLS evidence.
Full NVDA/screenreader-software certification is not claimed; semantic/keyboard
checks are explicit. Supplemental source browser tests cover touch, year boundary,
legacy seconds, internal logout, repeated Cancel, pending reply and timeout.

The memory fixture omitted ICS publication sequence (default0); it now projects
the current revision, consistent with the native PostgreSQL contract. Actual
server/domain code was not changed. Do not weaken the expected revision2 check.

OSV npm1.3.4 query13.11 returned no advisories; this is a dated observation,
not a future security guarantee. Existing dependency/corporate CSP unchanged.

Targeted source/browser/export checks PASS(46,44 and final5-case runs), Node
German/DST/seconds regression and JavaScript syntax PASS. First full suite:
1761 PASS/30 expected skips, one pre-existing offline fake-process timeout test
failed before its PID marker was written within2seconds. The exact isolated
rerun PASS; no real GPG/USB/server process was involved or changed. The final
committed-source immutable-package full gate PASS:1763 tests,30 expected skips
in414.14seconds. Exact production/build dependency versions, pip check, compile
and fresh isolated wheel install PASS. No unrelated timeout assertion changed.

## Bound Local Release

Source commit `5a555e9a9aaeecd03ccfa0645929b58d95801488`, clean tracked inputs,
committed-only135-file export. Release candidate only; metadata explicitly says
`deployment_authorized=false`. Python package version remains0.1.0; V1.2 names
the Calendar UX feature, not a separate runtime/dependency version.

- ZIP: `release-artifacts/webapp/competence-hub-webapp-0.1.0-5a555e9a9aae-20261113T151526Z.zip`.
- ZIP SHA-256: `754322cd57ab0f121a85f1625c1681fd271ec9049fa5beda9024437e77bdea58`.
- Wheel SHA-256: `dfe5b94ef14895f45b16b1e6502688fff5e65a340d8766c97ec7fd57ef3c1714`.
- All ten changed/new public UI assets, including license, compared byte for byte
  between actual wheel and source: PASS. No credentials/private artifacts bundled.
- Linux evidence: `release-artifacts/webapp-linux/20261113T151559Z-1a2ef9ab/local-summary.json`.
- Linux summary SHA-256: `5ddf14544645b490f71b01cc74472cb39b12c4e011f75f2855fe80a9a7fdb55f`.

Actual packaged Ubuntu runtime, locked Linux wheels/published hashes/advisory
snapshot, offline venv/pip and37 Nginx/HTTPS/Auth/CSRF/RBAC/logout/PG cleanup
checks PASS. Own Linux container removed; separate native PostgreSQL container
and volume removed, labeled inventory independently empty. No VPS action.

A separate local in-memory synthetic Firefox preview opens Coach/Reviewer views
with its own ephemeral trusted certificate/profile. It is not the existing VPS
pilot and does not import its private credentials. Its live address/status are
ephemeral under ignored `.tmp/v12-local-preview`; closing its own windows stops
its local server and discards synthetic state. Existing VPS windows stay intact.

## One Deployment Gate

V1.2 server update AUTHORIZED15.11 and now actually accepted below. At preparation
it was NOT_RUN; local proofs alone were not deployment. Exactly one controlled
V1.1→V1.2 private pilot window. Inputs: explicit new Owner grant, verified
candidate/hash, current accepted predecessor38153c1 and
receipt6554531a…/SHAd25223b0…, original CA/leaf, current suitable protected restore
proof. Manual tests may have changed data; do not reuse an older mismatching dump.

Deliverables/DoD: retain V1.1 as code rollback, preserve all original users/offers/
configuration/keys, separate synthetic acceptance/cohort cleanup, all14 cases
with drag N/A, MFA/RBAC/ICS/restart, six services and strict HTTPS. No installer,
new DB, migration, real identity, delivery, public port or Website action. No
operating command without the bound preflight; an open tunnel alone is not grant.

## Granted Window15.11

Manuel explicitly approved target `competence_hub_staging`, candidate ZIP/SHA
above, suitable current DPAPI/BitLocker backup with isolated exact restore if
needed, incremental runtime activation, own synthetic acceptance/cleanup and
original manual-access windows. No repeat Owner grant for those exact steps.

Read-only actual SSH15.11: V1.1 ExecStart, precisely20-v1 and22-v11 overrides,
six services active; API8001/proxy8443/PG5432 loopback only. Package and Linux
wheelhouse inventory hashes agree. Existing V1.1 evidence includes subsequent
normal role logins/manual testing, so do not treat its earlier pre-update data
snapshot as a current rollback baseline. The operating window obtains/proves the
current baseline without restoring or changing source data.

The existing update operator gains a bound V12 profile, not a new installer.
Only24-v12-runtime.conf is added;20-v1,22-v11 and both old installed/wheel copies
must validate exactly and remain retained. Unknown drops, already staged V1.2,
changed predecessors/identity/configuration or wrong target stop before writes.
On a failed acceptance, remove only the owned24-v12 override and own test cohort,
restart the previous V1.1 runtime and verify reference/health; never automatically
restore an older source database. Retain the deeper reviewed V1 as requested.

Remote Calendar acceptance reuses the existing61-check native security/CAL suite
through a date-only input adapter, then the same14 V1.2 cases with strict browser
CA/hostname checking, actual touch and native200%. Local ephemeral TLS bypasses
are not used on the VPS. Invitations remain closed throughout. Only a successful
server ACK and reference/health gate permit opening the original four logins;
those normal MFA/session/audit updates are expected, business rows are unchanged.

Entry: `deploy/scripts/run-vps-v12-update.ps1`, same-user elevated PowerShell7,
exact committed operator HEAD and quiet original pilot. One existing VPS sudo
prompt if required; no application/database/GPG password or login reset. Manual
starter receipt/runtime pin is updated only after actual accepted V1.2 evidence.

### Verified Operating Preparation

15.11 focused operating/access/browser/dependency regressions:85+68+12 PASS;
compilation, context/archive/link and diff checks PASS. Actual isolated Python
`-I -X utf8` import checked, so shared browser cases do not rely on a development
`sys.path`. Immutable application package/full1763+30 evidence above reused;
no application rebuild or unneeded repeat full suite. Initial local rehearsal
could not start with Docker Desktop stopped; engine started, no VPS mutation.

Actual local V1.1→V1.2 update, native PostgreSQL/strict TLS61 security/CAL checks,
shared13 UX PASS/drag N/A, actual390 touch/native200, current exact restore,
reference cleanup and normal original four-role access PASS.
Report `.tmp/ch-pilot-proof-ea3e832cd1ad47d1b230971a4930cb1e/result.json`,
SHA-256 `2cfa5afccf1e55041c9ad6d41e95481f18ceda3f777cd170e2ed277ca9b6f296`.

Separate actual rollback restores V1.1, all27 reference tables identical:
`.tmp/ch-pilot-proof-c739d45f26664220b668650f8163e48b/result.json`,
SHA-256 `783b52f65c58248c59a67a8c33eff303589162a76b89ed209582702be4ba0ff9`.
Both own containers removed and independently absent. These local proofs use a
process-service shim and synthetic AES instead of actual systemd/Windows DPAPI;
not claimed as real VPS/BitLocker/Owner-secret evidence. Actual operating window
was NOT_RUN at this checkpoint; the following is its separate real receipt/ACK.

## V1.2 Tatsächlich Abgenommen

15.11.2026,22:52 MEZ. Actual receipt
`release-artifacts/vps-v12-update/ab60077be6fb41cebce020168c2eff89.json`,
SHA-256 `0a034aae3d1e351f4a5a9868592beda933acbb580658b14863f4362014190a4e`.
Operator `efc3508b606a02913e940a86c63c6cfe61196bd3`, application5a555e9 and exact
ZIP SHA754322cd… as fully recorded above. `VPS_V12_UPDATE=PASS`, server ACK and
`PILOT_ACCESS=PASS`; no repeat installation or extra Owner/password dialog.

- Current27-table protected DPAPI/BitLocker backup and isolated exact restore
  PASS: all row hashes, schema/rights, format and sequence state equal; source
  unchanged and private probe removed. No source-database restoration.
- Actual native remote61 CAL/security checks and13 V1.2 cases PASS, optional
  drag N/A. German pointer/range dates, one-/multi-day,24h/quarters, targeted
  compact errors/venue hints, cancel/keep/discard/ESC/back after errors, reopen,
  changes-requested/revision/Reviewer/publication/ICS,390px/touch/keyboard/
  semantic checks/Reduced Motion and native200% all exercised on the VPS.
- MFA, exact RBAC/Coach isolation, CSRF/Origin, sessions/logout/one-time recovery,
  actual backend restart and PostgreSQL publication/session persistence PASS.
  Recovery used only on the owned temporary cohort, never original access copies.
- Scoped cohort cleanup/reference gate PASS:26 tables' original rows preserved,
  shared synthetic-IP security counters retained, sequences not rewound. Original
  four users/two Coaches and saved manual offers preserved. Configuration and
  application keys unchanged; own log secret scan PASS. No migrations.
- Independent post-receipt strict CA/hostname/leaf and negative certificate
  controls, all13 served UI assets byte-equal to exact wheel, anonymous session401
  and closed invitation503 PASS. No certificate bypass or global trust install.
- Independent SSH confirms six active services, actual5a555e9 ExecStart, retained
 20-v1/22-v11 beneath24-v12, unchanged listeners and loopback API8001/proxy8443/
  PG5432. Chatbot8000 and external existing web/SSH services unaffected.
- V1.1 is immediate code rollback, reviewed V1 remains deeper retained fallback;
  neither removed or overwritten. No real rollback required; local rollback
  above proves all27 original tables equal and actual V1.1 restarted.
- Original Admin/Reviewer/two Coach windows plus public Calendar opened normally
  via existing password/TOTP after the preservation gate. Expected new auth/MFA/
  audit activity only, no reset/new account/recovery consumption. Terminal34100
  intentionally held; Enter closes only this local access, not VPS services.

Fixed [test entry](../handoffs/PORTAL_TESTZUGAENGE.md) and later opener now bind
this actual receipt and V1.2 Calendar asset, not a candidate or V1.1. No further
installation needed for manual testing. Final115 access/operator/startup
regressions PASS; actual public receipt/runtime pin independently verified
without credential access. Actual owned remote mobile/native200 screenshots
visually reviewed: compact minute-only error, scrollable picker, reachable footer.
No full NVDA/screenreader-product certification claimed.
No real identity/import, invitations,
public activation, IONOS/Pages, GPG/USB or backup-job change. TLS expiry24.11 and
EDV app-domain/SMTP remain explicit external gates, not waived by private access.

## Fachliche Abnahme16.11

Manuel berichtet am16.11: Janay hat den vorgeführten Kalender-/Portalablauf
abgesegnet. Fachliche V1.2-Abnahme damit geschlossen; Manuels positive optische
Rückmeldung vom15.11 bleibt zusätzlich dokumentiert. Dies ist eine gemeldete
Stakeholderfreigabe, kein neuer technischer Einzeltest oder weiterer Testlauf.
Bestehende1763 lokale Tests/13 Bedienfälle und die tatsächliche VPS-Abnahme
werden gemäß [Teststrategie](../requirements/calendar-quality-plan-v0.1.md#risk-based-evidence-reuse)
wiederverwendet; keine erneute Demo-/Abnahmefreigabeschleife erforderlich.

EDV weiterhin offen: Manuel korrigiert am16.11 die versehentlich ausgewählte
Antwort ausdrücklich; es liegt noch keine EDV-Bestätigung vor. Kein Hostname,
TLS-/Zugriffskonzept oder SMTP-Verfahren gilt dadurch als bestätigt. Private
TLS-Frist24.11 bleibt sichtbar. Keine Serveraktion, neue Rolle oder Einladung.

Genau nächster Block: die bestätigten nicht geheimen EDV-Eingaben mit dem
vorhandenen [Aktivierungsvertrag](../requirements/activation-input-contract-2026-08-24.md)
abgleichen. Input: App-FQDN/DNS-Ziel, TLS/Zugriffsschutz und SMTP-/Absendervertrag,
Secrets nur extern. Ergebnis/DoD: vollständige Inputmatrix und gezielter
Konfigurations-/Smoke-Plan im bestehenden Verfahren, oder exakt fehlende Angaben.
Bis dahin persönliche Aktivierung, Coachzuordnungen und öffentliche Freigabe aus.
