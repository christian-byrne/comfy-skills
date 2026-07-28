---
name: test-driven-development
description: Write test first, watch it fail, then implement. Red-Green-Refactor cycle. No production code without a failing test first.
interaction: hybrid
type: leaf
synergies:
  requires: []
  enhances: [flaky-test-fixer]
  conflicts: []
  domain: [testing, tdd]
---

# Test-Driven Development

## Iron Law

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

Write the test. Watch it fail. Then implement.

## CI-Verified Red-Green Cycle

TDD isn't just local — the failing test must be verified in CI before writing implementation code. This prevents false reds from local environment quirks and proves the test actually exercises the right code path.

### Phase 1: RED — Write Failing Test and Verify in CI

1. **Write the test** — just the test, no implementation code.

   ```typescript
   test('user can login with valid credentials', () => {
     const result = login('user@example.com', 'password123')
     expect(result.success).toBe(true)
   })
   ```

2. **Run it locally** — confirm it fails.

   ```bash
   pnpm test:unit -- src/path/feature.test.ts
   ```

3. **Commit and push the failing test as a PR.**

   ```bash
   git add src/path/feature.test.ts
   git commit -m "test: add failing test for user login"
   git push origin HEAD
   gh pr create --title "test: user login" --body "RED phase — failing test, implementation to follow" --draft
   ```

4. **Sleep 10 minutes, then poll CI every 2 minutes** until checks complete.

   ```bash
   PR_NUMBER=$(gh pr view --json number -q .number)
   sleep 600  # initial 10 min wait for CI to start and run

   # Poll every 2 minutes until CI completes
   while true; do
     STATUS=$(gh pr checks "$PR_NUMBER" --json state,conclusion 2>/dev/null)
     PENDING=$(echo "$STATUS" | jq '[.[] | select(.state == "PENDING" or .state == "IN_PROGRESS")] | length')
     if [[ "$PENDING" -eq 0 ]]; then
       break
     fi
     sleep 120
   done
   ```

5. **Verify the test FAILS in CI.** This is the critical gate.

   ```bash
   FAILED=$(gh pr checks "$PR_NUMBER" --json conclusion | jq '[.[] | select(.conclusion == "FAILURE")] | length')
   if [[ "$FAILED" -eq 0 ]]; then
     echo "❌ TEST DID NOT FAIL IN CI — your test is not exercising real code."
     echo "   Fix the test so it actually fails before writing implementation."
     exit 1
   fi
   echo "✅ Test fails in CI as expected — RED phase confirmed."
   ```

   If the test does NOT fail in CI, **stop**. The test is broken — it's either not running, vacuously passing, or testing the wrong thing. Fix the test before proceeding.

### Phase 2: GREEN — Make It Pass

6. **Write the minimum code to make the test pass:**

   ```typescript
   function login(email: string, password: string) {
     // Just enough to pass
     return { success: true }
   }
   ```

7. **Run locally** — confirm the test passes.

8. **Commit and push the implementation.**

   ```bash
   git add src/path/login.ts
   git commit -m "feat: implement user login (GREEN)"
   git push origin HEAD
   ```

9. **Poll CI again** (sleep 10 min, poll every 2 min) and **verify the test now PASSES in CI.**

   ```bash
   sleep 600
   while true; do
     STATUS=$(gh pr checks "$PR_NUMBER" --json state,conclusion 2>/dev/null)
     PENDING=$(echo "$STATUS" | jq '[.[] | select(.state == "PENDING" or .state == "IN_PROGRESS")] | length')
     if [[ "$PENDING" -eq 0 ]]; then
       break
     fi
     sleep 120
   done

   FAILED=$(gh pr checks "$PR_NUMBER" --json conclusion | jq '[.[] | select(.conclusion == "FAILURE")] | length')
   if [[ "$FAILED" -gt 0 ]]; then
     echo "❌ TEST STILL FAILS IN CI — implementation is incomplete."
     echo "   Fix the implementation and push again."
   else
     echo "✅ All CI checks pass — GREEN phase confirmed."
   fi
   ```

### Phase 3: REFACTOR

10. **Improve the implementation** — proper validation, error handling, clean code.
11. **Tests must keep passing** throughout refactoring. Run after every change.
12. **Push and verify CI stays green** after refactoring.

### Phase 4: PROPERTIES (optional but recommended)

After green, ask: **does this function have an invariant that should hold for ALL inputs?** Common shapes:

- **Round-trip** — save/load, serialize/deserialize, encode/decode pairs → `fc.assert(fc.property(..., (x) => decode(encode(x)) === x))`
- **Idempotency** — normalize, format, cache write → `f(f(x)) === f(x)`
- **Ordering invariant** — output always sorted, priority queue always dequeues in non-decreasing order
- **Redaction never leaks** — `Secret.toString()` always returns `'[REDACTED]'` for any input value
- **State machine validity** — every valid transition returns the target state; every invalid pair throws

`fast-check` is installed as a root devDependency. Reach for it when the function has a clear algebraic property that holds for ALL inputs. Hand-picked unit tests only cover the cases you thought of — PBT covers the ones you didn't.

**Decision rule:** Use PBT when you can express the invariant without a reference implementation. Skip it when the only way to write the property is `output === referenceImpl(input)` — that just tests your impl against itself.

**Illustrative examples:**

| Kind of module                   | Property                                                                                                    |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| State machine                    | Valid transitions never throw; invalid ones always throw a typed error with the correct fields              |
| Priority queue                   | Dequeue order is non-decreasing priority; size tracks exactly; idempotency keys work correctly              |
| Serialization (events/contracts) | Round-trip JSON serialize/parse preserves required fields; invalid fields are rejected                      |
| Secret/redacted value wrapper    | `toString()`/`toJSON()` always return a redacted placeholder regardless of value length or content          |
| Filesystem abstraction           | `exists()` and `stat()` agree; write ops on a read-only layer always throw; readdir includes all categories |

## Rules

1. **No code before test**: Ever
2. **CI must confirm the RED**: A test that doesn't fail in CI is not a real test
3. **CI must confirm the GREEN**: Local green is not enough — CI is the source of truth
4. **Minimum to pass**: Don't over-engineer the GREEN phase
5. **Refactor with safety**: Tests catch regressions
6. **One thing at a time**: One test, then one implementation
7. **Separate commits**: Test commit (RED) and implementation commit (GREEN) must be separate and reviewable

## Workflow Summary

```
Write test → commit → push PR → sleep 10m → poll 2m → CI fails? ✅
  → Write implementation → commit → push → sleep 10m → poll 2m → CI passes? ✅
    → Refactor → push → CI still green? ✅ → Done
```

## After GREEN: CI and Review Loop

After the GREEN phase is confirmed in CI, keep pushing and watching CI, fixing failures and addressing new review comments as they come in, until the PR is mergeable.

## Vertical, Not Horizontal

**DO NOT write all tests first, then all implementation.**

Tests and implementation must progress as vertical slices — one behavior at a time, end-to-end.

```
WRONG (horizontal): RED: test1,2,3,4,5 → GREEN: impl1,2,3,4,5
RIGHT (vertical):   RED→GREEN: test1→impl1, test2→impl2, ...
```

Each RED→GREEN cycle is a thin tracer bullet through the full stack for one behavior. This flushes out integration issues early instead of accumulating them.

## Frontend Test Hierarchy

For frontend/UI code, prefer this order:

1. **E2E test** (default) — test the whole system as the user sees it
2. **Unit test** — only for pure functions with no UI or side effects
3. **Component test** — avoid; use E2E instead

**Mock count heuristic:** If a test needs 3+ mocks, rewrite it as an E2E test. Complexity in mocking signals you're testing the wrong layer.

**E2E selectors (priority order):** accessible role > label > visible text > `data-testid`

## Test Design Philosophy

Tests verify **behavior through public interfaces**, not implementation details.

- **Good tests**: integration-style, exercise real code paths through public APIs, survive refactors
- **Bad tests**: coupled to implementation, mock internal collaborators, break on rename without behavior change

Before writing tests, look for **deep module** opportunities. If the codebase has many tiny, undifferentiated modules, the AI (and humans) can't navigate it. Restructuring into larger modules with thin interfaces on top makes test boundaries clear and tests more meaningful.

### What to Test

For each behavior:

- [ ] Test describes behavior, not implementation
- [ ] Test uses public interface only
- [ ] Test would survive internal refactor
- [ ] Code is minimal for this test
- [ ] No speculative features added

## Bug Fix Mode — Test-First Reproduction + Subagent Delegation

When fixing a **reported bug** (not building a new feature), the workflow changes:

### Step 1: Write Reproduction Test First

Do NOT attempt to fix the bug. Instead, translate the bug report into a failing test:

```
Bug report: "Users see a 500 when submitting an empty form"
→ Write: test('submitting empty form returns validation error, not 500', ...)
→ Watch it fail (confirms the bug is real and reproducible)
```

The reproduction test IS your root cause proof. If you can't write a test that fails, you don't understand the bug yet.

### Step 2: Delegate Fix to Subagent

Once the failing test exists, delegate the fix to a subagent with the test as the acceptance criterion:

```
goal: "Fix the bug reproduced by test 'submitting empty form returns validation error, not 500'
       in src/api/forms.regression.test.ts. The test currently fails. Make it pass with a minimal
       fix. Run: pnpm test:unit -- src/api/forms.regression.test.ts to verify."
```

The subagent doesn't need full bug context — the failing test encodes the exact expected behavior. A passing test is machine-verifiable proof the fix works.

### Why This Order

- **Test first** prevents "fix it and hope" — you have a reproducible signal before touching production code
- **Subagent delegation** works because the test is a self-contained acceptance gate — no ambiguity about "is it fixed?"
- **Parallel attempts** are possible — dispatch multiple subagents with different fix strategies against the same test, then keep whichever fix passes cleanly

## Regression Gate

When fixing a bug, always add a **named regression test** to a `*.regression.test.*` file alongside the module's test file. This creates permanent institutional memory of every bug the codebase has encountered.

### Convention

```
src/feature/feature.test.ts              ← normal feature tests
src/feature/feature.regression.test.ts   ← regression tests only
```

### Regression Test Format

Every regression test must include:

1. A descriptive name starting with `regression:` that explains the original bug
2. A comment linking to the issue/PR that introduced the fix

```typescript
/**
 * Regression: saga compensation skipped step 3 when step 2 threw synchronously
 * Fix: #187 — https://github.com/org/repo/pull/187
 */
test('regression: saga compensates all completed steps even on sync throw', () => {
  // Arrange: set up saga with 3 steps, step 2 throws synchronously
  // Act: run saga
  // Assert: compensation ran for step 1 (the only completed step)
})
```

### When to Write Regression Tests

- **Always** when fixing a bug discovered in production or CI
- **Always** when a review check flags a regression risk via git blame
- **Optionally** for bugs caught during code review before merge

### Why Separate Files

- Single place to see "every bug we've caught and must never regress"
- Easy to audit: `find . -name '*.regression.test.*'` shows the full regression surface
- Regression tests survive refactors — if a regression file has zero tests, the bugs were never real

## Common Rationalizations

| Rationalization                                                    | Rebuttal                                                                                                                                                                                 |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "I'll add tests after the implementation is working."              | That's prototype-then-test, not TDD. The test IS the spec — without it, you're coding against vibes. Write the test first; it takes 2 minutes.                                           |
| "This is too simple to need a test."                               | Simple code doesn't need a long test. `expect(add(1,2)).toBe(3)` takes 10 seconds. If it's too simple to test, it's too simple to get wrong — so the test is free insurance.             |
| "I need to explore the implementation first to know what to test." | Write the test for the behavior you want, not the implementation you'll build. If you don't know the desired behavior yet, you're not ready to code.                                     |
| "Writing the test first would slow me down."                       | TDD is slower for the first 10 minutes. But skipping it means debugging blind later. Net time is always lower with a failing test guiding you.                                           |
| "The CI verification step is too slow — I'll just check locally."  | Local green ≠ CI green. Environment differences, missing dependencies, and import ordering are invisible locally. The CI step exists because local-only TDD has a ~15% false-green rate. |
| "I'll write all the tests first, then implement them all."         | That's horizontal, not vertical. Each RED→GREEN cycle is one behavior — writing 5 failing tests creates 5 problems to solve simultaneously instead of 1.                                 |

## Anti-Patterns

See testing-anti-patterns.md for what to avoid:

- Testing implementation details
- Flaky tests
- Over-mocking
- Test duplication
- Assertion-free tests
- Tests that pass without implementation (vacuous green)

## Sources

- **Frontend Test Hierarchy** — [sergiodxa/agent-skills](https://github.com/sergiodxa/agent-skills) — Skill triage source for E2E-first testing strategy and mock-count heuristic
