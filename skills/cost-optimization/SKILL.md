---
name: cost-optimization
description: 'Reduces costs across two dimensions: cloud infrastructure (AWS/Azure/GCP/OCI rightsizing, reserved capacity, governance) and AI token consumption (markdown token efficiency, file bloat, verbose documentation). TRIGGERS: reduce cloud spending, optimize costs, rightsizing, reserved instances, spot instances, budget alert, cost governance, reduce tokens, token bloat, optimize markdown, shrink SKILL.md, file too large for AI'
type: leaf
synergies:
  domain: [cloud, cost, ai, infrastructure, documentation]
---

# Cost Optimization

Two-domain cost reduction: **cloud infrastructure** and **AI token consumption**.

## Cloud Infrastructure

### Optimization Pillars

1. **Visibility** — tag resources, set budget alerts, build cost dashboards, enable anomaly detection
2. **Rightsizing** — analyze utilization, downsize over-provisioned resources, remove idle instances, enable auto-scaling
3. **Pricing models** — reserved instances (30–72% savings on AWS), spot/preemptible, savings plans, committed-use discounts (GCP: up to 57%)
4. **Architecture** — managed services over self-hosted, caching layers, lifecycle policies for tiered storage, minimize data transfer

### Cloud-Specific Handles

| Cloud | Tool                           | Notes                                  |
| ----- | ------------------------------ | -------------------------------------- |
| AWS   | Cost Explorer, Trusted Advisor | Reserved Instances, Savings Plans      |
| Azure | Cost Management                | Hybrid Benefit for Windows/SQL         |
| GCP   | Billing export → BigQuery      | Committed Use Discounts (1yr/3yr)      |
| OCI   | Cost Analysis                  | Flexible shapes + preemptible capacity |

### Checklist (run periodically)

- [ ] Unused resources terminated
- [ ] Over-provisioned instances resized
- [ ] Reserved/committed capacity reviewed
- [ ] Storage lifecycle policies applied
- [ ] Data transfer patterns audited
- [ ] Budget alerts configured

## AI Token Consumption

Applies to SKILL.md files, prompts, and any markdown consumed by agents.

### Workflow

1. **Count** — estimate tokens (~4 chars = 1 token), report per-file totals
2. **Scan** — find: emojis, verbose prose, duplication, large code blocks, nested lists
3. **Suggest** — table with: location | issue | fix | estimated savings
4. **Summary** — current / potential / savings, top 3 recommendations

### Targets

- SKILL.md: < 500 tokens
- Reference docs: < 1000 tokens

### Common Anti-Patterns

| Anti-pattern          | Fix                                |
| --------------------- | ---------------------------------- |
| Emoji decoration      | Remove unless load-bearing         |
| Repeated preamble     | Extract to frontmatter description |
| Verbose step prose    | Collapse to imperative bullets     |
| Redundant examples    | Keep one canonical example         |
| Nested bullet overuse | Flatten or use a table             |

**Rule:** suggest only — never auto-modify. Preserve clarity in all optimizations.

## Sources

- [wshobson/agents/cost-optimization](https://skills.sh/wshobson/agents/cost-optimization) — cloud infrastructure cost optimization patterns
- [microsoft/github-copilot-for-azure/markdown-token-optimizer](https://skills.sh/microsoft/github-copilot-for-azure/markdown-token-optimizer) — AI token efficiency for markdown files
