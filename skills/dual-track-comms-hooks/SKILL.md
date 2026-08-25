---
name: dual-track-comms-hooks
description: 'One-time setup of the dual-track comms enforcement hooks for Claude Code: two advisory PreToolUse hooks that check GitHub, Linear, Slack, and Notion posts against the dual-track format (terse top level plus native collapsible or thread) before they go out. Bundles the hook scripts, telemetry lib, and tests, and walks through installation, settings.json registration, and verification. Use when asked to install, set up, upgrade, or troubleshoot the dual comms hooks.'
interaction: interactive
type: leaf
disable-model-invocation: true
synergies:
  enhances: [dual-track-comms]
  domain: [communication, hooks, setup]
---

# Dual-Track Comms Hooks — Setup

Installs mechanical enforcement of the dual-track format (see the `dual-track-comms`
skill for the format itself). Once registered, every outbound post is checked before it
leaves the machine — no skill needs to be loaded, no agent needs to remember anything.

Both hooks are **advisory**: they deny with corrective guidance so the agent rewrites
the post, but they never crash the session. Genuine exceptions pass with an override
token, and every trigger is logged.

## What Gets Installed

| Script                          | Hook event / matcher                                                        | Covers                                                                                       |
| ------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `dual-comms-external-posts.sh`  | PreToolUse, matcher `Bash`                                                  | `gh pr comment`, `gh issue comment`, `gh pr review`, Linear `commentCreate` curls, Slack `chat.postMessage` curls |
| `dual-comms-notion-posts.sh`    | PreToolUse, matcher for MCP Notion comment/patch tools                       | Notion comments and appended blocks                                                          |
| `lib-jsonl-append.sh`           | (helper, not a hook)                                                        | Telemetry JSONL appends — both hooks source it from their own directory                       |

Allowed without prompting:

- Bodies already terse: ≤400 chars AND ≤6 lines (Linear payloads get 600 chars for
  GraphQL boilerplate)
- Bodies containing a `<details>` block or Linear `+++` collapsible
- Slack payloads with `thread_ts` (a threaded reply IS the full-context track)
- Bare `gh pr review --approve` / `--request-changes` with no body
- Unreadable bodies (`--body-file -`, `-d @file`) — allowed but logged

Overrides: append `# comms:exempt` to a shell command, or include `comms:exempt` in a
Notion body. Overrides are logged, not blocked.

## Install

1. Copy all three scripts from this skill's `scripts/` directory to one stable location
   (e.g. `~/.claude/hooks/`) and `chmod +x` them. They must stay in the same directory —
   the hooks source `lib-jsonl-append.sh` relative to their own resolved path (symlinks
   are followed).
2. Register in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "/path/to/dual-comms-external-posts.sh" }]
      },
      {
        "matcher": "mcp__notion__API_create_a_comment|mcp__notion__API_patch_block_children",
        "hooks": [{ "type": "command", "command": "/path/to/dual-comms-notion-posts.sh" }]
      }
    ]
  }
}
```

3. Optionally set `HOOKS_LOG_DIR` for telemetry (defaults to `$HOME/logs`). Rows land in
   `dual-comms-external-posts.jsonl` / `dual-comms-notion-posts.jsonl` with
   allowed/denied/overridden outcomes.

## Verify

Run the bundled tests directly — they exercise allow, deny, and override paths without
posting anything:

```bash
bash scripts/dual-comms-external-posts.test.sh
bash scripts/dual-comms-notion-posts.test.sh
```

Then confirm live behavior: start a Claude Code session and try a long
`gh issue comment` body without a `<details>` block — the hook should deny with
guidance; add the collapsible and it passes.

## Uninstall

Remove the two PreToolUse entries from `settings.json`. The scripts and telemetry logs
are inert without registration.
