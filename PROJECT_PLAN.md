# Project Plan

Last updated: 2026-07-16

## Vision

Build a professional digital presence for Firmendingsbums, starting with a public website and growing into an independent web-based administration system with its own login, backend API, and database.

## Current State

- Workflow model: informal multi-day work
- Current phase, sprint, milestone, board status, or release: Competence Hub website deadline sprint
- Current status: yellow
- Main blocker: final coach/publication approval, legal applicability, pricing semantics, and the approved live contact/response process are not finalized
- Next decision needed: approve the compact visual direction, curated intermediary positioning, and the Elisabeth Schwabauer / Carolin Hupp profile drafts

## Scope

In scope:

- Public website as the first deliverable.
- B2B-first Competence Hub presentation for Livecoaching and Businesscoaching.
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
- Users or affected groups: companies first; later internal staff, coaches, participants, and company contacts
- External stakeholders: executive stakeholders for 2026-07-01 presentation; EDV for hosting/subdomain/database coordination

## Roadmap Or Work Plan

- Now: complete the professional, mobile-first Competence Hub website MVP by 2026-07-23.
- Now: validate the new topic-based navigation and role-oriented login preview with Manuel; no real authentication belongs in the public website slice.
- Next: approve and publish the new coach content only after wording, current availability, image rights, and publication consent are confirmed.
- In parallel: perform a read-only inventory of the blank server after its purpose and secure access method are confirmed; then select the backend runtime and migration tool.
- Later: implement the independent web system with login, backend API, own database, roles, and first CRUD workflows.
- Before live handover: decide whether content maintenance stays developer-led in Astro, uses Astro plus CMS/API, moves to WordPress, or is fed by the later webapp.
- Before real-site visual production: remind Manuel to request the original seminar illustrations and approved logo exports from the media designer; do not extract production assets from the PDF.
- Future: evaluate document package automation, email sending, structured or AI-assisted matching, commute-time calculation, company feedback links, coach/lecturer workflows, company portal views, participant app, and Hermes Agent automation as separate implementation slices.

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

## Restart Note

Prepared on: 2026-07-16

Resume here:

1. Read `AGENTS.md`, `PROJECT_LOG.md`, and this `PROJECT_PLAN.md`.
2. Review `PROJECT_STATUS.md`, `SKILL_FEEDBACK_LOG.md`, and `docs/requirements/requirements-engineering-update-2026-07-16.md`.
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
