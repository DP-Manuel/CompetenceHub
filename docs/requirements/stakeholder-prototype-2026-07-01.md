# Stakeholder Prototype Scope - 2026-07-01

Last updated: 2026-06-16

## Purpose

Define the first stakeholder-ready website prototype for the executive presentation on 2026-07-01.

## Source Inputs

- Team feedback: Variant B was preferred because it looked more modern.
- Manuel clarification: no chatbot should be added to the new website; the existing chatbot VPS is only relevant as an available technical resource.
- Manuel clarification: the future system needs its own independent database and should not use the parent company's existing database.
- Product direction: the later web-based system should resemble the old administration system in business coverage, but be independent and able to grow.
- Reference system: `http://sophisto.de/`.
- Future system idea backlog: `docs/requirements/future-system-ideas-backlog.md`.

## MVP Boundary For 2026-07-01

In scope:

- Public website prototype, based on the modern Variant B direction.
- Clear B2B message for companies.
- Visible Donner + Partner endorsement.
- Sections explaining seminars, needs discovery, qualification, placement, and future digital capability.
- A visual or inactive contact path if legal/privacy wording is not approved yet.
- A lightweight "future platform" cue that explains the direction without pretending the app already exists.
- Responsive desktop and mobile presentation quality.

Out of scope for 2026-07-01:

- Real database integration.
- Real login page or user accounts.
- Operational CRUD screens for companies, seminars, coaches, participants, or job posts.
- Chatbot integration.
- Migration from the old administration system.
- Production storage of personal, participant, company, or applicant data.

## Stakeholder Demo Requirements

- REQ-DEMO-001: The prototype shall present Variant B as the main visual direction.
- REQ-DEMO-002: The prototype shall make the offer understandable within the first viewport.
- REQ-DEMO-003: The prototype shall show the path from seminar to company need, qualification, matching, and entry.
- REQ-DEMO-004: The prototype shall mention that a digital system/app is planned, without claiming it is already implemented.
- REQ-DEMO-005: The prototype shall avoid chatbot promises or chatbot UI.
- REQ-DEMO-006: The prototype shall avoid real personal-data collection unless legal/privacy wording and processing are approved.
- REQ-DEMO-007: The prototype shall be presentable from the chosen subdomain or a reliable preview URL before 2026-07-01.

## Future System Requirements Draft

- REQ-SYS-001: The future system shall have its own independent database.
- REQ-SYS-002: The future system shall not depend on the parent company's existing administration database.
- REQ-SYS-003: The future system shall provide authenticated access through a login page.
- REQ-SYS-004: The future system shall manage companies, seminars, coaches, participants, and job postings.
- REQ-SYS-005: The future system shall expose application behavior through a backend API instead of allowing website or app clients to access the database directly.
- REQ-SYS-006: The future system shall start with simple workflows and data models, but keep room for growth.
- REQ-SYS-007: The future system shall define roles and permissions before operational personal data is stored.
- REQ-SYS-008: The future system shall eventually support document generation for offers and contracts.
- REQ-SYS-009: The future system shall eventually support job posting management and participant or skilled-worker matching.
- REQ-SYS-010: The future system shall eventually support company feedback workflows.

## Acceptance Criteria

- AC-001: Stakeholders can open the prototype and understand the offer without needing a verbal explanation of the whole model.
- AC-002: The prototype contains no working login or database-backed management screens.
- AC-003: The prototype contains no chatbot element.
- AC-004: The prototype visually signals the future app/system direction without overpromising availability.
- AC-005: The team has a documented follow-up path for backend, login, database, and data model work after the 2026-07-01 presentation.

## Open Questions

- What is the final public offer or sub-brand name?
- Which exact subdomain will be used?
- Who approves legal/privacy wording for contact interactions?
- Which parts of the old administration system must be mirrored first?
- Which roles are required for the first app slice: admin, staff, coach, company contact, participant, or others?
