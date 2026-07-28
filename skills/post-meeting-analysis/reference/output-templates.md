# Output Templates

## Report Template (`report.md`)

```markdown
# Meeting Report: {title}

**Date:** {date}
**Duration:** {duration}
**Type:** {meeting_type}
**Attendees:** {attendee_list}

---

## Summary

{2-3 sentence overview from Fireflies summary + agent synthesis}

## Decisions Made

1. **{decision}** — {context}
   - Participants: {who was involved}
   - Reversible: {yes/no}

## Action Items

| #   | Task          | Owner   | Due    | Priority       | Dispatchable |
| --- | ------------- | ------- | ------ | -------------- | ------------ |
| 1   | {description} | {owner} | {date} | {high/med/low} | {yes/no}     |

## Key Discussion Topics

### {topic_name} (~{time_estimate})

{summary}

## Open Questions

- **{question}** — Raised by {person}, needs answer from {person}

## Fact-Check Claims

### Internal (needs product/usage data)

| Claim   | Speaker   | Verification Needed |
| ------- | --------- | ------------------- |
| {claim} | {speaker} | {what_to_check}     |

### External (publicly verifiable)

| Claim   | Speaker   | Verification Needed |
| ------- | --------- | ------------------- |
| {claim} | {speaker} | {what_to_check}     |

## Recurring Meeting Diff

> Only included for recurring meetings with prior data

**Series:** {series_name}
**Compared with:** {prior_date}

✅ **Completed since last meeting:**

- {item}

🔄 **Carried forward ({N} sessions):**

- {item} — originally assigned {date} {⚠️ STALE if >2 sessions}

🆕 **New this session:**

- {item}

⚠️ **Dropped (mentioned last time, not this time):**

- {item}

## Attendee Context (from Comms CRM)

### {attendee_name}

- **Relationship:** {brief context from profile}
- **Communication style:** {preferences}
- **Recent interactions:** {last 2-3 from comms}

---

_Processed by post-meeting-analysis on {processing_date}_
_Thread: {thread_id}_
```

## Action Items Template (`action-items.md`)

```markdown
# Action Items: {title} ({date})

## By Owner

### {owner_name}

- [ ] {description} — Due: {date} | Priority: {priority}
  > "{source_quote}"

### {owner_name_2}

- [ ] {description} — Due: {date} | Priority: {priority}

## By Priority

### 🔴 High

- [ ] {description} — @{owner} — Due: {date}

### 🟡 Medium

- [ ] {description} — @{owner} — Due: {date}

### 🟢 Low

- [ ] {description} — @{owner} — Due: {date}

## Carried Forward (from prior sessions)

- [ ] ⚠️ {description} — @{owner} — Open for {N} sessions since {date}

---

Total: {N} items | {N} high | {N} medium | {N} low | {N} carried forward
```

## Dispatch Tasks Template (`dispatch-tasks.md`)

```markdown
# Agent-Executable Tasks: {title} ({date})

Source: post-meeting-analysis output
Meeting: {title} ({date})

## Items

1. **{description}**
   - Suggested skill: {skill_name}
   - Owner: {owner}
   - Due: {date}
   - Context: {1-2 sentences of relevant context from the meeting}

2. **{description}**
   - Suggested skill: {skill_name}
   - Owner: {owner}
   - Due: {date}
   - Context: {context}
```

## Fact-Check Internal Template (`fact-check-internal.md`)

```markdown
# Fact-Check: Internal Data Queries

Meeting: {title} ({date})

Please verify the following claims using product data, usage metrics, error logs, and internal systems:

1. **Claim:** "{claim_text}"
   **Speaker:** {speaker}
   **What to check:** {verification_prompt}

2. **Claim:** "{claim_text}"
   **Speaker:** {speaker}
   **What to check:** {verification_prompt}

---

Source: post-meeting-analysis | {date} | {meeting_id}
```

## Fact-Check External Template (`fact-check-external.md`)

```markdown
# Fact-Check: External/Public Information

Meeting: {title} ({date})

Please verify the following claims using publicly available information, official documentation, and canonical sources:

1. **Claim:** "{claim_text}"
   **Speaker:** {speaker}
   **What to check:** {verification_prompt}

2. **Claim:** "{claim_text}"
   **Speaker:** {speaker}
   **What to check:** {verification_prompt}

---

Source: post-meeting-analysis | {date} | {meeting_id}
```
