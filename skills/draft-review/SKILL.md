---
name: draft-review
description: 'Lighter architectural review for draft external PRs. Focuses on direction, structure, and major alignment issues — not line-by-line nits. Use when assigned to review a draft PR from another contributor, or when asked to do an early review of a WIP PR.'
interaction: hybrid
type: leaf
synergies:
  requires: []
  enhances: []
  conflicts: []
  domain: [review, pr]
---

# Draft Review

Early-stage architectural review for draft/WIP PRs. Catches major directional issues before the contributor invests more time. NOT a full review — save line-by-line feedback for when the PR is marked ready.

## When to Use

- Draft PR from an external contributor assigned to you for review
- User says "do a quick review of this draft", "early feedback on this WIP"
- PR is marked as draft AND you're in assignees/reviewRequests
- An automated queue or dispatcher routes a draft external PR here

## When NOT to Use

- PR is marked ready for review → do a full review instead of this lighter pass
- PR is your own draft → skip (you know the direction)
- PR is from an onsite candidate → skip entirely

## Workflow

### 1. Gather Context

```bash
PR_NUMBER=<N>
REPO=$(gh pr view "$PR_NUMBER" --json repository --jq '.repository.nameWithOwner')
BRANCH=$(gh pr view "$PR_NUMBER" --json headRefName -q .headRefName)
AUTHOR=$(gh pr view "$PR_NUMBER" --json author -q .author.login')

# Get the diff stats and body
gh pr view "$PR_NUMBER" --repo "$REPO" --json body,title,labels,additions,deletions
gh pr diff "$PR_NUMBER" --repo "$REPO" | head -500
```

### 2. Checkout Locally

```bash
# Use worktree if available, otherwise shallow clone
wt-continue "$REPO_NAME" "$BRANCH" 2>/dev/null || {
  gh pr checkout "$PR_NUMBER"
}
git fetch origin
git reset --hard "origin/$BRANCH"
```

### 3. Architectural Scan

Focus ONLY on these high-signal areas:

| Check                    | What to look for                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------ |
| **File placement**       | Are new files in the right directories? Does the structure follow existing patterns?                   |
| **Component boundaries** | Are new components at the right abstraction level? Correct separation of concerns?                     |
| **API shape**            | Do new interfaces/types/props align with existing patterns?                                            |
| **State management**     | Is state in the right place? Using the right store/composable patterns?                                |
| **Dependencies**         | Any new dependencies that conflict with existing choices?                                              |
| **Approach alignment**   | Is the overall approach what we'd want, or is there a fundamentally different way this should be done? |

**Do NOT check:** formatting, naming nits, missing tests, documentation, edge cases, error handling minutiae. These are for the full review when the PR is ready.

### 4. Verdict

Classify the draft as one of:

| Verdict                           | Meaning                                            | Action                                                         |
| --------------------------------- | -------------------------------------------------- | -------------------------------------------------------------- |
| **🟢 Direction looks good**       | Architecture aligns, contributor should keep going | Post encouraging comment with any minor suggestions            |
| **🟡 Needs course correction**    | Some structural issues but salvageable             | Post specific architectural feedback with suggestions          |
| **🔴 Fundamental rethink needed** | Wrong approach, would need major rewrite           | Post clear explanation of why and suggest alternative approach |

### 5. Post Feedback

Leave a SINGLE top-level PR comment (not inline review comments). Draft PRs don't need scattered inline feedback — they need a cohesive architectural assessment.

Format:

```
## Draft Review — Architectural Feedback

**Verdict: 🟢/🟡/🔴**

### What's looking good
- [list positives]

### Architectural concerns (if any)
- [list concerns with specific suggestions]

### Suggested direction
[one paragraph on recommended next steps]

---
*This is an early-stage review focused on direction — detailed line-by-line feedback will come when the PR is marked ready for review.*
```

Post via:

```bash
gh pr comment "$PR_NUMBER" --repo "$REPO" --body "$(cat review-comment.md)"
```

## Rules

1. **One comment, not many** — draft PRs get a single cohesive comment, not scattered inline reviews
2. **Architecture only** — no nits, no formatting, no test coverage comments
3. **Be encouraging** — the contributor chose to share early, reward that with helpful direction
4. **Don't request changes** — use a comment, not a formal review with "changes requested" status
5. **Keep it short** — 10-20 lines max. This is early guidance, not a thesis.
