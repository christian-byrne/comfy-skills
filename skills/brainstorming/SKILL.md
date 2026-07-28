---
name: brainstorming
description: MUST use before creative work. Transforms ideas into fully formed designs and specs through collaborative dialogue. One question at a time, multiple choice preferred.
interaction: interactive
type: orchestrator
synergies:
  requires: []
  enhances: []
  conflicts: []
  domain: [ideation, planning]
---

# Brainstorming

Use this before any creative work to transform vague ideas into concrete designs.

Two modes: **Dialogue** (default) for iterative refinement, **Council** (`--council`) for multi-perspective analysis.

## When to Use

- Starting any new feature design
- Exploring implementation approaches
- Fleshing out requirements
- Any work where the path isn't clear

> **Writing projects?** If the creative work is writing (newsletter, column, docs, content), load `ai-style-guide` instead — it runs a specialized interview to surface voice, tone, and prose preferences, then synthesizes them into a reusable style guide.

---

## Mode 1: Dialogue (Default)

The interactive, one-question-at-a-time mode.

### Ask One Question at a Time

Don't overwhelm with multiple questions. Each turn:

1. Ask ONE focused question
2. Prefer multiple choice when possible
3. Wait for answer before continuing

### Multiple Choice Format

```
How should the API handle errors?

A) Return HTTP status codes with JSON body
B) Always return 200 with error field in body
C) Throw exceptions that propagate to client
D) Something else (please describe)
```

### Present Design in Chunks

When presenting back:

- 200-300 words per section
- Pause for validation checkpoint
- "Does this capture your intent?" before moving on

### Confidence-Gated Interrogation

Continue asking questions until you have **95% confidence** about what the user actually wants — not what they think they should want. Users often describe solutions instead of problems, or skip constraints they assume are obvious. Keep probing until:

- The core problem (not solution) is articulated
- Success criteria are concrete and measurable
- Hidden constraints have surfaced
- You can predict the user's response to "what if we did X instead?"

### Anti-Sycophancy

During brainstorming, **take positions**. Do not use phrases like:

- ❌ "That's interesting"
- ❌ "That could work"
- ❌ "Great idea"
- ❌ "I see where you're going with this"

Instead, respond with substance: "That solves X but introduces Y. Have you considered Z?" If you disagree with the user's framing, say so directly and explain why.

### Proportional Depth

Match the weight of the process to the weight of the task. A one-line config change doesn't need a full dialogue arc. Scale accordingly:

- **Clear request** — Skip discovery and go straight to proposing 2 options with a recommendation.
- **Moderate ambiguity** — Ask 1–2 focused questions, then propose.
- **High ambiguity / risky scope** — Full confidence-gated interrogation before proposing.

**Bias toward action:** When two options are genuinely close, pick one and say why. Don't stall for false precision.

### Convergence Limit

After proposing, get explicit approval before proceeding. If the user rejects, revise and repropose — **maximum 2 revision rounds**. If still not aligned after 2 rounds, ask the user to state what they want directly rather than continuing to guess.

**No implementation until approved.** Do not write code, scaffold files, or take implementation action until the user has explicitly approved a direction — even when the task seems obvious.

### Dialogue Workflow

1. **Understand the goal**: What are we trying to achieve?
2. **Explore constraints**: What must be true? What's off limits?
3. **Challenge the premise**: Is this the right problem? What if we do nothing? What existing code already solves part of this?
4. **Generate options**: Present 2-4 approaches with a clear recommendation
5. **Refine choice**: Drill into selected approach — converge within 2 revision rounds
6. **Capture**: Record the chosen direction inline (no separate design doc unless asked)

---

## Mode 2: Council (`--council`)

Multi-perspective analysis using parallel agents. Each agent embodies a distinct perspective and independently analyzes the question. An orchestrator synthesizes results into an actionable verdict.

### Flags

| Flag                  | Effect                                                |
| --------------------- | ----------------------------------------------------- |
| `--council`           | Activate council mode, 3 perspectives (default)       |
| `--council N`         | Activate with N perspectives (2-8)                    |
| `--quick`             | Shorthand for `--council 2`                           |
| `--full`              | Shorthand for `--council 8` (all perspectives)        |
| `--include name,name` | Force-add specific perspectives                       |
| `--exclude name,name` | Force-remove perspectives (advocate only if explicit) |

### The 8 Perspectives

Defined in `references/perspectives.md`:

| #   | Perspective      | Emoji | Core Question                                                            |
| --- | ---------------- | ----- | ------------------------------------------------------------------------ |
| 1   | User Advocate    | 🫂    | "How does this feel to encounter for the first time?"                    |
| 2   | Architect        | 🏛️    | "What are the load-bearing assumptions?"                                 |
| 3   | Pragmatist       | ⚙️    | "What's the simplest thing that works?"                                  |
| 4   | Skeptic          | 🔍    | "What are we not seeing?"                                                |
| 5   | Innovator        | 💡    | "What would the opposite approach look like?"                            |
| 6   | Temporal Analyst | ⏱️    | "What does this look like in 6 months?"                                  |
| 7   | Craft Critic     | 🎨    | "I've seen this a hundred times — what makes this one worth looking at?" |
| 8   | Brand Guardian   | 🛡️    | "Does every pixel reinforce who we are — or dilute it?"                  |

User Advocate is **always included** unless `--exclude advocate` is passed explicitly.

### Council Workflow

#### Step 1: Classify the Question

Read `references/classification.md`. Scan the user's question for signal words and match to a category. This determines which perspectives are most relevant and their priority order.

#### Step 2: Select Perspectives

Based on council size and classification:

- Take User Advocate first (unless excluded)
- Fill remaining seats from the category's relevance order
- Apply `--include` / `--exclude` overrides

#### Step 3: Dispatch Perspective Agents

Dispatch all N perspective agents **in parallel** using the Task tool. Each agent receives:

1. Their full perspective definition from `references/perspectives.md` (identity, methodology, signature questions, challenge targets, confidence calibration)
2. The user's question **verbatim**
3. These instructions:

```
You are the [Perspective Name] [Emoji] on a brainstorming council.

Follow your methodology step by step. For each step, show your reasoning.

At the end, provide:
- **Position**: Your recommendation in 2-3 sentences
- **Confidence**: High/Medium/Low for each aspect you assessed (reference your calibration)
- **Challenges**: Specifically push back on [challenge target perspectives] if they were also selected
- **Blind Spots**: What you know you're bad at assessing (from your confidence calibration)
```

#### Step 4: Synthesize (Orchestrator)

After all agents respond, the **orchestrator** (you, not another agent) performs synthesis following `references/synthesis.md`:

1. Map consensus (proportional thresholds)
2. Identify tensions (name conflicting values)
3. Resolve or frame tensions (false dichotomy / genuine trade-off / context-dependent)
4. Detect blind spots (what NO perspective addressed)
5. Build confidence map (aggregate by aspect)
6. Synthesize verdict (1-3 actionable sentences)
7. Order next steps (urgency → confidence → information value)

#### Step 5: Output Council Report

Structure the output as:

```markdown
## 🏛️ Council Verdict

[1-3 sentence actionable recommendation with confidence level]

### Consensus

[Points all/most perspectives agreed on]

### Tensions

[Named disagreements with values in conflict and resolution/framing]

### Blind Spots

[What no perspective addressed — the danger zone]

### Confidence Map

| Aspect | Confidence | Based On | Key Caveat |
| ------ | ---------- | -------- | ---------- |
| ...    | ...        | ...      | ...        |

### Next Steps

1. [Ordered by urgency → confidence → information value]

<details>
<summary>🫂 User Advocate</summary>
[Full perspective output]
</details>

<details>
<summary>🏛️ Architect</summary>
[Full perspective output]
</details>

[... additional perspectives ...]
```

### Reference Files

These companion files live alongside this skill and contain the detailed definitions:

- `references/perspectives.md` — Full definitions for all 6 perspectives (identity, methodology, signature questions, challenge targets, confidence calibration)
- `references/classification.md` — Question type → perspective routing table with signal words
- `references/synthesis.md` — 7-step dialectical synthesis methodology and anti-patterns

---

## Named Techniques

Structured ideation frameworks you can apply during brainstorming when the user wants volume or systematic coverage.

### 6-Question Generator

For any topic, theme, or pillar — run it through six questions to rapidly generate dozens of angles:

| Question  | What It Generates                                      |
| --------- | ------------------------------------------------------ |
| **Who**   | Audience, personas, "who benefits most"                |
| **What**  | Definitions, explanations, "what does X actually mean" |
| **Why**   | Motivation, justification, "why should you care"       |
| **How**   | Step-by-step processes, tutorials, breakdowns          |
| **When**  | Timing, deadlines, "when is the right time"            |
| **Where** | Context, platforms, "where does this apply"            |

**When to use:** When the user wants to brainstorm many topics from a single theme, explore coverage gaps in documentation, generate research directions from a broad area, or fill out a content calendar. One theme × 6 questions × 3-5 sub-angles = 20-30 ideas.

---

## Anti-Patterns (Both Modes)

- Asking 5 questions at once (dialogue mode)
- Assuming answers without confirming
- Jumping to implementation before the user has approved a direction
- Skipping validation checkpoints
- Running full discovery on a request that's already clear — go straight to proposing
- Iterating on proposals more than twice without asking the user to state what they want
- Summarization masquerading as synthesis (council mode — see `references/synthesis.md`)
- False balance across perspectives (council mode)
- Premature consensus that papers over real disagreements (council mode)
