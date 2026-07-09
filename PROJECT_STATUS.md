# Project Status

Last updated: 2026-06-30

## Snapshot

- Overall status: green
- Workflow model: informal multi-day work
- Current phase/sprint/milestone/board status: kickoff-ready stakeholder prototype
- Current goal: present the modern Variant B website prototype at the official 2026-07-01 project kickoff and collect decisions for the next increment
- CodexSkills source: `C:\Users\RödelManuel\Documents\IT\CodexSkills` or `https://github.com/DP-Manuel/CodexSkills.git`
- Last CodexSkills update check: 2026-06-22, canonical commit `6acdc18`; all 29 repository skills validated and matched the active runtime installation
- Last CodexSkills sync plan or backup: 2026-06-22, `-PlanSync` showed no additions or updates; no real sync or backup was needed
- Done since last update: Christian Galvano's supplied portrait and a complete coach-page visual polish were deployed in commit `8f860f7`; GitHub Actions run `28425939779` passed; coach listing, detail page, and portrait asset returned HTTP 200; desktop and narrow local screenshots confirmed the reported box-balance issue is resolved
- In progress: none; prototype is ready for stakeholder review
- Next: present the live prototype, confirm profile wording and positioning, and capture stakeholder feedback and decisions
- Blocked: no blocking technical issue; product/content decisions are still open
- Decisions needed: public offer name, exact subdomain, sub-brand endorsement, legal wording owner, whether "Für Unternehmen" remains a separate page, first app module, database engine/location, document templates/package order, email account/provider, matching score model, soft skills, Christian Galvano profile wording, approved media-designer illustration/logo exports, references, routing provider, long-term technical owner, Redaktionsworkflow for non-technical colleagues

## Timeline And Budget

- Timeline signal: stakeholder demo target is 2026-07-01
- Budget/effort signal: unknown
- Confidence: high for setup; low for delivery estimates until scope is defined

## Stakeholder View

- What can be shown publicly: first real coach profile for Christian Galvano with Neuroleadership, Konfliktmanagement, and Stress-/Burnoutprävention at `https://dp-manuel.github.io/Firmenschulung/coaches/christian-galvano/`
- What needs a decision: sub-brand name, DP visibility, exact subdomain, form privacy wording owner, whether the company page remains separate, first future-app slice: seminar offers/company contracts versus participant booking/document-package automation, coach profile wording feedback, reveal framing for the pre-built website prototype, whether long-term content maintenance uses Astro-only, Astro plus CMS/API, WordPress, or later webapp-fed content
- What changed since last stakeholder contact: leadership reportedly does not yet know that a website prototype is being built; 2026-07-01 is the actual project start, so the prototype should be presented as prepared pre-work and a positive surprise. Colleague preferred Variant B; subdomain was chosen over a separate domain; EDV confirmed available MySQL/MariaDB capacity; chatbot is explicitly out of scope for the new website; future app needs an independent database.

## Restart Handoff

- Files to read first: `AGENTS.md`, `PROJECT_LOG.md`, `PROJECT_PLAN.md`, `SKILL_FEEDBACK_LOG.md`, `docs/requirements/content-briefing-colleague-prototype.md`, `docs/requirements/website-maintenance-handover-and-editor-workflows.md`, `docs/requirements/stakeholder-prototype-2026-07-01.md`, `apps/website/src/pages/index.astro`, `apps/website/src/pages/coaches.astro`, `apps/website/src/pages/coaches/christian-galvano.astro`, `apps/website/src/pages/seminare.astro`, `apps/website/src/styles/global.css`
- Repo state to remember: public website commit `8f860f7` is pushed and deployed; internal docs/project memory, source PDFs, and temporary review files remain local and should not be pushed unless Manuel explicitly wants that.
- Tooling note: Astro build/check can fail in the sandbox when it tries to create `AppData\Roaming\astro\Config` for telemetry or when Vite/Astro hits `spawn EPERM`. Treat that as an environment issue, not a code failure; rerun the same build with approved escalation or documented telemetry disablement.
- CodexSkills note: active skills match canonical commit `6acdc18`. The local starter and project update helper now include safe planning, selective sync, backups, and explicit absolute skill paths; root `AGENTS.md` remains authoritative for this website.
- Next concrete action: present the live prototype at the kickoff, record decisions and feedback, then update requirements and priorities
- Risks to remember: keep website B2B-first; request original approved seminar illustrations and logo exports from the media designer before real-site production; do not imply that the app/login/database already exist
