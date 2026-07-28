# Epoch-Based Autoresearch (Slow Loop)

Reference for optimizing metrics that depend on real-world execution data accumulating over time. Complements the standard fast loop (`autonomous-loop-protocol.md`).

**Requirements:** this domain assumes you have your own telemetry pipeline that logs agent runs over time, plus mutate/eval scripts that read from it. The script names and paths below (`scripts/autoresearch-epoch-*.sh`, `telemetry/*.jsonl`) are illustrative — write equivalents for your own system.

## When to Use

Use the epoch-based loop when the verify command **cannot produce a fresh score** from a single shell command. The metric depends on external execution that happens over days/weeks.

### Classification Test

| Question                                                   | Fast Loop | Epoch-Based |
| ---------------------------------------------------------- | --------- | ----------- |
| Can `verify_cmd` produce a score in <60s?                  | ✅        | ❌          |
| Does the score change immediately when scope files change? | ✅        | ❌          |
| Can you run 50 iterations in one session?                  | ✅        | ❌          |
| Does the metric depend on real-world agent runs?           | ❌        | ✅          |

**If ANY answer points to epoch-based → use epoch-based.** The fast loop will silently produce no useful results (same score every iteration).

## The Two Loops

```
FAST LOOP (single session)          EPOCH-BASED (multi-session)
────────────────────────            ────────────────────────────
mutate → measure → keep/revert     mutate → deploy → wait days
    ↑_________________________↓         ↑                    ↓
    seconds between iterations          evaluate → keep/revert
                                        days/weeks between epochs
```

## Epoch Lifecycle

```bash
# 1. Start first epoch (baseline only)
bash scripts/autoresearch-epoch-mutate.sh

# 2. Wait for runs to accumulate (days/weeks)
#    ... agents run the target skill/system, telemetry accumulates ...

# 3. Enrich telemetry with latest data
bash scripts/enrich-telemetry.sh

# 4. Evaluate current epoch
bash scripts/autoresearch-epoch-eval.sh [--min-runs=15]

# 5. If epoch was kept or reverted, propose next mutation
bash scripts/autoresearch-epoch-mutate.sh

# 6. Repeat from step 2
```

(These scripts are examples, not shipped by this skill — build equivalents against your own telemetry store.)

## Key Differences from Fast Loop

| Aspect                     | Fast Loop                    | Epoch-Based                                       |
| -------------------------- | ---------------------------- | ------------------------------------------------- |
| **Iteration cadence**      | Seconds                      | Days/weeks                                        |
| **Session model**          | Single overnight session     | One eval per trigger                              |
| **Metric source**          | `verify_cmd` output          | Historical telemetry (date-windowed)              |
| **Mutation agent**         | Codex CLI (in-loop)          | Codex CLI or manual (per-epoch)                   |
| **Statistical confidence** | Single measurement (noisy)   | N runs minimum (configurable)                     |
| **Confound control**       | Atomic commits               | Must avoid other changes during epoch             |
| **Trigger**                | Continuous (never stop)      | Manual, cron, or orchestrator hook                |
| **State persistence**      | `.autoresearch/` dir (local) | `telemetry/autoresearch-epochs.jsonl` (committed) |

## Confound Control

The biggest risk in epoch-based loops: **other changes happen during the epoch** that affect the metric. If you change a skill's instructions AND update its scoring heuristics during the same epoch, you can't attribute the result to either change.

**Mitigation:**

- Only one active epoch per scope at a time
- Document any confounding changes in the epoch record
- If you must make a non-epoch change to the scope file (urgent fix), close the current epoch as "confounded" and start fresh

## Applicable Domains

| Domain                   | Scope (example)                    | Metric            | Min Runs |
| ------------------------ | ---------------------------------- | ----------------- | -------- |
| task-picking skill       | `skills/your-task-picker/SKILL.md` | composite_score   | 15       |
| dispatch/routing scoring | `src/dispatch/scoring.ts`          | merge_rate        | 20       |
| review check quality     | `.agents/checks/*.md`              | review_pass_rate  | 10       |
| skill instructions (any) | `skills/*/SKILL.md`                | task_success_rate | 10       |

## Relationship to Auto-Harness

Auto-harness with benchmark replay is a **bridge** that converts slow-loop domains into fast-loop domains by replaying reference tasks in a sandbox. When a benchmark suite exists (e.g. `benchmarks/your-skill/`), you can:

1. Use **fast loop + benchmark replay** for rapid iteration on instruction quality
2. Use **epoch-based loop** to validate that benchmark-optimized changes actually improve real-world metrics

Best practice: optimize with fast loop (benchmark), then validate with one epoch of real-world data before promoting.
