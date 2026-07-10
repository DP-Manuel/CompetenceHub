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

There is currently no automatic GitHub Pages deployment workflow. Deployment is intentionally manual/freigabepflichtig and must be planned separately before live publication.
