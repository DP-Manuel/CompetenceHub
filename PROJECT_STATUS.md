# Project Status

Last updated: 2026-08-07

## Snapshot

- Overall status: yellow, because the current local frontend and isolated VPS
  staging foundation are verified, but the exact legal operating company,
  off-server backup and production operational gates are still open.
- Workflow model: informal multi-day delivery.
- Current phase: Competence Hub public website MVP stabilization.
- Current goal: professional, mobile-first B2B and B2C website for offers from
  August 2026.
- Done: Living-Hub website, centered homepage hierarchy, `/ueber-uns` with the
  approved portrait of Frau Janay Rappelt, the same portrait in the homepage
  contact block, internal Hub-Journey navigation,
  Mindforge umbrella for Life Coaching and
  Businesscoaching, eight-node homepage Hub, topic-based Coach discovery,
  six Coach profiles, updated Herr T. Wegner-Ney profile, approved Frau
  Dr. Stefanie Becker profile with portrait and without customer references,
  qualification-gated
  Mediation topic, direct E-Mail inquiry path, legal links, role-oriented login
  preview, PostgreSQL 16 staging installation, separated database roles and a
  successful synthetic local dump/restore rehearsal.
- Latest remote state: commit `19a6f49` (`Prepare Competence Hub frontend and
  staging foundation`) is synchronized locally and contains the centered
  homepage/About/Journey revision plus the documented backend foundation.
- In progress: stakeholder review of the centered Hub and `/ueber-uns` through
  the manually published GitHub-Pages review environment.
- Waiting: remaining profile details and rights where still open; explicit
  qualification and approval before any Coach is assigned to Mediation;
  legal-provider decision, portal role matrix, Excel data input and validation
  of the encrypted Würzburg off-server backup target.
- Blocked for live launch: responsible legal entity, final Datenschutz/AGB
  applicability, mailbox response/absence process, content approval and an
  explicitly scheduled production deployment.
- Public contact decision: `competencehub@donner-partner.de`.
- Public mailbox owner: Janay Rappelt.
- Legal contact: Lars Donner; the concrete operating company, contract/invoice
  details and final Impressum are still pending.
- Deployment status: GitHub-Pages review commit `19a6f49` was manually
  published successfully through Actions run `31172489046` and is available at
  `https://dp-manuel.github.io/CompetenceHub/`. Homepage and `/ueber-uns/`
  return HTTP 200. The review banner and `noindex, nofollow, noarchive` remain
  active. Pushes still do not deploy automatically.
- Hosting status: EDV confirmed the IONOS webspace as production hosting for
  static/PHP files. Both Competence-Hub subdomains point there and are covered
  by wildcard TLS. Permanent Node/Python services are not possible.
- Database/server status: IONOS MySQL is accessible only from its own webspace
  and is not used by the VPS backend. On 2026-08-07 the VPS was patched and
  rebooted into kernel `6.8.0-137-generic`; Chatbot, Nginx and Fail2ban remained
  healthy. PostgreSQL 16.14 is installed, enabled and bound only to
  `127.0.0.1:5432`. The empty `competence_hub_staging` database uses separate
  owner, migrator and restricted app roles.
- Operational server gates: UFW defaults to deny incoming traffic and exposes
  only 22/80/443; Fail2ban protects SSH. PostgreSQL uses peer authentication on
  local sockets and SCRAM-SHA-256 on loopback TCP. A local protected dump and
  synthetic restore rehearsal succeeded. No encrypted off-server copy exists,
  so productive company or personal data remains blocked.
- Maintenance timing: the originally planned Saturday window was superseded
  by the approved Friday change on 2026-08-07 before the scheduled crawl. The
  crawl timer remains active for about 15:22 UTC / 17:22 Europe/Berlin.
- Backup decision: no Cloud/Object Storage purchase is currently authorized.
  PostgreSQL remains staging-only with synthetic data. Productive data requires
  an encrypted external copy to D+P-controlled storage and a restore test. The
  D+P workstation at the Würzburg site is the preferred candidate, pending
  disk-encryption/access checks and restore from the downloaded copy.
- Portal direction: the authenticated webapp will add internal user creation,
  multiple roles per person, company and Coach administration, scoped feedback
  and role-aware statistics. The first implementation slice is authentication,
  authorization and auditability; Manuel will provide users/rights and an Excel
  workbook before schema implementation.
- Confirmed ownership: Manuel owns VPS operations, patching, monitoring,
  backups and incident response. Thomas Roß, EDV-Leiter, owns production
  approval. Separate app/API subdomains are approved in principle.
- Canonical domain: `competencehub.donner-partner.de`; the hyphenated variant
  should redirect permanently.
- Database direction: ADR 0002 is accepted and implemented for staging with
  PostgreSQL 16. The existing IONOS MySQL database and its credentials are not
  used by the VPS backend. No application schema migration or real data exists.

## Timeline And Quality

- Website MVP deadline: 2026-07-23.
- First company offers planned: August 2026.
- Build evidence: Astro checks 36 files with 0 errors, 0 warnings and 0 hints;
  the static build generates 28 pages, including `/ueber-uns/`.
- Smoke evidence: local HTTP 200 for homepage, Mindforge, Coach overview,
  Frau Dr. Stefanie Becker, Herr T. Wegner-Ney and contact; eight Hub nodes,
  no separate Businesscoaching node, Mindforge-to-Businesscoaching link,
  Mediation filter and empty state confirmed in generated HTML.
- Accessibility direction: native filter buttons, `aria-pressed`, controlled
  profile grid, visible live status, honest empty state, visible focus and
  reduced-motion-aware automatic scrolling.
- Browser evidence: desktop screenshots and real 390-pixel mobile emulation
  show no horizontal overflow on `/` or `/ueber-uns/`. The Hub core route and
  all four internal Journey hashes were verified in the browser. Manuel's
  subjective visual acceptance remains open before publication.
- Network-drive note: direct Astro builds can hang on `Z:` after type
  generation. The same source and existing dependencies build successfully in
  a secret-free local `C:\tmp` verification copy.

## Decisions Needed

- Which Donner + Partner group company is the legal Competence Hub provider?
- What response expectation and absence cover apply to Janay Rappelt's public
  mailbox?
- Who performs the static IONOS deployment and rollback after Thomas Roß's
  production approval?
- Who receives controlled successor/emergency server access if Manuel is
  unavailable?
- Which encrypted off-server backup target, retention and restore-test rhythm
  are approved?
- Which initial users receive accounts, which roles do they hold, and what may
  each role read, create, edit, approve, deactivate, export or evaluate?
- Which Excel fields are authoritative ideas, required fields, relationships or
  import candidates, and which contain personal data?
- Which feedback types and statistical formulas are required first, and which
  roles may see them?
- Is an isolated staging instance on the same VPS sufficient?
- Which remaining Coach texts, qualifications, portraits and publication
  consents are approved?
- Which Coach may be assigned to Mediation after explicit qualification review?
- Which quote, formats, region and availability should complete Frau Elisabeth
  Schwabauer's profile?
- Which travel, cancellation and rescheduling rules apply to Mindforge prices?
- Does the future backend need a separate staging server, or is an isolated
  staging instance acceptable after the VPS inventory?
- Are psychological consultation and supervision approved public offers?
- Which real references, examples, numbers or quotes may be published?
- Which long-term editorial workflow and technical owner maintain the Astro
  website?

## Restart Handoff

- Read first: `AGENTS.md`, `PROJECT_PLAN.md`, newest `PROJECT_LOG.md`,
  `docs/architecture/hosting-runtime-decision-2026-08-06.md`,
  `docs/architecture/vps-read-only-inventory-2026-08-06.md`,
  `docs/architecture/versioning-and-operations-plan.md`,
  `docs/requirements/requirements-engineering-update-2026-08-04.md` and
  `docs/assets/designstyle.md`.
- Key implementation files: `apps/website/src/data/coaches.ts`,
  `apps/website/src/pages/coaches.astro`,
  `apps/website/src/pages/coaches/stefanie-becker.astro`,
  `apps/website/src/pages/coaches/wegner-ney.astro`,
  `apps/website/src/components/CompetenceHubMap.astro`,
  `apps/website/src/components/LivingHubPrototype.astro`,
  `apps/website/src/components/HubJourney.astro`,
  `apps/website/src/pages/ueber-uns.astro`,
  `apps/website/src/pages/mindforge.astro` and
  `apps/website/src/styles/global.css`.
- Workstation setup: Git/GitHub HTTPS authentication works; repository-local
  author identity matches the existing history. Canonical CodexSkills are
  cloned separately at `Z:\IT Development Manuel\CodexSkills`. Read
  `docs/architecture/second-workstation-setup.md` for the verified paths,
  Node/npm rules, network-drive build fallback and browser limitation.
- Safety: do not open credentials or `.env*`; keep `.tmp/` untracked; publish no
  customer references from Frau Dr. Stefanie Beckers source material; do not
  infer a Mediationsqualification.
- Next concrete action: verify the scheduled Friday crawl after it completes,
  then validate and test the Würzburg workstation as encrypted off-server
  backup target. In parallel, receive the portal user-rights list and synthetic
  Excel field model before turning `initial-data-model.md` into a versioned
  migration. Keep staging empty and free of real data until the backup gate is
  closed.
