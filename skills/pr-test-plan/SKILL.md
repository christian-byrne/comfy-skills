---
name: pr-test-plan
description: 'Writes a QA test plan for a single PR — risk-classifies the diff, picks a test target (preview env, local dev server, or desktop build), and writes edge-case-focused cases a non-coding QA tester can execute. Use when asked to write a test plan for a PR, generate QA cases for a change, prepare a PR for QA handoff, or do shift-left QA on a feature before merge.'
interaction: hybrid
type: leaf
synergies:
  requires: []
  enhances: [final-qa-launcher, release-test-plan, reviewing-external-prs]
  conflicts: []
  domain: [qa, verification, testing]
---
# PR Test Plan

Produces a QA test plan scoped to **one PR**, before merge.

This is the shift-left counterpart to `release-test-plan`. That skill plans a whole
version delta; this one plans a single change so the feature can be signed off on its
own PR and **dropped from the release plan**. The case-writing rules are shared — this
skill owns them, and `release-test-plan` references them.

## When to Use

- "Write a test plan for PR #14980"
- "What should QA check on this?"
- Preparing a PR for handoff to the QA team
- Before adding a `preview-*` label, to decide what the preview is actually for
- Called by `final-qa-launcher` as its plan-generation step
- A hot-spot mini plan: a risky diff (per `regression-risk-reviewer`, blame history, or a
  fired post-release signal) needs 3–5 recorder-executable cases before merge — same rules,
  smallest budget, cases written so a test recorder session can replay them verbatim
  (exact UI labels, no judgment steps). See the `post-release` skill graph for how fired
  signals route back into these mini plans.

## Step 1: Gather PR Context

```bash
PR=<N>; REPO=<OWNER/REPO>
gh pr view "$PR" --repo "$REPO" --json \
  title,body,author,baseRefName,headRefName,labels,files,additions,deletions,url
```

**Diff against the real base, not `main`.** For a stacked PR, `gh pr diff` and a
`main` comparison both include the parent's changes, which inflates the plan with
cases that belong to another PR.

```bash
BASE=$(gh pr view "$PR" --repo "$REPO" --json baseRefName -q .baseRefName)
git fetch origin "$BASE" -q
git diff --stat "origin/${BASE}...HEAD"
```

If `$BASE` is not the default branch, say so in the plan header — the tester needs to
know the parent must land first.

## Step 2: Classify What Changed

Read the diff and bucket it. This drives both risk and target selection.

| Signal in diff                                     | Risk | Notes                                        |
| -------------------------------------------------- | ---- | -------------------------------------------- |
| Auth, billing, payment, quota, credit              | HIGH | Test first; test every flag scenario         |
| Data serialization, workflow save/load, migration  | HIGH | Corruption is silent and permanent           |
| Shared render/state path (canvas, graph, store)    | HIGH | Broad blast radius beyond the stated feature |
| Network egress, URL construction, download targets | HIGH | Security-adjacent; check the negative case   |
| New user-facing feature behind a flag              | MED  | Needs the flag ON _and_ OFF                  |
| Isolated UI fix in one component                   | LOW  | 1–2 cases, or fold into a neighbouring item  |
| Pure refactor, no behavior delta                   | LOW  | Usually **no** QA plan — say so and stop     |

If everything lands in the LOW/refactor row, the correct output is "this does not need
a QA pass, automated tests cover it" plus the reason. Do not manufacture cases.

## Step 3: Choose the Test Target

Pick per-case, not per-plan. A single PR often needs two targets.

| Target                                     | Use when                                                    | How                                                        |
| ------------------------------------------ | ----------------------------------------------------------- | ---------------------------------------------------------- |
| Preview env `fe-pr-<N>.testenvs.comfy.org` | Change is cloud-hosted-frontend-specific                    | Add `preview-cpu` (or `preview-gpu`) — see reference below |
| Local dev server                           | Canvas, widgets, node graph, anything distribution-agnostic | `pnpm dev`, or `--front-end-version <repo>@<sha>` on core  |
| Desktop build                              | Desktop-only surface                                        | Release-time artifact only — a preview cannot serve this   |
| Automated only                             | Logic fully covered by unit/e2e                             | Cite the test file; no human case                          |

**A frontend preview is hardcoded `DISTRIBUTION=cloud`.** It cannot cover desktop,
local/core, concurrency, CSP/Turnstile, transactional email, or the services absent
from the ephemeral stack. Read `reference/preview-environments.md` (in
`final-qa-launcher`) before promising a preview covers something.

**Feature flags do not work on preview envs** — `/api/features` is per-environment DB
state seeded once at first boot, and only testcloud/stagingcloud/prod get dynamic
config. Tracked as [BE-6649](https://linear.app/comfyorg/issue/BE-6649). If the change
is dark-launched, either plan against testcloud/staging instead, or note the flag state
the preview is frozen at.

## Step 4: Write the Cases

**Budget: 3–10 checkboxes for a single PR.** More than that means the PR is doing too
much, or you are testing the happy path.

**Audience: QA testers who do NOT read code.** Every case must be actionable from the
UI alone, written as "do X → verify Y", and reproducible without knowing the diff.

**Include setup inline** when a case needs it — "Requires Linux with Wayland", "Start
ComfyUI with `--enable-manager` then disconnect internet", "Create by exporting a
workflow as API then disabling a custom node".

**Use exact UI labels.** "always show advanced widgets", not "show advanced widgets".

**Focus on:**

- Edge cases — empty states, rapid toggling, boundary values
- Integration — interaction with adjacent features
- Persistence — survives reload, tab switch, save/load
- Error recovery — malformed input, network failure, dismiss/retry
- The negative case — for a restriction, verify the thing is actually blocked

**Omit:**

- Happy paths ("verify it opens") — the developer tested this
- Obvious UI checks ("button is visible")
- Anything already covered by automated tests
- Code-internal behaviors a tester cannot observe

**Write cases recorder-ready.** QA executes plans with the test recorder
(`pnpm comfy-test record` in `Comfy-Org/ComfyUI_frontend`), which turns their session
into a committed Playwright test. So each case must read as a start-to-finish app
session — the steps a tester takes from app open to app close, in order, with the
verification stated as something observable on screen. Concretely:

- State the full path, not a fragment: "Open the workflows sidebar → load `default` →
  set seed mode to fixed → run → verify the seed value is unchanged", not "check seed
  stays fixed".
- Name the workflow the case needs (one available in the test corpus — `comfy-test list`
  shows them; local files a tester happens to have will not exist in CI).
- Keep one case = one recordable session. If a case needs two different setups
  (different flag state, different workflow), split it.
- Exceptions are fine where a recorder can't reach (desktop-only surface, email,
  concurrency) — mark those cases as manual.

### Calibration

| ✅ Write this                                                          | ❌ Not this                                               |
| ---------------------------------------------------------------------- | --------------------------------------------------------- |
| Toggle app mode on/off rapidly 5 times — verify no stale render state  | Open app mode — verify it opens correctly                 |
| Close all tabs, reopen browser — verify tabs restore in the same order | Verify V1→V2 tab state pointers migrate correctly         |
| Copy-paste a node with gradients — verify gradient still renders       | Verify `gradient_stops` is enumerable after object spread |
| Disconnect a link — verify the widget returns to normal                | Verify slot metadata clears                               |

## Recorder Setup Block (canonical spec)

This skill owns the recorder-command spec; `release-test-plan` references it. Every
plan section whose cases are recordable gets one copy-pastable command that encodes the
section's full setup. The point: a tester (or the agent supervising them) pastes one
line and the recorder session starts with the right branch, environment, workflow,
tags, and flags — no per-prompt decisions.

**Flag mapping** — each setup answer in the recorder maps 1:1 to a CLI flag:

| Setup decision    | Flag                        | Values / notes                                                                                                   |
| ----------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Environment       | `--distribution <id>`       | `cloud` (testcloud.comfy.org), `cloud-staging` (stagingcloud.comfy.org), `cloud-prod` (cloud.comfy.org), `local` |
| Ephemeral backend | `--backend <url>`           | Custom/ephemeral backend proxy target; implies custom distribution — do not combine with `--distribution`        |
| PR under test     | `--pr <number>`             | Checks out the PR branch before starting the dev server                                                          |
| Workflow          | `--workflow <name>`         | Must exist in the test corpus (`comfy-test list`)                                                                |
| Tags              | `--tags <a,b>`              | From the registered tag set (`comfy-test tags`)                                                                  |
| Feature flags     | `--feature-flags <k:v,...>` | Bare key = true; auto-appends `?ff=` URL params and seeds them into the generated test                           |
| Test-plan step    | `--use-case test-plan-step` | Routes the recorder's questions to test-plan phrasing                                                            |
| Case description  | `--description "<text>"`    | Paste the case text                                                                                              |
| Test name         | `--name <slug>`             | Optional; recorder can derive it                                                                                 |

**Template** (fill per section; drop flags the section doesn't need):

```bash
pnpm comfy-test record --pr {N} --distribution cloud --workflow {workflow} \
  --tags {tags} --feature-flags {flag:true} --use-case test-plan-step \
  --description "{section title}"
```

**Feature flags: use `?ff=` URL params, not localStorage dev overrides.** URL params
are session-scoped (no cross-test corruption), work on cloud, and are what
`--feature-flags` generates (`?ff=key` for true, `?ff=key:value` otherwise). Only fall
back to dev overrides for flags the URL mechanism doesn't support, and say so in the
plan. Remember flags are frozen on preview envs (BE-6649, Step 3).

**Standard plan frontmatter.** Every published plan opens with:

1. A 2–3 sentence non-technical intro: what the recorder is, that any recorded session
   becomes a real automated test, and that low-polish contributions are welcome —
   maintainers refactor them.
2. A "Learn more" link to the Test Recorder CLI Runbook (features in plain language,
   the three usage flows, glossary):
   `https://www.notion.so/comfy-org/3c76d73d3650817d8d31e4bdaf96ab9b`
3. One-time setup: clone/checkout, `pnpm install`, and a recommendation to use
   `comfy-cli` for managing ComfyUI instances alongside the recorder.
4. A collapsed **"Prompt for agents"** block: full instructions for an agent
   supervising a human through the plan (run `comfy-test guide` first, never show raw
   shell beyond the one paste-able command, plain-language phrasing), ending with a
   link back to the plan page itself.

**Canonical "Prompt for agents" copy.** Paste this into the collapsed block verbatim,
filling `{plan-url}` (and adjusting repo paths if the plan targets a different repo).
Do not rewrite it per plan — consistency is the point:

```text
You are helping a person run through a QA test plan. Assume they are not a
developer — never assume technical knowledge, and never show raw shell output
or multi-command instructions.

Setup (do it for them where you can; otherwise give ONE command at a time):
1. Ensure the ComfyUI_frontend repo exists locally and is up to date. If not,
   help them clone it and run `pnpm install`. Recommend `comfy-cli` for
   managing ComfyUI instances alongside the recorder.
2. Run `pnpm comfy-test guide` first — it explains the tool in plain language.
3. For each test-plan section, give them that section's single recorder
   command from its "Recorder setup" toggle. That one paste-able line (run in
   a separate terminal from this chat) is the only shell they should see.

While they record:
- Explain plainly: "the recorder watches what you do in the app and turns it
  into an automated test."
- Their only job is to perform the steps like a real user. They never judge
  code quality — maintainers refactor everything. There is no such thing as a
  bad or embarrassing recording; every contribution is valuable.
- Sign in BEFORE recording starts; never type passwords while recording.
- Avoid jargon: say "check that ..." instead of "assertion", "the app version
  being tested" instead of "branch" or "distribution".
- Long silent steps (refactor/PR generation) are normal — tell them it can
  take up to 10 minutes and summarize what changed when it finishes.

After each section, confirm what was recorded, then move to the next section.
Test plan: {plan-url}
```

**Length control:** in Notion, put each section's recorder command and any setup detail
inside a toggle block so the plan body stays scannable.

## Step 5: Format

```markdown
# QA Test Plan — {PR title}

{Standard plan frontmatter — see "Recorder Setup Block"}

**PR:** https://github.com/{owner}/{repo}/pull/{N}
**Author:** @{author}
**Base:** `{baseRefName}` {"— stacked, #{parent} must land first" if not default}
**Target:** {preview URL | local dev server | both, per case}
**Risk:** {HIGH|MEDIUM|LOW} — {one-line why}

**How to report issues:** Comment on the PR, or reply in the #qa thread.

## {Feature area}

▸ Recorder setup (toggle): `pnpm comfy-test record --pr {N} ...`

- ☐ {case}
- ☐ {case}

## Cannot be covered here

- {surface} — {why, and where it must be tested instead}
```

Formatting rules: no blank line between a heading and its checkboxes, or between
consecutive checkboxes; one blank line between groups. No author tags in the body. No
horizontal dividers. Keep it compact.

The "Cannot be covered here" section is not optional when the target is a preview env.
It is what keeps the residue visible to the release plan.

## Step 6: Hand Off

Present the plan and ask: **"Publish to Notion and draft the #qa post? (yes / adjust / local only)"**

On yes, follow the team process in `final-qa-launcher` → "Requesting QA" — create the
Notion task, assign it, and draft the #qa message. Do not post to Slack without
explicit confirmation of the final text.

## Anti-Patterns

- ❌ **Diffing against `main` on a stacked PR** — you will write cases for the parent's code
- ❌ **Manufacturing cases for a pure refactor** — say it needs no QA and stop
- ❌ **Promising a preview covers desktop or local** — it is `DISTRIBUTION=cloud`, always
- ❌ **Planning flag-gated behavior on a preview env** — flags are frozen at first boot (BE-6649)
- ❌ **Omitting the "cannot be covered" section** — the release plan needs to know the residue
- ❌ **Code-internal cases** — if a tester cannot observe it from the UI, it is not a QA case
- ❌ **Posting to #qa without confirmation** — always show the final text first

## Parent Graph

Part of: `quality`. Case-writing rules are shared with `release-test-plan`.
