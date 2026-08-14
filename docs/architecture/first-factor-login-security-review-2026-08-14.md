# First-Factor Login Security Review

Date: 2026-08-14

Status: SB-05 completed. No open high or critical finding in the reviewed
first-factor slice. This is not a production authorization.

## Scope

- `POST /api/v1/auth/login` request and response boundary
- account eligibility and account-enumeration resistance
- Argon2id verification and dummy-hash behavior
- account and network-peer rate limiting
- HMAC pseudonymization and runtime key configuration
- pre-auth challenge, CSRF token and secure login cookie
- PostgreSQL transactions, audit semantics and cleanup
- local and isolated Staging evidence

Not in scope because it is not implemented: TOTP enrollment/verification,
recovery codes, full-session creation after MFA, invitations, password reset,
real accounts, reverse-proxy configuration and backend deployment.

## Evidence

- 86 local tests pass; 11 opt-in Staging tests skip without explicit database
  configuration.
- 11/11 Auth Staging paths pass against PostgreSQL 16 in 103.75 seconds.
- Staging verifies active/inactive/external-role handling, challenge and CSRF
  hashes, five-minute expiry, audit, the fifth-failure boundary, progressive
  blocking, session behavior and database readiness.
- Cleanup leaves zero portal users, password credentials, login challenges,
  sessions, rate-limit buckets and audit events.
- Chatbot, Nginx, Fail2ban and PostgreSQL remain active after the run.
- Compileall, dependency check, PowerShell syntax and diff check pass.

## Findings And Fixes

### FL-001 - Failed login audit implied an authenticated actor

- Severity before fix: low audit-integrity risk.
- Risk: using the target user as `actor_user_id` on a failed password attempt
  could incorrectly imply that the requester was authenticated.
- Fix: failed attempts use no authenticated actor and identify only the optional
  target entity. Successful first-factor events identify the verified account.
- Evidence: repository tests and Staging audit checks.
- Status: resolved.

### FL-002 - Successful login response emitted a redundant delete cookie

- Severity before fix: low interoperability and test-clarity risk.
- Risk: a successful response first cleared and then set the same pre-auth
  cookie, producing two competing `Set-Cookie` headers.
- Fix: success now emits only the new secure pre-auth cookie.
- Evidence: API cookie regression test.
- Status: resolved.

### FL-003 - Oversized stream chunk was appended before rejection

- Severity before fix: low request-memory hardening risk.
- Risk: an oversized incoming chunk could be retained before the 32 KiB limit
  was detected.
- Fix: projected size is checked before extending the request buffer.
- Evidence: oversized-body API test.
- Status: resolved.

## Confirmed Controls

- Unknown accounts use a runtime-generated Argon2id dummy hash. Unknown,
  inactive and external-role accounts receive the same generic response and
  perform one password verification.
- Login accepts only JSON up to 32 KiB and rejects unknown fields, malformed
  email input and passwords longer than 128 characters without echoing input.
- Account and network-peer bucket identifiers use separate value prefixes and
  an external HMAC key of at least 256 bits; raw email and peer IP are not stored
  in rate-limit rows.
- Existing blocks are checked before Argon2id work. The fifth failure within 15
  minutes starts a 30-second block; later verified failures progressively
  increase the delay up to 15 minutes.
- A correct password creates only a five-minute pre-auth challenge. Token and
  CSRF plaintext values are returned only to the browser and excluded from
  object representations; PostgreSQL stores SHA-256 digests.
- The cookie is `__Host-` prefixed, `Secure`, `HttpOnly`, `SameSite=Lax`,
  `Path=/` and has no Domain attribute. No full session exists before MFA.
- Challenge replacement, success audit and account-bucket reset are atomic.
  Failure bucket updates and failure audit are atomic.
- The runtime rejects missing/short/non-base64 HMAC key configuration and keeps
  the decoded key out of representations.
- `X-Forwarded-For` is deliberately ignored. The direct network peer is used
  until an explicit trusted-proxy design is approved.

## Residual Gates Before Deployment

- Configure and test trusted reverse-proxy peer handling before deployment;
  otherwise every request proxied by local Nginx would share one peer bucket.
- Add Nginx connection/request limiting and resource monitoring before exposing
  Argon2id work to an untrusted network. Application buckets alone do not stop a
  distributed CPU-exhaustion attempt.
- Define generation, storage, access, backup and rotation for the production
  rate-limit HMAC key. Rotation must have an explicit bucket-reset consequence.
- A structural parity test exists, but no statistical remote timing study was
  performed. Reassess timing after proxy and production hardware are known.
- Keep the approved same-origin model. Any cross-origin client requires a new
  CORS, CSRF and cookie review.
- Password creation/reset still requires an approved offline compromised-
  password source. No real account may be created before that gate and the
  off-server backup/restore gate are closed.
- MFA, recovery and rotated full-session creation require their own focused
  review before any account can access the portal.

## Conclusion

The first-factor implementation is suitable as the synthetic foundation for
the TOTP/recovery slice. It is not deployable and does not authorize real
accounts or data. No high or critical finding remains in scope.
