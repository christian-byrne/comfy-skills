# Customization

## Repo-Specific Overrides

If a `.final-sweep.yaml` exists in the repo root, it overrides defaults:

```yaml
# .final-sweep.yaml
skip:
  - bundle-size # no frontend
  - terraform # no infra
  - license-check # internal project

custom_checks:
  - name: 'migration-test'
    command: 'pnpm dev:migrate && pnpm test:integration'
    condition: 'db/migrations changed'
    group: 1

follow_up_labels:
  - 'follow-up'
  - 'tech-debt'

require_changelog: false
require_agents_md: true
```
