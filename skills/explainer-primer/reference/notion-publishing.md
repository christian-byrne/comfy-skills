# Notion publishing — syntax, limits, and the things that bite

Everything here was learned by hitting it.

## Why the raw REST API and not an MCP Notion tool

MCP Notion wrappers are lossy. They reliably write paragraphs and bulleted lists, and **strip
headings, images, code blocks, and toggles** — which is most of what a teaching page is made of.
`md2notion.py` talks to `api.notion.com/v1` directly so the page matches the markdown.

Use the MCP tools for _reading_ Notion (search, fetch) — they are convenient and lossless in that
direction. Use the script for writing.

## Supported markdown

| Syntax                                                     | Becomes                                                          |
| ---------------------------------------------------------- | ---------------------------------------------------------------- |
| `#` `##` `###`                                             | headings (Notion has only three levels; `####+` collapses to h3) |
| `- item`, `1. item`                                        | lists; 2-space indent nests one level                            |
| `> quote`                                                  | quote block                                                      |
| `---`                                                      | divider                                                          |
| ` ```lang `                                                | code block — **`lang=mermaid` renders as a live diagram**        |
| `\| a \| b \|`                                             | table; first row is the header                                   |
| `:::callout 🧭 blue_background` … `:::`                    | callout; body is nested markdown                                 |
| `:::toggle Title` … `:::`                                  | collapsible; body is nested markdown                             |
| `:::columns` … `---col---` … `:::`                         | side-by-side columns                                             |
| `**bold**` `*italic*` `` `code` `` `[t](url)` `~~strike~~` | inline, and emphasis nests                                       |

Callout colours are Notion's: `gray_background`, `blue_background`, `yellow_background`,
`red_background`, `green_background`, and so on.

## Mermaid is the whole reason this is pleasant

Notion renders ` ```mermaid ` code blocks as diagrams natively. That means:

- no image host, no signed URLs, no `public_artifact_url` step
- no re-render when a diagram changes — edit the source, republish
- the diagram source lives next to the prose it belongs to, so they cannot silently disagree
- it stays crisp at any zoom, unlike a PNG

This is a genuine improvement over the older workflow of rendering per-section PNGs and embedding
them as external image blocks. Prefer mermaid unless you need a hand-drawn or photographic image.

Emoji and `<br/>` inside node labels work. Keep labels quoted (`A["text"]`) so punctuation is safe.

## Hard API limits

| Limit                              | Value                     | Consequence                                        |
| ---------------------------------- | ------------------------- | -------------------------------------------------- |
| Children per append call           | 100                       | `append()` chunks automatically                    |
| Characters per rich_text item      | 2000                      | long code bodies are split into multiple items     |
| Nesting depth in one create/append | 2 levels                  | a toggle containing a list containing a list fails |
| Rate                               | roughly 3 requests/second | archives run 4-wide; `_req` backs off on 429       |

The nesting limit is the one that surprises people: keep lists inside callouts and toggles **flat**.

## Transport: force IPv4

`md2notion.py` shells out to `curl -sS --ipv4`, not urllib. On a host that advertises IPv6 without a
working IPv6 route to `api.notion.com`, urllib picks the AAAA record and blocks inside `connect()`,
where **neither `socket.setdefaulttimeout()` nor `urlopen(timeout=)` applies** — the socket sits in
`SYN-SENT` through the kernel's SYN retry schedule. It looks exactly like a deadlock: minutes of
wall time, zero CPU.

Diagnose it:

```bash
ss -tnp | grep SYN-SENT              # an IPv6 peer address is the signature
curl -o /dev/null -w '%{http_code} %{time_total}\n' --ipv4 https://api.notion.com/v1/users/me
curl -o /dev/null -w '%{http_code} %{time_total}\n' --ipv6 https://api.notion.com/v1/users/me
```

If v4 answers in milliseconds and v6 times out, that is the bug. `curl` without a flag appears to
work only because it does Happy Eyeballs and falls back — which is why "urllib hangs but curl works"
gets misfiled as a library quirk rather than a broken route.

Auth headers go through a mode-0600 `curl -K` config file rather than argv, because
`-H "Authorization: Bearer $TOKEN"` puts the secret in the process table where any local user's `ps`
can read it.

## Safety rails, and why each exists

**Never archive `child_page` or `child_database` blocks.** A refresh archives a page's existing
blocks before re-appending. A hub page's children _include its subpages_ — so a naive refresh of the
hub tries to delete the entire series. Notion happens to reject it with a 400, but relying on
someone else's validation to protect your data is not a plan. `NEVER_ARCHIVE` makes it explicit.

**`page-map.json` is load-bearing state.** It is the only link between a slug and its Notion page.
Commit it. Delete it and the next publish creates a duplicate tree under the parent, and the
original is orphaned with no way to find it except by hand.

**Save the map after every page creation, not at the end.** A run that dies halfway then resumes
instead of duplicating. This is what made recovering from the IPv6 hang free.

**Append, never rewrite, on pages you do not own.** Entry-point callouts are appended and only the
skill's _own_ marker block is archived. In a multi-agent workspace another agent may be editing the
same page in the same minute; a rewrite would clobber it.

**The blocks API can only insert `after` a block.** "Top of page" therefore means "immediately after
the first block". Configure `"after": "first"` for that, or a specific block id to place it under a
status banner.

## Inline parsing gotcha

Emphasis has to parse **recursively**, or `**Start here: [the primer](url)**` renders the link as
literal text: the bold pattern matches the whole span first and swallows the link. `rich()` recurses
into emphasis spans and merges annotations, so a link inside bold keeps its href. If you extend the
inline grammar, keep that property — the `check` command greps for leaked `[text](url)` because this
failure is invisible in a diff and obvious on the page.

## Cross-links

Write `{{slug}}` anywhere a URL goes. Publishing is two-pass — every page is created first so its
URL exists, then content is rendered with placeholders substituted. Consequences:

- pages can link forwards and backwards freely; nobody pastes URLs
- reordering the series does not touch a single link
- renaming a slug orphans its page — change the title in `primer.json` instead

Prev/next/index navigation is generated from `series` order. Never hand-write it.

## Useful one-liners

```bash
# what actually landed on a page, by block type
python3 -c "
import sys; sys.path.insert(0,'skills/explainer-primer/scripts')
import md2notion as N, collections
print(collections.Counter(b['type'] for b in N.all_children('PAGE_ID')))"

# confirm the token is not in the process table during a request
ps -eo args | grep '^curl' | grep -c 'secret_\|ntn_'   # expect 0
```
