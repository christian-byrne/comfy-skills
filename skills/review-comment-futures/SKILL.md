---
name: review-comment-futures
description: 'Predict whether review comments will be accepted, pushed back on, or ignored. Track calibration over time. Use after posting external PR reviews, or when asked to score predictions, check calibration, or run review-comment-futures.'
interaction: hybrid
type: leaf
---

# Review Comment Futures

Predict the fate of each review comment you post on external PRs. Track calibration over time. Turn code review into deliberate practice.

## Prediction Step (After Posting)

After posting review comments on an external PR, annotate each with a prediction:

### 1. For Each Posted Comment, Predict

```
Comment #1: src/parser.ts:128 — suggestion: split assumes no delimiter
  Prediction: [accept / pushback / ignore]
  Confidence: [0.0–1.0]
  Rationale: (one sentence — why you expect this outcome)
```

**Outcome definitions:**

| Outcome    | Signal                                                                  |
| ---------- | ----------------------------------------------------------------------- |
| `accept`   | Author resolves thread, makes the change, or replies agreeing           |
| `pushback` | Author replies disagreeing, explains why they won't change, or debates  |
| `ignore`   | No response after PR closes — comment was not addressed or acknowledged |

### 2. Log Each Prediction

Append one JSONL line per comment to `telemetry/review-comment-futures.jsonl`:

```bash
REPO="owner/repo"
PR=42
cat >> telemetry/review-comment-futures.jsonl <<EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","repo":"$REPO","pr":$PR,"comment_id":$COMMENT_ID,"file":"src/parser.ts","line":128,"label":"suggestion","prediction":"accept","confidence":0.7,"rationale":"minor style nit, author usually receptive","actual":null,"scored_at":null}
EOF
```

### 3. Commit the Predictions

```bash
git add telemetry/review-comment-futures.jsonl
git commit -m "chore: log review-comment-futures predictions for $REPO#$PR"
```

## Scoring

After the PR closes (merged or abandoned), score your predictions:

```bash
bash scripts/score-review-futures.sh                    # Score all unscored
bash scripts/score-review-futures.sh --pr owner/repo#42 # Score one PR
bash scripts/score-review-futures.sh --stats             # Calibration report
bash scripts/score-review-futures.sh --dry-run           # Preview without writing
```

The script classifies outcomes by checking each comment's review thread via GitHub API:

- Thread has reply from PR author agreeing or thread resolved → `accept`
- Thread has reply from PR author disagreeing → `pushback`
- No reply from PR author and thread not resolved after PR closed → `ignore`

After scoring, commit the updated file.

## Calibration Report (`--stats`)

```
Review Comment Futures — Calibration Report
============================================
Total predictions: 23  |  Scored: 18  |  Pending: 5

Accuracy: 72% (13/18)

Per-outcome breakdown:
  accept:    predicted 10, actual 9,  precision 78%, recall 87%
  pushback:  predicted 4,  actual 5,  precision 75%, recall 60%
  ignore:    predicted 4,  actual 4,  precision 67%, recall 67%

Brier score: 0.21 (lower is better, 0 = perfect calibration)

Confidence calibration:
  High (>0.8):  predicted 8,  correct 7  (88%)
  Medium (0.5-0.8): predicted 7, correct 4 (57%)
  Low (<0.5):   predicted 3,  correct 2  (67%)
```

## When to Use

- **After every external PR review** — add predictions before moving on
- **Weekly** — run `--stats` to check calibration trends
- **Before reviewing** — glance at past accuracy to calibrate your commenting style

## Anti-Patterns to Watch For

If calibration reveals patterns:

- **High ignore rate** → comments are noise; be more selective
- **High pushback rate** → framing needs work; try questions over directives
- **Overconfident on pushback** → you're projecting disagreement; re-read the PR more charitably
- **Low confidence but high accuracy** → trust your instincts more
