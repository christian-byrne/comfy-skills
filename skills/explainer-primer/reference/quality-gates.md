# Quality gates — what the script checks, and the two things it cannot

Editorial standards that live only in someone's head get skipped under time pressure. Most of the
ones here are machine-checked, so "did we hold the bar" is a command rather than an argument.

## The automated audit

```bash
python3 skills/explainer-primer/scripts/primer.py --dir <primer-dir> check
```

Read-only. Prints a per-page table and exits non-zero on any failure.

| Check                                   | Severity | Catches                                                      |
| --------------------------------------- | -------- | ------------------------------------------------------------ |
| Parenting                               | fail     | Hub not under the design doc; a chapter that escaped the hub |
| Page not empty                          | fail     | A create that never got content                              |
| No leaked literal markdown              | fail     | `[text](url)` rendered as text — the recursive-emphasis bug  |
| No unresolved `{{slug}}`                | fail     | A cross-link to a slug that is not in `series`               |
| Nav footer present                      | fail     | A page you can navigate into but not out of                  |
| Diagram on every chapter                | fail     | A wall of prose with no dual coding                          |
| Hub subpage count                       | fail     | A chapter that failed to publish                             |
| Hub links every page                    | fail     | A page reachable only by URL                                 |
| Entry point present and at position ≤ 2 | fail     | A front door nobody will scroll to                           |
| Published block count ≥ local           | warn     | A truncated render                                           |
| Orientation callout                     | warn     | A chapter with no "where you are / what you'll learn"        |
| Check-yourself section                  | warn     | A chapter with no retrieval practice                         |

Pages marked `"reference": true` in `primer.json` (glossary, FAQ, index) are exempt from the
chapter-only checks.

**The audit has earned its keep.** On its first run against a finished-looking 18-page series it
found a chapter with no diagram — the longest page in the set, all prose and tables — and a
bold-swallowed link. Both looked fine in review.

## Judgement check 1 — calibrate style against the corpus, not a generic rule

Generic AI-writing guidance caps em dashes at about 1 per 1000 words and flags a word list
(`delve`, `leverage`, `robust`, `seamless`, …). Apply it blindly and you can make a document read
_less_ like its team, not more.

Measure the surrounding docs first:

````bash
python3 - <<'EOF'
import re, glob
def stat(paths, label):
    w = d = 0
    for p in glob.glob(paths):
        t = re.sub(r"```.*?```", "", open(p).read(), flags=re.S)
        w += len(t.split()); d += t.count("—")
    print(f"{label:28} {w:6d} words  {1000*d/max(w,1):5.1f} em-dashes/1k")
stat("CONTEXT.md", "house style")
stat("AGENTS.md", "house style")
stat("reports/primer/pages/*.md", "the primer")
EOF
````

If the team's own docs run at 15 per 1000 and the primer runs at 13, the primer is _in_ house voice
and the generic rule does not apply. If the primer runs at 40, that is a real finding.

The word list is worth a pass regardless — but check each hit in context. `harness` as a noun ("the
tool harness") is a legitimate technical term; `harness` as a verb is slop. Fix the vague ones
(`robust` → say what property you mean), keep the precise ones.

Also worth measuring, with the same script shape: mean sentence length (aim ~15 words for a
non-technical audience) and the share of sentences over 40 words. Tables and headings will produce
false positives in any naive sentence splitter — read the offenders before "fixing" them.

## Judgement check 2 — verify links with the right tool

Anonymous `curl` returns **404 for a private repo**, which looks identical to a dead link.

```bash
# external links
grep -ohr "https://[^)\" ]*" pages/*.md | sed 's/[.,]$//' | sort -u \
  | while read u; do printf '%s %s\n' "$(curl -s -o /dev/null -w '%{http_code}' --ipv4 -L --max-time 15 "$u")" "$u"; done

# anything that 404s and lives on a private org — check with auth instead
gh api repos/ORG/REPO --jq '.full_name + " private=" + (.private|tostring)'
gh api repos/ORG/REPO/issues/10 --jq '"#10: " + .title + " [" + .state + "]"'
```

Use `gh api` for issues and PRs you cited by number, and confirm the **title and state** match what
the primer claims. This catches the more damaging error: a link that resolves but describes
something that has since been merged, closed, or renamed.

## Judgement check 3 — accuracy against ground truth

The audit cannot tell you whether a sentence is true. Before shipping, re-read the chapters most
coupled to verified facts — protocol fields, feature flags, storage model, deployment targets,
invariants — with the canonical doc open beside them.

Specific things to re-check, because they are the ones that were nearly wrong:

- **Numbers you did not read from source.** An HTTP status code in a sequence diagram that "felt
  right" is a fabrication. Either verify it or describe the behaviour without the number.
- **Distinctions the team calls incident-grade.** If two similarly-named things must never be
  conflated, make sure the primer never conflates them, including in diagrams and table headers.
- **Anything stated as shipped.** Cross-check against the status table. "Working" claims are the
  ones a reader will repeat in a meeting.

## Recording the result

Quote the clean run in the handoff and in the primer's README:

```
Last audit: 26/26 pages OK, 0 failures, 0 warnings.
```

Add the stale triggers next to it — the specific facts that, when they change, make specific
chapters wrong. Naming them per chapter is what makes the primer maintainable instead of a
write-once artifact that quietly rots.
