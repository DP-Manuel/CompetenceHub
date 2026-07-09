# Project Agent Guide

Read this file before editing.

## Project Boundary

- Project name: Firmendingsbums Website
- Local project path: `C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website`
- Canonical remote: unknown
- Primary runtime or artifact type: website first; webapp and additional digital artifacts later
- Main entry points: project memory files in the repository root; website workspace in `apps/website`
- Sensitive areas: credentials, customer or company data, private brand material, analytics data, production deployment settings

## CodexSkills Access

- Use active runtime skills from `%USERPROFILE%\.codex\skills` for normal work.
- Use the local canonical CodexSkills folder when exact skill files, references, scripts, validation, or skill updates are needed: `C:\Users\RödelManuel\Documents\IT\CodexSkills`.
- If the local folder is unavailable or needs source history, use the canonical repository: `https://github.com/DP-Manuel/CodexSkills.git`.
- Use ManuWiki when skill catalog context, Manuel-specific knowledge, domain concepts, or portable AI-readable guidance is useful.
- Do not copy full skill folders into this project unless Manuel explicitly wants a local vendored snapshot.
- Run `.\scripts\codexskills-update-check.ps1 -Validate -PlanSync` when this project may be using stale skills. Use `-SyncActive -BackupActive` only after reviewing the plan and intentionally approving the canonical changes for global use. Use `-SyncSkill <name>` to limit either operation to selected skills.

## Default Skill Route

- Use `manage-project-state` to maintain `PROJECT_PLAN.md`, `PROJECT_LOG.md`, `PROJECT_STATUS.md`, `MEETINGS.md`, and restart handoffs.
- Use `coordinate-software-project` for broad planning, decomposition, routing, or end-to-end software delivery.
- Use `challenge-assumptions` when a critical sparring partner, outside-the-box view, blind-spot check, or optimization prompt is useful.
- Use `reverse-engineer-codebase` before substantial changes when behavior, architecture, data flow, or project conventions are unclear.
- Use `discover-product-context`, `write-requirements`, and `shape-user-stories` for product, requirements, backlog, or slice work.
- Use implementation, verification, delivery, and maintenance skills according to task intent; for website work this commonly includes `integrate-frontend`, `check-accessibility`, `review-performance`, and `write-tests`.
- Use `improve-skill-system` only for reusable workflow learnings that should improve CodexSkills itself.

## Project Memory

- Keep `PROJECT_PLAN.md` current after meaningful planning, scope, timeline, budget, stakeholder, risk, or decision changes.
- Keep `PROJECT_LOG.md` newest-first after meaningful work.
- Keep `PROJECT_STATUS.md` short and current when frequent handoffs, stakeholder updates, or multi-day work are happening.
- Use `MEETINGS.md` for stakeholder, steering, planning, review, retrospective, or decision meetings.
- Use `SKILL_FEEDBACK_LOG.md` for proposed CodexSkills improvements discovered during this project.

## Structure

- `apps/website` - first deliverable: public website.
- `apps/webapp` - reserved for the later web application.
- `docs/requirements` - product context, requirements, user stories, and acceptance criteria.
- `docs/architecture` - architecture notes, stack decisions, data/API sketches.
- `docs/decisions` - ADR-style decisions.
- `docs/assets` - notes about brand assets, copy, imagery, and source material.

## Data And Privacy

- Do not copy credentials, private documents, production data, personal data, or generated private artifacts into external notes.
- Sanitize examples before adding them to CodexSkills real cases, evals, release notes, or ManuWiki proposals.
- Ask Manuel before moving project material into ManuWiki or any shared knowledge base.

## Verification

- Run project-specific tests when available.
- For `apps/website`, use the project-local Node path before npm commands: `$env:PATH = "..\..\tools\node-v22.16.0-win-x64;$env:PATH"; npm run build`.
- If Astro build/check fails with `EPERM: operation not permitted, mkdir ...\AppData\Roaming\astro\Config` or `Could not load ... spawn EPERM`, the code may be fine; Astro/Vite is trying to do workspace-external or sandbox-restricted work. Re-run the same build with approved escalation or disable Astro telemetry in a documented way before judging the change.
- Document skipped checks with the reason, residual risk, and next verification action.
- For non-code artifacts, use artifact-specific verification in addition to normal tests.
- Binding project constraints, such as corporate identity, legal requirements, privacy expectations, API contracts, and deployment rules, override discretionary improvements.
