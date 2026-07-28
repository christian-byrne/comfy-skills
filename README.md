# comfy-skills

Agent skills for [Claude Code](https://claude.com/claude-code), Codex, and
friends — the source behind the listings on
[tools.comfy.org](https://tools.comfy.org).

> **This repository is generated.** Every file here is written by a sync job from
> a source repo. Hand edits are destroyed on the next run. To change a skill,
> change it upstream and let the sync republish it.

## Install one

```bash
git clone https://github.com/christian-byrne/comfy-skills /tmp/comfy-skills \
  && cp -r /tmp/comfy-skills/skills/<skill-name> ~/.claude/skills/<skill-name>
```

## Install all

```bash
git clone https://github.com/christian-byrne/comfy-skills /tmp/comfy-skills \
  && cp -r /tmp/comfy-skills/skills/* ~/.claude/skills/
```

## Layout

```
skills/<skill-name>/SKILL.md      the skill itself
skills/<skill-name>/scripts/      executable helpers, when a skill ships them
skills/<skill-name>/references/   deep-dive material the skill loads on demand
.toolbox-sync-state.json          sync bookkeeping — content hashes, listing URLs
```

## Reporting a problem

Open an issue here. Fixes land upstream and flow back on the next sync, so a PR
against this repo can't be merged — the sync would overwrite it.
