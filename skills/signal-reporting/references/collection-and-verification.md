# Collection and verification

## Start with a source contract

For each source, record:

| Field        | Question                                                                   |
| ------------ | -------------------------------------------------------------------------- |
| Authority    | What claim is this source allowed to establish?                            |
| Query        | How is the fixed window expressed, including timezone?                     |
| Freshness    | How late can observations arrive?                                          |
| Identity     | What is the unit: event, request, person, account, build, or conversation? |
| Dedupe key   | Which stable identifier prevents double counting?                          |
| Privacy      | What must remain raw/private or be aggregated before publication?          |
| Failure mode | Does a wrong field return an error, zero, `N/A`, or an ungrouped bucket?   |

Prefer primary evidence: production metrics for runtime behavior, the product analytics system for
product events, the issue tracker for current ownership, deployment state for what actually served,
and direct user feedback for user claims. Earlier reports, anchors, and ledgers are navigation aids.

## Window discipline

- Use explicit fixed boundaries. Store them in UTC; render them in the audience's timezone.
- Use the same boundaries across sources. Never combine one source's rolling `now()` with another
  source's stale epoch.
- Define a comparison before looking at the result: immediately preceding equal duration, a stable
  baseline, or the pre-change cohort. Explain why it is defensible.
- Leave an observation tail for delayed outcomes. Keep in-flight/open work visible rather than
  forcing it into success or failure.
- Save the next uncovered boundary after the run. Scheduler time is not data-window authority.

## Reconcile before interpreting

Check identities and invariants that should agree:

```text
accepted = completed + real_failures + cancellations + still_open
backend starts ≈ product accepted turns
failure endings = real failures + user cancellations
unique people at a later funnel step <= the relevant earlier-step population
```

An inequality may be expected when instruments have different capture points. If so, quantify and
name it rather than smoothing it away.

List actual event names, property names, and metric tags before declaring a zero. Many analytics
systems return an empty bucket for a nonexistent field. Verify emitter code or schema when a result
would materially change the conclusion.

## Release and canary attribution

Do not infer deployment from merge time. Query traffic by build/version and find the first and last
serving timestamps. Mixed-version windows should be segmented or disclosed. If outcome telemetry
cannot be joined to a version, state that limitation and avoid attributing the combined result to one
build.

For a canary decision, record:

- promotion or rollback thresholds and their owners;
- minimum traffic and minimum elapsed time;
- current sample, open outcomes, and maturation tail;
- control/baseline window;
- version share and any concurrent changes;
- pass, wait, or block, with the exact condition that changes the call.

“Wait” means evidence is incomplete, not that a threshold failed. “Block” means a defined safety or
quality condition failed. Keep those calls distinct.

## Qualitative evidence

Cluster feedback by underlying user outcome rather than keyword alone. Preserve a permalink or
stable source receipt privately, quote only what is necessary and authorized, and remove identifiers
from public output. One short customer sentence beside corroborating telemetry can turn an anecdote
and a metric into a finding.

## Final pre-publication pass

Immediately before send:

1. Freeze the upper boundary.
2. Re-run every displayed measure in one pass.
3. Reconcile mutable tracker and deploy claims.
4. Verify denominators and arithmetic.
5. Separate cancellations, real failures, and still-open outcomes.
6. Check that every claim is supported by the cited window.
7. Replace raw identifiers and sensitive text with aggregates or redacted examples.
