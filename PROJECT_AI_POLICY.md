# Website Project AI Policy

## Policy Metadata

- Project: Website
- Owner: Manuel
- Repository root: `C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website`
- Policy version: `0.1-pilot`
- Last reviewed: 2026-06-30
- Review owner: Manuel

## Approved AI Roles

| Role | Approved system or registry entry | Allowed work | Human gate |
| --- | --- | --- | --- |
| Primary coding | Codex Plus / `codex-plus-primary` | Genuine code changes, architecture, integration, technical review | Required for expanded scope, destructive actions, deployment, or external communication |
| Local sensitivity check | Ollama / `ornith:9b` | Sanitized permitted metadata and synthetic eval inputs only | Required if classification is ambiguous |
| Local simple classification | Ollama / `ornith:9b` | Low-impact closed-set classification of permitted, sanitized inputs | Required before expanding task or data classes |
| External routine assistance | OpenRouter / no model approved yet | None until a concrete model is registered, evaluated, and explicitly enabled | Always during pilot |
| Final review | Codex Plus plus deterministic project checks | Independent acceptance against project requirements | Required for production-impacting work |

Hermes Agent is not approved for this pilot.

## Hard Data And Path Denials

The following rules apply before directory listing, file reading, indexing, embedding, classification, prompt construction, or model invocation:

- Any directory or normalized path segment named `Quellen`, matched case-insensitively, is excluded from all AI access.
- Files named `.env` or beginning with `.env.` are excluded. A documented non-secret `.env.example` may be reviewed only after explicit confirmation that it contains no real values.
- Files or path segments named `key`, `token`, or `secret`, matched case-insensitively with or without common text/config suffixes, are excluded.
- Credential values, API keys, access tokens, passwords, private keys, session secrets, and authentication material are excluded regardless of filename.
- Personal data and personally identifiable information are excluded from auxiliary-model and external-model processing.
- Contractual data, contracts, offers, commercial terms, customer agreements, and related confidential records are excluded from auxiliary-model and external-model processing.
- Copied, archived, generated, linked, embedded, or renamed material remains excluded when its origin or content falls under these rules.

An excluded path must not be opened to determine whether it is sensitive. Path rules take precedence over model-based classification.

## Data Classes

| Class | Local Ollama | OpenRouter or another cloud model | Logging |
| --- | --- | --- | --- |
| Public and sanitized | Allowed for approved low-impact tasks | Denied until a concrete model is approved; then task-specific gate required | Metadata only |
| Internal, non-sensitive | Allowed only when minimized and explicitly in task scope | Denied during initial pilot | Metadata only |
| Ambiguous | Stop and request review | Denied | Classification outcome only |
| Personal data | Denied | Denied | Never |
| Contractual/confidential data | Denied | Denied | Never |
| Secret or credential | Denied | Denied | Never |
| Excluded path content | Denied | Denied | Path-rule outcome only |

## Pilot Routing Rules

- Genuine Website code or configuration changes route to Codex Plus. This read-only pilot authorizes no Website code changes.
- Sensitivity preflight and simple classification may route to local `ornith:9b` only after deterministic path and data gates pass.
- Only sanitized summaries created from the explicitly allowed project status files may be used in this pilot.
- OpenRouter is disabled for this pilot. No external-model call or payload preparation is allowed.
- Hermes Agent is disabled.
- `qwen3.5` and `gemma4:e2b-it-q4_K_M` are suspended because the local runtime currently fails to load them with CLIP/Vision-related errors.
- A failed or unavailable local model does not trigger an external fallback.

## Allowed Project Files For This Read-Only Pilot

Only these exact files may be opened if present:

- `PROJECT_LOG.md`
- `PROJECT_PLAN.md`
- `PROJECT_STATUS.md`

No other Website file or directory may be listed, opened, indexed, or changed during this pilot.

## Logging Policy

Allowed:

- eval-case identifier;
- selected registry entry and model identifier;
- task and sensitivity labels;
- pass/fail and sanitized failure category;
- latency and approximate local token metadata when available;
- policy and registry version.

Forbidden:

- raw prompts or model completions;
- Website file contents or excerpts;
- filenames beyond the three explicitly allowed status files;
- excluded-path content;
- personal, contractual, confidential, or credential data.

## Failure And Stop Conditions

- Stop before reading when a requested path matches a hard denial.
- Stop before local-model use when sanitized input cannot be separated confidently from a denied data class.
- Stop after malformed, policy-violating, or materially incorrect output; do not silently switch models.
- Escalate ambiguous sensitivity or expanded scope to Manuel.
- Treat any prohibited read, index, log, or transmission as a security incident and suspend routing.

## Pilot Approval Boundary

This policy authorizes one supervised, read-only project-state evaluation with local `ornith:9b`. It does not authorize Website code changes, OpenRouter, Hermes, automatic routing, background execution, deployment, or access to any file outside the three status files.
