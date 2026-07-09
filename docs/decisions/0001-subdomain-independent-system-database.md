# ADR 0001 - Subdomain, Independent Web System, And Database Direction

Date: 2026-06-16

## Status

Proposed

## Context

The project starts with a public website prototype for a stakeholder presentation on 2026-07-01. The preferred visual direction is Variant B because it was perceived as more modern.

EDV has provided webspace and suggested a subdomain under `donner-partner.de` or a separate new domain. MySQL/MariaDB capacity is available on the provided server.

Manuel clarified that the new website should not include the existing chatbot. The existing chatbot VPS is only relevant as an available technical resource and operational reference.

The longer-term goal is a simple but expandable web-based system similar in business coverage to the old administration system at `http://sophisto.de/`. The system must be independent and use its own database, not the parent company's existing database.

## Decision

Use a subdomain under `donner-partner.de` for the first website path.

Keep the first stakeholder prototype database-free and focus it on the public website, offer explanation, and future-system story.

Treat the later app as an independent web system with:

- a login page,
- a backend API,
- its own database,
- role-based access,
- operational data models for companies, seminars, coaches, participants, and job postings.

Website and app clients shall not connect directly to the database. They shall access operational data through the backend API.

## Database Direction

The database is required for the future app, not for the 2026-07-01 prototype.

Preferred long-term technical direction:

- PostgreSQL if the system is hosted on the existing VPS or a managed database can be used.
- MariaDB/MySQL is acceptable if EDV-hosted infrastructure and operational simplicity are more important than the PostgreSQL preference.

The first real database decision should be made after a small data model and auth/role model are drafted.

## Rationale

- A subdomain keeps trust, SEO, and brand connection close to Donner + Partner.
- A separate new domain would require more brand-building and separate setup effort.
- A database-free first prototype reduces risk before the 2026-07-01 stakeholder presentation.
- A backend API protects the future database from direct client access and centralizes validation, permissions, auditing, and privacy controls.
- A separate database supports independence from the old or parent-company systems while allowing a controlled migration or parallel operation later.

## Consequences

- The website can stay static or mostly static for the first presentation.
- The first app slice must include auth, roles, API boundaries, and a data model before real personal or company data is stored.
- The project needs a later ADR for the final database engine and hosting location.
- The app should be planned as a separate deliverable from the public website, even if both share design language and brand assets.

## Risks And Mitigations

- Risk: Stakeholders may expect the app to exist because the website mentions future digital capability.
  - Mitigation: Use careful wording such as "geplant" or "digital anschlussfaehig" and avoid fake operational UI.

- Risk: Early database choice may lock the project into the wrong hosting model.
  - Mitigation: Draft the core data model first, then choose PostgreSQL, MariaDB/MySQL, or managed hosting based on actual workflows.

- Risk: Sensitive participant or company data is stored before roles, retention, and privacy rules exist.
  - Mitigation: No operational data storage before auth, permissions, backup/restore, retention, and legal/privacy rules are documented.

## Follow-Up Decisions

- Exact subdomain.
- Final public offer/sub-brand name.
- Backend runtime and hosting location.
- Database engine and hosting location.
- First app roles and permission model.
- First app slice: companies, seminars, coaches, participants, or job postings.
