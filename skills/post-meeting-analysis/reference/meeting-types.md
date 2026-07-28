# Meeting Type Classification

## Taxonomy

| Type                | Detection Signals                                            | Extraction Focus                                                      |
| ------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------- |
| `recurring-1on1`    | Exactly 2 attendees, title matches prior meeting             | Relationship context, carried-forward items, personal action items    |
| `recurring-team`    | 3+ attendees, title matches prior meeting                    | Team commitments, blockers, status updates, ownership                 |
| `planning`          | Keywords: sprint, roadmap, planning, backlog, OKR, quarterly | Estimates, scope decisions, priority rankings, assignments            |
| `customer-external` | Attendee emails from external domains                        | Promises made, deliverable commitments, follow-up emails, fact-checks |
| `standup`           | Duration < 20min, keywords: standup, daily, sync             | Blockers only, minimal extraction                                     |
| `review`            | Keywords: review, retro, retrospective, postmortem, incident | Decisions, lessons learned, process improvements                      |
| `ad-hoc`            | No recurring pattern, no keyword match                       | General extraction (all categories)                                   |

## Classification Algorithm

1. Check attendee count: exactly 2 → candidate for `recurring-1on1`
2. Check title against prior meetings in registry → if match, prefix with `recurring-`
3. Check duration: < 20min + standup keywords → `standup`
4. Check keywords in title + topics for planning/review/customer signals
5. Check attendee email domains: any external → `customer-external`
6. Fallback: `ad-hoc`

## Per-Type Extraction Adjustments

### recurring-1on1

- **Extra emphasis on:** carried-forward diff, relationship dynamics, personal commitments
- **De-emphasize:** formal decisions (these are usually informal)
- **Comms enrichment:** Always update the person's profile with new context
- **Dashboard:** Track action item velocity between 1:1 partners

### recurring-team

- **Extra emphasis on:** who committed to what, blockers, dependencies between people
- **De-emphasize:** casual discussion topics
- **Comms enrichment:** Log interaction for all attendees
- **Dashboard:** Team-level action item distribution

### planning

- **Extra emphasis on:** scope decisions, priority rankings, timeline commitments
- **De-emphasize:** implementation details (those belong in tickets)
- **Dispatch:** High-value — planning outputs often map directly to tickets

### customer-external

- **Extra emphasis on:** exact promises made, deliverable timelines, competitor mentions
- **Fact-check:** Prioritize claims made to customers — verify before they become commitments
- **Comms enrichment:** Create/update customer profiles with relationship context
- **GWS follow-up:** Strongly suggest drafting a follow-up email (still opt-in)

### standup

- **Light extraction:** Blockers and brief status updates only
- **Skip:** Fact-check, detailed topics, comms enrichment
- **Skip:** Dashboard update (standups don't generate enough signal)

### review

- **Extra emphasis on:** decisions made, process changes agreed, lessons learned
- **Dispatch:** Action items from retros are often improvement tasks → good dispatch candidates
- **Comms enrichment:** Update team dynamics if conflict patterns discussed
