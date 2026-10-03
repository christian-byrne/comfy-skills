# Obligation Ledger

Use a small durable ledger when an action must survive a Slack scroll, agent restart, or context
compaction. The ledger complements live coordination; it is not another backlog. Record only work
that one party is waiting on or has promised to another party.

## Entry

```markdown
## OBL-014 — Review PR #1615

- Status: open
- Owed by: dev-b/reviewer
- Owed to: dev-a/builder
- Work: beta-args-preview
- Opened: 2026-10-01T11:20:00Z
- Due/checkpoint: 2026-10-01T15:00:00Z
- Action: Review the stopped-state preview and approve or request changes.
- Context: The running-state path passed QA; stopped state reuses launch grant resolution.
- Evidence: <PR/deep link>
- Resolution: —
```

Use a stable ID. `Owed by` is the next actor; `Owed to` is who needs the result. The actor may be a
human, agent, or peer participant. Put enough context in the entry that rereading it restores why the
request exists, but link to evidence rather than copying a transcript.

Valid statuses are `open`, `parked`, `reconciled`, and `superseded`. A parked entry names a wake
condition or date and is not treated as an active human ask before that trigger. Reconciliation
records the result, evidence, timestamp, and any successor obligation. A reply, merge, or passing
check is not enough by itself: update the ledger so the old request cannot be rediscovered as pending.

## Operating Pattern

1. On a request, promise, blocker, review handoff, approval need, or monitoring commitment that will
   outlive the current turn, create the ledger entry and send an `OWE` message with its ID.
2. At wake-up, read open entries owned by the local participant before reading broad channel history.
3. When the action resolves, reread its entry, update it, and send `RECONCILE`. This deliberately
   restores the original context before interpreting the response.
4. Periodically post a compact index only when it changes or at an agreed checkpoint:
   `Open: OBL-014 dev-b/reviewer → review #1615; OBL-018 human/release-owner → rollout decision`.
5. Before `DONE`, reconcile or explicitly transfer all obligations for the work key.

Run a coverage audit at agreed checkpoints: every in-scope unmerged pull request or work artifact
mentioned in the channel must map to an obligation or an explicit out-of-scope decision. Thread-per-
obligation is a useful view, not a protocol requirement. A top-level obligation should represent a
cross-party coordination edge; private single-owner details may stay in the ledger and compact index.

Natural-language promises inside threads still count. Promote “update me in 25 minutes,” a newly
requested review, or a nested approval into the current obligation or a stable child obligation. A
standing obligation needs a cancellation condition; a time-bound one needs a checkpoint an auditor
can detect. Human approval or risk acceptance names the human as the next actor rather than replacing
ownership with a program priority.

Link dependencies using navigable Slack or artifact links, not bare obligation IDs. When the transport
allows editing, the top-level obligation post may be the mutable current-state card: update its status
or strike the resolved ask while keeping its thread append-only as evidence, negotiation, and correction
history.

The charter's durable record may contain the ledger, or each participant may keep a local Markdown
file and publish the relevant open index. Name its location in the charter. Never put tokens, private
reasoning, or unrelated personal reminders in it.

An optional auditor loop may compare new Slack messages, recent agent output, and ledger changes to
flag a likely missing or stale entry. It may propose updates, but it must not invent a reconciliation
or silently assign a human.

## Good Boundaries

- “FYI, no action needed” is an `UPDATE`, not an obligation.
- A question needed to proceed creates an obligation on the named respondent.
- A monitoring promise creates an obligation on the monitor until its stop condition or next report.
- A correction reconciles or supersedes the inaccurate entry and links its replacement.
- A deferred finding needs an owner and durable follow-up; “later” alone is not reconciled.
- Evidence expectations are negotiable. If an authorized human says screenshots are unnecessary,
  record the accepted verification result rather than manufacturing proof.
