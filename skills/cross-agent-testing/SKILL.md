---
name: cross-agent-testing
description: 'Test skills end-to-end across all supported agent tools (Claude Code, Codex, OpenCode, Gemini CLI). Launch agents in tmux, observe, diagnose failures, fix skills/hooks, re-test. Use when told to cross-agent test, test a skill across agents, or verify multi-tool compatibility.'
interaction: interactive
type: leaf
synergies:
  requires: [tmux]
  domain: [testing, multi-agent, cross-tool]
---

# Cross-Agent Testing

Test skills end-to-end across all supported AI coding tools. Iterative loop: launch agent in tmux → observe → diagnose → fix skills/hooks/prompts → re-test → repeat.

## Requirements

- `tmux`, and the CLIs for whichever agents you're testing (`claude`, `codex`, `opencode`, `gemini`, etc.)
- A way to spin up an isolated worktree per agent/skill combo — the commands below assume a `wt-new`/`wt-rm`-style helper; substitute plain `git worktree add`/`git worktree remove` if you don't have one
- Any API keys/env vars the agent CLIs need, available in your shell before launching

## Installed Tools

| Agent           | Binary     | Launch Command                                                                                                 | Autonomous Flag                              |
| --------------- | ---------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| **Amp**         | `amp`      | `amp`                                                                                                          | Already autonomous                           |
| **Claude Code** | `claude`   | `claude --dangerously-skip-permissions`                                                                        | `--dangerously-skip-permissions`             |
| **Codex**       | `codex`    | `codex --full-auto`                                                                                            | `--full-auto` (still has 4+ startup prompts) |
| **OpenCode**    | `opencode` | `bash -c 'opencode run --dir DIR --dangerously-skip-permissions --model anthropic/claude-sonnet-4-6 "PROMPT"'` | `--dangerously-skip-permissions`             |
| **Gemini CLI**  | `gemini`   | `bash -c 'cd DIR && gemini'`                                                                                   | Interactive (trust + shell approval)         |

## Workflow

### 1. Setup — Create worktrees per agent per skill

```bash
SKILL="repo-audit"  # substitute the skill under test
for AGENT in claude codex opencode gemini; do
  wt-new <repo> "xtest-${AGENT}-${SKILL}"
done
```

### 2. Launch — One tmux window per agent

```bash
tmux new-session -s crosstest -d 2>/dev/null || true

for AGENT in claude codex opencode gemini; do
  WT="$WORKTREE_BASE/<repo>/xtest-${AGENT}-${SKILL}"
  tmux new-window -t crosstest -n "xtest-${AGENT}" -d 2>/dev/null || true
done

# Claude Code
tmux send-keys -t "crosstest:xtest-claude" \
  "cd $WORKTREE_BASE/<repo>/xtest-claude-${SKILL} && claude --dangerously-skip-permissions" C-m

# Codex
tmux send-keys -t "crosstest:xtest-codex" \
  "cd $WORKTREE_BASE/<repo>/xtest-codex-${SKILL} && codex --full-auto" C-m

# OpenCode
tmux send-keys -t "crosstest:xtest-opencode" \
  "cd $WORKTREE_BASE/<repo>/xtest-opencode-${SKILL} && opencode" C-m

# Gemini CLI
tmux send-keys -t "crosstest:xtest-gemini" \
  "cd $WORKTREE_BASE/<repo>/xtest-gemini-${SKILL} && gemini" C-m
```

Then send the skill prompt to each:

```bash
tmux send-keys -t "crosstest:xtest-claude" "use-skill: ${SKILL}" C-m
tmux send-keys -t "crosstest:xtest-codex" "use-skill: ${SKILL}" C-m
# etc.
```

### 3. Observe — Capture pane output

```bash
for AGENT in claude codex opencode gemini; do
  echo "=== $AGENT ==="
  tmux capture-pane -p -S -500 -t "crosstest:xtest-${AGENT}" 2>/dev/null || echo "(not running)"
  echo
done
```

For Claude Code, also check session JSONL:

```bash
# Find latest session
ls -t ~/.claude/projects/*/sessions/*.jsonl 2>/dev/null | head -1
```

### 4. Diagnose — Classify failures

| Category                 | Description                             | Example                              |
| ------------------------ | --------------------------------------- | ------------------------------------ |
| `skill-not-found`        | Agent can't locate the skill            | Codex has no skill directory         |
| `tool-name-mismatch`     | Agent doesn't have the expected tool    | No `handoff` in Codex                |
| `permission-blocked`     | Sandbox or safety check blocks action   | Bubblewrap in Codex                  |
| `hook-protocol-mismatch` | Hook wire format differs                | Stdin/stdout encoding                |
| `missing-context`        | Agent lacks AGENTS.md or MCP            | Gemini reads GEMINI.md not AGENTS.md |
| `git-safety-violation`   | Agent works on main or shared dir       | Missing worktree setup               |
| `handoff-missing`        | Agent lacks handoff/delegation          | Codex can't fire-and-forget          |
| `wrong-quality-commands` | Agent uses wrong lint/test commands     | `npm test` instead of `pnpm test`    |
| `interactive-prompt`     | Agent waits for user input unexpectedly | API key prompt, trust prompt         |
| `cwd-reset`              | Agent resets working directory          | Claude Code resets after each bash   |

### 5. Fix — Apply smallest fix

Priority order:

1. Add "Cross-Agent Notes" section to the skill's SKILL.md
2. Add a hook adapter or script in your project's hooks directory, if it has one
3. Add a prompt adapter in your project's prompts directory, if it has one
4. Document as agent limitation (won't fix)

**All fixes go in this repo** — never in global `~/.claude/skills/` or system files.

### 6. Re-test — Fresh worktree, re-launch

```bash
# Remove old worktree
wt-rm <repo> "xtest-${AGENT}-${SKILL}"
# Create fresh one
wt-new <repo> "xtest-${AGENT}-${SKILL}"
# Re-launch
```

### 7. Record — Learnings

If your project tracks run history, append a result line somewhere durable, e.g.:

```bash
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"'"$AGENT"'","skill":"'"$SKILL"'","outcome":"success|failure|partial","failure_category":"'${CATEGORY:-}'","failure_detail":"'${DETAIL:-}'","fix_applied":"'${FIX:-}'","duration_minutes":'${DURATION:-0}'}' \
  >> logs/cross-agent-runs.jsonl
```

Adjust the destination to wherever your project keeps this kind of log.
