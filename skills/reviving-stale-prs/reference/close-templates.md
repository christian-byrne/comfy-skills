# Close & Ask Author Templates

> **Note:** Close templates (Steps 11–12) intentionally use a warm human tone — they're
> directed at external contributors. The Ask Author template (Step 13) uses a terser,
> status-first tone since it reads as automation-posted.

## Push and Handoff (Step 11)

Push the branch and monitor CI to completion:

```bash
git push origin HEAD
gh pr checks "$PR_NUMBER" --repo "$REPO" --watch
```

If CI fails, fix the failure, re-run the affected quality gate locally, push again, and re-watch. Note in your own tracking that this is a revived stale PR — rebased onto main, quality gates passed, self-reviewed.

## Close Templates (Step 12)

### Superseded by merged work

```bash
gh pr close "$PR_NUMBER" --repo "$REPO" --comment "Closing this PR — the changes here have been superseded by #<N1>, #<N2>, and #<N3>, which landed on main and cover the same scope.

Specifically:
- <what #N1 addressed>
- <what #N2 addressed>
- <what #N3 addressed>

Thank you for the contribution! If you'd like to revisit this, feel free to open a new PR against the current main branch."
```

### Architectural incompatibility

```bash
gh pr close "$PR_NUMBER" --repo "$REPO" --comment "Closing this PR — the codebase has undergone significant restructuring since this was opened. Specifically, <describe refactors: file moves, directory reorganization, API changes> (see #<refactor_PR>), making a rebase impractical.

The feature/fix itself may still be valuable — if you'd like to re-implement it against the current codebase, feel free to open a new PR. Happy to help with guidance on the new structure."
```

### Team decided against approach

```bash
gh pr close "$PR_NUMBER" --repo "$REPO" --comment "Closing this PR — after reviewing the project history, this approach was discussed in #<issue/discussion> and the team decided against it because <reason>.

Thank you for the contribution! If circumstances have changed or you have a different approach, feel free to open a new discussion."
```

### Author unresponsive + adopted

```bash
gh pr close "$PR_NUMBER" --repo "$REPO" --comment "Closing this PR in favor of #<new_PR>, which picks up this work with a rebase onto current main and addresses the outstanding review feedback.

Thank you for the original contribution, @<author>! Your work is credited in the new PR."
```

## Ask Author (Step 13 — Last Resort)

Keep this terse and factual: no greeting, lead with a status marker, state facts.

```bash
gh pr comment "$PR_NUMBER" --repo "$REPO" --body "⚠️ Stale PR triage — <N> days old.
State: <has conflicts / unresolved comments / etc.>
Question: <specific question from verdict>

Options:
- Continue: <rebasing guidance>
- Hand off: we adopt, rebase, push
- No response in 7d: we adopt or close if superseded"
```
