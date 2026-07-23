# Project Status

Last updated: 2026-07-23

## Snapshot

- Overall status: yellow, because the local concept is implemented but content,
  legal, profile and production decisions remain open
- Workflow model: informal multi-day deadline sprint
- Current phase: Competence Hub public website MVP
- Current goal: professional, mobile-first B2B website ready by 2026-07-23; first offers are planned from August 2026
- Done: Competence Hub page structure, central interactive Connected-Core graph, topic-based B2B paths, direct E-Mail inquiry path, central legal links, curated intermediary positioning, four local coach profiles, visible personal contact role, role-oriented login preview, initial server/database planning, and the implementation-ready `docs/assets/designstyle.md`
- In progress: stakeholder review of the local Connected Core, Recruiting,
  Wegner-Ney and the Janay-Rappelt contact role; public wording and publication
  approvals remain open
- Waiting: final wording, availability, portrait rights, and publication approval for Elisabeth Schwabauer and Carolin Hupp; further coach data may follow
- Blocked for live launch: responsible legal entity/domain confirmation, final Datenschutz/AGB applicability, mailbox ownership and response process, final domain/deployment approval
- Public contact decision: `competencehub@donner-partner.de`
- Local development test contact: `roedel.kg@donner-partner.eu`; excluded from production builds
- Deployment status: the 2026-07-23 Connected-Core work was pushed in
  implementation commit `693901b`; the manual-only GitHub Pages review still
  shows the previous revision because CLI authentication must be renewed before
  dispatching the workflow
- Database status: no database change performed; a safe example, a local Git-ignored blank ENV, and an initial data model are prepared
- Server status: no login performed; technical hosting/database questions were sent to Herrn Roß and the response is pending

## Timeline And Quality

- Website MVP deadline: 2026-07-23
- First company offers planned: August 2026
- Build evidence: final `npm run build` passed with 0 Astro errors, warnings, or
  hints and generated 20 static pages
- Visual evidence: the central Connected-Core graph was checked on the
  homepage at 1440 and 500 px; Coach-Übersicht, Wegner-Ney, Kontakt and
  Businesscoaching were checked at desktop width. Hero wrapping, the mobile hub
  grid and portrait sizing were corrected during QA.
- Accessibility direction: semantic headings, native links/details navigation, visible focus, readable contrast, responsive text fit, and reduced-motion handling
- Remaining QA: real-browser keyboard/menu check, final content proofread, legal review, production-domain SEO/canonical/structured-data work, and incoming coach-profile QA

## Decisions Needed

- Which Donner + Partner group company is the legal Competence Hub provider?
- Who monitors `competencehub@donner-partner.de`, and what response expectation can be stated publicly?
- What is the final subdomain and approved deployment target?
- Which coach texts, qualifications, portraits, and publication consents are approved?
- Is the blank server intended for development/staging or production?
- Is MySQL or MariaDB installed, and which version is available?
- Are workshop/talk prices per person or per event, and what is included?
- Are psychological consultation and supervision approved public offers?
- Which real references, examples, numbers, or quotes may be published?
- Which approved logo, font, and photographic assets define the final brand treatment?
- Which long-term editorial workflow and technical owner maintain the Astro website?

## Restart Handoff

- Read first: `AGENTS.md`, `PROJECT_LOG.md`, `PROJECT_PLAN.md`, this file, `SKILL_FEEDBACK_LOG.md`, and `docs/assets/designstyle.md` for visual work.
- Website entry points: `apps/website/src/layouts/BaseLayout.astro`, `apps/website/src/pages/index.astro`, `apps/website/src/pages/kontakt.astro`, `apps/website/src/pages/coaches.astro`, and `apps/website/src/styles/global.css`.
- Git state: the central Connected-Core implementation was pushed in commit
  `693901b`; `.tmp/` remains intentionally untracked and the real `.env`
  remains ignored. The public Pages review has not yet been rebuilt from this
  commit.
- Safety: source files may only be opened when Manuel names and approves them. Do not open credential documents or real `.env*`, disclose secrets, or deploy without explicit approval.
- Next concrete action: Manuel and the design department review the central
  relationship graph and its wording locally against `docs/assets/designstyle.md`;
  approved corrections can then be prepared for a later review publication.
