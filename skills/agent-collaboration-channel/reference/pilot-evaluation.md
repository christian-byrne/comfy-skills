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
| Coverage gaps           | In-scope artifacts with neither an obligation nor an explicit out-of-scope decision.   |
| Dispatch ambiguity      | Handoffs lacking an exact receiving agent/session, destination, or acknowledgement.    |

## Initial Success Thresholds

- Median acknowledgement under ten minutes while both loops are active.
- At least 70% useful-action ratio.
- No unauthorized posts or duplicate implementation caused by conflicting claims.
- Every completed work unit links a durable artifact.
- Every owed action that survives a turn has a stable ledger ID; no orphan obligations remain at close.
- Both developers rate coordination burden lower than the comparison workflow.

## Review

Keep a durable learning cursor separate from operational polling. For each review, enumerate all
top-level messages and replies after that cursor, including early threads whose newest reply is later
than the cursor. Do not advance it after a partial fetch. Record accepted findings in the learning log,
then persist the greatest reviewed message/reply timestamp and audit time.

Read both sides' traces and channel threads. Separate transport failures, harness failures, protocol
ambiguity, agent judgment failures, and configurable local practice. Check especially for coverage
gaps, nested promises, stale status tables, parked work without wake conditions, ambiguous dispatch,
and human decisions without a named owner. Change the shared protocol only for repeated or high-impact
failures. Prefer improving a local adapter when the shared semantics already worked.

Dense top-level status tables should carry a short current headline and move details into threads.
If a canonical table is maintained, include operational readiness such as `CI failing`, `iterating`,
`agent QA done`, `ready for human`, `waiting on <reviewer>`, `blocked`, or `merged`; a stale table is
worse than no table.
