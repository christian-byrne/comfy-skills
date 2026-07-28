# Group 2: Self Code Review — Detailed Checks

**Dispatch as parallel subagents.** Each reviews the diff from a different angle.

```bash
# Get the diff for review context
DIFF=$(git diff $(git merge-base HEAD main)..HEAD)
CHANGED_FILES=$(git diff --name-only $(git merge-base HEAD main)..HEAD)
```

| #   | Review Angle           | What It Checks                                                                        |
| --- | ---------------------- | ------------------------------------------------------------------------------------- |
| 20  | **Architecture**       | SOLID violations, package boundary crossings, import graph health                     |
| 21  | **Bugs & regressions** | Logic errors, error handling gaps, git blame risk (lines that were previous bugfixes) |
| 22  | **Security**           | OWASP patterns, secrets exposure, injection risks, auth gaps                          |
| 23  | **Performance**        | N+1 queries, memory leaks, cold start impact, algorithmic complexity                  |
| 24  | **Test quality**       | Are new tests meaningful or just coverage padding? Missing edge cases?                |
| 25  | **Diff minimality**    | Did we change more than necessary? Leftover debug code? Console.logs? TODO comments?  |

**If `.agents/checks/` exists in this repo**, use those check files instead — they're more specific. If your `AGENTS.md` maps checks to file patterns (e.g. a "Dispatch When" column), dispatch relevant checks based on changed files that way.
