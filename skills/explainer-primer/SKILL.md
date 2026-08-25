---
name: explainer-primer
description: 'Build a multi-page plain-English primer that teaches a whole system to someone with no technical background, and publish it as a linked Notion page tree with machine-checked quality gates. Use when asked for an ELI5/ELI18 explainer, a non-technical rundown, an onboarding course, a concept primer, a cross-project glossary, "explain this system for beginners", "make our architecture understandable", or when a design doc needs a front door for PMs, designers, and new hires.'
interaction: autonomous
type: leaf
synergies:
  requires: []
  enhances: [doc-coauthoring, avoid-ai-writing, repo-doc-audit, architecture-diagram, workspace-sync]
  conflicts: []
  domain: [docs, education, notion, onboarding, diagrams]
---

# Explainer Primer

Turn a system that only its builders understand into a course anyone can read. Output is a hub page
plus one page per concept, cross-linked, diagram-first, published to Notion, and audited by a script
rather than by vibes.

This is Diátaxis **explanation** — "why is it like this," read while not at a keyboard. It is not a
tutorial, not a how-to, not reference. Do not let it drift into any of those; link to them instead.

## Pre-flight Status

```
Dir: !`pwd`
Ground-truth docs: !`ls CONTEXT.md AGENTS.md README.md 2>/dev/null | tr '\n' ' ' || echo none`
NOTION_TOKEN: !`[ -n "$NOTION_TOKEN" ] && echo set || echo 'UNSET — source your secrets file'`
Existing primer: !`find . -name primer.json -not -path '*/node_modules/*' 2>/dev/null | head -1 || echo none`
```

## When to Use

- A design doc exists but only its authors can read it, and PMs/designers/new hires keep asking
  the same five questions
- Onboarding a team onto a system with one genuinely hard idea in it (CRDTs, consensus, schedulers)
- A glossary is needed where every term links to where it is actually used
- "Write an explainer/primer/course for X"

Do **not** use for API reference, runbooks, or step-by-step tutorials.

---

## Phase 0 — Establish ground truth

Everything downstream is worthless if it is confidently wrong, and a non-technical reader cannot
catch your errors. Before writing a word:

1. **Find the canonical docs** — `CONTEXT.md`, `AGENTS.md`, ADRs, the design doc, the workspace
   registry. Read them fully, not by grep.
2. **Note what was read from source vs inferred.** Prefer docs that state their provenance
   (`verified against repo@SHA`). Record the SHAs — they go in the primer's footer.
3. **List the generations.** Most systems have a shipped version and a version being built. Almost
   every confusion in a project is one person describing one and another hearing the other. Every
   page must say which it means.
4. **List what is designed but not built.** This is the highest-value content in the whole primer:
   it is what lets a reader tell architecture from implementation.

> **Write only what the canonical docs already assert.** If a page needs a fact that is not in them,
> verify it against source and get it added there first. A primer is a re-explanation, never a new
> claim — otherwise it becomes a second source of truth that drifts.

## Phase 1 — Design the series

Draft the chapter list before writing any chapter. Three rules:

**Order by dependency, not by architecture.** The reader's questions, not the system's box diagram.
"What is this product" → "what is the thing being edited" → "what breaks" → "how we fix it."

**Put the hard idea in its own chapter and build it from zero.** If there is one genuinely difficult
concept, do not explain it in terms of the system. Build it from something the reader already knows
(counting, sets, two people editing a shopping list), _then_ map it onto the system. Give it a
problem chapter immediately before it, so the reader wants the answer before they get it.

**Separate teaching pages from lookup pages.** Chapters teach in order; a glossary, an FAQ, and a
reference index are consulted at random. Mark the latter `"reference": true` in the config — the
audit exempts them from the per-chapter diagram and scaffolding checks.

Suggested spine (adapt freely):

| Part | Chapters             | Job                                                                 |
| ---- | -------------------- | ------------------------------------------------------------------- |
| I    | What the thing is    | Product, the domain object, the interaction model, the architecture |
| II   | The hard problem     | Why the naive approach fails, then the real mechanism from scratch  |
| III  | Consequences         | Lifecycles, ownership, deployment targets, the rules and why        |
| Ref  | Glossary, FAQ, index | Lookup surfaces                                                     |

Write the list into `primer.json` (see Phase 2). **`series` order is the display order** — slugs are
identity, not sequence. Name slugs semantically (`07-crdt-from-scratch`), and never renumber a slug
to reorder a chapter; reorder the `series` array instead. Renaming a slug orphans its page.

## Phase 2 — Scaffold

```bash
python3 skills/explainer-primer/scripts/primer.py --dir reports/primer init
```

Creates `primer.json`, `pages/`, and `pages/_TEMPLATE.md`. Set `parent_page_id` to the Notion page
the hub should hang under (usually the canonical design doc — the primer belongs _under_ the thing
it explains, so it is discoverable from where people already are).

Then fill in `series`, and write one `pages/<slug>.md` per entry.

## Phase 3 — Write the chapters

Follow `reference/pedagogy.md` for the full chapter template and the teaching patterns. The
non-negotiables the audit enforces:

- **Orientation callout** at the top — where you are, what it assumes, how long, and _what you will
  be able to explain afterwards_. Objectives are stated as things the reader can say out loud.
- **At least one diagram per chapter**, as a ` ```mermaid ` block. Notion renders these
  natively, so there is no image host and no re-render step, and the diagram source lives next to
  the prose it belongs to.
- **A check-yourself toggle** at the end — questions with answers, collapsed.
- **Explicit misconception callouts.** Name the wrong belief people actually hold and correct it.
  A reader who holds it needs to see it addressed, not merely contradicted.
- **Terms introduced** + **where this lives in the real system** — every chapter hands off to the
  glossary and to real files/PRs/docs.

Cross-link with `{{slug}}` anywhere a URL would go: `[chapter 7]({{07-crdt-from-scratch}})`. It is
resolved to the real Notion URL at publish time, so nobody pastes URLs and links never rot.
Prev/next/index navigation is generated — do not hand-write it.

### The glossary is the load-bearing page

One alphabetical table: **term · plain-English definition · where it shows up**. The third column is
what makes it worth building — each term links to the chapter that teaches it _and_ the doc, repo,
or source file where it appears. Add a "terms frequently confused" table at the bottom pairing
lookalikes (`X ⟷ Y — the difference — the chapter that settles it`); it is consistently the most
useful section for people in meetings.

## Phase 4 — Publish

```bash
export NOTION_TOKEN=<your Notion integration token>   # or source it from your env manager
P=skills/explainer-primer/scripts/primer.py
python3 $P --dir reports/primer publish --dry     # parse check, touches nothing
python3 $P --dir reports/primer publish           # create + render everything
python3 $P --dir reports/primer publish 07 09     # refresh only these slugs
python3 $P --dir reports/primer entrypoints       # the "start here" callouts
```

Publishing is two-pass: every page is created first (so cross-links can resolve), then content is
rendered. `page-map.json` maps slug → page id and is **load-bearing** — commit it. Losing it orphans
the tree and the next publish creates a duplicate set.

If a publish dies partway, just run it again — pages already in `page-map.json` are reused, not
recreated.

See `reference/notion-publishing.md` for the API limits, the transport gotcha, and the safety rails.

## Phase 5 — Make it discoverable

A primer nobody finds is a primer nobody reads. Three placements, in order of value:

1. **The hub is a child of the canonical design doc**, and every chapter is a child of the hub.
   People navigate down from what they already have open.
2. **A callout at the top of every page a reader already lands on** — the design doc, the frontend
   doc, whatever the team links in standup. Configure these as `entrypoints`; the wording that
   works is a direct question plus the link:
   _"Want to understand this system and get a rundown with a non-technical lens? Start here: …"_
   Put it directly under the status banner, above the diagrams — position 1, not the bottom.
3. **On-disk registries** — the docs registry, `CONTEXT.md`, the todo log, so the next agent or
   maintainer knows the primer exists and knows not to hand-edit it in Notion.

`entrypoints` are appended, and only the skill's own marker callout is archived — so they are safe
to re-run on pages another person or agent owns.

## Phase 6 — Audit

```bash
python3 skills/explainer-primer/scripts/primer.py --dir reports/primer check
```

Read-only. Exits non-zero on failure. Checks parenting, empty pages, leaked literal markdown,
unresolved cross-links, nav footers, a diagram on every chapter, orientation and check-yourself
scaffolding, hub completeness, and entry-point placement.

Then run the two judgement checks the script cannot do — both in `reference/quality-gates.md`:

- **Style calibration against the corpus, not a generic rule.** Measure the surrounding docs before
  "fixing" anything. A generic AI-writing rule caps em dashes at 1 per 1000 words; if the team's own
  docs run at 15, matching the rule makes the primer read like a foreign object.
- **Link integrity with the right tool.** Private repos 404 to anonymous `curl`. Verify those with
  `gh api` — a 404 is not a broken link.

Fix what the audit finds and re-publish those slugs. **Ship only on a clean run.**

---

## Anti-Patterns

- ❌ **Hand-editing the published pages.** Publishing replaces page content from markdown, so Notion
  edits are destroyed on the next refresh. Say this in the primer's own README and in `CONTEXT.md`.
- ❌ **Rendering diagrams to PNG and hosting them.** You need a public image host, the images go
  stale silently against the prose next to them, and zoom degrades. Mermaid code blocks render
  natively, stay editable, and cannot drift from their caption.
- ❌ **Explaining the hard idea in terms of the system.** Build it from something the reader already
  knows first. A reader who does not know what a CRDT is cannot learn one from your wire protocol.
- ❌ **Hiding what is not built.** "Designed but not implemented" is the highest-value content in the
  primer. Status tables per capability beat prose hedging.
- ❌ **One tall page.** People stop reading. Many short pages with generated navigation and a
  glossary is strictly better, and it makes refreshes surgical.
- ❌ **Claiming anything the canonical docs do not.** Verify against source, add it there, then
  explain it here.
- ❌ **Skipping `check` because the pages "look fine."** The audit has caught a chapter with no
  diagram and a bold-swallowed link that rendered as literal markdown. Both looked fine in the diff.
- ❌ **Rewriting a page you do not own to add the entry point.** Append your marker and archive only
  your own; other agents and humans edit those pages concurrently.

## Output

- `reports/primer/` (or wherever) — `primer.json`, `pages/*.md`, `page-map.json`, a README stating
  that Notion is a render target
- A Notion hub under the canonical doc, with one subpage per chapter
- Entry-point callouts on the pages readers already land on
- A clean `check` run, quoted in the handoff

## Reference

- `reference/pedagogy.md` — chapter template, teaching patterns, the glossary spec, what to cut
- `reference/notion-publishing.md` — markdown syntax supported, API limits, transport, safety rails
- `reference/quality-gates.md` — what `check` verifies, plus the two judgement checks it cannot
