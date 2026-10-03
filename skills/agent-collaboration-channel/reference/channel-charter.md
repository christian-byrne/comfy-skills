# Channel Charter

A human creates the channel and posts or pins this charter before agents participate.

```markdown
# Agent collaboration charter

- Outcome: <one jointly owned result>
- In scope: <repositories, components, or decision surface>
- Out of scope: <important boundaries>
- Human owners: <people who may steer or close the channel>
- Participants: <stable logical identifiers, independent of Slack identity>
- Durable record: <issue, project, plan, or repository>
- Obligation ledger: <Markdown path or durable URL, or "none" for a short synchronous slice>
- Learning log: <durable path or URL, or "none" when no protocol trial is running>
- Posting authorization: participants may post agent-collab/v0 messages in this channel only
- Starts: <timestamp>
- Closes when: <observable condition or date>
- Protocol: agent-collab/v0
```

Keep one channel to one collaboration slice: a dependency, integration seam, or jointly owned
outcome that should finish in hours or days. A project may use several slices. Do not reuse an old
channel for unrelated work; its prior authorization and participant assumptions may no longer hold.

If a connector cannot create, join, read, or post to the channel, that is a local capability issue.
The human may invite it, choose another connector, or ferry messages without changing the charter.

When participants need a people-only or meta discussion inside an agent-active channel, agree on a
visible escape hatch such as a `:no-bots:` reaction. Local loops skip that message and its thread
unless a human explicitly addresses them.
