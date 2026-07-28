# Group 6: Follow-up Categories — Exhaustive Checklist

For each category, scan the diff, session context, and conversation history. **Create issues only for real gaps — don't fabricate follow-ups.** But DO NOT skip a category just because it feels minor — if it crossed your mind, it needs tracking.

| #   | Category                             | What to Look For                                                                          |
| --- | ------------------------------------ | ----------------------------------------------------------------------------------------- |
| 51  | **Future unit tests**                | Untested branches, edge cases mentioned in comments, complex functions with no test       |
| 52  | **Future integration tests**         | Cross-service interactions introduced but not integration-tested                          |
| 53  | **Future E2E tests**                 | User-facing flows changed but no E2E coverage                                             |
| 54  | **Cleanup / refactor**               | Tech debt introduced or noticed — complexity hotspots, duplication                        |
| 55  | **Wiring follow-ups**                | Connections to other systems not yet made — event handlers, webhooks, notifications       |
| 56  | **Performance follow-ups**           | Known slow paths to optimize later — N+1 queries, missing indexes, unoptimized loops      |
| 57  | **Monitoring / alerting**            | New failure modes that need alerts, dashboards, or health checks                          |
| 58  | **Feature flags**                    | Anything that should be gated for gradual rollout                                         |
| 59  | **Migration / rollback**             | If deploying — what's the rollback plan? Documented?                                      |
| 60  | **Deferred ideas**                   | Ideas that came up during implementation — backlog or issue                               |
| 61  | **Risks / outstanding concerns**     | Known risks, edge cases that might bite later, assumptions that could be wrong            |
| 62  | **Verification checkpoints**         | "Check back in N days to verify this actually works in production" — schedule a follow-up |
| 63  | **Future improvement opportunities** | Refactors, optimizations, or enhancements noticed but out of scope                        |
| 64  | **Open discussions / decisions**     | Architectural questions, design debates, or trade-offs that need broader input            |
| 65  | **Dependency updates**               | Libraries, tools, or upstream changes that this work depends on or should track           |

## Issue / Discussion Creation

For each real follow-up found, create a GitHub issue:

```bash
gh issue create \
  --title "follow-up: {category} — {description}" \
  --body "{context, file paths, what needs to happen}" \
  --label "follow-up"
```

For open-ended discussions or architectural questions, create a GitHub Discussion instead:

```bash
gh discussion create \
  --title "{topic}" \
  --body "{context and framing}" \
  --category "Ideas"
```

**Use sub-issues** when multiple follow-ups relate to the same parent ticket. Link with `Part of #NNN` in the body.

**Present all proposed issues to the user before creating them.** The user decides which are worth tracking.
