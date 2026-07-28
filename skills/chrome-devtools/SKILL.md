---
name: chrome-devtools
description: Expert browser automation, debugging, and performance analysis via Chrome DevTools Protocol MCP. Use when automating browser interactions, inspecting console/network, profiling performance, or troubleshooting Claude in Chrome MCP extension connectivity.
type: leaf
synergies:
  domain: [browser, debugging, performance, automation]
---

# chrome-devtools

Expert browser automation and debugging via the Chrome DevTools Protocol (CDP) MCP server.

## Prerequisites

MCP server must be configured. If `mcp__chrome-devtools__*` tools are unavailable, STOP — the chrome-devtools MCP server isn't configured.

Ask the user to add this to their MCP config:

```json
"chrome-devtools": {
  "type": "local",
  "command": ["npx", "-y", "chrome-devtools-mcp@latest"]
}
```

## Tool Categories

### Navigation & Page Management

- `new_page`, `navigate_page`, `select_page`, `list_pages`, `close_page`, `wait_for`

### Input & Interaction

- `click`, `fill` / `fill_form`, `hover`, `press_key`, `drag`, `handle_dialog`, `upload_file`

### Debugging & Inspection

- `take_snapshot`, `take_screenshot`, `list_console_messages`, `evaluate_script`, `list_network_requests`

### Emulation & Performance

- `resize_page`, `emulate`, `performance_start_trace`, `performance_stop_trace`, `performance_analyze_insight`

## Key Workflows

**Element targeting** — always `take_snapshot` first to get element UIDs; take a fresh snapshot after DOM changes.

**Debugging errors** — combine `list_console_messages` + `list_network_requests` to correlate JS errors with failed requests.

**Performance profiling** — `performance_start_trace` → trigger action → `performance_stop_trace` → `performance_analyze_insight` for Core Web Vitals bottlenecks.

**Visual verification** — `take_screenshot` after interactions to confirm state.

## Claude in Chrome MCP — Troubleshooting

Use this section when `mcp__claude-in-chrome__*` tools fail with "Browser extension is not connected" or behave erratically. **macOS only** — these paths don't apply on Linux/Windows.

### Root Cause: Competing Native Messaging Hosts

Claude.app (Cowork) and Claude Code CLI both register native messaging configs in Chrome, using incompatible socket formats:

| Component           | Binary                                                          | Socket                                                  |
| ------------------- | --------------------------------------------------------------- | ------------------------------------------------------- |
| Claude.app (Cowork) | `/Applications/Claude.app/Contents/Helpers/chrome-native-host`  | `/tmp/claude-mcp-browser-bridge-$USER/<PID>.sock`       |
| Claude Code CLI     | `~/.local/share/claude/versions/<version> --chrome-native-host` | `$TMPDIR/claude-mcp-browser-bridge-$USER` (single file) |

If the wrong config is active, Chrome routes extension requests to the wrong binary → connection fails even though processes appear running.

### Fix: Disable Claude.app's Native Host (Claude Code users)

```bash
mv ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json \
   ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json.disabled
```

Restart Chrome and Claude Code after.

### Toggle Function (switch between tools)

Add to `~/.zshrc` (or your shell's equivalent rc file) for easy switching:

```bash
chrome-mcp-toggle() {
  local CONFIG_DIR=~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts
  local CLAUDE_APP="$CONFIG_DIR/com.anthropic.claude_browser_extension.json"
  local CLAUDE_CODE="$CONFIG_DIR/com.anthropic.claude_code_browser_extension.json"

  if [[ -f "$CLAUDE_APP" && ! -f "$CLAUDE_APP.disabled" ]]; then
    mv "$CLAUDE_APP" "$CLAUDE_APP.disabled"
    [[ -f "$CLAUDE_CODE.disabled" ]] && mv "$CLAUDE_CODE.disabled" "$CLAUDE_CODE"
    echo "Switched to Claude Code CLI — restart Chrome and Claude Code"
  elif [[ -f "$CLAUDE_CODE" && ! -f "$CLAUDE_CODE.disabled" ]]; then
    mv "$CLAUDE_CODE" "$CLAUDE_CODE.disabled"
    [[ -f "$CLAUDE_APP.disabled" ]] && mv "$CLAUDE_APP.disabled" "$CLAUDE_APP"
    echo "Switched to Claude.app (Cowork) — restart Chrome"
  else
    echo "State unclear. Check:" && ls -la "$CONFIG_DIR"/com.anthropic*.json* 2>/dev/null
  fi
}
```

**Cannot use both simultaneously** — pick one and disable the other.

### Other Connectivity Issues

- **Multiple Chrome profiles** — extension may be active in the wrong profile; check which profile hosts it
- **Stale version wrapper** — hardcoded version paths go stale after updates; re-check `~/.local/share/claude/versions/`
- **Socket not found** — `TMPDIR` unset? Run `echo $TMPDIR`; if empty, set it explicitly
- **Multiple Claude Code sessions** — concurrent sessions can conflict on the same socket; close extras
- **MCP connects at startup** — if the browser bridge wasn't ready when Claude Code started, restart Claude Code after Chrome/extension is stable

### Diagnostics

```bash
# Check both native hosts are registered
ls ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/ | grep anthropic

# Check running native host processes
ps aux | grep -E "chrome-native-host|claude.*chrome"

# Verify socket exists
ls -la $TMPDIR/claude-mcp-browser-bridge-$USER 2>/dev/null || echo "socket missing"

# Check socket connections
lsof -U | grep claude-mcp-browser-bridge
```

## Sources

- [chrome-devtools](https://skills.sh/github/awesome-copilot/chrome-devtools) (github-awesome-copilot) — CDP MCP tool reference and workflow patterns
- [claude-in-chrome-troubleshooting](https://skills.sh/trailofbits/skills/claude-in-chrome-troubleshooting) (trailofbits-skills) — Claude extension native host conflict diagnosis and fixes
