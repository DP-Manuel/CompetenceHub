# Request Workflow Feedback - Janay Rappelt

Status: internal workflow input captured on 2026-08-14; transition model and
automation not yet approved.

## Purpose And Source Boundary

This note translates Janay Rappelt's internal feedback into implementation-
ready product input without copying the private Word document into the product
or public-content layer. The raw source remains in the approved internal source
folder.

The workflow facts below may guide requirements and data-model design. Example
claims from the source are not automatically commercial, legal or publication
approvals.

## Confirmed Operational Flow

1. **Initial inquiry and clarification**
   - The first inquiry should enter the central system immediately.
   - Record company, contact, target group or coachees, core topic and goal,
     desired timeframe, and delivery location or mode.
   - Location needs to distinguish the regional radius around Wuerzburg,
     delivery at the customer and remote delivery.
   - Success indicators and realistic coachee availability are frequently
     missing and should be made visible as clarification gaps.
2. **Coach matching**
   - Begin the search when the first conversation is documented and the
     requirement profile is sufficiently clear.
   - Contact two or three suitable Coaches in parallel where appropriate.
   - Initially disclose topic, objective, target group, scope or hours and
     region, but not the customer identity.
   - Disclose the customer identity only after a Coach indicates genuine
     interest and capacity and the approved confidentiality step is complete.
   - If a Coach declines, continue with the next shortlist candidate. If the
     pool is exhausted, expand the network and inform the customer honestly.
3. **Offer and order**
   - Prepare an offer only after a Coach has conditionally confirmed interest
     and capacity for a defined reservation period.
   - The customer receives the proposed Coach with one or two approved short
     profiles as part of the offer process.
   - Backoffice or project management prepares the offer; Janay currently owns
     this task operationally.
   - A request becomes a binding order only after documented acceptance through
     a legally approved channel.
4. **Kickoff and delivery**
   - Competence Hub coordinates the kickoff between Coach, coachee and customer.
   - Coach and coachee may coordinate later appointments directly within the
     agreed framework.
   - Delivery evidence includes the last booked session plus an internal
     activity or time record and an approved minimal completion note.
5. **Evaluation and closure**
   - Competence Hub, not the Coach, requests customer feedback.
   - Closure requires evaluated feedback, final invoicing, confirmed payment
     and an explicit closed status.
6. **Exceptions**
   - A request may be cancelled before an order.
   - Cancellation after an order follows approved contractual terms.
   - Paused work needs an `on hold` state and a dated reminder.
   - If no Coach can be matched, offer a later start or expanded search and
     communicate the situation transparently.

## Data Needed Later

- inquiry owner, company and contact reference
- target group or coachee description
- topic, objective and desired outcome
- timeframe, scope or hours, delivery mode, region and travel radius
- success criteria or KPI clarification status
- coachee availability and other unresolved requirements
- Coach shortlist candidates, contact and response state
- capacity reservation and expiry
- customer-identity disclosure authorization and timestamp
- proposed Coach profiles attached to an offer
- offer version, owner and status
- acceptance evidence without treating an unapproved click as legally binding
- kickoff and delivery milestone status
- activity or time evidence and minimal completion evidence
- feedback request, response and evaluation state
- invoice and payment status references
- pause reason, reminder date, cancellation and no-match outcome
- audit events for sensitive disclosure and material state changes

## Privacy And Security Requirements

- Minimize customer identity disclosure during initial Coach availability
  checks.
- Record who authorized and performed identity disclosure and when it happened.
- Do not place free-form health, crisis or other sensitive details in general
  logs, analytics or notifications.
- Define field-level purpose, access scope, retention and deletion before real
  inquiry data is accepted.
- Keep internal completion notes proportionate; no therapy or health record is
  implied by this workflow.
- Enforce server-side role and assignment checks for all request, matching,
  offer, feedback and finance status access.

## Proposed State Model - Decision Required

The following vocabulary is a design proposal, not an approved automation:

`new -> clarification -> matching -> capacity_held -> offer_sent -> ordered ->
in_delivery -> delivered -> evaluation -> payment_pending -> closed`

Possible side states are `on_hold`, `cancelled` and `no_match`. Re-entry,
terminal states, actor permissions, notifications and automatic transitions
must be approved before a database constraint or workflow engine is added.

## Open Gates

- **Requirements:** approve exact states, transitions, re-entry rules and actor
  responsibilities with Janay.
- **Legal/commercial:** approve acceptance channel, cancellation terms,
  capacity-reservation wording and any response-time commitment.
- **Privacy:** approve customer-identity disclosure timing, data minimization,
  free-text limits, retention and deletion.
- **Finance:** define the source of truth for offer, invoice and payment status.
- **Content/rights:** define whether short profiles are named or anonymized and
  which profile material is approved for offers.
- **Operations:** define reminders, absence cover and escalation when no Coach
  is available.

## Non-Approved Example Material

The example in the source that mentions a 48-hour offer, named package options,
click acceptance, specific session formats and a five-star result is a scenario
draft only. It is not an SLA, price approval, legal acceptance mechanism,
customer case, reference, measured outcome or public claim.

## Implementation Consequences

- Do not alter migration `0001` immediately. Its request core remains suitable
  for early CRUD and discovery work.
- Design matching, capacity holds, offer/order evidence, feedback and closure
  as later additive migrations after the relevant gates are approved.
- Keep the current authentication/runtime sprint independent from this fachlich
  workflow. Janay's feedback informs the first business slice after controlled
  staging acceptance.

## Acceptance Criteria For A Future Workflow Slice

- A request can record the confirmed first-call fields and show unresolved
  clarification gaps.
- Coach availability can be checked without prematurely exposing customer
  identity.
- Multiple shortlist candidates can coexist without implying an assignment.
- Offer, order, delivery, feedback, invoice and payment are distinguishable.
- Paused, cancelled and no-match paths remain auditable and recoverable where
  approved.
- Unauthorized users cannot view or change requests, identities, matching or
  closure evidence.
- Automated transitions are absent until the transition model is approved.
- Tests cover positive, negative, role, disclosure, pause, cancellation and
  no-match paths with synthetic data only.
