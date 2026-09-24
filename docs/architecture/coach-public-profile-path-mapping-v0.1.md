# Coach Public Profile Path Mapping v0.1

Stand: 24.09.2026

Status: local contract; no real Coach UUID has been mapped.

## Canonical Boundary

`competence_hub.coaches.public_profile_path` is the only supported link from an
internal Coach UUID to an approved public website profile. It is nullable,
unique when set and limited to canonical `/coaches/<slug>/` paths. Calendar
operations cannot set or change it. No path is derived from a display name and
there is no fallback slug.

## Existing Approved Website Routes

Only these real-person routes are approved as potential mapping targets:

- `/coaches/christian-galvano/`
- `/coaches/manuela-rodriguez/`

The Website also contains `/coaches/demoprofil-01/` through
`/coaches/demoprofil-06/`. Those routes are fictional UI examples and must
never be assigned to a real Coach UUID. Former personal routes removed by the
24.09 publication correction are invalid mapping targets and intentionally
return 404.

The website source does not contain stable internal Coach UUIDs. Therefore this
document records valid mapping targets only; it does not create UUIDs, assign
paths to database rows or authorize real-person data.
