#!/usr/bin/env bash
# verify-agents-md.sh — Deterministic verification of AGENTS.md files
# Usage: ./scripts/verify-agents-md.sh [dir] (default: current directory)
set -euo pipefail

DIR="${1:-.}"
err_file="$(mktemp)"
warn_file="$(mktemp)"
trap 'rm -f "$err_file" "$warn_file"' EXIT

echo "0" > "$err_file"
echo "0" > "$warn_file"

echo "=== AGENTS.md Verification ==="

# Check 1: Link check — file paths mentioned in AGENTS.md exist
echo "--- Link Check ---"
while read -r agents_file; do
  agents_dir=$(dirname "$agents_file")
  # shellcheck disable=SC2016
  refs=$(grep -oE '`[^`]*\.(ts|js|py|rs|go|md|json|yaml|toml|sh|sql|vue|css|html)`' "$agents_file" 2>/dev/null | tr -d '`' | sort -u || true)
  [[ -z "$refs" ]] && continue
  while read -r ref; do
    if [[ ! -f "$agents_dir/$ref" && ! -f "$DIR/$ref" ]]; then
      echo "❌ Dead ref in $agents_file: $ref"
      echo "$(( $(cat "$err_file") + 1 ))" > "$err_file"
    fi
  done <<< "$refs"
done < <(find "$DIR" -name 'AGENTS.md' -not -path '*/node_modules/*' -not -path '*/.git/*')

# Check 2: Length check — AGENTS.md files over 100 lines (exclude root)
echo "--- Length Check ---"
while read -r agents_file; do
  lines=$(wc -l < "$agents_file")
  rel_path="${agents_file#"$DIR"/}"
  if [[ "$rel_path" != "AGENTS.md" && "$lines" -gt 100 ]]; then
    echo "⚠️  $agents_file is $lines lines (target: <100)"
    echo "$(( $(cat "$warn_file") + 1 ))" > "$warn_file"
  fi
done < <(find "$DIR" -name 'AGENTS.md' -not -path '*/node_modules/*' -not -path '*/.git/*')

errors=$(cat "$err_file")
warnings=$(cat "$warn_file")

echo ""
echo "=== Summary ==="
if [[ $errors -gt 0 ]]; then
  echo "❌ $errors dead reference(s) found"
fi
if [[ $warnings -gt 0 ]]; then
  echo "⚠️  $warnings warning(s)"
fi
if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
  echo "✅ All AGENTS.md files pass verification"
fi

exit $(( errors > 0 ? 1 : 0 ))
