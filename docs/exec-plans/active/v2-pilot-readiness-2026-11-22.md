# V2 Pilot Launch Readiness

Source checkpoint: `22c37ff`, previous exact-source ZIP `a6bea57`. Freeze
product scope; only concrete readiness and accessibility issues may change.

| Step | Exit condition | State |
| --- | --- | --- |
| 1. Inventory | Repository, artifact and historical operational evidence distinguished from live readings. | Local inventory done; fresh VPS inventory pending authorization/access |
| 2. Recovery | Pinned Linux source and destination, local synthetic OpenPGP, original disposed, exact archive boots after restore. | Previous exact archive passed; current candidate retest pending |
| 3. Integrated QA | Native PostgreSQL, existing workflow and synthetic invitation through first permitted workspace; no mail. | In verification |
| 4. Accessibility | Technical findings remedied and checked; separate spoken result or actionable manual test. | In verification |
| 5. Candidate | Exact-source ZIP, checksum and nonsecret operator reference; independent recovery receipt. | Pending |
| 6. Protected access | Owner/EDV chooses valid TLS before 30 Nov; no changes without separate release authorization. | Open |
| 7. Controlled pilot | V2 sign-off, current VPS and source recovery parity, explicit clone/migrate/activate authorization; no real user rollout bundled. | Open |

[Consolidated handoff](../../handoffs/2026-11-22-v2-pilot-readiness.md).
Reusable verification rule: PostgreSQL parity and an installed package alone
do not prove restart with independently recovered runtime key material.
