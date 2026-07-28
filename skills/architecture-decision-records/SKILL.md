---
name: architecture-decision-records
description: Capture architectural decisions as structured ADRs during coding sessions. Use when a significant technical choice is made (framework selection, architectural pattern, API design, infrastructure decision).
interaction: hybrid
type: leaf
---

# Architecture Decision Records

Capture significant technical decisions during coding sessions. Prevents decisions from disappearing into Slack or PR comments.

## When to create an ADR

- Framework or library selection
- Architectural pattern adoption
- API design decisions
- Data modeling choices
- Infrastructure or security approaches
- Testing strategies that deviate from defaults
- Any decision future developers would ask "why did we do it this way?"

**Trigger:** User explicitly requests ADR documentation, or a significant technical choice emerges mid-implementation.

## Format (Michael Nygard lightweight)

```markdown
# ADR-NNNN: {Title}

**Status:** proposed | accepted | deprecated | superseded by ADR-XXXX

## Context

{The situation and forces at play. What problem triggered this decision?}

## Decision

{The choice made. One sentence, declarative.}

## Alternatives Considered

- **{Option A}** — {why rejected}
- **{Option B}** — {why rejected}

## Consequences

**Positive:** {What improves}
**Negative:** {What gets harder or breaks}
```

## Directory structure

```
docs/adr/
  README.md          ← index table (number, title, status, date)
  0001-{slug}.md
  0002-{slug}.md
```

**File only created after explicit approval.** Show the draft first.

## Index entry format

```markdown
| 0001 | {Title} | accepted | {YYYY-MM-DD} |
```

## Quality bar

- Specific over generic — name the actual technology chosen
- Rationale over facts — explain why, not just what
- Honest trade-offs — include the negatives

## Sources

- **ADR format & structure** — [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — Skill triage source for Michael Nygard lightweight ADR template and workflow guidance
