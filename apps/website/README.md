# Competence Hub Website

Astro workspace for the static public website MVP.

## Current MVP Routes

- `/` - homepage
- `/leistungen` - offer overview
- `/livecoaching` - live coaching offer
- `/businesscoaching` - business coaching offer
- `/unternehmen` - company-facing page
- `/coaches` - coach network page
- `/kontakt` - static request/contact page
- `/impressum` - legal placeholder, must be completed before live launch
- `/datenschutz` - privacy placeholder, must be completed before live launch

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
npm install
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

## Deployment

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
