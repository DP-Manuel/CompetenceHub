# CAL-1 Native Staging UI Acceptance

Date: 2026-10-21. Result: **NOT ACCEPTED - preflight prerequisite missing**.
Historical finding. The separately authorized 22.10 implementation and completed
native runtime/UI PASS are in the [access/batch report](calendar-cal1-access-batch-2026-10-22.md).
Synthetic Staging execution was explicitly authorized on this date. It was not
executed: the inspected native authentication path cannot admit Calendar-only
identities while preserving the existing internal login contract.

## Scope And Preflight

- Branch `main`, HEAD `b02ded1ad13759f2effcfe2eea05e32084250edb` matched `origin/main`.
- Known Context V2/Analytics documentation, `.vscode/` and the September weekly
  update were present before this block. No unexpected application changes.
- Those works were not reset, stashed or staged. Only the current checkpoint,
  active horizon and milestone log receive scoped steering updates.
- No listener on local Staging tunnel port `55432` was present at preflight.
  No secret files, passwords, private keys or unapproved sources were read.
- No SSH connection, Staging SQL, native server, account provisioning or remote
  mutation was performed. The earlier tunnel request is deferred until the
  authentication prerequisite is resolved; no operator command is needed now.

## Finding CAL1-NATIVE-AUTH-01

Classification: acceptance-blocking authentication integration gap, not evidence
of a privilege-escalation vulnerability. The existing boundary fails closed.

1. `auth/login_service.py` admits only active accounts with `admin` or `internal`.
   Correct credentials and enrolled MFA do not admit a pure `coach`,
   `calendar_reviewer`, `company_contact` or Coach/Reviewer combination.
2. `auth/postgres_mfa_repository.py` independently requires `admin`/`internal`
   when finding a challenge, saving enrollment and consuming a challenge.
3. `portal_ui/app.js` restores the session after MFA and on refresh through
   `/api/v1/auth/session`; its CSRF refresh also uses the internal Auth router.
   `web/auth.py` uses the internal session repository for these operations.
4. `runtime.py` correctly keeps that repository separate from the broader
   `calendar_session_repository`. Calendar endpoint permissions alone therefore
   do not provide a usable login/bootstrap path for pure Calendar roles.
5. The old local browser fixture replaces Login, MFA and Session with synthetic
   implementations accepting these identities. Native Calendar API tests insert
   completed sessions directly. Neither proves native Coach login/MFA/bootstrap.

Granting `internal` to Coach/Reviewer test accounts would broaden their scope and
invalidate the required negative tests. Injecting sessions, faking MFA or replacing
the internal resolver would hide the integration gap. None was done. No runtime,
role binding, API or authentication contract was changed.

## Actual Verification

All commands below ran in `apps/webapp`, except the Node syntax check from the
repository root. These are **local results**, not fresh native Staging evidence.

| Check | Result |
| --- | --- |
| Auth/Runtime/Session/MFA plus fixture/UI focus | 59 passed |
| CAL-1 domain/API/repository/projection/migration/UI focus | 62 passed |
| Complete Python suite, final run | 399 passed, 17 opt-in Staging skips, 7.74 s |
| Existing local browser runner | 57/57, Microsoft Edge 155.0.4283.62 |
| `python -m compileall -q src tests scripts` | PASS |
| `python -m pip check` | PASS, no broken requirements |
| Portable Node `--check .../portal_ui/app.js` | PASS |

`tests/test_login_service.py` now characterizes pure Calendar/reviewer/contact
and roleless denial, successful existing internal/admin combinations, and the
actual HTTP Auth router plus real LoginService returning generic `401` without
a challenge/cookie and with `no-store`. Account lookup and password verification
remain test doubles in these local tests; this is not a PostgreSQL/browser proof.

The local browser runner covers the Admin revision actions, Coach/reviewer flow,
stale-edit, keyboard/focus, 390 px and Reduced Motion. Its historical "200 percent
zoom" check is a 640-CSS-pixel viewport with device scale factor 2, **not actual
browser zoom**. Native acceptance still requires an explicit real-zoom check.
Its server, browser and temporary certificate context exited normally.

## Native Acceptance Matrix

`NOT RUN` means no native PASS/FAIL was obtained. Historical September results
remain dated evidence; the local 26-point checklist is not relabeled as native.

| Requested area | Native status / evidence |
| --- | --- |
| Preflight / working tree | PASS locally; native connection not established |
| Synthetic identities | NONE created; planned Coach A/B, Reviewer, Admin, Internal, contact only |
| Login/MFA/session/logout/CSRF rotation/expiry | BLOCKED by CAL1-NATIVE-AUTH-01; no native account tested |
| Coach empty/create/edit/validation/submit/withdraw/revision | NOT RUN |
| Two-tab stale ETag / safe recovery | NOT RUN |
| Reviewer queue / decisions / least privilege | NOT RUN |
| Admin Draft/Published/Changes Requested/In Review | NOT RUN; existing local runtime actions passed |
| Internal negative Calendar access | NOT RUN |
| Company-contact negative access | NOT RUN |
| IDOR / foreign revision / manipulated requests / role removal | NOT RUN |
| CSRF/Origin/XSS/errors/enumeration/token/private-field security | NOT RUN natively; no comprehensive security sign-off |
| Public published projection / unpublished revision exclusion | NOT RUN |
| Synthetic profile paths NULL / no fallback | No synthetic Coach created; native projection not checked |
| Desktop / 390 px / real 200% browser zoom | NOT RUN natively |
| Keyboard/focus/dialogs/Reduced Motion/busy/double-submit/FormData | NOT RUN natively |
| Mutation audit / no payload or token leakage | NOT RUN |
| Staging cleanup | NOT APPLICABLE: no native fixture/data created |
| SQL zero residue (users/sessions/roles/coaches/offers/revisions/decisions) | NOT RUN; do not claim database counts |
| PostgreSQL/Nginx/Fail2ban/dp-chatbot health | NOT RUN; no service accessed, changed or restarted |
| PostgreSQL localhost-only | NOT RUN; previous proof is historical, not current |
| Local regression | PASS as above; final diff/context checks below |
| IONOS production / GitHub Pages preview | No modifications, publication or deployment |
| Commit / push / real-data use | NONE |

## Files And Next Gate

Changes owned by this block: `apps/webapp/tests/test_login_service.py`, this
evidence file, and scoped steering amendments to `PROJECT_CONTEXT.md`,
`PROJECT_LOG.md` and the active backend horizon. Existing application/runtime,
website and deployment files are unchanged.

Exactly one recommended next backend slice: **CAL-1 native Calendar access**.
Purpose: provide a real least-privilege Coach/Reviewer authentication path without
changing the internal Auth contract. Inputs: this finding, accepted Auth/CAL-1
contracts and a separately approved additive authentication/session design.
Deliverables: bounded login/MFA/recovery/session/CSRF/logout design and, after its
approval, implementation and native synthetic harness. DoD: pure Coach/Reviewer
can authenticate and restore a session, do not gain company/admin rights, internal
Auth remains unchanged and negative/session regressions pass. Then resume this
same native acceptance matrix; it is not waived or replaced by local tests.

Reusable learning candidate: before promoting an in-memory browser fixture to
native acceptance, trace the complete login -> MFA -> session restore -> CSRF ->
domain authorization path for every pure role. Mocked sign-in and injected
sessions can conceal missing access integration. Recorded here; existing skill
feedback/context-migration work and global skills were not modified.

Final repository checks: `git diff --check` PASS (only existing CRLF conversion
warnings); context validator PASS with 7 archive hashes, 21 router files and
116 local links verified. Final status adds only the owned test/evidence to
the known baseline; existing checkpoint/horizon/log amendments are scoped above.
