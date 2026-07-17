# Initial Competence Hub Data Model

Last updated: 2026-07-16

## Goal And Scope

Define a small first model for internal login, companies, coaches, coaching
offers, assignments, and feedback. This is a design input, not an applied schema.

Assumptions:

- MySQL/MariaDB is the current database direction but still needs server verification.
- Internal Donner + Partner staff create and manage operational records first.
- The public Astro website has no direct database access.
- External company and coach accounts are later slices.

Out of scope for the first schema:

- Participant records, matching, invoices, contracts, calendars, file storage,
  public self-registration, and automated email sending.

## Core Entities

### User

Purpose: authenticated internal administration account.

Key fields: `id`, `email`, `display_name`, `password_hash`, `status`,
`last_login_at`, `created_at`, `updated_at`.

Rules: unique normalized email; password hashes only; initial roles are `admin`
and `staff`; disabled users cannot authenticate.

### Company

Purpose: company receiving or requesting services.

Key fields: `id`, `name`, `legal_name`, `status`, `industry`, `website`,
`address_*`, `notes`, timestamps.

Rules: archive instead of destructive deletion once assignments exist; free-text
notes are internal and excluded from public/API output by default.

### CompanyContact

Purpose: named contact belonging to a company.

Key fields: `id`, `company_id`, `name`, `role_title`, `email`, `phone`,
`is_primary`, `status`, timestamps.

Sensitivity: personal business contact data; define retention and access before
production use.

### Coach

Purpose: internal coach record plus controlled public-profile content.

Key fields: `id`, `display_name`, `professional_title`, `bio_public`,
`location_public`, `profile_slug`, `publication_status`, `status`, timestamps.

Rules: public fields are separated from private contact/contract data; unique
profile slug; publication requires content and image approval.

### Service

Purpose: reusable coaching, consultation, workshop, supervision, or talk offer.

Key fields: `id`, `name`, `service_type`, `summary`, `delivery_mode`,
`duration_minutes`, `status`, timestamps.

Rules: price is not stored until price unit, VAT, inclusions, and discount rules
are defined. `service_type` begins with coaching, consultation, supervision,
workshop, and talk.

### CoachService

Purpose: many-to-many link between coach and service.

Key fields: `coach_id`, `service_id`, `experience_note`, `is_primary`, timestamps.

Rules: unique pair of coach and service.

### CoachingRequest

Purpose: reviewed company need before an assignment exists.

Key fields: `id`, `company_id`, `company_contact_id`, `topic`, `target_group`,
`preferred_mode`, `preferred_period`, `status`, `internal_notes`, timestamps.

Lifecycle: `new`, `qualifying`, `proposal`, `accepted`, `declined`, `archived`.

### Assignment

Purpose: agreed connection between a company request, coach, and service.

Key fields: `id`, `request_id`, `coach_id`, `service_id`, `starts_at`, `ends_at`,
`delivery_mode`, `status`, `commercial_terms_snapshot`, timestamps.

Lifecycle: `draft`, `proposed`, `confirmed`, `completed`, `cancelled`.

Rule: preserve agreed commercial terms as a historical snapshot when pricing is
introduced later.

### CompanyFeedback

Purpose: company feedback about a completed assignment.

Key fields: `id`, `assignment_id`, `company_contact_id`, `rating`, `comment`,
`consent_to_publish`, `submitted_at`, `status`.

Rules: feedback is private by default; publication requires explicit approval;
external token links need expiry and revocation in a later design.

### AuditEvent

Purpose: trace sensitive administrative changes.

Key fields: `id`, `actor_user_id`, `entity_type`, `entity_id`, `action`,
`occurred_at`, `metadata_redacted`.

Rules: never log passwords, tokens, full personal-data payloads, or secrets.

## Main Relationships

- Company 1:n CompanyContact.
- Company 1:n CoachingRequest.
- Coach n:m Service through CoachService.
- CoachingRequest 1:n Assignment.
- Coach 1:n Assignment.
- Service 1:n Assignment.
- Assignment 1:n CompanyFeedback.
- User 1:n AuditEvent.

## Initial Indexes

- Unique: `user.email`, `coach.profile_slug`, `coach_service(coach_id, service_id)`.
- Lookup: company name/status, coach publication/status, request company/status,
  assignment coach/status/start date, feedback assignment/status.
- Add further indexes only from real query and reporting needs.

## Privacy And Lifecycle Decisions Still Needed

- Contact-data retention and deletion rules.
- Which coach fields are public, internal, or contract-sensitive.
- Whether feedback is anonymous, named, token-based, or account-based.
- Audit retention and access.
- Backup encryption, retention, deletion, and restore tests.
- Legal basis and notice for website-originated company inquiries.

## Implementation Handoff

Before writing migrations, select the backend stack and ORM/migration tool, turn
these entities into accepted user stories, define API contracts and role checks,
and review the schema for security and privacy. Start with fake test data only.
