---
name: improve-codebase-architecture
description: Explore a codebase to find architectural improvement opportunities, focusing on deepening shallow modules and improving testability. Use when user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more AI-navigable.
interaction: hybrid
type: leaf
synergies:
  requires: []
  enhances: []
  conflicts: []
  domain: [architecture, refactoring]
---

# Improve Codebase Architecture

Explore a codebase like an AI would, surface architectural friction, and propose module-deepening refactors as GitHub issue RFCs.

A **deep module** (John Ousterhout, "A Philosophy of Software Design") has a small interface hiding a large implementation. Shallow modules — where the interface is nearly as complex as the implementation — are the enemy.

## Workflow

### 1. Explore the Codebase

Use finder and Read to navigate. Note friction as you go — the friction you encounter IS the signal:

- Where does understanding one concept require bouncing between many small files?
- Where are modules so shallow that the interface is nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called?
- Where do tightly-coupled modules create integration risk?
- Which parts are untested, or hard to test?

### 2. Present Candidates

Present a numbered list of deepening opportunities. For each:

- **Cluster**: which modules/concepts are involved
- **Why they're coupled**: shared types, call patterns, co-ownership of a concept
- **Dependency type**: shared data, shared control flow, or shared abstraction
- **Test impact**: what existing tests would be replaced by boundary tests

Do NOT propose interfaces yet. Ask: "Which of these would you like to explore?"

### 3. Frame the Problem Space

For the selected candidate, write:

- The constraints any new interface would need to satisfy
- The dependencies it would need to rely on
- A rough illustrative code sketch

Then immediately proceed to step 4.

### 4. Design Multiple Interfaces

Spawn 3+ sub-agents in parallel via Task tool. Each gets a different constraint:

- Agent 1: "Minimize the interface — aim for 1-3 entry points max"
- Agent 2: "Maximize flexibility — support many use cases and extension"
- Agent 3: "Optimize for the most common caller — make the default case trivial"
- Agent 4: "Design around the ports & adapters pattern"

Each outputs: interface signature, usage example, what complexity it hides, dependency strategy, trade-offs.

After comparing, give your own recommendation. Be opinionated.

### 5. Create GitHub Issue

Create a refactor RFC as a GitHub issue using `gh issue create`. Do NOT ask the user to review before creating — just create it and share the URL.

Issue template:

```markdown
## Problem

{What's wrong with the current structure — in terms of friction, not opinion}

## Proposed Deepening

{Which modules merge, what the new boundary looks like}

## Interface Design

{Chosen interface from step 4}

## Migration Plan

{Incremental steps, each leaving codebase working}

## Testing Strategy

{What boundary tests replace, what new tests are needed}
```

## When to Run

- After a surge of development (weekly cadence)
- When agent output quality degrades in a module
- When test boundaries become unclear
- When onboarding friction is high in a part of the codebase

## Exemplar: Pi's Minimal Architecture

When evaluating architectural improvement opportunities, Pi (the coding agent) demonstrates what extreme module deepening looks like in practice:

- **3 packages with clear boundaries:** `pi-ai` (LLM API) → `pi-agent-core` (runtime) → `pi-coding-agent` (CLI/TUI). Each is independently usable.
- **4 tools as the entire interface:** `read`, `write`, `edit`, `bash` — everything else is an extension. The interface is tiny; the implementation is deep.
- **Session storage as a single concept:** append-only JSONL with `id`/`parentId` tree. One data structure handles branching, compaction, state persistence, and history replay.
- **Extension system as the escape hatch:** instead of adding tools to the core, the agent extends itself at runtime.

Use this as a reference when evaluating whether a module is "deep enough." If the interface is nearly as complex as the implementation, the module is too shallow.
