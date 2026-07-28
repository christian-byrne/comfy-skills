---
name: project-status-generator
description: Generates multi-format project status artifacts from Notion milestones, GitHub PRs, and Slack context. Produces AI-generated infographics, matplotlib charts, mermaid diagrams, and copy-paste Slack messages. Use when asked to create a status update, milestone report, project dashboard, or weekly update.
interaction: autonomous
type: leaf
---

# Project Status Generator

Ingests project data from Notion milestones, GitHub PRs, and Slack context, then generates a suite of status artifacts in multiple formats. The human picks what to post.

## When to Use

- "Create a status update"
- "Generate a milestone report"
- "Make a project dashboard"
- "Weekly update for Slack"
- "What's the current project status?"
- Any request for visual/shareable project state

## Quick Start

1. **Ingest** — Pull milestone tasks from Notion, PR statuses from GitHub
2. **Reconcile** — Cross-reference, correct stale data, identify gaps
3. **Generate** — Produce all output formats in a `visuals/` folder
4. **Present** — Show outputs, let human pick what to post

## Workflow

### Phase 1: Data Ingestion

For each milestone in the project:

1. **Notion**: Retrieve the milestone page → get `Comfy Tasks` relation → fetch each task's title, status, assignee
2. **GitHub**: For each PR referenced, run `gh pr view <number> --json url,state,title` to get current state
3. **Slack context**: Check any recent Slack exports or channel context for decisions/corrections

```
Data to extract per task:
- Task name
- Status (Done, In Progress, In Review, Not Started, Need Discussion, Paused, Duplicate)
- Assignee (person name)
- GitHub PR URL (if any)
- Blockers or notes
```

### Phase 2: Reconciliation

Cross-reference sources to catch:

- PRs marked merged on GitHub but still "In Progress" in Notion
- Tasks with no assignee that should have one
- Stale items (>2 weeks without progress)
- Scope decisions from Slack not reflected in Notion

Write corrections to a structured summary before generating visuals.

### Phase 3: Generate Artifacts

Create a `visuals/` directory in the project plans folder. Generate ALL of the following — the human picks what to use:

#### 1. AI-Generated Infographic (painter tool)

Use the painter tool with a detailed prompt following the **Swiss Pulse preset** (see `reference/infographic-prompt-template.md` in this skill):

```
Create a clean project status dashboard infographic.
Swiss Pulse aesthetic: white background (#ffffff), single accent #0066FF.
System sans-serif (Helvetica/-apple-system). Weights 400 and 600 only.
No gradients, no shadows, no decorative elements.

Status colors (the ONE exception to single-accent rule for status encoding):
green (#4ade80) done, blue (#0066FF) in-progress,
orange (#fbbf24) attention, red (#f87171) blockers.

Vertical layout ~1200x1800px. Max-width 720px content area.
Hero metric at top (42-48px): "{done_count}/{total_count} tasks complete"

[Include: milestone cards with %, progress bars, task lists
with status icons, path-to-prod steps, blocker summary, footer]
```

**Key rules for the infographic prompt:**

- Use LATEST reconciled data, never stale text
- Include milestone cards with % complete, task counts, deadline status
- List every task with owner and status icon (✅🔧⚠️🔴)
- Include "Path to Production" numbered steps if applicable
- Include blocker summary
- Footer with upcoming data/actions
- Follow Swiss Pulse typography: two weights only (400/600), no bold body text

Save as: `visuals/status-update-{date}.png`

#### 2. Matplotlib Charts (run scripts)

Run `scripts/generate-charts.py` with the task data to produce:

- **Pie chart**: Task status distribution per milestone
- **Bar chart**: Tasks by owner and status (horizontal bars, color-coded)
- **Progress bars**: All milestones side-by-side with % complete

Save as: `visuals/{milestone}-pie.png`, `visuals/{milestone}-gantt.png`, `visuals/milestones-overview.png`

#### 3. Mermaid Diagrams

Generate inline mermaid diagrams for:

- Gantt chart showing task timelines
- Pie chart showing status distribution

These render inline in the conversation.

#### 4. Copy-Paste Slack Message

Generate a plain-text (no markdown formatting, no `>` blockquotes) message inside a code fence that can be directly copied into Slack. Include:

- Milestone summary with emoji status indicators
- Task-level progress with full GitHub URLs (not hyperlinked)
- Path to production steps
- Blocker callouts
- Shout-outs to contributors

### Phase 4: Update Project Artifacts

After generating visuals, also update:

- `state.yaml` — phase, blocked_on, scope changes
- `todo.md` — add any Notion update tasks needed
- `decisions/` — document scope changes (punts, deadline moves)
- `knowledge/` — update milestone JSON-LD with latest counts
- `research/notion/` — save task tables with provenance metadata

## Output Folder Structure

<!-- docs-linter-disable-next-tree -->

```
plans/visuals/
├── status-update-{date}.png       # AI infographic (primary)
├── status-update-{date}-v{N}.png  # Iterations if needed
├── {milestone}-pie.png            # Matplotlib pie chart
├── {milestone}-gantt.png          # Matplotlib task bars
└── milestones-overview.png        # Matplotlib progress comparison
```

## Scripts

Run `scripts/generate-charts.py` to produce matplotlib charts.

| Script                       | Args                       | Output                   |
| ---------------------------- | -------------------------- | ------------------------ |
| `scripts/generate-charts.py` | `<data-json> <output-dir>` | PNG charts in output dir |

## Conventions

- **Always use full GitHub URLs** — `https://github.com/Org/Repo/pull/123`, never `#123`
- **Always use absolute paths** — `/home/user/project/file.md`, never relative
- **Draft messages in code fences** — no `>` blockquote prefixes, copy-paste ready
- **Latest data only** — never generate visuals from stale/cached text, always re-pull from Notion + GitHub first
- **All formats every time** — generate all output types, let human choose
