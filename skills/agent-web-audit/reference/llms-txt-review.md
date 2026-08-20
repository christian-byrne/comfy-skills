# Reviewing an `llms.txt`

`llms.txt` (spec: [llmstxt.org](https://llmstxt.org)) is a markdown file at the site root that tells an
LLM or agent what the site is and where the authoritative content lives. It completes a family of
machine-readable descriptors: `robots.txt` = may I crawl, `sitemap.xml` = what pages exist,
`llms.txt` = **what matters and where to start**. Wiki: `llms-txt-standard`.

Adoption is still early, which cuts both ways in review: there is no established house style to conform
to, and there is also no consensus authority to appeal to. Say which parts of a finding are spec and
which are judgment.

## The spec, minimally

```markdown
# Site Title

> One-line description of what this is.

Optional short prose block. No headings other than the ones below.

## Docs

- [Page title](https://example.com/page): why an agent would open this

## Optional

- [Lower-priority link](https://example.com/other)
```

Hard parts of the spec:

- `# Title` — required, exactly one, first line
- `> blockquote` — a single-sentence summary, immediately after the title
- `## Section` — H2 groups of links; free-form names
- list items are `- [text](url)` with an **absolute** URL, and an optional `: note` after the link
- `## Optional` is special-cased: a client under context pressure may skip that section, so anything
  load-bearing must not live there
- it is markdown for machines. Prose is allowed but every sentence competes with the links for context
  budget.

Related conventions worth checking in the same review: `llms-full.txt` (the whole corpus concatenated,
for tools that want one fetch), per-page `.md` twins (`/docs/x` → `/docs/x.md`), and `AGENTS.md` in the
repo for coding agents. These are separate files with separate audiences — do not collapse them.

## Review rubric

Score the draft on these, in this order. The first two are where real drafts fail.

### 1. Destination correctness — does it send the agent to the right surface?

The highest-value property of an `llms.txt`. If the product's real interface for an agent is a CLI, an
API, or an MCP server, the file should route there and say so, not hand back marketing pages the agent
will try to click. Check:

- does every link resolve, at the deployed host, unauthenticated? A link to a login-walled dashboard is
  worse than no link — the agent burns a fetch and gets an HTML shell
- do the linked pages themselves render content without JS? (see `aeo-code-checks.md` §3)
- is the programmatic path (CLI docs, API reference, OpenAPI, MCP endpoint) present and near the top?
- are docs linked at the page level, or only the docs _home_ page the agent then has to crawl?
- is there anything an agent will misread as an instruction to act on? `llms.txt` is fetched content, not
  a trusted channel; keep it descriptive.

### 2. Currency — will it still be true in three months?

A hand-written `llms.txt` rots exactly like a hand-written sitemap.

- is it generated from the docs/route source, or hand-maintained? Hand-maintained is acceptable for a
  first draft — say so explicitly and note the drift risk rather than blocking on it
- is there a test, a link-check, or a CI job that would catch a dead link in it?
- does it duplicate facts (version numbers, pricing, endpoint names) that live elsewhere and will change
  independently? Prefer linking to the source of truth over restating it.

### 3. Selection and ordering

- top links should be the three or four things an agent asking "how do I use this product" needs
- one section per audience/task, not one section per website nav group — the nav was designed for humans
  clicking, the file is for an agent deciding
- nothing load-bearing under `## Optional`
- no link that exists only for SEO reasons; padding costs context and lowers the density of what matters

### 4. Descriptions

Each `: note` earns its bytes by saying **why an agent would open that link**, not restating the title.
`- [CLI reference](…): every command, flags, and exit codes` is useful. `- [CLI](…): our CLI` is not.

### 5. Serving and discovery

- served at the root (`/llms.txt`), `200`, `Content-Type: text/plain` or `text/markdown`
- **not** blocked by `robots.txt`, and not behind auth, geo-routing, or a bot challenge
- referenced from `robots.txt` and/or a `<link rel="llms">`-style hint if the project wants discovery
  beyond convention
- committed in the repo and shipped by the build — a file that only exists in one environment's bucket
  will disappear on the next deploy (check the build config, not just the file)

## Mistakes first drafts make

1. **Sitemap-in-markdown** — every route listed, no ranking, no descriptions. Fetching the sitemap would
   have been equivalent, so the file adds nothing.
2. **Marketing copy** — adjectives, no links. The agent needed a map, got a brochure.
3. **Human docs index copied over** — inherits the nav's structure and its assumptions about clicking.
4. **Relative URLs** — the file is fetched out of context; relative links are unresolvable.
5. **Load-bearing content under `## Optional`.**
6. **Restating versioned facts** — pricing, limits, endpoint names that immediately drift.
7. **Links behind auth** — common on dashboard-shaped products, and easy to miss when the author is
   logged in while writing it.
8. **No owner** — nothing in CI or CODEOWNERS ties the file to the docs it describes.

## Review posture

For a first draft (the common case) the useful review is not a spec-compliance grind. Confirm the shape
is right, then spend the comments on destination correctness and rot — those are the two things the
author cannot easily see and the two that decide whether the file is worth having in six months. Where
there is no best practice yet, say that outright and give the reasoning behind the recommendation so the
author can weigh it, rather than citing a standard that does not exist.
