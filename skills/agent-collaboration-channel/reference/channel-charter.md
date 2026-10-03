# Channel Charter

A human creates the channel and posts or pins this charter before agents participate.

```markdown
# Agent collaboration charter

- Collaboration mode: <same-feature | bounded-assistance>
- Outcome: <one jointly owned result, review, approval, QA result, or unblock>
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

For `same-feature`, both sides may negotiate implementation and review ownership. For
`bounded-assistance`, name the requested review, QA, approval, or unblock boundary so the assisting
agent does not become a second coordinator. Preserve distinct local context by default; share only
the evidence needed for the current decision.

If a connector cannot create, join, read, or post to the channel, that is a local capability issue.
The human may invite it, choose another connector, or ferry messages without changing the charter.

When participants need a people-only or meta discussion inside an agent-active channel, agree on a
visible escape hatch such as a `:no-bots:` reaction. Local loops skip that message and its thread
unless a human explicitly addresses them.
