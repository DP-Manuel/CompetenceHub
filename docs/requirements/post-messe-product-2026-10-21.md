# Post-Messe Product Decisions

Source: Manuel's supplied Context Architecture V2 request and Product Addendum, 21.10.2026.
This document owns accepted product scope. Manuel confirmed on 21.10 that no additional Messefeedback is currently available; the supplied input is complete for this block.
Feedback is input, not automatic truth; classify bug/UX/content/design/requirement/architecture/privacy/backend/operations/future with route, evidence, existing behavior, conflicts, owner/gates, effort, risk and P0/P1/P2/Future priority.

## Supplied Feedback Triage

All rows cite the supplied 21.10 Product Addendum; no unprovided Messe document was inspected.

| Input / type | Route / existing state | Priority / effort / risk | Decision / gate / evidence |
| --- | --- | --- | --- |
| Stable production + official preview / architecture, operations | Existing manual Pages workflow; public IONOS live | P1 / medium / environment mix-up | Accepted; isolated build and publication proof |
| All intended Coaches approved / rights, content | Six profiles removed for Messe privacy scope | P1 / medium / accidental production restoration | Preview-only approval supersedes preview restriction; production privacy checks retained |
| Elisabeth offers / content, UX | Historical dedicated profile; supplied grouped titles | P1 / medium / therapeutic scope | Manuel confirmed Schwabauer on 21.10; supplied groups only, separate HeilprG mention |
| Three topic categories / requirement, UX | Existing static Coach/topic filter | P1 / medium / category-topic-format conflation | Accepted many-to-many model and accessible filter tests |
| Manuela Advisory / bug, content | Existing specific external Advisory link | P2 / small / unwanted production delta | Preview target explicitly supplied; href/browser check |
| Aggregate analytics / backend, architecture, privacy | No active tracking | P2 / discovery / privacy and false metrics | Options/design only; legal/consent OPEN, no service activation |
| Additional Messefeedback / future | Manuel confirmed none currently available | Future / unknown | Only reopen if a concrete authorized source is supplied; no current source blocker |

## Accepted Preview Scope

- All currently intended Coaches are approved for preview: supported existing names, portraits, competencies and text only.
- Production stays at its separate accepted release; do not restore former identities into IONOS artifacts implicitly.
- Themes have many-to-many categories `personalentwicklung`, `persoenlichkeitsentwicklung`, `karrierecoaching`.
- `Alle Themen` is a computed overall view, never a stored category.
- Coach, topic, category and offer format remain separate data concepts.
- Filters work on desktop/mobile/keyboard and announce updates; canonical topics are not duplicated.
- Manuela Rodriguez profile uses https://advisory.donner-partner.de/ as Advisory target, including href/structured data if present.
- Keep production/preview datasets isolated at build time using existing Astro conventions.

## Elisabeth Schwabauer Offers

The supplied addendum initially said Schabbauer; Manuel explicitly confirmed Elisabeth Schwabauer in the 21.10 spelling clarification.
Use Schwabauer in preview and retain the existing profile path; no new person/UUID mapping follows.
No concrete private source path is authorized; the supplied text is the available offer source.

Focus: Psychische Gesundheit am Arbeitsplatz.

| Format | Supplied titles |
| --- | --- |
| Vortraege | Psychische Gesundheit und gesund fuehren; Positive Leadership - Mitarbeiter staerken und Potenziale entfalten; Positive Psychologie im Arbeitsalltag |
| Workshops | Belastungen fruehzeitig erkennen und handeln; Gesund Fuehren; Umgang mit psychisch belasteten Mitarbeitenden; Wiedereingliederung nach psychischer Erkrankung; Mentale Gesundheit im Homeoffice und hybriden Arbeiten; Stressmanagement und Burnout-Praevention; Positive Psychologie |
| Individuelle Angebote | Resiliente und leistungsfaehige Teams entwickeln; Psychische Gefaehrdungsbeurteilung verstehen und umsetzen; Psychische Belastungen verstehen; Gefaehrdungsbeurteilung in der Praxis; Kurzanalyse im Team (KiT) |
| Weitere | Coaching; Psychotherapie (HeilprG) |

Public display uses normal German orthography. No missing numbered 2.2 is inferred.
Group offers using existing design/components rather than a long bullet wall.
The source's full document hierarchy has not been inspected: do not invent hierarchy beyond the supplied groups.
Psychotherapie (HeilprG) is a separate supplied service mention; no therapeutic promises, medical eligibility claims or mixing into Mindforge Life Coaching.

## Analytics Scope

ANALYTICS-01 is architecture/discovery only: aggregate public usage and a future protected Admin cockpit.
First investigate first-party self-hosted/no cookies/no browser storage/no persistent ID/no fingerprinting, minimized IP processing and short defined retention.
Exclude identity lists, raw-IP dashboard, replay, recordings, form content, keystrokes, persistent profiles and advertising.
Compare own aggregation, Matomo and a lightweight self-hosted alternative using primary sources.
[Analytics discovery](analytics-01-discovery-2026-10-21.md) owns the comparison and proposed design; PRIV-ANALYTICS-01 owns storage/consent decisions.
Consent remains OPEN pending privacy/legal review; no automatic banner and no active tracking.

## Gates

Only preview publication is authorized here. Production, real accounts/data, SMTP, backend deployment and tracking retain separate approvals.
CAL-2, .ics execution, FIN-01 implementation and PWA remain later scope.
After preview and Analytics discovery: stop, report and recommend one existing-backend slice.

## Subsequent Batch Authority: 22.10.2026

Manuel's Calendar Access Contract and Batched Development addendum supersede
the preceding local stop for the bounded follow-up, not the production/data gates.
The additive access policy, tests, native synthetic Staging acceptance and
scoped commit/push are authorized; production remains unchanged.

Preview UX now follows progressive disclosure: one initial All-topics Hub,
then three category satellites, then only relevant canonical topics. All remains
computed and many-to-many membership remains intact. Existing CI, gentle motion,
keyboard/touch semantics, Reduced Motion and mobile adaptation are required.
Home Mindforge/contact Bubble spacing must be proved geometrically at
2048/1440/1280/960/390 CSS px and actual 200% zoom. Publication is Pages only.

One fully prepared Staging window must contain native browser/API/RBAC checks,
exact synthetic cleanup, independent SQL zero residue and service/network health
before closing its owned tunnel. Prefer an already-working SSH key over new
keys or security changes. No credential-file reads or password automation.

Only after native acceptance is fully green, advance to one safe backend slice
chosen from actual context, preferably CAL-1 readiness preparation. Native
acceptance is not production activation. The [active plan](../exec-plans/active/post-messe-backend-horizon-2026-10.md)
and [batch evidence](../architecture/calendar-cal1-access-batch-2026-10-22.md)
own current execution and results; Analytics consent remains OPEN.
