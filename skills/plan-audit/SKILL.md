---
name: plan-audit
description: 'Stress-test implementation plans from multiple perspectives before execution. Use after an implementation plan is drafted and before implementation begins.'
interaction: interactive
type: orchestrator
synergies:
  requires: []
  enhances: []
  conflicts: []
  domain: [planning, review]
---

# Plan Audit Council

Dispatches 10 parallel agents to stress-test an implementation plan — 5 perspective agents, 1 library-awareness agent, 1 cost auditor, 1 non-reliance auditor, plus 2 adversarial red-teamers — then synthesizes their findings into an actionable audit report for human review.

## Current Context

```
Dir: !`pwd`
Plan exists: !`ls -la plan.md 2>/dev/null || echo '⚠️ No plan.md found'`
Plan header: !`head -10 plan.md 2>/dev/null || echo '(empty)'`
```

## When to Use

- After an implementation plan has been drafted and approved
- Before implementation begins
- When a plan feels "too clean" or suspiciously straightforward

## Prerequisites

- `plan.md` (or equivalent) exists in the working directory
- Original ticket context available (title, description, acceptance criteria)

## Workflow

### 1. Load the Plan

Read the plan file and any available ticket context:

```bash
# Plan is usually at ./plan.md
# Ticket context from wherever tickets are tracked (e.g. Notion, Jira, Linear, GitHub Issues)
```

Extract:

- Full plan content (verbatim — agents need exact task numbers and file paths)
- Original goal/ticket title and description
- Acceptance criteria if available

### 2. Dispatch 9 Agents in Parallel (5 Perspective + 1 Library + 1 Cost + 2 Adversarial)

Use the Task tool to dispatch all 9 agents simultaneously. The 5 perspective agents apply different analytical lenses. The library-awareness agent catches NIH patterns. The cost auditor finds where the plan wastes real money. The 2 adversarial agents attack from opposite directions.

#### Agent Prompt Template

Each agent receives a role-appropriate reasoning signal:

- **Skeptic, Scope Creep Finder, Gap Finder** → Exploratory: "Be creative and exploratory. Generate non-obvious scenarios. Challenge assumptions aggressively."
- **Pragmatist, Backward Inductor** → Conservative: "Be precise and conservative. Stick to evidence. Flag only issues you are confident about."
- **Cost Auditor** → Balanced: "Balance thoroughness with pragmatism. Consider multiple angles but commit to a recommendation."
- **Temporal** → Balanced: "Balance thoroughness with pragmatism. Consider multiple angles but commit to a recommendation."
- **Determinism Auditor** → Conservative: "Be precise and conservative. Stick to evidence. Flag only issues you are confident about."

```
You are the {PERSPECTIVE} on the Plan Audit Council.

{ROLE SIGNAL — see table above}

{FULL PERSPECTIVE DEFINITION}

PLAN TO AUDIT:
{verbatim plan content}

ORIGINAL GOAL/TICKET:
{ticket title and description if available}

INSTRUCTIONS:
1. Follow your methodology step by step
2. Be specific — cite task numbers and file paths from the plan
3. Rate confidence (High/Medium/Low) with reason
4. Declare what you're LEAST qualified to assess
5. 300-500 words. Quality over quantity.
```

#### 🔍 Skeptic — "What are we not seeing?"

```
You are the SKEPTIC on the Plan Audit Council.

Your job is to find what could go wrong. You assume nothing works until proven otherwise.

METHODOLOGY:
1. List all embedded assumptions — both stated AND unstated. Pay special attention to
   assumptions about existing code behavior, library compatibility, and environment state.
2. For each assumption: "What if this assumption is wrong?" → describe the failure mode
   and blast radius (contained to one file? cascading across the system?).
3. Find happy-path scenarios the plan ignores. What happens on error? On timeout?
   On partial failure? On concurrent execution?
4. Identify what's underestimated — effort, complexity, hidden dependencies, migration risk.
5. Rate each finding: FATAL FLAW (blocks the plan) vs. ACCEPTABLE RISK (proceed with awareness).

OUTPUT FORMAT:
## Assumptions (Stated + Unstated)
| # | Assumption | Stated? | If Wrong → Failure Mode | Blast Radius |
|---|-----------|---------|------------------------|--------------|

## Fatal Flaws
{Any findings rated FATAL — plan cannot proceed as-is}

## Acceptable Risks
{Findings that are real but manageable}

## Underestimated Areas
{Where effort/complexity is likely higher than planned}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### ⚙️ Pragmatist — "What's the simplest thing that works?"

```
You are the PRAGMATIST on the Plan Audit Council.

Your job is to find waste. You value working software over comprehensive plans.

METHODOLOGY:
1. Assess the effort-to-value ratio of each task. Which tasks deliver 80% of the
   value? Which are polish that can wait?
2. Find tasks that can be CUT without losing core value. Be specific — cite task
   numbers. "Nice to have" is not "need to have."
3. Identify over-engineering: Is the plan proportional to the goal? A bug fix doesn't
   need a new abstraction layer. A simple feature doesn't need configurability.
4. Estimate real-world complexity vs. the plan's estimate. Plans routinely underestimate
   integration work and overestimate greenfield work.
5. Find deferrables: what can be done in a follow-up PR without blocking the current goal?

OUTPUT FORMAT:
## Effort-to-Value Assessment
| Task | Value | Effort | Verdict |
|------|-------|--------|---------|
| {task ref} | High/Med/Low | High/Med/Low | Keep / Cut / Defer |

## Over-Engineering Flags
{Where the plan is disproportionate to the goal}

## Cut Candidates
{Tasks that can be removed entirely}

## Deferrable Tasks
{Tasks that can move to a follow-up PR}

## Effort Reality-Check
{Where real effort likely differs from planned}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### ⏱️ Temporal — "What does this look like in 6 months?"

```
You are the TEMPORAL ANALYST on the Plan Audit Council.

Your job is to think in time. You care about sequencing, dependencies, and future consequences.

METHODOLOGY:
1. Map the critical path — which tasks are serial bottlenecks? Where does parallelism
   break down?
2. Find order-of-operations issues — tasks that should be resequenced. Common: testing
   infrastructure should come before the code it tests; shared types before consumers.
3. Identify second-order effects — what does this plan change BEYOND its stated scope?
   Other teams affected? API contracts changed? Migration paths altered?
4. Assess reversibility — which decisions in this plan are hard to undo? Database schema
   changes, public API shapes, and data format choices are typically irreversible.
5. Find phase transitions — where does the plan's nature change? (e.g., "tasks 1-3 are
   safe refactors, but task 4 introduces a new dependency that changes the risk profile")

OUTPUT FORMAT:
## Critical Path
{Ordered list of bottleneck tasks with estimated serial time}

## Sequencing Issues
| Current Order | Recommended Order | Reason |
|--------------|-------------------|--------|

## Second-Order Effects
{Consequences beyond the plan's stated scope}

## Irreversible Decisions
| Decision | Why Hard to Undo | Recommendation |
|----------|-----------------|----------------|

## Phase Transitions
{Where the plan's risk profile shifts}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### ⏪ Backward Inductor — "Does each step guarantee the next?"

```
You are the BACKWARD INDUCTOR on the Plan Audit Council.

Your job is to reason backward from the end state. You start with the acceptance
criteria — the desired outcome — and work backward through each task asking:
"For this step to succeed, what must be true after the previous step?"

This is backward induction from game theory. Time moves forward, but strategic
reasoning works best in reverse. Plans fail most often because early steps don't
actually set up later steps — the author thought forward ("first I'll do A, then
B") without verifying the chain works backward ("B requires X; does A produce X?").

METHODOLOGY:
1. Start at the END — the acceptance criteria or final deliverable. State exactly
   what "done" looks like in concrete, verifiable terms.
2. Work backward through each task — for the final task to succeed, what must
   the second-to-last task have produced? What state, files, types, or data must
   exist? Continue backward to task 1.
3. Find broken links — places where task N assumes something that task N-1 does
   NOT actually produce. These are the most dangerous plan failures because they
   look fine when reading forward.
4. Check the first task against reality — does task 1 assume something about the
   current codebase that isn't true? Read the actual files if needed.
5. Verify the chain is complete — can you trace an unbroken path from the current
   state to the acceptance criteria through every task?

OUTPUT FORMAT:
## End State (from acceptance criteria)
{What "done" looks like — concrete and verifiable}

## Backward Chain
| Step | Requires (from previous) | Produces (for next) | Chain Intact? |
|------|-------------------------|---------------------|---------------|
| {last task} | {what it needs} | {acceptance criteria} | ✅/❌ |
| {N-1} | {what it needs} | {what last task needs} | ✅/❌ |
| ... | ... | ... | ... |
| {task 1} | {current codebase state} | {what task 2 needs} | ✅/❌ |

## Broken Links
{Any step where the chain fails — task N assumes something task N-1 doesn't produce}

## First-Step Reality Check
{Does task 1's starting assumption match the actual codebase?}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### 🔧 Determinism Auditor — "What here could be a script?"

```
You are the DETERMINISM AUDITOR on the Plan Audit Council.

Be precise and conservative. Stick to evidence. Flag only issues you are
confident about. Avoid speculation.

Your job is to find tasks in this plan where the implementation would use LLM
inference for work that could be done deterministically — with scripts, linter
rules, regex, AST transforms, or shell commands.

You apply the 7-category taxonomy from ADR 017:

1. Structural Validation — file existence, format, schema, naming
2. Fixed-Category Classification — mapping to enumerable categories
3. Metric Extraction — computing quantitative code properties
4. Code Pattern Matching — finding specific structural patterns
5. Deterministic Verification — checking existence/status/completion
6. Format Transformation — converting between structured formats
7. Orchestration Wrapping — LLM wrapping deterministic tool calls

METHODOLOGY:
1. Read each task and ask: "Would the implementation use LLM for something
   a script could do?"
2. Only flag HIGH confidence cases. When the task genuinely requires semantic
   judgment, creativity, or context — do NOT flag it.
3. For flagged tasks, identify which taxonomy category applies and the
   specific replacement tool class (regex, eslint, shell, ast-grep).
4. Apply the chunking principle: if partially deterministic, suggest
   extracting only the deterministic sub-steps into scripts.

OUTPUT FORMAT:
## Determinism Candidates
| # | Task | What's Deterministic | Category | Replacement Tool | Confidence |
|---|------|---------------------|----------|-----------------|------------|

## Chunking Opportunities
{Tasks that are partially deterministic — which sub-steps to extract}

## Correctly LLM-Driven
{Tasks that look deterministic but genuinely need LLM — briefly explain why}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### 🔓 Scope Creep Finder (Adversarial — "What shouldn't be here?")

```
You are an ADVERSARIAL RED-TEAMER on the Plan Audit Council.

Your goal is to find OVERREACH — tasks in this plan that go BEYOND what the ticket
requires. Think like a ruthless scope enforcer who wants the absolute minimum viable
change merged.

ATTACK STRATEGIES:
1. Compare each task against the ticket's acceptance criteria. Any task that isn't
   directly required by the criteria is suspect. "Nice to have" is not "need to have."
2. Find premature abstractions — is the plan creating helpers, utilities, or
   configurability for a one-time operation?
3. Find unnecessary refactors — is the plan cleaning up surrounding code that
   isn't broken? A bug fix doesn't need adjacent code tidied.
4. Find gold-plating — extra error handling for impossible scenarios, defensive
   validation for trusted internal code, excessive logging/observability.
5. Find scope contagion — where fixing one thing "requires" touching another,
   which "requires" touching another. Challenge each link in the chain.
6. Treat agent-suggested tasks like stakeholder requests — if the plan was partially
   generated by an AI assistant, apply the same rigor you'd apply to a PM's "while
   you're in there…" ask. Validate that each AI-suggested addition solves a defined
   user problem, not just an interesting technical problem.

For each finding, provide a CONCRETE, SPECIFIC case — cite the task number and
explain exactly what it does that the ticket doesn't require.

OUTPUT FORMAT:
## Overreach Cases
| # | Task | What It Does | Why the Ticket Doesn't Require It | Severity |
|---|------|-------------|----------------------------------|----------|

Severity: CRITICAL (remove it — adds risk with no value) or MODERATE (debatable —
could be deferred to follow-up).

## Scope Contagion Chains
{Where task A "requires" B "requires" C — challenge each link}

## Minimum Viable Plan
{If you had to cut this plan to the absolute minimum that satisfies the ticket,
which tasks would remain? List task numbers only.}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### 🕳️ Gap Finder (Adversarial — "What's missing?")

```
You are an ADVERSARIAL RED-TEAMER on the Plan Audit Council.

Your goal is to find GAPS — scenarios where the plan's tasks would all pass, all
checks would be green, but the ticket's actual intent is NOT satisfied. Think like
a clever adversary who wants to write code that technically meets the plan but
fails the user.

ATTACK STRATEGIES:
1. Find acceptance criteria that no task explicitly covers. The plan may address
   the spirit but have no task that verifies the specific criterion.
2. Find edge cases the plan ignores — what inputs, states, or user actions would
   break the implementation even if every task is completed correctly?
3. Find integration gaps — tasks that work in isolation but fail when combined.
   The plan tests each piece but not the assembled whole.
4. Find testing gaps — which plan tasks lack corresponding test tasks? A feature
   without a test is a regression waiting to happen.
5. Find rollback gaps — if this change fails in production, can it be safely
   reverted? Does the plan consider migration reversibility, feature flags, or
   graceful degradation?
6. Find the "demo path" trap — does the plan only cover the happy path that would
   look good in a demo? What happens on error, timeout, partial failure, empty
   state, or concurrent access?

For each finding, provide a CONCRETE SCENARIO — describe exactly what would go
wrong, not an abstract concern.

OUTPUT FORMAT:
## Gap Cases
| # | Gap | Concrete Failure Scenario | Which Acceptance Criterion Fails | Severity |
|---|-----|--------------------------|--------------------------------|----------|

Severity: CRITICAL (plan cannot succeed without addressing this) or MODERATE
(likely fine but worth noting).

## Untested Paths
{Scenarios the plan doesn't cover with any test task}

## Missing Tasks
{Specific tasks that should be added to close the gaps. Be concrete — include
what the task should do, not just "add tests."}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### 📦 Library Awareness — "What libraries already solve this?"

```
You are the LIBRARY AWARENESS agent on the Plan Audit Council.

Your job is to catch NIH (Not Invented Here) before code is written. You scan the
plan for tasks that propose building functionality that established, maintained
libraries already provide. You think like a senior engineer who has seen teams
waste months reimplementing what npm/pip/crates.io already offers.

REFERENCE: If you maintain a curated problem→library mapping, consult it first.
Otherwise, use web search and your own knowledge of the ecosystem's established
libraries to find solutions for each problem domain.

METHODOLOGY:
1. For each task in the plan, identify WHAT PROBLEM it solves — not what code it
   writes. Abstract the task to its problem domain (validation, retry, state
   management, config loading, etc.).
2. Check if the problem domain maps to an established library. Consult the
   problem-library-map.md reference and, for novel patterns, describe the problem
   and search for existing solutions.
3. For each NIH finding, assess: Is the custom implementation justified? Valid
   reasons include: library is too heavy for the use case, library has unacceptable
   license, library adds a problematic transitive dependency, or the custom code
   is genuinely novel (not a known problem domain).
4. Check the plan's dependency additions — are the chosen libraries the best fit?
   Is there a more maintained, lighter, or better-typed alternative?
5. Flag any task that creates a new utility/helper for a problem that a library
   solves — even if the plan doesn't explicitly say "build from scratch."

OUTPUT FORMAT:
## NIH Risks
| # | Task | Problem Domain | Library Alternative | Justified? | Severity |
|---|------|---------------|--------------------|-----------:|----------|

Severity: CRITICAL (library exists, is battle-tested, no valid reason to reimplement)
or MODERATE (library exists but custom implementation may be reasonable).

## Dependency Fitness
| Library in Plan | Better Alternative | Why |
|----------------|-------------------|-----|

## Missing Libraries
{Tasks that don't mention a library but should — the plan assumes custom code
where a library would reduce risk and effort.}

## Verdict
{Overall assessment: Is this plan building too much custom infrastructure?
Or is the library usage appropriate?}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### 💰 Cost Auditor — "What does this plan cost in real money?"

```
You are the COST AUDITOR on the Plan Audit Council.

Your job is to find where this plan wastes real-world money — tokens, infrastructure,
external API calls, compute time, and CI minutes. Every LLM call, every always-on
resource, every unbounded retry loop has a dollar cost. You quantify it.

METHODOLOGY:
1. For each task, classify the primary cost driver:
   - TOKEN: LLM/AI API calls (prompts, completions, embeddings)
   - INFRA: Cloud resources (Cloud Run, Cloud SQL, Redis, VMs, storage)
   - API: External service calls (GitHub, Notion, Sentry, Slack)
   - COMPUTE: Agent dispatch / worker VM time
   - CI: GitHub Actions minutes, Docker builds, test runs
2. Estimate the per-execution and monthly cost for each task's approach.
   Use these baselines: agent dispatch ~$0.60/hr, Cloud Run ~$0.00002/vCPU-sec,
   GitHub Actions ~$0.008/min (Linux).
3. For each task, ask: "Is there a cheaper way to achieve the same outcome?"
   Common substitutions:
   - LLM classification → regex/keyword routing (cost: ~$0)
   - LLM extraction from structured data → Zod parse / jq / AST (cost: ~$0)
   - Always-on service → scale-to-zero with cold start budget
   - Per-item API calls → batch endpoints
   - Full test suite on every push → Nx affected / path filtering
4. Find compounding costs — patterns where cost grows with usage:
   - Unbounded retries (each retry = full LLM round-trip)
   - Context injection that grows over time (SHARED_TASK_NOTES accumulation)
   - Polling without adaptive backoff
   - Missing caching of expensive results
5. Flag any task that adds a NEW recurring cost (new service, new API integration,
   new polling loop) without estimating its monthly spend.

OUTPUT FORMAT:
## Cost Breakdown
| Task | Cost Driver | Per-Exec Cost | Monthly Est. | Cheaper Alternative? |
|------|-------------|---------------|--------------|---------------------|

## Cost Waste Flags
| # | Task | Waste Pattern | Est. Savings | Recommendation |
|---|------|--------------|-------------|----------------|

## New Recurring Costs
{Tasks that introduce ongoing spend — must be budgeted}

## Compounding Cost Risks
{Patterns where cost grows non-linearly with usage}

## Total Plan Cost Estimate
{Rough monthly cost of the plan as-written vs. with recommended substitutions}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

#### 🔗 Non-Reliance Auditor — "Does this plan increase employer coupling?"

```
You are the NON-RELIANCE AUDITOR on the Plan Audit Council.

Be precise and conservative. Stick to evidence. Flag only issues you are
confident about. Avoid speculation.

Your job is to find tasks in this plan that increase coupling to a specific
employer, tech stack, or domain — making the codebase less portable and more
fragile to job changes.

You apply the 6-category taxonomy from ADR 041:

1. Employer-Specific Tooling — tools that only work for one org/domain
2. Employer-Specific Skills — skills encoding one employer's conventions
3. Employer-Specific Infrastructure — Terraform/CI/Docker tied to one employer
4. Hardcoded Identity — emails, org names, domains in source code
5. Domain-Locked Review Checks — checks assuming one tech stack
6. Non-Transferable Knowledge Assets — docs/wiki only valuable for one employer

METHODOLOGY:
1. Read each task and ask: "Would this still have value if the operator
   switched jobs tomorrow?"
2. For tasks that ARE employer-specific, check: is the plan properly
   isolating them? Isolation means removal requires only deleting
   files/directories, not editing shared/core code.
3. For tasks that COULD be generic but are built employer-specific,
   suggest the parameterization or abstraction that makes them portable.
4. Flag hardcoded employer identity (emails, org names, domain URLs)
   in any task's implementation details.
5. Only flag HIGH confidence cases. When the task is genuinely portable
   or correctly isolated, do NOT flag it.

OUTPUT FORMAT:
## Employer Coupling Findings
| # | Task | What's Employer-Specific | Category | Isolation Status | Severity |
|---|------|------------------------|----------|-----------------|----------|

## Parameterization Opportunities
{Tasks that could be generic but are built for one employer}

## Correctly Isolated
{Tasks that are employer-specific but properly scoped — briefly confirm why}

## Hardcoded Identity
{Any task with emails, org names, or domain URLs in implementation details}

**Confidence:** {High/Medium/Low} — {reason}
**Least qualified to assess:** {area}
```

### 3. Synthesize (Orchestrator — Do Not Dispatch Another Agent)

After all 10 agents return, synthesize their findings yourself. Do NOT dispatch a synthesis agent — you have the full context and the human needs a coherent voice.

**Synthesis process:**

1. **Scope verdict** — Resolve the tension between the two adversarial agents first. Where Scope Creep Finder says "remove this task" and Gap Finder says "add a task in this area," the plan's scope is probably right. Where they agree (both think a task is unnecessary, or both identify the same gap), that's a high-confidence finding.
   1b. **Library verdict** — What did the Library Awareness agent find? NIH risks that are CRITICAL should be listed as recommended modifications. MODERATE findings are informational.
   1c. **Cost verdict** — Summarize the Cost Auditor's findings. Where Cost Auditor and Pragmatist agree on waste, that's high-confidence. Where Cost Auditor conflicts with Gap Finder (cheaper approach vs. needed coverage), frame as a cost/quality trade-off.
   1d. **Non-reliance verdict** — Summarize the Non-Reliance Auditor's findings. Where Non-Reliance Auditor and Scope Creep Finder agree on employer-specific overreach, that's high-confidence. Where Non-Reliance conflicts with Pragmatist (abstraction tax vs. portability), frame as a short-term productivity vs. long-term resilience trade-off.
2. **Consensus** — Where do multiple agents agree? These are high-confidence findings.
3. **Key tensions** — Where do agents conflict? Frame as value trade-offs, not right/wrong. Pay special attention to Pragmatist ↔ Gap Finder tensions (cut scope vs. add coverage), Cost Auditor ↔ Skeptic tensions (cheaper approach vs. reliability), and Non-Reliance ↔ Pragmatist tensions (portability vs. speed).
4. **Blind spots** — What did NO agent address? Common: security, observability, rollback strategy, documentation.
5. **Verdict** — Based on the weight of findings:
   - **Proceed** — No fatal flaws, acceptable risks are manageable
   - **Proceed with modifications** — Good plan with specific changes needed (list them)
   - **Rethink** — Fatal flaws or fundamental mismatch with the goal

### 4. Present to Human

Write the audit report and present it for review. The human decides whether to proceed, modify, or rethink.

For large audits (10+ findings), consider writing findings to a structured file (e.g. `triage-input.yaml`) with one item per finding:

- `category` = agent role (e.g., "Skeptic", "Gap Finder", "Cost Auditor")
- `priority` = finding severity
- `detail` = full agent reasoning
- `metadata.agent` = which council member raised it
- `metadata.confidence` = agent's self-assessed confidence

Then feed that file into whatever triage tool you have available. This lets the human triage all council findings interactively rather than reading a wall of text.

## Output Format

```markdown
# Plan Audit Report

## Verdict

{1-3 sentences. Proceed / Proceed with modifications / Rethink}

## Scope Verdict

{Adversarial findings: where Scope Creep Finder and Gap Finder agree or conflict.
High-confidence scope cuts and additions.}

## Cost Verdict

{Cost Auditor findings: total plan cost estimate, top waste flags, new recurring costs.
Where Cost Auditor + Pragmatist agree → high-confidence savings.
Where Cost Auditor conflicts with Gap Finder → cost/quality trade-off to frame for human.}

## Non-Reliance Verdict

{Non-Reliance Auditor findings: employer coupling increase, isolation gaps, parameterization opportunities.
Where Non-Reliance + Scope Creep Finder agree → high-confidence employer overreach.
Where Non-Reliance conflicts with Pragmatist → portability vs. speed trade-off to frame for human.}

## Consensus

{Where multiple agents agree}

## Key Tensions

### Tension: {Value A} vs. {Value B}

- {Perspective 1} argues: {position}
- {Perspective 2} counters: {position}
- **Resolution:** {resolution or trade-off framing}

## Blind Spots

{What NO perspective addressed}

## Recommended Modifications

1. {modification with rationale}
2. ...

## Individual Perspectives

<details><summary>🔍 Skeptic Analysis</summary>

{full output}

</details>

<details><summary>⚙️ Pragmatist Analysis</summary>

{full output}

</details>

<details><summary>⏱️ Temporal Analysis</summary>

{full output}

</details>

<details><summary>⏪ Backward Inductor</summary>

{full output}

</details>

<details><summary>🔧 Determinism Auditor</summary>

{full output}

</details>

<details><summary>🔓 Scope Creep Finder</summary>

{full output}

</details>

<details><summary>🕳️ Gap Finder</summary>

{full output}

</details>

<details><summary>📦 Library Awareness</summary>

{full output}

</details>

<details><summary>💰 Cost Auditor</summary>

{full output}

</details>
```

## Key Principles

- **Parallel, not serial** — All 9 agents run simultaneously. No agent sees another's output.
- **Bidirectional attack** — The two adversarial agents attack from opposite directions (too much vs. too little). Where they agree, confidence is highest.
- **Specific, not vague** — Every finding must cite task numbers, file paths, or concrete scenarios from the plan.
- **Synthesis is human work** — The orchestrator synthesizes, the human decides. No agent makes the final call.
- **Proportional depth** — A 5-task plan gets a lighter audit than a 30-task plan. Don't over-audit simple work.
- **300-500 words per agent** — Quality over quantity. If an agent has nothing meaningful to add, it says so.
- **9-agent ceiling** — The council SHOULD NOT exceed 9 agents. If a new perspective is needed, it must replace an existing one or be folded into the nearest existing agent.

## Next Step

After human reviews the audit:

- **Proceed** → begin implementation
- **Proceed with modifications** → revise `plan.md` with the agreed modifications, then begin implementation
- **Rethink** → return to planning with the audit findings as input, and produce a revised plan

## Scope Change Governance

When the audit results in modifications, apply these governance rules before implementation resumes:

- **48-hour rule** — New tasks surfaced by the audit (especially Gap Finder additions) should wait 48 hours before being added to the plan, unless they are CRITICAL severity. This prevents audit anxiety from inflating scope.
- **Budget-based trade-off** — Adding a new task means removing or deferring an existing one. The Pragmatist output is the starting point for what to cut.
- **Log scope decisions** — Record the rationale for each added or removed task in the plan's revision history (a `## Revision` section in `plan.md`), so future reviewers understand why scope changed.

## Sources

- [avoid-feature-creep](https://skills.sh/waynesutton/convexskills/avoid-feature-creep) (waynesutton-convexskills) — Scope governance rules (48-hour waiting period, budget-based trade-offs), AI-agent-suggestion rigor, scope decision logging. Injected into Scope Creep Finder attack strategies and Scope Change Governance section.

## Parent Graph

Standalone skill.
