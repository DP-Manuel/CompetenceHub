# Account Lifecycle Security Review

Date: 2026-08-14

Follow-up status: ADR 0005 was accepted and its encrypted transactional Outbox,
persistent HMAC idempotency and bounded worker repository were implemented.
Migration `0004`, rollback smoke and 13/13 synthetic Staging paths were later
completed with zero residue. The original medium finding is closed for reliable
database enqueue/idempotency; external provider delivery remains an operational
gate.

## Findings

### Medium gate: reliable delivery and persistent idempotency are unresolved

The local service can issue invitation and reset tokens, but the contracted
Admin HTTP endpoint requires persistent idempotency and reliable delivery.
Synchronous post-commit delivery would leave retry windows. The Admin issue
route and runtime delivery therefore remain fail-closed. ADR 0005 proposes a
transactional encrypted outbox and HMAC-only idempotency records.

Impact is currently contained: no backend is deployed, no delivery adapter is
configured and no real account or token exists.

### Low residual: known and unknown reset timing needs outbox-level evidence

HTTP bodies and status codes are identical for known and unknown accounts.
Once delivery is enabled, known accounts perform an outbox write while unknown
accounts do not. Timing comparability must be measured and, if needed, padded
or normalized during the Staging proof.

### Low residual: delivery failure currently relies on safe reissue

The abstract delivery adapter can report a generic failure after token commit.
No token is exposed, and a later request revokes the old token, but reliable
retry is intentionally deferred to ADR 0005.

## Controls Verified

- 256-bit random bearer tokens; only SHA-256 token digests reach repositories
- token and password fields are excluded from dataclass representations
- Argon2id password policy is evaluated before persistence
- invitation acceptance activates the user and creates only a short-lived MFA
  enrollment challenge, never a full session
- reset confirmation consumes the token and revokes all sessions, open reset
  tokens and login challenges atomically
- issue/request/confirm rate-limit buckets use separate HMAC namespaces
- Admin invitation service accepts only `internal`, requires Admin role and a
  fresh authentication age of at most 15 minutes
- exact Origin, strict JSON models, 32-KiB request limit and generic failures
- successful reset and invitation acceptance clear conflicting browser cookies
- no raw email is stored in rate-limit buckets or unknown-account audit rows
- runtime without lifecycle service and delivery adapter returns controlled 503

## Evidence

- lifecycle service/repository tests: 19 passed
- lifecycle plus existing Auth API regression: 38 passed before final hardening
- complete local suite after hardening: `194 passed, 12 skipped`
- Python compile check: passed
- dependency check: no broken requirements

## Remaining Test And Delivery Gates

- real PostgreSQL transaction/integration proof is complete for invitation,
  reset, idempotency and Outbox paths; direct initial-admin creation remains a
  separate real-account gate
- ADR 0005 is accepted and migration `0004` is applied/proved on isolated
  synthetic Staging
- no approved mail provider, sender, template, retention or monitoring exists
- no real account, real personal data, persistent service or deployment occurred

No open high or critical finding was identified. External delivery operations
still block claiming the complete invitation-dispatch feature as production-ready.
