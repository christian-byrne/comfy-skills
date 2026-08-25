---
name: stakeholder-comms
description: 'Write program updates tailored per audience (engineering, leadership, support, finance, GTM, affected users) with the right content for each, not one update reformatted. Covers what each audience needs, what to omit, the decision-first structure, and how to write an update that survives being forwarded. Use when drafting a status update, exec summary, support brief, launch note, or any message where the reader is not the person doing the work.'
interaction: hybrid
type: leaf
synergies:
  enhances: [program-management, internal-comms, project-status-generator, program-dependencies]
  domain: [program-management, communication, reporting]
---
# Stakeholder Comms

The default failure is one update sent to five audiences. Four of them find nothing they can act
on, and they stop reading, which means the fifth time you need something from them you have no
channel left.

Different audiences need **different content**, not different formatting of the same content.

## When to Use

- Drafting a status update, exec summary, launch note, or support brief
- Announcing a change that affects people outside the team doing it
- A previous update got no response, or the wrong response
- Someone asks "can you send an update on this"

## Audience Matrix

| Audience        | Wants                                                             | Omit                              | Their action                        |
| --------------- | ----------------------------------------------------------------- | --------------------------------- | ----------------------------------- |
| Engineering     | What changed, what breaks, what to do differently, by when        | Business framing, headcount       | Change their code or their plan     |
| Leadership      | Decision needed, risk to date, tradeoff, one number               | Implementation detail, ticket IDs | Decide, unblock, reprioritize       |
| Support         | What users will see, what to say, when it starts, escalation path | Architecture, internal naming     | Answer tickets without escalating   |
| Finance         | What moves money, when, reversibility, exposure if wrong          | Technical mechanism               | Reconcile, forecast, approve        |
| GTM / marketing | What is now true for customers, what to promise, what not to say  | Internal sequencing               | Position, announce, brief customers |
| Affected users  | What changes for them, when, what they must do                    | Everything internal               | Prepare or migrate                  |

The **their action** column is the test. If the audience has no action, they do not need the
update, they need to be able to find the canonical view. Send them a link instead.

## Structure: Decision First

Lead with what the reader must do or decide. Context is support for the ask, not a runway to it.

```
<Audience>: <the one thing they must do or know>
By when:    <date>
Why now:    <one sentence>
Detail:     <2-4 lines, or a link>
If you do nothing: <what happens>
```

The "if you do nothing" line converts a broadcast into a decision. Without it, every recipient
can defer at no visible cost.

## Queue Hygiene

Before adding a message to a queue, classify the recipient's action:

| Action                             | Durable destination                                                              |
| ---------------------------------- | -------------------------------------------------------------------------------- |
| Decide or authorize                | Pending-decision queue; message contains only the ask and packet link            |
| Do tracked work                    | Issue/ticket assigned to its owner                                               |
| Know                               | Canonical program view; send a pointer only when timing makes delivery necessary |
| Communicate now                    | Staged message with sender, channel, deadline, and delivery state                |
| None, stale, duplicate, superseded | Record disposition and close; do not keep an open message                        |

An unticked message identifier is not evidence that a message is unsent. Reconcile staged drafts
against channel history before sending. Keep delivered messages in the communication record with
`sent_at`, channel, and thread/message ID, while closing their action item.

Treat delivery as a lifecycle, not a checkbox. Every queued message has one state — `staged`,
`sent`, `answered`, or `superseded`. A sent message also records `sent_at`, channel ID,
message/thread ID, and a reply cursor. Before drafting another ask for that recipient:

1. fetch replies to the recorded thread even when its parent predates the normal channel
   watermark;
2. inspect the immediate following top-level messages because people sometimes answer beside the
   thread instead of inside it;
3. advance the reply cursor and mark the message answered or superseded; and
4. reconcile every dependent draft, decision, task, and owner in the same pass.

Do not rewrite a delivered message as though it were still a draft. Preserve its delivery record
and stage only the unresolved remainder. A broad review request that the recipient acknowledged is
answered even while individual reviews remain open; track those PRs in their authoritative system
instead of repeating the broad ask.

Measure queue health as actionable asks by recipient, not raw draft count. A queue with 100 status
summaries and 5 decisions contains 5 blockers, not 105 teammate questions.

Worked example: a 147-draft staged Slack queue, triaged with this table, resolved into four
classes — send-as-owner (Communicate now: needs the human's identity, stays staged),
status-page-fyi (Know: moved to the canonical program view, stamped, closed as a message),
cancel-expired (None: superseded by events, archived with a dated reason, batch-vetoed in one
list), and answer-needed (Decide: routed to the pending-decision queue's batch review surface).
Only the first and last classes still required the human; the queue shrank by more than half
without sending anything.

## Staged Slack Drafts

For Markdown drafts staged in Notion for a human to paste into Slack:

1. Re-derive every cited PR/ticket state, review decision, assignee, and requested reviewer from
   its authoritative API immediately before rewriting the draft. Remove asks overtaken by a merge,
   approval, reassignment, or closed decision; do not merely update their tense.
2. Verify every code or coverage premise against the canonical repository's current target ref and
   CI routing. A borrowed worktree, local proof branch, or old head is a discovery lead, not evidence
   that a control is absent upstream; compare its files and commits with the current ref before
   asking somebody to move or add them.
3. Put each paragraph on one physical source line with a blank line between paragraphs. Do not
   hard-wrap prose at an arbitrary column because Notion preserves those breaks when copied.
4. Do not use `**double-asterisk**` bold in the paste-ready body. It is not Slack formatting and
   can paste as literal punctuation.
5. Hyperlink every external identifier and source descriptively. Use
   `[#123](https://github.com/.../123)` for GitHub PRs/issues and
   `[FE-123](https://linear.app/.../FE-123/...)` for Linear tickets, never a bare identifier or raw
   URL. This Markdown form is for human-copied staged drafts; direct Slack API payloads may require
   Slack's native link syntax instead.
6. Run `python3 skills/stakeholder-comms/scripts/validate_slack_drafts.py <queue.md>` before
   publishing the queue. Wire the same command before any automatic Notion republish so malformed
   drafts fail closed.
7. Reconcile the delivery lifecycle immediately before publication. A format-valid draft with
   stale state is still invalid; validators enforce syntax, while source APIs and reply cursors
   establish whether an ask remains live.

## Rules That Apply to Every Audience

- **One canonical view, linked from everywhere.** The update is a pointer plus an ask. If the
  detail lives in five messages, the five will diverge.
- **Numbers with denominators.** "4,000 migrated" says nothing. "4,000 of 5,200 (77%)" does.
- **Say what is not known.** Unknowns stated in advance are competence; unknowns discovered later
  by the reader are a credibility loss you do not get back.
- **Bad news early and plainly.** Slippage disclosed late costs more than the slippage.
- **Write for forwarding.** Assume it gets pasted somewhere with no context. Name the program in
  the first line and avoid pronouns whose referent is a previous message.
- **No status theater.** Activity lists ("met with X, reviewed Y") are not progress. Report state
  changes.

## Cadence

Match cadence to state change, not to the calendar. A weekly update with nothing new trains
people to skip the week something matters. If nothing changed, send one line saying so and what
the next gate is.

At minimum, send on: gate entered or exited, stop condition triggered, decision needed, date
moved.

## Escalations Are Not Updates

An escalation goes to one person or one forum with options and a required-by date. See
`program-decisions`. Do not bury a decision request inside a broadcast update, where it will be
read as information.

## Anti-Patterns

- One update forwarded to five audiences
- Leading with context and burying the ask in the last paragraph
- Raw counts with no denominator
- Status-only messages kept open as if somebody must answer them
- Assuming drafts are unsent without checking channel history
- Scanning only new parent messages and missing late replies on older threads
- Repeating an acknowledged broad ask because its individual work items remain open
- Treating a borrowed worktree as proof that its controls are absent from the current target ref
- Putting the full decision analysis in Slack instead of linking one canonical packet
- Weekly cadence maintained through periods of no change
- Support and finance learning from users and invoices respectively

## Parent Graph

Part of: `program-management`
