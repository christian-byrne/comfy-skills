#!/bin/bash
set -euo pipefail

# dual-comms-notion-posts — Enforces the dual-communication format on Notion
# comments posted via the Notion MCP tool. Notion comments have no collapsible
# mechanism, so dual-comms on Notion means: keep the comment ultra-terse (<=3
# takeaways) and put the full context in a page block / child page, linking it
# from the comment.
#
# Scope note: this hook deliberately covers ONLY comment creation
# (mcp__notion__API_create_a_comment). Page-content writes
# (API_patch_block_children etc.) are documents, not messages — long-form is
# legitimate there and is NOT policed.
#
# Protocol: PreToolUse (matcher: mcp__notion__API_create_a_comment)
#   stdin:  JSON { tool_name, tool_input: { rich_text: [ { text: { content } } ] }, session_id }
#   stdout: deny JSON or empty
#   exit 0: always (advisory hook — never crashes the agent)
#
# Allowed without prompt:
#   - short bodies (already terse: <=400 chars AND <=6 lines)
#   - body containing the override token 'comms:exempt'
#   - unparseable input (fail-open, logged)
#
# Telemetry: appends JSONL row to $HOOKS_LOG_DIR/dual-comms-notion-posts.jsonl
#            on every trigger (allowed/denied/overridden).

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "Hook: enforces dual-comms format (terse comment + full context in a linked page)"
  echo "      on Notion comments posted via mcp__notion__API_create_a_comment"
  echo "Event: PreToolUse (matcher: mcp__notion__API_create_a_comment)"
  echo "Override: include 'comms:exempt' anywhere in the comment text"
  exit 0
fi

# Resolve symlinks to find the actual script directory (hooks are often symlinked from ~/bin)
SCRIPT_PATH="${BASH_SOURCE[0]}"
[[ -L "$SCRIPT_PATH" ]] && SCRIPT_PATH=$(readlink -f "$SCRIPT_PATH")
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
# shellcheck source=lib-jsonl-append.sh
source "$SCRIPT_DIR/lib-jsonl-append.sh"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | { jq -r '.tool_name // ""' || true; })
SESSION_ID=$(echo "$INPUT" | { jq -r '.session_id // ""' || true; })

LOG_DIR="${HOOKS_LOG_DIR:-${AMP_LOG_DIR:-$HOME/logs}}"
LOG_FILE="$LOG_DIR/dual-comms-notion-posts.jsonl"

emit_telemetry() {
  local outcome="$1" detail="$2"
  local ts
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  local row
  row=$(jq -cn \
    --arg ts "$ts" \
    --arg session "$SESSION_ID" \
    --arg outcome "$outcome" \
    --arg tool "$TOOL_NAME" \
    --arg detail "$detail" \
    '{ts:$ts, session_id:$session, outcome:$outcome, tool:$tool, detail:$detail}')
  jsonl_append "$LOG_FILE" "$row" || true
}

# Self-match: only fire on Notion comment creation (settings matcher should
# already scope us, but stay safe if wired more broadly).
if [ "$TOOL_NAME" != "mcp__notion__API_create_a_comment" ]; then
  exit 0
fi

# Join all rich_text content into one body string. Fail-open on parse errors.
BODY=$(echo "$INPUT" | { jq -r '[.tool_input.rich_text[]?.text.content // empty] | join("\n")' 2>/dev/null || true; })

if [ -z "$BODY" ]; then
  emit_telemetry "allowed-no-body" ""
  exit 0
fi

# Override token — allow but log
if echo "$BODY" | grep -q 'comms:exempt'; then
  emit_telemetry "overridden" ""
  exit 0
fi

# Already terse: short comments are compliant as-is
CHAR_COUNT=$(printf '%s' "$BODY" | wc -c)
LINE_COUNT=$(printf '%s\n' "$BODY" | wc -l)
if [ "$CHAR_COUNT" -le 400 ] && [ "$LINE_COUNT" -le 6 ]; then
  emit_telemetry "allowed-terse" "chars=$CHAR_COUNT lines=$LINE_COUNT"
  exit 0
fi

# Otherwise: deny with guidance
emit_telemetry "denied" "chars=$CHAR_COUNT lines=$LINE_COUNT"

cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked: Notion comment is long — Notion comments have no collapsible block, so dual-comms means terse comment + linked full context.\n\n1. COMMENT — ultra-terse. At most 3 takeaways. Fragments fine. No fluff ('56/56 tests passing' -> 'green').\n\n2. FULL CONTEXT — write the long version into a page block or child page (page content is not policed), then link it from the comment.\n\nRewrite the comment that way, or if this post genuinely shouldn't follow dual-comms, include the token 'comms:exempt' in the comment text."
  }
}
EOF

exit 0
