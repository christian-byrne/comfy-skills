# Revival Steps Reference

## 5. Checkout the Branch

```bash
BRANCH=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json headRefName -q .headRefName)
REPO_NAME=$(echo "$REPO" | cut -d'/' -f2)

# A worktree keeps this isolated from your main checkout.
git fetch origin "$BRANCH"
git worktree add "../${REPO_NAME}-${BRANCH//\//-}" "origin/$BRANCH"
cd "../${REPO_NAME}-${BRANCH//\//-}"
```

(If you use a worktree-management tool, its checkout command works here too — a plain `git checkout -b "$BRANCH" "origin/$BRANCH"` in your existing clone is also fine if you don't need isolation.)

Confirm: `pwd && git branch --show-current && git log --oneline -3`

## 6. Rebase onto Main

Always use non-interactive mode to prevent editor hangs in agent environments:

```bash
git fetch origin main
GIT_EDITOR=true GIT_SEQUENCE_EDITOR=true git rebase origin/main
```

**If conflicts arise:**

```
⚠️ Merge conflicts during rebase.

Conflicting files:
<list from git status>

Conflict complexity: <TRIVIAL | MODERATE | SEVERE>
- TRIVIAL: whitespace, import order, lock files
- MODERATE: logic conflicts in 1-3 files, resolvable with context
- SEVERE: structural changes, file moves, >5 conflicting files

Options:
A) Resolve conflicts now (recommended for trivial/moderate)
B) Abort rebase — PR may not be worth the effort
C) Ask user for guidance
```

Resolve conflicts, then `GIT_EDITOR=true git rebase --continue`. Repeat until clean.

## 7. Re-evaluate Diff After Rebase (Re-Triage Checkpoint)

```bash
git diff origin/main --stat
git diff origin/main
```

Check that the rebased diff still makes sense:

- Did the rebase silently break logic? (e.g., code now references deleted functions)
- Did the diff size change significantly? (new code on main may overlap)
- Are there files in the diff that shouldn't be there? (rebase artifacts)

**Re-triage checkpoint:** If the rebase dramatically reduced the diff (main absorbed most of the changes), or if the remaining diff is broken/nonsensical, recommend closing instead of pushing. Compare the original PR's changed-file count and line count against the post-rebase diff — if >70% of the changes are now no-ops, the PR's value is likely gone.

If the rebase produced a broken or nonsensical result, report to user and suggest closing.

## 8. Quality Gates

**Note on fork PRs:** CI workflows often fail on fork PRs due to read-only `GITHUB_TOKEN` permissions. For fork PRs, always run quality gates locally rather than relying on CI. Work on the branch in your worktree/checkout and run checks locally before pushing.

Run the project's standard quality gates — format, lint, typecheck, and test — until they all pass. If the repo ships its own quality-check script, use it; otherwise run the individual commands directly, e.g.:

```bash
pnpm format && pnpm lint && pnpm typecheck && pnpm test
```

(Substitute the equivalent commands for the repo's actual toolchain.)

If checks fail:

1. Auto-fix what can be auto-fixed (format, lint:fix)
2. Fix remaining issues manually
3. Commit fixes: `git commit -am "fix: quality gate fixes after rebase"`
4. Re-run quality checks to confirm all pass

**Do NOT proceed to push until all quality gates pass.**

## 9. Self-Review Pass

```bash
git diff origin/main..HEAD --stat
git diff origin/main..HEAD
```

Verify:

- [ ] No debug code, console.logs, or TODO hacks
- [ ] No unintended file changes or rebase artifacts
- [ ] Changes are minimal and focused
- [ ] Commit messages are clear
- [ ] Code still makes sense in the context of current main

## 10. Address Existing Review Comments (If Any)

**Handle sequentially:** If the PR needs both rebasing AND review comment fixes, always finish the rebase first (steps 6–9), then address review comments. Do not try to do both in one pass — rebase can move/delete the lines that comments reference.

Check for unresolved review threads:

```bash
UNRESOLVED=$(gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          path
          line
          comments(first: 5) {
            nodes {
              body
              author { login }
            }
          }
        }
      }
    }
  }
}' -f owner="$OWNER" -f repo="$REPO_NAME" -F pr="$PR_NUMBER" \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)')
```

If there are unresolved threads with actionable feedback:

- Present them to the user
- If the user approves, address them one commit per comment, with the comment URL in each commit message

If the comments are stale (reference code that no longer exists), note them for resolution later.
