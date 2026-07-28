---
name: rl-applying-to-pipelines
description: 'Apply RL concepts to agent pipelines and non-training optimization. Maps RL terminology to pipeline equivalents — sessions as rollouts, skill amendments as policy updates, autoresearch as optimization loops. Use when designing self-improving agent systems or translating RL concepts to software engineering pipelines.'
interaction: autonomous
type: leaf
---

# Applying RL Concepts to Agent Pipelines

You don't need to train models to benefit from RL thinking. The core concepts — reward shaping, exploration/exploitation, policy optimization, environment design — apply directly to agent pipeline optimization.

## The Pipeline-RL Mapping

| RL Concept            | Pipeline Equivalent                            | How It Works Today                                       |
| --------------------- | ---------------------------------------------- | -------------------------------------------------------- |
| **Policy**            | Agent harness (system prompt + skills + model) | Skills + AGENTS.md + model choice                        |
| **Environment**       | Codebase + CI + review system                  | Git repos + GitHub + test suites                         |
| **Rollout / Episode** | Complete pipeline run (ticket → PR)            | Dispatch → implementation → review → merge               |
| **Action**            | Tool call, file edit, git commit               | Bash, edit_file, create_file, etc.                       |
| **State**             | Pipeline phase + codebase + context            | INTAKE → RESEARCH → PLANNING → ...                       |
| **Reward**            | Merge outcome + review quality + cost          | PR merged? Reviews passed? Budget?                       |
| **Policy update**     | Skill amendments + instinct system             | Traces review → amendments → next dispatch               |
| **Exploration**       | Trying new approaches, unfamiliar repos        | First-time repo dispatch, new skill usage                |
| **Exploitation**      | Using proven patterns on known repos           | Established repo-knowledge, cached conventions           |
| **Replay mechanism**  | Git worktrees                                  | Fresh worktree per dispatch = clean initial state        |
| **Recording proxy**   | Session artifacts + traces review              | Postmortem analyses, skill execution logs                |
| **Reward hacking**    | Gaming pipeline metrics                        | Inflating test count, superficial fixes, scope reduction |
| **Discount factor**   | Recency weighting for amendments               | Recent session learnings weighted higher than old ones   |

## Environment-Driven Pattern in a Pipeline

A pipeline built this way already operates in an environment-driven fashion:

1. **No sandbox** — Agents operate on real codebases via worktrees (not packaged Docker environments)
2. **Recording** — Session artifacts and execution traces are captured automatically
3. **Trace-derived rewards** — Postmortem analyses score sessions based on outcomes
4. **Replay** — Git worktrees provide clean initial state per dispatch
5. **Policy updates** — Skill amendments modify agent behavior for next dispatch

What's missing from a full RL loop:

- **Systematic reward computation** — Currently ad-hoc scoring, not a formal reward function
- **Multiple rollouts per task** — Typically one dispatch per ticket, not N parallel attempts
- **Automated policy updates** — Skill amendments require human review (by design)

## Exploration vs Exploitation Trade-off

| Exploration (try new things)      | Exploitation (use what works)                  |
| --------------------------------- | ---------------------------------------------- |
| Dispatch to unfamiliar repos      | Dispatch to repos with established conventions |
| Try new skill combinations        | Use proven skill chains                        |
| Use newer/different models        | Stick with the model that works                |
| Experiment with prompt variations | Use validated prompts                          |

**Common default:** Exploitation-heavy. Established patterns get reused, and exploration only happens when forced (new repos, new problem types).

**RL insight:** Some exploration is necessary to discover better strategies. The autoresearch skill provides this — it systematically tries variations and keeps improvements.

## Reward Function Design for Pipeline Quality

A pipeline "reward function" could combine:

```
R(session) = w1 * merge_outcome        # Binary: PR merged or not
           + w2 * review_quality        # 0-1: reviews passed first try?
           + w3 * cost_efficiency       # 0-1: cost vs budget
           + w4 * cycle_time            # 0-1: speed vs expected duration
           + w5 * code_quality_delta    # -1 to 1: did code quality improve?
           - p1 * scope_creep_penalty   # Penalty for out-of-scope changes
           - p2 * revert_penalty        # Penalty for reverted commits
```

This maps directly to how RL reward functions are designed: primary outcome + behavioral shaping + penalty terms.

## Next-State Signals in a Pipeline

Every pipeline step produces a next-state signal. Most are used for the immediate next action but discarded for improvement purposes. Classifying them as **evaluative** (good/bad scalar) vs **directive** (tells you what to change) reveals untapped improvement signal.

### Pipeline Signal Map

| Pipeline Event              | Next-State Signal       | Type                   | Currently Used For              | Untapped Use                          |
| --------------------------- | ----------------------- | ---------------------- | ------------------------------- | ------------------------------------- |
| CI run completes            | Pass/fail + logs        | Evaluative + Directive | Retry loop (immediate)          | Recurring failures → skill amendments |
| Review comment              | "Use X instead of Y"    | **Directive**          | Addressing feedback (immediate) | Pattern extraction → review checks    |
| PR merged/rejected          | Binary outcome          | Evaluative             | Session scoring                 | Reward function input                 |
| User correction in thread   | "No, I meant X"         | **Directive**          | Re-generation (immediate)       | Prompt refinement, skill updates      |
| Lint/typecheck errors       | Error messages          | **Directive**          | Auto-fix loop (immediate)       | Convention rules in repo-knowledge    |
| Test failure                | Stack trace + assertion | **Directive**          | Debug loop (immediate)          | Anti-pattern catalog entries          |
| User re-query (rephrased)   | Modified prompt         | **Directive**          | None (treated as new request)   | Intent-miss pattern detection         |
| Review approval (first try) | Approval signal         | Evaluative             | Celebration                     | Positive example harvesting           |

### The Directive Signal Gap

**What's typically done well:** Evaluative signals feed into session scoring and keep/revert decisions.

**What's typically underutilized:** Directive signals — especially review comments and user corrections — contain exact "how to improve" information that gets used once (for the immediate fix) and then discarded.

**The OPD analog for pipelines:** Instead of updating model weights with directive signals (OPD), update **skills and review checks**:

```
Directive signal (review comment)
  → Pattern recognition (recurring across sessions)
  → Skill amendment or new review check (policy update)
  → Future sessions avoid the same mistake
```

This can already happen via manual trace review → skill amendments. The gap is **systematic harvesting** — most teams rely on manual trace review instead of automated pattern extraction from directive signals.

### Process Rewards for Pipeline Steps

Outcome-only scoring (did the PR merge?) leaves most pipeline steps unsupervised. Per-step scoring provides denser signal:

| Pipeline Step   | Process Reward Signal                                       |
| --------------- | ----------------------------------------------------------- |
| File selection  | Did the agent read the right files? (reviewable from trace) |
| Approach choice | Was the approach aligned with codebase conventions?         |
| Implementation  | Clean diff? Minimal changes? No unnecessary refactoring?    |
| Testing         | Tests actually exercise the change? Not just happy-path?    |
| PR description  | Accurate summary? Links to ticket?                          |

Dense per-step scoring maps directly to the PRM approach that outperforms outcome-only rewards in OpenClaw-RL's experiments (76% improvement on tool-call tasks).

## Autoresearch as Policy Optimization

The autoresearch skill IS a simplified RL loop — but it has **two distinct shapes** (ADR 040):

### Fast Loop (deterministic metrics)

| RL Component  | Fast Loop Equivalent                      |
| ------------- | ----------------------------------------- |
| Policy        | The code being optimized                  |
| Action        | A code edit                               |
| Environment   | The benchmark/test suite                  |
| Reward        | Metric value (latency, bundle size, etc.) |
| Policy update | Keep the edit (if metric improved)        |
| Rollback      | Revert the edit (if metric worsened)      |

Works for: code perf, test speed, bundle size, prompt → fixed-output evals, auto-harness benchmark replay.

### Epoch-Based Loop (real-world metrics)

| RL Component  | Epoch Loop Equivalent                         |
| ------------- | --------------------------------------------- |
| Policy        | Agent skill instructions (SKILL.md)           |
| Action        | One mutation per epoch                        |
| Environment   | Real production runs over days/weeks          |
| Reward        | Metric from runs AFTER mutation was deployed  |
| Policy update | Keep mutation (score improved over baseline)  |
| Rollback      | Revert mutation (score same/worse)            |
| Episode       | One epoch (mutation → accumulate runs → eval) |

Works for: pick-issue optimization, dispatch scoring, review check quality, any skill measuring real-world outcomes.

**Key insight:** The fast loop fails silently for agent skills because the metric is computed from historical data — mutating the skill file doesn't change past runs. The epoch-based loop solves this by measuring only runs that occurred AFTER the mutation.

**Enhancement opportunity:** Apply more sophisticated RL concepts to both loops:

- **GRPO-style:** Generate N variations, keep the best, not just keep/revert
- **Curriculum:** Start with easy optimizations, progress to harder ones
- **Reward shaping:** Multi-metric optimization, not just single metric
- **Epoch scheduling:** Auto-trigger evaluation when min_runs threshold is hit

## Key Principles

1. **RL is a framing, not just a training technique** — The concepts (reward, policy, exploration) apply to any optimization loop
2. **Start with the reward** — Define what "good" looks like before optimizing. A vague goal leads to reward hacking.
3. **Environment fidelity matters** — Optimize in conditions that match production. Don't test in synthetic environments.
4. **Policy updates should be reversible** — Keep/revert, not permanent edits. Skill amendments can be archived.
5. **Explore deliberately** — Don't just exploit known patterns. Budget for experimentation.
