# Skill Feedback Router

Updated: 2026-11-13. This file is on-demand, not part of routine boot context.

## Active / Open Proposals

[Full prior feedback](docs/history/context-migration-2026-10-21/SKILL_FEEDBACK_LOG.md) retains every proposal and its recorded status.
Project-local implementation does not mean a canonical CodexSkills proposal is closed.

13.11 V1.1 learning: derive form requirements from contracts, never guess a
missing optional summary as root cause. Translate only allowlisted field/error
codes; deny non-owner mutations before exposing diagnostics. Preserve legacy
minutes/seconds and DST instants when adding convenient quarter-hour controls.
Keep a fixed human-facing test guide, with actual identifiers only in private
ACL-controlled operator output and no plaintext credential export. Native browser
tests must await the new dialog's identity before checking reused radio controls;
an already checked hidden old radio can make Playwright check() return early.
Read textarea.value, not textContent; await submit completion before reviewer
refresh. A copied zoom session rotates CSRF, so resume the original before logout.
Force delayed startup responses across logout and assert no JS error/private DOM
return. Capture viewport (not full-page) screenshots for scrollable modal focus.
Project fixes and evidence captured; no global skill or ManuWiki change.

13.11 operator-browser learning: a generic TimeoutError after credential loading
is not sufficient evidence to retry logins or claim a root cause. Emit fixed safe
role/step diagnostics, never raw Playwright exceptions/traces containing form
values. Static form visibility is not initialization readiness: finish the first
session response and its UI transition before submitting login. Reproduce delayed
initial401 against the unchanged packaged UI; test rejected password/MFA and rate
limits with one-shot synthetic requests. Distinguish the proven race from the
unlocated old operator failure; no blind real-authentication loops. Project-local
fix, global skill proposal remains open. Derive success statuses from the actual
API contract (password202, MFA204), not a generic200 mock; the native PostgreSQL
probe caught that test-fixture assumption before operator delivery.

11.11 usable-access learning: technical pilot acceptance plus encrypted login
files is not a manual test handoff. Provide a standalone reconnect/test-window
entry before asking a human to test; no installer rerun or decryption instructions
as a substitute. Use existing credentials privately through native login/MFA,
not fixed guessed accounts, password export or re-seeding. Map actual session
UUIDs/roles to windows, never browser-context iteration order (native Firefox
proved it is not creation order). Explain one-terminal sequencing and exit, bind
certificate/runtime and distinguish auth/session changes from business writes.
Provide all commands/roles/access addresses again when Manuel defers his test.
Project implementation/evidence captured; global skill proposal remains open.

11.11 successful-operator handoff learning: a completed deployment that retains
a private tunnel must not look like a hang. Native Python input prompts without
newlines are buffered by PowerShell Out-Host. Emit a complete flushed status line
before reading stdin; prove visibility before input with an actually blocked,
piped child, not only captured final output. Explain Enter as local-access close,
never suggest rerunning installation to end the wait. Independently verify the
actual receipt/runtime/TLS/services and close old WAITING gates in memory before
moving on. Project fix tested; no global skill change.

11.11 real postflight learning: read the actual receipt before interpreting an
early-sounding error name. Here61/33 remote checks and exact current restore had
passed; Type=simple process-active did not mean its TCP listener was bound.
Await bounded real readiness after own start and after rollback, not a fixed
sleep. Do not replay an installer against a retained release or repeat accepted
native evidence/backup by default. A narrow resume must pin the actual receipt,
revalidate ciphertext/config/package/reference rows, preserve shared security
counters, prove no new DB writes and distinguish reused from fresh evidence.
Native local rollback/resume and117 focused regressions implemented; canonical
skills unchanged. Privileged actual reconciliation remains an operator gate.

11.11 private-operator timeout learning: a broad local_preflight phase is not
enough to diagnose failed SSH/sudo checks. Record the exact fixed phase before
each boundary, close stdin for probes that must never consume operator input,
and preserve the later private password/bootstrap pipe separately. A failed SSH
transport is not evidence that a password is needed. Do not log raw timeout
exceptions/commands or claim a transient network cause from a successful later
probe. Test both timeout locations and both valid private-channel paths with
synthetic input. Project fix implemented; global skill proposal remains open.

11.11 existing-pilot update learning: never reuse an empty-target installer to
update a deliberately retained synthetic reference. Use a separate owned cohort,
fresh current-state recovery and exact original-row comparison; retain shared IP
security counters and never rewind sequences. Derive cleanup hashes from the
actual service bucket namespace, not its public action name (invitation_issue
versus invitation). Prove cleanup and old-runtime recovery in native PostgreSQL.
Do not consider postflight committed until final strict HTTPS/runtime/delivery
checks acknowledge acceptance. Preserve partial-write ownership for compensation.
Test the real PowerShell child forwarding and UTF-8 path, not just script text;
dot-sourced parameter blocks can silently replace the caller's values. Original
systemd quoted environment values require structured parsing, never shell eval.
For native Firefox200 pointer drift, test actual text hit regions and keyboard
activation without force-clicks; do not hide a possible visual defect with sleeps.
Project-local regressions only; no global skill or Wiki change.

10.11 user-readiness learning: first-onboarding auto tours change existing browser
harness contracts. Await the actually displayed tour/step before skipping or
reloading; a momentary is_visible check races asynchronous workspace loads.
For concurrent stale-edit tests capture the existing synthetic CSRF in memory,
do not rotate it and accidentally test CSRF failure instead of a version conflict.
Reuse the existing CDP native200 screenshot helper; CSS-sized Playwright captures
can be clipped/blank even when DOM geometry passes. Actual Tab/Shift+Tab uncovered
a management-dialog focus escape, fixed with bounded visible-control wrapping.
Repeated native zoom navigation also exposed out-of-order account reads appending
duplicate rows. Bind each bounded list/overview response to its current load
generation as well as the session; prove with deliberately reordered responses,
not an arbitrary sleep or a selector workaround.
Finally, an accepted pre-pilot empty restore is not a current copy of deliberately
retained pilot data. Distinguish source/package rollback from data recovery and
do not restart backup/password workflows simply to close a delivery checkbox.
Project-local implementation/tests; no global skill or Wiki change.

10.11 deployment closure learning: accept a real operator result only after
reviewing its actual sanitized receipt, exact source/package and configuration
ciphertext hash, then independently read service/enable/listener state and probe
strict HTTPS with exact served certificate match. Close installation in context,
roadmap, active plan and handoff together; don't leave next-install suggestions
that invite an unsafe rerun. Distinguish deliberately retained synthetic pilot
data from disposable-test zero residue; record tunnel lifetime/certificate expiry
and keep real-user/import/public gates separate. Implemented project-locally;
no global skills/Wiki change, no new backup/operator loop.

09.11 real-entry regression: a green native container probe bypassed the outer
accepted-receipt loader. The actual immutable legacy receipt lacked a later
baseline hash field, causing a local KeyError before authentication. Cover the
entire boundary with the actual historical schema and separately accepted hashes;
never rewrite the receipt or weaken verification to hide compatibility errors.
Also test UTF-8 native output under inherited OEM850, restoring console encoding
on success/failure.13 added cases/112 focused PASS; no new real operation.
Project-local learning; no global skill changes.

09.11 pilot execution learning: accepted backup/restore receipts must be reused,
not reopened because a separate sudo input is needed. Provide one actual
install+acceptance command, not successive preparation windows. Explicitly
distinguish local process-shim/systemd syntax proof from real remote acceptance.
Guard committed EOF from rollback, acknowledge scoped cleanup, independently
attempt own service stops and never clean data while own processes may still
write. Probe inherited umask0077: runtime/venv needs deliberate public-read modes,
configuration stays private. Month-overlap tests must select the intended month,
not stop at its previous month's first segment. Separate authenticated sessions
for stale-edit tests: a second tab renews shared-session CSRF and is a different
failure. Native zoom screenshots must show loaded events, not a loading state.
Implemented/tested project-locally; no global skill or Wiki change.

09.11 actual-operator learning: never accept a console PASS alone. Verify the
actual sanitized receipt, bound source/run and exact current ciphertext hashes/
ACLs, then CLOSE that gate without another password/backup loop. PowerShell
exit(function) captures native success-stream output: progress/REPORT disappeared
although Write-Host PASS stayed visible. Reproduced and fixed with Out-Host plus
preserved native exit checking; regression covers success/failure and mismatched
receipt/hash/run/cleanup booleans. Prior valid legacy receipt remains untouched,
explicitly accepted through independent verification, not silently rewritten.
Implemented project-locally; no global skill change.

09.11 backup continuation learning: keep one private authentication across dump
and restore, never recover a password from a previous terminal. Bind native dump
and reference hashes to one exported MVCC snapshot; identity sequences are not
MVCC data and require quiet-source plus before/after state verification. Restore
probe must deny app/migrator CONNECT even through inherited owner membership:
use postgres ownership, no connections initially, revoke before opening and
recheck after restore. Use existing private CreateNew ACL primitives with explicit
operator ownership under elevation. Retain exact ciphertext and bound receipts,
never treat a temporary same-machine DPAPI copy as independent disaster recovery.
Locally implemented/tested; real operator outcome still pending, global proposal open.

09.11 operating-window learning: distinguish owner authorization from missing
local elevation/sudo authentication; don't ask for the same decision again.
One read-only preflight must use the native Windows BitLocker host, never touch
protectors or retry passwords, and report NOT_RUN for backup/restore/install.
Pair PostgreSQL listen settings with actual sockets and indirect role membership.
Do not hard-code table totals from an older package: current source includes
0009, reviewed package ends at 0008; test both without promoting a migration.
Observed and tested locally; no global skill modification or new GPG workflow.

09.11 follow-up learning: a protected SSH path still needs independently checked
TLS certificate AND hostname; test foreign certificate/host/SSH key negatives.
Close a restore proof from the ciphertext actually reread from disk, not the
original RAM dump. Distinguish synthetic cryptographic proof from real storage
qualification and portable recovery. Windows identity may be Entra S-1-12,
not only S-1-5; don't reject a real current user through an invented SID family
assumption. Schema comparison must canonicalize catalog collections; trigger
names alone aren't unique across tables, and ACL array order isn't permission
meaning. Keep full identities/definitions/enabled state and effective grants.
Observed, regression-tested locally; global skill changes remain a separate
CodexSkills proposal. No new real password interaction or GPG process.

09.11 integrated-pilot learning: distinguish source implementation, actual
packaged public UI, private database acceptance and deployed Staging. Test the
packaged Calendar endpoint, not only a demo wrapper. Reuse renderer assets in
the wheel and allowlist .mjs with explicit MIME. Before lifecycle assertions,
read the canonical generic error contract (invalid activation400; pure-role
access to an internal-only session endpoint may401 rather than403). Optional
tours must restore focus to a visible trigger, handle absent targets, and test
closed details content and long mobile display names. PostgreSQL image readiness
must await final TCP startup, not the temporary Unix-only initialization server.
Keep failure cleanup in finally so it cannot hide the original assertion.
Capture external sudo/DNS/restore gates once early; finish independent local
work and request one operating decision. Local proposal only; no global skills
or Wiki edits. [Evidence](docs/operations/integrated-staging-pilot-2026-11-09.md).

06.11 native pilot learning: prove persistence with a fresh application AND
database restart on an explicitly owned test volume, then verify container/volume
absence through a successful daemon listing, not any failed inspect. Wait for
actual loaded list state before filter assertions; close owned browser contexts
before server teardown so cleanup cannot hide the original assertion. ICS UID/
SEQUENCE must follow the published revision, not private edits. RFC5545 TZID
cannot encode the second occurrence of an ambiguous autumn hour: preserve those
instants in UTC and regression-test the exact hour. [Evidence and scoped gates](docs/handoffs/2026-11-06-cal1-pilot-readiness.md).
Captured locally; no global skill change or canonical proposal closure.

06.11 integration learning: a renderer regression cannot prove retrieval of
already-running events; test the actual bounded month HTTP query separately.
Reuse the existing public DTO, not protected summaries. Auto-refresh must not
temporarily hide a retained detail panel (doing so drops keyboard focus to body),
reset input or erase last-approved revision semantics. Test pre-opened public
view publication and withdrawal without reload. Isolate local entry/source/output
from normal public builds and inspect both emitted artifacts, not just routes.
Native-zoom screenshots also need pixel/content verification: a manually supplied
CDP clip can capture blank space after scrolling despite valid DOM geometry.
Capture the native viewport without that clip and inspect the actual bitmap.
[Evidence](docs/handoffs/2026-11-05-cal1-demo-readiness.md#gemeinsame-lokale-kalenderdemo-06112026).
Captured project-locally; no global skill edit or new canonical proposal closure.

06.11 Calendar learning: render occupied civil days for [start,end), not only
start date or fixed24-hour increments. Test exact midnight, DST/repeated hours,
week/month/year clipping and concurrent lane geometry; count events, not segments.
Keep original record identity/detail action and API contracts separate from view
layout; explicitly record retrieval-window limits rather than silently widening
access. Test browser asset MIME on Windows: a200 response is not sufficient for
an ES module. Await a real initialization signal before accepting initially
hidden loading/error elements. [Evidence](docs/handoffs/2026-11-05-cal1-demo-readiness.md#mehrtägige-veranstaltungen-06112026).
Project-local implementation, global skill proposal still open.

05.11 COACH-5/CAL-demo learning: derive finder entries only from explicitly
approved offering lists, not qualifications; group family/formats/options and
match every dimension on the SAME format. Do not relabel missing metadata or
infer private-client offers. A runtime HTML conditional alone can still emit an
unused client bundle: verify every Production file, use existing build-alias
boundaries. Browser reset must assert values AND results, not only visual controls.
Distinguish static calendar examples, real local API/domain transitions and
synthetic auth/persistence; never call a replacement view existing-view reuse.
Keep six-step human demo and actual backend activation separate. On QA teardown
failure retain incomplete status; phase/engine/cleanup evidence matters, do not
start another application/password loop. [Evidence](docs/exec-plans/active/coach5-offering-finder-2026-11-05.md).
Project-local learning, no global skill edits.

05.11 Website-first learning: do not let a paused DB/key operating gate block
independent static Website value. Inventory known source/history/build/archive
locations once, deduplicate by content, distinguish technical reconstruction from
currently lawful/working rollback. Verify the actual current return artifact;
do not count copied folders as independent versions. Prove Preview isolation by
all-file Production hashes, not only environment labels. Manual Pages dispatch
requires scoped publication intent; a push alone is not deployment. Approved
short copy is usable without forcing an unfinished Registry migration. Search
only approved active offerings, and test real text rectangles/keyboard/no-JS.
[Project evidence](docs/content/website-first-2026-11-05.md). Local learning captured;
global skills unchanged, reusable proposal remains open.

05.11 crypto-custody acceptance learning: generation success, a written note,
matching fingerprint or a warm-agent roundtrip is NOT independent recovery.
Couple generation with cold protected export, exact external-copy import and
cold recovered decrypt of a NON-secret challenge BEFORE encrypting business or
application material. Prove both cold states and real native Ask transport;
distinguish a protocol double from Qt/physical keyboard evidence. On failure,
preserve partial identity, stop rather than request more operator guesses, and
use dependency evidence to choose repair vs separately approved replacement.
Observe bounded machine error classes, never raw secret diagnostics. Explain
necessary independent prompts upfront. [Evidence](docs/operations/gpg-root-cause-recovery-decision-2026-11-05.md).
Project-local preparation only; canonical skill proposal open, no global edits.

04.11 custody/partial-key lesson: never assume a password manager exists or ask
an operator to attest to a false storage method. Accept explicitly approved
protected written offline custody, kept separately from recovery media; record
non-secret method, not values/precise storage location. Preserve a generated key
across interrupted export: pin full identity and forbid replacement on resume.
Explicit method/valid prior record replaces unnecessary confirmation; correct
historical manager-only metadata append-only, never rewrite it. Paper passphrase
custody is NOT a second independent private-key recovery copy or crypto proof.
[Local contract](docs/operations/controlled-backup-key-rebase-2026-11-04.md#protected-offline-custody-and-existing-key-resume).
Global skill proposal remains open; project-local implementation only.

04.11 elevated-runtime regression: non-elevated success does not cover Windows
elevated default file ownership. Create private files atomically with explicit
user owner/security descriptor; never broadly relax owner checks to hide it.
Test default/elevated metadata, token context, no-overwrite and read-only recovery
of partial NON-secret state. Record substep/known bounded error before asking an
operator to retry; a new error code is not the same failure. Verify actual
metadata instead of repeating administrator/password advice. Existing source
keys/ACLs untouched; [local evidence](docs/operations/controlled-backup-key-rebase-2026-11-04.md#elevated-owner-fix).
Global skill proposal remains open, no global edits.

Latest04.11 operator learning: keep an approved key block separate from an
unconfigured future destination. Report unavailable volume metadata honestly,
not as unencrypted/encrypted; do not infer approval from capacity or a mapped
drive letter. A destination plan/evidence adapter is not runtime acceptance.
Protect actual artifacts outside Git and deny accidental copies. Preserve CLI
intent across dot-sourced PowerShell parameter blocks; avoid automatic HOME
variable collisions; use native GPG byte/status/packet tests alongside stubs.
One necessary manager-custody confirmation, no old-password loop, cryptographic
proof reuse on copy resume and explicit OPEN second recovery prevent repeated
operator work. [Evidence](docs/operations/controlled-backup-key-rebase-2026-11-04.md#approved-local-runner-handover).
Project changes only; no global skill modification or real operation claim.

Latest04.11 proposal: distinguish cryptographic layers before recovery advice:
BitLocker, Windows DPAPI application keys, OpenPGP private identity and portable
application-key ciphertext are not interchangeable. Record explicit GPG homedir,
sole technical custodian and actual independent recovery proof; never infer secret
custody from a business/contact role. Lost backup passphrase can justify a gated
new backup identity without rotating accessible app keys. Test real disposable
GPG export/import (not only fake roundtrips), pipeline output shape and cleanup;
Task completion objects must not leak into a bounded status return. Pin new
recipient at every downstream boundary and separately verify encrypted target
and plaintext workspace, not free space only. [Local evidence](docs/operations/controlled-backup-key-rebase-2026-11-04.md).
No global skill modification; proposed for canonical review after real operation.

Later04.11 open proposal: normalize non-secret human confirmation tokens with
Trim + ordinal case-insensitive equality, never passwords/cryptographic material.
Invalid/cancel must explain expected input without echoing submitted content or
automatic retry. Split a small key gate from the multi-stage admin window; old
entry paths must not retain hidden continuation. Reuse a valid hash-bound proof
after copy failure instead of repeating GPG prompts. Compare keycopy metadata
against device space separately from database volume/backup destination readiness.
18 new local cases plus synthetic full-flow proof; [evidence](docs/operations/local-staging-keys-2026-11-04.md).
Global proposal open; no global skill edit or actual operator execution.

04.11 open proposal: availability, consent and completed evidence are different
states. On stick return, inspect presence/ACL only, resume existing custody and
collect separate concrete runtime approvals before real backup/Admin writes.
One consolidated protected terminal entry avoids repeated password/command loops;
retain phase-only diagnostics and never regenerate partial keys. Native snapshot
tests must commit new child rows AFTER an earlier parent SELECT, not merely
update a row already read (which READ COMMITTED could also pass). Follow real
DDL-required fields in fixtures and prove exact cleanup after failed attempts.
Project evidence: [04.11 report](docs/operations/staging-resume-2026-11-04.md).
Global skill proposal remains open; no canonical/global changes made.

03.11 open proposal: read-only export needs both a narrow fixed-read capability
and transaction enforcement; paginated reads are not a consistent snapshot.
Reuse one domain hydrator and publication filter. Preserve full subject/evidence
only in the canonical memory snapshot; a redacted administrative artifact cannot
be rehashed into permission. Separate synthetic SQL-double proof from native DB
isolation, and reject real/tunnel targets before opening the local test seam.
When public bytes match the previous commit, verify actual consumer compatibility
and avoid repeating unchanged browser suites.91 new local cases plus prior-byte/
Astro checks demonstrate this; [evidence](docs/architecture/coach-read-only-export-contract-v0.1.md).
No global skill or ManuWiki write; native disposable-DB proof is the next gate.

| Proposal | Recorded state | Evidence home |
| --- | --- | --- |
| Actual text-line geometry, not only container bounds | Project regression implemented; global proposal open.23.10 additionally distinguishes unclipped glyphs from visible-overflow line boxes, and calibrates native zoom screenshots against physical CDP/PNG width | Archive: browser-visual-geometry; Susanne Preview QA |
| Clipboard passwords / two-terminal SFTP / ASCII paths | Project workflow implemented; global proposal open | Archive: sftp-one-terminal-ascii-path |
| Calendar-relative fixture acceptance | Project test corrected; global proposal open | Archive: browser-acceptance |
| Further proposed improvements | Review individual Status fields before promoting | Archive: Open Feedback |
| Current checkpoint versus full history | Proven root-context duplication; project migration implemented, reusable skill proposal open | Context policy and migration audit |
| Hash-preserved instruction archives | Use non-active snapshot filenames for old AGENTS and disable Git newline conversion; reusable proposal open | Context migration manifest and archive attributes |
| Batch authenticated operator windows | Prepare/rehearse locally, then one hidden-credential entry, native tests, cleanup, independent SQL/health before closing only owned tunnel; project runner implemented, global proposal open | 22.10 CAL-1 access/batch report and staging batch script |
| Authentication evidence versus fixtures | Follow actual Login/MFA/session admission, not only endpoint RBAC or fake browser success; project admission and real-PG harness implemented, global proposal open | CAL1-NATIVE-AUTH-01 and 22.10 access supplement |
| DB-clock authority in native browser tests | Sample actual DB clock; do not alter server time.23.10 public query at exact sampled now intermittently became past: use one sample and a valid future window, with101ms/30s regression. Global proposal open | 22.10 local rehearsal; native fixture public_query_window and regression |
| Semantic browser readiness | Native latency exposed network-idle/early-state assumptions; await real response and rendered state, not fixed sleeps; project assertions retained, global proposal open | CAL-1 shared browser helpers and native harness |
| Existing SSH capability before new setup | Two existing-key connections worked although agent disabled; do not create keys/change services unnecessarily; global proposal open | 22.10 access/batch report |
| Safe failure diagnostics and repair window | Type-only error lost exact assertion location; retain file/function/line without exception/locals. After verified clean failure, allow deliberate same-window R/Q retry rather than new credential round; project implementation, global proposal open | First 22.10 native attempt and repaired batch |
| Close the actual gate, not a larger deployment claim | 142 browser checks against VPS persistence plus API/cleanup PASS closes native runtime/UI, not Linux/systemd/public proxy/SMTP or real-data readiness. Follow-on readiness package records the difference; global proposal open | Verified 22.10 native reports and CAL-1 readiness package |
| Committed package allowlist and pre-install advisory gate | Project exporter/guard implemented.23.10 closure adds usage audit -> isolated patched-major trial -> crypto/full/native-local regression -> deterministic rebuild -> actual local proxy gate; never bypass guard or equate local evidence with VPS activation. Global proposal open | Backend assessment and23.10 security close-out |
| Coach source approval, publication and lifecycle are separate | Reusable candidate: concrete-source access -> privacy/issuer-attribution audit -> revision/environment approval -> preview -> independent production gate; stable UUID, no account/Calendar auto-grants, fresh reactivation approval. Global skills unchanged | ADR0008, Registry contract and Susanne source/QA report |
| Multi-tab auth, version conflicts and lost responses | COACH-2 native proof: another tab rotates CSRF; refresh once before writing but retain original optimistic version, never blind-retry mutations. Creation retains request identity across lost response. Include real Login/MFA and negative admission, not fake-session403 alone. Global proposal open | COACH-2 UI contract and native browser runner |
| Bounded views must retain authoritative action inputs | History pagination must not hide older still-valid activation evidence; bounded loader includes latest eligible revision plus selected/publication references. Browser readiness awaits rendered lists, not network idle. Capture scrolled fixed-element/zoom artifacts before diagnosing layout. Global proposal open | COACH-2 bounded-read and13-revision regression |
| Prove import no-op, do not only count entities | Compare all domain/ledger/audit rows and xmin; separate logical source IDs from revision snapshot rows. Inject cancellation/SQL failure after writes; preserve unknown historic dates and stop typed mapping gaps. Project implemented, global proposal open | [Import contract](docs/architecture/coach-import-contract-v0.1.md), [COACH-3 evidence](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md#coach-3a-nachweis) |
| Real source shape versus executable target |29.10 proof: green preparation may correctly mean NO_GO_APPLY. Separate source readability/access/copy rights/subject evidence/model readiness; request replacements early, preserve day-only dates and do not infer qualifications from handwritten service ideas. Global proposal open | [COACH-3 matrix/runbook](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md) |
| Additive models need field-presence and hash compatibility |29.10 COACH-3C: protect recursively populated nested fields, distinguish omission from explicit null/empty, preserve field presence through import normalization, retain v1 hash shape and prove old row/xmin identity through real DDL. New evidence is exact object/hash/environment consent, not a timestamp fabricated by import. Project regressions implemented; global proposal open | [Target contract](docs/architecture/coach-registry-contract-v0.1.md#coach-3c-additive-target-contract) and target/import tests |
| Nested disclosures need direct-child focus tests | Native add-family test found descendant last-of-type selecting an old nested variant. Select the new direct child and assert open state plus first editable focus; include long hostile literal text in390px/actual200% geometry. Add safe file/function/line diagnostics, not only exception type. Project fixed; global proposal open | COACH-3C native runner and Coach management UI |
| Optional unknowns are not repeated business decisions | COACH-3B closure: distinguish documented rights, source completeness, original date precision and future runtime DB binding. Apply existing decisions before asking; optional unknowns/Production exclusions need not block Preview. Bind actual input payloads, not a claimed hash field; reject orphaned reviewed subjects. Business READY never implies an implemented real runner or deployment approval. Project checks implemented; global proposal open | [Review closure](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md#coach-3b-reviewabschluss-2910) |
| Empty targets need an audit-actor preflight before execution promises |30.10: revision/evidence FKs require an existing active Admin, while the approved import forbids creating accounts/roles. Surface this technical dependency before a password window; do not invent a principal or silently provision one. Check taxonomy bootstrap scope, same-day backup collisions and exact-copy restore/cleanup too. Local guards added; global proposal open | [Real-import STOP](docs/architecture/coach3-existing-content-migration-plan-2026-10-23.md#coach-3b-real-apply-vorbereitung-3010) |
| Real human bootstrap needs durable custody and outcome receipts |30.10: prepare persistent versioned keys, protected pending receipt and current exact-copy restore before enrollment/write; recheck after unbounded password prompts and enforce empty scope/deadline inside the DB transaction. Preserve uncertain commits, never blind retry. Human instructions must remain visible when a key loader suppresses stdout. Project implemented/tested locally; actual human window pending, global proposal open | [Admin operator preparation](docs/operations/staging-admin-bootstrap-2026-10-30.md) |
| Actual subprocess/restore evidence beyond static script checks |30.10: real isolated PostgreSQL restore found unset LASTEXITCODE and temporary initdb readiness races; use explicit owned child exit codes and final-server readiness. Include SystemDrive in sanitized Windows child environments; synthetic GPG or positive table counts must never be reported as actual encryption/restore readiness. Project regression added; global proposal open | Restore supervisor, owned PG/Edge harness and operator contracts |
| Detailed sources must not silently replace approved short scope |30.10: preserve prior17 offerings and bind a private additive source annex; distinguish concept/format/package references, optional intra-source conflicts and genuinely unsupported typed fields. New processing permission is not publication consent; no forced schema expansion or invented exact durations. Project evaluator/reconciliation implemented; global proposal open | [Elisabeth source reconciliation](docs/architecture/elisabeth-source-reconciliation-2026-10-30.md) |

New open proposal02.11: after interrupted pinentry, distinguish metadata-only
partial custody from verified configuration before prompting or contacting a
server. Preserve existing keys, report a fixed safe reason and never equate
"retry" with regeneration. Recheck workstation-bound prerequisites and honor
manual backup deferral without bypassing dependent first-write gates. Project
diagnostic regression added; canonical/global skill change remains open.
Later02.11: explicit existing-custody completion prepared with synthetic proof;
one shared payload validator, exact memory comparison and no-overwrite metadata
publication. No automatic key regeneration or real secret execution. Full local
suite1097/29 opt-in skips and bounded independent review; global proposal open.

COACH-4 learning02.11 (open global proposal): use held real-operation windows to
finish independently gated local pipelines, not bypass custody. Separate public
visibility diff from private stable-identity/approval readiness; never infer an
identity/consent event from a removed/added route. Prove deterministic public
bytes, exact assets and frozen-review simulation separately from real DB parity.
Validate every existing output ancestor before mkdir/write/empty and test native
Windows junctions, not only mocked metadata. Actual Astro outside-CWD output
copied intermediate cache files: keep comparison builds inside the Website CWD,
reject leaked caches and bind screenshot/HTML/input hashes. Use existing JSON AST
parser for decoded duplicate keys, not a second regex parser. Hostile literal
mobile headings need glyph-level wrap/clipping tests. Full regression belongs
after the final stable edit batch, with focused checks during development.
Project implementation/evidence: [COACH-4](docs/exec-plans/completed/coach-4-local-readiness-2026-11-02.md).
No global skill or ManuWiki change made.

Incremental-source learning02.11 (open global proposal): distinguish a previous
processed-file baseline from an assumed complete folder snapshot. Hash bytes,
not modified time, decide NEW/MODIFIED/UNCHANGED; hash-confirmed known documents
must not be reinterpreted at every inventory. Persist processed-byte metadata
separately from rights and keep frozen approved short scope separate from a
private optional detail annex. Repeated method/credential headings, individual/
general labels and workshop/lecture blanket statements need contextual mapping,
not automatic role/qualification/format multiplication. Reference/customer,
contact, price and embedded attendee/image data stay out of public outputs;
preserve only necessary classification. Physical PDF page anchors avoid doubled
footer numbering. Publication diff needs explicit field groups and must not
invent identity/approval changes or flag empty boundary containers. Evidence:
[incremental review](docs/architecture/source-ingestion-20261030-2026-11-02.md).
Project safeguards/tests implemented; canonical skills unchanged.

## Implemented / Historical

The archive's Implemented Feedback section preserves authoritative-clock-integration-tests and design-system-derivation.
Its Rejected Or Deferred section and all older evidence remain unchanged.
Do not copy all historical proposals into this router or change global skills without an actual skill task.
