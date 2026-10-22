# CAL-1 Access And Batched Acceptance

Date: 2026-10-22. Local gate **PASS**. Native VPS-backed runtime/UI gate **PASS**.
The repaired run completed 142 browser checks, the 17-test API gate and every
cleanup/SQL/health check. This is not a deployed Linux/proxy or production gate.
Authority: Manuel's Calendar Access Contract and subsequent Batched Development
addendum. The latter replaces the local-only stop and authorizes scoped commits,
push, Pages preview publication and one synthetic Staging window. Production,
real identities/mappings and productive mail/tracking remain prohibited.

## Implementation And Root Cause

The 21.10 preflight finding was genuine: Login, PostgreSQL MFA and session resume
admitted admin/internal only, while the visual fixture simulated broader access.
Calendar endpoint authorization alone could not close that authentication gap.

The [canonical supplement](calendar-cal1-technical-design-v0.1.md) defines explicit
internal and additive Portal admission policies. `/api/v1/portal/access` reuses
the real password/MFA/session handlers with the latter; `/api/v1/auth` retains
the former. The shell uses the additive endpoints. No internal grants, new
roles, guessed Coach mappings or migration. Company/contact/Admin and Calendar
ownership remain separate live database authorization boundaries.

The visual fixture shares the admission policy but still simulates MFA; it is
only visual evidence. The native harness creates the unchanged runtime factory
and actual PostgreSQL repositories, enters password/TOTP through the browser,
and tests resume, real recovery, expiry, replay, role removal and logout.

One scoped hardening followed an actual local failure: PostgreSQL error DETAIL
can contain complete rows even when SQL bind values are hidden. The application
now returns a generic 503 and logs only an exception type, protected by a test.
No raw row, password, challenge, provisioning URI or recovery value is evidence.

## Local Evidence

| Gate | Actual result |
| --- | --- |
| Complete local pytest | 424 passed; 17 expected Staging skips |
| Existing Edge visual fixture | 57/57, including revision actions and company regression |
| Real-runtime / local PostgreSQL browser rehearsal | 142/142 in Edge; not VPS acceptance |
| PostgreSQL API tests in same local rehearsal | 17/17; 424 local tests deselected |
| Real-runtime / VPS Staging PostgreSQL browser acceptance | 142/142 in Edge 155.0.4283.62 |
| VPS Staging API regression | PASS, 17-test gate; batch native_api_exit=0 |
| VPS post-regression | 424 passed, 17 deselected in 7.46s; compile/pip/JS/latency/diff PASS |
| Local cleanup | All 20 dynamic table counts zero; 65 audit events observed before exact-ID cleanup |
| Python compile, pip consistency, JS syntax | PASS |
| Slow-response harness regression | PASS after correction; successful 6-second submit plus delayed list refresh |
| Preview UX | 134 local and 134 public focused checks; see [preview QA](github-pages-preview-2026-10-21.md) |

The rehearsal uses the already-available `postgres:16-bookworm` image in a fresh
container with tmpfs database storage, no host-volume mount, and only a
127.0.0.1:55433 host binding. Existing bootstrap/migrations 0001-0006 are applied
only there. Generated passwords live in process memory/environment, not command
arguments or files. The exact owned container is removed in `finally`.
Ignored evidence: `release-artifacts/cal1-local-pg-rehearsal-20261022/result.json`.

Harness repairs discovered during rehearsal, not product findings:

- Database triggers use real database time. A future injected test clock violated
  a legitimate timestamp constraint; the harness now samples `clock_timestamp()`.
- Sync Playwright owns an event loop. Synchronous operator database steps use a
  separate worker/short-lived engine rather than nesting `asyncio.run` on it.
- Native UI waits use the actual response plus loading/updated UI state instead
  of network-idle assumptions or fixed sleeps. All original assertions remain.
- Real 200% zoom uses a temporary browser profile and verifies measured CSS
  viewport/DPR; a separate viewport reflow check is not mislabeled as zoom.

## First VPS Attempt And Repair

The first actual VPS attempt passed unauthenticated denial, real Coach MFA
enrollment, exact Coach session resume, no Web Storage, no-store and empty state.
An AssertionError then stopped initial offer preparation. The first report did
not retain a safe traceback frame, so it does not identify the exact failed
assertion. No claim of complete native acceptance follows.

Independent postflight proved all 20 dynamic tables zero, migrations 0001-0006,
27 owner tables, SHOW listen_addresses=localhost, four active services and
loopback-only listener. Local post-regression: 424 passed, 17 deselected. API
suite was correctly NOT RUN after browser failure. The owned tunnel closed
only after those cleanup/health checks.

A controlled local reproduction proved a harness defect: a successful submit
delayed six seconds exceeded the old five-second status assertion. Mutation
success/dialog closure also preceded the list reload. The shared helpers now
await the concrete successful list GET and loading completion before unchanged
workflow assertions; native initial creation and review use the same boundary.
This is the best-supported cause, not retrospective proof of the lost VPS stack.
All 57 visual checks, 142 local-PG browser checks, 17 local-PG API tests and the
424-test suite passed again after repair. The dedicated latency regression is
part of the batch. No application permission or workflow logic changed.

Failure evidence now includes per-initial-offer phases and only safe traceback
file/function/line metadata, never exception contents, source lines or locals.
On a subsequent failed acceptance with proven zero residue/health, the wrapper
keeps one authenticated window for local repair and prompts R to retry or Q to
close safely. It archives preceding sanitized reports before the next attempt.
Unproven cleanup is never retried automatically. Credential URLs are cleared
when the operator window finishes, not persisted for later sessions.

## Native Acceptance Closure

Manuel completed the repaired operator batch from source `87844d1` and supplied
the all-PASS final line. The actual sanitized files were independently inspected:
environment `native-staging`, status/cleanup PASS, 142 checks, 65 audit events
observed before cleanup, every postflight table count zero. Every recorded
browser/API/local/compile/pip/JS/diff/latency exit code is zero. Services stayed
active and PostgreSQL listener/SHOW stayed loopback/localhost-only. The script
returned to PowerShell after its own tunnel cleanup; no more manual access is
needed for this closure.

Only the shared browser harness changed between the failed and passing native
attempts; no application authorization/workflow change was used to make the
gate pass. This supports the timing diagnosis while preserving the limitation
that the first attempt's exact assertion stack was not captured.

The tested UI/runtime ran locally through HTTPS and the SSH tunnel against real
VPS Staging PostgreSQL. Password/MFA/session/domain persistence were genuine.
This does NOT prove Linux wheel installation, systemd startup, public app DNS,
Nginx/TLS/cookie path, SMTP, productive backups or a hosted Portal service.
Those are separate readiness/rehearsal gates, not missing native UI checks.
Real zoom was measured; keyboard/focus/dialog reflow and Reduced Motion were
also exercised. No screenreader-device audit is claimed.

Evidence stays ignored under `release-artifacts/cal1-native-ui-20261022/`.
Only file-level hashes and outcomes are retained here, not fixture identifiers,
credentials, tokens, MFA values or raw audit rows. Prior failed sanitized reports
remain in the runner's attempt archive.

| File | SHA-256 |
| --- | --- |
| result.json | BBAAE75D69210DB9F8D088992761A06E86CB233E97EB8976206E975B4E39139A |
| batch-summary.json | 0A8CF408C7A7EA9FC4EE4019B5A61D6588B4E0E17E9CBB868180D74B4327D909 |
| postflight.json | A7502F7BFE5FBD91747A3BF44C3894577DA96EC3B5BDCD4F6B22DA797B540BF1 |
| service-preflight.json | 5A7852CA0578228BF7E8F98E68F474AFA1B15EED594F3943688CB45808AE0545 |
| service-postflight.json | 5A7852CA0578228BF7E8F98E68F474AFA1B15EED594F3943688CB45808AE0545 |
| native-actual-200-percent.png | A4654AF80BC4B78ED5C4E41F1B42AD6567547601E8B978424AB7BEA7C9F9BA98 |

## Browser And Security Matrix

The [26-point local checklist](calendar-cal1-browser-acceptance-checklist-2026-09-18.md)
and September history remain dated evidence, not a native VPS pass. The current
142-check PostgreSQL matrix was actually completed locally and against VPS Staging:

| Group | Local PostgreSQL browser | Native VPS |
| --- | --- | --- |
| Coach-only and Reviewer-only password, enrollment, MFA, resume | PASS | PASS |
| Admin, Internal and Company Contact admission boundaries | PASS | PASS |
| Draft edit, submit, permitted withdrawal and double-click | PASS | PASS |
| Published/changes-requested new revision, preserved published revision | PASS | PASS |
| Reviewer publication/change request and required comment | PASS | PASS |
| Coach without offers, loading/empty/generic error | PASS | PASS |
| Stale ETag, no automatic retry, explicit server-state recovery | PASS | PASS |
| 390 px text fit, keyboard, visible focus, Escape, Reduced Motion | PASS | PASS |
| Actual 200% browser zoom plus dialog/actions reflow | PASS | PASS |
| Foreign Coach read/edit/submit/withdraw and unknown-ID equivalence | PASS | PASS |
| Forged ownership/filter, Reviewer foreign mutations, role revocation | PASS | PASS |
| Invalid/expired/replayed MFA, single-use recovery, no session before MFA | PASS | PASS |
| Session expiry, CSRF rotation, stale-CSRF logout, actual revocation | PASS | PASS |
| Origin/CSRF, unknown fields, 32 KiB limit, stored text not executable | PASS | PASS |
| Published-only public DTO, exact allowlist, NULL real-profile paths | PASS | PASS |
| Actual audit schema, every Calendar mutation action, no payload columns | PASS | PASS |
| Exact-ID cleanup and independent 20-table zero-residue check | PASS locally | PASS |

Additional mixed/disabled/roleless and factor-transition cases are in permanent
local regression, not claimed as extra manually performed native browser cases.
No High/Critical implementation finding remains in this bounded review. This
does not supersede the separate inherited website toolchain advisory backlog.

## SSH And One Operator Window

The existing ED25519 key already authenticated two independent BatchMode SSH
connections, the second without connection sharing. No private key was read,
no new key was necessary, and authorized_keys/sshd/sudo were not changed.
Windows ssh-agent is stopped/disabled; there is no reason to alter it for this
working setup. Password recovery configuration was left untouched, not newly
tested by entering a password. SSH prompts needed for this batch: zero.

Read-only VPS preflight: dp-chatbot, nginx, fail2ban and postgresql all active;
5432 listens only on 127.0.0.1. This is health evidence, not DB/UI acceptance.

Historical operator entry, successfully completed. **No action currently required.**
For a future separately authorized recheck only, one PowerShell window:

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp'
.\scripts\run-native-cal1-staging-batch.ps1
```

Enter the two existing database-role passwords only at the hidden local prompts
for competence_hub_app and competence_hub_migrator. Never send them in chat.
The script opens its own key-authenticated loopback tunnel and leaves any
pre-existing tunnel alone. Keep the window open until all checks finish.

The prepared batch runs service/network preflight, strict DB/role/URL/schema
and empty-data checks, six exact synthetic identities, real browser/MFA matrix,
17 API tests, exact-ID cleanup, independent SQL counts/owners/migrations,
service/network postflight and complete local regression. Runtime is local
over the tunnel; there is no native service installation or backend deployment.
Only process environment contains credential URLs, cleared in `finally`.

Expected final line:

```text
NATIVE_UI=PASS API=PASS CLEANUP=PASS ZERO_RESIDUE=PASS SERVICES=PASS POSTGRES_LOCALHOST=PASS
```

The script closes only its own tunnel after proven cleanup/health. On unproven
cleanup it retains that tunnel for investigation and must not mark acceptance
complete. No service restart. Evidence stays in ignored
`release-artifacts/cal1-native-ui-20261022/`; the UUID manifest contains no
passwords or MFA secrets. Both the failed attempt and successful retry were
fully cleaned; the complete repaired native result is verified above.

## Batch Close-Out: 35 Requested Items

| # | Item | Current outcome |
| --- | --- | --- |
| 1 | Topic Hub | Implemented, public Preview PASS |
| 2 | Progressive disclosure | One initial core, then categories, then relevant topics |
| 3 | Satellites | Three categories; All computed, many-to-many preserved |
| 4 | Motion | Gentle pulse; touch/keyboard semantics and Reduced Motion PASS |
| 5 | Mindforge clearance | Preview-only geometry correction, five widths PASS |
| 6 | Contact clearance | Preview-only CTA separation PASS |
| 7 | Preview live | Source 1cc481de9210, Actions 39774218286, public checks PASS |
| 8 | Production unchanged | Full 52-file build manifest byte-identical; no IONOS writes |
| 9 | SSH key | Existing key, two independent connections PASS |
| 10 | ssh-agent | Disabled; unchanged, not needed for this working key |
| 11 | Manual passwords | Zero SSH; two existing DB-role passwords once in one batch |
| 12 | Security rules changed | No host, SSH, sudo or password-policy changes |
| 13 | Password recovery | Configuration untouched; no new password-login proof claimed |
| 14 | Access contract | Local PASS, no migration |
| 15 | Coach login/MFA | Real local PostgreSQL and VPS PASS |
| 16 | Reviewer login/MFA | Real local PostgreSQL and VPS PASS |
| 17 | Session resume | Exact live roles PASS locally and on VPS |
| 18 | Native Staging acceptance | Repaired retry PASS 142/142; actual files independently inspected |
| 19 | Coach flow | Local PostgreSQL and VPS PASS |
| 20 | Reviewer flow | Local PostgreSQL and VPS PASS |
| 21 | Admin flow | All workflow/revision projections PASS locally and on VPS |
| 22 | RBAC/IDOR | Local PostgreSQL, permanent regression and VPS PASS |
| 23 | Stale ETag | Conflict/recovery/no silent retry PASS locally and on VPS |
| 24 | Public projection | Exact DTO, no private mapping, published only PASS locally and on VPS |
| 25 | Accessibility | Browser keyboard/focus/390/zoom/motion PASS natively; no assistive-device audit claimed |
| 26 | Synthetic cleanup | Both local rehearsals and both VPS attempts fully cleaned |
| 27 | SQL zero residue | All 20 tables zero locally and in independent VPS postflight |
| 28 | Services | VPS preflight and first-attempt postflight four active |
| 29 | PG localhost | VPS listener and DB SHOW/postflight PASS |
| 30 | Additional backend slice | Sanitized DB-error logging hardening plus [CAL-1 readiness package](../operations/cal1-production-readiness-2026-10-22.md); no deployment |
| 31 | Deliberately not begun | Production, real accounts/mappings, SMTP, tracking, CAL-2/FIN-01 implementation |
| 32 | Commits | Preview 1cc481de9210; access 40a7574; public QA 3218750; native harness b5c65c7; context d064b1a; repair 87844d1; closure/readiness docs separate |
| 33 | Push | All listed commits pushed to main; Pages remains source 1cc481de9210; no auto production deployment |
| 34 | Remaining local changes | Closure slice changes only owned docs; unfamiliar .vscode and September weekly file remain untouched; generated evidence ignored; Git status owns live commit state |
| 35 | Exact next gate | Resolve non-secret operating inputs for one controlled Linux/proxy rehearsal; separate execution approval, no productive activation |

## Recommended Next Block

Native acceptance is closed. The follow-on readiness package is documentation,
not productive activation. Recommended next block: complete its non-secret
runtime/operations input matrix, so one scoped Linux/proxy rehearsal can be
approved and executed without repeated operator windows. See the package for
inputs, deliverables and Definition of Done. Do not rerun the closed UI gate
merely because another day starts.
