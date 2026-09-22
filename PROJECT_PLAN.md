# Project Plan

Last updated: 2026-09-22

## Vision

Build a professional digital presence for Firmendingsbums, starting with a public website and growing into an independent web-based administration system with its own login, backend API, and database.

## Current State

- Workflow model: hybrid Scrum/Kanban for multi-day delivery
- Current phase, sprint, milestone, board status, or release: time-boxed public
  Website Messe-Readiness sprint through Manuel's operative cutline on
  2026-09-25. The public frontend for the 2026-10-17 trade-fair presentation
  has priority over any further CAL-1 feature work.
- Current status: green for the public static Website and yellow for the
  separate Portal/backend production path. Migrations `0005` and `0006`, the CAL-1 domain/repository
  and the protected/public API are proven on isolated Staging with synthetic
  data. The explicit nullable Coach-profile mapping, endpoint-specific session
  role boundary, revisions, idempotency, concurrency, public projection and
  payload-free audit are verified. It builds
  on the deployed clean Website checkpoint `e6081580b0d7` and
  contains the verified public website, accepted same-origin pilot portal and
  completed encrypted external backup/restore rehearsal. The current full local
  suite passes 384 tests with 17 expected opt-in Staging skips, all 17/17
  isolated PostgreSQL paths passed, BA-01 through BA-17 are accepted and all
  26 CAL-1 browser-checklist points pass with 57/57 repeatable Edge checks. The
  local runner is stopped and its ephemeral context removed.
  No persistent Competence-Hub backend/worker service, real account, real data
  or Portal/backend production deployment exists yet.
- Primary deadline: Manuel is unavailable from 2026-09-26. By 2026-09-25 the
  Website must be locally messe-ready, reproducibly packaged, rollback-ready
  and documented so an authorized technician can operate it without Manuel.
  The stable Messe-Demostand is required on 2026-10-17. A controlled public
  live test completed early on 2026-09-22; corrections may still follow during
  the week. Thomas closed the EDV prerequisite and Manuel operated the
  controlled upload.
  Donner + Partner is the
  confirmed operator, Lars Donner the responsible person, and the central D+P
  Impressum, AGB and Datenschutz pages are the binding legal targets.
- Current critical path: freeze and hand over the now-live Website, test actual
  mailbox delivery to Janay and preserve exact source/artifact/rollback
  evidence. Manuel approved the portrait,
  supported professional profile data and publication on 22.09. EDV removed
  the temporary `index.php` diagnostic
  file and accepted `.htaccess` redirects; the public four-URL preflight now
  exposes no `phpinfo()`. Route analysis, local corrections, browser
  acceptance, read-only Webroot inventory and holiday handover are complete.
  The production gate passes 762/762 Edge checks. The SFTP tooling now protects
  resolved checklist values plus IONOS directory creation, permissions and
  entrypoint-last activation.
  App-DNS,
  SMTP, sender approval, backend
  activation, real accounts/roles/data and productive calendar offers remain
  separate gates and do not block a local handover-ready static Website.
- CAL-1 freeze: retain the committed migration/API/UI/browser work and its
  384-pass/17-skip, 17/17 Staging and 57/57 Edge evidence. Do not widen CAL-1 or
  start CAL-2 before Website Messe-Readiness closes. Native Staging UI remains a
  later separately approved gate.

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
- Donner + Partner is the confirmed operator and Lars Donner the responsible
  person. The central D+P Impressum, AGB and Datenschutz pages are the binding
  legal targets for the static Website.
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

1. **External P0 closure:** completed 22.09.; EDV removed `index.php`, accepted
   `.htaccess` redirects and the four-URL preflight exposes no `phpinfo()`.
2. **Content decision and visual Go/No-Go:** completed 22.09.; Guelcan profile,
   portrait, professional data and publication are approved. Contact-mail
   delivery remains an immediate production smoke.
3. **Clean source and artifact:** completed; source `e6081580b0d7`, 55 entries,
   SHA-256 `cc7b75c8...43da32e`.
4. **Controlled live test:** completed 22.09.; empty pre-state inventoried,
   exact artifact deployed and provider-specific directory issue corrected.
5. **Production smoke:** completed; redirects/core routes/assets/security and
   762/762 Edge checks pass. Actual mailbox delivery remains open.
6. **Holiday handover and feature freeze by 25.09.:** record exact production
   source/artifact, rollback evidence, owners and stop rules.
7. **During absence:** allow only approved content fixes or incident recovery
   through the handover; no Portal-/Backend-Aktivierung.
8. **After Messe / lower confidence:** resume native CAL-1 Staging UI and later
   CAL-2 only after the static Website release state is stable.

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
  green for the 2026-08-28 scope. The current static Website live-test target
  is 2026-09-24, followed by handover on 2026-09-25 and the Messe on
  2026-10-17. Portal onboarding remains a separate later gate.
- Budget or effort assumption: unknown
- Confidence: high for the static Website because its production release and
  browser acceptance completed on 22.09. Actual mailbox delivery remains an
  operational follow-up.
  Portal production confidence remains lower because its operational gates are
  separate.
- Risks to time or budget: unproven contact mailbox routing is the remaining
  Website operational gap. App-DNS, SMTP, runtime/worker packaging and account gates
  remain on the later Portal path.

## Risks And Blockers

- **Schedule / activation:** the controlled Website live test completed on
  22.09. Exact release content, artifact, upload, redirects and production
  browser smoke are closed; contact-mail delivery remains open.
  Runtime, DNS, SMTP, production backup scheduling/alerting, account handoff
  and production approval remain open. Owner: Manuel, with Thomas Ross for
  production approval. Mitigation: keep WIP small and close gates in order.
- **Real-data recovery:** the encrypted external-copy restore rehearsal passed.
  Before real data, enable an approved production schedule and alert route and
  retain the exact-copy restore discipline. Owner: Manuel.
- **Website release approval:** complete for the static site. Legal targets,
  Webroot, content/rights, upload authorization, redirects and production
  acceptance are evidenced. Actual mailbox delivery remains with Manuel/Janay.
- **Single-operator risk:** Manuel currently owns VPS operations. Thomas Ross
  is confirmed as technical break-glass successor, but his separate identity,
  MFA and controlled handoff still require implementation and testing.
- **Co-hosting risk:** Chatbot and Competence Hub share a VPS. Mitigation:
  dedicated identity, directories, ports, logs and services plus pre/post
  health and rollback checks; no Chatbot restart as part of Hub deployment.

## Quality Gates

- **Tests:** 384 local Webapp tests pass with 17 expected opt-in Staging skips;
  all 17/17 isolated PostgreSQL paths and migration `0005`/`0006` smoke passed.
  The focused CAL-1 API run passed 3/3. Postflight shows zero rows in all 19
  dynamic areas and four active services.
  Re-run local suite before packaging and Staging suite after backend/runtime
  changes.
- **Website build:** Astro must report zero diagnostics and build all expected
  routes. Current evidence: 36 checked files, 28 generated pages.
- **Browser/accessibility:** BA-01 through BA-17 and all 26 CAL-1 checklist
  points are accepted. The repeatable Edge gate passes 57/57 across desktop,
  390 CSS pixels, 200-percent layout, keyboard, visible focus, Escape, reduced
  motion, stale edit, role transitions, company/contact, MFA and recovery.
  Repeat the critical paths on the later deployed origin.
- **Security/privacy:** no secrets or `.env*` in Git; least privilege, exact
  Origin/CSRF, MFA, no-store, minimized lists/audit and negative role tests are
  mandatory. No open high/critical finding may cross deployment.
- **Data/operations:** no real data before encrypted off-server copy, restore
  from that exact copy, retention/error ownership, monitoring and rollback are
  proven.
- **Legal/content:** the operator and central Impressum/AGB/Datenschutz targets
  are decided; contact process and rights approvals remain required. Archive,
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
| EXT-03 | Janay onboarding and Thomas Ross Go/No-Go appointments | Request the preferred 2026-09-17 slot now; hold 2026-09-24 as fallback | Use 2026-09-17 if all preceding gates close, otherwise 2026-09-24 or a documented later date | Escalate on 2026-09-21 if neither slot is acknowledged; expose the affected pilot date | Blocks named-user acceptance and production release; retain reviewed release candidate | Dates proposed; confirmation open |
| EXT-04 | Final legal operator, Impressum and legal review | Name owner and request review path by 2026-09-18 | Confirm owner, required inputs and target date by 2026-09-24; complete before post-vacation Go/No-Go | Escalate on 2026-09-21 if no review path exists | Blocks promoted live launch; keep current legal placeholders and no promotion | Waiting; request due before vacation |
| EXT-05 | Controlled Wuerzburg off-server backup target and access window / Manuel | Completed 2026-08-25 | Quarterly after real-data activation and before relying on changed backup/encryption behavior | Reopen on failed backup, monitor, transfer or restore | Synthetic rehearsal complete: encrypted set, monitor, guarded external copy and exact-copy restore passed; production scheduling/alerting remains G-OPS work | Done for rehearsal |
| EXT-06 | Mailbox response and absence procedure / Janay | Owner confirmed 2026-09-11; no substitute currently exists | Test routing before pilot and keep the uncovered absence period explicit | Reopen when a substitute is named or before any response-time promise | Blocks only an advertised service level, not the technical pilot; publish no unsupported response promise | Known operational gap |

Lead-time rule: calculate `request by` from the latest useful date minus a
realistic response, rework and escalation buffer. When an acknowledgement or
target date is missed, show the schedule impact immediately and promote an
independent ready slice instead of silently waiting.

### Current Execution Backlog

Current sprint goal: freeze and hand over the public Website after the
successful 22.09. production release without widening the real-data or
backend-production boundary. The mailbox delivery smoke and release handover
are the only active Website items. Native Staging UI, seat
reservations and calendar delivery remain separately gated. EXT-01 and the
remaining Content owner decisions continue in parallel.

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
| SB-25 | Done read-only / EDV P0 closed | Confirm the exact IONOS Website Webroot without changing it and remove the public diagnostic | SB-22; host key and credentials verified; EDV repairs SFTP home | authenticated `pwd`/`ls -la` proved `/` as the confirmed Webroot-Chroot and only the 64-byte `index.php`; Thomas removed it on 22.09. and allowed `.htaccess` redirects; four public HTTP/HTTPS checks now return `403` without `phpinfo()`; no upload or Codex remote change occurred |
| SB-26 | Done locally | Make the static Website artifact self-contained for conservative IONOS Apache delivery | SB-17/SB-22; no remote Apache or Webroot assumption | production `.htaccess` prepares HTTPS/canonical redirects, 404 mapping and bounded security headers without HSTS; accessible noindex 404 page added; release builder uses .NET ZIP and fails unless `.htaccess`, `404.html` and `index.html` exist in source and archive; 7 focused tests and 39-file/29-page Astro build green; clean `f7afd3247c10` artifact is `dirty: false`, contains all three required root entries and has SHA-256 `8378655a120441cf5cd6c6e95709688e6ec3c000e93e2813761f07ed44f7e0a9`; no upload or deployment |
| SB-27 | Done, approved, review deployed and accepted | Add two source-governed use-case stories and the first Concept Clean customer voice to `/unternehmen` | authorized read of `Quellen/14.08.2026`; no invented claims; Manuel confirmed Concept Clean public-reference approval 2026-09-04 | illustrative leadership story visibly labelled; Concept Clean path limited to supplied facts; no logo copied; semantic ordered routes, desktop visual QA, exact 390-pixel `0 px` overflow evidence and 39-file/29-page Astro build green; GitHub Pages review run `33848941115` green; public HTTP/content/meta-robots smoke passed; Janay accepted the consolidated Website presentation on 2026-09-10; IONOS production and real-data use remain separate |
| SB-28 | Done locally | Complete SEO/GEO Content Inventory and first-party Evidence Matrix for the five Priority A routes | separate content workstream; repository evidence only; no private raw sources, new guide pages or invented authority signals | two versioned documents record target group, use case, expertise, first-party information, CTA, evidence/approval state, owner gaps and claim gaps for all five routes; no public copy or deployment changed |
| SB-29 | Done locally; first decisions processed | Prepare the Priority A Core Page Content Plan without changing public copy | SB-28; route overlap must remain explicit | five routes have a primary job, evidence plan and gates; CP-01/03/05/06 are decided, CP-02/04/07 partial and CP-08 open; only the bounded SB-40 wording update followed |
| SB-30 | Done; first return received | Prepare the early stakeholder request for CP-01 through CP-08 | SB-29; no assumption may replace a named approval | German review packet and A4 exports were completed; Manuel supplied an edited Word return on 11.09., preserved as stakeholder evidence and reconciled in SB-40 |
| SB-31 | Done, review deployed and accepted | Make approved customer feedback unmistakable and scalable on `/unternehmen` | EV-CC-001 name/quote approval plus Manuel's explicit request for visible customer logos; no additional claims | compact customer-feedback rail uses a central publication-gated data source, supplied Concept Clean logo, collaboration topic, short exact quotation and practice-path link; controls/automatic advance activate only with multiple approved entries; 40-file Astro check and 29-page build green; desktop and exact 390-pixel browser QA show one card, zero unnecessary controls and no horizontal overflow; review workflow `33852789095` and public page/logo/content smoke green; Janay accepted the consolidated Website presentation on 2026-09-10 |
| SB-32 | Done, review deployed and accepted | Correct the customer-feedback quotation-mark typography | Manuel's visual acceptance feedback; quotation text and evidence stay unchanged | opening and closing marks now sit inline beside the actual quote text with modest spacing; semantic quotation remains intact; desktop browser measurement shows 9-pixel gaps without overlap; review workflow `34479551380` green; Janay confirmed the result on 2026-09-10 |
| SB-33 | Done, review deployed and accepted | Reconcile the authorized update packets and implement the 04.09 compact Use-Case feedback | authorized 13.08, 14.08, 24.08, 27.08 and 04.09 packets; no invented claims or calendar implementation | feedback ledger records implemented/open/gated items; Use Cases sit side by side, open independently and remain collapsed initially; 1440/960/390-pixel browser QA shows no horizontal overflow; direct hash links open the matching story; public review returns HTTP 200 with `noindex`; Janay confirmed the result on 2026-09-10 |
| SB-34 | Done, review deployed and accepted | Build a no-data visual prototype for Janay's three-month Coach calendar and place-vormerkung concept | 27.08 workshop note and Janay's 10.09 request; no real availability, persistence, notification or booking | noindex prototype shows three bounded months, text-plus-color topic filters, example appointments, status-aware details and local seat simulation; 42-file Astro check and 30-page build green; browser checks at 1440/960/390 pixels prove month bounds, disabled reservation during internal review, 44-pixel mobile event targets and no horizontal overflow; review workflow `34482731102` and public route/bundle smoke green; Janay accepted the concept on 2026-09-10 |
| SB-35 | Done, review deployed and accepted | Apply Janay's first CAL-0.1 feedback while preserving the public/private boundary | authorized 10.09 feedback; only existing approved Coach profiles may be linked; no personal Coach calendar in the static Website | Coach links, planned-group-offer scope note and overlapping weekend examples implemented; requirements assign Coach self-service to authenticated CAL-1 and Janay's approval to a role-based permission; 42-file check and 30-page build plus 1440/960/390 CDP checks green; workflow `34513388689` and public noindex/profile/contact/bundle/no-write smokes green; Janay accepted the result on 2026-09-11 |
| SB-36 | Done and review deployed | Keep long Coach CTA headings and punctuation inside their layout column | shared Coach CTA; no copy or navigation change | shared columns can shrink; long German compounds hyphenate only when required; 42-file/30-page Astro build and 18 browser geometry checks across all six profiles at 1440, 960 and 390 pixels are green with zero overlap or horizontal overflow; workflow `34515246498` and public page/CSS/noindex smoke green |
| SB-37 | Done stakeholder handoff | Batch the remaining calendar decisions and define the future quality gates | CAL-0.1 accepted; no productive implementation before CAL-D01 through CAL-D08 and ADR 0007 | non-technical eight-decision handout delivered; Janay accepted every rule and the Pilot flow on 11.09.; quality plan reconciled in SB-41; Manuel accepted ADR 0007 on 11.09. |
| SB-38 | Done and review deployed | Add fail-closed internal-reference verification and correct 404 metadata before refreshing the clean Website artifact | current static source; no IONOS connection or production deployment | initial scan found the invalid `/404/` canonical; 404 now emits no canonical/OG URL; durable release gate verifies 1,137 internal references across 30 HTML files; clean `db96b9573d2a` artifact has 51 entries, required root files, no sensitive entries and SHA-256 `d322276b...c0481c17`; workflow `34577486065` and public 404/noindex/home/calendar smoke green; deployment flag false |
| SB-39 | Done decision-only | Close the currently decidable Pilot account and operations ownership | Manuel's decisions; no account creation, timer activation, secret handling or real data | Manuel remains operational Admin; Thomas Ross is the technical break-glass successor; Janay owns the mailbox without a current substitute; daily backup and monitor schedules plus 30/12 retention are accepted; concise success/incident notification is required but its delivery channel remains behind EXT-01; preferred acceptance date is 17.09. with 24.09. fallback |
| SB-40 | Done and review deployed | Reconcile the first Priority-A content return and implement only approved audience wording | edited stakeholder DOCX; no invented approval for partial or empty answers | CP-01/03/05/06 accepted; CP-02/04/07 partial and CP-08 open; Mindforge now distinguishes consultation conversations for private persons from Businesscoaching for companies across the relevant public routes; 43-file Astro check, 30-page build, 1,137-reference verification and true 390-pixel overflow checks across four affected routes are green; commit `5d126cb` pushed; workflow `34582211406` and public HTTP/content/noindex smoke green |
| SB-41 | Done decision-only | Process Janay's complete Coach-calendar decision return | authorized `Quellen/11.09.2026` calendar return; no raw private file copied | CAL-D01 through CAL-D08 and the Pilot flow are accepted; public reading, authenticated company reservations, per-offer threshold/capacity, deadlines, minimal fields, governed topics, Janay task plus E-Mail, publication checks and provider-neutral calendar delivery are documented; ADR 0007 accepted 11.09. |
| SB-42 | Done planning-only | Convert the supplied E-Mail templates into a safe automation inventory | authorized `Quellen/11.09.2026` mail-template draft; no automatic send or public claim | twelve workflow ideas are classified by event and gate; response-time, guarantee, refund, automatic reschedule, discount, newsletter and legal-acceptance claims remain blocked; transactional, marketing and legally relevant messages are explicitly separated |
| SB-43 | Done locally | Prepare a provider-neutral backup success/incident notification contract | accepted notification requirement; live channel remains behind EXT-01; no network, recipient, timer or VPS activation | bounded JSON renderer accepts only defined event/code combinations and emits fixed German action text plus stable UTC-day deduplication; 21 focused operations tests, 315 full local passes with 14 expected Staging skips, compileall and dependency checks are green; commit `58299ae`; no message was sent |
| SB-44 | Done design-only | Accept ADR 0007 and complete CAL-1 architecture, data, API and RBAC boundaries | Manuel's explicit ADR approval; no migration or implementation | revision-safe publication, separate public/private APIs, additive `calendar_reviewer`, optimistic concurrency, public projection and verification matrix documented; CAL-T01..T06 collect remaining migration decisions; no SQL, account, data, message or deployment |
| SB-45 | Done on isolated Staging | Prepare and prove additive CAL-1 migration `0005` plus rollback-only smoke | ADR 0007, CAL-T01..T06 and separate Staging approval; synthetic data only | three Calendar tables and unassigned `calendar_reviewer` applied; smoke rolled back to zero Calendar rows; 27 owner tables, migrations 0001-0005, denied runtime DDL/delete rights, protected readable 86/108-KiB pre/post dumps, localhost-only PostgreSQL and four active services verified |
| SB-46 | Done locally and on isolated Staging | Implement and prove the bounded CAL-1 domain and PostgreSQL repository | CAL-1 Domain/Repository approval; migration `0005`; no API/UI/reservation/mail/real data | normalized three-month drafts, own-Coach/Admin/reviewer scopes, idempotent create, immutable submitted revisions, optimistic locking, Coach-row serialization, half-open overlap checks, payload-free atomic audit and revision-safe publication implemented; UUID binding, authoritative DB-clock fixture and Calendar-only runner are regression-protected; 339 local passes, 15/15 native Staging paths, zero rows in 19 dynamic areas and four active services |
| SB-47 | Done locally and on isolated Staging | Add and prove explicit Coach-profile mapping plus protected/public CAL-1 APIs | proven SB-46 repository; separate migration approval; no UI/reservation/mail/roles/real data | migration `0006` plus rollback smoke, nullable canonical `/coaches/<slug>/` mapping without slug inference, unique partial index, endpoint-specific MFA session boundary, RBAC/Origin/CSRF/ETag protected API, published-only minimized public API and signed cursor; focused 3/3 and full 17/17 native Staging passes, 375 local passes/17 skips, zero residue, protected 0600 pre/post dumps, localhost-only PostgreSQL and four active services |
| SB-48 | Done locally and browser-accepted | Implement the synthetic CAL-1 Coach-/Reviewer-Portaloberflaeche | SB-47; same-origin portal; synthetic identities only; no deployment | server-derived capabilities/topics, own-Coach Draft/Edit/Submit/Withdraw/Revision, separate reviewer queue/decisions, ETag recovery, role-gated DOM cleanup, loading/error/empty states and responsive/accessibility CSS; all 26 checklist points plus 57/57 Edge checks pass; Admin fixture-state/status and topic-selection findings fixed; 384 local passes/17 skips; fixture stopped and temporary context removed |
| SB-49 | Done and pushed | Add a privacy-minimized public profile for Guelcan Elmas-Brandes | explicitly authorized source folder; Manuel approved portrait, supported professional data and publication on 22.09. | overview entry and profile route use the metadata-minimized portrait; expanded evidence-backed qualifications; 45-file Astro check, 32-page build, 1,274-reference link gate and 762 Edge checks pass; commit `4c3cb2f` pushed |
| SB-50 | Done in production | Harden the SFTP release handoff and deploy the exact static artifact | SB-49 pushed; Manuel authorized/operated release; no credentials in files or logs | source `e6081580b0d7`, SHA-256 `cc7b75c8...43da32e`, 55 entries; IONOS directory/permission recovery; HTTP/security smoke and 762/762 production Edge checks pass; reusable first-deploy/update command lists added |

The technical-readiness baseline remains complete: 384 Webapp tests pass with
17 expected Staging skips, the release ZIP includes the restore tool and no
`.env`/`.tmp`. The existing clean Website candidate passes 722 Edge checks,
31 pages and 1,233 internal references; the approved SB-49 update passes a
45-file Astro check, 32-page build, 1,274-reference verification and 762 Edge checks.
SB-25, its EDV diagnostic P0 and the static production release are closed.
Concept Clean's bounded publication approval is confirmed, SB-28 completed the
five-page inventory/evidence baseline and SB-29 completed the non-public Core
Page Content Plan. Janay accepted SB-32/SB-33 and CAL-0 on 2026-09-10.
Recommended next block: complete the short Website handover and verify that a
real test message to `competencehub@donner-partner.de` reaches Janay. Preserve
the exact production source/artifact, smoke evidence and rollback stop rules.
No CAL-1 expansion, account, role, mail automation or real-data operation
belongs to this block.

WIP rule: only one implementation slice is `doing`. Organizational gates may
progress in parallel but do not silently expand the execution backlog.

### Rolling Delivery Horizon (8 Steps)

| # | Status | Confidence | Intended outcome | Gate / dependency | Planned test or evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Done | High | Close public-domain P0 preflight | read-only inventory and EDV action | Thomas removed `index.php`; four URLs return `403` without `phpinfo()`; `.htaccess` redirects accepted |
| 2 | Done | High | Approve the new Coach profile | Manuel confirmed public name, copy, portrait rights and release timing on 22.09. | decision record plus desktop/390-px review; local build/link/762 Edge checks green |
| 3 | Done | High | Create exact clean source and release artifact | step 2 complete; commit/push and release authorized | source `e6081580b0d7`, 55-entry archive and matching SHA-256 |
| 4 | Done | High | Perform controlled IONOS live test | step 3; upload authorized; empty pre-state | exact-artifact upload, IONOS recovery and entrypoint-last activation |
| 5 | Done | High | Prove production behavior or roll back | step 4 | HTTPS/alias redirects, core routes/assets/security and 762/762 Edge checks |
| 6 | Doing | High | Freeze and hand over the Website | production outcome known | exact source/artifact, owner, smoke, rollback and stop criteria by 25.09.; mailbox delivery smoke |
| 7 | Deferred | Medium | Limit absence-period work to approved fixes and incidents | step 6 handover; authorized operator | logged change, focused retest and no backend activation |
| 8 | Deferred | Low | Resume native CAL-1 Staging UI acceptance after Messe readiness | Website stable; separate approval; synthetic only | workflow, role negatives, cleanup, zero residue and service health |

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
  use are approved as of 2026-09-04; later that day Manuel explicitly requested
  the supplied logo for the bounded customer-feedback presentation.
- **G-CONTACT:** replace the current local-mail-client handoff only after the
  receiving mailbox, sender/SMTP or API path, privacy text, retention, abuse
  protection, error behavior, monitoring and synthetic end-to-end delivery are
  approved and tested. Required fields must stay minimal and transparent.
- **G-CALENDAR:** The first productive Fachinkrement covers Coach availability,
  internal review and controlled publication. The first external delivery
  increment is provider-neutral `.ics` for a confirmed appointment and
  requires an authoritative event record, stable ID, organizer, time-zone,
  privacy, failure handling and role ownership. Evidence
  must cover Outlook plus one non-Outlook client, update/cancellation without
  duplicates, daylight-saving behavior and data minimization. Direct Graph
  synchronization is optional and separately gated. Coach availability and
  seat reservations use the accepted governed-topic, deadline, minimal-field
  and notification rules. Capacity remains separate from the configurable
  per-offer review threshold; its initial value `25` is not a minimum group
  size. Exact status transitions, concurrency, retention, deletion and abuse
  controls still require technical and privacy review.
- **G-READY-28:** the 2026-08-28 readiness checkpoint requires versioned,
  tested and rollback-ready Website/Portal packages plus an explicit matrix of
  remaining DNS, SMTP, backup, account and Go/No-Go gates. Deployment,
  real accounts and real data follow only after their separate gates.
- **G-PROD:** 2026-09-25 is the operative Manuel cutline and 2026-10-17 the
  Website Messe deadline. A static Website release may proceed independently
  of CAL-1 only after Webroot/rollback proof and Thomas's explicit
  Go/No-Go plus remote-change approval. Portal/backend production still
  requires the full account, mail, runtime, backup/alert and data gates.

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

Parallel organizational work: Thomas Ross removed the test file and approved
the redirect implementation; Manuel authorized the controlled public release.
Operator, responsible person and central Impressum, AGB and Datenschutz
targets are decided. App-DNS, SMTP, sender/routing, mailbox cover, onboarding,
backend activation and production timers remain separate and may be completed
by authorized owners during Manuel's absence. Portal/backend deployment and
real-data use remain separately gated actions.

## Restart Note

Prepared on: 2026-09-22

- Base checkpoint for this slice: `4797f79`; CAL-1 migration/API/UI and browser
  work remains in the current uncommitted local worktree.
- Evidence: 384 local tests pass with 17 expected opt-in Staging skips; all
  17/17 PostgreSQL paths, migrations `0005`/`0006`, BA-01 through BA-17 and all
  26 CAL-1 browser-checklist points passed. The repeatable Edge gate passes
  57/57 checks; postflight found zero rows in 19 dynamic areas and four active
  services. The local browser fixture, browser contexts and temporary
  certificates are stopped/removed; the exact encrypted `D:` copy is retained.
- No new persistent Portal service, account or real data exists. The static
  IONOS Website is live from source `e6081580b0d7`; SB-24 also remains on the
  crawler-blocked GitHub-Pages review. The
  IONOS ED25519 host key, corrected Webroot and authenticated read-only
  inventory are proven. Thomas removed the temporary `index.php` on 22.09. and
  allowed redirects via `.htaccess`. The controlled upload, redirect/route/
  security smokes and 762/762 production Edge checks are complete.
- The seventh Coach profile for Guelcan Elmas-Brandes is live with its approved
  metadata-minimized portrait and evidence-backed professional data.

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
4. Treat public Website Messe-Readiness as the only implementation WIP until
   the 25.09. feature freeze; preserve the accepted CAL-1 working tree.
5. Preserve production source/artifact/smoke evidence, test one real message to
   Janay and complete the Website freeze/handover by 25.09.
6. Keep separate approval for any later CAL-1, account, mail automation,
   real-data deployment or native CAL-1 Staging-UI run.
7. PostgreSQL Staging contains migrations 0001-0006 but no business or
   personal data. Do not assign real `calendar_reviewer` roles, add real
   availability, connect the Website calendar or deploy a backend without the
   separately documented gates. A push does not imply deployment.
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
- Is the 200 EUR talk price per participant, and which separately configured
  minimum and maximum attendance apply? The value `25` is now an internal
  review threshold, not the minimum group size.
- Which roles may change an offer's accepted review threshold and capacity?
- What default decision deadline applies to a non-binding seat reservation,
  and when does a separate wait-list state begin?
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
