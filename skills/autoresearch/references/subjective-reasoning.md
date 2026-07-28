# Subjective Reasoning (AutoReason)

Optimize prose, arguments, marketing copy, or any output where no numeric metric exists natively. Instead of measuring a number, manufacture a synthetic fitness function through adversarial debate and blind judging. Based on [SHL0MS's AutoReason](https://x.com/SHL0MS/status/2037939506733523025) pattern.

## When to Use

- Writing that needs to be more persuasive, clear, or compelling
- Arguments that need to be logically tighter
- Marketing copy, pitch decks, proposals
- Prompt/skill text where binary evals don't capture quality
- Any prose optimization where "better" is subjective

**When NOT to use:** If you can define a numeric metric (success rate, word count, readability score), use `prompt-optimization.md` or `code-quality.md` instead. Numeric metrics are always more reliable than synthetic judging. Only use this domain when the quality is genuinely subjective.

## How It Differs from Standard Autoresearch

| Standard Autoresearch                           | Subjective Reasoning                                              |
| ----------------------------------------------- | ----------------------------------------------------------------- |
| Metric exists in the domain (loss, time, score) | Metric is manufactured via agent debate                           |
| Single agent edits → verify → keep/revert       | Multi-agent loop: draft → critique → rewrite → synthesize → judge |
| Mechanical verification (number goes up/down)   | Blind panel judging with Borda count                              |
| Convergence: metric plateaus                    | Convergence: incumbent wins N consecutive rounds                  |

The core loop from `autonomous-loop-protocol.md` is **replaced** by the debate loop below. Do not use the standard edit→commit→verify→decide cycle for this domain.

## The Debate Loop

### Phase 0: Initialization

```
1. Identify the TASK — what the prose should achieve (persuade, explain, argue)
2. Identify the SCOPE — the file(s) containing the prose to optimize
3. Read the current prose as version A₀ (the baseline)
4. Create experiment branch: git checkout -b autoresearch/subjective-<tag>
5. mkdir -p .autoresearch/traces/round-0
6. Copy baseline: cp <SCOPE_FILES> .autoresearch/traces/round-0/version-A.md
7. Set streak = 0, round = 0
```

### Phase 1: Strawman Critique

Spawn a **fresh agent** (via `handoff` or `Task` with minimal context) whose only job is to attack version A. This agent receives:

- The original task description
- Version A (the current best)
- **Nothing else** — no history, no prior critiques, no author context

Prompt template for the strawman agent:

```
You are a harsh but fair critic. Your job is to find every weakness in this text.

TASK: {task_description}
TEXT TO CRITIQUE:
{version_A}

Rules:
- List ONLY problems. Do NOT suggest fixes.
- Be specific — cite exact phrases that are weak and explain WHY.
- Consider: logical gaps, unsupported claims, weak rhetoric, unclear structure,
  missing counterarguments, tone mismatches, redundancy.
- Do NOT praise any part of the text.

Output a numbered list of problems, most severe first.
```

Save output to `.autoresearch/traces/round-{N}/critique.md`.

**Why problems-only:** Forcing pure criticism without fixes prevents the compromising tendency where LLMs soften critique with solutions. The critique must be adversarial by design.

### Phase 2: Three-Candidate Generation

Generate three candidates in parallel, each via a **fresh agent** with isolated context:

#### Candidate A — Keep (unchanged)

The current version A. No agent needed — it's the incumbent.

#### Candidate B — Rewrite

Fresh agent receives:

- The original task description
- Version A
- The strawman critique from Phase 1
- **No other history**

```
You are a skilled writer. Rewrite this text to address the critique while
preserving its strengths.

TASK: {task_description}
CURRENT VERSION:
{version_A}
CRITIQUE:
{critique}

Write a complete new version. Do not reference the critique in your output —
the reader should never know a critique existed.
```

Save to `.autoresearch/traces/round-{N}/version-B.md`.

#### Candidate AB — Synthesize

Fresh agent receives:

- The original task description
- Version A
- Version B
- **No critique, no history**

```
You are an editor merging two drafts. Both attempt the same task.
Take the strongest elements of each and produce a unified version
that is better than either alone.

TASK: {task_description}
DRAFT 1:
{version_A}
DRAFT 2:
{version_B}

Produce a single merged version. Do not label which parts came from which draft.
```

Save to `.autoresearch/traces/round-{N}/version-AB.md`.

### Phase 3: Blind Judge Panel

Spawn **3 fresh judge agents** in parallel. Each judge receives all three candidates with **randomized labels** (shuffled assignment of X/Y/Z to A/B/AB). No judge knows which is the original, the rewrite, or the synthesis.

```
You are an expert evaluator. Rank these three texts from best to worst
for the given task. Be decisive — no ties.

TASK: {task_description}

TEXT X:
{randomized_candidate_1}

TEXT Y:
{randomized_candidate_2}

TEXT Z:
{randomized_candidate_3}

For each text, briefly explain its strengths and weaknesses.
Then output your final ranking:

RANKING:
1. [X/Y/Z] — [one-sentence reason]
2. [X/Y/Z] — [one-sentence reason]
3. [X/Y/Z] — [one-sentence reason]
```

**Aggregate via Borda count:** 1st place = 2 points, 2nd = 1 point, 3rd = 0 points. Sum across all 3 judges. Highest total wins.

**Tie-breaking:** If two candidates tie, prefer the shorter one (simplicity wins, per autoresearch rule 6). If still tied, prefer A (the incumbent — conservative bias toward stability).

### Phase 4: Convergence Check

```
winner = candidate with highest Borda score
if winner == A:
    streak += 1
else:
    streak = 0
    A = winner  # winner becomes new incumbent
    cp winner.md → version-A.md for next round

if streak >= 2:
    STOP — converged. The incumbent survived 2 consecutive challenges.
else:
    round += 1
    goto Phase 1
```

### Phase 5: Log

After each round:

```bash
echo -e "${round}\t${winner}\t${borda_A}/${borda_B}/${borda_AB}\t${streak}\t${description}" \
  >> autoresearch-results.tsv
```

Print one-line status:

```
[round 3] winner=AB (borda: A=2, B=1, AB=6) streak=0 → new incumbent from synthesis
[round 4] winner=A (borda: A=5, B=3, AB=1) streak=1 → incumbent held
[round 5] winner=A (borda: A=4, B=2, AB=3) streak=2 → CONVERGED
```

## Critical Rules (Subjective Domain)

1. **Context isolation is load-bearing.** Every agent in the loop gets FRESH context with ONLY the inputs listed above. No shared history, no prior round results, no author attribution. This is the core anti-sycophancy mechanism. See also `prompt-optimization.md` → "Context Isolation for Stability" and "Anti-Cheating Rules" for the same principle applied to automated prompt optimization loops.
2. **Randomize judge labels every round.** Never present candidates in the same order or with the same labels. Position bias is real in LLM evaluation.
3. **3 judges minimum.** A single judge is unreliable. 3 judges with Borda count provides robust aggregation.
4. **Streak of 2 for convergence.** The incumbent must win 2 consecutive rounds to prove stability. Adjust to 3 for high-stakes prose.
5. **Max 8 rounds.** If convergence hasn't happened by round 8, stop and present the current incumbent. Infinite loops on subjective work waste tokens without guaranteed improvement.
6. **Human spot-check every 3 rounds.** Print versions A, B, and AB at rounds 3 and 6 for human review. Synthetic judging can be Goodharted — the prose might optimize for "judge-friendly" rather than "actually good." A human glance catches this.
7. **Never stop on round 1.** Even if A wins round 1, it hasn't been challenged enough. Run at least 2 rounds.

## Goodhart Warning

> "Every proxy metric in history has eventually been Goodharted." — [mmntm.net analysis](https://www.mmntm.net/articles/autoresearch-overnight-loop)

The blind judge panel is a **synthetic** fitness function. It measures "survives adversarial scrutiny from LLM evaluators" — which correlates with quality but is not identical to it. Over many iterations, the loop may converge on text that is:

- Maximally persuasive to LLM judges but hollow to humans
- Rhetorically polished but factually weakened
- Structurally "safe" (no bold claims) because bold claims get attacked

**Mitigations:**

- Human spot-checks at rounds 3 and 6 (rule 6 above)
- Max 8 rounds cap (rule 5)
- Prefer the incumbent on ties (conservative bias)
- The strawman agent's problems-only constraint prevents the loop from becoming a mutual-admiration cycle

## Quick Start

```
/skill autoresearch
Goal: Make this proposal more compelling to technical decision-makers
Scope: docs/proposal.md
Metric: win_rate via blind judge panel (higher is better)
```

The agent will read this reference file, run the debate loop, and present the converged version with a summary of what changed across rounds.

## Implementation Notes

**Using handoff for isolation:** When spawning debate agents, use `handoff` with a focused goal string that includes ONLY the required inputs. Do not pass thread context.

**Using Task for parallelism:** Candidates B and AB can be generated in parallel (B only needs A + critique; AB only needs A + B). The 3 judges can also run in parallel. This means each round has ~3 sequential steps: critique → generate candidates → judge.

**Standalone judging:** The blind Borda-count judging pattern (Phase 3) can also be used on its own — spawn the judge panel directly against existing candidates — when you need a one-shot decision without running the full debate loop.

**Token cost:** Each round uses ~5 agent calls (1 strawman + 2 candidates + 3 judges, minus A which is free). Budget ~50K tokens per round. 8 rounds max = ~400K tokens. This is comparable to a long autoresearch run on code.

**Tracing:** All intermediate artifacts go to `.autoresearch/traces/round-{N}/`. The full debate history is preserved for post-mortem analysis. Read traces via `cat`, never summarize them.
