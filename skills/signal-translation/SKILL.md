---
name: signal-translation
description: 'Translating a fired release signal into concrete actions via a signal-class × severity decision table: regression test, reporter reach-out, repro, risk row, QA pull-in, support brief, fix-forward, backport, patch release, or canary width change. Thresholds live as reviewable YAML. Use when a post-release signal fired and you must decide the response, or when defining WATCH/STOP/ROLLBACK thresholds for a rollout.'
interaction: hybrid
type: leaf
synergies:
  enhances: [post-release, backport-management, pr-test-plan, crash-triage]
  domain: [release, incident, triage, thresholds]
---
# Signal Translation

A signal that fires and produces only a Slack message is wasted. Every fired signal gets mapped
through severity bands to one or more actions from a fixed menu, so the response is a routing
decision, not an improvisation.

## When to Use

- A telemetry threshold crossed, a community report cluster formed, or a test fleet regressed
- Defining thresholds before a rollout stage begins
- Auditing whether past signals actually produced actions

## Severity Bands

Three bands, defined per signal **before** the rollout starts, with numbers:

| Band         | Meaning                                  | Default posture                                                                                                                           |
| ------------ | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **WATCH**    | Above baseline noise, below harm         | Hold current exposure; investigate; do not widen                                                                                          |
| **STOP**     | Sustained or user-harming                | Freeze rollout; war room if multi-signal — see the war-room protocol in the parent `post-release` skill; fix-forward or backport decision |
| **ROLLBACK** | Data loss, security, or unrecoverable UX | Execute the pre-written rollback; comms out                                                                                               |

A threshold is (signal, baseline, level, sustain-window). "Error count > 3,500/day for 2
consecutive days against a baseline of 2,660 ± 260" is a threshold; "errors look high" is not.

## The Action Menu

Every response is one or more of these ten. Name them explicitly in the routing record.

| #   | Action              | When                                      | Executed via                                                                        |
| --- | ------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------- |
| 1   | Regression test     | Any confirmed repro                       | Test recorder / E2E suite; the bug becomes a permanent test                         |
| 2   | Reporter reach-out  | Report lacks version/repro/steps          | Ask on the original channel; community etiquette in `../community-testers/SKILL.md` |
| 3   | Build repro         | Signal is real but unreproduced           | Assign a repro owner before assigning a fix owner                                   |
| 4   | Program risk row    | Pattern may recur or worsen               | Risk ledger, with detection signal + contingency                                    |
| 5   | QA pull-in          | Area needs human exploration              | Targeted mini test plan (`pr-test-plan` skill)                                      |
| 6   | Support brief       | Users will see it before the fix ships    | Brief support with symptom, workaround, timeline                                    |
| 7   | Fix-forward         | Low-risk fix, next release soon           | Normal PR flow, tagged to the signal                                                |
| 8   | Backport            | Stable users affected, next release far   | `backport-management` skill                                                         |
| 9   | Patch release       | Backport lands and severity ≥ STOP        | Release process; patch-release hook in `backport-management`                        |
| 10  | Canary width change | Signal ambiguity needs more/less exposure | `../staged-rollout/SKILL.md` promote/pause criteria                                 |

Routing heuristics:

- STOP-band + confirmed repro → almost always {1, 7-or-8, 6 if user-visible}.
- WATCH-band + no repro → {3, 2}; escalate to STOP only with attribution.
- Any signal that survives triage gets action 1 eventually — the loop's compounding value is
  that every real incident becomes a permanent test.
- One report with version + repro + regression window outranks ten vague complaints.

## Thresholds as Reviewable YAML

Keep thresholds in a YAML file in the program workspace so changes are diffs, not folklore.
Template at `reference/thresholds-template.yaml` (relative to this skill). Generic structure
lives here in ttp; each program workspace carries its own populated copy with real numbers.

## Routing Record

Every fired signal appends one record wherever the program keeps operational logs:

```
signal: <source + metric/report>
band: WATCH|STOP|ROLLBACK   evidence: <link, baseline, window>
attribution: <version/change, or "unattributed">
actions: [<menu numbers>]   owners: [<named>]   follow-up: <date>
```

Unattributed STOP-band signals escalate to the program decision queue with a default-if-silent —
never sit on them waiting for attribution.
