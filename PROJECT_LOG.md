# Project Log

Newest entries first.

## 2026-09-04 | stakeholder update | Wochenupdate vorbereitet

- Das direkt in Teams einsetzbare Wochenupdate für den Zeitraum 31.08. bis
  04.09.2026 fasst Website- und Kundenstimmenfortschritt, SEO/GEO-Vorbereitung,
  IONOS-Blocker, Qualitätsstand, offene Freigaben und die nächsten fünf Schritte
  ohne interne technische Detailtiefe zusammen.
- Das Update hält Produktionsstatus und Datenschutzgrenze ausdrücklich fest:
  kein IONOS-Produktivstart, kein produktiver Mailversand und keine realen
  Kundendaten.
- Kein wiederverwendbares neues Skill-Learning über die bereits dokumentierte
  Stakeholder- und Projektstatusroutine hinaus.
- Kein Code, Deployment oder Real-Daten-Zugriff in diesem Block.

## 2026-09-04 | feedback/skills | Quote placement and learning loop captured

- Manuel's screenshot confirms that the decorative quotation marks in the
  Concept Clean card are still positioned against the quote container rather
  than the first and final text. The issue is recorded as SB-32 for the next
  frontend pass with desktop and 390-pixel visual acceptance evidence.
- Added a project-level skill-learning checkpoint to `AGENTS.md`: meaningful
  work blocks now include a brief check for durable Manuel preferences,
  repeated friction and evidenced reusable skill improvements. A finding is
  not required when there is no reusable learning.
- Captured the broader canonical-skill proposal in `SKILL_FEEDBACK_LOG.md`.
  The canonical CodexSkills working tree has unrelated active changes, so it
  was not modified or synchronized in this block.
- No frontend code or deployment was performed; only project memory and the
  local skill-learning standard changed.

## 2026-09-04 | frontend/content | Customer-feedback rail prepared

- Replaced the oversized single-customer composition with the requested heading
  `Das waren die Eindrücke von unseren Kunden` and a compact feedback card.
- The card shows the supplied Concept Clean logo, collaboration topic, a short
  exact excerpt with separated opening/closing quotation marks and a link to
  the detailed practice route.
- Added `apps/website/src/data/customerFeedbacks.ts` as the single public data
  source. Additional approved entries can join the horizontal scroll-snap rail;
  controls and automatic advance activate only when at least two entries exist,
  and reduced-motion preference disables smooth scrolling/automatic movement.
- Manuel's explicit request for customer logos extends EV-CC-001 to the supplied
  Concept Clean logo in this bounded context. No additional customer claim was
  added.
- Astro checked 40 files with zero findings and built 29 pages. Desktop and
  exact 390-pixel browser QA show one feedback card, no unnecessary controls
  and `390 px` document/scroll width.
- Commit `3130e0d` was pushed to `origin/main`; review workflow `33852789095`
  completed successfully. Public smoke returned HTTP 200 for both page and
  customer logo, confirmed heading, topic and Concept Clean content, and
  retained `noindex, nofollow, noarchive`. IONOS production remains unchanged.

## 2026-09-04 | frontend/content | Concept Clean feedback made explicit

- Confirmed that the approved Concept Clean quotation was present but visually
  buried at the end of Use Case 02.
- Added a standalone `Kundenfeedback` section before the two use cases. It names
  Concept Clean, states the bounded communication-course context and presents
  the approved quotation as the primary content rather than duplicating it.
- Astro checked 39 files with zero errors, warnings or hints and built 29 pages.
  Browser QA shows the complete section on desktop and `390 px` document width
  with `390 px` scroll width on mobile.
- Converted the CP-01 through CP-08 review handout to send-ready A4 Word and PDF
  files, applied Competence Hub typography/colors and visually checked all four
  PDF pages. No E-Mail was sent automatically.
- Review workflow `33851401250` built and deployed successfully. Public smoke
  returned HTTP 200 and confirmed the `Kundenfeedback` label, Concept Clean
  heading, approved quotation and `noindex, nofollow, noarchive` directive.
  IONOS production is unchanged.

## 2026-09-04 | content/release | Review deployed and Priority A evidence inventoried

- Deployed the approved SB-27 company stories to the crawler-blocked GitHub
  Pages review. Workflow run `33848941115` completed successfully.
- Public smoke at `/CompetenceHub/unternehmen/` returned HTTP 200, contained
  the leadership and Concept Clean stories and retained the expected
  `noindex, nofollow, noarchive` meta directive. IONOS production was not
  changed.
- Added `docs/content/priority-a-content-inventory-2026-09-04.md` and
  `docs/content/priority-a-content-evidence-matrix-2026-09-04.md` for `/`,
  `/unternehmen`, `/leistungen`, `/businesscoaching` and `/mindforge`.
- The baseline records audience, concrete use case, expertise, available
  first-party information, CTA, evidence status, approval boundary, owner gaps
  and claim gaps. It used repository evidence only and did not open private raw
  sources or create new public copy, guides, quotations, cases or statistics.
- `/unternehmen` currently contains the only approved customer authority item:
  the bounded Concept Clean name, quotation and communication-course path.
  The illustrative leadership path remains explicitly non-evidentiary.
- Added `docs/content/priority-a-core-page-content-plan-2026-09-04.md`. It gives
  every route one primary job, evidence and limitation boundaries, internal
  links, CTA, CP-01 through CP-08 decisions and a later verification plan.
- Next independent block: assign content owners and close or explicitly defer
  the bounded stakeholder decisions while EDV remains pending.
- Prepared a German stakeholder review packet with CP-01 through CP-08,
  recommended defaults, compact response format, E-Mail draft, public review
  URL and a return gate. No message was sent automatically.

## 2026-09-04 | content/release | Concept Clean reference approved

- Manuel confirmed publication approval for the prepared Concept Clean company
  name and quotation. The `G-CONTENT` gate for this exact reference is closed.
- The embedded logo remains excluded because logo/asset rights were not part of
  the bounded implementation and no approved original logo asset was needed.
- Manuel authorized a crawler-blocked GitHub-Pages review deployment so Janay
  can inspect both new company stories. IONOS production, direct contact,
  accounts and real-data use remain separately gated.
- Next independent work after the review smoke: SEO/GEO Content Inventory and
  first-party Content-Evidence Matrix for the five priority pages.

## 2026-09-03 | frontend/content | Use-case routes and first customer voice prepared

- Re-read only the explicitly authorized `Quellen/14.08.2026` folder. Janay's
  process feedback remains the internal journey source; the newly supplied
  Concept Clean document provides the first concrete customer feedback.
- Added two stories to `/unternehmen`: a clearly labelled illustrative
  leadership journey and a source-bounded Concept Clean communication-course
  journey. Both use an alternating five-step route on desktop and a linear
  ordered route on mobile.
- Preserved the Concept Clean quotation while adding no unsupported customer,
  result, price, participant, timing or service-level claim. The illustrative
  draft's 48-hour commitment, package/session details, click acceptance, 5/5
  rating and promised improvements were deliberately excluded.
- Added the durable content/evidence note
  `docs/requirements/public-use-cases-and-customer-voice-2026-09-03.md`.
  The embedded customer logo was not copied. Production publication of the
  company name and quotation remains `G-CONTENT`-gated until customer-side
  release evidence is retained.
- Verification: Astro checks 39 files with zero errors, warnings or hints and
  builds 29 pages. Desktop screenshots show the intended winding route. An
  exact Edge DevTools 390-pixel check reports document width `390`, both story
  widths within `18..372`, and `0 px` overflow for both stories and all ten
  step bodies. No interactive or motion dependency was introduced.
- The temporary preview and browser-debug processes were stopped; ports `4321`
  and `9333` are free. No source document, logo, credential, production
  deployment or real-data operation is included. The bounded Website/content
  change and project memory are committed and pushed together; a push does not
  trigger the manual review workflow.

## 2026-09-03 | website/release | Local IONOS Apache artifact completed

- Added a production `.htaccess` that prepares HTTP/alias redirects to the
  canonical HTTPS domain, maps the static 404 page and sets bounded security
  headers. HSTS and a script/style-restricting CSP remain deliberately gated
  until every production host is proven.
- Added an accessible, indexierungsfreie 404 page with working Start and
  contact paths for production and the GitHub-Pages review base.
- Replaced `Compress-Archive` in the Website release builder with the .NET ZIP
  API and fail-closed source/archive checks for `.htaccess`, `404.html` and
  `index.html`, avoiding platform-dependent omission of point files.
- Verification: seven focused Website-SFTP/Apache tests pass; Astro checks 39
  files with zero errors, warnings or hints and builds 29 pages. A clean
  release build from `f7afd3247c10` is marked `dirty: false`, contains
  `.htaccess`, `404.html` and `index.html`, and has SHA-256
  `8378655a120441cf5cd6c6e95709688e6ec3c000e93e2813761f07ed44f7e0a9`.
- No IONOS connection, upload, Apache activation, production deployment or
  real-data use occurred. Next recommended block remains the read-only Webroot
  inventory after EDV repairs the missing SFTP home.

## 2026-09-03 | operations/diagnosis | IONOS SFTP start directory blocks inventory

- Manuel's real SFTP account authenticated successfully by password against the
  independently verified IONOS ED25519 host key. The server accepted the SFTP
  subsystem and then immediately sent EOF.
- A separate read-only SSH diagnosis authenticated successfully and identified
  the exact server-side cause: the assigned IONOS home targeting
  `/htdocs/projektwue` does not exist. The
  account is intentionally restricted by `rssh` to SFTP; that restriction must
  remain in place.
- Prepared `docs/architecture/edv-sftp-webroot-fix-request-2026-09-03.md` asking
  EDV to repair/reassign the start directory and confirm both domains' exact
  Document Root. No credential is included.
- Public read-only checks confirm that both subdomains resolve to the same
  IONOS IPv4/IPv6 target and serve the valid `*.donner-partner.de` certificate.
  HTTP and HTTPS nevertheless return a 403 IONOS parking page on both names;
  neither HTTP-to-HTTPS nor alias-to-canonical redirect is active. The EDV
  request now includes these findings and confirms
  `competencehub@donner-partner.de` with Frau Janay Rappelt as mailbox owner.
- Manuel sent the consolidated correction request to EDV on 2026-09-03.
- No directory listing, download, upload, deletion, deployment or real-data use
  occurred. SB-25 now waits externally; after EDV correction, repeat only
  `pwd` and `ls -la` before designing any remote change.

## 2026-09-02 | operations/security | IONOS SFTP host key independently verified

- Probed the approved private IONOS SFTP target on port `22` without real
  username, password or user-key authentication. The server presented ED25519 fingerprint
  `SHA256:1gx2w8Rtv3wCgi7Jh8myf/KVd72cRQbow03UP8P095Q`.
- The fingerprint exactly matches the official IONOS Webhosting SSH
  fingerprint overview. The public host-key evidence, compatibility note,
  read-only commands and stop rules are documented in
  `docs/architecture/website-sftp-read-only-inventory-2026-09-02.md`.
- The Windows `ssh-keyscan` could not negotiate the server's first modern KEX.
  A normal isolated OpenSSH probe used secure `curve25519-sha256`, disabled
  password and public-key authentication and wrote only an untracked temporary
  host-key observation.
- Verification: `git diff --check` passes and all six focused Website-SFTP
  rehearsal tests pass. The first sandboxed Pytest attempts were blocked only
  by Windows Temp-directory ACLs; the approved identical run outside that
  restriction completed successfully.
- No credential login, file inventory, download, upload, deletion, deployment
  or real-data use occurred. Next recommended block: Manuel performs the
  interactive `pwd` and `ls -la` inventory; then classify every remote path and
  validate the private SFTP target contract.

## 2026-09-01 | release/deployment | SB-24 review published and verified

- Committed the approved website, requirements and project-state scope as
  `82c192b` (`Refine website feedback and Mindforge navigation`) and pushed it
  to `origin/main` without including `Quellen`, credentials or temporary QA.
- Manually triggered the crawler-blocked GitHub-Pages review workflow. Actions
  run `33502638029` completed both build and deployment successfully.
- Public verification: `/`, `/mindforge/` and `/leistungen/` return HTTP 200;
  each retains `noindex, nofollow, noarchive`; Mindforge contains the published
  Assessment-Center link. Pushes remain non-deploying by default.
- This is a review deployment only. IONOS production, direct contact delivery,
  calendar implementation, accounts and real data remain separately gated.
- Next recommended block: trusted read-only SFTP Webroot inventory, followed by
  host-specific EDV configuration no earlier than the expected 2026-09-14 input.

## 2026-09-01 | frontend/requirements/steering | Feedback packet 27.08 consolidated locally

- Follow-up review fixed five concrete frontend regressions: the Coach rail no
  longer pauses indefinitely under a resting pointer; open FAQ cards no longer
  stretch their closed neighbors; CTA and process-card clearances are explicit;
  Mindforge exposes Assessment Center as a fourth clickable Hero node; and the
  therapy boundary uses a controlled two-line heading without an orphaned word.
- Real-browser evidence at 1440 and 390 pixels: the Coach viewport moved from
  0 to 270 pixels after 7.2 seconds with `paused=false`; the open FAQ measured
  214 pixels while its closed neighbor remained 98 pixels; process clearance is
  30 pixels; CTA clearance is 20 pixels; four Mindforge nodes have zero
  collisions and no tested page has horizontal overflow.
- Manuel explicitly authorized commit, push and review deployment after these
  corrections. Production infrastructure, direct form delivery, calendar
  implementation and real-data use remain outside that authorization.
- Reviewed only the explicitly authorized `Quellen/27.08.2026` packet; private
  source files remain outside Git and temporary extraction is removed after QA.
- Grouped Beratung under Mindforge, consolidated the public service navigation,
  separated qualification-gated Supervision/Mediation and balanced the four
  principal service cards in a 2x2 layout.
- Refined the Living Hub: all surrounding nodes remain links, the asymmetric
  layout has no desktop collisions, subtle node pulses respect reduced motion,
  and Beratung replaces the former health node. The Coach rail now provides
  previous, pause/play and next controls instead of relying on an opaque loop.
- Updated the contact form semantics: Name, E-Mail and Thema are marked
  required; Anliegen is optional. Direct same-origin delivery is specified in
  `docs/requirements/public-contact-request-delivery.md` but not activated
  without mail/privacy/abuse/operations evidence; the current mail-client
  handoff remains honestly described.
- Expanded the future-system backlog for rolling three-month Coach
  availability, topic/format/capacity status, non-binding seat reservations,
  staff release, concurrent reservations and provider-neutral calendar
  invitations. The proposed threshold 25 remains explicitly provisional.
- Verification: Astro check/build reports 38 files with zero diagnostics and
  28 generated pages; exact 390-pixel browser emulation shows no page overflow;
  eight desktop Hub nodes have zero collisions; manual Coach-next changes the
  viewport and pauses automatic movement.
- No commit, push, deployment, direct message delivery, calendar implementation
  or real-data use occurred. Next recommended block is stakeholder browser
  review, followed by separately approved versioning.

## 2026-08-25 | steering/closeout | Pilot rebaselined to post-vacation October window

- Manuel retired the former 2026-09-25 production deadline. The current
  planning assumption is a first small controlled start no earlier than the
  second half of October after his return; the exact date remains open.
- Current plan, status, visual gate board, historical cutline warning and the
  production release plan were reconciled. Completed technical readiness and
  SB-23 external restore evidence are green; stale claims that no external
  restore existed or that the release refresh remained next were removed.
- Open critical path: trusted read-only SFTP inventory; EDV DNS/TLS/SMTP input
  from 2026-09-14 onward; production backup/monitor schedule and alert route;
  contract/Legal/mailbox closure; named-user onboarding; Thomas Ross Go/No-Go.
- Calendar delivery remains a deferred product epic and does not enter current
  WIP. No deployment, account creation, production timer enablement or real-data
  use occurred.

## 2026-08-25 | requirements/steering | Provider-neutral Coach calendar request captured

- Janay requested a future workflow in which confirmed appointments reach the
  assigned Coach's calendar. Manuel noted that Coaches may use Outlook or other
  calendar products and that the capability is not urgent.
- The future-system backlog now defines standards-compliant `.ics` invitations
  as the provider-neutral first increment. Direct Microsoft Graph/Outlook sync
  and availability lookup remain later, separately gated integration options.
- Future evidence must cover Outlook and at least one non-Outlook client,
  stable update/cancellation behavior, correct time zones, visible delivery
  failure and data minimization. No implementation, deployment or real-data use
  occurred.

## 2026-08-25 | operations/steering | SB-23 cleanup closed and EDV lead time rebaselined

- Manuel explicitly approved deletion of only the temporary owner-only export
  `/home/manuel/competence-hub-backup-export/2026-08-25`. The first remote
  command was stopped locally by an unintended PowerShell substitution before
  any deletion. The corrected literal-path command verified both resolved paths,
  removed exactly the approved dated directory and confirmed its absence.
- The original monitored VPS backup was not touched. Backup and monitor units
  still report `Result=success` and `ExecMainStatus=0`; Chatbot, Nginx,
  Fail2ban and PostgreSQL remain active.
- The external BitLocker `D:` copy remains present and all three manifest
  checks pass after remote cleanup. SB-23 has no remaining cleanup action.
- EDV input for App-DNS/TLS/SMTP is now expected no earlier than 2026-09-14.
  EXT-01 and dependent host-specific/live-mail work were rebaselined rather
  than silently treated as late. The next independent block is a refreshed full
  technical-readiness/release check; no production activation is implied.
- Clean commit `70e92ba` was used for the refreshed release evidence. The full
  Webapp gate passed 305 tests with 14 expected opt-in Staging skips, dependency
  checks, bytecode compilation, Wheel build, isolated installation and
  fail-closed smoke. The 33-entry ZIP includes the guarded Docker restore tool,
  contains no `.env`/`.tmp` entry and matches SHA-256
  `1db5418713625350a2fdc4ce779a32814227d1de5187d674d6726911deabe766`.
- The Website production build also passed: Astro checked 38 files with zero
  errors, warnings or hints and generated 28 pages. Deployment was not
  performed. The 2026-08-28 technical-readiness checkpoint is therefore green
  for local/rehearsal scope; production remains yellow/replanned behind the
  external gates.
- No deployment or real-data use occurred. Commit/push for the final readiness
  evidence remain separate.

## 2026-08-25 | operations/steering | Activation pack reviewed and SB-23 precheck started

- The explicitly released 24.08 activation pack was reviewed as untrusted
  operator input and converted into a versioned, secret-free activation input
  contract plus a compact Go-Live Evidence Index. The private workbook remains
  in `Quellen` and was not copied into Git.
- Git was clean and already synchronized with `origin/main`; no pull was
  required. The current remote checkpoint is `7dcaf6d`.
- The supplied `D:` USB candidate is healthy, removable, almost empty and about
  2 GB. The initial check found no BitLocker protection. Manuel then enabled
  BitLocker To Go interactively without exposing the password. The final status
  is fully encrypted, protection on, Aes128, 100 percent and unlocked. No
  backup, secret or real data was written to the medium.
- A durable SB-23 Wuerzburg execution note now preserves the interactive
  BitLocker command, secret-handling boundary, GPG/key-custody gate and the
  later exact-copy transfer/restore sequence. The focused operations package
  passes all 11 tests. BitLocker management, SSH and SCP are present. Gpg4win
  5.1.0 was installed through Winget with a verified installer hash and exposes
  GnuPG 2.5.21. No key has been generated yet because encrypted local key
  storage and recovery ownership must be confirmed first.
- The former 2026-09-25 production deadline is expected to move. It is now
  marked for rebaseline without inventing a replacement date. Technical,
  security, legal, operations and real-data gates remain unchanged.
- The local `C:` restore environment is also fully BitLocker-encrypted
  (`XtsAes128`, protection on, 100 percent). The USB medium will be stored in
  the safe and Janay Rappelt is the named emergency/recovery owner. Actual
  recovery-code/passphrase escrow remains to be confirmed; no recovery value
  or private key entered project files or chat.
- A passphrase-protected RSA-4096 backup key was created in the encrypted local
  GPG home. Its public fingerprint and export hash were verified, the public
  key was exported to the BitLocker USB and no private-key material was found
  there. An initially misdirected metadata check created two empty GPG files in
  the user root; both were identified by creation time and removed immediately,
  then the corrected check passed without residue.
- Manuel confirmed both BitLocker protector types and the safe storage of the
  Recovery code and GPG passphrase without transmitting either secret. The
  SB-23 target/key/custody precheck is complete; only public-key handoff and the
  native synthetic backup/transfer/restore evidence remain.
- SSH key authentication to the approved VPS succeeded without a password
  prompt. Only the verified public key was copied to Manuel's home; its remote
  SHA-256, size, owner and mode match the local evidence. The eight secret-free
  SB-21 files were staged in a new owner-only directory. Every local/remote
  SHA-256 pair matches. Nothing was installed, enabled or executed as root.
- Manuel installed the staged package under the reviewed root/postgres paths.
  The VPS GPG home contains the exact public fingerprint and no reported
  private key. Native unit verification passed, both timers remain disabled
  and Chatbot, Nginx, Fail2ban and PostgreSQL are active. At this checkpoint no
  backup had run yet.
- The first manual backup attempt failed closed before publication: the script
  removed write permission from its work directory before moving it into the
  daily retention directory. A minimal `postgres` rename probe reproduced the
  same `Permission denied` outside systemd; ownership, ext4 mount options,
  systemd write paths and the kernel log ruled out the surrounding platform.
  Cleanup left no plaintext or partial backup set, only the expected lock and
  empty retention directories.
- The publication order is corrected locally: the complete work directory is
  moved first and the final directory is then made read-only, with targeted
  cleanup if that final permission step fails. The focused operations package
  passes all 11 tests, including updated regression coverage. The exact fixed
  script is staged, not installed, as
  `/home/manuel/competence-hub-backup-install-20260825/competence-hub-postgres-backup.20260825-fix1`;
  local and remote SHA-256 are both
  `c8b6edcc7d79a077da8e2a8231e6756641873d5bb65c9114fb1327600672d1cb`,
  and remote `bash -n` passes.
- After installing that fix, the native backup unit completed successfully and
  published read-only daily and monthly encrypted sets. The monitor then failed
  closed at its OpenPGP packet validation. A native probe confirmed the payload
  is valid and that GnuPG 2.4.4 returns success when packet inspection uses
  `--list-only`; the unrelated direct-run working-directory warning is avoided
  by starting operator probes from `/`.
- The monitor now uses `--no-tty --list-only --list-packets`. All 11 focused
  operations tests pass. The exact monitor fix is staged, not installed, as
  `/home/manuel/competence-hub-backup-install-20260825/competence-hub-postgres-backup-monitor.20260825-fix2`;
  local and remote SHA-256 are both
  `335da9998893240c7a284334f8a075d4d9f75776ce558d476e87522ed7a60bdd`,
  and remote `bash -n` passes.
- Manuel installed Fix 2 and reran only the monitor. It completed successfully
  with `Result=success`, `ExecMainStatus=0` and identified the 2026-08-25 set as
  complete, encrypted and 307 seconds old. Chatbot, Nginx, Fail2ban and
  PostgreSQL all remained active. Backup and monitor evidence are now green;
  guarded external transfer and exact-copy restore remain open.
- The completed set was staged in the owner-only VPS export path. Its three
  manifest checks passed and the inventory contained only two encrypted
  payloads plus `METADATA`, `SHA256SUMS` and `COMPLETE`.
- The guarded pull created and independently verified
  `D:\CompetenceHub\competence-hub-backups\2026-08-25` on the previously
  evidenced BitLocker To Go target. It refused overwrite by contract, verified
  all three checksums, required exactly two `.gpg` payloads and found no
  plaintext backup material. The temporary remote export was deliberately not
  deleted before restore acceptance.
- Local Docker Desktop is installed and was started for restore-environment
  discovery, but no PostgreSQL image is present. Downloading the official
  image was blocked by the project's no-external-provider boundary and did not
  occur. Exact-copy restore now waits for an explicit choice between that
  one-time dependency download and an internal synthetic VPS restore path.
- Manuel explicitly approved the one-time official Docker Hub download for
  `postgres:16-bookworm`; no project or backup data was sent. The local image is
  pinned as
  `postgres@sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825`.
- Restore from the exact verified `D:` copy passed twice: first as the supervised
  proof and then through the new reusable guarded Windows/Docker restore tool.
  The isolated networkless PostgreSQL 16 instance contained one application
  schema and 24 application tables; the synthetic snapshot contained zero
  portal users. Cleanup left zero restore containers, zero temporary restore
  directories and zero plaintext dump files. All four VPS services remained
  active.
- `restore-competence-hub-backup-docker.ps1` now preserves the proven procedure:
  protected external source and explicit restore confirmations, repository
  separation, reparse/plaintext rejection, exact checksums, digest pinning,
  `--pull never`, `--network none`, local GPG pinentry, isolated restore and
  `finally` cleanup. The runbook documents its use and 12/12 focused operations
  tests plus PowerShell parsing pass.
- SB-23 and the synthetic G-BACKUP rehearsal are complete. This evidence closes
  the external-copy/restore prerequisite only; real data remains blocked by
  production scheduling/monitoring, Legal, named accounts and Go/No-Go.
- No deployment, external transfer, real-data use, production change, commit
  or push occurred in this block.

## 2026-08-21 | handoff | Week closed with colleague update

- The colleague-facing update for 17.08.-21.08. summarizes the accepted pilot
  portal, company/contact slice, release packages, operations rehearsals,
  quality evidence, external gates and next-week focus without exposing
  credentials or internal operational commands.
- Milestone signal remains yellow: technical readiness by 28.08. and controlled
  production by 25.09. are achievable, but depend on Wuerzburg restore evidence,
  EDV, contracts, Legal, named accounts and stakeholder Go/No-Go.
- The week closes with no production deployment, real-data use or external mail
  delivery. Next pull remains SB-23 in Wuerzburg or earlier EXT-01 processing.

## 2026-08-21 | steering | Visual readiness gate board consolidated

- A compact Kanban-style gate board now consolidates Done, Ready, Waiting and
  Blocked work for the 28.08. technical cutline and 25.09. production target.
- Every gate names its owner, latest useful date, acceptance evidence and
  effect if it remains open. The pull rule prioritizes Wuerzburg backup/restore,
  an earlier EDV response or a separately approved read-only SFTP inventory.
- Both milestones are yellow: achievable on current technical evidence, but
  dependent on backup restore, EDV, Legal, contracts, named accounts and
  stakeholder Go/No-Go. No budget baseline is documented.
- No implementation, connection, deployment, real-data use, commit or push
  occurred in this steering-only block.

## 2026-08-21 | git | Operations rehearsal package committed and pushed

- Commit `9210ea1` (`Prepare backup and SFTP release rehearsals`) was pushed
  successfully to `origin/main` without branch divergence.
- The commit contains the SB-21 PostgreSQL backup/restore package, the SB-22
  guarded Website SFTP rehearsal package, their tests/runbooks, project-memory
  reconciliation and the explicit `.tmp/` Git exclusion.
- Verification before commit: 304 local Webapp tests passed with 14 expected
  opt-in Staging skips; Dependency/Wheel/install checks, 17 focused operations/
  SFTP tests, PowerShell parsing and the 38-file/28-page Astro production build
  were green.
- No GitHub Pages, SFTP, VPS, SMTP, DNS or production deployment was triggered.
  No credentials or real data were read, committed or transferred.

## 2026-08-21 | release/operations | Website SFTP rehearsal package prepared

- SB-22 is complete locally. A secret-free target contract, local artifact
  preparer and operator runbook now separate checksum/archive validation,
  host-key and remote-root confirmation, Webspace inventory, mandatory
  backup-before-replace, upload, smoke and rollback into explicit gates.
- The preparer never invokes an SFTP client. It rejects Dirty builds, wrong
  domains or hashes, unresolved placeholders, unverified host keys/Webroots,
  path traversal, case-colliding ZIP entries, symlinks and oversized archives.
  Its generated plan keeps remote inventory, backup, change authorization,
  legal release, production smoke and rollback marked incomplete.
- Seventeen combined operations/SFTP tests pass, including five behavioral
  PowerShell cases. The PowerShell parser is green. The Astro check reports 38
  files without diagnostics and the production build creates 28 pages. The
  first sandboxed Vite run hit the known Windows `spawn EPERM`; the approved
  rerun completed successfully.
- The final combined Webapp release gate reports 304 passed and 14 expected
  opt-in Staging skips. Dependency checks, Wheel build and isolated install
  pass. The 32-entry verification archive was correctly marked Dirty and
  `deployment_authorized: false`, contained no `.env`/`.tmp` entry and was
  removed after inspection. `.tmp/` is now explicitly ignored by Git.
- No SFTP connection, upload, Webspace read, credential access, commit, push,
  deployment or real-data use occurred. The next recommended block is the
  native Wuerzburg off-server backup and restore rehearsal in the week of
  2026-08-24.

## 2026-08-21 | steering | Wuerzburg gate moved to next-week window

- Manuel will next be at the controlled Wuerzburg workstation during the week
  of 2026-08-24. EXT-05 therefore remains prepared but is intentionally not
  executed today; its exact rehearsal slot is due by 2026-08-28.
- SB-22 is the independent current recommendation: prepare the Website SFTP
  release, remote-backup and rollback package locally without credentials,
  connection, upload or deployment.
- EDV response, contract confirmation and appointment requests continue on the
  dated external-dependency radar. No commit, push or deployment occurred.

## 2026-08-21 | operations/steering | Backup package and lead-time radar

- EDV, contracts, legal review, Janay/Thomas appointments, mailbox operations
  and the Wuerzburg backup target now have request, chase, escalation and latest
  useful dates in `PROJECT_PLAN.md`.
- SB-21 is complete locally: encrypted daily/monthly PostgreSQL backup,
  freshness/integrity monitor, guarded Windows off-server pull, isolated
  restore check, hardened systemd/config templates and an executable gate
  runbook are versioned. The VPS is restricted to a public GPG key and local
  PostgreSQL socket; the private key stays on the restore environment.
- Eleven focused operations tests and Bash/PowerShell syntax pass. The full
  local release gate reports 298 passed and 14 expected Staging skips, clean
  dependency/compile/Wheel checks, all required files in the archive and zero
  `.env`/`.tmp` entries. Linux deployment files are pinned to LF line endings.
  The dirty verification artifact was removed after inspection and is not
  deployable evidence.
- A reusable visual Kanban/dependency-radar concept for Manuel and future team
  use was recorded in `SKILL_FEEDBACK_LOG.md`; CodexSkills itself was not
  changed in this block.
- No commit, push, VPS change, external transfer, real-data use or deployment
  occurred. EXT-05 still requires the protected Wuerzburg target, public-key
  handoff and a supervised rehearsal/restore window.

## 2026-08-21 | release/git | Release Candidate committed and pushed

- Commit `5db1e03` (`Prepare Competence Hub production release candidate`) ist
  erfolgreich nach `origin/main` gepusht worden.
- Der finale Clean-Source-Build gegen `5db1e03` meldet fuer Webapp und Website
  `dirty: false` und `deployment_authorized: false`. Das Webapp-Paket bestand
  287 lokale Tests, 14 erwartete Staging-Skips, Dependency-/Compile-/Wheel-
  und Fail-closed-Pruefungen; das Website-Paket pruefte 38 Astro-Dateien ohne
  Diagnose und baute 28 Seiten.
- Beide Archive enthalten weder `.env` noch `.tmp`. Lokal bleibt nur der
  gesperrte `.tmp/`-Ordner ungetrackt.
- Der Push hat kein GitHub-Pages-, SFTP-, VPS-, SMTP- oder sonstiges Deployment
  ausgeloest. Naechster Block bleibt die hostbezogene DNS/TLS/Nginx/SMTP-
  Validierung nach der EDV-Antwort.

## 2026-08-21 | review/release | Release Candidate fachlich und technisch geprueft

- Der gebuendelte Review von Website, Portal, SMTP-Worker und Releasepaket hat
  keine offenen hohen oder kritischen Befunde. Account-Action-Links muessen
  jetzt exakt auf dem erlaubten HTTPS-Portal-Origin liegen.
- Eine gemeinsame strikte E-Mail-Pruefung und eine zweite Schutzschicht im
  SMTP-Adapter verhindern Verteiler-/Mehrfachempfaengerwerte. Ein fehlerhafter
  Outbox-Empfaenger wird kontrolliert als Zustellfehler behandelt, statt den
  Worker unkontrolliert zu beenden.
- Der Nginx-Entwurf leitet HTTP fest auf den freigegebenen App-Host um, blendet
  die Serverversion aus und setzt HSTS am HTTPS-VHost. Tokens bleiben im URL-
  Fragment, werden sofort aus der Browserzeile entfernt und nicht gespeichert.
- Vollstaendige Verifikation: `pip check`, 287 lokale Tests bestanden, 14
  tunnelpflichtige Staging-Tests erwartungsgemaess uebersprungen, Compileall,
  JavaScript-Syntax und PowerShell-Parser sind gruen. Produktion und GitHub-
  Review pruefen 38 Astro-Dateien ohne Diagnose und bauen je 28 Seiten.
- Zwei vollstaendige post-review Webapp-Builds waren bytegleich
  (`f444a36c0ef1e51e4fd208f85621d15d54ccde9535c24927eaaced76ab5d2f9f`).
  Webapp- und Website-ZIPs enthielten weder `.env` noch `.tmp`; alle
  Testartefakte wurden danach entfernt.
- Nach der Commit-Freigabe bestand auch der Clean-Source-Webapp-Build: nur der
  gesperrte `.tmp/`-Ordner blieb ungetrackt, das Manifest meldete
  `dirty: false`, und Wheel-Installation sowie Fail-closed-Smokes waren gruen.
  SB-20 ist damit lokal abgeschlossen.
- Die App-DNS-/SMTP-Anfrage wurde am 21.08.2026 an die EDV versendet; Antwort
  und externe Werte stehen aus. Keine SMTP-Verbindung, E-Mail, DNS-Aenderung,
  VPS-Aktivierung, SFTP-Uebertragung, Echtdatenverwendung, Commit, Push oder
  Deployment erfolgte.

## 2026-08-21 | release/operations | Reproduzierbares Webapp-Paket vorbereitet

- `scripts/build-webapp-release.ps1` prueft den exakten Runtime-Lock,
  `pip check`, die lokale Suite und Compileall, baut das Anwendungs-Wheel,
  installiert es isoliert und prueft das Fail-closed-Verhalten von API und
  Worker ohne Konfiguration.
- Das erzeugte ZIP enthaelt Wheel, Migrationen, Rollback-Smokes,
  Deploymentvorlagen, Runbooks und ein internes SHA-256-Dateiinventar. Ein
  externes JSON-Manifest und eine `sha256sum`-kompatible Pruefdatei begleiten
  das Artefakt. Zwei vollstaendige Wiederholungsbuilds erzeugten bytegleich
  denselben ZIP-Hash.
- Der Clean-Worktree-Guard beruecksichtigt jetzt auch ungetrackte Dateien und
  nimmt ausschliesslich den gesperrten `.tmp/`-Ordner aus. Damit kann neuer,
  nicht versionierter Code nicht als sauberer Release erscheinen.
- Die systemd-Vorlagen verwenden ein releasebezogenes Virtual Environment
  hinter `/opt/competence-hub/current`; das Linux-Runbook beschreibt
  Installation, externe Konfiguration, Migration, native Validierung, Smoke,
  Stop-Kriterien und atomaren Rollback.
- Ein versandfertiger EDV-Entwurf fragt App-DNS, TLS, SMTP/TLS,
  Absenderfreigabe, SPF/DKIM/DMARC und Adressrouting ab, ohne ein Passwort per
  E-Mail anzufordern.
- Verifikation: 274 lokale Tests bestanden, 14 opt-in Staging-Tests wurden
  erwartungsgemaess uebersprungen; Dependency-, Compile-, Installations-,
  Manifest-, Ausschluss-, Clean-Guard- und Reproduzierbarkeitspruefung sind
  gruen. Native systemd-/Nginx-Pruefung bleibt fuer Linux vorgesehen.
- Keine SMTP-Verbindung, E-Mail, DNS-Aenderung, VPS-Aktivierung, SFTP-
  Uebertragung, Echtdatenverwendung, Commit, Push oder Deployment erfolgte.

## 2026-08-21 | staging/acceptance | Vollstaendiges Onboarding 14/14 bestanden

- Der korrigierte isolierte Staging-Harness bestand alle 14 Pfade in 151.77
  Sekunden. Der neue durchgehende Pfad prueft Admin-Einladung,
  verschluesselte Outbox, Capture-Zustellung, einmalige Tokenannahme,
  Passwortvergabe, TOTP-Einrichtung, Recovery-Codes und aktive Sitzung.
- Das Cleanup hinterliess jeweils null Nutzer, Sessions, Outbox- und
  Auditzeilen. Damit existieren keine synthetischen Testreste.
- `dp-chatbot`, Nginx, Fail2ban und PostgreSQL blieben aktiv. Der gemeinsame
  VPS-Betrieb wurde durch den Test nicht beeintraechtigt.
- SB-19 ist abgeschlossen. Naechster Implementierungsblock ist das
  reproduzierbare Backend-/Worker-Releaseartefakt mit Manifest, Hash und
  exaktem Installations-/Smoke-/Rollback-Runbook. Kein SMTP-Versand,
  Deployment, reales Konto, Echtdatum, Commit oder Push erfolgte.

## 2026-08-21 | staging/debug | Onboarding-Harness auf PostgreSQL-Uhr umgestellt

- Der erste erweiterte Staging-Lauf bestand 13/14 Pfade. Der neue Onboarding-
  Pfad erreichte die TOTP-Bestaetigung, scheiterte aber beim Session-Insert:
  seine feste Testzeit vom 14.08. lag vor dem realen PostgreSQL-`created_at`
  vom 21.08. und verletzte dadurch korrekt die Expiry-Constraint.
- Der Harness bezieht seine Referenzzeit nun direkt ueber
  `clock_timestamp()` aus PostgreSQL und arbeitet mit einem kontrollierten
  Fuenf-Minuten-Vorlauf, analog zum bereits bewaehrten MFA-Staging-Test.
- Die vollstaendige lokale Suite bleibt mit 274 Passes und 14 erwarteten
  opt-in Staging-Skips gruen; Compileall und `pip check` bestehen. Der
  kontrollierte 14/14-Wiederholungslauf steht aus.
- Kein Schema-, Migrations-, Produktivdaten-, Mail- oder Deploymentfehler lag
  vor; der Fehler war auf die Testuhr begrenzt.

## 2026-08-21 | webapp/runtime | Einladungs- und Reset-Slice lokal geschlossen

- Die konfigurierte FastAPI-Runtime verdrahtet jetzt den PostgreSQL-Account-
  Lifecycle, die externe kompromittierte-Passwort-Fingerprintquelle und die
  AES-GCM-verschluesselte Token-Outbox. Getrennte Idempotenz-/Outbox-Schluessel
  sind Pflicht; fehlende oder unsichere Werte stoppen den Start.
- Das Portal nimmt Einladungs- und Passwort-Reset-Links an, entfernt Tokens
  sofort aus der Adresszeile, speichert sie nicht im Browser und fuehrt eine
  Einladung direkt in die bestehende MFA-Einrichtung. Admins koennen genau die
  Pilotrolle `internal` idempotent per persoenlicher Arbeits-E-Mail einladen.
- Ein providerneutraler SMTP-Adapter erzwingt Authentifizierung sowie STARTTLS
  oder implizites TLS. Ein One-Shot-Outbox-Worker und geheimnisfreie systemd-
  Service-/Timerbeispiele sind vorbereitet; ohne externe SMTP-Werte laeuft
  kein Versand.
- Die komplette lokale Suite besteht mit 274 Tests und 14 erwarteten opt-in
  Staging-Skips. Compileall, `pip check` und JavaScript-Syntax sind gruen.
- Kein SMTP-Kontakt, E-Mail-Versand, reales Konto, Echtdatum, SFTP-Upload,
  VPS-Eingriff, Deployment, Commit oder Push erfolgte.
- Naechster Block ist der durchgehende synthetische Onboarding-Nachweis von
  Admin-Einladung bis MFA/Portal, zuerst lokal mit Capture-Mail und danach auf
  isoliertem Staging mit Null-Rueckstaenden.
- Der vorhandene isolierte Outbox-Staging-Test wurde bereits bis
  Einladungsannahme, Replay-Ablehnung, Passwort, TOTP, Recovery-Codes und aktive
  Sitzung erweitert. Lokale Sammlung/Compile sind sauber; der echte Lauf mit
  SSH-Tunnel und anschliessender Service-/Null-Rueckstands-Pruefung steht aus.

## 2026-08-21 | release/website | Erstes Produktionspaket lokal vorbereitet

- Die kanonische Website-Domain ist in Astro gesetzt. Jede Seite liefert eine
  kanonische URL und `og:url`; der GitHub-Reviewbuild entfernt seinen Basispfad
  korrekt und verweist ebenfalls auf die Produktionsdomain.
- `robots.txt` sperrt im Review alle Crawler. Produktion erlaubt Hauptinhalte,
  sperrt Login/Archiv/Prototyp und verweist auf eine aus den Coachdaten und
  Kernrouten erzeugte Sitemap.
- Ein PowerShell-Builder erstellt aus einem sauberen Commit ein ZIP plus JSON-
  Manifest, Commit-ID und SHA-256. Dirty Builds werden standardmaessig
  abgewiesen und sind nur fuer isolierte Tests explizit markierbar. Der
  Temp-Test bestaetigte je ein Artefakt/Manifest, passenden Hash und Cleanup.
- Geheimnisfreie Beispielvorlagen fuer einen dedizierten FastAPI-systemd-
  Dienst und den Nginx-Reverse-Proxy sind angelegt. Der Mail-Worker fehlt
  absichtlich, bis sein Einstiegspunkt und SMTP-Vertrag implementiert sind.
- Produktions- und Reviewbuild pruefen 38 Dateien ohne Diagnosen und erzeugen
  28 Seiten plus `robots.txt` und Sitemap. Kein SFTP-Upload, VPS-Eingriff,
  E-Mail-Versand, Konto, Echtdatum, Commit oder Push erfolgte.
- ADR-0005-Abgleich zeigte den naechsten kritischen Slice: Runtime-Lifecycle,
  SMTP-Worker, sichere Links und Portal-Annahme-/Resetoberflaeche muessen als
  durchgehender Einladungsweg umgesetzt werden; SMTP-Werte bleiben bis zur
  EDV-Antwort fail-closed.

## 2026-08-21 | planning/operations | Termine, Mailwege und SFTP-Richtung konkretisiert

- Der 28.08. ist kein harter Produktivtermin mehr, sondern der
  Technical-Readiness-Meilenstein nach erwarteter Vertragsfertigstellung.
  Janays Onboarding und Thomas Ross' Go/No-Go folgen danach; der harte Termin
  ist 25.09. vor Manuels dreiwoechiger Abwesenheit. Legal-/Betreiberangaben
  werden voraussichtlich Mitte September vorliegen.
- EDV hat beide Website-Subdomains auf denselben IONOS-Webspace gelegt und
  Wildcard-TLS bestaetigt. Manuel besitzt den SFTP-Zugang zum Startverzeichnis;
  Werte und Passwoerter bleiben ausserhalb von Git und Dokumentation. Ein
  Upload erfolgte nicht.
- Persoenliche Portalidentitaeten sind
  `roedel.kg@donner-partner.eu` (`admin`) und
  `rappelt.wue@donner-partner.eu` (`internal`). Einladungen sollen per E-Mail
  erfolgen. Funktions-/Weiterleitungsadressen werden nicht als geteilter Login
  verwendet.
- `competencehub@donner-partner.de` bleibt Janays oeffentliche Kontaktmailbox.
  `admin@competencehub.donner-partner.de` ist als Technikalias zu Manuel
  vorgeschlagen, benoetigt aber EDV-Bestaetigung. SMTP-Parameter und eine
  freigegebene Systemabsenderadresse fehlen noch.
- Der Wuerzburger Rechner ist kontrolliert zugaenglich; Verschluesselungs- und
  Restore-Nachweis koennen voraussichtlich in den naechsten ein bis zwei Wochen
  erfolgen. Echtdaten bleiben bis dahin gesperrt.
- SFTP schliesst nur den statischen Astro-Pfad. Portal/API/Worker benoetigen
  weiterhin eine auf den VPS gerichtete App-Subdomain, Nginx und eigene
  systemd-Dienste. Kein Deployment, Konto oder Echtdatum erfolgte.

## 2026-08-21 | steering/restart | Pilotstand abgeglichen und kritischen Pfad bereinigt

- `main` und `origin/main` stehen beide auf `c1f4cc8`; der sichere Arbeitsbaum
  war zu Beginn sauber. Der manuelle GitHub-Pages-Workflow bleibt ohne
  Push-Trigger. Zwischen dessen Review-Commit und `main` gibt es keine
  Aenderung an `apps/website`, die sichtbare Website-Review ist daher nicht
  hinter dem aktuellen Website-Code zurueck.
- Die lokale Webapp-Suite ist erneut gruen; 14 opt-in Staging-Pfade wurden ohne
  Tunnel erwartungsgemaess uebersprungen. Astro prueft 36 Dateien ohne Fehler,
  Warnungen oder Hinweise und baut 28 Seiten.
- Projektplan und Status wurden nach dem Portal-Push nachgezogen: BA-01 bis
  BA-17, Versionierung und Runner-Cleanup sind abgeschlossen. Aktuelle WIP ist
  die Pilot-Aktivierung statt weiterer Frontendfunktionalitaet.
- Ein Produktionsreview fand, dass `/system`, `/seminare`, `/qualifizierung`
  und die oeffentlichen Login-Vorschauen anders als die Prototypseiten noch
  indexierbar waren. Diese Routen senden nun `noindex`; die Startseite bleibt
  indexierbar. Der anschliessende Astro-Check bleibt mit 36 Dateien und null
  Diagnosen gruen, der Build erzeugt 28 Seiten.
- Fuenf Arbeitstage bleiben bis 28.08. Die Softwarebasis ist belastbar; offen
  sind persoenliche Konten und Uebergabe, Runtime/Worker-Paket, DNS/Reverse
  Proxy, verschluesselter externer Restore, Legal-/Produktionsfreigabe und
  beaufsichtigte Abnahme. Ohne diese Evidenz bleiben Echtdaten gesperrt.
- Kein Deployment, Konto, Echtdatum, Servereingriff, Commit oder Push erfolgte
  in diesem Statuscheck.

## 2026-08-20 | portal/browser/acceptance | BA-01 bis BA-17 bestanden

- Manuel bestaetigte nach den Nacharbeiten BA-09, BA-10 und BA-14 als
  bestanden. Damit sind alle 17 manuellen Funktions-, Responsive- und
  Accessibility-Pruefungen des Same-Origin-Pilotportals akzeptiert.
- Automatisierte Evidenz bleibt 248 lokale Passes plus 14 opt-in Staging-Skips;
  der reale isolierte Datenbanklauf bestand 14/14 mit null Rueckstaenden und
  vier aktiven VPS-Diensten.
- Der lokale Runner wurde danach sauber beendet. Port 8443 ist frei; das
  temporaere Edge-Profil und das selbstsignierte Zertifikat wurden entfernt.
  SB-15 ist damit fachlich und operativ abgeschlossen.
- Naechster Umsetzungsblock nach Cleanup ist die Gate-Matrix fuer persoenliche
  Erstnutzer, Einladungs-/MFA-Uebergabe, App-Origin/DNS und Janay-/Thomas-
  Abnahmetermine. Kein Deployment, Konto, Echtdatum, Commit oder Push erfolgte.

## 2026-08-20 | portal/browser/feedback | Recovery- und Re-Login-Nacharbeiten umgesetzt

- Manuel absolvierte die 17-Punkte-Browsercheckliste und markierte alle
  Kernablaeufe bestanden; BA-14 blieb wegen eines haengenden Re-Login-
  Fehlerzustands nur eingeschraenkt bestanden.
- Recovery-Codes werden nun als zehn getrennte responsive Eintraege statt in
  einer kollidierenden Mehrspaltenliste dargestellt. Die UI erklaert, dass
  jeder Code ein einmal verwendbarer Notfallersatz fuer den Authenticator ist.
- Bei der MFA-Einrichtung erscheint nicht mehr die technische `otpauth://`-URI,
  sondern nur der manuell einzutragende Schluessel samt Sicherheitshinweis.
  Sichtbare Portaltexte verwenden jetzt korrekte deutsche Umlaute.
- Nach MFA-Re-Login werden Schreib-CSRF bei Bedarf erneut rotiert, alte
  Formularfehler entfernt und Mutationselemente anhand des aktuellen
  Schreibzustands aktiviert. Abbrechen stellt Firmendetails aus dem zuletzt
  gespeicherten Zustand wieder her; Entwuerfe geraten nicht mehr in einen
  sichtbar haengenden Fehlerzustand.
- Fokussierte 25 Tests und die Vollsuite sind gruen: 248 bestanden, 14 opt-in
  Staging-Pfade ohne Tunnel uebersprungen; Compileall, `pip check`, JavaScript-
  Syntax und Diff-Pruefung sind ebenfalls gruen. BA-09/10/14 werden gezielt
  nachgetestet. Kein Deployment, Konto, Echtdatum, Commit oder Push erfolgte.

## 2026-08-20 | portal/browser/debug | BA-01 Browser-Loginfehler behoben

- Manuels erster echter Browserlauf zeigte trotz korrekter synthetischer
  Zugangsdaten die generische Eingabefehlermeldung. Der direkte HTTPS-Login
  gegen denselben laufenden Fixture-Prozess blieb mit `202` erfolgreich.
- Ursache: `setBusy` deaktivierte alle Formularfelder, bevor `FormData` erzeugt
  wurde. Browser schliessen deaktivierte Felder normgerecht aus FormData aus;
  E-Mail und Passwort erreichten die API daher als `null`.
- Der zentrale Submit-Helper erfasst nun validierte Formdaten vor der
  Doppelklicksperre. Der Fix gilt fuer alle sieben betroffenen Login-, MFA-,
  Enrollment-, Firmen- und Kontaktformulare; ein Regressionstest sichert
  Reihenfolge und vollstaendige Verwendung.
- Fokussierte Tests 9/9 und anschliessende Vollsuite sind gruen: 245 bestanden,
  14 opt-in Staging-Pfade ohne Tunnel uebersprungen; Compileall, `pip check`,
  JavaScript-Syntax und Diff-Pruefung sind ebenfalls gruen. Der laufende lokale
  Fixture liefert die korrigierte Datei aus; manueller BA-01-Retest ist offen.
- Kein Deployment, Konto, Echtdatum, Commit oder Push erfolgte.

## 2026-08-20 | portal/browser | Lokale Browser-Abnahme reproduzierbar vorbereitet

- Fuer SB-15 existiert nun eine rein synthetische In-Memory-Abnahme-App, die
  den produktionsnahen Portalclient ueber lokales Loopback-HTTPS bedient. Sie
  liest keine ENV-Datei, verbindet keine Datenbank und speichert keine Daten.
- Ein PowerShell-Runner erzeugt ein eintaegiges selbstsigniertes
  Loopback-Zertifikat und ein isoliertes temporaeres Edge-Profil. Nach dem
  Test werden Server, Profil, Zertifikat und Logs entfernt.
- Die dauerhafte Checkliste umfasst 17 Funktions-, Responsive- und
  Accessibility-Pruefungen fuer Desktop, exakt 390 CSS-Pixel, Tastatur, Fokus,
  200-Prozent-Zoom und Reduced Motion. Nur `example.invalid`-Identitaeten und
  synthetische Firmendaten sind erlaubt.
- Vollsuite: 258 Tests gesammelt, 244 bestanden und 14 opt-in Staging-Pfade
  ohne Tunnel erwartungsgemaess uebersprungen. Der fokussierte Portal-/Session-
  Lauf bestand 22/22; Compileall, `pip check`, JavaScript- und PowerShell-Syntax
  sind gruen. Der echte lokale HTTPS-Smoke bestaetigt `202 mfa_required`, CSP
  sowie Secure/HttpOnly/SameSite-Cookies.
- Offen bleibt Manuels manueller BA-01-bis-BA-17-Lauf. Kein Deployment, Konto,
  Echtdatum, Commit oder Push erfolgte in diesem Paket.

## 2026-08-20 | portal/staging | Same-Origin-Portal besteht 14/14 Pfade

- Der freigegebene SB-15-Staging-Lauf bestand alle 14 synthetischen Pfade in
  171.95 Sekunden, einschliesslich der neuen CSRF-Rotation nach Seitenreload.
- Der unabhaengige Nachlauf bestaetigte null Nutzer, Sitzungen, Firmen,
  Firmenkontakte und Auditereignisse. Chatbot, Nginx, Fail2ban und PostgreSQL
  blieben jeweils `active`.
- Damit sind Datenbank-, Cleanup- und Co-Hosting-Gate des Portal-Slices gruen.
  Offen bleibt der echte Browsernachweis fuer Desktop/390 Pixel, Tastatur,
  Fokus, Zoom, Reduced Motion und den gesamten synthetischen Nutzerablauf.
- Kein Deployment, Konto, Echtdatum, Commit oder Push wurde durch diesen Lauf
  ausgefuehrt. Tunnel und Datenbankkennwoerter gehoeren nicht ins Repository.

## 2026-08-20 | portal/frontend/security | ADR 0006 lokal umgesetzt

- Manuel hat Pilot-Cutline und ADR 0006 fuer den lokalen synthetischen Slice
  freigegeben; DNS, Konten, Echtdaten und Deployment sind davon ausgenommen.
- FastAPI paketiert nun einen frameworkfreien Same-Origin-Portalclient unter
  `/portal/`. Der vertikale Slice deckt Login, TOTP/Recovery, erstes
  MFA-Enrollment, Session-Restore/Logout sowie Firmen- und Kontaktworkflow ab.
- Nach Reload rotiert `POST /api/v1/auth/session/csrf` das CSRF-Material einer
  aktiven MFA-Sitzung. Nur der Digest wird gespeichert; der Klartext bleibt im
  Seitenspeicher und wird nicht in Browser-Storage persistiert.
- CSP, `no-store`, lokale Assets, sichere DOM-Ausgabe, Formular-Labels,
  eindeutige ID-Bezuege, Fokus-/Responsive-/Reduced-Motion-Stile,
  Fehler-/Leerzustaende und Doppel-Submit-Sperren wurden umgesetzt und
  regressionstestbar gemacht.
- Vollsuite: `241 passed, 14 skipped`; die Skips sind die opt-in PostgreSQL-
  Staging-Pfade ohne Tunnel. Compileall, JavaScript-Syntax und `pip check` sind
  gruen. Der fokussierte Review findet keinen offenen hohen oder kritischen
  Befund.
- Naechster Block ist SB-15: 14/14 Staging inklusive CSRF-Rotation, Cleanup und
  vier Service-Checks sowie realer Browserlauf auf Desktop und 390 Pixel mit
  ausschließlich synthetischen Daten. Commit, Push und Deployment erfolgten
  fuer dieses Paket noch nicht.

## 2026-08-20 | release/planning | Portal-Slice versioniert und Pilotgrenze vorbereitet

- Der Firmen-/Kontakt-Slice wurde nach 14/14 Staging-Pfaden als `6e52f52`
  committed und nach `origin/main` gepusht. `.tmp/`, Secrets, Konten,
  Echtdaten und Deployment blieben ausgeschlossen.
- `pilot-cutline-2026-08-28.md` konsolidiert als naechstes Paket Pilotziel,
  erste Rollen, minimale Felder, Non-Goals, zehn Abnahmekriterien, Gate-Owner,
  vorgeschlagene Domains und den Rueckwaertsplan bis 28.08.
- Vorgeschlagene Erstkonten sind Manuel als `admin` und Frau Janay Rappelt als
  `internal`, jeweils mit persoenlicher Arbeitsadresse. Die Funktionsmailbox
  bleibt Kontaktkanal und ist kein geteilter Login.
- Fuer den engen Pilot wird eine gemeinsame App-Origin fuer Portal und API
  empfohlen. Das vermeidet unnoetige CORS-/Cookie-Komplexitaet; eine getrennte
  API-Subdomain bleibt spaeter moeglich. Nutzeradressen, Einladungsweg,
  DNS-Name, Wuerzburg-Backupnachweis und Abnahmetermine bleiben freizugeben.
- ADR 0006 formulierte diese same-origin, frameworkfreie Pilot-UI als
  Freigabevorlage; sie wurde anschliessend von Manuel akzeptiert und lokal
  umgesetzt (siehe neuesten Eintrag).

## 2026-08-20 | backend/staging | Erster Firmen-/Kontakt-Lauf diagnostiziert

- Der erweiterte PostgreSQL-Staging-Runner bestand 12 von 14 Pfaden. Beide
  Fehler waren reproduzierbare Test-/Adapterprobleme, keine Datenmigration und
  kein Ausfall des VPS: Der MFA-Test nutzte einen veralteten festen Zeitpunkt,
  und asyncpg konnte den optionalen Suchparameter der Firmenliste ohne
  expliziten PostgreSQL-Texttyp nicht ableiten.
- Der MFA-Test verankert seine kontrollierte Uhr nun an `clock_timestamp()` der
  Staging-Datenbank. Die Firmensuche castet den optionalen Suchparameter
  ausdruecklich auf `text`; ein SQL-Regressionstest sichert dies.
- Fokussierte Tests, lokale Vollsuite, Kompilierung, `pip check` und
  `git diff --check` sind nach der Korrektur gruen. Der erneute reale Lauf
  bestand alle 14 Pfade; seine synthetischen Daten wurden entfernt und
  Chatbot, Nginx, Fail2ban sowie PostgreSQL blieben aktiv. Deployment, Konten
  und Echtdaten sind weiterhin nicht erfolgt.

## 2026-08-20 | backend/portal | Firmen- und Kontakt-Pilot lokal umgesetzt

- Der kritische Pfad zum 28.08 wurde als schmaler vertikaler B2B-Slice
  fortgesetzt: `admin` und `internal` koennen Firmen samt erstem Kontakt atomar
  anlegen, begrenzt suchen/lesen, weitere Kontakte hinzufuegen und Pilotfelder
  kontrolliert korrigieren.
- Schreibzugriffe verlangen aktive MFA-Sitzung, exakte Origin und
  sitzungsgebundenes CSRF. Bodies sind auf 32 KiB begrenzt, Antworten `no-store`
  und unbekannte Felder verboten; es gibt keinen Delete-Endpunkt.
- Audit schreibt nur Actor, Aktion, Objekttyp/-ID, Ergebnis und Zeitpunkt,
  niemals Firmennotiz, Kontaktdaten oder Requestpayload. Der Startstatus
  `prospect` ist explizit provisorisch und nicht als Fachworkflow freigegeben.
- Der Security-/Privacy-Review fand eine zu breite Listenform: interne Notizen
  waeren mitselektiert worden. Ein separates minimiertes Summary-Modell behebt
  dies; Regressionstests sichern SQL und API-Antwort.
- Neue Service-, PostgreSQL-Adapter-, API- und Runtime-Tests bestanden 24/24;
  die Vollsuite bestand mit 231 Tests und 14 erwarteten opt-in-Staging-Skips.
- Ein opt-in PostgreSQL-Test fuer CRUD, Audit und Null-Rueckstaende ist im
  Runner vorbereitet. Staging-Ausfuehrung, UI, persistenter Dienst, Konten,
  Echtdaten, Deployment, Commit und Push sind nicht erfolgt.
- Restgrenzen: Firmenanlage ist noch nicht persistent idempotent; der spaetere
  UI-Slice muss Doppel-Submit verhindern. Finales Feld-/Statusvokabular,
  Off-Server-Restore, Zustellung und Produktionsfreigabe bleiben Gates.

## 2026-08-14 | review/planning | Auth-Paket geprueft und Pilottermin 28.08 gesetzt

- Der abschliessende Code-/Security-Review fuer SB-01 bis SB-09 fand keinen
  offenen hohen oder kritischen Befund. Der Umfang bleibt synthetisch und
  deploymentfrei; `.tmp/`, `.env*`, Dumps und Secrets sind ausgeschlossen.
- Manuel hat Commit und Push fuer das gepruefte Paket freigegeben. Deployment,
  produktive Konten und Echtdaten bleiben eigene Gates.
- Neue operative Pilotmarke ist der 28.08.2026: Die kanonische Website soll
  ueber den freigegebenen Produktionspfad erreichbar sein und Janay soll die
  erste freigegebene Firma samt Kontakt im geschuetzten Portal erfassen koennen.
- Terminstatus: gefaehrdet, aber mit enger Pilot-Schnittlinie noch erreichbar.
  Kritischer Pfad sind Runtime/Zustellung, Firmen-/Kontakt-CRUD, minimale UI,
  Backup-Restore, Produktionsfreigabe sowie reale Rollen-/MFA-Einrichtung.
- Der Rolling Horizon wurde auf acht rueckwaerts geplante Schritte bis zum
  Pilot-Go-live umgestellt; Coaches, Matching, Feedback, Statistiken, Vertraege
  und weitere Automatisierung bleiben ausserhalb dieses ersten Datenpiloten.

## 2026-08-14 | backend/staging/security | Migration 0004 und Outbox-Gate abgeschlossen

- Manuel hat Migration `0004` separat fuer das leere, synthetische VPS-Staging
  freigegeben. SHA-256-Pruefsummen, 22-Tabellen-Ausgangslage, Migrationen
  `0001`-`0003`, vier aktive Dienste und localhost-only PostgreSQL wurden vorab
  bestaetigt; der geschuetzte 74-KiB Pre-Dump liegt mit Modus `0600` vor.
- Die Migrator-Rolle hat `0004` atomar mit `COMMIT` angewendet. Der
  rollback-only Smoke bestand ohne Rueckstaende; danach gehoeren alle 24
  Tabellen `competence_hub_owner`, beide neuen Tabellen sind leer und die App
  darf deren benoetigte DML-Operationen, aber weder Schemaerstellung noch
  Migrationsmetadatenzugriff ausfuehren.
- Der reale PostgreSQL-Lauf deckte drei Harness-/Adapterprobleme auf: einen
  31-Byte-Testschluessel, fehlende UUID-Casts im synthetischen Fixture und einen
  unnoetigen `FOR SHARE`-Lock auf der read-only Rollentabelle. Die ersten beiden
  wurden im Test korrigiert; der Lock wurde im Repository entfernt, statt der
  Runtime-Rolle gefaehrlich `UPDATE` auf Rollen zu geben. Ein Regressionstest
  sichert diese Least-Privilege-Entscheidung.
- Finaler Nachweis: `13 passed in 156.91s` gegen isoliertes Staging. Geprueft
  wurden Idempotenz-Replay/-Konflikt, verschluesseltes Enqueueing, Zustellung,
  terminaler Fehler mit Token-Widerruf, Minimierung, Cleanup und unbekannter
  Reset. Alle elf Datenbereiche blieben bei null Datensaetzen.
- Migrationen `0001`-`0004`, 24 Owner-Tabellen, Rollen-`SELECT=t` und
  Rollen-`UPDATE=f`, vier aktive Dienste sowie `127.0.0.1:5432` wurden
  unabhaengig bestaetigt. Der geschuetzte 86-KiB Post-Dump ist kataloglesbar,
  gehoert `postgres:postgres` und besitzt Modus `0600`.
- Keine echten Konten/Daten, kein Mailanbieter, kein persistenter Backend- oder
  Worker-Dienst, kein Deployment, Commit oder Push. `.tmp/` blieb unberuehrt.

## 2026-08-14 | backend/security | ADR 0005 und Auth-Outbox lokal umgesetzt

- ADR 0005 wurde durch Manuel freigegeben und als akzeptiert dokumentiert.
- Migration `0004` und ein rollback-only Smoke sind lokal vorbereitet, aber
  nicht auf Staging angewendet.
- Einladung und bekannter Passwort-Reset schreiben Token-Digest und AES-256-
  GCM-verschluesselten Outbox-Payload atomar; unbekannte Reset-Adressen erzeugen
  keinen Token- oder Outbox-Datensatz.
- Admin-Einladungen besitzen persistente HMAC-Idempotenz. Identische Replays
  liefern dieselbe Nutzerreferenz ohne neuen Token; veraenderte Requests mit
  demselben Key werden als Konflikt abgewiesen.
- Die Adminroute erzwingt MFA-Sitzung, Adminrolle, frische Authentisierung,
  Origin, CSRF, `Idempotency-Key` und ausschliesslich die Anfangsrolle
  `internal`. API-Antworten enthalten keine Roh-Tokens.
- Der providerneutrale Worker nutzt atomare Leases, `SKIP LOCKED`, begrenzte
  Retries, stabile Delivery-IDs, terminalen Token-Widerruf und loescht bei
  Abschluss Empfaengeradresse sowie Payload. Cleanup-Fristen bleiben explizit
  konfigurierbar.
- Verifikation: 56 fokussierte Tests und Vollsuite `214 passed, 13 skipped`;
  der neue Outbox-Staging-Harness ist opt-in vorbereitet. Kein offener hoher
  oder kritischer lokaler Befund.
- Kein Commit, Push, Deployment, Staging-Eingriff, Mailanbieter, Runtime-Secret,
  echtes Konto oder Echtdatum. `.tmp/` blieb unberuehrt.

## 2026-08-14 | backend/security | Einladungs- und Reset-Lifecycle lokal abgesichert

- SB-08 deckt lokal nun Initial-Admin, Einladung und Passwort-Reset ab:
  Single-use, Ablauf, Widerruf, Rate Limits, Audit und das Widerrufen aller
  Sitzungen nach einem Reset sind in Service und PostgreSQL-Repository
  umgesetzt.
- Generische oeffentliche HTTP-Grenzen fuer Reset-Anfrage, Reset-Bestaetigung
  und Einladungsannahme geben keine Kontoexistenz preis und bleiben ohne
  konfigurierte Runtime-Dienste kontrolliert `503`.
- Einladungsannahme fuehrt ausschliesslich in die MFA-Einrichtung; ein Reset
  erzeugt keine Sitzung. Roh-Tokens werden nicht persistiert oder in HTTP-
  Antworten ausgegeben.
- Die Admin-Einladungsroute und produktive Zustellung bleiben absichtlich
  gesperrt, bis ADR 0005 zu transaktionaler Outbox, verschluesselter Payload und
  persistenter Idempotenz entschieden ist.
- Verifikation: Lifecycle-Service 11 Tests, Service/Repository 19 Tests,
  Auth-API 38 Tests und Vollsuite `194 passed, 12 skipped`; Compile und
  Abhaengigkeitspruefung bestanden. Kein offener hoher oder kritischer Befund
  im fokussierten Review.
- Kein Commit, Push, Deployment, Staging-Eingriff, Provider, echtes Konto oder
  Echtdatum. `.tmp/` blieb unberuehrt.

## 2026-08-14 | backend/security | Initial-Admin-CLI lokal umgesetzt

- SB-08 wurde mit dem blockierenden Initial-Admin-Teilslice begonnen.
- Der neue interaktive CLI-Pfad besitzt keine Default-Zugangsdaten, nimmt kein
  Passwort als Argument an und verweigert nicht-interaktive Ausfuehrung.
- Eine verpflichtende absolute lokale SHA-256-Fingerabdruckdatei ergaenzt die
  bestehende Passphrase-Policy; leere oder fehlerhafte Quellen schliessen den
  Pfad.
- PostgreSQL serialisiert Bootstrap-Versuche per transaktionalem Advisory Lock.
  Ein vorhandener wirksamer Admin stoppt vor Schreibzugriff; Nutzer, Adminrolle,
  Argon2id-Credential und datensparsames Audit entstehen atomar.
- Verifikation: 21 fokussierte Tests sowie die Vollsuite mit `164 passed, 12
  skipped`; Compile, `pip check` und CLI-Help-Smoke bestanden.
- Review: `initial-admin-cli-security-review-2026-08-14.md`, kein offener hoher
  oder kritischer Befund. Fingerabdruckquelle, Staging-Rehearsal und reale
  Kontoanlage bleiben separate Gates.
- SB-08 bleibt fuer Einladung und Passwort-Reset offen. Kein Deployment,
  Commit, Push, echtes Konto oder Echtdatum.

## 2026-08-14 | staging/security | SB-07 vollstaendig abgeschlossen

- Der unabhaengige Abschlusscheck bestaetigt null Datensaetze in allen neun
  geprueften Portal-, Auth- und Auditbereichen.
- `schema_migrations` enthaelt genau die erwarteten Stufen `0001`, `0002` und
  `0003`.
- Chatbot, Nginx, Fail2ban und PostgreSQL sind jeweils `active`; PostgreSQL
  meldet `listen_addresses = localhost` und lauscht nur auf
  `127.0.0.1:5432`.
- Zusammen mit rollback-only Smoke, 12/12 MFA-Pfaden sowie geschuetzten,
  kataloglesbaren Pre-/Post-Dumps ist SB-07 ohne offenen hohen oder kritischen
  Befund abgeschlossen.
- Naechster empfohlener Block: SB-08, Initial-Admin-CLI plus Einladungs- und
  Passwort-Reset-Lifecycle lokal mit synthetischen Daten.
- Kein Deployment, Commit, Push, echtes Konto oder Echtdatum.

## 2026-08-14 | staging/backup | Post-0003-Dump verifiziert

- Nach dem erfolgreichen 12/12-MFA-Lauf wurde der Post-Dump
  `competence-hub-staging-post-0003-2026-08-14.dump` erstellt.
- Der Custom-Format-Katalog ist mit PostgreSQL 16.14 lesbar und enthaelt das
  erwartete `competence_hub`-Schema mit Owner `competence_hub_owner`.
- Post-Dump: 74 KiB; Pre-Dump: 73 KiB. Beide gehoeren `postgres:postgres` und
  sind mit Modus `0600` geschuetzt.
- SB-07 bleibt bis zum unabhaengigen Nullbestand, Migrationsstand,
  localhost-only Nachweis und unveraenderten Zustand aller vier Dienste offen.
- Kein Deployment, Commit, Push, echtes Konto oder Echtdatum.

## 2026-08-14 | staging/integration | Vollstaendiger MFA-Lauf bestanden

- Der opt-in PostgreSQL-Harness bestand alle 12 Session-, First-Factor- und
  MFA-Staging-Pfade in 134,98 Sekunden.
- Abgedeckt sind unter anderem Passwortlogin, TOTP-Enrollment, verschluesselte
  Speicherung, Bestaetigung, Replay-Ablehnung, einmaliger Recovery-Verbrauch,
  Rate-Limit und Rotation in eine neue Vollsession.
- Der Lauf nutzte nur temporaer eingegebene App-/Migrator-Passwoerter ueber
  einen lokalen SSH-Tunnel; keine Zugangsdaten wurden in Dateien oder Git
  geschrieben.
- SB-07 bleibt bis zum unabhaengigen Nullbestand, geschuetzten lesbaren
  Post-Dump, localhost-only Nachweis und unveraenderten Dienstzustand offen.
- Kein Deployment, Commit, Push, echtes Konto oder Echtdatum.

## 2026-08-14 | staging/verification | Migration 0003 Smoke bestanden

- Der administrative rollback-only Smoke fuer Migration `0003` lief nach der
  gezielten Uebergabe der temporaeren Datei an `postgres` erfolgreich durch:
  `BEGIN`, synthetischer Insert, Assertions und `ROLLBACK`.
- Anschliessend standen Portalbenutzer, Login-Challenges, Sessions,
  TOTP-Credentials, Recovery-Codes, Rate-Limit-Buckets und Auditereignisse
  jeweils bei null. Es verblieben keine synthetischen Daten.
- Migration `0003` wurde nicht erneut ausgefuehrt. Der vorherige Fehler war
  ausschliesslich ein Dateirechte-Handoff und ist damit geschlossen.
- Naechster Schritt: den vollstaendigen MFA-Staging-Harness ueber einen
  temporaeren SSH-Tunnel ausfuehren, danach Post-Dump und Dienstzustand pruefen.
- Kein Deployment, Commit, Push, echtes Konto oder Echtdatum.

## 2026-08-14 | staging/migration | Migration 0003 angewendet, Smoke nachzuholen

- Migration `0003` wurde auf der leeren Staging-Datenbank erfolgreich
  angewendet und ist in `schema_migrations` registriert.
- `auth_totp_credentials.last_accepted_time_step bigint NULL` und
  `auth_recovery_codes.key_version text NOT NULL` sind vorhanden.
- Der geschuetzte Pre-Dump
  `competence-hub-staging-pre-0003-2026-08-14.dump` existiert mit 73 KiB,
  Eigentuermer `postgres` und Modus `0600`.
- Der rollback-only Smoke startete nicht, weil seine `/tmp`-Datei korrekt mit
  `0600`, aber noch im Eigentum von `manuel` stand. Das ist ein Dateirechte-
  Handoff, kein SQL- oder Migrationsfehler; Migration nicht erneut ausfuehren.
- Naechster Schritt: Smoke-Datei an `postgres` uebergeben, Smoke ausfuehren und
  Nullbestand bestaetigen. Kein Deployment, Commit, Push oder Echtdaten.

## 2026-08-14 | approval/preparation | Migration 0003 fuer Staging freigegeben

- Manuel hat Migration `0003` separat fuer die leere PostgreSQL-Staging-
  Datenbank freigegeben.
- Der opt-in Harness prueft nun zusaetzlich Passwortlogin, TOTP-Enrollment,
  verschluesselte Speicherung, Session-Rotation, Replay-Ablehnung, einmaligen
  Recovery-Verbrauch, MFA-Rate-Limit und Cleanup gegen echtes PostgreSQL.
- Lokale Vorbereitung: `148 passed, 12 skipped`; der neue Skip ist der ohne
  Tunnel bewusst deaktivierte MFA-Staging-Pfad. PowerShell-Syntax des Runners
  ist gueltig.
- Noch nicht ausgefuehrt: Transfer, Pre-Dump, Migration, rollback-only Smoke,
  Staging-Harness, Post-Dump und Dienstpruefung.
- Keine echten Konten/Fachdaten, kein Deployment, Commit oder Push.

## 2026-08-14 | decision | ADR 0004 freigegeben

- Manuel hat ADR 0004 fuer TOTP-Kryptografie und das Recovery-Modell explizit
  freigegeben.
- Damit sind PyOTP, versionierte AES-256-GCM-Umschlaege, ein getrennter
  versionierter Recovery-HMAC-Keyring, Replay-Schutz und Session-Rotation als
  technische Richtung akzeptiert.
- Die Freigabe umfasst keine Anwendung von Migration `0003`, keine
  Runtime-Secrets, echten Konten, Fachdaten, kein Deployment, Commit oder Push.
- Naechstes Gate: separate Freigabe von Migration `0003` fuer das leere
  PostgreSQL-Staging mit geschuetzten Dumps und synthetischer Verifikation.

## 2026-08-14 | backend/security | MFA-Slice SB-06 lokal abgeschlossen

- TOTP-Enrollment, TOTP-Pruefung, Recovery-Code-Pruefung und Rotation von der
  Pre-Auth-Challenge in eine neue serverseitige Vollsession umgesetzt.
- PyOTP `2.10.x` uebernimmt TOTP/Provisioning; `cryptography` `49.x` schuetzt
  TOTP-Secrets per AES-256-GCM mit frischer Nonce, benutzergebundener
  Associated Data und versioniertem externem Keyring.
- Zehn Recovery-Codes mit je 80 Bit werden nur einmal nach Enrollment
  ausgegeben; PostgreSQL erhaelt ausschliesslich HMAC-Digest und Key-Version.
- Migration `0003` bereitet atomaren Replay-Schutz ueber den hoechsten
  akzeptierten TOTP-Zeitschritt sowie Recovery-Key-Versionen vor. Migration und
  rollback-only Smoke liegen lokal, sind aber nicht auf Staging angewendet.
- Challenge-Verbrauch, Replay-Zaehler oder Recovery-Verbrauch, Sessionanlage
  und Audit liegen jeweils in einer Transaktion. Deaktivierung oder Rollenentzug
  wird auch beim finalen Transaktionsschritt erneut geprueft.
- Vollsuite: `148 passed, 11 skipped`; `compileall` bestanden; `pip check` ohne
  gebrochene Abhaengigkeiten; `git diff --check` ohne Patchfehler.
- Sicherheitsreview:
  `docs/architecture/mfa-runtime-security-review-2026-08-14.md`; kein offener
  hoher oder kritischer Befund im lokalen Slice.
- Keine Staging-Aenderung, Runtime-Secrets, echten Konten, Fachdaten, kein
  Commit, Push oder Deployment. ADR 0004 wurde anschliessend freigegeben.
- Naechster Block: Migration `0003` und den vollstaendigen synthetischen
  MFA-Fluss separat fuer Staging freigeben.

## 2026-08-14 | security/staging | First-Factor-Gate SB-05 abgeschlossen

- Der kombinierte Session-/Login-Lauf bestand alle 11 PostgreSQL-Staging-Pfade
  in 103,75 Sekunden.
- First-Factor-Login, Rollen/Aktivstatus, Challenge-/CSRF-Hashes, fuenf Minuten
  Laufzeit, Audit, fuenfter Fehlversuch, progressive Sperre, Sessionpfade und
  Readiness sind damit gegen PostgreSQL 16 belegt.
- Cleanup bestaetigt null Portalbenutzer, Credentials, Login-Challenges,
  Sessions, Rate-Limit-Buckets und Auditereignisse. Chatbot, Nginx, Fail2ban und
  PostgreSQL blieben `active`.
- Der fokussierte Review dokumentiert drei bereits behobene Low-Risk-Punkte und
  keinen offenen hohen oder kritischen Befund. Proxy-Trust, vorgeschalteter
  DoS-Schutz und produktive Schluesselrotation bleiben Deployment-Gates.
- Review: `docs/architecture/first-factor-login-security-review-2026-08-14.md`.
  Keine echten Konten/Fachdaten, kein Deployment, Commit oder Push.
- Naechster Block: TOTP/recovery und sichere Rotation zur Vollsitzung mit
  synthetischen Daten.

## 2026-08-14 | backend/staging | Login-Cleanup und Dienste bestaetigt

- Nach dem vorbereiteten Auth-Staging-Lauf sind Portalbenutzer, Credentials,
  Login-Challenges, Sessions, Rate-Limit-Buckets und Auditereignisse jeweils
  bei null.
- `dp-chatbot`, Nginx, Fail2ban und PostgreSQL sind weiterhin `active`.
- Damit waren Cleanup und betriebliche Isolation belegt. Die anschliessend
  uebermittelte pytest-Abschlusszeile hat SB-05 inzwischen vollstaendig
  geschlossen.
- Keine echten Konten oder Fachdaten, kein Deployment, Commit oder Push.

## 2026-08-14 | backend/auth | First-Factor-Login lokal umgesetzt

- `POST /api/v1/auth/login` mit strikter JSON-Grenze, 32-KiB-Limit,
  unbekannten-Feld-Ablehnung und generischen Fehlerantworten umgesetzt.
- Unbekannte, inaktive und externe Rollen durchlaufen denselben
  Argon2id-Vergleich. Nach korrektem Passwort entsteht ausschliesslich eine
  fuenf Minuten gueltige MFA-Pre-Auth-Challenge, keine Vollsitzung.
- Konto- und Netzwerk-Peer-Buckets werden mit einem externen, mindestens 256 Bit
  starken HMAC-Schluessel pseudonymisiert. Der fuenfte Fehler in 15 Minuten
  startet eine progressive Sperre; rohe Mailadresse/IP werden nicht persistiert.
- Audit unterscheidet unauthentifizierten Fehlversuch von erfolgreichem ersten
  Faktor. `X-Forwarded-For` bleibt bis zu einer expliziten Proxy-Trust-
  Konfiguration unberuecksichtigt.
- Nachweis: 86 lokale Tests bestanden, elf Opt-in-Staging-Tests ohne explizite
  Zugangskonfiguration kontrolliert uebersprungen; Compileall, `pip check` und
  Diff-Check bestanden.
- Ein PostgreSQL-Staging-Test fuer Challenge-Hashes, Audit, Rollen/Aktivstatus,
  den fuenften Fehlversuch und garantiertes Cleanup ist vorbereitet, aber noch
  nicht ausgefuehrt. Keine echten Konten, keine Serveraenderung, kein Commit,
  Push oder Deployment.

## 2026-08-14 | security/backend | Session- und Runtime-Review SB-04 abgeschlossen

- Der lokale Session-/Runtime-Slice wurde fokussiert auf Konfiguration,
  Datenbankrollen, Token-/Cookie-Verarbeitung, CSRF, Fehlerausgaben, Readiness
  und das synthetische Staging-Harness geprueft.
- Behoben wurden vier Defense-in-Depth-Risiken: direkte Settings-Konstruktion
  kann die Validierung nicht mehr umgehen, die Runtime akzeptiert nur die
  eingeschraenkte Rolle `competence_hub_app`, Tokenwerte erscheinen nicht mehr
  in Dataclass-Repraesentationen und SQL-Parameter bleiben in Fehlern verborgen.
- Nachweis: 61 lokale Tests bestanden, sieben Opt-in-Staging-Tests ohne explizite
  Konfiguration kontrolliert uebersprungen; Compileall, `pip check` und
  Diff-Check bestanden. Der vorausgehende echte Staging-Lauf blieb bei 7/7.
- Ergebnis: kein offener hoher oder kritischer Befund im geprueften Slice. Das
  ist keine Produktionsfreigabe; Login, Rate Limits, MFA, reale Konten und
  Deployment bleiben ausserhalb des abgeschlossenen Blocks.
- Review: `docs/architecture/session-runtime-security-review-2026-08-14.md`.
  Kein Commit, Push, Deployment oder Einsatz echter Daten.
- Der damals empfohlene First-Factor-Block ist inzwischen als SB-05 lokal und
  auf isoliertem Staging abgeschlossen.

## 2026-08-14 | backend/staging | Session-Integration SB-03 abgeschlossen

- Opt-in Harness mit getrennten App- und Migrator-Verbindungen, ausschliesslich
  synthetischen Benutzern/Sitzungen und garantiertem Cleanup umgesetzt.
- Erster Staging-Lauf deckte einen mehrdeutigen optionalen SQL-Parameter im
  Fixture-Setup auf; die Setup-Transaktion wurde jeweils zurueckgerollt. Der Fix
  verwendet explizite Parameter und blendet SQL-Parameter in Fehlern/Logs aus.
- Zweiter Lauf bestaetigte sechs fachliche Pfade; die Readiness war ueber den
  SSH-Tunnel langsamer als das feste Zwei-Sekunden-Limit. Der Timeout ist nun
  begrenzt konfigurierbar: Standard 5, maximal 30, im Tunneltest 15 Sekunden.
- Finaler Nachweis: 7/7 Staging-Tests bestanden. Geprueft wurden aktive,
  abgelaufene, widerrufene, inaktive und rollenfalsche Sessions, Idle-Refresh,
  Origin/CSRF-Logout, Audit und echte PostgreSQL-Readiness.
- Unabhaengiger Abschlusscheck: null Portalbenutzer, null Auth-Sessions, null
  Auditereignisse; nur Migrationen `0001`/`0002`; Chatbot, Nginx, Fail2ban und
  PostgreSQL jeweils `active`.
- Lokaler Nachweis: 58 Tests bestanden, sieben Staging-Tests ohne Zugangsdaten
  kontrolliert uebersprungen; Compileall, `pip check`, PowerShell-Syntax und
  Diff-Check bestanden.
- Grenzen zum Zeitpunkt des Blocks: keine echten Konten/Fachdaten, keine
  Secret-Datei, keine Migration, kein Backend-Deployment, Commit oder Push.
  Der anschliessende Security-Review SB-04 ist inzwischen abgeschlossen.

## 2026-08-14 | process/feedback | Befehlsuebergabe erneut fehlgeschlagen

- Beim Start des Staging-Integrationstests standen die erforderlichen Befehle
  nur im Zwischenstand; die sichtbare Abschlussantwort verwies unbrauchbar auf
  die Befehle "oben". Manuel hat den wiederholten Verlust direkt beobachtet.
- Die Projektregel und ein Skill-Feedback-Eintrag existierten bereits. Als
  Ursache gilt daher fehlende Abschlusskontrolle, nicht fehlende Dokumentation.
- `AGENTS.md` enthaelt nun ein ausdrueckliches Durable-Handoff-Gate: Eine auf
  Manuels Kommandoausfuehrung wartende Antwort ist ohne vollstaendige Befehle,
  Reihenfolge, Arbeitskontext, erwartetes Ergebnis und Secret-Hinweis in
  derselben Abschlussnachricht unvollstaendig.
- Der Wiederholungsfall ist in `SKILL_FEEDBACK_LOG.md` als hochpriorisierte
  kanonische Skill-/Eval-Verbesserung erfasst. Kein Commit, Push oder Deployment.

## 2026-08-14 | requirements/backend | Janay-Feedback und Runtime-Block umgesetzt

- Janays interne Rueckmeldung wurde in eine sichere Fachnotiz ueberfuehrt. Sie
  konkretisiert Erstanfrage, parallele Coach-Verfuegbarkeitspruefung ohne
  vorzeitige Kundennennung, Angebot/Auftrag, Durchfuehrung, Feedback, Rechnung,
  Zahlung sowie Pause, Abbruch und fehlendes Matching.
- Nicht als Freigabe uebernommen wurden insbesondere 48-Stunden-Zusage,
  Klickannahme, Paketdetails, Ergebnisversprechen und Bewertung aus dem
  Beispielszenario. Statusuebergaenge, rechtliche Annahme, Datenschutz,
  Finance-Quelle und Abschlussnachweise bleiben gegatet.
- Backend SB-02 ist lokal umgesetzt: validierte Prozesskonfiguration ohne
  Secret-Datei, nur Loopback-PostgreSQL/asyncpg, exakte HTTPS-Origin, asynchroner
  Engine-Lifecycle und datenbankgestuetzte Readiness mit Timeout und sauberem
  Shutdown.
- Verifikation: 52 synthetische Tests, Compileall und `pip check` bestanden;
  Konfigurations-, Secret-Leakage-, Readiness-Fehler- und Lifecycle-Pfade sind
  abgedeckt. Der Default-Appzustand bleibt nicht bereit und deny-by-default.
- Grenzen: keine `.env*`, `.tmp/`, Zugangsdaten, echten Konten oder Fachdaten
  gelesen oder verwendet; keine Serveraenderung, kein Commit, Push oder
  Deployment.
- Naechster empfohlener Block: SB-03, synthetischer Session-/API-Nachweis gegen
  die isolierte Staging-Datenbank mit vollstaendiger Bereinigung und
  anschliessender Service-Health-Pruefung.

## 2026-08-13 | skills/process | Manage-project-state aktiv synchronisiert

- Manuel hat den globalen Sync ausdruecklich freigegeben.
- Der validierte kanonische Skill `manage-project-state` wurde mit vorheriger
  Sicherung gezielt nach `%USERPROFILE%\.codex\skills` synchronisiert.
- Backup der ersetzten aktiven Version:
  `%USERPROFILE%\.codex\skill-backups\20260813-161514\manage-project-state`.
- Der anschliessende Drift-Check meldete `manage-project-state` und alle
  weiteren aktiven Projektskills als `OK`.
- Fremde offene Aenderungen im kanonischen CodexSkills-Repository blieben
  unangetastet; kein Commit, Push oder Deployment.

## 2026-08-13 | planning/process | Rollierenden 8-Schritt-Horizont eingefuehrt

- Manuel hat verbindlich festgelegt, dass Status und Abschluss nicht nur den
  naechsten Einzelschritt, sondern vier bis acht geordnete Folgeschritte zeigen.
- `PROJECT_PLAN.md` trennt nun aktuellen Execution-/Sprint-Backlog, rollierenden
  Acht-Schritt-Horizont und groesseren Project Backlog.
- Jeder Horizontschritt nennt Ergebnis, Abhaengigkeit/Gate, geplanten
  Testnachweis und distanzabhaengige Konfidenz. Sechs querschnittliche Gates
  decken Daten, Sicherheit, Betrieb, Produktion, Anforderungen und Content ab.
- `AGENTS.md` macht Pflege und Reconciliation dieses Horizonts fuer kuenftige
  Arbeitsbloecke verbindlich; `PROJECT_STATUS.md` enthaelt die kompakte Sicht.
- CodexSkills: `manage-project-state` und seine Project-Memory-Referenz wurden
  kanonisch um Project Backlog, Execution Backlog, 4-8-Schritt-Horizont, Gates
  und vorgesehene Verifikation erweitert. Fremde offene CodexSkills-Aenderungen
  blieben unangetastet.
- Grenzen: Planungs-/Skillverbesserung; kein Commit, Push oder Deployment.

## 2026-08-13 | implementation/security | Session- und Logout-Slice lokal umgesetzt

- Implementierung: Async-SQLAlchemy-/asyncpg-Persistenz fuer interne
  MFA-Sitzungen sowie `GET` und `DELETE /api/v1/auth/session` ergaenzt.
- Schutz: Nur aktive `admin`-/`internal`-Benutzer mit gueltiger MFA-, Idle- und
  Absolutzeit werden akzeptiert. Browser-Token gelangen ausschliesslich als
  SHA-256-Digest zur Persistenzschicht; Standardverdrahtung bleibt geschlossen.
- Logout: aktive Sitzungen verlangen exakte Origin und sitzungsgebundenes CSRF.
  Widerruf und datensparsames Auditereignis erfolgen atomar; ungueltige
  Sitzungen werden idempotent mit Cookie-Loeschung beantwortet.
- Verifikation: 30 synthetische Tests bestanden. PostgreSQL-Adaptermapping,
  generische 401-, CSRF-/Origin-403-, Cookie- und Token-Negativpfade sind
  abgedeckt; noch kein echter Staging-Verbindungs- oder SQL-Integrationstest.
- Grenzen: keine `.env`, Secrets, echten Konten oder Fachdaten gelesen oder
  erzeugt; keine Serveraenderung, kein Commit, Push oder Deployment.
- Naechster empfohlener Block: isolierte Runtime-Konfiguration,
  Datenbank-Lifecycle/Readiness und synthetischer Staging-Integrationstest.

## 2026-08-13 | versioning | Portal- und Auth-Grundlage gepusht

- Feature-Commit `8feb2c8` (`Add portal schema and internal auth foundation`)
  wurde erfolgreich nach `origin/main` gepusht.
- Umfang: 37 freigegebene Dateien mit Portal-/RBAC-Dokumentation, Migrationen
  `0001`/`0002`, Smoke-Tests, ADR 0003, Auth-API-Vertrag, FastAPI-Grundrahmen,
  16 synthetischen Tests und aktualisiertem Projektgedaechtnis.
- Schutz: typische Secret-Signaturen wurden im Index nicht gefunden;
  `.tmp/`, `.venv/`, `*.egg-info`, echte `.env` und Quellen blieben ausserhalb.
- Der Push hat kein GitHub-Pages- oder Backend-Deployment ausgeloest.

## 2026-08-13 | versioning | Portal- und Auth-Grundlage zur Versionierung freigegeben

- Manuel hat Commit und Push des vollstaendigen Portal-, Datenbank-, Auth-,
  Scaffold-, Test- und Projektstatusstands ausdruecklich freigegeben.
- Vorabnachweis: `main` entspricht `origin/main`, 16 Tests bestehen,
  `git diff --check` ist sauber und die versionierte `.env.example` enthaelt nur
  leere Secret-Platzhalter.
- Ausschluss: `.tmp/`, `.venv/`, generierte `*.egg-info`, echte `.env`, Quellen
  und Secrets bleiben ausserhalb des Commits. Der Push loest kein Deployment
  aus.

## 2026-08-13 | database/security | Auth-Migration 0002 auf Staging verifiziert

- Freigabe: Manuel hat die Staging-Anwendung von Migration `0002` separat
  freigegeben. SQL und Rollback-Smoke-Test wurden nach `/tmp` uebertragen,
  gehasht geprueft und auf `0600` gesetzt.
- Sicherung: geschuetzter Pre-Migration-Dump angelegt; Ausgangszustand waren 15
  Tabellen, null Auth-Tabellen und nur Migration `0001`.
- Ausfuehrung: `0002_internal_auth.sql` als `competence_hub_migrator`
  erfolgreich committed. Der synthetische Smoke-Test bestand und endete mit
  `ROLLBACK`.
- Nachweis: 22 Tabellen gehoeren `competence_hub_owner`, davon sieben leere
  Auth-Tabellen. Benutzer, Credentials, Challenges, Sessions, Einmal-Token,
  TOTP, Recovery-Codes und Rate-Limit-Buckets enthalten jeweils null Zeilen.
- Rechte: `competence_hub_app` kann das Schema nicht erweitern und
  Migrationsmetadaten nicht lesen; erwartete Select-/Insert-/Update-Rechte fuer
  Sessions sind vorhanden.
- Betrieb: Chatbot, Nginx, Fail2ban und PostgreSQL blieben aktiv. PostgreSQL
  lauscht nur auf `127.0.0.1:5432`. Der lesbare Post-Dump hat Modus `0600`.
- Grenzen: kein Backenddienst, Login, echtes Konto, Commit, Push oder Deployment.

## 2026-08-13 | implementation/security | Auth-Grundrahmen lokal umgesetzt

- Freigabe: Manuel hat ADR 0003 ausdruecklich freigegeben. Der ADR ist auf
  `Accepted` gesetzt; Serveraenderung, Deployment, Mail und Echtdaten bleiben
  getrennte Freigaben.
- Daten: Migration `0002_internal_auth.sql` modelliert Passwort-Credentials,
  kurzlebige Login-Challenges, serverseitige MFA-Sitzungen, Einladungs-/Reset-
  Token, verschluesselte TOTP-Credentials, Recovery-Code-HMACs und
  HMAC-pseudonymisierte Rate-Limit-Buckets. Sie ist noch nicht auf dem VPS.
- Vertrag: `internal-auth-api-contract-v0.1.md` beschreibt Cookie-, CSRF-,
  Fehler-, Login-, MFA-, Reset-, Einladungs- und Sessionvertraege. Die Routen
  sind bewusst noch nicht vorgetaeuscht.
- Code: minimaler FastAPI-Grundrahmen mit ehrlichen Liveness-/Readinessrouten,
  Security-Headern, sicheren Cookie-Helfern, Argon2id-Passwortpolicy,
  256-Bit-Token und HMAC-Primitive.
- Verifikation: isolierte `.venv`, 16 synthetische Tests bestanden, Python-
  Compileall bestanden und `pip check` ohne defekte Anforderungen. Die erste
  Starlette-TestClient-Warnung wurde durch direkten ASGI-Transport beseitigt.
- Grenzen: keine `.env`, Secrets, echten Konten oder Fachdaten gelesen/erzeugt;
  kein VPS-Change, Commit, Push oder Deployment.

## 2026-08-13 | architecture/security | Interne Auth-Entscheidung vorbereitet

- ADR 0003 legt fuer den ersten internen Admin-/Intern-Slice opaque
  serverseitige Sessions in sicheren Host-only-Cookies, Argon2id, CSRF- und
  Origin-Pruefung, TOTP-MFA, Einladungs-/Resetflows, Rate Limits, Audit und
  getrennten Secretbetrieb fest.
- Sicherheitskorrektur: Nur Admin darf die Adminrolle oder Adminkonten
  veraendern; `internal` kann keine Privilegien zu Admin eskalieren. Diese
  Einschraenkung praezisiert die bisher zu breite Rollenvergabe der RBAC-Matrix.
- Anforderungen: `internal-authentication-v0.1.md` enthaelt 19 funktionale,
  neun nichtfunktionale Anforderungen und 18 pruefbare Akzeptanzkriterien.
- Scope: keine Selbstregistrierung, externen Nutzer, SSO, produktive
  Mailintegration, Login-Implementierung, neuen Dependencies oder Echtdaten.
- Status: Entscheidungsvorlage fertig, explizite Freigabe vor Login-Code offen;
  kein Commit, Push oder Deployment.

## 2026-08-13 | process/project-state | Naechsten Arbeitsblock verbindlich priorisiert

- Prozessfeedback: Der Abschluss der erfolgreichen Datenbankrunde enthielt
  keinen ausreichend klaren Folgeblock; zudem nannte `PROJECT_STATUS.md` die
  bereits erledigte Migration noch als naechste Aktion.
- Korrektur: Auth-ADR fuer den ersten internen Admin-/Intern-Login ist jetzt der
  eine empfohlene Folgeblock, inklusive Zweck, Eingaben, Ergebnissen und
  Definition of Done. Janay-Workflow und verschluesseltes Off-Server-Backup
  sind als parallele organisatorische Gates getrennt ausgewiesen.
- Skill-Learning: Wiederholte Evidenz zum fehlenden Steuerungs-Checkpoint und
  ein neues Learning zu verschwindenden Pflichtbefehlen wurden in
  `SKILL_FEEDBACK_LOG.md` dokumentiert. `AGENTS.md` enthaelt nun einen lokalen
  verbindlichen Abschluss- und Steering-Checkpoint.
- Freigabegrenze: kein Commit, Push, Deployment, Login-Code oder Echtdatenbetrieb
  durch diese Planungs- und Prozesskorrektur.

## 2026-08-13 | requirements/architecture/implementation | Portal-Fachmodell v0.1 uebernommen

- Synchronisation: `main` wurde per Fast-Forward von `e8e0704` auf `e434f01`
  aktualisiert. Die neue PWA-first-Planung vom Zweitrechner wurde uebernommen;
  `.tmp/` blieb unberuehrt.
- Quelle: Der ausdruecklich freigegebene Ordner `Quellen/13.08.2026` und die
  Product-Owner-Arbeitsmappe v0.2 wurden vollstaendig ausgewertet. Die Excel hat
  Vorrang vor den daraus abgeleiteten Begleitdokumenten.
- Bestaetigt: B2B-first Kern mit Benutzern/Mehrfachrollen, Unternehmen und
  Ansprechpartnern, Coaches/Themen/Leistungen, Coaching-Anfragen und Audit.
  Die Rechtematrix fuer Admin, Intern, Coach und Firmenkontakt ist weitgehend
  bestaetigt und deny-by-default zu implementieren.
- Provisorisch: Anfrage-Statuswerte, Coach/Leistung und Portalaccount-Bruecken
  sind vorbereitbar. Finale Transitionen, Automation und die Reihenfolge von
  Coach-Anfrage, Angebot und Auftrag bleiben Janay-/Praxis-Gate.
- Deferred: Auftraege, Termine, Dokumente, Feedbacktabellen, Reportingformeln,
  B2C, Teilnehmer, Vertraege/Rechnungen, Kalender, Push, Offline-Fachdaten und
  KI-Matching.
- Dokumente: Domainmodell, Schema-Spezifikation, Portal-IA, RBAC-Matrix und
  Open-Gates-Liste wurden in sichere Projektpfade ueberfuehrt. Der alte
  `initial-data-model.md` ist als historischer Vorentwurf markiert.
- Implementierung: `0001_portal_core.sql` und ein ausschliesslich synthetischer,
  mit `ROLLBACK` endender Smoke-Test wurden lokal erstellt. Migration `0001`
  wurde nach einem geschuetzten Pre-Migration-Dump auf die leere VPS-Staging-
  Datenbank angewendet und der Smoke-Test erfolgreich ausgefuehrt. Alle
  synthetischen Testdaten wurden zurueckgerollt.
- Verifikation: 15 Tabellen gehoeren `competence_hub_owner`, vier Arbeitsrollen
  sind vorhanden und Benutzer, Unternehmen, Anfragen sowie Audit-Ereignisse
  enthalten jeweils null Datensaetze. Die Runtime-Rolle darf weder das Schema
  erweitern noch Migrationsdaten lesen oder Anfragen physisch loeschen.
- Betrieb: Chatbot, Nginx, Fail2ban und PostgreSQL blieben aktiv. PostgreSQL
  lauscht weiterhin nur auf `127.0.0.1:5432`. Ein lesbarer Post-Migration-Dump
  wurde angelegt. Pre- und Post-Migration-Dump sind `postgres`-eigen und auf
  Modus `0600` gesetzt; das Backupverzeichnis steht auf `0700`. Das
  verschluesselte Off-Server-Backup bleibt Pflicht vor Echtdaten.
- Sicherheit: keine Echtdaten, Secrets oder `.env` gelesen oder geschrieben;
  keine produktive Migration, kein Backend-Deployment, Commit oder Push.

## 2026-08-11 | architecture/planning | PWA-first als zukünftige App-Distributionsrichtung aufgenommen

Die bereits vorbereitete PWA-Strategie wurde gegen den aktuellen Portal-,
Backend- und Datenbankrahmen geprüft und restart-sicher im Projektgedächtnis
verankert.

- Bevorzugte Richtung: Nach einem stabilen Webapp-Kern soll eine gemeinsame,
  mobile-first geplante und installierbare PWA der erste Mobile-Client sein.
- Distribution: App Stores sind kein initiales Gate. Native Android-/iOS-Clients
  bleiben optional und werden nur bei nachgewiesenem Bedarf samt dann aktuellen
  Distributionsbedingungen neu bewertet.
- Sicherheitsgrenze: Website und PWA greifen ausschließlich über die geschützte
  Backend-API zu; PostgreSQL bleibt serverseitig gekapselt. Authentifizierte
  Daten bleiben standardmäßig `NO_CACHE`.
- Separate Entscheidungen: Manifest/Installierbarkeit, Service Worker,
  Cache/Offline, Push und native Releases sind spätere eigene Slices. Push darf
  standardmäßig keine sensiblen Inhalte enthalten.
- Konfliktprüfung: Keine sichere Architekturdatei legt bereits eine native
  Android- oder iOS-App verbindlich fest. Der ältere Brief nannte nur allgemein
  eine spätere Mobile-App und wurde auf PWA-first/native optional präzisiert.
- Ausführung: keine PWA/Webapp implementiert, keine Dependency installiert,
  keine Serveränderung, kein Commit, Push oder Deployment ausgelöst.

## 2026-08-07 | deployment/review | Verbesserter Frontendstand auf GitHub Pages veröffentlicht

- Commit `19a6f49` wurde nach `origin/main` gepusht und anschließend bewusst
  über den manuellen Workflow `Publish GitHub Pages review` veröffentlicht.
- GitHub-Actions-Run `31172489046`: Build und Deploy erfolgreich.
- Review-URL: `https://dp-manuel.github.io/CompetenceHub/`.
- Verifikation: Startseite und `/ueber-uns/` liefern HTTP 200; Assetpfade nutzen
  `/CompetenceHub`. Interner Review-Banner sowie
  `noindex, nofollow, noarchive` sind aktiv.
- Die Vorschau dient ausschließlich der Kolleginnen-/Stakeholderprüfung. Sie
  ersetzt nicht die spätere freigegebene Veröffentlichung unter der
  kanonischen Donner-+Partner-Domain.

## 2026-08-07 | requirements/operations | Portalumfang und Würzburg-Backupkandidat bestätigt

- Backupkandidat: Manuels D+P-Arbeitsrechner am Standort Würzburg soll als
  erstes Off-Server-Ziel geprüft werden. Vorgesehen ist ein Pull des bereits
  verschlüsselten Dumps vom VPS ohne eingehende Standortfreigabe. Vor realen
  Daten müssen Datenträgerverschlüsselung, Zugriffsschutz, Aufbewahrung und ein
  Restore aus genau der heruntergeladenen Kopie nachgewiesen werden.
- Dateninput: Manuel erstellt eine Excel-Arbeitsmappe als Ideengeber für Felder
  und Zusammenhänge. Sie wird vor einem Import fachlich und technisch gemappt;
  synthetische Beispiele ersetzen vorerst reale Daten.
- Rolleninput: Manuel liefert die vorgesehenen Nutzer und Rechte. Bis dahin
  wird keine Rollenmatrix oder Berechtigung stillschweigend erfunden.
- Portalrichtung: Hinter dem Login entsteht eine getrennte Webapp für interne
  Nutzer-/Rollenverwaltung, Firmen, Coaches, Feedback und Statistiken. Der
  erste Slice umfasst Authentifizierung, serverseitige Autorisierung,
  Mehrfachrollen und Auditnachweise; die Fachmodule folgen schrittweise.
- Anforderungen: Der aktuelle Rahmen steht in
  `requirements-engineering-update-2026-08-07.md`; keine Implementierung,
  Veröffentlichung oder Verarbeitung realer Daten wurde ausgelöst.

## 2026-08-07 | operations/database | VPS gewartet und PostgreSQL-Staging abgenommen

- Zeitfenster: Das ursprünglich für Samstag geplante Wartungsfenster wurde in
  Manuels reservierten Freitag-Arbeitstag vorgezogen. Der Chatbot war vor und
  nach allen Änderungen öffentlich gesund; der geplante Crawl blieb aktiv.
- System: Ubuntu-Pakete wurden aktualisiert und der VPS kontrolliert neu
  gestartet. Aktiv ist Kernel `6.8.0-137-generic`; Chatbot, Nginx und Fail2ban
  liefen danach ohne Neustartzähler oder Health-Fehler weiter.
- Netzwerk: UFW ist aktiv mit `deny incoming`; öffentlich erlaubt sind nur
  22/80/443. PostgreSQL lauscht ausschließlich auf `127.0.0.1:5432`.
- Datenbank: PostgreSQL 16.14 und `postgresql-contrib` sind installiert. Die
  leere Datenbank `competence_hub_staging` besitzt getrennte Rollen für Owner,
  Migrationen und die eingeschränkte Anwendung. Passwörter wurden nur
  interaktiv in `psql` gesetzt und weder geteilt noch gespeichert.
- Authentifizierung: lokale Socket-Anmeldung nutzt `peer`; Loopback-TCP nutzt
  SCRAM-SHA-256. Das App-Konto darf DML nach Migrationen ausführen, aber keine
  Tabellen anlegen. Der Migrator kann kontrolliert die NOLOGIN-Ownerrolle
  übernehmen. Standardrechte für zukünftige Funktionen wurden `PUBLIC`
  entzogen und ausschließlich der App-Rolle erteilt.
- Restore-Nachweis: Ein synthetischer Datensatz wurde als geschützter lokaler
  Custom-Dump gesichert, in eine separate Testdatenbank wiederhergestellt und
  mit Eigentümer- und App-Rechten geprüft. Testdatenbank und Prüftabelle wurden
  anschließend entfernt; das Anwendungsschema ist wieder leer.
- Backupgrenze: Der lokale Dump liegt mit Modus `600` unter einem nur für
  PostgreSQL zugänglichen Serververzeichnis. Das ist noch kein vollständiges
  Produktivbackup. Reale Firmen-/Personendaten bleiben gesperrt, bis eine
  verschlüsselte externe D+P-Kopie aus genau dieser Kopie erfolgreich
  wiederhergestellt wurde.
- Projektartefakt: `apps/webapp/database/bootstrap-staging.sql` dokumentiert
  den geheimnisfreien, least-privilege Bootstrap. Kein Deployment, Commit oder
  Push wurde ausgeführt.

## 2026-08-07 | operations/decision | Wartungsfenster und Nicht-Cloud-Backupweg bestätigt

- Wartungsfenster: Samstag, 08.08.2026, 09:00 Uhr Europe/Berlin ist bestätigt.
- Sudo: Manuel gibt das Passwort ausschließlich interaktiv in seiner eigenen
  SSH-Sitzung ein; es wird nicht geteilt oder gespeichert.
- Backupgrenze: Für IONOS Object Storage und Cloud Backup fehlt aktuell die
  interne Berechtigung. Die PostgreSQL-Installation bleibt deshalb zunächst
  staging-only mit synthetischen Daten.
- Zwischenlösung: Dump/Restore wird lokal getestet. Vor Produktivdaten wird ein
  verschlüsselter Dump per SCP auf einen D+P-kontrollierten, verschlüsselten
  Rechner, eine interne Freigabe oder ein verschlüsseltes Wechselmedium kopiert
  und von dieser Kopie wiederhergestellt.
- Die lokale BitLocker-Abfrage konnte ohne Windows-Administratorrechte nicht
  ausgeführt werden; Verschlüsselung des Zielgeräts bleibt vor Nutzung zu
  bestätigen.
- Keine Serveränderung oder Installation ausgeführt.

## 2026-08-07 | operations/planning | Crawl-Zeit und Backupoptionen verifiziert

- Timer: Der aktive Chatbot-Crawl ist freitags für circa 15:22 UTC angesetzt,
  im August also circa 17:22 Uhr deutscher Zeit. Der letzte Lauf endete mit
  `success` und Status 0.
- Wartung: Samstagvormittag ist das bevorzugte Fenster. Freitagabend kommt erst
  ab 19:30 Uhr und nur nach erfolgreichem Crawl-/API-Healthcheck infrage.
- Backup: IONOS Object Storage wird als primäres Ziel für verschlüsselte,
  portable PostgreSQL-Dumps empfohlen; IONOS Cloud Backup kann ergänzend den
  ganzen VPS sichern. Eine weitere periodische D+P-interne Kopie reduziert das
  verbleibende Anbieter-/Kontorisiko.
- Der vorhandene Website-Webspace ist kein geeignetes Backupziel, solange kein
  ausdrücklich nicht öffentlich erreichbarer Speicherbereich bestätigt ist.
- Keine Wartung, Installation, Konfigurationsänderung oder Datenverarbeitung
  ausgeführt.

## 2026-08-06 | decision/runbook | PostgreSQL 16 freigegeben

Manuel hat ADR 0002 und PostgreSQL 16 als Datenbank für das eigenständige
Competence-Hub-Backend auf dem VPS freigegeben.

- ADR 0002 steht auf `Accepted`; PostgreSQL bleibt ausschließlich lokal und
  wird nicht über einen öffentlichen Datenbankport angeboten.
- `postgresql-16-installation-runbook.md` beschreibt Preflight,
  Systemwartung/Neustart, Firewallprüfung, Installation, getrennte Rollen,
  Secretgrenzen, Backup, Restore-Test, Abnahme und Rollback.
- Noch offen: Wartungsfenster, interaktive sudo-Ausführung und verschlüsseltes
  Off-Server-Backupziel.
- Keine Installation, Aktualisierung, Neustart, Passwortverarbeitung oder
  Serveränderung ausgeführt.

## 2026-08-06 | decisions/database | Ansprechpartner, Mailbox und PostgreSQL-Richtung geklärt

Manuel hat weitere Verantwortlichkeiten bestätigt und die vorhandene, bislang
ungenutzte IONOS-MySQL-Datenbank eingeordnet.

- Recht: Lars Donner ist der rechtliche Ansprechpartner. Die konkrete
  Gesellschaft, Vertrags-/Rechnungsangaben und das finale Impressum folgen.
- Kontakt: Janay Rappelt übernimmt
  `competencehub@donner-partner.de`; Reaktionszeit und Abwesenheitsvertretung
  werden noch als kurzer Betriebsprozess festgelegt.
- IONOS-Datenbank: Eine MySQL-Datenbank und Zugangsdaten existieren, werden aber
  nicht in Projektdateien übernommen. Wegen der bestätigten Beschränkung auf den
  IONOS-Webspace ist sie für das VPS-Backend nicht verwendbar.
- VPS-Pakete: Rein lesend bestätigt wurden PostgreSQL 16 und MariaDB 10.11 als
  verfügbare Ubuntu-Pakete; keines ist installiert.
- Entscheidungsvorlage: ADR 0002 schlägt eine lokale, nicht öffentlich
  erreichbare PostgreSQL-Datenbank auf dem VPS vor. Installation bleibt bis zu
  expliziter ADR-, Wartungs-, Firewall- und Backupfreigabe aus.
- Konfiguration: `.env.example` enthält nur PostgreSQL-Platzhalter. Die
  missverständlichen SSH-Felder wurden entfernt; SSH-Zugang gehört nicht in die
  Anwendungs-ENV.
- Keine echten Zugangsdaten gelesen oder gespeichert; keine Installation,
  Aktualisierung, Datenbankänderung oder Veröffentlichung ausgeführt.

## 2026-08-06 | infrastructure/security/planning | VPS-Inventur abgeschlossen und Betrieb geklärt

Manuel hat die read-only Prüfung des bestehenden Chatbot-VPS sowie dessen
grundsätzliche Nutzung für einen strikt getrennten Competence-Hub-Dienst
freigegeben. Es wurden ausschließlich System-, Ressourcen-, Dienst-, Port- und
Versionsmetadaten gelesen.

- Kapazität: Ubuntu 24.04 LTS, 6 vCPUs, 7,7 GiB RAM mit rund 6,8 GiB verfügbar,
  rund 228 GiB freier Speicher und sehr geringe Last. Ein kleiner Pilot ist
  kapazitiv realistisch.
- Betriebsbild: Nginx veröffentlicht 80/443, SSH nutzt 22 und der Chatbot bindet
  Uvicorn ausschließlich an `127.0.0.1:8000`. Fail2ban, unattended-upgrades,
  Certbot und der wöchentliche Chatbot-Crawler sind aktiv.
- Gates: System-/Kernelupdates und ein Neustart stehen aus. Firewall-/Fail2ban-
  Details konnten ohne interaktive sudo-Freigabe nicht verifiziert werden. Es
  gibt keinen nachgewiesenen App-/Datenbank-Off-Server-Backup- und Restoreweg;
  kein Swap und keine aktive Datenbank sind vorhanden.
- Bewertung: Conditional Go für eine isolierte Staging-/Pilotinstanz mit
  Testdaten. Noch kein Go für produktive personenbezogene Daten.
- Verantwortung: Manuel übernimmt Serverbetrieb, Patchen, Monitoring, Backup
  und Notfälle; Thomas Roß ist als EDV-Leiter Produktionsfreigabeowner.
  `competencehub.donner-partner.de` ist die kanonische Domain.
- Versionsverwaltung: GitHub bleibt Quellcode- und Releasequelle. Datenbanken,
  private Dateien und Off-Server-Backups werden separat gesichert.
- Dokumentation: `vps-read-only-inventory-2026-08-06.md` und
  `versioning-and-operations-plan.md` ergänzen Hostingentscheidung, Projektplan
  und Restart-Handoff.
- Sicherheit: keine Secrets, Konfigurationen, Logs, Datenbanken oder Nutzdaten
  geöffnet; keine Installation, Aktualisierung, Neustart oder Veröffentlichung.

## 2026-08-06 | architecture/planning/frontend | EDV-Rückmeldung in Betriebsplan überführt

Die ausdrücklich freigegebene EDV-Rückmeldung und der Status des vorhandenen
Donner-+Partner-Chatbot-Projekts wurden ohne Zugriff auf Zugangsdaten oder
Anwendungsdaten ausgewertet.

- IONOS: Der vorhandene Webspace eignet sich für die statische Astro-Website,
  aber nicht für dauerhaft laufende Node-/Python-Dienste. Die IONOS-MySQL-
  Datenbank ist ausschließlich vom eigenen Webspace erreichbar und daher nicht
  für ein Backend auf dem separaten VPS nutzbar.
- Domains: `competencehub.donner-partner.de` und die Bindestrich-Variante zeigen
  bereits auf den Webspace und sind durch Wildcard-TLS abgedeckt. Eine
  kanonische Domain und Weiterleitung müssen noch festgelegt werden.
- VPS: Der vorhandene Server ist nicht leer, sondern betreibt bereits den
  Chatbot mit FastAPI und systemd. Er bleibt nur eine Kandidatenplattform. Vor
  Co-Hosting sind organisatorische Freigabe, read-only Ressourcen-/Betriebs-
  inventur, Datenschutzentscheidung und vollständige technische Trennung nötig.
- Planung: `docs/architecture/hosting-runtime-decision-2026-08-06.md` vergleicht
  die Optionen und definiert Entscheidungsowner, Arbeitsblöcke und
  Deployment-Gates. `server-database-bootstrap.md`, `PROJECT_PLAN.md` und
  `PROJECT_STATUS.md` wurden an die bestätigte Infrastruktur angepasst.
- Frontend: Das freigegebene Porträt von Frau Janay Rappelt ersetzt nun auch in
  der Kontaktbox der Startseite den bisherigen Personen-Platzhalter.
- Verifikation: Astro prüft 36 Dateien ohne Fehler, Warnungen oder Hinweise und
  erzeugt 28 statische Seiten. Kein Serverlogin, Datenbankzugriff, Deployment,
  Commit oder Push wurde ausgeführt; `.tmp/` blieb unberührt.

## 2026-08-06 | frontend/planning | Startseiten-Hub zentriert und Über-uns-Weg ergänzt

Stakeholderfeedback zur Orientierung im Living Hub wurde als lokaler,
abgegrenzter Frontend-Slice umgesetzt.

- Startseite: Einordnung und Nutzenversprechen stehen nun über dem zentrierten
  Hub-Netzwerk; Bedarfsklärung, Hub-Erkundung und direkte Zielgruppenwege folgen
  darunter. Die lokalen A/B/C-Prototypseiten bleiben unverändert nutzbar.
- Hub-Kern: Der zentrale Kreis ist ein semantischer Link zu der neuen Route
  `/ueber-uns` und behält seine Hover- und Fokusreaktion auf die Verbindungen.
- Über uns: Die neue Seite erklärt den Competence Hub als Angebot von Donner +
  Partner, die Anliegen-zu-Expertise-Logik und den persönlichen Einstieg, ohne
  Unternehmensgeschichte, Referenzen oder Wirkungsversprechen zu erfinden.
- Ansprechpartnerin: Das ausdrücklich freigegebene Porträt von Frau Janay
  Rappelt aus `Quellen/Über uns` ist unverändert als öffentliches Team-Asset
  eingebunden. Ein eigener responsiver Abschnitt erklärt ihre Rolle zwischen
  Interessierten, Unternehmen und Coaches und führt zum Kontaktweg.
- Hub Journey: Die vier visuellen Kreise springen zu den jeweiligen
  Scrolltext-Schritten auf der Startseite. Erst die ausführlichen Text-CTAs
  führen weiterhin gezielt zu Unternehmen, Coaches, Leistungen oder Kontakt.
- Zukunftsplanung: Bedarfserhebung/Fragebogen, Coach-Auswahl, Anfrage,
  Angebot/Vertrag, Durchführung, Unternehmensfeedback und freigegebene
  Kundenstimmen sind als eigener späterer Workstream in `PROJECT_PLAN.md`
  dokumentiert. Das statische Frontend täuscht keine dieser Funktionen vor.
- Verifikation: Astro prüft 36 Dateien ohne Fehler, Warnungen oder Hinweise und
  erzeugt 28 statische Seiten. Startseite und `/ueber-uns/` liefern HTTP 200;
  Desktop und echte 390-Pixel-Mobil-Emulation zeigen keinen horizontalen
  Überlauf. Alle Journey-Hashes bleiben auf `/` und aktivieren den richtigen
  Schritt.
- Veröffentlichung: nur lokal unter `http://127.0.0.1:4321/`; kein Commit,
  Push oder Deployment ausgelöst. `.tmp/` blieb unberührt.

## 2026-08-05 | frontend/assets | Porträt von Frau Dr. Stefanie Becker integriert

Das ausdrücklich freigegebene Bild aus `Quellen/Coach/06. Dr. Stefanie Becker/Bild.docx`
wurde in Übersicht und Profil eingebunden.

- Quelle und Datenschutz: ausschließlich die einzelne Mediendatei aus
  `Bild.docx` wurde extrahiert. E-Mail, Profil-PDF und Zertifikate wurden für
  diese Änderung nicht geöffnet; Kundenreferenzen bleiben weiterhin außen vor.
- Asset: das eingebettete 642 × 594 px PNG wurde ohne übernommene Metadaten als
  `stefanie-becker.webp` mit 26 KB gespeichert.
- Frontend: die gemeinsame Coach-Datenquelle enthält Bildpfad und feste
  Abmessungen; der bisherige Monogramm-Platzhalter im Stefanie-Becker-Profil
  wurde durch das Porträt mit Alternativtext und Bildunterschrift ersetzt.
- Verifikation: Übersicht, Profil und Bild antworten lokal mit HTTP 200. Astro
  prüft 35 Dateien mit 0 Fehlern, 0 Warnungen und 0 Hinweisen und erzeugt 27
  statische Seiten.
- Einschränkung: die eingebettete Browser-Verbindung lief erneut ins Zeitlimit.
  Übersicht und Profil wurden zur visuellen Zuschnittskontrolle im sichtbaren
  Standardbrowser geöffnet.
- Nächster Schritt: sichtbaren Bildausschnitt in Übersicht und Profil bestätigen;
  Kundenreferenzen bleiben bis zu einer gesonderten Freigabe ausgeschlossen.

## 2026-08-05 | frontend/verification | Themensprung zeigt vollständiges Filterraster

Das von Manuel gemeldete Scrollproblem auf der Coach-Übersicht wurde im
laufenden lokalen Review korrigiert.

- Ursache: Nach der Themenwahl wurde die Ergebnis-Statuszeile am Viewport
  ausgerichtet. Dadurch lag die erste Reihe der Themenfelder oberhalb des
  sichtbaren Bereichs.
- Änderung: Der Scrollanker ist nun das gesamte Themenraster. Ein
  `scroll-margin-top` von 130 px berücksichtigt den sticky Seitenkopf; der
  Fokus bleibt auf dem ausgelösten nativen Button und reduzierte Bewegung wird
  weiterhin respektiert.
- Verifikation: aktualisierte lokale Vorschau liefert `/coaches` mit HTTP 200;
  Astro prüft 35 Dateien mit 0 Fehlern, 0 Warnungen und 0 Hinweisen und erzeugt
  27 statische Seiten.
- Einschränkung: Die eingebettete Browser-Verbindung lief erneut ins Zeitlimit.
  Die aktualisierte Seite wurde sichtbar im Standardbrowser geöffnet; Manuels
  visuelle Bestätigung bleibt der abschließende UI-Check.
- Nächster Schritt: Sichtprüfung des Sprungs in Desktop- und Mobilbreite; bei
  Freigabe keine weitere Änderung an der Filterlogik nötig.

## 2026-08-05 | verification/workflow | Lokale Vorschau und Zweitrechner-Handoff gesichert

Der aktuelle Stand wurde auf dem zweiten Rechner als sichtbare lokale Vorschau
bereitgestellt und die dafür relevanten Besonderheiten wurden restart-sicher
dokumentiert.

- Synchronisation: `main` und `origin/main` waren vor den Arbeiten identisch;
  `.tmp/` blieb ungetrackt und unberührt.
- Vorschau: Astro-Start direkt auf `Z:` hing. Eine geheimnisfreie lokale Kopie
  unter `C:\tmp` wurde stattdessen mit der vorhandenen Astro-Installation
  gestartet. `http://127.0.0.1:4321/` antwortete mit HTTP 200 und enthielt den
  aktuellen Mindforge-Inhalt.
- Anzeige: die eingebettete Browser-Verbindung lief erneut ins Zeitlimit; die
  verifizierte URL wurde deshalb sichtbar im Standardbrowser geöffnet.
- Rechnergedächtnis: `docs/architecture/second-workstation-setup.md` hält Pfade,
  Git/GitHub-Status, Node/npm-Regeln, Netzlaufwerk-Fallback, Browsergrenze und
  Sicherheitsregeln ohne Zugangsdaten fest. `AGENTS.md` verweist darauf.
- Skill-Feedback: ein wiederverwendbarer Multi-Workstation-/Windows-Preview-
  Bootstrap wurde in `SKILL_FEEDBACK_LOG.md` vorgeschlagen; noch keine Änderung
  am kanonischen CodexSkills-Repository.
- Verifikation: HTTP 200 und aktueller Seiteninhalt bestätigt; automatisierte
  visuelle und Tastaturprüfung bleibt wegen der Browser-Verbindung offen.
- Nächster Schritt: Manuel prüft die geöffnete Seite; nach Rückmeldung kann der
  betreffende UI-Slice gezielt angepasst und erneut lokal gezeigt werden.

## 2026-08-04 | frontend/content/workflow | Coach-Feedback und zweiter Rechner integriert

Das freigegebene Stakeholderfeedback und die neuen Coach-Unterlagen wurden als
abgegrenzter Frontend-Slice umgesetzt und auf dem zweiten Rechner verifiziert.

- Hub: Businesscoaching ist unter dem Mindforge-Oberbegriff gebündelt. Der
  separate Knoten entfällt; die Startseiten-Map besitzt acht Außenknoten.
  Mindforge verlinkt die eigenständige Businesscoaching-Seite weiterhin direkt.
- Coach-Netzwerk: Frau Dr. Stefanie Becker ist als sechstes freigegebenes Profil
  ohne Kundenreferenzen und ohne PDF-extrahiertes Porträt ergänzt. Herr T.
  Wegner-Neys Profil umfasst nun Technologie- und Prozessveränderung,
  Qualitätsmanagement, Mitarbeiterbeteiligung, Führung und Fachkräftesicherung;
  KI bleibt ein Nebenthema.
- Themenlogik: Mediation ist als allgemeiner, qualifikationsgebundener Bereich
  vorbereitet. Solange kein Coach ausdrücklich qualifiziert und freigegeben
  zugeordnet ist, zeigt der Filter einen transparenten Leerzustand.
- Interaktion: Themenauswahl aktualisiert einen sichtbaren Live-Status, filtert
  die Profile und scrollt reduziert-bewegungsbewusst zu den Ergebnissen. Die
  drei bisherigen Qualitätskarten wurden entfernt; FAQ-Köpfe erhielten mehr
  Raum.
- Anreden: sichtbare Coach-Namen verwenden Herr/Frau; die Kontaktperson wird als
  Frau Janay Rappelt bezeichnet.
- Requirements: hinzugefügt
  `docs/requirements/requirements-engineering-update-2026-08-04.md`.
- Verification: secret-freie lokale Build-Kopie mit Node 22; Astro prüft 35
  Dateien ohne Fehler, Warnungen oder Hinweise und erzeugt 27 statische Seiten.
  HTTP-Smoke-Checks bestätigen die betroffenen Routen, acht Hub-Knoten,
  Mindforge-Businesscoaching-Link, Mediation und Leerzustand.
- Einschränkung: direkte Builds auf `Z:` hingen nach der Typgenerierung; die
  in-app Browser-Verbindung lief zweimal ins Zeitlimit. Echte Desktop-/Mobil-
  und Tastaturprüfung bleibt vor einem öffentlichen Review manuell offen.
- Commit: `6bf28ec` (`Integrate coach feedback and profiles`). Kein öffentliches
  Deployment ausgelöst.
- Zweitrechner: GitHub-HTTPS-Zugriff und repository-lokale Autoridentität sind
  eingerichtet. `DP-Manuel/CodexSkills` wurde separat nach
  `Z:\IT Development Manuel\CodexSkills` geklont.
- Sicherheit: `.tmp/`, `.env*`, Zugangsdaten, private Nachweise und
  Kundenreferenzen blieben ausgeschlossen.
- Nächster Schritt: lokaler visueller/keyboard Review; danach separat über einen
  manuellen GitHub-Pages-Reviewlauf entscheiden.

## 2026-07-31 | release | Living-Hub-Review über GitHub Pages veröffentlicht

Der freigegebene Mittagsstand ist als GitHub-Pages-Review öffentlich
erreichbar.

- Website-Commit: `7f13cec` (`Extend Living Hub and coach discovery`) wurde
  nach `origin/main` gepusht.
- Workflow: `Publish GitHub Pages review`, Run `30620235023`; Build und Deploy
  wurden erfolgreich abgeschlossen.
- Review-URL: `https://dp-manuel.github.io/CompetenceHub/`
- Smoke-Test: Startseite, Leistungen, Coach-Übersicht und Goran-Celic-Profil
  antworten mit HTTP 200.
- Browserprüfung: Themenfilter, Hash-Direktlink `#thema-fuehrung`, Goran-Profil,
  Bilder und interne `/CompetenceHub`-Basispfade funktionieren öffentlich.
- Deploymentgrenze: Veröffentlichung bleibt ein manueller,
  freigabepflichtiger `workflow_dispatch`; Pushes deployen nicht automatisch.
- Lokale Grenze: `.tmp/` blieb ungetrackt und wurde weder geöffnet noch
  committed.

## 2026-07-31 | architecture/implementation | Coach-Themen skalierbar verknüpft

Die Coach-Übersicht kann Profile nun nach kanonischen Themenschwerpunkten
filtern, ohne Coaches bei Überschneidungen zu duplizieren.

- Datenbasis: Startseite und Coach-Übersicht verwenden
  `apps/website/src/data/coaches.ts` als gemeinsame öffentliche Quelle für
  Profile, Vorschautexte und Themenzuordnungen.
- Modell: Coaches und Themen sind viele-zu-viele verknüpft. Führung,
  Team-/Konfliktthemen oder Gesundheit können dadurch mehrere fachliche
  Perspektiven anzeigen.
- Darstellung: Ein kompaktes Themenraster filtert die vorhandenen Profile.
  Die Auswahl bleibt über `#thema-<id>` verlinkbar und wird barrierearm über
  `aria-pressed` und einen Live-Status vermittelt.
- Skalierungsgrenze: Kein dauerhaftes All-to-all-Diagramm. Eigene Themenseiten
  sind erst sinnvoll, wenn freigegebene fachliche Substanz über eine gefilterte
  Coach-Liste hinaus vorliegt.
- Dokumentation: `docs/architecture/coach-topic-network.md` beschreibt
  Datenmodell, visuelle Regeln, URL-Pfad und spätere Datenbankmigration.
- Visual QA: Das Themenraster nutzt Desktop vier, Tablet zwei und Mobil eine
  Spalte. Überschneidungen und Direktaufrufe per Hash wurden lokal geprüft.
- Bugfix: Primärbuttons bleiben beim Hover orange; der gewünschte Farbwechsel
  zwischen Primär- und Ghost-Button bleibt erhalten.
- Veröffentlichung: Nur lokal. Kein Commit, Push oder Deployment.

## 2026-07-31 | frontend/implementation | Living Hub auf Kernseiten erweitert

Die Living-Hub-Sprache der Startseite wurde als kleinerer, kontextbezogener
Seiteneinstieg auf vier priorisierte Unterseiten übertragen.

- Gemeinsame Komponente: `ConnectedPageHero.astro` verbindet H1, Einordnung,
  CTAs und drei passende, klickbare Nachbarknoten ohne die große Startseiten-Map
  zu duplizieren.
- Seiten: `/leistungen`, `/unternehmen`, `/businesscoaching` und `/mindforge`
  verwenden jeweils fachlich passende Verbindungen zu Angeboten, Zielgruppen
  oder vorhandenen Seitenankern.
- Interaktion: Außenknoten heben ihre Verbindung bei Hover und Tastaturfokus
  hervor. Der zentrale Kreis kann per Klick, Touch, Enter oder Leertaste
  eingerastet und mit Escape wieder gelöst werden.
- Konsistenz: Primäre Buttons, Ghost-Buttons, Textlinks und verlinkte
  Angebotskarten besitzen nun deutlichere, gemeinsame Hover-/Fokuszustände.
- Barrierefreiheit: Schaltersemantik, Fokusdarstellung, Reduced Motion und
  Farbkontraste wurden geprüft.
- Verifikation: Astro prüft 33 Dateien ohne Fehler, Warnungen oder Hinweise und
  erzeugt 26 statische Seiten. Alle vier Einstiege wurden bei 1440 und 390
  Pixeln ohne horizontalen Überlauf, Textkollision oder abgeschnittene Knoten
  geprüft.
- Veröffentlichung: Nur lokal. Kein Commit, Push oder Deployment.

## 2026-07-31 | planning | SEO, GEO & First-Party Authority eingeplant

`PROJECT_PLAN.md` enthält nun einen eigenen, mit dem Living-Hub-Frontend
verbundenen, aber getrennten SEO-/GEO-Workstream.

- Reihenfolge: zuerst Content Inventory für die fünf priorisierten Kernseiten,
  danach eine freigabebasierte Content-Evidence-Matrix.
- Grenzen: keine neuen Ratgeberseiten, erfundenen Autoritätssignale, privaten
  Rohquellen oder sensiblen Daten; GEO ergänzt klassische SEO.
- Status: reine Planung. Keine Content-Implementierung, Veröffentlichung oder
  Deployment-Aktion ausgelöst.

## 2026-07-31 | content/implementation | Goran Celic als fünfter Coach ergänzt

Der bestätigte Vertriebscoach Goran Celic wurde auf Basis des ausdrücklich
freigegebenen Quellenhinweises und seiner öffentlichen Website in das
Competence-Hub-Frontend aufgenommen.

- Coach-Netzwerk: Goran Celic erscheint mit offiziellem Porträt, Rolle und
  den bestätigten Hauptschwerpunkten Rhetorik und Vertrieb auf der Startseite
  sowie in der vollständigen Coach-Übersicht. Storytelling bleibt als
  ergänzende Methode sichtbar.
- Profilseite: `/coaches/goran-celic` bündelt Zielgruppen, Themen, Formate und
  Erfahrung in der sachlichen Competence-Hub-Tonalität. Kontaktanfragen laufen
  weiter über Janay Rappelt; die eigene Website ist als externe Quelle
  verlinkt.
- Inhaltsgrenze: Fremde Kundenlogos, externe Buchungssysteme und starke
  Umsatzversprechen der Ursprungsseite wurden nicht übernommen. Backend,
  Verfügbarkeiten und ausstehende interne Genehmigungen bleiben unberührt.
- Frontend: Das Coach-Raster passt sich nun flexibel an fünf Profile an und
  läuft als ruhiges, erweiterbares Laufband mit vier sichtbaren Profilbreiten.
  Auf Tablet und Mobil werden zwei beziehungsweise ein Profil dargestellt.
  Hover, Tastaturfokus und eine eigene Schaltfläche pausieren die Bewegung;
  bei `prefers-reduced-motion` bleibt die Liste statisch scrollbar.
- Lesbarkeit: Öffentliche Texte nennen keine feste Coach-Anzahl mehr. Der
  Profiltext auf dunklem Türkis ist hell gesetzt. Automatische Trennungen in
  Überschriften wurden global deaktiviert und die mobile Typografie so
  angepasst, dass lange Begriffe wie `Vertriebsbegleitung` vollständig
  umbrechen.
- Stakeholderfeedback: Die bisherige Website-Richtung wurde aus mehreren
  Abteilungen ausschließlich positiv bewertet.
- Verifikation: Astro prüft 32 Dateien ohne Fehler, Warnungen oder Hinweise und
  erzeugt 26 statische Seiten. Coach-Laufband, Pausezustand, Kontrast und
  Profilseite wurden lokal im Browser geprüft. Die Laufband-Spalte ist gegen
  Überbreite begrenzt; Einleitung und Pauseknopf bleiben bei 1200, 1440 und
  2048 Pixeln vollständig sichtbar. Die wichtigsten Seiten zeigen bei 390
  Pixeln weder horizontalen Überlauf noch überbreite Überschriften.
- Veröffentlichung: Nur lokal. Kein Commit, Push oder Deployment.

## 2026-07-30 | design/implementation | Living Hub C2 auf Startseite übernommen

Die freigegebene asymmetrische Living-Hub-Variante C2 ersetzt den bisherigen
oberen Connected-Core-Einstieg der Startseite.

- Startseite: Der produktive Hero verbindet die zentrale Hub-Map mit der
  Aussage `Wo Anliegen und passende Expertise zusammenfinden.` sowie direkten
  Einstiegen für Unternehmen, Mindforge und Kontakt. Variantenumschalter und
  Prototyp-Beschriftungen erscheinen nur auf den lokalen Vergleichsrouten.
- Bestehende Inhalte: Trust-Strip, Hub-Journey, Coach-Vorschau und persönlicher
  Kontaktabschluss bleiben vollständig erhalten.
- Feinkorrekturen: Der Unternehmensknoten wurde auf breiten Viewports aus der
  Überschrift herausgerückt. Zwischen `Competence` und `Hub` liegt ein kleiner
  zusätzlicher Abstand. `zusammenfinden` bleibt auch mobil vollständig und
  ungetrennt sichtbar.
- Responsive: Ab 1100 Pixeln wird die asymmetrische Komposition gestapelt;
  mobile Hub-Knoten bleiben zweispaltig und alle Ziele anklickbar.
- Verifikation: Startseite und Prototyp wurden bei 1920, 1000 und 500 Pixeln
  lokal gerendert. Der abschließende Astro-Build ist fehlerfrei.
- Veröffentlichung: Commit, Push und das manuelle GitHub-Pages-Review wurden
  nach lokaler Abnahme ausdrücklich freigegeben.

## 2026-07-30 | design/prototype | Drei lokale Living-Hub-Heros umgesetzt

Das neue Living-Hub-Konzept wurde als begrenzter, lokal vergleichbarer
Frontend-Prototyp umgesetzt. Die bestehende Startseite unter `/` bleibt
unverändert.

- Vergleich: Drei interaktive, untereinander verlinkte Varianten stehen unter
  `/prototyp/living-hub-a`, `/prototyp/living-hub-b` und
  `/prototyp/living-hub-c` bereit. A inszeniert eine vollständig zentrale
  Hub-Halle, B ergänzt Orientierungsdocks für Unternehmen und Mindforge, C
  vergleicht einen asymmetrischen Text-Core-Einstieg.
- Wiederverwendung: Alle Varianten verwenden dieselbe bestehende
  `CompetenceHubMap` mit echten Links sowie dieselbe `HubJourney`. Die stabile
  Map erhielt nur einen optionalen Präsentationsmodus.
- Interaktion: Feine Pointer-Parallaxe, eine ruhige Core-Signalisierung und ein
  direkter Sprung führen vom Hero in die vorhandene Hub-Journey. Touch,
  Tastaturbedienung und `prefers-reduced-motion` werden berücksichtigt.
- C2-Entscheidung: Der asymmetrische Einstieg ist die bevorzugte Richtung. Der
  erklärende Zwischenabschnitt wurde mangels Kundennutzen entfernt. Variante C
  besitzt eine eigene Knoten- und Liniengeometrie, damit kein Satellit vom
  großen Core verdeckt wird. Das Schlüsselwort `zusammenfinden` bleibt in
  jeder Überschriftenbreite ungetrennt. Unter 1100 Pixeln wird die Komposition
  kontrolliert gestapelt.
- Sicherheit/SEO: Die Prototypseiten sind ausdrücklich `noindex`; es wurden
  keine neuen Abhängigkeiten, Provider, Backend-Funktionen oder Deployments
  ergänzt.
- Verifikation: Die drei Hero-Varianten wurden lokal bei 1440 Pixeln und in
  schmaler Darstellung gerendert. Mobile Hub-Knoten nutzen für bessere
  Lesbarkeit zwei Spalten. Astro prüft 31 Dateien ohne Fehler, Warnungen oder
  Hinweise und erzeugt 25 statische Seiten.
- Veröffentlichung: Nur lokal. Kein Commit, Push oder Deployment.

## 2026-07-30 | handoff/release | Frontendstand für Konzeptreview übergeben

Der aktuelle Website-, Design- und Projektstand wurde für die Übergabe an eine
weitere KI konsolidiert.

- Interaktion: Die Mindforge-Prozessnummern besitzen mehr Abstand zum Text.
  Sekundärbuttons werden projektweit bei Hover oder Tastaturfokus orange; in
  Button-Gruppen wechselt der zugehörige Primärbutton auf Weiß. Einzelne
  Buttons erhalten eine sichtbare türkise Interaktionsbetonung.
- Übergabe: `CHATGPT_PROJECT_BRIEF.md` wurde vollständig auf den Stand vom
  30.07.2026 gebracht. Enthalten sind Produktpositionierung, Funktionen,
  Seiten, Komponenten, Designregeln, Ordnerstruktur, Stack, Deployment,
  Webapp-/Datenbankgrenzen, offene Punkte und Sicherheitsregeln.
- Sicherheit: `Quellen/`, `.env*`, Zugangsdaten, `.tmp/` und private
  Quelldokumente wurden weder gelesen noch in die Übergabe übernommen.
- Verifikation: Astro prüft 27 Dateien ohne Fehler, Warnungen oder Hinweise und
  erzeugt 22 statische Seiten. Prozessabstand und verallgemeinerte
  Buttonzustände wurden zusätzlich lokal im Browser geprüft.
- Veröffentlichung: Commit und Push auf `main` sind freigegeben. Der
  GitHub-Pages-Review-Workflow bleibt ein separater manueller Schritt und wird
  ohne erneute ausdrückliche Freigabe nicht gestartet.

## 2026-07-29 | requirements/implementation | Mindforge und Elisabeth erweitert

Der freigegebene Requirements-Engineering-Eintrag vom 29.07.2026 und die neuen
Unterlagen zu Elisabeth Schwabauer wurden lokal in die Website übertragen.

- Markenarchitektur: Competence Hub bleibt die Dachmarke. Mindforge ist als
  eigener Bereich für Life Coaching, Resilienz, Mindset und persönliche
  Entwicklung eingebunden.
- Zielgruppen: Die Website spricht nun neben Unternehmen auch Privatpersonen
  an. Kontaktweg, Leistungsübersicht, Startseite und Coach-Netzwerk wurden
  entsprechend geöffnet.
- Angebote und Preise: Die freigegebenen Privat- und Firmenpakete werden mit
  Umfang, 90-Minuten-Einheiten und korrektem Mehrwertsteuerhinweis dargestellt.
  `Sustainable Growth` wird als `Nachhaltige Entwicklung` geführt.
- Assessment Center: Der kleinere Spezialbereich verbindet Recruiting und
  Personalauswahl mit Development Assessment Center und anschließender
  Mindforge-Personalentwicklung. Beide freigegebenen Leistungsstufen und Preise
  sind auf der Unternehmensseite sichtbar.
- Elisabeth Schwabauer: Das freigegebene Foto wurde lokal als 1200 x 1800
  Pixel großes WebP ohne Quelldokumente übernommen. Die Heilpraktikererlaubnis
  wird nur als Zusatzqualifikation genannt; ein Therapieangebot wird
  ausdrücklich ausgeschlossen. Fehlendes Zitat, Formate und Verfügbarkeit sind
  klar als offene Profilangaben markiert.
- Dokumentation: Die Entscheidungen sind datensparsam in
  `docs/requirements/requirements-engineering-update-2026-07-29.md`
  festgehalten; private Kontaktdaten, Geburtsdaten und Zeugnisse wurden nicht
  in Website oder Projektdokumentation übernommen.
- Interaktionskorrektur: Die vier Kreise der Hub-Journey führen nun direkt zu
  Unternehmen, Coaches, Leistungen und Kontakt. Auf der Mindforge-Seite
  wechseln die Zielgruppen-Buttons gemeinsam ihren Zustand, alle drei
  Satelliten berühren den Mindforge-Kern ohne Linienüberlagerung und die
  Prozessnummern besitzen außen eine feine grüne Kontur.
- Verifikation: Astro prüft 27 Dateien ohne Fehler, Warnungen oder Hinweise und
  erzeugt 22 statische Seiten. Mindforge, Startseiten-Hub, Unternehmensseite
  und Elisabeth-Profil wurden bei 1440 und 500 Pixeln gerendert. Der gekoppelte
  Mindforge-Buttonzustand wurde zusätzlich im lokalen Browser geprüft.
- Lokale Nachkorrektur: Zwischen den nummerierten Prozesskästen und ihren
  Texten liegt nun mehr Abstand. Der gekoppelte Orange-Weiß-Wechsel gilt für
  alle vorhandenen Primär-/Sekundär-Button-Gruppen; einzelne Buttons und der
  Formularbutton besitzen ebenfalls einen deutlichen Hover- und
  Tastaturfokuszustand. Build und Browserprüfung sind erfolgreich.
- Veröffentlichung: Commit `a33ff12` wurde auf `main` gepusht und mit dem
  manuellen GitHub-Pages-Workflow `30483085264` erfolgreich als Review unter
  `https://dp-manuel.github.io/CompetenceHub/` veröffentlicht. Startseite,
  Mindforge, Unternehmen und Elisabeths Coach-Profil antworteten anschließend
  öffentlich mit HTTP 200 und enthielten die erwarteten neuen Inhalte.

## 2026-07-24 | design/implementation | Startseite als Connected Story verdichtet

Das freigegebene Variantenkonzept B wurde lokal umgesetzt und auf eine klarere
B2B-Erzählung reduziert.

- Hub-Bühne: Der zentrale Competence Hub ist deutlich größer, enthält nur noch
  Markenname und Nutzensatz und beginnt ohne übergroße vertikale Leerfläche
  direkt unter der Navigation.
- Beziehungen: Dezente Hauptverbindungen bleiben bereits im Ruhezustand
  sichtbar; Hover, Fokus und Aktivierung zeigen weiterhin die relevanten
  Zusammenhänge und den umlaufenden Orientierungspunkt.
- Scroll-Erzählung: Die neue Komponente `HubJourney.astro` führt schrittweise
  durch Anliegen, Expertise, Format und persönliche Begleitung. Desktop nutzt
  eine haftende Netzgrafik, mobil eine stabile lineare Übersetzung.
- Farbkorrektur: Die vier visuellen Stationen nutzen für Icon und Kurzlabel die
  kontraststärkere Web-Orange-Variante `#C14D2C` auf Weiß. Eine zu breit
  greifende SVG-Regel wurde auf die Orbitgrafik begrenzt, damit die
  Stationsicons ihre vorgesehenen Abmessungen behalten.
- Verdichtung: Sieben Anlasskarten, fünf Formatkarten und vier separate
  Prozesskarten wurden von der Startseite entfernt. Die Inhalte bleiben über
  Unternehmen, Leistungen, Coaches und Kontakt erreichbar.
- Zugänglichkeit: Native Links, sichtbare Fokuszustände, semantische
  Überschriften, vollständig sichtbarer Inhalt ohne JavaScript und
  `prefers-reduced-motion` bleiben erhalten.
- Verifikation: Astro prüft 25 Dateien ohne Fehler, Warnungen oder Hinweise und
  erzeugt 20 statische Seiten. Hub und Übergang wurden bei 1440, 1366 und
  500 Pixeln gerendert; ein Kontaktknoten-Überlauf in niedriger Laptopansicht
  wurde korrigiert.
- Veröffentlichung: Die Connected Story wurde mit Commit `fcc0129` nach
  `main` gepusht und durch den manuellen Pages-Workflow `30094540079`
  erfolgreich als öffentliche Prüffassung veröffentlicht. Der HTTP-Smoke-Test
  bestätigt Status 200, die neue Überschrift, die Scroll-Komponente und die
  korrigierte Web-Orange-Farbe im ausgelieferten CSS.

## 2026-07-23 | concept/implementation | Connected Core lokal umgesetzt

Das freigegebene Gesamtkonzept in `Quellen/Neues Konzept`, der heutige
Requirements-Engineering-Eintrag und die Unterlagen zu Wegner-Ney wurden
ausgewertet und in eine lokale Website-Version übertragen.

- Markenlogik: Die Startseite erklärt Competence Hub nun als sichtbaren Kern,
  der Unternehmensanliegen, ausgewählte Coaches, passende Formate und
  persönliche Begleitung verbindet.
- Gestaltung: Der Hub steht nun allein im Zentrum der ersten Ansicht.
  Kreisförmige Haupt- und Themenknoten bilden einen interaktiven
  Beziehungsgraphen; Hover, Fokus oder Aktivierung zeigen nur passende
  Verbindungen. Ein kleiner Orientierungspunkt läuft dann um den Kern.
  Mobile Geräte erhalten ein stabiles Kreisraster ohne unlesbare Linien.
- Angebot: Recruiting und Personalentwicklung sind lokal als ergänzendes
  Leistungsfeld sichtbar. Der öffentliche Leistungsumfang bleibt
  freigabepflichtig.
- Businesscoaching: Emotionale Ebene und Sachebene werden getrennt erklärt und
  als zusammengehörige Coachingperspektiven dargestellt.
- Personen: Wegner-Ney wurde mit freigegebenem Porträt und ausschließlich
  nicht-KI-bezogenen Themen als lokaler Profilentwurf ergänzt. Janay Rappelt
  wird ohne erfundenes Bild oder Profil als persönliche Ansprechpartnerin
  zwischen Unternehmen und Coaches gezeigt.
- Dokumentation: `docs/assets/designstyle.md` wurde um Connected Core ergänzt;
  die neuen Anforderungen stehen in
  `docs/requirements/requirements-engineering-update-2026-07-23.md`.
- Verifikation: Astro prüft 24 Dateien ohne Fehler, Warnungen oder Hinweise und
  erzeugt 20 statische Seiten. Die zentrale Hub-Ansicht wurde bei 1440 und
  500 Pixeln geprüft; Coach-Übersicht, Wegner-Ney, Kontakt und Businesscoaching
  zusätzlich im Desktop-Render. Gefundene Fehler bei Hero-Umbruch, mobilem
  Hub-Raster und Porträtformat wurden korrigiert.
- Veröffentlichung: Die Umsetzung wurde als Commit `693901b` nach `main`
  gepusht und mit dem manuellen Pages-Workflow `30016684516` erfolgreich als
  Prüffassung veröffentlicht. Die öffentliche Seite liefert den zentralen Hub,
  seine Interaktion und das Wegner-Ney-Profil aus.

## 2026-07-17 | design system / skill | Inspirationsserie in digitale Regeln übersetzt

Die sieben freigegebenen Bilder aus `Quellen/Inspiration` wurden vollständig visuell analysiert und mit dem Corporate Design Manual, dem Designerinnen-Feedback und der ergänzenden Datei `Rückmeldung KI.docx` abgeglichen.

- Designreferenz: `docs/assets/designstyle.md` dokumentiert Evidenzhierarchie, Markenwirkung, Farb- und Kontrastrollen, Typografie, Raster, Komponenten, Bildformate, Website-/App-Übertragung, Interaktion, Nicht-übernehmen-Regeln und Abnahmecheckliste.
- Kernergebnis: viel Weiß, Pantone als Orientierung und Rahmen, Kaminrot als sparsamer Akzent, dunkelgrauer Inhalt, weiße modulare Karten, reduzierte Outline-Icons und authentische Menschenbilder. Flyer-Dichte, QR-Logik und Mikroschrift werden nicht direkt digitalisiert.
- KI-Zweitmeinung: Bildformate, positives/negatives Markenprofil, App-Startscreen-Prioritäten und das Vermeiden generischer Handschlag-/KI-Roboter-Motive wurden übernommen. Größere Kartenradien und ein D+P-spezifischer Skillname wurden bewusst nicht als allgemeine Regel übernommen.
- Wiederverwendung: Der neue generische Skill `derive-design-system` und `references/design-analysis-framework.md` wurden in der kanonischen CodexSkills-Sammlung und der aktiven Runtime installiert; keine Projektbilder, Kontaktdaten oder markenspezifischen Inhalte wurden in den Skill kopiert.
- Website-Umsetzung: Die Startseite nutzt nun korallfarbene Primäraktionen mit dunkler Beschriftung, icongeführte Vertrauensmerkmale, stabile weiße Themenkarten, vollflächige korallfarbene Angebotsreiter, eine weiße Leitsatzfläche im Pantone-Rahmen, eine durchgehende responsive Prozesslinie und kontraststärkere Links sowie Fokuszustände.
- Bildentscheidung: Die vorhandenen generierten PNG-Motive wurden geprüft, aber wegen eingebetteter Texte, Flyer-Layout und teils austauschbarer Handschlagmotive nicht in die neue Startseite übernommen. Der vorhandene freigegebene Coach-Bildpfad bleibt bestehen; weitere Bildflächen warten auf Originalassets und Nutzungsfreigaben.
- Verifikation: Skill-Staging, kanonische und aktive Installation bestehen `quick_validate.py`. Die konkrete Designreferenz wurde gegen alle sieben Bilder geprüft. Die optimierte Startseite wurde bei 1440 und 500 Pixeln gerendert; eine entdeckte Timeline-Kaskade wurde korrigiert. Der finale Astro-Check meldet 0 Fehler, 0 Warnungen und 0 Hinweise, der Build erzeugt 19 Seiten.
- Status: Designsystem und Startseitenoptimierung sind lokal umgesetzt; kein Commit, kein Push und kein Deployment in diesem Arbeitsschritt.

## 2026-07-17 | stakeholder feedback | Designerinnen-Feedback umgesetzt

Die ausdrücklich freigegebene Word-Datei `Quellen/Feedback 17.07.2026.docx` mit sechs markierten Screenshots und anschließend das gezielt freigegebene `Quellen/Corporate Design Manual Stand 12.03.25.pdf` wurden ausgewertet. Weitere Quelldokumente wurden nicht gelesen.

- Farbwirkung: Primärbuttons und zentrale Markenflächen verwenden Pantone 320. Schwarze Rechteck- und Hintergrundflächen wurden entfernt. Nach der Designkorrektur sind die inneren Themen- und Leistungskarten weiß, Angebotsüberschriften verwenden Kaminrot und Inhaltstexte Dunkelgrau; Gelb wird nicht als Schrift auf Weiß eingesetzt.
- Layoutkorrektur: Kartenkanten verschmelzen nicht mehr Pantone-auf-Pantone, sondern verwenden auf der türkisen Rahmenfläche durchgehend sichtbares Kaminrot. Der Leistungsbereich übernimmt aus der gelieferten Inspiration einen weiß gerahmten Leitsatz neben dem 2×2-Kartenfeld. Abschnittslabels wie „Der Weg zum Coaching“ stehen nun oberhalb statt seitlich neben der jeweiligen Überschrift.
- Navigation: Das missverständliche separate Menü „Direkt zu“ wurde entfernt. „Leistungen“ enthält nun die Gesamtübersicht sowie Livecoaching, Businesscoaching, psychologische Beratung/Prävention und Gruppenformate.
- Sprache: „Was möchten Sie bewegen?“ wurde durch das klarere „Was interessiert Sie?“ ersetzt; weitere Hero- und Leistungstexte wurden gekürzt.
- Informationsdichte: Die Leistungsseite nutzt vier Icon-geführte Kurzangebote und eine einzige Bedarfsklärungs-CTA statt doppelter Vergleichstexte. Livecoaching, Businesscoaching und Unternehmensseite erhielten zusätzliche visuelle Themenanker.
- Prozessdarstellung: Die fünf Coaching-Schritte erscheinen als zusammenhängende Prozesslinie statt als vermeintlich klickbare FAQ-Karten.
- Kontakt: Ein ausfüllbares Anfrageformular bereitet lokal eine strukturierte E-Mail vor. Es speichert und versendet keine Formulardaten über die Website; eine echte serverseitige Übermittlung bleibt vom Hosting-/Backendentscheid abhängig.
- Offene Designabhängigkeit: Erklärbilder und weitere Bildflächen werden erst mit freigegebenen Originalassets und Nutzungsrechten aus dem Mediendesign ergänzt.
- Verifikation: regulärer und GitHub-Pages-Review-Build erfolgreich; 22 Astro-Dateien ohne Fehler, Warnungen oder Hinweise geprüft und 19 Seiten erzeugt. Start, Leistungen, Businesscoaching/Prozess und Kontakt wurden bei Desktopbreite geprüft; die Start- und Kontaktseite zusätzlich bei 500 Pixeln.
- Status: Änderungen sind lokal und noch nicht erneut auf die öffentliche GitHub-Pages-Review ausgerollt.

## 2026-07-17 | review deployment | GitHub-Pages-Review veröffentlicht

Für die Abstimmung mit Vertrieb und Mediendesign wurde das bestehende private Repository `DP-Manuel/CompetenceHub` als sinnvoller Review-Kanal bestätigt; das alte Firmenschulung-Repository wird nicht reaktiviert.

- Workflow: `.github/workflows/pages-review.yml` nutzt die offiziellen Astro-/GitHub-Pages-Actions und kann ausschließlich manuell über `workflow_dispatch` gestartet werden; Pushes veröffentlichen nichts automatisch.
- Review-Schutz: Der Pages-Build verwendet `/CompetenceHub`, zeigt einen sichtbaren Entwurfsstatus und setzt `noindex, nofollow, noarchive`. Dies ist keine Zugriffskontrolle; die veröffentlichte URL wäre weiterhin erreichbar.
- Freigabeblocker: Die Entwürfe für Elisabeth Schwabauer und Carolin Hupp dürfen erst nach Publikationsfreigabe öffentlich bereitgestellt werden.
- Verifikation: Review-Build mit GitHub-Pages-Basis erfolgreich; 22 Astro-Dateien ohne Fehler, Warnungen oder Hinweise geprüft und 19 statische Seiten erzeugt. Basis-Links, Review-Banner und Robots-Meta wurden im Build kontrolliert.
- Veröffentlichung: Nach ausdrücklicher Freigabe wurde das inzwischen öffentliche Repository mit Commit `f8104b9` aktualisiert, GitHub Pages im Workflow-Modus aktiviert und der manuelle Lauf `29576161306` erfolgreich abgeschlossen.
- Smoke-Test: `https://dp-manuel.github.io/CompetenceHub/` sowie `/coaches/`, `/kontakt/` und `/login/` antworten mit HTTP 200; Review-Banner, `noindex` und die `/CompetenceHub`-Basislinks sind vorhanden.
- Sicherheit: `.tmp/`, die echte `.env`, private Schlüssel und Passwörter wurden nicht committed. Der Workflow bleibt manuell und reagiert nicht automatisch auf Pushes.
- Infrastruktur: Die technischen Rückfragen zu SFTP, Hosting-Runtime, MySQL-Zugriff, TLS, Staging, Backups und Domain wurden an Herrn Roß gesendet; Antwort steht aus.

## 2026-07-16 | design/implementation | Textverdichtung, Direkteinstieg und Login-Rollenwege

Die B2B-Website wurde anhand aktueller Business-Website-Muster und der Navigationslogik der Haufe Akademie sichtbarer, kompakter und interaktiver gestaltet.

- Inspiration: Notarize, Traackr, Nespresso, Byredo, Skullcandy und Haufe Akademie wurden auf Einstiegslogik, Menüs, Themenfinder, Rollenwege und Textdichte geprüft; übernommen wurden nur robuste Muster, keine fremden Designs.
- Navigation: Der Desktop-Header bietet nun einen aufklappbaren Direkteinstieg nach Führung, Teams, Gesundheit und Coach-Suche sowie einen sichtbaren Login-Weg; mobil bleiben Kontakt und Login im nativen Menü erreichbar.
- Startseite: Der Hero wurde verdichtet, ein symbolgestützter Themenfinder ergänzt und die sechs Anlässe als zugängliche Aufklapper umgesetzt. Leistungsdetails und FAQs sind progressiv aufklappbar, damit Fachinhalte und SEO-Struktur erhalten bleiben, ohne die Seite visuell zu überladen.
- Login: `/login` zeigt die geplanten Rollenwege für internes Team, Coaches und Unternehmen. Die statischen Unterseiten `/login/intern`, `/login/coaches` und `/login/unternehmen` beschreiben nur den späteren Funktionsrahmen; es gibt keine Eingabemaske, Accounts, Sessions oder Datenbankzugriffe.
- Technik: lokale Icon-Komponente ohne neue Abhängigkeit; native `details`/`summary`-Interaktionen, sichtbare Fokusführung und reduzierte Bewegung bleiben berücksichtigt.
- Verifikation: finaler `npm run build` erfolgreich; Astro prüfte 22 Dateien mit 0 Fehlern, 0 Warnungen und 0 Hinweisen und erzeugte 19 statische Seiten. Start- und Loginseite wurden bei 1440 und 500 Pixeln ohne Überlappungen oder abgeschnittene Inhalte geprüft.
- Sicherheit: kein Backend, keine Secrets, keine echte Authentifizierung, kein Deployment, kein Commit und kein Push.

## 2026-07-16 | requirements/implementation/architecture | Vermittlungsprofil, Coaches und Datenbankvorbereitung

Die neue Requirements-Engineering-Quelle und die gezielt freigegebenen Coach-Unterlagen wurden ausgewertet und in sichtbare Website- sowie technische Vorbereitung überführt.

- Positionierung: Competence Hub wird nun korrekt als kuratierende Vermittlung zwischen Unternehmen und ausgewählten Coaches beschrieben; Qualität und Passung stehen vor Kataloggröße.
- Angebot: psychologische Beratung im beruflichen Kontext, Supervision, Workshops, Vorträge, Gesundheitsförderung und Prävention wurden vorsichtig in die Leistungslogik aufgenommen; Therapie- und Medizingrenzen bleiben sichtbar.
- Coach-Netzwerk: Elisabeth Schwabauer und Carolin Hupp wurden neben Christian Galvano als lokale Profilentwürfe ergänzt. Private Kontaktdaten wurden nicht übernommen; für beide neuen Profile fehlen noch Portrait und finale Publikationsfreigabe.
- Preisangaben: 850/680 EUR für Workshops und 200 EUR für Vorträge wurden nur als offene Anforderung dokumentiert, weil Preisbasis, Inklusivleistungen, Umsatzsteuer und Rabattlogik noch widersprüchlich beziehungsweise unbestätigt sind.
- Interaktive Inhalte: Leadership-, Stress- und KI-Selbstchecks sind als spätere Kandidaten dokumentiert, aber wegen Inhalts-, Datenschutz-, Ergebnis- und Accessibility-Fragen nicht in den Deadline-MVP gezogen.
- Datenbank: `apps/webapp/.env.example` als commit-fähige Vorlage und eine leere, Git-ignorierte `apps/webapp/.env` für Manuel erstellt; keine Secrets eingetragen. SSH-Passwörter sind ausdrücklich ausgeschlossen.
- Architektur: Server-Inventur, Datenbank-Bootstrap und ein initiales Modell für User, Firmen, Kontakte, Coaches, Leistungen, Anfragen, Einsätze, Feedback und Audit-Events dokumentiert.
- Verifikation: finaler `npm run build` erfolgreich; Astro prüfte 20 Dateien mit 0 Fehlern, 0 Warnungen und 0 Hinweisen und erzeugte 16 statische Seiten. Startseite, Coach-Übersicht sowie beide neuen Profile wurden in Desktop- und Mobilbreite gerendert; ein dabei entdeckter Startseiten-CTA-Kontrastfehler wurde behoben.
- Sicherheit: Das Zugangsdaten-Dokument wurde nicht geöffnet. Kein Serverzugriff, keine Installation, keine Migration, kein Deployment, kein Commit und kein Push.
- Nächster Schritt: Manuel-Freigabe für Profile/Positionierung und Bestätigung, ob der neue Server Staging oder Produktion ist.

## 2026-07-13 | implementation/verification | B2B conversion refresh and direct E-Mail contact

Implemented the first B2B-focused visual and content refresh after the website review.

- Homepage: replaced public MVP, roadmap, booking, login, database, and app language with the positioning "Coaching dort, wo Arbeit passiert", business use cases, format guidance, a three-step inquiry path, Donner + Partner trust signals, and the first real coach spotlight.
- Navigation: reduced the main navigation to Start, Leistungen, Für Unternehmen, Coaches, and Kontakt; added active-page states and a native keyboard-accessible mobile details menu.
- Contact: removed the non-functional demo form and added a usable `mailto:` inquiry path to `competencehub@donner-partner.de` with a prepared message structure.
- Test contact: `roedel.kg@donner-partner.eu` is visible only under the Astro development server through `import.meta.env.DEV`; verification confirmed that it is absent from the production build.
- Coach network: retained Christian Galvano as the only published real profile and added transparent network-growth wording. Manuel expects data for approximately five initial coaches during the week; no placeholder identities or unapproved details were invented.
- Visual/accessibility: strengthened the editorial hero, reduced repeated card treatment, added responsive content bands, improved mobile header density, preserved visible focus, used native controls, and added reduced-motion handling.
- SEO/content: added Open Graph title/description metadata and replaced ASCII `fuer/Fuehrungskraefte` wording in the main page descriptions with correct German text.
- Verification: final `npm run build` passed outside the sandbox with 0 Astro errors, 0 warnings, and 0 hints; all 14 static pages built. Desktop and 500 px homepage/contact renders were inspected without clipping or overlap.
- Local review: Astro development preview is available at `http://127.0.0.1:4321/` for Manuel's review.
- Safety: no backend, deployment, provider, secret, restricted-source access, commit, or push. `.tmp/` remains untouched and untracked.
- Next recommended task: review the local direction, then integrate approved coach data and complete legal/contact/SEO launch QA before 2026-07-23.

## 2026-07-13 | review/implementation | B2B website review and central legal links

Reviewed the rendered Competence Hub website at desktop and narrow viewports for visual distinctiveness, B2B trust, conversion, responsive behavior, and accessibility.

- Legal navigation: linked footer entries for Impressum, Datenschutz, and AGB directly to the public Donner + Partner parent-site pages supplied by Manuel.
- Legal placeholders: updated the local `/impressum` and `/datenschutz` pages with clear links to the central texts and retained the project-specific pre-live checks for the responsible group company, hosting, logs, contact processing, cookies, tracking, and external services.
- Review finding: the current visual system is technically clean and recognizable, but the homepage still exposes internal MVP/roadmap language and lacks strong business proof, real people, concrete use cases, and a working inquiry route.
- Verification: `npm run build` passed outside the sandbox with 0 Astro errors, 0 warnings, and 0 hints; all 14 static pages built successfully.
- Residual legal risk: the parent privacy page describes services such as analytics, consent management, external fonts, maps, and an active contact form that are not automatically identical to the Competence Hub implementation. Applicability of Datenschutz and AGB must be confirmed before launch; this is not legal advice.
- Next recommended task: refocus the homepage on business outcomes and trust, remove public MVP/system roadmap language, and provide a real approved contact path.

## 2026-07-09 | deployment cleanup | Disable GitHub Pages autodeploy

Checked and disabled the old GitHub Pages deployment path for the current Competence Hub MVP.

- Deployment cleanup: removed `.github/workflows/deploy.yml`, which previously deployed to GitHub Pages automatically on pushes to `main`.
- Config cleanup: removed the hard GitHub Pages `site` and `base` values from `apps/website/astro.config.mjs`; local/static builds now use Astro defaults until a later deployment decision is approved.
- Documentation/tooling cleanup: updated `apps/website/README.md` to describe the current MVP routes, local preview URL, static contact form, and the fact that deployment is manual/freigabepflichtig; made `apps/website/scripts/serve-dist.mjs` default to root preview with optional `BASE_PATH`.
- SEO/deployment note: removed the GitHub-Pages-specific static `robots.txt` and `sitemap.xml` for now, because no public GitHub Pages publication is planned yet.
- Safety: no GitHub Actions secrets were read, no deployment command was run, no push was performed, and `.tmp/` was not opened.

## 2026-07-09 | quality | Competence Hub MVP block 3

Completed the third Competence Hub deadline-sprint block: quality pass, SEO/legal placeholders, and build verification.

- User-facing change: added `/impressum` and `/datenschutz` as clearly marked legal placeholder pages with explicit pre-live legal/factual review notes and no invented company data.
- Navigation/SEO: replaced footer placeholder links with real routes, aligned package naming, and checked the deployment-facing SEO files before deferring public robots/sitemap output to a later approved deployment decision.
- Quality pass: checked MVP routes for H1/meta structure, internal links, CTA consistency, old prototype terms, demo credentials, legal placeholder clarity, and mobile-oriented CSS constraints; no new backend, provider, tracking, or form handling was added.
- Verification: sandbox build again hit the known `spawn EPERM` after `astro check` passed with 0 errors, 0 warnings, and 0 hints; rerunning the same build outside the sandbox succeeded and generated 14 static pages.
- Safety: did not open `Quellen/`, `.env*`, server/database access documents, `.tmp/`, or secrets; no deployment and no commit.

## 2026-07-09 | visual QA | Fix contact page contrast and heading wrap

Fixed the visible `/kontakt` contrast issue before commit/push.

- User-facing change: shortened the contact H1, disabled awkward hyphenation for that heading, set dark text on the light process cards, improved the static-form note contrast, and made contact form labels/placeholders easier to read.
- Verification: sandbox build again hit the known `spawn EPERM` after `astro check` passed with 0 errors, 0 warnings, and 0 hints; rerunning the same build outside the sandbox succeeded and generated 12 static pages.
- Safety: no backend, real form handling, deployment, provider integration, secrets, or restricted source access.

## 2026-07-09 | implementation | Competence Hub MVP block 2

Expanded the Competence Hub website subpages for the deadline MVP.

- User-facing change: rewrote `/unternehmen`, `/coaches`, `/leistungen`, `/livecoaching`, `/businesscoaching`, and `/kontakt` for Livecoaching, Businesscoaching, Firmenkunden, Coach-Netzwerk, and Anfrage flow.
- SEO/content structure: added clearer page titles, meta descriptions, H1/H2 structure, FAQ sections, internal links, target-group sections, benefit sections, process steps, and explicit boundaries for coaching versus therapy/medical advice where relevant.
- Prototype cleanup: kept `/seminare`, `/qualifizierung`, `/system`, and `/login` build-safe but reframed them as archived or later-stage pages; removed demo login credentials and avoided unfinished app promises.
- Styling: added shared FAQ, CTA, notice, and form-note styles using the existing visual system; no new dependencies or assets.
- Verification: sandbox build again hit the known `spawn EPERM` after `astro check` passed with 0 errors, 0 warnings, and 0 hints; rerunning the same build outside the sandbox succeeded and generated 12 static pages.
- Safety: did not open `Quellen/`, `.env*`, server/database access documents, or secrets; no deployment, provider integration, backend, real login, or booking functionality was added.

## 2026-07-09 | implementation | Competence Hub MVP block 1

Implemented the first visible Competence Hub deadline-sprint slice for the Astro website.

- User-facing change: replaced the old sub-brand/navigation framing with `Competence Hub`, focused the homepage on Livecoaching and Businesscoaching, added clear CTAs, offer cards, target-group copy, and a transparent note that booking, coach calendar, database, login, contracts, and app functionality are later stages.
- Routes added: `/leistungen`, `/livecoaching`, and `/businesscoaching` so the new MVP navigation has real static destinations.
- Existing pages: removed `[Submarke]` from page titles and lightly aligned the contact page wording and select options with the new offer language; login/system pages remain available but are no longer part of the main navigation.
- Verification: `npm run build` first hit the known Windows/Sandbox `spawn EPERM` after `astro check` passed with 0 errors, 0 warnings, and 0 hints; rerunning the same build outside the sandbox succeeded and generated 12 static pages.
- Safety: did not open `Quellen/`, `.env*`, server/database access documents, or secrets; no deployment, provider integration, backend, real login, or booking functionality was added.

## 2026-07-09 | documentation | Create external AI project brief

Created `CHATGPT_PROJECT_BRIEF.md` as a compact, copyable handoff for a second AI that will help write prompts and understand the Competence Hub website sprint.

- Captured: current Astro website structure, safe local development commands, existing pages/resources, project memory files, security boundaries, new target repo `DP-Manuel/CompetenceHub`, current remote mismatch with `DP-Manuel/Firmenschulung`, blank-server handling, MVP target for 2026-07-23, and recommended next implementation steps.
- Safety: did not open `Quellen/`, `.env*`, the server/database access document, or any secrets.
- Delivery note: no code implementation, Git remote change, commit, push, or deployment was performed.
- Next recommended task: update the website itself for the visible Competence Hub MVP: brand, navigation, homepage, Livecoaching, Businesscoaching, and contact/request flow.

## 2026-06-30 | handoff | Close day with kickoff-ready prototype

Closed the workday with the coach experience polished, deployed, and ready for the 2026-07-01 kickoff review.

- Delivered today: first real coach profile, supplied portrait, responsive visual polish, balanced content boxes, customer-facing coach CTA, and removal of internal editorial copy from the public coach page.
- Release evidence: commits `ebaf9ac` and `8f860f7`; latest GitHub Actions run `28425939779` passed; coach listing, detail page, and portrait asset returned HTTP 200.
- Visual evidence: desktop and narrow local browser renders were inspected; the reported squeezed-title and empty-column issue is resolved.
- Skill feedback: added `visual-ui-handoff` to `SKILL_FEEDBACK_LOG.md`, proposing that meaningful UI work always ends with a rendered, viewable local or deployed result plus representative viewport checks.
- Current state: green and ready for stakeholder review; no technical blocker.
- Next recommended task: run the kickoff demo, capture stakeholder feedback and decisions, then reconcile requirements, priorities, and the next website/app increment.

## 2026-06-30 | deployment | Publish kickoff polish and coach portrait

Published the visually refined coach experience for the 2026-07-01 kickoff meeting.

- User-facing change: added Christian Galvano's supplied portrait to the coach listing and detail page; rebalanced the profile hero, topic heading, seminar cards, qualifications, and calls to action; removed the oversized generic recruiting-image box and replaced the internal editorial note with a customer-facing coach inquiry.
- Accessibility/responsiveness: informative portrait alt text and intrinsic dimensions were added; headings and content boxes now use stable responsive columns and stack cleanly at narrow widths; native links/buttons and existing visible focus styles were preserved.
- Visual verification: rendered and inspected the detail page at 1440 px and 500 px widths plus the coach listing at 1440 px; the reported squeezed heading/empty-column issue is resolved.
- Build verification: `npm run build` passed with 0 Astro errors, 0 warnings, and 0 hints; all 9 static pages built.
- Release scope: only the portrait and three coach-related frontend files; source materials, screenshots, temporary files, and internal project memory were excluded.
- Commit: `8f860f7 Polish coach pages for kickoff` pushed to `origin/main`.
- CI/CD: GitHub Actions run `28425939779` completed successfully.
- Smoke test: public coach listing, Christian Galvano detail page, and portrait asset all returned HTTP 200; both pages contained the expected new content.
- Rollback: revert commit `8f860f7` and redeploy commit `ebaf9ac`.
- Residual check: Manuel should perform a final real-browser review at the meeting display size; exact profile wording can still be adjusted after stakeholder feedback.

## 2026-06-30 | deployment | Publish Christian Galvano coach profile

Published the first real coach profile to GitHub Pages.

- Release scope: only `apps/website/src/pages/coaches.astro`, `apps/website/src/pages/coaches/christian-galvano.astro`, and `apps/website/src/styles/global.css`; internal project memory, source flyers, and temporary review files were excluded.
- Commit: `ebaf9ac Add Christian Galvano coach profile` pushed to `origin/main`.
- CI/CD: GitHub Actions run `28424472761` completed successfully; both build and GitHub Pages deploy jobs passed.
- Smoke test: `/Firmenschulung/coaches/` and `/Firmenschulung/coaches/christian-galvano/` both returned HTTP 200 and contained Christian Galvano's name.
- Rollback: revert commit `ebaf9ac` and redeploy the previous commit `ab055e3`.
- Residual check: Manuel should review the live desktop/mobile presentation and confirm profile wording; an approved standalone portrait is still needed before replacing the monogram.

## 2026-06-30 | implementation | Add first real coach profile

Added Christian Galvano as the first real coach and dozent in the website prototype.

- User-facing change: replaced the three anonymous demo cards on `/coaches/` with a focused profile card and added the detail route `/coaches/christian-galvano/`.
- Profile scope: Neuroleadership, conflict management, stress and burnout prevention, professional qualifications, internal seminar inquiry CTAs, and a link to `https://changes-galvano.de/`.
- Sources: three supplied seminar flyers under `Quellen/Coach` and Christian Galvano's public CHANGES Galvano website and qualification page.
- Privacy/asset decision: did not publish contact details or extract a portrait from the composed flyer layouts; the profile uses a responsive monogram until an approved standalone image is available.
- Accessibility/responsiveness: semantic headings and lists, descriptive external link behavior, visible focus styles, and one/two-column responsive layouts reuse the existing design system.
- Verification: sandbox run completed Astro check with 0 errors, 0 warnings, and 0 hints, then hit the documented Vite `spawn EPERM`; the approved rerun passed and built all 9 static pages including the new coach route.
- Deployment: completed in commit `ebaf9ac`; GitHub Actions run `28424472761` passed and both public coach routes returned HTTP 200.
- Next recommended task: visually review the live coach listing and detail page, then confirm wording and portrait approval.

## 2026-06-22 | handoff | End-of-day restart preparation

Closed the workday with the prototype deployed and project memory current.

- Delivered today: updated CodexSkills project harness; analyzed the media designer onepager; refined and deployed the seminar page.
- Live evidence: commit `ab055e3`, GitHub Actions run `27970977233`, and HTTP 200 smoke test at `https://dp-manuel.github.io/Firmenschulung/seminare/`.
- Current state: no technical blocker; public website code is pushed, while internal project memory, sources, and feedback remain local/untracked by design.
- Restart point: review `/seminare/` and `/coaches/` with Manuel's colleague, collect visual/content feedback, then prepare the 2026-07-01 stakeholder reveal path.
- Reminder: request original approved seminar illustrations and logo exports from the media designer when prototype work moves to the real website.

## 2026-06-22 | deployment | Publish onepager-inspired seminar page

Published the refined seminar prototype so Manuel and his colleague can review it together.

- Release scope: only `apps/website/src/pages/seminare.astro` and `apps/website/src/styles/global.css`; internal project memory, sources, PDF, and starter files were excluded.
- Commit: `ab055e3 Refine seminar prototype` pushed to `origin/main`.
- CI/CD: GitHub Actions run `27970977233` completed successfully; both build and GitHub Pages deploy jobs passed.
- Smoke test: `https://dp-manuel.github.io/Firmenschulung/seminare/` returned HTTP 200 and contained the new seminar catalog and consultation CTA.
- Rollback: revert commit `ab055e3` or redeploy previous commit `23e817d` if a visual regression is found.
- Residual check: Manuel and colleague should review desktop/mobile appearance and wording in a real browser.

## 2026-06-22 | implementation | Refine seminar prototype from media designer onepager

Reworked the prototype seminar page using the approved onepager as the visual and content reference while keeping production illustration assets out of scope.

- User-facing change: replaced four abstract summaries with four detailed seminar cards covering 24 concrete topics; added stronger local positioning and a framed consultation CTA.
- Design alignment: reused the existing CI tokens with the onepager's pale background, coral card headers, teal dividers, yellow accents, rounded rectangles, and clear content hierarchy.
- Accessibility/responsiveness: retained semantic headings and lists, used dark text on coral for stronger contrast, preserved visible focus behavior, and added four/two/one-column layouts for desktop/tablet/mobile.
- Asset decision: no illustrations were extracted from the PDF. `PROJECT_PLAN.md` and `PROJECT_STATUS.md` now remind Manuel to request original approved illustration and logo exports when work moves to the real website.
- Verification: initial sandbox build hung without output; the unchanged approved rerun passed with Astro check reporting 0 errors, 0 warnings, 0 hints and built all 8 static pages.
- Next recommended task: visually review `/seminare/` at desktop and mobile widths, then incorporate the original illustrations once real-site production begins and usage approval is confirmed.

## 2026-06-22 | design | Analyze media designer seminar onepager

Reviewed the new `Quellen/Firmendingsbums Onepager.pdf` as a professional visual and content reference for website optimization.

- Evidence: rendered and visually inspected the one-page A4 Canva design; extracted its seminar structure and compared it with the homepage, seminar page, CSS tokens, existing seminar image, and corporate-design notes.
- Findings: the website already uses the correct CI palette and the same four seminar categories; the onepager adds a stronger card hierarchy, concrete topic bullets, inclusive illustrations, local Würzburg positioning, and a clearer consultation CTA.
- Documentation: updated `docs/assets/brand-design-notes.md` with reusable design evidence, recommended website application, and a publication/privacy guard for personal contact details.
- Scope: no website code changed during this analysis pass.
- Next recommended task: refine the seminar page around the onepager's four detailed topic cards and CTA after confirming whether original illustration/logo assets may be reused.

## 2026-06-22 | workflow | Integrate updated CodexSkills project harness

Integrated the current CodexSkills update and verified that this project can use it safely.

- Canonical source: commit `6acdc18` (`Improve skill harness and safe sync`).
- Runtime result: all 29 canonical skills validated and matched `%USERPROFILE%\.codex\skills`; the dry-run reported no additions or updates, so no real sync was needed.
- Project integration: updated root and starter `AGENTS.md`, starter `README.md`, starter status fields, root `PROJECT_STATUS.md`, and both project-local update helpers.
- Safety improvements: added `-PlanSync`, `-SyncSkill`, `-BackupActive`, explicit `--skills-root` handling, and non-destructive file-level planning.
- Feedback follow-through: marked `safe-skill-sync` implemented and retained the canonical working-directory/version-awareness gap as partially mitigated local feedback.
- Verification: `.\scripts\codexskills-update-check.ps1 -Validate -PlanSync` completed successfully from the website project directory.

## 2026-06-22 | feedback | Capture downstream starter drift and validator path bug

Recorded a reproducible CodexSkills improvement discovered while checking the updated starter guidance.

- Evidence: added `downstream-starter-drift` to `SKILL_FEEDBACK_LOG.md`; the project-local README and update helper are older than canonical commit `6acdc18`.
- Reproduction: project-local `codexskills-update-check.ps1 -Validate` reported `No skill folders found under skills` because repository scripts resolved `skills` against the downstream project's working directory.
- Control check: direct canonical validation passed all 29 skills, and the active runtime drift check passed when run from the canonical repository directory.
- Proposed improvement: make update scripts working-directory independent and add a version-aware, non-destructive plan for refreshing copied starter files.
- Verification: documentation-only change; no website build required.

## 2026-06-17 | implementation | Fix image cropping and card contrast feedback

Applied Manuel's visual feedback after reviewing the live prototype.

- Evidence: updated `apps/website/src/styles/global.css` to show images with `object-fit: contain`, reduce displayed image size, align floating cards with the image edge, make the dark-section login demo button visible, and replace the seminar topic rail flex row with a more stable grid.
- Verification: `npm run build` passed after approved rerun; Astro check reported 0 errors, 0 warnings, 0 hints; 8 static pages built.
- Deployment: committed and pushed public website files in `23e817d Fix prototype image and card layout`; GitHub Actions run `27707186900` completed successfully; live start page returned HTTP 200.
- Next recommended task: manual browser review of image proportions and topic-card alignment on desktop/mobile.

## 2026-06-17 | implementation | Improve visual fit and add source images

Reduced text overflow risk across the prototype and integrated selected local images.

- Evidence: copied selected files from `Quellen/Bilder` into `apps/website/public/images`; updated homepage hero image and added page images for seminars, companies, qualification, coaches, system, and contact; tightened typography, line-height, card heading sizes, responsive grids, and text wrapping in `apps/website/src/styles/global.css`.
- Context update: Manuel learned that leadership does not yet know the website is being built; 2026-07-01 is the actual project start, so visible copy was adjusted away from internal "presentation/prototype" wording toward neutral preview/system wording.
- Verification: `npm run build` passed after approved rerun; Astro check reported 0 errors, 0 warnings, 0 hints; 8 static pages built.
- Deployment: committed and pushed public website files in `a11f6d3 Improve prototype visuals`; GitHub Actions run `27706695479` completed successfully; live start page, `/coaches/`, and `/images/start.png` returned HTTP 200.
- Next recommended task: visual review on desktop/mobile, especially text fit in cards, image crops, and the surprise/reveal narrative.

## 2026-06-17 | feedback | Propose safe active skill sync mode

Captured a CodexSkills improvement idea for safer active runtime skill updates.

- Evidence: added `safe-skill-sync` entry to `SKILL_FEEDBACK_LOG.md`.
- Rationale: `-Validate` is safe but does not update active skills; `-SyncActive` may overwrite active runtime skills. A middle path should preview diffs, back up active skills, and allow selective or no-overwrite updates.
- Next recommended task: review this feedback in the canonical CodexSkills repository and decide whether to extend `codexskills-update-check.ps1` or the underlying sync script.

## 2026-06-17 | implementation | Add coach page and update system outlook

Added the missing visible prototype slice for coaches and updated the future-system wording to include companies, coaches, and job postings.

- Evidence: added `apps/website/src/pages/coaches.astro`; updated navigation/footer in `BaseLayout.astro`; updated homepage app-preview, system modules, login demo, and coach-card styles.
- Scope guard: coach profiles are anonymized demo profiles; real names, photos, roles, qualifications, and texts still require approval before publication.
- Verification: first sandbox build passed `astro check` with 0 errors, 0 warnings, 0 hints, then failed during static build with `spawn EPERM`; approved rerun passed and built 8 static pages including `/coaches/`.
- Deployment: committed and pushed public website files in `7982149 Add coach prototype page`; GitHub Actions run `27704830936` completed successfully; live `https://dp-manuel.github.io/Firmenschulung/coaches/` returned HTTP 200.
- Next recommended task: visually review the live/prototype route `/coaches/` on desktop and mobile.

## 2026-06-17 | workflow | Check CodexSkills update state

Checked whether CodexSkills updates are available before continuing website work.

- Evidence: ran `powershell -ExecutionPolicy Bypass -File .\scripts\codexskills-update-check.ps1 -Validate`.
- Result: local canonical CodexSkills source is at `63d8f11` with local modifications across project memory, starter files, references, and several skill files; no `-SyncActive` was run.
- Output note: validation reported `No repository skill folders found under skills`; active runtime drift check completed without a sync step.
- Next recommended task: review canonical CodexSkills changes intentionally before running `-SyncActive`.

## 2026-06-17 | workflow | Copy starter scripts snapshot

Copied the new scripts folder from the canonical CodexSkills new-project starter into this project's local starter snapshot.

- Evidence: copied `C:\Users\RödelManuel\Documents\IT\CodexSkills\deploy\new-project-starter\scripts\codexskills-update-check.ps1` to `new-project-starter\scripts\codexskills-update-check.ps1`.
- README note: canonical `deploy/new-project-starter\README.md` now documents the Skill Update Check section and lists `scripts/codexskills-update-check.ps1` as a starter file to copy.
- Verification: SHA-256 hash matched between canonical source and local starter copy: `EE1EB39D849F0A61ED3A78E10B2B05947FB5575D972A603EB28D8F9B8BD20579`.
- Scope note: did not overwrite local starter README/AGENTS snapshots; only copied the requested scripts folder.

## 2026-06-17 | planning | Record future redaction model decision and starter README drift

Made the future content-maintenance decision explicit and captured that the project-local starter README is behind the canonical CodexSkills starter.

- Decision to make later: before live operation, choose and document whether website content is maintained through Astro by a technical owner, Astro plus CMS/API, WordPress/other CMS, or the later webapp as content source.
- Evidence: canonical `C:\Users\RödelManuel\Documents\IT\CodexSkills\deploy\new-project-starter\README.md` now includes the Skill Update Check section, `scripts/codexskills-update-check.ps1`, and the optional multi-artifact web scaffold; project-local `new-project-starter\README.md` is an older snapshot.
- Project impact: root `AGENTS.md` and project memory remain authoritative; do not blindly overwrite the local starter snapshot, but consider refreshing/merging it after the canonical CodexSkills changes are reviewed.
- Verification: documentation-only update; no build needed.

## 2026-06-17 | workflow | Check CodexSkills starter drift

Ran the CodexSkills update check after Manuel noticed that `new-project-starter/AGENTS.md` may indicate updated skills or starter files.

- Evidence: `powershell -ExecutionPolicy Bypass -File .\scripts\codexskills-update-check.ps1 -Validate` succeeded.
- Result: canonical CodexSkills source at `C:\Users\RödelManuel\Documents\IT\CodexSkills` has local modifications, including `deploy/new-project-starter/AGENTS.md`, `PROJECT_STATUS.md`, `README.md`, and several skill/reference files.
- Project impact: root `AGENTS.md` remains the authoritative project instruction file and already includes the newer CodexSkills local-path and update-check guidance; the project-local `new-project-starter/AGENTS.md` is only an older starter snapshot.
- Next recommended task: do not sync active skills automatically until the canonical CodexSkills changes are intentionally reviewed; keep using project root `AGENTS.md` for this website.

## 2026-06-17 | requirements | Capture handover, editor workflow, and coach page requirements

Captured new operational requirements for the website beyond the immediate prototype copy.

- Evidence: added `docs/requirements/website-maintenance-handover-and-editor-workflows.md`; updated `PROJECT_PLAN.md` and `PROJECT_STATUS.md`.
- New requirements: website must be maintainable by another Informatiker if Manuel is not the technical owner; documentation must cover local setup, build, deployment, hosting, subdomain, access handover, dependency updates, and rollback; non-technical colleague should not need GitHub or development tooling to maintain companies, coaches, and job postings.
- New content scope: plan a small coach profile subpage where coaches can introduce themselves after profile, photo, role, and privacy approval.
- Open decisions: whether the coach subpage is visible by 2026-07-01; whether long-term editing is Astro-only, Astro plus CMS/API, WordPress, or fed by the later webapp; who owns technical operations long term.
- Verification: documentation-only requirements update; no build needed.

## 2026-06-17 | workflow | Record Astro build sandbox note and technology-selection feedback

Captured a project-specific build environment lesson and a broader technology-selection improvement.

- Evidence: updated `AGENTS.md` and `PROJECT_STATUS.md` with the Astro telemetry `AppData\Roaming\astro\Config` sandbox failure signature and recovery path.
- Skill feedback: added entries for Astro telemetry sandbox handling and for making handover, documentation burden, and technology aging explicit in stack decisions.
- Verification: documentation-only update; no build needed.

## 2026-06-17 | content | Incorporate colleague briefing into prototype copy

Processed the saved colleague answers into a clean content evaluation and updated the static website prototype copy.

- Evidence: rewrote `docs/requirements/content-briefing-colleague-prototype.md` as a structured evaluation with requirements, acceptance criteria, copy guidance, and open decisions; updated homepage, seminar, company, qualification, system, contact, and login demo copy under `apps/website/src`.
- Content direction: shifted copy toward regional KMU in Tauberfranken/Würzburg, praxisnahe Firmenschulungen, gezielte Personalqualifizierung, passgenaue Vermittlung, and the CTA "Kostenfreies Erstgespräch zur Bedarfsanalyse".
- Scope guard: kept login/system wording explicitly non-productive and avoided promoting "KI-gestütztes Matching" or a "komplexe digitale Plattform" for the 2026-07-01 prototype.
- Verification: `npm run build` passed with Astro check reporting 0 errors, 0 warnings, 0 hints; 7 static pages built.
- Next recommended task: visually review the updated prototype on desktop/mobile and decide whether the "Für Unternehmen" page should remain separate.

## 2026-06-16 | workflow | Add CodexSkills update check

Added the downstream CodexSkills update helper so the project can detect stale skill usage without vendoring skill folders.

- Evidence: copied `scripts/codexskills-update-check.ps1`, updated `AGENTS.md` with the local CodexSkills path and repo fallback, and added update-check fields to `PROJECT_STATUS.md`.
- Source: local canonical folder `C:\Users\RödelManuel\Documents\IT\CodexSkills`; repo fallback `https://github.com/DP-Manuel/CodexSkills.git`.
- Verification: `powershell -ExecutionPolicy Bypass -File .\scripts\codexskills-update-check.ps1` succeeded and reported the current CodexSkills working-tree state.
- Next recommended task: run `.\scripts\codexskills-update-check.ps1 -Validate` when this project may rely on stale skills; use `-SyncActive` only after CodexSkills is intentionally updated.
## 2026-06-16 | handoff | End-of-day restart preparation

Prepared the project for a clean restart tomorrow.

- Evidence: updated `PROJECT_PLAN.md` and `PROJECT_STATUS.md` with next actions, repo state, restart files, and current prototype scope.
- Repo note: public website implementation is already pushed in commits `0a4ffe3` and `c5b51ed`; internal planning and requirements files remain local/untracked and should not be pushed to the public repo without an explicit decision.
- Skills note: `SKILL_FEEDBACK_LOG.md` contains open improvements for proactive requirements intake and German stakeholder-language handling.
- Tomorrow's recommended start: read the German colleague briefing, convert colleague answers into prototype copy, then polish the GitHub Pages demo flow for the 2026-07-01 stakeholder presentation.
- Verification: documentation-only handoff update; no build needed.

## 2026-06-16 | documentation | German colleague briefing and skill feedback

Prepared the colleague-facing content package in German.

- Evidence: rewrote `docs/requirements/content-briefing-colleague-prototype.md` with German prototype questions, answer template, reusable wording, and an email draft covering the database decision direction.
- Database wording: clarified that the 2026-07-01 prototype stays database-free, while the later independent system should use its own database behind a backend/API; PostgreSQL is the preferred long-term direction, with MariaDB/MySQL as a possible EDV-friendly alternative.
- Skill feedback: added a note that stakeholder-facing documentation should follow the team's working language.
- Verification: documentation-only change; no build needed.
- Next recommended task: use colleague answers to refine prototype page copy and seminar emphasis.

## 2026-06-16 | deployment | Fix GitHub Pages subpage navigation

Fixed broken GitHub Pages subpage links after Manuel noticed that the subpages were not shown through navigation.

- Evidence: commit `c5b51ed Fix GitHub Pages subpage links` pushed to `origin/main`; GitHub Actions run `27633488735` completed successfully.
- Root cause: `import.meta.env.BASE_URL` did not include a trailing slash in the generated links, producing paths such as `/Firmenschulungseminare` instead of `/Firmenschulung/seminare`.
- Verification: `npm run build` passed with 0 Astro check errors/warnings/hints; live `/Firmenschulung/seminare/` and `/Firmenschulung/login/` returned HTTP 200 with the new deployment timestamp.
- Next recommended task: visually review the public page and subpage navigation in the browser.

## 2026-06-16 | prototype | Website demo pages and content briefing started

Started turning the A/B wireframe into a single stakeholder-ready Variant B prototype path.

- Evidence: added `apps/website/src/layouts/BaseLayout.astro`; replaced the homepage with a focused Variant B story; added static demo pages for companies, seminars, qualification, system outlook, contact, and login demo; replaced the stylesheet for the new prototype structure; added `docs/requirements/content-briefing-colleague-prototype.md`.
- Decisions: show a dummy login as future-system outlook, not as a working app; keep real database, real accounts, and real data processing out of the 2026-07-01 prototype.
- Content support: prepared questions and draft wording for the colleague responsible for prototype content.
- Verification: `npm run build` passed with Astro check reporting 0 errors, 0 warnings, 0 hints; static preview returned HTTP 200 at `http://127.0.0.1:4321/Firmenschulung/`.
- Next recommended task: review the local prototype visually, then refine wording and page emphasis with colleague feedback.

## 2026-06-16 | requirements | First operational workflows clarified

Captured Manuel's answers to the first requirements-intake questions for the future administration system.

- Evidence: updated `docs/requirements/future-system-ideas-backlog.md`.
- Clarified workflows: staff create participants, book them into existing measures/courses/seminars, and book internships or placements to companies; missing companies may need to be created during the workflow.
- Major pain point: document packages currently require many separate Word documents, manual print/export, Word-to-PDF conversion, PDF merging, custom email text, and company sending.
- Role direction: Donner + Partner staff create and manage core records; companies later view their own orders/trainings/coaches and give feedback; coaches/lecturers later get calendars, accept/decline flows, interest in released assignments, history, and statistics; participants may later receive a separate app.
- Priority direction: start business focus with seminars; first document priorities are offers and company contracts; matching should likely use a score, with staff retaining final decisions.
- Next recommended task: keep the 2026-07-01 website prototype seminar-focused, then decide whether the first app slice should be seminar offers/contracts or participant booking/document-package automation.

## 2026-06-16 | requirements | Future backlog coverage checked

Checked the current chat requirements and `PROJECT_LOG.md` against the future-system ideas backlog.

- Evidence: updated `docs/requirements/future-system-ideas-backlog.md` with missing nuances for website-to-app data flow, document exports, email attachments/links, job workflows, matching criteria snapshots, feedback triggers, document templates, skill catalogs, and a coverage check.
- Skill feedback: added `SKILL_FEEDBACK_LOG.md` entry proposing more proactive requirements-intake questions in `write-requirements` or related coordination guidance.
- Decision: keep the ideas in the future-system backlog and continue treating them as post-2026-07-01 app scope.
- Open risk: requirements are expanding quickly; future sessions should ask targeted questions before turning backlog items into implementation work.
- Next recommended task: refine the website prototype first, then run a focused requirements intake for the first app slice.

## 2026-06-16 | requirements | Future system idea backlog added

Captured new brainstorming input for the later independent web-based administration system.

- Evidence: added `docs/requirements/future-system-ideas-backlog.md`; linked it from `docs/requirements/stakeholder-prototype-2026-07-01.md`.
- Ideas captured: automatic contracts and offers, email sending, job posting management, direct or "could be interesting" placement statuses, structured matching, possible later AI matching, commute-time calculation by public transport/car, company feedback links, dedicated email account, and possible Hermes Agent evaluation on available VPS resources.
- Decisions: keep these ideas out of the 2026-07-01 website prototype; treat them as future app backlog and data/architecture inputs.
- Blockers or risks: email account, document templates, skills taxonomy, routing provider, feedback security model, AI necessity, and Hermes Agent privacy/security review are all open.
- Next recommended task: after the prototype direction is stable, turn the first future-system slice into user stories and a core data model.

## 2026-06-16 | requirements | Stakeholder prototype and independent system scope clarified

Manuel clarified that the new website should not include a chatbot. The existing chatbot VPS is only a possible technical resource. The future app should become an independent web-based administration system with its own database, similar in scope direction to the old Sophisto system, but not dependent on the parent company's database.

- Evidence: added `docs/requirements/stakeholder-prototype-2026-07-01.md` and `docs/decisions/0001-subdomain-independent-system-database.md`.
- Decisions: no chatbot on the new website; first stakeholder prototype on 2026-07-01 remains database-free; later app needs login, backend API, independent database, and role-based access.
- Architecture assessment: website and app should use a backend API for operational data; neither should access the database directly.
- Blockers or risks: final subdomain, sub-brand name, legal/privacy wording, database engine, backend runtime, roles, and first app slice remain open.
- Next recommended task: refine the Variant B website prototype for the 2026-07-01 stakeholder presentation, while drafting a simple future app/data model separately.

## 2026-06-16 | planning | Subdomain and database direction reviewed

Manuel reported that the colleague preferred homepage Variant B because it looked more modern, and that EDV provided webspace access plus the option for MySQL/MariaDB.

- Evidence: local source document `Quellen/Zugangsdaten Server.docx` confirms EDV-created webspace, subdomain-versus-domain guidance, and available MySQL/MariaDB capacity; credentials were not copied into project memory.
- Decisions: proceed with a subdomain under `donner-partner.de`; use Variant B as the design direction, with corporate trust/compliance discipline from Variant A.
- Architecture assessment: because the later app must manage companies, seminars, coaches, participants, job posts, and related workflows, the database should be treated as an app/backend concern, not as a direct website dependency.
- Blockers or risks: final database engine, backend hosting boundary, authentication/roles, privacy/legal rules, backup/restore, and data retention still need explicit decisions before storing operational data.
- Next recommended task: write a short architecture/data ADR comparing VPS-hosted PostgreSQL, EDV-provided MariaDB/MySQL, and a managed database option.

## 2026-06-09 | deployment | GitHub Pages live

GitHub Pages deployment succeeded after enabling Pages with GitHub Actions and rerunning the workflow.

- Evidence: workflow run `27227037472` completed successfully; published URL `https://dp-manuel.github.io/Firmenschulung/` returns HTTP 200.
- Verification: checked deployment with `gh run view` and `curl -I https://dp-manuel.github.io/Firmenschulung/`.
- Decisions: keep Pages source as GitHub Actions.
- Blockers or risks: GitHub Pages cache may take a few minutes to show changes after future pushes; form remains non-operational/visual pending privacy setup.
- Next recommended task: review the live preview with the team and collect A/B/hybrid feedback.

## 2026-06-09 | deployment | GitHub Pages workflow pushed

Configured the Astro preview for GitHub Pages and pushed the first public website commit to `DP-Manuel/Firmenschulung`.

- Evidence: commit `8d1d4d4 Add Astro GitHub Pages preview` pushed to `origin/main`; added `.github/workflows/deploy.yml`; set Astro `site` and `base` for `https://dp-manuel.github.io/Firmenschulung/`.
- Verification: local `npm run build` passed after the Pages config change.
- Decisions: push only public website/deployment files; keep `Quellen/`, project memory, design docs, and local tooling out of the public commit for now.
- Blockers or risks: GitHub Pages may still need repository setting `Settings -> Pages -> Source: GitHub Actions`; public Actions URL returned 404 without login, so deployment status must be checked in GitHub UI.
- Next recommended task: enable/check GitHub Pages in repo settings, then open the published URL after the workflow completes.

## 2026-06-09 | implementation | Astro preview scaffolded

Created a working Astro website preview with two homepage wireframe variants and started a local dev server.

- Evidence: added `apps/website/package.json`, `astro.config.mjs`, `tsconfig.json`, `src/pages/index.astro`, `src/styles/global.css`, and `.gitignore`; updated `apps/website/README.md`.
- Verification: `npm run build` completed successfully; `curl -I http://127.0.0.1:4321` returned HTTP 200.
- Decisions: used portable project-local Node.js because system-wide installation required admin privileges; pinned Astro to version 5 after Astro 6 resolver issues in this Windows/path setup.
- Blockers or risks: npm audit reports moderate dependency vulnerabilities; no final logo/images/legal text yet; contact form is visual only pending privacy/legal setup.
- Next recommended task: review both variants in the browser and decide whether to refine Variant A, Variant B, or the proposed hybrid.

## 2026-06-09 | design | Homepage wireframe concept drafted

Created a team-ready homepage wireframe concept with two visual directions for comparison.

- Evidence: added `docs/design/homepage-wireframe-concept.md`.
- Verification: aligned both variants with sub-brand direction, primary CTA `Kontakt aufnehmen`, real contact form requirement, CI notes, website outline, and B2B benchmark research.
- Decisions: compare Variant A `Seriös-Corporate` against Variant B `Modern-Dynamic`; recommend a hybrid using Variant B's hero/process energy and Variant A's trust/compliance discipline.
- Blockers or risks: sub-brand name, DP visibility, legal/privacy form wording, approved assets, and whether platform/app appears on the homepage remain open.
- Next recommended task: create low-fidelity visual wireframes or prototype both variants for team review.

## 2026-06-09 | research | B2B design benchmark completed

Reviewed Arounda's B2B website design analysis and a focused set of official reference sites that fit this project's B2B, recruiting, education, compliance, and multi-audience needs.

- Evidence: added `docs/research/b2b-design-benchmark.md`.
- Verification: compared references against current website outline and corporate design notes; identified reusable patterns and stack implications.
- Decisions: recommend Astro as baseline for the public website; keep future webapp separate.
- Blockers or risks: final stack should still account for hosting, editor needs, legal/privacy form setup, and approved assets.
- Next recommended task: create a homepage wireframe concept or write an ADR for the stack decision.

## 2026-06-09 | requirements | Website outline drafted

Created the first implementation-ready website outline from the discovery brief and brand notes.

- Evidence: added `docs/requirements/website-outline.md`.
- Verification: checked outline against B2B-first decision, source-derived topics, CI constraints, and legal/privacy boundaries.
- Decisions: recommend `Beratungsgespräch anfragen` as the primary CTA for now; keep participant and platform/app content secondary.
- Blockers or risks: offer name, final branding mode, approved assets, legal pages, stack, and deployment target remain open.
- Next recommended task: choose whether to turn the outline into requirements, wireframes, or a technical scaffold.

## 2026-06-09 | discovery | Source documents analyzed

Read the company concept and corporate design manual from `Quellen` and turned them into project-ready discovery and design notes.

- Evidence: created `docs/requirements/product-discovery-brief.md` and `docs/assets/brand-design-notes.md`.
- Verification: extracted 212 paragraphs from `Konzept Unternehmen.docx`; extracted readable text from the corporate design PDF.
- Decisions: website should start B2B-first for companies; later platform/app scope remains separate from the first website MVP.
- Blockers or risks: public offer name, CTA, legal wording, approved logo/assets, and deployment target remain open.
- Next recommended task: turn the discovery brief into first website requirements and a homepage/content outline.

## 2026-06-09 | planning | Project starter adopted

Initial project onboarding completed for a new website-first project with room for a later webapp.

- Evidence: read `new-project-starter/README.md`, `new-project-starter/AGENTS.md`, `PROJECT_PLAN.md`, `PROJECT_STATUS.md`, `MEETINGS.md`, `SKILL_FEEDBACK_LOG.md`, and active `manage-project-state` / `coordinate-software-project` skills.
- Verification: confirmed the root is not yet a Git repository; created project memory and workspace structure.
- Decisions: use active runtime CodexSkills instead of copying full skill folders into this project; start with public website discovery.
- Blockers or risks: product goals, audience, content, brand direction, stack, and deployment target are still unknown.
- Next recommended task: run a compact website intake and then scaffold `apps/website`.
