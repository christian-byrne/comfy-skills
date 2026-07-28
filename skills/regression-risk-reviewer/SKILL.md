---
name: regression-risk-reviewer
description: 'Detects potential regressions in PR diffs by analyzing git blame history. Use when reviewing PRs or before submitting your own code to catch lines that were previously bugfixes.'
interaction: autonomous
type: leaf
---

# Regression Risk Reviewer

Analyzes changed lines in a PR or local branch to detect if you're modifying/deleting code that was part of a previous bugfix.

## When to Use

- Reviewing someone else's PR
- Self-reviewing your own branch before submitting
- Asked to "check for regressions" or "review this diff for risks"

## Workflow

### 1. Identify the Diff

For a local branch:

```bash
git diff main...HEAD --unified=0
```

For a PR:

```bash
gh pr diff <PR_NUMBER> --patch
```

### 2. Extract Changed Line Ranges

Parse the diff to identify files and line ranges being modified or deleted. Focus on the **pre-image** (lines being removed or changed, marked with `-`).

### 3. Blame the Original Lines

For each file with changes, run blame on the base branch for the affected line ranges:

```bash
git blame <base-branch> -L <start>,<end> -- <file>
```

### 4. Analyze Blame Commits

For each commit found in the blame output, check for bugfix signals:

**Commit message patterns (case-insensitive):**

- `fix`, `bug`, `patch`, `hotfix`
- `regression`, `revert`
- `issue`, `closes #`, `fixes #`
- `broken`, `crash`, `error`, `fail`

**Retrieve commit details:**

```bash
git show --stat --format="%H%n%s%n%b" <commit-sha>
```

### 5. Check for Churn

Lines changed multiple times recently indicate fragility:

```bash
git log --oneline -n 10 -- <file>
```

Flag files with 3+ changes in last 6 months on the same lines.

### 6. Surface Context

For flagged commits, try to find linked issues/PRs:

```bash
# If commit message references a PR
gh pr view <pr-number> --json title,body,url

# Check for associated issues
gh issue view <issue-number> --json title,body,url
```

## Output Format

Group findings by risk level:

```markdown
## 🔴 High Risk (Bugfix Being Modified)

### file.ts:42-48

- **Original fix commit:** abc1234 - "Fix null pointer when user is undefined"
- **Fixed on:** 2024-08-15
- **Context:** Closes #142 - users reported crash on logout
- **Current change:** These lines are being deleted/rewritten

---

## 🟡 Medium Risk (High Churn Area)

### api.ts:100-115

- Changed 4 times in last 3 months
- Last change: def5678 - "Fix race condition in auth flow"

---

## 🟢 Low Risk (No Bugfix History Detected)

- components/Button.tsx (lines 10-20)
- utils/format.ts (lines 5-8)
```

## Heuristics

**Prioritize:**

- Recent fixes (last 6 months) over old ones
- Deleted lines over modified lines
- Multiple-fix chains ("fix of a fix")

**Deprioritize:**

- Pure refactors/renames (check if commit only moves code)
- Formatting changes
- Comment-only changes

## Edge Cases

- **Renamed files:** Use `git log --follow` to track history
- **Squashed commits:** May obscure history; note when detected
- **Large PRs:** Limit analysis to first 20 files, warn user about scope

## Example Invocation

```
Review this PR for regression risks: https://github.com/org/repo/pull/123
```

Or for local branch:

```
Check my current branch for regression risks before I submit
```
