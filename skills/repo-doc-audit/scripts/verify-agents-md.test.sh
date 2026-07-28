#!/usr/bin/env bash
# Test suite for verify-agents-md.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_SCRIPT="$SCRIPT_DIR/verify-agents-md.sh"

PASS=0
FAIL=0

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "✅ $desc"
    PASS=$((PASS + 1))
  else
    echo "❌ $desc"
    echo "   Expected: $expected"
    echo "   Actual:   $actual"
    FAIL=$((FAIL + 1))
  fi
}

# =============================================================================
# Setup / Teardown
# =============================================================================

TMPDIR_ROOT=""

setup() {
  TMPDIR_ROOT="$(mktemp -d)"
}

cleanup() {
  if [[ -n "${TMPDIR_ROOT:-}" && -d "$TMPDIR_ROOT" ]]; then
    rm -rf "$TMPDIR_ROOT"
  fi
}
trap cleanup EXIT

# =============================================================================
# Test: Dead file references detected
# =============================================================================

test_dead_refs() {
  setup
  mkdir -p "$TMPDIR_ROOT/subdir"

  # Root AGENTS.md — references a file that exists
  echo "See \`existing.ts\` for details." > "$TMPDIR_ROOT/AGENTS.md"
  touch "$TMPDIR_ROOT/existing.ts"

  # Subdir AGENTS.md — references a file that does NOT exist
  echo "Check \`missing-file.ts\` for the pattern." > "$TMPDIR_ROOT/subdir/AGENTS.md"

  output="$(bash "$VERIFY_SCRIPT" "$TMPDIR_ROOT" 2>&1 || true)"
  exit_code=0
  bash "$VERIFY_SCRIPT" "$TMPDIR_ROOT" > /dev/null 2>&1 || exit_code=$?

  assert_eq "Dead ref exits non-zero" "1" "$exit_code"

  if echo "$output" | grep -q "Dead ref.*missing-file.ts"; then
    assert_eq "Dead ref reported for missing-file.ts" "true" "true"
  else
    assert_eq "Dead ref reported for missing-file.ts" "true" "false"
  fi

  if echo "$output" | grep -q "Dead ref.*existing.ts"; then
    assert_eq "No false positive for existing.ts" "false" "true"
  else
    assert_eq "No false positive for existing.ts" "false" "false"
  fi

  cleanup
}

# =============================================================================
# Test: Length warning for subdirectory AGENTS.md over 100 lines
# =============================================================================

test_length_warning() {
  setup
  mkdir -p "$TMPDIR_ROOT/longdir"

  # Root AGENTS.md — 150 lines, should NOT warn (root is exempt)
  for i in $(seq 1 150); do echo "Root line $i"; done > "$TMPDIR_ROOT/AGENTS.md"

  # Subdir AGENTS.md — 120 lines, should warn
  for i in $(seq 1 120); do echo "Sub line $i"; done > "$TMPDIR_ROOT/longdir/AGENTS.md"

  output="$(bash "$VERIFY_SCRIPT" "$TMPDIR_ROOT" 2>&1 || true)"

  if echo "$output" | grep -q "longdir/AGENTS.md.*120 lines"; then
    assert_eq "Length warning for 120-line subdir AGENTS.md" "true" "true"
  else
    assert_eq "Length warning for 120-line subdir AGENTS.md" "true" "false"
  fi

  # Root should not be warned
  if echo "$output" | grep -q "⚠️.*$TMPDIR_ROOT/AGENTS.md"; then
    assert_eq "No length warning for root AGENTS.md" "false" "true"
  else
    assert_eq "No length warning for root AGENTS.md" "false" "false"
  fi

  cleanup
}

# =============================================================================
# Test: All valid — clean pass
# =============================================================================

test_all_valid() {
  setup
  mkdir -p "$TMPDIR_ROOT/validdir"

  # Root AGENTS.md with valid ref
  echo "See \`app.ts\` for entry." > "$TMPDIR_ROOT/AGENTS.md"
  touch "$TMPDIR_ROOT/app.ts"

  # Short subdir AGENTS.md with valid ref
  echo "Check \`handler.py\` for the handler." > "$TMPDIR_ROOT/validdir/AGENTS.md"
  touch "$TMPDIR_ROOT/validdir/handler.py"

  exit_code=0
  bash "$VERIFY_SCRIPT" "$TMPDIR_ROOT" > /dev/null 2>&1 || exit_code=$?

  assert_eq "All valid exits zero" "0" "$exit_code"

  output="$(bash "$VERIFY_SCRIPT" "$TMPDIR_ROOT" 2>&1)"
  if echo "$output" | grep -q "All AGENTS.md files pass verification"; then
    assert_eq "Shows pass message" "true" "true"
  else
    assert_eq "Shows pass message" "true" "false"
  fi

  cleanup
}

# =============================================================================
# Run all tests
# =============================================================================

echo "=== verify-agents-md.sh tests ==="
echo ""

test_dead_refs
test_length_warning
test_all_valid

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
