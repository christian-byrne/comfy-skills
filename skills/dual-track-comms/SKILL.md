---
name: dual-track-comms
description: 'Write every message in two tracks: an ultra-terse top level (≤3 takeaways) plus the full context in the platform-native collapsible or threaded mechanism. Encodes the validated per-platform mechanics for Slack, Notion, GitHub, Linear, Figma, email, and docs. Use when posting a PR/issue comment, Slack update, Notion comment, Linear comment, email, or any message longer than a few lines that humans will skim and agents will mine for detail.'
interaction: autonomous
type: leaf
synergies:
  enhances: [stakeholder-comms, internal-comms, project-status-generator, dual-track-comms-hooks]
  domain: [communication, reporting, program-management]
---

# Dual-Track Comms

Every message has two readers: a human who skims and an agent (or future you) who needs
everything. One message serves both when it is written in two tracks:

1. **Top level — ultra-terse.** At most 3 takeaways. Fragments fine. Cut anything that
   wouldn't change what the reader decides ("56/56 tests passing" → "green").
2. **Full context — platform-native disclosure.** Everything else goes in the platform's
   collapsible, thread, or linked-page mechanism so it's available but not in the way.

The top level is not a summary of the detail — it is the decision-relevant subset. If the
reader acts only on the top level, nothing should go wrong.

## Budgets

| Rule            | Value                                                 |
| --------------- | ----------------------------------------------------- |
| Takeaways       | ≤3                                                    |
| Top-level size  | ≤400 chars AND ≤6 lines                               |
| Linear payloads | 600 chars (GraphQL mutation boilerplate allowed)      |
| Override token  | `# comms:exempt` (commands) / `comms:exempt` (bodies) |

These budgets are enforced by the hooks `packages/hooks/scripts/dual-comms-external-posts.sh`
(GitHub, Linear, Slack) and `dual-comms-notion-posts.sh` (Notion comments). This skill is the
knowledge half; the hooks are the enforcement half. A body that already contains the platform's
collapse mechanism passes regardless of length.

## Per-Platform Mechanics (validated)

| Platform                      | Full-context mechanism                                                                | Notes                                                                                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub                        | `<details><summary>Title</summary>\n\n…\n\n</details>`                                | Blank lines around inner markdown or it renders literally. Works in PR/issue comments, reviews, README.                                      |
| Linear                        | `+++ Section title` … content … `+++`                                                 | Official API markdown syntax. Editor also: `>>>` or `/collapsible`. HTML `<details>` NOT supported — strict inline HTML allowlist strips it. |
| Slack                         | Terse top-level message; full context as a **threaded reply** (`thread_ts`)           | No collapse mechanism exists. A threaded reply IS the full-context track — the hook allows any length there.                                 |
| Notion                        | Comments: terse + link to a page block or child page. Page content: toggle blocks     | Comments have no collapse. In page content, lead each section with the terse takeaway and put evidence/detail in a `toggle` block (API: block type `toggle` with `children`; toggle headings also work). |
| Figma                         | Comments are plain text only — terse + link to full context elsewhere (Notion/GitHub) | No markdown, no collapse, no threads with formatting. Never put the detail in a Figma comment.                                               |
| Email                         | TL;DR ≤3 bullets at top, divider (`---` / `<hr>`), full context below — or link out   | `<details>` is NOT supported in Gmail/Outlook/most clients (caniemail: stripped or rendered inert). Don't use it.                            |
| Docs (Notion/Confluence/wiki) | Lead with the takeaway paragraph; push depth into toggles/child pages                 | Progressive disclosure, same principle at document scale.                                                                                    |

## Writing the Top Level

- Lead with the outcome or decision, not the activity ("merged, deploys tonight" not "I worked on…")
- Numbers only when they change a decision; otherwise compress ("green", "done", "blocked on X")
- Name the single action you need from the reader, if any
- No greetings, no hedging, no restating the question

## Writing the Full Context

- The full context is the message you would normally have sent — don't strip it, relocate it
- Include evidence agents need: exact commands, links, IDs, error text, file paths
- Title the collapsible for its reader: "Full context for agent readers", "Repro details", "Rollout evidence"

## Cross-Posting One Message to Multiple Platforms

Don't hand-convert. `@charlie-labs/format-for` (npm) parses one markdown input and renders
GitHub/Slack/Linear dialects, converting `+++` ↔ `<details>` and degrading safely on Slack
(collapsible → bold header + quote). For Figma/email, apply the table above manually.

## Enforcement Hooks (optional)

Mechanical enforcement exists as a separate one-time-setup skill:
`dual-track-comms-hooks` (tools.comfy.org/t/dual-track-comms-hooks). It installs two
advisory Claude Code PreToolUse hooks that check GitHub, Linear, Slack, and Notion posts
against this format before they go out. Once installed, this skill does not need to be
loaded for the format to be enforced.

## When NOT to Use

- The whole message fits the budget — send it plain
- Threaded replies (Slack `thread_ts` present) — they ARE the full-context track
- Notion page content and other documents are exempt from the message budgets, but not
  from the structure: lead each section with the takeaway and push evidence into toggle
  blocks or child pages
- Genuinely exempt posts — append the override token, which is logged

## Example (GitHub PR comment)

```markdown
Green. Root cause: stale cache key after rename. Fix + regression test in this PR.

<details><summary>Full context for agent readers</summary>

- Failing job: `test.yml` → `vitest packages/foo` (run 8123456)
- Root cause: `cacheKey` still hashed the old path after #4102 renamed `src/foo` → `src/bar`
- Fix: derive key from `pkg.name` (single source of truth) — `src/cache.ts:41`
- Regression test: `src/cache.test.ts` "invalidates on package rename"
- Verified: `pnpm test --filter foo` 34/34, lint/typecheck clean

</details>
```
