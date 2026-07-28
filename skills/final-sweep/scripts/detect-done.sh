#!/usr/bin/env bash
# detect-done.sh — Deterministic pre-flight scan for final-sweep Phase 0
#
# Detects PR status, CI checks, recent quality commits, and repo tooling.
# Outputs a human-readable summary to stdout for skill auto-execute injection.
#
# Usage:
#   bash skills/final-sweep/scripts/detect-done.sh
#
# Related: skills/final-sweep/SKILL.md Phase 0
# Issue: #1821 (extract Phase 0 dedup scan into standalone script)

set -euo pipefail

# --- Guard: must be in a git repo ---

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "⚠ Not in a git repo — skipping pre-flight scan."
  exit 0
}

BRANCH=$(git branch --show-current 2>/dev/null || echo "")

echo "=== Final Sweep Pre-Flight ==="
echo "Repo: $ROOT"
echo "Branch: ${BRANCH:-detached HEAD}"
echo ""

# --- PR & CI status ---

PR_NUMBER=$(gh pr list --head "${BRANCH}" --json number -q '.[0].number' 2>/dev/null || echo "")

if [ -n "$PR_NUMBER" ]; then
  echo "PR: #${PR_NUMBER}"
  CI_OUTPUT=$(gh pr checks "$PR_NUMBER" 2>/dev/null || echo "(gh not authenticated or checks unavailable)")
  echo "CI checks:"
  echo "$CI_OUTPUT" | head -20
else
  echo "PR: none found for branch '${BRANCH}'"
fi

echo ""

# --- Recent quality-related commits ---

echo "Recent quality commits (last 10):"
QUALITY_COMMITS=$(git log --oneline -10 2>/dev/null | grep -iE "fix|lint|format|test|chore|docs" || true)
if [ -n "$QUALITY_COMMITS" ]; then
  echo "$QUALITY_COMMITS"
else
  echo "  (none)"
fi

echo ""

# --- Tooling detection ---

SHARED_DETECT="$ROOT/scripts/detect-tooling.sh"

echo "Detected tooling:"
if [ -x "$SHARED_DETECT" ]; then
  # Optional: if this repo has its own shared tooling-detection script, prefer it
  TOOLING_JSON="$(bash "$SHARED_DETECT")"
  echo "$TOOLING_JSON" | jq -r 'to_entries | map(select(.value == true or (.value | type == "string" and . != "npm"))) | map("  \(.key)=\(.value)") | .[]'
else
  # This skill doesn't ship its own detect-tooling.sh — minimal inline fallback
  [ -f "$ROOT/package.json" ] && echo "  node=true" || true
  [ -f "$ROOT/Cargo.toml" ] && echo "  rust=true" || true
  { [ -f "$ROOT/pyproject.toml" ] || [ -f "$ROOT/setup.py" ]; } && echo "  python=true" || true
  [ -d "$ROOT/.github/workflows" ] && echo "  github-actions=true" || true
  [ -d "$ROOT/terraform" ] && echo "  terraform=true" || true
  ls "$ROOT"/Dockerfile* &>/dev/null && echo "  docker=true" || true
fi

echo ""
echo "=== End Pre-Flight ==="
