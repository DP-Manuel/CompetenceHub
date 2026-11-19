# Competence Hub Website

Astro workspace for the static public website MVP.

COACH-4 adds only an opt-in local comparison build. Static defaults remain
canonical. See the [projection/transition contract](../../docs/architecture/coach-public-projection-contract-v0.1.md)
for public artifacts, environment rights, isolated output and later release gates.

## Current MVP Routes

- `/` - homepage
- `/leistungen` - offer overview
- `/livecoaching` - live coaching offer
- `/businesscoaching` - business coaching offer
- `/unternehmen` - company-facing page
- `/coaches` - coach network page
- `/kontakt` - static request/contact page
- `/impressum` - reference to the central D+P legal information
- `/datenschutz` - reference to the central D+P privacy information

Legacy/prototype routes remain build-safe but are not part of the main navigation:

- `/seminare`
- `/qualifizierung`
- `/system`
- `/login`

The contact form is static. It does not authenticate, submit data, store data, or connect to a database.

## Local Commands

Use the portable Node.js runtime from the repository root:

```powershell
$env:PATH = "$PWD\tools\node-v22.16.0-win-x64;$env:PATH"
cd apps\website
  npm ci
npm run dev
```

If Astro's dev server is blocked by the Windows sandbox, build and serve the static output:

```powershell
$env:PATH = "$PWD\tools\node-v22.16.0-win-x64;$env:PATH"
cd apps\website
$env:ASTRO_TELEMETRY_DISABLED = "1"
npm run build
node .\scripts\serve-dist.mjs
```

Static preview URL:

```text
http://127.0.0.1:4321/
```

## Local V2 Calendar Journey

Build from this workspace with the portable Node runtime on PATH. Use a fresh,
private output directory supplied by the loopback runner:

```powershell
$env:ASTRO_TELEMETRY_DISABLED = "1"
node ./node_modules/astro/astro.js build --config astro.v2-local.config.mjs "--outDir=$privateOut"
node ./scripts/verify-v2-local-dist.mjs "$privateOut"
```

Serve the output as directory indexes and static assets at `/website/` on the
same loopback origin as `/portal/`. The separate config is the only switch;
standard Production and Pages builds cannot opt in via environment flags.
The local output is deliberately non-indexable and is not a release artifact.

- `/website/leistungen/#v2-demo-angebot` links to
  `/website/coaches/v2-demo-coach/`. The demo is separate from approved Finder
  entries, family links and real contact links.
- The synthetic profile links to `/portal/calendar-public.html?coach=v2-demo-coach`.
  The Portal owns event selection and maps only the synthetic stored path
  `/coaches/v2-demo-coach/` to the mounted profile. The Website's main Calendar
  navigation opens the unfiltered calendar; Portal-Login opens `/portal/`.
- Astro's local scripts and bundled styles are same-origin files. The loopback
  runner can authorize retained inline style blocks with per-document CSP
  SHA-256 hashes. No inline style attributes or executable inline scripts are
  required. Keep Portal and API CSP unchanged.

The optional second argument to `verify-v2-local-dist.mjs` is a standard
Production artifact directory for checking official Finder data and family links.

## Deployment

The prepared header Portal entry is off until `WEBSITE_PORTAL_URL` holds the
confirmed HTTPS `/portal/` address. Local design mode is dev-only and cannot
appear in a public build. See [local design, single setting and evidence](../../docs/architecture/website-portal-login-2026-11-17.md).

The repository contains a manual GitHub Pages review workflow at
`.github/workflows/pages-review.yml`. It has no `push` trigger and cannot
publish automatically. The review build uses `/CompetenceHub` as its base path,
adds a visible draft banner, and sets `noindex, nofollow, noarchive`.

Before a manual run:

1. Confirm that every named coach has approved publication of the current draft.
2. Commit and push the reviewed website state without `.env`, `.tmp`, or private source material.
3. In GitHub repository settings, select GitHub Actions as the Pages source.
4. Run `Publish GitHub Pages review` manually from the Actions tab.

GitHub Pages is not an access-controlled review environment. `noindex` reduces
search-engine discovery but does not make the URL private. Production deployment
to the final domain remains a separate approval and release step.

## Post-Messe Preview

`WEBSITE_ENV` is the only mode selector: `production` (default) or `preview`.
Do not set `GITHUB_PAGES_REVIEW` or `PUBLIC_REVIEW_MODE` independently; conflicting
legacy values fail validation. Local environment files are not loaded.

From this workspace, with Node 22.16.0 on PATH:

```powershell
$env:ASTRO_TELEMETRY_DISABLED = "1"
npm ci
npm run test:preview
$env:WEBSITE_ENV = "production"
npm run build
npm run verify:dist
$env:WEBSITE_ENV = "preview"
npm run build
npm run verify:dist
node scripts/serve-dist.mjs
```

Preview: http://127.0.0.1:4321/CompetenceHub/
Production output stays in `dist`; preview output is isolated in `dist-preview`.
Only the latter is uploaded by the manual Pages workflow.

The05.11 Website-first slice adds approved Guelcan short offerings, combined
Coach/topic/offer search and encoded Coach/format-specific email drafts in
Preview only. These drafts open the visitor's mail client; the site does not
send or store them. Held Becker candidates remain excluded. Registry projection
stays opt-in and inactive by default; no database or key setup is needed here.
Version inventory, current return targets and environment differences:
[Website-first report](../../docs/content/website-first-2026-11-05.md).

COACH-5 extends the existing `/leistungen/#angebotsfinder` in Preview only:
27 grouped entries /29 formats from the three explicitly approved offering
lists, shared canonical topics, combined filters and contextual mail drafts.
The component accepts a public view model; no Registry source is activated.
Production resolves the Finder import to a no-output component at build time,
so neither markup nor its client bundle enters the stable52-file artifact.
[Scope and acceptance](../../docs/exec-plans/active/coach5-offering-finder-2026-11-05.md).
For an explicitly selected installed browser the QA runner accepts
`WEBSITE_QA_BROWSER_EXECUTABLE`; its report names the actual engine/version.

For Edge browser checks use `scripts/run-preview-browser-acceptance.py` and the
existing production `scripts/run-messe-browser-acceptance.py`. Both accept
`WEBSITE_NODE` for the absolute Node executable in a separate worktree.
The Python environment must provide Playwright and Microsoft Edge.
Detailed boundaries, provenance and verification:
[Preview implementation](../../docs/architecture/github-pages-preview-2026-10-21.md).
