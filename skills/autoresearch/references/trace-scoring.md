# Trace-Derived Reward Scoring

Optimize agent-pipeline session quality using multi-dimensional reward signals derived from production traces. Inspired by Cursor's real-time RL approach (edit persistence + dissatisfaction + latency) and Baseten's environment-driven RL (trace-derived rewards without sandbox state access).

**Requirements:** this domain assumes you have a production system that runs agent sessions and logs structured outcomes (merged?, review comments, cost, duration) somewhere queryable — your own API, a database, or exported logs. The API and file paths below are illustrative placeholders for your own telemetry.

## When to Use

- Optimizing skill prompts or instructions for better pipeline outcomes
- Tuning dispatch scoring or complexity classification
- Improving autoresearch's own iteration quality
- Any optimization where the metric is derived from pipeline session traces rather than a single benchmark command

## Typical Metrics

Unlike other autoresearch domains that have one scalar metric, trace scoring uses a **composite reward function** — multiple signals combined into a single score.

| Signal                  | Unit    | Direction | Extraction                                   | Weight |
| ----------------------- | ------- | --------- | -------------------------------------------- | ------ |
| `merge_rate`            | 0-1     | ↑ higher  | PR merged? (from GitHub API)                 | 0.30   |
| `review_pass_first_try` | 0-1     | ↑ higher  | No review comments requiring changes?        | 0.20   |
| `cost_efficiency`       | 0-1     | ↑ higher  | `1 - (actual_cost / budget)`                 | 0.15   |
| `cycle_time_ratio`      | 0-1     | ↑ higher  | `1 - (actual_time / expected_time)`, clamped | 0.15   |
| `scope_adherence`       | 0-1     | ↑ higher  | No out-of-scope changes detected?            | 0.10   |
| `test_delta`            | -1 to 1 | ↑ higher  | Test coverage change (positive = better)     | 0.10   |

### Composite Score

```
R(session) = Σ(weight_i × signal_i) - penalties

Penalties:
  - 0.2 × scope_creep (binary: any out-of-scope changes?)
  - 0.3 × revert (binary: any commits reverted post-merge?)
```

**Adapt weights to your optimization goal.** If optimizing for speed, increase `cycle_time_ratio` weight. If optimizing for quality, increase `review_pass_first_try` and `merge_rate`.

### Trace-Level Metrics

For finer-grained optimization using a trace-recording module (your own equivalent of a `TraceRecorder`):

| Metric Name         | Unit  | Direction | Extraction                                                   |
| ------------------- | ----- | --------- | ------------------------------------------------------------ |
| `success_rate`      | ratio | ↑ higher  | `traceSummary.successRate`                                   |
| `total_actions`     | count | ↓ lower   | `traceSummary.totalActions` (fewer actions = more efficient) |
| `phase_duration_ms` | ms    | ↓ lower   | `traceSummary.phaseBreakdown[phase].durationMs`              |
| `retry_count`       | count | ↓ lower   | Count of repeated actions on the same file/tool              |
| `bounce_count`      | count | ↓ lower   | Number of phase regressions (e.g., QA → IMPLEMENTATION)      |

## Metric Extraction

### From Production API

```bash
API="<YOUR_TELEMETRY_API>"   # e.g. https://your-api.example.com

# Recent pipeline runs with outcomes
curl -s "$API/api/pipeline-runs?status=completed&limit=20" | jq '
  .[] | {
    id: .id,
    ticket: .ticket_url,
    merged: .pr_merged,
    review_comments: .review_comment_count,
    cost_usd: .total_cost_usd,
    duration_minutes: .duration_minutes,
    skills_used: .skills
  }
'
```

### From Skill Execution Logs

```bash
# Skill health — which skills are degrading?
curl -s "$API/api/skill-health/degrading" | jq '.[] | {skill: .skill_name, trend: .trend, score: .score}'

# Postmortem analyses — root causes of failures
curl -s "$API/api/postmortem/recent" | jq '.[] | {category: .category, severity: .severity, cause: .root_cause}'
```

### Verify Script Pattern

```bash
#!/bin/bash
set -e

API="<YOUR_TELEMETRY_API>"

# Guard: quality gates must pass
pnpm typecheck > /dev/null 2>&1
pnpm test:unit > /dev/null 2>&1

# Fetch last N completed runs
runs=$(curl -s "$API/api/pipeline-runs?status=completed&limit=10")

# Compute composite score
merge_rate=$(echo "$runs" | jq '[.[] | .pr_merged] | map(if . then 1 else 0 end) | add / length')
first_try_rate=$(echo "$runs" | jq '[.[] | select(.review_comment_count == 0)] | length / ([.[] | length] | add)')
avg_cost_ratio=$(echo "$runs" | jq '[.[] | (1 - (.total_cost_usd / .budget_usd))] | add / length')

# Weighted composite
score=$(echo "$merge_rate * 0.30 + $first_try_rate * 0.20 + $avg_cost_ratio * 0.15" | bc -l)

echo "METRIC composite_score=$score"
```

## Scope Selection

What you can optimize using trace-derived scoring:

| Target                     | Scope (example)           | What Changes                                 |
| -------------------------- | ------------------------- | -------------------------------------------- |
| **Skill prompts**          | `skills/{skill}/SKILL.md` | Prompt wording, instructions, examples       |
| **Dispatch scoring**       | `src/dispatch/`           | How tasks are scored and routed              |
| **Review checks**          | `.agents/checks/*.md`     | What reviewers look for, severity thresholds |
| **Complexity classifier**  | `src/complexity/`         | How task difficulty is assessed              |
| **Behavioral guardrails**  | your agent config         | Behavioral guardrails for agents             |
| **Research agent prompts** | `prompts/research/*.md`   | Faster research phase                        |

## Guard Command

The guard for trace-scoring optimizations is your existing quality gates, e.g.:

```bash
pnpm typecheck && pnpm test:unit
```

**Critical:** trace-scoring autoresearch must NOT modify files that would break the pipeline. The guard prevents regressions.

## Key Differences from Other Domains

| Aspect          | Standard Autoresearch     | Trace Scoring                                        |
| --------------- | ------------------------- | ---------------------------------------------------- |
| Metric source   | Single benchmark command  | Multi-signal from production traces                  |
| Iteration speed | Seconds per experiment    | Hours/days per experiment (needs real pipeline runs) |
| Feedback delay  | Immediate                 | Delayed (wait for sessions to complete)              |
| Sample size     | 1 experiment = 1 metric   | 1 experiment = N pipeline runs averaged              |
| Risk            | Low (revert code changes) | Medium (prompt changes affect real dispatches)       |

## Reward Hacking Risks

Trace-derived scoring is vulnerable to reward hacking, the same class of failure documented in Cursor's real-time RL case study:

- **Scope reduction gaming** — agent narrows task scope to guarantee merge, inflating merge_rate
- **Trivial test inflation** — adding empty/trivial tests to boost test_delta
- **Cost gaming** — producing minimal output to reduce cost_usd, sacrificing quality

**Mitigation:** Multi-dimensional scoring makes single-metric gaming harder. Human review gates catch qualitative degradation. The `review_pass_first_try` signal provides a human-in-the-loop check.

## Integration with Traces Review

Automated scoring complements manual traces review:

- **Automated**: Run after every pipeline session, flag regressions
- **Manual**: Deep-dive flagged sessions during weekly "traces hour"
- **Feedback loop**: Manual findings → prompt/skill edits → automated scoring validates improvement
