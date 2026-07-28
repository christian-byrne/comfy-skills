---
name: geo-seo
description: 'Automated GEO (Generative Engine Optimization) auditing. Scores any website for AI citation readiness across citability, AI crawler access, brand authority, E-E-A-T, schema markup, and platform optimization. Generates composite GEO Score (0-100) with prioritized action plans. Use when asked to audit a site for AI search, check AI visibility, score citability, check AI crawlers, generate llms.txt, scan brand mentions, or run a GEO audit.'
interaction: hybrid
type: orchestrator
---

# GEO-SEO Audit Tool

> **GEO-first, SEO-supported.** Optimizes websites for AI-powered search engines
> (ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews) while maintaining
> traditional SEO foundations.

Ported from [geo-seo-claude](https://github.com/zubair-trabzada/geo-seo-claude) (MIT). Stripped of CRM/prospect/proposal features — focused on auditing.

## Commands

| Command                 | What It Does                                           |
| ----------------------- | ------------------------------------------------------ |
| `/geo audit <url>`      | Full GEO + SEO audit with parallel analysis            |
| `/geo citability <url>` | Score content blocks for AI citation readiness         |
| `/geo crawlers <url>`   | Check AI crawler access (robots.txt for 14 bots)       |
| `/geo llmstxt <url>`    | Validate or generate llms.txt file                     |
| `/geo brands <url>`     | Scan brand mentions across AI-cited platforms          |
| `/geo schema <url>`     | Detect, validate, and generate JSON-LD structured data |
| `/geo technical <url>`  | Technical SEO audit (SSR, CWV, security headers)       |
| `/geo content <url>`    | Content quality and E-E-A-T assessment                 |
| `/geo quick <url>`      | 60-second GEO visibility snapshot                      |

## Scripts

Python utilities in `skills/geo-seo/scripts/` — install deps first:

```bash
pip install --user beautifulsoup4 requests lxml validators
```

| Script                 | Purpose                                                         | Usage                                                                 |
| ---------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| `fetch_page.py`        | Fetch HTML, parse robots.txt for 14 AI crawlers, crawl sitemaps | `python3 scripts/fetch_page.py <url> [--robots] [--sitemap] [--meta]` |
| `citability_scorer.py` | Score passages for AI citation readiness (0-100)                | `python3 scripts/citability_scorer.py <url>`                          |
| `llmstxt_generator.py` | Validate existing or generate new llms.txt                      | `python3 scripts/llmstxt_generator.py <url> [--validate\|--generate]` |
| `brand_scanner.py`     | Check Wikipedia/Wikidata entity presence                        | `python3 scripts/brand_scanner.py <brand_name>`                       |

## Full Audit Workflow (`/geo audit <url>`)

### Phase 1: Discovery (Sequential)

1. **Fetch homepage** — use `fetch_page.py` or WebFetch to retrieve HTML
2. **Detect business type** from signals:

| Type       | Signals                                                 |
| ---------- | ------------------------------------------------------- |
| SaaS       | Pricing page, "Sign up", "Free trial", `/app`, API docs |
| Local      | Phone, address, Google Maps embed, service area pages   |
| E-commerce | Product listings, cart, price elements, product schema  |
| Publisher  | Blog-heavy nav, article schema, author pages, bylines   |
| Agency     | Portfolio, case studies, "Our services", client logos   |

3. **Crawl sitemap** — `python3 scripts/fetch_page.py <url> --sitemap` (max 50 pages, 1s delay, 30s timeout)
4. **Collect page metadata** — title, meta desc, H1-H6 structure, word count, schema types, link counts, alt text, OG tags

### Phase 2: Parallel Analysis

Run these 5 analysis passes (dispatch as parallel Tasks if available):

| Analysis                  | What It Does                                                              | Script Support                                                                               |
| ------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **AI Visibility**         | Citability scoring + crawler access + llms.txt + brand mentions           | `citability_scorer.py`, `fetch_page.py --robots`, `llmstxt_generator.py`, `brand_scanner.py` |
| **Platform Optimization** | Per-platform readiness (ChatGPT, Perplexity, Google AIO, Gemini, Copilot) | Manual analysis via WebFetch                                                                 |
| **Technical SEO**         | SSR detection, security headers, Core Web Vitals risk, mobile             | `fetch_page.py --meta`                                                                       |
| **Content Quality**       | E-E-A-T scoring (Experience, Expertise, Authoritativeness, Trust)         | Manual analysis via WebFetch                                                                 |
| **Schema Markup**         | JSON-LD detection, validation, generation from templates                  | `fetch_page.py --meta` + schema templates                                                    |

### Phase 3: Synthesis — Composite GEO Score

```
GEO_Score = (Citability × 0.25) + (Brand × 0.20) + (E-E-A-T × 0.20)
          + (Technical × 0.15) + (Schema × 0.10) + (Platform × 0.10)
```

| Category                   | Weight | What It Measures                                                 |
| -------------------------- | ------ | ---------------------------------------------------------------- |
| AI Citability & Visibility | 25%    | Passage scoring, answer block quality, AI crawler access         |
| Brand Authority Signals    | 20%    | Reddit, YouTube, Wikipedia, LinkedIn mentions; entity presence   |
| Content Quality & E-E-A-T  | 20%    | Expertise signals, original data, author credentials             |
| Technical Foundations      | 15%    | SSR, Core Web Vitals, crawlability, mobile, security             |
| Structured Data            | 10%    | Schema completeness, JSON-LD validation, rich result eligibility |
| Platform Optimization      | 10%    | Per-platform readiness (Google AIO, ChatGPT, Perplexity)         |

### Score Interpretation

| Score  | Rating    | Meaning                                |
| ------ | --------- | -------------------------------------- |
| 90-100 | Excellent | Highly likely to be cited by AI        |
| 75-89  | Good      | Strong foundation, room to improve     |
| 60-74  | Fair      | Significant optimization opportunities |
| 40-59  | Poor      | Weak GEO signals; AI struggles to cite |
| 0-39   | Critical  | Largely invisible to AI systems        |

## Issue Severity Classification

- **Critical:** All AI crawlers blocked, no indexable content (JS-only + no SSR), domain noindex, 5xx on key pages
- **High:** Key crawlers (GPTBot, ClaudeBot, PerplexityBot) blocked, no llms.txt, zero Q&A content blocks, missing Organization schema
- **Medium:** Partial crawler blocking, malformed llms.txt, low citability scores (<50), missing FAQ schema, thin author bios
- **Low:** Minor schema errors, missing alt text, stale non-critical pages, missing OG tags

## AI Crawlers Checked (14)

```
GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, anthropic-ai,
PerplexityBot, CCBot, Bytespider, cohere-ai, Google-Extended,
GoogleOther, Applebot-Extended, FacebookBot, Amazonbot
```

Crawler Access Score: starts at 100, deducts 15pts per critical crawler blocked (GPTBot, ClaudeBot, PerplexityBot), 5pts per secondary, 10pts for missing sitemap.

## Citability Scoring (Per-Passage, 0-100)

Each content block is scored on 5 dimensions:

| Dimension              | Weight | Key Criteria                                                                         |
| ---------------------- | ------ | ------------------------------------------------------------------------------------ |
| Answer Block Quality   | 30pts  | Definition patterns, answer in first 60 words, question headings, source attribution |
| Self-Containment       | 25pts  | Word count 134-167 (optimal sweet spot), low pronoun ratio (<2%), ≥3 proper nouns    |
| Structural Readability | 20pts  | Avg sentence 10-20 words, lists/numbered items, paragraph breaks                     |
| Statistical Density    | 15pts  | Percentages, dollar figures, year references, named sources                          |
| Uniqueness Signals     | 10pts  | "Our research", "we found", case study indicators, specific tool mentions            |

Grades: A (80+) Highly Citable → F (<35) Poor Citability.

## Platform-Specific Optimization Notes

| Platform       | Key Factors                                                                                                           |
| -------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Google AIO** | Strong traditional SEO correlation (76% of citations from top 10), E-E-A-T heavy, question-based headings             |
| **ChatGPT**    | Wikipedia entity presence matters, community content (Reddit/forums), broader source selection beyond top 10          |
| **Perplexity** | Citation-first engine, favors academic/authoritative sources, high citation rate (~90% of answers), freshness matters |
| **Gemini**     | Google ecosystem preference, Knowledge Graph entity presence, IndexNow support helps                                  |
| **Copilot**    | Bing-powered, IndexNow protocol, LinkedIn presence boosts visibility                                                  |

## Schema Templates

Ready-to-use JSON-LD templates in `skills/geo-seo/schema/`:

| Template                    | For                            |
| --------------------------- | ------------------------------ |
| `organization.json`         | Organization with sameAs links |
| `local-business.json`       | LocalBusiness with geo/hours   |
| `article-author.json`       | Article + Person (E-E-A-T)     |
| `software-saas.json`        | SoftwareApplication            |
| `product-ecommerce.json`    | Product with offers            |
| `website-searchaction.json` | WebSite + SearchAction         |

## Output

Generate `GEO-AUDIT-REPORT.md` with:

1. Executive Summary + Overall GEO Score
2. Score Breakdown table (6 categories × weighted)
3. Issues by severity (Critical → Low)
4. Category deep dives
5. Quick Wins (top 5, implement this week)
6. 30-Day Action Plan (4 weeks themed)
7. Appendix: Pages Analyzed

## Quality Gates

- **Crawl limit:** Max 50 pages per audit
- **Timeout:** 30s per page fetch
- **Rate limiting:** 1s delay between requests
- **Robots.txt:** Always respect, always check
- **Deduplication:** Skip pages with >80% content similarity

## Market Context (Fact-Checked)

| Metric                                   | Value       | Source                         | Verification                                                                    |
| ---------------------------------------- | ----------- | ------------------------------ | ------------------------------------------------------------------------------- |
| AI traffic conversion vs organic         | 4.4x higher | Semrush June 2025              | ✅ Verified — but limited to informational/marketing queries. E-commerce mixed. |
| AI-referred traffic growth               | +527% YoY   | BrightEdge/SparkToro           | ✅ Verified                                                                     |
| AI traffic share of total                | ~1%         | Conductor 2026                 | ✅ Verified — growing fast but tiny base                                        |
| ChatGPT share of AI referrals            | 87.4%       | Conductor 2026                 | ✅ Verified                                                                     |
| GEO visibility boost (citations + stats) | Up to 40%   | Princeton/Georgia Tech KDD '24 | ✅ Verified — peer-reviewed research                                            |
| Keyword stuffing hurts AI visibility     | -10%        | Princeton/Georgia Tech KDD '24 | ✅ Verified                                                                     |

## Related Skills

- `ai-seo` — Strategy and knowledge for AI search optimization (complements this tool)
