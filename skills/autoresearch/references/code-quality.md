# Code Quality Optimization

Reduce lint warnings, improve test coverage, lower cyclomatic complexity, or shrink bundle size. Any static analysis metric that can be extracted as a number.

## Typical Metrics

| Metric Name     | Unit      | Direction | Extraction Example                                          |
| --------------- | --------- | --------- | ----------------------------------------------------------- |
| `lint_warnings` | count     | ↓ lower   | `eslint . 2>&1 \| grep "problems" \| awk '{print $2}'`      |
| `coverage_pct`  | percent   | ↑ higher  | `vitest --coverage \| grep "All files" \| awk '{print $4}'` |
| `complexity`    | score     | ↓ lower   | complexity analysis tool output                             |
| `bundle_kb`     | kilobytes | ↓ lower   | `du -sb dist/ \| awk '{print int($1/1024)}'`                |
| `type_errors`   | count     | ↓ lower   | `tsc --noEmit 2>&1 \| grep "error TS" \| wc -l`             |

## Benchmark Script Patterns

### Lint Warnings

```bash
#!/bin/bash
count=$(eslint . --format compact 2>&1 | grep -c "Warning\|Error" || true)
echo "METRIC lint_warnings=$count"
```

### Test Coverage

```bash
#!/bin/bash
pnpm test -- --coverage --reporter=json > coverage.json 2>&1
pct=$(jq '.total.lines.pct' coverage.json)
echo "METRIC coverage_pct=$pct"
```

### Bundle Size

```bash
#!/bin/bash
pnpm build > /dev/null 2>&1
size=$(du -sb dist/ | awk '{print int($1/1024)}')
echo "METRIC bundle_kb=$size"
```

## Optimization Patterns by Metric

### Reducing Lint Warnings

1. Fix auto-fixable warnings first (`eslint --fix`)
2. Replace deprecated APIs
3. Add missing type annotations
4. Fix unused imports/variables
5. **Do NOT** disable rules to reduce warnings — that's cheating

### Improving Coverage

1. Add tests for uncovered branches (if/else, switch, error paths)
2. Add tests for edge cases (empty input, null, boundary values)
3. Cover error handling paths
4. **Do NOT** delete uncovered code unless it's truly dead
5. **Do NOT** add trivial tests that cover lines but test nothing

### Reducing Bundle Size

1. Tree-shake unused exports
2. Replace heavy dependencies with lighter alternatives
3. Lazy-load non-critical modules
4. Remove unused CSS/assets
5. Optimize images and fonts

### Reducing Complexity

1. Extract complex conditions into named functions
2. Replace nested if/else with early returns
3. Break large functions into smaller focused ones
4. Replace switch statements with lookup tables

## Guard

The guard depends on the metric:

- **Lint warnings:** tests must still pass (`pnpm test`)
- **Coverage:** lint must still pass (`pnpm lint`)
- **Bundle size:** app must still work (`pnpm build && pnpm test:e2e`)
- **Complexity:** tests must still pass

**Never optimize one metric at the expense of another.** The guard prevents this.

## Scope Guidance

- For lint: scope to the directories with the most warnings (run `eslint . --format compact | sort` to find hot spots)
- For coverage: scope to files with lowest coverage (check coverage report)
- For bundle: scope to the build config and the largest source modules
- For complexity: scope to files flagged by complexity tools
