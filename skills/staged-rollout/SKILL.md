---
name: staged-rollout
description: 'Sequencing a release through exposure stages — nightly channel, canary percentage, flag cohorts, full release — with promote/pause/rollback criteria per stage. Use when planning how a release reaches users, deciding whether to widen a canary, choosing flag cohorts, or writing the promote/rollback runbook for a release.'
interaction: hybrid
type: leaf
synergies:
  enhances: [rollout-gates, post-release]
  domain: [release, rollout, canary, feature-flags]
---
# Staged Rollout

Load `rollout-gates` first — it owns the generic discipline (readiness criteria per stage,
observation windows, stop conditions, the point of no return). This skill binds that discipline
to concrete release-channel mechanics.

## When to Use

- Planning the stage sequence for a release
- Deciding whether to promote, pause, or roll back a stage
- Choosing which cohort mechanism fits a change (channel, traffic %, flag group)

## The Standard Ladder

Each stage exists to answer a question the previous stage could not. Skipping a stage means
accepting its question unanswered.

| Stage                  | Mechanism                                     | Population                        | Question it answers                                            |
| ---------------------- | --------------------------------------------- | --------------------------------- | -------------------------------------------------------------- |
| 1. CI + pre-release QA | test suites, QA plan                          | none (synthetic)                  | Does it work at all?                                           |
| 2. Nightly channel     | auto-built from main; opt-in community        | hundreds–thousands of enthusiasts | Does it survive real workflows and real machines?              |
| 3. Internal/eng target | a nightly deployment URL for the team         | the team                          | Can QA execute the full plan against it?                       |
| 4. Canary              | sticky-session traffic split on prod infra    | ~5–15% of real users              | Does it hold at real scale, on real data, with real telemetry? |
| 5. Flag cohort         | feature flag auto-enabled for an opt-in group | latest/beta channel users         | (For flagged features) same as canary, scoped to the feature   |
| 6. Full release        | stable channel, all users                     | everyone                          | Nothing — by now you should already know                       |

Notes on the mechanisms:

- **Nightly channel**: users opt in via an explicit version pin (for example, a CLI flag such as
  `--front-end-version` that pins a specific frontend build). Signal from this population is
  high-value but dirty — see `../signal-ingest/SKILL.md` for collection, and
  `../community-testers/SKILL.md` for growing the population.
- **Canary on shared infra**: route a percentage of real traffic with sticky sessions (a session
  cookie at the load balancer) so a user stays on one version. Sticky sessions make user-visible
  breakage attributable; a per-request split does not.
- **Flag cohorts**: a feature merged but disabled by default, auto-enabled for a pre-release
  channel group, is a second canary scoped to the feature. Ship risky features this way so the
  release and the feature can fail independently.

## Per-Stage Contract

For every stage, write down before entering it:

1. **Entry criteria** — what must be green (cite verification-surface rows, not prose).
2. **Observation window** — minimum soak time AND minimum traffic. A quiet weekend proves less
   than a quiet weekday; a canary spanning a weekend needs the following weekday too.
3. **Promote criteria** — the specific metrics at or under baseline, named dashboards checked,
   named owner who reads them.
4. **Pause criteria** — WATCH-level thresholds (see `../signal-translation/SKILL.md`): hold the
   stage, widen investigation, do not widen exposure.
5. **Rollback plan** — the actual command/procedure, who runs it, and the point past which
   rollback stops being clean (schema migrations, data written by the new version).

## Compressing Stages Under Deadline

When the calendar forces compression, prefer _simultaneous release with a longer prior canary_
over skipping the canary: hold the previous stable an extra cycle, canary the new version over
the gap, then release all channels at once. All users move together, attribution stays clean,
and support hears one story instead of two.

## Multi-Change Releases

Two significant changes in one release destroys attribution ("users can't load X — which change
did it?"). If both must ship in one version, put the riskier one behind a flag (stage 5) so the
signal streams separate. Record the pairing as a program risk with a detection signal.

## Anti-Patterns

- A percentage schedule with no per-stage questions — that is a calendar, not a rollout plan.
- Widening a canary because time passed rather than because promote criteria were met.
- A rollback plan discovered during the incident.
- Treating "merged behind a flag" as "released" in status reports — exposure is what counts.
