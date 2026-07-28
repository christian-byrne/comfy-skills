---
name: design-review-board
description: 'Generate Excalidraw or Mermaid review boards from technical design docs (ADRs, PRDs, TDDs, plan.mds, Slack threads). Multi-reviewer comment zones, structured decision areas. Use when asked to create a review board, design review, visualize an ADR, board from PRD, review board from plan, excalidraw review, or mermaid diagram from design doc. Supports --format excalidraw (default) and --format mermaid for embeddable GitHub diagrams.'
interaction: autonomous
type: leaf
synergies:
  requires: []
  optional: [excalidraw]
  enhances: [architecture-decision-records]
  conflicts: []
  domain: [visualization, design-review, collaboration]
---

# Design Review Board

Converts technical design documents into structured review boards with multi-reviewer comment zones, decision tracking, and concern areas.

**Two output formats:**

- **Excalidraw** (default) — drag-and-drop onto excalidraw.com for async annotation
- **Mermaid** (`--format mermaid`) — embeds directly in GitHub PRs, README files, or Notion without external tools

## Format Selection

```
--format excalidraw   Default. Produces .excalidraw JSON file.
--format mermaid      Produces Mermaid diagram (graph TD or flowchart TD).
```

If the user mentions "PR description", "GitHub", "README", "inline", or "embed" → default to `--format mermaid`.
If the user mentions "excalidraw", "annotate", "async review", "drag-and-drop" → use `--format excalidraw`.
If unclear → use `--format excalidraw` (richer layout, more reviewer features).

## Supported Source Types (Both Formats)

| Source Type         | Detection                                                                  | What Gets Rendered                                                    |
| ------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **ADR**             | File contains "Status:", "Context:", "Decision:", "Consequences:" sections | Decision tree, alternatives matrix, consequence map, migration phases |
| **PRD**             | File contains "Requirements", "User Stories", "Scope" sections             | Feature map, user flow diagram, scope boundaries, dependency graph    |
| **TDD / Test Plan** | File contains "Test", "Coverage", "Scenarios"                              | Test coverage map, scenario clusters, edge case zones                 |
| **Plan.md**         | File contains numbered tasks, phases, or "## Phase" headers                | Task dependency DAG, critical path highlight, PR split boundaries     |
| **Slack Thread**    | Pasted text with timestamps, usernames, thread structure                   | Discussion timeline, decision points extracted, open questions        |

## When to Use

- Before a design review meeting → Excalidraw board for async annotation
- Adding a diagram to a GitHub PR description → Mermaid format
- After writing an ADR → create a reviewable visual summary
- When a PRD needs stakeholder sign-off → visual feature map with comment zones
- From a Slack design discussion → extract decisions and open questions into a board
- "Create a review board from this ADR"
- "Visualize this design doc"
- "Make an excalidraw board for review"
- "Design review board from plan.md"
- "Mermaid diagram from this ADR for the PR description"
- "Embed a design board in the README"

## Workflow

> When `--format mermaid` is selected, skip Steps 2–3 (Excalidraw-specific) and follow the Mermaid Output section instead. Steps 1 and 4 apply to both formats.

### 1. Parse the Source Document

Determine the source type and extract structured data. The agent reads the document and extracts:

**For ADRs:**

- `title` — ADR title
- `status` — Proposed/Accepted/Deprecated/Superseded
- `context_summary` — 1-2 sentence context summary
- `decision_points` — list of key decisions made (max 8)
- `alternatives` — alternatives considered with brief rationale for rejection
- `consequences_positive` — positive consequences (max 6)
- `consequences_negative` — negative consequences (max 6)
- `migration_phases` — if migration strategy exists, extract phases (max 5)
- `entities` — key entities/types/interfaces defined (max 10)
- `related_adrs` — referenced ADR numbers
- `open_questions` — any unresolved questions in the doc

**For PRDs:**

- `title`, `goal_summary`
- `features` — feature list with brief descriptions (max 8)
- `user_flows` — key user journeys (max 5)
- `scope_in` / `scope_out` — what's in/out of scope
- `dependencies` — external dependencies
- `open_questions`

**For TDDs:**

- `title`, `coverage_goal`
- `test_categories` — unit/integration/e2e breakdown
- `scenarios` — key test scenarios (max 10)
- `edge_cases` — identified edge cases (max 6)
- `untested_areas` — known gaps

**For Plan.md:**

- `title`, `phase_count`
- `tasks` — task list with dependencies
- `critical_path` — longest dependency chain
- `pr_split` — suggested PR boundaries

**For Slack Threads:**

- `participants` — who was involved
- `decisions` — things that were decided
- `open_questions` — unresolved items
- `action_items` — assigned work
- `key_quotes` — important statements with attribution

### 2. Generate the Excalidraw Board

Build the `.excalidraw` JSON file following these layout conventions. All boards use the `excalidraw` skill conventions (container binding for labels, arrows after shapes, z-order).

#### Board Layout (1800×1200 canvas)

```
┌─────────────────────────────────────────────────────────────────────┐
│  TITLE BAR (y: 20-80)                                               │
│  [Doc Type Badge] [Title] [Status] [Date]                           │
├────────────────────────────────────┬────────────────────────────────┤
│                                    │                                │
│  MAIN CONTENT (x: 40-1100)        │  REVIEW SIDEBAR (x: 1160-1760)│
│                                    │                                │
│  Source-specific diagram:          │  ┌──────────────────────────┐  │
│  - ADR: decision flow + entities   │  │ 🟡 OPEN QUESTIONS       │  │
│  - PRD: feature map + flows        │  │ (yellow sticky zone)     │  │
│  - TDD: coverage map               │  │ • question 1             │  │
│  - Plan: task DAG                  │  │ • question 2             │  │
│  - Slack: timeline                 │  │ + empty slots for review │  │
│                                    │  └──────────────────────────┘  │
│                                    │  ┌──────────────────────────┐  │
│                                    │  │ 🔴 CONCERNS              │  │
│                                    │  │ (red sticky zone)        │  │
│                                    │  │ • risk 1                 │  │
│                                    │  │ + empty slots            │  │
│                                    │  └──────────────────────────┘  │
│                                    │  ┌──────────────────────────┐  │
│                                    │  │ 🟢 DECISIONS MADE        │  │
│                                    │  │ (green sticky zone)      │  │
│                                    │  │ ✓ decision 1             │  │
│                                    │  │ ✓ decision 2             │  │
│                                    │  └──────────────────────────┘  │
│                                    │  ┌──────────────────────────┐  │
│                                    │  │ 🟣 ALTERNATIVES          │  │
│                                    │  │ (purple sticky zone)     │  │
│                                    │  │ Option A vs B            │  │
│                                    │  └──────────────────────────┘  │
├────────────────────────────────────┴────────────────────────────────┤
│  REVIEWER LANES (y: bottom strip)                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                   │
│  │ Reviewer 1   │ │ Reviewer 2   │ │ Reviewer 3   │                 │
│  │ (cyan)       │ │ (orange)     │ │ (pink)       │                 │
│  │ Status: ___  │ │ Status: ___  │ │ Status: ___  │                 │
│  │ Notes: ___   │ │ Notes: ___   │ │ Notes: ___   │                 │
│  └─────────────┘ └─────────────┘ └─────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
```

#### Color Scheme

| Zone            | Background         | Stroke    | Purpose                        |
| --------------- | ------------------ | --------- | ------------------------------ |
| Title bar       | `#dee2e6` (gray)   | `#1e1e1e` | Document identity              |
| Main content    | `#ffffff`          | `#1e1e1e` | Primary diagram                |
| Open Questions  | `#ffec99` (yellow) | `#e8a500` | Unresolved items needing input |
| Concerns        | `#ffc9c9` (red)    | `#c92a2a` | Risks and blockers             |
| Decisions Made  | `#b2f2bb` (green)  | `#2b8a3e` | Locked-in choices              |
| Alternatives    | `#d0bfff` (purple) | `#7048e8` | Competing options              |
| Reviewer 1 lane | `#99e9f2` (cyan)   | `#1098ad` | First reviewer                 |
| Reviewer 2 lane | `#ffd8a8` (orange) | `#e8590c` | Second reviewer                |
| Reviewer 3 lane | `#fcc2d7` (pink)   | `#c2255c` | Third reviewer                 |

#### Element Conventions

- **Sticky notes** = rectangles with `roughness: 1`, `fillStyle: "solid"`, rounded corners (`roundness: { type: 3 }`)
- **Content boxes** = rectangles with `fillStyle: "hachure"` for the napkin aesthetic
- **Arrows** = connecting decisions to consequences, tasks to dependencies
- **Empty review slots** = dashed-border rectangles (`strokeStyle: "dashed"`) for reviewers to annotate
- **Status badges** = small rounded rectangles: green=Accepted, yellow=Proposed, red=Deprecated
- Max **8 items per zone** — if more exist, add a "+N more" ellipsis sticky
- All text uses `fontFamily: 1` (hand-drawn), `fontSize: 14-16` for content, `20-24` for headers

#### Source-Specific Main Content

**ADR Main Content:**

- Top: Entity taxonomy table (if present) as a grid of labeled boxes
- Middle: Decision flow — key decisions as diamond shapes with arrows to consequences
- Bottom: Migration phases as a horizontal timeline (numbered boxes with arrows)
- Alternatives shown as crossed-out boxes near the decisions they lost to

**PRD Main Content:**

- Top: Feature map — features as boxes grouped by priority (P0/P1/P2 columns)
- Middle: User flow — simplified flow diagram of the primary user journey
- Bottom: Scope boundary — a dashed rectangle containing "in scope" items, with "out of scope" items outside

**Plan.md Main Content:**

- Task boxes arranged as a DAG (topological sort for layout)
- Critical path highlighted with red arrows
- PR split boundaries shown as dashed group rectangles

**Slack Thread Main Content:**

- Vertical timeline with participant avatars (colored circles with initials)
- Decision points highlighted as green diamonds on the timeline
- Open questions as yellow diamonds

### 3. Multi-Reviewer Setup

The board supports up to 3 reviewer lanes. Each lane is a horizontal strip at the bottom with:

- Reviewer name placeholder (editable text)
- Status field: `[ ] Approved  [ ] Needs Changes  [ ] Blocked`
- Notes area: 3 empty dashed-border rectangles for the reviewer to type in

Reviewer count defaults to 3 but the agent can adjust based on context (e.g., if the user mentions specific reviewers).

### 4. Save Output

```bash
# Filename pattern: {source-type}-review-{short-title}.excalidraw
# Example: adr-review-entity-component-system.excalidraw
OUTPUT="design-review-board.excalidraw"
```

Print summary:

```
📋 Design Review Board generated: {filename}

  Source:     {source_type} — {title}
  Content:    {N} diagram elements
  Questions:  {N} open questions (yellow zone)
  Concerns:   {N} flagged concerns (red zone)
  Decisions:  {N} locked decisions (green zone)
  Reviewers:  {N} reviewer lanes

Drag-and-drop onto excalidraw.com to review.
```

## Mermaid Output (`--format mermaid`)

When Mermaid format is requested, skip Excalidraw board generation (Steps 2–3) and instead produce a Mermaid diagram that renders natively on GitHub, in Notion, and in most markdown renderers.

### Mermaid Structure by Source Type

**ADR → `flowchart TD`**

```
flowchart TD
  CTX["📋 Context\n{context_summary}"] --> DEC{"🔑 Decision\n{decision_title}"}
  DEC -->|Accepted| POS["✅ Positive Consequences\n• {pos_1}\n• {pos_2}"]
  DEC -->|Trade-off| NEG["⚠️ Negative Consequences\n• {neg_1}"]
  ALT1["❌ {alternative_1}\nRejected: {reason}"] -.->|Not chosen| DEC
  ALT2["❌ {alternative_2}\nRejected: {reason}"] -.->|Not chosen| DEC

  style DEC fill:#fff9c4,stroke:#f9a825
  style POS fill:#c8e6c9,stroke:#388e3c
  style NEG fill:#ffcdd2,stroke:#c62828
  style ALT1 fill:#f5f5f5,stroke:#9e9e9e
  style ALT2 fill:#f5f5f5,stroke:#9e9e9e
```

**PRD → `flowchart LR` (feature map)**

```
flowchart LR
  subgraph P0["🔴 P0 — Must Have"]
    F1["{feature_1}"]
    F2["{feature_2}"]
  end
  subgraph P1["🟡 P1 — Should Have"]
    F3["{feature_3}"]
  end
  subgraph P2["🟢 P2 — Nice to Have"]
    F4["{feature_4}"]
  end
  F1 --> F3
```

**Plan.md → `flowchart TD` (task DAG)**

```
flowchart TD
  T1["{task_1}"] --> T2["{task_2}"]
  T1 --> T3["{task_3}"]
  T2 --> T4["{task_4}"]
  T3 --> T4

  style T1 fill:#fff9c4
  linkStyle 0 stroke:#c62828,stroke-width:2px
```

Highlight the critical path with red `stroke:#c62828` links.

**TDD → `flowchart LR` (coverage map)**

```
flowchart LR
  subgraph Unit["Unit Tests ({N})"]
    U1["{test_1}"]
    U2["{test_2}"]
  end
  subgraph Integration["Integration Tests ({N})"]
    I1["{test_1}"]
  end
  subgraph Gaps["⚠️ Untested Areas"]
    G1["{gap_1}"]
  end
  style Gaps fill:#ffcdd2
```

**Slack Thread → `timeline` or `flowchart TD`**

Use `flowchart TD` with decision diamond nodes:

```
flowchart TD
  MSG1["{participant_1}: {summary}"] --> DEC1{"Decided:\n{decision_1}"}
  MSG2["{participant_2}: {summary}"] --> DEC1
  DEC1 --> OQ1["❓ Open: {open_question_1}"]
  DEC1 --> AI1["→ Action: {action_item_1} / {assignee}"]

  style DEC1 fill:#c8e6c9,stroke:#388e3c
  style OQ1 fill:#fff9c4,stroke:#f9a825
```

### Mermaid Output Rules

1. **No reviewer lanes** — Mermaid doesn't support annotations; omit the reviewer zone entirely. Add a note: `> 💬 For annotated review, run with --format excalidraw`
2. **Max 10 nodes** — Mermaid diagrams get unreadable beyond ~10 nodes. Summarize/truncate if source has more.
3. **Wrap long labels** — Use `\n` for line breaks inside node labels. Keep labels ≤40 chars per line.
4. **Fenced code block** — Always output inside a ` ```mermaid ` block, ready to paste into GitHub PR descriptions or README.
5. **Filename pattern**: `{source-type}-review-{short-title}.mmd` — save alongside the source doc.

### Mermaid Step 4: Save Output

```
💬 Design Review Board (Mermaid): {filename}.mmd

  Source:     {source_type} — {title}
  Nodes:      {N} diagram elements
  Questions:  {N} open questions (❓ nodes)
  Decisions:  {N} key decisions (diamond nodes)
  Format:     Mermaid — paste into GitHub PR description or README

> 💬 For annotated async review with reviewer lanes, run with --format excalidraw
```

## Usage Examples

### Excalidraw board (default) from a local ADR file

```
Create a review board from docs/adr/0008-entity-component-system.md
```

### Mermaid diagram for a PR description

```
Generate a mermaid design board from docs/adr/0008-entity-component-system.md --format mermaid
```

### From a PRD

```
Generate a design review board from plans/feature-prd.md
```

### Mermaid feature map from a PRD (embeddable in README)

```
Design board from plans/feature-prd.md --format mermaid
```

### From a pasted Slack thread

```
Make a review board from this Slack discussion:
[paste thread text]
```

### From a plan

```
Review board from plans/ecs-migration-plan.md
```

### Mermaid task DAG for GitHub wiki

```
Mermaid diagram from plans/ecs-migration-plan.md for the PR description
```

## Tips

- The Excalidraw board is the **final artifact** — designed to be reviewed in excalidraw.com, not round-tripped back
- Use `--format mermaid` when you want a diagram that renders natively in GitHub PRs, READMEs, or Notion without any external tools
- Reviewers add Excalidraw comments by placing text elements in the dashed review slots or anywhere on the board
- For large ADRs with many entities, the diagram will truncate to the 8 most important items per zone (Excalidraw) or 10 nodes (Mermaid)
- The empty review slots are intentionally sized for 1-2 sentences — keeps feedback focused
- To compare multiple competing boards, generate several with anonymized labels and evaluate them independently
- Mermaid output drops reviewer lanes (not supported) — add `--format excalidraw` if reviewers need annotation zones
