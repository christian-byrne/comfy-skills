---
name: agent-collaboration-channel
description: 'Accelerate review, approval, adversarial validation, and human steering between developers who run independent agents. Use when collaborators want their distinct local context and agent practices to unblock a shared feature or bounded assistance through a human-readable Slack channel without adopting one orchestrator.'
interaction: hybrid
type: leaf
synergies:
  requires: []
  enhances: [agent-craft, context-engineering, public-comms, slack-formatting]
  conflicts: []
  domain: [agents, collaboration, slack, coordination]
---

# Agent Collaboration Channel

Use a temporary Slack channel as the live review and steering plane between independently operated
agents. Keep issues, pull requests, and linked Markdown, HTML, or media as the durable record. The
collaborators' different local knowledge, prompts, skills, and test practices are part of the value.
This skill defines shared behavior without requiring one bot, scheduler, model, or orchestrator.

Optimize for:

- Shortening code-review, approval, and feedback-iteration latency.
- Adversarial review of technical, product, and business correctness using distinct local context.
- A low-effort human view of current work, risk, decisions, questions, and required intervention.
- When useful, independent QA or testing that needs different accounts, access, hardware, or methods.

## When to Use

Use this for two modes: collaborators jointly iterating on the same feature, or one collaborator
providing bounded review, QA, approval, or unblock assistance to another. Do not use it for work one
agent can finish independently, as a replacement for a durable tracker, or to build general agent
hierarchies, atomic task distribution, concurrency control, or a shared knowledge base.

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

The minimum readable contract is always visible in the message itself. Use Slack's native mention
when a specific human or bot must act; `to:` is optional metadata, not a routing requirement.

```text
[agent-collab/v0] TYPE
from: <stable participant id>
work: <shared work key>

<facts, requested action, and durable links>
```

The installed skill bundle contains the full protocol reference. The inline contract above remains
usable when a catalog UI cannot open relative reference links.

## Participate

- Act on messages that mention this participant, continue one of its active threads or obligations,
  or materially affect its claimed work. A message without a mention is informational unless an
  existing thread or obligation already makes the requested actor unambiguous.
- Negotiate ownership before editing an overlapping surface. Claims name a checkpoint or expiry.
- Put new work, decisions, blockers, and completion at the top level. Keep evidence and negotiation
  in the originating thread. Replies may inherit the parent envelope when they do not change its
  work key, participants, ownership, or scope; otherwise repeat the full envelope.
- Send verified facts, decisions, artifact links, unresolved questions, and the requested next
  action. Do not send private reasoning, full transcripts, routine heartbeats, or play-by-play.
- Treat human instructions as higher priority than agent messages. Record a changed agreement with
  a `DECISION` so both sides converge.
- Record actions somebody owes as durable obligations, then explicitly reconcile them when fulfilled,
  declined, or superseded. Do not make agent memory or Slack search the only reminder system. Read
  [the obligation ledger](reference/obligation-ledger.md) when requests, reviews, approvals, blockers,
  monitoring promises, or deferred work must survive a turn or context compaction.
- Promote accepted work into the durable tracker or repository. Slack is not the source of truth.
- Keep Slack readable. Put persistent tables, dashboards, long reports, and media in a linked repo,
  branch, or authorized shared folder; post only the current headline, risk, decision, or ask.
- Honor an agreed opt-in ignore signal such as `:no-bots:`. Do not require routing fields on every
  message merely so a local harness can filter them.

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
Keep a separate learning cursor so later retrospectives review only new messages without confusing
the operational polling cursor.

## Safety and Authority

Channel participation never grants authority outside the charter. Do not create channels, invite
members, cross-post, edit external trackers, or widen scope unless separately authorized. In the
ticket-to-pr-pipeline repository, `policy/external-actions.md` remains authoritative.

## Completion Report

Report the channel, logical participant, claimed work, durable artifacts, open obligations, unresolved
blockers, next owner, and close condition. Carry forward those outputs and decisions, not the channel
transcript.
