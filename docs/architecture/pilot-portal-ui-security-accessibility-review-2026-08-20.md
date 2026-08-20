# Pilot Portal UI Security And Accessibility Review

Date: 2026-08-20

Status: local synthetic review and isolated PostgreSQL Staging proof completed.
No open high or critical finding in the reviewed UI slice. Real-browser
acceptance remains open. This is not a deployment, account or real-data
approval.

## Scope

- packaged same-origin portal shell and route ownership
- login, MFA enrollment/verification/recovery and session restoration client
- company/contact list, detail, create and bounded correction client
- CSRF page-memory recovery after reload
- browser storage, DOM rendering, CSP and cache behavior
- keyboard/focus semantics, labels, live regions, contrast and responsive CSS
- duplicate-submit and network/error handling

## Confirmed Controls

- All API requests are relative same-origin requests with credentialed cookies;
  no CORS, CDN, analytics, external font or third-party runtime is introduced.
- Session and challenge cookies remain `HttpOnly`; JavaScript receives only the
  contracted CSRF values and keeps them in page memory.
- No `localStorage`, `sessionStorage`, inline script/style or `innerHTML` use is
  present. Dynamic API values are rendered with `textContent` and DOM methods.
- A restrictive CSP, `Cache-Control: no-store`, clickjacking protection,
  no-referrer and `nosniff` apply to portal assets and API responses.
- Page reload obtains a new session-bound CSRF token only after exact-Origin
  validation and an active MFA session. Persistence receives only its digest.
- Forms reject duplicate submits in the active page, disable controls while
  pending and expose `aria-busy`; server authorization remains authoritative.
- Static and dynamic fields have programmatic labels. IDs and `aria-labelledby`
  references have an automated uniqueness/existence regression test.
- Skip link, semantic headings, dialogs, visible focus, status/error regions,
  responsive constraints and reduced-motion handling are present.
- The default app remains fail-closed without configured repositories and
  allowed origin. The login shell contains no protected business data.

## Evidence

- 241 local tests passed; 14 opt-in PostgreSQL Staging tests skipped without an
  explicit tunnel.
- Focused portal/Auth/repository suite passed 24 tests.
- Python compileall, JavaScript syntax and dependency checks passed.
- All 14 opt-in paths passed against isolated PostgreSQL Staging in 171.95
  seconds, including rotated CSRF digest persistence.
- Post-run verification found zero users, sessions, companies, contacts and
  audit events; Chatbot, Nginx, Fail2ban and PostgreSQL remained active.

## Residual Gates

1. Exercise login, MFA, reload, logout and company/contact workflows in a real
   browser at desktop and 390-pixel width using synthetic data only.
2. Verify keyboard-only dialogs, focus return, long German labels, zoom and
   reduced motion with captured acceptance evidence.
3. Persistent company-create idempotency is not implemented; the page-level
   submit guard satisfies only the bounded pilot criterion and needs E2E proof.
4. Review packaged install, dedicated systemd/Nginx identity, TLS headers,
   monitoring, backup and rollback before any server change.
5. Personal account identities, invitation handoff, stakeholder acceptance and
   all real-data gates remain open.

## Conclusion

The local portal is suitable for isolated Staging and browser verification.
It is not yet suitable for DNS activation, real accounts, real company data or
production deployment.
