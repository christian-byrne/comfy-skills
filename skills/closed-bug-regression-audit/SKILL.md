---
name: closed-bug-regression-audit
description: Audit closed bug issues on a repo for missing regression tests using a 3-pass parallel-subagent strategy (keyword, adversarial, fix-PR-diff, systemic-pattern). Files gap issues with the `quality:missing-regression-test` label. Use when asked to find regression test gaps, audit closed bugs for test coverage, find bugs that could regress, or run a regression-gap sweep.
type: orchestrator
interaction: autonomous
synergies:
  enhances: [issue-triage, audit-code, test-driven-development]
  domain: [testing, quality, regression, bug-audit]
---

# Closed-Bug Regression Audit

A repeatable workflow for finding regression-test gaps for previously-fixed bugs. Catches three classes of gap that single-pass keyword search misses:

1. **Missing tests** — bug fixed but no test added
2. **Inadequate tests** — test exists but tests the wrong thing / mock-echoes / weak assertions / FABRICATED (file doesn't exist on disk)
3. **Systemic gaps** — multiple bugs share a missing class-level guard (CI job, lint, smoke test)

## When to Use

- "Find regression gaps for closed bugs"
- "Audit our bug history for missing tests"
- "What could regress?"
- Any periodic test-quality sweep

## Prerequisites

- `gh` CLI authenticated against the target repo
- `rg` (ripgrep)
- A workspace checkout of the target repo
- The `quality:missing-regression-test` label exists on the repo (create if missing — see step 0)

## Process

### Step 0 — Ensure the standard label exists

```bash
gh label create "quality:missing-regression-test" \
  --repo <owner/repo> \
  --description "A previously-fixed bug that lacks a regression test to prevent recurrence" \
  --color "D73A4A" 2>/dev/null || true
```

Follows the repo label taxonomy (`{category}:{subcategory}` — see root AGENTS.md).

### Step 1 — Enumerate closed bugs

```bash
gh issue list --repo <owner/repo> --state closed --label bug --limit 200 \
  --json number,title,closedAt,body,labels,url > /tmp/closed-bugs.json
jq -r '.[] | "\(.number)\t\(.closedAt[0:10])\t\(.title)"' /tmp/closed-bugs.json
```

### Step 2 — Pass 1: keyword + relevance (parallel subagents)

Split bugs into batches of ~5. Dispatch one subagent per batch IN PARALLEL (single message, multiple `Task` tool uses). Each subagent:

1. `gh issue view <num>` for full body + comments
2. Identify the fix PR
3. **Relevance check** — is the affected code still in the repo? (Read/Grep) If removed/rewritten → mark NOT RELEVANT
4. **Test search** — `rg` for keywords from bug title in `*.test.*`, `*.spec.*`, `e2e/`, `tests/`, `__tests__/`
5. If RELEVANT and no test → file issue (template below)

Return a markdown table: `Bug# | Relevant? | Has Test? | Action`

### Step 3 — Pass 2: adversarial + fix-PR-diff + systemic (parallel, different roles)

Dispatch THREE subagents in parallel with DIFFERENT roles:

**Role A — Adversarial test reviewer.** For every bug pass 1 marked "covered", read the test file AND the production code. Verify:

- Test exercises the actual failure mode (not adjacent behavior)
- Test would FAIL if the bug were re-introduced (mentally re-introduce it)
- Assertions are specific (value/state) not weak ("no error thrown")
- Not mock-echo (testing the mock instead of the real code)
- **The test file actually exists on disk** — pass-1 subagents sometimes hallucinate test files. Always `ls`/`Read` the path.

**Role B — Fix-PR-diff coverage.** For each closed bug, find the fix PR, list prod files it changed (exclude `*.test.*`, `*.md`), then `rg` for test files that import/reference those exact files. If a fix PR changed prod code with zero test references → gap.

**Role C — Systemic pattern finder.** Look across ALL bugs for shared missing class-level guards. Examples: "no smoke test for fresh-machine setup", "no lint for YAML frontmatter", "no CI job validates JSONL parseability". File ONE issue per pattern, listing all bugs it would have caught.

### Step 4 — File gap issues

All three roles file issues using the same label set:

```bash
gh issue create --repo <owner/repo> \
  --title "test: <action> for #<bug> (<short>)" \
  --label "bug,tech-debt,quality:missing-regression-test" \
  --body "$(cat <<'EOF'
## Missing Regression Test

Original bug: #<num> — <title>
Fix PR: #<pr>

## Why this gap matters
<1–2 sentences on what could silently regress>

## Suggested test
- **Layer**: unit | integration | e2e
- **File**: <suggested path>
- **Asserts**: <what to assert — be specific>

## Affected code
<paths still in repo>

Auto-filed by closed-bug regression audit.
EOF
)"
```

For systemic-pattern issues, also add `enhancement` label and title with `(would have caught #X, #Y, ...)`.

### Step 5 — Backfill label on any pre-existing gap issues

If you filed issues before standardising the label, backfill:

```bash
for n in <issue numbers>; do
  gh issue edit $n --repo <owner/repo> --add-label "quality:missing-regression-test"
done
```

## Anti-Patterns to Watch For (from real audit)

| Anti-pattern             | Example                                                              | How to catch                                                                     |
| ------------------------ | -------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Fabricated test**      | Pass-1 says "covered by `foo.test.sh`" but file doesn't exist        | Always `ls`/`Read` the path in adversarial pass                                  |
| **String-grep test**     | `grep -q "syncpull" startup.sh` passes if the call is in a comment   | Adversarial: would test pass with bug re-introduced as commented code?           |
| **Wrong-thing test**     | Test checks adjacent timer; original bug was about a different timer | Adversarial: re-read the bug repro and trace exact failure path                  |
| **Premature close**      | Issue closed but production fix never landed                         | Pass-2 Role B catches: fix PR exists but prod files unchanged or PR never merged |
| **Coverage by category** | One bug in a class is fixed; class-level guard missing               | Pass-3 Role C systemic finder                                                    |

## Output Template

After all passes, produce a final summary:

```markdown
## Regression Gap Audit — <repo>

Audited <N> closed bugs across 4 strategies (keyword, adversarial, fix-PR-diff, systemic).

| Bug# | Relevant? | Has Test? | Verdict | Issue |
| ---- | --------- | --------- | ------- | ----- |
| ...  |           |           |         |       |

**<X> gap issues filed** (label `quality:missing-regression-test`):

- #<...> per-bug missing tests
- #<...> inadequate/fabricated tests
- #<...> systemic class-level guards

**Notable findings**:

- <e.g. 3 of 7 "covered" claims were fabricated test files>
- <e.g. bug #X has actually regressed in current main>
```

## Tips

- **Do all dispatches in parallel.** 3 batches × pass 1, then 3 roles × pass 2 = 6 subagents total, ~2 sequential rounds.
- **Trust nothing from pass 1.** Pass 2 adversarial routinely invalidates 30–50% of "covered" claims.
- **Don't dedupe across passes upfront** — let pass 2 see the full list, instruct it to skip already-filed issue numbers in the prompt.
- **Cap output per subagent** — request a summary table only, not narrative.
- **Apply standard label even if `gh issue create` accepts it inline** — passes often forget; backfill loop in Step 5 is cheap insurance.
