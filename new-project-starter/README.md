# CodexSkills New Project Starter

Copy this folder's files into a new project when Manuel wants to start real work with CodexSkills.

For an existing project, do not blindly overwrite useful project memory. Merge these files as compact handoff scaffolding, keep existing detailed docs in place, and point the starter files to those detailed sources.

## Recommended Access Model

Use this order:

1. Active runtime skills: `%USERPROFILE%\.codex\skills`.
   - Best for daily work because Codex can discover the approved skills automatically.
2. Canonical source: `https://github.com/DP-Manuel/CodexSkills.git`.
   - Best when exact skill files, references, scripts, version history, validation, or skill updates are needed.
3. ManuWiki / Obsidian Vault.
   - Best for portable understanding, skill catalog lookup, Manuel-specific knowledge, and cross-project context.

Do not copy full skill folders into each downstream project by default. That creates drift. Copy this starter package instead, then rely on active runtime skills and the canonical CodexSkills repository.

For academic writing, LaTeX, thesis, workbook submission, or institution-specific document workflows, adapt the starter with `references/academic-project-starter-adaptation.md` from the CodexSkills repository. Those projects should name the active paper folder, source/input folder, citation rules, build command, and rendered-document quality gates.

## Skill Update Check

Use the local canonical source first:

```powershell
.\scripts\codexskills-update-check.ps1 -Validate -PlanSync
```

Default source path:

```text
C:\Users\RödelManuel\Documents\IT\CodexSkills
```

Canonical repository:

```text
https://github.com/DP-Manuel/CodexSkills.git
```

The plan shows file-level additions, updates, and destination-only files that will be preserved. Limit the plan to selected skills when useful:

```powershell
.\scripts\codexskills-update-check.ps1 -PlanSync -SyncSkill write-tests,manage-project-state
```

To refresh the active runtime skills after the local CodexSkills repository has been intentionally updated, validated, and reviewed:

```powershell
.\scripts\codexskills-update-check.ps1 -Validate -SyncActive -BackupActive
```

Backups are stored under `%USERPROFILE%\.codex\skill-backups\<timestamp>`. `-SyncSkill <name>` can also restrict the real sync. The check reports local repository state and never pulls remote changes automatically.

## Files To Copy

- `AGENTS.md` - project-local instructions and skill routing.
- `PROJECT_PLAN.md` - current plan, workflow model, timeline, budget, risks, decisions, and restart note.
- `PROJECT_LOG.md` - newest-first project history.
- `PROJECT_STATUS.md` - compact current-state snapshot for quick handoff or stakeholder updates.
- `MEETINGS.md` - recurring or ad-hoc meeting notes.
- `SKILL_FEEDBACK_LOG.md` - proposed improvements to CodexSkills discovered during the project.
- `scripts/codexskills-update-check.ps1` - local update/validation/sync helper for CodexSkills.

## Existing Project Adoption

When the project already has detailed docs, deployment notes, feedback plans, or a long project journal:

1. Read the existing project instructions and recent status first.
2. Keep detailed history in its current files.
3. Use root-level `PROJECT_PLAN.md`, `PROJECT_LOG.md`, and `PROJECT_STATUS.md` for compact restart memory.
4. Link compact starter files to the detailed docs instead of duplicating all history.
5. Preserve unrelated untracked files, generated artifacts, and local-only evidence unless Manuel explicitly asks for cleanup.

## Optional Multi-Artifact Web Scaffold

For website, webapp, CMS integration, or mixed public/internal projects, start with a small structure and expand only when real work needs it:

```text
apps/
|-- website/
`-- webapp/
docs/
|-- requirements/
|-- architecture/
|-- deployment/
`-- decisions/
assets/
data/
scripts/
```

Use only the folders that match the project. If there is one application, keep it simple. If the website, admin app, chatbot, or generated artifacts have different build/deploy lifecycles, separate them early enough that commands, docs, and ownership stay clear.

## Skill Feedback Rule

During the project, collect possible skill improvements in `SKILL_FEEDBACK_LOG.md` first. Do not edit CodexSkills immediately from every observation.

When the pattern is reusable, high-risk, repeated, or clearly reduces future work:

1. Record the evidence in this project's `SKILL_FEEDBACK_LOG.md`.
2. Decide whether it belongs in CodexSkills, ManuWiki, project docs, or nowhere yet.
3. Jump back to the CodexSkills repository.
4. Use `improve-skill-system` to update the skill, reference, script, template, or writeback proposal.
5. Validate and sync active runtime skills before relying on the change.

## Codex-Only Mode

When Manuel wants Codex to be the only active AI tool for a downstream project, archive obsolete AI-tool scaffolding into a local ignored folder, update active references to point to `AGENTS.md` and CodexSkills, and record the decision in project memory. Do not keep legacy tool instructions prominent in the root unless Manuel explicitly wants compatibility maintained.

## First Prompt Pattern

Suggested first message in a new project:

```text
Use the CodexSkills new-project starter. Read AGENTS.md, PROJECT_PLAN.md, PROJECT_LOG.md, PROJECT_STATUS.md, MEETINGS.md, and SKILL_FEEDBACK_LOG.md if present. Then onboard this project, identify the workflow model, create or update the project state, and propose the first useful next step.
```
