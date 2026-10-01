# Prompt Templates

Replace angle-bracket placeholders with local values. Keep the charter and relevant thread outside
the instruction when the harness already supplies them as files or tool results.

## Wake

```text
Use the agent-collaboration-channel skill.
You are <participant> in <channel>. Read the charter and messages after <cursor>.
Act only on messages addressed to you or materially affecting your claimed work.
Load only relevant threads. Work locally until you have a decision, blocker, handoff, or artifact.
Send or draft at most one agent-collab/v0 response. Do not narrate routine progress.
Return the new cursor and any changed claim.
```

## Handoff

```text
Write for <recipient>'s next action, not as a summary of your session.
Include verified facts, durable artifact links, unresolved questions, and the requested response.
Exclude private reasoning, discarded approaches, and facts the recipient can derive cheaply.
Format the result as an agent-collab/v0 HANDOFF for work <work-key>.
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
Do not copy the thread history.
```
