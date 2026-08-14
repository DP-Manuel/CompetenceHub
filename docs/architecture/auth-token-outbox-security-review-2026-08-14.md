# Auth Token Outbox Security Review

Date: 2026-08-14

## Scope

- accepted ADR 0005
- migration `0004`, applied to isolated synthetic Staging after separate approval
- invitation and password-reset enqueueing
- Admin invitation HTTP boundary
- outbox claim, retry, completion, failure and cleanup behavior
- local synthetic tests and isolated PostgreSQL Staging evidence

## Findings

No open high or critical finding was identified in the local slice.

### Medium operational gate: delivery is not production-ready

No mail provider, sender domain, adapter, worker service, runtime keyring,
monitoring or approved retention period exists. The application therefore does
not wire the account-lifecycle service in its default runtime and fails closed.

Required before real delivery: approve provider and templates, provision a
separate outbox AES-256-GCM keyring and idempotency HMAC key outside Git and
PostgreSQL, define worker monitoring/recovery and retention, then perform a
separate deployment review.

### Low residual risk: external delivery is at least once

A worker can deliver successfully and fail before marking the database row as
delivered. The lease then permits a retry. Every adapter call receives the
stable outbox UUID as `delivery_id`; a future provider adapter should use it for
deduplication where supported. Templates must remain safe if a duplicate email
is nevertheless delivered.

### Low residual risk: known/unknown reset timing needs API-level measurement

HTTP responses are identical and unknown addresses create neither one-time
token nor outbox row. Known accounts perform additional transactional writes,
The Staging repository path proves that unknown addresses create no token or
outbox row and that cleanup leaves no residue. Comparative end-to-end HTTP
timing still needs measurement through a deployed isolated Staging API before
the endpoint is exposed.

### Low operational decision: retention periods remain open

Terminal rows immediately lose recipient address, key version and encrypted
payload. A cleanup operation accepts explicit cutoffs for terminal metadata and
expired idempotency records, but no period is hard-coded before Product Owner,
privacy and operations approval.

## Controls Verified Locally

- Separate cryptographic context and keyring contract for token outbox data.
- New random AES-GCM nonce and associated-data binding per outbox UUID/purpose.
- Only SHA-256 token digests enter the one-time-token table.
- Only HMAC digests of idempotency keys and canonical requests are stored.
- Same actor/scope/key/request replays the original user reference; changed
  request content conflicts before another token or message is created.
- Token, outbox and idempotency record are created in one transaction.
- Reissues cancel pending old messages and clear their sensitive fields.
- Claims use leases and `FOR UPDATE SKIP LOCKED`; exhausted or expired delivery
  revokes the corresponding unused token.
- Success, terminal failure and cancellation clear recipient and payload.
- Admin route requires MFA session, Admin role, fresh authentication enforced
  by the service, exact Origin, CSRF and a non-privileged initial role.
- API responses contain no invitation/reset token.

## Staging Gate

Completed on 2026-08-14 after Manuel's separate approval:

- protected 74-KiB pre-dump and 86-KiB post-dump, both `postgres:postgres`
  with mode `0600`; post-dump catalog is readable
- migrator execution of `0004` with `ON_ERROR_STOP` and `COMMIT`
- rollback-only smoke with zero residue
- 13/13 combined Staging paths in 156.91 seconds, including idempotency replay
  and conflict, encrypted enqueueing, delivery, terminal failure/token
  revocation, minimization, cleanup and unknown-reset behavior
- all eleven checked data areas empty after the run; migrations `0001`-`0004`
  registered and all 24 tables owned by `competence_hub_owner`
- runtime role can read but not update `roles`, cannot create schema objects or
  read migration metadata; all four co-hosted services remain active and
  PostgreSQL remains bound only to `127.0.0.1:5432`

The Staging run exposed an unnecessary `FOR SHARE` on the read-only roles
lookup. It was removed instead of granting the runtime role `UPDATE`; a local
regression assertion protects that least-privilege boundary. No real account,
personal data, provider, persistent backend/worker service or deployment was
authorized or used.
