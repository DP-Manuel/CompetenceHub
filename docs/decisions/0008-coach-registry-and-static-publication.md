# ADR 0008: Coach Registry And Static Publication

Status: accepted by Manuel's COACH-1 addendum, 23.10.2026, for architecture
and first local implementation. Server migration and production activation
are NOT approved by this decision.

## Decision

Extend the existing PostgreSQL `coaches` identity, not a parallel person store.
Keep random stable UUID, optional Portal account and explicit Calendar mapping
independent from Coach lifecycle and each environment's publication.
Normal offboarding never requires deleting a Coach or historical activity.
Reactivation keeps the UUID and requires a fresh profile revision/approval.

Version public profiles and their topic/competency/offering/asset snapshots.
Record revision-bound review/person/environment attestations and payload-free
audit. Preview and production may publish different approved revisions.
Use the existing canonical topics and many-to-many category model.

Approved DB projection -> reviewed JSON/content artifact -> static Astro build.
No public Website/PostgreSQL connection or automatic IONOS promotion. Public
asset hashes must be verified by the later build importer against actual bytes;
static withdrawal requires an approved rebuild/deployment.

## Consequences And Transition

The [Registry contract](../architecture/coach-registry-contract-v0.1.md) owns
schema, API, lifecycle, onboarding/offboarding/reactivation, evidence and tests.
Migration0007 is local only; the runtime API is unavailable by default.
Existing Coaches are not silently adopted; real UUID mappings/imports need
their own review. Current preview content remains the interim source until a
reviewed projection/importer replaces it; do not manually duplicate it in DB.
Susanne's approved Preview is not a real backend import. FIN-01 may later
reference Coach UUIDs but owns its own invoice data; CAL-2 remains separate.

Alternative rejected: continue independent static/Portal/Calendar person copies,
or make the public Website dynamically depend on the private database.
