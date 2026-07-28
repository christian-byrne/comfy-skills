---
name: perf-fix-with-proof
description: 'Ships performance fixes with CI-proven improvement using stacked PRs. PR1 adds a @perf test (establishes baseline on main), PR2 adds the fix (CI shows delta). Use when implementing a perf optimization and wanting to prove it in CI.'
interaction: hybrid
type: leaf
---

# Performance Fix with Proof

Ships perf fixes as two stacked PRs so CI automatically proves the improvement.

## Why Two PRs

CI perf workflows compare PR metrics against the **base branch baseline**. If you add a new perf test in the same PR as the fix, that test doesn't exist on main yet — no baseline, no delta, no proof. Stacking solves this:

1. **PR1 (test-only)** — adds the perf test that exercises the bottleneck. Merges to main. CI runs it on main → baseline established.
2. **PR2 (fix)** — adds the optimization. CI runs the same test → compares against PR1's baseline → delta shows improvement.

## Workflow

### Step 1: Create the test branch

```bash
git worktree add <worktree-path> -b perf/test-<name> origin/main
```

### Step 2: Write the perf test

Add a test to your project's performance test suite. The test should stress the specific bottleneck.

**Test structure:**

```typescript
test('<descriptive name>', async ({ page }) => {
  // 1. Set up the scenario that exercises the bottleneck
  await setupScenario(page)

  // 2. Start measuring
  await startMeasuring(page)

  // 3. Perform the action that triggers the bottleneck (at scale)
  for (let i = 0; i < N; i++) {
    // ... stress the hot path ...
    await nextFrame(page)
  }

  // 4. Stop measuring and record
  const metrics = await stopMeasuring(page)
  recordMeasurement(metrics)
})
```

**Common metrics to capture:**

- Style recalculation count and duration
- Forced layout count and duration
- Total main-thread JS execution time
- Memory pressure delta (heap size)

### Step 3: Add test fixtures (if needed)

If the bottleneck needs a specific scenario (e.g., large data set, many DOM elements), add the fixture to your test assets directory. Keep it minimal — only the structure needed to trigger the bottleneck.

### Step 4: Verify locally

```bash
# Run with your project's test runner
npx playwright test --project=performance --grep "<test name>"
```

Confirm the test runs and produces reasonable metric values.

### Step 5: Create PR1 (test-only)

```bash
git add <test-files>
git commit -m "test: add perf test for <bottleneck description>"
git push -u origin perf/test-<name>
gh pr create --title "test: add perf test for <bottleneck>" \
  --body "Adds a perf test to establish a baseline for <bottleneck>.

This is PR 1 of 2. The fix will follow in a separate PR once this baseline is established on main.

## What
Adds \`<test-name>\` to the performance test suite measuring <metric> during <action>.

## Why
Needed to prove the improvement from the upcoming fix." \
  --base main
```

### Step 6: Get PR1 merged

Once PR1 merges, CI runs the test on main → baseline artifact saved.

### Step 7: Create PR2 (fix) on top of main

```bash
git worktree add <worktree-path> -b perf/fix-<name> origin/main
```

Implement the fix. The perf test from PR1 is now on main and will run automatically. CI will:

1. Run the test on the PR branch
2. Download the baseline from main (which includes PR1's test results)
3. Post a PR comment showing the delta

### Step 8: Verify the improvement shows in CI

The CI perf workflow posts a comment like:

```markdown
## ⚡ Performance Report

| Metric                | Baseline | PR (n=3) | Δ    | Sig |
| --------------------- | -------- | -------- | ---- | --- |
| <name>: style recalcs | 450      | 12       | -97% | 🟢  |
```

If Δ is negative for the target metric, the fix is proven.

## Test Design Guidelines

1. **Stress the specific bottleneck** — don't measure everything, isolate the hot path
2. **Use enough iterations** — the test should run long enough that the metric difference is clear (100+ frames for idle tests, 50+ interactions for event tests)
3. **Keep it deterministic** — avoid timing-dependent assertions; measure counts not durations when possible
4. **Reference the issue** — link the backlog item or issue number in the test name or PR description

## Identifying What to Fix (Measure First)

Performance work without measurement is guessing. Before writing PR1, profile and identify the specific bottleneck.

**Diagnostic decision tree:**

| Symptom                  | Where to look                                           | Common causes                                            |
| ------------------------ | ------------------------------------------------------- | -------------------------------------------------------- |
| Slow first load          | Bundle size, server response, render-blocking resources | Large JS bundle, no code splitting, blocking fonts/CSS   |
| Interaction sluggishness | Long tasks, input lag, animation jank                   | Synchronous work on main thread, N+1 React re-renders    |
| Slow post-navigation     | Data loading, client rendering                          | Unbounded queries, missing pagination, waterfall fetches |
| Slow API/backend         | Endpoint p95, DB query plans                            | N+1 queries, missing indexes, no caching                 |

**Measurement approaches:**

- **Synthetic** (Lighthouse, DevTools): controlled, reproducible, good for CI regression detection
- **RUM** (web-vitals library, CrUX): real user experience — validates synthetic findings

## Core Web Vitals Targets

| Metric                          | Good   | Needs Improvement |
| ------------------------------- | ------ | ----------------- |
| LCP (Largest Contentful Paint)  | ≤2.5s  | ≤4.0s             |
| INP (Interaction to Next Paint) | ≤200ms | ≤500ms            |
| CLS (Cumulative Layout Shift)   | ≤0.1   | ≤0.25             |

## Performance Budget Baselines

Use these as PR2 acceptance criteria when no project-specific budgets exist:

| Asset               | Budget      |
| ------------------- | ----------- |
| JS bundle (gzipped) | <200KB      |
| CSS (gzipped)       | <50KB       |
| Above-fold images   | <200KB each |
| Fonts total         | <100KB      |
| API p95 latency     | <200ms      |
| TTI on 4G           | <3.5s       |
| Lighthouse score    | ≥90         |

## Common Anti-Patterns and Fixes

| Anti-pattern                 | Fix                                                                       |
| ---------------------------- | ------------------------------------------------------------------------- |
| N+1 queries                  | Use joins/includes; batch fetches                                         |
| Unbounded data fetching      | Add pagination with `take`/`skip` or cursor                               |
| Missing image optimization   | Use `srcset`, `picture`, AVIF/WebP, explicit dimensions, `loading="lazy"` |
| Unnecessary React re-renders | `React.memo`, `useMemo`, stable references                                |
| Large JS bundles             | Dynamic imports, route-level code splitting, tree-shaking                 |
| Missing backend caching      | Time-based cache headers, `Cache-Control`                                 |

## Red Flags

Stop and profile before proceeding if you notice:

- Optimization without profiling justification ("this feels slow")
- N+1 patterns in data fetching code
- List endpoints without pagination
- Images missing dimensions, lazy loading, or responsive sizing
- Bundle size increase without explicit review
- No production performance monitoring in place

## Verification Checklist (PR2)

Before merging PR2, confirm:

- [ ] Before/after measurements exist (CI delta or local Lighthouse run)
- [ ] Specific bottleneck identified and addressed (not a shotgun optimization)
- [ ] CWV achieve "Good" classification where applicable
- [ ] Bundle size stable or reduced
- [ ] No new N+1 patterns introduced
- [ ] CI performance budget check passes
- [ ] Existing tests pass
