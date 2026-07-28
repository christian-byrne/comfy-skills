---
name: skill-from-trial-run
description: 'Builds a new skill through ideation, trial run, and iterative refinement. Five-phase loop: ideate features/tools → build SKILL.md → human runs trial in separate thread → review thread for failures/friction → iterate and PR. Use when building a skill from scratch, iterating on a new skill, refining a skill after a trial run, or asked to build a skill via trial run.'
---

# Skill from Trial Run

Build production-quality skills through a structured ideation → build → trial → review → iterate loop. Every skill gets battle-tested before merging.

## Workflow Overview

```
Phase 1: IDEATE     → Brainstorm features, tools, concepts, and augmentations
Phase 2: BUILD      → Create SKILL.md + reference files
Phase 3: TRIAL      → Human runs the skill in a separate agent thread
Phase 4: REVIEW     → Read trial thread, extract failures and friction
Phase 5: ITERATE    → Fix skill, run quality passes, PR + final sweep
```

## Phase 1: Ideate

When the user describes a skill idea:

1. **Validate the concept** — Does this overlap with existing skills? Check the repo's `skills/` directory and any personal `~/.claude/skills/` for conflicts. If overlap exists, suggest augmenting the existing skill instead.

2. **Suggest a three-layer feature set:**
   - **Core workflow** — The minimum viable skill (what phases, what steps)
   - **Tool ecosystem** — Static analysis tools, CLIs, APIs, linters that could be integrated
   - **Augmentations** — Advanced features, integrations, optional passes

3. **Present related resources** — Blog posts, concepts, prior art, similar tools, related skills in the repo. Be exhaustive — the user will curate.

4. **Get user feedback** — Let the user approve/deny/modify each suggestion. Don't build until the scope is agreed.

### Ideation Checklist

- [ ] Checked for overlapping skills
- [ ] Proposed core workflow
- [ ] Listed all applicable tools (language-aware)
- [ ] Suggested augmentations
- [ ] Listed related resources
- [ ] User approved scope

## Phase 2: Build

Create the skill following standard skill-authoring conventions:

1. **Create directory** — `skills/<skill-name>/` (in the repo `skills/` directory, not `~/.claude/skills/`)
2. **Write SKILL.md** — Under 500 lines, with:
   - Valid frontmatter (name, description with "Use when..." triggers)
   - Clear phase-based workflow
   - Tool commands with fallback/troubleshooting guidance
   - Anti-patterns section
   - Explicit output format expectations
3. **Write reference files** — `reference/` for:
   - Tool setup and troubleshooting (progressively disclosed)
   - Templates, checklists, or detailed specs
4. **Run quality checks:**

```bash
# If skill-lint exists in the repo
bash scripts/skill-lint.sh skills/<skill-name>/SKILL.md

# Manual checks
wc -l skills/<skill-name>/SKILL.md  # Must be <500
```

### Build Quality Bar

Before handing off for trial, verify:

- [ ] Frontmatter `name` matches directory name
- [ ] Description includes "Use when..." with 3+ trigger phrases
- [ ] All referenced files in `reference/` or `scripts/` exist
- [ ] No hardcoded absolute paths
- [ ] Tool commands include failure handling ("if X fails, try Y")
- [ ] Monorepo-aware where applicable (install flags, per-workspace fallbacks)
- [ ] Clear output format for every phase

## Phase 3: Trial

Tell the user to run the skill in a separate agent thread. Provide the exact invocation:

```
Run the <skill-name> skill on this repo.
```

**Important:** The trial MUST happen in a separate thread/agent so you get a clean signal on:

- What the agent struggled with (no prior context from this conversation)
- What instructions were ambiguous
- What tools failed and how the agent recovered
- What the final output quality looks like

Tell the user: "Run this in a separate agent, then paste me the thread ID or URL and I'll review it."

## Phase 4: Review Trial Thread

When the user provides the trial thread ID/URL:

1. **Read the thread:**

   ```
   read_thread(threadID="T-...", goal="Extract every problem encountered: tool failures, missing instructions, ambiguity, improvisation, ordering issues, output quality issues. Also extract the actual outputs to evaluate quality.")
   ```

2. **Classify issues found:**

| Category                  | What to Look For                               | Fix Target                |
| ------------------------- | ---------------------------------------------- | ------------------------- |
| **Tool failure**          | Tool crashed, wrong flags, missing deps        | `reference/tool-setup.md` |
| **Ambiguous instruction** | Agent had to improvise or guess                | `SKILL.md` workflow       |
| **Missing fallback**      | Agent hit a wall with no recovery path         | Add fallback/workaround   |
| **Monorepo issue**        | Install flags, workspace scoping               | Phase 0 detection         |
| **API limitation**        | gh CLI, external API missing features          | Update commands           |
| **Output quality**        | Findings too vague, wrong format, bad grouping | Templates/examples        |
| **Prompt construction**   | Subagent prompts unclear, inconsistent         | Add prompt templates      |
| **Ordering issue**        | Steps ran in wrong order, deps not met         | Reorder workflow          |

3. **Dispatch quality subagents** — Run these in parallel:

**Subagent A: Skill Quality Review**
Run `skill-lint` (if available) and audit the SKILL.md for frontmatter, discovery, structure, and examples.

**Subagent B: Agent-Facing Prompt Review**
Evaluate the skill's instructions as a prompt surface for an agent:

- Is the skill's prompt surface well-designed for agent consumption?
- Are there known anti-patterns in how instructions are structured (ambiguous steps, missing fallbacks, unclear triggers)?
- Are there iteration loop patterns that should be built into the skill?

**Subagent C: Skill Lint**
If the `skill-lint` script exists, run it:

```bash
bash scripts/skill-lint.sh skills/<skill-name>/SKILL.md
```

4. **Compile improvement plan** — Merge trial thread issues + subagent reviews into a prioritized list.

## Phase 5: Iterate

Apply fixes from the improvement plan:

1. **Fix critical issues first** — Tool failures, missing fallbacks, ambiguous instructions
2. **Then high-severity** — Output quality, prompt construction, ordering
3. **Then polish** — Structure, examples, progressive disclosure

After fixes:

1. **Run skill-lint** (if available)
2. **Verify line count** — SKILL.md must stay under 500 lines
3. **Verify all cross-references** — Every file mentioned in SKILL.md exists
4. **Create PR** — Commit with `feat: add <skill-name> skill`
5. **Run final-sweep** if the skill is available

### Iteration Criteria

The skill is ready to merge when:

- [ ] Trial thread issues are all addressed
- [ ] skill-lint passes (if available)
- [ ] SKILL.md < 500 lines
- [ ] All cross-references resolve
- [ ] No hardcoded paths
- [ ] Monorepo fallbacks tested
- [ ] Description has clear triggers

## When to Use This Skill

- Building any new skill from scratch
- "Build a skill for X"
- "Create a new skill via trial run"
- "I have an idea for a skill"
- "Let's iterate on this skill"
- User provides a trial thread for review

## Anti-Patterns

- ❌ **Skipping the trial** — Every skill MUST be trial-run before merging. A skill that hasn't been tested by a naive agent is untested.
- ❌ **Reviewing your own output** — The trial must run in a SEPARATE thread with no context from the build conversation. Same-thread testing gives false confidence.
- ❌ **Fixing everything at once** — Fix critical issues first, then re-trial if needed. Don't try to perfect the skill in one pass.
- ❌ **Ignoring tool failures** — If a tool failed in the trial, add explicit fallback instructions. Don't assume it was a one-off.
- ❌ **Building skills in `~/.claude/skills/`** — Pipeline skills go in repo `skills/`. Only personal utilities go in global skills.
