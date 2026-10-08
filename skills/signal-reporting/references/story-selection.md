# Story selection

A report is an argument, not a dump. Its structure should remain familiar while its contents change
with the evidence.

## What earns space

Include a finding when it is:

- **moving** enough to change a decision;
- **surprising** relative to the team's working assumption;
- **gating** a launch, rollout, rollback, or owner action;
- **newly visible** because instrumentation now answers an important question.

Stable, unsurprising, ungating metrics belong in the run record, not necessarily the broadcast.

## Turn levels into meaning

Lead with change, not a bare level. Pair each number with the thing that makes it readable:

- rate: `220 people · 29% of those who saw it`;
- comparison: `31% → 48% versus the preceding equal window`;
- bar: `2.5% · need 6% or under`;
- ceiling: `350 of the 500 turns required for a decision`.

Name denominators in words. For a forwardable headline, prefer rates, per-person measures, and
conditional conversion over volumes that rise automatically with rollout size.

## Find the surprise

Inspect distributions and segments, not only totals:

- median far below mean: concentration or long-tail behavior matters;
- top of funnel improves while downstream conversion falls: reach and usefulness diverged;
- a clean step change: find the deploy, flag, pricing, or instrumentation transition;
- two supposedly equivalent instruments disagree: measurement itself is a finding;
- aggregate stability hides a broken cohort: segment by version, funding state, new/returning use,
  mode, platform, or another decision-relevant dimension.

State the implication directly. The evidence grid carries facts; one or two sentences carry the
interpretation. Do not restate the grid as prose.

## Narrative order

1. Decision or finding: are we okay, and what changed?
2. Evidence: the smallest set that proves it.
3. Product/user meaning: what behavior or experience changed?
4. Action: who needs to do what, and under what condition?
5. Blind spots: what cannot be concluded and why?

Group actions by owner, not by discovery category. A reader should scan for their team without
reading the whole report.

## Headline test

The headline should be two or three plain-language sentences a teammate could repeat. Keep ratios,
query mechanics, internal milestone names, and definitions below the fold. Avoid “5% to now” or
“before GA”; say what changed in words and put exact windows in provenance.

Use exactly one visually dominant figure. Bold labels elsewhere, not every value. If the report has
no comparison, surprise, decision, or action above the fold, it is not ready.

## Credibility

End with the specific blind spot: which event is empty, which identifier cannot be joined, which
outcome is immature, or which source is unavailable. Say “cannot measure,” never imply green.

When nothing material changed, say so compactly or skip the broadcast. Recurrence is not a reason to
invent a story.
