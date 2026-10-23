# GitHub Pages Preview: 21.10.2026

## Current Publication: 23.10.2026

The historical checks below remain dated. Current Preview source is
`3e99e8e6151d78e281e17ed54d6c435bf4e9d740`, successful
[Pages run39932275108](https://github.com/DP-Manuel/CompetenceHub/actions/runs/39932275108).
Susanne Klemm is the ninth approved Preview Coach;89 actual public onboarding
and134 Hub checks PASS, including390px and native200% zoom. Source/portrait
rights, taxonomy, screenshots and production isolation are owned by the
[23.10 content report](../content/susanne-klemm-preview-2026-10-23.md).
No IONOS write, backend activation or real Coach Registry import.

## Preview UX Follow-Up: 22.10.2026

Manuel's batched-development addendum authorizes the preview-only topic Hub and
home Bubble-clearance corrections, their scoped commit/push and publication.
The directory now starts with one All-topics button, reveals three category
satellites on interaction, then only the selected category's canonical topics.
All is still computed; hash restoration and many-to-many membership remain.
Mobile adapts to a vertical, touch-operable category list instead of shrinking
the desktop diagram. Buttons expose expansion/selection, keyboard focus and
live results; a gentle pulse pauses on interaction and stops for Reduced Motion.

The actual home conflict came from the Hub stage's negative flow margins,
combined with circular nodes extending beyond percentage anchors. A preview-only
inline component removes that intrusion, rather than changing production CSS or
blindly repositioning individual nodes. Before geometry is from the unchanged
local production artifact (same home Hub layout); it is not an old live-preview
screenshot. Desktop Mindforge clearance was about -22 px, CTA clearance -1 px.
Afterward the desktop checks measure 31-49 px clearance at 960-2048 CSS px.

QA: 8 model tests, Astro 58 files/zero diagnostics, 33 routes, 1,243 preview and
1,237 production references, 1,219 broad Edge checks and 134 focused Hub checks.
The focused run covers 2048/1440/1280/960/390 CSS px, touch, keyboard, actual text
fit, satellite separation, motion and real 200% browser zoom (observed 703 CSS
px and DPR 2 at a fixed physical window, not merely a scale-factor simulation).
The zoom preference is set only in a temporary test profile, following
[Chromium's zoom preference implementation](https://chromium.googlesource.com/chromium/src/+/lkgr/chrome/browser/ui/zoom/chrome_zoom_level_prefs.cc).
All contexts/servers/profiles were stopped/removed. No external/write requests,
JS errors or failed resources in the broad preview test.

The production build's full 52-entry filename/SHA-256 manifest was compared
before and after: **no changed, added or removed files**. No SFTP or IONOS write.
Generated JSON/screenshots stay in ignored release-artifacts.

Publication completed from commit `1cc481de9210cc43126e574818fdfd5046b96965`
through the existing manual workflow only:
[Actions run 39774218286](https://github.com/DP-Manuel/CompetenceHub/actions/runs/39774218286).
The same 134 focused checks passed against the actual public preview, including
touch, keyboard, Reduced Motion, all five widths and real 200% zoom. The runner's
`--public` mode writes separate `public-acceptance.json` evidence; it does not
publish anything. No production artifact, service or deployment was changed.

## Scope And Authority

Manuel's supplied Post-Messe Product Addendum authorizes the existing GitHub
Pages preview, all intended approved public Coach content, category navigation,
Elisabeth's supplied offers and Manuela's Advisory link correction.
His subsequent explicit spelling confirmation is **Elisabeth Schwabauer
(bisheriges Profil)**. The display name and historical elisabeth-schwabauer
route remain unchanged. There is no unresolved spelling/source dependency.
No further Messefeedback currently exists.

This implementation is confined to apps/website, the existing manual Pages
workflow, this document and the
[publication matrix](../content/coach-publication-matrix-2026-09-24.md).
Root memory, context migration, Analytics discovery, Portal and production
operations are outside this slice. No private source directory or environment
file was read. Nothing authorizes IONOS upload, backend activation, real Portal
data, tracking or productive submissions.

## Build Boundary

config/environment.mjs validates the single WEBSITE_ENV selector:

| Mode | Site / base | Output | Content |
| --- | --- | --- | --- |
| production (default) | competencehub.donner-partner.de / | dist | Existing stable two real Coaches and six explicit demos |
| preview | dp-manuel.github.io /CompetenceHub | dist-preview | Eight approved real Coaches; no demo profile routes |

Empty/unknown modes and conflicting legacy GITHUB_PAGES_REVIEW or
PUBLIC_REVIEW_MODE values fail closed. Astro derives PUBLIC_REVIEW_MODE at
compile time from this configuration; callers do not set it separately.
Vite envDir=false prevents loading local .env files.

Astro resolves @website-coaches to the appropriate dataset at build time.
Historical templates live outside src/pages, in src/preview/profiles, and are
injected only in preview. Archived portraits live outside public, in
src/preview/portraits, and are copied only by the preview build hook.
Separate output directories avoid mixing artifacts when switching modes.
Merely hiding a production card is not the isolation mechanism.

Production still uses its unchanged dataset, demo getStaticPaths, robots,
sitemap, metadata, layout and old Manuela Advisory href. Production acceptance
is required before any future promotion. The existing production release
script is not used to build preview.

## Content Provenance

The six removed profile templates and five portraits were restored
mechanically from Git 53a89a8, immediately before removal commit 9955e03.
The historical Coach records retain their supported text and associations;
the current Christian and Manuela records take precedence.

| Restored slug | Portrait |
| --- | --- |
| elisabeth-schwabauer | elisabeth-schwabauer.webp |
| carolin-hupp | None: original monogram/placeholder |
| guelcan-elmas-brandes | guelcan-elmas-brandes.png |
| wegner-ney | wegner-ney.jpg |
| goran-celic | goran-celic.png |
| stefanie-becker | stefanie-becker.webp |

The model test fixes the five original Git blob IDs and checks actual
portrait bytes without requiring full Git history in CI. No portrait was
invented, re-downloaded, re-encoded or extracted from a private source.

Elisabeth's 17 supplied offer titles are grouped as 3 talks, 7 workshops,
5 individual offers and 2 further service mentions. No missing numbered
item is invented. Native keyboard-operable details/summary groups remain
expanded initially. Psychotherapie (HeilprG) is separated from Coaching and
explicitly not offered as bookable therapy through Competence Hub.

Only preview changes Manuela's Advisory target to
https://advisory.donner-partner.de/. Production keeps its existing href.

## Topics And Interaction

src/preview/topics.ts owns three actual category IDs:
personalentwicklung, persoenlichkeitsentwicklung, karrierecoaching.
Each canonical topic has a categories array, not one category field.
Alle Themen is computed, never stored as a fourth category.
Coach topic assignments, category navigation and offer formats remain separate.
Category assignments organize existing topics; they do not certify new
qualifications. No Coach is newly assigned to Mediation.

Category and topic buttons expose aria-pressed, labelled groups, aria-controls,
visible keyboard focus and a polite atomic result status. Topics occur once
in the canonical source and DOM, even when visible under multiple categories.
Category changes reset the topic selection; invalid deep-link values fall
back to All. Hash reloads restore valid selections. All includes Coaches
without a topic, while a specific category/topic requires a match.
Without JavaScript all approved profiles and ordinary links remain available.

Calendar events remain explicitly synthetic and non-binding. In preview their
runtime-generated Coach links target a valid filtered Coach directory rather
than removed demo routes; they do not claim real Coach availability.
The production calendar JS remains unchanged after compile-time elimination.

## Crawlers And Requests

Every preview HTML page carries noindex, nofollow, noarchive and the label
Entwicklungs-/Vorschauversion. Existing production-equivalent pages retain
production-domain canonicals and OpenGraph URLs with no preview base.
Restored preview-only profiles omit both canonical and og:url; 404 continues
to omit canonical. Preview sitemap is empty. Preview robots.txt blocks all.

Important limitation: /CompetenceHub/robots.txt is below the origin root and
cannot control dp-manuel.github.io as a whole. No root-domain setting is
changed. Page-level noindex remains essential; public preview is not private.
The existing Pages environment policy is not changed.
No analytics, external data submission, API writes, browser storage or real
backend actions are introduced.

## Workflow And Verification

.github/workflows/pages-review.yml remains workflow_dispatch only and uses
the existing github-pages environment. Node 22.16.0 and npm ci use the
existing lockfile. It runs model/provenance tests, production Astro check,
build and link/privacy gate, then preview check/build/link/metadata gate.
Only dist-preview is uploaded and deployed. There is no IONOS/SFTP step.
Deployment credentials are scoped to the deploy job.

Local commands live in the [Website README](../../apps/website/README.md).
The real Edge runner is scripts/run-preview-browser-acceptance.py; the existing
production runner is scripts/run-messe-browser-acceptance.py.
Set WEBSITE_NODE to the absolute repository-local node.exe when using a
separate worktree; use an existing Python/Playwright environment, not a new
framework.

Local evidence is generated under apps/website/release-artifacts/preview-qa
(ignored, not committed). compare-production.mjs compares every filename and
byte against its baseline subdirectory. Browser tests check all 33 HTML routes
on desktop, 390px and 200-percent-equivalent reflow (640 CSS px/device scale 2).
This is reflow emulation, not a claim of browser-chrome zoom automation.
The tests exercise keyboard/focus, many-to-many and computed All, hash
restoration, empty Mediation, all profiles/portraits, all offer groups, Advisory
href, homepage rail links and all generated links for all seven sample events
on both calendar routes. They abort/record external network and write requests.

Final local verification, Microsoft Edge 155.0.4283.62:

- Astro check: 58 files, zero errors/warnings/hints in both modes.
- Both static builds: 33 HTML pages each.
- Production: 1,237 internal references and original identity/privacy gate pass.
- Preview: 1,243 internal references plus robots/noindex/canonical/sitemap gate pass.
- Model/provenance tests: 8/8.
- Existing production Edge acceptance: 865/865.
- Preview Edge acceptance: 1,213/1,213 across all three viewport modes;
  zero console errors, resource failures, external requests or write requests.
- Nine screenshots visually reviewed: directory, Elisabeth offers and Manuela
  Advisory, each on desktop/390/reflow. No text overlap or horizontal overflow.
- Final typography follow-up: category labels use fixed 14px type without a
  forced word break. Focused real-Edge checks pass at 1440px, 390px and
  200-percent-equivalent reflow. Persönlichkeitsentwicklung is one line:
  measured text 189.44px, available width 195px / 250px / 202.39px respectively.
  The three directory screenshots were refreshed and visually reviewed.
  The browser runner now asserts single-line fit for every category label.
  The 1,213-check broad run above preceded this typography-only adjustment;
  the follow-up reran both build/link gates and the three focused viewport checks.
- Full final production inventory: 52/52 files byte-identical to the pre-edit
  worktree build, including the original Manuela href, calendar JS and all CSS.
  Aggregate filename-and-byte SHA-256:
  0a23f7f354cba72ac3a1f465ef709ebfba38055f723a01903433238b5feb5959.
- A pre-existing mobile overflow in the hidden company-login placeholder was
  fixed only in preview, as was category word wrapping; production is unchanged.
- git diff --check passes. Build outputs/screenshots remain ignored.

This is local implementation/QA evidence, not a claim of a successful Actions
run or public deployment. No commit, push, dispatch, production connection,
real-data write or Analytics activation occurred in this implementation session.

## Changed Files

Paths relative to the isolated worktree; generated evidence is excluded:

```text
.github/workflows/pages-review.yml
apps/website/.gitignore
apps/website/README.md
apps/website/astro.config.mjs
apps/website/config/environment.mjs
apps/website/package.json
apps/website/scripts/compare-production.mjs
apps/website/scripts/run-messe-browser-acceptance.py
apps/website/scripts/run-preview-browser-acceptance.py
apps/website/scripts/serve-dist.mjs
apps/website/scripts/test-preview-model.mjs
apps/website/scripts/verify-dist-links.mjs
apps/website/src/components/CalendarPrototype.astro
apps/website/src/layouts/BaseLayout.astro
apps/website/src/pages/coaches.astro
apps/website/src/pages/coaches/[slug].astro
apps/website/src/pages/coaches/manuela-rodriguez.astro
apps/website/src/pages/index.astro
apps/website/src/pages/login/[bereich].astro
apps/website/src/pages/sitemap.xml.ts
apps/website/src/preview/CoachDirectory.astro
apps/website/src/preview/ElisabethOffers.astro
apps/website/src/preview/coaches.ts
apps/website/src/preview/elisabeth-offers.ts
apps/website/src/preview/historical-coaches.ts
apps/website/src/preview/portraits/elisabeth-schwabauer.webp
apps/website/src/preview/portraits/goran-celic.png
apps/website/src/preview/portraits/guelcan-elmas-brandes.png
apps/website/src/preview/portraits/stefanie-becker.webp
apps/website/src/preview/portraits/wegner-ney.jpg
apps/website/src/preview/profiles/carolin-hupp.astro
apps/website/src/preview/profiles/elisabeth-schwabauer.astro
apps/website/src/preview/profiles/goran-celic.astro
apps/website/src/preview/profiles/guelcan-elmas-brandes.astro
apps/website/src/preview/profiles/stefanie-becker.astro
apps/website/src/preview/profiles/wegner-ney.astro
apps/website/src/preview/topics.ts
apps/website/tsconfig.json
docs/architecture/github-pages-preview-2026-10-21.md
docs/content/coach-publication-matrix-2026-09-24.md
```

## Residuals And Handoff

The initial locked npm install reported 17 dependency advisories: 1 low,
4 moderate, 11 high, 1 critical. No dependency upgrade or audit-fix was mixed
into this content slice. Main completed the bounded
[dependency assessment](preview-dependency-assessment-2026-10-21.md):
no reachable high/critical runtime exploit path was found in this exact static
slice under its documented trusted-input/no-SSR conditions. This is not a
general dependency security approval; toolchain upgrades remain separate debt.
The grouped offers are sourced only from the supplied text, not an unseen
original document or private attachment.
No new reusable skill-system learning was evidenced beyond the already
documented environment and artifact-isolation boundary.

Next recommended block: review the bounded diff and final evidence, commit
only this slice, push/dispatch the authorized preview through the existing
main-only Pages gate, then smoke-test public metadata, profiles and runtime
links. Done means the published preview passes those checks while IONOS
remains unchanged. Integration/publication belongs to the coordinating main
session; this worktree must not independently commit, push or dispatch.
