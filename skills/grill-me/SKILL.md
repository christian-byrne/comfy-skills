---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
interaction: interactive
type: leaf
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Session Structure

Move through these phases in order:

1. **Orientation (2–3 questions)** — Establish the shape of the plan: What problem does it solve? Who does it affect? Is this greenfield or a change to something existing?
2. **Deep Dive** — Walk each branch of the decision tree, category by category. Minimum 10 questions across all relevant areas before wrapping up.
3. **Conflict Resolution** — Surface any tensions between resolved decisions (see Precedent Binding below).
4. **Completeness Check** — Before producing the Decision Record, verify all key areas are covered.

## Precedent Binding

Every answered question becomes a **binding constraint** on all future questions. Maintain a running `## Resolved Decisions` list throughout the session. After each answer:

1. **Record the decision** — add a one-line summary to the resolved list (e.g., "Auth: JWT over session cookies, because stateless scales better")
2. **Never re-litigate** — do not ask questions whose answer is already determined by a prior decision. If a new question would contradict a resolved decision, say so explicitly: "This conflicts with decision #N — do you want to revise that, or should I find a compatible approach?"
3. **Tighten the constraint space** — each resolved decision should make subsequent questions more specific and edge-case-focused, not broader. Early questions resolve high-level architecture; later questions should probe the boundaries of those choices.
4. **Surface tensions** — if a new question reveals that two prior decisions are in genuine tension, escalate: "Decisions #X and #Y conflict in this scenario: {concrete example}. Which takes priority?"

## Knowledge Gap Detection

Watch for these signals during the interview. When detected, probe deeper or offer to research before continuing:

| Signal                                                   | Response                                                                                                   |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| "I think..." or "Maybe..."                               | Probe deeper — what's the uncertainty?                                                                     |
| "That sounds good" (agreeing to your suggestion)         | Verify they understand the implications, not just accepting it                                             |
| "Just simple/basic X"                                    | Challenge — define what simple means in this context                                                       |
| Technology buzzwords without substance                   | Ask what they think it does, what tradeoffs they've considered                                             |
| Conflicting requirements ("fast AND cheap AND reliable") | Surface the conflict explicitly with a concrete tradeoff                                                   |
| Short or vague answers                                   | They may be overwhelmed — simplify or break the question down                                              |
| "That's just how it's done" / "everyone does X this way" | Probe whether this is a physical constraint or inherited convention — ask "what breaks if we don't do X?"  |
| Optimizing before questioning existence                  | Apply the existence-first reframe (see below) — optimization is premature if the need itself is unexamined |

## Research Triggers

When uncertainty is high and the decision is consequential, pause grilling and offer to research:

> "You mentioned X but seem unsure about the tradeoffs. Want me to research this before we continue? I can compare approaches and come back with informed follow-up questions."

If exploring the codebase can resolve the uncertainty, do that instead.

## Reframing Stuck Questions

If a question is generating circular debate or the user keeps reversing decisions, reframe it upward:

- **Stuck in local optima?** Ask: "What would have to be true for this decision to be obvious?" or "What are we actually optimizing for here?"
- **Can't define the answer?** Apply the one-sentence test: "If you can't explain this decision in one sentence, the design may not be clear enough yet."
- **Two valid answers?** Escalate to the constraint that resolves them: "Both work — which matters more: X or Y? That determines the answer here."

### Existence-First Reframe

Before optimizing anything, challenge whether it should exist at all. Apply this sequence:

1. **Question existence** — "Why does this requirement/feature/step exist? Who owns it? Would removing it break a physical constraint or just a convention?"
2. **Delete before optimizing** — Only after confirming it must exist: "What's the minimum version? What can be removed without losing core value?"
3. **Simplify before accelerating** — "What's the simplest implementation that satisfies the constraint? Is there a path with 10x less complexity?"

If the user is optimizing something that shouldn't exist, surface that conflict explicitly: "We've been discussing _how_ to build X — I haven't heard a compelling reason _why_ X needs to exist. What's the physical constraint that requires it?"

### Idiot Index Signal

When a proposed design or cost structure seems disproportionate, probe the gap between theoretical minimum and current reality:

- "What's the absolute minimum this requires if you strip away all legacy/convention/process? What's actually mandatory versus inherited from how it's always been done?"
- "If you built this from scratch with no prior assumptions, what would it look like?"

Use this as a signal: the larger the gap between "theoretical minimum" and "what you're proposing," the more unexamined assumptions are embedded in the design.

## Completeness Check

Before producing the Decision Record, verify coverage:

- Problem statement is clear and concrete
- Core user/system journey is mapped
- Data model or key state is understood
- Integration points and dependencies are identified
- Failure modes and edge cases have been surfaced
- No "TBD" items blocking the main decisions

If anything is missing, continue the interview rather than producing an incomplete record.

## Output

When the session ends (user says "done", "enough", or all branches are resolved), produce a **Decision Record**:

```markdown
# Decision Record — {plan/design name}

## Resolved Decisions

1. {decision} — {rationale}
2. {decision} — {rationale}
   ...

## Tensions Resolved

- {decision X} vs {decision Y} → {resolution}

## Open Branches

- {any unresolved questions remaining}
```
