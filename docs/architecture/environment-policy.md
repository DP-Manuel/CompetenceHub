# Production, Preview And Backend Policy

Decision owner: Manuel. Accepted via supplied Post-Messe Product Addendum, 21.10.2026.

## Three Independent Environments

| Environment | Purpose | Publication / data boundary |
| --- | --- | --- |
| IONOS production | Stable public Website at competencehub.donner-partner.de | New scoped release gate for critical bugs, privacy/security fixes or expressly approved content |
| GitHub Pages preview | Approved frontend/content/UX development at dp-manuel.github.io/CompetenceHub/ | Existing manual Pages workflow, crawler blocked, no analytics or productive actions |
| VPS Portal/backend | Main technical product workstream | Isolated synthetic local/Staging evidence until separate runtime/data/deployment approvals |

The successful 17.10 Messe ends the temporary Messe freeze. Stable-production policy replaces it; no automatic production permission follows.
The 21.10 preview publication authorization covers the bounded preview implementation and necessary commit/push from a clean isolated worktree.
It does not extend to IONOS, backend activation, SMTP, real Portal identities or tracking.

## Public Preview Requirements

Preview is public, never a private sandbox. Use only approved public Coach/content data.
Apply noindex/nofollow/noarchive, blocking robots and production-domain canonical targets; avoid preview sitemap indexing.
Clearly label preview. Keep prototype appointments explicitly non-binding and synthetic; no productive form/API actions.
Disable analytics by default. Never mix preview visits with later production metrics.
Production builds must retain the stable production content/model until a separate production acceptance decision.

## Permanent Boundaries

Donner + Partner is operator; Lars Donner is responsible. Existing central D+P legal pages remain targets.
New data collection still needs a suitable privacy notice and review.
Coach approval authorizes publication of supported existing facts, not invented biographies, portraits, medical claims, qualifications or private source access.
