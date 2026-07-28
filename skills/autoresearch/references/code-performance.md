# Code Performance Optimization

Optimize runtime speed, reduce allocations, shrink latency. Based on Tobi Lutke's Liquid optimization (53% faster, 61% fewer allocations from ~120 automated experiments).

## Typical Metrics

| Metric Name      | Unit         | Direction | Extraction Example                                |
| ---------------- | ------------ | --------- | ------------------------------------------------- |
| `total_µs`       | microseconds | ↓ lower   | `grep "total_µs" run.log \| awk -F= '{print $2}'` |
| `parse_time_ms`  | milliseconds | ↓ lower   | benchmark script output                           |
| `allocations`    | count        | ↓ lower   | profiler output                                   |
| `p95_latency_ms` | milliseconds | ↓ lower   | load test output                                  |
| `rps`            | requests/sec | ↑ higher  | load test output                                  |

## Benchmark Script Pattern

Create an `autoresearch.sh` in the project that:

1. Runs the guard (tests) first — fail fast
2. Runs the benchmark 3 times
3. Reports the **median** of the 3 runs as `METRIC name=value`

```bash
#!/bin/bash
set -e

# Guard: tests must pass
<TEST_COMMAND> > /dev/null 2>&1

# Benchmark: 3 runs, take median
results=()
for i in 1 2 3; do
  result=$(<BENCHMARK_COMMAND> 2>&1 | grep "<METRIC_PATTERN>" | awk '{print $NF}')
  results+=("$result")
done

# Sort and take median
sorted=($(printf '%s\n' "${results[@]}" | sort -n))
median=${sorted[1]}
echo "METRIC total_µs=$median"
```

## High-Impact Optimization Patterns

Ordered by typical impact (try these first):

1. **Allocation reduction** — freeze strings, reuse objects, pool buffers, cache computed values. GC pressure is often the #1 bottleneck.
2. **Replace regex with byte scanning** — in hot loops, manual byte-level parsing is 2-5x faster than regex.
3. **Fast-path common cases** — if 90% of inputs are simple, add a fast path that skips the general parser.
4. **Eliminate method dispatch** — inline hot methods, avoid `respond_to?` / `instanceof` in tight loops.
5. **Lazy initialization** — defer expensive setup until first use.
6. **Batch I/O** — combine multiple small reads/writes into one.

## What Typically Doesn't Work

From the Liquid PR's "What did NOT work" section:

- Shared caches across templates (leak state, grow unbounded)
- Subclassing for fast paths (polymorphism hurts JIT optimization)
- `while` loops replacing `each` for long arrays (JIT optimizes `each` better)
- `String#scan` with capture groups (+5K allocations from MatchData)

## Scope Guidance

- **Start narrow:** one hot module or one hot function
- **Expand gradually:** after exhausting one module, profile again to find the next bottleneck
- **Never touch test files** — they're the guard
- **Never touch the benchmark script** — it's the metric source

## Guard Command Examples

```bash
# Ruby
bundle exec rake test

# Node.js
pnpm test

# Rust
cargo test

# Python
pytest
```
