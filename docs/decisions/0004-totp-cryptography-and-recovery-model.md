# ADR 0004 - TOTP-Kryptografie und Recovery-Modell

Stand: 14.08.2026

## Status

Accepted by Manuel on 14.08.2026 for implementation under ADR 0003. This does
not approve migration 0003 on Staging, real accounts or deployment.

Migration 0003 received its required separate Staging approval later on
14.08.2026; real accounts, runtime secrets and deployment remain unapproved.

## Kontext

ADR 0003 requires TOTP for internal accounts, authenticated encryption of TOTP
secrets, HMAC-only recovery-code persistence, rate limiting and rotation from a
short-lived pre-auth challenge to a full server-side session. The current
schema already contains TOTP credentials, recovery codes, login challenges and
sessions, but it cannot yet reject reuse of an already accepted TOTP time step
and recovery rows do not identify their HMAC key version.

The application runs on Python 3.11 through 3.13. Secrets remain outside Git and
PostgreSQL. No external identity or MFA provider is approved.

## Entscheidung

### TOTP

- Use PyOTP 2.10.x for RFC-compatible TOTP generation, verification helpers and
  `otpauth` provisioning URIs.
- Baseline parameters are SHA-1, six digits and a 30-second period for broad
  authenticator compatibility.
- Generate 160-bit random Base32 secrets.
- Accept at most the previous, current or next time step to tolerate limited
  clock drift. Verification evaluates the full window.
- Persist the last accepted time step and atomically accept only a strictly
  newer step. A correct but replayed code fails closed.

### Secret encryption

- Use `cryptography` 49.x and AES-256-GCM with a new random 96-bit nonce for
  every encryption.
- Store a versioned binary envelope in `encrypted_secret`; keep the active key
  version in the existing `key_version` column.
- Authenticate user ID, envelope version and key version as associated data so
  ciphertext cannot be moved silently between users or key versions.
- Runtime configuration provides a key ring plus one active key version. Old
  keys remain readable during controlled rotation; new writes use only the
  active key. Keys never appear in object representations or logs.

### Recovery codes

- Generate ten independent human-readable codes with 80 bits of entropy each.
- Display plaintext codes exactly once after successful TOTP enrollment.
- Normalize presentation separators before HMAC calculation.
- Persist only HMAC-SHA-256 digests and a key version. The recovery HMAC key is
  separate from TOTP encryption and rate-limit HMAC keys.
- Consume one matching code atomically. Regenerating a set invalidates all
  previous unused codes.

### Session rotation

- Successful TOTP or recovery verification consumes the pre-auth challenge,
  creates a new opaque MFA session and returns a new session cookie plus a
  one-time session CSRF token.
- No pre-auth token becomes a full-session token. The pre-auth cookie is
  cleared on success.

## Schema consequence

Migration `0003_totp_replay_and_recovery_keys.sql` adds:

- nullable `last_accepted_time_step bigint` with a non-negative constraint to
  `auth_totp_credentials`
- non-empty `key_version` to `auth_recovery_codes`

No table or real data is introduced. Existing rows, if any, receive an explicit
legacy key-version marker that must be mapped before use.

## Alternatives

### Own TOTP implementation

Rejected. HMAC/time-step code and provisioning URI handling add avoidable
security and interoperability risk.

### `cryptography` TOTP plus AES-GCM only

Viable, but rejected for this slice. Its TOTP primitive does not provide the
same focused provisioning and validity-window ergonomics; application code
would carry more protocol glue. `cryptography` remains the encryption owner.

### Fernet

Viable authenticated encryption, but AES-GCM with an explicit versioned
envelope and associated user/key metadata fits the required key-ring rotation
and row-binding model more directly.

## Risiken und Gates

- Migration 0003 requires separate Staging approval, protected pre/post dumps,
  rollback-only smoke verification and complete synthetic cleanup.
- Runtime key generation, `0600` storage, backup, rotation and emergency
  revocation remain deployment gates.
- Clock synchronization and monitoring are operational requirements for TOTP.
- No real account may be enrolled before the off-server backup/restore and
  production-security gates are closed.

## Referenzen

- PyOTP documentation: <https://pyauth.github.io/pyotp/>
- PyOTP 2.10.0 package metadata: <https://pypi.org/project/PyOTP/>
- PyCA authenticated encryption documentation:
  <https://cryptography.io/en/stable/hazmat/primitives/aead/>
- PyCA `cryptography` package metadata:
  <https://pypi.org/project/cryptography/>
