# Project Status

Last updated: 2026-08-04

## Snapshot

- Overall status: yellow, because the current local frontend slice is verified
  but legal, production and remaining profile/rights decisions are still open.
- Workflow model: informal multi-day delivery.
- Current phase: Competence Hub public website MVP stabilization.
- Current goal: professional, mobile-first B2B and B2C website for offers from
  August 2026.
- Done: Living-Hub website, Mindforge umbrella for Life Coaching and
  Businesscoaching, eight-node homepage Hub, topic-based Coach discovery,
  six Coach profiles, updated Herr T. Wegner-Ney profile, approved Frau
  Dr. Stefanie Becker profile without customer references, qualification-gated
  Mediation topic, direct E-Mail inquiry path, legal links, role-oriented login
  preview and initial server/database planning.
- Latest implementation: commit `6bf28ec` (`Integrate coach feedback and
  profiles`).
- In progress: final real-browser desktop/mobile review of Hub geometry, topic
  selection, automatic result scroll, focus behavior and long text wrapping.
- Waiting: remaining profile details and rights where still open; explicit
  qualification and approval before any Coach is assigned to Mediation.
- Blocked for live launch: responsible legal entity/domain confirmation, final
  Datenschutz/AGB applicability, mailbox ownership and response process, final
  domain and deployment approval.
- Public contact decision: `competencehub@donner-partner.de`.
- Deployment status: the last public GitHub-Pages review contains website commit
  `7f13cec`; the new `6bf28ec` slice is not deployed. Pushes do not deploy
  automatically; the review workflow remains a separate manual action.
- Database/server status: no database change and no server login performed;
  hosting/database clarification remains pending.

## Timeline And Quality

- Website MVP deadline: 2026-07-23.
- First company offers planned: August 2026.
- Build evidence: Astro checks 35 files with 0 errors, 0 warnings and 0 hints;
  the static build generates 27 pages, including
  `/coaches/stefanie-becker/`.
- Smoke evidence: local HTTP 200 for homepage, Mindforge, Coach overview,
  Frau Dr. Stefanie Becker, Herr T. Wegner-Ney and contact; eight Hub nodes,
  no separate Businesscoaching node, Mindforge-to-Businesscoaching link,
  Mediation filter and empty state confirmed in generated HTML.
- Accessibility direction: native filter buttons, `aria-pressed`, controlled
  profile grid, visible live status, honest empty state, visible focus and
  reduced-motion-aware automatic scrolling.
- Verification limitation: the in-app browser connection timed out twice on
  this workstation. Final visual and keyboard checks at representative desktop
  and mobile widths remain manual before any public review deployment.
- Network-drive note: direct Astro builds can hang on `Z:` after type
  generation. The same source and existing dependencies build successfully in
  a secret-free local `C:\tmp` verification copy.

## Decisions Needed

- Which Donner + Partner group company is the legal Competence Hub provider?
- Who monitors `competencehub@donner-partner.de`, and what response expectation
  can be stated publicly?
- What is the final subdomain and approved deployment target?
- Which remaining Coach texts, qualifications, portraits and publication
  consents are approved?
- Which Coach may be assigned to Mediation after explicit qualification review?
- Which quote, formats, region and availability should complete Frau Elisabeth
  Schwabauer's profile?
- Which travel, cancellation and rescheduling rules apply to Mindforge prices?
- Is the blank server intended for development/staging or production?
- Are psychological consultation and supervision approved public offers?
- Which real references, examples, numbers or quotes may be published?
- Which long-term editorial workflow and technical owner maintain the Astro
  website?

## Restart Handoff

- Read first: `AGENTS.md`, `PROJECT_PLAN.md`, newest `PROJECT_LOG.md`,
  `docs/requirements/requirements-engineering-update-2026-08-04.md` and
  `docs/assets/designstyle.md`.
- Key implementation files: `apps/website/src/data/coaches.ts`,
  `apps/website/src/pages/coaches.astro`,
  `apps/website/src/pages/coaches/stefanie-becker.astro`,
  `apps/website/src/pages/coaches/wegner-ney.astro`,
  `apps/website/src/components/CompetenceHubMap.astro`,
  `apps/website/src/pages/mindforge.astro` and
  `apps/website/src/styles/global.css`.
- Workstation setup: Git/GitHub HTTPS authentication works; repository-local
  author identity matches the existing history. Canonical CodexSkills are
  cloned separately at `Z:\IT Development Manuel\CodexSkills`.
- Safety: do not open credentials or `.env*`; keep `.tmp/` untracked; publish no
  customer references from Frau Dr. Stefanie Beckers source material; do not
  infer a Mediationsqualification.
- Next concrete action: visually and by keyboard review the new local slice,
  then decide separately whether to run the manual GitHub-Pages review workflow.
