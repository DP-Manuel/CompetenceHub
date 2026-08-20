# Company And Contact Slice Security Review

Stand: 20.08.2026

## Scope

Reviewed the local company/contact service, PostgreSQL repository, protected
HTTP routes, runtime wiring, tests and API contract. The review covers internal
MFA sessions only. No persistent service, portal UI, real account, real company
data or deployment exists.

## Protected Assets And Trust Boundaries

- internal company records and confidential notes
- business-contact names, email addresses, phone numbers and functions
- internal `admin`/`internal` sessions and CSRF tokens
- append-oriented audit evidence
- browser-to-FastAPI and FastAPI-to-local-PostgreSQL boundaries

## Findings

### Medium - list response selected confidential internal notes - fixed

The first implementation reused the detail record for collection results. That
would have selected and returned `internal_notes` even though the information
architecture requires only name, status and industry in the list.

Fix: a separate `CompanySummary` now selects and returns only ID, name,
industry, provisional status and update timestamp. A repository and API
regression test asserts that `internal_notes` does not occur in the list SQL or
response.

### Medium - company creation is not persistently idempotent - open gate

A retry after a network timeout can create a second company/contact pair. No
security boundary is bypassed, but duplicate personal/business data and audit
events could result.

Required before productive UI use: disable repeated submission while pending
and choose a durable business idempotency design or explicit duplicate-review
workflow. Do not silently make company names unique because distinct legal
entities may share display names.

### Low - corrections use last-write-wins - accepted for one-editor pilot

PATCH operations update only explicit fields but do not yet use an ETag or
expected `updated_at`. Concurrent internal editors could overwrite each
other's corrections.

Required before broader rollout: add optimistic concurrency and a `409`
contract if more than the named pilot editor will work on the same records.

## Controls Confirmed

- active MFA session and `admin`/`internal` role required server-side
- exact Origin and session-bound CSRF required for all writes
- request bodies bounded to 32 KiB; unknown fields and empty patches rejected
- parameterized SQL; list size bounded to 100
- company plus initial contact and both audit events share one transaction
- audit contains no notes, contact data or raw request body
- generic not-found responses; contact corrections scoped to company ID
- global `no-store` and defensive response headers
- no delete route and no runtime delete privilege by design
- provisional status cannot be changed through this API

## Verification

- focused service/repository/API/runtime tests: 24 passed
- complete local suite: 231 passed, 14 opt-in Staging tests skipped
- compileall: passed
- dependency check: no broken requirements

## Remaining Gates

- run the prepared real PostgreSQL Staging path and prove zero residue
- verify runtime denial for company/contact DELETE and audit mutation
- approve final fields/status, retention and deletion policy
- close encrypted off-server restore, operations and production gates
- implement and test the UI duplicate-submit control

No open high or critical finding remains in the reviewed local slice.
