---
name: pr-backlog-sweep
description: Triages the open PR backlog. Batch-rebases stale PRs, clusters CI failures to detect baseline issues on main, identifies salvageable vs. abandon candidates, and emits a per-PR verdict. Use when asked to sweep PRs, triage the PR backlog, rebase stale PRs, or do a backlog health pass.
interaction: autonomous
type: orchestrator
synergies:
  enhances: [reviving-stale-prs]
  domain: [pr, backlog, triage, ci]
---

# PR Backlog Sweep

Orchestrate a batch triage of the open PR backlog. Distinguishes **stale-but-fixable** PRs from **fundamentally broken** ones, and detects when many PRs share the same root cause (a baseline failure on `main`).

## When to Use

- Backlog has >10 open PRs and CI signal is unclear
- Multiple PRs failing the same checks (suspect baseline regression)
- Quarterly/monthly backlog health pass
- Before a release, to assess what can land

## Workflow

### 1. Snapshot the backlog

```bash
gh pr list --state open --limit 50 \
  --json number,title,headRefName,mergeable,updatedAt,statusCheckRollup,labels \
  > .session/prs.json
```

Persist to `.session/prs.json` for reproducibility — every later step references it.

### 2. Batch rebase

For each PR not labeled `do-not-rebase`, attempt rebase onto current `main`. Record outcome (`CLEAN`, `DIRTY`, `EMPTY`) in `.session/rebase-log.md`. Force-push only on `CLEAN`.

See `reference/heuristics.md` → "Batch Rebase Pattern".

### 3. Cluster CI failures

After rebases settle, fetch latest check runs for all PRs. Group by failing-check-name. **If ≥3 PRs fail the same check, treat as a baseline failure on `main`** — do not blame individual PRs. File or find the baseline-fix issue.

### 4. Per-PR verdict

For each PR, emit one of:

- `MERGE_READY` — green CI, no conflicts, recently updated
- `SALVAGE` — small, focused fix needed; assignable
- `BLOCKED_ON_BASELINE` — failures match the cluster
- `RECREATE_SLIM` — stale + heavy formatting bloat; close and reopen narrow
- `CLOSE` — superseded, abandoned, or no longer relevant

### 5. Output

Write `.session/verdict.md` with one section per PR: number, title, verdict, evidence (check names, conflict count, age), recommended next action.

## Anti-patterns

- **Don't trust "green CI" blindly.** Trivial workflows (labelers, doc-only) can pass while real tests never ran. Verify the failing-check name, not the rollup.
- **Don't fix baseline failures inside a feature PR.** Recreate the baseline fix as a slim dedicated PR (see `reference/heuristics.md` → #5 and G3).
- **Don't rebase PRs labeled `needs-discussion` or `breaking-change`** without a human gate.
- **Don't use `--ours` during rebase to "fix" conflicts.** It discards the PR's work — `--ours` is the upstream side during rebase. See `reference/heuristics.md` → G1.
- **Don't auto-resolve append-only log conflicts.** Both sides have legitimate entries — keep both halves manually. See G2.
- **Always log the prior SHA before force-push.** Cheapest insurance against G1. See G5.

## References

- `reference/heuristics.md` — 15 specific learnings from the trial run (Apr 2026, 16-PR sweep)
