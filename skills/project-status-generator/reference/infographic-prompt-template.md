# Infographic Prompt Template

Use this template when calling the `painter` tool to generate a status infographic. Replace all `{placeholders}` with latest reconciled data.

**Design system:** Swiss Pulse — the token reference below defines the full palette and typography rules.

## Template

```
Create a clean project status dashboard infographic.
Swiss Pulse aesthetic: white background (#ffffff), single accent #0066FF.
System sans-serif (Helvetica/-apple-system). Weights 400 and 600 only.
No gradients, no shadows, no decorative elements.

Vertical layout ~1200x1800px. Max-width 720px content area.

Hero metric at top (42-48px, weight 600):
"{done_count}/{total_count} tasks complete"

Title: "{project_name} — Status Update {date}"

Section 1 - Milestone cards in a row:
{for each milestone}
- {name} — {percent}% — accent-colored progress bar — "{task_count} tasks, {done_count} done" — deadline "{deadline} {deadline_icon}"
{end for}
Each card: 0.5px border rgba(0,0,0,0.1), border-radius 8px, #f5f5f0 background.

Section 2 - "{current_milestone} Progress ({remaining} tasks remaining{scope_note})" header (14px uppercase, weight 600).
{for each task in current milestone, sorted by status}
{status_icon} {task_name} — {description} ({owner})
{end for}

Status colors (exception to single-accent rule for semantic encoding):
✅ #4ade80 = done/merged
🔧 #0066FF = in progress / in review
⚠️ #fbbf24 = needs discussion / blocked
🔴 #f87171 = punted / not started
❓ #6b7280 = waiting on external

Section 3 - "Path to Production" header with numbered steps:
{numbered list of steps to ship}

Section 4 - "Blockers" header:
{list of blockers with status icons}

Footer: "{upcoming_data_or_actions}"

Professional dashboard aesthetic. Clean lines, generous whitespace, readable at Slack image sizes.
```

## Rules

1. **Always regenerate from latest data** — never reuse text from a previous draft
2. **Include every task** — don't summarize, list them all with owners
3. **Show scope changes** — if tasks were punted, show them with 🔴 and note "punted to M3"
4. **Full GitHub URLs in the Slack text version** — the infographic can use short names since URLs aren't clickable in images
5. **Save with date suffix** — `status-update-{date}.png`, iterate with `-v2`, `-v3` if needed
6. **Swiss Pulse compliance** — no weight 700+, no decorative illustrations, hero metric leads
