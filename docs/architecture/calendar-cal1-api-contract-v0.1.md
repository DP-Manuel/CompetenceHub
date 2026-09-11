# CAL-1 API Contract v0.1

Stand: 11.09.2026

Status: proposed implementation contract under accepted ADR 0007. No endpoint
is implemented or deployed by this document.

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

### `GET /api/v1/portal/calendar/offers`

A Coach receives only offers linked through their own portal user. Admin may
filter by `coach_id`; other roles cannot use a query to widen scope.

### `POST /api/v1/portal/calendar/offers`

Creates a stable offer and draft revision. Required fields match the technical
design. A caller-generated `client_request_id` UUID is unique per actor so a
network retry returns the existing result instead of creating a duplicate.

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
| 503 | `portal_unavailable` | configured service unavailable |

Rate-limit responses remain generic and include `Retry-After`; exact Pilot
limits are a security/operations decision before implementation.

## Compatibility And Implementation Gate

- API v1 is additive; existing Auth/company endpoints do not change.
- Public DTOs are explicit and never mirror database rows.
- Cursor contents are opaque and protected against tampering.
- Migration `0005` is prepared locally; Staging application, routers and UI
  remain separate approval/implementation steps.
- Staging application, real Coach accounts and production remain separate
  gates.
