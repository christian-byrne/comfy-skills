# `agent-collab/v0` Protocol

The protocol is a thin, visible envelope around ordinary language. Slack supplies transport,
timestamps, threading, and delivery identity; the envelope supplies stable meaning across harnesses.

## Envelope

```text
[agent-collab/v0] OFFER
from: dev-a/frontend
to: dev-b/frontend
work: primevue-overlay

I can own Dialog wrappers if you take Select and Popover.

Evidence: <links or verified facts>
Need: accept, counter-propose, or identify overlap
Next check: 14:30 UTC
```

The first four non-empty lines are required. `to` may be a participant identifier or `all`. Keep
identifiers stable for the channel lifetime. `work` is a short key shared by every message about the
same work unit.

The body is natural language. Include only the fields that help the receiver act:

- `Evidence:` verified facts or deep links.
- `Need:` the requested response or action.
- `Next check:` a checkpoint, not a routine heartbeat.
- `Claim until:` the expiry for exclusive ownership.
- `Artifacts:` durable issues, pull requests, commits, plans, or documents.
- `Obligation:` stable ledger ID for an owed action or its reconciliation.
- `Decision owner:` human or participant whose call is required.
- `No action needed:` explicitly marks an informational update.

## Message Types

| Type        | Use                                                               |
| ----------- | ----------------------------------------------------------------- |
| `OFFER`     | Propose ownership, a division of work, or an interface.           |
| `CLAIM`     | Accept bounded ownership and state a checkpoint or expiry.        |
| `QUESTION`  | Ask for information required for a decision or next action.       |
| `DECISION`  | Record an agreement that changes subsequent work.                 |
| `UPDATE`    | Report a material state or evidence change.                       |
| `HANDOFF`   | Transfer verified context and an explicit requested action.       |
| `BLOCKED`   | State an impediment, evidence, and the person or event needed.    |
| `OWE`       | Record a durable action owed by one party to another.             |
| `RECONCILE` | Close, decline, transfer, or supersede a recorded obligation.     |
| `DONE`      | Close a work unit with durable artifacts and remaining ownership. |

## Channel Shape

- Start a top-level message for a new work unit, decision, blocker, or completion.
- Reply in its thread for negotiation, evidence, and corrections.
- Keep a top-level message at or below 400 characters when practical; put detail in its thread.
- Do not respond to a message whose `from` matches the local participant unless explicitly testing.
- Use Slack's message timestamp or Events API `event_id` as the delivery deduplication key.
- Process retries idempotently. Never infer that a repeated delivery is a new request.
- Distinguish an informational update with `No action needed:` from a request that creates an
  obligation. Name the decision owner when presenting choices or asking for a call.

## Claims and Conflicts

A claim is advisory coordination, not a lock. It must identify its surface and a checkpoint or
expiry. Before overlapping work, reply with a counter-proposal or ask the human owners to decide.
Expired claims may be reclaimed after posting an `UPDATE`; never silently take them over.

## Obligations and Reconciliation

Use `OWE` when a requested or promised action must survive the current turn. Include `Obligation:`,
the next actor, requested outcome, context, evidence, and due time or checkpoint in the durable ledger.
Use `RECONCILE` only after rereading that entry and verifying the result. Link the result and name any
successor obligation. See [the ledger format](obligation-ledger.md).

Corrections are first-class state changes. Reply in the originating thread, identify the inaccurate
claim, and reconcile or supersede any affected obligation. Never silently edit history into appearing
correct.

## Protocol Evolution

Participants may add project-specific conventions through a `DECISION`. Do not change required
fields or redefine message types within v0. Record proposed protocol changes during the pilot and
update the shared skill after reviewing evidence from both sides.
