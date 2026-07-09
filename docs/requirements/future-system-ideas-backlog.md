# Future System Ideas Backlog

Last updated: 2026-06-16

## Purpose

Collect ideas and future requirements for the independent web-based administration system. This is intentionally broader than the 2026-07-01 website prototype.

The backlog preserves brainstorming input so it can later be turned into user stories, architecture, data model, API contracts, and implementation slices.

## Source Inputs

- Brainstorming from Manuel and colleague on 2026-06-16.
- Direction: build a simple but expandable web-based system, similar in business coverage to the old Sophisto-like administration system, but independent.
- Reference system: `http://sophisto.de/` should be reviewed later; initial fetch attempt on 2026-06-16 timed out.

## Product Direction

The system should begin simply, but grow into an operational platform for managing companies, seminars, coaches, participants or skilled workers, job postings, matching, offers, contracts, and communication.

The public website and the later app may both initiate data flows, but operational creation, review, approval, and management should happen through the authenticated app and backend API. The public website should only collect or submit limited lead/contact data once legal and privacy processing are approved.

Initial business priority: start with seminars because the project first needs external attention and company-facing offers. The first document priority is offers, then company contracts, because the early business model is expected to focus on company trainings.

Current pain point from the old workflow: participants must be created, booked into an existing measure/course/seminar, and for internships booked to a company. If the company is missing, staff must create it during the process. The most painful part is the document package: multiple Word documents must be printed or exported one by one, manually converted to PDF, merged into one PDF, paired with a suitable email text, and sent to the company.

## Idea Backlog

### Data-Based Document Generation

- IDEA-DOC-001: The system should automatically generate contracts from stored data.
- IDEA-DOC-002: The system should automatically generate offers or proposals from stored data.
- IDEA-DOC-003: Generated documents should use approved templates.
- IDEA-DOC-004: Generated documents should be reviewable before sending.
- IDEA-DOC-005: Generated documents should be versioned or traceable after sending.
- IDEA-DOC-006: Generated documents should be exportable as files suitable for email sending, such as PDF attachments or secure download links.
- IDEA-DOC-007: Document generation should separate template content from variable system data so wording can be approved without code changes.
- IDEA-DOC-008: The system should support a one-button document package workflow for a participant, measure/course/seminar, internship/company, or company-training context.
- IDEA-DOC-009: The system should generate or collect multiple required documents into one final PDF package where appropriate.
- IDEA-DOC-010: Word document templates may remain the editable source format if that is the practical way to preserve formatting.
- IDEA-DOC-011: The system should reduce manual Word-to-PDF conversion, PDF merging, and repeated printing/export steps.
- IDEA-DOC-012: The system should support suggested email text for generated document packages.
- IDEA-DOC-013: Offers should be treated as the first document-generation priority, followed by company contracts.

### Email And Sending Workflows

- IDEA-MAIL-001: The system should send generated contracts and offers by email.
- IDEA-MAIL-002: A dedicated email account or mailbox must be created before production sending.
- IDEA-MAIL-003: The system should record sending status, recipient, timestamp, and delivery outcome where technically possible.
- IDEA-MAIL-004: Hermes Agent may be evaluated later as a mail/automation component, potentially hosted on the existing VPS if resource and security checks pass.
- IDEA-MAIL-005: Email sending should support attachments or secure document links, depending on privacy, file-size, and audit requirements.
- IDEA-MAIL-006: Outbound emails should use approved sender identity, signature, reply-to handling, and logging rules.
- IDEA-MAIL-007: The system should support reusable or generated email text for sending offers, contracts, and document packages to companies.

### Job Posting Management

- IDEA-JOB-001: The system should allow staff to create and manage job postings for companies.
- IDEA-JOB-002: Job postings should support a status such as active, inactive, draft, filled, or archived.
- IDEA-JOB-003: Job postings should support an internal flag such as "direct placement" versus "could be interesting".
- IDEA-JOB-004: Job postings should be connected to the company that provided or owns the position.
- IDEA-JOB-005: Job postings should include hard skills, soft skills, location, working model, required qualification, and optional notes.
- IDEA-JOB-006: Job postings should support a workflow from company request through internal review, publication or internal-only handling, matching, placement attempt, and closure.
- IDEA-JOB-007: The system should distinguish externally visible job postings from internal matching opportunities.
- IDEA-JOB-008: Donner + Partner staff should be the only users allowed to create and approve company, participant, job posting, seminar, and operational records in the initial app model.
- IDEA-JOB-009: For company training requests, staff may create and release an internal opportunity such as a seminar request for "KI im Büroalltag" so coaches or lecturers can indicate interest.
- IDEA-JOB-010: Staff should decide which interested coach or lecturer is actually selected for the assignment, even if matching support exists later.

### Matching

- IDEA-MATCH-001: The system should match participants or skilled workers against job postings.
- IDEA-MATCH-002: Matching should compare hard skills and soft skills.
- IDEA-MATCH-003: Matching should be possible without AI at first, using structured fields such as dropdowns, tags, controlled vocabularies, and scoring rules.
- IDEA-MATCH-004: AI-assisted matching may be evaluated later if rule-based matching is not expressive enough.
- IDEA-MATCH-005: Matching should explain why a participant or skilled worker is considered suitable or unsuitable.
- IDEA-MATCH-006: Matching should allow staff to override, confirm, reject, or comment on a suggested match.
- IDEA-MATCH-007: Matching should define how mandatory criteria, optional criteria, missing data, exclusions, and soft preferences affect the result.
- IDEA-MATCH-008: Matching should preserve a snapshot of relevant criteria when a match recommendation is made, so later changes do not silently rewrite the historical reasoning.
- IDEA-MATCH-009: Matching output should initially be designed around a score.
- IDEA-MATCH-010: Staff should remain the final decision-maker for whether a participant/skilled worker, coach, lecturer, company, job posting, or seminar request actually matches.
- IDEA-MATCH-011: Coach/lecturer matching may be needed separately from participant/skilled-worker-to-job matching.

### Travel-Time Calculation

- IDEA-ROUTE-001: The system should calculate commute time from a participant or skilled worker to a potential workplace.
- IDEA-ROUTE-002: Commute time should support public transport and car routes.
- IDEA-ROUTE-003: Commute calculation should be optional at first and may depend on a third-party routing API.
- IDEA-ROUTE-004: The system should store enough location data to support commute checks while minimizing sensitive address exposure.
- IDEA-ROUTE-005: Route results should be treated as estimates and should show when they were last calculated.

### Company Feedback

- IDEA-FB-001: Companies should be able to submit feedback through a link or email-based flow.
- IDEA-FB-002: Feedback links should be scoped to a specific company, job posting, participant, match, seminar, or placement context.
- IDEA-FB-003: Feedback should be easy for company contacts to submit without requiring a full app account in the first version, if privacy/security allows it.
- IDEA-FB-004: Submitted feedback should become visible to authorized staff in the system.
- IDEA-FB-005: Feedback requests should be sendable after a match, placement, seminar, offer, or contract workflow event.
- IDEA-FB-006: Feedback links should expire or be revocable if token-based links are used.
- IDEA-FB-007: Companies should be able to view their own past orders, trainings, coaches, and related history once a company portal exists.

### Authentication And Roles

- IDEA-AUTH-001: The system needs a login page before operational data management begins.
- IDEA-AUTH-002: The first role model should distinguish at least internal admin/staff from external users.
- IDEA-AUTH-003: Later roles may include coach, company contact, participant, and read-only reviewer.
- IDEA-AUTH-004: Permissions must be defined before personal, participant, company-contact, or applicant data is stored.
- IDEA-AUTH-005: External company feedback flows may use scoped links before full external accounts exist, but only after privacy and security review.
- IDEA-AUTH-006: Donner + Partner staff should be able to create and manage operational records; external users should not create core records in the initial model.
- IDEA-AUTH-007: Company contacts should eventually be able to view their own company history, orders, trainings, coaches, and feedback options.
- IDEA-AUTH-008: Coaches and lecturers should eventually have personal accounts with calendars, assignment history, statistics, and accept/decline flows.
- IDEA-AUTH-009: Coaches and lecturers should be able to express interest in released assignments or seminar opportunities.
- IDEA-AUTH-010: Participants may eventually receive a separate app, but participant self-service is a later project track and should not drive the first app slice.

### Core Entities

- IDEA-DATA-001: The system should manage companies.
- IDEA-DATA-002: The system should manage company contacts.
- IDEA-DATA-003: The system should manage seminars.
- IDEA-DATA-004: The system should manage coaches.
- IDEA-DATA-005: The system should manage participants or skilled workers.
- IDEA-DATA-006: The system should manage job postings.
- IDEA-DATA-007: The system should manage matches between participants or skilled workers and job postings.
- IDEA-DATA-008: The system should manage generated documents and outbound communication records.
- IDEA-DATA-009: The system should manage company feedback.
- IDEA-DATA-010: The system should manage document templates.
- IDEA-DATA-011: The system should manage skill catalogs or controlled vocabularies for hard skills and soft skills.
- IDEA-DATA-012: The system should manage placement or matching workflow states.
- IDEA-DATA-013: The system should manage measures/courses/seminars as bookable entities.
- IDEA-DATA-014: The system should manage participant bookings into measures/courses/seminars.
- IDEA-DATA-015: The system should manage internship or placement bookings that connect participants to companies.
- IDEA-DATA-016: The system should manage coach/lecturer calendars, assignment requests, accept/decline decisions, and assignment history.
- IDEA-DATA-017: The system should manage company-visible history such as orders, trainings, coaches, and feedback records.
- IDEA-DATA-018: The system should manage participant-app content ideas separately from the first administration app, such as onboarding, life in Germany, and German as a foreign language.

### Participant, Measure, And Internship Workflow

- IDEA-PART-001: Staff should be able to create a participant record and enter the relevant information.
- IDEA-PART-002: Staff should be able to book a participant into an already-created measure, course, or seminar.
- IDEA-PART-003: Staff should be able to book a participant into an internship or placement at a company.
- IDEA-PART-004: If the required company does not exist during internship or placement booking, staff should be able to create the company without abandoning the workflow.
- IDEA-PART-005: The participant booking workflow should be a candidate for early app discovery because it is recurring and currently document-heavy.

### Coach And Lecturer Workflow

- IDEA-COACH-001: Coaches and lecturers should eventually have a personal calendar.
- IDEA-COACH-002: Coaches and lecturers should eventually be able to accept or decline assigned work.
- IDEA-COACH-003: Coaches and lecturers should eventually see previous work and basic statistics.
- IDEA-COACH-004: Staff may also be coaches or lecturers, so the role model must allow one person to hold multiple roles.
- IDEA-COACH-005: Staff should be able to release seminar opportunities so coaches or lecturers can indicate interest.

### Participant App Track

- IDEA-PAPP-001: Participants may eventually receive a separate app.
- IDEA-PAPP-002: The participant app may include onboarding content.
- IDEA-PAPP-003: The participant app may include content about life in Germany.
- IDEA-PAPP-004: The participant app may include German as a foreign language content.
- IDEA-PAPP-005: The participant app should be treated as a later separate project track, not as part of the initial administration system.

### Website-To-App Data Flow

- IDEA-FLOW-001: The public website may later submit limited company inquiries, seminar interests, or contact requests into the backend.
- IDEA-FLOW-002: Website-submitted data should enter a review queue before becoming operational app data.
- IDEA-FLOW-003: The app should be the authoritative place for staff to create, edit, approve, and archive operational records.
- IDEA-FLOW-004: Public website forms should not expose internal app data or management capabilities.

## Initial Non-Functional Requirements

- NFR-001: The system must use its own independent database.
- NFR-002: Website and app clients must access operational data through a backend API, not directly through the database.
- NFR-003: The system must minimize personal data and define retention/deletion rules before production use.
- NFR-004: The system must support backup and restore before storing operational data.
- NFR-005: The system must record important operational actions in an audit-friendly way.
- NFR-006: Integrations such as email, Hermes Agent, AI matching, and routing APIs must be evaluated for privacy, security, cost, and operational reliability before adoption.
- NFR-007: The system must define audit requirements for generated documents, outbound emails, feedback submissions, match recommendations, and staff overrides.

## Suggested Sequencing

1. Website prototype slice: modern seminar-focused website for 2026-07-01, without real database/login.
2. First app discovery slice: seminars, offers, company records, and company-contract workflow.
3. First internal-admin app slice: login, internal staff roles, companies, contacts, seminars, offers, and company contracts.
4. High-pain automation slice: participant creation, measure/course/seminar booking, internship/company booking, and one-button document package generation.
5. Matching slice: participants/skilled workers, skills, job postings, and score-based matching without AI.
6. Coach/lecturer slice: released seminar opportunities, interest, staff selection, calendars, accept/decline, and statistics.
7. Company portal slice: company history, orders, trainings, coaches, and feedback.
8. Later evaluation: email sending, feedback links, commute-time calculation, AI-assisted matching, Hermes Agent automation, and participant app.

## Coverage Check

Checked against the current chat and `PROJECT_LOG.md` on 2026-06-16.

Covered:

- Subdomain and independent system direction are captured in project memory and ADR 0001.
- No chatbot on the new website is captured in project memory and the 2026-07-01 prototype scope.
- Own independent database, login, backend API, roles, companies, seminars, coaches, participants or skilled workers, job postings, matching, document generation, email sending, route calculation, company feedback, and Hermes Agent evaluation are captured here.
- Participant creation, booking into measures/courses/seminars, internship/company booking, one-button document package generation, coach/lecturer calendars, accept/decline, statistics, company history, and later participant-app ideas are captured here.
- The 2026-07-01 prototype remains intentionally database-free and outside this backlog's implementation scope.

Needs later discovery:

- The old Sophisto-like system's relevant workflows still need direct review or stakeholder explanation.
- The first app slice is tentatively seminar/offers/company-contract focused, but the participant/document-package workflow may become the first high-pain internal automation slice after stakeholder alignment.
- The required document templates, role model, skill taxonomy, email setup, routing provider, and feedback security model are still open.

## Requirements Intake Prompts For Next Discovery

Use these questions before converting this backlog into implementation stories:

- Who creates each record type: internal staff, coach, company contact, participant, or an import?
- Which records are allowed to come from the public website, and which must only be created inside the authenticated app?
- What are the minimum fields for companies, contacts, job postings, participants, seminars, coaches, and matches?
- Which old administration workflows are painful today and should be improved first instead of merely copied?
- What is the first valuable workflow that could be demoed with fake data after the website prototype?
- Which data is sensitive enough to require stricter permissions, audit logs, or deletion rules from day one?
- Which exact documents belong to the participant/company document package, and in which order should they be merged?
- Which document steps must remain editable in Word, and which can be generated directly as PDF?
- Which company-facing history should be visible first: orders, trainings, coaches, offers, contracts, or feedback?
- Which coach/lecturer statistics are actually useful: number of assignments, hours, topics, ratings, revenue, or availability?

## Open Questions

- Which exact document types are needed first beyond offers and company contracts: participant agreements, company agreements, seminar offers, internship packages, or placement documents?
- Which email provider or mailbox should be used for outbound sending?
- Should company feedback links be anonymous, token-based, or account-based?
- Which routing provider would be acceptable from a DSGVO, cost, and reliability perspective?
- Which skills taxonomy should be used for hard skills and soft skills?
- Should skills be maintained as dropdowns, tags, free text, or a hybrid?
- What score scale should matching use: 0-100, 1-5, percentage, traffic-light plus score, or another model?
- Which operational workflow should be implemented first after the 2026-07-01 website prototype: seminar offers/contracts or participant booking/document package?
