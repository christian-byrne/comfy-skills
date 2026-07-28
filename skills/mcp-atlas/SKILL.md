---
name: mcp-atlas
description: 'Run MCP-Atlas tool-use evaluations against LLMs. 36 real MCP servers, 220 tools, 500 public tasks with claims-based scoring. Tests tool discovery, parameterization, multi-step orchestration, and error recovery. Use when asked to evaluate tool use, benchmark MCP agents, test tool orchestration, or run mcp-atlas.'
interaction: autonomous
type: leaf
synergies:
  enhances: [autoresearch]
  domain: [tool-use-eval, mcp-benchmark, agent-evaluation]
---

# MCP-Atlas — Tool-Use Competency Benchmark

Benchmark by [Scale AI](https://scale.com/blog/open-sourcing-mcp-atlas) measuring how well LLMs handle real tool use via MCP.

**Paper:** [arXiv:2602.00933](https://arxiv.org/abs/2602.00933)
**Repo:** [github.com/scaleapi/mcp-atlas](https://github.com/scaleapi/mcp-atlas)
**Dataset:** [HuggingFace ScaleAI/MCP-Atlas](https://huggingface.co/datasets/ScaleAI/MCP-Atlas) (500 public tasks)
**Leaderboard:** [scale.com/leaderboard/mcp_atlas](https://scale.com/leaderboard/mcp_atlas)

## What It Tests

| Dimension       | Detail                                                                 |
| --------------- | ---------------------------------------------------------------------- |
| Servers         | 36 real MCP servers (search, code exec, databases, APIs, productivity) |
| Tools           | 220 tools across servers                                               |
| Tasks           | 1,000 total (500 public, 500 held-out)                                 |
| Tool calls/task | 3–6, usually cross-server                                              |
| Scoring         | Claims-based rubric with partial credit                                |
| Prompt style    | Natural language — no tool names, agents must discover                 |

Key insight: **tool discovery and parameterization are the dominant bottleneck**, not answer synthesis. When tools are used correctly, the final answer is rarely wrong.

## Reference Scores (as of 2026-02)

| Model           | Pass Rate      | Coverage |
| --------------- | -------------- | -------- |
| Claude Opus 4.5 | 62.3%          | 78.5%    |
| Gemini 3 Pro    | 54.1%          | 73.2%    |
| GLM-5           | 67.8% (public) | —        |
| GPT-5           | 44.5%          | 61.8%    |
| GPT-5.2         | 68.0% (public) | —        |

## Setup

Prerequisites: Docker, uv, jq, Python 3.10+.

```bash
# Clone and configure
git clone git@github.com:scaleapi/mcp-atlas.git
cd mcp-atlas
cp env.template .env

# Edit .env — required keys:
# LLM_API_KEY     — model to evaluate
# EVAL_LLM_API_KEY — judge model (default: gemini-2.5-pro)
```

### Start Services

```bash
# Terminal 1: MCP servers (36 servers in Docker)
make run-mcp-servers

# Terminal 2: Completion service (agentic loop)
make run-mcp-completion
```

### Run Evaluation

```bash
cd services/mcp_eval

# Quick test (10 tasks, no API keys needed for 20/36 servers)
uv run python mcp_completion_script.py \
  --model "openai/gpt-5.1" \
  --input "sample_tasks.csv" \
  --output "sample_results.csv"

# Full evaluation (500 tasks from HuggingFace)
uv run python mcp_completion_script.py \
  --model "openai/gpt-5.1" \
  --input_huggingface "ScaleAI/MCP-Atlas" \
  --output "full_results.csv"

# Score results
uv run mcp_evals_scores.py \
  --input-file="completion_results/full_results.csv" \
  --model-label="gpt51"
```

Options: `--concurrency 10` (5-20), `--num-tasks N` (limit), `--no-filter` (skip server availability check).

### Add API Keys for More Coverage

Without extra API keys, only ~18% of tasks run (20 default servers). Key servers by task coverage:

```
exa: 13% | airtable: 12% | mongodb: 12% | oxylabs: 11% | brave-search: 10%
alchemy: 8% | national-parks: 8% | twelvedata: 8% | lara-translate: 7%
```

Five servers also need sample data uploaded (Airtable, Google Calendar, Notion, MongoDB, Slack) — see `data_exports/README.md`.

## Failure Taxonomy

| Failure Mode         | Frequency | Description                                               |
| -------------------- | --------- | --------------------------------------------------------- |
| Wrong tool selection | High      | Picked a plausible but incorrect tool                     |
| Bad parameterization | High      | Right tool, wrong arguments                               |
| No tool use at all   | Medium    | Agent stopped early or didn't recognize tools were needed |
| Sequencing errors    | Medium    | Right tools, wrong order                                  |
| Synthesis errors     | Low       | Correct tool use, mangled final answer                    |

## Interpreting Results

| Metric    | What It Means                                  |
| --------- | ---------------------------------------------- |
| Pass Rate | % of tasks with coverage ≥ 0.75                |
| Coverage  | Mean fraction of ground-truth claims satisfied |

Outputs saved to `evaluation_results/`: scored CSV, summary stats, histogram PNG.

## Applying the Results

Use MCP-Atlas to evaluate the tool-use quality of your own agents:

1. **Baseline** — run current model on the 500 public tasks
2. **Compare** — test model upgrades, prompt changes, or MCP server additions
3. **Diagnose** — use failure taxonomy to identify weak spots (discovery vs parameterization vs sequencing)
4. **Track** — monitor pass rate over time as a regression signal
