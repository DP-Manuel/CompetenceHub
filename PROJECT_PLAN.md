# Project Plan

Last updated: 2026-07-31

## Vision

Build a professional digital presence for Firmendingsbums, starting with a public website and growing into an independent web-based administration system with its own login, backend API, and database.

## Current State

- Workflow model: informal multi-day work
- Current phase, sprint, milestone, board status, or release: Competence Hub website deadline sprint
- Current status: yellow; the current Connected Story and Mindforge frontend
  is documented and ready for comparison with a possible new frontend concept
- Main blocker: final legal applicability, remaining coach approvals and the approved live contact/response process are not finalized
- Next decision needed: approve, reject or phase the expected new frontend
  direction after comparing it against current behavior, content and design

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
- In parallel: perform a read-only inventory of the blank server after its purpose and secure access method are confirmed; then select the backend runtime and migration tool.
- Later: implement the independent web system with login, backend API, own database, roles, and first CRUD workflows.
- Before live handover: decide whether content maintenance stays developer-led
  in Astro, uses Astro plus CMS/API, or is fed by the later webapp. WordPress
  remains excluded.
- Before real-site visual production: remind Manuel to request the original seminar illustrations and approved logo exports from the media designer; do not extract production assets from the PDF.
- Future: evaluate document package automation, email sending, structured or AI-assisted matching, commute-time calculation, company feedback links, coach/lecturer workflows, company portal views, participant app, and Hermes Agent automation as separate implementation slices.

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

1. Review the refreshed homepage, topic-based quick navigation, expandable content, and login role paths locally.
2. Review Elisabeth Schwabauer and Carolin Hupp profile wording; obtain portrait and publication approval or keep the profiles local.
3. Confirm whether psychological consultation and supervision are approved public offers and clarify all price units/inclusions.
4. Confirm which Donner + Partner group company legally operates Competence Hub and approve Impressum, Datenschutz, and AGB applicability for the final domain.
5. Confirm the operational owner and expected response process for `competencehub@donner-partner.de`.
6. Complete final browser, accessibility, SEO, and content QA before 2026-07-23.
7. Confirm whether the blank server is staging or production before the first read-only SSH inventory.
8. After server/runtime confirmation, scope secure authentication for the internal role first; coach and company access follow as separate backend slices.
9. Decide whether Recruiting becomes a confirmed public Competence-Hub offer
   and define its exact scope before production wording is finalized.

## Restart Note

Prepared on: 2026-07-16

Resume here:

1. Read `AGENTS.md`, `PROJECT_LOG.md`, and this `PROJECT_PLAN.md`.
2. Review `PROJECT_STATUS.md`, `SKILL_FEEDBACK_LOG.md`, `docs/assets/designstyle.md`, and `docs/requirements/requirements-engineering-update-2026-07-16.md`.
3. Review `apps/website/src/pages/index.astro`, `apps/website/src/pages/login.astro`, `apps/website/src/pages/kontakt.astro`, and `apps/website/src/pages/coaches.astro` for the current B2B direction, role paths, contact flow, and coach-network state.
4. Check `git status --short`; `.tmp/` must remain untracked and untouched.
5. Start the local Astro website and review the current routes; no public deployment is active or approved.
6. Continue from: Manuel's visual approval, coach/publication approval, legal/domain confirmation, and the read-only server inventory decision before 2026-07-23.

## Open Questions

- How should the sub-brand be named and endorsed under Donner + Partner?
- Is there approved imagery, legal text, or final deployment configuration?
- Which parts of the old Sophisto-like administration workflow should the new app mirror first?
- Which roles are needed first: admin, internal staff, coach, company contact, participant, or others?
- Should the later webapp share the same backend/API, auth, design system, and deployment setup?
- Should the operational database be PostgreSQL on the existing VPS, EDV-provided MySQL/MariaDB, or a managed database?
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
- Is the blank server intended as development/staging or as the eventual production environment?
- Who will be long-term technical owner for GitHub, hosting, deployment, domains/subdomains, and dependency updates?
- Which access handover documentation is required before Manuel can safely transfer technical ownership?
- May the media designer's original seminar illustrations and logo exports be reused on the public website, and in which file formats will they be supplied?
- Should the project-local `new-project-starter` snapshot be intentionally refreshed from the canonical CodexSkills starter after the canonical changes are reviewed?

## Decisions

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
