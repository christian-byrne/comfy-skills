---
name: postmortem-writing
description: 'Write blameless postmortems for incidents. Use when an SEV1/SEV2 occurred, a customer-facing outage lasted >15 min, data was lost, or a novel failure mode was encountered. Generates timeline, 5-whys analysis, and action items.'
interaction: autonomous
type: leaf
synergies:
  requires: []
  enhances: [systematic-debugging]
  conflicts: []
  domain: [incidents, reliability, documentation]
---

# Postmortem Writing

Blameless postmortems shift the question from "Who caused this?" to "What conditions allowed this?" Focus on systemic failure, not individual blame.

## When to Use

- SEV1/SEV2 incidents
- Customer-facing outage > 15 minutes
- Data loss or security incident
- Near-miss with severe potential impact
- Novel failure mode not seen before

## Structure

### 1. Incident Summary (2–3 sentences)

What happened, when, user impact, and resolution time.

### 2. Timeline

| Time (UTC) | Event                       |
| ---------- | --------------------------- |
| HH:MM      | Incident began              |
| HH:MM      | Alert fired / team notified |
| HH:MM      | Root cause identified       |
| HH:MM      | Mitigation applied          |
| HH:MM      | Full resolution             |

### 3. Root Cause Analysis (5 Whys)

Start with the symptom, ask "why?" until reaching a systemic cause (usually 4–6 levels deep).

```
Why did users see errors?        → Service returned 500s
Why did service return 500s?     → DB connection pool exhausted
Why was pool exhausted?          → Slow query held connections
Why was query slow?              → Missing index after schema migration
Why was index missing?           → Migration not reviewed for perf impact
Root cause: No perf review gate in migration workflow
```

### 4. Impact Assessment

- Affected users / % of traffic
- Revenue impact (if quantifiable)
- Duration of degradation

### 5. What Went Well

At least 2 items — detection speed, communication, rollback time.

### 6. What Could Have Gone Better

Concrete observations, no blame. "The alert threshold was too high" not "Bob set it wrong."

### 7. Action Items

| Action                                  | Owner | Due     | Priority |
| --------------------------------------- | ----- | ------- | -------- |
| Add index to migration review checklist | @eng  | +1 week | P1       |
| Lower alert threshold for 500 rate      | @sre  | +3 days | P1       |

Every item needs: named owner, due date, priority. Unowned items don't get done.

## Facilitation (60 min)

1. **Opening (5 min)** — Blameless culture reminder
2. **Timeline review (20 min)** — Chronological walkthrough
3. **Analysis (20 min)** — 5 Whys, systemic factors
4. **Action items (10 min)** — Assign owners and due dates
5. **Close (5 min)** — Schedule 30-day follow-up

## Anti-Patterns

| Anti-pattern                       | Fix                                     |
| ---------------------------------- | --------------------------------------- |
| "X made a mistake"                 | "What systemic gap allowed X?"          |
| Shallow root cause ("human error") | Drill 2 more levels                     |
| Unassigned action items            | Every item needs a named owner          |
| No follow-up                       | Schedule 30-day check-in during meeting |
