---
name: final-sweep
description: 'Lands the PR (rebase, fix conflicts, CI fix loop, merge) then runs a comprehensive completion sweep. Verifies code quality, tests, docs, git hygiene, CI, follow-ups, and more — then prints all-clear. Use when asked to do a final sweep, verify everything is done, check if anything is left, run completion checks, or wrap up.'
interaction: hybrid
type: leaf
---

## Current State

```
PR & CI: !`bash skills/final-sweep/scripts/detect-done.sh 2>/dev/null || echo '(not available)'`
```

# Final Sweep — Are We Truly Done?

A user-invokable completion checklist that verifies every dimension of "done" before declaring work complete. Runs deduplication-aware checks across 8 groups, creates follow-up issues for future work, and prints a verified all-clear signal.

**This skill is generalized** — it works for any repo, any language, any framework. Checks auto-detect what's relevant based on the repo's tooling.

## When to Trigger

**User-invokable only.** Never auto-trigger. Activate on:

- "Final sweep" / "sweep" / "are we done?"
- "Is there anything left to do?"
- "Wrap up" / "wrap this up"
- "Final check" / "completion check"
- "Make sure everything is done"

## Phase -1: Land the PR (Rebase → Fix CI → Merge)

**Before running any sweep checks, land the PR.** Non-interactive — don't ask "should I rebase?" or "should I merge?" — just do it.

1. **Rebase onto main:** `git fetch origin main && git rebase origin/main` — resolve conflicts automatically (preserve both sides where possible; for append-only files keep both entries)
2. **Quality gates + push:** Auto-fix (`pnpm format; pnpm lint:fix`), verify (`pnpm format:check && pnpm lint && pnpm typecheck`), then `git push --force-with-lease`
3. **Wait for CI:** Poll with `gh pr checks "$PR_NUMBER" --watch` or 60s loop
4. **Fix CI failures (max 3 iterations):** Read logs (`gh run view <id> --log-failed`), fix, commit, push, re-poll
5. **Merge:** `gh pr merge "$PR_NUMBER" --squash --delete-branch` then `git checkout main && git pull`

**Skip conditions:** No PR → skip to Phase 0. Already merged → skip to Phase 0. User says "don't merge" → skip step 5 only.

---

## Phase 0: Deduplication — What's Already Done?

Before running ANY check, detect what's already been completed by CI, other skills, or recent runs.

```bash
# CI status
PR_NUMBER=$(gh pr list --head "$(git branch --show-current 2>/dev/null)" --json number -q '.[0].number' 2>/dev/null)
[ -n "$PR_NUMBER" ] && gh pr checks "$PR_NUMBER" 2>/dev/null

# Recent commits & tooling detection
git log --oneline -10 2>/dev/null | grep -iE "fix|lint|format|test|chore|docs" || true
[ -f package.json ] && echo "node" ; [ -f Cargo.toml ] && echo "rust"
[ -f pyproject.toml ] && echo "python" ; [ -d .github/workflows ] && echo "github-actions"
```

Build a **skip list**, present to user: which checks are already green (CI) or recently run (< 10 min). If ALL green, skip to Phase 8.

---

## Group 1: Code Quality Gates (19 checks, parallel subagents)

Auto-detect tooling (Node/Rust/Python/Shell/Terraform/Docker/Actions) and run applicable checks: tests, lint, format, typecheck, stylelint, shellcheck, actionlint, SQL format, terraform fmt/validate, JSON/YAML lint, clippy, rust fmt, ruff, security scan, dependency audit, license compliance, dead code, bundle size.

📖 **Full check table & auto-detection bash:** `reference/quality-gate-checks.md`

---

## Group 2: Self Code Review (6 angles, parallel subagents)

Review the diff from 6 angles: Architecture, Bugs & regressions, Security, Performance, Test quality, Diff minimality. If `.agents/checks/` exists, use those instead.

📖 **Full review angle table:** `reference/self-review-checks.md`

---

## Group 3: Documentation (8 checks, parallel subagents)

| #   | Check                 | How to Detect Need                                                          |
| --- | --------------------- | --------------------------------------------------------------------------- |
| 26  | **README updated**    | Public API or behavior changed → README should mention it                   |
| 27  | **AGENTS.md**         | New dir or patterns → needs AGENTS.md; existing ones → verify still current |
| 28  | **CHANGELOG**         | User-facing changes → entry needed                                          |
| 29  | **API docs**          | Endpoint signatures changed → OpenAPI/JSDoc need updating                   |
| 30  | **Migration guide**   | Breaking changes → PR body must explain upgrade path                        |
| 31  | **Architecture docs** | Structural changes → ADRs/diagrams may need updating                        |
| 32  | **Inline docs**       | Complex functions (>10 cyclomatic or >50 lines) need comments               |
| 33  | **Skill docs**        | `skills/**` changed → verify description/triggers/examples                  |

Only flag items where the diff actually necessitates doc changes.

---

## Group 4: Git Hygiene (9 checks, sequential)

| #   | Check                            | Action on Fail              |
| --- | -------------------------------- | --------------------------- |
| 34  | **No merge conflicts**           | Rebase needed               |
| 35  | **Rebased on target**            | Rebase if behind            |
| 36  | **No stranded worktrees**        | Warn user                   |
| 37  | **No orphaned branches**         | List for user               |
| 38  | **No accidentally staged files** | Warn user                   |
| 39  | **Commit messages**              | Suggest squash/reword       |
| 40  | **Squash candidates**            | Suggest interactive rebase  |
| 41  | **No large files**               | Should these be gitignored? |
| 42  | **`.gitignore` check**           | Suggest additions           |

---

## Group 5: CI / PR State (8 checks, sequential)

| #   | Check                         | Action on Fail           |
| --- | ----------------------------- | ------------------------ |
| 43  | **PR exists**                 | Warn — need to create PR |
| 44  | **CI checks green**           | List failing checks      |
| 45  | **No pending reviews**        | Note status              |
| 46  | **Review comments addressed** | List unresolved          |
| 47  | **PR description complete**   | Suggest improvements     |
| 48  | **Labels applied**            | Suggest labels           |
| 49  | **Linked issues**             | Suggest linking          |
| 50  | **PR merged**                 | Merge or note blocker    |

Check 50 is the terminal gate — sweep is not complete until PR is merged.

---

## Group 6: Completeness & Follow-ups (15 categories, sequential)

**The rule: nothing leaves your head unlogged.** Every future improvement, risk, outstanding item, or "we should come back to this" MUST be captured as a GitHub issue/discussion.

1. **Scan for open items:** TODOs/FIXMEs/HACKs in the diff, `throw new Error("not implemented")` markers
2. **Walk 15 follow-up categories** (tests, cleanup, wiring, perf, monitoring, feature flags, migration, deferred ideas, risks, verification checkpoints, improvements, open discussions, dependency updates)
3. **Create issues** with `--label "follow-up"` (or GitHub Discussions for open-ended topics). Present all proposed issues to user before creating.

📖 **Full 15-category table & issue templates:** `reference/follow-up-categories.md`

**All-clear CANNOT be printed if** any risk/concern/improvement/deferred decision from the session is unlogged.

---

## Group 7: Environment & Config (6 checks, sequential, if relevant)

Checks: env vars documented, secrets in vault, config defaults safe, terraform plan clean, DB migrations reversible, Docker build works.

📖 **Full check table:** `reference/env-and-final-checks.md`

---

## Group 8: Final Verification (4 checks, sequential, last)

Fresh test run, full diff review, scope check (no scope creep?), worktree cleanup note.

📖 **Full check table:** `reference/env-and-final-checks.md`

---

## Execution Plan

```
Phase -1: Land the PR (rebase → quality gates → push → CI → fix loop → merge)
              │
              ▼
Phase 0: Dedup scan (30s)
         │
         ▼
┌────────┬────────┬────────┐
│Group 1 │Group 2 │Group 3 │  ← parallel subagents
│Quality │Review  │Docs    │
└────┬───┴────┬───┴────┬───┘
     └────────┼────────┘
              ▼
         Group 4: Git Hygiene → Group 5: CI/PR → Group 6: Follow-ups
              │
              ▼
         Group 7: Env & Config → Group 8: Final Verification
              │
              ▼
         Results table + All-clear signal
```

**Estimated time:** 3-8 minutes (Phase -1 depends on CI speed; Groups 1-3 run in parallel).

---

## Results & All-Clear

📖 **Results table template:** `reference/results-template.md`

**All-clear (only if ALL checks pass/skipped and ALL follow-ups tracked):**

```
✅🏁 SWEEP COMPLETE — nothing left to do.
```

**Blocking issues remain:**

```
⛔ SWEEP INCOMPLETE — {N} items need attention:
  1. [FAIL] typecheck — 3 errors in src/foo.ts
  2. [OPEN] PR review comment unresolved — thread #4
```

**Partial sweep (user interrupted):**

```
⚠️ PARTIAL SWEEP — Groups 1-4 clean. Groups 5-8 not run.
   Re-run with "final sweep" to complete.
```

---

## Customization

📖 **Repo-specific overrides & pipeline repo detection:** `reference/customization.md`

---

## Anti-Patterns

- ❌ **Running checks already green in CI** — always dedup first
- ❌ **Fabricating follow-up issues** — only create issues for real gaps
- ❌ **Blocking on non-blocking items** — warnings don't prevent all-clear
- ❌ **Running full test suite twice** — if CI already ran tests, skip
- ❌ **Creating 20 follow-up issues** — that many means implementation isn't done
- ❌ **Auto-triggering** — user-invokable only; never run without being asked
