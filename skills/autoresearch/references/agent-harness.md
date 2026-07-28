# Agent Harness Optimization

Optimize an agent's harness — system prompt, tools, orchestration, and sub-agents — against an evaluation suite. Based on the [AutoAgent](https://github.com/kevinrgu/autoagent) pattern: a meta-agent iterates on a task-agent's harness, measuring score against benchmarks or eval tasks.

## Typical Metrics

| Metric Name | Unit    | Direction | Extraction Example                          |
| ----------- | ------- | --------- | ------------------------------------------- |
| `pass_rate` | 0.0–1.0 | ↑ higher  | `grep "passed" run.log \| wc -l` / total    |
| `avg_score` | 0.0–1.0 | ↑ higher  | Mean of per-task scores from eval runner    |
| `cost_usd`  | dollars | ↓ lower   | Sum of API costs per run (secondary metric) |
| `avg_turns` | integer | ↓ lower   | Mean turns per task (efficiency proxy)      |

## Edit Surface (Two-Zone File Pattern)

Any file that an agent iteratively modifies should have a clearly marked **edit boundary** splitting it into an EDITABLE zone (what the agent may change) and a FIXED zone (adapter/infrastructure that must not change). This prevents agents from accidentally modifying framework plumbing, eval harnesses, or structural scaffolding during optimization loops.

The pattern generalizes beyond Python — use the native comment syntax for each file type:

**Python / Shell:**

```python
# ============================================================================
# EDITABLE HARNESS — prompt, tools, agent construction, orchestration
# ============================================================================
SYSTEM_PROMPT = "..."
MODEL = "..."
MAX_TURNS = 30

def create_tools(environment): ...
def create_agent(environment): ...
async def run_task(environment, instruction): ...

# ============================================================================
# FIXED ADAPTER BOUNDARY — do not modify below this line
# ============================================================================
```

**Markdown (skills, prompts):**

```markdown
<!-- EDITABLE — optimize the content below -->

## System Prompt

You are a helpful assistant that...

<!-- FIXED BOUNDARY — do not modify below this line -->

## Parent Graph

Part of: `autoresearch`
```

**YAML (configs, templates):**

```yaml
# EDITABLE — tune parameters below
model: claude-sonnet-4-20250514
temperature: 0.7
max_tokens: 4096

# FIXED BOUNDARY — do not modify below this line
schema_version: 2
required_fields: [model, temperature]
```

**Scope** for autoresearch = the EDITABLE zone only. Never touch the adapter or fixed boundary.

## What the Meta-Agent May Change

| Component         | Examples                                                     |
| ----------------- | ------------------------------------------------------------ |
| **System prompt** | Role definition, constraints, strategy hints, examples       |
| **Tools**         | Add specialized tools, rename for clarity, adjust parameters |
| **Orchestration** | Sub-agent handoffs, verification loops, retry logic          |
| **Model config**  | MAX_TURNS, temperature, model selection                      |

## What the Meta-Agent Must NOT Change

- The eval harness / scoring logic
- The adapter boundary (framework integration)
- Task files or test suites
- The experiment loop itself

## Pre-Optimization Diagnostic

Before running the optimization loop, score the harness across five subsystems (1–5 each) to identify the weakest link. Optimizing a well-scored subsystem while a 1-rated subsystem exists wastes iterations.

| Subsystem        | What to Check                                                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| **Instructions** | Does the agent have clear, layered guidance? (AGENTS.md, progressive disclosure)                     |
| **State**        | Can the agent resume after interruption? (progress files, structured feature tracking with evidence) |
| **Verification** | Is the agent required to prove completion? (verification commands, evidence recording)               |
| **Scope**        | Is the agent constrained to one task at a time? (feature list, definition of done)                   |
| **Lifecycle**    | Does the session have init/cleanup? (init script, clean state commit)                                |

Score each 1–5, then **target the lowest-scoring subsystem first** in the EDITABLE zone.

## Harness Edit Strategies

Ordered by typical impact:

1. **Add specialized tools** — replace generic `run_shell` with domain-specific tools (`inspect_file`, `validate_output`). Models pattern-match tool names before reading descriptions — name tools for what they _mean_.
2. **Add verification sub-agents** — wrap a checker agent that re-reads the output against the task requirements before reporting completion. Catches silent failures.
3. **Restructure orchestration** — add task-specific routing, progressive disclosure (dump large contexts to files), or multi-step pipelines.
4. **Tighten the system prompt** — add failure-class-specific guidance after diagnosing common failure patterns.
5. **Adjust turn budget** — increase MAX_TURNS if tasks are truncating, decrease if the agent is wasting turns on dead ends.
6. **Budget allocation** — reserve bonus turns for self-verification after the main task is complete.

## Failure Taxonomy

When diagnosing why the agent fails tasks, classify by root cause (see also: autonomous-loop-protocol.md Phase 2):

| Class                      | Signal                                      | Typical Fix                     |
| -------------------------- | ------------------------------------------- | ------------------------------- |
| **Misunderstanding**       | Agent misinterprets the task                | Clarify prompt, add examples    |
| **Missing tool**           | Agent tries to do something it can't        | Add a specialized tool          |
| **Weak info gathering**    | Agent acts before understanding the problem | Add exploration steps           |
| **Bad execution strategy** | Right idea, wrong approach                  | Restructure orchestration       |
| **Silent failure**         | Reports success, output is wrong            | Add verification sub-agent      |
| **Overshoot**              | Does more than asked, breaks constraints    | Tighten scope in prompt         |
| **Verification mismatch**  | Self-check passes, eval fails               | Align internal checks with eval |

## Model Empathy

Design the harness for how the task-agent model reasons, not how you reason:

- **Tool names are priors** — `inspect_workbook` beats `run_shell("python -c 'import openpyxl...'")`
- **Same-model pairing** — when meta-agent and task-agent share a model family, the meta-agent writes better harnesses because it implicitly understands the task-agent's tendencies
- **Progressive disclosure** — write large outputs to files, return summaries. Keep conversation context for reasoning, not storage.

## Overfitting Guard

After each improvement, ask: **"Would this still be worthwhile if this exact task disappeared?"**

If the answer is no, you're overfitting to the benchmark. Find a more general fix that addresses the class of failure, not the specific task.

## Bootstrap via `program.md`

When optimizing an unfamiliar harness (especially one you didn't write), create a standalone `program.md` that a fresh meta-agent can consume cold — no prior context needed. This is the key insight from [AutoAgent](https://github.com/kevinrgu/autoagent): the entire optimization protocol lives in one file.

A good `program.md` contains:

- **Directive** — what kind of agent to build, which model to use
- **Edit permissions** — exactly which variables/functions the meta-agent may change
- **Run commands** — exact shell commands to rebuild and evaluate
- **Keep/discard rules** — when to commit vs. revert (default: improved pass count → keep; same passes + simpler code → keep; else discard)
- **Failure taxonomy** — categories of failure to look for (see table above)
- **Anti-overfit heuristic** — "Would this still be worthwhile if this exact task disappeared?"
- **NEVER STOP** — explicit instruction to loop without pausing for confirmation

This makes the optimization portable — hand `program.md` to any AI coding agent and it bootstraps the full loop.

## Trajectory Standardization

For reproducibility and cross-tool analysis, consider serializing agent runs into a structured trajectory format. AutoAgent uses **ATIF v1.6** (Agent Trajectory Interchange Format) — a JSON schema that captures each turn's message outputs, reasoning items, tool calls, tool results, and token usage. This is distinct from the `.autoresearch/traces/` execution logs (which capture the meta-agent's experiment loop) — trajectories capture what the _task agent_ did during a single eval run.

Trajectory files are useful for:

- **Post-hoc failure analysis** — see exactly which tool calls led to a wrong answer
- **Cross-model comparison** — run the same tasks with different models and diff trajectories
- **Cost attribution** — token usage per turn reveals where the agent wastes budget

## Guard & Regression Suite

For agent harness optimization, **always enable suite gating** (see `autonomous-loop-protocol.md` Phase 5.7). Agent benchmarks have stable task IDs, making them ideal for the auto-growing regression suite. The three-step gate:

1. **Regression suite** — run only previously-fixed tasks (`suite.json`). Pass rate must be ≥ threshold (default 80%). This is fast — a subset of the full benchmark.
2. **Full benchmark** — run the complete test/validation split. Score must be ≥ best ever seen.
3. **Suite promotion** — newly-passing tasks auto-enter the suite as permanent constraints.

The smoke-test guard (does it crash on 3–5 tasks?) runs first as a fast pre-filter before the suite gate. If the smoke test fails, skip the suite gate entirely — no point running it on broken code.

## Quick Start Example

```
/skill autoresearch
Goal: Improve task completion rate for the coding agent harness
Scope: agent.py (EDITABLE zone only)
Metric: avg_score (higher is better)
Verify: uv run harbor run -p tasks/ -n 10 --agent-import-path agent:AutoAgent -o jobs --job-name latest > run.log 2>&1 && python -c "import json; scores=[...]; print(f'METRIC avg_score={sum(scores)/len(scores):.3f}')"
Guard: uv run harbor run -p tasks/ --task-name smoke-test -l 1 -n 1 --agent-import-path agent:AutoAgent -o jobs > /dev/null 2>&1
```
