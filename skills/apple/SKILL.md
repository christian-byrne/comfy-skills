---
name: apple
description: 'Router for Apple/macOS ecosystem skills — iMessage, Reminders, Notes. Only works on macOS. Use when asked about Apple services, sending messages, managing reminders, or working with Apple Notes.'
interaction: hybrid
type: router
---

# Apple Ecosystem Router

macOS-only skills for interacting with Apple services via CLI tools. All require macOS and specific Homebrew packages.

## Skill Graph

| Task                                            | Action                                                                        |
| ----------------------------------------------- | ----------------------------------------------------------------------------- |
| Send/receive iMessages or SMS                   | Read `subskills/imessage.md` in this directory and follow its workflow        |
| Manage Apple Reminders (create, complete, list) | Read `subskills/apple-reminders.md` in this directory and follow its workflow |
| Read, search, or create Apple Notes             | Read `subskills/apple-notes.md` in this directory and follow its workflow     |

## Read-Based Loading

When the `skill` tool is not available for sub-skills, use the `Read` tool to load them directly:

| Sub-Skill         | Path                                        |
| ----------------- | ------------------------------------------- |
| `imessage`        | `skills/apple/subskills/imessage.md`        |
| `apple-reminders` | `skills/apple/subskills/apple-reminders.md` |
| `apple-notes`     | `skills/apple/subskills/apple-notes.md`     |

## Prerequisites

All sub-skills require macOS. Check with:

```bash
[[ "$(uname)" == "Darwin" ]] && echo "✅ macOS" || echo "❌ Not macOS — these skills won't work"
```

## Context Management

- Carry forward only outputs and decisions — not sub-skill instructions.

## How This Graph Grows

As you discover new Apple-ecosystem patterns worth capturing:

1. **New sub-skill** → create in this directory and add to the dispatch table above
2. **New reference** → add to `reference/` and document in Reference Files table
3. **Cross-cutting pattern** → update the decision tree or create a new reference file
