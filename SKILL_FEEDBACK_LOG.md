# Skill Feedback Log

Use this file to collect possible CodexSkills improvements discovered during this project.

Do not implement every idea immediately. First collect evidence, then decide whether the change belongs in CodexSkills, ManuWiki, this project, or nowhere yet.

## Open Feedback

### 2026-06-30 | visual-ui-handoff | Require a rendered, viewable UI handoff

- Triggering project situation: The first real coach profile passed Astro check and build, but Manuel could not inspect it until it was pushed. A later screenshot then exposed a visibly unbalanced heading layout: the long title was squeezed into a narrow column while the adjacent column contained only one sentence.
- Current skill behavior: `integrate-frontend`, `check-accessibility`, and `prepare-release` mention responsive checks, screenshots, manual verification, and handoff notes, but they do not consistently require that UI work end with a rendered artifact Manuel can actually open.
- Friction or missed opportunity: technically valid frontend work can be handed off before visual hierarchy, box proportions, text wrapping, and real viewport behavior are inspected. A code/build summary alone also leaves Manuel unable to judge the result.
- Evidence: the coach profile initially passed with 0 errors, 0 warnings, and 0 hints. The layout issue became obvious only in a browser screenshot. Local Headless Edge renders at 1440 px and 500 px then guided the corrected box proportions, and the deployed pages were verified with HTTP 200 smoke tests. Manuel explicitly asked that future visual work be made available either through a local version or a pushed preview.
- Suggested improvement: for meaningful frontend layout work, require one viewable handoff path before completion: a local preview URL with clear startup instructions, a rendered screenshot/artifact, or an approved deployed preview. Add representative wide and narrow viewport renders when layout, wrapping, cards, or responsive behavior changed. Keep build/type checks as a separate gate, and document browser-emulation limitations when using a fallback such as Headless Edge.
- Reuse potential: high
- Risk if ignored: medium
- Proposed destination: CodexSkills `integrate-frontend`, `check-accessibility`, and `prepare-release` verification/handoff references
- Status: proposed

### 2026-06-22 | downstream-starter-drift | Make copied update helpers self-validating and version-aware

- Triggering project situation: After CodexSkills was updated, the project-local `new-project-starter/README.md` and `scripts/codexskills-update-check.ps1` were still older snapshots. Running the documented `-Validate` command from the downstream project reported `No skill folders found under skills`, even though all 29 canonical skills existed and validated successfully when an absolute skills path was supplied.
- Current skill behavior: the starter is intentionally copied into downstream projects, but it has no version marker or reliable stale-snapshot check. The update helper invokes repository scripts by absolute script path while those Python scripts still resolve their default `skills` directory relative to the caller's current working directory.
- Friction or missed opportunity: a healthy skill installation can appear invalid, and new safety features such as `-PlanSync`, `-BackupActive`, and `-SyncSkill` remain unavailable in older downstream copies. Agents may diagnose a nonexistent skill problem or overlook that the local helper itself is stale.
- Evidence: on 2026-06-22 the wrapper at canonical commit `6acdc18` emitted `No skill folders found under skills` when called from this website project; direct validation of `C:\Users\RödelManuel\Documents\IT\CodexSkills\skills` passed for all 29 skills, and the active runtime drift check passed when executed from the canonical repository directory.
- Suggested improvement: make repository scripts independent of the caller's working directory by resolving defaults from `__file__` or by passing absolute source paths from the PowerShell wrapper. Add a starter/version or manifest check that can report which copied downstream files are stale and offer a reviewed merge/update plan without overwriting project memory.
- Reuse potential: high
- Risk if ignored: high
- Proposed destination: CodexSkills update-check script, validator/install-check path handling, and new-project-starter update guidance
- Status: partially mitigated locally on 2026-06-22; canonical path handling and version-aware starter refresh remain proposed

### 2026-06-17 | safe-skill-sync | Add non-destructive active skill update mode

- Triggering project situation: The CodexSkills update check showed local canonical changes, but Codex intentionally avoided `-SyncActive` because it would overwrite active runtime skills and might negatively affect ongoing work.
- Current skill behavior: `codexskills-update-check.ps1 -Validate` reports repository state and drift, while `-SyncActive` can sync approved repository skills into `%USERPROFILE%\.codex\skills` with overwrite behavior. There is no intermediate safe mode for previewing, staging, diffing, backing up, or selectively updating active skills.
- Friction or missed opportunity: useful skill improvements may remain unapplied because the available sync path feels too blunt for active project work; conversely, using overwrite too casually could remove local runtime changes or introduce unreviewed behavior changes.
- Evidence: on 2026-06-17 the update check reported canonical changes across starter files, references, and skills; Codex did not run `-SyncActive` and noted that review should happen before active sync.
- Suggested improvement: add a safer active-skill update workflow, such as `-PlanSync`, `-DryRun`, `-BackupActive`, `-Selective`, or `-NoOverwrite`, that shows diffs, lists affected active skills, backs up current runtime skills, and requires explicit confirmation before replacing files.
- Reuse potential: high
- Risk if ignored: high
- Proposed destination: CodexSkills update-check script, sync script, and new-project-starter README guidance
- Status: implemented in CodexSkills commit `6acdc18`; integrated into this project on 2026-06-22

### 2026-06-17 | automatic-requirements-capture | Persist user-provided requirements without being asked

- Triggering project situation: Manuel provided important project requirements in chat: future handover to another Informatiker, non-technical colleague editing companies/coaches/job postings, and a planned coach profile subpage. Manuel explicitly noted that these ideas and specifications should be stored somewhere and that this should happen automatically through skills.
- Current skill behavior: `manage-project-state` and `write-requirements` instruct agents to update memory after meaningful work and stakeholder decisions, but live agents may still treat conversational additions as discussion unless the user explicitly asks to write them down.
- Friction or missed opportunity: valuable requirements can be lost in chat history instead of becoming restart-safe project memory, especially for multi-day projects with many open decisions.
- Evidence: this turn required adding `docs/requirements/website-maintenance-handover-and-editor-workflows.md` after Manuel reminded Codex to persist the information.
- Suggested improvement: strengthen coordination and requirements skills with a rule: when the user adds durable scope, role, workflow, operating, handover, or data requirements during a project, proactively persist them in the most specific project memory or requirements file, then update `PROJECT_LOG.md`/`PROJECT_STATUS.md` as needed.
- Reuse potential: high
- Risk if ignored: high
- Proposed destination: CodexSkills `manage-project-state`, `write-requirements`, and possibly `coordinate-software-project`
- Status: proposed

### 2026-06-17 | technology-selection | Include handover and aging cost in stack choices

- Triggering project situation: Manuel asked why Astro was selected instead of classic HTML/CSS or WordPress, and explicitly raised future handover, documentation, technical aging, and colleague maintainability as decision criteria.
- Current skill behavior: `select-technology` covers team fit, operations, maintenance, ecosystem, reversibility, and documentation, but live recommendations can still over-focus on build speed and product fit unless handover ownership is made explicit.
- Friction or missed opportunity: a technically good prototype stack can become a handover problem if future maintainers need CMS editing, patch routines, upgrade notes, and clear rollback guidance.
- Evidence: this project currently uses Astro for a static stakeholder prototype, but the future operator/editor model is still unclear and may include non-developer colleagues.
- Suggested improvement: strengthen `select-technology` guidance for websites and small internal tools: explicitly compare developer-maintained static stack, CMS-backed stack, and no-build static HTML against handover, update frequency, patch responsibility, documentation burden, and end-of-life/upgrade path.
- Reuse potential: high
- Risk if ignored: medium
- Proposed destination: CodexSkills `select-technology` reference
- Status: proposed

### 2026-06-17 | sandbox-tooling | Remember Astro telemetry AppData write failure

- Triggering project situation: `npm run build` for `apps/website` failed inside the workspace sandbox with `EPERM: operation not permitted, mkdir '...\AppData\Roaming\astro\Config'`, and later with Astro/Vite `Could not load ... spawn EPERM`; both passed unchanged after approved escalation.
- Current skill behavior: Windows frontend setup guidance already mentions telemetry/config writes outside the workspace, but project-specific restart notes did not yet preserve the exact failure signature and recovery path.
- Friction or missed opportunity: future agents may waste time debugging valid Astro code when the failure is only an environment permission issue.
- Evidence: 2026-06-17 builds passed with Astro check reporting 0 errors, 0 warnings, 0 hints after rerunning with approval; the coach-page build produced 8 static pages after escalation.
- Suggested improvement: when a build tool writes user-level config outside the workspace, record the exact error signature in project memory and suggest either approved escalation or a documented telemetry-disable path before treating it as a code failure.
- Reuse potential: medium
- Risk if ignored: low
- Proposed destination: project `AGENTS.md` plus possible CodexSkills Windows/frontend reference refinement
- Status: captured locally

### 2026-06-16 | documentation-language | Stakeholder artifacts should match team language

- Triggering project situation: Manuel clarified that the full team works in German and asked for the colleague questions plus database decision email in German after an earlier briefing still used English structure.
- Current skill behavior: documentation and requirements skills can inherit English headings or structure from repository conventions even when the stakeholder audience is German.
- Friction or missed opportunity: stakeholder-facing text needs to be directly copyable into Word, email, and internal communication without translation cleanup.
- Evidence: `docs/requirements/content-briefing-colleague-prototype.md` was rewritten as a German colleague briefing with German questions and an email draft.
- Suggested improvement: add guidance to `write-documentation` and `write-requirements`: for stakeholder briefings, questionnaires, meeting notes, email drafts, and decision memos, infer or confirm the working language; for Manuel's German teams, default to German stakeholder copy while keeping code-facing technical artifacts in the repo's established style where useful.
- Reuse potential: high
- Risk if ignored: medium
- Proposed destination: CodexSkills skill/reference
- Status: implemented on 2026-06-16 in CodexSkills

### 2026-06-16 | requirements-intake | Ask more proactive discovery questions

- Triggering project situation: Manuel provided a growing set of future-system ideas for an independent web-based administration system and then explicitly said he wants Codex to ask more questions, especially around requirements, to build a better picture.
- Current skill behavior: `write-requirements` instructs agents to establish goal, users, current state, target state, constraints, open questions, roles, data objects, and workflows, but in live work the agent can still over-index on documenting provided ideas instead of actively interviewing for missing requirements.
- Friction or missed opportunity: important context such as first app slice, exact roles, old-system pain points, workflow ownership, document types, skill taxonomy, and external user boundaries may remain implicit unless Codex asks targeted follow-up questions.
- Evidence: future-system backlog now contains many brainstormed ideas, but several open questions remain and Manuel explicitly requested more questioning behavior.
- Suggested improvement: add a stronger requirement-intake behavior to `write-requirements` and/or coordination guidance: after capturing brainstorm input, ask a small batch of high-leverage questions grouped by scope, actors, data, workflow, and priority; prefer 3-7 questions rather than a long questionnaire, and repeat as new requirements arrive.
- Reuse potential: high
- Risk if ignored: high
- Proposed destination: CodexSkills skill/reference
- Status: implemented on 2026-06-16 in CodexSkills

### 2026-06-09 | deployment-guidance | GitHub Pages Actions activation check

- Triggering project situation: The first GitHub Pages deployment workflow built the Astro artifact successfully but failed in the deploy step with `Ensure GitHub Pages has been enabled`.
- Current skill behavior: deployment planning covers environment assumptions and smoke tests, but does not explicitly remind agents that GitHub Pages must be enabled with `Source: GitHub Actions` before `actions/deploy-pages` can create a deployment.
- Friction or missed opportunity: the workflow looked broken in GitHub UI even though the code and build were correct; the fix was to set Pages source to GitHub Actions and rerun the same workflow.
- Evidence: workflow run `27227037472` failed before Pages activation, then succeeded after rerun; published site returned HTTP 200.
- Suggested improvement: add a GitHub Pages deployment checklist item: confirm repo visibility, Pages source, Actions permissions, `site`/`base`, and rerun behavior after first activation.
- Reuse potential: high
- Risk if ignored: medium
- Proposed destination: CodexSkills reference
- Status: implemented on 2026-06-16 in CodexSkills

### 2026-06-09 | implementation-tooling | Warn about Windows paths, umlauts, and local toolchains

- Triggering project situation: Astro setup in a Windows path containing `RödelManuel` required extra care; system Node.js was unavailable, MSI installation required admin privileges, and the project needed a portable Node fallback.
- Current skill behavior: implementation/frontend skills recommend inspecting stack and running verification, but do not explicitly call out Windows path encoding, umlaut paths, portable Node, npm PATH propagation to `cmd.exe`, or sandbox child-process issues as setup risks.
- Friction or missed opportunity: several install/build attempts were needed before the stable path was found: portable Node in `tools/`, absolute PATH for npm postinstall scripts, Astro telemetry disabled, and escalated build for child process spawning.
- Evidence: this project needed portable Node.js, Astro 5 pinning, telemetry env var, and elevated build execution before the preview built successfully.
- Suggested improvement: add a Windows frontend setup note to relevant implementation skills covering non-ASCII paths, adminless Node fallback, npm postinstall PATH propagation, telemetry/config writes outside workspace, and when to use an ASCII fallback path.
- Reuse potential: high
- Risk if ignored: medium
- Proposed destination: CodexSkills reference
- Status: implemented on 2026-06-16 in CodexSkills

### 2026-06-09 | delivery-handoff | End with useful next-step options

- Triggering project situation: Manuel found it useful when Codex ended a setup/discovery response by suggesting the next step or several alternative next paths.
- Current skill behavior: skills usually require summaries, verification, residual risks, and next recommended task, but they do not consistently ask for multiple next-step options with tradeoffs.
- Friction or missed opportunity: after finishing a task, the user may need to decide how to continue; a single next task can be helpful, but a small option set is often better for project steering.
- Evidence: Manuel explicitly asked to keep doing this because it has practical value.
- Suggested improvement: add a lightweight handoff pattern to relevant skills: "Recommended next step" plus "Alternative paths" when more than one sensible continuation exists.
- Reuse potential: high
- Risk if ignored: medium
- Proposed destination: CodexSkills skill
- Status: implemented on 2026-06-16 in CodexSkills

### 2026-06-09 | new-project-starter | Clarify initial folder scaffold guidance

- Triggering project situation: Manuel asked to load the starter and create all necessary folders for a website, webapp, and possible additional artifacts.
- Current skill behavior: the starter says which memory files to copy, but it does not recommend a minimal default structure for multi-artifact website/webapp projects.
- Friction or missed opportunity: the agent must infer whether to create `apps/website`, `apps/webapp`, `docs/requirements`, `docs/architecture`, and similar folders.
- Evidence: first setup turn for this project required a conservative structure decision.
- Suggested improvement: add an optional "multi-artifact web project scaffold" section or reference to the starter.
- Reuse potential: medium
- Risk if ignored: low
- Proposed destination: CodexSkills template
- Status: implemented on 2026-06-16 in CodexSkills

## Implemented Feedback

- 2026-06-22: Integrated safe skill sync planning, selective sync, and active-skill backups from CodexSkills commit `6acdc18`; added a local path-resolution fix so downstream validation works independently of the caller's working directory.
- 2026-06-16: Integrated stakeholder-language, proactive requirements intake, GitHub Pages deployment checks, Windows/frontend toolchain notes, next-step handoff options, and multi-artifact web scaffold guidance into CodexSkills.

## Rejected Or Deferred Feedback

-
