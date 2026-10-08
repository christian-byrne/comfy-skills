---
name: signal-reporting
description: 'Collect, reconcile, interpret, and publish recurring or one-off product signal reports. Use for daily digests, rollout and canary readouts, launch reports, KPI updates, incident summaries, or any Slack report that must turn telemetry and qualitative feedback into a defensible narrative rather than a metric dump.'
interaction: hybrid
type: leaf
synergies:
  enhances: [data-storytelling, slack-formatting, signal-ingest, signal-translation, signal-broadcasts]
  domain: [analytics, reporting, communication, slack]
---

# Signal Reporting

Produce a decision-ready report from heterogeneous evidence. The finished report should answer:

1. Is it working?
2. Is it getting better or worse?
3. What is surprising or newly visible?
4. What needs a person?

Do not start from a fixed list of metrics. Start from the decision, collect broadly, reconcile the
instruments, then select the facts that change the answer.

## When to use

Use this skill when a product, release, experiment, canary, incident, or operating program needs a
recurring or one-off evidence report. Do not use it for a single known metric lookup, raw dashboard
construction, or a message whose facts and narrative have already been supplied.

## Workflow

1. Establish the decision, audience, exact time window, comparison window, and observation tail.
2. Read [collection and verification](references/collection-and-verification.md), then build a
   source contract before querying. Treat cached ledgers and earlier reports as claims, not truth.
3. Pull quantitative and qualitative evidence. Preserve raw evidence privately; aggregate or redact
   anything that will be published.
4. Reconcile definitions, denominators, timestamps, deploy versions, and cross-source counts before
   interpreting movement.
5. Read [story selection](references/story-selection.md). Choose only findings that are moving,
   surprising, gating, or newly visible. A stable metric does not earn space through tradition.
6. Draft the headline as a conclusion a teammate could repeat aloud. Put derivation, provenance,
   definitions, and caveats below the evidence they qualify.
7. For Slack, read [Slack digest composition](references/slack-digest.md) and build with
   [`scripts/slack_blocks.py`](scripts/slack_blocks.py). Validate every part before sending.
8. Re-query mutable sources and recompute every published number in one pass immediately before
   publication. If the headline send fails, send no thread replies.
9. Record the fixed window, source receipts, publication receipt, unresolved blind spots, and next
   uncovered boundary so retries and later editions cannot duplicate or silently overlap work.

## Non-negotiable distinctions

- A user cancellation is not a system failure.
- A missing measurement is not a passing check.
- A merge is not proof of deployment; verify which build served the window.
- An event count is not necessarily a population. Use the authoritative denominator.
- Correlation across a release boundary is not causation; state what the comparison establishes.
- A short-window percentile is a watch signal unless the sample and decision bar support more.
- Publication is an external action. Draft unless the target and sender are explicitly authorized.

## Output contract

Deliver a compact headline plus supporting evidence, not an analysis transcript. Every published
number must carry at least one of: a denominator, comparison, threshold, ceiling, or uncertainty
interval. Name the denominator in words. Use one memorable figure, one interpretation per evidence
group, asks grouped by owner, and a specific blind-spots note.

Skip publication when there is no honest, useful story. “Nothing materially changed” is a valid
record; manufacturing novelty is not.
