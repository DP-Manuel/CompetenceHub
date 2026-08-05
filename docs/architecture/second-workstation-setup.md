# Second Workstation Setup

Last verified: 2026-08-05

This note records environment-specific behavior for the network-separated second
Windows workstation. It contains no credentials or token values.

## Paths And Repositories

- Website workspace: `Z:\IT Development Manuel\Firmendingsbums\Website`
- Canonical CodexSkills clone: `Z:\IT Development Manuel\CodexSkills`
- Website remote: `https://github.com/DP-Manuel/CompetenceHub.git`
- GitHub CLI: `C:\Program Files\GitHub CLI\gh.exe` (verified as version 2.97.0)
- Git safe-directory entries are configured for both network-share repositories
  because the server-side owner SID differs from the local Windows user.
- Git author identity is configured repository-locally and matches the existing
  project history. Recheck with `git config --local --list` rather than storing
  identity or authentication material in this note.

## Node And Astro

- System Node is v20.17.0.
- The project-local runtime is Node v22.16.0 at
  `tools\node-v22.16.0-win-x64` and remains the preferred build runtime.
- PowerShell execution policy can block `npm.ps1`; call `npm.cmd` explicitly.
- Before project npm commands in `apps\website`, prepend the project Node folder
  to `PATH` and set `ASTRO_TELEMETRY_DISABLED=1` when appropriate.
- Direct Astro dev/build processes on `Z:` can hang after startup or type
  generation even when the code is valid. A secret-free local copy under
  `C:\tmp` has built and served the same source successfully.
- When creating a local copy, exclude `.env`, `.env.*`, `.tmp`, build caches and
  unrelated private material. Copy `node_modules` separately: a broad Robocopy
  exclusion named `.astro` can also omit `node_modules\astro` unexpectedly.

## Local Preview

- The verified preview URL is `http://127.0.0.1:4321/`.
- On 2026-08-05 the current source was served successfully from a secret-free
  `C:\tmp` mirror by invoking its local `node_modules\astro\astro.js` directly
  with system Node. HTTP returned 200 and current Mindforge content.
- The preview process and its `C:\tmp` mirror are disposable workstation state;
  the repository remains the source of truth. Restart the preview after source
  changes because the mirror does not synchronize automatically.
- The in-app browser connection has timed out repeatedly on this workstation.
  After the required connection attempt, open the verified local URL in the
  visible default browser and record that automated visual/keyboard QA remains
  incomplete.

## Tooling And Safety Observations

- Sandboxed shell operations against `Z:` can hang while the same scoped command
  succeeds with approved execution outside that restriction.
- The patch-edit tool has repeatedly hung on both `Z:` and `C:\tmp` on this
  workstation. If that recurs, use a narrowly scoped, precondition-checked edit,
  then inspect the complete Git diff before accepting it.
- Keep the repository-local `.tmp/` directory untracked and do not inspect it.
- Never copy or open `.env*`, credentials, tokens or unrelated private source
  material while preparing a local build mirror.

## Restart Checks

1. Run `git status --short --branch`, `git fetch --prune origin`, and compare
   `HEAD...origin/main` before editing so parallel work is preserved.
2. Confirm GitHub access with `gh auth status` without printing token values.
3. Prefer the project Node runtime and `npm.cmd`; treat known network-drive hangs
   as environment failures until the same source is tested locally.
4. Keep local-preview availability separate from browser-based visual approval.
