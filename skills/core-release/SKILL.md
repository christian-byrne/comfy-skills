---
name: core-release
description: 'Cut a core ComfyUI frontend release (PyPI + desktop/self-host) via the biweekly workflow. Covers the requirements.txt-pin resolver, tag-before-publish ordering, skipping dead minors, and the release-done verification that backport-merged is NOT shipped. Use when publishing a core frontend version, running the biweekly release, bumping the ComfyUI pin, or verifying a core release actually reached users.'
interaction: agent
type: leaf
---

# Core Frontend Release (PyPI + desktop / self-host)

Cuts a **core** ComfyUI frontend release — the version that lands on PyPI as
`comfyui-frontend-package` and gets pinned by ComfyUI's `requirements.txt`, reaching
desktop and self-host users. This is a **stateful, non-idempotent, hard-to-reverse**
pipeline (a published PyPI version cannot be replaced). Read every step before firing
anything.

> **The #1 lesson from 1.47:** _backport-merged ≠ released._ Core `v1.47.9` was
> published to PyPI while our entire QA fix set (19 commits) sat unreleased past the
> tag — desktop/self-host users got a version advertised as fixed that wasn't, forcing
> a `1.47.10` re-cut. "The backport merged" is **not** a terminal state. Nothing but a
> manual `git rev-list` caught it. Run the [release-done verification](#release-done-verification)
> before any "shipped" claim.

## When to Use

- Publishing a new core frontend version to PyPI
- Running the biweekly release for a `core/X.Y` line
- Bumping / verifying the ComfyUI `requirements.txt` pin
- Confirming a core release actually reached users (not just merged)

## When NOT to Use

- Cloud (`cloud.comfy.org`) deploys → your cloud deploy process / `cloud-branch-rotation`
- Cherry-picking fixes onto a release branch → `comfyui-backport-management`

## Single-Writer Rule

Release ops (tag, PyPI publish, pin PR) are stateful and non-idempotent. **One thread
owns core-release execution at a time.** Two agents mutating the same release artifact
risk double-actions or masking each other's failures — in 1.47 one thread reported
"rotation succeeded" while live infra said the opposite. Before firing any workflow,
confirm no other thread is mid-release. "Done" for any step is a **live-state read-back**
(published tag, PyPI version, pin file), never the acting thread's claim.

## The biweekly resolver keys off ComfyUI's pin — pass `target_branch` explicitly

The biweekly release workflow resolves _which minor to release_ from **ComfyUI's current
`requirements.txt` pin**, not from what you intend. In 1.47, with the pin at `1.45.20`,
`release_type=minor` resolved to **core/1.46, not core/1.47**. Unless you override the
target, the resolver will pick the wrong minor.

**Always pass `target_branch` explicitly** so the resolver cannot guess wrong:

```bash
# Read scripts/cicd/resolve-comfyui-release.ts + the workflow's dispatch inputs BEFORE
# the first fire of a cycle, and state the expected resolved version/branch first.
gh workflow run release-biweekly-comfyui.yaml \
  --repo Comfy-Org/ComfyUI_frontend \
  --field release_type=patch \
  --field target_branch=core/1.47
```

- State the **predicted** resolved version/branch _before_ firing, then check the actual
  output against that prediction. The bump PR is human-reviewable — but only if actually
  reviewed. Do not fire-and-trust.
- **Skip dead minors by targeting the branch directly.** 1.46 was a dead version they did
  not want in ComfyUI's `requirements.txt` at all. Do **not** hack a temporary 1.46 pin to
  "step through"; the release workflow supports a manual version override, so the pin jumps
  `1.45.21 → 1.47.10` directly. Target `core/1.47` and skip 1.46 entirely.

## Tag-before-publish ordering

The publish is a **no-op if the tag doesn't exist yet** (a `1.47.10` run fired before the
tag was cut left PyPI on `1.47.9`). The correct order:

1. Merge the `Release`-labeled version-bump PR into `core/X.Y` (e.g. `#14029` "1.47.10"
   bumps `package.json`).
2. `release-draft-create` builds the **tag** + npm types package.
3. **Only then** publish PyPI + open the ComfyUI `requirements.txt` pin PR.

A publish run fired **before the tag exists is a no-op** — PyPI stays on the previous
version. Confirm the tag exists (`gh release view vX.Y.Z` / `git ls-remote --tags`) before
triggering or trusting a publish.

## Recovery / gotchas (from the 1.47.10 run)

The biweekly (`release-biweekly-comfyui.yaml`) chains `resolve-version →
trigger-release-if-needed → publish-pypi → create-comfyui-pr` in **one** run. Two failure
modes hit in 1.47.10 — neither means the release is lost:

### `publish-pypi` hard-fails on the tag-wait timeout — merge the bump PR promptly

`publish-pypi`'s first step (_"Wait for release PR to be created and merged"_) polls for
tag `v<target_version>` for **30 min (60 × 30s) and then `exit 1`s**. That tag is only
created by `release-draft-create` **when the `Release`-labeled bump PR merges** — which
needs a human. If the bump PR hasn't merged inside 30 min, `publish-pypi` **fails**, and
because `create-comfyui-pr` has `needs: publish-pypi` (+ `if: needs.publish-pypi.result ==
'success'`) it is **skipped** — so both the PyPI publish _and_ the ComfyUI pin PR are lost
from that run. In 1.47.10 the first biweekly run failed exactly this way.

**Merge the `Release`-labeled bump PR promptly after firing the biweekly**, or expect to
recover (below).

### Clean recovery: `gh run rerun <run-id> --failed` on the SAME biweekly run

Once the tag exists (bump PR merged), recover by **re-running the failed jobs of the same
biweekly run** — do **not** fire a fresh biweekly:

```bash
# After the bump PR has merged and tag v<target> exists:
gh run rerun <biweekly-run-id> --repo Comfy-Org/ComfyUI_frontend --failed
```

`--failed` reuses the already-resolved `target_version` from `resolve-version` (that job
already succeeded and is not re-run), so `publish-pypi` + `create-comfyui-pr` complete with
**no re-resolve and no risk of a spurious next-patch bump**. A _fresh_ biweekly, by
contrast, re-runs `resolve-version` and can resolve/bump to the **next** patch — avoid it
for recovery. (In 1.47.10 the rerun-failed of run `29979988134` finished the publish + pin
PR cleanly.)

### A `release-draft-create` "failure" can be purely cosmetic — check the jobs

`release-draft-create.yaml`'s `comment_release_summary` job (_"Post release summary
comment"_, a `peter-evans/create-or-update-comment`-style local action) has **no
`continue-on-error`**, so if that comment-poster crashes (a Node error did in 1.47.10) the
**whole run is marked `failure`** — even though `build`, `draft_release`, and
`publish_types` all succeeded (tag cut, GH release created, npm types published). **Don't
panic on a draft-create "failure": open the run and check the individual jobs** before
concluding the tag/release didn't happen.

### Core releases are published non-latest — verify they don't override real latest

`draft_release` sets `make_latest` to `true` **only** when the PR base is `main` and it's
not a prerelease; for a `core/X.Y` base it resolves to `false`. So a core release is
published **`draft=false` and non-latest** (`make_latest=false`, GH `made_latest` stays
`null`/false) — it is a real, immediately-published release, **not** a draft to "publish
later" (the older runbook's "publish the draft" framing was wrong for core). Verify the
core release's **`made_latest` stays null/false** (`gh release view vX.Y.Z --json
isLatest`) so it does not steal `latest` from the true newest line (e.g. `v1.48.x`).

## Release-Done Verification

**Run this before any "shipped / released" claim.** Backport-merged, and even
tag-created, is not enough — the tag / PyPI / pin must actually contain the commits.
Assert **all four**, from a freshly-fetched checkout (see below):

```bash
REPO=Comfy-Org/ComfyUI_frontend
BRANCH=core/1.47
TAG=v1.47.10          # the version you claim shipped
EXPECT=1.47.10
git fetch origin --tags --quiet

# (a) Every intended fix's CONTENT is present on origin/<branch>.
#     Use patch-id or file-content marker — NEVER raw SHA ancestry (squash-merge
#     rewrites SHAs, so an ancestry test lies — it produced a false RELEASE-CRITICAL
#     alarm in 1.47). Patch-id compares the change itself:
want=$(git show <fix-sha-on-main> | git patch-id --stable | awk '{print $1}')
git log "origin/${BRANCH}" --format=%H | while read -r c; do
  git show "$c" | git patch-id --stable | awk '{print $1}'
done | grep -qx "$want" && echo "present" || echo "MISSING on ${BRANCH}"
#     Pragmatic equivalent when you know the changed line — check file content directly:
git show "origin/${BRANCH}:<path>" | grep -q "<marker>" && echo "present" || echo "MISSING"

# (b) Nothing our release should contain sits PAST the tag.
git rev-list "${TAG}..origin/${BRANCH}" --count   # MUST be 0

# (c) PyPI 'latest' == expected version.
curl -s https://pypi.org/pypi/comfyui-frontend-package/json | jq -r '.info.version'  # == $EXPECT

# (d) ComfyUI's requirements.txt pin == expected version.
curl -s https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/requirements.txt \
  | grep comfyui-frontend-package   # == comfyui-frontend-package==$EXPECT
```

If (b) is non-zero, commits are unreleased past the tag — **the fixes are not shipped**;
cut the next patch. If (c) or (d) lag, the pin PR hasn't merged / PyPI hasn't updated —
still not shipped.

**Worked example — 1.47.10 (all four green):** `git rev-list v1.47.10..origin/core/1.47
--count == 0`; PyPI `.info.version == 1.47.10`; npm `@comfyorg/comfyui-frontend-types@1.47.10`
published; ComfyUI pin PR `Comfy-Org/ComfyUI#15045` (`requirements.txt`
`1.45.21 → 1.47.10`, base `master`). That is what "shipped" looks like.

## Pinned / fresh reference checkout

Correctness reads (the verification above, any file-existence claim) MUST come from a
**freshly-fetched worktree of the exact target branch** — never a long-lived checkout. In
1.47 a stale local checkout (646 commits behind, wrong branch) silently served May-11 code
and produced a phantom "lost bug." `git fetch origin` at the start of the session and
confirm HEAD is on the expected branch and not behind before trusting any read.

## Release-line CI is not a signal

Backport-branch CI reports **`skipping`** — build/deploy/chromatic/review workflows are
gated to main/PR-target conditions and don't run on release branches. A green-looking
backport PR has **no real CI signal**; local `typecheck/unit/lint/format` at cherry-pick
time are the only gates. Don't read a "green" release-branch PR as "tested by CI."

## Related

- Manual PyPI publish: fall back to your project's manual publish command/script if the
  automated pipeline needs a manual assist.
- Backporting fixes onto `core/X.Y`: `comfyui-backport-management`
- The QA loop that feeds this release: `cloud-release-qa-loop`
