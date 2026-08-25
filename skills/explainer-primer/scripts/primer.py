#!/usr/bin/env python3
"""primer — build, publish, and audit a multi-page explainer tree in Notion.

Pages are authored as markdown on disk; Notion is a render target. One command publishes the
whole tree, resolving `{{slug}}` cross-links and generating prev/next navigation, and another
audits what actually landed.

Subcommands
-----------
  init                 scaffold primer.json, pages/, and a template chapter
  publish [prefix...]  create/refresh pages (no args = all). --dry parses without touching Notion
  entrypoints          (re)apply the "start here" callout on the pages readers already land on
  check                read-only audit of the published tree; exits non-zero on failure

Config (primer.json, beside the pages directory)
------------------------------------------------
  parent_page_id   Notion page the hub is created under
  hub_slug         which series entry is the hub (default the first)
  pages_dir        directory of <slug>.md files (default "pages")
  series           ordered [{slug, icon, title, reference?}]
                     reference: true  -> a lookup page (glossary/FAQ/index), exempt from the
                                         per-chapter diagram and teaching-scaffolding checks
  entrypoints      [{page_id, after?, markdown}] — after: "first" | a block id | omitted (end)
  scaffolding      optional {orientation, quiz, nav} marker strings the audit looks for

State
-----
  page-map.json    slug -> {id, url}. LOAD-BEARING: it is the only link between a slug and its
                   Notion page. Delete it and the tree is orphaned; the next publish creates a
                   duplicate set under the parent. Commit it.

Env: NOTION_TOKEN
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import md2notion as N  # noqa: E402

CONFIG_NAME = "primer.json"
MAP_NAME = "page-map.json"
LINKREF = re.compile(r"\{\{([0-9a-zA-Z._-]+)\}\}")
LITERAL_MD = re.compile(r"\[[^\]]{2,80}\]\(https?://")
DEFAULT_MARKERS = {
    "orientation": "Where you are",
    "quiz": "Check yourself",
    "nav": "Back to the",
}


# ------------------------------------------------------------------ config/state
class Primer:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        cfg_path = os.path.join(self.root, CONFIG_NAME)
        if not os.path.exists(cfg_path):
            sys.exit(f"no {CONFIG_NAME} in {self.root} — run `primer.py init --dir {self.root}`")
        with open(cfg_path, encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.series = self.cfg["series"]
        self.order = [e["slug"] for e in self.series]
        self.by_slug = {e["slug"]: e for e in self.series}
        self.hub = self.cfg.get("hub_slug") or self.order[0]
        self.pages_dir = os.path.join(self.root, self.cfg.get("pages_dir", "pages"))
        self.markers = {**DEFAULT_MARKERS, **self.cfg.get("scaffolding", {})}
        self.map_path = os.path.join(self.root, MAP_NAME)
        self.pmap = {}
        if os.path.exists(self.map_path):
            with open(self.map_path, encoding="utf-8") as f:
                self.pmap = json.load(f)

    def save_map(self):
        with open(self.map_path, "w", encoding="utf-8") as f:
            json.dump(self.pmap, f, indent=2, sort_keys=True, ensure_ascii=False)

    def md_path(self, slug):
        return os.path.join(self.pages_dir, slug + ".md")

    def is_chapter(self, slug):
        return slug != self.hub and not self.by_slug[slug].get("reference")


def notion_url(pid):
    return "https://www.notion.so/" + pid.replace("-", "")


# ------------------------------------------------------------------ publish
def ensure_pages(p):
    """Pass 1 — every slug has a live Notion page, so pass 2 can cross-link them."""
    if p.hub not in p.pmap:
        e = p.by_slug[p.hub]
        page = N.create_page(p.cfg["parent_page_id"], e["title"], icon=e.get("icon"))
        p.pmap[p.hub] = {"id": page["id"], "url": notion_url(page["id"])}
        print(f"+ hub {p.hub} -> {p.pmap[p.hub]['url']}")
        p.save_map()
    hub_id = p.pmap[p.hub]["id"]
    for slug in p.order:
        if slug == p.hub or slug in p.pmap:
            continue
        e = p.by_slug[slug]
        page = N.create_page(hub_id, e["title"], icon=e.get("icon"))
        p.pmap[slug] = {"id": page["id"], "url": notion_url(page["id"])}
        print(f"+ {slug} -> {p.pmap[slug]['url']}")
        p.save_map()  # after each create: a crash mid-run resumes instead of duplicating


def substitute(md, pmap):
    missing = set()

    def repl(m):
        slug = m.group(1)
        if slug in pmap:
            return pmap[slug]["url"]
        missing.add(slug)
        return "#"

    return LINKREF.sub(repl, md), missing


def nav_footer(p, slug):
    if slug == p.hub:
        return ""
    i = p.order.index(slug)
    parts = []
    if i > 0:
        prev = p.order[i - 1]
        parts.append(f"← **Previous:** [{p.by_slug[prev]['title']}]({{{{{prev}}}}})")
    parts.append(f"⬆ [{p.markers['nav']} index]({{{{{p.hub}}}}})")
    if i + 1 < len(p.order):
        nxt = p.order[i + 1]
        parts.append(f"**Next:** [{p.by_slug[nxt]['title']}]({{{{{nxt}}}}}) →")
    return "\n\n---\n\n" + "  ·  ".join(parts) + "\n"


def render(p, slug, dry=False):
    path = p.md_path(slug)
    if not os.path.exists(path):
        print(f"  . {slug}: no markdown yet, skipping")
        return
    with open(path, encoding="utf-8") as f:
        md = f.read()
    if p.cfg.get("nav", True):
        md += nav_footer(p, slug)
    md, missing = substitute(md, p.pmap if not dry else {s: {"url": "#"} for s in p.order})
    if missing and not dry:
        print(f"  ! {slug}: unresolved cross-links -> {sorted(missing)}")
    blocks = N.md_to_blocks(md)
    if dry:
        print(f"  = {slug}: {len(blocks)} top-level blocks")
        return
    e = p.by_slug[slug]
    N.set_page_title(p.pmap[slug]["id"], e["title"], icon=e.get("icon"))
    N.replace_page_content(p.pmap[slug]["id"], blocks)
    print(f"  ✓ {slug}: {len(blocks)} blocks -> {p.pmap[slug]['url']}")


def cmd_publish(p, args):
    if not args.dry:
        ensure_pages(p)
    targets = [s for s in p.order if not args.slugs or any(s.startswith(a) for a in args.slugs)]
    print(f"rendering {len(targets)} page(s)")
    for slug in targets:
        render(p, slug, args.dry)


# ------------------------------------------------------------------ entrypoints
def flatten(blocks):
    out = []
    for b in blocks:
        t = b["type"]
        for r in b.get(t, {}).get("rich_text", []) or []:
            out.append(r.get("plain_text", ""))
        for cells in b.get(t, {}).get("cells", []) or []:
            for r in cells:
                out.append(r.get("plain_text", ""))
    return " ".join(out)


def hrefs(blocks):
    out = []
    for b in blocks:
        t = b["type"]
        for r in b.get(t, {}).get("rich_text", []) or []:
            if r.get("href"):
                out.append(r["href"])
        for cells in b.get(t, {}).get("cells", []) or []:
            for r in cells:
                if r.get("href"):
                    out.append(r["href"])
    return out


def cmd_entrypoints(p, _args):
    """Append a 'start here' callout to pages readers already land on.

    Deliberately append-then-archive-own-marker rather than rewrite: these pages usually belong to
    someone else (or another agent), and a rewrite would clobber concurrent edits. The marker makes
    it idempotent without needing to own the page.
    """
    eps = p.cfg.get("entrypoints", [])
    if not eps:
        print("no entrypoints configured")
        return
    marker = p.cfg.get("entrypoint_marker", "start here")
    for ep in eps:
        pid = ep["page_id"]
        kids = N.all_children(pid)
        stale = [b["id"] for b in kids
                 if b["type"] == "callout" and marker.lower() in flatten([b]).lower()]
        md, missing = substitute(ep["markdown"], p.pmap)
        if missing:
            print(f"  ! entrypoint {pid}: unresolved {sorted(missing)}")
        anchor = ep.get("after")
        if anchor == "first":
            # The blocks API can only insert *after* a block, so "top of page" means
            # "immediately after the first block" — still above the fold.
            anchor = kids[0]["id"] if kids else None
        N.append(pid, N.md_to_blocks(md), after=anchor)
        for b in stale:
            N.archive_block(b)
        print(f"  ✓ {pid}: linked (replaced {len(stale)} stale)")


# ------------------------------------------------------------------ check
def cmd_check(p, _args):
    fails, warns = [], []
    hub_id = p.pmap.get(p.hub, {}).get("id")
    if not hub_id:
        sys.exit("nothing published yet (no page-map.json entry for the hub)")

    print(f"{'page':32} {'blocks':>6} {'diagrams':>8} {'links':>5}  checks")
    print("-" * 80)
    for slug in p.order:
        if slug not in p.pmap:
            fails.append(f"{slug}: never published")
            continue
        pid = p.pmap[slug]["id"]
        page = N._req("GET", f"/pages/{pid}")
        top = N.all_children(pid)
        nested = list(top)
        for b in top:
            if b.get("has_children") and b["type"] in ("callout", "toggle", "column_list", "table"):
                try:
                    kids = N.all_children(b["id"])
                    nested += kids
                    for k in kids:
                        if k.get("has_children"):
                            nested += N.all_children(k["id"])
                except Exception:  # noqa: BLE001 - a fetch hiccup must not abort the audit
                    pass
        notes = []

        want = p.cfg["parent_page_id"] if slug == p.hub else hub_id
        got = (page.get("parent", {}).get("page_id") or "").replace("-", "")
        if got != want.replace("-", ""):
            fails.append(f"{slug}: wrong parent")
            notes.append("BAD-PARENT")

        content = [b for b in top if b["type"] not in N.NEVER_ARCHIVE]
        if not content:
            fails.append(f"{slug}: page is EMPTY")
            notes.append("EMPTY")
        if os.path.exists(p.md_path(slug)):
            with open(p.md_path(slug), encoding="utf-8") as f:
                local = N.md_to_blocks(f.read())
            if len(content) < len(local):
                warns.append(f"{slug}: {len(content)} blocks published vs {len(local)} local")
                notes.append("SHORT")

        text = flatten(nested)
        leaked = LITERAL_MD.search(text)
        if leaked:
            fails.append(f"{slug}: literal markdown link leaked: {leaked.group()[:60]}")
            notes.append("RAW-LINK")
        if LINKREF.search(text):
            fails.append(f"{slug}: unresolved cross-link placeholder")
            notes.append("UNRESOLVED")

        if p.cfg.get("nav", True) and slug != p.hub and p.markers["nav"] not in text:
            fails.append(f"{slug}: missing nav footer")
            notes.append("NO-NAV")

        mer = [b for b in nested if b["type"] == "code" and b["code"]["language"] == "mermaid"]
        if p.is_chapter(slug):
            if not mer:
                fails.append(f"{slug}: chapter with no diagram")
                notes.append("NO-DIAGRAM")
            if p.markers["orientation"] not in text:
                warns.append(f"{slug}: no orientation callout")
                notes.append("NO-ORIENT")
            if p.markers["quiz"] not in text:
                warns.append(f"{slug}: no check-yourself section")
                notes.append("NO-QUIZ")

        print(f"{slug:32} {len(content):>6} {len(mer):>8} {len(hrefs(nested)):>5}  "
              f"{'OK' if not notes else ' '.join(notes)}")

    print("-" * 80)
    hub_kids = N.all_children(hub_id)
    subs = [b for b in hub_kids if b["type"] == "child_page"]
    print(f"hub subpages: {len(subs)} (expected {len(p.order) - 1})")
    if len(subs) != len(p.order) - 1:
        fails.append(f"hub has {len(subs)} subpages, expected {len(p.order) - 1}")

    deep = list(hub_kids)
    for b in hub_kids:
        if b.get("has_children") and b["type"] in ("callout", "toggle", "column_list", "table"):
            deep += N.all_children(b["id"])
    linked = " ".join(hrefs(deep))
    missing = [s for s in p.order if s != p.hub and p.pmap[s]["url"].split("/")[-1] not in linked]
    if missing:
        fails.append(f"hub index does not link: {missing}")
    print(f"hub links every page: {'YES' if not missing else 'NO -> ' + str(missing)}")

    for ep in p.cfg.get("entrypoints", []):
        kids = N.all_children(ep["page_id"])
        marker = p.cfg.get("entrypoint_marker", "start here")
        hit = [i for i, b in enumerate(kids)
               if b["type"] == "callout" and marker.lower() in flatten([b]).lower()]
        ok = bool(hit) and hit[0] <= 2
        print(f"entrypoint {ep['page_id'][:8]}: "
              f"{'OK at position ' + str(hit[0]) if ok else 'MISSING OR BURIED'}")
        if not ok:
            fails.append(f"entrypoint {ep['page_id']} missing or buried")
        if len(hit) > 1:
            fails.append(f"duplicate callouts on entrypoint {ep['page_id']}")

    print("=" * 80)
    print(f"FAILURES: {len(fails)}")
    for f in fails:
        print("  ✘", f)
    print(f"WARNINGS: {len(warns)}")
    for w in warns:
        print("  ~", w)
    return 1 if fails else 0


# ------------------------------------------------------------------ init
TEMPLATE = """:::callout 🧭 blue_background
**Where you are:** chapter N of M. **Assumes:** [previous chapter]({{{{SLUG-OF-PREVIOUS}}}}). **Time:** X minutes.
**After this page you can explain:** the one or two things a reader should be able to say out loud.
:::

Open with the concrete thing the reader already understands. Analogy first, abstraction second.

## The idea

```mermaid
flowchart LR
  A["something familiar"] --> B["the new idea"]
```

:::callout ⚠️ yellow_background
**Misconception:** state the wrong belief people actually hold, then correct it. Name it as a
misconception explicitly — a reader who holds it needs to see it addressed, not merely contradicted.
:::

---

:::toggle ✅ Check yourself — three questions
**Q. Ask the thing this page exists to teach.**
The answer, stated plainly.
:::

## Terms introduced here

**term**, **term** — see the [glossary]({{{{SLUG-OF-GLOSSARY}}}}).

## Where this lives in the real system

- Repo, file, or doc the curious reader should open next
"""

INIT_CFG = {
    "parent_page_id": "REPLACE-WITH-NOTION-PAGE-ID",
    "hub_slug": "00-start-here",
    "pages_dir": "pages",
    "nav": True,
    "entrypoint_marker": "start here",
    "series": [
        {"slug": "00-start-here", "icon": "🎓", "title": "Understand This System — start here",
         "reference": True},
        {"slug": "01-first-chapter", "icon": "🎬", "title": "1 · First chapter"},
    ],
    "entrypoints": [],
}


def cmd_init(p_root, _args):
    os.makedirs(os.path.join(p_root, "pages"), exist_ok=True)
    cfg_path = os.path.join(p_root, CONFIG_NAME)
    if os.path.exists(cfg_path):
        sys.exit(f"{cfg_path} already exists")
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(INIT_CFG, f, indent=2, ensure_ascii=False)
    tmpl = os.path.join(p_root, "pages", "_TEMPLATE.md")
    with open(tmpl, "w", encoding="utf-8") as f:
        f.write(TEMPLATE)
    print(f"scaffolded {cfg_path} and {tmpl}")
    print("next: set parent_page_id, fill in series, write pages/<slug>.md, then `publish --dry`")


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--dir", default=".", help="primer directory (holds primer.json)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sp = sub.add_parser("publish")
    sp.add_argument("slugs", nargs="*", help="slug prefixes to refresh (default: all)")
    sp.add_argument("--dry", action="store_true", help="parse only; touch nothing")
    sub.add_parser("entrypoints")
    sub.add_parser("check")
    args = ap.parse_args()

    if args.cmd == "init":
        return cmd_init(os.path.abspath(args.dir), args)
    if not os.environ.get("NOTION_TOKEN") and not getattr(args, "dry", False):
        sys.exit("NOTION_TOKEN is not set")
    p = Primer(args.dir)
    return {"publish": cmd_publish, "entrypoints": cmd_entrypoints, "check": cmd_check}[args.cmd](p, args)


if __name__ == "__main__":
    sys.exit(main() or 0)
