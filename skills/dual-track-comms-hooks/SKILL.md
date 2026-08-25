---
name: dual-track-comms-hooks
description: 'One-time onboarding that sets up mechanical enforcement of the dual-track comms format (terse top level plus native collapsible or thread) on outbound GitHub, Linear, Slack, and Notion posts. Discovers the user''s agent harness and posting tools, then installs the right enforcement mechanism for that setup: Claude Code PreToolUse hooks (reference scripts bundled), Amp plugins, or the closest equivalent. Use when asked to install, set up, upgrade, or troubleshoot the dual comms hooks.'
interaction: interactive
type: leaf
disable-model-invocation: true
synergies:
  enhances: [dual-track-comms]
  domain: [communication, hooks, setup, onboarding]
---

# Dual-Track Comms Hooks — Adaptive Setup

Sets up mechanical enforcement of the dual-track format (see `dual-track-comms` for the
format itself) so every outbound post is checked before it leaves the machine — no skill
loaded, nothing for the agent to remember.

There is no uniform hook standard across harnesses, and people post to these platforms
with different tools (gh CLI vs GitHub MCP, curl vs Slack CLI, Linear MCP vs GraphQL
curl). So this skill is NOT "copy these scripts and register them." It is: **discover
what this user actually has, then install equivalent enforcement for that setup.** The
bundled scripts are the reference implementation for one common setup (Claude Code +
Bash tool + Notion MCP); adapt from them, don't assume them.

## Step 1 — Discover the environment

Before installing anything, establish three facts. Do not skip this; a hook registered
against a tool the user never posts with enforces nothing.

**1a. Which harness(es)?** Check for config dirs and running tools:

| Evidence                                   | Harness    | Interception mechanism                          |
| ------------------------------------------ | ---------- | ----------------------------------------------- |
| `~/.claude/settings.json`, `claude` on PATH | Claude Code | `hooks.PreToolUse` in settings.json             |
| `~/.config/amp/`, `amp` on PATH             | Amp        | Plugin (tool-call interception); no shell hooks |
| `~/.codex/`, `codex` on PATH                | Codex      | Config/notify hooks are limited — see fallback  |
| `~/.config/opencode/`, `opencode` on PATH   | OpenCode   | Plugin API (`tool.execute.before`)              |
| Other / none                                | —          | Fallback: guidance-only (see below)             |

If the user runs multiple harnesses, install for each one they actually post from. Ask
which they use daily rather than installing everywhere speculatively.

**1b. Which posting tools?** The enforcement must trigger on what the user actually
uses. Discover, don't assume:

- Grep shell history and repo scripts for `gh pr comment`, `gh issue comment`,
  `chat.postMessage`, `api.linear.app`, `api.notion.com`.
- List configured MCP servers (harness config) — Notion, Slack, Linear, GitHub MCPs
  each expose their own tool names that a matcher must target.
- Check PATH for dedicated CLIs (`slack`, `linear`, `notion`) or wrappers in `~/bin`.

**1c. Which platforms matter?** If the user never posts to Linear, do not police
Linear. Also ask about comms tools not on the default list (Discord, email CLIs,
Mattermost) — the check contract below ports to any of them.

## Step 2 — Map posting paths to trigger points

For each (platform, tool) pair from discovery, pick the trigger:

- Shell CLI or curl → intercept the shell/Bash tool call and pattern-match the command
  (this is what `dual-comms-external-posts.sh` does).
- MCP tool → intercept that specific MCP tool name (this is what
  `dual-comms-notion-posts.sh` does for the stock Notion MCP's comment-creation tool; a Slack or
  Linear MCP needs its own matcher with the same logic).
- No interception available in the harness → fallback: add a short standing instruction
  to the harness's global guidance file (AGENTS.md / CLAUDE.md equivalent) pointing at
  the `dual-track-comms` skill, and say clearly to the user that this is advisory
  guidance, not mechanical enforcement.

## Step 3 — Port the check contract (the invariant part)

Whatever the mechanism, the check itself is fixed. Preserve all of it:

- **Advisory, never fatal.** Deny with corrective guidance so the agent rewrites the
  post; never crash the session; fail open on unparseable input (but log it).
- **Terse passes.** ≤400 chars AND ≤6 lines is allowed as-is (600 chars for Linear
  GraphQL payloads, which carry boilerplate).
- **Full-context mechanism passes.** GitHub `<details>` block, Linear `+++` collapsible,
  Slack `thread_ts` (a threaded reply IS the full-context track). Notion comments have
  no collapsible: terse comment + link to a page/block holding the context.
- **Override token.** `comms:exempt` in the body or command allows but logs; genuine
  exceptions must have an escape hatch or people disable the hook entirely.
- **Telemetry.** Log every trigger (allowed/denied/overridden) as JSONL. Reference lib:
  `lib-jsonl-append.sh`, dir from `HOOKS_LOG_DIR` (default `$HOME/logs`).
- **Documents are not messages.** Do not police page-content writes (Notion page
  blocks, wiki edits); long-form is legitimate there. Police comments and messages.

## Reference implementation: Claude Code

The bundled scripts implement the contract for Claude Code. If discovery lands here:

1. Copy all three scripts from `scripts/` to a stable location (e.g. `~/.claude/hooks/`)
   and `chmod +x`. Keep them in one directory — the hooks source `lib-jsonl-append.sh`
   relative to their own resolved path (symlinks followed).
2. Register in `~/.claude/settings.json`, adjusting matchers to the MCP tool names found
   in discovery:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "/path/to/dual-comms-external-posts.sh" }]
      },
      {
        "matcher": "mcp__<your-notion-server>__API_create_a_comment",
        "hooks": [{ "type": "command", "command": "/path/to/dual-comms-notion-posts.sh" }]
      }
    ]
  }
}
```

3. Optionally set `HOOKS_LOG_DIR` for telemetry.

For other harnesses, port the same logic: the scripts are short bash with a documented
stdin/stdout protocol in their headers — read them, then re-express the contract in the
harness's plugin API. Name the artifact whatever the harness calls it (plugin, hook,
middleware); the contract is what matters.

## Verify

- Claude Code path: run the bundled tests — they exercise allow, deny, and override
  without posting anything:

```bash
bash scripts/dual-comms-external-posts.test.sh
bash scripts/dual-comms-notion-posts.test.sh
```

- Any path: live dry-run. Attempt a long post body without a collapsible against a
  target nobody watches (draft issue, private channel) — expect a deny with guidance;
  add the collapsible — expect a pass. Confirm a telemetry row appeared for each.
- Show the user what was installed, where, and how to uninstall it, before ending the
  session.

## Uninstall

Remove the registration (settings entries, plugin, or guidance-file paragraph). The
scripts and telemetry logs are inert without registration.
