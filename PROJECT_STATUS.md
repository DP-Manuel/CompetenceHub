# Project Status

Last updated: 2026-07-29

## Snapshot

- Overall status: yellow, because the local concept is implemented but content,
  legal, profile and production decisions remain open
- Workflow model: informal multi-day deadline sprint
- Current phase: Competence Hub public website MVP
- Current goal: professional, mobile-first B2B and B2C website for offers from August 2026
- Done: Competence Hub page structure, central interactive Connected-Core graph, Connected-Story start page, local Mindforge area with approved B2C/B2B prices, Assessment Center links for recruiting and development, direct E-Mail inquiry path, central legal links, curated intermediary positioning, four coach profiles, Elisabeth Schwabauer's approved portrait and additional qualification, visible personal contact role, role-oriented login preview, initial server/database planning, and the implementation-ready `docs/assets/designstyle.md`
- In progress: stakeholder review of the versioned Mindforge extension,
  approved prices, Assessment Center presentation and Elisabeth profile
- Waiting: Elisabeth Schwabauer's quote, preferred formats, region and
  availability; final wording, portrait rights and publication approval for
  Carolin Hupp; further coach data may follow
- Blocked for live launch: responsible legal entity/domain confirmation, final Datenschutz/AGB applicability, mailbox ownership and response process, final domain/deployment approval
- Public contact decision: `competencehub@donner-partner.de`
- Local development test contact: `roedel.kg@donner-partner.eu`; excluded from production builds
- Deployment status: the 2026-07-24 Connected-Story revision was pushed in
  implementation commit `fcc0129` and successfully published through manual
  GitHub Pages review workflow `30094540079`; automatic deployment remains
  disabled. The 2026-07-29 Mindforge revision is versioned on `main`, but its
  manual GitHub Pages review publication has not been started.
- Database status: no database change performed; a safe example, a local Git-ignored blank ENV, and an initial data model are prepared
- Server status: no login performed; technical hosting/database questions were sent to Herrn Roß and the response is pending

## Timeline And Quality

- Website MVP deadline: 2026-07-23
- First company offers planned: August 2026
- Build evidence: `npm run build` passes with 0 Astro errors, warnings, or
  hints across 27 files and generates 22 static pages
- Visual evidence: Mindforge, the updated Connected-Core graph, the company
  Assessment Center area and Elisabeth Schwabauer's profile were checked at
  1440 and 500 px
- Accessibility direction: semantic headings, native links/details navigation, visible focus, readable contrast, responsive text fit, and reduced-motion handling
- Remaining QA: final content proofread, legal review, production-domain
  SEO/canonical/structured-data work, and incoming coach-profile QA

## Decisions Needed

- Which Donner + Partner group company is the legal Competence Hub provider?
- Who monitors `competencehub@donner-partner.de`, and what response expectation can be stated publicly?
- What is the final subdomain and approved deployment target?
- Which remaining coach texts, qualifications, portraits, and publication consents are approved?
- Which quote, formats, region and availability should complete Elisabeth Schwabauer's profile?
- Which travel, cancellation and rescheduling rules apply to the approved Mindforge prices?
- Is the blank server intended for development/staging or production?
- Is MySQL or MariaDB installed, and which version is available?
- Are workshop/talk prices per person or per event, and what is included?
- Are psychological consultation and supervision approved public offers?
- Which real references, examples, numbers, or quotes may be published?
- Which approved logo, font, and photographic assets define the final brand treatment?
- Which long-term editorial workflow and technical owner maintain the Astro website?

## Restart Handoff

- Read first: `AGENTS.md`, `PROJECT_LOG.md`, `PROJECT_PLAN.md`, this file, `SKILL_FEEDBACK_LOG.md`, and `docs/assets/designstyle.md` for visual work.
- Website entry points: `apps/website/src/layouts/BaseLayout.astro`, `apps/website/src/pages/index.astro`, `apps/website/src/pages/mindforge.astro`, `apps/website/src/pages/unternehmen.astro`, `apps/website/src/pages/kontakt.astro`, `apps/website/src/pages/coaches.astro`, and `apps/website/src/styles/global.css`.
- Git state: the 2026-07-29 Mindforge and Elisabeth extension is versioned on
  `main`; its manual Pages publication remains pending. `.tmp/` remains
  intentionally untracked and the real `.env` remains ignored.
- Safety: source files may only be opened when Manuel names and approves them. Do not open credential documents or real `.env*`, disclose secrets, or deploy without explicit approval.
- Next concrete action: Manuel and the design department review Mindforge,
  approved prices, Assessment Center and Elisabeth's updated profile; after
  approval, the existing manual Pages workflow can publish the review build.
