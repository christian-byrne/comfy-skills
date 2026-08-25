---
name: community-testers
description: 'Recruiting and running community testers on pre-release builds — Discord/Reddit asks, version-pin install instructions, structured feedback capture, and tester-relations etiquette. Use when a release needs more real-world testing signal, when drafting a tester recruitment post, or when converting community feedback into actionable reports.'
interaction: hybrid
type: leaf
synergies:
  enhances: [post-release]
  domain: [community, testing, release, developer-relations]
---
# Community Testers

A nightly channel with thousands of users produces almost no structured signal on its own.
Testers must be recruited, given a one-command way in, asked specific questions, and thanked.
The difference between a passive nightly population and an active tester community is whether
anyone asked.

## When to Use

- A release stage needs more real-world coverage than QA can produce
- Drafting recruitment posts for Discord/Reddit/forums
- Community feedback is arriving but unusable (no versions, no repros)

## Recruitment

Post where the enthusiasts already are (project Discord, subreddit, forum). The ask must contain:

1. **What to test** — the specific feature areas or workflows at risk this release, not
   "try the nightly". Derive from the release test plan's risk areas.
2. **How to get on the build** — the exact opt-in command. When the product supports pinning a
   component version (e.g. a `--front-end-version <build>` style flag), give the full command
   line with the exact build id, copy-pasteable.
3. **How to report** — one canonical destination (usually the issue template), with the version
   field filled. Explicitly say screenshots + workflow files beat prose.
4. **The window** — when feedback stops being actionable ("we promote Thursday").

**Draft posts are staged, never auto-sent.** Write them into the program workspace's staged-
drafts file for a human to post. Agents do not post to community channels.

## Install-Instruction Hygiene

- One copy-paste block per platform. Every extra step halves participation.
- State how to get back to stable (the un-opt-in command) — fear of being stuck is the top
  objection.
- State known issues in the build up front so they aren't re-reported.

## Feedback Capture

Route everything to `../signal-ingest/SKILL.md` conventions:

- Chat reports are ephemeral: an owner converts promising ones into tracked issues with
  provenance links, or asks the reporter to file with the template.
- Always capture the version. If the tracker template has a version field with a dummy default,
  a defaulted answer means "ask again".
- Reach-outs (asking a reporter for more detail) are part of the loop, not a favor — a report
  with version + repro outranks ten vague ones, so upgrading vague reports is high-leverage.

## Etiquette

- Close the loop publicly: when a tester's report leads to a fix, say so in the channel where
  they reported it. This is what converts one-time reporters into standing testers.
- Never argue with a wrong report; ask for the workflow file.
- Do not ask the community to test what CI could catch — spend human testers on judgment,
  hardware diversity, and real workflows.
