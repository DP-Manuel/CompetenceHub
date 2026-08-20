# Company And Contact API Contract v0.1

Stand: 20.08.2026

## Purpose

This contract defines the smallest protected B2B data-entry slice for the
2026-08-28 pilot. An internal user can create a company together with its first
business contact, find and read companies, add contacts and correct the bounded
pilot fields. It does not implement requests, matching, contracts, feedback,
statistics or external company accounts.

## Security Boundary

- Consumers are authenticated browser users with active `admin` or `internal`
  roles and a completed MFA session.
- All responses use `Cache-Control: no-store`.
- Mutating requests require the exact configured HTTPS Origin and the
  session-bound `X-CSRF-Token`.
- JSON bodies are limited to 32 KiB and reject unknown fields.
- Authorization is server-side and deny-by-default. UI visibility is not an
  authorization control.
- Audit events contain actor, action, entity type/ID, outcome and timestamp,
  but no company notes, contact details or raw request payload.
- Physical company/contact deletion is not exposed to the runtime role or API.

## Provisional Data Cut

Company fields:

- `name`, required, maximum 200 characters
- `industry`, optional, maximum 200 characters
- `internal_notes`, optional, maximum 4,000 characters
- `status`, server-controlled initial value `prospect`

Contact fields:

- `first_name`, `last_name`, `email`, required
- `phone`, `job_function`, optional

`prospect` is a technical pilot default, not an approved final status
vocabulary or workflow. The API does not expose a status transition endpoint.
Legal name, display name, address, customer number and primary-contact flags
remain behind Gate B until Janay confirms a real need.

## Endpoints

### `GET /api/v1/portal/companies`

Optional `query` searches the company name. `limit` defaults to 50 and is
bounded to 100. Returns only ID, name, industry, status and update timestamp in
`{ "items": [...] }`; confidential internal notes are not selected for the
collection response. Pagination beyond the bounded pilot list is deferred.

### `GET /api/v1/portal/companies/{company_id}`

Returns the company and its contacts. Missing IDs return a generic `404`.

### `POST /api/v1/portal/companies`

Creates the company and required `initial_contact` atomically, then appends two
data-minimized audit events. Returns `201` with the created detail.

### `PATCH /api/v1/portal/companies/{company_id}`

Corrects only explicitly supplied `name`, `industry` or `internal_notes`.
Empty patches and a null name return `400`.

### `POST /api/v1/portal/companies/{company_id}/contacts`

Adds another business contact only when the company exists. Returns `201`.

### `PATCH /api/v1/portal/companies/{company_id}/contacts/{contact_id}`

Corrects only explicitly supplied contact fields and scopes the contact lookup
to the company ID. Empty patches and null required fields return `400`.

## Verification And Open Gates

Local service, PostgreSQL-adapter, HTTP and runtime tests cover normalization,
role denial, Origin/CSRF, bounded reads, atomic create, generic not-found
behavior, explicit-field patches and data-minimized audit calls.

Before Staging acceptance:

- run the opt-in PostgreSQL test with synthetic data and verify zero residue;
- verify the runtime app role can perform required DML but cannot delete
  companies/contacts or mutate audit rows;
- review duplicate-submit behavior. The v0.1 create route is not yet
  idempotent, so the UI must prevent repeated submission until a persistent
  business idempotency decision is implemented.

Before real data:

- complete encrypted off-server backup and restore evidence;
- approve retention/deletion and the final company/contact field cut;
- create named least-privilege users and complete MFA onboarding;
- pass deployment, privacy, security and stakeholder acceptance gates.
