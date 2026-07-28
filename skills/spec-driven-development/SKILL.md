---
name: spec-driven-development
description: 'Write specs before code. Use for new projects, ambiguous requirements, multi-file changes, architectural decisions, or any task >30 min. Generates structured spec docs that serve as shared truth between human and AI.'
interaction: hybrid
type: leaf
synergies:
  requires: []
  enhances: [plan-audit]
  conflicts: []
  domain: [planning, architecture, process]
---

# Spec-Driven Development

> Code without a spec is guessing.

Specs are the shared source of truth between AI agents and human engineers. Write the spec first, gate implementation on human approval, then execute.

## When to Use

**Use spec-driven approach for:**

- New projects or modules
- Ambiguous or vague requirements
- Multi-file changes (>3 files)
- Architectural decisions
- Work expected to take >30 minutes

**Skip for:**

- Typo fixes
- Single-line unambiguous changes
- Hotfixes with clear scope

## Four-Stage Workflow

```
SPECIFY → PLAN → TASKS → IMPLEMENT
   ↑         ↑       ↑        ↑
 human     human  human    autonomous
approval  review  review   (gated)
```

Each stage completes before the next begins. Do not implement until spec is approved.

## Spec Document Structure

Create `spec.md` in the project root or relevant directory:

### 1. Objective

```markdown
## Objective

**What:** One sentence — what are we building?
**Why:** The problem it solves, the metric it improves
**Success criteria:** Measurable ("LCP < 2.5s", "test suite passes", "zero 500s")
```

### 2. Commands

```markdown
## Commands

- **Build:** `pnpm build`
- **Test:** `pnpm test`
- **Dev:** `pnpm dev`
- **Lint:** `pnpm lint`
```

### 3. Project Structure

```markdown
## Structure

src/
components/ # UI components
services/ # Business logic
types.ts # Shared types
```

### 4. Code Style (Examples > Rules)

```markdown
## Style

Use existing patterns: see `src/services/auth.ts` for error handling convention.
Prefer explicit over clever. No magic strings — use enums or constants.
```

### 5. Testing Strategy

```markdown
## Testing

Framework: vitest
Coverage target: 80% on new code
Test location: co-located `*.test.ts` files
Mocking: integration tests use real DB (testcontainers)
```

### 6. Boundaries

```markdown
## Boundaries

Always: TypeScript strict mode, existing error patterns
Ask First: new external dependencies, DB schema changes
Never: `any` type, skipping tests, modifying unrelated files
```

## Surface Assumptions First

Before writing the spec, explicitly list assumptions:

```
Assumptions:
- Auth is handled upstream (not in scope)
- Postgres is the DB (SQLite not needed)
- Mobile support is not required
```

Wrong assumptions invalidate the spec. Better to surface them early.

## Reframe Vague Requirements

| Vague                   | Measurable                                  |
| ----------------------- | ------------------------------------------- |
| "Make it faster"        | "LCP < 2.5s on 4G connection"               |
| "Improve UX"            | "Form submission rate increases 10%"        |
| "Better error handling" | "Zero unhandled promise rejections in prod" |

## Living Document

- Commit `spec.md` alongside the PR
- Update spec when decisions shift during implementation
- Reference spec in PR description
- Never write spec post-implementation
