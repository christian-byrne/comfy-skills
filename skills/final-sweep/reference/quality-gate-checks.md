# Group 1: Code Quality Gates — Detailed Checks

**Dispatch as parallel subagents.** Each subagent runs one check, reports pass/fail + details.

**Skip any check already green in CI or recently run.**

## Auto-detect which checks apply

```bash
# Node ecosystem
HAS_NODE=$([ -f package.json ] && echo 1)
HAS_ESLINT=$([ -f .eslintrc* ] || [ -f eslint.config.* ] || jq -e '.devDependencies.eslint // .dependencies.eslint' package.json >/dev/null 2>&1 && echo 1)
HAS_PRETTIER=$([ -f .prettierrc* ] || jq -e '.devDependencies.prettier // .dependencies.prettier' package.json >/dev/null 2>&1 && echo 1)
HAS_TYPESCRIPT=$([ -f tsconfig.json ] && echo 1)
HAS_STYLELINT=$([ -f .stylelintrc* ] || jq -e '.devDependencies.stylelint' package.json >/dev/null 2>&1 && echo 1)

# Rust
HAS_RUST=$([ -f Cargo.toml ] && echo 1)

# Python
HAS_PYTHON=$([ -f pyproject.toml ] || [ -f setup.py ] && echo 1)

# Shell
HAS_SHELL=$(find . -maxdepth 3 -name '*.sh' -not -path './node_modules/*' 2>/dev/null | head -1 | grep -q . && echo 1)

# GitHub Actions
HAS_ACTIONS=$([ -d .github/workflows ] && echo 1)

# Terraform
HAS_TERRAFORM=$([ -d terraform ] && echo 1)

# SQL
HAS_SQL=$(find . -maxdepth 3 -name '*.sql' -not -path './node_modules/*' 2>/dev/null | head -1 | grep -q . && echo 1)

# Docker
HAS_DOCKER=$([ -f Dockerfile ] || [ -f Dockerfile.* ] && echo 1)
```

## Checks (run applicable ones in parallel)

| #   | Check                  | Condition                                | Command Pattern                                                       |
| --- | ---------------------- | ---------------------------------------- | --------------------------------------------------------------------- |
| 1   | **Tests pass**         | Any repo                                 | `pnpm test` / `cargo test` / `pytest` / `go test ./...` / `make test` |
| 2   | **Lint**               | `HAS_ESLINT`                             | `pnpm lint` / `eslint .`                                              |
| 3   | **Format**             | `HAS_PRETTIER`                           | `pnpm format:check` / `prettier --check .`                            |
| 4   | **Typecheck**          | `HAS_TYPESCRIPT`                         | `pnpm typecheck` / `tsc --noEmit`                                     |
| 5   | **Stylelint**          | `HAS_STYLELINT`                          | `pnpm stylelint`                                                      |
| 6   | **Shellcheck**         | `HAS_SHELL`                              | `shellcheck <files>`                                                  |
| 7   | **Actionlint**         | `HAS_ACTIONS`                            | `actionlint`                                                          |
| 8   | **SQL format**         | `HAS_SQL`                                | `sql-formatter --check` or repo-specific                              |
| 9   | **Terraform fmt**      | `HAS_TERRAFORM`                          | `terraform fmt -check -recursive terraform/`                          |
| 10  | **Terraform validate** | `HAS_TERRAFORM`                          | `terraform validate`                                                  |
| 11  | **JSON/YAML lint**     | Config files changed                     | `jsonlint` / `yamllint` on changed files                              |
| 12  | **Clippy**             | `HAS_RUST`                               | `cargo clippy --workspace`                                            |
| 13  | **Rust fmt**           | `HAS_RUST`                               | `cargo fmt --all -- --check`                                          |
| 14  | **Ruff**               | `HAS_PYTHON`                             | `ruff check .` / `ruff format --check .`                              |
| 15  | **Security scan**      | Any repo                                 | `gitleaks detect --no-git` on diff                                    |
| 16  | **Dependency audit**   | `HAS_NODE` or `HAS_RUST` or `HAS_PYTHON` | `pnpm audit` / `cargo audit` / `pip-audit`                            |
| 17  | **License compliance** | Any repo                                 | Check for GPL deps in MIT/Apache projects                             |
| 18  | **Dead code**          | `HAS_TYPESCRIPT` or `HAS_RUST`           | `knip` / unused exports in diff                                       |
| 19  | **Bundle size**        | Frontend with build                      | Compare bundle size before/after                                      |

## Report format per subagent

```
[PASS] lint — 0 errors, 0 warnings
[FAIL] typecheck — 3 errors in 2 files (see details)
[SKIP] terraform — no terraform files changed
```
