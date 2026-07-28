# PR Backlog Sweep — Heuristics

Compiled from a 16-PR trial sweep (Apr 2026). Each heuristic includes the observation, the rule, and the action.

> **Note:** This file was reconstructed from a thread summary after the local working copy was lost. The structure preserves the 5 high-confidence headline heuristics; sub-points are inferred from the same trial run and may need refinement on the next sweep.

## Top 5 Headline Heuristics

### 1. "Green CI" can be deceptive

**Observation:** Several PRs showed a green checkmark on the rollup despite the actual test workflow never running. The green came from trivial workflows (labelers, doc-only paths) that always pass.

**Rule:** Verify the **specific failing-check name**, not the aggregate `statusCheckRollup`. Use `gh pr checks <num>` and confirm `test.yml` (or the equivalent gating workflow) actually ran.

**Action:** In step 3 of the workflow, fetch `checkRuns` per PR and explicitly assert that the gating CI workflow appears with a non-`SKIPPED` conclusion before classifying as `MERGE_READY`.

### 2. PRs often have hidden dependencies

**Observation:** Some PRs (e.g., a lint cleanup) only become viable after a separate infra/baseline PR lands.

**Rule:** Read PR descriptions for "depends on #X" or "blocked by #Y" markers. When clustering failures, also cluster by **author** and **branch-base relationships** — sequential PRs from the same author on related branches are usually a chain.

**Action:** Build a dependency graph in `.session/deps.dot` before issuing verdicts. A PR labeled `BLOCKED_ON_BASELINE` may unblock 3 others — flag the cascade.

### 3. Batch rebase is high-leverage

**Observation:** ~50% of PRs flagged as "broken" were just stale and rebased cleanly with no real conflict.

**Rule:** Always batch-rebase before triage. The cost is one CI run per PR; the payoff is eliminating false-negative "conflicting" labels.

**Action:** Run rebase pass first (step 2). Force-push only on `CLEAN`. Skip PRs labeled `do-not-rebase` or `breaking-change`.

### 4. Failure clustering reveals baseline issues

**Observation:** When ≥3 PRs fail the same checks (same names, similar error signatures), the issue is almost always a baseline failure on `main`, not the individual PRs.

**Rule:** Don't blame the PR until you've ruled out the baseline. The threshold is **3 PRs** sharing failure mode = baseline suspect.

**Action:** Check `main`'s most recent CI run on the same checks. If `main` is also red, the verdict for clustered PRs is `BLOCKED_ON_BASELINE`, not `SALVAGE`. File or find the baseline-fix issue and link all blocked PRs to it.

### 5. Formatting bloat → recreate slim

**Observation:** Stale PRs that mixed a small fix with a large drive-by formatting change were nearly impossible to rebase cleanly.

**Rule:** If a PR's diff is >70% formatting/whitespace changes and it's >30 days stale, the conflict-resolution cost exceeds rewrite cost.

**Action:** Verdict `RECREATE_SLIM`. Comment on the original with a pointer to the new slim PR, then close. Apply only the substantive change in the new PR.

## Operational Sub-Heuristics

These supporting observations from the same trial run inform the workflow steps:

- **Force-push timing.** After batch rebase, wait for CI to settle (≥1 full run cycle, typically 15 min) before reading check results. Polling too early gives false `PENDING` reads.
- **Empty rebases.** If a rebase produces an empty diff (PR was already merged via squash), close the PR with comment `superseded by <merge-sha>`.
- **`UNKNOWN` mergeable state.** GitHub's `mergeable` field is async-computed. Poll `gh pr view <num> --json mergeable` until it returns `MERGEABLE` or `CONFLICTING`. Don't trust `UNKNOWN`.
- **Baseline-fix slim PR pattern.** When fixing the baseline (see #5), the slim PR should touch only files in the failing check's blast radius — no drive-by formatting, no test reorganization.
- **Author-load awareness.** If 5+ open PRs are from the same author, they're probably context-switching. Surface this in the verdict report so reviewers can prioritize unblocking that author rather than triaging in PR-number order.
- **`needs-discussion` is a hard gate.** Never auto-rebase or force-push these. Verdict: defer to human.
- **CI cost.** A full backlog rebase of 16 PRs costs ~$3–5 in CI minutes. Schedule sweeps weekly, not daily.
- **Verdict file as artifact.** Keep `.session/verdict.md` even after the sweep — it's the audit trail for closed/abandoned PRs.
- **Re-run vs. re-rebase.** If a PR fails CI after a clean rebase but the failure isn't in the cluster, prefer **re-running** the failed check (transient flake) before assuming `SALVAGE`. One free re-run per check.
- **Stale PR window.** PRs >90 days old with no comments in 30 days are usually `CLOSE`. Confirm with author via `@mention` comment if author is still active.

## Conflict Resolution Gotchas (Apr 2026 sweep — second pass)

### G1. `git rebase` ours/theirs is INVERTED vs. merge

This bites every sweep. Internalize it:

| Term       | During `git merge` | During `git rebase`             |
| ---------- | ------------------ | ------------------------------- |
| `--ours`   | The current branch | **Upstream** (e.g., main)       |
| `--theirs` | The merged branch  | **The PR commit being applied** |

**Action:** When a PR conflict is in a file the PR is meant to modify, you almost always want `git checkout --theirs <file>` during rebase to keep the PR's intended change. `--ours` discards the PR's work.

**Failure mode if you get it wrong:** PR branch ends up identical to main → diff becomes empty → push succeeds → PR appears "fixed" but actually destroyed. Recover via the prior SHA from the rebase log (`git push origin <prior-sha>:refs/heads/<branch>`).

### G2. Append-only log files: keep BOTH halves

For `run-log.yaml`, `idea-registry.yaml`, `session-learnings.md`, `*.jsonl`, `backlog.yaml`: the conflict is almost always "main added entries since the PR branched, the PR also added entries". Neither `--ours` nor `--theirs` is correct alone — you lose half the history.

**Action:** Open the file, delete only the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), keep both content blocks. If entries are date-keyed YAML lists, no further reconciliation needed.

### G3. The slim-recreate cost calculus

When deciding `RECREATE_SLIM` vs. `SALVAGE` for a stale CI/baseline-fix PR:

- If the PR's diff is >70% formatting OR touches >50 files OR has >10 conflict files on rebase → `RECREATE_SLIM` is cheaper.
- The slim PR should target ONE root cause. Trial run example: #2006 (5505 lines, 100 files, 20 conflicts) → #2410 (12 lines, 3 files) fixed the actual baseline killer (`pnpm/action-setup version: 9` conflicting with `packageManager`). Took ~5 minutes vs. the projected 1–2 hours for in-place merge.

### G4. Worktree pollution recovery

If `git worktree add` shows `fatal: '<branch>' is already used by worktree at ...`, that other worktree may itself be broken (wrong branch checked out, half-rebased state). Don't try to clean it up — just create a fresh detached worktree (`git worktree add /path --detach origin/main`) and ignore the polluted one.

### G5. Use rebase reflog as your safety net

Before any force-push during a sweep, write the prior remote SHA into `.session/rebase-log.md`. If a resolution goes wrong (see G1), you can restore in one command:

```bash
git push --force-with-lease=<branch>:<current-clobber-sha> origin <prior-sha>:refs/heads/<branch>
```
