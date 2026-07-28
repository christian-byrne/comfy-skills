# Test Speed Optimization

Reduce test suite execution time without sacrificing coverage or correctness.

## Typical Metrics

| Metric Name       | Unit         | Direction | Extraction Example                   |
| ----------------- | ------------ | --------- | ------------------------------------ |
| `seconds`         | seconds      | ↓ lower   | `time pnpm test 2>&1 \| grep real`   |
| `test_duration_s` | seconds      | ↓ lower   | vitest/jest JSON reporter            |
| `slowest_test_ms` | milliseconds | ↓ lower   | `--reporter=verbose --sort=duration` |

## Benchmark Script Pattern

```bash
#!/bin/bash
set -e

# Run tests with timing, 3 times, take median
results=()
for i in 1 2 3; do
  start=$(date +%s%3N)
  <TEST_COMMAND> > /dev/null 2>&1
  end=$(date +%s%3N)
  elapsed=$(( (end - start) ))
  results+=("$elapsed")
done

sorted=($(printf '%s\n' "${results[@]}" | sort -n))
median=${sorted[1]}
echo "METRIC test_duration_ms=$median"
```

## High-Impact Optimization Patterns

1. **Parallelize** — ensure vitest/jest workers are configured optimally. Check `pool`, `poolOptions`, `maxWorkers`.
2. **Reduce setup overhead** — shared DB connections, cached fixtures, lazy module imports.
3. **Mock heavy I/O** — replace real network/filesystem calls with mocks in unit tests.
4. **Shorten timeouts** — find tests with artificially long `setTimeout` or retry delays.
5. **Split slow integration tests** — move to a separate test suite that doesn't block the fast loop.
6. **Optimize imports** — barrel file re-exports can cause massive module graph loading. Replace `import { x } from '@package'` with direct imports.
7. **Vitest-specific:** `--no-file-parallelism` can be faster for small suites. `pool: 'threads'` vs `'forks'` — threads are faster but forks are more isolated.

## Scope Guidance

- `vitest.config.ts` / `jest.config.ts` — configuration is often the biggest lever
- `test/setup.ts` / `setupFiles` — global setup runs before every file
- The test files themselves — reduce redundant setup, combine small related tests
- Source files with heavy imports that tests load transitively

## Guard

The guard IS the test suite — tests must still pass. The verify command measures how long they take. If an optimization makes tests fail, it's automatically discarded.

```bash
# Verify: measure time
time pnpm test 2>&1 | grep real

# Guard: tests pass (same command, just check exit code)
pnpm test
```

**Shortcut:** For test speed, verify and guard are often the same command. The verify extracts timing; if it exits non-zero, that's also a guard failure.

## Anti-Patterns

- Don't skip tests to make the suite faster
- Don't reduce assertion depth
- Don't remove `beforeEach` cleanup (causes flaky tests)
- Don't share mutable state between test files to save setup time
