---
name: release-test-plan
description: Generates a risk-prioritized QA test plan for a release. Analyzes git history between versions, filters non-user-facing and already-backported changes, groups into compact test items, writes edge-case-focused test cases for QA testers, and publishes to Notion. Use when preparing a release, writing a test plan, doing release QA, or asked to create a test plan for a version.
interaction: autonomous
type: leaf
---

# Release Test Plan Generator

Creates a compact, risk-prioritized QA test plan from git history between two versions. Output is a Notion page with flat feature-grouped test checkboxes that QA testers can execute without code knowledge. This is a general RC test plan — not specific to any single distribution (cloud, desktop, local).

## When to Use

- Preparing a release
- Writing QA test plans for a version bump
- Creating a test plan for a patch release
- Asked to "make a test plan" or "write QA for the release"

## Inputs Required

Ask the user for:

1. **Target version** (e.g., `1.42`)
2. **Previous version / base** (e.g., `1.41`, or auto-detect from tags)
3. **Release branch** (e.g., `cloud/1.42`, or `main`)
4. **Notion parent page/database ID** (ask before publishing)

## Process

### Step 1: Gather Commits

```bash
git fetch origin
git log origin/${BASE}..origin/${TARGET} --oneline --no-merges --first-parent --format="%s"
```

For each commit with a `(#NNNN)` suffix, extract the PR number. For backport commits (`[backport ...]` prefix), extract the **original** PR number (first `#NNNN` in the title), not the backport PR number.

### Step 2: Filter Non-User-Facing Changes

Remove entries with these prefixes (case-insensitive):

- `test:`, `docs:`, `ci:`, `dx:`, `chore:`, `refactor:`, `style:`, `draft:`

Also remove:

- Version bump commits (e.g., `1.42.0 (#NNNN)`)
- Storybook-only story additions
- Screenshot regeneration
- Lint/format rule changes, CI pipeline fixes
- Mock factories, test utilities, perf test infra
- Internal renames without behavior change
- Telemetry-only PRs (analytics events, PostHog config, GTM tags)
- Internal tooling (codegen, agent skills, Sentry breadcrumbs)
- Icon safelist additions
- Performance metric additions that don't change user-visible behavior
- Component extractions / refactors with no UI change (e.g., "extract SeedControlButton")
- PrimeVue → custom component swaps where the UI is identical (e.g., ColorPicker replacement)

### Step 3: Filter Already-Backported PRs

**Critical step — do not skip.** Compare ALL remaining PR numbers against what's already on the base branch:

```bash
# Get every PR number referenced in the base branch
git log origin/${BASE} --oneline --format="%s" | grep -oP '#\d+' | tr -d '#' > /tmp/base_prs.txt

# For each PR in the test plan, check if it's already on base
while read -r pr; do
  if grep -qw "$pr" /tmp/base_prs.txt; then
    echo "ALREADY SHIPPED: $pr"
  fi
done < /tmp/testplan_prs.txt
```

Remove any PR that appears on the base branch — it was already tested in a prior patch release.

For backport bot PRs (e.g., `comfy-pr-bot`), resolve the **real author** from the original PR's commit metadata:

```bash
gh pr view $PR --repo $REPO --json commits --jq '.commits[0].authors[0].login'
```

### Step 4: Group Related PRs

Target: **20–40 total test items** (not raw PRs).

Consolidation rules:

- **Feature series**: All PRs for one feature → single item
- **Same component**: PRs touching the same UI area (e.g., "mask editor", "asset browser")
- **Fix-follows-feat**: Bug fixes merged into the feature group
- **Stacked PRs**: Multiple PRs on the same component

Group by **feature area**, NOT by author.

### Step 5: Categorize

Split items into flat sections by feature area (e.g., "Subgraphs", "App Mode", "Canvas"). No nested heading levels — just bold feature titles directly under the page level.

### Step 6: Risk-Prioritize

Order items from highest to lowest risk.

**High Risk** (test first):

- Core systems (rendering, data serialization, state management)
- Broad impact (shortcuts, navigation, primary workflows)
- Complex state (undo/redo, multi-selection, concurrent editing)

**Low Risk** (test last or drop):

- Isolated UI fixes
- Additive-only changes (new optional feature, no existing behavior changed)
- Drop the bottom ~20% lowest-risk items entirely
- Drop items that are purely visual/cosmetic and low-risk (carousel cycling, tooltip on hover, color picker rendering)

### Step 7: Write Test Cases

**Budget**: 60–100 total checkboxes across all items. 1–4 per item.

**Audience**: QA testers who do NOT read code. Every test case must be:

- Actionable from the UI alone (no code references, no internal variable names)
- Written as "do X → verify Y" with concrete steps
- Reproducible without knowing the PR or implementation details

**Include reproduction context when needed**: If a test requires special setup, add it inline:

- "Requires Linux with Wayland"
- "Requires disabling clipboard access in browser settings"
- "Start ComfyUI with `--enable-manager` and then disconnect internet"
- "Can create by exporting as API a workflow then disabling a custom node"
- Include sub-steps for multi-step verifications (e.g., "Do again but by clicking X and verify Y")

**Use actual setting names**: Reference the exact setting label as it appears in the UI, not a paraphrased version. E.g., "always show advanced widgets" not "show advanced widgets".

**Focus on**:

- Edge cases (empty states, rapid toggling, boundary values)
- Integration (interaction with other features)
- Persistence (survives reload, tab switch, save/load)
- Error recovery (malformed input, network failure, dismiss/retry)

**Omit**:

- Happy paths ("verify it opens") — the developer tested this
- Obvious UI checks ("button is visible")
- Anything already covered by automated tests
- **Code-internal behaviors** that a QA tester can't observe or verify:
  - "verify slot metadata clears" → instead: "disconnect a link — verify widget returns to normal"
  - "verify deep watcher removal reduces overhead" → just test perf directly
  - "verify widget.inputEl backward compatibility" → developer concern, not QA
  - "verify gradient_stops survives object spread" → instead: "paste a node with gradients — verify gradient still renders"
  - "verify V1 tab state migrates to V2" → instead: "reload — verify tabs restore"
- **Purely internal migration/refactoring concerns** that result in no observable behavior change
- **Component swap tests** where old and new look identical (user can't tell the difference)

**Quality calibration**:

- ✅ "Toggle app mode on/off rapidly 5 times — verify no stale render state"
- ❌ "Open app mode — verify it opens correctly"
- ✅ "Close all tabs, reopen browser — verify tabs restore in the same order"
- ❌ "Verify V1→V2 tab state pointers migrate correctly"
- ✅ "Copy-paste a node with gradients — verify gradient still renders"
- ❌ "Verify gradient_stops is enumerable after object spread"

### Step 8: Format for Notion

**Header** — general RC test plan format, not distribution-specific:

```markdown
**Test Targets:**

- **For things specific to cloud/staging**: {staging_url}
- For things specific to local/desktop: `--front-end-version {repo}@{version}`
- For general things: use discretion / either distribution

**How to report issues**: Tag the author of the associated PRs for details or report in Slack in associated QA thread

**Base**: {base_version} → **Target**: {target_version}

**Stats**: {N} PRs analyzed, {M} already-backported filtered → {X} items, {Y} test cases
```

**Body structure** — flat, compact, no section headings:

```markdown
**Feature Title** ([#PR1](url), [#PR2](url))

- ☐ Edge case test 1
- ☐ Integration test 2

**Another Feature** ([#PR3](url))

- ☐ Persistence test

**Cloud-Specific**

**Cloud Feature** ([#PR4](url))

- ☐ Cloud test 1
```

**Formatting rules**:

- **No blank lines** between a feature title and its checkboxes
- **No blank lines** between consecutive checkboxes
- **One blank line** between feature groups (bold title blocks)
- **No author grouping** — group by feature area only
- **No @author tags** in the document body
- **No section headings** (H2/H3) for general items — only use bold text headings for "Cloud-Specific" section separator
- Use `to_do` blocks for checkboxes when Notion API supports them
- **Do NOT** use `<details><summary>` HTML
- **Do NOT** use horizontal dividers
- Keep the plan **compact** — minimal whitespace
- When Notion MCP inserts unwanted blank lines between blocks, this is a known limitation — note it but don't fight it

### Step 9: Publish to Notion

If a Notion database/page ID is provided, create the page, then append blocks.

**Notion MCP limitations**: The MCP tool may only support `paragraph` and `bulleted_list_item` block types. If so:

- Use bold paragraphs for section headers
- Use `bulleted_list_item` with "☐ " prefix for checkboxes
- Known issue: the MCP adds a blank line between every block — this can't be fixed from the API side. The user may need to manually clean up spacing in Notion.

**CRITICAL**: Never modify a Notion page the user says they are editing or have edited. If they paste content, that is the source of truth — do not overwrite it.

> **Triage test items:** Before publishing to Notion, share the draft item list
> with QA leads so they can accept, skip, or reprioritize — publishing only the
> agreed set keeps the plan focused.

### Step 10: Present for Review

Show the user:

1. Summary stats: total PRs, backported filtered, total items, total test cases
2. The full test plan
3. Ask: "Publish to Notion?" / "Adjust anything?"

## Output format — the standard QA test-plan structure

This is the canonical shape of the deliverable. Prefer it whenever the release
gates behavior on env/flags or ships more than a trivial patch. The Notion flat
format above is a compact fallback; this fuller Markdown structure is the
source-of-truth format the team relies on for real releases.

### Skeleton

```markdown
# QA Test Plan — {distribution} {base_version} → {target_version} [{note e.g. "skipping 1.46"}]

**Prepared for:** QA team
**Deploy:** {env} (currently on `{base_branch}` tip `{base_sha}`) → `{target_branch}` tip `{target_sha}`
**This ships {N} minor(s)/patch(es} at once.** Test {each / this} delta.

## Test Targets

- **Cloud / staging (default for cloud-specific items):** {staging_url}
- Local / desktop (general canvas & node items): `--front-end-version {repo}@{version}`
- General items: use discretion / either distribution

**How to report issues:** Tag the PR author or post in the release QA Slack thread.

## Feature-flag scenarios (run cloud items under EACH where noted)

<!-- Include this section ONLY when a flag gates behavior. -->

The `{flag}` flag is ON for `{cohort}`. {What forks on it.}

1. **`{flag}` ON + {context A}** — {behavior}. {Why it's the highest-value target.}
2. **`{flag}` ON + {context B}** — {behavior}.
3. **`{flag}` OFF** — legacy path. Must still work.

**Dev override to force the flag in a session:** in browser console run
`localStorage.setItem('ff:{flag}_enabled','false')` then reload. (Set to `'true'` to force on.)

---

## Summary — the version delta(s)

| Delta     | Range                         | New commits (patch-id filtered)                           | Headline changes |
| --------- | ----------------------------- | --------------------------------------------------------- | ---------------- |
| **{ver}** | `{base_sha}..origin/{branch}` | **{N}** ({M} already-shipped patches filtered from {raw}) | {headline list}  |

> Note: prod diverged from `{line}` at `{tag}`. Counts use `--cherry-pick` so commits already
> backported to the prod line are excluded.

---

## Risk classification

**HIGH** (auth / billing / payment / data — test first, all flag scenarios):

- {item} ({PR refs})

**MEDIUM** (new features / UI behavior):

- {item} ({PR refs})

**LOW** (copy / telemetry / tests / website — smoke only or skip):

- {item}

---

## HIGH RISK — {Feature Area} (#PR, #PR, #issue)

{One line of context / why this is high risk.}

- ☐ **Scenario 1 (flag ON + X):** {concrete UI steps} — verify {observable expected result} (#PR)
- ☐ {multi-step user journey with a mid-flow perturbation} — verify {result} (#PR)

## MEDIUM — {Feature Area} (#PR, #PR)

- ☐ {UI steps} — verify {result} (#PR)

## LOW RISK — smoke only or skip

- ☐ {spot-check} (skip deep testing)

---

## Regression sanity checklist (always-critical paths — run before sign-off)

- ☐ App loads at {url} with no console errors on a fresh session
- ☐ Load the default workflow and run it end-to-end — verify a valid output
- ☐ Change a setting, reload — verify it persisted
- ☐ Save a workflow, reload the tab — verify it restores
- ☐ Log out and back in — verify identity, credits, and assets reload under the correct scope
- [ ] other basic user flows / journeys here… (QA experts: extend)
```

### Required elements (checklist)

- ☐ **Header block**: Prepared-for, Deploy line with `from → to` SHAs (and branch tips), one line on what ships.
- ☐ **Test Targets**: which env/distribution each class of item belongs to.
- ☐ **How to report issues**: PR author tag or the QA Slack thread.
- ☐ **Feature-flag scenarios** — include only when a flag gates behavior: the run matrix (each scenario) plus the `localStorage.setItem('ff:{flag}_enabled', …)` dev-override snippet.
- ☐ **Summary table of the delta(s)**: range, new-commit count that is **patch-id / `--cherry-pick` filtered** so already-shipped work is excluded, and headline changes.
- ☐ **Risk classification** into HIGH / MEDIUM / LOW, each with its one-line rule:
  - HIGH = auth / billing / payment / data → test first, all flag scenarios.
  - MEDIUM = new features / UI behavior → test.
  - LOW = copy / telemetry / tests / website → smoke only or skip.
- ☐ **Per-area sections grouped by feature**, each header carrying the relevant **PR/issue refs**, containing `- [ ]` / `☐` checkbox cases written as concrete **UI steps + expected result** (never code internals).
- ☐ **Regression sanity checklist** of always-critical paths at the end.

### Practice notes (bake these in)

- **Exclude already-shipped-on-prior-line work.** The prod line often diverged from the release line; use `--cherry-pick` and patch-id filtering so backported commits are not re-counted or re-tested. This is the most commonly missed step.
- **Exclude website / subrepo changes** — those deploy separately. Note them under LOW at most, don't write cases for them.
- **Deep-dive the highest-risk PRs.** For each HIGH item, write many concrete cases plus multi-step **user journeys** (navigate rapidly post-login, throttle the network mid-confirm, toggle a flag mid-session, etc.), not one happy-path line.
- **Add a custom-node lens** where relevant: does the change touch entity callbacks, `node.widgets`, serialization, or group-node → subgraph migration? Add a "load an old / custom-node workflow — verify no crash" case.
- **End open-ended.** Close the plan with a trailing `- [ ] other basic user flows / journeys here…` bullet so QA experts can extend it.
- **Write for QA who don't read code** — concrete UI actions and observable results only; keep the "Omit" / code-internal exclusions from Step 7.

## Notes

- For **major releases**, the commit range is large — be aggressive with grouping
- For **patch releases**, the range is small — can be more granular
- Always verify the base tag/branch is correct before generating
- The backport filter is the most commonly missed step — always do it thoroughly by checking each PR number against the base branch's full commit log
- QA testers don't know the codebase — write test cases as user-facing actions, never reference internal code structures
- Present the plan to the user for review BEFORE publishing to Notion
- Include reproduction context for tests that need special setup (OS, flags, browser settings, etc.)
- Use exact UI setting names, not paraphrased versions
- Drop cosmetic/visual-only items that don't merit QA time (carousel animations, tooltip hovers, color picker swaps)

## ComfyUI-Specific Context

When generating test plans for **ComfyUI frontend releases** (`Comfy-Org/ComfyUI_frontend`), apply the following additional context.

### High-Risk Systems (ComfyUI-specific)

- **LiteGraph** — canvas rendering, node connections, graph serialization
- **Node execution** — prompt queueing, caching, interrupts
- **Workflow management** — save/load, undo/redo, subgraphs
- **Keybindings** — global shortcuts, canvas shortcuts
- **Sidebar** — node library, workflow browser, model browser
- **App Mode** — builder, widget rendering, output display

### Release Branches

- Cloud releases: `cloud/X.XX`
- Core releases: `core/X.XX`

### Cloud-Specific Features to Categorize Separately

- Subscription tiers, billing, GCS storage
- Cloud-only UI (account settings, usage dashboard)
- API nodes (partner integrations)
- ComfyHub publish wizard

### Documents Hub (Notion)

Test plans go in the Notion database/page ID provided in the Inputs Required step.

- Set **Category** = "Test Plan"
- Set **Status** = "To Do"

### Section Categories

Typical sections (use as needed, drop empty ones):

- Subgraphs & Nested Subgraphs
- App Mode
- Workflow Management
- Canvas & LiteGraph
- Queue & Execution
- Widget System
- Missing Models & Errors
- Asset Browser
- Node Library
- Mask Editor
- Performance
- Cloud-Specific
- UI Polish

### Example Notion Pages

Refer to previously published test plans in your team's Notion workspace for format examples.

### Additional Reproduction Context (ComfyUI-specific)

- "Start ComfyUI with `--enable-manager` and then disconnect internet" — for missing models with registry offline
- "Can create by exporting as API a workflow then disabling a custom node used in it" — for API format workflow tests
- "Requires editing workflow metadata → find a loader node → add model metadata specifying a nested folder" — for nested model path tests

### Additional Non-User-Facing Filters (ComfyUI-specific)

Beyond the generic filters, also remove:

- Sentry breadcrumb additions
- PostHog/Mixpanel/GA4 telemetry-only PRs
- Firebase auth gate internals (unless login flow is affected)
- Icon safelist additions
- Preview variant defaults
- Internal error logging enrichment
- PrimeVue → custom component swaps where the UI behavior is unchanged
- Performance metric collection (TBT, frameDuration, CDP metrics) — unless perf is testable by user
