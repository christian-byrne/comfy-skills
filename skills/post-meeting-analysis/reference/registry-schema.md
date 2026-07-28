# Meeting State Registry Schema

The registry at `skills/post-meeting-analysis/meeting-state.yaml` tracks all meetings processed by this skill.

## Schema

```yaml
meetings:
  - id: 'fireflies-abc123' # Fireflies transcript ID
    title: 'Bert & Baira Weekly' # Meeting title from Fireflies
    date: '2026-04-22' # Meeting date (ISO)
    duration_minutes: 32 # Meeting duration
    attended: true # Whether user attended
    status: processed # pending | processing | processed | rerun
    processed_at: '2026-04-22T15:30:00Z' # When processing completed
    thread_id: 'T-...' # Amp thread that processed this meeting
    meeting_type: 'recurring-1on1' # Classified type (see meeting-types.md)

    # Output file paths (relative to skills/post-meeting-analysis/)
    outputs:
      report: 'outputs/2026-04-22-bert-baira-weekly/report.md'
      action_items: 'outputs/2026-04-22-bert-baira-weekly/action-items.md'
      fact_check_internal: 'outputs/2026-04-22-bert-baira-weekly/fact-check-internal.md'
      fact_check_external: 'outputs/2026-04-22-bert-baira-weekly/fact-check-external.md'
      dispatch_tasks: 'outputs/2026-04-22-bert-baira-weekly/dispatch-tasks.md'

    # Attendee enrichment
    enrichment:
      attendees:
        - name: 'Bert Smith'
          email: 'bert@company.com'
          comms_profile: 'people/BertSmith.md' # null if no profile
          profile_updated: true # Whether profile was updated this run
        - name: 'Baira Lee'
          email: 'baira@company.com'
          comms_profile: 'people/BairaLee.md'
          profile_updated: false

    # Recurring meeting tracking
    recurring:
      series: 'bert-baira-weekly' # null if not recurring
      prior_meeting_id: 'fireflies-xyz789' # null if first in series
      prior_meeting_date: '2026-04-15'
      completed_items: 2
      carried_forward_items: 1
      stale_items: 1 # carried forward > 2 sessions
      new_items: 3
      dropped_items: 0

    # Extraction stats
    stats:
      action_items: 7
      decisions: 3
      topics: 4
      open_questions: 2
      fact_check_claims: 4
      dispatch_tasks: 3
      parking_lot_items: 1

    # Communication pattern analysis (Phase 3.5 — only if run)
    communication_patterns:
      analyzed: true
      speaking_ratios: { 'Bert': 0.45, 'Baira': 0.35, 'You': 0.20 }
      top_patterns: ['conflict_avoidance', 'active_listening']
      filler_word_density: 2.3 # per minute, for primary speaker

    # Rerun tracking
    rerun_notes:
      - date: '2026-04-23'
        reason: 'Re-extracting after Bert clarified the API deadline in Slack'
```

## Registry Operations

### Adding a new meeting

Append to the `meetings` list. Never overwrite existing entries.

### Rerunning a meeting

1. Update `status` to `rerun`
2. Append to `rerun_notes` with date and reason
3. Overwrite the output files (they represent the latest extraction)
4. Keep the original `processed_at` timestamp
5. Add a `rerun_at` field with the new timestamp

### Detecting recurring series

Match meetings by normalized title similarity:

1. Lowercase, strip dates and numbers
2. If >80% similar to a prior meeting title → same series
3. Series name = slugified common title prefix

### Querying the registry

```bash
# Count by status
grep -c "status: processed" skills/post-meeting-analysis/meeting-state.yaml

# Find stale carried-forward items
grep -A2 "stale_items:" skills/post-meeting-analysis/meeting-state.yaml | grep -v "0$"

# List all series
grep "series:" skills/post-meeting-analysis/meeting-state.yaml | sort -u
```
