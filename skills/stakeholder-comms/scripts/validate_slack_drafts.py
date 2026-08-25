#!/usr/bin/env python3
"""Validate paste-ready Slack bodies embedded in a Markdown queue."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple

MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
RAW_URL = re.compile(r"https?://\S+")
BARE_GITHUB_ID = re.compile(r"(?<![\w[])#\d+\b")
BARE_LINEAR_ID = re.compile(r"(?<![\w[])FE-\d+\b")
GITHUB_DESTINATION = re.compile(r"github\.com/[^/]+/[^/]+/(?:pull|issues)/(\d+)(?:$|[?#])")
LINEAR_DESTINATION = re.compile(r"linear\.app/[^/]+/issue/(FE-\d+)(?:/|$)", re.IGNORECASE)


class DraftBlock(NamedTuple):
    start_line: int
    lines: list[tuple[int, str]]


def draft_blocks(markdown: str) -> list[DraftBlock]:
    """Return blockquotes and fenced-markdown bodies that are paste-ready drafts."""
    lines = markdown.splitlines()
    blocks: list[DraftBlock] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped == "```markdown":
            start = index + 2
            body: list[tuple[int, str]] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                body.append((index + 1, lines[index]))
                index += 1
            blocks.append(DraftBlock(start, body))
        elif lines[index].lstrip().startswith(">"):
            start = index + 1
            body = []
            while index < len(lines) and lines[index].lstrip().startswith(">"):
                value = lines[index].lstrip()[1:].removeprefix(" ")
                body.append((index + 1, value))
                index += 1
            blocks.append(DraftBlock(start, body))
            continue
        index += 1
    return blocks


def validate(markdown: str) -> list[str]:
    errors: list[str] = []
    blocks = draft_blocks(markdown)
    if not blocks:
        return ["no paste-ready Slack bodies found"]

    for block in blocks:
        previous_nonblank = False
        for line_number, line in block.lines:
            nonblank = bool(line.strip())
            if nonblank and previous_nonblank:
                errors.append(
                    f"line {line_number}: adjacent nonblank lines hard-wrap a paragraph; "
                    "use one physical line per paragraph with a blank line between paragraphs"
                )
            previous_nonblank = nonblank

            if "**" in line:
                errors.append(f"line {line_number}: Slack draft contains unsupported ** bold")

            links = list(MARKDOWN_LINK.finditer(line))
            without_links = MARKDOWN_LINK.sub("", line)
            if RAW_URL.search(without_links):
                errors.append(f"line {line_number}: raw external URL must use a descriptive link")
            if BARE_GITHUB_ID.search(without_links):
                errors.append(f"line {line_number}: bare GitHub identifier must be hyperlinked")
            if BARE_LINEAR_ID.search(without_links):
                errors.append(f"line {line_number}: bare Linear identifier must be hyperlinked")

            for link in links:
                label, destination = link.groups()
                if RAW_URL.fullmatch(label):
                    errors.append(f"line {line_number}: link label must describe its destination")
                github_match = GITHUB_DESTINATION.search(destination)
                if github_match and label != f"#{github_match.group(1)}":
                    errors.append(
                        f"line {line_number}: GitHub reference must use [#{github_match.group(1)}](URL)"
                    )
                linear_match = LINEAR_DESTINATION.search(destination)
                if linear_match and label.upper() != linear_match.group(1).upper():
                    errors.append(
                        f"line {line_number}: Linear reference must use [{linear_match.group(1).upper()}](URL)"
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors = validate(args.path.read_text(encoding="utf-8"))
    if errors:
        print(f"Slack draft validation failed: {args.path}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Slack draft validation passed: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
