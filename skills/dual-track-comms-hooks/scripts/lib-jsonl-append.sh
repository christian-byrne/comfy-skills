#!/bin/bash
# lib-jsonl-append.sh: atomic JSONL file appending with file locking
#
# Usage:
#   source "$(dirname "$0")/lib-jsonl-append.sh"
#   jsonl_append "/path/to/file.jsonl" "$JSON_LINE"
#
# Uses flock for atomic appends when available; falls back to direct append on systems
# without flock. Timeouts gracefully (flock -w 2) so failed appends don't break hooks.
#
# Rationale: POSIX write atomicity only guarantees for ≤4096 bytes (PIPE_BUF).
# Multiple concurrent writers or long entries can interleave. This helper ensures
# each line is appended atomically.

set -euo pipefail

# jsonl_append: atomically append a single JSON line to a file
# Args:
#   $1: file path (will be created if missing)
#   $2: JSON line to append (must be a single line)
# Returns:
#   0 on success, 0 on flock timeout (non-blocking failure)
#   Exit code from jq if JSON parsing fails (caller's responsibility)
jsonl_append() {
  local file="$1" line="$2"
  
  # Ensure directory exists
  mkdir -p "$(dirname "$file")"
  
  # Use flock for atomic append if available; fallback to direct append
  if command -v flock >/dev/null 2>&1; then
    # flock: -x = exclusive lock, -w 2 = timeout 2s, 9 = fd to lock
    # On timeout (exit code 1), we silently skip (|| exit 0) to avoid breaking the hook
    (
      flock -x -w 2 9 || exit 0
      printf '%s\n' "$line" >&9
    ) 9>>"$file"
  else
    # Fallback: direct append (less safe, but best-effort on systems without flock)
    printf '%s\n' "$line" >> "$file"
  fi
}
