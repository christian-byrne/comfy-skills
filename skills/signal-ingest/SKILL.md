---
name: signal-ingest
description: 'Collecting release signal from every source — community channels (Discord, Reddit, GitHub issues), telemetry (RUM, error tracking, product analytics), test suites (compat matrices, E2E), and ecosystem code search — with watermark discipline so nothing is read twice or missed. Use when monitoring a release in soak, setting up signal collection for a rollout, or auditing which signal sources a program actually covers.'
interaction: hybrid
type: leaf
synergies:
  enhances: [post-release, crash-triage, fleet]
  domain: [telemetry, community, monitoring, release]
---
# Signal Ingest

Every source of information about how a release behaves in the wild is a signal source. The job
is coverage (know every source that exists), access (a written recipe per source), and
watermarks (never re-read, never skip). Interpretation belongs to `../signal-translation/SKILL.md`.

## When to Use

- A release entered nightly/canary/full and needs monitoring
- Setting up or auditing a program's signal coverage
- You suspect signal exists somewhere nobody is reading

## The Source Taxonomy

Inventory sources per class; every class the program skips is a class of regression it learns
about late. The program-level inventory lives in a verification-surface ledger
(verification-surface template in the parent `post-release` skill) with one owner per row.

### 1. Community / human reports (dirty, high-value)

| Source           | Collection notes                                                                                                                                                                                                                   |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub issues    | Add a **version field** to the issue template with a deliberately wrong default; a defaulted value means the reporter skipped it — triage asks for the real version. Attribution (nightly vs stable) is the first triage question. |
| Discord / forums | Reports arrive as chat, not issues. Route promising ones to a repro owner; a community-ingest tool that aggregates mentions beats manual scrolling.                                                                                |
| Reddit / social  | Lowest signal-to-noise; scan for clusters, not single posts.                                                                                                                                                                       |
| Support tickets  | Often the only place non-technical-user breakage appears. Get a digest, not raw queue access.                                                                                                                                      |

Community signal is **passive by default** — a few thousand nightly users generate near-zero
structured reports unless asked. Pair this class with active collection:
`../community-testers/SKILL.md`.

### 2. Telemetry / product analytics (clean, needs baselines)

| Source class                                             | What it answers                                                    |
| -------------------------------------------------------- | ------------------------------------------------------------------ |
| RUM / frontend error tracking (e.g. Datadog RUM, Sentry) | Error-rate deltas, crash signatures, perf regressions per version  |
| Product analytics (e.g. PostHog)                         | Behavior deltas: feature usage drops, funnel breaks, rage patterns |
| Warehouse / notebooks (e.g. Hex)                         | Cohort and longitudinal questions dashboards can't answer          |
| In-product surveys (e.g. Typeform, NPS)                  | Sentiment shifts around a release window                           |

Rules for this class:

- **No baseline, no finding.** Record baseline as value ± spread over a stated window before
  the rollout starts. A number without a baseline and window is noise.
- **Segment by version** or the release is invisible in the aggregate.
- Every dashboard needs a named reader and cadence, or it is decoration.
- Wire threshold crossings to a chat channel (alert → channel) so reading is push, not pull.

### 3. Automated test fleets (pre- and post-release)

| Source                                                                        | What it answers                                                                                       |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Ecosystem compat matrix (fast, broad harness over all third-party extensions) | Did we break the long tail? Baseline on the control branch must be green or diffs are unattributable. |
| Ecosystem E2E suite (real browser, curated subset)                            | Did we break the supported core in real conditions?                                                   |
| Nightly CI on main                                                            | Drift detection between releases                                                                      |

Terminology discipline: name the broad-fast harness and the deep-narrow suite differently and
define both in the program glossary — teams reliably conflate them.

### 4. Ecosystem code search

Before shipping a breaking surface, grep the ecosystem (third-party extension/plugin repos) for
usage of the APIs you changed. This converts "we think nobody uses this" into a list of repos to
test or notify. Keep the query pack per breaking surface in the program workspace.

## Watermark Discipline

Per source, persist: last-read position (timestamp, issue number, message id), read cadence, and
provenance for every item routed onward (source + id + link). One agent/person owns moving each
watermark; interpreters read aggregates and never move watermarks. This is the same
ingest/interpret split fleet roles use — see the `fleet` skill family.

## Output Contract

Ingest produces **routed raw items**, each tagged with source, version attribution (or
"unattributed"), and a link. It does not conclude. Conclusions — and everything that follows
from them — belong to `../signal-translation/SKILL.md`.
