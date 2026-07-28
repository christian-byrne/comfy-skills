#!/usr/bin/env bash
# batch-checks.sh — Run ALL local checks (tests, lint, format, typecheck, pre-commit hooks, CI-reproducible jobs)
# with continue-on-error semantics. Writes a single structured issues file optimized for agent handoff.
#
# Design: Auto-discovers available checks from the repo (package.json scripts, pre-commit config,
# Makefile targets, CI workflow steps). Runs everything, collects every failure, reports once.
#
# Usage:
#   batch-checks.sh [REPO_DIR] [OUTPUT_DIR]
#   batch-checks.sh --discover [REPO_DIR]     # List what checks would run (dry run)
#   batch-checks.sh --categories [REPO_DIR]   # List discovered check categories
#
# Output files (in OUTPUT_DIR, default /tmp/batch-local-checks):
#   issues.txt       — Unified issue list: file:line — [CATEGORY] description (agent-optimized)
#   summary.txt      — One-line status per check with duration
#   issues.json      — Machine-readable array of {file, line, category, message, check}
#   <check>.log      — Full output per check (only kept for failures)
#
# Exit code: number of failed checks (0 = all clean)
#
# Extensibility:
#   - Drop executable scripts into REPO_DIR/.batch-checks.d/ for custom checks
#   - Each script: exit 0 = pass, exit non-zero = fail, stdout = issues
#   - Or set BATCH_CHECKS_EXTRA="cmd1;cmd2" env var for ad-hoc additions

set -o pipefail

#------------------------------------------------------------------------------
# Arguments
#------------------------------------------------------------------------------
MODE="run"
if [[ "$1" == "--discover" ]]; then
  MODE="discover"
  shift
elif [[ "$1" == "--categories" ]]; then
  MODE="categories"
  shift
fi

REPO_DIR="${1:-$(pwd)}"
OUTPUT_DIR="${2:-/tmp/batch-local-checks}"

# Resolve to absolute path
REPO_DIR="$(cd "$REPO_DIR" 2>/dev/null && pwd)" || {
  echo "ERROR: Cannot access repo directory: $1" >&2
  exit 255
}

#------------------------------------------------------------------------------
# State
#------------------------------------------------------------------------------
declare -a CHECK_NAMES=()
declare -a CHECK_CMDS=()
declare -a CHECK_CATEGORIES=()
declare -A RESULTS=()
declare -A DURATIONS=()
FAIL_COUNT=0

#------------------------------------------------------------------------------
# Check Registration
#------------------------------------------------------------------------------
register_check() {
  local name="$1" cmd="$2" category="$3"
  CHECK_NAMES+=("$name")
  CHECK_CMDS+=("$cmd")
  CHECK_CATEGORIES+=("$category")
}

#------------------------------------------------------------------------------
# Discovery: package.json scripts
#------------------------------------------------------------------------------
discover_package_json() {
  local pkg="$REPO_DIR/package.json"
  [[ -f "$pkg" ]] || return 0

  local scripts
  scripts=$(jq -r '.scripts // {} | keys[]' "$pkg" 2>/dev/null) || return 0

  local pm="pnpm"
  [[ -f "$REPO_DIR/yarn.lock" ]] && pm="yarn"
  [[ -f "$REPO_DIR/package-lock.json" ]] && pm="npm"
  [[ -f "$REPO_DIR/pnpm-lock.yaml" ]] && pm="pnpm"
  [[ -f "$REPO_DIR/bun.lockb" ]] && pm="bun"

  # Format checks
  for s in format "format:check" "format:fix" prettier; do
    if echo "$scripts" | grep -qx "$s"; then
      register_check "format" "$pm run $s" "format"
      break
    fi
  done

  # Lint checks
  for s in lint "lint:fix" "lint:check" eslint; do
    if echo "$scripts" | grep -qx "$s"; then
      register_check "lint" "$pm run $s" "lint"
      break
    fi
  done

  # Typecheck
  for s in typecheck "type-check" "check:types" tsc; do
    if echo "$scripts" | grep -qx "$s"; then
      register_check "typecheck" "$pm run $s" "typecheck"
      break
    fi
  done

  # Tests
  for s in test "test:unit" "test:ci" "test:run" vitest jest; do
    if echo "$scripts" | grep -qx "$s"; then
      register_check "test" "$pm run $s" "test"
      break
    fi
  done

  # Stylelint
  for s in stylelint "stylelint:fix" "stylelint:check"; do
    if echo "$scripts" | grep -qx "$s"; then
      register_check "stylelint" "$pm run $s" "lint"
      break
    fi
  done

  # Build (catches type errors that typecheck misses)
  for s in build "build:check"; do
    if echo "$scripts" | grep -qx "$s"; then
      register_check "build" "$pm run $s" "build"
      break
    fi
  done

  # Knip (dead code)
  if echo "$scripts" | grep -qx "knip"; then
    register_check "knip" "$pm run knip" "lint"
  fi

  # Verify/check-all composite scripts
  for s in verify "verify:quick" "check-all" "ci:local" validate; do
    if echo "$scripts" | grep -qx "$s"; then
      # Only register if we haven't already registered individual checks
      if [[ ${#CHECK_NAMES[@]} -eq 0 ]]; then
        register_check "verify" "$pm run $s" "verify"
      fi
      break
    fi
  done
}

#------------------------------------------------------------------------------
# Discovery: pre-commit hooks
#------------------------------------------------------------------------------
discover_pre_commit_hooks() {
  # Husky
  local husky_hook="$REPO_DIR/.husky/pre-commit"
  if [[ -x "$husky_hook" ]]; then
    register_check "pre-commit-hook" "bash $husky_hook" "hook"
    return
  fi

  # Lefthook
  if [[ -f "$REPO_DIR/lefthook.yml" ]] || [[ -f "$REPO_DIR/.lefthook.yml" ]]; then
    if command -v lefthook &>/dev/null; then
      register_check "pre-commit-hook" "cd $REPO_DIR && lefthook run pre-commit" "hook"
      return
    fi
  fi

  # pre-commit (Python)
  if [[ -f "$REPO_DIR/.pre-commit-config.yaml" ]]; then
    if command -v pre-commit &>/dev/null; then
      register_check "pre-commit-hook" "cd $REPO_DIR && pre-commit run --all-files" "hook"
      return
    fi
  fi
}

#------------------------------------------------------------------------------
# Discovery: Makefile targets
#------------------------------------------------------------------------------
discover_makefile() {
  local makefile="$REPO_DIR/Makefile"
  [[ -f "$makefile" ]] || return 0

  local targets
  targets=$(grep -E '^[a-zA-Z_-]+:' "$makefile" | sed 's/:.*//' 2>/dev/null) || return 0

  for t in lint check test format typecheck; do
    if echo "$targets" | grep -qx "$t"; then
      # Only register if not already covered by package.json
      local already=false
      for name in "${CHECK_NAMES[@]}"; do
        [[ "$name" == "$t" ]] && already=true && break
      done
      if [[ "$already" == false ]]; then
        register_check "make-$t" "make -C $REPO_DIR $t" "$t"
      fi
    fi
  done
}

#------------------------------------------------------------------------------
# Discovery: Python projects
#------------------------------------------------------------------------------
discover_python() {
  [[ -f "$REPO_DIR/pyproject.toml" ]] || [[ -f "$REPO_DIR/setup.py" ]] || return 0

  # Ruff
  if [[ -f "$REPO_DIR/ruff.toml" ]] || [[ -f "$REPO_DIR/pyproject.toml" ]] && grep -q "ruff" "$REPO_DIR/pyproject.toml" 2>/dev/null; then
    if command -v ruff &>/dev/null; then
      register_check "ruff-check" "cd $REPO_DIR && ruff check ." "lint"
      register_check "ruff-format" "cd $REPO_DIR && ruff format --check ." "format"
    fi
  fi

  # Mypy
  if grep -q "mypy" "$REPO_DIR/pyproject.toml" 2>/dev/null; then
    if command -v mypy &>/dev/null; then
      register_check "mypy" "cd $REPO_DIR && mypy ." "typecheck"
    fi
  fi

  # Pytest
  if [[ -d "$REPO_DIR/tests" ]] || grep -q "pytest" "$REPO_DIR/pyproject.toml" 2>/dev/null; then
    if command -v pytest &>/dev/null; then
      register_check "pytest" "cd $REPO_DIR && pytest" "test"
    fi
  fi
}

#------------------------------------------------------------------------------
# Discovery: Rust projects
#------------------------------------------------------------------------------
discover_rust() {
  [[ -f "$REPO_DIR/Cargo.toml" ]] || return 0

  register_check "cargo-check" "cd $REPO_DIR && cargo check 2>&1" "typecheck"
  register_check "cargo-clippy" "cd $REPO_DIR && cargo clippy -- -D warnings 2>&1" "lint"
  register_check "cargo-test" "cd $REPO_DIR && cargo test 2>&1" "test"
  register_check "cargo-fmt" "cd $REPO_DIR && cargo fmt --check 2>&1" "format"
}

#------------------------------------------------------------------------------
# Discovery: Go projects
#------------------------------------------------------------------------------
discover_go() {
  [[ -f "$REPO_DIR/go.mod" ]] || return 0

  register_check "go-vet" "cd $REPO_DIR && go vet ./..." "lint"
  register_check "go-test" "cd $REPO_DIR && go test ./..." "test"

  if command -v golangci-lint &>/dev/null; then
    register_check "golangci-lint" "cd $REPO_DIR && golangci-lint run" "lint"
  fi

  if command -v gofmt &>/dev/null; then
    register_check "gofmt" "cd $REPO_DIR && test -z \"\$(gofmt -l .)\"" "format"
  fi
}

#------------------------------------------------------------------------------
# Discovery: custom check scripts in .batch-checks.d/
#------------------------------------------------------------------------------
discover_custom() {
  local custom_dir="$REPO_DIR/.batch-checks.d"
  [[ -d "$custom_dir" ]] || return 0

  for script in "$custom_dir"/*; do
    [[ -x "$script" ]] || continue
    local name
    name=$(basename "$script" | sed 's/\.[^.]*$//')
    register_check "custom-$name" "$script" "custom"
  done
}

#------------------------------------------------------------------------------
# Discovery: BATCH_CHECKS_EXTRA env var
#------------------------------------------------------------------------------
discover_env_extra() {
  [[ -n "${BATCH_CHECKS_EXTRA:-}" ]] || return 0

  local i=0
  IFS=';' read -ra extras <<< "$BATCH_CHECKS_EXTRA"
  for cmd in "${extras[@]}"; do
    cmd=$(echo "$cmd" | xargs) # trim whitespace
    [[ -n "$cmd" ]] || continue
    register_check "extra-$((i++))" "$cmd" "extra"
  done
}

#------------------------------------------------------------------------------
# Node.js Environment Setup
#------------------------------------------------------------------------------
setup_node() {
  # Only needed for Node.js projects
  [[ -f "$REPO_DIR/package.json" ]] || return 0

  if [[ -f "$HOME/.nvm/nvm.sh" ]]; then
    export NVM_DIR="$HOME/.nvm"
    # shellcheck source=/dev/null
    source "$NVM_DIR/nvm.sh" --no-use 2>/dev/null
    if [[ -f "$REPO_DIR/.nvmrc" ]]; then
      local required_version
      required_version=$(cat "$REPO_DIR/.nvmrc")
      nvm ls "$required_version" &>/dev/null || nvm install "$required_version" >/dev/null 2>&1
      nvm use "$required_version" >/dev/null 2>&1
    fi
  elif command -v fnm &>/dev/null; then
    eval "$(fnm env --shell bash 2>/dev/null)"
    [[ -f "$REPO_DIR/.nvmrc" ]] && fnm use --install-if-missing 2>/dev/null
  fi

  # Ensure deps
  cd "$REPO_DIR" || return 1
  if [[ ! -d "node_modules" ]] || { [[ -f "pnpm-lock.yaml" ]] && [[ "pnpm-lock.yaml" -nt "node_modules/.pnpm/lock.yaml" ]]; }; then
    echo "Installing dependencies..." >&2
    pnpm install --frozen-lockfile 2>&1 | tail -3 >&2
  fi
}

#------------------------------------------------------------------------------
# Run a single check (continue-on-error)
#------------------------------------------------------------------------------
run_check() {
  local idx="$1"
  local name="${CHECK_NAMES[$idx]}"
  local cmd="${CHECK_CMDS[$idx]}"
  local log_file="$OUTPUT_DIR/${name}.log"
  local start_time end_time duration exit_code

  echo "  [$((idx + 1))/${#CHECK_NAMES[@]}] $name ..." >&2

  start_time=$(date +%s)

  cd "$REPO_DIR" || return 1
  eval "$cmd" > "$log_file" 2>&1 || true
  exit_code=${PIPESTATUS[0]:-$?}

  end_time=$(date +%s)
  duration=$(( end_time - start_time ))
  DURATIONS[$name]="${duration}s"

  if [[ $exit_code -eq 0 ]]; then
    RESULTS[$name]="PASS"
    rm -f "$log_file"
    echo "  [$((idx + 1))/${#CHECK_NAMES[@]}] $name ✓ (${duration}s)" >&2
  else
    RESULTS[$name]="FAIL"
    FAIL_COUNT=$(( FAIL_COUNT + 1 ))
    echo "  [$((idx + 1))/${#CHECK_NAMES[@]}] $name ✗ (${duration}s)" >&2
  fi
}

#------------------------------------------------------------------------------
# Parse check output into structured issues
#------------------------------------------------------------------------------
parse_issues() {
  local name="$1"
  local category="${2:-unknown}"
  local log_file="$OUTPUT_DIR/${name}.log"

  [[ -f "$log_file" ]] || return 0

  case "$category" in
    typecheck)
      # TS errors: src/foo.ts(10,5): error TS2345: ...
      grep -E '\.tsx?\(' "$log_file" | sed -E 's/\(([0-9]+),[0-9]+\)/:\1/' | while IFS= read -r line; do
        echo "$line" | sed -E 's/^([^:]+:[0-9]+): error ([A-Z0-9]+): (.*)$/\1 — [typecheck] \3 (\2)/'
      done
      # Also catch vue-tsc style: src/foo.ts:10:5 - error TS2345
      grep -E '\.tsx?:[0-9]+:[0-9]+ - error' "$log_file" | while IFS= read -r line; do
        echo "$line" | sed -E 's/^([^:]+:[0-9]+):[0-9]+ - error ([A-Z0-9]+): (.*)$/\1 — [typecheck] \3 (\2)/'
      done
      ;;
    lint)
      # ESLint/oxlint: /path/file.ts:10:5 error description rule-name
      grep -E ':[0-9]+:[0-9]+ (error|warning)' "$log_file" | while IFS= read -r line; do
        echo "$line" | sed -E 's/^([^:]+:[0-9]+):[0-9]+ (error|warning) (.*)$/\1 — [lint:\2] \3/'
      done
      # Ruff: file.py:10:5: E501 ...
      grep -E '\.py:[0-9]+:[0-9]+: [A-Z][0-9]+' "$log_file" | while IFS= read -r line; do
        echo "$line" | sed -E 's/^([^:]+:[0-9]+):[0-9]+: (.*)$/\1 — [lint] \2/'
      done
      # Clippy: warning: ... --> src/main.rs:10:5
      grep -E '^\s*-->' "$log_file" | while IFS= read -r line; do
        echo "$line" | sed -E 's/^\s*--> ([^:]+:[0-9]+):[0-9]+$/\1 — [lint] clippy warning/'
      done
      ;;
    format)
      # List files that need formatting
      grep -E '\.(ts|tsx|js|jsx|vue|css|json|py|rs|go)' "$log_file" | head -50 | while IFS= read -r line; do
        echo "$line — [format] needs formatting"
      done
      ;;
    test)
      # Vitest/Jest: FAIL src/foo.test.ts > describe > test name
      grep -E '(FAIL|✗|×|FAILED)' "$log_file" | head -30 | while IFS= read -r line; do
        echo "— [test] $line"
      done
      # Pytest: FAILED tests/test_foo.py::test_name
      grep -E '^FAILED' "$log_file" | while IFS= read -r line; do
        echo "$line" | sed -E 's/^FAILED ([^ ]+).*$/\1 — [test] FAILED/'
      done
      ;;
    *)
      # Generic: just include last 20 non-empty lines
      tail -20 "$log_file" | grep -v "^$" | while IFS= read -r line; do
        echo "— [$name] $line"
      done
      ;;
  esac
}

#------------------------------------------------------------------------------
# Generate JSON issues
#------------------------------------------------------------------------------
generate_json_issues() {
  echo "["
  local first=true
  for idx in "${!CHECK_NAMES[@]}"; do
    local name="${CHECK_NAMES[$idx]}"
    local category="${CHECK_CATEGORIES[$idx]}"
    local log_file="$OUTPUT_DIR/${name}.log"

    [[ -f "$log_file" ]] || continue

    parse_issues "$name" "$category" | while IFS= read -r line; do
      local file="" linenum="" msg=""
      if [[ "$line" =~ ^([^:]+):([0-9]+)\ —\ \[([^\]]+)\]\ (.*)$ ]]; then
        file="${BASH_REMATCH[1]}"
        linenum="${BASH_REMATCH[2]}"
        category="${BASH_REMATCH[3]}"
        msg="${BASH_REMATCH[4]}"
      else
        msg="$line"
      fi

      if [[ "$first" == true ]]; then
        first=false
      else
        echo ","
      fi
      printf '  {"file":"%s","line":%s,"category":"%s","message":"%s","check":"%s"}' \
        "$(echo "$file" | sed 's/"/\\"/g')" \
        "${linenum:-0}" \
        "$(echo "$category" | sed 's/"/\\"/g')" \
        "$(echo "$msg" | sed 's/"/\\"/g')" \
        "$name"
    done
  done
  echo ""
  echo "]"
}

#------------------------------------------------------------------------------
# Run all discovery
#------------------------------------------------------------------------------
discover_all() {
  discover_package_json
  discover_python
  discover_rust
  discover_go
  discover_makefile
  discover_pre_commit_hooks
  discover_custom
  discover_env_extra
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
  discover_all

  if [[ ${#CHECK_NAMES[@]} -eq 0 ]]; then
    echo "No checks discovered in $REPO_DIR" >&2
    echo "Supported: package.json, pyproject.toml, Cargo.toml, go.mod, Makefile, .batch-checks.d/, BATCH_CHECKS_EXTRA env" >&2
    exit 255
  fi

  # --discover: dry run
  if [[ "$MODE" == "discover" ]]; then
    echo "Discovered checks for: $REPO_DIR"
    echo ""
    for idx in "${!CHECK_NAMES[@]}"; do
      printf "  %-20s [%-10s] %s\n" "${CHECK_NAMES[$idx]}" "${CHECK_CATEGORIES[$idx]}" "${CHECK_CMDS[$idx]}"
    done
    echo ""
    echo "Total: ${#CHECK_NAMES[@]} checks"
    exit 0
  fi

  # --categories: list categories
  if [[ "$MODE" == "categories" ]]; then
    printf '%s\n' "${CHECK_CATEGORIES[@]}" | sort -u
    exit 0
  fi

  # --- Run mode ---
  echo "batch-checks: $REPO_DIR" >&2
  echo "Discovered ${#CHECK_NAMES[@]} checks" >&2
  echo "" >&2

  # Setup environment
  setup_node

  # Clean output dir
  rm -rf "$OUTPUT_DIR"
  mkdir -p "$OUTPUT_DIR"

  # Run all checks (continue-on-error)
  for idx in "${!CHECK_NAMES[@]}"; do
    run_check "$idx"
  done

  # --- Generate summary.txt ---
  {
    for idx in "${!CHECK_NAMES[@]}"; do
      local name="${CHECK_NAMES[$idx]}"
      printf "%-20s %-6s %s\n" "$name" "${RESULTS[$name]:-SKIP}" "${DURATIONS[$name]:-}"
    done
  } > "$OUTPUT_DIR/summary.txt"

  # --- Generate issues.txt (the primary handoff artifact) ---
  {
    echo "# Issues found by batch-local-checks"
    echo "# Repo: $REPO_DIR"
    echo "# Date: $(date -Iseconds)"
    echo "# Checks run: ${#CHECK_NAMES[@]}, Failed: $FAIL_COUNT"
    echo "#"
    echo "# Format: file:line — [category] description"
    echo ""

    for idx in "${!CHECK_NAMES[@]}"; do
      local name="${CHECK_NAMES[$idx]}"
      local category="${CHECK_CATEGORIES[$idx]}"
      [[ "${RESULTS[$name]}" == "FAIL" ]] || continue

      echo "=== $name ($category) ==="
      parse_issues "$name" "$category"
      echo ""
    done
  } > "$OUTPUT_DIR/issues.txt"

  # --- Generate issues.json ---
  generate_json_issues > "$OUTPUT_DIR/issues.json"

  # --- Print summary to stdout ---
  echo "" >&2
  echo "=== BATCH CHECK RESULTS ===" >&2
  cat "$OUTPUT_DIR/summary.txt" >&2
  echo "" >&2

  if [[ $FAIL_COUNT -gt 0 ]]; then
    echo "$FAIL_COUNT check(s) failed. Issues written to: $OUTPUT_DIR/issues.txt" >&2
    echo "" >&2
    # Print issues.txt to stdout (what the agent or next session reads)
    cat "$OUTPUT_DIR/issues.txt"
  else
    echo "ALL CHECKS PASSED" >&2
    echo "ALL CHECKS PASSED"
  fi

  exit "$FAIL_COUNT"
}

main "$@"
