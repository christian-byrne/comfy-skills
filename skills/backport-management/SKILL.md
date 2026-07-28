---
name: backport-management
description: Manages cherry-pick backports across stable release branches. Discovers candidates from Slack/git, analyzes dependencies, resolves conflicts via worktree, and logs results. Use when asked to backport, cherry-pick to stable, manage release branches, do stable branch maintenance, or run a backport session.
interaction: hybrid
type: leaf
---

# Backport Management

Cherry-pick backport management for stable release branches.

## Quick Start

1. **Discover** — Collect candidates from Slack bot + git log gap
2. **Analyze** — Categorize MUST/SHOULD/SKIP, check deps
3. **Plan** — Order by dependency (leaf fixes first), group into waves per branch
4. **Execute** — Label-driven automation → worktree fallback for conflicts
5. **Log** — Generate session report

## System Context

| Item           | Value                                         |
| -------------- | --------------------------------------------- |
| Repo           | `{OWNER}/{REPO}`                              |
| Merge strategy | Squash merge (`gh pr merge --squash --admin`) |
| Automation     | Label-driven GitHub Action (if available)     |
| Tracking dir   | `~/temp/backport-session/`                    |

## ⚠️ Gotchas

### Automation Over-Reports Conflicts

Backport automation often reports more conflicts than reality. `git cherry-pick -m 1` with git auto-merge handles many cases the automation can't. Always attempt manual cherry-pick before skipping.

### Never Skip Based on Conflict File Count

12 or 27 conflicting files can be trivial (snapshots, new files). **Categorize conflicts first**, then decide. See Conflict Triage below.

## Conflict Triage

**Always categorize before deciding to skip. High conflict count ≠ hard conflicts.**

| Type                         | Symptom                              | Resolution                                                      |
| ---------------------------- | ------------------------------------ | --------------------------------------------------------------- |
| **Binary snapshots (PNGs)**  | `.png` files in conflict list        | `git checkout --theirs $FILE && git add $FILE` — always trivial |
| **Modify/delete (new file)** | PR introduces files not on target    | `git add $FILE` — keep the new file                             |
| **Modify/delete (removed)**  | Target removed files the PR modifies | `git rm $FILE` — file no longer relevant                        |
| **Content conflicts**        | Marker-based (`<<<<<<<`)             | Accept theirs via regex (see below)                             |
| **Add/add**                  | Both sides added same file           | Accept theirs, verify no logic conflict                         |
| **Locale/JSON files**        | i18n key additions                   | Accept theirs, validate JSON after                              |

```python
# Accept theirs for content conflicts
import re
pattern = r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> [^\n]+\n'
content = re.sub(pattern, r'\2', content, flags=re.DOTALL)
```

### Escalation Triggers (Flag for Human)

- **Package.json/lockfile changes** → skip on stable (transitive dep regression risk)
- **Core type definition changes** → requires human judgment
- **Business logic conflicts** (not just imports/exports) → requires domain knowledge

## Auto-Skip Categories

Skip these without discussion:

- **Dep refresh PRs** — Risk of transitive dep regressions on stable. Cherry-pick individual CVE fixes instead.
- **CI/tooling changes** — Not user-facing
- **Test-only / lint rule changes** — Not user-facing
- **Revert pairs** — If PR A reverted by PR B, skip both. If fixed version (PR C) exists, backport only C.
- **Features not on target branch** — Features that don't exist on the target branch

## Quick Reference

### Label-Driven Automation (default path)

```bash
gh api repos/{OWNER}/{REPO}/issues/$PR/labels \
  -f "labels[]=needs-backport" -f "labels[]=TARGET_BRANCH"
# Wait 3 min, check: gh pr list --base TARGET_BRANCH --state open
```

### Manual Worktree Cherry-Pick (conflict fallback)

```bash
git worktree add /tmp/backport-$BRANCH origin/$BRANCH
cd /tmp/backport-$BRANCH
git checkout -b backport-$PR-to-$BRANCH origin/$BRANCH
git cherry-pick -m 1 $MERGE_SHA
# Resolve conflicts, push, create PR, merge
```

### PR Title Convention

```
[backport TARGET_BRANCH] Original Title (#ORIGINAL_PR)
```
