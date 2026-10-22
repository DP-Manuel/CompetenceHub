# Competence Hub

Public Astro website plus an independent authenticated Portal/backend.

Start with [AGENTS.md](AGENTS.md), then [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), then only the task's canonical domain documents.
[Context policy](docs/architecture/PROJECT_CONTEXT_POLICY.md) explains the memory layout.

- `apps/website`: Website implementation; stable IONOS production and separately authorized GitHub Pages preview.
- `apps/webapp`: FastAPI Portal and server-side PostgreSQL foundation.
- `docs/content`, `docs/requirements`, `docs/architecture`, `docs/operations`: canonical domain memory.
- `docs/exec-plans/active`: current execution; `docs/history`: preserved history.
- `PROJECT_PLAN.md`: roadmap; `PROJECT_STATUS.md`: compatibility pointer; `PROJECT_LOG.md`: major milestones.
- `new-project-starter`: original starter reference, not current operating instructions.

Production changes, real Portal data/accounts and external service activation retain their own gates.
