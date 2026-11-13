# CAL-1 V1.2 Calendar UX

Owner Manuel,13.11.2026. Local implementation/test/Git/package authorized. The
existing private VPS remains on accepted38153c1/V1.1, tunnel and four original
role windows untouched. The old V1.1 grant does not authorize this new release.
No real account, migration, Website/Pages, GPG/USB or remote database action.

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

V1.2 server update NOT AUTHORIZED/NOT_RUN. After bound package and Linux evidence,
recommend exactly one controlled V1.1→V1.2 private pilot window. Inputs: explicit
new Owner grant, verified candidate/hash, current accepted predecessor38153c1 and
receipt6554531a…/SHAd25223b0…, original CA/leaf, current suitable protected restore
proof. Manual tests may have changed data; do not reuse an older mismatching dump.

Deliverables/DoD: retain V1.1 as code rollback, preserve all original users/offers/
configuration/keys, separate synthetic acceptance/cohort cleanup, all14 cases
with drag N/A, MFA/RBAC/ICS/restart, six services and strict HTTPS. No installer,
new DB, migration, real identity, delivery, public port or Website action. No
new operating command before this gate; an open tunnel is availability, not grant.
