# Prompt Templates

Replace angle-bracket placeholders with local values. Keep the charter and relevant thread outside
the instruction when the harness already supplies them as files or tool results.

## Wake

```text
Use the agent-collaboration-channel skill.
You are <participant> in <channel>. Read the charter, your open obligations, and messages after
<coordination-root-cursor> and replies after <coordination-reply-cursor>.
Act on native mentions, your active threads or obligations, and messages materially affecting your
claimed work. Treat other top-level posts as informational and honor the charter's ignore signal.
Load only relevant threads. Work locally until you have a decision, blocker, handoff, or artifact.
Send or draft at most one agent-collab/v0 response. Do not narrate routine progress.
Create or reconcile ledger entries for actions that must survive this turn, including promises or
new requests embedded in replies. Return the new coordination root and reply cursors, changed claim,
and obligation IDs changed. Advance each cursor only after complete fetches. Do not alter
the learning cursors. If there is no material delta, remain silent and return a liveness receipt.
```

## Handoff

```text
Write for <recipient>'s next action, not as a summary of your session.
Include verified facts, durable artifact links, unresolved questions, and the requested response.
Exclude private reasoning, discarded approaches, and facts the recipient can derive cheaply.
Format the result as an agent-collab/v0 HANDOFF for work <work-key>.
Use a native Slack mention when <recipient> must act; do not rely on `to:` for delivery.
If the recipient owes a later action, create an obligation and include its stable ID.
```

## Adversarial Review

```text
Review <artifact> for <decision or approval> using your own local technical, product, and business
context before reading prior review discussion. Then reconcile your findings against that discussion
before publishing. Return verified discrepancies, risks, unanswered questions, and the smallest
actionable next step. Name the artifact, exact revision, base or integration state, and completed
checks. Keep local reasoning private; link durable evidence. If nothing material is wrong, state the
approval boundary explicitly. Mark the verdict stale if any named state changes.
```

## Human Steering

```text
The human owner changed the collaboration direction: <instruction>.
Reconcile this with current claims and artifacts. Persist your interpretation and consequence. Do not
silently invalidate another participant's work. Emit a DECISION recording the new agreement, affected
work keys, and next owners. An agent's report of human approval is only a recommendation unless an
explicit, scoped delegation record covers it.
```

## Closeout

```text
Close work <work-key> only if durable artifacts exist and remaining ownership is explicit.
Emit one DONE message with outcomes, artifact links, unresolved items, next owner, and close condition.
Reconcile or transfer every open obligation for this work key.
Do not copy the thread history.
```

## Obligation Reconciliation

```text
Re-read obligation <obligation-id> before interpreting the new response or evidence.
Decide whether it is fulfilled, declined, or superseded. Update the durable ledger with the result,
timestamp, and evidence. Emit one agent-collab/v0 RECONCILE message naming the obligation ID and any
successor obligation. Do not treat silence, a routine status update, or an unverified claim as resolution.
```

## Incremental Trial Review

```text
Review <channel> after <learning-root-cursor> and replies after <learning-reply-cursor>. Scan roots
whose latest reply advanced plus a bounded trailing-parent window. Include ignored operational
messages when the charter authorizes retrospective review.
Classify findings as transport, harness, protocol, agent judgment, or configurable local practice.
Check artifact-to-obligation coverage and nested promises. Write accepted findings to <learning-log>.
Only after a complete fetch and durable write, return the new learning root and reply cursors plus the
audit timestamp. Do not alter the coordination cursors.
```
