# Prompt Optimization

Optimize agent prompts (system prompts, skill prompts, tool descriptions) against an evaluation suite. Based on the AutoVoiceEvals pattern — propose one prompt edit, evaluate against test cases, keep or revert.

## Typical Metrics

| Metric Name       | Unit       | Direction | Extraction Example  |
| ----------------- | ---------- | --------- | ------------------- |
| `success_rate`    | 0.0–1.0    | ↑ higher  | eval script output  |
| `composite_score` | 0.0–1.0    | ↑ higher  | weighted pass rate  |
| `csat`            | 0–100      | ↑ higher  | quality rating      |
| `prompt_chars`    | characters | ↓ lower   | `wc -c < prompt.md` |

## How It Works

Unlike code performance (where the benchmark is a shell command), prompt optimization requires an **evaluation harness** that:

1. Runs the prompt against a set of test scenarios
2. Judges each response against criteria
3. Outputs a composite score

### Evaluation Script Pattern

```bash
#!/bin/bash
# eval-prompt.sh <prompt-file> <scenarios-file>
set -e

PROMPT_FILE=$1
SCENARIOS=${2:-eval-scenarios.json}
RESULTS=$(mktemp)

# Run each scenario
pass=0
total=0
while IFS= read -r scenario; do
  total=$((total + 1))
  # Run the agent/model with the prompt against this scenario
  # Judge the output against expected criteria
  # ... (domain-specific evaluation logic)
  if [ "$passed" = "true" ]; then
    pass=$((pass + 1))
  fi
done < <(jq -c '.scenarios[]' "$SCENARIOS")

# Compute score
score=$(echo "scale=3; $pass / $total" | bc)
echo "METRIC success_rate=$score"
echo "METRIC prompt_chars=$(wc -c < "$PROMPT_FILE")"

rm -f "$RESULTS"
```

## Prompt Edit Strategies

Ordered by typical impact:

1. **Remove unnecessary instructions** — shorter prompts are cheaper and less confusing. If the score stays the same with fewer instructions, that's a keep (simplicity wins).
2. **Add handling for discovered failure modes** — run the eval, find what fails, add specific guidance for those cases.
3. **Restructure for clarity** — reorder sections so the most important rules come first.
4. **Add examples** — concrete examples of expected behavior reduce ambiguity.
5. **Tighten constraints** — replace vague instructions ("be careful") with specific rules ("never do X when Y").
6. **Remove redundancy** — if two sections say the same thing differently, consolidate.

## Trace-Informed Mutation

When deciding what prompt edit to make next, **feed the optimizer the execution trace, not just the score.** This is the single biggest differentiator between effective and ineffective prompt optimization — the Zeta Alpha study ([Câmara et al. 2026](https://arxiv.org/abs/2604.02988)) showed that OpenAI's generic optimizer (no traces, no rubrics) scored 0.583 while trace-informed optimizers scored 0.654–0.705 on the same task.

**What to feed into the mutation step:**

1. **The failing scenario's input** — what query/task triggered the failure
2. **The agent's full execution trace** — tool calls, intermediate reasoning, the output it produced. Read from `.autoresearch/traces/{iteration}/`. Don't summarize.
3. **The rubric criteria it failed on** — which specific eval question got a "no" and why
4. **The current prompt** — so the optimizer can see what instruction was (or wasn't) present

**What NOT to feed:**

- ❌ Just the score ("success_rate dropped from 0.8 to 0.6") — no signal for what to change
- ❌ A prose summary of what went wrong — summaries lose the causal detail needed to diagnose
- ❌ Passing scenarios — focus attention on failures only; passing scenarios add noise

**Mutation prompt pattern:**

```
The agent using this prompt failed on the following scenario:
Input: {scenario_input}
Expected: {rubric_criteria}
Actual output: {agent_output}
Execution trace: {full_trace}

Current prompt: {current_prompt}

What single, specific instruction could be added or modified to handle this
failure case without breaking the scenarios that currently pass?
```

This connects the autoresearch principle "traces are memory, not just scores" (SKILL.md rule 7) directly to the prompt optimization domain.

### Meta-Prompt Design

When the autoresearch loop generates mutations, it uses an implicit "meta-prompt" — the instructions that tell the optimizer how to improve the target prompt. A task-aware meta-prompt outperforms a generic one. In the Zeta Alpha study, GEPA with a custom meta-prompt describing the DR pipeline scored 0.705 vs 0.685 with the default meta-prompt (+3%).

**Before starting the optimization loop, write a system description** that includes:

1. **Agent roles** — what each agent in the system does (e.g., "the research agent retrieves and reads documents, the planner converts findings into tasks")
2. **Workflow** — the data flow between agents (e.g., "orchestrator → reader → aggregator → writer, with iterative replanning")
3. **Which agent is being optimized** — and how its output affects downstream agents
4. **Evaluation criteria** — what makes a good end-to-end output (maps to the rubric)

Feed this system description as a preamble to the mutation prompt pattern above. The optimizer needs to understand the _role_ of the prompt it's editing within the larger system — otherwise it optimizes in a vacuum.

**Skip this** for standalone single-agent prompts where there's no pipeline context to describe.

## Model Empathy — Design for How Models Reason

When optimizing prompts, tools, or agent harnesses, design for the model's cognition, not yours:

- **Tool names are priors.** Models pattern-match tool names before reading descriptions. A tool named `inspect_workbook` will be used more correctly than `run_shell("python -c 'import openpyxl...'"`)`. Name tools for what they _mean_, not what they _do_.
- **Same-model pairing wins.** When the agent writing prompts/tools shares the same model family as the agent consuming them, it has implicit understanding of the consumer's tendencies. Claude writing for Claude outperforms Claude writing for GPT — the meta-agent shares weights with the task-agent and knows how it reasons.
- **Progressive disclosure for context.** Models lose track of instructions buried in walls of data. When a tool returns large output, write it to a file and return a summary with the file path. Keep the conversation context for reasoning, not storage.
- **Don't project human intuitions.** What reads well to you may confuse the model, and vice versa. When an experiment improves the metric but the prompt "looks worse" to human eyes, trust the metric — the model is the consumer.

## Mutation Anti-Patterns

Never do these during a prompt optimization loop:

- ❌ **Rewriting the entire skill from scratch** — atomic changes only. If you can't describe the change in one sentence, it's too big.
- ❌ **Adding 10 new rules at once** — you won't know which one helped (or hurt). One rule per iteration.
- ❌ **Making the prompt longer without targeting a specific failing eval** — length without purpose dilutes the good instructions.
- ❌ **Adding vague instructions** like "make it better", "be more careful", "try harder" — these have zero signal for the model.
- ❌ **Removing a worked example to save space** — examples are the highest-signal content in a prompt. Cut rules before examples.
- ❌ **Optimizing for the checklist instead of the output** — if the score goes up but the output reads worse to a human, the evals need fixing, not more gaming.

## Anti-Cheating Rules

Autonomous prompt optimization loops can "cheat" — the optimizer discovers shortcuts that game the eval without genuinely improving the prompt. These failure modes were documented empirically in a Codex-variant AutoReason loop ([reply thread to @shannholmberg](https://x.com/shannholmberg/status/2038866414057161145)).

**Known cheating patterns:**

1. **Output injection** — The optimizer embeds something resembling the expected output directly into the system prompt and declares victory. After a few iterations, it discovers that the shortest path to a passing eval is to hardcode the answer.
2. **Eval keyword stuffing** — The optimizer adds phrases it knows the judge looks for, without improving the actual reasoning the prompt produces.
3. **Scope narrowing** — The optimizer adds constraints that make the prompt refuse hard scenarios entirely, boosting pass rate on the remaining easy ones.

**Mandatory anti-cheating instructions for the mutation agent:**

Add these to the mutation prompt (the prompt that generates candidate edits):

```
RULES — read carefully:
- Do NOT embed expected outputs, example answers, or solution templates into the prompt.
- Do NOT add instructions that cause the agent to refuse or skip difficult scenarios.
- Do NOT add keywords solely because they appear in the evaluation criteria.
- Your edit must improve the agent's REASONING or BEHAVIOR, not game the scoring.
- If your edit would make the prompt pass by producing a more specific answer for one
  scenario at the cost of generality, it is cheating. Do not do it.
```

**Detection heuristic:** After each winning mutation, diff the prompt change. If the diff introduces content that closely resembles any eval scenario's expected output, flag it and revert. This can be automated:

```bash
# Check if the prompt edit contains substrings from expected outputs
for expected in $(jq -r '.scenarios[].should[]' eval-scenarios.json); do
  if grep -qiF "$expected" <(diff old-prompt.md new-prompt.md); then
    echo "⚠️ CHEATING DETECTED: prompt edit contains expected output substring: $expected"
    git checkout -- prompt.md
    exit 1
  fi
done
```

## Stability Testing

A single passing eval run is not sufficient evidence that a prompt mutation is an improvement. LLM outputs are stochastic — a prompt that passes 1/1 may fail 3/5. The stability testing protocol ensures winning prompts are robust across multiple trials.

**Source:** Empirical findings from a Codex-variant AutoReason loop ([reply thread to @shannholmberg](https://x.com/shannholmberg/status/2038866414057161145)) — 3 trials was insufficient; 5 trials with a 4/5 threshold produced stable winners.

### Per-Iteration Stability

After each mutation, run the eval suite **5 times** (not once):

```
trials = 5
pass_threshold = 3  # abandon if fewer than 3/5 pass

results = []
for i in range(trials):
    score = run_eval(candidate_prompt, scenarios)
    results.append(score)
    # Early exit: if 3 have already failed, abandon
    failures = sum(1 for r in results if r < passing_score)
    if failures > (trials - pass_threshold):
        REVERT — unstable mutation
        break

if median(results) > median(baseline_results):
    KEEP
else:
    REVERT
```

**Why 5 trials:** 3 trials showed high variance — prompts that won 2/3 frequently lost on subsequent runs. 5 trials with a 3/5 minimum and median comparison provides sufficient signal without excessive cost. Adjust upward (7 or 10 trials) for high-stakes prompts where a false positive is expensive.

### Final Validation

After the optimization loop converges (no improvement for N iterations), re-test the winning prompt **5 additional times** with a stricter threshold:

```
final_trials = 5
final_threshold = 4  # require 4/5 passes

for i in range(final_trials):
    score = run_eval(winning_prompt, scenarios)
    if score < passing_score:
        failures += 1
    if failures > (final_trials - final_threshold):
        WARN — winning prompt is not stable enough for production
        # Fall back to the last prompt that passed final validation,
        # or the original baseline if no candidate passed
        break
```

**The final validation gate prevents shipping a prompt that won the optimization tournament through luck.** A prompt that can't achieve 4/5 passes under clean conditions should not replace the baseline.

### Context Isolation for Stability

Each trial must run with **fresh context** — no shared conversation history, no cached results, no prior trial outputs. This prevents the agent from using memory of previous trial runs to improve subsequent ones (which would inflate the pass rate without the prompt itself being better).

When using `Task` subagents for trials, each trial is a separate `Task` call. When using direct execution, clear any conversation state between runs.

## Exploration Strategy: Greedy vs. Population-Based

Two modes for navigating the prompt search space. **Default is greedy** — use population-based only when the conditions below are met.

### Greedy (Default)

The standard keep/revert loop. One candidate prompt at a time. Edit → eval → keep if better, revert if worse. Fast, simple, sufficient for most optimization tasks.

**Use when:** Single metric target, <5 eval scenarios, or homogeneous eval distribution (all scenarios test the same capability).

### Population-Based (GEPA-Inspired)

Maintain a pool of 3–5 candidate prompts instead of one. Inspired by the GEPA optimizer ([Agrawal 2025](https://arxiv.org/abs/2502.02858)) which uses Pareto-optimal selection across heterogeneous evaluation queries. In the Zeta Alpha Deep Research study ([Câmara et al. 2026](https://arxiv.org/abs/2604.02988)), population-based exploration outperformed greedy search (0.705 vs 0.654 from minimal prompts) because different prompts excelled on different query types.

**Use when:** ≥5 diverse eval scenarios AND scenarios test different capabilities (e.g., planning vs. synthesis vs. citation accuracy). The diversity is what makes population worth the overhead.

**Protocol:**

1. **Initialize:** Create 3 variants of the baseline prompt (e.g., one emphasizing precision, one brevity, one coverage). Store in `.autoresearch/population/candidate-{N}.md`.
2. **Evaluate all candidates** against the full eval suite. Record per-scenario scores in `.autoresearch/population/scores.tsv`.
3. **Prune dominated candidates** — a candidate is dominated if another candidate beats it on _every_ scenario. Remove dominated candidates from the pool.
4. **Select next parent** — sample a candidate with probability proportional to its Pareto support (number of scenarios where it's the best or tied-for-best).
5. **Mutate** — apply one atomic edit to the selected parent (same rules as greedy: one change, one sentence description).
6. **Evaluate the child** against the full eval suite.
7. **Discard if no improvement** — if the child doesn't beat the parent on _any_ scenario, discard it (don't add to pool). This prevents population bloat.
8. **Repeat from step 3.**

**Post-loop:** The final deliverable is the candidate with the highest aggregate score across all scenarios. Report the full Pareto frontier so the human can choose a different trade-off if desired.

**Cost note:** Population-based runs N× more evals per round. Budget accordingly — the Zeta Alpha study used $50/round with GPT-4.1-mini.

## Scope Guidance

- One prompt file per autoresearch run (greedy) or one prompt file per candidate (population-based)
- The eval scenarios are the guard — never edit them during the optimization
- Track prompt length as a secondary metric (smaller is better, all else equal)

## Multi-Agent Co-Optimization

When multiple prompts interact in a pipeline (e.g., research → planning → implementation), optimizing one in isolation can miss downstream effects. The Zeta Alpha study ([Câmara et al. 2026](https://arxiv.org/abs/2604.02988)) optimizes their 4-agent system by updating one agent's prompt per step in round-robin while holding the others fixed.

**Use when:** The prompt being optimized feeds into or receives from other agent prompts, and the eval measures the _end-to-end_ output (not just the individual agent's output).

**Skip when:** The prompt is standalone (e.g., a formatting skill, a single-turn tool) with no downstream consumers.

**Protocol:**

1. **Identify the agent chain** — list all prompts involved in the end-to-end pipeline being evaluated. Example: `research-orchestrator.md → external-research.md → plan-generator SKILL.md → implementation SKILL.md`.
2. **Fix all but one.** Pick the first agent in the chain. Mark all other prompt files as read-only for this round.
3. **Optimize the selected agent** using greedy or population-based strategy. The eval must judge the _final pipeline output_, not the intermediate output of the agent being optimized.
4. **Rotate.** Move to the next agent in the chain. The prior agent's optimized prompt is now fixed.
5. **Repeat** for one full rotation through all agents. Multiple rotations show diminishing returns — the paper found 2–3 full rotations sufficient.

**Why round-robin beats simultaneous:** Changing all prompts at once creates a moving target — you can't attribute improvement or regression to any single agent. Round-robin isolates the effect of each prompt change against a stable context.

**Practical note:** This is expensive — each round requires end-to-end pipeline runs. Reserve for high-value prompt chains (e.g., a multi-stage content or coding pipeline) where prompt quality directly affects output quality. For most single-skill optimization, standard single-prompt autoresearch is sufficient.

## Guard

The guard for prompt optimization is the eval suite itself — if the score drops, revert. No separate guard command is needed unless the prompt is embedded in code that needs to compile/lint.

## The AutoVoiceEvals Scoring Pattern

A useful composite scoring formula:

```
composite = 0.50 * should_score + 0.35 * should_not_score + 0.15 * efficiency_score
```

- **should_score** — fraction of "the agent should do X" criteria passed
- **should_not_score** — fraction of "the agent should NOT do X" criteria passed
- **efficiency_score** — brevity, speed, or cost metric

## Creating an Eval Suite

If no eval suite exists, create one before starting the loop.

### Binary Eval Template

The most reliable scoring method for prompt optimization is **binary evals** — yes/no questions about the output. Define 3–6 evals per skill (sweet spot). More than 6 and the skill starts gaming the checklist without improving overall quality.

```
EVAL 1: [Short name]
Question: [Yes/no question about the output]
Pass condition: [What "yes" looks like — be specific]
Fail condition: [What triggers a "no"]

EVAL 2: [Short name]
Question: ...
```

**Score formula:** `max_score = [num_evals] × [runs_per_experiment]` (e.g., 4 evals × 5 runs = max 20).

**Example** (landing page copy skill):

```
EVAL 1: Specific headline
Question: Does the headline include a specific number or result?
Pass condition: Contains a number, percentage, or concrete outcome
Fail condition: Vague promises like "Transform Your Business" or "Grow Faster"

EVAL 2: No buzzwords
Question: Is the copy free of banned buzzwords?
Pass condition: None of: revolutionary, cutting-edge, synergy, next-level, game-changing, leverage, unlock
Fail condition: Any banned word appears

EVAL 3: Specific CTA
Question: Does the CTA use a specific verb phrase?
Pass condition: Action verb + outcome (e.g., "Start your free audit", "Get the checklist")
Fail condition: Generic CTAs like "Learn More", "Click Here", "Get Started"
```

### Eval Quality Self-Test

Before finalizing each eval, it must pass all 3:

1. **Can the agent actually measure this?** — If it requires external tools, user accounts, or subjective taste, it's not a valid binary eval.
2. **Would two humans agree on the answer?** — If reasonable people would disagree on pass/fail, the eval is too vague. Tighten the pass/fail conditions.
3. **Does it overlap with another eval?** — Overlapping evals double-count the same quality, distorting the score. Merge or drop one.

### Scenario-Based Evals (Alternative)

For skills with diverse input types, use a scenario matrix instead of (or alongside) binary evals:

1. **Identify 5–10 representative scenarios** covering normal cases, edge cases, and adversarial inputs
2. **Define pass/fail criteria** for each scenario — what the output MUST contain and MUST NOT contain
3. **Write them as JSON** so the eval script can iterate programmatically
4. **Run the baseline** — the current prompt should pass most scenarios (if it fails many, the prompt needs manual work first, not autoresearch)

```json
{
  "scenarios": [
    {
      "name": "simple bug fix ticket",
      "input": "Fix the typo in README.md line 42",
      "should": ["identify the file", "make minimal change"],
      "should_not": ["refactor surrounding code", "add new features"]
    }
  ]
}
```

### Baseline Confirmation Gate

After running the baseline, check the score before entering the loop:

- **Baseline ≥ 90%** — Ask the user if optimization is even needed. Gains will be marginal (+0.7% in the Zeta Alpha study when starting from expert prompts).
- **Baseline 40–70%** — **Highest ROI zone.** Automated optimization dramatically outperforms manual tuning here. The Zeta Alpha study showed +37% improvement from minimal prompts (0.513→0.705), matching and exceeding year-long expert-crafted prompts. Strongly recommend autoresearch over manual iteration.
- **Baseline < 40%** — The prompt likely needs manual rewriting first, not autoresearch. The loop works best on prompts that are "mostly right" but inconsistent.

**Key insight:** The weaker the starting prompt, the higher the ROI of automated optimization vs. manual tuning ([Câmara et al. 2026](https://arxiv.org/abs/2604.02988)). Don't waste time hand-tuning a mediocre prompt — let the loop find what works.
