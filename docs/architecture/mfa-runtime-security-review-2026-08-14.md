# MFA Runtime Security Review - 2026-08-14

## Scope

Reviewed the local synthetic SB-06 implementation for TOTP enrollment and
verification, recovery-code verification, pre-auth challenge consumption,
full-session rotation, runtime key configuration and migration 0003.

ADR 0004 was accepted by Manuel after this review on 14.08.2026. The review and
that decision do not apply migration 0003, provision runtime secrets, create
real accounts or authorize a backend deployment.

## Result

No open high or critical finding was identified in the reviewed local slice.

## Verified Controls

- TOTP uses maintained library code with six digits, a 30-second period and a
  bounded previous/current/next-step window.
- The highest accepted TOTP counter is persisted through migration 0003 and
  the PostgreSQL completion update accepts only a strictly newer counter.
- TOTP secrets use AES-256-GCM with a fresh 96-bit nonce, versioned envelope
  and associated data binding ciphertext to user and key version.
- TOTP and recovery keys are external, versioned key rings; rate-limit HMAC,
  recovery HMAC and TOTP encryption keys remain separate.
- Recovery codes contain 80 random bits each, are returned only by successful
  enrollment confirmation and are represented in persistence only by HMAC
  digest plus key version.
- Challenge consumption, TOTP replay-counter update or recovery-code use,
  session creation and success audit occur in one database transaction.
- A disabled user or removed internal/admin role fails the final transaction,
  including when eligibility changes after the initial challenge read.
- Successful MFA creates a new opaque session and CSRF token, clears the
  pre-auth cookie and never promotes the pre-auth token into a session token.
- Origin and challenge-bound CSRF checks precede state-changing browser calls.
- MFA failures use HMAC-pseudonymized user/IP buckets with progressive limits;
  object representations suppress tokens, ciphertext, plaintext recovery
  codes and runtime key material.
- The application remains deny-by-default when no MFA service is wired.

## Residual Risks And Gates

- ADR 0004 is accepted. Migration `0003`, rollback smoke and 12/12 synthetic
  MFA Staging paths were subsequently completed; its PostgreSQL replay and
  recovery-key behavior now has real adapter evidence.
- Runtime keys have not been generated, stored with service-account-only
  permissions, backed up, rotated or tested for emergency revocation.
- Host clock synchronization and drift monitoring have not been added to the
  deployment runbook.
- The future portal UI must ensure provisioning URIs and recovery codes are
  never logged, cached, persisted in browser storage or exposed after the
  one-time enrollment response.
- No synthetic initial account exists yet, so complete password-to-MFA browser
  acceptance and recovery-code reuse tests remain Staging work.
- The off-server backup/restore and production operations gates remain open;
  real accounts and real data are still prohibited.

## Evidence

- Full local suite: `148 passed, 11 skipped`.
- Focused MFA HTTP/service/repository/runtime tests: `30 passed`.
- Runtime/keyring/security foundation tests: `71 passed` before the complete
  vertical slice.
- `compileall`: passed for `src` and `tests`.
- `pip check`: no broken requirements.
- `git diff --check`: no patch errors; existing Windows line-ending warnings
  only.

## Next Gate

1. Completed: migration `0003` was separately approved and applied to empty
   Staging on 14.08.2026 with protected pre/post dumps and rollback smoke.
2. Completed: enrollment, replay rejection, recovery single-use, rate limiting,
   session rotation and complete cleanup passed 12/12 Staging paths.
3. Remaining: create no real initial account until its separate approval,
   offline password-fingerprint source, backup gate and immediate MFA handoff
   are ready.
