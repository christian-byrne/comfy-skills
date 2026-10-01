# Harness Integration

The common contract is the skill and visible message envelope, not a shared process. Each developer
keeps their existing loop and Slack access method.

```text
schedule, event, or human prompt
             |
             v
read after local cursor -> filter relevant/duplicate/self messages
             |
             v
run or resume local agent with charter + relevant thread + local project context
             |
             v
work locally -> draft at most one material coordination message
             |
             v
validate -> send through available connector -> persist cursor/receipt
```

## Capability Patterns

### Polling or Scheduled Loop

Persist the last Slack timestamp locally. On each run, read newer messages, expand only relevant
threads, and advance the cursor after processing. Respect Slack's `Retry-After` response and do not
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
cursor: <last processed Slack timestamp or event ID>
active_claims:
  primevue-overlay:
    checkpoint: 2026-09-30T14:30:00Z
```

Do not put tokens, private reasoning, or full transcripts in shared messages or portable state.

## Optional Lifecycle Hooks

Local harnesses may inject unread collaboration context before a turn and validate an outbound draft
before sending. These are optional integration points, not protocol requirements. Do not install a
global hook or autonomous posting path until the local operator has authorized it and verified its
scope.
