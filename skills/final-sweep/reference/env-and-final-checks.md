# Group 7: Environment & Config

**Run sequentially. Only if relevant changes detected.**

| #   | Check                        | Condition                                 | How                                                          |
| --- | ---------------------------- | ----------------------------------------- | ------------------------------------------------------------ |
| 66  | **New env vars documented**  | Diff adds `process.env.*` or `os.environ` | Check `.env.example`, README, deployment docs                |
| 67  | **Secrets in vault**         | Diff adds API keys, tokens, credentials   | Verify they're in secret manager, not hardcoded              |
| 68  | **Config defaults safe**     | New config values added                   | Verify defaults are fail-closed (paused, low limits, strict) |
| 69  | **Terraform plan clean**     | `HAS_TERRAFORM` + infra changes           | `terraform plan` shows only expected changes                 |
| 70  | **DB migrations reversible** | New migration files                       | Can the migration be rolled back safely?                     |
| 71  | **Docker build works**       | Dockerfile changed                        | `docker build` succeeds                                      |

# Group 8: Final Verification

**Run last, sequentially.**

| #   | Check                | How                                                                   |
| --- | -------------------- | --------------------------------------------------------------------- |
| 72  | **Fresh test run**   | One final test run after all changes are committed                    |
| 73  | **Full diff review** | Read `git diff origin/main..HEAD` one more time — any surprises?      |
| 74  | **Scope check**      | Did we ONLY do what was asked? No scope creep? No drive-by refactors? |
| 75  | **Worktree cleanup** | Is this worktree still needed after merge? Note for user.             |
