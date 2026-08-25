#!/usr/bin/env python3
"""md2notion — markdown (a documented subset) -> Notion blocks, over the raw Notion REST API.

Why this exists rather than an MCP Notion wrapper: the wrappers are lossy. They reliably write
paragraphs and bullets but strip headings, images, code blocks, and toggles — which is most of what
a teaching page is made of. This talks to the REST API directly so the published page matches the
markdown.

Transport is `curl --ipv4`, not urllib. See reference/notion-publishing.md for the reason; the short
version is that a host with a broken IPv6 route makes urllib block in connect() for minutes, where
neither socket.setdefaulttimeout() nor urlopen(timeout=) applies.

Supported syntax
----------------
  # / ## / ###            headings (Notion has only h1..h3)
  paragraph text          paragraph
  - item                  bulleted list (2-space indent = one nesting level)
  1. item                 numbered list
  > quote                 quote block
  ---                     divider
  ```lang ... ```         code block (lang=mermaid renders as a diagram in Notion)
  | a | b |               table (first row = header)
  :::callout EMOJI COLOR  callout, body is nested markdown, closed by :::
  :::toggle Title         toggle, body is nested markdown, closed by :::
  :::columns              side-by-side; split children on a line containing only `---col---`
  inline: **bold**  *italic*  `code`  [text](url)  ~~strike~~  (emphasis nests, so a link
                          inside bold keeps its href)

Env: NOTION_TOKEN must be set.
"""
import atexit
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

TOKEN = os.environ.get("NOTION_TOKEN")
VER = "2022-06-28"
BASE = "https://api.notion.com/v1"

MAX_TEXT = 1900  # Notion hard limit is 2000 chars per rich_text item


# --------------------------------------------------------------------------- API
_HEADER_FILE = None


def _header_file():
    """Write the auth headers to a 0600 temp file for `curl -K`.

    Passing `-H "Authorization: Bearer $TOKEN"` puts the secret in argv, where any local user's
    `ps` shows it in full. A mode-0600 config file keeps it out of the process table.
    """
    global _HEADER_FILE
    if _HEADER_FILE is None or not os.path.exists(_HEADER_FILE):
        fd, p = tempfile.mkstemp(prefix="notion-hdr-", suffix=".conf")
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(f'header = "Authorization: Bearer {TOKEN}"\n')
            f.write(f'header = "Notion-Version: {VER}"\n')
            f.write('header = "Content-Type: application/json"\n')
        _HEADER_FILE = p
        atexit.register(lambda: os.path.exists(p) and os.unlink(p))
    return _HEADER_FILE


def _req(method, path, body=None, _retries=4) -> dict:
    """One Notion REST call, over curl --ipv4.

    Why curl and not urllib: on a host that advertises IPv6 without a working IPv6 route to
    api.notion.com, urllib picks the AAAA record and blocks in connect(), where neither
    socket.setdefaulttimeout() nor urlopen(timeout=) applies — the socket sits in SYN-SENT
    through the kernel's SYN retry schedule (minutes, at zero CPU, looking like a deadlock).
    curl does Happy Eyeballs; --ipv4 removes the ambiguity and --max-time makes the ceiling real.
    Diagnose the underlying condition with: ss -tnp | grep SYN-SENT
    """
    url = BASE + path
    cmd = [
        "curl", "-sS", "--ipv4", "--max-time", "60", "--connect-timeout", "10",
        "-K", _header_file(),  # headers via config file, NOT argv — see _header_file()
        "-X", method, url,
        "-w", "\n%{http_code}",
    ]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    payload = json.dumps(body) if body is not None else None

    for attempt in range(_retries):
        p = subprocess.run(cmd, input=payload, capture_output=True, text=True, timeout=90)
        if p.returncode != 0:
            if attempt < _retries - 1:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"curl failed ({p.returncode}) {method} {path}: {p.stderr[:300]}")
        raw, _, status = p.stdout.rpartition("\n")
        code = int(status.strip() or 0)
        if code == 200:
            return json.loads(raw)
        if code in (429, 500, 502, 503, 504) and attempt < _retries - 1:
            time.sleep(2 + 2 * attempt)
            continue
        print(f"HTTP {code} {method} {path}\n{raw[:1200]}", file=sys.stderr)
        raise RuntimeError(f"Notion API {code} on {method} {path}")
    raise RuntimeError(f"{method} {path} exhausted retries")


def get_children(block_id, cursor=None):
    q = "?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
    return _req("GET", f"/blocks/{block_id}/children{q}")


def all_children(block_id):
    out, cursor = [], None
    while True:
        r = get_children(block_id, cursor)
        out += r["results"]
        if not r.get("has_more"):
            return out
        cursor = r["next_cursor"]


def archive_block(block_id):
    return _req("PATCH", f"/blocks/{block_id}", {"archived": True})


def append(block_id, children, after=None):
    """Append children in chunks of 100 (API max)."""
    res = []
    for i in range(0, len(children), 100):
        body = {"children": children[i:i + 100]}
        if after and i == 0:
            body["after"] = after
        res.append(_req("PATCH", f"/blocks/{block_id}/children", body))
    return res


def create_page(parent_page_id, title, icon=None, children=None):
    body: dict = {
        "parent": {"page_id": parent_page_id},
        "properties": {"title": {"title": [text_rt(title)]}},
    }
    if icon:
        body["icon"] = {"type": "emoji", "emoji": icon}
    if children:
        body["children"] = children[:100]
    page = _req("POST", "/pages", body)
    if children and len(children) > 100:
        append(page["id"], children[100:])
    return page


def set_page_title(page_id, title, icon=None):
    body: dict = {"properties": {"title": {"title": [text_rt(title)]}}}
    if icon:
        body["icon"] = {"type": "emoji", "emoji": icon}
    return _req("PATCH", f"/pages/{page_id}", body)


#: Blocks that are really *pages*. Archiving one deletes a subpage and everything under it, so
#: a content refresh must never touch them. Notion also rejects the call, but relying on that
#: is relying on someone else's validation to protect our data.
NEVER_ARCHIVE = {"child_page", "child_database"}


def replace_page_content(page_id, children):
    """Archive this page's own content blocks, then append the new ones. Subpages are left alone.

    Notion has no bulk-archive, so a refresh is one call per existing block — serially that is
    minutes for the whole series. A small pool keeps it under the API's rate limit while making a
    full republish practical; _req already backs off on 429.
    """
    doomed = [b["id"] for b in all_children(page_id) if b["type"] not in NEVER_ARCHIVE]

    def _kill(bid):
        try:
            archive_block(bid)
        except Exception as e:  # noqa: BLE001 - a stuck block must not abort the sync
            print(f"  ! could not archive {bid}: {e}", file=sys.stderr)

    if doomed:
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(_kill, doomed))
    append(page_id, children)


# ------------------------------------------------------------------- rich text
def text_rt(content, bold=False, italic=False, code=False, strike=False, link=None):
    o = {"type": "text", "text": {"content": content[:MAX_TEXT]}}
    if link:
        o["text"]["link"] = {"url": link}
    ann = {}
    if bold:
        ann["bold"] = True
    if italic:
        ann["italic"] = True
    if code:
        ann["code"] = True
    if strike:
        ann["strikethrough"] = True
    if ann:
        o["annotations"] = ann
    return o


INLINE = re.compile(
    r"(?P<link>\[(?P<ltext>[^\]]+)\]\((?P<lurl>[^)\s]+)\))"
    r"|(?P<code>`[^`]+`)"
    r"|(?P<bold>\*\*[^*]+\*\*)"
    r"|(?P<strike>~~[^~]+~~)"
    r"|(?P<italic>(?<![\w*])\*[^*\n]+\*(?![\w*]))"
)


def _annotate(items, **flags):
    """Apply annotations to already-parsed rich_text items, preserving what they already have."""
    for it in items:
        ann = it.setdefault("annotations", {})
        ann.update(flags)
    return items


def rich(s, **inherited):
    """Parse inline markdown into a Notion rich_text array.

    Emphasis spans are parsed *recursively* so a link inside bold keeps its href — writing
    `**see the [primer](url)**` must produce a bold link, not a bold literal "[primer](url)".
    """
    out, pos = [], 0
    for m in INLINE.finditer(s):
        if m.start() > pos:
            out.append(text_rt(s[pos:m.start()], **inherited))
        if m.group("link"):
            out.append(text_rt(m.group("ltext"), link=m.group("lurl"), **inherited))
        elif m.group("code"):
            out.append(text_rt(m.group("code")[1:-1], code=True, **inherited))
        elif m.group("bold"):
            out += _annotate(rich(m.group("bold")[2:-2], **inherited), bold=True)
        elif m.group("strike"):
            out += _annotate(rich(m.group("strike")[2:-2], **inherited), strikethrough=True)
        elif m.group("italic"):
            out += _annotate(rich(m.group("italic")[1:-1], **inherited), italic=True)
        pos = m.end()
    if pos < len(s):
        out.append(text_rt(s[pos:], **inherited))
    return out or [text_rt("")]


# ---------------------------------------------------------------------- blocks
def blk(t, payload):
    return {"object": "block", "type": t, t: payload}


def heading(level, s):
    t = f"heading_{min(level, 3)}"
    return blk(t, {"rich_text": rich(s), "is_toggleable": False})


def para(s):
    return blk("paragraph", {"rich_text": rich(s) if isinstance(s, str) else s})


def bullet(s, children=None):
    p = {"rich_text": rich(s)}
    if children:
        p["children"] = children
    return blk("bulleted_list_item", p)


def numbered(s, children=None):
    p = {"rich_text": rich(s)}
    if children:
        p["children"] = children
    return blk("numbered_list_item", p)


def quote(s):
    return blk("quote", {"rich_text": rich(s)})


def divider():
    return blk("divider", {})


def code(text, lang="plain text"):
    # Notion caps a single rich_text item at 2000 chars; chunk long code bodies.
    chunks = [text[i:i + MAX_TEXT] for i in range(0, max(len(text), 1), MAX_TEXT)]
    return blk("code", {"rich_text": [text_rt(c) for c in chunks], "language": lang})


def callout(s_children, icon="💡", color="gray_background"):
    children = s_children if isinstance(s_children, list) else [para(s_children)]
    first = children[0]
    rest = children[1:]
    rt = first.get(first["type"], {}).get("rich_text", [text_rt("")])
    p = {"rich_text": rt, "icon": {"type": "emoji", "emoji": icon}, "color": color}
    if rest:
        p["children"] = rest
    return blk("callout", p)


def toggle(title, children):
    return blk("toggle", {"rich_text": rich(title), "children": children})


def table(rows, has_header=True):
    width = max(len(r) for r in rows)
    trs = []
    for r in rows:
        cells = [rich(c) for c in r] + [[text_rt("")]] * (width - len(r))
        trs.append(blk("table_row", {"cells": cells}))
    return blk("table", {
        "table_width": width,
        "has_column_header": has_header,
        "has_row_header": False,
        "children": trs,
    })


def link_to_page(page_id):
    return blk("link_to_page", {"type": "page_id", "page_id": page_id})


def columns(col_children_lists):
    cols = [blk("column", {"children": c}) for c in col_children_lists]
    return blk("column_list", {"children": cols})


# ------------------------------------------------------------------ md -> blocks
FENCE = re.compile(r"^```(\w[\w+ -]*)?\s*$")
DIRECTIVE = re.compile(r"^:::(\w+)\s*(.*)$")
TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")
TABLE_SEP = re.compile(r"^\|[\s:|-]+\|\s*$")

LANG_MAP = {
    "": "plain text", None: "plain text", "text": "plain text", "txt": "plain text",
    "sh": "shell", "bash": "bash", "js": "javascript", "ts": "typescript",
    "py": "python", "go": "go", "json": "json", "yaml": "yaml", "yml": "yaml",
    "mermaid": "mermaid", "sql": "sql", "diff": "diff", "html": "html",
    "md": "markdown", "markdown": "markdown", "toml": "toml",
}


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def md_to_blocks(md):
    lines = md.replace("\t", "  ").split("\n")
    return _parse(lines, 0, len(lines))


def _parse(lines, i, end):  # noqa: C901 - a parser; splitting it hurts readability
    blocks = []
    while i < end:
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        # fenced code
        m = FENCE.match(line)
        if m:
            lang = LANG_MAP.get((m.group(1) or "").strip(), (m.group(1) or "plain text").strip())
            body, i = [], i + 1
            while i < end and not FENCE.match(lines[i].strip()):
                body.append(lines[i])
                i += 1
            i += 1
            blocks.append(code("\n".join(body), lang))
            continue

        # ::: directives
        m = DIRECTIVE.match(line)
        if m and m.group(1) != "":
            kind, arg = m.group(1), m.group(2).strip()
            depth, j = 1, i + 1
            while j < end:
                s = lines[j].strip()
                if DIRECTIVE.match(s) and s != ":::":
                    depth += 1
                elif s == ":::":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner = lines[i + 1:j]
            i = j + 1
            if kind == "callout":
                parts = arg.split(None, 1)
                icon = parts[0] if parts else "💡"
                color = parts[1].strip() if len(parts) > 1 else "gray_background"
                blocks.append(callout(_parse(inner, 0, len(inner)), icon, color))
            elif kind == "toggle":
                blocks.append(toggle(arg, _parse(inner, 0, len(inner))))
            elif kind == "columns":
                groups, cur = [], []
                for ln in inner:
                    if ln.strip() == "---col---":
                        groups.append(cur)
                        cur = []
                    else:
                        cur.append(ln)
                groups.append(cur)
                blocks.append(columns([_parse(g, 0, len(g)) for g in groups]))
            continue

        # table
        if TABLE_ROW.match(line):
            rows = []
            while i < end and TABLE_ROW.match(lines[i].strip()):
                s = lines[i].strip()
                if not TABLE_SEP.match(s):
                    rows.append([c.strip() for c in s[1:-1].split("|")])
                i += 1
            if rows:
                blocks.append(table(rows))
            continue

        if line == "---":
            blocks.append(divider())
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            blocks.append(heading(len(m.group(1)), m.group(2)))
            i += 1
            continue

        if line.startswith("> "):
            buf = []
            while i < end and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            blocks.append(quote(" ".join(buf)))
            continue

        # lists (with one level of nesting via indentation)
        m = re.match(r"^([-*])\s+(.*)$", line) or re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            base = _indent(raw)
            item_lines, i2 = [], i
            while i2 < end:
                r2 = lines[i2]
                if not r2.strip():
                    # blank line ends the list unless the next line continues it
                    nxt = lines[i2 + 1] if i2 + 1 < end else ""
                    if not (re.match(r"^\s*([-*]|\d+\.)\s+", nxt) and _indent(nxt) >= base):
                        break
                    i2 += 1
                    continue
                if _indent(r2) < base or not re.match(r"^\s*([-*]|\d+\.)\s+", r2):
                    if _indent(r2) > base:  # continuation / nested content
                        item_lines.append(r2)
                        i2 += 1
                        continue
                    break
                item_lines.append(r2)
                i2 += 1
            blocks += _list_blocks(item_lines, base)
            i = i2
            continue

        # paragraph (join soft-wrapped lines)
        buf = [line]
        i += 1
        while i < end:
            nxt = lines[i]
            s = nxt.strip()
            if (not s or FENCE.match(s) or DIRECTIVE.match(s) or TABLE_ROW.match(s)
                    or s == "---" or s.startswith("#") or s.startswith("> ")
                    or re.match(r"^\s*([-*]|\d+\.)\s+", nxt)):
                break
            buf.append(s)
            i += 1
        blocks.append(para(" ".join(buf)))
    return blocks


def _list_blocks(item_lines, base):
    """Turn a run of list lines (possibly nested) into Notion list blocks."""
    out, i = [], 0
    while i < len(item_lines):
        raw = item_lines[i]
        m = re.match(r"^\s*([-*])\s+(.*)$", raw)
        ordered = False
        if not m:
            m = re.match(r"^\s*(\d+)\.\s+(.*)$", raw)
            ordered = bool(m)
        if not m:
            i += 1
            continue
        content = m.group(2)
        # gather deeper-indented lines as this item's children
        child_lines, j = [], i + 1
        while j < len(item_lines) and _indent(item_lines[j]) > base:
            child_lines.append(item_lines[j])
            j += 1
        children = None
        if child_lines:
            inner_base = min(_indent(x) for x in child_lines if x.strip())
            children = _list_blocks(child_lines, inner_base) or _parse(child_lines, 0, len(child_lines))
        out.append((numbered if ordered else bullet)(content, children))
        i = j
    return out


def blocks_from_file(path):
    with open(path, encoding="utf-8") as f:
        return md_to_blocks(f.read())
