# Project Status

Last updated: 2026-07-17

## Snapshot

- Overall status: yellow, because the 2026-07-23 deadline is close and coach/legal/server decisions remain open
- Workflow model: informal multi-day deadline sprint
- Current phase: Competence Hub public website MVP
- Current goal: professional, mobile-first B2B website ready by 2026-07-23; first offers are planned from August 2026
- Done: Competence Hub page structure, topic-based B2B homepage, compact responsive navigation, symbol-supported quick paths, expandable content, direct E-Mail inquiry path, central Donner + Partner legal links, curated intermediary positioning, three local coach profiles, role-oriented login preview, initial server/database planning, successful build, responsive visual QA, and the implementation-ready `docs/assets/designstyle.md`
- In progress: erste Mediendesign-Rückmeldung ist lokal umgesetzt; der neue Designstil ist aus Manual, sieben Inspirationsbildern und geprüfter KI-Zweitmeinung dokumentiert; Vertriebs-, Asset- und Publikationsfreigaben stehen aus
- Waiting: final wording, availability, portrait rights, and publication approval for Elisabeth Schwabauer and Carolin Hupp; further coach data may follow
- Blocked for live launch: responsible legal entity/domain confirmation, final Datenschutz/AGB applicability, mailbox ownership and response process, final domain/deployment approval
- Public contact decision: `competencehub@donner-partner.de`
- Local development test contact: `roedel.kg@donner-partner.eu`; excluded from production builds
- Deployment status: manual-only GitHub Pages review is active at `https://dp-manuel.github.io/CompetenceHub/`; latest designer-feedback changes are local and require a new manual review deployment
- Database status: no database change performed; a safe example, a local Git-ignored blank ENV, and an initial data model are prepared
- Server status: no login performed; technical hosting/database questions were sent to Herrn Roß and the response is pending

## Timeline And Quality

- Website MVP deadline: 2026-07-23
- First company offers planned: August 2026
- Build evidence: final `npm run build` passed with 0 Astro errors, warnings, or hints and generated 19 static pages
- Visual evidence: all seven design references were inspected; the designer-feedback revision was checked on homepage, services, business process, and contact at desktop width; homepage and contact were additionally checked at 500 px; coach listing and profiles were checked in the preceding quality pass
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
- Git state: website and review deployment were pushed in commit `f8104b9`; `.tmp/` remains intentionally untracked and the real `.env` remains ignored.
- Safety: source files may only be opened when Manuel names and approves them. Do not open credential documents or real `.env*`, disclose secrets, or deploy without explicit approval.
- Next concrete action: Manuel and the design department review the local website against `docs/assets/designstyle.md`; approved corrections can then be implemented and manually published as a new review revision.
