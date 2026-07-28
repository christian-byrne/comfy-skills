---
name: flaky-test-fixer
description: 'Forensic investigation and fix workflow for flaky tests. 9-step process with a 20-category taxonomy of flakiness patterns. Use when a test fails intermittently, CI shows flakes, or asked to fix flaky tests.'
interaction: hybrid
type: leaf
synergies:
  requires: []
  enhances: [test-driven-development]
  conflicts: []
  domain: [debugging, testing]
---

# Flaky Test Fixer

Forensic investigation and fix workflow for flaky tests in target repos.

## Recent CI Failures

```
!`gh run list --status failure --limit 5 --json databaseId,conclusion,startedAt,name --jq '[.[] | {id: .databaseId, name: .name, at: .startedAt}]' 2>/dev/null || echo '(no gh CLI or no failures)'`
```

## Hard Rules

> **NEVER** skip, delete, or `.skip()` a spec as a "fix"
>
> **NEVER** guess root cause without CI error data — always download and analyze failure logs first
>
> **NEVER** apply a fix without reproducing the flake locally first (or verifying via CI logs)
>
> **ALWAYS** sweep for sibling instances of the same antipattern

## When to Use

- CI shows intermittent test failures
- A test passes locally but fails in CI (or vice versa)
- A CI-triage process identifies a flake and hands off to this workflow
- User says "fix flaky tests", "this test is flaky", "intermittent failure"

## Integration with CI Triage

If you have a broader CI-diagnosis process, it can detect flaky tests and hand off here once a failure persists after a re-run, for forensic investigation. This workflow also works invoked directly by a user.

## 9-Step Forensic Workflow

### 1. Identify the Flake

Get the test name, file, and failure history from CI.

```bash
# List recent failed runs
gh run list --status failure --limit 10

# Check if the same test fails intermittently
gh run list --workflow test.yml --limit 20 --json conclusion,startedAt \
  | jq '[.[] | {conclusion, date: .startedAt[:10]}]'
```

Look for the pattern: same test appearing in some failures but not others.

### 2. Download Failure Data

Get CI logs and extract error messages, stack traces, and timing data.

```bash
# Download failed logs for a specific run
gh run view {run_id} --log-failed

# If you need the full log
gh run view {run_id} --log > ci-log.txt

# Search for the failing test
grep -A 20 "FAIL.*{test_name}" ci-log.txt
```

Extract:

- The exact error message and stack trace
- Timing information (did it timeout?)
- Which test(s) ran before the failure (ordering clue)
- Environment details (Node version, OS, parallelism settings)

### 3. Classify Against Taxonomy

Match the failure pattern to one of the 20 categories in the [Flakiness Taxonomy](#flakiness-taxonomy) below.

Common signals:

- **"Timeout"** in error → Categories 1, 10, 18
- **"Expected X, received Y" with varying Y** → Categories 2, 3, 5, 12
- **"EADDRINUSE"** → Category 7
- **"ENOENT" or file errors** → Category 8
- **Passes alone, fails in suite** → Categories 2, 3, 11, 17
- **Date/time in diff** → Categories 6, 13, 14

### 4. Reproduce Locally

Try to reproduce the flake. If it doesn't fail on the first try, use these techniques:

```bash
# Run repeatedly to trigger intermittent failures
npx vitest run {test_file} --repeat 10

# Run with the same parallelism as CI
npx vitest run --maxWorkers=4

# Run the full suite (not just the failing file) to catch ordering issues
npx vitest run

# For timing-sensitive tests, add CPU pressure
stress-ng --cpu 4 --timeout 30s &
npx vitest run {test_file} --repeat 5
```

If you cannot reproduce locally, the CI logs from Step 2 are your reproduction evidence. Document this — some flakes are environment-specific (different OS, CPU count, memory).

### 5. Root Cause Analysis

Trace through the test code and production code to find the **actual cause**, not symptoms.

Questions to answer:

- What non-determinism exists in this code path?
- What implicit assumptions does the test make about execution order?
- What shared state could another test be mutating?
- Is there a race between setup and assertion?

Read the production code the test exercises, not just the test itself. The flake often lives in the production code's async behavior.

### 6. Sweep for Siblings

Flaky patterns rarely appear just once. Search for other instances of the same antipattern.

```bash
# Example: find all tests with raw setTimeout (timing flake)
grep -rn "setTimeout" tests/ --include="*.test.*"

# Example: find tests modifying process.env without restoring
grep -rn "process\.env\." tests/ --include="*.test.*"

# Example: find tests missing afterEach cleanup
ast-grep --pattern 'beforeEach($$$)' tests/ # compare count with afterEach

# Example: find tests using Date.now() directly
grep -rn "Date\.now\(\)\|new Date()" tests/ --include="*.test.*"
```

Record all sibling instances — they will be fixed in Step 7.

### 7. Implement Fix

Fix the root cause, not the symptom. Apply the fix to all sibling instances found in Step 6.

Guidelines:

- Fix the antipattern, don't add retries around it
- If mocking is needed, mock at the boundary (external service, clock, filesystem)
- Prefer deterministic assertions over timing-based ones
- If adding `await`, verify the promise chain is correct end-to-end

### 8. Verify Fix

Run the test repeatedly to confirm stability.

```bash
# Run the fixed test many times
npx vitest run {test_file} --repeat 20

# Run the full suite to verify no regressions
npx vitest run

# If the flake was ordering-dependent, run with shuffled order
npx vitest run --sequence.shuffle
```

All 20 repetitions must pass. If any fail, return to Step 5.

Also verify sibling fixes pass their respective tests.

### 9. Document

Add a brief comment at the fix site explaining what was flaky and why.

```typescript
// Fixed: flaky due to shared module-level `connectionPool` between tests.
// Each test now creates its own pool in beforeEach and closes in afterEach.
```

Keep it concise — future readers need to know _what was wrong_, not the full investigation story.

## Flakiness Taxonomy

| #   | Category                       | Pattern                                            | Common Fix                                        |
| --- | ------------------------------ | -------------------------------------------------- | ------------------------------------------------- |
| 1   | Timing/race condition          | `setTimeout`, unresolved promises, missing `await` | Add proper awaits, use `waitFor` utilities        |
| 2   | Shared mutable state           | Tests modify global/module-level state             | Isolate state per test, use `beforeEach` reset    |
| 3   | Test ordering dependency       | Test A sets up state Test B needs                  | Make each test self-contained                     |
| 4   | External service dependency    | Tests call real APIs/services                      | Mock external boundaries                          |
| 5   | Random data without seeds      | `Math.random()`, `uuid()` in assertions            | Use fixed seeds or deterministic data             |
| 6   | Time-sensitive assertions      | `Date.now()`, `performance.now()` comparisons      | Use fake timers (`vi.useFakeTimers()`)            |
| 7   | Port conflicts                 | Multiple test suites binding same port             | Use dynamic port allocation (`port: 0`)           |
| 8   | File system race conditions    | Temp files, parallel writes to same path           | Use unique temp dirs per test                     |
| 9   | Database state leaks           | Shared DB not cleaned between tests                | Use transactions with rollback, or truncate       |
| 10  | Event loop drainage            | Pending microtasks/macrotasks after test           | `await flushPromises()`, clean up timers          |
| 11  | Memory pressure                | Tests work in isolation but fail in suite          | Check for memory leaks, large fixtures            |
| 12  | Environment variable pollution | Tests set env vars without restoring               | Save/restore in `beforeEach`/`afterEach`          |
| 13  | Timezone sensitivity           | Tests assume UTC or local timezone                 | Use explicit timezone in assertions               |
| 14  | Locale sensitivity             | Number/date formatting varies by locale            | Use explicit locale or mock `Intl`                |
| 15  | Floating point comparison      | `0.1 + 0.2 !== 0.3`                                | Use `toBeCloseTo()`                               |
| 16  | Async cleanup missing          | Resources not cleaned up after test                | Add `afterEach` cleanup, close connections        |
| 17  | Mock restoration failure       | Mocks leak between tests                           | Use `vi.restoreAllMocks()` in `afterEach`         |
| 18  | Network timeout sensitivity    | Tests fail under slow CI networks                  | Increase timeouts, mock network calls             |
| 19  | CSS/DOM snapshot drift         | Snapshots break on minor rendering changes         | Use more specific assertions instead of snapshots |
| 20  | Retry mask                     | Test passes on retry but underlying bug persists   | Disable retries, fix the real issue               |
