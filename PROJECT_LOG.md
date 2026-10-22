# Project Log

Significant milestones only; newest first.
The complete log through 25.09.2026 is preserved byte-for-byte in [the history archive](docs/history/context-migration-2026-10-21/PROJECT_LOG.md).

## 2026-10-22 | implementation / verification | Preview Hub and Calendar access batch

- Preview source 1cc481de9210 pushed/published through manual Pages run 39774218286; 134 actual public Hub checks PASS. Full 52-file production build manifest unchanged; no IONOS write.
- Additive Calendar Login/MFA/session uses explicit admission policy without widening internal Auth or granting roles. No migration. Database exception logging hardened against row DETAIL leakage.
- Local: 424 tests, 17 expected Staging skips, 57 visual checks, 142 real-runtime/local-PostgreSQL browser checks and 17 integration tests. Exact cleanup left 20 dynamic tables zero; local owned container removed.
- Existing SSH key worked twice independently; no agent/sshd/sudo/key changes. Read-only VPS health four active and PG loopback; actual native VPS DB/UI batch still PENDING secure local entry of two role passwords.
- [Batch report](docs/architecture/calendar-cal1-access-batch-2026-10-22.md) owns the matrix/operator command; [active plan](docs/exec-plans/active/post-messe-backend-horizon-2026-10.md) advances to the single native gate, then readiness preparation only after PASS.
- Reusable learning captured in project skill feedback; global skills unchanged.

## 2026-10-21 | gate / finding | Native CAL-1 UI preflight

- Manuel authorized synthetic native Staging UI acceptance, not production or real identities.
- Preflight found the missing pure-Coach/Reviewer native login/MFA/session path; internal Auth was deliberately not widened. No Staging records or service changes.
- [Acceptance evidence](docs/architecture/calendar-cal1-native-staging-ui-acceptance-2026-10-21.md) distinguishes local regression from the still-open native matrix; the [active horizon](docs/exec-plans/active/post-messe-backend-horizon-2026-10.md) now prioritizes the access prerequisite.
- No commit, push or deployment. Existing Context V2/Analytics work remains separate.

## 2026-10-21 | context / decision | Post-Messe restart

- Manuel confirms that the Messe on 17.10.2026 succeeded; its temporary freeze and holiday cutlines are closed.
- Context V2 replaces repeated root-state loading with AGENTS -> PROJECT_CONTEXT -> domain router -> task plan.
- Six former root files are hash-bound in the [migration manifest](docs/history/context-migration-2026-10-21/manifest.json); no historical content was deleted.
- The [environment policy](docs/architecture/environment-policy.md) separates stable IONOS production, authorized GitHub preview and the backend product path.
- Preview publication/content are authorized in the 21.10 addendum; IONOS deployment, real Portal identities, SMTP and productive tracking are not.
- Preview commit b02ded1 was pushed and published through the existing manual Pages workflow; live checks passed. IONOS remained unchanged. Analytics is design-only, consent OPEN.
- Closed-scope evidence: [completed plan](docs/exec-plans/completed/post-messe-konsolidierung-2026-10.md) and [audit](docs/architecture/context-migration-audit-2026-10-21.md). Subsequent native Staging UI authorization/preflight is recorded above; it was not part of preview publication.
