---
name: autoresearch
description: 'Autonomous keep/revert optimization loop for any measurable metric, or adversarial debate loop for subjective domains. Applies the Karpathy autoresearch pattern to code performance, test speed, prompt tuning, ML training, code quality, and subjective prose via AutoReason. Use when asked to optimize, make faster, reduce size, improve performance, speed up, shrink, tune, improve writing, make more convincing, refine argument, or run experiments autonomously.'
interaction: autonomous
type: leaf
synergies:
  requires: []
  enhances: []
  conflicts: []
  domain: [optimization, automation]
---

# Autoresearch — Autonomous Optimization Loop

An autonomous agent loop that edits code, measures a metric, keeps improvements, reverts regressions, and repeats forever. Based on [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) pattern.

## When to Trigger

This skill has a **wide trigger surface** with an **explicit opt-in gate**. Activate on any of these:

**Explicit (skip opt-in, go straight to setup):**

- "Run autoresearch on…" / "autoresearch this"
- "Run experiments overnight" / "optimize in a loop"

**Implicit (trigger opt-in gate first):**

- "Make this faster" / "Speed up X" / "This is slow"
- "Optimize X" / "Improve performance"
- "Reduce bundle size" / "Shrink this"
- "Reduce test time" / "Tests are too slow"
- "Improve coverage" / "Too many lint warnings"
- "Tune this prompt" / "The prompt isn't working well"
- "Lower latency" / "Reduce allocations" / "Fewer objects"
- "Train faster" / "Reduce loss" / "Tune hyperparameters"
- "Improve this writing" / "Make this more convincing" / "Refine this argument"
- Any request involving **improving a measurable metric iteratively**

## Opt-In Gate

For **implicit triggers**, present the autoresearch option before proceeding:

> This looks like an optimization task with a measurable target. I can either:
>
> 1. **Make a single targeted fix** — I'll analyze the problem and apply one improvement
> 2. **Run an autoresearch loop** — I'll autonomously run dozens of experiments, keeping what improves the metric and reverting what doesn't. Best left running overnight.
>
> Which approach do you want?

If the user picks (1), do the task normally without this skill. If they pick (2), continue with setup below.

For **explicit triggers** (user said "autoresearch"), skip the gate and go straight to setup.

## Two Loop Shapes

**Before setting up any autoresearch loop, classify the metric.** There are two fundamentally different loop shapes, and using the wrong one silently produces no results.

### Fast Loop (single session) — DEFAULT

For deterministic metrics where a shell command produces a fresh score immediately.

| Component  | What It Is                                    |
| ---------- | --------------------------------------------- |
| **Metric** | A single number to optimize (lower or higher) |
| **Scope**  | The file(s) the agent may edit                |
| **Verify** | A shell command that outputs the metric       |
| **Guard**  | An optional safety check (tests must pass)    |

The loop: `Edit → Commit → Verify → Keep or Revert → Repeat` (seconds between iterations)

### Epoch-Based Loop (multi-session) — FOR AGENT SKILLS

For metrics that depend on real-world execution data accumulating over time. **Use this when the metric cannot be computed from a shell command alone** — e.g., pick-issue success rate, dispatch quality, review pass rate.

The loop: `Mutate → Deploy to main → Wait days/weeks → Evaluate from new runs → Keep or Revert`

Read `references/epoch-based-loop.md` for the full protocol, scripts, and applicable domains — including why this distinction exists and when each loop shape applies.

### Classification Test

| Question                                         | Fast           | Epoch                  |
| ------------------------------------------------ | -------------- | ---------------------- |
| Can `verify_cmd` produce a fresh score in <60s?  | ✅             | ❌                     |
| Does the score change when scope files change?   | ✅ Immediately | ❌ Only after new runs |
| Can you do 50 iterations in one session?         | ✅             | ❌                     |
| Does the metric depend on real-world agent runs? | ❌             | ✅                     |

**If ANY answer points to Epoch → use epoch-based.** The fast loop will return the same score every iteration.

## Domain Detection & Routing

Identify the domain from the user's request, then read the corresponding reference file for domain-specific setup guidance:

| Domain                   | Trigger Phrases                                                                      | Metric Direction    | Reference                            |
| ------------------------ | ------------------------------------------------------------------------------------ | ------------------- | ------------------------------------ |
| **Code Performance**     | "faster", "optimize speed", "reduce latency", "fewer allocations"                    | ↓ lower time/allocs | `references/code-performance.md`     |
| **Test Speed**           | "faster tests", "reduce test time", "speed up CI"                                    | ↓ lower seconds     | `references/test-speed.md`           |
| **Prompt Optimization**  | "optimize prompt", "improve success rate", "tune the skill"                          | ↑ higher score      | `references/prompt-optimization.md`  |
| **ML Training**          | "train", "loss", "val_bpb", "tune hyperparameters"                                   | ↓ lower loss        | `references/model-training.md`       |
| **Code Quality**         | "reduce complexity", "improve coverage", "fewer warnings"                            | varies              | `references/code-quality.md`         |
| **Agent Harness**        | "optimize agent", "improve agent", "tune harness", "agent perf"                      | ↑ higher score      | `references/agent-harness.md`        |
| **Visual Performance**   | "frametime", "WebGPU", "canvas perf", "rendering", "jank", "p99"                     | ↓ lower p99.9 ms    | `references/visual-performance.md`   |
| **Subjective Reasoning** | "improve this writing", "more convincing", "refine argument", "better copy"          | ↑ higher win rate   | `references/subjective-reasoning.md` |
| **Trace Scoring**        | "optimize pipeline quality", "improve merge rate", "tune dispatch", "reward shaping" | ↑ higher composite  | `references/trace-scoring.md`        |
| **Epoch-Based (any)**    | "optimize pick-issue", "improve dispatch", "tune skill over time"                    | ↑ higher score      | `references/epoch-based-loop.md`     |
| **Custom**               | anything with an explicit metric                                                     | user-specified      | Use the protocol directly            |

**After detecting the domain**, read the reference file for domain-specific guidance on metric extraction, scope selection, verify commands, and guard commands. Then proceed to setup.

## Interactive Setup

Before the loop starts, you need exactly 5 things. Ask for anything not provided or inferrable:

| Field                  | Required? | How to Infer                                                                                                                                                                                     |
| ---------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Goal**               | Yes       | From user's request                                                                                                                                                                              |
| **Scope**              | Yes       | From domain reference or user's file mentions. If files use two-zone markers (`EDITABLE` / `FIXED BOUNDARY`), scope to the editable zone only — see `references/agent-harness.md` → Edit Surface |
| **Metric + Direction** | Yes       | From domain reference table                                                                                                                                                                      |
| **Verify command**     | Yes       | From domain reference or user                                                                                                                                                                    |
| **Guard command**      | No        | Default: the repo's test command                                                                                                                                                                 |

**Batch questions.** Ask all missing fields in one message, not one at a time.

Once all fields are confirmed, read `references/autonomous-loop-protocol.md` and begin.

## Quick Start Examples

**Code performance** (à la Tobi/Shopify Liquid):

```
/skill autoresearch
Goal: Reduce parse+render time for the template benchmark
Scope: lib/liquid/**/*.rb
Metric: combined_µs (lower is better)
Verify: cd performance && bundle exec ruby bench_quick.rb
Guard: bundle exec rake test
```

**Test speed:**

```
/skill autoresearch
Goal: Reduce vitest execution time for a workspace package
Scope: packages/my-app/vitest.config.ts, packages/my-app/src/**/*.ts
Metric: seconds (lower is better)
Verify: time pnpm --filter my-app test 2>&1 | grep real | awk '{print $2}'
Guard: pnpm --filter my-app test
```

**Prompt optimization** (à la AutoVoiceEvals):

```
/skill autoresearch
Goal: Improve a skill's success rate
Scope: path/to/the-skill/SKILL.md
Metric: success_rate (higher is better)
Verify: ./scripts/eval-skill.sh the-skill
Guard: pnpm typecheck
```

**ML training** (the original):

```
/skill autoresearch
Goal: Minimize validation loss
Scope: train.py
Metric: val_bpb (lower is better)
Verify: uv run train.py 2>&1 | grep "^val_bpb:" | awk -F: '{print $2}'
Guard: none
```

**Agent harness** (à la AutoAgent):

```
/skill autoresearch
Goal: Improve task completion rate for coding agent
Scope: agent.py (EDITABLE zone only, above FIXED ADAPTER BOUNDARY)
Metric: avg_score (higher is better)
Verify: uv run harbor run -p tasks/ -n 10 -o jobs --job-name latest > run.log 2>&1 && grep "avg_score" run.log
Guard: uv run harbor run -p tasks/ --task-name smoke-test -l 1 -n 1 -o jobs > /dev/null 2>&1
```

**Subjective reasoning** (à la AutoReason):

```
/skill autoresearch
Goal: Make this pitch deck copy more persuasive
Scope: docs/pitch-deck.md
Metric: win_rate (higher is better — synthetic via blind judge panel)
Verify: (built into the loop — see references/subjective-reasoning.md)
Guard: none
```

## Critical Rules

1. **NEVER STOP.** Loop forever until interrupted. Do not ask "should I continue?" — the human might be asleep.
2. **ONE change per iteration.** Atomic edits. If you're touching >5 files, split it.
3. **Commit BEFORE verifying.** Every experiment gets a commit so you can revert cleanly.
4. **Mechanical verification only.** The metric number decides. Not your judgment of code quality.
5. **Auto-rollback on regression.** If the metric got worse or the guard failed, `git revert HEAD --no-edit` immediately.
6. **Simplicity wins on ties.** If two approaches score the same, keep the one with fewer lines of code.
7. **Traces are memory, not just scores.** Read execution traces from `.autoresearch/traces/` — not just the TSV — at the start of each iteration. Scores tell you _what_ happened; traces tell you _why_. When diagnosing regressions, `grep` and `cat` the run logs and diff the source snapshots. Never compress traces into summaries — raw logs outperform summaries by 15 points ([Meta-Harness, Stanford 2026](https://arxiv.org/abs/2603.28052)).
8. **Isolate confounds.** If an experiment bundles multiple changes and regresses, don't discard everything — separate the changes and test each independently in the next iterations.
9. **Redirect output.** Always `> .autoresearch/traces/${iteration}/run.log 2>&1` for long-running commands. Grep for the metric. Don't stream verbose output into context.

## Advanced Variants

### Damped Parameter Adjustment

When optimizing continuous parameters (not code edits), raw keep/revert can oscillate — overshooting the target, then overcorrecting. Use **damped delta application**:

```
new_value = current_value + damping × (target_value - current_value)
```

Where `damping` is 0.5–0.8. This interpolates between current and target instead of jumping directly. Clamp to the parameter's valid range after application. Reduces the number of rejected iterations significantly.

Use damping when the scope is a **parameter space** (config values, prompt weights, generation settings) rather than source code edits.

### Bipolar Scoring (Tradeoff Dimensions)

Standard autoresearch assumes unipolar metrics: higher (or lower) is better. But some dimensions are **bipolar tradeoffs** where neither pole is superior — e.g., abstract↔concrete, DRY↔readable, terse↔verbose.

For bipolar dimensions:

- Score on a -1 to +1 scale (pole A to pole B)
- **Always accept** — movement toward either pole is progress (it shows commitment to a direction)
- Composite = mean of `abs(scores)` — measures pole commitment, not pole direction
- Use **plateau detection** (score variance < threshold over last N iterations) instead of accept/reject as the stop condition

This is useful when the optimization goal is "find a coherent aesthetic direction" rather than "maximize a quality metric."

> The full pattern for translating qualitative critique into parameter deltas — ParamSpace descriptions, damped application, and the accept/reject rollback protocol — is described in [autocritic](https://github.com/mccoyspace/autocritic).

## Post-Loop

When the human returns or interrupts:

1. Print a summary: baseline → best, total experiments, keeps/discards/crashes
2. List the top 3 most impactful changes (by delta)
3. Note what was tried but didn't work (for the "What did NOT work" section)
4. The branch contains only the winning commits — ready for PR
