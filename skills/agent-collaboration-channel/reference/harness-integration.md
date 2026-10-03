# Harness Integration

The common contract is the skill and visible message envelope, not a shared process. Each developer
keeps their existing loop and Slack access method.

```text
schedule, event, or human prompt
             |
             v
read open local obligations -> read after cursor -> filter relevant/duplicate/self messages
             |
             v
run or resume local agent with charter + relevant thread + local project context
             |
             v
work locally -> draft at most one material coordination message
             |
             v
update obligation ledger -> validate -> send through connector -> persist cursor/receipt
```

## Capability Patterns

### Polling or Scheduled Loop

Persist the last Slack timestamp locally. On each run, read newer messages, expand only relevant
threads, and advance the coordination cursor after processing. Respect Slack's `Retry-After` response and do not
overlap polls. A two-to-five-minute interval is a reasonable trial default, not a protocol rule.

### Event Subscription

Acknowledge delivery before running the agent, enqueue work, and deduplicate on `event_id`. Subscribe
only to the pilot channel where possible. Event delivery changes latency, not message semantics.

### Interactive Connector

Give the connector the charter, logical participant identifier, unread messages, and wake prompt.
The connector may send directly when authorized. If it cannot persist a cursor, provide the last
processed timestamp in the next invocation.

### Read-Only or Human-Ferried

Have the agent emit a protocol-valid draft. A human or authorized local tool may paste it unchanged.
The declared `from` is the collaboration identity; Slack's visible sender remains the transport
identity.

## Local State

Each participant owns its state. At minimum retain:

```yaml
channel: <Slack channel ID or URL>
participant: dev-a/frontend
protocol: agent-collab/v0
cursors:
  coordination: <last processed Slack message timestamp or event ID>
  learning: <last message or reply timestamp reviewed for trial learnings>
learning_cursor_audited_at: <timestamp of the completed review>
active_claims:
  primevue-overlay:
    checkpoint: 2026-09-30T14:30:00Z
obligation_ledger: ./agent-collab-obligations.md
```

Do not put tokens, private reasoning, or full transcripts in shared messages or portable state.
The two cursors are independent. Advance `coordination` after an operational message is processed.
Advance `learning` only after every message and reply through that timestamp has been reviewed and
any accepted finding is written to the durable learning log. Never advance either cursor past a
failed or partial fetch.

## Dispatch and Coordinator Boundaries

Treat delivery as observable states: `requested`, `dispatched` to an exact agent/session, `started`,
and `verified`. “Relayed” alone is not a useful handoff state. Cross-host handoffs name the receiving
agent/session and destination, then wait for acknowledgement.

A coordinator allocates work, preserves scope, and tracks completion. It should delegate substantive
implementation, research, or QA when local capacity exists instead of becoming the default worker.

## Optional Lifecycle Hooks

Local harnesses may inject unread collaboration context before a turn and validate an outbound draft
before sending. These are optional integration points, not protocol requirements. Do not install a
global hook or autonomous posting path until the local operator has authorized it and verified its
scope.

A reminder hook may surface open obligations owned by the participant. An optional auditor may flag
messages that appear to create or settle an obligation without a corresponding ledger change. Keep
both advisory: they may not assign work, mark an obligation reconciled, or post autonomously unless
the operator separately authorizes that behavior.

Invoke the bundled validator with `python3 scripts/validate-message.py`; do not depend on copied files
retaining their executable bit. Pass `--inherited-context` only for a Slack reply whose parent supplies
the unchanged protocol envelope. A local loop should also honor the charter's people-only escape hatch.
