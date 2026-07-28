---
name: ai-style-guide
description: 'Build, maintain, and apply AI style guides that make model-generated prose sound like a specific writer. Covers the full loop: interview → build → apply → iterate. Use when asked to create a style guide, make AI write like me, define a writing voice, build a tone guide, or improve AI writing quality.'
interaction: interactive
type: leaf
---

# AI Style Guide

Build reusable style guides that push AI writing from generic defaults toward a specific writer's voice, tone, and judgment.

A style guide is NOT a prompt. A prompt tells AI what to do. A style guide is the reusable system underneath telling AI **how to sound** while doing it.

## When to Use

- "Create a style guide for my writing"
- "Make AI write like me"
- "Define a writing voice for this column/newsletter/blog"
- "Build a tone guide"
- "My AI drafts sound too generic"
- Before any sustained AI writing project (newsletter, column, docs)

## Three Modes

| Mode                    | When                                     | What happens                                   |
| ----------------------- | ---------------------------------------- | ---------------------------------------------- |
| **Interview** (default) | Starting fresh or refining               | Interactive Q&A to surface writing preferences |
| **Build**               | After interview or with existing samples | Synthesize preferences into a structured guide |
| **Apply**               | Guide exists, drafting/revising          | Use the guide to draft or revise prose         |

---

## Mode 1: Interview

Surface the writer's preferences through reactive Q&A — not self-description.

### Rules

1. **One question at a time.** Never batch questions.
2. **React to examples, not generalities.** Show sample lines, paraphrases, or alternatives and ask "does this sound like you?"
3. **Surface both preferences and aversions.** What they like AND what they hate.
4. **Get concrete.** "Smart and conversational" is not enough. Ask: "How formal? How much emotional temperature? What tone feels completely wrong?"

### Interview Flow

1. **Ask for samples** — 3-5 pieces of their writing, or writing they admire
2. **Voice & tone** — How should this feel? What's the emotional range? What's off-limits?
3. **Structure** — How do pieces open? How quickly to the point? Anecdote→argument or concept→example?
4. **Sentence rhythm** — Short and punchy or long and accumulative? Punctuation preferences?
5. **Signature moves** — What does this voice do especially well? Zoom out from concrete? Humor to cut abstraction?
6. **Anti-patterns** — Show AI-generated samples and ask what feels wrong. Build the blacklist reactively.
7. **Examples** — Which of these openings sounds more like you? Which ending feels dead? Why?

### Key Questions to Ask

- "Which of these two openings sounds more like you?" (show options)
- "What do you hate about this paragraph?"
- "Why does this sentence feel too polished?"
- "Which published piece feels most representative of your voice?"
- "What tone feels completely wrong for your writing?"
- "How much emotional temperature does your writing have?"
- "How do you typically open a piece — scene, question, claim, friction?"

### After Interview

Transition to Build mode. Synthesize into the 8-section template.

---

## Mode 2: Build

Synthesize interview responses (or provided samples) into a structured style guide.

### Use the 8-Section Template

See `reference/template.md` for the full template with examples. The sections:

1. **Voice and tone** — How the writing should feel, with tensions and boundaries
2. **Structure** — How pieces move (opening strategies, argument progression, endings)
3. **Sentence-level preferences** — Line-by-line habits (rhythm, diction, concreteness)
4. **Signature moves** — Named patterns this voice does well
5. **Anti-patterns / blacklist** — Pattern→solution table of what to avoid
6. **Positive examples** — Paragraphs, openings, sentences that nail the tone
7. **Negative examples** — AI-generated lines that miss, with explanation of why
8. **Revision checklist** — Testable assertions for evaluating drafts

### Quality Bar

- Every rule should be **specific enough to change model behavior.** "Write clearly" fails this test. "Favor concrete nouns and verbs over vague framing language" passes.
- Anti-patterns should have **pattern→solution pairs**, not just "avoid X."
- Examples should have **brief explanations** of why they work or fail.
- The guide should be **testable** — you can check a draft against it.

### Output

Save the guide as a markdown file. Recommended locations:

- Claude Project system prompt (for persistent use)
- `reference/` directory in a relevant skill
- Standalone document the writer can paste into any AI conversation

---

## Mode 3: Apply

Use an existing style guide to draft or revise prose.

### Drafting

1. Load the style guide into context
2. Draft with the guide as behavioral constraints
3. After drafting, run the revision checklist against the output
4. Flag any blacklist patterns that survived

### Revising

1. Load the style guide + the draft
2. Check against the anti-pattern blacklist first (highest signal)
3. Verify structural shape matches the guide's preferences
4. Check sentence-level rhythm and diction
5. Run the revision checklist
6. Report: what was changed and why

---

## Maturity Levels

### Level 1: Starter Guide (20 minutes)

For writers just beginning with AI. Enough to escape the model's default voice.

- 3-5 bullets on voice (with tensions, not just adjectives)
- Preferred structural shape
- Blacklist of 5-10 AI prose anti-patterns
- 2-3 example passages you like, with notes on why

**Where to put it:** Paste into the chat window when needed.

### Level 2: Working Guide (built over weeks)

For writers drafting regularly with AI. Built from real corrections.

- Full 8-section template
- Named signature moves
- Revision checklist from real problems
- Structural templates for recurring formats
- Expanded anti-patterns with before/after examples

**Where to put it:** Claude Project or custom GPT system prompt.

### Level 3: Compound System

For writers with AI deep in their workflow. The guide becomes infrastructure.

- Automated checks that scan drafts for blacklist patterns
- Workflows that run the guide against every piece before it ships
- Each editorial correction feeds back into the guide
- Same mistake never happens twice

**Where to put it:** Skill, plugin, or agent pipeline. Checked against every draft.

---

## Universal AI Writing Anti-Patterns

These are patterns AI writing converges toward regardless of topic. See `reference/anti-patterns.md` for the full list. The top offenders:

| Pattern                                         | Solution                                       |
| ----------------------------------------------- | ---------------------------------------------- |
| Hedges: "actually," "maybe," "just"             | Delete unless doing real intellectual work     |
| Correlative constructions: "not X, but Y"       | State Y directly; drop the scaffolding         |
| Rhetorical questions as filler                  | Cut or convert to declarative statement        |
| Meandering intro (>3 paragraphs to stakes)      | Start with friction or tension                 |
| Summary ending that recaps the essay            | End by extending, reframing, or leaving energy |
| Fake profundity ("at the end of the day...")    | Cut entirely                                   |
| Generic transitions ("that said," "moreover")   | Cut or make specific                           |
| Boilerplate authority ("studies show")          | Name the study or delete                       |
| Puffery ("revolutionary," "game-changing")      | Replace with specific evidence                 |
| Maddening symmetry ("It's not just X — it's Y") | State the point directly                       |
