---
name: agent-web-audit
description: 'Audit a web frontend from source for agent-readiness — AEO/GEO (answer-engine citability, llms.txt, AI-crawler rules, JSON-LD, SSR content visibility) and agent-native operability (accessibility-tree legibility, stable role+label anchors, canvas/opaque-widget gaps, export/copy affordances for a human ferrying a page into a prompt, and a programmatic path that lets an agent skip the UI). Static source audit, not a live-URL crawl. Use when asked to audit a frontend for AI agents or LLM crawlers, check agent accessibility, review an llms.txt or robots.txt, check AEO/GEO in code, make a site agent-friendly or LLM-friendly, review a PR touching robots.txt, llms.txt, sitemaps, <head> metadata, or structured data, or design agent-friendly UX. For scoring a live deployed URL, use a dedicated GEO scoring tool instead.'
interaction: autonomous
type: orchestrator
synergies:
  requires: []
  enhances: [geo-seo, marketing, reviewing-external-prs, draft-review, adversarial-review, agent-browser]
  conflicts: []
  domain: [audit, frontend, seo, agent, review]
---

# Agent Web Audit

Two audiences read a web app that nobody designed for: the **answer engine** that decides whether to cite
it (AEO/GEO), and the **agent** that has to operate it (accessibility tree, or an API it never found). This
skill audits **source** for both.

## When to Use

Use it on a repo or a diff: auditing a frontend for AI agents or LLM crawlers, reviewing an `llms.txt`
or `robots.txt`, checking whether content an answer engine needs is actually in the HTML, or checking
whether an agent can operate the UI at all.

**When NOT to use:** scoring a live URL, brand-mention scanning, or generating a composite GEO score →
a live-URL GEO scoring tool. GEO content strategy is a separate discipline. Human WCAG compliance →
a dedicated accessibility scanner. Those answer "how does the deployed page score"; this one answers "what
in the repo causes that score, and which line do I change".

## The four paths

There are four ways an agent gets what it needs from a web product. **Which ones are even available is
decided by one thing: whether the surface is behind a login.** Audit in the order that applies, and do
not spend findings on a path that is structurally closed.

| #   | Path                   | The agent…                           | Authed surface                           | Public surface |
| --- | ---------------------- | ------------------------------------ | ---------------------------------------- | -------------- |
| 1   | **Programmatic**       | skips the UI — CLI, API, MCP, schema | **first**, and best                      | worth having   |
| 2   | **Handoff**            | is handed the page by a person       | **the only other one that works**        | useful         |
| 3   | **Raw fetch**          | fetches the URL and reads the HTML   | blocked by the wall                      | **first**      |
| 4   | **Browser automation** | drives the UI                        | needs a credential it usually cannot get | second         |

Paths 3 and 4 are a machine arriving under its own power. Path 2 is a **different actor** — a person
ferrying the page into a prompt — so its test is "how many actions does that take, and does the content
survive the trip." Path 1 is the recognition that the best affordance is often no UI at all.

On a login-walled console, 3 and 4 are closed and the whole game is 1 and 2. On a docs or marketing
site, 3 dominates. Getting this ordering wrong is the most common way an audit produces true findings
that do not matter.

## Mode

| Ask                                                 | Mode                                                          |
| --------------------------------------------------- | ------------------------------------------------------------- |
| "audit this frontend for agents / AI search"        | **A. Repo sweep** — steps 1-4 below                           |
| "review this PR" (touches head/robots/llms/JSON-LD) | **B. Review lens** — step 1, then the lenses on the diff only |
| "is this llms.txt right?"                           | **C. Artifact review** — `reference/llms-txt-review.md` alone |
| "how should we build this so agents can use it?"    | **D. Author mode** — `reference/component-guidance.md` alone  |

In mode B, findings must anchor to a line **in the diff**. Adjacent pre-existing gaps go in a single
"outside this diff" note, never as PR comments. Follow the host review process's comment style.

## 1. Fingerprint first (never skip)

Every downstream finding depends on this, and getting it wrong produces confident nonsense.

```bash
bash skills/agent-web-audit/scripts/agent-web-probe.sh <repo-root>
```

It reports: render mode (SSR / SSG / SPA / hybrid + per-route escapes), router, framework, where
`<head>` is assembled, presence of `robots.txt` / `llms.txt` / sitemap / `AGENTS.md`, JSON-LD sites,
`<canvas>` usage, and role/label vs `data-testid` anchor density. Read its output before dispatching
anything. **A client-only SPA changes the verdict on almost every AEO check** — an answer engine that
does not execute JS sees an empty `<div id="app">`, so "the copy is well structured" is irrelevant until
the content ships in the initial HTML.

## 2. Discover the house rules

- target repo `AGENTS.md` (all levels), `docs/adr/*`, `CONTRIBUTING`
- existing `robots.txt`, `llms.txt`, sitemap config, meta/SEO helper modules — the current convention
  beats this skill's defaults
- what the product _is_: a docs site, a dashboard behind auth, and a marketing page have different
  agent contracts. A logged-in dashboard should score badly on citability and that is correct — do not
  file AEO findings against pages no crawler can reach.

## 3. Dispatch the lenses

Five profile cards in `reference/lenses.md`, one per path plus a split of path 3, run as parallel
read-only subagents (each: read its criteria file in full, then the named files; no writes, no posting;
every finding `path:line` + severity; end with a `COVERAGE / GAPS` line).

| Path | Lens                    | Asks                                                          | Criteria                              |
| ---- | ----------------------- | ------------------------------------------------------------- | ------------------------------------- |
| 1    | **Programmatic Path**   | Should the agent be in the UI at all?                         | `reference/agent-native-checks.md` §5 |
| 2    | **Handoff**             | How cheaply can a person get this page into a prompt?         | `reference/handoff-checks.md`         |
| 3    | **Crawler & Discovery** | Can it be fetched, found, and indexed by the right bots?      | `reference/aeo-code-checks.md` §1-2   |
| 3    | **Extractability**      | Once fetched, is the answer in the HTML and machine-parsable? | `reference/aeo-code-checks.md` §3-5   |
| 4    | **Agent Operability**   | Can an agent drive the UI without pixels or guesswork?        | `reference/agent-native-checks.md`    |

Drop the lenses whose path is closed for this surface rather than running them and reporting nothing.
Add a 6th only when the diff earns it: i18n/hreflang, or auth/CORS for headless access.

## 4. Report

Per lens: findings as `severity — path:line — what breaks — the fix`. Then:

- **Blocking** — an agent or crawler cannot complete the job at all (blocked critical crawler,
  content only in client JS, control with no accessible name, endpoint an agent cannot authenticate to).
- **Degrading** — it works but poorly (thin llms.txt, missing JSON-LD, `div` handlers, unlabelled icon buttons).
- **Opportunity** — cheap wins with real evidence behind them (llms.txt where none exists; statistics
  and citations in copy, +37%/+40% visibility in the KDD '24 benchmark).

Do not invent a 0-100 score here — a live-URL scoring tool owns scoring, and a score computed from source without
fetching the deployed page is a guess. Map findings to the six GEO pillars by name instead, and
say plainly when a claim needs the deployed URL to confirm.

## Non-findings

Do not file these; they burn reviewer trust:

- generic "add more schema" / "improve SEO" with no path:line and no named consumer
- AEO findings on authenticated or `noindex` routes (see step 2)
- keyword density advice — keyword stuffing measured **-10%** on Perplexity in the KDD '24 study; the
  reflex is inverted from traditional SEO
- "add `data-testid`" as an accessibility fix — a testid is invisible to the accessibility tree and to
  every agent that navigates by role and name; it is a test anchor, not an agent affordance
- ARIA added on top of a non-semantic element where a native element was available

## Reference

| File                               | Contents                                                                      |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| `reference/aeo-code-checks.md`     | Crawler rules (14 bots), discovery files, SSR visibility, JSON-LD, citability |
| `reference/agent-native-checks.md` | Accessibility-tree legibility, canvas gap, aria snapshots, programmatic path  |
| `reference/llms-txt-review.md`     | llms.txt spec, review rubric, the mistakes first drafts make                  |
| `reference/lenses.md`              | The four dispatch-ready reviewer profile cards                                |
| `reference/handoff-checks.md`      | Path 2: export affordances, copy fidelity, addressability, scripted crawls    |
| `reference/component-guidance.md`  | Author-facing: per-component build guidance, the three-mode legibility test   |


