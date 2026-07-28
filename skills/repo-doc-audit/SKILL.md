---
name: repo-doc-audit
description: Audit and refactor all documentation in a repo, then create/update AGENTS.md files per-directory with non-obvious context to help agents hit the ground running. Use when asked to audit docs, update documentation, refresh AGENTS.md, generate AGENTS.md files, do a doc sweep, or make a repo agent-ready.
interaction: autonomous
type: leaf
---

# Repo Doc Audit

Repo-wide documentation audit + AGENTS.md generation. Reads every markdown file, builds broad codebase understanding, refactors stale/unclear docs, and creates per-directory AGENTS.md files with non-obvious context that helps agents work effectively.

## Pre-flight Status

```
Dir: !`pwd`
Git root: !`git rev-parse --show-toplevel 2>/dev/null || echo '(not a git repo)'`
Markdown files: !`find . -name '*.md' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' -not -path '*/.understand-anything/*' | wc -l | tr -d ' '`
Existing AGENTS.md files: !`find . -name 'AGENTS.md' -not -path '*/node_modules/*' -not -path '*/.git/*' | wc -l | tr -d ' '`
Knowledge graph: !`ls .understand-anything/knowledge-graph.json 2>/dev/null && echo "✅ available" || echo "none"`
```

## When to Use

- Onboarding a new repo for agent work
- After a major refactor that invalidated docs
- Periodic documentation hygiene (monthly/quarterly)
- When agents are struggling with a repo and need better AGENTS.md guidance
- When asked to "make this repo agent-ready"

## Options

- `$ARGUMENTS` may contain:
  - `--scope <dir>` — Limit audit to a specific directory subtree
  - `--agents-only` — Skip doc refactoring, only create/update AGENTS.md files
  - `--docs-only` — Skip AGENTS.md generation, only audit/refactor existing markdown
  - `--dry-run` — Report findings without making changes

---

## Phase 1 — INVENTORY

Discover and catalog all documentation and code structure.

### 1a. Markdown Inventory

Find every markdown file in the repo:

```bash
find . -name '*.md' -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -not -path '*/dist/*' -not -path '*/vendor/*' -not -path '*/.understand-anything/*' \
  | sort
```

For each file, record:

- **Path** — relative to repo root
- **Size** — line count
- **Last modified** — `git log -1 --format=%ai -- <file>` (how stale is it?)
- **Last code change nearby** — `git log -1 --format=%ai -- <parent-dir>/*.{ts,js,py,rs,go}` (did code change after docs?)

### 1b. Codebase Structure Map

Build a lightweight understanding of the repo:

```bash
# Top-level structure
find . -maxdepth 2 -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | head -150

# Package manifests
find . -maxdepth 3 -name 'package.json' -o -name 'pyproject.toml' -o -name 'Cargo.toml' \
  -o -name 'go.mod' -o -name 'pom.xml' | head -20

# Entry points
find . -maxdepth 3 -name 'index.ts' -o -name 'main.ts' -o -name 'main.py' \
  -o -name 'main.go' -o -name 'main.rs' | head -20

# Config files (reveal conventions)
find . -maxdepth 2 -name '*.config.*' -o -name '.eslintrc*' -o -name 'tsconfig*' \
  -o -name 'Makefile' -o -name 'justfile' -o -name 'Dockerfile*' | head -20

# CI/CD (reveal quality gates)
find . -path '*/.github/workflows/*' -o -path '*/.gitlab-ci*' -o -path '*/Jenkinsfile' | head -10

# Test patterns
find . -name '*.test.*' -o -name '*.spec.*' -o -name '*_test.*' | head -10
```

Read the root README.md, any root AGENTS.md, and 2-3 key package manifests to understand the project.

### 1c. Existing AGENTS.md Audit

For each existing AGENTS.md file:

1. Read it fully
2. Cross-reference against current code — is the information still accurate?
3. Check for: outdated commands, wrong file paths, missing new modules, stale architecture descriptions
4. Rate: `current` | `stale` | `severely-outdated`

### 1d. Knowledge Graph (Optional Boost)

If `.understand-anything/knowledge-graph.json` exists, read it. Extract:

- Layer definitions (what architectural boundaries exist)
- Key node summaries (what each module does)
- Edge patterns (what depends on what)

This provides richer context for AGENTS.md generation. If no graph exists, proceed without it — the codebase structure map from 1b is sufficient.

**Gate check:** Present the inventory summary to the user:

```
📄 Found {N} markdown files across {M} directories
📋 {K} existing AGENTS.md files ({stale_count} stale)
🔍 Key directories needing AGENTS.md: {list}
⏰ Stalest docs: {top 5 by gap between doc edit and code edit}

Proceed with full audit? (Or adjust scope with --scope <dir>)
```

---

## Phase 2 — ANALYZE

Dispatch parallel subagents to analyze documentation quality. Batch by directory cluster.

### Clustering Strategy

Group markdown files into clusters of 5-15 files by proximity:

1. Files in the same directory → same cluster
2. Related directories (e.g., `apps/api-gateway/` and `packages/shared/`) → may share a cluster if small
3. Root-level files (README.md, CONTRIBUTING.md, CHANGELOG.md) → dedicated cluster

### Analysis Subagent Prompt

For each cluster, dispatch a Task subagent:

```
You are a documentation quality analyzer. Examine these markdown files and the code they document.

## Files to Analyze
{list of markdown files with paths and line counts}

## Codebase Context
{relevant directory structure, package manifests, entry points from Phase 1}

## For Each File, Assess:

1. **Accuracy**: Does the doc match current code? Check:
   - Code examples — do they use current APIs/function signatures?
   - File paths mentioned — do they still exist?
   - Commands — do they still work? (check package.json scripts, Makefile targets)
   - Architecture descriptions — do they match current module structure?

2. **Completeness**: What's missing?
   - New modules/features added after the doc was last updated
   - Setup steps that changed
   - Environment variables or config that's undocumented

3. **Clarity**: Would a new contributor (human or AI) understand this?
   - Jargon without explanation
   - Assumed context that isn't stated
   - Missing "why" — describes what but not why a pattern exists

4. **Duplication**: Is this info better covered elsewhere?
   - Redundant with another doc
   - Copy-pasted content that drifted out of sync

5. **Structure**: Is the doc well-organized?
   - Missing headers or sections
   - Wall-of-text without structure
   - Important info buried deep

## Output Format

For each file, produce:

- path: <file path>
  status: current | needs-update | needs-rewrite | should-delete
  staleness_signal: <last doc edit vs last code edit date>
  issues:
    - type: accuracy | completeness | clarity | duplication | structure
      severity: major | minor
      description: <specific issue>
      fix: <proposed fix — be specific>
  summary: <one-line assessment>
```

After all analysis subagents complete, merge results into a single findings list sorted by severity.

---

## Phase 3 — REFACTOR DOCS

Apply fixes to existing documentation. **Skip if `--agents-only` flag is set.**

### Triage

Present the analysis findings to the user, grouped by severity:

```
## Documentation Audit Results

### 🔴 Major Issues ({count})
{list — these will be fixed automatically}

### 🟡 Minor Issues ({count})
{list — these will be fixed automatically}

### ⚪ Suggestions ({count})
{list — optional, ask user}

### 🗑️ Candidates for Deletion ({count})
{list — duplicates or orphaned docs, ask user before deleting}
```

Wait for user confirmation before proceeding. The user may exclude specific files or issues.

### Execution Rules

1. **Make minimal edits** — fix what's wrong, don't rewrite for style
2. **Preserve voice** — match the existing doc's tone and conventions
3. **Update, don't invent** — if a section is stale, update it from code; don't add speculative content
4. **Verify code references** — before writing a code example, read the actual code to confirm the API
5. **Commit per-cluster** — group related doc fixes into logical commits

For each file needing updates:

1. Read the file fully
2. Read the code it references to verify current state
3. Apply the minimum edit needed
4. If the file needs heavy rewriting (>50% of content), present a before/after summary to the user first

---

## Phase 4 — GENERATE AGENTS.md

Create or update AGENTS.md files for directories that would benefit from agent guidance. **Skip if `--docs-only` flag is set.**

### Which Directories Get an AGENTS.md?

Not every directory needs one. Create AGENTS.md for directories where:

1. **Non-obvious conventions exist** — testing patterns, build quirks, import rules, naming conventions that differ from the rest of the repo
2. **Complex setup is required** — environment variables, database seeds, external service dependencies
3. **Common mistakes happen** — patterns an agent would get wrong without guidance
4. **The directory is a significant module** — apps, packages, services (not utility folders with 2 files)

**Skip AGENTS.md for:**

- Directories with <3 source files
- Generated/build output directories
- Directories whose conventions are identical to the parent's AGENTS.md
- `node_modules`, `dist`, `vendor`, `.git`, etc.

### Discovery: What's Non-Obvious?

For each candidate directory, the subagent must discover what an agent would NOT know from just reading the code:

1. **Read all source files** in the directory (or a representative sample for large dirs)
2. **Read the test files** — test patterns reveal conventions (mock factories, fixtures, test utilities)
3. **Read config files** — `tsconfig.json`, `.eslintrc`, `Dockerfile`, `Makefile` reveal build/lint/deploy quirks
4. **Read git history** — `git log --oneline -20 -- <dir>` reveals recent activity and conventions
5. **Check CI config** — does this directory have special CI steps?
6. **Check imports** — what packages does this directory depend on? Any unusual ones?
7. **Look for pitfalls** — environment variables, required setup, database migrations, external services

### AGENTS.md Template

````markdown
# {Directory Name} — Agent Instructions

{One-line description of what this directory contains and its role in the project.}

## Key Context

{2-3 sentences of the most important non-obvious information. What would cause an agent to fail or waste time without knowing this?}

## Structure

{Brief description of how files are organized in this directory. Only include if the structure is non-obvious.}

| Path     | Purpose |
| -------- | ------- |
| `src/`   | ...     |
| `tests/` | ...     |

## Conventions

{List specific conventions that differ from or extend the root-level conventions.}

- {Convention 1 — e.g., "All API handlers must use the `withAuth` middleware wrapper"}
- {Convention 2 — e.g., "Test files use shared mock factories from `@myorg/shared/test-utils`"}

## Common Commands

```bash
{Only commands specific to this directory — don't repeat root-level commands}
```
````

## Pitfalls

{Things an agent would likely get wrong without explicit guidance.}

- ⚠️ {Pitfall 1 — e.g., "Don't import from `../other-app/` directly — use the shared package"}
- ⚠️ {Pitfall 2 — e.g., "The database migration must run before integration tests"}

## Dependencies

{Non-obvious dependencies — external services, required env vars, sibling packages.}

```

### Content Rules

1. **Only include what's non-obvious.** If it's clear from reading the code, don't say it. AGENTS.md is for things you'd only learn by making mistakes or reading git history.
2. **Be specific, not generic.** "Follow best practices" is useless. "All Hono handlers must return `c.json()` not `new Response()`" is useful.
3. **Include real examples from the codebase.** Reference actual files: "See `src/middleware/auth.ts` for the auth pattern all handlers must follow."
4. **Keep it under 100 lines.** If it's longer, you're including obvious things. Cut ruthlessly.
5. **Commands must be runnable.** Every command in the file must work when pasted into a terminal in that directory.
6. **Don't duplicate the parent AGENTS.md.** If the root AGENTS.md covers it, don't repeat it.

### Generation Subagent Prompt

For each directory cluster, dispatch a Task subagent:

```

You are an AGENTS.md generator. Your job is to create guidance files that help AI coding agents work effectively in a directory they've never seen before.

## Directory: {path}

## Project Context: {root README summary, root AGENTS.md summary}

## Knowledge Graph Context: {layer info, node summaries for this dir — if available}

## Your Task

1. Read ALL source files in {path} (or top 20 by size if >30 files)
2. Read ALL test files in {path}
3. Read config files: tsconfig.json, .eslintrc\*, Dockerfile, Makefile, etc.
4. Run: git log --oneline -20 -- {path}
5. Check for existing AGENTS.md — if it exists, you're UPDATING not creating

## What to Write

Write an AGENTS.md that answers these questions:

- What would cause an agent to fail on its FIRST task in this directory?
- What conventions exist here that differ from standard {language} conventions?
- What commands must an agent run, and in what order?
- What imports/dependencies are non-obvious?
- What patterns do the existing tests follow that new tests must match?

## What NOT to Write

- Don't describe what the code does (that's what README is for)
- Don't list every file (agents can `ls` themselves)
- Don't repeat root-level AGENTS.md content
- Don't add generic advice ("write clean code", "follow DRY")
- Don't exceed 100 lines

## Output

Write the AGENTS.md content. Use the template structure provided.
If an AGENTS.md already exists and is mostly current, output only the specific edits needed (as edit_file-compatible old_str/new_str pairs).
If it needs a full rewrite or doesn't exist, output the complete file content.

````

---

## Phase 5 — VERIFY & COMMIT

### Pre-flight (Deterministic)

Run deterministic verification first:

!`bash skills/repo-doc-audit/scripts/verify-agents-md.sh 2>/dev/null || echo '(script not found)'`

This covers link checks and length checks. Focus manual review on:
- **Duplication check** — semantic comparison of parent/child AGENTS.md content
- **Command correctness** — whether commands produce the intended results (not just exist)

### Verification

1. **Link check** — **Automated:** Covered by `scripts/verify-agents-md.sh`. For every file path mentioned in any AGENTS.md, verify the file exists:
   ```bash
   grep -roh '`[^`]*\.\(ts\|js\|py\|rs\|go\|md\|json\|yaml\|toml\)`' */AGENTS.md | sort -u | while read f; do
     f_clean=$(echo "$f" | tr -d '`')
     [ ! -f "$f_clean" ] && echo "❌ Dead ref: $f_clean"
   done
````

2. **Command check** — for every command in a `bash` code block in AGENTS.md files, verify it references real scripts/binaries:

   ````bash
   # Extract first word of each command and check it exists
   grep -A1 '```bash' */AGENTS.md | grep -v '```' | awk '{print $1}' | sort -u
   ````

3. **Duplication check** — ensure no AGENTS.md repeats content from its parent AGENTS.md:
   - Read parent AGENTS.md
   - Compare key sections
   - Flag and remove duplicated content

4. **Length check** — **Automated:** Covered by `scripts/verify-agents-md.sh`. Flag any AGENTS.md over 100 lines (excluding the root one, which can be longer)

### Commit Strategy

Group changes into logical commits:

1. `docs: audit and update existing documentation` — all markdown fixes from Phase 3
2. `docs: create AGENTS.md files for {dirs}` — new AGENTS.md files from Phase 4
3. `docs: update existing AGENTS.md files` — updates to existing AGENTS.md files

### Summary Report

Present the final summary:

```
## 📋 Repo Doc Audit Complete

### Documentation Fixes
- {N} files updated (accuracy, completeness, clarity)
- {M} files unchanged (already current)
- {K} files flagged for manual review

### AGENTS.md Generation
- {A} new AGENTS.md files created: {list dirs}
- {B} existing AGENTS.md files updated: {list dirs}
- {C} directories skipped (too simple / conventions match parent)

### Verification
- ✅ All file references valid
- ✅ All commands reference real scripts
- ✅ No content duplication with parent AGENTS.md
- ⚠️ {any warnings}
```

---

## Error Handling

- If a subagent fails on a directory cluster, log the failure and continue with remaining clusters
- If a file can't be read (permissions, binary), skip it and note in the summary
- If git history is unavailable (not a git repo), skip staleness analysis — use file modification time instead
- Always produce partial results — a partial audit is better than no audit

## Integration with Existing Skills

| Skill                           | Relationship                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------- |
| `improve-codebase-architecture` | Complementary — that skill improves code structure; this skill improves doc structure |
