---
name: changelog-generator
description: Creates user-facing changelogs from git commits. Analyzes commit history, categorizes changes, transforms technical commits into customer-friendly release notes.
interaction: autonomous
type: leaf
---

# Changelog Generator

Transform technical git commits into polished, user-friendly changelogs.

## When to Use

- Preparing release notes
- Creating weekly/monthly update summaries
- Documenting changes for customers
- Writing changelog entries for app stores

## What It Does

1. **Scans Git History**: Analyzes commits from time period or between versions
2. **Categorizes Changes**: Features, improvements, bug fixes, breaking changes
3. **Translates**: Converts developer commits to customer language
4. **Formats**: Creates clean, structured entries
5. **Filters Noise**: Excludes internal commits (refactoring, tests)
6. **Anti-slop check**: Customer-facing changelogs must not read as AI-generated. Cut throat-clearing, business jargon ("leverages", "streamlines"), vague declaratives, and emphasis crutches. State what changed, for whom, concretely. Full ruleset: `avoid-ai-writing` skill.

## Usage

```
Create a changelog from commits since last release
```

```
Generate changelog for commits from the past week
```

```
Create release notes for version 2.5.0
```

## Example Output

```markdown
# Updates - Week of March 10, 2024

## ✨ New Features

- **Team Workspaces**: Create separate workspaces for different projects

## 🔧 Improvements

- **Faster Sync**: Files now sync 2x faster

## 🐛 Fixes

- Fixed issue where large images wouldn't upload
```
