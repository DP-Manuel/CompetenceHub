# CAL-1 API Contract v0.1

Stand: 18.09.2026

Status: API and migrations are proven locally and on isolated Staging under
accepted ADR 0007. The synthetic Portal UI is implemented and automatically
verified locally on 18.09.2026; manual browser acceptance remains open. The
routers and UI are not deployed.

## Boundary And Common Rules

- `/api/v1/calendar` provides anonymous read-only published data.
- `/api/v1/portal/calendar` provides protected Coach/review workflows.
- Protected writes require active MFA, exact Origin, `X-CSRF-Token`, JSON and
  the existing 32 KiB body limit.
- Unknown fields are rejected. Pilot responses use `Cache-Control: no-store`.
- IDs are UUIDs. Dates are RFC 3339 timestamps; `time_zone` is an IANA zone.
- Protected lookups return generic `404` for unknown and invisible records.
- Mutations carry `If-Match: "v<lock_version>"`; stale versions fail without a
  partial change.

## Public Operations

### `GET /api/v1/calendar/offers`

Returns only active offers with an approved published revision.

Query:

- `from`, `to`: required bounded date range inside the planning window;
- `topic_id`: optional UUID;
- `limit`: default 50, maximum 100;
- `cursor`: optional opaque continuation token.

Response:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000001",
      "coach": {
        "display_name": "Beispielcoach",
        "profile_path": "/coaches/beispielcoach/"
      },
      "topic": {
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "Kommunikation"
      },
      "title": "Beispielangebot",
      "summary": null,
      "starts_at": "2026-10-17T08:00:00Z",
      "ends_at": "2026-10-17T14:00:00Z",
      "time_zone": "Europe/Berlin",
      "format": "praesenz",
      "public_location": "Wuerzburg",
      "capacity": 30,
      "decision_deadline": "2026-10-02T21:59:59Z",
      "price_display_text": "Preis nach Abstimmung",
      "updated_at": "2026-09-18T09:30:00Z"
    }
  ],
  "next_cursor": null
}
```

All values are synthetic and approve neither format vocabulary, capacity nor
price wording.

### `GET /api/v1/calendar/offers/{offer_id}`

Returns the same public shape. Unpublished, withdrawn and unknown IDs share
one generic `404` response.

## Coach Operations

### `GET /api/v1/portal/calendar/capabilities`

Returns server-derived booleans for own-offer management, review and the
documented Admin Calendar scope. It does not expose identity heuristics or
replace endpoint authorization. Non-Calendar roles receive `403`.

### `GET /api/v1/portal/calendar/topics`

Returns active topic IDs and names visible to the linked Coach scope. Admin
may read the documented cross-Coach topic projection. Topic IDs are submitted
as controlled references but are not shown as technical UI content.

### `GET /api/v1/portal/calendar/offers`

A Coach receives only offers linked through their own portal user. Admin may
filter by `coach_id`; other roles cannot use a query to widen scope.

### `POST /api/v1/portal/calendar/offers`

Creates a stable offer and draft revision. Required fields match the technical
design. A caller-generated `client_request_id` UUID is unique per actor so a
network retry returns the existing result instead of creating a duplicate.

The JSON body contains `client_request_id`, optional Admin-only `coach_id` and
a `draft` object. Draft fields are `topic_id`, `title`, optional `summary`,
`starts_at`, `ends_at`, `time_zone`, `format`, optional `public_location`,
`capacity`, internal `review_threshold`, `decision_deadline` and
`price_display_text`. Unknown fields fail closed.

Returns `201`, protected detail and `ETag: "v1"`.

### `GET /api/v1/portal/calendar/offers/{offer_id}`

Returns stable metadata, current draft/review state and the last published
projection visible to that actor. Review notes are visible only to reviewers,
Admin and the owning Coach when they are an explicit change request.

### `PATCH /api/v1/portal/calendar/offers/{offer_id}/draft`

Edits an existing `draft`. If the latest submitted revision received a change
request, or the offer has only a published revision, the first edit creates
the next draft transactionally. Reviewed and published revisions remain
immutable.

The body is the draft object described by the create operation. Calendar
requests do not accept or mutate `public_profile_path`.

### `POST /api/v1/portal/calendar/offers/{offer_id}/submit`

Validates all publication fields and moves the draft to `in_review`. It does
not publish, reserve places or send E-Mail.

### `POST /api/v1/portal/calendar/offers/{offer_id}/withdraw`

Withdraws an own offer and removes the public projection. The action is
audited. CAL-2/CAL-4 notification consequences remain outside this endpoint.

## Reviewer Operations

### `GET /api/v1/portal/calendar/review-queue`

Requires `calendar_reviewer` or Admin. Returns bounded `in_review` summaries,
oldest first, with a maximum page size of 100. Internal users without this
dedicated permission are denied.

### `POST /api/v1/portal/calendar/offers/{offer_id}/review-decisions`

Requires `calendar_reviewer` or Admin and `If-Match`.

```json
{
  "outcome": "published",
  "note": null
}
```

Allowed outcomes are `published` and `changes_requested`. A change request
requires a bounded note. Publication must satisfy every public field and
atomically supersedes the prior public revision, publishes the reviewed one,
increments the version and appends decision plus audit evidence.

## Error Contract

Errors use the existing problem response without raw exception or private
record values.

| HTTP | Code | Meaning |
| --- | --- | --- |
| 400 | `invalid_request` | malformed, unknown or invalid field |
| 401 | `authentication_failed` | no active session |
| 403 | `authorization_failed` | role/scope denied |
| 403 | `request_verification_failed` | Origin or CSRF failed |
| 404 | `calendar_offer_not_found` | unknown or invisible record |
| 409 | `calendar_version_conflict` | missing/stale `If-Match`; reload required |
| 409 | `calendar_transition_conflict` | command invalid in current state |
| 409 | `calendar_time_conflict` | overlapping submitted/published interval for the same Coach |
| 409 | `calendar_idempotency_conflict` | request UUID reused with different content |
| 503 | `portal_unavailable` | configured service unavailable |

Rate-limit responses remain generic and include `Retry-After`; exact Pilot
limits are a security/operations decision before implementation.

## Compatibility And Implementation Gate

- API v1 is additive; existing Auth/company endpoints do not change.
- Migration `0006` adds nullable, explicitly managed and unique
  `coaches.public_profile_path`. It accepts only canonical
  `/coaches/<slug>/` values and never derives a path from a display name. No
  real Coach row is mapped by the migration.
- Public DTOs are explicit and never mirror database rows.
- Cursor contents are opaque and protected against tampering.
- Public fields are exactly: offer ID, Coach display name and nullable profile
  path, topic ID/name, title/summary, start/end/time zone, format, public
  location, capacity, decision deadline, price display text and update time.
- Public responses intentionally exclude Coach UUID, Portal user ID, actor and
  reviewer IDs, review threshold, review decisions/notes, drafts, unpublished
  revisions, audit/idempotency data and lock version.
- Migration `0005` remains unchanged and proven on isolated Staging. Migration
  `0006`, its rollback smoke and the protected/public routers passed focused
  3/3 and complete 17/17 native Staging tests with zero residue.
- Synthetic Portal UI and local automated checks are complete. Manual browser
  acceptance, native Staging UI, real Coach accounts, real mappings/data and
  production remain separate gates.
