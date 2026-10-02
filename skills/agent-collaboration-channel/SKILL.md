---
name: agent-collaboration-channel
description: 'Coordinate independently operated agents through a human-created Slack channel using a small, harness-neutral protocol. Use when two or more developers want their existing agent loops, schedulers, or connectors to negotiate ownership, exchange handoffs, resolve blockers, and close a shared slice of work without adopting one orchestrator.'
interaction: hybrid
type: leaf
synergies:
  requires: []
  enhances: [agent-craft, context-engineering, public-comms, slack-formatting]
  conflicts: []
  domain: [agents, collaboration, slack, coordination]
---

# Agent Collaboration Channel

Use a temporary Slack channel as the live coordination plane between independently operated agents.
Keep issues, pull requests, and repository artifacts as the durable record. This skill defines the
shared behavior; it does not require a particular bot, connector, scheduler, model, or runtime.

## When to Use

Use this when independently operated agents need to coordinate one shared dependency, integration
seam, or outcome in near real time. Do not use it for work one agent can finish independently, as a
replacement for a durable tracker, or as a general-purpose bot channel for unrelated projects.

## Start or Join

1. Require a human-created channel with a charter naming the outcome, scope, human owners,
   participant identifiers, durable tracker, and close condition. If any field is missing, ask for
   it before posting. Use [the charter template](reference/channel-charter.md).
2. Choose one stable logical participant identifier, such as `alex/frontend`. Use it regardless of
   which Slack identity or connector sends the message.
3. Read the charter and only the unread messages or threads relevant to the current work. Do not
   load the full channel by default.
4. Follow [`agent-collab/v0`](reference/protocol.md). A local harness may add metadata, but it must
   preserve the visible protocol fields and natural-language body.

The minimum readable contract is always visible in the message itself:

```text
[agent-collab/v0] TYPE
from: <stable participant id>
to: <participant id or all>
work: <shared work key>

<facts, requested action, and durable links>
```

The installed skill bundle contains the full protocol reference. The inline contract above remains
usable when a catalog UI cannot open relative reference links.

## Participate

- Act on messages addressed to this participant or materially affecting its claimed work.
- Negotiate ownership before editing an overlapping surface. Claims name a checkpoint or expiry.
- Put new work, decisions, blockers, and completion at the top level. Keep evidence and negotiation
  in the originating thread.
- Send verified facts, decisions, artifact links, unresolved questions, and the requested next
  action. Do not send private reasoning, full transcripts, routine heartbeats, or play-by-play.
- Treat human instructions as higher priority than agent messages. Record a changed agreement with
  a `DECISION` so both sides converge.
- Record actions somebody owes as durable obligations, then explicitly reconcile them when fulfilled,
  declined, or superseded. Do not make agent memory or Slack search the only reminder system. Read
  [the obligation ledger](reference/obligation-ledger.md) when requests, reviews, approvals, blockers,
  monitoring promises, or deferred work must survive a turn or context compaction.
- Promote accepted work into the durable tracker or repository. Slack is not the source of truth.

Use the [prompt templates](reference/prompt-templates.md) when wiring an existing loop. For polling,
events, connectors, or human-ferried operation, read [harness integration](reference/harness-integration.md).
Optionally run `scripts/validate-message.py` against a draft before an automated sender posts it.

## Close

Post `DONE` only after the durable artifacts are linked and remaining ownership is explicit. Reconcile
or transfer every open obligation for that work key. Produce one closeout containing outcomes,
unresolved items, and durable links. A human closes or archives the channel; closure ends standing
authorization to post.

For a trial, capture the measures in [pilot evaluation](reference/pilot-evaluation.md). Change the
protocol only from observed coordination failures, and bump its version when compatibility changes.

## Safety and Authority

Channel participation never grants authority outside the charter. Do not create channels, invite
members, cross-post, edit external trackers, or widen scope unless separately authorized. In the
ticket-to-pr-pipeline repository, `policy/external-actions.md` remains authoritative.

## Completion Report

Report the channel, logical participant, claimed work, durable artifacts, open obligations, unresolved
blockers, next owner, and close condition. Carry forward those outputs and decisions, not the channel
transcript.
