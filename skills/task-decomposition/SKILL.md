---
name: task-decomposition
description: REQUIRED before any non-trivial implementation. Break large/vague work into independently verifiable sub-tasks with explicit inputs, outputs, dependencies, and complexity tier. Use when creating an issue with effort medium+, when picking a large issue, when a request feels open-ended, or when an implementation will touch 3+ files. Triggers — phrases like "use skill task-decomposition", "decompose this", "break this down", "task breakdown", "sub-tasks", or any issue-creation or issue-pickup workflow flagged as effort:medium or effort:large.
---

# Task Decomposition

> Adapted from public decomposition-focused agent skills for general use in AI-agent development pipelines.

## Why this exists

Decomposition is the highest-leverage move you can make before writing code. A well-decomposed plan:

1. **Lets cheaper models handle trivial sub-tasks** — saves cost.
2. **Surfaces unknowns early** — avoids mid-task dead ends.
3. **Enables parallel dispatch** — independent sub-tasks fan out to subagents.
4. **Produces reviewable PRs** — each chunk maps to a commit/PR slice.
5. **Is a precondition for splitting work into PRs, dispatching sub-tasks in parallel, and writing an execution plan.**

ALWAYS announce: **"I am using skill: task-decomposition before implementing this."**

## When to use (mandatory triggers)

- Creating an issue with `effort:medium` or `effort:large`
- Picked up a large issue for implementation
- Request mentions 3+ files or 2+ packages
- Anything that would take >1 hour of focused work
- Any "design X then implement X" request

If none of the above apply, skip this skill — over-decomposing trivial work is its own anti-pattern.

## The 4-phase loop

```
UNDERSTAND ──→ DECOMPOSE ──→ CLASSIFY ──→ VALIDATE
     │             │            │            │
  Read inputs   Sub-tasks   Tier + model   Sanity-check
  Read repo     w/ deps     Risk + retry   against AC
  State goal    explicit    estimate       fail-fast
```

### Phase 1 — UNDERSTAND

Before decomposing, write 2-4 lines answering:

- **Goal (one sentence):** what is the verifiable end state?
- **Acceptance criteria (bullet list):** how will you know it's done?
- **Constraints:** what must NOT change? (public APIs, DB schema, perf budget)
- **Existing context:** which files/packages/skills are involved? Read them first.

If any of those are unclear → load the `brainstorming` skill, or otherwise pause to ask clarifying questions, and stop.

### Phase 2 — DECOMPOSE

Produce a **task graph**, not a linear list. Each sub-task uses this schema:

```yaml
- id: 1
  name: 'Short verb-first description'
  inputs: [files, types, prior-task-ids]
  output: 'What artifact/state this produces'
  depends_on: [ids of prerequisite tasks]
  est_minutes: 15 # 5/15/30/60 buckets
  acceptance: 'How to verify this single sub-task'
  fallback: 'What to do if this fails'
```

Rules:

- **Bite-sized** — each sub-task is 5-30 minutes of focused work. Larger → decompose further.
- **Independently verifiable** — each has an acceptance check that runs in isolation.
- **Explicit dependencies** — if A must come before B, say so. Otherwise mark them parallelizable.
- **No "do everything in one task"** — at least 3 sub-tasks for medium issues, 5+ for large.
- **Surface unknowns as research tasks** — "spike: confirm X library supports Y" is a valid sub-task.

### Phase 3 — CLASSIFY (complexity tier + suggested model)

For each sub-task, assign a tier. This unlocks per-task model routing if your dispatch tooling supports it.

| Tier         | Examples                                               | Suggested model class                                 |
| ------------ | ------------------------------------------------------ | ----------------------------------------------------- |
| `trivial`    | rename, add log line, doc typo, env var doc            | `claude-haiku` / `amp -m rush` / `gemini-flash`       |
| `routine`    | add a CRUD endpoint, add a test, refactor 1 fn         | `claude-sonnet` / `amp -m smart` / `gemini-2.5-flash` |
| `analytical` | new feature in 1 module, debug across 2-3 files        | `claude-sonnet` / `amp -m smart` / `gpt-5`            |
| `deep`       | new architecture, cross-package refactor, novel design | `claude-opus` / `amp -m deep` / `gpt-5-pro`           |

Per-task model selection can be wired into your own dispatch tooling if it routes different tiers to different models/CLIs.

### Phase 4 — VALIDATE

Before handing off to implementation, sanity-check:

- [ ] Sum of sub-task minutes ≈ original effort estimate (±50%)
- [ ] Every acceptance criterion in Phase 1 is covered by at least one sub-task acceptance
- [ ] No circular dependencies in the graph
- [ ] At least one sub-task is `trivial` or `routine` (otherwise: are you over-engineering?)
- [ ] Risk: any sub-task with `fallback: "abort, redesign"` belongs in a research spike first

## Output formats

### For a GitHub issue body

Append a `### Task Decomposition` section:

```markdown
### Task Decomposition

| ID  | Sub-task                    | Tier       | Est | Depends | Acceptance              |
| --- | --------------------------- | ---------- | --- | ------- | ----------------------- |
| 1   | Add Zod schema to contracts | routine    | 15m | —       | `pnpm typecheck` passes |
| 2   | Generate openapi types      | trivial    | 5m  | 1       | `pnpm codegen` clean    |
| 3   | Add API gateway route       | routine    | 30m | 1,2     | unit test green         |
| 4   | Add dashboard view          | analytical | 60m | 3       | screenshot in PR        |
```

### For a plan.md (effort:medium+)

Use the schema above as a YAML block, plus a Phase 1 narrative section, in a `plan.md` alongside the issue.

### For a quick chat reply

A bulleted list with `[trivial]` / `[routine]` / `[analytical]` / `[deep]` tags is fine. Always include dependencies and per-item acceptance.

## Anti-patterns

- **Linear lists with no tiers or deps** — you've made a TODO list, not decomposed.
- **One huge "implement the feature" task** — keep recursing until each piece is verifiable.
- **Skipping Phase 1** — if the goal isn't crisp, decomposition just makes confusion plural.
- **Decomposing trivial work** — a one-line fix doesn't need a task graph.
- **Treating decomposition as documentation** — it's a planning tool. If the plan is wrong, redo it; don't ship a wrong plan.

## Related practices (do these on demand)

- **Unclear goal** — load the `brainstorming` skill (if available) or otherwise clarify the goal before decomposing
- **Converting to a plan** — write this decomposition into a `plan.md` alongside the issue
- **Splitting into PRs** — map sub-tasks to reviewable PR slices
- **Parallel dispatch** — dispatch independent sub-tasks to separate subagents
- **Deciding on TDD** — judge which sub-tasks need a test-first approach based on risk and complexity
- **Stress-testing the plan** — load the `plan-audit` skill (if available) to audit the decomposition before executing
- **Greenfield/multi-phase work** — write a full requirements doc before decomposing

## Issue-driven development tips

- **No work without an issue.** Decomposition lives in the issue or its `plan.md`, not in chat.
- **Update the issue continuously** — when starting, on blockers, on significant decisions.
- **Each sub-task is a verifiable gate** — don't move on without its acceptance check passing.
- **Prefer cached project state** over labels for tracking sub-task status.

## Enforcing this skill

If your repo has hooks or automation available, wiring a reminder into issue-creation (e.g. a pre-`gh issue create` hook that nudges the agent to load this skill) helps compliance. This is optional tooling the skill itself does not ship.
