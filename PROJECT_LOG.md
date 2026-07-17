# Project Log

Newest entries first.

## 2026-07-17 | deployment preparation | Manuelle GitHub-Pages-Review vorbereitet

Für die Abstimmung mit Vertrieb und Mediendesign wurde das bestehende private Repository `DP-Manuel/CompetenceHub` als sinnvoller Review-Kanal bestätigt; das alte Firmenschulung-Repository wird nicht reaktiviert.

- Workflow: `.github/workflows/pages-review.yml` nutzt die offiziellen Astro-/GitHub-Pages-Actions und kann ausschließlich manuell über `workflow_dispatch` gestartet werden; Pushes veröffentlichen nichts automatisch.
- Review-Schutz: Der Pages-Build verwendet `/CompetenceHub`, zeigt einen sichtbaren Entwurfsstatus und setzt `noindex, nofollow, noarchive`. Dies ist keine Zugriffskontrolle; die veröffentlichte URL wäre weiterhin erreichbar.
- Freigabeblocker: Die Entwürfe für Elisabeth Schwabauer und Carolin Hupp dürfen erst nach Publikationsfreigabe öffentlich bereitgestellt werden.
- Verifikation: Review-Build mit GitHub-Pages-Basis erfolgreich; 22 Astro-Dateien ohne Fehler, Warnungen oder Hinweise geprüft und 19 statische Seiten erzeugt. Basis-Links, Review-Banner und Robots-Meta wurden im Build kontrolliert.
- Status: GitHub Pages ist im Repository noch nicht aktiviert; kein Commit, Push, Workflow-Lauf oder Deployment wurde durchgeführt.
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
