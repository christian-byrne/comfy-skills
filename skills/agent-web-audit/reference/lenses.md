# Agent-Web Reviewer Lenses

Five profile cards, one per path in `../SKILL.md` plus a split of path 3. Each reviewer adopts one lens
exclusively and reads its criteria file in full before looking at any code.

**Drop the lenses whose path is closed for the surface under review.** On an authenticated console,
Crawler & Discovery and Extractability have nothing to find, and running them produces filler that
buries the two lenses that matter. On a static docs site, Agent Operability usually does.

Contract for every lens: read-only, no writes, no GitHub posting, every finding anchored `path:line`,
close with a `COVERAGE / GAPS` line.

Give every card the fingerprint output from `scripts/agent-web-probe.sh` — a lens that does not know the
render mode will produce confident nonsense.

## Handoff

Criteria: `reference/handoff-checks.md`.

Challenge the cost of moving this page into a prompt **by hand**. The actor here is a person, not a
fetcher — this is the path that still works when the surface is behind a login, and the one nobody
designs for. Ask:

- is there any export affordance at all — copy as markdown, copy for agent, a `.md` twin of the route,
  an export or print view? On the specific pages people actually quote, not in the abstract.
- do ids, keys, endpoints, error codes and log lines have their own copy control, or must they be
  retyped by eye?
- does the content survive the copy — `user-select: none`, meaning in `::before` content, `div` grids
  that paste as one run-on line, values only present in their truncated form?
- does every coherent unit have its own URL, and is there also one aggregate route that returns the
  whole thing in a single fetch?
- what silently truncates on copy — a virtualized list, infinite scroll, an unmounted tab, a wizard
  step? Is there an escape (`?all=1`, an export, a paged route)?
- could a script walk this — stable pagination, a total count, `429` with `Retry-After`, a token it can
  authenticate with?

A missing copy button is friction; a missing accessible name is a wall. Do not file them at the same
severity. And never propose dropping virtualization — propose the escape hatch.

## Crawler & Discovery

Criteria: `reference/aeo-code-checks.md` §1-2, plus `reference/llms-txt-review.md` when the diff touches
`llms.txt`.

Challenge whether the content can be reached and found at all. Ask:

- which of the 14 AI crawlers can actually fetch this, counting middleware, WAF rules, bot challenges,
  and `X-Robots-Tag` — not just `robots.txt`?
- is a critical crawler (`GPTBot`, `ChatGPT-User`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`) blocked,
  and is that a decision someone made or a default nobody read?
- do `robots.txt`, `sitemap.xml`, `llms.txt`, and `AGENTS.md` agree with each other and with the routes
  that exist today?
- is each descriptor generated from the route source or hand-maintained, and what catches the drift?
- does the build actually ship these files to the deployed root?

Report the crawl/cite trade honestly where blocking is deliberate. Do not moralize about a publisher's
choice to block.

## Extractability

Criteria: `reference/aeo-code-checks.md` §3-5.

Challenge whether the answer survives being fetched. Ask:

- does the primary content exist in the initial HTML, or only after JS and a client-side fetch?
- what content hides behind an interaction — tab, accordion, "read more", infinite scroll?
- is there `noindex` or a bad canonical leaking onto public routes from a shared layout default?
- is JSON-LD present for the page type, absolute-URL'd, and generated from the same data as the visible
  copy — or hand-written and already drifting?
- would a RAG pipeline lifting one section out of this page get a self-contained answer, or a fragment
  full of pronouns pointing at the nav?
- does the copy carry statistics, citations, and named sources (the measured +37% / +40% levers), or
  adjectives?

Never file keyword advice. Stuffing measured **-10%** on Perplexity in the KDD '24 study.

## Agent Operability

Criteria: `reference/agent-native-checks.md` §1-4.

Challenge whether a program can drive this UI. Ask:

- does every interactive element have a role and a non-empty, unambiguous accessible name?
- is state (`pressed`, `checked`, `expanded`, `selected`, `busy`, `disabled`) readable, or only visual?
- how does an agent know an action finished — a live region, a status role, or nothing but a spinner
  that a screenshot cannot distinguish from a hang?
- are there duplicate accessible names in one view, so an agent silently targets the wrong control?
- what is inside a `<canvas>`, WebGL surface, or closed shadow root, and is there any bridge to it?
- is every action reachable by keyboard, with no hover-only affordances and no focus traps?
- would an `toMatchAriaSnapshot()` assertion on this view catch the next refactor that breaks all of it?

`data-testid` is never the fix for a missing accessible name. Do not restate WCAG findings that have no
agent consequence — route those to a WCAG scanner.

## Programmatic Path

Criteria: `reference/agent-native-checks.md` §5.

Challenge whether the agent should be in the UI at all. Ask:

- is there a CLI, API, or MCP surface that does this same operation, and does anything point an agent
  at it — `llms.txt`, `AGENTS.md`, the docs?
- is the schema (OpenAPI/GraphQL) published, current, and fetchable without a login?
- can a headless agent get a credential, or is the only path an interactive OAuth redirect?
- do CORS rules and rate limits permit the environment agents actually run in?
- do failures return something an agent can act on, or a generic 500 and a toast with no response body?
- are the write endpoints idempotent, given that agents retry?

Scope discipline: "expose an MCP server" is a roadmap conversation, not a review comment, unless the diff
is already building the agent surface. When it is, say what shape it should take and why.
