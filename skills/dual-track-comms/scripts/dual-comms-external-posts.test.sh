#!/bin/bash
# Tests for dual-comms-external-posts.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="${SCRIPT_DIR}/dual-comms-external-posts.sh"

# Sandbox HOOKS_LOG_DIR so telemetry doesn't bleed into ~/logs
TMP_LOG_DIR=$(mktemp -d)
TMP_BODY_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_LOG_DIR" "$TMP_BODY_DIR"' EXIT
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

run() {
  jq -cn --arg c "$1" --arg d "$TMP_BODY_DIR" \
    '{tool_input:{command:$c},session_id:"test",cwd:$d}' \
    | bash "$HOOK"
}

decision() {
  echo "$1" | jq -r '.hookSpecificOutput.permissionDecision // ""'
}

LONG=$(printf 'long analysis line with plenty of detail. %.0s' {1..15})

# 1. long inline body without <details> → DENY
OUT=$(run "gh pr comment 42 --body \"$LONG\"")
assert "denies long inline body without details block" "deny" "$(decision "$OUT")"

# 2. body with <details> block → ALLOW
OUT=$(run "gh pr comment 42 --body \"green. <details><summary>Full context for agent readers</summary>$LONG</details>\"")
assert "allows body containing details block" "" "$OUT"

# 3. short terse body → ALLOW
OUT=$(run "gh issue comment 9 --body \"green. shipping.\"")
assert "allows short terse body" "" "$OUT"

# 4. bare review approve (no body) → ALLOW
OUT=$(run "gh pr review 42 --approve")
assert "allows bare gh pr review --approve" "" "$OUT"

# 5. override token → ALLOW
OUT=$(run "gh pr comment 42 --body \"$LONG\" # comms:exempt")
assert "honors '# comms:exempt' override" "" "$OUT"

# 6. unrelated gh command → silent ALLOW
OUT=$(run "gh pr view 42")
assert "ignores unrelated gh commands" "" "$OUT"

# 7. long body-file → DENY
printf '%s\n%s\n%s\n%s\n%s\n%s\n%s\n' "$LONG" "$LONG" "$LONG" "$LONG" "$LONG" "$LONG" "$LONG" > "$TMP_BODY_DIR/long.md"
OUT=$(run "gh pr comment 42 --body-file $TMP_BODY_DIR/long.md")
assert "denies long body-file without details block" "deny" "$(decision "$OUT")"

# 7b. relative body-file path resolved against cwd → DENY
OUT=$(run "gh pr comment 42 --body-file long.md")
assert "resolves relative body-file against cwd" "deny" "$(decision "$OUT")"

# 8. compliant body-file → ALLOW
printf 'green.\n<details><summary>Full context for agent readers</summary>\n%s\n</details>\n' "$LONG" > "$TMP_BODY_DIR/ok.md"
OUT=$(run "gh pr comment 42 --body-file $TMP_BODY_DIR/ok.md")
assert "allows compliant body-file" "" "$OUT"

# 9. stdin body-file → ALLOW (unreadable, logged)
OUT=$(run "gh pr comment 42 --body-file -")
assert "allows stdin body-file" "" "$OUT"

# 10. missing body-file → ALLOW (unreadable, logged)
OUT=$(run "gh pr comment 42 --body-file /nonexistent/dc-xyz.md")
assert "allows unreadable body-file" "" "$OUT"

# 11. gh issue comment long body → DENY
OUT=$(run "gh issue comment 7 --body \"$LONG\"")
assert "denies long gh issue comment body" "deny" "$(decision "$OUT")"

# 12. gh pr review with long body → DENY
OUT=$(run "gh pr review 42 --request-changes --body \"$LONG\"")
assert "denies long gh pr review body" "deny" "$(decision "$OUT")"

# --- Linear (curl api.linear.app/graphql commentCreate) ---

LINEAR_URL="https://api.linear.app/graphql"

# L1. long Linear comment payload without collapsible → DENY
OUT=$(run "curl -sS -X POST $LINEAR_URL -H 'Authorization: key' -d '{\"query\": \"mutation { commentCreate(input: { issueId: \\\"abc\\\", body: \\\"$LONG\\\" }) { success } }\"}'")
assert "denies long Linear comment without +++ collapsible" "deny" "$(decision "$OUT")"

# L2. Linear comment with +++ collapsible → ALLOW
OUT=$(run "curl -sS -X POST $LINEAR_URL -d '{\"query\": \"mutation { commentCreate(input: { issueId: \\\"abc\\\", body: \\\"green. +++ Full context for agent readers $LONG +++\\\" }) { success } }\"}'")
assert "allows Linear comment with +++ collapsible" "" "$OUT"

# L3. short Linear comment → ALLOW (600-char budget for GraphQL boilerplate)
OUT=$(run "curl -sS -X POST $LINEAR_URL -d '{\"query\": \"mutation { commentCreate(input: { issueId: \\\"abc\\\", body: \\\"green. shipping.\\\" }) { success } }\"}'")
assert "allows short Linear comment" "" "$OUT"

# L4. Linear query (non-comment) → silent ALLOW
OUT=$(run "curl -sS -X POST $LINEAR_URL -d '{\"query\": \"{ issue(id: \\\"abc\\\") { title } }\"}'")
assert "ignores Linear reads (no commentCreate)" "" "$OUT"

# L5. Linear override token → ALLOW
OUT=$(run "curl -sS -X POST $LINEAR_URL -d '{\"query\": \"mutation { commentCreate(input: { issueId: \\\"abc\\\", body: \\\"$LONG\\\" }) { success } }\"}' # comms:exempt")
assert "honors override on Linear post" "" "$OUT"

# --- Slack (curl chat.postMessage) ---

SLACK_URL="https://slack.com/api/chat.postMessage"

# S1. long top-level Slack message → DENY
OUT=$(run "curl -sS -X POST $SLACK_URL -H 'Authorization: Bearer tok' -d '{\"channel\": \"C123\", \"text\": \"$LONG\"}'")
assert "denies long top-level Slack message" "deny" "$(decision "$OUT")"

# S2. threaded reply (thread_ts) → ALLOW regardless of length
OUT=$(run "curl -sS -X POST $SLACK_URL -d '{\"channel\": \"C123\", \"thread_ts\": \"123.456\", \"text\": \"$LONG\"}'")
assert "allows long Slack threaded reply (thread_ts)" "" "$OUT"

# S3. short top-level Slack message → ALLOW
OUT=$(run "curl -sS -X POST $SLACK_URL -d '{\"channel\": \"C123\", \"text\": \"green. shipping. details in thread.\"}'")
assert "allows short top-level Slack message" "" "$OUT"

# S4. unrelated Slack API call → silent ALLOW
OUT=$(run "curl -sS https://slack.com/api/conversations.history -d '{\"channel\": \"C123\"}'")
assert "ignores non-postMessage Slack calls" "" "$OUT"

# S5. payload file → read and enforced
printf '{"channel": "C123", "text": "%s %s %s"}\n' "$LONG" "$LONG" "$LONG" > "$TMP_BODY_DIR/slack-payload.json"
OUT=$(run "curl -sS -X POST $SLACK_URL -d @$TMP_BODY_DIR/slack-payload.json")
assert "denies long Slack payload from -d @file" "deny" "$(decision "$OUT")"

# 13. telemetry — denied rows recorded
LOG="$TMP_LOG_DIR/dual-comms-external-posts.jsonl"
COUNT=$(grep -c '"outcome":"denied"' "$LOG" 2>/dev/null || echo 0)
[ "$COUNT" -ge 4 ] && {
  echo "✓ telemetry logs denied rows"
  PASS=$((PASS+1))
} || {
  echo "✗ telemetry logs denied rows (got $COUNT, expected ≥4)"
  FAIL=$((FAIL+1))
}

# 14. telemetry — override row recorded
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
