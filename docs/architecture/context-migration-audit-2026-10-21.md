# Context Migration Audit

Date: 2026-10-21. Scope: documentation architecture and Post-Messe rebaseline.

## Before / Evidence Of Exposure

Old AGENTS required repeated PLAN/STATUS/LOG updates; README repeated that rule.
The old external brief added another full-brief + STATUS/LOG boot sequence.
STATUS alone mixed current state with 732 lines of history; PLAN retained obsolete July/September priorities and duplicate gates.
There was no current checkpoint, active ExecPlan or domain index.

| Original root | Lines | Bytes | Role / frequency | Default / overlap |
| --- | ---: | ---: | --- | --- |
| AGENTS | 119 | 8,563 | Durable rules / rare | Required; duplicated root-update rules |
| STATUS | 732 | 50,072 | State + history / every block | Required; plan/log evidence overlap |
| PLAN | 1,033 | 91,509 | Roadmap + active + history / every block | Required; duplicate snapshot/gates |
| LOG | 3,536 | 249,783 | History / every block | Required by old operating loop |
| SKILL_FEEDBACK | 960 | 73,422 | Open + implemented proposals / learning | On demand; status classification needed |
| README | 21 | 999 | Project entry / rare | Entry reference; old update rules |
| CHATGPT_PROJECT_BRIEF | 660 | 22,481 | Full external-review context / frontend restart | Additional frontend read; repeats boot/history |

Classification: durable rules -> AGENTS; current state -> CONTEXT; active plan -> ExecPlan; long-term roadmap -> PLAN; history -> archive; duplicated information -> pointers.
All seven pre-edit files are byte-preserved with SHA-256 in the [manifest](../history/context-migration-2026-10-21/manifest.json).
Archive-local Git attributes disable line-ending conversion so later Windows/Linux checkouts preserve these byte hashes.
Archive-only whitespace checking is disabled for these immutable originals;
otherwise Git reports preserved CRLF as new trailing whitespace. Active files
retain normal diff checks; no original snapshot was reformatted.
The old AGENTS bytes are named AGENTS.snapshot.md in the archive to prevent a nested instruction file from becoming active; the manifest records original and archived names.

## Default Loading Comparison

Conservative old baseline: AGENTS + STATUS + PLAN + LOG = 4 files, 5,420 lines, 399,927 bytes.
New mandatory boot: AGENTS + PROJECT_CONTEXT = 2 small files; validation reports exact current bytes/lines.
At validated rebaseline: 115 lines / 8,192 bytes, approximately 98.0% fewer mandatory bytes; the helper reports final live metrics after further checkpoint updates.
Final published-preview checkpoint: 113 lines / 8,511 bytes, 97.9% fewer mandatory bytes; seven archive files, 21 routed documents and 113 local links validated.
The optional old external brief and skill feedback are excluded from that baseline; actual task-specific reads add only relevant domain files.
This measures mandatory exposure, not token counts, runtime latency or deleted storage.

## Roles / Preservation / Compatibility

AGENTS routes permanent rules. CONTEXT owns the snapshot. STATUS is a thin compatibility file.
PLAN is roadmap; ExecPlan owns execution/horizon. LOG records major milestones and points to full history.
The history index routes untouched snapshots; existing domain/ADR/runbook paths remain valid.
Architecture/requirements/operations/content indexes are small navigation tables, not duplicate specifications.
The activation-input contract now follows the new update policy; the old external brief no longer requires full LOG/STATUS reads.
Tracked search found no CI/test/release-helper dependency on root document contents; the database README still names LOG, which remains present.
Historic evidence-index references to root LOG remain reconstructible through its archive pointer.
No global skills were edited. Unrelated .vscode and the untracked weekly update are preserved.

## Progressive Disclosure Checks

| Task | Small relevant read set after boot | Excluded by default |
| --- | --- | --- |
| Website Messefeedback | content/index; supplied source; impacted Astro component; environment policy for publication | Calendar/API/backup history |
| Continue CAL-1 | requirements/index; CAL-1 browser handoff; affected API/UI contract and tests | Finance, old website releases, full root history |
| Plan FIN-01 | requirements/index; FIN-01 epic; authorized bookkeeping input | CAL-1 code, deployment history, private source search |

Cold start must identify identity, live static Website checkpoint, active Post-Messe work, protected production/data boundaries, domain routes and next action from AGENTS + CONTEXT alone.
Validation: seven archive hashes, 17 router files, 97 local links and git diff --check PASS at rebaseline; new links are included in later helper runs.
An independent fresh agent read exactly AGENTS + CONTEXT and correctly identified all seven cold-start facts, the dated versus fresh production-evidence distinction and the stop boundary: PASS.

## Critical Retrospective

- Context exposure is reduced by changing the read/update contract, not merely renaming large files.
- Full LOG/PLAN/STATUS are no longer routine prerequisites.
- Deep knowledge is reconstructible from hash-verified full originals, unchanged canonical documents and Git.
- Each information type has one primary home; indexes/compatibility roots link to it.
- The production checkpoint is clear; historic test evidence is not misreported as an October retest.
- Messe/holiday gates live only as dated history; stable production remains separately gated.
- Supplied feedback is distinguished from accepted requirements and pending additional source access.
- No new service, database, framework or retrieval infrastructure was introduced; one local integrity helper checks docs.
