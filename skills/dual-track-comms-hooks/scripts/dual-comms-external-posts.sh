#!/bin/bash
set -euo pipefail

# dual-comms-external-posts — Enforces the dual-communication format on
# external posts (GitHub PR/issue comments and reviews, Linear comments,
# Slack messages). Every external post readable by humans must lead with an
# ultra-terse top level (<=3 takeaways, fragments fine, "56/56 tests" ->
# "green") and put everything else in the platform's collapsible/threaded
# full-context mechanism:
#   GitHub  -> <details><summary>...</summary>...</details>
#   Linear  -> +++ Section title ... +++ (collapsible section)
#   Slack   -> terse top-level message, full context as threaded reply
#              (thread_ts present = it IS the full-context reply -> allowed)
#
# Protocol: PreToolUse (matcher: Bash)
#   stdin:  JSON { tool_input: { command }, session_id, cwd }
#   stdout: deny JSON or empty
#   exit 0: always (advisory hook — never crashes the agent)
#
# Triggers on:
#   gh pr comment ...    --body/-b or --body-file/-F
#   gh issue comment ... --body/-b or --body-file/-F
#   gh pr review ...     --body/-b or --body-file/-F
#   curl ... api.linear.app/graphql ... commentCreate   (-d payload)
#   curl ... slack.com/api/chat.postMessage             (-d payload)
#
# Allowed without prompt:
#   - short bodies (already terse: <=400 chars AND <=6 lines; Linear payloads
#     get a higher 600-char budget for GraphQL boilerplate)
#   - bodies containing a <details> block or Linear +++ collapsible
#   - Slack payloads containing thread_ts (threaded reply = full context home)
#   - gh pr review with no body (bare --approve / --request-changes)
#   - --body-file - (stdin body; unreadable here) — allowed but logged
#   - unreadable -d @file payloads — allowed but logged
#   - presence of override token '# comms:exempt' in command
#
# Telemetry: appends JSONL row to $HOOKS_LOG_DIR/dual-comms-external-posts.jsonl
#            on every trigger (allowed/denied/overridden).

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "Hook: enforces dual-comms format (terse top level + <details> full context)"
  echo "      on gh pr comment / gh issue comment / gh pr review bodies"
  echo "Event: PreToolUse (matcher: Bash)"
  echo "Override: append '# comms:exempt' anywhere in the command"
  exit 0
fi

# Resolve symlinks to find the actual script directory (hooks are often symlinked from ~/bin)
SCRIPT_PATH="${BASH_SOURCE[0]}"
[[ -L "$SCRIPT_PATH" ]] && SCRIPT_PATH=$(readlink -f "$SCRIPT_PATH")
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
# shellcheck source=lib-jsonl-append.sh
source "$SCRIPT_DIR/lib-jsonl-append.sh"

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""')
CWD=$(echo "$INPUT" | jq -r '.cwd // ""')

LOG_DIR="${HOOKS_LOG_DIR:-${AMP_LOG_DIR:-$HOME/logs}}"
LOG_FILE="$LOG_DIR/dual-comms-external-posts.jsonl"

emit_telemetry() {
  local outcome="$1" matched="$2"
  local ts
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  local row
  row=$(jq -cn \
    --arg ts "$ts" \
    --arg session "$SESSION_ID" \
    --arg outcome "$outcome" \
    --arg matched "$matched" \
    --arg cmd "$CMD" \
    '{ts:$ts, session_id:$session, outcome:$outcome, matched:$matched, command:$cmd}')
  jsonl_append "$LOG_FILE" "$row" || true
}

# Only fire on the known external-post shapes
MATCHED=""
PLATFORM=""
if echo "$CMD" | grep -qE '\bgh\s+pr\s+comment\b'; then
  MATCHED="gh-pr-comment"; PLATFORM="github"
elif echo "$CMD" | grep -qE '\bgh\s+issue\s+comment\b'; then
  MATCHED="gh-issue-comment"; PLATFORM="github"
elif echo "$CMD" | grep -qE '\bgh\s+pr\s+review\b'; then
  MATCHED="gh-pr-review"; PLATFORM="github"
elif echo "$CMD" | grep -q 'api\.linear\.app/graphql' && echo "$CMD" | grep -q 'commentCreate'; then
  MATCHED="linear-comment"; PLATFORM="linear"
elif echo "$CMD" | grep -q 'slack\.com/api/chat\.postMessage'; then
  MATCHED="slack-post"; PLATFORM="slack"
fi

if [ -z "$MATCHED" ]; then
  exit 0
fi

# Override token — allow but log
if echo "$CMD" | grep -qE '#[[:space:]]*comms:exempt'; then
  emit_telemetry "overridden" "$MATCHED"
  exit 0
fi

# Extract the body.
# GitHub sources:
#   --body/-b <text>       (inline; often a quoted string or heredoc var)
#   --body-file/-F <path>  (read the file if it exists)
# Linear/Slack (curl) sources:
#   -d/--data/--data-raw/--data-binary <json>   (inline payload)
#   -d @<path>                                  (payload file)
BODY=""
BODY_SOURCE=""

if [ "$PLATFORM" != "github" ]; then
  # curl payload extraction (heuristic; length/marker checks tolerate rough edges)
  PAYLOAD=$(echo "$CMD" | sed -nE "s/.*(--data-raw|--data-binary|--data|[[:space:]]-d)(=|[[:space:]]+)//p")
  PAYLOAD_FILE=$(echo "$PAYLOAD" | { grep -oE '^@[^[:space:]]+' || true; } | sed -E "s/^@//; s/^['\"]//; s/['\"]$//")
  if [ -n "$PAYLOAD_FILE" ]; then
    [[ "$PAYLOAD_FILE" != /* ]] && [ -n "$CWD" ] && PAYLOAD_FILE="$CWD/$PAYLOAD_FILE"
    if [ -f "$PAYLOAD_FILE" ]; then
      BODY=$(cat "$PAYLOAD_FILE")
      BODY_SOURCE="file"
    else
      emit_telemetry "allowed-unreadable-payload-file" "$MATCHED"
      exit 0
    fi
  else
    BODY="$PAYLOAD"
    BODY_SOURCE="inline"
  fi

  if [ -z "$BODY" ]; then
    emit_telemetry "allowed-no-body" "$MATCHED"
    exit 0
  fi

  # Slack: a threaded reply IS the full-context half of dual-comms — allow.
  if [ "$PLATFORM" = "slack" ] && echo "$BODY" | grep -q 'thread_ts'; then
    emit_telemetry "allowed-threaded-reply" "$MATCHED"
    exit 0
  fi

  # Linear: +++ collapsible section (or <details>) = compliant.
  if [ "$PLATFORM" = "linear" ] && echo "$BODY" | grep -qE '\+\+\+|<details>'; then
    emit_telemetry "allowed-compliant" "$MATCHED"
    exit 0
  fi

  CHAR_COUNT=$(printf '%s' "$BODY" | wc -c)
  LINE_COUNT=$(printf '%s\n' "$BODY" | wc -l)
  # Linear GraphQL payloads carry ~200 chars of mutation boilerplate — budget for it.
  MAX_CHARS=400
  [ "$PLATFORM" = "linear" ] && MAX_CHARS=600
  if [ "$CHAR_COUNT" -le "$MAX_CHARS" ] && [ "$LINE_COUNT" -le 6 ]; then
    emit_telemetry "allowed-terse" "$MATCHED"
    exit 0
  fi

  emit_telemetry "denied" "$MATCHED (source=$BODY_SOURCE chars=$CHAR_COUNT lines=$LINE_COUNT)"

  if [ "$PLATFORM" = "linear" ]; then
    cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked: Linear comment body is long but not in dual-comms format.\n\nEvery external comment must use DUAL COMMUNICATION:\n\n1. TOP LEVEL — ultra-terse. At most 3 takeaways. Fragments fine. No fluff ('56/56 tests passing' -> 'green').\n\n2. FULL CONTEXT — everything else goes in a Linear collapsible section:\n    +++ Full context for agent readers\n\n    ...the message you would normally send...\n\n    +++\n\nRewrite the comment body in that shape, or if this post genuinely shouldn't follow dual-comms, append an override token:\n    <your curl command>  # comms:exempt"
  }
}
EOF
  else
    cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked: Slack top-level message is long — dual-comms puts full context in a thread.\n\nEvery external Slack post must use DUAL COMMUNICATION:\n\n1. TOP LEVEL message — ultra-terse. At most 3 takeaways. Fragments fine. No fluff ('56/56 tests passing' -> 'green').\n\n2. FULL CONTEXT — post the long version as a threaded reply to that message (include thread_ts in the payload).\n\nSend the terse top-level first, then reply in-thread with the detail. If this post genuinely shouldn't follow dual-comms, append an override token:\n    <your curl command>  # comms:exempt"
  }
}
EOF
  fi
  exit 0
fi

BODY_FILE=$(echo "$CMD" | { grep -oE -- '(--body-file|-F)(=|[[:space:]]+)[^[:space:]]+' || true; } \
  | head -1 \
  | sed -E 's/^(--body-file|-F)(=|[[:space:]]+)//' \
  | sed -E "s/^['\"]//; s/['\"]$//")

if [ -n "$BODY_FILE" ]; then
  if [ "$BODY_FILE" = "-" ]; then
    # stdin body — unreadable here; allow but log
    emit_telemetry "allowed-stdin-body" "$MATCHED"
    exit 0
  fi
  # Resolve relative to the session cwd when needed
  if [[ "$BODY_FILE" != /* ]] && [ -n "$CWD" ]; then
    BODY_FILE="$CWD/$BODY_FILE"
  fi
  if [ -f "$BODY_FILE" ]; then
    BODY=$(cat "$BODY_FILE")
    BODY_SOURCE="file"
  else
    # Can't read it (heredoc-generated later, tempfile, etc.) — allow but log
    emit_telemetry "allowed-unreadable-body-file" "$MATCHED"
    exit 0
  fi
else
  # Inline --body/-b. Grab everything after the flag; strip one layer of quotes.
  # This is heuristic — shell-quoted bodies inside a command string can't be
  # parsed perfectly, but length/marker checks tolerate rough extraction.
  BODY=$(echo "$CMD" | sed -nE "s/.*(--body|[[:space:]]-b)(=|[[:space:]]+)//p")
  BODY_SOURCE="inline"
fi

# No body at all (e.g. bare 'gh pr review --approve') — allow
if [ -z "$BODY" ]; then
  emit_telemetry "allowed-no-body" "$MATCHED"
  exit 0
fi

# Compliant: contains a collapsible details block
if echo "$BODY" | grep -qiE '<details>'; then
  emit_telemetry "allowed-compliant" "$MATCHED"
  exit 0
fi

# Already terse: short bodies don't need a details block
CHAR_COUNT=$(printf '%s' "$BODY" | wc -c)
LINE_COUNT=$(printf '%s\n' "$BODY" | wc -l)
if [ "$CHAR_COUNT" -le 400 ] && [ "$LINE_COUNT" -le 6 ]; then
  emit_telemetry "allowed-terse" "$MATCHED"
  exit 0
fi

# Otherwise: deny with guidance
emit_telemetry "denied" "$MATCHED (source=$BODY_SOURCE chars=$CHAR_COUNT lines=$LINE_COUNT)"

cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked: external post body is long but not in dual-comms format.\n\nEvery external comment/review must use DUAL COMMUNICATION:\n\n1. TOP LEVEL — ultra-terse. At most 3 takeaways. Fragments fine. No fluff, no niceties, no info that wouldn't change what a human decides ('56/56 tests passing' -> 'green').\n\n2. FULL CONTEXT — everything else goes in a collapsible block:\n    <details><summary>Full context for agent readers</summary>\n\n    ...the message you would normally send...\n\n    </details>\n\nRewrite the body in that shape, or if this post genuinely shouldn't follow dual-comms, append an override token:\n    <your gh command>  # comms:exempt"
  }
}
EOF

exit 0
