#!/bin/bash
# Deterministic scoring — compares agent output against expected result.
# Writes a score (0.0–1.0) to /logs/reward.txt.

set -euo pipefail
mkdir -p /logs

OUTPUT="/task/output.txt"
EXPECTED="/task/files/expected.txt"

if [ ! -f "$OUTPUT" ]; then
  echo "0.0" > /logs/reward.txt
  echo "FAIL: No output file produced"
  exit 0
fi

if diff -q "$OUTPUT" "$EXPECTED" > /dev/null 2>&1; then
  echo "1.0" > /logs/reward.txt
  echo "PASS: Output matches expected"
else
  # Partial credit: count matching lines / total lines
  TOTAL=$(wc -l < "$EXPECTED")
  MATCHING=$(comm -12 <(sort "$OUTPUT") <(sort "$EXPECTED") | wc -l)
  SCORE=$(python3 -c "print(f'{$MATCHING / max($TOTAL, 1):.2f}')")
  echo "$SCORE" > /logs/reward.txt
  echo "PARTIAL: $MATCHING/$TOTAL lines match (score: $SCORE)"
fi
