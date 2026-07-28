---
name: post-meeting-analysis
description: "Processes a single meeting from Fireflies into structured action items, reports, fact-check prompts, and dispatch tasks. Tracks parsed vs unparsed meetings. Use when asked to 'analyze a meeting', 'process meeting notes', 'extract action items from meeting', 'post-meeting analysis', 'run meeting analysis', or 'what happened in my meetings'."
interaction: interactive
type: leaf
synergies:
  enhances: [gws]
  domain: [meetings, fireflies, action-items, fact-check]
---

# Post-Meeting Analysis

Pull a single meeting from Fireflies, extract structured intelligence, generate actionable outputs, and optionally hand off agent-executable tasks to your own agent-dispatch workflow.

## Requirements

- A Fireflies account and API key (see Prerequisites below).
- Optional: a CRM/people-tracking tool of your own for attendee enrichment (Phase 4) — the skill degrades gracefully without one.
- Optional: an agent-dispatch workflow of your own (parallel worktrees/agents) if you want to hand off `dispatch-tasks.md` items automatically — otherwise treat that output as a plain checklist.
- Optional: a SessionEnd hook of your own if you want Phase 8 telemetry persisted automatically — otherwise the summary JSON is just written to disk for you to consume manually.

## When to Use

- "Analyze a meeting" / "Process meeting notes"
- "Extract action items from meeting"
- "Post-meeting analysis" / "Run meeting analysis"
- "What happened in my meetings"
- "How do I communicate in meetings?" / "Analyze my speaking patterns"
- "Am I avoiding conflict in meetings?" / "Track my filler words"
- After any meeting you want structured outputs from

## Prerequisites

- Fireflies API key set as `FIREFLIES_API_KEY` env var (get from Fireflies → Settings → Developer Settings)
- Fireflies MCP server (bundled via `mcp.json` in this skill directory)
- `comms` CLI available on PATH (for person enrichment — optional, has fallback)

Verify:

```bash
echo $FIREFLIES_API_KEY | head -c 8   # Should show first 8 chars
which comms                             # Optional — enrichment degrades gracefully
```

### Fireflies API Access

The skill bundles a Fireflies MCP server via `mcp.json`. If the MCP tools are not available (connection failure, server not started), fall back to direct GraphQL:

```bash
curl -s -X POST https://api.fireflies.ai/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $FIREFLIES_API_KEY" \
  -d '{"query": "{ transcripts(limit: 50) { id title date duration organizer_email participants speakers { name email } } }"}'
```

**API limits:** Never request `limit` > 50 — the Fireflies API returns null/errors for higher values. Use `skip` for pagination if needed.

## Workflow

```
Phase 0:   SELECT    → List meetings, user picks one
Phase 0.5: ROLE      → Detect user's role (organizer vs attendee)
Phase 1:   INGEST    → Pull transcript + summary from Fireflies
Phase 2:   CLASSIFY  → Auto-detect meeting type
Phase 3:   EXTRACT   → Structured action items, decisions, topics, claims, parking lot
Phase 3.5: PATTERNS  → Optional: communication pattern analysis (speaking ratios, conflict, filler words)
Phase 4:   ENRICH    → Cross-reference attendees with comms CRM
Phase 5:   DIFF      → For recurring meetings, compare with prior session
Phase 6:   OUTPUT    → Write prompt files, report, dashboard
Phase 7:   HANDOFF   → Optional: agent dispatch, Slack, GWS (role-scoped)
Phase 8:   TELEMETRY → Write run summary for SessionEnd hook
```

## Phase 0: Select Meeting

### Load registry

Read `skills/post-meeting-analysis/meeting-state.yaml`. If it doesn't exist or is empty, initialize with `meetings: []`.

### List meetings from Fireflies

```
# Meetings you attended (15 most recent, unprocessed first)
Use fireflies_get_transcripts with: mine=true, limit=50

# Meetings you didn't attend (10 most recent)
Use fireflies_get_transcripts with: mine=false, limit=10
```

**If the user asks for a specific meeting by name/person** and it doesn't appear in the list, search broadly:

```
Use fireflies_search with: keyword:"{person_name}" limit:20
```

Try multiple name variations (first name, last name, nickname). If still not found, try `fireflies_get_transcripts` with `participants` filter using the person's email if known (check `comms ls {name}` for email).

### Present selection UI

Cross-reference the Fireflies results against the registry to separate processed vs unprocessed:

```
📋 Unprocessed meetings (15 most recent you attended):
 #  | Date       | Title                           | Duration | Attendees
 1  | 2026-04-22 | Bert & Baira Weekly              | 32m      | You, Bert, Baira
 2  | 2026-04-21 | Frontend Sync                    | 45m      | You, Jin, Alex
 ...

📋 Meetings you didn't attend (10 most recent):
 16 | 2026-04-22 | Design Review                    | 28m      | Bert, Jin
 ...

✅ Already processed: {N} meetings (pick a number + --rerun to re-process)
```

Ask: **"Which meeting to process? (number, or N --rerun to re-process)"**

If rerunning, ask for a note explaining why (stored in `rerun_notes`).

## Phase 0.5: Detect User Role

Determine the user's role in this meeting by comparing the user's email against the `organizer_email` field from Fireflies:

- **Organizer**: User's email matches `organizer_email` → full handoff options (Slack posting, email drafts, dispatch of any task)
- **Attendee**: User's email does NOT match → scoped handoffs only:
  - Dispatch: Only tasks assigned to the user or unassigned
  - Slack: Skip suggestion (organizer's responsibility)
  - Email: Skip follow-up email suggestion
  - GWS: Only calendar reminders for user's own action items

Store role as `user_role: organizer | attendee` in the registry entry and telemetry.

**Important:** Action items owned by others should still be extracted and reported, but dispatch suggestions should only include items the user owns or can act on. Never suggest dispatching someone else's work without their knowledge.

## Phase 1: Ingest

For the selected meeting:

1. **Summary first** (lightweight): `fireflies_get_summary` with the meeting ID → action items, keywords, topics, overview
2. **Full transcript**: `fireflies_fetch` with the meeting ID → complete data with speaker attribution
3. **Action items**: `fireflies_get_action_items` if available → pre-extracted action items

Store the raw data in memory (not written to disk). The structured extraction in Phase 3 is what gets persisted.

## Phase 2: Classify Meeting Type

Auto-classify using signals from the meeting data. See `reference/meeting-types.md` for the full taxonomy and extraction template per type.

| Type                | Signals                                | Focus                               |
| ------------------- | -------------------------------------- | ----------------------------------- |
| `recurring-1on1`    | 2 attendees, recurring title pattern   | Relationship, carried-forward items |
| `recurring-team`    | 3+ attendees, recurring title          | Commitments, blockers, updates      |
| `planning`          | Keywords: sprint, roadmap, planning    | Estimates, scope, assignments       |
| `customer-external` | External domain emails                 | Promises, follow-ups, fact-checks   |
| `standup`           | Short duration, standup/daily keywords | Blockers only, light extraction     |
| `review`            | Keywords: review, retro, postmortem    | Decisions, lessons, improvements    |
| `ad-hoc`            | No recurring pattern, misc             | General extraction                  |

Present the classification: **"Classified as: {type}. Correct? (yes / change to X)"**

## Phase 3: Extract Structured Data

Apply the extraction template for the classified meeting type. For all types, extract:

### Action Items

```yaml
action_items:
  - description: 'Finalize API schema for v2 endpoint'
    owner: 'Bert'
    due_date: '2026-04-25' # null if not mentioned
    priority: 'high' # high/medium/low, inferred from urgency language
    source_quote: "Bert said he'd have the schema done by Friday"
    dispatchable: true # Can an agent help with this?
    dispatch_skill: 'ticket-intake' # Suggested skill if dispatchable
```

### Decisions

```yaml
decisions:
  - decision: 'Use GraphQL instead of REST for the new API'
    context: 'Team discussed trade-offs, decided GraphQL better for frontend flexibility'
    participants: ['Bert', 'Baira']
    reversible: true
```

### Key Topics

```yaml
topics:
  - name: 'API Migration'
    time_spent_estimate: '15m'
    summary: 'Discussed timeline and schema changes'
  - name: 'Q3 Planning'
    time_spent_estimate: '10m'
    summary: 'Reviewed priorities, agreed on 3 key deliverables'
```

### Fact-Check Claims

Extract any quantitative claims, metrics, or assertions made during the meeting:

```yaml
fact_check_claims:
  - claim: 'API latency is averaging 230ms on the /users endpoint'
    speaker: 'Bert'
    category: 'internal' # internal = needs product/usage data, external = publicly verifiable
    verification_prompt: 'Check the average p50 and p99 latency for the /users endpoint over the last 7 days'
  - claim: 'React 19 has built-in server components support'
    speaker: 'Baira'
    category: 'external'
    verification_prompt: 'Does React 19 include built-in server components? Check the React 19 release notes and changelog'
```

### Open Questions

```yaml
open_questions:
  - question: 'Should we support backward compatibility for v1 clients?'
    raised_by: 'Baira'
    needs_answer_from: 'Bert'
```

### Parking Lot

Items explicitly tabled for a future meeting or that surfaced and couldn't be addressed:

```yaml
parking_lot:
  - item: 'Revisit the caching strategy for the new API'
    raised_by: 'Bert'
    suggested_timeline: 'next sprint planning'
```

## Phase 3.5: Communication Pattern Analysis (Optional)

Run this phase when the user explicitly asks for communication feedback, speaking pattern analysis, or is processing multiple meetings in a series. Skip for standup meetings.

Analyze the transcript for behavioral patterns across these dimensions:

### Conflict Avoidance

- Hedging language: "maybe", "kind of", "I think", "sort of"
- Indirect phrasing instead of direct requests
- Changing subject when tension arises
- Agreeing without commitment ("yeah, but...")
- Not addressing obvious problems raised by others

### Speaking Ratios

- Approximate percentage of meeting each participant spent speaking
- Interruptions (by and of each speaker)
- Question vs. statement ratio per speaker
- Longest speaking turns

### Filler Words

Track frequency of "um", "uh", "like", "you know", "actually" per speaker. Note if frequency spikes in specific contexts (presenting, being questioned, uncertain).

### Active Listening Signals

- Questions that reference others' previous points
- Paraphrasing or summarizing others' ideas
- Building on others' contributions
- Clarifying questions

### Leadership & Facilitation

- Decision-making approach (directive vs. collaborative)
- How disagreements were handled
- Inclusion of quieter participants
- Time management and agenda adherence

### Output Format

For each pattern found, report:

```markdown
### [Pattern Name]

**Finding**: [One-sentence summary]
**Frequency**: [X times across this meeting]

**Examples**:

1. **[Timestamp or context]**
   **What Happened**: > [Quote from transcript]
   **Why It Matters**: [Impact or missed opportunity]
   **Better Approach**: [Specific alternative phrasing or behavior]
```

End with a synthesis:

```markdown
## Communication Summary

**Strengths**: [2-3 concrete observations with examples]
**Growth Opportunities**: [2-3 specific, actionable recommendations]
**Speaking Statistics**: approximate % speaking time per attendee, filler word density, interruption count
```

## Phase 4: Enrich with Comms CRM

**Graceful degradation:** If `comms` CLI is not available or fails (build errors in worktree, missing dependencies), skip this phase with a warning and continue to Phase 5. Record `comms_available: false` in telemetry. The remaining phases work without enrichment.

For each attendee extracted from the meeting:

1. **Match profile**: `comms ls {attendee_name}` — try multiple name variations (first name, full name, email prefix). Names may differ across systems — check your own CRM/people-lookup tool's docs for matching guidance.
2. **If profile exists**: Pull relationship context, communication style, prior interactions
3. **If no profile**: Ask user "Create a comms profile for {name}? (yes/skip)"
4. **Log interaction**: Append the interaction to whatever interaction log your CRM tool uses (date, person, meeting title, note).

**Fallback if `comms` CLI fails:** If your comms tool stores profiles as flat files, try reading the profile directly (path depends on your setup).

Store enrichment data in the registry entry (see `reference/registry-schema.md`).

## Phase 5: Recurring Meeting Diff

**Only runs if the meeting is part of a recurring series** (detected by title similarity with prior processed meetings).

1. Find the most recent prior meeting in the same series from the registry
2. Load the prior meeting's action items from its output file
3. Diff:
   - **Completed**: Items from last time that weren't mentioned or were confirmed done
   - **Carried forward**: Items still discussed, still open
   - **New**: Items that appeared for the first time
   - **Dropped**: Items from last time that weren't mentioned at all (potential concern)

```yaml
recurring_diff:
  series: 'bert-baira-weekly'
  prior_meeting_id: 'fireflies-xyz789'
  prior_meeting_date: '2026-04-15'
  completed: ['Set up staging environment']
  carried_forward:
    - item: 'Finalize API schema'
      sessions_open: 3
      originally_assigned: '2026-04-01'
      stale: true # open > 2 sessions
  new: ['Review Q3 roadmap draft']
  dropped: ['Update documentation'] # was mentioned last time, not this time
```

## Phase 6: Generate Outputs

Create output directory: `skills/post-meeting-analysis/outputs/{date}-{title-slug}/`

### 6a. Report (`report.md`)

Full meeting report with all extracted data, formatted for reading. See `reference/output-templates.md` for the template.

### 6b. Action Items (`action-items.md`)

Standalone action item list with owner, due date, priority. Formatted as a checklist.

### 6c. Fact-Check Prompts

**`fact-check-internal.md`** — Prompt ready to send to your internal Slack AI bot:

```markdown
# Fact-Check: Internal Data Queries

Meeting: {title} ({date})

Please verify the following claims using product data, usage metrics, error logs, and internal systems:

1. **Claim:** "API latency is averaging 230ms on /users endpoint"
   **Speaker:** Bert
   **What to check:** Average p50 and p99 latency for /users over last 7 days

2. ...
```

**`fact-check-external.md`** — Prompt for any LLM with public/repo knowledge:

```markdown
# Fact-Check: External/Public Information

Meeting: {title} ({date})

Please verify the following claims using publicly available information, documentation, and canonical sources:

1. **Claim:** "React 19 has built-in server components support"
   **Speaker:** Baira
   **What to check:** React 19 release notes, official documentation

2. ...
```

### 6d. Dispatch Tasks (`dispatch-tasks.md`)

Action items where `dispatchable: true`, formatted for handoff to your own agent-dispatch workflow (if you have one) or as a plain checklist otherwise:

```markdown
# Agent-Executable Tasks from {title} ({date})

Items:

1. Finalize API schema for v2 endpoint → {suggested skill/owner}
2. Update CI config for new test suite → {suggested skill/owner}
3. Draft migration guide for v1→v2 → {suggested skill/owner}
```

### 6e. Dashboard (`dashboard.html`)

**Always regenerate the dashboard on every run.** Read `reference/dashboard-template.html` as the base template. Replace the HTML comment placeholders (`<!-- TOTAL_PROCESSED -->`, `<!-- MEETING_ROWS -->`, etc.) with actual data from the full registry + current run stats. Write the result to `skills/post-meeting-analysis/dashboard.html`.

To populate the dashboard:

1. Read all entries from `meeting-state.yaml`
2. Count totals (processed, unprocessed, action items, stale items, fact-checks, dispatch tasks)
3. Build the meeting rows table, person heatmap, series table, stale items table, and timeline
4. Replace each `<!-- PLACEHOLDER -->` comment with the generated HTML

After writing, tell the user how to view it:

```
📊 Dashboard updated: skills/post-meeting-analysis/dashboard.html
   View: python3 -m http.server 8090   →   http://localhost:8090/skills/post-meeting-analysis/dashboard.html
```

## Phase 7: Act on Outputs

**Present a concrete action menu. The user picks which to execute. Scope by role (Phase 0.5).**

After generating all output files, present this menu:

```
📋 Outputs ready for: {title} ({date})

What to do next? (pick numbers, or "all", or "done" to finish)

  1. 🔍 Fact-check INTERNAL — Hand off to a new thread that sends the {N} internal claims
     to your internal Slack AI bot for verification against product data
     → reads: fact-check-internal.md

  2. 🔍 Fact-check EXTERNAL — Hand off to a new thread that verifies the {N} external claims
     using web search and public documentation
     → reads: fact-check-external.md

  3. 🚀 Dispatch agent tasks — Hand off {N} of your action items to your own agent-dispatch
     workflow (worktrees + parallel agents), if you have one
     → reads: dispatch-tasks.md

  4. 📊 View dashboard — Open the HTML dashboard
     → python3 -m http.server 8090

  5. 💬 Post summary to Slack (organizer only) — channel name?
  6. 📅 Calendar reminders for your {N} due-dated items
  7. 📧 Draft follow-up email (organizer only)
```

**For items 5-7**: Skip from the menu if `user_role == attendee` and item is organizer-only.

### Executing handoffs

**For fact-check internal (option 1):** Use `handoff` to create a new thread with goal:

```
Read the file skills/post-meeting-analysis/outputs/{date-slug}/fact-check-internal.md.
For each claim, use the Slack MCP to post it as a question to the appropriate Slack channel
(or if no Slack MCP, just verify each claim using available tools and write results back
to a new file: fact-check-internal-results.md in the same directory).
```

**For fact-check external (option 2):** Use `handoff` to create a new thread with goal:

```
Read the file skills/post-meeting-analysis/outputs/{date-slug}/fact-check-external.md.
Verify each claim using web search and public documentation.
Write results to fact-check-external-results.md in the same directory.
```

**For dispatch (option 3):** Use `handoff` to create a new thread with goal:

```
Read the file skills/post-meeting-analysis/outputs/{date-slug}/dispatch-tasks.md
and dispatch the listed items using your own agent-dispatch workflow
(parallel worktrees/agents), if available. Otherwise, treat it as a checklist.
```

**For Slack/GWS (options 5-7):** Execute inline using the Slack MCP or `gws` skill. Always confirm before sending.

## Phase 8: Telemetry

Write `.post-meeting-run-summary.json` to the repo root. If you have a SessionEnd hook of your own, wire it to process this file into `run-log.yaml` (and wherever else you track skill runs) — this is optional and the rest of the skill works without it.

See `reference/telemetry.md` for the schema and an example hook design.

### Update Registry

Append or update the meeting entry in `meeting-state.yaml` with:

- Status → `processed`
- Timestamp
- Thread ID
- Output paths
- Enrichment data
- Recurring diff data (if applicable)

## Anti-Patterns

- ❌ **Processing multiple meetings at once** — One meeting per invocation. Use the registry to track progress across sessions.
- ❌ **Reading raw transcript directly** — Always use the pre-processed summary + structured extraction. Full transcript is only for targeted quote lookup.
- ❌ **Auto-posting to Slack or sending emails** — Phase 7 handoffs are ALWAYS opt-in. Ask first.
- ❌ **Ignoring user role** — Check organizer vs attendee in Phase 0.5. Never suggest dispatching someone else's tasks or posting summaries when user is just an attendee.
- ❌ **Skipping the comms CRM sync** — Every meeting is an interaction. At minimum, log it. (But degrade gracefully if comms CLI is unavailable.)
- ❌ **Hardcoding attendee names** — Always resolve via Fireflies attendee data + comms profile matching. Try multiple name variations.
- ❌ **Overwriting rerun data** — When rerunning, preserve the original processing and add rerun metadata alongside it.
- ❌ **Requesting limit > 50 from Fireflies API** — The API returns null for high limits. Use pagination with `skip` instead.
- ❌ **Skipping dashboard generation** — Always regenerate `dashboard.html` even if only one meeting is processed.
- ❌ **Running Phase 3.5 on standups** — Communication pattern analysis is only useful for substantive meetings with discussion. Skip for standups and short syncs.
- ❌ **Judging communication patterns from a single data point** — Pattern analysis is most valuable across multiple meetings. Flag low confidence when analyzing only one meeting.

## Related Skills

- `gws` — Google Workspace for calendar/email follow-ups
- `project-status-generator` — Multi-format status artifacts (dashboard patterns)
