---
name: test-mock-quality-analysis
description: Analyze unit test quality by mapping mocked vs real code boundaries. Produces ASCII diagrams showing fake world vs reality, identifies over-mocking, and compares against repo test patterns. Use when reviewing test PRs, assessing test confidence, or deciding whether tests need more integration-style coverage.
type: leaf
interaction: autonomous
synergies:
  enhances: []
  domain: [testing, quality, code-review]
---

# Test Mock Quality Analysis

Analyzes test files to determine what's _actually_ being tested vs what's mocked away. Line coverage % is misleading when most dependencies are stubbed.

## When to Use

- Reviewing PRs that add test coverage
- Assessing whether tests provide real confidence
- Deciding if integration tests are needed
- Understanding test quality beyond coverage %

## Core Insight

A test with 90% line coverage but heavy mocking may only test orchestration logic, not actual behavior. This skill maps the boundary between fake and real to reveal true test confidence.

## Process

### Phase 1: Extract Mock Inventory

Scan the test file for all mocking:

```typescript
// Top-level vi.mock() calls
vi.mock('@/scripts/app', () => ({ ... }))

// Inline mocks
vi.fn(), vi.spyOn(), jest.fn()

// Mock factories
createMock*(), __mocks__/
```

For each mock, note:

- Module being mocked
- What behavior is stubbed (returns fixed value, no-op, simplified logic)
- Whether it's a total mock or partial

### Phase 2: Identify Real Code Paths

Look for:

- Imports NOT preceded by `vi.mock()`
- Real class instantiation (`new ClassName()`)
- Comments like "NOT mocked" (intentional)
- Actual function calls that exercise real logic

### Phase 3: Map the Boundary

Create a two-column inventory:

| Mocked (Fake World)        | Real (Actually Tested)         |
| -------------------------- | ------------------------------ |
| `app.registerExtension`    | `PrimitiveNode` class methods  |
| `ComfyWidgets.*` factories | `getWidgetConfig()` resolution |
| `graph.getNodeById()`      | Connection validation logic    |

### Phase 4: Generate ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      MOCKED / FAKE WORLD                        │
├─────────────────────────────────────────────────────────────────┤
│  @/scripts/app              @/services/api                      │
│  ┌───────────────────┐      ┌───────────────────┐               │
│  │ registerExtension │      │ fetchData → {}    │               │
│  │ canvas.graph_mouse│      │ postData → void   │               │
│  └───────────────────┘      └───────────────────┘               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    REAL CODE BEING TESTED                       │
├─────────────────────────────────────────────────────────────────┤
│  MyClass (ALL methods)                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ✅ constructor - initialization logic                   │    │
│  │ ✅ processData - transformation pipeline                │    │
│  │ ✅ validate - input validation                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  Exported Functions                                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ✅ parseConfig - config parsing                         │    │
│  │ ✅ mergeOptions - option merging                        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 5: Compare Against Repo Patterns

Search for existing test patterns:

```bash
# Find integration tests
find . -name "*.integration.test.ts"

# Find test utilities
ls src/utils/__tests__/*Utils.ts

# Find fixture patterns
find . -path "*__fixtures__*" -name "*.ts"

# Check for real instance factories
grep -r "new LGraph\|new.*Node\|createTest" --include="*.test.ts"
```

Identify if the repo uses:

- Real instances via factories (`createTestSubgraph()`)
- Fixture-based graphs loaded from JSON
- Vitest `.extend<>()` for layered fixtures
- Partial mocking (mock some, real others)

### Phase 6: Generate Quality Assessment

| Aspect                 | Status   | Notes                       |
| ---------------------- | -------- | --------------------------- |
| **Branching Logic**    | ✅/⚠️/❌ | Are conditionals exercised? |
| **State Mutations**    | ✅/⚠️/❌ | Are state changes real?     |
| **Integration Points** | ✅/⚠️/❌ | Real or mocked?             |
| **Error Paths**        | ✅/⚠️/❌ | Are failures tested?        |

### Phase 7: Recommendations

Based on findings, suggest:

1. **Worth doing** - high-value changes to reduce mocking
2. **Not worth it** - mocks that are appropriate (DOM, network, etc.)
3. **Existing patterns** - repo utilities that could replace custom mocks

## Output Format

When posting to PR comments, use:

```markdown
## 🔍 Test Coverage Analysis

### 🎭 Mocked World vs Reality

[ASCII diagram]

### 📊 Coverage Quality Assessment

[Table]

### 💡 Improvement Opportunities

[Recommendations]
```

## Anti-patterns

- ❌ Treating all mocking as bad (some is necessary)
- ❌ Recommending integration tests for pure functions
- ❌ Ignoring repo's existing test patterns
- ❌ Suggesting changes that require massive refactoring

## Examples

### Good Mock (Keep It)

```typescript
// Canvas 2D context - DOM dependency, appropriate to mock
vi.mock('canvas', () => ({
  getContext: () => createMockCanvasRenderingContext2D(),
}))
```

### Bad Mock (Consider Removing)

```typescript
// Graph traversal mocked when real LGraph is available
node.graph = { getNodeById: vi.fn(() => targetNode) }

// Better: Use real graph
const graph = new LGraph()
graph.add(targetNode)
node.graph = graph
```

## Related Practices

- **Finding untested modules** is a complementary check — this skill only analyzes tests that already exist.
- **Broader test quality review** — this skill's mock/reality mapping is one input into a fuller test-quality pass; combine it with coverage numbers and manual read-through for a complete picture.
- **General PR review** — fold this analysis in as one section of a larger review when the PR under review adds or changes tests.
