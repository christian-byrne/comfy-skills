#!/usr/bin/env python3
"""Build, validate and send a Slack Block Kit digest as a headline plus threaded detail.

Why this exists: a recurring signal post is a UI, not prose. Sent as one plain-text
message it becomes a wall nobody reads. The shape that works is a skimmable headline
in the channel and the evidence in the thread beneath it, built from Block Kit so
there is real visual hierarchy — headers, dividers, two-column metric grids, and
muted context lines for provenance.

Pure builders and validation live here so they can be unit-tested without a token.
Sending is a separate function that takes an injected poster.

Usage as a library:

    from slack_blocks import H, S, D, F, C, Digest

    d = Digest(channel="C123", headline_fallback="Rollout check — step does not pass yet")
    d.headline = [
        H("Agent rollout check"),
        S("> *Tomorrow's step does not pass yet.* Nothing is bad enough to roll back."),
        D,
        F(["*Requests*\\n*417* · need 500", "*Failures*\\n*3.9%* · need 6% or under"]),
        C("Window 24h to 4:27pm PT · pass marks from the rollout plan"),
    ]
    d.add_part("1 · Would anything make us roll back?", [...], fallback="Rollback checks")
    d.validate()                      # raises BlockError on any Slack limit
    for path in d.write("out/run28-"): print(path)
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Iterator

# Slack's documented limits. Exceeding any of these is a 400 at send time, which on a
# threaded digest means a headline with no thread — the worst possible failure mode.
MAX_BLOCKS = 50
MAX_FIELDS = 10
MAX_FIELD_CHARS = 2000
MAX_SECTION_CHARS = 3000
MAX_HEADER_CHARS = 150
MAX_FALLBACK_CHARS = 4000
MAX_LINK_TEXT_CHARS = 120  # a link label is a label, not a clause

# Two-column `fields` is the default presentation for numbers. A `section` text block
# holding several short number-bearing lines is a table someone typed as prose: Slack
# renders it as a ragged left-aligned wall, and the reader cannot compare values down a
# column. These thresholds describe that shape without catching genuine prose, which
# carries its numbers inside long sentences rather than on short labelled lines.
MIN_METRIC_LINES = 3
MAX_METRIC_LINE_CHARS = 80

# House policy for *signal posts specifically*: the only shortcodes those may use. Other
# genres have their own conventions — the coverage leaderboard's trophies and medals are the
# point of that message — so this is passed in by the caller rather than baked into validation.
# Universal Slack mechanics (limits, link integrity, Unicode emoji) always apply.
SIGNAL_POST_SHORTCODES = frozenset(
    {"pr-open", "pr-merged", "pr-closed", "github-queued", "git-approved", "github", "thread"}
)
ALLOWED_SHORTCODES = SIGNAL_POST_SHORTCODES  # back-compat alias


class BlockError(ValueError):
    """A payload that Slack would reject, or that breaks the house format rules."""


# ── builders ────────────────────────────────────────────────────────────────────
def H(text: str) -> dict:
    """A header. One per message, at the top, so a reader landing mid-thread knows
    where they are without reading a sentence. plain_text only — no links or bold."""
    return {"type": "header", "text": {"type": "plain_text", "text": text, "emoji": True}}


def S(text: str) -> dict:
    """A section of mrkdwn. Prefix with `> ` for the verdict line; Slack renders a
    left bar that reads as the answer rather than as the first sentence."""
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


D: dict = {"type": "divider"}


def F(cells: Iterable[str]) -> dict:
    """A two-column grid. Give every cell `*Label*\\nvalue · what's needed` so the eye
    scans a table instead of parsing sentences. Anything with a number belongs here."""
    return {"type": "section", "fields": [{"type": "mrkdwn", "text": c} for c in cells]}


def C(text: str) -> dict:
    """Small muted type. Provenance, caveats, owner routing and freshness stamps go
    here so they are available without competing with the numbers."""
    return {"type": "context", "elements": [{"type": "mrkdwn", "text": text}]}


# ── validation ──────────────────────────────────────────────────────────────────
def _rendered_texts(blocks: list[dict]) -> Iterator[str]:
    """Every string Slack renders as its own formatting unit, one at a time.

    Slack applies mrkdwn per string, so a code fence or span opened in one block cannot
    close in another. Any check that cares about code regions has to iterate these rather
    than scan a joined dump of the payload, or it will pair delimiters across blocks.
    """
    for b in blocks:
        t = b.get("text")
        if isinstance(t, dict) and "text" in t:
            yield t["text"]
        for cell in b.get("fields") or []:
            if isinstance(cell, dict) and "text" in cell:
                yield cell["text"]
        for el in b.get("elements") or []:
            if isinstance(el, dict) and "text" in el:
                yield el["text"]


def metric_prose_sections(blocks: list[dict]) -> list[tuple[int, int]]:
    """Find `section` text blocks that are really tables typed as prose.

    Returns `(block_index, metric_line_count)` for each offender. The shape being caught
    is several short lines that each carry a number — which belongs in a two-column
    `fields` block. Long sentences that happen to contain a figure are left alone: a
    line only counts when it is at most `MAX_METRIC_LINE_CHARS`, which is what separates
    a label/value pair from a clause.
    """
    found = []
    for i, b in enumerate(blocks):
        if b.get("type") != "section" or "text" not in b or "fields" in b:
            continue
        lines = [ln.strip() for ln in b["text"]["text"].split("\n") if ln.strip()]
        if len(lines) < MIN_METRIC_LINES:
            continue
        metric_lines = [
            ln for ln in lines
            if len(ln) <= MAX_METRIC_LINE_CHARS and any(ch.isdigit() for ch in ln)
        ]
        if len(metric_lines) >= MIN_METRIC_LINES:
            found.append((i, len(metric_lines)))
    return found


def validate_blocks(
    blocks: list[dict],
    label: str = "message",
    shortcodes: frozenset[str] | None = None,
    require_columns: bool = True,
) -> None:
    """Validate against Slack's own limits and the failure modes that survive valid JSON.

    `shortcodes` restricts which `:name:` codes may appear. Pass
    `SIGNAL_POST_SHORTCODES` for a signal digest; leave it None for any other genre,
    which skips the shortcode check while keeping every universal check.

    `require_columns` rejects a `section` that holds several short number-bearing lines,
    because that is a table typed as prose and belongs in a two-column `fields` block.
    Set it False only where the ORDER of the lines is the content and a grid would
    destroy it — the two cases seen in practice are a chronological trace (a timeline
    of what a user did, second by second) and a copy-pasteable list of ids. Both are
    sequences, not tables. A metric grid is never one of these.
    """
    if not blocks:
        raise BlockError(f"{label}: no blocks")
    if len(blocks) > MAX_BLOCKS:
        raise BlockError(f"{label}: {len(blocks)} blocks exceeds Slack's {MAX_BLOCKS}")
    for i, b in enumerate(blocks):
        where = f"{label} block {i} ({b.get('type')})"
        if b.get("type") == "header":
            t = b["text"]["text"]
            if len(t) > MAX_HEADER_CHARS:
                raise BlockError(f"{where}: header {len(t)} chars exceeds {MAX_HEADER_CHARS}")
            if b["text"]["type"] != "plain_text":
                raise BlockError(f"{where}: headers must be plain_text")
            if "<http" in t or "*" in t:
                raise BlockError(f"{where}: headers cannot carry links or bold")
        elif b.get("type") == "section":
            if "fields" in b:
                if len(b["fields"]) > MAX_FIELDS:
                    raise BlockError(f"{where}: {len(b['fields'])} fields exceeds {MAX_FIELDS}")
                for f in b["fields"]:
                    if len(f["text"]) > MAX_FIELD_CHARS:
                        raise BlockError(f"{where}: field {len(f['text'])} chars exceeds {MAX_FIELD_CHARS}")
            elif "text" in b:
                if len(b["text"]["text"]) > MAX_SECTION_CHARS:
                    raise BlockError(
                        f"{where}: section {len(b['text']['text'])} chars exceeds {MAX_SECTION_CHARS}"
                    )
            else:
                raise BlockError(f"{where}: section needs text or fields")
        elif b.get("type") not in {"divider", "context"}:
            raise BlockError(f"{where}: unsupported block type for a signal digest")
    if require_columns:
        for i, n in metric_prose_sections(blocks):
            raise BlockError(
                f"{label} block {i}: {n} short number-bearing lines in one section. "
                "Numbers go in a two-column `fields` block — F([...]) — so they can be "
                "compared down a column. Pass require_columns=False only where the ORDER "
                "of the lines is the content — a chronological trace, or an id list — and "
                "a grid would destroy it."
            )
    _check_links_and_emoji(blocks, label, shortcodes)


def _check_links_and_emoji(
    blocks: list[dict], label: str, shortcodes: frozenset[str] | None = None
) -> None:
    """Catch the two mistakes that survive a JSON-valid payload: a link whose text
    swallowed the rest of the sentence, and an emoji outside the allowed set."""
    import re

    # ensure_ascii=False matters: the default escapes emoji to \udXXX surrogate pairs,
    # and the emoji check below would then never see a real character to reject.
    raw = json.dumps(blocks, ensure_ascii=False)

    # A link label is a label. When a closing `>` is forgotten mid-sentence the label
    # silently swallows the following prose, which is JSON-valid and renders as one
    # enormous blue run. Raw length alone is a weak signal — a real instance measured
    # 195 chars — so check the label itself for the fingerprints of swallowed prose.
    for text in re.findall(r"<[^<>|]+\|([^<>]*)>", raw):
        if len(text) > MAX_LINK_TEXT_CHARS:
            raise BlockError(
                f"{label}: link label runs {len(text)} chars — labels should be short, "
                f"so this has probably swallowed following prose: {text[:70]!r}"
            )
        if text.count("*") % 2:
            raise BlockError(
                f"{label}: unbalanced bold inside a link label — a closing `>` is likely "
                f"missing, so the label ate the next clause: {text[:70]!r}"
            )
        if re.search(r"[.!?](?:\\n|\s)+[A-Z*]", text):
            raise BlockError(
                f"{label}: link label spans a sentence break — it has swallowed following "
                f"prose: {text[:70]!r}"
            )

    # Strip well-formed links, then any surviving `<` is a malformed one. A surviving
    # `>` is fine: it is how Slack opens a blockquote, which the verdict line uses.
    stripped = re.sub(r"<[^<>|]+\|[^<>]*>", "", raw)
    stripped = re.sub(r"<[^<>|]+>", "", stripped)
    if "<" in stripped:
        raise BlockError(f"{label}: malformed link — a `<` with no closing `>`")

    if shortcodes is not None:
        # Slack does not apply other formatting inside a code span or fence, and a
        # timestamp like 01:02:48 contains the substring `:02:`. Scanning for shortcodes
        # without excluding code therefore rejects a legitimate chronological trace as an
        # unknown emoji, which is what happened to a Datadog trace posted for a colleague.
        #
        # Scan PER RENDERED STRING, never over the whole payload. Slack formats each
        # block's text independently, so it can never pair a backtick in one block with a
        # backtick in another — but a regex run over the joined payload can, and then it
        # deletes every block in between before the scan. One stray unmatched backtick in
        # two separate blocks was enough to exempt everything between them.
        for text in _rendered_texts(blocks):
            scan = re.sub(r"```.*?```", "", text, flags=re.S)  # re.S: real newlines here
            scan = re.sub(r"`[^`]*`", "", scan)
            for code in re.findall(r":([a-z0-9_+-]+):", scan):
                if code not in shortcodes:
                    raise BlockError(f"{label}: shortcode :{code}: is not in the allowed set")
    if re.search("[\U0001f000-\U0001faff☀-➿⬀-⯿️]", raw):
        raise BlockError(f"{label}: Unicode emoji are not allowed in outbound posts")


# ── digest ──────────────────────────────────────────────────────────────────────
@dataclass
class Part:
    fallback: str
    blocks: list[dict]


@dataclass
class Digest:
    """A headline plus ordered thread parts, all destined for one channel."""

    channel: str
    headline_fallback: str
    require_columns: bool = True
    """Set False for a digest whose content is a sequence — a chronological trace, an id
    list — where a grid would destroy the ordering. Without this the documented genre is
    unreachable from the documented entry point."""
    headline: list[dict] = field(default_factory=list)
    parts: list[Part] = field(default_factory=list)
    unfurl: bool = False

    def add_part(self, header: str, blocks: list[dict], fallback: str | None = None) -> None:
        self.parts.append(Part(fallback or header, [H(header), *blocks]))

    shortcodes: frozenset[str] | None = SIGNAL_POST_SHORTCODES

    def validate(self) -> None:
        validate_blocks(self.headline, "headline", self.shortcodes, self.require_columns)
        if len(self.headline_fallback) > MAX_FALLBACK_CHARS:
            raise BlockError("headline fallback too long")
        if self.headline[0].get("type") != "header":
            raise BlockError("headline must open with a header block")
        for i, p in enumerate(self.parts, 1):
            validate_blocks(p.blocks, f"part {i}", self.shortcodes, self.require_columns)

    def payloads(self) -> list[dict]:
        base = {"channel": self.channel, "unfurl_links": self.unfurl, "unfurl_media": self.unfurl}
        out = [{**base, "text": self.headline_fallback, "blocks": self.headline}]
        out += [{**base, "text": p.fallback, "blocks": p.blocks} for p in self.parts]
        return out

    def write(self, prefix: str) -> list[str]:
        """Write one file per message. Keep them on disk: the exact post stays
        reproducible and diffable, and the readability linter runs on files."""
        self.validate()
        paths = []
        for i, payload in enumerate(self.payloads()):
            name = "00-head" if i == 0 else f"{i:02d}"
            path = Path(f"{prefix}{name}.json")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
            paths.append(str(path))
        return paths


def lint(paths: list[str], linter: str) -> None:
    """Run the outbound readability linter over every payload. Hard stop on failure —
    it catches bare tracker IDs, which are the most common reason a post is unreadable
    to anyone who was not in the thread it came from."""
    for p in paths:
        r = subprocess.run([linter, p], capture_output=True, text=True)
        if r.returncode != 0:
            raise BlockError(f"readability lint failed for {p}:\n{r.stdout}{r.stderr}")


def send_thread(
    payloads: list[dict],
    poster: Callable[[dict], dict],
    pause: float = 0.0,
) -> list[str]:
    """Post the headline, then each part beneath it.

    If the headline fails, nothing else is sent: a thread with no root is worse than
    no post at all. If a part fails, the already-sent parts stay and the error names
    which index stopped, so a retry can resume rather than duplicate.
    """
    if not payloads:
        return []
    head = poster(payloads[0])
    if not head.get("ok"):
        raise BlockError(f"headline send failed ({head.get('error')}) — no parts sent")
    root = head["ts"]
    sent = [root]
    for i, payload in enumerate(payloads[1:], 1):
        if pause:
            time.sleep(pause)
        r = poster({**payload, "thread_ts": root})
        if not r.get("ok"):
            raise BlockError(f"part {i} failed ({r.get('error')}); sent so far: {sent}")
        sent.append(r["ts"])
    return sent


def permalink(workspace: str, channel: str, ts: str) -> str:
    return f"https://{workspace}.slack.com/archives/{channel}/p{ts.replace('.', '')}"
