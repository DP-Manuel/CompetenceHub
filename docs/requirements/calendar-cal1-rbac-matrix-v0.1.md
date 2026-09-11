# CAL-1 RBAC Matrix v0.1

Stand: 11.09.2026

Status: technical authorization baseline under accepted ADR 0007. The proposed
`calendar_reviewer` role is not seeded or assigned by this document.

## Roles And Scope

- `admin`: technical break-glass and full Calendar operation, still bound by
  MFA, state transitions and audit.
- `internal`: no automatic publication right.
- `calendar_reviewer`: additive least-privilege role for review queue, changes
  requests and publication. Initially intended for Janay, never tied to her
  identity in code.
- `coach`: manages only the Coach linked to their own portal user.
- `company_contact` and anonymous: published reads only in CAL-1.

## Matrix

| Action | Admin | Internal | Calendar reviewer | Coach | Company contact | Anonymous |
| --- | --- | --- | --- | --- | --- | --- |
| Read public published offers | yes | yes | yes | yes | yes | yes |
| Read private drafts/reviews | all | no | review scope | own only | no | no |
| Create offer/draft | yes | no | no | own only | no | no |
| Edit draft/change request | yes | no | no | own only | no | no |
| Submit for review | yes | no | no | own only | no | no |
| Read review queue | yes | no | yes | no | no | no |
| Request changes | yes | no | yes | no | no | no |
| Publish reviewed revision | yes | no | yes | no | no | no |
| Withdraw offer | yes | no | review scope | own only | no | no |
| Hard-delete offer/revision/decision | no | no | no | no | no | no |
| Assign `calendar_reviewer` | yes | no for Pilot | no | no | no | no |
| Read Calendar audit evidence | yes | existing audit policy | no by role alone | no | no | no |

Multiple roles combine explicit grants, but Coach ownership and reviewer scope
remain enforced. A role never turns a client-supplied Coach ID into ownership.

## Required Negative Tests

- unauthenticated and company-contact writes are denied;
- Internal without `calendar_reviewer` cannot see queue or publish;
- a Coach cannot infer, read, edit, submit or withdraw another Coach's draft;
- reviewer cannot create/edit as Coach without the linked Coach role;
- deactivated, expired, revoked and pre-MFA sessions are denied;
- stale CSRF, wrong Origin, guessed UUID and stale ETag fail without mutation;
- Admin bypasses scope only, not state, validation, MFA or audit;
- role removal takes effect on the next server-side permission check;
- public projection contains no draft, reviewer, portal-user or contact data.

## Assignment Gate

The future migration may seed `calendar_reviewer`, but no account receives it
until named-account onboarding is authorized. Pilot assignment/removal is
Admin-only, audited and verified through positive and negative tests. A future
substitute uses a separate account.
