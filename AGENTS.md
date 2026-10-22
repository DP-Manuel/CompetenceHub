# Competence Hub Agent Guide

## Start Here

Read this file, then [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), then only the canonical files relevant to the task.
Do not routinely read full PLAN, STATUS, LOG, all ADRs or QA history.
[Context policy](docs/architecture/PROJECT_CONTEXT_POLICY.md) defines ownership and loading.

## Identity And Boundaries

- Competence Hub: public Astro website in `apps/website`; separate authenticated FastAPI Portal in `apps/webapp`.
- Canonical repository: https://github.com/DP-Manuel/CompetenceHub.git.
- IONOS production, GitHub Pages preview and VPS Portal are separate environments; see [environment policy](docs/architecture/environment-policy.md).
- Production changes require a current, scoped release approval. Prior releases do not authorize new releases.
- Never read secrets, `.env*`, private keys or credentials. Keep `.tmp/`, private artifacts and credentials out of commits and external notes.
- Read `Quellen/` only for an explicitly authorized concrete path; publication approval is not source-directory access.
- Real accounts, roles, business data and Coach UUID/person mappings require their own approval. Never guess mappings or qualifications.
- PostgreSQL stays server-side; preserve Staging/production separation and the co-hosted Chatbot system.
- Preserve unfamiliar working-tree changes; inspect before editing and stage only owned changes.
- Do not move project material to ManuWiki or shared knowledge bases without Manuel's approval.

## Task Router

| Task | Start with |
| --- | --- |
| Website, Astro, public content, rights, Coaches | [Content index](docs/content/index.md) |
| Portal, Auth, API, architecture | [Architecture index](docs/architecture/index.md) |
| Calendar CAL-0/1/2, Finance, Analytics | [Requirements index](docs/requirements/index.md) |
| VPS, backup, restore, releases, SFTP | [Operations index](docs/operations/index.md) |
| Current larger work | Active plan linked from PROJECT_CONTEXT |
| History / previous evidence | [History index](docs/history/index.md), then a dated file or Git |
| Colleague-facing Teams updates | [Binding weekly standard](docs/updates/WEEKLY_UPDATE_STANDARD.md) |

## Memory And Completion

- PROJECT_CONTEXT is the current checkpoint, not a log; update on milestone, gate, blocker, workstream or production-state changes.
- Durable decisions belong in one canonical domain document. Link them instead of repeating details in root files.
- PROJECT_PLAN owns the long-term roadmap; an active ExecPlan owns current tasks, gates, evidence and the ordered 4-8-step horizon.
- PROJECT_STATUS is a compatibility pointer. PROJECT_LOG records significant milestones, decisions, regressions and releases only.
- Keep history intact. Hash-bind and archive before replacing substantial root memory.
- Use MEETINGS for stakeholder meetings; SKILL_FEEDBACK_LOG routes open proposals separately from implemented history.
- After meaningful blocks check for reusable workflow learning; capture evidence or explicitly record no new reusable learning.
- End with one recommended next block: purpose, inputs, deliverables and Definition of Done; state commit/push/deployment/data status.
- If Manuel must execute commands, final response must contain all commands in order, terminal names, working directory, expected result and secret warning.

## Skills And Tooling

- Use active skills in `%USERPROFILE%/.codex/skills`; canonical source is `C:/Users/RödelManuel/Documents/IT/CodexSkills`.
- Use manage-project-state and coordinate-software-project for steering; route implementation and verification by actual task.
- Do not vendor skills or modify global skills merely to reorganize project context.
- For stale skills, review `scripts/codexskills-update-check.ps1 -Validate -PlanSync`; global sync is intentional, scoped and backed up.
- On workstation `Z:/IT Development Manuel/Firmendingsbums/Website`, first read [second-workstation setup](docs/architecture/second-workstation-setup.md).
- Website Node before npm: `$env:PATH = "..\..\tools\node-v22.16.0-win-x64;$env:PATH"`.
- Run risk-appropriate checks; for docs validate links, integrity and diff rather than the entire app suite.
- Astro telemetry/AppData or spawn EPERM can be environmental; diagnose before judging code and document skipped evidence.
- Corporate identity, legal, rights, privacy, API and deployment contracts override discretionary styling.

## SFTP Operator Interaction

Manuel pastes the password from the clipboard into the hidden OpenSSH prompt.
Never preload SFTP commands before authentication.
Use Terminal A for login/SFTP and Terminal B to copy the verified command file only after A shows `sftp>`.
Use ASCII-safe operator paths and prove `lcd` before remote changes.
Follow the [SFTP runbook](docs/architecture/website-sftp-release-rehearsal-runbook.md).
