---
name: avoid-ai-writing
description: 'Audit and rewrite content to remove AI writing patterns ("AI-isms"). Use when asked to humanize text, remove AI patterns, audit writing for AI tells, make writing sound less AI-generated, or fix robotic prose. Also use when writing marketing copy, blog posts, or any published content. Triggers: stop slop, remove slop, clean up writing, make it sound human.'
interaction: autonomous
type: leaf
---

# Avoid AI Writing

Audit and rewrite content to remove AI writing patterns. Two modes: **rewrite** (fix it) and **detect** (flag only).

Ported from [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) v3.3.1 (MIT).

## Modes

**`rewrite`** (default) — Flag AI-isms and rewrite the text to fix them.

**`detect`** — Flag AI-isms only. No rewriting. Use when:

- The writer wants to decide what to fix themselves
- Flagged patterns might be intentional
- Auditing text you don't want altered

**Detect mode triggers:** "detect," "flag only," "audit only," "just flag," "scan."

---

## Severity Tiers

### P0 — Credibility Killers (fix immediately)

- Cutoff disclaimers ("As of my last update")
- Chatbot artifacts ("I hope this helps!", "Great question!")
- Vague attributions without sources ("Experts believe")
- Significance inflation on routine events

### P1 — Obvious AI Smell (fix before publishing)

- Word-list violations (delve, leverage, harness, robust, etc.)
- Template phrases and slot-fill constructions
- "Let's" transition openers
- Synonym cycling within a paragraph
- Formulaic openings ("In the rapidly evolving world of…")
- Bold overuse
- Em dash frequency (above 1 per 1,000 words)

### P2 — Stylistic Polish (fix when time allows)

- Generic conclusions ("The future looks bright")
- Compulsive rule of three
- Uniform paragraph length
- Copula avoidance (serves as, features, boasts)
- Transition phrases (Moreover, Furthermore, Additionally)

Use P0+P1 for quick passes. Full audit covers all three.

---

## Pattern Categories

### Formatting (4)

1. **Em dashes (— and --)** — Replace with commas, periods, parentheses, or two sentences. Target: zero. Hard max: one per 1,000 words. Applies to headings too.
2. **Bold overuse** — Strip bold from most phrases. One bolded phrase per major section at most. Restructure to lead with what's important.
3. **Emoji in headers** — Remove entirely. Social posts may use 1-2 sparingly at end of line, never mid-sentence.
4. **Excessive bullet lists** — Convert to prose. Bullets only for genuinely list-like content (feature comparisons, step-by-step instructions, API parameters).

### Sentence Structure (6)

5. **"It's not X — it's Y"** — Rewrite as a direct positive statement. Max one per piece.
6. **Hollow intensifiers** — Cut `genuine`, `real`, `truly`, `quite frankly`, `to be honest`, `let's be clear`, `it's worth noting that`.
7. **Vague endorsement ("worth [verb]ing")** — Cut `worth reading`, `worth exploring`, `worth checking out`. Say _why_ instead.
8. **Hedging** — Cut `perhaps`, `could potentially`, `it's important to note that`, `to be clear`.
9. **Missing bridge sentences** — Each paragraph should connect to the last.
10. **Compulsive rule of three** — Vary groupings. Max one "adj, adj, and adj" per piece.

### Language (7)

11. **Template phrases** — Flag slot-fill constructions: "a [adj] step towards [adj] AI infrastructure," "Whether you're [X] or [Y]," "I recently had the pleasure of [verb]ing."
12. **Transition phrases** — Remove or rewrite `Moreover`, `Furthermore`, `Additionally`, `In today's [X]`, `In an era where`, `Here's what's interesting`, `In conclusion`, `When it comes to`, `At the end of the day`, `That said`.
13. **Copula avoidance** — AI replaces "is/has" with `serves as`, `features`, `boasts`, `presents`, `represents`. Default to "is" or "has."
14. **Synonym cycling** — AI rotates synonyms: "developers… engineers… practitioners… builders." Repeat the clearest word.
15. **Filler phrases** — Strip `It is important to note that`, `In terms of`, `The reality is that`.
16. **False ranges** — "From the Big Bang to dark matter" — sweeping pairings that say nothing. List actual topics.
17. **Parenthetical hedging** — "(and, increasingly, Z)" / "(or, more precisely, Y)." Give it a sentence or cut it.

### Content (7)

18. **Significance inflation** — "marking a pivotal moment in the evolution of…" — state what happened; let the reader judge.
19. **Vague attributions** — "Experts believe," "Studies show" without sources. Cite specifically or drop.
20. **Notability name-dropping** — AI piles on prestigious citations. Use one specific reference with context.
21. **Superficial -ing analyses** — "symbolizing… reflecting… showcasing…" — replace with specific facts or cut.
22. **Promotional language** — Tourism-brochure prose: "a vibrant hub of innovation." Use plain description.
23. **Formulaic challenges** — "Despite challenges, continues to thrive." Name the actual challenge and response.
24. **Novelty inflation** — AI treats existing concepts as invented: "the insight everyone's missing." Describe what was _done with_ the concept.

### Communication (8)

25. **Chatbot artifacts** — Remove "I hope this helps!", "Certainly!", "Absolutely!", "Let's dive in!", "Feel free to reach out."
26. **"Let's" constructions** — Flag "let's + verb" as a transition. Just start with the point.
27. **Cutoff disclaimers** — "As of my last update," "While specific details are limited." Never publish.
28. **Generic conclusions** — Cut "The future looks bright," "Only time will tell," "One thing is certain." Make conclusions specific.
29. **Emotional flatline** — "What surprised me most," "I was fascinated to discover" — claiming emotions without earning them. If it's surprising, the content should show it.
30. **Reasoning chain artifacts** — "Let me think step by step," "Breaking this down," "Here's my thought process." State conclusion, then evidence.
31. **Sycophantic tone** — "Great question!", "Excellent point!", "You're absolutely right!" Remove entirely.
32. **Acknowledgment loops** — "You're asking about," "To answer your question." Just answer.

### Structure (5)

33. **Confidence calibration phrases** — "Interestingly," "Notably," "Surprisingly," "Importantly." Signaling how the reader should feel instead of letting the fact speak. Flag by density.
34. **Excessive structure** — More than 3 headings in under 300 words; 8+ bullets in under 200 words; formulaic headers ("Overview," "Key Points," "Summary").
35. **Inline-header lists** — "**Performance:** Performance improved by…" Strip the bold; write the point directly.
36. **Title case headings** — Use sentence case for subheadings. Title case only for the main title, if at all.
37. **Numbered list inflation** — "Three key takeaways" / "Five things to know." Only use when content genuinely has that many discrete items.

### Meta (3)

38. **Rhythm and uniformity** — Metronomic sentence length (all 15-25 words), uniform paragraph size, missing first-person perspective, over-polishing. **Structure is the #1 AI detection signal** (Pangram Labs, 28M human docs).
39. **False concession** — "While X is impressive, Y remains a challenge" — vague balance without real weighing. Make it specific or pick a side.
40. **Rhetorical question openers** — "But what does this mean for developers?" AI stalls before making the point. Just say it.

---

## Vocabulary Table

### Tier 1 — Always replace

These appear 5-20× more often in AI text than human text. Replace on sight.

| Replace                                 | With                                            |
| --------------------------------------- | ----------------------------------------------- |
| delve / delve into                      | explore, dig into, look at                      |
| landscape (metaphor)                    | field, space, industry                          |
| tapestry                                | (describe the actual complexity)                |
| realm                                   | area, field, domain                             |
| paradigm                                | model, approach, framework                      |
| embark                                  | start, begin                                    |
| beacon                                  | (rewrite entirely)                              |
| testament to                            | shows, proves, demonstrates                     |
| robust                                  | strong, reliable, solid                         |
| comprehensive                           | thorough, complete, full                        |
| cutting-edge                            | latest, newest, advanced                        |
| leverage (verb)                         | use                                             |
| pivotal                                 | important, key, critical                        |
| underscores                             | highlights, shows                               |
| meticulous / meticulously               | careful, detailed, precise                      |
| seamless / seamlessly                   | smooth, easy, without friction                  |
| game-changer                            | describe what specifically changed              |
| hit differently                         | (say what changed, or cut)                      |
| utilize                                 | use                                             |
| watershed moment                        | turning point, shift                            |
| marking a pivotal moment                | (state what happened)                           |
| the future looks bright                 | (cut or say something specific)                 |
| only time will tell                     | (cut or say something specific)                 |
| nestled                                 | is located, sits, is in                         |
| vibrant                                 | (describe what makes it active, or cut)         |
| thriving                                | growing, active (or cite a number)              |
| showcasing                              | showing, demonstrating (or cut)                 |
| deep dive / dive into                   | look at, examine, explore                       |
| unpack / unpacking                      | explain, break down, walk through               |
| bustling                                | busy, active (or cite what makes it busy)       |
| intricate / intricacies                 | complex, detailed (or name the specifics)       |
| complexities                            | (name them, or use "problems" / "details")      |
| ever-evolving                           | changing, growing (or describe how)             |
| enduring                                | lasting, long-running (or cite how long)        |
| daunting                                | hard, difficult, challenging                    |
| holistic / holistically                 | complete, full, whole                           |
| actionable                              | practical, useful, concrete                     |
| impactful                               | effective, significant (or describe the impact) |
| learnings                               | lessons, findings, takeaways                    |
| thought leader                          | expert, authority                               |
| best practices                          | what works, proven methods                      |
| at its core                             | (cut — just state the thing)                    |
| synergy / synergies                     | (describe the actual combined effect)           |
| interplay                               | relationship, connection, interaction           |
| in order to                             | to                                              |
| due to the fact that                    | because                                         |
| serves as                               | is                                              |
| features (verb)                         | has, includes                                   |
| boasts                                  | has                                             |
| presents (inflated)                     | is, shows, gives                                |
| commence                                | start, begin                                    |
| ascertain                               | find out, determine                             |
| endeavor                                | effort, attempt, try                            |
| keen (intensifier)                      | interested, eager (or cut)                      |
| symphony (metaphor)                     | (describe the actual coordination)              |
| embrace (metaphor)                      | adopt, accept, use, switch to                   |
| despite challenges… continues to thrive | (name the challenge and response, or cut)       |

### Tier 2 — Flag when 2+ appear in the same paragraph

Legitimate in isolation; two or more together is a strong AI signal.

| Replace                         | With                                         |
| ------------------------------- | -------------------------------------------- |
| harness                         | use, take advantage of                       |
| navigate / navigating           | work through, handle, deal with              |
| foster                          | encourage, support, build                    |
| elevate                         | improve, raise, strengthen                   |
| unleash                         | release, enable, unlock                      |
| streamline                      | simplify, speed up                           |
| empower                         | enable, let, allow                           |
| bolster                         | support, strengthen                          |
| spearhead                       | lead, drive, run                             |
| resonate / resonates with       | connect with, appeal to, matter to           |
| revolutionize                   | change, transform (or describe what changed) |
| facilitate                      | enable, help, allow                          |
| underpin                        | support, form the basis of                   |
| nuanced                         | specific, subtle, detailed                   |
| crucial                         | important, key, necessary                    |
| multifaceted                    | (describe the actual facets, or cut)         |
| ecosystem (metaphor)            | system, community, network                   |
| myriad                          | many, numerous (or give a number)            |
| plethora                        | many, a lot of (or give a number)            |
| encompass                       | include, cover, span                         |
| catalyze                        | start, trigger, accelerate                   |
| reimagine                       | rethink, redesign, rebuild                   |
| galvanize                       | motivate, rally, push                        |
| augment                         | add to, expand, supplement                   |
| cultivate                       | build, develop, grow                         |
| illuminate                      | clarify, explain, show                       |
| elucidate                       | explain, clarify, spell out                  |
| juxtapose                       | compare, contrast                            |
| paradigm-shifting               | (describe what actually shifted)             |
| transformative / transformation | (describe what changed and how)              |
| cornerstone                     | foundation, basis, key part                  |
| paramount                       | most important, top priority                 |
| poised (to)                     | ready, set, about to                         |
| burgeoning                      | growing, emerging (or cite a number)         |
| nascent                         | new, early-stage, emerging                   |
| quintessential                  | typical, classic, defining                   |
| overarching                     | main, central, broad                         |
| underpinning                    | basis, foundation                            |

### Tier 3 — Flag only at high density

Normal words. Flag only when the text is saturated with vague praise instead of specifics.

| Word                           | What to do                                       |
| ------------------------------ | ------------------------------------------------ |
| significant / significantly    | Replace some with numbers, comparisons, examples |
| innovative / innovation        | Describe what's actually new                     |
| effective / effectively        | Say how or cite a metric                         |
| dynamic / dynamics             | Name the actual forces or changes                |
| scalable / scalability         | Describe what scales and to what                 |
| compelling                     | Say why it compels                               |
| unprecedented                  | Name the precedent it breaks (or cut)            |
| exceptional / exceptionally    | Cite what makes it an exception                  |
| remarkable / remarkably        | Say what's worth remarking on                    |
| sophisticated                  | Describe the sophistication                      |
| instrumental                   | Say what role it played                          |
| world-class / state-of-the-art | Cite a benchmark or comparison                   |

---

## Context Profiles

### Auto-detection

| Signal                                              | Profile                                       |
| --------------------------------------------------- | --------------------------------------------- |
| Under 300 words + hashtags or mentions              | `linkedin`                                    |
| Code blocks, API references, technical architecture | `technical-blog`                              |
| Salutation + investor/fundraising language          | `investor-email`                              |
| Step-by-step instructions, README structure         | `docs`                                        |
| No strong signals                                   | `blog` (default — all rules at full strength) |

User can override with a hint: "audit this as a linkedin post."

### Tolerance matrix

Rules not listed apply at full strength across all profiles.

| Rule                   | linkedin                  | blog   | technical-blog     | investor-email   | docs    | casual  |
| ---------------------- | ------------------------- | ------ | ------------------ | ---------------- | ------- | ------- |
| Em dashes              | relaxed (2/post)          | strict | strict             | strict           | relaxed | skip    |
| Bold                   | relaxed (hooks OK)        | strict | strict             | strict           | relaxed | skip    |
| Emoji in headers       | relaxed (1-2 end-of-line) | strict | strict             | strict           | skip    | skip    |
| Bullets                | skip                      | strict | relaxed            | strict           | skip    | skip    |
| Hedging                | strict                    | strict | relaxed ("may" OK) | strict           | relaxed | skip    |
| Word table             | strict                    | strict | partial\*          | strict           | relaxed | P0 only |
| Promotional language   | relaxed                   | strict | strict             | **extra strict** | strict  | skip    |
| Significance inflation | strict                    | strict | strict             | **extra strict** | relaxed | skip    |
| Copula avoidance       | skip                      | strict | relaxed            | strict           | skip    | skip    |
| Paragraph uniformity   | skip                      | strict | strict             | strict           | relaxed | skip    |
| Numbered lists         | relaxed                   | strict | relaxed            | strict           | skip    | skip    |
| Rhetorical questions   | relaxed (1 hook)          | strict | strict             | strict           | strict  | skip    |
| Transitions            | skip                      | strict | strict             | strict           | relaxed | skip    |
| Generic conclusions    | skip                      | strict | strict             | **extra strict** | skip    | skip    |

\*Technical-blog word table exceptions (legitimate technical meaning, do not flag):
`robust`, `comprehensive`, `seamless`, `ecosystem`, `leverage` (API sense), `facilitate`, `underpin`, `streamline`.
Still flag: `delve`, `tapestry`, `beacon`, `embark`, `testament to`, `game-changer`, `harness`.

**Extra strict** = flag even borderline instances.
**Skip** = don't audit this category.

---

## Output Format

### Rewrite mode (default) — 4 sections

1. **Issues found** — every AI-ism identified, with the offending text quoted
2. **Rewritten version** — clean version with AI-isms removed. Preserve structure, intent, and all specific details. Only change what the guidelines require.
3. **What changed** — summary of major edits
4. **Second-pass audit** — re-read the rewrite. Flag patterns that survived the first pass (recycled transitions, lingering inflation, copula swaps). Fix inline, note what changed. If clean, say so.

### Detect mode — 2 sections

1. **Issues found** — every AI-ism, grouped by severity (P0, P1, P2)
2. **Assessment** — which flags are clear problems vs. judgment calls. What the writer should definitely fix vs. what might be fine in context.

---

## Special Rules

### Self-reference escape hatch

Text inside quotation marks or code blocks (cited examples of bad writing) is exempt from flagging. Only flag patterns in the author's own prose.

### When to rewrite from scratch vs. patch

If the text has **all three**: 5+ flagged vocabulary hits across categories, 3+ distinct pattern categories triggered, and uniform sentence/paragraph length — advise a full rewrite. Patching won't fix it; the structure itself is AI-generated.

### Tone calibration — 5 principles for human-sounding rewrites

1. **Vary sentence length** — mix short with long. Fragments are fine.
2. **Be concrete** — replace vague claims with numbers, names, dates, examples.
3. **Have a voice** — use first person, state preferences, show reactions.
4. **Cut the neutrality** — humans have opinions. Take positions.
5. **Earn your emphasis** — don't tell the reader something is interesting. Make it interesting.

> The replacement table provides **defaults, not mandates.** If a flagged word is clearly the right choice in context, preserve it.

---

## Related Skills

- **copy-editing** — Seven Sweeps framework for marketing copy. Use avoid-ai-writing as a pre-sweep or post-sweep audit.

---

## Attribution

Ported from [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) v3.3.1 (MIT license).
Pattern research credits: Pangram Labs (28M human document classifier), [brandonwise/humanizer](https://github.com/brandonwise/humanizer), Wikipedia's [Signs of AI-generated text](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).
