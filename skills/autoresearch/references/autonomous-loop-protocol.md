# Autonomous Loop Protocol

The core experiment loop, shared by all autoresearch domains.

## Phase 0: Initialization (once)

```bash
# 1. Verify git repo
git rev-parse --git-dir 2>/dev/null || echo "ERROR: not a git repo"

# 2. Verify clean tree
git status --porcelain  # must be empty

# 3. Create experiment branch
git checkout -b autoresearch/<descriptive-tag>

# 4. Create trace directory (NOT committed — local only)
mkdir -p .autoresearch/traces/baseline

# 5. Run baseline
<VERIFY_COMMAND> > .autoresearch/traces/baseline/run.log 2>&1
grep "<METRIC_PATTERN>" .autoresearch/traces/baseline/run.log  # record as baseline

# 6. Capture baseline state
cp <SCOPE_FILES> .autoresearch/traces/baseline/  # snapshot of in-scope files
echo '{"iteration": 0, "metric": <BASELINE>, "status": "baseline"}' > .autoresearch/traces/baseline/scores.json

# 7. Initialize results log (NOT committed — local only)
echo -e "iteration\tcommit\tmetric\tdelta\tguard\tstatus\tdescription" > autoresearch-results.tsv
```

**Record the baseline metric.** All future deltas are relative to this.

> **Trace directory structure.** `.autoresearch/traces/{iteration}/` stores the full execution record for each experiment — source snapshots, run logs, guard logs, and scores. The proposer reads these via `grep` and `cat` in Phase 1 to understand _why_ things broke, not just _that_ they broke. Per Stanford's Meta-Harness research, full execution traces produce a 15-point improvement over scalar-only feedback at median.

## Phase 1: Review (start of every iteration)

```bash
# What's been tried?
git log --oneline -20
tail -20 autoresearch-results.tsv

# What's the current state of the code?
# Read the in-scope files to understand what's already optimized
```

### Trace-Based Diagnosis

Before ideating, **read execution traces from recent iterations** — especially discarded/crashed ones. Don't just check the TSV; dig into _why_ things failed:

```bash
# Find the last 3 failed iterations
grep -E 'discard|crash' autoresearch-results.tsv | tail -3

# Read their execution logs — look for error patterns, regressions, unexpected behavior
cat .autoresearch/traces/<iteration>/run.log
grep -i 'error\|fail\|timeout\|assert' .autoresearch/traces/<iteration>/run.log

# Compare what changed between a kept iteration and a discarded one
diff .autoresearch/traces/<kept>/source/ .autoresearch/traces/<discarded>/source/

# Check if a discard had a confounded change (multiple things changed at once)
diff .autoresearch/traces/<N-1>/source/ .autoresearch/traces/<N>/source/ | head -40
```

**Key principle:** Scalar scores tell you _what_ happened. Execution traces tell you _why_. A regression could be caused by the intended change OR by a side effect — traces let you isolate the causal factor. If you see repeated regressions after bundling structural + prompt changes, **isolate them into separate experiments** (test structural changes alone, then prompt changes alone).

Scan for patterns: >5 consecutive discards means you're stuck. Re-read all in-scope files from scratch and try a fundamentally different approach.

## Phase 2: Ideate

Based on the review, choose the highest-impact change to try next. Prioritize:

1. **Low-hanging fruit first** — obvious inefficiencies, unnecessary allocations, dead code
2. **Structural changes second** — algorithm improvements, caching, batching
3. **Micro-optimizations last** — only after the big wins are captured

**Never repeat a failed experiment.** Check `autoresearch-results.tsv` and `git log` for prior attempts.

### Failure Taxonomy

When diagnosing why the metric isn't improving, classify failures by root cause before choosing the next edit. This prevents blind guessing:

| Class                          | Signal                                               | Typical Fix                              |
| ------------------------------ | ---------------------------------------------------- | ---------------------------------------- |
| **Misunderstanding**           | Agent misinterprets the task or instruction          | Clarify prompt, add examples             |
| **Missing tool**               | Agent tries to do something it has no capability for | Add a specialized tool                   |
| **Weak information gathering** | Agent acts before understanding the problem          | Add exploration/inspection steps         |
| **Bad execution strategy**     | Agent has the right idea but wrong approach          | Restructure orchestration or ordering    |
| **Silent failure**             | Agent reports success but output is wrong            | Add verification sub-agent or self-check |
| **Overshoot**                  | Agent does more than asked, breaking constraints     | Tighten scope constraints in prompt      |
| **Verification mismatch**      | Agent's self-check passes but external eval fails    | Align internal checks with eval criteria |

**Prefer changes that fix a class of failures, not a single task.** Ask: "Would this improvement still be worthwhile if this exact task disappeared?" If no, it's overfitting — find a more general fix.

## Phase 3: Modify

Make **ONE atomic change**. Self-check:

- Am I touching more than 5 files? → Split into smaller experiments
- Can I describe this in one sentence? → If not, it's too big
- Does this change the test/guard behavior? → NEVER modify guard/test files
- Am I editing below a `FIXED BOUNDARY` marker? → NEVER modify fixed zones (see `agent-harness.md` → Edit Surface)

Use `edit_file` for targeted changes. Never rewrite entire files.

## Phase 4: Commit

```bash
git add <specific-files>   # NEVER git add -A
git commit -m "experiment(<scope>): <one-line description>

Hypothesis: <why this should help>
Files: <list of changed files>"
```

The `experiment()` prefix is load-bearing — it makes `git log --oneline | grep experiment` reliable for reviewing history.

## Phase 5: Verify

```bash
# Create trace directory for this iteration
mkdir -p .autoresearch/traces/${iteration}

# Capture source snapshot BEFORE running (what was changed)
cp <SCOPE_FILES> .autoresearch/traces/${iteration}/source/

<VERIFY_COMMAND> > .autoresearch/traces/${iteration}/run.log 2>&1
```

**Always redirect to a file.** Never stream verbose output into context.

Extract the metric:

```bash
grep "<METRIC_PATTERN>" .autoresearch/traces/${iteration}/run.log | <extraction_command>
```

If the command crashes (non-zero exit, no metric output):

1. Read the last 50 lines: `tail -50 .autoresearch/traces/${iteration}/run.log`
2. If it's a trivial fix (typo, import): fix and re-run (max 2 attempts)
3. If it's fundamentally broken: log as `crash`, revert, move on

## Phase 5.5: Guard (if configured)

```bash
<GUARD_COMMAND> > .autoresearch/traces/${iteration}/guard.log 2>&1
echo $?  # must be 0
```

If the guard fails:

1. Attempt to fix without changing the optimization (max 2 attempts)
2. If unfixable: log as `discard`, revert

## Phase 6: Decide

| Metric     | Guard              | Decision                      |
| ---------- | ------------------ | ----------------------------- |
| Improved   | Pass (or no guard) | **KEEP** — commit stays       |
| Improved   | Fail               | Attempt fix → KEEP or DISCARD |
| Same/Worse | —                  | **DISCARD**                   |
| Crash      | —                  | **CRASH**                     |

### Dominant Keeps

When a KEEP improves the primary metric AND the guard passes AND no secondary metric regresses, log it as `dominant-keep` in the TSV status column instead of plain `keep`. A dominant keep means the edit is a strict improvement with no tradeoffs — a [[dominance-arguments]] from game theory. This distinction helps post-hoc trace review: dominant keeps are no-brainer wins that never need revisiting, while regular keeps may involve subtle tradeoffs worth re-examining if the optimization direction changes.

For DISCARD and CRASH:

```bash
# Preferred: preserves experiment as negative example in git log
git revert HEAD --no-edit

# Fallback if revert conflicts:
git revert --abort
git reset --hard HEAD~1
```

`git revert` is preferred over `git reset` because reverted commits remain visible in `git log`, serving as memory of failed approaches for future iterations.

### Discard Learning

**Failed experiments still carry signal.** Before moving on from a DISCARD, extract:

1. **Newly solved** — did any previously-failing cases start passing? That change had partial merit; a refined version may work.
2. **Regressions** — which passing cases broke? This reveals brittle assumptions in the current harness.
3. **Missing capabilities** — did the failure reveal a tool, check, or orchestration pattern the harness lacks entirely?

Log these observations in the discard's TSV description (e.g., `"discard: verification sub-agent — regressed on task 3, but solved task 7; need scoped verification"`). This turns every discard into a hypothesis refinement for the next iteration.

### Semantic Scope Wipe

**Why this exists:** `git revert` only undoes the code diff. But failed experiments contaminate beyond the diff — variable renames, comment additions, type changes, and style shifts can leak into files outside the scope during a streak of failed iterations. These surviving artifacts anchor future iterations toward the same flawed direction, even though the code itself was reverted.

**When to run:** After **3+ consecutive discards**, run a semantic scope wipe before the next iteration. Not needed for isolated discards — contamination accumulates over streaks.

```bash
# Compare current state against the last KEPT commit across ALL tracked files
LAST_KEPT=$(grep 'keep' autoresearch-results.tsv | tail -1 | cut -f2)

# 1. Find files that differ from last-kept state OUTSIDE the declared scope
git diff ${LAST_KEPT} -- . ':!<SCOPE_FILES>' > .autoresearch/traces/${iteration}/drift.diff

# 2. If non-empty, inspect for contamination patterns
if [ -s .autoresearch/traces/${iteration}/drift.diff ]; then
  echo "⚠️  Semantic drift detected outside scope files:"
  # Look for renamed variables, new comments, changed types
  grep -E '^\+.*(/\*|//|#|@param|@returns|type |interface )' .autoresearch/traces/${iteration}/drift.diff | head -20
  grep -E '^\-.*(/\*|//|#|@param|@returns|type |interface )' .autoresearch/traces/${iteration}/drift.diff | head -20
fi
```

**If drift is found:**

1. **Review each change** — is it a legitimate improvement that should stay, or conceptual contamination from the failed streak?
2. **Revert contamination selectively:** `git checkout ${LAST_KEPT} -- <contaminated-file>` for files that drifted without reason
3. **Keep legitimate changes** — sometimes a failed experiment correctly renames a variable even if the optimization itself didn't work

**What to look for:**

- Comments that describe a failed approach as if it's the design intent
- Variable/function names that encode a flawed mental model (e.g., `batchSize` renamed to `chunkWindow` to match a rejected batching strategy)
- Type changes that narrow interfaces to fit a failed experiment's assumptions
- Import additions for libraries that the reverted experiment used

## Phase 7: Log

```bash
# Write scores to trace directory
echo "{\"iteration\": ${iteration}, \"metric\": ${metric_value}, \"delta\": ${delta_from_baseline}, \"guard\": \"${guard_status}\", \"status\": \"${status}\", \"description\": \"${description}\", \"commit\": \"${commit_sha}\"}" \
  > .autoresearch/traces/${iteration}/scores.json

# Append to results TSV (never committed)
echo -e "${iteration}\t${commit_sha}\t${metric_value}\t${delta_from_baseline}\t${guard_status}\t${status}\t${description}" \
  >> autoresearch-results.tsv
```

**Do NOT** print a verbose summary after each iteration. Print a one-line status:

```
[iter 7] metric=3,534µs (Δ-12.3%) → keep: replaced regex tokenizer with byte scanning
```

### Structured Changelog (Prompt Optimization Only)

For prompt optimization runs, also append to `autoresearch-changelog.md`. This captures reasoning that the TSV can't — invaluable for resuming later or handing off to a smarter model.

```markdown
## Experiment [N] — [KEEP/DISCARD/CRASH]

**Score:** [X]/[max] ([percent]%)
**Change:** [One sentence describing what was changed]
**Hypothesis:** [Why this change was expected to help]
**Result:** [What actually happened — which evals improved/declined]
**Still failing:** [Brief description of remaining failures, if any]
```

**Example:**

```markdown
## Experiment 3 — KEEP

**Score:** 16/20 (80%)
**Change:** Added banned buzzwords list: "NEVER use: revolutionary, cutting-edge, synergy, next-level"
**Hypothesis:** Eval 2 (No buzzwords) was failing 4/5 runs — adding an explicit blocklist should eliminate them
**Result:** Eval 2 went from 1/5 to 5/5. Overall score 12→16. No regressions on other evals.
**Still failing:** Eval 3 (Specific CTA) still fails 3/5 — agent defaults to "Learn More"
```

This changelog is the most durable artifact of the run. The TSV powers automation; the changelog powers understanding.

## Phase 8: Repeat

**Go to Phase 1. NEVER STOP. NEVER ASK IF YOU SHOULD CONTINUE.**

The human might be asleep. The loop runs until interrupted.

### Convergence Exit (Prompt Optimization Only)

Exception to "never stop": if the domain is prompt optimization and the score reaches **≥ 95% for 3 consecutive kept experiments**, exit the loop automatically. At that point gains are marginal and further iterations burn tokens on lateral moves. Print the final summary and stop.

Every ~10 iterations, print a brief progress summary:

```
=== Progress after 10 iterations ===
Baseline: 7,469µs → Best: 3,534µs (-52.7%)
Kept: 7 | Discarded: 2 | Crashed: 1
===
```

## Noise Handling

For fast benchmarks (<5s), measurements are noisy. Mitigation:

1. **Run the verify command 3 times**, take the median
2. **Only keep if improvement exceeds noise floor** — if the variance between runs is ±5%, require >5% improvement to keep
3. Document the noise strategy in the first iteration's log entry

## Stuck Detection

If >5 consecutive experiments are discarded:

1. **Re-read the goal** to check if you've drifted
2. **Try a fundamentally different approach** — if you've been doing micro-opts, try a structural change
3. **Consider if the metric is near its floor** — sometimes the optimization is done

If >10 consecutive discards, escalate to the **Nuclear Rewrite Protocol** below. If that also fails, print a stuck notice and continue trying (don't stop).

### Nuclear Rewrite Protocol

**Why this exists:** LLMs treat existing code as authoritative. After many iterations, flawed logic permeates the in-scope files — not just in the core algorithm, but in variable names, comments, types, and style. Re-reading these files just re-anchors the model to the same local minimum. The fix is to erase the contaminated code and regenerate from specification only, with zero prior code in context.

**Trigger:** >10 consecutive discards, OR when you recognize the "fix this button" pattern — you keep making small changes that don't work, but you suspect a clean rewrite would be trivial.

**Protocol:**

```bash
# 1. Record the stuck state
STUCK_METRIC=<current metric value>
STUCK_COMMIT=$(git rev-parse HEAD)
mkdir -p .autoresearch/traces/nuclear

# 2. Snapshot the contaminated files (for comparison later)
cp <SCOPE_FILES> .autoresearch/traces/nuclear/before/

# 3. Revert to last KEPT commit (not just HEAD — skip all the reverts)
LAST_KEPT=$(grep 'keep' autoresearch-results.tsv | tail -1 | cut -f2)
git stash push -m "nuclear-rewrite-backup"

# 4. DELETE the in-scope files entirely
rm <SCOPE_FILES>
```

Now regenerate **without reading the old code**. Write a spec-only prompt to yourself:

> "Implement [COMPONENT] that achieves [GOAL]. Requirements: [LIST FROM ORIGINAL SETUP]. Do NOT reference any prior implementation. Start from first principles."

Key constraints:

- **Do NOT read** `.autoresearch/traces/nuclear/before/` — that's the contaminated code
- **Do NOT run** `git log` to see prior approaches — those are the local minimum
- **DO read** the verify command and guard command to understand the interface contract
- **DO read** any files OUTSIDE the scope that the in-scope files must integrate with (imports, types, APIs)

```bash
# 5. After regeneration, verify
<VERIFY_COMMAND> > .autoresearch/traces/nuclear/run.log 2>&1
NUCLEAR_METRIC=<extract metric>

# 6. Decide
if [ NUCLEAR_METRIC better than STUCK_METRIC ]; then
  # KEEP the nuclear rewrite — commit and continue the loop from here
  git add <SCOPE_FILES>
  git commit -m "experiment(<scope>): nuclear rewrite — fresh approach after $consecutive_discards consecutive discards

Hypothesis: prior code was anchoring model in local minimum
Nuclear metric: $NUCLEAR_METRIC vs stuck metric: $STUCK_METRIC"
  # Reset discard counter, continue loop
else
  # RESTORE from stash — the nuclear rewrite wasn't better
  git checkout -- .
  git stash pop
  # Log the attempt and continue with normal stuck-detection (different approach)
fi
```

**After a successful nuclear rewrite:** The discard counter resets to 0. The loop continues from Phase 1 with the fresh codebase. The old contaminated code is preserved in `.autoresearch/traces/nuclear/before/` for post-mortem analysis but is never read during the loop.

**After a failed nuclear rewrite:** Restore from stash, log it as a special `nuclear-fail` status in the TSV, and continue trying. The metric may genuinely be near its floor.
