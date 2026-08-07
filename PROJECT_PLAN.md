# Project Plan

Last updated: 2026-08-07

## Vision

Build a professional digital presence for Firmendingsbums, starting with a public website and growing into an independent web-based administration system with its own login, backend API, and database.

## Current State

- Workflow model: informal multi-day work
- Current phase, sprint, milestone, board status, or release: Competence Hub website deadline sprint
- Current status: yellow; the latest remote frontend and Coach updates through
  commit `8165ebc` are synchronized locally. The centered homepage Hub, the
  About route and Frau Janay Rappelt's contact portrait are implemented locally
  and verified, but remain uncommitted.
- Main blocker: legal/content launch approval and the operating model for the
  future backend are not finalized. EDV has confirmed that IONOS can host the
  static Astro website but cannot provide a permanent Node/Python runtime, and
  its MySQL database cannot be used directly by a backend on the existing VPS.
- Next decision needed: choose and verify an encrypted off-server backup target
  before productive data is permitted. PostgreSQL 16 staging is installed and
  locally restore-tested. The exact operating company follows with the final
  Impressum.

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
- Production deployment, analytics, authentication, payments, or customer data handling until explicitly scoped.
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
- Later: implement the independent web system with login, backend API, own database, roles, and first CRUD workflows.
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
2. **Operational gate:** schedule system updates/reboot, verify firewall and
   Fail2ban administratively, choose an encrypted off-server backup target and
   complete a restore test plan.
3. **Architecture decision:** use the positive capacity inventory to decide the
   isolated pilot shape, backend stack, database engine, staging boundary,
   DNS/TLS ownership, backup and rollback; document the result as an ADR.
4. **Static production readiness:** set the canonical Astro `site`, prepare the
   domain redirect, security/cache headers, error pages and an SFTP deployment
   plus rollback runbook. Deployment still requires separate approval.
5. **First backend slice:** only after the infrastructure gates, build an
   internal `admin`/`staff` workflow for Company, Coach, Service and
   CoachingRequest using test data. External logins, contracts and feedback
   remain later slices.

## Workstream: SEO, GEO & First-Party Authority

Status: planned; inventory and evidence planning only. No new guide pages,
content implementation, publication, or deployment is authorized by this
workstream yet.

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

Status: planned and deferred. The public website may explain the future path,
but no questionnaire, contract workflow, feedback collection or testimonial
publication is authorized in the current static frontend slice.

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

### Planned Customer Path

1. **Need discovery**
   - Explain typical starting situations and offer a personal first contact.
   - Evaluate a structured questionnaire only after purpose, data minimization,
     privacy notice, retention, ownership and secure processing are defined.
2. **Matching and Coach selection**
   - Connect needs and topic areas to one or more suitable Coach profiles.
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
   - No contract data belongs in the public Astro frontend.
5. **Delivery and coordination**
   - Later expose agreed appointments, responsible contacts and relevant
     documents according to role and authorization.
6. **Company feedback**
   - Later provide a role-protected feedback path for company contacts.
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

## Timeline And Budget Signals

- Target date or milestone: website MVP complete by 2026-07-23; first offers planned from August 2026
- Budget or effort assumption: unknown
- Confidence: medium for setup; low for delivery estimates until scope is known
- Risks to time or budget: unclear content, unclear brand direction, late stack or deployment decisions, legal/privacy requirements discovered late

## Risks And Blockers

- Risk: The website could become a generic landing page if goals and audience stay unclear.
- Impact: weaker content, design, and conversion quality.
- Owner: Manuel with Codex support.
- Next mitigation: run a short product/context intake before implementation.

## Quality Gates

- Tests: project-specific checks once a stack exists.
- Manual verification: review responsive desktop/mobile layout and main user flows.
- Security/privacy: avoid committing secrets; identify forms, analytics, cookies, and personal data before implementation.
- Legal/privacy: operational recruiting, placement, platform, app, and participant data flows require legal/DSGVO review before launch.
- Accessibility: keyboard navigation, semantic structure, contrast, focus states, alt text, and responsive readability.
- Performance: lightweight assets, stable layout, image optimization, and build performance checks.
- Deployment/release: deployment target and rollback approach to be defined.
- Artifact-specific checks: website copy, imprint/legal pages, brand asset licensing, and browser compatibility.

## Immediate Next Steps

1. Verify the scheduled Friday Chatbot crawl after it completes; the API and
   services were healthy throughout the maintenance and database installation.
2. Validate Manuels D+P-controlled Würzburg workstation as the first encrypted
   off-server backup target. It must pull the encrypted dump from the VPS; test
   a restore from that exact downloaded copy before real data.
3. Run the portal role/data intake using Manuels forthcoming user-rights list
   and Excel workbook. Use synthetic examples and document field visibility,
   editing rights and retention before creating the first migration.
4. Confirm which Donner + Partner company legally operates Competence Hub when
   contract/invoice data and the final Impressum arrive. Lars Donner is already
   confirmed as legal contact.
5. Define response time and absence cover for Janay Rappelt as mailbox owner.
6. Prepare the static IONOS production-readiness and rollback plan independently
   of backend timing; do not deploy before the previous launch gates are met.
7. Review the centered homepage Hub, `/ueber-uns`, Frau Janay Rappelt's portrait
   and Journey scrolling, then decide separately on commit/push/review deploy.
8. Continue Coach/topic approval work in parallel; assign Mediation only after
   explicit qualification and publication approval.
## Restart Note

Prepared on: 2026-08-06

Resume here:

1. Read `AGENTS.md`, `PROJECT_LOG.md`, this `PROJECT_PLAN.md` and
   `PROJECT_STATUS.md`.
2. Review `docs/architecture/hosting-runtime-decision-2026-08-06.md`,
   `docs/architecture/vps-read-only-inventory-2026-08-06.md`,
   `docs/architecture/versioning-and-operations-plan.md`,
   `docs/requirements/requirements-engineering-update-2026-08-04.md` and
   `docs/assets/designstyle.md`.
3. Check `git status --short`; `.tmp/` must remain untracked and untouched.
4. Review the current uncommitted homepage/About slice locally.
5. Continue from the off-server backup and first migration gates in the
   Hosting, Deployment & Backend Foundation workstream.
6. PostgreSQL staging is installed and empty. Do not add real data or deploy a
   backend without the separately documented production gates. A push does not
   imply either GitHub-Pages or production deployment.
## Open Questions

- How should the sub-brand be named and endorsed under Donner + Partner?
- Is there approved imagery, legal text, or final deployment configuration?
- Which parts of the old Sophisto-like administration workflow should the new app mirror first?
- Which roles are needed first: admin, internal staff, coach, company contact, participant, or others?
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
- Is a logically isolated staging instance on the existing VPS sufficient, or
  is a separate staging server required later?
- Who will be long-term technical owner for GitHub, hosting, deployment, domains/subdomains, and dependency updates?
- Which access handover documentation is required before Manuel can safely transfer technical ownership?
- May the media designer's original seminar illustrations and logo exports be reused on the public website, and in which file formats will they be supplied?
- Should the project-local `new-project-starter` snapshot be intentionally refreshed from the canonical CodexSkills starter after the canonical changes are reviewed?

## Decisions

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
