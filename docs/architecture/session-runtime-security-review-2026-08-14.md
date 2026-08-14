# Session And Runtime Security Review

Date: 2026-08-14

Status: SB-04 completed locally. No open high or critical finding in the
reviewed session/runtime slice. This is not a production authorization.

## Scope

- opaque session and CSRF token handling
- secure cookie attributes and logout verification
- PostgreSQL session queries, role filtering and audit write
- runtime configuration and database engine lifecycle
- readiness behavior and database error exposure
- synthetic Staging integration harness and cleanup
- current API contract and authentication requirements

Not in scope because it is not implemented yet: password login endpoint, rate
limiting behavior, TOTP processing, recovery, invitations, reset, real accounts,
mail delivery, reverse-proxy configuration and backend deployment.

## Evidence

- 61 local tests pass; seven opt-in Staging tests are skipped without explicit
  process configuration.
- Earlier SB-03 execution: 7/7 tests passed against isolated PostgreSQL Staging.
- Staging cleanup verification: zero portal users, sessions and audit events.
- Database state remained at migrations `0001` and `0002`.
- Chatbot, Nginx, Fail2ban and PostgreSQL remained active.
- Compileall, dependency check, PowerShell syntax and diff check passed.

## Findings And Fixes

### SR-001 - Runtime settings could bypass validation through direct construction

- Severity before fix: medium defense-in-depth risk; no deployed exposure.
- Risk: code could construct `RuntimeSettings` directly with a remote database,
  unsafe origin, excessive timeout or privileged database role even though the
  environment factory rejected those values.
- Fix: frozen settings now validate in `__post_init__` on every construction
  path. Database access is restricted to loopback PostgreSQL/asyncpg and the
  dedicated `competence_hub_app` role; origin and timeout bounds remain strict.
- Evidence: direct-construction and privileged-role regression tests.
- Status: resolved.

### SR-002 - Token-bearing dataclass representations

- Severity before fix: medium logging/debug exposure risk; no real tokens used.
- Risk: default dataclass `repr()` included newly issued plaintext tokens or a
  session CSRF digest if an object reached a log, debugger or failure message.
- Fix: token plaintext, token digest and session CSRF digest are excluded from
  representations. Synthetic Staging fixture tokens are hidden as well.
- Evidence: representation regression tests.
- Status: resolved.

### SR-003 - SQL parameters visible in database exception details

- Severity before fix: low-to-medium logging exposure risk; observed only with
  synthetic fixture parameters.
- Fix: runtime and Staging engines use SQLAlchemy `hide_parameters=True`.
- Evidence: engine-configuration test and reduced subsequent error exposure.
- Status: resolved.

### SR-004 - Fixed readiness timeout unsuitable for tunneled diagnostics

- Severity before fix: low availability/diagnostic risk.
- Fix: bounded runtime setting, default 5 seconds and accepted range 1-30;
  controlled SSH-tunneled Staging uses 15 seconds.
- Evidence: config boundary tests and successful Staging readiness test.
- Status: resolved.

## Confirmed Controls

- Session tokens have at least 256 bits of entropy and only SHA-256 digests
  reach persistence.
- Cookie names use the `__Host-` prefix with `Secure`, `HttpOnly`,
  `SameSite=Lax`, `Path=/` and no Domain attribute.
- Logout requires exact configured Origin plus a session-bound CSRF token and
  compares digests with `hmac.compare_digest`.
- Session lookup accepts only active users, active `admin` or `internal` roles,
  MFA-level sessions and valid idle/absolute expiry.
- Logout revocation and a minimal audit event commit in one transaction.
- Auth responses are `no-store`; API documentation endpoints are disabled.
- Default app wiring remains not ready and has no repository or browser origin.
- Runtime startup rejects missing or unsafe configuration without echoing the
  database URL.

## Residual Gates Before Login Or Deployment

- Implement account- and IP-based rate limits with generic responses before a
  login endpoint can be considered complete.
- Add the contractually required request-size and unknown-field rejection with
  login request schemas.
- Decide and test the approved offline compromised-password source before any
  password creation/reset workflow.
- Select maintained TOTP and authenticated-encryption handling before MFA.
- Keep the approved same-origin model; any later cross-origin architecture
  requires a separate CORS and cookie review.
- Define dedicated system user, protected service configuration, reverse-proxy
  trust/host handling, HTTPS/HSTS ownership, sanitized logging, monitoring and
  rollback before deployment.
- No real data before the encrypted off-server backup/restore gate.

## Review Conclusion

The current session/runtime slice is suitable to become the foundation for the
next synthetic first-factor login slice. It is not deployable and does not
authorize real accounts or data. No high or critical finding remains in scope.
