# Webapp

Reserved workspace for the later Competence Hub administration application.

## Status

The backend stack is not selected yet. Keep webapp decisions separate from the
public Astro website. The website must never connect directly to the database.

## Local Configuration

- `.env.example` contains placeholders only and may be committed.
- Copy it to `.env` only when a backend implementation starts.
- `.env` is ignored by Git and must contain no shared or production credentials.
- Do not store SSH passwords in `.env`; use an SSH key/agent or an interactive
  password prompt.

See `docs/architecture/server-database-bootstrap.md` and
`docs/architecture/initial-data-model.md` before server or database changes.
