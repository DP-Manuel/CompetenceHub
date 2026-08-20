# ADR 0006: Same-Origin Pilot Portal UI

Status: Accepted

Date: 2026-08-20

Accepted by Manuel on 2026-08-20 for the local synthetic pilot slice. This
does not authorize DNS, server installation, accounts, real data or deployment.

## Context

The public Astro website and the protected FastAPI/PostgreSQL application have
deliberately separate ownership and deployment paths. The 2026-08-28 pilot now
needs a small browser UI for personal login, MFA and Frau Janay Rappelt's
company/contact workflow. The repository has no existing webapp frontend stack.

Adding a second SPA framework, a separate API origin or a new Node production
runtime during the remaining pilot window would add package, CORS, cookie,
CSRF, TLS, deployment and rollback work without improving the first workflow.
The VPS already supports FastAPI behind Nginx, while the IONOS webspace remains
the destination for the independent public Astro website.

## Decision

For the narrow pilot:

1. Portal UI and `/api/v1/...` are delivered from one HTTPS origin, proposed as
   `competencehub-app.donner-partner.de`.
2. The UI is a build-free, modular HTML/CSS/JavaScript client owned by
   `apps/webapp` and packaged with the FastAPI application. No new frontend
   framework or production Node process is introduced.
3. FastAPI serves the packaged portal shell and same-origin static assets after
   all API and health routes are registered. Nginx terminates TLS and proxies
   the dedicated Competence-Hub service; it does not mix files, configuration,
   users or logs with the Chatbot.
4. Authentication continues to use Secure, HttpOnly session/challenge cookies.
   Raw tokens are never stored in `localStorage`, `sessionStorage`, HTML or
   normal logs. CSRF material returned by the contracted Auth flow exists only
   in the active page's memory.
5. The first UI contains only login/MFA, current-session/logout and the
   protected company/contact list, create, detail and bounded correction flow.
6. The client prevents duplicate submits, renders explicit loading/error/empty/
   expired-session states and remains keyboard-, focus-, contrast- and
   reduced-motion-aware. API authorization remains the security boundary.
7. No offline cache, PWA, analytics, external fonts, CDN scripts or third-party
   provider is added to the authenticated surface.

The stable API contract remains replaceable-client architecture. A later
frontend framework or separate API origin may supersede only the presentation
and deployment decision; it must not require direct database access or weaken
server-side authorization.

## Consequences

Positive:

- one origin avoids pilot CORS and cross-site cookie complexity;
- no additional framework, package supply chain or Node service is required;
- public website and protected application remain separately deployable;
- the UI can be shipped and rolled back with the exact backend release;
- a future client can reuse the existing versioned API.

Negative:

- vanilla modules require discipline as UI scope grows;
- server releases also carry portal asset changes;
- advanced component tooling, type checking and browser-test infrastructure are
  deferred;
- a later migration is likely before broad Coach/company/PWA functionality.

These downsides are accepted only for the narrow two-user pilot. New workflows
beyond company/contact CRUD trigger a frontend-stack review.

## Alternatives Considered

### Extend the public Astro website with authenticated pages

Rejected for the pilot because it couples the IONOS public deployment to the
VPS application, while cross-origin cookies and API calls require additional
security and release work.

### Create a second Astro application now

Plausible after the pilot and reuses an existing project technology, but it
still introduces a second package/build/deployment pipeline during the critical
window. Re-evaluate when the protected UI grows beyond the bounded workflow.

### Introduce React, Vue or another SPA framework

Rejected because no such framework exists in the repository and the current
workflow does not justify the dependency and operational expansion.

### Separate portal and API origins immediately

Rejected for the pilot because it adds CORS, credentialed-fetch, cookie-domain,
preflight, CSP/connect-src and certificate/DNS failure modes. The reserved
future API hostname does not need to be activated now.

## Validation

- API and health routes remain reachable before the static fallback.
- Unauthenticated portal access returns only the login shell and no protected
  data.
- Login, enrollment, MFA verification, session expiry and logout work without
  exposing raw session/challenge tokens to JavaScript.
- Company/contact happy paths and wrong-role/Origin/CSRF paths pass in browser
  tests with synthetic data.
- Double-click/slow-network tests create only one visible operation attempt.
- Keyboard, visible focus, contrast, 390-pixel viewport, reduced motion and
  long German labels are verified.
- Security headers, `Cache-Control: no-store`, CSP and no-secret-log checks pass.
- Package/install/restart and rollback tests prove that Chatbot services are
  unchanged.

Local implementation evidence on 2026-08-20:

- FastAPI packages and serves the portal shell and local assets after API and
  health routes; route-priority regression tests pass.
- CSP, `no-store`, no-indexing, local-only assets and absence of browser token
  storage are covered by automated tests.
- Session restore rotates page-memory CSRF through an exact-Origin endpoint;
  unit/repository tests and the PostgreSQL Staging path pass.
- Semantic ID references, labels, responsive styles, focus visibility,
  reduced-motion behavior and duplicate-submit guards were reviewed locally.
- The complete local Webapp suite passes 241 tests with 14 opt-in Staging tests
  skipped while no tunnel is present; Python, JavaScript and dependency checks
  pass.
- The expanded isolated PostgreSQL harness passed 14/14 in 171.95 seconds,
  left no synthetic business/Auth/audit residue and all four VPS services
  active.
- Real browser E2E, 390-pixel visual evidence, packaged service/restart/rollback
  and stakeholder acceptance remain open gates.

## Follow-Ups

1. Confirm the single app hostname, DNS owner and Nginx/TLS path with Thomas
   Ross.
2. Define the exact authenticated CSP and static-asset cache policy.
3. Verify the implemented portal shell as one vertical login-to-company slice
   against isolated PostgreSQL Staging and in a real browser.
4. Review the frontend stack again before Coach, company-contact, feedback,
   statistics, offline or PWA scope is admitted.
