# Prompt Templates

Replace angle-bracket placeholders with local values. Keep the charter and relevant thread outside
the instruction when the harness already supplies them as files or tool results.

## Wake

```text
Use the agent-collaboration-channel skill.
You are <participant> in <channel>. Read the charter, your open obligations, and messages after <cursor>.
Act only on messages addressed to you or materially affecting your claimed work.
Load only relevant threads. Work locally until you have a decision, blocker, handoff, or artifact.
Send or draft at most one agent-collab/v0 response. Do not narrate routine progress.
Create or reconcile ledger entries for actions that must survive this turn.
Return the new cursor, changed claim, and obligation IDs changed.
```

## Handoff

```text
Write for <recipient>'s next action, not as a summary of your session.
Include verified facts, durable artifact links, unresolved questions, and the requested response.
Exclude private reasoning, discarded approaches, and facts the recipient can derive cheaply.
Format the result as an agent-collab/v0 HANDOFF for work <work-key>.
If the recipient owes a later action, create an obligation and include its stable ID.
```

## Human Steering

```text
The human owner changed the collaboration direction: <instruction>.
Reconcile this with current claims and artifacts. Do not silently invalidate another participant's
work. Emit a DECISION recording the new agreement, affected work keys, and next owners.
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
