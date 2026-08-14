# Initial Admin CLI Security Review

Date: 2026-08-14

## Scope

- interactive initial-admin service and PostgreSQL repository
- `competence-hub-admin create-initial-admin` command boundary
- password policy and offline compromised-password fingerprint loading
- synthetic unit and repository-adapter tests

The command was not run against Staging and no real account was created.

## Controls Verified

- no default username or password
- password and confirmation are read interactively, never as command arguments
- non-interactive execution fails closed before configuration is read
- database URL must use `postgresql+asyncpg`, loopback and the restricted
  `competence_hub_app` role
- compromised-password fingerprints come from an explicit absolute regular
  file and must be valid SHA-256 values; an empty source fails closed
- Argon2id hashing happens before persistence; only the encoded hash reaches the
  repository
- a transaction-scoped PostgreSQL advisory lock serializes bootstrap attempts
- an existing effective active Admin closes bootstrap before any write
- user, role, credential and secret-free audit event are created atomically
- SQLAlchemy hides parameters and CLI failures do not print exception details
- the database engine is disposed after success or failure

## Evidence

- focused tests: `21 passed`
- complete local suite: `164 passed, 12 skipped`
- Python compile check: passed
- dependency check: no broken requirements
- CLI help smoke: passed without reading runtime configuration

## Findings And Residual Gates

No open high or critical finding was identified in this local sub-slice.

- The approved offline compromised-password fingerprint source does not yet
  exist. The command cannot be used until that source and its operating owner
  are approved.
- The PostgreSQL transaction has not yet been integration-tested on Staging.
- Python cannot guarantee immediate zeroization of immutable password strings;
  the bounded CLI process should exit immediately after execution.
- Running the command would create a real privileged account and therefore
  requires separate explicit approval, protected pre/post dumps, synthetic
  rehearsal first and an MFA-enrollment handoff.
- Invitation/password-reset lifecycle and Outbox behavior are now implemented
  and proved separately. Direct initial-admin creation remains unexecuted and
  still requires its own explicit real-account gate.
