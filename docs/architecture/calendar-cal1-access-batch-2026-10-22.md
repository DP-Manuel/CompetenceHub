# CAL-1 Access And Batched Acceptance

Date: 2026-10-22. Local gate **PASS**. Native VPS gate **NOT ACCEPTED**:
first attempt stopped after six checks; cleanup/SQL/health PASS, repaired retry ready.
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

## Browser And Security Matrix

The [26-point local checklist](calendar-cal1-browser-acceptance-checklist-2026-09-18.md)
and September history remain dated evidence, not a native VPS pass. The current
142-check PostgreSQL rehearsal actually covers:

| Group | Local PostgreSQL browser | Native VPS |
| --- | --- | --- |
| Coach-only and Reviewer-only password, enrollment, MFA, resume | PASS | PENDING |
| Admin, Internal and Company Contact admission boundaries | PASS | PENDING |
| Draft edit, submit, permitted withdrawal and double-click | PASS | PENDING |
| Published/changes-requested new revision, preserved published revision | PASS | PENDING |
| Reviewer publication/change request and required comment | PASS | PENDING |
| Coach without offers, loading/empty/generic error | PASS | PENDING |
| Stale ETag, no automatic retry, explicit server-state recovery | PASS | PENDING |
| 390 px text fit, keyboard, visible focus, Escape, Reduced Motion | PASS | PENDING |
| Actual 200% browser zoom plus dialog/actions reflow | PASS | PENDING |
| Foreign Coach read/edit/submit/withdraw and unknown-ID equivalence | PASS | PENDING |
| Forged ownership/filter, Reviewer foreign mutations, role revocation | PASS | PENDING |
| Invalid/expired/replayed MFA, single-use recovery, no session before MFA | PASS | PENDING |
| Session expiry, CSRF rotation, stale-CSRF logout, actual revocation | PASS | PENDING |
| Origin/CSRF, unknown fields, 32 KiB limit, stored text not executable | PASS | PENDING |
| Published-only public DTO, exact allowlist, NULL real-profile paths | PASS | PENDING |
| Actual audit schema, every Calendar mutation action, no payload columns | PASS | PENDING |
| Exact-ID cleanup and independent 20-table zero-residue check | PASS locally | PENDING |

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

**MANUEL ACTION REQUIRED**, one PowerShell window, no second terminal:

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
passwords or MFA secrets. The first failed run's cleanup is proven; the complete
native matrix requires the repaired run and inspection of its sanitized result.

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
| 15 | Coach login/MFA | Real local PostgreSQL PASS; VPS PENDING |
| 16 | Reviewer login/MFA | Real local PostgreSQL PASS; VPS PENDING |
| 17 | Session resume | Exact live roles PASS locally; VPS PENDING |
| 18 | Native Staging acceptance | First attempt FAIL after six checks; repaired retry ready, never substituted by Docker |
| 19 | Coach flow | Local PostgreSQL PASS; VPS PENDING |
| 20 | Reviewer flow | Local PostgreSQL PASS; VPS PENDING |
| 21 | Admin flow | All workflow/revision projections PASS locally; VPS PENDING |
| 22 | RBAC/IDOR | Local PostgreSQL and permanent regression PASS; VPS PENDING |
| 23 | Stale ETag | Conflict/recovery/no silent retry PASS locally; VPS PENDING |
| 24 | Public projection | Exact DTO, no private mapping, published only PASS locally |
| 25 | Accessibility | Browser keyboard/focus/390/zoom/motion PASS; no assistive-device audit claimed |
| 26 | Synthetic cleanup | Both local rehearsals and first failed VPS attempt fully cleaned |
| 27 | SQL zero residue | All 20 tables zero locally and in independent VPS postflight |
| 28 | Services | VPS preflight and first-attempt postflight four active |
| 29 | PG localhost | VPS listener and DB SHOW/postflight PASS |
| 30 | Additional backend slice | Sanitized DB-error logging hardening implemented/tested; readiness package gated on native PASS |
| 31 | Deliberately not begun | Production, real accounts/mappings, SMTP, tracking, CAL-2/FIN-01 implementation |
| 32 | Commits | Preview 1cc481de9210; access 40a7574; public QA 3218750; native harness b5c65c7; context d064b1a; retry repair separately |
| 33 | Push | All listed commits pushed to main; Pages remains source 1cc481de9210; no auto production deployment |
| 34 | Remaining local changes | Bounded retry repair/status until its commit; unfamiliar .vscode and September weekly file preserved |
| 35 | Exact next gate | One secure operator batch above; no new content decision needed |

## Recommended Next Block

Run and inspect the single authorized native Staging batch. Inputs: prepared
runner and two existing role passwords entered only by Manuel. Deliverables:
native browser/API result, exact-ID cleanup, independent SQL/health evidence.
Done means every expected final PASS is proven, not just the browser exit code.
Only then advance the active horizon to CAL-1 production-readiness preparation;
this is planning/hardening, not productive activation.
