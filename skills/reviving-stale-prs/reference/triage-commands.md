# Triage Commands Reference

## 1. Fetch PR Metadata

```bash
PR_NUMBER=<N>
REPO="<OWNER/REPO>"

PR_DATA=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json \
  title,body,author,createdAt,updatedAt,state,isDraft,mergeable,\
  headRefName,baseRefName,additions,deletions,changedFiles,\
  labels,assignees,reviewDecision,reviews,comments,\
  headRepository,headRepositoryOwner)
```

Extract key signals:

- **Age**: days since creation and last update
- **Author activity**: last comment date, whether author responded to reviews
- **Size**: additions + deletions + changed files
- **Review state**: approved, changes requested, or no reviews
- **Draft status**: still marked as draft?
- **Fork status**: is `headRepositoryOwner` different from the repo owner? (affects push strategy)

**Important:** Always use `author.login` for API calls, assignments, and @-mentions. Never use `author.name` or display names — they don't resolve correctly in GitHub API calls.

## 2. Check for Superseding Work

This is the most common reason to close rather than revive. Dispatch these checks in parallel when possible:

### 2a. Code Existence Check

Do the files and functions this PR touches still exist on `main`?

```bash
PR_FILES=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json files --jq '.files[].path')

for FILE in $PR_FILES; do
  # Does the file still exist?
  git show origin/main:"$FILE" > /dev/null 2>&1 || echo "DELETED: $FILE"

  # Was it renamed/moved?
  git log --oneline --diff-filter=R --find-renames --since="$PR_CREATED" origin/main -- "$FILE"
done
```

### 2b. Already-Landed Check

Search for merged PRs AND closed PRs that cover the same change. Closed PRs are critical — a maintainer may have attempted the same fix and abandoned it due to regressions.

```bash
PR_CREATED=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json createdAt -q .createdAt)

# Check file modifications on main since PR was opened
for FILE in $PR_FILES; do
  git log --oneline --since="$PR_CREATED" origin/main -- "$FILE"
done

# Search merged AND closed PRs for overlapping work
TITLE_KEYWORDS=$(echo "$PR_TITLE" | tr ' ' '\n' | grep -v '^[a-z]\{1,3\}$' | head -5 | tr '\n' ' ')
gh pr list --repo "$REPO" --state merged --search "$TITLE_KEYWORDS" --limit 10
gh pr list --repo "$REPO" --state closed --search "$TITLE_KEYWORDS" --limit 10

# Search commits that reference this area
git log --oneline --grep="$TITLE_KEYWORDS" --since="$PR_CREATED" origin/main
```

### 2c. Semantic Overlap Analysis

When candidate superseding PRs are found, don't just note they exist — compare their diffs against this PR's diff:

```bash
# Get this PR's diff
gh pr diff "$PR_NUMBER" --repo "$REPO" > /tmp/stale-pr.diff

# Get the candidate superseding PR's diff
gh pr diff "$CANDIDATE_PR" --repo "$REPO" > /tmp/candidate.diff

# Compare: which files overlap? Which changes are unique to the stale PR?
diff <(grep '^[+-]' /tmp/stale-pr.diff | sort) <(grep '^[+-]' /tmp/candidate.diff | sort)
```

Report:

- Which parts of the stale PR were fully absorbed by merged work
- Which parts (if any) remain **uniquely valuable** and unaddressed
- If 100% absorbed → CLOSE. If partial → note the remaining value explicitly.

### 2d. Deprecation & Architectural Shift Check

```bash
# Check for deprecation markers
grep -r "@deprecated" -- $(echo "$PR_FILES" | head -20)
grep -i "deprecated\|removed" CHANGELOG.md 2>/dev/null

# Check for directory reorganization (renames/moves)
git log --oneline --diff-filter=R --find-renames --since="$PR_CREATED" origin/main -- $(echo "$PR_FILES" | head -20)

# Check if feature is still documented
for FILE in $PR_FILES; do
  BASENAME=$(basename "$FILE" | sed 's/\..*//')
  grep -ri "$BASENAME" docs/ 2>/dev/null | head -3
done
```

### 2e. Team Decisions Check

Search for prior team decisions about this feature area in issues and discussions:

```bash
# Search issues for related decisions
gh issue list --repo "$REPO" --state all --search "$TITLE_KEYWORDS" --limit 10

# Search for discussions referencing these files/features
gh api "repos/$REPO/issues?state=all&per_page=20&q=$TITLE_KEYWORDS" \
  --jq '.[].title' 2>/dev/null
```

Look for comments from maintainers that indicate a deliberate decision (e.g., "we decided not to do this because…"). These are strong CLOSE signals.

### Bail-Out Criteria

- A merged PR already implements the same change → close with reference
- A closed PR shows the same approach was tried and abandoned due to regressions → close with reference
- The files were heavily refactored/moved and the PR's approach is now incompatible → close with explanation
- A newer open PR covers the same scope → close as duplicate
- Team explicitly decided against the approach in an issue/discussion → close with reference

## 3. Check Author Engagement

```bash
# Last activity from the PR author
AUTHOR=$(echo "$PR_DATA" | jq -r '.author.login')
gh pr view "$PR_NUMBER" --repo "$REPO" --json comments \
  --jq "[.comments[] | select(.author.login == \"$AUTHOR\")] | last | .createdAt"

# Check author's recent GitHub activity
gh api "users/$AUTHOR" --jq '{login, updated_at, bio}' 2>/dev/null
```

**Signals:**

- Author responded to all review comments → engaged, worth reviving
- Author went silent after review feedback → may need to adopt
- Author self-approved their own PR → external contributor, needs careful review
- Last activity >6 months with unaddressed reviews → likely abandoned
- Author's GitHub account is inactive/deleted → adopt or close

Note the engagement level but don't bail out on this alone — docs PRs and small fixes from external contributors are often worth adopting even if abandoned.
