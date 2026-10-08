# Slack digest composition

Treat a recurring Slack report as a small interface. A reader's first questions are “are we okay?”
and “is there anything for me?” Answer both in the channel; put evidence in the thread.

## Shape

```text
headline (channel)  header · conclusion · compact metric grid · action · provenance
  ├ detail 1        evidence for the main finding
  ├ detail 2        product and user behavior
  ├ detail 3        failures, risks, and owner actions
  └ detail 4        blind spots and measurement limits
```

Do not force a fixed number of replies. Use only the parts the story needs.

## Block vocabulary

| Block            | Use                                                                   |
| ---------------- | --------------------------------------------------------------------- |
| `header`         | One per message, at the top; plain text only                          |
| `section` text   | Conclusion, interpretation, owner asks                                |
| `section.fields` | Numbers in a two-column grid, each cell `*Label*\nvalue · comparison` |
| `divider`        | Separate conceptual groups                                            |
| `context`        | Window, provenance, caveat, freshness                                 |

Set top-level `text` for notifications and accessibility. Disable link and media unfurls for link-
dense reports.

## Composition rules

- Keep the headline near one screen and free of internal jargon.
- Put anything numeric in fields rather than stacking pseudo-table prose.
- Bold one memorable figure. Bold field labels elsewhere.
- Put exact windows and methodological caveats below the numbers they qualify.
- Compress passing safety checks; spend space on movement, failures, and decisions.
- Group asks by actor: `Frontend`, `Infrastructure`, `Product analytics`, not `Latency findings`.
- Use human-readable link labels that explain why an issue or change matters.
- Keep raw user identifiers and sensitive quotations out of the payload.

## Send sequence

1. Build every payload with `scripts/slack_blocks.py`.
2. Validate every part before any network call.
3. Send the headline first and capture its timestamp.
4. If the headline fails, send nothing else.
5. Add the captured timestamp to each detail payload and send replies in order.
6. Persist the headline receipt and the last successfully sent part so a retry does not duplicate
   messages.

Transport identity and authorship are separate. Use a bot identity for an automated digest. Only
customize a post as a person when that person genuinely authored or explicitly approved it and the
platform authorization allows customized identity.

## Validation

The included builder checks Slack's structural limits and report-specific formatting failures. It
cannot establish that the data is correct or that publication is authorized; those remain explicit
preconditions.
