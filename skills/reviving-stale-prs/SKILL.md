---
name: reviving-stale-prs
description: 'Revives stale GitHub PRs by rebasing, running quality gates, assessing viability, and presenting a verdict. Use when asked to revive a PR, check if an old PR is worth merging, or bring a stale PR up to date.'
interaction: hybrid
type: leaf
---

# Reviving Stale PRs

Evaluates and revives stale pull requests. Ordered for early bail-out: cheapest checks first, expensive work only if the PR is worth saving.

## Prerequisites Check

```
gh auth: !`gh auth status 2>&1 | head -2`
worktree-utils: !`which wt-continue 2>/dev/null && echo "✅ available" || echo "⚠️ not found"`
```

## When to Use

- User says "revive this PR", "is this PR worth merging", "bring this PR up to date"
- User provides a stale/old PR URL and asks to evaluate it
- During backlog grooming of open PRs
- When a PR has been open for weeks/months without activity

## Prerequisites

- GitHub CLI authenticated: `gh auth status`
- A way to check out the PR branch locally — a worktree-management tool such as `git-worktree-utils` (checked above) works well, or plain `git worktree add` / `git checkout`
- Write access to the repository (for approval/push)

## Workflow

### Phase 1: Triage (Bail Out Early If Not Worth It)

Do ALL of Phase 1 before touching any code. The goal is to decide whether to invest time in reviving.

When triaging multiple PRs, dispatch parallel subagents (one per PR) for steps 1–4.

> **Detailed commands:** See `reference/triage-commands.md` for all bash commands and checks.

1. **Fetch PR metadata** — age, author activity, size, review state, draft/fork status
2. **Check for superseding work** — code existence, already-landed PRs (merged AND closed), semantic overlap analysis, deprecation/architectural shifts, team decisions. Bail out if superseded, incompatible, or explicitly rejected.
3. **Check author engagement** — last activity, response to reviews, account status. Don't bail on this alone — small fixes from external contributors are often worth adopting.
4. **Assess viability and present verdict** (see Verdict Template below)

### Confidence Thresholds

| Confidence | Action                                                                   |
| ---------- | ------------------------------------------------------------------------ |
| >80%       | Act on the verdict (REVIVE or CLOSE)                                     |
| 50–80%     | Act but flag for review — explain the uncertainty                        |
| <50%       | ASK AUTHOR only as last resort, after exhausting all autonomous research |

**ASK AUTHOR is a last resort, not a default.** Before recommending ASK AUTHOR, you MUST have:

- ✅ Checked for superseding merged AND closed PRs
- ✅ Compared diffs of candidate superseding PRs against this PR
- ✅ Verified the specific files/functions still exist on `main`
- ✅ Searched closed issues for team decisions about this feature area
- ✅ Checked architectural compatibility (file moves, API changes)
- ✅ Checked the author's recent GitHub activity

**Bias toward ADOPT over ASK AUTHOR.** If the PR is good quality and the only unknown is whether the author wants to continue, prefer adopting. For same-repo branches, push directly to the author's branch. For fork PRs, create a new branch and open a new PR citing the original.

### Verdict Template

```
## PR Revival Assessment: #<N> — <TITLE>

**Key finding:** <ONE-LINE BOLD SUMMARY of the most important finding>

**Author:** @<author> | **Age:** <N> days | **Last activity:** <date>
**Size:** +<additions> -<deletions> across <files> files
**Fork:** <Yes/No> | **Confidence:** <N%>

### Superseding Work
- <findings from step 2, with specific PR numbers/SHAs as evidence>
- <or "None found — no merged or closed PRs overlap with this change">

### Remaining Value
- <what unique value this PR still provides that hasn't landed elsewhere>
- <or "None — fully superseded by #X, #Y">

### Author Engagement
- <findings from step 3>

### Unresolved Review Comments
- <count> unresolved threads from <reviewers>
- <summary of blocking vs non-blocking>

### Verdict: <REVIVE | CLOSE | ADOPT | ASK AUTHOR>

<reasoning — must cite specific evidence: PR numbers, commit SHAs, discussion links>

<If ASK AUTHOR: include the specific question to ask and what the answer changes>

**Options:**
(a) Revive — rebase, fix quality gates, push, and prepare for review
(b) Close — with comment explaining why
(c) Adopt — take over the PR (push to their branch, or new PR if fork)
(d) Ask author — with specific question (last resort)
```

#### Batch Summary Table

When triaging multiple PRs, present a consolidated summary after individual reports:

```
## Batch Triage Summary

| PR | Title | Verdict | Confidence | Key Finding |
|----|-------|---------|------------|-------------|
| #123 | Fix widget alignment | CLOSE | 95% | Superseded by #456 |
| #124 | Add dark mode toggle | REVIVE | 85% | Still needed, trivial conflicts |
| #125 | Refactor auth flow | ADOPT | 75% | Author inactive 8mo, PR is solid |

Process order: CLOSE first, then REVIVE, then ADOPT, then ASK AUTHOR.
```

**Wait for user decision before proceeding.** Do NOT revive without approval.

---

### Phase 2: Revive (Only After User Approves)

> **Detailed steps:** See `reference/revival-steps.md` for all commands, conflict resolution, and review comment handling.

5. **Checkout the branch** — enter a worktree (or fresh checkout) for the branch
6. **Rebase onto main** — non-interactive (`GIT_EDITOR=true GIT_SEQUENCE_EDITOR=true`). If conflicts arise, classify as TRIVIAL/MODERATE/SEVERE and decide whether to continue.
7. **Re-evaluate diff after rebase** — if >70% of changes are now no-ops, recommend closing instead. Check for broken logic, rebase artifacts.
8. **Quality gates** — run the project's format/lint/typecheck/test commands (or its own quality-check script, if it has one). For fork PRs, run locally (CI often fails on forks). All gates must pass before pushing.
9. **Self-review pass** — verify no debug code, no rebase artifacts, changes are minimal and focused.
10. **Address existing review comments** — always rebase first, then address comments. One commit per comment, with the comment URL in the commit message.

---

### Phase 3: Push and Handoff

> **Templates:** See `reference/close-templates.md` for push handoff, all 4 close templates, and ask-author template.

11. **Push and monitor** — push the branch and watch CI to completion, fixing any failures
12. **Close** (if verdict was close) — use the template matching the reason: superseded, architectural incompatibility, team decided against, or author unresponsive + adopted
13. **Ask author** (last resort) — comment with current state, specific question, and what happens based on their answer (adopt after 7 days if no response)

## Related Practices

> **Full detail:** See `reference/skill-integration.md`

- **Quality gates (step 8):** run the project's format/lint/typecheck/test commands until clean.
- **Push and CI monitoring (step 11):** push, poll CI to completion, fix failures, and repeat — self-review before every push.
- **Addressing review comments (step 10):** one commit per comment, comment URL in the message, never batched.
- **Resolving review threads:** after fixes are pushed, resolve your own and bot threads only, once the code is verified.
- **Verdict reasoning:** process oldest PRs first, verify before acting, escalate genuine uncertainty, use the confidence thresholds above.

## Rules

1. **Triage before touching code** — complete Phase 1 before any checkout/rebase
2. **Always present verdict to user** — never revive or close without human approval
3. **Check for superseding work first** — this is the #1 reason stale PRs should close
4. **Search closed PRs too** — a closed attempt at the same fix is critical context
5. **Exhaust autonomous research before ASK AUTHOR** — ASK AUTHOR is a last resort, not a default
6. **Every verdict needs evidence** — cite specific PR numbers, commit SHAs, or discussion links
7. **Rebase, don't merge** — keep history clean
8. **Use non-interactive git** — always set `GIT_EDITOR=true GIT_SEQUENCE_EDITOR=true` for rebase
9. **Re-triage after rebase** — if the diff shrunk dramatically, recommend closing
10. **Rebase first, review comments second** — never mix the two in one pass
11. **Quality gates must pass** before pushing
12. **Self-review after rebase** — rebase can silently break things
13. **One commit per review fix** — cite the comment URL in the commit message
14. **Close politely with context** — use the specific template that matches the reason, cite PRs/issues
15. **Don't force-push** unless the branch was already force-pushed by the author
16. **Use `author.login` not display names** — display names don't resolve in GitHub API calls
17. **Fork PRs can't be pushed to** — for adopted fork PRs, create a new branch and open a new PR citing the original
18. **Run local quality gates for fork PRs** — fork CI often fails due to `GITHUB_TOKEN` permissions
19. **Report the PR link at the end** — always give the user the URL for manual merge
