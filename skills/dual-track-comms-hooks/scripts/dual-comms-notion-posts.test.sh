#!/bin/bash
# Tests for dual-comms-notion-posts.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="${SCRIPT_DIR}/dual-comms-notion-posts.sh"

# Sandbox HOOKS_LOG_DIR so telemetry doesn't bleed into ~/logs
TMP_LOG_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_LOG_DIR"' EXIT
export HOOKS_LOG_DIR="$TMP_LOG_DIR"

PASS=0
FAIL=0

assert() {
  local name="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    echo "✓ $name"
    PASS=$((PASS+1))
  else
    echo "✗ $name"
    echo "  expected: $expected"
    echo "  actual:   $actual"
    FAIL=$((FAIL+1))
  fi
}

# run <tool_name> <comment-text...>  — each extra arg becomes a rich_text item
run() {
  local tool="$1"; shift
  jq -cn --arg t "$tool" '$ARGS.positional | map({text:{content:.}}) | {tool_name:$t, tool_input:{parent:{page_id:"p1"}, rich_text:.}, session_id:"test"}' --args "$@" \
    | bash "$HOOK"
}

decision() {
  echo "$1" | jq -r '.hookSpecificOutput.permissionDecision // ""'
}

TOOL="mcp__notion__API_create_a_comment"
LONG=$(printf 'long analysis line with plenty of detail. %.0s' {1..15})

# 1. long comment → DENY
OUT=$(run "$TOOL" "$LONG")
assert "denies long Notion comment" "deny" "$(decision "$OUT")"

# 2. short terse comment → ALLOW
OUT=$(run "$TOOL" "green. shipping. full context: <page link>")
assert "allows short terse comment" "" "$OUT"

# 3. multiple rich_text items summed → DENY when combined length is long
OUT=$(run "$TOOL" "$LONG" "$LONG")
assert "sums multiple rich_text items" "deny" "$(decision "$OUT")"

# 4. override token → ALLOW
OUT=$(run "$TOOL" "$LONG comms:exempt")
assert "honors comms:exempt override" "" "$OUT"

# 5. other tool name → silent ALLOW
OUT=$(run "mcp__notion__API_retrieve_a_page" "$LONG")
assert "ignores non-comment Notion tools" "" "$OUT"

# 6. empty rich_text → ALLOW
OUT=$(jq -cn --arg t "$TOOL" '{tool_name:$t, tool_input:{parent:{page_id:"p1"}, rich_text:[]}, session_id:"test"}' | bash "$HOOK")
assert "allows empty rich_text" "" "$OUT"

# 7. malformed input → fail-open ALLOW
OUT=$(echo '{"tool_name":"mcp__notion__API_create_a_comment"}' | bash "$HOOK")
assert "fails open on missing tool_input" "" "$OUT"

# 8. telemetry — denied rows recorded
LOG="$TMP_LOG_DIR/dual-comms-notion-posts.jsonl"
COUNT=$(grep -c '"outcome":"denied"' "$LOG" 2>/dev/null || echo 0)
[ "$COUNT" -ge 2 ] && {
  echo "✓ telemetry logs denied rows"
  PASS=$((PASS+1))
} || {
  echo "✗ telemetry logs denied rows (got $COUNT, expected ≥2)"
  FAIL=$((FAIL+1))
}

# 9. telemetry — override row recorded
COUNT=$(grep -c '"outcome":"overridden"' "$LOG" 2>/dev/null || echo 0)
[ "$COUNT" -ge 1 ] && {
  echo "✓ telemetry logs override row"
  PASS=$((PASS+1))
} || {
  echo "✗ telemetry logs override row (got $COUNT)"
  FAIL=$((FAIL+1))
}

echo ""
echo "Passed: $PASS  Failed: $FAIL"
[ "$FAIL" -eq 0 ]
