# Public Contact Request Delivery

Last updated: 2026-09-01

## Purpose

Define the safe replacement for the public Website's temporary `mailto:`
handoff. The intended user experience submits the request directly through the
Website and routes it to Frau Janay Rappelt without requiring a local mail
client.

## Current State

- The public form currently prepares an E-Mail in the visitor's mail client.
- The form does not store or transmit data through a Website backend.
- Required fields are name, E-Mail address and topic. The free-text concern is
  optional.
- The UI must state this temporary behavior honestly until the direct delivery
  gate is closed.

## Target Flow

1. A visitor submits the minimum required contact data on the Website.
2. A same-origin server endpoint validates the request, rejects automated
   abuse and records only the approved minimum operational metadata.
3. The request is delivered to the approved Competence Hub mailbox owned by
   Frau Janay Rappelt.
4. The visitor receives an accessible success or retry message without leaving
   the Website.
5. Delivery failure remains observable to the responsible operator and does
   not produce a false success response.

## Required Decisions And Inputs

- Final Website runtime capability for a same-origin PHP endpoint on IONOS.
- Approved recipient, sender, reply-to and envelope-sender rules from EDV.
- Privacy notice, retention period and legal basis for submitted request data.
- Spam protection that does not introduce an unapproved external processor.
- Rate limit, input-size limits, logging minimization and incident ownership.
- Mail delivery monitoring, failure handling and Janay's absence cover.

No SMTP credentials, recipient secrets or production configuration belong in
Git. Public E-Mail addresses may be configured in the deployment environment,
but authentication material must remain external.

## Functional Requirements

- CONTACT-001: The direct endpoint accepts only `POST` over HTTPS from the
  canonical Website origin.
- CONTACT-002: Name, syntactically valid E-Mail address and one approved topic
  are required; company and concern text are optional.
- CONTACT-003: Unknown fields, oversized values and invalid encodings are
  rejected without reflecting raw input.
- CONTACT-004: The endpoint must not accept a recipient address from the
  browser.
- CONTACT-005: Success is shown only after the server accepts the request for
  approved delivery or durable processing.
- CONTACT-006: User-facing errors remain generic while operational logs retain
  a secret-free correlation identifier and delivery state.
- CONTACT-007: The endpoint applies CSRF/origin checks where technically
  appropriate, a honeypot or equivalent low-friction abuse signal and bounded
  rate limiting.
- CONTACT-008: The endpoint sends no internal notes, hidden form data or
  unnecessary technical metadata to the public requester.
- CONTACT-009: The temporary `mailto:` flow is removed only after production
  delivery, failure and rollback tests pass.

## Acceptance Evidence

- Valid synthetic submission succeeds without opening a local E-Mail client.
- Missing required fields, malformed E-Mail, oversized input, forged recipient
  and cross-origin submission are rejected.
- Repeated automated submissions are bounded without blocking an ordinary
  single request.
- Mail reaches the approved test mailbox with the intended sender and reply-to
  behavior; no credentials or sensitive values appear in source, response or
  logs.
- Simulated delivery failure produces no false success and is visible to the
  operator.
- Keyboard, screen-reader and 390-pixel mobile checks cover loading, success
  and error states.
- The old Website artifact remains restorable if the endpoint or routing fails.

## Gate

Status: **specified, not implemented**. Direct submission and publication are
blocked by EDV mail/runtime details, privacy approval and an explicit
production rehearsal. The current Website must not imply that direct delivery
already exists.
