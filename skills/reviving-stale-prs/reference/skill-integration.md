# Related Practices Reference

## Where Each Practice Applies

| Practice                           | Used For                                            | When                                   |
| ---------------------------------- | --------------------------------------------------- | -------------------------------------- |
| Quality gates                      | Running format, lint, typecheck, test               | Step 8                                 |
| Push and CI monitoring             | Pushing, polling CI, fixing failures                | Step 11 (handoff)                      |
| Addressing review comments         | Implementing review feedback as individual commits  | Step 10 (if unresolved threads exist)  |
| Resolving review threads           | Marking threads resolved after fixes are pushed     | After push and CI monitoring completes |
| Full code review of the PR content | If the user wants a thorough review before deciding | Optional, before Step 4                |
| Verdict/decision reasoning         | Confidence thresholds, relevance checks             | Step 2 & 4 verdict reasoning           |
| Complexity assessment              | Sizing the change to judge revival effort           | Step 4 size/scope evaluation           |

## Best Practices

- **Addressing review comments:** one commit per review comment, always include the comment URL in the commit message. Never batch.
- **Push and CI monitoring:** cap fix iterations (e.g. 3) before escalating. Never redo skill-specific work in the loop — only fix CI and new review comments. Always self-review before every push.
- **Verdict reasoning:** process oldest PRs first. Verify before acting. Escalate uncertainty. Be idempotent. Use confidence thresholds (>80% act, 50-80% flag, <50% escalate).
- **Resolving review threads:** only resolve your own and bot threads. Verify the code before resolving. Be concise in replies.
- **Full PR review:** always check out the branch locally — never rely on the API alone to read file contents. Batch comments into a single review. Get human approval before posting.
- **Batch triage:** when triaging multiple PRs, dispatch independent checks in parallel, compile and deduplicate results, and present a triaged summary for human decision.
