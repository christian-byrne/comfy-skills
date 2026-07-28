# Dialectical Synthesis Methodology

The orchestrator (not a perspective agent) performs synthesis after all perspective agents have responded. This is the most critical step — bad synthesis wastes good analysis.

## The 7 Steps

### Step 1: Map Consensus

Identify claims where multiple perspectives agree. Use proportional thresholds:

| Council Size | Consensus Threshold |
| ------------ | ------------------- |
| 2            | 2/2 agree           |
| 3            | 3/3 agree           |
| 4            | 3/4 agree           |
| 5            | 3/5 agree           |
| 6            | 4/6 agree           |

For each consensus point, note:

- What they agree ON (the claim)
- How confident each is (from their confidence calibration)
- Whether any perspective is silent on this topic (silence ≠ agreement)

### Step 2: Identify Tensions

Find where 2+ perspectives **meaningfully disagree** — not just different emphasis, but genuinely incompatible recommendations.

For each tension:

- Name the perspectives in conflict
- State each position in one sentence
- Name the **values** in conflict (e.g., "speed vs. safety", "simplicity vs. flexibility")
- Rate tension severity: **Minor** (style preference) / **Significant** (affects approach) / **Fundamental** (blocks progress without resolution)

### Step 3: Resolve or Frame Tensions

For each tension identified in Step 2, classify and handle:

**Resolvable (false dichotomy):**
The disagreement dissolves on closer inspection. Propose the resolution that satisfies both sides. Example: "The Architect and Pragmatist disagree on abstraction level, but a facade pattern gives the Architect clean boundaries while the Pragmatist gets a simple API."

**Genuine trade-off:**
Real opposing forces with no free lunch. State the exchange explicitly: "Choosing X gains [benefit] but costs [price]. Choosing Y gains [other benefit] but costs [other price]." Do NOT pretend both sides can win.

**Context-dependent:**
The right answer depends on information not yet available. Name the missing information and how to get it: "This depends on expected query volume. If <1000/day, approach A. If >10,000/day, approach B. Measure current volume before deciding."

### Step 4: Detect Blind Spots

What did **no perspective** address? This is the most valuable step — the danger zone is what everyone missed, not what someone flagged.

Check for:

- Stakeholders not represented (ops team? security? legal? the person on-call at 3am?)
- Assumptions shared by ALL perspectives (therefore unchallenged)
- Time horizons not considered (everyone thinking 6 months out, nobody thinking 6 weeks or 6 years)
- Failure modes outside everyone's mental model
- Second-order effects that cross perspective boundaries

### Step 5: Build Confidence Map

Aggregate each perspective's self-reported confidence into an aspect-level view:

| Aspect                | Confidence | Based On                             | Key Caveat                    |
| --------------------- | ---------- | ------------------------------------ | ----------------------------- |
| Technical feasibility | High       | Architect (high) + Pragmatist (high) | Neither addressed edge case X |
| User adoption         | Medium     | Advocate (high) + Skeptic (low)      | No user research to validate  |
| Timeline accuracy     | Low        | Temporal (medium) + Pragmatist (low) | Novel technology, no baseline |

Confidence is the **minimum** of the relevant perspectives, not the average. One credible doubt caps confidence.

### Step 6: Synthesize Verdict

1-3 sentences. Must be:

- **Actionable** — a clear recommendation, not a summary of opinions
- **Accounts for the strongest counter-argument** — acknowledge the best reason NOT to follow this advice
- **Calibrated** — honest about confidence level

Template: "**Do X** because [strongest supporting arguments]. The main risk is [strongest counter-argument], which we mitigate by [mitigation]. Confidence: [High/Medium/Low] because [reason]."

### Step 7: Order Next Steps

Concrete actions, ordered by:

1. **Urgency** — what's time-sensitive or blocking?
2. **Confidence** — do high-confidence items first to build momentum
3. **Information value** — what, if learned, would change everything?

Each step: what to do, who should do it, what "done" looks like.

---

## Anti-Patterns

Actively avoid these — they are the most common synthesis failures:

### Summarization Masquerading as Synthesis

❌ "The Architect said X, the Skeptic said Y, and the Pragmatist said Z."
✅ "X and Y are in tension because [values conflict]. Z resolves this by [mechanism]."

### False Balance

❌ Giving equal weight to all perspectives regardless of relevance.
✅ Weight perspectives by their confidence calibration for this topic. A Skeptic's view on risk matters more than an Innovator's.

### Premature Consensus

❌ Smoothing over genuine disagreements to present a clean answer.
✅ Name the disagreement. If it's a genuine trade-off, say so. The user decides.

### Missing the Meta-Pattern

❌ Treating each perspective's output as independent data points.
✅ The **shape** of a disagreement is often the insight. If the Architect and Pragmatist disagree on every point, that itself tells you something about the problem's complexity.

### Opinion Laundering

❌ Using perspective agents to give a predetermined conclusion the appearance of deliberation.
✅ Each perspective must genuinely engage with its methodology. If a perspective would actually agree with the consensus, that's fine — but it must show its work.
