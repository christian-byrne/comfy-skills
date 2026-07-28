---
name: batch-local-checks
description: 'Run ALL local checks (tests, lint, format, typecheck, pre-commit hooks) with continue-on-error, writing every issue to a single file optimized for agent handoff. Auto-discovers checks from package.json, pyproject.toml, Cargo.toml, go.mod, Makefile, and custom scripts. Use when asked to run all checks, batch checks, collect all errors, pre-push validation, or local CI.'
interaction: autonomous
type: leaf
synergies:
  requires: []
  enhances: []
  conflicts: []
  domain: [quality, ci, automation]
---

# Batch Local Checks

Run every available local check in a repo with continue-on-error semantics. Instead of stopping at the first failure, collects ALL issues into a single `issues.txt` optimized for handing to a fresh agent session (especially on a cheaper model).

## When to Use

- Before pushing — run everything locally instead of waiting for CI
- After implementation — collect all issues in one pass before ending the session
- Session break pattern — run batch checks, end session, hand `issues.txt` + compaction to a cheaper model
- "Run all checks" / "local CI" / "what's broken?"

## Quick Start

Paths below are relative to this skill's own directory — adjust for wherever it's installed.

```bash
# Run all discovered checks in current repo
scripts/batch-checks.sh

# Run against a specific repo
scripts/batch-checks.sh /path/to/repo

# Dry run — see what checks would run
scripts/batch-checks.sh --discover

# Custom output directory
scripts/batch-checks.sh /path/to/repo /tmp/my-checks
```

## What It Discovers

The script auto-discovers checks from multiple sources, in order:

| Source                        | Checks Found                                          | Examples                       |
| ----------------------------- | ----------------------------------------------------- | ------------------------------ |
| `package.json` scripts        | format, lint, typecheck, test, stylelint, knip, build | `pnpm lint`, `npm test`        |
| `pyproject.toml` / `setup.py` | ruff, mypy, pytest                                    | `ruff check .`, `pytest`       |
| `Cargo.toml`                  | check, clippy, test, fmt                              | `cargo clippy`, `cargo test`   |
| `go.mod`                      | vet, test, golangci-lint, gofmt                       | `go test ./...`                |
| `Makefile` targets            | lint, check, test, format, typecheck                  | `make lint`                    |
| Pre-commit hooks              | husky, lefthook, pre-commit                           | `.husky/pre-commit`            |
| `.batch-checks.d/`            | custom executable scripts                             | `./check-migrations.sh`        |
| `BATCH_CHECKS_EXTRA` env      | ad-hoc semicolon-separated commands                   | `"shellcheck *.sh;vale docs/"` |

Package manager auto-detected: pnpm > yarn > npm > bun (based on lockfile).

## Output Structure

All output written to `/tmp/batch-local-checks/` (configurable):

| File          | Purpose                                                                                           | When to Read                                     |
| ------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `issues.txt`  | **Primary handoff artifact.** Unified issue list with `file:line — [category] description` format | Always — this is what you hand to the next agent |
| `summary.txt` | One-line pass/fail per check with duration                                                        | Quick status overview                            |
| `issues.json` | Machine-readable array of structured issues                                                       | Programmatic consumption                         |
| `<check>.log` | Full raw output per check                                                                         | Only for failed checks, deep debugging           |

## Extensibility

### Custom Checks (`.batch-checks.d/`)

Drop executable scripts into `REPO_DIR/.batch-checks.d/`:

```bash
mkdir -p .batch-checks.d
cat > .batch-checks.d/check-migrations.sh << 'EOF'
#!/bin/bash
# Verify all migrations are applied
pnpm db:migrate:status | grep -q "pending" && echo "Pending migrations found" && exit 1
exit 0
EOF
chmod +x .batch-checks.d/check-migrations.sh
```

### Ad-Hoc Extra Checks

```bash
BATCH_CHECKS_EXTRA="shellcheck scripts/*.sh;vale docs/" batch-checks.sh
```

## Session Break Pattern

The primary use case — token-optimized local validation that avoids cold-cache polling, noisy output, and expensive models on cheap fixes.

### The Flow

**Step 1 — Finish implementation, commit**

Normal workflow. Ensure all changes are committed.

**Step 2 — Generate resume prompt**

Write `/tmp/batch-local-checks/resume-prompt.md` with context for the next session:

```markdown
# Resume: Fix batch check issues

## Context

Branch: {branch name}
Repo: {absolute repo path}
Implemented: {1-3 sentence summary of what was built}

## What to do

1. Read /tmp/batch-local-checks/issues.txt
2. Fix every issue listed
3. Run: scripts/batch-checks.sh {repo path}
4. If clean, rebase/push and monitor CI as usual

## Key files touched

- {list of files modified in this session}

## Checks running

Started: {timestamp}
Script: batch-checks.sh in tmux session "batch-checks"
Monitor: tmux attach -t batch-checks
```

**Step 3 — Kick off checks in tmux background**

```bash
REPO_DIR="$(git rev-parse --show-toplevel)"
tmux new-session -d -s batch-checks \
  "scripts/batch-checks.sh '$REPO_DIR' /tmp/batch-local-checks; \
   echo ''; echo '## Checks complete' >> /tmp/batch-local-checks/resume-prompt.md; \
   echo 'Finished: $(date)' >> /tmp/batch-local-checks/resume-prompt.md; \
   echo 'Issues: $(wc -l < /tmp/batch-local-checks/issues.txt) lines' >> /tmp/batch-local-checks/resume-prompt.md"
```

**Step 4 — Print instructions to human and end session**

Print this exact message (fill in the ETA):

```
✅ Implementation complete. Checks running in background.

⏱  ETA: ~{N} minutes (around {HH:MM} {timezone})
📋 Monitor: tmux attach -t batch-checks

When ready, start a new session and say:

  "Read /tmp/batch-local-checks/resume-prompt.md and do what it says"
```

Then let the session end. Zero idle token cost.

**Step 5 — Human starts new session (any time, any model)**

Human says: `Read /tmp/batch-local-checks/resume-prompt.md and do what it says`

**Step 6 — New agent picks up and fixes**

The new agent:

1. Reads `resume-prompt.md` for branch/repo/context
2. Reads `issues.txt` for the structured issue list
3. Fixes all issues
4. Re-runs `batch-checks.sh` to verify clean
5. If clean → proceeds to push and monitor CI

### ETA Estimation

Estimate check duration based on what was discovered:

| Checks present                 | Typical ETA |
| ------------------------------ | ----------- |
| Lint + format + typecheck only | ~1-2 min    |
| Above + unit tests             | ~3-5 min    |
| Above + build step             | ~5-8 min    |
| Above + e2e tests              | ~10-15 min  |

Use `--discover` to see what will run and estimate accordingly.

### Why This Works

- **No cold cache** — session ends immediately, no idle time burning tokens
- **No noisy output** — all issues collected once, structured in `file:line — [category]` format
- **Model flexibility** — fix session can use a cheaper model; lint nits, type errors, and format fixes are structured work that doesn't need frontier reasoning
- **Human-paced** — human picks up when convenient, not when CI finishes
- **Self-contained context** — `resume-prompt.md` has everything the next agent needs

## Integration with a push/CI flow

This skill complements but does not replace your normal push-and-monitor-CI flow. Use batch-local-checks _before_ pushing to catch everything locally first.

```
Implementation complete
    ↓
batch-local-checks (session break: background checks + resume-prompt.md)
    ↓
[session ends — human resumes when ready]
    ↓
New session reads resume-prompt.md → fixes issues
    ↓
Re-run batch-local-checks (verify clean)
    ↓
Push and monitor CI (rebase, push, poll CI for env-specific issues only)
```

## Exit Codes

- `0` — All checks passed
- `N` — Number of failed checks (1-254)
- `255` — Setup error (no repo, no checks discovered)
