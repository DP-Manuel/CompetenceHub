# Project Status

Last updated: 2026-08-21

## Snapshot

- Overall status: yellow. The website and complete synthetic portal
  slice are verified. The 2026-08-28 target is now technical readiness after
  contract completion; the hard production deadline is 2026-09-25. Runtime,
  App-DNS, SMTP, named accounts, external restore evidence, legal approval and
  Go/No-Go are still open.
- Workflow model: hybrid Scrum/Kanban with a bounded execution backlog and
  rolling six-step horizon.
- Current phase: Competence Hub public website stabilization plus isolated
  portal/backend foundation.
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
- Canonical `main` at `c1f4cc8` contains the reviewed authentication
  foundation and protected company/contact API. PostgreSQL migrations `0001`
  through `0004`, rollback smokes and the prior complete 13/13 Auth/Outbox
  Staging proof are finished. The local suite reports 231 passes with 14
  expected opt-in Staging skips. The first expanded
  Staging run passed 12/14 paths; a stale fixed MFA test time and an untyped
  optional company-search parameter caused the two failures. The corrected
  rerun passed 14/14 with zero synthetic residue, and all four co-hosted VPS
  services remained active. The accepted local ADR-0006 portal package now
  serves login/MFA/session and company/contact UI from the same FastAPI origin;
  241 local tests pass. All 14 tunnel-dependent Staging paths then passed in
  171.95 seconds, including CSRF rotation; checked residue is zero and all four
  VPS services remain active. A synthetic loopback-HTTPS fixture, isolated
  Edge runner and 17-item browser checklist are now prepared. The local suite
  now passes 287 tests with 14 expected opt-in Staging skips; the focused UI/
  fixture tests and an HTTPS/MFA/Secure-cookie/CSP smoke also pass. The first
  manual BA-01 attempt exposed a browser-only disable-before-FormData defect
  across seven forms; it is fixed and regression-protected, with the live
  browser retest then passed. Manuel marked the remaining browser checklist
  passed except BA-14 as qualified. Recovery-code layout, MFA explanation and
  stale reauth/form state were corrected; BA-09, BA-10 and BA-14 then passed
  their focused retests. All 17 browser checks are accepted; the local runner
  is stopped, port 8443 is free and its ephemeral test context is removed. No
  backend or worker is persistently connected or
  deployed as a service.
- Completed locally: SB-20 is reviewed and its clean-source release proof has
  passed. The exact dependency lock,
  deterministic Wheel/ZIP builder, internal file inventory, external
  manifest/checksum, isolated install/fail-closed smoke and executable Linux
  rehearsal runbook are prepared. The final review closed cross-origin action-
  link, multi-recipient mail and Host-header redirect risks. Two complete
  dirty-tree builds after those fixes produced the same ZIP SHA-256; the
  subsequent committed build reported `dirty: false`, passed all package gates
  and installed its Wheel in isolation. The complete synthetic onboarding
  chain passed isolated Staging. SMTP and deployment remain disabled until
  external values and gates close.
- Waiting: remaining profile details and rights where still open; explicit
  qualification and approval before any Coach is assigned to Mediation;
  legal-provider decision, approval of Janay's remaining workflow gates and
  validation of the encrypted Wuerzburg off-server backup target.
- Blocked for live launch: responsible legal entity, final Datenschutz/AGB
  applicability, mailbox response/absence process, content approval and an
  explicitly scheduled production deployment.
- Public contact decision: `competencehub@donner-partner.de`.
- Public mailbox owner: Janay Rappelt.
- Personal portal identities: Manuel uses
  `roedel.kg@donner-partner.eu`; Janay uses
  `rappelt.wue@donner-partner.eu`. Functional aliases are not shared portal
  logins.
- Proposed technical alias: `admin@competencehub.donner-partner.de` forwards
  to Manuel, subject to EDV mail/DNS confirmation; it is not an authentication
  identity. E-Mail is the approved invitation channel. The App-DNS/SMTP/TLS/
  sender/routing request was sent to EDV on 2026-08-21; its answer remains open.
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
- Static deployment access: Manuel holds the SFTP server, username and password
  for the Website start directory. Credentials remain outside Git and project
  documentation. No SFTP upload has been performed.
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
- Portal direction: Product-Owner workbook v0.2 has been evaluated. The
  B2B-first core covers users/multiple roles, companies/contacts,
  Coaches/topics/services, coaching requests and audit. The RBAC matrix for
  Admin, Intern, Coach and Firmenkontakt is largely confirmed. Domain/schema,
  portal IA and RBAC tests are prepared. Migrations `0001`/`0002` are applied
  to VPS staging. Janay's 2026-08-14 feedback now grounds inquiry,
  confidentiality-aware matching, offer/order separation, delivery, feedback
  and closure; exact transition, legal, finance and privacy rules remain gated.
  The local FastAPI Auth runtime now covers session, login, MFA, generic reset
  requests/confirmation, invitation acceptance, persistent invitation
  idempotency and encrypted token outbox processing. Migrations `0003` and
  `0004` are applied to empty Staging with protected pre/post dumps and
  rollback-only smoke evidence. The controlled MFA harness passed 12/12 paths;
  the expanded harness passed 13/13 paths in 156.91 seconds and left all eleven
  checked data areas empty. The final 86-KiB post-dump is catalog-readable.
  All 24 tables belong to `competence_hub_owner`; the App may read but not
  update roles, cannot create schema objects or read migration metadata.
  PostgreSQL remains loopback-only and all four services remain active.
  Nothing is persistently connected, deployed or used with real accounts.
  Admin invitation issuance is wired in the configured Runtime while the
  unconfigured default app remains deny-by-default. Productive token delivery
  remains unavailable until external keys, SMTP/sender, worker operations and
  retention are approved and configured.
- App-distribution direction: PWA-first is the proposed future path for the
  installable authenticated client after the Webapp core. Nothing has been
  implemented; no store or native release is decided. Website/PWA, backend API
  and PostgreSQL remain separated, with no direct client database access.
- Confirmed ownership: Manuel owns VPS operations, patching, monitoring,
  backups and incident response. Thomas Roß, EDV-Leiter, owns production
  approval. Separate app/API subdomains are approved in principle.
- Canonical domain: `competencehub.donner-partner.de`; the hyphenated variant
  should redirect permanently.
- Database direction: ADR 0002 is accepted and implemented for staging with
  PostgreSQL 16. The existing IONOS MySQL database and its credentials are not
  used by the VPS backend. Portal-core migration `0001` exists on the VPS
  staging database, but no business or personal data exists there.

## Timeline And Quality

- Website MVP deadline: 2026-07-23.
- First company offers planned: August 2026.
- Technical-readiness milestone: 2026-08-28, aligned with expected contract
  completion. Janay onboarding and production Go/No-Go will occur afterward;
  dates remain open.
- Hard deadline: 2026-09-25 before Manuel's three-week absence. Legal/operator
  information is expected around mid-September.
- Schedule health: yellow-orange. Database, migrations, Auth/Outbox,
  company/contact API and the local portal UI are implemented; the expanded
  portal harness has 14/14 Staging evidence and all 17 manual browser checks
  passed and runner cleanup is complete. Productive runtime, account
  onboarding, off-server restore evidence and production
  rollout remain on the critical path, but the revised September window is
  achievable if runtime/DNS/SMTP work starts before legal approval arrives.
- Build evidence: Astro checks 38 files with 0 errors, 0 warnings and 0 hints;
  the static build generates 28 pages, including `/ueber-uns/`.
- Release evidence: production and GitHub-review builds both pass. Production
  emits canonical/OG URLs, selective robots rules and a Coach-driven sitemap;
  review emits full crawler blocking and points canonicals to production. The
  ZIP/manifest builder produced a matching SHA-256 and cleaned its isolated
  temporary test artifact. No upload occurred.
- Webapp package evidence: the builder passes dependency-lock validation,
  `pip check`, 287 local tests with 14 expected Staging skips, compileall,
  deterministic Wheel creation, isolated package installation, fail-closed
  API/worker configuration and deployment-placeholder checks. Two repeated
  post-review ZIP builds had identical SHA-256
  `f444a36c0ef1e51e4fd208f85621d15d54ccde9535c24927eaaced76ab5d2f9f`;
  generated test artifacts were removed. Native systemd/Nginx checks remain a
  Linux rehearsal gate.
- Production-indexing safeguard: archived `/system`, `/seminare`,
  `/qualifizierung`, public `/login` previews and prototype routes emit
  `noindex`; the homepage remains indexable.
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
  subjective website acceptance is positive. The portal's BA-01 through BA-17
  browser checklist is fully accepted.
- Network-drive note: direct Astro builds can hang on `Z:` after type
  generation. The same source and existing dependencies build successfully in
  a secret-free local `C:\tmp` verification copy.

## Delivery Horizon

- Recommended next work block: after the EDV response, render and natively
  validate the App-DNS/TLS/Nginx/SMTP configuration without real accounts or
  data. Definition of Done: exact App-Origin and sender are approved, no
  placeholder remains, `systemd-analyze verify` and `nginx -t` pass, and one
  approved synthetic delivery leaves no secret or Outbox residue. Deployment
  still requires a separate approval.
- SB-19 evidence: the existing isolated Outbox Staging test now continues
  through single-use invitation acceptance, password hashing, TOTP enrollment,
  Recovery-code generation and active session creation. It compiles and skips
  cleanly without a tunnel. The corrected controlled execution passed 14/14
  in 151.77 seconds. Users, sessions, outbox and audit rows were all zero after
  cleanup; Chatbot, Nginx, Fail2ban and PostgreSQL remained active.
- Cutline evidence: `docs/requirements/pilot-cutline-2026-08-28.md` now
  proposes Manuel=`admin`, Frau Janay Rappelt=`internal`, the existing minimal
  company/contact fields, explicit non-goals, ten acceptance checks, owners and
  a daily backward plan. Personal account addresses and the E-Mail channel are
  decided; SMTP details, final app DNS, Wuerzburg backup evidence and
  acceptance dates remain open.
- UI architecture: ADR 0006 is accepted. The modular static client is packaged
  with FastAPI on one app origin, adds no frontend framework or Node production
  runtime and keeps the public Astro website independent. Local implementation
  and security/accessibility review plus isolated Staging acceptance are
  complete; all 17 real-browser acceptance checks passed.
- First-factor evidence: 86 local tests pass; 11/11 Auth paths pass against
  isolated PostgreSQL Staging in 103.75 seconds. Cleanup leaves all six checked
  Auth data areas at zero, all four services remain active and the focused
  review has no open high or critical finding.
- MFA local evidence: 148 tests pass, 12 opt-in Staging tests skip; compileall,
  pip check and PowerShell runner syntax pass. The focused review has no open
  high or critical finding.
- Initial-admin and lifecycle evidence: an interactive fail-closed CLI, atomic
  PostgreSQL repository and strict offline SHA-256 fingerprint loader are
  implemented. Invitation/reset single-use, expiry, revocation, rate limiting,
  generic public responses, audit and all-session revocation are covered
  locally. Accepted ADR 0005 adds encrypted transactional token delivery,
  persistent idempotency, Admin invitation API and bounded worker/cleanup
  boundaries. The complete suite reports 214 passed and 13 Staging skips; compile,
  dependency and CLI-help checks pass. No real account was created.
- Company/contact evidence: the protected local API now creates company plus
  first contact atomically, supports bounded list/detail and controlled
  corrections, requires internal MFA plus Origin/CSRF for writes, writes
  payload-free audit events and exposes no delete route. A review finding that
  exposed internal notes in the list shape was fixed through a minimized
  summary model. The full suite reports 231 passed and 14 opt-in Staging skips.
  The corrected real run passed 14/14, removed its synthetic rows and left all
  four co-hosted services active.
- Invitation/runtime evidence: configured lifecycle and password policy,
  encrypted outbox, TLS-only authenticated SMTP adapter, one-shot worker,
  fragment-only action links, Portal forms and service/timer examples are
  implemented. Full local verification reports 287 passed and 14 opt-in
  Staging skips; compileall, `pip check` and JavaScript syntax pass. The final
  review also enforces same-origin action links and single-recipient delivery.
  No external SMTP connection or message occurred.
- Rolling delivery horizon: (1) use the EDV reply to render and natively
  validate DNS/TLS/SMTP configuration, (2) rehearse reverse proxy, static
  release and rollback, (3) close off-server backup/operations gates, (4)
  onboard named users and run supervised synthetic acceptance, (5) obtain
  Legal/Thomas Go/No-Go, (6) release the narrow pilot and first approved company
  no later than 2026-09-25.
  Confidence decreases after step 3.
- Active gates and intended tests are maintained in `PROJECT_PLAN.md` under
  `Delivery Steering`: G-DATA, G-SEC, G-OPS, G-PROD, G-REQ and G-CONTENT.

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
- Which concrete people receive the first synthetic/staging accounts and which
  combinations of the four working roles do they need?
- Which feedback types and statistical formulas are required first, and which
  roles may see them?
- Which exact inquiry states and transitions are approved, who may disclose a
  customer identity to a Coach, and what re-entry rules apply after `on hold`,
  cancellation or no match?
- Which acceptance channel is legally binding, and which system is the source
  of truth for offer, invoice and payment status?
- Which Webapp frontend stack and supported browser/platform baseline make the
  later client PWA-ready without implementing PWA features in the first slice?
- May any authenticated data ever leave the default `NO_CACHE` boundary, and
  who owns the later cache, push and native-distribution security decisions?
- Which remaining Coach texts, qualifications, portraits and publication
  consents are approved?
- Which Coach may be assigned to Mediation after explicit qualification review?
- Which quote, formats, region and availability should complete Frau Elisabeth
  Schwabauer's profile?
- Which travel, cancellation and rescheduling rules apply to Mindforge prices?
- Are psychological consultation and supervision approved public offers?
- Which real references, examples, numbers or quotes may be published?
- Which long-term editorial workflow and technical owner maintain the Astro
  website?

## Restart Handoff

- Read first: `AGENTS.md`, `PROJECT_PLAN.md`, newest `PROJECT_LOG.md`,
  `docs/architecture/hosting-runtime-decision-2026-08-06.md`,
  `docs/architecture/vps-read-only-inventory-2026-08-06.md`,
  `docs/architecture/versioning-and-operations-plan.md`,
  `docs/architecture/pwa-app-distribution-strategy-2026-08-11.md`,
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
- Auth status: ADR 0003 is approved. Migration `0002` is applied and verified on
  VPS staging: 22 tables total, seven empty Auth tables, correct owner/runtime
  rights, protected readable pre/post dumps and unchanged service health. The
  local API now resolves active internal MFA sessions, refreshes idle expiry,
  validates Origin/CSRF for logout, revokes atomically and writes a secret-free
  audit event. Runtime configuration rejects missing or unsafe values without
  exposing the database URL, accepts only loopback PostgreSQL/asyncpg and an
  exact HTTPS browser origin, disposes its engine and reports database-backed
  readiness. Sixty-one local tests pass. Seven of seven opt-in tests also pass
  against isolated PostgreSQL Staging, covering active/expired/revoked/inactive/
  wrong-role sessions, idle refresh, CSRF logout, audit and readiness. Cleanup
  left zero users, sessions and audit rows; only migrations `0001`/`0002`
  remain, and Chatbot, Nginx, Fail2ban and PostgreSQL stayed active. Locally,
  TOTP enrollment/verification, HMAC-only recovery codes, replay protection,
  rate limiting and full-session rotation are implemented with versioned
  external keyrings. The complete local suite reports 148 passed and 12
  skipped; compileall and pip check pass, and the MFA review has no open
  high/critical issue. ADR 0004 is accepted, migration `0003` is applied to
  Staging, its rollback-only smoke passed without residue and the complete
  synthetic MFA integration passed 12/12 paths in 134.98 seconds. Its protected
  74-KiB post-dump is catalog-readable. Independent checks confirm all nine
  data areas empty, migrations `0001`-`0003`, four active services and
  PostgreSQL only on `127.0.0.1:5432`. Migration `0004` is also applied and
  rollback-smoke-tested. The expanded Staging harness passed 13/13 paths in
  156.91 seconds; all eleven checked data areas are empty, migrations
  `0001`-`0004` are registered, all 24 tables have the intended owner and the
  protected 86-KiB post-dump is catalog-readable. The runtime role can read but
  not update roles. Real accounts and deployable service configuration do not
  exist.
- Versioning status: feature commit `8feb2c8` was pushed successfully to
  `origin/main` on 2026-08-13. `.tmp/`, `.venv/`, generated package metadata,
  real `.env` files and secrets were excluded; no deployment was triggered.
- Parallel organizational gates: approve the remaining state/legal/privacy/
  finance decisions in Janay's captured workflow before final automation, and
  validate the Wuerzburg workstation as an encrypted off-server backup/restore
  target before any real data.
- Separate approvals still required: backend deployment,
  production deployment and use of real business or personal data.
