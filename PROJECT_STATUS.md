# Project Status

Last updated: 2026-09-11

## Snapshot

- Overall status: yellow for production, green for the 2026-08-28 technical-
  readiness checkpoint. The website and complete synthetic portal slice,
  clean release package and external restore rehearsal are verified. The former
  2026-09-25 production deadline is retired. A first small controlled start can
  be accepted on 2026-09-17 if every preceding gate closes; 2026-09-24 is the
  preferred fallback, otherwise the start moves to a documented later date.
  Production runtime scheduling/alerting,
  App-DNS, SMTP, named accounts, legal approval and Go/No-Go are still open.
- Workflow model: hybrid Scrum/Kanban with a bounded execution backlog and
  rolling eight-step horizon.
- External-dependency steering: a dated lead-time radar now tracks EDV, legal,
  contract, onboarding, mailbox and off-server-backup inputs before they block
  current WIP. EXT-01 is waiting; SB-21 and the native EXT-05 rehearsal are
  complete. A USB
  target is now present in Wuerzburg and BitLocker To Go is fully enabled.
  The restore workstation system drive is also BitLocker-encrypted, the USB
  will be kept in the safe and Janay is the named recovery owner. The
  workstation-only RSA-4096 GPG key and public export are verified. Recovery-
  code/passphrase escrow is confirmed without exposing either value. Public-key
  handoff and the complete SB-21 package are hash-verifiably staged on the VPS.
  Root/postgres installation, native backup/monitor, guarded external transfer
  and exact-copy restore passed with timers disabled and all co-hosted services
  healthy. Production scheduling/alerting and the other data gates remain.
- Pilot operations decisions: Manuel remains operational Admin; Thomas Ross is
  the technical break-glass successor, not a general holiday or mailbox cover.
  Janay owns the Competence Hub mailbox; no substitute is currently named for
  her absence, so no public response-time promise is permitted. Daily backup
  and monitoring schedules plus 30 daily/12 monthly retention are accepted.
  Manuel must receive a concise success or incident notice automatically; the
  delivery channel still depends on the EDV/SMTP decision.
- Backup notification slice: commit `58299ae` provides a local-only, bounded
  JSON contract for daily success and defined incidents. Event/code pairs,
  fixed text, UTC timestamps and stable deduplication are tested; the renderer
  imports no network or process module. No adapter, message or timer is active.
- Calendar business decisions: Janay accepted CAL-D01 through CAL-D08 and the
  complete Pilot flow on 2026-09-11. Public offer visibility, authenticated
  company reservations, separate threshold/capacity, decision deadlines,
  minimal fields, governed topics, Janay's task plus E-Mail, publication checks
  and provider-neutral `.ics` delivery are now the approved business baseline.
  Manuel accepted ADR 0007 on 2026-09-11. The CAL-1 architecture, data, API and
  RBAC design is complete; migration and activation remain separate gates.
- E-Mail workflow input: twelve supplied templates are inventoried as future
  process ideas. Fixed response times, guarantees, refunds, automatic
  rescheduling, discounts, newsletters and E-Mail acceptance are not approved
  for automation. Transactional, marketing and legally relevant messages stay
  separated.
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
  Mediation topic, honest mail-client inquiry path, legal links, role-oriented login
  preview, PostgreSQL 16 staging installation, separated database roles and a
  successful synthetic local dump/restore rehearsal.
- Done and GitHub-Pages review deployed: the authorized 27.08 website
  feedback is consolidated. Beratung now sits under Mindforge; public offers
  and navigation are reduced to clearer top-level groups; the four service
  cards form a balanced 2x2 layout; Hub nodes are clickable, spaced and gently
  pulsing with reduced-motion support; the Coach rail has real previous/pause/
  next controls; required contact fields are explicit and Anliegen remains
  optional. Follow-up QA confirms independent FAQ heights, a fourth clickable
  Assessment-Center bubble on Mindforge, 30-pixel process-card clearance and
  automatic Coach movement even while the pointer rests over the rail. No
  direct form endpoint or calendar booking was activated.
- Done and crawler-blocked review deployed: `/unternehmen` now contains two source-governed visual
  stories. A clearly labelled illustrative leadership path and a Concept Clean
  communication-course path each use a semantic five-step winding route that
  becomes linear on mobile. The customer quote remains faithful to the
  supplied feedback; unsupported response times, package sizes, ratings,
  outcomes and click acceptance were excluded.
  Desktop visual review and exact 390-pixel layout checks report no document,
  story or step overflow; Astro checks 39 files without diagnostics and builds
  29 pages. Manuel confirmed Concept Clean publication approval for company
  name and quotation on 2026-09-04 and then explicitly requested the supplied
  logo in a scalable customer-feedback presentation. The resulting compact
  rail uses a publication-gated data source, visible logo, collaboration topic,
  short quotation and separate quotation marks; controls activate only when
  more entries exist. Workflow `33852789095` deployed successfully; public
  page and logo return HTTP 200, the expected content is present and the review
  remains `noindex, nofollow, noarchive`. Janay accepted the consolidated
  Website presentation on 2026-09-10.
- Done, crawler-blocked review deployed and accepted: the 04.09 feedback is reconciled
  with the earlier authorized update packets. Both Use Cases now appear as
  compact side-by-side choices and open independently, so their winding paths
  remain available without forcing the full page length at 150-percent zoom.
  The Concept Clean quotation marks now sit next to the actual opening and
  closing text. Browser checks at 1440, 960 and 390 CSS pixels show no
  horizontal overflow; direct links open the matching story. The calendar is
  retained as a separate gated epic: controlled Coach availability comes first;
  provider-neutral `.ics` is the first external calendar-delivery step, with
  optional Outlook/Graph later. Workflow `34479551380` is green; the public
  page returns HTTP 200, contains both Use-Case controls and Concept Clean, and
  retains `noindex, nofollow, noarchive`.
- Janay confirmed on 2026-09-10 that the current Website refinements look good
  and asked to proceed with the calendar concept from the 27.08 notes. A
  no-data CAL-0 prototype is review-deployed: three bounded months, topic
  filters, text-plus-color event labels, example detail/capacity states and a
  local non-binding seat simulation. It performs no persistence, notification
  or booking. CAL-0.1 uses only already published Coach profile names and still
  contains no real appointment, availability or contact data. Workflow
  `34482731102` is green; the public route and JavaScript bundle pass HTTP,
  `noindex`, example-data and no-network-write checks. ADR 0007 is accepted;
  productive calendar work remains separately gated. Janay accepted the visual concept on
  2026-09-10 and then supplied a bounded CAL-0.1 follow-up: link published Coach
  profiles, show overlapping weekend examples and separate planned group offers
  from individual contact requests. The personal Coach calendar remains a
  protected CAL-1 Webapp workflow; Janay is the initial approval owner through
  an assignable permission, not a hard-coded identity.
- CAL-0.1 is review-deployed and was accepted by Janay as very good on
  2026-09-11. The
  42-file Astro check, 30-page build and browser checks at 1440, 960 and 390
  pixels are green. Workflow `34513388689` and the public smoke confirm HTTP
  200 for calendar/contact/Coach targets, `noindex`, same-day weekend overlap,
  profile links and a bundle without network writes. CAL-D01 through CAL-D08
  and ADR 0007 are now accepted; productive work remains gated by CAL-T01
  through CAL-T06 and all later migration/activation gates.
- A shared Coach-CTA correction keeps long German headings and their final
  punctuation inside the left layout column. All six Coach profiles pass 18
  browser geometry checks at 1440, 960 and 390 pixels without overlap or
  horizontal overflow. Workflow `34515246498` deployed successfully; the
  public Coach page, CSS bundle, heading and `noindex` smoke are green.
- The calendar rules were batched in a non-technical stakeholder handout and
  all accepted by Janay on 11.09. The reconciled quality plan defines RBAC,
  concurrency, privacy, accessibility, calendar compatibility and operations
  evidence. The CAL-1 design adds revision-safe publication, dedicated reviewer
  permission and separate public/private projections without creating SQL.
- The current clean Website production artifact is rebuilt from source
  `5d126cbaec0e`. It contains 51 entries, all required root files, no
  `.env`/`.tmp`, a matching SHA-256 and `deployment_authorized: false`. The new
  release gate verifies 1,137 internal references across 30 HTML files; the
  404 page remains `noindex` and no longer emits a misleading canonical URL.
  Workflow `34582211406` is green; the public review returns HTTP 200 for the
  affected pages with the expected content and crawler blocking.
- Release-candidate source commit `5db1e03` is pushed to `origin/main` and
  contains the reviewed authentication
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
- Completed locally: SB-21 adds a fail-closed encrypted PostgreSQL backup,
  daily integrity/age monitor, provisional 30-daily/12-monthly retention,
  guarded Windows pull and isolated local restore check. VPS encryption accepts
  only an exact public-key fingerprint and rejects private keys; database tools
  use the local Unix socket. Eleven focused tests plus Bash/PowerShell syntax
  pass. The complete dirty-tree verification passed 298 tests with 14 expected
  Staging skips, installed its Wheel in isolation and packaged every operations
  file with zero `.env`/`.tmp` entries. Linux checkout files are pinned to LF.
  The disposable artifact was removed.
- Waiting: Janay's visual/content acceptance of the two company stories,
  remaining profile details and rights where still open; explicit
  qualification and approval before any Coach is assigned to Mediation;
  legal-provider decision, approval of Janay's remaining workflow gates,
  direct-contact delivery inputs and stakeholder acceptance of SB-24. The
  encrypted Wuerzburg off-server rehearsal itself is complete.
- Blocked for live launch: responsible legal entity, final Datenschutz/AGB
  applicability, mailbox response/absence process, content approval and an
  explicitly scheduled production deployment.
- Public contact decision: `competencehub@donner-partner.de`.
- Direct-contact status: the desired same-origin form delivery is specified in
  `docs/requirements/public-contact-request-delivery.md` but remains gated by
  mailbox/sender routing, privacy/retention, abuse protection, monitoring and
  synthetic end-to-end evidence. The website therefore still prepares an
  E-Mail in the local mail client and says so explicitly.
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
- Deployment status: SB-24 feature commit `82c192b` was pushed and manually
  published successfully through Actions run `33502638029`; the review is available at
  `https://dp-manuel.github.io/CompetenceHub/`. Homepage and `/ueber-uns/`
  as well as `/mindforge/` and `/leistungen/` return HTTP 200. The review banner
  and `noindex, nofollow, noarchive` remain active; the published Mindforge page
  contains the Assessment-Center link. Pushes still do not deploy automatically.
  SB-27 source is versioned on `main` but is not part of that review deployment
  or IONOS production.
- Hosting status: EDV confirmed the IONOS webspace as production hosting for
  static/PHP files. Both Competence-Hub subdomains point there and are covered
  by wildcard TLS. Permanent Node/Python services are not possible.
- Static deployment access: Manuel holds the SFTP server, username and password
  for the Website start directory. Credentials remain outside Git and project
  documentation. On 2026-09-02 the server's observed ED25519 fingerprint
  exactly matched the official IONOS fingerprint list. On 2026-09-03 password
  authentication succeeded, but the server closed SFTP because the assigned
  `/htdocs/projektwue` target does not exist.
  The account remains correctly SFTP-only; EDV must repair the path. No Webroot
  inventory or SFTP upload has been performed. Both public subdomains resolve
  to the same IONOS IPv4/IPv6 target and serve the valid wildcard TLS
  certificate, but HTTP and HTTPS currently return a 403 IONOS parking page;
  HTTP-to-HTTPS and alias-to-canonical redirects are not active.
- Independent local Website delivery readiness: the production artifact now
  includes a conservative Apache `.htaccess`, an accessible noindex 404 page
  and fail-closed ZIP checks for `.htaccess`, `404.html` and `index.html`.
  Seven focused tests pass; Astro checks 39 files without diagnostics and
  builds 29 pages. The clean `f7afd3247c10` ZIP is marked `dirty: false`,
  contains all required root files and has SHA-256
  `8378655a120441cf5cd6c6e95709688e6ec3c000e93e2813761f07ed44f7e0a9`.
  Apache behavior remains unclaimed until the corrected IONOS Webroot is
  available for a separately approved rehearsal.
- Database/server status: IONOS MySQL is accessible only from its own webspace
  and is not used by the VPS backend. On 2026-08-07 the VPS was patched and
  rebooted into kernel `6.8.0-137-generic`; Chatbot, Nginx and Fail2ban remained
  healthy. PostgreSQL 16.14 is installed, enabled and bound only to
  `127.0.0.1:5432`. The empty `competence_hub_staging` database uses separate
  owner, migrator and restricted app roles.
- Operational server gates: UFW defaults to deny incoming traffic and exposes
  only 22/80/443; Fail2ban protects SSH. PostgreSQL uses peer authentication on
  local sockets and SCRAM-SHA-256 on loopback TCP. The encrypted exact-copy
  external restore rehearsal succeeded. Productive company or personal data
  remains blocked until production timers/alerts and all Legal, account,
  runtime and Go/No-Go gates close.
- Maintenance timing: the originally planned Saturday window was superseded
  by the approved Friday change on 2026-08-07 before the scheduled crawl. The
  crawl timer remains active for about 15:22 UTC / 17:22 Europe/Berlin.
- Backup decision: no Cloud/Object Storage purchase is currently authorized.
  PostgreSQL remains staging-only with synthetic data. The BitLocker-protected
  D+P medium, encrypted transfer and restore from the exact external copy are
  proven. Backup and monitor timers remain deliberately disabled until a
  production schedule, alert route and operator response are approved.
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
- Active calendar discovery direction: Coaches should later publish rolling three-month
  availability with topic, format, capacity and status. Companies may place
  non-binding seat reservations; an approved threshold triggers an internal
  notification and staff alone release a binding offer/booking. The suggested
  value 25 is provisional. Confirmed appointments should first use provider-
  neutral `.ics` invitations; direct Microsoft Graph/Outlook synchronization
  remains separate. CAL-0.1 is accepted; only the static SB-38 release-quality
  refresh is in the current execution backlog. Productive calendar code is not.
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
  completion. Janay onboarding and production Go/No-Go remain separate gates.
- Former production target: 2026-09-25, now retired. The preferred candidate
  for Onboarding/Go-No-Go is 2026-09-17, with 2026-09-24 as fallback; either
  date moves if EDV, Legal, operations or acceptance evidence is incomplete.
- Schedule health: yellow. Database, migrations, Auth/Outbox,
  company/contact API and the local portal UI are implemented; the expanded
  portal harness has 14/14 Staging evidence and all 17 manual browser checks
  passed and runner cleanup is complete. Productive runtime, account
  onboarding, off-server restore evidence and production
  rollout remain on the critical path. The earlier candidates increase
  schedule pressure but do not relax any production or real-data gate.
- Build evidence: after SB-24, Astro checks 38 files with 0 errors, 0 warnings
  and 0 hints; the static build generates 28 pages, including `/ueber-uns/`.
  Exact 390-pixel browser emulation finds no document overflow on homepage or
  contact. Eight desktop Hub nodes have no geometric collisions, and the Coach
  rail's next control advances the viewport and changes to paused state.
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
- Release-candidate publication: commit `5db1e03` was pushed to `origin/main`.
  Its clean Webapp and Website manifests both report `dirty: false`,
  `deployment_authorized: false` and commit `5db1e030aa39`. This Git push did
  not deploy either artifact.
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

- Review release: Concept Clean name/quote approval is confirmed. GitHub Pages
  review run `33848941115` succeeded; the public review returned HTTP 200,
  contained both company stories and the approved Concept Clean reference, and
  retained `noindex, nofollow, noarchive`. Janay's visual/content acceptance is
  still open. Follow-up run `33851401250` moved the exact quotation into a
  standalone section. Manuel then requested a smaller, scalable customer rail
  with customer logos, collaboration topic and short quotations. The supplied
  Concept Clean logo is now explicitly approved for this bounded use; the
  refreshed review deployment is pending.
- Independent content work: the SEO/GEO Content Inventory, Content-Evidence
  Matrix and Core Page Content Plan for `/`, `/unternehmen`, `/leistungen`,
  `/businesscoaching` and `/mindforge` are complete in `docs/content/`. The next
  first edited stakeholder return has been processed. CP-01/03/05/06 are
  accepted; CP-02/04/07 are partial and CP-08 remains open. Only the approved
  Mindforge distinction was implemented: consultation conversations serve
  private persons and Businesscoaching serves companies. The affected routes
  pass Astro, build, internal-reference and true 390-pixel overflow checks. No
  guide page or unsupported authority claim is authorized.

- Activation inputs: the reviewed 24.08 operator pack is represented by
  `docs/requirements/activation-input-contract-2026-08-24.md`; durable gate
  evidence is indexed in `docs/operations/go-live-evidence-index.md`. The
  private workbook remains outside Git.
- Visual steering board: `docs/requirements/readiness-gate-board-2026-08-28.md`
  consolidates Done/Ready/Waiting/Blocked flow, owners, dates, evidence and the
  completed 28.08. technical checkpoint plus the gate-dependent 17.09./24.09.
  candidates. Technical readiness is green; production is yellow behind named
  gates.
- Current verified implementation checkpoint: commit `58299ae` adds the
  backup notification contract and is pushed to `origin/main`. The Website
  checkpoint `5d126cb` is on `origin/main`; its crawler-blocked review was deployed through
  workflow `34582211406`; public route, content and `noindex` smokes are green.
  The matching clean IONOS artifact contains 51 entries and has SHA-256
  `8056d431...5269d4`. Neither review nor artifact authorizes IONOS production
  or real-data operations.
- SB-22 is complete locally: the Website now has a secret-free SFTP target
  contract, fail-closed artifact preparer and operator runbook. Dirty artifacts,
  wrong hashes/domains, unresolved targets, unverified host keys/Webroots and
  unsafe archives stop. Seventeen combined operations/SFTP tests, the PowerShell
  parser and the 38-file/28-page Astro production build pass. The complete
  Webapp release gate also passes 304 tests with 14 expected Staging skips,
  Dependency/Wheel/install checks and no `.env`/`.tmp` archive entry. The Dirty,
  non-deployable verification artifact was removed and `.tmp/` is now ignored
  by Git. No connection or deployment occurred.
- Recommended next work block: Manuel decides CAL-T01 through CAL-T06 now that
  ADR 0007 and the bounded CAL-1 design are complete. Approval authorizes only
  local migration `0005` preparation, not Staging, accounts, messages, real
  data or production. While that decision is pending, close or explicitly
  defer CP-02/04/07/08. The
  provider-neutral backup-notification contract is complete locally; its live
  adapter remains behind EXT-01, and neither real messages nor VPS timers are
  activated. In parallel, review the EDV response from 2026-09-14 or chase it from
  2026-09-15, then repeat the read-only Webroot inventory. Preferred
  onboarding/Go-No-Go is 17.09. if all gates close, with 24.09. as fallback.
  Real data and
  production activation remain blocked by operational, Legal, account and
  Go/No-Go gates.
- Lead-time radar: EDV input is not expected before 2026-09-14 and should be
  reviewed then or chased from 2026-09-15. Contract and Legal status should be
  requested by 2026-09-18. The 17.09. and 24.09. acceptance candidates should
  be confirmed as early as possible. Janay's mailbox currently has no absence
  cover; Thomas Ross covers only technical emergencies.
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
- Lead-time update: EDV expects no response before 2026-09-14. Review receipt on
  that date and chase from 2026-09-15; no host-specific or live-mail claim is
  made before evidence arrives.
- Rolling delivery horizon: (1) decide CAL-T01 through CAL-T06, (2) close
  residual CP-02/04/07/08, (3) resolve Webroot/DNS/SMTP and the notifier
  adapter, (4) author migration `0005` locally, (5) apply it on Staging only
  after separate approval, (6) implement CAL-1 domain/repository/APIs, (7) add
  Coach/reviewer Portal UI and browser acceptance, and (8) prepare the
  controlled Pilot candidate. Confidence decreases from step 6 onward.
- Closed, review deployed and accepted: the Concept Clean quotation marks are inline with the actual
  quote text, and the 04.09 request for side-by-side, independently collapsible
  Use Cases is implemented. Janay confirmed the result on 2026-09-10.
- Active gates and intended tests are maintained in `PROJECT_PLAN.md` under
  `Delivery Steering`: G-DATA, G-SEC, G-OPS, G-PROD, G-REQ, G-CONTENT,
  G-CONTACT and G-CALENDAR.

## Decisions Needed

- Accept or amend CAL-T01 through CAL-T06: same-Coach overlap, format codes,
  technical bounds, immediate public withdrawal, Pilot retention boundary and
  the additive Admin-assigned `calendar_reviewer` role.
- Which Donner + Partner group company is the legal Competence Hub provider?
- Who may later cover Janay Rappelt's public mailbox during her absence? Until
  then, no public response-time promise applies.
- Who performs the static IONOS deployment and rollback after Thomas Roß's
  production approval?
- How and when is Thomas Ross's confirmed technical break-glass access created
  and tested without sharing an account?
- Which EDV-approved channel delivers Manuel's automatic backup success and
  incident notices?
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
- Which sender/mailbox, retention, privacy text and anti-spam control govern
  direct contact-form delivery?
- Which availability topics, capacities, reservation expiry/cancellation rules
  and staff threshold govern the later Coach calendar?

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
