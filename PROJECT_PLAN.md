# Project Plan

Last updated: 2026-08-25

## Vision

Build a professional digital presence for Firmendingsbums, starting with a public website and growing into an independent web-based administration system with its own login, backend API, and database.

## Current State

- Workflow model: hybrid Scrum/Kanban for multi-day delivery
- Current phase, sprint, milestone, board status, or release: public website
  stabilization plus isolated authenticated-portal foundation
- Current status: yellow for production and green for the completed technical-
  readiness scope. Source commit `ea276b9` is pushed to `origin/main` and
  contains the verified public website, accepted same-origin pilot portal and
  completed encrypted external backup/restore rehearsal. The current full local
  suite passes 305 tests with 14 expected opt-in Staging skips, all 14
  isolated PostgreSQL paths passed, and BA-01 through BA-17 are accepted in a
  real browser. The local runner is stopped and its ephemeral context removed.
  No persistent Competence-Hub backend/worker service, real account, real data
  or production deployment exists yet.
- Main blocker: the former 2026-09-25 production deadline is retired. Manuel's
  current planning assumption is a first small controlled start only after his
  return in mid-October 2026; the exact date remains open. Runtime services,
  App-DNS, SMTP delivery, production backup scheduling/alerting, legal website
  approval, named-user onboarding and production Go/No-Go remain open. The
  software and external-restore rehearsals are proven; operational activation
  and organizational approval are the critical path.
- Next decision needed: after the EDV response expected no earlier than
  2026-09-14, confirm the exact post-vacation pilot date and close app hostname,
  SMTP/sender, production timer/alert ownership, Legal, onboarding and Go/No-Go
  gates. Productive data remains blocked until all production gates close.

## Scope

In scope:

- Public website as the first deliverable.
- Competence Hub presentation for companies and private customers, including
  Mindforge Life Coaching and Businesscoaching.
- B2B-first communication for company seminars, personnel needs discovery, qualification, and placement.
- Surprise website prototype for 2026-07-01, because leadership does not yet know that the website is being prepared and the actual project start is 2026-07-01.
- Handover-ready website operation so another Informatiker can understand, maintain, build, and deploy the website if Manuel is no longer the active technical owner.
- Future editing workflow for a non-technical colleague to maintain companies, coaches, and job postings without using GitHub or development tooling.
- A later independent web-based administration system with login, backend API, and own database.
- A protected portal with internal user provisioning, multi-role authorization,
  company and Coach administration, scoped feedback and role-aware statistics.
- A future-system ideas backlog covering document generation, offers, contracts, job postings, matching, commute calculations, company feedback, email sending, and possible automation integrations.
- Project-local working structure for requirements, architecture, decisions, assets, and implementation.
- Project memory using CodexSkills starter files.
- Skill feedback collection during the project.
- Future-ready space for a webapp that can manage companies, seminars, coaches, participants, and job postings.
- Coach profile subpages, starting with Christian Galvano, using approved professional content and privacy-aware publication.

Out of scope:

- Copying full CodexSkills folders into this project by default.
- Production deployment, analytics, payments, real accounts or customer data
  handling until separately scoped and approved. Internal authentication is
  currently limited to local and synthetic staging foundation work.
- Final brand, copy, and legal text until content sources are provided or approved.
- Chatbot integration on the new website.
- Direct reuse of the parent company's existing administration database.
- Real login, database, or CRUD workflows in the 2026-07-01 prototype.
- Non-technical live editing workflow for the colleague until the CMS/webapp/API direction is selected.

## Stakeholders

- Product owner / decision owner: Manuel
- Technical owner: Manuel with Codex support
- Users or affected groups: companies, private coaching customers, internal staff, coaches, participants, and company contacts
- External stakeholders: executive stakeholders for 2026-07-01 presentation; EDV for hosting/subdomain/database coordination

## Roadmap Or Work Plan

- Now: review and stabilize the professional, mobile-first website revision
  created directly after the 2026-07-23 MVP deadline.
- Now: validate the new topic-based navigation and role-oriented login preview with Manuel; no real authentication belongs in the public website slice.
- Now: use `docs/assets/designstyle.md` as the shared visual acceptance basis for website corrections and later portal/app work.
- Now: use `CHATGPT_PROJECT_BRIEF.md` and `docs/assets/designstyle.md` to review
  the current frontend with stakeholders and the other KI.
- Now: review the reusable Connected Page Hero on `/leistungen`,
  `/unternehmen`, `/businesscoaching`, and `/mindforge`; decide whether the
  smaller Living-Hub pattern should later extend to coaches and contact after
  the Priority A content inventory.
- Next: approve and publish the new coach content only after wording, current availability, image rights, and publication consent are confirmed.
- In parallel: continue the isolated backend pilot on the occupied Chatbot VPS.
  System maintenance, firewall verification and the PostgreSQL staging
  bootstrap are complete. Resolve the encrypted off-server backup, application
  runtime, migration and privacy gates without altering the Chatbot service or
  its data.
- In parallel: build the independent web system in small approved slices. The
  database and internal session foundation exist; login creation, portal UI and
  first CRUD workflows follow only after their own quality gates.
- Before live handover: decide whether content maintenance stays developer-led
  in Astro, uses Astro plus CMS/API, or is fed by the later webapp. WordPress
  remains excluded.
- Before real-site visual production: remind Manuel to request the original seminar illustrations and approved logo exports from the media designer; do not extract production assets from the PDF.
- Future: evaluate document package automation, email sending, structured or AI-assisted matching, commute-time calculation, company feedback links, coach/lecturer workflows, company portal views, participant app, and Hermes Agent automation as separate implementation slices.

## Workstream: Hosting, Deployment & Backend Foundation

Status: system maintenance, firewall verification and isolated PostgreSQL 16
staging bootstrap completed on 2026-08-07. Local synthetic dump/restore is
verified. Off-server backup, application runtime, privacy and production
deployment gates remain.

### Confirmed Boundaries

- The IONOS webspace is the production destination for static files and PHP.
  It cannot run a permanent Node.js or Python backend.
- Both `competencehub.donner-partner.de` and
  `competence-hub.donner-partner.de` already point to that webspace and are
  covered by the existing wildcard TLS certificate.
- The IONOS MySQL database is reachable only from the IONOS webspace. It is
  therefore not a database option for a backend hosted on the separate VPS.
- The existing VPS is not blank. It already runs the Donner + Partner Chatbot
  with FastAPI, systemd services and scheduled crawling. Competence Hub must
  not share its application, credentials, database or service account.
- GitHub Pages remains a manually triggered `noindex` review environment. A
  normal push must not publish the website.
- Manuel has approved the existing VPS as a candidate, the read-only inventory
  and, in principle, future Competence-Hub company/personal data processing.
  He owns server patching, monitoring, backups and incident response.
- Thomas Roß, EDV-Leiter, is the production approval owner.
- `competencehub.donner-partner.de` is the confirmed canonical domain; the
  hyphenated variant should redirect permanently.
- Lars Donner is the confirmed legal contact. The concrete operating company,
  contract/invoice details and final Impressum are still pending.
- Janay Rappelt owns `competencehub@donner-partner.de`; the response-time and
  absence-cover process still need a small operating rule.
- The inventory showed sufficient pilot capacity. System updates/reboot and
  firewall/Fail2ban verification are complete. PostgreSQL 16.14 is localhost-
  only with separate owner, migrator and app roles; the remaining operational
  blocker is a verified encrypted off-server backup before real data.

### Provisional Direction

1. Publish the Astro website as an independent static artifact on IONOS after
   legal, content, contact-process and deployment approval.
2. Treat the existing VPS as the approved staging candidate for the later
   backend and its private database; no real data is permitted yet.
3. Patching, reboot, firewall verification, least-privilege database roles and
   local restore rehearsal are complete. Close off-server backup, monitoring
   and successor-access gates before production use.
4. Continue isolation through a dedicated system user, directories, process,
   configuration, logs, backup jobs and app/API subdomains. Database roles are
   already separated from the Chatbot.
5. Keep PHP plus IONOS MySQL as an alternative only if the project deliberately
   chooses a separate PHP stack; do not adopt it merely because MySQL exists.

See `docs/architecture/hosting-runtime-decision-2026-08-06.md` for the option
comparison, target topology, decision owners and deployment gates.
See `docs/architecture/vps-read-only-inventory-2026-08-06.md` for measured
capacity and findings, and `docs/architecture/versioning-and-operations-plan.md`
for Git, release, backup and restore responsibilities.

### Next Blocks

1. **Remaining ownership gate:** confirm the exact legal operating company when
   the Impressum/contract details arrive and define response time plus absence
   cover for the Janay Rappelt-owned public mailbox.
2. **Operational gate:** validate the encrypted Wuerzburg off-server backup
   target and restore from that exact external copy before real data.
3. **Backend integration:** PostgreSQL staging, the B2B-first core schema and
   Auth/session model are selected. Runtime configuration and database
   lifecycle/readiness are complete locally. Next prove the repository/API
   against isolated Staging before login code or API deployment.
4. **Static production readiness:** set the canonical Astro `site`, prepare the
   domain redirect, security/cache headers, error pages and an SFTP deployment
   plus rollback runbook. Deployment still requires separate approval.
5. **First backend slice:** migrations `0001`/`0002` are applied and verified;
   the local session repository plus current-session/logout API is implemented.
   Keep external logins, contracts and feedback in later slices.

## Workstream: Authenticated Portal Core

Status: Product-Owner workbook v0.2 evaluated on 2026-08-13. Domain model,
schema specification, portal information architecture, RBAC matrix and
migrations `0001`/`0002` are versioned and applied to isolated staging. The
local FastAPI slice can resolve and revoke internal MFA sessions through a
PostgreSQL repository. The local runtime factory validates external config,
owns the async engine lifecycle and reports database-backed readiness. No login
creation, real account, Staging connection or deployment exists.

### Confirmed Phase-1 Core

- portal users with multiple roles
- companies and multiple company contacts
- Coaches with canonical topics and optional service relations
- services
- B2B coaching requests with topics, services and one internal responsibility
- append-oriented audit events
- active working roles: Admin, Intern, Coach and Firmenkontakt; participant is
  deferred
- server-side deny-by-default authorization and restricted own/assigned scopes

### Provisional

- request status values may be stored as draft data, but transitions and
  automation are not final
- Coach/service relation is optional until its maintenance rule is confirmed
- company-contact/portal-user and Coach/portal-user links are optional bridges
  until their external account invitation and identity flows are approved
- role codes are working identifiers pending formal naming confirmation

### Deferred

- orders, appointments, documents, feedback tables and reporting formulas
- B2C/Mindforge accounts and participants
- contracts, invoices, file storage, calendar, push, offline data and AI
  matching

### Portal-Core Next Slices

1. Completed 2026-08-13: apply and transaction-test `0001_portal_core.sql` on
   isolated staging with synthetic data and the rollback-only smoke test.
2. Completed 2026-08-13: ADR 0003 and the internal-auth acceptance criteria
   were explicitly approved by Manuel.
3. Completed 2026-08-13: local security primitives, API contract, FastAPI health
   scaffold and synthetic tests are prepared; migration `0002` is applied and
   verified on isolated staging with no remaining test data.
4. Completed 2026-08-13: version the complete portal/auth/migration state in
   feature commit `8feb2c8` and project-status commit `1205b28`.
5. Completed locally 2026-08-13: implement the PostgreSQL session repository
   plus protected current-session/logout endpoints with synthetic tests.
6. Completed locally 2026-08-14: wire validated external runtime configuration,
   async database lifecycle and database-backed readiness without a secret
   file or deployment.
7. Completed 2026-08-14: prove the session repository/API against isolated
   Staging with synthetic rows, full cleanup and unchanged service health.
8. Completed locally 2026-08-14: review and harden the session/runtime slice;
   no high or critical finding remains in scope and 61 local tests pass.
9. Completed 2026-08-14: implement and prove first-factor login plus
   account/network-peer rate limiting locally and on isolated Staging; the
   focused review has no open high or critical finding.
10. Completed 2026-08-14: prove migration `0004`, transactional Outbox and
    persistent idempotency on isolated Staging with rollback smoke, 13/13
    synthetic paths, zero residue, protected pre/post dumps and unchanged
    service/network health. Next add fail-closed local runtime/worker
    configuration before building the minimal portal shell.
   Janay's captured workflow informs request/matching design; its remaining
   transition, legal, privacy and finance gates must be approved before
   automation.

See `docs/architecture/portal-domain-model-v0.1.md`,
`docs/architecture/portal-schema-spec-v0.1.md`,
`docs/requirements/portal-rbac-matrix-v0.1.md`,
`docs/requirements/portal-information-architecture-v0.1.md` and
`docs/requirements/portal-open-gates-v0.1.md`.

## Workstream: SEO, GEO & First-Party Authority

Status: Phases 1 through 3 completed as planning drafts on 2026-09-04;
stakeholder ownership, taxonomy, commercial and boundary decisions are next.
No new guide pages, content implementation, publication, or deployment is
authorized by this workstream yet.

### Objective And Relationship To The Frontend

- Strengthen classical SEO and add GEO so Competence Hub becomes easier for
  search engines and AI-supported answer systems to understand, retrieve, and
  cite.
- Build authority from approved first-party expertise, concrete use cases, and
  traceable evidence instead of generic or mass-produced content.
- Keep the Living Hub/frontend workstream and this content/GEO workstream
  separate but connected. The frontend defines presentation and interaction;
  this workstream defines audience fit, content substance, evidence, and
  findability.
- Preserve the Competence Hub journey:
  `Anliegen -> Klärung -> passende Expertise -> passendes Format -> nächster Schritt`.
- GEO complements classical SEO; it does not replace technical SEO, semantic
  HTML, clear titles and descriptions, internal links, understandable URLs,
  performance, or mobile usability.

### Guardrails

- Do not create new guide or advice pages before the inventory and evidence
  phases are complete and sufficient original substance is approved.
- Do not invent expert quotations, cases, customer references, statistics,
  outcomes, or other authority signals.
- Do not open or use private raw sources. `Quellen/`, `.env`, `.tmp/`, secrets,
  private coach/customer data, and other sensitive data remain excluded.
- Store no private raw data in the Content-Evidence Matrix.
- Treat the GEO-video figures of roughly 30-40% visibility improvement and
  roughly 500-2,000 words only as research orientation. They are not promises,
  targets, acceptance criteria, or fixed content-length rules.
- Publication requires factual, editorial, privacy, rights, and stakeholder
  approval where applicable.

### Planned Sequence And Deliverables

1. **Phase 1 - Content Inventory**
   - Inventory the existing core pages without rewriting them.
   - For every page record route, primary audience, concrete use case/pain
     point, central user question, relevant expertise, available first-party
     information, current CTA, content owner if known, and review status.
   - Mark mixed audiences, redundancies, unsupported claims, unclear CTAs, and
     missing evidence.
   - Start with `/`, `/unternehmen`, `/leistungen`, `/businesscoaching`, and
     `/mindforge`.
2. **Phase 2 - Content-Evidence Matrix**
   - Add relevant service, "Why Competence Hub?", approved primary
     information, expert quote, case/practical experience, verified statistic,
     external primary source, approval status, CTA, and last subject-matter
     review.
   - Distinguish `available`, `needs verification`, `needs approval`, and
     `missing`; absence must not be filled with assumptions.
   - Prepare standardized expert/content interviews, but publish no interview
     result before explicit approval.
3. **Phase 3 - Core Page Content Plan**
   - Use the completed inventories to plan focused improvements for the five
     priority routes.
   - Define a direct answer/value proposition, audience and situation, typical
     triggers, solution path, relevant expertise, evidence, limitations, and
     next step for each route.
   - Keep the content scannable and compatible with the Living Hub rather than
     increasing text volume for its own sake.
4. **Phase 4 - Approved Expertise Components**
   - Plan reusable `Expert Insight`, `Aus der Praxis`, `Zahlen & Fakten`,
     `Für wen passt das?`, and `Wann ist ein anderer Weg sinnvoll?`
     components.
   - Implement them only after evidence, permissions, design fit, and
     accessibility are approved.
5. **Phase 5 - Knowledge Content Gate**
   - Consider new knowledge content only when it contains approved original
     expertise, a real expert perspective, a concrete case analysis, own data,
     or a valuable synthesis from reliable primary sources.
   - Do not create pages merely to increase page count or target keywords.
6. **Phase 6 - Measurement And Iteration**
   - After a separately approved publication, evaluate classical search data,
     a stable set of realistic AI-search questions, source mentions, content
     gaps, contact paths, and subject-matter feedback.
   - Treat observations as learning signals, not as guarantees of visibility.

Completed baseline artifacts:

- `docs/content/priority-a-content-inventory-2026-09-04.md`
- `docs/content/priority-a-content-evidence-matrix-2026-09-04.md`
- `docs/content/priority-a-core-page-content-plan-2026-09-04.md`
- `docs/content/priority-a-stakeholder-review-packet-2026-09-04.md`

The baseline confirms that `/unternehmen` contains the only currently approved
customer authority item: the bounded Concept Clean name, quotation and
communication-course path. Other current offer descriptions remain first-party
information that needs named editorial, subject-matter or commercial review;
they are not silently promoted to evidence.

### Priority A Inventory Baseline

The following entries are planning hypotheses from the approved project
positioning. Phase 1 must verify them against the current public page content
before any copy change.

| Route | Primary audience | Concrete use case to verify | Relevant expertise to verify | Existing first-party basis to inventory | CTA to verify |
| --- | --- | --- | --- | --- | --- |
| `/` | Companies first; private customers as a distinct path | Understand the Hub and find the right route from an initial concern | Curated matching of concern, expertise, and format | Existing Competence Hub positioning and journey; no quote, case, or number assumed | Discuss the need / choose the relevant path |
| `/unternehmen` | Company decision-makers, HR, and leaders | Find support for a concrete organizational, leadership, team, recruiting, or development need | Coaching for companies, leadership/team development, recruiting and personnel development where approved | Existing company-facing process and offer information; evidence and approvals still to inventory | Discuss the company need |
| `/leistungen` | Prospective customers comparing suitable support formats | Determine which service or format fits the situation | Approved coaching, workshop, talk, assessment, and related formats | Existing service and format descriptions; factual support and overlap still to inventory | View a relevant offer or request orientation |
| `/businesscoaching` | Companies, leaders, and teams | Address a concrete leadership, collaboration, or professional-development situation | Approved Businesscoaching and relevant coach expertise | Existing Businesscoaching content and approved profile information; quotes/cases/statistics not assumed | Request an initial discussion |
| `/mindforge` | Private customers; company personnel-development use cases only where clearly separated | Seek Life Coaching for resilience, mindset, orientation, or personal development | Mindforge Life Coaching and approved additional qualifications | Existing Mindforge positioning and process; evidence, boundaries, and approvals still to inventory | Choose the private/company path and request an initial discussion |

### Priority After The Baseline

- Priority B: `/coaches`, approved coach profiles, recruiting and personnel
  development, assessment center, psychological consultation/prevention,
  supervision, workshops/talks, and `/lifecoaching`.
- Priority C: guide content, case studies, and own research only after the
  Knowledge Content Gate is met.

## Workstream: Customer Journey, Feedback & Trust

Status: internal workflow input captured on 2026-08-14; implementation remains
deferred. The public website may explain the future path, but no questionnaire,
contract workflow, feedback collection or testimonial publication is
authorized in the current static frontend slice.

### Objective And Workstream Boundaries

- Make the path from an initial need to a suitable Coach and completed
  engagement understandable for customers.
- Keep three connected responsibilities separate:
  - the Living-Hub frontend explains orientation and next steps;
  - the later webapp handles authenticated workflows and status data;
  - the SEO/GEO workstream governs approved first-party evidence and public
    customer voices.
- Do not simulate completed transactions, contracts, accounts, feedback or
  customer references in the static website.
- Use `docs/requirements/janay-request-workflow-feedback-2026-08-14.md` as the
  current operational input. Its state model remains proposed until legal,
  privacy, finance and transition gates are approved.

### Planned Customer Path

1. **Need discovery**
   - Explain typical starting situations and offer a personal first contact.
   - Evaluate a structured questionnaire only after purpose, data minimization,
     privacy notice, retention, ownership and secure processing are defined.
2. **Matching and Coach selection**
   - Connect needs and topic areas to one or more suitable Coach profiles.
   - Support two or three parallel availability checks and a shortlist without
     treating a contacted Coach as assigned.
   - Do not disclose customer identity during the initial availability check;
     record the later approved disclosure separately.
   - Keep overlapping expertise as a many-to-many relation; do not promise an
     automated or AI-based recommendation before its rules are approved.
3. **Inquiry and clarification**
   - Capture scope, target group, timing and preferred format through an
     approved contact process.
   - Janay Rappelt owns the mailbox; define response expectations, absence
     cover and internal handoff.
4. **Offer and contract**
   - Plan offer approval, contract generation, versioning, signatures and
     auditability as an authenticated webapp/backend slice.
   - Keep conditional Coach capacity, sent offer and binding order as separate
     states. The legally valid acceptance channel is still open.
   - No contract data belongs in the public Astro frontend.
5. **Delivery and coordination**
   - Later expose agreed appointments, responsible contacts and relevant
     documents according to role and authorization.
6. **Company feedback**
   - Later provide a role-protected feedback path for company contacts.
   - Competence Hub owns the feedback request; project closure also depends on
     the approved invoice/payment source of truth.
   - Define questions, purpose, access, retention, moderation and escalation
     before collecting personal or performance-related data.
7. **Customer voices and reviews**
   - Treat testimonials, reviews and case studies as first-party evidence only
     after source, context, consent, wording, attribution or anonymization and
     publication rights are documented in the Content-Evidence Matrix.
   - Never invent, silently rewrite or publish identifiable feedback without
     approval.

### First Planning Deliverables

- A service blueprint showing customer-visible steps and internal ownership.
- A privacy-aware questionnaire decision brief, not an implemented form.
- Status and role definitions for inquiry, matching, offer, contract, delivery
  and feedback.
- A customer-feedback and testimonial approval workflow connected to
  `PROJECT_PLAN_GEO_FIRST_PARTY_CONTENT.md`.
- Approval of states, transitions, customer-identity disclosure, legal
  acceptance, finance source of truth and closure evidence.

## Workstream: PWA & Mobile Distribution

Status: proposed and deferred. This workstream records the preferred future
distribution direction only. No PWA, native app, store integration, dependency,
server change or deployment is authorized by it.

### Architecture Boundaries

- The public Astro website remains a separate static frontend.
- The later authenticated client lives in `apps/webapp` and is planned
  mobile-first and PWA-ready.
- Webapp/PWA clients use the protected backend API; neither the website nor a
  PWA may connect directly to PostgreSQL.
- PWA-first is the preferred first installable mobile direction. App stores are
  not an initial gate; native Android/iOS clients remain optional and require a
  demonstrated need plus a new distribution review.
- An installable PWA is not synonymous with offline storage. Authenticated data
  defaults to `NO_CACHE` until an explicit privacy and security decision
  permits a narrower classification.
- Push is a later optional workstream and must not expose sensitive content by
  default.

### Planned Sequence

1. **Webapp core:** authentication, server-side authorization, multiple roles,
   auditability and the first approved portal workflow with synthetic data.
2. **PWA readiness:** mobile-first UI, touch operation, stable routes/deep
   links and a frontend architecture that does not require later rework.
3. **Installable PWA:** only after a stable webapp core; add manifest, icons,
   display settings, HTTPS verification and platform-specific install guidance
   as a separately approved slice.
4. **Cache/offline decision:** classify `PUBLIC_STATIC`,
   `AUTHENTICATED_NON_SENSITIVE`, `PERSONAL_DATA`,
   `CONFIDENTIAL_DOCUMENT` and `NO_CACHE` before any Service Worker caches
   authenticated content.
5. **Push only with a use case:** define purpose, consent, content boundary,
   revocation and platform support before implementation.
6. **Native-app evaluation:** only when real requirements cannot be met
   reasonably by Web/PWA; recheck current Android and Apple distribution rules
   before selecting technology or a release path.

### Open Decisions

- Webapp frontend stack and the exact PWA-readiness acceptance criteria.
- Session/token model, secure client storage, logout/session expiry, device
  loss, multi-device behavior, CSRF/XSS protection and possible MFA.
- Supported platform/browser baseline and owner of installation guidance.
- Whether any authenticated data may ever be cached, for which purpose and
  under which retention/deletion controls.
- Whether a concrete push or native-device capability creates proven value.

See `docs/architecture/pwa-app-distribution-strategy-2026-08-11.md` for the
full planning rationale, distribution constraints, security boundaries and
phase model.

## Timeline And Budget Signals

- Target dates: website MVP completed by 2026-07-23; technical readiness is
  green for the 2026-08-28 scope. The former controlled-production target of
  2026-09-25 is retired. The current planning window for a first small pilot is
  the second half of October 2026 after Manuel's return; the exact date requires
  EDV, Legal, onboarding and Go/No-Go confirmation.
- Budget or effort assumption: unknown
- Confidence: medium-high for the 2026-08-28 technical-readiness checkpoint.
  Production confidence is medium for a post-vacation October pilot if EDV and
  Legal input arrive during September. The database, Auth, company/contact API,
  browser UI and external restore are proven; production operations and
  organizational gates are not.
- Risks to time or budget: App-DNS, SMTP details/sender authorization,
  runtime/worker packaging, legal operator/Impressum, production approval,
  encrypted external restore and correct-domain rollout are on the critical
  path. Janay and Thomas acceptance dates remain unscheduled.

## Risks And Blockers

- **Schedule / activation:** technical readiness is green; the former
  2026-09-25 production deadline is retired and the first small pilot is planned
  no earlier than the second half of October. Runtime, DNS, SMTP, production
  backup scheduling/alerting, account handoff and production approval remain
  open. Owner: Manuel, with Thomas Ross for production approval. Mitigation:
  keep implementation WIP small and close activation gates in order.
- **Real-data recovery:** the encrypted external-copy restore rehearsal passed.
  Before real data, enable an approved production schedule and alert route and
  retain the exact-copy restore discipline. Owner: Manuel.
- **Legal website release:** the concrete operating company, final Impressum,
  Datenschutz/AGB applicability and mailbox absence process remain open.
  Owners: Lars Donner/final company, Janay Rappelt and Thomas Ross. Mitigation:
  obtain explicit release evidence or issue a documented No-Go for production.
- **Single-operator risk:** Manuel currently owns VPS operations without a
  confirmed successor/break-glass path. Mitigation: name controlled emergency
  access and test the handoff before productive operation.
- **Co-hosting risk:** Chatbot and Competence Hub share a VPS. Mitigation:
  dedicated identity, directories, ports, logs and services plus pre/post
  health and rollback checks; no Chatbot restart as part of Hub deployment.

## Quality Gates

- **Tests:** 248 local Webapp tests pass with 14 expected opt-in Staging skips;
  14/14 isolated PostgreSQL paths passed. Re-run local suite before packaging
  and Staging suite after runtime/reverse-proxy changes.
- **Website build:** Astro must report zero diagnostics and build all expected
  routes. Current evidence: 36 checked files, 28 generated pages.
- **Browser/accessibility:** BA-01 through BA-17 are accepted, including
  desktop, 390 CSS pixels, keyboard, focus, zoom and reduced motion. Repeat the
  critical login/company path on the deployed origin.
- **Security/privacy:** no secrets or `.env*` in Git; least privilege, exact
  Origin/CSRF, MFA, no-store, minimized lists/audit and negative role tests are
  mandatory. No open high/critical finding may cross deployment.
- **Data/operations:** no real data before encrypted off-server copy, restore
  from that exact copy, retention/error ownership, monitoring and rollback are
  proven.
- **Legal/content:** final operator/Impressum, Datenschutz/AGB applicability,
  contact process and rights approvals are required for production. Archive,
  prototype and public login-preview routes must remain `noindex` or be
  removed/redirected.
- **Release:** static website and backend use separate reproducible artifacts,
  rollback points and smoke tests. GitHub Pages remains manual review only and
  does not satisfy production acceptance.

## Delivery Steering

Planning model: hybrid Scrum/Kanban for multi-day AI-assisted delivery. The
execution backlog limits current WIP; the rolling horizon preserves likely
sequencing. Items become more provisional with distance and are reconciled
after every meaningful completion, blocker or stakeholder decision.

The compact visual flow and milestone gate view is maintained in
`docs/requirements/readiness-gate-board-2026-08-28.md`. It summarizes this
plan but does not replace the evidence and decisions recorded here.

### External Dependency And Lead-Time Radar

External decisions, data, access and approvals are requested before their
dependent slice becomes current WIP. The dates below are steering thresholds,
not promises made by the named stakeholders. Review the radar at every material
checkpoint and at least weekly. A waiting item must show its owner, next chase,
latest useful date, affected work and a safe fallback.

| ID | External input / owner | Requested or schedule by | Planning target / latest useful | Early warning / escalation | Affected work and fallback | Status |
| --- | --- | --- | --- | --- | --- | --- |
| EXT-01 | App-DNS, TLS path, SMTP contract and sender routing / EDV | Requested 2026-08-21; response expected no earlier than 2026-09-14 | Earliest planning input 2026-09-14; production latest useful date follows rebaseline | Review receipt 2026-09-14; chase from 2026-09-15 and expose replacement-launch impact immediately | Blocks host-specific config and live invitations; continue full secret-free release/readiness checks and synthetic work | Waiting until 2026-09-14 |
| EXT-02 | Final contracts / Lars Donner and responsible business stakeholders | Confirm status after 2026-08-28 | Complete before named-user acceptance | Escalate if contract workflow is still unclear by 2026-09-18 | Blocks approved first-company workflow; keep pilot data synthetic | Waiting for final status |
| EXT-03 | Janay onboarding and Thomas Ross Go/No-Go appointments | Prepare September scheduling request | Target after Manuel's return in mid-October; exact date open | Confirm slots no later than 2026-10-02 or expose pilot impact | Blocks named-user acceptance and production release; retain reviewed release candidate | Planned for post-vacation pilot |
| EXT-04 | Final legal operator, Impressum and legal review | Name review slot during September | Complete before post-vacation Go/No-Go | Escalate if no review path exists by 2026-10-02 | Blocks promoted live launch; keep current legal placeholders and no promotion | Waiting |
| EXT-05 | Controlled Wuerzburg off-server backup target and access window / Manuel | Completed 2026-08-25 | Quarterly after real-data activation and before relying on changed backup/encryption behavior | Reopen on failed backup, monitor, transfer or restore | Synthetic rehearsal complete: encrypted set, monitor, guarded external copy and exact-copy restore passed; production scheduling/alerting remains G-OPS work | Done for rehearsal |
| EXT-06 | Mailbox response, absence and ownership procedure / Janay and Manuel | Clarify during September | Complete before post-vacation Go/No-Go | Escalate if no owner/cover is confirmed by 2026-10-02 | Blocks advertised contact service level; publish no unsupported response promise | Planned |

Lead-time rule: calculate `request by` from the latest useful date minus a
realistic response, rework and escalation buffer. When an acknowledgement or
target date is missed, show the schedule impact immediately and promote an
independent ready slice instead of silently waiting.

### Current Execution Backlog

Current sprint goal: keep the accepted synthetic same-origin portal reversible
and production-shaped while incorporating approved public-website feedback as
a separate bounded slice. API, database, browser acceptance, release packaging
and external-copy restore evidence are complete. SB-24 consolidates the
27.08 website feedback and SB-27 prepares two source-governed company stories.
Direct contact delivery, calendar availability and seat reservations remain
separately gated. No implementation slice is currently doing. EXT-01 remains
parallel; Content Inventory/Evidence Matrix work may proceed independently
while infrastructure and stakeholder gates are waiting.

| ID | Status | Slice | Gate / dependency | Completion evidence |
| --- | --- | --- | --- | --- |
| SB-01 | Done locally | Session repository plus current-session/logout API | ADR 0003 and migration 0002 | repository/API synthetic tests, compileall, pip check, deny-by-default review |
| SB-02 | Done locally | Runtime configuration, async engine lifecycle and honest DB readiness | no secrets in Git; invalid config must fail closed | 58 local synthetic tests, including config/lifecycle and readiness success/failure; compileall and dependency check |
| SB-03 | Done | Synthetic Staging repository/API integration | SB-02; explicit connection window; staging only | 7/7 Staging tests; active/expired/revoked/role/idle/logout/audit/readiness; zero remaining rows; four services active |
| SB-04 | Done locally | Slice security review and restart handoff | SB-03 evidence complete | no open high/critical finding; settings/role/repr/log hardening; 61 local tests; review artifact |
| SB-05 | Done | First-factor login, generic failures, pre-auth challenge and account/network-peer rate limiting | SB-04; external HMAC key; migration 0002 | 86 local tests; 11/11 Staging paths; zero cleanup; four services active; no open high/critical finding |
| SB-06 | Done locally | TOTP enrollment/verification, recovery codes and full-session rotation | SB-05; accepted ADR 0004 | 148 local tests, compileall, pip check, negative API/replay/key-separation tests and no open high/critical finding |
| SB-07 | Done | Apply migration 0003 and prove MFA against isolated Staging | ADR/migration approval; synthetic data only | migration/smoke, 12/12 MFA paths in 134.98 seconds, zero residue, protected readable pre/post dumps, migrations 0001-0003, localhost-only PostgreSQL and four active services |
| SB-08 | Done locally | Initial-admin CLI plus invitation/reset lifecycle in synthetic mode | SB-07; interactive secret entry; approved offline compromised-password source before real use | CLI, service/repository, generic public reset/invitation-accept boundaries, focused reviews and fail-closed runtime complete |
| SB-09 | Done | Transactional Auth-token outbox, persistent idempotency, Admin invitation API and migration 0004 | Accepted ADR 0005 and separate migration approval; synthetic data only | 214 local tests plus 13/13 Staging paths in 156.91 seconds; rollback smoke, zero residue, protected readable pre/post dumps, migrations 0001-0004, 24 owner tables, least-privilege role lookup, localhost-only PostgreSQL and four active services |
| SB-10 | Done | Bounded pre-commit code/security review and versioning package for SB-01 through SB-09 | SB-09 evidence complete; Manuel approved commit/push | no open high/critical finding, reviewed file scope, 214 local tests plus 13/13 Staging paths, clean dependency/compile/diff evidence, secrets and `.tmp/` excluded |
| SB-11 | Done for scope | Freeze the 2026-08-28 readiness cut line | accepted by Manuel; account addresses and E-Mail invitation channel are set; SMTP, app DNS, Wuerzburg backup evidence and acceptance dates remain parallel gates | accepted `pilot-cutline-2026-08-28.md` defines roles, fields, non-goals, acceptance, owners and backward plan |
| SB-12 | Done locally | Protected company/contact create, read and correct API with audit | Existing migration 0001; admin/internal RBAC; provisional `prospect` default | 231 local tests, compile/pip clean, bounded bodies/list, Origin/CSRF, no-store, minimized summary, no delete and opt-in Staging test prepared |
| SB-13 | Done | Prove company/contact repository and permission boundary on isolated PostgreSQL Staging | SSH tunnel; synthetic data only; existing migrations 0001-0004 | corrected rerun 14/14; real CRUD/audit, runtime DELETE/audit denials, zero residue and four active co-hosted services |
| SB-14 | Done locally and on Staging | Same-origin static pilot portal shell and vertical login/MFA/company UI | accepted ADR 0006 and SB-11; synthetic operation only | packaged client, CSRF reload rotation, accessible local UI, 241 local tests and 14/14 PostgreSQL Staging paths with zero residue/four active services |
| SB-15 | Done | Complete real-browser acceptance of the portal vertical slice | SB-14; supported Edge browser; synthetic data only | BA-01 through BA-17 passed, including Recovery/MFA/reauth retests; 248 local tests plus 14 opt-in skips, HTTPS/MFA/cookie/CSP smoke and 14/14 Staging pass; runner stopped, port 8443 free and ephemeral profile/certificate removed |
| SB-16 | Done locally | Prevent indexing of archived, prototype and public login-preview routes | website production-readiness review | `/system`, `/seminare`, `/qualifizierung`, `/login` and login subpages emit `noindex`; homepage remains indexable; Astro 36-file check and 28-page build pass |
| SB-17 | Done locally | Prepare static Website production artifact contract and initial VPS templates | canonical Website domain; no deployment approval | canonical/OG URLs, production/review robots split, Coach-driven sitemap, ZIP plus manifest/SHA-256 builder, API systemd and Nginx examples; 38-file Astro checks and both production/review builds pass; release-builder hash/cleanup test passes |
| SB-18 | Done locally | Complete invitation-by-E-Mail vertical slice and production runtime packaging | accepted ADR 0005; SMTP contract/sender remains blocked; no real delivery | configured Runtime wires Lifecycle/password policy/encrypted outbox; TLS-only authenticated SMTP adapter and one-shot worker; fragment-based invitation/reset links and Portal forms; Admin-only idempotent internal invitation; systemd service/timer examples; 274 local passes plus 14 opt-in skips, compile/pip/JS checks green |
| SB-19 | Done | Prove the complete synthetic onboarding chain and rehearse runtime packaging | SB-18; no external SMTP; isolated local capture adapter and Staging tunnel | corrected expanded harness passed 14/14 in 151.77 seconds; Admin invite -> encrypted outbox -> capture token -> password -> TOTP -> Recovery-Codes -> active session plus replay rejection; users/sessions/outbox/audit all zero afterward; Chatbot, Nginx, Fail2ban and PostgreSQL active |
| SB-20 | Done locally | Build the reproducible backend/worker release artifact and executable rehearsal runbook | SB-19; no deployment; external SMTP and App-DNS may remain placeholders | exact runtime lock, deterministic Wheel/ZIP plus internal inventory and external manifest/checksum, isolated install/fail-closed smoke, deployment-template contract, executable install/health/rollback runbook; final review enforces same-origin action links, single-recipient mail and canonical proxy redirects; 287 local passes plus 14 skips; repeated dirty builds were byte-identical and the committed clean build reported `dirty: false` with successful isolated Wheel installation |
| SB-21 | Done locally | Prepare secret-free PostgreSQL backup, retention, monitoring and external-restore rehearsal package | no production change; no real data; external Wuerzburg target may remain unavailable | encrypted daily/monthly backup, local monitor, guarded Windows pull, isolated restore check, hardened systemd/config templates and runbook; 11 focused operations tests and Bash/PowerShell syntax pass; full release gate passes 298 tests with 14 expected Staging skips, packages every required file and contains no `.env`/`.tmp` entry |
| SB-22 | Done locally | Prepare a guarded Website SFTP release, remote-backup and rollback rehearsal package | existing static release builder; no credentials in Git; no upload or deployment approval | secret-free target contract, local preparer and runbook; checksum/archive, host-key and verified remote-root guards; mandatory backup-before-replace plus smoke/rollback gates; 17 focused operations/SFTP tests, PowerShell parser, 38-file/28-page Astro build and full 304-pass/14-skip release gate green |
| SB-23 | Done | Prove encrypted external copy and isolated restore from that exact copy | D+P-controlled encrypted target, workstation-only private key, synthetic data and rehearsal approval | backup and corrected monitor green; guarded `D:` copy hash-verified; digest-pinned networkless PostgreSQL 16 restored 24 tables twice; reusable guarded script 12/12; zero container/plaintext residue; four VPS services active |
| SB-24 | Done and review deployed | Consolidate approved 27.08 public-website feedback without expanding backend scope | authorized source packet; existing content/rights rules; no direct form endpoint or calendar implementation | Mindforge now contains Coaching and Beratung; services/navigation are consolidated; Coach rail auto-runs despite pointer hover and retains manual controls; FAQ cards size independently; Mindforge exposes a fourth Assessment-Center node; spacing, desktop/390-pixel browser QA and Astro build pass; feature commit `82c192b` pushed; manual review workflow `33502638029` green; public review pages HTTP 200 and crawler-blocked |
| SB-25 | Waiting external: authenticated, assigned Webroot missing | Confirm the exact IONOS Website Webroot without changing it | EDV must repair or reassign missing SFTP home; SB-22; host key and credentials verified | password authentication and SFTP subsystem acceptance proven; server then closes because the assigned `/htdocs/projektwue` target does not exist; public DNS/TLS reach the same IONOS target but both HTTP/HTTPS names return a 403 parking page without redirects; after EDV repair collect `pwd`, complete hidden-file inventory, provider-file classification and target-contract validation; no upload or remote change occurred |
| SB-26 | Done locally | Make the static Website artifact self-contained for conservative IONOS Apache delivery | SB-17/SB-22; no remote Apache or Webroot assumption | production `.htaccess` prepares HTTPS/canonical redirects, 404 mapping and bounded security headers without HSTS; accessible noindex 404 page added; release builder uses .NET ZIP and fails unless `.htaccess`, `404.html` and `index.html` exist in source and archive; 7 focused tests and 39-file/29-page Astro build green; clean `f7afd3247c10` artifact is `dirty: false`, contains all three required root entries and has SHA-256 `8378655a120441cf5cd6c6e95709688e6ec3c000e93e2813761f07ed44f7e0a9`; no upload or deployment |
| SB-27 | Done, approved and review deployed | Add two source-governed use-case stories and the first Concept Clean customer voice to `/unternehmen` | authorized read of `Quellen/14.08.2026`; no invented claims; Manuel confirmed Concept Clean public-reference approval 2026-09-04 | illustrative leadership story visibly labelled; Concept Clean path limited to supplied facts; no logo copied; semantic ordered routes, desktop visual QA, exact 390-pixel `0 px` overflow evidence and 39-file/29-page Astro build green; GitHub Pages review run `33848941115` green; public HTTP/content/meta-robots smoke passed; Janay acceptance remains open; IONOS production and real-data use remain separate |
| SB-28 | Done locally | Complete SEO/GEO Content Inventory and first-party Evidence Matrix for the five Priority A routes | separate content workstream; repository evidence only; no private raw sources, new guide pages or invented authority signals | two versioned documents record target group, use case, expertise, first-party information, CTA, evidence/approval state, owner gaps and claim gaps for all five routes; no public copy or deployment changed |
| SB-29 | Done locally; stakeholder decisions open | Prepare the Priority A Core Page Content Plan without changing public copy | SB-28; route overlap must remain explicit | five routes now have a primary job, answer direction, evidence plan, limits, internal links, CTA, decision owner type and later verification plan; CP-01 through CP-08 remain open; no public implementation |
| SB-30 | Done locally; awaiting dispatch and replies | Prepare the early stakeholder request for CP-01 through CP-08 | SB-29; no assumption may replace a named approval | German review packet contains decision table, recommended defaults, compact answer format, E-Mail draft, review URL and return gate; no message sent automatically |

The refreshed technical-readiness block is complete from clean commit
`70e92ba`: 305 Webapp tests pass with 14 expected Staging skips, the 33-entry
release ZIP includes the restore tool and no `.env`/`.tmp`, and the Website
passes a 38-file check plus 28-page build. No implementation slice is doing;
SB-25 is waiting on a corrected IONOS SFTP start directory. Concept Clean's
name/quote publication approval is confirmed and the crawler-blocked review
deployment passed its public smoke. SB-28 completed the five-page inventory and
evidence baseline; SB-29 completed the non-public Core Page Content Plan.
Recommended next block: obtain the bounded CP-01 through CP-08 content
decisions early, beginning with page ownership, service taxonomy and commercial
review. Required inputs are named business/subject-matter approvers and the
current approved offer facts. Deliverables are an owner/review matrix and
recorded decisions. Definition of Done: every Priority A route has named
editorial and subject-matter ownership, and commercial/route-boundary questions
are approved or explicitly deferred. No direct form delivery, calendar booking,
IONOS production deployment or real-data use is authorized by this content
workstream.

WIP rule: only one implementation slice is `doing`. Organizational gates may
progress in parallel but do not silently expand the execution backlog.

### Rolling Delivery Horizon (8 Steps)

| # | Status | Confidence | Intended outcome | Gate / dependency | Planned test or evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Done | High | Publish SB-27 to the crawler-blocked review and hand it to Janay | Concept Clean name/quote and review deployment approved; no logo use | run `33848941115` green; public HTTP 200, expected stories and `noindex, nofollow, noarchive` meta verified |
| 2 | Done | High | Complete SEO/GEO Content Inventory and first-party Evidence Matrix for the five priority pages | separate content workstream; no new guide pages or invented authority signals | SB-28 records every required field and explicit evidence/owner gaps in two versioned documents |
| 3 | Done locally | High | Prepare the Priority A Core Page Content Plan without changing public copy | SB-28; resolve route intent and overlap as explicit decisions | SB-29 defines five route plans, CP-01 through CP-08 and later verification evidence |
| 4 | Waiting stakeholder; packet ready | High | Assign page owners and decide taxonomy, commercial facts and route boundaries | SB-29/SB-30; Manuel sends the prepared request to named business and subject-matter approvers | approved/deferred CP-01 through CP-08 with owner, date and evidence reference |
| 5 | Waiting external | High | Confirm the exact Website SFTP target and validate App-DNS/SMTP/contact configuration | EDV repairs SFTP home and supplies EXT-01 details; host key/credentials verified | read-only inventory, target contract, DNS/TLS preflight, exact Origin and synthetic mail evidence |
| 6 | Pending | Medium | Rehearse Website SFTP release and VPS package activation/rollback without real data | Step 5; explicit rehearsal approval; protected SFTP/VPS access | artifact hash, complete remote backup, health/readiness/header checks, synthetic outbox, Chatbot isolation and rollback evidence |
| 7 | Pending | Medium-low | Close direct contact and named-user acceptance | Steps 5-6; privacy/operations approval; EXT-03; legal progress | negative contact tests or documented fallback; E-Mail invitation, MFA, least privilege and Janay walkthrough |
| 8 | Pending | Low | Close Legal/Go-No-Go and release the narrow pilot on the confirmed replacement date | EXT-02 through EXT-06; all real-data and production gates | signed gate matrix, production smoke, backup evidence, first approved company and rollback readiness |

### Cross-Cutting Gates

- **G-DATA:** no real company or personal data before encrypted off-server copy
  to D+P-controlled storage and restore from that exact external copy.
- **G-SEC:** no slice advances to deployment with an open high or critical
  security finding; Auth changes require negative permission and secret-leakage
  tests.
- **G-OPS:** no backend deployment before dedicated runtime identity, external
  secrets, monitoring/logging, backup, rollback and Chatbot isolation evidence.
- **G-PROD:** production still requires Thomas Ross's explicit approval, final
  legal operator/Impressum, controlled domains/origins and an approved rollout.
- **G-REQ:** Janay's workflow feedback is captured. Approved status vocabulary,
  transition/actor rules, customer-identity disclosure, legal acceptance and
  finance/closure evidence still gate workflow constraints and automation, but
  do not block the Auth foundation.
- **G-CONTENT:** public Coach/topic/customer-reference changes require factual,
  qualification, portrait/logo/quotation rights and publication approval.
  Mediation remains qualification-gated. Concept Clean company-name and quote
  use are approved as of 2026-09-04; logo use remains outside that approval.
- **G-CONTACT:** replace the current local-mail-client handoff only after the
  receiving mailbox, sender/SMTP or API path, privacy text, retention, abuse
  protection, error behavior, monitoring and synthetic end-to-end delivery are
  approved and tested. Required fields must stay minimal and transparent.
- **G-CALENDAR:** Coach availability and seat reservations require an approved
  topic taxonomy, capacity/threshold rules, reservation expiry/cancellation,
  role permissions, concurrency behavior, notification ownership and privacy
  model before implementation. The proposed minimum group size of 25 is not a
  fixed business rule until confirmed.
- **G-READY-28:** the 2026-08-28 readiness checkpoint requires versioned,
  tested and rollback-ready Website/Portal packages plus an explicit matrix of
  remaining DNS, SMTP, backup, Legal, account and Go/No-Go gates. Deployment,
  real accounts and real data follow only after their separate gates.
- **G-PROD:** the former 2026-09-25 target is retired. The first small pilot is
  planned no earlier than the second half of October, with its exact date still
  open. Production still requires the canonical
  Website, separately deployed Portal, Janay's MFA-protected least-privilege
  account, a verified external restore and successful first approved company
  plus contact. A database-only or UI-only state is not sufficient.

### Project Backlog Beyond The Horizon

- Companies and contacts, then Coaches/topics/services administration.
- Coaching-request CRUD, Coach shortlist/capacity holds and only afterward the
  approved transition workflow.
- Company/Coach feedback, customer voices and evidence-governed statistics.
- Role-scoped dashboards and reporting formulas after Product-Owner approval.
- Contract, invoice, document and mobile/PWA slices as independent epics with
  their own privacy, security and operational gates.
- Provider-neutral Coach calendar as a later portal epic: Coaches publish a
  rolling three-month availability window with topic, format, capacity and
  status; companies may place non-binding seat reservations; staff are notified
  when an approved threshold is reached and alone may release a binding offer
  or booking. Status must never be conveyed by color alone. Begin confirmed
  appointment delivery with standards-compliant `.ics` invitations for Outlook
  and non-Outlook clients; treat direct Microsoft Graph synchronization and
  free/busy lookup as separately gated integrations. Evidence must cover role
  boundaries, concurrent reservations, expiry/cancellation/wait-list behavior,
  threshold notification, Outlook plus one non-Outlook client, stable event
  updates/cancellations, time-zone correctness and data minimization.
- SEO/GEO content inventory and evidence matrix remain a connected but separate
  public-website workstream.

Parallel organizational work: process the expected EDV response from
2026-09-14 onward, confirm contract status, complete the final legal operator/
Impressum and mailbox absence cover, schedule Janay's onboarding and secure
Thomas Ross's static/backend production Go/No-Go path. The encrypted Wuerzburg
restore rehearsal is complete; production timers and alert routing remain
disabled until their separate approval. Deployment and real-data use remain
separate gated actions.

## Restart Note

Prepared on: 2026-09-02

- Canonical `main`: `e5eb186`; accepted cutline, ADR 0006, same-origin portal,
  browser harness, clean release evidence, SB-23 restore evidence and the
  deployed SB-24 Website review are versioned.
- Evidence: 305 local tests pass with 14 expected opt-in Staging skips; all 14
  PostgreSQL Staging paths and BA-01 through BA-17 passed. Astro reports 38
  files without diagnostics and 28 built pages. The local browser runner and
  temporary VPS export are stopped/removed; the exact encrypted `D:` copy is
  retained.
- No new persistent service, account, IONOS production deployment or real data
  exists. SB-24 is available on the crawler-blocked GitHub-Pages review. The
  IONOS ED25519 host key is independently verified; continue with the
  interactive read-only SFTP inventory and do not upload or download yet.

Resume here:

1. Read `AGENTS.md`, `PROJECT_LOG.md`, this `PROJECT_PLAN.md` and
   `PROJECT_STATUS.md`.
2. Review `docs/architecture/hosting-runtime-decision-2026-08-06.md`,
   `docs/architecture/vps-read-only-inventory-2026-08-06.md`,
   `docs/architecture/versioning-and-operations-plan.md`,
   `docs/architecture/pwa-app-distribution-strategy-2026-08-11.md`,
   `docs/requirements/requirements-engineering-update-2026-08-04.md` and
   `docs/assets/designstyle.md`.
3. Check `git status --short`; `.tmp/` must remain untracked and untouched.
4. Review accepted `docs/decisions/0006-same-origin-pilot-portal-ui.md`, the
   pilot cutline and current canonical checkpoint `ea276b9`.
5. SB-15 browser acceptance, isolated Staging evidence and local runner cleanup
   are complete. Continue with the named-user, invitation, app-origin and
   acceptance-date gate matrix; do not create
   accounts, use real data or deploy without separate approval.
6. PostgreSQL staging contains the verified portal-core schema but no business
   or personal data. Do not add real data or deploy a backend without the
   separately documented production gates. A push does not imply either
   GitHub-Pages or production deployment.
## Open Questions

- How should the sub-brand be named and endorsed under Donner + Partner?
- Is there approved imagery, legal text, or final deployment configuration?
- Which parts of the old Sophisto-like administration workflow should the new app mirror first?
- Are the four active working role names Admin, Intern, Coach and
  Firmenkontakt formally final, or should display labels change before auth?
- Should the later webapp share the same backend/API, auth, design system, and deployment setup?
- Who receives successor/emergency access if Manuel is unavailable?
- Which concrete app/API subdomains should be created for staging and
  production?
- Which document templates are needed first for offers and contracts?
- Which skills taxonomy should drive matching: dropdowns, tags, free text, AI-assisted extraction, or a hybrid?
- Which email account/provider should be used for generated documents and feedback workflows?
- Which routing API would be acceptable for commute-time calculations?
- Should the first app slice after the website focus on seminar offers/company contracts or on the high-pain participant booking/document package workflow?
- Which documents belong in the participant/company document package and in what merge order?
- Which soft skills should be captured for later matching?
- Which references, examples, numbers, or quotes may be named publicly?
- Which content maintenance model should support the non-technical colleague: developer-led Astro edits, Astro plus CMS/API, WordPress, or later webapp-fed content?
- Are the workshop prices 850/680 EUR per person or per event, and do they include VAT, room, and catering?
- Is the 200 EUR talk price per participant, and is the minimum group size of 25 binding?
- For Coach availability, is 25 a minimum group size, a notification threshold
  or a format-specific capacity, and who may override it?
- How long may a non-binding seat reservation remain active, which party may
  cancel it, and when does a wait list begin?
- Which mailbox, sender identity, anti-spam mechanism, retention period and
  privacy text govern direct website contact delivery?
- Who will be long-term technical owner for GitHub, hosting, deployment, domains/subdomains, and dependency updates?
- Which access handover documentation is required before Manuel can safely transfer technical ownership?
- May the media designer's original seminar illustrations and logo exports be reused on the public website, and in which file formats will they be supplied?
- Should the project-local `new-project-starter` snapshot be intentionally refreshed from the canonical CodexSkills starter after the canonical changes are reviewed?

## Decisions

- 2026-09-01: Beratung is grouped under Mindforge together with Coaching.
  Public top-level offers are consolidated into Mindforge, Recruiting and
  Personalentwicklung, Workshops and Vortraege, plus separately qualified
  Supervision and Mediation. Life and Business Coaching address self-payers;
  Firmencoaching addresses companies.
- 2026-09-01: Direct website contact delivery is an approved target but is not
  active. The current mail-client handoff stays honestly labeled until
  G-CONTACT closes; no endpoint, mailbox delivery or personal-data processing
  is inferred from the static prototype.
- 2026-09-01: Three-month Coach availability and hotel-style seat reservations
  are captured as a later portal epic. The proposed threshold of 25 remains an
  open business rule; no booking/calendar implementation is authorized by this
  requirements decision.
- 2026-08-25: The former 2026-09-25 production deadline is retired. Plan the
  first small controlled pilot no earlier than the second half of October after
  Manuel's return; the exact date remains subject to EDV, Legal, onboarding and
  Go/No-Go evidence. Technical readiness and the encrypted external-copy
  restore rehearsal are green, but production timers and alert routing remain
  disabled pending approval.
- 2026-08-25: Provider-neutral `.ics` invitations are the preferred first
  calendar-delivery increment for Coaches. Direct Microsoft Graph/Outlook sync
  and availability lookup remain later, separately gated integrations.
- 2026-08-14: Manuel accepted ADR 0005. The local implementation uses an
  encrypted transactional outbox, HMAC-based persistent idempotency, leased
  bounded worker claims and terminal data minimization. Manuel later approved
  migration `0004` separately; it was applied and proved on isolated synthetic
  Staging with rollback smoke, 13/13 integration paths, zero residue and
  protected pre/post dumps. Providers, runtime secrets, real accounts and
  deployment remain separate approvals.
- 2026-08-14: Manuel separately approved migration `0003` for the empty VPS
  Staging database. The approval covers protected pre/post dumps, migration,
  rollback-only smoke, synthetic MFA integration, cleanup and service-health
  verification. It does not authorize real accounts/data, a persistent backend
  service, deployment, commit or push.
- 2026-08-14: Manuel accepted ADR 0004. TOTP uses PyOTP with the documented
  compatibility parameters; TOTP secrets use versioned AES-256-GCM envelopes,
  recovery codes use a separate versioned HMAC keyring, and successful MFA
  rotates into a new server-side session. This decision does not authorize
  migration 0003, Staging changes, runtime secrets, real accounts or deployment.

- 2026-08-13: After explicit approval, migration `0001` was applied to the
  empty VPS staging database. The rollback-only synthetic smoke test passed;
  all synthetic rows were removed. All 15 tables belong to
  `competence_hub_owner`, PostgreSQL remains localhost-only and the Chatbot,
  Nginx, Fail2ban and PostgreSQL services remained active. This does not
  authorize auth/backend deployment or real data.
- 2026-08-13: Manuel approved ADR 0003. The first internal Auth slice uses
  server-side opaque sessions, Argon2id, mandatory TOTP-MFA, CSRF/Origin checks,
  strict Admin privilege boundaries and external secret storage. Local
  migration/API/scaffold work with synthetic data is authorized; server change,
  deployment, mail integration and real data remain separate approvals.
- 2026-08-13: After separate approval, migration `0002` was applied to isolated
  VPS staging. The rollback-only smoke test passed; all seven Auth tables are
  empty, owned by `competence_hub_owner`, and runtime privileges match the
  contract. Pre/post dumps are protected and the Chatbot remained healthy.
- 2026-08-11: Plan the future authenticated client PWA-first after the Webapp
  core. App stores are not an initial gate; native clients remain optional.
  Offline/cache and push remain separate security decisions. No implementation
  or release is authorized by this planning decision.
- 2026-08-13: Product-Owner workbook v0.2 is the authoritative input for the
  B2B-first portal core. The RBAC matrix is largely confirmed; the request
  workflow remains a Janay practice gate. A local PostgreSQL migration and
  rollback-only synthetic smoke test were initially authorized for preparation;
  this preparation decision alone did not authorize a server change, backend
  deployment, auth implementation or real data. The later explicit staging-
  migration approval is recorded separately above.
- 2026-08-06: Lars Donner is the legal Competence-Hub contact; the concrete
  operating company, contract/invoice details and final Impressum will follow.
- 2026-08-06: Janay Rappelt owns the public
  `competencehub@donner-partner.de` mailbox.
- 2026-08-06: The existing IONOS MySQL database is provisioned and credentials
  exist, but it is not used by the VPS architecture because it is unreachable
  from the VPS. Credentials remain outside Git and project documentation.
- 2026-08-07: The approved maintenance window was moved into Manuel's Friday
  workday. Ubuntu was patched and rebooted, firewall/Fail2ban were verified,
  and PostgreSQL 16.14 staging was installed localhost-only. Separate roles and
  a synthetic local dump/restore rehearsal passed. Real data remains blocked
  until an encrypted off-server restore is proven.
- 2026-08-07: The Würzburg D+P workstation is the preferred non-cloud
  off-server backup candidate, pending encryption/access verification and an
  external-copy restore test. The future authenticated portal is confirmed to
  cover internal user/role administration, companies, Coaches, feedback and
  role-scoped statistics. Manuel will provide the initial user-rights list and
  an Excel workbook as a data-model input.
- 2026-08-06: Manuel accepted ADR 0002 and PostgreSQL 16 as the Competence-Hub
  VPS database.
- 2026-08-06: Use `competencehub.donner-partner.de` as the canonical domain and
  redirect the hyphenated variant.
- 2026-08-06: Thomas Roß, EDV-Leiter, is the production approval owner; Manuel
  is the operational VPS owner for patching, monitoring, backup and incidents.
- 2026-08-06: The existing VPS may be assessed and may in principle host a
  strictly isolated Competence-Hub backend and future company/personal data.
  Technical privacy, backup/restore, firewall and access gates still apply.
- 2026-08-06: The read-only inventory gives a Conditional Go for a small pilot
  with test data. No production data before the documented operational gates.
- 2026-08-06: GitHub is the source-code and release source, not the database or
  off-server backup destination.

- 2026-06-09: Use CodexSkills new-project starter as project memory foundation.
- 2026-06-09: Do not vendor full CodexSkills folders into this project by default; use active runtime skills and canonical CodexSkills sources.
- 2026-06-09: Prepare a structure that supports website first and webapp later.
- 2026-06-09: Treat companies as the first website audience; participants and the later platform/app are secondary paths for now.
- 2026-06-16: Prefer homepage Variant B because it was better received as the more modern direction.
- 2026-06-16: Use a subdomain under `donner-partner.de` instead of starting with a separate new domain.
- 2026-06-16: Do not place a chatbot on the new website; the existing chatbot VPS is only relevant as a possible technical resource.
- 2026-06-16: The future app must use its own independent database and must not depend on the parent company's existing administration database.
- 2026-06-16: Keep the 2026-07-01 stakeholder prototype database-free and focused on website/story validation.
- 2026-06-16: Capture document generation, job posting, matching, commute-time, feedback, email, and Hermes Agent ideas in a future-system backlog, not in the first website prototype scope.
- 2026-06-16: Initial future-system priority is seminar attention and company-facing offers/contracts; the highest internal pain point identified so far is participant/course/internship booking plus document package automation.
- 2026-06-17: Use the colleague briefing to shift prototype copy toward regional KMU, Tauberfranken/Würzburg, praxisnahe Firmenschulungen, gezielte Personalqualifizierung, and a kostenfreies Erstgespräch zur Bedarfsanalyse.
- 2026-06-17: Treat handover and maintainability as first-class website requirements: the site must be understandable to another Informatiker, and non-technical colleague workflows for companies, coaches, and job postings need a CMS/API/webapp or documented interim process.
- 2026-06-17: Future decision to document before live operation: whether website content is maintained through Astro by a technical owner, Astro with CMS/API, WordPress/other CMS, or the later webapp as content source.
- 2026-06-17: Leadership does not yet know that the website is being built; the 2026-07-01 milestone is the actual project start, so the prototype should be framed as prepared pre-work and a positive surprise.
- 2026-06-22: Use the media designer's onepager as the prototype reference for the seminar page; request original approved illustrations and logo exports when work moves to the real public website.
- 2026-06-30: Use Christian Galvano as the first real coach profile, based on the supplied seminar flyers and his public CHANGES Galvano profile; publish no flyer-derived portrait until an approved standalone image is available.
- 2026-06-30: Use the standalone Christian Galvano portrait supplied by Manuel on the coach listing and detail page; do not derive the portrait from the composed seminar flyers.
- 2026-07-13: Use `competencehub@donner-partner.de` as the public Competence Hub contact address.
- 2026-07-13: Expose `roedel.kg@donner-partner.eu` only as a local development test contact; do not include it in production builds.
- 2026-07-13: Expect data for approximately five initial coaches from the colleague during the week; publish no placeholder identities or unapproved profile details.
- 2026-07-13: Keep the separate "Für Unternehmen" route and use a reduced B2B navigation with Start, Leistungen, Für Unternehmen, Coaches, and Kontakt.
- 2026-07-16: Position Competence Hub as a curated intermediary between companies and coaches; coach quality and fit are the central public differentiators.
- 2026-07-16: Prepare Elisabeth Schwabauer and Carolin Hupp as local coach profiles without private contact data or invented portraits; require final publication approval.
- 2026-07-16: Keep ambiguous price input and interactive quizzes out of the public deadline MVP until commercial, content, privacy, and accessibility questions are resolved.
- 2026-07-16: Prepare MySQL/MariaDB-oriented placeholders and a data-model brief, but perform no server/database change before a read-only inventory and explicit approval.
- 2026-07-31: Add SEO, GEO & First-Party Authority as a separate but connected
  workstream. Begin with Content Inventory and a Content-Evidence Matrix; GEO
  complements SEO, and no new guide content or unsupported authority signal is
  permitted.
- 2026-07-31: Model Coach topics as a many-to-many relation. Use a compact
  topic filter for the current public network, avoid a permanent all-to-all
  graph, and add dedicated topic routes only when approved first-party content
  provides value beyond a filtered Coach list.
- 2026-08-04: Treat Mindforge as the central Hub umbrella for Life Coaching and Businesscoaching; remove the separate Businesscoaching Hub node while preserving the dedicated Businesscoaching page.
- 2026-08-04: Treat Mediation as a qualification-gated network topic; assign no Coach without explicit evidence and approval.
- 2026-08-04: Publish Frau Dr. Stefanie Becker's approved profile without customer references or a PDF-derived portrait; expand Herr T. Wegner-Ney toward technology, processes and change with KI only as a secondary topic.
- 2026-08-04: Use Herr/Frau honorifics consistently for visible Coach names and refer to the contact person as Frau Janay Rappelt.
- 2026-08-06: Center the homepage Living Hub between introductory copy and the
  primary actions. The central Hub links to `/ueber-uns`; the four Journey
  nodes navigate within the homepage while their detailed text links may still
  lead to relevant subpages.
- 2026-08-06: Plan need discovery, matching, inquiry, offer/contract, delivery,
  company feedback and approved customer voices as a future customer-journey
  workstream. Do not simulate these workflows in the static MVP.
