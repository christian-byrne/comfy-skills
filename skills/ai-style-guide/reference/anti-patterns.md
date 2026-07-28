# AI Writing Anti-Patterns

Universal patterns that AI writing converges toward regardless of topic or model. Use this as a blacklist reference when building style guides or reviewing AI-generated prose.

## Severity: Always Cut

These patterns are never justified in good prose.

| Pattern                   | Example                                                         | Fix                                      |
| ------------------------- | --------------------------------------------------------------- | ---------------------------------------- |
| **Fake profundity**       | "At the end of the day..." / "In a world where..."              | Delete the sentence                      |
| **Puffery**               | "revolutionary," "game-changing," "transformative"              | Replace with specific evidence or delete |
| **Boilerplate authority** | "Studies show..." / "Research suggests..." / "Experts agree..." | Name the study/expert or delete          |
| **Maddening symmetry**    | "It's not just X — it's Y" / "Not merely A, but B"              | State Y directly without the scaffolding |
| **The triple**            | "It's fast, flexible, and forward-thinking"                     | Pick the one that matters most           |
| **Throat-clearing**       | "It's worth noting that..." / "It goes without saying..."       | Delete and start with the actual point   |

## Severity: Usually Cut

These occasionally do real work but are almost always filler.

| Pattern                            | Example                                                 | Fix                                       |
| ---------------------------------- | ------------------------------------------------------- | ----------------------------------------- |
| **Hedges**                         | "actually," "maybe," "just," "quite," "rather"          | Delete unless doing genuine qualification |
| **Rhetorical questions as filler** | "But what does this really mean?"                       | Convert to declarative statement or cut   |
| **Generic transitions**            | "That said," "Moreover," "Furthermore," "Additionally"  | Cut or replace with a specific connection |
| **Correlative constructions**      | "not X, but Y" / "less about A, more about B"           | State the point directly                  |
| **Sycophantic openings**           | "Great question!" / "That's a really interesting point" | Delete entirely                           |

## Severity: Watch For

These are contextual — sometimes fine, often a sign of lazy generation.

| Pattern                    | Example                                              | Fix                                            |
| -------------------------- | ---------------------------------------------------- | ---------------------------------------------- |
| **Summary endings**        | Final paragraph that restates the essay's points     | End by extending, reframing, or leaving energy |
| **Meandering intros**      | >3 paragraphs before stakes are clear                | Start with friction, tension, or a scene       |
| **Over-smooth prose**      | Every sentence flows perfectly, no friction anywhere | Let some roughness remain — it sounds human    |
| **Vague framing language** | "leverage," "utilize," "facilitate," "optimize"      | Replace with concrete verbs                    |
| **Emotional abstraction**  | "I felt a deep sense of accomplishment"              | Locate the feeling in the body or in action    |
| **List-heavy structure**   | Every section is a bulleted list                     | Vary with prose paragraphs, scenes, dialogue   |
| **Context-first openings** | Opening with history or background before the hook   | Lead with the hook, backfill context later     |

## Structural Anti-Patterns

These kill engagement even when the prose is clean.

| Pattern                                              | Impact                                  | Fix                                                      |
| ---------------------------------------------------- | --------------------------------------- | -------------------------------------------------------- |
| Abstract analysis without personal stakes            | Readers disengage — no one to root for  | Anchor in a specific person's experience                 |
| Process documentation without emotional arc          | Reads like a manual, not a story        | Add friction, surprise, or transformation                |
| Theory before practical application                  | Readers don't know why they should care | Lead with the practical, zoom out to theory              |
| Opening with context/history instead of friction     | Buries the lede                         | Start with what's at stake, backfill later               |
| Perfectly balanced "on one hand / on the other hand" | Feels like the writer has no opinion    | Take a position, acknowledge the counterargument briefly |

## How to Use This List

1. **When building a style guide:** Start with these universals, then add domain-specific patterns from real AI drafts.
2. **When revising AI prose:** Scan for severity "Always Cut" first — these are the fastest wins.
3. **When training a model via system prompt:** Include your top 10 as a blacklist with examples.
4. **When the same pattern keeps appearing:** Sharpen the instruction. "Avoid clichés" doesn't work. "Never use 'at the end of the day' or 'in a world where'" does.
