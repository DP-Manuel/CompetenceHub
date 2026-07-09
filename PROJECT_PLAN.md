# Project Plan

Last updated: 2026-06-30

## Vision

Build a professional digital presence for Firmendingsbums, starting with a public website and growing into an independent web-based administration system with its own login, backend API, and database.

## Current State

- Workflow model: informal multi-day work
- Current phase, sprint, milestone, board status, or release: kickoff-ready stakeholder prototype
- Current status: green
- Main blocker: public offer name, exact subdomain, legal wording, final visual review, and future app/backend/database architecture are not finalized
- Next decision needed: how to frame the pre-built prototype as a positive surprise for the official 2026-07-01 project start

## Scope

In scope:

- Public website as the first deliverable.
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

- Now: present the polished Variant B prototype and first real coach profile at the official 2026-07-01 project kickoff.
- Next: use stakeholder feedback to align positioning, sub-brand, website scope, and future app direction without implying prior leadership approval.
- Later: design the independent web system with login, backend API, own database, roles, and first CRUD workflows.
- Before live handover: decide whether content maintenance stays developer-led in Astro, uses Astro plus CMS/API, moves to WordPress, or is fed by the later webapp.
- Before real-site visual production: remind Manuel to request the original seminar illustrations and approved logo exports from the media designer; do not extract production assets from the PDF.
- Future: evaluate document package automation, email sending, structured or AI-assisted matching, commute-time calculation, company feedback links, coach/lecturer workflows, company portal views, participant app, and Hermes Agent automation as separate implementation slices.

## Timeline And Budget Signals

- Target date or milestone: stakeholder presentation on 2026-07-01
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

1. Review the deployed prototype and Christian Galvano's polished live coach profile at the 2026-07-01 meeting display size.
2. Decide whether the separate "Für Unternehmen" page remains or becomes part of homepage/qualification.
3. Confirm Christian Galvano's profile wording and collect stakeholder feedback; the portrait supplied by Manuel is already integrated.
4. Before live operation, make and document the future Redaktionsmodell decision: Astro developer-maintained, Astro plus CMS/API, WordPress/other CMS, or later webapp-fed content.
5. Prepare a stakeholder reveal path for 2026-07-01: what to show first, how to frame the pre-work, what to say about scope, and what decisions to request.
6. Keep future app/data model work separate from the website prototype unless a stakeholder decision requires a short visual preview.
7. Collect missing decisions for login/system roles, soft skills, references, exact subdomain, legal/privacy wording, public offer name, Redaktionsworkflow, and long-term technical owner.
8. When prototype work becomes real-site production, ask the media designer for the original seminar illustrations and approved logo files before replacing the temporary visual treatment.

## Restart Note

Prepared on: 2026-06-30

Resume here:

1. Read `AGENTS.md`, `PROJECT_LOG.md`, and this `PROJECT_PLAN.md`.
2. Review `PROJECT_STATUS.md`, `SKILL_FEEDBACK_LOG.md`, and `docs/requirements/content-briefing-colleague-prototype.md`.
3. Review `docs/requirements/website-maintenance-handover-and-editor-workflows.md` and `apps/website/src/pages/coaches/christian-galvano.astro` for handover, editor workflow, and the first real coach profile.
4. Check `git status --short`; expect public website code to be clean/pushed and internal project memory/docs to remain local/untracked unless Manuel asks to commit them.
5. Open the public prototype at `https://dp-manuel.github.io/Firmenschulung/` and verify the navigation path.
6. Continue from: live visual review of the updated German prototype and Christian Galvano profile, photo/content approval, and stakeholder demo preparation for 2026-07-01.

## Open Questions

- What is the public offer or product name?
- How should Manuel frame that the website prototype was prepared before leadership knew about the website work?
- How should the sub-brand be named and endorsed under Donner + Partner?
- What should the website make visitors do?
- Which pages or sections are required for the first version?
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
- Should the separate "Für Unternehmen" page remain in the prototype, or should its content be merged into homepage and qualification?
- Which soft skills should be captured for later matching?
- Which references, examples, numbers, or quotes may be named publicly?
- Which content maintenance model should support the non-technical colleague: developer-led Astro edits, Astro plus CMS/API, WordPress, or later webapp-fed content?
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
