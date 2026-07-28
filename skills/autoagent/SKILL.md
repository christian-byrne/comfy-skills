---
name: autoagent
description: "Clone an external agent repo and autonomously optimize its harness (prompts, tools, orchestration) overnight via the autoresearch loop. Use when asked to 'autoagent this repo', 'optimize this agent', 'clone and optimize', 'improve this agent harness', or 'run autoagent on'."
interaction: autonomous
type: orchestrator
---

# AutoAgent — Clone → Configure → Optimize

Takes an external agent repository and autonomously optimizes its harness overnight. This is a thin intake/scaffolding wrapper around the `autoresearch` skill's `agent-harness` domain — it handles the setup that AutoAgent's README assumes you do manually.

Based on [AutoAgent](https://github.com/kevinrgu/autoagent) by Thirdlayer Inc.

## When to Trigger

- "Autoagent this repo" / "clone and optimize this agent"
- "Optimize this agent overnight" / "run autoagent on [url]"
- "Set up an autoresearch loop for this agent repo"
- User pastes a GitHub URL to an agent repo and asks to improve it

## What This Skill Does (and Doesn't Do)

**Does:** Clone → detect harness → mark edit boundary → scaffold tasks → generate program.md → hand off to `autoresearch` (agent-harness domain).

**Doesn't:** Run the loop itself. That's `autoresearch`. This skill is intake only.

## Process

### Step 1: Clone & Inspect

```bash
# Clone into a worktree or temp directory
git clone <REPO_URL> /tmp/autoagent-target
cd /tmp/autoagent-target

# Inventory — what are we working with?
find . -maxdepth 2 -type f | head -40
cat README.md
```

Look for:

- **Existing harness file** — `agent.py`, `agent.ts`, `main.py`, `index.ts`, or similar
- **Existing eval/benchmark setup** — `tasks/`, `evals/`, `tests/`, `benchmarks/`
- **Existing config** — `program.md`, `config.yaml`, `.env.example`
- **Dependencies** — `pyproject.toml`, `package.json`, `requirements.txt`

### Step 2: Detect or Create the Edit Boundary

Scan the harness file for an existing `EDITABLE` / `FIXED` boundary (AutoAgent-style repos already have this). If not present, **create one**.

**Detection patterns:**

```bash
grep -n "EDITABLE\|FIXED.*BOUNDARY\|do not modify" <harness_file>
```

**If no boundary exists**, analyze the harness file and insert comment fences:

```python
# ============================================================================
# EDITABLE HARNESS — prompt, tools, agent construction, orchestration
# ============================================================================

# ... system prompt, model config, tool definitions, agent setup ...

# ============================================================================
# FIXED ADAPTER BOUNDARY — do not modify below this line
# ============================================================================

# ... framework integration, API adapters, entry points ...
```

**Heuristic for the split:** The EDITABLE zone contains anything the meta-agent should tune (prompts, tool lists, model selection, orchestration logic). The FIXED zone contains framework glue, serialization, CLI entry points, and test infrastructure.

### Step 3: Scaffold Tasks (if missing)

If the repo has no eval tasks, help the user create them. Each task follows this structure:

<!-- docs-linter-disable-next-tree -->

```
tasks/<task-name>/
├── instruction.md      # Natural-language prompt for the agent
├── test.sh             # Writes score (0.0–1.0) to /logs/reward.txt
├── files/              # Reference files (if needed)
└── expected/           # Expected outputs (if deterministic)
```

**Minimal `test.sh` template:**

```bash
#!/bin/bash
# Score: 1.0 if output matches expected, 0.0 otherwise
if diff -q /task/output.txt /task/expected/output.txt > /dev/null 2>&1; then
  echo "1.0" > /logs/reward.txt
else
  echo "0.0" > /logs/reward.txt
fi
```

**For LLM-as-judge scoring**, use a `test.py` that calls an LLM to evaluate quality on a rubric and writes a 0.0–1.0 score.

Ask the user:

> I need 3–10 evaluation tasks to optimize against. Each task is: an instruction + a way to score the output. Do you have existing evals, or should I help you create tasks from example inputs/outputs?

### Step 4: Generate `program.md`

Create a `program.md` that the meta-agent will consume. This is the "one markdown file" from AutoAgent's pitch.

**Template:**

````markdown
# Program — [Agent Name] Optimization

## Directive

Build a [description of what the agent should do]. Optimize for task completion
rate across the evaluation suite.

Model: [model name]

## What You Can Modify

In `[harness_file]`, above the FIXED ADAPTER BOUNDARY:

- SYSTEM_PROMPT — role definition, constraints, strategy
- Tool definitions — add specialized tools, rename for clarity
- Agent orchestration — sub-agents, routing, verification loops
- Model config — MAX_TURNS, temperature

## What You Must Not Modify

- Anything below the FIXED ADAPTER BOUNDARY
- Task files in `tasks/`
- Test/scoring logic
- This file (`program.md`)

## How to Run

```bash
[exact command to run all tasks and produce scores]
```
````

## Keep / Discard Rules

- If passed count improved → KEEP
- If passed count is the same AND code is simpler → KEEP
- Otherwise → DISCARD (git revert)

## Failure Analysis

When tasks fail, classify by root cause before choosing the next edit:

- Misunderstanding — agent misinterprets the task
- Missing tool — agent lacks a needed capability
- Silent failure — agent reports success but output is wrong
- Overshoot — agent does more than asked

## Overfitting Guard

After each improvement, ask: "Would this still be worthwhile if this exact
task disappeared?" If no, find a more general fix.

## NEVER STOP

Run the loop continuously. Do not pause for confirmation.

```

### Step 5: Hand Off to Autoresearch

Once the boundary is marked, tasks exist, and `program.md` is generated, hand off:

```

Goal: Improve task completion rate for [agent name]
Scope: [harness_file] (EDITABLE zone only)
Metric: avg_score (higher is better) — or pass_rate, depending on eval setup
Verify: [the run command from program.md that outputs scores]
Guard: [a quick smoke test command, if available]

````

The `autoresearch` skill's `agent-harness` domain handles everything from here — the autonomous loop, keep/revert decisions, failure taxonomy, trace logging.

> **Loop shape: fast loop only.** AutoAgent uses benchmark replay, which makes it a fast-loop (single-session keep/revert) optimization. This is valid because benchmarks are deterministic and repeatable. If you need to optimize agent skills measured by real-world success rates (not benchmarks), use autoresearch's epoch-based loop instead.

## Using AutoAgent Directly

If the user wants the original AutoAgent workflow (Harbor + OpenAI Agents SDK) rather than our autoresearch adaptation:

```bash
# Clone and install
git clone https://github.com/kevinrgu/autoagent /tmp/autoagent
cd /tmp/autoagent
uv sync

# Set credentials
echo 'OPENAI_API_KEY=...' > .env

# Build base image
docker build -f Dockerfile.base -t autoagent-base .

# Add tasks to tasks/ (see references/harbor-task-template/ for skeleton)
# Edit program.md to define your directive

# Run all tasks
rm -rf jobs && mkdir -p jobs && uv run harbor run -p tasks/ -n 100 \
  --agent-import-path agent:AutoAgent -o jobs --job-name latest > run.log 2>&1

# Start the meta-agent loop
# Point your AI coding agent at the repo and prompt:
#   "Read program.md and let's kick off a new experiment!"
````

**When to use this vs. our wrapper:** Use AutoAgent directly when you need Harbor's container isolation, ATIF trajectory output, or the OpenAI Agents SDK specifically. Use our wrapper (Steps 1–5 above) when you want the autoresearch loop with its trace management, stuck detection, and domain routing.

## Notes

- **Docker isolation is recommended.** If the target repo uses Docker/Harbor, use it. If not, at minimum run evals in a sandboxed environment.
- **Cost awareness.** Agent harness optimization burns API tokens. Each iteration = one full eval suite run. Estimate cost per run before starting.
- **The user should sleep.** The whole point is overnight autonomous optimization. Set it up, verify one iteration works, then let it run.
