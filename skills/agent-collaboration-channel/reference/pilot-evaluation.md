# Pilot Evaluation

Run one real collaboration slice for three to five working days. Compare it with a recent
GitHub/Linear-only collaboration where possible.

## Capture

| Measure                 | Definition                                                                             |
| ----------------------- | -------------------------------------------------------------------------------------- |
| Acknowledgement latency | Time from an addressed message to acknowledgement or action.                           |
| Blocker duration        | Time from `BLOCKED` to resolution, reroute, or human decision.                         |
| Useful-action ratio     | Messages that cause an action, decision, correction, or artifact / all agent messages. |
| Duplicate work          | Overlapping implementation caused by conflicting or missed claims.                     |
| Stale claims            | Claims that expire without an update, handoff, or explicit release.                    |
| Human steering          | Interventions needed to correct scope, ownership, protocol, or noise.                  |
| Durable promotion       | Accepted decisions and outputs represented in the tracker or repository.               |
| Obligation recall       | Owed actions reopened correctly after restart or context compaction.                   |
| Reconciliation lag      | Time from fulfilled action to verified ledger reconciliation.                          |
| Orphan obligations      | Open entries with no actor, checkpoint, or explicit transfer at close.                 |
| Noise score             | Each developer's 1-5 rating of interruption and channel clutter.                       |

## Initial Success Thresholds

- Median acknowledgement under ten minutes while both loops are active.
- At least 70% useful-action ratio.
- No unauthorized posts or duplicate implementation caused by conflicting claims.
- Every completed work unit links a durable artifact.
- Every owed action that survives a turn has a stable ledger ID; no orphan obligations remain at close.
- Both developers rate coordination burden lower than the comparison workflow.

## Review

Read both sides' traces and channel threads. Separate transport failures, harness failures, protocol
ambiguity, and agent judgment failures. Change the shared protocol only for repeated or high-impact
failures. Prefer improving a local adapter when the shared semantics already worked.
