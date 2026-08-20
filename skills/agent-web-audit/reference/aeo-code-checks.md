# AEO / GEO Checks Against Source

AEO (answer-engine optimization) and GEO (generative-engine optimization) are the same practice: getting
**cited** by ChatGPT, Claude, Perplexity, Gemini, and Google AI Overviews rather than **ranked** by Google.
The mechanisms differ from SEO — answer engines run RAG over embeddings, not PageRank over a link graph.
Only ~12% of ChatGPT citations match Google's top 10, and ~80% of LLM citations do not rank in Google's
top 100 — so "our SEO is fine" is not evidence that AEO is fine.



## §1. Crawler access (robots.txt, headers, middleware)

If a crawler is blocked, that platform **cannot cite you** — blocking prevents training _and_ citation.
Check `robots.txt`, plus any edge middleware, WAF rule, `X-Robots-Tag` header, or bot-detection
dependency that blocks by user-agent (a Cloudflare bot-fight setting or a `isBot()` gate in middleware
blocks agents that `robots.txt` allows — read the code, not just the file).

| Crawler             | Platform               | Criticality |
| ------------------- | ---------------------- | ----------- |
| `GPTBot`            | OpenAI (training)      | Critical    |
| `ChatGPT-User`      | OpenAI (live browsing) | Critical    |
| `OAI-SearchBot`     | OpenAI (search)        | Secondary   |
| `ClaudeBot`         | Anthropic              | Critical    |
| `anthropic-ai`      | Anthropic (training)   | Secondary   |
| `PerplexityBot`     | Perplexity             | Critical    |
| `Google-Extended`   | Google Gemini / AIO    | Critical    |
| `GoogleOther`       | Google (other AI)      | Secondary   |
| `CCBot`             | Common Crawl           | Secondary   |
| `Bytespider`        | ByteDance              | Secondary   |
| `cohere-ai`         | Cohere                 | Secondary   |
| `Applebot-Extended` | Apple Intelligence     | Secondary   |
| `FacebookBot`       | Meta AI                | Secondary   |
| `Amazonbot`         | Amazon Alexa / AI      | Secondary   |

Findings to raise:

- a critical crawler blocked with no recorded decision — **blocking**, and needs an owner, not a silent flip
- `Disallow: /` under `User-agent: *` with no AI-specific allow — check whether that is intentional
- no `Sitemap:` directive in `robots.txt`
- a user-agent allowlist that will silently drop every crawler added after it was written
- **The blocking dilemma is a product decision, not a bug.** A defensible middle ground is blocking
  training-only bots (`CCBot`, `anthropic-ai`) while allowing search/browse bots (`GPTBot`,
  `ChatGPT-User`, `PerplexityBot`, `Google-Extended`). Crawl-to-refer ratios are lopsided (Cloudflare
  2025: Anthropic up to 500,000:1, OpenAI ~3,700:1 at peak, Perplexity ~700:1), so a publisher choosing
  to block is making a rational trade. Surface the trade; do not moralize about it.

## §2. Discovery surface (the machine-readable descriptor family)

| File           | Answers                               | Check                                                 |
| -------------- | ------------------------------------- | ----------------------------------------------------- |
| `robots.txt`   | may I crawl?                          | §1                                                    |
| `sitemap.xml`  | what pages exist?                     | generated? includes new routes? referenced in robots? |
| `llms.txt`     | what matters, and where do I start?   | `reference/llms-txt-review.md`                        |
| `AGENTS.md`    | how do I work in this repo?           | present, current, points at real commands             |
| `/pricing.md`  | what does it cost? (machine-readable) | opportunity for commercial products                   |
| `openapi.json` | what can I call instead of clicking?  | published and linked, not just internal               |

Two failures recur: the file exists but nothing links to it (never discovered), and the file is
generated at build time from a stale source (silently drifts from the routes it claims).

## §3. Render mode — is the answer in the HTML?

The single highest-leverage check. An answer engine's fetcher generally does **not** execute your JS.

- client-only route rendering primary content → **blocking** for citability, regardless of copy quality
- content behind an interaction (tab, accordion, "read more", infinite scroll) → invisible to the fetcher
  even on an SSR page
- SSR shell with content hydrated in from a client-side fetch → looks SSR, is not
- `noindex` / `robots: none` leaking onto public routes from a shared layout default
- canonical tag pointing at a staging or preview host
- important copy rendered inside `<canvas>` or an image with no text equivalent

Verify by reading the initial HTML the server actually returns, not the component source. When the
deployed URL is available, `curl -s <url> | grep -o '<main.*</main>'` beats reasoning about the framework.

## §4. Structured data (JSON-LD)

Schema is ~10% of a typical GEO score but it is the cheapest signal to fix. Check in source:

- JSON-LD present for the page type: `Article`, `FAQPage`, `Product`, `SoftwareApplication`,
  `Organization`, `BreadcrumbList`, `WebSite` + `SearchAction`
- generated from the same data as the visible copy — a hand-maintained JSON-LD block **will** drift from
  the rendered page, and a mismatch is worse than absence
- no fabricated `aggregateRating` / review counts (an integrity issue, and penalized when detected)
- `@id` and `url` absolute, not relative
- start from the schema.org type templates for the page type

## §5. Citability of the copy itself

From the KDD '24 GEO study (Princeton / Georgia Tech / IIT Delhi, GEO-bench, 10K queries, validated on
Perplexity) — ranked by measured visibility lift:

| Method               | Lift        | In-source check                                        |
| -------------------- | ----------- | ------------------------------------------------------ |
| Cite sources         | **+40%**    | claims link to an authority, not to internal marketing |
| Add statistics       | **+37%**    | specific numbers with a named source                   |
| Add quotations       | **+30%**    | expert quotes with name and title                      |
| Authoritative tone   | **+25%**    | demonstrated expertise, not adjectives                 |
| Fluency optimization | **+15-30%** | readability and flow                                   |
| Keyword stuffing     | **-10%**    | **actively harmful** — inverted from traditional SEO   |

Best measured combination: fluency + statistics. Lower-ranked sites gain the most (up to +115%).

Passage-level citability  — a block scores well when it is:

- **an answer block** (30pts): definition pattern ("X is a…"), answer inside the first 60 words,
  question-shaped headings
- **self-contained** (25pts): ~134-167 words, pronoun ratio under ~2%, ≥3 proper nouns — it must make
  sense when a RAG pipeline lifts it out with no surrounding page
- **structurally readable** (20pts): 10-20 word sentences, lists, real paragraph breaks
- **statistically dense** (15pts): percentages, figures, years, named sources
- **unique** (10pts): "our research", "we found", proprietary data

In a repo this maps to real code findings: one `<h1>` per route; headings that are questions users ask;
h2/h3 hierarchy not chosen for font size; copy that survives extraction without the nav around it.

## §6. E-E-A-T signals in source

Author components with real names and credentials; `dateModified` wired to actual content changes rather
than the build timestamp; an About/team page that exists as a route; outbound citations that are real
links. Fake freshness (a `dateModified` that moves on every deploy) is detectable and corrosive.
